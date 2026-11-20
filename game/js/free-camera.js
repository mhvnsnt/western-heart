/* ============================================================
   WESTERN HEART — Free Camera for game scene playback
   User directive 2026-10-24 21:35 CDT: during ANY scene playback the
   user can take the camera himself — orbit, pan, zoom, on his phone
   (one-finger orbit, pinch zoom, two-finger pan) — plus part-focus
   and preset views. Extends the closet manual-control spec
   (CLOSET_MANUAL_CONTROL_SPEC.md §6) from the closet viewer to
   live game scenes.

   CONTRACT (read before touching this file):
   - The fight NEVER pauses for the free camera. Photo Mode
     (game/js/photomode.js) pauses; this module does not, ever.
   - The authored camera is NEVER overwritten. The authored fight
     camera in game/js/scene.js (Arena.update) is procedural: it is
     recomputed from the fighters every frame. This module only
     gates it (Arena.freeCameraActive, see scene.js) while active,
     and on exit the next Arena.update() recomputes it — the camera
     eases back to the authored view on its own smoothing. No
     authored pose, shot list, or stage-intro path is stored,
     mutated, or saved over by this module.
   - A free-camera move is NEVER saved over a scene. saveTake()
     only returns a new, named, versioned take object (and fires
     a 'wh:free-camera-take' event for whoever wants to persist
     it). It writes nothing into stage-intros.js, camdirector.js,
     or any authored path.
   - This module does NOT touch packages/creation-suite/ui2/viewer.js
     (the closet lane's viewer). It reuses only the part-focus
     formula from the closet spec: distance = bbox size x 2.5.
   - Scope of this version: FIGHT scene playback (the live Arena
     camera). Stage-intro sweeps (stage-intros.js) and cutscene
     shot lists (camdirector.js) are NOT gated here — see
     docs/tech/free-camera-scene-playback.md for the exact
     follow-up, not a silent claim that they are covered.
   - Mutual exclusion: enter() refuses while Photo Mode is active,
     because Photo Mode owns the camera and pauses the game.
     Exit free camera before pressing P/F9. Photo Mode itself is
     not patched by this module.
   ============================================================ */

import * as THREE from 'three';

const MIN_DIST = 1.2;
const MAX_DIST = 14;
const MIN_PHI = 0.12;
const MAX_PHI = Math.PI * 0.55;

function clampDist(d) { return THREE.MathUtils.clamp(d, MIN_DIST, MAX_DIST); }

export class FreeCamera {
  constructor(game) {
    this.game = game;
    this.active = false;
    this._target = new THREE.Vector3(0, 1.0, 0);
    this._theta = 0;
    this._phi = 1.1;
    this._dist = 6;
    this._pointers = new Map();
    this._pinchDist = 0;
    this._panMid = null;
    this._raf = 0;
    this._ui = null;
    this._toggle = null;
    this._savedTouchAction = '';
  }

  get camera() { return this.game.arena && this.game.arena.camera; }
  get canvas() {
    return (this.game.arena && this.game.arena.renderer && this.game.arena.renderer.domElement)
      || document.getElementById('game-canvas');
  }

  _midpoint() {
    const g = this.game;
    if (g.p1 && g.p2 && g.p1.root && g.p2.root) {
      return g.p1.root.position.clone().add(g.p2.root.position).multiplyScalar(0.5);
    }
    return new THREE.Vector3(0, 1.0, 0);
  }

  _setArenaGate(on) {
    const arena = this.game.arena;
    if (!arena) return;
    if (typeof arena.setFreeCamera === 'function') arena.setFreeCamera(on);
    else arena.freeCameraActive = !!on;
  }

  enter() {
    const cam = this.camera, canvas = this.canvas;
    if (!cam || !canvas || this.active) return false;
    if (this.game.photoMode && this.game.photoMode.active) return false;
    this.active = true;
    // Start from where the authored camera is looking, so takeover
    // is a smooth handoff, not a jump to a canned pose.
    const mid = this._midpoint();
    mid.y = Math.max(0.8, mid.y);
    this._target.copy(mid);
    const off = cam.position.clone().sub(mid);
    this._dist = clampDist(off.length() || 6);
    this._theta = Math.atan2(off.x, off.z);
    this._phi = THREE.MathUtils.clamp(
      Math.acos(THREE.MathUtils.clamp(off.y / (off.length() || 1), -1, 1)),
      MIN_PHI, MAX_PHI);
    this._setArenaGate(true);
    this._savedTouchAction = canvas.style.touchAction;
    canvas.style.touchAction = 'none';
    this._buildUI();
    this._bindInput();
    this._loop();
    return true;
  }

  exit() {
    if (!this.active) return;
    this.active = false;
    cancelAnimationFrame(this._raf);
    this._unbindInput();
    const canvas = this.canvas;
    if (canvas) canvas.style.touchAction = this._savedTouchAction;
    if (this._ui) { this._ui.remove(); this._ui = null; }
    // Deliberately NO pose restore here: the authored camera is
    // procedural, so the next Arena.update() recomputes it. Restoring
    // a snapshot (as camdirector.release() does) would freeze the
    // authored view at the takeover moment instead of the live one.
    this._setArenaGate(false);
    if (this._toggle) this._toggle.textContent = 'FREE CAMERA';
  }

  toggle() { this.active ? this.exit() : this.enter(); }

  /* ---- Presets + focus (closet-spec formula, no per-part numbers) ---- */

  preset(name) {
    if (!this.active) return false;
    if (name === 'front') { this._theta = 0; this._phi = 1.1; }
    else if (name === 'side') { this._theta = Math.PI / 2; this._phi = 1.1; }
    else if (name === 'back') { this._theta = Math.PI; this._phi = 1.1; }
    else if (name === 'top') { this._phi = MIN_PHI; }
    else if (name === 'wide') { this._dist = clampDist(this._dist * 1.8); }
    else return false;
    this._apply();
    return true;
  }

  fullBody() {
    if (!this.active) return false;
    const mid = this._midpoint();
    mid.y = Math.max(0.8, mid.y);
    this._target.copy(mid);
    this._dist = clampDist(6.5);
    this._phi = 1.1;
    this._apply();
    return true;
  }

  /* Frame one part (or fighter) alone, closet-spec formula:
     target = bounding-box centre, distance = bbox size x 2.5. */
  focusOn(object3D) {
    if (!this.active || !object3D) return false;
    const box = new THREE.Box3().setFromObject(object3D);
    if (box.isEmpty()) return false;
    const size = box.getSize(new THREE.Vector3());
    const center = box.getCenter(new THREE.Vector3());
    this._target.copy(center);
    this._dist = clampDist(Math.max(size.x, size.y, size.z) * 2.5);
    this._apply();
    return true;
  }

  focusFighter(fighter) {
    return fighter && fighter.root ? this.focusOn(fighter.root) : false;
  }

  /* A take is a NEW object, never a write over an authored path. */
  saveTake(name) {
    const take = {
      name: name || `take-${Date.now()}`,
      version: 1,
      savedAt: new Date().toISOString(),
      target: [this._target.x, this._target.y, this._target.z],
      theta: this._theta, phi: this._phi, dist: this._dist,
    };
    document.dispatchEvent(new CustomEvent('wh:free-camera-take', { detail: take }));
    return take;
  }

  /* ---- Per-frame pose (own rAF, like PhotoMode._loop) ---- */

  _apply() {
    const cam = this.camera;
    if (!cam) return;
    cam.position.set(
      this._target.x + this._dist * Math.sin(this._phi) * Math.sin(this._theta),
      this._target.y + this._dist * Math.cos(this._phi),
      this._target.z + this._dist * Math.sin(this._phi) * Math.cos(this._theta));
    cam.lookAt(this._target);
  }

  _loop() {
    if (!this.active) return;
    // Leaving the fight (quit, results, menus) ends the free camera: its bar must never sit over a menu.
    const g = this.game;
    if (g && !g.running && !g.brawler) { this.exit(); return; }
    this._apply();
    this._raf = requestAnimationFrame(() => this._loop());
  }

  /* ---- Touch + wheel input: 1-finger orbit, pinch zoom, 2-finger pan ---- */

  _bindInput() {
    const canvas = this.canvas;
    this._onPointerDown = (e) => {
      this._pointers.set(e.pointerId, { x: e.clientX, y: e.clientY });
      try { canvas.setPointerCapture(e.pointerId); } catch (_) { /* noop */ }
      if (this._pointers.size === 2) {
        const [a, b] = [...this._pointers.values()];
        this._pinchDist = Math.hypot(a.x - b.x, a.y - b.y);
        this._panMid = { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 };
      }
      e.preventDefault();
    };
    this._onPointerMove = (e) => {
      const p = this._pointers.get(e.pointerId);
      if (!p) return;
      const dx = e.clientX - p.x, dy = e.clientY - p.y;
      this._pointers.set(e.pointerId, { x: e.clientX, y: e.clientY });
      if (this._pointers.size === 1) {
        // One finger: orbit.
        this._theta -= dx * 0.005;
        this._phi = THREE.MathUtils.clamp(this._phi + dy * 0.005, MIN_PHI, MAX_PHI);
      } else if (this._pointers.size === 2) {
        const [a, b] = [...this._pointers.values()];
        // Pinch: zoom.
        const cur = Math.hypot(a.x - b.x, a.y - b.y);
        if (this._pinchDist > 0 && cur > 0) this._dist = clampDist(this._dist * (this._pinchDist / cur));
        this._pinchDist = cur;
        // Two-finger drag: pan the target in the camera plane.
        const mid = { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 };
        if (this._panMid) {
          const mdx = mid.x - this._panMid.x, mdy = mid.y - this._panMid.y;
          const cam = this.camera;
          if (cam) {
            const fwd = new THREE.Vector3();
            cam.getWorldDirection(fwd);
            const right = new THREE.Vector3().crossVectors(fwd, new THREE.Vector3(0, 1, 0)).normalize();
            const up = new THREE.Vector3().crossVectors(right, fwd).normalize();
            const s = this._dist * 0.0015;
            this._target.addScaledVector(right, -mdx * s).addScaledVector(up, mdy * s);
          }
        }
        this._panMid = mid;
      }
      this._apply();
      e.preventDefault();
    };
    const endPointer = (e) => {
      this._pointers.delete(e.pointerId);
      if (this._pointers.size < 2) { this._pinchDist = 0; this._panMid = null; }
    };
    this._onPointerUp = endPointer;
    this._onPointerCancel = endPointer;
    this._onWheel = (e) => {
      this._dist = clampDist(this._dist * (1 + e.deltaY * 0.001));
      this._apply();
      e.preventDefault();
    };
    canvas.addEventListener('pointerdown', this._onPointerDown);
    canvas.addEventListener('pointermove', this._onPointerMove);
    canvas.addEventListener('pointerup', this._onPointerUp);
    canvas.addEventListener('pointercancel', this._onPointerCancel);
    canvas.addEventListener('wheel', this._onWheel, { passive: false });
  }

  _unbindInput() {
    const canvas = this.canvas;
    if (!canvas) return;
    canvas.removeEventListener('pointerdown', this._onPointerDown);
    canvas.removeEventListener('pointermove', this._onPointerMove);
    canvas.removeEventListener('pointerup', this._onPointerUp);
    canvas.removeEventListener('pointercancel', this._onPointerCancel);
    canvas.removeEventListener('wheel', this._onWheel);
    this._pointers.clear();
  }

  /* ---- UI: every button >= 44px, tap targets, no keyboard hijack ---- */

  _buildUI() {
    const bar = document.createElement('div');
    bar.id = 'free-cam-ui';
    bar.style.cssText = 'position:fixed;left:12px;right:12px;bottom:12px;z-index:80;display:flex;flex-wrap:wrap;gap:8px;align-items:center;'
      + 'background:rgba(8,8,14,.92);border:1px solid #7a5cff;border-radius:10px;padding:10px 12px;'
      + 'color:#e8e4ff;font:14px/1.4 system-ui;';
    const btn = (label, fn) => {
      const b = document.createElement('button');
      b.textContent = label;
      b.style.cssText = 'min-width:44px;min-height:44px;padding:8px 12px;background:#14141f;color:#e8e4ff;border:1px solid #444;border-radius:8px;';
      b.addEventListener('click', fn);
      bar.appendChild(b);
      return b;
    };
    const title = document.createElement('span');
    title.textContent = 'FREE CAMERA';
    title.style.cssText = 'font-weight:700;letter-spacing:.08em;color:#b7a6ff';
    bar.appendChild(title);
    btn('FRONT', () => this.preset('front'));
    btn('SIDE', () => this.preset('side'));
    btn('BACK', () => this.preset('back'));
    btn('TOP', () => this.preset('top'));
    btn('WIDE', () => this.preset('wide'));
    btn('FOCUS P1', () => this.focusFighter(this.game.p1));
    btn('FOCUS P2', () => this.focusFighter(this.game.p2));
    btn('FULL BODY', () => this.fullBody());
    const status = document.createElement('span');
    status.id = 'free-cam-status';
    status.style.cssText = 'opacity:.6';
    status.textContent = '1 finger orbit · pinch zoom · 2 fingers pan · fight keeps playing';
    bar.appendChild(status);
    btn('SAVE TAKE', () => {
      const take = this.saveTake();
      status.textContent = `Saved take: ${take.name} (new take — authored camera untouched)`;
    });
    btn('BACK TO AUTHORED', () => this.exit());
    document.body.appendChild(bar);
    this._ui = bar;
  }
}

/* One FreeCamera per game. No key is hijacked, so it can never collide with Photo Mode (P/F9) or fight inputs.
   ENTRY POINT (owner 2026-10-31: the button "is always covering up stuff ... the main menu and the character
   select menu and in the fight in the arena select ... should only be there where it's appropriate"): there is
   NO free-floating button any more. The camera is entered from the fight's PAUSE menu (menus.js, FREE CAMERA),
   the way fighting games put camera/photo tools behind pause, and left with its own BACK TO AUTHORED button or
   automatically when the fight ends. */
export function installFreeCamera(game) {
  if (game.freeCamera) return game.freeCamera;
  const fc = new FreeCamera(game);
  game.freeCamera = fc;
  fc._toggle = null;
  return fc;
}
