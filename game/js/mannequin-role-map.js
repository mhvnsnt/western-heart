/* ============================================================
   WESTERN HEART — Mannequin-bone -> WH semantic-role map (transfer T1b)
   Pure, headless-testable. No DOM, no THREE.

   SOURCE (docs only, from WH's own tooling): the 19-bone mannequin
   list WH's Blender bake path already uses (tools/anim/t7_bl_basis.py):
   BASE, Spine1, Hip, Neck, Head, R/L Shoulder, R/L Arm, R/L ForeArm,
   R/L Hand, R/L UpLeg, R/L Leg, R/L Foot.
   This module maps those 19 bones onto WH's semantic roles
   (game/js/retarget.js SEMANTIC_ROLES) — the same role names
   game/js/rig-compat.js already uses for its rig types, so a baked
   mannequin pose can be retargeted onto any WH rig by role.

   HONEST GAPS, stated in the data, not hidden:
   - BASE is the root: it carries translation, not a WH role, so it
     maps to `root` and is returned separately from roles.
   - R_Arm / L_Arm (upper arm) have NO WH semantic role: WH roles
     name shoulder (clavicle) / elbow (forearm) / wrist (hand).
     They are listed in UNMAPPED_BONES, never silently dropped —
     callers that need the upper-arm segment read it from the
     shoulder->elbow chain, not from a guessed role.
   - The 23-bone compressed clip format (teardown §5: bones 0-1 are
     float root translations in mm, the rest short Euler rotations)
     is NOT the same list as these 19 mannequin bones. This module
     does NOT claim a 23->19 index map: converting a raw 23-bone
     clip still waits on the per-bone reference-frame fix the
     teardown records as evidence-gated. validateClip23() below
     only validates the 23-bone *shape* (frame count, 23x3 numbers)
     and spike-filters it; it never invents a bone map.
   ============================================================ */

export const MANNEQUIN_BONES = Object.freeze([
  'BASE', 'Spine1', 'Hip', 'Neck', 'Head',
  'R_Shoulder', 'R_Arm', 'R_ForeArm', 'R_Hand',
  'L_Shoulder', 'L_Arm', 'L_ForeArm', 'L_Hand',
  'R_UpLeg', 'R_Leg', 'R_Foot', 'L_UpLeg', 'L_Leg', 'L_Foot',
]);

/** Mannequin bone -> WH semantic role ('root' for BASE, null = unmapped). */
export const MANNEQUIN_TO_ROLE = Object.freeze({
  BASE: 'root', Spine1: 'spine', Hip: 'hips', Neck: 'neck', Head: 'head',
  R_Shoulder: 'shoulderR', R_Arm: null, R_ForeArm: 'elbowR', R_Hand: 'wristR',
  L_Shoulder: 'shoulderL', L_Arm: null, L_ForeArm: 'elbowL', L_Hand: 'wristL',
  R_UpLeg: 'hipR', R_Leg: 'kneeR', R_Foot: 'ankleR',
  L_UpLeg: 'hipL', L_Leg: 'kneeL', L_Foot: 'ankleL',
});

export const UNMAPPED_BONES = Object.freeze(['R_Arm', 'L_Arm']);
export const MAPPED_ROLE_COUNT = 16; // 19 bones - BASE(root) - 2 unmapped = 16 roles

/** Convert a mannequin pose { bone: joint } to { roles, root, unmapped }.
 *  A joint may be [x,y,z] or { rot, pos }. Unmapped bones are returned
 *  in `unmapped` (with their joint) instead of being dropped silently.
 *  Unknown bones are also reported in `unmapped` with reason 'unknown-bone'. */
export function mannequinPoseToRoles(pose) {
  const roles = {}, unmapped = {};
  let root = null;
  for (const [bone, joint] of Object.entries(pose || {})) {
    if (!(bone in MANNEQUIN_TO_ROLE)) { unmapped[bone] = { joint, reason: 'unknown-bone' }; continue; }
    const role = MANNEQUIN_TO_ROLE[bone];
    if (role === 'root') root = joint;
    else if (role === null) unmapped[bone] = { joint, reason: 'no-wh-role' };
    else roles[role] = joint;
  }
  return { roles, root, unmapped };
}

/* ---- 23-bone compressed-clip shape (teardown §5) ---- */
export const CLIP23_BONE_COUNT = 23;
export const CLIP23_ROOT_INDICES = Object.freeze([0, 1]);
/** Spike threshold from the teardown's bake rule: frame steps over 0.5 rad
 *  on a rotation bone are gimbal spikes, not motion — filtered, not kept. */
export const CLIP23_SPIKE_RAD = 0.5;

/** Validate a 23-bone clip: { frames: [ [ [x,y,z] x 23 ] ... ] }.
 *  Returns problem strings; empty = shape-valid. Units are NOT checked
 *  here (root = mm, rotations = rad is the caller's contract). */
export function validateClip23(clip) {
  const problems = [];
  if (!clip || !Array.isArray(clip.frames) || !clip.frames.length) return ['no frames'];
  clip.frames.forEach((fr, i) => {
    if (!Array.isArray(fr) || fr.length !== CLIP23_BONE_COUNT) { problems.push(`frame ${i}: expected 23 bones, got ${Array.isArray(fr) ? fr.length : typeof fr}`); return; }
    fr.forEach((bone, j) => {
      if (!Array.isArray(bone) || bone.length !== 3 || bone.some((v) => typeof v !== 'number' || !Number.isFinite(v))) {
        problems.push(`frame ${i} bone ${j}: expected [x,y,z] numbers`);
      }
    });
  });
  return problems;
}

/** Spike-filter a validated 23-bone clip in place-shape (returns a new clip):
 *  any rotation-bone component whose step from the previous frame exceeds
 *  CLIP23_SPIKE_RAD is held at the previous frame's value. Root bones
 *  (indices 0-1, mm translations) are never spike-filtered. Returns
 *  { clip, spikesFiltered } so callers can report how much was filtered. */
export function spikeFilterClip23(clip) {
  const frames = clip.frames.map((fr) => fr.map((b) => [...b]));
  let spikesFiltered = 0;
  for (let i = 1; i < frames.length; i++) {
    for (let j = 2; j < CLIP23_BONE_COUNT; j++) {
      for (let k = 0; k < 3; k++) {
        if (Math.abs(frames[i][j][k] - frames[i - 1][j][k]) > CLIP23_SPIKE_RAD) {
          frames[i][j][k] = frames[i - 1][j][k]; spikesFiltered++;
        }
      }
    }
  }
  return { clip: { frames }, spikesFiltered };
}

/** Root translation of a 23-bone frame, converted mm -> metres. */
export function clip23RootMetres(frame) {
  return [frame[0], frame[1]].map((b) => b.map((v) => v / 1000));
}
