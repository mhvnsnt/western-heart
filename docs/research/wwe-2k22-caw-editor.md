# WWE 2K22 Create-A-Moveset editor wiring (Western Heart)

Date: 2026-10-24. This PR wires the real, publicly documented WWE 2K22
Create-A-Moveset structure into the Western Heart Create-A-Move List
editor (`packages/creation-suite/src/movelist-editor.js`, PR #998 merged)
and adds the structure as editor data
(`packages/creation-suite/src/wwe2k22-caw-slots.js`). Structure only:
no famous names, no real-wrestler likeness, no invented move data.

## What is wired

- Editor data module: 8 top-level categories, 23 subcategories, the
  confirmed 10-slot standing grapple grid (2 strengths x 5 stick
  positions), the combo system (30 combos, 18 for 3-hit powerhouse
  characters, 3 chains: towards / away / neutral, 2–4 hits, every
  combo starts with a Light Attack, ender type is the combo type),
  global limits (100 CAW slots, 3000+ move pool, 1 Payback, 3 Special
  Stock, 3 Finishers stored), and 57 host-ready editor rows.
- Editor constants and helpers (Sections B): `WWE_CATEGORIES`,
  `WWE_SUBCATEGORIES`, `WWE_GRAPPLE_GRID`, `WWE_COMBO_RULES`,
  `WWE_GLOBAL_LIMITS`, `WWE_SLOT_STATUSES`,
  `groupEntriesByWweCategory`, `wwePositionKey`,
  `validateWwePosition`.
- Editor wiring (Sections C): WWE fields pass through
  `fromMovesetFile` and `listAllMoves`; `swapMove` adds a WWE
  position gate after the existing context check and accepts a
  `null` clear only for nullable springboard slots;
  `eligibleCandidates` filters on position as well as context;
  `serializeMoveset` / `exportMovesetJSON` / `createSavePayload`
  emit WWE fields and a separate `wwe_slots` array; the existing
  `slots` index is intentionally NOT rewritten (the game loader
  rebuilds it from `moves`); `renderEditorHTML` groups rows under
  WWE headings with Uncategorised (Tekken) last and adds a
  WWE combo-chain section only when WWE combo rows are present;
  `mount` wires swap controls on every table body, not just the
  first, so grouped tables all get swap controls.
- Button names everywhere: LP1 = Left Punch = Tekken 1,
  RP2 = Right Punch = Tekken 2, LK3 = Left Kick = Tekken 3,
  RK4 = Right Kick = Tekken 4. WH grapple translations use the
  editor's own LP1+LK3 / RP2+RK4 convention; WWE's own notation is
  Square/X/Circle (PS) / X/A/B (Xbox) plus stick direction, and the
  LP1/RP2/LK3/RK4 strings are a proposed WH translation, not a
  2K22 fact.

## Sources (public 2K22 documentation)

- Pro Game Guides, "Best movesets for CAWs in WWE 2K22", 2022-05-25
  (editor category headings):
  https://progameguides.com/wwe/best-movesets-for-caws-in-wwe-2k22/
- SmackDown Hotel, "WWE 2K22 Controls Tips and Tricks", 2022-03-21
  (10 grapple attacks, 30/18 combos, reposition rules):
  https://www.thesmackdownhotel.com/news/wwe2k22/wwe-2k22-controls-tips-and-tricks-for-beginner-players
- RealSport101, "WWE 2K22 Combos Guide":
  https://realsport101.com/article/wwe-2k22-combos-guide-how-to-light-heavy-grapple-controls
- SmackDown Hotel, "WWE 2K22 & 2K20 Creation Suite Comparison"
  (100 CAW slots, 3000+ moves):
  http://www.thesmackdownhotel.com/news/wwe2k22/wwe-2k22-2k20-creation-suite-comparison-how-much-has-changed
- SmackDown Hotel, "What Happened to Abilities, Skills & OMG Moments"
  (exactly 1 Payback per Superstar):
  https://www.thesmackdownhotel.com/news/wwe2k22/wwe-2k22-what-happened-to-abilities-skills-omg-moments
- RealSport101, "How to fill Special / Finisher meter faster"
  (3 Special Stock, max 3 Finishers stored):
  https://realsport101.com/article/wwe-2k22-how-to-fill-special-finisher-meter-faster-signature-payback
- RealSport101, "How to do springboard moves"
  ("None" is valid for every springboard position):
  https://realsport101.com/wwe2k/wwe-2k22-how-to-do-springboard-moves-dive-outside-ringside-running/
- Gamepur, "How to do a Middle Rope Diving Attack in WWE 2K22":
  https://www.gamepur.com/guides/how-to-do-a-middle-rope-diving-attack-in-wwe-2k22
- SmackDown Hotel forum, "Tutorial (Character data 1): The
  Charactermapping file in WWE 2K22" (2K22 modding storage:
  `bakedfileNN.cak` via Caketools, `charactermapping.jsfb`; no
  `.pac`/`chunk0.def` flow, no public 2K22 CAW save format):
  https://smacktalks.org/forums/topic/77748-tutorial-character-data-1-the-charactermapping-file-in-wwe-2k22/

## Slot counts: NULL until played (honesty statement)

Per-subcategory slot counts are NULL in this PR. No public source
found states a complete per-category slot count for 2K22's in-game
editor, and no per-subcategory count is estimated or presented as
recorded here. The only integer counts shipped are the ones a
public source states: the 10-slot standing grapple grid, 30/18
combos, 100 CAW slots, 1 Payback, 3 Special Stock, 3 Finishers
stored. "3 Finishers stored" is NOT a finisher-slot count. The
behind-grapple grid in the data module is an INFERRED mirror,
status `inferred-mirror, unconfirmed`, never confirmed 2K22 parity.
Diving / springboard / apron rows are gameplay-confirmed with
editor-tab placement unconfirmed. Do not fill a null from a
recommendation list, and do not distribute 30 combos as 10/10/10
across chains — the per-chain counts are unknown.

## Still owed: 2K22 editor-play recording (parent browser delegation)

This lane has no live browser and did not play 2K22. A parent
browser delegation must play 2K22's Create-A-Move-Set editor and
record, per subcategory, with screenshots:

1. Open Create-A-Move-Set for a fresh custom Superstar; open each
   top-level category in turn (Standing, Ground, Corner, Rope,
   Irish Whip, Holds, Finisher, Signature).
2. For each subcategory, count the assignable move slots shown by
   the editor (not the number of moves in the pool, not a
   recommendation list): record subcategory id + slot count +
   screenshot of the slot list.
3. Standing grapples: confirm or refute the 10-slot front grid
   (Light/Heavy x Neutral/Up/Down/Left/Right) and confirm or refute
   a separate behind grid versus a facing flag on the front grid.
4. Combos: record the per-chain counts (Towards / Away / Neutral)
   for a standard Superstar and for a 3-hit powerhouse Superstar.
5. Signature / Finisher: record how many Signature slots and how
   many Finisher slots the editor itself shows (versus "3 stored").
6. Diving / springboard / apron: record which editor tab, if any,
   each family lives under, and confirm "None" is offered for every
   springboard position.
7. File the recorded counts back into `wwe2k22-caw-slots.js`
   (replacing the matching nulls only, with the play-session date
   and screenshots cited); leave every unmeasured count null.

## Loader-verification item (carried forward, not resolved here)

The editor does NOT rewrite the opaque `slots` index in a moveset
file, and this PR adds a separate `wwe_slots` array instead. Whether
the game's moveset loader reads `wwe_slots`, rebuilds slots from
`moves` only, or needs a loader change to surface WWE slot rows
in-game is a loader-verification item for the suite lane: verify by
loading a saved moveset carrying `wwe_slots` in the game and
confirming what the loader does with it, before claiming in-game
WWE slot behaviour.

## Overlap note: creation-suite lane (PR #1057, open)

PR #1057 ("Creation Suite: remove Mixamo Soldier, wire real
templates, nested menus, universal rigs") touches
`packages/creation-suite/src/` but none of its files is
`movelist-editor.js` or `wwe2k22-caw-slots.js` (its suite files are
`body.js`, `face-texture-map.js`, `rig-adapter.js`,
`template-map.js`, plus UI and game files). This PR therefore
shares a directory with #1057 but no file; a real 3-way merge
preserves both. If #1057 merges first, this branch must still be
rebased onto latest main before its own merge, per the standing
sync rule.

## Deploy sequence

This PR does NOT merge itself. Deploy queue merges via the
3-way merge tool only when checks are green and clean, and only
after the popup deploy (PR #1076, open at filing time) has gone
first, per the user priority order: popups first, then combos /
animations work. This PR is editor wiring, not a live-play
verification: live phone playtest of the grouped editor UI and of
a saved WWE-grouped moveset is still owed after merge.
