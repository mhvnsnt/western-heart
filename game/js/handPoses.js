/* ============================================================
   WESTERN HEART — Hand Pose Driver (finger-rig lane C3, 2026-11-22)

   Drives REAL finger poses as game controls — fist (close), palm/open
   (extend), point (index only), grip (tight curl for throws), and
   per-finger bends — by rotating the finger bones with quaternions.
   Poses are applied AFTER the animation mixer each frame (fighter.js
   update: _animate -> _hands.update), so they ride on top of whatever
   clip is playing and the mixer re-asserts the clip pose next frame:
   no drift, no state carried in the bones.

   MATH (same as Lane B's Blender proof, lane-b-tou/pose_render.py):
   each finger curls by chained axis-angle rotations about
     axis = normalize(cross(palmNormal, fingerDir))
   measured in the hand's REST pose; a positive angle curls the
   fingertip toward the palm. Per segment the target LOCAL quaternion is
     qLocal = inv(parentRestWorldQ) * R(axis, angle) * restWorldQ
   (Lane B's `b = rest^-1 @ R @ rest`, expressed in three.js local
   space). Only the pose quaternion is ever written — never the matrix
   (Lane B found matrix writes double-apply rotations: Middle1 read
   120 deg for a 60 deg curl). Location/scale are never touched.
   Angles (Lane B, proven on Tou's rigged model):
     FIST  seg1/2/3 = 60 / 75 / 65 deg, thumb 45 / 60 / 50 deg.
   PALM/OPEN is all-zero + a small per-finger fan spread about the
   palm normal. POINT is index at zero, the other four at fist angles.
   GRIP is a tighter fist for throw clinches.

   NAMING SCHEMES (Lane A audit — all five in the wild):
     1. canonical  `LeftHandThumb1…` / `RightHandPinky3` (most Tripo /
        GameRig files; also what assets.js hands us, since
        createInstance() strips any `mixamorig:` prefix off the
        bones dict keys).
     2. `mixamorig:`-prefixed canonical (all Brutal Fist files when
        read raw — a raw skeleton / GLB node list still carries the
        prefix; the resolver strips it when matching).
     3. `arm left/right finger Na/b/c` (mariposa-monarch / Zafina
        rebuild). VERIFIED by Lane C3 geometry (see WIRING.md): the
        number->finger map (1=thumb, 2=index, 3=middle, 4=ring,
        5=pinky) matches the model's own rest geometry — finger 1's
        base sits proximal (0.042 m from the wrist vs 0.084–0.096 m
        for the rest: the thumb), fingers 2–5 sit in order along the
        knuckle line, middle chain longest (0.133 m), pinky shortest
        (0.084 m), both hands identical. The point render also shows
        the extended finger in the anatomical index position.
     4. `LeftHandFinger1/2` (michiko — two bones per hand, no
        per-finger segments). NOT drivable per finger: reported only,
        never rotated.
     5. `fingers.L` / `fingers.R` (megami, menajerii — one bone per
        hand, no per-finger segments). NOT drivable per finger:
        reported only, never rotated.
   The driver poses only the bones that exist and skips the rest —
   a fighter with no finger bones (tou/kai/pantera live bodies),
   dead/unweighted bones, or a missing model (byou/ryuji/bannon) can
   never crash it and never produces NaN: every quaternion written is
   checked finite first, and a non-finite result leaves the mixer's
   pose untouched. NOTE: bone presence is not skinning — a bone can
   exist with zero skinned verts (Lane A: 11 dead rigs), in which case
   rotating it moves no mesh. The capability report is bone-presence
   only; weights are the rig lanes' audit (FINGER-AUDIT.md).

   Usage (same call sites as before — fighter.js already wires this):
     import { HandPoseBlender, setHandPose } from './handPoses.js';
     const hands = new HandPoseBlender(bones); // bind at REST, before
     hands.setPose('fist');                    // the mixer first updates
     hands.update(bones, dt);                  // every frame after _animate
     hands.setFinger('Left', 'Index', 0.5);    // per-finger bend, 0..1
     getHandCapability(bones);                 // { scheme, poses, ... }
   ============================================================ */
import * as THREE from 'three';

export const FINGERS = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky'];
export const SIDES = ['Left', 'Right'];

// Lane B proven curl angles, degrees per segment (seg1, seg2, seg3).
export const FIST_ANGLES = Object.freeze([60, 75, 65]);
export const THUMB_FIST_ANGLES = Object.freeze([45, 60, 50]);
export const GRIP_ANGLES = Object.freeze([75, 85, 75]);
export const GRIP_THUMB_ANGLES = Object.freeze([60, 70, 60]);
const ZERO_ANGLES = Object.freeze([0, 0, 0]);

// Fan spread (radians) about the palm normal, seg1 only, open/palm pose.
// Mirrored per side at apply time. (Kept from the previous handPoses.js.)
const FINGER_SPREAD = Object.freeze({
  Thumb: 0.25, Index: 0.12, Middle: 0.0, Ring: -0.12, Pinky: -0.2,
});

export const HAND_POSES = Object.freeze(['fist', 'open', 'palm', 'point', 'grip', 'custom']);
// 'palm' is the owner's word for the open hand; 'open' is the old name.
const POSE_ALIAS = Object.freeze({ palm: 'open' });

const _D2R = Math.PI / 180;

/* ---------------- naming-scheme resolution ---------------- */

// Normalize a bone name for matching: lowercase, strip the
// `mixamorig:` prefix, drop every non-alphanumeric.
function _norm(name) {
  return String(name || '').replace(/^mixamorig:?/i, '').toLowerCase().replace(/[^a-z0-9]/g, '');
}

// `arm finger` number -> finger name. VERIFIED from mariposa-monarch's
// own rest geometry by Lane C3 (knuckle order 2-3-4-5, middle longest,
// pinky shortest, finger-1 base proximal = thumb; see WIRING.md).
// Lane A had flagged it T7-convention-only; the geometry check settles it.
const ARM_FINGER_MAP = Object.freeze(['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']);

function _bonesToList(bones) {
  if (!bones) return [];
  if (Array.isArray(bones)) return bones.filter(Boolean);
  if (Array.isArray(bones.bones)) return bones.bones.filter(Boolean);
  if (typeof bones === 'object') return Object.values(bones).filter(Boolean);
  return [];
}

function _lookupByName(bones) {
  const map = new Map();
  for (const b of _bonesToList(bones)) {
    if (b && typeof b.name === 'string') {
      const key = _norm(b.name);
      if (!map.has(key)) map.set(key, b);
    }
  }
  return map;
}

/**
 * Resolve a bones collection to canonical finger slots.
 * Returns { Left: {Thumb:[b1,b2,b3], ...}, Right: {...},
 *           scheme, mappingVerified, handChain, handBone, notes }.
 * Missing bones are null in their slot — never throws, never invents.
 * `handChain` (LeftHandFinger1/2 scheme) and `handBone` (fingers.L/R
 * scheme) are reported for the capability readout but are NEVER posed
 * per finger: one/two bones per hand cannot bend individual fingers.
 */
export function resolveFingerBones(bones) {
  const byName = _lookupByName(bones);
  const out = { Left: {}, Right: {}, scheme: 'none', mappingVerified: true, handChain: {}, handBone: {}, notes: [] };
  for (const side of SIDES) for (const f of FINGERS) out[side][f] = [null, null, null];

  // 1/2. Canonical (+ mixamorig:-stripped by _norm).
  let found = 0;
  for (const side of SIDES) {
    for (const f of FINGERS) {
      for (let s = 1; s <= 3; s++) {
        const b = byName.get(_norm(`${side}Hand${f}${s}`));
        if (b) { out[side][f][s - 1] = b; found++; }
      }
    }
  }
  if (found > 0) {
    out.scheme = 'canonical';
    out.notes.push(`${found}/30 canonical finger bones present.`);
    return out;
  }

  // 3. `arm left/right finger Na/b/c` (mariposa-monarch).
  found = 0;
  for (const side of SIDES) {
    const sLower = side.toLowerCase();
    for (let n = 1; n <= 5; n++) {
      const f = ARM_FINGER_MAP[n - 1];
      for (let s = 0; s < 3; s++) {
        const b = byName.get(_norm(`arm ${sLower} finger ${n}${'abc'[s]}`));
        if (b) { out[side][f][s] = b; found++; }
      }
    }
  }
  if (found > 0) {
    out.scheme = 'arm-finger';
    out.mappingVerified = true;
    out.notes.push(
      `${found}/30 'arm finger' bones present. Mapping 1=thumb..5=pinky ` +
      'verified from this model\'s rest geometry by Lane C3 (finger-1 ' +
      'base proximal at the thumb, knuckle order 2-3-4-5, middle longest, ' +
      'pinky shortest — see WIRING.md).');
    return out;
  }

  // 4. `LeftHandFinger1/2` (michiko): two bones per hand, no segments.
  for (const side of SIDES) {
    const pair = [byName.get(_norm(`${side}HandFinger1`)), byName.get(_norm(`${side}HandFinger2`))];
    if (pair[0] || pair[1]) out.handChain[side] = pair;
  }
  if (Object.keys(out.handChain).length > 0) {
    out.scheme = 'finger1-2';
    out.notes.push('Two bones per hand, no per-finger segments — not drivable per finger; reported only.');
    return out;
  }

  // 5. `fingers.L/R` (megami, menajerii): one bone per hand.
  for (const side of SIDES) {
    const b = byName.get(_norm(`fingers.${side === 'Left' ? 'L' : 'R'}`));
    if (b) out.handBone[side] = b;
  }
  if (Object.keys(out.handBone).length > 0) {
    out.scheme = 'fingers';
    out.notes.push('One bone per hand, no per-finger segments — not drivable per finger; reported only.');
    return out;
  }

  out.notes.push('No finger bones found under any known naming scheme.');
  return out;
}

/**
 * Bone-presence capability report. This is BONE presence only — a bone
 * with zero skinned verts (Lane A dead rigs) reports present here and
 * still moves no mesh. Weights live in FINGER-AUDIT.md, not at runtime.
 * fist/palm/perFinger: 'full' (all 10 fingers have 3/3 segments),
 * 'partial' (at least one finger has 3/3), 'none'. point: 'full' (both
 * index fingers 3/3), 'partial' (one hand), 'none'.
 */
export function getHandCapability(bones) {
  const r = resolveFingerBones(bones);
  const perFinger = {};
  let fullFingers = 0, anyFinger = 0;
  for (const side of SIDES) {
    perFinger[side] = {};
    for (const f of FINGERS) {
      const present = r[side][f].filter(Boolean).length;
      perFinger[side][f] = { segments: present, bendable: present === 3 };
      if (present === 3) { fullFingers++; anyFinger++; }
      else if (present > 0) { /* present but not bendable */ }
    }
  }
  const indexFull = ['Left', 'Right'].map((s) => perFinger[s].Index.bendable);
  const cap = {
    scheme: r.scheme,
    mappingVerified: r.mappingVerified,
    fingers: perFinger,
    poses: {
      fist: fullFingers === 10 ? 'full' : (anyFinger > 0 ? 'partial' : 'none'),
      palm: fullFingers === 10 ? 'full' : (anyFinger > 0 ? 'partial' : 'none'),
      perFinger: fullFingers === 10 ? 'full' : (anyFinger > 0 ? 'partial' : 'none'),
      point: (indexFull[0] && indexFull[1]) ? 'full' : (indexFull[0] || indexFull[1] ? 'partial' : 'none'),
    },
    notes: r.notes.slice(),
  };
  if (r.scheme === 'none') cap.notes.push('Nothing to drive: no finger bones, no hand chain bone.');
  return cap;
}

/* ---------------- driver ---------------- */

const _qTmp1 = new THREE.Quaternion();
const _qTmp2 = new THREE.Quaternion();
const _qTmp3 = new THREE.Quaternion();
const _vTmp1 = new THREE.Vector3();
const _vTmp2 = new THREE.Vector3();
const _vTmp3 = new THREE.Vector3();

function _finiteQuat(q) {
  return q && Number.isFinite(q.x) && Number.isFinite(q.y) && Number.isFinite(q.z) && Number.isFinite(q.w);
}

// Target angles (degrees) for one finger in a named pose.
function _poseAngles(pose, finger) {
  const isThumb = finger === 'Thumb';
  switch (pose) {
    case 'open': return ZERO_ANGLES;
    case 'grip': return isThumb ? GRIP_THUMB_ANGLES : GRIP_ANGLES;
    case 'point': return finger === 'Index' ? ZERO_ANGLES : (isThumb ? THUMB_FIST_ANGLES : FIST_ANGLES);
    case 'fist': default: return isThumb ? THUMB_FIST_ANGLES : FIST_ANGLES;
  }
}

export class HandPoseBlender {
  /**
   * @param {object|array} [bones] — bind now if given (must be at REST:
   *   call from Fighter._build, before the mixer first updates, so the
   *   captured rest pose is exact). Without bones, the first update()
   *   binds lazily (rest is then estimated from the live pose — still
   *   safe, still no crash, but the curl axis is measured off a posed
   *   hand; prefer binding at build).
   */
  constructor(bones = null) {
    this.current = 'fist';
    this.target = 'fist';
    this.blend = 1.0;
    this.overrides = {}; // 'custom' pose: { 'Left.Index': amount 0..1, ... }
    this._bound = null;  // { resolved, perBone: Map<bone, rec>, restEstimated }
    this._angles = {};   // 'Left.Index' -> [deg, deg, deg] currently applied
    this._spread = {};   // 'Left.Index' -> radians of fan spread currently applied
    this._boundBonesRef = null;
    for (const side of SIDES) for (const f of FINGERS) { this._angles[`${side}.${f}`] = [0, 0, 0]; this._spread[`${side}.${f}`] = 0; }
    if (bones) this.bind(bones);
  }

  get bound() { return !!this._bound; }
  get scheme() { return this._bound ? this._bound.resolved.scheme : 'none'; }
  get capability() { return this._bound ? this._bound.capability : getHandCapability(null); }

  /**
   * Capture the rest pose + per-segment curl axes. Safe to call again
   * (model swap / rebind): old records are dropped. Never throws —
   * a hand that cannot be measured is skipped, not crashed.
   */
  bind(bones) {
    const resolved = resolveFingerBones(bones);
    const perBone = new Map();
    let restEstimated = false;
    try {
      // Rest world transforms: updateWorldMatrix(true, false) refreshes
      // each bone's ancestor chain, so world quats are exact even before
      // the model has ever been rendered.
      for (const side of SIDES) {
        for (const f of FINGERS) {
          for (let s = 0; s < 3; s++) {
            const bone = resolved[side][f][s];
            if (!bone || perBone.has(bone)) continue;
            bone.updateWorldMatrix(true, false);
            const restWorldQ = bone.getWorldQuaternion(new THREE.Quaternion());
            const restWorldP = bone.getWorldPosition(new THREE.Vector3());
            // A bone already carrying a non-finite quaternion (fighter.js
            // notes NaN quaternions can reach bones) is unmeasurable:
            // skip it — posing it later would only write NaN back.
            if (!_finiteQuat(restWorldQ) || !Number.isFinite(restWorldP.x + restWorldP.y + restWorldP.z)) continue;
            const parent = bone.parent;
            let parentRestQ = new THREE.Quaternion();
            if (parent) {
              parent.updateWorldMatrix(true, false);
              parent.getWorldQuaternion(parentRestQ);
              if (!_finiteQuat(parentRestQ)) continue;
            }
            perBone.set(bone, {
              side, finger: f, seg: s,
              restLocalQ: bone.quaternion.clone(),
              restWorldQ, restWorldP, parentRestQ,
            });
          }
        }
      }
      // Per-hand curl axes from rest geometry: palm normal N from the
      // knuckle line, axis = normalize(cross(N, segmentDir)).
      for (const side of SIDES) {
        const seg1Pos = {};
        for (const f of FINGERS) {
          const b = resolved[side][f][0];
          if (b && perBone.has(b)) seg1Pos[f] = perBone.get(b).restWorldP;
        }
        const have = Object.keys(seg1Pos);
        if (have.length < 2 || !seg1Pos.Middle) continue;
        const lateral = _vTmp1.copy(seg1Pos.Pinky || seg1Pos.Ring).sub(seg1Pos.Index || seg1Pos.Middle);
        if (lateral.lengthSq() < 1e-12) continue;
        lateral.normalize();
        // Segment directions: toward the child bone. Seg3 (no child)
        // continues along seg2's direction — the tip's own line — the
        // same axis Lane B uses for the whole finger (its fan dir).
        const dirOf = (bone, rec) => {
          const child = resolved[rec.side][rec.finger][rec.seg + 1];
          if (child && perBone.has(child)) {
            const d = perBone.get(child).restWorldP.clone().sub(rec.restWorldP);
            if (d.lengthSq() > 1e-12) return d.normalize();
          }
          if (rec.seg === 2) {
            const prev = resolved[rec.side][rec.finger][1];
            if (prev && perBone.has(prev)) {
              const d = rec.restWorldP.clone().sub(perBone.get(prev).restWorldP);
              if (d.lengthSq() > 1e-12) return d.normalize();
            }
          }
          return new THREE.Vector3(0, 1, 0).applyQuaternion(rec.restWorldQ).clone();
        };
        const midDir = dirOf(resolved[side].Middle[0], perBone.get(resolved[side].Middle[0]));
        const normal = new THREE.Vector3().crossVectors(midDir, lateral);
        if (normal.lengthSq() < 1e-12) continue;
        normal.normalize();
        // Sign self-check: a +45 deg curl of the middle finger must move
        // its tip TOWARD the palm (knuckle centroid). If the test curl
        // moves it away, this hand's normal is flipped. This makes the
        // driver correct for mirrored left/right rigs without guessing.
        const palmCenter = new THREE.Vector3();
        for (const p of Object.values(seg1Pos)) palmCenter.add(p);
        palmCenter.multiplyScalar(1 / have.length);
        const mid1 = resolved[side].Middle[0];
        const mid3 = resolved[side].Middle[2] || resolved[side].Middle[1] || mid1;
        const tipRest = perBone.get(mid3).restWorldP.clone();
        // Small-angle tip displacement for a curl about axis through mid1:
        // disp ~= theta * axis x (tip - origin). Test both signs.
        const origin = perBone.get(mid1).restWorldP;
        const r = tipRest.clone().sub(origin);
        const toPalm = palmCenter.clone().sub(tipRest);
        const axisTest = new THREE.Vector3().crossVectors(normal, midDir).normalize();
        const disp = new THREE.Vector3().crossVectors(axisTest, r);
        if (disp.dot(toPalm) < 0) normal.negate();
        // Store per-segment axes (recomputed with the settled normal).
        for (const f of FINGERS) {
          for (let s = 0; s < 3; s++) {
            const bone = resolved[side][f][s];
            if (!bone || !perBone.has(bone)) continue;
            const rec = perBone.get(bone);
            const d = dirOf(bone, rec);
            const axis = new THREE.Vector3().crossVectors(normal, d);
            if (axis.lengthSq() < 1e-12) { axis.copy(axisTest); }
            axis.normalize();
            rec.axis = axis;
            rec.normal = normal.clone();
          }
        }
      }
    } catch (e) {
      // Binding must never take the fight down: keep whatever was
      // captured, skip the rest. (Same guard style as jiggle/softbody.)
      restEstimated = true;
    }
    this._bound = { resolved, perBone, restEstimated, capability: null };
    this._bound.capability = getHandCapabilityFromResolved(resolved);
    this._boundBonesRef = bones;
    return this._bound;
  }

  setPose(pose, opts = null) {
    const p = POSE_ALIAS[pose] || pose;
    if (!HAND_POSES.includes(p)) return;
    if (p !== this.target) { this.target = p; this.blend = 0.0; }
    if (opts && opts.fingers) {
      this.overrides = { ...opts.fingers };
      if (p !== 'custom') this.target = 'custom';
    } else if (p !== 'custom') {
      this.overrides = {};
    }
    this.current = this.target;
  }

  /** Per-finger bend: side 'Left'|'Right', finger name, amount 0..1 of fist curl. */
  setFinger(side, finger, amount) {
    if (!SIDES.includes(side) || !FINGERS.includes(finger)) return;
    const a = Math.max(0, Math.min(1, Number(amount) || 0));
    this.overrides[`${side}.${finger}`] = a;
    if (this.target !== 'custom') { this.target = 'custom'; this.blend = 0.0; }
    this.current = 'custom';
  }

  clearFingers() {
    this.overrides = {};
    if (this.target === 'custom') this.setPose('fist');
  }

  _targetAngles() {
    const out = {};
    for (const side of SIDES) {
      for (const f of FINGERS) {
        const key = `${side}.${f}`;
        if (this.target === 'custom') {
          const a = this.overrides[key];
          if (a == null) { out[key] = [0, 0, 0]; continue; }
          const base = f === 'Thumb' ? THUMB_FIST_ANGLES : FIST_ANGLES;
          out[key] = base.map((d) => d * a);
        } else if (this.target === 'open') {
          out[key] = [0, 0, 0];
        } else {
          out[key] = _poseAngles(this.target, f).slice();
        }
      }
    }
    return out;
  }

  update(bones, dt) {
    if (!bones) return;
    // Rebind when the bones collection itself changed (model swap on
    // transform: _doModelSwap replaces this.bones with a fresh dict).
    // The fresh instance is at rest, so the new binding captures an
    // exact rest pose. Same dict object -> same bones, no re-resolve.
    if (!this._bound || bones !== this._boundBonesRef) this.bind(bones);
    if (!this._bound) return;
    if (!Number.isFinite(dt) || dt <= 0) dt = 0.016;
    if (this.blend < 1.0) this.blend = Math.min(1.0, this.blend + dt * 6);
    const targets = this._targetAngles();
    const spreadTargets = this._targetSpread();
    const rate = Math.min(1, this.blend);
    for (const side of SIDES) {
      for (const f of FINGERS) {
        const key = `${side}.${f}`;
        const cur = this._angles[key];
        const tgt = targets[key];
        for (let s = 0; s < 3; s++) cur[s] += (tgt[s] - cur[s]) * rate;
        this._spread[key] += (spreadTargets[key] - this._spread[key]) * rate;
        this._applyFinger(side, f, cur, this._spread[key]);
      }
    }
    this.current = this.target;
  }

  // Fan-spread targets (radians, unsigned — the side mirror is applied
  // in _applyFinger). Open: full fan. Point: the extended index keeps
  // its fan, curled fingers lose it. Fist/grip: none. Custom: a finger
  // keeps (1 - amount) of its fan as it curls, so going palm -> bend
  // one finger leaves the other four exactly where they were.
  _targetSpread() {
    const out = {};
    for (const side of SIDES) {
      for (const f of FINGERS) {
        const key = `${side}.${f}`;
        const full = FINGER_SPREAD[f] || 0;
        if (this.target === 'open') out[key] = full;
        else if (this.target === 'point') out[key] = f === 'Index' ? full : 0;
        else if (this.target === 'custom') out[key] = full * (1 - (this.overrides[key] || 0));
        else out[key] = 0;
      }
    }
    return out;
  }

  // Apply one finger's current angles (degrees) as absolute local
  // quaternions. spreadRad is the seg1 fan spread about the palm normal.
  _applyFinger(side, finger, anglesDeg, spreadRad) {
    if (!this._bound) return;
    const resolved = this._bound.resolved;
    const perBone = this._bound.perBone;
    for (let s = 0; s < 3; s++) {
      const bone = resolved[side][finger][s];
      if (!bone || !perBone.has(bone)) continue;
      const rec = perBone.get(bone);
      if (!rec.axis || !rec.normal) continue;
      const theta = (Number(anglesDeg[s]) || 0) * _D2R;
      if (!Number.isFinite(theta)) continue;
      // World-space curl about the rest axis, then seg1 fan spread.
      _qTmp1.setFromAxisAngle(rec.axis, theta);
      _qTmp2.copy(_qTmp1).multiply(rec.restWorldQ); // worldQ = Rcurl * Qrest
      if (s === 0 && spreadRad) {
        const spread = spreadRad * (side === 'Right' ? -1 : 1);
        _qTmp3.setFromAxisAngle(rec.normal, spread);
        _qTmp2.premultiply(_qTmp3); // worldQ = Rspread * Rcurl * Qrest
      }
      // Local = inv(parentRestWorldQ) * worldQ. Parent animation flows
      // through the parent chain; the finger pose is relative to the hand.
      const qLocal = new THREE.Quaternion().copy(rec.parentRestQ).invert().multiply(_qTmp2);
      if (!_finiteQuat(qLocal)) continue; // never write NaN to a bone
      bone.quaternion.copy(qLocal);
    }
  }

  /** Release: restore every finger bone to its captured rest pose. */
  dispose() {
    if (!this._bound) return;
    for (const [bone, rec] of this._bound.perBone) {
      if (bone && _finiteQuat(rec.restLocalQ)) bone.quaternion.copy(rec.restLocalQ);
    }
    this._bound = null;
  }
}

function getHandCapabilityFromResolved(resolved) {
  const perFinger = {};
  let fullFingers = 0, anyFinger = 0;
  for (const side of SIDES) {
    perFinger[side] = {};
    for (const f of FINGERS) {
      const present = resolved[side][f].filter(Boolean).length;
      perFinger[side][f] = { segments: present, bendable: present === 3 };
      if (present === 3) { fullFingers++; anyFinger++; }
    }
  }
  const idx = ['Left', 'Right'].map((s) => perFinger[s].Index.bendable);
  return {
    scheme: resolved.scheme,
    mappingVerified: resolved.mappingVerified,
    fingers: perFinger,
    poses: {
      fist: fullFingers === 10 ? 'full' : (anyFinger > 0 ? 'partial' : 'none'),
      palm: fullFingers === 10 ? 'full' : (anyFinger > 0 ? 'partial' : 'none'),
      perFinger: fullFingers === 10 ? 'full' : (anyFinger > 0 ? 'partial' : 'none'),
      point: (idx[0] && idx[1]) ? 'full' : (idx[0] || idx[1] ? 'partial' : 'none'),
    },
    notes: resolved.notes.slice(),
  };
}

/**
 * One-shot pose (kept for the old call sites): binds a scratch blender,
 * applies the pose at full blend. NOTE: binding measures the rest pose
 * from the bones as they are right now — call it right after animation
 * only via a HandPoseBlender bound at build; for one-off callers the
 * rest pose is estimated from the live pose. Prefer the blender.
 */
export function setHandPose(bones, pose = 'fist', amount = 1.0) {
  const p = POSE_ALIAS[pose] || pose;
  if (!HAND_POSES.includes(p) || p === 'custom') return;
  amount = Math.max(0, Math.min(1, Number(amount) || 0));
  if (amount <= 0.001) return;
  const blender = new HandPoseBlender(bones);
  blender.setPose(p);
  blender.blend = amount;
  blender.update(bones, 1);
}

// Kept for backward compatibility: the old WeakMap base cache is gone
// (it held the FIRST frame's quaternion forever — the stale-base bug);
// rest is now captured once at bind. Nothing to clear.
export function resetHandPoseCache() {}
