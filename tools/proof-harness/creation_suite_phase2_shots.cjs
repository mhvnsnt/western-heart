// Creation Suite phase-2 proof harness (POSE & PICTURE).
// Pattern: tools/proof-harness/creation_suite_phase1_shots.cjs.
// Drives the suite to a roster fighter (Pantera), opens the POSE tab, plays
// his own stance clip, takes the picture, and asserts the picture landed in
// on-device storage under the user-portraits key (wh.portrait.<id>.<attire>)
// — the same key the select screen reads. Screenshots in landscape AND
// portrait. Usage: node creation_suite_phase2_shots.cjs <suite-url> <out-dir>
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const out = process.argv[3];
  fs.mkdirSync(out, { recursive: true });
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const ctx = await b.newContext({ viewport: { width: 844, height: 390 }, hasTouch: true, isMobile: true });
  const p = await ctx.newPage();
  const errs = [];
  p.on('pageerror', (e) => errs.push('pageerror ' + e.message.slice(0, 200)));
  p.on('console', (m) => { if (m.type() === 'error') errs.push('console ' + m.text().slice(0, 200)); });
  await p.route(/workers\.dev/, (r) => r.abort());
  await p.goto(process.argv[2], { waitUntil: 'load', timeout: 120000 });
  await p.waitForFunction(() => document.querySelector('#loader.done') && window.__suite && window.__suite.viewer && window.__suite.viewer.ready, null, { timeout: 180000, polling: 500 });
  // First visit opens the base-body template picker; dismiss it the way a
  // player would (CANCEL) so the proof frames show the suite itself.
  const modalOpen = await p.evaluate(() => !document.querySelector('#modal').hidden);
  if (modalOpen) {
    await p.locator('#modal .btn', { hasText: 'CANCEL' }).first().click();
    await p.waitForFunction(() => document.querySelector('#modal').hidden, null, { timeout: 30000 });
  }
  // roster mode: Pantera (his own bank drives the poses)
  await p.evaluate(() => window.__suite.selectRosterAttire('pantera', 'classic'));
  await p.waitForFunction(() => window.__suite.viewer.currentUrl && /pantera/.test(window.__suite.viewer.currentUrl), null, { timeout: 120000, polling: 500 });
  await p.waitForTimeout(2000);
  // POSE tab
  await p.evaluate(() => window.__suite.setTab('pose'));
  await p.waitForFunction(() => document.querySelector('[data-pose="stance"]'), null, { timeout: 60000, polling: 500 });
  await p.waitForTimeout(500);
  await p.screenshot({ path: out + '/1_pose_tab_landscape.png' });
  // play his stance (the bank clip retargeted onto this body by the game's
  // own pipeline); sample the hips twice — a playing pose moves.
  await p.evaluate(() => document.querySelector('[data-pose="stance"]').click());
  await p.waitForTimeout(1500);
  const q1 = await p.evaluate(() => { const h = window.__suite.viewer.bones.Hips; return h ? h.quaternion.toArray().map(n => +n.toFixed(3)) : null; });
  await p.waitForTimeout(700);
  const posed = await p.evaluate((a) => {
    const v = window.__suite.viewer;
    const hip = v.bones && v.bones.Hips;
    const q2 = hip ? hip.quaternion.toArray().map(n => +n.toFixed(3)) : null;
    const moved = a && q2 ? Math.max(...a.map((v2, i) => Math.abs(v2 - q2[i]))) : 0;
    return { url: v.currentUrl, hipsQ1: a, hipsQ2: q2, hipsDelta: +moved.toFixed(3) };
  }, q1);
  console.log('POSED', JSON.stringify(posed));
  await p.screenshot({ path: out + '/2_stance_landscape.png' });
  // TAKE PICTURE -> on-device portrait store (CARD FRAMING first, the way a
  // player frames a card before taking it)
  await p.evaluate(() => document.querySelector('#pose-cardframe').click());
  await p.waitForTimeout(600);
  await p.evaluate(() => document.querySelector('#pose-take').click());
  await p.waitForTimeout(1500);
  const stored = await p.evaluate(() => {
    const keys = Object.keys(localStorage).filter(k => k.startsWith('wh.portrait.'));
    return keys.map(k => ({ key: k, head: String(localStorage.getItem(k)).slice(0, 22), len: String(localStorage.getItem(k)).length }));
  });
  console.log('STORED', JSON.stringify(stored));
  await p.screenshot({ path: out + '/3_picture_saved_landscape.png' });
  // portrait orientation: victory pose, framed by the suite itself
  await p.setViewportSize({ width: 390, height: 844 });
  await p.waitForTimeout(2500);
  await p.evaluate(() => document.querySelector('[data-pose="victory"]').click());
  await p.waitForTimeout(3000);
  await p.screenshot({ path: out + '/4_victory_portrait.png' });
  const ok = stored.some(s => s.head.startsWith('data:image/png') && s.len > 10000);
  console.log('ASSERT portrait-stored', ok ? 'PASS' : 'FAIL');
  console.log('ERRORS', JSON.stringify(errs.slice(0, 12)));
  await b.close();
  if (!ok) process.exitCode = 2;
})();
