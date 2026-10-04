"""publish 단계: 원고 → 웹 e북 한 장짜리 HTML (범용).

사용:
  python3 <스킬>/scripts/generate_ebook.py --run <run> [--root <프로젝트 폴더>]

디자인은 블록 `publish.ebook.design`으로 고른다. 찾는 순서: 프로젝트 폴더의 `designs/ebook/<design>.html`(작품 전용 디자인) → `<스킬>/templates/ebook/<design>.html`.
  plain  기본(스킬에 포함). 작품과 무관한 장식만 쓴다.
  작품 전용 디자인은 plain.html을 복사해 프로젝트의 designs/ebook/에 두고 고친다. 슬롯 이름은 그대로 둔다.
디자인 파일의 {{슬롯}}은 모두 블록에서 채운다. 원고는 블록에 정의된 부·장 구간과 back_matter 섹션만 넣는다.
"""
import argparse
import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from booktoc import require_run, ROOT, SKILL_DIR, DEFAULT_TOC, load_params, heading, latest_run, split_draft, outline, final_draft_name, run_params, split_back  # noqa: E402

DESIGNS = SKILL_DIR / "templates" / "ebook"


def design_path(name, root=ROOT):
    for base in (Path(root) / "designs" / "ebook", DESIGNS):
        if (base / f"{name}.html").exists():
            return base / f"{name}.html"
    raise SystemExit(f"e북 디자인 '{name}'을 찾지 못했다: {Path(root) / 'designs' / 'ebook'}, {DESIGNS}")


def manuscript(draft_text, p):
    """부·장 헤딩, 장 본문, back_matter 섹션만 남긴 마크다운. </script> 조기 종료를 막는다."""
    chapters, _ = split_draft(draft_text, p)
    by_heading = {heading(c): c["no"] for c in p["chapters"]}
    out = []
    for kind, h in outline(p):
        out.append(h)
        if kind == "chapter":
            out.append(one_line_per_paragraph(chapters.get(by_heading[h], "")))
    for bh, text in split_back(draft_text, p):
        out += [bh, one_line_per_paragraph(text)]
    return "\n\n".join(out).replace("</script", "<\\/script") + "\n"


def one_line_per_paragraph(text):
    """원고의 줄 하나를 문단 하나로 본다. e북 파서는 빈 줄로 문단을 나누므로 줄 사이에 빈 줄을 넣는다."""
    return "\n\n".join(ln.strip() for ln in text.split("\n") if ln.strip())


def lines_html(lines):
    return "<br>".join(html.escape(x) for x in lines)


def build(draft_text, p, out):
    pub = p["publish"]
    eb = pub.get("ebook", {})
    design = design_path(eb.get("design", "plain"))
    tpl = design.read_text(encoding="utf-8")
    e = html.escape
    title_lines = eb.get("cover_title_lines") or [p["title"]]
    epi = eb.get("epigraph")
    bq = eb.get("back_quote")
    slots = {
        "MANUSCRIPT": manuscript(draft_text, p),
        "TITLE": e(p["title"]),
        "TITLE_JS": json.dumps(p["title"], ensure_ascii=False),
        "PEN_NAME": e(p["pen_name"]),
        "GENRE_LABEL": e(pub["cover_label"]),
        "DESCRIPTION": e(eb.get("description", "")),
        "OG_DESCRIPTION": e(eb.get("og_description") or eb.get("description", "")),
        "COVER_TITLE_1": e(title_lines[0]),
        "COVER_TITLE_2": e(title_lines[1] if len(title_lines) > 1 else ""),
        "COVER_COPY": e(eb.get("cover_copy", "")),
        "PUBLISHER": e(pub.get("publisher") or ""),
        "COVER_PUBLISHER": "",   # 디자인이 <template data-slot="COVER_PUBLISHER">로 모양을 정한다 (아래)
        "BACK_PUBLISHER": (f'<div class="back-publisher">\n              <span class="pub-mark"></span>\n              <span>{e(pub["publisher"])}</span>\n            </div>'
                           if pub.get("publisher") else ""),
        "PUBLISHER_LINE": f"<div>발행 · {e(pub['publisher'])}</div>" if pub.get("publisher") else "",
        "PUB_DATE_LINE": f"<div>{e(pub['pub_date'])} 발행</div>" if pub.get("pub_date") else "",
        "ISBN_LINE": f'<div class="copyright-isbn">ISBN {e(pub["isbn"])}</div>' if pub.get("isbn") else "",
        "COPYRIGHT_LINE": (f'<div class="copyright-c">© {e(str(pub["copyright_year"]))} {e(pub.get("copyright_holder") or p["pen_name"])}</div>'
                           if pub.get("copyright_year") else ""),
        "COLOPHON_NOTE_LINE": (f'<div class="copyright-c copyright-note">{e(pub["colophon_note"])}</div>'
                               if pub.get("colophon_note") else ""),
        "HAS_EPIGRAPH": "true" if epi else "false",
        "EPIGRAPH_TEXT": lines_html(epi["lines"]) if epi else "",
        "EPIGRAPH_ATTR": lines_html(epi.get("attr_lines") or [epi.get("attr", "")]) if epi else "",
        "BACK_QUOTE_BLOCK": (f'<div class="back-quote">{lines_html(bq["lines"])}</div>\n'
                             f'            <div class="back-quote-attr">{lines_html(bq.get("attr_lines") or [bq.get("attr", "")])}</div>') if bq else "",
        "SYNOPSIS": "<br>\n              ".join(e(x) for x in eb.get("synopsis", [])),
    }
    # 디자인 전용 조각: <template data-slot="이름">…</template>. 출판사가 있을 때만 그 조각을 쓰고, 조각 자체는 결과물에서 뺀다.
    # 좌표·색 같은 모양은 디자인 파일이 갖고, 생성기는 값만 넣는다.
    def take(m):
        slots[m.group(1)] = m.group(2).strip().replace("{{PUBLISHER}}", e(pub.get("publisher") or "")) if pub.get("publisher") else ""
        return ""
    tpl = re.sub(r'[ \t]*<template data-slot="(\w+)">(.*?)</template>\n?', take, tpl, flags=re.S)
    left = set(re.findall(r"\{\{(\w+)\}\}", tpl)) - set(slots)
    if left:
        raise SystemExit(f"디자인 {design.name}에 채울 수 없는 슬롯: {sorted(left)}")
    for k, v in slots.items():
        tpl = tpl.replace("{{" + k + "}}", v)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(tpl, encoding="utf-8")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run")
    ap.add_argument("--draft")
    ap.add_argument("--out")
    ap.add_argument("--toc", default=str(DEFAULT_TOC))
    ap.add_argument("--root", help="프로젝트 폴더 (기본: book-toc.md를 위로 찾아감)")
    a = ap.parse_args()
    run = require_run(a.run or latest_run())
    p = run_params(run) if a.toc == str(DEFAULT_TOC) else load_params(a.toc)
    draft = Path(a.draft) if a.draft else ROOT / "02_draft" / run / final_draft_name(p)
    out = Path(a.out) if a.out else ROOT / "03_output" / run / "ebook.html"
    build(draft.read_text(encoding="utf-8"), p, out)
    print(f"OK {out}  ({p['title']} / 디자인 {p['publish'].get('ebook', {}).get('design', 'plain')})")


if __name__ == "__main__":
    main()
