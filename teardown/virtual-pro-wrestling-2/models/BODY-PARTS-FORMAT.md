# VPW2 body-part selection (CRACKED 2026-11-19)

The per-wrestler body-part selection table lives in the ROM main segment,
not in VPWStudio's documented data. This closes the `model_gap` in
`hidden25.json` for the base body (no-attire) and the head.

## Body sets: ROM 0x435AC

Six 72-byte entries (36 u16 each). Each entry is one 19-model body set:
17 consecutive file IDs, two zero u16s, then the two file IDs just below
the run (so the set is 19 consecutive models), then zeros.

```
entry = [F, F+1, ..., F+16, 0, 0, F-1, F-2, 0, 0, ...]
set   = F-2 .. F+16   (19 models)
```

Within a set, the slot layout (from geometry — bounding boxes of the
extracted OBJs):

| Slots | Part |
|---|---|
| 0–4 | torso (5 models, centered on x≈0; sizes palindromic) |
| 5–11 | LEFT limbs (7 models, model-space x ≈ 8–10.5) |
| 12–18 | RIGHT limbs (7 models, model-space x ≈ 4.5–7) |

The 7 per-side slots are the AKI limb joints (thigh, shin, foot, upper
arm, forearm, hand, fingers). Confident identifications: slot 3 of each
side is the HAND (its geometry matches the standalone hand models at
0x19FA+/0x1A06+ in size and center); slot 4 is FINGERS (smallest mesh).
Provisional by size: slot 1 = thigh (biggest, longest), slot 2 = foot
(long in Z = forward), slot 5 = forearm (thin). Slots 0 and 6 are the
upper arm and shin in unknown order. The render agent should confirm by
assembly against the joint pivots.

Left/right: model-space X mirrors around x≈7.5; the LEFT hand model
(0x19FA) sits at x≈9, the RIGHT (0x1A06) at x≈6 — so the first limb
septet (higher X) is LEFT.

## Pointer table: ROM 0x438D0

27 u32 entries, indexed by BodyType (0–8):

- slots 0–8: body-set entries (full 72 B)
- slots 9–17: body-set second halves (+0x24)
- slots 18–26: nine 36-byte attire entries (ROM 0x4375C)

BodyType → body set:

| BodyType | Name | Set (group base) |
|---|---|---|
| 0, 1 | thin-muscular / thin (ヤセ型筋肉質 / ヤセ型) | 0x98B |
| 2, 3 | standard-muscular / standard (標準型筋肉質 / 標準型) | 0x978 |
| 4, 5 | (4 unused in shipped costumes) / stocky (ずんどう型) | 0x965 |
| 6 | huge (巨漢型) | 0x93F |
| 7 | super-heavy (超重量型) | 0x952 |
| 8 | giant (巨人型) | 0x92C |

**Verification (geometric):** torso bulk increases monotonically across
sets 0→4 (thin → standard → stocky → huge → super-heavy), and the giant
set is tall-narrow (tallest Y, narrow X/Z) — exactly matching the body
types. All 2,860 resolved body+head model files for the 130 roster
entries exist in the extracted models.

## Head triple: file 0x15D5 grid

Face/neck/head are a 5×12×2 grid starting at file 0x15D5 (stride 3):

```
k = body_idx*60 + shape_idx*12 + hair_idx
face = 0x15D5 + 3k, neck = face+1, head = face+2
```

- body_idx: 0 if BodyType in {7,8}, else 1.
- shape_idx from head_shape: Tall(4)→0, Round(2)→1, Standard(0)→2,
  Triangular(3)→3, Slender(1)→4.
- hair_idx from hair_type (N = value+1): N=1→1, N=4→2, N∈{5,6,14}→3,
  N=7→4, N=9→5, N=12→6, N=13→10, N=15→11, else 0 ("most").
  Hair classes 7–9 (Ponytail / unknown / Wide Ponytail) are unused by
  shipped costumes.

**Verification:** formula reproduces all 23 Hidden-25 head triples
(0 mismatches).

## What is still open

- **Attire-variant geometry:** 19-groups 6+ (file IDs 0x99E–0xE4F) are
  selected by RingAttire/UpperAttire through tables not yet located.
  The base body above is the default (no-attire) body; ring-attire
  models for the Hidden 25 were already label-matched by the jp-sourcing
  lane. The nine 36-byte attire entries at ROM 0x4375C reference
  texture/small files (0x0E57–0x0E9F, 0x1303, 0x1A32/0x1A34), not
  geometry — they are per-BodyType default attire data, not the
  per-RingAttire selector.
- **The 14 models at 0x91E–0x92B** (before group 0): 7 left/right pairs
  of similar small parts, unassigned.
- **Glove variants:** hand models 0x19FA+ (left) / 0x1A06+ (right) with
  selection tables at ROM 0x4120C / 0x4123C, selected by the Gloves
  costume field — not yet mapped.
- **Mask models:** mask_face/mask_neck/mask_sides (0x192C–0x19A9) are
  extracted and labeled; the Mask/MaskNumber → file selection is not
  yet mapped (4 masked Hidden-25 wrestlers have mask files listed in
  hidden25.json).

## Outputs

- `tools/vpw2_bodyparts.py` — resolver (reads the tables from the ROM
  to verify; `body_models()`, `head_triple()`).
- `tools/decode_all_bodies.py` — regenerates the JSON.
- `roster/decoded_bodies.json` — base body + head triple for all 130
  roster entries (costume slot 0).
