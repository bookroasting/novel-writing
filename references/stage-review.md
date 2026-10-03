# review 단계, 리뷰와 수정 사이클

> **묻기와 기록.** 이 문서에서 사용자에게 묻는 자리와 원장에 `gate:`·`waiver:` 줄을 남기는 일은 지휘(`<스킬>/SKILL.md`)가 한다. 서브 에이전트로 실행 중이면 그 자리에서 작업을 저장하고 `need_user`로 돌아간다. 서브 에이전트 없이(Codex 등) 이 문서를 직접 수행할 때는 직접 묻고 기록한다. `stage:`·`note:` 줄은 단계를 수행한 쪽이 쓴다.

내부 리뷰(1~6단계)와 외부 리뷰(7~9단계)를 순서대로 한다. 평가자 인격은 `<스킬>/references/reviewers.md`의 **본문 모드** 섹션에 있고, 이 문서에 다시 적지 않는다. 숫자는 `book-toc.md` 블록, 점수식과 동결 규칙은 `<스킬>/references/workflow.md` 4절을 따른다.

## 0. 준비

1. 원장에 `stage: write done`이 있는지 확인한다.
2. book-toc, 통과본 storyline(1차 사실 소스), `02_outline.md` 인물 시트, reviewers.md 카드 인덱스를 읽는다.
3. 단계마다 모드를 한 줄로 의식한다: 리뷰 단계(1·3·5·7·8)는 카드 인격, 수정 단계(2·4·6·9)는 BLACK.

## 1. 흐름과 이어하기

| 단계 | 모드 | 입력 | 출력 |
|:-:|---|---|---|
| 1 | PINK | 03 | 04_review-pink.md |
| 2 | BLACK 수정 | 03 + 04 | 05_draft-v2.md |
| 3 | 합평 1 (RED·SILVER·BLUE·GOLD) | 05 | 06_ensemble-1.md |
| 4 | BLACK 수정 | 05 + 06 | 07_draft-v3.md |
| 5 | 합평 2 | 07 | 08_ensemble-2.md |
| 5+ | 미통과 시 라운드 k≥3 | 07_draft-v<k+1> | 08_ensemble-<k>.md, 반영본 07_draft-v<k+2>.md |
| 6 | BLACK 통과 정리 | 최신 draft + 최신 ensemble | 09_draft-final.md |
| 7 | EDITOR | 09 | 10_review-editor.md |
| 8 | MARKETER, PROOF | 09 | 11_review-marketer.md, 12_review-proofreader.md |
| 9 | BLACK 최종 수정 | 09 + 10 + 12 | 09_draft-final.md (직전본은 09_draft-final_pre9.md) |

1~9 모든 단계는 끝날 때 원장에 `stage: review-<단계> done <날짜>`를 남긴다(리뷰 단계 포함). 이어하기는 이 줄로 판정한다. publish 단계가 남긴 `reopen: review-9 <사유>`가 있으면 9단계부터 다시 한다. 원장 기록이 없을 때만 파일 존재로 판단한다. 9단계 완료는 원장 `stage: review done`으로만 판정한다(09 파일은 6단계에도 생기므로).

### 순서의 이유

- PINK 단독 첫인상: 첫 두 페이지가 작품의 절반이다. 합평 전에 도입과 호흡을 먼저 잡는다.
- 합평 두 라운드: 한 번만 하면 1라운드 🔴를 고친 효과를 검증할 수 없다.
- EDITOR는 합평 뒤: 시장 시각이 작품 내부 평가에 섞이지 않게 한다.
- MARKETER는 본문 미반영(publish 입력), PROOF는 9단계 수정에 반영.

### 장편 (`structure_mode: "part"`)

위 표를 부마다 따로 돌린다. 파일 이름은 단편 이름 뒤에 `-part<n>`을 붙인다(`05_draft-v2-part1.md`, `06_ensemble-1-part1.md`, `08_ensemble-<k>-part1.md`). 모든 부가 통과하면 부 파일을 이어 붙인 원고로 전체 합평을 한 번 더 한다(`06_ensemble-1-overall.md`, 입력은 부 파일을 이은 임시 통합본 `07_draft-merged-v1.md`). 그다음 6단계에서 `09_draft-final-merged.md`를 만들고 7~9단계는 단편과 같다. 원장 stage 줄에도 부를 붙인다: `stage: review-3-part1 done`.

## 2. 수정 단계 공통 (2·4·6·9)

- 🔴 전부 반영. 🟡는 판단해 반영하고, 넘긴 항목은 이유 한 줄.
- **작가 승인 문장.** `00_author-edits.inherited.md`(rework가 물려준 출판 뒤 수정 기록)에 있는 문장·설정과 back_matter 섹션(작가의 말, 서평)은 작가가 승인한 것이다. 🔴가 이 자리를 고치라고 해도 바로 고치지 않는다. 한 수정 단계에서 걸리는 자리를 **모두 모아 한 번에** `need_user`(질문 id `author-edit`)로 돌아가 자리마다 원래 문장, 제안, 이유를 보여 준다. 나머지 수정은 그동안 마쳐 둔다. 승인되면 고치고, 거절되면 그 🔴는 넘긴 항목으로 이유를 남긴다(`open_red` 대상이 아니다).
- 변경 요약(장·단락·무엇을)은 본문 파일에 넣지 않는다. 다음 합평 파일의 "바뀐 자리" 목록으로 넘기고, 원장에는 한 줄만 남긴다: `stage: review-<단계> done <날짜> 변경 N곳`.
- **변경 0곳이어도 다음 버전 파일은 만든다**(내용은 그대로 복사). 번호 체계가 끊기지 않게 하기 위해서다. 원장에 `변경 0곳`을 남긴다. 다음 합평 라운드의 입력이 앞선 합평 라운드의 입력과 같으면 동결한다. 1라운드(06)는 앞선 합평이 없으므로 PINK 반영이 0곳이어도 그대로 채점한다.

## 3. 리뷰 단계 공통 (1·3·5·7·8)

0. **머리 줄**. 합평 라운드(3·5·5+)는 `입력`, `입력 sha256`, `판정 점수`(4인 평균), `남은 🔴`, `판정: 통과|재수정|동결`을, 한 번만 하는 리뷰(1 PINK, 7 EDITOR, 8 MARKETER·PROOF)는 `입력`, `입력 sha256` 두 줄을 파일 맨 위에 둔다(workflow.md 4.2).
1. **점수 동결 먼저** (합평 라운드만, workflow.md 4.2). 입력 sha256이 앞선 어느 합평 입력과 같으면 채점하지 않는다. 산출물에 `점수 동결` 한 줄과 직전 점수만 쓰고 원장에 `freeze:`를 남긴다.
2. 다르면 `## 바뀐 자리` 섹션(2라운드부터 필수). 점수를 올리는 카드는 바뀐 자리를 근거로 인용한다.
3. 검증기 결과를 근거 자료로 붙인다: `python3 <스킬>/scripts/validate_draft.py --run <run> --draft <입력 파일들>` (장편은 부 파일을 순서대로 모두 준다). 검증기 FAIL 항목은 해당 카드(GOLD: 문체, SILVER: 구조·시점, RED: 사실)의 🔴로 옮긴다.
4. 카드 섹션 헤딩은 `## <카드> 평가`. 카드의 출력 형식과 첫 문장 톤을 따른다.
5. 합평 파일 끝 박스: 카드별 점수, 4인 평균, 🔴 총 건수, 판정.

## 4. 3·5단계 판정

- 4인 평균 ≥ 블록 `review.body_pass` 그리고 🔴 0건이면 통과 → 6단계.
- 🔴가 남으면 점수와 무관하게 다음 라운드.
- 라운드 수가 `review.rounds_before_user_check`에 닿았는데 미통과면 멈추고 묻는다.
  - (a) 한 라운드 더
  - (b) 현재 원고를 09로 확정하고 외부 리뷰로 진행. 원장에 `waiver: open_red <마지막 합평 파일명> <남은 🔴 목록>`과 `gate: waiver-open_red → approved "<원문>"`을 남긴다.
  응답을 원장에 `gate: review-rounds → <a|b>`로 남긴다. 미통과 후 BLACK 반영본 번호는 workflow.md 5절을 따른다(라운드 k 뒤 `07_draft-v<k+2>.md`).

## 5. 6단계, 통과 정리 → `09_draft-final.md`

통과 원고에 마지막 합평의 🟡를 반영해 09를 만든다. 장편(`structure_mode: "part"`)이면 부 파일을 부 순서대로 이어 `09_draft-final-merged.md`를 만든다(부 헤딩 `# <no>부. <title>` 포함). 이후 외부 리뷰는 이 최종본만 입력으로 쓴다. 최종본 이름은 단편 `09_draft-final.md`, 장편 `09_draft-final-merged.md`다.

## 6. 7·8단계, 외부 리뷰

- EDITOR → `10_review-editor.md`
- MARKETER → `11_review-marketer.md`. 카드 출력 형식의 세 블록(`### 판매 카피 초안 (publish 입력)`, `### 검색 키워드 후보 (publish 입력)`, `### 단편집 묶음 추천`)을 반드시 포함. 정본에 없는 수상, 판매량, 평점, 추천인 실명을 쓰지 않는다.
- PROOF → `12_review-proofreader.md`

## 7. 9단계, 최종 수정

1. 09를 `09_draft-final_pre9.md`로 복사해 둔다.
2. EDITOR와 PROOF 지적을 반영한다(MARKETER는 반영하지 않는다).
3. 검증기를 돌린다: `python3 <스킬>/scripts/validate_draft.py --run <run>` (단편·장편 최종본을 알아서 고른다). FAIL 0이어야 한다.
4. MANUAL 네 항목(주술 호응, 위트 횟수·출처, 감정 직접 노출, 장 마지막 줄)은 PROOF·GOLD 결과로 확인했다고 원장에 한 줄씩 남긴다.
5. 원장에 `stage: review done <날짜>`.

9단계 이후 09에 어떤 섹션도 덧붙이지 않는다. 덧붙일 것이 있으면 블록을 고치고 7단계부터 다시 거친다.

완료하면 "리뷰 사이클 완료. publish 단계로 웹 e북을 만드세요."라고 안내한다.
