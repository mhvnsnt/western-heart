// TOUCH-BUTTON WIRING TEST (no browser).
// Stubs the DOM, instantiates the REAL InputManager from game/js/input.js,
// dispatches real 'touchstart' events on the PSX face buttons (same markup as
// game/index.html), and asserts the queue receives the correct Tekken limb.
// This is the exact path a user's tap takes: touchstart -> _tekken('1') ->
// _push('1') -> game._update consumes -> p1.tryAttack('1').
import { readFile } from 'fs/promises';

function makeEl(dataset) {
  const listeners = {};
  return {
    dataset, style: {},
    _listeners: listeners,
    addEventListener: (t, fn) => { (listeners[t] = listeners[t] || []).push(fn); },
    dispatch: (type) => {
      const e = { type, preventDefault() {}, target: null };
      for (const fn of listeners[type] || []) fn(e);
    },
  };
}
// Same buttons as game/index.html (PSX diamond + shoulders + transform).
const buttons = ['2', '4', '3', '1', 'block', 'surge', 'transform'].map(b => makeEl({ btn: b }));
const joy = makeEl({}), knob = makeEl({});
globalThis.document = {
  querySelectorAll: (sel) => (sel === '.act-btn' ? buttons : []),
  getElementById: (id) => (id === 'joystick' ? joy : id === 'joystick-knob' ? knob : null),
};
globalThis.window = { addEventListener: () => {} };

const src = await readFile(new URL('../../game/js/input.js', import.meta.url), 'utf8');
const modSrc = src.replace(/^export /gm, '');
const factory = new Function(`${modSrc}\nreturn { InputManager };`);
const { InputManager } = factory();

const im = new InputManager();
im.init();
im.enable(true);

let pass = 0, fail = 0;
const check = (label, actual, expected) => {
  const ok = JSON.stringify(actual) === JSON.stringify(expected);
  ok ? pass++ : fail++;
  console.log(`${ok ? 'PASS' : 'FAIL'} ${label}: got ${JSON.stringify(actual)}${ok ? '' : ` want ${JSON.stringify(expected)}`}`);
};

// Button-by-button: tap each PSX face button -> its Tekken limb in the queue.
// (Zero the 140ms chord windows between taps so rapid test taps don't chain.)
for (const [dataBtn, want] of [['1', ['1']], ['2', ['2']], ['3', ['3']], ['4', ['4']]]) {
  im.consume();
  im._lastT = { '1': 0, '2': 0, '3': 0, '4': 0 };
  buttons.find(b => b.dataset.btn === dataBtn).dispatch('touchstart');
  check(`tap data-btn="${dataBtn}" -> queue`, im.consume(), want);
}
// Every button is functional: shoulders + transform queue; block is hold-type.
for (const b of ['surge', 'transform']) {
  im.consume();
  im._lastT = { '1': 0, '2': 0, '3': 0, '4': 0 };
  buttons.find(x => x.dataset.btn === b).dispatch('touchstart');
  const q = im.consume();
  check(`tap data-btn="${b}" functional`, q.length > 0, true);
}
{
  const blk = buttons.find(x => x.dataset.btn === 'block');
  blk.dispatch('touchstart');
  check('tap data-btn="block" functional (hold)', im.held.block, true);
  blk.dispatch('touchend');
}
// Block is hold-type: touchstart sets held, touchend clears.
{
  const blk = buttons.find(x => x.dataset.btn === 'block');
  blk.dispatch('touchstart'); check('block held on touchstart', im.held.block, true);
  blk.dispatch('touchend'); check('block released on touchend', im.held.block, false);
}
// Chord: 1 then 3 within 140ms -> single '1' at once, then '1+3' throw chord.
// (Zero the chord windows first: rapid test taps would otherwise chain.)
{
  im.consume();
  im._lastT = { '1': 0, '2': 0, '3': 0, '4': 0 };
  const b1 = buttons.find(x => x.dataset.btn === '1');
  const b3 = buttons.find(x => x.dataset.btn === '3');
  b1.dispatch('touchstart'); b3.dispatch('touchstart');
  check(`tap 1 then 3 -> chord queue`, im.consume(), ['1', '1+3']);
}
// Disabled input swallows taps (menu state) — nothing queued.
{
  im.enable(false);
  buttons.find(x => x.dataset.btn === '1').dispatch('touchstart');
  check('disabled input queues nothing', im.consume(), []);
  im.enable(true);
}
console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
