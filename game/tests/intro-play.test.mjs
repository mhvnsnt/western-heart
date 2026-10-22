/* Node integration test: playIntroInteraction presentation flow.
   Stubs a functional-enough DOM + the voice module's playLine to capture calls. */
function makeEl(id) {
  const el = {
    id, children: [], _cls: new Set(), _listeners: {}, textContent: '',
    setAttribute() {},
    appendChild(c) { el.children.push(c); return c; },
    addEventListener(t, f) { (el._listeners[t] = el._listeners[t] || []).push(f); },
    removeEventListener(t, f) { el._listeners[t] = (el._listeners[t] || []).filter(x => x !== f); },
    querySelector(sel) {
      const map = { '.wh-intro-name': '_name', '.wh-intro-line': '_line', '.wh-intro-skip': '_skip' };
      const k = map[sel];
      if (!k) return null;
      if (!el[k]) el[k] = makeEl(k);
      return el[k];
    },
    classList: {
      add: (c) => el._cls.add(c), remove: (c) => el._cls.delete(c),
      contains: (c) => el._cls.has(c),
    },
    set innerHTML(v) { el.children = []; }, get innerHTML() { return ''; },
    click() { (el._listeners.click || []).forEach(f => f({ target: el })); },
  };
  return el;
}
const els = {};
global.document = {
  getElementById: (id) => els[id] || null,
  createElement: () => makeEl('dyn'),
  head: { appendChild() {} },
  body: { appendChild(el) { els[el.id] = el; } },
};

// capture voice.playLine calls instead of playing
const calls = [];
const voiceMod = await import('../js/voice.js');
const origPlayLine = voiceMod.voice.playLine.bind(voiceMod.voice);
voiceMod.voice.playLine = async (fighterId, clipId, text) => {
  calls.push({ fighterId, clipId, text });
  return origPlayLine(fighterId, clipId, text);
};
// speed up: shrink subtitle hold by stubbing _wait
voiceMod.voice._wait = (ms) => new Promise(r => setTimeout(r, 30));

const { playIntroInteraction, _resetIntroMemory } = await import('../js/intro-interactions.js');
let pass = 0, fail = 0;
const ok = (c, m) => { c ? pass++ : (fail++, console.log('FAIL:', m)); };

const p1 = { id: 'dorowani', name: 'DOROWANI' };
const p2 = { id: 'pantera', name: 'PANTERA' };

// 1. full interaction plays beats in order with voice refs
_resetIntroMemory(); calls.length = 0;
const r1 = await playIntroInteraction({}, p1, p2);
ok(r1.kind === 'pair', `pair interaction played (kind=${r1.kind})`);
const { INTRO_INTERACTIONS: DB } = await import('../js/intro-interactions.js');
const played = DB['dorowani|pantera'].find(v => v.id === r1.variant);
ok(calls.length === played.beats.length,
   `${played.beats.length} beats fired voice lines (got ${calls.length})`);
played.beats.forEach((b, i) => {
  ok(calls[i].fighterId === b.speaker && calls[i].text === b.line,
     `beat ${i + 1} = ${b.speaker} "${b.line}"`);
  ok(calls[i].clipId === b.voice, `beat ${i + 1} carries voice clip ref ${b.voice}`);
});
const ov = els['wh-intro'];
ok(ov && !ov.classList.contains('show'), 'overlay hidden after interaction');

// 2. overlay showed the matchup title-card for unknown pair
_resetIntroMemory(); calls.length = 0;
const r2 = await playIntroInteraction({}, { id: 'skull', name: 'SKULL' }, { id: 'zen', name: 'ZEN' });
ok(r2.kind === 'versus', 'versus fallback for unscripted pair');
const lineEl = els['wh-intro'].querySelector('.wh-intro-line');
ok(lineEl.textContent.includes('SKULL') && lineEl.textContent.includes('ZEN'),
   `versus card shows both names ("${lineEl.textContent}")`);

// 3. skip resolves immediately
_resetIntroMemory(); calls.length = 0;
const p = playIntroInteraction({}, p1, p2);
setTimeout(() => els['wh-intro'].querySelector('.wh-intro-skip').click(), 50);
const r3 = await p;
ok(r3.skipped === true, 'skip button ends the interaction');

// 4. opts.skip bypasses everything
calls.length = 0;
const r4 = await playIntroInteraction({}, p1, p2, { skip: true });
ok(r4.skipped === true && calls.length === 0, 'opts.skip fires no beats');

// 5. variant rotation: two consecutive interactions differ
_resetIntroMemory();
const ra = await playIntroInteraction({}, p1, p2);
const rb = await playIntroInteraction({}, p1, p2);
ok(ra.variant !== rb.variant, `consecutive intros rotate (${ra.variant} -> ${rb.variant})`);

console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
