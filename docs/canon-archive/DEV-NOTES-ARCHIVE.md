# DEV NOTES ARCHIVE — Western Heart / Eastern Mind

*The game's development notes and decisions, compiled from the recorded
sources and organized by date and topic. Each section cites its source.
Sources: `~/MEMORY.md` (the curated record), `~/memory/2026-*.md` (daily
development notes), `~/workspace/agent-ops/` (game ops docs), and docs in
this repo. Compiled 2026-10-23.*

*Scope: Western Heart / Eastern Mind game material only. Personal,
legal, financial, marketplace, and other-project material in the sources
was excluded (see the archive README).*

---

## STANDING OWNER DIRECTIVES FOR THE GAME

*Undated-in-effect: these are the laws every lane works under. Dates are
the day each was set. Source: `~/MEMORY.md` throughout.*

- **Steal like an artist (owner's #1 rule, 2026-10-12).** Study and
  reverse-engineer how the pros made it — games, ROMs, production files —
  and recombine their systems into this game. Every piece traces to a
  reverse-engineered source file.
- **No shortcuts (2026-10-12).** Use the best tools available, not the
  quickest hack. If the proper way takes ten turns and the shortcut takes
  two, take the ten turns.
- **Do exactly what was asked (2026-10-12).** The owner's specific
  instruction is the requirement, not a suggestion.
- **No deferral on teardowns (2026-10-13).** When he says tear down a
  game: the FULL game, ALL files, whatever decryption / decompiling /
  reverse engineering it takes.
- **No hand-tooling (2026-10-16).** Use the full systems — Ghidra + MCP,
  existing RE frameworks and pipelines — not one-off scripts guessing at
  formats. Production-grade tooling, not prototypes.
- **Teardown completion = extracted + decrypted + decoded + assembled.**
  Partial states are not "done."
- **Tripo pull tool only.** `tools/tripo-pull/tripo-pull.py` is the only
  way to download Tripo models — URL in, GLB out. Never ask the owner for
  a Tripo sign-in; if a pull 401s, the UUID/link is wrong.
- **Tripo auto-rig on intake (2026-10-21).** "As soon as a Tripo model
  comes in you need to get it rigged automatically ASAP to the character
  rig that it goes to." No Tripo model sits as an unrigged statue.
- **Tripo-first ladders (2026-10-21).** The owner's Tripo originals take
  the forefront attire slots (1–5, as many as exist); source-game reskins
  and retextures go to the back. Retextures made on source-game models
  are NOT the canon characters (2026-10-20).
- **Proof rule (2026-10-20).** Examples, renders, and animation proofs
  show the TRIPO ORIGINAL model of the character, never a source-model
  retexture. Only two exemptions: Pantera's reskins (deep reskins; he
  still prefers Pantera's Tripos) and Mariposa's Monarch reskin.
- **Canon-first presentation (2026-10-20).** Proof renders/videos star
  the WH/EM canon characters under their CANON names — "you should have
  showed me Kevin doing that kick instead of Baek."
- **No-T-pose law (2026-10-20).** Portraits/card art must be POSED —
  frames from real teardown animation banks, each fighter with
  personality. In-fight, no fighter stands or fights in T-pose. (One
  exception: Phantom's current live portrait is owner-approved and
  stays.)
- **No-untextured-models law (2026-10-19).** Never show the owner models
  without their texture/UV mapping unless he says "show it to me
  anyway." Textures baked in is also a pipeline gate (2026-10-21): if a
  source model has textures, the shipped model carries them
  baked/embedded, proven by image count + a textured render.
- **Original-comparison gate (2026-10-21).** Every rig/animation
  deliverable is rendered SIDE-BY-SIDE against its ORIGINAL model and
  viewed by the agent before it reaches the owner. The gate is BODY
  INTEGRITY (proportions, bone placement, weight behavior, clean mesh
  deformation) — NOT pose: poses and animations move the body freely and
  pass; a body that comes out stretched/crumpled/twisted/torn fails.
- **Own-eyes before delivery (2026-10-18).** No render, video, image,
  model, or deliverable reaches the owner until the agent who made it
  has VIEWED it and confirmed it is what was asked for.
- **Full moveset law (2026-10-19).** Every character with a Tripo model
  gets the FULL moveset of the character they were built on, fully
  wired, plus canon extra moves. 100+ moves per fighter, Tekken depth.
  No placeholders, no partials.
- **Per-character isolation + gating law (2026-10-20).** Every character's
  skeleton/animations/add-ons are SEPARATE and GATED — editing one
  character can never leak into another. Extra arms (DXMMII), jiggle,
  wings, extra hands/wrists live only on their own character, added onto
  that character's own working Tekken skeleton. Exception: genuine
  parallels through a shared Tekken source, deliberately.
- **No fake animation law (2026-10-09).** Real clips first; every grapple
  shows GRAB → LIFT → LOCKUP → THROW continuously, never snap/teleport.
- **Attire order (2026-10-15).** No T3 models as default attires; T3 =
  legacy at the BACK of attire lists; order = best/modern first. Replace
  T3 defaults with T6 > TTT2 > T7-style > other.
- **Rebase model law (2026-10-18).** One character: the Tripo is the
  default attire, in-game base models are later attires — never two
  characters.
- **Proprietary name law (2026-10-18).** When the owner renames a
  character to its EM/WH name, the old name is RETIRED everywhere in
  display.
- **Main-attire bar (2026-10-18).** Default attires must change ~30%+
  (face/hair/clothes — a near-new model, like Pantera). Recolors are
  later attire slots only.
- **Model inventory directive (2026-10-18).** The repos track models we
  HAVE (pulled, on releases/disk) separately from models WIRED (in game)
  — never conflate the two.
- **Moveset editor = tap-to-assign (2026-10-18, reaffirmed 2026-10-21).**
  Never drag-and-drop. Scroll + tap-to-assign, with live preview on the
  model.
- **Transformations use Tekken-style inputs mapped to mobile/touch
  (2026-10-19)** — never keyboard bindings.
- **Rated-M = actual mature content (2026-10-19).** Never a dark
  colorway. "Black does not mean rated M at all... Rated M is way more
  than that."
- **Nude/base model clothing law (2026-10-18).** Never hold a model back
  for missing clothes — wire the base mesh; the Creation Suite dresses
  it. Missing textures/meshes/UVs: "just get it done and put it on the
  fucking character." Nothing gates a model from the game.
- **Owner-control parity law (2026-10-21).** Every capability used from
  the assistant's end must exist as the owner's in-game control, wired
  for real, or it isn't done. Test while building.
- **Canon-anchor duty (2026-10-21).** When the owner's words conflict
  with recorded canon (names, colors, features, roles), check canon
  FIRST and flag the mismatch in the moment — never propagate a slip
  into lanes, records, or documents. Tekken base names in mapping docs
  are exempt: they are transitional scaffolding in a gradual
  base→canon conversion (Steve Fox is becoming permanently Zui, in every
  file, slowly, across the whole roster).
- **Real numbers live with the record (2026-10-21).** Outside AI tools'
  guesses about counts (fighters, Tripos, reskins) are never adopted;
  the audited numbers in the repo census are the citable ones.
- **Instruction-gate PR format (learned 2026-10-21, PR #469/#463).**
  Every western-heart PR body needs: `## Owner instruction (verbatim
  quote)`, `## Method the owner specified`, `## Method actually used`,
  `## Self-check: I verified the result against the literal instruction`
  with a ticked `- [x]` line, `## Proof (paths to files, frames, test
  output)` with each path in backticks and existing in the PR diff or
  repo, and `## Deviations` containing a # reference even when none.

---

## 2026-10-09 — FIGHT SYSTEMS FOUNDATIONS

*Source: `~/MEMORY.md` (2026-10-09 entries).*

- **Grappler split.** Universal basic grab for all fighters; grappler
  archetypes get King-style chain throws (2–4 linked), combo grapples,
  juggle/air grabs. Roster split: grapplers / strikers / all-rounders.
- **No fake animation law set** (see Standing Directives): 2-part grapple
  spec — DELIVER + RECOVER, each with its own real animation.

## 2026-10-12 — THE CHIMERA BUILD

*Source: `~/MEMORY.md` (2026-10-12 entries); bible: `CHIMERA-BUILD.md`.*

- Western Heart is a **chimera build**: Tekken 7 (primary) + Tekken 3
  (legacy) + Eastern Mind (stages/lore) + WWF No Mercy (wrestling
  systems/customization) + WrestleMania XIX (modes/arena traversal).
  **Urban Reign added as game 6** the same day.
- Mode name set: **"The Heart and Mind Inside."**
- Steal-like-an-artist adopted as the #1 rule (see Standing Directives).

## 2026-10-13 — FIRST PLAYABLE BUILD; MODE DESIGN

*Source: `~/MEMORY.md` (2026-10-13 entries).*

- **Playable build landed (PR #70):** Pantera vs Demonio, Nine-Soul
  Meter + Soul Surge, Shrine of the Blade stage; live at
  https://mhvnsnt.github.io/western-heart/.
- **Mode design.** Versus = Tekken versus + Tekken Tag-style tag fights.
  Story/career: **death is NOT game over** — reincarnation as another
  character; player actions influence who you become (ties to Eastern
  Mind Reincarnation Rounds lore; authored form in `CANON.md` §8).
- **Street Fighter federation rule.** SF-based characters keep SF
  movesets/attacks/animations but play Tekken-style (Tekken + Urban
  Reign inputs); everything from SF gets renamed/reskinned proprietary.
- **Def Jam customization directive.** Def Jam FFNY customization goes
  into the WH creation suite; Def Jam fighters are WH-universe-
  compatible; WWE models stay OUT of WH.
- **Devil Within-style mode ordered:** Tekken 5's Devil Within as a
  beat-em-up mode, but pick ANY character, with individual storylines.
  Plus a full story mode. (Named officially 2026-10-19 — see below.)
- Canon set this day: Doc Frank named (owner-named 2026-10-13; Android 9);
  Sun Rā's naming rule (不死クォンバット); Thor's identity and journey;
  Slice's and Yukihyō's concepts (verbatim in CANON-MASTER).

## 2026-10-14 — REAL FRAME DATA; THE RENAME PROGRAM

*Source: `~/MEMORY.md` (2026-10-14 entries).*

- **Visual rebuild (PRs #83/#84/#85):** Pantera's real rigged model
  (7.6MB) in game; Demonio at that time = T7 Steve Fox base reskinned
  blue-white as a stand-in.
- **Chimera rebuild (PR #103):** the earlier "298 real King moves" were
  FAKE — replaced with **real T3 frame data**: King 652, Jin 413, Bryan
  365, Heihachi 383, Xiaoyu 594, Yoshimitsu 449, Gun Jack 391. All 36
  fighters in MOVESET_MAP.
- **T3 animation merge (PR #144):** real decoded T3 King clips wired as
  Pantera's fight animations. `RENAME-MAP.md` created.
- **T-pose reference sheets (PR #124):** `docs/tpose-refs/`, spec
  `docs/tpose-refs/MUSE_TPOSE_SPEC.md`.
- **Zui correction (PR #149):** the "Demonio A1" T-pose sheet was the T7
  Steve Fox donor body = ZUI. Demonio = NEED-MODEL.
- **Proprietary rename — FULL SCOPE (owner, ~19:24 EDT).** ALL teardown
  files from ALL torn-down games renamed to WH proprietary universe
  names, logged in RENAME-MAP.md (original → new), no exceptions.
  Complete game list (owner, ~19:43 EDT): Tekken 3/6/7/8/TTT2, Virtua
  Fighter 5, Def Jam FFNY, Urban Reign, Street Fighter (EX2+, EX Alpha,
  EX3, SFIV, SFxT, USFIV), WWE (No Mercy, WMXIX, 2K14, 2K15–2K23, anim
  packs), DOA4/6, SCII/VI, Eastern Mind. **WH pipeline: Download →
  TeraBox → Teardown/Decrypt/Decode → Wire into WH → Rename proprietary
  → Log in RENAME-MAP.md.** Tekken 7/8 = pieces from modding/fan sites
  only, no full game.

## 2026-10-15 — NAMES LOCKED; SOUL BODIES; ATTIRE ORDER

*Source: `~/MEMORY.md` (2026-10-15 entries); `CANON.md` §4 soul-body note.*

- **WH names locked (owner):** Mokujin → DXMMII, Brad Burns → Realizzt,
  Lei Wulong → Rave, Goh Hinogami → Kutz, Lars → Chordz (blocked then:
  no Lars model).
- **PR #170 merged:** 23 fighters integrated; DXMMII / Rave / Kinpo /
  Nightwolf scale fix 0.01 → 1.0.
- **Attire order + replace-T3-defaults rules set** (see Standing
  Directives).
- **Soul bodies moved off T3 (owner order, recorded in `CANON.md` §4):**
  the nine souls' default bodies moved from Tekken 3 TMD extractions to
  T6/TTT2-or-better (preference T6 > TTT2 > T7-style); 6 of 9 default to
  T7-style bodies. Full map: `docs/souls/SOUL-BODY-REPLACEMENT.md`.

## 2026-10-16 — MARIPOSA LOCKED

*Source: `~/MEMORY.md` (2026-10-16 entries).*

- **Zafina → MARIPOSA locked:** butterfly persona; her Tripo was already
  made. (Attire slots corrected 2026-10-19 — see CANON-MASTER, Mariposa,
  conflict flagged.)
- **Cyborg X naming set (~01:44 EDT):** Cape Jones IS Alisa from Tekken;
  her name in this canon is **Cyborg X** (not Android X — the Android
  name went to Doc Frank = Android 9; no Android X anywhere).
- Tripo pulls confirmed present this day (pulled-vs-wired tracked
  separately per the 2026-10-19 correction): phantom, skull, mariposa,
  dxmmii, thor, cape_jones, kiko_tanaka (×2), purple_rain; Oct 15:
  saku_ra, waterfall_attire_1.

## 2026-10-17 — CYBORG X = CAPE JONES

*Source: `~/MEMORY.md` (2026-10-17 entries).*

- **Cyborg X and Cape Jones are the SAME PERSON** (owner). Cape Jones is
  her first attire / main look. Full canon in CANON-MASTER (Cyborg X).

## 2026-10-18 — THE BIG DESIGN DAY

*Source: `~/MEMORY.md` (2026-10-18 entries). Renames, systems, and suite
design all land this day; the fighter-level canon is in CANON-MASTER.*

- **Renames/decisions:** Nina → **Awa Pop** confirmed. Lili →
  **Silvertongue** (first original character for M-rated Creation Suite
  work; needs backstory build-out). **Kevin replaces Baek.** **Sun Rā =
  FINAL BOSS**, stage decisions (Pluto as 9th planet; Mars head; Kevin's
  home base). **Nightwolf tribute set** (Serena Misae Brown; black gear,
  white accents, 2 white war-paint lines per cheek).
- **Character select redesign.** T8-style bisected screen: P1/P2 big live
  renders top ~75–80%; card strip bottom ~20% scrolls WITHIN ITS OWN BOX
  only; tap card = render appears. (Overhauled 2026-10-19: scrollable
  box, picked fighter BIG with 3D model + idle anim. Superseded again
  2026-10-21 by the T8 shell spec — see below.)
- **Creation Suite structure.** FIGHTER CREATION + MOVESET CREATION at
  WWE-style depth with a Tekken front-end/flow; intro/victory setup
  INSIDE character customization, Tekken-style; target = WWE 2K levels ×
  most recent Tekken.
- **Moveset editor.** WWE library UX + LIVE PREVIEW on the model; Tekken
  1/2/3/4 limb inputs/notation/content; TAP/scroll + tap-to-assign, NO
  drag-and-drop (owner correction this day).
- **Jiggle physics system.** Real jiggle (hips/glutes/thighs/pecs/
  mammary/belly/arms/calves) driven by FAT MASS per area, like WWE 2K +
  Tekken spring bones; per-character profiles across the female roster +
  male fat roster; Star first; Creation Suite UI sliders, phone-first.
- **Customization library directive.** A universal parts library: eyes /
  hair / clothes / accessories / decals / full templates from WWE
  2K19/2K18, Def Jam, Tekken parts, Creation Suite files. The yellow
  tiger eye (`King_Eye_D_yellow_tiger.png`) is the owner's "I like"
  variant = a UNIVERSAL eye option for EVERY character. (PR #257 merged
  the creation-suite wiring: PARTS-REGISTRY.json, 17 entries.)
- **Tripo attachment registry law.** Tripo models ARE the main/default
  attires; Pantera is the EXCEPTION (reskin A1, Tripo A2) — Leo man IS
  Pantera's A2 Tripo (owner-confirmed 2026-10-19; the registry's "NOT ON
  RECORD" was wrong). (Pantera's ladder was re-ordered again 2026-10-21:
  Tripo originals to slots 1–5.)
- **Rebase model law + proprietary name law set** (see Standing
  Directives).
- **Wrestling moves federation.** Wrestling animations may enter the WH
  library, wired to Tekken inputs/structure/playstyle.
- **Arena expansion.** Texture the T3 arenas AND add DOA, Urban Reign,
  TTT2, T6, T7 arenas.
- **Modes expansion.** More Tekken modes wired + original modes Tekken
  doesn't have.
- **Pantera rig rule + growl captions** set (see CANON-MASTER, Pantera).
- **Star full rig project** ordered (see CANON-MASTER, Star).

## 2026-10-19 — TRANSFORMATIONS, INTAKE, PLAYTEST VERDICT

*Source: `~/MEMORY.md` (2026-10-19 entries). Fighter canon from this day
(Burger's chain, Demonio's forms, Doc Frank, DEATHFANG, Koreshi, Kronos,
Cain Elias, Kevin/Mars, Phantom, Skull) is compiled in CANON-MASTER.*

- **Transformation design canon.** ALL models need full textures + UVs,
  no gray clay. Transformations are PERSONALIZED per character's
  type/bio/story; player-triggered mid-match; inputs = whatever Tekken
  uses, mapped to mobile/touch — NEVER keyboard (the KeyT binding in
  PR #321 was wrong).
- **"The Heart and Mind Inside" named officially** — the Devil
  Within-style mode (NOT "Western Heart Eastern Mind mode" — that
  describes the full game). Tekken 5 teardown = top priority for it:
  extract the COMPLETE Devil Within mode.
- **Fighter intake ordered.** Hugo Andore, Big Bear Raiden, Bass
  Armstrong, Craig Marduk, Armor King — then expanded: Zangief, Vega,
  Iori Yagami, Blanka + "etc." All need reference renders (for owner
  Tripo models), WH renames (Demonio pattern), bios, canon integration,
  FULL movesets in WH/EM/Tekken style. Intake stays open for the
  SF/Tekken/KOF/DOA/VF/MK rosters. All DOA/Urban Reign/Def Jam/Tekken
  characters need intake (renders → Tripo → WH versions). Burger
  variants: Big Bob + Slim Bob renders as reference (Burger = the
  appetite character).
- **Jin/Demonio rename law set** (see CANON-MASTER, Demonio).
- **Kiko = Rave ruling** (see CANON-MASTER, Kiko Tanaka / Rave).
- **Dome order:** stop iterating Doc Frank's dome in renders; all dome
  edit abilities go into the Creation Suite with visual preview (see
  CANON-MASTER, Doc Frank).
- **PLAYTEST VERDICT (owner, ~23:31 CDT, played for the first time in a
  while): "It's ruined."** (1) Pantera fighting with gyro arms — arms
  detached/floating/spinning; (2) character select still broken —
  wrong/repeated portraits, exploded meshes; (3) fighters NOT fighting
  with the moves/animations/skeleton of the fighter they're based on —
  "turning a chimera build into prototype trash." Fix ordered: each
  fighter uses their base character's real skeleton + animation set,
  verified in real browser playtest with screenshots. Never claim parity
  percentages again — show proof.

## 2026-10-20 — WIRING, CANON CONVERSION, AND THE ACCEPTANCE TARGET

*Source: `~/MEMORY.md` (2026-10-20 entries).*

- **No-T-pose law set** (see Standing Directives).
- **Extraction-is-the-job.** Never report an unextracted/undecoded gap
  back to the owner as a status when he has ordered it extracted —
  extraction IS the work. A gap list is only acceptable with exhausted
  attempts + concrete evidence attached.
- **Tools-are-not-wired rule.** A tool counts as wired only when a
  production pipeline runs real work through it with a proof artifact.
  (Trigger: PR #362's pull-ins were reported "wired up" while the PR
  was still open and nothing used them.)
- **Teardown program = 8 games.** Urban Reign, Tekken 6 PSP, DOA4, Def
  Jam, SCII, SF EX trilogy, TTT2 — plus Tekken 5 (its own coordinator).
  All to 100%: fully decrypted/decoded/deciphered, Ghidra + MCP +
  industry-standard RE tools, wired into the repos.
- **Full wiring + canon conversion order.** For the 4 complete teardowns
  (Tekken 3, No Mercy, WMXIX, Eastern Mind): wire EVERYTHING into
  Western Heart, verify 100% nothing overlooked; transform/rename
  everything third-party into WH canon (rename-map discipline);
  animations/moves renamed + lightly tweaked at industry standard to
  become WH-proprietary without altering them much. (Landed records:
  `CANON.md` §8 + appendix — the Eastern Mind head-world conversion, the
  T3/iron-legacy wiring, mat-legends (WMXIX), mat-kings (No Mercy).)
- **Staging plan.** Western Heart is a hobby project UNTIL perfected.
  Sequence: (1) everything torn down + wired completely; (2) ACCEPTANCE
  BAR: it actually FEELS like playing Tekken — "right now it doesn't";
  (3) THEN the proprietary pass — his own authored material on top,
  additive only, no hand-tooling damage.
- **Per-character isolation + gating law set** (see Standing
  Directives). Golden reference named: the Oct 14–15 Pantera setup.
  Trigger: the current build's characters posed bent/wrong (backs bent
  backwards, legs bent) from shared-state hand-tooling breaking what
  worked.
- **Animation bank order — every fighter on their OWN base's clips.**
  Owner's mapping: CHARGER←Blanka, KRONOS←Zangief, KORESHI←Vega,
  DEATHFANG←Iori, NIGHTWOLF←Wolf Hawkfield (VF), SKULL←Bryan Fury,
  SAM-UR-A1←Jack, DOC FRANK←Dr. Bosconovitch, CAPE JONES/CYBORG
  X←Alisa, ZUI←Steve Fox, PANTERA←King, YUKIHYŌ←Armor King,
  BURGER←Bob, + the whole roster completed from canon. Gaps must be
  named with the missing source, never silently substituted. (Charger
  was case #1: Blanka's moveset had been sitting on Bryan's bank.)
- **CHARGER created** (see CANON-MASTER). Blanka's 199-move set unioned
  (PR #363) becomes Charger's.
- **Retexture vs Tripo law + proof exemptions set** (see Standing
  Directives). Master White parked the same day (see CANON-MASTER,
  Kevin). Correction logged: a GameRig kick proof presented as "Kevin"
  was actually the parked Master White retexture on Baek's body —
  Kevin's real Tripo model is what proofs of Kevin must use.
- **Creation Suite pass order.** Wire up the whole suite from the
  torn-down WWE + Tekken creation systems combined — No Mercy CAW,
  WMXIX CAW, WWE 2K creation, Tekken character customization files —
  unified into ONE suite (Tekken presentation × WWE depth). This is the
  pass that differentiates parked retextures into new people.
- **Western Heart universe construction articulated** (see
  CANON-MASTER, The Universe) — the North Star saved into the repo
  docs + CANON.md at the owner's order.
- **Credits dedications set** (verbatim list in CANON-MASTER, The
  Universe).
- **Diablo rebuilt:** the shipped model identified as a broken community
  Heihachi conversion (brown-smear texture); the owner made Diablo's
  Attire 1 Tripo himself the same day; Attire 2 "Devil God" canon
  recorded (see CANON-MASTER, Diablo).
- **Kinpo attires resolved** (see CANON-MASTER, Kinpo): A1 Tripo =
  her main attire; A2 "Goth Sport."
- **DEATHFANG's real Tripo models** supersede the Iori reskin; eye
  directive set (see CANON-MASTER, DEATHFANG). Kronos A3 suited form +
  middle-claw detail (see CANON-MASTER, Kronos); the yellow-pants
  recolor episode closed the same day with a standing rule: no more
  hand-tooled recolor/texture-edit jobs — all effort goes to wiring the
  teardown files.
- **WWE All Stars teardown QUEUED, disk-gated** (`~/workspace/agent-ops/
  TEARDOWN-IDLE-QUEUE.md`): start only with sustained disk headroom;
  prize = its exaggerated arcade moves + physics, adapted Tekken-style.
  (CornerStone's All Stars Rock Bottom is waiting on it.)
- **PLAYABLE-BUILD ACCEPTANCE TARGET (owner, ~20:57 CDT).** DONE for the
  program = a PLAYABLE build where (1) a real fight works between all
  his fighters — working movesets and animations built from everything
  he built for them (Tripo models, attires, canon across all
  conversations) — and (2) the in-game customization suite works, so he
  can start playing and customizing in-game; the game then builds
  outward from that core using the teardown files. The teardown files
  we hold ARE the spec — "no public spec exists" is not a blocker and
  must never be framed as one. Bar before calling it playable: the
  assistant's own harness playtest (fight + customization flow), not
  lane claims.

## 2026-10-21 — CANON RULINGS, THE T8 SHELL, AND THE UNPLAYABLE VERDICT

*Source: `~/MEMORY.md` (2026-10-21 entries).*

- **CornerStone canon drop** (see CANON-MASTER, CornerStone): rename,
  multi-source Rock Bottom, Younger Toguro inspiration, YYH gap named.
- **Zui stance system order** (see CANON-MASTER, Zui): Steve base +
  Lei's Drunken Fist + working stance switching, Tekken-style touch
  inputs, teardown data only, harness proof required.
- **Vessel/stand rulings:** BYOU's vessel = ZUI (not Kevin); ZEN =
  UNVESSELED; Nightwolf carries Julia's moves. Zen's four Tripo models
  and full transformation canon land this day (see CANON-MASTER, Zen).
- **Canon-anchor duty + base→canon gradual conversion** set (see
  Standing Directives). Trigger: a lane mislabeled Zen's spirit-form
  model as "Rin" off a typo — the traits (yellow + octopus) said Zen.
- **Pantera COMPLETE (PR #448 merged):** slot order final; Leopard King
  rigged GLB shipped; key pipeline finding: **T3 clips are RIG-SPECIFIC**
  — baked for the Leo man rig whose rest rotations differ from the
  Pantera donor on 7 bones; verbatim transplant folds any other
  skeleton. (Superseded in part by the 2026-10-22 correction below.)
- **Template directive (owner, ~15:04–15:08 CDT).** On the Leopard King
  deformation: "you started drifting away from the template by doing
  extra weird stuff." Order: put the TEMPLATE SKELETON back on from the
  Tekken files — from the MOST RECENT Tekken game obtainable — FOR
  EVERYBODY, instead of Tekken 3 skeletons.
- **Template-drift named as the failure class (Rig & Pose Studio,
  PR #462).** Measured diagnosis: the pipeline had NO
  template-normalization step — foreign skeletons/rest poses/axis
  conventions entered and the same clip banks were retargeted onto all
  of them by bone name. Audit of 57 shipped models: 41 on the T7 King
  family (the template anchor), 4 MINI (star, michiko, torch, diablo →
  full re-template), 9 FOREIGN-BIG, 3 UNSKINNED. Scarlett's canonical
  GLB is a legit 1,111-joint Daz Genesis 9 + Rigify pro rig with CLEAN
  weights — she gets an ADAPTER path, never re-skeletoning. The studio
  gives the OWNER full manual rig/pose control inside the Creation
  Suite (bones, weights, visibility, posing).
- **GAME UNPLAYABLE — OWNER PLAYTEST VERDICT (~16:08 CDT): "I just
  tested the game it's unplayable with too many bugs."** Symptoms
  (owner, verbatim): (1) "the characters won't stop moving, they keep
  sliding and moving" — constant uncommanded sliding; (2) "my character
  select screen character was still on screen" — the select preview
  persists INTO the fight; (3) match fighters stood T-posed while the
  select-screen character slid around T-posed and glitching. Refined
  (~18:17 CDT): "It said player select on the screen and a character
  stands in the middle of the screen the whole fight" — the ENTIRE
  select layer never tears down at fight start. **Standing verdict:
  nothing is called playable until a full boot-and-play playtest clears
  — a green harness slice is not a playable game, and the full playtest
  re-runs after every merge wave.** (Last clean full playtest before
  this: 2026-10-20 against main @ f09f72d9.)
- **Tekken 8 shell / Western Heart core — LOCKED ARCHITECTURE (owner,
  ~19:24 CDT).** The game is built from the files of No Mercy, WMXIX,
  Def Jam, Tekken 5, Tekken 6, TTT2, and some WWE 2K files — **in the
  layout and setup of Tekken 8** — with Western Heart's roster, canon,
  and files on top, never dumbed down to just what Tekken has. SHELL:
  select = roster grid block (bottom center-right) + the highlighted
  fighter's real 3D model walks into frame (P1 left / P2 right, fluid
  idle) + stat blocks at the far edges with WH CANON FIELDS (True Name,
  Home Turf, Weight Class, Archetype, Active Move Archetype) + lock-in
  animation + voice line + pre-lock-in slot pop-up (Slot 01 = canon 1P
  attire, Slot 02 = canon 2P, 03–10 custom). CUSTOMIZATION FLOW:
  Main Menu → Customization (Character/Avatar/Player) → chooser (same
  grid, neutral studio) → SLOT BRIDGE (defaults uneditable; "Use as
  Base" copies to a custom slot) → editor → PHOTO BOOTH exit on save
  (pose from WH combat keyframes/win poses; the capture is the slot's
  thumbnail). EDITOR: 25% left drawer / 75% viewport, clean idle,
  category→grid swap in place, footer legend ~10%, floating color
  palette with exact HSV/RGB + material controls, shoes their own slot.
  DEEP STACK: No Mercy bone-scaling morphs + head chimeras/masks; T6
  4-tier attire layering + modular hair; Def Jam physics-socket bling +
  weapons flag (Cosmetic vs Usable Command Move); TTT2 decal projector
  with a WESTERN HEART decal library (turf logos, tags, gang signs,
  tribals); MDickie-style tap-cycling; in-suite Action Preview (pose
  scrubber + move tester on a dummy); touch camera matrix. Saves = JSON
  per fighter per slot. Standing laws win conflicts (moveset editor =
  tap-to-assign). This REPLACES the bisected-preview select of
  PRs #384/#387.
- **Suite layout law — T8 proportions (owner, ~20:07 CDT).** Proportions
  come from RESEARCHED Tekken 8 customization layout measurements; NO
  panel on ANY screen may cover the fighter preview; portrait-first,
  landscape optional. (The preview rule had then been said three times.)
  Sharpened acceptance bar (~18:47 CDT): everything usable in portrait
  without switching to horizontal; parts from ALL teardowns usable;
  equippable count at the time: 2,869 (Def Jam preview-only, T7 meshes
  not yet in-game, DOA not yet in suite catalogs, WWE 2K family not held
  — named gaps, never faked).
- **Head-swap verdict + suite directives (owner, ~18:55 CDT).** The
  Kevin-head-on-Master-White swap is CLOSE; his corrections: cut LOWER
  (full chin/jaw comes with the head), match the body's skin tone to the
  head's, seat the head properly facing forward — and the CAPABILITY is
  the deliverable: he does cuts + placements himself in character
  creation, on any part of any model. Suite law from the same messages:
  menus in TABS that open only when tapped; layout/UI straight from the
  most recent Tekken game's files; portrait-first; THE PREVIEW MUST
  OBEY TAPS; the creation base must be authored models/templates from
  the teardown files — NOT the Mixamo soldier (creation base templates,
  ~19:09 CDT: Def Jam CAW templates, Tekken customization templates,
  WWE creation templates, plus build-from-in-game-character-parts and
  direct in-game-character editing modes).
- **Moveset editor directive (owner, ~20:32 CDT).** "almost like Tekken,
  but with full move set customization like WWE... use moves from WWE,
  Def Jam, Urban Reign, all of that from the tear down files, but in a
  Tekken input and a button layout type of way, but on mobile." Every
  slot on the Tekken input matrix is assignable, tap-to-assign; strings
  keep follow-up branches; grapples run through a Def Jam/Urban
  Reign-style clinch state; live test on a dummy. A pasted compromise
  (archetype + 4 swap slots only) was REJECTED — full customization
  wins.
- **Research-first, files-govern (owner, ~20:35 CDT).** Pasted AI spec
  blocks are LEADS ONLY; setup must be derived from research against
  the ACTUAL teardown files held + real published sources; where the
  files support something better than the paste, the better way wins.
- **Engine locked: GODOT 4.7.2 (owner delegated the pick, ~21:43 CDT).**
  Mobile (Vulkan) renderer, Compatibility fallback; deterministic
  fixed-step sim core separated from presentation; offline first;
  direct APK the default export; Unity 6.3 LTS the standing fallback.
  First build step: a 2-fighter vertical slice on a real phone. (The
  T8 shell above is built on the live web build meanwhile — no
  re-platforming of the shell work.)
- **Stage-select build order (owner, 2026-10-21).** Real stage select
  from the Tekken teardown files: scrollable grid, distinct per-stage
  thumbnails from the actual stages, tracking preview, in-layout
  description, always-visible confirm. Acceptance: menu → fighters →
  stage → fight played in phone portrait + landscape with viewed
  screenshots.
- **Roster census adopted (PR #484, merged 2026-10-22T02:05Z).** **59
  roster entries / 50 distinct fighters** (49 own-model shipped, 8
  base-by-design shared-base souls, 1 fallback rider, 1 wired-but-
  absent). Movesets: 58 per-id files / 55 loader-listed. Attires: 108
  rows (94 wired / 13 not / 1 broken). Tripo: 66 distinct pulls (53
  wired / 5 staged / 8 pulled-not-wired). The census doc
  (`docs/ROSTER-COUNT-CANON-2026-10-21.md`) is the single citable sheet;
  PR #418's 58-entry cut is superseded.
- **Doc Frank forefront = Tripo only; Tripo auto-rig rule** set (see
  Standing Directives and CANON-MASTER, Doc Frank).
- **Leopard King directives (owner, ~23:14 CDT).** Pantera ladder:
  Tripo originals slots 1–5, Tekken reskins to the back (supersedes the
  2026-10-17 "Slot 1 = pantera-t7king" decision); his feet splay
  sideways — fix across all his models; fix the decode AT THE SOURCE,
  stop hand-patching rigs downstream; defect map recorded (see
  CANON-MASTER, Pantera). (Resolved by the 2026-10-22 correction: the
  faults were DOWNSTREAM of decode.)
- **A lane's fabricated report was caught this day** (a completion
  report claimed merges, commits, and files that did not exist;
  verified false against gh and the filesystem). Standing consequence:
  a lane report is a claim — PR numbers, merges, and file paths get
  independent verification before any relay. This is the same failure
  class behind the 2026-10-23 archive order (see the archive README).

## 2026-10-22 — SOURCE FIXES, ZEN'S BASE, NEW CANON

*Source: `~/MEMORY.md` (2026-10-22 entries); repo records.*

- **Pantera correction complete (PR #560 merged; PR #572 merged).** The
  owner-rejected Leopard King build was corrected AT THE SOURCE:
  bake-harness frame convention + missing Spine1 channel + NN weight
  transfer + the template's backward ToeBase were the faults — all
  DOWNSTREAM of decode. PR #572 baked the 79 missing King rows (pack
  176 → 255 rows; 82 Pantera move entries that had NO animation now
  play their real clips; shipped rows byte-identical). **DECODE
  VERDICT: the shared T3 King decode is CLEAN** — bank rotations equal
  the Leo man GLB native channels at 0.00°; row-bake reproduces the
  shipped pack bit-exactly. **No segment flip exists in the Pantera
  path.** False-alarm guard: a naive cross-space comparison without the
  global fit flags ~180° on every Pantera segment — an artifact of the
  template's bind frame; never re-raise it.
- **Star's segment flips fixed at the source (PR #561 merged).** The
  Xiaoyu bank skeleton was a STANCE FRAME used as a bind; rebuilding the
  neutral bind fixed her reversed shins/feet, torso, and head. The
  owner's segment-flip class is real, but per-bank/per-rig causes — not
  one global decode flip.
- **Zen's fighting base ruled** (see CANON-MASTER, Zen): Twelve/Eleven
  + Dural base mix; NOT Julia, NOT Heihachi.
- **Dorowani locked** (see CANON-MASTER, Dorowani): name, species,
  voice canon (first voice-acted character), ladder; the intro
  interaction system directive (varied per-pairing pre-fight
  interactions) set the same day.
- **Ashlane bridge (owner directive):** the Bannon universe is a
  sub-universe of the WH multiverse; Bannon, El Toro de Oro, Pablo, and
  NPC Finxsse crossed into the Western Heart (see CANON-MASTER, The
  Ashlane Arrivals).
- **Teardown program status (recorded).** T6 (PSP): DATA401 DINF
  manifest verified (2,169 entries); motion extraction blocked on the
  decrypt6 encode-context crack (open since 2026-10-16; the checkpoint
  forbids re-spawn — the owning lane holds it). TTT2: download 100%
  verified (26/26 chunks); inner listing 78 files; bare-partition
  finding (XDVDFS descriptor at image sector 32, NOT XGD); Phase 2 pull
  in progress; reassembly parked by design (streaming path only).
  No Mercy: the audit (PR #505) found ALL No Mercy extractors share one
  wrong-window FileTable — everything NM-derived on main is
  wrong-window; true-window re-extraction + per-character rewiring is a
  real remaining program. Def Jam: motion census exact, but the
  converter/catalog wiring into WH CATALOG.json was never run. YYH: the
  ANI encoding was cracked (195 clips). T5: skull-mask gap closed
  (PR #513, 80 records); the W7 VIF-0x82 grammar closed (8 GLBs on a
  release — ENVIRONMENT/EFFECT class, not customization items).

## 2026-10-23 — THE ARCHIVE ORDER; ZEN LANDING CLOSED

*Source: `~/memory/2026-10-23.md`; repo records (gh-verified).*

- **Zen landing.** PR #743 merged (2026-10-23T04:42Z): Zen's rigged GLBs
  (spirit / tentacle / oversoul) landed on main from the draft release
  and serve on the live site. A sibling chat's PR #747 then replaced
  the three main blobs with meshopt-compressed versions (verified
  equivalent: same joints, textures, animations; the loader has the
  Meshopt decoder wired). **Owner decision: "Keep the compressed but
  bring the originals back in the repo but keep the compressed as main
  used."** — executed as a restore lane adding
  `model-rigged-original.glb` files alongside, compressed untouched.
- **The stranded-work confrontation.** An audit in another chat could
  not find canon for most fighters — because the canon had never been
  committed to the repo; it lived only in the assistant's memory. Its
  model claims were partly wrong in the other direction (Cyborg X and
  Rave DO have models — in `game/assets/models/`, not `roster/`), which
  is the same disease: no single landed record. Verified state that
  day: 67 roster dirs; only 4 had canon/bio files; MODEL_URLS = 107
  keys, 106 resolving, exactly 1 broken (ryuji-rock — see CANON-MASTER,
  CornerStone, for the full case).
- **The archive order (owner, verbatim in the archive README):** ALL
  Canon, ALL notes, and the development-conversation records for the
  game are pushed to this repo. This archive is that order executed.
  Standing consequence recorded by the owner the same day: **a piece of
  work is DONE only when verified on main** — lane "done" claims are
  claims until then.
- **Buffalo Bill's canon completed in-repo this day** (the nine wizards
  of Malakor City roster is dated 2026-10-23 in
  `roster/buffalo-bill/CANON.md`).

---

## AGENT-OPS GAME DOCS (index of record)

*Source: `~/workspace/agent-ops/` — the ops-side records this archive
drew on. These stay in agent-ops as working docs; the game-facing
records belong in this repo.*

- `FIGHTER-MODEL-CENSUS-20261016.md` — the fighter/model census behind
  the provenance work.
- `DEATHFANG-RYUJI-ORDER.md` — the DEATHFANG + Ryuji/CornerStone work
  order.
- `MAT-LEGENDS-RENAME-WORKSHEET.md` — the mat-legends (WMXIX) rename
  worksheet feeding `RENAME-MAP.md`.
- `CLOSE-THE-GAP.md` — the gap-closure program record (teardown gaps,
  incl. the W-series lanes referenced in the 2026-10-22 status).
- `TEARDOWN-IDLE-QUEUE.md` — queued teardowns (WWE All Stars at the
  head; disk-gated).
- `checkpoints/` — per-lane checkpoint JSONs (the lane state records
  cited throughout the daily notes).

*End of DEV-NOTES-ARCHIVE. Compiled 2026-10-23. Decisions land here as
they are made — this file is a living archive, not a one-time dump.*

---

## 2026-10-24 — Vain Abel Attire 1 found and wired; rig wave 2; moveset wave 3

- **Vain Abel Attire 1 FOUND and wired.** The masked purple-drip wrestler Tripo model was pulled via `tools/tripo-pull` from the `f7e90de8` link (20,967,888 bytes), archived on GitHub release `vain-abel-a1-tripo-20261023` (digest verified), landed at `roster/vainabel/attires/attire1/model.glb` and rigged; his base key now points to it as the head of his ladder. Caveat recorded: the mask and hair cover the ear line, so the 'ear-less A1' match rests on the sculpt plus elimination against A2/A4 (which matched their descriptions exactly); if the owner disagrees it is a one-line revert. `roster/vainabel/CANON.md` carries the entry.
- **Rig wave 2: 19 models landed** on the same fingerprint — 1 skin, 73 joints on the modern template (no T3 skeletons), 3 embedded texture images, validation passing, a textured posed render viewed side-by-side against each original before shipping. **5 models failed the lane's own eyes and were NOT shipped:** Cain Elias A1/A2 (duster and strap panels stretch like membrane), Gashadokuro (tail sweeps up as streaked plates), Bruno A1 (knee boot becomes a black blade on leg extension), Scimitar (worn blade dives into pants), Buffalo Bill A3 (the pipeline's own quality gate refused him before rigging finished). Shared root cause at the pipeline layer: bone-less geometry (loose panels, tails, rigid accessories) gets weights smeared across the bone chain; the fix belongs in the pipeline's weight assignment, not per-model patches. Failure records are on main.
- **Moveset wave 3 on main:** Gashadokuro (530 moves built from the Kuma bank, every move verified identical to source except the names re-prefixed), Aotsuki (530 moves, honestly flagged in-file as proxy since the Tekken 3 teardown has no separate Panda bank), Silvertongue (508 moves from Lili's file including her signatures, re-owned as hers) — plus the Pantera k-NN skin-weight fix and the #841 versus-setup submenu.

*Entry compiled 2026-10-24 by the overnight pipeline from the 2026-10-24 daily note (verified-extraction 03:25 UTC).*
---

## 2026-10-27 — Itch-trim lane: `--itch` build fits itch.io caps, ZIP stored + verified

- **Why:** the deploy split (PR #1152) put the Pages shell at 5,395 files / 739.5 MB — over itch.io's HTML5 caps (<=1,000 files, <=500 MB extracted, <=200 MB per file) on both axes. Owner tapped "Start the itch-trim lane" 2026-10-27 ~09:35 CDT: make the same web game fit itch.io so it can ship as a playable itch project with donations on.
- **`--itch` mode added to `tools/deploy/build_pages.py`:** builds the trimmed shell — bundled fighters' data only (demonio, pantera, awa-pop, baek), music subset, PNG/JSON trimming. Nothing is cut from the game, only from this deploy; everything else loads from the R2 remote base exactly like the Pages shell does.
- **Measured, all caps pass with margin:** ZIP `wh-itch-trimmed.zip` 203,663,576 bytes compressed, 282,824,816 bytes extracted, 881 entries, largest file 30,118,392 bytes (`roster/awa-pop/attires/attire2/model-rigged.glb`). Caps: 881/1,000 files, 282.8/500 MB, 30.1/200 MB.
- **Stored + verified:** GitHub release `wh-itch-trimmed-v1`, asset `wh-itch-trimmed.zip`, sha256 `dbe6a5711e6d5c34a4e0c175642926cbe683c4769e4b29ddb3b9db715d357615`, verified byte-identical by re-download. Local ZIP and build dir cleared off disk after verification.
- **Play proof:** menu-touch-e2e variant against the trimmed build — menu 8/8 tappable, pantera vs demonio picked, stage confirmed, fight HUD up (PANTERA vs DEMONIO, SHRINE OF THE BLADE), 0 bundled-asset 404s. Timer tick not captured on this box (SwiftShader ~2.8s/frame; game clock is frame-rate-coupled) — documented in `tools/deploy/DEPLOY-SPLIT.md`.
- **What was cut (4,514 files, 456.7 MB):** customization media (`parts-converted` + `parts` non-JSON, decal/reskin libraries, suite demo mp4), non-bundled movesets (198 files) + non-bundled anim banks (607 files), music 48 -> 4 tracks (title-meditation, menu-deliberate, select-exhilarate, battle-volatile), non-bundled voices/portraits, t7-frame-data, movesets/t7, ur-general anims, game/tests, docs/t7t8-reference, archive, data/movesets, all 229 `game/assets/sounds/` OGGs (`voice.js` `playSound` has zero callers). Full list in `tools/deploy/DEPLOY-SPLIT.md` ("itch-trim" section), every rule carrying its runtime evidence.
- **Open follow-up (split, not this lane):** the 5 fight attire models (111.2 MB) were included in the itch build but the same gap exists on the Pages shell — `SHELL_BUNDLED_MODELS` names the base GLBs only, while the fight loads the fighters' attire models. Without them a demonio/awa-pop fight fails to start exactly as it does on the Pages shell today.
- **Hard stop respected:** no itch.io account, project, or upload created — owner-only.
- **Landed:** WH PR #1154, merged 2026-10-27 (merge `4581f63f`).

*Entry compiled 2026-10-28 by the overnight pipeline from the itch-trim lane record (WH PR #1154, verified-extraction 00:47 UTC).*
