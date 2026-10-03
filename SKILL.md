---
name: novel-writing
description: "AI 에이전트 팀으로 소설을 설계·집필·합평해 웹 e북(ebook.html)으로 출판하는 워크플로우. 다섯 단계(storyline 스토리 합평, research 자료 조사, write 장면 설계와 초안, review 합평과 수정, publish 품질 게이트와 출판)를 서브 에이전트에 맡기고, 사용자 확인 게이트는 직접 받아 원장에 기록한다. 사용자가 '소설 쓰자', '스토리 합평', '스토리 다듬자', '리서치', '자료 조사', '초안 쓰자', '리뷰', '합평', '이북 만들자', '출판', '/novel-writing'이라고 하거나, 프로젝트에 book-toc.md와 00_storyline/storyline.md가 있을 때 쓴다."
---

# novel-writing

작가 페르소나 BLACK과 평가자 카드 13장이 소설을 설계, 집필, 합평해 웹 e북(`ebook.html`)으로 출판한다. Word(docx)는 만들지 않는다. 이 파일은 **지휘**만 한다. 단계 작업은 서브 에이전트(또는 단계 문서)가 하고, 사용자에게 묻는 일은 여기서 한다.

## 경로 규칙

- `<스킬>`: 이 `SKILL.md`가 있는 폴더. 스크립트·단계 문서·템플릿은 모두 여기 있다.
- **프로젝트 폴더**: 작품 파일이 있는 폴더. `book-toc.md`가 있는 곳이다. 스크립트는 현재 폴더에서 위로 올라가며 `book-toc.md`를 찾는다. 다른 곳에서 실행하면 `--root <프로젝트 폴더>`를 준다.
- **폴더 이름은 영문만 쓴다.** 새로 만드는 폴더(작품 폴더, run, 보관 폴더 등)는 영문 소문자·숫자·하이픈·밑줄로만 짓고 한글을 쓰지 않는다. 새 작품 폴더는 `projects/<영문-슬러그>/`로 만든다(예시: `projects/care-robot-unit-1/`). 제목이 한글이면 뜻을 옮긴 영문 슬러그를 사용자에게 제안해 확인받는다.
- 프로젝트 안의 경로(`book-toc.md`, `00_storyline/`, `01_test/<run>/`, `02_draft/<run>/`, `03_output/<run>/`)는 모두 프로젝트 폴더 기준이다.

## 처음 한 번

필요 환경: python3 3.9 이상. 표준 라이브러리만 쓰므로 따로 설치할 패키지가 없다.

1. 프로젝트 폴더에 `book-toc.md`와 `00_storyline/storyline.md`가 없으면(첫 작품) 사용자에게 **한 번에** 묻는다: 제목, 필명, 장르, 표지 장르 표기, 대상 독자, 화자 이름과 인칭, 본문에 반드시 나올 이름·호칭, 장 제목과 장별 매수, 마지막 한 줄. 선택으로 흡수한 작가, 인물 한 줄 요약, 본문에 풀지 않을 사실, 마지막 장 뒤에 둘 섹션(작가의 말 등)도 받는다. 답을 JSON 파일로 적고 `python3 <스킬>/scripts/init_project.py --answers <파일>`을 돌리면 두 파일이 함께 생긴다(형식은 스크립트 머리 주석). 이미 있는 파일은 덮어쓰지 않는다. 출판 정보(`publish.*` 빈칸)는 publish 단계에서 묻는다(그 전까지 린터 WARN). storyline.md의 남은 빈칸(줄거리, 인물, 장별 사건)은 작가가 쓴다. 작가가 원하면 지휘가 빈칸을 섹션별 질문으로 받아 응답 원문 그대로 채운다(지휘가 지어 넣지 않는다).
2. `python3 <스킬>/scripts/lint_project.py`를 돌린다. FAIL이 있으면 메시지(파일:줄, 고칠 방법)를 사용자에게 보여 주고 멈춘다.
3. 공통 규약 `<스킬>/references/workflow.md`와 원장 규칙 `<스킬>/references/ledger.md`를 읽는다. 원장, 게이트, 점수 동결, waiver, 잠금(`lock:` 줄) 규칙이 여기 있다.

## 어느 단계인가

사용자가 단계를 말하면 그 단계로 간다. 말하지 않았으면 끝나지 않은 가장 최근 run의 원장(`02_draft/<run>/00_RUN_STATUS.md`)을 읽고 정한다.

| 원장 상태 | 다음 단계 |
|---|---|
| run 없음, 또는 모든 run이 끝남 | 새 run을 연다 (아래 "새 run 열기") |
| `stage: storyline done` 없음, 또는 그 뒤에 `reopen: storyline` | storyline |
| `stage: research done` 없음 | research |
| `stage: write done` 없음 | write |
| `stage: review done` 없음, 또는 `reopen: review-…` | review |
| `stage: publish done` 없음 | publish |
| 끝난 run에 대한 수정 요청(윤문, 서평 빼기, 판권 고치기) | 출판 뒤 수정 (아래) |
| `republish.py --status`가 진행 중인 수정을 알림 | 출판 뒤 수정 0단계 (기다림·이어받기·버리기) |

## 새 run 열기 (지휘가 직접 한다)

끝나지 않은 run이 없을 때 연다. 지난 run이 하나도 없는 첫 작품이면 묻지 않고 `--mode same --answer "첫 run"`으로 연다. 지난 run이 있으면 사용자에게 한 번 묻는다.

- (same) 같은 storyline으로 처음부터
- (updated) `00_storyline/storyline.md`를 고친 뒤 처음부터
- (rework) 끝난 run을 물려받아 특정 단계부터 다시 (예: 재합평이면 review부터). 출판 뒤 고친 기록이 있으면 같은 질문에서 보호 범위도 묻는다: 출판 뒤 수정 절차로 고친 문단만(recent, 기본) / 그 전 원고 교체·윤문까지 전부(all) / 보호하지 않음(none). `new_run.py --protect`로 넘긴다

응답을 받으면 지휘가 스크립트로 run을 연다. 스크립트가 원장에 `gate: new-run → <선택> "<응답 원문>"`을 직접 쓰므로 따로 적지 않는다.

```
python3 <스킬>/scripts/new_run.py --mode same|updated --answer "<응답 원문>"
python3 <스킬>/scripts/new_run.py --mode rework --from <끝난 run> --stage research|write|review --answer "<응답 원문>"
```

rework는 물려받을 run의 스토리 게이트가 닫혀 있어야 열린다. 그다음 해당 단계의 서브 에이전트를 부른다.

## 단계 실행

| 단계 | 서브 에이전트 | 단계 문서 |
|---|---|---|
| storyline | `novel-writing-storyline` | `references/stage-storyline.md` |
| research | `novel-writing-research` | `references/stage-research.md` |
| write | `novel-writing-write` | `references/stage-write.md` |
| review | `novel-writing-review` | `references/stage-review.md` |
| publish | `novel-writing-publish` | `references/stage-publish.md` |

- **서브 에이전트를 쓸 수 있는 환경(Claude Code)**: 해당 서브 에이전트에게 맡긴다. 프롬프트에 프로젝트 폴더, run 이름, 이번 호출의 목적, 지금까지 받은 사용자 응답 원문을 넣는다.
- **서브 에이전트가 없는 환경(Codex 등)**: 단계 문서를 직접 읽고 그대로 수행한다. 아래 게이트 규칙은 같다.

서브 에이전트는 사용자와 대화할 수 없다. 사용자 확인이 필요한 지점에서 작업을 멈추고 아래 형식으로 돌아온다.

```
상태: done | need_user | blocked
질문 id: <게이트 id, 예: storyline-pass>
질문: <사용자에게 보여 줄 보고와 선택지>
산출물: <새로 쓰거나 고친 파일 목록>
다음: <다음 단계 또는 다시 부를 때 할 일>
```

## 사용자 게이트 (지휘가 직접 한다)

1. 서브 에이전트가 `need_user`로 돌아오면, 질문을 사용자에게 그대로 보여 주고 응답을 기다린다. 응답 전에는 진행하지 않는다.
2. 응답을 원장에 원문 그대로 남긴다: `gate: <질문 id> → <선택> (날짜) "<응답 원문>"`. 승인 성격의 응답이면 `→ approved`를 쓴다(린터는 `approved`·`verified`만 승인으로 센다). 거절이면 `→ rejected`로 남기고 진행하지 않는다.
   - waiver가 필요한 선택(라운드 상한에서 진행, 가상 평자 서평 유지 등)이면 **먼저** `waiver: <id> <대상 파일명> <사유>`를 쓰고 **그 아래에** `gate: waiver-<id> → approved (날짜) "<응답 원문>"`을 쓴다. 승인 줄은 바로 위의 waiver 하나만 승인한다.
3. 같은 서브 에이전트를 다시 부르면서 응답 원문을 넘긴다.

매번 묻는 게이트는 셋이다: `new-run`(지난 run이 있을 때 새 run을 열면서), `storyline-pass`(스토리 통과 후 a/b), `write-mode`(장마다 확인할지). publish 단계의 질문(`publish-info`, `epigraph-source`)은 한 번에 묶어 묻고, 같은 응답 원문으로 gate 줄을 따로 남긴다. 그 밖의 게이트(`publish-info` 출판 정보 빈칸, `epigraph-source` 출처 미확인 제사, 라운드 상한, autofix, waiver, 작가 산출물 제거 `remove-<대상>`)는 조건이 맞을 때만 묻는다.

**작가 산출물은 승인 없이 빼거나 옮기지 않는다.** 원고 문장·섹션, e북, 메타데이터를 지우거나 옮기거나 갈아 끼우려면 먼저 묻고 `gate: remove-<대상> → approved "<원문>"`을 남긴다.

## 출판 뒤 수정 (지휘가 직접 한다)

**한 run은 한 번에 한 세션만 고친다.** 출판 뒤 수정은 `--prepare`가 발급한 owner를 가진 세션만 마칠 수 있고, 진행 중에는 잠금(`lock_run.py`)과 rework가 열리지 않는다.

끝난 run을 고쳐 달라는 요청은 새 run이 아니라 이 절차로 한다. 원고를 다시 합평해야 할 만큼 크면 rework run을 연다.

0. **묻기 전에** `python3 <스킬>/scripts/republish.py --run <run> --status`로 진행 중인 수정이 있는지 본다(rework를 열 때도 같다). 있으면 새 수정을 묻지 않는다. 그 수정을 시작한 세션이 살아 있으면 기다린다. 끊겼으면 `--status`가 보여 주는 요청 원문·시작 시각·원고와 산출물이 바뀌었는지를 함께 보여 주며 작가에게 한 번 묻는다: (a) 기다린다 (b) 이어받는다 (c) 버린다. 새로 받은 요청(예: 서평 빼기)이 있으면 같은 질문에 함께 묻고, 한 응답 원문으로 gate 줄을 각각 남긴다. (a)는 `gate: post-audit-wait → wait …`, 그 밖은 응답 원문을 `gate: post-audit-takeover → approved …` 또는 `gate: post-audit-abandon → approved …`로 남기고 `republish.py --takeover`(새 owner 발급, 원고 수정과 변경 기록을 마친 뒤 그 owner로 마침) 또는 `--abandon`(원고를 수정 전 보관본으로 되돌리고 `stage: post-audit-fix abandoned`)을 돌린다. owner는 실수로 겹치는 것을 막는 표시이고 비밀이 아니다.
1. 무엇을 어떻게 바꿀지 한 번에 보여 주고 묻는다. 승인이면 같은 응답 원문으로 `gate: post-audit → approved (날짜) "<원문>"`을 남기고, 빼는 것이 있으면 `gate: remove-<대상> → approved …`, 블록 값을 바꾸면 `gate: block-change → approved <키> …`도 남긴다.
2. 고치기 전: `python3 <스킬>/scripts/republish.py --run <run> --prepare`. 09 최종본을 `_archive/<시각>_post-audit_<owner>/`에 보관하고 MANIFEST에 적고, `02_draft/<run>/14_post-audit-changelog.md`를 준비하고, 이 수정의 **owner**를 발급한다. 다른 수정이 진행 중이면 멈춘다(다른 세션이 같은 run을 고치는 중이다. 끝날 때까지 기다리고, 그동안 새 승인을 받지 않는다).
3. 원고·블록·스냅샷을 고치고 `02_draft/<run>/14_post-audit-changelog.md`에 날짜, 승인 원문, 바꾼 자리, 전과 후를 적는다.
4. 고친 뒤: `python3 <스킬>/scripts/republish.py --run <run> --owner <owner>`. 산출물 보관, e북 다시 만들기, 메타 분량, 검증, 원장 기록, 재잠금을 한다. 승인, prepare, 변경 기록 중 하나라도 빠졌으면 아무것도 바꾸지 않고 멈춘다.
5. 린터 FAIL 0을 확인하고 바뀐 자리를 한 단락으로 알린다. 같은 날 여러 번 고치면 1~5를 수정마다 반복한다(재잠금 뒤에는 새 승인이 필요하다).

## 단계를 마칠 때

1. `python3 <스킬>/scripts/lint_project.py`가 FAIL 0인지 본다.
2. 원고가 있는 단계면 `python3 <스킬>/scripts/validate_draft.py --run <run>`이 FAIL 0인지 본다.
3. 사용자에게 한 단락으로 알린다: 끝낸 단계, 만든 파일, 다음 단계, 남은 WARN.

## 도구가 보장하지 못하는 것

린터와 검증기는 기록끼리 맞는지를 검사한다. 합평 점수가 타당한지, 원장의 응답 원문이 실제 응답인지는 사람이 확인한다(`references/workflow.md` 7절).
