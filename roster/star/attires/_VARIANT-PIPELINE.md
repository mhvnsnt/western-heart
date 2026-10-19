# STAR — VARIANT PIPELINE

Owner 2026-10-18: "we will make more and some rated M versions and models of
her and some variants and color ways." This doc reserves the slots and
records the plan. No invented canon — structure only.

## Shipped (PR: star/attires-1to4-20261018)

| Slot | Name | Kind | Source |
|---|---|---|---|
| 1 | Red Latex (DEFAULT) | Tripo as-pulled | Tripo ea73eeb3 |
| 2 | After Dark | colorway, black latex — NOT rated-M (owner correction 2026-10-19: "Black does not mean rated M at all") | texture build on Tripo base |
| 3 | Capoeira Gold | colorway, Brazil green/yellow | texture build on Tripo base |
| 4 | Classic | in-game model slot-back | `game/assets/models/star.glb` (untextured — texture pass queued, never a gate) |

## Reserved

- **Slots 5–6**: true RATED-M versions/models (mature content — nudity;
  owner correction 2026-10-19: a dark colorway is NOT rated-M). Per the
  owner's RATED-M law (2026-10-18): the game targets RATED M, nothing
  watered down, nothing held back for nudity/partial nudity — models wire
  in as-is and the customization/clothing system dresses them. The actual
  rated-M Star versions are a separate in-flight lane (not After Dark);
  deeper rated-M work (new geometry/models beyond texture-level) is queued
  for the Creation Suite pipeline lanes.
- **Slots 7–8**: further colorways / variants (tournament schemes, alt hair).
- **Jiggle**: Star is FIRST for the jiggle-physics lane (hips/glutes/thighs
  per-area profiles) — builds on this wiring.

## Build notes

- A2/A3 are texture-level builds on the Tripo base (Pantera Crimson Rage
  pattern): single-atlas HSV recolor, skin/hair/boots/tattoos untouched,
  ORM + normal maps carried over unchanged so the latex material response
  is identical. Recompressed with meshopt (same as Tripo's original).
- Renders: `docs/tpose-refs/star/` — locked-standard FRONT, own-eyes verified.
  512px previews shipped under memory pressure; 2048px locked-standard
  re-renders queued when the VM frees up.
