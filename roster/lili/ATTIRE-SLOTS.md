# SILVERTONGUE — Attire Slots (owner 2026-10-18)

Proprietary name: **Silvertongue** (retired: Lili — never use the old name).

Canonical slot map. Ordering follows the Tripo Attachment Registry law
(owner 2026-10-18): Tripo 3D models are the main/default attires when attached;
older in-game attires slot in after. (Pantera is the exception.)

**The live slot map now lives at `roster/silvertongue/ATTIRE-SLOTS.md`.**
This file is kept for the Tekken-based attires that live under `roster/lili/`.

## Slots

**The live slot map is `roster/silvertongue/ATTIRE-SLOTS.md`** (reconciled
2026-10-19 — the table below used to say Slot 1 = Spy Debut with a "reserved"
Tripo row; the Tripo main has since been attached at Slot 1 per the
reserved-row rule, so this file's old table was stale). This file covers the
Tekken-based attires that live under `roster/lili/`.

| Slot | Display name | Contents |
|------|--------------|----------|
| 1 | **Silvertongue — Tripo Main ("Metallic Bodysuit")** | `roster/silvertongue/attires/attire1/model.glb` — attached 2026-10-19 per the reserved-row rule; took Slot 1. See `roster/silvertongue/ATTIRE-SLOTS.md`. |
| 2 | **Silvertongue — Spy Debut** | `roster/silvertongue/attires/spy-debut/silvertongue-spy-debut.glb` — was Slot 1 (2026-10-18); shifted to Slot 2 when the Tripo main attached. 007 honeypot spy, drills gone, 007 makeup, MPFB2 body morph. |
| 4 | **Silvertongue — Noir Gala** | `roster/lili/attires/noir-gala/lili-noir-gala.glb` — deep-black formal colorway reskin (2026-10-18, PR #262). NOT moved, NOT deleted. Was Slot 3; now Slot 4 (Rated-M Nude took Slot 3). |

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
- 2026-10-19: Reconciled against the live map — Tripo Main ("Metallic
  Bodysuit") attached at Slot 1 per the reserved-row rule; Spy Debut → Slot 2,
  Rated-M Nude → Slot 3, Noir Gala → Slot 4. This file's old Slot 1 = Spy Debut
  table (from #276) retired; live map is `roster/silvertongue/ATTIRE-SLOTS.md`.
