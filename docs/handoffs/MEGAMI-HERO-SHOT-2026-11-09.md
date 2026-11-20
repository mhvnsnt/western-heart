# MEGAMI HERO SHOT — Pilot 2 final composition (2026-11-09)

The owner's ordered combined set: Megami + complete tattoos + Pilot 2 v2 Angel face +
Angel-brown eyes + the fixed Angel afro, on the reshaped v2 body, bare. Composed in the
standard three.js proof harness (same dark stage and 3-point rig as the accepted hair-fix
proofs of PR #1689). Every frame below was viewed by the composing lane before shipping;
the parent reviews before the owner sees anything.

## Inputs (exact, no substitutes)

- BODY: `megami-angel-pilot2-v2.glb`, 59,108,496 B, from release `megami-pilot2-20261108`.
  Verified in the file before rendering: mesh-level morph defaults AngelFace = 1 and
  AngelBody = 1 on every mesh (indices 474/475 on the body mesh), so the exported state
  IS the v2 state. Tattoos incl. T13 "XIV" and T14 sternum glyph are in its skin textures.
- AFRO: `customization/parts/megami-hair/megami-hair-angel-afro/megami-hair-angel-afro.glb`
  from main (PR #1689 build12), 81,320,784 B downloaded byte-size exact.
- EYES: Angel-brown iris part `eye-brown-angel-daz.png` (1024×1024) applied to the body's
  `Irises-2` material — RepeatWrapping both axes, flipY=false, SRGB. NOTE: this file
  currently lives on the PR #1678 branch (`pilot2/megami-angel-20261108`), not on main;
  the copy used here is byte-identical (cmp) to the copy the hair lane used for the
  accepted #1689 proofs. Tiger eye not used in this set.

## Composition (all measured in the loaded scene, logged by the harness)

- FIT: the afro was placed by measured head-joint alignment — body `Head` bone world
  (0.000, 1.487, -0.003) minus the afro rig's `head` joint bind world (0.000, 1.629, -0.004),
  applied afro root delta = (0.000, -0.142, +0.001). The negative Y is the afro part's own
  subset-rig bind offset, not a body defect: NO mesh-vs-skeleton offset exists in this
  pilot GLB (the v4 game GLB's -0.33 m artifact does not apply here and no such
  compensation was used). The seated result was verified from front, back and both sides.
- BARE: 10 bundled nodes hidden by name in the harness — `Hair001` (the GLB's `Hair.001`,
  loader-sanitized), `Full` (strand hair), `AngelHairScalpCap`, `AngelHairStraight`,
  `AngelHeadband` (the bundled v1 straight set), `Goggles`, `Top`, `Bottom`, `Gaunlet`,
  `Shoes`. Only `Parvati Mesh` + `Eyebrow` + `Eyelashes` render. Nothing was reposed;
  the body is in its exported state throughout.
- STAGE: background #14121c, SRGB output, NeutralToneMapping exposure 1.1, hemisphere
  1.15 + key 2.2 + fill 0.55 + rim 0.9 — identical to the hair-fix stage.
- Cameras are framed from measured bone positions (Head / Chest / pelvis) and the fitted
  afro bounding box (frame height 1.761, top 1.773); the face camera was lowered after the
  first pass because the afro fringe occluded her eyes from a high angle — the shipped
  face frame is shot slightly upward, matching the full-body sightline.

## Frames (docs/proof/2026-11-09/megami-hero/)

- `hero-front-20261109.png` — full body front. Afro seated, dense black, ears covered;
  brown eyes readable; thigh butterflies T1/T2 and T4 outer-left patch visible; chest
  marks in frame.
- `hero-back-20261109.png` — full body back. T5 wingtips at the blades under the afro
  edge; T6 lower-back/hip swirl field and T7 buttock + back-of-thigh coverage read fully;
  afro dense to the nape.
- `hero-left-20261109.png` — her left profile. T4 patch and T6/T7 wrap read; afro side
  silhouette rounded, face inside the mass.
- `hero-right-20261109.png` — her right profile. T8/T9 marks on the right upper arm in
  frame; swirls wrap the hip.
- `hero-face-closeup-20261109.png` — the v2 face framed by the afro: brown eyes clear,
  brows/lips at the v2 values, T13/T14 in frame below.
- `hero-chest-closeup-20261109.png` — T13 "XIV" fully legible below her left clavicle;
  T14 ankh-form glyph legible at centre sternum; T8 canon script partially legible on
  her right upper arm ("...was here before you / ...will be here after").
- `hero-pelvis-front-closeup-20261109.png` — anatomical proof frame; GP anatomy renders
  with its natural tonal variation preserved (never flattened, per the skin constraint).
- `hero-pelvis-back-closeup-20261109.png` — T6/T7 swirl field fills the frame, dense
  and legible hip-to-hip.

## Watch items / caveats (honest)

1. FOREARMS/HANDS: the soft, warped forearm bend flagged in the v2 tattoo proofs
   PERSISTS in all four full-body frames. It is a property of the pilot GLB's exported
   state (bind pose), symmetric on both arms; per the no-hand-posing rule it was not
   corrected here. Belongs to the fidelity lane with the v4 body work.
2. HAIRLINE: at face-close distance there is a small centre-front notch in the afro's
   fringe seal and the dome arc is faintly visible behind the front curl row. The same
   notch is present in the hair lane's own #1689 proof. At full-body distance it reads
   as a natural high hairline; no scalp gap exists at the sides, back or crown.
3. SKIN SHEEN: under the standard stage her exported physical materials (clearcoat /
   specular) render a glossy sheen, strongest on shoulders, chest and hips. Tone stays
   in her v4 family — no washout, no pale shift — and the read is consistent with the
   hair lane's accepted proofs on the identical rig.
4. AFRO MACRO CHARACTER: at close range the curls read as chunky geometric hooks —
   the shipped character of the tube-clump part (1,670,136 tris). Dense, black and
   opaque at every proof distance in this set.
5. The eye-part file should land on main when PR #1678 merges; until then it exists
   only on that branch (used here byte-identical).

## Harness

`stage.html` + `shoot.py` in the proof folder reproduce the set: serve the workspace
root on 127.0.0.1:8843, place body/afro/eye files in `_hero-shot-20261109/assets/`
(body.glb, afro.glb, eye-brown.png), and run the shoot script per camera group. The
harness logs every hidden node, the applied eye part, the morph defaults read back from
the loaded mesh, and the afro fit delta on each load.
