/* t7-graph-driver.js — drives ONE fighter frame by frame from an imported T7 move graph (wh-t7-graph/2) and its
   shipped clip bank (wh-t7-graph-clips/1). Pure (no DOM / THREE), so the same code runs in the game and in the node
   replay harness (test/t7-graph-adapter-pantera.test.mjs).
   One tick = one 60 Hz source frame:
     1. this tick plays frame `frame` (1-based) of the current source move; its clip sample is frame - 1;
     2. this tick's input { dir, down, held, special } is recorded and the move's cancel list is evaluated at that frame
        (t7graph.stepCancel, source order, unknown requirement = skipped + reported);
     3. a cancel whose cancel frame is now applies: the target move's frame 1 plays on the NEXT tick; an accepted input
        whose cancel frame is later waits for it (P3 in t7graph.js);
     4. with nothing applied and the animation at its last frame, the move's own `transition` plays next (the motbin's
        anim_max_len is 0 for every King move on disk — the engine fills it from the animation — so the move length
        IS the clip's frame count).
   A cancel taken after an earlier row was skipped for an unknown condition is flagged (fired.precedenceUnknown):
   the engine might have taken that earlier row instead.
   Effects reported per tick (the fighter applies them): source move id/name, clip key + sample, damage and the
   source active window [first_active, last_active] (hit level: see hitLevelOf), forward root travel this tick from
   the clip's raw T7 root channel (root_motion_fwd_m; lateral 0, sign unproven). */
import { stepCancel, resolveMoveId, makeEvalCond, buttonsMask, F, T7_VAR_WRITERS, T7_FLAG_WRITERS } from './t7graph.js';

export const T7G_FPS = 60;
export const T7G_HISTORY = 160; // frames kept; the longest King sequence window is 155

export class T7GraphDriver {
  /** graph: wh-t7-graph/2; clips: { key: { frames, fwd: number[] } } (key = '<bank>_<clip>'). */
  constructor(graph, clips, { evalState = null, strict = true, props = null } = {}) {
    this.props = props; // wh-t7-graph-props/1 (extra move properties per move), or null
    this.graph = graph; this.clips = clips; this.evalState = evalState || {};
    this.strict = strict; // fail closed when an outranking row's requirement truth is unknown (see stepCancel)
    this.stats = { ticks: 0, fired: 0, transitions: 0, skipped: {}, unknownConditions: {}, missingClip: 0 };
    this.attackId = 0;
    // Match start (only when the caller asks for tracked state): the exe player init 0x140759a50 zeroes [0x938],
    // [0x960..0x967] and the 100 player-flag words (0x14075a033..0x14075a065); the reset 0x140746ad0 zeroes [0x938]/[0x964].
    // Set BEFORE the stance is entered so the stance's own property writers are applied to it.
    if (this.evalState.trackPlayerVars) {
      this.evalState.playerVars = { [0x938]: 0, [0x964]: 0 };
      this.evalState.playerFlags = new Array(100).fill(0);
    }
    this.reset();
  }
  clipKey(m) { return m && m.clip != null ? `${m.bank}_${m.clip}` : null; }
  clipOf(m) { const k = this.clipKey(m); return k ? this.clips[k] || null : null; }
  reset(moveId = this.graph.stance) {
    this.history = []; this.pending = null; this._enter(moveId);
  }
  _enter(id) {
    this.moveId = id; this.frame = 1; this.pending = null; this._prevFwd = null;
    const m = this.graph.moves[id];
    if (m && m.damage > 0) this.attackId += 1;
    const P = this.props && this.props.moves[id];
    if (P) this._applyWriters([...P.extra.map((x) => [x[2], x[3]]), ...P.start.map((x) => [x[2], x[3]]), ...P.end.map((x) => [x[2], x[3]])]);
  }
  get move() { return this.graph.moves[this.moveId]; }
  /* Player variables [self+0x938] / [self+0x964] (requirements 809 / 361). Exe: zeroed by the reset 0x140746ad0, written
     only by property ids 0x8414-0x8416 / 0x80ed, 0x8112, 0x8113 (property switch 0x1407198ac). King's extra-move-property
     lists contain none (graph.props.json, tested); his cancel requirement lists DO (667 rows). WHEN the engine applies a
     list's property entries is not traced, so after such a row fires the variable becomes UNKNOWN (fail closed). */
  _varWriters(rowIndex, m) {
    const row = m.cancels[rowIndex]; if (!row) return;
    this._applyWriters((this.graph.requirements[String(row[F.req])] || []).map(([c, p]) => [c, p]));
  }
  /* A property entry that can write tracked state makes that state UNKNOWN (when / how it applies is not traced):
     player vars by T7_VAR_WRITERS, own flag (value >> 16) by T7_FLAG_WRITERS. Never a guessed write. */
  _applyWriters(entries) {
    const pv = this.evalState.playerVars, fl = this.evalState.playerFlags;
    for (const [c, p] of entries) {
      const v = T7_VAR_WRITERS[c];
      if (v != null && pv && pv[v] !== null) { pv[v] = null; this.stats.varsUnknown = (this.stats.varsUnknown || 0) + 1; }
      if (T7_FLAG_WRITERS[c] && fl) { const k = p >>> 16; if (k <= 0x63 && fl[k] !== null) { fl[k] = null; this.stats.flagsUnknown = (this.stats.flagsUnknown || 0) + 1; } }
    }
  }
  /** Advance one source frame. inp: { dir, down, held, special: [cmd] }. Returns this tick's record. */
  step(inp = {}) {
    const g = this.graph, m = this.move, f = this.frame;
    const clip = this.clipOf(m); const len = clip ? clip.frames : 0;
    const down = buttonsMask(inp.down), held = buttonsMask(inp.held) | down, dir = inp.dir || 'n';
    this.history.push({ dir, down, held });
    if (this.history.length > T7G_HISTORY) this.history.shift();
    this.stats.ticks += 1;
    if (!clip) this.stats.missingClip += 1;
    const sample = clip ? Math.min(Math.max(0, f - 1), clip.frames - 1) : null;
    const fwd = clip && clip.fwd ? clip.fwd[sample] : 0;
    const dFwd = this._prevFwd == null ? 0 : fwd - this._prevFwd; this._prevFwd = fwd;
    const rec = { tick: this.stats.ticks, moveId: this.moveId, name: m.name, frame: f, clipKey: this.clipKey(m), sample,
      len, dFwd, damage: m.damage || 0, active: !!(m.damage > 0 && m.first_active > 0 && f >= m.first_active && f <= m.last_active),
      attackId: this.attackId, hitlevelRaw: m.hitlevel, fired: null, skipped: [] };
    const sp = inp.special || [];
    const evalCond = makeEvalCond(this.evalState);
    let fire = null;
    if (this.pending) {
      if (f >= this.pending.at) fire = this.pending;
    } else {
      const r = stepCancel(g, this.moveId, { frame: f, moveLen: len, dir, down, held, history: this.history,
        special: (c) => sp.includes(c), evalCond, strict: this.strict });
      rec.skipped = r.skipped;
      if (r.ambiguous) { rec.ambiguous = r.ambiguous; this.stats.ambiguous = (this.stats.ambiguous || 0) + 1; }
      for (const s of r.skipped) {
        this.stats.skipped[s.reason] = (this.stats.skipped[s.reason] || 0) + 1;
        for (const c of s.unknown || []) this.stats.unknownConditions[c] = (this.stats.unknownConditions[c] || 0) + 1;
      }
      if (r.row) {
        // An earlier row skipped for an UNKNOWN condition could have outranked this one in the engine: the fire is
        // kept (the row's own requirements are all known + true) but flagged, never presented as certain.
        const unk = [...new Set(r.skipped.flatMap((s) => s.unknown || []))];
        const p = { to: r.to, at: r.at, index: r.index, cmd: r.row[0], acceptedFrame: f, via: 'cancel', precedenceUnknown: unk };
        if (r.at <= f) fire = p; else this.pending = p;
      }
    }
    if (!fire && len && f >= len) {
      // At the clip end the source falls through to `transition` only when no cancel fires. If an ambiguous row is still
      // open, that fall-through is not certain: hold the last frame (counted as a stall) instead of guessing.
      if (rec.ambiguous) { rec.stalled = true; this.stats.stalled = (this.stats.stalled || 0) + 1; return rec; }
      fire = { to: resolveMoveId(g, m.transition), via: 'transition', index: -1 };
    }
    if (fire) {
      rec.fired = { to: fire.to, toName: g.moves[fire.to] ? g.moves[fire.to].name : null, via: fire.via, index: fire.index,
        acceptedFrame: fire.acceptedFrame ?? f, appliedFrame: f, precedenceUnknown: fire.precedenceUnknown || [] };
      if (fire.via === 'transition') this.stats.transitions += 1; else this.stats.fired += 1;
      if (fire.via === 'cancel') this._varWriters(fire.index, m);
      if (rec.fired.precedenceUnknown.length) this.stats.precedenceUnknown = (this.stats.precedenceUnknown || 0) + 1;
      this._enter(fire.to);
    } else this.frame += 1;
    return rec;
  }
}

/** Clip table for the driver from a loaded wh-t7-graph-clips/1 bank: { key: { frames, fwd } }. */
export function driverClipsFromBank(clipData) {
  const out = {};
  for (const [k, d] of Object.entries(clipData)) {
    const n = d.root_t ? d.root_t.length : (d.frames || 0);
    out[k] = { frames: n, fwd: d.root_motion_fwd_m || null };
  }
  return out;
}
