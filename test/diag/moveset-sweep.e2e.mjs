// Full moveset sweep (Grok, 2026-10-28). Serve the repo root on $WH_URL.
// Run: node test/e2e/moveset-sweep.e2e.mjs <outDir> [fighter ...]
// For every move in each fighter's moveset file, the sweep types the move's own input on
// the keyboard into a live fight (sim stepped by hand at 60 Hz, page clock = sim clock),
// then checks: (1) the game fired THAT move (attackName resolves to the move's key),
// (2) every hit of a string fired in order, (3) a damaging move connected with the
// opponent (hit, block, launch, knockdown or throw), (4) throws reach thrower+victim exec
// states with clips, (5) launchers juggle (a follow-up hits the airborne opponent).
// Output: <outDir>/<fighter>.json per fighter (one row per move) + console summary.
import { chromium } from 'playwright';
import fs from 'node:fs';
const BASE = process.env.WH_URL || 'http://127.0.0.1:8811';
// WH_LOAD_SCALE stretches the page / fight load timeouts on a loaded box (heavy bodies: bob, burgers).
const LS = Math.max(1, Number(process.env.WH_LOAD_SCALE) || 1);
const OUT = process.argv[2] || 'moveset-sweep-out';
const OPP = process.env.WH_OPP || 'kronos';
const LIMIT = +(process.env.WH_SWEEP_LIMIT || 0); // dev: moves per fighter
fs.mkdirSync(OUT, { recursive: true });
const idx = JSON.parse(fs.readFileSync(new URL('../../game/assets/movesets/index.json', import.meta.url), 'utf8'));
let FIGHTERS = process.argv.slice(3);
const { bodyFor } = await import('./moveset-sweep.bodies.mjs');
const SKIP_DONE = process.env.WH_SWEEP_SKIP_DONE === '1';
if (!FIGHTERS.length) FIGHTERS = Object.keys(idx.fighters);
const launch = () => chromium.launch({ executablePath: process.env.CHROME || undefined,
  args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist',
    // sweep only: michiko / nightwolf / demonio renderers ran out of heap on the default limit
    '--js-flags=--max-old-space-size=' + (process.env.WH_SWEEP_HEAP_MB || 6144)] });
let b = await launch();
const PAGE_LIB = fs.readFileSync(new URL('./moveset-sweep.page.js', import.meta.url), 'utf8');

async function fight(P1, body) {
  const p = await b.newPage({ viewport: { width: 960, height: 540 } });
  p.errs = []; p.on('pageerror', (e) => p.errs.push(String(e).slice(0, 300)));
  if (process.env.WH_SWEEP_DEBUG) p.on('console', (m) => console.log('   [page]', m.text().slice(0, 200)));
  // Soft-body tissue (softbody.js) recomputes vertex normals every step on heavy bodies (blanka, bob,
  // burgers, chargers): with the sweep's thousands of synthetic steps on SwiftShader that ran past 5 min.
  // Tissue jiggle is cosmetic and not part of move correctness, so the sweep plays with it off.
  await p.addInitScript(() => { try { localStorage.setItem('wh_softbody_v1', 'off'); } catch {} });
  await p.goto(BASE + '/game/index.html');
  await p.waitForFunction(() => window.__startFight, null, { timeout: 120000 * LS });
  // Moveset ids that are not roster ids play on their mapped WH roster body (bodies.mjs):
  // the roster entry with this moveset id and the mapped model, so p1._movesetId = P1.
  await p.evaluate(async ([a, c, bd]) => {
    if (!bd || bd.how === 'roster id') return window.__startFight(a, c, {});
    const R = await import('./js/roster-full.js');
    const e = bd.rosterId ? R.getFighter(bd.rosterId) : R.modelPendingFighter(a);
    return window.__startFight(a, c, { playerChar: { ...e, id: a, model: bd.model, modelPending: false } });
  }, [P1, OPP, body]);
  await p.waitForFunction(() => { const g = window.__game; return g && g.roundState === 'fight' && g.p1 && g.p2; }, null, { timeout: 400000 * LS, polling: 500 });
  if (process.env.WH_SWEEP_DEBUG) console.log(`.. ${P1}: in fight`);
  await p.evaluate(PAGE_LIB);
  await p.waitForFunction(() => window.__sweepReady, null, { timeout: 60000 * LS });
  return p;
}

for (const id of FIGHTERS) {
  if (SKIP_DONE && fs.existsSync(`${OUT}/${id}.json`) && !JSON.parse(fs.readFileSync(`${OUT}/${id}.json`, 'utf8')).error) continue;
  const t0 = Date.now();
  let p;
  // a crashed renderer / browser is relaunched and the fighter retried once
  const body = bodyFor(id, idx.fighters[id] || {});
  if (!body.ok) { fs.writeFileSync(`${OUT}/${id}.json`, JSON.stringify({ fighter: id, blocker: body })); console.log(`== ${id}: BLOCKER ${body.how} ${body.file || ''}`); continue; }
  try { p = await fight(id, body); } catch (e0) { try { if (!b.isConnected()) b = await launch(); p = await fight(id, body); } catch (e) { p = null; e0 = e; }
    if (!p) { const e = e0; fs.writeFileSync(`${OUT}/${id}.json`, JSON.stringify({ fighter: id, error: 'fight did not load: ' + String(e).slice(0, 200) })); console.log(`== ${id}: LOAD FAIL`); if (!b.isConnected()) b = await launch(); continue; } }
  const got = await p.evaluate(() => window.__game.p1.char.id);
  const gotModel = await p.evaluate(() => window.__game.p1.char.model);
  if (got !== id) { fs.writeFileSync(`${OUT}/${id}.json`, JSON.stringify({ fighter: id, error: `game loaded '${got}'` })); console.log(`== ${id}: loaded ${got}`); await p.close(); continue; }
  if (gotModel !== body.model && !String(gotModel).startsWith(`${body.model}-attire`)) { fs.writeFileSync(`${OUT}/${id}.json`, JSON.stringify({ fighter: id, body, error: `game loaded model '${gotModel}', not '${body.model}'` })); console.log(`== ${id}: model ${gotModel} != ${body.model}`); await p.close(); continue; }
  fs.mkdirSync(`${OUT}/shots`, { recursive: true });
  await p.evaluate(() => window.__game.render && window.__game.render(0)).catch(() => {});
  await p.screenshot({ path: `${OUT}/shots/${id}.png` }).catch(() => {});
  if (process.env.WH_SWEEP_RT) { // debug: a row clip's decoded root track (forward/lateral, m)
    console.log(JSON.stringify(await p.evaluate((n) => { const f = window.__game.p1, c = f._t3 && f._t3.clips; if (n === 'yaw') { const res = []; for (const [k, cl] of Object.entries(c || {})) { const R = cl.userData && cl.userData.raw; const rt = R && R.root_t; if (!rt || rt.length < 2 || !R.rot.Hips) continue; const q = R.rot.Hips[0]; const yaw = Math.atan2(2 * (q[3] * q[1] + q[0] * q[2]), 1 - 2 * (q[1] * q[1] + q[0] * q[0])) * 57.3;
      let bi = 0, bd = 0; rt.forEach((r, i) => { const d = Math.hypot(r[0] - rt[0][0], r[2] - rt[0][2]); if (d > bd) { bd = d; bi = i; } }); if (bd < 0.3) continue; const dir = Math.atan2(rt[bi][0] - rt[0][0], rt[bi][2] - rt[0][2]) * 57.3; res.push([k, Math.round(yaw), Math.round(dir), +bd.toFixed(2)]); } return res; } if (n === '*') { const out = { bank: f._t3 && f._t3.bank, pos: 0, neg: 0 }; for (const [k, cl] of Object.entries(c || {})) { const rt = cl.userData && cl.userData.raw && cl.userData.raw.root_t; if (!rt || rt.length < 2) continue; const m = Math.max(...rt.map((r) => r[2] - rt[0][2])), mn = Math.min(...rt.map((r) => r[2] - rt[0][2])); if (m > 0.3 && m > -mn) out.pos++; else if (mn < -0.3) out.neg++; } return out; } return n.split('|').map((k) => { const cl = c && c[k]; const rt = cl && cl.userData && cl.userData.raw && cl.userData.raw.root_t;
      return { k, n: rt && rt.length, z: rt && rt.filter((_, i) => i % 3 === 0).map((r) => +r[2].toFixed(2)), x: rt && rt.filter((_, i) => i % 3 === 0).map((r) => +r[0].toFixed(2)) }; }); }, process.env.WH_SWEEP_RT))); process.exit(0); }
  if (process.env.WH_SWEEP_TRACE) { // debug: sweep one move with its frame trace
    console.log(JSON.stringify(await p.evaluate((k) => { const L = window.__moveList(); return k.split('|').map((kk) => { const m = L.find((x) => x.key === kk); if (!m) return { key: kk, miss: 1 }; const r = window.__sweepMove({ ...m, trace: true }); const T = r.trace || [], A = T.filter((t) => t.p1.st === 'attack');
        const dx = A.map((t) => +(t.p2.x - t.p1.x).toFixed(2)); return { key: kk, ok: r.ok, why: r.why, setup: r.setup, n: A.length, dx0: dx[0], dxMin: Math.min(...dx), dxMax: Math.max(...dx), p2: [...new Set(T.map((t) => t.p2.st))].join('/'), clip: A[0] && A[0].p1.clip }; }); }, process.env.WH_SWEEP_TRACE))); process.exit(0); }
  if (process.env.WH_SWEEP_PROBE) { // debug: per-step trace of one move (phase, hitbox, reach, defender state)
    console.log(JSON.stringify(await p.evaluate((n) => { const g = window.__game, W = window.__sw, f = g.p1, o = g.p2; W.reset(1.1); const out = [];
      f.tryAttack(n); for (let i = 0; i < 50; i++) { W.step(1); const hb = f.getHitbox ? (f._attackPhase === 'active' && !f.hasHit ? 'A' : '') : ''; const H = (f._attackPhase === 'active') ? f.getHitbox() : null; if (H) f._prevHitPoint = null; out.push([i, H && +H.reach.toFixed(2), H && [+(H.x-f.root.position.x).toFixed(2), +H.y.toFixed(2)], f.attack && f.attack.hitWord, f.attack && JSON.stringify(f.attack).slice(0,400), o._postureBits(), o.canBeHitBy(f.attack||{}), o.getHurtboxes().length, o.invuln, f.state, f.attackName, f._attackPhase, +f.stateT.toFixed(3), f.attack && f.attack.startup, f.attack && f.attack.active, o.state, +(o.root.position.x - f.root.position.x).toFixed(2), f.hasHit]); }
      return out; }, process.env.WH_SWEEP_PROBE))); process.exit(0); }
  let list = await p.evaluate(() => window.__moveList());
  if (LIMIT) list = list.slice(0, LIMIT);
  const rows = [];
  const CH = process.env.WH_SWEEP_DEBUG ? 1 : 20;
  for (let i = 0; i < list.length; i += CH) {
    if (process.env.WH_SWEEP_DEBUG) console.log(`.. ${id} move ${i} ${list[i].key} ${list[i].input}`);
    const part = await p.evaluate((chunk) => chunk.map((m) => { try {
      return Object.assign(window.__sweepMove(m), { slotted: m.slotted, owner: m.owner });
    } catch (e) { return { key: m.key, input: m.input, ok: false, why: 'harness error ' + String(e).slice(0, 160) + ' @ ' + String((e && e.stack) || '').split('\n').slice(1, 3).join(' | ').replace(/https?:\/\/[^/]+/g, '').slice(0, 200) }; } }), list.slice(i, i + CH));
    rows.push(...part);
  }
  const jug = [];
  for (const r of rows.filter((r) => r.ok && r.launch && !r.isThrow)) jug.push(await p.evaluate((r) => { try { return window.__juggle(r); } catch (e) { return { key: r.key, ok: false, why: String(e).slice(0, 100) }; } }, r));
  const sum = { fighter: id, body: { rosterId: body.rosterId, model: gotModel, how: body.how, file: body.file }, moves: rows.length, pass: rows.filter((r) => r.ok === true).length, fail: rows.filter((r) => r.ok === false).length, na: rows.filter((r) => r.ok == null).length,
    juggles: jug.filter((j) => j.ok != null).length, jugglePass: jug.filter((j) => j.ok === true).length, pageErrors: p.errs.slice(0, 5), secs: Math.round((Date.now() - t0) / 1000) };
  fs.writeFileSync(`${OUT}/${id}.json`, JSON.stringify({ ...sum, rows, juggle: jug }, null, 1));
  console.log(`== ${id}: ${sum.pass}/${sum.moves} pass, ${sum.fail} fail, ${sum.na} n/a, juggles ${sum.jugglePass}/${sum.juggles}, ${sum.secs}s`);
  await p.close();
}
await b.close();
