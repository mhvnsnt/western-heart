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
Tentacle Mode, below). His fighting base is **no longer Julia** — owner 2026-10-22: "Zen can't use Julia's moves ... night wolf uses
Julia's moves" (see *Fighting base (owner 2026-10-22)* below).

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

## Fighting base (owner 2026-10-22)

- **Base = Twelve** (Street Fighter III: 3rd Strike) — the faceless shapeshifting fighter — and his **3D relative
  Eleven** (Street Fighter V). Owner: "Twelve/eleven stance and moves from the street fighter games", "use his 3d
  relative eleven instead too". Zen's stance and move list come from them.
- **X.COPY** (Twelve's Super Art: he becomes a copy of the opponent for a while) is one of Zen's abilities — owner
  chose it — but Zen is NOT only a copier: "he has to have his own stuff as well that fits his canon". His own kit =
  Twelve/Eleven's moves + his canon spirit-stand attacks + Tentacle Mode + Oversoul (above).
- **Not Julia** (Nightwolf owns Julia's moves) and **not Heihachi** (Heihachi becomes Diablo).
- **Data status (checked 2026-10-22):** no Twelve or Eleven data is in the repo. SF3:3S holds Twelve only as 2D sprites
  (stance/move animation must be lifted to 3D from them); SFV (Eleven, 3D) is in the SFV pull, still blocked on
  downloads (teardown/street-fighter-5/CAST-STATUS.md). Until it lands, `game/js/fighter.js` FIGHTER_BANK still maps
  `zen -> julia` and his 639-move list (game/assets/movesets/zen.json) is built on T3 Heihachi rows — both are
  interim and owned by the moveset/inputs lane (PR #615 crew) to replace with the Twelve/Eleven data.
  RESOLVED 2026-10-24 (owner decision, docs/decisions/2026-10-24-zen-base-decision.md):
  `game/js/fighter.js` FIGHTER_BANK now maps `zen -> UNMAPPED` (null) — NOT Julia,
  NOT Heihachi. The 639-move Heihachi list stays as interim data only, in a separate
  section from the true moveset (`wh_true_moveset` in game/assets/movesets/zen.json);
  the two sources are never mixed. Dural motion extraction + Twelve 2D->3D conversion
  are still the unblock path.

### Base mix: Dural (Virtua Fighter 5) + Twelve/Eleven on top, owner 2026-10-22

Owner: "not a interim base ... a base mix with everything else ... once we get that stuff from 11 and 12s converted
over from 2D to 3D we can just add it on top ... I want him to have some of the similar movements from them like that
weird dancing idol stance"; "the person ... from virtual fighter they might have a cool stance too ... to use for now".
So **Dural's stance is Zen's stance for now**, Dural is a permanent layer of his base mix (with his canon kit and
X.COPY), and Twelve's/Eleven's movement (incl. Twelve's dancing idle stance) is added ON TOP once converted 2D->3D.
**Dural** (VF5): a chrome, faceless humanoid with
inhuman movement, the closest match to Twelve in the teardown files (Muse lane survey: Alpha-152's moves were never
extracted from DOA4, Charade is missing from SC2, the free T3 fighters are too human). Her model is on the VF5
release (`dur.farc`). **Data note:** the VF5 extraction holds models; VF5 motion data has not been converted yet
(see the Nightwolf note in game/js/fighter.js bankIdFor), so Dural's moves need VF5 motion extracted before they can
drive Zen. Owned by the moveset/inputs lane.
