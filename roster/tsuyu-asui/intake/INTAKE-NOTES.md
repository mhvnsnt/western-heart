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
