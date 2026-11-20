// tools/auto_rig/list_models.mjs — print every fighter / attire model the game loads, from the game's own
// MODEL_URLS (game/js/assets.js), as JSON [[key, game-relative url, repo path, bytes], ...]. Used by
// tools/auto_rig/batch_audit.py so the audit covers exactly what the game ships.
//   node tools/auto_rig/list_models.mjs > models.json
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
await import(path.join(ROOT, 'tools/anim/node_game_env.mjs'));
const A = await import(path.join(ROOT, 'game/js/assets.js'));
const urls = A.MODEL_URLS;
if (!urls) throw new Error('game/js/assets.js has no MODEL_URLS export');
const rows = [];
for (const [key, url] of Object.entries(urls)) {
  const abs = path.resolve(ROOT, 'game', url);
  let bytes = -1;
  try { bytes = fs.statSync(abs).size; } catch (e) { /* not in this checkout */ }
  rows.push([key, url, path.relative(ROOT, abs), bytes]);
}
process.stdout.write(JSON.stringify(rows) + '\n');
