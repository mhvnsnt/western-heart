  press(input, ctx = {}) {
    const ms = playedMoveset(this.fighterId);
    if (!ms || !ms.moves) return input; // no data — raw passthrough
    _prepare(ms);
    this.pendingStep = null; // V2 sets it when this press only typed a string step (nothing fires)
    if (inputResolverV2()) { const r = this._pressV2(input, ctx, ms); this._markStep(); return r; }
    return this._pressLegacy(input, ctx, ms);
  }

  /* INPUT RESOLVER V2 (owner t116u, 2026-10-23 — "presses give random moves, neutral 3 fires a
     crouching kick"). Deterministic Tekken priority from the stick ACTUALLY held at press time:
       0) Soul Urge / rage system moves (HEAT 2+3, rage drive 3+4)
       1) string continuation (the string tree, lane B 2026-10-24: _stringStep)
       2) for each state prefix, most specific first (combined prefixes, stance, R., RD., H., BT.,
          SS., FC. only while crouching, WS. only in the rising window): motion > held direction
          + button
       3) only then the plain button (tap-release spellings first), again most specific prefix first.
     So a held direction always beats a stance-neutral move, a neutral stick never reaches a
     directional / FC move (FC needs a real crouch), and no input ever picks a move at random.
     Rules: docs/input/INPUT-RESOLVER-V2.md. Old resolver: _pressLegacy, reachable with
     localStorage wh_input_resolver='legacy' or window.WH_INPUT_RESOLVER='legacy'.
     Tests: test/input-determinism.test.mjs, test/moveset-reachability.test.mjs (CI). */
  _pressV2(input, ctx, ms) {
    const has = (n) => (resolveMoveKey(this.fighterId, n) ? n : null);
    const dir = this.lastDir && this.lastDir !== 'n' ? this.lastDir : '';
    const withDir = dir ? `${dir}+${input}` : input;
    const holdDir = dir ? `${dir.toUpperCase()}+${input}` : null;
    const now = performance.now();
    // 0) Soul Urge (T8 Heat) reservation, restored from the legacy resolver (V2 had dropped it, so
    //    the HEAT button fired the fighter's ordinary 2+3): while the gauge is live, neutral 2+3 with
    //    no stance is the Urge Burst (fresh gauge) or the Urge Smash (urging). A directional / stance
    //    2+3 (H.d/f+2+3, H.BT.2+3) stays the fighter's own.
    if (input === '2+3' && (ctx.urgeOn || ctx.urgeAvailable) && !dir && !ctx.stance && !ctx.backturned) {
      const sys = has(ctx.urgeOn ? 'US.2+3' : 'UB.2+3');
      if (sys) return this._recordMove(sys);
    }
    const contOk = ctx.inMove !== undefined ? ctx.inMove : (now - this.lastMoveT < STRING_PENDING);
    // 1) String cursor: the notation typed so far — a pending partial string (a step that is not
    //    a standalone move) for STRING_PENDING ms, else the last move while it still plays.
    //    _stringStep walks the string tree (one press = one step, held-direction / plain fallback).
    const pendingOk = this._strPath && now - this._strPathT < STRING_PENDING;
    const bases = [];
    // BATCH: strip ~shadow suffixes here too (see continuation()) — a pending path or last move of
    // '1~t8.king' must also try '1' as its chain base. (lane B: only a merge-source suffix is
    // stripped — '4~3' is a real Tekken notation and must not fall back to '4'.)
    const strip = (b) => { const m = b ? MERGE_KEY.exec(b) : null; return m ? b.slice(0, m.index) : null; };
    if (pendingOk) { bases.push(this._strPath); const s = strip(this._strPath); if (s) bases.push(s); }
    if (this.lastMove && contOk) { bases.push(this.lastMove); const s = strip(this.lastMove); if (s) bases.push(s); }
    for (const base of bases) {
      const c = this._stringStep(base, input, ms, ctx);
      if (!c) continue;
      if (has(c)) return this._recordMove(c);
      this._strPath = c; this._strPathT = now; this.pendingStep = c; // step with no move of its own
      return null;
    }
    this._strPath = null;
    // Opening step of a string that has no standalone move ('BM.2' of 'BM.2,1,2,1', 'u/b+1' of
    // 'u/b+1,1'): remember it as the string path and keep resolving — the press still plays the
    // move this priority order gives without it (Tekken: the first hit of a string always plays),
    // and the next press continues the string. Nothing else resolves = the press only opened it.
    let opened = null;
    const opener = (c) => { if (!opened && ms._strKids && ms._strKids.has(c) && !has(c)) opened = c; return false; };
    const fire = (c) => { this._recordMove(c); if (opened) { this._strPath = opened; this._strPathT = now; this._strPathMove = c; } return c; };
    const prefixes = [];
    const active = new Set([ctx.stance, ctx.urgeOn && 'H', ctx.rage && 'R', ctx.backturned && 'BT',
      ctx.sidestep && 'SS', ctx.crouching && 'FC', ctx.rising && 'WS'].filter(Boolean));
    for (const c of ms._combos || []) if (c.toks.every(t => active.has(t))) prefixes.push(c.p);
    if (ctx.stance) prefixes.push(ctx.stance + '.');
    if (ctx.rage) prefixes.push('R.');
    // Rage lane (T7): the rage drive lives on 3+4 while raging (synthesized RD., rage.js) —
    // restored from the legacy resolver, V2 had dropped the prefix.
    if (ctx.rage) prefixes.push('RD.');
    // Soul Urge = T8 Heat (renamed): the moveset's Heat moves ('H.2', 'H.f+4,4') while urging.
    if (ctx.urgeOn) prefixes.push('H.');
    if (ctx.backturned) prefixes.push('BT.');
    if (ctx.sidestep) prefixes.push('SS.');
    if (ctx.crouching) prefixes.push('FC.');
    if (ctx.rising) prefixes.push('WS.');
    prefixes.push('');
    for (const p of prefixes) {
      // Final step HELD (>= MOTION_HOLD frames) prefers the capital spelling (f,f,F+3), a quick
      // final tap the lowercase one (f,f,f+3); each still falls back to the other. Same physical
      // input under two spellings: the T7/T8 move beats a merged T3 row (rank).
      const capFirst = this._heldFrames() >= MOTION_HOLD;
      const cap = (mo) => /[A-Z]/.test(mo.n.split(',').pop().split('+')[0]);
      const motions = ms._motions.slice().sort((a, b) => (b.plen - a.plen) || ((cap(b) === capFirst) - (cap(a) === capFirst)) || (a.rank - b.rank));
      for (const mo of motions) {
        if (mo.prefix !== p || mo.btn !== input) continue;
        // neutral-ending motions ('f,n,2') need the stick released; the rest need the last
        // step still held at the press (f,F+2 = f held).
        if (mo.neutral ? dir : dir !== mo.dirs[mo.dirs.length - 1]) continue;
        if (mo.opener) { if (this._motionHeldV2(mo)) opener(mo.n); continue; }
        if (this._motionHeldV2(mo) && has(mo.n)) return fire(mo.n);
      }
      if (dir) {
        // Held spelling ('D/F+2') when the direction has been held >= HOLD_FRAMES, tap otherwise.
        const held = this._heldFrames() >= HOLD_FRAMES;
        const order = held ? [p + holdDir, p + withDir] : [p + withDir, p + holdDir];
        // A held 'D/B+3' that only opens 'D/B+3,4,...' is remembered before the tap move plays.
        for (const c of order) { if (has(c)) return fire(c); opener(c); }
        for (const c of order) if (has(c + '*')) return fire(c + '*'); // hold-button spelling ('H.u/b+1+2*')
        // Crouching: holding down IS the crouch, so FC.1 is pressed with the stick at d / d/b /
        // d/f — it must not fall through to the standing d+1 of the next prefix. A crouch held at
        // d/f or d/b IS that direction held: the moveset's exact held spelling (D/F+1, D/B+2)
        // wins over FC.x when it exists, otherwise FC.x.
        if (p === 'FC.' && dir[0] === 'd') {
          if (dir !== 'd' && has(holdDir)) return fire(holdDir);
          for (const c of [p + input, p + input + '*']) if (has(c)) return fire(c);
          opener(p + input);
        }
      }
    }
    const taps = dir ? [] : this.tapSteps(input);
    for (const p of prefixes) {
      for (const c of taps) { if (has(p + c)) return fire(p + c); if (has(p + c + '*')) return fire(p + c + '*'); opener(p + c); } // tap-release 'd/f,4', 'f,n,4'
      if (has(p + input)) return fire(p + input);
      if (has(p + input + '*')) return fire(p + input + '*');
      if (!dir && has(p + 'n+' + input)) return fire(p + 'n+' + input); // neutral spelling ('n+3+4')
      opener(p + input); // stance chain opener ('SLEEPER.1' of 'SLEEPER.1,1,1+2')
    }
    if (opened) { this._strPath = opened; this._strPathT = now; this.pendingStep = opened; }
    return null;
  }

  /** One press further down the string from `base` (lane B, 2026-10-24): the child notation in
      the string tree this press types, or null. Tekken order: a motion step, then the direction
      as held (held/tap spelling by HOLD_FRAMES), then the plain button — a follow-up with no
      directional version still comes out while the stick is held — then a step that starts in
      the stance the move transitions to ('3+4,SNE.2'). Spellings of one physical base share
      their children; a direction-specific step under any spelling beats a plain fallback. */
  _stringStep(base, input, ms, ctx = {}) {
    const alias = (ms._physAlias && ms._physAlias.get(physKey(base))) || [];
    const bases = [base, ...alias.filter(x => x !== base)];
    for (const strict of [true, false]) {
      for (const b of bases) { const c = this._stepFrom(b, input, ms, ctx, strict); if (c) return c; }
    }
    return null;
  }
  _stepFrom(base, input, ms, ctx, strict = false) {
    const kids = ms._strKids && ms._strKids.get(base);
    if (!kids) return null;
    const dir = this.lastDir && this.lastDir !== 'n' ? this.lastDir : '';
    const L = base.length + 1;
    for (const c of kids) { // motion step ('b+2,f,F+1', 'd,d+1,qcb+1')
      const s = c.slice(L);
      if (!/,|^(qcf|qcb|hcf|hcb)\+/.test(s)) continue;
      const mo = parseMotion(s);
      if (!mo || mo.prefix || mo.btn !== input) continue;
      if (mo.neutral ? dir : dir !== mo.dirs[mo.dirs.length - 1]) continue;
      if (this._motionHeldV2(mo)) return c;
    }
    const steps = [];
    if (dir) {
      const tap = `${dir}+${input}`, hold = `${dir.toUpperCase()}+${input}`;
      steps.push(...(this._heldFrames() >= HOLD_FRAMES ? [hold, tap] : [tap, hold]));
    }
    if (!(strict && dir)) steps.push(input, input + '*');
    if (!dir) steps.unshift(...this.tapSteps(input)); // tap-release 'd,4' / 'f,n,4' / 'U/F,4': the player did tap it
    if (!dir) steps.push('n+' + input, 'n,' + input, 'n~' + input, 'N,' + input); // neutral spellings ('n+4', 'n,4')
    // Soul Urge on: the string's Heat step ('d/f+1,H.2') before the normal one.
    if (ctx.urgeOn) for (const s of steps) for (const sep of [',', '~', ':']) if (kids.has(`${base}${sep}H.${s}`)) return `${base}${sep}H.${s}`;
    // '~' = "immediately": when both '3,4' and '3~4' exist, a press < TILDE_FRAMES of game time
    // after the previous press is the '~' one (Eddy 4~3), a later press the ',' one.
    const quick = this._framesSinceStep() < TILDE_FRAMES;
    const seps = quick ? ['~', ',', ':'] : [',', '~', ':'];
    for (const s of steps) for (const sep of seps) if (kids.has(base + sep + s)) return base + sep + s;
    for (const s of steps) {
      for (const c of kids) { const m = STATE_PREFIX.exec(c.slice(L)); if (m && /^[A-Z]/.test(m[1]) && m[2] === s) return c; }
    }
    return null;
  }

  /** Fighter API (lane B): the press `input` while the move `base` plays (Fighter.tryAttack), or
      inside the string grace after it. { notation, pending:false } = the string's next hit (buffer
      it, it fires when this hit's active frames end); { notation, pending:true } = a string step
      with no move of its own (the path advances, nothing new plays); null = not a continuation
      (Tekken: the press does nothing until the move ends). A pending path (_strPath) is continued
      before `base`. peek = look only, change nothing. The urge chord never continues a string. */
  continueString(input, ctx = {}, base = this.lastMove, peek = false) {
    const ms = playedMoveset(this.fighterId);
    if (!ms || !ms.moves) return null;
    _prepare(ms);
    if (input === '2+3' && (ctx.urgeOn || ctx.urgeAvailable) && !(this.lastDir && this.lastDir !== 'n')) return null;
    const now = performance.now();
    const bases = [];
    // a pending path stays open STRING_PENDING ms — and for as long as the move that played for it
    // is still playing (a throw stand-in can outlast the window)
    if (this._strPath && (now - this._strPathT < STRING_PENDING || (base && base === this._strPathMove))) bases.push(this._strPath);
    if (base && base !== this._strPath) bases.push(base);
    const sm = base ? MERGE_KEY.exec(base) : null; // batch safety net: a '~shadow' key chains from its base
    if (sm) bases.push(base.slice(0, sm.index));
    for (const b of bases) {
      const c = this._stringStep(b, input, ms, ctx);
      if (!c) continue;
      const pending = !resolveMoveKey(this.fighterId, c);
      if (!peek) { this._strPath = pending ? c : null; this._strPathT = now; this._strPathMove = pending ? base : null; this._markStep(); }
      return { notation: c, pending };
    }
    return null;
  }

