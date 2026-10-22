# ZEN — Attire Slots

_ZEN is UNVESSELED (owner canon ruling 2026-10-21): he refused the trial, so he
has no vessel. His Tekken fighting base is Julia (animation bank `zen → julia`,
PR #425) and Julia became Nightwolf — the bank stays as his fighting base, but
his MODEL is his own: the spirit body below is his main model, not a vessel
swap. His spirit form (a separate model, below) is Zen himself as a spirit —
the "stand version of himself" from the owner's design._

| Slot | Name | Status | Model |
|---|---|---|---|
| **Attire 1 (default)** | Spirit Body (owner Tripo) | ✅ WIRED 2026-10-21 | `attires/attire1/model.glb` |
| Attire 2 | Legacy Body | ✅ WIRED (pre-existing) | `game/assets/models/zen-body.glb` (key `zen-body`) |
| Spirit form (NOT an attire) | Zen's Spirit | ✅ WIRED 2026-10-21 | `spirit/model.glb` (key `zen-spirit`) |
| Transform stage 1 (NOT an attire) | Tentacle Mode | ✅ WIRED 2026-10-21 | `tentacle/model.glb` (key `zen-tentacle`) |
| Transform stage 2 (NOT an attire) | Oversoul | ✅ WIRED 2026-10-21 | `oversoul/model.glb` (key `zen-oversoul`) |

Transformation modes live INSIDE Attire 1 (owner canon 2026-10-21, see
`CANON.md`): forms chain in roster-full.js — spirit body **up → Tentacle
Mode up → Oversoul**, reciprocal down edges, via the transform system
(touch TRANSFORM + full nine-soul meter). They are never attire-ladder
entries.

## Attire 1 — Spirit Body (owner Tripo, 2026-10-21)

- **Source**: owner's own Tripo —
  https://studio.tripo3d.ai/3d-model/8c46e379-a51c-4741-b4a3-2132ca89078f
  ("fantasy creature 3d model" by tzflo312), pulled 2026-10-21 via
  `tools/tripo-pull/` (public share link, no sign-in). Raw meshopt GLB:
  19,574,656 B, sha256
  `9eee938f05857b63dbefc6fc6d793ad1c1c449865e926dd979f122e0ea537b74`,
  archived immutable in release `zen-tripo-pulls-20261021` as
  `zen_spirit_body_tripo_8c46e379_raw.glb`. Wired copy = the
  meshopt-decompressed GLB at `attires/attire1/model.glb` (57,367,520 B,
  sha256 `176eca4ad57377c7fd6c773c06aae6d0ee7d7da3ab865ef626bf7c681629e8e8`):
  1 mesh, 1 PBR material, 3 textures, 1,029,153 verts, **static — no
  skeleton, no animations** (rigged at the rig stage, like the other Tripo
  mains). MODEL_URLS keys `zen` + `zen-attire1`; roster-full `model:` =
  `zen` (default on both the player and enemy/raw paths).
- **What it replaced**: before this wire, roster-full pointed Zen at
  `steve-fox` — a borrowed placeholder; he had no attire ladder at all. The
  steve-fox model is untouched and remains Steve Fox's. Zen's own legacy
  body (`game/assets/models/zen-body.glb`, 20,880,260 B) was never moved or
  modified — byte-identical — and now ladders back as Attire 2.

### Owner's design description (verbatim, 2026-10-21 — canon)

> "Attach him to a body like this, mixed with this guy and mixed with
> spirit-body Tripo model and stand blending Susanoo, a JoJo stand, and Over
> Soul in T pose and Yellow skin like the original on a white background in T
> pose and a ambiguous face like black panthers but with white comic book
> character eyes surrounded by that spike black circular shape that used to
> make his eyes, and a nose in the middle like he used to have, but no mouth,
> the mouth he used to have will now be on his chest, and he'll have octopus
> tentacles and be yellow with pastel blue, pastel cyan, pastel pink, and
> pastel green, pastel purple octopus underparts and suckers on the tentacles
> but he'll be yellow still on the rest and gave him a image of a tentacle
> octopus super hero I do not know the name of."

(Provenance note: the owner fed the image generator a reference image of a
tentacled octopus superhero whose name he doesn't know. The blend brief was
Susanoo × JoJo Stand × Shaman King Over Soul.)

### Tentacle canon (owner clarification, verbatim core, 2026-10-21)

> "That version has no tentacles coming out" — and his summary of what Zen
> is: "a fucking yellow lemon octopus Spirit demon."

The spirit body's BASE form has **no protruding tentacles**, and that is
canon-correct: the tentacle IMAGES on his clothes can come out of his clothes
and become REAL tentacles. He is a spirit body, so his clothes aren't actual
closed garments — they're part of his body — and the tentacles emerge from
his body/clothes when he uses them. Tentacle manifestation is an ABILITY
(see `RIG-NOTES.md`), player-triggered, not his resting look.

## Spirit form — Zen himself as a spirit (owner Tripo, 2026-10-21)

- **Source**: owner's own Tripo —
  https://studio.tripo3d.ai/3d-model/803f4cf1-35a5-4126-8971-a3a89aee114b
  ("stylized creature 3d model" by dm333n), pulled 2026-10-21 via
  `tools/tripo-pull/`. Raw meshopt GLB: 17,279,708 B, sha256
  `4814781faa239ad604b5c54543209970b9eed143c30f1ff9c46bc2d1c5d55cfe`,
  archived in release `zen-tripo-pulls-20261021` as
  `zen_spirit_form_tripo_803f4cf1_raw.glb`. Wired copy = decompressed GLB at
  `spirit/model.glb` (54,385,012 B, sha256
  `5ceb521d5d3858496ddd87aa5b0a7c59d06b84c86027862909221ce92db21108`):
  1 mesh, 1 material, 3 textures, 987,287 verts, static.
- **Role**: NOT an attire and NOT a second character. This is Zen's spirit
  form — the stand version of himself. In the stand system he floats behind
  the spirit body (full behavior + animation spec in `RIG-NOTES.md`).
  MODEL_URLS key `zen-spirit`, tied to Zen's fighter record; loadable as its
  own model; it does not replace any attire and does not change Zen's
  default body.

## Tentacle Mode — transform stage 1 (owner Tripo, 2026-10-21)

- **Source**: owner's own Tripo 9460095d, pulled via `tools/tripo-pull/`.
  Raw meshopt GLB: 20,483,320 B, sha256
  `e6f4e12df489b810233bf7a9b582be874addb96c1bd90fbb7e31e7f3225e4f03`,
  archived in release `zen-tripo-pulls-20261021` as
  `zen_tentacle_mode_tripo_9460095d_raw.glb`. Wired copy = the
  meshopt-decompressed GLB at `tentacle/model.glb` (58,606,064 B, sha256
  `35a18d51867b598bb8cc58046683a3000921d60d8b88ffb4da2376cba6114051`):
  1 mesh, 1 material, 3 textures, static — no skeleton, no animations
  (rigged at the rig stage). MODEL_URLS key `zen-tentacle`.
- **Canon**: the clothing tentacle designs become REAL tentacles busting
  out of him. NO Oversoul head in this mode. The spirit floats a little
  HIGHER and FURTHER BACK than its base placement (see RIG-NOTES.md).
  The model ships one loose floating tentacle — owner-chosen attachment
  point: TOP OF HIS SPINE, behind his neck. He fights with the tentacles;
  pastel chromatic blast attacks (ink / razor beams / waves) are a
  moveset design requirement in RIG-NOTES.md.

## Oversoul — transform stage 2 (owner Tripo, 2026-10-21)

- **Source**: owner's own Tripo 2bbc8e88, pulled via `tools/tripo-pull/`.
  Raw meshopt GLB: 20,277,088 B, sha256
  `ca8c91c6e1de5a013a72ca09019924c4fd346364ab265386e825ed93485863ad`,
  archived in release `zen-tripo-pulls-20261021` as
  `zen_oversoul_combined_tripo_2bbc8e88_raw.glb`. Wired copy = the
  meshopt-decompressed GLB at `oversoul/model.glb` (57,381,932 B, sha256
  `788f232df63d5c98b47e4a1d01796cfc48a3084f1b6239cee423abbb4b7356d0`):
  1 mesh, 1 material, 3 textures, static — no skeleton, no animations
  (rigged at the rig stage). MODEL_URLS key `zen-oversoul`.
- **Canon**: the combined form. Transformation sequence: the spirit moves
  to the spirit body's head position, TAKES THE HEAD'S PLACE, then the
  Oversoul form manifests — the spirit functions as his head. Body
  tentacles are IMAGERY on the body, NOT protruding (verified on the
  front render 2026-10-21). Head tentacles, independent snail/chameleon
  eyes, articulating mouth, flame/ribbon-flow appendages: animation
  requirements in RIG-NOTES.md.

## Renders

All four models rendered 2026-10-21 with the locked method
(`docs/RENDER-ORIENTATION.md`): Cycles, orthographic, 2048px, white
background, via `docs/tpose-refs/_tools/tpose_render_cycles.py`. These
Tripo models are authored facing +X, so a facePX variant of the approved
script (the faceY variant's post-import rotation set to Rz 180°) was used
to put the front on the -X front camera; the -Y side camera then shows
the left side, per spec. Every front below was checked with the lane's
own eyes against the owner's canon.

- `docs/tpose-refs/zen/a1_front.png` + `a1_side.png` (+ `a1_report.json`)
  — Spirit Body. Own-eyes: yellow skin, white comic eyes in spiky black
  circles, nose, NO mouth on the face — the mouth is on his chest — and
  the pastel tentacle designs are IMAGERY on the body, nothing
  protruding (base-form canon).
- `docs/tpose-refs/zen/spirit_front.png` + `spirit_side.png`
  (+ `spirit_report.json`) — the Spirit. Own-eyes: lemon-shaped yellow
  body, face with spiky-ringed eyes / nose / open red mouth, wavy
  tentacles all around, NO arms, NO legs.
- `docs/tpose-refs/zen/tentacle_front.png` + `tentacle_side.png`
  (+ `tentacle_report.json`) — Tentacle Mode. Own-eyes: REAL tentacles
  busting out around/behind him and wrapping his legs, pastel
  blue/cyan/pink/purple underparts + suckers; his OWN head (no Oversoul
  head attached).
- `docs/tpose-refs/zen/oversoul_front.png` + `oversoul_side.png`
  (+ `oversoul_report.json`) — Oversoul. **Own-eyes check line: the body
  tentacles are IMAGERY on the torso/arms/legs, NOT protruding** — the
  real tentacles cluster at the head, where the spirit's face (spiky
  eyes, nose, red mouth) sits in the head's place.
- Owner copies in `~/workspace/your_files/`: `zen-spirit-body-front-20261021.png`,
  `zen-spirit-entity-front-20261021.png`, `zen-tentacle-mode-front-20261021.png`,
  `zen-oversoul-front-20261021.png`.
