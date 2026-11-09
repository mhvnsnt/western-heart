# MEGAMI — The Shrine Soul

*Owner canon. SmutBase Parvati intake → Western Heart fighter MEGAMI.*

## Identity

MEGAMI — the Shrine Soul. Housed in `roster/parvati/` (intake model: SmutBase
commission "Parvati," Blender 4.02, GZM widget rig, Genesis-family; 90 objects;
clothing as separate modeled geometry — recorded in `roster/parvati/intake/README.md`,
landed 2026-10-22). *Megami* — goddess. The source figure gets no canon here
(owner canon law). Megami is the proprietary character.

## Backstory

Before the Trial ever pulled her, Megami was the guardian of a sealed door at
a shrine that no living record can date. She did not choose the post; the post
chose her the way stone chooses a wall — by being there first. The door has
never opened. That is her entire biography, and she will tell it to you in
those exact words.

She trained Chatur. That is the one crack in the biography. Chatur came to the
shrine as a dancer who refused to die and left as a spirit with four arms and
a direction; Megami taught her the temple forms the way one teaches a knife to
be patient — and then watched her student walk into the Trial's pull without
looking back. Megami stayed at the door. Then the call came for her too, and
for the first time in her existence she was the one who left something behind.

## Personality

Grief in motion. She is not sad — sadness is weather, and she is stone. Her
grief is structural: it holds up everything she does, the way a roof holds up
by being heavy. She speaks little, moves less, and hits like a landslide that
has been considering it for centuries. Underneath is a teacher's fury —
watchful, exacting, unwilling to let a student be wasted. She will correct
your stance mid-fight, and the correction will hurt.

## Fighting philosophy

> "The shrine was here before you. It will be here after."

A door is not a wall. A wall refuses; a door *decides*. Every one of her
strikes is a gate closing.

## Element

Earth — shrine ground, stone thresholds, the weight of a place that does not
move. She fights downhill; the ground is her ally and she never forgets it.

## Body / Mind / Soul

- **Body:** A temple icon made mobile. Regalia, choker, gauntlets, heels —
  every piece of her dress is armor that never stopped being clothing. She
  moves like a procession.
- **Mind:** The guardian's mind: thresholds, rituals, what is permitted. She
  counts your steps. She knows exactly how many you get.
- **Soul:** The Shrine Soul — the part of the Trial that remembers that some
  things are *kept*, not conquered. She is grief as architecture: a loss you
  can stand inside.

## Relationships

- **Chatur:** Her student, and the wound. Megami taught the four-armed dancer
  every form she knows; Chatur took them into the Trial and became a spirit
  Megami can no longer instruct. Their fights are the only time Megami raises
  her voice — to give corrections Chatur no longer needs, from a shrine Chatur
  no longer guards.
- **The Trader:** The guardian of a sealed door and the keeper of the Trial's
  trades understand each other perfectly: both hold something nobody else can
  touch, both set the terms, both wait. They have never raised their voices at
  each other. They never will.

## Why she thinks she's here

Because the door is sealed and she is not needed there for now — or because
the Trial mistook the shrine's patience for a summons. She tells herself the
first. She fears the second. It changes nothing about how she fights.

## Being purified of

Clinging. The guardian's disease: holding the door shut so long you forget
doors are meant to be *opened* — by the right hands, at the right hour. The
Trial keeps putting opponents in front of her who will not be kept. Her
purification is learning that guarding Chatur's memory is not the same as
guarding the door.

## Signature detail

She never looks at the sealed door in her win pose. She looks past it — at
where Chatur would be standing.

## Voice

Sparse. Imagistic. Japanese-influenced. She does not explain; she pronounces.

- *Fight start:* "Koko made." (This far. No further.)
- *Win:* "Tobira wa, shizuka." (The door is quiet.)
- *Taunt:* "Mō ichido." (Once more. — said like a teacher, not a threat.)

## Technical (not canon)

- **Moveset source:** Jun Kazama (Tekken) — the Kazama Style Classic Martial
  Arts kit, rebuilt with Tekken inputs in `game/assets/movesets/megami.json`.
  A guardian's kit for a guardian: parries, reversals, stance transitions
  (Genjitsu, Izumo), the patience of frame-perfect punishment.
- **Model:** `roster/parvati/attires/attire1/model.glb` (meshopt-compressed from
  the intake GLB; original archived on the release). Full mesh inventory in
  `roster/parvati/PARTS.md`.
- Wired in `game/js/assets.js` (MODEL_URLS `megami`, `megami-attire1`),
  `game/js/movesets.js` (MOVESET_IDS), `game/assets/movesets/index.json`.

## Owner orders — 2026-11-08 (Megami ← Angel Fernandez "Pilot 2", look, hair, skin)

Recorded from the owner's orders of 2026-11-08. Full detail lives in the
owner's memory record; this section is the repo-home copy.

### Likeness — Angel Fernandez ("Pilot 2", owner 2026-11-08 ~18:25 CST)

- Megami gets Angel Fernandez's FACE exactly, plus ALL of Angel's tattoos
  exactly how and where Angel has them (11 catalogue-confirmed pieces;
  catalogue: physics-playground-pwa `docs/likeness-pilot2/TATTOO-CATALOGUE-2026-11-08.md`).
- Megami keeps her own skin-colour family (see Body/skin amendment below —
  shifted a little toward Angel's tones). All ink is black/grey monochrome.
  Areas never tattooed on Angel stay bare.
- "Mutumbo" in the owner's usage = Angel Fernandez.
- Angel-inspired elements are mixed into Megami's bio ADAPTED to the WH
  universe and Megami canon — never copied from Angel's real bio.
- Face chain is licence-clean ONLY: MediaPipe Face Landmarker + house shape
  basis + Blender. FLAME / SMPL / BFM / DECA / EMOCA / MICA / SMIRK /
  SPECTRE / Pixel3DMM are BANNED anywhere in the chain.
- CANON-FILL RULE (owner 2026-11-08 ~18:27 CST): "any word that can't be
  read use megami cannon to fill them" — unreadable script-tattoo wording
  is filled from Megami canon in this repo, in fine cursive at catalogue
  sizes. The fills chosen (listed in the Pilot 2 build report for owner
  approval) draw on lines already in this file:
  - T8: "The shrine was here before you. / It will be here after."
    (her Fighting philosophy, above)
  - T11 "koko" + T12 "made" = "Koko made." across the hands
    (her fight-start line, above)
  - T3: "shizuka" (her win line "Tobira wa, shizuka.", above)

### Pilot 2 build state (2026-11-08)

- Built 2026-11-08 as PR #1678 (open, awaiting the owner's pass; draft
  release `megami-pilot2-20261108`): AngelFace shape key on the
  licence-clean MediaPipe chain; all 11 tattoos + T3 placed. Numeric gate
  was NEUTRAL (OFF 9.57% vs ON 9.77% mean error, neither passing ≤3%;
  camera mismatch dominates), so the likeness verdict is the OWNER'S EYES
  on the side-by-sides.
- Bio draft in PR #1678 carries 3 owner flags: added pre-fight line,
  ink-as-ledger framing, "tallest soul" superlative.
- OWNER VERDICT — FACE/EYES v1 REJECTED (2026-11-08 ~20:20 CST):
  "Get eyes and face like Angel Fernandez." v2 lane launched:
  matched-camera gate first, per-region key iteration (eyes / brows /
  lips), Angel dark-brown iris built via the tiger radial-remap method as
  the Angel-look eye part. The tiger eye itself stays as the universal
  option and Megami's pick; eyes are swappable parts.
- OWNER FACE VERDICT 2 (2026-11-08 ~20:22 CST, verbatim): "it looks like
  u didn't change the face" — v2 escalated: no damped deltas, full
  measured values per region; proof must show an obvious at-a-glance
  OFF/ON difference.
- BODY/SKIN AMENDMENT (owner 2026-11-08 ~20:35 CST, supersedes the
  skin-colour rule in part): make Megami TALLER with LONGER LEGS (gain
  mainly from leg length, proper deformation, not Y-scale), shape
  everything else toward Angel's build — EXCEPT her bust and ass, which
  stay Megami's own huge size/volume untouched — and shift her skin tone
  A LITTLE toward Angel's tones (partial; she keeps her own base family;
  tattoos stay black/grey). SKIN-SHIFT CONSTRAINT (owner 2026-11-08
  ~20:36 CST): the shift touches general skin only — the natural tonal
  variation her own model carries in her intimate areas stays exactly as
  her source model has it, never flattened or unified; verified by
  texture sampling in the build report. IMPROVE-DON'T-REWORK (owner
  2026-11-08 ~20:36 CST): her own existing v4 tones/colours are the base
  and win any conflict — the Angel-ward move is a light touch at most;
  the skin job is to IMPROVE what Parvati already has, never to damage
  her natural tones. Body pass sits with the v2 lane; the combined
  hero shot is composed on the reshaped body.
- BOUNDARY (set 2026-11-08 ~20:22 CST): sourcing a real person's nude
  imagery to replicate her intimate anatomy onto her likeness is
  off-limits (matches the study's standing rule: leaked / OnlyFans
  material never used). Megami's anatomy texturing stays as built from
  her own source model. Do not re-offer or delegate this.

### Hair — Angel styles (owner 2026-11-08)

- Build BOTH Angel Fernandez hairstyles for Megami. The straight style is
  fully evidenced (4/4 held videos); the curly afro had NO held-video
  evidence and is built only from a legitimate public reference or the
  owner's photo — never guessed.
- OWNER VERDICT — ANGEL STRAIGHT HAIR v1 REJECTED (2026-11-08 ~20:20
  CST): "the hair there looks terrible and unrealistic." Full
  strand-grade opaque REBUILD assigned to the hair lane (not a
  transparency tweak), same evidenced design: centre part, blonde
  front-left streak, toggleable headband. (v1: cards translucent;
  vertex group `head` vs bone `Head` binding fix + spring-bone physics
  go to the hair lane.)
- AFRO PRIORITY (owner 2026-11-08 ~20:22 CST): "That hair is ok, but the
  afro will look better" — of the two Angel styles the AFRO is his
  preferred one for Megami and takes priority the moment a reference
  lands; the straight style is an acceptable second option (still gets
  its realism rebuild).
- AFRO REFERENCE RECEIVED (owner 2026-11-08 ~20:24 CST): the owner
  supplied 5 screenshots of Angel's PUBLIC posts (Threads / X /
  Facebook) showing the afro. Spec: very large dense black rounded afro,
  ~2× head width, high top volume, full hairline, ears covered. Afro
  build UNBLOCKED and priority in the hair lane (strand-grade, bind +
  physics, registered as an option).
- COMBINED SHOT ORDERED (owner, verbatim): "let me see it with the tats
  and better face and angel Fernandez eyes and face and the afro. Save
  the other hairstyles as options" — hero render = tattoos + v2 Angel
  face + Angel-brown eyes + afro; Flora + straight saved as options
  (Flora still default until the owner rules otherwise).

### Tattoos — re-audit (owner 2026-11-08 ~20:25 CST)

- Evidence note: the owner's photos appear to show a tiny upper-chest
  script (reads "XIX") the video catalogue logged as bare.
- OWNER RULED (verbatim): "Yes any other tattoos ur missing of angel
  Fernandez add them" — the chest script is ADDED, and a full tattoo
  re-audit is ordered (all held evidence + her public posts; every
  confirmed missed tattoo built at real placement/scale; unresolvable
  motifs stay as built, never invented). Work sits with the v2 lane
  (holds the build textures); proofs + per-addition evidence list land
  in PR #1678.

### Look — default attire, hair, eyes, skin (owner 2026-11-08)

- DEFAULT ATTIRE (owner: "save that as megami base default attire"):
  the Roses & Bows set MINUS the bra — pantie + stockings + garter belt —
  plus the Sugar choker, Flora hair, and the black gauntlets, on the fixed
  v4 base/skin. Landed as code/registry in PR #1677 (merged). Shoe slot
  is empty — the owner is still picking.
- HAIR PICK: Flora Hair (long waves + bangs) from her source blend is her
  chosen hair — "that hair is better on her." Flora is her MAIN DEFAULT
  hairstyle (reaffirmed 2026-11-08 ~18:29 CST); the two Angel styles are
  ADDITIONAL options, not replacements. (The white look in the
  2026-11-07 wardrobe shot was missing textures in the static master
  export only — real Flora is dark/textured from the blend.)
- EYES PICK (owner: "Give her the tiger eyes"): Megami gets the yellow
  tiger eye from the universal eye library; the tiger-eye iris was
  rebuilt for her Daz-atlas UVs (radial remap into the sampled window,
  RepeatWrapping required). Close-up v3 render 2026-11-08 — gold reads
  clearly, parent-verified.
- SKIN STANDARD: her skin is the fixed v4 skin (clean continuous tone,
  GP shells skin-textured, no splotches/plate) in every render and in
  game.

### Roster-wide orders recorded with her (owner 2026-11-08)

- ALL HAIR: all hair from ALL held game files usable + swappable in the
  customization suite, organized the source games' way (Tekken pieces /
  styles, WWE styles), wired from the actual game files and their own
  systems — industry standard, no hand-tooling. Hair must be RIGGED AND
  ALIVE in game: physics reacting to gravity, wind, and movement.
- ALL ITEMS: EVERY clothing item, outfit piece, accessory and item from
  ALL held games saved INDIVIDUALLY as customization options
  (Tekken/WWE organization, straight from their files) for ALL models —
  same treatment as hair.

### Face/body creation system — dual home (owner 2026-11-08 ~20:27 CST)

- The top-level industry-standard face/body creation system — able to
  make any woman's face and body as accurate and customizable as
  possible — is BUILT in the physics-playground-pwa repo (Physique Lab)
  FOR Western Heart, and the same mechanic also ships inside
  western-heart's creation/customization suite, shared formats (dual
  home). Its proving case is the Angel→Megami face (same matched-camera
  gate as Pilot 2 v2; the parent ships the winning face). Lane launched
  2026-11-08 ~20:28 CST.
- NAME LAW (owner 2026-11-08 ~20:28 CST): the system's product name
  lives in its Physique Lab home ONLY and never appears in western-heart
  — no strings, files, or docs here; the WH side uses clean in-universe
  naming. (This section records the law without the name, as the law
  requires.)
- Licence honesty stands: FLAME-family etc. stay documented-not-pulled;
  capability is reached via the licence-clean stack (MediaPipe + GNM
  parametric face + MPFB2 body + Blender).
