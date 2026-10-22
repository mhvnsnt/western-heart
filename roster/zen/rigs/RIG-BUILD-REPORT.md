# ZEN Rig Build Report — rigs per transformation + visual transformation sequences

Built 2026-10-22 by the zen-rig recovery lane (checkpoint `zen-rig-transforms-20261021`).
Owner directive 2026-10-21: rig all four forms each as its transformation needs, on the
SAME attire (Attire 1), with visual transformation sequences between them.

## Deliverables (all NEW files, zero modifications, zero deletions)

`roster/zen/rigs/`:
- `spirit-body-rigged.glb` — 49-joint WH canonical skeleton, clips: `ZEN_IDLE`, `ZEN_MANIFEST`
- `spirit-entity-rigged.glb` — ZenRoot + 20 tentacle strands (5 joints each) + EyeA/EyeB/Mouth,
  clips: `ZEN_IDLE`, `ZEN_DOCK`
- `tentacle-mode-rigged.glb` — 49-joint WH skeleton + 12 tentacle strands (5 joints each),
  clips: `ZEN_BUST_OUT`, `ZEN_IDLE`
- `oversoul-rigged.glb` — 49-joint WH skeleton + 7 head/appendage strands + EyeA/EyeB/Mouth/ChestMouth,
  clips: `ZEN_OVERSOUL_FORM`, `ZEN_IDLE`
- `RIG-BUILD-REPORT.md` — this file

`docs/tpose-refs/zen/seq_*.png` — own-eyes proof renders of the actual sequences (2048px,
locked render method, Cycles, white background, textured).

The wired static models (`attires/attire1/model.glb`, `spirit/model.glb`, `tentacle/model.glb`,
`oversoul/model.glb`) and all game wiring (`assets.js`, `roster-full.js` forms chain) are
UNTOUCHED. The rigged files are the rig-stage outputs the stand/moveset system wires in;
clip trigger wiring (e.g. play `ZEN_BUST_OUT` on up-transform to `zen-tentacle`) is
stand-system work, documented below.

## Template statement (TEMPLATE DIRECTIVE compliance)

Rigs ride the operation's current TEKKEN-template standard: the WH canonical 49-bone
Mixamo-style skeleton as rebuilt on `game/assets/models/pantera.glb` (PR #560, merged
2026-10-22, owner-verified clean against the T7-era template ground truth). Skin weights
are k-NN transferred (k=4, repo PR #264 path) from that donor. **No T3-era skeleton or
T3-baked data was touched.** The spirit entity is deliberately NOT on the humanoid
template — canon says NO arms, NO legs; it gets a purpose-built float-root + tentacle
+ face rig, which is why it does not pass the fighter height/bone gate (it is a stand,
not a fighter).

## Method (pure-numpy GLB surgery, no Blender in the rig path)

Blender import/export reorders ~1M-vert meshes and scrambles per-vertex weight
correspondence, so the entire rig is written directly (vertex order preserved exactly):
1. `prep`: feet→y=0, uniform scale to 1.50 m (humanoids) / 0.75 m (spirit entity).
2. k-NN weight transfer from the pantera.glb donor in donor-facing space (zen rotated
   Ry(−90°) to the donor's +Z facing for the query only); the donor skeleton is mapped
   into authored space by the similarity A (rotation + uniform scale + translation),
   joints conjugated as J′=AJA⁻¹, IBMs as IBM′=A·IBM·A⁻¹. Donor's `Character` wrapper
   rotation is baked into Hips' local so W·IBM=I holds exactly (verified 0.0 / 2e-6).
3. Tentacle strands: protrusions beyond the body (axis-radius profile + head-sphere
   core term, so above-head archers are caught) are grouped by nearest core-surface
   patch; each strand gets a 5-joint chain fitted by medial walk (arc-length
   parameterization, triangular kernel weights, smooth blend to body weights at the
   base). Strands whose verts are >40% hand/foot by k-NN are dropped (they are fingers,
   not tentacles — they keep donor finger weights).
4. Face bones: baseColor texture sampled per-vertex; blue→EyeA/EyeB (split by lateral
   median), red below the eye line→Mouth. Oversoul also gets ChestMouth (the red chest
   oval). Spirit entity: face constrained to the +X face side.
5. Clips baked as glTF animations (30 fps, LINEAR), rotation deltas premultiplied by
   bind quats (glTF channels replace bind locals).

## Transformation sequences (what each clip does)

- `ZEN_MANIFEST` (spirit-body, 60f): anticipation/power pose — crouch, knees bend,
  arms abduct, chest expands, holds. Plays on transform-start out of base.
- `ZEN_BUST_OUT` (tentacle-mode, 90f): body takes the manifest pose in 30f; the 12
  tentacle strand roots scale 0.001→1 staggered (each tentacle emerges from its base
  point on the body/clothing), wiggle amplitude ramps in to full. End state = the
  tentacle mode at rest.
- `ZEN_DOCK` (spirit-entity, 90f): ZenRoot flies (0,0,0)→(+0.55 fwd, +0.38 up) on an
  eased arc with a slight roll; eyes track forward. Intended: plays while the
  body plays `ZEN_MANIFEST`; at the dock point the game swaps to the oversoul model.
  (Authored in spirit-local space; the stand system orients +X toward the body.)
  NOTE: the spirit's tentacle strands are NOT individually wiggled during dock/idle —
  the tightly-packed radial tentacles produced hard k-means weight boundaries, and
  per-strand rotation tore the surface (verified with own eyes, then fixed by
  switching to rigid root motion; the tear is gone in the proof render).
- `ZEN_OVERSOUL_FORM` (oversoul, 120f): head-tentacle strands flow in a traveling
  wave; EyeA/EyeB look at INDEPENDENT targets (opposite phases, per canon);
  Mouth + ChestMouth articulate; appendage strands flow like flame/ribbon; body holds
  a power stance.
- `ZEN_IDLE` loops (60/90f): breathing + per-strand sine wiggle with per-strand phase
  offsets (individual tentacle motion per canon) on tentacle-mode/oversoul; the
  spirit-entity idle uses rigid root bob/sway (see dock note above).

## Proof (own eyes, this lane)

Rendered in Blender 4.0.2 (xvfb, Cycles, locked method) from the actual rigged GLBs
with the actual clips applied — not T-poses, not stand-ins:
- `seq_manifest.png` — spirit-body `ZEN_MANIFEST` f40: power pose, rig intact, textured.
- `seq_bustout.png` — tentacle-mode `ZEN_BUST_OUT` f45: tentacles mid-emergence
  (partially scaled strands bursting from the body).
- `seq_dock.png` — spirit-entity `ZEN_DOCK` f45: mid-flight toward the head position,
  tentacles trailing, mouth open.
- `seq_oversoul.png` — oversoul `ZEN_OVERSOUL_FORM` f60: head tentacles flowing,
  face on the head, mouth open, body imagery flat (correct — not chained).

Gate: `tools/auto_rig/validate.py` PASS on all three humanoid rigs (valid glTF, skinned,
all 49 Mixamo bones, 1.5 m, feet y=0). The spirit entity intentionally skips the
fighter gate (stand rig, documented above).

## Known limits (not faked, logged)

- Strand chains are a surface-patch approximation: a long curved tentacle can span 2
  adjacent strands (each still wiggles with its own phase — reads as individual motion).
- Tentacle tips near hands/feet keep donor hand/foot weights (no independent wiggle
  there) — flagged by the >40% hand/foot drop rule.
- The pastel chromatic blast attacks (ink/razor beams/waves) are a moveset-stage
  requirement (RIG-NOTES.md) — not modeled here.
- Eye look targets are procedural saccades; the stand system will drive them.
- `ZEN_DOCK`'s end offset (+0.55 fwd, +0.38 up) is a starting value for the stand
  system to tune against the real body head position, like the +0.35/+0.30 spirit
  placement offset in RIG-NOTES.md.
