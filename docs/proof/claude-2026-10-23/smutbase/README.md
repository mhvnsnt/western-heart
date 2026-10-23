# SmutBase fighters: rigs wired (Chatur, Pond, Megami, Menajerii) — 2026-10-23, Claude session

Owner: "Rig the smutbase models they count just as good as tripo pulls, models we hand choose as the models for
the character while others ladders behind them".

## State before

All six SmutBase fighters (Chatur/Rahkasa, Pond/Tsuyu Asui, Megami/Parvati, Menajerii/Vixen, Ryusan/Mina Ashido,
Tobi/Miruko) had their playable keys on the unskinned `model.glb`, so they stood frozen in fights. Rigged builds
existed (`8c4fef1b3`, `model-rigged.glb`, 52 joints) but were never wired, and the rigging report says they were
"built facing −Z" because "the game assumes every model rests facing −Z". That is backwards: the game's convention is
+Z (`game/assets/models/model-facing.json` note), and a −Z entry turns the model 180°.

## What the renders show (viewed)

- `static_four_views_smutbase.png`: the original statics from +Z/+X/−Z/−X. Megami and Menajerii stand upright; Chatur
  and Pond (and Ryusan, Tobi) are Z-up exports lying on their backs.
- `ingame_crew_rigs_with_minusZ_facing_WRONG.png`: the crew's rigs with `-Z` facing. The game turns them around and
  the +Z camera sees their backs.
- `ingame_crew_rigs_with_plusZ_facing.png`: the same rigs with `+Z`. All six face front. Chatur, Pond and Megami hold
  the T3 stance. Menajerii carries a 4.23 m floor plane (mesh `Plane`) skinned into the model. Ryusan and Tobi tear
  apart in the stance.
- `ingame_menajerii_floor_plane_removed.png`: Menajerii after the `Plane` mesh is removed (gltf-transform: node
  disposed + prune; 52 skin joints kept). Written beside the crew's file as `model-rigged-noplane.glb`
  (sha256 `e06f7a811ce691ea…`).
- `rig_sheet_results.json`: facing +1, max bone-direction error 0.2° for all six.

## Wired

- `chatur` → roster/rahkasa/attires/attire1/model-rigged.glb
- `pond` → roster/tsuyu-asui/attires/attire1/model-rigged.glb
- `megami`, `megami-attire1` → roster/parvati/attires/attire1/model-rigged.glb
- `menajerii`, `menajerii-attire1` → roster/vixen/attires/attire1/model-rigged-noplane.glb
- model-facing.json `models`: those keys `+Z`.

## Not wired yet

- Ryusan and Tobi: the crew rigs shred in the stance. The statics were stood upright with the new
  `tools/auto_rig/reorient_static.py` (−90° about X; `upright_four_views_ryusan_tobi.png` shows both facing +Z) and
  are being re-rigged with `rig_tripo_static.py --facing +Z`. They stay on their statics until the new rigs pass the
  same in-game check.
- No textures on any of the six (the extractor writes positions/UVs/material colours only): they render grey/white.
