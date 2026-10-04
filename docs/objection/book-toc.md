# 작품 설정 (이 파일과 00_storyline/storyline.md만 교체하면 다른 작품을 쓴다)

init_project.py가 만든 파일이다. 숫자·이름의 정본은 아래 블록이다. 고친 뒤 `python3 <스킬>/scripts/lint_project.py`로 확인한다. 출판 정보 빈칸(`<…>`)은 publish 단계에서 묻는다.

## 작품 파라미터 블록

```json
{
  "schema_version": 1,
  "title": "이의신청",
  "pen_name": "AI ROASTING",
  "genre": "SF",
  "genre_label": "단편 소설",
  "base_year": 2032,
  "target_reader": "김초엽·천선란·정세랑·장강명을 즐겨 읽는 30~40대 한국 독자. 일상 SF에 익숙하고 사회파 색을 좋아한다.",
  "narrator": {
    "name": "한서진",
    "person": 1
  },
  "length": {
    "target_pages": 60,
    "chars_per_page": 200,
    "tolerance": 0.1
  },
  "structure_mode": "chapter",
  "chapters": [
    {
      "no": 1,
      "title": "접수",
      "pages": 14
    },
    {
      "no": 2,
      "title": "점수",
      "pages": 16
    },
    {
      "no": 3,
      "title": "현장",
      "pages": 18
    },
    {
      "no": 4,
      "title": "결정",
      "pages": 12
    }
  ],
  "last_line": "나는 도장을 찍지 않고 서랍을 닫았다.",
  "anchors": [
    {
      "name": "기각 도장과 인주, 서랍",
      "keywords": [
        "도장",
        "인주",
        "서랍"
      ],
      "min_total": 8,
      "chapters": [
        1,
        3,
        4
      ]
    },
    {
      "name": "연필 수위선",
      "keywords": [
        "연필",
        "수위"
      ],
      "min_total": 5,
      "chapters": [
        2,
        3,
        4
      ]
    },
    {
      "name": "손글씨 한 문장",
      "keywords": [
        "제 집을 봐 주세요"
      ],
      "min_total": 3,
      "chapters": [
        1,
        2,
        3,
        4
      ]
    }
  ],
  "characters": [
    "조옥순",
    "민 팀장",
    "배용수"
  ],
  "retired_names": [
    "조봉례"
  ],
  "forbidden_disclosures": [
    "어릴 때 반지하",
    "어렸을 때 반지하",
    "반지하에서 자랐",
    "나도 반지하",
    "위원회는 인용",
    "위원회는 기각",
    "입주가 결정",
    "입주 통지",
    "남편이 남긴",
    "남편의 글씨",
    "남편 글씨",
    "내가 찍은 도장으로",
    "아버지가 새",
    "아버지가 판",
    "아버지가 파",
    "벽이라고 적",
    "적어 놓고 지나",
    "팀장이 배정",
    "배정한 사람",
    "열고 싶지 않"
  ],
  "wit": {
    "per_chapter_min": 1,
    "per_chapter_max": 2,
    "sources": [
      "건조한 분류",
      "절차와 현실의 간격",
      "무심한 관찰",
      "옅은 자조",
      "일상의 미세한 부조리"
    ],
    "zero_zones": [
      "3장 벽의 수위선부터 3장 끝까지",
      "4장 민 팀장이 결정서를 내려놓는 순간부터 마지막 줄까지"
    ]
  },
  "style": {
    "principles": 9,
    "avg_sentence_chars_max": 22,
    "paragraph_lines": [
      4,
      6
    ],
    "em_dash": "forbid",
    "bullets": "forbid",
    "bold_markdown": "forbid",
    "translationese": [
      "에 대해",
      "에 의해",
      "함에 있어",
      "에 있어서",
      "을 통해",
      "를 통해",
      "되어졌다"
    ],
    "cliches": [
      "심장이 쿵",
      "시간이 멈춘",
      "눈앞이 캄캄",
      "가슴이 철렁"
    ]
  },
  "review": {
    "story_panel": "standard",
    "story_pass": 9.5,
    "story_critic_min": 8.0,
    "story_proof_weight": 0.5,
    "body_pass": 9.0,
    "rounds_before_user_check": 3,
    "self_bias_warn": 0.5
  },
  "publish": {
    "cover_label": "단편 소설",
    "formats": [
      "ebook"
    ],
    "publisher": "ArgosLab",
    "pub_date": "2026년 10월",
    "copyright_year": 2026,
    "colophon_note": "이 책은 Anthropic의 Claude Opus 5.5로 썼습니다.",
    "isbn": null,
    "ebook": {
      "design": "objection",
      "description": "2032년 서울, 공공임대주택 이의신청은 AI가 심사하고 사람은 기각 결정서에 도장만 찍는다. 9년차 심사관 한서진은 같은 문장을 아홉 번 보낸 신청서 한 장 앞에서 처음으로 손을 멈춘다.",
      "cover_title_lines": [],
      "cover_copy": "2032년, AI가 판정하고 사람은 도장을 찍는다.",
      "epigraph": {
        "lines": [
          "우리는 아직 컴퓨터를 지혜롭게 만들 방법을 모른다.",
          "그러니 지금은 지혜가 필요한 일을 컴퓨터에게 맡겨서는 안 된다."
        ],
        "attr_lines": [
          "요제프 바이첸바움",
          "최초의 챗봇으로 꼽히는 ELIZA(1966)를 만든 MIT 컴퓨터과학자",
          "『컴퓨터의 힘과 인간의 이성』(1976)에서"
        ],
        "source_verified": true
      },
      "back_quote": {
        "lines": [
          "나는 도장을 찍지 않고",
          "서랍을 닫았다."
        ],
        "attr_lines": [
          "4장 「결정」에서"
        ]
      },
      "synopsis": [
        "2032년 서울, 공공임대주택 이의신청은",
        "AI가 심사하고 사람은 도장만 찍는다.",
        "",
        "9년차 심사관 한서진은 하루 200장을 찍는다.",
        "어느 월요일, 같은 문장을 아홉 번 보낸",
        "신청서 한 장에서 손이 멈춘다.",
        "앞의 여덟 장에는 모두 서진의 도장이 찍혀 있었다.",
        "",
        "처리기한은 14일, 규정은 현장 방문을 금지한다.",
        "장맛비가 내리는 토요일,",
        "서진은 계단 아래 그 집의 문을 두드린다."
      ],
      "og_description": "AI가 쓴 기각서에 도장만 찍던 사람이, 처음으로 손을 멈췄다."
    },
    "copyright_holder": "ArgosLab"
  },
  "back_matter": [
    "작가의 말"
  ]
}
```

## 필드 설명

| 키 | 뜻 | 누가 쓰나 |
|---|---|---|
| `genre` | 장르 이름(SF, 가족 드라마 등). WRITER_SF(장르 동료 작가)·MARKETER·PINK 카드가 읽는다. `genre_label`은 표지·메타에 찍는 표기 | storyline, review |
| `characters` | 본문에 반드시 나올 이름·호칭. 1인칭 화자의 이름은 대사로 불릴 때만 본문에 나오므로, 본문에 이름이 안 나오는 작품이면 넣지 않는다 | 검증기 |
| `publish.ebook.description`, `og_description` | e북 메타 소개문. `og_description`을 비우면 `description`을 쓴다 | e북 생성기 |
| `publish.ebook.cover_copy`, `synopsis` | e북 표지 한 줄 문구, 뒤표지 소개(줄 목록, 빈 문자열은 빈 줄) | e북 생성기 |
| `narrator.person` | 1이면 1인칭. 검증기가 서술문의 화자 이름 주어를 시점 위반으로 잡는다 | write, 검증기 |
| `length` | 200자 원고지 매수와 허용 오차. 글자 수는 장 구간만, 줄바꿈 제외, 공백 포함 | write, 검증기 |
| `structure_mode` | `chapter` 또는 `part`. `part`면 `parts` 배열을 추가하고 `<스킬>/references/workflow.md` 5절 장편 규칙을 쓴다 | write, review |
| `chapters[].pages` | 장별 매수. 합이 `length.target_pages`와 같아야 한다 | write, SILVER, 린터 |
| `last_line` | 작품 마지막 줄. storyline 통과본에 같은 문장이 있어야 한다 | 검증기, 린터 |
| `back_matter` | 마지막 장 뒤에 둘 섹션 이름 목록(예: 작가의 말). 원고에서 `# <이름>` 헤딩으로 쓴다. 목록에 없는 장 밖 H1은 FAIL | 검증기, e북 생성기 |
| `anchors` | 시각 닻. `min_total` 미달은 FAIL, `chapters` 배치 누락은 WARN | write, BLUE, 검증기 |
| `retired_names` | 바꾸기 전 이름. 본문에 남으면 FAIL | 검증기 |
| `forbidden_disclosures` | 명시 금지 항목을 잡는 구절 | 검증기 |
| `wit` | 장당 위트 횟수 범위와 0회 구역 | write, GOLD |
| `review.story_panel` | `lite` / `standard` / `extended` (`<스킬>/references/workflow.md` 4.3) | storyline |
| `base_year` | 작품 안의 기준 연도. 리서치와 본문 연도 표기가 따른다 | research, write |
| `review.story_critic_min` | 스토리 패널에 CRITIC이 있을 때 CRITIC 카드 점수 하한 | storyline, 린터 |
| `review.story_proof_weight` | 스토리 패널 점수에서 PROOF 카드의 가중치(0~1) | storyline |
| `review.rounds_before_user_check` | 이 라운드를 넘기기 전 사용자에게 계속할지 묻는다 | storyline, review, 린터 |
| `style.*` | 문체 9원칙의 숫자(문장 평균 길이, 단락 줄 수)와 금지 목록(번역투, 클리셰). em dash·불릿·`**`는 forbid 고정 | write, 검증기 |
| `publish.third_party_verified` | back_matter의 서평·추천사·해설이 실제 제3자 글이면 true. 가상 평자면 원장 waiver로 처리 | 린터 |
| `review.self_bias_warn` | BLACK 자기 점수가 패널보다 이만큼 높으면 편향 의심 표기 | storyline |
| `review.*_pass` | 통과선. 이 값 외의 곳에 통과선을 적지 않는다 | storyline, review |
| `publish.formats` | 출판 형식. `["ebook"]` 하나다(웹 e북 `ebook.html`). Word(docx)는 만들지 않는다 | publish, 린터 |
| `publish.copyright_holder` | 판권면 © 줄의 저작권자. 비우면 필명(`pen_name`)을 쓴다 | e북 생성기 |
| `publish.publisher`, `pub_date`, `isbn`, `copyright_year` | 판권 정보. 비우면(`""`, `null`) 그 줄을 넣지 않는다. 정본에 없는 값을 지어 넣지 않는다 | e북 생성기 |
| `publish.ebook.design` | e북 디자인 이름. `plain`(공용 기본). 작품 전용 디자인은 프로젝트 폴더의 `designs/ebook/<이름>.html`(스킬의 `templates/ebook/plain.html`을 복사해 고친다), 공용 디자인은 `<스킬>/templates/ebook/`에 둔다. 생성기는 프로젝트 쪽을 먼저 찾는다. 스킬 폴더에 넣은 파일은 다시 설치할 때 지워지므로 작품 전용 디자인을 거기에 두지 않는다. | e북 생성기 |
| `publish.ebook.cover_title_lines` | 표지 제목 줄바꿈(두 줄까지, 한 줄 8자 이내). 비우면 제목 한 줄 | e북 생성기 |
| `publish.ebook.epigraph` | 제사 `{"lines": [...], "attr_lines": [...], "source_verified": true}`. 출처를 확인하지 않았으면 false로 두고 검증기가 WARN을 낸다 | e북 생성기, 검증기 |
| `publish.ebook.back_quote` | 뒤표지 인용 `{"lines": [...], "attr_lines": [...]}` 또는 null | e북 생성기 |

## 페르소나

### BLACK, 작가

아래는 기본값이다. 작품에 맞게 고치되 비워 두지 않는다. 평가자 카드(BLACK, GOLD)가 이 절을 그대로 읽는다.

- 이름: 블록의 `pen_name`
- 세대·배경: 30대 한국 작가. 블록 `genre` 장르의 단편으로 등단. 흡수한 작가는 storyline 합평에서 정한다
- 세계관: 큰 메시지를 박지 않는다. 한 사람의 동작 하나에 관계나 사회 전체가 잠깐 비치는 자리를 본다.
- 시선: 차가운 거리감을 갖되 인물에게 따뜻하다. 인물의 약점을 비웃지 않는다.

### 문체 9원칙 (『이의신청』 2판에서 조정)

1. **읽히는 문장.** 한 문장 평균 `style.avg_sentence_chars_max`자 안쪽. 한 장면 안의 연속 동작은 연결 어미로 잇는다. 한 문장에 한 동작씩 끊어 나열하지 않는다. 소리 내어 읽어 걸리는 문장은 고친다.
2. **단락 짧게, 중언부언 금지.** 한 단락 `style.paragraph_lines`줄. 한 정보는 한 번만 준다. 서술과 대사로 같은 말을 두 번 하지 않고, 장면이 보여 준 것을 다음 문장이 요약하지 않는다.
3. **마지막 한 줄.** 각 장의 마지막 문장은 동작 또는 사물로 닫는다. 정리·요약 문장으로 닫지 않는다.
4. **위트.** 한 장에 `wit.per_chapter_min`~`wit.per_chapter_max`회. 강한 농담 0회. `wit.zero_zones`에는 0회. 출처는 `wit.sources`.
5. **비유는 일상 사물.** 추상어를 줄인다.
6. **설명하지 말고 보여 준다.** 인물의 감정, 동기, 깨달음, 의미를 서술하지 않는다. 동작, 사물, 화면의 글자, 대사, 침묵으로만 보인다. 독자가 한 번에 알아듣지 못하는 비유는 쓰지 않는다.
7. **시점 안정.** 1인칭이면 화자는 자기 이름을 서술문의 주어로 쓰지 않는다(대사 속 호명은 허용). 화자가 모르는 정보는 쓰지 않는다.
8. **자연스러운 한국어.** 번역투(`style.translationese`), 영어식 무생물 주어, 영어식 수동태 금지. 직장 상사는 부하에게 존댓말을 쓴다. 수량·단위는 아라비아 숫자(200장, 11센티), 시각과 서수는 한글(네 시, 아홉 번째).
9. **주술 호응.** 모든 문장의 주어와 서술어가 정확히 호응한다.

원칙 개수를 바꾸면 블록 `style.principles`도 같이 바꾼다. em dash(—, –)는 쓰지 않는다.

## 작품 내 인물

주요 인물을 한 사람에 한 줄로 요약한다(이름, 나이, 직업, 작품 속 역할, 손버릇). 1차 정본은 storyline 통과본이고, 여기는 평가자 카드가 빨리 읽는 요약이다. 블록 `characters`의 이름이 모두 나와야 한다.

- 한서진 (41, 여성, 공공주택배정원 이의신청 심사관 9년차): 화자. 성별 단서는 3장 장면 6 조옥순 씨의 한마디 하나(run 20261003_03 review 6단계 지휘 결정). 결점은 서식 칸에 없는 것은 보지 않는 것(2027 일지의 "벽" 한 글자). 도장 뚜껑을 엄지로 여닫고, 아침마다 서랍에서 나무 도장(옆면 각인 "한씨도장포 23.3.")을 꺼낸다. 2029년까지 같은 구의 현장 조사를 다녔다
- 조옥순 (79, 반지하 단독 거주, 전 봉제공장 미싱사, 신청인): 9주째 같은 문장으로 이의신청서를 보낸다. 원하는 것은 새 집보다 2027년 판정의 정정이다. 먹지 사본을 쥐고 심사관을 시험했다(3장 "벽은요?"). 몽당연필을 귀에 꽂고, 수위와 양수기 시간을 공책에 적는다
- 민정훈 (54, 이의신청 심사팀장, 본문 호칭 "민 팀장"): 서진에게 존댓말을 쓴다. 현황판을 볼 때 안경을 이마에 올린다. 2027년 그 구 현장조사팀 팀장(본문은 일지의 배정 확인 도장 이름만). 4장에서 인주 통을 밀고, 대기 순번 화면의 한 줄(이삿짐 계약서를 낸 집)을 짚고, 정정 의견서를 접어 서진의 서랍에 넣는다
- 배용수 (조옥순의 남편, 2030년 겨울 사망, 본문 밖 인물): 2019년부터 벽에 연필 수위선을 긋고 공책을 썼다. 본문에는 먹지 사본의 입회인 서명, 글씨, 작업복과 작업화, 연필로만 나온다

### 이름 짓기 원칙

기본값:

- 한국인 성씨 관례를 따른다. 자녀는 모친 성을 잇지 않는다.
- 가족이 아닌 주요 인물끼리는 성씨가 겹치지 않게 한다. 가족은 관례대로 같은 성을 쓴다(SF·가족 서사 공통).
- 로봇·시스템 인공물에는 사람 이름을 붙이지 않는다. 모델 코드만 쓴다.
- 바꾼 이름은 블록 `retired_names`에 남긴다.

## 메시지 정책

기본값: 작품이 메시지를 박지 않는다. 독자가 안고 가게 둔다. 마지막 장의 마지막 동작 외에는 결론을 쓰지 않는다.

## 명시 금지 항목

storyline에만 있고 본문에 풀어 쓰지 않을 사실을 적는다(인물의 과거, 사건의 진상 등). 검증기가 잡을 구절은 블록 `forbidden_disclosures`에 넣는다. 없으면 "없음"이라고 적는다.

- 서진이 2027년 일지에 "벽"을 적고 지나간 사정, 2장에서 서랍 맨 아래 칸을 열지 않은 이유, 민 팀장이 2027년 배정을 확인했다는 설명(본문은 일지의 글자 하나와 도장 이름만, run 20261003_03)
- B02 가구와 이삿짐 계약서를 낸 가구에 일어날 일
- 서진의 반지하 유년은 이번 판(run 20261003_02)에서 쓰지 않는다. 블록의 관련 구절은 오기 방지로 남겨 둔다
- 2027년 현장 조사자가 서진이라는 것을 화자가 진술하는 문장, 서진이 그날을 기억하는지에 대한 진술 (본문은 먹지 사본의 도장 자국으로만 보인다)
- 서진의 나무 도장을 아버지가 새겼고 아버지가 세상을 떠났다는 사실 (본문은 각인, 닳은 엄지 자리, 뜯지 않은 만년도장으로만 보인다)
- 남편 배용수에 대한 설명. 조옥순의 말은 "그 사람 글씨예요" 한마디
- 위원회 심사 결과와 조옥순의 입주 여부
- 조옥순이 그 집에 오래 머문 사정(남편이 남긴 보증금, 이사 비용). storyline의 "본문에 쓰지 않는 배경"이며 화자가 모르는 정보다

## 작성 스타일

기본값:

- 어미: 해라체와 1인칭 진술 혼합.
- 독자 지칭: 본문에 "독자"를 부르지 않는다.
- 불릿 0회, `**` 0회, 클리셰 0회, em dash 0회.
- 마지막 장 뒤에는 블록 `back_matter`의 섹션만 둔다.
