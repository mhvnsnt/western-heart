/* ============================================================
   WESTERN HEART — WHHitEffects (unified combat hit FX)
   Owner bug 2026-10-22: "HIT EFFECTS — current ones look prototype —
   pull Tekken's hit effects and replace."

   Effekseer (game/js/fx/particles.js) is the primary hit-effect
   backend: real GPU particle effects from official .efkefc files
   (ToonHit = impact burst, Blow1 = blast wind, Light = core flash,
   Cure1 = aura). The three-nebula WHHitFX stays as the fallback
   (dust, surge, and any case where Effekseer is unavailable) —
   layering, never parallel competing systems.

   API: spawn(x, y, z, color, scale, kind) is signature-compatible
   with game.js _spawnImpact and WHHitFX.spawn. kind:
   impact | heavy | ko | block | dust | surge (auto-derived from scale
   when null: >=1.3 ko, >=0.9 heavy, else impact).

   Kick wind trails: trailStart(anchorObject3D) attaches a moving wind
   burst to a limb during kicks; trailStop(id) ends it. Gated by the
   Effekseer quality level (off on 'low').

   No top-level window/document/three: safe to import in node tests.
   ============================================================ */

/** Official .efkefc effects (game/assets/fx/effekseer/), per WH role. */
export const EFX_ASSETS = {
  'toon-hit': 'ToonHit.efkefc',  // cartoon impact burst (impact/heavy)
  'light':    'Light.efkefc',    // core flash (heavy/ko/block)
  'blow':     'Blow1.efkefc',    // blast wind (KO, kick wind, urge dash)
  'cure':     'Cure1.efkefc',    // aura glow (Soul Urge)
};

export function kindForScale(scale) {
  return scale >= 1.3 ? 'ko' : scale >= 0.9 ? 'heavy' : 'impact';
}

let _trailId = 0;

export class WHHitEffects {
  constructor() {
    this.ready = false;
    this.fx = null;        // WHEffekseerFX (primary)
    this.fallback = null;  // WHHitFX / nebula (fallback)
    this._trails = new Map(); // id -> { handle, anchor, pos }
  }

  /** Preload the combat effects through the Effekseer wrapper. */
  async init(fx, fallback) {
    this.fx = fx || null;
    this.fallback = fallback || null;
    if (this.fx && this.fx.ready) {
      for (const [name, file] of Object.entries(EFX_ASSETS)) {
        try { await this.fx.loadEffect(name, this.fx.assetUrl(file)); }
        catch (e) { /* one missing effect must not kill the set */ }
      }
    }
    this.ready = true;
    return this;
  }

  /**
   * Spawn a hit effect. Returns true when something was drawn.
   * Signature-compatible with WHHitFX.spawn(x,y,z,color,scale,kind).
   */
  spawn(x, y, z, color = 0xffcf4d, scale = 1, kind = null) {
    const k = kind || kindForScale(scale);
    if (this.fx && this.fx.ready) {
      try {
        if (k === 'ko') {
          // KO: layered blast + core flash (never dropped mid-budget).
          this.fx.play('blow', x, y, z, { scale: 1.5 * scale, color, priority: 'high' });
          this.fx.play('light', x, y, z, { scale: 1.2 * scale, color, priority: 'high' });
          return true;
        }
        if (k === 'heavy') {
          this.fx.play('toon-hit', x, y, z, { scale: 1.15 * scale, color });
          this.fx.play('light', x, y, z, { scale: 0.7 * scale, color });
          return true;
        }
        if (k === 'block') {
          this.fx.play('light', x, y, z, { scale: 0.65 * scale, color: 0x9fd8ff });
          return true;
        }
        if (k === 'impact') {
          this.fx.play('toon-hit', x, y, z, { scale: 0.8 * scale, color });
          return true;
        }
        // dust / surge: nebula's domain (soft particles, rising auras).
      } catch (e) { /* fall through to fallback */ }
    }
    if (this.fallback && typeof this.fallback.spawn === 'function') {
      return this.fallback.spawn(x, y, z, color, scale, kind) !== false;
    }
    return false;
  }

  /**
   * Start a kick wind trail on an Object3D anchor (e.g. a foot bone).
   * Returns a trail id, or null when trails are disabled (low quality)
   * or Effekseer is unavailable.
   */
  trailStart(anchor, { effect = 'blow', scale = 0.55 } = {}) {
    if (!this.fx || !this.fx.ready) return null;
    if (!this.fx._q || !this.fx._q.trails) return null;
    if (!anchor || typeof anchor.getWorldPosition !== 'function') return null;
    const id = ++_trailId;
    const h = this.fx.play(effect, 0, 0, 0, { scale, priority: 'low' });
    if (!h) return null;
    const pos = {
      x: 0, y: 0, z: 0,
      set(x, y, z) { this.x = x; this.y = y; this.z = z; return this; },
      // three's getWorldPosition(target) calls target.setFromMatrixPosition.
      setFromMatrixPosition(m) {
        const e = m.elements;
        this.x = e[12]; this.y = e[13]; this.z = e[14];
        return this;
      },
    };
    anchor.getWorldPosition(pos);
    h.setLocation(pos.x, pos.y, pos.z);
    this._trails.set(id, { handle: h, anchor, pos });
    return id;
  }

  /** Stop a kick wind trail. */
  trailStop(id) {
    const t = this._trails.get(id);
    if (!t) return false;
    try { t.handle.stop(); } catch (e) {}
    this._trails.delete(id);
    return true;
  }

  /** Per-frame: follow trail anchors; prune dead trails. */
  update(dt) {
    void dt;
    for (const [id, t] of this._trails) {
      let alive = true;
      try { alive = !!t.handle.exists; } catch (e) { alive = false; }
      if (!alive) { this._trails.delete(id); continue; }
      try {
        t.anchor.getWorldPosition(t.pos);
        t.handle.setLocation(t.pos.x, t.pos.y, t.pos.z);
      } catch (e) { /* anchor removed; keep last position */ }
    }
  }

  stopAll() {
    for (const id of [...this._trails.keys()]) this.trailStop(id);
    if (this.fx) this.fx.stopAll();
  }
}
