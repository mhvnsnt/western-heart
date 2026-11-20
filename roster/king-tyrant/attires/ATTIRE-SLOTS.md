# KING TYRANT — Attire Slots (owner 2026-10-19)

Canonical slot map. Slot ORDER is the law below; everything gets built and wired
at the same time — ordering is about slot positions, not schedule.

## The locked slots

| Slot | Display name | Contents |
|------|--------------|----------|
| 1 | **King Tyrant — White Tyrant (Tripo)** | `attires/attire1/model.glb` — owner's Tripo build (https://studio.tripo3d.ai/3d-model/22d9d916-71b1-4372-bdce-2d27acf0d18e, "wrestling figure 3d model", 19MB compressed GLB, 1 mesh, 3 textures). Muscular Black wrestler, white trunks with red/black TYRANT tribal logo, white/black hand wraps, black knee pads, black boots, long braided/dread hair. Pulled via `tools/tripo-pull/` 2026-10-19. Render at `docs/tpose-refs/king-tyrant/p1_front.png`. STATIC (unrigged) — playable/game-default swap rides with the auto-rig pass. |
| 2 | **King Tyrant — Tyrant King (Tripo)** | `attires/attire2/model.glb` — owner's Tripo build (https://studio.tripo3d.ai/3d-model/85fb8756-33d1-466a-a0ef-2d4c8f1b65ff, "royal wrestler 3d model", 19MB compressed GLB, 1 mesh, 3 textures). Gold crown, ermine-trimmed cape (white fur w/ black spots, dark red interior), black trunks w/ blue TYRANT logo, white/black wraps, black knee pads, black boots. Render at `docs/tpose-refs/king-tyrant/a2_front.png`. ⚠️ **CAPE RIGGING TASK** — the cape needs cloth/rig work (auto-rig wave + cape cloth pipeline). Recorded, not blocking wiring. |
| 3 | **King Tyrant — Black Snow (Tripo)** | `attires/attire3/model.glb` — owner's Tripo build (https://studio.tripo3d.ai/3d-model/fed0d1d3-ba55-40c4-a0b7-fc78cb4560aa, "wrestler figure 3d model", 18.6MB compressed GLB, 1 mesh, 3 textures). Red velvet robe/coat w/ leopard-print collar, red trunks w/ black TYRANT logo, black boots. Name from Booker T's famous "Black Snow" commentary moment — see `../CHARACTER-RESEARCH.md`. Render at `docs/tpose-refs/king-tyrant/a3_front.png`. ⚠️ **JACKET RIGGING TASK** — the robe needs cloth/rig work (auto-rig wave + cape cloth pipeline). Recorded, not blocking wiring. |
| 4 | **King Tyrant — Fight Gear (Tripo)** | `attires/attire4/model.glb` — owner's Tripo build (https://studio.tripo3d.ai/3d-model/3dcb748f-8e96-49dd-a975-3ebf78f414f9, "wrestler action figure 3d model", 19.2MB compressed GLB, 1 mesh, 3 textures). Red trunks w/ black TYRANT logo, SHORT spiky hair (no dreads), white/black wraps, black knee pads, black boots. Clean — no cape, no jacket, no cloth-rig blockers. Render at `docs/tpose-refs/king-tyrant/a4_front.png`. STATIC (unrigged) — playable swap rides with the auto-rig pass. |
| 5+ | **In-game Eddy-based models** | `game/assets/models/king-tyrant.glb`, `game/assets/models/king-tyrant_alt1.glb` (RigModels fan rips) — ladder back behind ALL custom/Tripo attires per the ordering law. |

## Slot-ordering law (owner, standing)

- Tripo 3D models (his proprietary builds) take the DEFAULT / early slots.
- His customs fill the slots after.
- In-game / Tekken-based models ladder BACK (slots 5+).
- Ordering is slot position, not schedule — everything wires at once when ready.

## Notes

- Live-game default (`game/js/assets.js`) NOT swapped yet — all four attires are
  unrigged statics; the playable swap rides with the auto-rig pass (same pattern
  as Kevin/Star/Thor). Recorded, not deferred — the wires are ready when rig lands.
- Cape (A2) and robe (A3) are cloth-rig tasks on top of the body rig — see the
  auto-rig wave (`tools/auto_rig/`, PR #273) and the cape cloth work in cape-jones.
- The 4 uploaded owner renders live in `../attire-targets/` as design targets;
  targets #2/#3 are now REALIZED as Attires 2 and 3 (owner's own Tripo builds).
  Target #1 (red trunks) is realized in spirit by A4 Fight Gear (red trunks,
  black TYRANT logo — with short spiky hair instead of dreads); the render stays
  as the design ref for a future dreads variant.
