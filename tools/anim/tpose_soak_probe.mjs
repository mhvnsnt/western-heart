// tools/anim/tpose_soak_probe.mjs — T-POSE SOAK TEST: two CPU fighters fight for minutes in the real game while every
// sample checks both bodies for the bind pose (owner 2026-11-01: "Pantera ... his animations are falling back to T
// pose ... need to get solved for all the characters in the game ... including all attacks grapples and animations").
//
// A per-move probe only sees the moves it presses from idle. The owner sees T-poses in the fight itself: strings,
// throws and their reactions, stances, knockdowns, wake-ups, getting hit. Here both sides are driven by the game's own
// AIController (aggressive, throw-happy), with infinite health and no round clock, and every ~150 ms both fighters are
// sampled:
//   bindFrac  share of the major bones (spine, neck, head, arms, legs) whose local rotation is still the skeleton's
//             BIND rotation (within ~1 degree). Real animation moves nearly all of them; >= 0.7 = the model shows its
//             bind pose: the T-pose (or A-pose) the owner sees.
// Every T-pose sample is logged with what the fighter was doing (state, move, attack plan kind/name, the top mixer
// actions and their weights) and grouped into incidents; the first sample of each new incident is screenshotted.
//
// usage: NO_REMOTE=1 node tools/anim/tpose_soak_probe.mjs <game-url> <out-dir> <fighter> [opponent] [--seconds 240]
import { createRequire } from 'module';
import fs from 'fs';
const { chromium } = createRequire(import.meta.url)('playwright');
const args = process.argv.slice(2);
const flag = (k, d) => { const i = args.indexOf(k); if (i < 0) return d; const v = args[i + 1]; args.splice(i, 2); return v; };
const seconds = +flag('--seconds', '240');
const [base, out, fid, opp = 'negativo'] = args;
if (!fid) { console.error('usage: node tpose_soak_probe.mjs <game-url> <out-dir> <fighter> [opponent] [--seconds N]'); process.exit(2); }
fs.mkdirSync(out, { recursive: true });
const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: 640, height: 480 } });
if (process.env.NO_REMOTE) await page.route(/workers\.dev/, (r) => r.abort());
const logs = [];
page.on('console', (m) => { const t = m.text(); if (/T-?pose|unbound|no clip|missing|failed|Error/i.test(t)) logs.push(`[${m.type()}] ${t.slice(0, 220)}`); });
page.on('pageerror', (e) => logs.push(`[pageerror] ${e.message.slice(0, 220)}`));
await page.goto(`${base}?quick=${fid},${opp},shrine`, { waitUntil: 'load', timeout: 180000 });
const t0 = Date.now();
let ready = false;
while (Date.now() - t0 < 420000) {
  ready = await page.evaluate(() => { const g = window.__game; return !!(g && g.p1 && g.p2 && g.p1.t3actions && g.roundState === 'fight'); }).catch(() => false);
  if (ready) break;
  await page.waitForTimeout(1000);
}
console.log('READY', ready);
if (!ready) { await browser.close(); process.exit(1); }
// both sides CPU, aggressive and throw-happy; endless fight
await page.evaluate(async () => {
  const g = window.__game;
  const { AIController } = await import('./js/ai.js');
  const per = { aggression: 0.95, grabBias: 0.35, reaction: 0.8, difficulty: 1 };
  g.ai1 = new AIController(g.p1, per);
  g.ai = new AIController(g.p2, per);
  g.roundTime = 0; g.timer = Infinity;
  window.__soak = { cache: new Map() };
});
const sampleFn = async () => {
  const g = window.__game, T3 = await import('three');
  const S = window.__soak;
  const out = [];
  g.timer = Infinity;
  for (const [side, f] of [['p1', g.p1], ['p2', g.p2]]) {
    if (!f || !f.model) continue;
    f.hp = f.maxHp;  // endless fight: no KO, no round end
    let sk = null;
    f.model.traverse((o) => { if (!sk && o.isSkinnedMesh && o.skeleton) sk = o.skeleton; });
    if (!sk) continue;
    let ref = S.cache.get(sk.uuid);
    if (!ref) {
      const bindW = sk.boneInverses.map((m) => m.clone().invert());
      const idx = new Map(sk.bones.map((b, i) => [b, i]));
      ref = [];
      sk.bones.forEach((b, i) => {
        if (!/(Spine\d?|Neck|Head|Arm|ForeArm|UpLeg|Leg)$/.test(b.name.split(':').pop())) return;
        const pi = idx.get(b.parent);
        const L = pi !== undefined ? bindW[pi].clone().invert().multiply(bindW[i]) : bindW[i];
        const q = new T3.Quaternion(); L.decompose(new T3.Vector3(), q, new T3.Vector3());
        ref.push([b, q]);
      });
      S.cache.set(sk.uuid, ref);
    }
    let at = 0;
    for (const [b, q] of ref) if (2 * Math.acos(Math.min(1, Math.abs(q.dot(b.quaternion)))) < 0.02) at++;
    const bindFrac = ref.length ? at / ref.length : 0;
    if (bindFrac < 0.7) { out.push({ side, ok: true, state: f.state }); continue; }
    const acts = [];
    for (const a of (f.mixer && f.mixer._actions) || []) {
      const w = a.enabled ? a.getEffectiveWeight() : 0;
      if (w > 0.01) acts.push(`${a.getClip().name}@${w.toFixed(2)}${a.isRunning() ? '' : '(held)'}`);
    }
    const p = f._atkPlan || {};
    out.push({ side, ok: false, id: f.char && f.char.id, bindFrac: +bindFrac.toFixed(2), state: f.state, stateT: +(f.stateT || 0).toFixed(2),
      attackName: f.attackName || null, moveKey: f.attack && f.attack.moveKey || null, plan: p.name || null, kind: p.kind || null,
      cinematic: !!(f._cinematic && !f._cinematic.done), grab: f.state === 'throwing' || f.state === 'thrown' || f.state === 'throwExec',
      acts: acts.slice(0, 6), nActs: acts.length });
  }
  return out;
};
const incidents = new Map();
const stateTally = {}, tposeTally = {};
let samples = 0, shots = 0;
const tEnd = Date.now() + seconds * 1000;
while (Date.now() < tEnd) {
  const res = await page.evaluate(sampleFn).catch((e) => [{ error: String(e.message || e).slice(0, 160) }]);
  samples++;
  for (const r of res) {
    if (r.error) { logs.push('[sample] ' + r.error); continue; }
    const sk = `${r.side}:${r.state}`;
    stateTally[sk] = (stateTally[sk] || 0) + 1;
    if (r.ok) continue;
    tposeTally[sk] = (tposeTally[sk] || 0) + 1;
    const key = `${r.side}|${r.id}|${r.state}|${r.attackName || ''}|${r.kind || ''}:${r.plan || ''}|${(r.acts[0] || 'NO ACTION').split('@')[0]}`;
    const inc = incidents.get(key) || { key, count: 0, first: r, firstAt: +((Date.now() - (tEnd - seconds * 1000)) / 1000).toFixed(1) };
    inc.count++;
    if (!incidents.has(key)) {
      incidents.set(key, inc);
      console.log('TPOSE', JSON.stringify(r));
      if (shots < 12) {
        await page.evaluate(() => { window.__game.paused = true; });
        try { await page.screenshot({ path: `${out}/tpose_${String(++shots).padStart(2, '0')}.png`, timeout: 60000 }); inc.shot = `tpose_${String(shots).padStart(2, '0')}.png`; } catch (e) { /* slow renderer */ }
        await page.evaluate(() => { window.__game.paused = false; });
      }
    }
  }
  await page.waitForTimeout(150);
}
const list = [...incidents.values()].sort((a, b) => b.count - a.count);
const total = Object.values(tposeTally).reduce((a, b) => a + b, 0), all = Object.values(stateTally).reduce((a, b) => a + b, 0);
fs.writeFileSync(`${out}/tpose_soak.json`, JSON.stringify({ fighter: fid, opponent: opp, seconds, samples, fighterSamples: all, tposeSamples: total, stateTally, tposeTally, incidents: list, logs: logs.slice(0, 200) }, null, 1));
const md = [`# T-pose soak: ${fid} vs ${opp} (${seconds} s, ${samples} samples, \`tools/anim/tpose_soak_probe.mjs\`)`, '',
  `**T-pose in ${total} of ${all} fighter samples (${all ? (100 * total / all).toFixed(1) : 0}%)**, ${list.length} distinct incidents.`, '',
  '| count | side | fighter | state | move | plan | top action | bindFrac | shot |', '|---|---|---|---|---|---|---|---|---|',
  ...list.map((i) => `| ${i.count} | ${i.first.side} | ${i.first.id} | ${i.first.state} | ${i.first.attackName || ''} | ${i.first.kind || ''} ${i.first.plan || ''} | ${(i.first.acts[0] || 'NO ACTION').replace(/\|/g, '/')} | ${i.first.bindFrac} | ${i.shot || ''} |`)].join('\n');
fs.writeFileSync(`${out}/tpose_soak.md`, md + '\n');
console.log('DONE', JSON.stringify({ samples, fighterSamples: all, tposeSamples: total, incidents: list.length }));
await browser.close();
