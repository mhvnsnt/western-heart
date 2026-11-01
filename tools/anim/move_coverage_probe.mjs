// tools/anim/move_coverage_probe.mjs — press EVERY input in a fighter's move list in the real game and record what
// animation plays (owner 2026-11-01: "Pantera ... his animations are falling back to T pose ... it feels really empty
// ... 100% of their move list and animation playing in the fight including all attacks, grapples").
//
// For each notation in the fighter's slot table (game/assets/movesets/<id>.json "slots"), from idle (string grace
// waited out), it calls fighter.tryAttack(notation) like the input layer, then samples mid-move:
//   plan   fighter._atkPlan {name, kind}: t7 (real T7 clip), notation / own / anim (bank row), donor, match, generic,
//          step-plan;
//   weight the summed effective weight of the animation actions running on the fighter's mixer. A skinned model with
//          no running action (weight ~0) is drawn in its bind pose: the T-POSE the owner sees.
// Outcome per input: OK (animated), TPOSE (fired, nothing animating), NOFIRE (tryAttack false: needs a stance /
// state / opponent situation, or no move), and the plan kind. JSON + Markdown report.
//
// usage: NO_REMOTE=1 node tools/anim/move_coverage_probe.mjs <game-url> <out-dir> <fighter> [opponent] [--max N] [--only-neutral]
import { createRequire } from 'module';
import fs from 'fs';
const { chromium } = createRequire(import.meta.url)('playwright');
const args = process.argv.slice(2);
const flag = (k) => { const i = args.indexOf(k); if (i < 0) return null; const v = args[i + 1]; args.splice(i, 2); return v; };
const bool = (k) => { const i = args.indexOf(k); if (i < 0) return false; args.splice(i, 1); return true; };
const max = +(flag('--max') || 0), onlyNeutral = bool('--only-neutral');
const [base, out, fid, opp = 'pantera'] = args;
if (!fid) { console.error('usage: node move_coverage_probe.mjs <game-url> <out-dir> <fighter> [opponent] [--max N] [--only-neutral]'); process.exit(2); }
fs.mkdirSync(out, { recursive: true });
const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: 640, height: 480 } });
if (process.env.NO_REMOTE) await page.route(/workers\.dev/, (r) => r.abort());
const logs = [];
page.on('console', (m) => { const t = m.text(); if (/WH-T7|pageerror|Error|T-?pose|unavailable|failed/i.test(t)) logs.push(`[${m.type()}] ${t.slice(0, 240)}`); });
page.on('pageerror', (e) => logs.push(`[pageerror] ${e.message.slice(0, 240)}`));
await page.goto(`${base}?quick=${fid},${opp},shrine`, { waitUntil: 'load', timeout: 180000 });
const t0 = Date.now();
let ready = false;
while (Date.now() - t0 < 420000) {
  ready = await page.evaluate(() => { const g = window.__game; return !!(g && g.p1 && g.p1.t3actions && Object.keys(g.p1.t3actions).length && g.roundState === 'fight'); }).catch(() => false);
  if (ready) break;
  await page.waitForTimeout(1000);
}
console.log('READY', ready);
// no AI, no KO and NO ROUND CLOCK (game.js counts g.timer down from rules.roundTime = 60 s and times the round out;
// after that nothing can act, which read as every later input "NOFIRE")
await page.evaluate(() => { const g = window.__game; g.ai = { update() {}, reset() {} }; g.p1.hp = g.p1.maxHp = 1e6; g.p2.hp = g.p2.maxHp = 1e6; g.roundTime = 0; g.timer = Infinity; });
const notations = await page.evaluate(async ({ fid, onlyNeutral }) => {
  const M = await import('./js/movesets.js');
  const ms = M.getFighterMoveset(fid);
  let keys = Object.keys((ms && ms.slots) || {});
  if (onlyNeutral) keys = keys.filter((k) => !/^[A-Za-z_][A-Za-z0-9_]*\./.test(k));
  return keys;
}, { fid, onlyNeutral });
const list = max ? notations.slice(0, max) : notations;
console.log('inputs', list.length, 'of', notations.length);
const rows = [];
for (const n of list) {
  const r = await page.evaluate(async (n) => {
    const g = window.__game, f = g.p1;
    g.timer = Infinity; f.hp = f.maxHp; g.p2.hp = g.p2.maxHp;
    if (g.roundState !== 'fight') return { n, ok: false, error: 'round not in fight: ' + g.roundState };
    const until = async (c, ms) => { const e = Date.now() + ms; while (!c() && Date.now() < e) await new Promise((r) => setTimeout(r, 15)); };
    await until(() => (typeof f.canAct === 'function' ? f.canAct() : f.state === 'idle'), 12000);
    await until(() => performance.now() > (f._stringGraceUntil || 0) + 40, 2000);
    f.root.position.x = g.p2.root.position.x - (f.facing || 1) * 1.1;  // keep a fixed spacing (throws need range)
    const oldId = f._atkPlan && f._atkPlan.id;
    let ok = false;
    try { ok = f.tryAttack(n); } catch (e) { return { n, ok: false, error: String(e.message || e).slice(0, 160) }; }
    if (!ok) return { n, ok: false, state: f.state, round: g.roundState, canAct: typeof f.canAct === 'function' ? f.canAct() : null };
    await until(() => f._atkPlan && f._atkPlan.id !== oldId, 4000);
    const p = f._atkPlan || {};
    const tm = p.timing || {};
    const act = p.name && f.t3actions && f.t3actions[p.name];
    const tMid = Number.isFinite(tm.t0) ? tm.t0 : 0.15;
    if (act) await until(() => act.time >= tMid || f.state === 'idle', 5000);
    else await new Promise((r) => setTimeout(r, 250));
    // every ENABLED action with weight poses the body (a finished, clamped one-shot is paused, not running, but still
    // holds its pose); none at all = the skinned model shows its bind pose (T-pose)
    let weight = 0, running = 0;
    for (const a of (f.mixer && f.mixer._actions) || []) {
      const w = a.enabled ? a.getEffectiveWeight() : 0;
      if (w > 0.001) weight += w;
      if (a.isRunning()) running++;
    }
    // direct pose check: share of the major bones whose local rotation is still the BIND rotation (the T-pose). Real
    // animation moves nearly all of them; an action whose tracks do not bind to this model's bones leaves them at bind
    // even at full weight.
    let bindFrac = null;
    try {
      const T3 = await import('three');
      let sk = null;
      f.model.traverse((o) => { if (!sk && o.isSkinnedMesh && o.skeleton) sk = o.skeleton; });
      if (sk) {
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
        bindFrac = cnt ? +(at / cnt).toFixed(2) : null;
      }
    } catch (e) { bindFrac = null; }
    return { n, ok: true, state: f.state, moveKey: f.attack && f.attack.moveKey, plan: p.name || null, kind: p.kind || null, bindFrac,
             why: (p.why || '').slice(0, 80), hasAction: !!act, running, weight: +weight.toFixed(2),
             act: act ? { enabled: act.enabled, w: +act.getEffectiveWeight().toFixed(2), t: +act.time.toFixed(3), d: +act.getClip().duration.toFixed(3), paused: act.paused } : null };
  }, n).catch((e) => ({ n, ok: false, error: String(e.message || e).slice(0, 160) }));
  r.outcome = !r.ok ? (r.error ? 'ERROR' : 'NOFIRE') : (r.weight < 0.2 || (r.bindFrac != null && r.bindFrac >= 0.7) ? 'TPOSE' : 'OK');
  rows.push(r);
  if (r.outcome !== 'OK') console.log(r.outcome.padEnd(7), n.padEnd(24), r.plan || '', r.kind || '', r.error || '');
}
const tally = {};
for (const r of rows) tally[r.outcome] = (tally[r.outcome] || 0) + 1;
const kinds = {};
for (const r of rows.filter((x) => x.ok)) kinds[r.kind || 'none'] = (kinds[r.kind || 'none'] || 0) + 1;
fs.writeFileSync(`${out}/coverage.json`, JSON.stringify({ fighter: fid, inputs: rows.length, tally, kinds, rows, logs }, null, 1));
const md = [`# Move coverage: ${fid} (${rows.length} inputs, \`tools/anim/move_coverage_probe.mjs\`)`, '',
  `**${Object.entries(tally).map(([k, v]) => `${k} ${v}`).join(', ')}**; plans: ${Object.entries(kinds).map(([k, v]) => `${k} ${v}`).join(', ')}`, '',
  '| input | outcome | plan | kind | why |', '|---|---|---|---|---|',
  ...rows.filter((r) => r.outcome !== 'OK').map((r) => `| \`${r.n}\` | ${r.outcome} | ${r.plan || ''} | ${r.kind || ''} | ${(r.why || r.error || '').replace(/\|/g, '/')} |`)].join('\n');
fs.writeFileSync(`${out}/coverage.md`, md + '\n');
console.log('TALLY', JSON.stringify(tally), 'KINDS', JSON.stringify(kinds));
await browser.close();
