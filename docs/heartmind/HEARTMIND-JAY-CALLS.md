# HeartMind — Jay calls owed (one-go ask list)

**Date:** 2026-11-08
**From:** the rename-application lane (`rename/heartmind-canon`), working from
`HEARTMIND-RENAME-MAP.md` (538 lines, §§0–§5).
**Rule:** every item below is a PROPOSED name or a rule the map says only Jay
can call. Nothing here was answered by this lane. Until Jay calls one, the
game keeps whatever it has today and the PROPOSED name stays out of the code.

**Names:** Pantera is male (he/him). Every other fighter is named only, no
guessed pronouns.

---

## 1. "Soul Seals" — the 40-symbol hunt name

- **Map citation:** §0 ("Devil Symbols → Soul Seals (PROPOSED)"), §4 systems
  table ("Soul Seals — PROPOSED (40-symbol hunt)"), §5.10 (symbol-hunt
  placement UNMEASURED).
- **What it would name:** Devil Within's 40 red symbols, as a HeartMind
  collectible hunt (find all 40 symbols across the descent).
- **Options:** accept "Soul Seals", or give it another name.
- **If unanswered:** the hunt stays unnamed and unwired (no symbol system
  exists in code today; the hunt thresholds + symbol placement are
  UNMEASURED until the decode lands them).

## 2. "Trials" — the mission-structure name

- **Map citation:** §2 (100 mission PPKs → "Trials — PROPOSED"), §4 systems
  table ("Trials — PROPOSED (mission structure)"), §4 build order step 2.
- **What it would name:** Urban Reign's 100 missions as HeartMind's trial
  structure (wave + objective + boss per trial).
- **Note:** the main menu already has a story mode called 'THE TRIAL'
  (`game/js/mainmenu.js:53`) — that is a different, pre-existing name. This
  call is about the UR-mission structure, not that menu item.
- **If unanswered:** the mission structure stays unnamed; the 100 mission
  PPKs stay undecoded and unwired.

## 3. "Descent String" — the core 3-press string name

- **Map citation:** §2 ("3-press string (third hit juggles)" →
  "Descent String — PROPOSED"), §4 systems table ("Descent String —
  PROPOSED name; mechanic CONFIRMED (Part C §6b)").
- **What it would name:** HeartMind's core string — 3 presses, third hit
  juggles (Urban Reign's feel, renamed).
- **If unanswered:** the mechanic stays in code unnamed (no UI string uses
  any name for it today).

## 4. "Dodge Window" — the timed-dodge defense name

- **Map citation:** §2 ("Dodge-timing instead of block" → "Dodge Window —
  PROPOSED"), §4 systems table ("Dodge Window — PROPOSED name; mechanic
  CONFIRMED (Part C §6b)").
- **What it would name:** HeartMind's defense — a timed dodge, not a block
  button.
- **If unanswered:** the mechanic stays in code unnamed.

## 5. "Twin Strike" — the stand double-team name

- **Map citation:** §2 ("Partner double-team commands" → "Twin Strike —
  PROPOSED"), §4 systems table ("Twin Strike — PROPOSED (stand
  double-team)").
- **What it would name:** the partner / celestial-stand double-team command
  — your stand strikes with you.
- **If unanswered:** the command stays unnamed (and unwired — no
  double-team command exists in code today).

## 6. "Soul Beam" — the Soul Surge Form beam name

- **Map citation:** §1 `gym_dwhadoh00` ("Soul Surge Form — PROPOSED 'Soul
  Beam'"), §4 systems table ("`dwhadoh00` PROPOSED 'Soul Beam'").
- **What it would name:** the Soul Surge Form's beam attack (Devil Within's
  hadou / wave attack, renamed).
- **If unanswered:** the beam stays unnamed; the file stays PROVISIONAL
  until the decode lands its contents.

## 7. "Strays of the Trial" — the Redux-guest category name

- **Map citation:** §3 (16 Tekken guests + 9 crossover guests →
  "Strays of the Trial — PROPOSED"), §5.8 ("PROPOSED category, Jay's
  call").
- **What it would name:** the 25 Redux guests as moveset-template donors in
  the template library — fighters who wandered into the descent from other
  worlds. They keep their own names as template names either way; they are
  NOT WH canon fighters.
- **Alternative the map offers:** "Guest Templates" (plain, no canon claim).
- **If unanswered:** the guests stay uncategorised in the template library.

## 8. "the Hollow" — the DW mutant group name

- **Map citation:** §5.9 ("'G Corp' ... its mutants (Adam, Eve, Duke,
  Regal, Jill) → echo donors. PROPOSED group name for the mutants: 'the
  Hollow' — Jay's call. The mutants keep no individual WH names.").
- **What it would name:** Devil Within's mutant enemies as a group of wave
  echoes.
- **If unanswered:** the mutants stay unnamed donors; no group name is used.

## 9. "the Jaundiced Stand" — BYOU's soul-body (stand) name

- **Map citation:** §5.7 ("canon names no soul-body for BYOU's stand.
  PROPOSED: 'the Jaundiced Stand' — Jay's call. Do not wire a BYOU
  body.").
- **What it would name:** the celestial stand BYOU fights through (BYOU has
  no body of its own by canon; the vessel is Zui).
- **If unanswered:** BYOU's stand stays unnamed; no BYOU body is wired
  either way.

## 10. The Jin rule — what bare "Jin" means, and the bloodline Jin

- **Map citation:** §5.1 ("Collision rule: in HeartMind text, 'Jin' alone
  always means the soul JIN (刃). Every other Jin is written out in full
  ('Jin Kazama', 'Devil Jin kit', 'bloodline Jin'). Jay's call owed:
  confirm the rule, and whether the bloodline Jin gets a name at all.").
- **What it would settle:** (a) confirm bare "Jin" = the soul JIN, never
  Jin Kazama; (b) whether the third bloodline Jin (wears a devil curse,
  shares the name with Phantom) gets a name at all.
- **Why it matters now:** the roster data still carries `base: 'Jin Kazama'`
  for RIN (`game/js/roster-full.js:13`) and DEMONIO (`game/js/roster-full.js:64`)
  — data provenance, not rendered UI text today — and the moveset library
  still maps `jin: 'Jin Kazama'` (`game/js/moveset-library.js:93`). This lane
  changed none of that: the map lists no CONFIRMED rename for the `base`
  field, and the rule itself is Jay's call.
- **If unanswered:** the rule stays unconfirmed; nothing is renamed.

## 11. The Force rule — what bare "Force" means

- **Map citation:** §5.4 ("Collision rule: in HeartMind, 'Force' alone
  means an elemental force. The currency is 'Force Claiming' (full phrase)
  and the DW economy maps onto it — PROPOSED, Jay's call.").
- **What it would settle:** confirm that bare "Force" = one of the five
  elemental forces (Wood, Fire, Earth, Metal, Water), and that the currency
  is always written out as "Force Claiming".
- **Already true in code today:** the menu text uses "elemental forces"
  (`game/js/menus.js:89`) and "Five forces" (`game/js/mainmenu.js:53`) —
  both canon-correct under this rule; "Force Claiming" already exists as a
  system name in `DESIGN.md:55`. No code change was owed for this rule.
- **If unanswered:** the rule stays unconfirmed; the existing strings stay
  as they are.

## 12. The Surge rule — the versus L-key move name

- **Map citation:** §5.6 ("Collision rule: in HeartMind, 'Surge' alone
  means the Form. The versus L-key move needs its own name if it keeps
  existing — UNMEASURED, Jay's call.").
- **What it would settle:** the versus L-key move ("Soul Surge", an
  18-damage strike costing the full meter) needs its own name, because
  "Surge" alone means the Soul Surge Form. The real versus super is
  Nine-Soul Release (1+2+3+4 chord).
- **If unanswered:** the L-key move keeps its current working name; nothing
  is renamed.

## 13. Does DW Force = Force Claiming?

- **Map citation:** §5.4 ("Jay's call owed: does DW Force = Force Claiming,
  or are they separate?"), §4 systems table ("Force (DW currency → WH Force
  Claiming) ... CONFIRMED (system name in DESIGN.md); values UNMEASURED").
- **What it would settle:** whether Devil Within's Force currency/economy
  maps onto WH Force Claiming (claim a foe's force after beating them), or
  the two are separate systems.
- **If unanswered:** the two stay unmapped; DW Force values stay UNMEASURED
  until the decode lands them.

## 14. DIABLO's player-visible "Devil" strings — what replaces them?

- **Found by this lane's grep (not in the map's row tables):** the word
  "Devil" still appears in two player-visible strings, and no CONFIRMED
  canon name exists to replace either one, so this lane changed neither.
  - Roster title: `game/js/roster-full.js:93` — DIABLO, title
    `'The Devil Soul'`.
  - Attire picker label: `game/js/attires.js:232` — DIABLO Attire 2,
    label `'ATTIRE 2 · DEVIL GOD'`.
- **Map citation:** §0 ("The word 'Devil' never appears in a HeartMind
  name"), §5.3 ("Diablo is written 'Diablo, the Devil Soul' only in canon
  docs, never in game UI").
- **What Jay's call would settle:** what DIABLO's UI title and Attire 2
  picker label should say instead. (This lane invented no replacement: the
  map gives none, and guessing one would break the no-guessing rule.)
- **If unanswered:** both strings stay exactly as they are.

## 15. "Region Strike" — the direction = body-region name (PROPOSED)

- **Map citation:** §2 ("Direction = body region" → "Region Strike —
  PROPOSED"), §4 systems table ("Region Strike / region damage ... CONFIRMED").
- **What it would name:** direction input picking the body region struck
  (head / body / legs). The name is PROPOSED; the underlying region-damage
  mechanic is the map's CONFIRMED row (see the application doc — this lane
  could NOT verify a per-region damage implementation in code at HEAD, so
  the mechanic itself is flagged to the coordinator separately).
- **If unanswered:** the direction system stays unnamed in UI.

---

## What is NOT on this list (already decided, no call needed)

- Boss and stage names (WARDEN OF THE THRESHOLD, THE MASKS, THE DROWNED
  OGRE, THE SOUL SPHERE, SHADOW SELF → THE UNMASKED; THE THRESHOLD, THE
  GALLERY OF MASKS, THE DROWNING ROOM, THE FURNACE, THE STILL POINT) —
  already in code, CONFIRMED.
- Nine-Soul Meter, Soul Surge Form, soul embers, ranks S/A/B/C, Force
  Claiming (system name) — already in code / canon docs, CONFIRMED.
- "Ogre" never alone in UI (always "Drowned Ogre" / "Unmasked") and no
  "Jack" in UI (wave brutes are "brutes") — already true in code.
- "Devil" in code comments (brawler.js / heartmind.js / fighter.js headers
  and notes) — provenance attribution, not player-visible names; this lane
  left comments alone. If Jay wants the comments reworded too, that is a
  separate call, not listed above.
