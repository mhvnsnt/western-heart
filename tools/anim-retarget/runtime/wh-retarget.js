/* ============================================================
   WESTERN HEART — runtime animation retargeting (wh-retarget.js)
   Part of tools/anim-retarget. Loads a source animation GLB
   (Mixamo / Rokoko export, Mixamo bone names) and retargets its
   clips onto a fighter's WH skeleton at load time, using the
   vendored three/addons SkeletonUtils.retargetClip (MIT, r160).

   Offline bake (tools/anim-retarget/retarget_blender.py) is preferred
   for shipped clips — this module is for rapid iteration and for
   clips that ship as data (e.g. a downloadable anim pack).

   Usage:
     import { loadRetargetedClips } from './wh-retarget.js';
     // after assets.loadModels(['demonio-body']):
     const clips = await loadRetargetedClips(
       assets.gltfs['demonio-body'],          // target: loaded fighter GLB
       'assets/anims/mixamo_punch.glb',       // source: animation GLB
       { inPlace: true }                      // pin Hips like AssetManager
     );
     fighter.playClip(clips['Punch']);
   ============================================================ */
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { retargetClip } from 'three/addons/utils/SkeletonUtils.js';

// Mixamo source bone -> WH target bone. WH is already Mixamo-named
// (tools/auto_rig/backends/skeleton_template.json), so this is the
// identity plus the `mixamo:` FBX prefix strip, kept in sync with
// tools/anim-retarget/bone_maps/mixamo_to_wh.json (nulls dropped).
const MIXAMO_PREFIXES = ['mixamo:', 'Mixamo:'];

function stripPrefix(name) {
  for (const p of MIXAMO_PREFIXES) if (name.startsWith(p)) return name.slice(p.length);
  return name;
}

/** Build { targetBoneName: sourceBoneName } for retargetClip. */
export function buildNameMap(targetRoot, sourceRoot) {
  const targetBones = new Set();
  targetRoot.traverse((o) => { if (o.isBone) targetBones.add(o.name); });
  const sourceBones = new Set();
  sourceRoot.traverse((o) => { if (o.isBone) sourceBones.add(o.name); });
  const names = {};
  for (const t of targetBones) {
    if (sourceBones.has(t)) { names[t] = t; continue; }          // exact
    for (const p of MIXAMO_PREFIXES) {                            // prefixed FBX
      if (sourceBones.has(p + t)) { names[t] = p + t; break; }
    }
  }
  return names;
}

function pinHipsToBind(clip, targetRoot) {
  let hipsBind = null;
  targetRoot.traverse((o) => {
    if (o.isBone && o.name === 'Hips' && !hipsBind) hipsBind = o.position.clone();
  });
  if (!hipsBind) return clip;
  for (const track of clip.tracks) {
    if (track.name === 'Hips.position') {
      for (let i = 0; i < track.values.length; i += 3) {
        track.values[i] = hipsBind.x;
        track.values[i + 1] = hipsBind.y;
        track.values[i + 2] = hipsBind.z;
      }
    }
  }
  return clip;
}

/**
 * Load animation GLB(s) and retarget every clip onto the target fighter.
 * @param {Object3D} targetRoot  loaded fighter scene (has .skeleton via SkinnedMesh)
 * @param {string|string[]} animUrls  source animation GLB URLs
 * @param {object} opts  { fps=30, inPlace=true, scaleRoot=true }
 * @returns {Promise<Object<string, AnimationClip>>} name -> retargeted clip
 */
export async function loadRetargetedClips(targetRoot, animUrls, opts = {}) {
  const { fps = 30, inPlace = true, scaleRoot = true } = opts;
  const urls = Array.isArray(animUrls) ? animUrls : [animUrls];
  const loader = new GLTFLoader();
  const out = {};

  // Target helper: first skinned mesh's skeleton defines the target rig
  let targetMesh = null;
  targetRoot.traverse((o) => { if (o.isSkinnedMesh && !targetMesh) targetMesh = o; });
  if (!targetMesh) throw new Error('wh-retarget: target has no SkinnedMesh');

  for (const url of urls) {
    const gltf = await loader.loadAsync(url);
    const names = buildNameMap(targetRoot, gltf.scene);
    const mapped = Object.keys(names).length;
    console.log(`[WH retarget] ${url}: ${mapped} bones mapped`);

    for (const clip of gltf.animations) {
      const retargeted = retargetClip(targetMesh, gltf.scene, clip, {
        fps,
        names,
        // keep the target's rest-pose proportions; scale handled below
        useFirstFramePosition: false,
      });
      retargeted.name = clip.name || url.split('/').pop().replace(/\.glb$/i, '');
      if (inPlace) pinHipsToBind(retargeted, targetRoot);
      if (scaleRoot) {
        // Match root-motion amplitude to the target's leg length so a
        // tall source doesn't moon-walk a short fighter.
        const srcHips = _boneWorldY(gltf.scene, names['Hips'] || 'Hips');
        const tgtHips = _boneWorldY(targetRoot, 'Hips');
        const s = tgtHips / Math.max(srcHips, 1e-6);
        if (isFinite(s) && Math.abs(s - 1) > 0.01) {
          for (const track of retargeted.tracks) {
            if (track.name === 'Hips.position') {
              for (let i = 0; i < track.values.length; i++) track.values[i] *= s;
            }
          }
        }
      }
      out[retargeted.name] = retargeted;
    }
  }
  return out;
}

function _boneWorldY(root, name) {
  let y = 1;
  root.traverse((o) => {
    if (o.isBone && o.name === name) {
      o.updateWorldMatrix(true, false);
      y = o.getWorldPosition(new THREE.Vector3()).y;
    }
  });
  return y;
}
