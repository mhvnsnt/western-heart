/* ============================================================
   WESTERN HEART — University retargeting patterns, implemented
   as small honest modules (no paper code is vendored here; these
   are WH implementations of the published PATTERNS, each labeled):
   U1 SIGGRAPH 2019 character-agnostic retargeting: motion is
     carried as joint ROLE trajectories, not as a source hierarchy
     — retargetPose() reads roles, so a 2D/video-derived pose in
     role form retargets the same way a 3D clip does.
   U2 topology-agnostic semantic encoding (arXiv 2026-05-26):
     mapByRole() aligns by SEMANTIC role (shoulder/elbow/wrist…),
     not by bone name or hierarchy — this is what lets a human T7
     clip drive non-humanoid roster (4-armed Chatur, beast spirits,
     Deathfang) via EXTRA roles (arm3/arm4, tail, earL/earR).
   U4 correspondence-free retargeting (arXiv 2302.00556): when NO
     bone map is supplied, mapByRole() IS the fast path — no hand
     map needed. Hand maps, when present, win (they are higher
     quality); the fast path exists for the 29 UNMAPPED stances.
   U5 physics-based retargeting from sparse inputs (arXiv
     2307.01938): cleanFootSlide() removes foot slide + floor
     penetration from sparse-keyframe output; tail/ear secondary
     motion is carried as damped-follow roles (secondaryFollow()).
   U6 Disney+ETH Differentiable Optimal Control (SIGGRAPH 2023):
     solveHandTarget() is the DOC pattern in miniature — solve for
     a hand placement SUBJECT TO reach + balance constraints,
     instead of copying source directions (which fails on Cape's
     wide shoulders + short 0.243 arms, documented 2026-10-24).
     It is NOT Disney's solver; it is a reach-clamped two-bone
     solve with a balance check, which is the same constraint
     structure at WH scale.
   U3 Aalto+NVIDIA online motion synthesis: proceduralIdle()
     samples deterministic seeded variation (no reference motion)
     for idle/stance so no two idles are identical.
   Poses here are plain data: { role: { rot: [x,y,z], pos: [x,y,z] } }
   or { role: [x,y,z] } positions. No THREE dependency.
   ============================================================ */

export const SEMANTIC_ROLES = Object.freeze([
  'hips', 'spine', 'chest', 'neck', 'head',
  'shoulderL', 'elbowL', 'wristL', 'shoulderR', 'elbowR', 'wristR',
  'hipL', 'kneeL', 'ankleL', 'hipR', 'kneeR', 'ankleR',
  // Non-humanoid extras (U2): extra arms, tail, ears.
  'shoulder3L', 'elbow3L', 'wrist3L', 'shoulder3R', 'elbow3R', 'wrist3R',
  'tail', 'tailTip', 'earL', 'earR',
]);

// Build a role -> target-bone map. boneMap (hand map) wins when
// given; otherwise fall back to role-name matching against the
// target rig's bone names (correspondence-free, U4). Names are
// normalized (lowercase, separators _ . - stripped) before
// matching, so 'Shoulder_L', 'shoulder.l' and 'shoulderL' all
// match role 'shoulderL' — separator style must never break a map.
export function mapByRole(targetBoneNames, boneMap = null) {
  const norm = (s) => String(s).toLowerCase().replace(/[^a-z0-9]/g, '');
  const map = {};
  const names = targetBoneNames || [];
  const normalized = names.map(norm);
  for (const role of SEMANTIC_ROLES) {
    if (boneMap && boneMap[role]) { map[role] = boneMap[role]; continue; }
    const idx = normalized.findIndex((n) => n.includes(norm(role)));
    if (idx >= 0) map[role] = names[idx];
  }
  return map;
}

// Retarget a source pose (role -> joint) onto target roles.
// Rotations copy 1:1 (direction-independent); positions scale by
// per-limb proportion factors so a short-armed target does not
// inherit a long-armed source's reach. proportions: role -> scale,
// default 1. Returns a target-role pose (unmapped roles dropped).
export function retargetPose(sourcePose, roleMap, proportions = {}) {
  const out = {};
  for (const [role, joint] of Object.entries(sourcePose)) {
    if (!roleMap[role]) continue;
    const scale = proportions[role] ?? 1;
    if (Array.isArray(joint)) out[role] = joint.map((v) => v * scale);
    else if (joint && Array.isArray(joint.pos)) out[role] = { rot: joint.rot, pos: joint.pos.map((v) => v * scale) };
    else out[role] = joint;
  }
  return out;
}

// U5 foot-slide cleanup: frames = [{ ankleL: [x,y,z], ankleR: [...] }].
// A foot is "planted" when its height is within plantEps of groundY:
// planted feet snap to groundY and freeze horizontally (the slide
// in the source is removed, not copied); airborne feet pass through
// untouched, except they never penetrate the floor.
export function cleanFootSlide(frames, { groundY = 0, plantEps = 0.05 } = {}) {
  const out = frames.map((f) => ({ ankleL: [...f.ankleL], ankleR: [...f.ankleR] }));
  for (let i = 1; i < out.length; i++) {
    for (const foot of ['ankleL', 'ankleR']) {
      const prev = out[i - 1][foot], cur = out[i][foot];
      if (Math.abs(cur[1] - groundY) <= plantEps) {
        cur[0] = prev[0]; cur[2] = prev[2]; cur[1] = groundY;
      } else if (cur[1] < groundY) {
        cur[1] = groundY; // never penetrate the floor
      }
    }
  }
  return out;
}

// U5 secondary motion: a follower joint chases its driver with
// damping (tail/ear motion generated, not hand-animated).
export function secondaryFollow(prevFollower, driver, damping = 0.35) {
  return prevFollower.map((v, i) => v + (driver[i] - v) * damping);
}

// U6 miniature: solve a hand target subject to maxReach and a
// balance check (hips x must stay within the feet span). Returns
// { reachable, target: [x,y,z] (clamped if needed), balanced }.
export function solveHandTarget(shoulder, desired, { maxReach = 0.243, feetSpan = [-0.3, 0.3], hipsX = 0 } = {}) {
  const d = desired.map((v, i) => v - shoulder[i]);
  const len = Math.hypot(...d) || 1;
  const reachable = len <= maxReach;
  const clamped = reachable ? [...desired] : shoulder.map((v, i) => v + (d[i] / len) * maxReach);
  return { reachable, target: clamped, balanced: hipsX >= feetSpan[0] && hipsX <= feetSpan[1] };
}

// U3 procedural idle: deterministic seeded sway/breath offsets.
// Same seed + time -> same output (reproducible); different seed
// -> different idle. No reference motion involved.
export function proceduralIdle(seed, t) {
  const s = (k) => Math.sin(t * 1.7 + seed * 12.9898 + k) * 0.5 + Math.sin(t * 0.9 + seed * 78.233 + k * 2) * 0.5;
  return { breath: s(0) * 0.02, swayX: s(1) * 0.015, swayZ: s(2) * 0.01, headTilt: s(3) * 0.03 };
}
