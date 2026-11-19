// In-page half of moveset-sweep.e2e.mjs (evaluated in the game page after the fight starts).
(async () => {
  const MS = await import('./js/movesets.js');
  const T3 = await import('./js/t3-conditions.js');
  const g = window.__game; g.running = false; g.ai.update = () => {}; g.timer = 9999; g._hitStop = 0;
  // sweep is headless logic: skip GPU draws (swiftshader), keep the scene-graph update hitboxes need
  if (g.arena && g.arena.renderer) g.arena.renderer.render = (sc) => { if (sc && sc.updateMatrixWorld) sc.updateMatrixWorld(); };
  window.__vt = 1e6; g.input._pressT = () => window.__vt;
  performance.now = () => window.__vt; // page clock = sim clock (string / dash / motion windows)
  const KEY = { 1: 'Digit1', 2: 'Digit2', 3: 'Digit3', 4: 'Digit4', S: 'KeyO', G: 'KeyU', f: 'KeyD', b: 'KeyA', u: 'KeyW', d: 'KeyS' };
  const held = new Set();
  const key = (codes, type) => { for (const c of [].concat(codes)) {
    if (type === 'keydown') { if (held.has(c)) continue; held.add(c); } else { if (!held.has(c)) continue; held.delete(c); }
    window.dispatchEvent(new KeyboardEvent(type, { code: KEY[c] || c, key: c, bubbles: true })); } };
  const dirKeys = (d) => (d && d.toLowerCase() !== 'n' ? d.toLowerCase().split('/') : []);
  const setDir = (d) => { const want = new Set(dirKeys(d)); for (const k of ['u', 'd', 'f', 'b']) if (!want.has(k)) key(k, 'keyup'); key([...want], 'keydown'); };
  const REACT = /hit|stun|launch|knock|thrown|block|stagger|crumple|fall|air|juggle|down|splat|bound|dizzy|spin|guard/i;
  const s = (f) => ({ st: f.state, an: f.attackName, mk: f.attack ? f.attack.moveKey : null, ar: f.attack && f.attack.t3row != null ? f.attack.t3source + ':' + f.attack.t3row : null, clip: f._t3current ? f._t3current.getClip().name : null,
    x: +f.root.position.x.toFixed(2), y: +f.root.position.y.toFixed(2), hp: f.hp,
    // contact diagnostics (sweep 2026-10-29): attack phase, and whether the other fighter's
    // posture accepts this attack (canBeHitBy) - classifies 'fired but did not connect'
    ph: f.attack ? f._attackPhase : null, cb: f.attack && f._opp && f._opp.canBeHitBy ? f._opp.canBeHitBy(f.attack) : null,
    rm: f.attack && f.attack.reach ? +f.attack.reach : null });
  const step = (n, out) => { for (let i = 0; i < n; i++) { window.__vt += 1000 / 60;
    { const I = g.input; if (I._udDir && !I._udHeld && window.__vt - I._udT >= 200) { clearTimeout(I._udTimer); if (I._udDir === 'up') I.up = true; else I.down = true; I._udHeld = true; } } // input.js 200 ms u/d hold timer, on the sim clock
    if (g._hitStop > 0) g._hitStop -= 1 / 60; else g._update(1 / 60); if (out) out.push({ p1: s(g.p1), p2: s(g.p2) }); } };
  const reset = (gap) => {
    // a launcher/wall hit can break the floor or a wall (stagebreaks.js drops GROUND_Y to the lower
    // level, -6 m): every later row then played falling through the old floor. Each row starts
    // on the intact stage, as a new match does (game.js calls the same reset).
    if (g.stageBreaks && ((g.stageBreaks.broken && g.stageBreaks.broken.size) || g.stageBreaks.groundY)) g.stageBreaks.reset();
    for (const k of [...held]) key(k, 'keyup');
    for (const f of [g.p1, g.p2]) { f.hp = f.maxHp || 100; f._enter('idle'); f.attack = null; f.attackName = null; f._throwPair = null;
      f.stance = null; f.stanceT = 0; f._stanceSpins = 0; f._risingT = 0; f.lockT = 0; f.lockMove = null; f.tekken.lastMove = null; f.tekken._strPath = null;
      f._stringGraceUntil = 0; f._queuedNext = null; f._queuedAfter = []; f._urgeOn = false; f._urgeT = 0; f._urgeUsed = false;
      f.lastCounterHit = false; f._t3Contact = null; f._t3Whiff = 0; f._faceDown = false; f.ssDir = 0;
      f._rageUsed = false; f._soulUses = 0; f._rageActive = false; f._nearObject = false; f._soulReleaseReady = false;
      f.vx = 0; f.vy = 0; f.stun = 0; f.invuln = 0; f._pressBuf && f._pressBuf.clear(); f.root.position.y = 0; f.onGround = true; f.dead = false; }
    g.p1.root.position.set(-gap / 2, 0, 0); g.p2.root.position.set(gap / 2, 0, 0); g.finalRound = false;
    g.input.enabled = true; g._roundLockT = 0; // a KO'ing finisher (KESSHOU / SEAL) leaves the round over
    g.roundState = 'fight'; g.timer = 9999; g.input._queue.length = 0; g.p1.facing = 1; g.p2.facing = -1; step(30); window.__vt += 1000; };
  // notation -> hits. 'X.' prefix = state X; hits split on , ~ : ; pure-direction tokens are
  // motion steps of the next hit; capital direction = held; '*' = held button.
  const MOT = { qcf: ['d', 'd/f', 'f'], qcb: ['d', 'd/b', 'b'], hcf: ['b', 'd/b', 'd', 'd/f', 'f'], hcb: ['f', 'd/f', 'd', 'd/b', 'b'], dp: ['f', 'd', 'd/f'] };
  const DIR = /^(?:[udfbnUDFBN](?:\/[udfbUDFB])?)$/;
  function parse(n) {
    let rest = n, pre = null; const m = /^([A-Za-z0-9_]+)\.(.*)$/.exec(n); if (m && !/^[1-4]$/.test(m[1])) { pre = m[1]; rest = m[2]; }
    const toks = rest.split(/([,~:])/); const hits = []; let mot = [];
    for (let i = 0; i < toks.length; i += 2) {
      let t = toks[i].trim(); const sep = i ? toks[i - 1] : ',';
      if (!t) return { err: `empty token in '${n}'` };
      const sub = /^([A-Za-z_]+)\.(.+)$/.exec(t); let sp = null; if (sub && !DIR.test(sub[1])) { sp = sub[1]; t = sub[2]; }
      if (DIR.test(t)) { mot.push(t); continue; }
      const ch = /^charge_(b|d|db|d\/b|u|f)$/i.exec(t); if (ch) { mot.push('CH:' + ({ db: 'd/b' }[ch[1].toLowerCase()] || ch[1].toLowerCase())); continue; } // hold the charge 48f
      if (MOT[t]) { mot.push(...MOT[t]); continue; } // named motion as its own step ('hcb,f+1', 'qcf,qcf+1')
      const hm = /^(?:(qcf|qcb|hcf|hcb|dp|[udfbnUDFBN](?:\/[udfbUDFB])?)\+)?([1-4](?:\+[1-4])*|S|P\+K)(\*)?$/.exec(t);
      if (!hm) return { err: `token '${t}' is not a stick/button input` };
      let dirs = mot; mot = []; let last = hm[1] || null;
      if (last && MOT[last]) { dirs = dirs.concat(MOT[last].slice(0, -1)); last = MOT[last].slice(-1)[0]; }
      hits.push({ sep, sub: sp, motion: dirs, dir: last, btn: hm[2] === 'P+K' ? ['G'] : hm[2].split('+'), hold: !!hm[3] });
    }
    if (mot.length && !hits.length) return { motionOnly: mot, pre };
    // trailing bare stick step ('f+4,u', 'f+3,d/f'): a direction-only string follow-up
    if (mot.length) for (const d of mot) hits.push({ sep: ',', sub: null, motion: [], dir: d, btn: [], hold: false, dirOnly: true });
    return { pre, hits };
  }
  function setup(pre, f) {
    if (!pre) return 'neutral';
    const o = g.p2;
    switch (pre) {
      case 'FC': setDir('d'); step(20); return 'held d (full crouch)';
      case 'WS': setDir('d'); step(20); setDir('n'); step(2); return 'crouch then release (while standing)';
      case 'SS': f.trySidestep(-1); step(12); return 'sidestep';
      case 'BT': f.stance = 'BT'; f.stanceT = 0; return 'back turned';
      case 'R': case 'RD': f.hp = f.maxHp * 0.2; return 'rage (hp 20%)';
      case 'UB': return 'urge available';
      case 'US': f._urgeOn = true; f._urgeT = 5; f._urgePips = 3; return 'soul urge on';
      case 'SPIRIT': f._nearObject = true; return 'near object';
      case 'SOUL9': f._soulReleaseReady = true; return 'soul release ready';
      case 'REIHOU': o._rageActive = true; return 'opponent raging';
      case 'SEAL': o._rageUsed = true; o.hp = o.maxHp * 0.18; g.finalRound = true; return 'final round, opp 18%, rage spent';
      case 'KESSHOU': o._rageUsed = true; o.hp = o.maxHp * 0.12; return 'opp 12%, rage spent';
      default: f.stance = pre; f.stanceT = 0; return `stance ${pre}`;
    }
  }
  function pressHit(h, f, out, crouch) {
    if (h.sub && h.sub !== 'H') setup(h.sub, f);
    if (h.dirOnly) { for (let k = 0; k < 40 && g._hitStop > 0; k++) step(1, out); setDir('n'); step(2, out); setDir(h.dir); for (let k = 0; k < 40 && g._hitStop > 0; k++) step(1, out); step(4, out); setDir('n'); step(1, out); return; }
    const cap = (d) => /[A-Z]/.test(d);
    for (let i = 0; i < h.motion.length; i++) { const d = h.motion[i];
      if (d.startsWith('CH:')) { setDir(d.slice(3)); step(48, out); continue; }
      if (i && h.motion[i - 1].toLowerCase() === d.toLowerCase()) { setDir('n'); step(2, out); }
      setDir(d); step(cap(d) && d.toLowerCase() !== 'n' ? 8 : 3, out); }
    if (h.dir) { const prev = h.motion[h.motion.length - 1];
      if (prev && prev.toLowerCase() === h.dir.toLowerCase()) { setDir('n'); step(2, out); }
      setDir(h.dir); step(cap(h.dir) ? 12 : 2, out); }
    else if (h.motion.length) { setDir('n'); step(1, out); }
    else setDir(crouch ? 'd' : 'n');
    key(h.btn, 'keydown'); step(h.hold ? 24 : 1, out); key(h.btn, 'keyup');
  }
  // Chain throws: 'AB1.1,1+2' is entered during the throw that opens stage AB1 ('Arm Breaker (AB1)').
  function stageParent(pre) {
    if (!pre || !MS.throwStageTag) return null; const M = (MS.playedMoveset(g.p1.char.id) || {}).moves || {};
    const VAR = /~t\d+\.[a-z0-9_]+(\.\d+)?$/i; // a T7/T8 copy is equipped on its base input
    return Object.keys(M).find((k) => M[k] && M[k].move_class === 'throw' && !k.startsWith(pre + '.') && MS.throwStageTag(M[k].name) === pre && !parse(k.replace(VAR, '')).err) || null;
  }
  function stageInput(k) { const b = k.replace(/~t\d+\.[a-z0-9_]+(\.\d+)?$/i, ''); if (b !== k) MS.setLoadoutSlot(g.p1.char.id, b, k); return b; }
  function runStage(f, P, out) {
    const par = stageParent(P.pre), PP = parse(stageInput(par)); PP.key = par;
    if (PP.pre && stageParent(PP.pre)) runStage(f, PP, out); else { setup(PP.pre, f); run(f, PP, out); }
    for (let k = 0; k < 400 && !((f.attackName === par || MS.resolveMoveKey(g.p1.char.id, f.attackName) === par) && /throw/.test(f.state)); k++) step(1, out);
    for (const h of P.hits) { step(6, out); key(h.btn, 'keydown'); step(1, out); key(h.btn, 'keyup'); }
    for (let k = 0; k < 600 && /throw/.test(f.state) && f.attackName !== P.key; k++) step(1, out);
  }
  function run(f, P, out) {
    for (let i = 0; i < P.hits.length; i++) {
      const h = P.hits[i];
      if (i) step(h.sep === '~' ? 2 : h.sep === ':' ? 6 : 9, out);
      // A throw's follow-up ('2+4,2') is entered once the throw has grabbed, as played.
      if (i && f.attack && (f.attack.isGrab || f.attack.throw || f.attack.move_class === 'throw')) {
        for (let k = 0; k < 90 && f.state === 'attack'; k++) step(1, out);
        if (/throw/.test(f.state)) step(6, out); }
      pressHit(h, f, out, P.pre === 'FC' && i === 0);
    }
    setDir('n');
  }
  // T3 row command ('6/9+LP', 'LK+RK', '2+RP') -> Tekken notation ('f+1', '3+4', 'd+2').
  const NUM = { 6: 'f', 4: 'b', 2: 'd', 8: 'u', 3: 'd/f', 1: 'd/b', 9: 'u/f', 7: 'u/b' }, BTN = { LP: '1', RP: '2', LK: '3', RK: '4' };
  function t3cmd(c) { if (!c) return null; const parts = String(c).split('+'); let dir = ''; const b = [];
    for (const p of parts) { if (BTN[p]) b.push(BTN[p]); else if (/^[1-9](\/[1-9])?$/.test(p) && NUM[p[0]]) dir = NUM[p[0]]; else return null; }
    return b.length ? (dir ? dir + '+' : '') + b.sort().join('+') : null; }
  // Play the state a T3 branch condition tests (t3-conditions.js) right before the press.
  function oppAttack(o, want) { // opponent starts an attack of level `want` ('high'|'mid'|'low'|null)
    for (const n of ['1', '2', 'd+4', 'd+3', 'd/f+1', 'f+2', '3', '4', 'd/f+2', 'd+1']) {
      o._enter('idle'); o.attack = null; if (!o.tryAttack(n) || o.state !== 'attack') continue;
      const w = o.attack.hitWord ?? 0x217, hl = String(o.attack.hitLevel || '').toLowerCase();
      const lv = ((w & 7) === 4 || /^h/.test(hl)) ? 'high' : (((w & 0x18) === 0x08 && (w & 7) === 7) || /^l/.test(hl)) ? 'low' : 'mid';
      if (!want || want === lv || (want === 'hm' && lv !== 'low')) return n; }
    o._enter('idle'); o.attack = null; return null; }
  function contactFirst(f, o, guard) { // play a jab that connects (or is guarded) right before the row
    if (guard) o._enter('block');
    f.root.position.x = o.root.position.x - 0.75; f.tryAttack('1');
    for (let i = 0; i < 40 && !(f._t3Contact && f._clock - f._t3Contact.t < 0.1); i++) step(1);
    for (let i = 0; i < 90 && (f.state !== 'idle' || o.state !== 'idle'); i++) step(1);
    o.vx = 0; f.vx = 0;
    f.root.position.x = o.root.position.x - Math.min(condGap, 0.75); // step back in after the pushback
    return (f._t3Contact ? (f._t3Contact.guarded ? 'jab guarded' : 'jab connected') : 'jab never connected') + ` @${(o.root.position.x - f.root.position.x).toFixed(2)}m`; }
  let condGap = 1.1;
  function condSetup(c, f, o) {
    const back = () => { f.stance = 'BT'; f.stanceT = 9; };
    const swap = () => { const x = f.root.position.x; f.root.position.x = o.root.position.x; o.root.position.x = x; f.facing = -1; o.facing = 1; };
    if (c >= 2 && c <= 0x17) { const code = c <= 0x13 ? c : [2, 3, 4, 5][c - 0x14];
      const r = contactFirst(f, o); o._enter('idle'); o.attack = null; o.stun = 0;
      // A throw situation is positional, not a string: let the jab's 500 ms string window lapse
      // (as it would before a player walks into the situation) so the press reads the situation row, not '1,1'.
      f._stringGraceUntil = 0; f._queuedNext = null; f._queuedAfter = null; if (f.tekken) f.tekken._strPending = null;
      const q = (code - 2) % 4, base = code >= 18 ? 18 : code >= 14 ? 14 : code >= 10 ? 10 : code >= 6 ? 6 : 2;
      if (base === 6) o._enter('crouch'); if (base >= 10 && base < 18) { o._enter('knockdown'); o.onGround = true; o.stun = 5; o._faceDown = base === 14; }
      if (base === 18) { back(); if (code === 19) o.facing = 1; return r + ' · own back turned'; }
      const qq = [0, 2, 1, 3][q]; // code offset -> opponent quadrant (0 front, 1/3 sides, 2 back)
      if (qq === 2) o.facing = 1; if (qq === 1 || qq === 3) { o._enter('sidestep'); o.ssDir = qq === 1 ? 1 : -1; }
      return `${r} · situation ${code}`; }
    switch (c) {
      case 1: case 0x1A: return contactFirst(f, o);
      case 0x1B: return contactFirst(f, o, true);
      case 0x1C: f.root.position.x = o.root.position.x - 3; f.tryAttack('1'); /* the press is buffered: wait for the jab to start, then to recover */ for (let i = 0; i < 20 && f.state !== 'attack'; i++) step(1); for (let i = 0; i < 90 && f.state === 'attack'; i++) step(1); /* past the 500 ms string grace (else the press is the jab's own 1,1 string), inside the 1.5 s whiff window */ step(36); f.root.position.x = o.root.position.x - 1.1; return 'jab whiffed';
      case 0x18: case 0x33: case 0x34: f.root.position.x = o.root.position.x - 0.7; return 'close';
      case 0x19: f.root.position.x = o.root.position.x - 2.0; return 'far';
      case 0x1E: case 0x1F: case 0x45: case 0x4A: case 0x4B: case 0x47: return 'opponent attacking ' + oppAttack(o, c === 0x47 ? 'mid' : null);
      case 0x46: case 0x30: return 'opponent high ' + oppAttack(o, 'high');
      case 0x48: return 'opponent low ' + oppAttack(o, 'low');
      case 0x49: return 'opponent high/mid ' + oppAttack(o, 'hm');
      case 0x20: { const n = oppAttack(o, null); o.stance = 'FC'; return 'opponent attacking from crouch ' + n; }
      case 0x23: o._enter('crouch'); return 'opponent crouching';
      case 0x35: case 0x37: o._enter('knockdown'); o.onGround = true; o.stun = 5; return 'opponent down';
      case 0x38: o._enter('knockdown'); o.onGround = true; o.stun = 5; back(); return 'opponent down, own back turned';
      case 0x24: case 0x25: case 0x26: case 0x2A: case 0x40: back(); return 'own back turned';
      case 0x41: swap(); back(); return 'right side, own back turned';
      case 0x3F: swap(); return 'right side';
      case 0x28: case 0x29: f.trySidestep(c === 0x28 ? 1 : -1); step(10); return 'own sidestep';
      case 0x2C: case 0x2D: o.trySidestep(c === 0x2C ? 1 : -1); step(2); return 'opponent sidestep';
      case 0x2E: o.facing = 1; return 'opponent back turned';
      case 0x32: f._risingT = 0.4; return 'own rising';
      case 0x39: o.lastCounterHit = true; return 'opponent took a counter hit';
      case 0x43: f._rageActive = true; return 'power on (rage)';
      default: return 'neutral';
    }
  }
  /* KOF XV system rows (fighter.js KOF / _systemPress / trySystemMotion): each is checked
     against its system's rule, not just "a move fired". */
  const sysCheck = (m, sr) => {
    const f = g.p1, o = g.p2, K = f.constructor.KOF || window.__KOF; const out = [];
    const fires = (o2) => o2.some((fr) => fr.p1.an && (fr.p1.an === m.key || MS.resolveMoveKey(f.char.id, fr.p1.an) === m.key));
    const press = (n) => { const P = parse(n); run(f, P, out); };
    const res = (ok, why, how) => ({ key: m.key, input: sr.input, via: 'KOF system: ' + sr.sys, setup: how, ok, why, fired: [...new Set(out.map((x) => x.p1.an).filter(Boolean))] });
    reset(1.1); f.meter = 100;
    if (sr.sys === 'dash' || sr.sys === 'backdash' || sr.sys === 'roll') {
      const d = sr.input[0], x0 = f.root.position.x; let inv = 0;
      setDir(d); step(3, out); setDir('n'); step(3, out); setDir(d); step(2, out); setDir('n');
      for (let i = 0; i < 40; i++) { step(1, out); if (f.invuln > 0 && f.attackName === m.key) inv++; }
      const dx = (f.root.position.x - x0) * f.facing; const dirOk = d === 'f' ? dx > 0.3 : dx < -0.3;
      if (!fires(out)) return res(false, `double tap ${d},${d} did not start '${m.key}'`, 'neutral double tap');
      if (!dirOk) return res(false, `moved ${dx.toFixed(2)} m, wrong way`, 'neutral double tap');
      if (sr.sys === 'roll' && inv < 20) return res(false, `roll invulnerable only ${inv}f (KOF XV: 24f)`, 'neutral double tap');
      return res(true, '', `double tap ${d},${d} · moved ${dx.toFixed(2)} m` + (sr.sys === 'roll' ? ` · invulnerable ${inv}f` : ''));
    }
    if (sr.sys === 'guard') {
      press(sr.input); step(30, out);
      if (fires(out)) return res(false, 'guard cancel fired from neutral (KOF: blockstun only)', 'neutral');
      reset(1.1); out.length = 0; f.meter = 100; g.input.held.block = true; step(2); f.stun = 0.3; const m0 = f.meter;
      try { press(sr.input); step(40, out); } finally { g.input.held.block = false; }
      if (!fires(out)) return res(false, 'did not fire from blockstun', 'blockstun');
      const sg = (MS.playedMoveset(f.char.id).moves[m.key] || {}).soulGain || 0;
      if (!(m0 - f.meter + sg >= 25 - 1e-6)) return res(false, `cost ${m0 - f.meter + sg} souls, not 1 stock (25)`, 'blockstun');
      return res(true, '', 'neutral: no fire · blockstun: fired, 1 stock spent');
    }
    if (sr.sys === 'max') {
      f.meter = 0; press(sr.input); step(40, out);
      if (f._maxT > 0) return res(false, 'MAX started with an empty gauge', 'meter 0');
      reset(1.1); out.length = 0; f.meter = 100; press(sr.input); step(2, out);
      const t0 = f._maxT || 0; step(60, out); const t1 = f._maxT || 0;
      if (!(t0 > 0)) return res(false, 'MAX timer did not start', 'meter 100');
      if (!(t1 < t0 - 0.5)) return res(false, `MAX timer not running (${t0} -> ${t1})`, 'meter 100');
      const sgm = (MS.playedMoveset(f.char.id).moves[m.key] || {}).soulGain || 0;
      if (!(f.meter <= 50 + sgm + 1e-6)) return res(false, `MAX did not spend 2 stocks (meter ${f.meter})`, 'meter 100');
      return res(true, '', `meter 0: refused · meter 100: 2 stocks spent, timer ${t0.toFixed(2)} s -> ${t1.toFixed(2)} s after 1 s`);
    }
    if (sr.sys === 'taunt') {
      f._urgeUsed = true; press(sr.input); let n = 0; for (let i = 0; i < 90; i++) { step(1, out); if (f.state === 'attack' && f.attackName && MS.resolveMoveKey(f.char.id, f.attackName) === m.key) n++; }
      if (!fires(out)) return res(false, 'taunt did not fire', 'neutral');
      if (n < 46) return res(false, `taunt committed only ${n}f (KOF XV: 49f)`, 'neutral');
      return res(true, '', `fired · committed ${n}f`);
    }
    if (sr.sys === 'throw_escape') {
      press(sr.input); step(30, out);
      if (fires(out)) return res(false, 'throw escape fired as a move in neutral', 'neutral');
      reset(0.7); out.length = 0; o.tryAttack('1+3');
      for (let i = 0; i < 30 && f.state !== 'thrown'; i++) step(1, out);
      if (f.state !== 'thrown') return res(null, 'n/a: opponent throw did not grab', 'opponent 1+3');
      const ok = f.tryThrowBreak(sr.input);
      return ok ? res(true, '', 'neutral: no fire · thrown: escaped in window') : res(false, 'escape input did not break the throw', 'thrown');
    }
    return res(false, 'unknown system ' + sr.sys, '');
  };
  const sweepOne = (m, gap = 1.1) => {
    // States the game does not have (checked in fighter.js / game.js 2026-10-28): no running
    // state (WR), no face-up / face-down ground orientation moves, no tackle mount, no jump-landing
    // move window. Those rows are n/a WITH the missing state named, never a pass.
    { const t = `${m.key} ${m.input || ''}`; const NA = [[/\bWR\b/, 'running (WR)'], [/Face (Up|Down)|Roll(ing)? Forward/i, 'face-up/face-down ground'],
        [/During Tackle/i, 'tackle mount'], [/Upon Landing/i, 'jump-landing window']];
      for (const [re, st] of NA) if (re.test(t)) return { key: m.key, input: m.input, ok: null, why: `n/a: game has no ${st} state`, via: 'not wired' }; }
    const f = g.p1, o = g.p2, id = f.char.id, ms = MS.playedMoveset(id) || {}; const mv = (ms.moves || {})[m.key] || {};
    { const sr = MS.systemRows && MS.systemRows(id).find((r) => r.key === m.key); if (sr) return sysCheck(m, sr); }
    // T3 branch-condition rows (gen-movesets-t3.py t3_condition, decoded in game/js/t3-conditions.js):
    // the row fires only while its condition holds, so the condition's state is played first.
    const cond = mv.t3_condition ?? null;
    if (cond === 0x2F) return { key: m.key, input: m.input, ok: null, why: 'n/a: T3 condition 0x2F is "never" in the original game (the row cannot fire there either)', via: 'not wired' };
    if (cond === 0x3D) return { key: m.key, input: m.input, ok: null, why: 'n/a: T3 condition 0x3D fires only from the own-KO collapse (health 0), never from player input, in the original as here', via: 'not wired' };
    // A move on its own notation is pressed as-is; an alternate on an input another move owns
    // is equipped on that input through the loadout (what the moveset editor writes), pressed,
    // then the loadout entry is removed.
    let notation = m.key, via = 'own input';
    // close/far normals and stance spin variants (movesets.js _variant) fire on the plain input
    // from the fight context: close within MS.CLOSE_RANGE, far beyond it, spins after N real
    // stance entries. A base row sharing that input is what the editor equips there.
    const V = ms._variants || {}; let vrow = null;
    for (const [n, list] of Object.entries(V)) { const h = list.find((x) => x.key === m.key); if (h) { vrow = { note: n, key: h.key, kind: h.kind, spinN: h.n }; break; } }
    const vBase = !vrow && V[m.key] && !(MS.getLoadout(id) || {})[m.key];
    const alias = MS.legacyAlias && MS.legacyAlias(m.key);
    const ok = (n) => n && !parse(n).err && !parse(n).motionOnly;
    // Donor-bank moves ('donor.kronos.3+4 (cyclone1)', 'n+1~donor.kronos.2') belong to another
    // fighter's bank: the moveset editor equips them on their base input through the loadout.
    const DON = /^donor\.[a-z0-9-]+\.(.+)$/i.exec(m.key) || /^(.+)~donor\.[a-z0-9-]+(?:\.\d+)?$/i.exec(m.key);
    const donBase = DON && (MS.canonNotation || ((x) => x))(DON[1]);
    if (DON && ok(donBase)) { notation = donBase; via = 'equipped via moveset loadout'; }
    else if (MS.canonNotation && parse(m.key).err && MS.canonNotation(m.key) !== m.key && !parse(MS.canonNotation(m.key)).err && MS.resolveMoveKey(id, MS.canonNotation(m.key)) === m.key) { notation = MS.canonNotation(m.key); via = 'canonical spelling'; }
    else if (parse(m.key).err && MS.t3CommandNotations && MS.t3CommandNotations(mv.t3_command).some((c) => ok(c) && MS.resolveMoveKey(id, c) === m.key)) {
      notation = MS.t3CommandNotations(mv.t3_command).find((c) => ok(c) && MS.resolveMoveKey(id, c) === m.key); via = `T3 source command ${mv.t3_command}`; }
    else if (alias && parse(m.key).err && MS.resolveMoveKey(id, alias) === m.key) { notation = alias; via = 'legacy P/K alias'; }
    else if (vrow && ok(vrow.note)) { notation = vrow.note; via = vrow.kind === 'spins' ? `stance spin variant (${vrow.note} after ${vrow.spinN} stance entries)` : `${vrow.kind} normal by distance`; if (vrow.kind === 'close') gap = Math.min(gap, MS.CLOSE_RANGE - 0.3); else if (vrow.kind === 'far') gap = Math.max(gap, MS.CLOSE_RANGE + 0.05); }
    else if (vBase) { via = 'equipped via moveset loadout'; }
    else if (!m.slotted || !parse(m.key).hits) {
      // the editor equips a move on one of its input_slots (or its legacy alias / own input)
      const cn = MS.canonNotation || ((x) => x);
      const cands = [alias, ...(mv.input_slots || []), m.input, cn(m.input), cn(m.key), t3cmd(mv.t3_command), ...(MS.t3CommandNotations ? MS.t3CommandNotations(mv.t3_command) : [])].filter(ok);
      notation = cands[0] || [cn(m.input), cn(m.key)].find((c) => c && !parse(c).err) || m.input; via = 'equipped via moveset loadout'; } // a movement-only row in FGC spelling ('f,n,d,df') reads as movement
    const P = parse(notation);
    if (P.err) return { key: m.key, input: notation, ok: false, why: 'unparsed: ' + P.err, via };
    if (P.motionOnly) return { key: m.key, input: notation, ok: null, why: 'movement input (no button)', via };
    // a back-turned condition row is equipped on the back-turned input (BT.<input>), where the
    // fighter's back-turned press resolves — exactly what the editor's BT slot writes
    if (via === 'equipped via moveset loadout' && [0x24, 0x25, 0x26, 0x2A, 0x38, 0x40, 0x41, 18, 19].includes(cond) && !/^BT\./.test(notation)) notation = 'BT.' + notation;
    if (via === 'equipped via moveset loadout') MS.setLoadoutSlot(id, notation, m.key);
    try {
      reset(gap);
      // neutral 2+3 is the Urge Burst while urge is live (T8 Heat); the fighter's own 2+3 is tested with urge spent
      const urgeSpent = /^2\+3(\D|$)/.test(notation) && !/^U[BS]\./.test(m.key); if (urgeSpent) f._urgeUsed = true;
      const stg = stageParent(P.pre); if (stg) P.key = notation;
      let how = (stg ? `chain throw: during ${stg}` : (setup(P.pre, f) || '')) + (urgeSpent ? ' · urge spent' : '');
      // decoded T3 hit word: a row that cannot hit a STANDING foe (ground hits, crouch-only
      // rows) is tested against the posture it does hit — never forced through a standing foe
      { const RM = MS.getMove ? MS.getMove(id, notation) : null; const W = (RM && RM.hitWord) ?? mv.hitWord ?? (f.constructor.defaultWord ? f.constructor.defaultWord(RM || mv) : 2);
        if ((mv.damage || 0) > 0 && !mv.throw && !(W & 2)) {
          if (W & 1) { o._enter('crouch'); how += ' · foe crouching (row hits crouchers only)'; }
          else if (W & 4) { o._enter('knockdown'); o.onGround = true; o.stun = 5; how += ' · foe downed (ground hit)'; } } }
      if (vrow && vrow.kind === 'spins') { // real stance re-entries: fire the stance's entry move N times
        const st = vrow.note.split(/[.,\s]/)[0]; f.stance = null; f.stanceT = 0; f._stanceSpins = 0; // spins come only from the real entries below
        const entry = Object.keys(ms.stance_after || {}).find((k) => ms.stance_after[k] === st && !/^[A-Z]+\./.test(k));
        for (let i = 0; entry && i < vrow.spinN; i++) { f.tryAttack(entry); for (let w = 0; w < 120 && f.state === 'attack'; w++) step(1); }
        how += ` · ${entry} ×${vrow.spinN} → ${f.stance} spins=${f._stanceSpins}`; }
      if (vrow && vrow.kind !== 'spins') how += ` · range ${f._inputCtx().dist?.toFixed(2)} m (close ≤ ${MS.CLOSE_RANGE} m)`;
      condGap = gap;
      if (cond != null) { const r = condSetup(cond, f, o, notation); how += ' · T3 cond 0x' + cond.toString(16) + ': ' + r + (T3.t3ConditionHolds(cond, f, o, notation) ? ' (holds)' : ' (NOT holding)'); }
      const out = []; const hp0 = o.hp;
      if (stg) runStage(f, P, out); else run(f, P, out);
      for (let k = 0; stg && k < 400 && /throw/.test(f.state); k++) step(1, out);
      const tail = Math.min(150, Math.round(((mv.startup || 0.2) + (mv.active || 0.05) + (mv.recovery || 0.5)) * 60) + 40);
      // Queued string hits fire after hit-stop; drain them before the tail (a connecting
      // long string spends its fixed tail inside hit-stop and dropped its last hits).
      for (let k = 0; k < 360 && (f.state === 'attack' || f._queuedNext); k++) step(1, out);
      step(tail, out);
      const x0 = out.length ? Math.abs(out[0].p2.x - out[0].p1.x) : null;
      const fired = []; let last = null;
      for (const fr of out) { const a = (fr.p1.st === 'attack' || /throw/.test(fr.p1.st)) ? fr.p1.an : null; if (a && a !== last) fired.push(a); last = a; }
      const keys = fired.map((n) => MS.resolveMoveKey(id, n) || n);
      // A T3 condition row passes when it is the attacking move (moveKey), or when the fired attack
      // resolves to this row AND plays this row's own T3 source row (bank:row, the animation it resolves to) - a base move that only
      // shares the notation (different source row) still fails.
      const rowRef = mv.t3_row != null ? (mv.t3_source || ms.t3_source) + ':' + mv.t3_row : null;
      const atk = (fr) => fr.p1.st === 'attack' || /throw/.test(fr.p1.st);
      const firedIt = cond != null ? out.some((fr) => atk(fr) && (fr.p1.mk === m.key
        || (rowRef && fr.p1.ar === rowRef && MS.resolveMoveKey(id, fr.p1.an) === m.key))) : keys.includes(m.key);
      const react = [...new Set(out.map((fr) => fr.p2.st))].filter((x) => x !== 'idle' && x !== 'walk');
      const dmg = Math.round((hp0 - Math.min(...out.map((fr) => fr.p2.hp))) * 10) / 10;
      const connected = dmg > 0 || react.some((x) => REACT.test(x));
      const needHit = (mv.damage || 0) > 0;
      const isThrow = !!(mv.throw || mv.isGrab || mv.move_class === 'throw');
      let throwOk = null;
      if (isThrow && firedIt) { const p1s = new Set(out.map((x) => x.p1.st)), p2s = new Set(out.map((x) => x.p2.st));
        throwOk = p1s.has('throwExec') && p2s.has('thrownExec') && out.filter((x) => x.p2.st === 'thrownExec').every((x) => x.p2.clip); }
      const nHits = P.hits.length;
      // a string whose opening step has no standalone move fires as one move (opener path)
      /* opening step through the first button: 'f,n,1' of 'f,n,1,2' */ const firstStep = (/^(?:[^,~:1-4]*[,~:])*?[^,~:]*?[1-4][^,~:]*/.exec(notation) || [notation.split(/[,~:]/)[0]])[0]; const openerOnly = !MS.resolveMoveKey(id, firstStep);
      const strOk = nHits > 1 ? (fired.length >= Math.min(nHits, 2) || openerOnly) && firedIt : true;
      const ok = firedIt && strOk && (!needHit || connected) && throwOk !== false;
      const why = !firedIt ? `fired ${JSON.stringify(fired)} (keys ${JSON.stringify(keys)}) not '${m.key}'` : !strOk ? `string fired ${JSON.stringify(fired)}` :
        (needHit && !connected) ? 'fired but did not connect' + missCause(out, x0) : throwOk === false ? 'throw did not reach exec with victim clip' : '';
      return { trace: m.trace ? out.filter((_, i) => i % 3 === 0) : undefined, key: m.key, input: notation, via, setup: how, ok, why, fired, dmg, react: react.slice(0, 6), launch: out.some((fr) => fr.p2.y > 0.35), isThrow, throwOk,
        tClip: [...new Set(out.filter((x) => /throw/.test(x.p1.st)).map((x) => x.p1.clip))].slice(0, 3),
        vClip: [...new Set(out.filter((x) => /thrown/.test(x.p2.st)).map((x) => x.p2.clip))].slice(0, 3) };
    } finally { if (via === 'equipped via moveset loadout') MS.setLoadoutSlot(id, notation, null); }
  };
  // A whiff at the default 1.1 m spacing is retried at closer ranges (short-reach jabs/elbows
  // connect point-blank in a real fight); the row keeps the gap it connected at.
  /* Why a fired strike did not connect: never reached its active frames (active window), was
     active only while the opponent's posture rejects it (posture: highs over a croucher, lows
     vs airborne, down-only words), or was active out of range - split by whether the attacker's
     root moved away from its start spacing during the move (root motion) or not (range). */
  function missCause(out, x0) {
    const act = out.filter((fr) => fr.p1.ph === 'active');
    if (!act.length) return ' (active window: never active)';
    if (act.every((fr) => fr.p1.cb === false)) return ' (posture: opponent posture rejects the hit word)';
    const dx = Math.min(...act.map((fr) => Math.abs(fr.p2.x - fr.p1.x)));
    if (x0 != null && dx > x0 + 0.15) return ` (root motion: active at ${dx.toFixed(2)} m, started ${x0.toFixed(2)} m)`;
    if (Math.abs(act[0].p2.y - act[0].p1.y) > 0.6) return ` (height: opponent ${act[0].p2.y > act[0].p1.y ? 'above' : 'below'} during active)`;
    return ` (range: closest ${dx.toFixed(2)} m during ${act.length} active frames)`;
  }
  window.__sweepMove = (m) => { let r = sweepOne(m, 1.1);
    for (const gp of [0.8, 0.55]) { if (r.ok || !/^fired but did not connect/.test(r.why)) break; const r2 = sweepOne(m, gp); r2.gap = gp; if (r2.ok || !/^fired but did not connect/.test(r2.why)) r = r2; }
    return r; };
  // Juggle: replay a launcher that lifted the opponent, then a 1 while they are airborne must hit.
  window.__juggle = (r, gap = 1.1) => {
    const f = g.p1, id = f.char.id; const P = parse(r.input);
    if (r.via === 'equipped via moveset loadout') MS.setLoadoutSlot(id, r.input, r.key);
    try {
      reset(gap); setup(P.pre, f); run(f, P, null);
      let k = 0; while (k++ < 90 && !(g.p2.root.position.y > 0.35)) step(1);
      if (!(g.p2.root.position.y > 0.35)) return { key: r.key, ok: null, why: 'no lift on replay' };
      let hit = false; const dbg = r.trace ? [] : null;
      for (let t = 0; t < 8 && !hit; t++) {
        // the follow-up 1 must be a fresh move: let the launcher (and any queued string hits) finish
        for (let w = 0; w < 300 && (g.p1.state === 'attack' || g.p1._queuedNext); w++) step(1);
        const hp = g.p2.hp;
        // aim at where the opponent will be when the jab's active frames arrive: its ballistic
        // path (fighter.js gravity 22 m/s²) clamped at its landing point, not a fixed spot
        { const o = g.p2, y = o.root.position.y, vy = o.vy || 0, G = 22;
          const tLand = (vy + Math.sqrt(vy * vy + 2 * G * Math.max(0, y))) / G;
          const J = MS.getMove ? MS.getMove(id, '1') : null; const tHit = ((J && J.startup) || 0.15) + 0.02;
          const t = Math.min(tHit, tLand); const px = o.root.position.x + (o.vx || 0) * t;
          g.p1.root.position.x = px - 0.85; g.p1.facing = 1; }
        const st0 = [g.p1.state, +(g.p2.root.position.x - g.p1.root.position.x).toFixed(2), +g.p2.root.position.y.toFixed(2), g.p2.state, +(g.p2.vx || 0).toFixed(2), +(g.p2.vy || 0).toFixed(2)];
        // the hit counts only if it lands while the opponent is still off the ground (a juggle),
        // not after it landed and stood up
        key(['1'], 'keydown'); step(1); key(['1'], 'keyup');
        let airHit = false; for (let q = 0; q < 18; q++) { const h0 = g.p2.hp, air = !g.p2.onGround || g.p2.root.position.y > 0.05; step(1); if (g.p2.hp < h0 && air) airHit = true; }
        if (dbg) dbg.push([...st0, '->', g.p1.attackName, g.p1._attackPhase, g.p1.hasHit, +(g.p2.root.position.y).toFixed(2), g.p2.state]);
        if (airHit) hit = true;
        if (g.p2.onGround && g.p2.root.position.y < 0.05) break;
      }
      return { key: r.key, ok: hit, why: hit ? '' : 'follow-up 1 never hit the airborne opponent', dbg: dbg || undefined };
    } finally { if (r.via === 'equipped via moveset loadout') MS.setLoadoutSlot(id, r.input, null); }
  };
  window.__moveList = () => { const id = g.p1.char.id, ms = MS.playedMoveset(id); const rows = [];
    for (const [k, mv] of Object.entries(ms.moves || {})) rows.push({ key: k, input: mv.input || k, slotted: MS.resolveMoveKey(id, k) === k });
    return rows; };
  window.__sw = { reset, step, setDir, key, parse }; // debug hooks
  window.__sweepReady = true;
})();
