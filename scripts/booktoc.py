"""book-toc.md의 작품 파라미터 블록과 원고를 읽는 공용 모듈.

스킬·검증기·린터·e북 생성기가 모두 이 모듈로 값을 읽는다.
작품 고유 값은 이 모듈에도 하드코딩하지 않는다.
"""
import json
import os
import re
import sys
from pathlib import Path


def _find_root():
    """프로젝트 폴더 찾기: --root 인자 > NOVEL_ROOT 환경 변수 > 현재 폴더에서 위로 book-toc.md가 있는 곳 > 현재 폴더."""
    for i, a in enumerate(sys.argv):
        if a == "--root" and i + 1 < len(sys.argv):
            return Path(sys.argv[i + 1]).resolve()
        if a.startswith("--root="):
            return Path(a.split("=", 1)[1]).resolve()
    if os.environ.get("NOVEL_ROOT"):
        return Path(os.environ["NOVEL_ROOT"]).resolve()
    cur = Path.cwd().resolve()
    for d in [cur, *cur.parents]:
        if (d / "book-toc.md").exists():
            return d
    return cur


SKILL_DIR = Path(__file__).resolve().parents[1]   # 이 스크립트가 든 스킬 폴더
ROOT = _find_root()                                # 작품 프로젝트 폴더
DEFAULT_TOC = ROOT / "book-toc.md"
RUN_RE = re.compile(r"^\d{8}_\d{2}$")
FORMATS = {"ebook": "ebook.html"}             # 만드는 출판 형식은 웹 e북 하나다
LEGACY_FORMATS = {"docx": "final.docx"}       # 예전 작품에만 남은 형식. 만들지 않고, 블록에서 빼며 보관함으로 옮길 때만 알아본다
ALL_FORMATS = {**FORMATS, **LEGACY_FORMATS}
THIRD_PARTY = ("서평", "추천사", "해설")


def load_params(toc_path=DEFAULT_TOC):
    text = Path(toc_path).read_text(encoding="utf-8")
    m = re.search(r"```json\s*\n(.*?)\n```", text, re.S)
    if not m:
        raise SystemExit(f"{toc_path}: 작품 파라미터 JSON 블록이 없다")
    return json.loads(m.group(1))


def heading(ch):
    return f"# {ch['no']}장. {ch['title']}"


def latest_run(stage="02_draft", root=ROOT):
    base = Path(root) / stage
    runs = sorted(p.name for p in base.iterdir() if p.is_dir() and RUN_RE.match(p.name)) if base.exists() else []
    return runs[-1] if runs else None


def part_heading(pt):
    return f"# {pt['no']}부. {pt['title']}"


def is_part_mode(params):
    return params.get("structure_mode") == "part"


def final_draft_name(params):
    return "09_draft-final-merged.md" if is_part_mode(params) else "09_draft-final.md"


def outline(params):
    """목차 순서대로 (종류, 헤딩 텍스트) 목록. 장편이면 부 제목이 해당 장들 앞에 온다."""
    out, by_no = [], {c["no"]: c for c in params["chapters"]}
    if is_part_mode(params):
        for pt in params["parts"]:
            out.append(("part", part_heading(pt)))
            out += [("chapter", heading(by_no[n])) for n in pt["chapters"]]
    else:
        out = [("chapter", heading(c)) for c in params["chapters"]]
    return out


def back_headings(params):
    return [f"# {name}" for name in params.get("back_matter", [])]


def split_back(text, params):
    """back_matter 섹션을 원고 순서대로 [(헤딩, 본문)]으로 돌려준다."""
    allowed, out, cur = set(back_headings(params)), [], None
    for line in text.split("\n"):
        if line.startswith("# "):
            cur = None
            if line.strip() in allowed:
                cur = [line.strip(), []]
                out.append(cur)
            continue
        if cur is not None:
            cur[1].append(line)
    return [(h, "\n".join(b).strip()) for h, b in out]


def doc_order(text, params):
    """원고에 실제로 있는 순서의 헤딩 목록: 부·장(outline) 다음 back_matter."""
    present = [h for h, _ in split_back(text, params)]
    return [h for _, h in outline(params)] + present


def split_draft(text, params):
    """원고를 (장 번호 -> 본문) 사전과 허용되지 않은 H1 헤딩 목록으로 나눈다. 부 헤딩은 허용 헤딩이다."""
    allowed = {heading(c): c["no"] for c in params["chapters"]}
    parts = {part_heading(p) for p in params.get("parts", [])} if is_part_mode(params) else set()
    chapters, extra, cur = {}, [], None
    for line in text.split("\n"):
        if line.startswith("# "):
            h = line.strip()
            if h in allowed:
                cur = allowed[h]
                chapters[cur] = []
            elif h in parts or h in back_headings(params):
                cur = None
            else:
                extra.append(h)
                cur = None
            continue
        if cur is not None:
            chapters[cur].append(line)
    return {k: "\n".join(v) for k, v in chapters.items()}, extra


def run_params(run, root=ROOT):
    """run을 열 때 저장한 블록 스냅샷을 읽는다. 없으면 현재 블록."""
    snap = Path(root) / "01_test" / run / "book-toc.snapshot.md"
    return load_params(snap if snap.exists() else Path(root) / "book-toc.md")


def ledger(run, root=ROOT):
    f = Path(root) / "02_draft" / run / "00_RUN_STATUS.md"
    return f.read_text(encoding="utf-8") if f.exists() else ""


def is_closed(run, root=ROOT):
    return bool(re.search(r"^closed:", ledger(run, root), re.M))


def is_finished(run, root=ROOT):
    """끝난 run: 닫혔거나 출판까지 마쳤다. 끝난 run은 이어 쓰지 않는다(references/workflow.md 2절)."""
    led = ledger(run, root)
    return bool(re.search(r"^closed:", led, re.M) or re.search(r"^stage:\s*publish done", led, re.M))


def work_tokens(params):
    """작품 고유 토큰: 제목, 마지막 줄, 화자, 인물, 폐기된 이름."""
    return [params["title"], params["last_line"], params["narrator"]["name"]] + params["characters"] + params.get("retired_names", [])


def past_work_tokens(root=ROOT):
    """run 스냅샷에서 모은 지난 작품 토큰 {토큰: 작품 제목}."""
    out = {}
    for snap in sorted((Path(root) / "01_test").glob("*/book-toc.snapshot.md")):
        try:
            sp = load_params(snap)
        except SystemExit:
            continue
        for t in work_tokens(sp):
            out.setdefault(t, sp["title"])
    return out


def count_chars(s):
    """200자 원고지 기준: 줄바꿈만 빼고 공백은 센다."""
    return len(s.replace("\n", "").replace("\r", ""))


def strip_quotes(s):
    """대사(큰따옴표·작은따옴표·낫표 안)를 지운 서술문만 남긴다."""
    return re.sub(r"\"[^\"\n]*\"|“[^”\n]*”|‘[^’\n]*’|「[^」\n]*」|『[^』\n]*』", "", s)


def waiver_approvals(led, closed=None):
    """waiver 줄 번호 → 그것을 승인한 줄 번호. 짝짓기 규칙의 유일한 정의.
    승인 줄은 **바로 위**(빈 줄·note 줄만 건너뜀)의 같은 id waiver 하나만 승인한다. 사이에 다른 waiver나 gate가 있으면 짝이 아니다.
    닫힌 run(`closed:` 줄이 있음)의 close-run 승인은 그보다 앞선 미승인 waiver 전부를 승인한다(사용자에게 목록을 보여 주고 받은 승인).
    closed 인자는 옛 호출 호환용이고 쓰지 않는다. 닫힘 여부는 원장에서 직접 읽는다."""
    lines = led.split("\n")
    is_closed_led = bool(re.search(r"^closed:", led, re.M))
    approved, last = {}, None   # last: 바로 위 의미 있는 줄 (번호, waiver id 또는 None)
    for i, ln in enumerate(lines):
        if not ln.strip() or ln.startswith("note:"):
            continue
        m = re.match(r"^gate:\s*waiver-(\S+)\s*→\s*approved\b", ln)
        if m and last and last[1] == m.group(1) and last[0] not in approved:
            approved[last[0]] = i
        elif is_closed_led and re.match(r"^gate:\s*close-run\s*→\s*approved\b", ln):
            for j, lj in enumerate(lines[:i]):
                if lj.startswith("waiver:") and j not in approved:
                    approved[j] = i
        w = re.match(r"^waiver:\s*(\S+)", ln)
        last = (i, w.group(1)) if w else (i, None)
    return approved


def paired_waivers(led, closed=None):
    """승인된 waiver의 (줄 번호, id, 나머지 내용) 목록."""
    lines = led.split("\n")
    out = []
    for i in sorted(waiver_approvals(led)):
        m = re.match(r"^waiver:\s*(\S+)(.*)$", lines[i])
        out.append((i, m.group(1), m.group(2)))
    return out


APPROVAL_RE = r"^gate:\s*([^\s→\"]+(?: [^\s→\"]+)*?)\s*→\s*(approved|verified)\b(.*)$"   # 섹션 이름에 빈칸이 있어도 된다(remove-작가의 말). id에 →와 따옴표는 없다(응답 원문 속 "→ approved"를 승인으로 읽지 않게)
NOTE_SYNC_KEYS = ("characters", "retired_names", "anchors", "last_line", "forbidden_disclosures")   # storyline 동기화가 note로 바꿀 수 있는 키


def approved_gates(segment):
    """구간 안의 사용자 승인 gate id 집합. `→ approved`·`→ verified`만 승인이다."""
    return {m.group(1) for m in re.finditer(APPROVAL_RE, segment, re.M)}


def leaf_diff(a, b, path=""):
    """두 블록 사이에서 바뀐 값의 경로 목록 (예: publish.ebook.epigraph.source_verified, back_matter)."""
    if isinstance(a, dict) and isinstance(b, dict):
        out = []
        for k in sorted(set(a) | set(b)):
            out += leaf_diff(a.get(k), b.get(k), f"{path}.{k}" if path else k)
        return out
    return [] if a == b else [path or "(전체)"]


def key_tokens(text):
    """승인·기록 줄에 적힌 키 이름들. 키 목록은 선택(approved) 바로 뒤부터 첫 괄호·따옴표 앞까지다.
    그 뒤(날짜, 응답 원문, 덧붙인 설명)의 낱말은 키로 세지 않는다. 가운뎃점·쉼표·빈칸·슬래시로 나눈다."""
    head = re.split(r"[(\"“”‘’「『]", text, maxsplit=1)[0]
    return {x for x in re.split(r"[·,\s/]+", head) if x and re.match(r"^[A-Za-z_][\w.]*$", x)}


def covers(token, leaf):
    """토큰이 바뀐 경로를 가리키는가: 같은 경로, 상위 경로(접두), 또는 끝 이름이 같을 때."""
    return leaf == token or leaf.startswith(token + ".") or leaf.split(".")[-1] == token


MISSING = object()   # 블록에 그 키가 아예 없음(빈칸과 다르다)


def get_path(params, path):
    cur = params
    for k in path.split("."):
        if not isinstance(cur, dict) or k not in cur:
            return MISSING
        cur = cur[k]
    return cur


def all_leaves(params, path=""):
    if isinstance(params, dict):
        out = []
        for k, v in params.items():
            out += all_leaves(v, f"{path}.{k}" if path else k)
        return out
    return [path]


def is_hole(v):
    if v is MISSING:   # 새로 생긴 키는 빈칸 채우기가 아니다(block-change 승인이 필요하다)
        return False
    return v in (None, "", []) or (isinstance(v, str) and bool(re.fullmatch(r"<[^<>]*>", v.strip()))) or \
        (isinstance(v, list) and all(is_hole(x) for x in v))


def leaf_allowed(leaf, seg, ok, old=None):
    """바뀐 경로 하나를 이 구간의 기록이 덮는가. 키를 적은 승인만 그 키를 덮는다.
    끝 이름은 블록 안에서 그 이름으로 끝나는 경로가 하나뿐일 때만 키로 인정한다(예: lines는 epigraph·back_quote 둘에 있어 안 된다).
    publish-info는 빈칸(<…>·빈 값)이던 출판 정보를 채운 것만, epigraph-source는 출처 확인 표시(source_verified)만 덮는다."""
    leaves = all_leaves(old) if isinstance(old, dict) else []
    ends = {}
    for lf in leaves:
        ends.setdefault(lf.split(".")[-1], set()).add(lf)

    def cov(tok):
        if leaf == tok or leaf.startswith(tok + "."):
            return True
        return leaf.split(".")[-1] == tok and len(ends.get(tok, {leaf})) <= 1

    for m in re.finditer(APPROVAL_RE, seg, re.M):
        gid, rest = m.group(1), m.group(3)
        if gid == "block-change" and any(cov(tk) for tk in key_tokens(rest)):
            return True
        if gid == "publish-info" and leaf.startswith("publish.") and not leaf.startswith("publish.formats") \
                and isinstance(old, dict) and is_hole(get_path(old, leaf)):
            return True
        if gid == "epigraph-source" and leaf == "publish.ebook.epigraph.source_verified":
            return True
    if leaf.split(".")[0] in NOTE_SYNC_KEYS:
        for m in re.finditer(r"^note:\s*block-change\b(.*)$", seg, re.M):
            if any(cov(tk) for tk in key_tokens(m.group(1))):
                return True
    return False


def parse_lock(line):
    m = re.match(r"^lock:\s*back_matter=(\[.*?\])\s+formats=(\[.*?\])\s+snapshot=(\S+)(?:\s+publish=(\S+))?(?:\s+block=(\S+))?(?:\s+draft=(\S+))?", line)
    if not m:
        return None
    extra = dict(re.findall(r"\b(blocksha|out|out2)=(\S+)", line))
    return {"back_matter": json.loads(m.group(1)), "formats": json.loads(m.group(2)), "snapshot": m.group(3),
            "publish": m.group(4), "block": m.group(5), "draft": m.group(6),
            "blocksha": extra.get("blocksha"), "out": extra.get("out"), "out2": extra.get("out2")}


def draft_sha(run, root=ROOT):
    """최종 원고(09_draft-final*.md 전부)의 해시. 없으면 none."""
    import hashlib
    fs = sorted((Path(root) / "02_draft" / run).glob("09_draft-final*.md"))
    if not fs:
        return "none"
    h = hashlib.sha256()
    for f in fs:
        h.update(f.name.encode() + b"\0" + f.read_bytes())
    return h.hexdigest()[:16]


def require_run(run, root=ROOT):
    """run 폴더와 원장이 있는지 본다. 없으면 있는 run 목록과 함께 멈춘다(스크립트 공통 안내)."""
    if run and (Path(root) / "02_draft" / run / "00_RUN_STATUS.md").exists():
        return run
    runs = sorted(p.name for p in (Path(root) / "02_draft").glob("*_*") if (p / "00_RUN_STATUS.md").exists()) \
        if (Path(root) / "02_draft").exists() else []
    raise SystemExit(f"run '{run}'이 없다(02_draft/{run}/00_RUN_STATUS.md 없음). 있는 run: {', '.join(runs) or '없음'}")


def open_post_audit(run, root=ROOT):
    """진행 중인 출판 뒤 수정: 마지막 잠금 뒤 note: post-audit-prepare가 있고 그 뒤 stage: post-audit-fix done이 없으면
    (원장 줄 번호, owner)를 돌려준다. owner가 없는 옛 prepare 줄이면 owner는 None. 진행 중인 수정이 없으면 None.
    한 run의 출판 뒤 수정은 한 번에 하나, 시작한 세션(owner)만 마친다."""
    lines = ledger(run, root).split("\n")
    last = max([i for i, ln in enumerate(lines) if ln.startswith("lock:")], default=-1)
    preps = [i for i, ln in enumerate(lines) if i > last and ln.startswith("note: post-audit-prepare")]
    if not preps:
        return None
    k = preps[-1]
    if any(re.match(r"^stage:\s*post-audit-fix (done .*\(republish\.py, owner |abandoned)", ln) for ln in lines[k + 1:]):
        return None
    m = re.search(r"\bowner=(\S+)", lines[k])
    owner = m.group(1) if m else None
    for ln in lines[k + 1:]:   # 이어받기(takeover)가 있으면 마지막 이어받은 owner가 주인이다
        t = re.match(r"^note:\s*post-audit-takeover\b.*\bowner=(\S+)", ln)
        if t:
            owner = t.group(1)
    return k, owner


META_OUT = ("final.docx", "ebook.html", "metadata.md")


def output_sha(run, root=ROOT, names=("final.docx", "ebook.html")):
    """출판 산출물의 해시. 모두 없으면 none. out=은 e북(예전 작품은 docx 포함), out2=는 metadata.md까지 담는다(옛 잠금 줄과 호환)."""
    import hashlib
    out = Path(root) / "03_output" / run
    fs = [out / n for n in names if (out / n).exists()]
    if not fs:
        return "none"
    h = hashlib.sha256()
    for f in fs:
        h.update(f.name.encode() + b"\0" + f.read_bytes())
    return h.hexdigest()[:16]


def out_unchanged(lk, run, root=ROOT):
    """잠금 줄의 산출물 해시와 지금 산출물이 같은가. out2(metadata 포함)가 있으면 그것으로, 옛 out이면 두 계산 방식 모두와 비교한다.
    잠금에 산출물 해시가 없으면 None."""
    if not lk:
        return None
    if lk.get("out2") not in (None, "none"):
        return output_sha(run, root, META_OUT) == lk["out2"]
    if lk.get("out") not in (None, "none"):
        return lk["out"] in (output_sha(run, root), output_sha(run, root, META_OUT))
    return None


def file_sha16(path):
    import hashlib
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()[:16]


def lock_dir(run, root=ROOT):
    return Path(root) / "01_test" / run / "locks"


def lock_violations(run, root=ROOT):
    """잠금 위반 목록 (references/ledger.md "잠금"). 이어진 잠금끼리, 마지막 잠금과 지금 상태를 구간마다 비교한다.
    잠금마다 그 시점 블록을 01_test/<run>/locks/lock-NN.json에 두고, 바뀐 값의 경로마다 그 키를 적은 승인(또는 허용된 note)을 찾는다.
    lint_project.py, lock_run.py, republish.py가 함께 쓴다."""
    led = ledger(run, root)
    lines = led.split("\n")
    locks = [(i, parse_lock(ln)) for i, ln in enumerate(lines) if ln.startswith("lock:")]
    out = [f"원장 {i + 1}줄 잠금 줄 형식이 깨졌다" for i, st in locks if st is None]
    locks = [(i, st) for i, st in locks if st]
    files = sorted(lock_dir(run, root).glob("lock-*.json"))
    if not locks:
        if re.search(r"^gate:\s*new-run\b", led, re.M) or files:
            out.append("잠금 줄이 하나도 없다. new_run.py로 연 run은 잠금 줄로 시작한다(잠금 줄이 지워졌다)")
        return out
    named = [st["block"] for _, st in locks if st["block"]]
    for f in files:
        if f.name not in named:
            out.append(f"잠금 파일 {f.name}에 해당하는 잠금 줄이 원장에 없다(잠금 줄이 지워졌다)")
    seen_block = False
    for i, st in locks:
        if st["block"]:
            seen_block = True
            bf = lock_dir(run, root) / st["block"]
            if not bf.exists():
                out.append(f"원장 {i + 1}줄 잠금 파일 {st['block']}이 없다")
            elif st["blocksha"] and file_sha16(bf) != st["blocksha"]:
                out.append(f"잠금 파일 {st['block']}이 원장 {i + 1}줄에 적힌 해시와 다르다(잠금 뒤 고쳐졌다)")
        elif seen_block:
            out.append(f"원장 {i + 1}줄 잠금 줄에 block= 이 빠졌다(앞 잠금에는 있다)")
    p = run_params(run, root)
    now = {"back_matter": p.get("back_matter", []), "formats": p.get("publish", {}).get("formats", ["ebook"]),
           "snapshot": snapshot_sha(run, root), "publish": publish_sha(p), "params": p, "draft": draft_sha(run, root), "out": output_sha(run, root),
           "out2": output_sha(run, root, META_OUT)}
    pub_done = [i for i, ln in enumerate(lines) if re.match(r"^stage:\s*publish done", ln)]
    for i, st in locks:
        bf = lock_dir(run, root) / st["block"] if st["block"] else None
        st["params"] = json.loads(bf.read_text(encoding="utf-8")) if bf and bf.exists() else None
    states = locks + [(len(lines), now)]
    for (ai, a), (bi, bst) in zip(states, states[1:]):
        seg = "\n".join(lines[ai + 1:bi])
        ok = approved_gates(seg)
        where = f"원장 {ai + 1}줄 잠금" + (f"과 {bi + 1}줄 잠금 사이" if bi < len(lines) else " 이후")
        # 출판 뒤 잠긴 최종 원고는 post-audit 승인 없이 바뀌면 안 된다(글자 수가 같은 수정도 해시로 잡는다)
        # 출판 뒤 원고·산출물이 바뀐 구간은 republish.py 절차 하나로만 닫힌다: owner가 있는 prepare 한 줄, 같은 owner의 done 줄
        # (republish.py가 쓴 형식), 원고가 바뀌었으면 산출물도 다시 만들어졌어야 한다. 옛 형식 잠금(blocksha 없음) 구간은 보지 않는다
        okey = "out2" if a.get("out2") and bst.get("out2") else "out"   # metadata까지 잠근 줄끼리는 out2로 비교
        # 2026-10-03 잠깐 동안 out=에 metadata까지 담아 쓴 잠금 줄이 있다. 그 값이 지금의 out2와 같으면 바뀌지 않은 것이다
        out_moved = a.get(okey) not in (None, "none") and bst.get(okey) and a[okey] != bst[okey] and \
            not (okey == "out" and bst.get("out2") and a["out"] == bst["out2"])
        changed = (a.get("draft") not in (None, "none") and bst.get("draft") and a["draft"] != bst["draft"]) or out_moved
        if pub_done and pub_done[0] < ai and a.get("blocksha") and changed and bi < len(lines):
            preps = re.findall(r"^note:\s*post-audit-prepare\b.*$", seg, re.M)
            owners = {mm.group(1) for p_ in preps for mm in [re.search(r"\bowner=(\S+)", p_)] if mm}
            owners |= set(re.findall(r"^note:\s*post-audit-takeover\b.*\bowner=(\S+)", seg, re.M))
            dones = re.findall(r"^stage:\s*post-audit-fix done .*\(republish\.py, owner (\S+?),", seg, re.M)
            if re.search(r"^gate:\s*post-audit-abandon\s*→\s*approved\b", seg, re.M):   # 작가 승인으로 버린 수정도 닫힘이다
                dones += re.findall(r"^stage:\s*post-audit-fix abandoned \S+ \(owner (\S+?),", seg, re.M)
            if len(preps) != 1 or not all("owner=" in p_ and "changelog=" in p_ for p_ in preps):
                out.append(f"{where}에 출판 뒤 수정이 있는데 republish.py --prepare 줄이 정확히 하나(owner·changelog 포함)가 아니다")
            elif not dones or dones[-1] not in owners:
                out.append(f"{where}의 출판 뒤 수정이 republish.py(같은 owner)로 끝나지 않았다. 손으로 쓴 done 줄로는 닫히지 않는다")
            if a.get("draft") != bst.get("draft") and not out_moved and a.get("out") not in (None, "none"):
                out.append(f"{where}에 최종 원고는 바뀌었는데 e북을 다시 만들지 않았다(republish.py로 마친다)")
        elif pub_done and pub_done[0] < ai and a.get("blocksha") and changed and \
                not re.search(r"^note:\s*post-audit-prepare\b.*\bowner=", seg, re.M):
            out.append(f"{where}에 출판본 원고·산출물이 바뀌었는데 republish.py --prepare 기록이 없다(고치기 전 보관 없이 고쳤다)")
        if pub_done and pub_done[0] < ai and out_moved and "post-audit" not in ok:
            out.append(f"출판 산출물(ebook.html·metadata.md)이 {where}에 바뀌었는데 gate: post-audit → approved 줄이 없다. "
                       f"생성기를 직접 돌리지 말고 SKILL.md \"출판 뒤 수정\" 절차(republish.py)로 다시 만든다")
        if pub_done and pub_done[0] < ai and a.get("draft") not in (None, "none") and bst.get("draft") and a["draft"] != bst["draft"] \
                and "post-audit" not in ok:
            out.append(f"출판된 최종 원고가 {where}에 바뀌었는데 gate: post-audit → approved 줄이 없다. "
                       f"작가에게 묻고 SKILL.md \"출판 뒤 수정\" 절차(republish.py --prepare)로 고친다")
        for kind in ("back_matter", "formats"):
            for gone in [x for x in a[kind] if x not in bst[kind]]:
                if not ({f"remove-{gone}", f"remove-{ALL_FORMATS.get(gone, gone)}"} & ok):   # 형식 이름과 파일 이름 어느 쪽 승인도 같다
                    out.append(f"{kind}에서 '{gone}'이 빠졌는데 {where}에 사용자 승인이 없다. "
                               f'작가에게 묻고 gate: remove-{gone} → approved (날짜) "<응답 원문>"을 남긴다')
        removed = {"back_matter", "publish.formats"}
        if a.get("params") is not None and bst.get("params") is not None:
            for leaf in leaf_diff(a["params"], bst["params"]):
                if leaf in removed:   # 목록에서 빠진 항목은 위에서 remove-<항목>으로 본다. 더해진 항목이 있으면 아래 승인 규칙
                    k = "back_matter" if leaf == "back_matter" else "formats"
                    if set(bst[k]) <= set(a[k]):
                        continue
                if not leaf_allowed(leaf, seg, ok, a["params"]):
                    note_ok = "" if leaf.split(".")[0] in NOTE_SYNC_KEYS else " (이 키는 note로 바꿀 수 없다)"
                    out.append(f"블록 '{leaf}'이 {where}에 바뀌었는데 그 키를 적은 승인이 없다{note_ok}. "
                               f'gate: block-change → approved {leaf} (날짜) "<응답 원문>"을 남긴다')
        else:   # 블록 사본이 없는 옛 잠금: 해시로만 본다
            if a["snapshot"] != bst["snapshot"] and "block-change" not in ok and not re.search(r"^note:\s*block-change\b", seg, re.M):
                out.append(f"스냅샷이 {where}에 바뀌었는데 기록이 없다. "
                           f'gate: block-change → approved <바꾼 키> (날짜) "<응답 원문>"을 남긴다')
            if a["publish"] and bst["publish"] and a["publish"] != bst["publish"] and \
                    not ({"block-change", "publish-info", "epigraph-source"} & ok):
                out.append(f"출판 정보(publish)가 {where}에 바뀌었는데 사용자 승인이 없다(note로는 안 된다). "
                           f'gate: block-change → approved <바꾼 키> (날짜) "<응답 원문>"을 남긴다')
    return out


def snapshot_sha(run, root=ROOT):
    f = Path(root) / "01_test" / run / "book-toc.snapshot.md"
    import hashlib
    return hashlib.sha256(f.read_bytes()).hexdigest()[:16] if f.exists() else "none"


def publish_sha(p):
    """출판 정보(publish 하위 전체)의 해시. 잠금 뒤 이 값이 바뀌면 사용자 gate가 있어야 한다."""
    import hashlib
    return hashlib.sha256(json.dumps(p.get("publish", {}), ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:16]


def lock_line(run, root=ROOT):
    """작가 산출물 잠금 줄을 만들고, 그 시점 블록을 01_test/<run>/locks/lock-NN.json에 남긴다.
    이후 바뀐 값은 경로마다 그 키를 적은 승인이 있어야 한다(lock_violations)."""
    p = run_params(run, root)
    d = lock_dir(run, root)
    d.mkdir(parents=True, exist_ok=True)
    name = f"lock-{len(list(d.glob('lock-*.json'))) + 1:02d}.json"
    (d / name).write_text(json.dumps(p, ensure_ascii=False, indent=1), encoding="utf-8")
    return (f"lock: back_matter={json.dumps(p.get('back_matter', []), ensure_ascii=False)} "
            f"formats={json.dumps(p.get('publish', {}).get('formats', ['ebook']), ensure_ascii=False)} "
            f"snapshot={snapshot_sha(run, root)} publish={publish_sha(p)} block={name} draft={draft_sha(run, root)} "
            f"blocksha={file_sha16(d / name)} out={output_sha(run, root)} out2={output_sha(run, root, META_OUT)}")


def headers(txt):
    """합평 파일 머리 줄(workflow.md 4.2)."""
    keys = {"입력": r"^입력:\s*(\S+)", "sha": r"^입력 sha256:\s*([0-9a-f]{64})", "score": r"^판정 점수:\s*([\d.]+)",
            "reds": r"^남은 🔴:\s*(\d+)", "verdict": r"^판정:\s*(통과|재수정|동결)", "critic": r"^(?:BURGUNDY|CRITIC):\s*([\d.]+)"}  # CRITIC은 옛 이름
    out = {}
    for k, pat in keys.items():
        m = re.search(pat, txt, re.M)
        out[k] = m.group(1) if m else None
    return out


def ensemble_groups(run, root=ROOT):
    """합평 계열: {"story": [...], "": [...], "part1": [...], "overall": [...]} (라운드 순)."""
    root = Path(root)
    out = {"story": sorted((root / "01_test" / run).glob("00[b-z]_story-ensemble-*.md"))}
    tmp = {}
    for f in (root / "02_draft" / run).glob("0[68]_ensemble-*.md"):
        m = re.match(r"^0[68]_ensemble-(\d+)(?:-(part\d+|overall))?\.md$", f.name)
        if m:
            tmp.setdefault(m.group(2) or "", []).append((int(m.group(1)), f))
    out.update({k: [f for _, f in sorted(v)] for k, v in tmp.items()})
    return out


def gate_status(run, root=ROOT, kind="story"):
    """단계 게이트가 닫혔는가. (닫힘 여부, 이유). 린터와 new_run.py가 같은 판정을 쓴다.

    기준 시점은 그 단계의 마지막 reopen 줄이다(스토리 `reopen: storyline`, 본문 `reopen: review-1~5`. review-6~9로 되돌리는 것은 본문 합평 통과를 무르지 않는다).
    story: 기준 시점 뒤에 `gate: storyline-pass → a`가 있고 최신 스토리 합평이 `판정: 통과`이거나,
           최신 합평 파일명을 적은 open_red가 승인되고 `gate: storyline-rounds → c`가 있어야 한다.
    body:  필수 계열(단편은 본문 계열, 장편은 블록 parts의 모든 부와 overall)의 최신 합평이 통과했거나 open_red로 승인되어야 하고,
           본문 reopen이 있었다면 그 뒤에 합평 라운드 완료 줄(`stage: review-3/5… done`)이 있어야 한다.
    예외: 기준 시점보다 앞선 rework 상속은 원래 run의 판정을 따른다. 기준 시점 뒤의 승인된 gate_log waiver는
          첫 낱말이 대상 게이트(`story` 또는 `body`)와 같을 때만 그 게이트를 닫는다.
          머리 줄 이전의 옛 합평 파일은 승인된 ensemble_header waiver가 있을 때만 본문 끝의 '통과' 표기로 판정한다."""
    root = Path(root)
    led = ledger(run, root)
    lines = led.split("\n")
    paired = paired_waivers(led, is_closed(run, root))
    if kind == "story":
        reopen, pass_pat, rounds_pat = r"^reopen:\s*storyline", r"^gate:\s*storyline-pass\s*→\s*a\b", r"^gate:\s*storyline-rounds\s*→\s*c\b"
        stage_word = "storyline"
    else:
        reopen, pass_pat, rounds_pat = r"^reopen:\s*review-[1-5]\b", None, r"^gate:\s*review-rounds\s*→\s*b\b"
        stage_word = "review"
    cut = max([i for i, ln in enumerate(lines) if re.match(reopen, ln)], default=-1)
    after = lines[cut + 1:]

    def waiver_ok(cid, about=None, after_cut=False):
        return any(wid == cid and (not about or about in rest) and (not after_cut or i > cut) for i, wid, rest in paired)

    inh = [i for i, ln in enumerate(lines) if re.match(rf"^stage:\s*{stage_word} done .*inherited", ln)]
    if inh and inh[0] > cut:
        m = re.search(r"^inherit:\s*(\S+)", led, re.M)
        if not m or not (root / "02_draft" / m.group(1)).exists():
            return False, "rework run인데 원장에 inherit: <지난 run>이 없거나 그 run이 없다"
        ok, why = gate_status(m.group(1), root, kind)
        return ok, ("" if ok else f"물려받은 run {m.group(1)}: {why}")
    token = "story" if kind == "story" else "body"   # gate_log waiver는 첫 낱말로 대상 게이트를 밝힌다: `waiver: gate_log story|body <사유>`
    if any(wid == "gate_log" and i > cut and rest.split()[:1] == [token] for i, wid, rest in paired):
        return True, "승인된 gate_log waiver (기록상 닫힘)"
    if kind == "story" and not re.search(r"^stage:\s*storyline done", led, re.M):
        return False, "원장에 stage: storyline done이 없다"
    groups = ensemble_groups(run, root)
    if kind == "story":
        required = [("스토리", groups.get("story", []))]
    else:
        p = run_params(run, root)
        if is_part_mode(p):
            required = [(f"본문 part{pt['no']}", groups.get(f"part{pt['no']}", [])) for pt in p.get("parts", [])]
            required.append(("본문 overall", groups.get("overall", [])))
        else:
            required = [("본문", groups.get("", []))]
        if cut >= 0 and not any(re.match(r"^stage:\s*review-[35]\S* done", x) for x in after):
            return False, "본문 reopen 뒤에 끝난 합평 라운드(stage: review-3/5 done)가 없다"
    legacy_ok = waiver_ok("ensemble_header")
    for label, series in required:
        if not series:
            return False, f"{label} 합평이 없다"
        last = series[-1]
        txt = last.read_text(encoding="utf-8")
        hv = headers(txt)
        if hv["verdict"] is None and legacy_ok:
            passed = "통과" in txt[-600:]   # 머리 줄 이전 형식(옛 run)
        else:
            passed = hv["verdict"] == "통과"
        if passed and (pass_pat is None or any(re.match(pass_pat, x) for x in after)):
            continue
        if any(re.match(rounds_pat, x) for x in after) and waiver_ok("open_red", last.name):
            continue
        return False, (f"최신 {label} 합평 {last.name}이 통과하지 않았다" if not passed
                       else f"{label} 통과 뒤 사용자 승인 줄이 없다") + " (마지막 reopen 이후 기준)"
    return True, ""


def story_gate_open(run, root=ROOT):
    return gate_status(run, root, "story")[0]
