# SILVERTONGUE — Attire Slots (owner 2026-10-18)

Proprietary name: **Silvertongue** (retired: Lili — never use the old name).
007-villain old-school female honeypot. Seductive spy, not formal gown.

Canonical slot map. Ordering follows the Tripo Attachment Registry law
(owner 2026-10-18): Tripo 3D models are the main/default attires when attached;
older in-game attires slot in after. (Pantera is the exception.)

## Slots

| Slot | Display name | Contents |
|------|--------------|----------|
| 2 | **Silvertongue — Spy Debut** | (shifted from Slot 1 per the reserved-row rule) `roster/silvertongue/attires/spy-debut/silvertongue-spy-debut.glb` — REAL default attire (~30%+ changed, Pantera-Attire-1 bar): blonde drill rolls REMOVED (new sleek hair silhouette), tiara + corsage + full formal gown (skirt, frills) removed, black leather spy jacket / silk blouse / spy shorts / patent boots / opera gloves / gunmetal hardware (luminance-preserving retextures of the real T7 meshes), 007 makeup on the head diffuse (smoky eye, winged liner, beauty mark), yellow tiger "I like" eyes, MPFB2 spy-athletic body morph (slimmer waist, toned, taller), GNM-semantic face refinement. Built in the Creation Suite pipeline. |
| 1 | **Silvertongue — Tripo Main ("Metallic Bodysuit")** | `roster/silvertongue/attires/attire1/model.glb` — Tripo "metallic bodysuit 3d model" by eqqq57218 (https://studio.tripo3d.ai/3d-model/2e20f9eb-5591-4f73-8d11-980f993c91d6, pulled 2026-10-18), 23.87MB as-pulled, 1 mesh / 1 primitive / 1 material / 3 textures, static — needs auto-rig. DEFAULT/main attire per the Tripo Attachment Registry law (owner 2026-10-18). 👁️ `docs/tpose-refs/silvertongue/p1_front.png` (T-pose front, own-eyes verified 2026-10-19). |
| 3 | **Silvertongue — Rated-M Nude** | (was Slot 2, 2026-10-19) `roster/silvertongue/attires/attire2/model.glb` — texture-level build: silver bodysuit + clothing replaced with skin, tasteful anatomy. Fully rigged (22-bone) with 7 jiggle bones. Dir name unchanged — no files moved. |
| 4 | **Silvertongue — Noir Gala** | (was Slot 3) `roster/lili/attires/noir-gala/lili-noir-gala.glb` — deep-black formal colorway reskin (2026-10-18, PR #262). NOT moved, NOT deleted. Later slot per the main-attire bar (recolors ladder back). |

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
- 2026-10-19: Slot 2 built — Rated-M Nude variant (owner: "Need a rated M nudity version... same for SilverTongue, fully rigged jiggle parts and all"). Texture-level build: silver bodysuit + clothing replaced with skin, tasteful anatomy. Fully rigged (22-bone) with 7 jiggle bones. `attires/attire2/model.glb`.
- 2026-10-19: Tripo main attire attached ("metallic bodysuit" 2e20f9eb, owner standing rule 2026-10-19: Tripo links from him = pull + wire, no separate 'word' needed) — took Slot 1 per the reserved-row rule; Spy Debut → Slot 2, Rated-M Nude → Slot 3, Noir Gala → Slot 4. No files moved or deleted.
