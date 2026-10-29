/* ============================================================
   WESTERN HEART — Reversal Brain
   Split-second reversal decision framework for the CPU fighter.
   Reads the opponent's state and picks the reversal option whose
   frame window is actually open — the Tekken way: you can't sidestep
   a jab that's already active, you block it; you CAN step the slow
   launcher you saw coming.

   This is a pure decision function (no Yuka dependency, no fighter
   handles): decide(snapshot) -> { action, confidence, reason }.
   The AIController executes the action through its existing try*
   calls, gated by confidence so low-reaction AI stays fair.

   Actions: 'throw-break' | 'v-reversal' | 'v-shift' | 'sidestep' |
            'duck' | 'block' | 'punish' | 'none'

   Snapshot contract:
     { myState, foeState, foeAttackPhase,  // 'startup'|'active'|'recovery'|null
       foeStartupFrames,   // estimated startup frames of the incoming attack
       dist, onGround, canAct, meter, stun, inBlockstun,
       lockMove,           // set while caught in a throw
       reaction }          // 0..1 personality stat
   ============================================================ */

export const REVERSAL_ACTIONS = {
  THROW_BREAK: 'throw-break',
  V_REVERSAL: 'v-reversal',
  V_SHIFT: 'v-shift',
  SIDESTEP: 'sidestep',
  DUCK: 'duck',
  BLOCK: 'block',
  PUNISH: 'punish',
  NONE: 'none',
};

/* Frame windows (Tekken-flavored, 60fps): sidestepping needs a slow,
   readable startup; anything faster must be blocked. */
const SIDESTEP_MIN_STARTUP = 15; // frames: slower than this can be stepped
const DUCK_MIN_STARTUP = 10;     // frames: high attacks can be ducked later
const PUNISH_RANGE = 2.4;        // world units: close enough to whiff-punish

export class ReversalBrain {
  constructor(personality = {}) {
    this.reaction = personality.reaction ?? 0.6;
  }

  /**
   * @param {object} snap - fight snapshot (see contract above).
   * @param {function} rand - injectable RNG (tests).
   * @returns {{action:string, confidence:number, reason:string}}
   */
  decide(snap, rand = Math.random) {
    const s = {
      myState: 'idle', foeState: 'idle', foeAttackPhase: null,
      foeStartupFrames: null, dist: 3, onGround: true, canAct: false,
      meter: 0, stun: 0, inBlockstun: false, lockMove: null,
      reaction: this.reaction, ...snap,
    };
    const R = s.reaction;

    // 1) Caught in a throw: read the arm. (AIController's thrown
    //    handler runs first and owns the timing; this is the framework
    //    answer other callers use.)
    if (s.myState === 'thrown' && s.lockMove) {
      const want = String(s.lockMove.throw_break || '1').split('|')[0];
      return {
        action: REVERSAL_ACTIONS.THROW_BREAK,
        confidence: 0.30 + R * 0.55,
        breakInput: want === '1+2' ? '1+2' : want,
        reason: 'thrown: read the arm',
      };
    }

    if (!s.canAct) return { action: REVERSAL_ACTIONS.NONE, confidence: 0, reason: 'cannot act' };

    // 2) Blockstun + meter: V-Reversal is the installed comeback tool.
    if (s.inBlockstun && s.meter >= 50 && rand() < 0.10 + R * 0.10) {
      return {
        action: REVERSAL_ACTIONS.V_REVERSAL,
        confidence: 0.55 + R * 0.40,
        reason: 'blockstun + 50 meter: v-reversal window',
      };
    }

    // 3) Incoming attack: pick the option whose window is open.
    if (s.foeAttackPhase === 'startup' && s.dist < 3.2) {
      const startup = s.foeStartupFrames;
      // Slow, readable startup: step it like a Tekken player.
      if (s.onGround && startup !== null && startup >= SIDESTEP_MIN_STARTUP &&
          rand() < 0.20 + R * 0.45) {
        return {
          action: REVERSAL_ACTIONS.SIDESTEP,
          confidence: 0.45 + R * 0.45,
          reason: `slow startup (~${startup}f): sidestep window open`,
        };
      }
      // Mid-speed high: duck under it.
      if (s.onGround && startup !== null && startup >= DUCK_MIN_STARTUP &&
          rand() < 0.12 + R * 0.30) {
        return {
          action: REVERSAL_ACTIONS.DUCK,
          confidence: 0.40 + R * 0.40,
          reason: `readable startup (~${startup}f): duck window open`,
        };
      }
      // Rare V-Shift read on the hard callout.
      if (s.onGround && rand() < 0.03 + R * 0.05) {
        return {
          action: REVERSAL_ACTIONS.V_SHIFT,
          confidence: 0.60 + R * 0.35,
          reason: 'hard callout: v-shift the incoming attack',
        };
      }
      // Too fast to step: block. This is the honest Tekken answer.
      if (rand() < 0.25 + R * 0.50) {
        return {
          action: REVERSAL_ACTIONS.BLOCK,
          confidence: 0.60 + R * 0.35,
          reason: 'fast startup: block the mixup',
        };
      }
      return { action: REVERSAL_ACTIONS.NONE, confidence: 0, reason: 'reaction failed the read' };
    }

    if (s.foeAttackPhase === 'active' && s.dist < 2.6) {
      // Active frames: only blocking is real. (No parry fantasy.)
      if (rand() < 0.25 + R * 0.50) {
        return {
          action: REVERSAL_ACTIONS.BLOCK,
          confidence: 0.60 + R * 0.35,
          reason: 'attack active: block',
        };
      }
      return { action: REVERSAL_ACTIONS.NONE, confidence: 0, reason: 'too late to react' };
    }

    // 4) Foe whiffed (recovery): hand the punish to the offense brain.
    if (s.foeAttackPhase === 'recovery' && s.dist < PUNISH_RANGE) {
      return {
        action: REVERSAL_ACTIONS.PUNISH,
        confidence: 0.50 + R * 0.45,
        reason: 'foe recovering in range: punish window',
      };
    }

    return { action: REVERSAL_ACTIONS.NONE, confidence: 0, reason: 'no reversal window' };
  }
}
