// test-lobby.mjs -- node tests for the lobby client state machine.
// A fake in-memory server implements just enough of the v2 protocol to
// exercise create/join/ready/rotation/match-start and the directory.
// Run: node --test game/netplay/lobby/test-lobby.mjs   (from repo root)
import test from 'node:test';
import assert from 'node:assert/strict';
import { LobbyClient, LOBBY_DEFAULTS, QUICK_CHAT } from './lobby-protocol.js';

/** Minimal fake socket pair: client sock <-> server handler. */
function makePair(server) {
  const clientSock = {
    onopen: null, onclose: null, onmessage: null,
    send(raw) { server._receive(clientSock, raw); },
  };
  clientSock._deliver = (obj) => clientSock.onmessage(JSON.stringify(obj));
  return clientSock;
}

/** Tiny fake server: lobbies, seats, ready, rotation, match-start. */
class FakeServer {
  constructor() {
    this.clients = new Map(); // sock -> { id, name }
    this.lobbies = new Map(); // room -> lobby
    this.seq = 0;
  }
  _receive(sock, raw) {
    const msg = JSON.parse(raw);
    if (!this.clients.has(sock)) {
      const id = 'p' + (++this.seq);
      this.clients.set(sock, { id, name: '?' });
      sock._deliver({ t: 'welcome', id });
    }
    const me = this.clients.get(sock);
    const reply = (obj) => sock._deliver({ ...obj, seq: msg.seq });
    const broadcast = (room, obj) => {
      for (const [s, c] of this.clients) {
        const l = this.lobbies.get(room);
        if (l && l.players.some((p) => p.id === c.id)) s._deliver(obj);
      }
    };
    const stateOf = (room) => {
      const l = this.lobbies.get(room);
      return { t: 'lobby-state', lobby: JSON.parse(JSON.stringify(l)) };
    };
    switch (msg.t) {
      case 'list-lobbies':
        reply({ t: 'lobby-list', lobbies: [...this.lobbies.values()].map((l) => ({
          room: l.room, name: l.name, players: l.players.length,
          maxPlayers: l.settings.maxPlayers, hasPassword: !!l.settings.password,
          ranked: l.settings.ranked, inMatch: !!l.inMatch,
        })) });
        break;
      case 'create-lobby': {
        const room = 'RM' + (++this.seq);
        me.name = msg.playerName;
        const lobby = {
          room, name: msg.name, host: me.id, settings: msg.settings,
          players: [{ id: me.id, name: me.name, role: 'host', ready: false, seat: 0, character: null }],
          inMatch: false,
        };
        this.lobbies.set(room, lobby);
        me.room = room;
        reply({ t: 'lobby-state', lobby });
        break;
      }
      case 'join-lobby': {
        const l = this.lobbies.get(msg.room);
        if (!l) { reply({ t: 'error', reason: 'lobby not found' }); break; }
        if (l.settings.password && l.settings.password !== msg.password) {
          reply({ t: 'error', reason: 'wrong password' }); break;
        }
        const fighters = l.players.filter((p) => p.role !== 'spectator').length;
        const wantSpectate = msg.spectate || fighters >= l.settings.maxPlayers;
        if (wantSpectate && !l.settings.allowSpectate) {
          reply({ t: 'error', reason: 'spectating is disabled in this lounge' }); break;
        }
        me.name = msg.playerName; me.room = msg.room;
        l.players.push({
          id: me.id, name: me.name,
          role: wantSpectate ? 'spectator' : 'player',
          ready: false, seat: l.players.length, character: null,
        });
        reply({ t: 'lobby-state', lobby: JSON.parse(JSON.stringify(l)) });
        broadcast(msg.room, stateOf(msg.room));
        break;
      }
      case 'ready': {
        const l = this.lobbies.get(me.room);
        const p = l.players.find((x) => x.id === me.id);
        p.ready = !!msg.ready;
        broadcast(me.room, stateOf(me.room));
        break;
      }
      case 'start-match': {
        const l = this.lobbies.get(me.room);
        if (l.host !== me.id) { sock._deliver({ t: 'lobby-error', reason: 'only the host can do that' }); break; }
        l.inMatch = true;
        broadcast(me.room, { t: 'match-start', p1: msg.p1, p2: msg.p2, room: me.room });
        break;
      }
      case 'report-result': {
        const l = this.lobbies.get(me.room);
        l.inMatch = false;
        broadcast(me.room, { t: 'match-end', winner: msg.winner });
        broadcast(me.room, stateOf(me.room));
        break;
      }
      default:
        reply({ t: 'error', reason: 'unknown message' });
    }
  }
}

function connectClient(server, name) {
  const sock = makePair(server);
  const c = new LobbyClient(sock);
  c.setName(name);
  sock.onopen();
  return c;
}

test('lobby: create -> directory lists it', async () => {
  const server = new FakeServer();
  const host = connectClient(server, 'HOST');
  await host.createLobby({ name: 'TEST LOUNGE' });
  assert.ok(host.lobby);
  assert.equal(host.lobby.name, 'TEST LOUNGE');
  assert.ok(host.isHost);
  const guest = connectClient(server, 'GUEST');
  const res = await guest.listLobbies();
  assert.equal(res.lobbies.length, 1);
  assert.equal(res.lobbies[0].name, 'TEST LOUNGE');
});

test('lobby: join, ready, rotation pair, host starts match', async () => {
  const server = new FakeServer();
  const host = connectClient(server, 'HOST');
  const p2 = connectClient(server, 'P2');
  await host.createLobby({ name: 'FIGHT CLUB' });
  const room = host.lobby.room;

  let hostSawJoin = false;
  host.on('lobby', (l) => { if (l && l.players.length === 2) hostSawJoin = true; });
  await p2.joinLobby(room);
  assert.ok(hostSawJoin, 'host should see the join broadcast');

  host.setReady(true);
  p2.setReady(true);
  // let broadcasts flush (synchronous in the fake, but be safe)
  await new Promise((r) => setTimeout(r, 10));
  assert.equal(host.readyFighters().length, 2);
  const pair = host.rotationPair();
  assert.ok(pair, 'rotation pair should exist with 2 ready fighters');
  assert.equal(pair[0].name, 'HOST', 'host (seat 0) fights first');

  let matchSeen = null;
  p2.on('match-start', (m) => { matchSeen = m; });
  host.startMatch(pair[0].id, pair[1].id);
  await new Promise((r) => setTimeout(r, 10));
  assert.ok(matchSeen, 'guest should receive match-start');
  assert.equal(matchSeen.p1, host.playerId);

  let endSeen = null;
  host.on('match-end', (m) => { endSeen = m; });
  p2.reportResult(host.playerId);
  await new Promise((r) => setTimeout(r, 10));
  assert.ok(endSeen);
  assert.equal(endSeen.winner, host.playerId);
});

test('lobby: password gate + spectator overflow', async () => {
  const server = new FakeServer();
  const host = connectClient(server, 'HOST');
  await host.createLobby({ name: 'PRIVATE', password: 'soul', maxPlayers: 1 });
  const room = host.lobby.room;
  const intruder = connectClient(server, 'INTRUDER');
  await assert.rejects(() => intruder.joinLobby(room, { password: 'wrong' }), /wrong password/);
  // maxPlayers=1 and host occupies the fighter seat -> join as spectator
  const spec = connectClient(server, 'SPEC');
  await spec.joinLobby(room, { password: 'soul', spectate: true });
  assert.equal(spec.me.role, 'spectator');
  assert.equal(spec.readyFighters().length, 0, 'spectators are not fighters');
  assert.equal(spec.rotationPair(), null);
});

test('lobby: non-host cannot start a match', async () => {
  const server = new FakeServer();
  const host = connectClient(server, 'HOST');
  const p2 = connectClient(server, 'P2');
  await host.createLobby({ name: 'CLUB' });
  await p2.joinLobby(host.lobby.room);
  let err = null;
  p2.on('error', (e) => { err = e; });
  p2.startMatch(p2.playerId, host.playerId);
  await new Promise((r) => setTimeout(r, 10));
  assert.ok(err, 'non-host start should be refused');
  assert.match(err.message, /only the host/);
});

test('lobby: quick-chat presets are sane', () => {
  assert.ok(QUICK_CHAT.length >= 3);
  assert.ok(QUICK_CHAT.every((s) => s.length <= 140));
  assert.deepEqual(Object.keys(LOBBY_DEFAULTS).sort(),
    ['allowSpectate', 'maxPlayers', 'password', 'ranked', 'rotation'].sort());
});
