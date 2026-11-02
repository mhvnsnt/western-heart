// tools/proof-harness/xray_anatomy_live_check.cjs — does the X-ray KO get its anatomy layers on a build that does
// not ship roster/<fighter>/anatomy/ (the size-capped GitHub Pages build)? 2026-11-02: on the live site every
// anatomy-layers.json 404'd, so Rage Art / Urge Smash KOs showed the skin / camera beat only; game/js/xray.js now
// falls back to jsDelivr.
//
// Loads game/js/xray.js as a module in a real browser page under the given base URL, optionally 404s the page's
// roster/*/anatomy/ requests (--block-local: live conditions on a full local checkout), prefetches each fighter and
// reports where each file came from and how many bone / muscle primitives parsed.
//
// usage: node tools/proof-harness/xray_anatomy_live_check.cjs <site-base-url> [--block-local] [fighter ...]
//   e.g. node tools/proof-harness/xray_anatomy_live_check.cjs http://127.0.0.1:8765 --block-local pantera demonio
//        node tools/proof-harness/xray_anatomy_live_check.cjs https://mhvnsnt.github.io/western-heart pantera
const { chromium } = require('playwright');

(async () => {
  const args = process.argv.slice(2);
  const base = (args.shift() || '').replace(/\/$/, '');
  if (!base) { console.error('usage: xray_anatomy_live_check.cjs <site-base-url> [--block-local] [fighter ...]'); process.exit(2); }
  const block = args.includes('--block-local');
  const fighters = args.filter((a) => !a.startsWith('--'));
  if (!fighters.length) fighters.push('pantera', 'demonio');
  const b = await chromium.launch();
  const p = await (await b.newContext()).newPage();
  const reqs = [];
  p.on('response', (r) => { if (/anatomy-layers\.json/.test(r.url())) reqs.push(`${r.status()} ${r.url()}`); });
  if (block) {
    const host = new URL(base).host.replace(/\./g, '\\.');
    await p.route(new RegExp(`^https?://${host}/.*roster/[^/]+/anatomy/`), (r) => r.fulfill({ status: 404, body: 'not on pages' }));
  }
  // the module resolves '../roster/...' against the page, so the page must sit in game/ like game/index.html
  await p.goto(`${base}/game/index.html?xraycheck=1`, { waitUntil: 'domcontentloaded', timeout: 120000 });
  const res = await p.evaluate(async ({ base, fighters }) => {
    const { XraySystem } = await import(`${base}/game/js/xray.js`);
    const out = {};
    for (const fid of fighters) {
      const x = new XraySystem({ arena: null }, null);
      await x.prefetch(fid);
      // builds before 2026-11-02 return nothing from prefetch(): wait for the cache to settle (up to 20 s)
      for (let i = 0; i < 200 && x._cache[fid] === undefined; i++) await new Promise((r) => setTimeout(r, 100));
      const l = x._cache[fid];
      out[fid] = l ? { bone: l.bone.length, muscle: l.muscle.length, organ: l.organ.length } : l;
    }
    return out;
  }, { base, fighters });
  console.log('LAYERS', JSON.stringify(res));
  console.log('REQUESTS\n' + reqs.join('\n'));
  const okAll = fighters.every((f) => res[f] && res[f].bone > 0);
  console.log(okAll ? 'PASS: every fighter got its anatomy layers' : 'FAIL: a fighter has no layers');
  await b.close();
  process.exit(okAll ? 0 : 1);
})();
