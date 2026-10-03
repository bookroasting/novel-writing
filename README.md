# novel-writing

AI 에이전트 팀이 소설을 설계, 집필, 합평해 출판본(웹 e북, docx)까지 만드는 Agent Skill이다. 작가 페르소나 BLACK이 쓰고, 평가자 카드 13장이 합평한다. 사용자에게 물어야 하는 자리(게이트)는 지휘 에이전트가 직접 묻고, 답을 원장에 원문 그대로 남긴다.

Claude Code와 Codex에 설치할 수 있다.

## 무엇이 들어 있나

```
SKILL.md          지휘: 단계 고르기, 서브 에이전트에 맡기기, 사용자에게 묻기
agents/           단계별 서브 에이전트 5개 (storyline, research, write, review, publish)
references/       공통 규약(workflow.md), 원장 규칙(ledger.md), 평가자 카드(reviewers.md), 단계 절차(stage-*.md)
scripts/          검증기, e북·docx 생성기, 린터, run 열기, 잠금, 출판 뒤 수정, 첫 작품 시작
templates/        book-toc·storyline 양식, e북 기본 디자인
tools/            설치 스크립트, 자가 시험
examples/         예시 작품과 출판본
```

## 설치

```bash
python3 -m pip install -r requirements.txt
python3 tools/install_skill.py --target claude-user        # ~/.claude/skills, ~/.claude/agents (모든 프로젝트)
python3 tools/install_skill.py --target claude-project --project ~/novels/my-book   # 한 작품 폴더에만
python3 tools/install_skill.py --target codex              # ~/.codex/skills
python3 tools/install_skill.py --target zip                # dist/novel-writing.zip (Claude 앱 업로드용)
```

설치는 `SKILL.md`, `agents`, `references`, `scripts`, `templates`, `requirements.txt`만 복사한다. Claude Code 대상이면 서브 에이전트를 agents 폴더에도 넣는다. Codex에는 서브 에이전트 형식이 없어서 지휘가 단계 문서를 직접 읽는다.

## 첫 작품 시작

1. 작품 폴더를 만들고 그 폴더에서 Claude Code(또는 Codex)를 연다.
2. "소설 쓰자"라고 말한다. 지휘가 제목, 필명, 장르, 화자, 장 구성, 마지막 한 줄 같은 첫 질문을 한 번에 묻고 `book-toc.md`와 `00_user_input/storyline.md`를 만든다(`scripts/init_project.py`).
3. storyline의 남은 빈칸(줄거리, 인물, 장별 사건)을 채운다. 어렵다면 "빈칸 같이 채우자"라고 한다.
4. 이후 "스토리 합평하자", "초안 쓰자", "이북 만들자"처럼 말하면 지휘가 원장을 보고 다음 단계를 고른다.

작품 폴더 구조:

```
book-toc.md                 작품 파라미터 블록 (숫자·이름·통과선의 정본)
00_user_input/storyline.md  작가가 쓴 1차 콘셉트
01_test/<run>/              스토리 합평과 통과본, 블록 스냅샷, 잠금 파일
02_draft/<run>/             리서치, 초안, 합평, 최종본(09), 원장(00_RUN_STATUS.md)
03_output/<run>/            출판본과 메타데이터
```

## 단계

| 단계 | 하는 일 |
|---|---|
| storyline | 평가자 패널이 storyline을 합평해 통과본을 만든다 |
| research | 본문에 필요한 사실·세계관 자료를 모은다 |
| write | 장면 설계와 장 단위 초안을 BLACK 페르소나로 쓴다 |
| review | 첫인상, 4인 합평, 외부 리뷰, 최종 수정으로 다듬는다. 원고가 바뀌지 않으면 채점하지 않는다 |
| publish | 품질 게이트를 통과한 최종본으로 출판본과 메타데이터를 만들고 잠근다 |

출판한 뒤에 고칠 때는 새 run이 아니라 출판 뒤 수정 절차를 쓴다: 작가 승인 → `scripts/republish.py --prepare`(보관, owner 발급) → 고치기와 변경 기록 → `scripts/republish.py --owner <owner>`(다시 만들기, 검증, 재잠금).

## 용어

| 용어 | 뜻 |
|---|---|
| 지휘 | `SKILL.md`를 읽고 단계를 고르고 사용자에게 묻는 에이전트(대화 중인 Claude·Codex). 단계 작업은 서브 에이전트에 맡긴다 |
| BLACK | 작품을 쓰는 작가 페르소나. `book-toc.md`의 "페르소나" 절에 정의한다 |
| 평가자 카드 | 합평에 들어가는 평자 13장(PINK, RED, SILVER, BLUE, GOLD, EDITOR, MARKETER, PROOF, 동료 작가 3장, CRITIC). `references/reviewers.md` |
| 블록 | `book-toc.md` 안의 JSON. 숫자·이름·통과선의 유일한 정본 |
| run | 한 번의 워크플로우 실행. `YYYYMMDD_NN` 폴더가 `01_test`, `02_draft`, `03_output`에 하나씩 생긴다 |
| 원장 | `02_draft/<run>/00_RUN_STATUS.md`. 단계 완료(`stage:`), 사용자 선택(`gate:`), 예외 기록(`waiver:`), 잠금(`lock:`)을 남긴다 |
| 게이트 | 사용자에게 묻고 답을 받아야 넘어가는 자리. 답은 원장에 `gate: <질문 id> → <선택> "<응답 원문>"`으로 남는다 |
| waiver | 규칙 위반을 숨기지 않고 기록하는 줄. 사용자 승인 줄이 짝으로 있어야 인정된다 |
| 잠금 | 원장의 `lock:` 줄. 그 시점의 블록·산출물 목록·원고·출판본 해시를 적어 둔다. 이후 승인 없이 바뀌면 린터가 FAIL을 낸다 |
| 출판 뒤 수정 | 출판한 run을 작가 요청으로 고치는 절차. 한 run은 한 번에 한 세션만 고친다 |
| owner | 출판 뒤 수정 하나를 시작한 쪽의 표시. `--prepare`가 발급하고 같은 owner로만 마친다. 비밀번호가 아니다 |
| rework | 끝난 run을 물려받아 특정 단계부터 다시 하는 새 run |
| 시각 닻 | 작품에서 반복해 돌아오는 장면·사물. 블록 `anchors`에 장 배치와 최소 횟수를 적고 검증기가 센다 |
| 점수 동결 | 합평 입력 원고가 앞선 라운드와 같으면 채점하지 않고 그 점수를 그대로 둔다 |

## 검사 도구

```bash
python3 scripts/lint_project.py --root <작품 폴더>      # 문서·블록·폴더·run 감사 (L1~L8)
python3 scripts/validate_draft.py --run <run> --root <작품 폴더>   # 원고·출판본 품질 게이트
bash tools/tests/selftest.sh                           # 스킬 회귀 시험 (examples/kimjang-day를 작품으로 쓴다)
```

린터 코드: L1 스킬 구조·설치, L2 작품 블록·양식 빈칸, L3 지난 작품 흔적, L4 숫자 중복, L5 블록과 스냅샷·storyline 일치, L6 폴더 규칙, L7 문서 크기, L8 run 감사(합평 기록, 게이트, 잠금, 출판본).

도구는 기록끼리 맞는지를 검사한다. 합평 점수가 타당한지, 원장의 응답 원문이 실제 응답인지는 사람이 확인한다.

## 예시

- `examples/care-robot-unit-1/ebook.html`: 이 스킬로 쓰고 출판한 단편 『돌봄로봇 1호기』(Care Robot Unit 1)의 웹 e북. 브라우저로 바로 열린다.
- `examples/kimjang-day/`: 3장짜리 가족 드라마 예시 작품 폴더. 첫 run부터 출판, 출판 뒤 수정 한 번까지의 원장과 산출물이 들어 있다. 자가 시험이 이 폴더를 쓴다.
