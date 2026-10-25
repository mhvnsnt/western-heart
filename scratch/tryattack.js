  tryAttack(name) {
    // TEKKEN STRING BUFFER (lane B, 2026-10-24; owner: "combos don't work ... random stuff is
    // happening", "8 or 10 button strings, some 16-hit"). A press while a move plays either
    // continues THAT move's string or does nothing until the move ends (Tekken). The next hit is
    // buffered and fires when this hit's active frames end (_tickState). Rules, all deterministic:
    //  - the string cursor is the notation now playing (attackName), or a pending string step in
    //    the buffer — never tekken.lastMove, which a surge / AI / raw-fallback move leaves stale;
    //  - presses faster than the hits queue behind the buffered hit, in order (_queuedNext, then
    //    _queuedMore, promoted by _fireNotation): a 10-hit string tapped every 120-250 ms plays
    //    out; a later press never overwrites an earlier one (1, 2, 1 inside one jab used to give 1,1);
    //  - a press that types a string step with no move of its own (10-hit strings) advances the
    //    string path and plays nothing new; the string's move fires on the step that has one.
    if (!/^[1234](\+[1234])*$/.test(name)) {
      this._lastPress = null;
      const r = this._tryAttackFresh(name);
      if (r && this._pressBuf) this._pressBuf.clear();
      return r;
    }
    const tb = this.tekken, now = performance.now();
    const FIELDS = ['state', 'stateT', 'attack', 'attackName', '_attackPhase', 'hasHit', '_queuedNext', '_queuedMore',
      'stance', 'stanceT', '_risingT', '_rageUsed', 'meter', 'vx'];
    const cp = (v) => (Array.isArray(v) ? v.slice() : v);
    const grab = () => { const o = { buf: tb.snapshot() }; for (const k of FIELDS) o[k] = cp(this[k]); return o; };
    const put = (o, all) => {
      tb.restore(o.buf);
      if (all) for (const k of FIELDS) this[k] = cp(o[k]);
      else { this._queuedNext = o._queuedNext; this._queuedMore = cp(o._queuedMore); }
    };
    // CHORD = the single just pressed + one more button. input.js emits the first button at once
    // and the chord when the second lands inside CHORD_WINDOW_MS (50 ms), so '1' then '1+2' means
    // the player pressed 1+2: undo what the single did (a fresh move < 70 ms old with nothing hit,
    // a buffered string hit, a string step) and play the chord from the state before it — a fresh
    // 1+2, or a chord step inside a string (b+3,1+2; chain throws). A second button later than that
    // window is never a chord: when the pair continues the string it is the next string step (1 then
    // 2 = 1,2, not 1+2). A chord with no move keeps the single and tries the other button as the step.
    const lp = this._lastPress;
    if (name.includes('+') && lp && name.split('+').includes(lp.btn)) {
      const rest = name.split('+').filter(b => b !== lp.btn).join('+');
      const sameMove = (this._attackId || 0) === lp.attackId;
      // (by time, not phase: moves with startup 0 in the data are already 'recovery' on frame 1)
      const justStarted = (this._attackId || 0) === lp.attackId + 1 && this.state === 'attack'
        && this.stateT <= 0.07 && !this.hasHit;
      if (now - lp.t <= 60 && (sameMove || justStarted)) {
        const after = grab();
        put(lp.before, justStarted); this._lastPress = null;
        // the single is part of this chord: it must not also fire later from the press buffer
        if (this._pressBuf && this._pressBuf.item && this._pressBuf.item.name === lp.btn) this._pressBuf.clear();
        const r = this.tryAttack(name);
        if (r || this._lastPending) return r; // a move, or a chord string step with no move of its own
        put(after, true);
      }
      this._lastPress = null;
      if (!rest) return false;
      name = rest;
    }
    const before = grab(), id0 = this._attackId || 0;
    let ok;
    this._lastPending = false; tb.pendingStep = null;
    if (this.state === 'attack' && this.attack) {
      const more = this._queuedMore || (this._queuedMore = []);
      const q = more.length ? more[more.length - 1] : this._queuedNext; // the deepest buffered hit
      const ctx = this._inputCtx();
      if (q) {
        const st = tb.continueString(name, ctx, q, true);
        if (st && st.notation[q.length] === '~' && st.notation.startsWith(q)) {
          // '~' = immediately: a press right behind the buffered hit's own press makes it that
          // hit's '~' follow-up (2,1,4~4)
          tb.continueString(name, ctx, q); // commit (a '~' step with no move of its own stays pending)
          if (!st.pending) { if (more.length) more[more.length - 1] = st.notation; else this._queuedNext = st.notation; }
          ok = !st.pending; this._lastPending = st.pending;
        } else if (st && more.length < 15) { // only real continuations queue, so a 16-hit string is the bound
          // taps faster than the hits (touch rhythm 120-250 ms on a 10-hit string): the press
          // continues the deepest buffered hit and waits its turn (_fireNotation promotes it)
          const step = tb.continueString(name, ctx, q);
          ok = !!(step && !step.pending); this._lastPending = !!(step && step.pending);
          if (ok) more.push(step.notation);
        } else ok = false; // not a continuation of the buffered string
      } else {
        const step = tb.continueString(name, ctx, this.attackName);
        ok = !!(step && !step.pending); // pending: a string step with no move — the path advanced
        this._lastPending = !!(step && step.pending);
        if (ok) this._queuedNext = step.notation;
      }
    } else { ok = this._tryAttackFresh(name); this._lastPending = !ok && !!tb.pendingStep; }
    this._lastPress = /^[1234]$/.test(name) ? { btn: name, t: now, attackId: id0, before } : null;
    // Tekken input buffer (combat-core PressBuffer): a press that started nothing and typed no
    // string step — while recovering, in hitstun, or not a continuation of the move playing — is
    // held ~10 frames and fires on the first actionable frame (_drainPressBuffer).
    if (ok) { if (this._pressBuf) this._pressBuf.clear(); }
    else if (!this._lastPending && !this.dead) (this._pressBuf ||= new PressBuffer(10)).push(name, this._clock || 0);
    return ok;
  }
