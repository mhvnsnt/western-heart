# SILVERTONGUE — Attire Slots (owner 2026-10-18)

Proprietary name: **Silvertongue** (retired: Lili — never use the old name).

Canonical slot map. Ordering follows the Tripo Attachment Registry law
(owner 2026-10-18): Tripo 3D models are the main/default attires when attached;
older in-game attires slot in after. (Pantera is the exception.)

**The live slot map now lives at `roster/silvertongue/ATTIRE-SLOTS.md`.**
This file is kept for the Tekken-based attires that live under `roster/lili/`.

## Slots

| Slot | Display name | Contents |
|------|--------------|----------|
| 1 | **Silvertongue — Spy Debut** | `roster/silvertongue/attires/spy-debut/silvertongue-spy-debut.glb` — REAL default attire (2026-10-18): 007 honeypot spy, drills gone, 007 makeup, MPFB2 body morph. See `roster/silvertongue/ATTIRE-SLOTS.md`. |
| — | *(reserved)* | Future Tripo main attire (registry law). |
| 3 | **Silvertongue — Noir Gala** | `roster/lili/attires/noir-gala/lili-noir-gala.glb` — deep-black formal colorway reskin (2026-10-18, PR #262). NOT moved, NOT deleted. |

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
- Spy Debut originals: `customization/parts/silvertongue-default/` (MANIFEST.json).

## History

- 2026-10-18: Slot 1 built — Noir Gala reskin (black dress / red accents /
  yellow tiger eyes); renders at `docs/tpose-refs/lili-noir-gala/`.
- 2026-10-18: Slot 1 replaced by Spy Debut default attire
  (`roster/silvertongue/`); Noir Gala moved to Slot 3 (not moved on disk).
