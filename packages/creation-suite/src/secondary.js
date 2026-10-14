// Size-adaptive secondary physics: generates spring ("jiggle") bones per
// character from its measured body size, re-skins the region's vertices onto
// them, and simulates a damped spring each frame. Same idea as VRM
// springBone (MIT, pixiv/three-vrm) but generated, not authored, so every
// Tripo model gets it automatically. Hair/cloth chains use the same spring.
import * as THREE from 'three';
import { REGIONS, physicsFor, familyOf, regionAmount } from './regions.js';
import { boneByName, measureGirth, prepareBody } from './body.js';

// reference girths (m) of an average adult; mass scales with (girth/ref)^3
const REF_GIRTH = { belly: 0.15, chest: 0.15, glute: 0.12, thigh: 0.08 };
// chest/glute springs also need the slider pushed (so a flat male chest never bounces)
const NEEDS_SLIDER = { chest: 0.25, glute: 0.25 };

export function buildSecondaryRig(root, { regions = Object.keys(REGIONS), share = 0.85, sliders = {} } = {}) {
  const springs = [];
  for (const mesh of prepareBody(root)) {
    if (mesh.userData.csSprings) { springs.push(...mesh.userData.csSprings); continue; }
    const sk = mesh.skeleton, cs = mesh.userData.cs;
    const bones = sk.bones.slice(), inverses = sk.boneInverses.slice();
    const si = mesh.geometry.attributes.skinIndex, sw = mesh.geometry.attributes.skinWeight;
    const local = [];
    for (const name of regions) {
      const def = REGIONS[name]; if (!def?.jiggle || !cs.frames[name]) continue;
      const fam = familyOf(name);
      if (NEEDS_SLIDER[fam] && regionAmount(def, sliders) < NEEDS_SLIDER[fam]) continue;
      const girth = measureGirth(mesh, name);
      const phys = physicsFor(name, girth, REF_GIRTH[fam] || girth);
      if (!phys) continue;
      const parent = boneByName(sk, def.parent); if (!parent) continue;
      const f = cs.frames[name];
      const bone = new THREE.Bone(); bone.name = 'cs_jiggle_' + name;
      // place bone at region centre in parent space (bind pose)
      const pIdx = sk.bones.indexOf(parent);
      const parentBind = new THREE.Matrix4().copy(sk.boneInverses[pIdx]).invert();
      const centreInParent = f.c.clone().applyMatrix4(sk.boneInverses[pIdx]);
      const pScale = new THREE.Vector3(); parentBind.decompose(new THREE.Vector3(), new THREE.Quaternion(), pScale);
      bone.position.copy(centreInParent); parent.add(bone);
      const inv = new THREE.Matrix4().makeTranslation(-f.c.x, -f.c.y, -f.c.z);
      // bind matrix of new bone = parentBind * T(centreInParent) => world translation f.c when parent unrotated in bind; keep exact:
      const boneBind = parentBind.clone().multiply(new THREE.Matrix4().makeTranslation(centreInParent.x, centreInParent.y, centreInParent.z));
      inv.copy(boneBind).invert();
      const bi = bones.length; bones.push(bone); inverses.push(inv);
      // reweight: move share*falloff of each vertex onto the spring bone
      const w = cs.weights[name];
      for (let i = 0; i < w.length; i++) {
        const k = w[i] * share; if (k < 0.02) continue;
        const idx = [si.getX(i), si.getY(i), si.getZ(i), si.getW(i)], wt = [sw.getX(i), sw.getY(i), sw.getZ(i), sw.getW(i)];
        let slot = wt.indexOf(Math.min(...wt));
        const exist = idx.findIndex((x, j) => x === bi && wt[j] > 0); if (exist >= 0) slot = exist;
        for (let j = 0; j < 4; j++) wt[j] *= (1 - k);
        wt[slot] += k; idx[slot] = bi;
        const s = wt.reduce((a, b) => a + b, 0);
        si.setXYZW(i, ...idx); sw.setXYZW(i, ...wt.map(x => x / s));
      }
      local.push({ name, bone, parent, rest: bone.position.clone(), girth, ...phys,
        pos: null, vel: new THREE.Vector3(), offset: new THREE.Vector3() });
    }
    si.needsUpdate = sw.needsUpdate = true;
    const skel = new THREE.Skeleton(bones, inverses);
    mesh.bind(skel, mesh.bindMatrix);
    mesh.userData.csSprings = local; springs.push(...local);
  }
  return new SpringSystem(springs);
}

const _t = new THREE.Vector3(), _a = new THREE.Vector3(), _q = new THREE.Quaternion();
export class SpringSystem {
  constructor(springs) { this.springs = springs; this.gravity = new THREE.Vector3(0, -9.8, 0); }
  // call after animation / bone poses are set, before render
  update(dt) {
    dt = Math.min(dt, 1 / 30);
    for (const s of this.springs) {
      s.bone.position.copy(s.rest);
      s.bone.updateMatrixWorld(true);
      _t.setFromMatrixPosition(s.bone.matrixWorld); // where the region wants to be
      if (!s.pos) { s.pos = _t.clone(); continue; }
      // F = -k x - c v + m g(small sag)
      _a.subVectors(_t, s.pos).multiplyScalar(s.stiffness).addScaledVector(s.vel, -s.damping).addScaledVector(this.gravity, 0.15);
      s.vel.addScaledVector(_a, dt); s.pos.addScaledVector(s.vel, dt);
      s.offset.subVectors(s.pos, _t);
      if (s.offset.length() > s.maxOffset) { s.offset.setLength(s.maxOffset); s.pos.addVectors(_t, s.offset); }
      // world offset -> parent-local
      s.parent.getWorldQuaternion(_q).invert();
      const ws = new THREE.Vector3(); s.parent.getWorldScale(ws);
      const lo = s.offset.clone().applyQuaternion(_q).divide(ws);
      s.bone.position.copy(s.rest).add(lo);
    }
  }
}
