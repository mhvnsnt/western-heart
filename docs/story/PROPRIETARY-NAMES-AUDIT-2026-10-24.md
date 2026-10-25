# Proprietary Names Audit (Lane 6, 2026-10-24)

User directive (2026-10-24 19:29 CDT, still open at audit time):
audit CANON.md, SOUL-SYSTEMS.md, `docs/decisions/`,
`docs/research/`, MEMORY.md for proprietary names for the
systems below. Rule for this audit: a name counts as NAMED
only if a source says the owner locked/approved it (or canon
itself names it). A PROPOSAL is not a lock. Where no name
exists, the row says NEEDS NAME and offers OPTIONS — the
owner picks; this audit never decides a canon name itself.
Tekken names stay in technical files only, never in CANON.md
bios or in-universe writing. Game ships with NO famous names.

Audit scope actually searched (2026-10-24): `CANON.md`,
`docs/design/SOUL-SYSTEMS.md`, `docs/owner-directives.md`,
`docs/research/SOUL-URGE-SYSTEM.md`,
`docs/research/SOUL-GAUGE-MAPPING.md`,
`docs/research/FINISHER-DESIGN-2026-10-23.md`,
`docs/research/REALM-TRAVEL-CANON-2026-10-23.md`,
`game/js/rage.js`, `game/js/soulurge.js`,
`game/js/soul-systems.js`, `game/js/finisher.js`,
`game/js/stagebreaks.js`, `game/js/tag-relay.js`,
`game/js/v-system.js`, `game/js/spirit-actions.js`,
`game/js/soul-kindle.js`, `game/js/fighter.js`,
`game/js/movesets.js`, `game/js/game.js`, `game/assets/movesets/pantera.json`
(sample), `~/MEMORY.md`. Line numbers below are from those
files on main at audit time. Full-repo grep (moveset JSONs,
all docs) was NOT completed: the fresh clone was still
fetching at report time — see Gaps. Terms reported as "not
found" are "not found in the searched files", not a
whole-repo proof.

## Summary table

| System (Tekken name) | WH name | Status |
|---|---|---|
| Heat (T8) | SOUL URGE (+ Urge Burst / Smash / Dash / Engager, Urge gauge, Urge pip) | LOCKED 2026-10-22 |
| Finisher system | KESSHOU 結章 "the Closing Chapter" | LOCKED 2026-10-23 |
| Full-meter super | Nine-Soul Release 九魂解放 | LOCKED 2026-10-23 (but see Climax variance below) |
| Spirit Release (foe in RAGE) | Reihou 霊放 | LOCKED 2026-10-23 |
| Round-end verdict seal | Trial's Seal 試練の封 | LOCKED 2026-10-23 |
| Full-meter channel of another soul | Soul Surge | CANON-NAMED (name is canon's own) |
| Context finisher (URGE on + context) | 魂 ACTION | NAMED 2026-10-23 |
| Chess Kombat remake (Go-based) | Go Qombat | NAMED 2026-10-23, implementation not found in `game/js` |
| Fight-lab dummy mode (TTT2 Combot equiv.) | Gungaku 軍楽 | LOCKED 2026-10-22 |
| Immortal Qombat mode (Sun Rā) | 不死クォンバット Immortal Qombat | NAMED (distinct from Go Qombat — do not conflate) |
| Ki Charge (T7) | Soul Kindle — PROPOSAL ONLY | NEEDS OWNER PICK |
| Tag (TTT2) | Soul Relay — PROPOSAL ONLY | NEEDS OWNER PICK |
| Rage (state) | — | NEEDS NAME |
| Rage Art | — | NEEDS NAME |
| Rage Drive | — | NEEDS NAME |
| Power Crush | — | NEEDS NAME (+ implementation question) |
| Screw | — | NEEDS NAME |
| Tornado (T8 rename of Screw) | — | NEEDS NAME (same decision as Screw unless owner splits) |
| Bound | — | NEEDS NAME |
| Wall Break | — | NEEDS NAME |
| Floor Break | — | NEEDS NAME |
| Balcony Break | — | NEEDS NAME |
| Slow-mo finish | — | NEEDS NAME (or owner rules it needs none) |
| V-System (SFV-derived) | — | NEEDS NAME (TBD in code) |
| WWE entrance-tool repurpose | — (working title only) | NEEDS NAME |

## NAMED — with source, line, date

### Heat → SOUL URGE — LOCKED
- `game/js/soulurge.js` L2–3: "USER-LOCKED NAME 2026-10-22:
  'Soul Urge' is the official name — use it everywhere (UI,
  docs, code, comments)." Rename table L9–17: Heat → Soul
  Urge; Heat Bar → Urge gauge; Heat Burst → Urge Burst
  (2+3); Heat Engager → Urge Engager; Heat Smash → Urge
  Smash (2+3 during Urge); Heat Dash → Urge Dash (1+2 during
  Urge); Heat Energy pip → Urge pip.
- `docs/research/SOUL-URGE-SYSTEM.md` L3 (name user-locked
  2026-10-22), L19–24 (rename table).
- `docs/owner-directives.md` L160–161: "Soul Urge — NAME
  LOCKED (2026-10-22)."
- Cleanup note (NOT a naming gap): "HEAT"/"heat" still
  appears in comments — `game/js/fighter.js` L1609,
  `game/js/movesets.js` L635–637, `game/js/game.js` L418,
  `game/js/spirit-actions.js` header, `docs/design/SOUL-SYSTEMS.md`
  Interactions line. The rename is locked; the remnants are
  comments, not user-facing names. A comment-sweep PR may
  clean them; it must not change behaviour.

### KESSHOU 結章 — LOCKED (finisher system)
- `docs/design/SOUL-SYSTEMS.md` L8 (owner decision
  2026-10-23): KESSHOU, meter full + victim < 25% HP, on the
  killing blow, victory outro, per-fighter variants.
- `game/js/finisher.js` header (gates: Nine-Soul Meter full +
  opponent HP < 25%), L31, L70–71 (KESSHOU variants).
- `docs/research/FINISHER-DESIGN-2026-10-23.md` L173+
  (proposal "KESSHOU — the Closing Chapter", recommended;
  adopted per SOUL-SYSTEMS.md).
- `~/MEMORY.md` L102 (user approved name, 2026-10-23).
- Gates restated (do not conflate): full meter + victim
  < 25% HP, Tekken-style complex inputs for the finisher
  path, NO one-hit kill from full health, lethal variants
  RARE under special conditions only.

### Nine-Soul Release 九魂解放 — LOCKED, with a Climax variance to resolve
- `docs/design/SOUL-SYSTEMS.md` L9 (2026-10-23): meter full,
  cost 100, input 1+2+3+4 at full meter, unblockable super,
  30 dmg × variant power, HUD callout "SOUL RELEASE READY".
- `game/js/soul-systems.js` L3, L11 (`LABELS.release =
  'NINE-SOUL RELEASE 九魂解放'`).
- VARIANCE (owner question, not decided here):
  `~/MEMORY.md` L103 (2026-10-23) lists "Nine-Soul
  Climax/Release (九魂極)" as its own system, and
  `docs/research/FINISHER-DESIGN-2026-10-23.md` (2026-10-23)
  proposed "NINE-SOUL CLIMAX (九魂極)" as the meter-state
  name with callout "SOUL CLIMAX READY" — but
  SOUL-SYSTEMS.md and `soul-systems.js` implement
  "SOUL RELEASE READY" and 九魂解放. Question for the
  owner: is Climax the ready-state name and Release the
  fired super, or is Climax superseded by Release? Until
  answered, code and HUD use Release; do not print
  "SOUL CLIMAX READY" anywhere.

### Reihou 霊放 "Spirit Release" — LOCKED
- `docs/design/SOUL-SYSTEMS.md` L10 (2026-10-23): foe is in
  RAGE, cost 50, input 1+4 (LP1+RK4), foe's rage purged for
  the round, 6 dmg.
- `game/js/soul-systems.js` L1 (owner 2026-10-23), L5, L11
  (`LABELS.reihou = 'REIHOU 霊放'`).
- Separate from KESSHOU, from Release, and from Trial's
  Seal — never merged in docs or code.

### Trial's Seal 試練の封 — LOCKED
- `docs/design/SOUL-SYSTEMS.md` L11 (2026-10-23): round ends
  by KO and winner ≥ 50% HP, or KO came from a soul system;
  automatic; decisive verdict seal banner + `matchStats.seals`;
  not a death.
- `game/js/soul-systems.js` L7, L11.
- "Automatic banner" in the brief = this: no input, no
  cost. Separate from KESSHOU.

### Soul Surge — CANON-NAMED
- `CANON.md` L447: "a fighter can invoke a Soul Surge —
  channeling one of the *other* eight souls for ten seconds,
  borrowing its signature techniques. This is not a
  mechanic layered onto the fiction. It *is* the fiction."
  Also L1398 ("The Soul Surge is memory, not magic").
- `game/js/fighter.js` L8–9, L50 (surge move, cost 100);
  `docs/research/SOUL-GAUGE-MAPPING.md` L11, L20.
- Status reasoning: the name comes from canon itself, not
  from a rename decision — it needs no owner rename pick.
  `game/js/heartmind.js` uses Soul Surge as the
  transform-meter analog in adventure mode; that is the
  same name in a second mode, not a second system.

### 魂 ACTION — NAMED
- `game/js/spirit-actions.js` L1 (canon, owner 2026-10-23),
  L4–6 (player-visible label '魂 ACTION', ja '魂アクション';
  "The source game's term must never appear on screen").
- `docs/design/SOUL-SYSTEMS.md` Interactions: fires from
  2+3 while URGE is on + a context trigger (wall-crush,
  ground-stomp, back-turned, stun-burst, prop-strike).
- Open input question (not a name gap): the brief states
  RP2+LK3 while URGE active; the code gates on URGE on +
  context. Combat lane to confirm the chord mapping;
  this audit reports code as found and does not invent it.

### Go Qombat — NAMED, implementation not found
- `~/MEMORY.md` L96–99 (user 2026-10-23): Chess Kombat
  (MK Deception) pulled as a Just Fun strategy side mode,
  renamed Go Qombat (user's spelling), based on Go (囲碁),
  fight-for-square, health handicaps by piece rank, power
  squares, single-use spells.
- Implementation: no `go-qombat` module in `game/js` (main
  listing, audited 2026-10-24). `game/js/modes.js` L276,
  L326–334 has `qombat` = 不死クォンバット Immortal Qombat
  (WH original, Sun Rā canon) — a DIFFERENT mode. Do not
  conflate the two. Go Qombat wiring is a modes-lane
  follow-up.

### Gungaku 軍楽 — LOCKED (found in audit, not in brief list)
- `docs/owner-directives.md` L162–163 (2026-10-22): fight
  lab / programmable training dummy mode (TTT2 Combot
  equivalent), name locked.

## PROPOSED ONLY — owner pick still needed

### Soul Kindle (T7 Ki Charge) — PROPOSAL
- `game/js/soul-kindle.js` L2, L12–13: "WH canon mapping
  (PROPOSED — needs owner approval): 'SOUL KINDLE'".
  Input 1+2+3+4; next landed hit is a guaranteed
  counter-hit; kindled fighter takes +10% damage, cannot
  block during the flash. Below full meter the same press
  is Soul Kindle per SOUL-SYSTEMS.md L9 note; at full
  meter it is Nine-Soul Release. The proposal is coherent;
  it is still not locked.

### Soul Relay (Tag) — PROPOSAL
- `game/js/tag-relay.js` L20–25: "WH canon mapping
  (PROPOSED — needs owner approval): 'SOUL RELAY' —
  partners are soul-fragments of one being relaying vessels
  mid-trial. Canon precedent: SHA's three-way split
  (Saku Ra / Kinpo / Awa Pop) and KAI's two moods (King
  Tyrant / Star). Proposed mechanical names: Relay Assault
  / Relay Crash / Relay Throw."
- Mechanics themselves are implemented (raw tag, tag
  assault, tag crash, tag throw, red health — L2–18). Only
  the name awaits the owner.

## NEEDS NAME — no proprietary name in any searched source

Options below are OPTIONS ONLY, grounded in canon
vocabulary (Trial, Soul, Ember, Seal, Still Point, Verdict).
None is canon until the owner picks it. Each row states
what was searched so the owner can see the gap is real.

### Rage (state: ≤ 25% HP, once per round)
- Found as Tekken name only: `game/js/rage.js` L7 header,
  L25 (`RAGE_THRESHOLD = 0.25`), L34 (`isRaging`).
- Options: (a) Trial Wrath — the trial's anger at the
  wounded soul, still the fighter's to spend; (b) Last
  Ember — the soul burning lowest burns brightest, fits
  the soul-ember vocabulary; (c) Soul Blaze — pairs with
  Soul Urge / Soul Surge without colliding with either.
  Note: Reihou is documented as "the counter to rage"
  (SOUL-SYSTEMS.md Interactions) — whichever name is
  picked, that sentence must be reworded to match.

### Rage Art (R.1+2 while raging; cinematic armored super, 32 dmg)
- Found as Tekken name only: `game/js/rage.js` L7, L15,
  L59, L79; `game/js/fighter.js` L1551 (comment), L1587.
- Options: (a) Ember Verdict — the wounded soul's
  verdict blow (kept distinct from Trial's Seal, which is
  a banner, not a blow); (b) Final Word — one armored
  statement before the round ends; (c) Wrath Blow —
  pairs with Trial Wrath if Rage takes that name.

### Rage Drive (RD.3+4 while raging; powered-up strike)
- Found as Tekken name only: `game/js/rage.js` L10, L59,
  L93; `game/js/movesets.js` L660 (comment).
- Options: (a) Ember Drive — keeps the drive shape,
  proprietary word; (b) Wrath Strike — pairs with
  Trial Wrath; (c) Last Surge — NOT recommended if
  picked alongside Soul Surge (collision risk); listed
  only so the owner can reject it explicitly.

### Power Crush (armored attack that absorbs hits)
- NOT found as a system in searched files: zero hits for
  "power crush" in `fighter.js`, `movesets.js`, `game.js`
  (grep 2026-10-24). What DOES exist and must not be
  confused with it: (a) per-move `armor: true` flags on
  synthesized rage/urge moves; (b) moveset `crush:
  "low"/"high"` property (e.g. `pantera.json` L1676,
  L1795) = high/low evasion, a different mechanic;
  (c) "Power Bomb" = a King throw name (`pantera.json`
  L423, L431). Implementation question for the combat
  lane: is armored-attack behaviour present generically,
  or does Power Crush need implementing as well as
  naming? This audit cannot answer that from the
  searched files.
- Options: (a) Iron Soul — the soul holds its ground;
  (b) Unbroken Guard — armored advance, Tekken-free
  wording; (c) Ember Wall — pairs with Last Ember.

### Screw (T7 juggle-spin state)
- NOT found as a system in searched files: zero hits in
  `fighter.js` / `movesets.js` / `game.js`. Moveset hits
  for "screw" are King throw NAMES, not the mechanic:
  `pantera.json` L9363 "Screwdriver (MMD7)", L22517
  "Mid-Air Leg Screw", L24358 "Screwdriver", L24768
  "Leg Screw".
- Options: (a) Soul Spiral — the launched soul spins
  before the follow-up; (b) Still Spin — spin at the
  still point of the juggle; (c) Trial Turn.

### Tornado (T8's rename of Screw)
- NOT found in searched files (same grep as Screw).
  Decision shape is the owner's: one shared name for the
  juggle-spin state (recommended — Screw and Tornado are
  the same state across eras), or two era-split names.
- Options: same three as Screw, or (if split) Tornado →
  Soul Storm, Screw → Soul Spiral.

### Bound (T6 juggle-bounce state)
- NOT found as a system in searched files: "bound" hits
  in `fighter.js` (L116, L695, L712, L759, L1287, L2336,
  L2342) are T3 animation-bank binding, not the juggle
  mechanic. No Bound flag in `movesets.js` / `game.js`.
- Options: (a) Soul Bounce — plain, ownable; (b) Earth
  Rebound — the ground returns the fighter (Earth =
  Octagonal Shrine element, CANON.md L38); (c) Trial
  Bounce.

### Wall Break / Floor Break / Balcony Break
- Implemented with Tekken names + types: `game/js/stagebreaks.js`
  header L4–15 (floor / wall / balcony), L29
  (`WALL_BREAK_BONUS = 8`), L30 (`FLOOR_BREAK_BONUS =
  12`), breakables `type: 'floor'|'wall'|'balcony'`.
  Walls are also called "spirit barriers" in the stage
  defs (a framing phrase, not a locked system name).
- Standing UI law (~/MEMORY.md L46): NEVER big
  "WALL BREAK" / "TIME BREAK" text across the screen
  during fights. A proprietary name is still needed for
  small labels, docs, and records — the UI law bans the
  big text, it does not name the mechanic.
- Options (one family, three members — owner may pick
  the family or name each separately): (a) Barrier /
  Floor / Ledge Sunder — "Sunder" family (Wall Sunder,
  Floor Sunder, Ledge Sunder); (b) Spirit Break family
  (Spirit Wall Break → "Barrier Break" — note: keep
  distinct from "spirit barriers" phrasing or embrace
  it deliberately); (c) Threshold Break family (the
  trial's thresholds give way — Wall Threshold, Floor
  Threshold, Ledge Threshold).

### Slow-mo finish (match-deciding KO slow motion)
- Found as Tekken-named presentation: `game/js/rage.js`
  L13, L172–199 (`RAGE_SLOWMO_SCALE = 0.12`,
  `RAGE_SLOWMO_TIME = 1.5`).
- Options: (a) Still Moment — the still point, at the
  KO (canon-adjacent: the Shrine is "still", CANON.md
  L38); (b) Final Heartbeat — the head-world's pulse
  (CANON.md L1387: "the head has a pulse"); (c) owner
  may rule this needs NO name (presentation detail,
  not a system) — that ruling itself should be recorded
  when made.

### V-System (V-Skill / V-Trigger / V-Reversal / V-Shift)
- `game/js/v-system.js` L26: "all user-facing names are
  «name TBD» placeholders flagged for user approval
  (owner directive 2026-10-22). Code keys stay neutral
  (vskill/vtrigger/vreversal/vshift)." Also
  `docs/owner-directives.md` L237: "Eastern Mind names TBD."
- Options (umbrella + members, owner picks the set):
  (a) Soul Arts family — Soul Skill / Soul Trigger /
  Soul Reversal / Soul Shift (collision risk with Soul
  Surge/Urge/Soul Kindle noted — owner to judge);
  (b) Vessel Arts family — Vessel Skill / Vessel
  Trigger / Vessel Reversal / Vessel Shift (leans on
  vessel vocabulary, CANON.md L407+); (c) Trial Arts
  family — Trial Skill / Trial Trigger / Trial
  Reversal / Trial Shift.

### WWE entrance-tool repurpose (out of story-lane scope, listed complete)
- `docs/owner-directives.md` L234–236: repurposed toolset
  (cutscene + taunt creation only, NOT full entrances)
  "needs a proprietary WH name — TBD with the user;
  working title `WH_CINEMATIC_TOOLS_WORKING_TITLE`
  until approved."

## Rules restated (so the next lane cannot re-break them)

- NEVER conflate the four separate systems: KESSHOU
  (finisher) ≠ Nine-Soul Release (super) ≠ Reihou
  (rage purge) ≠ Trial's Seal (automatic banner).
  Each has its own gates, cost, and input in
  `docs/design/SOUL-SYSTEMS.md` L8–11.
- NEVER conflate Go Qombat (Go-based Chess Kombat
  remake, named, unwired) with Immortal Qombat
  (不死クォンバット, WH original, wired in `modes.js`).
- NEVER conflate T6 PSP "SP Rage" effect-item names
  (`teardown/tekken6-customization-research.md` §2) with
  the Rage combat system.
- NEVER conflate moveset `crush` (high/low evasion),
  "Power Bomb" (throw name), or "Screwdriver"/"Leg
  Screw" (throw names) with Power Crush / Screw systems.
- NEVER print "SOUL CLIMAX READY" until the owner
  resolves the Climax/Release variance above.
- In-universe writing (CANON.md bios, banter lines,
  story dialogue) uses ONLY the NAMED column. NEEDS
  NAME systems are referred to by description ("the
  armored blow", "the spin state") or not at all, until
  the owner picks. `game/js/versus-banter.js` now
  carries this rule in its header (this PR).

## Gaps

1. Full-repo grep not completed (clone still fetching
   at report time). Unblock: re-run the term sweep
   (`Rage`, `Power Crush`, `Screw`, `Tornado`, `Bound`,
   `Wall/Floor/Balcony Break`, `Rage Art`, `Rage Drive`)
   over a fresh clone and amend this doc if any
   additional name surfaces. No name in this audit
   depends on that sweep except the NEEDS NAME rows'
   "not found" claims, which are scoped to the searched
   files above.
2. Owner picks outstanding: all NEEDS NAME rows +
   Soul Kindle + Soul Relay proposals + Climax/Release
   variance + 魂 ACTION chord confirmation. None are
   decided by this audit.
