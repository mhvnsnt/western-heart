// Arm-frame normalization (roster arm audit, 2026-11-07). Node, no browser.
// Run: node --test test/arm-frame-normalization.test.mjs
//
// THE DEFECT (owner, 2026-11-06 23:51 CST): "Now gotta fix the wired
// candy wrapper shoulders, arms, elbows, and hands twists and wired
// stuff happening on every caharcters arms almost"
//
// MEASURED ROOT CAUSE: the retarget's per-joint swing A(c) aligns
// bone DIRECTIONS exactly but cannot carry the source frame's ROLL,
// so the roll split between adjacent arm locals is scrambled by the
// conjugation local(k) = Wrest(parent)^-1 A(parent)^-1 G-local A(k)
// Wrest(k). On the banks' own skeletons the arm chain is anatomical
// (elbow hinge error 0.0-0.5 deg in 24 of 26 banks; forearm locals
// are pure hinge swings). After transport the forearm local carries
// a CONSTANT twist error (spread 0.0 across stance/light/heavy):
// jin right -154.1 deg (elbow hinge error 79.7-82.7 deg on the
// canonical rig vs 0-5.8 in the source), paul right +84.2, gunjack
// +17.3/-19.8. The hand local's twist transports exactly (the wrist
// wrapper is the forearm's rolled frame). Full audit:
// docs/proof/2026-11-07/arm-twist-audit/AUDIT.md
//
// THE FIX (game/js/t3anims.js, estimateArmCorr + the frame-loop
// G-roll): per (bank, rig) constants measured from the bank's own
// stance at first retarget — the stance is built once uncorrected
// (the probe), each arm joint's twist error (target local vs source
// local, about each side's own bone axis) is zeroed top-down by a
// constant roll about the joint's posed bone axis, gated at 12 deg
// (25 for the torso-match-entangled Shoulder). Rolls change no
// position and no bone direction. Clean transports measure 0.0 and
// stay untouched (king; jun/roger/xiaoyu arm chains; the T7
// mannequin path), and source-true data stays untouched (xiaoyu's
// in-source 29-33 deg hinge error is HERS, transported faithfully).
//
// This test runs the REAL banks through the REAL retarget onto a
// synthetic canonical rig (Mixamo-shaped, identity rest — the
// head-frame test's rig) and pins the measured behavior.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
await import(join(ROOT, 'tools/anim/node_game_env.mjs'));
const THREE = await import('three');
const T = await import(join(ROOT, 'game/js/t3anims.js'));

const DEG = 180 / Math.PI;
const wrap = (a) => { while (a > Math.PI) a -= 2 * Math.PI; while (a < -Math.PI) a += 2 * Math.PI; return a; };
const twistOf = (q, ax) => wrap(2 * Math.atan2(q.x * ax.x + q.y * ax.y + q.z * ax.z, q.w));
function circMean(angs) {
  let x = 0, y = 0; for (const a of angs) { x += Math.cos(a); y += Math.sin(a); }
  const n = angs.length || 1; const R = Math.hypot(x / n, y / n);
  return { mean: Math.atan2(y / n, x / n), spread: Math.sqrt(Math.max(0, -2 * Math.log(Math.max(R, 1e-9)))) };
}

function buildCanonicalRig() {
  const B = (name, parent, x, y, z) => {
    const b = new THREE.Bone(); b.name = name; b.position.set(x, y, z);
    if (parent) parent.add(b); return b;
  };
  const root = new THREE.Object3D(); root.name = 'Armature';
  const hips = B('Hips', root, 0, 1.00, 0);
  const spine = B('Spine', hips, 0, 0.14, 0);
  const spine1 = B('Spine1', spine, 0, 0.14, 0);
  const spine2 = B('Spine2', spine1, 0, 0.14, 0);
  const neck = B('Neck', spine2, 0, 0.16, 0);
  B('Head', neck, 0, 0.12, 0);
  for (const s of ['Left', 'Right']) {
    const d = s === 'Left' ? 1 : -1;
    const sh = B(s + 'Shoulder', spine2, d * 0.09, 0.13, 0);
    const arm = B(s + 'Arm', sh, d * 0.11, 0, 0);
    const fore = B(s + 'ForeArm', arm, d * 0.28, 0, 0);
    B(s + 'Hand', fore, d * 0.26, 0, 0);
    const up = B(s + 'UpLeg', hips, d * 0.10, -0.05, 0);
    const leg = B(s + 'Leg', up, 0, -0.45, 0);
    const foot = B(s + 'Foot', leg, 0, -0.45, 0);
    B(s + 'ToeBase', foot, 0, -0.07, 0.10);
  }
  const model = new THREE.Group(); model.name = 'test-instance';
  model.add(root); model.updateMatrixWorld(true);
  return model;
}
const byCanon = (model, cn) => {
  let h = null;
  model.traverse((o) => { if (!h && o.isBone && T.canonBoneName(o.name) === cn) h = o; });
  return h;
};

// Source-side per-frame locals + bone axes from a wh-anim skeleton
// and a clip's raw rot data (the census composition).
function sourceData(skel, raw) {
  const J = {}; const order = [];
  for (const j of skel.joints) { J[j.name] = j; order.push(j.name); }
  const CHILD = { Shoulder: 'Arm', Arm: 'ForeArm', ForeArm: 'Hand' };
  const axis = {};
  for (const name of order) {
    const base = name.replace(/^(Left|Right)/, ''); const side = name.slice(0, name.length - base.length);
    const cn = CHILD[base] ? side + CHILD[base] : null;
    let v = null;
    if (cn && J[cn]) v = J[cn].rest.map((x, i) => x - J[name].rest[i]);
    else if (base === 'Hand') { const p = J[side + 'ForeArm'].rest; v = J[name].rest.map((x, i) => x - p[i]); }
    if (v) { const l = Math.hypot(...v); axis[name] = new THREE.Vector3(v[0] / l, v[1] / l, v[2] / l); }
  }
  let n = 0; for (const j of order) if (raw.rot[j] && raw.rot[j].length > n) n = raw.rot[j].length;
  const frames = [];
  const G = {};
  for (let f = 0; f < n; f++) {
    for (const name of order) {
      const r = raw.rot[name]; const q = new THREE.Quaternion();
      if (r && r.length) { const v = r[Math.min(f, r.length - 1)]; q.set(v[0], v[1], v[2], v[3]); }
      const p = J[name].parent; if (p && G[p]) q.premultiply(G[p]);
      G[name] = q;
    }
    const snap = {};
    for (const name of order) { const p = J[name].parent; snap[name] = p && G[p] ? G[p].clone().invert().multiply(G[name]) : G[name].clone(); }
    frames.push(snap);
    for (const k of Object.keys(G)) G[k] = G[k].clone();
  }
  return { frames, axis, n };
}

// Measure one retargeted clip on the model: per-joint circular-mean
// twist error vs the source, plus flexion-weighted elbow hinge error.
function measure(model, rclip, src, fps) {
  const bones = {};
  for (const s of ['Left', 'Right']) for (const j of ['Shoulder', 'Arm', 'ForeArm', 'Hand']) bones[s + j] = byCanon(model, s + j);
  const mixer = new THREE.AnimationMixer(model);
  const act = mixer.clipAction(rclip); act.play();
  const dT = {}; for (const k of Object.keys(bones)) dT[k] = [];
  let hN = { Left: 0, Right: 0 }, hD = { Left: 0, Right: 0 };
  for (let f = 0; f < src.n; f++) {
    mixer.setTime(f / fps);
    model.updateMatrixWorld(true);
    for (const s of ['Left', 'Right']) {
      const axT = new THREE.Vector3(s === 'Left' ? 1 : -1, 0, 0);
      for (const j of ['Shoulder', 'Arm', 'ForeArm', 'Hand']) {
        const nm = s + j;
        dT[nm].push(wrap(twistOf(bones[nm].quaternion, axT) - twistOf(src.frames[f][nm], src.axis[nm])));
      }
      const pA = bones[s + 'Arm'].getWorldPosition(new THREE.Vector3());
      const pF = bones[s + 'ForeArm'].getWorldPosition(new THREE.Vector3());
      const pH = bones[s + 'Hand'].getWorldPosition(new THREE.Vector3());
      const hinge = new THREE.Vector3().crossVectors(pF.clone().sub(pA).normalize(), pH.clone().sub(pF).normalize());
      const faL = bones[s + 'ForeArm'].quaternion;
      const flex = 2 * Math.acos(Math.min(1, Math.abs(faL.w)));
      if (hinge.length() > 1e-4 && flex > 0.05) {
        hinge.normalize();
        const axW = new THREE.Vector3(faL.x, faL.y, faL.z).normalize().applyQuaternion(bones[s + 'Arm'].getWorldQuaternion(new THREE.Quaternion()));
        hN[s] += Math.acos(Math.min(1, Math.abs(axW.dot(hinge)))) * flex; hD[s] += flex;
      }
    }
  }
  mixer.stopAllAction();
  const out = { joints: {}, hinge: {} };
  for (const k of Object.keys(dT)) { const c = circMean(dT[k]); out.joints[k] = { mean: c.mean * DEG, spread: c.spread * DEG }; }
  for (const s of ['Left', 'Right']) out.hinge[s] = hD[s] ? hN[s] / hD[s] * DEG : null;
  return out;
}
const skelOf = (bank) => JSON.parse(fs.readFileSync(join(ROOT, 'game', T.T3_BANKS[bank], 'skeleton.json'), 'utf8'));

test('demonio (jin bank): stance arm twists match the source — the wrapper is gone', async () => {
  const clips = await T.loadT3Clips(THREE, 'jin');
  const model = buildCanonicalRig();
  const rc = T.retargetT3Clips(clips, 'jin', model, THREE, 'demonio');
  assert.ok(rc && rc.stance, 'stance retargeted');
  for (const tr of rc.stance.tracks) assert.ok(!tr.name.endsWith('.scale'), `scale track emitted: ${tr.name}`);
  const src = sourceData(skelOf('jin'), clips.stance.userData.raw);
  const m = measure(model, rc.stance, src, clips.stance.userData.raw.fps);
  // Before the fix: LeftArm -42.7, RightArm +50.2, LeftForeArm -19.9,
  // RightForeArm -154.1 deg; hinge error L 13.7 / R 79.7 deg.
  for (const j of ['LeftArm', 'RightArm', 'LeftForeArm', 'RightForeArm', 'LeftHand', 'RightHand']) {
    assert.ok(Math.abs(m.joints[j].mean) <= 3, `${j} stance twist error ${m.joints[j].mean.toFixed(1)}deg > 3deg`);
  }
  assert.ok(m.hinge.Left <= 3 && m.hinge.Right <= 3,
    `stance hinge error L ${m.hinge.Left.toFixed(1)} / R ${m.hinge.Right.toFixed(1)} deg > 3deg`);
});

test('demonio (jin bank): move clips keep an anatomical elbow', async () => {
  const clips = await T.loadT3Clips(THREE, 'jin');
  const model = buildCanonicalRig();
  const rc = T.retargetT3Clips(clips, 'jin', model, THREE, 'demonio');
  const skel = skelOf('jin');
  for (const action of ['light', 'heavy']) {
    const src = sourceData(skel, clips[action].userData.raw);
    const m = measure(model, rc[action], src, clips[action].userData.raw.fps);
    // The forearm constant is clip-independent (spread 0.0 pre-fix),
    // so the correction holds in moves: before the fix the hinge
    // error measured 25.8/79.7 (light) and 13.9/82.7 (heavy).
    for (const j of ['LeftForeArm', 'RightForeArm', 'LeftHand', 'RightHand']) {
      assert.ok(Math.abs(m.joints[j].mean) <= 3, `${action} ${j} twist error ${m.joints[j].mean.toFixed(1)}deg > 3deg`);
    }
    assert.ok(m.hinge.Left <= 3 && m.hinge.Right <= 3,
      `${action} hinge error L ${m.hinge.Left.toFixed(1)} / R ${m.hinge.Right.toFixed(1)} deg > 3deg`);
  }
});

test('paul bank: the +84.2 deg right-forearm constant is normalized', async () => {
  const clips = await T.loadT3Clips(THREE, 'paul');
  const model = buildCanonicalRig();
  const rc = T.retargetT3Clips(clips, 'paul', model, THREE, 'harness');
  const src = sourceData(skelOf('paul'), clips.stance.userData.raw);
  const m = measure(model, rc.stance, src, clips.stance.userData.raw.fps);
  for (const j of ['LeftForeArm', 'RightForeArm']) {
    assert.ok(Math.abs(m.joints[j].mean) <= 3, `${j} stance twist error ${m.joints[j].mean.toFixed(1)}deg > 3deg`);
  }
  // Before the fix the right hinge error measured 46.6 deg.
  assert.ok(m.hinge.Right <= 3, `right hinge error ${m.hinge.Right.toFixed(1)}deg > 3deg`);
});

test('megami (jun bank): the torso-split shoulder constant is normalized, chain stays exact', async () => {
  const clips = await T.loadT3Clips(THREE, 'jun');
  const model = buildCanonicalRig();
  const rc = T.retargetT3Clips(clips, 'jun', model, THREE, 'megami');
  const src = sourceData(skelOf('jun'), clips.stance.userData.raw);
  const m = measure(model, rc.stance, src, clips.stance.userData.raw.fps);
  // Before the fix: LeftShoulder +28.4 / RightShoulder -29.8 deg
  // (over the 25 deg shoulder gate), Arm/ForeArm/Hand already 0.0.
  for (const j of ['LeftShoulder', 'RightShoulder', 'LeftArm', 'RightArm', 'LeftForeArm', 'RightForeArm']) {
    assert.ok(Math.abs(m.joints[j].mean) <= 3, `${j} stance twist error ${m.joints[j].mean.toFixed(1)}deg > 3deg`);
  }
});

test('yukihyo (king bank): the clean bank is NOT normalized — data untouched', async () => {
  const clips = await T.loadT3Clips(THREE, 'king');
  const model = buildCanonicalRig();
  const rc = T.retargetT3Clips(clips, 'king', model, THREE, 'yukihyo');
  const src = sourceData(skelOf('king'), clips.stance.userData.raw);
  const m = measure(model, rc.stance, src, clips.stance.userData.raw.fps);
  for (const j of ['LeftArm', 'RightArm', 'LeftForeArm', 'RightForeArm', 'LeftHand', 'RightHand']) {
    assert.ok(Math.abs(m.joints[j].mean) <= 1, `${j} twist error ${m.joints[j].mean.toFixed(1)}deg — king must stay exact`);
  }
  // The shoulders' +-1.3 deg is the pre-existing torso-match split,
  // identical in the unmodified engine; king gets no arm correction.
  for (const j of ['LeftShoulder', 'RightShoulder']) {
    assert.ok(Math.abs(m.joints[j].mean) <= 2, `${j} twist error ${m.joints[j].mean.toFixed(1)}deg — king shoulder split changed`);
  }
  // King's own stance hinge error (8.8 / 13.7 deg) is his data: the
  // retarget must reproduce it, not normalize it away.
  assert.ok(m.hinge.Left > 5 && m.hinge.Left < 13, `king left hinge ${m.hinge.Left.toFixed(1)}deg outside his measured band`);
  assert.ok(m.hinge.Right > 9 && m.hinge.Right < 18, `king right hinge ${m.hinge.Right.toFixed(1)}deg outside his measured band`);
});

test('xiaoyu bank: transported exactly, with an anatomical elbow on her own rig rest', async () => {
  const clips = await T.loadT3Clips(THREE, 'xiaoyu');
  const model = buildCanonicalRig();
  const rc = T.retargetT3Clips(clips, 'xiaoyu', model, THREE, 'harness');
  const src = sourceData(skelOf('xiaoyu'), clips.stance.userData.raw);
  const m = measure(model, rc.stance, src, clips.stance.userData.raw.fps);
  for (const j of ['LeftArm', 'RightArm', 'LeftForeArm', 'RightForeArm', 'LeftHand', 'RightHand']) {
    assert.ok(Math.abs(m.joints[j].mean) <= 1, `${j} twist error ${m.joints[j].mean.toFixed(1)}deg — xiaoyu must stay exact`);
  }
  // 2026-11-07: this test used to pin a 29-33 deg "source-true" elbow hinge error. That number came from her
  // skeleton.json, which had been rewritten to a neutral T-pose (tools/anim/t3_bank_skeleton.py NEUTRAL_BIND, now
  // retired) while her clips are local rotations of the source rig at ITS rest (t3_bank_skeleton.py --check: 522
  // channels equal the GLB's own animation, max error 8e-7). Composed on the real rest, her elbow is a pure hinge like
  // 24 of the 26 banks, and every Xiaoyu-bank fighter now matches the source within ~2 deg in poselab
  // (docs/proof/2026-11-07/xiaoyu-bank-rest/).
  assert.ok(m.hinge.Left < 5 && m.hinge.Right < 5,
    `xiaoyu hinge L ${m.hinge.Left.toFixed(1)} / R ${m.hinge.Right.toFixed(1)} deg — her elbow should be anatomical on her own rig rest`);
});

test('pantera (T7 king stance): the mannequin path stays exact and untouched', async () => {
  const clips = await T.loadT3Clips(THREE, 'king');
  const model = buildCanonicalRig();
  let rc = T.retargetT3Clips(clips, 'king', model, THREE, 'pantera');
  rc = T.applyT7Stance('pantera', 'king', rc, model, THREE, 'pantera');
  assert.ok(rc && rc.stance, 'T7 stance applied');
  const skel = JSON.parse(fs.readFileSync(join(ROOT, 'game/assets/anim/t7/king/skeleton.json'), 'utf8'));
  const data = JSON.parse(fs.readFileSync(join(ROOT, 'game/assets/anim/t7/king/stance.json'), 'utf8'));
  const src = sourceData(skel, { rot: data.rot_xyzw, fps: data.fps });
  const m = measure(model, rc.stance, src, data.fps);
  // The T7 stance's own arm twists (L Arm -57 / R Arm +37 deg — his
  // real side-on guard) are reproduced, and the transport onto this
  // rig already measures 0.0, so no correction may fire.
  for (const j of ['LeftArm', 'RightArm', 'LeftForeArm', 'RightForeArm', 'LeftHand', 'RightHand']) {
    assert.ok(Math.abs(m.joints[j].mean) <= 1, `${j} T7 twist error ${m.joints[j].mean.toFixed(1)}deg — T7 path must stay exact`);
  }
});
