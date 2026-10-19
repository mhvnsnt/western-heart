# SILVERTONGUE — Attire Slots (owner 2026-10-18)

Canonical slot map. Ordering follows the Tripo Attachment Registry law
(owner 2026-10-18): Tripo 3D models are the main/default attires when attached;
older in-game attires slot in after. (Pantera is the exception.)

## Slots

| Slot | Display name | Contents |
|------|--------------|----------|
| 1 | **Silvertongue — Noir Gala** | `roster/lili/attires/noir-gala/lili-noir-gala.glb` — custom colorway reskin of her Tekken 7 1P formal outfit: white/cream dress → deep black, red bow tie + boot/glove trim kept, silver tiara, purple corsage, yellow tiger "I like" eyes. Texture-only; rig intact. **No Tripo model attached for Silvertongue as of 2026-10-18** — if one is attached later it takes the main slot per registry law and Noir Gala shifts down. |
| — | *(reserved)* | Future Tripo main attire (registry law). |

## Slot-ordering law

- Early slots: Western Heart / Eastern Mind-based attires and Tripo mains.
- Later slots: Tekken-based attires (ports, recolors, ripped variants).
- Every attire goes through the Tekken character customizer + customization
  suite; the owner does the creative customization himself.

## Options wired

- Eyes: `customization/parts/lili-eyes/` (original blue-gray saved) +
  universal `customization/eye-library/` (yellow tiger applied).
- Dress textures: `customization/decal-library/lili/` — full noir set and
  white-original restore set, per-texture `replaces_texture` entries.

## History

- 2026-10-18: Slot 1 built — Noir Gala reskin (black dress / red accents /
  yellow tiger eyes); renders at `docs/tpose-refs/lili-noir-gala/`.
