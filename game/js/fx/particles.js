/* ============================================================
   WESTERN HEART — WHEffekseerFX (Effekseer 1.80.7 particle runtime)
   Vendored: game/vendor/effekseer/ (MIT, official release binaries).
   Sample effects: game/assets/fx/effekseer/ (official .efkefc files).

   The runtime wrapper: loads the WASM module, creates one shared
   EffekseerContext on the game's WebGL context, loads .efkefc effect
   files, plays them at world positions, and manages lifecycle
   (budgets, LOD, quality levels).

   Render integration: Effekseer shares Three's GL context and draws
   AFTER the scene. init() wraps renderer.render so effects are drawn
   over the frame, then calls renderer.resetState() (fast render mode
   — official pattern from the EffekseerForWebGL sample).

   Mobile performance (owner requirement):
   - Quality levels (low/medium/high): instance caps, effect budgets,
     LOD distance, and trail effects are gated by quality.
   - Auto-detect: phones / <=4 CPU cores default to low.
   - Override persisted in localStorage 'wh-fx-quality'.
   - Concurrent-handle budget: low-priority effects are dropped first
     when the budget is exhausted, so frame rate stays flat.

   No top-level window/document/three access: safe to import in node
   for unit tests. All DOM work happens inside init().
   ============================================================ */

/** Quality levels: instance caps are applied at init; budgets/LOD live. */
export const EFX_QUALITY = {
  low:    { instanceMaxCount: 1024, squareMaxCount: 2000, maxHandles: 24,
            lodDistance: 24, trails: false, label: 'low' },
  medium: { instanceMaxCount: 2048, squareMaxCount: 4000, maxHandles: 48,
            lodDistance: 40, trails: true,  label: 'medium' },
  high:   { instanceMaxCount: 4096, squareMaxCount: 8000, maxHandles: 96,
            lodDistance: 64, trails: true,  label: 'high' },
};

/** 0xRRGGBB -> [r,g,b] floats for Effekseer setAllColor. */
export function hexToRgb(hex) {
  const h = (hex >>> 0) & 0xffffff;
  return [((h >> 16) & 0xff) / 255, ((h >> 8) & 0xff) / 255, (h & 0xff) / 255];
}

/** Quality pick: stored override, else device heuristics (phone-safe). */
export function detectQuality(env) {
  const e = env || {};
  try {
    const stored = e.localStorage && e.localStorage.getItem('wh-fx-quality');
    if (stored && EFX_QUALITY[stored]) return stored;
    const ua = (e.navigator && e.navigator.userAgent) || '';
    const cores = (e.navigator && e.navigator.hardwareConcurrency) || 4;
    const mobile = /Android|iPhone|iPad|iPod|Mobile/i.test(ua);
    if (mobile || cores <= 4) return 'low';
    return 'medium';
  } catch (err) { return 'medium'; }
}

/** Inject a classic <script> tag; the Effekseer build is a global, not ESM. */
function loadScript(url) {
  return new Promise((resolve, reject) => {
    const s = document.createElement('script');
    s.src = url;
    s.onload = () => resolve();
    s.onerror = () => reject(new Error('effekseer script load failed: ' + url));
    document.head.appendChild(s);
  });
}

export class WHEffekseerFX {
  constructor() {
    this.ready = false;
    this.context = null;
    this.renderer = null;
    this.quality = detectQuality(typeof window !== 'undefined' ? window : undefined);
    this._q = EFX_QUALITY[this.quality];
    this._effects = {};        // name -> EffekseerEffect
    this._handles = new Set(); // live handles (for budget pruning)
    this._dtFrames = 1;        // frames to advance per render
    this._drawErrors = 0;
    this._base = null;         // URL base for vendored files
  }

  /** URL of a file in the vendored runtime directory. */
  vendorUrl(file) {
    const base = this._base || new URL('../../vendor/effekseer/', import.meta.url).href;
    return base + file;
  }

  /** URL of a .efkefc effect file in game/assets/fx/effekseer/. */
  assetUrl(file) {
    const base = this._baseAssets || new URL('../../assets/fx/effekseer/', import.meta.url).href;
    return base + file;
  }

  /**
   * init(renderer, opts): loads effekseer.min.js + .wasm, creates the
   * context on the game's GL context, wraps renderer.render.
   * opts: { quality, vendorBase, assetsBase }
   */
  async init(renderer, opts = {}) {
    this.renderer = renderer;
    if (opts.quality && EFX_QUALITY[opts.quality]) {
      this.quality = opts.quality;
      this._q = EFX_QUALITY[this.quality];
    }
    if (opts.vendorBase) this._base = opts.vendorBase;
    if (opts.assetsBase) this._baseAssets = opts.assetsBase;

    await loadScript(this.vendorUrl('effekseer.min.js'));
    const G = (typeof window !== 'undefined' ? window.effekseer : null);
    if (!G) throw new Error('effekseer global missing after script load');

    await new Promise((resolve, reject) => {
      G.initRuntime(this.vendorUrl('effekseer.wasm'), resolve,
        (m, url) => reject(new Error('effekseer wasm init failed: ' + m + ' ' + url)));
    });

    this._G = G;
    this.context = G.createContext();
    this.context.init(renderer.getContext(), {
      instanceMaxCount: this._q.instanceMaxCount,
      squareMaxCount: this._q.squareMaxCount,
    });
    // Fast render mode: skip GL state save/restore (we reset Three after).
    this.context.setRestorationOfStatesFlag(false);

    // Draw effects over every frame, right after the scene.
    if (!renderer._whEfxPatched) {
      renderer._whEfxPatched = true;
      const origRender = renderer.render.bind(renderer);
      const self = this;
      renderer.render = function (scene, camera) {
        origRender(scene, camera);
        self._drawOver(camera);
      };
    }

    this.ready = true;
    return this;
  }

  /** Per-frame tick from the integration rAF (dt in seconds). */
  tick(dt) {
    this._dtFrames = Math.max(0.5, Math.min(3, dt * 60));
  }

  _drawOver(camera) {
    if (!this.ready || !camera) return;
    try {
      camera.updateMatrixWorld();
      this.context.setProjectionMatrix(camera.projectionMatrix.elements);
      this.context.setCameraMatrix(camera.matrixWorldInverse.elements);
      this.context.update(this._dtFrames);
      this.context.draw();
      // Fast render mode dirties GL state: Three must rebuild its cache.
      this.renderer.resetState();
      this._drawErrors = 0;
    } catch (e) {
      this._drawErrors++;
      // Fail safe: after repeated draw errors, stop drawing over frames
      // rather than corrupting the render loop.
      if (this._drawErrors > 30) { this.ready = false; }
    }
  }

  /** Load a .efkefc effect file by name (cached; promise per name). */
  loadEffect(name, url) {
    if (this._effects[name]) return Promise.resolve(this._effects[name]);
    const G = this._G;
    void G; // init() already validated the runtime
    return new Promise((resolve, reject) => {
      const effect = this.context.loadEffect(url, 1.0,
        () => { this._effects[name] = effect; resolve(effect); },
        (m, u) => reject(new Error('loadEffect ' + name + ' failed: ' + m + ' ' + u)));
    });
  }

  _pruneDead() {
    for (const h of this._handles) {
      try { if (!h.exists) this._handles.delete(h); }
      catch (e) { this._handles.delete(h); }
    }
  }

  /** Live-handle count for the budget / HUD debugging. */
  liveCount() {
    this._pruneDead();
    return this._handles.size;
  }

  /**
   * Play an effect at a world position.
   * opts: { scale, color (0xRRGGBB tint), rotationY, priority: 'low'|'normal'|'high',
   *         camera (for LOD distance cull) }
   * Returns the EffekseerHandle, or null when culled / over budget.
   */
  play(name, x = 0, y = 0, z = 0, opts = {}) {
    if (!this.ready) return null;
    const effect = this._effects[name];
    if (!effect) return null;

    // LOD: drop low-priority effects far from the camera.
    if (opts.camera && opts.priority === 'low' && cameraHasPosition(opts.camera)) {
      const p = opts.camera.position;
      const dx = p.x - x, dy = p.y - y, dz = p.z - z;
      if (dx * dx + dy * dy + dz * dz > this._q.lodDistance * this._q.lodDistance) {
        return null;
      }
    }

    // Budget: never exceed maxHandles; low-priority drops first.
    this._pruneDead();
    if (this._handles.size >= this._q.maxHandles) {
      if (opts.priority !== 'high') return null;
      // High priority: stop the oldest handle to make room.
      const oldest = this._handles.values().next().value;
      if (oldest) { try { oldest.stop(); } catch (e) {} this._handles.delete(oldest); }
    }

    const h = this.context.play(effect, x, y, z);
    const s = opts.scale || 1;
    if (s !== 1) h.setScale(s, s, s);
    if (opts.rotationY) h.setRotation(0, opts.rotationY, 0);
    if (opts.color != null) {
      const [r, g, b] = hexToRgb(opts.color);
      h.setAllColor(r, g, b, 1);
    }
    this._handles.add(h);
    return h;
  }

  /** Change quality at runtime (budgets/LOD/trails apply immediately;
      instance caps apply on next init). */
  setQuality(q) {
    if (!EFX_QUALITY[q]) return false;
    this.quality = q;
    this._q = EFX_QUALITY[q];
    try { localStorage.setItem('wh-fx-quality', q); } catch (e) {}
    return true;
  }

  stopAll() {
    if (this.context) { try { this.context.stopAll(); } catch (e) {} }
    this._handles.clear();
  }

  stats() {
    let rest = -1;
    try { rest = this.context ? this.context.getRestInstancesCount() : -1; } catch (e) {}
    return {
      ready: this.ready, quality: this.quality,
      liveHandles: this._handles.size, restInstances: rest,
    };
  }
}

function cameraHasPosition(camera) {
  return camera && camera.position &&
    typeof camera.position.x === 'number';
}
