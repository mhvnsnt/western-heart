// signaling/server.js -- WebRTC signaling + lobby server for Western Heart netplay.
//
// Two protocols share this server:
//
//   v1 (original demo): room codes pair exactly 2 peers.
//     -> { t: 'join', room: 'ABCD' }            join (or create) a room
//     <- { t: 'joined', room, peers: n }        ack; peers = occupants incl. you
//     <- { t: 'peer', n: 2 }                    a second peer joined (host starts offer)
//     -> { t: 'signal', room, data: {...} }     relayed verbatim to the other peer
//     <- { t: 'signal', data: {...} }
//     <- { t: 'full' }                          room already has 2 peers
//     <- { t: 'left' }                          the other peer disconnected
//
//   v2 (lobbies -- TTT2 player matches + SFV battle lounges):
//     <- { t: 'welcome', id }                   server-assigned player id
//     -> { t: 'list-lobbies', seq }             lobby directory
//     <- { t: 'lobby-list', seq, lobbies: [...] }
//     -> { t: 'create-lobby', seq, name, settings, playerName }
//     -> { t: 'join-lobby', seq, room, playerName, password, spectate }
//     <- { t: 'lobby-state', seq?, lobby }      full lobby snapshot (broadcast on change)
//     <- { t: 'error', seq?, reason }
//     -> { t: 'leave-lobby' }
//     -> { t: 'ready', ready }                  broadcast via lobby-state
//     -> { t: 'character', charId }             broadcast via lobby-state
//     -> { t: 'fight-request', target }         TTT2 World Arena challenge
//     <- { t: 'fight-request', from, fromName }
//     -> { t: 'fight-accept'|'fight-decline', target }
//     -> { t: 'start-match', p1, p2 }           host only
//     <- { t: 'match-start', p1, p2, room }
//     -> { t: 'report-result', winner }         -> { t: 'match-end', winner }
//     -> { t: 'signal', target, data }          WebRTC mesh relay (SDP/ICE)
//     <- { t: 'signal', from, data }
//     -> { t: 'chat', text, preset? }           -> { t: 'chat', from, fromName, text }
//     -> { t: 'bracket', bracket }             host: tournament bracket broadcast
//     <- { t: 'bracket-update', bracket }
//     -> { t: 'quick-match', seq, playerName }  TTT2 quick-match queue
//     <- { t: 'quick-found', seq, room }        paired -> auto-lobby
//     -> { t: 'leave-queue' }
//
// Game traffic is peer-to-peer; the server only relays signaling + lobby
// state. Passwords are compared in cleartext here -- this is a prototype
// relay, not an auth system (production: TLS + hashed passwords + accounts).
//
//   npm install        # installs `ws`
//   node server.js     # listens on :8765
//
// Protocol notes: lobby rooms and v1 rooms share the code namespace but
// never mix -- a connection in a v2 lobby ignores v1 messages and vice
// versa.

import { createServer } from 'node:http';
import { WebSocketServer } from 'ws';

const PORT = process.env.PORT || 8765;
const MAX_LOBBY = 8; // SFV battle lounge size

const v1rooms = new Map(); // room -> Set<ws> (original 2-peer demo)
const lobbies = new Map(); // room -> lobby object (v2)
const queue = [];          // quick-match queue: [{ ws, id, name }]
let nextId = 1;

function roomCode() {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
  let c = '';
  for (let i = 0; i < 4; i++) c += chars[(Math.random() * chars.length) | 0];
  return (v1rooms.has(c) || lobbies.has(c)) ? roomCode() : c;
}

const send = (ws, obj) => {
  if (ws.readyState === 1) ws.send(JSON.stringify(obj));
};

/* ---------------- v2 lobby helpers ---------------- */

function publicLobby(l) {
  return {
    room: l.room, name: l.name, host: l.host,
    settings: { ...l.settings, password: undefined }, // never leak the password
    players: l.players.map((p) => ({ ...p })),
    inMatch: l.inMatch,
  };
}

function directoryEntry(l) {
  return {
    room: l.room, name: l.name,
    players: l.players.length, maxPlayers: l.settings.maxPlayers,
    hasPassword: !!l.settings.password, ranked: !!l.settings.ranked,
    inMatch: l.inMatch,
  };
}

function broadcastLobby(lobby) {
  const snap = { t: 'lobby-state', lobby: publicLobby(lobby) };
  for (const p of lobby.players) send(p.ws, snap);
}

function findPlayerLobby(ws) {
  for (const l of lobbies.values()) {
    if (l.players.some((p) => p.ws === ws)) return l;
  }
  return null;
}

function seatFor(lobby, ws, name, spectate) {
  const fighters = lobby.players.filter((p) => p.role !== 'spectator').length;
  const wantSpectate = spectate || fighters >= lobby.settings.maxPlayers;
  return {
    id: ws._pid, name, ws,
    role: wantSpectate ? 'spectator' : (lobby.players.length === 0 ? 'host' : 'player'),
    ready: false, seat: lobby.players.length, character: null, title: null,
  };
}

function removeFromLobby(ws, lobby) {
  const i = lobby.players.findIndex((p) => p.ws === ws);
  if (i < 0) return;
  const [gone] = lobby.players.splice(i, 1);
  // reseat
  lobby.players.forEach((p, s) => { p.seat = s; });
  if (lobby.players.length === 0) { lobbies.delete(lobby.room); return; }
  if (gone.role === 'host' || lobby.host === gone.id) {
    // host migrates to the longest-seated player (SFV lounge keeps running)
    const next = lobby.players.filter((p) => p.role !== 'spectator')[0] || lobby.players[0];
    next.role = 'host';
    lobby.host = next.id;
  }
  broadcastLobby(lobby);
}

function tryQuickMatch() {
  while (queue.length >= 2) {
    const a = queue.shift(), b = queue.shift();
    if (a.ws.readyState !== 1) continue;
    if (b.ws.readyState !== 1) { queue.unshift(a); break; }
    const room = roomCode();
    const lobby = {
      room, name: `${a.name} vs ${b.name}`, host: a.id,
      settings: { maxPlayers: 2, rotation: 1, allowSpectate: true, ranked: false, password: null },
      players: [], inMatch: false, quick: true,
    };
    for (const [q, role] of [[a, 'host'], [b, 'player']]) {
      lobby.players.push({
        id: q.id, name: q.name, ws: q.ws, role,
        ready: true, seat: lobby.players.length, character: null, title: null,
      });
      q.ws._lobbyRoom = room;
    }
    lobbies.set(room, lobby);
    send(a.ws, { t: 'quick-found', seq: a.seq, room });
    send(b.ws, { t: 'quick-found', seq: b.seq, room });
    broadcastLobby(lobby);
    console.log(`quick-match: ${a.name} vs ${b.name} -> ${room}`);
  }
}

/* ---------------- server ---------------- */

const wss = new WebSocketServer({ noServer: true });
const server = createServer((req, res) => {
  if (req.url === '/health') { res.writeHead(200); res.end('ok'); return; }
  if (req.url === '/lobbies') {
    res.writeHead(200, { 'content-type': 'application/json' });
    res.end(JSON.stringify([...lobbies.values()].map(directoryEntry)));
    return;
  }
  res.writeHead(404); res.end('signaling server: connect with websocket');
});
server.on('upgrade', (req, socket, head) => wss.handleUpgrade(req, socket, head, ws => wss.emit('connection', ws)));

wss.on('connection', ws => {
  ws._pid = 'p' + (nextId++);
  ws._v1room = null;
  ws._lobbyRoom = null;
  send(ws, { t: 'welcome', id: ws._pid });

  ws.on('message', raw => {
    let msg;
    try { msg = JSON.parse(raw); } catch { return; }
    const seq = msg.seq;

    /* ----- v1 demo protocol (unchanged) ----- */
    if (msg.t === 'join') {
      const room = (msg.room || '').toUpperCase() || roomCode();
      if (!v1rooms.has(room)) v1rooms.set(room, new Set());
      const peers = v1rooms.get(room);
      if (peers.size >= 2) { send(ws, { t: 'full', room }); return; }
      peers.add(ws);
      ws._v1room = room;
      send(ws, { t: 'joined', room, peers: peers.size });
      for (const p of peers) if (p !== ws) send(p, { t: 'peer', n: peers.size });
      console.log(`v1 room ${room}: ${peers.size}/2`);
      return;
    }
    if (msg.t === 'signal' && msg.room && v1rooms.has(msg.room) && !msg.target) {
      // v1 broadcast signal (demo)
      for (const p of v1rooms.get(msg.room)) if (p !== ws) send(p, { t: 'signal', data: msg.data });
      return;
    }

    /* ----- v2 lobby protocol ----- */
    if (msg.t === 'list-lobbies') {
      send(ws, { t: 'lobby-list', seq, lobbies: [...lobbies.values()].map(directoryEntry) });
      return;
    }
    if (msg.t === 'create-lobby') {
      const room = roomCode();
      const s = msg.settings || {};
      const lobby = {
        room,
        name: String(msg.name || 'LOUNGE').slice(0, 40),
        host: ws._pid,
        settings: {
          maxPlayers: Math.min(MAX_LOBBY, Math.max(2, s.maxPlayers || 8)),
          rotation: Math.min(5, Math.max(1, s.rotation || 2)),
          allowSpectate: s.allowSpectate !== false,
          ranked: !!s.ranked,
          password: s.password ? String(s.password).slice(0, 24) : null,
        },
        players: [{
          id: ws._pid, name: String(msg.playerName || 'SOUL').slice(0, 16),
          ws, role: 'host', ready: false, seat: 0, character: null, title: null,
        }],
        inMatch: false,
      };
      lobbies.set(room, lobby);
      ws._lobbyRoom = room;
      send(ws, { t: 'lobby-state', seq, lobby: publicLobby(lobby) });
      console.log(`lobby ${room} "${lobby.name}" created by ${msg.playerName}`);
      return;
    }
    if (msg.t === 'join-lobby') {
      const lobby = lobbies.get(String(msg.room || '').toUpperCase());
      if (!lobby) { send(ws, { t: 'error', seq, reason: 'lobby not found' }); return; }
      if (lobby.settings.password && lobby.settings.password !== msg.password) {
        send(ws, { t: 'error', seq, reason: 'wrong password' }); return;
      }
      const seat = seatFor(lobby, ws, String(msg.playerName || 'SOUL').slice(0, 16), !!msg.spectate);
      if (seat.role === 'spectator' && !lobby.settings.allowSpectate) {
        send(ws, { t: 'error', seq, reason: 'spectating is disabled in this lounge' }); return;
      }
      lobby.players.push(seat);
      ws._lobbyRoom = lobby.room;
      send(ws, { t: 'lobby-state', seq, lobby: publicLobby(lobby) });
      broadcastLobby(lobby);
      console.log(`lobby ${lobby.room}: ${seat.name} joined as ${seat.role}`);
      return;
    }
    if (msg.t === 'leave-lobby') {
      const lobby = findPlayerLobby(ws);
      if (lobby) { removeFromLobby(ws, lobby); ws._lobbyRoom = null; }
      return;
    }
    const lobby = findPlayerLobby(ws);
    const me = lobby ? lobby.players.find((p) => p.ws === ws) : null;

    if (msg.t === 'ready' && me) {
      me.ready = !!msg.ready;
      broadcastLobby(lobby);
      return;
    }
    if (msg.t === 'character' && me) {
      me.character = String(msg.charId || '').slice(0, 32) || null;
      broadcastLobby(lobby);
      return;
    }
    if (msg.t === 'title' && me) {
      me.title = String(msg.title || '').slice(0, 24) || null;
      broadcastLobby(lobby);
      return;
    }
    if (msg.t === 'fight-request' && me) {
      const target = lobby.players.find((p) => p.id === msg.target);
      if (target) send(target.ws, { t: 'fight-request', from: me.id, fromName: me.name });
      return;
    }
    if ((msg.t === 'fight-accept' || msg.t === 'fight-decline') && me) {
      const target = lobby.players.find((p) => p.id === msg.target);
      if (target) send(target.ws, { t: msg.t, from: me.id, fromName: me.name });
      return;
    }
    if (msg.t === 'start-match' && me) {
      if (lobby.host !== me.id) { send(ws, { t: 'lobby-error', reason: 'only the host can do that' }); return; }
      const p1 = lobby.players.find((p) => p.id === msg.p1);
      const p2 = lobby.players.find((p) => p.id === msg.p2);
      if (!p1 || !p2) { send(ws, { t: 'lobby-error', reason: 'both fighters must be in the lounge' }); return; }
      lobby.inMatch = true;
      for (const p of lobby.players) send(p.ws, { t: 'match-start', p1: p1.id, p2: p2.id, room: lobby.room });
      broadcastLobby(lobby);
      console.log(`lobby ${lobby.room}: match ${p1.name} vs ${p2.name}`);
      return;
    }
    if (msg.t === 'report-result' && me) {
      if (!lobby.inMatch) return; // idempotent: only the first report counts
      lobby.inMatch = false;
      for (const p of lobby.players) send(p.ws, { t: 'match-end', winner: msg.winner });
      broadcastLobby(lobby);
      const w = lobby.players.find((p) => p.id === msg.winner);
      console.log(`lobby ${lobby.room}: winner ${w ? w.name : msg.winner}`);
      return;
    }
    if (msg.t === 'signal' && msg.target && me) {
      const target = lobby.players.find((p) => p.id === msg.target);
      if (target) send(target.ws, { t: 'signal', from: me.id, data: msg.data });
      return;
    }
    if (msg.t === 'chat' && me) {
      const text = String(msg.text || '').slice(0, 140);
      if (!text) return;
      for (const p of lobby.players) send(p.ws, { t: 'chat', from: me.id, fromName: me.name, text });
      return;
    }
    if (msg.t === 'bracket' && me) {
      if (lobby.host !== me.id) { send(ws, { t: 'lobby-error', reason: 'only the host can do that' }); return; }
      for (const p of lobby.players) send(p.ws, { t: 'bracket-update', bracket: msg.bracket });
      return;
    }
    if (msg.t === 'quick-match') {
      queue.push({ ws, id: ws._pid, name: String(msg.playerName || 'SOUL').slice(0, 16), seq });
      tryQuickMatch();
      return;
    }
    if (msg.t === 'leave-queue') {
      const i = queue.findIndex((q) => q.ws === ws);
      if (i >= 0) queue.splice(i, 1);
      return;
    }
  });

  ws.on('close', () => {
    // v1 cleanup (unchanged)
    if (ws._v1room && v1rooms.has(ws._v1room)) {
      const peers = v1rooms.get(ws._v1room);
      peers.delete(ws);
      for (const p of peers) send(p, { t: 'left' });
      if (peers.size === 0) v1rooms.delete(ws._v1room);
      console.log(`v1 room ${ws._v1room}: ${peers.size}/2`);
    }
    // v2 cleanup
    const qi = queue.findIndex((q) => q.ws === ws);
    if (qi >= 0) queue.splice(qi, 1);
    const lobby = findPlayerLobby(ws);
    if (lobby) {
      const me = lobby.players.find((p) => p.ws === ws);
      removeFromLobby(ws, lobby);
      console.log(`lobby ${lobby.room}: ${me ? me.name : '?'} left`);
    }
  });
});

server.listen(PORT, () => console.log(`netplay signaling+lobby on :${PORT}`));
