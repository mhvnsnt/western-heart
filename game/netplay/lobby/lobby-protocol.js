// lobby-protocol.js -- Western Heart lobby client (DOM-free, node-testable).
//
// Lobby model pulls from the teardowns (see
// docs/research/online-lobby-tournament-research.md):
//   TTT2 Player Matches: Quick Match (random pair) / Custom Match (parameter
//     search over a lobby list) / Create Session (host with settings).
//     World Arena: persistent lobby rooms + fight requests + tournament room.
//   SFV Battle Lounge: owner-customized lounge -- set length before rotation,
//     password, private slots, enable/disable character select for speed
//     matches, connection-bar restriction, up to 8 players + spectators.
//
// This client speaks the signaling server's lobby protocol (v2) over any
// WebSocket-like object { send(string), onmessage, onopen, onclose }.
// Wire it to a real WebSocket in the browser, or to a fake in tests.
//
// Roles: 'host' | 'player' | 'spectator'.
// Flow: connect -> listLobbies | createLobby | joinLobby -> lobby-state
//   updates -> ready up -> host startMatch(p1, p2) -> 'match-start' event
//   (the caller then opens the WebRTC + rollback session) -> winner
//   reported -> back to lobby, rotation advances.

export const LOBBY_DEFAULTS = Object.freeze({
  maxPlayers: 8,        // SFV battle lounge size
  rotation: 2,          // sets before rotation (SFV: "length of a set")
  allowSpectate: true,  // TTT2 lobbies + SFV spectator option
  ranked: false,        // TTT2: player matches don't touch rank
  password: null,
});

export const LOBBY_ERRORS = Object.freeze({
  NOT_FOUND: 'lobby not found',
  FULL: 'lobby is full',
  BAD_PASSWORD: 'wrong password',
  NOT_HOST: 'only the host can do that',
  NO_SPECTATE: 'spectating is disabled in this lounge',
});

/**
 * LobbyClient -- state machine for one player's lobby session.
 * All network goes through `this.sock`; all state changes emit events.
 */
export class LobbyClient {
  constructor(sock = null) {
    this.sock = sock;
    this.connected = false;
    this.playerId = null;
    this.playerName = 'SOUL';
    this.lobby = null;      // latest lobby-state snapshot
    this.directory = [];    // latest lobby-list snapshot
    this.match = null;      // active match { p1, p2, room } after match-start
    this._handlers = new Map();
    this._reqSeq = 0;
    this._pending = new Map(); // seq -> { resolve, reject }
    if (sock) this.attach(sock);
  }

  attach(sock) {
    this.sock = sock;
    sock.onopen = () => { this.connected = true; this.emit('connected'); };
    sock.onclose = () => {
      this.connected = false; this.lobby = null; this.match = null;
      this.emit('disconnected');
    };
    sock.onmessage = (ev) => this._onMessage(typeof ev === 'string' ? ev : ev.data);
    // The socket may already be open (attach-after-open race).
    if (sock.readyState === 1) { this.connected = true; this.emit('connected'); }
  }

  on(event, fn) {
    if (!this._handlers.has(event)) this._handlers.set(event, []);
    this._handlers.get(event).push(fn);
    return this;
  }

  emit(event, data) {
    for (const fn of this._handlers.get(event) || []) {
      try { fn(data); } catch (e) { console.error('LobbyClient handler error:', e); }
    }
  }

  _send(obj) {
    if (!this.sock || !this.connected) throw new Error('LobbyClient: not connected');
    this.sock.send(JSON.stringify(obj));
  }

  /** Request/response helper: messages carrying `seq` get a promise. */
  _request(type, payload = {}) {
    const seq = ++this._reqSeq;
    return new Promise((resolve, reject) => {
      this._pending.set(seq, { resolve, reject });
      try { this._send({ t: type, seq, ...payload }); }
      catch (e) { this._pending.delete(seq); reject(e); }
      setTimeout(() => {
        if (this._pending.has(seq)) {
          this._pending.delete(seq);
          reject(new Error('lobby request timed out: ' + type));
        }
      }, 8000);
    });
  }

  _onMessage(raw) {
    let msg;
    try { msg = JSON.parse(raw); } catch { return; }
    // State-carrying responses update local state AND resolve the request.
    if (msg.t === 'lobby-state' || msg.t === 'lobby-list') this._applyState(msg);
    if (msg.seq && this._pending.has(msg.seq)) {
      const { resolve, reject } = this._pending.get(msg.seq);
      this._pending.delete(msg.seq);
      if (msg.t === 'error') reject(new Error(msg.reason || 'lobby error'));
      else resolve(msg);
      return;
    }
    switch (msg.t) {
      case 'welcome':
        this.playerId = msg.id;
        this.emit('welcome', msg);
        break;
      case 'lobby-list':
      case 'lobby-state':
        break; // already applied above
      case 'lobby-error':
        this.emit('error', new Error(msg.reason || 'lobby error'));
        break;
      case 'match-start':
        this.match = { p1: msg.p1, p2: msg.p2, room: msg.room };
        this.emit('match-start', this.match);
        break;
      case 'match-end':
        this.match = null;
        this.emit('match-end', msg);
        break;
      case 'fight-request':
        this.emit('fight-request', { from: msg.from, fromName: msg.fromName });
        break;
      case 'chat':
        this.emit('chat', { from: msg.from, fromName: msg.fromName, text: msg.text });
        break;
      case 'bracket-update':
        this.emit('bracket-update', msg.bracket);
        break;
      case 'signal':
        // WebRTC mesh signaling relayed through the lobby server.
        this.emit('signal', { from: msg.from, data: msg.data });
        break;
      case 'quick-found':
        this.emit('quick-found', msg);
        break;
      default:
        this.emit('unknown', msg);
    }
  }

  /** Apply a state-carrying message (lobby-state / lobby-list). */
  _applyState(msg) {
    if (msg.t === 'lobby-list') {
      this.directory = msg.lobbies || [];
      this.emit('directory', this.directory);
    } else if (msg.t === 'lobby-state') {
      this.lobby = msg.lobby;
      this.emit('lobby', this.lobby);
    }
  }

  // ---------------- player actions ----------------

  setName(name) {
    this.playerName = String(name || 'SOUL').slice(0, 16) || 'SOUL';
  }

  /** TTT2 "Custom Match": browse the directory. */
  listLobbies() { return this._request('list-lobbies'); }

  /** TTT2 "Create Session" / SFV "create Battle Lounge". */
  createLobby(opts = {}) {
    const settings = { ...LOBBY_DEFAULTS, ...opts };
    delete settings.playerName;
    return this._request('create-lobby', {
      name: String(opts.name || `${this.playerName}'S LOUNGE`).slice(0, 40),
      settings,
      playerName: this.playerName,
    });
  }

  joinLobby(room, { password = null, spectate = false } = {}) {
    return this._request('join-lobby', {
      room: String(room).toUpperCase(),
      playerName: this.playerName,
      password,
      spectate: !!spectate,
    });
  }

  leaveLobby() {
    this.lobby = null;
    this._send({ t: 'leave-lobby' });
    this.emit('lobby', null);
  }

  setReady(ready) { this._send({ t: 'ready', ready: !!ready }); }

  setCharacter(charId) { this._send({ t: 'character', charId }); }

  /** TTT2 World Arena: send a fight request to another lobby member. */
  requestFight(targetId) { this._send({ t: 'fight-request', target: targetId }); }
  acceptFight(fromId) { this._send({ t: 'fight-accept', target: fromId }); }
  declineFight(fromId) { this._send({ t: 'fight-decline', target: fromId }); }

  /** Host: start a match between two members (spectators watch). */
  startMatch(p1Id, p2Id) { this._send({ t: 'start-match', p1: p1Id, p2: p2Id }); }

  /** Either fighter: report the result; server broadcasts match-end. */
  reportResult(winnerId) { this._send({ t: 'report-result', winner: winnerId }); }

  sendChat(text) {
    const t = String(text || '').slice(0, 140);
    if (t) this._send({ t: 'chat', text: t });
  }

  /** Quick-chat presets (no moderation surface for free text in v1). */
  quickChat(preset) { this._send({ t: 'chat', text: preset, preset: true }); }

  /** Host: broadcast tournament bracket state to the lounge. */
  updateBracket(bracket) { this._send({ t: 'bracket', bracket }); }

  /** TTT2 "Quick Match": join the matchmaking queue. */
  quickMatch() { return this._request('quick-match', { playerName: this.playerName }); }
  leaveQueue() { this._send({ t: 'leave-queue' }); }

  /** WebRTC mesh: relay SDP/ICE to one peer via the server. */
  signalTo(targetId, data) { this._send({ t: 'signal', target: targetId, data }); }

  // ---------------- local helpers (no network) ----------------

  /** Am I the host of the current lobby? */
  get isHost() { return !!(this.lobby && this.lobby.host === this.playerId); }

  /** My seat in the current lobby, if any. */
  get me() {
    if (!this.lobby) return null;
    return (this.lobby.players || []).find((p) => p.id === this.playerId) || null;
  }

  /** Non-spectator members who are ready. */
  readyFighters() {
    if (!this.lobby) return [];
    return (this.lobby.players || []).filter((p) => p.role !== 'spectator' && p.ready);
  }

  /** Next two fighters in rotation order (SFV set-rotation feel). */
  rotationPair() {
    const fs = this.readyFighters();
    if (fs.length < 2) return null;
    // Stable order: host first, then join order (server assigns seat).
    const sorted = fs.slice().sort((a, b) => a.seat - b.seat);
    return [sorted[0], sorted[1]];
  }
}

export const QUICK_CHAT = Object.freeze([
  'Good fight!',
  'Rematch?',
  'Nice combo.',
  'One more.',
  'GG — that surge was clean.',
]);
