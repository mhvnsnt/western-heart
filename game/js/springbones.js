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
    // Production hair / cloth (2026-11-01, TressFX-style): stiffness falls from the root (holds the style) to the tip
    // (flows); fixed substeps keep fast moves stable; body colliders (spheres / capsules on the fighter's own bones)
    // keep strands and cloth outside the head, neck, chest, shoulders, arms and thighs. Defaults reproduce the old
    // single-step, collider-free behaviour, so existing jiggle chains (breast / glutes) are unchanged.
    this.stiffnessTip = opts.stiffnessTip ?? this.stiffness;
    this.substeps = Math.max(1, opts.substeps ?? 1);
    this.colliders = opts.colliders || [];     // [{ bone, radius, up?: m along the bone's +Y, tailBone? (capsule) }]
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
    const frame = Math.min(dt, 1 / 30), n = this.substeps, dtc = frame / n;
    const damp = Math.pow(Math.max(0, 1 - this.dragForce), 1 / n);
    const g = this.gravityPower * frame * frame * 60 * 0.02 * this.scale / n; // same pull per frame for any substeps
    const cols = this.colliders.length ? this._colliderShapes() : null;
    for (let s = 0; s < n; s++) {
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
        // Stiffness: pull toward rest offset from head (root -> tip falloff)
        const k = this.bones.length > 1 ? i / (this.bones.length - 1) : 0;
        const stiff = this.stiffness + (this.stiffnessTip - this.stiffness) * k;
        const target = t.head.clone().add(this._restOffset(i));
        t.cur.lerp(target, 1 - Math.exp(-stiff * 8 * dtc));
        // Gravity
        t.cur.addScaledVector(this.gravityDir, g);
        this._keepLength(t);
        // collide <-> length, ending on length: strands never stretch; any residual contact is millimetres
        if (cols) for (let it = 0; it < 3; it++) { this._collide(t.cur, cols); this._keepLength(t); }
        // Solve bone rotation to aim at the simulated tail
        this._aimBone(b, t.head, t.cur, i);
      }
    }
  }

  _keepLength(t) {
    const dir = t.cur.clone().sub(t.head);
    if (dir.lengthSq() < 1e-12) dir.set(0, -1, 0);
    t.cur.copy(t.head).addScaledVector(dir.normalize(), t.len);
  }

  /** World spheres / capsules of this chain's colliders for the current pose: [{a, b, r}] (b === a: sphere). */
  _colliderShapes() {
    const out = [];
    for (const c of this.colliders) {
      if (!c.bone) continue;
      c.bone.updateWorldMatrix(true, false);
      const a = new THREE.Vector3();
      c.bone.getWorldPosition(a);
      if (c.up) {
        const q = new THREE.Quaternion();
        c.bone.getWorldQuaternion(q);
        a.addScaledVector(new THREE.Vector3(0, 1, 0).applyQuaternion(q), c.up);
      }
      let b = a;
      if (c.tailBone) {
        c.tailBone.updateWorldMatrix(true, false);
        b = new THREE.Vector3();
        c.tailBone.getWorldPosition(b);
      }
      out.push({ a, b, r: c.radius });
    }
    return out;
  }

  _collide(p, cols) {
    const r0 = this.hitRadius * this.scale;
    for (const c of cols) {
      const ab = c.b.clone().sub(c.a), L = ab.lengthSq();
      const u = L > 1e-12 ? Math.min(1, Math.max(0, p.clone().sub(c.a).dot(ab) / L)) : 0;
      const q = c.a.clone().addScaledVector(ab, u);
      const d = p.clone().sub(q), dist = d.length(), min = c.r + r0;
      if (dist < min) p.copy(q).addScaledVector(dist > 1e-9 ? d.divideScalar(dist) : new THREE.Vector3(0, 0, -1), min);
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

/* Per-family defaults (2026-11-01). Hair: TressFX-style global shape stiffness falling root -> tip, light gravity.
   Cloth (capes, robes, coat tails, straps): the cape-cloth.js tuning (stiffness 0.95 -> 0.5, heavier drag). */
const FAMILY = {
  hair: { stiffness: 0.92, stiffnessTip: 0.3, dragForce: 0.3, gravityPower: 0.45, hitRadius: 0.012, substeps: 3 },
  cloth: { stiffness: 0.95, stiffnessTip: 0.5, dragForce: 0.35, gravityPower: 0.6, hitRadius: 0.02, substeps: 3 },
};

const _bone = (root, n) => {
  let hit = null;
  root.traverse((o) => { if (!hit && o.isBone && o.name.split(':').pop() === n) hit = o; });
  return hit;
};

/** Body colliders from the fighter's own skeleton, sized by its height (Hips -> Head x 2.9): head sphere, neck,
    chest, shoulder and upper-arm capsules, and thigh capsules (`leg`, used by cloth only). */
export function bodyColliders(root) {
  const B = (n) => _bone(root, n);
  const hips = B('Hips'), head = B('Head');
  if (!hips || !head) return [];
  const a = new THREE.Vector3(), b = new THREE.Vector3();
  hips.getWorldPosition(a); head.getWorldPosition(b);
  const H = a.distanceTo(b) * 2.9; // hips -> head joint is ~1/3 of standing height
  const out = [];
  const add = (bone, radius, extra = {}) => { if (bone) out.push(Object.assign({ bone, radius }, extra)); };
  add(head, 0.065 * H, { up: 0.055 * H });
  add(B('Neck'), 0.035 * H, { tailBone: head });
  add(B('Spine1') || B('Spine'), 0.09 * H, { tailBone: B('Spine2') || B('Neck') });
  for (const s of ['Left', 'Right']) {
    add(B(s + 'Shoulder'), 0.04 * H, { tailBone: B(s + 'Arm') });
    add(B(s + 'Arm'), 0.032 * H, { tailBone: B(s + 'ForeArm') });
    add(B(s + 'UpLeg'), 0.055 * H, { tailBone: B(s + 'Leg'), leg: true });
  }
  return out;
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
    let colliders = null;
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
          : /hair|ponytail/i.test(chainRoot.name) ? 'hair'
          : /cape|cloak|robe|coat|skirt|strap|tassel/i.test(chainRoot.name) ? 'cloth' : 'generic';
        const preset = Object.assign({}, FAMILY[fam] || {}, (opts.presets && opts.presets[fam]) || {});
        const body = (fam === 'hair' || fam === 'cloth') ? (colliders || (colliders = bodyColliders(root))) : [];
        this.chains.push(new SpringChain(chain, {
          stiffness: preset.stiffness ?? 0.9,
          stiffnessTip: preset.stiffnessTip,
          dragForce: preset.dragForce ?? 0.35,
          gravityPower: preset.gravityPower ?? (fam === 'hair' ? 0.35 : 0.6),
          hitRadius: preset.hitRadius ?? 0.06,
          substeps: preset.substeps,
          colliders: fam === 'cloth' ? body : body.filter((c) => !c.leg),
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
