import { chromium } from 'playwright'; import fs from 'node:fs';
const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--use-gl=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'] });
const p = await b.newPage({ viewport: { width: 960, height: 540 } });
await p.goto('http://127.0.0.1:8812/game/index.html');
await p.waitForFunction(() => window.__startFight, null, { timeout: 120000 });
await p.evaluate(([a, c]) => window.__startFight(a, c, {}), [process.argv[2], 'kronos']);
await p.waitForFunction(() => { const g = window.__game; return g && g.roundState === 'fight'; }, null, { timeout: 400000, polling: 500 });
await p.evaluate(fs.readFileSync('test/e2e/moveset-sweep.page.js','utf8')); await p.waitForFunction(() => window.__sweepReady);
console.log(await p.evaluate(fs.readFileSync(process.argv[3],'utf8'))); await b.close();
