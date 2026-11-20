# SUN RĀ vs KEVIN — fight preview (owner's preview order, 2026-10-19)

Owner's verbatim order (2026-10-19 ~00:39 CDT): *"Need to see this too with sun ra
and Kevin in a fight there and Mars floating in the sky in the background with
his planets."*

## The files

- `sunra-kevin-fight-still.png` — the money shot: Sun Rā mid-lunge with his
  jagged-tooth mouth open toward the viewer, bleeding-eye glow flaring, Kevin
  in a fighting lean facing him, Mars's giant cobalt head floating in the sky
  with the forehead portal + bleeding-eye glows, Jupiter / Saturn (+ring) /
  Neptune / Pluto visible on their inclined orbits around him. 960×540.
- `sunra-kevin-fight.mp4` — the full 12-second choreographed fight loop (H.264,
  960×540, 10fps): circle/weave → Kevin dash → Sun Rā mouth-first lunge →
  forced datamosh reality-shift mid-fight → exchange flurry → Kevin power-dash
  finale. Impact flashes, camera shake, FOV punch. No audio (frame-sequence
  capture).

## How it was made

Test harness `game/fight-preview.html` (kept in the stage work dir, not shipped):
loads the real `sunra` stage through the game's `Arena`, then adds the two
fighters and drives them with a procedural fight director. Money-shot camera
locks the fighters low-center and Mars + planets high. The datamosh shift is
triggered mid-fight through the stage's own `sunraDebug.forceShift()` hook —
what you see in the video is the real stage state machine, not a mockup.
Captured as 121 choreo-locked frames (?seq=1 stepped mode, canvas.toDataURL
per frame — no compositor dependence) and encoded to H.264.

## Honest flags

- **960×540, not 720p.** The capture box was at ~95% RAM with 6 other lanes'
  Blender renders running; 1280×720 crashed the Chromium tab. Re-capture at
  720p+ when memory frees.
- **Decimated preview models.** Sun Rā 56→14MB, Kevin 48→5.6MB (gltf-transform
  simplify 0.07) so the tab survives. Full-res Tripo GLBs stay in tripo-downloads.
- **Statics posed render-side.** Sun Rā's rig lane had not landed an animated
  GLB, so both fighters are posed whole-body (lunges, weaves, recoils, eye
  flare). No rigged animation — that rides with the auto-rig pass.
- Sun Rā's bleeding eyes = glow-sprite VFX (he never blinks, per canon) plus
  an animated blood drip from the mouth corner; the texture already bleeds.
- No music in the video. The stage def carries per-land `music` palettes as
  data; audio.js doesn't consume them yet (follow-up).
