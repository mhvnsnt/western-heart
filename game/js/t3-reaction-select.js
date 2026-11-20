/* ============================================================
   WESTERN HEART — t3-reaction-select.js (pure T3 reaction pick)
   Headless-testable: no THREE, no window, no fetch. Implements
   docs/anim/T3-REACTIONS.md "Picking a hit reaction"
   (HitSelectReaction, EXE 0x8002EDF8) over the decoded tables in
   game/assets/anim/t3/reactions.json (PR #1003, lane E: 633
   reaction records x 21 words, 58 close reactions, 6 air kinds).

   WHAT IT DOES: given the attacker's bank row for the move that
   just landed, it picks the defender's reaction RECORD field and
   slot — the same choice T3 makes — WITHOUT loading any clip.
   Clip playback is a separate lane: the packs
   (game/assets/anim/t3/<bank>/reactions.pack.json, ~6.5 MB per
   bank) need a lazy per-fight loader before a slot can play, so
   fighter.js stores the pick on the defender
   (this._reactionSel) and plays a 'react:<slot>' action only
   when such an action exists; today it falls back to the generic
   'hit' clip. This module never claims a clip played.

   Inputs (see the doc for the T3 meaning of each):
   - R: the parsed reactions.json ({ records, close_reactions,
     air_kinds, banks }) — or null, in which case select() is null.
   - row: [reaction, closeIdx, attackClass] from
     R.banks[attackerDir].rows[move.t3row] (or R.common_rows for
     divmot99 rows). Missing row -> null (no decoded reaction).
   - opts: { guarded, crouch, counter, airborne, down, downOther,
     quadrant (0 front, 1 side1, 2 back, 3 side3), close (bool),
     airKind (0-5, default 0; kind 5 comes only from a launch
     branch, never from this pick) }

   Returns null (no reaction: class 1/3, class 2 on an airborne
   or downed defender, zero/throw-range reaction value) or
   { record, field, slot, code, push, angle } where slot is the
   move slot to resolve with reactionClip(V, A, slot) and code is
   the transition (0x23 guard, 0x24 air, 0x25 down, 0x26 counter,
   0x2a front, 0x27 side1, 0x2b back, 0x28 side3).
   ============================================================ */

const RECORD_FIELDS = ['front', 'front_crouch', 'counter', 'counter_crouch',
  'side1', 'side1_crouch', 'side3', 'side3_crouch', 'back', 'back_crouch',
  'guard', 'guard_crouch', 'down', 'down_other',
  'push_angle', 'push_hit', 'unused_angle', 'push_counter', 'push_angle_down',
  'push_down', 'push_guard'];

export function selectReactionSlot(R, row, opts = {}) {
  if (!R || !row) return null;
  const [react, closeIdx, cls] = row;
  const { guarded = false, crouch = false, counter = false,
    airborne = false, down = false, downOther = false,
    quadrant = 0, close = false, airKind = 0 } = opts;
  // MoveStep gate: class 1 and 3 never react; class 2 reacts only
  // on a grounded, standing defender.
  if (cls === 1 || cls === 3 || (cls === 2 && (airborne || down))) return null;
  const cr = (close && closeIdx && R.close_reactions) ? R.close_reactions[closeIdx] : null;
  let v = cr ? (cr[0] & 0xffff) : react;
  if (!v || (v & 0xf000)) return null; // 0x1nnn only acts through a throw
  const r = R.records[v];
  if (!r) return null;
  const c = crouch ? 1 : 0;
  const field = (i) => RECORD_FIELDS[i];
  if (guarded) return { record: v, field: field(10 + c), slot: r[10 + c], code: 0x23, push: r[20], angle: r[14] };
  if (airborne) {
    const kind = (airKind >= 0 && airKind < R.air_kinds.length) ? airKind : 0;
    return { record: v, field: 'air', slot: R.air_kinds[kind][1], code: 0x24, push: null, angle: null };
  }
  if (downOther) return { record: v, field: field(13), slot: r[13], code: 0x25, push: r[19], angle: r[18] };
  if (down) return { record: v, field: field(12), slot: r[12], code: 0x25, push: r[19], angle: r[18] };
  if (counter) return { record: v, field: field(2 + c), slot: r[2 + c], code: 0x26, push: r[17], angle: r[14] };
  const q = [0, 4, 8, 6][quadrant] ?? 0;
  const codes = [0x2a, 0x27, 0x2b, 0x28];
  return { record: v, field: field(q + c), slot: r[q + c], code: codes[quadrant] ?? 0x2a, push: r[15], angle: r[14] };
}

/* Resolve a slot the way the game does (DivmotMergeSharedSlots):
   the defender's bank first, else the attacker's. Returns the
   bank dir that defines the slot, or null. Pack rows themselves
   are resolved by the loader lane, not here. */
export function reactionSlotBank(R, defenderDir, attackerDir, slot) {
  if (!R) return null;
  const k = '0x' + (slot & 0xffff).toString(16);
  for (const d of [defenderDir, attackerDir]) {
    if (d && R.banks[d] && R.banks[d].slots && R.banks[d].slots[k]) return d;
  }
  return null;
}
