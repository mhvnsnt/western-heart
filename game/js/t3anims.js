/* t3anims.js — REAL Tekken 3 animation clips for Western Heart.
 *
 * Loads the decoded T3 motion banks (wh-anim/1 JSON format) and converts
 * them to THREE.AnimationClip for the game's AnimationMixer.
 *
 * Source: assets/anim/t3/<bank>/*.json — one bank per decoded T3
 *         character (king, jin, xiaoyu, bryan, gunjack, yoshimitsu,
 *         paul, lei, nina, hwoarang, eddy, julia, anna, bosconovitch,
 *         armorking; heihachi = heihachi_on_jin, plus an own-rig
 *         heihachi_ownrig decode), decoded from the owner's T3 disc via
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
  // Neutral standing stance = move-index slot 3 (n0madic/Tekken3Remake
  // docs/research/code/moves.md: row +0x10 stance slot, 3 = standing).
  // t3_stance.json is slot 0, a round-start intro move — not the idle.
  //
  // SHOW-ANIMATION LOCK (owner 2026-10-23): show animations and fight moves
  // are SEPARATE LOCKED SETS. Actions flagged show:true (intro, win poses)
  // are SHOW: intros/cutscenes ONLY, must NEVER enter a fighter's moveset
  // without the user's explicit approval. Everything else is FIGHT.
  // Bank clip JSONs carry the same split as "anim_set" (+ sets.json manifest).
  stance:  { file: 't3_neutral.json', loop: true  },
  intro:   { file: 't3_stance.json',  loop: false, show: true },
  light:   { file: 't3_light.json',   loop: false },  // punch (J)
  medium:  { file: 't3_medium.json',  loop: false },  // kick (K)
  heavy:   { file: 't3_heavy.json',   loop: false },  // heavy attack
  grab:    { file: 't3_grab.json',    loop: false },  // command grab (U)
  block:   { file: 't3_block.json',   loop: true  },  // block hold
  hit:     { file: 't3_hit.json',     loop: false },  // hitstun reaction
  launch:  { file: 't3_hit_launch.json', loop: false, noRise: true }, // launched (physics owns the arc)
  ko:      { file: 't3_ko.json',      loop: false },  // knocked out
  win:     { file: 't3_win_rp.json',  loop: true, show: true },  // victory pose (SHOW)
  walkFwd: { file: 't3_walk_fwd.json', loop: true },
  walkBack:{ file: 't3_walk_back.json', loop: true },
  dash:    { file: 't3_dash_fwd.json', loop: false },
  crouch:  { file: 't3_crouch.json',  loop: false },  // stand -> crouch (slot 0x3b)
  crouchHold:{ file: 't3_crouch_hold.json', loop: true }, // crouching neutral (slot 40)
  backdash:{ file: 't3_backdash.json', loop: false },
  // noRise: the game's jump/launch physics lifts the fighter, so the clip
  // keeps its crouch/landing compression but not its rise (else the
  // height doubles: hips measured at 2.46 m mid-jump before this).
  jumpUp:  { file: 't3_jump_up.json', loop: false, noRise: true },
  jumpFwd: { file: 't3_jump_fwd.json', loop: false, noRise: true },
  jumpBack:{ file: 't3_jump_back.json', loop: false, noRise: true },
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
import { checkClip, CTX } from './anim-gate.js';
export const T3_BANKS = {
  king:       'assets/anim/t3/king_on_pantera_leoman/',
  jin:        'assets/anim/t3/jin/',
  xiaoyu:     'assets/anim/t3/xiaoyu/',
  bryan:      'assets/anim/t3/bryan/',
  gunjack:    'assets/anim/t3/gunjack/',
  yoshimitsu: 'assets/anim/t3/yoshimitsu/',
  // Remainder banks (2026-10-20, T3 bank recovery): REAL divmot
  // banks decoded from TEKKEN3.BNS through the same bake pipeline
  // (forward-merged with main's PR #389 combat-animation rewrite).
  // armorking = divmot03_king baked on King's OWN rig (Armor King has
  // no T3 divmot of his own; reached via the fighter.js override).
  // heihachi_ownrig = divmot13 decoded onto Heihachi's OWN rig via the
  // pose-chain pivot override for his geometry-less KMD parts 2/9/13
  // (docs/anim/T3-REMAINDER-BANKS-20261020.md). The 'heihachi' bank key
  // keeps main's merged heihachi_on_jin/ (same motion, Jin's skeleton);
  // the own-rig decode ships as an alternative — one line to switch.
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
  heihachi_ownrig: 'assets/anim/t3/heihachi/',
  armorking:    'assets/anim/t3/armorking/',
  // Law (2026-10-23, Buffalo Bill pull): divmot01_law.bin baked onto Law's
  // own T3 18-part rig (lab/tools/t3_motion_bake.py --bank law). Buffalo
  // Bill's moveset source is 'law', so bankIdFor resolves him here.
  law:          'assets/anim/t3/law/',
  // Heihachi's OWN divmot13 motion stream, posed on Jin's T3 skeleton:
  // heihachi191's KMD has no hip/shoulder vertex data, so his body can't
  // be fitted (docs/anim/PROCEDURAL_AUDIT.md). tools/anim/t3_row_bake.py
  // --bank heihachi --kmd-from jin. Real Heihachi motion, Jin proportions.
  heihachi:   'assets/anim/t3/heihachi_on_jin/',
  // Last decoded banks (2026-10-23, tools/anim/t3_bake_bank.py): own divmot motion on each character's
  // own body. ogre = divmot14 (Ogre / True Ogre), kuma = divmot11 (Kuma; Panda shares it in T3),
  // gon = divmot19, law = divmot01 (Marshall Law).
  ogre:       'assets/anim/t3/ogre/',
  kuma:       'assets/anim/t3/kuma/',
  gon:        'assets/anim/t3/gon/',
  law:        'assets/anim/t3/law/',
  // Forest Law's own divmot20 motion posed on Law's body (his KMDs do not fit; heihachi_on_jin pattern).
  forestlaw:  'assets/anim/t3/forestlaw_on_law/',
// VF5 motion banks (2026-10-22, VF5 motion pipeline): Dural's motion
  // decoded from VF5 PS3 mot_DUR.bin. Per INTEGRATION LAW, VF5 motion
  // wires into the existing Tekken bank system (same wh-anim/1 format,
  // same loadT3Clips path, same retargetT3Clips) — no parallel subsystem.
  // dural -> Zen's stance (owner 2026-10-22: "Dural's stance is Zen's stance").
  dural:      'assets/anim/vf5/dural/',

};
/* PRIVATE VF5 Dural bank (Zen, 2026-10-28). Decoded from VF5 (PS3 BLES00029)
   mot_DUR.bin in the private mhvnsnt/game-reverse-engineering repo
   (vf5/dural/bake_dural.py); a private build copies the bank to
   game/assets/private/anim/vf5/dural/ and sets __WH_PRIVATE_ASSETS. Its
   throw tables ship beside it (reactions.bank.json) and are merged into
   WH_T3_REACTIONS.banks.dural when the bank loads. Public builds: absent. */
if (globalThis.__WH_PRIVATE_ASSETS) T3_BANKS.dural = 'assets/private/anim/vf5/dural/';


// Moveset source name -> bank key. 'demonio' is the game's rename of Jin
// (owner canon 2026-10-19: Tekken's Jin = DEMONIO). bosconovitch maps to
// his OWN real bank since 2026-10-20 (the old bosconovitch -> gunjack
// stand-in is retired: docfrank's frame data was built from Bosconovitch's
// real moveset). heihachi -> heihachi (main's heihachi_on_jin bank; an
// own-rig divmot13 decode also ships as T3_BANKS.heihachi_ownrig).
// Fixup for fictitious sources: deviljin -> jin.
export const SOURCE_TO_BANK = {
  king: 'king', demonio: 'jin', jin: 'jin', bryan: 'bryan',
  xiaoyu: 'xiaoyu', yoshimitsu: 'yoshimitsu', gunjack: 'gunjack',
  deviljin: 'jin',
  paul: 'paul', lei: 'lei', nina: 'nina', hwoarang: 'hwoarang',
  eddy: 'eddy', julia: 'julia', anna: 'anna',
  bosconovitch: 'bosconovitch', heihachi: 'heihachi',
  armorking: 'armorking', 'armor-king': 'armorking',
  ogre: 'ogre', kuma: 'kuma', panda: 'kuma', gon: 'gon', law: 'law', forestlaw: 'forestlaw',
  // VF5 Dural (Zen's 3D base, owner 2026-10-24/28): zen.json moves name t3_source 'dural'. The bank
  // itself only exists in private builds (T3_BANKS.dural, __WH_PRIVATE_ASSETS); bankIdFor keeps
  // public Zen UNMAPPED, so this entry only resolves Zen's own rows when the private bank is bound.
  dural: 'dural',
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
    // Track name matches bone node name in the scene (Hips, Spine, etc.).
    // Canonicalization: the T3 bake's skeleton named the chest bone
    // 'Chest'; every current game skeleton (Mixamo family, Lane-C rigs,
    // the WH auto-rig template) names it 'Spine2'. Without this mapping
    // the chest track binds to nothing on ANY shipped model and every
    // clip loses its chest motion. Name mapping only — no motion data
    // is altered, and the mapping is the game's own naming convention.
    const trackBone = bone === 'Chest' ? 'Spine2' : bone;
    tracks.push(new THREE.QuaternionKeyframeTrack(`${trackBone}.quaternion`, times, values));
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
const _t3facing = {};       // bankId -> { turned, kneeDeg, samples } (bankFacing)
const _t3hitRows = {};      // bankId -> decoded hit windows { row: [first, last, stream, word] }

/* ============================================================
   SOURCE FACING (2026-10-21) — every bank is declared "faces +Z,
   character left = +X" (skeleton.json note), and retargetT3Clips
   relies on it. Five banks were baked facing -Z instead:
   lab/tools/t3_to_gltf.py picks "forward" from the head-mesh
   centroid, and on characters whose head/hair mass sits behind the
   face it turned the rig 180°, then named Left/Right by the +X side
   (so their "Left*" joints are the anatomical right). Retargeted as
   +Z, the swing-matched torso, arms and legs land behind the fighter
   while the delta-driven hips and head keep facing the opponent —
   Doc Frank's "owl" (body turned the wrong way, head right).
   Detection uses the bank's own decoded frames, nothing authored:
   knees bend forward, so the circular mean of each knee's horizontal
   offset from its hip-ankle midline, measured against the hips'
   forward ((G_Hips·X) × Y), must lie in front of the hips. A bank
   whose knees lie behind (mean forward component < 0) is turned
   180° about Y (joint rests and root_t: (x,y,z) -> (-x,y,-z); every
   local rotation conjugated: (x,y,z,w) -> (-x,y,-z,w)) and its
   Left/Right joint names swapped. Measured 2026-10-21 on all 17
   bank folders: bosconovitch -179.5°, eddy -178.6°, gunjack 149.9°,
   heihachi (own rig) 137.7°, yoshimitsu 155.1° -> turned; the other
   twelve lie within ±61° (anna 60.5°, lei -45.9°) -> untouched.
   Offline twin of this check: tools/anim/t3_bank_facing.py.
   ============================================================ */
const FACING_CLIPS = ['stance', 'walkFwd', 'crouchHold', 'block'];
function _qmul(a, b) {
  return [a[3] * b[0] + a[0] * b[3] + a[1] * b[2] - a[2] * b[1],
    a[3] * b[1] - a[0] * b[2] + a[1] * b[3] + a[2] * b[0],
    a[3] * b[2] + a[0] * b[1] - a[1] * b[0] + a[2] * b[3],
    a[3] * b[3] - a[0] * b[0] - a[1] * b[1] - a[2] * b[2]];
}
function _qrot(q, v) {
  const [x, y, z, w] = q;
  const tx = 2 * (y * v[2] - z * v[1]), ty = 2 * (z * v[0] - x * v[2]), tz = 2 * (x * v[1] - y * v[0]);
  return [v[0] + w * tx + (y * tz - z * ty), v[1] + w * ty + (z * tx - x * tz), v[2] + w * tz + (x * ty - y * tx)];
}
function bankFacing(skel, datas) {
  const P = {}, par = {}, order = skel.joints.map(j => j.name);
  for (const j of skel.joints) { P[j.name] = j.rest; par[j.name] = j.parent; }
  let fwdSum = 0, leftSum = 0, samples = 0;
  for (const data of datas) {
    if (!data || !data.rot_xyzw) continue;
    let n = 0;
    for (const v of Object.values(data.rot_xyzw)) if (v && v.length > n) n = v.length;
    for (let f = 0; f < n; f++) {
      const G = {}, X = {};
      for (const j of order) {
        const r = data.rot_xyzw[j];
        const q = r && r.length ? r[Math.min(f, r.length - 1)] : [0, 0, 0, 1];
        const p = par[j];
        if (p && G[p]) {
          G[j] = _qmul(G[p], q);
          const o = _qrot(G[p], [P[j][0] - P[p][0], P[j][1] - P[p][1], P[j][2] - P[p][2]]);
          X[j] = [X[p][0] + o[0], X[p][1] + o[1], X[p][2] + o[2]];
        } else { G[j] = q; X[j] = P[j].slice(); }
      }
      if (!G.Hips) continue;
      const hx = _qrot(G.Hips, [1, 0, 0]);
      let fx = -hx[2], fz = hx[0];             // (G_Hips·X) × Y, horizontal
      const fl = Math.hypot(fx, fz);
      if (fl < 1e-6) continue;
      fx /= fl; fz /= fl;
      for (const s of ['Left', 'Right']) {
        const a = X[s + 'UpLeg'], k = X[s + 'Leg'], e = X[s + 'Foot'];
        if (!a || !k || !e) continue;
        const ox = k[0] - (a[0] + e[0]) / 2, oz = k[2] - (a[2] + e[2]) / 2;
        fwdSum += ox * fx + oz * fz;
        leftSum += ox * fz - oz * fx;          // component along forward rotated +90° about Y
        samples++;
      }
    }
  }
  return { turned: samples > 0 && fwdSum < 0, kneeDeg: Math.atan2(leftSum, fwdSum) * 180 / Math.PI, samples };
}
const _swapLR = (n) => (typeof n === 'string' ? n.replace(/^(Left|Right)/, (m) => (m === 'Left' ? 'Right' : 'Left')) : n);
function turnSkeleton(skel) {
  for (const j of skel.joints) {
    j.name = _swapLR(j.name); j.parent = _swapLR(j.parent);
    j.rest = [-j.rest[0], j.rest[1], -j.rest[2]];
  }
  if (skel.foot_tip) {
    const ft = {};
    for (const [k, v] of Object.entries(skel.foot_tip)) ft[_swapLR(k)] = [-v[0], v[1], -v[2]];
    skel.foot_tip = ft;
  }
  skel._info = undefined;
  skel.turned_180 = true;
}
function turnData(data) {
  if (!data || !data.rot_xyzw) return;
  const rot = {};
  for (const [b, arr] of Object.entries(data.rot_xyzw)) rot[_swapLR(b)] = arr.map(q => [-q[0], q[1], -q[2], q[3]]);
  data.rot_xyzw = rot;
  if (data.bones) data.bones = data.bones.map(_swapLR);
  if (data.root_t) data.root_t = data.root_t.map(t => [-t[0], t[1], -t[2]]);
}
export function getT3BankFacing(bankId) { return _t3facing[bankId] || null; }

/* PER-CLIP HEADING (moveset sweep 2026-10-29). The bank turn above is decided
   on the stance/walk/crouch/block clips only. Some banks' attack rows are
   baked facing the other way from those (yoshimitsu: 69 of its row clips start
   ~180° from its stance; bryan/jin: 0). Played as-is the body spins round
   and its root_t carries it AWAY from the foe — jin_soul f+2 (yoshimitsu
   row 125): heading 172° off the stance in game, gap 1.45 -> 2.36 m, whiff.
   Measured, not assumed: a clip's frame-0 front is where its knees point
   (same test as bankFacing). A row more than 135° from the stance heading
   is turned 180° about Y (root-child rotations q -> qY(pi)·q, root_t
   rotated about frame 0). Rows within 135° are untouched, and so are rows
   any moveset using them plays under a T3 facing condition 0x24-0x2E
   (own back turned, turned away; t3-conditions.js): those start turned
   on purpose (yoshimitsu r65-r75, r97-r102, r207, r209, r329-r334). */
async function facingCondRows(base, bankId, rowData) {
  const ids = new Set();
  for (const r of Object.values(rowData)) for (const u of (r.rec && r.rec.used_by) || []) ids.add(u);
  const keep = new Set();
  await Promise.all([...ids].map(async (id) => {
    try {
      const res = await fetch(new URL(`../../../movesets/${id}.json`, new URL(base, location.href)));
      if (!res.ok) return;
      const m = await res.json();
      for (const mv of Object.values(m.moves || {})) {
        if (mv && mv.t3_source === bankId && mv.t3_row != null && mv.t3_condition >= 0x24 && mv.t3_condition <= 0x2E) keep.add(+mv.t3_row);
      }
    } catch (e) {}
  }));
  return keep;
}
function clipHeading(skel, data, f = 0) {
  if (!data || !data.rot_xyzw) return null;
  const P = {}, par = {}, order = skel.joints.map(j => j.name);
  for (const j of skel.joints) { P[j.name] = j.rest; par[j.name] = j.parent; }
  const G = {}, X = {};
  for (const j of order) {
    const r = data.rot_xyzw[j];
    const q = r && r.length ? r[Math.min(f, r.length - 1)] : [0, 0, 0, 1];
    const p = par[j];
    if (p && G[p]) {
      G[j] = _qmul(G[p], q);
      const o = _qrot(G[p], [P[j][0] - P[p][0], P[j][1] - P[p][1], P[j][2] - P[p][2]]);
      X[j] = [X[p][0] + o[0], X[p][1] + o[1], X[p][2] + o[2]];
    } else { G[j] = q; X[j] = P[j].slice(); }
  }
  if (!G.Hips) return null;
  const hx = _qrot(G.Hips, [1, 0, 0]);
  let fx = -hx[2], fz = hx[0];
  const fl = Math.hypot(fx, fz);
  if (fl < 1e-6) return null;
  fx /= fl; fz /= fl;
  let s = 0;
  for (const side of ['Left', 'Right']) {
    const a = X[side + 'UpLeg'], k = X[side + 'Leg'], e = X[side + 'Foot'];
    if (a && k && e) s += (k[0] - (a[0] + e[0]) / 2) * fx + (k[2] - (a[2] + e[2]) / 2) * fz;
  }
  if (Math.abs(s) < 0.01) return null; // knees too straight to tell
  const sg = s >= 0 ? 1 : -1;
  return Math.atan2(fx * sg, fz * sg);
}
function yawData180(skel, data) {
  const roots = new Set(skel.joints.filter(j => !j.parent).map(j => j.name));
  const kids = skel.joints.filter(j => j.parent && roots.has(j.parent)).map(j => j.name);
  const qy = [0, 1, 0, 0];
  for (const b of kids) { const arr = data.rot_xyzw[b]; if (arr) data.rot_xyzw[b] = arr.map(q => _qmul(qy, q)); }
  if (data.root_t && data.root_t.length) { const r0 = data.root_t[0]; data.root_t = data.root_t.map(t => [2 * r0[0] - t[0], t[1], 2 * r0[2] - t[2]]); }
}
export function alignRowHeadings(skel, actionData, rowData, keepRows = new Set()) {
  const hs = FACING_CLIPS.map(a => clipHeading(skel, actionData[a])).filter(h => h != null);
  if (!hs.length) return [];
  const ref = Math.atan2(hs.reduce((a, h) => a + Math.sin(h), 0), hs.reduce((a, h) => a + Math.cos(h), 0));
  const fixed = [];
  for (const [row, r] of Object.entries(rowData)) {
    if (keepRows.has(+row)) continue; // played under a facing condition (back turned): baked turn is right
    const h = clipHeading(skel, r.data);
    if (h == null) continue;
    const d = Math.atan2(Math.sin(h - ref), Math.cos(h - ref));
    if (Math.abs(d) > 135 * Math.PI / 180) { yawData180(skel, r.data); fixed.push(+row); }
  }
  return fixed;
}

/* STANDING IDLE (2026-10-21). The 'stance' action loops move-index slot 3.
   On the bosconovitch bank slot 3 (row 237) is a 15-frame fall onto his
   back (root 0.45 -> -0.45 m; slot 1 is him lying still, slot 0 getting
   back up): looped as the idle, Doc Frank fell through the stage twice a
   second. A slot-3 clip that drops more than a quarter of the hip height
   is not an idle (every other bank's drops under 0.15 x hip height).
   Such a bank idles in its own standing guard instead — in Tekken the
   neutral stance IS the standing guard (holding back blocks from it) —
   the bank's guard-hold clip (T3_CLIP_DEFS.block), played ping-pong so its
   one-way settle (crouched guard -> upright guard, seam 24 deg on
   bosconovitch) breathes without a pop. Rendered 2026-10-21: the
   bosconovitch guard is the same hunched, hands-up posture as his walk.
   (The most loopable standing stretch of his round-start clip was tried
   first and rejected on sight: it is his arms-wide stretch.)
   Returns the replacement wh-anim/1 data or null (bank unchanged). */
function standingIdle(actionData, skel) {
  const st = actionData.stance, guard = actionData.block;
  const rest = skel && skel.root_rest_y;
  if (!st || !st.root_t || !guard || !(rest > 0)) return null;
  const ys = st.root_t.map(t => t[1]);
  const drop = Math.max(...ys) - Math.min(...ys);
  if (drop <= 0.25 * rest) return null;
  return { ...guard, pingpong: true,
    neutral_note: `Idle = the bank's standing guard (${T3_CLIP_DEFS.block.file}, ping-pong): ` +
      `its slot-3 clip drops ${drop.toFixed(2)} m, a fall, not a stance (t3anims.js standingIdle)` };
}

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
    // Decoded frames first (all of them), then the facing check, then clips.
    const actionData = {};
    let rowData = {};
    const jobs = Object.entries(T3_CLIP_DEFS).map(async ([action, def]) => {
      try {
        const res = await fetch(base + def.file);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        if (data.format !== 'wh-anim/1') {
          console.warn(`[WH-T3] ${bankId}/${def.file}: unexpected format ${data.format}`);
        }
        actionData[action] = data;
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
        for (const [row, rec] of Object.entries(pack.rows || {})) rowData[row] = { rec, data: decodePackRow(pack, rec) };
      } catch (e) {
        console.warn(`[WH-T3] ${bankId}/rows.pack.json unavailable:`, e.message || e);
        rowData = {};
      }
    })());
    // T3 reaction tables (hit-reaction wiring lane, 2026-10-24): the
    // selection in fighter.js reads globalThis.WH_T3_REACTIONS. The
    // throw lane loads them on demand; this fetch runs with the
    // bank load so strikes have the tables at fight start even in
    // a fight with no throw attempt. The global cache guard means
    // whichever loader runs second is a no-op.
    jobs.push(ensureT3Reactions().then(R => mergeBankThrowTables(R, base)).catch(() => null));
    // Real Tekken 7 stances baked for fighters on this bank (T7_STANCES): loaded with the bank so the
    // fight and the select preview can swap them in synchronously (applyT7Stance).
    for (const [fid, def] of Object.entries(T7_STANCES)) {
      if (def.bank === bankId && !_t7stance[fid]) jobs.push(loadT7Stance(fid, def, THREE));
    }
    // Decoded active window of every attack row (tools/anim/t3_hit_frames.py, lane D 2026-10-24):
    // { row: [active_first, active_last, stream_frames, attack_word, throw] } — fighter.js times the
    // clip on it and never plays a throw row for a strike (or a strike row for a throw).
    let hitRows = {};
    jobs.push((async () => {
      try {
        const res = await fetch(base + 'hit_frames.json');
        if (res.ok) hitRows = (await res.json()).rows || {};
      } catch (e) { hitRows = {}; }
    })());
    await Promise.all(jobs);
    const skel = _t3skelCache[bankId];
    if (skel) {
      const facing = bankFacing(skel, FACING_CLIPS.map(a => actionData[a]));
      _t3facing[bankId] = facing;
      if (facing.turned) {
        turnSkeleton(skel);
        for (const d of Object.values(actionData)) turnData(d);
        for (const r of Object.values(rowData)) turnData(r.data);
        console.log(`[WH-T3] bank '${bankId}': baked facing -Z (knees ${facing.kneeDeg.toFixed(1)}° from hips forward) — turned 180° to +Z, Left/Right relabelled`);
      }
      const flipped = alignRowHeadings(skel, actionData, rowData, await facingCondRows(base, bankId, rowData));
      if (flipped.length) console.log(`[WH-T3] bank '${bankId}': ${flipped.length} row clips baked >135° from the stance heading — turned 180° to match`);
      const idle = standingIdle(actionData, skel);
      if (idle) {
        actionData.stance = idle;
        console.log(`[WH-T3] bank '${bankId}': ${idle.neutral_note}`);
      }
    }
    for (const [action, data] of Object.entries(actionData)) {
      const def = T3_CLIP_DEFS[action];
      const clip = jsonToClip(`t3_${bankId}_${action}`, data, THREE);
      if (clip) {
        clip.userData.loop = def.loop;
        clip.userData.noRise = !!def.noRise;
        if (data.pingpong) clip.userData.pingpong = true;
        // SHOW-ANIMATION LOCK: bank clip JSONs carry "anim_set": "SHOW" for
        // intro/win clips. Tag the THREE clip so anim-gate.js (CTX.FIGHT)
        // rejects it in combat — these play in intros/cutscenes only.
        if (data.anim_set === 'SHOW') clip.userData.animSet = 'show';
        clips[action] = clip;
      }
    }
    let n = 0;
    for (const [row, { rec, data }] of Object.entries(rowData)) {
      const clip = jsonToClip(`t3_${bankId}_row${row}`, data, THREE);
      if (clip) { clip.userData.loop = false; clip.userData.move_row = rec.move_row; clips['row:' + row] = clip; n++; }
    }
    // Attach the decoded hit window to every clip that plays an attack row (move rows and the
    // light/medium/heavy/grab action clips, which carry their source move_row too).
    for (const clip of Object.values(clips)) {
      const h = clip.userData.move_row != null ? hitRows[String(clip.userData.move_row)] : null;
      if (h) clip.userData.hit = h;
    }
    _t3hitRows[bankId] = hitRows;
    console.log(`[WH-T3] bank '${bankId}': ${n} move-row clips`);
    console.log(`[WH-T3] bank '${bankId}': loaded ${Object.keys(clips).length} real T3 clips`);
    _t3clipCache[bankId] = clips;
    return clips;
  })();
  return _t3clipPromises[bankId];
}

/** Synchronous accessor for one bank's cached clips (null if not loaded). */
export function getT3Clips(bankId = 'king') { return _t3clipCache[bankId] || null; }

/* REAL TEKKEN 7 STANCES (2026-10-30; owner: Pantera's moves "come straight from King ... get that 100% done ...
   the animations all for him"). King's actual T7 standing stance: kinrotsm.arc clip 132 'nakg_kg2kam', the 0xC8
   clip his Kg_sKAM00_ / Kg_KAM / Kg_sKAM_WAIT moves play, converted by tools/anim/t7_c8_stance_bake.py through
   the community 0xC8 path (Kiloutre's applyRotationFromAnimdata on Koenji's TekkenMannequin). It ships as a
   wh-anim/1 clip on its own wh-anim-skel/1 skeleton (the T7 rest pose), so retargetT3Clips puts it on any rig
   exactly like a bank clip. It replaces the bank's T3 slot-3 'stance' for the fighters listed here only; every
   other action and every move row stays the bank's own. Nothing authored. */
export const T7_STANCES = {
  pantera: { bank: 'king', dir: 'assets/anim/t7/king/' },
};
const _t7stance = {}; // fighterId -> { bank, skelId, clip }
async function loadT7Stance(fid, def, THREE) {
  try {
    const [skel, data] = await Promise.all(['skeleton.json', 'stance.json'].map(async (f) => {
      const res = await fetch(def.dir + f);
      if (!res.ok) throw new Error(`${f}: HTTP ${res.status}`);
      return res.json();
    }));
    const skelId = 't7:' + def.dir;
    _t3skelCache[skelId] = skel;
    const clip = jsonToClip(`t7_${fid}_stance`, data, THREE);
    if (!clip) return;
    clip.userData.loop = true;
    clip.userData.noRise = false;
    clip.userData.t7 = data.t7_source || true;
    _t7stance[fid] = { bank: def.bank, skelId, clip };
  } catch (e) {
    console.warn(`[WH-T7] ${fid}: real T7 stance unavailable, keeps the bank stance:`, e.message || e);
  }
}
/** Swap a fighter's baked real-T7 stance (T7_STANCES) into its retargeted bank clips. `clips` is the map
    retargetT3Clips returned for `model`; call it before createT3Actions, in the same rest-pose window. */
export function applyT7Stance(fighterId, bankId, clips, model, THREE, instanceKey = null) {
  const t7 = _t7stance[fighterId];
  if (!t7 || t7.bank !== bankId || !clips) return clips;
  const rc = retargetT3Clips({ stance: t7.clip }, t7.skelId, model, THREE, instanceKey, ['stance']);
  if (rc && rc.stance) clips.stance = rc.stance;
  return clips;
}

/* ============================================================
   REACTION PACKS (grapple lane, 2026-10-24) — the throw /
   victim / escape clips of docs/anim/T3-REACTIONS.md. These
   live in game/assets/anim/t3/<bank>/reactions.pack.json
   (~6.5 MB per bank) and are NOT part of loadT3Clips, which
   is why fighter.js could only play generic 'hit'/'grab'/
   'launch' for throws until now. loadReactionPack decodes a
   bank's pack into canonical clips keyed by slot ('0xaeb'),
   exactly the way loadT3Clips decodes rows.pack.json into
   'row:<n>' clips; fighter.js retargets the two slots of a
   throw pair on demand, the same way it retargets a row clip
   on first use. Turned banks (bankFacing, above) get the same
   180 deg turn applied to the pack rows, or the pair would
   play backwards like the old Doc Frank "owl". Failures log
   and return null — the caller keeps the legacy lock path.
   ============================================================ */
const _reactionPackCache = {};    // bankId -> { pack, clips }
const _reactionPackPromises = {};
export function reactionPackRowToClip(pack, rec, THREE) {
  const data = decodePackRow(pack, rec);
  const clip = jsonToClip(`t3_react_${rec.slot}`, data, THREE);
  if (clip) {
    clip.userData.slot = rec.slot;
    clip.userData.roles = rec.roles || [];
    clip.userData.stream_frames = rec.stream_frames;
    clip.userData.yaw0 = rec.yaw0;
    clip.userData.anchorScale = pack.anchor_mm_to_rig_m;
  }
  return clip;
}
export async function loadReactionPack(THREE, bankId) {
  if (!bankId || !T3_BANKS[bankId]) return null;
  if (_reactionPackCache[bankId]) return _reactionPackCache[bankId];
  if (_reactionPackPromises[bankId]) return _reactionPackPromises[bankId];
  const base = T3_BANKS[bankId];
  _reactionPackPromises[bankId] = (async () => {
    try {
      const res = await fetch(base + 'reactions.pack.json');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const pack = await res.json();
      // Phone-load note: the pack JSON (~6.5 MB) is cached, but
      // clips are decoded ONE SLOT AT A TIME on demand
      // (getReactionClip, below) — decoding all ~568 clips up
      // front would triple fight-load clip memory on top of the
      // row clips loadT3Clips already builds.
      const out = { pack, clips: {}, turned: !!(_t3facing[bankId] && _t3facing[bankId].turned) };
      _reactionPackCache[bankId] = out;
      console.log(`[WH-T3] bank '${bankId}': reaction pack loaded (${Object.keys(pack.rows || {}).length} slots)`);
      return out;
    } catch (e) {
      console.warn(`[WH-T3] ${bankId}/reactions.pack.json unavailable:`, e.message || e);
      return null;
    }
  })();
  return _reactionPackPromises[bankId];
}
/** Decode (once, cached) the canonical clip for one pack slot. */
export function getReactionClip(bankId, slot, THREE) {
  const rp = _reactionPackCache[bankId];
  if (!rp) return null;
  const key = '0x' + Number(slot).toString(16);
  if (rp.clips[key]) return rp.clips[key];
  const rec = rp.pack.rows && rp.pack.rows[key];
  if (!rec) return null;
  const data = decodePackRow(rp.pack, rec);
  if (rp.turned) turnData(data);
  const clip = jsonToClip(`t3_react_${rec.slot}`, data, THREE);
  if (clip) {
    clip.userData.slot = rec.slot;
    clip.userData.roles = rec.roles || [];
    clip.userData.stream_frames = rec.stream_frames;
    clip.userData.yaw0 = rec.yaw0;
    clip.userData.anchorScale = rp.pack.anchor_mm_to_rig_m;
    rp.clips[key] = clip;
  }
  return clip || null;
}
/** Synchronous accessor for a loaded reaction pack (null if not loaded). */
export function getReactionPack(bankId) { return _reactionPackCache[bankId] || null; }

/* Strike-reaction playback adapter (hit-reaction lane, 2026-10-24).
   The throw lane above owns the pack fetch and cache, so this
   lane adds no second fetch: the scale reads the cached pack,
   and the strike clip decodes fresh from the cached pack rows
   (facing is re-checked at decode time, and the clip carries
   its own loop/noRise flags, so the throw lane's cached clip
   is never mutated). A slot no pack defines returns null and
   the caller keeps its generic fallback (UNMAPPED, never guessed). */

/** Anchor scale (mm -> rig metres) of an already-loaded pack, else null. */
export function getT3ReactionPackScale(bankId) {
  const rp = getReactionPack(bankId);
  return rp && rp.pack && typeof rp.pack.anchor_mm_to_rig_m === 'number' ? rp.pack.anchor_mm_to_rig_m : null;
}

/** Decode one reaction slot into a bank-space THREE clip, or null.
    noRise: set for air reactions (code 0x24) — the game's launch
    physics owns the arc, so the clip must not lift the hips too. */
export async function loadT3ReactionClip(THREE, bankId, slot, { noRise = false } = {}) {
  if (!bankId || !T3_BANKS[bankId] || slot == null) return null;
  await loadT3Clips(THREE, bankId); // skeleton + facing, cached after fight load
  const rp = await loadReactionPack(THREE, bankId);
  if (!rp || !rp.pack || !rp.pack.rows) return null;
  const key = '0x' + (slot & 0xffff).toString(16);
  const rec = rp.pack.rows[key];
  if (!rec) return null; // UNMAPPED: slot planned but not baked in this pack
  const data = decodePackRow(rp.pack, rec);
  if (_t3facing[bankId] && _t3facing[bankId].turned) turnData(data);
  const clip = jsonToClip('react:' + slot, data, THREE);
  if (!clip) return null;
  clip.userData.loop = false;
  if (noRise) clip.userData.noRise = true;
  return clip;
}

/** Fetch (once) and cache the parsed reactions.json tables.
    The throw lane's loader sets the same global; whichever runs
    first wins, and this one returns the cached tables after that,
    so strikes have the tables at fight start even in a fight
    with no throw attempt. */
let _t3reactionsPromise = null;
/* A private bank (assets/private/...) carries its own throw tables in
   reactions.bank.json (the public reactions.json never names it); merge
   them into WH_T3_REACTIONS.banks[<dir>] once. No-op for public banks. */
async function mergeBankThrowTables(R, base) {
  if (!R || !R.banks || !base || !base.includes('/private/')) return R;
  const dir = base.split('/').filter(Boolean).pop();
  if (R.banks[dir]) return R;
  try {
    const res = await fetch(base + 'reactions.bank.json');
    if (res.ok) R.banks[dir] = await res.json();
  } catch (e) { console.warn(`[WH-T3] ${dir}/reactions.bank.json unavailable:`, e.message || e); }
  return R;
}

export function ensureT3Reactions() {
  if (globalThis.WH_T3_REACTIONS) return Promise.resolve(globalThis.WH_T3_REACTIONS);
  if (_t3reactionsPromise) return _t3reactionsPromise;
  _t3reactionsPromise = (async () => {
    try {
      const anyBase = Object.values(T3_BANKS)[0] || 'assets/anim/t3/king_on_pantera_leoman/';
      const base = anyBase.replace(/[^/]+\/$/, '');
      const res = await fetch(base + 'reactions.json');
      if (!res.ok) throw new Error('HTTP ' + res.status);
      const data = await res.json();
      globalThis.WH_T3_REACTIONS = data;
      return data;
    } catch (e) {
      console.warn('[WH-T3] reactions.json unavailable — hit reactions stay generic:', e.message || e);
      _t3reactionsPromise = null;
      return null;
    }
  })();
  return _t3reactionsPromise;
}

/* ============================================================
   STRIKE PROFILE (lane D, 2026-10-24) — what a clip's own decoded
   frames do with each limb. Forward kinematics on the bank's source
   skeleton (rest = world joint positions, every rest rotation
   identity — the FK bankFacing uses): per frame, the distance of the
   limb's end joint (wrist / ankle — the joints fighter.js hits with)
   from the pelvis (Hips). ext = (farthest - frame 0) / limb length:
   how far the limb leaves the guard the move starts from. Read-only
   on the decoded rotations; nothing is authored. Cached on the clip.
   Call it on the bank clip (getT3Clips), not a retargeted copy: the
   retargeted copies drop the raw frames.
   ============================================================ */
const STRIKE_LIMBS = {
  armL: ['LeftArm', 'LeftForeArm', 'LeftHand'], armR: ['RightArm', 'RightForeArm', 'RightHand'],
  legL: ['LeftUpLeg', 'LeftLeg', 'LeftFoot'], legR: ['RightUpLeg', 'RightLeg', 'RightFoot'],
};
const _dist = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);
export function clipStrikeProfile(bankId, clip) {
  if (!clip || !clip.userData) return null;
  if (clip.userData.strike !== undefined) return clip.userData.strike;
  const skel = _t3skelCache[bankId], raw = clip.userData.raw;
  if (!skel || !raw || !raw.rot) return (clip.userData.strike = null);
  const P = {}, par = {}, order = skel.joints.map(j => j.name);
  for (const j of skel.joints) { P[j.name] = j.rest; par[j.name] = j.parent; }
  let n = 0;
  for (const v of Object.values(raw.rot)) if (v && v.length > n) n = v.length;
  const limbs = {};
  for (const [k, ch] of Object.entries(STRIKE_LIMBS)) {
    if (!P.Hips || ch.some(j => !P[j])) continue;
    limbs[k] = { d: new Array(n), len: _dist(P[ch[0]], P[ch[1]]) + _dist(P[ch[1]], P[ch[2]]) };
  }
  for (let f = 0; f < n; f++) {
    const G = {}, X = {};
    for (const j of order) {
      const r = raw.rot[j];
      const q = r && r.length ? r[Math.min(f, r.length - 1)] : [0, 0, 0, 1];
      const p = par[j];
      if (p && G[p]) {
        G[j] = _qmul(G[p], q);
        const o = _qrot(G[p], [P[j][0] - P[p][0], P[j][1] - P[p][1], P[j][2] - P[p][2]]);
        X[j] = [X[p][0] + o[0], X[p][1] + o[1], X[p][2] + o[2]];
      } else { G[j] = q; X[j] = P[j].slice(); }
    }
    for (const [k, L] of Object.entries(limbs)) L.d[f] = _dist(X[STRIKE_LIMBS[k][2]], X.Hips);
  }
  const out = { fps: raw.fps, n, limbs: {}, dominant: null };
  let best = -Infinity;
  for (const [k, L] of Object.entries(limbs)) {
    let pf = 0;
    for (let f = 1; f < n; f++) if (L.d[f] > L.d[pf]) pf = f;
    const ext = L.len > 1e-6 ? (L.d[pf] - L.d[0]) / L.len : 0;
    out.limbs[k] = { peakF: pf, peakT: pf / raw.fps, ext, reach: L.len > 1e-6 ? L.d[pf] / L.len : 0 };
    if (ext > best) { best = ext; out.dominant = k; }
  }
  return (clip.userData.strike = out);
}

/* When a clip's hit lands, in clip seconds: { t0, t1, src }.
   'decoded' — the clip plays a T3 attack row with a decoded active
   window (hit_frames.json, 60 fps stream, moveFrame 1 = stream frame 0,
   n0madic/Tekken3Remake docs/research/code/moves.md); 'measured' — the
   frame where `limb` (else the clip's most-extending limb) is farthest
   from the pelvis (clipStrikeProfile). null when neither exists. */
export function clipHitWindow(bankId, clip, limb) {
  if (!clip || !clip.userData) return null;
  const h = clip.userData.hit;
  if (h && h[0] > 0) {
    // Stream frame active_first at 60 fps. Checked on every baked attack row of all 21 banks
    // (lane D 2026-10-24): the measured extension peak of the striking limb lies a median
    // 1-3 frames after (active_first - 1)/60, i.e. 0-2 frames from active_first/60.
    const t0 = Math.min(clip.duration, h[0] / 60);
    return { t0, t1: Math.min(clip.duration, Math.max(t0, h[1] / 60)), src: 'decoded' };
  }
  const sp = clipStrikeProfile(bankId, clip);
  const L = sp && (sp.limbs[limb] && sp.limbs[limb].ext > 0.05 ? sp.limbs[limb] : sp.limbs[sp.dominant]);
  if (!L) return null;
  return { t0: L.peakT, t1: L.peakT, src: 'measured' };
}

/** Decoded hit windows of a loaded bank: { row: [active_first, active_last, stream_frames, attack_word, throw] }. */
export function getT3HitRows(bankId) { return _t3hitRows[bankId] || null; }

/** Does this clip play a decoded THROW row (hit_frames.json throw flag: reaction 0x1xxx = throw attempt
    selecting a victim move, or attack word 0x800 = throw-system row)? false for strikes / unknown. */
export function clipIsThrow(clip) { const h = clip && clip.userData && clip.userData.hit; return !!(h && h[4]); }

/* Attack level of a decoded T3 attack word (n0madic/Tekken3Remake docs/research/code/combat.md,
   "Attack levels, postures and guards"; same bits as Fighter.canBeHitBy): posture bits 1/2/4,
   guard bits 0x08 crouching / 0x10 standing. 'h' high (hits standing only), 'm' mid (standing
   guard blocks), 's' special mid (either guard), 'l' low (crouching guard), 'u' unblockable,
   't' throw-class (0x800, no posture bits). */
export function attackLevelOfWord(w) {
  if (w == null || !Number.isFinite(+w)) return null;
  w = +w;
  const post = w & 7, guard = w & 0x18;
  if (!post) return (w & 0x800) ? 't' : null;
  if (post === 2) return 'h';
  if (guard === 0x08) return 'l';
  if (guard === 0x18) return 's';
  if (guard === 0) return 'u';
  return 'm';
}

/* Button mask (1 LP, 2 RP, 4 LK, 8 RK — T3 command bits) -> limb, for single-button masks. */
export const BUTTON_LIMB = { 1: 'armL', 2: 'armR', 4: 'legL', 8: 'legR' };

/* The baked move rows of a loaded bank that fighter.js may match a move with no row clip of its own
   against (closest real clip of the same character), as { name, row, btn, limb, limbSrc, level, t0 }
   sorted by row. btn = the buttons that start the row (hit_frames.json: decoded branch commands, else
   the movesets' t3_command); limb = BUTTON_LIMB[btn], or for rows with no known button the limb its
   own frames extend most (clipStrikeProfile, limbSrc 'measured', kept only when ext >= 0.1 limb
   lengths). Strikes (default): decoded attack rows (active window) that are NOT throw rows.
   { throws: true }: the decoded throw ATTEMPT rows (throw flag + active window). Cached per bank. */
const _poolCache = new Map(); // clips object -> { strike, throw }
export function bankAttackPool(bankId, { throws = false } = {}) {
  const clips = _t3clipCache[bankId];
  if (!clips) return [];
  if (!_poolCache.has(clips)) {
    const pools = { strike: [], throw: [] };
    for (const [name, clip] of Object.entries(clips)) {
      const h = clip.userData.hit;
      if (!name.startsWith('row:') || !h || !(h[0] > 0)) continue;
      const btn = h[5] || 0;
      let limb = BUTTON_LIMB[btn] || null, limbSrc = 'button';
      if (!limb && !btn) {
        const sp = clipStrikeProfile(bankId, clip);
        const L = sp && sp.dominant && sp.limbs[sp.dominant];
        if (L && (h[4] || L.ext >= 0.1)) { limb = sp.dominant; limbSrc = 'measured'; }
        else if (!h[4]) continue;
      }
      const w = clipHitWindow(bankId, clip, limb);
      (h[4] ? pools.throw : pools.strike).push({ name, row: +name.slice(4), btn, limb, limbSrc,
        level: h[4] ? 't' : attackLevelOfWord(h[3]), t0: w ? w.t0 : 0 });
    }
    pools.strike.sort((a, b) => a.row - b.row); pools.throw.sort((a, b) => a.row - b.row);
    _poolCache.set(clips, pools);
  }
  return _poolCache.get(clips)[throws ? 'throw' : 'strike'];
}

/* Clip time for game time g (s since the move started) under a piecewise-linear warp that puts the
   clip's hit window [t0, t1] on the move's active frames [S, S+A]: windup [0, t0] -> [0, S],
   recovery [t1, D] -> [S+A, S+A+R] (the rest of the move's total). timing = { S, A, R, t0, t1, D }. */
export function attackClipTime(timing, g) {
  const { S, A, R, t0, t1, D } = timing;
  const end = Math.max(0, D - 1e-4);
  if (g <= S) return Math.min(end, S > 1e-4 ? t0 * Math.max(0, g) / S : t0);
  if (g <= S + A) return Math.min(end, A > 1e-4 ? t0 + (t1 - t0) * (g - S) / A : t1);
  const r = R > 1e-4 ? Math.min(1, (g - S - A) / R) : 1;
  return Math.min(end, t1 + (D - t1) * r);
}

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
    // Only quaternion tracks take the bind-premultiply below. Any other
    // track (e.g. the Hips.position VectorKeyframeTrack that
    // retargetT3Clips emits from root_t, stride 3) must stay exactly
    // what it is: running it through the stride-4 quaternion loop reads
    // past its value groups, emits NaNs, and pushes a malformed
    // duplicate '<bone>.quaternion' track (values.length = times*3)
    // that hangs/crashes the mixer on first evaluation.
    if (!track.name.endsWith('.quaternion')) {
      if (target === bone) { tracks.push(track); continue; }
      changed = true;
      tracks.push(new track.constructor(`${target}.${track.name.slice(dot + 1)}`, track.times, track.values));
      continue;
    }
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
  // NOT re-retargeted here (2026-10-21). Every caller — Fighter._bindT3, Fighter._moveRowAction,
  // SelectScreen — passes clips that retargetT3Clips() already converted into THIS rig's own
  // bone names and rest frame (PR #389). PR #403 added retargetClipToRig() at this point; on
  // those clips it misses every 'mixamorig:'-named track (bind keys are stripped names), drops or
  // bind-premultiplies them a second time, and fight start hung: bisect over main (pantera vs
  // diablo, tools/proof-harness/fight.mjs) — #378 reaches the fight, #403 hangs at "Entering the
  // arena", and with this call removed the fight starts. retargetClipToRig stays defined above
  // for raw identity-rest clips; nothing in the game passes those any more.
  const actions = {};
  for (const [name, clip] of Object.entries(t3Clips)) {
    // ANIMATION GATE (owner t117u): fighter actions are FIGHT context; show clips never become actions.
    if (!checkClip(name, clip, CTX.FIGHT).ok) continue;
    try {
      const action = mixer.clipAction(clip);
      const loop = clip.userData.loop;
      action.setLoop(loop ? (clip.userData.pingpong ? THREE.LoopPingPong : THREE.LoopRepeat) : THREE.LoopOnce, Infinity);
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
  // Chest swing aligns the OVERALL torso (hips -> head) with the source's,
  // not the upper-chest bone alone: on a model sculpted hunched (old Doc
  // Frank, the Tripo demon) aligning Spine2->Neck straightened the chest and
  // threw the head back (torso error 11.6 deg vs 1-2 deg on Mixamo rigs).
  const dirs = { Chest: dir(by.Hips, by.Head) };
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
  // Floor contact (2026-10-21): the humanoid joints under the hips, and how
  // high the lowest of them sits at rest (the standing ankle/toe height) —
  // retargetT3Clips keeps every posed frame at or above that level.
  const contact = Object.values(by).filter(b => b === by.Hips || isAnc(by.Hips, b));
  const floorY = Math.min(...contact.map(b => rest(b).pos.y));
  return { bones, by, chest, driver, rest, facesNegZ, swapLR, dirs, hipsY: rest(by.Hips).pos.y, contact, floorY,
    trackName: (b) => (nameCount[b.name] === 1 ? b.name : b.uuid), uniqueNames: bones.every(b => nameCount[b.name] === 1) };
}

/* Source-side data per bank: hierarchy order + rest directions. */
function sourceInfo(skel, THREE) {
  if (skel._info) return skel._info;
  const P = {}, par = {};
  for (const j of skel.joints) { P[j.name] = new THREE.Vector3().fromArray(j.rest); par[j.name] = j.parent; }
  const d = (a, b) => (P[a] && P[b]) ? new THREE.Vector3().subVectors(P[b], P[a]) : null;
  const dirs = { Chest: d('Hips', 'Head') }; // overall torso, see analyzeRig
  for (const s of ['Left', 'Right']) {
    dirs[s + 'Shoulder'] = d(s + 'Shoulder', s + 'Arm');
    dirs[s + 'Arm'] = d(s + 'Arm', s + 'ForeArm');
    dirs[s + 'ForeArm'] = d(s + 'ForeArm', s + 'Hand');
    dirs[s + 'UpLeg'] = d(s + 'UpLeg', s + 'Leg');
    dirs[s + 'Leg'] = d(s + 'Leg', s + 'Foot');
    const tip = P[s + 'ToeBase'] || (skel.foot_tip && skel.foot_tip[s + 'Foot'] ? new THREE.Vector3().fromArray(skel.foot_tip[s + 'Foot']) : null);
    dirs[s + 'Foot'] = tip && P[s + 'Foot'] ? new THREE.Vector3().subVectors(tip, P[s + 'Foot']) : null;
    // Foot-data sanity (2026-10-22): foot_tip is the centroid of the T3 rig's foot-part vertices
    // (tools/anim/t3_bank_skeleton.py). Across the 17 banks it sits 0.05-0.21 leg lengths from the
    // ankle — except bosconovitch, 0.52: his decoded foot part is scattered (27 verts spanning
    // 45 cm on a 0.35 m leg; the KMD seam-vertex gap in lab/README.md), so its "toe" pointed
    // ~65-90 deg sideways and Doc Frank's feet splayed out. A centroid further than 0.3 leg
    // lengths from the ankle is not a foot: such a foot keeps the fighter's own authored foot
    // relation to its shin instead (same rule as a target foot whose toe points backwards).
    if (dirs[s + 'Foot'] && P[s + 'UpLeg'] && P[s + 'Leg'] && P[s + 'Foot']) {
      const legLen = P[s + 'Leg'].distanceTo(P[s + 'UpLeg']) + P[s + 'Foot'].distanceTo(P[s + 'Leg']);
      if (legLen > 1e-6 && dirs[s + 'Foot'].length() / legLen > 0.3) dirs[s + 'Foot'] = 'leg';
    }
  }
  skel._info = { order: skel.joints.map(j => j.name), par, dirs, rootY: skel.root_rest_y, P };
  return skel._info;
}

/* Source joint positions for one frame (FK: rest offsets rotated by G). */
function sourcePosed(src, G) {
  const out = {};
  for (const j of src.order) {
    const p = src.par[j];
    if (!p || !out[p]) { out[j] = src.P[j].clone(); continue; }
    out[j] = src.P[j].clone().sub(src.P[p]).applyQuaternion(G[p]).add(out[p]);
  }
  return out;
}
/* Target bone positions for the posed world rotations W (FK on rest offsets). */
function targetPosed(rig, W, want) {
  const pos = new Map();
  const fk = (b) => {
    if (pos.has(b)) return pos.get(b);
    const r = rig.rest(b);
    const par = b.parent && b.parent.isBone ? b.parent : null;
    if (!par) { pos.set(b, r.pos.clone()); return pos.get(b); }
    const pr = rig.rest(par);
    const off = r.pos.clone().sub(pr.pos).applyQuaternion(pr.quat.clone().invert()).applyQuaternion(W.get(par));
    const v = fk(par).clone().add(off);
    pos.set(b, v);
    return v;
  };
  return want.map(fk);
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
    if (ds && dt && ds !== 'leg' && dt !== 'leg' && ds.lengthSq() > 1e-10 && dt.lengthSq() > 1e-10) {
      A[c].setFromUnitVectors(dt.clone().normalize(), ds.clone().applyQuaternion(F).normalize());
    }
  }
  for (const s of ['Left', 'Right']) {
    if (rig.dirs[s + 'Foot'] === 'leg' || src.dirs[s + 'Foot'] === 'leg') A[s + 'Foot'] = A[s + 'Leg'];
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
      // W per target bone.
      const solveW = () => {
        W.clear();
        for (const b of ordered) {
          const dv = rig.driver.get(b);
          const w = W.get(b) || new THREE.Quaternion();
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
        }
      };
      solveW();
      // Exact torso match: rotate the chest so the target's POSED hips->head
      // direction equals the source's (forward kinematics on both). A curved
      // target spine otherwise leans differently from T3's rigid torso.
      if (src.P.Hips && src.P.Head && G.Hips && G.Head) {
        const sp = sourcePosed(src, G);
        const ds = new THREE.Vector3().subVectors(sp.Head, sp.Hips).applyQuaternion(F).normalize();
        for (let it = 0; it < 2; it++) {
          const tp = targetPosed(rig, W, [rig.by.Hips, rig.by.Head]);
          const dt = new THREE.Vector3().subVectors(tp[1], tp[0]).normalize();
          if (dt.angleTo(ds) < 0.002) break;
          D.Chest.premultiply(new THREE.Quaternion().setFromUnitVectors(dt, ds));
          D.Neck = D.Chest;
          solveW();
        }
      }
      for (const b of driven) {
        const pw = (b.parent && W.get(b.parent)) || (b.parent ? rig.rest(b.parent).quat : tmpQ.identity());
        const local = tmpQ.copy(pw).invert().multiply(W.get(b));
        vals.get(b).set([local.x, local.y, local.z, local.w], f * 4);
      }
      if (hipPos) {
        const rt = raw.root_t[Math.min(f, raw.root_t.length - 1)];
        let dy = (rt[1] - src.rootY) * hipScale;
        if (clip.userData.noRise && dy > 0) dy = 0;
        // No floor penetration: no joint below its standing-rest height. The
        // bosconovitch and yoshimitsu banks' root heights do not match their
        // skeletons (bosconovitch lies 0.89 x hip height BELOW the floor in
        // t3_ko, yoshimitsu stands at 0.28-0.37 x hip height; every other
        // bank lies at +0.09..+0.21 and stands at 0.81..1.02), which sank
        // Doc Frank, Phantom and JIN through the stage. A no-op on frames
        // whose joints are already above the floor.
        const low = Math.min(...targetPosed(rig, W, rig.contact).map(p => p.y)) + dy;
        if (low < rig.floorY) dy += rig.floorY - low;
        tmpV.set(hipsRest.x, hipsRest.y + dy, hipsRest.z).applyMatrix4(hipsParentInv);
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
