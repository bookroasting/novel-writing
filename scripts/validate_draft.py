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
    "주술 호응 (BLACK 9원칙 9번). 정규식으로 판정할 수 없다. OLIVE 리뷰로 확인",
    "위트 횟수와 출처 분포, zero_zones 위트 0회 (9원칙 4번). GOLD 카운트로 확인",
    "감정의 직접 노출 (9원칙 6번). GOLD 리뷰로 확인",
    "각 장 마지막 한 줄이 동작·사물로 닫힘 (9원칙 3번). 아래 '장 마지막 줄' 목록을 눈으로 확인",
    "처음 읽는 독자가 멈추는 자리: 문장 사이 연결, 압축 위트·비유, 높임, 서술 호칭, 성별 단서, 인용 메모의 뜻 (references/reader-check.md). review 단계 reader-check 파일로 확인",
]

SHORT_SENT_CHARS, SHORT_SENT_SHARE = 12, 0.2   # 단문 나열 WARN: 12자 이하 서술문이 한 장의 20% 이상
RHYTHM_PARA_CV, RHYTHM_SENT_CV = 0.4, 0.35   # 리듬 단조 WARN: 서술 단락·서술문 길이의 변동계수가 이 값보다 작으면 길이가 고르게 같다

# 한글로 쓴 수 (reader-check R4: 수량·단위는 아라비아 숫자, 시각·서수는 한글). 오탐이 있을 수 있어 WARN만 낸다.
# 잡는 것: 큰 수(이백, 백십 장, 이백 열둘, 삼만 원, 백 명)와 측정 단위가 붙은 한자어 수(삼 센티, 십일 센티, 삼십 퍼센트).
# 잡지 않는 것: 시각(세 시 이십 분), 서수, 고유어 수(두 시간, 세 장), 어림수(수백, 이삼 일), 낱말 속 글자(천천히, 사건, 영원).
SINO = "일이삼사오육칠팔구"
_G = rf"(?:[{SINO}]?천)?(?:[{SINO}]?백)?(?:[{SINO}]?십)?[{SINO}]?"
SINO_NUM = re.compile(rf"^(?:{_G}만)?{_G}$")
NUM_RUN = re.compile(rf"(?<![가-힣0-9])([영{SINO}십백천만]+)(\s?)([가-힣]*)")
MEASURE = ("센티미터", "센티", "밀리미터", "밀리", "킬로미터", "킬로그램", "킬로", "미터", "그램", "리터", "퍼센트")
COUNTERS = ("장", "개", "건", "명", "권", "대", "쪽", "통", "곳", "채", "가구", "세대", "원", "평") + MEASURE
NATIVE_TAIL = re.compile(r"^(?:열|스물|서른|마흔|쉰|예순|일흔|여든|아흔)")
PARTICLE = re.compile(r"^(?:짜리|째|쯤|씩|여)?(?:이|가|은|는|을|를|의|에|에서|에게|도|과|와|만|으로|로|이다|이었다|였다|이나|나|까지|부터)?$")
NOT_NUM = {"백일", "천일", "일백", "일천", "일만", "이만", "오만"}   # 백일잔치, 천일야화, 이만 가자, 오만한


def korean_numerals(text):
    """한글로 쓴 수를 찾는다. [(수와 단위, 앞뒤 문맥)]."""
    hits = []
    for m in NUM_RUN.finditer(text):
        num, sp, rest = m.groups()
        if num in NOT_NUM or not (SINO_NUM.match(num) or num == "영") or (num == "천만" and rest.startswith("에")):
            continue
        unit = next((u for u in COUNTERS if rest.startswith(u)), "")
        if unit and not PARTICLE.match(rest[len(unit):]):
            unit = ""
        if not sp and not unit and not PARTICLE.match(rest) and not NATIVE_TAIL.match(rest):
            continue   # 낱말의 일부다 (삼천리, 오만한)
        big = len(num) >= 2 and any(c in num for c in "백천만")
        single_big = num in ("백", "천", "만") and sp and unit           # 백 명, 천 원 (백 번, 천 년은 잡지 않는다)
        small = (unit in MEASURE or (unit == "원" and "십" in num)) and not (sp and num in ("이", "일"))   # '이 미터'는 지시어일 수 있다
        if big or single_big or small:
            ctx = text[max(0, m.start() - 8): m.end() + 4].replace("\n", " ").strip()
            hits.append((num + (sp + unit if unit else ""), ctx))
    return hits


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

    # 6-1. 단문 나열 (reader-check R1): 한 동작짜리 짧은 문장이 한 장 서술의 큰 몫이면 리듬이 아니라 목록으로 읽힌다.
    # 블록 값과 무관한 독자 기준이다(블록 기본값이 15자였을 때 독자가 "읽을 수가 없다"고 한 원고가 이 몫을 넘었다).
    for n in sorted(chapters):
        sents = [x.strip() for x in re.split(r"(?<=[.?!])\s+", narration_of(chapters[n])) if x.strip()]
        if len(sents) >= 20:
            share = sum(1 for x in sents if len(x) <= SHORT_SENT_CHARS) / len(sents)
            if share >= SHORT_SENT_SHARE:
                warns.append(f"{n}장 단문 나열 의심: 서술문 {len(sents)}개 중 {share:.0%}가 {SHORT_SENT_CHARS}자 이하. "
                             f"연속 동작은 이어 쓰고 문장 사이를 잇는다 (reader-check R1·R2)")

    # 6-1b. 리듬 단조 (문체 2원칙): 서술 단락과 서술문의 길이가 고르면 AI 문체처럼 단조롭게 읽힌다.
    def _cv(xs):
        m = sum(xs) / len(xs)
        return (sum((x - m) ** 2 for x in xs) / len(xs)) ** 0.5 / m if m else 0
    for n in sorted(chapters):
        paras = [len(q.strip()) for q in re.split(r"\n\s*\n", chapters[n])
                 if q.strip() and not q.strip().startswith(("#", '"', "\u201c"))]
        sents = [len(x.strip()) for x in re.split(r"(?<=[.?!])\s+", narration_of(chapters[n])) if x.strip()]
        why = []
        if len(paras) >= 8 and _cv(paras) < RHYTHM_PARA_CV:
            why.append(f"서술 단락 길이 변동계수 {_cv(paras):.2f}")
        if len(sents) >= 20 and _cv(sents) < RHYTHM_SENT_CV:
            why.append(f"서술문 길이 변동계수 {_cv(sents):.2f}")
        if why:
            warns.append(f"{n}장 리듬 단조: {', '.join(why)}. 한 줄 단락과 긴 단락, 짧은 문장과 긴 문장을 섞는다 (문체 2원칙)")

    # 6-2. 한글로 쓴 수 (reader-check R4). 대사 포함
    for n in sorted(chapters):
        hits = korean_numerals(chapters[n])
        if hits:
            warns.append(f"{n}장 한글 수 표기 {len(hits)}건 (수량·단위는 아라비아 숫자, 시각·서수는 한글): "
                         + "; ".join(f"'{h}' …{c}…" for h, c in hits[:3]))

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
