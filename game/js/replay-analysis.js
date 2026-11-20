/* ============================================================
   WESTERN HEART — Replay Analysis ("Trial Review")
   Coordination: worker 29's replay system owns capture/playback. It has
   NOT merged to main yet, so this module defines the REPLAY EVENT
   CONTRACT it analyzes — a minimal, documented event log any recorder
   can emit. When worker 29's recorder lands, it should emit these
   events (or a documented superset); this analyzer plugs straight in.
   REPLAY EVENT CONTRACT (v1):
     { t, type, ... } where type is one of:
     • 'hit'    { by, move, dmg, counter, combo, comboDmg }
     • 'block'  { by, move, chip }
     • 'whiff'  { by, move }
     • 'throw'  { by, broken }
     • 'punish' { by, move, frames }   // punish landed, +frames advantage
     • 'missed-punish' { by, foeMove, foeMinusFrames }
     • 'round'  { winner, timeLeft }
     • 'kindle' { by }  • 'surge' { by } • 'tag' { by, kind }
   The analyzer computes: combo usage, punish rate, whiff rate, throw
   breaks, damage efficiency, missed-punish opportunities — and renders
   a findings overlay (DOM) + a plain-text report.
   WH canon mapping (PROPOSED — needs owner approval):
     "TRIAL REVIEW" — the Trial shows you where you fell. Death is the
     mechanism; the Review is the diagnosis ("It is not an invitation.
     It is a diagnosis." — CANON.md). Minor naming flag.
   ============================================================ */

export const REPLAY_CONTRACT_V = 1;

/* ---------- analysis (pure) ---------- */
export function analyzeReplay(events) {
  const s = {
    hits: 0, blocks: 0, whiffs: 0, throws: 0, throwBreaks: 0,
    counters: 0, punishes: 0, missedPunishes: 0,
    damage: 0, comboHits: 0, maxComboDmg: 0,
    moveUse: {}, punishableEaten: 0,
  };
  for (const e of events) {
    switch (e.type) {
      case 'hit':
        s.hits++; s.damage += e.dmg || 0;
        if (e.counter) s.counters++;
        if (e.combo) { s.comboHits++; s.maxComboDmg = Math.max(s.maxComboDmg, e.comboDmg || 0); }
        if (e.move) s.moveUse[e.move] = (s.moveUse[e.move] || 0) + 1;
        break;
      case 'block': s.blocks++; break;
      case 'whiff': s.whiffs++; if (e.move) s.moveUse[e.move] = (s.moveUse[e.move] || 0) + 1; break;
      case 'throw': s.throws++; if (e.broken) s.throwBreaks++; break;
      case 'punish': s.punishes++; break;
      case 'missed-punish': s.missedPunishes++; s.punishableEaten += 1; break;
    }
  }
  const total = s.hits + s.blocks + s.whiffs;
  return {
    ...s,
    accuracy: total ? s.hits / total : 0,
    punishRate: (s.punishes + s.missedPunishes) ? s.punishes / (s.punishes + s.missedPunishes) : 1,
    throwBreakRate: s.throws ? s.throwBreaks / s.throws : 1,
  };
}

/* Turn stats into human findings, harshest first. */
export function findings(stats) {
  const f = [];
  if (stats.missedPunishes > 0)
    f.push({ sev: 'high', text: `${stats.missedPunishes} punishable move${stats.missedPunishes > 1 ? 's' : ''} went unpunished — the Trial noticed.` });
  if (stats.whiffs > stats.hits)
    f.push({ sev: 'high', text: `More whiffs (${stats.whiffs}) than hits (${stats.hits}). Shorten your strings; the Trial punishes greed.` });
  else if (stats.whiffs > 8)
    f.push({ sev: 'med', text: `${stats.whiffs} whiffed attacks — space yourself like RIN, not like TOU.` });
  if (stats.accuracy < 0.4 && (stats.hits + stats.whiffs) > 5)
    f.push({ sev: 'med', text: `Hit rate ${(stats.accuracy * 100).toFixed(0)}% — confirm before you commit.` });
  if (stats.counters === 0 && stats.hits > 10)
    f.push({ sev: 'low', text: 'No counter-hits all match. Kindle your soul (1+2+3+4) and fish for them.' });
  if (stats.throws > 0 && stats.throwBreakRate < 0.5)
    f.push({ sev: 'med', text: `Throw breaks at ${(stats.throwBreakRate * 100).toFixed(0)}% — watch the arms, break on reaction.` });
  if (stats.maxComboDmg > 0)
    f.push({ sev: 'info', text: `Best combo: ${stats.maxComboDmg} dmg across ${stats.comboHits} combo hits.` });
  const top = Object.entries(stats.moveUse).sort((a, b) => b[1] - a[1]).slice(0, 3);
  if (top.length)
    f.push({ sev: 'info', text: 'Most used: ' + top.map(([m, n]) => `${m}×${n}`).join(', ') });
  if (!f.length) f.push({ sev: 'info', text: 'Clean. The Trial has no notes. Suspicious.' });
  return f;
}

/* ---------- event helpers (so the game emits contract-shaped events) ---------- */
export function evHit(by, move, dmg, opts = {}) {
  return { t: Date.now(), type: 'hit', by, move, dmg, counter: !!opts.counter, combo: !!opts.combo, comboDmg: opts.comboDmg || 0 };
}
export function evMissedPunish(by, foeMove, foeMinusFrames) {
  return { t: Date.now(), type: 'missed-punish', by, foeMove, foeMinusFrames };
}

/* ---------- overlay (DOM; no-op without document) ---------- */
const OVERLAY_ID = 'wh-trial-review';
export function showTrialReview(stats, mount) {
  const list = findings(stats);
  if (typeof document === 'undefined') return list.map(f => `[${f.sev}] ${f.text}`).join('\n');
  let ov = document.getElementById(OVERLAY_ID);
  if (!ov) {
    ov = document.createElement('div'); ov.id = OVERLAY_ID;
    ov.style.cssText = 'position:fixed;inset:0;z-index:220;display:flex;align-items:center;justify-content:center;background:rgba(8,4,14,.78);';
    document.body.appendChild(ov);
  }
  ov.innerHTML = `<div style="width:min(92vw,560px);background:rgba(20,12,32,.95);border:1px solid rgba(255,177,77,.4);border-radius:14px;padding:20px;color:#fff;font-family:inherit;">
    <div style="letter-spacing:4px;font-size:12px;color:#b48cff;margin-bottom:10px;">TRIAL REVIEW — WHERE YOU FELL</div>
    ${list.map(f => `<div style="margin:8px 0;padding:8px 10px;border-left:3px solid ${f.sev === 'high' ? '#ff5a5a' : f.sev === 'med' ? '#ffb14d' : '#7ae08a'};background:rgba(255,255,255,.04);font-size:14px;">${f.text}</div>`).join('')}
    <div style="text-align:right;margin-top:12px;"><button id="wh-tr-close" style="padding:10px 18px;border-radius:10px;border:1px solid rgba(255,255,255,.25);background:rgba(20,12,32,.8);color:#fff;min-height:44px;">RETURN ▸</button></div>
  </div>`;
  ov.style.display = 'flex';
  const btn = ov.querySelector('#wh-tr-close');
  if (btn) btn.addEventListener('click', () => { ov.style.display = 'none'; });
  return list;
}
export function hideTrialReview() {
  if (typeof document === 'undefined') return;
  const ov = document.getElementById(OVERLAY_ID);
  if (ov) ov.style.display = 'none';
}
