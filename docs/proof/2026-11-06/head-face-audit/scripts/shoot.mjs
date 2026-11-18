// Playwright screenshots of the proof harness. Usage: node shoot.mjs
import { chromium } from '/home/hatch/workspace/_roster100-wave2-20261105/node_modules/playwright/index.mjs';
import { spawn } from 'node:child_process';
import { mkdirSync } from 'node:fs';
const OUT = new URL('./proof/', import.meta.url).pathname;
mkdirSync(OUT, { recursive: true });
const server = spawn('python3', ['-m', 'http.server', '8931', '--bind', '127.0.0.1'], { cwd: new URL('./wh', import.meta.url).pathname, stdio: 'ignore' });
await new Promise((r) => setTimeout(r, 1200));
const browser = await chromium.launch({ executablePath: '/home/hatch/workspace/_playverify-20261030/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell' });
const page = await browser.newPage({ viewport: { width: 640, height: 760 } });
const shots = [];
for (const v of ['pristine', 'fixed']) {
  for (const [key, bank] of [['kinpo', 'jin'], ['zui', 'jin'], ['yukihyo', 'king'], ['dio', 'heihachi']]) {
    for (const [clip, t] of [['stance', 0.3], ['heavy', 0.4]]) {
      shots.push({ v, key, bank, clip, t, view: 'front' });
    }
  }
}
shots.push({ v: 'pristine', key: 'kinpo', bank: 'jin', clip: 'stance', t: 0.3, view: 'side' });
shots.push({ v: 'fixed', key: 'kinpo', bank: 'jin', clip: 'stance', t: 0.3, view: 'side' });
shots.push({ v: 'pristine', key: 'yukihyo', bank: 'king', clip: 'heavy', t: 0.4, view: 'q34' });
shots.push({ v: 'fixed', key: 'yukihyo', bank: 'king', clip: 'heavy', t: 0.4, view: 'q34' });
for (const s of shots) {
  const url = `http://127.0.0.1:8931/game/harness.html?key=${s.key}&bank=${s.bank}&v=${s.v}&clip=${s.clip}&t=${s.t}&view=${s.view}`;
  try {
    await page.goto(url, { waitUntil: 'load', timeout: 60000 });
    await page.waitForFunction(() => window.__ready === true, null, { timeout: 60000 });
    await page.waitForTimeout(250);
    const name = `${s.key}-${s.clip}-${s.view}-${s.v}.png`;
    await page.screenshot({ path: OUT + name });
    console.log('shot', name);
  } catch (e) { console.log('FAIL', s, String(e).slice(0, 160)); }
}
await browser.close();
server.kill();
console.log('done');
