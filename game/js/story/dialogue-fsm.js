/* ============================================================
   WESTERN HEART — WHDialogueFSM (Track 7, 2026-10-23)
   Combat-reactive NPC dialogue: enemy banter that changes with the
   fight state — damage taken, HP thresholds, KOs, wave starts.
   Lightweight state machine, zero network, mobile-safe: this is the
   DEFAULT dialogue brain.

   LLM / Inworld seam: an optional provider ({ generateReply }) can
   enrich or replace lines. Inworld AI and runtime LLMs are evaluated
   in docs/research/CUTSCENE-STORY-2026-10-23.md — both are heavy
   for this phone-first game (network latency, API keys, WebGPU
   models), so they ship as [SPEC ONLY] behind this seam, and the
   FSM below is the wired fallback that always works offline.

   Line contract (matches the existing beat contract in
   game/js/versus-banter.js): { speaker, line }. The game registers
   lines from its canon data (versus banter, intro interactions,
   episode beats); the FSM only selects, never authors.

   Node-testable: pure logic, no DOM/three imports.
   ============================================================ */

/* Combat events the FSM listens to. */
export const DLG_EVENTS = [
  'fightStart', 'roundStart', 'roundEnd',
  'damageTaken', 'hpLow', 'hpCritical', 'ko', 'timeout',
  'waveStart', 'waveClear', 'taunt',
];

/* Line: {
     id, speaker, line, event, priority=1,
     cond: { minDmg?, maxHpPct?, minHpPct?, wave?, tags?[] },
     once?: bool, cooldownMs?: number
   } */
export class WHDialogueFSM {
  constructor(opts = {}) {
    this.opts = { globalCooldownMs: 2500, ...opts };
    this.lines = [];
    this._lastGlobal = 0;
    this._lastBySpeaker = new Map();
    this._usedOnce = new Set();
    this._hpNotified = new Map(); // fighterId -> Set<'low'|'critical'>
    this.onLine = null;           // ({speaker, line, event, lineId}) => void
    this.llm = null;              // optional { generateReply(payload) }
    this.llmTimeoutMs = 1200;
    this._now = () => (typeof performance !== 'undefined' ? performance.now() : Date.now());
  }

  registerLines(lines) {
    for (const l of lines) {
      if (!l.id || !l.speaker || !l.line || !l.event) continue;
      this.lines.push({ priority: 1, cond: {}, ...l });
    }
    return this;
  }
  /* Pull beats from an existing banter/intro table into lines for an
     event. table: { 'a|b': [ { beats:[{speaker,line}] } ] } */
  registerBeats(table, event, pairKey) {
    const variants = table[pairKey] || [];
    variants.forEach((v, vi) => {
      (v.beats || []).forEach((b, bi) => {
        this.registerLines([{
          id: `beat-${pairKey}-${vi}-${bi}`, speaker: b.speaker, line: b.line,
          event, tags: v.tags || [],
        }]);
      });
    });
    return this;
  }

  setLLMProvider(provider) { this.llm = provider || null; return this; }

  /* Inworld-compatible event envelope: the structured combat-state
     payload an LLM connector (Inworld web SDK or server LLM) consumes.
     Also useful for logging/telemetry. */
  toInworldEvent(evt) {
    return {
      characterId: evt.speakerId || evt.fighterId || 'unknown',
      eventType: evt.type,
      combatState: {
        hpPct: evt.hpPct ?? null,
        damageTaken: evt.damage ?? 0,
        damageDealt: evt.damageDealt ?? 0,
        wave: evt.wave ?? null,
        round: evt.round ?? null,
        opponentId: evt.opponentId || null,
      },
      history: (evt.recentLines || []).slice(-6),
      ts: Date.now(),
    };
  }

  /* Main entry: feed a combat event, maybe get a line. Returns the
     emitted line record or null. Synchronous FSM path; the LLM path
     is async and best-effort (see emitAsync). */
  emit(evt) {
    const now = this._now();
    if (now - this._lastGlobal < this.opts.globalCooldownMs) return null;
    const line = this._pick(evt, now);
    if (!line) return null;
    return this._fire(line, evt, now);
  }

  /* Async entry: asks the LLM provider first (with timeout), falls
     back to the FSM on failure/timeout. Always resolves. */
  async emitAsync(evt) {
    const payload = this.toInworldEvent(evt);
    if (this.llm && typeof this.llm.generateReply === 'function') {
      try {
        const line = await Promise.race([
          this.llm.generateReply(payload),
          new Promise((_, rej) => setTimeout(() => rej(new Error('llm-timeout')), this.llmTimeoutMs)),
        ]);
        if (line && (line.line || line.text)) {
          return this._fire({
            id: 'llm-' + Date.now(), speaker: line.speaker || payload.characterId,
            line: line.line || line.text, event: evt.type, priority: 10,
          }, evt, this._now());
        }
      } catch { /* fall through to FSM */ }
    }
    return this.emit(evt);
  }

  _pick(evt, now) {
    const cands = [];
    for (const l of this.lines) {
      if (l.event !== evt.type) continue;
      if (l.once && this._usedOnce.has(l.id)) continue;
      const cd = l.cooldownMs || 0;
      const last = this._lastBySpeaker.get(l.speaker);
      if (cd && last !== undefined && now - last < cd) continue;
      if (!this._condMet(l.cond || {}, evt)) continue;
      cands.push(l);
    }
    if (!cands.length) return null;
    cands.sort((a, b) => (b.priority - a.priority) || (a.id < b.id ? -1 : 1));
    // Top-priority tie: deterministic pick (no RNG in core loop).
    const top = cands.filter((c) => c.priority === cands[0].priority);
    return top[evt.pickIndex ? evt.pickIndex % top.length : 0];
  }

  _condMet(cond, evt) {
    if (cond.minDmg != null && (evt.damage || 0) < cond.minDmg) return false;
    if (cond.maxHpPct != null && (evt.hpPct == null || evt.hpPct > cond.maxHpPct)) return false;
    if (cond.minHpPct != null && (evt.hpPct == null || evt.hpPct < cond.minHpPct)) return false;
    if (cond.wave != null && evt.wave !== cond.wave) return false;
    if (cond.tags && cond.tags.length) {
      const et = evt.tags || [];
      if (!cond.tags.some((t) => et.includes(t))) return false;
    }
    return true;
  }

  _fire(line, evt, now) {
    this._lastGlobal = now;
    this._lastBySpeaker.set(line.speaker, now);
    if (line.once) this._usedOnce.add(line.id);
    const rec = { speaker: line.speaker, line: line.line, event: evt.type, lineId: line.id };
    if (this.onLine) { try { this.onLine(rec); } catch { /* non-fatal */ } }
    return rec;
  }

  /* Convenience: HP-threshold watcher — call on every damage event;
     emits hpLow/hpCritical once per fighter per fight. */
  watchHp(fighterId, hpPct) {
    const seen = this._hpNotified.get(fighterId) || new Set();
    let evt = null;
    if (hpPct <= 0.25 && !seen.has('critical')) { seen.add('critical'); evt = 'hpCritical'; }
    else if (hpPct <= 0.5 && !seen.has('low')) { seen.add('low'); evt = 'hpLow'; }
    this._hpNotified.set(fighterId, seen);
    return evt ? { type: evt, fighterId, hpPct } : null;
  }
  resetFight() { this._hpNotified.clear(); this._usedOnce.clear(); this._lastGlobal = 0; return this; }
}

/* ---- DEMO line set (system demo only, not canon content) --------
   Marked [DEMO]: proves the trigger paths in tests and the harness.
   Real lines come from versus-banter.js / intro-interactions.js /
   episodes.js via registerLines()/registerBeats(). */
export const DEMO_LINES = [
  { id: 'demo-start', speaker: 'guide', line: 'The Trial keeps what it catches.', event: 'fightStart', priority: 5 },
  { id: 'demo-dmg1', speaker: 'echo', line: 'You bleed. The dark noticed.', event: 'damageTaken', cond: { minDmg: 15 }, priority: 3, cooldownMs: 8000 },
  { id: 'demo-dmg2', speaker: 'echo', line: 'That one cracked something.', event: 'damageTaken', cond: { minDmg: 40 }, priority: 5, cooldownMs: 8000 },
  { id: 'demo-low', speaker: 'guide', line: 'Your ember gutters. Feed it or fall.', event: 'hpLow', priority: 8, once: true },
  { id: 'demo-crit', speaker: 'echo', line: 'Almost mine now.', event: 'hpCritical', priority: 9, once: true },
  { id: 'demo-ko', speaker: 'guide', line: 'The echo takes its toll and walks on.', event: 'ko', priority: 5 },
  { id: 'demo-wave', speaker: 'guide', line: 'Another echo rises.', event: 'waveStart', priority: 4 },
];
