// Real Tekken 7 stance for Pantera (2026-10-30). Node, no browser. Run: node --test test/t7-stance.test.mjs
// Data: game/assets/anim/t7/king/{skeleton,stance}.json, baked by tools/anim/t7_c8_stance_bake.py from King's T7
// kinrotsm.arc clip 132 (nakg_kg2kam, 0xC8) through Kiloutre's applyRotationFromAnimdata on Koenji's mannequin.
// Checks: the files are well-formed bank data with full provenance; the pose is a real standing guard (FK on the
// shipped skeleton: feet on the floor, upright torso, left foot forward, both hands up in front, seamless loop);
// and the wiring: t3anims.js T7_STANCES binds it for Pantera only, the fight and the select preview both apply it.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const DIR = join(ROOT, 'game/assets/anim/t7/king');
const skel = JSON.parse(readFileSync(join(DIR, 'skeleton.json'), 'utf8'));
const clip = JSON.parse(readFileSync(join(DIR, 'stance.json'), 'utf8'));
const src = (f) => readFileSync(join(ROOT, f), 'utf8');

// the joints game/js/t3anims.js retargetT3Clips drives (RIG_REQUIRED + spine/neck + shoulders + toes)
const JOINTS = ['Hips', 'Spine', 'Chest', 'Neck', 'Head', 'LeftShoulder', 'LeftArm', 'LeftForeArm', 'LeftHand',
  'LeftUpLeg', 'LeftLeg', 'LeftFoot', 'LeftToeBase', 'RightShoulder', 'RightArm', 'RightForeArm', 'RightHand',
  'RightUpLeg', 'RightLeg', 'RightFoot', 'RightToeBase'];

const qmul = (a, b) => [a[3] * b[0] + a[0] * b[3] + a[1] * b[2] - a[2] * b[1], a[3] * b[1] - a[0] * b[2] + a[1] * b[3] + a[2] * b[0],
  a[3] * b[2] + a[0] * b[1] - a[1] * b[0] + a[2] * b[3], a[3] * b[3] - a[0] * b[0] - a[1] * b[1] - a[2] * b[2]];
const qrot = (q, v) => { const [x, y, z, w] = q, tx = 2 * (y * v[2] - z * v[1]), ty = 2 * (z * v[0] - x * v[2]), tz = 2 * (x * v[1] - y * v[0]);
  return [v[0] + w * tx + (y * tz - z * ty), v[1] + w * ty + (z * tx - x * tz), v[2] + w * tz + (x * ty - y * tx)]; };
const P = {}, PAR = {};
for (const j of skel.joints) { P[j.name] = j.rest; PAR[j.name] = j.parent; }
function pose(f) { // FK on the shipped skeleton, exactly as the game's sourcePosed
  const G = {}, X = {};
  for (const j of skel.joints.map(k => k.name)) {
    const q = clip.rot_xyzw[j][f], p = PAR[j];
    if (!p) { G[j] = q; X[j] = clip.root_t[f]; continue; }
    G[j] = qmul(G[p], q);
    const o = qrot(G[p], [P[j][0] - P[p][0], P[j][1] - P[p][1], P[j][2] - P[p][2]]);
    X[j] = [X[p][0] + o[0], X[p][1] + o[1], X[p][2] + o[2]];
  }
  return X;
}
const N = clip.root_t.length;

test('T7 King stance files: well-formed bank data with full provenance', () => {
  assert.equal(skel.format, 'wh-anim-skel/1');
  assert.deepEqual(skel.joints.map(j => j.name).sort(), [...JOINTS].sort());
  assert.ok(skel.root_rest_y > 1 && skel.root_rest_y < 1.3, 'hip height of the T7 rest pose');
  assert.equal(clip.format, 'wh-anim/1');
  assert.equal(clip.fps, 60);
  assert.equal(clip.anim_set, 'FIGHT', 'a fight stance, never a show clip');
  assert.equal(N, 60);
  assert.equal(clip.t7_source.clip, 132);
  assert.equal(clip.t7_source.format, '0xC8');
  assert.equal(clip.t7_source.anim, 'nakg_kg2kam(DVD)');
  assert.deepEqual(clip.t7_source.moves, ['Kg_sKAM00_', 'Kg_KAM', 'Kg_sKAM_WAIT']);
  assert.equal(clip.applier.commit, 'bebb3d8bc5c4c2c58778ac6af4f87f3dc80062b1');
  assert.equal(clip.fk_selfcheck_max_m, 0, 'the bake reproduced the posed T7 joints exactly');
  for (const j of JOINTS) {
    assert.equal(clip.rot_xyzw[j].length, N, j);
    for (const q of clip.rot_xyzw[j]) assert.ok(Math.abs(Math.hypot(...q) - 1) < 1e-3, `${j} unit quaternion`);
  }
});

test('T7 King stance is a real standing guard on every frame (left foot forward, hands up in front)', () => {
  for (let f = 0; f < N; f++) {
    const X = pose(f);
    const low = Math.min(...Object.values(X).map(p => p[1]));
    assert.ok(low >= 0 && low < 0.1, `f${f}: feet on the floor (lowest joint ${low.toFixed(3)} m)`);
    assert.ok(X.Head[1] - X.Hips[1] > 0.4, `f${f}: torso upright`);
    assert.ok(X.LeftFoot[2] > X.RightFoot[2] + 0.4, `f${f}: left foot forward (orthodox, King)`);
    for (const s of ['Left', 'Right']) {
      assert.ok(X[s + 'Hand'][2] > X.Chest[2], `f${f}: ${s} hand in front of the chest`);
      assert.ok(X[s + 'Hand'][1] > X.Chest[1], `f${f}: ${s} hand up (guard)`);
    }
  }
  const a = pose(0), b = pose(N - 1);
  const seam = Math.max(...JOINTS.map(j => Math.hypot(a[j][0] - b[j][0], a[j][1] - b[j][1], a[j][2] - b[j][2])));
  assert.ok(seam < 0.03, `loop seam ${seam.toFixed(3)} m`);
});

test('wiring: Pantera only, applied in the fight and in the select preview', () => {
  const t3 = src('game/js/t3anims.js');
  const m = t3.match(/export const T7_STANCES = \{([\s\S]*?)\n\};/);
  assert.ok(m, 'T7_STANCES table');
  const entries = [...m[1].matchAll(/^\s*([\w-]+):\s*\{\s*bank:\s*'(\w+)',\s*dir:\s*'([^']+)'/gm)].map(x => x.slice(1));
  assert.deepEqual(entries, [['pantera', 'king', 'assets/anim/t7/king/']]);
  assert.match(t3, /export function applyT7Stance\(/);
  assert.match(src('game/js/fighter.js'), /applyT7Stance\(this\.char\.id, bank, clips, model, THREE, modelKey\)/);
  assert.match(src('game/js/select-screen.js'), /applyT7Stance\(c\.id, bank, rc, inst\.model, THREE, modelId\)/);
});
