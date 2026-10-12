# WWE WrestleMania XIX — Teardown

## Game #4 in Western Heart Chimera Build
- **Role:** Additional modes, arena traversal, Revenge Mode structure
- **Developer:** THQ (Yukes engine — different from AKI)
- **Platform:** Nintendo GameCube
- **Game ID:** GW9E78
- **ROM Status:** ✅ DOWNLOADED + VERIFIED 2026-10-12 — `WWE Wrestlemania XIX (USA).iso`
  (1,459,978,240 bytes, MD5 `c13c47a5ed24a675545c99a15e44529d` — matches source listing;
  disc header: Game ID `GW9E78`, name `WRESTLEMANIA XIX`, magic `C2339F3D`).
  Source: CDRomance (via browser task, no signup/payment needed).

## Download Sources (for parent browser delegation)
1. https://cdromance.org/gamecube/wwe-wrestlemania-xix-usa/ (Game ID GW9E78, MD5: c13c47a5ed24a675545c99a15e44529d)
2. https://www.gamulator.com/roms/gamecube/wwe-wrestlemania-xix (has "Direct" download option)
3. https://Coolrom.com/roms/gcn/40659/WWE_WrestleMania_XIX.php
4. https://www.freeroms.com/roms/nintendo_gamecube/wwe_wrestlemania_xix.htm

## Known Features (from research)
- ~40 WWE wrestlers on roster
- **Revenge Mode:** mission-based mode (not traditional story) — objectives in various settings beyond the ring
- **Create-a-Wrestler:** highly customizable, modify "every little nuance"
- **Create-an-Entrance:** more control than any wrestling game to date
- **WWE Shopzone:** spend earned money on attire, weapons, moves, ability points
- Improved graphics over WrestleMania X8, more realistic moves

## Key Differences from No Mercy (for Western Heart design)
- Yukes engine vs AKI engine — different animation philosophy
- GameCube hardware — higher poly, better textures than N64
- Revenge Mode arena traversal — fighting OUTSIDE the ring in various environments
- This informs the "Wrestling Mode" arena design in Western Heart

## TODO
- [x] Download ISO (verified MD5) — DONE 2026-10-12
- [x] Map file structure — DONE 2026-10-12 (streaming FST parse, no full extraction —
  disk at 89%, so no 1.4GB duplicate; tool reads directly from ISO offsets)
- [ ] Extract character models (YOBJ format decode — streaming via gcn_fst.py `get`)
- [ ] Decode YANM animation format
- [ ] Document Create-a-Wrestler save format (edit_data/ layout)
- [ ] Document Revenge Mode arena designs (bg/ arena sets)
- [ ] Compare Yukes vs AKI animation approach

## File Structure (mapped 2026-10-12 via tools/gcn_fst.py — pure-Python GCN FST reader)
- 5016 FST entries, 4222 files, 1.41 GB total (compressed/scrubbed ISO = 1.46 GB on disk)
- FST header note: on this disc the FST offset/size live at header 0x424/0x428
  (0x362F00 / 0x1A8A3), NOT 0x420 — tool handles this.
- `model/wrestler/` — 484 files: per-slot model groups `NNN_M` (slots 000–110 = 111 slots):
  `_0` always `.tex` + `.ymg` + `.ycg`; `_1` second variant (alt attire) on 66 slots;
  `_2`/`_3` on a handful. More slots than the ~40-man roster — extras likely CAW
  parts, managers, refs, divas.
- `ringmotion/` — 340 files: move animation pairs `.yag` (YANM skeletal anim, median
  38.6 KB) + `.atr` ("DATA" metadata, median 388 B — 16-byte records, describes its
  .yag companion). Letter groups: a=68, b=46, c=208, d=12 — likely move categories
  (attack/grapple/strike/special). Includes `cnv.bat` (build-time converter left on disc).
- `motion/*.mpc` — shared move packages (common, move, win, nyujo_ch entrance).
- `edit_data/` — 2690 files: CAW creation suite parts — MODEL/ (1213), TEX/ (1469), COL/ (8).
- `bg/` — 373 files: arena sets (per-arena `.ymg`/`.ycg`/`.tex` + `.pac` arena packages,
  `weapon/` 61, `object/` 61, `placard/` 51 — Revenge Mode out-of-ring environments here).
- `Entrance/` — Create-an-Entrance data (CamData.dat, EffData.dat, entpac.mpq).
- `viewer/` — dev-viewer assets (TestEffect.gef, motion/ test anims).
- `2d/`, `thp/` (videos), `tutorial/`, `paint_tool/` (CAW paint tool UI).

## Proprietary Format Magic (first structural pass)
- `.ymg` → **`YOBJ`** — YUKE's mesh/object format (models, arenas, ring).
  Sample `model/wrestler/000_0.ymg` (69,176 B): `59 4F 42 4A` = "YOBJ".
- `.yag` → **`YANM`** — YUKE's skeletal animation. Header: `59 41 4E 4D` "YANM",
  then u32 (payload size ≈ file size − header), constant `0x011F0000`, u32 = 8,
  then `0xCD89A39E`. Sample `ringmotion/a000_0a.yag` (22,674 B): header size 22,500.
- `.atr` → **`DATA`** — 16-byte records, per-animation attribute table (36–2532 B,
  median 388). Sample `ringmotion/a000_0a.atr` (218 B = 100-byte header + 8 records × 16?).
- `.ycg` — no ASCII magic (`00 00 00 2A ...`); small (2.3 KB) — skeleton/graph or
  camera data, always paired with `.ymg`.
- `.tex` — textures (need TPL/TXTR check), `.mpc` — move packages, `.pac` — arena packs.

## Tool: tools/gcn_fst.py
Pure-stdlib GCN disc FST reader. Modes: `list` (full file listing), `get <path>`
(extract single file by streaming from ISO — no full extraction, disk-safe),
`extract <dir>` (full tree — avoid at high disk usage).

## Tool: tools/yukes_fmt.py (new 2026-10-12)
Structural probe for YOBJ/YANM/YCG: streams files from ISO byte ranges (disk-safe),
prints u32/float header words, finds plausible file-internal offsets, scans for
ASCII section tags. Usage: `python3 tools/yukes_fmt.py <disc/path/file> [...]`.

## YOBJ (.ymg) structural decode v1 — MEASURED (sample: model/wrestler/000_0.ymg, 69,176 B)
- Header 64+ bytes of u32 fields. Confirmed internal offsets (u32 value < file size,
  target non-zero):
  - `[0x04]` → `0x10D80` (target blob `ddfd 7a6e dffb a6f5 0f46 3000 0000 0a8…`) —
    dense packed data = **vertex/index payload region** (last ~1.2 KB of file).
  - `[0x1C]` → `0x10704` (target `32 00 70 00 cc cc cc cc b2 b2 b2 ff …`) —
    GCN GX display-list region (0x32/0x98-class primitive bytes, matrix indices).
  - `[0x3C]` → `0x10D44` (target `04 07 07 07 00 50 04 0c 0c 5b f2 79 00 18 79 6d…`) —
    byte-triplet descriptor table = **vertex attribute format descriptors**.
  - `[0x38]` = `0xF360`, `[0x14]` = `0xF3B4` — mid-file section area.
- Section tags found in file (ASCII scans): `GCTC` @0xF370, `FIXE` @0xF384 —
  real section markers (not keyframe noise). Trailing `ABBB…/DDDD/EEEE/WWWW` runs
  @0x10D90+ are saturated-data patterns inside the vertex payload, not tags.
- HYPOTHESIS (not yet verified): layout = header → GCTC/FIXE section table (~0xF370)
  → GX display list (~0x10704) → attribute descriptors (~0x10D44) → vertex payload
  (~0x10D80). Next: decode GX DL command bytes to recover draw calls + attribute
  strides, then map vertices to triangles.

## .ycg structural decode v1 — MEASURED (sample: model/wrestler/000_0.ycg, 2,356 B)
- `[0x00]` = `0x2A` = **42** — matches the No Mercy wrestler-ID-table count (42) by
  coincidence; here it reads as a joint/entry count.
- From `0x14`: repeating records of the form `05 00000000 00000000` + four f32 that
  are all ±0.5 variants (`0x3F000001`=0.5, `0xBEFFFFFE`≈−0.5, 0.5001/−0.4999…) =
  **normalized rotation quaternions** (±0.5 components = 120°-class base rotations).
- Pairs like `415030A1`=13.01 f, `40EA72D6`=7.327 f, `413922DC`=11.57 f read as
  floats (plausible joint-scale or bone-length values); interleaved `00000005`
  counts suggest per-joint child-count fields.
- VERDICT (measured): `.ycg` is the **skeleton file** — joint count + per-joint
  local rotations (quats) + scalar params — always paired 1:1 with a `.ymg` mesh.
  This is the Western Heart retarget source: Yukes joint rotations → Tekken 3 bones.
  Next: segment the 42 records, recover parent/child hierarchy from the count fields.

## YANM (.yag) structural decode v1 — MEASURED (sample: ringmotion/a000_0a.yag, 22,556 B)
- `[0x04]` = `0x57E4` = 22,500; file size − 22,500 = **56 (0x38) = header size**.
- `[0x08]` = `0x011F0000` (constant), `[0x0C]` = `0x08`, `[0x10]` = `0xCD89A39E`
  (magic constant — same as noted in v0 pass).
- Section offsets in header (all land on non-zero data): `0x3E8`, `0x3EC`, `0x3F4`,
  `0x7E0`, `0xCC8`, `0xE6C`, `0x124C`, `0x1564`, `0x1574`, `0x1804`, `0x180C`, `0x1C80`.
- `0x3C` = `0x3CE51EBD` = **0.02797 as f32** — plausible per-frame delta (≈1/35.75 s;
  NTSC-adjacent; exact frame rate TBD). `0x40`–`0x48` = 0.5146 / 1.887 / −0.2931
  floats (anim params — root-motion or blend values, TBD).
- `0xCC8` region bytes (`59 02 ff 59 ff 59 02 bf c1 3f c1 3f 00 c1 3f c1…`) and
  `0x124C` (`00 01 00 02 00 01 00 02 ff f9 00 7e 00 ff f9 00…`) read as
  **s16 keyframe delta streams** (small signed 16-bit values around 0).
- `0x57F4` "ABAG/BAGAHGA…" hits are s16-stream byte patterns, not section tags.
- VERDICT (measured): 56-byte header + ~12 section offsets + s16 delta keyframe
  streams. Next: associate each offset with a joint from the .ycg skeleton
  (42 joints vs N tracks), recover frame count from the 0x3E8 track table.

## TODO (updated)
- [x] Download ISO (verified MD5) — DONE 2026-10-12
- [x] Map file structure — DONE 2026-10-12 (streaming FST parse, no full extraction)
- [x] YOBJ/YANM/YCG structural probe v1 — DONE 2026-10-12 (tools/yukes_fmt.py;
      header layouts + section offsets measured, see above)
- [ ] YOBJ: decode GX display list → vertex strides → triangle meshes (streaming)
- [ ] YCG: segment 42 joint records → parent/child hierarchy
- [ ] YANM: map tracks → joints → frame counts; decode s16 keyframe streams
- [ ] Document Create-a-Wrestler save format (edit_data/ layout)
- [ ] Document Revenge Mode arena designs (bg/ arena sets)
- [ ] No Mercy animation data isolation; recomp syms cross-ref (0x13E4A0 pointer table)
- [ ] Retarget test: Yukes anim → Tekken 3 model
- [ ] Compare Yukes vs AKI animation approach
