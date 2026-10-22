/* ============================================================
   WESTERN HEART — Replays (worker 29, 2026-10-22)
   Deterministic fight replays: a resolved fighter-call log plus one
   snapshot per round — NOT video. Re-simulation replays the exact
   fight: same inputs, same ticks, same outcome.

   Why resolved calls instead of raw inputs: the engine's input
   resolution (TekkenBuffer motion windows, input.js chord timing)
   depends on wall-clock (performance.now) and per-tick direction
   history. Recording the RESOLVED fighter calls (setStick/tryMove/
   tryAttack/... — the exact calls Game._update makes) makes the
   replay a pure function of (snapshot, call log): fully
   deterministic, immune to wall-clock. Fighter internals are
   deterministic given the call sequence (all Math.random/
   performance.now uses in fighter.js are visual-only: aura
   particles, trail pulses — verified 2026-10-22).

   • ReplayRecorder — attaches to a live Game, monkey-patches the two
     fighters' intent methods, logs per-tick calls + per-round
     snapshots. Auto-saves to the library when the match ends.
   • ReplayPlayer — drives a Game from a replay: feeds recorded calls
     per tick (no input, no AI), handles round transitions from
     snapshots, transport controls (play/pause/slow-mo/frame-step/
     scrub), free camera.
   • FreeCam — orbit camera shared by the replay viewer and the
     Gungaku fight lab (js/training.js).
   • Library wrappers over localStorage (see replay-codec.js).

   Teardown grounding: T7's replay theater (input-log + chapter
   select), TTT2's replay chapter skip, DOA5's slow-mo viewer —
   combined: transport + slow-mo + free camera + library.
   ============================================================ */
import * as THREE from 'three';
import {
  REPLAY_VERSION, LIB_MAX,
  snapFighter, restoreFighter, indexCallsByTick, sameArgs,
  listReplays as _list, saveReplay as _save, getReplay as _get,
  deleteReplay as _del, makeMeta,
} from './replay-codec.js';
import { getRealMove } from './fighter.js';

const FIXED_DT = 1 / 120; // mirrors game.js FIXED_DT (not exported there)

/* Fighter intent methods the recorder taps. Continuous ones
   (called every tick) are logged on change only; event ones always. */
const PATCH_METHODS = [
  'setStick', 'tryMove', 'tryJump', 'tryBlock', 'tryCrouch',
  'trySidestep', 'tryDodge', 'tryTransform', 'tryThrowBreak', 'tryAttack',
];
const CONTINUOUS = { setStick: 1, tryMove: 1, tryBlock: 1, tryCrouch: 1 };

/* Storage shim: localStorage in the browser, guarded (private mode). */
function storage() {
  try {
    if (typeof localStorage !== 'undefined') return localStorage;
  } catch (e) { /* fall through */ }
  return null;
}
const _memStore = (() => {
  const m = new Map();
  return {
    getItem: (k) => (m.has(k) ? m.get(k) : null),
    setItem: (k, v) => { m.set(k, String(v)); },
    removeItem: (k) => { m.delete(k); },
  };
})();
function store() { return storage() || _memStore; }

export const listReplays = () => _list(store());
export const getReplay = (id) => _get(store(), id);
export const deleteReplay = (id) => _del(store(), id);
export function saveReplayToLibrary(data) { return _save(store(), data); }

/* ============================================================
   ReplayRecorder
   ============================================================ */
export class ReplayRecorder {
  static attach(game, metaOpts) {
    const r = new ReplayRecorder(game, metaOpts);
    game._recorder = r;
    return r;
  }

  constructor(game, metaOpts = {}) {
    this.game = game;
    this.meta = makeMeta({
      p1id: game.p1.char.id, p2id: game.p2.char.id,
      p1name: game.p1.char.name, p2name: game.p2.char.name,
      stageId: game._stageId, stageName: game._stageName,
      mode: metaOpts.mode || 'versus',
      winner: null,
    });
    this.rounds = [];
    this.cur = null;
    this.capped = false;
    this.stopped = false;
    this._last = { p1: {}, p2: {} };
    this._tick = () => this._onTick();
    game._tickHooks.push(this._tick);
    this._patch(game.p1, 'p1');
    this._patch(game.p2, 'p2');
    console.log('[WH] replay recorder attached');
  }

  _onTick() {
    if (this.stopped || this.capped) return;
    const g = this.game;
    if (g.roundState !== 'fight' || !g.p1 || !g.p2) return;
    if (!this.cur || this.cur.round !== g.round) this._beginRound();
  }

  _beginRound() {
    const g = this.game;
    if (this.rounds.length >= 3) { this.capped = true; return; } // endless modes: cap at 3 rounds
    this.cur = {
      round: g.round,
      tick0: g.tick,
      endTick: 0,
      snapshot: {
        tick: g.tick,
        timer: g.timer,
        round: g.round,
        wins: { ...g.wins },
        p1: snapFighter(g.p1),
        p2: snapFighter(g.p2),
      },
      calls: [],
    };
    this.rounds.push(this.cur);
    this._last = { p1: {}, p2: {} }; // continuous baselines re-arm per round
  }

  _patch(f, who) {
    const rec = this;
    f._replayOrig = f._replayOrig || {};
    for (const m of PATCH_METHODS) {
      if (typeof f[m] !== 'function' || f._replayOrig[m]) continue;
      const orig = f[m].bind(f);
      f._replayOrig[m] = orig;
      f[m] = function (...args) {
        if (m === 'tryAttack') {
          const before = f.attackName;
          const ok = orig(...args);
          const fired = (ok && f.attackName !== before) ? f.attackName : null;
          if (rec.cur && !rec.capped && !rec.stopped) {
            rec.cur.calls.push([rec.game.tick - rec.cur.tick0, who, m, args[0], ok ? 1 : 0, fired]);
          }
          return ok;
        }
        let keep = true;
        if (CONTINUOUS[m]) {
          const key = args; // compared element-wise
          if (sameArgs(rec._last[who][m], key)) keep = false;
          else rec._last[who][m] = key.slice ? key.slice() : key;
        }
        const r = orig(...args);
        if (keep && rec.cur && !rec.capped && !rec.stopped) {
          rec.cur.calls.push([rec.game.tick - rec.cur.tick0, who, m, ...args]);
        }
        return r;
      };
    }
  }

  _unpatch() {
    for (const f of [this.game.p1, this.game.p2]) {
      if (!f || !f._replayOrig) continue;
      for (const [m, orig] of Object.entries(f._replayOrig)) f[m] = orig;
      delete f._replayOrig;
    }
    const ix = this.game._tickHooks.indexOf(this._tick);
    if (ix >= 0) this.game._tickHooks.splice(ix, 1);
  }

  /** Match ended normally — finalize, stamp the winner, auto-save. */
  finish() {
    if (this.stopped) return null;
    this.stopped = true;
    const g = this.game;
    for (const r of this.rounds) r.endTick = Math.max(r.endTick, g.tick - r.tick0);
    if (this.cur) this.cur.endTick = Math.max(this.cur.endTick, g.tick - this.cur.tick0);
    this._unpatch();
    if (g._recorder === this) g._recorder = null;
    this.meta.winner = g.wins.p1 > g.wins.p2 ? 'p1' : g.wins.p2 > g.wins.p1 ? 'p2' : 'draw';
    const data = this.toData();
    const entry = saveReplayToLibrary(data);
    console.log('[WH] replay saved:', this.meta.id, entry ? `${(entry.bytes / 1024).toFixed(0)}KB` : '(library full/denied)');
    return entry;
  }

  /** Match abandoned (quit to menu) — drop everything. */
  discard() {
    if (this.stopped) return;
    this.stopped = true;
    this._unpatch();
    if (this.game._recorder === this) this.game._recorder = null;
  }

  toData() {
    return { v: REPLAY_VERSION, meta: this.meta, rounds: this.rounds };
  }
}

/* ============================================================
   ReplayPlayer
   ============================================================ */
export class ReplayPlayer {
  constructor(data, ui = null) {
    this.data = data;
    this.ui = ui;
    this.roundIdx = 0;
    this.ended = false;
    this.scrubbing = false;
    this._byTick = data.rounds.map((r) => indexCallsByTick(r.calls));
    this._bar = null; // transport bar element (wired by UI layer)
    this.onExit = null;
  }

  /** Drive an already-started Game (fighters built) from this replay. */
  attach(game) {
    this.game = game;
    game.replay = this;
    game.training = false;
    game.onMatchEnd = null;
    game.timeScale = 1;
    // Note: no _tickHooks registration — Game._update calls applyTick
    // explicitly in its replay branch (single application point, also
    // used by scrub and frame-step which drive _update directly).
    this._startRound(0);
    console.log('[WH] replay playing:', this.data.meta.id);
    return this;
  }

  detach() {
    const g = this.game;
    if (!g) return;
    if (g.replay === this) g.replay = null;
    g.timeScale = 1;
    this.game = null;
  }

  _startRound(i) {
    const g = this.game;
    const rd = this.data.rounds[i];
    this.roundIdx = i;
    restoreGameSnapshot(g, rd.snapshot);
    g.roundState = 'fight';
    g.input.enable(false);
    if (this.ui && this.ui.banner) this.ui.banner(`REPLAY — ROUND ${rd.round}`);
    this._updateTime();
  }

  /* Drive one fixed-step tick from the recorded call log. Called by
     Game._update (registered tick hook) and by scrub/step. */
  applyTick(tick) {
    if (this.ended) return;
    const g = this.game;
    if (!g || g.roundState !== 'fight') return;
    const rd = this.data.rounds[this.roundIdx];
    const t = tick - rd.snapshot.tick;
    const calls = this._byTick[this.roundIdx].get(t);
    // NOTE: scrub drives _update in a loop with scrubbing=true — calls
    // must still apply (that IS the re-simulation); only the transport
    // readout and audio are suppressed while scrubbing.
    if (calls) for (const c of calls) this._applyCall(c);
    if (!this.scrubbing && (this._timeFrame = (this._timeFrame || 0) + 1) % 12 === 0) this._updateTime();
  }

  _applyCall(c) {
    const g = this.game;
    const who = c[1], m = c[2];
    const f = who === 'p1' ? g.p1 : g.p2;
    if (!f) return;
    if (m === 'tryAttack') {
      const name = c[3], ok = c[4], fired = c[5];
      if (!ok) return;
      if (fired) {
        // Resolved at record time — fire directly, no TekkenBuffer
        // re-resolution (its motion windows use wall-clock).
        if (typeof f.replayMove === 'function') f.replayMove(fired, name);
        else f.tryAttack(name);
        if (!this.scrubbing) {
          if (name === 'surge') g.surgePresentation(f);
        }
      } else {
        f.tryAttack(name); // buffered/string path — pure state, deterministic
      }
      return;
    }
    f[m](...c.slice(3));
  }

  /* Game._afterRound delegates here while a replay drives. */
  onAfterRound() {
    if (this.ended || this.scrubbing) return;
    if (this.roundIdx + 1 < this.data.rounds.length) {
      this._startRound(this.roundIdx + 1);
    } else {
      this._finish();
    }
  }

  _finish() {
    this.ended = true;
    const g = this.game;
    g.roundState = 'idle';
    if (this.ui && this.ui.banner) this.ui.banner('REPLAY END');
    if (this.onReplayEnd) this.onReplayEnd();
  }

  restart() {
    this.ended = false;
    this._startRound(0);
  }

  /* --- transport --- */
  setPaused(on) { if (this.game) this.game.pause(on); this._updatePlayBtn(); }
  togglePause() { if (this.game) this.setPaused(!this.game.paused); }
  setSpeed(s) { if (this.game) this.game.timeScale = s; this._updateSpeedBtns(); }
  stepFrames(n = 1) {
    const g = this.game;
    if (!g || this.ended) return;
    const wasPaused = g.paused;
    g.pause(true);
    for (let i = 0; i < n; i++) {
      if (g._hitStop > 0) { g._hitStop -= FIXED_DT; continue; }
      g._update(FIXED_DT);
    }
    g.pause(wasPaused && false); // stay paused after stepping
    g.pause(true);
    this._updateTime();
    this._updatePlayBtn();
  }

  /* Scrub within the current round: restore the round snapshot and
     re-simulate forward to the target tick (deterministic). */
  scrub(tickTarget) {
    const g = this.game;
    if (!g || this.ended) return;
    const rd = this.data.rounds[this.roundIdx];
    const target = Math.max(0, Math.min(tickTarget | 0, rd.endTick || 0));
    this.scrubbing = true;
    const wasPaused = g.paused;
    g.pause(true);
    restoreGameSnapshot(g, rd.snapshot);
    g.roundState = 'fight';
    let guard = target + 120; // never spin forever
    while ((g.tick - rd.snapshot.tick) < target && guard-- > 0) {
      if (g._hitStop > 0) { g._hitStop -= FIXED_DT; continue; }
      g._update(FIXED_DT);
      if (g.roundState !== 'fight') break; // KO crossed — stop at the boundary
    }
    this.scrubbing = false;
    g.pause(true);
    if (this.ui) {
      this.ui.updateHP(g.p1, g.p2);
      this.ui.updateMeter(g.p1, g.p2);
      this.ui.setRounds(g.wins);
    }
    this._updateTime();
    this._updatePlayBtn();
    void wasPaused;
  }

  _updateTime() {
    if (!this._timeEl || !this.game) return;
    const rd = this.data.rounds[this.roundIdx];
    const t = Math.max(0, this.game.tick - rd.snapshot.tick);
    const total = Math.max(1, rd.endTick || 1);
    const fmt = (tk) => `${Math.floor(tk / 7200)}:${String(Math.floor(tk / 120) % 60).padStart(2, '0')}`;
    this._timeEl.textContent = `R${this.roundIdx + 1}/${this.data.rounds.length} ${fmt(t)} / ${fmt(total)}`;
    if (this._seekEl) {
      this._seekEl.max = total;
      if (document.activeElement !== this._seekEl) this._seekEl.value = t;
    }
  }
  _updatePlayBtn() {
    if (this._playBtn && this.game) this._playBtn.textContent = this.game.paused ? '▶' : '⏸';
  }
  _updateSpeedBtns() {
    if (!this._bar || !this.game) return;
    this._bar.querySelectorAll('[data-speed]').forEach((b) => {
      b.classList.toggle('on', parseFloat(b.dataset.speed) === this.game.timeScale);
    });
  }
}

/* Restore a full game snapshot (round start). */
export function restoreGameSnapshot(g, s) {
  g.tick = s.tick;
  g.timer = s.timer;
  g.round = s.round;
  g.wins = { ...s.wins };
  g._hitStop = 0;
  g._acc = 0;
  restoreFighter(g.p1, s.p1, getRealMove);
  restoreFighter(g.p2, s.p2, getRealMove);
  g.ui.setRounds(g.wins);
  g.ui.setTimer(Math.ceil(g.timer));
  g.ui.updateHP(g.p1, g.p2);
  g.ui.updateMeter(g.p1, g.p2);
}

/* ============================================================
   FreeCam — orbit camera for replay viewer + Gungaku lab.
   The Arena skips its auto-framing while arena.freeCam is set
   (scene.js); this controller drives arena.camera directly.
   Drag = orbit, wheel / pinch = zoom. Double-click resets.
   ============================================================ */
export class FreeCam {
  constructor(arena) {
    this.arena = arena;
    this.enabled = false;
    this.theta = 0;      // orbit angle around the fighters
    this.phi = 0.32;     // elevation
    this.dist = 7.5;
    this.target = new THREE.Vector3(0, 1.0, 0);
    this._bound = false;
  }

  setEnabled(on) {
    this.enabled = on;
    this.arena.freeCam = on;
    if (on) this._bind();
    else this._unbind();
  }

  _bind() {
    if (this._bound) return;
    this._bound = true;
    const cv = this.arena.renderer.domElement;
    let dragging = false, lx = 0, ly = 0, pinchD = 0;
    this._down = (e) => { dragging = true; lx = e.clientX; ly = e.clientY; };
    this._move = (e) => {
      if (!dragging || !this.enabled) return;
      this.theta -= (e.clientX - lx) * 0.008;
      this.phi = Math.max(0.05, Math.min(1.35, this.phi + (e.clientY - ly) * 0.006));
      lx = e.clientX; ly = e.clientY;
    };
    this._up = () => { dragging = false; };
    this._wheel = (e) => {
      if (!this.enabled) return;
      e.preventDefault();
      this.dist = Math.max(2.5, Math.min(20, this.dist + e.deltaY * 0.01));
    };
    this._dbl = () => { this.theta = 0; this.phi = 0.32; this.dist = 7.5; };
    this._touch = (e) => {
      if (!this.enabled || e.touches.length !== 2) return;
      const d = Math.hypot(
        e.touches[0].clientX - e.touches[1].clientX,
        e.touches[0].clientY - e.touches[1].clientY);
      if (pinchD > 0) this.dist = Math.max(2.5, Math.min(20, this.dist - (d - pinchD) * 0.02));
      pinchD = d;
    };
    this._touchEnd = () => { pinchD = 0; };
    cv.addEventListener('pointerdown', this._down);
    window.addEventListener('pointermove', this._move);
    window.addEventListener('pointerup', this._up);
    cv.addEventListener('wheel', this._wheel, { passive: false });
    cv.addEventListener('dblclick', this._dbl);
    cv.addEventListener('touchmove', this._touch, { passive: true });
    cv.addEventListener('touchend', this._touchEnd);
  }

  _unbind() {
    if (!this._bound) return;
    this._bound = false;
    const cv = this.arena.renderer.domElement;
    cv.removeEventListener('pointerdown', this._down);
    window.removeEventListener('pointermove', this._move);
    window.removeEventListener('pointerup', this._up);
    cv.removeEventListener('wheel', this._wheel);
    cv.removeEventListener('dblclick', this._dbl);
    cv.removeEventListener('touchmove', this._touch);
    cv.removeEventListener('touchend', this._touchEnd);
  }

  /** Call every frame with the two fighters (either may be null). */
  update(p1, p2) {
    if (!this.enabled) return;
    const cam = this.arena.camera;
    let tx = 0, ty = 1.0, tz = 0;
    if (p1 && p2) {
      tx = (p1.root.position.x + p2.root.position.x) / 2;
      ty = 1.0 + Math.max(p1.root.position.y, p2.root.position.y) * 0.5;
      tz = (p1.root.position.z + p2.root.position.z) / 2;
    } else if (p1) {
      tx = p1.root.position.x; tz = p1.root.position.z;
    }
    const k = 1 - Math.min(1, 0.016 * 6);
    this.target.x += (tx - this.target.x) * (1 - k);
    this.target.y += (ty - this.target.y) * (1 - k);
    this.target.z += (tz - this.target.z) * (1 - k);
    const sp = Math.sin(this.phi), cp = Math.cos(this.phi);
    cam.position.set(
      this.target.x + Math.sin(this.theta) * cp * this.dist,
      this.target.y + sp * this.dist,
      this.target.z + Math.cos(this.theta) * cp * this.dist
    );
    cam.lookAt(this.target);
  }
}
