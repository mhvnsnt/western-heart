/* SELECT POSES (owner t199u, 2026-10-23): every select fighter plays a
   real idle on its OWN rig, no two fighters on the same pose, and each
   pose comes from the Tekken character whose moves the fighter uses.

   How: the fighter's source bank (fighter.js bankIdFor, or the canon
   `base` Tekken character when the moveset has no t3_source yet) is
   forward-solved from its own decoded T3 clip (skeleton.json rest +
   rot_xyzw) into per-bone AIM DIRECTIONS in the body frame, the same
   format as data/stances/cmu-guard.json. stance-aim.js then drives the
   target rig by direction, so the pose never depends on the target's bind
   pose (the reason so many bank stances failed the old fit gates and fell
   back to the one shared CMU guard).

   Uniqueness: fighters sharing a bank get different clips from that
   bank, in roster order: neutral stance, then the round intro, the four
   win poses and the alt stances. Fighters with no decoded bank for their
   source get distinct, labelled CMU windows (mirrored / phase-shifted) and
   are listed in SELECT_POSE_DEBT for the anim lane. */
import { T3_BANKS, SOURCE_TO_BANK, getT3BankFacing } from './t3anims.js';

// Clip order inside one bank. key -> file in the bank folder.
export const POSE_CLIPS = [
  ['stance', 't3_neutral.json'], ['intro', 't3_stance.json'], ['win_rp', 't3_win_rp.json'],
  ['win_lp', 't3_win_lp.json'], ['win_lk', 't3_win_lk.json'], ['win_rk', 't3_win_rk.json'],
  ['stance_b', 't3_stance_b.json'], ['stance_c', 't3_stance_c.json'], ['block', 't3_block.json'],
];

// Canon base (roster-full.js `base`) -> T3 bank, used only when the
// fighter's moveset has no decoded bank (the moveset data lane will
// supersede this as t3_source fields land).
const BASE_TO_BANK = {
  'jin kazama': 'jin', 'lei wulong': 'lei', 'paul phoenix': 'paul', xiaoyu: 'xiaoyu',
  'eddy gordo': 'eddy', 'bryan fury': 'bryan', heihachi: 'heihachi', hwoarang: 'hwoarang',
  king: 'king', yoshimitsu: 'yoshimitsu', 'jack-7': 'gunjack', nina: 'nina', julia: 'julia',
  anna: 'anna', bosconovitch: 'bosconovitch', 'armor king': 'armorking', gon: 'gon',
  'true ogre': 'ogre', ogre: 'ogre', 'marshall law': 'law', 'forest law': 'forestlaw',
  kuma: 'kuma', panda: 'kuma', 'roger jr.': 'kuma',
};

export function poseBankFor(c, bankIdFor, getMovesetInfo) {
  let b = null;
  try { b = bankIdFor(c.id, getMovesetInfo && getMovesetInfo(c.id) ? c.id : (c.moveset || c.id)); } catch (_) {}
  if (b && T3_BANKS[b]) return b;
  const k = String(c.base || '').toLowerCase().trim();
  const viaBase = BASE_TO_BANK[k] || SOURCE_TO_BANK[k];
  return viaBase && T3_BANKS[viaBase] ? viaBase : null;
}

/* Deterministic assignment over the VISIBLE select roster.
   Returns Map(id -> { bank, clip, file } | { bank:null, cmu:{mirror, phase} }). */
export function assignSelectPoses(fighters, bankOf) {
  const out = new Map(), used = new Map();
  let cmuN = 0;
  for (const c of fighters) {
    const bank = bankOf(c);
    if (!bank) {
      out.set(c.id, { bank: null, clip: `cmu#${cmuN}`, cmu: { mirror: cmuN % 2 === 1, phase: (Math.floor(cmuN / 2) * 0.37) % 2 } });
      cmuN++; continue;
    }
    const n = used.get(bank) || 0; used.set(bank, n + 1);
    const [clip, file] = POSE_CLIPS[n % POSE_CLIPS.length];
    out.set(c.id, { bank, clip, file, order: n });
  }
  return out;
}

const _cache = new Map();
/* Bank clip -> aim data { fps, dirs } (stance-aim.js format). */
export async function bankAimData(THREE, bank, file) {
  const key = bank + '/' + file;
  if (_cache.has(key)) return _cache.get(key);
  const p = (async () => {
    const base = T3_BANKS[bank];
    const [sr, cr] = await Promise.all([fetch(base + 'skeleton.json'), fetch(base + file)]);
    if (!sr.ok || !cr.ok) return null;
    const skel = await sr.json(), clip = await cr.json();
    const J = skel.joints, byName = new Map(J.map(j => [j.name, j]));
    const rot = clip.rot_xyzw || {};
    const F = Math.max(...Object.values(rot).map(a => a.length), 0);
    if (!F) return null;
    const turned = !!(getT3BankFacing(bank) && getT3BankFacing(bank).turned);
    const sw = (n) => turned ? n.replace(/^Left/, '#').replace(/^Right/, 'Left').replace(/^#/, 'Right') : n;
    const dirs = {};
    const push = (n, v) => { (dirs[n] = dirs[n] || []).push(v); };
    const step = Math.max(1, Math.round(F / 60));
    for (let f = 0; f < F; f += step) {
      const wq = new Map(), wp = new Map();
      for (const j of J) { // joints are listed parent-first
        const r = rot[j.name] ? rot[j.name][Math.min(f, rot[j.name].length - 1)] : [0, 0, 0, 1];
        const lq = new THREE.Quaternion(r[0], r[1], r[2], r[3]);
        if (!j.parent) { wq.set(j.name, lq); wp.set(j.name, new THREE.Vector3(...j.rest)); continue; }
        const pq = wq.get(j.parent), pp = wp.get(j.parent), pr = byName.get(j.parent).rest;
        const off = new THREE.Vector3(j.rest[0] - pr[0], j.rest[1] - pr[1], j.rest[2] - pr[2]).applyQuaternion(pq);
        wp.set(j.name, pp.clone().add(off)); wq.set(j.name, pq.clone().multiply(lq));
      }
      // body frame: source faces +Z, left = +X; turned banks face -Z
      const P = (n) => { const v = wp.get(n); return v ? (turned ? new THREE.Vector3(-v.x, v.y, -v.z) : v) : null; };
      const d = (a, b) => { const A = P(a), B = P(b); if (!A || !B) return null; const v = B.clone().sub(A); return v.lengthSq() > 1e-10 ? v.normalize().toArray() : null; };
      const L = d(sw('RightUpLeg'), sw('LeftUpLeg')), up = d('Hips', 'Chest') || [0, 1, 0];
      if (!L) return null;
      push('Hips', [...L, ...up]); push('Spine', up);
      const head = d('Chest', 'Head'); if (head) { push('Neck', head); push('Head', head); }
      for (const [n, c] of [['Shoulder', 'Arm'], ['Arm', 'ForeArm'], ['ForeArm', 'Hand'], ['UpLeg', 'Leg'], ['Leg', 'Foot']]) {
        for (const s of ['Left', 'Right']) { const v = d(sw(s + n), sw(s + c)); if (v) push(s + n, v); }
      }
    }
    for (const k of Object.keys(dirs)) if (dirs[k].length !== dirs.Hips.length) delete dirs[k];
    return { fps: (clip.fps || 30) / step, frames: dirs.Hips.length, dirs, source: `${bank}/${file}` };
  })();
  _cache.set(key, p);
  return p;
}

/* CMU window variant for fighters with no decoded source bank. */
export function cmuVariant(data, { mirror, phase }) {
  if (!mirror) return data;
  const dirs = {};
  const flip = (v) => v.map((x, i) => (i % 3 === 0 ? -x : x));
  for (const [n, arr] of Object.entries(data.dirs)) {
    const m = n.startsWith('Left') ? 'Right' + n.slice(4) : n.startsWith('Right') ? 'Left' + n.slice(5) : n;
    dirs[m] = arr.map(v => (n === 'Hips' ? [...flip(v.slice(0, 3)).map(x => -x), ...flip(v.slice(3))] : flip(v)));
  }
  return { ...data, dirs, phase };
}
