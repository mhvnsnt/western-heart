# Alisa (ASA) T7 motion SOURCE pack — landed 2026-11-05

**Tag: SOURCE / not yet a playable FIGHT bank.**

## What this is
Owner (t91u) ordered Alisa files into both `cape-jones` and `western-heart`.
Prior docs said motion was PENDING-T8-PAKS. Exhaustive search found the real
Tekken 7 Alisa mothead pack already in `mhvnsnt/game-reverse-engineering`
under code **ASA** (roster ID 19 = Alisa Bosconovitch), not under the string
"alisa".

| File | Bytes | sha256 | Role |
|---|---:|---|---|
| asamot.bin | 2706996 | 0a74f027d7eda6a6cada9f5c409172aabb6b0e12e7aab357eec6e5beed3a9cb4 | T7 motbin binary |
| asamot.json | 7298226 | ec68b1c22dac66d3f18279e00dfe76d8a984f4328413b9b1687b9e49d5eeaf65 | Decoded motbin (2464 moves); meta.character_name=`[ALISA]`, meta.fighter=`capejones` |
| asarotsm.arc | 6025040 | cd879ae0b2b8acfd4289ec328af7bf15c75b505b6c663dd458221062f648bc92 | Rotation/state machine arc (bake input) |
| asa.mvl | 151836 | 9da230f288deee87094e73280f87deb90e09a03a2f72866eefc5adca1578f982 | Movelist |
| asa.nhb | 8376 | ada0a720b4d56c1fa449e90b672a390085b4d6449d35273647bf0718cc544594 | NUA header |
| asa.vbn | 22316 | 3b021c837bf46d74dabd03b5cdac63c0243ddae2bd64c18de3e878c369feed55 | NUA body |

**Provenance:** copied byte-exact from
`mhvnsnt/game-reverse-engineering` `teardown/tekken7-steam/tkdata/mothead/`
(bin/json/mask/movelist/nua) on 2026-11-05. Same schema as Pond/Ryusan T7 banks
(`docs/handoffs/SMUTBASE-T7-BANKS-2026-11-03.md`).

## FIGHT vs SHOW (ALISA-ANIM-GAP lock)
- These SOURCE files are intake for a future FIGHT bank at
  `game/assets/anim/t3/alisa/` + `game/assets/anim/t7/alisa/` after the
  offline bake pipeline (`t7_move_resolve.py` / `t7_anim64_to_c8.py` /
  `t7_move_bake.py` / `t7_generic_bank_bake.py`) runs against ASA + common.arc
  + shipping exe.
- Until that bake lands, Cyborg X / Cape still falls back to T3 gunjack for
  attack clips (logged in `game/data/cape-alisa-binding.json`).
- **Current FIGHT stance in use today:** `game/assets/anim/oss/cyborgx/stance.glb`
  (CMU 13_17 boxing guard, owner-approved pt128u 2026-10-23). Tag: **FIGHT**.
  This is NOT decoded Alisa T7 motion; do not relabel it as Alisa anim.

## Not in this pack
- Playable wh-anim `t3_*.json` / `rows.pack.json` Alisa bank (bake still required)
- Jungle Outpost (stg02) stage geometry (still missing — see PROOF)

<!-- intake CI re-trigger 2026-11-05 -->
