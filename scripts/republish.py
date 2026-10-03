"""출판 뒤 수정(post-audit) 마무리: 승인을 확인하고, 지금 산출물을 보관한 뒤 다시 만들고, 메타 분량을 맞추고, 검증하고, 다시 잠근다.

사용:
  python3 <스킬>/scripts/republish.py --run <run> --prepare          # 고치기 전: 최종본 보관, 변경 기록 준비, owner 발급
  python3 <스킬>/scripts/republish.py --run <run> --owner <owner>    # 고친 뒤: 다시 만들기, 메타 분량, 검증, 재잠금

한 run의 출판 뒤 수정은 한 번에 하나다. --prepare가 owner를 발급하고, 그 owner를 가진 쪽만 마칠 수 있다.
다른 수정이 진행 중이면 --prepare가 멈춘다(다른 세션이 같은 run을 고치는 중이라는 뜻이다).

순서 (SKILL.md "출판 뒤 수정"):
  1. 작가에게 묻고 지휘가 원장에 gate: post-audit → approved "<원문>"을 남긴다 (빼는 것이 있으면 같은 원문으로 gate: remove-<대상>도).
  2. --prepare: 09 최종본(장편은 통합본)을 _archive/<시각>_post-audit_<owner>/02_draft/<run>/에 (블록·스냅샷과 함께) 복사하고 MANIFEST.tsv에 적는다.
     02_draft/<run>/14_post-audit-changelog.md가 없으면 만들고, 원장에 note: post-audit-prepare 줄(보관 위치, 변경 기록 해시)을 남긴다.
  3. 원고·블록·스냅샷을 고치고 14_post-audit-changelog.md에 무엇을 왜 바꿨는지 적는다. 블록을 바꿨으면 gate: block-change → approved <키>.
  4. --owner <owner>로 다시 돌린다.

멈추는 경우(아무것도 바꾸지 않는다): 마지막 잠금 뒤 post-audit 승인이 없다, 승인 없는 변경(lock 위반)이 있다,
--prepare를 하지 않았다, 변경 기록 파일이 prepare 뒤 그대로다.
"""
import argparse
import datetime
import hashlib
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from booktoc import (ROOT, count_chars, final_draft_name, ledger, lock_line,  # noqa: E402
                     lock_violations, open_post_audit, run_params, split_draft, parse_lock, draft_sha, output_sha, out_unchanged,
                     FORMATS, ALL_FORMATS)

HERE = Path(__file__).parent


def sync_metadata(meta, text, p):
    """metadata.md의 분량 줄과 장 구성 표를 검증기 기준 글자 수로 맞춘다. 바꾼 줄 수를 돌려준다."""
    ch, _ = split_draft(text, p)
    cpp = p["length"]["chars_per_page"]
    counts = {no: count_chars(body) for no, body in ch.items()}
    total = sum(counts.values())
    t, n0 = meta.read_text(encoding="utf-8"), 0
    t, n = re.subn(r"분량:\s*[\d,]+자(\s*\([\d.]+매)?", lambda m: f"분량: {total:,}자" + (f" ({total / cpp:.1f}매" if m.group(1) else ""), t)
    n0 += n
    for no, c in counts.items():
        t, n = re.subn(rf"^(\|\s*{no}장\s*\|[^|\n]*\|\s*)[\d.]+매 \([\d,]+자\)(\s*\|)$", rf"\g<1>{c / cpp:.1f}매 ({c:,}자)\g<2>", t, flags=re.M)
        n0 += n
    t, n = re.subn(r"^(\|\s*합계\s*\|[^|\n]*\|\s*)[\d.]+매(\s*\|)$", rf"\g<1>{total / cpp:.1f}매\g<2>", t, flags=re.M)
    meta.write_text(t, encoding="utf-8")
    return n0 + n, total


def locked_copy(root, run, want):
    """_archive에서 해시가 잠금의 draft 해시와 같은 09 사본을 찾는다(되돌릴 원본 안내용)."""
    import hashlib
    for p in sorted((Path(root) / "_archive").glob(f"*/02_draft/{run}/09_draft-final*.md"), reverse=True):
        h = hashlib.sha256()
        h.update(p.name.encode() + b"\0" + p.read_bytes())
        if h.hexdigest()[:16] == want:
            return str(p.relative_to(root))
    return None


def file_sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16] if p.exists() else "none"


def archive(root, src, arc_root, reason, today):
    dst = arc_root / src.relative_to(root)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    man = root / "_archive" / "MANIFEST.tsv"
    if not man.exists():
        man.write_text("date\tsrc\tdst\treason\n", encoding="utf-8")
    with man.open("a", encoding="utf-8") as f:
        f.write(f"{today}\t{src.relative_to(root)}\t{dst.relative_to(root)}\t{reason}\n")


def append(led, text):
    led.write_text(led.read_text(encoding="utf-8").rstrip("\n") + "\n" + text + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--prepare", action="store_true", help="고치기 전: 최종본 보관과 변경 기록 파일 준비")
    ap.add_argument("--owner", help="--prepare가 발급한 이 수정의 owner (마칠 때)")
    ap.add_argument("--status", action="store_true", help="진행 중인 출판 뒤 수정이 있는지만 알려 준다(묻기 전에 쓴다)")
    ap.add_argument("--takeover", action="store_true", help="끊긴 세션의 수정을 이어받는다(작가 승인 gate: post-audit-takeover 필요)")
    ap.add_argument("--abandon", action="store_true", help="끊긴 세션의 수정을 버리고 원고를 수정 전 보관본으로 되돌린다(작가 승인 gate: post-audit-abandon 필요)")
    a = ap.parse_args()
    root, run = Path(a.root), a.run
    led = root / "02_draft" / run / "00_RUN_STATUS.md"
    if not led.exists():
        runs = sorted(p.name for p in (root / "02_draft").glob("*_*") if (p / "00_RUN_STATUS.md").exists())
        raise SystemExit(f"멈춤: run '{run}'이 없다({led.relative_to(root)} 없음). 있는 run: {', '.join(runs) or '없음'}")
    lines = ledger(run, root).split("\n")
    if not re.search(r"^stage:\s*publish done", "\n".join(lines), re.M):
        raise SystemExit("멈춤: 이 run은 아직 출판하지 않았다(stage: publish done 없음). 출판 전 수정은 해당 단계에서 한다")
    if a.status:
        st = open_post_audit(run, root)
        if not st:
            print("진행 중인 출판 뒤 수정 없음")
            return
        k = st[0]
        req = next((ln for ln in reversed(lines[:k]) if re.match(r"^gate:\s*post-audit\s*→\s*approved\b", ln)), "(승인 줄 없음)")
        stamp_m = re.search(r"_archive/(\d{8})_(\d{6})", lines[k])
        started = f"{stamp_m.group(1)[:4]}-{stamp_m.group(1)[4:6]}-{stamp_m.group(1)[6:]} {stamp_m.group(2)[:2]}:{stamp_m.group(2)[2:4]}" if stamp_m else "알 수 없음"
        lk = parse_lock(lines[max(i for i, ln in enumerate(lines[:k]) if ln.startswith("lock:"))]) if any(ln.startswith("lock:") for ln in lines[:k]) else None
        d_changed = "알 수 없음" if not lk or lk.get("draft") in (None, "none") else ("예" if draft_sha(run, root) != lk["draft"] else "아니오")
        same = out_unchanged(lk, run, root)
        o_changed = "알 수 없음" if same is None else ("아니오" if same else "예")
        print(f"진행 중인 출판 뒤 수정: 원장 {k + 1}줄, owner {st[1] or '기록 없음'}, 시작 {started}\n"
              f"  요청: {req}\n  원고가 잠금 뒤 바뀌었나: {d_changed}\n  e북이 잠금 뒤 바뀌었나: {o_changed}\n"
              f"  작가에게 (a) 기다림 (b) 이어받기 (c) 버리기를 이 정보와 함께 묻는다(SKILL.md \"출판 뒤 수정\" 0단계)")
        return
    locks = [i for i, ln in enumerate(lines) if ln.startswith("lock:")]
    if not locks:
        raise SystemExit(f"멈춤: 잠금 줄이 없다. 먼저 python3 {HERE / 'lock_run.py'} --run {run} 으로 지금 출판본을 잠근다")
    last_lock = locks[-1]
    since = lines[last_lock + 1:]
    if a.takeover or a.abandon:
        st = open_post_audit(run, root)
        if not st:
            raise SystemExit("멈춤: 진행 중인 출판 뒤 수정이 없다")
        gid = "post-audit-takeover" if a.takeover else "post-audit-abandon"
        marks = [i for i, ln in enumerate(lines) if i >= st[0] and re.match(r"^note:\s*post-audit-(prepare|takeover)\b", ln)]
        if not any(re.match(rf"^gate:\s*{gid}\s*→\s*approved\b", ln) for ln in lines[marks[-1] + 1:]):   # 승인 하나는 한 번만 쓴다
            raise SystemExit(f"멈춤: 원장 {st[0] + 1}줄 수정 뒤에 gate: {gid} → approved 줄이 없다. 작가에게 (a) 기다림 (b) 이어받기 (c) 버리기를 묻고 응답 원문을 남긴다")
        if a.takeover:
            import secrets
            new = secrets.token_hex(3)
            append(led, f"note: post-audit-takeover from={st[1] or '-'} owner={new}")
            print(f"OK 원장 {st[0] + 1}줄의 수정을 이어받았다. 새 owner: {new}. 원고 수정과 변경 기록을 마친 뒤 --owner {new}로 마친다")
            return
        arcdir = re.match(r"^note:\s*post-audit-prepare\s+(\S+)", lines[st[0]])
        p0 = run_params(run, root)
        restored = []
        if arcdir:
            gone = root / "_archive" / f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')}_abandoned_{st[1] or 'x'}"
            for cur_f in sorted((root / "02_draft" / run).glob("09_draft-final*.md")):   # 버리는 수정본도 지우지 않고 보관한다
                archive(root, cur_f, gone, "abandoned post-audit edit (replaced by pre-edit copy)", datetime.date.today().isoformat())
            for src in sorted((root / arcdir.group(1) / "02_draft" / run).glob("09_draft-final*.md")):
                shutil.copy2(src, root / "02_draft" / run / src.name)
                restored.append(src.name)
        if not restored:
            raise SystemExit("멈춤: 수정 전 보관본을 찾지 못해 되돌릴 수 없다. 원고를 손으로 되돌린 뒤 다시 실행한다")
        if arcdir:   # 이 수정 중에 바뀐 블록·스냅샷도 수정 전으로
            for rel in (f"01_test/{run}/book-toc.snapshot.md",):   # run은 스냅샷으로 검사한다. 루트 book-toc.md(다음 작품용일 수 있다)는 건드리지 않는다
                src = root / arcdir.group(1) / rel
                if src.exists():
                    shutil.copy2(src, root / rel)
                    restored.append(rel)
        # 끊긴 세션이 산출물까지 다시 만들었을 수 있다. 잠금의 out 해시와 다르면 이 수정의 보관본에서 산출물도 되돌린다
        lk = parse_lock(lines[last_lock])
        out_dir = root / "03_output" / run
        out_note = "산출물은 잠금 당시 그대로였다"
        if out_unchanged(lk, run, root) is False:
            copies = [root / arcdir.group(1) / "03_output" / run] if arcdir and (root / arcdir.group(1) / "03_output" / run).exists() else []
            copies += sorted(root.glob(f"_archive/*_post-audit_{st[1]}/03_output/{run}")) if st[1] else []
            if copies:
                for src in copies[0].iterdir():
                    shutil.copy2(src, out_dir / src.name)
                restored += [f"03_output/{run}/{s.name}" for s in copies[0].iterdir()]
                out_note = "산출물도 이 수정 전 판으로 되돌렸다"
            if out_unchanged(lk, run, root) is False:
                # 보관본이 없으면 되돌린 원고로 다시 만든다(같은 원고·블록·디자인이면 e북은 같은 결과)
                p1 = run_params(run, root)
                fm = p1["publish"].get("formats", ["ebook"])
                py = [sys.executable]
                if "ebook" in fm:
                    subprocess.run(py + [str(HERE / "generate_ebook.py"), "--run", run, "--root", str(root)], cwd=root, capture_output=True)
                if (out_dir / "metadata.md").exists():
                    sync_metadata(out_dir / "metadata.md", (root / "02_draft" / run / final_draft_name(p1)).read_text(encoding="utf-8"), p1)
                restored.append("산출물 다시 만듦")
                out_note = "이 수정 중에 산출물이 바뀌었는데 보관본이 없어, 되돌린 원고로 다시 만들었다"
        bad = lock_violations(run, root)
        if any("최종 원고" in b for b in bad):
            raise SystemExit("멈춤: 되돌린 원고가 잠금 당시 원고와 다르다:\n  " + "\n  ".join(bad))
        append(led, f"stage: post-audit-fix abandoned {datetime.date.today().isoformat()} (owner {st[1] or '-'}, 되돌림: {', '.join(restored)} ← {arcdir.group(1)})\n"
                    + lock_line(run, root))   # 다시 잠가 구간을 닫는다. 다음 수정은 새 승인부터
        print(f"OK 수정을 버리고 {', '.join(restored)}를 수정 전으로 되돌렸다. {out_note}")
        return
    if not any(re.match(r"^gate:\s*post-audit\s*→\s*approved\b", ln) for ln in since):
        raise SystemExit("멈춤: 마지막 잠금 뒤에 gate: post-audit → approved 줄이 없다. 작가에게 묻고 지휘가 응답 원문을 남긴 뒤 다시 실행한다")
    keep = [i for i, ln in enumerate(since) if re.match(r"^gate:\s*regenerate-outputs\s*→\s*keep\b", ln)]
    if keep and not any(re.match(r"^gate:\s*post-audit\s*→\s*approved\b", ln) for ln in since[keep[-1] + 1:]):
        raise SystemExit("멈춤: 작가가 지금 산출물을 유지하기로 했다(gate: regenerate-outputs → keep). 다시 만들려면 그 뒤에 새 post-audit 승인을 받는다")
    if a.prepare and not open_post_audit(run, root):   # 승인 전에 이미 고친 원고는 '수정 전 보관본'이 될 수 없다. 되돌릴 사본 위치를 먼저 알려 준다
        lk = parse_lock(lines[last_lock])
        if lk and lk.get("draft") not in (None, "none") and draft_sha(run, root) != lk["draft"]:
            hint = locked_copy(root, run, lk["draft"])
            raise SystemExit("멈춤: 최종 원고가 원장 " f"{last_lock + 1}줄 잠금 뒤에 이미 바뀌었다(승인 전 수정). 수정 전 원고를 보관할 수 없으니 "
                             "먼저 잠금 당시 원고로 되돌린다" + (f": {hint}" if hint else ". 잠금 당시 원고 사본은 _archive에서 찾지 못했다"))
    bad = lock_violations(run, root)
    if bad:
        raise SystemExit("멈춤: 승인 없는 변경이 있다:\n  " + "\n  ".join(bad))
    today = datetime.date.today().isoformat()
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    cur = open_post_audit(run, root)
    changelog = root / "02_draft" / run / "14_post-audit-changelog.md"

    if a.prepare:
        if cur:
            raise SystemExit(f"멈춤: 원장 {cur[0] + 1}줄에서 시작한 출판 뒤 수정이 아직 끝나지 않았다. 다른 세션이 고치는 중이면 기다린다. "
                             f"그 세션이 끊겼으면 작가에게 (a) 기다림 (b) 이어받기 --takeover (c) 버리기 --abandon 을 묻는다(SKILL.md \"출판 뒤 수정\" 0단계)")
        import secrets
        owner = secrets.token_hex(3)
        p0 = run_params(run, root)
        arc_root = root / "_archive" / f"{stamp}_post-audit_{owner}"
        drafts = sorted((root / "02_draft" / run).glob("09_draft-final*.md")) or [root / "02_draft" / run / final_draft_name(p0)]
        outs = [root / "03_output" / run / n_ for n_ in ("final.docx", "ebook.html", "metadata.md")]
        for src in drafts + [root / "book-toc.md", root / "01_test" / run / "book-toc.snapshot.md"] + outs:
            if src.exists():
                archive(root, src, arc_root, "copy before post-audit edit (file kept in place)", today)
        if not changelog.exists():
            changelog.write_text(f"# 출판 뒤 수정 기록: {run}\n\n항목마다 날짜, 승인 원문, 바꾼 자리(장·문단), 바꾸기 전과 뒤를 적는다.\n", encoding="utf-8")
        append(led, f"note: post-audit-prepare {arc_root.relative_to(root)} changelog={file_sha(changelog)} owner={owner}")
        print(f"OK 최종본을 {arc_root.relative_to(root)}에 보관했다. 이 수정의 owner: {owner}\n"
              f"이제 원고를 고치고 {changelog.relative_to(root)}에 적은 뒤: python3 {HERE / 'republish.py'} --run {run} --owner {owner}")
        return

    if not cur:
        raise SystemExit(f"멈춤: 고치기 전 보관을 하지 않았다. 먼저 python3 {HERE / 'republish.py'} --run {run} --prepare")
    if cur[1] and a.owner != cur[1]:
        raise SystemExit(f"멈춤: 원장 {cur[0] + 1}줄의 수정은 owner {cur[1]}가 시작했다. 그 수정을 시작한 쪽이 --owner {cur[1]}로 마친다"
                         + ("" if a.owner else " (--owner가 빠졌다)"))
    m = re.search(r"changelog=(\S+)", lines[cur[0]])
    if m and file_sha(changelog) == m.group(1):
        raise SystemExit(f"멈춤: {changelog.relative_to(root)}에 이번 수정을 적지 않았다(--prepare 뒤 그대로다)")

    p = run_params(run, root)
    fmts = p["publish"].get("formats", ["ebook"])
    if stale := [f_ for f_ in fmts if f_ not in FORMATS]:
        raise SystemExit(f"멈춤: 블록 publish.formats에 더는 만들지 않는 형식 {stale}이 있다. 이번 수정에서 블록을 [\"ebook\"]로 바꾸고 "
                         f"gate: block-change → approved publish.formats 와 gate: remove-{stale[0]} → approved 를 남긴다. 그 산출물은 보관함으로 옮겨진다")
    out = root / "03_output" / run
    draft = root / "02_draft" / run / final_draft_name(p)
    # 산출물을 건드리기 전에 원고부터 검증한다. 실패하면 아무것도 바꾸지 않는다
    from validate_draft import validate
    pre = validate(draft.read_text(encoding="utf-8"), p)[0]
    if pre:
        raise SystemExit("멈춤: 고친 원고가 검증을 통과하지 못했다(산출물은 그대로다):\n  " + "\n  ".join(pre))
    arc = root / "_archive" / f"{stamp}_post-audit{'_' + cur[1] if cur[1] else ''}"
    kept = []
    for name in ("final.docx", "ebook.html", "metadata.md", "validate_report.txt"):
        if (out / name).exists():
            archive(root, out / name, arc, "copy before post-audit republish (file kept in place)", today)
            kept.append(name)

    # 블록에서 뺀 형식의 산출물(예: 예전 작품의 docx)은 승인(gate: remove-<형식>)을 확인하고 보관함으로 옮긴다
    lk_prev = parse_lock(lines[last_lock])
    for fmt in [f_ for f_ in (lk_prev or {}).get("formats", []) if f_ not in fmts]:
        fname = ALL_FORMATS.get(fmt)
        if fname and (out / fname).exists():
            if not any(re.match(rf"^gate:\s*remove-({re.escape(fmt)}|{re.escape(fname)})\s*→\s*approved\b", ln) for ln in since):
                raise SystemExit(f"멈춤: 블록에서 '{fmt}'을 뺐는데 gate: remove-{fmt} → approved 줄이 없다. 작가에게 묻고 남긴다")
            archive(root, out / fname, arc, f"removed format {fmt} (gate: remove-{fmt})", today)
            (out / fname).unlink()
            print(f"OK 뺀 형식의 산출물 {fname}을 {arc.relative_to(root)}로 옮겼다")

    def restore(why):
        for name in kept:
            shutil.copy2(arc / "03_output" / run / name, out / name)
        raise SystemExit(f"멈춤: {why}. 산출물을 다시 만들기 전 판으로 되돌렸다({arc.relative_to(root)}). 잠그지 않았다")

    py = [sys.executable]
    if "ebook" in fmts:
        if subprocess.run(py + [str(HERE / "generate_ebook.py"), "--run", run, "--root", str(root)], cwd=root).returncode:
            restore("e북 생성 실패")
    if (out / "metadata.md").exists():
        n, total = sync_metadata(out / "metadata.md", draft.read_text(encoding="utf-8"), p)
        got = re.search(r"분량:\s*([\d,]+)자", (out / "metadata.md").read_text(encoding="utf-8"))
        if not got or int(got.group(1).replace(",", "")) != total:
            restore(f"metadata.md에서 '분량: N자' 줄을 찾지 못해 {total:,}자로 맞추지 못했다. stage-publish.md 2단계 형식으로 분량 줄을 넣는다")
        print(f"OK metadata 분량 {total:,}자로 맞춤 ({n}줄)")
    rep = subprocess.run(py + [str(HERE / "validate_draft.py"), "--run", run, "--root", str(root)], capture_output=True, text=True, cwd=root)
    (out / "validate_report.txt").write_text(rep.stdout, encoding="utf-8")
    if rep.returncode != 0:
        report = rep.stdout
        restore(f"새 산출물 검증 FAIL (보고서는 {arc.relative_to(root)}와 아래)\n{report[-1500:]}")

    for src in sorted((root / "02_draft" / run).glob("09_draft-final*.md")):   # 잠글 원고도 보관해 둔다(다음 --prepare의 되돌림 안내가 찾는다)
        archive(root, src, arc, "locked manuscript at post-audit republish (file kept in place)", today)
    append(led, f"stage: post-audit-fix done {today} (republish.py, owner {cur[1] or '-'}, 보관: {arc.relative_to(root)}, 기록: {changelog.relative_to(root)})\n"
                + lock_line(run, root))
    print(f"OK {run} 다시 출판하고 잠갔다. 다음: python3 {HERE / 'lint_project.py'} --root {root}")


if __name__ == "__main__":
    main()
