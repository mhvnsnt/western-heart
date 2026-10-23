/* ============================================================
   WESTERN HEART — Ghost AI ("Soul Echoes")
   Teardown source: fighting-game ghost AI (Tekken 6 Ghost Battle /
   TTT2 ghosts, VF ghost system): the CPU records a player's behavior
   and replays a statistical model of it — the ghost fights LIKE you.
   Faithful port of the design:
     • RECORD: (situation, action) pairs sampled every decision tick.
       Situation = compact state key (range band, stance, foe state,
       health band, frames since foe attack). Action = input notation.
     • MODEL: per-situation action histograms with Laplace smoothing.
     • FIGHT: sample from the histogram (temperature-controlled) blended
       with a base AI policy so the ghost never hard-locks.
     • PERSIST: ghosts serialize to localStorage; named per player tag.
   WH canon mapping (PROPOSED — needs owner approval):
     "SOUL ECHOES" — when a soul dies and returns, the fallen version's
     echo remains ("the soul that loses and returns is not the soul that
     fell" — Reincarnation, CANON.md). Ghosts are those echoes: past
     vessels still fighting in the head-world. The Assembled Soul
     ("moves like Pantera, strikes like Demonio...") is the ultimate
     echo — every vessel at once. Ghost battle = sparring your own echo.
   ============================================================ */

export const GHOST_STORE_KEY = 'wh_soul_echoes';
export const GHOST_SITUATION_BANDS = ['point-blank', 'close', 'mid', 'far'];

/* Compact situation key from a fight snapshot. Pure — unit-testable. */
export function situationKey(snap) {
  // snap: { dist, myStance, foeState, myHpFrac, foeHpFrac, foeAttackStartup }
  const d = snap.dist;
  const band = d < 1.2 ? 'point-blank' : d < 2.6 ? 'close' : d < 4.5 ? 'mid' : 'far';
  const foe = snap.foeAttackStartup ? 'foe-attacking' : (snap.foeState || 'neutral');
  const hp = snap.myHpFrac < 0.3 ? 'lowhp' : 'okhp';
  return [band, snap.myStance || 'standing', foe, hp].join('|');
}

/* The learned model: situation -> { action -> count }. */
export class GhostModel {
  constructor(name = 'echo') {
    this.name = name;
    this.table = {};   // situation -> { action: count }
    this.samples = 0;
  }
  record(situation, action) {
    const row = this.table[situation] || (this.table[situation] = {});
    row[action] = (row[action] || 0) + 1;
    this.samples++;
  }
  /* Distribution with Laplace smoothing; temperature scales sharpness. */
  distribution(situation, temperature = 1.0) {
    const row = this.table[situation];
    if (!row) return null;
    const actions = Object.keys(row);
    const weights = actions.map(a => Math.pow(row[a] + 1, 1 / Math.max(0.05, temperature)));
    const sum = weights.reduce((x, y) => x + y, 0);
    return actions.map((a, i) => ({ action: a, p: weights[i] / sum }));
  }
  sample(situation, temperature = 1.0, rand = Math.random) {
    const dist = this.distribution(situation, temperature);
    if (!dist) return null;
    let r = rand(), acc = 0;
    for (const { action, p } of dist) { acc += p; if (r <= acc) return action; }
    return dist[dist.length - 1].action;
  }
  toJSON() { return { name: this.name, table: this.table, samples: this.samples, v: 1 }; }
  static fromJSON(j) {
    const g = new GhostModel(j.name || 'echo');
    g.table = j.table || {}; g.samples = j.samples || 0;
    return g;
  }
}

/* Recorder: call observe() each AI tick while fighting the player. */
export class GhostRecorder {
  constructor(model) { this.model = model; this.enabled = true; }
  observe(snap, playerAction) {
    if (!this.enabled || !playerAction) return;
    this.model.record(situationKey(snap), playerAction);
  }
}

/* Fighter: blends ghost sampling with a fallback policy. */
export class GhostAI {
  constructor(model, fallbackPolicy = null, temperature = 0.8, ghostMix = 0.75) {
    this.model = model;
    this.fallback = fallbackPolicy; // () -> action when ghost has no data
    this.temperature = temperature;
    this.ghostMix = ghostMix;       // P(use ghost) when data exists
  }
  decide(snap, rand = Math.random) {
    const key = situationKey(snap);
    const dist = this.model.distribution(key, this.temperature);
    if (dist && rand() < this.ghostMix) return this.model.sample(key, this.temperature, rand);
    return this.fallback ? this.fallback(snap) : null;
  }
}

/* ---------- persistence ---------- */
const _mem = {};
function _ls() { try { return (typeof localStorage !== 'undefined') ? localStorage : null; } catch { return null; } }
export function saveGhost(model) {
  const v = JSON.stringify(model.toJSON());
  const s = _ls();
  if (s) { try { s.setItem(GHOST_STORE_KEY + ':' + model.name, v); } catch {} }
  else _mem[model.name] = v;
}
export function loadGhost(name) {
  const s = _ls();
  const v = s ? s.getItem(GHOST_STORE_KEY + ':' + name) : _mem[name];
  if (!v) return null;
  try { return GhostModel.fromJSON(JSON.parse(v)); } catch { return null; }
}
export function listGhosts() {
  const s = _ls(), out = [];
  if (s) { try { for (let i = 0; i < s.length; i++) { const k = s.key(i); if (k && k.startsWith(GHOST_STORE_KEY + ':')) out.push(k.slice(GHOST_STORE_KEY.length + 1)); } } catch {} }
  else for (const k of Object.keys(_mem)) out.push(k);
  return out;
}
