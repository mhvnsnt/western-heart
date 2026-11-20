# POND (Tsuyu Asui) — PARTS.md

Attire 1: `roster/tsuyu-asui/attires/attire1/model.glb` (5.8 MB) — byte-inspected 2026-10-23.
Source `.blend`: `roster/tsuyu-asui/intake/Tsuyu Asui IK/` (IK-rigged `.blend` + textures).
Full object-level breakdown: `roster/tsuyu-asui/intake/INTAKE-NOTES.md`.

**Summary: 9 meshes, unrigged static (0 skins).** Clothing IS separate modeled geometry (verified in the `.blend`): bodysuit, boots, gloves, belt, mask, goggles, hair are independent of the body mesh. **Undress = hide/remove those meshes** — no painted-on clothing; the body underneath is fully modeled. Bounding boxes below use the GLB's space (Z-up, head ≈ Z 4.0).

## Mesh inventory

| # | GLB mesh name | Verts | Region (bbox) | Probable identity (maps to `.blend` object) | Category | Swappable | Layer |
|---|---------------|-------|---------------|----------------------------------------------|----------|-----------|-------|
| 1 | `Tsuyu` | 86,126 | full figure (Z 0–4.05) | `OBtsuyu` — body mesh | full-body | no — base body | skin |
| 2 | `Holo_001` | 49,370 | torso-to-legs (Z 0.26–3.38, X ±1.30) | `OBsuit` — bodysuit (export-renamed; mats `boots`/`eyes` are export artifacts) | full-body | **yes** | clothing over skin |
| 3 | `Mesh0000_003` | 24,852 | lower body (Z 1.60–2.04, Y −0.51–−0.14) | `OBboots` fragment — boot/lower-leg covering | footwear | **yes** | clothing over skin |
| 4 | `Mesh0000_004` | 30,708 | lower body (Z 1.61–2.14, Y −0.96–−0.16) | `OBboots` fragment — second boot/lower-leg covering | footwear | **yes** | clothing over skin |
| 5 | `Plane_003` | 16,192 | chest plane (Z 2.94–3.26, X ±1.91, flat) | `OBgloves` fragment or suit chest panel — wide flat covering at chest/arm span | gloves/tops | **yes** | clothing over skin |
| 6 | `Tsuyu_Asui_MHA_rstar_Tsuyu_Asui_Tsuyu_Asui_SFM_mdl_Belt_Body_bel` | 4,668 | waist (Z 2.47–2.66) | `OBBody_belt.dmx` — belt | accessories | **yes** | accessory over clothing |
| 7 | `Tsuyu_Asui_MHA_rstar_Tsuyu_Asui_Tsuyu_Asui_SFM_mdl_Googles_Body_` | 6,864 | head top (Z 3.98–4.39) | `OBBody_google.dmx` — goggles (worn on forehead per canon) | headwear | **yes** | accessory over hair |
| 8 | `Tsuyu_Asui_MHA_rstar_Tsuyu_Asui_Tsuyu_Asui_SFM_mdl_Mask_Body_mas` | 540 | face (Z 3.51–3.68) | `OBBody_mask.dmx` — face mask | headwear | **yes** | accessory over skin |
| 9 | `Tsuyu_Asui_MHA_rstar_Tsuyu_Asui_Tsuyu_Asui_SFM_mdl_hair_BodyHair` | 6,087 | head (Z 1.90–4.12) | `OBHair` — hair | hair | **yes** | hair over skin |

Notes on export naming: the GLB exporter renamed the `.blend` objects (`OBsuit`→`Holo_001`, `OBboots`→`Mesh0000_003`/`Mesh0000_004`, etc.) and collapsed materials to generic `boots`/`eyes`. Identities above are assigned by bounding-box region + the verified `.blend` object list in INTAKE-NOTES.md; the rig lane should confirm each mapping when the model is re-exported with clean names.

## NOT in the source — documented absences

- **Frog hat: confirmed NOT in the source `.blend`** (never modeled — verified in INTAKE-NOTES.md object list). No hat mesh exists to wire; a frog hat is built new in the creation suite if ever wanted.
- `OBBulge` (camel-toe anatomy): present in `.blend`, **KEPT per owner directive** — part of the requested anatomy, do not flatten.
- `OBPenis`: present in `.blend`; the rig lane decides what ships per the character's design.

## Creation-suite notes

- **Tops:** bodysuit (`Holo_001`) — full-body suit, swappable yes.
- **Bottoms:** none separate (suit covers) — author new or split the suit mesh.
- **Full-body:** body (`Tsuyu`, not swappable) + bodysuit (`Holo_001`, swappable).
- **Underwear:** none — body underneath is fully modeled; author new.
- **Accessories:** belt (waist), goggles (headwear/forehead), mask (face) — all swappable.
- **Gloves:** `Plane_003` region suggests glove/chest coverage — verify at rig; author clean glove meshes as needed.
- **Footwear:** `Mesh0000_003`/`Mesh0000_004` — swappable yes.
- **Headwear:** goggles + mask (swappable); frog hat does not exist — new build only.
- **Hair:** `OBHair` mesh — swappable yes.
- Layer order: skin (body) < clothing (suit/boots/gloves) < accessories (belt/goggles/mask) < hair. Undress path: hide clothing meshes → body.
