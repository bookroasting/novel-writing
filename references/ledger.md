# ledger.md, 원장·게이트·waiver 규칙

`workflow.md` 3절을 나눈 문서다. 경로 표기(`<스킬>`, 프로젝트 폴더)는 `workflow.md` 머리와 같다.

## 원장 `00_RUN_STATUS.md`

```
status: in-progress | published | published-with-known-issues
stage: storyline done 2026-05-05
gate: storyline-pass → a (2026-05-05) "컨펌, 진행"
freeze: review-round-2 입력 해시 = 직전 라운드, 채점 생략
waiver: <검사 id> <사유>
gate: waiver-<검사 id> → approved (2026-05-05) "<사용자 응답 원문>"
closed: superseded 2026-10-03
```

- `gate:` 줄. 사용자에게 선택을 물은 모든 자리의 질문 id, 응답, 날짜, 응답 원문. 응답을 받기 전에는 다음 단계로 가지 않는다. **기록은 지휘(SKILL.md)가 한다.** 서브 에이전트는 `gate:` 줄을 쓰지 않는다. 예외로 `new_run.py`는 `--answer`로 받은 원문을 `gate: new-run` 줄로 직접 쓴다.
- `waiver:` 줄. 규칙 위반을 숨기지 않고 남기는 자리다. 짝이 되는 사용자 승인 줄이 있어야 린터가 WARN으로 내린다. 진행 중 run은 `gate: waiver-<id> → approved "<응답 원문>"`, 닫힌 run은 `gate: close-run → approved "<응답 원문>"`이다. `approved`가 아닌 응답은 승인이 아니다. 에이전트가 혼자 쓴 waiver는 FAIL 그대로다.
- 승인 줄은 **바로 위** waiver 하나만 승인한다(사이에 빈 줄과 `note:` 줄만 올 수 있다). waiver를 쓰면 곧바로 그 아래에 승인 줄을 둔다. waiver 두 줄 뒤에 승인 한 줄이면 위쪽 waiver는 승인되지 않는다. 유일한 예외: 닫힌 run의 `gate: close-run → approved "<원문>"`은 그보다 앞선 미승인 waiver를 함께 승인한다. run을 닫을 때 사용자에게 남은 waiver 목록을 보여 주고 묻는다.
- 다음 단계 산출물이 있으면 그 단계의 게이트가 닫혀 있어야 한다. 기준은 마지막 reopen 이후다(스토리 `reopen: storyline`, 본문 `reopen: review-1`~`review-5`). 게이트는 다음 셋 중 **하나**로 닫힌다.
  1. 최신 합평이 `판정: 통과`다. 스토리는 그 뒤 `gate: storyline-pass → a`도 있어야 한다. 본문은 통과 판정만으로 닫히되, 본문 reopen이 있었다면 그 뒤 `stage: review-3/5 done`이 있어야 한다. 장편은 블록 `parts`의 모든 부와 overall 합평이 각각 이 조건을 채워야 한다.
  2. 최신 합평 파일명을 적은 `open_red` waiver가 승인되었고, 라운드 상한 응답(스토리 `storyline-rounds → c`, 본문 `review-rounds → b`)이 있다.
  3. 기준 시점 뒤에 승인된 `waiver: gate_log story|body <사유>`가 있다(첫 낱말이 대상 게이트). 옛 run의 기록 누락을 남기는 용도다.
- 작가 산출물(03_output의 html·md·pdf와 예전 작품의 docx, 02_draft의 09 최종본)을 옮겨 없앴다면 run 원장에 `gate: remove-<파일명 또는 형식 이름> → approved "<원문>"`이 있어야 한다(`remove-final.docx`와 `remove-docx`는 같은 승인이다). 형식을 블록에서 빼면 `republish.py`가 그 산출물을 승인 확인 뒤 보관함으로 옮긴다. 린터가 `_archive/MANIFEST.tsv`와 대조한다.
- waiver id: `open_red`(라운드 상한에서 남은 🔴를 안고 진행), `fictional_reviewer`(가상 평자의 서평·추천사), `pass_threshold`, `round_gate`, `review_freeze`, `change_log`, `ensemble_header`, `ensemble_integrity`, `gate_log`, `publish_gate`, `publish_files`, `metadata`, `lock`, `epigraph_source`(출처를 확인하지 않은 제사를 싣기로 함). 라운드 상한 게이트에서 사용자가 진행을 고르면 `waiver: open_red <통과로 볼 합평 파일명> <남은 🔴 목록>`과 `gate: waiver-open_red → approved "<원문>"`을 그 아래에 함께 남긴다. 린터는 파일명이 적힌 waiver만 그 합평의 통과로 인정하고, 승인 줄이 waiver 줄보다 뒤에 있어야 인정한다. 라운드 상한 게이트는 상한을 넘긴 라운드마다 응답이 하나씩 있어야 한다(`storyline-rounds`는 a/b/c, `review-rounds`는 a/b).
- rework run은 물려받은 run의 스토리 게이트가 닫혀 있어야 한다(`gate: storyline-pass → a` 또는 승인된 `open_red`·`gate_log` waiver). `new_run.py`와 린터가 함께 검사한다.
- `closed:` 줄. 더 이어 쓰지 않는 run. 재작업은 새 run에서 한다.
- rework는 지난 run에서 승인된 `fictional_reviewer` waiver를 **승인 줄 원문 그대로** 짝으로 옮긴다(close-run으로 함께 승인된 경우 그 응답 원문을 waiver 승인 줄로 옮긴다). `gate: block-change` 줄도 `(inherited from <run>)`을 붙여 옮긴다.

## 잠금 `lock:`

```
lock: back_matter=["작가의 말", "서평"] formats=["ebook"] snapshot=<스냅샷 해시> publish=<출판 정보 해시> block=lock-03.json draft=<최종 원고 해시> blocksha=<잠금 파일 해시> out=<e북 해시> out2=<e북·metadata 해시>
```

- 그 시점의 작가 산출물 목록과 블록 전체를 잠근다. 블록 사본은 `01_test/<run>/locks/lock-NN.json`이다. `new_run.py`가 run을 열 때, publish 단계가 출판을 마칠 때(`lock_run.py`), `republish.py`가 출판 뒤 수정을 마칠 때 남긴다.
- 잠금 줄과 잠금 파일은 지우지 않는다. 린터는 잠금 줄이 하나도 없는데 `gate: new-run`이 있거나, 원장에 없는 잠금 파일이 있거나, 앞 잠금에 있던 `block=`이 뒤 잠금에서 빠지면 FAIL이다.
- 린터는 잠금을 **구간마다** 비교한다: 이어진 두 잠금 사이, 마지막 잠금과 지금. 다시 잠그기만 해서 앞 구간의 변경을 덮을 수 없고, `lock_run.py`·`republish.py`는 위반이 있으면 쓰지 않는다. `lock_run.py`는 진행 중인 출판 뒤 수정(마지막 잠금 뒤 post-audit 승인이 있고 아직 `stage: post-audit-fix done`이 없음)이 있어도 잠그지 않는다. 그 수정은 `republish.py`가 마치며 잠근다. 규칙은 `booktoc.lock_violations` 하나다.
- 구간 안에서 필요한 것 (없으면 FAIL `lock`):
  - `back_matter`·`formats` 항목이 빠졌다 → 그 항목 이름의 `gate: remove-<항목> → approved (날짜) "<원문>"`.
  - 블록 값이 바뀌었다(항목 추가 포함) → 바뀐 **키를 적은** 승인 `gate: block-change → approved <키>[·<키>] (날짜) "<원문>"`. 키 목록은 `approved` 바로 뒤부터 첫 괄호·따옴표 앞까지이고(날짜·응답 원문 속 낱말은 키가 아니다), 각 키는 바뀐 값의 경로 자체(`publish.ebook.epigraph`), 그 상위 경로(`review`), 또는 끝 이름(`publisher`)이어야 한다. 경로 중간 마디(`ebook`)는 하위 전체를 덮지 않는다. 출판 정보 빈칸 채우기는 `gate: publish-info → approved`, 제사 출처 확인은 `gate: epigraph-source → verified`가 그 범위를 덮는다.
  - storyline 동기화 키(`characters`, `retired_names`, `anchors`, `last_line`, `forbidden_disclosures`)만 단계 작업의 `note: block-change <키>`로 바꿀 수 있다. 통과선(`review.*`), 출판 정보(`publish.*`) 같은 다른 키는 note로 못 바꾼다.
  - `post-audit`, 무관한 `remove-…` 승인은 블록 변경을 덮지 않는다.
- 출판(`stage: publish done`) 뒤의 잠금이 있으면, 그 뒤 최종 원고(`09_draft-final*.md`)나 출판 산출물(`ebook.html`, `metadata.md`)이 바뀐 구간에는 `gate: post-audit → approved`가 있어야 한다. 글자 수가 같은 수정도, 다른 원고 파일로 생성기를 직접 돌린 것도 해시로 잡는다.
- 잠금 파일은 원장 줄의 `blocksha=`와 대조한다. 잠금 뒤 파일만 고치면 FAIL이다.
- 출판 뒤 원고·산출물이 바뀐 잠금 구간은 `republish.py` 절차로만 닫힌다: owner·changelog가 적힌 `note: post-audit-prepare` 줄이 정확히 하나, 같은 owner(이어받았으면 이어받은 owner)의 `stage: post-audit-fix done … (republish.py, owner <owner>, …)` 줄, 원고가 바뀌었으면 산출물도 다시 만들어졌어야 한다. 손으로 쓴 done 줄은 닫힘이 아니다.
- 끊긴 수정: `--takeover`는 마지막 prepare·takeover 뒤의 `gate: post-audit-takeover → approved` 하나로 한 번만 이어받는다. `--abandon`은 `gate: post-audit-abandon → approved` 뒤에 원고·블록·스냅샷(필요하면 산출물)을 수정 전 보관본으로 되돌리고 `stage: post-audit-fix abandoned`와 잠금 줄을 남긴다. 다음 수정은 새 승인부터 시작한다.
- `publish-info` 승인은 블록에 이미 있던 빈칸 값만 덮는다. 새로 생긴 키는 `block-change` 승인이 필요하다.
- **승인으로 세는 응답은 `→ approved`와 `→ verified`뿐이다.** `→ rejected`나 다른 선택은 승인이 아니다.
- `block=`이 없는 옛 잠금 줄은 해시로만 비교한다(스냅샷: block-change 승인 또는 note, 출판 정보: block-change·publish-info·epigraph-source 승인).
- `stage: publish done`이 있는데 잠금이 없거나 마지막 잠금이 그보다 앞서면 FAIL이다.
- 한계: 원장과 잠금 파일을 함께 위조하는 것은 도구가 막지 못한다. 사람이 원장의 응답 원문을 확인한다(workflow.md 7절).
