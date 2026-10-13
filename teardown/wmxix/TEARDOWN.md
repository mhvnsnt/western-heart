# WWE WRESTLEMANIA XIX — Teardown for Western Heart

**Role in Chimera Build:** Wrestling Mode — modes, arena traversal, Revenge Mode structure.
**Developer:** THQ (Yukes engine — different philosophy from No Mercy's AKI engine)
**Platform:** Nintendo GameCube (Game ID `GW9E78`)
**Last updated:** 2026-10-13 (teardown sweep)

---

## What's Extracted and Documented

### ISO — Downloaded + Verified
- `WWE Wrestlemania XIX (USA).iso` (1,459,978,240 bytes, MD5 `c13c47a5ed24a675545c99a15e44529d` — matches source listing; disc header name `WRESTLEMANIA XIX`, magic `C2339F3D`)
- Source: CDRomance (via browser task, no signup/payment). Mirrors: gamulator.com, Coolrom, freeroms
- Full listing in `wwe-wrestlemania-xix/docs/WMXIX-FILE-LISTING.txt` and research doc `WMXIX-TEARDOWN.md`

### File Structure — Mapped
- Streaming FST parse (no full extraction): **5,016 entries, 4,222 files, ~1.41GB**
- Tooling: `wwe-wrestlemania-xix/tools/gcn_fst.py` (FST reader), `yukes_fmt.py` (Yukes format helpers)

### Arenas — Mapped, Decode In Progress
- Main show arenas inventoried: `bg/00` (RAW, 00.ymg 304KB), `bg/01` (SmackDown, 279KB), `bg/02` (PPV/WrestleMania, 230KB) plus `_add/ent/gt/light/scr` variants and `.tex` texture banks
- `ARENA-UNIVERSE-MAP.md` (this dir): maps each WMXIX arena → Eastern Mind stage target. Principle: WMXIX gives us **geometry** (arena layouts, wall structures, outdoor environments, cage frameworks), Eastern Mind gives us **soul** (bitmaps, textures, atmosphere, meaning)
- **ACTIVE LANE (2026-10-13):** `wmxix-arena-decode` — validating the **/64 fixed-point vertex hypothesis** for YOBJ vertex dequantization. Approach documented at `~/workspace/tools/wmxix-mesh-decode/APPROACH.md`

### Wrestler Data — Decoded
- Skeleton + YANM animation format decoded; **YANM→Tekken 3 v2 retarget** (leg/arm IK, half-angle decode, Z-channel pitch, L/R resolved, render-verified) committed to western-heart main (bbcf8fe)
- Roster: ~40 WWE wrestlers. Revenge Mode: mission-based objectives in settings beyond the ring

---

## What's Blocked and Why

- **YOBJ vertex positions not yet decoded** — dequantization hypothesis (divide-by-64 fixed-point) under validation by the active arena-decode lane. Until confirmed, arena geometry is mapped but not rebuildable.
- No Mercy animation keyframe bank and per-code text-engine semantics (sister No Mercy lane) are open but do not block WMXIX arena work.

---

## Chimera Build Value

- **Wrestling Mode arenas:** WMXIX arena geometry (rings, cages, outdoor environments) feeds the Eastern Mind stage set — the universe map already assigns each arena its destination
- **Revenge Mode structure:** mission-based objectives outside the ring → template for Western Heart's arena-traversal missions
- **Create-a-Wrestler / Shopzone:** upgrade economy (attire, weapons, moves, ability points) informs the chimera customization meta-progression
- **YANM retarget pipeline:** proven path for bringing WMXIX animations onto chimera skeletons

---

## Next Steps

1. Finish YOBJ vertex validation (arena-decode lane) → decode all arena YMG meshes
2. Map remaining `bg/` slots + backstage/environments (Revenge Mode traversal zones)
3. Wrestler YANM motion capture → chimera retarget pipeline (Tekken-3-style IK rig pattern)
4. Consolidate `wmxix/` + `wwe-wrestlemania-xix/` dirs into one canonical teardown home
