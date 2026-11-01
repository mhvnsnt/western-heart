// tools/proof-harness/fight_load_recovery_probe.mjs — break a fight load on purpose and check the game still gets the
// player into the fight with no tap and no manual reload (owner 2026-11-01: "it keeps kicking me back out to the arena
// select menu and then I have to end up reloading the game ... that needs to be fixed 100%").
//
// Scenarios (each in a fresh browser context):
//   model   the player's fighter model fails to download (every request aborted) until the first failed fight load:
//           startFight must retry on its own (FIGHT-LOAD RECOVERY v2: retry, then SAFE LOAD) -> FIGHT, 0 reloads.
//   module  a game module fails to import (js/fighter.js aborted, as when a deploy lands while the tab is open) until
//           the page reloads: startFight must reload straight back into the same versus fight -> FIGHT, 1 reload.
//   build   the fight fails to BUILD once (game.startMatch throws): one clean rebuild -> FIGHT, 0 reloads.
// Fights start through the versus controller (window.__modes.resumeVersus: the same _beginVersus path a stage-screen
// CONFIRM ends in), so the resumed fight keeps its rules / result screen.
//
// usage: NO_REMOTE=1 node tools/proof-harness/fight_load_recovery_probe.mjs <game-url> <out-dir> [p1] [p2] [stage] [scenario ...]
import { createRequire } from 'module';
import fs from 'fs';
const { chromium } = createRequire(import.meta.url)('playwright');
const [,, url, out, p1 = 'pantera', p2 = 'negativo', stage = 'shrine', ...only] = process.argv;
if (!out) { console.error('usage: node fight_load_recovery_probe.mjs <game-url> <out-dir> [p1] [p2] [stage] [model|module|build ...]'); process.exit(2); }
fs.mkdirSync(out, { recursive: true });
const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });

async function scenario(name) {
  const ctx = await browser.newContext({ viewport: { width: 640, height: 480 } });
  const page = await ctx.newPage();
  const t0 = Date.now();
  const at = () => +((Date.now() - t0) / 1000).toFixed(1);
  const ev = [];
  let loads = 0, failedLoads = 0, broken = true, aborted = 0;
  page.on('console', (m) => {
    const t = m.text();
    if (/fight load failed|startMatch failed|Failed to load|Retry|reload|\[resume\]/i.test(t)) ev.push(`${at()}s [${m.type()}] ${t.slice(0, 200)}`);
    if (/\[WH\] fight load failed/.test(t)) { failedLoads++; if (name === 'model') broken = false; }
  });
  page.on('pageerror', (e) => ev.push(`${at()}s [pageerror] ${e.message.slice(0, 200)}`));
  page.on('load', () => { loads++; ev.push(`${at()}s [load] page load #${loads}`); if (name === 'module' && loads >= 2) broken = false; });
  if (process.env.NO_REMOTE) await page.route(/workers\.dev/, (r) => r.abort());
  if (name === 'model') {
    // the player's model GLB, on every host (page, jsDelivr, ...)
    await page.route((u) => new RegExp(`/${p1}[^/]*\\.glb(\\?|$)`).test(u.pathname + u.search) || new RegExp(`/roster/${p1}/`).test(u.pathname) && /\.glb$/.test(u.pathname),
      (r) => { if (broken) { aborted++; return r.abort('connectionreset'); } return r.continue(); });
  }
  if (name === 'module') {
    await page.route(/\/js\/fighter\.js(\?|$)/, (r) => { if (broken) { aborted++; return r.abort('connectionreset'); } return r.continue(); });
  }
  await page.goto(url, { waitUntil: 'load', timeout: 180000 });
  await page.waitForFunction(() => !!(window.__modes && window.__game), null, { timeout: 180000, polling: 250 });
  if (name === 'build') {
    await page.evaluate(() => {
      const g = window.__game, orig = g.startMatch.bind(g);
      let n = 0;
      g.startMatch = (...a) => { if (!n++) return Promise.reject(new Error('probe: simulated fight build failure')); return orig(...a); };
    });
  }
  const tStart = at();
  await page.evaluate(({ p1, p2, stage }) => { window.__modes.resumeVersus(p1, p2, stage); }, { p1, p2, stage });
  let outcome = 'TIMEOUT';
  const end = Date.now() + 480000;
  while (Date.now() < end) {
    const st = await page.evaluate(() => {
      const g = window.__game, hud = document.getElementById('hud'), stageScr = document.getElementById('screen-stage');
      const vis = (e) => !!e && getComputedStyle(e).display !== 'none' && !e.classList.contains('hidden');
      return { fight: !!(g && g.p1 && (g.roundState === 'fight' || g.roundState === 'intro') && vis(hud)),
               stage: vis(stageScr) && stageScr.classList.contains('active'),
               hint: (document.getElementById('stage-hint') || {}).textContent || '' };
    }).catch(() => null);  // mid-reload
    if (st && st.fight) { outcome = 'FIGHT'; break; }
    if (st && st.stage && /fail/i.test(st.hint)) { outcome = 'BOUNCED: ' + st.hint.slice(0, 160); break; }
    await page.waitForTimeout(500);
  }
  const res = { scenario: name, outcome, seconds: +(at() - tStart).toFixed(1), pageLoads: loads, failedLoads, abortedRequests: aborted, events: ev };
  try { await page.screenshot({ path: `${out}/${name}.png`, timeout: 60000 }); } catch (e) { /* slow renderer */ }
  await ctx.close();
  console.log('SCENARIO', JSON.stringify({ ...res, events: undefined }));
  return res;
}

const results = [];
for (const s of (only.length ? only : ['model', 'module', 'build'])) results.push(await scenario(s));
fs.writeFileSync(`${out}/fight_load_recovery.json`, JSON.stringify({ url, p1, p2, stage, results }, null, 1));
const pass = (r) => r.outcome === 'FIGHT' && (r.scenario !== 'module' || r.pageLoads === 2) && (r.scenario === 'module' || r.pageLoads === 1);
console.log(results.every(pass) ? 'ALL PASS' : 'FAIL', results.map((r) => `${r.scenario}=${pass(r) ? 'PASS' : 'FAIL'}`).join(' '));
await browser.close();
