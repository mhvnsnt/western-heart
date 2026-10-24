# Pantera string audit + fix — 2026-10-24

User verdict: the game is UNPLAYABLE, combo strings missing/broken.
Pantera is the user's test character. Source of truth for this fix: T7 King
MOD frame data (TheBigTuna/Tekken-7-Frame-Data), converted to LP1/RP2
display, at `~/workspace/mvlt-community-pull/t7-all/t7-king-lp-rp-lk-rk.json`
(157 entries). Scope: STRINGS + the string input system only. Root-motion
and hitbox/hurtbox fixes are separate lanes and are NOT touched here.

## 1. What the runtime actually uses (read this before the counts)

- **Runtime notation is 1/2/3/4, not LP1/RP2.** Touch buttons emit `'1'..'4'`
  (`game/js/input.js`), `TekkenBuffer` resolves on exact 1/2/3/4 strings
  (`game/js/movesets.js`), and `Fighter` looks moves up through
  `slots` + `moves` keys (`game/js/fighter.js` `getRealMove`). Renaming keys
  to LP1/RP2 would break every lookup. So: **keys stay 1/2/3/4; LP1/RP2/LK3/RK4
  is added as `input_lp` display alongside** (owner button-name directive:
  LP1 = Tekken 1, RP2 = Tekken 2, LK3 = Tekken 3, RK4 = Tekken 4).
- **The `strings` list (81 entries) is documentation-only.** Nothing in
  `fighter.js` or `movesets.js` reads it. What fires in-game is `moves` keys
  + `slots`. The 81 breaks down as: 10 T3 dict entries, 26 plain strings,
  43 throw-chain entries (e.g. `PILE_DRIVER.1+2,1+2` — chain throws, not
  strike strings), 2 other prefixed entries. Comparing "81 vs 77" directly
  is therefore misleading; the audit below compares T7 rows against the
  keys that actually resolve.
- **Spelling bridges already exist in `slots`.** `d/f+3,4` resolves to the
  `df+3,4` move, `WS.2,2` resolves to `ws2,2`. The `d/f` vs `df` and
  `WS.` vs `ws` dualities do NOT break chaining, because `slots` maps both
  spellings. (Two gaps in that bridging were real and are fixed: the
  `d/b` variant of `d/f+4,3,d+4`, and the `WS+2,2` spelling.)
- **The user's "76 strings" vs the file's "77".** The T7 file has 77
  comma-notation rows, but `f,F+1` appears TWICE with different damage
  (29? and 33). Unique notations = 76. That is the whole discrepancy.
  This fix uses the wired t7 record's value (29) for `f,F+1`.

## 2. The string input system, measured by simulation

Simulation method: the SHIPPED `game/js/movesets.js` (`TekkenBuffer`,
`resolveMove`) and `game/js/combat-core.js` (`attackPhase`, `PressBuffer`)
run in Node, with a minimal Fighter shell whose `tryAttack` /
`_tryAttackFresh` / `_tickState` / `_drainPressBuffer` are verbatim copies
of `game/js/fighter.js` (the full class needs WebGL/DOM and cannot run
headless). 15 tests, rapid touch-style taps. Pre-fix baseline and
post-fix results are both recorded below. This simulates
input → string trigger → damage; it does NOT verify rendered animation
(see §6 — that still needs a live playtest).

### What already worked pre-fix (fast taps)

Chaining itself works for fast taps on the core strings: a press during a
move hits `tekken.continuation()`, queues `_queuedNext`, and fires at the
start of the current hit's recovery (recovery is CUT, not waited out — so
LP1,RP2 lands the second hit ~21 frames after the first, Tekken-like).
Verified pre-fix: LP1,RP2; LP1,RP2,LP1; LP1,RP2,LP1,RP2+RK4 (throw end);
f+RP2; d/f+LK3,RK4; WS+RP2,RP2; d/f+RK4,LK3,RK4. The "strings are broken"
complaint is therefore NOT primarily "chains never fire" — it is damage,
late taps, and the dead Jaguar Step path (§3).

### Buffer / cancel windows, measured

- **String window (during a move):** the whole move up to recovery start.
  A continuation press at any point in startup/active/recovery queues and
  fires at recovery start. Presses during recovery fire on the next tick.
- **PressBuffer (non-string presses):** 10 frames = 167 ms. A non-string
  press made within 10 frames of the move ending fires as a fresh move on
  the first actionable frame; a press made earlier than that is DROPPED
  silently (verified: LK3 pressed early in LP1 produces no kick at all).
  This matches Tekken's short-buffer philosophy and is NOT changed.
- **Chord window:** 50 ms in `input.js` (two limbs within 50 ms = one
  chord). A deliberate string tap is >= ~70 ms after the previous tap, so
  strings stay strings; faster double-taps can still merge into chords.
  NOT changed without touch-timing data.
- **Cancel windows:** there is no cancel-before-recovery for strings — the
  queued hit fires at recovery start, which is the Tekken-like behavior
  for these strings. You cannot input RP2 during LP1's startup and get it
  instantly; you get it buffered to recovery start. That is by design.
- **NEW — post-move grace (this fix):** pre-fix, a tap landing AFTER the
  previous hit fully recovered produced a fresh single instead of the
  string (verified: LP1 ends, RP2 100 ms later = plain RP2 jab, 6 damage).
  Touch cadence routinely lands there. Fix: 200 ms wall-clock grace after
  a non-grab attack completes (`_stringGraceUntil`, set in `_tickState`,
  consumed in `_tryAttackFresh`, canAct-only so it never chains out of a
  sidestep-cancel). After the grace expires, the same press is a fresh
  single again (verified). Getting hit clears the grace and any queued
  hit (hitstun/knockdown/KO paths in `receiveHit`/`_knockout`); a throw
  never starts a grace window.

## 3. What was actually broken (pre-fix), with numbers

### (a) Damage: the big one. String steps carried running totals, singles were gutted.

WH fires each string STEP as its own attack, so a step's runtime
`damage` must be that step's own hit — but pre-fix steps carried T8
running totals, and the firing singles carried broken values:

| Input | Pre-fix | MOD (correct) | What it is |
|---|---|---|---|
| LP1 (`1~t8.king`) | 3 | 9 | jab did 3 damage |
| RP2 (`2~t8.king`) | 6 | 13 | |
| LK3 (`3~t8.king`) | 9 | 33 | |
| RK4 (`4~t8.king`) | 11 | 27 | |
| LP1,RP2,LP1 step (`1,2,1`) | 30 (= T8 5+15+10) | 13 | last hit only |
| LP1,RP2,LP1,RP2+RK4 throw (`1,2,1,2+4`) | 70 | 40 | last hit only |
| RP2,LP1 step (`2,1~t8.king`) | 8 | 16 | |
| d/f+RK4,LK3,RK4 step (`df+4,3,4`) | 48 | 36 | |
| WS+RP2,RP2 step (`ws2,2`) | 36 | 33 | |
| b+RP2,RK4 (`b+2,4`) | 54 | 24 | + misflagged as throw (see b) |

Resulting string totals pre-fix vs MOD: LP1,RP2,LP1 = 53 vs 42;
LP1,RP2,LP1,RP2+RK4 = 123 vs 82; d/f+RK4,LK3,RK4 = 79 vs 63.
Post-fix every core string total equals its MOD total (verified in sim
and by arithmetic: 9+20+13=42, 9+20+13+40=82, 13+14+36=63, 14+33=47,
22+28=50, 17+27=44, 6+17=23, 20+19=39, 16+20=36, 18+9=27, 18+9+9=36).
T8 `multi_hit.total` values are left untouched as source records; only
the runtime `damage` field changed.

### (b) Two strike strings were flagged as throws (press a strike, get a grab)

- `b+2,4` (MOD 16,24, hit level h,m): flagged `throw/isGrab/unblockable`,
  class `throw` — in-game it lunged into a throw lock. Fixed to strike,
  damage 24. (T8's record lists a throw variant; T7 is this task's source
  and the owner's standing complaint is strikes showing as throws.)
- `f,F+2+3` plain (MOD 40, mid jumping attack): same misflag, fixed to
  strike, damage 40. Its Close throw variant is UNMAPPED (see §5).
- `JGS.3,2+3` plain (MOD 40, mid): same misflag, fixed to strike, damage 40.

### (c) Jaguar Step follow-ups were completely dead

`3+4` (Jaguar Step) never sets a JGS stance (`stance_after` has only 2
entries, both JGR), and no `3+4,1` / `3+4,2` / `3+4,3` / `3+4,4` /
`3+4,d/f+4` / `3+4,3,2+3` continuation keys existed — so pressing LP1
during Jaguar Step buffered, expired, and vanished (verified: only the
0-damage `3+4` fired). The JGS follow-up moves themselves dealt 0 damage.
Fix: slots aliases `3+4,X → JGS.X` (additive, no existing slot changed)
plus 1-spin MOD damage (JGS.1=28, JGS.2=20, JGS.3=31, JGS.4=54,
JGS.d/f+4=40). Verified post-fix: 3+4,LP1 fires `JGS.1` for 28.

### (d) One dash single was missing; two dash spellings are unresolvable by design

- `f,F+3` (MOD 24, mid) did not exist at all. Added as a new move
  (startup 15f from MOD; recovery templated from sibling `f,F+4` and
  flagged as such; animation UNMAPPED).
- `f,f,2` (held) and `f,f,1+2` (held) were NOT added on purpose: in the
  resolver they share the `[f,f]` motion dirs with `f,F+2` / `f,F+1+2`,
  and the held-final-direction rule picks the capital spelling when `f`
  is held >= 4 frames. Adding them would steal Beast Elbow / Flying Cross
  Chop presses. Their playable forms already fire: `f,f,n,2` (18, fixed
  from 17) and `f,f,n,1+2` (0, already correct) — release the stick, then
  press. A dash-phase distinction in the resolver would be needed to do
  better; that is a resolver feature, not a data fix.

### (e) First-hit singles fixed in a second audit pass

The step-damage fix initially missed five first-hit singles, caught by a
first-hit completeness audit: `df+1` 15→20, `df+2` 12→16, `d+1` 5→6,
`b+1` 13→17 (wired t7 king_100), `d+3+4` 14→18. `d+3+4` MOD variance is
documented in-file: standalone row 18 (used), wired king_88 record 14,
extended ALI row first hit 21.

## 4. The 77-row accounting (post-fix)

Of the 77 comma-notation T7 rows:

- **53 exact** (correct string, correct MOD per-hit damage): all 27 core
  multi-hit strike strings and dash/wave-dash entries, including the 5
  one-spin Jaguar Step rows.
- **20 spin-approx:** the 2–5-spin Jaguar Step rows all fire, but at
  1-spin damage (WH has no spin counter; 2–5-spin scaling is UNMAPPED).
- **2 close-approx:** `f,F+2+3 (Close)` and `3+4,3,2+3 (Close)` — the plain
  strikes are present and correct, but the close-range throw forms need
  a proximity system that does not exist (UNMAPPED).
- **1 far-approx:** `f,F+1+2 (Far)` — the near form is present at the same
  damage (20); the far/near hit-level distinction is unmodeled.
- **1 not-a-hit:** `d/f+4,3,4,B` ends with a direction input, not a hit;
  its hits are covered by `d/f+4,3,4`.
- **0 rows with no playable form.** (Four rows looked "missing" under
  naive key matching but resolve via existing forms: the `d/b`-or-`d`
  variant via the new `d/b` alias + `df+4,3,d+4`; both `f,f` held
  spellings via their neutral variants; the `3+4,1+4`-or-`3+4,2+3` throw
  via its first alternative `3+4,1+4`. Its second alternative `3+4,2+3`
  does not exist — noted.)

Pre-fix, **0 of the 77 rows were fully correct** on string + damage: every
damage-bearing row had at least one hit at the wrong value, and the
Jaguar Step rows did not fire at all. (The `strings` list's 81 entries
were never the right denominator — see §1.)

On the "correct animation" bar, post-fix is still **0 of 77 verified**:
no T7-wired string step carries a `t3_row` (all are `None`), so clips
come from `fighter.js`'s notation/match/donor fallback and are
UNVERIFIED per move. That is the remaining gap, and it belongs to the
animation-mapping lane, not this fix.

## 5. UNMAPPED list (string works, animation or variant unproven)

- **All T7 string-step animations:** `t3_row` is `None` for every
  T7-wired step (two carry `anim_t3` "nearest" rows, which the code itself
  flags as approximate and wrong-button 43% of the time). No step maps to
  T3 row 35 (the LP1+RP2 chord row) in this file — verified by scan — and
  the runtime's button-mask filter excludes chord rows from the match
  pool, but per-move clips are still unverified. **Wrong animation is
  better than a missing string, per the task — strings are all wired;
  clips need the animation lane.**
- **New `f,F+3`:** `anim_unmapped: true`, no verified row.
- **Spin scaling:** 2–5-spin damage (JGS.1 up to 41, JGS.4 up to 70).
- **Proximity variants:** `d/f+3+4 (Close)`, `f,F+2+3 (Close)`,
  `3+4,3,2+3 (Close)`, `f,F+1+2 (Far)` throw/level forms.
- **ALI:** the T7 `ALI RP2` row (18,13) is ambiguous and `ALI.1` does not
  exist; `ALI.2` (6) left untouched.
- **`3+4,2+3`:** second alternative of the `3+4,1+4`-or-`3+4,2+3` throw;
  first alternative present.

## 6. What was deliberately NOT changed

- `1+2` (19) is Pantera's WH SIGNATURE "Battle Itself", not King's T7
  1+2 — MOD 24 was NOT applied. Its string steps (`1+2,1` → 28,
  `1+2,3` → 33) use MOD last-hit damage, so totals from the signature
  differ from T7 by design (47 vs 52 for `1+2,1`).
- Plain T3 records (`1`, `2`, `2,1`, `WS.2,2` shadow keys) are left as T3
  source records; they are shadowed by `slots` and do not fire.
- T8 `multi_hit.total` values left untouched (source records).
- `d/f+3+4` (Frankensteiner throw, 45) left alone: its T7 plain-vs-close
  status is ambiguous and its T8 throw record is coherent.
- PressBuffer (10f), chord window (50 ms), queue-at-recovery timing:
  measured Tekken-like, unchanged.
- No animation rows were guessed. No chord-row mappings. No main pushes.

## 7. Files changed

- `game/assets/movesets/pantera.json` — MOD per-hit damage on 54 firing
  keys (49 in the first pass + 5 first-hit singles), throw-flag fixes on
  3 keys, 1 new move (`f,F+3`), 10 additive slots aliases, `input_lp` on
  all touched moves + all 55 dict entries in `strings`, and a top-level
  `string_fix_20261024` record of the rule and the deliberate
  non-changes. Runtime keys unchanged (1/2/3/4).
- `game/js/fighter.js` — 200 ms post-move string grace (+ grace start in
  `_tickState`, consumption in `_tryAttackFresh`, clearing on
  hitstun/knockdown/KO). 20 changed lines, all additive except one line
  split.

## 8. Verification still owed (cannot be done from this lane)

This fix was verified by simulation (input → trigger → damage) on the
shipped resolver/phase/buffer code — not by playing the live build (this
lane has no live browser). Before calling strings "fixed" for the user:
play the live build on a phone, tap LP1,RP2 / LP1,RP2,LP1 / 3+4,LP1 /
d/f+LK3,RK4, confirm the strings fire AND the clips look like the right
limbs (animation lane owns any wrong-clip findings), and confirm the
damage numbers above land. Deploy follows the merge.

## Rebase note (2026-10-24)

`game/js/fighter.js` in this PR was rebased onto current main (hitbox/reaction lane) after the first merge attempt was refused for stale-base lines: the grace edits were re-applied surgically onto main's newer fighter.js with no other content changed.
