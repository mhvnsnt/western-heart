/* ============================================================
   WESTERN HEART — Combo Trials (per-character)
   Teardown source: Tekken's combo/punishment trial modes (T6/T7/T8) —
   per-character scripted input sequences with step validation, timing
   grades, and progressive difficulty. Faithful port of the format:
     • trials are DATA (per fighter id), the runner is generic;
     • each step is a Tekken notation the player must perform in order;
     • timing between steps is graded (PERFECT/GOOD/LATE);
     • trials unlock in order; completion persists (localStorage).
   WH canon mapping (PROPOSED — needs owner approval):
     "TRIAL INSCRIPTIONS" — the Trial itself teaches. The shrine stones
     show each vessel its own techniques; the trial is inscribed in stone
     ("Fight. Die. Return. Claim the forces. Forge the katana. Become
     whole."), so the stones drilling combos is the Trial diagnosing the
     vessel. Narrator voice: stone-text in Sato's deadpan register (per
     canon's last text card). Alternative: Megami (trained Chatur) as the
     in-universe master — flagged for owner call.
   ============================================================ */

export const TRIAL_STORE_KEY = 'wh_trial_progress';
export const TRIAL_TIMING = { perfect: 12, good: 24 }; // frames between steps

/* Trial step: { notation } — Tekken notation string, e.g. '1', 'd/f+2', '2,1'.
   Trial: { id, fighter, name, difficulty 1-5, steps:[{notation, hint}], briefing } */
export const COMBO_TRIALS = {
  /* ——— PANTERA (King base — grappler trials) ——— */
  pantera: [
    { id: 'pantera-1', name: 'First Blood', difficulty: 1,
      briefing: 'The stones remember your hands. Show them the jab.',
      steps: [{ notation: '1', hint: 'Left punch' }, { notation: '2', hint: 'Right punch' }] },
    { id: 'pantera-2', name: 'String Theory', difficulty: 2,
      briefing: 'Two hits, one breath.',
      steps: [{ notation: '2', hint: 'Right punch' }, { notation: '2,1', hint: 'Follow with 1' }] },
    { id: 'pantera-3', name: 'Tou Remembers', difficulty: 3,
      briefing: 'Battle itself lives in your arms. Chain it.',
      steps: [{ notation: '1', hint: '1' }, { notation: '2', hint: '2' }, { notation: '2,1', hint: '2,1 to finish' }] },
  ],
  /* ——— DEMONIO (discipline trials) ——— */
  demonio: [
    { id: 'demonio-1', name: 'The Code', difficulty: 1,
      briefing: 'Rin is dignified. Strike like it.',
      steps: [{ notation: '1', hint: 'Left punch' }, { notation: '1', hint: 'Left punch again' }] },
    { id: 'demonio-2', name: 'No Bow', difficulty: 2,
      briefing: 'You bow to every soul. Not this one. Hit twice.',
      steps: [{ notation: '2', hint: '2' }, { notation: '1', hint: '1' }, { notation: '2,1', hint: '2,1' }] },
  ],
  /* ——— DOROWANI (trickster trials — simple, goofy) ——— */
  dorowani: [
    { id: 'dorowani-1', name: 'Konnichiwa!', difficulty: 1,
      briefing: 'Konnichiwa! (The stone says: punch.)',
      steps: [{ notation: '1', hint: '1!' }, { notation: '2', hint: '2!' }] },
    { id: 'dorowani-2', name: 'Ichiban Bankai', difficulty: 2,
      briefing: 'Ichiban! (The stone says: punch, punch, punch.)',
      steps: [{ notation: '1', hint: '1' }, { notation: '1', hint: '1' }, { notation: '2,1', hint: '2,1!' }] },
  ],
  /* ——— SKULL (punisher trials) ——— */
  skull: [
    { id: 'skull-1', name: 'Targets', difficulty: 1,
      briefing: 'Another target. Mark it.',
      steps: [{ notation: '1', hint: '1' }, { notation: '2', hint: '2' }] },
  ],
};

/* Normalize a notation for comparison ('d/f+2' vs 'd/f + 2'). */
export function normNotation(n) {
  return String(n).toLowerCase().replace(/\s+/g, '').replace(/\+/g, ',');
}

/* The trial runner — pure logic, no DOM. Feed performed notations in. */
export class TrialRunner {
  constructor(trial) {
    this.trial = trial;
    this.stepIdx = 0;
    this.grades = [];      // per-step 'PERFECT'|'GOOD'|'LATE'
    this.framesSinceStep = 0;
    this.done = false;
    this.failed = false;
    this.started = false;
  }
  begin() { this.started = true; this.framesSinceStep = 0; }
  tick(frames = 1) { if (this.started && !this.done) this.framesSinceStep += frames; }
  /* A move was performed (notation string). Returns step result. */
  perform(notation) {
    if (!this.started || this.done) return { ok: false, reason: 'not-running' };
    const step = this.trial.steps[this.stepIdx];
    if (!step) return { ok: false, reason: 'no-step' };
    if (normNotation(notation) !== normNotation(step.notation)) {
      this.failed = true;
      return { ok: false, reason: 'wrong-move', expected: step.notation, got: notation };
    }
    const f = this.framesSinceStep;
    const grade = f <= TRIAL_TIMING.perfect ? 'PERFECT' : f <= TRIAL_TIMING.good ? 'GOOD' : 'LATE';
    this.grades.push(grade);
    this.stepIdx++;
    this.framesSinceStep = 0;
    if (this.stepIdx >= this.trial.steps.length) {
      this.done = true;
      return { ok: true, grade, complete: true, grades: this.grades.slice() };
    }
    return { ok: true, grade, complete: false, next: this.trial.steps[this.stepIdx] };
  }
  currentStep() { return this.trial.steps[this.stepIdx] || null; }
  progress() { return { step: this.stepIdx, total: this.trial.steps.length, done: this.done, failed: this.failed }; }
}

/* Completion persistence (browser localStorage; in-memory fallback). */
const _mem = {};
function _store() {
  try { return (typeof localStorage !== 'undefined') ? localStorage : null; } catch { return null; }
}
export function trialProgress() {
  const s = _store();
  try { return JSON.parse((s ? s.getItem(TRIAL_STORE_KEY) : _mem[TRIAL_STORE_KEY]) || '{}'); }
  catch { return {}; }
}
export function markTrialComplete(fighterId, trialId) {
  const p = trialProgress(), k = fighterId + ':' + trialId;
  p[k] = { at: Date.now() };
  const s = _store(), v = JSON.stringify(p);
  if (s) { try { s.setItem(TRIAL_STORE_KEY, v); } catch {} } else _mem[TRIAL_STORE_KEY] = v;
  return p;
}
export function trialsFor(fighterId) { return COMBO_TRIALS[fighterId] || []; }
