# Wrestling Teardown — Best-Of (Western Heart Chimera Build)

Owner directive 2026-10-12: the teardown best-of lives here too. Full measured
docs stay in `~/workspace/game-reverse-engineering/` (wwe-wrestlemania-xix/docs/,
wwf-no-mercy/docs/). This file is the concise actionable summary. Nothing below
is invented — every claim traces to measured bytes; open items are labeled OPEN.

## WWF No Mercy (N64, AKI engine) — ROM verified
`WWF No Mercy (USA) (Rev-A).z64`, 32MB. Community RE: chaotix610/wwfnomercy-docs,
Gadge64/WWFNoMercyRecomp (both cloned locally).

- Wrestler ID table @ ROM `0x168D930`: 42 entries, IDs 0–43 with gaps at 5/37.
  Full name→ID map in `wwf-no-mercy/docs/wrestler-id-table.json`.
- Move data segment @ `0x13E000`: u32 move-attribute records + float table +
  N64 RAM pointer table (`0x8014CDxx`) + 15KB u16 index run. (Earlier "move slot
  table" label was wrong — corrected.) Float table resolved: **7 position
  records `[0, x, y, z]` (camera/spawn)**; u16 run = **7,565 entries**
  (`0x13E4D4`–`0x141FEE`, plausibly move-index → data-index remap).
- Preset/theme table @ `0x168D8B4`, CAW presets @ `0x168D885`, creation-suite
  strings @ `0x168DD89+`.

### Create-a-Wrestler tables (2026-10-13, ROM-verified — directly reusable)
- **Entrance-music table @ `0x168D790`: 50 entries** `[u8 music_id][coded title]00`;
  wrestler themes in wrestler-table order + extras. `ORIGINAL 1`–`7` =
  music_ids `0x33`–`0x39` (51–57): the CAW original-theme slots. A CAW save
  record's entrance-music field indexes this table. Parser:
  `game-reverse-engineering/wwf-no-mercy/tools/caw_parse.py` (regenerates
  `caw-name-table.json`, `caw-categories.json`).
- **Part-string regions @ `0x168DD89`+ (15 categories)**: body types, elbow
  pads, masks, entrance attire, gloves, feet, wrists, hair (Bald…Mohawk 1-2),
  front hair, facial hair, hats, knee pads, accessories, ring attire.
  Record shape: `[u8 part_id][display name + inline codes][attr bytes][terminator]`
  (`FD F0` / `FB F0` / `FA F1` item terminators). `part_id`s are the values a
  CAW save record stores per slot — full id→name maps in the two JSONs.
- **Inline text codes: TWO classes** (not all zero-width). Zero-width:
  `FF` (47×, verified: BLACKMAN/ANGLE/ACOLYTES…), `EF 01 19 7F DF F7 FB
  BF` — not kerning-pair-specific, not Shift-JIS. Expansion tokens:
  `AA 01`→`"ERICAN"` (REAL AMERICAN!), `1C`→`"Buh"` (Buh Buh) —
  dictionary/compression escapes (dictionary not yet located). Trap: bytes
  like `<1C>` in the music table are usually the `music_id` byte, not text
  tokens. Full per-code table needs the renderer.

### Animation: KEYFRAME BANK ISOLATED (2026-10-13)
- Animations live in the ROM **FileTable @ `0x16C3238`** (19,462 entries;
  `FirstFile` = `0x1BD1B0`; format/locations confirmed against
  AKI-Club/VPWStudio). `FirstAnimationFileID` = `0x2DD9`,
  `FirstMoveAnimationID` = `0x3322`.
- **AkiAnimation format**: 4-byte `Toki2` + N×**98-byte frames**; each frame
  = 19× PivotRotation (12-bit pivot X, s8 rotation, 12-bit pivot Z) +
  OverallMovementXYZ + 6× MovementXYZ, fixed joint order (pelvis → arms).
  ~1,360 clips, 1–123 frames. Extractor:
  `game-reverse-engineering/wwf-no-mercy/tools/anim_extract.py`
  (`info`/`json`/`survey`) — file `0x2DD9` decodes to a smooth lunge,
  verified numerically.
- **Move→clip linkage**: move menu entries carry `AnimID` = file ID −
  `0x3322` (VPWStudio).
- OPEN: Toki2 semantics; triangle connectivity for YOBJ; retarget AKI
  19-joint clips onto Tekken skeletons (same pattern as YANM→Tekken3).

### Move tables + overlay map (2026-10-13)
- **0x13E4A0 = 10-pointer move-CATEGORY string table** (correction: the
  earlier "move-data index" used the wrong overlay context — B/C/D share
  vram `0x80106760`). Under ovl_d the pointers hit ROM `0x1437F0`+ exactly
  on: `Grappling`, `Standing`, `Running`, `Ground`, `Turnbuckle`,
  `Ringside`, `Apron`, `Irish Whip`, `Taunt`, `Double Team`
  (+`Favorite:`/`%d`/`best`). The `0x13E530` block is move-slot UI
  (`"No Data"` + u16 remap).
- **Move DB index @ `0xF5BF8`: 40 entries** (move-record ptr, count);
  move bank ~`0xF2390`–`0xF6390` (`04 00` records + `04 4B/4A/5F/…` params).
- **Overlay DMA table @ `0x539A0`** (36B entries): true ROM ranges —
  a `0x57310`–`0x81210`, b `0x81210`–`0xAE390`, c `0xAE390`–`0xFD250`, d
  `0xFD250`–`0x144BE0`, e `0x144BE0`–`0x1BD150` (bigger than dump.toml).
- OPEN: save-record byte layout (needs real emulator save file to diff
  against the id tables above).

## WWE WrestleMania XIX (GameCube, Yukes engine) — ISO verified
`WWE Wrestlemania XIX (USA).iso`, 1,459,978,240 B, MD5
`c13c47a5ed24a675545c99a15e44529d`. 4222 files mapped via streaming FST
(`tools/gcn_fst.py` — never extract the full ISO; disk-safe).

### Formats (all magic-verified)
- `.ymg` = **YOBJ** (mesh). `.yag` = **YANM** (skeletal animation).
  `.atr` = **DATA** (per-animation 16-byte metadata records). `.ycg` = **animation
  rig** (no magic, header u32 = 42; v3-verified 2026-10-12: 21 unique joint
  hashes matched by YANM tracks — separate from the 70-bone `.ymg` render rig).
  `.tex` = textures.

### The skeleton — FULLY DECODED (retargeting gold)
`model/wrestler/000_0.ymg` bone table: **70 bones**, 64-byte slots —
name | parent idx | pos xyz (f32) | euler xyz radians (f32) | bone length.
Hierarchy: Bip→Pelvis→Spine→Spine1→{Neck→Head→12 facial bones, L/R Clavicle→
UpperArm→{twist helper, Forearm→Hand→{15 finger bones/side}}};
Pelvis→{L/R Thigh→{twist, Calf→Foot→Toe0}}. L/R symmetric (verified).
Full table: `game-reverse-engineering/wwe-wrestlemania-xix/docs/WRESTLER-SKELETON.md`
+ `wrestler-skeleton-000.json`.
- `.ycg` is the **animation rig** (42 records, 21 unique joint hashes —
  v3 verified 2026-10-12): 21 of 29 YANM track hashes match it exactly.
  The 70-bone `.ymg` is the separate render rig. ycg hash sets are universal
  across all 111 wrestler slots → one YANM decode retargets everywhere.

### Models
- **Vertex positions CRACKED (2026-10-13, eye-verified).** `000_0.ymg`:
  batch-table s16x3 runs ARE the positions — 606 verts, /64 dequant →
  0–30 units, point cloud renders as coherent character geometry
  (`tools/yobj_validate.py` streams from ISO, writes OBJs + check renders).
  CAW elbow part: 148 verts as u16x3 @ file `0x4D8` (curved-shell =
  elbow-pad shape). Correction: the v3 "150-triangle index list (max idx
  1224)" was a misread — 1224 was a coordinate; the region is descriptor +
  positions.
- **Triangle connectivity CRACKED (2026-10-13, eye-verified).** YOBJ meshes
  use **no index buffers** — triangles are implicit **triangle strips**:
  each vertex run is strip-ordered (ladder/zigzag), triangles = consecutive
  triples (v_i,v_{i+1},v_{i+2}) within jump-delimited strips (split at edge
  jumps > max(400, 4×median); separators are single near-origin verts).
  Each strip renders as a smooth surface patch (verified per-strip).
  Exports: `wwe-wrestlemania-xix/objs/wrestler_000_0.obj` (606v, 58 strips,
  383 tris), `objs/elbow_me0_000_l0.obj` (148v, 14 strips, 113 tris);
  tool `tools/yobj_strips.py`.
- OPEN: assembling `000_0`+`000_1`; strip→world needs skinning (bone
  matrices) — strips are smooth but scattered without it.
- `model/wrestler/`: 111 slots (000–110), each `_0` = base (`.tex`+`.ymg`+`.ycg`),
  `_1`/`_2` = alt attires. More slots than the ~40 roster (CAW parts, staff).
- YOBJ header map (measured): bone table @0xF3B4 (71 slots), material table
  @0x10704 (57 records, RGBA + u16 index-chunk offsets), texture-name table
  @0x10574, per-bone skin batch table @0x7CA0.

### Animations
- `ringmotion/`: YANM skeletal anims (`.yag` magic YANM) + `.atr` metadata.
- YANM track directory decoded (29×32B records): **21 tracks = the 21
  joint-groups of the .ycg animation rig** (hash-matched, universal across
  wrestler slots) + 8 unknown static tracks (2nd performer/camera/prop?).
- Key format: 5B keys = (32767·sin α, dt, 32767·sin β), dt = middle byte
  (delta); hinge angle = asin(s16/32767); header [0x3C] = seconds/tick.
- **Anatomical mapping (task-3, 2026-10-12)**: ycg groups → body parts with
  confidence: **BD5B2A59/5259 = LEGS (HIGH)** — segment ratio 0.991 =
  thigh:calf 1.004, dominant gait motion; **6198F425/4D5 = ARMS
  (MED-HIGH)** — ratio 1.179 ≈ upperarm:forearm 1.136; two extra mirrored
  3-hinge chains (7AD45E02, 6865B2C0) UNRESOLVED; core/singles mostly
  unresolved. Full table:
  `~/workspace/game-reverse-engineering/wwe-wrestlemania-xix/docs/ycg-group-mapping.json`.
- Retargeting path: YANM track → ycg group → anatomical joint → Tekken
  skeleton joint. **v1 WORKING 2026-10-12**: `yanm_to_tekken3.py` plays
  entrance `a000_0a.yag` on Tekken 3 King — 465 frames @30fps of 49-channel
  pose vectors (base = King stance, YANM motion overlaid on pelvis/chest/
  hips/head/shoulders; verified numerically + motion plots). **v2 DONE
  2026-10-13**: `yanm_to_tekken3_v2.py` — leg/arm IK (YANM ycg chain FK →
  ankle/wrist trajectories → Tekken3 normalized-skeleton IK targets;
  ankles ±150 fwd/back, ±50 up/down), hinge→Euler corrections measured:
  hinge axis = ycg local X → world lateral Y, leg tracks use half-angle
  quaternion-style encoding (hinge = 2·atan2 unwrap to ±180°, hips swing
  −13°..+36°), arms use small-regime asin, YANM sagittal hinge → T3
  **Z-channel** (v1's X was yaw — wrong), ycg→T3 map `T3=(−ycg_x,−ycg_z,
  −ycg_y)` det=+1 chirality-preserving, ycg-R→T3-R. 574 frames @30fps
  (19.13s), pelvis −41°..0°, chest −80°..0° (deep entrance bow),
  head 0°..+47° — render-verified, no explosions/NaNs.
- OPEN: YANM knee DOF (undecoded if any); ycg forward sign; absolute ycg L/R
  proof (needs in-game pose); swivel modulation; root translation
  (YANM has no root track — entrances stay in place).
- They are ENTRANCE animations — disc `ringmotion/cnv.bat` shows Yukes'
  `yma2yag` converting `Nyujo_YMA/*.yma` (Nyujo = 入場 = "entrance") → `*.yag`.
  Letter groups a/b/c/d = 68/46/208/12; median `.yag` 38.6KB.
- YANM: 56-byte header ("YANM", payload size, `0x011F0000`, `0xCD89A39E`);
  **track directory at 0x50–0x3EF: 29 × 32B records** — (u32 joint_hash,
  u32 trackA_off|0, u32 keystream_off, u32 0, f32×3, u32 keycount_word).
  Single tracks: keycount keys × 5B (s16 x, u8 dt, s16 y) at keystream_off.
  Dual tracks: keycount packs (countA<<16)|countB; track A = countA × 4B
  (s16,s16) keys, track B = countB × 5B keys.
- OPEN: dual-A value semantics; 2ch→3rec assignment; ycg-Y→L/R; 8 unknown tracks.

### Create-a-Wrestler (directly reusable)
- `edit_data/MODEL/{Man,Woman}/{Elbow,Face,Gears,Gloves,Hair,Knee,Lower_Body,Shoes,Upper_Body,Wrist}/…/{l0,r0}.ymg`
- Parts ARE YOBJ files — the same parser as base models extracts them.
- `edit_data/TEX/` (1469) + `edit_data/COL/` (8) = part textures/colors.

### Arenas (Revenge Mode / out-of-ring)
- `bg/`: 373 files — per-arena `.ymg`/`.ycg`/`.tex` + `.pac` packages,
  `weapon/` (61), `object/` (61), `placard/` (51). OPEN: arena doc.

## What this unlocks for Western Heart
1. **Retargeting**: the 70-bone Yukes skeleton (with bind transforms) is the
   source rig — map to Tekken bones, then play YANM tracks on Tekken models.
2. **CAW parts**: YOBJ part files drop straight into a creation suite.
3. **AKI systems**: No Mercy's move-attribute tables + CAW preset format inform
   the wrestling-systems layer.
4. Next: crack YOBJ vertex positions → export reference mesh; task-4 retarget
   test (Yukes YANM → Tekken 3 King model) in progress.

## Sources (steal-like-an-artist)
Binaries cataloged with SHA-256 in `teardown/TEARDOWN-SOURCES.md`. Full RE docs:
`~/workspace/game-reverse-engineering/wwe-wrestlemania-xix/docs/WMXIX-TEARDOWN.md`,
`~/workspace/game-reverse-engineering/wwf-no-mercy/docs/CHARACTER-DATA.md`,
`~/workspace/game-reverse-engineering/wwf-no-mercy/docs/CAW-EDIT-DATA.md`,
`~/workspace/game-reverse-engineering/wwf-no-mercy/docs/ANIMATION-ISOLATION.md`.
