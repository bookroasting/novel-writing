# 작품 설정 (이 파일과 00_storyline/storyline.md만 교체하면 다른 작품을 쓴다)

사용법: 시험용 픽스처다. 프로젝트 폴더의 `book-toc.md` 자리에 두고 쓴다.

## 작품 파라미터 블록

```json
{
  "schema_version": 1,
  "title": "김장하는 날",
  "pen_name": "테스트 필명",
  "genre": "가족 드라마",
  "genre_label": "단편 소설",
  "base_year": 2026,
  "target_reader": "가족 서사를 즐겨 읽는 40대 독자.",
  "narrator": {
    "name": "윤서",
    "person": 1
  },
  "length": {
    "target_pages": 40,
    "chars_per_page": 200,
    "tolerance": 0.1
  },
  "structure_mode": "chapter",
  "chapters": [
    {
      "no": 1,
      "title": "배추",
      "pages": 14
    },
    {
      "no": 2,
      "title": "소금",
      "pages": 14
    },
    {
      "no": 3,
      "title": "항아리",
      "pages": 12
    }
  ],
  "last_line": "엄마가 항아리 뚜껑을 덮었다.",
  "anchors": [
    {
      "name": "빨간 고무장갑",
      "keywords": [
        "고무장갑"
      ],
      "min_total": 3,
      "chapters": [
        1,
        3
      ]
    }
  ],
  "characters": [
    "엄마",
    "윤재"
  ],
  "retired_names": [],
  "forbidden_disclosures": [
    "아버지가 떠난 이유는"
  ],
  "wit": {
    "per_chapter_min": 1,
    "per_chapter_max": 3,
    "sources": [
      "건조한 분류",
      "절차와 현실의 간격",
      "무심한 관찰",
      "옅은 자조",
      "일상의 미세한 부조리"
    ],
    "zero_zones": [
      "아버지의 빈자리"
    ]
  },
  "style": {
    "principles": 9,
    "avg_sentence_chars_max": 15,
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
    "publisher": "",
    "pub_date": "2026년 11월",
    "copyright_year": 2026,
    "isbn": null,
    "ebook": {
      "design": "plain",
      "description": "김장하는 날, 세 식구가 말하지 않는 것.",
      "cover_title_lines": [],
      "cover_copy": "",
      "epigraph": null,
      "back_quote": null,
      "synopsis": [
        "11월 첫 토요일, 엄마 집 마당.",
        "세 식구가 배추를 절인다."
      ],
      "og_description": null
    },
    "copyright_holder": ""
  },
  "back_matter": []
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
| `publish.ebook.design` | e북 디자인. `plain`(기본, 장식만) 또는 `<스킬>/templates/ebook/`의 다른 파일 이름 | e북 생성기 |
| `publish.ebook.cover_title_lines` | 표지 제목 줄바꿈(두 줄까지, 한 줄 8자 이내). 비우면 제목 한 줄 | e북 생성기 |
| `publish.ebook.epigraph` | 제사 `{"lines": [...], "attr_lines": [...], "source_verified": true}`. 출처를 확인하지 않았으면 false로 두고 검증기가 WARN을 낸다 | e북 생성기, 검증기 |
| `publish.ebook.back_quote` | 뒤표지 인용 `{"lines": [...], "attr_lines": [...]}` 또는 null | e북 생성기 |

## 페르소나

### BLACK, 작가

아래는 기본값이다. 작품에 맞게 고치되 비워 두지 않는다. 평가자 카드(BLACK, GOLD)가 이 절을 그대로 읽는다.

- 이름: 블록의 `pen_name`
- 세대·배경: 30대 한국 작가. 블록 `genre_label` 장르의 단편으로 등단. 최은영·김애란을 흡수.
- 세계관: 큰 메시지를 박지 않는다. 한 사람의 동작 하나에 관계나 사회 전체가 잠깐 비치는 자리를 본다.
- 시선: 차가운 거리감을 갖되 인물에게 따뜻하다. 인물의 약점을 비웃지 않는다.

### 문체 9원칙 (기본값, 작품에 맞게 조정)

1. **단문 우선.** 한 문장 평균 `style.avg_sentence_chars_max`자 안쪽. 30자 이상 문장은 한 단락에 두 개를 넘기지 않는다.
2. **단락 짧게.** 한 단락 `style.paragraph_lines`줄. 페이지의 공백도 호흡이다.
3. **마지막 한 줄.** 각 장의 마지막 문장은 동작 또는 사물로 닫는다. 정리·요약 문장으로 닫지 않는다.
4. **위트.** 한 장에 `wit.per_chapter_min`~`wit.per_chapter_max`회. 강한 농담 0회. `wit.zero_zones`에는 0회. 출처는 `wit.sources`.
5. **비유는 일상 사물.** 추상어를 줄인다.
6. **감정의 직접 노출 금지.** 동작과 침묵으로 보여 준다.
7. **시점 안정.** 1인칭이면 화자는 자기 이름을 서술문의 주어로 쓰지 않는다(대사 속 호명은 허용). 화자가 모르는 정보는 쓰지 않는다.
8. **자연스러운 한국어.** 번역투(`style.translationese`), 영어식 무생물 주어, 영어식 수동태 금지.
9. **주술 호응.** 모든 문장의 주어와 서술어가 정확히 호응한다.

원칙 개수를 바꾸면 블록 `style.principles`도 같이 바꾼다. em dash(—, –)는 쓰지 않는다.

## 작품 내 인물

주요 인물을 한 사람에 한 줄로 요약한다(이름, 나이, 직업, 작품 속 역할, 손버릇). 1차 정본은 storyline 통과본이고, 여기는 평가자 카드가 빨리 읽는 요약이다. 블록 `characters`의 이름이 모두 나와야 한다.

- 윤서 (38세, 회사원): 화자. 손버릇: 칼 닦기
- 엄마 (67세): 김장을 이끈다. 손버릇: 고무장갑 끝 당기기
- 윤재 (34세): 동생. 손버릇: 물 길어 오기

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

- 아버지가 집을 떠난 이유

## 작성 스타일

기본값:

- 어미: 해라체와 1인칭 진술 혼합.
- 독자 지칭: 본문에 "독자"를 부르지 않는다.
- 불릿 0회, `**` 0회, 클리셰 0회, em dash 0회.
- 마지막 장 뒤에는 블록 `back_matter`의 섹션만 둔다.
