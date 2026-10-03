"""publish 단계 0단계 품질 게이트 (범용).

사용:
  python3 <스킬>/scripts/validate_draft.py                    # 최신 02_draft/<run>/09_draft-final.md
  python3 <스킬>/scripts/validate_draft.py --run <run>          # 그 run의 블록 스냅샷으로 검사
  python3 <스킬>/scripts/validate_draft.py --draft X.md --toc Y.md --ebook Z.html
  어느 명령이든 --root <프로젝트 폴더>를 줄 수 있다 (기본: 현재 폴더에서 위로 book-toc.md를 찾는다)

모든 기준값은 book-toc.md의 작품 파라미터 블록에서 읽는다.
FAIL이 하나라도 있으면 exit 1. WARN은 보고만 한다. MANUAL은 사람이 확인할 항목이다.
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from booktoc import (require_run, ROOT, DEFAULT_TOC, load_params, heading, latest_run, split_draft, count_chars,  # noqa: E402
                     strip_quotes, outline, final_draft_name, run_params, back_headings, doc_order)

MANUAL = [
    "주술 호응 (BLACK 9원칙 9번). 정규식으로 판정할 수 없다. PROOF 리뷰로 확인",
    "위트 횟수와 출처 분포, zero_zones 위트 0회 (9원칙 4번). GOLD 카운트로 확인",
    "감정의 직접 노출 (9원칙 6번). GOLD 리뷰로 확인",
    "각 장 마지막 한 줄이 동작·사물로 닫힘 (9원칙 3번). 아래 '장 마지막 줄' 목록을 눈으로 확인",
]


def validate(draft_text, p, ebook_path=None):
    fails, warns, info = [], [], []
    chapters, extra = split_draft(draft_text, p)
    body = "\n".join(chapters[k] for k in sorted(chapters))
    narration = strip_quotes(body)

    # 1. 장 헤딩: 전부, 순서대로. 장 밖 헤딩은 back_matter 목록에 있을 때만, 마지막 장 뒤에
    missing = [heading(c) for c in p["chapters"] if c["no"] not in chapters]
    if missing:
        fails.append(f"장 헤딩 누락: {missing}")
    want = [h for _, h in outline(p)]
    got = [ln.strip() for ln in draft_text.split("\n") if ln.strip() in set(want)]
    if got != want and not missing:
        fails.append(f"부·장 헤딩 순서 어긋남: {got}")
    if extra:
        fails.append(f"허용되지 않은 장 밖 섹션: {extra} (블록 back_matter = {p.get('back_matter', [])})")
    h1 = [ln.strip() for ln in draft_text.split("\n") if ln.startswith("# ")]
    backs = [i for i, x in enumerate(h1) if x in back_headings(p)]
    chaps = [i for i, x in enumerate(h1) if x in {hh for _, hh in outline(p)}]
    missing_back = [h for h in back_headings(p) if h not in h1]
    if missing_back and chaps and len(chaps) == len(outline(p)):   # 전 장이 다 있는 원고(최종본)에서만 본다
        fails.append(f"블록 back_matter의 섹션 {missing_back}이 원고에 없다. 작가 산출물이므로 빼려면 "
                     f"블록과 run 스냅샷(01_test/<run>/book-toc.snapshot.md)의 back_matter에서 지우고 원장에 gate: remove-<섹션> → approved \"<원문>\"을 남긴다")
    if backs and chaps and min(backs) < max(chaps):
        fails.append("back_matter 섹션이 마지막 장보다 앞에 있다")
    all_lines = [ln.strip() for ln in draft_text.strip().split("\n") if ln.strip() and not ln.startswith("# ")]
    doc_last = all_lines[-1] if all_lines else ""

    # 2. 분량 (장 구간만, 줄바꿈 제외 공백 포함)
    L = p["length"]
    target = L["target_pages"] * L["chars_per_page"]
    lo, hi = round(target * (1 - L["tolerance"])), round(target * (1 + L["tolerance"]))
    total = count_chars(body)
    info.append(f"분량 {total:,}자 = {total / L['chars_per_page']:.1f}매 (허용 {lo:,}~{hi:,}자)")
    if not lo <= total <= hi:
        fails.append(f"분량 범위 밖: {total:,}자")
    for c in p["chapters"]:
        if c["no"] in chapters:
            n, plan = count_chars(chapters[c["no"]]), c["pages"] * L["chars_per_page"]
            dev = (n - plan) / plan
            if abs(dev) > 0.20:
                warns.append(f"{c['no']}장 분량 편차 {dev:+.0%} ({n:,}자 / 계획 {plan:,}자)")

    # 3. 마지막 줄
    lines = [ln.strip() for ln in body.strip().split("\n") if ln.strip()]
    last = lines[-1] if lines else ""
    if last != p["last_line"]:
        fails.append(f"마지막 줄 불일치: '{last[:40]}' (기대: '{p['last_line']}')")

    # 4. 시각 닻: 총량은 FAIL, 장 분포는 WARN
    for a in p["anchors"]:
        tot = sum(body.count(k) for k in a["keywords"])
        per = {n: sum(chapters.get(n, "").count(k) for k in a["keywords"]) for n in sorted(chapters)}
        info.append(f"닻 '{a['name']}' {tot}회 {per}")
        if tot < a["min_total"]:
            fails.append(f"시각 닻 부족: '{a['name']}' {tot}회 < {a['min_total']}")
        absent = [n for n in a["chapters"] if per.get(n, 0) == 0]
        if absent:
            warns.append(f"시각 닻 '{a['name']}'이 계획된 장 {absent}에 없다")

    # 5. 형식 금지
    if re.search(r"\*\*[^*\n]+\*\*", draft_text):
        fails.append("** 마크다운 강조 잔존")
    bullets = [ln for ln in body.split("\n") if re.match(r"^\s*([●•*]|-\s)", ln)]
    if bullets:
        fails.append(f"불릿 {len(bullets)}건: {bullets[0][:30]}")
    em = draft_text.count("—") + draft_text.count("–")
    if em:
        fails.append(f"em dash {em}건")

    # 6. 문장
    s = p["style"]
    found = [t for t in s["translationese"] if t in body]
    if found:
        fails.append(f"번역투: {found}")
    found = [t for t in s["cliches"] if t in body]
    if found:
        fails.append(f"클리셰: {found}")
    for n in sorted(chapters):
        sents = [x for x in re.split(r"(?<=[.?!])\s+", narration_of(chapters[n])) if x.strip()]
        if sents:
            avg = sum(len(x) for x in sents) / len(sents)
            if avg > s["avg_sentence_chars_max"] * 1.5:
                warns.append(f"{n}장 서술문 평균 {avg:.1f}자 (기준 {s['avg_sentence_chars_max']}자)")

    # 7. 사실·인물
    found = [t for t in p["forbidden_disclosures"] if t in body]
    if found:
        fails.append(f"명시 금지 항목 진술: {found}")
    found = [c for c in p["characters"] if c not in body]
    if found:
        fails.append(f"인물 누락: {found}")
    found = [c for c in p.get("retired_names", []) if c in draft_text]
    if found:
        fails.append(f"폐기된 이름 잔존: {found}")

    # 8. 시점: 1인칭 화자가 서술문에서 자기 이름을 주어로 쓰면 위반
    nar = p["narrator"]
    if nar["person"] == 1:
        hits = []
        for n in sorted(chapters):
            for m in re.finditer(re.escape(nar["name"]) + r"(이|은|가|는)\s", narration_of(chapters[n])):
                ctx = narration_of(chapters[n])[max(0, m.start() - 12): m.end() + 8].replace("\n", " ")
                hits.append(f"{n}장 '…{ctx}…'")
        if hits:
            fails.append(f"1인칭 시점 위반 {len(hits)}건 (화자 이름이 서술 주어): " + "; ".join(hits[:3]))

    # 9. 장 마지막 줄 (사람 확인용)
    for n in sorted(chapters):
        ls = [x.strip() for x in chapters[n].strip().split("\n") if x.strip()]
        info.append(f"{n}장 마지막 줄: {ls[-1] if ls else '(없음)'}")

    # 10. e북 사후 검증 (원고와 산출물이 갈라지지 않았는지)
    if ebook_path:
        ef, ew = check_ebook(ebook_path, p, doc_last, doc_order(draft_text, p))
        fails += ef
        warns += ew

    return fails, warns, info


def narration_of(text):
    return strip_quotes(text)


def check_ebook(path, p, last=None, order=None):
    """e북 사후 검증: 제목, 원고 헤딩·순서, 마지막 줄, em dash, 남은 슬롯, 출처 미확인 인용."""
    path = Path(path)
    if not path.exists():
        return [f"e북 없음: {path}"], []
    h = path.read_text(encoding="utf-8")
    fails, warns = [], []
    if f"<title>{html_escape(p['title'])}" not in h:
        fails.append("e북 <title>이 블록 title과 다르다")
    holes = sorted(set(re.findall(r"\{\{(\w+)\}\}", h)))
    if holes:
        fails.append(f"e북에 채우지 않은 슬롯: {holes[:5]}")
    m = re.search(r'<script type="text/markdown" id="manuscript">(.*?)</script>', h, re.S)
    if not m:
        return fails + ["e북에 원고 블록(script#manuscript)이 없다"], warns
    ms = m.group(1)
    heads = [ln.strip() for ln in ms.split("\n") if ln.startswith("# ")]
    want = order or [hh for _, hh in outline(p)]
    last = last or p["last_line"]
    if heads != want:
        fails.append(f"e북 원고 헤딩 불일치: {heads} (기대 {want})")
    lines = [ln.strip() for ln in ms.strip().split("\n") if ln.strip()]
    if not lines or lines[-1] != last:
        fails.append(f"e북 마지막 줄 불일치: '{(lines or [''])[-1][:40]}'")
    if "—" in ms or "–" in ms:
        fails.append("e북 원고에 em dash")
    eb = p.get("publish", {}).get("ebook", {})
    for i, line in enumerate(eb.get("cover_title_lines") or [p["title"]]):
        if len(line) > 8:
            warns.append(f"e북 표지 제목 {i + 1}째 줄 '{line}'이 {len(line)}자: 8자를 넘으면 표지 밖으로 나간다. cover_title_lines로 줄을 나눈다")
    epi = eb.get("epigraph")
    if epi and not epi.get("source_verified"):
        warns.append(f"e북 제사 인용의 출처가 확인되지 않았다: {' '.join(epi.get('attr_lines') or [epi.get('attr', '')])[:30]}")
    return fails, warns


def html_escape(s):
    import html
    return html.escape(s)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run")
    ap.add_argument("--draft", nargs="+", help="원고 파일. 장편 부 파일은 여러 개를 순서대로 준다")
    ap.add_argument("--toc", default=str(DEFAULT_TOC))
    ap.add_argument("--root", help="프로젝트 폴더 (기본: book-toc.md를 위로 찾아감)")
    ap.add_argument("--ebook")
    a = ap.parse_args()
    run = a.run if a.draft else (a.run or latest_run())  # --run과 --draft를 함께 주면 그 run의 스냅샷으로 검사한다
    if run and not a.draft:
        require_run(run)
    p = run_params(run) if run and a.toc == str(DEFAULT_TOC) else load_params(a.toc)
    if a.draft:
        drafts = [Path(x) for x in a.draft]
    else:
        drafts = [ROOT / "02_draft" / run / final_draft_name(p)]
        if not a.ebook and (ROOT / "03_output" / run / "ebook.html").exists():
            a.ebook = str(ROOT / "03_output" / run / "ebook.html")
    text = "\n\n".join(d.read_text(encoding="utf-8") for d in drafts)
    fails, warns, info = validate(text, p, a.ebook)

    print("=" * 60)
    def shown(d):   # 보고서에 개인 경로가 남지 않게 프로젝트 폴더 기준으로 적는다
        try:
            return str(Path(d).resolve().relative_to(Path(ROOT).resolve()))
        except ValueError:
            return Path(d).name
    print(f"품질 게이트: {p['title']}  |  {', '.join(shown(d) for d in drafts)}")
    print("=" * 60)
    for x in info:
        print("  ·", x)
    for x in warns:
        print("  WARN", x)
    print("  MANUAL (사람 확인):")
    for x in MANUAL:
        print("    -", x)
    if fails:
        print(f"\nFAIL {len(fails)}건")
        for x in fails:
            print("  ✗", x)
        sys.exit(1)
    print("\nPASS. 자동 검사 전 항목 통과.")


if __name__ == "__main__":
    main()
