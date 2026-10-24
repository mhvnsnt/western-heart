// MOVE PROOF HARNESS (lane B, 2026-10-24) — the owner's "play it to see what's wrong" tool.
//
//   node tools/proof-harness/moves.mjs OUTDIR [fighters] [set]
//     fighters  comma list of fighter ids | core (skull,buffalo-bill,pantera,chatur,thor) | roster
//     set       core (default: the buttons, strings, directionals, motions, chords, HEAT, rage)
//               | strings (core + every <=4-step string in the fighter's moveset) | all (every
//               playable notation in the fighter's notation table) | a ';'-separated notation list
//   env: PORT (8765), DUMMY (p2 id, default thor; skull for thor), PLAYWRIGHT_MODULE, CHROMIUM_PATH
//
// A real arcade fight in headless Chromium (the repo served on PORT). The CPU is frozen in front
// of P1 as a dummy. Every notation is PLAYED on the real keyboard (game/js/input.js bindings:
// arrows = stick, Digit1-4 = 1/2/3/4) with human timing: a direction tapped ~40 ms before its
// button, a held one ~180 ms, a motion ~40 ms per step, a chord's two keys 8 ms apart, every later
// string step pressed ~100 ms into the hit before it. Instrumentation only OBSERVES the game:
// InputManager.consume (what the input layer emitted), Fighter.tryAttack (what the fighter got
// and returned), the attack that started (notation, move key + name, frame data), the animation
// clip that actually played (Fighter._t3current, lane D's clip plan kind), the dummy's
// receiveHit result (hit / block / ...) and its HP. Each row: expected move vs what fired, flags:
//   THROW_FOR_NON_THROW  a non-throw input fired a throw move or played a grab/throw clip
//   CHORD_FROM_SINGLE    the input layer turned a single-button input into a chord
//   SIDESTEP             the input layer emitted a sidestep (ss-up / ss-down) during the input
//   WRONG_MOVE           the last move that fired is not the notation's move
//   NOTHING              no move fired
// Output: OUTDIR/moves.json (every row + raw event log), OUTDIR/moves.csv, OUTDIR/summary.txt,
// a screenshot per fighter of its first row.
const { chromium } = await import(process.env.PLAYWRIGHT_MODULE || '/opt/node22/lib/node_modules/playwright/index.mjs');
import fs from 'fs';
import path from 'path';
const [,, out = 'moves-proof', fightersArg = 'core', setArg = 'core'] = process.argv;
fs.mkdirSync(out, { recursive: true });
const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..', '..');
const PORT = process.env.PORT || 8765;
const CORE_FIGHTERS = ['skull', 'buffalo-bill', 'pantera', 'chatur', 'thor'];
const CORE_SET = ['1', '2', '3', '4', '1,2', '1,2,1', '2,1', '1,1', '3,3', '4,4', 'd/f+1', 'd/f+2', 'd+1', 'd+4',
  'f+2', 'b+1', 'b+2', 'u/f+4', 'f,f+2', 'f,F+2', 'qcf+1', 'qcf+2', 'd/b+3', 'FC.1', 'WS.2', '1+2', '3+4',
  '1+3', '2+4', 'b+1+2', '1+4', 'HEAT:2+3', 'RAGE:1+2', 'RAGE:3+4'];

// ---- notation grammar (same as test/moveset-reachability.test.mjs) ----
const DIRS = 'd/f|d/b|u/f|u/b|f|b|u|d|n|D/F|D/B|U/F|U/B|F|B|U|D|N';
const BTN = '[1-4](?:\\+[1-4])*\\*?';
const RX_PRESS = new RegExp(`^(?:(qcf|qcb|hcf|hcb|${DIRS})\\+)?(${BTN})$`);
const RX_DIR = new RegExp(`^(?:qcf|qcb|hcf|hcb|${DIRS})$`);
const RX_PFX = /^((?:[A-Za-z][A-Za-z0-9_]*\.)+)(.*)$/;
const MOTION = { qcf: ['d', 'd/f', 'f'], qcb: ['d', 'd/b', 'b'], hcf: ['b', 'd/b', 'd', 'd/f', 'f'], hcb: ['f', 'd/f', 'd', 'd/b', 'b'] };
function parse(n) {
  const toks = n.split(/[,~:]/); const steps = []; let acc = [], pos = 0;
  for (const t of toks) {
    const pm = RX_PFX.exec(t); const body = pm ? pm[2] : t;
    if (!RX_PRESS.test(body) && !RX_DIR.test(body)) return null;
    acc.push(t); pos += t.length;
    if (RX_PRESS.test(body)) { acc.upto = n.slice(0, pos); steps.push(acc); acc = []; }
    pos += 1; // the separator
  }
  if (acc.length || !steps.length) return null;
  return steps.map(ts => { // ['d','d/f','f+1'] -> {prefix, dirs:[...], hold, btn}
    const pm = RX_PFX.exec(ts[0]); const prefix = pm ? pm[1] : '';
    const first = pm ? pm[2] : ts[0];
    const all = [first, ...ts.slice(1)];
    const last = RX_PRESS.exec(all[all.length - 1]);
    let dirs = []; let neutral = false;
    for (const t of all.slice(0, -1)) dirs.push(...(MOTION[t] || [t]));
    if (last[1]) dirs.push(...(MOTION[last[1]] || [last[1]]));
    else if (dirs.length && dirs[dirs.length - 1].toLowerCase() === 'n') neutral = true;
    const fin = last[1] && !MOTION[last[1]] ? last[1] : null;
    return { text: ts.join(','), upto: ts.upto, prefix, dirs, hold: !!(fin && fin !== fin.toLowerCase()), neutral, btn: last[2].replace(/\*$/, '') };
  });
}

// ---- browser ----
const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
  args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const allRows = []; const pageLogs = [];
const csvEsc = (v) => { const s = v == null ? '' : String(v); return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s; };

async function newPage() {
  const page = await browser.newPage({ viewport: { width: 960, height: 540 } });
  page.on('pageerror', e => pageLogs.push(`[pageerror] ${e.message}`));
  page.on('console', m => { if (/error/i.test(m.type()) || /pageerror|Uncaught/.test(m.text())) pageLogs.push(`[${m.type()}] ${m.text()}`); });
  await page.goto(`http://127.0.0.1:${PORT}/game/index.html`, { waitUntil: 'load' });
  await page.waitForFunction(() => window.__modes && window.__game, null, { timeout: 90000 });
  return page;
}

let fighters = fightersArg === 'core' ? CORE_FIGHTERS : fightersArg.split(',').filter(Boolean);
if (fightersArg === 'roster') {
  const p = await newPage();
  fighters = await p.evaluate(async () => (await import('./js/characters.js')).ROSTER.map(c => c.id));
  await p.close();
}
console.log(`fighters (${fighters.length}): ${fighters.join(' ')}`);

for (const fid of fighters) {
  const dummy = process.env.DUMMY || (fid === 'thor' ? 'skull' : 'thor');
  let page;
  try {
    page = await newPage();
    await page.evaluate(() => window.__modes.startMode('arcade'));
    // Software GL here cannot draw the stage at a usable rate; game logic runs unchanged, the arena
    // renders only for the screenshot (same as combat_inputs.mjs).
    await page.evaluate(() => { const a = window.__game.arena; a.__render = a.render.bind(a); a.render = () => {}; });
    await page.evaluate(async ([a, b]) => { await window.__modes.startFight(a, b, { mode: 'arcade' }); }, [fid, dummy]);
    await page.waitForFunction(() => window.__game && window.__game.roundState === 'fight', null, { timeout: 180000 });
  } catch (e) {
    console.log(`${fid}: fight did not start (${e.message.split('\n')[0]})`);
    allRows.push({ fighter: fid, input: '-', flags: 'NO_FIGHT', note: e.message.split('\n')[0] });
    if (page) await page.close().catch(() => {});
    continue;
  }
  // Instrument (observe only) + freeze the CPU as a training dummy in front of P1.
  const info = await page.evaluate(async () => {
    const g = window.__game, f = g.p1, d = g.p2;
    const M = await import('./js/movesets.js');
    window.__MV = { M, log: [], seen: new Set() };
    const L = window.__MV.log;
    g.ai.update = () => {}; g.timer = 9999;
    const consume = g.input.consume.bind(g.input);
    g.input.consume = () => { const q = consume(); if (q.length) L.push({ k: 'in', t: performance.now(), q }); return q; };
    const ta = f.tryAttack.bind(f);
    f.tryAttack = (name) => { const r = ta(name); L.push({ k: 'try', t: performance.now(), name, ret: !!r, now: f.attackName, id: f._attackId }); return r; };
    const rh = d.receiveHit.bind(d);
    d.receiveHit = (move, att) => { const hp = d.hp; const r = rh(move, att); L.push({ k: 'contact', t: performance.now(), id: att && att._attackId, by: att && att.attackName, r, dmg: +(hp - d.hp).toFixed(1) }); return r; };
    const up = f.update.bind(f);
    let lastId = f._attackId || 0, lastClip = null;
    const clipName = () => { const a = f._t3current; return a ? (a._clip ? a._clip.name : (a.getClip ? a.getClip().name : null)) : null; };
    f.update = (dt, opp) => {
      up(dt, opp);
      const id = f._attackId || 0;
      if (id !== lastId && f.attack) {
        lastId = id; lastClip = null;
        const a = f.attack;
        L.push({ k: 'atk', t: performance.now(), id, n: f.attackName, key: a.moveKey || null, name: a.moveName || null, grab: !!a.isGrab,
          st: a.startup, act: a.active, rec: a.recovery, dmg: a.damage, t3row: a.t3row ?? null, animRow: a.animRow ?? null });
      }
      if (f.attack && (f.state === 'attack')) {
        const c = clipName();
        if (c && c !== lastClip) { lastClip = c; const p = f._atkPlan; L.push({ k: 'clip', t: performance.now(), id, clip: c, kind: p && p.id === id ? p.kind : null }); }
      }
    };
    const ms = M.getFighterMoveset(f._movesetId);
    return { movesetId: f._movesetId, facing: f.facing, bank: f._t3 && f._t3.bank, nMoves: ms ? Object.keys(ms.moves).length : 0,
      slots: ms ? Object.keys(ms._slots || ms.slots || {}) : [] };
  });
  // the bank row -> which moves own it (so 'row:44' reads as a move name)
  let rowOwner = {};
  try {
    const msj = JSON.parse(fs.readFileSync(path.join(ROOT, 'game/assets/movesets', `${info.movesetId}.json`), 'utf8'));
    for (const [k, m] of Object.entries(msj.moves || {})) {
      const r = Array.isArray(m.t3_row) ? m.t3_row[m.t3_row.length - 1] : m.t3_row;
      const ownBank = !info.bank || m.t3_source === info.bank || String(m.anim_ref || '').startsWith(`t3:${info.bank}:`);
      if (r != null && ownBank && !rowOwner['row:' + r]) rowOwner['row:' + r] = `${m.input || k} ${m.name || ''}`.trim();
    }
  } catch (e) { /* no json */ }
  let set = setArg === 'core' || setArg === 'strings' || setArg === 'all' ? CORE_SET.slice() : setArg.split(';');
  if (setArg === 'strings') set.push(...info.slots.filter(n => /,/.test(n) && !/~[a-z]/.test(n) && parse(n) && parse(n).length > 1 && parse(n).length <= 4 && !set.includes(n)));
  if (setArg === 'all') set.push(...info.slots.filter(n => !/~[a-z]/.test(n) && parse(n) && !set.includes(n)));
  const fwd = info.facing > 0 ? 'ArrowRight' : 'ArrowLeft', back = info.facing > 0 ? 'ArrowLeft' : 'ArrowRight';
  const KEYS = { f: [fwd], b: [back], u: ['ArrowUp'], d: ['ArrowDown'], 'u/f': ['ArrowUp', fwd], 'u/b': ['ArrowUp', back], 'd/f': ['ArrowDown', fwd], 'd/b': ['ArrowDown', back], n: [] };
  const held = new Set();
  const stick = async (dir) => {
    const want = new Set(KEYS[(dir || 'n').toLowerCase()] || []);
    for (const k of [...held]) if (!want.has(k)) { await page.keyboard.up(k); held.delete(k); }
    for (const k of want) if (!held.has(k)) { await page.keyboard.down(k); held.add(k); }
  };
  const wait = (ms) => page.waitForTimeout(ms);
  const press = async (btn) => {
    const bs = btn.split('+');
    for (let i = 0; i < bs.length; i++) { if (i) await wait(8); await page.keyboard.down('Digit' + bs[i]); }
    await wait(45);
    for (const b of bs) await page.keyboard.up('Digit' + b);
  };
  let shot = false;
  for (const raw of set) {
    const sys = /^(HEAT|RAGE):(.*)$/.exec(raw);
    const n = sys ? sys[2] : raw;
    const steps = parse(n);
    if (!steps) { allRows.push({ fighter: fid, input: raw, flags: 'NOT_A_NOTATION' }); continue; }
    const prefix = steps[0].prefix;
    const ptoks = prefix.split('.').filter(Boolean);
    // reset both fighters, the buffer and the input layer; state the notation needs
    const expect = await page.evaluate(([n, sys, ptoks]) => {
      const g = window.__game, f = g.p1, d = g.p2, M = window.__MV.M;
      for (const x of [f, d]) { x.hp = 100; x.stun = 0; x.attack = null; x.attackName = null; x._queuedNext = null; x._enter('idle'); x.vx = 0; x.vz = 0; }
      d.root.position.x = f.root.position.x + 1.15 * f.facing; d.root.position.z = f.root.position.z;
      f.stance = null; f.stanceT = 0; f._risingT = 0; f._rageUsed = false; f._lastPress = null;
      f._urgeOn = false; f._urgeUsed = true; f._urgePips = 0; // urge spent: 2+3 is the fighter's own move
      Object.assign(f.tekken, { lastMove: null, lastMoveT: 0, _strPath: null, dirEvents: [], _dash: null });
      if (sys === 'HEAT') f._urgeUsed = false;                       // fresh Soul Urge gauge: HEAT = Urge Burst
      if (sys === 'RAGE' || ptoks.includes('R') || ptoks.includes('RD')) f.hp = 20; // rage
      if (ptoks.includes('US')) { f._urgeOn = true; f._urgePips = 2; }
      if (ptoks.includes('UB')) f._urgeUsed = false;
      const st = ptoks.find(t => !['FC', 'WS', 'SS', 'R', 'RD', 'UB', 'US'].includes(t));
      if (st) { f.stance = st; f.stanceT = 5; }
      window.__MV.log.length = 0;
      const want = sys === 'HEAT' ? 'UB.2+3' : sys === 'RAGE' ? (n === '3+4' ? 'RD.3+4' : 'R.1+2') : n;
      const r = M.resolveMove(f._movesetId, want);
      return { want, key: r ? r.key : null, name: r ? r.move.name : null, grab: !!(r && (r.move.isGrab || r.move.move_class === 'throw')) };
    }, [n, sys ? sys[1] : null, ptoks]);
    await wait(250);
    // ---- play it ----
    const t0 = Date.now();
    if (ptoks.includes('FC') || ptoks.includes('WS')) { await stick('d'); await wait(320); }
    if (ptoks.includes('WS')) { await stick('n'); await wait(40); }
    if (ptoks.includes('SS')) { await page.keyboard.down('ArrowUp'); await wait(60); await page.keyboard.up('ArrowUp'); await wait(220); }
    const base = ptoks.includes('FC') ? 'd' : 'n';
    let prevText = null;
    for (let i = 0; i < steps.length; i++) {
      const s = steps[i];
      if (i > 0) { // ~100 ms into the previous hit (or 150 ms after the press when it played nothing)
        await page.waitForFunction((p) => { const f = window.__game.p1; return f.attackName === p && f.stateT >= 0.1 && !f._queuedNext; }, prevText, { timeout: 1200, polling: 16 }).catch(() => {});
        await wait(20);
      }
      const dirs = s.dirs.filter(x => x.toLowerCase() !== 'n' || s.neutral);
      if (s.dirs.length > 1 || s.neutral) { // motion
        for (let j = 0; j < s.dirs.length; j++) {
          await stick(s.dirs[j]); await wait(40);
          if (s.dirs[j + 1] && s.dirs[j + 1].toLowerCase() === s.dirs[j].toLowerCase()) { await stick('n'); await wait(40); }
        }
        if (s.hold) await wait(90);
        if (s.neutral) { await stick('n'); await wait(40); }
      } else if (dirs.length === 1) {
        await stick(dirs[0]); await wait(s.hold ? 180 : 40);
      } else await stick(i === 0 ? base : 'n');
      await press(s.btn);
      await wait(30);
      await stick(i === 0 ? base : 'n');
      prevText = s.upto; // the notation typed so far = the move this step should be playing
    }
    await stick('n');
    await page.waitForFunction(() => { const f = window.__game.p1; return f.state !== 'attack' && !f._queuedNext && f.state !== 'throwing'; }, null, { timeout: 4000, polling: 30 }).catch(() => {});
    await wait(350);
    const log = await page.evaluate(() => window.__MV.log.slice());
    const ms = Date.now() - t0;
    // ---- row ----
    const emitted = log.filter(e => e.k === 'in').flatMap(e => e.q);
    const atks = log.filter(e => e.k === 'atk');
    const clipOf = (id) => { const c = log.find(e => e.k === 'clip' && e.id === id); return c ? c : null; };
    const contactOf = (id) => log.filter(e => e.k === 'contact' && e.id === id);
    const fired = atks.map(a => {
      const c = clipOf(a.id); const hits = contactOf(a.id);
      return { n: a.n, key: a.key, name: a.name, grab: a.grab, clip: c ? c.clip : null, clipKind: c ? c.kind : null,
        clipOwner: c && /row:?(\d+)/.test(c.clip) ? (rowOwner['row:' + /row:?(\d+)/.exec(c.clip)[1]] || null) : null,
        contact: hits.length ? hits.map(h => h.r).join('+') : 'whiff', dmg: hits.reduce((s, h) => s + (h.dmg || 0), 0) };
    });
    const last = fired[fired.length - 1];
    const flags = [];
    const singleInput = !/\d\+\d/.test(n) && !sys;
    if (!last) flags.push('NOTHING');
    else if (expect.key && last.key !== expect.key && last.name !== expect.name) flags.push('WRONG_MOVE');
    if (singleInput && emitted.some(a => /\+/.test(a))) flags.push('CHORD_FROM_SINGLE');
    if (emitted.some(a => /^ss-/.test(a))) flags.push('SIDESTEP');
    if (!expect.grab && fired.some(x => x.grab || /throw|grab/i.test(String(x.name)) || /grab|throw/i.test(String(x.clip)) || /throw|1\+3|2\+4/i.test(String(x.clipOwner))))
      flags.push('THROW_FOR_NON_THROW');
    const tries = log.filter(e => e.k === 'try').map(e => `${e.name}${e.ret ? '' : '(x)'}`).join(' ');
    const row = { fighter: fid, input: raw, expected_notation: expect.want, expected_key: expect.key, expected_name: expect.name,
      emitted: emitted.join(' '), tries, fired: fired.map(x => x.n).join(' > '),
      move_key: last ? last.key : null, move_name: last ? last.name : null, clip: last ? last.clip : null, clip_kind: last ? last.clipKind : null,
      clip_row_owner: last ? last.clipOwner : null, contact: last ? last.contact : null, dmg: last ? +last.dmg.toFixed(1) : 0,
      verdict: flags.length ? 'FAIL' : 'ok', flags: flags.join(' '), ms, sequence: fired };
    allRows.push(row);
    console.log(`${fid.padEnd(13)} ${raw.padEnd(12)} emit[${row.emitted}] fired[${row.fired}] ${String(row.move_name).slice(0, 30).padEnd(30)} clip=${row.clip}(${row.clip_kind || '-'}) ${row.contact} ${row.verdict} ${row.flags}`);
    if (!shot && last) { shot = true; await page.evaluate(() => window.__game.arena.__render()); await page.screenshot({ path: path.join(out, `${fid}.png`) }); }
  }
  await page.close();
}
await browser.close();

// ---- outputs ----
const cols = ['fighter', 'input', 'expected_notation', 'expected_name', 'emitted', 'tries', 'fired', 'move_key', 'move_name', 'clip', 'clip_kind', 'clip_row_owner', 'contact', 'dmg', 'verdict', 'flags'];
fs.writeFileSync(path.join(out, 'moves.csv'), [cols.join(','), ...allRows.map(r => cols.map(c => csvEsc(r[c])).join(','))].join('\n') + '\n');
fs.writeFileSync(path.join(out, 'moves.json'), JSON.stringify({ generated: new Date().toISOString(), fighters, rows: allRows, pageErrors: pageLogs }, null, 1));
const per = {};
for (const r of allRows) { const p = per[r.fighter] = per[r.fighter] || { rows: 0, ok: 0, flags: {} }; p.rows++; if (r.verdict === 'ok') p.ok++; for (const fl of String(r.flags || '').split(' ').filter(Boolean)) p.flags[fl] = (p.flags[fl] || 0) + 1; }
const lines = Object.entries(per).map(([f, p]) => `${f.padEnd(24)} ${p.ok}/${p.rows} ok  ${Object.entries(p.flags).map(([k, v]) => `${k}=${v}`).join(' ')}`);
lines.push(`page errors: ${pageLogs.filter(l => /pageerror/.test(l)).length}`);
fs.writeFileSync(path.join(out, 'summary.txt'), lines.join('\n') + '\n');
console.log(lines.join('\n'));
