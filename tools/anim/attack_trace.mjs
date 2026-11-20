// In-game attack trace (lane D, 2026-10-24): does the move's clip extend its striking limb ON the
// move's active frames, in the real game loop?
//
// node tools/anim/attack_trace.mjs OUTDIR P1 P2 'd/f+1,d/b+4,...'   (repo served on :8765, as fight.mjs)
// Starts an arcade fight, switches the CPU off, puts P2 in reach of P1 and has P2 perform each listed
// notation (Fighter._fireNotation, the resolved-notation entry the string buffer uses). After every
// fixed step it records P2's stateT / phase / clip / clip time and the distance of the move's
// striking joint (wrist or ankle, the joint the hitbox uses) from the pelvis. Writes trace.json and
// prints, per move, the step where that distance peaks vs the move's startup, plus whether P1 got hit.
const { chromium } = await import(process.env.PLAYWRIGHT_MODULE || '/opt/node22/lib/node_modules/playwright/index.mjs');
import fs from 'fs';
const [,, out = 'trace', p1 = 'pantera', p2 = 'skull', list = 'd/f+1'] = process.argv;
fs.mkdirSync(out, { recursive: true });
const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
  args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: 960, height: 540 } });
const logs = [];
page.on('console', m => logs.push(`[${m.type()}] ${m.text()}`));
page.on('pageerror', e => logs.push(`[pageerror] ${e.message}`));
page.on('response', r => { if (r.status() >= 400) logs.push(`[http ${r.status()}] ${r.url()}`); });
await page.goto(`http://127.0.0.1:${process.env.PORT || 8765}/game/index.html`, { waitUntil: 'load' });
await page.waitForFunction(() => window.__modes, null, { timeout: 60000 });
await page.evaluate(() => window.__modes.startMode('arcade'));
await page.evaluate(([a, b]) => window.__modes.startFight(a, b, { mode: 'arcade' }), [p1, p2]).catch(e => logs.push('startFight err ' + e.message));
await page.waitForFunction(() => window.__game && window.__game.p2 && window.__game.round === 'fight' || (window.__game && window.__game.state === 'fight'), null, { timeout: 60000 }).catch(() => {});
await page.waitForTimeout(1500);
const res = await page.evaluate(async (notations) => {
  // Headless SwiftShader renders ~1 frame/s and the loop caps a frame at 0.05 s of sim, so the
  // rAF loop is paused and the game's own fixed step (Game._update, 1/120 s: input, AI, fighters,
  // hit detection) is driven directly. Rendering is not needed: the mixer poses the bones.
  const g = window.__game, A = g.p1, B = g.p2;
  if (g.ai) g.ai.update = () => {};
  if (g.ai1) g.ai1.update = () => {};
  g.running = false;
  const DT = 1 / 120;
  const rec = [];
  const bone = { armL: 'LeftHand', armR: 'RightHand', legL: 'LeftFoot', legR: 'RightFoot' };
  const sample = (n) => {
    const p = B._atkPlan, a = B._t3current;
    const limb = (p && p.id === B._attackId && p.limb) || 'armR';
    const e = B.bones[bone[limb]], h = B.bones.Hips;
    let d = null;
    if (e && h) d = e.getWorldPosition(e.position.clone()).distanceTo(h.getWorldPosition(h.position.clone()));
    rec.push({ n, st: B.state, t: +B.stateT.toFixed(4), ph: B._attackPhase, clip: a ? a.getClip().name : null,
      ct: a ? +a.time.toFixed(4) : null, d: d == null ? null : +d.toFixed(4), limb, p1hp: +A.hp.toFixed(2), hb: !!B.getHitbox() });
  };
  const summary = [];
  for (const n of notations) {
    A.root.position.x = -0.6; B.root.position.x = 0.6; A.facing = 1; B.facing = -1;
    A._enter('idle'); B._enter('idle'); A.hp = A.maxHp; B.hp = B.maxHp; A.stun = 0; B.stun = 0; A.invuln = 0; B.invuln = 0;
    for (let i = 0; i < 60; i++) g._update(DT); // settle into the stance
    A.root.position.x = -0.6; B.root.position.x = 0.6;
    const hp0 = A.hp;
    const ok = B._fireNotation(n);
    const mv = B.attack;
    const total = mv ? (mv.startup || 0) + (mv.active || 0) + (mv.recovery || 0) : 1;
    const start = rec.length;
    for (let i = 0; i < Math.ceil((total + 0.1) / DT) && i < 600; i++) {
      g._update(DT);
      sample(n);
      if (B.state !== 'attack' && rec.length - start > 2) break;
    }
    const rows = rec.slice(start).filter(r => r.st === 'attack' || r.st === 'vskill');
    let peak = null;
    for (const r of rows) if (r.d != null && (!peak || r.d > peak.d)) peak = r;
    const p = B._atkPlan || {};
    summary.push({ n, fired: ok, move: mv && (mv.moveName || mv.moveKey), startup: mv && mv.startup, active: mv && mv.active, recovery: mv && mv.recovery,
      clip: p.name, kind: p.kind, limb: p.limb, timing: p.timing, steps: rows.length, peakT: peak && peak.t, peakPhase: peak && peak.ph,
      peakErrFrames: peak && mv ? +((peak.t - mv.startup) * 60).toFixed(1) : null, p1Damage: +(hp0 - A.hp).toFixed(2) });
  }
  g.running = true;
  return { summary, rec };
}, list.split(',').map(s => s.trim()).filter(Boolean));
fs.writeFileSync(`${out}/trace.json`, JSON.stringify(res, null, 1));
fs.writeFileSync(`${out}/console.log`, logs.join('\n'));
const shot = await page.screenshot();
fs.writeFileSync(`${out}/end.png`, shot);
for (const s of res.summary) console.log(JSON.stringify(s));
console.log('pageerrors:', logs.filter(l => l.startsWith('[pageerror]')).length, ' http>=400:', logs.filter(l => l.startsWith('[http')).join(' | '));
await browser.close();
