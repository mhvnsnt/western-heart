/* ============================================================
   WESTERN HEART — t3-throw.js (Tekken throw-pair selection)
   Pure T3 throw wiring: no THREE, no window, no fetch at import
   time, so node can test it headlessly. Implements
   docs/anim/T3-REACTIONS.md "Throws" + "Shared root frame"
   over the decoded tables in game/assets/anim/t3/reactions.json
   (R.banks[<dir>].throws / throw_attempts / throw_inputs) and
   the baked clips in game/assets/anim/t3/<bank>/reactions.pack.json.

   TEKKEN GRAPPLE STATE MACHINE (owner directive 2026-10-24):
     attempt  -> the throw ATTEMPT row clip plays, whether it
                 connects or not (whiff or hit — the reach always
                 plays; it is the move's own clip, picked by
                 fighter.js _attackClipPlan, never a generic clip).
     connect  -> AUTOMATICALLY, with no further button press, the
                 file's throw pair plays: the thrower's slot clip
                 plus the victim's paired slot clip, in sync, on
                 the shared root frame anchored at the victim.
     whiff    -> the attempt ends and the fighter returns to
                 neutral. No throw execution, no receiver clip.
     break    -> inside the file's break window (the first frames
                 of the same two clips — there is NO separate lock
                 in T3), the victim's break input starts the file's
                 escape pair, roles swapped. Outside the window the
                 throw lands at the file's damage_frames.

   NOTHING HERE IS GUESSED. Every pairing, window and damage
   frame comes from reactions.json / the pack row. When the file
   has no wiring for a throw (no attempt row, no branch matching
   the situation, no throw entry, or no baked clip for a slot),
   selection returns null with a reason and the caller keeps the
   legacy lock behaviour — the throw is UNMAPPED, never paired
   by invention. Command throws whose WH move carries no T3
   attempt row are UNMAPPED by this rule, not translated from
   WH notation to a T3 command string.

   Damage AMOUNT is deliberately NOT taken from the file: the
   throw is a WH move with a WH damage value (MOD damage
   decision, 2026-10-24). Only the file's damage TIMING
   (damage_frames) is used. Escape pairs are not WH moves, so
   they use the file damage scaled T3 170 HP -> WH 100 HP, the
   same scaling fighter.js documents for T3 frame data.
   ============================================================ */

/** Slot number -> reactions.pack.json row key. */
export function hexSlot(slot) { return '0x' + Number(slot).toString(16); }

/** T3 break input -> Tekken button label used across the UI. */
export const BREAK_LABEL = { '1': 'LP1', '2': 'RP2', '1+2': 'LP1+RP2' };

/* Situation codes (T3-REACTIONS.md "Choosing the throw", step 3).
   quadrant: 0 front, 1 side1 (defender's +X side), 2 back,
   3 side3 (defender's -X side) — the same quadrant convention
   fighter.js _pickReaction already uses. posture is the victim's:
   'standing' | 'crouching' | 'lying' | 'lyingOther'. When the
   thrower's own back is turned (relAngle > 120 deg) the codes
   are 18/19 instead; WH has no back-turned stance state, so
   attackerBackTurned is normally false and is carried only so
   the rule is complete, not approximated away. */
export function situationCode(posture, quadrant, attackerBackTurned = false) {
  if (attackerBackTurned) return quadrant === 2 ? 19 : 18;
  const table = {
    standing: [2, 4, 3, 5],
    crouching: [6, 8, 7, 9],
    lying: [10, 12, 11, 13],
    lyingOther: [14, 16, 15, 17],
  };
  const row = table[posture];
  if (!row || quadrant == null || quadrant < 0 || quadrant > 3) return null;
  return row[quadrant];
}

/* Does a branch condition accept a situation code? Exact match,
   plus the 0x14-0x17 aliases that accept the standing OR the
   crouching code of the same quadrant (doc step 3). */
export function branchAccepts(cond, code) {
  if (cond === code) return true;
  const alias = { 20: [2, 6], 21: [3, 7], 22: [4, 8], 23: [5, 9] };
  return !!(alias[cond] && alias[cond].includes(code));
}

/* WH quadrant, same convention as fighter.js _pickReaction:
   attacker ahead of the victim's facing = front, behind = back,
   otherwise the world-z side. WH fights are x-axis fights with
   transient z separation after a sidestep, so a z-dominant
   offset is the only side signal available; this is a documented
   WH approximation of T3's 3D quadrant, not a file value. */
export function throwQuadrant(attackerPos, victimPos, victimFacing) {
  const dx = attackerPos.x - victimPos.x;
  const dz = attackerPos.z - victimPos.z;
  if (Math.abs(dz) > Math.abs(dx)) return dz > 0 ? 1 : 3;
  return dx * victimFacing > 0 ? 0 : 2;
}

/* Bank folder name for a reactions.json banks key, from a
   t3anims.js T3_BANKS base path (e.g. 'assets/anim/t3/king_on_pantera_leoman/'). */
export function bankDirOf(base) {
  return base ? String(base).split('/').filter(Boolean).pop() : null;
}

/**
 * Select the file's throw for one attempt.
 * R: parsed reactions.json. attackerDir / victimDir: banks keys.
 * attemptRow: the attempt move's bank row (from the attempt
 * clip plan's 'row:<n>' name, or from throw_inputs — see
 * attemptRowForInput below). opts: { posture, quadrant,
 * distanceM, anchorScale, attackerBackTurned }.
 * distanceM is the WH fighter separation in metres; param is
 * in T3 units and anchorScale (the pack's anchor_mm_to_rig_m)
 * converts T3 units to metres, the same conversion the doc
 * uses for close-reaction distances.
 * Returns { throw, branch, code } or { throw: null, reason }.
 * Branches are walked in BranchFind order; the first branch
 * whose situation matches AND whose distance is <= param wins.
 */
export function selectThrow(R, attackerDir, attemptRow, opts = {}) {
  if (!R || !R.banks || !attackerDir) return { throw: null, reason: 'no reactions tables loaded' };
  const bank = R.banks[attackerDir];
  if (!bank) return { throw: null, reason: `no reactions bank for '${attackerDir}' (UNMAPPED)` };
  if (attemptRow == null) return { throw: null, reason: 'no T3 attempt row for this throw (UNMAPPED)' };
  const attempts = bank.throw_attempts && bank.throw_attempts[String(attemptRow)];
  if (!attempts || !attempts.branches) {
    return { throw: null, reason: `attempt row ${attemptRow} has no throw branches in bank '${attackerDir}' (UNMAPPED)` };
  }
  const code = situationCode(opts.posture || 'standing', opts.quadrant ?? 0, !!opts.attackerBackTurned);
  if (code == null) return { throw: null, reason: `unknown situation posture=${opts.posture} quadrant=${opts.quadrant}` };
  const k = opts.anchorScale || 0;
  for (const branch of attempts.branches) {
    if (!branchAccepts(branch.cond, code)) continue;
    if (k > 0 && opts.distanceM != null && branch.param != null && opts.distanceM > branch.param * k) continue;
    const entry = (bank.throws || []).find((t) => t.slot === branch.throw_slot);
    if (!entry) continue;
    return { throw: entry, branch, code };
  }
  return { throw: null, reason: `no branch matches situation ${code} at this distance (UNMAPPED for this situation)` };
}

/**
 * Attempt row for a WH throw input, from the file's own
 * throw_inputs table (stance slot 3 = standing, 40 = crouching;
 * cond 36 = thrower's back turned). input is a Tekken chord:
 * '1+3' (LP1+LK3) or '2+4' (RP2+RK4). Returns the attempt row
 * or null — never a translated command string.
 */
export function attemptRowForInput(R, attackerDir, input, crouching = false, backTurned = false) {
  const bank = R && R.banks && R.banks[attackerDir];
  if (!bank || !bank.throw_inputs) return null;
  const want = input === '1+3' ? 'LP+LK' : input === '2+4' ? 'RP+RK' : null;
  if (!want) return null;
  const stance = crouching ? 40 : 3;
  const cond = backTurned ? 36 : 0;
  // EXACT command match only: '1+LP+LK' (a down-back variant) also
  // contains 'LP+LK' as a substring, but it is a different attempt
  // (row 277, a crouching throw) from the neutral LP+LK (row 273).
  // A substring match here would wire the wrong attempt.
  const hit = bank.throw_inputs.find((t) => t.command === want
    && t.stance_slot === stance && t.cond === cond);
  return hit ? hit.attempt_row : null;
}

/**
 * Resolve which banks' packs hold the two clips of a throw
 * (DivmotMergeSharedSlots, doc "Choosing the throw" step 4).
 * Returns { throwerBank, throwerSlot, victimBank, victimSlot,
 * defined, note }. victimBank is the victim's own bank when it
 * defines the victim slot, else the thrower's bank (the victim
 * move defined only in the thrower's bank). When
 * defined === false (Forest Law's standard throws) the thrower
 * clip itself comes from the victim bank's throw of the same
 * slot, and the victim clip from that throw's victim slot.
 */
export function resolveThrowClips(R, entry, attackerDir, victimDir) {
  if (!entry) return null;
  const hex = (s) => hexSlot(s);
  const defines = (dir, slot) => !!(R.banks[dir] && R.banks[dir].slots && R.banks[dir].slots[hex(slot)]);
  if (entry.defined === false) {
    const tv = R.banks[victimDir] && (R.banks[victimDir].throws || []).find((t) => t.slot === entry.slot);
    if (!tv) return { throwerBank: null, throwerSlot: entry.slot, victimBank: null, victimSlot: null, defined: false, note: 'undefined throw has no victim-bank twin (UNMAPPED)' };
    return { throwerBank: victimDir, throwerSlot: entry.slot, victimBank: victimDir, victimSlot: tv.victim_slot, defined: false,
      note: 'thrower clip from victim bank (defined === false)' };
  }
  const victimBank = defines(victimDir, entry.victim_slot) ? victimDir : attackerDir;
  return { throwerBank: attackerDir, throwerSlot: entry.slot, victimBank, victimSlot: entry.victim_slot, defined: true,
    note: entry.victim_in_thrower_bank === false && victimBank !== victimDir ? 'victim clip from thrower bank' : 'victim clip from victim bank' };
}

/** Break windows of a throw, in seconds (60 fps frames / 60). */
export function throwBreaks(entry) {
  return (entry && entry.breaks || []).map((b) => ({
    input: b.input,
    label: BREAK_LABEL[b.input] || b.input,
    windowSec: [b.window[0] / 60, b.window[1] / 60],
    escapeSlot: b.escape_slot,
  }));
}

/** First damage frame of a throw, in seconds (60 fps / 60). */
export function throwDamageTimeSec(entry) {
  const f = entry && entry.damage_frames && entry.damage_frames[0];
  return f != null ? f / 60 : null;
}

/** Duration of a throw pair's clips, in seconds (longer stream). */
export function throwPairDurationSec(entry) {
  const a = entry && entry.frames ? entry.frames / 60 : 0;
  const b = entry && entry.victim_frames ? entry.victim_frames / 60 : 0;
  return Math.max(a, b);
}

/**
 * The escape pair for a broken throw (doc "When the victim
 * breaks"): the victim starts escape_slot as a new throw pair
 * and becomes the thrower; the original thrower plays that
 * escape's victim move. Returns null when the file names no
 * escape throw for the slot.
 */
export function escapePairFor(R, entry, breaks, attackerDir, victimDir) {
  const brk = breaks && breaks[0];
  if (!entry || !brk || brk.escapeSlot == null) return null;
  const escape = (R.banks[attackerDir] && R.banks[attackerDir].throws || []).find((t) => t.slot === brk.escapeSlot);
  if (!escape) return null;
  // Roles swap: original victim is the new thrower, original
  // attacker the new victim. The escape throw lives in the
  // original attacker's bank, so its clips resolve with the
  // banks swapped the same way.
  const clips = resolveThrowClips(R, escape, victimDir, attackerDir);
  return { throw: escape, clips, newThrowerDir: victimDir, newVictimDir: attackerDir };
}

/* ---- pack anchor decoding (same int16 base64 as t3anims.js
   decodePackRow; ax/ay/az are the decoded root channels in mm
   in the move's heading frame, per the pack schema) ---- */
function b64i16(str) {
  if (!str) return [];
  const bin = typeof atob !== 'undefined' ? atob(str) : Buffer.from(str, 'base64').toString('binary');
  const out = new Int16Array(bin.length >> 1);
  for (let i = 0; i < out.length; i++) {
    const v = bin.charCodeAt(2 * i) | (bin.charCodeAt(2 * i + 1) << 8);
    out[i] = v >= 0x8000 ? v - 0x10000 : v;
  }
  return out;
}

/** Anchor (root) offset of a pack row at frame f, in mm. */
export function anchorAt(packRow, f) {
  if (!packRow) return { ax: 0, ay: 0, az: 0 };
  const ax = b64i16(packRow.ax), ay = b64i16(packRow.ay), az = b64i16(packRow.az);
  const i = Math.max(0, Math.min(f, (ax.length || 1) - 1));
  return { ax: ax[i] || 0, ay: ay[i] || 0, az: az[i] || 0 };
}

/**
 * Shared-root-frame world position (doc formula): P is the
 * anchor fighter's root (x, z); H_yaw = -victim.facing * PI/2;
 * k is the thrower's pack anchor_mm_to_rig_m, used for both
 * clips so contact geometry is preserved.
 */
export function sharedFramePos(P, hYaw, anchorMm, k) {
  const c = Math.cos(hYaw), s = Math.sin(hYaw);
  return {
    x: P.x + (c * anchorMm.ax + s * anchorMm.az) * k,
    z: P.z + (-s * anchorMm.ax + c * anchorMm.az) * k,
  };
}

/* ---- loaders (browser fetch; cached; never throw) ---- */
let _tablesPromise = null;
/** Parsed reactions.json, shared on globalThis like _pickReaction reads. */
export async function loadThrowTables(fetchFn) {
  if (typeof globalThis !== 'undefined' && globalThis.WH_T3_REACTIONS) return globalThis.WH_T3_REACTIONS;
  const f = fetchFn || (typeof fetch !== 'undefined' ? fetch : null);
  if (!f) return null;
  if (!_tablesPromise) {
    _tablesPromise = (async () => {
      try {
        const res = await f('assets/anim/t3/reactions.json');
        if (!res.ok) return null;
        const R = await res.json();
        if (typeof globalThis !== 'undefined') globalThis.WH_T3_REACTIONS = R;
        return R;
      } catch (e) { return null; }
    })();
  }
  return _tablesPromise;
}
