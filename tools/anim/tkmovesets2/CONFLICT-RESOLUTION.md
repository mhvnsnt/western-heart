# Conflict resolution: where does the victim's receiver animation live?

Date: 2026-11-20. Lane C (scramble-research), workdir
`_tekken-scramble-research-20261120/lane-c-pullin/`.

## The disagreement

- **Lane B** (`lane-b-mechanisms/MECHANISMS.md` §7, TekkenMods Reaction List
  doc): the victim's receiver clip lives in the **thrower's** moveset —
  "Reaction animations originate from the attacker's moveset, not the
  opponent's."
- **Lane A** (`lane-a-survey/SURVEY.md` TL;DR #4, extractor TODO): the
  thrower's move carries an Extra Move Property that sets the opponent's
  move id — i.e. the receiver lives in the **victim's** moveset, and pulling
  only King's moveset can never supply it.

## Verdict

**Both mechanisms exist, for different things. Lane B is right for throws;
Lane A's citation is real but misapplied to throws.**

- The throw receiver is delivered by the **Reaction List**: throw move →
  HitCondition → ReactionList → reaction move ids. Those ids resolve in the
  **attacker's** moveset. This is the throw-receiver mechanism.
- The Extra Move Property **0x83C3 (33731) "Set opponent's move"** is real
  and DOES set the opponent's move id — resolving in the **opponent's**
  moveset — but its documented use is the **balcony-break victim** event,
  not throws. It is a separate, scripted-event mechanism.

**Pull consequence: King-only suffices for the throw pair.** Both the
thrower's throw motion and the victim's receiver live in King's moveset,
reached by different reference paths. No victim moveset is needed for
throws. (A pull that needed EMP 0x83C3 would need the victim's moveset —
but throws do not go through that property.)

## Evidence 1 — the Reaction List doc (primary community doc, fetched live)

TekkenMods, Reaction List
(https://tekkenmods.com/documentation/Tekken_8/Basic_Information/Overview/Moveset/Structures/Reaction_List/),
"Key Notes", verbatim:

> "Every Hit Condition is paired with a Reaction List entry."
> "Reaction animations originate from the **attacker's** moveset, not the
> opponent's. For example, reaction animations to King's throws are stored
> in King's moveset and simply played on the opponent."

And "Reaction Move IDs": "These are stored as **move indexes** within the
attacker's moveset." The doc's hex example shows the standing reaction at
offset 0x0050 = Move ID 386.

## Evidence 2 — the Reaction List in code (TKMovesets2, pinned 8e6bfc1)

`TKMovesets2/GameSpecific/Editors/Editor_t7/Editor_t7.cpp:627`,
`EditorT7::MoveHitReactions(uint16_t moveId, bool opponentAirborne)`:

- reads the move's `hit_condition_addr` from `m_iterators.moves` — the
  moveset being edited (the attacker's);
- resolves every reaction move id through `ResolveMoveId()`, which resolves
  aliases against the same moveset's alias table and bounds-checks against
  `m_iterators.moves.size()` — the same moveset's move table;
- comment in the code: "Requirements judged for the preview's opponent"
  and "The game's move ids start at 0x50 … the field named default_moveid
  holds the standing reaction."

`TEditorMove.cpp:68-76` renders the opponent mannequin in the editor from
those same-moveset ids (`input.opponent.reactions`,
`input.opponent.move = [editor](int id) { editor->ResolveMoveId(id); … }`).
There is no second moveset involved anywhere in the reaction path.

## Evidence 3 — the EMP, verified in code (and its real scope)

- `TKMovesets2/.../Resources/TKMInterface/editor_t7_properties.txt:260`:
  `33731, Set opponent's move` (0x83C3).
- `TKMovesets2/.../MovesetConverters/Converter_ttt2_to_t7_Aliases.cpp:539`:
  `{ 0x826e, {.target_id = 0x83c3, .nofill = true }}, // Balconybreak
  victim: set opponent move ID`
- Same line in LukzB's fork and in the original Kiloutre extractor,
  `Tag2Aliases.py:581`: `'desc': 'Balconybreak victim: set opponent move
  ID', 'nofill': True`.

`nofill` means: when converting a moveset to another character/game, do
NOT remap this value as a move id in the attacker's table — because it
indexes the opponent's moveset. That is the grain of truth in Lane A's
claim. But the documented use is the balcony-break victim — a scripted
stage-break event — not a throw. No source ties 0x83C3 to throw receivers.

## Evidence 4 — Lane A's quoted TODO line was NOT found verbatim

Lane A quoted the extractor family's TODO as: "Don't force_type the extra
move prop that sets opponent move id". Checked 2026-11-20:

- Original Kiloutre/TekkenMovesetExtractor README TODO section (lines
  129+, read in full): no such line; no mention of `force_type`, extra move
  props, or opponent move ids.
- LukzB/TekkenMovesetExtractor README TODO (identical text): same, no
  such line.
- `force_type` grep across the original extractor, LukzB's fork, and
  TKMovesets2 (code + docs + READMEs): **zero hits**.

The underlying EMP fact is real (Evidence 3); the TODO attribution is not
verified. Treat the quote as a paraphrase, not a citation.

## Evidence 5 — decisive: our OWN repo data (King's moveset, graph.json)

`game/assets/anim/t7/king/graph.json` (King's moveset, 2787 moves, ex
`kinmot.json`). Throw move **1785** (`ThrmvLB2_00`, 1+3)
has cancel rows on throw-hit requirements, each pointing at a row in
King's OWN moveset:

| Requirement (graph id → condition) | Meaning (TKMovesets2 `editor_t7_requirements.txt`) | `to` move | Clip |
|---|---|---|---|
| 2594 → [3, 1536] | 3 = Throw Hit Forward (Standing) | 2125 `Kg_FLnage00_n` | rotsm_574 |
| 1610 → [5, 1536] | 5 = Throw Hit Left Side (Standing) | 2135 `Kg_Lnage_n` | rotsm_588 |
| 1612 → [6, 1536] | 6 = Throw Hit Right Side (Standing) | 2137 `Kg_Rnage_n` | rotsm_590 |
| 1614 → [4, 1536] | 4 = Throw Hit Backward (Standing) | 2139 `Kg_BLnage_n` | rotsm_592 |
| 2598 → [27, 2536] | 27 = Airborne Throw Hit Forward (Face Up) | 2276 `Kg_AirHizaj_n` | rotsm_718 |

Throw move **1787** (`ThrmvRB2_00`, 2+4) likewise: front → 2129
(`Kg_FRnage00_n`, rotsm_578); left → 2135; right → 2137; back → 2141
(`Kg_BRnage_n`, rotsm_594); air → 2274 (`Kg_AirDragon_n`, rotsm_716).

Why the `to` targets are the THROWER's own follow-through, not the
victim's reaction:

1. Cancel rows are evaluated by the character performing the move. The
   repo's own exe-decoded requirement evaluator
   (`docs/proof/2026-11-10/t7-requirements/README.md`, decoded from
   `TekkenGame-Win64-Shipping.exe` 0x1406f5490, args `(req, self,
   opponent)`) says: "Throw-side cases 2..16 compare the id with a
   computed throw direction." The throw-hit conditions (3/4/5/6/27) are
   judged throw-side, on the thrower's attempt — the victim never evaluates
   "Throw Hit Forward" on the thrower's move.
2. Pattern scan across the graph (2026-11-20, this lane): all **43**
   throw-class moves (`damage == 0x4000`) carry throw-hit cancel rows, and
   **every** such row targets a row inside King's own 2787-move graph —
   zero missing targets. The targets are the throw's outcome moves
   (`Kg_*nage*`, `Kg_kawazu_n`, `Kg_brain1_n`, `Kg_gsw_00n`, …). 11 of the
   43 have all five branches; the rest have subsets (chain-throw
   intermediates have L/R/B only; air-only throws have just the air row).
3. Supporting, not conclusive: 2125 carries damage 35 = Winding Nut's 35;
   2137 carries damage 42 = Knee Crusher's 42. Caveat: 2135 carries damage
   0, not Argentina Backbreaker's 40 — so damage is not a clean
   discriminator and is not relied on here.

**Consequence: `rotsm_574` / `rotsm_578` (and 588/590/592/594/716/718)
are the THROWER's throw motions, mislabeled "victim" in
`game/assets/anim/t7/king/throws/index.json` and `game/js/t7-throw-clips.js`.**
That is the role swap the owner diagnosed — confirmed by data structure,
not just by eye. Note `t7-throw-clips.js` itself (header, lines 38-41)
records the old reading explicitly ("their cancel lists … name the
VICTIM's reaction move") and even cites the throw-side requirement doc —
the pattern it verified across the 43 throw-class moves is real; the role
label it attached is inverted. This lane does NOT change that file (per
brief: propose, don't make); the fix proposal is in
`king-throw-triple.json` + COMPARISON-REPORT.md §6.

## What is still UNKNOWN (named, not filled in)

The real receiver move id. It comes from the throw move's HitCondition →
ReactionList (Move +0x60 `hit_condition_addr` → HitCondition
`reactions_addr` → `tk_reaction` standing @0x50 / left @0x58 / right
@0x5C / back @0x60 …). Our `graph.json` drops the hit-condition,
reaction, extra-property and throw-camera tables (it carries only
cancels / requirements / sequences / aliases), so the receiver id cannot
be read from any WH repo data. It needs a real King `.tkmvst` (game-gated
extraction) or the `kinmot.json` source with those tables. The tool in
this directory (`tkmvst_to_wh.py triple`) reads it the moment such a file
exists.
