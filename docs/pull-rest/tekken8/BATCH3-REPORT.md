# PULL-REST — Batch 3 Report (2026-10-16)

On-disk backlog: three more model archives already downloaded by earlier lanes,
never verified/landed.

## diablo.glb — Heihachi Mishima (T7 base)
- Source: `game-reverse-engineering/tekken7/models/heihachi-mishima/
  ...1600860987_heihachi_mishima.rar` (GTA SA .dff + .txd)
- Pipeline: `~/workspace/pull-rest/verify_render_dff.py` (DragonFF addon,
  cloned from Parik27/DragonFF; .txd imported first, then .dff; material
  rewire: TXD images are named `txd/NAME/0` vs DFF refs `NAME.PNG` — match on
  the middle component; emission override for flat render)
- Verified: **51,525 verts (scene), 1 mesh, 1 armature**, complete humanoid —
  PASS by own-eyes (textured gi, spiky hair, T-pose)
- GLB: 21,834 verts (welded), 1 mesh, 1 image, **1 skin (rigged)**; GLB
  reimported + rendered to confirm completeness
- WH name: DIABLO (owner-named 2026-10-13)

## kinpo-t8.glb — Asuka Kazama (T8 base, bikini variant)
- Source: `game-reverse-engineering/tekken8/models/sfmlab-tekken8-asuka_SFM.rar`
  (Source Filmmaker .mdl + .vtf/.vmt)
- Pipeline: `~/workspace/pull-rest/verify_render_sfm.py` (SourceIO 5.5.4)
- Verified: **26,337 verts, 4 meshes, 1 armature, 1.12m**, complete textured
  humanoid — PASS by own-eyes (faces -Y)
- GLB: 47MB (4K VTF textures embedded); rigged
- WH name: KINPO (owner-named 2026-10-13); `-t8` suffix (T7 asuka.glb exists)

## phantom-t8.glb — Yoshimitsu (T8 base)
- Source: `game-reverse-engineering/tekken8/models/t8-yoshimitsu-s1-blender.7z`
  (Blender .blend, extracted via py7zr)
- Pipeline: `~/workspace/pull-rest/verify_render_blend.py` (open .blend,
  export GLB, render 4 views)
- Verified: **63,947 verts, 14 meshes, 1 armature, 2.01m**, complete fully-
  textured armored humanoid — PASS by own-eyes (faces -Y)
- GLB: 40MB (4K textures embedded); rigged
- WH name: PHANTOM (owner-named 2026-10-13); `-t8` suffix (T7 phantom.glb exists)

## Blocked
- `t8-heihachi-s1.7z` (122MB): CORRUPT — py7zr raises
  `Bad7zFile: next header size 37 exceeds the archive size`. Needs re-download
  (browser lane / gdrive-dl.sh in the same dir).

## This PR
- `game/assets/models/diablo.glb`
- `game/assets/models/kinpo-t8.glb`
- `game/assets/models/phantom-t8.glb`
- `docs/pull-rest/tekken8/diablo_front.png`, `docs/pull-rest/tekken8/kinpo-t8_front.png`,
  `docs/pull-rest/tekken8/phantom-t8_front.png` (front approval renders)
- `docs/pull-rest/tekken8/BATCH3-REPORT.md`

Models land AS ASSETS ONLY — no hookup/integration/gameplay edits (gate).
New tooling proven: DragonFF (~/.../addons/DragonFF), py7zr for .7z,
verify_render_dff.py, verify_render_blend.py.
