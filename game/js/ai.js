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
  }

  update(dt, player) {
    const f = this.f, p = player;
    if (f.dead || f.state === 'ko' || f.state === 'victory') return;

    this._think -= dt;
    this._actionT -= dt;

    const dx = p.root.position.x - f.root.position.x;
    const dist = Math.abs(dx);
    const dir = Math.sign(dx) || 1;
    const playerAttacking = p.state === 'attack' && p._attackPhase !== 'recovery';

    // Reactive defense: block/dodge incoming attacks (gated by reaction stat)
    if (playerAttacking && dist < 2.6 && f.canAct()) {
      const react = Math.random() < (0.25 + this.reaction * 0.5);
      if (react) {
        if (Math.random() < 0.35 && f.onGround) { f.tryDodge(); this._think = 0.4; return; }
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
      else { this._action = 'attack'; f.tryAttack(Math.random() < 0.6 ? 'punch' : 'kick'); }
    } else {
      const r = Math.random();
      if (r < 0.5 + this.aggression * 0.2) { this._action = 'attack'; f.tryAttack(r < 0.3 ? 'kick' : 'punch'); }
      else if (r < 0.8) { this._action = 'approach'; f.tryMove(dir); }
      else { this._action = 'neutral'; }
    }
  }
}
