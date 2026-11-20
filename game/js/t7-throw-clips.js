/* ============================================================
   WESTERN HEART — t7-throw-clips.js (Tekken 7 throw-pair clips)
   Pure T7 throw wiring: no THREE, no window, no fetch at import
   time, so node can test it headlessly (same discipline as
   t3-throw.js). The thrower + victim clips for Pantera's 1+3 /
   2+4, extracted from the baked T7 graph bank
   (game/assets/anim/t7/king/graph-clips/, wh-t7-graph-clips/1)
   into standalone wh-anim/1 files under
   game/assets/anim/t7/king/throws/ — one file per clip, so the
   throw path loads two small files instead of the whole 57 MB
   bank (ensureT7Graph loads all 10 shards; the default game
   must not).

   SOURCE (all from game/assets/anim/t7/king/graph.json,
   verified 2026-11-20, main 0bc373e0):
     1+3 -> move 1785 ThrmvLB2_00, bank common, clip 709,
            anim naco_tukami2l(DVD), 40f @60fps, first_active 12
     2+4 -> move 1787 ThrmvRB2_00, bank rotsm, clip 534,
            anim msco_rtukami(DVD), 40f @60fps, first_active 12
   Both moves are throw-class (damage == 0x4000, the exact throw
   marker fighter.js uses) and their cancel lists, at the connect
   window [12, 14], name the VICTIM's reaction move — five rows,
   one per throw direction. The requirement-list ids behind them
   (graph.requirements) are:
     2594 = [[3, 1536]]  -> FRONT reactions (FL/FR nage, dmg 35)
     1610 = [[5, 1536]]  -> LEFT reactions (Lnage)
     1612 = [[6, 1536]]  -> RIGHT reactions (Rnage, dmg 42)
     1614 = [[4, 1536]]  -> BACK reactions (BL/BR nage, dmg 60)
     2598 = [[27, 2536]] -> AIR reactions (AirDragon/AirHizaj)
   That mapping is PROVEN from the data, not labelled: across
   all 43 throw-class moves in the graph, req 2594 always points
   at a front (*F*nage / throw-specific front) reaction, 1610
   always at *Lnage*, 1612 always at *Rnage*, 1614 always at
   *B*nage, 2598 always at *Air*. (The exe note in
   docs/proof/2026-11-10/t7-requirements/README.md agrees:
   "Throw-side cases 2..16 compare the id with a computed throw
   direction".) The front damage 35 on both FL/FR nage moves is
   the documented front-throw damage. The victim clips are the
   reactions KING's graph carries for a victim of King's throw;
   they are King's own rotsm-bank animations (the same bank the
   thrower clips come from), applied to the victim's rig.

   UNPROVEN, flagged not guessed: which physical side "left" /
   "right" is (the names only say L/R; the engine's computed
   throw direction is not in the shipped data). The caller maps
   its quadrant to a situation string; the front default — the
   only case the live game uses today — needs no left/right call.
   A playtest must confirm the victim does not mirror on side
   throws before side situations are trusted live.

   T7-FIRST RULE: when these clips load, they are the DEFAULT
   pair for Pantera 1+3 / 2+4. When they do not load (fetch
   fails, file missing, validation fails), resolution returns
   null and the caller keeps the T3 pair (rows 415/417 +
   victims 3018/3051) — the working fallback. Nothing here
   invents motion: an unknown input or situation returns null.

   TIMING (documented limit, same as the DW Surge Kit swap in
   fighter.js _bindThrowPair): the pair clock, anchors, damage
   time and break windows stay the T3 pair's. The T7 thrower
   clips are 40f; the T7 front victim clips are 130f (1+3) /
   138f (2+4) — longer than the T3 pair — so frames past the
   pair duration are cut by the pair clock, and the thrower
   finishes before the victim. What the thrower does after its
   clip ends (hold last frame vs blend to idle) is the
   integration's call, not this module's.
   ============================================================ */

/** Asset dir for the standalone throw clips (page-relative, like t3-throw.js loadThrowTables). */
export const T7_THROW_CLIP_DIR = 'assets/anim/t7/king/throws/';

/** Situations a T7 throw can connect in (the five cancel rows). */
export const T7_THROW_SITUATIONS = ['front', 'left', 'right', 'back', 'air'];

/** The 21 bones every T7 king clip carries (skeleton.json). */
export const T7_THROW_BONES = ['Hips', 'Spine', 'Chest', 'Neck', 'Head',
  'LeftShoulder', 'LeftArm', 'LeftForeArm', 'LeftHand', 'LeftUpLeg', 'LeftLeg', 'LeftFoot', 'LeftToeBase',
  'RightShoulder', 'RightArm', 'RightForeArm', 'RightHand', 'RightUpLeg', 'RightLeg', 'RightFoot', 'RightToeBase'];

/*
 * Pair table. Thrower: graph move id + clip key + frames. Victim: per
 * situation, graph move id + clip key + frames + the nage move's own
 * damage (the throw damage T7 books on the reaction; the WH move's own
 * damage still rules — MOD decision 2026-10-24, same as T3).
 */
export const T7_THROW_PAIRS = {
  '1+3': {
    thrower: { key: 'common_709', move: 1785, name: 'ThrmvLB2_00', anim: 'naco_tukami2l(DVD)', bank: 'common', clip: 709, frames: 40, fps: 60, firstActive: 12 },
    victim: {
      front: { key: 'rotsm_574', move: 2125, name: 'Kg_FLnage00_n', anim: 'nakg_nagexx0a_f(DVD)', bank: 'rotsm', clip: 574, frames: 130, fps: 60, damage: 35 },
      left: { key: 'rotsm_588', move: 2135, name: 'Kg_Lnage_n', anim: 'nagexx2d_n(DVD)', bank: 'rotsm', clip: 588, frames: 226, fps: 60, damage: 0 },
      right: { key: 'rotsm_590', move: 2137, name: 'Kg_Rnage_n', anim: 'V_kgnc_n(DVD)', bank: 'rotsm', clip: 590, frames: 160, fps: 60, damage: 42 },
      back: { key: 'rotsm_592', move: 2139, name: 'Kg_BLnage_n', anim: 'skkg_kebi_b(DVD)', bank: 'rotsm', clip: 592, frames: 203, fps: 60, damage: 60 },
      air: { key: 'rotsm_718', move: 2276, name: 'Kg_AirHizaj_n', anim: 'sukg_skyhizaj_n(DVD)', bank: 'rotsm', clip: 718, frames: 155, fps: 60, damage: 30 },
    },
  },
  '2+4': {
    thrower: { key: 'rotsm_534', move: 1787, name: 'ThrmvRB2_00', anim: 'msco_rtukami(DVD)', bank: 'rotsm', clip: 534, frames: 40, fps: 60, firstActive: 12 },
    victim: {
      front: { key: 'rotsm_578', move: 2129, name: 'Kg_FRnage00_n', anim: 'kjkg_brain_f(DVD)', bank: 'rotsm', clip: 578, frames: 138, fps: 60, damage: 35 },
      left: { key: 'rotsm_588', move: 2135, name: 'Kg_Lnage_n', anim: 'nagexx2d_n(DVD)', bank: 'rotsm', clip: 588, frames: 226, fps: 60, damage: 0 },
      right: { key: 'rotsm_590', move: 2137, name: 'Kg_Rnage_n', anim: 'V_kgnc_n(DVD)', bank: 'rotsm', clip: 590, frames: 160, fps: 60, damage: 42 },
      back: { key: 'rotsm_594', move: 2141, name: 'Kg_BRnage_n', anim: 'bk_cob_n(DVD)', bank: 'rotsm', clip: 594, frames: 240, fps: 60, damage: 60 },
      air: { key: 'rotsm_716', move: 2274, name: 'Kg_AirDragon_n', anim: 'sukg_skydora_n(DVD)', bank: 'rotsm', clip: 716, frames: 90, fps: 60, damage: 0 },
    },
  },
};

/**
 * Resolve the T7 pair for one throw input + situation.
 * Returns { input, situation, thrower, victim } (table entries,
 * never invented) or null — unknown input, unknown situation, or
 * a missing table entry. Null means "T7 unavailable": the caller
 * keeps the T3 pair. Default situation is 'front' (the live
 * game's front throw).
 */
export function resolveT7ThrowPair(input, situation = 'front') {
  const pair = T7_THROW_PAIRS[input];
  if (!pair) return null;
  if (!T7_THROW_SITUATIONS.includes(situation)) return null;
  const victim = pair.victim[situation];
  if (!victim) return null;
  return { input, situation, thrower: pair.thrower, victim };
}

/** Asset path for one standalone throw clip. */
export function t7ThrowClipPath(key) {
  return `${T7_THROW_CLIP_DIR}${key}.json`;
}

/**
 * Structural validation of one standalone wh-anim/1 throw clip
 * record (the same checks the node probe runs, minus FK shape).
 * Returns { ok: true } or { ok: false, errors: [...] }. Never throws.
 * Shape (FK chest-bend / root-Y) is verified by
 * test/t7-throw-clips.test.mjs, not here: the runtime loader must
 * stay cheap, and a structurally valid record from the bank is
 * already shape-proven at extraction time.
 */
export function validateT7ThrowClip(key, rec) {
  const errors = [];
  if (!rec || typeof rec !== 'object') return { ok: false, errors: ['not an object'] };
  if (rec.format !== 'wh-anim/1') errors.push(`format ${rec.format} != wh-anim/1`);
  if (rec.fps !== 60) errors.push(`fps ${rec.fps} != 60`);
  if (rec.loop !== false) errors.push('loop is not false');
  const bones = rec.bones || [];
  if (bones.length !== 21) errors.push(`bones ${bones.length} != 21`);
  for (const b of T7_THROW_BONES) if (!bones.includes(b)) errors.push(`missing bone ${b}`);
  const rot = rec.rot_xyzw || {};
  const rootT = rec.root_t || [];
  const fwd = rec.root_motion_fwd_m || [];
  const n = rootT.length;
  if (n === 0) errors.push('root_t is empty');
  if (fwd.length !== n) errors.push(`root_motion_fwd_m ${fwd.length} != root_t ${n}`);
  let nan = 0, zero = 0, badNorm = 0, badLen = 0;
  for (const b of bones) {
    const arr = rot[b];
    if (!arr || arr.length !== n) { badLen++; continue; }
    for (const q of arr) {
      if (!Array.isArray(q) || q.length !== 4) { badLen++; continue; }
      if (q.some((v) => typeof v !== 'number' || !Number.isFinite(v))) { nan++; continue; }
      const l = Math.hypot(q[0], q[1], q[2], q[3]);
      if (l === 0) zero++;
      else if (Math.abs(l - 1) > 0.01) badNorm++;
    }
  }
  if (badLen) errors.push(`${badLen} bone channels with wrong length`);
  if (nan) errors.push(`${nan} non-finite quat components`);
  if (zero) errors.push(`${zero} zero quats`);
  if (badNorm) errors.push(`${badNorm} quats with |norm-1| > 0.01`);
  for (let f = 0; f < n; f++) {
    const t = rootT[f];
    if (!Array.isArray(t) || t.length !== 3 || t.some((v) => typeof v !== 'number' || !Number.isFinite(v))) { errors.push(`root_t[${f}] is not 3 finite numbers`); break; }
  }
  const table = Object.values(T7_THROW_PAIRS).flatMap((p) => [p.thrower, ...Object.values(p.victim)]).find((c) => c.key === key);
  if (table && n !== table.frames) errors.push(`frames ${n} != table ${table.frames} for ${key}`);
  if (table && rec.t7_source && rec.t7_source.clip !== table.clip) errors.push(`t7_source.clip ${rec.t7_source.clip} != table ${table.clip}`);
  return errors.length ? { ok: false, errors } : { ok: true };
}

/* ---- loaders (browser fetch; cached; never throw) ---- */
const _clipCache = new Map();
/** One standalone throw clip record, validated, or null (missing / fetch fails / invalid). */
export async function loadT7ThrowClip(key, fetchFn) {
  if (_clipCache.has(key)) return _clipCache.get(key);
  const p = (async () => {
    try {
      const f = fetchFn || (typeof fetch !== 'undefined' ? fetch : null);
      if (!f) return null;
      const res = await f(t7ThrowClipPath(key));
      if (!res.ok) return null;
      const rec = await res.json();
      if (!validateT7ThrowClip(key, rec).ok) return null;
      return rec;
    } catch (e) { return null; }
  })();
  _clipCache.set(key, p);
  return p;
}

/** Both records of a resolved T7 pair, or null (unresolved input/situation, or either clip unavailable/invalid). */
export async function loadT7ThrowPair(input, situation = 'front', fetchFn) {
  const pair = resolveT7ThrowPair(input, situation);
  if (!pair) return null;
  const [thrower, victim] = await Promise.all([
    loadT7ThrowClip(pair.thrower.key, fetchFn),
    loadT7ThrowClip(pair.victim.key, fetchFn),
  ]);
  if (!thrower || !victim) return null;
  return { ...pair, throwerRecord: thrower, victimRecord: victim };
}
