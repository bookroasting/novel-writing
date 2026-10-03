# 워크플로우 원장: 20261003_01

status: in-progress
gate: new-run → same (2026-10-03) "첫 run"
lock: back_matter=["작가의 말", "서평"] formats=["docx", "ebook"] snapshot=253a317f96028b12 publish=d00751fd3994b005 block=lock-01.json draft=none blocksha=95ee8137a0d00333 out=none out2=none
note: 이 run은 스킬 저장소의 예시 작품이다. 합평 기록은 생략했다(아래 gate_log waiver)
stage: storyline done 2026-10-03
gate: storyline-pass → a (2026-10-03) "예시: 진행"
waiver: gate_log story 예시 작품이라 스토리 합평 기록을 생략했다
gate: waiver-gate_log → approved (2026-10-03) "예시: 생략 승인"
stage: research done 2026-10-03
gate: write-mode → b (2026-10-03) "예시: 한 번에"
stage: write done 2026-10-03
waiver: gate_log body 예시 작품이라 본문 합평 기록을 생략했다
gate: waiver-gate_log → approved (2026-10-03) "예시: 생략 승인"
stage: review done 2026-10-03
waiver: fictional_reviewer 09_draft-final.md 서평은 가상 평자의 예시 글이다
gate: waiver-fictional_reviewer → approved (2026-10-03) "예시: 가상 서평 유지"
gate: trim → 신국판 (2026-10-03) "예시: 신국판"
stage: publish done 2026-10-03
status: published
lock: back_matter=["작가의 말", "서평"] formats=["docx", "ebook"] snapshot=253a317f96028b12 publish=d00751fd3994b005 block=lock-02.json draft=a3bcd6e0eec37cb8 blocksha=95ee8137a0d00333 out=2734252d8bc2332e out2=207d1cef8245e795
gate: post-audit → approved (2026-10-03) "예시: 첫 문장을 조금 고쳐"
note: post-audit-prepare _archive/20261003_111716_463652_post-audit_261405 changelog=ea108214cd22d5bc owner=261405
stage: post-audit-fix done 2026-10-03 (republish.py, owner 261405, 보관: _archive/20261003_111716_514951_post-audit_261405, 기록: 02_draft/20261003_01/14_post-audit-changelog.md)
lock: back_matter=["작가의 말", "서평"] formats=["docx", "ebook"] snapshot=253a317f96028b12 publish=d00751fd3994b005 block=lock-03.json draft=22236c585d7b1e4b blocksha=95ee8137a0d00333 out=fdf4175f6b134cfe out2=292fc9aba000a50d
gate: post-audit → approved (2026-10-03) "스킬을 수정하자. 작업 완료 버전은 ebook.html 파일로 만드는 걸로. docx 는 만들지 마" (예시 작품을 e북 하나로 옮김)
gate: remove-docx → approved (2026-10-03) "스킬을 수정하자. 작업 완료 버전은 ebook.html 파일로 만드는 걸로. docx 는 만들지 마"
gate: block-change → approved publish.formats·trim_options·body_font·body_font_fallback·body_size_pt·line_spacing·first_line_indent_chars·heading_font·heading_size_pt·heading_color·margin_cm·header·footer (2026-10-03) "스킬을 수정하자. 작업 완료 버전은 ebook.html 파일로 만드는 걸로. docx 는 만들지 마"
note: post-audit-prepare _archive/20261003_112516_683621_post-audit_dc014d changelog=067d6d98907fc6ae owner=dc014d
stage: post-audit-fix done 2026-10-03 (republish.py, owner dc014d, 보관: _archive/20261003_112530_392681_post-audit_dc014d, 기록: 02_draft/20261003_01/14_post-audit-changelog.md)
lock: back_matter=["작가의 말", "서평"] formats=["ebook"] snapshot=209f95fc290f1510 publish=f17c23d73336b121 block=lock-04.json draft=22236c585d7b1e4b blocksha=b5dfa4c966951176 out=f6963eda86c9669e out2=0a8e24fe767ac554
