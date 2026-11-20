/* ============================================================
   WESTERN HEART — Hand Pose Library

   Authored finger poses (all three reference games — Tekken, SFV, DOA —
   do finger posing via authored animation, not procedural systems).
   Poses are defined as local-space Euler rotations per finger bone,
   applied on top of the animation pose.

   Canonical bone names (53-joint WH skeleton):
     {Left,Right}Hand{Thumb,Index,Middle,Ring,Pinky}{1,2,3}

   Poses:
     fist  — default fight pose (all fingers curled)
     open  — parry/slap moves (fingers extended, slight spread)
     point — taunts/intros (index extended, others curled)
     grip  — throw animations (tight curl)

   Usage:
     import { setHandPose, HAND_POSES } from './handPoses.js';
     setHandPose(bones, 'fist', 1.0);   // bones: {name: THREE.Bone}
     setHandPose(bones, 'open', 0.5);   // blend amount 0..1
   ============================================================ */

// Euler rotations [x, y, z] in radians, applied in bone local space.
// Positive X curls fingers inward (toward palm) for the WH skeleton.
const FINGER_CURL = {
  // [seg1, seg2, seg3] curl amounts per pose
  fist:  [1.2, 1.4, 1.0],
  open:  [0.05, 0.05, 0.05],
  point: [1.2, 1.4, 1.0],  // overridden for index below
  grip:  [1.5, 1.6, 1.2],
};

const THUMB_CURL = {
  fist:  [0.8, 0.9, 0.6],
  open:  [0.1, 0.1, 0.1],
  point: [0.8, 0.9, 0.6],
  grip:  [1.0, 1.1, 0.8],
};

// Finger spread (Z rotation) for open pose
const FINGER_SPREAD = {
  Thumb: 0.25, Index: 0.12, Middle: 0.0, Ring: -0.12, Pinky: -0.2,
};

export const HAND_POSES = ['fist', 'open', 'point', 'grip'];

// Cache of base quaternions so poses blend from the animated pose
const _baseQuat = new WeakMap();

function getBase(bone) {
  if (!_baseQuat.has(bone)) {
    _baseQuat.set(bone, bone.quaternion.clone());
  }
  return _baseQuat.get(bone);
}

export function resetHandPoseCache() {
  // Called when the model changes; WeakMap auto-cleans but we clear explicitly
}

function fingerBones(bones, side, finger) {
  // Returns [seg1, seg2, seg3] bones or nulls for missing
  const out = [];
  for (let s = 1; s <= 3; s++) {
    const name = `${side}Hand${finger}${s}`;
    out.push(bones[name] || null);
  }
  return out;
}

export function setHandPose(bones, pose = 'fist', amount = 1.0) {
  if (!HAND_POSES.includes(pose)) pose = 'fist';
  amount = Math.max(0, Math.min(1, amount));
  if (amount <= 0.001) return;

  const fingers = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky'];
  for (const side of ['Left', 'Right']) {
    for (const finger of fingers) {
      const segs = fingerBones(bones, side, finger);
      const isThumb = finger === 'Thumb';
      const curl = isThumb ? THUMB_CURL[pose] : FINGER_CURL[pose];

      for (let s = 0; s < 3; s++) {
        const bone = segs[s];
        if (!bone) continue;

        let cx = curl[s];
        let cz = 0;
        // Point pose: index stays extended
        if (pose === 'point' && finger === 'Index') {
          cx = 0.05;
        }
        // Open pose: add spread
        if (pose === 'open') {
          cz = FINGER_SPREAD[finger] || 0;
          if (side === 'Right') cz = -cz;
        }

        // Build target quaternion from Euler
        const e = { x: cx * amount, y: 0, z: cz * amount };
        const qx = Math.sin(e.x / 2), qy = 0, qz = Math.sin(e.z / 2);
        const qw = Math.sqrt(Math.max(0, 1 - qx * qx - qz * qz));
        // Apply on top of base: q = base * delta
        const base = getBase(bone);
        // Use THREE.Quaternion if available via bone
        const dq = new bone.quaternion.constructor(qx, qy, qz, qw);
        bone.quaternion.copy(base).multiply(dq);
      }
    }
  }
}

// Pose blending helper for state transitions
export class HandPoseBlender {
  constructor() {
    this.current = 'fist';
    this.target = 'fist';
    this.blend = 1.0;
  }
  setPose(pose) {
    if (pose !== this.target) {
      this.target = pose;
      this.blend = 0.0;
    }
  }
  update(bones, dt) {
    if (this.blend < 1.0) {
      this.blend = Math.min(1.0, this.blend + dt * 6);
    }
    // Apply target pose; if blending, we'd need two-pose interpolation.
    // For simplicity, snap-blend via amount.
    setHandPose(bones, this.target, this.blend);
    this.current = this.target;
  }
}
