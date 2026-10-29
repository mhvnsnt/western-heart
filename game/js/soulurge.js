/* ============================================================
   WESTERN HEART — Soul Urge (Tekken 8 Heat, proprietary rename)
   USER-LOCKED NAME 2026-10-22: "Soul Urge" is the official name —
   use it everywhere (UI, docs, code, comments).
   Pulled straight from the T8 files:
   • teardown/tekken7/tekkenmods-docs/.../Tekken_8/.../Move (Heat
     Smash as a move category) and Hit_Conditions (Heat Engager hit
     conditions, Heat Dash conditions).
   T8 HEAT -> SOUL URGE rename table:
     Heat            -> Soul Urge (the state)
     Heat Bar        -> Urge gauge (per-round, under the health bar)
     Heat Burst      -> Urge Burst      (input 2+3, armored smash)
     Heat Engager    -> Urge Engager    (fighter's launcher, on hit)
     Heat Smash      -> Urge Smash      (input 2+3 during Urge)
     Heat Dash       -> Urge Dash       (input 1+2 during Urge, 1 pip)
     Heat Energy pip -> Urge pip
   T8 rules implemented:
   • Once per round; gauge refreshes every round.
   • Urge Burst (2+3): armored smash, activates on hit OR block
     (T8), grants 1 urge pip, 10 s of Soul Urge.
   • Urge Engager: the fighter's own launcher-class strike — on HIT
     only (T8) it auto-triggers Soul Urge with 2 pips, 15 s, plus a
     small heal and dash-in (T8 engager behavior).
   • During Soul Urge: every blocked attack deals chip damage that
     can never kill (T8); the timer pauses while the opponent is
     hit/grounded (T8); the fighter burns with soul-flame aura.
   • Urge Dash (1+2 while urging, not raging): spends 1 pip for a
     fast dash-in cancel (T8 Heat Dash). Rage art keeps priority on
     1+2 while raging.
   • Urge Smash (2+3 during Soul Urge): big cinematic hit that
     spends ALL remaining pips and ends Soul Urge (T8 Heat Smash).
   NOTE (loadspeed lane): this module must NOT statically import
   movesets.js (it streams via lazy.js). The Game injects the moveset
   API: ensureUrgeMoves(fighterId, msApi) with
   msApi = { playedMoveset, getFighterMoveset }.
   ============================================================ */
import { audio } from './audio.js';

export const URGE_BURST_TIME = 10;    // T8: 10 s from a burst
export const URGE_ENGAGER_TIME = 15;  // T8: 15 s from an engager
export const URGE_BURST_NOTATION = 'UB.2+3';
export const URGE_SMASH_NOTATION = 'US.2+3';
export const URGE_DASH_PIPS = 1;
export const URGE_SMASH_DAMAGE = 30;

/* The fighter's launcher-class strike becomes their Urge Engager
   (T8: every character has their own engager moves). Highest knock,
   non-grab strike — synthesized rage/urge moves are never eligible. */
function _engagerKey(ms) {
  let best = null, bestKnock = -1;
  for (const [key, m] of Object.entries(ms.moves)) {
    if (!m || m.isGrab || m.move_class === 'throw') continue;
    if (/^(R\.|RD\.|UB\.|US\.)/.test(key)) continue; // synthesized, not a real move
    const k = m.knock || 0;
    if (k > bestKnock && (m.damage || 0) > 0) { best = key; bestKnock = k; }
  }
  return best;
}

/**
 * Synthesize + register UB.2+3 (Urge Burst) and US.2+3 (Urge Smash),
 * and flag the fighter's launcher as their Urge Engager. Idempotent.
 */
export function ensureUrgeMoves(fighterId, msApi) {
  if (!msApi) return false;
  const ms = msApi.playedMoveset(fighterId) || msApi.getFighterMoveset(fighterId);
  if (!ms || !ms.moves) return false;
  const bKey = URGE_BURST_NOTATION, sKey = URGE_SMASH_NOTATION;
  if (!ms.moves[bKey]) {
    ms.moves[bKey] = {
      name: 'URGE BURST', input: bKey,
      startup: 0.3, active: 0.06, recovery: 0.7,
      damage: 14, limb: 'armR', heavy: true,
      knock: 5.5, knockdown: true, armor: true, urgeBurst: true,
      soulGain: 0, input_slots: [bKey], move_class: 'strike',
    };
  }
  if (!ms.moves[sKey]) {
    ms.moves[sKey] = {
      name: 'URGE SMASH', input: sKey,
      startup: 0.38, active: 0.06, recovery: 0.95,
      damage: URGE_SMASH_DAMAGE, limb: 'armR', heavy: true,
      knock: 8, knockdown: true, armor: true, urgeSmash: true,
      soulGain: 0, input_slots: [sKey], move_class: 'strike',
    };
  }
  if (ms._slots) { ms._slots[bKey] = bKey; ms._slots[sKey] = sKey; }
  else {
    // slotless moveset: seed from the notation-keyed moves (see rage.js)
    ms.slots = ms.slots || Object.fromEntries(Object.keys(ms.moves).map(k => [k, k]));
    ms.slots[bKey] = bKey; ms.slots[sKey] = sKey;
  }
  // flag the engager (once). GAP-FILL LANE 1: if the moveset
  // data already flags an Engager (per-character T8 lists, when
  // the moveset lane authors them), respect it — do NOT crown a
  // second, synthesized engager on top of the data one. The
  // strongest-knock synthesis below is only the fallback for
  // movesets with no data-flagged engager at all.
  // COMBAT SYSTEMS 2026-10-24: per-character engager LISTS. A
  // moveset may declare urgeEngagers: [...] (T8: characters have
  // several engager moves). Every listed existing non-grab,
  // non-synthesized move is flagged; the list wins over the
  // single-key fallback, which stays for movesets without one.
  if (Array.isArray(ms.urgeEngagers) && ms.urgeEngagers.length) {
    const keys = [];
    for (const key of ms.urgeEngagers) {
      const m = ms.moves[key];
      if (m && !m.isGrab && m.move_class !== 'throw' && !/^(R\.|RD\.|UB\.|US\.)/.test(key)) {
        m.urgeEngager = true; keys.push(key);
      }
    }
    if (keys.length) { ms._urgeEngagerKeys = keys; ms._urgeEngagerKey = keys[0]; }
  }
  if (!ms._urgeEngagerKey) {
    let ek = null;
    for (const [key, m] of Object.entries(ms.moves)) {
      if (m && m.urgeEngager && !/^(R\.|RD\.|UB\.|US\.)/.test(key)) { ek = key; break; }
    }
    if (!ek) ek = _engagerKey(ms);
    if (ek && ms.moves[ek]) { ms.moves[ek].urgeEngager = true; ms._urgeEngagerKey = ek; }
  }
  return true;
}

/* Engager keys for a moveset: the declared list when present,
   else the single key, else any data-flagged engager move. */
export function listUrgeEngagers(ms) {
  if (!ms) return [];
  if (Array.isArray(ms._urgeEngagerKeys) && ms._urgeEngagerKeys.length) return [...ms._urgeEngagerKeys];
  if (ms._urgeEngagerKey) return [ms._urgeEngagerKey];
  return Object.entries(ms.moves || {})
    .filter(([k, m]) => m && m.urgeEngager && !/^(R\.|RD\.|UB\.|US\.)/.test(k))
    .map(([k]) => k);
}

/* ---------------- per-match Soul Urge director ---------------- */
export class SoulUrge {
  constructor(game) {
    this.game = game;
  }

  /** Round reset: fresh urge gauge every round (T8). */
  resetRound() {
    for (const f of [this.game.p1, this.game.p2]) {
      if (!f) continue;
      f._urgeUsed = false; f._urgeOn = false; f._urgePips = 0; f._urgeT = 0;
      if (f.setUrgeAura) f.setUrgeAura(false);
      // GAP-FILL LANE 1: the per-round combat state that lives
      // on the fighter is reset here, through this existing
      // per-round director hook (game.js calls resetRound every
      // round; fighter.js has no round-reset method of its own).
      // Recoverable pool is per-round in T8; the extender slot
      // and wall-splat count never carry across rounds either.
      f._recoverable = 0;
      f._extenderUsed = false; f._extenderKind = null;
      f._inScrew = false; f._inTornado = false;
      f._wallSplatHits = 0; f._wallSplatArmed = false;
    }
    // Safety net: movesets may finish loading after startMatch.
    try {
      const msApi = this.game._msApi;
      if (msApi) {
        if (this.game.p1) ensureUrgeMoves(this.game.p1._movesetId || this.game.p1.char.id, msApi);
        if (this.game.p2) ensureUrgeMoves(this.game.p2._movesetId || this.game.p2.char.id, msApi);
      }
    } catch (e) { /* movesets optional */ }
    const ui = this.game.ui;
    if (ui && ui.setUrge) { ui.setUrge('p1', false); ui.setUrge('p2', false); }
  }

  _idOf(f) { return this.game.p1 === f ? 'p1' : 'p2'; }

  /** Called when the attacker lands a hit. Burst/engager/smash triggers. */
  onHit(attacker, move) {
    if (!move) return;
    const id = this._idOf(attacker);
    if (move.urgeBurst) {
      // Urge Burst connects: enter Soul Urge (T8: activates on hit OR block).
      this.activate(attacker, id, 1, URGE_BURST_TIME);
    } else if (move.urgeSmash) {
      // Urge Smash connects: cinematic beat, spends everything, ends Urge.
      this.urgeSmashHit(attacker);
      this.spendAll(attacker, id);
    } else if (move.urgeEngager && !attacker._urgeUsed && !attacker._urgeOn) {
      // Urge Engager lands (hit only, T8): 2 pips, 15 s, small heal, dash-in.
      attacker.hp = Math.min(attacker.maxHp, attacker.hp + 10);
      attacker.vx = attacker.facing * 4;
      this.activate(attacker, id, 2, URGE_ENGAGER_TIME);
    }
  }

  /** Called when the attacker's move is blocked. Burst activates on block (T8). */
  onBlockedHit(attacker, move) {
    if (move && move.urgeBurst) {
      this.activate(attacker, this._idOf(attacker), 1, URGE_BURST_TIME);
    }
  }

  /** Spend one urge pip (Urge Dash). */
  spendPip(f) {
    if (!f) return;
    f._urgePips = Math.max(0, (f._urgePips || 0) - 1);
  }

  /** Per fixed-step: tick the urge timer (pauses while the opponent
      is hit or grounded — T8), expire at zero. */
  update(dt) {
    const g = this.game;
    const pairs = [[g.p1, g.p2, 'p1'], [g.p2, g.p1, 'p2']];
    for (const [f, opp, id] of pairs) {
      if (!f || !f._urgeOn) continue;
      const paused = opp && (
        opp.state === 'hitstun' || opp.state === 'knockdown' ||
        opp.state === 'thrown' || !opp.onGround);
      if (!paused) f._urgeT -= dt;
      if (f._urgeT <= 0) this._expire(f, id);
    }
    const ui = g.ui;
    if (ui && ui.updateUrge && g.p1 && g.p2) ui.updateUrge(g.p1, g.p2);
  }

  /** Enter Soul Urge (burst = 1 pip / 10 s, engager = 2 pips / 15 s). */
  activate(f, id, pips, time) {
    if (!f || f._urgeUsed || f._urgeOn) return false;
    f._urgeUsed = true; f._urgeOn = true;
    f._urgePips = pips; f._urgeT = time; f._urgeMaxT = time;
    if (f.setUrgeAura) f.setUrgeAura(true);
    const ui = this.game.ui;
    if (ui && ui.setUrge) ui.setUrge(id, true);
    try { audio.urge(); } catch (e) { /* audio unlocks on user gesture */ }
    return true;
  }

  _expire(f, id) {
    f._urgeOn = false; f._urgePips = 0; f._urgeT = 0;
    if (f.setUrgeAura) f.setUrgeAura(false);
    const ui = this.game.ui;
    if (ui && ui.setUrge) ui.setUrge(id, false);
  }

  /** Urge Smash spends everything and ends Soul Urge (T8). */
  spendAll(f, id) {
    if (!f || !f._urgeOn) return;
    this._expire(f, id);
  }

  /** Urge Smash connect: hitstop + flash (the T8 beat). No center text — Tekken shows Heat Smash via the cinematic hit itself. */
  urgeSmashHit(attacker, hb) {
    const g = this.game;
    g._hitStop = Math.max(g._hitStop || 0, 0.28);
    try { g.arena.shake(0.65, 0.5); } catch (e) {}
    const ui = g.ui;
    if (ui && ui.rageArtFlash) ui.rageArtFlash();
  }
}
