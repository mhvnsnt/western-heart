// Minimal static server for game/ (keep-alive, concurrent). Run: node server.mjs [port]
import { createServer } from 'http';
import { readFileSync, statSync, existsSync } from 'fs';
import { extname, join } from 'path';
const ROOT = '/home/hatch/workspace/fix3/loadspeed';
const PORT = Number(process.argv[2] || 8901);
const CT = { '.html':'text/html', '.js':'text/javascript', '.css':'text/css', '.json':'application/json', '.png':'image/png', '.jpg':'image/jpeg', '.glb':'model/gltf-binary', '.wasm':'application/wasm' };
createServer((req, res) => {
  let p = decodeURIComponent(req.url.split('?')[0]);
  if (p.endsWith('/')) p += 'index.html';
  const f = join(ROOT, p);
  if (!f.startsWith(ROOT) || !existsSync(f) || !statSync(f).isFile()) { res.writeHead(404); res.end('nf'); return; }
  const body = readFileSync(f);
  res.writeHead(200, { 'Content-Type': CT[extname(f)] || 'application/octet-stream', 'Content-Length': body.length, 'Cache-Control': 'no-store', 'Connection': 'keep-alive' });
  res.end(body);
}).listen(PORT, () => console.log('serving', ROOT, 'on', PORT));
