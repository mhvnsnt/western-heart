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
  // Exe list semantics (0x1406f4750 and the inline copies at 0x140716fa4 / 0x140721634): acc = 1; for each entry
  // until id 0x371: acc = acc && eval(entry). So the list is a plain AND: ANY known-false entry makes it false, even
  // after an unknown one; it is true only when every entry is true; otherwise it is UNKNOWN.
  const unknown = [];
  for (const [c, p] of rows) {
    if (c === 0) continue; // 'always true'
    const v = evalCond ? evalCond(c, p, ctx) : null;
    if (v === false) return { ok: false, unknown: [], falseBy: c };
    if (v !== true) unknown.push(c);
  }
  return unknown.length ? { ok: false, unknown } : { ok: true, unknown };
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
  // STRICT: a row whose input/timing semantics are not proven (P1 button-less row on a press frame, mode-0 sequence
  // elements, undecoded specials that were signalled, unknown modes, cancel frames past the clip) could be the source's
  // choice unless its requirement list is known-false, so it blocks every lower row exactly like an unknown requirement.
  const uncertain = (i, r, reason, extra) => {
    skipped.push({ index: i, reason, ...extra });
    if (!ctx.strict) return null;
    const rq = evalRequirements(graph, r[F.req], ctx, ctx.evalCond);
    if (!rq.ok && !rq.unknown.length) return null; // known-false: cannot fire whatever the input semantics are
    return { row: null, index: -1, to: null, at: null, skipped, ambiguous: { index: i, unknown: rq.unknown, reason } };
  };
  for (let i = 0; i < mv.cancels.length; i++) {
    const r = mv.cancels[i]; const cmd = r[F.cmd];
    if (cmd === GROUP_END) continue;
    let at;
    if (cmd === AUTO) {
      at = r[F.start] || len;
      if (!at) { const u = uncertain(i, r, 'auto-len'); if (u) return u; continue; }
      if (f < at) continue;
    } else {
      if (r[F.start] && f < r[F.start]) continue;
      if (r[F.end] && r[F.end] !== WHOLE && f > r[F.end]) continue;
      if (cmd >= SEQ0 && cmd <= SEQ_MAX) {
        const m = matchSequence(graph, r[F.seq], ctx.history);
        if (m === null) { const u = uncertain(i, r, 'seq-mode', { seq: r[F.seq] }); if (u) return u; continue; }
        if (!m) continue;
      } else if (cmd > AUTO) {
        if (!KNOWN_SPECIALS[cmd]) { if (ctx.special && ctx.special(cmd)) { const u = uncertain(i, r, 'special', { cmd }); if (u) return u; } continue; }
        if (!(ctx.special && ctx.special(cmd))) continue;
      } else {
        if (!dirOk(r[F.dir], ctx.dir)) continue;
        const pp = r[F.buttons], mode = r[F.mode];
        if (r[F.held] && (held & r[F.held]) !== r[F.held]) continue;
        if (r[F.notHeld] && (held & r[F.notHeld])) continue;
        if (mode === MODE_AT_LEAST) { if (!pp || (down & pp) !== pp) continue; }
        else if (mode === MODE_ANY) { if (!(down & pp)) continue; }
        else if (mode === 0 && !pp) { if (down) { const u = uncertain(i, r, 'input-semantics'); if (u) return u; continue; } } // P1 (unproven)
        else { const u = uncertain(i, r, 'mode', { mode }); if (u) return u; continue; }
      }
      const sf = r[F.sf];
      if (sf === 0) at = len || null;
      else if (len && sf > len) at = null;
      else at = Math.max(sf, f);
      if (at == null) { const u = uncertain(i, r, 'timing', { sf }); if (u) return u; continue; }
    }
    const rq = evalRequirements(graph, r[F.req], ctx, ctx.evalCond);
    if (!rq.ok) {
      if (rq.unknown.length) {
        skipped.push({ index: i, reason: 'requirement', unknown: rq.unknown });
        // Strict precedence: this row's input, window and frame all matched, and only its requirement truth is unknown.
        // The engine takes the FIRST row whose requirements hold, so no lower row can be presented as the source's choice.
        if (ctx.strict) return { row: null, index: -1, to: null, at: null, skipped, ambiguous: { index: i, unknown: rq.unknown } };
      }
      continue;
    }
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
  225: 'controller type (exe, needs controller)', 809: 'player var [+0x938] == param (exe)', 359: 'player flag == value (exe)', 361: 'player var [+0x964] == param (exe)', 609: 'has item (exe, needs the equipped item set)', 135: 'on death', 558: 'story battle (false)', 636: 'assist button (false)', 811: 'basic combo (false)' };
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

/* Property ids that write player variables (exe property switch 0x1407198ac): id -> variable offset. */
export const T7_FLAG_WRITERS = { 0x8106: 'set', 0x8107: 'add', 0x8108: 'sub' }; // self flag [0x968 + (value>>16)*2]
export const T7_VAR_WRITERS = { 0x8414: 0x938, 0x8415: 0x938, 0x8416: 0x938, 0x80ed: 0x964, 0x8112: 0x964, 0x8113: 0x964 };

/* Requirement ids whose slot in the exe evaluator's jump table (0x1406f9478, 0x36C entries, evaluator 0x1406f5490) is the
 default case 0x1406f56e5 (`xor bl,bl` -> false); ids above 0x36B take the same default via `ja`. Extracted from the shipping
 exe (329 ids); these are source-proven ALWAYS FALSE in this build, independent of game state. */
export const T7_EXE_DEFAULT_FALSE = new Set([1,37,38,39,40,41,42,55,56,57,58,152,153,154,160,167,181,204,205,206,207,208,209,210,211,212,213,214,215,237,238,240,241,242,243,245,246,247,248,249,250,254,263,264,291,300,301,328,337,338,366,372,373,389,395,396,412,418,431,432,433,434,435,436,437,438,439,440,441,442,443,444,445,446,447,448,449,450,451,452,453,454,455,456,457,458,459,460,461,462,463,464,465,466,467,468,469,470,471,472,473,474,475,476,477,478,479,480,481,482,483,484,485,486,487,488,489,490,491,492,493,494,495,496,497,498,499,500,501,502,503,504,505,506,507,508,509,510,511,512,513,514,515,516,517,518,519,520,521,522,523,524,525,526,527,528,529,530,531,555,557,565,568,616,617,621,622,623,624,625,626,627,644,645,646,647,648,649,650,651,652,653,654,655,656,657,658,659,660,661,662,663,664,665,666,667,668,669,670,671,672,673,674,675,676,677,678,679,680,681,682,683,684,685,686,687,688,689,690,691,692,693,694,695,696,697,698,699,700,701,702,703,704,705,706,707,708,709,710,711,712,713,714,715,716,717,718,719,720,721,722,723,724,725,726,727,728,729,730,731,732,733,734,735,736,737,738,739,740,742,743,744,745,746,747,748,749,750,751,752,753,754,755,756,757,758,759,760,761,762,763,764,766,767,768,769,770,771,772,773,774,775,776,781,782,783,784,785,786,787,788,789,790,791,792,793,794,795,805,831,832,833,834,835,836,837,838,839,840]);

export function makeEvalCond(state) {
  return (c, p) => {
    if (!(c & 0x8000) && (c > 0x36b || T7_EXE_DEFAULT_FALSE.has(c))) return false; // exe default case
    if (c & 0x8000) return true; // exe 0x1406f54d9: an id with bit 0x8000 returns 1 before the switch
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
      // Player variables (exe): 809 = [self+0x938] == param (case 0x1406f7849), 361 = [self+0x964] == param (0x1406f7e2c).
      // Written ONLY by extra properties 0x8414/0x8415/0x8416 (set/add/sub [0x938]) and 0x80ed/0x8112/0x8113 ([0x964])
      // in the property switch at 0x1407198ac (id - 0x8001 jump table), and zeroed by the reset 0x140746ad0.
      // Player flags (exe case 0x1406f8298): idx = param >> 16 (must be <= 0x63), value = param low 16 bits sign-extended
      // (prologue 0x1406f5550..0x1406f556d); true when word [self+0x968+idx*2] == value. The init 0x140759a50 zeroes
      // all 100 words (rep stosw at 0x14075a065); writers are props 0x8106/0x8107/0x8108 (self).
      case 359: {
        const idx = p >> 16; if (idx > 0x63) return false;
        const lo = p & 0xffff, val = lo & 0x8000 ? lo - 0x10000 : lo;
        const fl = state.playerFlags; if (!fl || fl[idx] == null) return null;
        return fl[idx] === val;
      }
      case 809: return state.playerVars && state.playerVars[0x938] != null ? state.playerVars[0x938] === p : null;
      case 361: return state.playerVars && state.playerVars[0x964] != null ? state.playerVars[0x964] === p : null;
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
