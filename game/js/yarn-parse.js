/* ============================================================
   WESTERN HEART — Yarn Spinner (.yarn) parser + runner
   Yarn Spinner itself is C# (Unity/Godot, MIT); .yarn files are plain
   text, so WH reads them directly with this parser instead of porting
   the C# runtime. Dependency-free, browser + Node.
   Wire-in: game/js/versus-banter.js (versus banter dialogue) and
   game/js/heartmind.js (Heart and Mind Within dialogue) import
   parseYarn / YarnRunner from here. Ink (game/js/ink-loader.js) is
   the pick for heavily branching story; Yarn is the pick where
   writers author visually in the Yarn editor and hand WH .yarn files.
   Proven 2026-10-24 (workspace test, ~/workspace/pulls-wire/js-tests/):
   sample.yarn (Trader crossroads, Trial gate, Nine Souls) parses to
   5 nodes; Trial path yields souls=3, trial_done=true and the
   interpolated line "Souls gathered: 3"; CondTest yields RIGHT BRANCH
   (else) and never WRONG BRANCH; direct next()/choose() works.
   See docs/research/PULL-WIRE-PART2-2026-10-24.md.
   ============================================================ */

export function parseValue(raw, vars) {
  const s = String(raw).trim();
  if (s.startsWith('$')) return vars[s.slice(1)];
  if (/^-?\d+(\.\d+)?$/.test(s)) return Number(s);
  if (s === 'true') return true;
  if (s === 'false') return false;
  const q = s.match(/^"(.*)"$/) || s.match(/^'(.*)'$/);
  if (q) return q[1];
  return s;
}

function evalCondition(expr, vars) {
  const m = String(expr).trim().match(/^\$(\w+)\s*(==|!=|>=|<=|>|<)?\s*(.*)$/);
  if (!m) return false;
  const left = vars[m[1]];
  if (!m[2]) return !!left;
  const right = parseValue(m[3], vars);
  switch (m[2]) {
    case '==': return left == right; // eslint-disable-line eqeqeq
    case '!=': return left != right; // eslint-disable-line eqeqeq
    case '>': return left > right;
    case '<': return left < right;
    case '>=': return left >= right;
    case '<=': return left <= right;
    default: return false;
  }
}

export function parseYarn(text) {
  const chunks = String(text).replace(/^\uFEFF/, '').split(/^===\s*$/m);
  const nodes = {};
  const order = [];
  for (const chunk of chunks) {
    const lines = chunk.split(/\r?\n/);
    const sep = lines.findIndex((l) => l.trim() === '---');
    const header = sep >= 0 ? lines.slice(0, sep) : [];
    const body = sep >= 0 ? lines.slice(sep + 1) : lines;
    let title = null;
    for (const h of header) {
      const m = h.match(/^\s*title\s*:\s*(.+?)\s*$/i);
      if (m) title = m[1];
    }
    if (!title) continue;
    const steps = [];
    for (const rawLine of body) {
      const line = rawLine.trim();
      if (!line) continue;
      const cmd = line.match(/^<<(.+)>>$/);
      if (cmd) { steps.push({ type: 'command', raw: cmd[1].trim() }); continue; }
      const choice = line.match(/^\[\[(.+)\]\]$/);
      if (choice) {
        const inner = choice[1];
        const bar = inner.indexOf('|');
        steps.push(bar >= 0
          ? { type: 'choice', text: inner.slice(0, bar).trim(), target: inner.slice(bar + 1).trim() }
          : { type: 'choice', text: inner.trim(), target: inner.trim() });
        continue;
      }
      steps.push({ type: 'line', text: rawLine });
    }
    nodes[title] = steps;
    order.push(title);
  }
  return { nodes, order, start: order[0] || null };
}

export class YarnRunner {
  constructor(parsed, start) {
    this.nodes = parsed.nodes;
    this.vars = {};
    this.current = start || parsed.start;
    this.index = 0;
    this.done = false;
  }

  startNode(title) {
    if (!this.nodes[title]) throw new Error('yarn: unknown node ' + title);
    this.current = title;
    this.index = 0;
    this.done = false;
  }

  // Skip from an if/else step to its matching else/endif (or endif).
  _skipTo(steps, from, wantElse) {
    let depth = 0;
    for (let i = from; i < steps.length; i++) {
      const s = steps[i];
      if (s.type !== 'command') continue;
      if (/^if\b/.test(s.raw)) depth++;
      else if (s.raw === 'endif') {
        if (depth === 0) return i + 1;
        depth--;
      } else if (s.raw === 'else' && depth === 0 && wantElse) {
        return i + 1;
      }
    }
    return steps.length;
  }

  _interp(text) {
    return String(text).replace(/\{\$(\w+)\}/g, (_, name) =>
      this.vars[name] === undefined ? '' : String(this.vars[name]));
  }

  _execCommand(raw) {
    const set = raw.match(/^set\s+\$(\w+)\s+(?:=|to)\s+(.+)$/);
    if (set) { this.vars[set[1]] = parseValue(set[2], this.vars); return null; }
    const jump = raw.match(/^jump\s+(.+)$/);
    if (jump) { this.startNode(jump[1].trim()); return 'jumped'; }
    if (raw === 'stop') { this.done = true; return null; }
    return null; // if/else/endif handled by the step loop, unknown commands ignored
  }

  // Returns { type: 'line', text } | { type: 'choices', choices } |
  //         { type: 'end' } | { type: 'node', node }
  next() {
    if (this.done || !this.current) return { type: 'end' };
    const steps = this.nodes[this.current];
    if (!steps) return { type: 'end' };
    while (this.index < steps.length) {
      const step = steps[this.index];
      if (step.type === 'line') {
        this.index++;
        return { type: 'line', text: this._interp(step.text).trim() };
      }
      if (step.type === 'choice') {
        const choices = [];
        while (this.index < steps.length && steps[this.index].type === 'choice') {
          choices.push(steps[this.index]);
          this.index++;
        }
        this._pendingChoices = choices;
        return { type: 'choices', choices };
      }
      // command
      this.index++;
      const raw = step.raw;
      if (/^if\b/.test(raw)) {
        const ok = evalCondition(raw.replace(/^if\s+/, ''), this.vars);
        if (!ok) this.index = this._skipTo(steps, this.index, true);
        continue;
      }
      if (raw === 'else') {
        // Reached else after a taken if-branch: skip to endif.
        this.index = this._skipTo(steps, this.index, false);
        continue;
      }
      if (raw === 'endif') continue;
      if (this._execCommand(raw) === 'jumped') return { type: 'node', node: this.current };
    }
    this.done = true;
    return { type: 'end' };
  }

  choose(i) {
    const out = this._pendingChoices;
    if (!out) throw new Error('yarn: choose() called with no pending choices');
    const target = out[i] && out[i].target;
    if (!target) throw new Error('yarn: bad choice index ' + i);
    this.startNode(target);
    this._pendingChoices = null;
    return { type: 'node', node: target };
  }

  // Convenience: run to end, auto-picking choices via pickFn(choices)->index.
  run(pickFn) {
    const lines = [];
    let guard = 0;
    for (;;) {
      if (++guard > 10000) throw new Error('yarn: runaway dialogue');
      const out = this.next();
      if (out.type === 'line') lines.push(out.text);
      else if (out.type === 'choices') {
        this._pendingChoices = out.choices;
        this.choose(pickFn ? pickFn(out.choices) : 0);
      } else break;
    }
    return lines;
  }
}
