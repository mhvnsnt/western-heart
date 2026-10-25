// Node environment for importing the game's own ES modules (fighter.js, t3anims.js, movesets.js)
// without a browser: maps the bare 'three' specifier to the vendored build (as game/index.html's
// import map does) and serves fetch() from the repo's game/ folder (the page root).
// Used by tools/anim/attack_anim_audit.mjs and test/attack-anim.test.mjs.
// Usage: `await import('./node_game_env.mjs')` BEFORE importing any game module.
import { register } from 'node:module';
import { readFile } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

export const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..', '..');
export const GAME = join(ROOT, 'game');

const hooks = `
const THREE_URL = ${JSON.stringify(pathToFileURL(join(GAME, 'vendor/three.module.js')).href)};
const ADDONS = ${JSON.stringify(pathToFileURL(join(GAME, 'vendor/addons/')).href)};
export async function resolve(spec, ctx, next) {
  if (spec === 'three') return { url: THREE_URL, shortCircuit: true };
  if (spec.startsWith('three/addons/')) return { url: ADDONS + spec.slice(13), shortCircuit: true };
  return next(spec, ctx);
}`;
register('data:text/javascript,' + encodeURIComponent(hooks));

const g = globalThis;
if (!g.window) g.window = g;
if (!g.localStorage) {
  const s = {};
  g.localStorage = { getItem: k => (k in s ? s[k] : null), setItem: (k, v) => { s[k] = String(v); }, removeItem: k => { delete s[k]; } };
}
// fetch(): page-relative paths resolve against game/, file:// URLs read the file. Network URLs are refused.
g.fetch = async (url) => {
  const u = String(url);
  let p;
  if (u.startsWith('file:')) p = fileURLToPath(u);
  else if (/^[a-z]+:/i.test(u)) throw new Error('node_game_env: no network fetch (' + u + ')');
  else {
    const rel = u.replace(/^\.?\//, '');
    p = join(GAME, rel);
    // WH_FETCH_OVERLAY=<dir>: a file at <dir>/<page-relative path> wins (e.g. a bank's rows.pack.json
    // from an older commit, to audit the code against the data as it was).
    const ov = process.env.WH_FETCH_OVERLAY;
    if (ov) { const q = join(ov, rel); try { await readFile(q); p = q; } catch (e) { /* not overlaid */ } }
  }
  try {
    const buf = await readFile(p);
    return { ok: true, status: 200, json: async () => JSON.parse(buf.toString('utf8')), text: async () => buf.toString('utf8') };
  } catch (e) {
    return { ok: false, status: 404, json: async () => { throw new Error('404 ' + u); }, text: async () => '' };
  }
};
