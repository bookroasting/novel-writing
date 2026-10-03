"""첫 작품 시작: 사용자 답 한 묶음으로 book-toc.md와 00_storyline/storyline.md를 함께 만든다.

사용: python3 <스킬>/scripts/init_project.py --answers answers.json [--root <프로젝트 폴더>]

answers.json (지휘가 사용자에게 한 번에 물어 받은 답):
{
  "title": "제목", "pen_name": "필명", "genre": "SF", "genre_label": "단편 소설",
  "target_reader": "대상 독자 한두 문장",
  "narrator": {"name": "화자 이름", "person": 1},
  "characters": ["본문에 반드시 나올 이름·호칭"],
  "chapters": [{"title": "장 제목", "pages": 14}, ...],
  "last_line": "작품 마지막 줄",
  "base_year": 2026, "chars_per_page": 200,
  "influences": "흡수한 작가 2~3명 (선택)",
  "cast": ["윤서 (34, 요리사): 화자. 손버릇: 칼을 닦는다", ...] (선택),
  "hidden_facts": ["본문에 풀지 않을 사실", ...] (선택),
  "back_matter": ["작가의 말"] (선택. 마지막 장 뒤에 둘 섹션. 나중에 넣으면 review 7~9단계를 다시 해야 한다)
}

이미 book-toc.md나 storyline.md가 있으면 덮어쓰지 않고 멈춘다(작가 산출물 보호).
시각 닻, 명시 금지 항목, 위트 0회 구역은 빈 목록으로 둔다. storyline 단계가 통과본에서 블록으로 옮긴다.
publish.* 빈칸(발행 연월, 소개문)은 publish 단계에서 묻는다(그 전까지 린터 WARN).
"""
import argparse
import json
import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
TEMPLATES = SKILL_DIR / "templates"
REQUIRED = ("title", "pen_name", "genre", "genre_label", "target_reader", "narrator", "characters", "chapters", "last_line")


def build_block(a):
    tpl = (TEMPLATES / "book-toc.template.md").read_text(encoding="utf-8")
    p = json.loads(re.search(r"```json\s*\n(.*?)\n```", tpl, re.S).group(1))
    p.update({k: a[k] for k in ("title", "pen_name", "genre", "genre_label", "target_reader", "last_line")})
    p["base_year"] = int(a.get("base_year", p["base_year"]))
    p["narrator"] = {"name": a["narrator"]["name"], "person": int(a["narrator"].get("person", 1))}
    p["chapters"] = [{"no": i, "title": c["title"], "pages": int(c["pages"])} for i, c in enumerate(a["chapters"], 1)]
    p["length"]["target_pages"] = sum(c["pages"] for c in p["chapters"])
    p["length"]["chars_per_page"] = int(a.get("chars_per_page", p["length"]["chars_per_page"]))
    p["characters"] = list(a["characters"])
    p["anchors"], p["forbidden_disclosures"] = [], []
    p["wit"]["zero_zones"] = []
    p["publish"]["cover_label"] = a["genre_label"]
    p["back_matter"] = list(a.get("back_matter") or [])
    p["publish"]["copyright_year"] = int(a.get("copyright_year") or __import__("datetime").date.today().year)   # 발행 연도(작품 속 기준 연도와 다르다)
    body = "```json\n" + json.dumps(p, ensure_ascii=False, indent=2) + "\n```"
    out = re.sub(r"```json\s*\n.*?\n```", lambda _: body, tpl, count=1, flags=re.S)
    out = re.sub(r"^사용법: .*$", "init_project.py가 만든 파일이다. 숫자·이름의 정본은 아래 블록이다. 고친 뒤 `python3 <스킬>/scripts/lint_project.py`로 확인한다. "
                 "출판 정보 빈칸(`<…>`)은 publish 단계에서 묻는다.", out, count=1, flags=re.M)
    # 서술 섹션: 선택 답이 없으면 빈칸 대신 "storyline 단계에서 정한다"를 남긴다(린터가 막지 않게, 그러나 비었다는 사실은 보이게)
    inf = a.get("influences") or "흡수한 작가는 storyline 합평에서 정한다"
    out = re.sub(r"<흡수한 작가[^>]*>", lambda _: inf, out, count=1)
    cast = a.get("cast") or [f"{n}: storyline 통과본을 따른다" for n in a["characters"]]
    out = out.replace("- <이름> (<나이, 직업>): <작품 속 역할>. 손버릇: <동작·사물>", "\n".join(f"- {c}" for c in cast), 1)
    hid = a.get("hidden_facts") or ["없음 (storyline 단계에서 정하면 고친다)"]
    out = out.replace("- <본문에 풀지 않을 사실>", "\n".join(f"- {h}" for h in hid), 1)
    return out


def build_storyline(a):
    t = (TEMPLATES / "storyline.template.md").read_text(encoding="utf-8")
    t = t.replace("<제목>", a["title"]).replace("<장르>", a["genre"])
    nar = a["narrator"]
    t = t.replace("<인칭, 시제, 화자가 모르는 정보>", f"{int(nar.get('person', 1))}인칭, 화자 {nar['name']}. <시제, 화자가 모르는 정보>")
    cast = "\n\n".join(f"### {n} (<나이, 직업, 작품 속 역할>)\n- 동기:\n- 손버릇·사물:\n- 변화 곡선:" for n in dict.fromkeys([nar["name"]] + [re.split(r"[ (:]", c, 1)[0] for c in a.get("cast") or []]))
    t = re.sub(r"### <이름> \(<나이, 직업, 작품 속 역할>\)\n- 동기:\n- 손버릇·사물:\n- 변화 곡선:", lambda _: cast, t, count=1)
    t = re.sub(r"^사용법: .*$", "init_project.py가 만든 초안이다. 남은 `<…>` 빈칸을 작가가 채운다(쓰지 않을 줄은 지워도 된다). 린터가 빈칸을 파일:줄로 알려 준다. "
               "숫자·이름 정본은 book-toc.md 블록이고, storyline 단계가 통과 처리 때 이 파일 기준으로 블록을 맞춘다.", t, count=1, flags=re.M)
    total = sum(int(c["pages"]) for c in a["chapters"])
    chs = []
    for i, c in enumerate(a["chapters"], 1):
        last = a["last_line"] if i == len(a["chapters"]) else "<문장>"
        chs.append(f"### {i}장. {c['title']} ({c['pages']}매)\n- 사건:\n- 장 마지막 한 줄: \"{last}\"\n")
    skel = f"## 장 골격 (총 {total}매)\n\n" + "\n".join(chs) + "\n(마지막 장의 마지막 한 줄이 작품의 마지막 줄이다)\n"
    return re.sub(r"## 장 골격 \(총 <매수>매\).*?(?=\n## 시각 닻)", lambda _: skel, t, count=1, flags=re.S)


def init(root, a):
    root = Path(root)
    miss = [k for k in REQUIRED if not a.get(k)]
    if miss:
        raise SystemExit(f"답이 빠졌다: {miss}. 사용자에게 한 번에 묻고 다시 실행한다")
    toc, story = root / "book-toc.md", root / "00_storyline" / "storyline.md"
    exist = [str(f.relative_to(root)) for f in (toc, story) if f.exists()]
    if exist:
        raise SystemExit(f"이미 있다: {exist}. 덮어쓰지 않는다. 새 작품이면 사용자가 옮긴 뒤 다시 실행한다")
    story.parent.mkdir(parents=True, exist_ok=True)
    toc.write_text(build_block(a), encoding="utf-8")
    story.write_text(build_storyline(a), encoding="utf-8")
    st = re.sub(r"`[^`\n]*`", lambda m: " " * len(m.group(0)), story.read_text(encoding="utf-8"))
    holes = len(re.findall(r"<[^<>\n`]*[가-힣][^<>\n`]*>", st))   # 린터(L2 양식 빈칸)와 같은 규칙으로 센다
    return toc, story, holes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--answers", required=True, help="사용자 답을 담은 JSON 파일")
    ap.add_argument("--root", default=".", help="프로젝트 폴더 (기본: 현재 폴더)")
    a = ap.parse_args()
    toc, story, holes = init(a.root, json.loads(Path(a.answers).read_text(encoding="utf-8")))
    print(f"OK {toc}\nOK {story}")
    print(f"다음: storyline.md의 빈칸 {holes}곳(줄거리, 인물, 장별 사건 등)을 작가가 채운다. 직접 쓰기 어렵다면 지휘에게 '빈칸 같이 채우자'고 하면 질문으로 받아 채운다. "
          f"채운 뒤 python3 {SKILL_DIR}/scripts/lint_project.py --root {Path(a.root).resolve()}")


if __name__ == "__main__":
    sys.exit(main())
