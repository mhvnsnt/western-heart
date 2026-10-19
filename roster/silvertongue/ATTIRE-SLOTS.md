# SILVERTONGUE — Attire Slots (owner 2026-10-18)

Proprietary name: **Silvertongue** (retired: Lili — never use the old name).
007-villain old-school female honeypot. Seductive spy, not formal gown.

Canonical slot map. Ordering follows the Tripo Attachment Registry law
(owner 2026-10-18): Tripo 3D models are the main/default attires when attached;
older in-game attires slot in after. (Pantera is the exception.)

## Slots

| Slot | Display name | Contents |
|------|--------------|----------|
| 1 | **Silvertongue — Spy Debut** | `roster/silvertongue/attires/spy-debut/silvertongue-spy-debut.glb` — REAL default attire (~30%+ changed, Pantera-Attire-1 bar): blonde drill rolls REMOVED (new sleek hair silhouette), tiara + corsage + full formal gown (skirt, frills) removed, black leather spy jacket / silk blouse / spy shorts / patent boots / opera gloves / gunmetal hardware (luminance-preserving retextures of the real T7 meshes), 007 makeup on the head diffuse (smoky eye, winged liner, beauty mark), yellow tiger "I like" eyes, MPFB2 spy-athletic body morph (slimmer waist, toned, taller), GNM-semantic face refinement. Built in the Creation Suite pipeline. |
| — | *(reserved)* | Future Tripo main attire (registry law) — takes Slot 1 when attached, Spy Debut shifts to Slot 2. |
| 3 | **Silvertongue — Noir Gala** | `roster/lili/attires/noir-gala/lili-noir-gala.glb` — deep-black formal colorway reskin (2026-10-18, PR #262). NOT moved, NOT deleted. Later slot per the main-attire bar (recolors ladder back). |

## Slot-ordering law

- Early slots: Western Heart / Eastern Mind-based attires and Tripo mains.
- Later slots: Tekken-based attires (ports, recolors, ripped variants).
- Every attire goes through the Tekken character customizer + customization
  suite; the owner does the creative customization himself.

## Options wired

- Eyes: `customization/parts/lili-eyes/` (original blue-gray saved) +
  universal `customization/eye-library/` (yellow tiger applied).
- Hair: `customization/parts/silvertongue-default/` — original drill rolls +
  tiara + corsage saved as restorable mesh GLB.
- Face: `customization/parts/silvertongue-default/` — original face/lip/brow
  textures saved.
- Outfit: `customization/parts/silvertongue-default/` — all original garment
  textures saved (jacket, pants, boots, gloves, lace, blouse, bow tie, metallic).

## History

- 2026-10-18: Slot 1 built — Spy Debut default attire (this PR).
- 2026-10-18: Noir Gala moved to Slot 3 (was Slot 1; PR #262).
