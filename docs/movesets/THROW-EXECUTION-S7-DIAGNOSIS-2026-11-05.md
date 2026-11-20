# THROW-EXECUTION DIAGNOSIS — Roster-100 Wave 1 item S7 (2026-11-05)

Owner instruction (verbatim, owner 2026-11-04 ~18:04 CST, as recorded in
docs/handoffs/ROSTER-100-FIX-2026-11-04.md): "All of the models need to be fixed
100% and the character select images need to be fixed 100% and um yeah
everything pretty much need to be fixed 100% the animations the inputs the
models everything and then we can move forward from there."

## Scope

The throw-execution class named by the S7 line of the roster-100 queue:
throw inputs that animate but deal 0 damage / fail to execute as throws.
Named members: Demonio 1+3, Vain Abel 1+3, Menajerii 2+4, and Pantera A1
(deliberate throws vs bankless opponents). Megami 1+3/2+4, recorded by S5
with the same 2+4-reads-0 shape, is probed as an observation and reported
here; no Megami change is made by this item. Demonio d+1 (S8) is used in
one probe sequence only as a prior-throw trigger, exactly as it appeared
in the 2026-11-03 roster-pass sequence; its own verdict belongs to S8.
Vain Abel 1+2 is NOT re-opened: it is a throw in his own DOA source data
(closed NOT-A-BUG, #1565) and appears here only as his first-throw control.

## Reconciliation with WH #1579 (Pantera A1) — read first

WH #1579 (merged 2026-11-05T14:06:36Z, merge commit f281ede8) already
landed the A1 fix before this lane ran. Its audit
(docs/movesets/PANTERA-KING-T7-AUDIT-2026-11-05.md) names the root cause:
`_enterThrownExec` never cleared the victim's `_throwHitDone`. After the
first legacy slam the victim kept `true`, so every later throw skipped
`_throwSlamDamage` while still playing `thrownExec`. The fix clears the
flag in `_enterThrownExec` and in `startThrowLock`
(game/js/fighter.js, present at lines 1869 and 2100-2106 of main
1e3f8033, verified by this lane in the served tree: sha256 of the served
fighter.js matches the pinned main blob). #1579 also reclassified
Pantera's chain follow-ups `1+3,1` / `2+4,1` (King rows 415/417) from
strike to throw in pantera.json (C1). No Pantera damage value was missing:
his records already carried their damage.

So the open S7 question was never "fix A1 again" — it is whether the
other named cases are the same mechanism (and therefore already fixed by
#1579) or separate per-fighter defects. That is an empirical question,
answered below with order-controlled probes on current main.

## Engine damage paths (game/js/fighter.js @ 1e3f8033)

A connected throw takes exactly one of two paths, and both price damage
off the attacker's resolved move record:

- Legacy lock: `startThrowLock` finds no file pair, the lock runs, and
  `completeThrow` enters `throwExec`/`thrownExec`; the victim's
  `_throwSlamDamage()` applies `move.damage * attacker.stats.power /
  victim.stats.defense` at the slam.
- Paired (Tekken grapple): `_throwPairFor` resolves a file pair (it needs
  BOTH fighters' T3 banks, an attempt row, and a selectable throw), and
  `_throwPairDamage()` applies `whMove.damage` on the same
  power/defense scale at the file's damage time (or at pair end).

A throw can therefore read 0 in exactly three honest ways: (1) the
victim-side once-per-throw guard (`_throwHitDone`) is stuck from an
earlier throw — the A1 mechanism; (2) the resolved move record carries
no damage; (3) the pair/legacy damage call is never reached. Each case
below is tested against all three.

## The evidence pattern in the prior probes

Every prior 0-damage reading was taken inside a single-session input
sequence, and in every session an EARLIER input had already executed a
damaging throw:

| Session | Earlier throw (damaging) | Probed throw | Reading |
|---|---|---|---|
| Roster pass, demonio vs pantera (2026-11-03) | d+1 throw, 21 dmg (= 24 data x 0.875) | 1+3 | animates, 0 |
| Roster pass, vainabel vs pantera (2026-11-03) | 1+2 throw, 22.9 dmg (= 25 data x 0.916) | 1+3 | animates, 0 |
| Vainabel VIDEO run (2026-11-03) | none — 1+3 was the first throw | 1+3 | 19.3 dmg (= 21 data x 0.919) |
| #1551 video, pantera vs zen | 1+3, 23.5 dmg | 2+4 | 0 |
| S5 probe, menajerii vs pantera (2026-11-05) | 1+3, 33.5 dmg (= 35 data x 0.957) | 2+4 | 0 |
| S5 probe, megami vs pantera (2026-11-05) | 1+3, 32.1 dmg (= 35 data x 0.917) | 2+4 | 0 |

That is the A1 signature exactly: first throw in a session deals its data
damage, later throws animate and deal 0. The S5 probes ran on a tree
built before #1579 merged, so their 2+4 readings predate the fix.

## Method

Order-controlled re-probes on main 1e3f8033 in the standard
fixed-step harness (Playwright headless, swiftshader; the game's own
`_update` at 120 Hz with the page paused; AI stubbed; both fighters at
1e6 HP; attacker re-spotted to 1.1 m before each input; victim HP
refilled per input so no KO ends a sequence; NO engine state is reset
between inputs in a sequence — state carries exactly as in a match).
Each run is a fresh fight (fresh page). Per input the probe records the
resolved move (key, damage, isGrab), the plan attribution, pair-vs-legacy
path evidence (`_throwPair` sampling plus the engine's own `[WH-THROW]`
console lines), the victim's state transitions, the first-damage time,
and the victim HP delta. Serve tree: repo files fetched at the pinned
main commit; served game/js/fighter.js sha256 verified identical to the
pinned blob. Canvas frame grabs are black under swiftshader in this
harness (the standing S5 limitation), so proof is the engine trace +
damage record, not screenshots. Main advanced to a2aa63e8 while the
probes ran (merges #1584, #1585, #1586, #1588); a compare of
1e3f8033...a2aa63e8 verifies none of them touches game/js/fighter.js,
any of the five fighters' moveset files, or any other file the probes
exercised, so the readings stand on current main.

Per-case expected damage (data damage x the attacker's measured
power/defense ratio vs Pantera from the 2026-11-03 pass): Demonio 1+3
21 x 0.875 = ~18.4; Vain Abel 1+3 21 x 0.919 = ~19.3; Menajerii 1+3 and
2+4 35 x 0.957 = ~33.5; Megami 1+3 and 2+4 35 x 0.917 = ~32.1; Pantera
1+3 vs Zen 23.5 (his recorded value in the #1551 session).

## Verdicts

**All four named cases are the one A1 engine mechanism, fixed by
WH #1579 before this lane ran. No case is a per-fighter data defect, and
no case needed a code or data change from this item.** Every named
record carries its damage in the fighter's own file (Demonio 1+3: his
file's copies price 21/21/19; Vain Abel 1+3: 21; Menajerii 2+4: 35;
Pantera 2+4 vs Zen: priced 23.5 after ratio). On current main every one
of them deals its full data damage in every session position, including
the exact session orders that produced the 0 readings. Results
(resolved data damage -> HP dealt; full traces in the proof JSONs):

| Case | Session order probed | Result on main 1e3f8033 | Prior 0 reading |
|---|---|---|---|
| Pantera A1 vs zen (bankless) | 1+3, 2+4, 1+3 | **23.5, 23.5, 23.5** | 23.5, then 2+4 = 0 (#1551) |
| Demonio 1+3 vs pantera | first | 19 -> **16.6** | — |
| Demonio 1+3 vs pantera | d+1 throw first (24 -> 21), then 1+3 | **16.6** | 0 (roster pass, same order) |
| Demonio vs pantera | 1+3, 2+4, 1+3 in one session | **16.6, 16.6, 16.6** | — |
| Vain Abel 1+3 vs pantera | first | 21 -> **19.3** | 19.3 (video run, first) |
| Vain Abel 1+3 vs pantera | 1+2 first (25 -> 22.9), then 1+3 | **19.3** | 0 (roster pass, same order) |
| Menajerii 2+4 vs pantera | first | 35 -> **33.5** | — |
| Menajerii vs pantera | 1+3, 2+4 (the S5 order) | **33.5, 33.5** | 33.5, then 2+4 = 0 (S5, pre-#1579 tree) |
| Menajerii vs pantera | 2+4, 1+3 (reverse) | **33.5, 33.5** | — |
| Megami 2+4 vs pantera (observation) | first | 35 -> **32.1** | — |
| Megami vs pantera (observation) | 1+3, 2+4 (the S5 order) | **32.1, 32.1** | 32.1, then 2+4 = 0 (S5, pre-#1579 tree) |

Per-case notes:

1. **Pantera A1 — FIXED BY #1579, verified here.** The A1 replication
   is exact: the #1551 session shape (deliberate throws vs bankless
   Zen) now prices every throw. Cause: the stuck `_throwHitDone`
   mechanism in the #1579 audit. Nothing about Pantera's own data was
   ever missing.
2. **Demonio 1+3 — same mechanism, verified fixed.** In the roster
   pass his d+1 (a throw-class record in his file, damage 24) executed
   first and consumed the session's one working slam; 1+3 animated and
   read 0. Replicated order on current main: d+1 deals 21, then 1+3
   deals full damage. Resolution detail: the plain `1+3` press resolves
   in this build to his file's damage-19 recorded variant (his file
   carries three 1+3 throw records — T3 row 117 at 21, a T7 Jin record
   at 21, a T8 record at 19 — all his own data), and the dealt damage is
   exactly that record's price (19 x 0.874 = 16.6), the same ratio his
   strikes measure against Pantera. His pair attempt reports the jin
   reactions pack has no throw branches for attempt row 117
   (UNMAPPED), so the throw runs the legacy path by design.
3. **Vain Abel 1+3 — same mechanism, verified fixed.** His 2026-11-03
   record already contained the control experiment: first-throw in the
   video run it dealt 19.3; second (after 1+2's throw) in the probe
   run it dealt 0. On current main both positions deal 19.3. He has no
   T3 bank (his motion source is DOA), so his throws always run the
   legacy path; the engine's `[WH-THROW]` line says so in every probe.
4. **Menajerii 2+4 — same mechanism, verified fixed.** S5's 0 reading
   was taken in second position on a serve tree built before #1579
   merged. In first position, in S5's order, and in reverse order on
   current main, 2+4 deals 33.5 (35 x 0.957). One probe attempt in
   this lane read 0 for BOTH throws with no lock ever entered; its
   transition trace shows the victim in `jump` at the 2+4 press and
   `walk` through the 1+3 press — whiffed grabs against an
   airborne/moving victim, a harness artifact of the settle logic,
   preserved as `probe-menajerii-rev-whiff-attempt.json` and superseded
   by the standing-victim re-run (33.5 / 33.5).
5. **Megami (observation) — same mechanism.** Both throws price the
   Jun row-111 throw at 32.1 in the S5 order; her 2+4 in first position
   also deals 32.1. No Megami change is made by this item.

Engine-coverage observation (not a damage defect): in every probe
above, connected throws executed through the LEGACY lock path, never
the paired file-grapple path — the pair lookup declines per bank
(jin: attempt rows carry no throw branches in the reactions pack;
roger and jun: no reactions bank is registered for the bank; vainabel:
no T3 bank exists; zen as victim: no bank, the owner's standing
no-bank decision). The legacy path prices each throw from the
attacker's own record at the same power/defense scale, which is why
damage is exact everywhere; what the missing pair coverage costs is
the paired grapple ANIMATION for these banks, not damage. Widening
pair coverage is a bank/reactions authoring question, not an S7 fix,
and is recorded here rather than silently left or unilaterally built.

## The line this item held

Fixes only on a proven cause, per fighter, from the fighter's own data.
No damage value, row, or clip was invented, imported, or copied from
another fighter anywhere in this item. Where the mechanism was the
already-landed engine fix, this item ships verification and this record,
not a second fix.

## Proof

Probe JSONs (one per fresh fight, full trial traces):
docs/proof/2026-11-05/roster-100-s7/
