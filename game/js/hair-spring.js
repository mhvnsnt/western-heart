/* ============================================================
   WESTERN HEART — Spring-bone hair physics (browser / Three.js)

   WHY THIS EXISTS (owner order 2026-11-08): hair in Western Heart must
   be "rigged and active and alive with physics and reactions to gravity
   and wind" — for EVERY swappable hairstyle, not per-hair hacks.

   HOW THE SOURCE GAMES DO IT (what this mirrors):
   - Tekken 7 hair items (GRE teardown, pakchunk0 SK_CH_*_har_1p GLBs)
     carry the full character skeleton plus dedicated SWING bones:
     Lili's hair is weighted to 16 chains of `SWG_Hair_OPTnnn__swing`
     bones, Asuka's to `Hair_OPTnnn` chains, Heihachi's short hair to
     none (rigid — it follows the head, exactly like the game).
     In Tekken those swing bones are driven by the engine's physics
     asset (PA) spring simulation.
   - DAZ/Genesis hair (Parvati's Flora) is weighted to named section
     bones off the head (`back1>Back2`, `right1>Right2`,
     `bangsR_A1>BangsR_A2`, ...) — two-level chains with the same
     spring-joint semantics.
   - The SmutBase rigs use the same pattern again (backhair_0-2,
     AC_hair_A-D, hair01-hair06 chains).

   This module is the generic driver for that pattern — the industry-
   standard spring-bone solver (the VRM/UE "spring bone" formulation):
   every hair bone is a verlet particle at its tip, pulled by gravity
   and wind, held by a stiffness spring toward its animated (bind-
   relative) pose, distance-constrained to its parent, and pushed out
   of sphere colliders (head / shoulders). One system drives any hair
   part whose skeleton carries hair chains; rigid hair (no chains)
   simply follows the head bone, as in the source games.

   DISCOVERY (data-driven, no per-hair authoring):
   A bone is a hair bone when ANY of these hold:
     1. its name matches the source games' hair conventions
        (/hair/i, /^SWG_/ swing bones, DAZ section names), or
     2. it descends from a head bone, is actually weighted by the hair
        mesh (skinIndex scan), and is not a face/body bone (blocklist
        built from the held T7 + GZM skeletons: brows, eyelids, lips,
        jaw, nose, cheeks, tongue, ...).
   Chains run root->leaf from each hair bone whose parent is not one.
   End bones (`*end`, `*__null`) are chain tips, simulated as joints
   whose own tip extrapolates one segment further.

   WIRING: fighter-depth.js attaches one system per fighter at fight
   build and steps it in the frame loop; customization-consumer.js
   attaches one to every hair part it equips (stored on
   fighter.userData.whHairSprings). Registry entries may carry a
   `physics` block ({stiffness, drag, gravityPower, windScale}) —
   values below are the defaults.

   DIVISION OF LABOUR with game/js/springbones.js (WHSpringBones):
   that system drives secondary motion on WH-AUTHORED rigs — breast /
   butt / belly / cloth chains and hair chains baked through the
   Blender Wiggle-2 pipeline, discovered by its jiggle name patterns.
   This system drives IMPORTED GAME HAIR (Tekken / DAZ / SmutBase
   bone conventions + skin-weight evidence) and adds the wind term
   the owner ordered. The two never write the same bone: discovery
   here refuses bones matching the authored-rig jiggle patterns
   (/jiggle|ponytail/i), which remain WHSpringBones' territory.
   ============================================================ */

const HAIR_NAME = /hair|swg_/i;
const DAZ_SECTION = /^(back|bangs|front|side|left|right|cap)\w*\d*$/i;
const FACE_BLOCK = /mayu|eye|mabuta|lip|jaw|hana|hoho|chobo|bero|tongue|teeth|mouth|nose|brow|lid|cheek|ear_|labia|gaze|face|__offset|__group/i;
const HEAD_NAME = /^(head|neck)/i;

import * as THREE from 'three';

const tmpA = new THREE.Vector3();
const tmpB = new THREE.Vector3();
const tmpC = new THREE.Vector3();
const tmpQ = new THREE.Quaternion();
const tmpQ2 = new THREE.Quaternion();

const AUTHORED_JIGGLE = /jiggle|ponytail/i; // WHSpringBones territory — never claimed here

function isHairBoneByName(name) {
  if (!name) return false;
  if (FACE_BLOCK.test(name)) return false;
  if (AUTHORED_JIGGLE.test(name)) return false;
  if (HAIR_NAME.test(name)) return true;
  if (name === 'back') return false; // GZM spine helper, not a hair section
  return DAZ_SECTION.test(name);
}

function descendsFromHead(bone) {
  let p = bone.parent;
  while (p) { if (p.isBone && HEAD_NAME.test(p.name)) return true; p = p.parent; }
  return false;
}

/* Collect the set of joint indices actually used by a skinned mesh. */
function usedJointIndices(mesh) {
  const used = new Set();
  const attr = mesh.geometry && mesh.geometry.getAttribute('skinIndex');
  if (!attr) return used;
  for (let i = 0; i < attr.count; i++) {
    used.add(attr.getX(i)); used.add(attr.getY(i));
    used.add(attr.getZ(i)); used.add(attr.getW(i));
  }
  return used;
}

/* Discover hair chains under `root`.
   Returns [{ joints: [Bone, ...] }] root->leaf ordered. */
export function discoverHairChains(root, opts = {}) {
  const chains = [];
  const hairBones = new Set();
  root.updateMatrixWorld(true);
  root.traverse((o) => {
    if (!o.isSkinnedMesh || !o.skeleton) return;
    const used = usedJointIndices(o);
    const bones = o.skeleton.bones;
    bones.forEach((bone, idx) => {
      if (FACE_BLOCK.test(bone.name)) return;
      if (!descendsFromHead(bone)) return;
      if (isHairBoneByName(bone.name)) { hairBones.add(bone); return; }
      if (AUTHORED_JIGGLE.test(bone.name)) return; // authored-rig chain: WHSpringBones owns it
      // Carrier bones (head / neck themselves) are weighted by every
      // hair cap and face mesh, but they are NOT hair joints — the head
      // must never be aimed by the solver. Only weighted non-carrier
      // descendants qualify by use.
      if (HEAD_NAME.test(bone.name)) return;
      if (used.has(idx)) hairBones.add(bone);
    });
  });
  // chains: start at hair bones whose parent is not a hair bone
  for (const bone of hairBones) {
    if (bone.parent && hairBones.has(bone.parent)) continue;
    // walk down: follow hair-bone children (branch = its own chain)
    const stack = [[bone, []]];
    while (stack.length) {
      const [cur, prefix] = stack.pop();
      const path = [...prefix, cur];
      const kids = (cur.children || []).filter((c) => c.isBone && hairBones.has(c));
      if (!kids.length) { chains.push(path); continue; }
      for (const k of kids) stack.push([k, path]);
    }
  }
  return chains.map((joints) => ({ joints }));
}

class HairJoint {
  constructor(bone, tipLocal, tipLen) {
    this.bone = bone;
    this.tipLocal = tipLocal;       // tip position in bone-local space (bind)
    this.tipLen = tipLen;           // |tipLocal|
    this.cur = new THREE.Vector3(); // world tip (simulated)
    this.prev = new THREE.Vector3();
    this.init = false;
  }
}

export class HairSpringSystem {
  /* opts: { stiffness 0..1 (pull to animated pose per step at 60Hz),
             drag 0..1 (velocity kept), gravityPower (multiplier),
             gravity (Vector3, default (0,-9.8,0)),
             wind (Vector3 or fn(t)->Vector3), windScale,
             colliders: [{bone|name, radius, offset:Vector3}],
             maxDistance (LOD sleep distance), substeps } */
  constructor(root, opts = {}) {
    this.root = root;
    this.stiffness = opts.stiffness ?? 0.55;
    this.drag = opts.drag ?? 0.28;
    this.gravityPower = opts.gravityPower ?? 1.0;
    this.gravity = opts.gravity ? opts.gravity.clone() : new THREE.Vector3(0, -9.8, 0);
    this.wind = opts.wind || null;
    this.windScale = opts.windScale ?? 1.0;
    this.maxDistance = opts.maxDistance ?? 24;
    this.substeps = opts.substeps ?? 2;
    this.time = 0;
    this.chains = [];
    this.colliders = (opts.colliders || []).map((c) => ({ ...c, center: new THREE.Vector3() }));
    if (!opts.colliders) {
      // default: a head sphere on the first head-named bone we find
      let head = null;
      root.traverse((o) => { if (!head && o.isBone && /^head$/i.test(o.name)) head = o; });
      if (head) this.colliders = [{ bone: head, radius: 0.115, offset: new THREE.Vector3(0, 0.03, 0), center: new THREE.Vector3() }];
    }
    const found = discoverHairChains(root, opts);
    root.updateMatrixWorld(true);
    for (const { joints } of found) {
      const chain = [];
      joints.forEach((bone, i) => {
        const next = joints[i + 1];
        let tipLocal, tipLen;
        if (next) {
          tipLocal = next.position.clone();
          tipLen = tipLocal.length();
        } else {
          // end joint: extrapolate along its own bind direction
          const parent = joints[i - 1];
          if (parent) {
            tipLocal = bone.position.clone();
            tipLen = Math.max(tipLocal.length(), 0.02);
            tipLocal.normalize().multiplyScalar(tipLen);
          } else {
            tipLocal = new THREE.Vector3(0, -0.05, 0); tipLen = 0.05;
          }
        }
        chain.push(new HairJoint(bone, tipLocal, tipLen));
      });
      if (chain.length) this.chains.push(chain);
    }
    this.count = this.chains.reduce((n, c) => n + c.length, 0);
  }

  get active() { return this.count > 0; }

  _colliderCenters() {
    for (const c of this.colliders) {
      const src = c.bone || (c.name ? this.root.getObjectByName(c.name) : null);
      if (!src) continue;
      src.getWorldPosition(c.center);
      if (c.offset) c.center.add(c.offset);
    }
  }

  /* dt seconds; env: { cameraPos } for LOD. Call AFTER the pose
     (animation / socket attach) has been applied for this frame. */
  update(dt, env = {}) {
    if (!this.active) return;
    if (env.wind !== undefined) this.wind = env.wind;
    if (env.cameraPos && this.root.getWorldPosition(tmpA).distanceTo(env.cameraPos) > this.maxDistance) return;
    dt = Math.min(dt, 1 / 30);
    const steps = this.substeps;
    const h = dt / steps;
    for (let s = 0; s < steps; s++) { this.time += h; this._step(h); }
  }

  _step(h) {
    const wind = typeof this.wind === 'function' ? this.wind(this.time) : this.wind;
    this._colliderCenters();
    for (const chain of this.chains) {
      for (const j of chain) {
        const bone = j.bone;
        bone.updateWorldMatrix(true, false);
        const jointWorld = bone.getWorldPosition(tmpA);
        // animated target tip (where the pose alone would put it)
        const target = tmpB.copy(j.tipLocal).applyQuaternion(bone.getWorldQuaternion(tmpQ)).add(jointWorld);
        if (!j.init) { j.cur.copy(target); j.prev.copy(target); j.init = true; }
        // verlet integration
        const vx = (j.cur.x - j.prev.x) * (1 - this.drag);
        const vy = (j.cur.y - j.prev.y) * (1 - this.drag);
        const vz = (j.cur.z - j.prev.z) * (1 - this.drag);
        j.prev.copy(j.cur);
        j.cur.x += vx + (this.gravity.x * this.gravityPower + (wind ? wind.x * this.windScale : 0)) * h * h;
        j.cur.y += vy + (this.gravity.y * this.gravityPower + (wind ? wind.y * this.windScale : 0)) * h * h;
        j.cur.z += vz + (this.gravity.z * this.gravityPower + (wind ? wind.z * this.windScale : 0)) * h * h;
        // stiffness spring toward the animated pose
        j.cur.lerp(target, this.stiffness);
        // distance constraint to the joint origin
        tmpC.copy(j.cur).sub(jointWorld);
        const d = tmpC.length() || 1e-6;
        j.cur.copy(jointWorld).addScaledVector(tmpC, j.tipLen / d);
        // sphere colliders
        for (const c of this.colliders) {
          tmpC.copy(j.cur).sub(c.center);
          const cd = tmpC.length();
          if (cd > 1e-6 && cd < c.radius) j.cur.copy(c.center).addScaledVector(tmpC, c.radius / cd);
        }
        // aim the bone at its simulated tip
        const curDir = tmpC.copy(j.cur).sub(jointWorld).normalize();
        const restDir = tmpB.copy(j.tipLocal).normalize().applyQuaternion(bone.getWorldQuaternion(tmpQ));
        tmpQ2.setFromUnitVectors(restDir, curDir);
        const newWorld = tmpQ2.multiply(bone.getWorldQuaternion(tmpQ));
        const parent = bone.parent;
        if (parent && parent.isBone) {
          parent.getWorldQuaternion(tmpQ);
          bone.quaternion.copy(tmpQ.invert().multiply(newWorld));
        } else {
          bone.quaternion.copy(newWorld);
        }
        bone.updateWorldMatrix(false, false);
      }
    }
  }
}

/* Attach a spring system to any loaded part/character root.
   Returns null for rigid hair (no chains) — the correct source-game
   behaviour for short/rigid styles. Fail-silent by design: physics
   must never break a fight or a suite session. */
export function attachHairPhysics(root, opts = {}) {
  try {
    const sys = new HairSpringSystem(root, opts);
    return sys.active ? sys : null;
  } catch (e) {
    console.warn('[WH-HAIR] attachHairPhysics failed:', e && e.message || e);
    return null;
  }
}
