// pond_functional_test.mjs — FUNCTIONAL BANK TEST (chirality ground truth) for a T7 fighter.
// Fires the fighter's real input-1 (LEFT punch) and input-2 (RIGHT punch) clips through the
// game's own retarget (ensureT7Moves + t7MoveRetarget, game/js/t3anims.js) onto the fighter's
// own rig and measures per-hand forward extension peaks. If '1' lands with the anatomical
// right arm, the fighter is SWAPPED. Fixture: a JSON snapshot of the model's scene nodes
// (name/bone/TR children) — generate with the python snippet in
// docs/proof/2026-11-07/full-model-audit/AUDIT.md's lane notes, or reuse the pattern in
// tools/model-audit/chirality_audit.py's GLB reader. Set POND_SCRATCH to the fixture dir.
// Pond functional chirality test: fire her REAL T7 move clips for
// inputs 1 (Nj_lp002, left punch) and 2 (Nj_rp00, right punch)
// through the game's own retarget (wh2 == main + spine patch) onto
// her shipped GLB rig (fixture from the GLB itself) and measure
// which ANATOMICAL hand delivers each strike.
// Anatomical frame: her mesh faces +Z (audit: head/torso/foot
// vertex votes +Z), so anatomical left = +X in model space.
import { readFileSync, writeFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const WH2 = resolve(HERE, '../..');
await import(join(WH2, 'tools/anim/node_game_env.mjs'));
const THREE = await import('three');
const T = await import(join(WH2, 'game/js/t3anims.js'));

const gltfName = (n) => String(n || '').replace(/[^a-zA-Z0-9_]/g, '');
function buildModel(file) {
  const fx = JSON.parse(readFileSync(file, 'utf8'));
  const objs = fx.nodes.map((n) => {
    const o = n.bone ? new THREE.Bone() : new THREE.Object3D();
    o.name = gltfName(n.name);
    o.position.fromArray(n.translation);
    o.quaternion.fromArray(n.rotation);
    o.scale.fromArray(n.scale);
    return o;
  });
  fx.nodes.forEach((n, i) => { for (const c of n.children) objs[i].add(objs[c]); });
  const model = new THREE.Group(); model.name = 'bench-instance';
  for (const r of fx.roots) model.add(objs[r]);
  model.updateMatrixWorld(true);
  return model;
}

const SCRATCH = process.env.POND_SCRATCH || '/tmp';
const model = buildModel(join(SCRATCH, 'pond-fixture.json'));
const t3 = await T.loadT3Clips(THREE, 'raven');
const rc = T.retargetT3Clips(t3, 'raven', model, THREE, 'pond');
console.log('bank clips retargeted:', rc ? Object.keys(rc).length : null);
const withStance = T.applyT7Stance ? T.applyT7Stance('pond', 'raven', rc, model, THREE, 'pond') : null;
console.log('applyT7Stance:', withStance ? 'ok' : 'n/a');
const t7 = await T.ensureT7Moves('pond', THREE);
console.log('t7 moves loaded:', t7 ? Object.keys(t7.moves).length : null, 'byInput 1/2:', t7 && t7.byInput['1'], t7 && t7.byInput['2']);

const bones = {};
model.traverse((o) => { if (o.isBone) bones[o.name] = o; });
const wp = (o) => o.getWorldPosition(new THREE.Vector3());

function sampleClip(clip, label) {
  const mixer = new THREE.AnimationMixer(model);
  const action = mixer.clipAction(clip);
  action.setLoop(THREE.LoopRepeat, Infinity);
  action.play();
  const dur = clip.duration;
  const rows = [];
  const steps = 40;
  for (let i = 0; i <= steps; i++) {
    const t = dur * i / steps;
    mixer.setTime(t);
    model.updateMatrixWorld(true);
    const hips = wp(bones.Hips);
    const lh = wp(bones.LeftHand), rh = wp(bones.RightHand);
    rows.push({ t: +t.toFixed(3),
      L: { fwd: +(lh.z - hips.z).toFixed(3), lat: +(lh.x - hips.x).toFixed(3), up: +(lh.y - hips.y).toFixed(3) },
      R: { fwd: +(rh.z - hips.z).toFixed(3), lat: +(rh.x - hips.x).toFixed(3), up: +(rh.y - hips.y).toFixed(3) } });
  }
  mixer.stopAllAction();
  const peak = (side) => rows.reduce((a, r) => (r[side].fwd > a.fwd ? { fwd: r[side].fwd, t: r.t } : a), { fwd: -9, t: 0 });
  const pL = peak('L'), pR = peak('R');
  console.log(`${label}: duration=${dur.toFixed(2)}s peakFwd LeftHand=${pL.fwd}m @${pL.t}s | RightHand=${pR.fwd}m @${pR.t}s`);
  return { label, dur, pL, pR, rows };
}

const out = {};
// stance (T7 stance if swapped in, else bank stance)
const stanceClip = (withStance && withStance.stance) || rc.stance;
if (stanceClip) out.stance = sampleClip(stanceClip, 'stance');
for (const key of ['1~t7.masterraven', '2~t7.masterraven']) {
  const r = T.t7MoveRetarget('pond', 'raven', key, model, THREE, 'pond');
  if (!r) { console.log('NO RETARGET for', key); continue; }
  const name = Object.keys(r)[0];
  out[key] = sampleClip(r[name], key);
}
writeFileSync(join(SCRATCH, 'pond-functional.json'), JSON.stringify(out, null, 1));
console.log('WROTE pond-functional.json (in POND_SCRATCH)');
