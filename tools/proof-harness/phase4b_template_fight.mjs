/* Lane B Phase 4B — CDP fight proof v7 (final harness).
   Single self-contained run: launch -> boot -> fight -> frames ->
   exit. Built from the three runs that each proved a piece:
   - probe_v4: launch flags that work here (Playwright set incl.
     anti-throttling), all-external-DNS refused fast (MAP * ->
     127.0.0.1), profile on /dev/shm, seeded Creation-Suite save,
     modes via boot or menu tap.
   - driver5: current-main API (game.p1/game.p2 Fighters, .char,
     .bones, .root, .model, ._t3.bank/.modelKey, .t3actions,
     model.userData.morphInfluencesApplied) + full wiring dump.
     modes.startFight's promise runs match-long, so settle =
     fighters constructed + roundState 'fight', never the promise.
   - driver6: Page.captureScreenshot hangs in this headless build;
     frames are grabbed same-task (arena render + canvas.toDataURL
     in one synchronous evaluate).
   The save exercises the suite flow exactly as a player's does:
   localStorage wh_creation_suite_v1 -> custom-fighter.js ->
   roster entry -> startFight. Template: powerhouse. Morphs:
   b_weight 0.8, b_tone 0.4 (PR #1495/#1496 path). Opponent:
   pantera (stock, king bank). */
import { spawn } from 'node:child_process';
import { createHash } from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';

const HOME = process.env.HOME;
const OUT = path.join(HOME, 'workspace/_everything-else-20261102/laneB/proof');
const URL = 'http://127.0.0.1:8765/game/';
const CHROME = HOME + '/.cache/ms-playwright/chromium-1248/chrome-linux64/chrome';
fs.mkdirSync(OUT, { recursive: true });

const SAVE = {
  version: 1, app: 'wh-creation-suite',
  profile: { name: 'PHASE4B PROOF', short_name: 'P4B', soul: 'proof', title: ['THE TEMPLATE'] },
  body: { body_type: 'Austin', skin_tone: '#c98d5e', proportions: {}, morph_targets: { b_weight: 0.8, b_tone: 0.4 }, frame: {} },
  morphs: {}, jiggle: {}, attireIndex: 0, attires: [{}, {}, {}, {}], wardrobe: [],
  wallet: { souls: 0 }, mode: 'blank', rosterRef: null,
  template: 'powerhouse', baseGlb: 'customization/templates/meshes/powerhouse.glb',
};

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const sha = (b) => createHash('sha256').update(b).digest('hex').slice(0, 16);

const child = spawn(CHROME, [
  '--headless=new', '--remote-debugging-port=9337', '--remote-debugging-address=127.0.0.1',
  '--user-data-dir=/dev/shm/laneB-profile8',
  '--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader',
  '--ignore-gpu-blocklist', '--no-sandbox', '--hide-scrollbars',
  '--window-size=640,360', '--mute-audio',
  '--disable-field-trial-config', '--disable-background-networking',
  '--disable-background-timer-throttling', '--disable-backgrounding-occluded-windows',
  '--disable-renderer-backgrounding', '--disable-hang-monitor',
  '--disable-ipc-flooding-protection', '--disable-sync', '--no-first-run',
  '--force-color-profile=srgb', '--enable-features=CDPScreenshotNewSurface',
  '--host-resolver-rules=MAP * 127.0.0.1, EXCLUDE 127.0.0.1, EXCLUDE localhost',
  'about:blank',
], { stdio: ['ignore', 'pipe', 'pipe'] });
child.stderr.on('data', () => {});

async function waitChrome() {
  for (let i = 0; i < 120; i++) {
    try { const r = await fetch('http://127.0.0.1:9337/json/version'); if (r.ok) return await r.json(); } catch {}
    await sleep(500);
  }
  throw new Error('chrome devtools never came up');
}
const ver = await waitChrome();
console.log('chrome up:', ver.Browser, 'pid', child.pid);

const ws = new WebSocket(ver.webSocketDebuggerUrl);
await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
let mid = 0;
const pending = new Map();
const logs = [];
ws.onmessage = (ev) => {
  const m = JSON.parse(ev.data);
  if (m.id && pending.has(m.id)) { const p = pending.get(m.id); pending.delete(m.id); m.error ? p.rej(new Error(JSON.stringify(m.error).slice(0, 300))) : p.res(m.result); return; }
  if (m.method === 'Runtime.consoleAPICalled') {
    const txt = (m.params.args || []).map((a) => a.value !== undefined ? String(a.value) : (a.description || a.type)).join(' ').slice(0, 300);
    const line = `[console.${m.params.type}] ${txt}`; logs.push(line); console.log('PAGE', line);
  } else if (m.method === 'Runtime.exceptionThrown') {
    const d = m.params.exceptionDetails;
    const line = `[pageerror] ${(d.exception && (d.exception.description || d.exception.value)) || d.text}`;
    logs.push(line); console.log('PAGE', line);
  } else if (m.method === 'Log.entryAdded') {
    const e = m.params.entry; const line = `[log.${e.level}] ${(e.text || '').slice(0, 300)}`;
    logs.push(line); console.log('PAGE', line);
  }
};
function send(method, params = {}, sessionId, deadlineMs = 30000) {
  const id = ++mid;
  const msg = { id, method, params };
  if (sessionId) msg.sessionId = sessionId;
  const p = new Promise((res, rej) => { pending.set(id, { res, rej }); ws.send(JSON.stringify(msg)); });
  const d = new Promise((_, rej) => setTimeout(() => { pending.delete(id); rej(new Error('CDP deadline ' + deadlineMs + 'ms: ' + method)); }, deadlineMs));
  return Promise.race([p, d]);
}
const targets = await (await fetch('http://127.0.0.1:9337/json/list')).json();
const page = targets.find((t) => t.type === 'page');
const { sessionId: S } = await send('Target.attachToTarget', { targetId: page.id, flatten: true });
await send('Page.enable', {}, S).catch(() => {});
await send('Runtime.enable', {}, S).catch(() => {});
await send('Log.enable', {}, S).catch(() => {});
await send('Page.addScriptToEvaluateOnNewDocument', {
  source: `try { localStorage.setItem('wh_creation_suite_v1', ${JSON.stringify(JSON.stringify(SAVE))}); } catch (e) {}`,
}, S);

async function evaluate(expr, tries = 4) {
  let last;
  for (let i = 0; i < tries; i++) {
    try {
      const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: false }, S, 45000);
      if (r.exceptionDetails) throw new Error('eval exc: ' + JSON.stringify(r.exceptionDetails).slice(0, 300));
      return r.result.value;
    } catch (e) { last = e; console.log('eval retry', i + 1, String(e.message).slice(0, 120)); await sleep(2000); }
  }
  throw last;
}
async function pollUntil(fnExpr, timeoutMs, label, heartbeat) {
  const t0 = Date.now(); let lastBeat = 0;
  for (;;) {
    const v = await evaluate(fnExpr, 2).catch(() => undefined);
    if (v) return v;
    if (Date.now() - t0 > timeoutMs) throw new Error('timeout waiting: ' + label);
    if (heartbeat && Date.now() - lastBeat > 30000) {
      lastBeat = Date.now();
      const hb = await evaluate(heartbeat, 1).catch(() => 'hb-failed');
      console.log('HEARTBEAT', label, JSON.stringify(hb));
    }
    await sleep(1500);
  }
}

const SNAP = `(() => { const g = window.__game; if (!g) return null;
  const f = g.p1;
  return { round: g.roundState, p1model: f && f.char && f.char.model, p1state: f && f.state, p1atk: f && f.attackName,
    p1clip: f && (f._t3stateKey || (f._t3current && f._t3current.getClip && f._t3current.getClip().name) || null),
    p2state: g.p2 && g.p2.state, p2hp: g.p2 && g.p2.hp, p1hp: f && f.hp }; })()`;
const POSE = `(f) => { const o = {}; if (!f || !f.bones) return o;
  if (f.root && f.root.updateMatrixWorld) f.root.updateMatrixWorld(true);
  for (const n of ['Hips','Head','LeftHand','RightHand','LeftFoot','RightFoot']) {
    const b = f.bones[n]; if (!b || !b.matrixWorld) { o[n] = null; continue; }
    const e = b.matrixWorld.elements;
    o[n] = [Math.round(e[12]*1000)/1000, Math.round(e[13]*1000)/1000, Math.round(e[14]*1000)/1000];
  } return o; }`;

async function shoot(name, note) {
  const grab = await evaluate(`(() => { const g = window.__game; const a = g.arena;
    if (a && a.__render) a.__render();
    const cs = [...document.querySelectorAll('canvas')];
    const c = cs.sort((x, y) => (y.width * y.height) - (x.width * x.height))[0];
    if (!c) return { err: 'no canvas' };
    return { data: c.toDataURL('image/png'), s: ${SNAP}, pose: (${POSE})(g.p1) }; })()`);
  if (!grab || grab.err || !grab.data) throw new Error('grab failed for ' + name + ': ' + JSON.stringify(grab).slice(0, 200));
  const buf = Buffer.from(grab.data.split(',')[1], 'base64');
  const file = path.join(OUT, name + '.png');
  fs.writeFileSync(file, buf);
  const ok = fs.readFileSync(file).equals(buf);
  console.log('SHOT', name, buf.length, 'B sha', sha(buf), 'verified', ok, JSON.stringify(grab.s), JSON.stringify(grab.pose), note || '');
  return { name, bytes: buf.length, sha256_16: sha(buf), writeVerified: ok, state: grab.s, pose: grab.pose };
}
async function key(type, def) {
  await send('Input.dispatchKeyEvent', { type, key: def[0], code: def[1], windowsVirtualKeyCode: def[2], nativeVirtualKeyCode: def[2] }, S, 15000);
}
const tap = async (def) => { await key('keyDown', def); await sleep(70); await key('keyUp', def); };
const D1 = ['1', 'Digit1', 49], D2 = ['2', 'Digit2', 50], D4 = ['4', 'Digit4', 52];
const shots = [];
let success = false;
try {
  console.log('navigating');
  await send('Page.navigate', { url: URL }, S, 60000);
  const route = await pollUntil(`(() => {
    if (window.__modes) return { via: 'boot' };
    const els = [...document.querySelectorAll('[data-action="mode-arcade"], [data-action="play"]')];
    const el = els.find((e) => { const r = e.getBoundingClientRect(); return r.width > 4 && r.height > 4; });
    if (!el) return null;
    el.scrollIntoView({ block: 'center' });
    const r = el.getBoundingClientRect();
    return { via: 'tap', action: el.dataset.action, x: Math.round(r.left + r.width / 2), y: Math.round(r.top + r.height / 2) };
  })()`, 600000, 'modes or menu card', SNAP);
  console.log('route:', JSON.stringify(route));
  if (route.via === 'tap') {
    await send('Input.dispatchMouseEvent', { type: 'mousePressed', x: route.x, y: route.y, button: 'left', clickCount: 1 }, S);
    await sleep(90);
    await send('Input.dispatchMouseEvent', { type: 'mouseReleased', x: route.x, y: route.y, button: 'left', clickCount: 1 }, S);
    await pollUntil('!!window.__modes', 240000, 'window.__modes after tap', SNAP);
  }
  console.log('modes ready');

  await evaluate(`(() => { if (window.__fightFired) return 'already';
    window.__fightFired = true; window.__fightErr = null;
    window.__modes.startFight('custom', 'pantera', { mode: 'arcade' })
      .catch((e) => { window.__fightErr = String((e && e.message) || e); });
    return 'fired'; })()`);
  console.log('fight fired');
  await pollUntil(`(() => { const g = window.__game; return !!(g && g.p1 && g.p2); })()`, 1200000, 'fighters constructed', SNAP);
  const ferr = await evaluate('window.__fightErr');
  if (ferr) throw new Error('startFight rejected: ' + ferr);
  await pollUntil(`window.__game && window.__game.roundState === 'fight'`, 300000, 'roundState fight', SNAP);
  console.log('round live');
  await sleep(1200);

  const wiring = await evaluate(`(() => {
    const g = window.__game; const out = {};
    const f = g.p1;
    out.roundState = g.roundState;
    out.p1 = { charId: f.char && f.char.id, model: f.char && f.char.model, name: f.char && f.char.name,
      template: f.char && f.char.template, morphTargets: f.char && f.char.morphTargets,
      morphApplied: f.model && f.model.userData && f.model.userData.morphInfluencesApplied,
      t3bank: f._t3 && f._t3.bank, t3modelKey: f._t3 && f._t3.modelKey,
      t3actions: f.t3actions ? Object.keys(f.t3actions).length : 0, state: f.state };
    const need = ['Hips','Spine','Spine1','Spine2','Chest','Neck','Head','LeftArm','RightArm','LeftForeArm','RightForeArm','LeftHand','RightHand','LeftUpLeg','RightUpLeg','LeftLeg','RightLeg','LeftFoot','RightFoot'];
    out.bonesPresent = need.filter((n) => f.bones && f.bones[n]);
    out.bonesMissing = need.filter((n) => !(f.bones && f.bones[n]));
    const p2 = g.p2;
    out.p2 = { charId: p2.char && p2.char.id, model: p2.char && p2.char.model,
      t3bank: p2._t3 && p2._t3.bank, t3actions: p2.t3actions ? Object.keys(p2.t3actions).length : 0, state: p2.state };
    return out;
  })()`);
  fs.writeFileSync(path.join(OUT, 'wiring.json'), JSON.stringify(wiring, null, 2));
  console.log('WIRING', JSON.stringify(wiring));

  await evaluate(`(() => { const g = window.__game;
    if (g.ai) g.ai.update = () => {};
    if (g.ai1) g.ai1.update = () => {};
    g.timer = 999;
    const a = g.arena; if (a && a.render) { a.__render = a.render.bind(a); a.render = () => {}; }
    return true; })()`);
  await sleep(400);

  const reset = async () => { await evaluate(`(() => { const g = window.__game; const a = g.p1, b = g.p2;
    b.root.position.x = a.root.position.x + 1.15 * (a.facing || 1); b.root.position.z = a.root.position.z;
    b.hp = b.maxHp; b.state = 'idle'; a.state = 'idle'; a.attackName = null; return true; })()`); await sleep(120); };

  shots.push(await shoot('01-idle-stance', 'idle after round start'));
  await tap(D1); await sleep(130); shots.push(await shoot('02-attack-1', 'after Digit1 tap +130ms'));
  await reset();
  await tap(D2); await sleep(150); shots.push(await shoot('03-attack-2', 'after Digit2 tap +150ms'));
  await reset();
  await tap(D4); await sleep(170); shots.push(await shoot('04-attack-4', 'after Digit4 tap +170ms'));
  await reset();
  await tap(D1); await sleep(140); await tap(D2); await sleep(160); shots.push(await shoot('05-string-1-2', 'Digit1 then Digit2 string'));
  await reset();
  const fwdKey = await evaluate(`(() => { const a = window.__game.p1; return (a.facing || 1) >= 0 ? 'ArrowRight' : 'ArrowLeft'; })()`);
  const fwdDef = fwdKey === 'ArrowRight' ? ['ArrowRight', 'ArrowRight', 39] : ['ArrowLeft', 'ArrowLeft', 37];
  await key('keyDown', fwdDef); await sleep(650); shots.push(await shoot('06-walk-forward', 'holding forward 650ms')); await key('keyUp', fwdDef);
  await reset();
  await key('keyDown', ['ArrowDown', 'ArrowDown', 40]); await key('keyDown', fwdDef); await sleep(60);
  await tap(D2); await sleep(150); shots.push(await shoot('07-df-2', 'df+2 launcher attempt'));
  await key('keyUp', fwdDef); await key('keyUp', ['ArrowDown', 'ArrowDown', 40]);

  fs.writeFileSync(path.join(OUT, 'shots.json'), JSON.stringify(shots, null, 2));
  console.log('SHOTS DONE', shots.length);
  success = true;
} finally {
  try { fs.writeFileSync(path.join(OUT, 'console.log'), logs.join('\n')); } catch {}
  if (success) {
    try { await send('Browser.close', {}, null, 10000); } catch {}
    try { ws.close(); } catch {}
    child.kill('SIGKILL');
  } else {
    console.log('FAILED — browser left running on :9337 (pid ' + child.pid + ') for inspection');
  }
}
console.log('PROBE V7 COMPLETE success=' + success);
process.exit(success ? 0 : 2);
