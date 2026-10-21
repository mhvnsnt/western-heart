/* t3anims.js — REAL Tekken 3 animation clips for Western Heart.
 *
 * Loads the decoded T3 motion banks (wh-anim/1 JSON format) and converts
 * them to THREE.AnimationClip for the game's AnimationMixer.
 *
 * Source: assets/anim/t3/<bank>/*.json — one bank per decoded T3
 *         character (king, jin, xiaoyu, bryan, gunjack, yoshimitsu),
 *         decoded from the owner's T3 disc via lab/tools/t3_motion_bake.py.
 * Provenance: REAL T3 motion data, not procedural. See docs/anim/PROCEDURAL_AUDIT.md.
 *
 * Bone names in the JSON (Hips, Spine, etc.) match the game's stripped
 * Mixamo bone names (mixamorigHips -> Hips), so tracks bind directly.
 * Each fighter plays ONLY their own moveset source's bank (see
 * SOURCE_TO_BANK + fighter.js bankIdFor) — a fighter must never be
 * animated with a different character's clips.
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

// Decoded T3 motion banks. Real teardown animation data (wh-anim/1 JSON),
// one bank per T3 character decoded so far.
// Paths are relative to the game page like every other game asset
// (assets/portraits, assets/*_moves.json). DEPLOY NOTE (verified live
// 2026-10-19): the game is served at the site root, so the previous
// '../assets/anim/...' base resolved ABOVE the game and 404'd every
// clip in production — the banks must live under game/assets/anim/.
export const T3_BANKS = {
  king:       'assets/anim/t3/king_on_pantera_leoman/',
  jin:        'assets/anim/t3/jin/',
  xiaoyu:     'assets/anim/t3/xiaoyu/',
  bryan:      'assets/anim/t3/bryan/',
  gunjack:    'assets/anim/t3/gunjack/',
  yoshimitsu: 'assets/anim/t3/yoshimitsu/',
  // heihachi: no decoded bank exists (raw divmot only) — intentionally absent.
};

// Moveset source name -> bank key. 'demonio' is the game's rename of Jin
// (owner canon 2026-10-19: Tekken's Jin = DEMONIO). Fixups for fictitious
// sources: deviljin -> jin, bosconovitch -> gunjack. heihachi -> null.
export const SOURCE_TO_BANK = {
  king: 'king', demonio: 'jin', jin: 'jin', bryan: 'bryan',
  xiaoyu: 'xiaoyu', yoshimitsu: 'yoshimitsu', gunjack: 'gunjack',
  bosconovitch: 'gunjack', deviljin: 'jin',
  heihachi: null,
};

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
 * Per-bank loading (GYRO-ARMS FIX 2026-10-19): loadT3Clips(THREE, bankId)
 * loads ONE character bank; results are cached per bank so Fighters can
 * access them synchronously via getT3Clips(bankId). Failures are logged
 * but don't throw — the game falls back to procedural.
 */
const _t3clipCache = {};    // bankId -> { actionName: clip }
const _t3clipPromises = {}; // bankId -> Promise

export async function loadT3Clips(THREE, bankId = 'king') {
  if (!bankId || !T3_BANKS[bankId]) return null;
  if (_t3clipCache[bankId]) return _t3clipCache[bankId];
  if (_t3clipPromises[bankId]) return _t3clipPromises[bankId];
  const base = T3_BANKS[bankId];
  _t3clipPromises[bankId] = (async () => {
    const clips = {};
    const jobs = Object.entries(T3_CLIP_DEFS).map(async ([action, def]) => {
      try {
        const res = await fetch(base + def.file);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        if (data.format !== 'wh-anim/1') {
          console.warn(`[WH-T3] ${bankId}/${def.file}: unexpected format ${data.format}`);
        }
        const clip = jsonToClip(`t3_${bankId}_${action}`, data, THREE);
        if (clip) {
          clip.userData.loop = def.loop;
          clips[action] = clip;
        }
      } catch (e) {
        console.warn(`[WH-T3] failed to load ${bankId}/${def.file}:`, e.message || e);
      }
    });
    await Promise.all(jobs);
    console.log(`[WH-T3] bank '${bankId}': loaded ${Object.keys(clips).length}/${Object.keys(T3_CLIP_DEFS).length} real T3 clips`);
    _t3clipCache[bankId] = clips;
    return clips;
  })();
  return _t3clipPromises[bankId];
}

/** Synchronous accessor for one bank's cached clips (null if not loaded). */
export function getT3Clips(bankId = 'king') { return _t3clipCache[bankId] || null; }

/* Canonical -> target-rig bone retargets. The T3 banks were baked against
   the WH-CANONICAL-22 rig (lab/tools/t3_motion_bake.py), whose bone-local
   rest rotations are ALL identity — verified 2026-10-20 against the baked
   GLBs (lab/game/assets/t3_*_t3real.glb): every recoverable canonical
   rest local is exactly [0,0,0,1]. Game models are Mixamo-style: no
   'Root' node, no 'Chest' node (the chest segment is Spine2 in the chain
   Hips->Spine->Spine1->Spine2->Neck, mirroring canonical
   Hips->Spine->Chest->Neck), and some bind locals are rotated ~180 deg
   from canonical (e.g. pantera Hips [0,.707,.707,0], UpLegs 180 deg X).
   Chest's delta therefore lands on Spine2; Root has no counterpart and
   its track (identity in the banks) is dropped. */
const CANON_TO_TARGET = { Chest: 'Spine2' };

/* BIND-RELATIVE RETARGET (frozen/folded-pose fix, 2026-10-20).
   Bank JSONs carry ABSOLUTE bone-local quaternions for the identity-rest
   canonical rig. Applied raw to a Mixamo bone whose bind local is
   non-identity, the clip's absolute frame replaces the bind frame and
   the body folds (FK check on pantera + king stance, frame 37: raw clip
   puts the head at hip height, pitched horizontal, feet folded up;
   converted clip stands upright at bind head height). Conversion per
   bone: out(t) = targetBindLocal * clipQuat(t) — the canonical rest is
   identity, so the clip quat IS the bind-relative delta. Tracks whose
   target bone is missing are dropped; tracks on identity-bind bones
   with no rename pass through untouched. Returns the original clip when
   nothing needed converting. */
function retargetClipToRig(clip, bind, THREE) {
  let changed = false;
  const tracks = [];
  const tmp = new THREE.Quaternion();
  for (const track of clip.tracks) {
    const dot = track.name.indexOf('.');
    const bone = dot >= 0 ? track.name.slice(0, dot) : track.name;
    // Chest -> Spine2 ONLY when the rig has no Chest of its own but does
    // have Spine2 (Mixamo). Rigs that carry a real Chest (e.g. the Vega
    // foreign-rig remap in assets.js) keep their Chest track as-is.
    const target = (bone === 'Chest' && !bind.Chest && bind.Spine2) ? CANON_TO_TARGET.Chest : bone;
    const bq = bind[target];
    if (!bq) { changed = true; continue; } // no such bone on this rig (e.g. Root)
    const identityBind = (bq.x * bq.x + bq.y * bq.y + bq.z * bq.z) < 1e-8;
    if (target === bone && identityBind) { tracks.push(track); continue; }
    changed = true;
    const values = new Float32Array(track.values.length);
    for (let i = 0; i < track.values.length; i += 4) {
      tmp.set(track.values[i], track.values[i + 1], track.values[i + 2], track.values[i + 3]);
      tmp.premultiply(bq); // out = bind * clip
      values[i] = tmp.x; values[i + 1] = tmp.y; values[i + 2] = tmp.z; values[i + 3] = tmp.w;
    }
    tracks.push(new THREE.QuaternionKeyframeTrack(`${target}.quaternion`, track.times, values));
  }
  if (!changed) return clip;
  const converted = new THREE.AnimationClip(clip.name, clip.duration, tracks);
  converted.userData = clip.userData;
  return converted;
}

/**
 * Create mixer actions for T3 clips on a fighter's mixer.
 * Clips are retargeted to the mixer's rig bind pose (see above) before
 * actions are created — the cached bank clips stay canonical, each
 * fighter's actions carry rig-space tracks.
 * Returns { actionName: AnimationAction }.
 */
export function createT3Actions(mixer, t3Clips, THREE) {
  // Target rig bind locals, keyed by stripped bone name (same stripping
  // as the bones dict in assets.js). Read before the mixer ever poses the
  // model — Fighter constructs actions on a fresh bind-pose instance.
  const bind = {};
  const rootObj = mixer.getRoot();
  if (rootObj && rootObj.traverse) {
    rootObj.traverse((o) => {
      if (o.isBone) {
        const nm = o.name.replace(/^mixamorig:?/, '');
        if (!(nm in bind)) bind[nm] = o.quaternion.clone();
      }
    });
  }
  const actions = {};
  for (const [name, clip] of Object.entries(t3Clips)) {
    try {
      const action = mixer.clipAction(retargetClipToRig(clip, bind, THREE));
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
