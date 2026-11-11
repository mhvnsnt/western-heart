# Phase B proof — Megami, straight hair (megami-straight-v1)

**Read the verdict first.** The collision *core* is real and unit-proven
(11/11 + 7/7 tests, re-verified this lane). The *measured* AFTER numbers
below are also real. But this proof does **not** yet demonstrate the
owner's canonical case — hair resting on shoulders, pushed around by
them — because the part of the hair that is *visible* is not the part
that is *simulated*. Section 3 is the honest core of this record; the
numbers in section 2 must not be quoted without it.

## 1. What was run

- Stage: `proof-stage/stage8843.html` (standard dark stage: bg #14121c,
  hemi 1.15 / key 2.2 / fill 0.55 / rim 0.9, NeutralToneMapping 1.1,
  fov 35), deterministic 60 Hz stepping (3 substeps per captured frame,
  0.05 s/frame, 160 frames = 8.0 s of scripted motion: settle → head
  turn in/hold/return (yaw 0.55 rad) → torso sway → settle).
- Body: `megami-angel-pilot2-v5.glb` (the current v5 body; bundled hair
  hidden per the composition rule). Hair: the registered straight part
  `_hair-fit-20261109/glb/megami-hair-angel-straight.glb`.
- Collision data: `baked/megami-v5/` — header `bakedFrom =
  megami-angel-pilot2-v5.glb` (the current body; the stage's FACTS
  record `sdfBakedFrom` matches — this is the bake the runs used).
  `baked/megami/` is the older **v4** bake and still carries the buggy
  Spine2→Neck capsule r=1.1729 (v5 bake: fixed, r=0.2434) — do not use it.
- Measurement: every captured frame, the 19 simulated hair-chain joints'
  tips are sampled against the body SDF (`inside` = count with d < 0,
  `maxPenM`, `minDM` = nearest tip distance). Measurement is computed
  in-page from the SDF, never from pixels.

## 2. Measured results

### AFTER (collision core ON)
- Probe run (6 settle frames, t 0.05–0.30): **inside 0/19, maxPen 0,
  framesWithPenetration 0** (`summary-after.json`, archived copy in
  `run-archive/`).
- Full-motion run (this lane): **135 of 160 frames captured**
  (`probe-after/f000–f134`), then the renderer target crashed under box
  load (~28) and the run ended. Every logged sample (frames 0/20/40/60/
  80/100/120, spanning settle + head turn + sway) reads **inside 0/19,
  maxPen 0 mm**. `measures-after.json` on disk is still the probe-6
  file — the full run writes its measures only at completion, so no
  full-run measures file exists; the per-frame overlay text and the run
  log (`probe-after-full8.log`) are the surviving record. Nothing here
  is reconstructed or interpolated.
- Spot measures (diag9/diag11, settled stage): nearest simulated tip to
  the body surface **minD = +67.9 mm** (t=0.55) / **+68.5 mm** (t=1.55,
  head turn) — the tips are not merely non-penetrating, they never come
  within ~68 mm of the body at all. See section 3 for why.
- Video: `after.mp4` — the 135 landed frames at 20 fps (real-time),
  labelled as a partial run.

### BEFORE (legacy, head-sphere only)
- **Not run.** From ~19:10 CST onward every browser launch on this box
  died during page load (target crashed / browser closed; six attempts
  across diag12/diag12b, before and after clearing stale Chromium
  profiles). The BEFORE numbers are therefore **not measured** and are
  not estimated anywhere in this record.
- Design note (analysis, not data): BEFORE would measure the same 19
  tips against the same SDF (the SDF is the measurement oracle in both
  modes; legacy mode only removes it as a *collider*). Given the tip
  trajectories in section 3, BEFORE would very likely also read zero —
  which is precisely why this pair, as currently built, cannot
  discriminate. Do not quote an expected BEFORE number as a result.

## 3. Why this does not yet prove hair-on-shoulders (the honest core)

1. **The visible hair is not simulated.** The straight part's strand
   geometry is 2,573 independent cards (~80 verts each, max edge
   27.4 mm — measured offline from the GLB). The spring solver drives
   only the part's 19 guide bones (11 chains: back/left/right/bangs).
   ~43% of the strand mass (67,531 of 156,144 verts in the AngelBlack
   prim) is weighted to the `head` bone alone — a static shell co-moving
   with the head. In every captured frame the visible strands sit as a
   thin wisp layer at the crown; nothing long ever rests on a shoulder,
   in either mode, at any camera.
2. **The simulated tips never approach the body.** diag11 read the
   solver's world state directly (bind pose, after the 200-substep
   settle, and again after 11 stepped frames — identical): every
   chain's tip (`cur`) sits *above* its joint, along the authored bind
   direction (e.g. back1 joint y=1.492 → tip y=1.646; Left2 tip
   y=1.863 vs head joint 1.480). The solver pins each tip at the
   authored segment length along the bone's rest direction and the
   0.55 stiffness spring holds it near the animated pose; the chains
   cannot drape onto the shoulders from this configuration. Hence
   minD ≈ +68 mm everywhere and penetration 0 in both modes — true,
   and vacuous for the shoulder-contact claim.
3. **Camera.** The stage's default framing targets the chest (target
   y=1.19) and shows no hair at all. The validated framing for any
   re-shoot is the raised camera used by diag8/9/11
   (`&cx=0.36&cy=0.34&cz=0.85`, FACTS-recorded target y=1.19 at
   distance ~0.92): head, neck and shoulders in frame. A further
   target-lift experiment (`ty=0.10`) never got a page load (browser
   crash wall) and is **unvalidated**.

What a discriminating Phase B proof needs (next work, in order):
(a) simulate what is visible — strand-level sim, or bind the strand
cards to the guide chains with solver parameters that let the chains
actually fall (gravity vs stiffness balance, longer settle from a
draped initial state); (b) re-shoot BEFORE and AFTER at the validated
raised camera on the same deterministic motion; (c) only then quote a
penetration pair. The collision core itself (SDF projection, capsule
projection, PBD friction, self-collision, articulator coupling) is
unit-proven and is not the blocker — the hair *presentation* layer is.

## 4. Root-cause flag for the parent (export pipeline)

Both GLBs in this proof are Blender exports whose skin **surface sits
~0.19 below their own joint skeletons** (the offset lives in the IBMs;
mesh nodes are identity). Body: joints crown 1.6088, skin crown 1.4142
— sink 0.1946. The harness compensates by driving the hair part's whole
scene root **down by 0.1946** so its hairline sits on the *rendered*
skull; chains, colliders and the SDF all stay in the baker's (joint)
frame, which is self-consistent. The compensation is presentation-only.
**The root-cause fix belongs to the export pipeline** (meshes exported
~0.19 low vs their own IBMs) — flagged here, deliberately not fixed in
this lane. In-game, parts worn on this body need the same −0.1946 frame
shift (or the body export's root offset removed).

## 5. Presentation disclosures (never physics)

- Textures capped at 1024 px and material transmission disabled in the
  proof stage only (SwiftShader survival on a loaded box).
- Hair settles for 200 substeps (3.33 s) at bind pose before the
  captured run, both modes identically (`__facts.settleSubsteps=200`).
- Frames are captured via `canvas.toDataURL` (the stage sets
  `preserveDrawingBuffer:true`); CDP `Page.screenshot` repeatedly timed
  out under load and killed earlier runs. Capture path only — the sim
  and the SDF measurement are untouched.
- The in-page overlay label (mode / phase / measured counts) is a DOM
  element and is **not** burned into the canvas frames; video labels
  are added by ffmpeg instead.

## 6. Files

- `after.mp4` — AFTER video, 135/160 frames, 20 fps, labelled partial.
- `probe-after/` — the 135 AFTER frames (default camera).
- `measures-after.json`, `summary-after.json` — probe-6 AFTER (6f).
- `run-archive/` — preserved probe-6 measures/summary copies.
- `diag/`, `diag2/`, `diag7/`, `diag8/`, `diag9/`, `diag11/` — diagnostic
  stills + logs (diag8/9/11 = raised camera; diag11 = solver state dump).
- `probe-after-full8.log` — the full AFTER run log (crash at f135).
- No `before.mp4`, no `probe-before/`, no side-by-side: the BEFORE run
  does not exist yet (section 2). Nothing was fabricated to fill the gap.
