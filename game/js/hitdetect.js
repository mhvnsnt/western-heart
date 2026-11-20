/* ============================================================
   WESTERN HEART — WHHitDetect (BVH precision hit-detection layer)
   Vendored: game/vendor/three-mesh-bvh/index.module.js (MIT).
   Loaded lazily by game/js/integration.js.

   The combat authority stays the sphere hitbox/hurtbox test in
   game/js/game.js `_resolveCombat`. This module adds the MESH-ACCURATE
   layer underneath it:

   1. `buildFighterBVH(fighterRoot)` — bakes each SkinnedMesh to a static
      posed geometry (StaticGeometryGenerator) and builds a BVH.
      Cached per model; rebuilt only when the model changes.
   2. `testLimbVsBody(att, def, limbBones)` — shapecast of the attacker's
      striking limb (capsule segment per bone) against the defender's BVH.
      Returns {hit, point, distance}.
   3. Verify mode (default ON): after every sphere-test hit, run the BVH
      test and log disagreements — this is the tuning instrument for the
      "only ~1/10 attacks land" playtest bug. It never changes outcomes.
   4. Authority mode (opt-in, needs a lane + proof): the BVH test becomes
      the hit authority for strikes.

   No dependencies beyond three + three-mesh-bvh.
   ============================================================ */

import * as THREE from 'three';

let BVH = null;
async function loadBVH() {
  if (BVH) return BVH;
  BVH = await import('three-mesh-bvh');
  return BVH;
}

/* Bone-name hints for striking limbs, per rig family. */
const LIMB_HINTS = {
  punch: [/hand[._-]r/i, /hand[._-]l/i, /fist/i, /lowerarm/i, /forearm/i],
  kick: [/foot[._-]r/i, /foot[._-]l/i, /shin/i, /lowerleg/i, /toe/i],
  elbow: [/elbow/i, /upperarm/i],
  knee: [/knee/i, /upperleg/i, /thigh/i],
  head: [/head/i],
};

export class WHHitDetect {
  constructor() {
    this.ready = false;
    this.mode = 'verify';      // 'verify' | 'authority' | 'off'
    this.cache = new Map();    // modelKey -> { bvh, meshes, updated }
    this.stats = { sphereHits: 0, bvhAgree: 0, bvhDisagree: 0 };
  }

  async init() {
    await loadBVH();
    this.ready = true;
    return this;
  }

  _modelKey(root) {
    return root.uuid || root.name || 'unknown';
  }

  /** Build (or fetch cached) BVH for a fighter's current posed meshes.
      The baked geometry is converted to ROOT-LOCAL space so the BVH stays
      valid while the fighter walks (body parts relative to root). The bake
      captures the pose at build time — call with {force:true} to re-bake
      (throttled by the caller; a 60k-tri build is ~50-200ms, so verify
      mode re-bakes at most on sphere-hit, never per frame). */
  async buildFighterBVH(fighterRoot, { force = false } = {}) {
    const M = await loadBVH();
    const key = this._modelKey(fighterRoot);
    if (!force && this.cache.has(key)) return this.cache.get(key);
    const skinned = [];
    fighterRoot.traverse((o) => { if (o.isSkinnedMesh) skinned.push(o); });
    if (!skinned.length) return null;
    const gen = new M.StaticGeometryGenerator(skinned);
    gen.attributes = ['position'];
    const baked = gen.generate();
    // generate() bakes with world transforms (applyWorldTransforms=true);
    // bring it into root-local space so it tracks the fighter.
    fighterRoot.updateWorldMatrix(true, true);
    baked.applyMatrix4(new THREE.Matrix4().copy(fighterRoot.matrixWorld).invert());
    baked.computeBoundsTree();
    const rec = { bvh: baked.boundsTree, baked, meshes: skinned, root: fighterRoot };
    this.cache.set(key, rec);
    return rec;
  }

  invalidate(fighterRoot) {
    this.cache.delete(this._modelKey(fighterRoot));
  }

  /** Find striking-limb bones on a fighter skeleton by attack kind. */
  findLimbBones(fighterRoot, kind = 'punch') {
    const hints = LIMB_HINTS[kind] || LIMB_HINTS.punch;
    const bones = [];
    fighterRoot.traverse((o) => {
      if (o.isBone && hints.some((re) => re.test(o.name))) bones.push(o);
    });
    return bones;
  }

  /** Capsule shapecast: attacker's limb segments vs defender's BVH.
      Returns { hit, point:Vector3, distance } or { hit:false }. */
  async testLimbVsBody(attackerRoot, defenderRoot, limbBones = null, { radius = 0.09 } = {}) {
    if (!this.ready) return { hit: false };
    const M = await loadBVH();
    const def = await this.buildFighterBVH(defenderRoot);
    if (!def) return { hit: false };
    const bones = limbBones || this.findLimbBones(attackerRoot, 'punch');
    if (!bones.length) return { hit: false };

    const a = new THREE.Vector3(), b = new THREE.Vector3();
    let best = null;
    const sphere = new THREE.Sphere();
    for (const bone of bones) {
      bone.getWorldPosition(a);
      // Segment: joint → child joint (or short extension at tip).
      let tip = null;
      const kids = bone.children.filter((c) => c.isBone);
      if (kids.length) { tip = new THREE.Vector3(); kids[0].getWorldPosition(tip); }
      else {
        const dir = new THREE.Vector3();
        bone.getWorldDirection(dir);
        tip = a.clone().addScaledVector(dir, 0.14);
      }
      // Sweep 3 sample spheres along the segment.
      for (let s = 0; s <= 2; s++) {
        sphere.center.copy(a).lerp(tip, s / 2);
        sphere.radius = radius;
        // Transform sphere into defender baked-geometry local space.
        const inv = new THREE.Matrix4().copy(def.root.matrixWorld).invert();
        const local = sphere.clone().applyMatrix4(inv);
        const hit = def.bvh.intersectsSphere(local);
        if (hit) {
          const pt = sphere.center.clone();
          const d = pt.distanceTo(defenderRoot.position);
          if (!best || d < best.distance) best = { hit: true, point: pt, distance: d };
        }
      }
    }
    return best || { hit: false };
  }

  /** Verify hook: call after the sphere test lands a hit.
      Logs sphere/BVH agreement; never changes the outcome. */
  async verify(attackerRoot, defenderRoot, sphereHit, limbBones, meta = {}) {
    if (!this.ready || this.mode === 'off') return sphereHit;
    this.stats.sphereHits++;
    try {
      const r = await this.testLimbVsBody(attackerRoot, defenderRoot, limbBones);
      if (r.hit === sphereHit) this.stats.bvhAgree++;
      else {
        this.stats.bvhDisagree++;
        console.info('[WHHitDetect] sphere/BVH disagree', {
          sphere: sphereHit, bvh: r.hit, ...meta,
          agreeRate: (this.stats.bvhAgree / this.stats.sphereHits).toFixed(3),
        });
      }
      if (this.mode === 'authority') return r.hit;
    } catch (e) {
      console.warn('[WHHitDetect] verify failed, keeping sphere result', e);
    }
    return sphereHit;
  }

  /** Fast raycast pick against a model (creation-suite tap-to-select).
      Installs acceleratedRaycast once; returns intersections or []. */
  async pick(modelRoot, raycaster) {
    const M = await loadBVH();
    if (!this._pickInstalled) {
      const proto = (await import('three')).Mesh.prototype;
      if (proto.raycast !== M.acceleratedRaycast) proto.raycast = M.acceleratedRaycast;
      this._pickInstalled = true;
    }
    const meshes = [];
    modelRoot.traverse((o) => {
      if (o.isMesh) {
        if (!o.geometry.boundsTree) o.geometry.computeBoundsTree();
        meshes.push(o);
      }
    });
    return raycaster.intersectObjects(meshes, false);
  }

  report() {
    const s = this.stats;
    return { ...s, agreeRate: s.sphereHits ? s.bvhAgree / s.sphereHits : 1 };
  }
}
