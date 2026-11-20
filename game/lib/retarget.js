// WH animation retargeting wrapper — three.js SkeletonUtils edition.
// Wiring target in repo: game/lib/retarget.js (drop-in; game passes THREE).
// What it does: retargets a source clip (e.g. a Tekken clip baked to a
// generic rig) onto a WH character SkinnedMesh whose bones differ in
// proportion/rest pose, using three's built-in SkeletonUtils.retargetClip.
// Contract learned from three's source (not assumed): BOTH target and
// source must carry a .skeleton (be SkinnedMeshes); track names must match
// bone names. The bone map below renames tracks when names differ.
// This is the in-game wrapper layer; the university retarget patterns
// (U1-U6) live separately in game/js/retarget.js (PR #1066 lane).
// Usage:
//   import { retargetClipTo } from './retarget.js';
//   const clip = retargetClipTo(THREE, whMesh, sourceMesh, tekkenClip, BONE_MAP);
// Bone map: { sourceBoneName: whBoneName }. Unmapped bones keep their name.
export function renameClipTracks(THREE, clip, boneMap) {
  const tracks = clip.tracks.map((t) => {
    const m = t.name.match(/^([^.]+)\.(.+)$/);
    if (!m) return t;
    const renamed = boneMap[m[1]] || m[1];
    const nt = t.clone(); nt.name = renamed + '.' + m[2]; return nt;
  });
  return new THREE.AnimationClip(clip.name, clip.duration, tracks);
}
export function retargetClipTo(THREE, SkeletonUtils, targetMesh, sourceMesh, clip, boneMap = {}) {
  if (!targetMesh.skeleton || !sourceMesh.skeleton) {
    throw new Error('retargetClipTo: target and source must be SkinnedMeshes with .skeleton');
  }
  const renamed = renameClipTracks(THREE, clip, boneMap);
  return SkeletonUtils.retargetClip(targetMesh, sourceMesh, renamed, { useFirstFramePosition: false });
}
// Starter bone map: generic/Tekken-style names -> WH rig names.
// ADAPT to the actual WH rig bone names before production use; this map is
// the one place that translation lives, so a rig rename is a one-file edit.
export const BONE_MAP_GENERIC_TO_WH = {
  Hips: 'pelvis', Spine: 'spine', Chest: 'chest', Neck: 'neck', Head: 'head',
  UpperArmL: 'upperarm_L', LowerArmL: 'forearm_L', HandL: 'hand_L',
  UpperArmR: 'upperarm_R', LowerArmR: 'forearm_R', HandR: 'hand_R',
  UpperLegL: 'thigh_L', LowerLegL: 'shin_L', FootL: 'foot_L',
  UpperLegR: 'thigh_R', LowerLegR: 'shin_R', FootR: 'foot_R',
};
