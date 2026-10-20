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
  // Neutral standing stance = move-index slot 3 (n0madic/Tekken3Remake
  // docs/research/code/moves.md: row +0x10 stance slot, 3 = standing).
  // t3_stance.json is slot 0, a round-start intro move — not the idle.
  stance:  { file: 't3_neutral.json', loop: true  },
  intro:   { file: 't3_stance.json',  loop: false },
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
  crouch:  { file: 't3_crouch.json',  loop: false },  // stand -> crouch (slot 0x3b)
  crouchHold:{ file: 't3_crouch_hold.json', loop: true }, // crouching neutral (slot 40)
  backdash:{ file: 't3_backdash.json', loop: false },
  jumpUp:  { file: 't3_jump_up.json', loop: false },
  jumpFwd: { file: 't3_jump_fwd.json', loop: false },
  jumpBack:{ file: 't3_jump_back.json', loop: false },
  sidestepA:{ file: 't3_sidestep_a.json', loop: false },
  sidestepB:{ file: 't3_sidestep_b.json', loop: false },
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
  // Heihachi's OWN divmot13 motion stream, posed on Jin's T3 skeleton:
  // heihachi191's KMD has no hip/shoulder vertex data, so his body can't
  // be fitted (docs/anim/PROCEDURAL_AUDIT.md). tools/anim/t3_row_bake.py
  // --bank heihachi --kmd-from jin. Real Heihachi motion, Jin proportions.
  heihachi:   'assets/anim/t3/heihachi_on_jin/',
};

// Moveset source name -> bank key. 'demonio' is the game's rename of Jin
// (owner canon 2026-10-19: Tekken's Jin = DEMONIO). Fixups for fictitious
// sources: deviljin -> jin, bosconovitch -> gunjack. heihachi -> null.
export const SOURCE_TO_BANK = {
  king: 'king', demonio: 'jin', jin: 'jin', bryan: 'bryan',
  xiaoyu: 'xiaoyu', yoshimitsu: 'yoshimitsu', gunjack: 'gunjack',
  bosconovitch: 'gunjack', deviljin: 'jin',
  heihachi: 'heihachi',
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
  // Raw decoded frames stay on the clip: retargetT3Clips() rebuilds the
  // clip for each fighter rig from them (the canonical tracks below only
  // bind correctly on an identity-rest WH-Canonical rig).
  const raw = { fps, rot: data.rot_xyzw, root_t: data.root_t || null };
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
    // Lateral root drift (source frame, +x = the character's left):
    // tells side steps apart without guessing which slot goes where.
    lateralDx: raw.root_t && raw.root_t.length > 1 ? raw.root_t[raw.root_t.length - 1][0] - raw.root_t[0][0] : 0,
    raw,
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
/* wh-anim-pack/1 row -> the wh-anim/1 shape jsonToClip reads. */
function b64i16(str) {
  const bin = atob(str), n = bin.length >> 1, out = new Int16Array(n);
  for (let i = 0; i < n; i++) { const v = bin.charCodeAt(2 * i) | (bin.charCodeAt(2 * i + 1) << 8); out[i] = v >= 0x8000 ? v - 0x10000 : v; }
  return out;
}
function decodePackRow(pack, rec) {
  const q = b64i16(rec.q), rx = b64i16(rec.rx), ry = b64i16(rec.ry), rz = b64i16(rec.rz);
  const nb = pack.bones.length, n = rec.n, rot = {};
  pack.bones.forEach((b, bi) => {
    const arr = new Array(n);
    for (let f = 0; f < n; f++) { const o = (f * nb + bi) * 4; arr[f] = [q[o] / 32767, q[o + 1] / 32767, q[o + 2] / 32767, q[o + 3] / 32767]; }
    rot[b] = arr;
  });
  const root_t = new Array(n);
  for (let f = 0; f < n; f++) root_t[f] = [rx[f] / 1000, ry[f] / 1000, rz[f] / 1000];
  return { format: 'wh-anim/1', fps: pack.fps, bones: pack.bones, rot_xyzw: rot, root_t,
    bank: pack.bank, slot: rec.slot, move_row: rec.move_row };
}

const _t3clipCache = {};    // bankId -> { actionName: clip }
const _t3clipPromises = {}; // bankId -> Promise
const _t3skelCache = {};    // bankId -> wh-anim-skel/1 source skeleton

export async function loadT3Clips(THREE, bankId = 'king') {
  if (!bankId || !T3_BANKS[bankId]) return null;
  if (_t3clipCache[bankId]) return _t3clipCache[bankId];
  if (_t3clipPromises[bankId]) return _t3clipPromises[bankId];
  const base = T3_BANKS[bankId];
  _t3clipPromises[bankId] = (async () => {
    const clips = {};
    // Source skeleton of the rig this bank was baked onto
    // (tools/anim/t3_bank_skeleton.py) — required by retargetT3Clips.
    try {
      const res = await fetch(base + 'skeleton.json');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      _t3skelCache[bankId] = await res.json();
    } catch (e) {
      console.warn(`[WH-T3] ${bankId}/skeleton.json unavailable — bank cannot be retargeted:`, e.message || e);
    }
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
    // Every move row the fighters' movesets reference (rows.pack.json,
    // tools/anim/t3_row_bake.py): clips keyed 'row:<n>', played by the
    // move whose t3_row is n.
    jobs.push((async () => {
      try {
        const res = await fetch(base + 'rows.pack.json');
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const pack = await res.json();
        let n = 0;
        for (const [row, rec] of Object.entries(pack.rows || {})) {
          const clip = jsonToClip(`t3_${bankId}_row${row}`, decodePackRow(pack, rec), THREE);
          if (clip) { clip.userData.loop = false; clip.userData.move_row = rec.move_row; clips['row:' + row] = clip; n++; }
        }
        console.log(`[WH-T3] bank '${bankId}': ${n} move-row clips`);
      } catch (e) {
        console.warn(`[WH-T3] ${bankId}/rows.pack.json unavailable:`, e.message || e);
      }
    })());
    await Promise.all(jobs);
    console.log(`[WH-T3] bank '${bankId}': loaded ${Object.keys(clips).length} real T3 clips`);
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

/** Source skeleton (wh-anim-skel/1) of a loaded bank, or null. */
export function getT3Skeleton(bankId) { return _t3skelCache[bankId] || null; }

/* ============================================================
   RUNTIME RETARGET (2026-10-20) — the bank clips are LOCAL rotations
   of the identity-rest rig they were baked onto (skeleton.json).
   Played raw on a fighter rig whose bones have their own rest
   orientations (Mixamo: Hips rotated under 'Character', shoulders
   rolled 90°, Biped pelvis, ...) they pitch the body flat and gyro
   the arms — the collapse seen in every fight. This rebuilds each
   clip for the fighter's own rig with the same math the offline
   baker uses (lab/tools/t3_motion_bake.py retarget):
     G(j)  = world rotation of source joint j (compose the bank's
             local quats down the SOURCE hierarchy; rest = identity)
     A(c)  = swing taking the target bone's rest direction to the
             source bone's rest direction (Hips/Head: identity,
             Hand = ForeArm, Toe = Foot), in the target's frame
     D(c)  = F G(c) F^-1 A(c)   (F = 180° yaw when the rig faces -Z)
     W(k)  = D(driver(k)) Wrest(k);   local(k) = W(parent)^-1 W(k)
   Spine bones between hips and chest take slerp(D Hips, D Chest)
   (0.5 .. 1), neck bones take D Chest — both exactly as the baker.
   Hips height follows the bank's root_t, scaled by hip height.
   No values are authored here: every rotation comes from the
   decoded T3 frames and every rest pose from the two GLBs.
   ============================================================ */

// Canonical bone for a (GLTFLoader-sanitized) bone name: Mixamo
// (with or without the mixamorig prefix), 3ds Max Biped (Iori,
// DEATHFANG) and the L_/R_ naming of the Tekken-7-style rigs (Dio).
const CANON_SET = new Set(['Hips', 'Spine', 'Spine1', 'Spine2', 'Chest', 'Neck', 'Head',
  'LeftShoulder', 'LeftArm', 'LeftForeArm', 'LeftHand', 'RightShoulder', 'RightArm', 'RightForeArm', 'RightHand',
  'LeftUpLeg', 'LeftLeg', 'LeftFoot', 'LeftToeBase', 'RightUpLeg', 'RightLeg', 'RightFoot', 'RightToeBase']);
const BIPED = { Pelvis: 'Hips', Spine: 'Spine', Spine1: 'Spine1', Spine2: 'Spine2', Neck: 'Neck', Head: 'Head',
  Clavicle: 'Shoulder', UpperArm: 'Arm', Forearm: 'ForeArm', Hand: 'Hand',
  Thigh: 'UpLeg', Calf: 'Leg', Foot: 'Foot', Toe0: 'ToeBase' };
const LR_STYLE = { Shoulder: 'Shoulder', Arm: 'Arm', ForeArm: 'ForeArm', Hand: 'Hand',
  UpLeg: 'UpLeg', Leg: 'Leg', Foot: 'Foot', Toe: 'ToeBase' };
export function canonBoneName(name) {
  let n = String(name).replace(/^mixamorig[:_]?/i, '');
  if (CANON_SET.has(n)) return n;
  n = n.replace(/_\d+$/, '');                    // Sketchfab index suffix (Head_019)
  if (CANON_SET.has(n)) return n;
  let m = n.match(/^Bip0*1_(?:(L|R)_)?([A-Za-z]+\d?)$/); // Biped: Bip001_L_Thigh
  if (m && BIPED[m[2]]) {
    const part = BIPED[m[2]];
    if (!m[1]) return ['Hips', 'Spine', 'Spine1', 'Spine2', 'Neck', 'Head'].includes(part) ? part : null;
    return (m[1] === 'L' ? 'Left' : 'Right') + part;
  }
  m = n.match(/^(L|R)_([A-Za-z]+)$/);           // T7-style: L_ForeArm
  if (m && LR_STYLE[m[2]]) return (m[1] === 'L' ? 'Left' : 'Right') + LR_STYLE[m[2]];
  if (n === 'Hip' || n === 'Pelvis') return 'Hips';
  return null;
}

const RIG_REQUIRED = ['Hips', 'Head', 'LeftArm', 'LeftForeArm', 'LeftHand', 'RightArm', 'RightForeArm', 'RightHand',
  'LeftUpLeg', 'LeftLeg', 'LeftFoot', 'RightUpLeg', 'RightLeg', 'RightFoot'];

/* Rest-pose analysis of a fighter rig, in the model's own space.
   Must run before the instance's mixer first updates (rest pose). */
function analyzeRig(model, THREE) {
  model.updateMatrixWorld(true);
  const inv = new THREE.Matrix4().copy(model.matrixWorld).invert();
  const bones = [];
  model.traverse((o) => { if (o.isBone) bones.push(o); });
  const by = {};
  for (const b of bones) {
    const c = canonBoneName(b.name);
    if (c && !by[c]) by[c] = b;
  }
  if (RIG_REQUIRED.some(c => !by[c])) return null;
  // Anatomical sides come from the MESH, not the bone labels: the
  // instance space has the mesh facing +Z (assets.js), so the
  // character's left is +X. The auto-rig template skeleton faces -Z, and
  // when it sits in a +Z mesh its Left* bones lie on the mesh's right
  // (verified on rest renders, docs/proof/claude-2026-10-20/model-facing).
  // Such rigs are driven with sides swapped so the mesh's left arm takes
  // the source's left arm.
  model.updateMatrixWorld(true);
  const xOf = (b) => new THREE.Vector3().setFromMatrixPosition(new THREE.Matrix4().multiplyMatrices(inv, b.matrixWorld)).x;
  const swapLR = xOf(by.LeftArm) < xOf(by.RightArm);
  if (swapLR) {
    const sw = {};
    for (const [c, b] of Object.entries(by)) {
      const m = c.match(/^(Left|Right)(.*)$/);
      sw[m ? (m[1] === 'Left' ? 'Right' : 'Left') + m[2] : c] = b;
    }
    for (const k of Object.keys(by)) delete by[k];
    Object.assign(by, sw);
  }
  const restOf = new Map(); // Object3D -> { pos, quat, mat } in model space
  const tmpS = new THREE.Vector3();
  const rest = (o) => {
    if (restOf.has(o)) return restOf.get(o);
    const mat = new THREE.Matrix4().multiplyMatrices(inv, o.matrixWorld);
    const pos = new THREE.Vector3(), quat = new THREE.Quaternion();
    mat.decompose(pos, quat, tmpS);
    const r = { pos, quat, mat };
    restOf.set(o, r);
    return r;
  };
  bones.forEach(rest);
  const isAnc = (a, b) => { for (let o = b.parent; o; o = o.parent) if (o === a) return true; return false; };
  // Chest = lowest common ancestor of the two upper arms, stepping
  // below a Biped neck (Biped clavicles hang off the neck).
  const ancL = [];
  for (let o = by.LeftArm.parent; o && o !== model; o = o.parent) ancL.push(o);
  let chest = null;
  for (let o = by.RightArm.parent; o && o !== model && !chest; o = o.parent) if (ancL.includes(o)) chest = o;
  while (chest && ['Neck', 'Head'].includes(canonBoneName(chest.name)) && chest.parent && chest.parent.isBone) chest = chest.parent;
  if (!chest || !chest.isBone) return null;
  // Drivers. Spine chain: chest's ancestors that are not ancestors of
  // the hips (and are not the hips). Neck chain: chest -> head.
  const driver = new Map();
  for (const [c, b] of Object.entries(by)) {
    if (['Spine', 'Spine1', 'Spine2', 'Chest', 'Neck'].includes(c)) continue;
    driver.set(b, { c });
  }
  driver.set(chest, { c: 'Chest' });
  const spine = [];
  for (let o = chest.parent; o && o !== model && o.isBone; o = o.parent) {
    if (o === by.Hips || isAnc(o, by.Hips)) break;
    spine.unshift(o);
  }
  spine.forEach((b, i) => driver.set(b, { slerp: 0.5 + 0.5 * i / spine.length }));
  for (let o = by.Head.parent; o && o !== chest && o.isBone; o = o.parent) driver.set(o, { c: 'Chest' });
  // Facing: the instance space has the mesh facing +Z (assets.js), the
  // same as the canonical source rigs, so no facing flip is needed here.
  const facesNegZ = false;
  // Bone rest directions (model space) for the swing alignment.
  const dir = (a, b) => (a && b) ? new THREE.Vector3().subVectors(rest(b).pos, rest(a).pos) : null;
  let neckRef = by.Neck && by.Neck !== chest && isAnc(chest, by.Neck) ? by.Neck : by.Head;
  const dirs = { Chest: dir(chest, neckRef) };
  for (const s of ['Left', 'Right']) {
    dirs[s + 'Shoulder'] = by[s + 'Shoulder'] ? dir(by[s + 'Shoulder'], by[s + 'Arm']) : null;
    dirs[s + 'Arm'] = dir(by[s + 'Arm'], by[s + 'ForeArm']);
    dirs[s + 'ForeArm'] = dir(by[s + 'ForeArm'], by[s + 'Hand']);
    dirs[s + 'UpLeg'] = dir(by[s + 'UpLeg'], by[s + 'Leg']);
    dirs[s + 'Leg'] = dir(by[s + 'Leg'], by[s + 'Foot']);
    dirs[s + 'Foot'] = by[s + 'ToeBase'] ? dir(by[s + 'Foot'], by[s + 'ToeBase']) : null;
    // A toe joint pointing behind the heel (template skeleton in a +Z mesh)
    // would swing the whole foot round; such a foot keeps its rest relation
    // to the shin instead (A(Foot) = A(Leg)).
    if (dirs[s + 'Foot'] && dirs[s + 'Foot'].z < 0) dirs[s + 'Foot'] = 'leg';
  }
  // Track names must resolve to exactly one node under the model.
  const nameCount = {};
  model.traverse((o) => { nameCount[o.name] = (nameCount[o.name] || 0) + 1; });
  return { bones, by, chest, driver, rest, facesNegZ, swapLR, dirs, hipsY: rest(by.Hips).pos.y,
    trackName: (b) => (nameCount[b.name] === 1 ? b.name : b.uuid), uniqueNames: bones.every(b => nameCount[b.name] === 1) };
}

/* Source-side data per bank: hierarchy order + rest directions. */
function sourceInfo(skel, THREE) {
  if (skel._info) return skel._info;
  const P = {}, par = {};
  for (const j of skel.joints) { P[j.name] = new THREE.Vector3().fromArray(j.rest); par[j.name] = j.parent; }
  const d = (a, b) => (P[a] && P[b]) ? new THREE.Vector3().subVectors(P[b], P[a]) : null;
  const dirs = { Chest: P.Neck ? d('Chest', 'Neck') : d('Chest', 'Head') };
  for (const s of ['Left', 'Right']) {
    dirs[s + 'Shoulder'] = d(s + 'Shoulder', s + 'Arm');
    dirs[s + 'Arm'] = d(s + 'Arm', s + 'ForeArm');
    dirs[s + 'ForeArm'] = d(s + 'ForeArm', s + 'Hand');
    dirs[s + 'UpLeg'] = d(s + 'UpLeg', s + 'Leg');
    dirs[s + 'Leg'] = d(s + 'Leg', s + 'Foot');
    const tip = P[s + 'ToeBase'] || (skel.foot_tip && skel.foot_tip[s + 'Foot'] ? new THREE.Vector3().fromArray(skel.foot_tip[s + 'Foot']) : null);
    dirs[s + 'Foot'] = tip && P[s + 'Foot'] ? new THREE.Vector3().subVectors(tip, P[s + 'Foot']) : null;
  }
  skel._info = { order: skel.joints.map(j => j.name), par, dirs, rootY: skel.root_rest_y };
  return skel._info;
}

const _retargetCache = new WeakMap(); // model instance -> Map(bankId -> { rig, out: { action: clip } })

/**
 * Retarget a bank's clips onto one fighter model. The FIRST call for a
 * key must happen right after createInstance, before the mixer first
 * updates: it captures the rig's rest pose. Returns
 * { actionName: THREE.AnimationClip } with tracks bound to the model's
 * own bones, or null when the rig lacks the core humanoid bones (the
 * fighter then keeps its embedded/procedural layer).
 * The captured rig is cached per model instance (WeakMap): later calls
 * reuse that rest pose, so move rows ('row:<n>', skipped unless named in
 * `only`) can be retargeted lazily mid-fight. `instanceKey` only names
 * the clips.
 */
export function retargetT3Clips(t3Clips, bankId, model, THREE, instanceKey = null, only = null) {
  const skel = _t3skelCache[bankId];
  if (!t3Clips || !skel) return null;
  let perModel = _retargetCache.get(model);
  if (!perModel) { perModel = new Map(); _retargetCache.set(model, perModel); }
  const cached = perModel.get(bankId);
  if (cached === null) return null;
  const names = only || Object.keys(t3Clips).filter(n => !n.startsWith('row:')); // rows retarget on demand
  if (cached && names.every(n => cached.out[n] || !t3Clips[n])) {
    const o = {}; for (const n of names) if (cached.out[n]) o[n] = cached.out[n];
    return o;
  }
  const rig = (cached && cached.rig) || analyzeRig(model, THREE);
  if (!rig) { perModel.set(bankId, null); return null; }
  const src = sourceInfo(skel, THREE);
  const F = new THREE.Quaternion();
  if (rig.facesNegZ) F.setFromAxisAngle(new THREE.Vector3(0, 1, 0), Math.PI);
  const Finv = F.clone().invert();
  // A(c): target rest dir -> source rest dir (source dir brought into the target frame by F).
  const A = {};
  for (const c of Object.keys(src.dirs)) {
    const ds = src.dirs[c], dt = rig.dirs[c];
    A[c] = new THREE.Quaternion();
    if (ds && dt && dt !== 'leg' && ds.lengthSq() > 1e-10 && dt.lengthSq() > 1e-10) {
      A[c].setFromUnitVectors(dt.clone().normalize(), ds.clone().applyQuaternion(F).normalize());
    }
  }
  for (const s of ['Left', 'Right']) {
    if (rig.dirs[s + 'Foot'] === 'leg') A[s + 'Foot'] = A[s + 'Leg'];
    A[s + 'Hand'] = A[s + 'ForeArm']; A[s + 'ToeBase'] = A[s + 'Foot'];
  }
  // Hips position: parent space transform + hip-height scale.
  const hips = rig.by.Hips;
  const hipsParentInv = hips.parent ? new THREE.Matrix4().copy(rig.rest(hips.parent).mat).invert() : null;
  const hipScale = src.rootY > 1e-3 ? rig.hipsY / src.rootY : 1;
  const hipsRest = rig.rest(hips).pos;
  // Hierarchy order of the target bones (parents before children).
  const ordered = rig.bones;
  const driven = ordered.filter(b => rig.driver.has(b));

  const out = {};
  const G = {}, D = {}, W = new Map();
  const tmpQ = new THREE.Quaternion(), tmpV = new THREE.Vector3();
  for (const action of names) {
    const clip = t3Clips[action];
    if (cached && cached.out[action]) { out[action] = cached.out[action]; continue; }
    const raw = clip && clip.userData && clip.userData.raw;
    if (!raw) continue;
    let n = 0;
    for (const j of src.order) if (raw.rot[j] && raw.rot[j].length > n) n = raw.rot[j].length;
    if (!n) continue;
    const times = new Float32Array(n);
    for (let i = 0; i < n; i++) times[i] = i / raw.fps;
    const vals = new Map(driven.map(b => [b, new Float32Array(n * 4)]));
    const hipPos = raw.root_t && hipsParentInv ? new Float32Array(n * 3) : null;
    for (let f = 0; f < n; f++) {
      // G: source world rotations down the source hierarchy.
      for (const j of src.order) {
        const q = G[j] || (G[j] = new THREE.Quaternion());
        const r = raw.rot[j];
        if (r && r.length) { const v = r[Math.min(f, r.length - 1)]; q.set(v[0], v[1], v[2], v[3]); } else q.identity();
        const p = src.par[j];
        if (p && G[p]) q.premultiply(G[p]);
      }
      // D: world deltas in the target frame.
      const delta = (c) => {
        const d = D[c] || (D[c] = new THREE.Quaternion());
        if (!G[c]) return d.identity();
        d.copy(F).multiply(G[c]).multiply(Finv);
        if (A[c]) d.multiply(A[c]);
        return d;
      };
      for (const c of ['Hips', 'Chest', 'Head', 'LeftShoulder', 'LeftArm', 'LeftForeArm', 'LeftHand',
        'RightShoulder', 'RightArm', 'RightForeArm', 'RightHand', 'LeftUpLeg', 'LeftLeg', 'LeftFoot',
        'RightUpLeg', 'RightLeg', 'RightFoot']) delta(c);
      // Bank has no Shoulder joint -> shoulder follows the chest (as the baker's nearest-ancestor rule).
      for (const s of ['Left', 'Right']) {
        if (!G[s + 'Shoulder']) D[s + 'Shoulder'] = (D[s + 'Shoulder'] || new THREE.Quaternion()).copy(D.Chest);
        D[s + 'ToeBase'] = (D[s + 'ToeBase'] || new THREE.Quaternion()).copy(D[s + 'Foot']);
      }
      // W per target bone, then local.
      W.clear();
      for (const b of ordered) {
        const dv = rig.driver.get(b);
        const w = new THREE.Quaternion();
        if (dv) {
          if (dv.slerp !== undefined) w.slerpQuaternions(D.Hips, D.Chest, dv.slerp);
          else w.copy(D[dv.c] || tmpQ.identity());
          w.multiply(rig.rest(b).quat);
        } else {
          const pw = b.parent && W.get(b.parent);
          if (pw) w.copy(pw).multiply(b.quaternion); // follows its (driven) parent at rest local
          else w.copy(rig.rest(b).quat);
        }
        W.set(b, w);
        if (dv) {
          const pw = (b.parent && W.get(b.parent)) || (b.parent ? rig.rest(b.parent).quat : tmpQ.identity());
          const local = tmpQ.copy(pw).invert().multiply(w);
          vals.get(b).set([local.x, local.y, local.z, local.w], f * 4);
        }
      }
      if (hipPos) {
        const rt = raw.root_t[Math.min(f, raw.root_t.length - 1)];
        tmpV.set(hipsRest.x, hipsRest.y + (rt[1] - src.rootY) * hipScale, hipsRest.z).applyMatrix4(hipsParentInv);
        hipPos.set([tmpV.x, tmpV.y, tmpV.z], f * 3);
      }
    }
    const tracks = [];
    for (const b of driven) {
      const v = vals.get(b);
      // keep quaternion sign continuity for clean interpolation
      for (let f = 1; f < n; f++) {
        const o = (f - 1) * 4, c = f * 4;
        if (v[o] * v[c] + v[o + 1] * v[c + 1] + v[o + 2] * v[c + 2] + v[o + 3] * v[c + 3] < 0) {
          v[c] = -v[c]; v[c + 1] = -v[c + 1]; v[c + 2] = -v[c + 2]; v[c + 3] = -v[c + 3];
        }
      }
      tracks.push(new THREE.QuaternionKeyframeTrack(`${rig.trackName(b)}.quaternion`, times, v));
    }
    if (hipPos) tracks.push(new THREE.VectorKeyframeTrack(`${rig.trackName(hips)}.position`, times, hipPos));
    const rc = new THREE.AnimationClip(`${clip.name}@${instanceKey || 'rig'}`, n / raw.fps, tracks);
    rc.userData = { ...clip.userData, raw: undefined, retargeted: true, rigFacesNegZ: rig.facesNegZ, rigSwapLR: rig.swapLR };
    out[action] = rc;
  }
  const c = cached || { rig, out: {} };
  Object.assign(c.out, out);
  perModel.set(bankId, c);
  return out;
}
