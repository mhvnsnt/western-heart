# TEKKEN 3 — Teardown for Western Heart

**Role in Chimera Build:** Legacy/retro mode. Tekken 3 versions are ALT COSTUMES — same character slot, retro skin selectable as an attire. Retro King vs modern King mirror matches possible. Tekken 3 never shows unless the player picks it.

**Source:** Owner-supplied "Tekken 3 (Everything Unlocked).zip" (494MB, patched ROM; SHA-256 cataloged in `teardown/TEARDOWN-SOURCES.md`, raw dump stays local)
**Teardown status:** Complete — geometry, textures, motion bank, and all 15 stage panoramas extracted. Pose sampling still blocked at EXE tables (owner decision pending).
**Last updated:** 2026-10-13

---

## What's Extracted and Documented

### Disc Structure (mapped)
- 6 ISO files: `SLUS_004.02` (1.2MB MIPS exe), `TEKKEN3.BNS` (37MB model/texture bank), `TEKKEN3.XAS` (488MB XA audio/video; raw dump local-only, SHA-256 in `teardown/TEARDOWN-SOURCES.md`)
- BNS parsed: 303-record index, 297 valid, **67 model records** (52 with `3DMK` magic + 15 candidates), **8,556 TIM textures**
- Record index: `bns-table.pkl` (list of `(id, sector, size)`; byte offset = sector × 2048). Full model inventory: `model-inventory.json` / `model-inventory.csv`; texture inventory: `tim-inventory.json`

### Character Geometry — King Extracted, All 7 Fighters Mapped
- Character name table at `SLUS_004.02` offset `0x129ac`: PAUL(0), LAW(1), LEI(2), KING(3), YOSHIMITSU(4), NINA(5), HWOARANG(6), XIAOYU(7), EDDY(8), JIN(9), JULIA(10), KUMA(11), BRYAN(12), HEIHACHI(13), OGRE(14), MOKUJIN(15), GUN JACK(16), GON(17), ANNA(18), DOCTOR B.(19), PANDA(20), TIGER(21)…
- **BNS ID = 71 + (index × 8), P2 = +4.** Verified by extraction on two data points: BNS 87 = LEI WULONG (the "King" misidentification, corrected 2026-10-12), BNS 95/99 = real King (geometry + 59 textures match).
- **Correction 2026-10-13:** four BNS IDs circulated earlier were wrong (they pointed at other characters' slots). Correct values re-derived from the USA name-table bytes:
  | Fighter | Name idx | BNS P1/P2 |
  |---|---|---|
  | King | 3 | 95 / 99 |
  | Jin | 10 | 151 / 155 |
  | Yoshimitsu | 4 | 103 / 107 |
  | Heihachi | 15 | 191 / 195 |
  | Bryan | 14 | 183 / 187 |
  | Gun Jack | 18 | 215 / 219 |
  | Xiaoyu | 7 | 127 / 131 |
- **Correction 2026-10-20 (verification lane):** the Jin / Heihachi / Bryan / Gun Jack rows above were themselves wrong in the 2026-10-13 "correction" (143/147, 175/179, 167/171, 199/203) and are fixed here to the values in `docs/BNS-ORGANIZATION-PATTERN.md`, which the tree proves: the model folders are `models/jin151`, `models/heihachi191`, `models/bryan183`, `models/gunjack215`. Root cause: the name-index list in "Character Geometry" above omits TIGER (index 9) and PANDA (index 13), shifting every later index; the pattern doc's name table (…EDDY 8, TIGER 9, JIN 10, JULIA 11, KUMA 12, PANDA 13, BRYAN 14, HEIHACHI 15, OGRE 16, MOKUJIN 17, GUN JACK 18, GON 19, ANNA 20) governs. That list itself is flagged, not rewritten wholesale — see `docs/FULL-WIRING-VERIFICATION-2026-10-20.md` §7. Also superseded since this doc's 2026-10-13 update: pose sampling is no longer blocked (the USA EXE tables are verified and in use) and all 20 character motion banks + the common bank are extracted — see `CANON-CONVERSION.md` §5 (PR #382).
- King geometry: 27 rows, 21 active parts, 0 unresolved seams. Files: `models/king95/king95.kmd`, `king95_parts.obj`, `renderdata.pkl`, part montage, 2 sampled stance poses
- **Characters are ~27 separate rigid mesh parts in a hierarchy — NO vertex skinning.** Each part parented to one joint, overlapping at joints like action figures.

### Textures
- King's 59 real TIM textures (IDs 6213–6271) extracted as PNGs: jaguar spots, blue pants, jaguar mask, purple trunks w/ gold design, gold boots → `renders/king/textures/` (103 PNGs incl. adjusted variants)
- TIM inventory of the whole bank: `tim-inventory.json`; sample TIM decodes: `tim-output/`

### Motion Bank — Partial
- King's motion bank `divmot03` extracted from TEKKEN3.BNS (BNS ID 283) → `animations/divmot03_king.bin`
- Analytic motion-bank pose sampler built (`tools/local/pose_sample_analytic.py`, uniform cubic B-spline basis)
- Sampled King stance poses slots 0 and 2 frame 0 → `models/king95/king95_stance0_pose.json`, `king95_stance2_pose.json`
- KMD parser: `tools/local/kmd_parse.py`

### Stages — All 15 Extracted (2026-10-13)
- Fight stages 0–14: panorama TMD = BNS 56–70, floor/texture ARC = BNS 36–50. (Stages 15–19 are Tekken Force / Tekken Ball tile-map modes — no panorama TMD.)
- Parser ported from tekken3remake `tools/remake_import/stage.py` → `tools/local/extract_stages.py` (headless, geometry only — the full pipeline needs its Disc/Vram/atlas/sources modules).
- Verified parse: **12,909 verts / 8,014 packets / 36 objects per TMD**, all 15 headers check out. King's stage (11, `l`) renders as a proper box room (±1242 walls, −769…513 height) — eyeball-verified.
- Output: `stages/<letter>/stg_<letter>_panorama.obj` (v/vt/f, UVs 0–1 across the 256px VRAM page) + `stage.json` (cell, extents, counts, home stage, BNS ids) per stage.
- Stage table: 0a Paul/Bryan, 1b Law/Kuma/Panda, 2c Yoshimitsu/Mokujin, 3d Xiaoyu, 4e Hwoarang, 5f Lei, 6g Ogre/True Ogre, 7n Xiaoyu/Jin, 8i Jin, 9j Nina/Anna/Gun Jack, 10k Eddy/Tiger, 11l **King**, 12m Julia/Heihachi, 13t Gon, 14u Doctor B.
- Textured panoramas (atlas PNGs) and floor tiles still need the full tekken3remake `remake_import` pipeline run against a disc image — geometry is done, texturing is the remaining step.

### Docs (in `teardown/tekken3/docs/`)
- `TEKKEN3-ARCHITECTURE.md` — disc layout, BNS format, 3DMK models
- `TEKKEN3-RIG-LESSONS.md` — rigid-part rig method (no skinning)
- `REVERSE-ENGINEERING-PLAYBOOK.md` — reusable RE methodology
- `BNS-ORGANIZATION-PATTERN.md` — BNS index structure
- `3DMK-MODEL-MAPPING.md` — model record mapping

### Tools (in `teardown/tekken3/tools/`)
- `tools/local/kmd_parse.py` — 3DMK/KMD parser
- `tools/local/pose_sample_analytic.py` — analytic motion-bank pose sampler
- `tools/local/extract_stages.py` — headless stage panorama extractor (new)
- `tools/tekken3recompiled/` — pulled-in open-source Tekken 3 PC recompile project (its 150MB `mods/assets/` bulk stays local per `teardown/TEARDOWN-SOURCES.md`)

### T3 vs T7 Comparison
- T3 ≈ ~1K tris/fighter, 20–27 rigid parts, no skinning, 32×32 textures
- T7 = UE4 smooth-skinned, tens of thousands of tris
- PSP models (Tekken 6) are ~1/4 poly of PS3 but same skeleton/proportions/animations

---

## What's Blocked and Why

**Full-body pose sampling: needs_owner (attempts=3)**

Requires locating these tables in USA `SLUS_004.02` and porting `pose.py`'s ExeTables:
- `EULER_SLOTS`, `LIMB_BASIS`, `SKELETON_OFFSETS`, `LIMB_OFFSETS`, `SIN_TABLE`, `SQRT_TABLE`

USA EXE pose/motion tables shifted −0x424 vs Japan Rev.1 (known offsets: LIMB_BASIS 0x80096EAC, SKELETON_OFFSETS 0x80096ECC, LIMB_OFFSETS 0x80096EFC, SPLINE_TABLE_BASE 0x8009671C).

This is a heavy reverse-engineering step, not a quick task. Parked awaiting owner direction.

**Remaining character extractions:** Jin (151/155), Yoshimitsu (103/107), Heihachi (191/195), Bryan (183/187), Gun Jack (215/219), Xiaoyu (127/131) — geometry extraction pipeline proven on King, can repeat once pose system is unblocked. (BNS IDs corrected 2026-10-20 per the note in "Character Geometry" above; the pose system has since been unblocked — see `CANON-CONVERSION.md` §5.)

---

## What the Chimera Build Gets

1. **Retro alt costumes** — all 7 named fighters get Tekken 3 retro skins (BNS IDs mapped, King fully extracted)
2. **Rigid-part rig method** — "clay pieces on a wire skeleton" — no weight painting needed. Informs the Statue-to-Fighter tool.
3. **Motion data** — authentic Tekken 3 animations once EXE tables are ported
4. **Low-poly base** — ~1K tri models useful for mobile/web performance targets
5. **Stage panoramas** — all 15 fight-stage backdrops as OBJs for retro stage select / backdrop reference

---

## Next Steps

1. Owner decision: invest in EXE table porting, or accept geometry-only extraction
2. If unblocked: extract remaining 6 fighters' geometry + textures (BNS IDs verified above)
3. If unblocked: full motion bank extraction → animation pipeline
4. Run the full tekken3remake `remake_import` pipeline for textured stage panoramas + floor tiles (geometry already in repo)
5. Render all 7 fighters at 1:1 for owner review → Gemini reskin workflow
