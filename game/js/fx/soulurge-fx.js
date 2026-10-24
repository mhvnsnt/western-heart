/* ============================================================
   WESTERN HEART — WHSoulUrgeFX (Soul Urge / T8 Heat visual cues)
   Soul Urge is the game's Heat system (user-locked 2026-10-22).

   Layers Effekseer particle cues over the existing soul-flame aura
   tint (fighter.setUrgeAura): 
     - onActivate: ignition burst (Light + ToonHit) + looping aura
     - onExpire:   aura stops with the state
     - onSmash:    URGE SMASH cinematic burst (Blow1 + Light + ToonHit)
     - onDash:     Urge Dash wind whoosh

   Hooked from game/js/integration.js via SoulUrge/Fighter prototype
   patches — no soulurge.js or fighter.js edits needed. All adults;
   pure VFX, no character content.

   Aura persistence: the Cure1 sample effect is one-shot, so the aura
   re-plays while the fighter is urging (AURA_REPLAY_S seconds).
   ============================================================ */

export const AURA_REPLAY_S = 1.1; // aura pulse interval while urging

export class WHSoulUrgeFX {
  constructor() {
    this.ready = false;
    this.fx = null;
    this._auras = new Map(); // fighter -> { fighter, lastPlay }
    this._time = 0;
  }

  async init(fx) {
    this.fx = fx || null;
    this.ready = !!(fx && fx.ready);
    return this;
  }

  _posOf(fighter, out) {
    if (fighter && fighter.root && fighter.root.position) {
      out.x = fighter.root.position.x;
      out.y = (fighter.root.position.y || 0) + 1.0;
      out.z = fighter.root.position.z;
      return out;
    }
    return null;
  }

  /** Soul Urge ignition: burst + start the looping aura. */
  onActivate(fighter) {
    if (!this.ready) return false;
    const p = this._posOf(fighter, { x: 0, y: 0, z: 0 });
    if (!p) return false;
    this.fx.play('light', p.x, p.y, p.z, { scale: 1.8, color: 0x3aa8ff, priority: 'high' });
    this.fx.play('toon-hit', p.x, p.y, p.z, { scale: 1.4, color: 0x3aa8ff, priority: 'high' });
    this._auras.set(fighter, { fighter, lastPlay: -AURA_REPLAY_S });
    return true;
  }

  /** Soul Urge ends: stop the aura loop. */
  onExpire(fighter) {
    this._auras.delete(fighter);
    return true;
  }

  /** Urge Smash connect: the big cinematic beat. */
  onSmash(fighter) {
    if (!this.ready) return false;
    const p = this._posOf(fighter, { x: 0, y: 0, z: 0 });
    if (!p) return false;
    this.fx.play('blow', p.x, p.y, p.z, { scale: 2.2, color: 0x3aa8ff, priority: 'high' });
    this.fx.play('light', p.x, p.y, p.z, { scale: 1.8, color: 0xffffff, priority: 'high' });
    this.fx.play('toon-hit', p.x, p.y, p.z, { scale: 1.6, color: 0x3aa8ff, priority: 'high' });
    return true;
  }

  /** Urge Dash: a quick wind whoosh at the fighter's feet. */
  onDash(fighter) {
    if (!this.ready) return false;
    const p = this._posOf(fighter, { x: 0, y: 0, z: 0 });
    if (!p) return false;
    this.fx.play('blow', p.x, 0.4, p.z, { scale: 0.8, color: 0x3aa8ff });
    return true;
  }

  /** Per-frame: re-pulse the aura while the fighter is still urging. */
  update(dt) {
    if (!this.ready) return;
    this._time += dt || 0;
    for (const [fighter, a] of this._auras) {
      const urging = fighter && fighter._urgeOn;
      if (!urging) { this._auras.delete(fighter); continue; }
      if (this._time - a.lastPlay >= AURA_REPLAY_S) {
        a.lastPlay = this._time;
        const p = this._posOf(fighter, { x: 0, y: 0, z: 0 });
        if (p) {
          this.fx.play('cure', p.x, p.y, p.z,
            { scale: 1.3, color: 0x3aa8ff, priority: 'low' });
        }
      }
    }
  }

  stopAll() {
    this._auras.clear();
    if (this.fx) this.fx.stopAll();
  }
}
