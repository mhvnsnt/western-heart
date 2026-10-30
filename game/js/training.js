/* ============================================================
   WESTERN HEART — GUNGAKU 軍楽 FIGHT LAB (worker 29, 2026-10-22)
   "War music" — the user-locked name for the programmable training
   dummy mode (TTT2 Combot equivalent).

   Training-mode depth, attached to a live Game in training mode:
   • Frame data display — live readout of the current/last move
     (startup / active / recovery in frames, damage), pulled from the
     move's resolved data (game/js/fighter.js getRealMove — real T3
     teardown frame data, not hand-written).
   • Dummy controls — STAND / CROUCH / BLOCK / JUMP behaviors driven
     by a TrainingDummy that replaces the AIController (same
     update(dt, player) interface, so Game._update needs no changes).
   • Record / playback — record the PLAYER's inputs, play them back
     on the dummy, looped (T7 practice-record style). Raw inputs are
     re-resolved against the dummy's own moveset, like T7.
   • Hitbox viewer — real-time attack/hurt box visualization built on
     the hitbox system (fighter.js getHitbox/getHurtboxes): red
     wireframe = active attack box, green wireframe = hurtboxes.
   • Reset positions — both fighters back to spawn (positions/state;
     HP untouched unless someone is down).
   • Free camera — orbit/zoom while labbing (shared FreeCam in
     js/replay.js).

   Teardown grounding: T7 practice mode (dummy settings, command
   display, frame data), TTT2 Combot (programmable/recordable dummy),
   DOA (move details), SCVI (frame-data overlay) — combined.
   ============================================================ */
import * as THREE from 'three';
import { getStage } from './stages.js';
import { snapFighter, restoreFighter, indexCallsByTick, sameArgs } from './replay-codec.js';
import { FreeCam } from './replay.js';
import { getRealMove } from './fighter.js';

/* Dummy behaviors (the task's required set). */
export const DUMMY_BEHAVIORS = ['stand', 'crouch', 'block', 'jump'];

/* ============================================================
   TrainingDummy — replaces AIController in the lab.
   Same interface: update(dt, player). Faces the player every tick.
   ============================================================ */
export class TrainingDummy {
  constructor(fighter, behavior = 'stand') {
    this.f = fighter;
    this.behavior = behavior;
    this._t = 0;
  }

  _face(player) {
    const f = this.f;
    const dx = player.root.position.x - f.root.position.x;
    const want = Math.sign(dx) || 1;
    if (want !== f.facing) {
      f.facing = want;
      f._faceY = (want * Math.PI) / 2;
      f.lean.rotation.y = (want * Math.PI) / 2;
    }
  }

  update(dt, player) {
    const f = this.f;
    if (!f || f.dead) return;
    this._face(player);
    switch (this.behavior) {
      case 'crouch':
        f.tryBlock(false);
        f.setStick('d/b');
        f.tryCrouch(true);
        break;
      case 'block':
        f.tryCrouch(false);
        f.setStick('b');
        f.tryBlock(true);
        break;
      case 'jump':
        f.tryCrouch(false);
        f.tryBlock(false);
        this._t -= dt;
        if (this._t <= 0 && f.canAct && f.canAct()) {
          f.tryJump();
          this._t = 1.4;
        }
        break;
      case 'stand':
      default:
        f.tryCrouch(false);
        f.tryBlock(false);
        break;
    }
  }
}

/* ============================================================
   HitboxViewer — real-time attack/hurt box overlay.
   Red wireframe sphere = active attack hitbox (fighter.getHitbox()).
   Green wireframe spheres = hurtboxes (fighter.getHurtboxes()).
   ============================================================ */
export class HitboxViewer {
  constructor(scene) {
    this.scene = scene;
    this.visible = false;
    this._pool = [];
    const mk = (color) => {
      const m = new THREE.Mesh(
        new THREE.SphereGeometry(1, 12, 10),
        new THREE.MeshBasicMaterial({ color, wireframe: true, transparent: true, opacity: 0.9, depthTest: false })
      );
      m.visible = false;
      m.renderOrder = 999;
      scene.add(m);
      return m;
    };
    // 2 fighters x (1 hitbox + 4 hurtboxes headroom)
    for (let i = 0; i < 10; i++) this._pool.push(mk(i % 5 === 0 ? 0xff2a2a : 0x2aff5a));
    this._hitMeshes = [this._pool[0], this._pool[5]];
    this._hurtMeshes = [this._pool.slice(1, 5), this._pool.slice(6, 10)];
  }

  setVisible(v) {
    this.visible = v;
    if (!v) for (const m of this._pool) m.visible = false;
  }

  update(p1, p2) {
    if (!this.visible) return;
    const fs = [p1, p2];
    for (let i = 0; i < 2; i++) {
      const f = fs[i];
      const hb = f && f.state === 'attack' ? f.getHitbox() : null;
      const hm = this._hitMeshes[i];
      if (hb) {
        hm.visible = true;
        hm.position.set(hb.x, hb.y, hb.z);
        hm.scale.setScalar(Math.max(0.05, hb.r));
      } else hm.visible = false;
      const hurts = f ? f.getHurtboxes() : [];
      const pool = this._hurtMeshes[i];
      for (let j = 0; j < pool.length; j++) {
        const hu = hurts[j];
        const m = pool[j];
        if (hu) {
          m.visible = true;
          m.position.set(hu.x, hu.y, hu.z);
          m.scale.setScalar(Math.max(0.05, hu.r));
        } else m.visible = false;
      }
    }
  }

  dispose() {
    for (const m of this._pool) {
      this.scene.remove(m);
      m.geometry.dispose();
      m.material.dispose();
    }
    this._pool = [];
  }
}

/* ============================================================
   DummyRecorder — records the PLAYER's raw intent calls for the
   lab's record/playback (short loop, T7 practice style). Separate
   from ReplayRecorder (which records resolved match calls): here
   raw inputs are re-resolved live against the dummy's moveset.
   ============================================================ */
const REC_METHODS = [
  'setStick', 'tryMove', 'tryJump', 'tryBlock', 'tryCrouch',
  'trySidestep', 'tryDodge', 'tryTransform', 'tryThrowBreak', 'tryAttack',
];
const REC_CONTINUOUS = { setStick: 1, tryMove: 1, tryBlock: 1, tryCrouch: 1 };
const REC_MAX_TICKS = 120 * 20; // 20 s max

export class DummyRecorder {
  constructor(game) {
    this.game = game;
    this.recording = false;
    this.calls = [];
    this.tick0 = 0;
    this._last = {};
    this._tick = () => this._onTick();
  }

  start() {
    if (this.recording) return;
    this.recording = true;
    this.calls = [];
    this.tick0 = this.game.tick;
    this._last = {};
    this.game._tickHooks.push(this._tick);
    this._patch(this.game.p1);
  }

  stop() {
    if (!this.recording) return [];
    this.recording = false;
    this._unpatch();
    const ix = this.game._tickHooks.indexOf(this._tick);
    if (ix >= 0) this.game._tickHooks.splice(ix, 1);
    return this.calls;
  }

  get totalTicks() {
    if (!this.calls.length) return 0;
    return this.calls[this.calls.length - 1][0] + 1;
  }

  _onTick() {
    if (this.game.tick - this.tick0 > REC_MAX_TICKS) this.stop();
  }

  _patch(f) {
    const rec = this;
    f._labOrig = f._labOrig || {};
    for (const m of REC_METHODS) {
      if (typeof f[m] !== 'function' || f._labOrig[m]) continue;
      const orig = f[m].bind(f);
      f._labOrig[m] = orig;
      f[m] = function (...args) {
        let keep = true;
        if (REC_CONTINUOUS[m]) {
          if (sameArgs(rec._last[m], args)) keep = false;
          else rec._last[m] = args.slice();
        }
        const r = orig(...args);
        if (keep && rec.recording) {
          rec.calls.push([rec.game.tick - rec.tick0, m, ...args]);
        }
        return r;
      };
    }
  }

  _unpatch() {
    const f = this.game.p1;
    if (!f || !f._labOrig) return;
    for (const [m, orig] of Object.entries(f._labOrig)) f[m] = orig;
    delete f._labOrig;
  }
}

/* Playback driver: performs the recorded raw inputs on the dummy,
   looped. Implements the AI update(dt, player) interface. */
export class PlaybackDummy {
  constructor(fighter, calls) {
    this.f = fighter;
    this.byTick = indexCallsByTick(calls);
    this.total = calls.length ? calls[calls.length - 1][0] + 1 : 1;
    this.t = 0;
  }

  update(dt, player) {
    const f = this.f;
    if (!f || f.dead) return;
    const dx = player.root.position.x - f.root.position.x;
    const want = Math.sign(dx) || 1;
    if (want !== f.facing) {
      f.facing = want;
      f._faceY = (want * Math.PI) / 2;
      f.lean.rotation.y = (want * Math.PI) / 2;
    }
    const arr = this.byTick.get(this.t);
    if (arr) {
      for (const c of arr) {
        const m = c[1], args = c.slice(2);
        if (typeof f[m] === 'function') {
          try { f[m](...args); } catch (e) { /* lab tool: never break the fight */ }
        }
      }
    }
    this.t++;
    if (this.t >= this.total) this.t = 0;
  }
}

/* ---------------- frame data ----------------
   Seconds -> frames @60fps (Tekken standard display). */
const f2f = (s) => Math.round((s || 0) * 60);

export function frameDataFor(f) {
  if (!f || f.state !== 'attack' || !f.attack) return null;
  const a = f.attack;
  return {
    input: f.attackName,
    name: a.moveName || a.name || f.attackName,
    phase: f._attackPhase,
    frame: Math.floor(f.stateT * 60) + 1,
    startup: f2f(a.startup),
    active: f2f(a.active),
    recovery: f2f(a.recovery),
    total: f2f((a.startup || 0) + (a.active || 0) + (a.recovery || 0)),
    damage: a.damage,
    t3row: a.t3row,
    t3source: a.t3source,
  };
}

/* ============================================================
   TrainingLab — the GUNGAKU controller.
   ============================================================ */
export class TrainingLab {
  static current = null;

  static attach(game, ui) {
    TrainingLab.detach();
    const lab = new TrainingLab(game, ui);
    TrainingLab.current = lab;
    return lab;
  }

  static detach() {
    if (TrainingLab.current) {
      TrainingLab.current.dispose();
      TrainingLab.current = null;
    }
  }

  constructor(game, ui) {
    this.game = game;
    this.ui = ui;
    this.dummyBehavior = 'stand';
    this.playback = null;   // PlaybackDummy when playing a recording
    this.recorder = null;
    this._origAi = game.ai;

    this.viewer = new HitboxViewer(game.arena.scene);
    this.freecam = new FreeCam(game.arena);

    this._dummy = new TrainingDummy(game.p2, this.dummyBehavior);
    game.ai = this._dummy;

    this._panel = document.getElementById('gungaku');
    this._fdEl = document.getElementById('gk-framedata');
    if (this._panel) this._panel.style.display = 'block';
    const btn = document.getElementById('gungaku-btn');
    if (btn) btn.style.display = 'block';

    this._frame = 0;
    this._tick = () => this._onTick();
    game._tickHooks.push(this._tick);
    this._wirePanel();
    console.log('[WH] Gungaku fight lab attached');
  }

  dispose() {
    const g = this.game;
    const ix = g._tickHooks.indexOf(this._tick);
    if (ix >= 0) g._tickHooks.splice(ix, 1);
    if (this.recorder) this.recorder.stop();
    this.recorder = null;
    this.playback = null;
    if (g.ai === this._dummy || (this._dummyDriverActive && g.ai === this._pbDriver)) {
      g.ai = this._origAi;
    }
    this._dummyDriverActive = false;
    this.viewer.setVisible(false);
    this.viewer.dispose();
    this.freecam.setEnabled(false);
    if (this._panel) this._panel.style.display = 'none';
    const btn = document.getElementById('gungaku-btn');
    if (btn) btn.style.display = 'none';
  }

  /* ---- dummy behavior ---- */
  setDummyBehavior(b) {
    if (!DUMMY_BEHAVIORS.includes(b)) return;
    this.dummyBehavior = b;
    this.playback = null;
    this._dummyDriverActive = false;
    this._dummy.behavior = b;
    this.game.ai = this._dummy;
    this._syncDummyButtons();
    this.ui.banner && this.ui.hudNote(`DUMMY: ${b.toUpperCase()}`);
  }

  /* ---- record / playback ---- */
  toggleRecord() {
    if (this.recorder) {
      const calls = this.recorder.stop();
      this.recorder = null;
      this._syncRecButtons();
      if (calls.length > 4) {
        this.ui.banner && this.ui.hudNote(`RECORDED ${(this._lastTotal / 120).toFixed(1)}s — PRESS PLAY`);
      } else {
        this.ui.banner && this.ui.hudNote('NOTHING RECORDED');
      }
      return;
    }
    this.setDummyBehavior('stand');
    this.recorder = new DummyRecorder(this.game);
    this._lastTotal = 0;
    const origStop = this.recorder.stop.bind(this.recorder);
    this.recorder.stop = () => {
      const calls = origStop();
      this._lastTotal = this.recorder.totalTicks;
      this._lastCalls = calls;
      return calls;
    };
    this.recorder.start();
    this._syncRecButtons();
    this.ui.banner && this.ui.hudNote('● RECORDING DUMMY — FIGHT!');
  }

  togglePlayback() {
    if (this.playback) {
      this.playback = null;
      this._dummyDriverActive = false;
      this.game.ai = this._dummy;
      this._syncRecButtons();
      return;
    }
    const calls = this._lastCalls;
    if (!calls || !calls.length) {
      this.ui.banner && this.ui.hudNote('RECORD SOMETHING FIRST (● REC)');
      return;
    }
    this._pbDriver = new PlaybackDummy(this.game.p2, calls);
    this.playback = this._pbDriver;
    this._dummyDriverActive = true;
    this.game.ai = this._pbDriver;
    this._syncRecButtons();
    this.ui.banner && this.ui.hudNote('▶ DUMMY PLAYBACK (LOOPED)');
  }

  stopAll() {
    if (this.recorder) this.toggleRecord();
    if (this.playback) this.togglePlayback();
  }

  /* ---- hitbox viewer ---- */
  toggleHitboxes() {
    this.viewer.setVisible(!this.viewer.visible);
    const b = document.getElementById('gk-hitbox');
    if (b) {
      b.textContent = `HITBOX: ${this.viewer.visible ? 'ON' : 'OFF'}`;
      b.classList.toggle('on', this.viewer.visible);
    }
  }

  /* ---- free camera ---- */
  toggleCamera() {
    this.freecam.setEnabled(!this.freecam.enabled);
    const b = document.getElementById('gk-cam');
    if (b) {
      b.textContent = `CAM: ${this.freecam.enabled ? 'FREE' : 'FIGHT'}`;
      b.classList.toggle('on', this.freecam.enabled);
    }
  }

  /* ---- reset ---- */
  resetPositions() {
    const g = this.game;
    if (!g.p1 || !g.p2) return;
    const spawns = getStage(g._stageId || 'shrine').spawns;
    const defs = [
      [g.p1, spawns.p1, 1],
      [g.p2, spawns.p2, -1],
    ];
    for (const [f, x, facing] of defs) {
      // T7 training reset: positions + neutral state; HP kept unless down.
      const snap = snapFighter(f);
      snap.pos = [x, 0, 0];
      snap.facing = facing;
      snap.faceY = (facing * Math.PI) / 2;
      snap.leanY = (facing * Math.PI) / 2;
      snap.state = 'idle';
      snap.stateT = 0;
      snap.attackName = null;
      snap.attackNotation = null;
      snap.attackPhase = 'startup';
      snap.hasHit = false;
      snap.vx = 0;
      snap.stun = 0;
      snap.queuedNext = null;
      if (snap.dead || snap.hp <= 0) { snap.dead = false; snap.hp = f.maxHp; }
      restoreFighter(f, snap, getRealMove);
    }
    g.ui.hudNote('RESET — POSITIONS RESTORED');
    g.ui.updateHP(g.p1, g.p2);
  }

  /* ---- per-tick lab work ---- */
  _onTick() {
    const g = this.game;
    if (!g.p1 || !g.p2) return;
    this.viewer.update(g.p1, g.p2);
    this.freecam.update(g.p1, g.p2);
    // Frame-data readout, throttled (every 6 ticks = 20 Hz).
    if ((this._frame++ % 6) === 0) this._renderFrameData();
  }

  _renderFrameData() {
    if (!this._fdEl) return;
    const g = this.game;
    const rows = [];
    for (const [f, tag] of [[g.p1, 'P1'], [g.p2, 'DUMMY']]) {
      const fd = frameDataFor(f);
      if (!fd) {
        rows.push(`<div class="gk-fd-row"><span class="gk-fd-tag">${tag}</span><span class="gk-fd-idle">—</span></div>`);
        continue;
      }
      const total = Math.max(1, fd.total);
      const pct = Math.min(100, Math.round((fd.frame / total) * 100));
      const phaseCls = fd.phase === 'startup' ? 'ph-s' : fd.phase === 'active' ? 'ph-a' : 'ph-r';
      const src = fd.t3source ? ` <span class="gk-fd-src">T3 ${fd.t3source}${fd.t3row != null ? ' r' + fd.t3row : ''}</span>` : '';
      rows.push(
        `<div class="gk-fd-row"><span class="gk-fd-tag">${tag}</span>` +
        `<span class="gk-fd-name">${fd.input} · ${fd.name}${src}</span></div>` +
        `<div class="gk-fd-bar"><div class="gk-fd-fill ${phaseCls}" style="width:${pct}%"></div></div>` +
        `<div class="gk-fd-nums"><span class="${phaseCls}">${fd.phase.toUpperCase()} ${fd.frame}f</span>` +
        `<span>S ${fd.startup}</span><span>A ${fd.active}</span><span>R ${fd.recovery}</span>` +
        `<span>${fd.damage ?? '?'} dmg</span></div>`
      );
    }
    this._fdEl.innerHTML = rows.join('');
  }

  /* ---- panel wiring ---- */
  _wirePanel() {
    const q = (s) => this._panel && this._panel.querySelector(s);
    const qa = (s) => (this._panel ? [...this._panel.querySelectorAll(s)] : []);
    qa('[data-dummy]').forEach((b) => {
      b.addEventListener('click', () => this.setDummyBehavior(b.dataset.dummy));
    });
    const rec = q('#gk-rec');
    if (rec) rec.addEventListener('click', () => this.toggleRecord());
    const play = q('#gk-play');
    if (play) play.addEventListener('click', () => this.togglePlayback());
    const stop = q('#gk-stop');
    if (stop) stop.addEventListener('click', () => this.stopAll());
    const hb = q('#gk-hitbox');
    if (hb) hb.addEventListener('click', () => this.toggleHitboxes());
    const cam = q('#gk-cam');
    if (cam) cam.addEventListener('click', () => this.toggleCamera());
    const rst = q('#gk-reset');
    if (rst) rst.addEventListener('click', () => this.resetPositions());
    this._syncDummyButtons();
    this._syncRecButtons();
  }

  _syncDummyButtons() {
    if (!this._panel) return;
    this._panel.querySelectorAll('[data-dummy]').forEach((b) => {
      b.classList.toggle('on', b.dataset.dummy === this.dummyBehavior && !this.playback);
    });
  }

  _syncRecButtons() {
    if (!this._panel) return;
    const rec = this._panel.querySelector('#gk-rec');
    const play = this._panel.querySelector('#gk-play');
    if (rec) {
      rec.textContent = this.recorder ? '■ STOP' : '● REC';
      rec.classList.toggle('rec-on', !!this.recorder);
    }
    if (play) {
      play.textContent = this.playback ? '❚❚ PLAYING' : '▶ PLAY';
      play.classList.toggle('on', !!this.playback);
    }
  }
}
