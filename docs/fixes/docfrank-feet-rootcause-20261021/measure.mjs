// FEET MEASUREMENT — run the game's REAL t3anims path (loadT3Clips ->
// retargetT3Clips -> createT3Actions -> mixer) on a GLB and measure
// foot/toe world orientation at rest and posed, vs character forward.
// Also FKs the SOURCE skeleton with the bank's own clip for the
// source-side toe direction (foot_tip as toe).
// usage: GAME_ROOT=<dir with game/> node measure.mjs <glbPath> <bankId> <modelKey> [action]
// GAME_ROOT defaults to the ladder worktree; the module URLs are built from it.
import fs from 'fs';
const GAME_ROOT = process.env.GAME_ROOT || '/home/hatch/workspace/_docfrank-ladder/wh';
const THREE = await import(`file://${GAME_ROOT}/game/vendor/three.module.js`);
const T3 = await import(`file://${GAME_ROOT}/game/js/t3anims.js`);
const { loadT3Clips, getT3Clips, getT3Skeleton, getT3BankFacing, retargetT3Clips, createT3Actions, canonBoneName } = T3;

const [,, glbPath, bankId, modelKey, actionName = 'stance'] = process.argv;

const _fetch = globalThis.fetch;
globalThis.fetch = (u, o) => _fetch(typeof u === 'string' && !u.startsWith('http')
  ? 'http://127.0.0.1:8791/game/' + u : u, o);

function parseGLB(path) {
  const buf = fs.readFileSync(path);
  const jsonLen = buf.readUInt32LE(12);
  return JSON.parse(buf.subarray(20, 20 + jsonLen).toString('utf8'));
}
function buildHierarchy(json) {
  const nodes = json.nodes || [];
  const jointSet = new Set((json.skins?.[0]?.joints) || []);
  const objs = nodes.map((n, i) => {
    const o = jointSet.has(i) ? new THREE.Bone() : new THREE.Object3D();
    o.name = n.name || `node${i}`;
    if (n.matrix) {
      const m = new THREE.Matrix4().fromArray(n.matrix);
      m.decompose(o.position, o.quaternion, o.scale);
    } else {
      if (n.translation) o.position.fromArray(n.translation);
      if (n.rotation) o.quaternion.fromArray(n.rotation);
      if (n.scale) o.scale.fromArray(n.scale);
    }
    return o;
  });
  nodes.forEach((n, i) => (n.children || []).forEach(c => objs[i].add(objs[c])));
  const root = new THREE.Group();
  (json.scenes[json.scene || 0].nodes || []).forEach(r => root.add(objs[r]));
  root.updateMatrixWorld(true);
  return { root, objs };
}
const wp = (o) => { const v = new THREE.Vector3(); o.getWorldPosition(v); return v; };
const yawDeg = (v) => +THREE.MathUtils.radToDeg(Math.atan2(v.x, v.z)).toFixed(1);

function measureFeet(root, label) {
  const by = {};
  root.traverse(o => { if (o.isBone) { const c = canonBoneName(o.name); if (c && !by[c]) by[c] = o; } });
  root.updateMatrixWorld(true);
  let fwd = null;
  if (by.LeftShoulder && by.RightShoulder) {
    const line = wp(by.RightShoulder).sub(wp(by.LeftShoulder)); line.y = 0; line.normalize();
    fwd = new THREE.Vector3(-line.z, 0, line.x);
  } else if (by.LeftArm && by.RightArm) {
    const line = wp(by.RightArm).sub(wp(by.LeftArm)); line.y = 0; line.normalize();
    fwd = new THREE.Vector3(-line.z, 0, line.x);
  }
  const out = { label, fwdYaw: fwd ? yawDeg(fwd) : null, feet: {} };
  for (const s of ['Left', 'Right']) {
    const foot = by[s + 'Foot'], toe = by[s + 'ToeBase'];
    if (!foot) { out.feet[s] = 'NO FOOT BONE'; continue; }
    const fp = wp(foot);
    let dir = null, src = 'none';
    if (toe) { dir = wp(toe).sub(fp); src = 'ToeBaseJoint'; }
    if (dir && dir.lengthSq() > 1e-10) {
      const flat = dir.clone(); flat.y = 0;
      out.feet[s] = {
        via: src, toeDir: flat.toArray().map(v => +v.toFixed(3)),
        yawVsPlusZ: yawDeg(flat),
        footPos: fp.toArray().map(v => +v.toFixed(3)),
      };
    } else out.feet[s] = 'NO TOE REFERENCE';
  }
  return out;
}

function sourceFK(skel, clip, frac) {
  const raw = clip.userData.raw;
  const P = {}, par = {};
  for (const j of skel.joints) { P[j.name] = new THREE.Vector3().fromArray(j.rest); par[j.name] = j.parent; }
  const n = Math.max(...Object.values(raw.rot).map(a => a.length));
  const f = Math.min(n - 1, Math.floor(frac * n));
  const G = {}, X = {};
  for (const j of skel.joints) {
    const r = raw.rot[j.name];
    const q = new THREE.Quaternion();
    if (r && r.length) { const v = r[Math.min(f, r.length - 1)]; q.set(v[0], v[1], v[2], v[3]); }
    const p = par[j.name];
    if (p && G[p]) {
      q.premultiply(G[p]);
      X[j.name] = P[j.name].clone().sub(P[p]).applyQuaternion(G[p]).add(X[p]);
    } else X[j.name] = P[j.name].clone();
    G[j.name] = q;
  }
  const res = { frame: f, feet: {} };
  for (const s of ['Left', 'Right']) {
    const tipArr = (skel.foot_tip && skel.foot_tip[s + 'Foot']) || null;
    if (!tipArr) { res.feet[s] = 'no foot_tip'; continue; }
    const tipRest = new THREE.Vector3().fromArray(tipArr);
    const posedTip = tipRest.clone().sub(P[s + 'Foot']).applyQuaternion(G[s + 'Foot']).add(X[s + 'Foot']);
    const dir = posedTip.clone().sub(X[s + 'Foot']); dir.y = 0;
    res.feet[s] = { toeDir: dir.toArray().map(v => +v.toFixed(3)), yawVsPlusZ: yawDeg(dir) };
  }
  return res;
}

const json = parseGLB(glbPath);
const { root } = buildHierarchy(json);
console.log('REST:', JSON.stringify(measureFeet(root, 'rest')));

await loadT3Clips(THREE, bankId);
const skel = getT3Skeleton(bankId);
console.log('BANK FACING:', JSON.stringify(getT3BankFacing(bankId)), 'turned_180:', !!skel.turned_180);
const raw = getT3Clips(bankId);
const clips = retargetT3Clips(raw, bankId, root, THREE, modelKey);
if (!clips) { console.error('retarget returned null'); process.exit(1); }
const probeMixer = new THREE.AnimationMixer(root);
const actions = createT3Actions(probeMixer, clips, THREE);
const names = Object.keys(actions);
const pick = names.includes(actionName) ? actionName : names[0];
console.log('ACTION:', pick, 'of', names.length, 'actions');
const clip = actions[pick].getClip();
{
  const seen = {}, dups = [];
  for (const t of clip.tracks) { if (seen[t.name]) dups.push(t.name); seen[t.name] = 1; }
  let nan = 0; for (const t of clip.tracks) for (const v of t.values) if (!Number.isFinite(v)) { nan++; break; }
  console.log('TRACKS:', clip.tracks.length, 'duplicateNames:', JSON.stringify(dups), 'tracksWithNaN:', nan);
}
console.log('SOURCE FK stance @0%:', JSON.stringify(sourceFK(skel, raw[pick] || raw.stance, 0)));
console.log('SOURCE FK stance @40%:', JSON.stringify(sourceFK(skel, raw[pick] || raw.stance, 0.4)));

const mixer = new THREE.AnimationMixer(root);
const act = mixer.clipAction(clip);
act.setLoop(THREE.LoopRepeat, Infinity); act.enabled = true; act.setEffectiveWeight(1); act.play();
for (const frac of [0.0, 0.25, 0.4, 0.6, 0.99]) {
  mixer.setTime(clip.duration * frac);
  console.log(`POSED @${Math.round(frac * 100)}%:`, JSON.stringify(measureFeet(root, 'posed')));
}
