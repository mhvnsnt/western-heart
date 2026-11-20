/* Node module-customization hooks for the brawler sim test.
 * brawler.js is imported from a data: URL (always ESM); every import it
 * makes is redirected here to a headless stub. The module under test is
 * the REAL game/js/brawler.js, byte for byte. */
import { fileURLToPath, pathToFileURL } from 'node:url';
import { dirname, join } from 'node:path';

const STUBS = join(dirname(fileURLToPath(import.meta.url)), 'brawler-sim-stubs');
const MAP = {
  'three': 'three.mjs',
  './fighter.js': 'fighter.mjs',
  './assets.js': 'assets.mjs',
  './stages.js': 'stages.mjs',
  './movesets.js': 'movesets.mjs',
  './t3anims.js': 't3anims.mjs',
  './modes.js': 'modes.mjs',
  './audio.js': 'audio.mjs',
  './customization-consumer.js': 'customization-consumer.mjs',
  './menus.js': 'menus.mjs',
};

export async function resolve(specifier, context, nextResolve) {
  if (MAP[specifier] && context.parentURL.startsWith('data:')) {
    return { url: pathToFileURL(join(STUBS, MAP[specifier])).href, shortCircuit: true };
  }
  return nextResolve(specifier, context);
}
