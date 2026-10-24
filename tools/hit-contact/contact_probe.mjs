// HIT CONTACT PROBE (lane C, 2026-10-24) — measures how CPU-vs-CPU attacks resolve.
//
//   node tools/proof-harness/../hit-contact/contact_probe.mjs OUTDIR P1 P2 [seconds=60] [query=demo=1]
//
// Serves from the repo static server (PORT, default 8765). Starts a demo (both CPU) arcade fight,
// then drives the fixed-step sim directly (Game._update(1/120), rendering paused) so a minute of
// fight time runs in seconds. HP and the round timer are topped up so the round never ends.
// For every attack (fighter + _attackId) it records:
//   reachedActive   the move entered its active frames
//   outcome         what receiveHit/startThrowLock returned (hit, counter, block, ko, armor, dodge, throw)
//                   or 'whiff' when the active frames passed without contact
//   dx, dz          root distance along / across the fight axis at the first active tick
//   gapActive       closest approach (m) of the striking limb (forearm+fist or shin+foot capsule)
//                   to the defender's body capsules DURING the active frames (<= 0 = touching)
//   gapAny          the same over the whole move (startup..recovery)
// The geometry here is the probe's own (bone pairs + radii scaled to the rig), independent of
// fighter.js, so the same numbers compare the old sphere test with any new one.
// Writes OUTDIR/attacks.json and OUTDIR/summary.json, prints the summary.
const { chromium } = await import(process.env.PLAYWRIGHT_MODULE || '/opt/node22/lib/node_modules/playwright/index.mjs');
import fs from 'fs';
const [,, out = 'probe', p1 = 'pantera', p2 = 'skull', secs = '60', q = 'demo=1'] = process.argv;
fs.mkdirSync(out, { recursive: true });
const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
  args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: 480, height: 270 } });
const logs = [];
page.on('console', m => { if (m.type() === 'error' || /hitcontact|HITC/.test(m.text())) logs.push(`[${m.type()}] ${m.text()}`); });
page.on('pageerror', e => logs.push(`[pageerror] ${e.message}`));
await page.goto(`http://127.0.0.1:${process.env.PORT || 8765}/game/index.html?${q}`, { waitUntil: 'load' });
await page.waitForFunction(() => window.__modes, null, { timeout: 60000 });
await page.evaluate(() => window.__modes.startMode('arcade'));
await page.waitForTimeout(300);
await page.evaluate(async ([a, b]) => { await window.__modes.startFight(a, b, { mode: 'arcade' }); }, [p1, p2])
  .catch(e => logs.push('startFight err ' + e.message));
await page.waitForFunction(() => window.__game && window.__game.roundState === 'fight', null, { timeout: 120000 });

await page.evaluate(async () => {
  const T3 = await import('/game/js/t3anims.js');
  const g = window.__game;
  const P = window.__hitProbe = { attacks: {}, ticks: 0 };
  const V3 = g.p1.root.position.constructor;
  const tmp = () => new V3();
  // canonical bone dict per fighter (probe-side; independent of assets.js aliases)
  const canon = (f) => {
    if (f.__probeCanon && f.__probeCanonModel === f.model) return f.__probeCanon;
    const by = {};
    f.model.traverse((o) => { if (!o.isBone) return; const c = T3.canonBoneName(o.name) || ({ root_hips: 'Hips', pelvis: 'Hips', spine_lower: 'Spine', spine_upper: 'Spine2', head: 'Head', head_neck_lower: 'Neck' })[o.name]
      || (o.name.match(/^(arm|leg)_(left|right)_(shoulder_2|elbow|wrist|thigh|knee|ankle|toes)$/) ? (({ left: 'Left', right: 'Right' })[RegExp.$2] + ({ shoulder_2: 'Arm', elbow: 'ForeArm', wrist: 'Hand', thigh: 'UpLeg', knee: 'Leg', ankle: 'Foot', toes: 'ToeBase' })[RegExp.$3]) : null);
      if (c && !by[c]) by[c] = o; });
    if (!by.Spine1) by.Spine1 = by.Spine2 || by.Chest || by.Spine;
    if (!by.Spine2) by.Spine2 = by.Chest || by.Spine1;
    if (!by.Head) by.Head = by.Neck;
    f.__probeCanon = by; f.__probeCanonModel = f.model; return by;
  };
  const wp = (b) => { const v = tmp(); b.getWorldPosition(v); return v; };
  // anatomical side: character left = up x forward; forward = facing * +X  -> left = -Z * facing
  const sideSwap = (f, by) => {
    if (!by.LeftArm || !by.RightArm) return false;
    const l = wp(by.LeftArm), r = wp(by.RightArm);
    return ((l.z - r.z) * -f.facing) < 0;
  };
  const segDist = (p1, q1, p2, q2) => { // closest distance between segments p1q1 and p2q2
    const d1 = tmp().subVectors(q1, p1), d2 = tmp().subVectors(q2, p2), r = tmp().subVectors(p1, p2);
    const a = d1.dot(d1), e = d2.dot(d2), f = d2.dot(r);
    let s, t;
    if (a <= 1e-9 && e <= 1e-9) return p1.distanceTo(p2);
    if (a <= 1e-9) { s = 0; t = Math.min(1, Math.max(0, f / e)); }
    else {
      const c = d1.dot(r);
      if (e <= 1e-9) { t = 0; s = Math.min(1, Math.max(0, -c / a)); }
      else {
        const b = d1.dot(d2), den = a * e - b * b;
        s = den !== 0 ? Math.min(1, Math.max(0, (b * f - c * e) / den)) : 0;
        t = (b * s + f) / e;
        if (t < 0) { t = 0; s = Math.min(1, Math.max(0, -c / a)); }
        else if (t > 1) { t = 1; s = Math.min(1, Math.max(0, (b - c) / a)); }
      }
    }
    const c1 = tmp().copy(p1).addScaledVector(d1, s), c2 = tmp().copy(p2).addScaledVector(d2, t);
    return c1.distanceTo(c2);
  };
  const scaleOf = (by) => { const h = by.Hips && by.Head ? wp(by.Hips).distanceTo(wp(by.Head)) : 0.6; return Math.max(0.5, Math.min(2.5, h / 0.62)); };
  const body = (f) => { // defender capsules [a, b, r]
    const by = canon(f), s = scaleOf(by), out = [];
    const cap = (a, b, r) => { if (by[a] && by[b]) out.push([wp(by[a]), wp(by[b]), r * s]); };
    if (by.Head) { const h = wp(by.Head), n = by.Neck ? wp(by.Neck) : h; const top = tmp().subVectors(h, n).setLength(0.1 * s).add(h); out.push([h, top, 0.11 * s]); }
    cap('Spine2', 'Neck', 0.16); cap('Hips', 'Spine2', 0.15);
    for (const S of ['Left', 'Right']) { cap(S + 'UpLeg', S + 'Leg', 0.085); cap(S + 'Leg', S + 'Foot', 0.06); }
    return out;
  };
  const limbsOf = (f) => {
    const n = String(f.attackName || ''), L = f.attack && f.attack.limb;
    const last = (n.split('~')[0].split(',').filter(x => /[1-4]/.test(x)).pop() || '').replace(/^.*\./, '');
    const btn = (last.match(/[1-4]/g) || []);
    const conv = { 1: 'armL', 2: 'armR', 3: 'legL', 4: 'legR' };
    const c = new Set();
    if (L === 'both') { if (btn.some(b => b < 3) || !btn.length) { c.add('armL'); c.add('armR'); } if (btn.some(b => b > 2)) { c.add('legL'); c.add('legR'); } }
    else if (/^(arm|leg)[LR]$/.test(L || '')) c.add(L);
    for (const b of btn) c.add(conv[b]);
    if (!c.size) c.add(n === 'kick' ? 'legR' : 'armR');
    return [...c];
  };
  const limbSegs = (f) => {
    const by = canon(f), s = scaleOf(by), sw = sideSwap(f, by), out = [];
    for (const l of limbsOf(f)) {
      let S = l.endsWith('L') ? 'Left' : 'Right'; if (sw) S = S === 'Left' ? 'Right' : 'Left';
      if (l.startsWith('arm') && by[S + 'ForeArm'] && by[S + 'Hand']) {
        const a = wp(by[S + 'ForeArm']), b = wp(by[S + 'Hand']); const tip = tmp().subVectors(b, a).multiplyScalar(0.35).add(b);
        out.push([a, tip, 0.06 * s]);
      } else if (l.startsWith('leg') && by[S + 'Leg'] && by[S + 'Foot']) {
        const a = wp(by[S + 'Leg']), b = wp(by[S + 'Foot']); const toe = by[S + 'ToeBase'] ? wp(by[S + 'ToeBase']) : b;
        out.push([a, b, 0.06 * s]); out.push([b, toe, 0.05 * s]);
      }
    }
    return out;
  };
  const gap = (atk, def) => {
    let best = Infinity; const B = body(def);
    for (const [a, b, r] of limbSegs(atk)) for (const [c, d, r2] of B) best = Math.min(best, segDist(a, b, c, d) - r - r2);
    return best;
  };
  const ATK = new Set(['attack', 'vskill', 'vreversal']);
  const recOf = (f) => {
    const k = (f === g.p1 ? 'p1' : 'p2') + ':' + f._attackId;
    return P.attacks[k] || (P.attacks[k] = { who: f === g.p1 ? 'p1' : 'p2', name: f.attackName, limb: f.attack && f.attack.limb,
      hitWord: f.attack && f.attack.hitWord, activeS: f.attack && f.attack.active, reachedActive: false, outcome: null, gapActive: null, gapAny: null });
  };
  const wrap = (f) => {
    if (f.__probeWrapped) return; f.__probeWrapped = true;
    const rh = f.receiveHit;
    f.receiveHit = function (move, attacker) { const r = rh.call(this, move, attacker); try { const rec = recOf(attacker); if (!rec.outcome || rec.outcome === 'dodge') rec.outcome = r; } catch (e) {} return r; };
    const st = f.startThrowLock;
    if (st) f.startThrowLock = function (move, attacker) { try { recOf(attacker).outcome = 'throw'; } catch (e) {} return st.apply(this, arguments); };
  };
  P.step = (n) => {
    for (let i = 0; i < n; i++) {
      if (g.roundState !== 'fight') return 'not-fight';
      wrap(g.p1); wrap(g.p2);
      g._update(1 / 120); P.ticks++;
      for (const [a, d] of [[g.p1, g.p2], [g.p2, g.p1]]) {
        if (!ATK.has(a.state) || !a.attack) continue;
        const rec = recOf(a);
        let gp = null; try { gp = gap(a, d); } catch (e) { gp = null; }
        if (gp != null) rec.gapAny = rec.gapAny == null ? gp : Math.min(rec.gapAny, gp);
        if (a._attackPhase === 'active') {
          if (!rec.reachedActive) { rec.reachedActive = true; rec.dx = +Math.abs(a.root.position.x - d.root.position.x).toFixed(3); rec.dz = +Math.abs(a.root.position.z - d.root.position.z).toFixed(3); rec.defState = d.state; }
          if (gp != null) rec.gapActive = rec.gapActive == null ? gp : Math.min(rec.gapActive, gp);
        }
      }
      for (const f of [g.p1, g.p2]) { if (f.hp < 40 && !f.dead) f.hp = f.maxHp; }
      g.timer = 60;
    }
    return 'ok';
  };
  P.minPush = () => Math.abs(g.p1.root.position.x - g.p2.root.position.x);
});

const ticks = Math.round(+secs * 120);
let done = 0, guard = 0;
while (done < ticks && guard++ < 4000) {
  const r = await page.evaluate((n) => { const g = window.__game; g.paused = true; const s = window.__hitProbe.step(n); g.paused = false; return [s, window.__hitProbe.ticks]; }, 240);
  done = r[1];
  if (r[0] !== 'ok') await page.waitForTimeout(400);
}
const attacks = await page.evaluate(() => Object.values(window.__hitProbe.attacks));
const act = attacks.filter(a => a.reachedActive);
const cnt = (arr, f) => arr.filter(f).length;
const landed = (a) => ['hit', 'counter', 'ko', 'throw', 'armor'].includes(a.outcome);
const blocked = (a) => a.outcome === 'block';
const touchA = act.filter(a => a.gapActive != null && a.gapActive <= 0);
const near = act.filter(a => a.dx != null && a.dx < 1.6);
const summary = {
  pair: `${p1} vs ${p2}`, seconds: done / 120, attacks: attacks.length, reachedActive: act.length,
  landed: cnt(act, landed), blocked: cnt(act, blocked), dodged: cnt(act, a => a.outcome === 'dodge'), whiffed: cnt(act, a => !a.outcome),
  // geometric truth from the probe's own capsules
  touchingDuringActive: touchA.length,
  touchingDuringActive_registered: cnt(touchA, a => landed(a) || blocked(a) || a.outcome === 'dodge'),
  notTouching_registered: cnt(act.filter(a => !(a.gapActive != null && a.gapActive <= 0)), a => landed(a) || blocked(a)),
  touchingAnyTime: cnt(act, a => a.gapAny != null && a.gapAny <= 0),
  within1_6m: near.length, within1_6m_landedOrBlocked: cnt(near, a => landed(a) || blocked(a)),
  medianDxAtActive: (() => { const d = act.map(a => a.dx).filter(x => x != null).sort((x, y) => x - y); return d.length ? d[d.length >> 1] : null; })(),
  medianDzAtActive: (() => { const d = act.map(a => a.dz).filter(x => x != null).sort((x, y) => x - y); return d.length ? d[d.length >> 1] : null; })(),
  minDx: Math.min(...act.map(a => a.dx).filter(x => x != null)),
  pageErrors: logs.filter(l => l.startsWith('[pageerror]')).length,
};
fs.writeFileSync(`${out}/attacks.json`, JSON.stringify(attacks, null, 1));
fs.writeFileSync(`${out}/summary.json`, JSON.stringify(summary, null, 1));
fs.writeFileSync(`${out}/console.log`, logs.join('\n'));
console.log(JSON.stringify(summary));
await browser.close();
