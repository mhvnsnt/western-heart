/* t3anims.js — REAL Tekken 3 animation clips for Western Heart.
 *
 * Loads the decoded T3 motion banks (wh-anim/1 JSON format) and converts
 * them to THREE.AnimationClip for the game's AnimationMixer.
 *
 * Source: assets/anim/t3/<bank>/*.json — one bank per decoded T3
 *         character (king, jin, xiaoyu, bryan, gunjack, yoshimitsu,
 *         paul, lei, nina, hwoarang, eddy, julia, anna, bosconovitch,
 *         heihachi, armorking), decoded from the owner's T3 disc via
 *         lab/tools/t3_motion_bake.py. Remainder banks + mokujin blocker:
 *         docs/anim/T3-REMAINDER-BANKS-20261020.md.
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
  // Remainder banks (2026-10-20, T3 bank remainder lane): REAL divmot
  // banks decoded from TEKKEN3.BNS through the same bake pipeline.
  // Heihachi's bake needed the pose-chain pivot override for his
  // geometry-less KMD parts 2/9/13 — see the remainder doc.
  // armorking = divmot03_king baked on King's OWN rig (Armor King has
  // no T3 divmot of his own; reached via the fighter.js override).
  // mokujin: NO bank — divmot15 is absent from the owner's disc image
  // (BNS entry 295 has size 0); no fighter references him as a source.
  paul:         'assets/anim/t3/paul/',
  lei:          'assets/anim/t3/lei/',
  nina:         'assets/anim/t3/nina/',
  hwoarang:     'assets/anim/t3/hwoarang/',
  eddy:         'assets/anim/t3/eddy/',
  julia:        'assets/anim/t3/julia/',
  anna:         'assets/anim/t3/anna/',
  bosconovitch: 'assets/anim/t3/bosconovitch/',
  heihachi:     'assets/anim/t3/heihachi/',
  armorking:    'assets/anim/t3/armorking/',
};

// Moveset source name -> bank key. 'demonio' is the game's rename of Jin
// (owner canon 2026-10-19: Tekken's Jin = DEMONIO). Fixup for fictitious
// sources: deviljin -> jin. bosconovitch and heihachi map to their REAL
// banks since 2026-10-20 (the old bosconovitch -> gunjack stand-in and
// the heihachi -> null dead end are retired: docfrank's frame data was
// built from Bosconovitch's real moveset, and the 9 heihachi-source
// fighters now get Heihachi's own clips).
export const SOURCE_TO_BANK = {
  king: 'king', demonio: 'jin', jin: 'jin', bryan: 'bryan',
  xiaoyu: 'xiaoyu', yoshimitsu: 'yoshimitsu', gunjack: 'gunjack',
  deviljin: 'jin',
  paul: 'paul', lei: 'lei', nina: 'nina', hwoarang: 'hwoarang',
  eddy: 'eddy', julia: 'julia', anna: 'anna',
  bosconovitch: 'bosconovitch', heihachi: 'heihachi',
  armorking: 'armorking', 'armor-king': 'armorking',
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
