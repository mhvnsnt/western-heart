/* ============================================================
   WESTERN HEART — FIGHT LAB: GUNGAKU (軍楽)
   Official name — owner-locked 2026-10-22. "War music."
   The programmable training dummy (TTT2 Combot equivalent).

   Builds on worker 29's training mode (modes.js `_beginTraining`):
   training's passive dummy becomes a Gungaku dummy here — a
   programmable AI that runs authored or recorded behavior
   sequences instead of standing still.

   Design (Combot-style):
   - A GungakuProgram is an ordered list of steps. Each step is an
     op the dummy performs for `dur` seconds, then the next step.
     Programs loop by default.
   - Ops are BUTTON/STATE level, not move names: '1'..'4' resolve
     through the dummy's own TekkenBuffer (fighter.tryAttack),
     so a program recorded on one fighter plays back sensibly on
     any other fighter.
   - The RECORDER captures the player's own button/state ops into
     a program — program the dummy by demonstrating, Combot-style.
   - Presets cover the classic lab drills (guard all, crouch,
     walk-in, punish check, juggle sandbag).
   ============================================================ */
import { AIController } from './ai.js';

/** Official mode name. Owner-locked 2026-10-22 — not a working title. */
export const GUNGAKU_NAME = 'GUNGAKU';
export const GUNGAKU_KANJI = '軍楽'; // "war music"
export const GUNGAKU_LABEL = 'GUNGAKU 軍楽';

/* Step ops. `dur` in seconds. */
export const GUNGAKU_OPS = [
  'idle',        // stand, do nothing
  'guard',       // hold stand block
  'crouch',      // hold crouch (low guard implied by stance)
  'walk_in',     // walk toward the player
  'walk_out',    // walk away from the player
  'jump',        // single jump
  'sidestep_l',  // sidestep left
  'sidestep_r',  // sidestep right
  'dodge',       // Tekken-style dodge
  'attack',      // tryAttack(step.btn || '1')
  'wait',        // like idle but explicit beat (Combot "pause")
];

/* ---------- Program ---------- */
export class GungakuProgram {
  constructor(name = 'UNTITLED', steps = [], loop = true) {
    this.name = name;
    this.loop = loop;
    this.steps = steps.map((s) => GungakuProgram.normStep(s));
  }
  static normStep(s) {
    const op = GUNGAKU_OPS.includes(s.op) ? s.op : 'idle';
    return { op, dur: Math.max(0.1, Math.min(10, s.dur ?? 1)), btn: s.btn || null };
  }
  get length() { return this.steps.length; }
  toJSON() { return { name: this.name, loop: this.loop, steps: this.steps }; }
  static fromJSON(j) {
    if (!j || !Array.isArray(j.steps)) return null;
    return new GungakuProgram(j.name || 'UNTITLED', j.steps, j.loop !== false);
  }
}

/* ---------- Preset programs (the classic lab drills) ---------- */
export const GUNGAKU_PRESETS = {
  idle:        new GungakuProgram('IDLE — SANDABAG', [{ op: 'idle', dur: 2 }]),
  guard_all:   new GungakuProgram('GUARD ALL', [{ op: 'guard', dur: 3 }]),
  crouch:      new GungakuProgram('CROUCH', [{ op: 'crouch', dur: 3 }]),
  walk_in:     new GungakuProgram('WALK IN', [{ op: 'walk_in', dur: 2.5 }, { op: 'wait', dur: 0.5 }]),
  walk_out:    new GungakuProgram('WALK OUT', [{ op: 'walk_out', dur: 2.5 }, { op: 'wait', dur: 0.5 }]),
  punish:      new GungakuProgram('PUNISH CHECK', [
    { op: 'guard', dur: 1.2 }, { op: 'attack', dur: 0.4, btn: '1' }, { op: 'wait', dur: 1.0 },
  ]),
  juggle:      new GungakuProgram('JUGGLE SANDABAG', [
    { op: 'idle', dur: 0.8 }, { op: 'jump', dur: 0.6 }, { op: 'idle', dur: 1.2 },
  ]),
  sidestep:    new GungakuProgram('SIDESTEP DRILL', [
    { op: 'sidestep_l', dur: 0.5 }, { op: 'wait', dur: 0.4 },
    { op: 'sidestep_r', dur: 0.5 }, { op: 'wait', dur: 0.4 },
  ]),
  mixup:       new GungakuProgram('MIXUP LOOP', [
    { op: 'guard', dur: 1.0 }, { op: 'crouch', dur: 1.0 },
    { op: 'attack', dur: 0.4, btn: '2' }, { op: 'wait', dur: 0.6 },
  ]),
};

/* ---------- Recorder: program the dummy by demonstrating ---------- */
export class GungakuRecorder {
  constructor(maxSteps = 32) {
    this.maxSteps = maxSteps;
    this.recording = false;
    this.steps = [];
    this._cur = null; // { op, t0 }
  }
  start() { this.recording = true; this.steps = []; this._cur = null; }
  stop() {
    this._flush();
    this.recording = false;
    return new GungakuProgram('RECORDED', this.steps.slice());
  }
  /* Feed the player's sampled op each frame; compresses repeats. */
  sample(op, btn, now) {
    if (!this.recording) return;
    if (!this._cur || this._cur.op !== op || this._cur.btn !== (btn || null)) {
      this._flush(now);
      if (this.steps.length >= this.maxSteps) return;
      this._cur = { op, btn: btn || null, t0: now };
    }
  }
  _flush(now) {
    if (!this._cur) return;
    const dur = Math.max(0.25, (now ?? performance.now() / 1000) - this._cur.t0);
    this.steps.push({ op: this._cur.op, dur: Math.min(5, dur), btn: this._cur.btn });
    this._cur = null;
  }
}

/* Map the player's live state to a recordable op (called per frame). */
export function playerOp(player) {
  if (!player) return 'idle';
  if (player.state === 'attack') return null; // attacks recorded via button hook
  if (player.state === 'block') return 'guard';
  if (player.state === 'crouch' || player.state === 'crouchblock') return 'crouch';
  if (player.state === 'walk') return (player._walkDir || 1) > 0 ? 'walk_in' : 'walk_out';
  return 'idle';
}

/* ---------- The programmable dummy AI ---------- */
export class GungakuAI extends AIController {
  constructor(fighter, personality = {}) {
    super(fighter, { ...personality, passive: false });
    this.gungaku = true;
    this.program = personality.gungakuProgram instanceof GungakuProgram
      ? personality.gungakuProgram
      : (GUNGAKU_PRESETS[personality.gungakuPreset] || GUNGAKU_PRESETS.idle);
    this._stepIdx = 0;
    this._stepT = 0;
    this._holding = null; // op currently being held (guard/crouch/walk)
    this.recorder = null; // GungakuRecorder attached by the panel (records the PLAYER)
  }

  setProgram(prog) {
    if (prog instanceof GungakuProgram && prog.length) {
      this.program = prog;
      this._stepIdx = 0; this._stepT = 0;
      this._releaseHold();
    }
  }

  _releaseHold() {
    const f = this.f;
    try {
      if (this._holding === 'guard') f.tryBlock(false);
      if (this._holding === 'crouch') f.tryCrouch(false);
    } catch (e) { /* never break the lab on a hold release */ }
    this._holding = null;
  }

  _doOp(op, btn, player) {
    const f = this.f;
    if (!f.canAct()) { this._releaseHold(); return; }
    const dir = Math.sign(player.root.position.x - f.root.position.x) || 1;
    try {
      switch (op) {
        case 'guard': f.tryBlock(true); this._holding = 'guard'; break;
        case 'crouch': f.tryCrouch(true); this._holding = 'crouch'; break;
        case 'walk_in': f.tryMove(dir); break;
        case 'walk_out': f.tryMove(-dir); break;
        case 'jump': f.tryJump(); break;
        case 'sidestep_l': f.trySidestep(-1); break;
        case 'sidestep_r': f.trySidestep(1); break;
        case 'dodge': f.tryDodge(); break;
        case 'attack': f.tryAttack(btn || '1'); break;
        case 'idle':
        case 'wait':
        default: this._releaseHold(); break;
      }
    } catch (e) { /* a failed op degrades to idle — the lab never hard-breaks */ }
  }

  update(dt, player) {
    const f = this.f;
    if (f.dead || f.state === 'ko' || f.state === 'victory') return;
    // Recorder samples the PLAYER while the program drives the dummy.
    if (this.recorder && this.recorder.recording) {
      this.recorder.sample(playerOp(player), null, performance.now() / 1000);
    }
    const steps = this.program.steps;
    if (!steps.length) return;
    this._stepT += dt;
    let step = steps[this._stepIdx % steps.length];
    if (this._stepT >= step.dur) {
      this._stepT = 0;
      this._stepIdx++;
      if (this._stepIdx >= steps.length) {
        if (!this.program.loop) { this._releaseHold(); return; }
        this._stepIdx = 0;
      }
      step = steps[this._stepIdx % steps.length];
      // One-shot ops fire on step entry; holds persist across frames.
      if (['jump', 'sidestep_l', 'sidestep_r', 'dodge', 'attack'].includes(step.op)) {
        this._doOp(step.op, step.btn, player);
      }
    }
    // Hold ops re-assert every frame (blocks/crouch/walk need continuous input).
    if (['guard', 'crouch', 'walk_in', 'walk_out'].includes(step.op)) {
      this._doOp(step.op, step.btn, player);
    } else if (this._holding && !['guard', 'crouch'].includes(step.op)) {
      this._releaseHold();
    }
  }
}

/* ---------- In-fight HUD panel (G toggles) ---------- */
export function mountGungakuPanel(game, ai) {
  if (document.getElementById('gungaku-panel')) return;
  const el = document.createElement('div');
  el.id = 'gungaku-panel';
  el.style.cssText = 'position:fixed;right:12px;top:12px;z-index:60;display:none;' +
    'background:rgba(8,8,14,.92);border:1px solid #7a5cff;border-radius:10px;' +
    'padding:12px 14px;color:#e8e4ff;font:12px/1.5 system-ui;max-width:250px;';
  const title = `${GUNGAKU_LABEL} — FIGHT LAB`;
  el.innerHTML =
    `<div style="font-weight:700;letter-spacing:.08em;margin-bottom:8px;color:#b7a6ff">${title}</div>` +
    `<div style="margin-bottom:8px"><label>PROGRAM </label><select id="gg-preset" style="width:100%;margin-top:4px;background:#14141f;color:#e8e4ff;border:1px solid #444;border-radius:6px;padding:4px">${
      Object.keys(GUNGAKU_PRESETS).map((k) =>
        `<option value="${k}">${GUNGAKU_PRESETS[k].name}</option>`).join('')
    }</select></div>` +
    `<div style="display:flex;gap:6px;margin-bottom:8px">` +
    `<button id="gg-rec" style="flex:1">● REC</button>` +
    `<button id="gg-play" style="flex:1" disabled>▶ PLAY</button></div>` +
    `<div id="gg-status" style="opacity:.75">Dummy: IDLE — SANDABAG · G toggles panel</div>` +
    `<div style="opacity:.55;margin-top:6px">Recorder captures your buttons + stances, Combot-style. Attacks record as 1/2/3/4 and resolve on the dummy's own moveset.</div>`;
  document.body.appendChild(el);
  const status = el.querySelector('#gg-status');
  const setStatus = (t) => { status.textContent = t; };

  el.querySelector('#gg-preset').onchange = (e) => {
    ai.setProgram(GUNGAKU_PRESETS[e.target.value]);
    setStatus('Dummy: ' + ai.program.name);
  };
  const recBtn = el.querySelector('#gg-rec');
  const playBtn = el.querySelector('#gg-play');
  let recorded = null;
  recBtn.onclick = () => {
    if (!ai.recorder || !ai.recorder.recording) {
      ai.recorder = new GungakuRecorder();
      ai.recorder.start();
      recBtn.textContent = '■ STOP';
      recBtn.style.color = '#ff6b6b';
      setStatus('Recording YOUR actions… press ■ STOP when done.');
    } else {
      recorded = ai.recorder.stop();
      recBtn.textContent = '● REC';
      recBtn.style.color = '';
      playBtn.disabled = !recorded.length;
      setStatus(`Recorded ${recorded.length} steps. Press ▶ PLAY to program the dummy.`);
    }
  };
  playBtn.onclick = () => {
    if (recorded && recorded.length) {
      ai.setProgram(recorded);
      setStatus('Dummy programmed: ' + recorded.steps.map((s) => s.op).join(' → '));
    }
  };
  // The player's attack buttons feed the recorder (Combot programs inputs).
  const origTry = game.p1.tryAttack.bind(game.p1);
  game.p1.tryAttack = (name) => {
    if (ai.recorder && ai.recorder.recording && /^[1234](\+[1234])*$/.test(name)) {
      ai.recorder.steps.push({ op: 'attack', dur: 0.5, btn: name });
    }
    return origTry(name);
  };
  document.addEventListener('keydown', (e) => {
    if (e.code === 'KeyG' && game.running) {
      el.style.display = el.style.display === 'none' ? 'block' : 'none';
    }
  });
  el.style.display = 'block';
  return el;
}
