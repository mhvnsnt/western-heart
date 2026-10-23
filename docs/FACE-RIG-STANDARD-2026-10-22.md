# WH Face Rig Standard (2026-10-22)

Canonical facial animation standard for Western Heart characters. Follows the
DOA/SF/Tekken teardown research (`~/workspace/jiggle-face-hands-teardown.md`).

## Teardown verdict: Tekken 7 uses MORPH TARGETS, zero face bones

- **[FILE]** The Tekken-derived 53-joint skeleton (verified in
  `roster/pantera/attires/leopard-king/model-rigged.glb` and
  `roster/mariposa/attires/monarch/mariposa-monarch-rigged.glb`) has only
  `Neck → Head`. **No jaw, eyelid, brow, or tongue bones exist.** Tekken 7
  ships UE4 morph targets (blend shapes / glTF `targets`) driven by
  animation curves — intros, win poses, rage-art close-ups. In-fight faces
  are largely static (the camera is far); expression work concentrates on
  intros/outros/customization.
- **[PUB]** SFV (UE4) uses the same morph-target pipeline. Capcom's house bar
  is ~134 expressions/character on RE Engine — WH needs the fighting-game
  subset first, not the film set.
- **[FILE]** WH rigged models today have **zero morph targets AND zero face
  bones** — faces are completely static. This is the biggest facial-rig gap
  vs. all three reference games.

### Alternate evidence (documented, not adopted)
WWE WrestleMania XIX's teardown
(`teardown/wwe-wrestlemania-xix/docs/wrestler-skeleton-000.json`) shows a
12-bone face rig (lip/tooth/eyelid/brow bones). WH follows the Tekken/SFV
morph approach instead — it matches the 53-joint shared skeleton the whole
roster already uses, and keeps face work in the mesh where the Tripo intake
models already have the geometry. The jiggle bake driver still guards any
legacy face bones via `face_guard` tokens (belt and braces), but no NEW rig
gets face bones.

## WH standard: morph-target faces

1. **No face bones on new rigs.** The skeleton stays at 53 joints
   (Neck → Head, nothing more). Face work = glTF morph targets.
2. **Canonical morph MVP set** (10 morphs — fighting-game needs):
   `blink_L`, `blink_R`, `jawOpen`, `browUp`, `browDown`, `mouthSmile`,
   `mouthFrown`, `mouthOpen`, `eyesWide`, `eyesSquint`.
   Canonical names/roles live in `tools/auto_rig/backends/face_morphs.json`.
   Per-character extras are allowed (e.g. Dorowani's creature mouth) but the
   MVP 10 are mandatory on every humanoid face — intro interactions, win
   poses, and hit reactions all key them by name.
3. **Blink system:** automatic timer — blink every 3–6 s (randomized),
   150 ms close-open on `blink_L`/`blink_R`, plus forced blink on hit
   reactions. Morph-driven; runs in-game and in cutscenes.
4. **Lip-sync:** follow Tekken — fights use text UI for win quotes, not
   phonemes. `jawOpen` + `mouthOpen`/`mouthSmile`/`mouthFrown` on simple
   open/close curves is the first pass for cutscenes and Dorowani's voice
   moments (win poses/taunts/intros). A full phoneme/viseme system is built
   ONLY when story-mode cutscenes need it — not before.
5. **Hit reactions / win poses / taunts:** expression = morph weights keyed
   on the same animation as the body — never a separate track. Multiple
   varied intro interactions per matchup (owner directive 2026-10-22) reuse
   these morph poses; names must be stable across attires.
6. **Intake rule:** if a source model ships blend shapes, map them to the
   canonical names where they match; otherwise sculpt the MVP 10 at intake.
   Never bake face animation into bone transforms on new rigs.

## Pipeline wiring
- `tools/auto_rig/backends/face_morphs.json`: canonical morph names/roles.
- Intake backends must verify the MVP 10 morphs exist (or are sculpted) —
  `validate.py` gains a `face_morphs_present` informational check.
- `tools/jiggle/wiggle2_jiggle.py` `face_guard`: unchanged — protects any
  face bones on legacy rigs (e.g. Scarlett/Star Rigify rigs) from jiggle
  bakes; hash-verified before/after every bake.
- Runtime: blink timer + morph driver live in the game client (follow-up
  lane); the morph NAMES are the contract.

## Teardown deltas (open)
- [ ] DOA facial rig technique / morph counts — unverified (`.g1m` never
  extracted); update this doc if the crew extracts one.
