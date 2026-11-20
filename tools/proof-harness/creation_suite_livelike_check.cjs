const { chromium } = require('playwright');
(async () => {
  const out = process.argv[3];
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await (await b.newContext({ viewport: { width: 390, height: 844 }, hasTouch: true, isMobile: true })).newPage();
  const ev = [];
  p.on('pageerror', (e) => ev.push('pageerror ' + e.message.slice(0, 200)));
  p.on('console', (m) => { if (m.type() === 'error' || m.type() === 'warning') ev.push(m.type() + ' ' + m.text().slice(0, 200)); });
  p.on('requestfailed', (r) => ev.push('requestfailed ' + r.url().slice(0, 120) + ' ' + (r.failure() && r.failure().errorText)));
  p.on('response', (r) => { if (/\.glb|jsdelivr/.test(r.url())) ev.push('resp ' + r.status() + ' ' + r.url().slice(0, 120)); });
  // live conditions: these are not on Pages
  await p.route(/^http:\/\/127\.0\.0\.1:8765\/customization\/(create-fighter|templates\/meshes)\//, (r) => r.fulfill({ status: 404, body: 'not on pages' }));
  await p.goto(process.argv[2], { waitUntil: 'load', timeout: 120000 });
  try { await p.waitForFunction(() => document.querySelector('#loader.done') && window.__suite && window.__suite.viewer && window.__suite.viewer.ready, null, { timeout: 150000, polling: 500 }); }
  catch (e) { const st = await p.evaluate(() => ({ loader: (document.querySelector('#loader')||{}).className, suite: !!window.__suite, ready: !!(window.__suite && window.__suite.viewer && window.__suite.viewer.ready) })); console.log('TIMEOUT', JSON.stringify(st)); console.log(ev.slice(0, 30).join('\n')); await b.close(); return; }
  await p.waitForTimeout(2000);
  const st = await p.evaluate(() => ({ url: window.__suite.viewer.currentUrl, modal: document.querySelector('#modal-title').textContent, cards: document.querySelectorAll('[data-t]').length }));
  console.log('STATE', JSON.stringify(st));
  await p.screenshot({ path: out + '/livelike_portrait.png' });
  console.log('ERRORS', JSON.stringify(ev.filter((e) => !/404/.test(e)).slice(0, 8)));
  await b.close();
})();
