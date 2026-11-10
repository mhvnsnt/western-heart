/* t7graph.js — runtime interpreter for an imported Tekken 7 move graph (wh-t7-graph/2, tools/anim/t7_graph_import.py).
   Pure (no DOM / THREE): the caller feeds the current source move + frame and this frame's input; stepCancel returns
   the cancel the SOURCE table takes, in the table's own order (first match wins, as the engine walks the list), and
   WHEN it applies. Semantics, all from the decoded table (decoding sources in the importer's docstring):
     - dir mask 0 = any direction; otherwise the stick's direction bit must be in the mask (bits 1..9 = d/b d d/f b n
       f u/b u u/f);
     - button command 0xMMNNHHPP: mode 0x40 = the PP buttons (at least) go DOWN this frame; 0x20 = any one of the PP
       buttons goes down; mode 0 = a state row (direction + HH held + NN not-held, no press);
     - input window [start, end] in the move's frames (1-based; 32767 = the whole move);
     - cancel frame (starting_frame): the frame of the CURRENT move the cancel is applied on (an earlier accepted
       input waits for it, TekkenMods "Cancel Frame"); 0 with an input = at the animation's end. A cancel frame past
       the animation (e.g. 32767) has no proven meaning -> skipped and reported ('timing');
     - AUTO (0x8000) ends the list and applies at its window start, or at the animation end when that is 0;
     - input sequences (0x800D+) match the recorded inputs inside the sequence's own window (mode 0x80 = a direction
       with no press; 0x40 = a press); a sequence element of mode 0 WITH buttons has no proven meaning -> 'seq-mode';
     - engine specials: 0x8001 / 0x8002 (double-tap f / b) through ctx.special(cmd); 0x8003+ -> 'special' (unknown);
     - requirements: every [condition, param] must be TRUE through ctx.evalCond; a condition the evaluator does not
       know returns null -> the cancel is SKIPPED and reported (never satisfied by default).
   WH runtime policies that the source does not prove (named, reported in docs/proof/2026-11-10/t7-graph-adapter):
     P1 a button-less state row does not take a frame on which a button went down;
     P2 sequence elements match as an ordered subsequence of the input events inside the window (contiguity unproven);
     P3 the first accepted, not-yet-applied cancel is kept until its cancel frame (later inputs do not replace it).
   NOT interpreted (kept raw in the graph): cancel_extradata values, cancel option. */
export const DIR_BITS = { 'd/b': 0x2, d: 0x4, 'd/f': 0x8, b: 0x10, n: 0x20, f: 0x40, 'u/b': 0x80, u: 0x100, 'u/f': 0x200 };
export const BTN_BITS = { 1: 1, 2: 2, 3: 4, 4: 8 };
export const AUTO = 0x8000, GROUP_END = 0x800C, SEQ0 = 0x800D, SEQ_MAX = 0x8FFF, WHOLE = 32767;
export const MODE_AT_LEAST = 0x40, MODE_ANY = 0x20, MODE_DIR_ONLY = 0x80;
export const F = { cmd: 0, dir: 1, buttons: 2, mode: 3, seq: 4, req: 5, start: 6, end: 7, sf: 8, to: 9, option: 10,
  extradata: 11, group: 12, held: 13, notHeld: 14, raw: 15 };
export const KNOWN_SPECIALS = { 0x8001: 'double-tap f', 0x8002: 'double-tap b' };

export function buttonsMask(list) {
  if (typeof list === 'number') return list;
  let m = 0; for (const b of list || []) for (const p of String(b).split('+')) m |= BTN_BITS[p] || 0; return m;
}
export function resolveMoveId(graph, id) {
  return id >= 0x8000 && id - 0x8000 < graph.aliases.length ? graph.aliases[id - 0x8000] : id;
}
export function moveByName(graph, name) {
  if (!graph._byName) { graph._byName = new Map(); for (const m of graph.moves) if (!graph._byName.has(m.name)) graph._byName.set(m.name, m.id); }
  return graph._byName.get(name);
}

/* Evaluate one requirement list. evalCond(cond, param, ctx) -> true | false | null (unknown). */
export function evalRequirements(graph, reqIdx, ctx, evalCond) {
  const rows = graph.requirements[String(reqIdx)] || [];
  const unknown = [];
  for (const [c, p] of rows) {
    if (c === 0) continue; // 'always true'
    const v = evalCond ? evalCond(c, p, ctx) : null;
    if (v === false) return { ok: false, unknown };
    if (v !== true) { unknown.push(c); return { ok: false, unknown }; }
  }
  return { ok: true, unknown };
}

function dirOk(mask, dir) { return mask === 0 || !!(mask & (DIR_BITS[dir] || 0)); }

/* Input events inside the last `win` frames of history (one entry per 60 Hz frame, newest last:
   { dir, down: mask|list, held: mask|list }): a new event on every frame a button goes down or the stick changes. */
function inputEvents(history, win) {
  const h = history.slice(Math.max(0, history.length - win));
  const ev = [];
  for (let i = 0; i < h.length; i++) {
    const d = buttonsMask(h[i].down);
    if (i === 0 || d || h[i].dir !== h[i - 1].dir) ev.push({ dir: h[i].dir, down: d, held: buttonsMask(h[i].held) | d, frame: i });
  }
  return { ev, lastFrame: h.length - 1 };
}
function elementOk(e, x) {
  const [dm, pp, mode, hh, nn] = e;
  if (!dirOk(dm, x.dir)) return false;
  if (hh && (x.held & hh) !== hh) return false;
  if (nn && (x.held & nn)) return false;
  if (mode === MODE_DIR_ONLY) return x.down === 0;
  if (mode === MODE_AT_LEAST) return pp !== 0 && (x.down & pp) === pp;
  if (mode === MODE_ANY) return (x.down & pp) !== 0;
  return pp ? null : x.down === 0; // mode 0 + buttons: unproven
}
/* true | false | null (an element whose mode has no proven meaning). The last element must be THIS frame's input. */
export function matchSequence(graph, seqIdx, history) {
  const s = graph.sequences[seqIdx]; if (!s) return false;
  if (s.inputs.some((e) => e[2] === 0 && e[1])) return null;
  if (!history || !history.length) return false;
  const { ev, lastFrame } = inputEvents(history, Math.max(1, s.window || history.length));
  const want = s.inputs; const cur = ev[ev.length - 1];
  if (!cur || cur.frame !== lastFrame || !elementOk(want[want.length - 1], cur)) return false;
  let k = want.length - 2;
  for (let i = ev.length - 2; i >= 0 && k >= 0; i--) if (elementOk(want[k], ev[i])) k--; // P2
  return k < 0;
}

/* The cancel the source takes on this frame, or row null. ctx: { frame, moveLen (animation frames), dir,
   down: buttons that went down this frame, held: buttons held, history, special(cmd) -> bool, evalCond }.
   Returns { row, index, to, at, skipped: [{ index, reason, unknown? , cmd? }] } — `at` is the frame of the current
   move the cancel applies on (>= frame). */
export function stepCancel(graph, moveId, ctx) {
  const mv = graph.moves[moveId]; if (!mv) return null;
  const skipped = []; const down = buttonsMask(ctx.down), held = buttonsMask(ctx.held) | down;
  const len = ctx.moveLen || 0, f = ctx.frame;
  for (let i = 0; i < mv.cancels.length; i++) {
    const r = mv.cancels[i]; const cmd = r[F.cmd];
    if (cmd === GROUP_END) continue;
    let at;
    if (cmd === AUTO) {
      at = r[F.start] || len;
      if (!at) { skipped.push({ index: i, reason: 'auto-len' }); continue; }
      if (f < at) continue;
    } else {
      if (r[F.start] && f < r[F.start]) continue;
      if (r[F.end] && r[F.end] !== WHOLE && f > r[F.end]) continue;
      if (cmd >= SEQ0 && cmd <= SEQ_MAX) {
        const m = matchSequence(graph, r[F.seq], ctx.history);
        if (m === null) { skipped.push({ index: i, reason: 'seq-mode', seq: r[F.seq] }); continue; }
        if (!m) continue;
      } else if (cmd > AUTO) {
        if (!KNOWN_SPECIALS[cmd]) { if (ctx.special && ctx.special(cmd)) skipped.push({ index: i, reason: 'special', cmd }); continue; }
        if (!(ctx.special && ctx.special(cmd))) continue;
      } else {
        if (!dirOk(r[F.dir], ctx.dir)) continue;
        const pp = r[F.buttons], mode = r[F.mode];
        if (r[F.held] && (held & r[F.held]) !== r[F.held]) continue;
        if (r[F.notHeld] && (held & r[F.notHeld])) continue;
        if (mode === MODE_AT_LEAST) { if (!pp || (down & pp) !== pp) continue; }
        else if (mode === MODE_ANY) { if (!(down & pp)) continue; }
        else if (mode === 0 && !pp) { if (down) continue; } // P1
        else { skipped.push({ index: i, reason: 'mode', mode }); continue; }
      }
      const sf = r[F.sf];
      if (sf === 0) at = len || null;
      else if (len && sf > len) at = null;
      else at = Math.max(sf, f);
      if (at == null) { skipped.push({ index: i, reason: 'timing', sf }); continue; }
    }
    const rq = evalRequirements(graph, r[F.req], ctx, ctx.evalCond);
    if (!rq.ok) { if (rq.unknown.length) skipped.push({ index: i, reason: 'requirement', unknown: rq.unknown }); continue; }
    return { row: r, index: i, to: resolveMoveId(graph, r[F.to]), at: Math.max(at, f), skipped };
  }
  return { row: null, index: -1, to: null, at: null, skipped };
}

/* Condition ids this runtime evaluates, by their meaning in the community label table (TKMovesets2
   editor_t7_requirements.txt @a1b1917a). Only conditions that are labelled AND whose truth WH actually knows; every other
   id returns null (unknown -> the cancel is skipped and reported). Character-ID conditions (217/218/221-224) stay
   unknown: the label table lists 217 and 221 both as "Player character ID" and the T7 character-ID numbering is not
   in any source on hand. Distances are T7 units (state.oppDistT7); no metre conversion is assumed, so in the game
   (where no T7-unit distance exists) 35 / 36 stay unknown. */
export const KNOWN_CONDITIONS = { 1: 'practice demo (false)', 35: 'opp dist <= (T7 units)', 36: 'opp dist >= (T7 units)',
  72: 'backturned (exe, needs relHeading16)', 73: 'not backturned (exe, needs relHeading16)', 80: 'rel heading in [0x3fff,0x7fff] (exe)', 81: 'rel heading in [0x8000,0xbfff] (exe)', 217: 'self chara_id == param (exe, needs charId)',
  225: 'controller type (exe, needs controller)', 609: 'has item (exe, needs the equipped item set)', 135: 'on death', 558: 'story battle (false)', 636: 'assist button (false)', 811: 'basic combo (false)' };
/* Requirement 217 params 76..90 → the chara_id they test, read from the exe helper 0x1406f46a0's jump table
   (TekkenGame-Win64-Shipping.exe; see docs/proof/2026-11-10/t7-requirements/README.md). */
export const T7_CHAR_GROUPS = { 76: 0x21, 77: 0x22, 78: 0x23, 79: 0x3d, 80: 0x4b, 81: 0x1f, 82: 0x4b, 83: 5, 84: 0x4b,
  85: 0x45, 86: 0x4b, 87: 0x1e, 88: 0x4b, 89: 0x0f, 90: 0x4b };

/* [self+0x1c4] from [self+0x1c2] exactly as 0x1406ec17f..0x1406ec18e computes it (rel >= 0x8000 -> ~rel). */
export function t7FacingFold(state) {
  if (state.relHeading16 == null) return null;
  const rel = state.relHeading16 & 0xffff;
  return rel >= 0x8000 ? (~rel & 0xffff) : rel;
}

export function makeEvalCond(state) {
  return (c, p) => {
    switch (c) {
      case 1: return false;                                                  // Practice mode move demo
      case 35: return state.oppDistT7 == null ? null : state.oppDistT7 <= p; // Opponent distance <= param
      case 36: return state.oppDistT7 == null ? null : state.oppDistT7 >= p; // Opponent distance >= param
      // Facing family (exe 0x1406ebfe0, per frame): rel = [self+0x1c2] = (own yaw - bearing to opponent) as a 16-bit
      // binary angle; [self+0x1c4] = rel folded to 0..0x7fff. Evaluated only from an explicit relHeading16.
      case 72: { const f = t7FacingFold(state); return f == null ? null : f > 0x4000; }   // Backturned  (exe 0x1406f5bdd)
      case 73: { const f = t7FacingFold(state); return f == null ? null : f <= 0x4000; }  // Not backturned (0x1406f5bf1)
      case 80: return state.relHeading16 == null ? null : ((state.relHeading16 - 0x3fff) & 0xffff) <= 0x4000; // 0x1406f5cd5
      case 81: return state.relHeading16 == null ? null : ((state.relHeading16 + 0x8000) & 0xffff) <= 0x3fff; // 0x1406f5cf4
      case 217: {                                                            // Player character ID: exe chara_id [self+0xD8] == param,
        if (state.charId == null) return null;                               // params 76..90 are exe-coded groups (T7_CHAR_GROUPS)
        const grp = T7_CHAR_GROUPS[p];
        return grp != null ? state.charId === grp : state.charId === p;
      }
      case 225: {                                                            // Character Controller: exe [self+0x1570] (0 = player)
        if (state.controller == null) return null;
        if (state.controller === 0) return p === 0;                          // a player-controlled fighter: true only for param 0 (both exe paths)
        return p === 0 ? null : state.controller === p;                      // param 0 for a non-player depends on unmodelled exe flags
      }
      case 609:                                                              // Has item: exe asks the customization object (side, item id);
        return Array.isArray(state.items) ? state.items.includes(p) : null;  // false when a global byte is set. Needs the full equipped set.
      case 135: return state.dead == null ? null : !!state.dead;             // On death
      case 558: return false;                                                // Story Battle (WH is never story mode)
      case 636: return false;                                                // Assist button pressed (WH has none)
      case 811: return false;                                                // Basic combo enabled (T7 assist mode)
      default: return null;
    }
  };
}
