/* t3anims.js — REAL Tekken 3 animation clips for Western Heart.
 *
 * Loads Grok's decoded T3 King motion (wh-anim/1 JSON format) and converts
 * to THREE.AnimationClip for the game's AnimationMixer.
 *
 * Source: assets/anim/t3/king_on_pantera_leoman/*.json
 *         (decoded from owner's T3 disc via lab/tools/t3_motion_bake.py)
 * Provenance: REAL T3 motion data, not procedural. See docs/anim/PROCEDURAL_AUDIT.md.
 *
 * Bone names in the JSON (Hips, Spine, etc.) match the game's stripped
 * Mixamo bone names (mixamorigHips -> Hips), so tracks bind directly.
 */

const T3_CLIP_DEFS = {
  // Game action -> T3 clip file + playback mode
  stance:  { file: 't3_stance.json',  loop: true  },
  light:   { file: 't3_light.json',   loop: false },  // punch (J)
  medium:  { file: 't3_medium.json',  loop: false },  // kick (K)
  heavy:   { file: 't3_heavy.json',   loop: false },  // heavy attack
  grab:    { file: 't3_grab.json',    loop: false },  // command grab (U)
  block:   { file: 't3_block.json',   loop: true  },  // block hold
  hit:     { file: 't3_hit.json',     loop: false },  // hitstun reaction
  launch:  { file: 't3_hit_launch.json', loop: false }, // launched
  ko:      { file: 't3_ko.json',      loop: false },  // knocked out
  win:     { file: 't3_win_rp.json',  loop: true  },  // victory pose
  walkFwd: { file: 't3_walk_fwd.json', loop: true },
  walkBack:{ file: 't3_walk_back.json', loop: true },
  dash:    { file: 't3_dash_fwd.json', loop: false },
  crouch:  { file: 't3_crouch.json',  loop: true  },
};

// Bones in the game's Mixamo skeleton that the T3 clips drive.
// T3 JSON uses these exact names (Root/Hips/Spine/etc.).
const T3_BONES = ['Root','Hips','Spine','Chest','Neck','Head',
  'LeftShoulder','LeftArm','LeftForeArm','LeftHand',
  'RightShoulder','RightArm','RightForeArm','RightHand',
  'LeftUpLeg','LeftLeg','LeftFoot','LeftToeBase',
  'RightUpLeg','RightLeg','RightFoot','RightToeBase'];

// Base URL for T3 clip JSONs. NOTE (teardown-integration 2026-10-19): the
// decoded clip JSONs live at the REPO ROOT (assets/anim/t3/...), not under
// game/assets/anim/ — game/ is a subpath, so this resolves up one level.
// The old base 404'd every clip and the real T3 motion never loaded.
const T3_ANIM_BASE = '../assets/anim/t3/king_on_pantera_leoman/';

/**
 * Convert a wh-anim/1 JSON object to a THREE.AnimationClip.
 * - Quaternion tracks per bone (Hips.quaternion, etc.)
 * - NO position tracks (in-place; game drives root.position for locomotion)
 * - Root motion (root_t) is SKIPPED — the game handles positioning.
 *   This matches the existing Hips bind-pose pinning philosophy.
 */
function jsonToClip(name, data, THREE) {
  const fps = data.fps || 30.0;
  const tracks = [];

  // Frame count from the rotation arrays (they're the authoritative length)
  const bones = data.bones || T3_BONES;
  let frameCount = 0;
  for (const b of bones) {
    const arr = data.rot_xyzw[b];
    if (arr && arr.length > frameCount) frameCount = arr.length;
  }
  if (frameCount === 0) {
    console.warn(`[WH-T3] ${name}: no rotation frames`);
    return null;
  }

  // Build time array (evenly spaced at fps)
  const times = new Float32Array(frameCount);
  for (let i = 0; i < frameCount; i++) times[i] = i / fps;

  for (const bone of bones) {
    const quats = data.rot_xyzw[bone];
    if (!quats || quats.length === 0) continue;
    // Flatten [x,y,z,w] per frame into values array
    const values = new Float32Array(frameCount * 4);
    for (let i = 0; i < frameCount; i++) {
      const q = quats[Math.min(i, quats.length - 1)];
      values[i * 4] = q[0]; values[i * 4 + 1] = q[1];
      values[i * 4 + 2] = q[2]; values[i * 4 + 3] = q[3];
    }
    // Track name matches bone node name in the scene (Hips, Spine, etc.)
    tracks.push(new THREE.QuaternionKeyframeTrack(`${bone}.quaternion`, times, values));
  }

  const clip = new THREE.AnimationClip(name, frameCount / fps, tracks);
  clip.userData = {
    source: 'REAL T3 decoded motion',
    bank: data.bank,
    slot: data.slot,
    move_row: data.move_row,
    sha256: data.sha256,
  };
  return clip;
}

/**
 * Load all T3 clips. Returns { actionName: THREE.AnimationClip }.
 * Failures are logged but don't throw — the game falls back to procedural.
 * Results are cached module-level so Fighters can access synchronously.
 */
let _t3clipCache = null;
let _t3clipPromise = null;

export async function loadT3Clips(THREE) {
  if (_t3clipCache) return _t3clipCache;
  if (_t3clipPromise) return _t3clipPromise;
  _t3clipPromise = (async () => {
    const clips = {};
    const jobs = Object.entries(T3_CLIP_DEFS).map(async ([action, def]) => {
      try {
        const res = await fetch(T3_ANIM_BASE + def.file);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        if (data.format !== 'wh-anim/1') {
          console.warn(`[WH-T3] ${def.file}: unexpected format ${data.format}`);
        }
        const clip = jsonToClip(`t3_${action}`, data, THREE);
        if (clip) {
          clip.userData.loop = def.loop;
          clips[action] = clip;
        }
      } catch (e) {
        console.warn(`[WH-T3] failed to load ${def.file}:`, e.message || e);
      }
    });
    await Promise.all(jobs);
    console.log(`[WH-T3] loaded ${Object.keys(clips).length}/${Object.keys(T3_CLIP_DEFS).length} real T3 clips`);
    _t3clipCache = clips;
    return clips;
  })();
  return _t3clipPromise;
}

/** Synchronous accessor for cached clips (null if not loaded yet). */
export function getT3Clips() { return _t3clipCache; }

/**
 * Create mixer actions for T3 clips on a fighter's mixer.
 * Returns { actionName: AnimationAction }.
 */
export function createT3Actions(mixer, t3Clips, THREE) {
  const actions = {};
  for (const [name, clip] of Object.entries(t3Clips)) {
    try {
      const action = mixer.clipAction(clip);
      const loop = clip.userData.loop;
      action.setLoop(loop ? THREE.LoopRepeat : THREE.LoopOnce, Infinity);
      action.clampWhenFinished = !loop;
      action.enabled = true;
      action.setEffectiveWeight(0);
      actions[name] = action;
    } catch (e) {
      console.warn(`[WH-T3] failed to create action for ${name}:`, e.message || e);
    }
  }
  return actions;
}
