---
version: alpha
name: Objection Seal — Frame (video / frame layer)
description: >
  『이의신청』 책 표지·e북에서 가져온 브랜드를 영상 프레임용으로 옮긴 스펙. 프리셋 중에 블랙·화이트·인장 주홍
  조합이 없어 책 디자인(docs/objection/ebook.html, docs/index.html의 --seal, --holo-ink, 날인란 SVG)을
  정본으로 삼는다. 사용자 지시: "블랙 화이트 + 인장의 색깔을 테마로", "로봇 주황 쓰지 말 것",
  "키네틱 텍스트 + 홀로그래픽".
unit: the frame — 1920×1080
principle: black ground · white type · seal red is the ONLY color · holography is light, not paint

colors:
  ground: "#050505"        # 화면 바탕. 순수 #000 대신 이것
  ground-raise: "#0E0E0E"  # 패널, 문서 면
  ink: "#F5F5F2"           # 본문 흰색 (종이 흰색)
  ink-dim: "#8C8C88"       # 보조 문구
  ink-faint: "rgba(245,245,242,0.14)"  # 헤어라인, 그리드
  seal: "#C8281E"          # 인장 주홍. 유일한 유채색
  seal-glow: "rgba(200,40,30,0.55)"
  # 홀로그램 빛 (채움색으로 쓰지 않는다. 흰 글자 위를 지나가는 빛줄기, 히트 순간의 색수차에만)
  holo-cyan: "rgba(160,235,255,0.55)"
  holo-pink: "rgba(255,170,225,0.45)"
  holo-violet: "rgba(201,184,255,0.45)"
  split-red: "rgba(255,40,40,0.85)"
  split-cyan: "rgba(0,220,255,0.85)"

typography:
  # 글꼴 파일은 assets/fonts/ 에 있다 (KS X 1001 한글 2,350자 + ASCII 서브셋, 가변 굵기).
  #   @font-face { font-family:"Noto Serif KR"; src:url("assets/fonts/NotoSerifKR.woff2") format("woff2"); font-weight:200 900; }
  #   @font-face { font-family:"Pretendard"; src:url("assets/fonts/Pretendard.woff2") format("woff2"); font-weight:45 930; }
  #   @font-face { font-family:"JetBrains Mono"; src:url("assets/fonts/JetBrainsMono.woff2") format("woff2"); font-weight:100 800; }
  # 경로는 루트 index.html 기준 (서브 컴포지션은 호스트에 복제된다).
  title:    { fontFamily: "Noto Serif KR", px: 240, weight: 900, lineHeight: 0.92, tracking: "-0.06em" }
  hero:     { fontFamily: "Noto Serif KR", px: 150, weight: 800, lineHeight: 1.0, tracking: "-0.045em" }
  headline: { fontFamily: "Noto Serif KR", px: 96,  weight: 700, lineHeight: 1.1, tracking: "-0.03em" }
  hand:     { fontFamily: "Noto Serif KR", px: 112, weight: 500, lineHeight: 1.15, tracking: "-0.02em" }  # 손글씨 한 문장
  system:   { fontFamily: "Pretendard", px: 40, weight: 300, lineHeight: 1.3, tracking: "-0.01em" }
  label:    { fontFamily: "JetBrains Mono", px: 18, weight: 500, tracking: "0.22em", upper: true }
  data:     { fontFamily: "JetBrains Mono", px: 64, weight: 300, tracking: "-0.02em" }

components:
  holo-layer:
    description: >
      모든 프레임에 똑같이 깔리는 홀로그램 투사면. 프레임 사이 하드컷이 한 작품으로 읽히게 하는 장치다.
      (1) 스캔라인: repeating-linear-gradient(0deg, rgba(245,245,242,0.035) 0 1px, transparent 1px 4px), 전체 화면,
          트랙 시간 t에 따라 background-position-y = (t*24)px 로 천천히 흐른다 (프레임 로컬이 아니라 트랙 시간 기준).
      (2) 비네트: box-shadow inset 0 0 240px rgba(0,0,0,0.85).
      (3) 미세 그레인: 고정 seed SVG feTurbulence, opacity 0.06.
      출처: compositions/components/yt-screen-warp.html 의 .yt-screen-fx 를 위 값으로 조정.
  hud:
    description: >
      모든 프레임 공통 크롬. 위치·크기 고정 (하드컷 때 흔들리지 않게).
      위 헤어라인 y=84px, 좌우 여백 96px, 1px ink-faint.
      왼쪽 위 (x=96, y=48): label "OBJECTION · 이의신청" ink-dim.  오른쪽 위 (right=96, y=48): label "2032 · SEOUL" ink-dim.
      아래 진행선: y=1012px, x=96..1824, 높이 2px. 바탕 ink-faint, 위에 seal 색 막대 width = (트랙 t / 15.0) * 1728px.
      프레임마다 자기 구간의 트랙 시간으로 계산해 이어지게 한다.
      왼쪽 아래 (x=96, y=1032): label 트랙 시간 "00:00.00" 형식 mono (ink-dim). t는 트랙 시간.
  holo-sheen:
    description: >
      흰 히어로 글자 위를 지나가는 무지갯빛 빛줄기. 글자 복제본에 linear-gradient(115deg, transparent 30%,
      #ffffff 42%, holo-cyan 47%, holo-pink 52%, holo-violet 56%, transparent 68%)를 background-clip:text 로 입히고
      background-position을 가로질러 한 번 쓸고 지나간다. 0.5~0.9s. 출처: compositions/components/text-shimmer.html.
      채움색으로 남기지 않는다. 지나간 뒤 글자는 다시 순수 ink.
  chroma-hit:
    description: >
      강박(kick/strong)과 SURGE에서만. 글자 복제 두 장(split-red, split-cyan)을 좌우 4~12px 벌렸다가 2~4프레임 뒤
      0으로. 출처: compositions/components/rgb-glitch-text.html, scan-band.html.
  seal-imprint:
    description: >
      인장 자국. 정사각 테두리 seal 색, 굵기 = 한 변의 4%, 안쪽 2.5% 지점에 점선 사각 (책 표지 날인란과 같은 결).
      안에 Noto Serif KR 900 seal 색 글자 (예: "기각"). 잉크 질감은 고정 seed feTurbulence + feDisplacementMap(scale 3~5)로
      가장자리를 거칠게. 회전은 인덱스로 정한 -9°~+9°. opacity 0.92.
  nalin-box:
    description: >
      날인란. 흰 헤어라인 정사각 (1.5px ink), 안쪽 점선 사각, 위에 label "날인" seal 색 (책 SVG와 같다: 2.4px 실선 + 1px 점선).
  stamp:
    description: >
      도장. 옆에서 본 원기둥 손잡이(흰 홀로그램 와이어프레임: 1.5px ink 윤곽 + 수평 스캔 해칭) 아래에 seal 색으로 채운 인면(印面).
      인면 아래쪽 가장자리에 seal-glow 번짐.

do:
  - 한 화면에 유채색은 seal 하나만. 홀로그램 빛(시안·핑크·바이올렛)은 움직이는 빛줄기와 히트 순간 색수차에만, 0.9s 이하.
  - 메시지 문장은 최소 1비트 이상 정지해 읽히게.
  - 하드 히트는 0ms set. 이징으로 타격을 죽이지 않는다.
dont:
  - 로봇 로고 주황 계열 (#C04800~#E08000) 금지.
  - 줄표(—) 금지. 쉼표와 마침표를 쓴다.
  - 카드나 문구 옆 세로 색 막대(왼쪽 강조선) 금지.
  - 위원회 결과와 남편 이야기는 꺼내지 않는다. 4장 결말(찍지 않고 서랍을 닫는다)은 작가 요청으로 보여 준다.
---
