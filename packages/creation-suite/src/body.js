// Body sliders on a real skinned GLB (three.js). Tripo exports ship without
// morph targets, so regions are turned into procedural morph targets once at
// load (displace along the normal with a smooth ellipsoid falloff); authored
// morph targets with the same slider names (e.g. "belly") are used instead
// when the model has them.
import * as THREE from 'three';
import { REGIONS, regionAmount } from './regions.js';
import { SLIDERS } from './dna.js';

const _v = new THREE.Vector3(), _m = new THREE.Matrix4();

export function findSkinned(root) {
  const out = []; root.traverse(o => { if (o.isSkinnedMesh) out.push(o); }); return out;
}

export function boneByName(skeleton, name) {
  return skeleton.bones.find(b => b.name === name || b.name === `mixamorig:${name}` || b.name.toLowerCase() === name.toLowerCase());
}

// bind-space position of a bone (inverse of its inverse bind matrix)
export function bindPos(skeleton, bone) {
  const i = skeleton.bones.indexOf(bone);
  return new THREE.Vector3().setFromMatrixPosition(_m.copy(skeleton.boneInverses[i]).invert());
}

// +1 if the model faces +Z in bind space, -1 if -Z (Tripo exports vary): toes point forward.
export function facing(skeleton) {
  const f = boneByName(skeleton, 'LeftFoot'), t = boneByName(skeleton, 'LeftToeBase');
  if (!f || !t) return 1;
  return Math.sign(bindPos(skeleton, t).z - bindPos(skeleton, f).z) || 1;
}

// region ellipsoid in bind space
export function regionFrame(skeleton, def) {
  const A = boneByName(skeleton, def.a), B = boneByName(skeleton, def.b);
  if (!A || !B) return null;
  const pa = bindPos(skeleton, A), pb = bindPos(skeleton, B);
  const H = boneByName(skeleton, 'Hips'), Hd = boneByName(skeleton, 'Head');
  const len = H && Hd ? bindPos(skeleton, H).distanceTo(bindPos(skeleton, Hd)) : Math.max(0.1, pa.distanceTo(pb));
  const c = pa.clone().lerp(pb, def.t);
  if (def.drop) c.y -= def.drop * len;
  const r = new THREE.Vector3(...def.radius).multiplyScalar(len);
  const axis = c.clone(), front = (def.front || 0) * facing(skeleton);
  return { c, r, len, axis, front };
}

export function falloff(p, f, def) {
  const dx = (p.x - f.c.x) / f.r.x, dy = (p.y - f.c.y) / f.r.y, dz = f.front ? 0 : (p.z - f.c.z) / f.r.z;
  const d2 = dx * dx + dy * dy + dz * dz;
  if (d2 >= 1) return 0;
  if (f.front && Math.sign(p.z - f.axis.z) !== f.front) return 0;
  const s = 1 - d2; return s * s; // smooth
}

function boundPositions(mesh) {
  const pos = mesh.geometry.attributes.position, out = new Float32Array(pos.count * 3);
  for (let i = 0; i < pos.count; i++) { _v.fromBufferAttribute(pos, i).applyMatrix4(mesh.bindMatrix); _v.toArray(out, i * 3); }
  return out;
}

// Build procedural morph targets "cs_<region>" (idempotent).
export function prepareBody(root) {
  const meshes = findSkinned(root);
  for (const mesh of meshes) {
    if (mesh.userData.cs) continue;
    const g = mesh.geometry;
    if (!g.attributes.normal) g.computeVertexNormals();
    const P = boundPositions(mesh), N = g.attributes.normal, n = g.attributes.position.count;
    g.morphAttributes.position = g.morphAttributes.position || [];
    const frames = {}, weights = {};
    const p = new THREE.Vector3(), nn = new THREE.Vector3();
    for (const [name, def] of Object.entries(REGIONS)) {
      const f = regionFrame(mesh.skeleton, def); if (!f) continue;
      frames[name] = f;
      const w = new Float32Array(n), d = new Float32Array(n * 3);
      const amp = Math.min(f.r.x, f.r.y, f.r.z) * 0.6; // 1.0 slider = 60% of region radius
      for (let i = 0; i < n; i++) {
        p.fromArray(P, i * 3); const k = falloff(p, f, def); if (!k) continue;
        w[i] = k; nn.fromBufferAttribute(N, i).normalize();
        d[i * 3] = nn.x * k * amp; d[i * 3 + 1] = nn.y * k * amp * 0.5; d[i * 3 + 2] = nn.z * k * amp;
      }
      weights[name] = w;
      const attr = new THREE.BufferAttribute(d, 3); attr.name = 'cs_' + name;
      g.morphAttributes.position.push(attr);
    }
    g.morphTargetsRelative = true;
    mesh.updateMorphTargets();
    mesh.userData.cs = { frames, weights, bound: P, rest: new Map(mesh.skeleton.bones.map(b => [b, b.scale.clone()])) };
  }
  return meshes;
}

const BONE_MAP = {
  height: [['Hips', 'xyz']],
  torsoLen: [['Spine', 'y'], ['Chest', 'y']],
  armLen: [['LeftArm', 'xyz'], ['RightArm', 'xyz']],
  legLen: [['LeftUpLeg', 'y'], ['RightUpLeg', 'y']],
  shoulders: [['LeftShoulder', 'x'], ['RightShoulder', 'x']],
  headSize: [['Head', 'xyz']],
};

export function applySliders(root, sliders) {
  for (const mesh of prepareBody(root)) {
    const cs = mesh.userData.cs;
    for (const [name, def] of Object.entries(REGIONS)) {
      const authored = def.slider.find(s => mesh.morphTargetDictionary[s] !== undefined);
      const idx = mesh.morphTargetDictionary['cs_' + name];
      if (idx !== undefined) mesh.morphTargetInfluences[idx] = authored ? 0 : regionAmount(def, sliders);
    }
    for (const s of Object.keys(SLIDERS)) {
      const i = mesh.morphTargetDictionary[s]; if (i !== undefined) mesh.morphTargetInfluences[i] = sliders[s] || 0;
    }
    for (const [b, s] of cs.rest) b.scale.copy(s);
    for (const [key, list] of Object.entries(BONE_MAP)) {
      const v = sliders[key] || 0; if (!v) continue;
      for (const [bn, axes] of list) {
        const b = boneByName(mesh.skeleton, bn); if (!b) continue;
        for (const ax of axes) b.scale[ax] *= 1 + v;
      }
    }
  }
}

// Mean region girth (m) after sliders: drives the size-adaptive physics.
export function measureGirth(mesh, name) {
  const cs = mesh.userData.cs, f = cs.frames[name], w = cs.weights[name];
  const idx = mesh.morphTargetDictionary['cs_' + name];
  const d = mesh.geometry.morphAttributes.position[idx], inf = mesh.morphTargetInfluences[idx] || 0;
  let sum = 0, ws = 0;
  for (let i = 0; i < w.length; i++) {
    if (w[i] < 0.2) continue;
    const x = cs.bound[i * 3] + d.getX(i) * inf - f.axis.x, z = cs.bound[i * 3 + 2] + d.getZ(i) * inf - f.axis.z;
    sum += (f.front ? Math.abs(z) : Math.hypot(x, z)) * w[i]; ws += w[i];
  }
  return ws ? sum / ws : 0;
}
