# Decision Log — 2026-10-22 — VF5 Full Integration, Worker 57 (re-dispatch)

## Re-dispatch context

Worker 57 re-dispatched after the previous worker was killed by a runtime
daemon failure mid-batch (van's render, 21:48). Prior state verified on
resume: PR #692 + PR #696 both merged to main (extractors, 4 locked
movesets, research doc, WORKLOG + decision log). 17/18 renders complete and
uploaded to remote storage. Remaining: van (obj written, PNG interrupted),
wol (not started).

## van + wol renders completed

- van: re-rendered from existing `van.obj` (Blender 4.5.3, same pipeline).
  Verified visually: clean T-pose clay, facing camera. No geometry issues.
- wol: extracted `wolitm000` -> obj, rendered. **Head missing in first
  render** — see fix below.

## Wolf's head was in a second itm file (new format layout found)

**Finding:** `wolitm000_obj.bin` (the file the whole batch rendered) contains
Wolf's body but NO face geometry — only an eye band (chunk1, 168 verts at
y 1.854-1.884). His kao (face) mesh lives in `wolitm001_obj.bin`.

**Second vertex-header layout:** files like wolitm001 do NOT use the chunk
table at +0x40. Their vertex headers sit at ~0x94 with the same
(vcount @+0x20, pos_rel @+0x24, end_rel @+0x28) triple, vertex buffer at
header+pos_rel. Coords are in the same model space as the body (verified:
face x ±0.092, y 1.770-1.984 — sits exactly above the eye band).
Index strips are u16 runs elsewhere in the file.

String IDs confirmed the part: `KaO` (face) in wolitm001; `zura_MZ`
(wig), `I_osagekami_MZ` / `I_kami_MZ` / `regent_*_MZ` (hair) in other files.

**Fix:** merged face (921 verts @0x558 — 7 stray non-face verts dropped,
u16 strip @0x12704, 2322 idx, 1311 tris) into wol.obj (5136 + 921 verts)
and re-rendered. Verified visually: head sits correctly on the neck, no
artifact triangles.
Reproducible script: `tools/vf5/merge_wol_head.py`.

**Consequence:** all 18 VF5 fighters now have complete T-pose renders.
Only wol was affected — the other 17 renders were visually verified
(jef, van spot-checked; all OBJs have full y-extents 1.50-1.98).

## claimed-map.json verified (read-only, worker 47's lane)

`game/data/moveset-library/claimed-map.json` (w47 staging, not yet on main)
already records `vf5_mappings_locked` (Bannon->Jeffry, El Toro de Oro->Wolf,
NPC Finxsse->Lei-Fei, Pablo->El Blaze + candidate list) and
Dural->Zen in approved_exceptions. No conflicts with Tekken claims
(separate pool). No edit needed; update noted here per task.

## Gaps carried forward (unchanged from worker 45 + teardown lane)

- Motion data: NOT in vf5-ps3-v1. Teardown lane's
  `docs/research/VF5-MOTION-GAP-2026-10-22.md` documents the precise
  blocker + path (4GB vf5-500m archive or BLES00029 dump; multi-day RE).
  Dural's animation for Zen remains data-blocked.
- Stages: 38 `stg*.farc` listed; extraction/visual-ID belongs to the arena
  pipeline (`docs/research/VF5-FULL-INTEGRATION-2026-10-22.md` has the list).
- Textures: TXP containers not yet extracted; renders are untextured clay.

## Delivery

- 17 prior render URLs in `upload_urls.log` (worker 45); van + wol uploaded
  by worker 57 and appended. URLs relayed to parent for user delivery.
  Renders stay out of the repo (review-only deliverables).
- NOTE: the old `watch_upload.sh` (worker 45) was still running and uploaded
  interim versions of van/wol on its own; it has been stopped. The DEFINITIVE
  URLs are the LAST two lines of `upload_urls.log` (the fixed wol render
  with the merged face).
- MERGE FREEZE: branch pushed, PR opened, NOT merged. Merge-ready on freeze lift.
