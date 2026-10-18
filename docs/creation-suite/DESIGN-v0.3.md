# Creation Suite v0.3 — Western Heart Flagship Design

**Lane H · 2026-10-18 · branch `r2/creation-suite`**
Two pillars: **FIGHTER CREATION** (character customization) + **MOVESET CREATION**
(WWE-style editor). Depth/detail/freedom = WWE 2K levels; front-end/setup/flow =
Tekken, built from our real Tekken files. Every screen cites which game's editor
pattern it borrows from.

Related: `TEKKEN-INVENTORY.md` (what we hold), `WWE-FEATURE-MATRIX.md`
(competitor research + gap table). The older `DESIGN.md` (v0, 2026-10-14) is the
cross-game shared-package sketch — this doc is the Western Heart v0.3 build plan.

## 1. Laws the design obeys (owner-verbatim)

- **WWE = the EDITOR UX. Tekken = the CONTENT and the FIGHTING.** Never confuse
  the two. (2026-10-18)
- **INTERACTION = TAP, not drag.** "None of WWE/Tekken/MDickie do that"
  (drag-and-drop). Tap a move slot → scroll the library menus → tap the move to
  assign. Phone = tapping. (2026-10-18)
- **Federation rule:** wrestling-game animations/moves CAN enter the move library,
  but every one is wired to TEKKEN-style inputs (1/2/3/4 limbs), Tekken moveset
  structure, Tekken fighting style. Tekken inputs are the language; no wrestling
  control schemes, ever. (2026-10-18)
- **Options stack, never overwrite:** every eye, mouth interior, attire, decal,
  and part variant is saved and swappable Tekken/WWE-style. (2026-10-18)
- **Intro/victory flavor = Tekken:** fighter walks in, says something, interacts,
  then FIGHT — not a wrestling entrance. (2026-10-18)

## 2. Screen map — what each screen borrows from

| Screen (left rail) | Borrowed from | Why |
|---|---|---|
| FIGHTER SELECT (base) | **Tekken 8** — pick character → outfit slots → dressing room | T8's flow is literally "select base, then customize"; our bases = 36 roster GLBs + NEW FIGHTER |
| BODY | **WWE 2K** — Appearance: Body (morph sliders, body-type presets, skin tones) | 2K's parametric body depth; our sliders = height/weight/muscle + 16 No Mercy presets |
| ATTIRE | **WWE 2K** — Clothing: Head/Upper/Lower + layers, per-item colors, materials; **Tekken 6/8** — 4-slot overlay + full-body conflict rule | 2K's layering freedom on T6's slot system; conflict rule verified in both |
| ATTIRE → DECALS | **WWE 2K** — logo placement (any piece, scale/rotate) | Pantera MANIFEST = our "logo placement" system; options stack per the owner rule |
| WARDROBE | **DOA6** — title phrases + quick loadout slots | already in v0.2 (10 slots, two-phrase titles) |
| PROFILE | **WWE 2K** — Superstar Information + **No Mercy** page 1 | name/alias/height/weight/music + Face/Heel/Tweener crowd reaction (new v0.3) + WH canon (soul/element/land) |
| PERFORMANCE (new) | **WWE 2K22** — Performance section inside Create-a-Superstar: Entrance, Victory, Taunt, Signature, Finisher quick-picks | verified: 2K22 puts these quick-picks INSIDE the superstar flow; deep editors stay outside |
| MOVESET | **WWE 2K** — Create-a-Moveset browser/assign/preview flow; **MDickie** — tap interaction | categories → slots → tap move; tap-once = live preview (MDickie), tap ASSIGN = commit |
| LIMBS | **WH original** — DXMMII 4-arm system | no competitor equivalent; our own tech |

**Tekken 8 front-end constants across all screens:** full-screen real-time 3D
preview that is never covered (the "dressing room" principle); buy → equip loop
with Fight Money; per-character save slots; slot thumbnails via photo capture.

## 3. Moveset editor — detailed flow

```
MOVESET tab
 ├─ Slot browser: Tekken input groups (1/2/3/4 limbs · 1+3/2+4 throws ·
 │   strings 1,2 · motion inputs qcf+2/f,F+1 · rage-art/finisher slots)
 │   [borrowed: WWE 2K's position/category tree; content: Tekken inputs]
 ├─ Tap a slot → library list for that slot's eligible moves
 │   [borrowed: WWE 2K's per-category move lists]
 ├─ Library = 539 real Tekken moves (45 fighters) + wrestling-federation moves,
 │   EVERY entry showing Tekken input notation + damage + limb + source
 │   [borrowed: WWE 2K's "hundreds of moves" browser; content: Tekken per rule]
 ├─ Tap a move ONCE → LIVE PREVIEW: the preview fighter animates the move
 │   (T3 clip mapped by limb/input; per-move anim_ref when linked)
 │   [borrowed: MDickie's "touch once = preview, touch again = proceed"]
 ├─ Tap ASSIGN → move commits to the slot (Combot rule: any move, any slot,
 │   cross-roster mixing allowed — already in v0.2)
 │   [borrowed: WWE 2K's tap-to-assign; never drag-and-drop]
 └─ Dummy opponent stays in frame during browsing (WWE two-fighter preview)
```

Preview-clip mapping (honest, documented in the UI): input 1/2 → t3_light,
3/4 → t3_medium, 1+3/2+4 → t3_grab, strings/motions → t3_heavy, finisher →
t3_win_rp. A move with a real `anim_ref` always wins over the mapping.

## 4. Performance tab — detailed flow

```
PERFORMANCE tab  [inside the Create flow — WWE 2K22 Performance-section pattern]
 ├─ INTRO picker: t3_walk_fwd · t3_walk_fwd_b · t3_dash_fwd (+ later: 2K19 entrance motions)
 ├─ VICTORY picker: t3_win_rp · t3_win_lp · t3_win_rk · t3_win_lk (+ Face/Heel variants)
 ├─ TAUNT picker: t3_stance · t3_stance_b · t3_stance_c
 ├─ SIGNATURE / FINISHER move slots (link into MOVESET tab slots)
 └─ Tap an option → preview fighter plays it immediately (same tap-preview law)
```

Flavor rule: intro = walk in, say something (alias/shout line), interact, then
fight. NOT a wrestling entrance (no ramp, no pyro, no Titantron choreography).

## 5. Data contracts

**Lane F (movesets — READ ONLY):** `game/assets/movesets/{fighter_id}.json`,
45 files, moves keyed by Tekken input string. The suite keeps a DERIVED index at
`customization/create-fighter/data/TEKKEN-LIBRARY.json` (built by
`customization/build_tekken_library.py`), adding `preview_clip` +
`slot_eligibility` per move. Regenerate when Lane F's data grows. The suite never
imports `game/js/movesets.js` and never writes `game/assets/movesets/`.

**Fighter JSON (save format):** extends CHARACTER-CREATION.md §6 with
`performance: { intro, victory, victory_alignment, taunt, signature, finisher }`,
`moveset: { slotName: move_id }` (Tekken input keys), `decals: [...]`,
`attireIndex`, wardrobe, limbs. Saved to slots (`wh_create_fighter_slots`,
backward-compatible read of `wh_create_fighter_v1`).

**Game loader (`game/js/custom-fighter.js`):** converts a slot's fighter JSON →
roster object: real moveset object (no hardcoded `'jin'`), intro/victory/taunt
clip ids, body scale, stats from parameters, AI from fighting style.

## 6. WWE 2K19/2K18 pull status

Owner-confirmed 2026-10-18. Already-held assets (no new disk spend):
- `wwe2k19-entrance-pack` + `wwe2k19-moves-pack` (GitHub release
  wwe2k19-animation-packs-v1, wrestling-game repo): 445 entrance motions + 34
  motion PACs — the future INTRO/VICTORY clip pool (Yukes PAC decode pending).
- `customization/wwe2k-caw/CAW-SUITE-BREAKDOWN.md` + `~/workspace/menu-research/
  wwe2k_menus.md`: full menu/feature research (in-repo, zero disk).
- The 47GB 2K19 CSF full game stays staged for the TeraBox pipeline (disk is at
  77% — the full pull does NOT go through this VM).
Design above proceeds from the documented feature matrix; no binary pull needed
for v0.3.
