/* ============================================================
   WESTERN HEART — WHSpringBones (runtime jiggle / secondary motion)
   WH-original verlet spring-chain solver with VRM-springbone-compatible
   parameters (stiffness, dragForce, gravityPower, hitRadius), so chains
   authored in the Blender Wiggle-2 pipeline map 1:1 to runtime values.

   Pipeline side (bake): tools/jiggle/ (Wiggle 2, Blender).
   Runtime side (this file): live jiggle on the real jiggle bones —
   DEF-breast.L/R, Butt_L/R chains, hair/cloth chains — driven every
   frame after the animation update, exactly like VRM spring bones.

   Loaded lazily by game/js/integration.js. No dependencies.
   ============================================================ */

import * as THREE from 'three';

/* Name patterns that identify jiggle chains on WH rigs.
   GameRig/Blender names first, then common variants. */
const CHAIN_PATTERNS = [
  /breast/i, /bust/i, /mammary/i,
  /butt/i, /glute/i, /hip_jiggle/i,
  /belly/i, /stomach_jiggle/i,
  /thigh_jiggle/i, /ponytail/i, /hair_jiggle/i,
  /jiggle/i,
];

export class SpringChain {
  constructor(bones, opts = {}) {
    this.bones = bones;                       // ordered root → tip (tip = end site)
    this.stiffness = opts.stiffness ?? 0.9;   // spring pull to rest
    this.dragForce = opts.dragForce ?? 0.35;   // velocity damping
    this.gravityPower = opts.gravityPower ?? 0.6;
    this.gravityDir = opts.gravityDir ?? new THREE.Vector3(0, -1, 0);
    this.hitRadius = opts.hitRadius ?? 0.06;
    this.scale = opts.scale ?? 1.0;            // global jiggle amplitude scale
    this._tails = [];                          // verlet state per joint
    this._restLocal = [];
    this._init();
  }

  _init() {
    const v = new THREE.Vector3();
    this.bones.forEach((b, i) => {
      b.updateWorldMatrix(true, false);
      // Rest tail = child position, or bone pos + bone dir * avg length at tip.
      let tail;
      if (i < this.bones.length - 1) {
        tail = new THREE.Vector3();
        this.bones[i + 1].getWorldPosition(tail);
      } else {
        const dir = new THREE.Vector3();
        b.getWorldPosition(v);
        b.getWorldDirection(dir);
        const len = this._tails.length
          ? this._tails[this._tails.length - 1].len : 0.12;
        tail = v.clone().addScaledVector(dir, len || 0.12);
      }
      const head = new THREE.Vector3();
      b.getWorldPosition(head);
      this._tails.push({
        prev: tail.clone(), cur: tail.clone(),
        head, len: tail.distanceTo(head),
      });
      this._restLocal.push(b.quaternion.clone());
    });
  }

  update(dt, time) {
    const dtc = Math.min(dt, 1 / 30);
    const damp = Math.max(0, 1 - this.dragForce);
    for (let i = 0; i < this.bones.length; i++) {
      const b = this.bones[i], t = this._tails[i];
      b.updateWorldMatrix(true, false);
      const head = new THREE.Vector3();
      b.getWorldPosition(head);
      t.head.copy(head);
      // Verlet: velocity = (cur - prev) * damping
      const vel = t.cur.clone().sub(t.prev).multiplyScalar(damp);
      t.prev.copy(t.cur);
      t.cur.add(vel);
      // Stiffness: pull toward rest offset from head
      const restOffset = this._restOffset(i);
      const target = t.head.clone().add(restOffset);
      t.cur.lerp(target, 1 - Math.exp(-this.stiffness * 8 * dtc));
      // Gravity
      t.cur.addScaledVector(this.gravityDir, this.gravityPower * dtc * dtc * 60 * 0.02 * this.scale);
      // Length constraint: keep segment length
      const dir = t.cur.clone().sub(t.head);
      const d = dir.length() || 1e-6;
      t.cur.copy(t.head).addScaledVector(dir.normalize(), t.len);
      // Solve bone rotation to aim at the simulated tail
      this._aimBone(b, t.head, t.cur, i);
    }
  }

  _restOffset(i) {
    // Rest direction of joint i in parent space → world offset from head.
    const b = this.bones[i];
    const dir = new THREE.Vector3(0, 1, 0);
    if (i < this.bones.length - 1) {
      // direction to next bone in rest pose
      const a = new THREE.Vector3(), c = new THREE.Vector3();
      b.getWorldPosition(a);
      this.bones[i + 1].getWorldPosition(c);
      dir.copy(c.sub(a));
    } else if (i > 0) {
      const a = new THREE.Vector3(), p = new THREE.Vector3();
      b.getWorldPosition(a);
      this.bones[i - 1].getWorldPosition(p);
      dir.copy(a.sub(p));
    }
    const len = this._tails[i].len;
    return dir.normalize().multiplyScalar(len * this.scale);
  }

  _aimBone(bone, headWorld, tailWorld, idx) {
    // Rotate the bone so its +Y axis points at the simulated tail.
    const m = new THREE.Matrix4().lookAt(headWorld, tailWorld, new THREE.Vector3(0, 0, 1));
    const q = new THREE.Quaternion().setFromRotationMatrix(m);
    const parentQ = new THREE.Quaternion();
    if (bone.parent) bone.parent.getWorldQuaternion(parentQ);
    parentQ.invert();
    const local = parentQ.multiply(q);
    // three.js bones point +Y along their length; lookAt aims -Z → rotate.
    const fix = new THREE.Quaternion().setFromEuler(new THREE.Euler(Math.PI / 2, 0, 0));
    bone.quaternion.copy(local.multiply(fix));
    // Blend back toward rest so chains never collapse fully.
    bone.quaternion.slerp(this._restLocal[idx], 0.15);
  }
}

export class WHSpringBones {
  constructor() {
    this.chains = [];
    this.enabled = true;
    this.globalScale = 1.0;
  }

  /** Scan a skinned mesh / skeleton for jiggle chains and build solvers.
      Returns the number of chains found. */
  autoDiscover(root, opts = {}) {
    const bones = [];
    root.traverse((o) => { if (o.isBone) bones.push(o); });
    const byName = new Map(bones.map((b) => [b.name, b]));
    const used = new Set();
    let found = 0;
    for (const b of bones) {
      if (used.has(b.name)) continue;
      if (!CHAIN_PATTERNS.some((re) => re.test(b.name))) continue;
      // Walk up to the chain root: highest ancestor that also matches.
      let chainRoot = b;
      while (chainRoot.parent && chainRoot.parent.isBone &&
             CHAIN_PATTERNS.some((re) => re.test(chainRoot.parent.name)) &&
             !used.has(chainRoot.parent.name)) {
        chainRoot = chainRoot.parent;
      }
      // Walk down the longest matching descendant path.
      const chain = [chainRoot];
      used.add(chainRoot.name);
      let cur = chainRoot;
      for (;;) {
        const kids = cur.children.filter(
          (c) => c.isBone && !used.has(c.name) &&
                 CHAIN_PATTERNS.some((re) => re.test(c.name)));
        if (!kids.length) break;
        // Prefer the child whose name continues the chain (e.g. .01, _mid).
        kids.sort((a, c2) => a.name.length - c2.name.length);
        cur = kids[0];
        chain.push(cur);
        used.add(cur.name);
      }
      if (chain.length >= 1) {
        const fam = /breast|bust|mammary/i.test(chainRoot.name) ? 'mammary'
          : /butt|glute/i.test(chainRoot.name) ? 'glutes'
          : /belly|stomach/i.test(chainRoot.name) ? 'belly'
          : /hair|ponytail/i.test(chainRoot.name) ? 'hair' : 'generic';
        const preset = (opts.presets && opts.presets[fam]) || {};
        this.chains.push(new SpringChain(chain, {
          stiffness: preset.stiffness ?? 0.9,
          dragForce: preset.dragForce ?? 0.35,
          gravityPower: preset.gravityPower ?? (fam === 'hair' ? 0.35 : 0.6),
          hitRadius: preset.hitRadius ?? 0.06,
          scale: (opts.scale ?? 1) * this.globalScale,
        }));
        found++;
      }
    }
    return found;
  }

  /** Manually register a chain by bone names (for rigs with known chains). */
  addChainByNames(skeleton, names, opts = {}) {
    const bones = names.map((n) => skeleton.getBoneByName(n)).filter(Boolean);
    if (bones.length < 1) return null;
    const chain = new SpringChain(bones, opts);
    this.chains.push(chain);
    return chain;
  }

  update(dt, time) {
    if (!this.enabled) return;
    for (const c of this.chains) {
      c.scale = this.globalScale;
      c.update(dt, time);
    }
  }

  setAreaScale(family, scale) {
    // Called by the creation suite JIGGLE tab: per-area live tuning.
    for (const c of this.chains) c.scale = scale;
  }
}
