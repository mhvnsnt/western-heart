// Re-shoot the blank/missing proof frames, fresh context per shot.
import { chromium } from '/home/hatch/workspace/_roster100-wave2-20261105/node_modules/playwright/index.mjs';
import { spawn } from 'node:child_process';
const OUT = new URL('./proof/', import.meta.url).pathname;
const server = spawn('python3', ['-m', 'http.server', '8933', '--bind', '127.0.0.1'], { cwd: new URL('./wh', import.meta.url).pathname, stdio: 'ignore' });
await new Promise((r) => setTimeout(r, 1000));
const EXE = '/home/hatch/workspace/_playverify-20261030/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell';
const shots = [
  { v: 'fixed', key: 'dio', bank: 'heihachi', clip: 'stance', t: 0.3, view: 'front' },
  { v: 'fixed', key: 'dio', bank: 'heihachi', clip: 'heavy', t: 0.4, view: 'front' },
  { v: 'fixed', key: 'yukihyo', bank: 'king', clip: 'stance', t: 0.3, view: 'front' },
  { v: 'fixed', key: 'yukihyo', bank: 'king', clip: 'heavy', t: 0.4, view: 'front' },
  { v: 'pristine', key: 'kinpo', bank: 'jin', clip: 'stance', t: 0.3, view: 'side' },
  { v: 'fixed', key: 'kinpo', bank: 'jin', clip: 'stance', t: 0.3, view: 'side' },
  { v: 'pristine', key: 'yukihyo', bank: 'king', clip: 'heavy', t: 0.4, view: 'q34' },
  { v: 'fixed', key: 'yukihyo', bank: 'king', clip: 'heavy', t: 0.4, view: 'q34' },
];
for (const s of shots) {
  const browser = await chromium.launch({ executablePath: EXE });
  const page = await browser.newPage({ viewport: { width: 640, height: 760 } });
  const url = `http://127.0.0.1:8933/game/harness.html?key=${s.key}&bank=${s.bank}&v=${s.v}&clip=${s.clip}&t=${s.t}&view=${s.view}`;
  const name = `${s.key}-${s.clip}-${s.view}-${s.v}.png`;
  try {
    await page.goto(url, { waitUntil: 'load', timeout: 90000 });
    await page.waitForFunction(() => window.__ready === true, null, { timeout: 90000 });
    await page.waitForTimeout(300);
    await page.screenshot({ path: OUT + name });
    console.log('shot', name);
  } catch (e) { console.log('FAIL', name, String(e).slice(0, 140)); }
  await browser.close();
}
server.kill();
console.log('done');
process.exit(0);
