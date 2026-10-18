# ZAFINA — Attire Slots (owner 2026-10-18)

Canonical slot map. Ordering follows the Tripo Attachment Registry law
(owner 2026-10-18): Tripo 3D models are the main/default attires when attached;
older in-game attires slot in after. (Pantera is the exception.)

## Slots

| Slot | Display name | Contents |
|------|--------------|----------|
| 1 | **Zafina — Golden Pharaoh** | `roster/zafina/attires/golden-pharaoh/zafina-golden-pharaoh.glb` — custom colorway reskin of her Tekken 6 outfit: butterfly top pink → metallic gold on black, teal scarf + lapis-blue roses kept, gold ring belt, yellow tiger "I like" eyes. Texture-only; rig intact. **No Tripo model attached for Zafina as of 2026-10-18** — if one is attached later it takes the main slot per registry law and Golden Pharaoh shifts down. |
| — | *(reserved)* | Future Tripo main attire (registry law). |

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

- 2026-10-18: Slot 1 built — Golden Pharaoh reskin (gold butterfly / black /
  yellow tiger eyes); renders at `docs/tpose-refs/zafina-golden-pharaoh/`
  (faceY variant — model authored facing -Y).
