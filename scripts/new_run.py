"""새 run 열기 (references/workflow.md 2절).

사용:
  python3 <스킬>/scripts/new_run.py --mode same    --answer "<사용자 응답 원문>"
  python3 <스킬>/scripts/new_run.py --mode updated --answer "<사용자 응답 원문>"
  python3 <스킬>/scripts/new_run.py --mode rework  --from 20260505_01 --stage review --answer "<사용자 응답 원문>"

하는 일
  1. 오늘 날짜(또는 --date)로 다음 run 이름(YYYYMMDD_NN)을 정하고 01_test·02_draft·03_output 폴더를 만든다.
  2. 블록 스냅샷 01_test/<run>/book-toc.snapshot.md를 만든다 (rework는 지난 run의 스냅샷을 물려받는다).
  3. 원장 02_draft/<run>/00_RUN_STATUS.md에 status, gate: new-run 줄(응답 원문)을 남긴다.
  4. same·updated: 00_user_input/storyline.md를 01_test/<run>/storyline.md로 복사한다. 다음 단계는 storyline (지휘가 /novel-writing으로 이어 간다).
     rework: 지난 run의 결과를 --stage 직전 단계까지 물려받는다.
       research  storyline 통과본
       write     + 리서치 노트
       review    + 장면 설계서, 지난 최종본 → 새 03_draft-v1.md
     물려받은 단계마다 원장에 `stage: <스킬> done <날짜> (inherited from <run>)`을 남긴다.
"""
import argparse
import datetime
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from booktoc import ROOT, RUN_RE, final_draft_name, is_finished, is_part_mode, load_params, lock_line, open_post_audit, story_gate_open, waiver_approvals  # noqa: E402

STAGES = ["storyline", "research", "write", "review", "publish"]


def next_run(root, date):
    used = {d.name for s in ("01_test", "02_draft", "03_output") if (root / s).exists()
            for d in (root / s).iterdir() if d.is_dir() and RUN_RE.match(d.name)}
    n = 1
    while f"{date}_{n:02d}" in used:
        n += 1
    return f"{date}_{n:02d}"


def author_edited_paragraphs(root, run, p, scope="recent"):
    """작가가 출판 뒤 고친 문단을 (장 제목, 문단)으로 돌려준다. 기준 원고와 지금 최종본을 문단 단위로 비교한다.
    scope: recent = republish.py --prepare가 남긴 첫 보관본(출판 뒤 수정 절차 이후의 작가 수정만),
           all = MANIFEST에 남은 가장 이른 09 보관본(그 전의 원고 교체·전면 윤문까지), none = 보호하지 않음."""
    if scope == "none":
        return []
    name = final_draft_name(p)
    man = Path(root) / "_archive" / "MANIFEST.tsv"
    cur = Path(root) / "02_draft" / run / name
    if not man.exists() or not cur.exists():
        return []
    first = None
    for row in man.read_text(encoding="utf-8").split("\n")[1:]:
        c = row.split("\t")
        if len(c) >= 4 and scope == "recent" and not c[3].startswith("copy before post-audit edit"):
            continue
        if len(c) >= 3 and c[1] == f"02_draft/{run}/{name}" and (Path(root) / c[2]).exists():
            first = Path(root) / c[2]
            break
    if first is None:
        return []
    old = {x.strip() for x in first.read_text(encoding="utf-8").split("\n") if x.strip()}
    out, where = [], ""
    for ln in cur.read_text(encoding="utf-8").split("\n"):
        s = ln.strip()
        if s.startswith("# "):
            where = s[2:]
        elif s and s not in old:
            out.append((where, s))
    return out


def open_run(root, mode, answer, src_run=None, stage=None, date=None, protect="recent"):
    root = Path(root)
    date = date or datetime.date.today().strftime("%Y%m%d")
    today = f"{date[:4]}-{date[4:6]}-{date[6:]}"
    open_runs = sorted(x.name for x in (root / "02_draft").glob("*") if x.is_dir() and RUN_RE.match(x.name)
                       and not is_finished(x.name, root)) if (root / "02_draft").exists() else []
    if open_runs:
        raise SystemExit(f"끝나지 않은 run {open_runs[-1]}이 있다. 새 run을 열지 말고 그 run을 이어 쓴다 (references/workflow.md 2절)")
    if mode == "rework":
        if not src_run or stage not in ("research", "write", "review"):
            raise SystemExit("rework에는 --from <지난 run>과 --stage research|write|review가 필요하다")
        if not is_finished(src_run, root):
            raise SystemExit(f"{src_run}은 끝난 run이 아니다. 끝나지 않은 run은 새로 열지 말고 이어 쓴다")
        busy = open_post_audit(src_run, root)
        if busy:
            raise SystemExit(f"{src_run} 원장 {busy[0] + 1}줄의 출판 뒤 수정이 아직 끝나지 않았다. 그 수정이 republish.py로 끝난 뒤 rework를 연다. "
                             f"그 세션이 끊겼으면 republish.py --run {src_run} --status로 내용을 보고 작가에게 이어받기(--takeover)·버리기(--abandon)를 묻는다")
        if not story_gate_open(src_run, root):
            raise SystemExit(f"{src_run}의 스토리 게이트가 닫히지 않았다. 스토리 합평 통과와 사용자 a 응답(또는 승인된 waiver)이 없는 run은 물려받을 수 없다")
    if mode == "rework":  # 물려받을 파일이 모두 있는지 폴더를 만들기 전에 확인한다
        st, sd = root / "01_test" / src_run, root / "02_draft" / src_run
        snap = st / "book-toc.snapshot.md"
        p0 = load_params(snap if snap.exists() else root / "book-toc.md")
        need = [st / "storyline.md"]
        if STAGES.index(stage) > STAGES.index("research"):
            need.append(sd / "01_research-notes.md")
        if STAGES.index(stage) > STAGES.index("write"):
            need.append(sd / final_draft_name(p0))
        if missing := [str(x.relative_to(root)) for x in need if not x.exists()]:
            raise SystemExit(f"rework에 필요한 파일이 없다: {missing}. 아무 폴더도 만들지 않았다")
    elif not (root / "00_user_input" / "storyline.md").exists():
        raise SystemExit("00_user_input/storyline.md가 없다. 아무 폴더도 만들지 않았다")
    run = next_run(root, date)
    t, d, o = (root / s / run for s in ("01_test", "02_draft", "03_output"))
    for x in (t, d, o):
        x.mkdir(parents=True)
    lines = ["status: in-progress", f'gate: new-run → {mode} ({today}) "{answer}"']

    if mode in ("same", "updated"):
        shutil.copy(root / "book-toc.md", t / "book-toc.snapshot.md")
        shutil.copy(root / "00_user_input" / "storyline.md", t / "storyline.md")
        nxt = "storyline 단계 (/novel-writing \"스토리 합평하자\")"
    else:
        st, sd = root / "01_test" / src_run, root / "02_draft" / src_run
        snap = st / "book-toc.snapshot.md"
        shutil.copy(snap if snap.exists() else root / "book-toc.md", t / "book-toc.snapshot.md")
        p = load_params(t / "book-toc.snapshot.md")
        lines.append(f"inherit: {src_run}")
        shutil.copy(st / "storyline.md", t / "storyline.md")
        lines.append(f"stage: storyline done {today} (inherited from {src_run})")
        upto = STAGES.index(stage)
        if upto > STAGES.index("research"):
            shutil.copy(sd / "01_research-notes.md", d / "01_research-notes.md")
            lines.append(f"stage: research done {today} (inherited from {src_run})")
        if upto > STAGES.index("write"):
            src_final = sd / final_draft_name(p)
            if (sd / "02_outline.md").exists():
                shutil.copy(sd / "02_outline.md", d / "02_outline.md")
            if is_part_mode(p):  # 장편: 통합본을 부 헤딩에서 나눠 부 파일로 둔다
                chunks = re.split(r"(?m)^(?=# \d+부\. )", src_final.read_text(encoding="utf-8"))
                chunks = [c for c in chunks if c.strip()]
                for i, c in enumerate(chunks, 1):
                    (d / f"03_draft-v1-part{i}.md").write_text(c, encoding="utf-8")
                made = f"03_draft-v1-part1~{len(chunks)}.md"
            else:
                shutil.copy(src_final, d / "03_draft-v1.md")
                made = "03_draft-v1.md"
            lines.append(f"stage: write done {today} (inherited from {src_run}, {made} = {src_run}/{final_draft_name(p)})")
        # 작가 결정은 run을 넘어 이어진다: 서평 유지 같은 waiver와 그 승인, 블록 변경 승인을 순서대로 옮긴다
        src_led = (sd / "00_RUN_STATUS.md").read_text(encoding="utf-8")
        src_lines = src_led.split("\n")
        appr = waiver_approvals(src_led)
        for wi, ai in sorted(appr.items()):   # 승인된 서평 결정은 waiver와 승인 줄을 응답 원문 그대로 짝으로 옮긴다
            if re.match(r"^waiver:\s*fictional_reviewer\b", src_lines[wi]):
                lines.append(f"{src_lines[wi]} (inherited from {src_run})")
                approval = src_lines[ai]
                if not approval.startswith("gate: waiver-fictional_reviewer"):   # close-run으로 함께 승인된 경우
                    approval = f"gate: waiver-fictional_reviewer → approved {approval.split('→', 1)[1].strip()}"
                lines.append(f"{approval} (inherited from {src_run})")
        lines += [f"{ln} (inherited from {src_run})" for ln in src_lines if re.match(r"^gate:\s*block-change\s*→", ln)]
        # 출판 뒤 작가가 승인한 수정(윤문, 설정 변경)은 재합평이 승인 없이 되돌리지 못하게 함께 넘긴다
        protected = author_edited_paragraphs(root, src_run, p, protect)
        pac = sd / "14_post-audit-changelog.md"
        if protected or pac.exists():
            body = [f"# 물려받은 작가 승인 수정 ({src_run})", "",
                    "아래 '보호 문단'은 출판 뒤 작가가 승인해 고친 문단이다(출판 당시 최종본과 지금 최종본을 문단 단위로 비교해 뽑았다). "
                    "review 단계는 이 문단을 승인 없이 되돌리거나 고치지 않는다(stage-review.md \"작가 승인 문장\"). back_matter 섹션 전체도 같다.", "",
                    f"## 보호 문단 ({len(protected)}개)", ""]
            body += [f"- [{where}] {para}" for where, para in protected] or ["- (출판 당시 최종본 보관본이 없어 문단을 뽑지 못했다. 아래 변경 기록을 본다)"]
            if pac.exists():
                body += ["", "## 참고: 변경 기록 원문", "", pac.read_text(encoding="utf-8")]
            (d / "00_author-edits.inherited.md").write_text("\n".join(body) + "\n", encoding="utf-8")
            lines.append(f"note: author-edits 00_author-edits.inherited.md (보호 범위 {protect}, 보호 문단 {len(protected)}개, {src_run})")
        nxt = f"{stage} 단계 (/novel-writing)"
    (d / "00_RUN_STATUS.md").write_text(f"# 워크플로우 원장: {run}\n\n" + "\n".join(lines) + "\n", encoding="utf-8")
    led = d / "00_RUN_STATUS.md"
    led.write_text(led.read_text(encoding="utf-8") + lock_line(run, root) + "\n", encoding="utf-8")
    return run, nxt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", required=True, choices=["same", "updated", "rework"])
    ap.add_argument("--answer", required=True, help="새 run을 열기로 한 사용자 응답 원문")
    ap.add_argument("--from", dest="src")
    ap.add_argument("--stage", choices=["research", "write", "review"])
    ap.add_argument("--date", help="YYYYMMDD (기본 오늘)")
    ap.add_argument("--protect", choices=["recent", "all", "none"], default="recent",
                    help="rework에서 보호할 작가 수정 범위: recent(출판 뒤 수정 절차 이후), all(가장 이른 보관본 이후 전부), none")
    ap.add_argument("--root", default=str(ROOT))
    a = ap.parse_args()
    if a.date and not re.match(r"^\d{8}$", a.date):
        raise SystemExit("--date는 YYYYMMDD")
    run, nxt = open_run(a.root, a.mode, a.answer, a.src, a.stage, a.date, a.protect)
    print(f"OK run {run} 열림. 다음: {nxt}")


if __name__ == "__main__":
    main()
