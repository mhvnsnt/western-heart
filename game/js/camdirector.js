/* ============================================================
   WESTERN HEART — WHCamDirector (camera-controls cutscene camera)
   Vendored: game/vendor/camera-controls/camera-controls.module.js
   (MIT, yomotsu/camera-controls). Loaded lazily by integration.js.

   The fight camera is untouched. This director is opt-in for:
   - real-time rendered cutscenes (owner directive 2026-10-22):
     shot lists with smooth setLookAt transitions,
   - creation-suite photo mode: damped orbit rig around the model.

   Shots: { pos:[x,y,z], target:[x,y,z], dolly?:number, hold?:seconds,
            transition?:seconds }. playCutscene(shots, {onDone}).
   ============================================================ */

import * as THREE from 'three';

let CC = null;
async function loadCC(THREE_NS) {
  if (CC) return CC;
  CC = await import('camera-controls');
  CC.default.install({ THREE: THREE_NS });
  return CC;
}

export class WHCamDirector {
  constructor() {
    this.ready = false;
    this.controls = null;
    this.camera = null;
    this._queue = [];
    this._hold = 0;
    this._onDone = null;
    this._saved = null;
  }

  async init(camera, domElement) {
    const mod = await loadCC(THREE);
    this.camera = camera;
    this.controls = new mod.default(camera, domElement);
    this.controls.smoothTime = 0.35;
    this.ready = true;
    return this;
  }

  /** Take over the camera (saves current transform for release()). */
  takeOver() {
    if (!this.ready || this._saved) return;
    this._saved = {
      pos: this.camera.position.clone(),
      quat: this.camera.quaternion.clone(),
    };
    this.controls.enabled = true;
  }

  /** Give the camera back to whoever owned it. */
  release() {
    if (!this.ready) return;
    this.controls.enabled = false;
    this._queue = [];
    this._onDone = null;
    if (this._saved) {
      this.camera.position.copy(this._saved.pos);
      this.camera.quaternion.copy(this._saved.quat);
      this._saved = null;
    }
  }

  /** Play a cutscene shot list. */
  playCutscene(shots, { onDone = null, loop = false } = {}) {
    if (!this.ready) return false;
    this.takeOver();
    this._queue = shots.map((s) => ({ ...s }));
    this._onDone = onDone;
    this._loop = loop;
    this._hold = 0;
    this._next();
    return true;
  }

  _next() {
    const shot = this._queue.shift();
    if (!shot) {
      if (this._loop && this._shots0) { this._queue = this._shots0.map((s) => ({ ...s })); return this._next(); }
      const cb = this._onDone;
      this._onDone = null;
      this.release();
      cb && cb();
      return;
    }
    if (!this._shots0) this._shots0 = [shot];
    else if (this._loop) this._shots0.push(shot);
    const t = shot.transition ?? 1.2;
    this.controls.setLookAt(
      shot.pos[0], shot.pos[1], shot.pos[2],
      shot.target[0], shot.target[1], shot.target[2],
      t > 0);
    if (shot.dolly) this.controls.dolly(shot.dolly, t > 0);
    this._hold = shot.hold ?? 2.0;
    this._transition = t;
  }

  /** Photo-mode rig: damped orbit around a target point. */
  photoMode(target = [0, 1.2, 0], distance = 3.2) {
    if (!this.ready) return false;
    this.takeOver();
    this.controls.setLookAt(
      target[0] + distance * 0.7, target[1] + 0.6, target[2] + distance * 0.7,
      target[0], target[1], target[2], false);
    this.controls.minDistance = 1.2;
    this.controls.maxDistance = 8;
    this.controls.maxPolarAngle = Math.PI * 0.55;
    return true;
  }

  update(dt) {
    if (!this.ready || !this.controls.enabled) return;
    if (this._queue.length || this._hold > 0) {
      if (this._hold > 0) {
        this._hold -= dt;
        if (this._hold <= 0) this._next();
      }
    }
    this.controls.update(dt);
  }
}
