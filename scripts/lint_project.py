"""프로젝트 정합성 린터.

사용: python3 <스킬>/scripts/lint_project.py [--root <프로젝트 폴더>] [--verbose]

검사 묶음
  L1 스킬 구조      <스킬>/SKILL.md(name: novel-writing), 서브 에이전트 5개, 단계 문서, 설치본 동기화, 옛 경로 잔존
  L2 블록           필수 키, 템플릿 빈칸(<…>) 잔존, 장 매수 합, 패널 값, 장편 parts 정합
  L3 작품 중립성    규약·스킬·카드에 현재·과거 작품 고유 토큰이 '예시(' 라벨 없이 나오지 않음
  L4 숫자 단일화    규약·스킬·카드에 통과선·매수·위트 횟수 숫자, 'em dash 허용', 원칙 개수 불일치 없음
  L5 정본 동기화    진행 중 run: 블록 = run 스냅샷, 블록의 인물·장 제목·마지막 줄이 storyline 통과본에 있음
  L6 폴더 규칙      영문 폴더 이름, run 이름, 00_storyline 단일 파일, run마다 01_test 짝·원장·스냅샷
  L7 문서 크기      CLAUDE.md 6KB, AGENTS.md 20KB, SKILL.md 500줄
  L8 실행 감사      합평 머리(입력·sha256·판정 점수), 무결성, 점수 동결, 바뀐 자리, 게이트 로그,
                    출판 run의 원고·e북·metadata·게이트 보고서
waiver 규칙: waiver는 사용자 승인 줄이 있을 때만 WARN으로 내린다.
  진행 중 run: `gate: waiver-<id> → approved "<원문>"`
  닫힌 run:    `closed:` + `gate: close-run → approved "<원문>"` (run 안의 모든 waiver를 함께 승인)
  'approved'가 아닌 응답(rejected 등)은 승인이 아니다.
출력: 닫힌 run의 승인된 waiver 경고는 run마다 한 줄로 요약한다. 전부 보려면 --verbose.
"""
import argparse
import difflib
import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import booktoc  # noqa: E402
from booktoc import (FORMATS, ALL_FORMATS, LEGACY_FORMATS, THIRD_PARTY, count_chars, final_draft_name, is_closed,  # noqa: E402
                     is_finished, ledger, load_params, paired_waivers, lock_violations, past_work_tokens, run_params,
                     split_back, split_draft, work_tokens, gate_status, ensemble_groups)
from validate_draft import validate  # noqa: E402

SKILL_NAME = "novel-writing"
STAGES = ["storyline", "research", "write", "review", "publish"]
SKILL_DIR = booktoc.SKILL_DIR
META_SECTIONS = ["도서 분류", "판매 카피", "검색 키워드", "작품 정보", "가격 전략", "배포"]
REQUIRED_KEYS = ["title", "pen_name", "genre", "genre_label", "target_reader", "narrator", "length", "structure_mode",
                 "chapters", "last_line", "back_matter", "anchors", "characters", "forbidden_disclosures",
                 "wit", "style", "review", "publish"]
CAPS = {"CLAUDE.md": 6 * 1024, "AGENTS.md": 20 * 1024}   # 프로젝트 폴더의 진입 문서
SKILL_CAPS = {"references/workflow.md": 20 * 1024, "references/ledger.md": 20 * 1024}
SMALL_EDIT_RATIO, SMALL_EDIT_JUMP = 0.99, 0.3  # 린터 경고 기준. 작품 값이 아니라 감사 도구의 민감도다


class Report:
    def __init__(self):
        self.fails, self.warns, self.folded = [], [], {}

    def fail(self, code, msg):
        self.fails.append(f"{code} {msg}")

    def warn(self, code, msg):
        self.warns.append(f"{code} {msg}")


def system_docs(root, sd=None):
    sd = sd or SKILL_DIR
    docs = [root / "AGENTS.md", root / "CLAUDE.md", sd / "SKILL.md"]
    docs += sorted((sd / "references").glob("*.md")) + sorted((sd / "agents").glob("*.md"))
    return [d for d in docs if d.exists()]


def frontmatter(path):
    parts = path.read_text(encoding="utf-8").split("---")
    return parts[1] if len(parts) > 2 else ""


def tree_digest(folder):
    h = hashlib.sha256()
    for f in sorted(p for p in folder.rglob("*") if p.is_file() and "__pycache__" not in p.parts
                    and p.name != ".DS_Store" and p.suffix != ".pyc"
                    and p.relative_to(folder).parts[0] in ("SKILL.md", "references", "scripts", "templates")):
        h.update(str(f.relative_to(folder)).encode())
        h.update(f.read_bytes())
    return h.hexdigest()


def lines_without_examples(path):
    for i, ln in enumerate(path.read_text(encoding="utf-8").split("\n"), 1):
        if "예시(" not in ln:
            yield i, ln


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None


def strings_in(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from strings_in(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from strings_in(v)

NUM = (int, float)
SCHEMA = {
    "title": str, "pen_name": str, "genre": str, "genre_label": str, "target_reader": str,
    "narrator.name": str, "narrator.person": int, "base_year": int,
    "length.target_pages": int, "length.chars_per_page": int, "length.tolerance": NUM,
    "structure_mode": str, "chapters": list, "last_line": str, "back_matter": list, "anchors": list,
    "characters": list, "forbidden_disclosures": list,
    "wit.per_chapter_min": int, "wit.per_chapter_max": int, "wit.sources": list, "wit.zero_zones": list,
    "style.principles": int, "style.avg_sentence_chars_max": int, "style.translationese": list, "style.cliches": list,
    "review.story_panel": str, "review.story_pass": NUM, "review.story_critic_min": NUM, "review.story_proof_weight": NUM,
    "review.body_pass": NUM, "review.rounds_before_user_check": int, "review.self_bias_warn": NUM,
    "publish.formats": list, "publish.cover_label": str,
}
# 예전 docx 조판 키. 이제 아무 생성기도 읽지 않는다(남아 있으면 WARN으로 알린다)
DOCX_ONLY_KEYS = ("trim_options", "body_font", "body_font_fallback", "body_size_pt", "line_spacing", "first_line_indent_chars",
                  "heading_font", "heading_size_pt", "heading_color", "margin_cm", "header", "footer")
NONEMPTY = ["title", "pen_name", "genre", "genre_label", "target_reader", "narrator.name", "last_line", "publish.cover_label"]
ITEM_SCHEMA = {
    "chapters": {"no": int, "title": str, "pages": int},
    "anchors": {"name": str, "keywords": list, "min_total": int, "chapters": list},
}


def get_path(p, path):
    cur = p
    for k in path.split("."):
        if not isinstance(cur, dict) or k not in cur:
            return KeyError
        cur = cur[k]
    return cur


def key_line(text, path):
    """블록 안에서 경로의 마지막 키가 처음 나오는 book-toc.md 줄 번호."""
    return line_of(text, f'"{path.split(".")[-1]}"')


def check_schema(p, text):
    errs = []
    for path, typ in SCHEMA.items():
        v = get_path(p, path)
        if v is KeyError:
            errs.append(f"블록 키 `{path}`가 없다 (템플릿의 같은 키를 복사해 채운다)")
        elif isinstance(v, bool) or not isinstance(v, typ):
            want = typ.__name__ if isinstance(typ, type) else "숫자"
            errs.append(f"book-toc.md:{key_line(text, path)} `{path}` 값 {v!r}의 형식이 틀렸다 ({want}여야 한다)")
    for path in NONEMPTY:
        v = get_path(p, path)
        if isinstance(v, str) and not v.strip():
            errs.append(f"book-toc.md:{key_line(text, path)} `{path}`가 비어 있다. 따옴표 안에 값을 적는다")
    def at(fk, val):
        return line_of(text, f'"{fk}": ' + json.dumps(val, ensure_ascii=False)) or key_line(text, fk)
    for key, fields in ITEM_SCHEMA.items():
        items = p.get(key) if isinstance(p.get(key), list) else []
        for i, it in enumerate(items):
            for fk, ft in fields.items():
                if not isinstance(it, dict) or fk not in it:
                    errs.append(f"book-toc.md:{key_line(text, key)} `{key}[{i}]`에 `{fk}`가 없다")
                elif isinstance(it[fk], bool) or not isinstance(it[fk], ft):
                    errs.append(f"book-toc.md:{at(fk, it[fk])} `{key}[{i}].{fk}` 값 {it[fk]!r}의 형식이 틀렸다 ({ft.__name__}여야 한다)")
                elif ft is str and not it[fk].strip():
                    errs.append(f"book-toc.md:{at(fk, it[fk])} `{key}[{i}].{fk}`가 비어 있다. 값을 적거나 그 항목을 지운다")
    for i, c in enumerate(p.get("chapters", []) if isinstance(p.get("chapters"), list) else []):
        if isinstance(c, dict) and isinstance(c.get("pages"), int) and c["pages"] < 1:
            errs.append(f"book-toc.md:{at('pages', c['pages'])} `chapters[{i}].pages` 값 {c['pages']}: 1 이상이어야 한다")
    for path in ("characters", "forbidden_disclosures", "back_matter", "wit.sources"):
        v = get_path(p, path)
        if isinstance(v, list):
            for i, s in enumerate(v):
                if not isinstance(s, str) or not s.strip():
                    errs.append(f"book-toc.md:{key_line(text, path)} `{path}[{i}]` 값 {s!r}: 비어 있지 않은 문자열이어야 한다")
    nos = {c.get("no") for c in p.get("chapters", []) if isinstance(c, dict)}
    for i, a in enumerate(p.get("anchors", []) if isinstance(p.get("anchors"), list) else []):
        if not isinstance(a, dict):
            continue
        if isinstance(a.get("keywords"), list) and any(not isinstance(k, str) or not k.strip() for k in a["keywords"]):
            errs.append(f"book-toc.md:{at('name', a.get('name'))} `anchors[{i}].keywords`에 빈 낱말이 있다")
        if isinstance(a.get("min_total"), int) and a["min_total"] < 1:
            errs.append(f"book-toc.md:{at('min_total', a['min_total'])} `anchors[{i}].min_total` 값 {a['min_total']}: 1 이상이어야 한다")
        if isinstance(a.get("chapters"), list) and (bad := [n for n in a["chapters"] if n not in nos]):
            errs.append(f"book-toc.md:{at('name', a.get('name'))} `anchors[{i}].chapters`에 없는 장 번호 {bad} (있는 장: {sorted(nos)})")
    def num(path):
        v = get_path(p, path)
        return v if isinstance(v, (int, float)) and not isinstance(v, bool) else None
    for path, test, want in [("narrator.person", lambda v: v in (1, 3), "1(1인칭) 또는 3(3인칭)"),
                             ("length.tolerance", lambda v: 0 < v < 1, "0과 1 사이 (예: 0.10)"),
                             ("review.story_pass", lambda v: 0 < v <= 10, "10점 만점 점수"),
                             ("review.body_pass", lambda v: 0 < v <= 10, "10점 만점 점수"),
                             ("review.story_critic_min", lambda v: 0 < v <= 10, "10점 만점 점수"),
                             ("review.story_proof_weight", lambda v: 0 <= v <= 1, "0과 1 사이"),
                             ("review.rounds_before_user_check", lambda v: v >= 1, "1 이상"),
                             ("length.target_pages", lambda v: v > 0, "1 이상"),
                             ("length.chars_per_page", lambda v: v > 0, "1 이상 (원고지 200)"),
                             ("base_year", lambda v: 1000 <= v <= 3000, "네 자리 연도")]:
        v = num(path)
        if v is not None and not test(v):
            errs.append(f"book-toc.md:{key_line(text, path)} `{path}` 값 {v}이 범위를 벗어났다 ({want})")
    lo, hi = num("wit.per_chapter_min"), num("wit.per_chapter_max")
    if lo is not None and hi is not None and lo > hi:
        errs.append(f"book-toc.md:{key_line(text, 'per_chapter_max')} `wit.per_chapter_max`가 per_chapter_min보다 작다")
    pub = p.get("publish", {}) if isinstance(p.get("publish"), dict) else {}
    opt = {"publisher": str, "pub_date": str, "copyright_holder": str, "isbn": (str, type(None)),
           "copyright_year": (int, type(None)), "third_party_verified": bool,
           "colophon_note": (str, type(None))}
    for k, typ in opt.items():
        if k in pub and not isinstance(pub[k], typ):
            errs.append(f"book-toc.md:{key_line(text, k)} `publish.{k}` 값 {pub[k]!r}의 형식이 틀렸다")
    eb = pub.get("ebook")
    if eb is not None:
        if not isinstance(eb, dict):
            errs.append(f"book-toc.md:{key_line(text, 'ebook')} `publish.ebook`은 객체여야 한다")
        else:
            for k, typ in {"design": str, "description": str, "og_description": (str, type(None)), "cover_copy": str,
                           "cover_title_lines": list, "synopsis": list}.items():
                if k in eb and not isinstance(eb[k], typ):
                    errs.append(f"book-toc.md:{key_line(text, k)} `publish.ebook.{k}` 값 {eb[k]!r}의 형식이 틀렸다")
            if isinstance(eb.get("cover_title_lines"), list) and len(eb["cover_title_lines"]) > 2:
                errs.append(f"book-toc.md:{key_line(text, 'cover_title_lines')} `publish.ebook.cover_title_lines`는 두 줄까지다 (셋째 줄부터는 표지에 나오지 않는다)")
            for k, need in (("epigraph", ("lines", "attr_lines")), ("back_quote", ("lines", "attr_lines"))):
                v = eb.get(k)
                if v is None:
                    continue
                if not isinstance(v, dict) or any(not isinstance(v.get(x), list) for x in need):
                    errs.append(f"book-toc.md:{key_line(text, k)} `publish.ebook.{k}`는 null 또는 "
                                f"{{\"lines\": [...], \"attr_lines\": [...]}} 형식이어야 한다 (지금 {str(v)[:40]})")
    return errs


def strings_with_path(obj, path=""):
    if isinstance(obj, str):
        yield path, obj
    elif isinstance(obj, dict):
        for k, v in obj.items():
            yield from strings_with_path(v, f"{path}.{k}" if path else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from strings_with_path(v, f"{path}[{i}]")


def line_of(text, needle):
    i = text.find(needle)
    return text.count("\n", 0, i) + 1 if i >= 0 else 0


def headers(txt):
    keys = {"입력": r"^입력:\s*(\S+)", "sha": r"^입력 sha256:\s*([0-9a-f]{64})", "score": r"^판정 점수:\s*([\d.]+)",
            "reds": r"^남은 🔴:\s*(\d+)", "verdict": r"^판정:\s*(통과|재수정|동결)", "critic": r"^CRITIC:\s*([\d.]+)"}
    out = {}
    for k, pat in keys.items():
        m = re.search(pat, txt, re.M)
        out[k] = m.group(1) if m else None
    return out


def run_dirs(root):
    base = root / "02_draft"
    return sorted(d for d in base.iterdir() if d.is_dir() and booktoc.RUN_RE.match(d.name)) if base.exists() else []


def ensemble_files(root, run):
    story = sorted((root / "01_test" / run).glob("00[b-z]_story-ensemble-*.md"))
    groups = {}
    for f in (root / "02_draft" / run).glob("0[68]_ensemble-*.md"):
        m = re.match(r"^0[68]_ensemble-(\d+)(?:-(part\d+|overall))?\.md$", f.name)
        if m:
            groups.setdefault(m.group(2) or "", []).append((int(m.group(1)), f))
    return [story] + [[f for _, f in sorted(g)] for g in groups.values()]


def lint(root, skill_dir=None):
    sd = Path(skill_dir) if skill_dir else SKILL_DIR
    r = Report()
    def rel(p):
        for base in (root, sd.parent):
            try:
                return str(p.relative_to(base))
            except ValueError:
                pass
        return str(p)

    # L1 스킬 구조 (Agent Skills 표준: 폴더 하나에 SKILL.md + references·scripts·templates)
    sm = sd / "SKILL.md"
    if not sm.exists():
        r.fail("L1", f"SKILL.md 없음: {rel(sm)}")
    else:
        fm = frontmatter(sm)
        if not re.search(rf"^name:\s*{SKILL_NAME}\s*$", fm, re.M):
            r.fail("L1", f"{rel(sm)} frontmatter name이 '{SKILL_NAME}'이 아니다 (소문자·숫자·하이픈만)")
        m = re.search(r'^description:\s*"?(.*?)"?\s*$', fm, re.M)
        if not m or not m.group(1).strip():
            r.fail("L1", f"{rel(sm)} description 없음")
        elif len(m.group(1)) > 1024:
            r.fail("L1", f"{rel(sm)} description {len(m.group(1))}자 > 1024")
        if len(sm.read_text(encoding="utf-8").split("\n")) > 500:
            r.fail("L1", f"{rel(sm)} 500줄 초과. references/로 나눈다")
    for st in STAGES:
        ag = sd / "agents" / f"{SKILL_NAME}-{st}.md"
        if not ag.exists():
            r.fail("L1", f"서브 에이전트 없음: {rel(ag)}")
        elif not re.search(rf"^name:\s*{SKILL_NAME}-{st}\s*$", frontmatter(ag), re.M):
            r.fail("L1", f"{rel(ag)} frontmatter name이 '{SKILL_NAME}-{st}'가 아니다")
        if not (sd / "references" / f"stage-{st}.md").exists():
            r.fail("L1", f"단계 문서 없음: references/stage-{st}.md")
    for need in ("references/workflow.md", "references/ledger.md", "references/reviewers.md", "templates/book-toc.template.md",
                 "templates/storyline.template.md", "templates/ebook/plain.html"):
        if not (sd / need).exists():
            r.fail("L1", f"스킬 자원 없음: {need}")
    for old in (root / ".claude" / "book-toc.md", root / ".claude" / "reviewers.md", root / ".claude" / "scripts"):
        if old.exists():
            r.fail("L1", f"옛 경로 {rel(old)}가 남아 있다. book-toc.md는 프로젝트 폴더로, 나머지는 스킬 폴더로 옮긴다")
    bt = root / "book-toc.md"
    if bt.exists():
        for i, ln in enumerate(bt.read_text(encoding="utf-8").split("\n"), 1):
            if re.search(r"\.claude/(scripts|templates|book-toc|reviewers)|`/(storyline|research|write|review|publish)`", ln):
                r.fail("L1", f"book-toc.md:{i} 옛 경로·명령이 남아 있다: {ln.strip()[:60]}")
    for f in (root / ".claude" / "skills").glob("*.md") if (root / ".claude" / "skills").exists() else []:
        r.fail("L1", f"평면 스킬 파일 {rel(f)}. 스킬은 <이름>/SKILL.md 폴더여야 한다")
    # 설치본 동기화: 원본은 프로젝트의 novel-writing/ (있을 때). 설치본에서 린터를 돌려도 원본과 비교한다
    src = root / SKILL_NAME if (root / SKILL_NAME / "SKILL.md").exists() else sd
    inst = root / ".claude" / "skills" / SKILL_NAME
    if inst.exists() and inst.resolve() != src.resolve() and tree_digest(inst) != tree_digest(src):
        r.warn("L1", f"설치본 {rel(inst)}가 원본 {rel(src)}과 다르다. python3 tools/install_skill.py --target claude-project 로 다시 설치한다")
    agents_dir = root / ".claude" / "agents"
    for a in sorted((src / "agents").glob("*.md")) if inst.exists() else []:
        want = a.read_text(encoding="utf-8").replace("{{SKILL_DIR}}", f".claude/skills/{SKILL_NAME}")
        for got in (agents_dir / a.name, inst / "agents" / a.name):
            if not got.exists() or got.read_text(encoding="utf-8") != want:
                r.warn("L1", f"서브 에이전트 설치본 {rel(got)}가 원본과 다르거나 없다. 다시 설치한다")

    # L2
    toc = root / "book-toc.md"
    if not toc.exists():
        r.fail("L2", f"프로젝트 폴더({root})에 book-toc.md가 없다. {sd / 'templates' / 'book-toc.template.md'}를 복사해 채운다")
        return r
    toc_text = toc.read_text(encoding="utf-8")
    mb = re.search(r"```json\s*\n(.*?)\n```", toc_text, re.S)
    if not mb:
        r.fail("L2", "book-toc.md에 ```json 블록이 없다 (템플릿의 블록을 복사한다)")
        return r
    try:
        p = json.loads(mb.group(1))
    except json.JSONDecodeError as e:
        base = toc_text.count("\n", 0, mb.start(1))
        hint = {"Expecting ',' delimiter": "이 줄 끝에 쉼표가 빠졌다",
                "Expecting property name enclosed in double quotes": "마지막 항목 뒤에 남은 쉼표를 지우거나, 키를 큰따옴표로 감싼다",
                "Expecting value": "값이 비었거나 끝 쉼표가 남았다",
                "Expecting ':' delimiter": "키 뒤에 콜론(:)이 빠졌다",
                "Unterminated string starting at": "닫는 큰따옴표가 빠졌다"}.get(e.msg, "쉼표·따옴표·괄호를 확인한다")
        ln = base + e.lineno - (1 if e.msg == "Expecting ',' delimiter" else 0)
        r.fail("L2", f"book-toc.md:{ln} 블록 JSON 문법 오류: {hint} (원문: {e.msg})")
        return r
    schema_errs = check_schema(p, toc_text)
    for x in schema_errs:
        r.fail("L2", x)
    for k in REQUIRED_KEYS:
        if k not in p and not any(x.startswith(f"블록 키 `{k}") for x in schema_errs):
            r.fail("L2", f"블록 키 `{k}`가 없다 (템플릿의 같은 키를 복사해 채운다)")
    seen_n = {}
    publishing = any(re.search(r"^stage:\s*review done", ledger(d.name, root), re.M) and not is_finished(d.name, root)
                     for d in run_dirs(root))
    for path, s in strings_with_path(p):
        if re.search(r"<[^<>]+>", s):
            needle = json.dumps(s, ensure_ascii=False)
            seen_n[needle] = seen_n.get(needle, 0) + 1
            pos, n = -1, seen_n[needle]
            for _ in range(n):
                pos = toc_text.find(needle, pos + 1)
            ln = toc_text.count("\n", 0, pos) + 1 if pos >= 0 else line_of(toc_text, s)
            msg = f"book-toc.md:{ln} 블록 `{path}` 빈칸: {s[:40]}"
            if path.startswith("publish.") and not publishing:
                r.warn("L2", msg + " (publish 단계 전까지 채운다)")
            else:
                r.fail("L2", msg)
    narrative = re.sub(r"`[^`\n]*`", lambda m: " " * len(m.group(0)), re.sub(r"```.*?```", lambda m: "\n" * m.group(0).count("\n"), toc_text, flags=re.S))
    for m in re.finditer(r"<[^<>\n`]*[가-힣][^<>\n`]*>", narrative):  # 한글이 든 <…>만 빈칸으로 본다
        r.fail("L2", f"book-toc.md:{narrative.count(chr(10), 0, m.start()) + 1} 서술 섹션 빈칸: {m.group(0)[:40]}")
    if schema_errs or [k for k in REQUIRED_KEYS if k not in p]:
        return r  # 형식이 틀린 블록으로 계산하면 오류가 꼬리를 문다. 위 항목부터 고친다
    if sum(c["pages"] for c in p["chapters"]) != p["length"]["target_pages"]:
        r.fail("L2", f"book-toc.md:{key_line(toc_text, 'target_pages')} 장 매수 합 {sum(c['pages'] for c in p['chapters'])} ≠ length.target_pages {p['length']['target_pages']}")
    if p["review"]["story_panel"] not in ("lite", "standard", "extended"):
        r.fail("L2", f"book-toc.md:{key_line(toc_text, 'story_panel')} review.story_panel 값 '{p['review']['story_panel']}' (가능: lite, standard, extended)")
    if p["structure_mode"] not in ("chapter", "part"):
        r.fail("L2", f"structure_mode 값 '{p['structure_mode']}' (가능: chapter, part)")
    if p["structure_mode"] == "part":
        listed = [n for pt in p.get("parts", []) for n in pt["chapters"]]
        if sorted(listed) != sorted(c["no"] for c in p["chapters"]) or len(listed) != len(set(listed)):
            r.fail("L2", "structure_mode가 part인데 parts가 모든 장을 한 번씩 담지 않음")
    ui = root / "00_storyline" / "storyline.md"
    if ui.exists():
        utext = re.sub(r"`[^`\n]*`", lambda m: " " * len(m.group(0)), ui.read_text(encoding="utf-8"))
        for m in re.finditer(r"<[^<>\n`]*[가-힣][^<>\n`]*>", utext):
            r.fail("L2", f"00_storyline/storyline.md:{utext.count(chr(10), 0, m.start()) + 1} 양식 빈칸 {m.group(0)[:40]} (채우거나 그 줄을 지운다)")
    if not p["characters"]:
        r.fail("L2", "characters가 비어 있다. 본문에 반드시 나올 이름·호칭을 넣는다")
    pub = p["publish"]
    fm = pub.get("formats", ["ebook"])
    if legacy := [x for x in fm if x in LEGACY_FORMATS]:
        r.fail("L2", f"book-toc.md:{key_line(toc_text, 'formats')} publish.formats에 더는 만들지 않는 형식 {legacy}이 있다. [\"ebook\"]로 바꾼다. "
                     f"이미 출판한 run이면 출판 뒤 수정 절차로 gate: block-change → approved publish.formats 와 gate: remove-{legacy[0]} → approved 를 남긴다")
    elif not fm or any(x not in FORMATS for x in fm):
        r.fail("L2", f"book-toc.md:{key_line(toc_text, 'formats')} publish.formats 값 {fm} (가능: {list(FORMATS)})")
    if left := [k for k in DOCX_ONLY_KEYS if k in pub]:
        r.warn("L2", f"book-toc.md:{key_line(toc_text, left[0])} 예전 docx 조판 키 {left}는 더 쓰지 않는다. 지워도 된다")
    if "ebook" in fm:
        design = pub.get("ebook", {}).get("design", "plain")
        if not any((b / f"{design}.html").exists() for b in (root / "designs" / "ebook", sd / "templates" / "ebook")):
            have = sorted({x.stem for b in (root / "designs" / "ebook", sd / "templates" / "ebook") for x in b.glob("*.html")})
            r.fail("L2", f"book-toc.md:{key_line(toc_text, 'design')} publish.ebook.design '{design}' 파일이 없다 (가능: {have}). "
                         f"작품 전용 디자인은 {root / 'designs' / 'ebook' / (design + '.html')}에 {sd / 'templates' / 'ebook' / 'plain.html'}을 복사해 만든다")
    tp_ok = any(re.search(r"^gate:\s*waiver-fictional_reviewer\s*→\s*approved\b", ledger(d.name, root), re.M)
                and run_params(d.name, root)["title"] == p["title"] for d in run_dirs(root))
    _pd, _cy = str(pub.get("pub_date") or ""), pub.get("copyright_year")
    _m = re.search(r"(\d{4})\s*년", _pd)
    if _m and _cy and int(_m.group(1)) != int(_cy):
        r.warn("L2", f"발행 연월 '{_pd}'과 저작권 연도 {_cy}가 다르다. 판권면에 둘 다 찍힌다. 의도가 아니면 publish.copyright_year를 발행 연도로 맞춘다")
    if any(n in THIRD_PARTY for n in p.get("back_matter", [])) and not pub.get("third_party_verified") and not tp_ok:
        r.warn("L2", f"back_matter에 제3자 글 {[n for n in p['back_matter'] if n in THIRD_PARTY]}이 있다. 실제 글이면 publish.third_party_verified를 true로, 가상 평자면 run 원장에 fictional_reviewer 승인을 남긴다")

    # L3
    rw = root / "_archive" / "retired_works.json"
    retired = json.loads(rw.read_text(encoding="utf-8")) if rw.exists() else {}
    tokens = {t: f"지난 작품 『{w}』" for t, w in past_work_tokens(root).items()}  # run 스냅샷에서 자동 수집
    tokens.update({t: f"지난 작품 『{w}』" for w, ts in retired.items() if not w.startswith("_") for t in ts})
    tokens.update({t: "현재 작품" for t in work_tokens(p)})
    pats3 = {}
    for t in tokens:
        if len(t) >= 3:
            pats3[t] = re.compile(re.escape(t))
        elif len(t) == 2:  # 두 글자 이름은 앞이 한글이 아니고 뒤에 조사·공백·문장부호가 올 때만
            pats3[t] = re.compile(r"(?<![가-힣])" + re.escape(t) + r"(?=[이가은는을를의와과도에께]|[\s.,)\]'\"·]|$)")
    for d in system_docs(root, sd):
        for i, ln in lines_without_examples(d):
            for t, rx in pats3.items():
                if rx.search(ln):
                    r.fail("L3", f"{rel(d)}:{i} {tokens[t]} 토큰 '{t}' (블록 키로 바꾸거나 '예시(' 라벨)")

    # L4
    n_pr = p["style"]["principles"]
    pats = [
        (r"em dash\s*허용", "em dash 허용 표기 (블록 style.em_dash와 충돌)"),
        (r"위트[^\n|]{0,25}?\d+\s*[~\-]\s*\d+\s*회", "위트 횟수 숫자 (블록 wit 키로)"),
        (r"\d+(\.\d+)?\s*점?\s*(이상|미만)\s*(이면|으로|통과)", "통과선 숫자 (블록 review 키로)"),
        (r"\d+\s*매(?![일번])", "매수 숫자 (블록 length·chapters 키로)"),
    ]
    for d in system_docs(root, sd):
        for i, ln in lines_without_examples(d):
            for pat, why in pats:
                if re.search(pat, ln):
                    r.fail("L4", f"{rel(d)}:{i} {why}: {ln.strip()[:50]}")
            for m in re.finditer(r"(\d+)\s*원칙", ln):
                if int(m.group(1)) != n_pr:
                    r.fail("L4", f"{rel(d)}:{i} '{m.group(0)}' (블록 style.principles = {n_pr})")

    # L5
    open_runs = [d.name for d in run_dirs(root) if not is_finished(d.name, root)]
    if not open_runs:
        ui_sl = root / "00_storyline" / "storyline.md"
        if ui_sl.exists() and p["last_line"].rstrip(".") not in ui_sl.read_text(encoding="utf-8"):
            r.warn("L5", f"블록 last_line이 00_storyline/storyline.md에 없다: '{p['last_line']}'. 새 작품이면 초안의 마지막 문장을 적는다")
    else:
        run = open_runs[-1]
        snap = root / "01_test" / run / "book-toc.snapshot.md"
        if snap.exists() and load_params(snap) != p:
            r.fail("L5", f"블록이 run {run} 스냅샷과 다르다. 의도한 변경이면 스냅샷을 갱신하고 원장에 gate를 남긴다")
        sl = root / "01_test" / run / "storyline.md"
        if sl.exists() and "통과 시점" in "".join(f.read_text(encoding="utf-8") for f in ensemble_files(root, run)[0]):
            s = sl.read_text(encoding="utf-8")
            for c in p["characters"]:
                if c not in s:
                    r.fail("L5", f"블록 인물 '{c}'이 통과본 {rel(sl)}에 없음")
            if p["last_line"].rstrip(".") not in s:
                r.fail("L5", f"블록 last_line이 통과본에 없음: {p['last_line']}")
            for c in p["chapters"]:
                if f"{c['no']}장. {c['title']}" not in s:
                    r.fail("L5", f"장 제목 '{c['no']}장. {c['title']}'이 통과본에 없음")

    # L6
    for d in [root] + [x for x in root.rglob("*") if x.is_dir() and ".git" not in x.parts]:
        if re.search(r"[가-힣ㄱ-ㅎㅏ-ㅣ]", d.name):
            r.fail("L6", f"폴더 이름에 한글이 있다: {d.name}. 영문 소문자·숫자·하이픈·밑줄로 바꾼다 (작품 폴더는 docs/<영문-슬러그>/)")
    if (root / "00_user_input").exists():
        r.fail("L6", "옛 폴더 이름 00_user_input이 남아 있다. 00_storyline으로 이름을 바꾼다")
    ui =sorted(f.name for f in (root / "00_storyline").iterdir() if not f.name.startswith(".")) if (root / "00_storyline").exists() else []
    if ui != ["storyline.md"]:
        how = (f"{sd / 'templates' / 'storyline.template.md'}를 00_storyline/storyline.md로 복사해 채운다"
               if "storyline.md" not in ui else "storyline.md 말고 다른 파일은 _archive/로 옮긴다")
        r.fail("L6", f"00_storyline에는 storyline.md 하나만 둔다 (지금: {ui}). {how}")
    for stage in ("01_test", "02_draft", "03_output"):
        base = root / stage
        if base.exists():
            for d in base.iterdir():
                if d.is_dir() and not booktoc.RUN_RE.match(d.name):
                    r.fail("L6", f"run 이름 규칙 위반: {rel(d)}")
    for d in run_dirs(root):
        if not (root / "01_test" / d.name).exists():
            r.fail("L6", f"{rel(d)}에 짝 01_test/{d.name} 없음")
        if not (d / "00_RUN_STATUS.md").exists():
            r.fail("L6", f"{rel(d)}에 원장 00_RUN_STATUS.md 없음")
        if not (root / "01_test" / d.name / "book-toc.snapshot.md").exists():
            r.fail("L6", f"01_test/{d.name}에 블록 스냅샷 book-toc.snapshot.md 없음")

    # L7
    for name, cap in CAPS.items():
        f = root / name
        if f.exists() and f.stat().st_size > cap:
            r.fail("L7", f"{name} {f.stat().st_size:,}B > {cap:,}B")
    for name, cap in SKILL_CAPS.items():
        f = sd / name
        if f.exists() and f.stat().st_size > cap:
            r.fail("L7", f"{name} {f.stat().st_size:,}B > {cap:,}B")

    # L8
    for d in run_dirs(root):
        run, led, closed = d.name, ledger(d.name, root), is_closed(d.name, root)
        rp = run_params(run, root)
        lines = led.split("\n")
        waiver_at = {}   # id -> [(줄 번호, 줄 내용)]
        for i, ln in enumerate(lines):
            m = re.match(r"^waiver:\s*(\S+)(.*)$", ln)
            if m:
                waiver_at.setdefault(m.group(1), []).append((i, m.group(2)))
        waived = set(waiver_at)
        close_at = [i for i, ln in enumerate(lines) if re.match(r"^gate:\s*close-run\s*→\s*approved\b", ln)]
        close_ok = closed and bool(close_at)
        paired = {i for i, _, _ in paired_waivers(led)}   # 짝짓기 규칙은 booktoc.paired_waivers 하나

        def ok_waiver(cid, about=None, _wa=waiver_at, _pd=paired):
            """승인 줄과 짝지어진 waiver만 인정한다. about이 주어지면 그 이름(파일명)을 적은 waiver만 센다."""
            return any(wi in _pd and (not about or about in rest) for wi, rest in _wa.get(cid, []))

        def emit(cid, msg, _run=run, _ok=ok_waiver, _c=close_ok):
            if _ok(cid):
                if _c:
                    r.folded[_run] = r.folded.get(_run, 0) + 1
                r.warn("L8", f"{_run} [{cid} waived] {msg}")
            else:
                r.fail("L8", f"{_run} [{cid}] {msg}")

        for wi_line, wl in [(i, ln) for i, ln in enumerate(lines) if ln.startswith("waiver:")]:
            wid = wl.split()[1] if len(wl.split()) > 1 else "?"
            if wi_line in paired:
                continue
            r.fail("L8", f"{run} 원장 {wi_line + 1}줄 waiver '{wid}'에 짝이 되는 사용자 승인 줄이 없다 (gate: waiver-{wid} → approved \"<원문>\" 또는 닫힌 run의 close-run 승인)")

        for tag, series in ensemble_groups(run, root).items():
            story = tag == "story"
            seen, prev_src, prev_score, k = {}, None, None, 0
            for f in series:
                txt = f.read_text(encoding="utf-8")
                h = headers(txt)
                if not all(h[x] for x in ("입력", "sha", "score", "reds", "verdict")):
                    emit("ensemble_header", f"{f.name}에 머리 줄(입력, 입력 sha256, 판정 점수, 남은 🔴, 판정)이 없다")
                    continue
                k += 1
                src = f.parent / h["입력"]
                if not src.exists():
                    emit("ensemble_integrity", f"{f.name}의 입력 파일 {src.name}이 없다")
                elif sha(src) != h["sha"]:
                    emit("ensemble_integrity", f"{f.name}의 입력 {src.name} 해시가 기록과 다르다 (채점 뒤 입력이 바뀜)")
                score, reds = float(h["score"]), int(h["reds"])
                if h["sha"] in seen:
                    pf, ps = seen[h["sha"]]
                    if h["verdict"] != "동결" or "점수 동결" not in txt or score != ps:
                        emit("review_freeze", f"{f.name} 입력이 {pf}와 같은데 동결하지 않음 (판정: 동결, 점수 {ps}를 옮겨야 한다)")
                else:
                    if h["verdict"] == "동결":
                        emit("review_freeze", f"{f.name}이 동결로 표시됐지만 같은 입력의 앞선 라운드가 없다")
                    if k > 1 and "## 바뀐 자리" not in txt:
                        emit("change_log", f"{f.name}에 '## 바뀐 자리' 섹션이 없다")
                    if prev_src is not None and prev_src.exists() and src.exists() and prev_score is not None:
                        ratio = difflib.SequenceMatcher(None, prev_src.read_text(encoding="utf-8"),
                                                        src.read_text(encoding="utf-8"), autojunk=False).quick_ratio()
                        if ratio >= SMALL_EDIT_RATIO and score - prev_score >= SMALL_EDIT_JUMP:
                            r.warn("L8", f"{run} {f.name} 입력이 직전과 {ratio:.1%} 같은데 점수가 {score - prev_score:+.2f} 올랐다. 바뀐 자리 인용을 확인한다")
                rv = rp["review"]
                if h["verdict"] == "통과":
                    th = rv["story_pass"] if story else rv["body_pass"]
                    short = []
                    if score < th:
                        short.append(f"판정 점수 {score} < 통과선 {th}")
                    if reds:
                        short.append(f"남은 🔴 {reds}건")
                    if story and rv["story_panel"] in ("standard", "extended"):
                        if not h["critic"]:
                            short.append("CRITIC 줄 없음")
                        elif float(h["critic"]) < rv["story_critic_min"]:
                            short.append(f"CRITIC {h['critic']} < {rv['story_critic_min']}")
                    if short and not ok_waiver("open_red", f.name):
                        emit("pass_threshold", f"{f.name} 통과 판정이 기준 미달: {', '.join(short)} (승인된 open_red waiver 없음)")
                limit = rv["rounds_before_user_check"]
                gate_id = "storyline-rounds" if story else "review-rounds"
                opts = "abc" if story else "ab"
                answers = len([x for x in lines if re.match(rf"^gate:\s*{gate_id}\s*→\s*[{opts}]\b", x)
                               and (tag in ("story", "") or f"({tag})" in x)])   # 장편 부 계열은 응답에 (part<n>)을 적는다
                if k > limit and answers < k - limit:
                    emit("round_gate", f"{f.name}은 {k}라운드다. {limit}라운드를 넘긴 라운드마다 사용자 선택(gate: {gate_id} → {'|'.join(opts)})이 하나씩 있어야 한다 (지금 {answers}개)")
                seen.setdefault(h["sha"], (f.name, score))
                prev_src, prev_score = src, score
        # 머리 줄이 없는 옛 run을 위한 보조 검사: 원고 쌍 해시
        for prev, cur_, ens in (("03_draft-v1.md", "05_draft-v2.md", "06_ensemble-1.md"),
                                ("05_draft-v2.md", "07_draft-v3.md", "08_ensemble-2.md")):
            e = d / ens
            if e.exists() and not headers(e.read_text(encoding="utf-8"))["sha"] and sha(d / prev) and sha(d / prev) == sha(d / cur_) \
                    and "점수 동결" not in e.read_text(encoding="utf-8"):
                emit("review_freeze", f"{cur_}이 {prev}와 같은데 {ens}가 채점함")

        # 단계 게이트(스토리·본문 공통): 다음 단계 산출물이 있으면 마지막 reopen 뒤에서
        # 최신 합평이 통과했고 그 뒤 사용자 승인이 있거나, 최신 합평 파일을 적은 open_red가 승인되어 있어야 한다.
        # 단계 순서: 어떤 단계가 done이면 앞 단계도 모두 done이어야 한다 (원장 한 줄로 건너뛰기 방지)
        done = {s for s in STAGES if re.search(rf"^stage:\s*{s} done", led, re.M)}
        for i, s in enumerate(STAGES):
            if s in done and (miss := [x for x in STAGES[:i] if x not in done]):
                emit("stage_order", f"stage: {s} done이 있는데 앞 단계 {miss}의 done이 없다")
        if "storyline" in done:
            ok, why = gate_status(run, root, "story")
            if not ok:
                emit("gate_log", f"stage: storyline done이 있는데 스토리 게이트가 닫히지 않았다: {why}")
        if "review" in done:
            ok, why = gate_status(run, root, "body")
            if not ok:
                emit("gate_log", f"stage: review done이 있는데 본문 게이트가 닫히지 않았다: {why}")
        # 단계 게이트: 다음 단계 산출물이 있으면 그 게이트가 닫혀 있어야 한다 (판정은 booktoc.gate_status 하나)
        story_later = [x for x in ("01_research-notes.md", "02_outline.md", "03_draft-v1.md") if (d / x).exists()]
        if story_later:
            ok, why = gate_status(run, root, "story")
            if not ok:
                emit("gate_log", f"스토리 게이트: {why}. {story_later[0]}이 있으므로 이 게이트가 먼저 닫혀야 한다")
        body_later = [x for x in (final_draft_name(rp), "10_review-editor.md") if (d / x).exists()]
        if body_later:
            ok, why = gate_status(run, root, "body")
            if not ok:
                emit("gate_log", f"본문 게이트: {why}. {body_later[0]}이 있으므로 이 게이트가 먼저 닫혀야 한다")

        # 감사 수정은 끝난 run에서 사용자 승인이 먼저 있어야 한다
        pa = [i for i, ln in enumerate(lines) if re.match(r"^stage:\s*post-audit-fix", ln)]
        pg = [i for i, ln in enumerate(lines) if re.match(r"^gate:\s*post-audit\s*→\s*approved\b", ln)]
        prev = -1
        for k in pa:   # 감사 수정마다 그 앞(직전 수정 이후)에 승인이 있어야 한다
            if not any(prev < g < k for g in pg):
                emit("post_audit", f"원장 {k + 1}줄 stage: post-audit-fix 앞에 gate: post-audit → approved 줄이 없다")
            prev = k

        # 작가 산출물 제거는 승인이 있어야 한다: MANIFEST에서 옮겨져 지금 없는 03_output·09 파일
        man = root / "_archive" / "MANIFEST.tsv"
        if man.exists():
            seen_src = set()
            for row in man.read_text(encoding="utf-8").split("\n")[1:]:
                cols = row.split("\t")
                if len(cols) < 2:
                    continue
                src = cols[1]
                m = re.match(rf"^(03_output/{run}/[^/]+\.(docx|html|md|pdf)|02_draft/{run}/09[^/]*\.md)$", src)
                if m and not (root / src).exists() and src not in seen_src:
                    seen_src.add(src)
                    base = Path(src).name
                    fmt = {v: k for k, v in ALL_FORMATS.items()}.get(base)   # ebook.html ↔ ebook, (예전) final.docx ↔ docx: 어느 이름으로 승인해도 같다
                    names = [base] + ([fmt] if fmt else [])
                    if not any(re.search(rf"^gate:\s*remove-{re.escape(nm)}\s*→\s*approved\b", led, re.M) for nm in names):
                        emit("remove_output", f"작가 산출물 {src}이 옮겨졌는데 gate: remove-{fmt or base} → approved 줄이 없다")

        # 작가 이름으로 나가는 글: 이 run에서 원고를 쓰고 아직 출판하지 않았으면 back_matter 섹션마다 author-text 승인이 있어야 한다
        # (SKILL.md "사용자 게이트"). rework가 물려받은 원고(inherited)와 이 규칙 전에 출판한 run은 지난 기록을 따른다.
        if (re.search(r"^stage:\s*write done(?!.*inherited)", led, re.M)
                and not re.search(r"^stage:\s*publish done", led, re.M)):
            for sec in (rp.get("back_matter") or []):
                if not re.search(rf"^gate:\s*author-text-{re.escape(sec)}\s*→\s*approved\b", led, re.M):
                    emit("author_text", f"back_matter '{sec}'에 gate: author-text-{sec} → approved 줄이 없다 (작가 원문, 승인한 초안, BLACK에게 쓰라는 요청 중 하나)")

        # 작가 산출물 잠금: 마지막 lock 줄 이후 back_matter·formats가 줄거나 스냅샷이 바뀌었으면 그 뒤에 승인·기록이 있어야 한다
        locks = [(i, ln) for i, ln in enumerate(lines) if ln.startswith("lock:")]
        pub_done = [i for i, ln in enumerate(lines) if re.match(r"^stage:\s*publish done", ln)]
        if not locks and pub_done:
            emit("lock", f"출판을 마쳤는데 잠금 줄이 없다 (python3 <스킬>/scripts/lock_run.py --run {run})")
        elif not locks and not re.search(r"^gate:\s*new-run\b", led, re.M):
            r.warn("L8", f"{run} 잠금 줄이 없다. new_run.py로 연 run은 자동으로 생긴다 (python3 <스킬>/scripts/lock_run.py --run {run})")
        elif locks and pub_done and pub_done[-1] > locks[-1][0]:
            emit("lock", f"원장 {pub_done[-1] + 1}줄 publish done 뒤에 잠금 줄이 없다 (lock_run.py)")
        busy = booktoc.open_post_audit(run, root)
        if busy:
            r.warn("L8", f"{run} 출판 뒤 수정 진행 중(원장 {busy[0] + 1}줄, owner {busy[1] or '-'}). 시작한 세션이 republish.py --owner로 마친다. "
                         f"그 세션이 끊겼으면 SKILL.md \"출판 뒤 수정\" 0단계(이어받기·버리기)")
        for msg in lock_violations(run, root):   # 구간 비교 규칙은 booktoc.lock_violations 하나
            emit("lock", msg)

        fin = d / final_draft_name(rp)
        if fin.exists():
            text = fin.read_text(encoding="utf-8")
            tp = [hh for hh, _ in split_back(text, rp) if hh[2:] in THIRD_PARTY]
            if tp and not rp["publish"].get("third_party_verified"):
                emit("fictional_reviewer", f"제3자 글 {tp}의 출처가 확인되지 않았다 (실제 글이면 third_party_verified: true)")

        if re.search(r"^stage:\s*publish done", led, re.M):
            out = root / "03_output" / run
            formats = rp["publish"].get("formats", ["ebook"])
            for need in ["metadata.md", "validate_report.txt"] + [FORMATS[x] for x in formats if x in FORMATS]:
                if not (out / need).exists():
                    emit("publish_files", f"03_output/{run}/{need} 없음")
            epi = rp["publish"].get("ebook", {}).get("epigraph")
            if "ebook" in formats and epi and not epi.get("source_verified"):
                emit("epigraph_source", "e북 제사 인용의 출처가 확인되지 않았다. 확인했으면 epigraph.source_verified를 true로, "
                                        "확인 없이 싣기로 했으면 사용자 승인(waiver: epigraph_source + gate: waiver-epigraph_source → approved), 빼기로 했으면 epigraph를 null로")
            if fin.exists():
                eb = out / "ebook.html" if "ebook" in formats and (out / "ebook.html").exists() else None
                busy_now = booktoc.open_post_audit(run, root)
                for x in validate(text, rp, eb)[0]:
                    emit("publish_gate", f"출판본 게이트 실패: {x}" + (" (출판 뒤 수정 진행 중: 산출물은 republish.py --owner가 다시 만든다. 손으로 만들지 않는다)" if busy_now else ""))
                if eb is not None:
                    import tempfile
                    from generate_ebook import build as build_ebook
                    with tempfile.TemporaryDirectory() as tdx:
                        regen = Path(tdx) / "e.html"
                        try:
                            build_ebook(text, rp, regen)
                            if regen.read_bytes() != eb.read_bytes():
                                r.warn("L8", f"{run} ebook.html이 지금 원고·스냅샷·디자인으로 다시 만든 결과와 다르다. "
                                             + ("출판 뒤 수정 진행 중: republish.py --owner가 다시 만든다(손으로 만들지 않는다)" if busy_now else
                                                "의도한 차이면 그대로 두고, 아니면 작가 승인 뒤 출판 뒤 수정(republish.py)으로 다시 만든다"))
                        except Exception as ex:  # noqa: BLE001
                            r.warn("L8", f"{run} e북 재생성 비교 실패: {ex}")
                meta = out / "metadata.md"
                if meta.exists():
                    mt = meta.read_text(encoding="utf-8")
                    if "—" in mt or "–" in mt:
                        emit("metadata", "metadata.md에 em dash")
                    if not re.search(r"분량:\s*[\d,]+자", mt):
                        emit("metadata", "metadata.md에 '분량: <글자 수>자' 줄이 없거나 형식이 다르다(예: '분량: 18,152자 (90.8매, …)'). "
                                         "출판 뒤 수정 때 republish.py가 이 줄을 맞춘다")
                    ch, _ = split_draft(text, rp)
                    n = sum(count_chars(v) for v in ch.values())
                    m = re.search(r"분량:\s*([\d,]+)자", mt)
                    if m and int(m.group(1).replace(",", "")) != n and busy_now:
                        r.warn("L8", f"{run} metadata 분량 {m.group(1)}자 ≠ 검증기 {n:,}자 (출판 뒤 수정 진행 중: republish.py --owner가 맞춘다)")
                    elif m and int(m.group(1).replace(",", "")) != n:
                        emit("metadata", f"metadata 분량 {m.group(1)}자 ≠ 검증기 {n:,}자. metadata.md의 분량 줄과 장 구성 표를 고친다 "
                                         f"(출판 뒤 수정이면 republish.py가 맞춘다)")
                    heads = re.findall(r"^##\s+(.+)$", mt, re.M)
                    miss = [s for s in META_SECTIONS if not any(s in hh for hh in heads)]
                    if miss:
                        emit("metadata", f"metadata에 publish 사양 섹션이 없다: {miss}")
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(booktoc.ROOT))
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args()
    r = lint(Path(a.root).resolve())
    shown = [w for w in r.warns
             if a.verbose or not any(w.startswith(f"L8 {run} [") and "waived]" in w for run in r.folded)]
    if not a.verbose:
        shown += [f"L8 {run} 닫힌 run, 승인된 기록 waiver {n}건 (원장 참조, 전부 보려면 --verbose)" for run, n in r.folded.items()]
    for w in shown:
        print("WARN", w)
    for f in r.fails:
        print("FAIL", f)
    print(f"\nlint: FAIL {len(r.fails)} / WARN {len(shown)}")
    sys.exit(1 if r.fails else 0)


if __name__ == "__main__":
    main()
