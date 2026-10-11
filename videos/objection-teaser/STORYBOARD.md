---
compositionId: objection-teaser
duration_s: 15.0 # == audiomap.audio.duration_sec
canvas: { w: 1920, h: 1080, fps: 30 }
style:
  font: "Noto Serif KR / Pretendard / JetBrains Mono"
  palette: ["#050505", "#F5F5F2", "#C8281E", "#8C8C88", "#0E0E0E"]
assets: "no user media; fonts in assets/fonts/; registry components in compositions/components/ (yt-screen-warp, scan-band, text-shimmer, rgb-glitch-text, beat-accent) as recipes to fork"
build_notes:
  - "one paused timeline per frame"
  - "no remote assets except the host's gsap"
  - "every frame carries the identical holo-layer + hud from frame.md, computed from TRACK time, so hard cuts read as one projection"
  - "@font-face for the three fonts inside each frame's <style>, url('assets/fonts/…')"
avoid: ["robot-logo orange", "em dash", "side accent bars", "generic slideshow", "tiny unreadable hero text", "spoiling the ending"]
---

<!-- Gestalt: 15.0s excerpt of Kevin MacLeod "The Way Out" (CC BY 4.0). A restrained pulse with
four accelerating snare rolls (1.56-3.06, 3.41-3.88, 5.32-6.83, 8.45-9.54), one big SURGE hit at
9.89s, ring-out decay, hard_stop at 12.24, silence 14.0-15.0. Rolls present → grid reliable.
Density arc: tense pulse ×2 phrases → HIT → decay → silence. -->

## Frame 1 — f1

- src: compositions/frames/01-f1.html
- duration: 3.88s
- span_sec: [0.0, 3.88]
- pacing: beat_cut
- mood: [tense, glitch]
- feel: steady kick pulse with an accelerating snare roll (1.56-3.06) and a short second roll (3.41-3.88) ending on a strong riser hit

### Groups

- **g1** — free_design
  - span_sec: [0.0, 3.88]
  - free_design: { dominant_system: "kinetic serif statement on a hologram projection, buried by red 기각 seals that accumulate on every roll hit, resolving to a locked counter", primitives: ["hard-cut", "kinetic-letter-in", "chromatic-split", "color-grid-shuffle", "counting-punch"], density_topology: "accumulate then lock" }
  - anchors: [0.05, 1.21, 1.56, 1.76, 1.86, 2.16, 2.39, 2.60, 2.72, 2.83, 2.97, 3.06, 3.41, 3.67, 3.88]
  - copy:
    - "2032년, 서울." (label scale, lands on 0.05 with the holo-layer boot: scanlines flash on, hud hairline draws)
    - "AI가 판정하고" (hero serif, white, slams on 0.05 kick; chroma-hit)
    - "사람은 도장을 찍는다." (hero serif on 1.21 kick, second line; the word 도장 in seal red)
    - "기각" seal-imprints: one per roll hit 1.56→3.06 (10 hits). They land around and then over the two lines, random-but-seeded positions and rotations, growing denser, so the statement is buried under the stamps. Each lands with a 0ms set + 2-frame scale 1.08→1.0 squash.
    - counter (data mono, bottom right above the hud line): "날인 000" counting to "날인 200" across the roll, locking exactly on 3.06 with a punch
    - "하루 200장." (hero serif, white, hard cut on 3.06: stamps clear in one frame, only this line + the locked counter remain; 3.41-3.88 roll = small chroma flicker on the line, no new copy)

## Frame 2 — f2

- src: compositions/frames/02-f2.html
- duration: 2.95s
- span_sec: [3.88, 6.83]
- pacing: beat_cut
- mood: [tense, cinematic]
- feel: riser hit opens a quieter bar, two strong kicks (4.95, 6.13) with a snare roll (5.32-6.83) between and after them

### Groups

- **g1** — free_design
  - span_sec: [3.88, 6.83]
  - free_design: { dominant_system: "a holographic application form tilted in 3D space; eight ghost sheets stacked behind it each wearing a red 기각 seal; one handwritten line written onto the form in two beats", primitives: ["3d-card-flip", "staggered-reveal", "mask-reveal", "chrome-sweep", "content-swap"], density_topology: "one focal object, layers behind" }
  - anchors: [3.88, 4.23, 4.71, 4.95, 5.32, 5.53, 5.62, 5.90, 6.13, 6.36, 6.57, 6.71]
  - copy:
    - on 3.88: hologram form flips in (rotateY into a resting tilt of about -10deg, perspective 1800px), ground-raise panel with ink-faint hairline rows. Form header label: "이의신청서 · 9번째". Field rows (system/label scale): "신청인  조옥순 (79)", "이전 결정  기각 8건".
    - 4.23, 4.71: the eight ghost sheets fan out behind the form (4 on 4.23, 4 on 4.71), each a faint outline with a small red 기각 seal-imprint. Texture only.
    - field label "이유" above an empty ruled line, visible from 3.88.
    - on 4.95: "제 점수 말고" written onto the ruled line (hand style, pencil-stroke wipe left to right, per-glyph rotation jitter of about ±1.2deg seeded by index)
    - on 6.13: "제 집을 봐 주세요." written on the second ruled line, same treatment; holo-sheen sweeps across both lines right after it lands. This sentence is the book's line; spell it exactly.
    - roll 5.32-6.83: texture only. Faint mono digit columns behind the form scramble per hit (no meaningful numbers, no claimed score). Do not move the handwritten words.

## Frame 3 — f3

- src: compositions/frames/03-f3.html
- duration: 5.41s
- span_sec: [6.83, 12.24]
- pacing: beat_cut
- mood: [tense, cinematic]
- feel: two kicks into a strong downbeat, an accelerating roll (8.45-9.54) that builds into one big SURGE hit at 9.89, then a long ring-out decay to the hard stop

<!-- REVISED per user: "책 마지막 내용을 키네틱 타이포로 흥미진진하게". Frames 3-4 now tell chapter 4 (결정) in kinetic type,
using the book's own sentences (docs/objection/ebook.html, 4장). The ending is shown on purpose (author's request).
Canon: the stamp is lowered to just above the paper and held; as the hand withdraws, one edge of the seal tilts and grazes the
MARGIN leaving ONE RED HALF-MOON MARK (붉은 반달 자국). There is NO falling ink drop. The 날인란 stays empty. -->

### Groups

- **g1** — free_design
  - span_sec: [6.83, 9.89]
  - free_design: { dominant_system: "office desk on a hologram plane: a 결정서 with an empty 날인란, an open 인주 통; the team lead's lines and the question land as kinetic serif type on the kicks; during the roll the stamp plunges toward the 날인란, trembling", primitives: ["hard-cut", "kinetic-letter-in", "chromatic-split", "screen-shake", "dolly-zoom"], density_topology: "build" }
  - anchors: [6.83, 7.17, 7.41, 7.50, 8.01, 8.08, 8.45, 8.71, 8.80, 9.06, 9.17, 9.27, 9.38, 9.54, 9.59]
  - copy (v2, 2026-10-05: the author cut the lead's lines and the child question):
    - on 6.83: "처리기한 마지막 날." (hero 120px, white, slam + chroma; second chroma beat on 7.50). Holds to 8.45. The desk plane + 결정서 (empty 날인란) + open 인주 통 are visible from 6.83; 8.01/8.08 texture only.
    - on 8.45 (roll start): hard cut → "인주를 묻힌 도장을" (hero 120px) as the stamp enters from above; holds to 9.89.
    - 9.06 / 9.17 / 9.27 / 9.38: "종이에 닿기 직전까지." builds under it in chunks (canon: "인주를 묻힌 도장을 종이에 닿기 직전까지 내렸다."). Holds to 9.89.
    - 8.45-9.89: the stamp descends toward the box, accelerating; screen-shake 2→8px on 8.71-9.59.
- **g2** — free_design
  - span_sec: [9.89, 12.24]
  - free_design: { dominant_system: "freeze on the hit; the stamp held a hair above the empty 날인란; as it withdraws one edge grazes the margin leaving a red half-moon; the last sentence assembles word by word", primitives: ["freeze-hold", "flash-cut", "chromatic-split", "kinetic-letter-in"], density_topology: "collapse to one mark" }
  - anchors: [9.89, 12.24]
  - copy:
    - on 9.89: 0ms freeze. The stamp face hangs about 14px above the empty nalin-box, glow not touching the paper. One white flash (0.85 → 0 over 3 frames) + chroma-hit on the whole stage. "그대로 들고 있었다." (hero serif, white) slams in on the hit and holds to about 10.55. Nothing else moves for ~0.3s (timecode and scanline drift freeze too).
    - about 10.55: the stamp tilts slightly as it withdraws upward; one edge grazes the paper MARGIN outside the box and leaves ONE red half-moon mark (a seal-red crescent, ink-textured, about 60-80px). The 날인란 stays empty. Text cuts to "날인란은 비어 있었다." (hero serif, white) holding to about 11.35.
    - about 11.35-12.1: the text cuts and "나는 도장을 찍지 않고" assembles word by word (나는 · 도장을 · 찍지 않고), large serif, white, center, each word snapping in with a short settle; holds into the frame end. No falling ink drop anywhere.

## Frame 4 — f4

- src: compositions/frames/04-f4.html
- duration: 2.76s
- span_sec: [12.24, 15.0]
- pacing: beat_cut
- mood: [cinematic, aggressive]
- feel: hard stop kick (12.24) then sparse fading kicks (13.14, 13.58) and silence from 14.0 to the end

### Groups

- **g1** — free_design
  - span_sec: [12.24, 13.14]
  - free_design: { dominant_system: "the drawer slam: the whole frame shuts like a drawer on the hard-stop kick while the book's last words land", primitives: ["system-replace", "braam-punch", "screen-shake", "chromatic-split"], density_topology: "slam then hold" }
  - anchors: [12.24]
  - copy:
    - frame starts on "나는 도장을 찍지 않고" in the same position/size F3 left it (continuity), and on 12.24 exactly: "서랍을 닫았다." slams in below it (hero serif, white, bigger weight), while a drawer front (near-black #0E0E0E slab with a 1px ink-faint top edge and a small white hairline handle slot) slams up from the bottom and stops with a hard thunk at about 45% of the frame height, overshoot 0, screen-shake 10px decaying in ~0.25s, chroma-hit. The full last line "나는 도장을 찍지 않고 서랍을 닫았다." is readable together and holds until 13.14.
- **g2** — free_design
  - span_sec: [13.14, 15.0]
  - free_design: { dominant_system: "end card held in negative space; the empty 날인란 with the single red half-moon mark in its margin as the book's mark", primitives: ["hard-cut", "negative-space-hold", "spotlight-sweep"], density_topology: "hold" }
  - anchors: [13.14, 13.58, 14.0]
  - copy:
    - on 13.14: hard cut to the end card (the existing end-card layout). Left: title "이의신청" (title style, white). Under it, system style ink: "2032년, AI가 판정하고 사람은 도장을 찍는다." Under that, label ink-dim: "AI ROASTING 단편 소설 · 웹 e북".
    - right side: a small nalin-box, EMPTY, with ONE red half-moon mark in its margin (callback; replaces the old ink-drop splat). Box label "날인" in seal red.
    - 13.58: one slow spotlight/holo-sheen sweep across the title (about 0.8s), no new content.
    - credit line, bottom right, label scale, ink-dim, visible from 13.14: "MUSIC  \"THE WAY OUT\" KEVIN MACLEOD (INCOMPETECH.COM) · CC BY 4.0"
    - 14.0-15.0 silence: everything holds still; the hud progress line reaches the end exactly at 15.0.

<!-- ===================================================================================
2026-10-05 · 30초판. 이 파일의 Frame 1-4는 15초판(index-15s.html)이다. 30초판 계획은
versions/30s/STORYBOARD.md 에 있다. 15초판 루트 index는 versions/15s/index.html (assemble/validate 는 그 파일을 --storyboard 로 받는다).
==================================================================================== -->
