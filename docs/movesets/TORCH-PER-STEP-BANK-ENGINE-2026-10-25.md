# Torch per-step-bank engine support (2026-10-25)

Stack: #1096 (step-plan engine) → this PR (engine) → torch Batch 1 (#1136,
plans) → torch Batch 2. This PR merges AFTER #1096. It touches NO
moveset file and NO plan: torch.json plans are read-only evidence here.

## 1. The problem, from file evidence

Torch's bound in-game bank is anna (fighter.js #1096 FIGHTER_BANK
override torch→anna + moveset anim_bank anna). Torch is dual-bank: its
T3 moves carry t3_source jin (145) and anna (224), and its Batch 1
plans adjudicate each step against ITS OWN move's bank.

The #1096 step-plan branch resolved every step's row against the bound
bank ONLY:

- `_resolveStepPlan` returned `'row:' + st.row` for verified steps.
- `_attackClip` retargeted that name from `this._t3.clips` (bound bank).
- `_rootMotionApply` read root travel from `this._t3.clips[p.name]`.

So a jin-bank gate-verified step could not wire: writing it as
verified row N would have played anna row N — a wrong-bank clip.
Batch 1 therefore recorded those steps as review, row null,
`bank_verified_row` preserved, with a BANK-BLOCKED reason. 22
canonical-plan instances (34 plan-key instances incl. twins, 8
distinct prefix/row pairs: 2→220, 2,1→221, 2,1,2→222, 2,1,2,2→223,
1,2→249, d+1+2→92, d+1+2,2→93, d+1+2,1,2→183).

This PR does NOT rebind torch to jin. The bound bank stays anna.
The fix is per-step-bank resolution.

## 2. Schema — no plan-file change (STOP-check answer)

The task asked: if per-step-bank resolution needs a schema change to
the plan files themselves, report that and STOP before rewriting plan
files. It does NOT. Every field the engine needs already exists in
the shipped Batch 1 plans, and in no other fighter's plans:

| Field | Meaning |
|---|---|
| `step.bank` | Bank the step was adjudicated in ('jin' / 'anna' / null / absent). Absent/null = "the bound bank". |
| `step.row` | Playable row, in the BOUND bank only. Non-null only on verified bound-bank steps. |
| `step.bank_verified_row` | Gate-verified row in `step.bank`, present ONLY on BANK-BLOCKED review steps whose bank differs from the bound bank. |
| `step.status` | 'verified' / 'review' / 'unmapped' (unchanged semantics for bound steps). |
| `step.bound_bank` | Bound bank recorded at adjudication. Informational only — the engine uses the live bound bank (`_t3.bank`), never this field, so a rebind cannot silently change playback. |
| `step.reasons` | A BANK-BLOCKED promotion requires a reason containing 'BANK-BLOCKED'. |

The engine reads that evidence; it does not rewrite torch.json.

## 3. Effective play (game/js/step-plan-bank.js, pure, no THREE)

`effectiveStepPlay(step, boundBank)` → `{ row, bank, via }` or null,
in order:

- **Path A — verified step:** status 'verified' + finite row. Plays
  from `step.bank` when that is a real bank name different from the
  bound bank (a mechanically promoted cross-bank step), else from
  the bound bank. For every step whose bank is null/absent or equals
  the bound bank, this IS the #1096 rule, unchanged.
- **Path B — BANK-BLOCKED promotion:** status 'review' + finite
  `bank_verified_row` + real `step.bank` ≠ bound bank + a
  BANK-BLOCKED reason. Plays that row from `step.bank`. This is what
  flips torch Batch 1 with no rewrite and no re-gate: the gates
  already passed in the step's own bank; the review status recorded
  only the engine limitation, not a gate failure.
- **Otherwise null:** the step plays NO bank row (UNMAPPED, never a
  donor / match / generic fallback — the step-plan branch returns
  before those tiers, exactly as in #1096).

`playableStepPlay` adds the fail-safe: the play bank's cached source
clips must contain `'row:' + row`. An override pointing at a bank
with no such row, at an unloaded bank, or at an unknown bank returns
null — UNMAPPED, never the bound bank's clip of the same number,
never a throw that breaks the fight. The engine must never substitute
bound-bank clips for the check.

`stepActionName(play, boundBank)`: bound-bank steps keep
`'row:<row>'` byte-identically. Override steps use
`'row:<bank>:<row>'` so a jin row 220 action can never collide with
(or overwrite) an anna row 220 action on the same fighter's mixer.

`stepPlanBanksFor(moveset, boundBank)`: distinct override banks a
moveset's plans need, excluding the bound bank.

## 4. fighter.js wiring (surgical; all other tiers untouched)

- **Import:** `loadT3Clips` (t3anims.js) + the four helpers from
  `./step-plan-bank.js`.
- **`_bindT3`:** resets `this._stepBankClips = {}` and preloads each
  override bank from the fighter's plans (fire-and-forget, errors
  swallowed). Until a bank is cached, its steps fail safe to
  UNMAPPED for that press and play once loaded. In practice the load
  starts at fighter creation, before round start, so first-press
  playback is expected — but the race is real and is in the
  play-verify checklist, not hidden.
- **`_resolveStepPlan`:** both branches (chain step, last step) now
  resolve through `playableStepPlay` with a play-bank clip check,
  and return `playBank` / `playRow` alongside `playName`. The
  `unmapped` list is steps with no effective play — byte-identical
  to the #1096 status-based list for every plan without overrides.
  The old bound-only formulas
  `(st.status === 'verified' && st.row != null) ? 'row:' + st.row`
  and the last-step equivalent are gone (asserted by test).
- **`_attackClipPlan` step branch:** the source clip and the hit
  window (`clipHitWindow`) are read from the PLAY bank, not the
  bound bank. A missing override clip logs an override-miss line
  and returns name null. The plan carries `stepBank` / `stepRow`.
- **`_attackClip`:** for a namespaced action, retargets the override
  bank's own `'row:<row>'` source clip, CLONES it, renames the clone
  to the namespaced action name (the retarget cache is never
  mutated), and caches the source clips in `_stepBankClips` for root
  motion. Bound steps use the exact #1096 retarget path.
- **`_rootMotionApply`:** reads root travel from the play bank's
  source clip (`_stepBankClips` or `getT3Clips`), never from the
  bound bank's row of the same number.
- **`_throwPairFor`:** the attempt row comes from `_atkPlan.stepRow`
  first, because `parseInt('jin:220')` is NaN. The old parse path is
  kept for non-step-plan attacks.

No other tier changes: own / notation / anim / donor / match /
generic resolution still reads bound-bank clips only, exactly as in
#1096. A single-bank fighter never reaches the override code: its
steps carry no bank and no `bank_verified_row`.

## 5. Promotion rule (exact — how torch's 22 steps become wired)

Once THIS engine PR and #1136 (torch Batch 1 plans) are BOTH on
main and deployed, torch's BANK-BLOCKED steps play automatically via
Path B — no further data change, no re-gate, no re-adjudication:

- 2,1 → [jin 220, jin 221] as actions `row:jin:220`, `row:jin:221`
- 2,1,2 → + jin 222; 2,1,2,2 → + jin 223
- 1,2-family step 2 → jin 249; 2,2 / 2,uf+1+2 step 1 → jin 220
- d+1+2-family → jin 92 / 93 / 183 (with their GATE-NOTEs intact)

Merge order between this PR and #1136 does not matter for
correctness: engine without plans is a no-op (no override steps
exist in pantera), and plans without engine keep the #1096 behavior
(BANK-BLOCKED steps UNMAPPED). The flip happens only when both are
live. This PR's base is the #1096 branch, NOT #1136, per the task —
so it must be rebased after #1096 lands (see §8) before it merges.

**Forward schema (optional, later lane, NOT required for the flip):**
a lane may mechanically promote a BANK-BLOCKED step by setting
`status='verified'` and `row=bank_verified_row` (bank kept). Path A
then plays the identical row from the identical bank under the
identical action name — playback is equivalent either way. No new
gate pass is ever needed for these steps; their evidence is already
in the file.

**What does NOT flip:** review steps without `bank_verified_row`
(the 3 anna review steps + all others), unmapped steps (65 planned),
1,2 step 1 (jin row 248, button 12 ≠ LP1 bits — still UNMAPPED, never
a multi-button clip played as a jab), and the TACKLE family (no plan,
CSV-only grapple label).

## 6. Regression proof — single-bank fighters unchanged

Workspace census over the 8 done fighters' Batch 1–4 plan files
(burger, demonio, diablo, kinpo, phantom, scimitar, skull, pantera
workspace files) + the pantera plans on the #1096 tree itself:

- 5,883 plan steps (batches 1–4) + 137 pantera tree steps.
- `bank_verified_row` non-null: 0. `bank` field non-empty: 0.
- Old-rule vs new-rule effective play: 0 differences.

In-repo, CI-runnable: the new test loads the real pantera.json from
the #1096 tree (60 plans, 137 steps) and asserts effective play ==
old-rule play for every step, plus synthetic bank-null/absent plans.
The other 7 fighters' plan files are NOT in this branch's tree (only
pantera's plans shipped on #1096), so their regression rests on the
census above + the construction argument (the override code triggers
only on fields their plans do not carry) — stated here, not faked as
a CI check.

## 7. Tests

Minimal-tree `node --test game/tests/torch-per-step-bank.test.mjs`:
**12 pass / 0 fail.** `node --check fighter.js` OK,
`node --check step-plan-bank.js` OK.

- (a) Torch 2,1 / 2,1,2 / 2,1,2,2 chains resolve to jin rows
  220/221/222/223 via Path B, action names `row:jin:<row>`.
- (b) Torch anna steps (355, 174, 32, …) resolve via the bound bank
  with unchanged names (`row:355`, …); their unmapped openers play
  nothing.
- (c) Synthetic mixed plan (anna verified step + jin BANK-BLOCKED
  step in one string) plays each step from its own bank.
- (d) Pantera real-file + synthetic single-bank regression (§6).
- (e) Fail-safe: override bank missing the row plays NOTHING even
  when the bound bank HAS that row number (anna row 220 exists in
  anna hit_frames — the trap case); unknown bank, unloaded bank,
  missing BANK-BLOCKED reason, bound-bank review step, non-integer
  row, verified-with-null-row all play nothing.
- Promotion-rule test: the mechanically promoted copy of 2,1
  (verified + row + bank jin) resolves identically via Path A.
- `stepPlanBanksFor`: torch fixture → ['jin']; pantera → [];
  no-plan moveset → [].
- fighter.js static guards: all wiring markers present; both old
  bound-only formulas absent; the step branch reads its source clip
  from the play bank.

Test fixture (`game/tests/torch-per-step-bank-fixture.json`) is TEST
DATA copied verbatim from the #1136 Batch 1 plans for 7 keys
(2,1; 2,1,2; 2,1,2,2; b+1+2,1; d/f+1+2,2; 1,2; u+1,1), with a
verbatim spot-check test. It is not a moveset file and never
replaces torch.json.

## 8. Merge interaction (stated, not attempted)

- #1096's merge onto current main must reconcile fighter.js with
  #1078's changes; that reconciliation belongs to #1096's merge,
  not this PR. This branch inherits it when #1096 merges — so this
  PR MUST be rebased (or 3-way-merged with `git_merge.py`, which
  refuses on conflict rather than clobbering) onto the post-#1096
  main before it merges. Its fighter.js hunks are confined to:
  imports, `_bindT3`, `_resolveStepPlan`, the `_attackClipPlan`
  step branch, `_attackClip`, `_rootMotionApply`, `_throwPairFor`.
- Per the revised merge order (2026-10-25): #1137 → #988 (only after
  its quarantine-data + anim_t3-only fix + field-level
  re-verification + CI green) → #1096 → fighter stacks (this PR).
  This PR waits in the stack; it does not merge on mergeable:true
  alone, and it merges nothing itself.
- Full 200-test suite comparison NOT run (no full current-main
  checkout on this box) — CI must cover before merge. No play
  verification claimed.

## 9. Play-verify checklist (parent browser delegation, after #1096 + this PR + #1136 merge + deploy + sync)

Phone portrait, human simulation. Torch vs any fighter.

1. 2,1 plays [jin 220, jin 221]; 2,1,2 adds jin 222; 2,1,2,2 adds
   jin 223 — the jin chain reads as the jin chain, NOT as anna
   rows 220/221/222/223 standing in. (This inverts the Batch 1
   checklist item 5: those strings must now PLAY, from jin.)
2. 1,2-family step 2 plays jin 249; step 1 still plays NO row
   (jin 248 button-12 clip must NOT play as an LP1 jab).
3. d+1+2-family steps play jin 92 / 93 / 183; no anna row of the
   same number stands in.
4. Anna families unchanged: b+1+2,1 [NO row, anna 355];
   d/f+1+2,2 [NO row, anna 174]; u+1,1 [NO row, anna 32]; etc.
5. Mixed strings: each step's bank matches its step (anna steps
   anna, jin steps jin) — never a whole string from one bank.
6. First-press race: if a jin step ever plays NO row on the very
   first press after round start but plays on the next press, the
   override bank was still loading — report it; it must not play a
   wrong-bank clip in that window.
7. No step plays a jin airborne/jump row for a ground step; no step
   plays anna row 220 or 216 as a stand-in for a jin row.
8. All other fighters (spot-check pantera): inputs, strings, and
   throws play exactly as before — no behavior change.
