/* ============================================================
   WESTERN HEART — Photo Mode (DOA-style)
   Pause anytime -> free camera -> filters -> capture.

   - P (or F9) anywhere in a fight: freezes the game, hands the
     camera to the player.
   - Drag = orbit, wheel = dolly zoom, right-drag / WASD = pan.
   - Filters are post looks applied to the canvas element
     (CSS filter stack + vignette overlay), DOA photo-mode style.
   - C or the capture button: downloads a PNG of the frame.
   - ESC exits, restores the fight camera, resumes.
   ============================================================ */

export const PHOTO_FILTERS = {
  none:      { name: 'NONE',        css: 'none', vignette: 0 },
  noir:      { name: 'NOIR',        css: 'grayscale(1) contrast(1.25) brightness(.95)', vignette: 0.35 },
  sepia:     { name: 'SEPIA',       css: 'sepia(.8) contrast(1.05)', vignette: 0.25 },
  vivid:     { name: 'VIVID',       css: 'saturate(1.8) contrast(1.15)', vignette: 0 },
  cinematic: { name: 'CINEMATIC',   css: 'saturate(1.2) contrast(1.2) brightness(.92)', vignette: 0.55 },
  ghost:     { name: 'GHOST',       css: 'hue-rotate(160deg) saturate(.7) brightness(1.1)', vignette: 0.3 },
  ember:     { name: 'EMBER',       css: 'sepia(.4) hue-rotate(-25deg) saturate(1.6) contrast(1.1)', vignette: 0.4 },
};

export class PhotoMode {
  constructor(game) {
    this.game = game;
    this.active = false;
    this.filter = 'none';
    this._keys = {};
    this._raf = 0;
    // orbit state
    this._target = null; this._theta = 0; this._phi = 1.1; this._dist = 6;
    this._saved = null;
  }

  get camera() { return this.game.arena && this.game.arena.camera; }
  get canvas() { return document.getElementById('game-canvas'); }

  toggle() { this.active ? this.exit() : this.enter(); }

  enter() {
    const cam = this.camera, canvas = this.canvas;
    if (!cam || !canvas || this.active) return;
    if (!this.game.running) return;
    this.active = true;
    this.game.pause(true);
    // Save the fight camera pose for a clean restore.
    this._saved = {
      pos: cam.position.clone(), quat: cam.quaternion.clone(),
      filter: canvas.style.filter, vig: null,
    };
    // Orbit around the midpoint between the fighters (or arena center).
    const g = this.game;
    const mid = (g.p1 && g.p2)
      ? g.p1.root.position.clone().add(g.p2.root.position).multiplyScalar(0.5)
      : new (cam.position.constructor)(0, 1, 0);
    mid.y = Math.max(0.8, mid.y);
    this._target = mid;
    const off = cam.position.clone().sub(mid);
    this._dist = Math.max(2, Math.min(14, off.length()));
    this._theta = Math.atan2(off.x, off.z);
    this._phi = Math.acos(Math.max(-1, Math.min(1, off.y / (off.length() || 1))));
    this._buildUI();
    this._applyFilter('none');
    this._bindInput();
    this._loop();
  }

  exit() {
    if (!this.active) return;
    this.active = false;
    cancelAnimationFrame(this._raf);
    this._unbindInput();
    const cam = this.camera, canvas = this.canvas;
    if (cam && this._saved) {
      cam.position.copy(this._saved.pos);
      cam.quaternion.copy(this._saved.quat);
    }
    if (canvas && this._saved) canvas.style.filter = this._saved.filter || '';
    const vig = document.getElementById('photo-vignette');
    if (vig) vig.remove();
    const ui = document.getElementById('photo-ui');
    if (ui) ui.remove();
    this.game.pause(false);
  }

  _buildUI() {
    const ui = document.createElement('div');
    ui.id = 'photo-ui';
    ui.style.cssText = 'position:fixed;left:12px;bottom:12px;z-index:70;display:flex;gap:8px;align-items:center;' +
      'background:rgba(8,8,14,.92);border:1px solid #7a5cff;border-radius:10px;padding:10px 12px;' +
      'color:#e8e4ff;font:12px/1.4 system-ui;';
    ui.innerHTML =
      `<span style="font-weight:700;letter-spacing:.08em;color:#b7a6ff">PHOTO MODE</span>` +
      `<select id="photo-filter" style="background:#14141f;color:#e8e4ff;border:1px solid #444;border-radius:6px;padding:4px">${
        Object.entries(PHOTO_FILTERS).map(([k, f]) => `<option value="${k}">${f.name}</option>`).join('')
      }</select>` +
      `<button id="photo-cap">📷 CAPTURE (C)</button>` +
      `<button id="photo-exit">EXIT (ESC)</button>` +
      `<span style="opacity:.6">drag orbit · wheel zoom · right-drag/WASD pan</span>`;
    document.body.appendChild(ui);
    ui.querySelector('#photo-filter').onchange = (e) => this._applyFilter(e.target.value);
    ui.querySelector('#photo-cap').onclick = () => this.capture();
    ui.querySelector('#photo-exit').onclick = () => this.exit();
  }

  _applyFilter(key) {
    this.filter = PHOTO_FILTERS[key] ? key : 'none';
    const canvas = this.canvas;
    if (canvas) canvas.style.filter = PHOTO_FILTERS[this.filter].css;
    let vig = document.getElementById('photo-vignette');
    const v = PHOTO_FILTERS[this.filter].vignette;
    if (v > 0) {
      if (!vig) {
        vig = document.createElement('div');
        vig.id = 'photo-vignette';
        vig.style.cssText = 'position:fixed;inset:0;z-index:65;pointer-events:none;';
        document.body.appendChild(vig);
      }
      vig.style.background = `radial-gradient(ellipse at center, transparent 55%, rgba(0,0,0,${v}) 100%)`;
      vig.style.display = 'block';
    } else if (vig) vig.style.display = 'none';
  }

  capture() {
    const canvas = this.canvas;
    if (!canvas) return;
    try {
      const a = document.createElement('a');
      a.download = `western-heart-photo-${Date.now()}.png`;
      a.href = canvas.toDataURL('image/png');
      a.click();
    } catch (e) { console.warn('[WH] photo capture failed:', e?.message || e); }
  }

  _bindInput() {
    const canvas = this.canvas;
    this._onMouseDown = (e) => {
      this._drag = { x: e.clientX, y: e.clientY, btn: e.button };
      e.preventDefault();
    };
    this._onMouseMove = (e) => {
      if (!this._drag) return;
      const dx = e.clientX - this._drag.x, dy = e.clientY - this._drag.y;
      this._drag.x = e.clientX; this._drag.y = e.clientY;
      if (this._drag.btn === 2 || e.shiftKey) {
        // pan
        const s = this._dist * 0.0016;
        const right = { x: Math.cos(this._theta), z: -Math.sin(this._theta) };
        this._target.x -= dx * s * right.x;
        this._target.z -= dx * s * right.z;
        this._target.y += dy * s;
        this._target.y = Math.max(0.2, Math.min(4, this._target.y));
      } else {
        this._theta -= dx * 0.005;
        this._phi = Math.max(0.15, Math.min(1.5, this._phi - dy * 0.005));
      }
    };
    this._onMouseUp = () => { this._drag = null; };
    this._onWheel = (e) => {
      this._dist = Math.max(1.5, Math.min(16, this._dist + e.deltaY * 0.005));
      e.preventDefault();
    };
    this._onKeyDown = (e) => {
      this._keys[e.code] = true;
      if (e.code === 'Escape') this.exit();
      else if (e.code === 'KeyC') this.capture();
    };
    this._onKeyUp = (e) => { this._keys[e.code] = false; };
    this._onCtx = (e) => e.preventDefault();
    canvas.addEventListener('mousedown', this._onMouseDown);
    window.addEventListener('mousemove', this._onMouseMove);
    window.addEventListener('mouseup', this._onMouseUp);
    canvas.addEventListener('wheel', this._onWheel, { passive: false });
    window.addEventListener('keydown', this._onKeyDown);
    window.addEventListener('keyup', this._onKeyUp);
    canvas.addEventListener('contextmenu', this._onCtx);
  }

  _unbindInput() {
    const canvas = this.canvas;
    if (!canvas) return;
    canvas.removeEventListener('mousedown', this._onMouseDown);
    window.removeEventListener('mousemove', this._onMouseMove);
    window.removeEventListener('mouseup', this._onMouseUp);
    canvas.removeEventListener('wheel', this._onWheel);
    window.removeEventListener('keydown', this._onKeyDown);
    window.removeEventListener('keyup', this._onKeyUp);
    canvas.removeEventListener('contextmenu', this._onCtx);
    this._keys = {};
  }

  _loop() {
    if (!this.active) return;
    // WASD pan
    const k = this._keys, s = this._dist * 0.02;
    const right = { x: Math.cos(this._theta), z: -Math.sin(this._theta) };
    const fwd = { x: Math.sin(this._theta), z: Math.cos(this._theta) };
    if (k['KeyA']) { this._target.x -= right.x * s; this._target.z -= right.z * s; }
    if (k['KeyD']) { this._target.x += right.x * s; this._target.z += right.z * s; }
    if (k['KeyW']) { this._target.x += fwd.x * s; this._target.z += fwd.z * s; }
    if (k['KeyS']) { this._target.x -= fwd.x * s; this._target.z -= fwd.z * s; }
    if (k['KeyQ']) this._target.y = Math.max(0.2, this._target.y - s * 0.5);
    if (k['KeyE']) this._target.y = Math.min(4, this._target.y + s * 0.5);
    const cam = this.camera;
    if (cam && this._target) {
      cam.position.set(
        this._target.x + this._dist * Math.sin(this._phi) * Math.sin(this._theta),
        this._target.y + this._dist * Math.cos(this._phi),
        this._target.z + this._dist * Math.sin(this._phi) * Math.cos(this._theta),
      );
      cam.lookAt(this._target);
    }
    this._raf = requestAnimationFrame(() => this._loop());
  }
}

/* One PhotoMode per game; P/F9 toggles it mid-fight. */
export function installPhotoMode(game) {
  if (game.photoMode) return game.photoMode;
  game.photoMode = new PhotoMode(game);
  window.addEventListener('keydown', (e) => {
    if ((e.code === 'KeyP' || e.code === 'F9') && game.running && !e.repeat) {
      // Don't hijack typing in suite inputs.
      if (/INPUT|TEXTAREA|SELECT/.test(document.activeElement?.tagName || '')) return;
      game.photoMode.toggle();
    }
  });
  return game.photoMode;
}
