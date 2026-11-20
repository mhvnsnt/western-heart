/* ============================================================
   WESTERN HEART — Jiggle (runtime spring-bone solver)

   Implements the SFV spring-bone pattern per the DOA/SF/Tekken teardown
   research (~/workspace/jiggle-face-hands-teardown.md):
     - extra jiggle joints in the game skeleton (Breast_L/R, Butt_L/R,
       Belly, optional ThighFat_L/R), parented to Spine2/Hips/Spine1
     - per-frame spring integration on those joints (stiffness, damping,
       gravity scale), tuned per region
     - user-tunable intensity presets (DOA5's Natural/DOA/OMG idea)

   Canonical data lives in tools/jiggle/jiggle_chains.json (schema
   wh-jiggle-chains-v2): CHAIN_DEFAULTS below mirrors its runtime_params
   per chain; regenerate from the JSON if the standard changes.
   Families: female -> [breast, butt, belly]; male -> [butt];
   male_fat -> [butt, belly]. Camel-toe (Pelvic_L/R) is per-character
   (Torch A3 reference piece) — pass explicit chains to enable it.

   INTEGRATION CONTRACT (for the game lane — this module is NOT wired
   into the game loop yet):
     1. After loading a fighter's SkinnedMesh: 
          const jig = JiggleRig.fromMesh(skinnedMesh, 'female');
        (family from the character's rig spec; intensity via
         jig.setIntensity('natural' | 'doa' | 'omg'))
     2. Every frame, AFTER the animation/moveset pose is applied and
        BEFORE render:
          jig.update(dt);
     3. On fighter swap / dispose: jig.dispose() restores rest pose.

   Solver: per chain root, a spring on the offset vector in the parent's
   local space, excited by parent acceleration (the standard spring-bone
   formulation: acc = -k*offset - c*vel + parentAccel*coupling - g*scale).
   The offset becomes a small rotation of the jiggle bone around its rest
   direction. Stable for any dt via substeps (max 1/30 s each).
   ============================================================ */
import * as THREE from 'three';

// Mirrors tools/jiggle/jiggle_chains.json runtime_params + intensity_presets.
// [stiffness, damping, gravityScale] per chain id.
const CHAIN_DEFAULTS = {
  breast: { bones: ['Breast_L', 'Breast_L.001', 'Breast_R', 'Breast_R.001'],
            stiffness: 0.45, damping: 0.35, gravityScale: 0.6 },
  butt:   { bones: ['Butt_L', 'Butt_R'],
            stiffness: 0.50, damping: 0.40, gravityScale: 0.6 },
  belly:  { bones: ['Belly'],
            stiffness: 0.50, damping: 0.45, gravityScale: 0.6 },
  thigh:  { bones: ['ThighFat_L', 'ThighFat_R'],
            stiffness: 0.60, damping: 0.50, gravityScale: 0.7 },
  pelvic: { bones: ['Pelvic_L', 'Pelvic_R'],   // Torch A3 only
            stiffness: 0.55, damping: 0.40, gravityScale: 0.5 },
};
const FAMILIES = {
  female:   ['breast', 'butt', 'belly'],
  male:     ['butt'],
  male_fat: ['butt', 'belly'],
};
const INTENSITY = { natural: 1.0, doa: 1.5, omg: 2.2 };
const MAX_OFFSET = 0.06;   // meters — hard clamp on spring travel

class SpringChain {
  constructor(bone, params) {
    this.bone = bone;
    this.params = params;
    this.restDir = new THREE.Vector3();
    bone.getWorldPosition(this.restDir);          // filled on first update
    this.offset = new THREE.Vector3();            // parent-local offset
    this.vel = new THREE.Vector3();
    this.prevParentPos = new THREE.Vector3();
    this.parentVel = new THREE.Vector3();
    this.parentAccel = new THREE.Vector3();
    this.init = false;
    // rest orientation, so dispose() can restore exactly
    this.restQuat = bone.quaternion.clone();
    this.restPos = bone.position.clone();
  }
  update(dt, intensity) {
    const bone = this.bone;
    const parent = bone.parent;
    const p = this.params;
    const k = p.stiffness * 90.0;                 // -> rad/s^2-ish spring
    const c = p.damping * 6.0;
    const g = p.gravityScale * 2.2 * intensity;

    // parent world position -> accel (finite difference)
    const pw = new THREE.Vector3();
    parent.getWorldPosition(pw);
    if (!this.init) { this.prevParentPos.copy(pw); this.init = true; }
    const pv = pw.clone().sub(this.prevParentPos).divideScalar(Math.max(dt, 1e-4));
    const pa = pv.clone().sub(this.parentVel).divideScalar(Math.max(dt, 1e-4));
    this.parentVel.copy(pv);
    this.prevParentPos.copy(pw);
    // smooth the accel so mocap jitter doesn't inject noise
    this.parentAccel.lerp(pa, 0.35);

    // spring in parent-local space; excitation = -parentAccel (inertia)
    const local = parent.worldToLocal(pa.clone().negate());
    const acc = this.offset.clone().multiplyScalar(-k)
      .addScaledVector(this.vel, -c)
      .addScaledVector(local, 0.9 * intensity);
    acc.y -= g * dt * 60 * 0.016;                // gravity bias, frame-rate-ish
    this.vel.addScaledVector(acc, dt);
    this.offset.addScaledVector(this.vel, dt);
    if (this.offset.length() > MAX_OFFSET)
      this.offset.setLength(MAX_OFFSET);

    // offset -> small rotation about rest direction
    const restDirLocal = new THREE.Vector3(0, 1, 0); // bones point +Y locally
    const target = restDirLocal.clone().add(this.offset.clone()
      .divideScalar(Math.max(bone.position.length(), 0.02)));
    const q = new THREE.Quaternion()
      .setFromUnitVectors(restDirLocal, target.normalize());
    bone.quaternion.copy(this.restQuat).multiply(q);
  }
  restore() {
    this.bone.quaternion.copy(this.restQuat);
    this.bone.position.copy(this.restPos);
  }
}

export class JiggleRig {
  constructor() {
    this.chains = [];
    this.intensity = INTENSITY.natural;
  }
  static fromMesh(skinnedMesh, family = 'female', chainIds = null) {
    const rig = new JiggleRig();
    const ids = chainIds || FAMILIES[family] || FAMILIES.female;
    const bones = {};
    skinnedMesh.traverse(o => { if (o.isBone) bones[o.name] = o; });
    for (const id of ids) {
      const def = CHAIN_DEFAULTS[id];
      if (!def) continue;
      for (const bn of def.bones) {
        const bone = bones[bn];
        if (bone) rig.chains.push(new SpringChain(bone, def));
      }
    }
    return rig;
  }
  setIntensity(preset) {
    if (preset in INTENSITY) this.intensity = INTENSITY[preset];
  }
  update(dt) {
    // substep for stability on hitches
    let remaining = Math.min(dt, 0.1);
    while (remaining > 1e-4) {
      const h = Math.min(remaining, 1 / 30);
      for (const ch of this.chains) ch.update(h, this.intensity);
      remaining -= h;
    }
  }
  dispose() {
    for (const ch of this.chains) ch.restore();
    this.chains.length = 0;
  }
  get activeBones() { return this.chains.map(c => c.bone.name); }
}
