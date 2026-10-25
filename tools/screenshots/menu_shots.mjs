import { chromium } from 'playwright';
// Usage: node tools/screenshots/menu_shots.mjs BASE_URL TAG [private]
// Headless-Chrome walk of title/menu -> mode -> select -> stage -> results at 390x844 + 844x390.
const [base, tag, priv] = process.argv.slice(2);
const b = await chromium.launch({ channel:'chrome', args:['--use-angle=swiftshader','--enable-unsafe-swiftshader'] });
const sizes = { portrait:{width:390,height:844}, landscape:{width:844,height:390} };
const out = (n) => `/workspace/wh-shots/${tag}-${n}.png`;
for (const [sn, vp] of Object.entries(sizes)) {
  const p = await b.newPage({ viewport: vp, deviceScaleFactor: 1, isMobile: true, hasTouch: true });
  if (priv) await p.addInitScript(() => { globalThis.__WH_PRIVATE_ASSETS = true; });
  const errs = []; p.on('pageerror', e => errs.push(e.message)); p.on('response', r => { if (r.status() >= 400) errs.push(r.status() + ' ' + r.url()); });
  await p.goto(base, { waitUntil: 'load', timeout: 90000 });
  await p.waitForTimeout(6000);
  await p.screenshot({ path: out(`${sn}-1-title-menu`) });
  const click = async (sel) => { const e = await p.$(sel); if (!e) return false; await e.click({ force: true }).catch(()=>{}); await p.waitForTimeout(1500); return true; };
  await click('[data-mm="versus"]');
  await p.screenshot({ path: out(`${sn}-2-mode-select`) });
  // first sub option
  const sub = await p.$$('#screen-menu .mm-sub button, .mm-sub-list button, [data-mm-sub]');
  if (sub.length) { await sub[0].click({ force: true }).catch(()=>{}); await p.waitForTimeout(4000); }
  await p.screenshot({ path: out(`${sn}-3-select`) });
  const cards = await p.$$('#char-grid .card, #char-grid > *');
  if (cards[3]) { await cards[3].click({ force: true }); await p.waitForTimeout(3000); }
  await p.screenshot({ path: out(`${sn}-4-select-hover`) });
  const conf = await p.evaluate(() => { const e = document.getElementById('confirm-fighter'); if (!e) return 'none'; const r = e.getBoundingClientRect(); return { top: r.top, bottom: r.bottom, vis: r.bottom <= innerHeight && r.top >= 0, vh: innerHeight }; });
  console.log(sn, 'confirm', JSON.stringify(conf), 'cards', cards.length);
  for (let i = 0; i < 6; i++) {
    if (await p.evaluate(() => document.getElementById('screen-stage')?.classList.contains('active'))) break;
    const cs = await p.$$('#char-grid .char-card'); if (cs[7 + i]) { await cs[7 + i].click({ force: true }); await p.waitForTimeout(800); }
    await click('#confirm-fighter');
    if (i === 0) await p.screenshot({ path: out(`${sn}-5-after-confirm`) });
  }
  await p.waitForTimeout(2500); await p.screenshot({ path: out(`${sn}-6-stage-select`) });
  console.log(sn, 'stage-cards', await p.$$eval('#stage-grid .stage-card', e => e.length));
  await p.evaluate(() => { document.querySelectorAll('.screen').forEach(s => s.classList.remove('active')); document.getElementById('result-title').textContent = 'YOU WIN!'; document.getElementById('screen-result')?.classList.add('active'); });
  await p.waitForTimeout(800); await p.screenshot({ path: out(`${sn}-7-results`) });
  console.log(sn, 'errors', JSON.stringify([...new Set(errs)].slice(0, 30)));
  await p.close();
}
await b.close();
