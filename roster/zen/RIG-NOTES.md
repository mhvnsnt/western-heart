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

## Future forms (owner will send models — planned, do NOT build yet)

- **(a) Manifestation models**: the spirit's tentacles come OFF the spirit
  and become REAL tentacles (pairs with the spirit body's
  clothing-imagery-becomes-real ability above).
- **(b) FUSION MODE**: Zen's spirit form combines with the spirit body and
  the SPIRIT's HEAD REPLACES the body's head — the spirit body wearing the
  spirit's head on top.
