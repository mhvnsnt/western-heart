# T3 animation classification — GPU Job 1 output (DATA ONLY)

Status: DATA PREP for Priority #2 (combos + animations). This commit adds
classifier output and this note ONLY. It changes NO resolver, combat, or
animation logic, NO moveset row, and NO editor code. It is NOT merged,
NOT deployed, and NOT play-verified at filing. Per the locked user sequence
of 2026-10-24 20:56 CDT, Priority #2 work lands ONLY after the Priority #1
fight-UI popup fix (PR #1078) reaches the playable build and passes the
popup play pass. The coordinator sequences any merge of this PR behind
that deploy. Do not merge this PR ahead of that gate.

Button names in user-facing text use LP1/RP2/LK3/RK4: LP1 = Left Punch =
Tekken 1, RP2 = Right Punch = Tekken 2, LK3 = Left Kick = Tekken 3,
RK4 = Right Kick = Tekken 4.

## Source

GPU Job 1, T3 animation classifier, run 2026-10-24 8:25-9:27 PM CDT.
Backend: torch CUDA (Tesla T4). Elapsed: 6.1s, 774.3 rows/sec.
Thresholds: rise >= 0.15 m, fall >= 0.10 m, drop >= 0.15 m.
Scale authority: tools/anim/t3_row_bake.py (rx/ry/rz int16 millimetres).
Target list: 22 banks. Classified: 21 banks. Missing: heihachi (see below).

Job verification note, quoted verbatim from the classifier output
(JOB-VERIFICATION.txt):

> T3 anim batch analysis job
> Banks processed: 21 of 21 inputs
> Rows classified: 4685
> Backend: torch CUDA (Tesla T4)
> Elapsed: 6.1s (774.3 rows/sec)
> Thresholds: rise>=0.15m, fall>=0.1m, drop>=0.15m
> Scale authority: tools/anim/t3_row_bake.py (rx/ry/rz int16 millimetres)

## Files committed (verbatim job output, no edits)

Placement decision, checked against main before filing: per-bank animation
packs live under game/assets/anim/t3/{bank}/ (each with rows.pack.json),
and a top-level ancillary file already lives at
game/assets/anim/t3/reactions.json. The combined classifier output therefore
goes at the game/assets/anim/t3/ top level, alongside reactions.json,
NOT split per bank (splitting would alter the job output) and NOT under
docs/anim/ (docs/anim/ holds prose docs, not game data).

- game/assets/anim/t3/anim-classification.json — 1,336,276 bytes.
  21 banks, 4,685 rows. Top-level keys are bank names; each row key is the
  T3 row number, with fields: class, rise_m, fall_m, drop_m, start_y_m,
  peak_y_m, end_y_m, net_travel_m, peak_travel_m, frames, used_by.
- game/assets/anim/t3/anim-classification-summary.json — 4,337 bytes.
  Per-bank row counts, class counts, format (wh-anim-pack/1), source_bank.
- docs/anim/T3-ANIM-CLASSIFICATION-JOB1-2026-10-24.md — this doc.

Verification performed before filing (from the unzipped job output, not
assumed): zip size 100,528 bytes; anim-classification.json 1,336,276 bytes
exactly; 21 top-level banks; row counts sum to 4,685; class totals
crouching 854 / jumping 1,181 / standing 2,650.

## Per-bank table (from anim-classification-summary.json)

| bank | rows | crouching | jumping | standing | source_bank |
| --- | ---: | ---: | ---: | ---: | --- |
| anna | 213 | 33 | 42 | 138 | teardown/tekken3/animations/divmot17_anna.bin |
| armorking | 187 | 36 | 47 | 104 | teardown/tekken3/animations/divmot03_king.bin |
| bosconovitch | 647 | 120 | 158 | 369 | teardown/tekken3/animations/divmot18_bosconovitch.bin |
| bryan | 160 | 31 | 40 | 89 | teardown/tekken3/animations/divmot12_bryan.bin |
| eddy | 211 | 50 | 70 | 91 | teardown/tekken3/animations/divmot08_eddy.bin |
| forestlaw_on_law | 198 | 37 | 51 | 110 | teardown/tekken3/animations/divmot20_forestlaw.bin |
| gon | 148 | 18 | 50 | 80 | teardown/tekken3/animations/divmot19_gon.bin |
| gunjack | 238 | 41 | 43 | 154 | teardown/tekken3/animations/divmot16_gunjack.bin |
| heihachi_on_jin | 195 | 28 | 60 | 107 | teardown/tekken3/animations/divmot13_heihachi.bin |
| hwoarang | 187 | 32 | 51 | 104 | teardown/tekken3/animations/divmot06_hwoarang.bin |
| jin | 220 | 30 | 56 | 134 | teardown/tekken3/animations/divmot09_jin.bin |
| julia | 175 | 34 | 37 | 104 | teardown/tekken3/animations/divmot10_julia.bin |
| king_on_pantera_leoman | 256 | 42 | 63 | 151 | teardown/tekken3/animations/divmot03_king.bin |
| kuma | 164 | 34 | 37 | 93 | teardown/tekken3/animations/divmot11_kuma.bin |
| law | 219 | 30 | 73 | 116 | teardown/tekken3/animations/divmot01_law.bin |
| lei | 262 | 41 | 55 | 166 | teardown/tekken3/animations/divmot02_lei.bin |
| nina | 203 | 32 | 43 | 128 | teardown/tekken3/animations/divmot05_nina.bin |
| ogre | 189 | 34 | 56 | 99 | teardown/tekken3/animations/divmot14_ogre.bin |
| paul | 168 | 35 | 42 | 91 | teardown/tekken3/animations/divmot00_paul.bin |
| xiaoyu | 230 | 64 | 59 | 107 | teardown/tekken3/animations/divmot07_xiaoyu.bin |
| yoshimitsu | 215 | 52 | 48 | 115 | teardown/tekken3/animations/divmot04_yoshimitsu.bin |

Largest bank: bosconovitch, 647 rows. King bank
(king_on_pantera_leoman): 256 rows (42 crouching / 63 jumping / 151
standing).

## Row 38 vs row 39 resolution — King bank (king_on_pantera_leoman)

File evidence, read from game/assets/anim/t3/anim-classification.json
as committed (bank king_on_pantera_leoman):

Row 38:

- class: jumping
- rise_m: 0.224 (>= 0.15 m threshold), fall_m: 0.841 (>= 0.10 m threshold),
  drop_m: 0.7
- start_y_m: 1.518, peak_y_m: 1.742, end_y_m: 0.901
- net_travel_m: 0.0, peak_travel_m: 0.0, frames: 20
- used_by: ["cainelias"] — pantera is NOT in this list.

Row 39:

- class: jumping
- rise_m: 0.224, fall_m: 0.841, drop_m: 0.7
- start_y_m: 1.518, peak_y_m: 1.742, end_y_m: 0.901
- net_travel_m: 0.0, peak_travel_m: 0.0, frames: 20
- used_by: ["armor-king", "hugo", "kronos", "kronos-attire2", "kutz",
  "marduk", "pantera", "yukihyo", "zangief"] — pantera IS in this list.

Resolution:

- Both rows jump. The trajectory values are IDENTICAL between row 38 and
  row 39 on every measured field above, so the jumping finding does not
  depend on which of the two keys is cited.
- Row 38 is NOT re-labeled, NOT re-attributed, and NOT treated as
  Pantera's clip: its used_by list contains only cainelias. Row 39 is the
  King-bank key whose used_by list includes pantera.
- No moveset row was repointed in this PR. No mapping was invented.
- Boundary, stated plainly: the classifier output lists WHICH fighters use
  a key (used_by); it does NOT state which input slot (LP1, RP2, LK3, RK4,
  or any other input) points at key 39 for Pantera. That slot-to-key link
  is UNMAPPED in this data and must be confirmed from Pantera's moveset
  file in Stage 1 — do not assume LP1 = key 39 from this file alone.
- Additional observed fact, same file: row 40 carries the identical
  trajectory values as rows 38 and 39 (class jumping, rise_m 0.224,
  fall_m 0.841, 20 frames) with used_by including pantera. The jumping
  clip is therefore shared across keys 38/39/40, not unique to one key.
  Stage 1 must work from the moveset file's actual key reference, not
  from key-number proximity.
- What this does prove for the user's jumping-punch report: a King-bank
  clip that Pantera's file uses (key 39, and likewise key 40) genuinely
  leaves the ground — rise 0.224 m, fall 0.841 m, start 1.518 m to peak
  1.742 m to end 0.901 m over 20 frames. A standing punch label on such a
  clip is contradicted by the clip's own trajectory.

## Heihachi data gap (repo data gap, NOT substituted)

- The 22nd target bank, heihachi, was NOT classified. Exact error from the
  job (HEIHACHI-NOTE.txt): HTTP 404 Not Found for
  https://raw.githubusercontent.com/mhvnsnt/western-heart/main/game/assets/anim/t3/heihachi/rows.pack.json
- Independently confirmed against main before filing:
  game/assets/anim/t3/heihachi/ contains 33 items (hit_frames.json,
  reactions.pack.json, skeleton.json, t3_*.json moveset files) and NO
  rows.pack.json.
- Heihachi motion data IS present under a different bank label and WAS
  classified: game/assets/anim/t3/heihachi_on_jin/rows.pack.json
  (1,182,517 bytes on main, bank field
  teardown/tekken3/animations/divmot13_heihachi.bin) — 195 rows
  (28 crouching / 60 jumping / 107 standing) in this output.
- NO substitution was made: heihachi_on_jin rows were NOT copied under
  the heihachi name, and no alias was created silently. Open item for a
  follow-up data PR: either land a real
  game/assets/anim/t3/heihachi/rows.pack.json, or record a documented
  alias from heihachi to heihachi_on_jin with owner approval. Until then,
  heihachi lookups against this classification file are UNMAPPED.

## Wire-in point for Stage 1 — validateAssignment() (DOCUMENTED ONLY)

No code in this section was changed. This is the exact point Stage 1
must touch, after the popup play pass, so that the moveset editor checks
REAL clip classes (jumping / crouching / standing) instead of JSON labels.

File: packages/creation-suite/src/movelist-editor.js (on main at filing).

- validateAssignment(slotContext, candidate) — line 409. Its stance check
  (lines 427-435) compares props.stance against slotContext.stance and
  returns status "wrong" with allowed false on mismatch. It does NOT
  measure clips itself; it trusts whatever deriveCandidateProperties()
  returns.
- deriveCandidateProperties(candidate) — line 346. Called by
  validateAssignment() at line 421. It reads candidate.properties (or
  candidate.anim_properties) ONLY when clip.source === "clip" (line 353);
  otherwise it falls back to properties derived from the candidate's own
  Tekken input (source "input", lines 380-391). The file header (lines
  49-60) states the failure this creates: input-derived properties
  cannot catch a clip that jumps while its JSON label says "jab".
- Library entry shape (lines 511-517) already carries t3_bank and t3_row
  alongside anim_ref. That pair is the join key.
- Stage 1 wire-in, precisely: the host / library builder that produces
  candidates (movelist-data.js entries, or fromMovesetFile() in the same
  editor module) must attach, for each T3 candidate,
  properties: { stance: <class from anim-classification.json for that
  candidate's (t3_bank, t3_row)>, source: "clip", ... } — reading from
  game/assets/anim/t3/anim-classification.json committed here. Once
  source is "clip", deriveCandidateProperties() returns the measured
  class, validateAssignment()'s stance check enforces it, and a jumping
  clip in a standing slot comes back "wrong" instead of passing on its
  label.
- Class vocabulary mapping: the classifier emits exactly three classes —
  jumping, crouching, standing — which map directly onto the editor's
  stance vocabulary (standing | crouching | jumping | rising |
  crouch_dash | back_turned | sidestep | unknown | any, line 292-293).
  rising, crouch_dash, back_turned, and sidestep are NOT produced by this
  classifier and remain UNMAPPED from this data; Stage 1 must not invent
  them from these rows.
- What Stage 1 must still confirm from moveset files (not in this data):
  the slot-to-key link for Pantera (see row 38 vs 39 above), and the
  heihachi gap (see above). Neither is resolved by this commit.

## Explicitly NOT in this PR

- No changes to packages/creation-suite/src/movelist-editor.js or any
  other .js/.mjs/.py resolver, combat, or animation file.
- No changes to any game/assets/movesets/ file or any
  game/assets/anim/t3/{bank}/ file.
- No deletions. All three committed files are new additions.
- No merge, no deploy, no play-verification claim. Merge-readiness only,
  sequenced behind the popup deploy per the locked order.
