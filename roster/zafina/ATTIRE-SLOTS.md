# MARIPOSA — Attire Slots (owner 2026-10-18)

> **Canonical slot map moved:** Mariposa's slots now live at
> `roster/mariposa/ATTIRE-SLOTS.md` (Zafina → Mariposa rename). This directory
> holds her Tekken in-game attires, which are her LATER slots (6+ as of owner
> 2026-10-19 — was 5+) — they ladder behind all custom attires per owner
> 2026-10-18. NOTE: the Butterfly Default lives in this directory
> (`attires/butterfly-default/`) but is her **Slot 1** default per owner
> 2026-10-19 — it is not a later-slot attire.

## In-game attires (later slots)

| Slot | Display name | Contents |
|------|--------------|----------|
| 6+ | **Mariposa — Golden Pharaoh** | `roster/zafina/attires/golden-pharaoh/zafina-golden-pharaoh.glb` — custom colorway reskin of her Tekken 6 outfit: butterfly top pink → metallic gold on black, teal scarf + lapis-blue roses kept, gold ring belt, yellow tiger "I like" eyes. Texture-only; rig intact. |
| 6+ | *(other Zafina in-game outfits)* | Original T6 outfit and any other in-game attires, as recovered. |

## Slot-ordering law

- Slot 1: Butterfly Default — owner-designated default (2026-10-19; lives in
  this directory at `attires/butterfly-default/`).
- Slot 2: her Tripo 3D model.
- Slot 3: Monarch — owner-locked.
- Slots 4–5: new custom Tripo-based colorways.
- Slot 6+: the Tekken reskins (this directory, minus Butterfly Default).

## Options wired

- Eyes: `customization/parts/zafina-eyes/` (original dark brown saved) +
  universal `customization/eye-library/` (yellow tiger applied).
- Top texture: `customization/decal-library/zafina/` — gold pharaoh (applied)
  and pink original (restore), `replaces_texture: butterfly_d`.

## History

- 2026-10-18: Slot map moved to `roster/mariposa/ATTIRE-SLOTS.md` on the
  Zafina → Mariposa rename; this file now covers the in-game later slots.
- 2026-10-18: Golden Pharaoh reskin built (gold butterfly / black /
  yellow tiger eyes); renders at `docs/tpose-refs/zafina-golden-pharaoh/`
  (faceY variant — model authored facing -Y).
- 2026-10-19: Owner decision — Butterfly Default is her Slot 1 default;
  in-game attires in this directory move from 5+ to 6+ (Butterfly Default
  excepted — it is Slot 1). See `roster/mariposa/ATTIRE-SLOTS.md`.
