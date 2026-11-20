// Contact proof (pt198u): like combat_inputs.mjs at a given viewport (VW/VH env), CPU frozen at touching spacing (1.45), logs every receiveHit. NOSHOT=1 skips renders.
// Combat input proof: real keyboard input -> which move each Tekken input fires.
//
// node tools/proof-harness/combat_inputs.mjs OUTDIR [p1] [p2]
// Starts an arcade fight, freezes the CPU (training-dummy style) so inputs are exact, then
// plays scripted Tekken inputs on the keyboard (game/js/input.js bindings: arrows = stick,
// Digit1-4 = 1/2/3/4) and logs per input: resolved notation, move key + name + source,
// decoded hit word, the defender's HP change, and a screenshot. Proves the 2026-10-21
// engine: slots/loadout resolution, crouch/WS./FC., strings, motions, guard and posture.
//
// Proof harness from the 2026-10-20/21 Claude session (tools/TOOLS-INDEX.md). Serve the repo
// first: python3 -m http.server ' + (process.env.PORT || 8771) + ' (from the repo root).
const { chromium } = await import(process.env.PLAYWRIGHT_MODULE || '/workspace/pw/node_modules/playwright/index.mjs');
import fs from 'fs';
const [,, out = 'combat', p1 = 'byou', p2 = 'docfrank'] = process.argv;
fs.mkdirSync(out, { recursive: true });
const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || '/home/box/.cache/ms-playwright/chromium-1248/chrome-linux64/chrome',
  args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: +process.env.VW, height: +process.env.VH } });
const logs = [];
page.on('console', m => { if (/error|warn|\[WH\]/i.test(m.text())) logs.push(`[${m.type()}] ${m.text()}`); });
page.on('pageerror', e => logs.push(`[pageerror] ${e.message}`));
console.log('loading page'); await page.goto('http://127.0.0.1:' + (process.env.PORT || 8771) + '/game/index.html', { waitUntil: 'load' });
await page.waitForFunction(() => window.__game, null, { timeout: 180000 });
await page.evaluate(() => { const b = document.createElement('button'); b.dataset.action = 'mode-arcade'; document.body.appendChild(b); b.click(); });
await page.waitForFunction(() => window.__modes, null, { timeout: 180000 }).catch(e => console.log('no __modes', logs.slice(-8).join(' | ')));
await page.evaluate(() => window.__modes.startMode('arcade'));
// Software GL in the cloud container cannot draw the stage at a usable rate (origin/main blocks the
// same way: 0 frames per 15 s). The game logic runs unchanged; the arena only renders for screenshots.
await page.evaluate(() => { const a = window.__game.arena; a.__render = a.render.bind(a); a.render = () => {}; });
console.log('starting fight'); await page.evaluate(async ([a, b]) => { await window.__modes.startFight(a, b, { mode: 'arcade' }); }, [p1, p2]);
console.log('fight started, waiting for round');
await page.waitForFunction(() => window.__game && window.__game.roundState === 'fight', null, { timeout: 120000 }).catch(() => console.log('round never reached fight state'));
console.log('round state:', await page.evaluate(() => window.__game && window.__game.roundState));
await page.waitForTimeout(1200);
// freeze the CPU: inputs below are the only thing moving
await page.evaluate(() => { const g = window.__game; g.ai.update = () => {}; g.timer = 999; g.p2.root.position.x = g.p1.root.position.x + (+(window.__SPACING || 1.45)) * g.p1.facing; });

await page.evaluate(() => { const g = window.__game; const o = g.p2.receiveHit.bind(g.p2); window.__rh = []; g.p2.receiveHit = (m, a) => { const r = o(m, a); window.__rh.push({ n: a && a.attackName, r, w: m.hitWord, st: g.p2.state, stick: g.p2._stickDir }); return r; }; });
const key = async (k, ms = 40) => { await page.keyboard.down(k); await page.waitForTimeout(ms); await page.keyboard.up(k); };
const state = () => page.evaluate(() => {
  const g = window.__game, f = g.p1, a = f.attack;
  return { state: f.state, notation: f.attackName, key: a && a.moveKey, name: a && a.moveName, word: a && a.hitWord,
           anim: a && (a.t3row != null ? `row ${a.t3row}` : a.animRow != null ? `anim_t3 ${a.animBank}:${a.animRow}` : null),
           stance: f.stance, p2hp: +g.p2.hp.toFixed(1), p1hp: +g.p1.hp.toFixed(1), bank: f._t3 && f._t3.bank, su: a && a.startup, ac: a && a.active, rc: a && a.recovery, dmg: a && a.damage, lvl: a && a.hitLevel, dist: +(g.p2.root.position.x - f.root.position.x).toFixed(2), dz: +(g.p2.root.position.z - f.root.position.z).toFixed(2), p2s: g.p2.state };
});
const reset = () => page.evaluate(() => { const g = window.__game; g.p1.hp = 100; g.p2.hp = 100; g.p1._enter('idle'); g.p2._enter('idle'); g.p2.stun = 0; g.p2.vx = 0; g.p2.vz = 0; g.p1.vx = 0; g.p2.root.position.z = g.p1.root.position.z;
  g.p2.root.position.x = g.p1.root.position.x + (+(window.__SPACING || 1.45)) * g.p1.facing; g.p1.tekken.lastMove = null; });

const fwd = await page.evaluate(() => window.__game.p1.facing > 0 ? 'ArrowRight' : 'ArrowLeft');
const back = fwd === 'ArrowRight' ? 'ArrowLeft' : 'ArrowRight';
const cases = [
  ['1', async () => key('Digit1')],
  ['1,2 (string)', async () => { await key('Digit1'); await page.waitForTimeout(120); await key('Digit2'); }],
  ['d/f+1', async () => { await page.keyboard.down('ArrowDown'); await page.keyboard.down(fwd); await page.waitForTimeout(30); await key('Digit1'); await page.keyboard.up(fwd); await page.keyboard.up('ArrowDown'); }],
  ['f,F+2 (dash)', async () => { await key(fwd, 40); await page.waitForTimeout(40); await page.keyboard.down(fwd); await page.waitForTimeout(30); await key('Digit2'); await page.keyboard.up(fwd); }],
  ['crouch then 3 (FC)', async () => { await page.keyboard.down('ArrowDown'); await page.waitForTimeout(400); await key('Digit3'); await page.keyboard.up('ArrowDown'); }],
  ['WS.4 (rise + 4)', async () => { await page.keyboard.down('ArrowDown'); await page.waitForTimeout(400); await page.keyboard.up('ArrowDown'); await page.waitForTimeout(60); await key('Digit4'); }],
  ['1+3 (throw)', async () => { await page.keyboard.down('Digit1'); await page.keyboard.down('Digit3'); await page.waitForTimeout(40); await page.keyboard.up('Digit1'); await page.keyboard.up('Digit3'); }],
  ['b+1+2', async () => { await page.keyboard.down(back); await page.waitForTimeout(30); await page.keyboard.down('Digit1'); await page.keyboard.down('Digit2'); await page.waitForTimeout(40); await page.keyboard.up('Digit1'); await page.keyboard.up('Digit2'); await page.keyboard.up(back); }],
];
const rows = [];
for (const [label, run] of cases) {
  await reset();
  await page.waitForTimeout(250);
  await run();
  await page.waitForTimeout(90);
  const s1 = await state();
  await page.waitForTimeout(+(process.env.SETTLE_MS || 1400));
  const s2 = await state();
  const r = await page.evaluate(() => window.__game.renderer ? 1 : 0).catch(() => 0);
  const shot = `${out}/${label.replace(/[^a-z0-9]+/gi, '_')}.png`;
  if (!process.env.NOSHOT) { await page.evaluate(() => window.__game.arena.__render()); await page.screenshot({ path: shot }); }
  console.log('RH', JSON.stringify(await page.evaluate(() => { const r = window.__rh; window.__rh = []; return r; })));
  rows.push({ input: label, ...s1, p2hp_after: s2.p2hp, shot });
  console.log(JSON.stringify({su:s1.su,ac:s1.ac,rc:s1.rc,dmg:s1.dmg,lvl:s1.lvl,dist:s1.dist,dz:s1.dz,p2s:s1.p2s,p2s2:s2.p2s})); console.log(`${label.padEnd(20)} -> ${String(s1.notation).padEnd(12)} ${String(s1.key).padEnd(18)} ${String(s1.name).slice(0, 28).padEnd(28)} word=${s1.word ? '0x' + s1.word.toString(16) : '-'} anim=${s1.anim} state=${s1.state} p2hp 100->${s2.p2hp}`);
}
// guard + posture checks driven directly through the fighters (decoded T3 rules)
const rules = await page.evaluate(() => {
  const g = window.__game, d = g.p1, a = g.p2;
  const mk = (w) => ({ damage: 10, knock: 2.2, hitWord: w });
  const out = {};
  d.isPlayer = true;
  d._enter('crouch'); out.high_vs_crouch_connects = d.canBeHitBy(mk(0x412));
  d._enter('idle'); out.high_vs_stand_connects = d.canBeHitBy(mk(0x412));
  d.setStick('n'); out.mid_vs_neutral_human = d.receiveHit(mk(0x217), a); d.hp = 100; d._enter('idle'); d.stun = 0;
  d.setStick('n'); out.low_vs_neutral_human = d.receiveHit(mk(0x10F), a); d.hp = 100; d._enter('crouch'); d.stun = 0;
  d.setStick('d/b'); out.low_vs_downback = d.receiveHit(mk(0x10F), a); d.hp = 100; d._enter('crouch'); d.stun = 0;
  d.setStick('d/b'); out.mid_vs_downback = d.receiveHit(mk(0x217), a); d.hp = 100; d._enter('idle'); d.stun = 0;
  d.setStick('f'); out.mid_vs_walking_fwd = d.receiveHit(mk(0x217), a); d.hp = 100; d._enter('idle'); d.stun = 0;
  return out;
});
console.log('T3 guard/posture rules:', JSON.stringify(rules));
fs.writeFileSync(`${out}/results.json`, JSON.stringify({ p1, p2, rows, rules, logs }, null, 1));
fs.writeFileSync(`${out}/console.log`, logs.join('\n'));
console.log(`console lines: ${logs.length}; errors: ${logs.filter(l => /error/i.test(l)).length}`);
await browser.close();
