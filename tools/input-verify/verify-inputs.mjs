// INPUT-TO-MOVE FIDELITY PROOF (moveset lane, worker 11).
// Real keyboard input -> which move each Tekken input fires, on the live game.
// node tools/input-verify/verify-inputs.mjs OUTDIR [p1] [p2]
// Serve the repo first: python3 -m http.server 8765 (from the repo root).
//
// Proves the owner's law: "in Tekken every input produces a specific,
// predictable move — press 1, left punch comes out, every time."
//   * determinism: 1/2/3/4 pressed 3x each -> identical notation every time
//   * distinctness: 1/2/3/4 -> four distinct moves
//   * singles, all 6 chords, directionals, WS./FC./SS./BT. states,
//     strings (1,2 / 1,2,2 / 2,1 / f+2,1), motions (f,F+2, qcf+2)
//   * per-input screenshot + results.json (notation, key, name, hit word,
//     anim ref, defender HP delta, state machine trace)
import { chromium } from 'playwright-core';
import fs from 'fs';
import path from 'path';

const [,, out = 'input-proof', p1 = 'torch', p2 = 'pantera'] = process.argv;
fs.mkdirSync(out, { recursive: true });
const shot = (n) => path.join(out, n.replace(/[^a-z0-9]+/gi, '_') + '.png');

const browser = await chromium.launch({
  executablePath: process.env.CHROMIUM_PATH || '/opt/meta-chromium/chrome',
  args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader',
         '--ignore-gpu-blocklist', '--no-sandbox',
         '--disable-features=LocalNetworkAccessChecks,PrivateNetworkAccessSendPreflights'],
});
const page = await browser.newPage({ viewport: { width: 960, height: 540 } });
const logs = [];
page.on('console', m => { if (/error|warn|\[WH\]/i.test(m.text())) logs.push(`[${m.type()}] ${m.text()}`); });
page.on('pageerror', e => logs.push(`[pageerror] ${e.message}`));

console.log('loading page');
await page.goto('http://localhost:8765/game/index.html', { waitUntil: 'load' });
await page.waitForTimeout(1500);
// NOTE (2026-10-22): bypass the select screen — the menu lane's T8 grid
// transplant (PR #588) currently crashes startMode('arcade') in
// select-screen.js renderPlate (null plateEls). Input verification starts the
// fight directly via __modes.startFight (menu-independent) and does not touch
// select-screen layout.
console.log('starting fight', p1, 'vs', p2);
// Software GL in this container cannot draw the stage at a usable rate; the
// game logic runs unchanged. Arena renders once per screenshot.
await page.evaluate(() => { const a = window.__game.arena; a.__render = a.render.bind(a); a.render = () => {}; });
await page.evaluate(async ([a, b]) => { await window.__modes.startFight(a, b, { mode: 'arcade' }); }, [p1, p2]);
await page.waitForFunction(() => window.__game && window.__game.roundState === 'fight', null, { timeout: 120000 })
  .catch(() => console.log('!! round never reached fight state'));
console.log('round state:', await page.evaluate(() => window.__game && window.__game.roundState));
await page.waitForTimeout(1200);
// Freeze the CPU so scripted inputs are the only thing moving.
await page.evaluate(() => {
  const g = window.__game;
  g.ai.update = () => {}; g.timer = 999;
  g.p2.root.position.x = g.p1.root.position.x + 1.15 * g.p1.facing;
});

const key = async (k, ms = 40) => { await page.keyboard.down(k); await page.waitForTimeout(ms); await page.keyboard.up(k); };
const state = () => page.evaluate(() => {
  const g = window.__game, f = g.p1, a = f.attack;
  return {
    state: f.state, notation: f.attackName, key: a && a.moveKey, name: a && a.moveName,
    word: a && a.hitWord, anim: a && (a.t3row != null ? `t3row ${a.t3row}` : a.animRow != null ? `anim ${a.animBank}:${a.animRow}` : null),
    stance: f.stance, stateT: +f.stateT.toFixed(3),
    p2hp: +g.p2.hp.toFixed(1), p1hp: +g.p1.hp.toFixed(1), rage: !f._rageUsed && f.hp <= f.maxHp * 0.25,
  };
});
const reset = () => page.evaluate(() => {
  const g = window.__game;
  g.input.consume(); // drain any presses the slow frame loop hasn't eaten yet
  g.p1.hp = 100; g.p2.hp = 100; g.p1._enter('idle'); g.p2._enter('idle');
  g.p2.stun = 0; g.p1.stun = 0;
  const t = g.p1.tekken;
  t.lastMove = null; t.lastMoveT = 0; t.lastDir = 'n';
  t.hist.fill('n'); t.dirEvents.length = 0; t._dash = null;
  g.p1._queuedNext = null;
  g.p1.stance = null; g.p2.stance = null;
  g.p2.root.position.x = g.p1.root.position.x + 1.15 * g.p1.facing;
  g.p1.root.position.z = 0; g.p2.root.position.z = 0;
  g.input.consume();
});
// Wait until p1 is idle and the input queue is empty (slow software-GL frames
// can otherwise deliver a previous case's press into the next case).
const settle = () => page.waitForFunction(() => {
  const g = window.__game;
  return g.p1.state === 'idle' && g.p1.stun <= 0;
}, null, { timeout: 15000 }).catch(() => console.log('!! settle timed out'));
const fps = await page.evaluate(() => new Promise((res) => {
  let n = 0; const t0 = performance.now();
  const tick = () => { n++; if (performance.now() - t0 < 2000) requestAnimationFrame(tick); else res((n / 2).toFixed(1)); };
  requestAnimationFrame(tick);
}));
console.log('rAF fps in this environment:', fps);
const render = () => page.evaluate(() => window.__game.arena.__render());

const fwd = await page.evaluate(() => window.__game.p1.facing > 0 ? 'ArrowRight' : 'ArrowLeft');
const back = fwd === 'ArrowRight' ? 'ArrowLeft' : 'ArrowRight';
console.log('fwd key:', fwd);

// Each case: label, async runner, when to sample ('early' ~90ms after input for
// attackName, else settled). Runner must leave p1 idle-ish when done.
const cases = [
  ['1 jab', async () => key('Digit1')],
  ['2', async () => key('Digit2')],
  ['3', async () => key('Digit3')],
  ['4', async () => key('Digit4')],
  ['1+2', async () => { await page.keyboard.down('Digit1'); await page.keyboard.down('Digit2'); await page.waitForTimeout(40); await page.keyboard.up('Digit1'); await page.keyboard.up('Digit2'); }],
  ['3+4', async () => { await page.keyboard.down('Digit3'); await page.keyboard.down('Digit4'); await page.waitForTimeout(40); await page.keyboard.up('Digit3'); await page.keyboard.up('Digit4'); }],
  ['1+3 throw', async () => { await page.keyboard.down('Digit1'); await page.keyboard.down('Digit3'); await page.waitForTimeout(40); await page.keyboard.up('Digit1'); await page.keyboard.up('Digit3'); }],
  ['2+4 throw', async () => { await page.keyboard.down('Digit2'); await page.keyboard.down('Digit4'); await page.waitForTimeout(40); await page.keyboard.up('Digit2'); await page.keyboard.up('Digit4'); }],
  ['1+4', async () => { await page.keyboard.down('Digit1'); await page.keyboard.down('Digit4'); await page.waitForTimeout(40); await page.keyboard.up('Digit1'); await page.keyboard.up('Digit4'); }],
  ['2+3', async () => { await page.keyboard.down('Digit2'); await page.keyboard.down('Digit3'); await page.waitForTimeout(40); await page.keyboard.up('Digit2'); await page.keyboard.up('Digit3'); }],
  ['f+1', async () => { await page.keyboard.down(fwd); await page.waitForTimeout(400); await key('Digit1'); await page.keyboard.up(fwd); }],
  ['f+2', async () => { await page.keyboard.down(fwd); await page.waitForTimeout(400); await key('Digit2'); await page.keyboard.up(fwd); }],
  ['f+3', async () => { await page.keyboard.down(fwd); await page.waitForTimeout(400); await key('Digit3'); await page.keyboard.up(fwd); }],
  ['f+4', async () => { await page.keyboard.down(fwd); await page.waitForTimeout(400); await key('Digit4'); await page.keyboard.up(fwd); }],
  ['b+1', async () => { await page.keyboard.down(back); await page.waitForTimeout(400); await key('Digit1'); await page.keyboard.up(back); }],
  ['d+1', async () => { await page.keyboard.down('ArrowDown'); await page.waitForTimeout(400); await key('Digit1'); await page.keyboard.up('ArrowDown'); }],
  ['d/f+1', async () => { await page.keyboard.down('ArrowDown'); await page.keyboard.down(fwd); await page.waitForTimeout(400); await key('Digit1'); await page.keyboard.up(fwd); await page.keyboard.up('ArrowDown'); }],
  ['d/f+2', async () => { await page.keyboard.down('ArrowDown'); await page.keyboard.down(fwd); await page.waitForTimeout(400); await key('Digit2'); await page.keyboard.up(fwd); await page.keyboard.up('ArrowDown'); }],
  ['d/b+4', async () => { await page.keyboard.down('ArrowDown'); await page.keyboard.down(back); await page.waitForTimeout(400); await key('Digit4'); await page.keyboard.up(back); await page.keyboard.up('ArrowDown'); }],
  ['u/f+4', async () => { await page.keyboard.down('ArrowUp'); await page.keyboard.down(fwd); await page.waitForTimeout(400); await key('Digit4'); await page.keyboard.up(fwd); await page.keyboard.up('ArrowUp'); }],
  ['FC.3 (crouch+3)', async () => { await page.keyboard.down('ArrowDown'); await page.waitForTimeout(450); await key('Digit3'); await page.keyboard.up('ArrowDown'); }],
  ['FC.4 (crouch+4)', async () => { await page.keyboard.down('ArrowDown'); await page.waitForTimeout(450); await key('Digit4'); await page.keyboard.up('ArrowDown'); }],
  ['WS.4 (rise+4)', async () => { await page.keyboard.down('ArrowDown'); await page.waitForTimeout(450); await page.keyboard.up('ArrowDown'); await page.waitForTimeout(80); await key('Digit4'); }],
  ['WS.2 (rise+2)', async () => { await page.keyboard.down('ArrowDown'); await page.waitForTimeout(450); await page.keyboard.up('ArrowDown'); await page.waitForTimeout(80); await key('Digit2'); }],
  ['SS.2 (sidestep+2)', async () => { await key('ArrowUp', 60); await page.waitForTimeout(220); await key('Digit2'); }],
  ['SS.3 (sidestep+3)', async () => { await key('ArrowDown', 60); await page.waitForTimeout(220); await key('Digit3'); }],
  ['BT.1 (backturned+1)', async () => { await page.evaluate(() => { const f = window.__game.p1; f.stance = 'BT'; f.stanceT = 5; }); await key('Digit1'); }],
  ['BT.3 (backturned+3)', async () => { await page.evaluate(() => { const f = window.__game.p1; f.stance = 'BT'; f.stanceT = 5; }); await key('Digit3'); }],
  ['f,F+2 (dash)', async () => { await key(fwd, 120); await page.waitForTimeout(250); await page.keyboard.down(fwd); await page.waitForTimeout(250); await key('Digit2'); await page.keyboard.up(fwd); }],
  ['qcf+2', async () => { await page.keyboard.down('ArrowDown'); await page.waitForTimeout(150); await page.keyboard.down(fwd); await page.waitForTimeout(150); await page.keyboard.up('ArrowDown'); await page.waitForTimeout(150); await key('Digit2'); await page.keyboard.up(fwd); }],
  // strings: sample while the follow-up is firing
  ['1,2 string', async () => { await key('Digit1'); await page.waitForTimeout(150); await key('Digit2'); }, 'early'],
  ['1,2,2 string', async () => { await key('Digit1'); await page.waitForTimeout(150); await key('Digit2'); await page.waitForTimeout(150); await key('Digit2'); }, 'early'],
  ['2,1 string', async () => { await key('Digit2'); await page.waitForTimeout(150); await key('Digit1'); }, 'early'],
  ['f+2,1 string', async () => { await page.keyboard.down(fwd); await page.waitForTimeout(400); await key('Digit2'); await page.waitForTimeout(250); await key('Digit1'); await page.keyboard.up(fwd); }, 'early'],
];

const rows = [];
for (const [label, run, when] of cases) {
  await reset();
  await settle();
  await page.waitForTimeout(300);
  await run();
  await page.waitForTimeout(when === 'early' ? 120 : 150);
  const s1 = await state();
  await page.waitForTimeout(900);
  const s2 = await state();
  await render();
  await page.screenshot({ path: shot(label) });
  const r = { input: label, ...s1, p2hp_after: s2.p2hp, shot: path.basename(shot(label)) };
  rows.push(r);
  console.log(`${label.padEnd(20)} -> ${String(s1.notation).padEnd(12)} ${(s1.key || '').padEnd(20)} ${String(s1.name).slice(0, 30).padEnd(30)} anim=${s1.anim} p2hp 100->${s2.p2hp}`);
}

// Determinism: 1/2/3/4 three times each -> identical notation.
const det = {};
for (const d of ['Digit1', 'Digit2', 'Digit3', 'Digit4']) {
  const seen = [];
  for (let i = 0; i < 3; i++) {
    await reset(); await settle(); await page.waitForTimeout(300);
    await key(d); await page.waitForTimeout(150);
    const s = await state(); seen.push(`${s.notation}|${s.key}`);
  }
  det[d] = seen;
  const ok = new Set(seen).size === 1;
  console.log(`determinism ${d}: ${ok ? 'PASS' : 'FAIL'} ${JSON.stringify(seen)}`);
}
// Distinctness: 1/2/3/4 -> four distinct moves.
const distinct = new Set(Object.values(det).map(v => v[0])).size === 4;
console.log(`distinctness 1/2/3/4 -> 4 distinct moves: ${distinct ? 'PASS' : 'FAIL'}`);

fs.writeFileSync(path.join(out, 'results.json'), JSON.stringify({ p1, p2, fwd, rows, determinism: det, distinct4: distinct, logs }, null, 1));
fs.writeFileSync(path.join(out, 'console.log'), logs.join('\n'));
console.log(`console lines: ${logs.length}; errors: ${logs.filter(l => /error/i.test(l)).length}`);
await browser.close();
