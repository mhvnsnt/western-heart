# ZEN — Rig Notes (owner specs, recorded 2026-10-21)

Standing rig-stage / stand-system requirements for Zen, in the owner's own
direction. These are implemented at rig/animation time — NOT in the
pull/wire lanes. Riggers and stand-system builders: read this before
touching Zen.

## Spirit body (Attire 1, Tripo 8c46e379)

- The wired model is a static, unrigged Tripo (1 mesh, no skeleton). It gets
  its rig at the rig stage like the other Tripo mains. Fighting base stays
  Julia's bank (`zen → julia`) — the model swap does not change his moveset
  or bank.
- The model's clothes are PART OF HIS BODY (he is a spirit body — the
  garments are not closed clothing). Rig and deform them as body, not as
  cloth shells.

## ABILITY — tentacle manifestation (spirit body)

- The tentacle IMAGES printed/embossed on his clothes can come out of his
  clothes and become REAL tentacles, emerging from his body/clothes when he
  uses them (owner canon, 2026-10-21). At rest (base form) there are NO
  protruding tentacles.
- Per standing law, manifestations/transformations are PLAYER-TRIGGERED,
  PERSONALIZED, and GRADUAL. This is a moveset/ability design requirement
  for the stand/moveset system work — logged here, not modeled or rigged in
  the pull lane.

## Spirit form (`zen-spirit`, Tripo 803f4cf1) — stand-system behavior spec

Zen's spirit form is Zen himself as a spirit — his stand. Owner's spec
(2026-10-21):

- **Position**: he FLOATS a foot or two BEHIND the spirit body, over the
  RIGHT shoulder. He SWITCHES SIDES sometimes (right shoulder ↔ left
  shoulder). Hovering float while behind the body — he does not stand on
  the ground.
- **Attacks**: he is INCORPORATED INTO ATTACKS somehow (owner's phrasing —
  design requirement for the stand system; the exact integration is the
  stand-system design work, informed by the soul-stand recon).
- **Look**: crude ancient-sculpture MASK like the original Zen from the
  Eastern Mind games; octopus tentacles made CRUDÉLY, like a crude ancient
  sculpture. The crudeness is the design, not a defect.
- **ANIMATION REQUIREMENTS** (stand/rig stage, not the pull lane):
  - ALL of his tentacles move
  - the tentacles WIGGLE INDIVIDUALLY (independent per-tentacle motion)
  - his MOUTH MOVES
  - his EYES LOOK AROUND (gaze motion)
  - hovering float while positioned behind the body

## Transformation modes (WIRED 2026-10-21 — models arrived, canon in CANON.md)

The two planned form families below arrived as owner Tripos and are wired
as TRANSFORMATION MODES WITHIN ATTIRE 1 (forms chain in roster-full.js:
base up → `zen-tentacle` up → `zen-oversoul`, reciprocal downs) — NOT
attires, NOT separate characters. Both wired models are static Tripo
meshes (1 mesh, no skeleton) until the rig stage. Every animation item
below is an explicit design requirement for the rig/stand/moveset
systems — logged precisely, never faked in the wire lane.

### TENTACLE MODE (`zen-tentacle`, Tripo 9460095d)

- The clothing tentacle IMAGES become REAL tentacles busting out of
  him / off his clothing. NO Oversoul head attached in this mode.
- **Spirit placement (mode offset)**: the spirit still floats behind him,
  moving like the tentacles, but a little HIGHER and FURTHER BACK than
  its base placement (base: a foot or two behind, over the right
  shoulder) so it clears the manifested tentacles. Stand-system
  parameters relative to the base placement: **+0.35 m up, +0.30 m
  back** (starting values for the stand system to tune; the owner's
  words are the spec: "a little HIGHER and FURTHER BACK").
- **Loose tentacle attachment**: the model ships ONE LOOSE FLOATING
  TENTACLE. Owner-chosen attachment point: **TOP OF HIS SPINE, behind
  his neck.** Rig it as a spine-top tentacle with its own motion chain.
- **Animation requirements**:
  - ALL tentacles move, with INDIVIDUAL per-tentacle animations.
  - He FIGHTS with the tentacles — they are attack limbs, not set
    dressing: strikes, grabs, and guards are tentacle moves.
  - The spirit's own animation (above) continues in this mode, synced
    loosely to the tentacles' motion.
- **Attack design (moveset requirement)**: chromatic pastel attacks
  blasted FROM the tentacles — pastel ink, razor beams, waves — in the
  tentacles' pastel colors (blue / cyan / pink / green / purple of the
  underparts and suckers). These are new Zen tentacle specials to author
  in his moveset at the moveset stage; there is NO existing moveset file
  for them yet — do not point the forms chain at a moveset key that does
  not exist.

### OVERSOUL (`zen-oversoul`, Tripo 2bbc8e88) — the combined form

- **Transformation sequence (cinematic requirement)**: the spirit leaves
  its behind-the-shoulder placement, moves to where the head is on the
  spirit body, and TAKES THE PLACE OF THE HEAD; then the combined
  Oversoul form manifests. The spirit IS the Oversoul of the spirit
  body, functioning as its head.
- **Body tentacles: NONE OUT.** On the Oversoul body the tentacles are
  still just the IMAGES on his body — protruding tentacles belong to
  Tentacle Mode only. (Model check 2026-10-21, front render: imagery,
  not protruding.)
- **Animation requirements**:
  - Head tentacles present and MOVING — wiggling / flowing, symmetric
    but slightly asymmetric.
  - Eyes: snail-like + chameleon-like, moving INDEPENDENTLY of each
    other (independent gaze targets per eye).
  - Mouth articulates like the spirit form's mouth (same mouth-motion
    rig family as `zen-spirit`).
  - The wrist/elbow → shoulder-blade appendages FLOW like flames /
    ribbons (continuous flowing motion, not rigid posing).
  - The hip / pelvis pieces FLOW like flames.

## Future forms (owner will send models — planned, do NOT build yet)

- None currently outstanding: the manifestation model (Tentacle Mode)
  and the fusion model (Oversoul) both arrived 2026-10-21 and are wired
  above.
