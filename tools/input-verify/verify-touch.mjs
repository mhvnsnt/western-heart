// TOUCH-BUTTON INPUT-TO-MOVE FIDELITY PROOF (moveset lane, worker 11).
// Real TOUCH taps on the PSX face buttons -> which move each fires, on the live game.
// node tools/input-verify/verify-touch.mjs OUTDIR [p1] [p2]
// Requires: python3 -m http.server 8765 (from the repo root) + a CDP chrome on :9333.
// Connects over CDP (playwright-core connectOverCDP) because managed launch crashes here.
//
// Proves the owner's acceptance criteria (2026-10-22, verbatim):
//   "Pressing buttons does random moves or nothing -> every button must do its
//    CORRECT Tekken move, every time"
//   "Combos don't work, just one random move at a time -> real working combo strings"
//   "Some buttons don't work at all -> every button functional"
// PSX map: Square=1 (left punch), Triangle=2 (right punch),
//          X=3 (left kick), Circle=4 (right kick).
import { chromium } from 'playwright-core';
import fs from 'fs';
import path from 'path';

const [,, out = 'touch-proof', p1 = 'torch', p2 = 'pantera'] = process.argv;
fs.mkdirSync(out, { recursive: true });
const shot = (n) => path.join(out, n.replace(/[^a-z0-9]+/gi, '_') + '.png');

const browser = await chromium.connectOverCDP('http://127.0.0.1:9333');
const ctx = await browser.newContext({
  hasTouch: true, isMobile: true,
  viewport: { width: 844, height: 390 }, // landscape phone
  userAgent: 'Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0 Mobile Safari/537.36',
});
const page = await ctx.newPage();
const logs = [];
page.on('console', m => { if (/error|warn|\[WH\]/i.test(m.text())) logs.push(`[${m.type()}] ${m.text()}`); });
page.on('pageerror', e => logs.push(`[pageerror] ${e.message}`));

console.log('loading page');
await page.goto('http://localhost:8765/game/index.html', { waitUntil: 'load' });
await page.waitForTimeout(2000);

const vis = await page.evaluate(() => {
  const tc = document.getElementById('touch-controls');
  const cs = tc ? getComputedStyle(tc) : null;
  const btns = [...document.querySelectorAll('.act-btn')].map(b => ({
    btn: b.dataset.btn, label: b.textContent.trim(),
    rect: (() => { const r = b.getBoundingClientRect(); return { x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height) }; })(),
  }));
  return { touchControlsDisplay: cs && cs.display, buttons: btns };
});
console.log('touch-controls display:', vis.touchControlsDisplay);
console.log('buttons:', JSON.stringify(vis.buttons));

// Overlap check: no two button rects may intersect.
const rects = vis.buttons.map(b => b.rect);
let overlap = false;
for (let i = 0; i < rects.length; i++) for (let j = i + 1; j < rects.length; j++) {
  const a = rects[i], b = rects[j];
  if (a.x < b.x + b.w && b.x < a.x + a.w && a.y < b.y + b.h && b.y < a.y + a.h) {
    overlap = true;
    console.log(`!! OVERLAP: ${vis.buttons[i].btn} (${vis.buttons[i].label}) x ${vis.buttons[j].btn} (${vis.buttons[j].label})`);
  }
}
console.log('overlap check:', overlap ? 'FAIL' : 'PASS (no overlaps)');

// NOTE: bypass the select screen (menu lane's T8 transplant crashes arcade startMode);
// start the fight directly via __modes.startFight. Input verification only.
console.log('starting fight', p1, 'vs', p2);
await page.evaluate(() => { const a = window.__game.arena; a.__render = a.render.bind(a); a.render = () => {}; });
await page.evaluate(async ([a, b]) => { await window.__modes.startFight(a, b, { mode: 'arcade' }); }, [p1, p2]);
await page.waitForFunction(() => window.__game && window.__game.roundState === 'fight', null, { timeout: 120000 })
  .catch(() => console.log('!! round never reached fight state'));
console.log('round state:', await page.evaluate(() => window.__game && window.__game.roundState));
await page.waitForTimeout(1200);
await page.evaluate(() => {
  const g = window.__game;
  g.ai.update = () => {}; g.timer = 999;
  g.p2.root.position.x = g.p1.root.position.x + 1.15 * g.p1.facing;
});

const tapBtn = (dataBtn) => page.evaluate((db) => {
  const el = document.querySelector(`.act-btn[data-btn="${db}"]`);
  if (!el) return 'missing';
  const r = el.getBoundingClientRect();
  const cx = r.x + r.width / 2, cy = r.y + r.height / 2;
  const t = new Touch({ identifier: Date.now() % 100000, target: el, clientX: cx, clientY: cy });
  el.dispatchEvent(new TouchEvent('touchstart', { touches: [t], targetTouches: [t], changedTouches: [t], bubbles: true, cancelable: true }));
  el.dispatchEvent(new TouchEvent('touchend', { touches: [], targetTouches: [], changedTouches: [t], bubbles: true, cancelable: true }));
  return 'tapped';
}, dataBtn);
const state = () => page.evaluate(() => {
  const g = window.__game, f = g.p1, a = f.attack;
  return {
    state: f.state, notation: f.attackName, key: a && a.moveKey, name: a && a.moveName,
    word: a && a.hitWord, anim: a && (a.t3row != null ? `t3row ${a.t3row}` : a.animRow != null ? `anim ${a.animBank}:${a.animRow}` : null),
    p2hp: +g.p2.hp.toFixed(1),
  };
});
const reset = () => page.evaluate(() => {
  const g = window.__game;
  g.input.consume();
  g.p1.hp = 100; g.p2.hp = 100; g.p1._enter('idle'); g.p2._enter('idle');
  g.p2.stun = 0; g.p1.stun = 0;
  const t = g.p1.tekken;
  t.lastMove = null; t.lastMoveT = 0; t.lastDir = 'n';
  t.hist.fill('n'); t.dirEvents.length = 0; t._dash = null;
  g.p1._queuedNext = null; g.p1.stance = null; g.p2.stance = null;
  g.p2.root.position.x = g.p1.root.position.x + 1.15 * g.p1.facing;
  g.input.consume();
});
const settle = () => page.waitForFunction(() => {
  const g = window.__game;
  return g.p1.state === 'idle' && g.p1.stun <= 0;
}, null, { timeout: 15000 }).catch(() => console.log('!! settle timed out'));
const render = () => page.evaluate(() => window.__game.arena.__render());

// Button-by-button demo: each PSX face button -> its CORRECT Tekken move.
const cases = [
  ['tap SQUARE (1)', async () => tapBtn('1')],
  ['tap TRIANGLE (2)', async () => tapBtn('2')],
  ['tap X (3)', async () => tapBtn('3')],
  ['tap CIRCLE (4)', async () => tapBtn('4')],
  ['combo 1,2', async () => { await tapBtn('1'); await page.waitForTimeout(150); await tapBtn('2'); }, 'early'],
  ['combo 1,2,2', async () => { await tapBtn('1'); await page.waitForTimeout(150); await tapBtn('2'); await page.waitForTimeout(150); await tapBtn('2'); }, 'early'],
];

const rows = [];
for (const [label, run, when] of cases) {
  await reset(); await settle(); await page.waitForTimeout(300);
  const tr = await run();
  if (tr === 'missing') console.log(`!! ${label}: button element missing from DOM`);
  await page.waitForTimeout(when === 'early' ? 120 : 150);
  const s1 = await state();
  await page.waitForTimeout(900);
  const s2 = await state();
  await render();
  await page.screenshot({ path: shot(label) });
  rows.push({ input: label, ...s1, p2hp_after: s2.p2hp, shot: path.basename(shot(label)) });
  const fired = s1.state === 'attack' || s1.notation ? 'FIRED' : 'NOTHING';
  console.log(`${label.padEnd(18)} -> [${fired}] ${String(s1.notation).padEnd(12)} ${(s1.key || '').padEnd(20)} ${String(s1.name).slice(0, 28)} p2hp 100->${s2.p2hp}`);
}

// Determinism: each button 3x -> identical notation every time (fidelity law).
const det = {};
for (const db of ['1', '2', '3', '4']) {
  const seen = [];
  for (let i = 0; i < 3; i++) {
    await reset(); await settle(); await page.waitForTimeout(300);
    await tapBtn(db); await page.waitForTimeout(150);
    const s = await state(); seen.push(`${s.notation}|${s.key}`);
  }
  det[db] = seen;
  console.log(`determinism btn ${db}: ${new Set(seen).size === 1 ? 'PASS' : 'FAIL'} ${JSON.stringify(seen)}`);
}
const distinct = new Set(Object.values(det).map(v => v[0])).size === 4;
console.log(`distinctness 1/2/3/4 -> 4 distinct moves: ${distinct ? 'PASS' : 'FAIL'}`);

// Layout proof: portrait + landscape screenshots of the PSX button layout.
await render();
await page.screenshot({ path: shot('layout_landscape') });
await page.setViewportSize({ width: 390, height: 844 }); // portrait phone
await page.waitForTimeout(600);
await render();
await page.screenshot({ path: shot('layout_portrait') });
const portRects = await page.evaluate(() => [...document.querySelectorAll('.act-btn')].map(b => {
  const r = b.getBoundingClientRect(); return { btn: b.dataset.btn, x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height) };
}));
let portOverlap = false;
for (let i = 0; i < portRects.length; i++) for (let j = i + 1; j < portRects.length; j++) {
  const a = portRects[i], b = portRects[j];
  if (a.x < b.x + b.w && b.x < a.x + a.w && a.y < b.y + b.h && b.y < a.y + a.h) { portOverlap = true; console.log(`!! PORTRAIT OVERLAP: ${a.btn} x ${b.btn}`); }
}
console.log('portrait overlap check:', portOverlap ? 'FAIL' : 'PASS (no overlaps)');

fs.writeFileSync(path.join(out, 'results.json'), JSON.stringify({
  p1, p2, overlapCheckLandscape: !overlap, overlapCheckPortrait: !portOverlap,
  touchControlsDisplay: vis.touchControlsDisplay, buttons: vis.buttons, portraitRects: portRects,
  rows, determinism: det, distinct4: distinct, logs,
}, null, 1));
fs.writeFileSync(path.join(out, 'console.log'), logs.join('\n'));
console.log(`console lines: ${logs.length}; errors: ${logs.filter(l => /error/i.test(l)).length}`);
await ctx.close();
console.log('TOUCH PROOF DONE ->', out);
