// customization/profiles/index.json must list exactly the profile files present,
// so the in-fight consumer never fetches a missing profile (phantom.json 404).
import { readdirSync, readFileSync } from 'node:fs';
import assert from 'node:assert/strict';
const dir = new URL('../customization/profiles/', import.meta.url);
const files = readdirSync(dir).filter(f => f.endsWith('.json') && f !== 'index.json').map(f => f.slice(0, -5)).sort();
const idx = JSON.parse(readFileSync(new URL('index.json', dir))).profiles.slice().sort();
assert.deepEqual(idx, files, 'profiles/index.json out of sync with profile files');
assert.ok(!idx.includes('phantom'), 'phantom has no profile file');
const src = readFileSync(new URL('../game/js/customization-consumer.js', import.meta.url), 'utf8');
assert.ok(src.includes("customization/profiles/index.json") && src.includes('ids.has(fighter.char.id)'), 'consumer must gate on index');
console.log(`profiles-index: ok (${idx.length} profile(s): ${idx.join(', ')})`);
