---
compositionId: objection-teaser-30s
duration_s: 30.0 # == versions/30s/audiomap.json audio.duration_sec
canvas: { w: 1920, h: 1080, fps: 30 }
style:
  font: "Noto Serif KR / Pretendard / JetBrains Mono"
  palette: ["#050505", "#F5F5F2", "#C8281E", "#8C8C88", "#0E0E0E"]
assets: "no user media; fonts in assets/fonts/; 15s-version frames in compositions/frames/ are the visual reference and may be forked"
build_notes:
  - "one paused timeline per frame"
  - "every frame carries the identical holo-layer + hud from frame.md computed from TRACK time over a 30.0s track (progress = t/30*1728, timecode 00:00.00 → 00:30.00)"
  - "@font-face for the three fonts inside each frame's <style>, url('assets/fonts/…')"
  - "namespace every id with the frame prefix; style elements by their own ids/classes (descendant selectors that start with #stage[...] do NOT match once cloned into the host)"
  - "readability rule for this version: every message line holds at least ~0.16s per syllable + 0.3s"
avoid: ["robot-logo orange", "em dash", "side accent bars", "lines that vanish before they can be read"]
---

<!-- Music: Kevin MacLeod "The Way Out" (CC BY 4.0), spliced on its 7.5s cycle: source 27.65-42.65 + 57.65-72.65.
0-15s = the driving section (dense sustained snare fill, HIGH 2-5 and 9-10, SURGE 8, VOID 7-8 and 13-14).
15-30s = identical to the 15s version shifted +15s: pulse, rolls 15.97-18.76 / 19.71-22.50 / 23.45-24.89,
SURGE hit 24.89, hard_stop 27.24, silence 29-30.
Story: 1장 접수 → 2장 → 3장 현장 → 4장 결정 (the ending, shown on purpose at the author's request).
Canon lines are quoted from docs/objection/ebook.html and docs/index.html. -->

## Frame 1 — 31-f1

- src: compositions/frames-30s/31-f1.html
- duration: 7.0s
- span_sec: [0.0, 7.0]
- pacing: beat_cut
- mood: [tense, glitch]
- feel: dense driving snare fill from the first kick, HIGH energy 2-5, one strong hit at 4.95, settling toward a silence at 7.0

### Groups

- **g1** — free_design
  - span_sec: [0.0, 7.0]
  - free_design: { dominant_system: "fork of 15s frame 01-f1: kinetic serif statement on the hologram projection, buried by red 기각 seals on every hit, resolving to a locked counter and a held line", primitives: ["hard-cut", "kinetic-letter-in", "chromatic-split", "color-grid-shuffle", "counting-punch"], density_topology: "accumulate then lock then hold" }
  - anchors: [0.05, 0.70, 1.30, 1.53, 1.86, 2.00, 2.37, 2.58, 2.72, 2.83, 2.95, 3.41, 3.88, 4.23, 4.46, 4.62, 4.95, 5.39, 5.76, 6.13, 6.46, 6.80]
  - copy:
    - 0.05: holo-layer boot; label "2032년, 서울."; hero "AI가 판정하고" slams in (chroma-hit). Holds.
    - 1.30: hero second line "사람은 도장을 찍는다." (도장 in seal red). Both lines readable alone until 2.00.
    - 2.00 → 4.62: one red "기각" seal-imprint per hit (2.00, 2.37, 2.58, 2.72, 2.83, 2.95, 3.41, 3.88, 4.23, 4.46, 4.62), burying the statement; counter "날인 000" climbing toward 200.
    - 4.95: counter locks "날인 200" with a punch; hard cut clears the seals and statement; hero "하루 200장." Holds to 7.0.
    - 5.39: label line above it, ink-dim: "9년차 심사관 한서진" (canon). 5.76, 6.46: tiny chroma flickers only.

## Frame 2 — 32-f2

- src: compositions/frames-30s/32-f2.html
- duration: 6.0s
- span_sec: [7.0, 13.0]
- pacing: beat_cut
- mood: [tense, cinematic]
- feel: a one-beat silence (7-8), SURGE at 8 with a strong snare at 8.80, HIGH 9-10 with kicks 9.15-9.50, then energy falls away (DROP 10, LOW 12, silence from 13)

### Groups

- **g1** — free_design
  - span_sec: [7.0, 13.0]
  - free_design: { dominant_system: "fork of 15s frame 02-f2: the holographic 9th application form with eight 기각 ghost sheets; the handwritten sentence written in two beats; then the hand stops", primitives: ["3d-card-flip", "staggered-reveal", "mask-reveal", "chrome-sweep", "hard-cut"], density_topology: "one focal object, then collapse to one line" }
  - anchors: [7.62, 7.92, 8.20, 8.80, 9.03, 9.15, 9.36, 9.50, 10.45, 11.38, 12.79]
  - copy:
    - 7.0-7.62: projection flickers on in the silence; on 7.62 the form flips in. Header "이의신청서 · 9번째"; rows "신청인  조옥순 (79)", "이전 결정  기각 8건"; field "이유".
    - 7.92, 8.20: ghost sheets fan out behind (4 + 4), each with a small red 기각 seal.
    - "제 점수 말고": pencil-stroke write completing ON 8.80.
    - "제 집을 봐 주세요.": write starting ~9.03, completing ON 9.36; holo-sheen sweep across both lines ~9.5-10.1. Both lines hold, untouched, until 11.38 (≈2s of reading time).
    - 11.38: hard cut; the form dims to 25% and drifts back; hero "손이 멈춘다." (canon: "…신청서 한 장에서 손이 멈춘다.") holds to 13.0. 12.79: a tiny push (scale 1.0→1.015).

## Frame 3 — 33-f3

- src: compositions/frames-30s/33-f3.html
- duration: 6.71s
- span_sec: [13.0, 19.71]
- pacing: beat_cut
- mood: [cinematic, tense]
- feel: near-silence with sparse kicks (13.26 strong), a restrained pulse from 15.0, an accelerating snare roll 15.97-18.76 that stays quiet, sparse hits 18.67 and 19.23

### Groups

- **g1** — free_design
  - span_sec: [13.0, 17.39]
  - free_design: { dominant_system: "rain on the hologram, then a wall where pencil water lines climb one per roll hit while a translucent water band rises from the bottom", primitives: ["hard-cut", "staggered-reveal", "kinetic-letter-in"], density_topology: "build" }
  - anchors: [13.26, 13.40, 14.33, 15.0, 15.97, 16.21, 16.77, 16.86, 17.16]
  - copy:
    - 13.26: hard cut to rain: thin white diagonal streaks falling across the frame (seeded, seek-safe, 20-35% opacity, no color). Hero "토요일, 장맛비." holds to ~15.0.
    - 14.33: label under it, ink-dim mono/Pretendard: "규정은 현장 방문을 금지한다." (canon)
    - 15.0: the rain thins; hard cut to a dark wall plane. Hand-drawn pencil water lines (ink 35-60%, 1.5px, slightly uneven, each with a tiny illegible pencil tick at the right end, no real dates/numbers) appear one per hit 15.0, 15.97, 16.21, 16.77, 16.86, each higher than the last; a translucent grey water band rises from the bottom underneath them, stopping just under the lowest line. Hero "벽에는 연필로 그은 수위선." lands on 15.0 and holds to 17.39 (top-left).
- **g2** — free_design
  - span_sec: [17.39, 19.71]
  - free_design: { dominant_system: "the twist: the 2027 survey copy as a white hologram sheet; a round red seal glows in its 조사자 날인란", primitives: ["3d-card-flip", "chromatic-split", "outline-to-fill"], density_topology: "reveal one mark" }
  - anchors: [17.39, 18.07, 18.67, 19.23]
  - copy:
    - 17.39: hard cut; a white hologram document slides/tilts in: label header "2027년 5월 현장 조사서" ; one row "판정  양호" with a hand-drawn circle around 양호; a small field "조사자 날인" with an empty ROUND frame.
    - 18.07: a ROUND red seal-imprint appears in that frame (seal red, ink-textured, the three syllables "한서진" inside the ring, ~120px) with chroma-hit; hero "내 도장이었다." (white) lands at the same time and holds to 19.71.
    - 18.67, 19.23: no new copy; the seal glow pulses once each, very slightly.

## Frame 4 — 34-f4

- src: compositions/frames-30s/34-f4.html
- duration: 7.53s
- span_sec: [19.71, 27.24]
- pacing: beat_cut
- mood: [tense, cinematic]
- feel: accelerating roll 19.71-22.50 with hard stops at 20.53 and 21.36, a strong snare at 21.83, a sustained fill 23.45-24.89 into the big SURGE hit at 24.89, then a long ring-out to the hard stop

### Groups

- **g1** — free_design
  - span_sec: [19.71, 24.89]
  - free_design: { dominant_system: "fork of 15s frame 03-f3 g1 (desk plane, 결정서 with an empty 날인란, open 인주 통, the stamp), re-timed with more reading time", primitives: ["hard-cut", "kinetic-letter-in", "chromatic-split", "screen-shake", "dolly-zoom"], density_topology: "build" }
  - anchors: [19.71, 19.95, 20.53, 21.36, 21.83, 22.41, 23.01, 23.45, 23.71, 24.06, 24.38, 24.54]
  - copy:
    - 19.71: desk scene visible. headline ink-dim "처리기한 마지막 날, 오후 네 시."
    - 19.95: hero "“서진 씨,”"
    - 20.53: hero "“찍고 퇴근하세요.”" (slam + chroma). Holds to 21.83.
    - 21.83: hard cut → hero "“이 집 애한테는 뭐라고 해요?”" (two lines) holds to 23.71 (≈1.9s). The stamp enters from above at 21.83 and descends slowly; from 23.45 it accelerates with the fill; screen-shake 2→8px on 23.71-24.54.
    - 23.71: the question cuts; "종이에 닿기 직전까지." builds in chunks on 23.71 / 24.06 / 24.38 / 24.54, holds to 24.89.
- **g2** — free_design
  - span_sec: [24.89, 27.24]
  - free_design: { dominant_system: "fork of 15s frame 03-f3 g2 (freeze, hover above the EMPTY box with its shadow, withdraw, margin graze → one red half-moon, last sentence word by word)", primitives: ["freeze-hold", "flash-cut", "chromatic-split", "kinetic-letter-in"], density_topology: "collapse to one mark" }
  - anchors: [24.89, 27.24]
  - copy:
    - 24.89: 0ms freeze, stamp hovering above the EMPTY 날인란 with its shadow on the box (keep the 15s fix: FREEZE_Y pose + box shadow). White flash + chroma. Hero "그대로 들고 있었다." holds to 25.70.
    - 25.70: text → "날인란은 비어 있었다." holds to 26.45; the stamp withdraws left, tilts, comes down onto the margin and grazes it at ~25.95 leaving ONE red half-moon; then lifts out.
    - 26.45 / 26.70 / 26.95: "나는 · 도장을 · 찍지 않고" word by word, centered, center y=440, Noto Serif KR 700 120px -0.03em (exactly the 15s position, so frame 5 continues it). Holds to the frame end.

## Frame 5 — 35-f5

- src: compositions/frames-30s/35-f5.html
- duration: 2.76s
- span_sec: [27.24, 30.0]
- pacing: beat_cut
- mood: [cinematic, aggressive]
- feel: hard stop kick (27.24) then sparse fading kicks (28.14, 28.58) and silence from 29.0 to the end

### Groups

- **g1** — free_design
  - span_sec: [27.24, 28.14]
  - free_design: { dominant_system: "fork of 15s frame 04-f4 g1: the drawer slam on the hard-stop kick", primitives: ["system-replace", "braam-punch", "screen-shake", "chromatic-split"], density_topology: "slam then hold" }
  - anchors: [27.24]
  - copy:
    - "나는 도장을 찍지 않고" continues from frame 4; on 27.24 "서랍을 닫았다." slams in on the drawer front. Holds to 28.14.
- **g2** — free_design
  - span_sec: [28.14, 30.0]
  - free_design: { dominant_system: "fork of 15s frame 04-f4 g2: end card with the empty 날인란 and the red half-moon", primitives: ["hard-cut", "negative-space-hold", "spotlight-sweep"], density_topology: "hold" }
  - anchors: [28.14, 28.58, 29.0]
  - copy:
    - 28.14: end card: "이의신청" / "2032년, AI가 판정하고 사람은 도장을 찍는다." / "AI ROASTING 단편 소설 · 웹 e북"; empty 날인란 + red half-moon; credit "MUSIC  \"THE WAY OUT\" KEVIN MACLEOD (INCOMPETECH.COM) · CC BY 4.0". Sweep around 28.58; still through 29-30; progress line full at 30.0, timecode "00:30.00".
