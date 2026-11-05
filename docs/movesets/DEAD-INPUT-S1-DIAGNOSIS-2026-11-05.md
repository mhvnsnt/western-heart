# DEAD-INPUT DIAGNOSIS — Roster-100 Wave 1 item S1 (2026-11-05)

Owner instruction (verbatim, owner 2026-11-04 ~18:04 CST, as recorded in
docs/handoffs/ROSTER-100-FIX-2026-11-04.md): "All of the models need to be fixed
100% and the character select images need to be fixed 100% and um yeah
everything pretty much need to be fixed 100% the animations the inputs the
models everything and then we can move forward from there."

## Scope

Exactly the 7 undiagnosed dead BASICS slots named by the S1 line of the
roster-100 queue: charger d/f+1, charger d/f+2, dorowani d/f+2, dorowani
u/f+4, ryuji-rock d/f+1, ryuji-rock d/f+2, deathfang d/f+1. The 5 dead d+1
data gaps (#1560 class D), Pantera's 11 still-dead slots, Demonio d+1 (S8)
and the throw-execution class (S7) are NOT in this item's scope.

## Method

The #1560 method: for each slot, classify (a) slotting/preparation gap — the
fighter's own moveset data has the row but it never gets prepared/bound;
(b) plan-parse/notation gap; (c) genuine data gap — no honest row exists in
the fighter's own recorded data.

Diagnosis ran on the real engine from main at 3f63454e (game/js/movesets.js +
full-movelist.js + canon-names.js) in Node: `registerMoveset` then
`resolveMoveKey`. The baseline trace reproduced the roster-pass verdicts
(docs/proof/2026-11-03/roster/roster-verdicts-20261103.json) exactly: all 7
slots resolve to null while the same fighters' other BASICS resolve.

Each fighter's merged file was then scanned exhaustively: keys,
canon(key), canon(input), input_slots, t7_command, t8_id, t3_command
(including numpad and any-of encodings), string heads, and raw-text
occurrences. Bank evidence comes from the repo's own T3 banks
(teardown/tekken3) and from same-bank merged files already on main.

## The line this item held (same as #1560)

S1 repairs the binding of a row that is PRESENT in the fighter's own file.
It never imports a row, never fabricates a move, a clip, or damage data.
A row that exists only in the source bank but never entered the fighter's
merged file is a data gap for owner adjudication — the #1560 class-D shape
(cainelias: the king bank has d+1 via Pantera; cainelias's own merge lacks
it; documented, not imported).

## Verdicts

### 1. charger d/f+2 — FIXED (class a: binding/label gap)

Charger's T3 source is the bryan bank. Bank row 149 IS present in
charger.json — as key `2_r149` — with its fight data intact and correctly
scaled (damage 9 = bank 16 in this file's WH scaling; anim_ref
`t3:bryan:row:149`). What the 2026-10-20 merge (tools/gen-movesets-t3.py)
dropped is the row's direction: its recorded `t3_command` is the bare `RP`,
its `input` is `2_r149`, its `input_slots` is `["2"]`. The bank's own
record of the same row survives in skull.json (same bank, same row): key
`d/f+2`, `t3_command` `3+RP`, `t3_damage` 16. The mislabeled row is bound
to no playable input today: pressing `2` resolves to key `2` (bryan r48).

Repair (charger.json and charger-attire2.json — the fighter's attire-2 file
carries the identical row with the identical mislabel): the row's recorded
`input` is corrected to `d/f+2`, `t3_command` to `3+RP`, `input_slots` to
`["d/f+2"]`, and the file gains the binding `"slots": {"d/f+2": "2_r149"}`.
No fight datum changes: key, name, damage, startup, active, recovery,
anim_ref are byte-identical. Post-fix trace: `d/f+2` resolves to `2_r149`
(strike, damage 9) in both files. Browser re-probe (below): the slot now
FIRES the r149 strike in a real fight (press=true, anim row 149) at every
tested spacing, where it was press=false before.

Damage rider (stated plainly, not hidden): in the S1 probe harness
(software-GL Chromium; see Re-probe) the fired r149 strike registers 0 HP
damage, while the same fighter's other bank-row strikes register their
recorded damage (1→10, 2→11, d+1→14, d+2→12, u/f+4→12). The row's hit
data exists (game/assets/anim/t3/bryan/hit_frames.json row 149: active
frame 23, attack word 535), and the reference roster harness measured the
same bank row dealing damage through Skull (19, roster pass 2026-11-03),
whose file carries the later T7 frame-data wiring for the row (startup
0.2167 from T7 data; the in-fight clip resolves through that wiring).
Charger's record carries the bank's raw active frame as its startup
(0.383) and a single-frame active window (hit_frames 23–23), which the
software-GL harness's coarse stepping can skip. Whether any residual
damage-path gap remains on real hardware belongs to the fire-no-damage
workstream (S6, which consumes the S5 hit-frames production) — it is a
hit-data question, not a slotting question, and it is NOT fixed here. What
S1 fixed is the dead slot: the input now fires the fighter's own row.

### 2. charger d/f+1 — DATA GAP (class c: merge-provenance)

The bryan bank HAS this row: r146 (command 3+LP, bank damage 15), and
skull.json carries it keyed `d/f+1`. But r146 never entered charger's
merge: the string `146` occurs ZERO times in charger.json — not as a key,
not as a t3_row, not in hit_words. His curated layer agrees: blanka.json
(the file his record names as source_moveset) has no d/f+1 either.
sf-blanka.json does have d/f+1 rows, but that is a different roster
fighter's file, not charger's recorded data — borrowing it is exactly the
move #1560 refused for cainelias. Documented for owner adjudication
(import-the-bank-row decision), not fixed here.

### 3. dorowani d/f+2 — DATA GAP (class c: pure source gap)

Dorowani's T3 source is the gon bank (merge_sources.py, 2026-10-23, bases:
gon only). The gon bank contains no attack row entered by 3+RP: its state
tables route 3+RP only to common/state slots (725, 1016) and to row 335, a
0-damage non-attack row. The generator's own pure-bank product,
t3-gon.json, likewise has no d/f+2. There is no row to slot.

### 4. dorowani u/f+4 — DATA GAP (class c: pure source gap)

The gon bank has no 9+RK entry to any attack row (the token occurs only
inside 6/9+RK air-table entries bound for common slots). t3-gon.json has
no u/f+4 (and no u/f+2). Same conclusion as d/f+2: Gon's recorded T3 data
simply has no such move.

### 5. ryuji-rock d/f+1 — DATA GAP (class c: merge-provenance)

The king bank HAS this row: r117, carried by armor-king.json keyed
`d/f+1`. Ryuji-rock's file is a curated union build (cornerstone_build,
2026-10-21: the Yamazaki KOF set + Rock canon entries + 18 king rows);
r117 is not among the king rows it carried, and the Yamazaki layer has no
standing d/f+1 — its d/f+1 occurrences are the DP motions (f,n,d,d/f+1
Todome/Sabaki) and the d/f+1+2 Rock Bottom throw, which are different
moves and already bound. This gap rides the recorded owner ruling #6
(ryuji-rock's place in the ryuji hybrid is an owner decision).

### 6. ryuji-rock d/f+2 — DATA GAP (class c: merge-provenance)

Same shape: king r202 ("Concussion Hook") exists and is carried by
armor-king.json keyed `d/f+2`; it never entered ryuji-rock's curated
build, and no Yamazaki or canon row in his file is a standing d/f+2.

### 7. deathfang d/f+1 — DATA GAP (class c: merge-provenance)

The heihachi bank HAS this row: its standing state table (bank row 168)
enters row 109 on 3+LP (damage 20, standing stance slot, 58-frame stream).
Deathfang's curated merge (forward_merge over an Iori base + heihachi
proxy) carried only 16 heihachi rows; r109 is not one of them. His Iori
layer's d/f+1 occurrences are all inside the Oniyaki DP motions
(f,n,d,d/f+1 / f,n,d,d/f+1+2) — different moves, already bound. Not
imported, per the line above.

## Regression

Full-registry slot-map diff over all 163 files in game/assets/movesets/
(real engine, original vs repaired): exactly 2 slot additions —
charger d/f+2 and charger-attire2 d/f+2, both to the pre-existing row
`2_r149`. 0 slots overwritten, 0 removed, every other file's slot map
unchanged (zen and chatur included; neither is touched by this change).

## Re-probe

Engine trace (real engine from main): proof file
`docs/proof/2026-11-05/dead-input-s1/reprobe-verdicts-s1-20261105.json`.
Before: all 7 slots resolve null. After: charger d/f+2 resolves to the
r149 strike in both of the fighter's files; the 6 data-gap slots still
resolve null — re-probed to confirm they stay dead for the documented
data reason, not for a fixable binding reason. Charger's remaining BASICS
re-probed unchanged (1, 2, 3, 4, d+1→`7`, d+2→`8`, f+1→`5`, f+2, b+1→`9`,
b+2→`10`, d/f+1+2→`df+1+2`, u/f+4→`f_c36_r86`, 1+2).

Browser fight re-probe (real keyboard input through the game's own input
path, opponent Pantera, stage Shrine of the Blade, identity gate
`p1.char.id` + round state `fight` verified per run; probe tree = main
3f63454e + this repair, asset bases pointed at the local tree because
remote candidates hang in this container's Chromium — probe-only, the
live Pages build untouched). Per-fighter results:
`docs/proof/2026-11-05/dead-input-s1/browser-probe-charger-20261105.json`,
`docs/proof/2026-11-05/dead-input-s1/browser-probe-dorowani-20261105.json`,
`docs/proof/2026-11-05/dead-input-s1/browser-probe-ryuji-rock-20261105.json`,
`docs/proof/2026-11-05/dead-input-s1/browser-probe-deathfang-20261105.json`;
fight frame: `docs/proof/2026-11-05/dead-input-s1/fight-frame-charger-20261105.png`
(HUD/stage level — the arena renderer was stubbed during input probing
for software-GL performance, so the frame shows the fight HUD, stage and
HP state rather than the models).

| fighter slot | before (roster pass) | after (browser re-probe) |
| --- | --- | --- |
| charger d/f+1 | press=false | no d/f+1 move fires (falls back to standing `1`) — data gap confirmed |
| charger d/f+2 | press=false | **press=true, key `2_r149`, anim row 149** — fires; HP damage 0 in this harness (see the damage rider in §1) |
| dorowani d/f+2 | press=false | no attack fires — data gap confirmed |
| dorowani u/f+4 | press=false | no u/f+4 move fires (falls back to standing `4`) — data gap confirmed |
| ryuji-rock d/f+1 | press=false | no d/f+1 move fires (falls back to close standing RP) — data gap confirmed |
| ryuji-rock d/f+2 | press=false | no d/f+2 move fires (same fallback) — data gap confirmed |
| deathfang d/f+1 | press=false | no d/f+1 move fires (falls back to his d+2, key `8`) — data gap confirmed |

Control damage in the same runs (proves the harness measures damage when
a strike connects): charger 1→10, 2→11, 3→12, d+1→14, d+2→12, u/f+4→12;
dorowani d/f+1 fires (his known working move).

Unit test: `test/dead-input-s1-slotting.test.mjs`.

## Summary

1 fixed (charger d/f+2, in both of the fighter's files), 6 documented
data gaps: 4 merge-provenance (charger d/f+1, ryuji-rock d/f+1,
ryuji-rock d/f+2, deathfang d/f+1 — the bank row exists and is named in
this doc; importing it is the owner's call, the #1560 class-D pattern) and
2 pure source gaps (dorowani d/f+2, dorowani u/f+4 — Gon's bank has no
such moves at all).
