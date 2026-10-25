/* ============================================================
   WESTERN HEART — Rage / comeback systems
   Pulled from the Tekken teardowns (T7 base, TTT2, T6):
   • T7 RAGE: activates automatically at <= 25% HP, once per round.
     (T6 also had rage; T7 kept the 25% threshold and replaced the
     passive damage boost with the art/drive comeback tools.)
   • RAGE ART: cinematic armored super. Input 1+2 while raging.
     Armor through startup/active (T7), big damage, knockdown +
     wallsplat, once per round — firing it spends rage.
   • RAGE DRIVE: powered-up strike. Input 3+4 while raging (RD.
     prefix). +damage, wallsplat, spends rage. T7 rule: art OR
     drive per round — one comeback tool, not both.
   • SLOW-MO FINISH: T7's signature — the match-deciding KO blow
     (and any rage-art KO) plays in slow motion.
   Rage art/drive data is SYNTHESIZED per fighter from their own
   real T3 strike data (strongest strike), never hand-authored, so
   every fighter in the roster gets working comeback tools.
   NOTE (loadspeed lane): this module must NOT statically import
   movesets.js (it streams via lazy.js). The Game injects the moveset
   API: ensureRageMoves(fighterId, msApi) with
   msApi = { playedMoveset, getFighterMoveset }.
   ============================================================ */
import { audio } from './audio.js';

export const RAGE_THRESHOLD = 0.25;   // T7: rage at <= 25% HP
export const RAGE_ART_DAMAGE = 32;    // T7 art ~55 on 170 HP -> WH 100 HP scale
export const RAGE_ART_NOTATION = 'R.1+2';
export const RAGE_DRIVE_NOTATION = 'RD.3+4';
export const RAGE_SLOWMO_SCALE = 0.12;
export const RAGE_SLOWMO_TIME = 1.5;  // seconds of real time

/** T7 rage check: alive, <= 25% HP, rage unspent this round. */
export function isRaging(f) {
  return !!f && !f.dead && !f._rageUsed && f.hp > 0 && f.hp <= f.maxHp * RAGE_THRESHOLD;
}

/* Strongest real strike in the moveset (no grabs): returns [key, move]. */
function _strongestStrike(ms, excludeKey = null) {
  let best = null, bestKey = null, bestDmg = -1;
  for (const [key, m] of Object.entries(ms.moves)) {
    if (!m || key === excludeKey) continue;
    if (m.isGrab || m.move_class === 'throw') continue;
    const d = m.damage || 0;
    if (d > bestDmg && (m.move_class === 'strike' || !m.move_class)) { best = m; bestKey = key; bestDmg = d; }
  }
  return [bestKey, best];
}

/* Generic fallback when a fighter has no loaded moveset at all. */
function _fallbackBase() {
  return {
    name: 'HEAVY STRIKE', t3_source: 't7', limb: 'armR',
    startup: 0.3, active: 0.05, recovery: 0.6, damage: 18, knock: 4,
    anim_ref: null, input_slots: [],
  };
}

/**
 * Synthesize + register R.1+2 (rage art) and RD.3+4 (rage drive) for a
 * fighter, built from their own real T3 strike data. Idempotent — safe
 * to call every match. Returns true when the fighter has rage tools.
 */
export function ensureRageMoves(fighterId, msApi) {
  if (!msApi) return false;
  const ms = msApi.playedMoveset(fighterId) || msApi.getFighterMoveset(fighterId);
  if (!ms || !ms.moves) return false;
  const artKey = RAGE_ART_NOTATION, driveKey = RAGE_DRIVE_NOTATION;
  if (ms.moves[artKey] && ms.moves[driveKey]) return true;

  const [artBaseKey, artBase0] = _strongestStrike(ms);
  const artBase = artBase0 || _fallbackBase();
  const plain12 = ms.moves['1+2'];
  const [driveBaseKey, driveBase0] = (plain12 && !plain12.isGrab)
    ? ['1+2', plain12] : _strongestStrike(ms, artBaseKey);
  const driveBase = driveBase0 || artBase;

  if (!ms.moves[artKey]) {
    ms.moves[artKey] = {
      name: `${(artBase.name || 'STRIKE').toUpperCase()} — RAGE ART`,
      input: artKey,
      t3_source: artBase.t3_source, t3_row: artBase.t3_row,
      startup: 0.33, active: 0.06, recovery: 0.95,
      damage: RAGE_ART_DAMAGE, limb: artBase.limb || 'armR',
      heavy: true, knock: 7.5, knockdown: true,
      soulGain: 0, armor: true, rageArt: true,
      hitWord: artBase.hitWord, anim_ref: artBase.anim_ref,
      input_slots: [artKey], move_class: 'strike',
    };
  }
  if (!ms.moves[driveKey]) {
    const bd = driveBase.damage || 15;
    ms.moves[driveKey] = {
      name: `${(driveBase.name || 'STRIKE').toUpperCase()} — RAGE DRIVE`,
      input: driveKey,
      t3_source: driveBase.t3_source, t3_row: driveBase.t3_row,
      startup: Math.max(0.18, (driveBase.startup || 0.3) * 0.85),
      active: driveBase.active || 0.05, recovery: driveBase.recovery || 0.6,
      damage: Math.round(bd * 1.5) + 6, limb: driveBase.limb || 'armR',
      heavy: true, knock: 6.5, knockdown: true,
      soulGain: 0, rageDrive: true,
      hitWord: driveBase.hitWord, anim_ref: driveBase.anim_ref,
      input_slots: [driveKey], move_class: 'strike',
    };
  }
  // register into the notation slots (works even if _prepare already ran)
  if (ms._slots) { ms._slots[artKey] = artKey; ms._slots[driveKey] = driveKey; }
  else {
    ms.slots = ms.slots || {};
    ms.slots[artKey] = artKey; ms.slots[driveKey] = driveKey;
  }
  return true;
}

/* ---------------- per-match rage director ---------------- */
export class RageSystem {
  constructor(game) {
    this.game = game;
    this.slowMoT = 0; // real seconds remaining
  }

  /** Round reset: rage unspent, indicators cleared (T7: fresh rage every round). */
  resetRound() {
    for (const f of [this.game.p1, this.game.p2]) {
      if (!f) continue;
      f._rageUsed = false;
      if (f._rageOn) { f._rageOn = false; f.setRageAura(false); }
    }
    this.slowMoT = 0;
    // Safety net: movesets may finish loading after startMatch.
    try {
      const msApi = this.game._msApi;
      if (msApi) {
        if (this.game.p1) ensureRageMoves(this.game.p1._movesetId || this.game.p1.char.id, msApi);
        if (this.game.p2) ensureRageMoves(this.game.p2._movesetId || this.game.p2.char.id, msApi);
      }
    } catch (e) { /* movesets optional */ }
    const ui = this.game.ui;
    if (ui && ui.setRage) { ui.setRage('p1', false); ui.setRage('p2', false); }
  }

  /** Per fixed-step: announce rage when it starts, clear when it ends. */
  update() {
    const ui = this.game.ui;
    const pairs = [[this.game.p1, 'p1'], [this.game.p2, 'p2']];
    for (const [f, id] of pairs) {
      if (!f) continue;
      const on = isRaging(f);
      if (on && !f._rageOn) {
        f._rageOn = true;
        f.setRageAura(true);
        if (ui && ui.setRage) ui.setRage(id, true);
        if (ui && ui.banner) ui.banner('RAGE');
        try { audio.rage(); } catch (e) { /* audio unlocks on user gesture */ }
      } else if (!on && f._rageOn) {
        f._rageOn = false;
        f.setRageAura(false);
        if (ui && ui.setRage) ui.setRage(id, false);
      }
    }
  }

  /** Would this attacker winning right now decide the match? */
  _decidesMatch(attacker) {
    const g = this.game;
    const need = g.roundsToWin || 2;
    const w1 = g.wins.p1 + (attacker === g.p1 ? 1 : 0);
    const w2 = g.wins.p2 + (attacker === g.p2 ? 1 : 0);
    return w1 >= need || w2 >= need;
  }

  /**
   * Called when a KO blow lands. T7 slow-mo: the match-deciding KO, or
   * any rage-art KO, plays in slow motion. Returns true when slow-mo fired.
   */
  onHitKO(attacker, defender) {
    const art = !!(attacker.attackName && attacker.attackName.indexOf('R.') === 0);
    if (art || this._decidesMatch(attacker)) {
      this.slowMoT = RAGE_SLOWMO_TIME;
      return true;
    }
    return false;
  }

  /** Rage-art connect: hitstop + flash + brief slow-mo (the T7 cinematic beat). */
  rageArtHit(attacker, hb) {
    const g = this.game;
    g._hitStop = Math.max(g._hitStop || 0, 0.3);
    try { g.arena.shake(0.7, 0.5); } catch (e) {}
    this.slowMoT = Math.max(this.slowMoT, 0.55);
    const ui = g.ui;
    if (ui && ui.rageArtFlash) ui.rageArtFlash();
    if (ui && ui.banner) ui.banner('RAGE ART');
  }

  get timeScale() { return this.slowMoT > 0 ? RAGE_SLOWMO_SCALE : 1; }

  /**
   * Apply cinematic slow-mo to one real-time frame slice. Decrements the
   * slow-mo clock in REAL seconds and returns the scaled dt the sim runs.
   */
  slowMoScale(frameDt) {
    if (this.slowMoT > 0) {
      this.slowMoT -= frameDt;
      return frameDt * RAGE_SLOWMO_SCALE;
    }
    return frameDt;
  }
}
