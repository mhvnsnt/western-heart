// Lane B Phase 4b local server.
// Serves the western-heart tree at CURRENT main (pinned commit via
// PIN_SHA env, default: main) by proxying jsDelivr in-memory, with
// the audit-run checkout on disk as fallback. Nothing is written
// to disk. Logs every served path + byte size + source so the
// proof can state exactly what the browser loaded.
import http from 'http';
import fs from 'fs';
import path from 'path';

const PORT = 8765;
const PIN = process.env.PIN_SHA || 'main';
const CDN = 'https://cdn.jsdelivr.net/gh/mhvnsnt/western-heart@' + PIN + '/';
const DISK_ROOT = process.env.HOME + '/workspace/_claude-wip-finish-20261102/audit-run';
const MIME = {
  '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8',
  '.mjs': 'text/javascript; charset=utf-8', '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8', '.glb': 'model/gltf-binary',
  '.gltf': 'model/gltf+json', '.png': 'image/png', '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg', '.webp': 'image/webp', '.svg': 'image/svg+xml',
  '.wasm': 'application/wasm', '.bin': 'application/octet-stream',
  '.mp3': 'audio/mpeg', '.ogg': 'audio/ogg', '.wav': 'audio/wav',
  '.txt': 'text/plain; charset=utf-8', '.md': 'text/plain; charset=utf-8',
};
const cache = new Map(); // path -> { buf, type }
let cacheBytes = 0;
const MAX_CACHE = 220 * 1024 * 1024;

async function fromCdn(rel) {
  const r = await fetch(CDN + rel);
  if (!r.ok) return null;
  const buf = Buffer.from(await r.arrayBuffer());
  return buf;
}
function fromDisk(rel) {
  const p = path.join(DISK_ROOT, rel);
  try {
    const st = fs.statSync(p);
    if (st.isFile() && st.size > 0) return fs.readFileSync(p);
  } catch (e) { /* miss */ }
  return null;
}

const server = http.createServer(async (req, res) => {
  try {
    const u = new URL(req.url, 'http://x');
    let rel = decodeURIComponent(u.pathname).replace(/^\/+/, '');
    if (!rel || rel.endsWith('/')) rel += 'index.html';
    if (rel.includes('..')) { res.writeHead(400); res.end('bad'); return; }
    const ext = path.extname(rel).toLowerCase();
    const type = MIME[ext] || 'application/octet-stream';
    if (cache.has(rel)) {
      const { buf } = cache.get(rel);
      console.log('HIT ', rel, buf.length);
      res.writeHead(200, { 'Content-Type': type, 'Content-Length': buf.length, 'Access-Control-Allow-Origin': '*' });
      res.end(buf);
      return;
    }
    // CDN first (current main), disk fallback (audit-run checkout).
    let buf = null, src = '';
    try { buf = await fromCdn(rel); if (buf) src = 'cdn'; } catch (e) { /* fall through */ }
    if (!buf) { buf = fromDisk(rel); if (buf) src = 'disk'; }
    if (!buf) {
      console.log('404 ', rel);
      res.writeHead(404, { 'Content-Type': 'text/plain' });
      res.end('not found: ' + rel);
      return;
    }
    console.log('SERV', src, rel, buf.length);
    if (cacheBytes + buf.length < MAX_CACHE) { cache.set(rel, { buf }); cacheBytes += buf.length; }
    res.writeHead(200, { 'Content-Type': type, 'Content-Length': buf.length, 'Access-Control-Allow-Origin': '*' });
    res.end(buf);
  } catch (e) {
    console.log('ERR ', req.url, e.message);
    try { res.writeHead(500); res.end('err'); } catch (_) {}
  }
});
server.listen(PORT, '127.0.0.1', () => console.log('laneB server on ' + PORT + ' pin=' + PIN + ' cdn=' + CDN));
