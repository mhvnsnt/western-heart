// T7 generic banks (2026-11-10, owner: "negativo should have only had t7 data from negan"). Each T7-stance fighter's
// base character's OWN Tekken 7 walk / dash / crouch / jump / sidestep / guard / damage / KO states, baked from its
// motbin (tools/anim/t7_generic_slots.py + t7_generic_bank_bake.py --slots) into game/assets/anim/t3/t7_<base>/ and laid
// over the fighter's bound bank slot by slot (fighter.js OWN_SLOT_BANKS). Run: node --test test/t7-generic-banks.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
await import(join(ROOT, 'tools/anim/node_game_env.mjs'));
const THREE = await import('three');
const F = await import(join(ROOT, 'game/js/fighter.js'));
const T = await import(join(ROOT, 'game/js/t3anims.js'));
const T7_BAKE_TOOL = 'tools/anim/t7_c8_stance_bake.py';
const t7Banks = Object.keys(T.T3_BANKS).filter((b) => b.startsWith('t7_'));
const readJson = (rel) => JSON.parse(fs.readFileSync(join(ROOT, 'game', rel), 'utf8'));

// 14 (2026-11-10): the 13 T7-stance bases + Ganryu for Thor (tools/anim/t7_generic_slots/gan.json).
test('14 T7 generic banks are registered, each a T7-baked bank with its generic slots', () => {
  assert.equal(t7Banks.length, 14);
  for (const b of t7Banks) {
    const dir = T.T3_BANKS[b];
    assert.equal(readJson(dir + 'skeleton.json').tool, T7_BAKE_TOOL, `${b}: baked on the T7 mannequin path`);
    for (const slot of ['t3_neutral', 't3_walk_fwd', 't3_walk_back', 't3_block', 't3_hit', 't3_hit_launch', 't3_ko',
      't3_crouch', 't3_jump_up', 't3_dash_fwd', 't3_backdash', 't3_sidestep_a', 't3_sidestep_b']) {
      const d = readJson(dir + slot + '.json');
      assert.ok(d.t7_source && d.t7_source.moves && d.t7_source.moves.length, `${b}/${slot}: carries its T7 source move`);
    }
  }
});

test('every T7 KO falls and STAYS down (not the Fall_sKAM knockdown-and-recover)', () => {
  for (const b of [...t7Banks, 'raven', 'luckychloe']) {
    const d = readJson(T.T3_BANKS[b] + 't3_ko.json');
    const ys = d.root_t.map((r) => r[1]);
    assert.ok(ys[0] > 0.9 && ys[ys.length - 1] < 0.3, `${b}: KO hips ${ys[0].toFixed(2)} -> ${ys[ys.length - 1].toFixed(2)} m`);
    assert.ok(!d.t7_source.moves.includes('Fall_sKAM'), `${b}: KO is not Fall_sKAM`);
  }
});

test('each T7-stance fighter layers its OWN T7 stance base\'s generic bank', () => {
  for (const [fid, def] of Object.entries(T.T7_STANCES)) {
    if (fid === 'pond' || fid === 'ryusan') continue; // bound to their own T7 banks (raven / luckychloe) already
    const base = def.dir.replace(/\/$/, '').split('/').pop();
    assert.equal(F.OWN_SLOT_BANKS[fid], 't7_' + base, `${fid}: own-slot bank`);
    assert.equal(F.ownSlotBankFor(fid), 't7_' + base);
  }
});

test('T7-baked banks get no Tekken 3 head / spine / arm normalization; Tekken 3 banks still do', async () => {
  const logs = [];
  const log = console.log; console.log = (...a) => { logs.push(a.join(' ')); };
  try {
    const rig = () => {
      const B = (n, p, x, y, z) => { const b = new THREE.Bone(); b.name = n; b.position.set(x, y, z); if (p) p.add(b); return b; };
      const root = new THREE.Object3D(); const hips = B('Hips', root, 0, 1, 0); const sp = B('Spine', hips, 0, 0.14, 0);
      const s2 = B('Spine2', B('Spine1', sp, 0, 0.14, 0), 0, 0.14, 0); B('Head', B('Neck', s2, 0, 0.16, 0), 0, 0.12, 0);
      for (const s of ['Left', 'Right']) {
        const d = s === 'Left' ? 1 : -1;
        B(s + 'Hand', B(s + 'ForeArm', B(s + 'Arm', B(s + 'Shoulder', s2, d * 0.09, 0.13, 0), d * 0.11, 0, 0), d * 0.28, 0, 0), d * 0.26, 0, 0);
        B(s + 'ToeBase', B(s + 'Foot', B(s + 'Leg', B(s + 'UpLeg', hips, d * 0.1, -0.05, 0), 0, -0.45, 0), 0, -0.45, 0), 0, -0.07, 0.1);
      }
      const m = new THREE.Group(); m.add(root); m.updateMatrixWorld(true); return m;
    };
    const t7 = await T.loadT3Clips(THREE, 't7_negan');
    assert.ok(T.retargetT3Clips(t7, 't7_negan', rig(), THREE, 'negativo'), 't7_negan retargets');
    assert.equal(T.getT3Skeleton('t7_negan')._headCorr, undefined, 'no head constant on a T7-baked bank');
    assert.ok(!logs.some((l) => /bank 't7_negan': (head-frame|spine-pitch|arm-frame)/.test(l)), 'no T3 normalization logged for t7_negan');
    const jin = await T.loadT3Clips(THREE, 'jin');
    T.retargetT3Clips(jin, 'jin', rig(), THREE, 'demonio');
    assert.ok(T.getT3Skeleton('jin')._headCorr, 'the Tekken 3 jin bank still measures its head constant');
  } finally { console.log = log; }
});
