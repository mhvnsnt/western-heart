# Bannon mask: a shared, editable attire attachment

The owner treats the Bannon mask as the core piece of his work, so it's built to drop into every game (Western Heart, brutalfistgrokversionten, AshLanev2). Provenance: **ORIGINAL, owner-made**. The source is the Drive file "Bannon mask only 1st 3d model.glb" (`1kduK8mg8_webC76cwRQw0MyETY5eHP44`).

## Files (western-heart `lab/`)
| File | What |
|---|---|
| `source_assets/original/bannon_mask_original.glb` | **Untouched original** (sha256 starts `6f117352f396f3f7`, meshopt + quantized, 977k verts) |
| `game/attire/bannon_mask/bannon_mask.glb` | Game LOD: `gltf-transform dequantize → weld → simplify(0.025) → resize 1024`. 32.7k verts, 2.6 MB |
| `game/attire/bannon_mask/bannon_mask.manifest.json` | **The contract**: socket aliases, material slots/params, user transform, parts, per-rig presets, follow-check results |
| `game/scripts/attire.gd` | Godot loader (`Attire.attach`) |
| `tools/mask_fit.py` | Fits presets for each rig, runs the follow/clip/pop check, renders the proof sheet |

## Manifest contract (any engine)
- `socket.bone_aliases`: the first bone found wins (`Head`, `mixamorig:Head`, `head`, …).
- `presets[rig_id]`: `{bone, offset[xyz], rotation[xyzw], scale}`, expressed **in the head bone's rest frame**. Final transform: `bone_world × T(offset) × R(rotation) × S(scale × user.scale_mul)`, followed by `user_transform.offset_add` and `rotation_euler_deg_add`.
- Shipped presets: `wh_canonical_t3` (Tekken 3 rigid King), `wh_canonical_autorig` (Pantera Leo-Man), `mixamo` (49-bone pantera.glb) and `bannon_mixamo58` (brutalfist `BANNON_rigged.glb`).
- `material_slots[0].params`: `tint`, `use_texture`, `roughness`, `metallic`, `emission`, `emission_energy`, `normal_strength`, each with a default and range.
- `parts`: only `whole` toggles. The mesh is one primitive and splits into 278 decimation fragments rather than semantic pieces. Clean part toggles (crest, jaw, …) need the owner's source split per part.

## Godot API
```gdscript
var mask := Attire.attach(skeleton, "res://attire/bannon_mask/bannon_mask.manifest.json", "wh_canonical_t3",
                          {"tint": Color(1, 0.8, 0.8), "metallic": 0.3})
mask.set_params({"emission": Color.RED, "emission_energy": 2.0})   # live edit
mask.set_transform_params({"scale_mul": 1.1, "offset_add": [0, 0.01, 0.02]})
mask.set_part("whole", false)                                       # toggle
```
In the Lab slice, `Fighter.wear_mask(params)` wraps this. King (P2) wears it from round 1, and Pantera (P1) puts it on in round 2 with a purple metallic tint. The **M** key / gamepad Back toggles P1's mask.

## Three.js (brutalfist / AshLane) adoption
Load the manifest, then `skeleton.getBoneByName(alias)` → `bone.add(maskScene)`. Set `maskScene.position/quaternion/scale` from the preset. Because Three.js parents to the bone's *current* frame, a rest-frame preset is exact. Clone the material and apply params with `MeshStandardMaterial.color/roughness/metalness/emissive/normalScale`.

## Verification (`python3 lab/tools/mask_fit.py <manifest> <proof.png>`)
Each animated rig gets 337 frames at 60 fps across idle, walk_fwd, light, medium, heavy, hit and block:
| Rig | Relative drift (pop) | Max step/frame | Body verts newly entering the mask volume | Result |
|---|---|---|---|---|
| wh_canonical_t3 (King) | 6.7e-16 | 8.1 cm | 0 (1 at rest) | PASS |
| wh_canonical_autorig (Leo-Man) | 6.7e-16 | 5.2 cm | 24 (105 mane verts overlap at rest, by design) | PASS |
The Mixamo and Bannon rigs get static presets plus rest renders only. `BANNON_rigged.glb` **fails the rig check**: its skinned bind differs from the authored mesh (inverse bind matrices don't match the skeleton), so its preset is fitted to the authored mesh.
