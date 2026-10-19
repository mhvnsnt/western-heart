# MARIPOSA — Attire Slots (owner 2026-10-18)

Canonical slot map. Ordering follows the Tripo Attachment Registry law
(owner 2026-10-18): Tripo 3D models are the main/default attires when attached;
older in-game attires slot in after. (Pantera is the exception.)

## Slots

| Slot | Display name | Contents |
|------|--------------|----------|
| 1 | **Mariposa — Butterfly Default** | `roster/mariposa/attires/butterfly-default/mariposa-butterfly-default.glb` — real default attire, ~30%+ changed (owner work 2026-10-18): proprietary butterfly persona on the wired T6 base. Canonical slot map: `roster/mariposa/ATTIRE-SLOTS.md`. |
| 2 | *(reserved)* | Future Tripo main attire (registry law). |
| 3 | **Mariposa — Golden Pharaoh** | `roster/zafina/attires/golden-pharaoh/zafina-golden-pharaoh.glb` — custom colorway reskin of her Tekken 6 outfit: butterfly top pink → metallic gold on black, teal scarf + lapis-blue roses kept, gold ring belt, yellow tiger "I like" eyes. Texture-only; rig intact. Shifted to slot 3 per the slot-ordering law (early slots = Western Heart / Eastern Mind-based attires); untouched on disk. |

## Slot-ordering law

- Early slots: Western Heart / Eastern Mind-based attires and Tripo mains.
- Later slots: Tekken-based attires (ports, recolors, ripped variants).
- Every attire goes through the Tekken character customizer + customization
  suite; the owner does the creative customization himself.

## Options wired

- Eyes: `customization/parts/zafina-eyes/` (original dark brown saved) +
  universal `customization/eye-library/` (yellow tiger applied).
- Top texture: `customization/decal-library/zafina/` — gold pharaoh (applied)
  and pink original (restore), `replaces_texture: butterfly_d`.

## History

- 2026-10-19: Slot 1 Butterfly Default built; Golden Pharaoh shifted to slot 3 (untouched).
- 2026-10-18: Slot 1 built — Golden Pharaoh reskin (gold butterfly / black /
  yellow tiger eyes); renders at `docs/tpose-refs/zafina-golden-pharaoh/`
  (faceY variant — model authored facing -Y).
