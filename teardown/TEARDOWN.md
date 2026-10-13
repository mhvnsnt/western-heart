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
  table" label was wrong — corrected.)
- Preset/theme table @ `0x168D8B4`, CAW presets @ `0x168D885`, creation-suite
  strings @ `0x168DD89+`.
- OPEN: isolate wrestler animation data; cross-ref recomp syms for the
  `0x13E4A0` pointer table; FF control-byte semantics in preset tables.

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
- `model/wrestler/`: 111 slots (000–110), each `_0` = base (`.tex`+`.ymg`+`.ycg`),
  `_1`/`_2` = alt attires. More slots than the ~40 roster (CAW parts, staff).
- YOBJ header map (measured): bone table @0xF3B4 (71 slots), material table
  @0x10704 (57 records, RGBA + u16 index-chunk offsets), texture-name table
  @0x10574, per-bone skin batch table @0x7CA0.
- OPEN: vertex position buffer + dequantization (quantized s8/s16; index buffers
  located, position array not yet). No mesh OBJ exported yet.

### Animations
- `ringmotion/`: 340 files — `.yag` (YANM, median 38.6KB) + `.atr` companions.
  **They are ENTRANCE animations** — disc `ringmotion/cnv.bat` shows Yukes'
  `yma2yag` converting `Nyujo_YMA/*.yma` (Nyujo = 入場 = "entrance") → `*.yag`.
  Letter groups a/b/c/d = 68/46/208/12.
- YANM: 56-byte header ("YANM", payload size, `0x011F0000`, `0xCD89A39E`);
  **track directory at 0x50–0x3EF: 29 × 32B records** — (u32 joint_hash,
  u32 trackA_off|0, u32 keystream_off, u32 0, f32×3, u32 keycount_word).
  Single tracks: keycount keys × 5B (s16 x, u8 dt, s16 y) at keystream_off.
  Dual tracks: keycount packs (countA<<16)|countB; track A = countA × 4B
  (s16,s16) keys, track B = countB × 5B keys. 8 static 1-key tracks use
  hashes in no wrestler's ycg (camera/prop/2nd-performer candidates, open).
- OPEN: exact channel→quat-component mapping (dual-track semantics, dt time
  unit); ycg-group → ymg-bone anatomical mapping; then the Tekken 3 retarget
  test.

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
4. Next: crack YOBJ vertex positions → export reference mesh; decode YANM
   tracks → first retarget test onto a Tekken 3 model.

## Sources (steal-like-an-artist)
Binaries cataloged with SHA-256 in `teardown/TEARDOWN-SOURCES.md`. Full RE docs:
`~/workspace/game-reverse-engineering/wwe-wrestlemania-xix/docs/WMXIX-TEARDOWN.md`,
`~/workspace/game-reverse-engineering/wwf-no-mercy/docs/CHARACTER-DATA.md`.
