/* ============================================================
   WESTERN HEART — Replay codec (worker 29, 2026-10-22)
   PURE module: zero imports, no DOM, no THREE — unit-testable in
   node (game/tests/training-replay.test.mjs).

   Covers the deterministic-replay data layer shared by the recorder
   (js/replay.js) and the training lab (js/training.js):
   • fighter snapshot / restore (plain-field round trip)
   • recorded-call indexing by tick
   • replay-library CRUD over an injected storage (localStorage in
     the browser, a mock in tests)

   Replay format (NOT video — deterministic re-simulation):
     { v: 1, meta: {...}, rounds: [ { round, tick0, snapshot, calls } ] }
   calls: [tickRel, who('p1'|'p2'), method, ...args]
   tryAttack calls append [ok, firedNotation]:
     [tickRel, who, 'tryAttack', rawName, ok, fired]
   ============================================================ */

export const REPLAY_VERSION = 1;
export const LIB_KEY = 'wh_replays_v1';
export const LIB_MAX = 12;

/* ---------------- fighter snapshot ----------------
   Captures everything the fight sim reads that _startRound (or the
   lab reset) does not re-derive identically at replay time. Plain
   fields only — JSON-safe. `resolveMove` is injected by the caller
   (fighter.js getRealMove) so this module stays import-free. */
export function snapFighter(f) {
  const tk = f.tekken || {};
  return {
    pos: [f.root.position.x, f.root.position.y, f.root.position.z],
    facing: f.facing,
    faceY: (f._faceY !== undefined && f._faceY !== null) ? f._faceY : f.lean.rotation.y,
    leanY: f.lean.rotation.y,
    state: f.state,
    stateT: f.stateT,
    hp: f.hp,
    meter: f.meter,
    vx: f.vx,
    stun: f.stun,
    dead: !!f.dead,
    invuln: f.invuln || 0,
    attackName: f.attackName,
    attackPhase: f._attackPhase,
    hasHit: !!f.hasHit,
    // The resolved move object is re-derived on restore from its notation
    // (notations are stable keys into the moveset data).
    attackNotation: f.attackName || null,
    combo: f.combo || 0,
    stance: f.stance || null,
    stanceT: f.stanceT || 0,
    rageUsed: !!f._rageUsed,
    queuedNext: f._queuedNext || null,
    queuedAfter: f._queuedAfter ? f._queuedAfter.slice() : null,
    lastMove: tk.lastMove || null,
  };
}

export function restoreFighter(f, s, resolveMove) {
  f.root.position.set(s.pos[0], s.pos[1], s.pos[2]);
  f.facing = s.facing;
  f._faceY = s.faceY;
  f.lean.rotation.y = s.leanY;
  f.state = s.state;
  f.stateT = s.stateT;
  f.hp = s.hp;
  f.meter = s.meter;
  f.vx = s.vx;
  f.stun = s.stun;
  f.dead = s.dead;
  f.invuln = s.invuln;
  f.attackName = s.attackName;
  f._attackPhase = s.attackPhase;
  f.hasHit = s.hasHit;
  f.attack = (s.attackNotation && resolveMove)
    ? (resolveMove(f._movesetId, s.attackNotation) || null)
    : null;
  f.combo = s.combo;
  f.stance = s.stance;
  f.stanceT = s.stanceT;
  f._rageUsed = s.rageUsed;
  f._queuedNext = s.queuedNext;
  f._queuedAfter = s.queuedAfter ? s.queuedAfter.slice() : null;
  if (f.tekken) f.tekken.lastMove = s.lastMove;
  return f;
}

/* ---------------- call indexing ----------------
   Recorder emits a flat array; the player needs O(1) per-tick lookup. */
export function indexCallsByTick(calls) {
  const map = new Map();
  for (const c of calls) {
    const t = c[0];
    let arr = map.get(t);
    if (!arr) { arr = []; map.set(t, arr); }
    arr.push(c);
  }
  return map;
}

/* Change detection for continuous inputs (setStick/tryMove/tryBlock/
   tryCrouch are called every tick — only record on change). */
export function sameArgs(a, b) {
  if (a === b) return true;
  if (!a || !b || a.length !== b.length) return false;
  for (let i = 0; i < a.length; i++) {
    const x = a[i], y = b[i];
    if (typeof x === 'number' && typeof y === 'number') {
      if (Math.abs(x - y) > 1e-3) return false;
    } else if (x !== y) return false;
  }
  return true;
}

/* ---------------- replay library ----------------
   storage: { getItem(k), setItem(k, v), removeItem(k) } — localStorage
   in the browser. Newest first. Bounded (LIB_MAX); oldest evicted. */
export function listReplays(storage) {
  try {
    const raw = storage.getItem(LIB_KEY);
    if (!raw) return [];
    const arr = JSON.parse(raw);
    return Array.isArray(arr) ? arr : [];
  } catch (e) {
    return [];
  }
}

function writeList(storage, arr) {
  try {
    storage.setItem(LIB_KEY, JSON.stringify(arr));
    return true;
  } catch (e) {
    return false;
  }
}

export function saveReplay(storage, data) {
  const arr = listReplays(storage);
  const entry = {
    id: data.meta.id,
    date: data.meta.date,
    p1name: data.meta.p1name,
    p2name: data.meta.p2name,
    p1id: data.meta.p1id,
    p2id: data.meta.p2id,
    stageId: data.meta.stageId,
    stageName: data.meta.stageName,
    mode: data.meta.mode,
    winner: data.meta.winner,
    rounds: data.rounds.length,
    ticks: data.rounds.reduce((n, r) => n + (r.endTick || 0), 0),
    bytes: JSON.stringify(data).length,
    data,
  };
  const ix = arr.findIndex((e) => e.id === entry.id);
  if (ix >= 0) arr[ix] = entry; else arr.unshift(entry);
  while (arr.length > LIB_MAX) arr.pop();
  return writeList(storage, arr) ? entry : null;
}

export function getReplay(storage, id) {
  return listReplays(storage).find((e) => e.id === id) || null;
}

export function deleteReplay(storage, id) {
  const arr = listReplays(storage).filter((e) => e.id !== id);
  return writeList(storage, arr);
}

export function clearReplays(storage) {
  try { storage.removeItem(LIB_KEY); return true; } catch (e) { return false; }
}

/* Replay metadata factory (ids are time-based; collisions impossible
   in practice — one fight ends before the next begins). */
export function makeMeta({ p1id, p2id, p1name, p2name, stageId, stageName, mode, winner }) {
  return {
    id: 'rp_' + Date.now().toString(36),
    date: new Date().toISOString(),
    p1id, p2id, p1name, p2name, stageId, stageName, mode,
    winner: winner || null,
  };
}
