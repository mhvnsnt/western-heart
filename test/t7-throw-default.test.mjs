// Pantera T7 throw clips (Lane 5, 2026-11-20) — live default OFF since the
// 2026-11-20 owner verdict (Lane C, T7-fix): the real T7 pair is broken vs the
// T3 pair (thrower barely twists, victim carries the spin), so the T3 pair
// (slots 2795/2797 + victims 3018/3051) is the live default again. The T7
// module below still resolves + loads the pair — only the live default
// changed, gated by T7_THROW_DEFAULT_ENABLED = false in fighter.js.
// Node only: no browser, no THREE, no model proof. Run: node --test test/t7-throw-default.test.mjs
// Proves the selection contract fighter.js wires in: for Pantera 1+3 / 2+4 the
// T7 pair resolves (front: common_709 + rotsm_574 / rotsm_534 + rotsm_578),
// and when T7 loading fails the T3 pair stands as the working fallback —
// real T3 motion, never generic, never invented. The live bind itself (fighter.js _throwPairFor /
// _bindThrowPair) cannot run in node (it imports THREE + the game), so the
// seam it calls is tested here — resolveT7ThrowPair, t7SituationForQuadrant,
// loadT7ThrowPair, getT7ThrowClipRecord — plus a guard that the call-site
// still exists in fighter.js. The retarget step (t7ThrowClipRetargetSync)
// is the same jsonToClip + retargetT3Clips as Lane 3's async twin, which the
// game already ships.
// ORDER MATTERS: node:test runs these in declaration order and the loader
// caches per key, so the success test runs before the failure test (the
// failure test uses back/air keys the success test never loads).
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  selectThrow, resolveThrowClips, throwBreaks, throwDamageTimeSec,
  throwPairDurationSec, attemptRowForInput,
} from '../game/js/t3-throw.js';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const R = JSON.parse(readFileSync(join(ROOT, 'game/assets/anim/t3/reactions.json'), 'utf8'));
const KING = 'king_on_pantera_leoman';
const JIN = 'jin';
const SCALE = 0.000829923; // King pack anchor_mm_to_rig_m (reactions.pack.json)
const M = await import(join(ROOT, 'game/js/t7-throw-clips.js'));
const readJson = (p) => JSON.parse(readFileSync(p, 'utf8'));
const stubFetch = async (path) => ({ ok: true, json: async () => readJson(join(ROOT, 'game', path)) });
const failFetch = async () => ({ ok: false, json: async () => null });

// The T3 fallback pair, from the file's own tables (same values
// test/t3-throw.test.mjs asserts): 1+3 -> slot 2795 / victim 3018,
// 2+4 -> slot 2797 / victim 3051. This is what plays when T7 fails.
function t3FrontPair(input) {
  const row = attemptRowForInput(R, KING, input);
  const sel = selectThrow(R, KING, row, { posture: 'standing', quadrant: 0, distanceM: 1.0, anchorScale: SCALE });
  return { sel, clips: resolveThrowClips(R, sel.throw, KING, JIN) };
}

test('T3 fallback baseline: 1+3 -> slot 2795 / victim 3018, 2+4 -> slot 2797 / victim 3051', () => {
  const a = t3FrontPair('1+3');
  assert.equal(a.sel.throw.slot, 2795);
  assert.equal(a.sel.throw.victim_slot, 3018);
  assert.equal(a.clips.throwerSlot, 2795);
  assert.equal(a.clips.victimSlot, 3018);
  assert.deepEqual(a.sel.throw.damage_frames, [61]);
  assert.equal(throwDamageTimeSec(a.sel.throw), 61 / 60);
  assert.equal(throwPairDurationSec(a.sel.throw), 131 / 60);
  assert.deepEqual(throwBreaks(a.sel.throw), [{ input: '1', label: 'LP1', windowSec: [1 / 60, 15 / 60], escapeSlot: 2898 }]);
  const b = t3FrontPair('2+4');
  assert.equal(b.sel.throw.slot, 2797);
  assert.equal(b.sel.throw.victim_slot, 3051);
  assert.equal(b.clips.throwerSlot, 2797);
  assert.equal(b.clips.victimSlot, 3051);
});

test('quadrant map: front/back resolve, side quadrants keep T3 (left/right unproven)', () => {
  assert.equal(M.t7SituationForQuadrant(0), 'front');
  assert.equal(M.t7SituationForQuadrant(2), 'back');
  assert.equal(M.t7SituationForQuadrant(1), null);
  assert.equal(M.t7SituationForQuadrant(3), null);
  assert.equal(M.t7SituationForQuadrant(null), null);
  assert.equal(M.t7SituationForQuadrant(4), null);
  assert.equal(M.t7SituationForQuadrant(-1), null);
});

test('default selection: T7 pair resolves for 1+3/2+4 front and back', () => {
  const f13 = M.resolveT7ThrowPair('1+3', M.t7SituationForQuadrant(0));
  assert.equal(f13.thrower.key, 'common_709');
  assert.equal(f13.victim.key, 'rotsm_574');
  assert.equal(f13.thrower.frames, 40);
  assert.equal(f13.victim.frames, 130);
  const f24 = M.resolveT7ThrowPair('2+4', M.t7SituationForQuadrant(0));
  assert.equal(f24.thrower.key, 'rotsm_534');
  assert.equal(f24.victim.key, 'rotsm_578');
  assert.equal(f24.thrower.frames, 40);
  assert.equal(f24.victim.frames, 138);
  assert.equal(M.resolveT7ThrowPair('1+3', M.t7SituationForQuadrant(2)).victim.key, 'rotsm_592');
  assert.equal(M.resolveT7ThrowPair('2+4', M.t7SituationForQuadrant(2)).victim.key, 'rotsm_594');
  // Side quadrants map to null, so no T7 pair is ever resolved for them.
  assert.equal(M.t7SituationForQuadrant(1), null);
  assert.equal(M.t7SituationForQuadrant(3), null);
});

test('sync record cache: empty before any load (bind keeps T3 until preload lands)', () => {
  for (const k of ['common_709', 'rotsm_534', 'rotsm_574', 'rotsm_578']) {
    assert.equal(M.getT7ThrowClipRecord(k), null);
  }
});

test('loader success (default path): both front pairs load from the real files; sync cache feeds the bind', async () => {
  const p13 = await M.loadT7ThrowPair('1+3', 'front', stubFetch);
  assert.ok(p13);
  assert.equal(p13.thrower.key, 'common_709');
  assert.equal(p13.victim.key, 'rotsm_574');
  assert.equal(p13.throwerRecord.root_t.length, 40);
  assert.equal(p13.victimRecord.root_t.length, 130);
  assert.ok(M.validateT7ThrowClip('common_709', p13.throwerRecord).ok);
  assert.ok(M.validateT7ThrowClip('rotsm_574', p13.victimRecord).ok);
  const p24 = await M.loadT7ThrowPair('2+4', 'front', stubFetch);
  assert.ok(p24);
  assert.equal(p24.thrower.key, 'rotsm_534');
  assert.equal(p24.victim.key, 'rotsm_578');
  assert.equal(p24.throwerRecord.root_t.length, 40);
  assert.equal(p24.victimRecord.root_t.length, 138);
  // The sync accessor the bind reads returns the same records.
  assert.equal(M.getT7ThrowClipRecord('common_709').root_t.length, 40);
  assert.equal(M.getT7ThrowClipRecord('rotsm_574').root_t.length, 130);
  assert.equal(M.getT7ThrowClipRecord('rotsm_534').root_t.length, 40);
  assert.equal(M.getT7ThrowClipRecord('rotsm_578').root_t.length, 138);
});

test('loader failure: T7 unavailable -> null, sync cache stays empty, T3 pair still stands', async () => {
  // Back/air keys were never loaded above, so the failing fetch is really
  // exercised here — not the cache. Either clip failing nulls the pair.
  assert.equal(await M.loadT7ThrowPair('1+3', 'back', failFetch), null);
  assert.equal(await M.loadT7ThrowPair('2+4', 'air', failFetch), null);
  assert.equal(await M.loadT7ThrowClip('rotsm_590', failFetch), null);
  assert.equal(M.getT7ThrowClipRecord('rotsm_592'), null);
  assert.equal(M.getT7ThrowClipRecord('rotsm_716'), null);
  assert.equal(M.getT7ThrowClipRecord('rotsm_590'), null);
  // The fallback is the real T3 pair, unchanged by the T7 failure.
  assert.equal(t3FrontPair('1+3').sel.throw.slot, 2795);
  assert.equal(t3FrontPair('1+3').sel.throw.victim_slot, 3018);
  assert.equal(t3FrontPair('2+4').sel.throw.slot, 2797);
  assert.equal(t3FrontPair('2+4').sel.throw.victim_slot, 3051);
});

test('wiring presence: fighter.js calls the T7 default path (guard against the call-site being dropped)', () => {
  const src = readFileSync(join(ROOT, 'game/js/fighter.js'), 'utf8');
  for (const marker of [
    "from './t7-throw-clips.js'",
    'resolveT7ThrowPair',
    't7SituationForQuadrant(quadrant)',
    'clips, t7,',
    '_t7ThrowActions',
    't7ThrowClipRetargetSync',
    'ensureT7ThrowSkeleton',
    'pair.t7Active = true',
    "loadT7ThrowPair(input, 'front')",
  ]) assert.ok(src.includes(marker), `fighter.js missing: ${marker}`);
  // The T3 bind still runs first: the T7 swap sits after the DW block,
  // and the fallback is the T3 actions when the swap does not run.
  const dwAt = src.indexOf('pair.throwerAction = dwName');
  const t7At = src.indexOf('pair.t7Active = true');
  assert.ok(dwAt > 0 && t7At > dwAt, 'T7 swap must follow the T3/DW bind');
  const bindAt = src.indexOf('_bindThrowPair(pair, victim)');
  assert.ok(bindAt > 0 && bindAt < t7At, 'T7 swap must be inside _bindThrowPair');
});

test('live default OFF (owner verdict 2026-11-20): fighter.js gates the T7 resolution — T3 pair stands', () => {
  const src = readFileSync(join(ROOT, 'game/js/fighter.js'), 'utf8');
  assert.ok(src.includes('const T7_THROW_DEFAULT_ENABLED = false'), 'T7 default gate must be off');
  assert.ok(src.includes('T7_THROW_DEFAULT_ENABLED && (this.attackName'), 'T7 resolution must be gated on the flag');
  // The T7 pair still resolves in the module (above) — only the live default changed.
  assert.equal(t3FrontPair('1+3').sel.throw.slot, 2795);
  assert.equal(t3FrontPair('2+4').sel.throw.slot, 2797);
});
