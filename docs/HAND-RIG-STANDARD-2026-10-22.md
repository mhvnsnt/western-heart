# WH Hand / Finger Rig Standard (2026-10-22)

Canonical hand rig standard for Western Heart characters, grounded in
teardown data.

## Teardown evidence

### WWE WrestleMania XIX — 15 finger bones per side
From `teardown/wwe-wrestlemania-xix/docs/wrestler-skeleton-000.json`
(verified 2026-10-12): each hand has 5 three-segment chains, e.g. right:

- `Bip R Finger0 → Finger01 → Finger02` (thumb)
- `Bip R Finger1 → Finger11 → Finger12`
- `Bip R Finger2 → Finger21 → Finger22`
- `Bip R Finger3 → Finger31 → Finger32`
- `Bip R Finger4 → Finger41 → Finger42`

30 finger bones total across both hands, all under the Hand bone.

### WH skeleton template — matches the teardown count
`tools/auto_rig/backends/skeleton_template.json` already ships 15 finger
bones per side with the same 3-segment chain structure:
`{Left,Right}Hand{Thumb,Index,Middle,Ring,Pinky}{1,2,3}`. The WH template
agrees with the WMXIX teardown — no structural change needed.

### DOA / Street Fighter / Tekken — from teardown research
`~/workspace/jiggle-face-hands-teardown.md` (pending) adds each title's
finger bone count/segmentation and hand weight conventions. DOA's glove
hands and Tekken's mitt-style hands vs fully articulated fingers determine
whether WH keeps per-finger chains for ALL characters or uses simplified
hands for mitten/glove designs.

**STATUS: research doc has not landed yet.** `## Teardown deltas` below
holds the slots.

## WH standard (applies to every character rig)

1. **Full articulation by default.** 15 finger bones per side, 3 segments
   per finger, canonical names from `skeleton_template.json`
   (`{L,R}Hand{Thumb,Index,Middle,Ring,Pinky}{1,2,3}`). Every character that
   has visible fingers gets the full set — no half-rigged hands.
2. **Mitt/glove exception.** Characters whose design has mitten or
   paw-style hands (e.g. Dorowani's chompy design, Kuma/Panda paws) use a
   single `Hand` bone plus optional `Paw1/2/3` stub chains — flagged in the
   character's rig spec, not silently dropped.
3. **Segment roles:** segment 1 (knuckle) carries the curl, segment 2 the
   follow-through, segment 3 the fingertip. Weight falloff along the chain:
   heat diffusion + `weight_conventions.py` normalize; finger regions must
   never leak weights into palm/forearm bones (region isolation — the
   recurring failure behind "fingers stretch when the wrist moves").
4. **Thumb orientation:** thumb chain sits forward (-Z) of the palm plane;
   the thumb's curl axis differs from the fingers. Donor k-NN transfers must
   map thumb→thumb explicitly (geometric nearest-neighbor alone swaps
   thumb/index on mirrored hands — verified failure mode).
5. **Weight isolation rules** (enforced in `weight_conventions.py`
   TEARDOWN_RULES once the research lands):
   - finger bone weights may not exceed 0.05 on verts whose dominant bone
     is palm/wrist/forearm, and vice versa;
   - fingertip segments (×3) cap at the fingertip region.
6. **Gameplay:** throws, grapples, and the intro interaction system drive
   finger poses (open/closed/grip). The moveset pipeline's hand poses must
   reference the canonical bone names — no per-character finger aliases.
7. **Validation:** `anim_check.py` gates hand tearing the same as body
   tearing (p99.9 edge stretch); the playable gate rejects rigs with
   unweighted finger verts.

## Verified defect + repair spec (research 2026-10-22)

**[FILE]** The shipped 53-joint rigs are L/R asymmetric: `RightHandThumb3`
exists but `LeftHandThumb3` does not (verified on
`roster/pantera/attires/leopard-king/model-rigged.glb` and
`roster/mariposa/attires/monarch/mariposa-monarch-rigged.glb`). Both pinkies
are 2-segment on both sides (symmetric — fine). Any finger-pose system
(fist, point, spread) behaves differently per hand until fixed.

**Repair spec (model-quality lane):** add `LeftHandThumb3` as a child of
`LeftHandThumb2`, positioned/rotated as the mirror of `RightHandThumb3`
(negate X of the right bone's head/tail in skeleton space), then mirror the
skin weights: for every vertex weighted to the right thumb chain, copy the
weight to the corresponding left thumb bone. Do NOT leave it asymmetric.

**Pipeline guard (this PR):** `tools/auto_rig/validate.py` now gates
`fingers_symmetric` — every finger bone must have its L/R mirror. Rigs
without finger bones (mitt/paw designs) pass trivially. The two verified
shipped rigs FAIL this gate until repaired — that is intentional.

## Teardown deltas (filled from research doc 2026-10-22)
- DOA finger segmentation: unknown (`.g1m` files never extracted) — no
  convention taken.
- SFV: UE4 standard, fingers present — no deviation from the WH/Tekken
  layout.
- Tekken 7: full chains in the base skeleton, 2–3 segments per digit —
  WH keeps this layout verbatim.
- Procedural curl: NONE of the three games do runtime procedural finger
  curl — all use authored animation poses. WH does the same (no procedural
  finger system).

## Pipeline wiring
- `tools/auto_rig/backends/skeleton_template.json`: finger chains already
  canonical (verified vs WMXIX teardown — no change).
- `tools/auto_rig/backends/weight_conventions.py`: `TEARDOWN_RULES` is the
  hook for per-region hand weight caps from the research.
- `tools/auto_rig/backends/knn_transfer.py`: thumb/index mapping must use
  the canonical name map, never pure geometric nearest-neighbor.
