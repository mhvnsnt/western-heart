# Roger Jr. bank audit — 2026-11-02

## Premise correction (read first)

The brief for this step said the Roger Jr. bank was missing (no
`Roger/RogerJr` code search hits, no kangaroo fighter). That premise is
wrong, and building a second bank from it would have duplicated a
playable fighter's kit. Verified on main:

- `game/assets/movesets/menajerii.json`: fighter `menajerii`, display
  `MENAJERII`, schema v2, `proxy: false`, **193 moves**.
- `game/js/movesets.js` `MOVESET_IDS` includes `menajerii`, annotated
  "MENAJERII (Roger Jr. TTT2 kit, fresh Tekken inputs per owner
  directive)".
- `game/js/roster-full.js`: `{ id: 'menajerii', name: 'MENAJERII',
  title: 'The Menagerie Soul', moveset: 'menajerii',
  model: 'menajerii', ... }` — a roster fighter, moveset + model wired.
- `game/assets/movesets/index.json`: menajerii 193 moves, 190 inputs
  (3 keys share a notation, e.g. side throws).
- The earlier "no bank" check inventoried only `game/assets/*_moves.json`
  (T3 animation banks). It did not check `game/assets/movesets/*.json`
  (v2 per-fighter movesets), where this kit lives.

**No duplicate bank file was created.** The work below audits the
existing kit against public TTT2 move-list structure (Wavu Wiki TTT2
movelist, cross-checked against the Tekken Wiki/Fandom TTT2 movelist, per
the 2026-11-02 research draft), lists what is genuinely missing with
counts, and names the decisions still owed. The research draft itself
(`boomer`, 117 entries) is NOT landed as a file: it was the audit input,
and its WH-generic names differ from this file's existing convention
(source move names, e.g. "Tasmanian Doormat", "Wind Up Punch").
Gap-fill entries, when they land, should follow the file's existing
convention; the draft report's §9 mapping table is the Rosetta stone
(source name ↔ WH-generic name).

## Method

Normalized-notation comparison: strip `/`, spaces, `~`, `*`, and BT
markers, and resolve stance-prefixed keys to full inputs
(`ROS 1` = `b+1+2,1`, `BOB 1` = `b+3+4,1`, `WR 4` = `WR+4`,
`WS 1` = `WS+1`). A draft entry counts as covered when its normalized
input, its stance-prefixed form, or one of its input slots exists in
menajerii. Notation variants are NOT counted as missing
(`d/f+2` = `df+2`, `d,d/f,f+1` = `qcf+1` Pile Driver,
`f,b,d/b,d,d/f,f+1` = Giant Swing).

## Coverage: draft universe 117 entries

- Covered in menajerii: **110/117 (94.0%)**.
- Confirmed gaps: **6/117 (5.1%)** — see below.
- Unresolved (not counted as missing): **1/117 (0.9%)** — see below.
- Draft frame coverage for reference: 77/117 with Wavu startup frames
  (65.8%), 40/117 without (34.2%).

### Confirmed gaps (6)

| Input | Source name | Draft frames / damage (Wavu) |
|---|---|---|
| `d+1` | Crouch Jab | i10, 6 |
| `FC.df+2` | Crouching Uppercut | i16, 31 |
| `FC.df+4` | Tail Mopping (crouch) | i21, 27 |
| `1+2+3+4` | Ki Charge | no frames, no damage (special) |
| `f,n,d,df` | Crouch Dash (transition only) | no frames (its attacks already exist: `f,N,d,d/f+1` Uppercut, `f,N,d,d/f+1+2` + `FC+1+2` Smash) |
| `b+1,2,1,4,3,3,3+4,2,1+2` | Tenstring B (10-hit) | per-hit damage in draft, no per-hit frames |

Tenstring A (`b+1,2,1,4,3,3,3,4,3,2`) IS covered: menajerii combos
"Tenstring A", same input, 113 dmg note.

### Unresolved (1, needs a Wavu re-read, not a guess)

- `f+2+4` "Tasmanian Doormat (forward)", i15~17, 35. Menajerii has
  `d/b,f+2+4` "Tombstone Pile Driver" (58 dmg, `ttt2:rog:row:80`), a
  different throw. Whether `f+2+4` is a distinct throw or a notation
  variant of a throw already in the file is not settled by the two
  public lists as crawled.

### Modeling difference (not counted as missing)

- AKS intermediate extension rows (7 draft rows: `db+4,1`,
  `db+4,3`, `db+4,3,4`, `db+4,3,4,1`, `db+4,3,4,3`, `db+4,3,4,b`,
  `db+4,3,4,3,4,b`): menajerii carries the completed chains
  (`d/b+4,3,4,3,4` Animal Kick Rush; `d/b+4,1,3>4,3>4,B` Kick
  Rushes Roll Back; ROS-chain variants) but not each intermediate as
  its own row. Whether partial strings need their own rows is an
  engine question for the moveset lane, not a can't-do-the-move gap.

### Stances

Menajerii's stance array lists ROS (Rocket, `b+1+2`), BOB (Bobbin
Dance, `b+3+4`), HRN (canon), HBS (canon). AKS and CD are NOT stance
array entries, but their moves exist: AKS entry `d/b+4` + chains,
ROC follow-ups as `ROS 1/2/3/4/1+2/3+4/F/D/F`, CD attacks under full
inputs. Only the standalone CD transition entry is missing (above).

## Menajerii's own numbers (main, 2026-11-02)

- 193 moves: 154 with startup (79.8%), 154 with damage (79.8%),
  26 with `anim_ref` (13.5%), 19 with a `ttt2:rog` anim row (9.8%).
- 4 combos, 4 canon moves (Heron/Boar/Serpent canon layer, 2026-10-24).
- `ttt2_integration` wired 2026-10-30, additive only: no existing entry
  modified, no anim-mapped entry touched.
- File size 119,657 bytes; the movesets index still says 82,574 bytes
  (moves count 193 matches) — the index entry is stale on bytes. A
  regeneration of the index, not a hand edit, should fix that.

## Discrepancies — NOT silently resolved

- **Damage source.** Menajerii matches Fandom values (Jab `1`: 7;
  `df+2`: 15; `f+3`: 20). The research draft's Wavu values differ
  (9; 20; 27). The file's `t3_source` is the Tekken Wiki TTT2
  movelist, so Fandom is the file's incumbent source. Overwriting
  with Wavu values (or vice versa) is a lane decision, not taken here.
- **Startup provenance.** Menajerii's `frame_convention` admits its
  startups are "standard Tekken archetype estimates". The draft's 77
  Wavu startups are sourced frames. Example: hopkick — menajerii
  `u+4` (input slots include `u/f+4`) 13 dmg, 0.333 s; draft `uf+4`
  Wavu 17 dmg, i15~16 (0.25 s). Upgrading estimated startups to
  sourced frames is additive-safe in principle (startup is not an
  anim mapping), but it changes 77 numbers and needs the
  damage-source decision first, so it is NOT done in this PR.
- **Wind-Up Punch WH balance.** Menajerii `b+1+4`, 60 dmg, 0.75 s
  startup, unblockable, heavy. WH balance for an unblockable of this
  size is owed (same item the draft flagged).

## Still owed (Roger kit)

- Damage-source decision: Fandom (incumbent) vs Wavu — 1 decision,
  blocks the startup upgrade and the gap-fill numbers.
- 6 gap entries above (5 moves + 1 tenstring) — blocked on the
  damage-source decision, not on sourcing (all 6 are sourced above).
- `f+2+4` resolution — 1 Wavu re-read.
- AKS intermediate-row modeling — 1 engine question.
- `anim_ref` for the remaining 167/193 moves (86.5%).
- Wind-Up Punch WH balance — 1 tuning decision.
- Movesets index bytes refresh (82,574 → 119,657) via regeneration.
- No raw TTT2/T5 game files were copied into this repo; all
  provenance above is public movelist pages only.
