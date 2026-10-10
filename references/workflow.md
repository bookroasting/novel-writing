# workflow.md, 소설쓰기 워크플로우 규약

이 파일은 `novel-writing` 스킬의 다섯 단계(storyline, research, write, review, publish)가 공통으로 따르는 규약이다. 스킬의 진입점은 `<스킬>/SKILL.md`, 작품 값은 프로젝트의 `book-toc.md` 작품 파라미터 블록(이하 "블록")이다.

**경로 표기.** `<스킬>`은 이 스킬 폴더(`SKILL.md`가 있는 폴더)다. 그 밖의 경로(`book-toc.md`, `00_storyline/`, `01_test/` 등)는 모두 **프로젝트 폴더** 기준이다. 프로젝트 폴더는 `book-toc.md`가 있는 폴더이며, 스크립트는 현재 폴더에서 위로 올라가며 이 파일을 찾는다(`--root`로 직접 줄 수도 있다).

**폴더 이름 규칙.** 새로 만드는 폴더는 영문 소문자·숫자·하이픈·밑줄로만 짓는다. 한글 폴더 이름은 쓰지 않는다. 작품 폴더는 `docs/<영문-슬러그>/`다. `lint_project.py`가 L6에서 검사한다.

**숫자 규칙.** 이 파일과 단계 문서에는 작품 고유 값(인물명, 매수, 시각 닻, 마지막 줄)과 통과선 숫자를 적지 않는다. 블록의 키 이름으로만 가리킨다(예: `review.story_pass`). 설명용 예시를 둘 때는 줄 앞에 `예시(작품명):`를 붙인다. `lint_project.py`가 이 규칙을 검사한다.

## 1. 파일 역할

| 파일 | 역할 | 작품마다 교체 |
|---|---|:-:|
| `00_storyline/storyline.md` | 1차 콘셉트(스토리 설계도). 날짜 폴더 없이 한 장 | 예 |
| `book-toc.md` | 블록(숫자·이름·통과선) + 페르소나·문체 서술 | 예 |
| `<스킬>/SKILL.md` | 지휘: 단계 선택, 서브 에이전트 위임, 사용자 확인 | 아니오 |
| `<스킬>/agents/novel-writing-<단계>.md` | 단계별 서브 에이전트 (Claude Code) | 아니오 |
| `<스킬>/references/stage-<단계>.md` | 단계별 실행 절차. 서브 에이전트와 Codex가 읽는다 | 아니오 |
| `<스킬>/references/reviewers.md` | 14장 평가자 카드. 작품 값은 블록과 storyline에서 읽는다 | 아니오 |
| `<스킬>/references/reader-check.md` | 처음 읽는 독자 점검표(R1~R12)와 재독 로그 | 아니오 |
| `<스킬>/references/purple-loop.md` | PURPLE 4R 루프(설명충·중언부언·주제 전달) | 아니오 |
| `<스킬>/references/read-aloud.md` | 구두 낭독 점검 루프(연결·습관어·문단·이해, 출판 뒤 윤문과 작가의 말) | 아니오 |
| `<스킬>/scripts/*.py` | 검증기, e북 생성기, 린터, new_run | 아니오 |
| `<스킬>/templates/` | 새 작품용 book-toc·storyline 양식, e북 디자인 | 아니오 |

## 2. 워크플로우

```
00_storyline/storyline.md
  → storyline 단계  → 01_test/<run>/   (스토리 합평, 통과본 storyline.md)
  → research 단계   → 02_draft/<run>/01_research-notes.md
  → write 단계      → 02_draft/<run>/02_outline.md, 03_draft-v1.md
  → review 단계     → 02_draft/<run>/04~13, 09_draft-final.md
  → publish 단계    → 03_output/<run>/ebook.html, metadata.md
```

한 단계가 끝나기 전에 다음 단계를 시작하지 않는다. 모든 단계는 끝날 때 원장(`02_draft/<run>/00_RUN_STATUS.md`)에 `stage: <스킬명> done YYYY-MM-DD` 한 줄을 남긴다.

### run 폴더

- 이름은 `YYYYMMDD_NN` (NN은 01부터 두 자리). `01_test`, `02_draft`, `03_output`이 같은 이름을 쓴다.
- 새 run은 지휘가 `new_run.py`로 연다. 세 폴더, 원장, 블록 스냅샷(`01_test/<run>/book-toc.snapshot.md`, 그 시점 book-toc 사본)을 함께 만든다.
- 스냅샷은 그 run의 숫자 정본이다. 검증기와 린터는 run을 검사할 때 스냅샷을 쓴다. 그래서 다음 작품으로 book-toc를 갈아 끼워도 지난 run 검사는 깨지지 않는다.
- run 진행 중 블록을 고치면(예: storyline 5단계 동기화) 스냅샷도 같이 갱신하고 원장에 남긴다. 단계 작업의 동기화면 `note: block-change <무엇을>`, 사용자 요청이면 `gate: block-change → approved <무엇을> (날짜) "<원문>"`이다. 린터는 진행 중 run의 블록과 스냅샷이 다르면 FAIL을 낸다.
- **끝난 run**은 원장에 `stage: publish done` 또는 `closed:`가 있는 run이다. 검증기·린터·스킬 모두 이 정의 하나를 쓴다.
- 어느 run을 쓸지와 새 run을 여는 법(same/updated/rework 선택)은 SKILL.md "새 run 열기"가 정본이다. `new_run.py`가 원장에 `gate: new-run → <선택> "<원문>"`을 쓴다. rework는 다음과 같이 물려받는다.
  - `rework`: 지난 run의 결과를 물려받아 특정 단계부터 다시 한다(재리뷰 등). 지난 run의 storyline 통과본, 스냅샷, 리서치 노트를 새 run으로 복사하고, 물려받은 원고를 시작 파일로 둔다(재리뷰면 지난 `09_draft-final.md` → 새 `03_draft-v1.md`). 원장에 `inherit: <지난 run>`과 물려받은 단계마다 `stage: <스킬> done <날짜> (inherited)`를 남긴다. 그다음 스킬이 그 단계부터 이어서 시작한다.
- 끝난 run을 다시 열지 않는다. 재작업은 새 run에서 한다. 이전 run을 닫으려면 사용자에게 묻고 `closed: superseded <날짜>`와 `gate: close-run → approved "<응답 원문>"` 두 줄을 남긴다.
- 예외는 출판 뒤 수정(post-audit) 하나다. 끝난 run의 산출물에서 결함이 나오거나 작가가 고쳐 달라고 하면(윤문, 서평 빼기 등) 사용자 승인(`gate: post-audit → approved "<원문>"`)을 받은 뒤에만 고친다. 절차는 SKILL.md "출판 뒤 수정"과 `republish.py` 머리 주석이다: `republish.py --prepare`가 고치기 전 최종본을 `_archive/`에 보관하고, 고친 내용은 `02_draft/<run>/14_post-audit-changelog.md`에 적고, `republish.py --owner <owner>`가 다시 만들기, 메타 분량, 검증, `stage: post-audit-fix done`, 재잠금을 한다. 판을 새로 짜는 재합평이면 rework run을 연다.
- **작가 산출물은 승인 없이 빼거나 옮기지 않는다.** 원고의 문장·섹션(작가의 말, 서평 포함), `03_output`의 산출물(e북, 메타데이터)을 지우거나 `_archive/`로 옮기거나 다른 내용으로 갈아 끼우려면 먼저 사용자에게 묻고 `gate: remove-<대상> → approved "<원문>"`을 남긴다. 결함이 있으면 결함을 보고하고 고칠지 묻는다. 규칙과 어긋나 보여도 작가가 만든 것이면 먼저 묻는다.
- 새 run은 `python3 <스킬>/scripts/new_run.py`로 연다(사용법은 7절). 폴더, 원장, 스냅샷, rework 상속을 한 번에 만든다.
- 각 단계는 시작할 때 "입력: … / 출력: …" 한 줄로 쓸 run을 알린다.

### 이어하기

1순위는 원장의 `stage:`·`reopen:` 줄이다. `reopen:`은 되돌릴 단계를 적는다(`reopen: storyline <사유>`, `reopen: review-9 <사유>`). 린터의 게이트 검사도 단계별로 센다: 스토리 게이트는 마지막 `reopen: storyline` 뒤, 본문 게이트는 마지막 `reopen: review-1`~`review-5` 뒤만 본다. `review-6`~`review-9`로 되돌리는 것(통과 정리, 외부 리뷰, 최종 수정)은 본문 합평 통과를 무르지 않는다. `reopen: <단계> <사유>`가 마지막 `stage:`보다 뒤에 있으면 그 단계부터 다시 한다. 원장에 기록이 없을 때만 파일 존재로 판단한다. 같은 파일을 두 번 쓰지 않는다(예외: `09_draft-final.md`는 6·6P·9단계가 이어 고친다. 앞 판은 각 단계의 버전 파일과 보관본에 남는다). 부분 작성 파일은 마지막 지점부터 이어 붙인다.

## 3. 원장 `00_RUN_STATUS.md`

원장 형식, `gate:`·`waiver:`·`note:`·`closed:` 줄의 뜻, 승인 짝짓기, 게이트가 닫히는 조건, 작가 산출물 제거 승인은 **`<스킬>/references/ledger.md`**에 있다. 이 문서의 "3절"은 그 문서를 가리킨다.

## 4. 합평 공통 규칙

### 4.1 심각도

- 🔴 필수: 고치지 않으면 다음 단계로 못 간다.
- 🟡 권장: BLACK이 판단해 반영한다. 반영하지 않으면 이유를 한 줄 남긴다.
- 🟢 참고: 무시해도 된다.

### 4.2 점수 동결 (의례 방지)

채점하는 합평 파일(스토리 `00b~`, 본문 `06`, `08`, `08_ensemble-<k>`, 장편 부 단위 합평)은 머리에 아래 줄들을 둔다. 린터가 이 줄로 모든 라운드를 검사한다. 한 번만 하는 리뷰(PINK `04`, IVORY `10`, ORANGE `11`, OLIVE `12`)는 라운드가 아니라서 동결 대상이 아니다. 이 파일들은 `입력`과 `입력 sha256` 두 줄만 둔다.

```
입력: <같은 폴더 안의 입력 파일명>
입력 sha256: <64자리 해시>          (shasum -a 256 <입력>)
판정 점수: X.XX                    (스토리는 패널 점수, 본문은 4인 평균)
남은 🔴: N
판정: 통과 | 재수정 | 동결
BURGUNDY: X.XX                       (스토리 합평이고 패널에 BURGUNDY가 있을 때만)
```

린터는 `판정: 통과`인 파일의 점수를 run 스냅샷의 통과선(`review.story_pass`, `review.body_pass`, `review.story_critic_min`)과 비교하고 `남은 🔴: 0`을 확인한다. 미달이면 승인된 `open_red` waiver가 있을 때만 통과로 인정한다.

- 입력은 이후 고치지 않는 버전 파일이어야 한다(스토리 `storyline_v<N>.md`, 본문 `05_draft-v2.md` 등). 채점 뒤 입력이 바뀌면 린터가 무결성 FAIL을 낸다.
- 입력 해시가 같은 계열의 **앞선 어느 라운드**와 같으면 채점하지 않는다. `판정: 동결`과 `점수 동결: 입력 해시가 <파일> 라운드와 같다`를 쓰고, 그 라운드의 점수를 그대로 옮기며, 원장에 `freeze:` 줄을 남긴다. 계열의 첫 합평(스토리 1라운드, 본문 1라운드)은 옮길 점수가 없으므로 동결하지 않고 채점한다.
- 입력이 직전과 거의 같은데(유사도 99% 이상) 점수가 크게 오르면 린터가 WARN을 낸다. 한두 글자 수정으로 동결을 피하는 것을 사람이 보게 하기 위해서다.
- 다르면 2라운드부터는 `## 바뀐 자리` 섹션(장·단락·한 줄 요약)을 먼저 적는다. 섹션이 없으면 린터가 FAIL을 낸다. 평가자는 점수를 올릴 때 반드시 바뀐 자리 하나 이상을 근거로 인용한다. 근거 없는 상향("재독 후 익숙해짐" 등)은 금지한다.

### 4.3 스토리 합평 점수 (storyline 단계)

1. 카드 점수 = 그 카드의 5축 점수를 카드별 축 가중치(`reviewers.md`)로 가중 평균한 값.
2. 패널 점수 = Σ(w × 카드 점수) / Σw. w는 모두 1, OLIVE만 `review.story_proof_weight`.
3. BLACK은 패널에 넣지 않는다. 00a 자기 검토 점수는 따로 보고한다.
4. 통과 조건은 셋을 모두 만족할 때다.
   - 패널 점수 ≥ `review.story_pass`
   - BURGUNDY가 패널에 있으면 BURGUNDY 카드 점수 ≥ `review.story_critic_min`
   - 남은 🔴 0건
5. 패널 구성은 블록의 `review.story_panel`로 정한다.

| story_panel | 패널 카드 |
|---|---|
| lite | PINK, RED, SILVER, BLUE, GOLD, IVORY, ORANGE, OLIVE |
| standard | lite + TEAL, BROWN, INDIGO, BURGUNDY |
| extended | standard + 사용자 지정 게스트 (게스트 카드 점수도 `review.story_critic_min` 이상) |

통과선은 패널 구성과 무관하게 같다.

### 4.4 본문 합평 점수 (review 단계)

- 패널: RED, SILVER, BLUE, GOLD. 각 카드는 `reviewers.md` 본문 모드 루브릭으로 10점에서 감점한다.
- 라운드마다 합평 전에 처음 읽는 독자 점검(`reader-check.md`)을 한다. 그 🔴는 합평 파일의 `남은 🔴`에 더한다.
- 통과 조건: 4인 단순 평균 ≥ `review.body_pass` 그리고 🔴 0건(reader-check 🔴 포함).
- 통과 뒤 외부 리뷰 전에 PURPLE 루프(`purple-loop.md`)를 돈다. 합평 점수와 섞지 않는다. PURPLE 카드 합격선과 마지막 독자 점검 🔴 0, 또는 승인된 `purple_open` waiver가 있어야 7단계로 간다.

### 4.5 라운드 상한과 사용자 확인

- 라운드 번호는 제한 없이 이어 간다. 덮어쓰지 않는다.
- `review.rounds_before_user_check` 라운드를 넘기기 전에 반드시 사용자에게 묻고 원장에 `gate:`를 남긴다.
- 통과해도 storyline 단계는 사용자 a/b 게이트를 거친다(stage-storyline.md 5단계).

## 5. 산출물 번호

### 01_test/<run>/

| 파일 | 내용 |
|---|---|
| `00a_story-self.md` | BLACK 자기 검토 |
| `00b_story-ensemble-1.md` | 합평 1라운드 |
| `00c_story-ensemble-2.md`, `00d…`, `00e…` | 2라운드부터 알파벳을 이어 간다 |
| `storyline_v<N>.md` | 수정 직전 버전 백업 |
| `storyline.md` | 통과본 |

### 02_draft/<run>/

| 파일 | 단계 | 내용 |
|---|---|---|
| `00_RUN_STATUS.md` | 전 단계 | 원장 |
| `01_research-notes.md` | research 단계 | 사실·세계관 자료 |
| `02_outline.md` | write 단계 | 장면 설계서 |
| `03_draft-v1.md` | write 단계 | 초안 |
| `04_review-pink.md` | review 단계 1 | PINK 첫인상 |
| `05_draft-v2.md` | review 단계 2 | PINK 반영본 |
| `06_reader-check-1.md` | review 단계 3 | 처음 읽는 독자 점검 1라운드(합평 전, 재독 로그) |
| `06_ensemble-1.md` | review 단계 3 | 합평 1라운드 |
| `07_draft-v3.md` | review 단계 4 | 합평 1 반영본 |
| `08_ensemble-2.md` | review 단계 5 | 합평 2라운드 |
| `07_draft-v<k+2>.md` | review 단계 | 라운드 k(≥2) 미통과 후 BLACK 반영본. 라운드 k+1의 입력 (덮어쓰지 않음) |
| `08_ensemble-<k>.md` | review 단계 | k≥3 라운드 합평. 입력은 `07_draft-v<k+1>.md` |
| `08_reader-check-<k>.md` | review 단계 | 라운드 k(≥2)의 독자 점검. 입력은 그 라운드 합평과 같다 |
| `09_draft-final.md` | review 단계 6·9 | 합평 통과본. 9단계 직전 버전은 `09_draft-final_pre9.md`로 남긴다 |
| `10_review-editor.md` | review 단계 7 | IVORY |
| `11_review-marketer.md` | review 단계 8 | ORANGE (본문 미반영, publish 입력) |
| `12_review-proofreader.md` | review 단계 8 | OLIVE |
| `13_purple-<k>.md`, `13_purple-resolve-<k>.md`, `13_draft-purple-v<k>.md`, `13_reader-check-<k>.md` | review 단계 6P, 출판 뒤 수정 | PURPLE 루프(purple-loop.md 3절). v0은 루프 입력 사본 |

라운드 k의 입력 버전은 항상 v<k+1>이다: 1라운드 v2, 2라운드 v3, 3라운드 v4.

### 03_output/<run>/

`ebook.html`(웹 e북, 유일한 출판 형식), `metadata.md`, `validate_report.txt`. 블록 `publish.formats`는 `["ebook"]`이다(예전 작품의 `docx`는 출판 뒤 수정으로 빼고 보관함으로 옮긴다). 스크립트는 run 폴더에 복사하지 않고 `<스킬>/scripts/`의 범용본을 실행한다. e북 디자인을 고르고 두는 곳은 book-toc 템플릿 필드 표(`publish.ebook.design`)가 정본이다.

### 장편 (`structure_mode: "part"`)

블록의 `structure_mode`가 `"part"`이면 장편이다. 이때 `parts` 배열(`{"no", "title", "chapters": [장 번호]}`)이 모든 장을 한 번씩 담아야 한다(린터 L2). 매수로 판정하지 않는다. 원고에서 부 헤딩은 `# <no>부. <title>`이다. 부 단위 파일은 단편 파일 이름 뒤에 `-part<n>`을 붙인다: 초안 `03_draft-v1-part<n>.md`, 반영본 `05_draft-v2-part<n>.md`·`07_draft-v<k>-part<n>.md`, 합평 `06_ensemble-1-part<n>.md`·`08_ensemble-<k>-part<n>.md`. 전체 통합 합평은 `-overall`(`06_ensemble-1-overall.md`), 통합본은 `09_draft-final-merged.md`다. 린터는 `-part<n>`, `-overall`마다 별도 계열로 동결을 검사한다. 외부 리뷰(10~12)는 통합본으로 한 번 한다.

## 6. 본문 범용 규칙

1. 본문은 book-toc의 BLACK 페르소나와 문체 9원칙으로 쓴다.
2. 최종 산출물에 내부 역할명(BLACK, RED 등)이 나오지 않는다. 작성자 표기는 블록의 `pen_name`.
3. 인물·세계관·사실의 1차 소스는 통과본 `01_test/<run>/storyline.md`. 어긋나면 🔴.
4. 장 헤딩은 `# <no>장. <title>` 형식, 블록의 `chapters`와 정확히 일치.
5. book-toc의 "명시 금지 항목"은 어떤 단계에서도 풀어 쓰지 않는다.
6. 이름 짓기 원칙(book-toc)을 지킨다. 로봇·시스템에 사람 이름 금지.
7. em dash(—, –), 불릿, `**`, 번역투, 클리셰 0건.
8. 위트는 블록의 `wit` 범위와 출처, `zero_zones` 0회.
9. 마지막 장 뒤의 섹션(작가의 말, 서평 등)은 블록 `back_matter`에 이름이 있을 때만, 마지막 장 뒤에 둔다. 작가 이름으로 나가는 글(작가의 말, 감사의 말, 헌사)은 작가가 준 원문, 작가가 명시 승인한 초안, 작가가 BLACK에게 쓰라고 명시 요청한 글만 넣는다. 어느 쪽이든 원장에 `gate: author-text-<섹션> → approved "<원문>"`이 있어야 한다. 요청 없이 AI가 지어 넣지 않는다. BLACK이 쓸 때의 규칙은 stage-write.md 3절이다.
10. 정본에 없는 실명을 만들지 않는다. 제3자 글(서평, 추천사, 해설)은 실제 글이면 블록 `publish.third_party_verified: true`, 작가가 쓴 가상 평자의 글이면 원장에 `waiver: fictional_reviewer`와 `gate: waiver-fictional_reviewer → approved "<원문>"`이 있어야 한다. 린터가 검사한다.

## 7. 도구

| 명령 | 용도 | 언제 |
|---|---|---|
| `python3 <스킬>/scripts/validate_draft.py --run <run>` | 원고·e북 품질 게이트 | write 단계 완료, review 9단계 후, publish 0·1단계 |
| `python3 <스킬>/scripts/init_project.py --answers <답 JSON>` | 첫 작품의 book-toc.md와 storyline.md를 한 번에 만든다 | 처음 한 번 |
| `python3 <스킬>/scripts/new_run.py --mode same\|updated\|rework --answer "<원문>" [--from <run> --stage <단계>]` | 새 run 열기(폴더, 원장, 스냅샷, rework 상속, 잠금) | storyline 단계 시작, 재작업 |
| `python3 <스킬>/scripts/republish.py --run <run> --prepare` / `--owner <owner>` | 출판 뒤 수정: `--prepare`는 고치기 전 보관과 owner 발급, `--owner`는 다시 만들기·메타 분량·검증·재잠금 | post-audit 승인 뒤, 고치기 전과 후 |
| `python3 <스킬>/scripts/lock_run.py --run <run>` | 원장에 잠금 줄을 남긴다(ledger.md "잠금") | 출판을 마칠 때, 승인받은 블록 변경 뒤 |
| `python3 <스킬>/scripts/generate_ebook.py --run <run>` | 웹 e북 생성 | publish 1단계 |
| `python3 <스킬>/scripts/lint_project.py` | 문서 정합성, 폴더 규칙, 점수 동결·게이트 로그 감사 | 스킬·book-toc 수정 후, 각 단계 종료 시 |
| `bash tools/tests/selftest.sh` (이 스킬의 원본 저장소에서) | 다른 장르 픽스처로 범용성 회귀 시험 | 스크립트 수정 후 |

### 도구가 보장하지 못하는 것

린터와 검증기는 **기록끼리 맞는지**를 검사한다. 기록이 **사실인지**는 보장하지 못한다.

- 합평 점수, 🔴 개수, 판정 줄은 평가 내용에서 나온 값이다. 린터는 그 값이 통과선과 맞는지만 본다. 점수 자체가 타당한지는 사람이 합평 본문을 읽고 판단한다.
- `gate:` 줄의 응답 원문은 에이전트가 적는다. 사용자는 원장을 열어 자기 답과 같은지 확인할 수 있다.
- 해시는 누구나 다시 계산할 수 있다: `shasum -a 256 <입력 파일>`. 머리 줄의 해시와 다르면 그 합평은 믿지 않는다.
- 주술 호응, 위트, 감정 노출, 마지막 줄의 결, 처음 읽는 독자가 멈추는 자리는 검증기의 MANUAL 항목이다. 사람(또는 reader-check)이 읽어야 한다.

## 8. 문서 크기 상한

린터가 검사하는 상한은 CLAUDE.md 6KB, AGENTS.md 20KB, SKILL.md 본문 500줄이다. workflow.md·ledger.md는 각 20KB 안으로 지휘가 관리한다(린터 밖). 넘으면 `references/`로 나눈다.
