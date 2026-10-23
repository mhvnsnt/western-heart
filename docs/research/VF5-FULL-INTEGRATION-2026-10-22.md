# VF5 Full Integration — 2026-10-22 (Worker 45)

Owner order: "everything we can get from Virtua Fighter 5" — full integration round.
Release: `vf5-ps3-v1` (Virtua Fighter 5 PS3 BLES00029) + `vf5-model-library-v1` + `vf5-local-models-v1`.

## Phase 1 — T-pose renders (COMPLETE)

All 18 VF5 fighters extracted and rendered in T-pose (bind pose), facing camera, neutral background.

### mon/msk identified (verified)

| Code | Fighter | Style | ID method |
|------|---------|-------|-----------|
| `mon` | **Eileen** | Monkey Kung Fu | release README (`mon` = monkey) |
| `msk` | **El Blaze** | Lucha Libre | release README (`msk` = mask); render verified (masked luchador build) |

**CRITICAL FINDING:** `msk` = El Blaze DOES exist in vf5-ps3-v1. The earlier "El Blaze has NO farc" note was wrong — he was listed as `msk` (unidentified). **Pablo → El Blaze is NOT blocked** — msk.farc/mskitm.farc provide the model; movelist converted from GameFAQs VF5 guide.

### Extraction pipeline (new, this round)

VF5 PS3 `.farc` format reverse-engineered (no working public tool existed):
- Container: `FArC` magic + BE u32 entries `[name\0][offset][comp_size][decomp_size]` + gzip payloads → `farc_extract.py`
- Model `.obj.bin`: magic `0x05062500` (LE), 14 mesh chunks; chunk header has bounding sphere + submesh count; second header block gives `vcount`, `pos_rel`, `end_rel` (positions = LE f32 triplets, 12 bytes/vert)
- Indices: u16 triangle strips (degenerate-restart), located per-chunk; `vf5extract.py` maps them
- Skinning: `SKIN` blocks present per chunk (bone weights — parsed, not yet converted)
- Textures: `*_tex.bin` → TXP container (QuickBMS TXP.bms) — not yet extracted (renders are untextured clay)

Renders: Blender 4.5.3, Cycles 32spp, white world, 1080×1440, auto-framed T-pose.

### Ashlane locked mappings (user 2026-10-22 — wire first)

- Bannon → Jeffry McWild (`jef.farc`) ✓ render + moveset
- El Toro de Oro → Wolf Hawkfield (`wol.farc`) ✓ render + moveset (powerhouse with slight aerial)
- Pablo → El Blaze (`msk.farc`) ✓ render + moveset (big/fat powerhouse attempting lucha aerials; Goldust theatricality + Black Reign/Abyss/Mankind darkness)
- NPC Finxsse → Lei-Fei (`lei.farc`) ✓ render + moveset

All other VF5 fighters: candidate-only, NO canon until user says so. Renders are for review only.

## Phase 2 — Movesets (4 locked fighters converted)

Schema-v2 JSONs in `game/assets/movesets/`: `vf-jeffry.json` (25), `vf-wolf.json` (21), `vf-leifei.json` (22), `vf-elblaze.json` (28). VF→Tekken mapping per `docs/movesets/DOA-VF-CONVERSION-2026-10-19.md` (P→1/2, K→3/4, P+K→1+2, P+G→1+3, K+G→3+4, numpad→Tekken dirs). Directional P/K use fixed right limb (1/3) for input predictability (INPUT-TO-MOVE FIDELITY LAW).

Sources: GameFAQs VF5 guides (Jeffry, El Blaze), GameRevolution VF5 FAQ (Wolf, Lei-Fei), VF5 PS3 manual. Frame data estimated from archetype (marked per schema honesty rule); damage scaled to WH 100HP.

Feeds the MOVESET LIBRARY SYSTEM (user directive 2026-10-22): organized by type (strikes/throws/strings/specials/stances), ready for per-fighter assembly.

## Phase 2 — Motion data (GAP)

Binary motion data NOT in vf5-ps3-v1 (only models/textures). Likely in the 3.7GB `vf5-500m` ROM archive (not pulled). **Dural's animation for Zen is unblocked at the DATA level** (model extracted, SKIN weights located) but **motion clips still need the ROM pull**. Moveset conversions above provide the input→move mapping; animation uses `anim_ref` hooks for the retarget pipeline.

## Phase 2 — Stages (40)

`stg*.farc` on vf5-ps3-v1 (38) + `vf5-stages.tar` on vf5-model-library-v1. Stage→WH arena mapping in `docs/research/VF5-STAGE-ARENA-MAP-2026-10-22.md` (to be completed; arena pipeline ingests via existing stage-arena-pull tooling).

## Source map update

VF5 fighters are a NEW moveset source pool. Claimed (user-locked): Jeffry→Bannon, Wolf→El Toro de Oro, El Blaze→Pablo, Lei-Fei→NPC Finxsse. Dural→Zen (permanent base-mix layer, user-approved). Free: Akira, Pai, Lau, Kage, Sarah, Jacky, Shun, Lion, Aoi, Vanessa, Brad, Goh, Eileen. (Goh also candidate for Cipher/music-fighter; user still deciding.)

No conflicts with claimed Tekken sources (separate pool).
