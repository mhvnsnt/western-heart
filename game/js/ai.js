/* ============================================================
   WESTERN HEART — AI Controller
   Utility/behaviour driver for the CPU fighter. Reads distance,
   the player's current action and its own Nine-Soul Meter.

   Personalities come from the character entry (char.ai):
     • PANTERA  — aggressive, closes distance, hunts command grabs.
     • DEMONIO  — balanced, fundamental spacing, whiff-aware.
   ============================================================ */
export class AIController {
  constructor(fighter, personality = {}) {
    this.f = fighter;
    this.aggression = personality.aggression ?? 0.6;
    this.grabBias = personality.grabBias ?? 0.1;
    this.reaction = personality.reaction ?? 0.6;
    this._think = 0;
    this._action = 'neutral';
    this._actionT = 0;
    this._block = 0;
    this.passive = !!personality.passive; // modes lane: training dummy never acts
  }

  update(dt, player) {
    const f = this.f, p = player;
    if (f.dead || f.state === 'ko' || f.state === 'victory') return;
    if (this.passive) return; // training dummy: stands, takes hits, never fights back

    this._think -= dt;
    this._actionT -= dt;

    const dx = p.root.position.x - f.root.position.x;
    const dist = Math.abs(dx);
    const dir = Math.sign(dx) || 1;
    const playerAttacking = p.state === 'attack' && p._attackPhase !== 'recovery';

    // Stream 6: caught in a throw — attempt the break (gated by reaction).
    // The AI "reads the arm" after a reaction delay, like a human would.
    if (f.state === 'thrown' && f.lockMove) {
      if (this._breakT === undefined) {
        // reaction delay: better AI reads the arm faster
        this._breakT = 0.08 + (1 - this.reaction) * 0.18;
        this._breakWill = Math.random() < (0.3 + this.reaction * 0.55);
      }
      this._breakT -= dt;
      if (this._breakT <= 0) {
        const want = f.lockMove.throw_break || '1';
        if (this._breakWill) f.tryThrowBreak(want === '1+2' ? '1+2' : want);
        else f.tryThrowBreak(want === '1' ? '2' : '1'); // wrong read
        this._breakT = undefined;
      }
      return;
    }
    this._breakT = undefined;

    // V-System (owner 2026-10-22): V-Trigger when the gauge is full
    // (comeback install), V-Reversal out of blockstun (gated by reaction).
    if (f.meter >= 100 && f.canAct() && f.onGround && Math.random() < 0.03) f.tryVTrigger();
    if (f.state === 'block' && f.stun > 0.05 && f.meter >= 50 &&
        Math.random() < 0.10 + this.reaction * 0.1) {
      f.tryVReversal(); this._think = 0.3; return;
    }

    // Reactive defense: block/dodge/sidestep incoming attacks (gated by reaction stat)
    if (playerAttacking && dist < 2.6 && f.canAct()) {
      const react = Math.random() < (0.25 + this.reaction * 0.5);
      if (react) {
        const r = Math.random();
        // V-System: V-Shift the incoming attack (reads like an SFV player).
        if (r < 0.08 && f.onGround) {
          f.tryVShift();
          this._think = 0.5; return;
        }
        // Stream 6: sidestep the linear attack (reads like a Tekken player).
        if (r < 0.28 && f.onGround) {
          f.trySidestep(Math.random() < 0.5 ? -1 : 1);
          this._think = 0.5; return;
        }
        if (r < 0.54 && f.onGround) { f.tryDodge(); this._think = 0.4; return; }
        f.tryBlock(true); this._block = 0.35; this._think = 0.25; return;
      }
    }

    // Release block once the threat passes
    if (f.isBlocking()) {
      this._block -= dt;
      if (this._block <= 0 || !playerAttacking) f.tryBlock(false);
      else return;
    }

    if (this._think > 0) {
      if (this._action === 'approach') f.tryMove(dir);
      else if (this._action === 'retreat') f.tryMove(-dir);
      return;
    }

    // ----- Decide a new action -----
    this._think = 0.12 + (1 - this.aggression) * 0.4 + Math.random() * 0.2;

    // Soul Surge when the meter is full and in range
    if (f.meter >= 100 && dist < 2.8 && Math.random() < 0.6) {
      f.tryAttack('surge'); return;
    }

    // Rage lane (T7 comeback): while raging, spend it on the rage art
    // (1+2) or rage drive (3+4) when in range — never hold it forever.
    if (f._rageOn && f.onGround && dist < 3.4) {
      const rr = Math.random();
      if (rr < 0.4) { f.tryAttack('1+2'); return; }  // RAGE ART
      if (rr < 0.55) { f.tryAttack('3+4'); return; } // RAGE DRIVE
    }

    // Soul Urge lane (T8 Heat): pop the Urge Burst in range; while
    // urging, dash in with spare pips or cash out with the Urge Smash.
    if (!f._urgeUsed && !f._urgeOn && f.onGround && dist < 2.6 && Math.random() < 0.3) {
      f.tryAttack('2+3'); return; // URGE BURST
    }
    if (f._urgeOn && f.onGround) {
      if (f._urgePips > 0 && dist > 3 && dist < 7 && Math.random() < 0.4) {
        f.tryAttack('1+2'); return; // URGE DASH (1+2 while urging, not raging)
      }
      if (dist < 2.8 && Math.random() < 0.22) {
        f.tryAttack('2+3'); return; // URGE SMASH
      }
    }

    // Command grab when chest-to-chest (grapplers live for this)
    if (dist < 1.9 && f.onGround && Math.random() < this.grabBias) {
      f.tryAttack('grab'); return;
    }

    if (dist > 3.2) {
      this._action = 'approach';
      if (Math.random() < 0.12 && f.onGround) f.tryJump();
      f.tryMove(dir);
    } else if (dist < 1.4) {
      if (Math.random() < 0.2 - this.aggression * 0.1) { this._action = 'retreat'; f.tryMove(-dir); }
      // Stream 6: full Tekken limbs (1/2/3/4) so the AI uses expanded movelists.
      else { this._action = 'attack'; f.tryAttack(String(1 + Math.floor(Math.random() * 4))); }
    } else {
      const r = Math.random();
      if (r < 0.5 + this.aggression * 0.2) { this._action = 'attack'; f.tryAttack(String(1 + Math.floor(Math.random() * 4))); }
      else if (r < 0.56) { this._action = 'attack'; f.tryVSkill(); } // V-System poke
      else if (r < 0.8) { this._action = 'approach'; f.tryMove(dir); }
      else { this._action = 'neutral'; }
    }
  }
}
