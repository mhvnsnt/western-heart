# WWE WRESTLEMANIA XIX — Teardown for Western Heart

**Role in Chimera Build:** Wrestling Mode — modes, arena traversal, Revenge Mode structure.
**Developer:** THQ (Yukes engine — different philosophy from No Mercy's AKI engine)
**Platform:** Nintendo GameCube (Game ID `GW9E78`)
**Roster:** ~40 WWE wrestlers. **Revenge Mode:** mission-based objectives in settings beyond the ring.
**Create-a-Wrestler / Shopzone:** upgrade economy (attire, weapons, moves, ability points) informs the chimera customization meta-progression.
**Last updated:** 2026-10-13 (full rewrite — canonical doc)

**Directory layout (this teardown has two homes):**
- `teardown/wmxix/` — **arena/stage integration lane**: `ARENA-UNIVERSE-MAP.md` (every arena → Western Heart stage), `arenas/` (43 decoded OBJ point clouds + `ARENA-FORMAT.md` + extraction tools), this doc.
- `teardown/wwe-wrestlemania-xix/` — **format research lane**: `docs/` (measured format specs), `tools/` (26 decoder/analysis tools), `objs/` (eye-verified strip OBJs), `YANM-FORMAT.md`, `YOBJ-SKINNING-NOTES.md`, `WRESTLER-SKELETON.md`.
- Research log: `docs/WMXIX-TEARDOWN.md` (running notes). Full file listing: `docs/WMXIX-FILE-LISTING.txt`.

---

## 1. ISO — Downloaded + Verified (2026-10-12)

- `WWE Wrestlemania XIX (USA).iso` — 1,459,978,240 bytes, MD5 `c13c47a5ed24a675545c99a15e44529d` (matches source listing)
- Disc header: name `WRESTLEMANIA XIX`, Game ID `GW9E78`, magic `C2339F3D`
- Source: CDRomance (via browser task, no signup/payment). Mirrors: gamulator.com, Coolrom, freeroms
- Local working copy: `~/workspace/game-reverse-engineering/wwe-wrestlemania-xix/` (ISO + tools + docs; mirrored best-of into this repo per TEARDOWN-TO-REPO LAW)

## 2. File Structure — Mapped (2026-10-12)

Streaming FST parse via `tools/gcn_fst.py` (pure-stdlib GCN disc FST reader; no full extraction — streams from ISO byte ranges, disk-safe):
- **5,016 FST entries, 4,222 files, ~1.41GB** (scrubbed ISO 1.46GB on disk)
- FST offset/size at disc header `0x424`/`0x428` (`0x362F00`/`0x1A8A3`) — NOT the usual `0x420`; `gcn_fst.py` handles this

| Dir | Files | Content |
|---|---|---|
| `model/wrestler/` | 484 | Per-slot model groups `NNN_M`, slots 000–110 (111 slots — more than the ~40-man roster; extras likely CAW parts, managers, refs, divas). `_0` = `.tex` + `.ymg` + `.ycg`; `_1` second variant (alt attire) on 66 slots; `_2`/`_3` on a handful |
| `ringmotion/` | 340 | Move animation **pairs**: `.yag` (YANM skeletal anim, median 38.6 KB) + `.atr` (`DATA` metadata, median 388 B — 16-byte records describing its `.yag` companion). Letter groups a=68, b=46, c=208, d=12 — likely move categories (attack/grapple/strike/special). Includes `cnv.bat` (build-time converter left on disc) |
| `motion/*.mpc` | — | Shared move packages (`common`, `move`, `win`, `nyujo_ch` entrance) |
| `edit_data/` | 2,690 | CAW creation suite: `MODEL/` 1,213 part meshes (YOBJ), `TEX/` 1,469 part textures, `COL/` 8 `.ycg` (skeleton-size 2,356 B + small palette/override files) |
| `bg/` | 373 | Arena sets: per-arena `.ymg`/`.ycg`/`.tex` + `.pac` arena packages, `weapon/` 61 (hardcore weapons), `object/` 61 (Revenge Mode props), `placard/` 51 (crowd signs/banners) — Revenge Mode out-of-ring environments live here |
| `Entrance/` | — | Create-an-Entrance data (`CamData.dat`, `EffData.dat`, `entpac.mpq`) |
| `viewer/`, `2d/`, `thp/`, `tutorial/`, `paint_tool/` | — | Dev viewer assets, UI, videos, CAW paint-tool UI |

## 3. Wrestler Skeleton — Decoded (2026-10-12/13)

**70 bones**, measured from `model/wrestler/000_0.ymg` (64-byte slots at file `0xF3BC`): parent (0-based, −1 = root), local translation (f32 ×3), local euler XYZ (f32 ×3, rad), bone length.
- Full measured table + JSON: `../wwe-wrestlemania-xix/WRESTLER-SKELETON.md`, `../wwe-wrestlemania-xix/docs/wrestler-skeleton-000.json`
- Structure: Bip → Pelvis → Spine → Spine1 → Neck → Head (+ face bones: lips, teeth, eyes, brows); R/L clavicle → upper arm → forearm → hand (+ 5 × 3-segment fingers); R/L thigh → calf → foot → toe. Bip root at y = −102.695 (Yukes authoring convention: local y+ = R for clavicles and thighs)
- **`.ycg` joint groups** (the animation rig): 42 records = 8 singles + 5 L/R pairs + 8 3-chains; every record is a **1-DOF hinge**. Hinge axis uniform per group — local X (13 groups: limbs/torso/pelvis), local Z (6: head/neck + accessory chains), local Y (2) — FK-confirmed. 3-chain groups: ch1→rec1 (hip/shoulder), ch2→rec2 (knee/elbow), **rec3 = −(rec1+rec2)** (measured ≤0.03° end-effector stability — holds foot/hand world orientation)

## 4. YOBJ Mesh Format — Two Variants Cracked

### 4a. Arena variant — POSITIONS CRACKED ✅ (2026-10-13, PR #20)

- Version `0x00030013`. **f32 (float32) vertex triplets, big-endian** — NOT quantized like wrestler models
- **43 arena files extracted → OBJ point clouds, 324,425 vertices total** (`arenas/`: `00.obj`–`02.obj` main arenas, `0_0.obj`–`2_2.obj` bs/ sub-arenas, `ring.obj` = wrestling ring 809 verts, `kaijo_x8.obj` 14,170 verts, `*_ad2.obj` detail/LOD variants, entrance/ground/lighting/screen pieces)
- Point-cloud renders verified with own eyes: bg/00 = full arena bowl, ring.ymg = ring with posts/ropes, kaijo_x8 = arena structure
- File structure (bg/00.ymg, 304,480 B): object/bone names (`kaijo_rw`) @0x46BB4, material table (25 × 20-byte records) @0x47404, texture name table (`rw19.bmp`…) @0x470B4, mesh metadata @0x0830
- Material records: `[u32 color1][u32 color2][u32 color3][u32 0][u16 0x0004][u16 idx_offset]` — index offsets are ABSOLUTE file offsets pointing to ~52-byte u16 chunks
- **Face indices: OPEN** — the u16 chunks at material index offsets are mixed data (interleaved attributes or different stride), not clean triangle indices. Next: parse mesh descriptors at 0x0830+ to link vertex arrays to index arrays, or Blender Poisson reconstruction on the point clouds
- Tools: `arenas/extract_all_arenas.py` (all 43), `arenas/yobj_arena_extract.py` (single). Format doc: `arenas/ARENA-FORMAT.md`

### 4b. Wrestler variant — POSITIONS + CONNECTIVITY CRACKED ✅ (2026-10-13, PR #24)

- Version `0x00040001`. **s16x3 vertices, dequantized /64** — different from the arena variant's f32
- **Connectivity = implicit triangle strips, NO index buffers** (`../wwe-wrestlemania-xix/tools/yobj_strips.py`): vertex runs are strip-ordered (ladder/zigzag); split at jump boundaries (threshold max(400, 4× median step)); single near-origin separator verts between strips. The "dense u16 runs" in file gaps are NOT index buffers (coordinate-scale values + zero runs; no valid index buffer referencing the vertex list exists anywhere in the file)
- Eye-verified: `model/wrestler/000_0.ymg` → 13 skin batches (8-byte records @0x7CA0, 606 s16x3 verts) → 58 strips → **383 tris**; elbow CAW part (148 verts) → **113 tris**; OBJs at `../wwe-wrestlemania-xix/objs/`
- **Batch descriptor table**: 58 × 16-byte records at header `[0x5C]` (0x5AE0) — payload offset (base file 0x80), material/part id (b8, range 3–70), unit count (4-byte units). Fully measured in `../wwe-wrestlemania-xix/docs/YOBJ-BATCH-SEMANTICS.md` (group-header pattern: records 1–7 counts sum to record 0's count; `marker_hi = b8−1`; payload is (u16, 0) pairs whose exact semantics are OPEN)
- **Skinning — per-batch bone bind REJECTED** (`../wwe-wrestlemania-xix/YOBJ-SKINNING-NOTES.md`): hierarchical/inverse-bind/translation-only/local-matrix transforms all scattered; 6 axis permutations all scattered. The elbow (rigid CAW part) renders coherent, so s16/64 is valid — wrestler batches need per-VERTEX weights from an unlocated table, or positions are delta-encoded. OPEN
- Note: `000_0.ymg` == `000_1.ymg` byte-identical (69,176 B) — the `_1` alt attire is texture-only

## 5. YANM Animation Format — Decoded (2026-10-13, PR #26)

Measured against 170 `ringmotion/*.yag` files; streaming from ISO. Full spec: `../wwe-wrestlemania-xix/YANM-FORMAT.md`. All fields big-endian.

**Header (56 bytes):** `YANM` magic; u32 payload size (file size − 56); `0x011F0000`; `0x08`; `0xCD89A39E`; `0x0010B4F0` @0x30 (constant, semantics open); **f32 seconds-per-tick** @0x3C (e.g. 0.0279688; clip seconds = tick_total × this; 0.0 in some files — not always valid); f32 ×3 anim params @0x40–0x48 (root-motion/blend candidates)

**Track directory — 29 × 32-byte records @0x50–0x3F0:** joint hash (matches `.ycg` group hash for 21/29 tracks), A-stream offset (0 = single track), B/key-stream offset, f32 ×3 (nonzero ⟺ dual track), w24 (nonzero ⟺ dual), key count / packed (ca,cb). All-zero terminator @0x3F0. Track hash sets DIFFER per clip.

**Key formats:**
- **Single track — 5-byte keys** `(s16 ch1, u8 dt, s16 ch2)`: dt is the middle byte and is a DELTA (0–255). Channel = **32767·sin(hinge angle)** → angle = asin(s16/32767); saturates ±90° (proven by circularity + small-angle smoothness tests)
- **Dual track — A: 4-byte keys** `(s16 value, u8 flags, u8 dt)`, **B: 5-byte keys**: A = bilateral COMMON-MODE hinge angle (asin encoding), B = per-side trims; `rec_i(t) = A(t) + B_i(t)` on the group's hinge axis; r²(A~B) ≈ 0.00–0.05 (independent component). Duals exist ONLY for symmetric-motion 2-record groups
- 21 tracks ↔ 21 `.ycg` joint-groups 1:1 (hash match); 8 track hashes appear in NO wrestler `.ycg` (0/154 files — identity open: 2nd performer / camera / prop / referee candidates)
- Per-track durations vary up to 2× within a clip (large-dt hold-key authoring variance); retarget handling: hold-last + clip

**Mapping evidence:** `docs/yanm-track-joint-map.json` (29-track table × 3 clips), `docs/yanm-task2-finish.json` (dual-A semantics, chain assignment, hinge axes), `docs/yanm-rec3-rule.json` (rec3 = −(rec1+rec2) proof), `docs/ycg-group-mapping.json`. Probe tools: `yanm_census.py`, `yanm_track_probe.py`, `yanm_keyseg.py`, `yanm_semantics.py`, `yanm_unitfit.py`, `yanm_gait.py`, `yanm_hashscan.py`.

## 6. Arenas — Decoded + Mapped to Western Heart

- **43 arena OBJ point clouds decoded** (see §4a; `arenas/`), extraction PR #20 merged
- **`ARENA-UNIVERSE-MAP.md`** (PR #18): ~45 arena configurations inventoried; **all 7 Western Heart stages mapped to WMXIX donors**. Principle: WMXIX gives **geometry** (arena layouts, wall structures, outdoor environments, cage frameworks); Eastern Mind gives **soul** (bitmaps, textures, atmosphere, meaning)
- Mapping summary: `bg/00` → Helix Palace (Stage 2, walled); `bg/01` → Octagonal Shrine Par-Fang (Stage 6, walled); `bg/02` → Phantom Marketplace (Stage 5); Revenge Mode outdoor slots (A/C/F/H/P/S/T, 35 env packages) → Plains of Chi-U / Tree of Life / Palace of Dreaming (open stages); `bg/bs/` backstage interiors → Helix interior rooms; `bg/cage/hell.pac` (Hell in a Cell) → **The Drill Wound** (Stage 7 secret — the most direct mapping in the set); `cage.pac` → cage-match concept; prop libraries (`object/` 61, `placard/` 51, `weapon/` 61) → stage dressing
- Decode priority: `hell.pac` → `bg/00` → `bg/01` → one open Revenge Mode environment → `bg/02` → remaining
- Pipeline: decoded arena → OBJ → Blender cleanup (strip WWE branding, rescale to 16.8-unit combat plane) → Eastern Mind retexture → Godot 4 import

## 7. CAW edit_data — Structure Mapped, Save Blocked (PR #27)

- `edit_data/MODEL/{Man,Woman}/{Category}/{style}_{variant}/{l0,r0}.ymg` — 1,213 part meshes (YOBJ v0x00030001, same as wrestler). 10 categories (Elbow, Face, Gears, Gloves, Hair, Knee, Lower_Body, Shoes, Upper_Body, Wrist); Man Face 77 styles / Hair 76 / Gears 140; Woman similar
- `edit_data/TEX/64gara/` — 1,469 part textures; `edit_data/COL/` — 8 `.ycg` (2× 2,356 B skeleton-size + 6 small palette/override files)
- Doc: `../wwe-wrestlemania-xix/docs/CAW-EDIT-DATA-WMXIX.md`
- **Blocked:** the created-wrestler SAVE lives on the GameCube memory card, not the ISO. Unblocking needs: Dolphin + ISO → create a CAW with known values → export the `.gci` → diff against the part-id tables. Without a real save, field order/string encoding/stats layout cannot be determined from the ISO alone

## 8. Retarget Pipelines — Proven

### YANM → Tekken 3 (Yukes path)
- **v1** (2026-10-12): `ringmotion/a000_0a.yag` (entrance, 13.93s) → King (BNS record 95); 465 frames @30fps; 6 ycg groups → T3 FK Euler joints; mean-subtraction overlay keeps King's stance, adds wrestling motion; output `docs/yanm_to_tekken3_v1.json` (+ plot). FK only, legs not retargeted
- **v2** (2026-10-13): leg/arm IK (FK the ycg chains → ankle/wrist targets → T3 normalized-skeleton IK channels, pure IK, no double-drive); hinge = ycg local X → world lateral; **leg tracks use half-angle encoding** (`hinge = 2·unwrap(atan2(c2,c1))`, ±180° — the c1 sign-flip "spikes" are the wrap, not glitches; legs swing −13°..+36° sane walk); arms use small-regime asin; hinge→Euler driven on the **Z channel** (sagittal pitch; v1's X was yaw); ycg y+ = R with chirality-preserving map. 574 frames @30fps (19.13s); **render-verified with own eyes** (`docs/retarget_v2_render.png`, `docs/retarget_v2_paths.png`). Tools: `yanm_to_tekken3_v2.py`, `fk_ycg.py`, `render_retarget_v2.py`. Doc: `docs/YANM-TEKKEN3-RETARGET.md`
- Open: knee DOF (YANM leg is 1-DOF); ycg forward sign; absolute ycg L/R proof (needs in-game pose); swivel modulation; root translation (YANM has no root track)

### AKI → Tekken 3 (No Mercy cross-engine path)
- **v1** (2026-10-13): No Mercy move `0x339A` (58 frames) → King; 19 × 1-DOF `PivotRotation` (s8 = degrees, calibrated: `Tekken_s16 = s8 × 182.04`); 9 AKI joints → T3 FK joints; source-vs-retarget motion correlations **0.69–1.0** (pelvis 1.000). This unlocks the ~1,360-clip AKI library for retarget
- Doc/tooling lives in the sister lane: `../wwf-no-mercy/AKI-TEKKEN3-RETARGET.md`, `../wwf-no-mercy/aki_to_tekken3.py`, `../wwf-no-mercy/aki_to_tekken3_v1.json`
- Cross-engine comparison: `../wwe-wrestlemania-xix/docs/YUKES-VS-AKI-ANIMATION.md` — AKI is frame-based (N × 98-byte frames, 25 fixed-order joints, s8 degrees + pivots, explicit root motion); Yukes is track-based (29 sparse delta-timed key streams, 21 1-DOF hinge groups, s16 sin-encoding, common-mode+trim bilateral factorization). Yukes = finer (finer resolution, ~10× more compact); AKI = broader (1,360 anims + move DB linkage)

## 9. Tools

`../wwe-wrestlemania-xix/tools/` (26 tools — streaming, ISO-safe unless noted):

| Tool | What it does |
|---|---|
| `gcn_fst.py` | Pure-stdlib GCN disc FST reader: `list` / `get <path>` / `extract <dir>` (streams from ISO) |
| `yukes_fmt.py` | Yukes format helpers (big-endian readers, `stream_file`) |
| `extract_all_arenas.py` | Extracts all 43 arena YMGs → OBJ point clouds (repo copy in `arenas/`) |
| `yobj_arena_extract.py` | Single-arena extractor (repo copy in `arenas/`) |
| `yobj_strips.py` | Wrestler YOBJ triangle-strip connectivity → OBJ + render (elbow, 000_0) |
| `yobj_diag.py`, `yobj_validate.py`, `yobj_v3_probe.py`, `yobj_batches.py`, `yobj_batch_semantics.py` | Batch-table probes and semantic validation |
| `ycg_parse.py`, `ycg_ymg_map.py`, `fk_ycg.py` | YCG joint-group parsing, ycg↔ymg mapping, ycg FK |
| `yanm_census.py`, `yanm_track_probe.py`, `yanm_keyseg.py`, `yanm_semantics.py`, `yanm_unitfit.py`, `yanm_gait.py`, `yanm_hashscan.py` | YANM track/key probes and semantic fits |
| `yanm_track_joint_map.py`, `yanm_task2_finish.py`, `yanm_task2b.py`, `yanm_rec3_rule.py` | Track→joint mapping, dual-A semantics, rec3 rule proof |
| `yanm_to_tekken3.py`, `yanm_to_tekken3_v2.py`, `render_retarget_v2.py` | YANM→Tekken3 retarget v1/v2 + render |

No Mercy-side tools for the AKI path: `../wwf-no-mercy/tools/anim_extract.py`, `../wwf-no-mercy/aki_to_tekken3.py`.

## 10. What's Blocked and Why

1. **Arena face indices** — u16 chunks at material index offsets are mixed data, not clean indices. Parse mesh descriptors at 0x0830+ to link vertex arrays → index arrays, or Poisson-reconstruct the point clouds. (Geometry is usable as point clouds; faces needed for real stage builds.)
2. **Full YANM channel mapping** — directory f32-triple + w24 semantics; A-stream first-8-bytes (header vs 2 keys); authoritative clip duration (`.atr` lead); per-clip hash-set → move-category mapping; identity of the 8 non-ycg track hashes. (Does NOT block retarget — the 21 mapped groups carry the wrestler's motion.)
3. **Wrestler per-vertex skinning** — per-batch bone bind matrices rejected by measurement; need the weight table or the true position-pool semantics. (Rigid CAW parts decode clean; skinned wrestlers need this.)
4. **CAW save-record layout** — blocked on a real Dolphin `.gci` memory-card dump (see §7).
5. **Revenge Mode slot→location identities** — which lettered slot (A0–A4, C0–C2, F1–F6, H3–H9, P0–P3, S0–S5, T0–T3) is the construction site vs parking lot vs mall. Decodes will identify visually; doesn't block the type-based universe mapping.
6. **`.tex` texture decoding** — texture format unexamined (TPL/TXTR check open).

## 11. Chimera Build Value

- **Wrestling Mode arenas:** WMXIX arena geometry (rings, cages, outdoor environments) feeds the Eastern Mind stage set — the universe map assigns each arena its destination (see `ARENA-UNIVERSE-MAP.md`)
- **Revenge Mode structure:** mission-based objectives outside the ring → template for Western Heart's arena-traversal missions
- **Create-a-Wrestler / Shopzone:** upgrade economy (attire, weapons, moves, ability points) informs the chimera customization meta-progression
- **YANM retarget pipeline:** proven path for bringing WMXIX wrestling animations onto chimera skeletons (v2: leg/arm IK, render-verified); AKI path gives the 1,360-clip No Mercy library the same door

## 12. Next Steps

1. Arena face indices → real stage geometry (parse mesh descriptors or Poisson reconstruction)
2. Assign decoded Revenge Mode slots to specific Western Heart stages (replaces the type-based mapping with slot-exact assignments)
3. Wrestler per-vertex skinning → fully assembled skinned wrestler meshes
4. Dolphin `.gci` dump → CAW save-record layout
5. YANM 8-unknown track identities (second performer / camera / prop / referee)
6. Wrestling Mode arena pass (separate from the Eastern Mind stage transformation — main show arenas kept closer to wrestling origins)
