/* v-system.test.mjs — V-System rules (owner-approved 2026-10-22).
 *
 * Covers the pure rules in game/js/v-system.js: V-Skill dispatch,
 * V-Trigger costs/enhancement, V-Reversal template, V-Shift tap timing,
 * and the V-Skill catalog. Wiring (fighter.js/game.js) is exercised
 * through these same rules; DOM/THREE paths are not unit-tested here.
 *
 * Run: node --test game/tests/v-system.test.mjs   (from repo root)
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
const vs = await import(join(here, '..', 'js', 'v-system.js'));

test('vskillDispatch: blockstun + 50 souls -> vreversal', () => {
  assert.equal(vs.vskillDispatch({ state: 'block', stun: 0.2, meter: 60 }), 'vreversal');
});

test('vskillDispatch: blockstun but poor -> vskill (tryVSkill will fail gracefully)', () => {
  assert.equal(vs.vskillDispatch({ state: 'block', stun: 0.2, meter: 10 }), 'vskill');
});

test('vskillDispatch: blocking without stun is not a reversal', () => {
  assert.equal(vs.vskillDispatch({ state: 'block', stun: 0, meter: 100 }), 'vtrigger');
});

test('vskillDispatch: full meter in neutral -> vtrigger', () => {
  assert.equal(vs.vskillDispatch({ state: 'idle', stun: 0, meter: 100 }), 'vtrigger');
});

test('vskillDispatch: neutral, partial meter -> vskill', () => {
  assert.equal(vs.vskillDispatch({ state: 'walk', stun: 0, meter: 40 }), 'vskill');
});

test('vskillDispatch: vreversal wins over vtrigger while pressured', () => {
  // Being mauled at full meter: the defensive answer comes first.
  assert.equal(vs.vskillDispatch({ state: 'block', stun: 0.3, meter: 100 }), 'vreversal');
});

test('V tuning: trigger costs the full bar, reversal half', () => {
  assert.equal(vs.V.TRIGGER_COST, 100);
  assert.equal(vs.V.REVERSAL_COST, 50);
  assert.ok(vs.V.TRIGGER_DURATION > 0 && vs.V.TRIGGER_DMG_MULT > 1);
});

test('vskillFor: every fighter gets a skill, default when unlisted', () => {
  const d = vs.vskillFor('some-unknown-fighter');
  assert.equal(d.kind, 'strike');
  assert.ok(d.damage > 0 && d.startup > 0 && d.recovery > 0);
  assert.match(d.name, /name TBD/); // placeholder flagged, per owner directive
});

test('vskillFor: per-character kits differ (identity, not wallpaper)', () => {
  const pantera = vs.vskillFor('pantera');
  const ryusan = vs.vskillFor('ryusan');
  const phantom = vs.vskillFor('phantom');
  assert.equal(pantera.armor, true); // grappler's armored way in
  assert.ok(ryusan.startup < pantera.startup); // fastest V-Skill
  assert.equal(phantom.kind, 'parry'); // swordsman's parry, not a strike
  assert.equal(phantom.noHitbox, true);
  for (const id of ['pantera', 'dio', 'ryusan', 'phantom']) {
    assert.match(vs.vskillFor(id).name, /name TBD/, `${id} name flagged TBD`);
  }
});

test('vtriggerEnhance: EX skill hits harder and gains armor', () => {
  const base = vs.vskillFor('dio');
  const ex = vs.vtriggerEnhance(base);
  assert.ok(ex.damage > base.damage);
  assert.ok(ex.knock > base.knock);
  assert.equal(ex.armor, true);
  assert.match(ex.name, /name TBD/);
  // base untouched (no mutation of the catalog)
  assert.equal(base.armor, undefined);
});

test('vreversalMove: a real guard-cancel counter template', () => {
  const m = vs.vreversalMove();
  assert.ok(m.damage > 0 && m.knock >= 6); // knocks them off you
  assert.equal(m.isGrab, false);
  assert.equal(m.unblockable, false);
  assert.match(m.name, /name TBD/);
});

test('vshiftTap: double-tap block window', () => {
  const now = 10000;
  assert.equal(vs.vshiftTap(null, now), false); // never released: no tap
  assert.equal(vs.vshiftTap(now - 100, now), true); // quick re-tap: SHIFT
  assert.equal(vs.vshiftTap(now - vs.V.SHIFT_TAP_MS, now), true); // boundary in
  assert.equal(vs.vshiftTap(now - vs.V.SHIFT_TAP_MS - 1, now), false); // too slow
});

test('vshiftVelocity: backwards, covers SHIFT_BACK_DIST in SHIFT_DURATION', () => {
  const v = vs.vshiftVelocity(1);
  assert.ok(v < 0); // away from the opponent when facing +x
  assert.ok(Math.abs(Math.abs(v) * vs.V.SHIFT_DURATION - vs.V.SHIFT_BACK_DIST) < 1e-9);
  assert.equal(vs.vshiftVelocity(-1), -v);
});

test('V-Shift Break: window + multiplier sane', () => {
  assert.ok(vs.V.BREAK_WINDOW > 0.5 && vs.V.BREAK_DMG_MULT > 1);
  assert.ok(vs.V.SLOWMO_SCALE < 1 && vs.V.SLOWMO_DURATION > 0);
});

test('V-Skill parry: window + rewards sane', () => {
  assert.ok(vs.V.PARRY_WINDOW > 0.1 && vs.V.PARRY_WINDOW < 0.4);
  assert.ok(vs.V.PARRY_SOUL_GAIN > vs.V.SKILL_SOUL_ON_USE);
});
