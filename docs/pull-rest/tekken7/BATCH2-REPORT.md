# PULL-REST — Batch 2 Report (2026-10-16)

On-disk backlog: two model archives already downloaded by earlier lanes but
never verified/landed. Both verified this batch via Blender 4.0.2 headless.

## doc-frank.glb — Dr. Bosconovitch (TTT2 base)
- Source: `game-reverse-engineering/tekken7/models/dr-bosconovitch/dr-bosconovitch-ttt2-xps.rar`
  (XPS format, TTT2)
- Pipeline: `~/workspace/pull-rest/verify_render_xps.py` (XNALara-io-Tools
  addon; model faces -Y; absolute-path import; DDS texture fixup + emission
  override — the importer's TEX_IMAGE nodes need basename reload to decode)
- Verified: **9,559 verts, 25 meshes, 1 armature, 1.79m**, humanoid bbox —
  PASS, own-eyes verified (textured: lab coat, tie, glasses, wild hair)
- GLB: 10,442 verts, 25 meshes, **23 embedded images, 1 skin (rigged)**
- WH name: DOC FRANK (owner-named 2026-10-13)

## cyborg-x.glb — Alisa Bosconovitch (T7 base)
- Source: `agent-ops/worktrees/wrestling-teardown/tekken7/models/alisa-bosconovitch/
  browser-download-20261013T042141.056181166Z-11-Alisa_Bosconovitch_v1.1.rar`
  (Source Filmmaker .mdl + .vvd/.vtx + .vtf/.vmt, T7)
- Pipeline: `~/workspace/pull-rest/verify_render_sfm.py` (SourceIO 5.5.4
  addon; needs `enum.StrEnum` shim on Blender 4.0.2/py3.10; operator requires
  `filepath` + `files=[...]` — filepath alone silently imports nothing)
- Verified: **51,132 verts, 19 meshes, 1 armature, 1.49m** — PASS by own-eyes
  (complete T-pose humanoid, faces -Y; auto h/w gate tripped on wide armspan)
- GLB: 51,133 verts, 19 meshes, **1 skin (rigged), 0 embedded images**
  (SourceIO packs VTFs as custom-shader images; glTF exporter skips them —
  textures verified present in Blender render; re-texture on reskin)
- WH name: CYBORG X (owner-named 2026-10-13; = Cape Jones canon)

## This PR
- `game/assets/models/doc-frank.glb`
- `game/assets/models/cyborg-x.glb`
- `docs/pull-rest/tekken7/doc-frank_front.png`, `docs/pull-rest/tekken7/cyborg-x_front.png`
  (front approval renders, white void, ortho)

Models land AS ASSETS ONLY — no hookup/integration/gameplay edits (gate).
New tooling proven this batch: unrar 7.20 @ `~/workspace/tools/unrar/rar/unrar`
(RAR5), SourceIO 5.5.4 installed to Blender addons (with py3.10 StrEnum shim).
