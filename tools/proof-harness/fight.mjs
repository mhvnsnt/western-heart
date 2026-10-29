// Fight screenshot + state probe
//
// node tools/proof-harness/fight.mjs OUTDIR P1 P2 [query] [shots] [interval_ms]
// Starts an arcade fight through window.__modes, captures frames and logs each fighter's state,
// attack, hips/head height and current T3 clip (the roster-sweep proof).
//
// Proof harness from the 2026-10-20/21 Claude session (tools/TOOLS-INDEX.md). Serve the repo
// first:  python3 -m http.server 8765   (from the repo root), then run with node 18+.
// PLAYWRIGHT_MODULE / CHROMIUM_PATH override the defaults below (cloud container layout).
// Usage: node fight.mjs <outdir> <p1> <p2> [query] [shots] [interval_ms]
const { chromium } = await import(process.env.PLAYWRIGHT_MODULE || '/opt/node22/lib/node_modules/playwright/index.mjs');
import fs from 'fs';
const [,, out='shots', p1='pantera', p2='demonio', q='demo=1', nShots='6', every='700'] = process.argv;
fs.mkdirSync(out, { recursive: true });
const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
  args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: 960, height: 540 } });
const logs = [];
page.on('console', m => logs.push(`[${m.type()}] ${m.text()}`));
page.on('pageerror', e => logs.push(`[pageerror] ${e.message}`));
// ATTIRES='{"pantera":"pantera-leopard-king"}' picks attires the way the select screen saves them.
if (process.env.ATTIRES) await page.addInitScript((m) => localStorage.setItem('wh_attires_v1', m), process.env.ATTIRES);
await page.goto(`http://127.0.0.1:${process.env.PORT || 8765}/game/index.html?${q}`, { waitUntil: 'load' });
await page.waitForTimeout(1500);
// modes.js loads lazily (game/js/lazy.js): wait for the controller instead of assuming it is up.
await page.waitForFunction(() => window.__modes, null, { timeout: 60000 });
await page.evaluate(([a, b]) => { window.__modes.startMode('arcade'); }, [p1, p2]);
await page.waitForTimeout(500);
// start fight directly through the mode controller's startFight dep
await page.evaluate(async ([a, b]) => {
  const m = window.__modes;
  await window.__modes.startFight(a, b, { mode: "arcade" });
}, [p1, p2]).catch(e => logs.push('startFight err ' + e.message));
const cdp = await page.context().newCDPSession(page);
await page.waitForTimeout(4000);
for (let i = 0; i < +nShots; i++) {
  const r = await cdp.send('Page.captureScreenshot', { format: 'png' });
  fs.writeFileSync(`${out}/f${String(i).padStart(2,'0')}.png`, Buffer.from(r.data, 'base64'));
  const st = await page.evaluate(() => { const g = window.__game; if (!g || !g.p1) return null;
    const f = (x) => { const h = x.bones.Hips, hd = x.bones.Head; if (!h || !hd) return { id: x.char.id, model: x.char.model, bones: Object.keys(x.bones).slice(0,8) }; const a = new (h.position.constructor)(), b = new (h.position.constructor)();
      h.getWorldPosition(a); hd.getWorldPosition(b);
      return { id: x.char.id, model: x.char.model, st: x.state, atk: x.attackName, hipsY: +a.y.toFixed(2), headY: +b.y.toFixed(2), t3: Object.keys(x.t3actions).length, cur: x._t3current?._clip?.name || null }; };
    return { p1: f(g.p1), p2: f(g.p2), round: g.roundState }; });
  logs.push('STATE ' + i + ' ' + JSON.stringify(st));
  await page.waitForTimeout(+every);
}
fs.writeFileSync(`${out}/console.log`, logs.join('\n'));
await browser.close();
