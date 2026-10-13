# TEKKEN 3 — Teardown for Western Heart

**Role in Chimera Build:** Legacy/retro mode. Tekken 3 versions are ALT COSTUMES — same character slot, retro skin selectable as an attire. Retro King vs modern King mirror matches possible. Tekken 3 never shows unless the player picks it.

**Source:** Owner-supplied "Tekken 3 (Everything Unlocked).zip" (494MB, patched ROM)
**Teardown status:** Partial — geometry extracted, motion bank extracted, pose sampling blocked at EXE tables
**Last updated:** 2026-10-13

---

## What's Extracted and Documented

### Disc Structure (mapped)
- 6 ISO files: `SLUS_004.02` (1.2MB MIPS exe), `TEKKEN3.BNS` (37MB model/texture bank), `TEKKEN3.XAS` (488MB XA audio/video)
- BNS parsed: 303-record index, 297 valid, **67 model records** (52 with `3DMK` magic + 15 candidates), **8,556 TIM textures**

### Character Geometry — King Extracted
- King's real BNS records identified: **BNS 95/99** (P1/P2). Character name table at `SLUS_004.02` offset `0x129ac`: PAUL(0), LAW(1), LEI(2), KING(3)... BNS ID = 71 + (index × 8), P2 = +4
- **Correction:** The "King" shown earlier (BNS record 87) was actually LEI WULONG. Corrected 2026-10-12.
- King's 59 real TIM textures (IDs 6213–6271) extracted as PNGs: jaguar spots, blue pants, jaguar mask, purple trunks w/ gold design, gold boots
- King geometry: 27 rows, 21 active parts, 0 unresolved seams. Files: `models/king95/king95.kmd`, `king95_parts.obj`, `renderdata.pkl`, part montage
- **Characters are ~27 separate rigid mesh parts in a hierarchy — NO vertex skinning.** Each part parented to one joint, overlapping at joints like action figures.

### Motion Bank — Partial
- King's motion bank `divmot03` extracted from TEKKEN3.BNS (BNS ID 283) → `animations/divmot03_king.bin`
- Analytic motion-bank pose sampler built (`tools/local/pose_sample_analytic.py`, uniform cubic B-spline basis)
- Sampled King stance poses slots 0 and 2 frame 0 → `king95_stance0_pose.json`, `king95_stance2_pose.json`

### Docs (in `game-reverse-engineering/tekken3/docs/`)
- `TEKKEN3-ARCHITECTURE.md` — disc layout, BNS format, 3DMK models
- `TEKKEN3-RIG-LESSONS.md` — rigid-part rig method (no skinning)
- `REVERSE-ENGINEERING-PLAYBOOK.md` — reusable RE methodology
- `BNS-ORGANIZATION-PATTERN.md` — BNS index structure
- `3DMK-MODEL-MAPPING.md` — model record mapping

### T3 vs T7 Comparison
- T3 ≈ ~1K tris/fighter, 20–27 rigid parts, no skinning, 32×32 textures
- T7 = UE4 smooth-skinned, tens of thousands of tris
- PSP models (Tekken 6) are ~1/4 poly of PS3 but same skeleton/proportions/animations

---

## What's Blocked and Why

**Status: needs_owner (attempts=3)**

Full-body pose sampling requires locating these tables in USA `SLUS_004.02` and porting `pose.py`'s ExeTables:
- `EULER_SLOTS`, `LIMB_BASIS`, `SKELETON_OFFSETS`, `LIMB_OFFSETS`, `SIN_TABLE`, `SQRT_TABLE`

USA EXE pose/motion tables shifted −0x424 vs Japan Rev.1 (known offsets: LIMB_BASIS 0x80096EAC, SKELETON_OFFSETS 0x80096ECC, LIMB_OFFSETS 0x80096EFC, SPLINE_TABLE_BASE 0x8009671C).

This is a heavy reverse-engineering step, not a quick task. Parked awaiting owner direction.

**Remaining character extractions:** Jin (BNS 151/155), Yoshimitsu (103/107), Heihachi (191/195), Bryan (183/187), Gun Jack (215/219), Xiaoyu (127/131) — geometry extraction pipeline proven on King, can repeat once pose system is unblocked.

---

## What the Chimera Build Gets

1. **Retro alt costumes** — all 7 named fighters get Tekken 3 retro skins
2. **Rigid-part rig method** — "clay pieces on a wire skeleton" — no weight painting needed. Informs the Statue-to-Fighter tool.
3. **Motion data** — authentic Tekken 3 animations once EXE tables are ported
4. **Low-poly base** — ~1K tri models useful for mobile/web performance targets

---

## Next Steps

1. Owner decision: invest in EXE table porting, or accept geometry-only extraction
2. If unblocked: extract remaining 6 fighters' geometry + textures
3. If unblocked: full motion bank extraction → animation pipeline
4. Render all 7 fighters at 1:1 for owner review → Gemini reskin workflow
