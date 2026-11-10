/* t7graph.js — runtime interpreter for an imported Tekken 7 move graph (wh-t7-graph/1, tools/anim/t7_graph_import.py).
   Pure (no DOM / THREE): the fighter feeds it the current source move + frame and this frame's input, it returns the
   cancel the SOURCE table takes, in the table's own priority order (first match wins, as the engine walks the list).
   Semantics, all from the decoded table:
     - dir mask 0 = any direction; otherwise the stick's direction bit must be in the mask (bits 1..9 = d/b d d/f b n f
       u/b u u/f);
     - buttons: press flag set -> those buttons must go DOWN this frame (edge) and be the whole chord; no press flag and
       buttons -> held; no buttons -> a direction STATE test (e.g. dash 'f' held at frame 12 -> run);
     - window [start, end] in the move's frames (1-based), AUTO (0x8000) fires at starting_frame (0 = the move's end);
     - input sequences (cmd 0x800D+) match the decoded chronological inputs inside their own window;
     - requirements: every [condition, param] must evaluate TRUE through the caller's evaluator. A condition the
       evaluator does not know returns null -> the cancel is SKIPPED and reported (never satisfied by default).
   NOT interpreted here (kept raw in the graph): cancel_extradata values, cancel option; engine specials 0x8001..0x800A
   (double taps / sidesteps) are delegated to ctx.special(cmd). */
export const DIR_BITS = { 'd/b': 0x2, d: 0x4, 'd/f': 0x8, b: 0x10, n: 0x20, f: 0x40, 'u/b': 0x80, u: 0x100, 'u/f': 0x200 };
export const BTN_BITS = { 1: 1, 2: 2, 3: 4, 4: 8 };
const AUTO = 0x8000, SEQ0 = 0x800D, SEQ_MAX = 0x8FFF, GROUP_END = 0x800C;
const F = { cmd: 0, dir: 1, buttons: 2, press: 3, seq: 4, req: 5, start: 6, end: 7, sf: 8, to: 9 };

export function buttonsMask(list) { let m = 0; for (const b of list || []) m |= BTN_BITS[b] || 0; return m; }
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

/* Input history entry: { dir: 'f', down: [buttons pressed this frame] }, newest last. */
export function matchSequence(graph, seqIdx, history) {
  const s = graph.sequences[seqIdx]; if (!s || !history || !history.length) return false;
  const want = s.inputs; const win = Math.min(history.length, s.window || history.length);
  const h = history.slice(history.length - win);
  // last element must be on THIS frame (it carries the press); earlier ones in order, each a distinct stick state
  const last = want[want.length - 1], cur = h[h.length - 1];
  if (!dirOk(last[0], cur.dir) || (last[1] && !(last[2] ? edgeChord(last[1], cur.down) : true))) return false;
  let k = want.length - 2, prev = cur.dir;
  for (let i = h.length - 2; i >= 0 && k >= 0; i--) {
    if (h[i].dir === prev) continue; // a held state counts once
    prev = h[i].dir;
    if (dirOk(want[k][0], h[i].dir)) k--;
  }
  return k < 0;
}
function dirOk(mask, dir) { return mask === 0 || !!(mask & (DIR_BITS[dir] || 0)); }
function edgeChord(btns, down) { return buttonsMask(down) === btns; }

/* The cancel the source takes this frame, or null. ctx: { frame, dir, down: [btn], held: [btn], history,
   moveLen, special(cmd) -> bool, evalCond(cond, param, ctx) }. Returns { row, to, index, skipped: [{index, unknown}] }. */
export function stepCancel(graph, moveId, ctx) {
  const mv = graph.moves[moveId]; if (!mv) return null;
  const skipped = []; const down = buttonsMask(ctx.down), held = buttonsMask(ctx.held) | down;
  for (let i = 0; i < mv.cancels.length; i++) {
    const r = mv.cancels[i]; const cmd = r[F.cmd];
    if (cmd === GROUP_END) continue;
    if (cmd === AUTO) {
      const at = r[F.sf] || mv.len || ctx.moveLen || 0;
      if (ctx.frame < at) continue;
    } else {
      if (r[F.start] && ctx.frame < r[F.start]) continue;
      if (r[F.end] && ctx.frame > r[F.end]) continue;
      if (cmd >= SEQ0 && cmd <= SEQ_MAX) { if (!matchSequence(graph, r[F.seq], ctx.history)) continue; }
      else if (cmd > AUTO) { if (!(ctx.special && ctx.special(cmd))) continue; }
      else {
        if (!dirOk(r[F.dir], ctx.dir)) continue;
        const b = r[F.buttons];
        if (b) { if (r[F.press] ? down !== b : (held & b) !== b) continue; }
        else if (down) continue; // a button-less (state) link never eats a fresh press
      }
    }
    const rq = evalRequirements(graph, r[F.req], ctx, ctx.evalCond);
    if (!rq.ok) { if (rq.unknown.length) skipped.push({ index: i, unknown: rq.unknown }); continue; }
    return { row: r, index: i, to: resolveMoveId(graph, r[F.to]), skipped };
  }
  return { row: null, index: -1, to: null, skipped };
}

/* Condition ids this runtime evaluates, by their meaning in the community label table (TKMovesets2
   editor_t7_requirements.txt @a1b1917a). Only conditions that are labelled AND whose truth WH actually knows; every other
   id returns null (unknown -> the cancel is skipped and reported). Character-ID conditions (217/218/221-224) stay
   unknown: the label table lists 217 and 221 both as "Player character ID" and the T7 character-ID numbering is not
   in any source on hand. Distances are T7 units (state.oppDistT7); no metre conversion is assumed. */
export function makeEvalCond(state) {
  return (c, p) => {
    switch (c) {
      case 1: return false;                                                  // Practice mode move demo
      case 35: return state.oppDistT7 == null ? null : state.oppDistT7 <= p; // Opponent distance <= param
      case 36: return state.oppDistT7 == null ? null : state.oppDistT7 >= p; // Opponent distance >= param
      case 72: return !!state.backturned;                                    // Backturned
      case 135: return !!state.dead;                                         // On death
      case 558: return false;                                                // Story Battle (WH is never story mode)
      case 636: return false;                                                // Assist button pressed (WH has none)
      case 811: return false;                                                // Basic combo enabled (T7 assist mode)
      default: return null;
    }
  };
}
