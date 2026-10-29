/* ============================================================
   WESTERN HEART — Tournament UI + local runner

   Renders the single-elim bracket (tournament.js) and runs LOCAL
   tournaments: the human picks their fighter(s), CPU fills the field,
   matches play in round order, winners advance, champion crowned.

   Wiring contract (additive):
   - OnlineController (js/online.js) constructs TournamentRunner with:
       { getChar, playHumanMatch(p1, p2) -> Promise<winnerId>,
         onEvent(msg) }
   - playHumanMatch is implemented by the controller: it starts a real
     local fight (versus rules) and resolves with the winner's entry id.
   - CPU-vs-CPU matches auto-resolve with a seeded RNG (offline only).
   ============================================================ */
import {
  buildBracket, reportWinner, pendingMatches, isComplete,
  bracketView, describeMatch, mulberry32, BRACKET_SIZES,
} from './tournament.js';

export const TOURNAMENT_CSS_ID = 'wh-tournament-css';

export function ensureTournamentCss() {
  if (document.getElementById(TOURNAMENT_CSS_ID)) return;
  const st = document.createElement('style');
  st.id = TOURNAMENT_CSS_ID;
  st.textContent = `
  .wh-tourn-setup .menu-buttons { display:flex; flex-direction:column; gap:10px; margin-top:14px; }
  .wh-size-row { display:flex; gap:10px; justify-content:center; margin:12px 0; }
  .wh-size-row button { min-width:64px; min-height:48px; }
  .wh-size-row button.sel { outline:2px solid #ffd400; }
  .wh-bracket { display:flex; gap:14px; overflow-x:auto; padding:10px 4px; }
  .wh-bround { min-width:190px; }
  .wh-bround h3 { font-size:12px; letter-spacing:1px; opacity:.8; margin:0 0 8px; }
  .wh-bmatch { border:1px solid #3a3a48; border-radius:8px; padding:8px; margin-bottom:10px; background:rgba(255,255,255,.03); }
  .wh-bmatch .p { padding:4px 6px; border-radius:4px; font-size:13px; }
  .wh-bmatch .p.win { background:rgba(255,212,0,.16); outline:1px solid #ffd400; }
  .wh-bmatch .p.bye { opacity:.4; font-style:italic; }
  .wh-bmatch .vs { font-size:10px; opacity:.5; text-align:center; margin:2px 0; }
  .wh-champ { text-align:center; padding:18px; }
  .wh-champ .crown { font-size:40px; }
  .wh-champ h2 { margin:8px 0 4px; }
  .wh-entrants { display:flex; flex-wrap:wrap; gap:8px; justify-content:center; margin:10px 0; }
  .wh-entrant { border:1px solid #3a3a48; border-radius:8px; padding:6px 10px; font-size:12px; }
  .wh-entrant.human { border-color:#ffd400; }
  .wh-hint { font-size:12px; opacity:.65; text-align:center; }
  `;
  document.head.appendChild(st);
}

/* ---------------- screens ---------------- */

export function buildTournamentScreens(show) {
  if (document.getElementById('screen-tournament')) return;
  ensureTournamentCss();
  document.body.insertAdjacentHTML('beforeend', `
  <section id="screen-tournament" class="screen">
    <div class="panel wh-tourn-setup">
      <p class="stage-kicker">SINGLE ELIMINATION</p>
      <h2>TOURNAMENT</h2>
      <p class="stage-sub">One loss and the shrine forgets your name. TTT2's World
      Arena ran its tournament room the same way — random draw, win or go home.</p>
      <h3 class="trade-h">BRACKET SIZE</h3>
      <div class="wh-size-row" id="tourn-size-row">
        ${BRACKET_SIZES.map((s) => `<button class="btn-ghost${s === 8 ? ' sel' : ''}" data-size="${s}">${s}</button>`).join('')}
      </div>
      <h3 class="trade-h">YOUR FIGHTERS (tap roster cards, then CONFIRM below)</h3>
      <p class="wh-hint">Pick 1 fighter for a solo run, or 2 for couch versus inside the bracket.
      CPU rivals fill the rest of the field.</p>
      <div class="wh-entrants" id="tourn-entrants"></div>
      <div class="menu-buttons">
        <button class="btn-primary" id="tourn-start" disabled>START TOURNAMENT</button>
        <button class="btn-ghost" data-action="online-hub">BACK</button>
      </div>
    </div>
  </section>
  <section id="screen-bracket" class="screen">
    <div class="panel">
      <p class="stage-kicker" id="bracket-kicker">TOURNAMENT</p>
      <h2 id="bracket-title">BRACKET</h2>
      <div class="wh-bracket" id="wh-bracket"></div>
      <div class="wh-champ" id="wh-champ" hidden></div>
      <p class="wh-hint" id="bracket-hint"></p>
      <div class="menu-buttons">
        <button class="btn-primary" id="bracket-next" disabled>NEXT MATCH</button>
        <button class="btn-ghost" data-action="online-hub">QUIT TOURNAMENT</button>
      </div>
    </div>
  </section>`);
}

/** Render a bracket into #wh-bracket. Pure DOM, no game needed. */
export function renderBracket(bracket) {
  const wrap = document.getElementById('wh-bracket');
  if (!wrap) return;
  wrap.innerHTML = '';
  for (const { name, matches } of bracketView(bracket)) {
    const col = document.createElement('div');
    col.className = 'wh-bround';
    col.innerHTML = `<h3>${name}</h3>`;
    for (const m of matches) {
      const d = document.createElement('div');
      d.className = 'wh-bmatch';
      const p = (pl, slot) => {
        if (!pl) return `<div class="p">—</div>`;
        const cls = ['p'];
        if (pl.bye) cls.push('bye');
        if (m.winner && pl.id === m.winner) cls.push('win');
        return `<div class="${cls.join(' ')}">${pl.name}${m.walkover && pl.id === m.winner ? ' (BYE)' : ''}</div>`;
      };
      d.innerHTML = `${p(m.p1)}<div class="vs">vs</div>${p(m.p2)}`;
      col.appendChild(d);
    }
    wrap.appendChild(col);
  }
  const champ = document.getElementById('wh-champ');
  if (bracket.champion && champ) {
    champ.hidden = false;
    champ.innerHTML = `<div class="crown">👑</div><h2>${bracket.champion.name}</h2>
      <p class="stage-sub">TOURNAMENT CHAMPION — the shrine remembers.</p>`;
  } else if (champ) { champ.hidden = true; champ.innerHTML = ''; }
}

/* ---------------- local runner ---------------- */

/**
 * TournamentRunner -- drives a local single-elim tournament.
 * deps: { getChar(id), playHumanMatch(p1entry, p2entry) -> Promise<winnerId>,
 *         cpuPool: [{id,name}], onEvent(type, data), show }
 */
export class TournamentRunner {
  constructor(deps) {
    this.getChar = deps.getChar;
    this.playHumanMatch = deps.playHumanMatch;
    this.cpuPool = deps.cpuPool || [];
    this.onEvent = deps.onEvent || (() => {});
    this.show = deps.show || ((s) => {});
    this.bracket = null;
    this.humanIds = [];
    this.running = false;
  }

  start(humanIds, size = 8) {
    this.humanIds = humanIds.slice();
    const entries = humanIds.map((id) => {
      const c = this.getChar(id);
      return { id, name: (c && c.name) || id, cpu: false };
    });
    this.bracket = buildBracket(entries, {
      size,
      fillCpu: this.cpuPool,
      seed: (Date.now() ^ (Math.random() * 1e9)) >>> 0,
    });
    this.running = true;
    this.onEvent('start', { bracket: this.bracket });
    this._render();
    this.show('bracket');
    this._updateNext();
  }

  quit() {
    this.running = false;
    this.bracket = null;
  }

  /** Play the next pending match (button handler). */
  async next() {
    if (!this.running || !this.bracket) return;
    const pending = pendingMatches(this.bracket);
    if (!pending.length) return;
    const m = pending[0];
    this._setHint(`FIGHT — ${describeMatch(m)}`);
    this._nextDisabled(true);
    const winnerId = await this._playMatch(m);
    if (!this.running) return; // quit mid-match
    reportWinner(this.bracket, m.id, winnerId);
    const w = m.p1.id === winnerId ? m.p1 : m.p2;
    this.onEvent('match', { match: m, winner: w });
    this._render();
    if (isComplete(this.bracket)) {
      this._setHint('');
      this._nextDisabled(true);
      this.onEvent('champion', { champion: this.bracket.champion });
    } else {
      this._updateNext();
    }
  }

  async _playMatch(m) {
    const humans = [m.p1, m.p2].filter((p) => p && this.humanIds.includes(p.id));
    if (!humans.length) {
      // CPU vs CPU: seeded auto-resolve (offline only).
      const rng = mulberry32((Date.now() ^ m.id.length) >>> 0);
      const winner = rng() < 0.5 ? m.p1 : m.p2;
      this.onEvent('auto', { match: m, winner });
      await new Promise((r) => setTimeout(r, 600)); // let the bracket breathe
      return winner.id;
    }
    return this.playHumanMatch(m.p1, m.p2);
  }

  _render() { renderBracket(this.bracket); }

  _updateNext() {
    const pending = pendingMatches(this.bracket);
    const btn = document.getElementById('bracket-next');
    if (!btn) return;
    if (!pending.length) { btn.disabled = true; return; }
    const m = pending[0];
    const humans = [m.p1, m.p2].filter((p) => p && this.humanIds.includes(p.id));
    btn.disabled = false;
    btn.textContent = humans.length ? `FIGHT — ${m.p1.name} VS ${m.p2.name}` : `SIM — ${m.p1.name} VS ${m.p2.name}`;
  }

  _nextDisabled(v) {
    const btn = document.getElementById('bracket-next');
    if (btn) btn.disabled = v;
  }

  _setHint(t) {
    const h = document.getElementById('bracket-hint');
    if (h) h.textContent = t;
  }
}
