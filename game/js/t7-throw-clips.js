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
   the documented front-throw damage.

   ROLES, CORRECTED 2026-11-21 (Lane E, T7 throw fix — the old
   table mislabelled the `_n` motions as the victim; they are the
   THROWER's throw motions, and the victim's receivers are the
   `_y` moves, fixed here):
     grab       = the 40f attempt (1785/1787). Plays first; on
                  connect the pair clock starts and the throw
                  motion + receiver play together.
     throwMotion = the `_n` throw motion (574/578/588/590/592/
                  594/716/718) — the thrower's half of the pair.
     victim     = the `_y` receiver (575/579/589/591/593/595/
                  717/719) — the victim's half, rebuilt with the
                  joint sandwich (see below) and stored as
                  `rotsm_<n>-fixed.json`. The receiver's f0 is
                  the thrower's f0: both are 130f/138f front, and
                  the pair clock starts at connect, where
                  `_n` f0 == `_y` f0.
   The victim clips are the reactions King's graph carries for a
   victim of King's throw; they are King's own rotsm-bank
   animations (the same bank the thrower clips come from),
   applied to the victim's rig.

   JOINT SANDWICH (Lane B, 2026-11-21): the `_y` receivers as
   decoded by the 574-only sandwich were flipped ~180 deg at f0
   (victim upside down, feet 2.00 m up). The corrected sandwich
   (tools/anim/tkmovesets2/joint-sandwich.json — U/V/W quats,
   fit cost 1.26e-11; 574 max 0.1303 deg, 578 max 0.1264 deg,
   hold-out 588 max 0.1278 deg) rebuilds all 24 receivers +
   hold 554 + 15 escapes. Fixed receivers at f0: torso pitch
   22.9–34.4 deg (591: 45.1 deg — the untouched approximate
   Spine, spine-identity pitch 12.8 deg), feet Y 0.13 m, head
   1.53–1.55 m. Only the Hips channel differs from the decoded
   originals; the other 20 joints, root_t and root_motion_fwd_m
   are byte-identical. Spine was NOT touched. Ground face-down
   receivers (692/696/700/704) are unchanged by the rebuild
   (their E_BASE stayed in-family) and still carry a heading
   question — see OPEN below.

   TWO-STAGE RECEIVER (real T7 moveset, T7_King.tkmvst,
   verified 2026-11-21): the grab does NOT go straight to the
   `_y` receiver. On connect the victim enters the grabbed hold,
   move 554 (`___________`, anim nab6_guard(DVD), 30f) — a held,
   lifted, bent-forward pose (f0: 25 deg forward lean, feet
   0.33 m dangling) — and the thrower's `_n` HitCondition then
   selects the specific `_y` in the STANDING slot, with 554 in
   all 13 other slots. The hold is breakable (cancel reqs
   (182, 4/2/8), detection [1, 2], start 1) to move 1423
   (`Kg_sKAM00_`, 60f). Each `_y` is breakable in its window to
   its escape (see the table): front [1, 15] start 15 ->
   Esc_FLnage00_n / Esc_FRnage00_n; left/right [1, 10] start 1
   -> SideEscL_n / SideEscR_n. BACK and AIR receivers are
   UNBREAKABLE — the real file has zero cancel rows for
   2140/2142/2144 and 2275/2277. The hold + escapes live in the
   same throws/ dir (hold_554.json, esc_<move>.json), decoded
   from the real .tkmvst (control-proven: the 2126 blob sampled
   c8 == the arc-slice c8 exactly, max abs diff 0.0).

   DAMAGE, CORRECTED (property 33307, real .tkmvst):
     2125=35, 2129=35, 2135=40, 2137=42, 2139=60, 2141=60,
     2274=30, 2276=30. The old table had 2135=0 and 2274=0.
   The throw damage T7 books on the reaction is the `_n` move's
   own damage (the WH move's own damage still rules — MOD
   decision 2026-10-24, same as T3).

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
   time and break windows stay the T3 pair's. The grab is 40f;
   the front throw motion and receiver are both 130f (1+3) /
   138f (2+4) — longer than the T3 pair — so frames past the
   pair duration are cut by the pair clock, and the thrower
   finishes before the victim. What the thrower does after its
   clip ends (hold last frame vs blend to idle) is the
   integration's call, not this module's.

   OPEN, flagged not decided (see the PR body):
     - Live side/air gate: left/right/air throwMotion +
       receiver data is now complete in this table, but
       t7SituationForQuadrant still returns null for them
       (side mapping unproven, air has no quadrant signal) —
       those throws keep T3 live.
     - Live T7 break routing: the hold + escape data is in
       this table, but the live game still uses the T3 pair's
       break windows. Routing a live break to the escape needs
       the thrower's escape-reaction move, which the shipped
       data does not name — not invented here.
     - Runtime yaw: the render proof places the pair in the
       thrower's shared frame (one heading, one translation);
       the live game squares the pair heading in
       _startThrowPair/_driveThrowPair. Whether the authored
       facing deltas need any further yaw work is a playtest
       call, not a table change.
     - Crouch/ground receivers (655/657/786, 663–704) and the
       extra front/chain receivers (597/615/581) exist as fixed
       files in throws/ but are NOT in this table: they are
       reached via other throw moves (ThrmvLOW_*, ThrmvDWN_*,
       2143/2163/2131), not via 1785/1787's cancel rows.
       Posture-aware resolution is the follow-up.
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
 * Pair table. grab: the 40f attempt (connects at first_active
 * 12). throwMotion: per situation, the thrower's `_n` throw
 * motion + its own damage (the throw damage T7 books on the
 * reaction; the WH move's own damage still rules — MOD decision
 * 2026-10-24, same as T3). hold: the grabbed hold (move 554),
 * shared by both inputs. victim: per situation, the victim's
 * `_y` receiver (fixed file) + its break window and escape —
 * null window/escape means UNBREAKABLE in the real file.
 */
export const T7_THROW_PAIRS = {
  '1+3': {
    grab: { key: 'common_709', move: 1785, name: 'ThrmvLB2_00', anim: 'naco_tukami2l(DVD)', bank: 'common', clip: 709, frames: 40, fps: 60, firstActive: 12 },
    throwMotion: {
      front: { key: 'rotsm_574', move: 2125, name: 'Kg_FLnage00_n', anim: 'nakg_nagexx0a_f(DVD)', bank: 'rotsm', clip: 574, frames: 130, fps: 60, damage: 35 },
      left: { key: 'rotsm_588', move: 2135, name: 'Kg_Lnage_n', anim: 'nagexx2d_n(DVD)', bank: 'rotsm', clip: 588, frames: 226, fps: 60, damage: 40 },
      right: { key: 'rotsm_590', move: 2137, name: 'Kg_Rnage_n', anim: 'V_kgnc_n(DVD)', bank: 'rotsm', clip: 590, frames: 160, fps: 60, damage: 42 },
      back: { key: 'rotsm_592', move: 2139, name: 'Kg_BLnage_n', anim: 'skkg_kebi_b(DVD)', bank: 'rotsm', clip: 592, frames: 203, fps: 60, damage: 60 },
      air: { key: 'rotsm_718', move: 2276, name: 'Kg_AirHizaj_n', anim: 'sukg_skyhizaj_n(DVD)', bank: 'rotsm', clip: 718, frames: 155, fps: 60, damage: 30 },
    },
    hold: { key: 'hold_554', move: 554, name: '___________', anim: 'nab6_guard(DVD)', bank: 'rotsm', clip: 554, frames: 30, fps: 60, breaksTo: 1423, breakWindowFrames: [1, 2] },
    victim: {
      front: { key: 'rotsm_575-fixed', move: 2126, name: 'Kg_FLnage00_y', anim: 'nakg_nagexx0a_y(DVD)', bank: 'rotsm', clip: 575, frames: 130, fps: 60, breakWindowFrames: [1, 15], breakStartFrame: 15, escape: { key: 'esc_2127', move: 2127, name: 'Esc_FLnage00_n', anim: 'kjkg_swingcan_f(DVD)', clip: 2127, frames: 70 } },
      left: { key: 'rotsm_589-fixed', move: 2136, name: 'Kg_Lnage_y', anim: 'nagexx2d_y(DVD)', bank: 'rotsm', clip: 589, frames: 241, fps: 60, breakWindowFrames: [1, 10], breakStartFrame: 1, escape: { key: 'esc_237', move: 237, name: 'SideEscL_n', anim: 'G_Lnuke_n(DVD)', clip: 237, frames: 30 } },
      right: { key: 'rotsm_591-fixed', move: 2138, name: 'Kg_Rnage_y', anim: 'V_kgnc_y(DVD)', bank: 'rotsm', clip: 591, frames: 160, fps: 60, breakWindowFrames: [1, 10], breakStartFrame: 1, escape: { key: 'esc_239', move: 239, name: 'SideEscR_n', anim: 'G_Rnuke_n(DVD)', clip: 239, frames: 30 } },
      back: { key: 'rotsm_593-fixed', move: 2140, name: 'Kg_BLnage_y', anim: 'ozkg_kebi_y(DVD)', bank: 'rotsm', clip: 593, frames: 202, fps: 60, breakWindowFrames: null, breakStartFrame: null, escape: null },
      air: { key: 'rotsm_719-fixed', move: 2277, name: 'Kg_AirHizaj_y', anim: 'sukg_skyhizaj_y(DVD)', bank: 'rotsm', clip: 719, frames: 155, fps: 60, breakWindowFrames: null, breakStartFrame: null, escape: null },
    },
  },
  '2+4': {
    grab: { key: 'rotsm_534', move: 1787, name: 'ThrmvRB2_00', anim: 'msco_rtukami(DVD)', bank: 'rotsm', clip: 534, frames: 40, fps: 60, firstActive: 12 },
    throwMotion: {
      front: { key: 'rotsm_578', move: 2129, name: 'Kg_FRnage00_n', anim: 'kjkg_brain_f(DVD)', bank: 'rotsm', clip: 578, frames: 138, fps: 60, damage: 35 },
      left: { key: 'rotsm_588', move: 2135, name: 'Kg_Lnage_n', anim: 'nagexx2d_n(DVD)', bank: 'rotsm', clip: 588, frames: 226, fps: 60, damage: 40 },
      right: { key: 'rotsm_590', move: 2137, name: 'Kg_Rnage_n', anim: 'V_kgnc_n(DVD)', bank: 'rotsm', clip: 590, frames: 160, fps: 60, damage: 42 },
      back: { key: 'rotsm_594', move: 2141, name: 'Kg_BRnage_n', anim: 'bk_cob_n(DVD)', bank: 'rotsm', clip: 594, frames: 240, fps: 60, damage: 60 },
      air: { key: 'rotsm_716', move: 2274, name: 'Kg_AirDragon_n', anim: 'sukg_skydora_n(DVD)', bank: 'rotsm', clip: 716, frames: 90, fps: 60, damage: 30 },
    },
    hold: { key: 'hold_554', move: 554, name: '___________', anim: 'nab6_guard(DVD)', bank: 'rotsm', clip: 554, frames: 30, fps: 60, breaksTo: 1423, breakWindowFrames: [1, 2] },
    victim: {
      front: { key: 'rotsm_579-fixed', move: 2130, name: 'Kg_FRnage00_y', anim: 'kjkg_brain_y(DVD)', bank: 'rotsm', clip: 579, frames: 138, fps: 60, breakWindowFrames: [1, 15], breakStartFrame: 15, escape: { key: 'esc_2133', move: 2133, name: 'Esc_FRnage00_n', anim: 'sukg_brainnuke_f(DVD)', clip: 2133, frames: 65 } },
      left: { key: 'rotsm_589-fixed', move: 2136, name: 'Kg_Lnage_y', anim: 'nagexx2d_y(DVD)', bank: 'rotsm', clip: 589, frames: 241, fps: 60, breakWindowFrames: [1, 10], breakStartFrame: 1, escape: { key: 'esc_237', move: 237, name: 'SideEscL_n', anim: 'G_Lnuke_n(DVD)', clip: 237, frames: 30 } },
      right: { key: 'rotsm_591-fixed', move: 2138, name: 'Kg_Rnage_y', anim: 'V_kgnc_y(DVD)', bank: 'rotsm', clip: 591, frames: 160, fps: 60, breakWindowFrames: [1, 10], breakStartFrame: 1, escape: { key: 'esc_239', move: 239, name: 'SideEscR_n', anim: 'G_Rnuke_n(DVD)', clip: 239, frames: 30 } },
      back: { key: 'rotsm_595-fixed', move: 2142, name: 'Kg_BRnage_y', anim: 'Pkg_cob_y(DVD)', bank: 'rotsm', clip: 595, frames: 239, fps: 60, breakWindowFrames: null, breakStartFrame: null, escape: null },
      air: { key: 'rotsm_717-fixed', move: 2275, name: 'Kg_AirDragon_y', anim: 'sukg_skydora_y(DVD)', bank: 'rotsm', clip: 717, frames: 90, fps: 60, breakWindowFrames: null, breakStartFrame: null, escape: null },
    },
  },
};

/**
 * Resolve the T7 pair for one throw input + situation.
 * Returns { input, situation, grab, thrower, hold, victim }
 * (table entries, never invented) or null — unknown input,
 * unknown situation, or a missing table entry. Null means
 * "T7 unavailable": the caller keeps the T3 pair. Default
 * situation is 'front' (the live game's front throw).
 * `thrower` is the throw MOTION for this situation (the old
 * table's `victim` field, re-roled) — fighter.js _t7ThrowActions
 * reads t7.thrower.key / t7.victim.key, so the swap needs no
 * caller change. `grab` is the 40f attempt; `hold` is the
 * grabbed hold (move 554) the victim enters on connect.
 */
export function resolveT7ThrowPair(input, situation = 'front') {
  const pair = T7_THROW_PAIRS[input];
  if (!pair) return null;
  if (!T7_THROW_SITUATIONS.includes(situation)) return null;
  const thrower = pair.throwMotion[situation];
  const victim = pair.victim[situation];
  if (!thrower || !victim) return null;
  return { input, situation, grab: pair.grab, thrower, hold: pair.hold, victim };
}

/**
 * Resolve the two-stage receiver for one throw input +
 * situation: the grabbed hold (move 554) the victim enters on
 * connect, then the `_y` receiver, with the break window and
 * the escape move the real file gives that receiver.
 * Returns { input, situation, hold, receiver, breakWindowFrames,
 * breakStartFrame, escape } or null — unknown input, unknown
 * situation, or a missing table entry. `escape` is null (and
 * `breakWindowFrames` null) for the UNBREAKABLE back/air
 * receivers. Live break routing still uses the T3 pair's
 * windows (see the module header) — this resolver is the DATA
 * the routing will read when it is wired.
 */
export function resolveT7ThrowReceiver(input, situation = 'front') {
  const pair = T7_THROW_PAIRS[input];
  if (!pair) return null;
  if (!T7_THROW_SITUATIONS.includes(situation)) return null;
  const receiver = pair.victim[situation];
  if (!receiver) return null;
  return { input, situation, hold: pair.hold, receiver, breakWindowFrames: receiver.breakWindowFrames, breakStartFrame: receiver.breakStartFrame, escape: receiver.escape };
}

/**
 * WH throw quadrant (t3-throw.js throwQuadrant: 0 front, 1 side1,
 * 2 back, 3 side3) -> T7 situation, or null when this lane does
 * NOT wire the T7 pair for that quadrant. Front and back resolve
 * from the graph bank's own pairing; left/right return null —
 * which physical side "left"/"right" is is UNPROVEN (see the
 * module header), so side throws keep the T3 pair; air has no
 * quadrant signal on the throw path, so it also keeps T3.
 * The left/right/air data is complete in the table — only the
 * live gate is still closed.
 */
export function t7SituationForQuadrant(quadrant) {
  if (quadrant === 0) return 'front';
  if (quadrant === 2) return 'back';
  return null;
}

/** Asset path for one standalone throw clip. */
export function t7ThrowClipPath(key) {
  return `${T7_THROW_CLIP_DIR}${key}.json`;
}

/**
 * Structural validation of one standalone wh-anim/1 throw clip
 * record (the same checks the node probe runs, minus FK shape).
 * Returns { ok: true, errors: [] } or { ok: false, errors: [...] }. Never throws.
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
  const table = Object.values(T7_THROW_PAIRS).flatMap((p) => [
    p.grab,
    ...Object.values(p.throwMotion),
    p.hold,
    ...Object.values(p.victim),
    ...Object.values(p.victim).map((v) => v.escape).filter(Boolean),
  ]).find((c) => c.key === key);
  if (table && n !== table.frames) errors.push(`frames ${n} != table ${table.frames} for ${key}`);
  if (table && rec.t7_source && rec.t7_source.clip !== table.clip) errors.push(`t7_source.clip ${rec.t7_source.clip} != table ${table.clip}`);
  return errors.length ? { ok: false, errors } : { ok: true, errors: [] };
}

/* ---- loaders (browser fetch; cached; never throw) ---- */
const _clipCache = new Map();
const _clipRecords = new Map(); // key -> resolved record (sync read of the async cache)
/** One standalone throw clip record that already loaded, or null (not loaded yet / failed). Sync read only — never triggers a fetch; the throw bind path (fighter.js _bindThrowPair is sync) swaps the T7 pair in from this cache, and keeps the T3 pair when it is empty. */
export function getT7ThrowClipRecord(key) {
  return _clipRecords.get(key) || null;
}
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
  p.then((rec) => { if (rec) _clipRecords.set(key, rec); }).catch(() => {});
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
