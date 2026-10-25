/* ============================================================
   WESTERN HEART — WHCinematicDirector (Track 7, 2026-10-23)
   Cinematic direction for story mode + Heart and Mind Within:
   keyframe timeline sequences, narrative branches, event flags,
   dialogue prompts, and timeline triggers.

   Open-source lineage (see docs/research/CUTSCENE-STORY-2026-10-23.md):
     • Sequence engine follows Theatre.js core concepts
       (@theatre/core, Apache-2.0): Project -> Sheet -> SheetObject ->
       Sequence; typed props, keyframed values, onValuesChange, scrub.
       Studio editor (@theatre/studio, AGPL-3.0) is NOT shipped — the
       game consumes sequences authored in data, exactly like the
       runtime-only Theatre pattern.
     • Trigger graph follows Godot Orchestrator patterns
       (Godot Orchestrator, MIT): event nodes (flag/proximity/timer/
       dialogue/combat) wired to action nodes (play sequence, dialogue
       prompt, set flag, call function).
     • Branching narrative runs on ink/inkjs (inkle ink MIT,
       inkjs MIT): compiled .ink.json stories via the vendored runtime
       game/vendor/inkjs/ink.mjs. Writer tool: Inky.

   Node-testable: no static three.js import. Camera/object targets are
   plain {position:{x,y,z}} duck types; the game passes THREE objects.
   ============================================================ */

const EASE = {
  linear: (t) => t,
  smooth: (t) => t * t * (3 - 2 * t),
  easeIn: (t) => t * t,
  easeOut: (t) => 1 - (1 - t) * (1 - t),
  easeInOut: (t) => (t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2),
};

function _getPath(obj, path) {
  const parts = path.split('.');
  let cur = obj;
  for (const p of parts) {
    if (cur == null) return undefined;
    cur = cur[p];
  }
  return cur;
}
function _setPath(obj, path, value) {
  const parts = path.split('.');
  let cur = obj;
  for (let i = 0; i < parts.length - 1; i++) {
    if (cur[parts[i]] == null) cur[parts[i]] = {};
    cur = cur[parts[i]];
  }
  cur[parts[parts.length - 1]] = value;
}
function _lerp(a, b, t) {
  if (typeof a === 'number' && typeof b === 'number') return a + (b - a) * t;
  if (Array.isArray(a) && Array.isArray(b)) return a.map((v, i) => _lerp(v, b[i], t));
  return t < 0.5 ? a : b;
}

/* ---------------- WHSequence: Theatre-style keyframe timeline --- */
/* keyframes: { propPath: [ { t, value, ease? }, ... ] } (t in seconds) */
export class WHSequence {
  constructor(name = 'seq') {
    this.name = name;
    this.tracks = {};      // propPath -> sorted keyframes
    this.length = 0;
    this.time = 0;
    this.playing = false;
    this.iterationCount = 1;
    this._iter = 0;
    this._onDone = null;
    this._onValues = new Map(); // target -> Set<cb>
  }
  addTrack(propPath, keyframes) {
    const kf = [...keyframes].sort((a, b) => a.t - b.t);
    this.tracks[propPath] = kf;
    if (kf.length) this.length = Math.max(this.length, kf[kf.length - 1].t);
    return this;
  }
  onValuesChange(target, cb) {
    if (!this._onValues.has(target)) this._onValues.set(target, new Set());
    this._onValues.get(target).add(cb);
    return () => this._onValues.get(target).delete(cb);
  }
  _applyAt(target, time) {
    const values = {};
    for (const [path, kf] of Object.entries(this.tracks)) {
      if (!kf.length) continue;
      let v;
      if (time <= kf[0].t) v = kf[0].value;
      else if (time >= kf[kf.length - 1].t) v = kf[kf.length - 1].value;
      else {
        let i = 0;
        while (i < kf.length - 2 && kf[i + 1].t <= time) i++;
        const a = kf[i], b = kf[i + 1];
        const ease = EASE[(b.ease || a.ease) || 'smooth'] || EASE.smooth;
        v = _lerp(a.value, b.value, ease((time - a.t) / (b.t - a.t)));
      }
      _setPath(target, path, v);
      values[path] = v;
    }
    const cbs = this._onValues.get(target);
    if (cbs) for (const cb of cbs) { try { cb(values, time); } catch { /* non-fatal */ } }
  }
  play(target, { onDone = null, iterationCount = 1, from = 0 } = {}) {
    this.time = from;
    this._iter = 0;
    this.iterationCount = iterationCount;
    this._onDone = onDone;
    this.playing = true;
    this._applyAt(target, this.time);
    this._target = target;
    return this;
  }
  pause() { this.playing = false; return this; }
  resume() { this.playing = true; return this; }
  seek(target, t) { this.time = Math.max(0, Math.min(this.length, t)); this._applyAt(target, this.time); return this; }
  stop() { this.playing = false; this.time = 0; return this; }
  update(dt) {
    if (!this.playing || !this._target) return;
    this.time += dt;
    if (this.time >= this.length) {
      this._iter++;
      if (this._iter >= this.iterationCount) {
        this._applyAt(this._target, this.length);
        this.playing = false;
        const cb = this._onDone; this._onDone = null;
        if (cb) cb(this);
        return;
      }
      this.time = this.time % this.length;
    }
    this._applyAt(this._target, this.time);
  }
}

/* ---------------- WHSheet / WHProject: Theatre-style containers - */
export class WHSheet {
  constructor(name) { this.name = name; this.objects = {}; this.sequence = new WHSequence(name); }
  object(name, defaults = {}) { this.objects[name] = { ...defaults }; return this.objects[name]; }
}
export class WHProject {
  constructor(name) { this.name = name; this.sheets = {}; }
  sheet(name) { if (!this.sheets[name]) this.sheets[name] = new WHSheet(name); return this.sheets[name]; }
}

/* ---------------- WHTriggerGraph: Orchestrator-style events ------ */
/* Trigger: { id, when: {flag?, zone?, timer?, dialogue?, combat?},
              do: [ {action:'play'|'dialogue'|'flag'|'fn', ...} ] } */
export class WHTriggerGraph {
  constructor() {
    this.flags = {};
    this.triggers = [];
    this._timers = new Map();
    this._fired = new Set(); // one-shot by default
    this.onDialogue = null;  // (prompt) => void — game wires to beat UI
    this.onAction = null;    // ({trigger, action}) => void — game observes
  }
  setFlag(name, value = true) { this.flags[name] = value; }
  getFlag(name) { return this.flags[name]; }
  addTrigger(tr) {
    const t = { once: true, enabled: true, ...tr };
    if (t.when && t.when.timer != null) this._timers.set(t.id || Symbol(), t.when.timer);
    this.triggers.push(t);
    return t;
  }
  removeTrigger(id) { this.triggers = this.triggers.filter((t) => t.id !== id); }
  /* ctx: { playerPos:{x,y,z}, combatEvent?, dt } */
  update(dt, ctx = {}) {
    for (const t of this.triggers) {
      if (!t.enabled) continue;
      if (t.once && this._fired.has(t)) continue;
      if (!this._whenMet(t, dt, ctx)) continue;
      this._fired.add(t);
      for (const a of (t.do || [])) this._runAction(a, t, ctx);
    }
  }
  _whenMet(t, dt, ctx) {
    const w = t.when || {};
    if (w.flag != null) { const [n, v = true] = Array.isArray(w.flag) ? w.flag : [w.flag]; if (this.flags[n] !== v) return false; }
    if (w.zone && ctx.playerPos) {
      const z = w.zone; const dx = ctx.playerPos.x - z.x, dz = ctx.playerPos.z - (z.z || 0);
      if (Math.hypot(dx, dz) > (z.r || 2)) return false;
    }
    if (w.timer != null) {
      const left = (this._timers.get(t.id) ?? w.timer) - dt;
      this._timers.set(t.id, left);
      if (left > 0) return false;
    }
    if (w.dialogueChoice) { if ((this.flags.__choice || null) !== w.dialogueChoice) return false; }
    if (w.combat && ctx.combatEvent !== w.combat) return false;
    return true;
  }
  _runAction(a, trigger, ctx) {
    if (this.onAction) { try { this.onAction({ trigger, action: a, ctx }); } catch { /* non-fatal */ } }
    switch (a.action) {
      case 'flag': this.setFlag(a.name, a.value !== undefined ? a.value : true); break;
      case 'dialogue': if (this.onDialogue) this.onDialogue(a.prompt, trigger); break;
      case 'fn': if (typeof a.fn === 'function') a.fn(ctx, this); break;
      /* 'play' (sequence) is handled by the director, which sees onAction */
    }
  }
  reset() { this._fired.clear(); this._timers.clear(); }
}

/* ---------------- WHCinematicDirector --------------------------- */
/* Owns projects, the trigger graph, and ink narrative. update(dt)
   advances active sequences + triggers. Dialogue renders through
   onDialogue (game wires to the existing story-beat UI). */
let _inkMod = null;
async function _loadInk() {
  if (_inkMod) return _inkMod;
  try { _inkMod = await import('../../vendor/inkjs/ink.mjs'); }
  catch { _inkMod = null; }
  return _inkMod;
}

export class WHCinematicDirector {
  constructor() {
    this.projects = {};
    this.graph = new WHTriggerGraph();
    this.active = [];   // { seq, target }
    this.story = null;  // inkjs Story
    this.onDialogue = null;
    this.onSequenceEvent = null;
    this.graph.onDialogue = (prompt, trigger) => { if (this.onDialogue) this.onDialogue(prompt, trigger); };
  }
  project(name) { if (!this.projects[name]) this.projects[name] = new WHProject(name); return this.projects[name]; }

  playSequence(sheet, target, opts = {}) {
    const rec = { seq: sheet.sequence, target };
    sheet.sequence.play(target, {
      ...opts,
      onDone: (s) => { this.active = this.active.filter((r) => r.seq !== s); if (opts.onDone) opts.onDone(s); },
    });
    this.active.push(rec);
    return rec;
  }
  /* Apply a camera shot list (camdirector-style) as a sequence:
     shots: [{ pos:[x,y,z], look:[x,y,z], fov?, hold?, transition? }] */
  playShots(camera, shots, opts = {}) {
    const seq = new WHSequence('shots');
    const look = { x: 0, y: 0, z: 0 };
    let t = 0;
    const posTrack = [], lookTrack = [];
    shots.forEach((s, i) => {
      const dur = s.transition ?? 1.2;
      posTrack.push({ t, value: s.pos, ease: 'smooth' });
      lookTrack.push({ t, value: s.look, ease: 'smooth' });
      t += dur + (s.hold ?? 0.8);
      if (i === shots.length - 1) { posTrack.push({ t, value: s.pos }); lookTrack.push({ t, value: s.look }); }
    });
    seq.addTrack('camPos', posTrack);
    seq.addTrack('camLook', lookTrack);
    const proxy = { camPos: [...camera.position.toArray ? camera.position.toArray() : [0, 0, 0]], camLook: { ...look } };
    seq.onValuesChange(proxy, (values) => {
      if (values.camPos && camera.position.set) camera.position.set(...values.camPos);
      if (values.camLook) camera.lookAt(values.camLook.x, values.camLook.y, values.camLook.z);
    });
    return this.playSequence({ sequence: seq }, proxy, opts);
  }

  /* ---- ink narrative (inkjs, lazy) ---- */
  async loadStory(inkJson) {
    const mod = await _loadInk();
    if (!mod) return { ok: false, reason: 'inkjs unavailable' };
    this.story = new mod.Story(typeof inkJson === 'string' ? inkJson : JSON.stringify(inkJson));
    return { ok: true };
  }
  storyContinue() {
    if (!this.story) return { lines: [], choices: [] };
    const lines = [];
    while (this.story.canContinue) { const t = this.story.Continue().trim(); if (t) lines.push(t); }
    const choices = this.story.currentChoices.map((c) => ({ index: c.index, text: c.text }));
    return { lines, choices };
  }
  storyChoose(index) {
    if (!this.story) return { lines: [], choices: [] };
    this.story.ChooseChoiceIndex(index);
    this.graph.setFlag('__choice', index);
    return this.storyContinue();
  }
  storyVar(name, value) {
    if (!this.story) return;
    if (value === undefined) return this.story.variablesState[name];
    this.story.variablesState[name] = value;
  }
  /* Sync trigger flags -> ink variables (one direction, explicit). */
  syncFlagsToStory(names) {
    if (!this.story) return;
    for (const n of names) this.story.variablesState[n] = this.graph.getFlag(n);
  }

  update(dt, ctx = {}) {
    for (const r of [...this.active]) r.seq.update(dt);
    this.graph.update(dt, ctx);
    if (this.onSequenceEvent) { /* reserved: sequence markers */ }
  }
}
