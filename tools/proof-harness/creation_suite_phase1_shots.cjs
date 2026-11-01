const { chromium } = require('playwright');
(async () => {
  const out = process.argv[3];
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const ctx = await b.newContext({ viewport: { width: 844, height: 390 }, hasTouch: true, isMobile: true });
  const p = await ctx.newPage();
  const errs = [];
  p.on('pageerror', (e) => errs.push('pageerror ' + e.message.slice(0, 200)));
  p.on('console', (m) => { if (m.type() === 'error' || m.type() === 'warning') errs.push(m.type() + ' ' + m.text().slice(0, 200)); });
  await p.route(/workers\.dev/, (r) => r.abort());
  await p.goto(process.argv[2], { waitUntil: 'load', timeout: 120000 });
  await p.waitForFunction(() => document.querySelector('#loader.done') && window.__suite && window.__suite.viewer && window.__suite.viewer.ready, null, { timeout: 180000, polling: 500 });
  await p.waitForTimeout(1500);
  await p.screenshot({ path: out + '/1_first_visit.png' });
  const modalTitle = await p.evaluate(() => document.querySelector('#modal-title').textContent);
  console.log('MODAL', modalTitle, 'cards', await p.evaluate(() => document.querySelectorAll('[data-t]').length));
  await p.evaluate(() => document.querySelector('[data-t="powerhouse"]').click());
  await p.waitForFunction(() => window.__suite.viewer.currentUrl && /powerhouse\.glb/.test(window.__suite.viewer.currentUrl), null, { timeout: 120000, polling: 500 });
  await p.waitForTimeout(2500);
  await p.screenshot({ path: out + '/2_powerhouse_landscape.png' });
  const st = await p.evaluate(() => ({ tpl: window.__suite.F.template, glb: window.__suite.F.baseGlb, bt: window.__suite.F.body.body_type,
    bones: Object.keys(window.__suite.viewer.bones || {}).filter(k => /^(Head|LeftArm|Hips|LeftUpLeg)$/.test(k)) }));
  console.log('STATE', JSON.stringify(st));
  // move a body slider
  await p.evaluate(() => { const i = document.querySelector('#morph-bulk input') || document.querySelector('#prop-muscle input'); if (i) { i.value = i.max; i.dispatchEvent(new Event('input')); } });
  await p.waitForTimeout(1500);
  await p.screenshot({ path: out + '/3_slider_landscape.png' });
  await p.setViewportSize({ width: 390, height: 844 });
  await p.waitForTimeout(2500);
  await p.screenshot({ path: out + '/4_portrait.png' });
  await p.evaluate(() => document.querySelector('#btn-roster').click());
  await p.waitForTimeout(1000);
  await p.screenshot({ path: out + '/5_create_edit_portrait.png' });
  console.log('ERRORS', JSON.stringify(errs.slice(0, 12)));
  await b.close();
})();
