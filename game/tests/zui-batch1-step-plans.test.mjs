/* Zui Batch 1 step plans (LP1/RP2-only strings, 2026-10-25) — data + engine-marker guard.
 * Docs: docs/movesets/ZUI-BATCH1-STEP-PLANS-2026-10-25.md.
 * Stack: this branch is stacked on #1096 (feat/batch1-step-plans-pantera-20261024,
 * the step-playback engine). It does NOT stack on the Pantera plan branches,
 * the burger plan branches, the demonio plan branches, the diablo plan
 * branches, the kinpo plan branches, the phantom plan branches, the scimitar
 * plan branches, the skull plan branches, or the torch plan branches:
 * zui.json plans do not conflict with any other fighter's plans.
 * It does NOT include #1097's Pantera Batch 1 follow-up fills (Pantera-specific,
 * and its row-49 SOFT fill is still unapproved); no SOFT fill is inherited here.
 * This PR does not touch `fighter.js`: #1096's merge onto post-#1078 main must
 * reconcile #1078's `fighter.js` changes with #1096's engine branch, and that
 * belongs to #1096's merge, not this PR.
 * SINGLE BANK (verified, not assumed): zui's T3 moves are jin only
 * (file-level t3_source jin, t3_bank moveset_jin.json, on BOTH #1096 and
 * main; per-move t3_source jin 152 / none 502; all 152 t3_row moves carry
 * t3_source jin). Zui has NO FIGHTER_BANK override in fighter.js #1096, so
 * the bound in-game bank is jin. There is NO bank-blocked category for zui
 * (torch dual-bank only): jin gate-verified steps wire directly.
 * GATE-ONLY batch: Job 2 zui entries 0, Job 3 zui entries 0 — Job 3 fills
 * 0 and Job 4 joins 0 by data absence, not by failure.
 * Jin-bank rules, per-bank evidence (freshly derived here): row 35 EXISTS
 * (starts-airborne, btn 1); row 220 EXISTS (standing RP2, btn 2); row 216
 * EXISTS (jump, btn 0); row 41 EXISTS (starts-airborne, btn 1).
 * Zui basics DIFFER from torch (verified here): LP1 move 1 (damage 7),
 * RP2 move 2 (damage 12), LK3 move 3 (damage 0, special), RK4 move 4
 * (damage 0, special) are T7-sourced with NO t3_row on either file —
 * zui's basics carry no T3 row at all.
 * Re-baseline #1096 vs main: moves + strings deep-equal; row-changed 0,
 * damage-only 0 — suspended 0. Gap-1 jin: hit_frames + skeleton IDENTICAL,
 * rows.pack ADDITIVE-ONLY (main adds 89/112/247/288/339/357; 0 changed,
 * 0 removed; affected fills 0).
 * SINGLE-BANK-FALLBACK (1 step, lane decision flagged for the coordinator):
 * f+2,1 step 2 (row 221) — bank resolved to jin from the file-level bank
 * because zui is verified single-bank; revertible mechanically.
 * Canonicalization is the CORRECTED rule: strip ONLY a trailing
 * ~t[378] source-variant suffix; input-~ is Tekken cancel notation, part of
 * the move. Zui Batch 1 contains 23 input-~ canonicals (own keys) and 19
 * ~t8.steve twin variants. No CSV-only canonicals in Batch 1 scope.
 * Rules asserted here (all data-level, no THREE needed):
 *   1. zui.json still has 654 moves / 87 strings entries (plans additive only).
 *   2. string_step_plans has exactly 194 keys (175 planned canonicals + 19 twins).
 *   3. Batch 1 verified steps always carry a row whose OWN-BANK (jin, the
 *      bound bank) hit_frames button equals the step bits and whose throw
 *      flag is 0; verified rows always exist in the jin hit_frames;
 *      review/unmapped steps carry row null. No Batch 1 step carries a soft
 *      flag (Batch 1 wires zero Job 3 fills — no zui Job 3 data exists —
 *      and zero SOFT fills). No Batch 1 step carries a bank_verified_row
 *      (no bank-blocked category for a single-bank fighter).
 *   4. d+1+2,2 flagship: verified-all, rows [92,93] (GATE-NOTE: standing
 *      rows for crouch-context steps, demonio Batch 1 precedent).
 *   5. f+2,1 flagship: partial, step 1 unmapped (no candidate), step 2
 *      VERIFIED jin row 221 (SINGLE-BANK-FALLBACK).
 *   6. f+2,1,2,2 flagship: partial, steps 1-2 unmapped (no candidate),
 *      step 3 VERIFIED jin row 222, step 4 VERIFIED jin row 223.
 *   7. d+1+2,1 flagship: partial, step 1 VERIFIED jin row 92 (GATE-NOTE),
 *      step 2 unmapped (jin row 177 button 12 != bits 1).
 *   8. f+2,1_r221: step 2 unmapped, candidate jin row 221, button 1 !=
 *      step bits 3 — the bits-3 reading comes from the _r221 row-suffix
 *      digits in the key, not from the LP1 input; documented, not fixed.
 *   9. Jin rows 35 (starts-airborne), 220 (standing RP2), 216 (jump,
 *      button 0) are never wired for any Batch 1 step.
 *  10. The verified-last-step Batch 1 keys are exactly the 6 listed below.
 *  11. fighter.js: the step-plan branch markers exist (static guard; the engine is
 *      inherited from #1096, not changed by this PR; behaviour is play-verified).
 * Run: node --test game/tests/zui-batch1-step-plans.test.mjs   (from repo root)
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..', '..');
const zui = JSON.parse(readFileSync(join(ROOT, 'game/assets/movesets/zui.json'), 'utf8'));
const fighterSrc = readFileSync(join(ROOT, 'game/js/fighter.js'), 'utf8');
const hfJin = JSON.parse(readFileSync(join(ROOT, 'game/assets/anim/t3/jin/hit_frames.json'), 'utf8')).rows;

const plans = zui.string_step_plans.plans;
const B1 = ["(1),(1),2", "(1),(1),d+1", "(1),(2),(1),2", "(1),(2),(1),d+2", "(1),(2),1", "(1),(2),1,2", "(1),(2),1,d+2", "(1),1", "(1),1,2", "(1),1,d+1", "(1),2", "(1),2,1", "(1),2,1,2", "(1),2,1,d+2", "(1),d+1", "(2),(1),2", "(2),1,2", "(D+2),(1),2", "(D+2),1", "(D+2),1,2", "(During Tackle) 1/2,1/2", "(During Tackle) 1/2,1/2,1/2", "(During Tackle) 1/2,1/2,1/2,1/2", "(b+1),(d+2),1", "(b+1),2", "(b+1),d+2", "(b+1),d+2,1", "(d/f+1),2", "(d/f+1),2~1", "(d/f+1),2~2", "(d/f+1),2~f+1+2", "(d/f+1),2~f+1+2_r56", "(f+1+2),2", "(f+2),1", "(f+2),1~2", "1,1", "1,1,2", "1,1,2~t8.steve", "1,1,d+1", "1,1,d+1~t8.steve", "1,1~t8.steve", "1,2", "1,2,1", "1,2,1,2", "1,2,1,2~t8.steve", "1,2,1,d+2", "1,2,1,d+2~t8.steve", "1,2,1~t8.steve", "1,2~t8.steve", "1,d+1", "1,d+1~t8.steve", "2,1", "2,1,2", "2,1,2~t8.steve", "2,2", "D+2,1", "D+2,1,2", "DCK 1+2,1,2,1,2,1,2,1,2,1", "DCK.1+2,1+2", "DCK.1+2,1+2,1+2", "DCK.1+2,1+2,1+2,1+2", "DRU (2),2", "DRU 1+2,1+2", "DRU 1+2,1+2,1+2", "DRU 2,2", "DRU u/b+1+2,1", "FLK (1),(1),(1),2", "FLK (1),(1),1", "FLK (1),(1),1,2", "FLK (1),1", "FLK (1),1,1", "FLK (1),1,1,2", "FLK (1),d+1", "FLK (1),f+1", "FLK 1,1", "FLK 1,1,1", "FLK 1,1,1,2", "FLK 1,d+1", "FLK 1,f+1", "FLK.1,1", "FLK.1,1,1", "FLK.1,1,1,2", "FLK.1,1,2", "FLK.1,1,d+1", "FLK.1,1,f+1", "FLK.1,2", "FLK.1,d+1", "FLK.1,f+1", "LWV (1),(f+1),1", "LWV (1),1", "LWV (1),f+1", "LWV (1),f+1,1", "LWV (2),1", "LWV 1,1", "LWV 1,f+1", "LWV 1,f+1,1", "LWV 2,1", "LWV.1,1", "LWV.1,2", "LWV.1,2~1", "LWV.1,f+1", "LWV.1,f+1,1", "LWV.2,1", "PAB (1),(2),1", "PAB (1),2", "PAB (1),2,1", "PAB (b+1),(1),(2),1", "PAB (b+1),(1),2", "PAB (b+1),(1),2,1", "PAB (b+1),1", "PAB (b+1),1,2", "PAB (b+1),1,2,1", "PAB (d/f+1),(1),(2),1", "PAB (d/f+1),(1),2", "PAB (d/f+1),(1),2,1", "PAB (d/f+1),1", "PAB (d/f+1),1,2", "PAB (d/f+1),1,2,1", "PAB (d/f+1),2", "PAB (f+2),1", "PAB 1,2", "PAB 1,2,1", "PAB b+1,1", "PAB b+1,1,2", "PAB b+1,1,2,1", "PAB d/f+1,1", "PAB d/f+1,1,2", "PAB d/f+1,1,2,1", "PAB d/f+1,2", "PAB f+2,1", "PAB.1,2", "PAB.1,2,1", "PAB.b+1,1", "PAB.b+1,1,2", "PAB.b+1,1,2,1", "PAB.d/f+1,1", "PAB.d/f+1,1,2", "PAB.d/f+1,1,2,1", "PAB.d/f+1,2", "PAB.d/f+1,2~1", "PAB.f+2,1", "RWV (1),2", "RWV 1,2", "RWV.1,2", "RWV.1,2~1", "WS (1),1", "WS (1),2", "WS 1,1", "WS 1,2", "WS.1,1", "WS.1,2", "WS.2,2", "b+1+2,H.1+2", "b+1,2", "b+1,2~1", "b+1,2~t8.steve", "b+1,d+2", "b+1,d+2,1", "b+1,d+2,1~t8.steve", "b+1,d+2~t8.steve", "d+1+2,1", "d+1+2,1,2", "d+1+2,2", "d+2,1", "d+2,1,2", "d+2~n~(1),2", "d+2~n~(1),f+2", "d+2~n~1,2", "d+2~n~1,f+2", "d/f+1,2", "d/f+1,2~1", "d/f+1,2~1~t8.steve", "d/f+1,2~2", "d/f+1,2~2~t8.steve", "d/f+1,2~f+1+2", "d/f+1,2~f+1+2,1", "d/f+1,2~f+1+2,1,1", "d/f+1,2~f+1+2,1,1,2", "d/f+1,2~f+1+2,1,1,2,1", "d/f+1,2~f+1+2,1,1,2,1,1,2,1,2", "d/f+1,2~f+1+2,1,1,2,1,1,2,1,b+2", "d/f+1,2~f+1+2~t8.steve", "d/f+1,2~t8.steve", "f+1+2,2", "f+1+2,2~t8.steve", "f+2,1", "f+2,1,2", "f+2,1,2,2", "f+2,1_r221", "f+2,1~2", "f+2,1~2~t8.steve", "f+2,1~t8.steve", "f+2,2", "f+2,2,1+2"];
const B1_VERIFIED_LAST = ["d+1+2,1,2", "d+1+2,2", "f+2,1", "f+2,1,2", "f+2,1,2,2", "f+2,1~t8.steve"];
const VERIFIED_BUTTONS = {"92": 3, "93": 2, "183": 2, "221": 1, "222": 2, "223": 2};

function stepBits(step) {
  const seg = step.split('.').pop();
  let b = 0;
  for (const c of seg) if ('1234'.includes(c)) b |= 1 << (Number(c) - 1);
  return b;
}

test('zui move/string counts unchanged by the additive plans block', () => {
  assert.equal(Object.keys(zui.moves).length, 654);
  assert.equal(zui.strings.length, 87);
  assert.equal(Object.keys(plans).length, 194);
});

test('Batch 1 keys are exactly the documented 194', () => {
  assert.equal(B1.length, 194);
  for (const key of B1) assert.ok(plans[key], `Batch 1 key ${key} missing`);
  const extra = Object.keys(plans).filter((k) => !B1.includes(k));
  assert.deepEqual(extra, []);
});

test('Batch 1 verified steps carry jin rows (button == step bits, throw 0, row exists in jin hit_frames); review/unmapped carry row null; no soft flags; no bank_verified_row anywhere', () => {
  for (const key of B1) {
    for (const s of plans[key].steps) {
      assert.ok(!('soft' in s) || s.soft !== true, `${key} step ${s.step} carries a soft flag`);
      assert.equal(s.bank_verified_row, null, `${key} step ${s.step} carries a bank_verified_row — zui has no bank-blocked category`);
      if (s.status === 'verified') {
        assert.notEqual(s.row, null, `${key} step ${s.step} verified but row null`);
        assert.equal(s.bank, 'jin', `${key} step ${s.step} verified on non-jin bank ${s.bank} — bound bank is jin`);
        assert.ok(hfJin[String(s.row)], `${key} step ${s.step} verified on row ${s.row} which does not exist in the jin hit_frames`);
        assert.equal(hfJin[String(s.row)][5], stepBits(s.step), `${key} step ${s.step} row ${s.row} button mismatch`);
        assert.equal(hfJin[String(s.row)][5], VERIFIED_BUTTONS[String(s.row)], `${key} step ${s.step} row ${s.row} button mismatch (map)`);
        assert.equal(hfJin[String(s.row)][4], 0, `${key} step ${s.step} row ${s.row} is a throw row`);
      } else {
        assert.equal(s.row, null, `${key} step ${s.step} ${s.status} must not carry a playable row`);
      }
    }
  }
});

test('jin rows 35 / 220 / 216 have their derived identities and are never wired', () => {
  assert.equal(hfJin['35'][5], 1, 'jin row 35 must be button 1');
  assert.equal(hfJin['220'][5], 2, 'jin row 220 must be button 2');
  assert.equal(hfJin['216'][5], 0, 'jin row 216 must be button 0');
  const wired = new Set();
  for (const key of B1) for (const s of plans[key].steps) if (s.row != null) wired.add(s.row);
  assert.deepEqual([...wired].sort((a, b) => a - b), [92, 93, 183, 221, 222, 223]);
  for (const r of [35, 220, 216]) assert.ok(!wired.has(r), `jin row ${r} must never be wired in Batch 1`);
});

test('d+1+2,2 flagship: verified-all, rows [92,93], GATE-NOTE on both steps', () => {
  const p = plans['d+1+2,2'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [92, 93]);
  assert.deepEqual(p.steps.map((s) => s.status), ['verified', 'verified']);
  assert.equal(p.string_status, 'verified-all');
  for (const s of p.steps) {
    assert.equal(s.bank, 'jin');
    assert.ok(s.reasons.join(' ').includes('GATE-NOTE'), 'crouch-context step on a standing row must carry the GATE-NOTE');
  }
});

test('f+2,1 flagship: partial, step 1 unmapped (no candidate), step 2 VERIFIED jin row 221 (SINGLE-BANK-FALLBACK)', () => {
  const p = plans['f+2,1'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [null, 221]);
  assert.deepEqual(p.steps.map((s) => s.status), ['unmapped', 'verified']);
  assert.equal(p.string_status, 'partial');
  assert.equal(p.steps[0].candidate_row, null);
  assert.equal(p.steps[1].bank, 'jin');
  assert.ok(p.steps[1].reasons.join(' ').includes('SINGLE-BANK-FALLBACK'), 'step 2 must record the SINGLE-BANK-FALLBACK');
});

test('f+2,1,2,2 flagship: partial, steps 1-2 unmapped, step 3 VERIFIED 222, step 4 VERIFIED 223', () => {
  const p = plans['f+2,1,2,2'];
  assert.equal(p.steps.length, 4);
  assert.deepEqual(p.steps.map((s) => s.row), [null, null, 222, 223]);
  assert.deepEqual(p.steps.map((s) => s.status), ['unmapped', 'unmapped', 'verified', 'verified']);
  assert.equal(p.string_status, 'partial');
});

test('d+1+2,1 flagship: partial, step 1 VERIFIED jin row 92 (GATE-NOTE), step 2 unmapped (jin row 177 button 12 != bits 1)', () => {
  const p = plans['d+1+2,1'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [92, null]);
  assert.deepEqual(p.steps.map((s) => s.status), ['verified', 'unmapped']);
  assert.equal(p.string_status, 'partial');
  assert.equal(p.steps[1].candidate_row, 177);
  assert.ok(p.steps[1].reasons.join(' ').includes('button 12'), 'step 2 must record the button-12 rejection');
  assert.ok(p.steps[0].reasons.join(' ').includes('GATE-NOTE'), 'step 1 standing row for a crouch step must carry the GATE-NOTE');
});

test('f+2,1_r221: step 2 unmapped, candidate jin row 221, button 1 != step bits 3 (row-suffix digits, documented)', () => {
  const p = plans['f+2,1_r221'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [null, null]);
  assert.deepEqual(p.steps.map((s) => s.status), ['unmapped', 'unmapped']);
  assert.equal(p.steps[1].candidate_row, 221);
  assert.ok(p.steps[1].reasons.join(' ').includes('button 1'), 'step 2 must record the button-1 rejection');
});

test('verified-last-step Batch 1 keys are exactly the documented 6', () => {
  assert.equal(B1_VERIFIED_LAST.length, 6);
  for (const key of B1_VERIFIED_LAST) assert.equal(plans[key].last_step_status, 'verified', `${key} last step not verified`);
  const others = B1.filter((k) => !B1_VERIFIED_LAST.includes(k));
  for (const key of others) assert.notEqual(plans[key].last_step_status, 'verified', `${key} last step unexpectedly verified`);
});

test('fighter.js: the step-plan branch markers exist', () => {
  assert.ok(fighterSrc.includes('_attackClipPlan'), 'fighter.js missing _attackClipPlan');
  assert.ok(fighterSrc.includes('string_step_plans') || fighterSrc.includes('_stepChain'), 'fighter.js missing step-plan markers');
});
