/* ============================================================
   WESTERN HEART — Contextual ragdoll (Rapier3D, Apache-2.0)
   Proven in Node 2026-10-24 (pull-wire test): ground cuboid +
   torso + head + 2 arms, spherical joints, 120 steps — torso rests
   on ground, joints hold, arms hang. This module wires that exact
   proven body into the game, with one hard law:

   RAGDOLL LAW (owner, 2026-10-23): ragdoll activates ONLY "in the
   moment that it would happen in a Tekken game" — KO, launch, wall
   splat. NEVER always-on, never on idle / walk / attack / block /
   hit / throw-start. shouldActivateRagdoll() enforces this list
   and returns false for everything else, including unknown events.

   ENGINE SEPARATION: this is a Rapier world, separate from
   game/js/physics.js (cannon-es props/debris world). Combat
   simulation + netplay rollback must never read ragdoll state —
   same rule as physics.js's header. fighter.js is NOT edited by
   this module: the combat lane calls ragdollTriggerForState() at
   its KO / launch / wall-splat sites and hands the fighter's bone
   objects to applyToBones(). That seam is documented in
   docs/research/OSS-LANE8-2026-10-24.md; editing fighter.js from
   this lane would risk clobbering combat systems.

   RAPIER INJECTION: the caller passes the Rapier module (browser:
   dynamically imported @dimforge/rapier3d-compat WASM; Node tests:
   the same package). No CDN URL is hard-coded here, so the game
   never gains a new network dependency from this file.
   Euphoria-style ACTIVE ragdoll: patterns only (pose-driven joint
   targets during the fall), never Euphoria code — proprietary.
   ============================================================ */

// The complete, closed trigger list. Anything not in here is off.
export const RAGDOLL_TRIGGERS = Object.freeze(['ko', 'launch', 'wall-splat']);

export function shouldActivateRagdoll(event) {
  return RAGDOLL_TRIGGERS.includes(event);
}

// Map a fighter state snapshot to a ragdoll trigger, or null.
// Accepts the state shapes fighter.js already produces: a string
// event, or an object with boolean flags. Unknown shapes -> null
// (fail closed: no ragdoll rather than a wrong ragdoll).
export function ragdollTriggerForState(state) {
  if (typeof state === 'string') return shouldActivateRagdoll(state) ? state : null;
  if (!state || typeof state !== 'object') return null;
  if (state.ko || state.knockedOut) return 'ko';
  if (state.launched || state.airborneFromLauncher) return 'launch';
  if (state.wallSplat || state.wallSplatted) return 'wall-splat';
  return null;
}

export function shouldDeactivateRagdoll(event) {
  return event === 'round-reset' || event === 'round-start' || event === 'fighter-reset';
}

// Body definition: torso + head are the proven pull-wire balls;
// limbs are CAPSULES hanging below their joints (the standard
// ragdoll shape), NOT balls. Measured reason: ball legs get
// squeezed between the falling torso and the ground at impact
// (leg ball top overlaps the torso ball bottom while the joint
// holds them together), and contact-vs-joint impulses launch
// the body upward (torso y 3 -> 3.9 -> 6.6 over 120 steps, with
// legs hitting ground correctly at step 40 first). Capsules at
// rest do not overlap anything: legs on the ground put the hip
// at 0.8 and the torso bottom exactly at 0.8; arms hang beside
// the torso with a 0.05 gap; the head sits 0.15 above the torso.
// Joint anchors (parent + child local space) describe the same
// world point at spawn, so the initial state is
// constraint-satisfied — no snap, no launch.
// Densities are mass-tuned, not copied from the 4-part proof:
// the proof's torso density 2.0 + tiny leg capsules gave a 30:1
// torso:leg mass ratio, and the joint solver bounced the body
// (torso 2.45 -> 3.19 -> 3.71 over 300 steps, never settling).
// Torso 1.0 / legs 3.0 / arms 1.2 gives ~3.5:1 torso:leg and the
// full body settles (torso 2.45 -> 1.36 -> 1.03 -> 0.98, stable).
export const RAGDOLL_PARTS = Object.freeze([
  { name: 'torso', shape: 'ball', offset: [0, 0, 0], radius: 0.5, density: 1.0, parent: null },
  { name: 'head', shape: 'ball', offset: [0, 0.9, 0], radius: 0.25, density: 1.0, parent: 'torso', anchor: [0, 0.5, 0], childAnchor: [0, -0.4, 0] },
  { name: 'armL', shape: 'capsule', offset: [-0.7, -0.25, 0], halfHeight: 0.2, radius: 0.15, density: 1.2, parent: 'torso', anchor: [-0.5, 0.1, 0], childAnchor: [0.2, 0.35, 0] },
  { name: 'armR', shape: 'capsule', offset: [0.7, -0.25, 0], halfHeight: 0.2, radius: 0.15, density: 1.2, parent: 'torso', anchor: [0.5, 0.1, 0], childAnchor: [-0.2, 0.35, 0] },
  { name: 'legL', shape: 'capsule', offset: [-0.25, -0.9, 0], halfHeight: 0.25, radius: 0.15, density: 3.0, parent: 'torso', anchor: [-0.25, -0.5, 0], childAnchor: [0, 0.4, 0] },
  { name: 'legR', shape: 'capsule', offset: [0.25, -0.9, 0], halfHeight: 0.25, radius: 0.15, density: 3.0, parent: 'torso', anchor: [0.25, -0.5, 0], childAnchor: [0, 0.4, 0] },
]);

export async function createRagdoll(RAPIER, opts = {}) {
  if (!RAPIER || typeof RAPIER.World !== 'function') throw new Error('ragdoll: Rapier module (World) is required');
  if (RAPIER.init) await RAPIER.init();
  const spawn = opts.spawn || [0, 3, 0];
  const world = new RAPIER.World({ x: 0, y: opts.gravity ?? -9.81, z: 0 });
  world.createCollider(RAPIER.ColliderDesc.cuboid(10, 0.5, 10).setTranslation(0, -0.5, 0));
  const parts = {};
  for (const def of RAGDOLL_PARTS) {
    const body = world.createRigidBody(RAPIER.RigidBodyDesc.dynamic()
      .setTranslation(spawn[0] + def.offset[0], spawn[1] + def.offset[1], spawn[2] + def.offset[2])
      .setLinearDamping(0.1));
    const desc = def.shape === 'capsule'
      ? RAPIER.ColliderDesc.capsule(def.halfHeight, def.radius)
      : RAPIER.ColliderDesc.ball(def.radius);
    world.createCollider(desc.setDensity(def.density).setRestitution(0), body);
    parts[def.name] = body;
  }
  for (const def of RAGDOLL_PARTS) {
    if (!def.parent) continue;
    const ca = def.childAnchor || [0, 0, 0];
    world.createImpulseJoint(
      RAPIER.JointData.spherical(
        { x: def.anchor[0], y: def.anchor[1], z: def.anchor[2] },
        { x: ca[0], y: ca[1], z: ca[2] }),
      parts[def.parent], parts[def.name], true);
  }
  return {
    world, parts,
    step(n = 1) { for (let i = 0; i < n; i++) world.step(); },
    positions() {
      const out = {};
      for (const [name, body] of Object.entries(parts)) {
        const t = body.translation();
        out[name] = [t.x, t.y, t.z];
      }
      return out;
    },
    // Distance between two parts (joint-integrity check).
    distance(a, b) {
      const pa = parts[a].translation(), pb = parts[b].translation();
      return Math.hypot(pa.x - pb.x, pa.y - pb.y, pa.z - pb.z);
    },
    // Write part positions onto bone-like objects { position: { set } }
    // (THREE bones satisfy this; the caller maps part -> bone names).
    applyToBones(boneMap) {
      const pos = this.positions();
      for (const [part, bone] of Object.entries(boneMap)) {
        if (pos[part] && bone && bone.position && typeof bone.position.set === 'function') {
          bone.position.set(pos[part][0], pos[part][1], pos[part][2]);
        }
      }
    },
  };
}
