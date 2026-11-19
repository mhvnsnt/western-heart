// QA 2026-10-23 (PR #965): in-match targeting regression test.
// Real fight via taps, then: sidestep -> both fighters back on one line and
// facing each other; jab connects after the step; cross-up -> facing flips.
import { chromium, devices } from 'playwright';
import fs from 'node:fs';
const BASE = process.env.WH_URL || 'http://127.0.0.1:8811';
const SHOTS = process.argv[2] || 'facing-shots'; fs.mkdirSync(SHOTS, { recursive: true });
const b = await chromium.launch();
const ctx = await b.newContext({ ...devices['iPhone 13'], viewport: { width: 390, height: 844 }, hasTouch: true, isMobile: true });
const p = await ctx.newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e)));
await p.goto(BASE + '/game/index.html');
await p.waitForSelector('#screen-menu [data-mm]', { state: 'visible', timeout: 30000 }); await p.waitForTimeout(5000);
const tap = async s => { try { await p.tap(s, { timeout: 60000 }); } catch { await p.locator(s).dispatchEvent('click'); } await p.waitForTimeout(1500); };
await tap('[data-mm="versus"]'); await tap('#mm-cards .mm-card[data-action] >> nth=0');
await tap('.char-card >> nth=0'); await tap('#confirm-fighter'); await tap('.char-card >> nth=2'); await tap('#confirm-fighter');
await p.tap('#confirm-stage');
await p.waitForFunction(() => window.__game && window.__game.p1 && getComputedStyle(document.getElementById('hud')).display !== 'none', null, { timeout: 90000 });
await p.waitForTimeout(4000);
const r = await p.evaluate(async () => {
  const G = window.__game, a = G.p1, d = G.p2; const W = ms => new Promise(s => setTimeout(s, ms));
  if (G.ai) G.ai.update = () => {};
  const err = f => { const o = f === a ? d : a; const want = Math.atan2(o.root.position.x - f.root.position.x, o.root.position.z - f.root.position.z);
    let e = Math.abs(f.lean.rotation.y - want) % (2 * Math.PI); return Math.min(e, 2 * Math.PI - e); };
  const out = {};
  for (let i = 0; i < 60 && !(a.canAct() && d.canAct() && !G.paused); i++) await W(500);
  out.ready = a.canAct() && d.canAct(); out.st = [a.state, d.state, G.state || G.phase || null];
  await W(500); a.trySidestep(-1); await W(400); out.dzMid = Math.abs(a.root.position.z - d.root.position.z);
  out.yawMid = Math.max(err(a), err(d));
  await W(2500); out.dzAfter = Math.abs(a.root.position.z - d.root.position.z); out.yawAfter = Math.max(err(a), err(d));
  // jab after the step must connect
  const s = Math.sign(d.root.position.x - a.root.position.x) || 1; d.root.position.x = a.root.position.x + 1.2 * s; await W(300);
  const hp0 = d.hp; for (let i = 0; i < 4 && d.hp === hp0; i++) { a.tryAttack('1'); await W(600); } out.jabDmg = hp0 - d.hp;
  // cross-up: put the opponent on the other side; facing must flip
  await W(1500); const f0 = a.facing; d.root.position.x = a.root.position.x - 1.6 * s; await W(1200);
  out.flipped = a.facing === -f0 && d.facing === f0; out.yawCross = Math.max(err(a), err(d));
  return out; });
console.log(JSON.stringify(r));
await p.screenshot({ path: `${SHOTS}/facing-after.png`, timeout: 30000 }).catch(() => {}); await b.close();
const fails = [];
if (!(r.dzMid > 0.5)) fails.push(`sidestep did not leave the line (dz ${r.dzMid})`);
if (!(r.dzAfter < 0.3)) fails.push(`not re-aligned after sidestep (dz ${r.dzAfter})`);
if (!(r.yawAfter < 0.2)) fails.push(`not facing after sidestep (yaw err ${r.yawAfter})`);
if (!(r.jabDmg > 0)) fails.push('jab whiffed after sidestep');
if (!r.flipped || !(r.yawCross < 0.2)) fails.push(`cross-up facing wrong ${JSON.stringify(r)}`);
if (errs.length) console.log('pageerrors:', errs.slice(0, 5));
if (fails.length) { console.error('FAIL\n' + fails.join('\n')); process.exit(1); }
console.log('PASS');
