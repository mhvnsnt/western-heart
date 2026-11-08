// dw_server.mjs — a static server for the DW overlay / game verification.
// Use this instead of `python3 -m http.server`: python's server drops
// concurrent module fetches (HTTP/1.0 + a 5-deep listen backlog RSTs
// connections when the game's ~100-file module graph loads at once), which
// surfaces in the browser as "Failed to fetch dynamically imported module"
// and window.__game never setting. Node's http server handles the concurrency.
// usage: node dw_server.mjs [root] [port]   (defaults: /tmp/dw-overlay, 8765)
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';

const ROOT = process.argv[2] || '/tmp/dw-overlay';
const PORT = Number(process.argv[3] || 8765);
const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript',
  '.css': 'text/css', '.json': 'application/json', '.png': 'image/png', '.jpg': 'image/jpeg',
  '.glb': 'model/gltf-binary', '.gltf': 'model/gltf+json', '.wasm': 'application/wasm',
  '.svg': 'image/svg+xml', '.ico': 'image/x-icon', '.webmanifest': 'application/manifest+json' };
const server = http.createServer((req, res) => {
  const url = decodeURIComponent(req.url.split('?')[0]);
  let p = path.join(ROOT, url === '/' ? 'index.html' : url);
  if (!p.startsWith(ROOT)) { res.writeHead(403); res.end(); return; }
  fs.stat(p, (err, st) => {
    if (err || !st.isFile()) { res.writeHead(404); res.end('404'); return; }
    res.writeHead(200, { 'Content-Type': MIME[path.extname(p)] || 'application/octet-stream',
      'Content-Length': st.size, 'Access-Control-Allow-Origin': '*' });
    fs.createReadStream(p).pipe(res);
  });
});
server.listen(PORT, '127.0.0.1', () => console.log(`dw-server on http://127.0.0.1:${PORT}/ (root ${ROOT})`));
