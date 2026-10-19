# KING TYRANT — Attire Slots (owner 2026-10-19)

Canonical slot map. Slot ORDER is the law below; everything gets built and wired
at the same time — ordering is about slot positions, not schedule.

## The locked slots

| Slot | Display name | Contents |
|------|--------------|----------|
| 1 | **King Tyrant — White Tyrant (Tripo)** | `attires/attire1/model.glb` — the owner's Tripo build (https://studio.tripo3d.ai/3d-model/22d9d916-71b1-4372-bdce-2d27acf0d18e, "wrestling figure 3d model", 19MB compressed GLB, 1 mesh, 3 textures). Muscular Black wrestler, white trunks with red/black TYRANT tribal logo, white/black hand wraps, black knee pads, black boots, long braided/dread hair. Pulled via `tools/tripo-pull/` 2026-10-19. Render at `docs/tpose-refs/king-tyrant/p1_front.png`. STATIC (unrigged) — playable/game-default swap rides with the auto-rig pass. |
| 2 | **King Tyrant — Red Trunks** | RESERVED. Owner attire target #1: red trunks, black TYRANT logo, white/black wraps, black knee pads, black boots. Render ref: `../attire-targets/01-red-trunks-base.jpg`. Model arrives from the owner's Tripo builds. |
| 3 | **King Tyrant — KING (crown + ermine cape)** | RESERVED. Owner attire target #2: gold crown, ermine-trimmed red velvet cape, black trunks with blue TYRANT logo. Render ref: `../attire-targets/02-king-crown-cape.jpg`. Model arrives from the owner's Tripo builds. |
| 4 | **King Tyrant — Red Robe (leopard collar)** | RESERVED. Owner attire targets #3/#4: long red velvet robe with leopard-print collar over white/red TYRANT trunks. Render refs: `../attire-targets/03-red-robe-leopard-collar.jpg`, `../attire-targets/04-red-robe-full.jpg`. Model arrives from the owner's Tripo builds. |
| 5+ | **In-game Eddy-based models** | `game/assets/models/king-tyrant.glb`, `game/assets/models/king-tyrant_alt1.glb` (RigModels fan rips) — ladder back behind ALL custom/Tripo attires per the ordering law. |

## Slot-ordering law (owner, standing)

- Tripo 3D models (his proprietary builds) take the DEFAULT / early slots.
- His customs fill the slots after.
- In-game / Tekken-based models ladder BACK (slots 5+).
- Ordering is slot position, not schedule — everything wires at once when ready.

## Notes

- Live-game default (`game/js/assets.js`) NOT swapped yet — Attire 1 is an
  unrigged static; the playable swap rides with the auto-rig pass (same pattern
  as Kevin/Star/Thor). Recorded, not deferred — the wire is ready when rig lands.
- Reskin work on the Tripo base (owner also ordered "new attire 1 and reskin")
  builds as texture-level colorways on `attire1/model.glb` and takes the next
  open custom slots.
