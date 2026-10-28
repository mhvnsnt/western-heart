// Combat input e2e (Grok, 2026-10-28). Serve the repo root on $WH_URL (default
// http://127.0.0.1:8811). Run: node test/e2e/combat-inputs.e2e.mjs [shotsDir] [fighter ...]
// The RAF sim is stopped and Game._update is stepped at 60 Hz by hand, and the
// InputManager's press clock follows the sim. That keeps the chord window and string
// timings exact on software GL, where a real frame takes hundreds of ms.
// Checks, per fighter: every single/chord button fires that exact move; every listed
// string, pressed one hit at a time 150 ms apart, fires each hit in order (hits chain);
// each listed directional special fires from its input; 1+3 / 2+4 grab connects, and both
// thrower and victim reach the exec states with a clip playing; no page errors.
import { chromium } from 'playwright';
import fs from 'node:fs';
const BASE = process.env.WH_URL || 'http://127.0.0.1:8811';
const SHOTS = process.argv[2] || 'combat-inputs-shots';
const FIGHTERS = process.argv.slice(3).length ? process.argv.slice(3) : ['bruno', 'zen'];
const OPP = process.env.WH_OPP || 'kronos';
fs.mkdirSync(SHOTS, { recursive: true });
const fails = []; let passes = 0;
const ok = (c, m) => { if (c) passes++; else { fails.push(m); console.log('FAIL', m); } };
const b = await chromium.launch({ executablePath: process.env.CHROME || undefined,
  args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });

async function fight(P1) {
  const p = await b.newPage({ viewport: { width: 960, height: 540 } });
  p.errs = []; p.on('pageerror', (e) => p.errs.push(String(e).slice(0, 300)));
  p.throwLog = new Set(); p.on('console', (m) => { const t = m.text(); if (t.startsWith('[WH-THROW]')) p.throwLog.add(t.slice(0, 200)); });
  await p.goto(BASE + '/game/index.html');
  await p.waitForFunction(() => window.__startFight, null, { timeout: 90000 });
  await p.evaluate(([a, c]) => window.__startFight(a, c, {}), [P1, OPP]);
  await p.waitForFunction(() => { const g = window.__game; return g && g.roundState === 'fight' && g.p1 && g.p2; }, null, { timeout: 300000, polling: 500 });
  await p.evaluate(() => {
    const g = window.__game; g.running = false; g.ai.update = () => {}; g.timer = 9999; g._hitStop = 0;
    window.__vt = 1e6; g.input._pressT = () => window.__vt; // press clock = sim clock
    const KEY = { 1: 'Digit1', 2: 'Digit2', 3: 'Digit3', 4: 'Digit4', f: 'KeyD', b: 'KeyA', u: 'KeyW', d: 'KeyS' };
    window.__key = (codes, type = 'keydown') => { for (const c of [].concat(codes)) window.dispatchEvent(new KeyboardEvent(type, { code: KEY[c] || c, key: c, bubbles: true })); };
    const s = (f) => ({ st: f.state, an: f.attackName, clip: f._t3current ? f._t3current.getClip().name : null, x: +f.root.position.x.toFixed(2), y: +f.root.position.y.toFixed(2) });
    window.__step = (n) => { const out = []; for (let i = 0; i < n; i++) { window.__vt += 1000 / 60;
      if (g._hitStop > 0) g._hitStop -= 1 / 60; else g._update(1 / 60); out.push({ p1: s(g.p1), p2: s(g.p2) }); } return out; };
    window.__reset = (gap) => {
      for (const f of [g.p1, g.p2]) { f.hp = f.maxHp || f.hp; f._enter('idle'); f.attack = null; f.attackName = null; f._throwPair = null;
        f.lockT = 0; f.lockMove = null; f.tekken.lastMove = null; f.tekken._strPath = null; f._stringGraceUntil = 0; f._queuedNext = null; f._queuedAfter = []; f._urgeOn = false; f._urgeT = 0; // Soul Urge built up over the sweep turns 1+2 into Urge Dash
        f.vx = 0; f.stun = 0; f.invuln = 0; f._pressBuf && f._pressBuf.clear(); }
      g.p1.root.position.set(-gap / 2, 0, 0); g.p2.root.position.set(gap / 2, 0, 0);
      g.roundState = 'fight'; g.timer = 9999; // a KO earlier in the sweep must not end the round
      g.input._queue.length = 0; g.p1.facing = 1; window.__step(30); window.__vt += 1000; };
  });
  return p;
}
const seq = (frames) => { const o = []; let last = null; for (const f of frames) { const s = f.p1; if (s.st === 'attack' && s.an) { if (s.an !== last) o.push(s.an); last = s.an; } else last = null; } return o; };
// Press one hit: '1', '1+3', 'f+2', 'd/f+1'. Directions are held 15 frames (past the 200 ms
// tap-vs-hold timer), the buttons pressed, then all released.
const press = (p, hit, gap = 1.2, reset = true, after = 9) => p.evaluate(([hit, gap, reset, after]) => {
  if (reset) window.__reset(gap);
  const m = /^(?:([udfbn/]+)\+)?([1234](?:\+[1234])*)$/.exec(hit); if (!m) return null;
  const dirs = m[1] ? m[1].split('/').filter((d) => d !== 'n') : []; const btns = m[2].split('+');
  let fr = [];
  if (dirs.length) { window.__key(dirs); fr = fr.concat(window.__step(15)); }
  window.__key(btns); fr = fr.concat(window.__step(1)); window.__key(btns, 'keyup'); window.__key(dirs, 'keyup');
  return fr.concat(window.__step(after));
}, [hit, gap, reset, after]);

for (const id of FIGHTERS) {
  const ms = JSON.parse(fs.readFileSync(new URL(`../../game/assets/movesets/${id}.json`, import.meta.url), 'utf8'));
  const p = await fight(id);
  const got = await p.evaluate(() => window.__game.p1.char.id);
  console.log(`== ${id} (loaded ${got}) vs ${OPP}`);
  for (const n of ['1', '2', '3', '4', '1+2', '3+4']) {
    const fr = await press(p, n, 1.6, true, 60);
    const s = seq(fr);
    ok(s[0] === n, `${id} ${n}: fired ${JSON.stringify(s)}`);
  }
  for (const str of (ms.strings || [])) {
    if (/^[A-Z]+\./.test(str.input)) { console.log(`  skip ${id} string ${str.input}: stance-entry string (resolver test covers it)`); continue; }
    const hits = str.hits || str.input.split(/[,~]/);
    let fr = [], bad = hits.find((h) => !/^(?:[udfbn/]+\+)?[1234](?:\+[1234])*$/.test(h)) || null; // check before pressing anything
    for (let i = 0; i < hits.length && !bad; i++) {
      const r = await press(p, hits[i], 1.6, i === 0, i === hits.length - 1 ? 60 * hits.length : 9);
      if (!r) bad = hits[i]; else fr = fr.concat(r);
    }
    if (bad) { console.log(`  skip ${id} string ${str.input}: hit '${bad}' is not a button press (resolver test covers it)`); continue; }
    const s = seq(fr);
    // Expected prefixes keep the list's own separators (',' or '~'): '2,2~1+2' -> 2, 2,2, 2,2~1+2.
    const cuts = []; { let pos = 0; for (const h of hits) { pos = str.input.indexOf(h, pos) + h.length; cuts.push(str.input.slice(0, pos)); } }
    const want = cuts;
    ok(JSON.stringify(s) === JSON.stringify(want), `${id} string ${str.input}: fired ${JSON.stringify(s)} want ${JSON.stringify(want)}`);
  }
  for (const sp of (ms.specials || [])) {
    if (sp.throw || !/^([udfbn/]+\+)?[1234](\+[1234])*$/.test(sp.input)) continue; // motion/throw specials: resolver tests
    const s = seq(await press(p, sp.input, 1.6, true, 60));
    ok(s[0] === sp.input, `${id} special ${sp.input}: fired ${JSON.stringify(s)}`);
  }
  for (const g of ['1+3', '2+4']) {
    const fr = await press(p, g, 1.0, true, 260);
    const p1 = new Set(fr.map((f) => f.p1.st)), p2 = new Set(fr.map((f) => f.p2.st));
    ok(p1.has('throwing') && p1.has('throwExec'), `${id} grab ${g}: thrower states ${[...p1]}`);
    ok(p2.has('thrown') && p2.has('thrownExec'), `${id} grab ${g}: victim states ${[...p2]}`);
    const vc = [...new Set(fr.filter((f) => /thrown/.test(f.p2.st)).map((f) => f.p2.clip))];
    const tc = [...new Set(fr.filter((f) => /throw(ing|Exec)/.test(f.p1.st)).map((f) => f.p1.clip))];
    ok(vc.some(Boolean), `${id} grab ${g}: victim clip ${vc}`);
    // Paired with the attacker, no fling: every thrownExec frame has a victim clip playing,
    // and the victim stays within arm's reach of the thrower (a launch-across-the-room has no anim).
    const ex = fr.filter((f) => f.p2.st === 'thrownExec');
    ok(ex.length && ex.every((f) => f.p2.clip), `${id} grab ${g}: thrownExec frames without a victim clip`);
    const far = Math.max(0, ...ex.map((f) => Math.abs(f.p2.x - f.p1.x)));
    ok(far < 2.2, `${id} grab ${g}: victim flung ${far} m from thrower during thrownExec`);
    console.log(`  grab ${g}: thrownExec ${ex.length} frames, max victim distance ${far} m`);
    console.log(`  grab ${g}: thrower clips ${JSON.stringify(tc)} victim clips ${JSON.stringify(vc)}`);
    if (g === '1+3') { // frame sheet: four moments of the throw (camera stepped with the sim)
      await p.evaluate(() => window.__reset(1.0));
      for (const [i, n] of [[0, 0], [1, 4], [2, 20], [3, 30], [4, 40]]) {
        await p.evaluate((n) => { const g = window.__game; if (n === 4) { window.__key(['1', '3']); window.__step(1); window.__key(['1', '3'], 'keyup'); } window.__step(n); for (let k = 0; k < 30; k++) g.arena.update(1 / 60, g.p1, g.p2, 0); g.arena.render(); }, n);
        await p.screenshot({ path: `${SHOTS}/${id}-grab-${i}.png` });
      }
    }
  }
  { // stick-stuck-down: hold the touch stick down past the 200 ms tap/hold timer (real
    // time: input.js times the hold with performance.now/setTimeout), release, back to neutral.
    await p.evaluate(() => { window.__reset(1.6); window.__game.input._stick8(0, -1); });
    // wait for the hold timer itself: on software GL a 200 ms setTimeout can land seconds late
    await p.waitForFunction(() => window.__game.input.down, null, { timeout: 20000 }).catch(() => {});
    const held = await p.evaluate(() => { const g = window.__game; window.__step(20); return { down: g.input.vertNow(), latched: g.input.down, ground: g.p1.onGround, st: g.p1.state }; });
    const rel = await p.evaluate(() => { const g = window.__game, inp = g.input; inp.stickNeutral(); window.__step(30);
      return { down: inp.vertNow(), dir: inp.stickDir, axisX: inp.axisX, st: g.p1.state }; });
    ok(held.down === 'down' && /crouch/i.test(held.st), `${id} stick: held down did not crouch ${JSON.stringify(held)}`);
    ok(!rel.down && (rel.dir === 'n' || rel.dir == null) && rel.axisX === 0 && !/crouch|sidestep/i.test(rel.st), `${id} stick stuck after release ${JSON.stringify(rel)}`);
    console.log(`  stick: held ${JSON.stringify(held)} released ${JSON.stringify(rel)}`);
  }
  if (p.throwLog.size) console.log('  ' + [...p.throwLog].join('\n  '));
  ok(p.errs.length === 0, `${id}: page errors ${JSON.stringify(p.errs.slice(0, 3))}`);
  await p.close();
}
await b.close();
console.log(`${passes} passed, ${fails.length} failed`);
process.exit(fails.length ? 1 : 0);
