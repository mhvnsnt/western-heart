// In-page half of moveset-sweep.e2e.mjs (evaluated in the game page after the fight starts).
(async () => {
  const MS = await import('./js/movesets.js');
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
  const s = (f) => ({ st: f.state, an: f.attackName, clip: f._t3current ? f._t3current.getClip().name : null,
    x: +f.root.position.x.toFixed(2), y: +f.root.position.y.toFixed(2), hp: f.hp });
  const step = (n, out) => { for (let i = 0; i < n; i++) { window.__vt += 1000 / 60;
    { const I = g.input; if (I._udDir && !I._udHeld && window.__vt - I._udT >= 200) { clearTimeout(I._udTimer); if (I._udDir === 'up') I.up = true; else I.down = true; I._udHeld = true; } } // input.js 200 ms u/d hold timer, on the sim clock
    if (g._hitStop > 0) g._hitStop -= 1 / 60; else g._update(1 / 60); if (out) out.push({ p1: s(g.p1), p2: s(g.p2) }); } };
  const reset = (gap) => {
    for (const k of [...held]) key(k, 'keyup');
    for (const f of [g.p1, g.p2]) { f.hp = f.maxHp || 100; f._enter('idle'); f.attack = null; f.attackName = null; f._throwPair = null;
      f.stance = null; f.stanceT = 0; f._risingT = 0; f.lockT = 0; f.lockMove = null; f.tekken.lastMove = null; f.tekken._strPath = null;
      f._stringGraceUntil = 0; f._queuedNext = null; f._queuedAfter = []; f._urgeOn = false; f._urgeT = 0; f._urgeUsed = false;
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
      const hm = /^(?:(qcf|qcb|hcf|hcb|dp|[udfbnUDFBN](?:\/[udfbUDFB])?)\+)?([1-4](?:\+[1-4])*|S|P\+K)(\*)?$/.exec(t);
      if (!hm) return { err: `token '${t}' is not a stick/button input` };
      let dirs = mot; mot = []; let last = hm[1] || null;
      if (last && MOT[last]) { dirs = dirs.concat(MOT[last].slice(0, -1)); last = MOT[last].slice(-1)[0]; }
      hits.push({ sep, sub: sp, motion: dirs, dir: last, btn: hm[2] === 'P+K' ? ['G'] : hm[2].split('+'), hold: !!hm[3] });
    }
    if (mot.length && !hits.length) return { motionOnly: mot, pre };
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
    const cap = (d) => /[A-Z]/.test(d);
    for (let i = 0; i < h.motion.length; i++) { const d = h.motion[i];
      if (i && h.motion[i - 1].toLowerCase() === d.toLowerCase()) { setDir('n'); step(2, out); }
      setDir(d); step(cap(d) && d.toLowerCase() !== 'n' ? 8 : 3, out); }
    if (h.dir) { const prev = h.motion[h.motion.length - 1];
      if (prev && prev.toLowerCase() === h.dir.toLowerCase()) { setDir('n'); step(2, out); }
      setDir(h.dir); step(cap(h.dir) ? 12 : 2, out); }
    else if (h.motion.length) { setDir('n'); step(1, out); }
    else setDir(crouch ? 'd' : 'n');
    key(h.btn, 'keydown'); step(h.hold ? 24 : 1, out); key(h.btn, 'keyup');
  }
  function run(f, P, out) {
    for (let i = 0; i < P.hits.length; i++) {
      const h = P.hits[i];
      if (i) step(h.sep === '~' ? 2 : h.sep === ':' ? 6 : 9, out);
      pressHit(h, f, out, P.pre === 'FC' && i === 0);
    }
    setDir('n');
  }
  // T3 row command ('6/9+LP', 'LK+RK', '2+RP') -> Tekken notation ('f+1', '3+4', 'd+2').
  const NUM = { 6: 'f', 4: 'b', 2: 'd', 8: 'u', 3: 'd/f', 1: 'd/b', 9: 'u/f', 7: 'u/b' }, BTN = { LP: '1', RP: '2', LK: '3', RK: '4' };
  function t3cmd(c) { if (!c) return null; const parts = String(c).split('+'); let dir = ''; const b = [];
    for (const p of parts) { if (BTN[p]) b.push(BTN[p]); else if (/^[1-9](\/[1-9])?$/.test(p) && NUM[p[0]]) dir = NUM[p[0]]; else return null; }
    return b.length ? (dir ? dir + '+' : '') + b.sort().join('+') : null; }
  const sweepOne = (m, gap = 1.1) => {
    const f = g.p1, o = g.p2, id = f.char.id, ms = MS.playedMoveset(id) || {}; const mv = (ms.moves || {})[m.key] || {};
    // A move on its own notation is pressed as-is; an alternate on an input another move owns
    // is equipped on that input through the loadout (what the moveset editor writes), pressed,
    // then the loadout entry is removed.
    let notation = m.key, via = 'own input';
    const alias = MS.legacyAlias && MS.legacyAlias(m.key);
    const ok = (n) => n && !parse(n).err && !parse(n).motionOnly;
    if (MS.canonNotation && parse(m.key).err && MS.canonNotation(m.key) !== m.key && ok(MS.canonNotation(m.key)) && MS.resolveMoveKey(id, MS.canonNotation(m.key)) === m.key) { notation = MS.canonNotation(m.key); via = 'canonical spelling'; }
    else if (alias && parse(m.key).err && MS.resolveMoveKey(id, alias) === m.key) { notation = alias; via = 'legacy P/K alias'; }
    else if (!m.slotted || !parse(m.key).hits) {
      // the editor equips a move on one of its input_slots (or its legacy alias / own input)
      const cn = MS.canonNotation || ((x) => x);
      const cands = [alias, ...(mv.input_slots || []), m.input, cn(m.input), cn(m.key), t3cmd(mv.t3_command)].filter(ok);
      notation = cands[0] || m.input; via = 'equipped via moveset loadout'; }
    const P = parse(notation);
    if (P.err) return { key: m.key, input: notation, ok: false, why: 'unparsed: ' + P.err, via };
    if (P.motionOnly) return { key: m.key, input: notation, ok: null, why: 'movement input (no button)', via };
    if (via === 'equipped via moveset loadout') MS.setLoadoutSlot(id, notation, m.key);
    try {
      reset(gap);
      // neutral 2+3 is the Urge Burst while urge is live (T8 Heat); the fighter's own 2+3 is tested with urge spent
      const urgeSpent = /^2\+3(\D|$)/.test(notation) && !/^U[BS]\./.test(m.key); if (urgeSpent) f._urgeUsed = true;
      const how = (setup(P.pre, f) || '') + (urgeSpent ? ' · urge spent' : ''); const out = []; const hp0 = o.hp;
      run(f, P, out);
      const tail = Math.min(150, Math.round(((mv.startup || 0.2) + (mv.active || 0.05) + (mv.recovery || 0.5)) * 60) + 40);
      step(tail, out);
      const fired = []; let last = null;
      for (const fr of out) { const a = (fr.p1.st === 'attack' || /throw/.test(fr.p1.st)) ? fr.p1.an : null; if (a && a !== last) fired.push(a); last = a; }
      const keys = fired.map((n) => MS.resolveMoveKey(id, n) || n);
      const firedIt = keys.includes(m.key);
      const react = [...new Set(out.map((fr) => fr.p2.st))].filter((x) => x !== 'idle' && x !== 'walk');
      const dmg = Math.round((hp0 - Math.min(...out.map((fr) => fr.p2.hp))) * 10) / 10;
      const connected = dmg > 0 || react.some((x) => REACT.test(x));
      const needHit = (mv.damage || 0) > 0;
      const isThrow = !!(mv.throw || mv.isGrab || mv.move_class === 'throw');
      let throwOk = null;
      if (isThrow && firedIt) { const p1s = new Set(out.map((x) => x.p1.st)), p2s = new Set(out.map((x) => x.p2.st));
        throwOk = p1s.has('throwExec') && p2s.has('thrownExec') && out.filter((x) => x.p2.st === 'thrownExec').every((x) => x.p2.clip); }
      const nHits = P.hits.length;
      const strOk = nHits > 1 ? fired.length >= Math.min(nHits, 2) && firedIt : true;
      const ok = firedIt && strOk && (!needHit || connected) && throwOk !== false;
      const why = !firedIt ? `fired ${JSON.stringify(fired)} (keys ${JSON.stringify(keys)}) not '${m.key}'` : !strOk ? `string fired ${JSON.stringify(fired)}` :
        (needHit && !connected) ? 'fired but did not connect' : throwOk === false ? 'throw did not reach exec with victim clip' : '';
      return { trace: m.trace ? out.filter((_, i) => i % 3 === 0) : undefined, key: m.key, input: notation, via, setup: how, ok, why, fired, dmg, react: react.slice(0, 6), launch: out.some((fr) => fr.p2.y > 0.35), isThrow, throwOk,
        tClip: [...new Set(out.filter((x) => /throw/.test(x.p1.st)).map((x) => x.p1.clip))].slice(0, 3),
        vClip: [...new Set(out.filter((x) => /thrown/.test(x.p2.st)).map((x) => x.p2.clip))].slice(0, 3) };
    } finally { if (via === 'equipped via moveset loadout') MS.setLoadoutSlot(id, notation, null); }
  };
  // A whiff at the default 1.1 m spacing is retried at closer ranges (short-reach jabs/elbows
  // connect point-blank in a real fight); the row keeps the gap it connected at.
  window.__sweepMove = (m) => { let r = sweepOne(m, 1.1);
    for (const gp of [0.8, 0.55]) { if (r.ok || r.why !== 'fired but did not connect') break; const r2 = sweepOne(m, gp); r2.gap = gp; if (r2.ok || r2.why !== 'fired but did not connect') r = r2; }
    return r; };
  // Juggle: replay a launcher that lifted the opponent, then a 1 while they are airborne must hit.
  window.__juggle = (r, gap = 1.1) => {
    const f = g.p1, id = f.char.id; const P = parse(r.input);
    if (r.via === 'equipped via moveset loadout') MS.setLoadoutSlot(id, r.input, r.key);
    try {
      reset(gap); setup(P.pre, f); run(f, P, null);
      let k = 0; while (k++ < 90 && !(g.p2.root.position.y > 0.35)) step(1);
      if (!(g.p2.root.position.y > 0.35)) return { key: r.key, ok: null, why: 'no lift on replay' };
      let hit = false;
      for (let t = 0; t < 8 && !hit; t++) {
        while (g.p1.state === 'attack' && k++ < 260) step(1);
        const hp = g.p2.hp;
        g.p1.root.position.x = g.p2.root.position.x - 0.85; g.p1.facing = 1;
        key(['1'], 'keydown'); step(1); key(['1'], 'keyup'); step(18);
        if (g.p2.hp < hp) hit = true;
        if (g.p2.onGround && g.p2.root.position.y < 0.05) break;
      }
      return { key: r.key, ok: hit, why: hit ? '' : 'follow-up 1 never hit the airborne opponent' };
    } finally { if (r.via === 'equipped via moveset loadout') MS.setLoadoutSlot(id, r.input, null); }
  };
  window.__moveList = () => { const id = g.p1.char.id, ms = MS.playedMoveset(id); const rows = [];
    for (const [k, mv] of Object.entries(ms.moves || {})) rows.push({ key: k, input: mv.input || k, slotted: MS.resolveMoveKey(id, k) === k });
    return rows; };
  window.__sw = { reset, step, setDir, key, parse }; // debug hooks
  window.__sweepReady = true;
})();
