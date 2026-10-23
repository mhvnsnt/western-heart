# T-Pose Render Batch — 2026-10-22 (Worker 10)

Renders for the user's 12-model shortlist work. All renders viewed and verified before shipping.

## Shipped renders

### Yukihyo / Armor King (Task D)
- `yukihyo-p1_front.png` / `yukihyo-p1_side.png` — Main attire (game/assets/models/yukihyo.glb). Gray clay (model has no textures). Clean T-pose.
- `yukihyo-attire1_front.png` / `yukihyo-attire1_side.png` — Attire 1 (roster/armor-king/attires/attire1/model.glb). Fully textured leopard-mask Armor King. Clean T-pose.

**Not shipped:** `lab/game/assets/t3_armorking.glb` and `t3_armorking_t3real.glb` — both are disassembled PS1-era rips (parts scattered, unusable for clean renders).

### Negativo (Task C — texture fix + proof)
- `negativo-pinkfix_front.png` / `negativo-pinkfix_side.png` — Pink beard restored (was white). See texture fix notes below.

### Unmapped fighters audit (Task F)
- `unmapped-fighters-audit.md` — Complete audit of Tekken T7/T6/T3 rosters vs WH mappings. 22 T7 fighters, 3 T3-only, and 4 T6-only fighters have no WH character assigned.

## Texture fixes

### Negativo: white → pink beard (FIXED)
**Problem:** White patch on face (beard mesh, `ModelBeard_2_Material031`) rendered white because the material had no texture and no base color.
**Fix:** Set `baseColorFactor` to hot pink `[1.0, 0.4118, 0.7059, 1.0]` on the beard material in `game/assets/models/n3g4tiv0.glb`.
**Note:** Initially fixed the wrong mesh (bandage/cheek patch) to pink, then reverted it to white and applied pink to the beard (the actual white patch). Bandage texture restored to plain white.
**Proof:** `negativo-pinkfix_front.png` shows the pink beard clearly.

## Blocked items (not shipped)

### Bruno (Task B) — BLOCKED: missing face texture
`bruno.glb` materials reference face/hair/neck/eyeball textures (indices 11/13/15/17) that don't exist in the file. No Miguel/Bruno textures found in local teardown files. SFMLab download blocked by bot protection. Needs external Miguel model pull.

### Scimitar (Task B) — BLOCKED: corrupted model
`scimitar.glb` (Shaheen-based) renders as a jumbled polygon mess — mesh is corrupted/disassembled, not a clean Shaheen. Needs a clean Shaheen model from external source.

### Paul Phoenix (Task A) — BLOCKED: no usable model
T3 `paul.kmd` converted to OBJ/GLB produces a flat unrecognizable blob (KMD converter doesn't handle the bone hierarchy correctly). No T7 Paul model locally. Needs external Paul model pull.

### Panda, Kuma, Law, Lars, Ogre (Task A) — BLOCKED: no models locally
No 3D models found in teardown files. Tekken 3 `models/` has 15 .kmd files (anna, bosconovitch, bryan, eddy, gunjack, heihachi, hwoarang, jin, julia, king, lei, nina, paul, xiaoyu, yoshimitsu) — no kuma/panda/ogre/law/gon. Need external model pulls.

### Gon (Task A) — BLOCKED: no 3D model exists
User approved a REPLACEMENT design (not Tekken's Gon). Only 2D drafts exist in `~/workspace/gon-replacement/`. No 3D model to render.

## Render pipeline notes
- Used `tools/tpose-render/render.py` (Blender 4.0.2 headless) with fixes for armature-space posing math.
- Yukihyo faces +Y; Negativo faces -Y (front).
- All renders: 2048px, white background, front + side views.
