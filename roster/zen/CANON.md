# ZEN — Canon: the combined form and its transformation modes

Owner canon, 2026-10-21. ZEN is UNVESSELED — he refused the trial, so he
has no vessel; the spirit body below is his own body. All of Zen's versions
are **TRANSFORMATION MODES WITHIN THE SAME ATTIRE** (Attire 1), not
separate attires: a forms chain through the existing transform system
(touch TRANSFORM + full nine-soul meter), Burger-style.

Transformation class: **spiritual / celestial** — an Oversoul / Susanoo
manifestation, a JoJo Stand combining with its user.

The owner's summary of what Zen is, verbatim: **"a fucking yellow lemon
octopus Spirit demon."**

## The four models (all owner Tripos, release `zen-tripo-pulls-20261021`)

| Model | Tripo | Role |
|---|---|---|
| Spirit body | 8c46e379 | Attire 1 default — his body |
| The spirit | 803f4cf1 | His spirit — a separate ENTITY, his stand |
| Oversoul | 2bbc8e88 | Final transformation stage (combined form) |
| Tentacle mode | 9460095d | Middle transformation stage |

## Spirit body (base form)

Yellow skin; ambiguous Black-Panther-like face; white comic eyes in the
spiky black circular shape; a nose; **NO mouth on the face — the mouth is
on his chest**. The tentacle IMAGES on his clothes are imagery only at
rest: no protruding tentacles in base form. His clothes are part of his
spirit body, and the tentacle images can become REAL tentacles (that is
Tentacle Mode, below). His Tekken fighting base stays Julia's animation
bank (`zen → julia`).

## The spirit (803f4cf1) — its own entity

A little **lemon-shaped octopus-looking guy**: a FACE and TENTACLES on a
lemon-shaped body, **NO arms, NO legs** — it doesn't fight with limbs. Its
look is a crude ancient-sculpture mask, like the original Eastern Mind
Zen. It is its **OWN SEPARATE ENTITY**, animated as its own entity:
tentacles wiggle individually, mouth moves, eyes look around, hovering
float. (It is never a "sphere.")

**Placement**: floats a foot or two BEHIND the spirit body, over the
RIGHT shoulder; it switches sides sometimes, and it is incorporated into
attacks.

## OVERSOUL MODE (2bbc8e88) — the sequence and the form

Sequence: the spirit moves to where the head is on the spirit body,
**TAKES THE PLACE OF THE HEAD**, then he transforms into Oversoul mode.
The spirit IS the Oversoul of the spirit body, functioning as its head.

Oversoul features:

- **NO body tentacles out** — on the body they are still just the IMAGES;
  tentacle manifestation is the other stage (Tentacle Mode). (Verified
  on the model's front render 2026-10-21: no protruding body tentacles.)
- Head tentacles are present and must MOVE — wiggling / flowing,
  symmetric but slightly asymmetric.
- Eyes are snail-like + chameleon-like, moving INDEPENDENTLY.
- The mouth moves like his spirit form's mouth.
- The wrist/elbow → shoulder-blade appendages flow like flames / ribbons.
- The hip / pelvis pieces flow like flames.

## TENTACLE MODE (9460095d)

Tentacles **BUST OUT** of him / off his clothing — the designs become REAL
tentacles. This is a real stage of the transformation.

- **NO Oversoul head attached** in this mode.
- The spirit still floats behind him, moving like the tentacles, but a
  little **HIGHER and FURTHER BACK** so it clears the tentacles
  (mode-specific placement offset — recorded in RIG-NOTES.md).
- The model ships ONE LOOSE FLOATING TENTACLE. The owner's chosen
  attachment point: **TOP OF HIS SPINE, behind his neck.**
- ALL tentacles need movement + INDIVIDUAL animations. **He FIGHTS with
  them.**
- Attack design: chromatic pastel attacks blasted from the tentacles —
  pastel ink, razor beams, waves — in the tentacles' pastel colors (the
  blue / cyan / pink / green / purple of the underparts / suckers).

## Wiring (2026-10-21)

- MODEL_URLS: `zen` / `zen-attire1` → `attires/attire1/model.glb`;
  `zen-spirit` → `spirit/model.glb`; `zen-tentacle` →
  `tentacle/model.glb`; `zen-oversoul` → `oversoul/model.glb`.
- Forms chain (roster-full.js, keyed on both `zen` and `zen-attire1`):
  base **up → `zen-tentacle`** (TENTACLE MANIFESTATION), tentacle **up →
  `zen-oversoul`** (OVERSOUL), with reciprocal down edges
  (oversoul down → tentacle, tentacle down → base).
- The animation/rig requirements for every state (per-tentacle motion,
  spirit entity animation, flame-flow appendages, the spine attachment)
  are design requirements logged in RIG-NOTES.md — the wired models are
  static Tripo meshes that receive their rigs at the rig stage.

## Rigged transformations (2026-10-22)

Each form now has a built, gate-passed rig on the SAME attire, wired to the
forms chain above:
- `spirit-body-rigged.glb` (49j): `ZEN_IDLE`, `ZEN_MANIFEST`
- `spirit-entity-rigged.glb` (ZenRoot + 20 strands + face): `ZEN_IDLE`, `ZEN_DOCK`
- `tentacle-mode-rigged.glb` (49j + 12 strands): `ZEN_BUST_OUT`, `ZEN_IDLE`
- `oversoul-rigged.glb` (49j + 7 strands + face): `ZEN_OVERSOUL_FORM`, `ZEN_IDLE`

Rig-stage GLBs live on draft release `zen-rig-delivery-20261022`
(byte-exact, own-eyes proof renders in `docs/tpose-refs/zen/`).
Per-form rig maps + template statement in `roster/zen/RIG-NOTES.md`.
Clip trigger wiring (e.g. play `ZEN_BUST_OUT` on up-transform to `zen-tentacle`)
is stand-system work, spec'd in `roster/zen/rigs/RIG-BUILD-REPORT.md`.
