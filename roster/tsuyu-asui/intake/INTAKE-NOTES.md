# Tsuyu Asui — intake notes (batch 2, 2026-10-22)

Source: `Tsuyu_Asui_IK_V1.1.zip` (sha256 `eb8495ee…5d02d57a41baa`), in-repo at
`roster/tsuyu-asui/intake/` (IK-rigged `.blend` + `.blend1` + `textures/`).
The `.blend` was byte-inspected (object/datablock names, zstd frame) — findings:

## Clothing: SEPARATE modeled geometry (verified)
These are separate objects from the body mesh (`OBtsuyu`):
- `OBsuit` — bodysuit
- `OBboots`, `OBgloves`
- `OBBody_belt.dmx`, `OBBody_mask.dmx`, `OBBody_google.dmx` (goggles)
- `OBHair`

**Undress = hide/remove those meshes.** No painted-on clothing to repaint;
the body underneath is fully modeled.

## Anatomy notes
- **`OBBulge` — user-flagged pronounced camel-toe region. KEEP it in the
  anatomy pass** (do not flatten or remove). It is part of the requested anatomy.
- `OBPenis` mesh is also present in the file — the rig lane decides what ships
  per the character's design; the camel-toe (`OBBulge`) stays regardless.
- Separate `OBface_template` / `OBmouth_template` objects present (face rigging aids).
- Rig: `OBtsuyu rig` armature + IK widgets (`OBWGT-tsuyu rig_*`).

## Textures
`suit_*`, `boots_*`, `Tsuyu_skin.png`, `skin_face.png`, `penis.png` — per-material
sets matching the separate meshes above.

## Frog hat + hair investigation (worker 64, 2026-10-22)

Owner catch: Tsuyu's T-pose render (PR #634) was missing her frog hat
("Tsuyu without her frog hat isn't Tsuyu. Get it on her.") and possibly her hair.

Full object-name scan of `Tsuyu Asui IK.blend` (decompressed, 37 objects):
`suit`, `boots`, `gloves`, `Body_belt.dmx`, `Body_google.dmx`,
`Body_mask.dmx`, `Hair`, `tsuyu`, `Bulge`, `Penis`, `face_template`,
`mouth_template`, `tsuyu rig` + IK widgets.

- **Frog hat: NOT in the source at all.** Not hidden, not unexported — the
  object doesn't exist. Verdict: missing entirely → crew modeled one as a
  separate interchangeable library part:
  `customization/parts/headwear/frog-hat/` (label `headwear_frog-hat_01`),
  registered in her clothing config. Re-rendered T-pose ships with it on.
- **Hair: PRESENT.** `OBHair` exists in the source and IS visible in the PR
  #634 render — no fix needed. Registered as the first-class hair library
  item `hair_bob_01` (hair is separate from headwear per owner directive).

Clothing label map for Tsuyu: `game/data/clothing-layers.json` → `tsuyu-asui`
(standard: `docs/CLOTHING-ACCESSORY-LABELING-STANDARD.md`).
