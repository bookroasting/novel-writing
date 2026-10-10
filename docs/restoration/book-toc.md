# 작품 설정 (이 파일과 00_storyline/storyline.md만 교체하면 다른 작품을 쓴다)

init_project.py가 만든 파일이다. 숫자·이름의 정본은 아래 블록이다. 고친 뒤 `python3 <스킬>/scripts/lint_project.py`로 확인한다. 출판 정보 빈칸(`<…>`)은 publish 단계에서 묻는다.

## 작품 파라미터 블록

```json
{
  "schema_version": 1,
  "title": "복원",
  "pen_name": "AI ROASTING",
  "genre": "SF",
  "genre_label": "단편 소설",
  "base_year": 2034,
  "target_reader": "부모의 노화를 곁에서 지켜보는 30~50대 독자. 가족 사진과 대화 기록을 AI에 맡겨 볼까 한 번쯤 생각해 본 사람.",
  "narrator": {
    "name": "노은재",
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
      "title": "수집",
      "pages": 12
    },
    {
      "no": 2,
      "title": "대조",
      "pages": 16
    },
    {
      "no": 3,
      "title": "누락",
      "pages": 18
    },
    {
      "no": 4,
      "title": "복원",
      "pages": 14
    }
  ],
  "last_line": "나는 반짇고리 뚜껑 위에 손바닥을 얹었다.",
  "anchors": [
    {
      "name": "편도 기차표 두 장과 반짇고리",
      "keywords": [
        "기차표",
        "승차권",
        "반짇고리"
      ],
      "min_total": 5,
      "chapters": [
        3,
        4
      ]
    },
    {
      "name": "가사 없는 허밍",
      "keywords": [
        "흥얼"
      ],
      "min_total": 5,
      "chapters": [
        1,
        2,
        3,
        4
      ]
    },
    {
      "name": "그런 기록은 없어요와 비어 있는 칸",
      "keywords": [
        "기록은 없어요",
        "비어 있"
      ],
      "min_total": 6,
      "chapters": [
        1,
        2,
        3,
        4
      ]
    },
    {
      "name": "옥수수",
      "keywords": [
        "옥수수"
      ],
      "min_total": 5,
      "chapters": [
        2,
        3,
        4
      ]
    }
  ],
  "characters": [
    "노은재",
    "신옥희",
    "노은석",
    "새록"
  ],
  "retired_names": [
    "다시봄"
  ],
  "forbidden_disclosures": [
    "가출",
    "도망",
    "이혼",
    "돌아오지 않을 생각",
    "돌아오지 않으려",
    "엄마를 돌려보냈",
    "이제야 알았",
    "일부러 비웠",
    "일부러 비워"
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
      "3장 장면 3(강릉의 기억)부터 3장 끝까지",
      "4장 엄마의 \"그럼 내 거네\" 다음 문장부터 마지막 줄까지"
    ]
  },
  "style": {
    "principles": 9,
    "avg_sentence_chars_max": 22,
    "paragraph_lines_max": 6,
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
    "pub_date": "2026년 10월",
    "copyright_year": 2026,
    "isbn": null,
    "ebook": {
      "design": "restoration",
      "description": "2034년 봄, 경도 치매 진단을 받은 엄마의 식탁에 기억 보조 AI 새록이 놓인다. 엄마가 딸과 기차를 타고 바다에 갔던 날을 말할 때마다 새록은 정중하게 답한다. 그런 기록은 없어요.",
      "cover_title_lines": [],
      "cover_copy": "",
      "epigraph": null,
      "back_quote": null,
      "synopsis": [
        "엄마는 딸과 기차를 타고 바다에 가서 옥수수를 먹었다고 했다. 기억 보조 AI는 그런 기록이 없다고 했다.",
        "가스 불은 꺼 주고 날짜는 바로잡아 주는 정중한 기계 앞에서, 딸은 비어 있는 하루를 채울 버튼에 손을 올린다."
      ],
      "og_description": null
    },
    "copyright_holder": "",
    "colophon_note": ""
  },
  "back_matter": [
    "작가의 말"
  ]
}
```

## 필드 설명

| 키 | 뜻 | 누가 쓰나 |
|---|---|---|
| `genre` | 장르 이름(SF, 가족 드라마 등). TEAL(장르 동료 작가)·ORANGE·PINK 카드가 읽는다. `genre_label`은 표지·메타에 찍는 표기 | storyline, review |
| `characters` | 본문에 반드시 나올 이름·호칭. 1인칭 화자의 이름은 대사로 불릴 때만 본문에 나오므로, 본문에 이름이 안 나오는 작품이면 넣지 않는다 | 검증기 |
| `publish.ebook.description`, `og_description` | e북 메타 소개문. `og_description`을 비우면 `description`을 쓴다 | e북 생성기 |
| `publish.ebook.cover_copy`, `synopsis` | e북 표지 한 줄 문구, 뒤표지 소개(줄 목록, 빈 문자열은 빈 줄) | e북 생성기 |
| `narrator.person` | 1이면 1인칭. 검증기가 서술문의 화자 이름 주어를 시점 위반으로 잡는다 | write, 검증기 |
| `length` | 200자 원고지 매수와 허용 오차. 글자 수는 장 구간만, 줄바꿈 제외, 공백 포함 | write, 검증기 |
| `structure_mode` | `chapter` 또는 `part`. `part`면 `parts` 배열을 추가하고 `<스킬>/references/workflow.md` 5절 장편 규칙을 쓴다 | write, review |
| `chapters[].pages` | 장별 매수. 합이 `length.target_pages`와 같아야 한다 | write, SILVER, 린터 |
| `last_line` | 작품 마지막 줄. storyline 통과본에 같은 문장이 있어야 한다 | 검증기, 린터 |
| `back_matter` | 마지막 장 뒤에 둘 섹션 이름 목록(예: 작가의 말). 원고에서 `# <이름>` 헤딩으로 쓴다. 목록에 없는 장 밖 H1은 FAIL. 작가 이름으로 나가는 글(작가의 말, 감사의 말, 헌사)은 작가가 원문을 주거나, 초안을 명시 승인하거나, BLACK에게 쓰라고 명시 요청한 것만 넣는다(원장 `gate: author-text-<섹션>`) | 검증기, e북 생성기 |
| `anchors` | 시각 닻. `min_total` 미달은 FAIL, `chapters` 배치 누락은 WARN | write, BLUE, 검증기 |
| `retired_names` | 바꾸기 전 이름. 본문에 남으면 FAIL | 검증기 |
| `forbidden_disclosures` | 명시 금지 항목을 잡는 구절 | 검증기 |
| `wit` | 장당 위트 횟수 범위와 0회 구역 | write, GOLD |
| `review.story_panel` | `lite` / `standard` / `extended` (`<스킬>/references/workflow.md` 4.3) | storyline |
| `base_year` | 작품 안의 기준 연도. 리서치와 본문 연도 표기가 따른다 | research, write |
| `review.story_critic_min` | 스토리 패널에 BURGUNDY가 있을 때 BURGUNDY 카드 점수 하한 | storyline, 린터 |
| `review.story_proof_weight` | 스토리 패널 점수에서 OLIVE 카드의 가중치(0~1) | storyline |
| `review.rounds_before_user_check` | 이 라운드를 넘기기 전 사용자에게 계속할지 묻는다 | storyline, review, 린터 |
| `style.*` | 문체 9원칙의 숫자(문장 평균 길이, 단락 줄 수)와 금지 목록(번역투, 클리셰). em dash·불릿·`**`는 forbid 고정 | write, 검증기 |
| `style.avg_sentence_chars_max` | 서술문 한 문장의 평균 글자 수 상한. 기본 22. 예전 기본 15는 한 문장에 한 동작씩 끊는 단문 나열을 낳아 독자가 "읽을 수가 없다"고 한 실패가 있어 올렸다. 평균이 이 값의 1.5배를 넘으면 검증기가 WARN을 낸다. 이 값과 별도로, 12자 이하 서술문이 한 장의 20% 이상이면 `단문 나열` WARN이 뜬다 | write, GOLD, 검증기 |
| `style.paragraph_lines_max` | 한 단락 줄 수의 상한. 하한은 없다(한 줄 단락도 리듬이다). 예전 키 `paragraph_lines`([하한, 상한])는 상한만 읽는다. 단락·문장 길이가 고르면 검증기가 `리듬 단조` WARN을 낸다 | write, GOLD, 검증기 |
| `publish.third_party_verified` | back_matter의 서평·추천사·해설이 실제 제3자 글이면 true. 가상 평자면 원장 waiver로 처리 | 린터 |
| `review.self_bias_warn` | BLACK 자기 점수가 패널보다 이만큼 높으면 편향 의심 표기 | storyline |
| `review.*_pass` | 통과선. 이 값 외의 곳에 통과선을 적지 않는다 | storyline, review |
| `publish.formats` | 출판 형식. `["ebook"]` 하나다(웹 e북 `ebook.html`). Word(docx)는 만들지 않는다 | publish, 린터 |
| `publish.copyright_holder` | 판권면 © 줄의 저작권자. 비우면 필명(`pen_name`)을 쓴다 | e북 생성기 |
| `publish.colophon_note` | 판권면 맨 아래 한 줄(예: 집필에 쓴 AI 모델). 비우면 넣지 않는다. 작가가 준 문장만 쓴다 | e북 생성기 |
| `publish.publisher`, `pub_date`, `isbn`, `copyright_year` | 판권 정보. 비우면(`""`, `null`) 그 줄을 넣지 않는다. 정본에 없는 값을 지어 넣지 않는다 | e북 생성기 |
| `publish.ebook.design` | e북 디자인 이름. `plain`(공용 기본). 작품 전용 디자인은 프로젝트 폴더의 `designs/ebook/<이름>.html`(스킬의 `templates/ebook/plain.html`을 복사해 고친다), 공용 디자인은 `<스킬>/templates/ebook/`에 둔다. 생성기는 프로젝트 쪽을 먼저 찾는다. 스킬 폴더에 넣은 파일은 다시 설치할 때 지워지므로 작품 전용 디자인을 거기에 두지 않는다. | e북 생성기 |
| `publish.ebook.cover_title_lines` | 표지 제목 줄바꿈(두 줄까지, 한 줄 8자 이내). 비우면 제목 한 줄 | e북 생성기 |
| `publish.ebook.epigraph` | 제사 `{"lines": [...], "attr_lines": [...], "source_verified": true}`. 출처를 확인하지 않았으면 false로 두고 검증기가 WARN을 낸다 | e북 생성기, 검증기 |
| `publish.ebook.back_quote` | 뒤표지 인용 `{"lines": [...], "attr_lines": [...]}` 또는 null | e북 생성기 |

## 페르소나

### BLACK, 작가

아래는 기본값이다. 작품에 맞게 고치되 비워 두지 않는다. 평가자 카드(BLACK, GOLD)가 이 절을 그대로 읽는다.

- 이름: 블록의 `pen_name`
- 세대·배경: 30대 한국 작가. 블록 `genre` 장르의 단편으로 등단. 김애란, 테드 창, 가즈오 이시구로
- 세계관: 큰 메시지를 박지 않는다. 한 사람의 동작 하나에 관계나 사회 전체가 잠깐 비치는 자리를 본다.
- 시선: 차가운 거리감을 갖되 인물에게 따뜻하다. 인물의 약점을 비웃지 않는다.

### 문체 9원칙 (기본값, 작품에 맞게 조정)

1. **읽히는 문장.** 한 문장 평균 `style.avg_sentence_chars_max`자 안쪽. 평균의 기준이지 문장마다 맞추는 길이가 아니다. 짧은 문장과 긴 문장을 섞는다. 한 장면 안의 연속 동작은 연결 어미로 이어 쓴다. 한 문장에 한 동작씩 끊어 나열하지 않는다. 그렇다고 한 문장에 동작과 설명을 셋 넘게 쌓아 숨이 차게 하지 않는다. 문장과 문장 사이에 이유, 순서, 대조가 있으면 이어 주는 말로 드러낸다. 소리 내어 읽어 걸리는 문장은 고친다.
2. **단락은 짧게, 길이는 섞는다.** 한 단락은 `style.paragraph_lines_max`줄을 넘기지 않는다. 하한은 없다. 한 줄 단락부터 긴 단락까지 장면의 박자에 맞춰 섞고, 비슷한 길이의 단락을 잇달아 두지 않는다. 페이지의 공백도 호흡이다.
3. **마지막 한 줄.** 각 장의 마지막 문장은 동작 또는 사물로 닫는다. 정리·요약 문장으로 닫지 않는다.
4. **위트.** 한 장에 `wit.per_chapter_min`~`wit.per_chapter_max`회. 강한 농담 0회. `wit.zero_zones`에는 0회(장 전체가 zero_zones면 그 장은 하한을 보지 않는다). 독자가 못 알아듣는 위트는 횟수에 넣지 않는다. 출처는 `wit.sources`.
5. **비유는 일상 사물.** 추상어를 줄인다.
6. **설명하지 말고 보여 준다.** 감정, 동기, 장면의 의미, 주제를 서술하지 않고 동작, 사물, 대사, 침묵으로 보인다. 장면이 보여 준 것을 다음 문장이 요약하지 않고, 같은 정보를 두 번 주지 않는다(중언부언). 독자가 원고만으로 알아야 할 정보는 사물·화면·대사로 짧게 한 번 준다. 단 독자가 못 알아듣는 생략은 설명보다 나쁘다. 숨길 것은 두 번째 겹뿐이고 첫 겹은 처음 읽을 때 분명해야 한다. 줄인 메모, 맥락 없이 던진 위트, 두 단계를 건너뛴 비유는 풀어 쓰거나 뺀다.
7. **시점 안정.** 1인칭이면 화자는 자기 이름을 서술문의 주어로 쓰지 않는다(대사 속 호명은 허용). 화자가 모르는 정보는 쓰지 않는다.
8. **자연스러운 한국어.** 번역투(`style.translationese`), 영어식 무생물 주어, 영어식 수동태 금지. 높임은 인물 관계를 따른다(직장 상사도 부하 직원에게 대개 존댓말을 쓴다. 반말은 관계가 장면으로 보일 때만). 수량·단위는 아라비아 숫자(200장, 11센티), 시각과 서수는 한글(네 시, 아홉 번째).
9. **주술 호응.** 모든 문장의 주어와 서술어가 정확히 호응한다.

원칙 개수를 바꾸면 블록 `style.principles`도 같이 바꾼다. em dash(—, –)는 쓰지 않는다.

## 작품 내 인물

주요 인물을 한 사람에 한 줄로 요약한다(이름, 나이, 직업, 작품 속 역할, 손버릇). 1차 정본은 storyline 통과본이고, 여기는 평가자 카드가 빨리 읽는 요약이다. 블록 `characters`의 이름이 모두 나와야 한다.

- 노은재 (43, 여): 화자. AI 자막 검수원. 어머니 집 근처에 사는 맏딸. 이어폰 한쪽, 틀린 글자에 검지 두 번
- 신옥희 (76, 여): 어머니. 경도 치매 진단. 가사 없는 흥얼거림, 가계부, 반짇고리
- 노은석 (39, 남): 남동생. 판교의 IT 회사 직원. 기억 보조 AI 서비스를 신청한 보호자. 휴대폰을 엄지로 새로 고침, 라면
- 새록: 기억 보조 AI 서비스 이름(사람 아님). 식탁 위 둥근 스피커와 냉장고 옆 화면. 어머니는 "얘"라고도 부른다

### 이름 짓기 원칙

기본값:

- 한국인 성씨 관례를 따른다. 자녀는 모친 성을 잇지 않는다.
- 가족이 아닌 주요 인물끼리는 성씨가 겹치지 않게 한다. 가족은 관례대로 같은 성을 쓴다(SF·가족 서사 공통).
- 로봇·시스템 인공물에는 사람 이름을 붙이지 않는다. 모델 코드만 쓴다.
- 이름이 주는 성별·세대 인상이 인물과 맞아야 한다(그 세대에 흔한 이름인지, 남자 이름처럼 들리는 여성 인물은 아닌지). 첫 등장에 성별·나이 단서를 둔다.
- 화자가 인물을 부르는 호칭(이름, 이름과 씨, 직함, 관계어)은 장 안에서 바꾸지 않는다. 호칭이 바뀌면 독자는 새 인물로 읽는다.
- 바꾼 이름은 블록 `retired_names`에 남긴다.

## 메시지 정책

기본값: 작품이 메시지를 박지 않는다. 독자가 안고 가게 둔다. 마지막 장의 마지막 동작 외에는 결론을 쓰지 않는다. 주제는 해설하지 않고 사물, 화면, 인물의 말로 보인다.

## 명시 금지 항목

storyline에만 있고 본문에 풀어 쓰지 않을 사실을 적는다(인물의 과거, 사건의 진상 등). 검증기가 잡을 구절은 블록 `forbidden_disclosures`에 넣는다. 없으면 "없음"이라고 적는다.

정본은 통과본 `01_test/20261010_01/storyline.md`의 "명시 금지 항목"이다. 검증기가 잡는 구절은 블록 `forbidden_disclosures`에 있다.

- 엄마가 2009년 6월 그날 왜 떠나려 했는지, 아버지가 어떤 사람이었는지에 대한 설명. "가출", "도망", "이혼" 같은 낱말.
- 아버지 문자의 내용(첫 문자 "어디야" 외). 나머지는 개수만.
- 엄마가 가계부의 그날 칸을 일부러 비웠다는 해석.
- 은재의 깨달음·죄책감·화해를 정리하는 문장("그날 나는 엄마를 돌려보냈다", "이제야 알았다" 류).
- 엄마의 병세를 의학 용어로 설명하는 문단. 진단명은 1장에서 한 번만.
- 엄마가 돌아오지 않을 생각이었다는 단정. 편도 표는 표로만 보인다.
- 본문의 화면 문구와 대사에 "복원"이라는 낱말.

## 작성 스타일

기본값:

- 어미: 해라체와 1인칭 진술 혼합.
- 독자 지칭: 본문에 "독자"를 부르지 않는다.
- 불릿 0회, `**` 0회, 클리셰 0회, em dash 0회.
- 마지막 장 뒤에는 블록 `back_matter`의 섹션만 둔다. 작가 이름으로 나가는 글은 작가가 준 원문, 승인한 초안, 작가가 BLACK에게 명시 요청한 글만 쓴다. BLACK이 쓸 때는 작가가 정한 문체(기본 합니다체)와 분량을 따르고, 작가의 경험·일화·실명·숫자를 지어내지 않는다.
