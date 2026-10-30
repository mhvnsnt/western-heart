/* ============================================================
   WESTERN HEART — Soul Kindle (ki charge)
   Teardown source: Tekken 7 — Ki Charge (1+2+3+4).
   T7 behavior, faithfully ported:
     • Input: all four attack buttons (1+2+3+4) within KINDLE_WINDOW ms.
     • The fighter flashes/glows; the KINDLED state lasts until the next
       landed hit or until KINDLE_DURATION expires.
     • While kindled, the next attack that connects is a GUARANTEED
       counter-hit (T7: "your next hit is a counter hit").
     • While kindled the fighter takes KINDLE_DMG_TAKEN_MULT extra damage
       (T7: 10% more) and CANNOT block during the kindle flash itself.
   WH canon mapping (PROPOSED — needs owner approval):
     "SOUL KINDLE" — the vessel focuses its own soul fragment's nature
     before striking (TOU burns brighter, RIN grows colder...). This is the
     vessel's OWN soul focused, distinct from:
       • SOUL SURGE (canon Nine-Soul Meter): channeling one of the OTHER
         eight souls for ten seconds;
       • SOUL URGE (owner-locked 2026-10-22): Tekken 8 Heat renamed.
     Canon question flagged in docs/research/FIGHTER-DEPTH-CANON-MAPPING.
   ============================================================ */

export const KINDLE_WINDOW_MS = 240;   // all four limbs inside this window
export const KINDLE_DURATION_S = 8;    // kindled state lifetime
export const KINDLE_DMG_TAKEN_MULT = 1.10; // T7: +10% damage taken while kindled
export const KINDLE_FLASH_S = 0.45;    // vulnerable flash (cannot block)

/* Scan a consumed input queue (array of action strings from InputManager)
   for a 1+2+3+4 kindle press. Returns true when all four limbs appear
   within KINDLE_WINDOW_MS. Pure — unit-testable. */
export function detectKindlePress(queue, nowMs = (typeof performance !== 'undefined' ? performance.now() : Date.now())) {
  if (!queue || !queue.length) return false;
  const limbs = new Set();
  // queue entries may be plain action strings
  for (const a of queue) {
    const s = String(a);
    if (s === '1' || s === '2' || s === '3' || s === '4') limbs.add(s);
    // chords count their limbs too (1+2 covers 1 and 2)
    if (/^[1-4](\+[1-4])+$/.test(s)) for (const c of s.split('+')) limbs.add(c); // 3- and 4-limb chords too
  }
  return limbs.size === 4;
}

/* Per-fighter kindle state. Attach one per Fighter (fighter.kindle). */
export class SoulKindle {
  constructor() { this.reset(); }
  reset() {
    this.active = false;      // kindled: next landed hit is a guaranteed CH
    this.t = 0;               // time left in kindled state
    this.flash = 0;           // kindle-flash vulnerability timer (cannot block)
    this.kindlesUsed = 0;
  }
  /* Attempt to start a kindle. Returns 'kindled' | 'busy' | 'denied'. */
  tryKindle(fighter) {
    if (this.active || this.flash > 0) return 'busy';
    if (!fighter.canAct || !fighter.canAct()) return 'denied';
    this.active = true;
    this.t = KINDLE_DURATION_S;
    this.flash = KINDLE_FLASH_S;
    this.kindlesUsed++;
    if (fighter._enter) fighter._enter('kindle');
    return 'kindled';
  }
  /* Per-frame (dt seconds). Returns events for the presentation layer. */
  update(dt) {
    const ev = [];
    if (this.flash > 0) { this.flash = Math.max(0, this.flash - dt); if (this.flash === 0) ev.push('flash-end'); }
    if (this.active) {
      this.t -= dt;
      if (this.t <= 0) { this.active = false; ev.push('expired'); }
    }
    return ev;
  }
  /* Called when THIS fighter lands a hit. Consumes kindle -> force CH. */
  consumeOnHitLanded() {
    if (!this.active) return false;
    this.active = false; this.t = 0;
    return true; // caller upgrades the hit to a counter-hit
  }
  /* Damage-taken multiplier while kindled (T7: +10%). */
  damageTakenMult() { return this.active ? KINDLE_DMG_TAKEN_MULT : 1; }
  /* T7: cannot block during the kindle flash. */
  canBlock() { return this.flash <= 0; }
  /* Presentation state for the renderer: 0..1 glow pulse. */
  glowPhase(nowS) { return this.active ? (0.5 + 0.5 * Math.sin(nowS * 14)) : 0; }
}

/* Wire helper: call each frame for a fighter with its consumed queue.
   Returns 'kindled' when a kindle started (for sfx/overlay). */
export function updateKindle(fighter, pressedQueue, dt) {
  if (!fighter.kindle) fighter.kindle = new SoulKindle();
  if (pressedQueue && pressedQueue.length && detectKindlePress(pressedQueue)) {
    const r = fighter.kindle.tryKindle(fighter);
    if (r === 'kindled') return 'kindled';
  }
  fighter.kindle.update(dt);
  return null;
}
