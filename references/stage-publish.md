# publish 단계, 품질 게이트와 출판

> **묻기와 기록.** 이 문서에서 사용자에게 묻는 자리와 원장에 `gate:`·`waiver:` 줄을 남기는 일은 지휘(`<스킬>/SKILL.md`)가 한다. 서브 에이전트로 실행 중이면 그 자리에서 작업을 저장하고 `need_user`로 돌아간다. 서브 에이전트 없이(Codex 등) 이 문서를 직접 수행할 때는 직접 묻고 기록한다. `stage:`·`note:` 줄은 단계를 수행한 쪽이 쓴다.

네 단계다. 0단계 게이트를 통과해야 다음 단계가 시작된다. 스크립트는 run 폴더에 복사하지 않고 `<스킬>/scripts/`의 범용본을 실행한다. 모든 값은 그 run의 블록 스냅샷(`01_test/<run>/book-toc.snapshot.md`)에서 읽는다. 스크립트에 `--run <run>`을 주면 스냅샷과 최종본 파일 이름(단편 `09_draft-final.md`, 장편 `09_draft-final-merged.md`)을 알아서 고른다.

## 준비

1. 원장에 `stage: review done`이 있는지 확인한다. 없으면 review 단계를 안내하고 종료한다.
2. 블록의 `title`, `pen_name`, `genre_label`, `chapters`, `back_matter`, `publish`(특히 `formats`), 통과본 storyline, `11_review-marketer.md`를 읽는다.
3. 한 줄로 알린다: `입력: 02_draft/<run>/<최종본> / 출력: 03_output/<run>/ / 형식: <formats>`.

## 출판 정보 확인 (게이트 `publish-info`)

publish를 시작하면 사용자 확인이 필요한 것을 **한 번에 모아** 묻는다(`need_user`, 질문 id `publish-info`): 판형(`trim_options` 중 하나), 블록 `publish.*` 빈칸(발행 연월, 뒤표지 소개, 소개문 등), 출처 미확인 제사가 있으면 그 처리(아래 "제사 출처"). 지휘는 같은 응답 원문으로 `gate: trim → <판형>`, `gate: publish-info → approved`, `gate: epigraph-source → verified|approved|removed`를 각각 남긴다. 빈칸이 없으면 판형(과 제사)만 묻는다. 지휘가 응답 원문을 원장에 `gate: publish-info → approved "<원문>"`으로 남기면, 블록과 run 스냅샷에 같은 값을 넣고 원장에 `note: block-change publish-info`를 남긴다. 린터는 `stage: review done` 이후 `publish.*` 빈칸을 FAIL로 본다.

## 0단계, 품질 게이트

```
python3 <스킬>/scripts/validate_draft.py --run <run> > 03_output/<run>/validate_report.txt
```

검사 항목(기준값은 모두 블록):

| 구분 | 항목 |
|---|---|
| FAIL | 부·장 헤딩 전부·순서, `back_matter` 밖의 장 밖 섹션, 분량(`length`), 마지막 줄(`last_line`), 시각 닻 총량, `**`, 불릿, em dash, 번역투, 클리셰, 명시 금지 키워드, 인물 누락, 폐기된 이름, 1인칭 시점 위반 |
| WARN | 시각 닻 장 분포, 장별 분량 편차 ±20% 초과, 서술문 평균 길이, 출처 미확인 제사 |
| MANUAL | 주술 호응, 위트 횟수·출처, 감정 직접 노출, 장 마지막 줄의 동작·사물 닫힘 |

- FAIL 0 → 1단계.
- 기계 치환이 안전한 FAIL(`**`, 불릿, em dash)은 사용자에게 목록을 보여 주고 확인을 받은 뒤 치환한다. 원장에 `gate: publish-autofix → <yes|no>`.
- 나머지 FAIL은 review 9단계로 되돌린다. 원장에 `reopen: review-9 <사유>`를 남긴다.
- MANUAL은 원장에 review 9단계 확인 줄이 있는지 본다. 없으면 되돌린다.

## 1단계, Word 생성 (`formats`에 docx가 있을 때)

판형은 블록 `publish.trim_options` 중에서 사용자에게 한 번 묻고 원장에 `gate: trim → <판형>`을 남긴다. `generate_docx.py`는 `--trim`이 없으면 원장의 판형 결정을 쓰고, 결정이 없거나 `--trim`이 결정과 다르면 멈춘다. 린터는 docx 쪽 크기가 결정과 맞는지 본다.

```
python3 <스킬>/scripts/generate_docx.py --run <run>              # 원장의 판형 결정을 쓴다
python3 <스킬>/scripts/generate_docx.py --run <run> --trim <판형> # 결정과 같은 값만 받는다
```

생성기가 하는 일: 표지(제목, `publish.cover_label`, 필명), 판권면, 목차(부·장·`back_matter`), 부 제목 페이지(장편), 장마다 새 페이지, 본문 폰트·크기·줄간격·들여쓰기, 여백. 앞부분(표지·판권·목차)과 본문은 구역이 나뉘어 머리글·쪽번호는 본문에만 찍히고 쪽번호는 본문 첫 쪽이 1이다. 장편의 부 제목 쪽도 자기 구역이라 머리글·쪽번호가 없다(번호는 이어서 센다). 세로 위치는 판형 높이에 비례한 간격으로, 쪽 나눔은 제목 문단의 '앞에서 쪽 나눔'으로 잡아 빈 문단을 넣지 않는다. 원고의 문단 사이 빈 줄은 문단 간격으로 바뀌고(e북과 같은 문단 구성), 빈 줄이 두 줄 이상이면 장면 전환으로 보고 간격을 더 둔다. docx에는 글꼴 이름이 하나만 저장된다. 생성기는 글꼴 표에 계열(본문 명조=roman, 제목 고딕=swiss), 한글 문자 집합, 대체 이름 하나(`body_font_fallback`·`heading_font_fallback`과 흔한 글꼴 목록 중 이 컴퓨터에 있는 첫 글꼴)를 적는다. Word는 원래 글꼴이 없으면 이 정보로 같은 계열의 한글 글꼴을 고른다. LibreOffice는 자기 대체 표를 써서 장식용 글꼴로 바뀔 수 있다. 생성기는 지정 글꼴이 이 컴퓨터에 없으면 WARN을 낸다(fc-list가 있으면 그것으로, 없으면 macOS·Windows·Linux 글꼴 폴더의 글꼴 파일 이름 표를 직접 읽어 확인한다. macOS가 내려받기만 하고 켜지 않은 글꼴은 깔린 것으로 세지 않는다). 블록의 글꼴 이름은 설치된 글꼴의 계열 이름과 글자 하나까지 같아야 한다. WARN이 나오면 글꼴 관리자에서 실제 계열 이름을 확인한다. 확실한 조판이 필요하면 지정 글꼴(KoPubWorld는 무료)을 깔거나 블록 `body_font`를 깔린 글꼴로 바꾼다(`gate: block-change`).

## 2단계, 웹 e북 생성 (`formats`에 ebook이 있을 때)

```
python3 <스킬>/scripts/generate_ebook.py --run <run>
```

디자인은 블록 `publish.ebook.design`(기본 `plain`)이다. 표지 문구, 소개문, 뒤표지 인용, 제사, 판권(출판사, 발행 연월, ISBN, 저작권 연도)은 모두 블록 `publish`와 `publish.ebook`에서 채운다. 값이 비어 있으면 그 줄을 넣지 않는다. 정본에 없는 ISBN이나 출판사를 지어 넣지 않는다.

- **제사 출처.** 제사(`epigraph`)가 있고 `source_verified`가 true가 아니면 출판 전에 사용자에게 묻는다(`need_user`, 질문 id `epigraph-source`): (a) 출처를 확인해 true로 바꾼다 (b) 확인 없이 싣는다(지휘가 `waiver: epigraph_source <사유>`와 승인 줄을 남긴다) (c) 뺀다(`epigraph: null`, `gate: block-change → approved publish.ebook.epigraph (날짜) "<원문>"`). 린터는 승인 없는 미확인 제사를 FAIL로 본다.
- **네트워크.** e북은 웹 글꼴(Pretendard)과 쪽 넘김 라이브러리(page-flip)를 CDN에서 불러온다. 오프라인이거나 5초 안에 못 불러오면 넘김 효과 없이 같은 쪽 구성으로 읽는 대체 화면이 뜨고, 글꼴은 시스템 글꼴로 바뀐다.
- **디자인 전용 조각.** 표지 출판사 표시처럼 모양이 디자인마다 다른 부분은 디자인 파일 안의 `<template data-slot="COVER_PUBLISHER">…{{PUBLISHER}}…</template>`가 정한다. 생성기는 값만 넣고 조각을 슬롯 자리로 옮긴다.

## 1·2단계 사후 검증

```
python3 <스킬>/scripts/validate_draft.py --run <run> > 03_output/<run>/validate_report.txt
```

`--run`이면 같은 run의 `final.docx`와 `ebook.html`도 검사한다: 표지 제목·장르 표기, 목차, 마지막 문단(docx), `<title>`, 원고 헤딩·순서, 마지막 줄, 채우지 않은 슬롯(e북). FAIL이면 블록이나 생성기 인자를 고쳐 다시 만든다. docx 폰트 대체와 e북 페이지 넘김은 직접 열어 확인하고 원장에 한 줄 남긴다.

## 3단계, 메타데이터 → `03_output/<run>/metadata.md`

마케터 리뷰를 1차 입력으로 쓰고, 빠진 항목은 본문과 블록을 보고 채운다. 아래 여섯 개의 `##` 섹션 이름을 그대로 쓴다(린터가 검사한다).

- `## 작품 정보`: 제목, 장르 표기, 필명, 출판사, 분량(`분량: <글자 수>자 (<매수>매, …)` 형식, 글자 수는 검증기 보고 그대로), 화자, 기준 연도, 핵심 모티프
- `## 도서 분류`: BISAC 1~2개, KDC (한국 소설 813.x 계열)
- `## 판매 카피`: 한 줄(40자 이내), 띠지(2~3행), 본문 카피(150~250자, 결말 누설 금지, 실제 글자 수 표기)
- `## 검색 키워드`: 7~10개, 한국어 우선
- `## 가격 전략`: 단독 출판 가격대 제안, 묶음 추천
- `## 배포 메모`: 교보문고, 리디, 예스24, 밀리의 서재, 알라딘의 분류·키워드 적용

금지: 합평 점수 인용, 정본에 없는 수상·판매량·평점·추천인 실명, em dash.

## 완료

1. 원장에 `stage: publish done <날짜>`, `status: published`. 이 run은 이제 끝난 run이다(workflow.md 2절). 이어서 `python3 <스킬>/scripts/lock_run.py --run <run>`으로 잠금 줄을 남긴다(ledger.md "잠금").
2. `python3 <스킬>/scripts/lint_project.py`가 FAIL 0인지 확인한다.
3. 안내: "퍼블리싱 완료. `03_output/<run>/`에 형식별 산출물과 `metadata.md`가 준비되었습니다. 게이트 보고서는 `validate_report.txt`에 있습니다."
