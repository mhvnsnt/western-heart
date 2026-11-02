// tools/input-verify/input_coverage_probe.mjs — does an animation actually START for every input
// in a fighter's move list? (owner 2026-11-01: moves "aren't working ... just random stuff is
// happening"; Claude's coverage probe, reworked 2026-11-01 to step game time directly.)
//
// Method (Claude's stepped design, replacing the wall-clock waits of
// tools/anim/move_coverage_probe.mjs):
//   * the game is paused (game.pause(true)) so the real rAF loop stops advancing the sim;
//   * the probe then steps game time itself: game._update(1/120) — the game's own fixed-step
//     update (game/js/game.js FIXED_DT = 1/120). Animation mixers advance inside
//     fighter.update, so stepping the update steps the animation: no wall-clock waits,
//     no frame-rate dependence, fully deterministic;
//   * before every input the input window is reset (TekkenBuffer drained, string grace
//     zeroed — it is wall-clock based, fighter.js _stringGraceUntil — queued follow-ups
//     cleared, both fighters restored to idle at fixed spacing);
//   * the input is fed exactly where the input layer feeds it: fighter.tryAttack(notation);
//   * the probe then steps until the move ends (or a step budget runs out), recording the
//     attack plan (clip name + kind), the mixer's running actions and effective weight, and
//     the share of major bones still at their bind rotation (the T-pose signature).
//
// Outcome per input: OK (an animation action ran), NOFIRE (tryAttack refused: the move
// cannot start from neutral), TPOSE (fired but nothing animated — bind pose shows),
// ERROR (exception). Strings fire their first step; the chain is input-buffer territory
// and is covered by test/input-determinism.test.mjs.
//
// usage: node tools/input-verify/input_coverage_probe.mjs <game-url> <out-dir> [fighter] [opponent]
//        [--max N] [--only-neutral] [--all] [--report-md path] [--model-fallback glb]
// Serve the repo first: python3 -m http.server 8765 (from the repo root), game-url is the
// game page URL, e.g. http://127.0.0.1:8765/game/index.html
import { createRequire } from 'module';
import fs from 'fs';

let chromium;
try { ({ chromium } = createRequire(import.meta.url)('playwright')); }
catch { ({ chromium } = await import(process.env.PLAYWRIGHT_MODULE || '/opt/node22/lib/node_modules/playwright/index.mjs')); }

const args = process.argv.slice(2);
const flags = {};
const positionals = [];
for (let i = 0; i < args.length; i++) {
  const a = args[i];
  if (a === '--all' || a === '--only-neutral') flags[a.slice(2)] = true;
  else if (a.startsWith('--')) flags[a.slice(2)] = args[++i];
  else positionals.push(a);
}
const max = +(flags.max || 0);
const reportMd = flags['report-md'] || null;
const modelFallback = flags['model-fallback'] || null;
const onlyNeutral = !!flags['only-neutral'] || !flags.all; // neutral list is the deliverable default
const [base, out, fid = 'pantera', opp = 'pantera'] = positionals;
if (!base || !out) { console.error('usage: node input_coverage_probe.mjs <game-url> <out-dir> [fighter] [opponent] [--max N] [--only-neutral|--all] [--report-md path] [--model-fallback glb]'); process.exit(2); }
fs.mkdirSync(out, { recursive: true });

const browser = await chromium.launch({
  executablePath: process.env.CHROMIUM_PATH || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
  args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--no-sandbox'],
});
const page = await browser.newPage({ viewport: { width: 640, height: 480 } });
if (process.env.NO_REMOTE) await page.route(/workers\.dev/, (r) => r.abort());
// Sparse-checkout / offline runs: other fighters' models are not on disk and
// the loader's remote retries stall the fight-load queue. --model-fallback
// <glb> serves that one GLB for every OTHER fighter's model request; the
// probed fighter's own model, banks and data always come from the real
// files, so the measurement is untouched — only the preload noise is cut.
if (modelFallback) {
  const body = fs.readFileSync(modelFallback);
  await page.route(/workers\.dev|cdn\.jsdelivr\.net/, (r) => r.abort());
  await page.route('**/roster/**', async (route) => {
    const url = route.request().url();
    if (url.includes(`/${fid}/`)) return route.continue();
    if (url.endsWith('.glb')) return route.fulfill({ status: 200, contentType: 'model/gltf-binary', body });
    return route.continue();
  });
  await page.route('**/game/assets/models/*.glb', async (route) => {
    const url = route.request().url();
    if (url.includes(fid)) return route.continue();
    return route.fulfill({ status: 200, contentType: 'model/gltf-binary', body });
  });
}
const logs = [];
page.on('console', (m) => { const t = m.text(); if (/error|warn|failed|unavailable/i.test(t)) logs.push(`[${m.type()}] ${t.slice(0, 200)}`); });
page.on('pageerror', (e) => logs.push(`[pageerror] ${e.message.slice(0, 200)}`));

console.log('loading', `${base}?quick=${fid},${opp},shrine`);
await page.goto(`${base}?quick=${fid},${opp},shrine`, { waitUntil: 'load', timeout: 180000 });
const t0 = Date.now();
let ready = false;
while (Date.now() - t0 < 420000) {
  ready = await page.evaluate(() => { const g = window.__game; return !!(g && g.p1 && g.p1.t3actions && Object.keys(g.p1.t3actions).length && g.roundState === 'fight'); }).catch(() => false);
  if (ready) break;
  await page.waitForTimeout(1000);
}
console.log('READY', ready);
if (!ready) {
  console.error('fight never became ready; see coverage.json logs');
  fs.writeFileSync(`${out}/coverage.json`, JSON.stringify({ fighter: fid, ready: false, logs }, null, 2));
  await browser.close();
  process.exit(3);
}

// Freeze the match around the probe: no AI, no KO, no round clock, no arena rendering
// (software GL is far too slow to draw every stepped frame; rendering is not simulation).
await page.evaluate(() => {
  const g = window.__game;
  g.ai = { update() {}, reset() {} };
  if (g.ai1) g.ai1 = { update() {}, reset() {} };
  g.p1.hp = g.p1.maxHp = 1e6; g.p2.hp = g.p2.maxHp = 1e6;
  g.roundTime = 0; g.timer = Infinity;
  if (g.arena) { g.arena.__render = g.arena.render.bind(g.arena); g.arena.render = () => {}; }
  g.pause(true); // the real loop stops advancing the sim; the probe steps _update itself
  window.__step = (n = 1) => { for (let i = 0; i < n; i++) g._update(1 / 120); };
});

const notations = await page.evaluate(async ({ fid, onlyNeutral }) => {
  const M = await import('./js/movesets.js');
  const ms = M.getFighterMoveset(fid);
  let keys = Object.keys((ms && ms.slots) || {});
  if (onlyNeutral) keys = keys.filter((k) => !/^[A-Za-z_][A-Za-z0-9_]*\./.test(k));
  return keys;
}, { fid, onlyNeutral });
const list = max ? notations.slice(0, max) : notations;
console.log('inputs', list.length, 'of', notations.length, onlyNeutral ? '(neutral list)' : '(full list)');

const rows = [];
for (const n of list) {
  const r = await page.evaluate(async (n) => {
    const g = window.__game, f = g.p1, foe = g.p2, step = window.__step;
    const T3 = await import('three');
    // ---- reset the input window + both fighters (Claude: "reset the input window before each input")
    try { g.input && g.input.consume && g.input.consume(); } catch (e) {}
    const t = f.tekken;
    if (t) { t.lastMove = null; t.lastMoveT = 0; t.lastDir = 'n'; t.hist && t.hist.fill('n'); t.dirEvents && (t.dirEvents.length = 0); t._dash = null; t._strPending = null; }
    f._queuedNext = null; f._queuedAfter = null; f._stepChain = null; f._stringGraceUntil = 0;
    f.stance = null; foe.stance = null;
    f.hp = f.maxHp; foe.hp = foe.maxHp; f.stun = 0; foe.stun = 0;
    f._enter('idle'); foe._enter('idle');
    foe.root.position.set(f.root.position.x + (f.facing || 1) * 1.1, foe.root.position.y, 0);
    // ---- settle: step game time until the fighter can act from neutral (bounded)
    let settle = 0;
    while (settle < 720 && !(f.canAct && f.canAct() && f.state === 'idle')) { step(1); settle++; }
    if (!(f.canAct && f.canAct())) return { n, ok: false, error: 'never settled to idle/canAct after ' + settle + ' steps, state=' + f.state };
    // ---- feed the input where the input layer feeds it
    const oldPlanId = f._atkPlan && f._atkPlan.id;
    let ok = false;
    try { ok = f.tryAttack(n); } catch (e) { return { n, ok: false, error: String(e.message || e).slice(0, 160) }; }
    if (!ok) return { n, ok: false, state: f.state, stance: f.stance || null };
    // ---- step the move: watch the plan, the mixer and the pose
    let plan = null, maxWeight = 0, sawRunning = false, sawAttack = false, bindFrac = null, steps = 0, midDone = false, firstAttack = null;
    // Share of major bones still at their BIND rotation (the T-pose signature) — same
    // measurement as tools/anim/move_coverage_probe.mjs: bind local rotation comes from
    // the skeleton's boneInverses (parent bind world^-1 x own bind world).
    const bindCheck = () => {
      let sk = null;
      f.model && f.model.traverse((o) => { if (!sk && o.isSkinnedMesh && o.skeleton) sk = o.skeleton; });
      if (!sk) return null;
      const bindW = sk.boneInverses.map((m) => m.clone().invert());
      const idx = new Map(sk.bones.map((b, i) => [b, i]));
      let at = 0, cnt = 0;
      sk.bones.forEach((b, i) => {
        if (!/(Spine\d?|Neck|Head|Arm|ForeArm|UpLeg|Leg)$/.test(b.name.split(':').pop())) return;
        const pi = idx.get(b.parent);
        const L = pi !== undefined ? bindW[pi].clone().invert().multiply(bindW[i]) : bindW[i];
        const q = new T3.Quaternion(); L.decompose(new T3.Vector3(), q, new T3.Vector3());
        cnt++; if (2 * Math.acos(Math.min(1, Math.abs(q.dot(b.quaternion)))) < 0.02) at++;
      });
      return cnt ? +(at / cnt).toFixed(2) : null;
    };
    while (steps < 480) {
      step(1); steps++;
      if (f.state === 'attack' || f.attack) sawAttack = true;
      if (!plan && f._atkPlan && f._atkPlan.id !== oldPlanId) {
        const p = f._atkPlan;
        plan = { name: p.name || null, kind: p.kind || null, why: (p.why || '').slice(0, 80) };
      }
      if (!firstAttack && f.attack) firstAttack = { moveKey: f.attack.moveKey || null, moveName: f.attack.moveName || null };
      let w = 0, running = 0;
      for (const a of (f.mixer && f.mixer._actions) || []) {
        const ew = a.enabled ? a.getEffectiveWeight() : 0;
        if (ew > 0.001) w += ew;
        if (a.isRunning()) running++;
      }
      if (w > maxWeight) maxWeight = w;
      if (running > 0) sawRunning = true;
      if (!midDone && plan && steps >= 36) { bindFrac = bindCheck(); midDone = true; }
      if (steps > 24 && f.state === 'idle' && !f.attack) break; // move finished
    }
    if (bindFrac === null) bindFrac = bindCheck();
    return { n, ok: true, state: f.state, moveKey: firstAttack && firstAttack.moveKey, moveName: firstAttack && firstAttack.moveName,
             plan: plan && plan.name, kind: plan && plan.kind, why: plan && plan.why,
             maxWeight: +maxWeight.toFixed(2), sawRunning, sawAttack, bindFrac, steps };
  }, n).catch((e) => ({ n, ok: false, error: String(e.message || e).slice(0, 160) }));
  r.outcome = !r.ok ? (r.error ? 'ERROR' : 'NOFIRE')
    : ((r.maxWeight < 0.2 && !r.sawRunning) || (r.bindFrac != null && r.bindFrac >= 0.7) ? 'TPOSE' : 'OK');
  rows.push(r);
  console.log(r.outcome.padEnd(7), n.padEnd(24), r.plan || '', r.kind || '', r.error || '');
}

// ---- chain pass: a string continuation only animates when the string is
// actually chained, the way a player inputs it. Every TPOSE row whose
// notation is a chain (contains a comma) is replayed as a chain — feed each
// prefix in turn, stepping game time between feeds — and the final step is
// measured exactly like the main pass. CHAIN-OK = alive in real play; a row
// that stays TPOSE even chained is dead for real.
for (const r of rows.filter((x) => x.outcome === 'TPOSE' && /,/.test(x.n))) {
  const cr = await page.evaluate(async (n) => {
    const g = window.__game, f = g.p1, foe = g.p2, step = window.__step;
    const T3 = await import('three');
    try { g.input && g.input.consume && g.input.consume(); } catch (e) {}
    const t = f.tekken;
    if (t) { t.lastMove = null; t.lastMoveT = 0; t.lastDir = 'n'; t.hist && t.hist.fill('n'); t.dirEvents && (t.dirEvents.length = 0); t._dash = null; t._strPending = null; }
    f._queuedNext = null; f._queuedAfter = null; f._stepChain = null; f._stringGraceUntil = 0;
    f.stance = null; foe.stance = null;
    f.hp = f.maxHp; foe.hp = foe.maxHp; f.stun = 0; foe.stun = 0;
    f._enter('idle'); foe._enter('idle');
    foe.root.position.set(f.root.position.x + (f.facing || 1) * 1.1, foe.root.position.y, 0);
    let settle = 0;
    while (settle < 720 && !(f.canAct && f.canAct() && f.state === 'idle')) { step(1); settle++; }
    if (!(f.canAct && f.canAct())) return { n, ok: false, error: 'never settled (chain)' };
    const parts = n.split(',');
    const prefixes = parts.map((_, i) => parts.slice(0, i + 1).join(','));
    for (let i = 0; i < prefixes.length - 1; i++) {
      try { f.tryAttack(prefixes[i]); } catch (e) {}
      for (let s = 0; s < 40; s++) step(1);
    }
    const oldPlanId = f._atkPlan && f._atkPlan.id;
    let ok = false;
    try { ok = f.tryAttack(n); } catch (e) { return { n, ok: false, error: String(e.message || e).slice(0, 160) }; }
    if (!ok) return { n, ok: false, state: f.state, stance: f.stance || null };
    let plan = null, maxWeight = 0, sawRunning = false, sawAttack = false, bindFrac = null, steps = 0, midDone = false, firstAttack = null;
    const bindCheck = () => {
      let sk = null;
      f.model && f.model.traverse((o) => { if (!sk && o.isSkinnedMesh && o.skeleton) sk = o.skeleton; });
      if (!sk) return null;
      const bindW = sk.boneInverses.map((m) => m.clone().invert());
      const idx = new Map(sk.bones.map((b, i) => [b, i]));
      let at = 0, cnt = 0;
      sk.bones.forEach((b, i) => {
        if (!/(Spine\d?|Neck|Head|Arm|ForeArm|UpLeg|Leg)$/.test(b.name.split(':').pop())) return;
        const pi = idx.get(b.parent);
        const L = pi !== undefined ? bindW[pi].clone().invert().multiply(bindW[i]) : bindW[i];
        const q = new T3.Quaternion(); L.decompose(new T3.Vector3(), q, new T3.Vector3());
        cnt++; if (2 * Math.acos(Math.min(1, Math.abs(q.dot(b.quaternion)))) < 0.02) at++;
      });
      return cnt ? +(at / cnt).toFixed(2) : null;
    };
    while (steps < 480) {
      step(1); steps++;
      if (f.state === 'attack' || f.attack) sawAttack = true;
      if (!plan && f._atkPlan && f._atkPlan.id !== oldPlanId) {
        const p = f._atkPlan;
        plan = { name: p.name || null, kind: p.kind || null, why: (p.why || '').slice(0, 80) };
      }
      if (!firstAttack && f.attack) firstAttack = { moveKey: f.attack.moveKey || null, moveName: f.attack.moveName || null };
      let w = 0, running = 0;
      for (const a of (f.mixer && f.mixer._actions) || []) {
        const ew = a.enabled ? a.getEffectiveWeight() : 0;
        if (ew > 0.001) w += ew;
        if (a.isRunning()) running++;
      }
      if (w > maxWeight) maxWeight = w;
      if (running > 0) sawRunning = true;
      if (!midDone && plan && steps >= 36) { bindFrac = bindCheck(); midDone = true; }
      if (steps > 24 && f.state === 'idle' && !f.attack) break;
    }
    if (bindFrac === null) bindFrac = bindCheck();
    return { n, ok: true, state: f.state, moveKey: firstAttack && firstAttack.moveKey, moveName: firstAttack && firstAttack.moveName,
             plan: plan && plan.name, kind: plan && plan.kind, why: plan && plan.why,
             maxWeight: +maxWeight.toFixed(2), sawRunning, sawAttack, bindFrac, steps };
  }, r.n).catch((e) => ({ n: r.n, ok: false, error: String(e.message || e).slice(0, 160) }));
  cr.outcome = !cr.ok ? (cr.error ? 'ERROR' : 'NOFIRE')
    : ((cr.maxWeight < 0.2 && !cr.sawRunning) || (cr.bindFrac != null && cr.bindFrac >= 0.7) ? 'TPOSE' : 'OK');
  r.chain = cr;
  if (cr.outcome === 'OK') r.outcome = 'CHAIN-OK';
  console.log('CHAIN'.padEnd(7), cr.outcome.padEnd(7), r.n.padEnd(24), cr.plan || '', cr.error || '');
}

const tally = {};
for (const r of rows) tally[r.outcome] = (tally[r.outcome] || 0) + 1;
const kinds = {};
for (const r of rows.filter((x) => x.ok)) kinds[r.kind || 'none'] = (kinds[r.kind || 'none'] || 0) + 1;
const summary = { fighter: fid, opponent: opp, inputs: rows.length, neutralOnly: onlyNeutral, tally, kinds };
fs.writeFileSync(`${out}/coverage.json`, JSON.stringify({ ...summary, rows, logs }, null, 1));

const esc = (s) => String(s == null ? '' : s).replace(/\|/g, '/');
const table = (rs) => ['| input | fired | animation / clip | kind | outcome | notes |', '|---|---|---|---|---|---|',
  ...rs.map((r) => `| \`${esc(r.n)}\` | ${r.ok ? 'yes' : 'no'} | ${esc(r.plan || '')} | ${esc(r.kind || '')} | ${r.outcome} | ${esc(r.why || r.error || (r.moveName ? r.moveName : ''))}${r.chain ? ` — chained replay: ${r.chain.outcome}${r.chain.plan ? ` (${esc(r.chain.plan)})` : ''}` : ''} |`)].join('\n');
const md = [
  `# Input coverage (stepped probe): ${fid} — ${rows.length} ${onlyNeutral ? 'neutral ' : ''}inputs`, '',
  `Tool: \`tools/input-verify/input_coverage_probe.mjs\` (game time stepped directly, FIXED_DT 1/120; no wall-clock waits).`, '',
  `**Tally: ${Object.entries(tally).map(([k, v]) => `${k} ${v}`).join(', ')}**; plan kinds: ${Object.entries(kinds).map(([k, v]) => `${k} ${v}`).join(', ')}`, '',
  'Outcomes: OK = fired and an animation played from neutral. TPOSE = fired but the body stayed in bind pose (no animation). CHAIN-OK = a string continuation that stays in bind pose when fed cold from neutral but animates when the string is chained the way a player inputs it (chain pass: prefixes fed in turn, game time stepped between them). NOFIRE = the input layer rejected it. ERROR = probe-side failure.', '',
  '## Non-OK inputs', '',
  table(rows.filter((r) => r.outcome !== 'OK')), '',
  '## All inputs', '',
  table(rows), '',
].join('\n');
fs.writeFileSync(`${out}/coverage.md`, md + '\n');
if (reportMd) { fs.mkdirSync(reportMd.replace(/\/[^/]*$/, ''), { recursive: true }); fs.writeFileSync(reportMd, md + '\n'); }
console.log('TALLY', JSON.stringify(tally), 'KINDS', JSON.stringify(kinds));
await browser.close();
