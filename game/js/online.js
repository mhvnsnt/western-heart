/* ============================================================
   WESTERN HEART — OnlineController: lobbies, tournaments, netplay,
   daily challenges.

   Lineage (see docs/research/online-lobby-tournament-research.md):
   - TTT2 Player Matches: Quick Match (random pair) / Custom Match
     (lobby list) / Create Session (host with settings); World Arena
     rooms + fight requests + tournament room.
   - SFV Battle Lounge: owner settings (set rotation length, password,
     private slots, fast character select), 8 players + spectators,
     connection-bar restriction.

   Wiring (additive — no edits to main.js/menus.js/modes.js):
   - Loaded via <script type="module" src="js/online.js"> (index.html).
   - Self-initializes on DOMContentLoaded; waits for window.__game.
   - Handles data-action="mode-online" with its own delegated listener
     (main.js's dispatch doesn't know this action — this runs alongside).
   - Screens are built dynamically (same pattern as menus.js
     buildOverlays); show() reuses the .screen switcher.
   - ChallengeManager chains game.onMatchEnd + wraps mode-clear
     methods via prototype — no game.js/modes.js edits.

   HONEST SCOPE: lobby/matchmaking/tournament/challenges are fully
   playable. Netcode versus runs the deterministic REFERENCE sim
   (game/netplay/sim/fighter-sim.js) over WebRTC + lite-rollback —
   playable proof of rollback. Real-fighter netplay awaits the combat
   sim port (docs/netcode/NETCODE-ARCHITECTURE.md).
   ============================================================ */
import { LobbyClient, QUICK_CHAT } from '../netplay/lobby/lobby-protocol.js';
import { encodeInput, inputWordToSimBits } from '../netplay/bridge/input-codec.js';
import { buildTournamentScreens, TournamentRunner } from './tournament-ui.js';
import { ChallengeManager } from './challenges.js';
import {
  onUnlock, unlockedTitles, activeTitle, setActiveTitle, UNLOCKABLES,
} from './unlockables.js';
import { todayStr } from '../data/challenges.js';

const SIGNAL_PORT = 8765;
const NAME_KEY = 'wh_online_name';

export function playerName() {
  try {
    let n = localStorage.getItem(NAME_KEY);
    if (!n) {
      n = 'SOUL' + Math.floor(1000 + Math.random() * 9000);
      localStorage.setItem(NAME_KEY, n);
    }
    return n;
  } catch { return 'SOUL'; }
}
export function setPlayerName(n) {
  const v = String(n || '').slice(0, 16) || playerName();
  try { localStorage.setItem(NAME_KEY, v); } catch { /* private mode */ }
  return v;
}

function showScreen(name) {
  document.querySelectorAll('.screen').forEach((s) => s.classList.remove('active'));
  const t = document.getElementById(name === 'hud' ? 'hud' : `screen-${name}`);
  if (t) t.classList.add('active');
}

const el = (tag, cls, html) => {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (html != null) e.innerHTML = html;
  return e;
};

function ensureOnlineCss() {
  if (document.getElementById('wh-online-css')) return;
  const st = document.createElement('style');
  st.id = 'wh-online-css';
  st.textContent = `
  .wh-online .menu-buttons { display:flex; flex-direction:column; gap:10px; margin-top:14px; }
  .wh-event-banner { border:1px solid #ffd400; border-radius:8px; padding:8px 12px; margin:10px 0;
    background:rgba(255,212,0,.07); font-size:13px; text-align:center; }
  .wh-lobby-list { display:flex; flex-direction:column; gap:8px; margin:12px 0; max-height:40vh; overflow-y:auto; }
  .wh-lobby-row { display:flex; align-items:center; gap:10px; border:1px solid #3a3a48; border-radius:8px;
    padding:10px 12px; background:rgba(255,255,255,.03); }
  .wh-lobby-row .grow { flex:1; }
  .wh-lobby-row .meta { font-size:11px; opacity:.6; }
  .wh-slots { display:grid; grid-template-columns:1fr 1fr; gap:8px; margin:12px 0; }
  .wh-slot { border:1px solid #3a3a48; border-radius:8px; padding:10px; min-height:76px;
    background:rgba(255,255,255,.03); font-size:13px; }
  .wh-slot .nm { font-weight:bold; }
  .wh-slot .rl { font-size:11px; opacity:.6; }
  .wh-slot.me { border-color:#ffd400; }
  .wh-slot.ready .nm::after { content:' ✓'; color:#7dff8a; }
  .wh-slot.empty { opacity:.45; display:flex; align-items:center; justify-content:center; }
  .wh-roomcode { font-size:28px; letter-spacing:6px; text-align:center; margin:6px 0; }
  .wh-chat { border:1px solid #3a3a48; border-radius:8px; height:120px; overflow-y:auto;
    padding:8px; font-size:12px; margin:10px 0; background:rgba(0,0,0,.25); }
  .wh-chat .sys { opacity:.55; font-style:italic; }
  .wh-chat-row { display:flex; gap:8px; }
  .wh-chat-row input { flex:1; min-height:44px; }
  .wh-quickchat { display:flex; flex-wrap:wrap; gap:6px; margin:8px 0; }
  .wh-quickchat button { font-size:11px; padding:6px 10px; min-height:36px; }
  .wh-form { display:flex; flex-direction:column; gap:10px; margin:12px 0; }
  .wh-form label { font-size:12px; opacity:.75; display:flex; flex-direction:column; gap:4px; }
  .wh-form input[type=text], .wh-form input[type=password], .wh-form select { min-height:44px; }
  .wh-form .row { display:flex; gap:12px; align-items:center; }
  .wh-chal { border:1px solid #3a3a48; border-radius:8px; padding:10px 12px; margin:10px 0;
    background:rgba(255,255,255,.03); }
  .wh-chal .cn { font-weight:bold; }
  .wh-chal .cf { font-size:12px; opacity:.7; margin:4px 0; }
  .wh-chal .bar { height:8px; border-radius:4px; background:#22222c; overflow:hidden; margin:6px 0; }
  .wh-chal .bar i { display:block; height:100%; background:#ffd400; }
  .wh-chal .diff { font-size:10px; letter-spacing:1px; opacity:.6; }
  .wh-chal.done { border-color:#7dff8a; }
  .wh-toast { position:fixed; left:50%; bottom:18px; transform:translateX(-50%); z-index:9999;
    background:#1a1a24; border:1px solid #ffd400; border-radius:10px; padding:12px 18px;
    font-size:14px; text-align:center; animation:wh-toast-in .25s ease-out; max-width:88vw; }
  @keyframes wh-toast-in { from { opacity:0; transform:translate(-50%,12px);} to { opacity:1; transform:translate(-50%,0);} }
  .wh-netversus { position:fixed; inset:0; z-index:9000; background:#0a0a0e; display:flex;
    flex-direction:column; align-items:center; justify-content:center; gap:8px; }
  .wh-netversus canvas { width:min(96vw,900px); border:1px solid #2a2a30; border-radius:8px; }
  .wh-netversus .hud { display:flex; gap:14px; font-size:12px; opacity:.75; font-family:monospace; }
  .wh-netversus .keys { font-size:11px; opacity:.55; }
  `;
  document.head.appendChild(st);
}

/* ============================================================
   OnlineController
   ============================================================ */
export class OnlineController {
  constructor() {
    this.client = null;
    this.challenges = new ChallengeManager();
    this.tournRunner = null;
    this.netversus = null;
    this._built = false;
    this._name = playerName();
  }

  /** Boot: wait for the game, then wire everything. */
  init() {
    const tryInit = () => {
      if (!window.__game || !window.__modes) { setTimeout(tryInit, 150); return; }
      if (this._built) return;
      this._built = true;
      ensureOnlineCss();
      buildOnlineScreens();
      buildTournamentScreens(showScreen);
      this._wireHubButton();
      this._wireGlobalActions();
      // challenge tracking: chain match-end + mode clears (additive)
      this.challenges.watch(window.__game);
      import('./modes.js').then((m) => {
        this.challenges.hookModes(m.ModeController, m.timeAttackGrade);
      }).catch(() => {});
      onUnlock((def) => this.toast(`🏆 UNLOCKED — ${def.name}`));
      this.challenges.onChange(() => { if (document.getElementById('screen-challenges').classList.contains('active')) this.renderChallenges(); });
    };
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', tryInit);
    } else tryInit();
  }

  /* ---------- hub ---------- */

  _wireHubButton() {
    // main.js doesn't know data-action="mode-online"; handle it here.
    document.addEventListener('click', (e) => {
      const b = e.target.closest('[data-action="mode-online"]');
      if (b) { e.stopPropagation(); this.openHub(); }
    }, true);
  }

  _wireGlobalActions() {
    document.addEventListener('click', (e) => {
      const b = e.target.closest('[data-action]');
      if (!b) return;
      const a = b.dataset.action;
      if (a === 'online-hub') this.openHub();
      else if (a === 'online-find') this.openBrowser();
      else if (a === 'online-create') this.openCreate();
      else if (a === 'online-quick') this.quickMatch();
      else if (a === 'online-tournament') this.openTournamentSetup();
      else if (a === 'online-challenges') this.openChallenges();
      else if (a === 'online-leave') this.leaveLobby();
    });
  }

  openHub() {
    const t = activeTitle();
    const titleName = t && UNLOCKABLES[t] ? UNLOCKABLES[t].name : null;
    const ev = this.challenges.today().event;
    document.getElementById('online-player-line').innerHTML =
      `FIGHTER: <b>${this._name}</b>${titleName ? ` · <span style="color:#ffd400">${titleName}</span>` : ''}`;
    document.getElementById('online-event').innerHTML =
      `⚡ <b>${ev.name}</b> — ${ev.flavor}`;
    showScreen('online');
  }

  /* ---------- signaling ---------- */

  signalUrl() {
    const host = location.hostname || 'localhost';
    return `ws://${host}:${SIGNAL_PORT}`;
  }

  async ensureClient() {
    if (this.client && this.client.connected) return this.client;
    const sock = new WebSocket(this.signalUrl());
    const client = new LobbyClient();
    client.setName(this._name);
    client.on('error', (e) => this.toast('⚠ ' + e.message));
    client.on('lobby', () => { if (this._inLobby()) this.renderLobby(); });
    client.on('directory', () => { if (this._inBrowser()) this.renderBrowser(); });
    client.on('chat', (m) => this._chatLine(`${m.fromName}: ${m.text}`));
    client.on('fight-request', (m) => this._onFightRequest(m));
    client.on('match-start', (m) => this._onMatchStart(m));
    client.on('match-end', (m) => this._onMatchEnd(m));
    client.on('bracket-update', (b) => this._onBracketUpdate(b));
    client.on('signal', ({ from, data }) => {
      if (this.netversus) this.netversus.onSignal(from, data);
    });
    await new Promise((resolve, reject) => {
      const to = setTimeout(() => reject(new Error('signaling unreachable')), 6000);
      sock.onopen = () => { clearTimeout(to); resolve(); };
      sock.onerror = () => { clearTimeout(to); reject(new Error('signaling unreachable')); };
    }).catch((e) => {
      this.toast(`⚠ ${e.message} — start it: node game/netplay/signaling/server.js`);
      throw e;
    });
    client.attach(sock);
    // wait for the server's welcome (player id) before returning
    await new Promise((r) => {
      if (client.playerId) r();
      else client.on('welcome', () => r());
      setTimeout(r, 3000);
    });
    this.client = client;
    return client;
  }

  _inLobby() {
    const s = document.getElementById('screen-lobby');
    return s && s.classList.contains('active');
  }
  _inBrowser() {
    const s = document.getElementById('screen-lounges');
    return s && s.classList.contains('active');
  }

  /* ---------- TTT2 "Quick Match" ---------- */

  async quickMatch() {
    try {
      const c = await this.ensureClient();
      this.toast('Searching for a rival… (TTT2 quick match)');
      const res = await c.quickMatch();
      if (res.t === 'quick-found') {
        this._chatLine('Matched! Entering lounge ' + res.room, true);
        this.openLobby();
      }
    } catch { /* toast already shown */ }
  }

  /* ---------- TTT2 "Custom Match": browse + join ---------- */

  async openBrowser() {
    showScreen('lounges');
    document.getElementById('lounges-list').innerHTML = '<p class="wh-hint">Scanning the World Arena…</p>';
    try {
      const c = await this.ensureClient();
      await c.listLobbies();
    } catch { /* toast already shown */ }
  }

  renderBrowser() {
    const list = document.getElementById('lounges-list');
    const dirs = this.client ? this.client.directory : [];
    list.innerHTML = '';
    if (!dirs.length) {
      list.innerHTML = '<p class="wh-hint">No lounges. Create one — be the house.</p>';
      return;
    }
    for (const l of dirs) {
      const row = el('div', 'wh-lobby-row', `
        <div class="grow"><b>${l.name}</b> <span class="meta">${l.hasPassword ? '🔒' : ''}</span><br>
        <span class="meta">${l.players}/${l.maxPlayers} · ${l.ranked ? 'RANKED' : 'CASUAL'} · ${l.inMatch ? 'IN MATCH' : 'OPEN'}</span></div>`);
      const join = el('button', 'btn-primary', 'JOIN');
      join.addEventListener('click', () => this.joinLounge(l));
      row.appendChild(join);
      list.appendChild(row);
    }
  }

  async joinLounge(l) {
    let password = null;
    if (l.hasPassword) {
      password = prompt('Password for ' + l.name + ':');
      if (password == null) return;
    }
    try {
      const c = await this.ensureClient();
      await c.joinLobby(l.room, { password });
      this.openLobby();
    } catch (e) { this.toast('⚠ ' + e.message); }
  }

  /* ---------- TTT2 "Create Session" / SFV lounge options ---------- */

  openCreate() { showScreen('lounge-create'); }

  async createLounge() {
    const v = (id) => document.getElementById(id).value;
    const name = v('lc-name') || `${this._name}'S LOUNGE`;
    const maxPlayers = parseInt(v('lc-max'), 10) || 8;
    const password = v('lc-pass') || null;
    const rotation = parseInt(v('lc-rotation'), 10) || 2;
    const allowSpectate = document.getElementById('lc-spectate').checked;
    const ranked = document.getElementById('lc-ranked').checked;
    try {
      const c = await this.ensureClient();
      await c.createLobby({ name, maxPlayers, password, rotation, allowSpectate, ranked });
      this.openLobby();
    } catch (e) { this.toast('⚠ ' + e.message); }
  }

  /* ---------- the lounge room ---------- */

  openLobby() { showScreen('lobby'); this.renderLobby(); }

  leaveLobby() {
    try { this.client && this.client.leaveLobby(); } catch { /* offline */ }
    this.openHub();
  }

  renderLobby() {
    const c = this.client;
    const lobby = c && c.lobby;
    if (!lobby) { this.openHub(); return; }
    document.getElementById('lobby-code').textContent = lobby.room;
    document.getElementById('lobby-name').textContent = lobby.name;
    const st = lobby.settings || {};
    document.getElementById('lobby-meta').textContent =
      `${lobby.players.length}/${st.maxPlayers || 8} souls · ` +
      `rotation ${st.rotation || 2} · ${st.ranked ? 'RANKED' : 'CASUAL'} · ` +
      `${st.allowSpectate ? 'spectators welcome' : 'no spectators'}` +
      (c.isHost ? ' · 👑 YOU HOST' : '');
    const slots = document.getElementById('lobby-slots');
    slots.innerHTML = '';
    const max = st.maxPlayers || 8;
    const bySeat = [...lobby.players].sort((a, b) => a.seat - b.seat);
    for (let i = 0; i < max; i++) {
      const p = bySeat[i];
      if (!p) {
        slots.appendChild(el('div', 'wh-slot empty', '— open —'));
        continue;
      }
      const d = el('div', 'wh-slot' + (p.id === c.playerId ? ' me' : '') + (p.ready ? ' ready' : ''));
      const role = p.role === 'host' ? '👑 HOST' : p.role === 'spectator' ? '👁 SPECTATOR' : 'FIGHTER';
      const title = p.title ? ` <span style="color:#ffd400;font-size:11px">${p.title}</span>` : '';
      d.innerHTML = `<div class="nm">${p.name}${title}</div><div class="rl">${role}${p.character ? ' · ' + p.character : ''}</div>`;
      if (c.isHost && p.id !== c.playerId) {
        const fr = el('button', 'btn-ghost', 'FIGHT?');
        fr.style.cssText = 'margin-top:6px;min-height:36px;font-size:11px;';
        fr.addEventListener('click', () => c.requestFight(p.id));
        d.appendChild(fr);
      }
      slots.appendChild(d);
    }
    // ready / spectate controls
    const me = c.me;
    document.getElementById('lobby-ready').textContent = me && me.ready ? 'NOT READY' : 'READY UP';
    document.getElementById('lobby-ready').disabled = !me || me.role === 'spectator';
    const sc = document.getElementById('lobby-spectate');
    sc.textContent = me && me.role === 'spectator' ? 'JOIN AS FIGHTER' : 'SPECTATE';
    // host controls
    const hostBox = document.getElementById('lobby-host');
    hostBox.innerHTML = '';
    if (c.isHost) {
      const pair = c.rotationPair();
      const start = el('button', 'btn-primary',
        pair ? `START — ${pair[0].name} VS ${pair[1].name}` : 'START MATCH (need 2 ready)');
      start.disabled = !pair;
      start.addEventListener('click', () => { if (pair) c.startMatch(pair[0].id, pair[1].id); });
      hostBox.appendChild(start);
      const note = el('p', 'wh-hint', 'SFV lounge rule: the two longest-waiting ready fighters rotate in.');
      hostBox.appendChild(note);
    }
  }

  toggleReady() {
    const c = this.client;
    if (!c || !c.me) return;
    c.setReady(!c.me.ready);
  }

  async toggleSpectate() {
    // rejoin with the flipped role (simple + robust for v1)
    const c = this.client;
    if (!c || !c.lobby) return;
    const room = c.lobby.room;
    const wantSpectate = c.me && c.me.role !== 'spectator';
    c.leaveLobby();
    try { await c.joinLobby(room, { spectate: wantSpectate }); this.renderLobby(); }
    catch (e) { this.toast('⚠ ' + e.message); }
  }

  sendChat() {
    const inp = document.getElementById('lobby-chat-in');
    const t = inp.value.trim();
    if (!t || !this.client) return;
    this.client.sendChat(t);
    inp.value = '';
  }

  _chatLine(text, sys = false) {
    const box = document.getElementById('lobby-chat');
    if (!box) return;
    const d = el('div', sys ? 'sys' : '', text);
    box.appendChild(d);
    box.scrollTop = box.scrollHeight;
  }

  _onFightRequest({ from, fromName }) {
    // TTT2 World Arena: a fight request. Accept -> both ready up, host starts.
    if (confirm(`${fromName} wants to fight you. Accept?`)) {
      this.client.acceptFight(from);
      this.client.setReady(true);
      this._chatLine(`${fromName}'s challenge accepted. Ready up!`, true);
    } else this.client.declineFight(from);
  }

  _onMatchStart(match) {
    this._chatLine(`⚔ MATCH — starting…`, true);
    this.startNetVersus(match);
  }

  _onMatchEnd({ winner }) {
    if (this.netversus) this.netversus.destroy();
    this.netversus = null;
    const name = this._playerName(winner);
    this._chatLine(`🏆 ${name} takes the match!`, true);
    this.toast(`🏆 ${name} wins`);
    if (this._inLobby()) this.renderLobby();
  }

  _onBracketUpdate(bracket) {
    // host is running a lounge tournament; render for everyone
    if (document.getElementById('screen-bracket')) {
      import('./tournament-ui.js').then((m) => {
        m.renderBracket(bracket);
        showScreen('bracket');
      });
    }
  }

  _playerName(id) {
    const l = this.client && this.client.lobby;
    const p = l && l.players.find((x) => x.id === id);
    return p ? p.name : '???';
  }

  /* ---------- netcode versus (reference sim, rollback, WebRTC) ---------- */
  async startNetVersus(match) {
    if (this.netversus) this.netversus.destroy();
    this.netversus = new NetVersus({
      client: this.client,
      match,
      localId: this.client.playerId,
      onEnd: (winnerId) => {
        // only the match's p1 reports (p2 is the fallback after 3s)
        if (match.p1 === this.client.playerId) this.client.reportResult(winnerId);
        else setTimeout(() => {
          if (this.client && this.client.match) this.client.reportResult(winnerId);
        }, 3000);
      },
    });
    await this.netversus.start().catch((e) => {
      this.toast('⚠ netplay failed: ' + e.message);
      this.netversus = null;
    });
  }

  /* ---------- tournament ---------- */

  openTournamentSetup() {
    showScreen('tournament');
    this._tournSize = 8;
    this._tournPicks = [];
    document.querySelectorAll('#tourn-size-row button').forEach((b) => {
      b.classList.toggle('sel', parseInt(b.dataset.size, 10) === 8);
      b.onclick = () => {
        this._tournSize = parseInt(b.dataset.size, 10);
        document.querySelectorAll('#tourn-size-row button').forEach((x) => x.classList.remove('sel'));
        b.classList.add('sel');
        this._renderTournPicks();
      };
    });
    // roster pick grid (tap 1-2 fighters)
    let grid = document.getElementById('tourn-roster');
    if (!grid) {
      grid = el('div', 'wh-entrants');
      grid.id = 'tourn-roster';
      document.getElementById('tourn-entrants').after(grid);
    }
    grid.innerHTML = '';
    const roster = (window.__modes && window.__modes.roster) || [];
    for (const c of roster.slice(0, 48)) {
      const b = el('button', 'wh-entrant', c.name);
      b.addEventListener('click', () => {
        const i = this._tournPicks.indexOf(c.id);
        if (i >= 0) this._tournPicks.splice(i, 1);
        else if (this._tournPicks.length < 2) this._tournPicks.push(c.id);
        this._renderTournPicks();
      });
      b.dataset.id = c.id;
      grid.appendChild(b);
    }
    document.getElementById('tourn-start').onclick = () => this.startLocalTournament();
    this._renderTournPicks();
  }

  _renderTournPicks() {
    const wrap = document.getElementById('tourn-entrants');
    wrap.innerHTML = '';
    const roster = (window.__modes && window.__modes.roster) || [];
    const nameOf = (id) => { const c = roster.find((x) => x.id === id); return c ? c.name : id; };
    for (const id of this._tournPicks) {
      wrap.appendChild(el('div', 'wh-entrant human', 'P' + (this._tournPicks.indexOf(id) + 1) + ' · ' + nameOf(id)));
    }
    document.querySelectorAll('#tourn-roster .wh-entrant').forEach((b) => {
      b.classList.toggle('human', this._tournPicks.includes(b.dataset.id));
    });
    document.getElementById('tourn-start').disabled = this._tournPicks.length === 0;
    document.getElementById('tourn-start').textContent =
      this._tournPicks.length ? `START ${this._tournSize}-SOUL TOURNAMENT` : 'PICK A FIGHTER FIRST';
  }

  startLocalTournament() {
    const roster = (window.__modes && window.__modes.roster) || [];
    const picked = new Set(this._tournPicks);
    const cpuPool = roster
      .filter((c) => !picked.has(c.id) && c.id !== 'custom')
      .map((c) => ({ id: c.id, name: c.name }));
    const getChar = (id) => {
      const c = roster.find((x) => x.id === id);
      return c ? { id: c.id, name: c.name } : { id, name: id };
    };
    this.tournRunner = new TournamentRunner({
      getChar,
      cpuPool,
      show: showScreen,
      onEvent: (type, data) => {
        if (type === 'champion') {
          this.toast(`👑 ${data.champion.name} — TOURNAMENT CHAMPION`);
          // broadcast to the lounge if we're hosting one
          if (this.client && this.client.isHost && this.client.lobby) {
            this.client.updateBracket(this.tournRunner.bracket);
          }
        }
      },
      playHumanMatch: (p1, p2) => this._playTournamentMatch(p1, p2),
    });
    document.getElementById('bracket-next').onclick = () => this.tournRunner.next();
    this.tournRunner.start(this._tournPicks, this._tournSize);
  }

  /** Play one tournament match as a real local fight; resolves winner entry id. */
  _playTournamentMatch(p1entry, p2entry) {
    return new Promise((resolve) => {
      const modes = window.__modes;
      const g = window.__game;
      modes.mode = 'tournament';
      // versus flow (stage select per match — Tekken-like), but WE own the
      // result: override the versus end handler right after _beginVersus
      // assigns it. Challenge tracking still chains through.
      modes._beginVersus(p1entry.id, p2entry.id);
      const prev = g.onMatchEnd; // the challenge dispatch (or raw)
      g.onMatchEnd = (won) => {
        if (prev) { try { prev(won); } catch (e) { console.error(e); } }
        const winnerId = won ? p1entry.id : p2entry.id;
        setTimeout(() => {
          showScreen('bracket');
          resolve(winnerId);
        }, 1800); // let the KO banner breathe
      };
      this.toast(`⚔ ${p1entry.name} vs ${p2entry.name} — tournament match`);
    });
  }

  /* ---------- daily challenges ---------- */

  openChallenges() {
    showScreen('challenges');
    this.renderChallenges();
  }

  renderChallenges() {
    const { dailies, event, date } = this.challenges.today();
    document.getElementById('chal-date').textContent =
      `TODAY'S TRIALS — ${date} · resets midnight`;
    document.getElementById('chal-event').innerHTML =
      `⚡ <b>${event.name}</b> — ${event.flavor}`;
    const wrap = document.getElementById('chal-list');
    wrap.innerHTML = '';
    for (const c of dailies) {
      const prog = this.challenges.progressOf(c.id);
      const done = this.challenges.isComplete(c.id);
      const claimed = this.challenges.isClaimed(c.id);
      const pct = Math.min(100, Math.round((prog / c.target) * 100));
      const d = el('div', 'wh-chal' + (done ? ' done' : ''));
      const targetTxt = typeof c.target === 'number' ? `${Math.min(prog, c.target)}/${c.target}` : c.target;
      d.innerHTML = `
        <div class="diff">${c.difficulty.toUpperCase()}</div>
        <div class="cn">${c.name}</div>
        <div class="cf">${c.flavor}</div>
        <div class="bar"><i style="width:${pct}%"></i></div>
        <div class="cf">${targetTxt}${done ? ' — COMPLETE' : ''}</div>`;
      if (done && !claimed) {
        const b = el('button', 'btn-primary', 'CLAIM REWARD');
        b.addEventListener('click', () => {
          const ch = this.challenges.claim(c.id);
          if (ch) this.renderChallenges();
        });
        d.appendChild(b);
      } else if (claimed) {
        d.appendChild(el('div', 'cf', '✓ reward claimed'));
      }
      wrap.appendChild(d);
    }
    // unlock shelf
    const shelf = document.getElementById('chal-unlocks');
    shelf.innerHTML = '<h3 class="trade-h">YOUR UNLOCKS</h3>';
    const titles = unlockedTitles();
    if (!titles.length) shelf.innerHTML += '<p class="wh-hint">No unlocks yet. Complete a daily.</p>';
    for (const t of titles.slice(0, 12)) {
      const row = el('div', 'wh-lobby-row', `<div class="grow">🏷 ${t.name}</div>`);
      const cur = activeTitle() === t.id;
      const b = el('button', cur ? 'btn-primary' : 'btn-ghost', cur ? 'ACTIVE' : 'EQUIP');
      b.addEventListener('click', () => { setActiveTitle(t.id); this.renderChallenges(); });
      row.appendChild(b);
      shelf.appendChild(row);
    }
  }

  /* ---------- toast ---------- */

  toast(msg, ms = 2600) {
    const t = el('div', 'wh-toast', msg);
    document.body.appendChild(t);
    setTimeout(() => t.remove(), ms);
  }
}

/* ============================================================
   Screens (built once, dynamically)
   ============================================================ */
function buildOnlineScreens() {
  if (document.getElementById('screen-online')) return;
  ensureOnlineCss();
  document.body.insertAdjacentHTML('beforeend', `
  <section id="screen-online" class="screen">
    <div class="panel wh-online">
      <p class="stage-kicker">WORLD ARENA</p>
      <h2>ONLINE</h2>
      <p class="stage-sub" id="online-player-line"></p>
      <div class="wh-event-banner" id="online-event"></div>
      <div class="menu-buttons">
        <button class="btn-primary" data-action="online-quick">⚡ QUICK MATCH<small>TTT2 style — instant rival</small></button>
        <button class="btn-primary" data-action="online-find">FIND LOUNGE<small>browse the World Arena</small></button>
        <button class="btn-primary" data-action="online-create">CREATE LOUNGE<small>SFV battle lounge — your rules</small></button>
        <button class="btn-primary" data-action="online-tournament">TOURNAMENT<small>single-elim bracket</small></button>
        <button class="btn-primary" data-action="online-challenges">DAILY CHALLENGES<small>today's trials + rewards</small></button>
        <button class="btn-ghost" data-action="back-menu">BACK</button>
      </div>
      <p class="wh-hint">Netplay runs rollback over WebRTC (P2P). Needs the signaling
      server: <span style="font-family:monospace">node game/netplay/signaling/server.js</span></p>
    </div>
  </section>
  <section id="screen-lounges" class="screen">
    <div class="panel wh-online">
      <p class="stage-kicker">WORLD ARENA</p>
      <h2>FIND LOUNGE</h2>
      <div class="wh-lobby-list" id="lounges-list"></div>
      <div class="menu-buttons">
        <button class="btn-ghost" data-action="online-find">REFRESH</button>
        <button class="btn-ghost" data-action="online-hub">BACK</button>
      </div>
    </div>
  </section>
  <section id="screen-lounge-create" class="screen">
    <div class="panel wh-online">
      <p class="stage-kicker">BATTLE LOUNGE</p>
      <h2>CREATE LOUNGE</h2>
      <div class="wh-form">
        <label>LOUNGE NAME<input type="text" id="lc-name" maxlength="40" placeholder="MY LOUNGE"></label>
        <div class="row">
          <label>MAX SOULS
            <select id="lc-max"><option>2</option><option>4</option><option selected>8</option></select></label>
          <label>SET ROTATION
            <select id="lc-rotation"><option>1</option><option selected>2</option><option>3</option><option>5</option></select></label>
        </div>
        <label>PASSWORD (optional)<input type="password" id="lc-pass" maxlength="24" placeholder="open lounge"></label>
        <div class="row">
          <label><input type="checkbox" id="lc-spectate" checked> Spectators welcome</label>
          <label><input type="checkbox" id="lc-ranked"> Ranked (stub)</label>
        </div>
      </div>
      <div class="menu-buttons">
        <button class="btn-primary" id="lc-create">OPEN THE DOORS</button>
        <button class="btn-ghost" data-action="online-hub">BACK</button>
      </div>
    </div>
  </section>
  <section id="screen-lobby" class="screen">
    <div class="panel wh-online">
      <p class="stage-kicker">LOUNGE</p>
      <h2 id="lobby-name">—</h2>
      <div class="wh-roomcode" id="lobby-code">————</div>
      <p class="wh-hint" id="lobby-meta"></p>
      <div class="wh-slots" id="lobby-slots"></div>
      <div class="menu-buttons" style="flex-direction:row">
        <button class="btn-primary" id="lobby-ready" style="flex:1">READY UP</button>
        <button class="btn-ghost" id="lobby-spectate" style="flex:1">SPECTATE</button>
      </div>
      <div id="lobby-host"></div>
      <div class="wh-chat" id="lobby-chat"></div>
      <div class="wh-quickchat" id="lobby-quickchat"></div>
      <div class="wh-chat-row">
        <input type="text" id="lobby-chat-in" maxlength="140" placeholder="talk…">
        <button class="btn-primary" id="lobby-send">SEND</button>
      </div>
      <div class="menu-buttons">
        <button class="btn-ghost" data-action="online-leave">LEAVE LOUNGE</button>
      </div>
    </div>
  </section>
  <section id="screen-challenges" class="screen">
    <div class="panel wh-online">
      <p class="stage-kicker">DAILY</p>
      <h2>CHALLENGES</h2>
      <p class="wh-hint" id="chal-date"></p>
      <div class="wh-event-banner" id="chal-event"></div>
      <div id="chal-list"></div>
      <div id="chal-unlocks"></div>
      <div class="menu-buttons">
        <button class="btn-ghost" data-action="online-hub">BACK</button>
      </div>
    </div>
  </section>`);

  // wire static buttons inside the new screens
  document.getElementById('lc-create').addEventListener('click', () =>
    window.__online && window.__online.createLounge());
  document.getElementById('lobby-ready').addEventListener('click', () =>
    window.__online && window.__online.toggleReady());
  document.getElementById('lobby-spectate').addEventListener('click', () =>
    window.__online && window.__online.toggleSpectate());
  document.getElementById('lobby-send').addEventListener('click', () =>
    window.__online && window.__online.sendChat());
  document.getElementById('lobby-chat-in').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') window.__online && window.__online.sendChat();
  });
  const qc = document.getElementById('lobby-quickchat');
  QUICK_CHAT.forEach((q) => {
    const b = el('button', 'btn-ghost', q);
    b.addEventListener('click', () => {
      const c = window.__online && window.__online.client;
      if (c) c.quickChat(q);
    });
    qc.appendChild(b);
  });
}

/* ---------------- boot ---------------- */
const controller = new OnlineController();
window.__online = controller;
controller.init();
export default controller;

/* ============================================================
   NetVersus -- playable netcode versus on the reference sim.

   GGPO-style: lite-rollback session (input prediction + rollback +
   re-simulate) over a WebRTC data channel. SDP is exchanged through
   the lobby's `signal` relay (no separate signaling step).

   The sim is the deterministic REFERENCE fighter
   (game/netplay/sim/fighter-sim.js) -- integer fixed-point, checksummed.
   Local WH controls are mapped through the input codec so it FEELS
   like Western Heart inputs. Real-fighter netplay needs the combat sim
   port (docs/netcode/NETCODE-ARCHITECTURE.md) -- this is the playable
   proof that the rollback + transport + codec wiring is correct.
   ============================================================ */
export class NetVersus {
  constructor({ client, match, localId, onEnd }) {
    this.client = client;
    this.match = match;
    this.localId = localId;
    this.onEnd = onEnd;
    this.isHost = match.p1 === localId;
    this.peerId = this.isHost ? match.p2 : match.p1;
    this.localPlayer = this.isHost ? 0 : 1;
    this.session = null;
    this.transport = null;
    this.ctl = null;
    this.running = false;
    this.raf = 0;
    this.acc = 0;
    this.last = 0;
    this.keys = new Set();
    this.pressed = new Set();
    this._keyDown = (e) => {
      if (['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','Space'].includes(e.code)) e.preventDefault();
      if (!e.repeat) this.pressed.add(e.code);
      this.keys.add(e.code);
    };
    this._keyUp = (e) => { this.keys.delete(e.code); };
    this._wireBuf = new Uint8Array(8 + 4 * 2 * 4);
  }

  async start() {
    const [
      { createSession, packInputs, unpackInputs },
      { createHost, createJoiner },
      sim,
    ] = await Promise.all([
      import('../netplay/vendor/lite-rollback/src/index.js'),
      import('../netplay/vendor/lite-rollback-webrtc/src/index.js'),
      import('../netplay/sim/fighter-sim.js'),
    ]);
    this._rb = { createSession, packInputs, unpackInputs };
    this._sim = sim;
    this._buildOverlay();

    // ---- WebRTC handshake through the lobby relay ----
    if (this.isHost) {
      this.ctl = createHost({});
      this._status('creating offer…');
      const offer = await this.ctl.createOffer();
      this.client.signalTo(this.peerId, { kind: 'offer', sdp: offer });
      this._status('offer sent — waiting for answer…');
      await new Promise((resolve, reject) => {
        this._awaitAnswer = resolve;
        setTimeout(() => reject(new Error('answer timeout (15s)')), 15000);
      });
      await this.ctl.acceptAnswer(this._answerSdp);
    } else {
      this._status('waiting for host offer…');
      await new Promise((resolve, reject) => {
        this._awaitOffer = resolve;
        setTimeout(() => reject(new Error('offer timeout (15s)')), 15000);
      });
      this.ctl = createJoiner({});
      const answer = await this.ctl.acceptOffer(this._offerSdp);
      this.client.signalTo(this.peerId, { kind: 'answer', sdp: answer });
      this._status('answer sent — connecting…');
    }
    this.transport = await this.ctl.onOpen;
    this.transport.onMessage((payload) => {
      unpackInputs(this.session, payload, (player, frame, input) =>
        this.session.feedRemoteInput(player, frame, input));
    });

    // ---- rollback session on the reference sim ----
    this.session = createSession({
      capacity: 120,
      fields: sim.FIELDS,
      numPlayers: 2,
      inputWords: 1,
      inputDelay: 2, // 33ms head start — the single biggest rollback reducer
      simulate: sim.fighterSimulate,
      onDesync: (f) => console.warn('[netplay] DESYNC at frame', f),
    });
    this.session.setLocalPlayer(this.localPlayer);
    sim.initFighterState(this.session.fields);

    window.addEventListener('keydown', this._keyDown);
    window.addEventListener('keyup', this._keyUp);
    this.running = true;
    this.last = performance.now();
    this._status(this.isHost ? 'connected — you are P1 (gold)' : 'connected — you are P2 (blue)');
    const loop = (t) => {
      if (!this.running) return;
      this.raf = requestAnimationFrame(loop);
      this.acc += Math.min(100, t - this.last); this.last = t;
      while (this.acc >= 1000 / 60) {
        this.acc -= 1000 / 60;
        this._tick();
      }
    };
    this.raf = requestAnimationFrame(loop);
  }

  /** Incoming lobby `signal` messages route here from the controller. */
  onSignal(from, data) {
    if (from !== this.peerId || !data) return;
    if (data.kind === 'offer' && this._awaitOffer) {
      this._offerSdp = data.sdp;
      const r = this._awaitOffer; this._awaitOffer = null; r();
    } else if (data.kind === 'answer' && this._awaitAnswer) {
      this._answerSdp = data.sdp;
      const r = this._awaitAnswer; this._awaitAnswer = null; r();
    }
  }

  _readInput() {
    const k = this.keys;
    const left = k.has('KeyA') || k.has('ArrowLeft');
    const right = k.has('KeyD') || k.has('ArrowRight');
    const pressed = [];
    for (const code of this.pressed) {
      if (code === 'KeyJ') pressed.push('1');
      else if (code === 'KeyK') pressed.push('2');
      else if (code === 'KeyU') pressed.push('3');
      else if (code === 'KeyI') pressed.push('4');
    }
    this.pressed.clear();
    return encodeInput({
      axisX: left && !right ? -1 : right && !left ? 1 : 0,
      up: k.has('KeyW') || k.has('ArrowUp'),
      down: false,
      block: k.has('KeyS') || k.has('ArrowDown') || k.has('Space'),
      pressed,
    });
  }

  _tick() {
    const { packInputs } = this._rb;
    const s = this.session;
    if (!s) return;
    s.setLocalInput(inputWordToSimBits(this._readInput()));
    s.step();
    if (this.transport && s.frame() > 0) {
      const n = packInputs(s, this._wireBuf, s.frame() - 1, 1 << this.localPlayer, 4);
      this.transport.send(this._wireBuf.subarray(0, n));
    }
    this._render();
    this._hud();
    // round over -> winner maps back to lobby player ids
    if (s.fields.flags[0] & 1) {
      const p1Won = s.fields.hp[0] > 0;
      const winnerId = p1Won ? this.match.p1 : this.match.p2;
      const done = this.onEnd;
      this.onEnd = null;
      this.destroy();
      if (done) done(winnerId);
    }
  }

  destroy() {
    this.running = false;
    cancelAnimationFrame(this.raf);
    window.removeEventListener('keydown', this._keyDown);
    window.removeEventListener('keyup', this._keyUp);
    try { this.transport && this.transport.close(); } catch { /* noop */ }
    try { this.ctl && this.ctl.close(); } catch { /* noop */ }
    const o = document.getElementById('wh-netversus');
    if (o) o.remove();
    this.session = null;
  }

  /* ---------- overlay ---------- */

  _buildOverlay() {
    document.getElementById('wh-netversus')?.remove();
    const o = document.createElement('div');
    o.id = 'wh-netversus';
    o.className = 'wh-netversus';
    o.innerHTML = `
      <div class="hud"><span id="nv-status">starting…</span>
        <span>frame <b id="nv-frame">–</b></span>
        <span>confirmed <b id="nv-conf">–</b></span>
        <span>rollbacks <b id="nv-rb">–</b></span>
        <span>checksum <b id="nv-sum">–</b></span></div>
      <canvas id="nv-canvas" width="1000" height="420"></canvas>
      <div class="keys">A/D move · W jump · S/Space block · J/K/U/I = LP/RP/LK/RK ·
        rollback netcode proof on the reference sim</div>
      <button class="btn-ghost" id="nv-quit">QUIT MATCH</button>`;
    document.body.appendChild(o);
    o.querySelector('#nv-quit').addEventListener('click', () => {
      const done = this.onEnd; this.onEnd = null;
      // quitting counts as a loss for the quitter
      const winnerId = this.localId === this.match.p1 ? this.match.p2 : this.match.p1;
      this.destroy();
      if (done) done(winnerId);
    });
    this._cv = o.querySelector('#nv-canvas');
    this._ctx = this._cv.getContext('2d');
  }

  _status(t) {
    const s = document.getElementById('nv-status');
    if (s) s.textContent = t;
  }

  _hud() {
    const s = this.session;
    if (!s) return;
    const set = (id, v) => { const e = document.getElementById(id); if (e) e.textContent = v; };
    set('nv-frame', s.frame());
    set('nv-conf', s.confirmedFrame());
    set('nv-rb', s.stats.rollbacks);
    set('nv-sum', s.confirmedFrame() >= 0
      ? (s.checksumAt(s.confirmedFrame()) >>> 0).toString(16) : '–');
  }

  _render() {
    const sim = this._sim, s = this.session, ctx = this._ctx;
    if (!sim || !s || !ctx) return;
    const { FP, ST, STAGE, ATTACKS } = sim;
    const f = s.fields;
    const SX = 1000 / 960, GROUND_Y = 330;
    ctx.fillStyle = '#0d0d12'; ctx.fillRect(0, 0, 1000, 420);
    ctx.fillStyle = '#1a1a22'; ctx.fillRect(0, GROUND_Y + 2, 1000, 88);
    for (let p = 0; p < 2; p++) {
      const bx = p === 0 ? 20 : 620, bw = 360;
      ctx.fillStyle = '#2a2a30'; ctx.fillRect(bx, 16, bw, 18);
      const frac = Math.max(0, f.hp[p]) / STAGE.HP;
      ctx.fillStyle = p === 0 ? '#ffd400' : '#4da3ff';
      const wpx = bw * frac;
      ctx.fillRect(p === 0 ? bx : bx + bw - wpx, 16, wpx, 18);
    }
    ctx.fillStyle = '#e0e0ea'; ctx.font = '20px monospace'; ctx.textAlign = 'center';
    ctx.fillText(String(Math.ceil(f.timer[0] / 60)), 500, 32);
    const colors = ['#ffd400', '#4da3ff'];
    const labels = [
      this.localPlayer === 0 ? 'P1 (you)' : 'P1',
      this.localPlayer === 1 ? 'P2 (you)' : 'P2',
    ];
    for (let p = 0; p < 2; p++) {
      const px = (f.pos[p] / FP) * SX, py = GROUND_Y + (f.y[p] / FP);
      const w = 34, h = f.state[p] === ST.JUMP ? 64 : 78;
      ctx.globalAlpha = f.state[p] === ST.KO ? 0.45 : 1;
      ctx.fillStyle = colors[p];
      ctx.fillRect(px - w / 2, py - h, w, h);
      ctx.beginPath(); ctx.arc(px, py - h - 10, 11, 0, Math.PI * 2); ctx.fill();
      if (f.state[p] === ST.ATTACK) {
        const a = ATTACKS[f.atk[p]];
        const elapsed = a ? (a.su + a.ac + a.rec) - f.stateT[p] : 0;
        const active = a && elapsed >= a.su && elapsed < a.su + a.ac;
        ctx.fillStyle = active ? '#ff3b30' : '#ffd400';
        ctx.fillRect(f.facing[p] === 1 ? px + w / 2 : px - w / 2 - 26, py - h + 18, 26, 10);
        ctx.fillStyle = colors[p];
      }
      ctx.globalAlpha = 1;
      ctx.fillStyle = '#7a7a8a'; ctx.font = '11px monospace';
      ctx.fillText(labels[p], px, py + 16);
    }
    if (f.flags[0] & 1) {
      ctx.fillStyle = '#ff3b30'; ctx.font = 'bold 44px monospace';
      const w = f.hp[0] > 0 ? 'P1 WINS' : 'P2 WINS';
      ctx.fillText(w, 500, 200);
    }
  }
}
