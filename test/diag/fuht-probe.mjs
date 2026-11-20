import { chromium } from 'playwright';
const b = await chromium.launch({ args: ['--use-gl=swiftshader','--enable-unsafe-swiftshader','--js-flags=--max-old-space-size=6144'] });
const p = await b.newPage({ viewport: { width: 960, height: 540 } });
await p.addInitScript(() => { try { localStorage.setItem('wh_softbody_v1', 'off'); } catch {} });
await p.goto('http://127.0.0.1:8834/game/index.html');
await p.waitForFunction(() => window.__startFight, null, { timeout: 360000 });
await p.evaluate(() => window.__startFight('jin', 'docfrank', {}));
await p.waitForFunction(() => { const g = window.__game; return g && g.roundState === 'fight' && g.p2; }, null, { timeout: 900000, polling: 500 });
const r = await p.evaluate(async () => {
  const g = window.__game, f = g.p2, a = g.p1; g.ai.update = () => {}; g.timer = 9999;
  const move = { damage: 5, knock: 6, startup: 0.2, active: 0.05, recovery: 0.3 };
  const out = {};
  for (const [lbl, st] of [['back', 'BT'], ['front', null]]) {
    f.stance = st; f.state = 'idle'; f.hp = f.maxHp || 170;
    f.receiveHit ? f.receiveHit(move, a, false) : f.takeHit(move, a, false);
    out[lbl + '_state'] = f.state; out[lbl+'_kd'] = f._kdHeadTowards; await new Promise((r)=>setTimeout(r,3000)); let seen = null;
    for (let i = 0; i < 1500 && !seen; i++) { await new Promise((r) => requestAnimationFrame(r)); if (f.state !== 'knockdown') seen = f.stance || 'none'; out[lbl+'_last'] = f.state; }
    out[lbl + '_exit'] = seen; out.id = f._movesetId;
  }
  return out;
});
console.log(JSON.stringify(r)); await b.close();
