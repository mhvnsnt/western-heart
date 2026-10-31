# JOB-SEQUENCE — Short Jobs First, Then Long Jobs (2026-10-31)

Owner order 2026-10-31: finish the short jobs first and deploy each one
before starting the long jobs. Every step is a playable thing the player
experiences, in player-progression sequence, shipped to the deployable
build — never a pile of unrelated unwired mechanics.

## The law

- **SHORT job:** a T-pose fighter with a simpler moveset, no canon extra
  moves, and moves taken straight from ONE source character
  (Tekken / DOA / KOF / VF5 / Urban Reign).
- **LONG job:** a fighter with canon extra moves, a size-changing
  transformation, an A-pose, or a mixed / multi-source moveset.
- **Refinement (owner 2026-10-31):** a transformation only makes a
  fighter a LONG job when it changes SIZE. A visual-only transformation
  plus a straightforward single-source moveset is SHORT class.
  Demonio is therefore SHORT class (straightforward Jin moveset;
  his transformations are visual only, no size change) and is
  startable immediately — but he is NOT presentable until his full
  T7 Jin treatment (rig, skin weights, decoded real motions/stance)
  has landed. A hand-posed still is not proof.
- Steps run in player-progression order. How the work is done is
  written into handoff docs as it goes, so any agent can continue
  in the same direction step by step.

## Method

Classification evidence comes ONLY from sources on main, cited
file + section per fighter below:

- `docs/movesets/MOVESET-PROVENANCE-2026-10-30.md`
  ("Per-fighter classification" table; "Owner Decision List")
- `docs/movesets/MOVESET-PROVENANCE-PHASE2-2026-10-30.md`
  ("Phase 1 — COMPLETE"; "Phase 2 — findings")
- `docs/movesets/MOVESET-PROVENANCE-PHASE1-CONTINUATION-2026-10-31.md`
  ("Landed"; "Held — proven, not landed")
- `docs/WH-100-GAP-INVENTORY-2026-10-30.md`
- `docs/RIG-AUDIT-SWEEP-2026-10-30.md`
- `CANON.md` (per-fighter base lines cited in the provenance table)
- `ROSTER.md` (soul / vessel framework)
- `game/js/roster-full.js` (the selectable roster; its `forms` transformation chains and `bodyScale` values are the size evidence for the transformation axis)
- `roster/<fighter>/CANON.md` where the provenance table cites it

Provenance classes map to job-sequence class like this:

- Provenance class 1 (1-C complete, 1-W workable, 1-S
  source-pending) = single-source straight moveset = SHORT class,
  unless a canon-extra layer, a size-changing transformation, or a
  mix is named for that fighter.
- Provenance class 2 (owner-approved mix) and 2-spec = LONG.
- Provenance class D (Owner Decision List), class 3 (placeholder),
  and 1-core + class-3 layer = LONG / GATED — not scheduled until
  the owner decision lands or the foreign layer is replaced.
- Class-3 residue inside an otherwise single-source file (Demonio's
  34 devil_jin-bank rows, Gyou's 47 paul-bank rows) is a Phase-2
  cleanup item on a SHORT-class fighter, not a second base and not
  a mix. It does not by itself move the fighter to LONG.
- Missing evidence = UNVERIFIED with the named gap. Never guessed.

## Pose — read this before starting any fighter

The sources listed above do NOT record T-pose vs A-pose per
fighter, and the rig-audit sweep contains no per-fighter pose
column. Pose is therefore UNVERIFIED for every fighter below
until it is confirmed from that fighter's model at work start.
This is a gate, not a detail: **any fighter that turns out to be
A-pose moves to LONG before work starts, whatever its moveset
class.** Do not assume a fighter is T-pose because its moveset
is single-source.

## SHORT — Wave 1: finish + deploy first (provenance 1-C)

Single-source, no guess-grade anim_t3, no UNMAPPED. Pose gate
above still applies at work start.

| Fighter | Single source | Evidence |
|---|---|---|
| BRUNO | Tekken — Miguel Caballero Rojo | Provenance "Per-fighter classification", `bruno.json` row; `CANON.md` "Miguel base" |
| DIO | Street Fighter — Akuma, as in Tekken 7 | Provenance, `dio.json` row; `CANON.md` "Akuma base" |
| DOROWANI | Tekken 3 — Gon | Provenance, `dorowani.json` row; `roster/dorowani/README.md` "Base: Gon (Tekken 3)" |
| DXMMII | Tekken — Mokujin | Provenance, `dxmmii.json` row; mimicry IS the base, not a mix |
| MICHIKO | Tekken — Katarina Alves | Provenance, `michiko.json` row; `CANON.md` "Katarina Alves base" |
| NEGATIVO | Tekken 7 — Negan | Provenance, `negativo.json` row; `CANON.md` "Negan base". Lane note: Negativo is owned by the Claude Code lane (GameRig re-rig, skins) — do not queue as new work here |
| PURPLE RAIN | Tekken — Lee Chaolan | Provenance, `purplerain.json` row; `CANON.md` "Lee Chaolan base" |
| SLICE | Tekken — Sergei Dragunov | Provenance, `slice.json` row; `CANON.md` (owner words) |
| RYUJI | KOF — Ryuji Yamazaki | Provenance, `ryuji.json` row (1-C — the pure-Yamazaki roster entry, `CANON.md` L1311: it "is untouched and stays in the repo"); distinct from CORNERSTONE (ryuji-rock) in LONG below |
| WATERFALL | Tekken — Josie Rizal | Provenance, `waterfall.json` row; `CANON.md` "Josie Rizal base" |
| YUKIHYŌ | Tekken — Armor King | Provenance, `yukihyo.json` row; `CANON.md` "YUKIHYŌ is the Western Heart version of Armor King" |
| CHATUR | Tekken 3 — True Ogre | Provenance, `chatur.json` row (1-C, straight T3 Ogre-bank port). Gap: no `CANON.md` entry — wiring-doc base only |

## SHORT — Wave 2: single-source, graph corrections in progress (provenance 1-W)

Same SHORT class as Wave 1. The remaining work is correcting
guess-grade anim_t3 from the fighter's own T3 bank graph
(Phase 1 program in the provenance doc), plus the Phase-2
residue items named per fighter.

| Fighter | Single source | Evidence / remaining work |
|---|---|---|
| AWA POP | Tekken — Nina Williams | Provenance, `awapop.json` row (1-W) |
| BUFFALO BILL / ASHES | Tekken 3 — Marshall Law / Forest Law | Provenance, `buffalo-bill.json` row (1-W); T3 provisional, TTT2 primary pending extraction |
| DEMONIO (main, human, Bloodline Ember files) | Tekken — Jin Kazama | Provenance, `demonio.json` (1-W + 3-residue), `demonio-human.json`, `demonio-bloodline-ember.json` rows. Residue: 34 devil_jin-bank rows, Phase-2 cleanup. 80 UNMAPPED await the Jin T7 source. SHORT per the size-transformation refinement above. NOT presentable until the full T7 Jin treatment lands. The winged/Devil form file is GATED separately (see below) |
| DIABLO | Tekken — Heihachi Mishima | Provenance, `diablo.json` row (1-W); 80 UNMAPPED await the Heihachi T7 source |
| GYOU (main file) | Tekken — Hwoarang | Provenance, `gyou.json` row (1-W + 3-residue); 47 paul-bank rows are Phase-2 residue, not a base. The spirit-body form file is GATED separately |
| KING TYRANT / KAI | Tekken — Eddy Gordo | Provenance, `kingtyrant.json` and `kai.json` rows (1-W) |
| NIGHTWOLF | Tekken — Julia Chang | Provenance, `nightwolf.json` row (1-W) |
| PANTERA | Tekken — King | Provenance, `pantera.json` row (1-W); 109 UNMAPPED await the King T7 clip source. King T7 stance already landed; No Mercy grappling library is a shared library, not a second base |
| PHANTOM | Tekken — Yoshimitsu | Provenance, `phantom.json` row (1-W); 127 UNMAPPED await the Yoshimitsu T7 source |
| RIN | Tekken — Jin Kazama | Provenance, `rin.json` row (1-W); `ROSTER.md` protagonist soul |
| SAKU RA | Tekken — Ling Xiaoyu | Provenance, `sakura.json` row (1-W); `CANON.md` "Xiaoyu base" |
| SAM-UR-A1 | Tekken 3 — Gun Jack | Provenance, `samura1.json` row (1-W); canon names Gun Jack |
| SHA (soul) | Tekken — Ling Xiaoyu | Provenance, `sha.json` row (1-W); Saku Ra is its vessel |
| SKULL / RETSU | Tekken — Bryan Fury | Provenance, `skull.json` and `retsu.json` rows (1-W); Skull 114 UNMAPPED await the Bryan T7 source |
| TORCH | Tekken — Anna Williams | Provenance, `torch.json` row (1-W); `CANON.md` "Anna Williams base" |
| TOU | Tekken — Paul Phoenix | Provenance, `tou.json` row (1-W); `CANON.md` "Paul→TOU" |
| TOBI | Tekken 3 — Hwoarang | Provenance, `tobi.json` row (1-W, straight T3 Hwoarang port, wiring-doc base only). Gap: no `CANON.md` entry; slot also claimed by Gyou |
| AOTSUKI / GASHADOKURO | Tekken 3 — Kuma (bear bank, technical only) | Provenance, `aotsuki.json` and `gashadokuro.json` rows (1-W); bear-bank scaffolding, corrections use the Kuma graph |

## SHORT — Wave 3: single-source, base source still pending (provenance 1-S)

SHORT class, but a fighter in this wave cannot be finished until
its base character's own T7 / T8 / TTT2 / DOA / VF extraction
lands (the Steam lane for T7/T8, the DOA/VF conversion lanes).
Do not invent the missing source, and do not start a Wave-3
fighter ahead of a finished Wave-1 or Wave-2 fighter on the
strength of this list alone — waves are readiness order inside
SHORT, not a licence to skip ahead.

| Fighter | Single source | Evidence / blocker |
|---|---|---|
| BAEK / KEVIN | Tekken — Baek Doo San | Provenance, `baek-master-white.json` and `baek.json` rows (1-S); Bryan bank is a declared proxy, 153 no-anim moves await a Baek source |
| CHORDZ | Tekken — Lars Alexandersson | Provenance, `chordz.json` row (1-S, wiring-doc base only, no `CANON.md` entry) |
| CYBORG X (= Cape Jones) | Tekken — Alisa Bosconovitch | Provenance, `cyborgx.json` row (1-S); `CANON.md` "Alisa Bosconovitch base"; T7/T8 Alisa source pending |
| KINPO | Tekken — Asuka Kazama | Provenance, `kinpo.json` row (1-S); 103 UNMAPPED await the Asuka T7 source |
| MARIPOSA | Tekken — Zafina | Provenance, `mariposa.json` and `mariposa-monarch.json` rows (1-S); Zafina T7/T8 source pending |
| MEGAMI | Tekken Tag Tournament 2 — Jun Kazama | Provenance, `megami.json` row (1-S, document-sourced; TTT2 data is the future real source) |
| MENAJERII | Tekken Tag Tournament 2 — Roger Jr. | Provenance, `menajerii.json` row (1-S, document-sourced; TTT2 data is the future real source) |
| POND | Tekken 7 — Raven | Provenance, `pond.json` row (1-S, wiring-doc base only, no `CANON.md` entry); 151 no-anim moves, Raven T7 source pending |
| RYUSAN | Tekken 7 — Lucky Chloe | Provenance, `ryusan.json` row (1-S, wiring-doc base only, no `CANON.md` entry); T7 source pending |
| SCIMITAR | Tekken — Shaheen | Provenance, `scimitar.json` row (1-S); 57 UNMAPPED await the Shaheen T7 source |
| SILVERTONGUE | Tekken 7 — Lili De Rochefort | Provenance, `silvertongue.json` row (1-S); `CANON.md` "Lili's Tekken 7 frame"; T7 Lili source pending |
| THOR | Tekken — Ganryu | Provenance, `thor.json` row (1-S); `CANON.md` (owner words) "Ganryu is Thor"; 78 no-anim moves await a Ganryu source |
| VAIN ABEL ELIAS | DOA — Bass Armstrong | Provenance, `vainabel.json` row (1-S); `roster/vainabel/CANON.md` (owner words, all Bass moves); DOA anim extraction pending |

## LONG — after every SHORT wave (mixes, canon extras, size, gated layers)

| Fighter | Why LONG | Evidence |
|---|---|---|
| KRONOS (+ Attire 2) | Owner-approved mix (Zangief + others) | Provenance class 2, `kronos.json` / `kronos-attire2.json` rows; Appendix A citations. NOT reworked |
| RAVE (= Kiko Tanaka) | Owner-approved mix (Lei + Byou addition) | Provenance class 2, `rave.json` row; "U can add leis and byous moves to rave". NOT reworked |
| ZUI | Owner-approved mix (Steve Fox + Lei drunken fist + WH originals) | Provenance class 2, `zui.json` row; `docs/decisions/2026-10-24-zui-mix-per-canon.md` |
| ZEN | Owner-approved mix (Dural / Eleven-Twelve concept + own canon moves); FIGHTER_BANK null by owner decision | Provenance class 2, `zen.json` row; `docs/decisions/2026-10-24-zen-base-decision.md` + `roster/zen/CANON.md`. NOT reworked |
| CORNERSTONE (ryuji-rock) | Owner-approved mix (Yamazaki + Rock + King + Toguro intent) | Provenance class 2, `ryuji-rock.json` row; `CANON.md` owner words. Its No Mercy-sourced Rock specials are SUSPECT (wrong FileTable window) — flagged, not fixed |
| BURGER | Canon extra moves (owner-recorded) + size-changing transformation chain (the-mouth bodyScale 1.1, demon bodyScale 1.14 — `game/js/roster-full.js` forms) + Bob T7 source pending | Lane brief: Burger canon extras are owned by the Claude Code lane (GameRig re-rig, skins, Bob gap fills, Burger canon extras) — do not queue as new work here. Provenance, `burger.json` row (1-S, 111 UNMAPPED await the Bob T7 source); variant files `burger-demon.json`, `burger-speed-demon.json`, `burger-the-mouth.json` have NO canon statement |
| KORESHI | Vega core + 312-move Yoshimitsu layer that canon records as NOT owner-specified and rejected | Provenance, `koreshi.json` row (1-core + 3-layer); `roster/koreshi/CANON.md`. Phase 2 replaces the Yoshimitsu layer from the Vega source; what Vega lacks stays UNMAPPED by name |
| CAIN ELIAS | Mix spec approved but base never settled (Glen Kluger OR a fitting Tekken character) | Provenance class 2-spec, `cainelias.json` row; `CANON.md` owner spec. Also on the Owner Decision List — gated until the base is settled |
| DOC FRANK (all files) | Size-changing transformation — every attire's TRANSFORM target carries bodyScale 1.18; the moveset itself is single-source | Provenance, `docfrank.json` row (1-C) + `doc-frank-*.json` rows (1-W, self-inheritance donors only); `game/js/roster-full.js` Doc Frank `forms` (bodyScale 1.18) |
| DEATHFANG (human + werewolf forms) | Size-changing transformation — werewolf form bodyScale 1.12 up / 0.89 down; the moveset itself is single-source | Provenance, `deathfang.json` / `deathfang-werewolf.json` rows (1-S); `CANON.md` Iori in both forms; `game/js/roster-full.js` Deathfang `forms` (bodyScale 1.12 / 0.89) |

## GATED — do not schedule (Owner Decision List, provenance doc)

These stay untouched until the owner decides. They are not
SHORT, not LONG — they are gated. The full questions are in
`docs/movesets/MOVESET-PROVENANCE-2026-10-30.md`,
"Owner Decision List" (10 items):

- STAR — Christie slot vs Xiaoyu/Eddy data conflict
- BYOU (soul) — base not recorded anywhere
- JIN (soul file) — Yoshimitsu-style soul JIN vs Mishima-ryu
  Jin Kazama identity conflict
- DEMONIO (winged/Devil form file) — Devil Jin moveset layer
  has no canon approval
- GYOU (spirit-body form file) — Paul data conflicts with
  Gyou's canon Hwoarang base
- CHARGER (+ Attire 2) — no canon base; Blanka data is a
  stand-in
- STREET REIGN (stub) — 5 moves, no base anywhere
- CAIN ELIAS — base unsettled (also listed under LONG above)
- ECHO — no moveset file exists; copy/mimicry in canon belongs
  to The Trader, DXMMII/Mokujin, and Zen's X.COPY super
- KORESHI Yoshimitsu layer — Phase-2 confirmation item (also
  listed under LONG above)

## UNVERIFIED — roster dirs with no provenance fighter row

The following `roster/` dirs have no fighter row in the
2026-10-30 provenance classification and no moveset file cited
there. They are UNVERIFIED with the named gap (no provenance
row / no moveset file) and are NOT scheduled by this doc:
`bonus`, `jin-eastern-mind`, `kuma-replacement`, `mina-ashido`,
`miruko`, `parvati`, `rahkasa`, `theory`, `tsuyu-asui`, `vixen`,
`wizard-gang`, plus model/bank dirs that are not fighters
(`blanka`, `iori`, `kuma`, `panda`, `vega`, `zafina`, `zangief`,
`props`). Data/bank files (`t3-*.json`, `doa-*.json`,
`vf-*.json`, `sf-*.json`, `ur-char*.json`, original-character
files such as `bob.json`, `armor-king.json`, `lili.json`) are
source material, not roster fighters, and are excluded from
the waves above.

## How each fighter job is worked (method)

1. **Pose + rig state.** Read the bind pose off his own default model
   (pose gate above) and record it. Run `tools/auto_rig` `skin_audit.py`
   on his rigged GLBs — EXT_meshopt_compression files go through the
   meshopt decode stage first (`docs/RIG-AUDIT-SWEEP-2026-10-30.md`,
   "Reading the verdicts").
2. **Skin weights.** `weight_cleanup.py` / `rigfix.py` until the audit
   passes — weights domain only. Skeleton-stage defects (dead
   foreign-named joints, singular inverse-bind matrices, proportion
   flags) get their own named stage, reported, never hidden.
3. **Real motions + stance.** His OWN source's decoded real motions and
   stance: T3 bank clips today; T7 format-200 (0xC8) clips where
   decoded; his own T7/T8/TTT2/DOA/VF extraction when it lands for
   Wave-3 fighters. Never another character's motions.
4. **Moveset data.** Finish from his own source only (branch-walk
   proofs A/B/C/S; unproven mappings stay byte-identical and counted —
   `docs/movesets/MOVESET-PROVENANCE-PHASE1-CONTINUATION-2026-10-31.md`).
   The T3 condition-code decode
   (`docs/movesets/T3-CONDITION-CODE-DECODE-2026-10-31.md`) and the
   `common` bank extraction are the shared unblockers for the remaining
   guess-grade mappings.
5. **Hit reactions.** Wire `t3_row` from his own proven-grade `anim_t3`
   (`docs/WH-100-GAP-INVENTORY-2026-10-30.md`, F12 follow-ups).
6. **Play-verify.** A real fight on the built game, video evidence,
   before the fighter is called done — data-corrected is not
   play-verified.
7. **Ship + log.** Republish the deployable build per
   `tools/deploy/REPUBLISH.md` (`tools/deploy/check_module_graph.py`
   must exit 0), verify the live manifest names the new main commit,
   and update this doc + the gap inventory in the same wave.

## In-progress — deconfliction (do NOT queue these as new work)

- **BURGER** — Claude Code lane: GameRig re-rig, skin/weight fix, Bob
  gap fills, canon extra moves (see LONG table).
- **NEGATIVO** — Claude Code lane: re-rig from his T-pose static plus
  Negan's real T7 attacks (0xC8 per-move clips) (see Wave 1 note).
- **DEMONIO** — parent lane, started 2026-10-31: full T7 Jin treatment
  (skin weights, rig, decode via modding-community tools, T7 Jin
  animations / motions / stance / pose). This is NOT Claude's lane.
  Demonio is SHORT class but is not presentable until this lands.
- **T7 stance batch** — Claude Code's plan: real T7 stances (0xC8) for
  Diablo, Skull, Retsu, Burger, Saku Ra, Sha, Phantom, Gyou, Tobi,
  Gashadokuro, Aotsuki, Nightwolf, plus Purple Rain (Lee), Chordz
  (Lars), Negativo (Negan). Pantera's King stance from this family
  already landed. For wave fighters in this batch, the stance piece
  belongs to the batch — a wave lane does the fighter's other work and
  does not redo the stance.

## Order of work

1. SHORT Wave 1, one fighter at a time, each shipped to the
   deployable build as a playable step before the next starts.
2. SHORT Wave 2, same rule.
3. SHORT Wave 3 as each base source lands — a Wave-3 fighter
   whose source has landed outranks a Wave-2 fighter still
   blocked on graph work only if the owner or coordinator
   says so; the default order above stands.
4. LONG, in the table order above, after every SHORT wave.
5. GATED and UNVERIFIED only after their owner decision or
   their missing file exists. Never guess a base, a pose, or
   a size change to move a fighter between lists.
