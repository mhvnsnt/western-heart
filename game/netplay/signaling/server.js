// signaling/server.js -- minimal WebRTC signaling server for the netplay demo.
//
// Room codes pair exactly 2 peers. After the data channel opens, all game
// traffic is peer-to-peer; this server only relays SDP + ICE.
//
//   npm install        # installs `ws`
//   node server.js     # listens on :8765
//
// Protocol (JSON over ws):
//   -> { t: 'join', room: 'ABCD' }            join (or create) a room
//   <- { t: 'joined', room, peers: n }        ack; peers = occupants incl. you
//   <- { t: 'peer', n: 2 }                    a second peer joined (host starts offer)
//   -> { t: 'signal', room, data: {...} }     relayed verbatim to the other peer
//   <- { t: 'signal', data: {...} }
//   <- { t: 'full' }                          room already has 2 peers
//   <- { t: 'left' }                          the other peer disconnected

import { createServer } from 'node:http';
import { WebSocketServer } from 'ws';

const PORT = process.env.PORT || 8765;
const rooms = new Map(); // room -> Set<ws>

function roomCode() {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
  let c = '';
  for (let i = 0; i < 4; i++) c += chars[(Math.random() * chars.length) | 0];
  return rooms.has(c) ? roomCode() : c;
}

const wss = new WebSocketServer({ noServer: true });
const server = createServer((req, res) => {
  if (req.url === '/health') { res.writeHead(200); res.end('ok'); return; }
  res.writeHead(404); res.end('signaling server: connect with websocket');
});
server.on('upgrade', (req, socket, head) => wss.handleUpgrade(req, socket, head, ws => wss.emit('connection', ws)));

wss.on('connection', ws => {
  let room = null;
  ws.on('message', raw => {
    let msg;
    try { msg = JSON.parse(raw); } catch { return; }
    if (msg.t === 'join') {
      room = (msg.room || '').toUpperCase() || roomCode();
      if (!rooms.has(room)) rooms.set(room, new Set());
      const peers = rooms.get(room);
      if (peers.size >= 2) { ws.send(JSON.stringify({ t: 'full', room })); return; }
      peers.add(ws);
      ws.send(JSON.stringify({ t: 'joined', room, peers: peers.size }));
      for (const p of peers) if (p !== ws) p.send(JSON.stringify({ t: 'peer', n: peers.size }));
      console.log(`room ${room}: ${peers.size}/2`);
    } else if (msg.t === 'signal' && room && rooms.has(room)) {
      for (const p of rooms.get(room)) if (p !== ws) p.send(JSON.stringify({ t: 'signal', data: msg.data }));
    }
  });
  ws.on('close', () => {
    if (!room || !rooms.has(room)) return;
    const peers = rooms.get(room);
    peers.delete(ws);
    for (const p of peers) p.send(JSON.stringify({ t: 'left' }));
    if (peers.size === 0) rooms.delete(room);
    console.log(`room ${room}: ${peers.size}/2`);
  });
});

server.listen(PORT, () => console.log(`netplay signaling on :${PORT}`));
