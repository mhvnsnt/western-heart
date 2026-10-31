// Real Tekken 7 stances (2026-10-30/31). Node, no browser. Run: node --test test/t7-stance.test.mjs
// Data: game/assets/anim/t7/<character>/{skeleton,stance}.json, baked by tools/anim/t7_c8_stance_bake.py from each
// character's own 0xC8 stance clip (the clip its <code>_sKAM00_ move plays) through Kiloutre's
// applyRotationFromAnimdata on Koenji's mannequin.
// Checks: well-formed bank data with full provenance; every frame a real standing stance (FK on the shipped
// skeleton: feet on the floor, upright torso, hands above the knees, seamless loop; King's orthodox guard for
// Pantera); and the wiring: t3anims.js T7_STANCES names exactly the fighters below on their own base, applied in the
// fight and in the select preview.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const src = (f) => readFileSync(join(ROOT, f), 'utf8');

// character dir -> [T7 clip index, anim name, stance move]  (the character's own <code>_sKAM00_ stance clip, 0xC8)
const CLIPS = {
  king: [132, 'nakg_kg2kam(DVD)', 'Kg_sKAM00_'],
  heihachi: [126, 'nahe_he2kam(DVD)', 'He_sKAM00_'],
  bryan: [126, 'nabx_bx2kam(DVD)', 'Bx_sKAM00_'],
  xiaoyu: [126, 'kmfu_kamae(DVD)', 'Fu_sKAM00_'],
  bob: [128, 'ikfa_kamae(DVD)', 'Ft_sKAM00_'],
  yoshimitsu: [117, 'mbym_kamae(DVD)', 'Ym_sKAM00_'],
  hwoarang: [126, 'kmhw_kamae_L(DVD)', 'Hw_sKAM00_'],
  kuma: [201, 'nakm_kam(DVD)', 'Km_sKAM00_'],
  panda: [201, 'nakm_kam(DVD)', 'Km_sKAM00_'],
  julia: [119, 'najl_jl2kam', 'Jl_sKAM00_'],
  lee: [126, 'kole_kamae(DVD)', 'Le_sKAM00_'],
  lars: [123, 'amla_kamae(DVD)', 'La_sKAM00_'],
  negan: [131, 'nass_kamae', 'Na_sKAM00_'],
};
// Western Heart fighter -> [bound bank, character dir] (CANON base; FIGHTER_BANK / moveset index bank)
const WIRED = {
  pantera: ['king', 'king'], diablo: ['heihachi', 'heihachi'], skull: ['bryan', 'bryan'], retsu: ['bryan', 'bryan'],
  burger: ['bryan', 'bob'], sakura: ['xiaoyu', 'xiaoyu'], sha: ['xiaoyu', 'xiaoyu'], phantom: ['yoshimitsu', 'yoshimitsu'],
  gyou: ['hwoarang', 'hwoarang'], tobi: ['hwoarang', 'hwoarang'], gashadokuro: ['kuma', 'kuma'], aotsuki: ['kuma', 'panda'],
  nightwolf: ['julia', 'julia'],
  // proxy-bank fighters (moveset t3_source jin / jin / bryan) on their own bases' stances
  purplerain: ['jin', 'lee'], chordz: ['jin', 'lars'], negativo: ['bryan', 'negan'],
};

// the joints game/js/t3anims.js retargetT3Clips drives (RIG_REQUIRED + spine/neck + shoulders + toes)
const JOINTS = ['Hips', 'Spine', 'Chest', 'Neck', 'Head', 'LeftShoulder', 'LeftArm', 'LeftForeArm', 'LeftHand',
  'LeftUpLeg', 'LeftLeg', 'LeftFoot', 'LeftToeBase', 'RightShoulder', 'RightArm', 'RightForeArm', 'RightHand',
  'RightUpLeg', 'RightLeg', 'RightFoot', 'RightToeBase'];
const qmul = (a, b) => [a[3] * b[0] + a[0] * b[3] + a[1] * b[2] - a[2] * b[1], a[3] * b[1] - a[0] * b[2] + a[1] * b[3] + a[2] * b[0],
  a[3] * b[2] + a[0] * b[1] - a[1] * b[0] + a[2] * b[3], a[3] * b[3] - a[0] * b[0] - a[1] * b[1] - a[2] * b[2]];
const qrot = (q, v) => { const [x, y, z, w] = q, tx = 2 * (y * v[2] - z * v[1]), ty = 2 * (z * v[0] - x * v[2]), tz = 2 * (x * v[1] - y * v[0]);
  return [v[0] + w * tx + (y * tz - z * ty), v[1] + w * ty + (z * tx - x * tz), v[2] + w * tz + (x * ty - y * tx)]; };
function load(dir) {
  const D = join(ROOT, 'game/assets/anim/t7', dir);
  const skel = JSON.parse(readFileSync(join(D, 'skeleton.json'), 'utf8'));
  const clip = JSON.parse(readFileSync(join(D, 'stance.json'), 'utf8'));
  const P = {}, PAR = {};
  for (const j of skel.joints) { P[j.name] = j.rest; PAR[j.name] = j.parent; }
  const pose = (f) => { // FK on the shipped skeleton, exactly as the game's sourcePosed
    const G = {}, X = {};
    for (const j of skel.joints.map(k => k.name)) {
      const q = clip.rot_xyzw[j][f], p = PAR[j];
      if (!p) { G[j] = q; X[j] = clip.root_t[f]; continue; }
      G[j] = qmul(G[p], q);
      const o = qrot(G[p], [P[j][0] - P[p][0], P[j][1] - P[p][1], P[j][2] - P[p][2]]);
      X[j] = [X[p][0] + o[0], X[p][1] + o[1], X[p][2] + o[2]];
    }
    return X;
  };
  return { skel, clip, pose, N: clip.root_t.length };
}

for (const [dir, [idx, anim, move]] of Object.entries(CLIPS)) {
  test(`T7 ${dir} stance: well-formed bank data with full provenance`, () => {
    const { skel, clip, N } = load(dir);
    assert.equal(skel.format, 'wh-anim-skel/1');
    assert.deepEqual(skel.joints.map(j => j.name).sort(), [...JOINTS].sort());
    assert.ok(skel.root_rest_y > 1 && skel.root_rest_y < 1.3, 'hip height of the T7 rest pose');
    assert.equal(clip.format, 'wh-anim/1');
    assert.equal(clip.fps, 60);
    assert.equal(clip.anim_set, 'FIGHT', 'a fight stance, never a show clip');
    assert.ok(N >= 30, `${N} frames`);
    assert.equal(clip.t7_source.clip, idx);
    assert.equal(clip.t7_source.format, '0xC8');
    assert.equal(clip.t7_source.anim, anim);
    assert.ok(clip.t7_source.moves.includes(move), `played by ${move}`);
    assert.equal(clip.t7_source.frames, N);
    assert.equal(clip.applier.commit, 'bebb3d8bc5c4c2c58778ac6af4f87f3dc80062b1');
    assert.ok(clip.fk_selfcheck_max_m <= 1e-5, `the bake reproduced the posed T7 joints (FK error ${clip.fk_selfcheck_max_m} m)`);
    for (const j of JOINTS) {
      assert.equal(clip.rot_xyzw[j].length, N, j);
      for (const q of clip.rot_xyzw[j]) assert.ok(Math.abs(Math.hypot(...q) - 1) < 1e-3, `${j} unit quaternion`);
    }
  });

  test(`T7 ${dir} stance is a real standing stance on every frame`, () => {
    const { pose, N } = load(dir);
    for (let f = 0; f < N; f++) {
      const X = pose(f);
      const low = Math.min(...Object.values(X).map(p => p[1]));
      assert.ok(low >= 0 && low < 0.1, `f${f}: feet on the floor (lowest joint ${low.toFixed(3)} m)`);
      assert.ok(X.Head[1] - X.Hips[1] > 0.4, `f${f}: torso upright`);
      const knee = Math.max(X.LeftLeg[1], X.RightLeg[1]);
      for (const s of ['Left', 'Right']) assert.ok(X[s + 'Hand'][1] > knee + 0.2, `f${f}: ${s} hand above the knees`);
    }
    const a = pose(0), b = pose(N - 1);
    const seam = Math.max(...JOINTS.map(j => Math.hypot(a[j][0] - b[j][0], a[j][1] - b[j][1], a[j][2] - b[j][2])));
    assert.ok(seam < 0.03, `loop seam ${seam.toFixed(3)} m`);
  });
}

test("Pantera's King stance is King's orthodox guard (left foot forward, both hands up in front)", () => {
  const { pose, N } = load('king');
  for (let f = 0; f < N; f++) {
    const X = pose(f);
    assert.ok(X.LeftFoot[2] > X.RightFoot[2] + 0.4, `f${f}: left foot forward`);
    for (const s of ['Left', 'Right']) {
      assert.ok(X[s + 'Hand'][2] > X.Chest[2], `f${f}: ${s} hand in front of the chest`);
      assert.ok(X[s + 'Hand'][1] > X.Chest[1], `f${f}: ${s} hand up (guard)`);
    }
  }
});

test('wiring: each fighter on its own CANON base, applied in the fight and in the select preview', () => {
  const t3 = src('game/js/t3anims.js');
  const m = t3.match(/export const T7_STANCES = \{([\s\S]*?)\n\};/);
  assert.ok(m, 'T7_STANCES table');
  const entries = Object.fromEntries([...m[1].matchAll(/^\s*'?([\w-]+)'?:\s*\{\s*bank:\s*'(\w+)',\s*dir:\s*'assets\/anim\/t7\/(\w+)\/'/gm)]
    .map(x => [x[1], [x[2], x[3]]]));
  assert.deepEqual(entries, WIRED);
  for (const [, dir] of Object.values(WIRED)) assert.ok(CLIPS[dir], `${dir} has a baked stance`);
  // owner decisions stay untouched: Zen is NOT Heihachi, cyborgx/zui keep their stances, jin_soul / menajerii /
  // silvertongue are not on these bases
  for (const id of ['zen', 'cyborgx', 'zui', 'jin_soul', 'menajerii', 'silvertongue']) assert.ok(!(id in entries), id);
  assert.match(t3, /export function applyT7Stance\(/);
  assert.match(src('game/js/fighter.js'), /applyT7Stance\(this\.char\.id, bank, clips, model, THREE, modelKey\)/);
  assert.match(src('game/js/select-screen.js'), /applyT7Stance\(c\.id, bank, rc, inst\.model, THREE, modelId\)/);
});
