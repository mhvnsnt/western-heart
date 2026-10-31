/* step-plan-bank.js — per-step-bank resolution for Batch 1 step plans.
 *
 * Pure JS, no THREE dependency, so CI can test it in node (same pattern
 * as anim-gate.js). fighter.js imports it for _resolveStepPlan /
 * _attackClipPlan / _attackClip; nothing else in the game needs it.
 *
 * PROBLEM (torch, 2026-10-25): a fighter's bound in-game bank
 * (fighter.js FIGHTER_BANK, e.g. torch -> anna) is the bank _bindT3
 * loads, and the #1096 step-plan branch resolved every step's row
 * against that bound bank ONLY. Torch is dual-bank: its T3 moves carry
 * t3_source jin (145) and anna (224), and its Batch 1 plans adjudicate
 * each step against ITS OWN move's bank. A jin-bank gate-verified step
 * therefore could not wire: writing it as verified row N would have
 * played anna row N — a wrong-bank clip. Batch 1 recorded those steps
 * as review, row null, bank_verified_row preserved, with a
 * BANK-BLOCKED reason. This module is the engine side of the fix: it
 * resolves a step's clip from the step's own bank, never from the
 * bound bank by default.
 *
 * SCHEMA (no plan-file change — these fields already exist in the
 * shipped torch Batch 1 plans, and in no other fighter's plans):
 *   step.bank               bank the step was adjudicated in
 *                           ('jin' | 'anna' | null | absent). Absent /
 *                           null means "the bound bank" (every
 *                           single-bank fighter's plans: pantera,
 *                           burger, demonio, diablo, kinpo, phantom,
 *                           scimitar, skull carry no bank field at all).
 *   step.row                playable row, in the BOUND bank only.
 *                           Non-null only on verified steps whose
 *                           bank is the bound bank (or null/absent).
 *   step.bank_verified_row  gate-verified row in step.bank, present
 *                           ONLY on BANK-BLOCKED review steps whose
 *                           bank differs from the bound bank.
 *   step.status             'verified' | 'review' | 'unmapped'.
 *   step.bound_bank         bound bank recorded at adjudication
 *                           (informational; the engine uses the live
 *                           bound bank from _t3.bank, never this field,
 *                           so a rebind cannot silently change playback).
 *   step.reasons            free text; a BANK-BLOCKED promotion
 *                           requires a reason containing 'BANK-BLOCKED'.
 *
 * EFFECTIVE PLAY (effectiveStepPlay), in order:
 *   Path A — verified step: status 'verified' and a finite row.
 *     The row plays from step.bank when step.bank is a real bank
 *     name different from the bound bank (a mechanically promoted
 *     cross-bank step: status flipped to verified, row set from
 *     bank_verified_row, bank kept — no re-gate), else from the
 *     bound bank. This is the forward schema; it is also exactly
 *     the #1096 rule for every step whose bank is null/absent or
 *     equals the bound bank.
 *   Path B — BANK-BLOCKED promotion: status 'review', a finite
 *     bank_verified_row, a real step.bank different from the bound
 *     bank, and a BANK-BLOCKED reason. The row plays from step.bank.
 *     This is what flips torch Batch 1's 22 canonical BANK-BLOCKED
 *     step instances (34 plan-key instances incl. twins, 8 distinct
 *     prefix/row pairs) with NO plan rewrite and NO re-gate: the
 *     gates already passed in the step's own bank, and the review
 *     status recorded only the engine limitation, not a gate failure.
 *   Otherwise: null — the step plays NO bank row (UNMAPPED, never a
 *     donor / match / generic fallback; the step-plan branch returns
 *     before those tiers, exactly as in #1096).
 *
 * FAIL-SAFE (playableStepPlay): effective play PLUS a clip-existence
 * check in the play bank's cached clips. An override pointing at a
 * bank with no such row, at an unloaded bank, or at an unknown bank
 * returns null — UNMAPPED, never a bound-bank clip of the same
 * number, never a throw that breaks the fight. The engine must pass
 * hasClip = (bank, row) => the bank's source clips contain
 * 'row:' + row; it must never substitute the bound bank's clips.
 *
 * ACTION NAMES (stepActionName): bound-bank steps keep the #1096
 * name 'row:<row>' byte-identically. Override steps use the
 * namespaced name 'row:<bank>:<row>' so a jin row 220 action can
 * never collide with (or overwrite) an anna row 220 action on the
 * same fighter's mixer. fighter.js retargets the namespaced action
 * from the override bank's source clips and clones the clip before
 * renaming, so the retarget cache is never mutated.
 *
 * Buttons: LP1/RP2/LK3/RK4. Tekken names here are technical
 * references only, never canon.
 */

/** The bank a step was adjudicated in, or null for "the bound bank". */
export function stepBankOf(step) {
  if (!step || typeof step !== 'object') return null;
  return (typeof step.bank === 'string' && step.bank.length > 0) ? step.bank : null;
}

function finiteRow(v) {
  return (typeof v === 'number' && Number.isFinite(v) && Number.isInteger(v) && v >= 0) ? v : null;
}

function isBankBlocked(step) {
  if (!step || !Array.isArray(step.reasons)) return false;
  return step.reasons.some((r) => typeof r === 'string' && r.includes('BANK-BLOCKED'));
}

/**
 * The step's playable clip, or null. Pure: no clip-existence check
 * here — use playableStepPlay for the engine path, which adds it.
 * Returns { row, bank, via } where via is 'verified' (bound bank),
 * 'verified-bank' (verified step with its own bank), or
 * 'bank-blocked' (review step promoted from bank_verified_row).
 */
export function effectiveStepPlay(step, boundBank) {
  if (!step || typeof step !== 'object') return null;
  const bank = stepBankOf(step);
  // Path A — verified step.
  const row = finiteRow(step.row);
  if (step.status === 'verified' && row != null) {
    if (bank && bank !== boundBank) return { row, bank, via: 'verified-bank' };
    return { row, bank: boundBank, via: 'verified' };
  }
  // Path B — BANK-BLOCKED promotion (torch Batch 1 evidence, as shipped).
  const bvr = finiteRow(step.bank_verified_row);
  if (step.status === 'review' && bvr != null && bank && bank !== boundBank && isBankBlocked(step)) {
    return { row: bvr, bank, via: 'bank-blocked' };
  }
  return null;
}

/** #1096 rule, for regression comparison: verified + row, bound bank only. */
export function oldRulePlay(step, boundBank) {
  if (!step || typeof step !== 'object') return null;
  const row = finiteRow(step.row);
  if (step.status === 'verified' && row != null) return { row, bank: boundBank, via: 'verified' };
  return null;
}

/**
 * Effective play gated on clip existence in the PLAY bank.
 * hasClip(bank, row) must answer from that bank's own cached source
 * clips — never from the bound bank's clips. Returns the play or null.
 */
export function playableStepPlay(step, boundBank, hasClip) {
  const play = effectiveStepPlay(step, boundBank);
  if (!play) return null;
  if (typeof hasClip !== 'function') return play;
  return hasClip(play.bank, play.row) ? play : null;
}

/**
 * Mixer action name for a play. Bound-bank steps keep 'row:<row>'
 * exactly as in #1096; override steps are namespaced 'row:<bank>:<row>'.
 */
export function stepActionName(play, boundBank) {
  if (!play || play.row == null) return null;
  if (play.bank && play.bank !== boundBank) return `row:${play.bank}:${play.row}`;
  return `row:${play.row}`;
}

/**
 * Distinct override banks a moveset's step plans need, excluding the
 * bound bank. fighter.js _bindT3 preloads these (fire-and-forget) so
 * an override step's clips are cached by first use; until they are,
 * playableStepPlay fails safe to UNMAPPED. Returns [] for movesets
 * without plans, and never includes the bound bank itself.
 */
export function stepPlanBanksFor(moveset, boundBank) {
  const out = [];
  try {
    const plans = moveset && moveset.string_step_plans && moveset.string_step_plans.plans;
    if (!plans || typeof plans !== 'object') return out;
    for (const plan of Object.values(plans)) {
      if (!plan || !Array.isArray(plan.steps)) continue;
      for (const step of plan.steps) {
        const bank = stepBankOf(step);
        if (bank && bank !== boundBank && !out.includes(bank)) out.push(bank);
      }
    }
  } catch (e) { /* a malformed plans block preloads nothing, never throws */ }
  return out;
}
