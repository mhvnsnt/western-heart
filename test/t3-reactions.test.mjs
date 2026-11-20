// T3 hit reactions + throws (lane E, 2026-10-24). Node, no browser. Run: node --test test/t3-reactions.test.mjs
// Data: game/assets/anim/t3/reactions.json (tools/anim/t3_reaction_tables.py) and every
// game/assets/anim/t3/<bank>/reactions.pack.json (tools/anim/t3_reaction_bake.py). Contract: docs/anim/T3-REACTIONS.md.
// Checks: every slot a reaction record, throw, air kind, KO or continuation can start resolves -- the way the game
// resolves it (defender's bank first, else the attacker's / thrower's, DivmotMergeSharedSlots) -- to a baked clip
// or to a listed-missing reason; every clip has the 22 WH-Canonical bones and finite values.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const T3 = join(ROOT, 'game/assets/anim/t3');
const R = JSON.parse(readFileSync(join(T3, 'reactions.json'), 'utf8'));
const DIRS = Object.keys(R.banks);
const CANON22 = ['Root', 'Hips', 'Spine', 'Chest', 'Neck', 'Head', 'LeftShoulder', 'LeftArm', 'LeftForeArm', 'LeftHand',
  'RightShoulder', 'RightArm', 'RightForeArm', 'RightHand', 'LeftUpLeg', 'LeftLeg', 'LeftFoot', 'LeftToeBase',
  'RightUpLeg', 'RightLeg', 'RightFoot', 'RightToeBase'];
const hex = (s) => '0x' + (s & 0xffff).toString(16);
const PACK = {};
for (const d of DIRS) {
  const p = join(T3, d, 'reactions.pack.json');
  PACK[d] = existsSync(p) ? JSON.parse(readFileSync(p, 'utf8')) : null;
}
const i16 = (b64) => { const b = Buffer.from(b64, 'base64'); const a = new Int16Array(b.length >> 1); for (let i = 0; i < a.length; i++) a[i] = b.readInt16LE(2 * i); return a; };

// The game's slot lookup for a fighter using bank V whose opponent uses bank A (MoveLookup after the merge).
function resolve(V, A, slot) {
  const k = hex(slot);
  for (const d of [V, A]) {
    if (R.banks[d].slots[k]) {
      const pk = PACK[d];
      if (pk && pk.rows[k]) return { dir: d, clip: pk.rows[k] };
      if (pk && pk.missing[k]) return { dir: d, missing: pk.missing[k] };
      return { dir: d, unaccounted: true };
    }
  }
  return null;
}

test('reactions.json: decoded EXE tables verified', () => {
  assert.equal(R.format, 'wh-t3-reactions/1');
  assert.ok(R.verification.length >= 8 && R.verification.every((c) => c.pass), JSON.stringify(R.verification.filter((c) => !c.pass)));
  assert.equal(R.records.length, 633);
  assert.ok(R.records.every((r) => r.length === 21));
  assert.equal(R.record_fields.length, 21);
  assert.deepEqual(R.air_kinds, [[440, 0xd56], [550, 0xd61], [204, 0xd62], [436, 0xd63], [436, 0xd64], [1357, 0xd57]]);
  assert.ok(R.throw_victim_slots.length >= 397);
  assert.equal(DIRS.length, 22);
});

test('every bank has a reactions pack; every clip has 22 bones and finite values', () => {
  let clips = 0;
  for (const d of DIRS) {
    const pk = PACK[d];
    assert.ok(pk, `${d}: reactions.pack.json missing`);
    assert.equal(pk.format, 'wh-anim-pack/1', d);
    assert.deepEqual(pk.bones, CANON22, `${d}: bones`);
    assert.ok(Number.isFinite(pk.fps) && pk.fps > 0, `${d}: fps`);
    for (const [k, rec] of Object.entries(pk.rows)) {
      const n = rec.n;
      assert.ok(Number.isInteger(n) && n > 0, `${d} ${k}: n`);
      assert.equal(hex(rec.slot), k, `${d} ${k}: key = slot`);
      const q = i16(rec.q);
      assert.equal(q.length, n * 22 * 4, `${d} ${k}: q is [n][22][4]`);
      for (let i = 0; i < q.length; i += 4) {
        const x = q[i] / 32767, y = q[i + 1] / 32767, z = q[i + 2] / 32767, w = q[i + 3] / 32767;
        const len = Math.hypot(x, y, z, w);
        assert.ok(Number.isFinite(len) && Math.abs(len - 1) < 0.01, `${d} ${k}: quaternion ${i >> 2} norm ${len}`);
      }
      for (const t of ['rx', 'ry', 'rz', 'ax', 'ay', 'az']) {
        const a = i16(rec[t]);
        assert.equal(a.length, n, `${d} ${k}: ${t} length`);
      }
      assert.ok(rec.yaw0 === null || Number.isFinite(rec.yaw0), `${d} ${k}: yaw0`);
      clips++;
    }
  }
  assert.ok(clips > 1000, `clips baked: ${clips}`);
});

test('every planned slot of a bank is baked or listed missing', () => {
  for (const d of DIRS) {
    const pk = PACK[d];
    for (const k of Object.keys(R.banks[d].slots)) {
      assert.ok(pk.rows[k] || pk.missing[k], `${d}: planned slot ${k} neither baked nor listed missing`);
    }
  }
});

test('every reaction slot any attack can start resolves (defender bank first, else attacker bank)', () => {
  let checked = 0;
  for (const A of DIRS) {
    const recs = new Set();
    for (const [react, close] of Object.values(R.banks[A].rows)) {
      for (const v of [react, close ? (R.close_reactions[close][0] & 0xffff) : 0]) {
        if (v && !(v & 0xf000)) recs.add(v);
      }
    }
    for (const rec of recs) {
      for (let f = 0; f < 14; f++) {
        const slot = R.records[rec][f];
        if (!slot) continue;
        for (const V of DIRS) {
          const r = resolve(V, A, slot);
          assert.ok(r, `${A} record ${rec} ${R.record_fields[f]} slot ${hex(slot)}: empty in ${V} and ${A}`);
          assert.ok(!r.unaccounted, `${A} record ${rec} ${R.record_fields[f]} slot ${hex(slot)} (${r.dir}): no clip and no reason`);
          checked++;
        }
      }
    }
  }
  assert.ok(checked > 10000, `checked ${checked}`);
});

test('air kinds and the KO collapse resolve for every bank', () => {
  for (const V of DIRS) {
    for (const slot of [0xd56, 0xd61, 0xd62, 0xd63, 0xd64, 0xd66]) {
      const r = resolve(V, V, slot);
      assert.ok(r && !r.unaccounted, `${V}: ${hex(slot)}`);
    }
  }
});

test('every throw has its thrower clip and a victim clip for every opponent bank', () => {
  let throws = 0, pairs = 0;
  for (const A of DIRS) {
    for (const t of R.banks[A].throws) {
      if (!t.defined) {
        // the thrower's bank lacks the throw row: the game takes the opponent's row (and its victim move)
        for (const V of DIRS) {
          const tv = R.banks[V].throws.find((x) => x.slot === t.slot && x.defined);
          const r = resolve(A, V, t.slot);
          if (!r) continue;                          // neither bank defines it: that branch cannot start
          assert.ok(!r.unaccounted && tv, `${A}: borrowed throw ${hex(t.slot)} from ${V}`);
          if (tv.victim_slot !== null) assert.ok(!resolve(V, V, tv.victim_slot)?.unaccounted, `${V} victim ${hex(tv.victim_slot)}`);
          pairs++;
        }
        continue;
      }
      throws++;
      const th = resolve(A, A, t.slot);
      assert.ok(th && th.dir === A && !th.unaccounted, `${A}: thrower clip ${hex(t.slot)}`);
      if (t.victim_slot === null) continue;
      for (const V of DIRS) {
        const r = resolve(V, A, t.victim_slot);
        assert.ok(r && !r.unaccounted, `${A} throw ${hex(t.slot)} -> victim ${hex(t.victim_slot)} on ${V}`);
        pairs++;
      }
    }
  }
  assert.ok(throws > 100 && pairs > throws, `${throws} throws, ${pairs} pairs`);
});

test('throw breaks: the escape move resolves on the victim, its own victim move on the thrower', () => {
  let n = 0;
  for (const A of DIRS) {
    const bySlot = new Map(R.banks[A].throws.map((t) => [t.slot, t]));
    for (const t of R.banks[A].throws) {
      for (const e of t.breaks || []) {
        assert.ok(['1', '2', '1+2'].includes(e.input), `${A} ${hex(t.slot)}: break input ${e.input}`);
        const esc = bySlot.get(e.escape_slot);
        assert.ok(esc && esc.defined, `${A} ${hex(t.slot)}: escape ${hex(e.escape_slot)} listed as a throw`);
        for (const V of DIRS) {
          const r = resolve(V, A, e.escape_slot);
          assert.ok(r && !r.unaccounted, `${A} ${hex(t.slot)}: escape ${hex(e.escape_slot)} on ${V}`);
          if (esc.victim_slot !== null) {
            const rv = resolve(A, V, esc.victim_slot);
            assert.ok(rv && !rv.unaccounted, `${A} ${hex(t.slot)}: escaped thrower move ${hex(esc.victim_slot)} (vs ${V})`);
          }
          n++;
        }
      }
    }
  }
  assert.ok(n > 0, 'no throw breaks decoded');
});

test('reaction slots named by divmot99 attack rows are baked in some bank', () => {
  const planned = new Set(DIRS.flatMap((d) => Object.keys(R.banks[d].slots)));
  for (const [react, close] of Object.values(R.common_rows)) {
    for (const v of [react, close ? (R.close_reactions[close][0] & 0xffff) : 0]) {
      if (!v || (v & 0xf000)) continue;
      for (let f = 0; f < 14; f++) {
        const slot = R.records[v][f];
        if (slot) assert.ok(planned.has(hex(slot)), `common record ${v} ${R.record_fields[f]} ${hex(slot)}`);
      }
    }
  }
});

test('default continuations of baked clips stay resolvable', () => {
  for (const d of DIRS) {
    for (const [k, m] of Object.entries(R.banks[d].slots)) {
      const nx = m.next;
      if (nx === 3 || nx === 40) continue;           // standing / crouching stance (t3_neutral / crouch clips)
      if (!R.banks[d].slots[hex(nx)]) continue;      // not defined by this bank: the partner's bank supplies it
      const pk = PACK[d];
      assert.ok(pk.rows[hex(nx)] || pk.missing[hex(nx)], `${d} ${k}: next ${hex(nx)}`);
    }
  }
});
