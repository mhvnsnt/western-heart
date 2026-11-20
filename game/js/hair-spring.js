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

   COLLISION (2026-11-09, owner collision order): the source
   games' spring solvers collide hair against the character's
   physics asset — fitted capsule/sphere colliders — plus a
   distance-field volume for the torso. opts.collision plugs in
   the shared collision core (game/js/collision.js): a posed
   capsule/sphere set fitted per character from the skinned bind
   pose (the PhAT pattern) and/or a baked BodySDF volume, with
   PBD friction so hair RESTS and DRAGS on shoulders instead of
   skating or sinking. Build one from baked data with
   collisionSetFromData(). Without opts.collision the legacy
   sphere colliders (opts.colliders, head-sphere default) apply,
   unchanged.

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
import {
  collideSphere as collideSphereFlat,
  collideCapsule as collideCapsuleFlat,
  applyContactFriction,
} from './collision.js';

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
    // shared collision core set (see header): posed per substep
    this.collision = opts.collision || null;
    this._posedSpheres = [];   // {c:Vector3, r, friction}
    this._posedCapsules = [];  // {a:Vector3, b:Vector3, r, friction}
    this._sdfToWorld = new THREE.Matrix4();
    this._sdfFromWorld = new THREE.Matrix4();
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

  /* Pose the shared collision set for this substep: capsule end
     points and sphere centres follow their bones (which may live
     on the BODY's skeleton — colliders are world-space); the SDF
     frame follows its bone from its bind pose. */
  _poseCollision() {
    const set = this.collision;
    if (!set) return;
    this._posedSpheres.length = 0;
    this._posedCapsules.length = 0;
    for (const s of set.spheres || []) {
      const c = s.bone.getWorldPosition(new THREE.Vector3());
      if (s.offset) c.add(tmpA.copy(s.offset).applyQuaternion(s.bone.getWorldQuaternion(tmpQ)));
      this._posedSpheres.push({ c, r: s.radius + (s.margin || 0), friction: s.friction ?? 0.35 });
    }
    for (const cp of set.capsules || []) {
      const a = cp.boneA.getWorldPosition(new THREE.Vector3());
      const b = cp.boneB.getWorldPosition(new THREE.Vector3());
      this._posedCapsules.push({ a, b, r: cp.radius + (cp.margin || 0), friction: cp.friction ?? 0.35 });
    }
    if (set.sdf) {
      this._sdfToWorld.copy(set.sdf.bone.matrixWorld).multiply(set.sdf.bindInv);
      this._sdfFromWorld.copy(this._sdfToWorld).invert();
    }
  }

  /* Collide one joint's simulated tip against the posed set:
     projection + PBD friction (resting contact). */
  _collideJoint(j) {
    const set = this.collision;
    const p = [j.cur.x, j.cur.y, j.cur.z];
    const prev = [j.prev.x, j.prev.y, j.prev.z];
    const n = [0, 0, 0];
    let touched = false;
    for (const s of this._posedSpheres) {
      if (collideSphereFlat(p, [s.c.x, s.c.y, s.c.z], s.r, n) > 0) {
        applyContactFriction(p, prev, n, s.friction); touched = true;
      }
    }
    for (const cp of this._posedCapsules) {
      if (collideCapsuleFlat(p, [cp.a.x, cp.a.y, cp.a.z], [cp.b.x, cp.b.y, cp.b.z], cp.r, n) > 0) {
        applyContactFriction(p, prev, n, cp.friction); touched = true;
      }
    }
    if (set.sdf) {
      tmpA.set(p[0], p[1], p[2]).applyMatrix4(this._sdfFromWorld);
      const lp = [tmpA.x, tmpA.y, tmpA.z];
      const depth = set.sdf.body.project(lp, set.sdf.margin || 0, 2);
      if (depth > 0) {
        tmpA.set(lp[0], lp[1], lp[2]).applyMatrix4(this._sdfToWorld);
        n[0] = tmpA.x - p[0]; n[1] = tmpA.y - p[1]; n[2] = tmpA.z - p[2];
        const nl = Math.hypot(n[0], n[1], n[2]);
        if (nl > 1e-9) { n[0] /= nl; n[1] /= nl; n[2] /= nl; }
        p[0] = tmpA.x; p[1] = tmpA.y; p[2] = tmpA.z;
        applyContactFriction(p, prev, n, set.sdf.friction ?? 0.35);
        touched = true;
      }
    }
    if (touched) {
      j.cur.set(p[0], p[1], p[2]);
      j.prev.set(prev[0], prev[1], prev[2]);
    }
  }

  _step(h) {
    const wind = typeof this.wind === 'function' ? this.wind(this.time) : this.wind;
    this._colliderCenters();
    this._poseCollision();
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
        // collision: shared core set when supplied, else the
        // legacy sphere colliders
        if (this.collision) {
          this._collideJoint(j);
        } else {
          for (const c of this.colliders) {
            tmpC.copy(j.cur).sub(c.center);
            const cd = tmpC.length();
            if (cd > 1e-6 && cd < c.radius) j.cur.copy(c.center).addScaledVector(tmpC, c.radius / cd);
          }
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

/* Build a live collision set (for opts.collision) from baked
   per-character data — the JSON written by
   tools/collision/bake-collision.mjs plus a loaded BodySDF.
   `bodyRoot` is the BODY's scene root (collider bones live there,
   not on the hair part). Call in bind pose: the SDF frame's bind
   inverse is captured from the frame bone's current world matrix.
   Returns null when a named bone is missing (fail-silent, like
   attach) — a character without baked data simply gets no set. */
export function collisionSetFromData(bodyRoot, data, sdfBody) {
  try {
    const bone = (name) => bodyRoot.getObjectByName(name);
    const spheres = [], capsules = [];
    for (const s of data.spheres || []) {
      const b = bone(s.bone);
      if (!b) return null;
      spheres.push({
        bone: b,
        offset: s.offset ? new THREE.Vector3(...s.offset) : undefined,
        radius: s.radius, margin: s.margin || 0, friction: s.friction,
      });
    }
    for (const c of data.capsules || []) {
      const a = bone(c.boneA), b = bone(c.boneB);
      if (!a || !b) return null;
      capsules.push({ boneA: a, boneB: b, radius: c.radius, margin: c.margin || 0, friction: c.friction });
    }
    let sdf = null;
    if (data.sdf && sdfBody) {
      const frame = bone(data.sdf.frameBone);
      if (!frame) return null;
      bodyRoot.updateMatrixWorld(true);
      const bindInv = frame.matrixWorld.clone().invert();
      sdf = { body: sdfBody, bone: frame, bindInv, margin: data.sdf.margin || 0, friction: data.sdf.friction };
    }
    return { spheres, capsules, sdf };
  } catch (e) {
    console.warn('[WH-HAIR] collisionSetFromData failed:', e && e.message || e);
    return null;
  }
}
