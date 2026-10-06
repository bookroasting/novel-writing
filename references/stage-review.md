# review 단계, 리뷰와 수정 사이클

> **묻기와 기록.** 이 문서에서 사용자에게 묻는 자리와 원장에 `gate:`·`waiver:` 줄을 남기는 일은 지휘(`<스킬>/SKILL.md`)가 한다. 서브 에이전트로 실행 중이면 그 자리에서 작업을 저장하고 `need_user`로 돌아간다. 서브 에이전트 없이(Codex 등) 이 문서를 직접 수행할 때는 직접 묻고 기록한다. `stage:`·`note:` 줄은 단계를 수행한 쪽이 쓴다.

내부 리뷰(1~6단계), PURPLE 루프(6P), 외부 리뷰(7~9단계)를 순서대로 한다. 평가자 인격은 `<스킬>/references/reviewers.md`의 **본문 모드** 섹션에 있고, 이 문서에 다시 적지 않는다. 숫자는 `book-toc.md` 블록, 점수식과 동결 규칙은 `<스킬>/references/workflow.md` 4절을 따른다.

## 0. 준비

1. 원장에 `stage: write done`이 있는지 확인한다.
2. book-toc, 통과본 storyline(1차 사실 소스), `02_outline.md` 인물 시트, reviewers.md 카드 인덱스를 읽는다. 단, 처음 읽는 독자 점검(reader-check)과 PURPLE 평가를 맡은 호출은 이것들을 읽지 않는다(3절 0.5, purple-loop.md 2절).
3. 단계마다 모드를 한 줄로 의식한다: 리뷰 단계(1·3·5·7·8)와 PURPLE 평가는 카드 인격, 수정 단계(2·4·6·9)와 PURPLE Resolve·Rewrite는 BLACK.

## 1. 흐름과 이어하기

| 단계 | 모드 | 입력 | 출력 |
|:-:|---|---|---|
| 1 | PINK | 03 | 04_review-pink.md |
| 2 | BLACK 수정 | 03 + 04 | 05_draft-v2.md |
| 3 | 처음 읽는 독자 점검 → 합평 1 (RED·SILVER·BLUE·GOLD) | 05 | 06_reader-check-1.md → 06_ensemble-1.md |
| 4 | BLACK 수정 | 05 + 06 | 07_draft-v3.md |
| 5 | 처음 읽는 독자 점검 → 합평 2 | 07 | 08_reader-check-2.md → 08_ensemble-2.md |
| 5+ | 미통과 시 라운드 k≥3 | 07_draft-v<k+1> | 08_reader-check-<k>.md → 08_ensemble-<k>.md, 반영본 07_draft-v<k+2>.md |
| 6 | BLACK 통과 정리 | 최신 draft + 최신 ensemble | 09_draft-final.md |
| 6P | PURPLE 루프 (Rate → Resolve → Rewrite → Rerate, 마지막에 독자 점검) | 09 | 13_purple-<k>.md, 13_purple-resolve-<k>.md, 13_draft-purple-v<k>.md, 13_reader-check-<k>.md → 09_draft-final.md |
| 7 | IVORY | 09 | 10_review-editor.md |
| 8 | ORANGE, OLIVE | 09 | 11_review-marketer.md, 12_review-proofreader.md |
| 9 | BLACK 최종 수정 | 09 + 10 + 12 | 09_draft-final.md (직전본은 09_draft-final_pre9.md) |

1~9 모든 단계는 끝날 때 원장에 `stage: review-<단계> done <날짜>`를 남긴다(리뷰 단계 포함). 6P는 `stage: review-purple done`이다. 이어하기는 이 줄로 판정한다. publish 단계가 남긴 `reopen: review-9 <사유>`가 있으면 9단계부터, `reopen: review-purple <사유>`가 있으면 6P부터 다시 하고 7~9단계도 다시 거친다. 원장 기록이 없을 때만 파일 존재로 판단한다. 9단계 완료는 원장 `stage: review done`으로만 판정한다(09 파일은 6단계에도 생기므로).

### 순서의 이유

- PINK 단독 첫인상: 첫 두 페이지가 작품의 절반이다. 합평 전에 도입과 호흡을 먼저 잡는다.
- 합평 두 라운드: 한 번만 하면 1라운드 🔴를 고친 효과를 검증할 수 없다.
- 독자 점검을 합평보다 먼저: 카드는 설계도와 맞춰 읽어서, 설계도를 모르는 독자가 멈추는 자리(호칭, 숫자, 압축한 비유, 메모의 뜻)를 놓친다. 점수가 통과선을 넘어도 독자가 멈추는 원고는 통과가 아니다.
- PURPLE 루프는 합평 통과 뒤, 외부 리뷰 앞: 합평 중에 돌리면 4인 합평의 🔴(사실, 시점, 문체)와 같은 문장을 두 번 고치게 된다. 루프는 문장을 많이 덜어 내므로, IVORY와 OLIVE가 덜어 낸 뒤의 원고를 봐야 교정이 다시 깨지지 않는다.
- IVORY는 합평 뒤: 시장 시각이 작품 내부 평가에 섞이지 않게 한다.
- ORANGE는 본문 미반영(publish 입력), OLIVE는 9단계 수정에 반영.

### 장편 (`structure_mode: "part"`)

위 표를 부마다 따로 돌린다. 파일 이름은 단편 이름 뒤에 `-part<n>`을 붙인다(`05_draft-v2-part1.md`, `06_reader-check-1-part1.md`, `06_ensemble-1-part1.md`, `08_ensemble-<k>-part1.md`). 모든 부가 통과하면 부 파일을 이어 붙인 원고로 전체 합평을 한 번 더 한다(`06_ensemble-1-overall.md`, 입력은 부 파일을 이은 임시 통합본 `07_draft-merged-v1.md`). 그다음 6단계에서 `09_draft-final-merged.md`를 만들고 6P와 7~9단계는 단편과 같다(PURPLE 루프는 통합본으로 한 번 돈다). 원장 stage 줄에도 부를 붙인다: `stage: review-3-part1 done`.

## 2. 수정 단계 공통 (2·4·6·9)

- 🔴 전부 반영. 🟡는 판단해 반영하고, 넘긴 항목은 이유 한 줄.
- **작가 승인 문장.** `00_author-edits.inherited.md`(rework가 물려준 출판 뒤 수정 기록)에 있는 문장·설정과, back_matter 섹션 가운데 작가가 원문을 주거나 초안을 승인한 것(작가의 말, 서평)은 작가가 승인한 것이다. BLACK에게 맡긴 작가의 말은 여기에 들지 않는다(stage-write.md 3절). 🔴가 이 자리를 고치라고 해도 바로 고치지 않는다. 한 수정 단계에서 걸리는 자리를 **모두 모아 한 번에** `need_user`(질문 id `author-edit`)로 돌아가 자리마다 원래 문장, 제안, 이유를 보여 준다. 나머지 수정은 그동안 마쳐 둔다. 승인되면 고치고, 거절되면 그 🔴는 넘긴 항목으로 이유를 남긴다(`open_red` 대상이 아니다).
- 변경 요약(장·단락·무엇을)은 본문 파일에 넣지 않는다. 다음 합평 파일의 "바뀐 자리" 목록으로 넘기고, 원장에는 한 줄만 남긴다: `stage: review-<단계> done <날짜> 변경 N곳`.
- **변경 0곳이어도 다음 버전 파일은 만든다**(내용은 그대로 복사). 번호 체계가 끊기지 않게 하기 위해서다. 원장에 `변경 0곳`을 남긴다. 다음 합평 라운드의 입력이 앞선 합평 라운드의 입력과 같으면 동결한다. 1라운드(06)는 앞선 합평이 없으므로 PINK 반영이 0곳이어도 그대로 채점한다.

## 3. 리뷰 단계 공통 (1·3·5·7·8)

0. **머리 줄**. 합평 라운드(3·5·5+)는 `입력`, `입력 sha256`, `판정 점수`(4인 평균), `남은 🔴`, `판정: 통과|재수정|동결`을, 한 번만 하는 리뷰(1 PINK, 7 IVORY, 8 ORANGE·OLIVE)는 `입력`, `입력 sha256` 두 줄을 파일 맨 위에 둔다(workflow.md 4.2).
0.5. **처음 읽는 독자 점검 먼저** (합평 라운드만). `<스킬>/references/reader-check.md`를 따른다. 서브 에이전트를 쓸 수 있으면 지휘가 이 점검만 하는 새 호출을 연다(목적: `reader-check <입력 파일>`). 그 호출은 입력 원고와 reader-check.md만 읽고 storyline, outline, 리서치 노트, book-toc 인물 서술, 이전 합평을 열지 않는다. 산출물은 `06_reader-check-1.md`(1라운드), `08_reader-check-<k>.md`(라운드 k)이고 재독 로그를 반드시 담는다. 입력이 앞선 라운드와 같아 동결하는 라운드는 점검도 하지 않는다. 합평을 맡은 호출은 그 라운드의 reader-check 파일이 없으면 채점하지 않고 돌아가 `다음:`에 "reader-check <입력 파일> 새 호출 필요"라고 적는다.
1. **점수 동결 먼저** (합평 라운드만, workflow.md 4.2). 입력 sha256이 앞선 어느 합평 입력과 같으면 채점하지 않는다. 산출물에 `점수 동결` 한 줄과 같은 입력이던 라운드의 점수만 쓰고 원장에 `freeze:`를 남긴다.
2. 다르면 `## 바뀐 자리` 섹션(2라운드부터 필수). 점수를 올리는 카드는 바뀐 자리를 근거로 인용한다.
3. 검증기 결과를 근거 자료로 붙인다: `python3 <스킬>/scripts/validate_draft.py --run <run> --draft <입력 파일들>` (장편은 부 파일을 순서대로 모두 준다). 검증기 FAIL 항목은 해당 카드(GOLD: 문체, SILVER: 구조·시점, RED: 사실)의 🔴로 옮긴다.
4. 카드 섹션 헤딩은 `## <카드> 평가`. 카드의 출력 형식과 첫 문장 톤을 따른다.
5. 합평 파일 끝 박스: 카드별 점수, 4인 평균, 🔴 총 건수(reader-check 🔴 포함), 판정. 머리 줄 아래에 `reader-check: <파일명> 🔴 N` 한 줄을 두고, `남은 🔴`에는 카드 🔴와 reader-check 🔴를 더해 적는다. GOLD는 reader-check의 요약을 storyline과 대조한다(reader-check.md 2절).
6. 점수 보정: 재독 로그에 자리가 있으면 그 자리를 맡는 카드 점수는 reviewers.md "점수 보정"을 따른다.

## 4. 3·5단계 판정

- 4인 평균 ≥ 블록 `review.body_pass` 그리고 🔴 0건(카드 🔴와 reader-check 🔴 모두)이면 통과 → 6단계.
- reader-check 🔴가 하나라도 남으면 4인 평균과 무관하게 `판정: 재수정`이다.
- 🔴가 남으면 점수와 무관하게 다음 라운드.
- 라운드 수가 `review.rounds_before_user_check`에 닿았는데 미통과면 멈추고 묻는다.
  - (a) 한 라운드 더
  - (b) 현재 원고를 09로 확정하고 외부 리뷰로 진행. 원장에 `waiver: open_red <마지막 합평 파일명> <남은 🔴 목록>`과 `gate: waiver-open_red → approved "<원문>"`을 남긴다.
  응답을 원장에 `gate: review-rounds → <a|b>`로 남긴다. 미통과 후 BLACK 반영본 번호는 workflow.md 5절을 따른다(라운드 k 뒤 `07_draft-v<k+2>.md`).

## 5. 6단계, 통과 정리 → `09_draft-final.md`

통과 원고에 마지막 합평의 🟡를 반영해 09를 만든다. 장편(`structure_mode: "part"`)이면 부 파일을 부 순서대로 이어 `09_draft-final-merged.md`를 만든다(부 헤딩 `# <no>부. <title>` 포함). 이후 외부 리뷰는 이 최종본만 입력으로 쓴다. 최종본 이름은 단편 `09_draft-final.md`, 장편 `09_draft-final-merged.md`다.

## 5.5 6P단계, PURPLE 루프

`<스킬>/references/purple-loop.md`를 그대로 따른다. 요약하면 다음과 같다.

1. `09_draft-final.md`(장편은 `09_draft-final-merged.md`)를 `13_draft-purple-v0.md`로 복사한다.
2. 지휘가 PURPLE을 새 호출로 부른다(목적 `purple <입력> <회차>`). PURPLE은 카드와 원고만 읽고 평가만 한다.
3. BLACK이 결함마다 수용, 기각, 보류를 이유와 함께 표로 남기고(Resolve), 10점 기준으로 다시 쓴다(Rewrite). 주제가 해설에만 기대면 화면, 사물, 대사로 보강한다.
4. 새 PURPLE 호출이 무엇이 해결됐는지 결함 번호별로 다시 평가한다(Rerate).
5. PURPLE이 합격하면 처음 읽는 독자 점검을 새 호출로 한 번 한다. 🔴 0이면 마지막 버전을 09로 복사하고 원장에 `stage: review-purple done`을 남긴다.
6. back_matter는 본문 루프에 섞지 않는다. BLACK에게 맡긴 작가의 말이 있으면 본문 루프를 마친 뒤 그 섹션만 입력으로 PURPLE 카드 "작가의 말 모드" 회차를 따로 돌린다(회차 번호는 이어 간다). 작가가 원문을 주거나 승인한 back_matter는 돌리지 않는다.

통과 조건은 PURPLE 카드의 합격선과 마지막 독자 점검 🔴 0이다. 회차 상한이나 중단 조건(평균 상승폭이 0.2 미만인 회차가 2번 이어짐)에 닿으면 `purple-rounds` 게이트로 묻는다. 진행을 고르면 `purple_open` waiver를 남긴다. 둘 중 하나가 없으면 7단계로 가지 않는다.

## 6. 7·8단계, 외부 리뷰

- IVORY → `10_review-editor.md`
- ORANGE → `11_review-marketer.md`. 카드 출력 형식의 세 블록(`### 판매 카피 초안 (publish 입력)`, `### 검색 키워드 후보 (publish 입력)`, `### 단편집 묶음 추천`)을 반드시 포함. 정본에 없는 수상, 판매량, 평점, 추천인 실명을 쓰지 않는다.
- OLIVE → `12_review-proofreader.md`

## 7. 9단계, 최종 수정

1. 09를 `09_draft-final_pre9.md`로 복사해 둔다.
2. IVORY와 OLIVE 지적을 반영한다(ORANGE는 반영하지 않는다).
3. 검증기를 돌린다: `python3 <스킬>/scripts/validate_draft.py --run <run>` (단편·장편 최종본을 알아서 고른다). FAIL 0이어야 한다.
4. MANUAL 항목(주술 호응, 위트 횟수·출처, 감정 직접 노출, 장 마지막 줄, 처음 읽는 독자 점검)은 OLIVE·GOLD 결과와 마지막 reader-check로 확인했다고 원장에 한 줄씩 남긴다. 9단계에서 고친 문단은 reader-check.md R1~R9·R12로 다시 훑는다. 검증기의 `한글 수 표기`·`단문 나열` WARN은 고치거나 남긴 이유를 한 줄 적는다.
5. 원장에 `stage: review done <날짜>`.

9단계 이후 09에 어떤 섹션도 덧붙이지 않는다. 덧붙일 것이 있으면 블록을 고치고 7단계부터 다시 거친다.

완료하면 "리뷰 사이클 완료. publish 단계로 웹 e북을 만드세요."라고 안내한다.
