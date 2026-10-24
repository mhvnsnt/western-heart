// POSE DUMP — evaluate the game's real t3anims path at a clip fraction and
// dump posed bone world matrices (for bake_pose.py) + feet measurements.
// usage: GAME_ROOT=<dir with game/> node pose_dump.mjs <glbPath> <bankId> <modelKey> <action> <frac> <outJson>
import fs from 'fs';
const GAME_ROOT = process.env.GAME_ROOT || process.env.HOME + '/workspace/_docfrank-feet/wh';
const THREE = await import(`file://${GAME_ROOT}/game/vendor/three.module.js`);
const T3 = await import(`file://${GAME_ROOT}/game/js/t3anims.js`);
const { loadT3Clips, getT3Clips, retargetT3Clips, createT3Actions, canonBoneName } = T3;

const [,, glbPath, bankId, modelKey, actionName = 'stance', fracS = '0.4', outJson] = process.argv;
const frac = parseFloat(fracS);

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

const json = parseGLB(glbPath);
const { root, objs } = buildHierarchy(json);
const bindMeshWorlds = {};
json.nodes.forEach((n, i) => {
  if (n.mesh !== undefined && n.skin !== undefined)
    bindMeshWorlds[i] = objs[i].matrixWorld.elements.map(v => +v.toFixed(6));
});

await loadT3Clips(THREE, bankId);
const raw = getT3Clips(bankId);
const clips = retargetT3Clips(raw, bankId, root, THREE, modelKey);
if (!clips) { console.error('retarget returned null'); process.exit(1); }
const probeMixer = new THREE.AnimationMixer(root);
const actions = createT3Actions(probeMixer, clips, THREE);
const names = Object.keys(actions);
const pick = names.includes(actionName) ? actionName : names[0];
const clip = actions[pick].getClip();
if (!process.env.REST) {
  const mixer = new THREE.AnimationMixer(root);
  const act = mixer.clipAction(clip);
  act.setLoop(THREE.LoopRepeat, Infinity); act.enabled = true; act.setEffectiveWeight(1); act.play();
  mixer.setTime(clip.duration * frac);
}
root.updateMatrixWorld(true);

const wp = (o) => { const v = new THREE.Vector3(); o.getWorldPosition(v); return v; };
const yawDeg = (v) => +THREE.MathUtils.radToDeg(Math.atan2(v.x, v.z)).toFixed(1);
const by = {};
root.traverse(o => { if (o.isBone) { const c = canonBoneName(o.name); if (c && !by[c]) by[c] = o; } });
const feet = {};
for (const s of ['Left', 'Right']) {
  const f = by[s + 'Foot'], t = by[s + 'ToeBase'];
  if (f && t) {
    const d = wp(t).sub(wp(f)); d.y = 0;
    feet[s] = { toeYawVsPlusZ: yawDeg(d), footPos: wp(f).toArray().map(v => +v.toFixed(3)) };
  }
}
let nanBones = 0;
const worlds = {};
root.traverse(o => {
  if (o.isBone) {
    worlds[o.name] = o.matrixWorld.elements.map(v => +v.toFixed(6));
    if (!o.matrixWorld.elements.every(Number.isFinite)) nanBones++;
  }
});
fs.writeFileSync(outJson, JSON.stringify({ glb: glbPath, bank: bankId, modelKey, clip: pick, frac, feet, nanBones, worlds, bindMeshWorlds }));
console.log(JSON.stringify({ clip: pick, frac, feet, nanBones }));
