// test_music.mjs — offline node tests for the WH adaptive score core.
// Run: node test_music.mjs   (exit 0 = green)
import { composeBars, layerGains, markovMelody, mulberry32, STATES } from './wh_adaptive_music.mjs';

let failures = 0;
const ok = (cond, name) => { console.log(`${cond ? 'PASS' : 'FAIL'}  ${name}`); if (!cond) failures++; };

// 1. Determinism: same seed -> identical output (reproducible score).
const a = JSON.stringify(composeBars('combat', 1234, 4));
const b = JSON.stringify(composeBars('combat', 1234, 4));
ok(a === b, 'deterministic output for same seed');
ok(JSON.stringify(composeBars('combat', 1234, 4)) !== JSON.stringify(composeBars('combat', 9999, 4)),
  'different seeds differ');

// 2. MIDI range sanity.
for (const st of Object.keys(STATES)) {
  const { events } = composeBars(st, 42, 2);
  ok(events.every((e) => e.midi >= 0 && e.midi <= 127 && e.vel > 0 && e.vel <= 1), `${st}: midi/vel in range`);
  ok(events.length > 0, `${st}: non-empty`);
}

// 3. Intensity ordering: combat denser than menu.
const nCombat = composeBars('combat', 7, 4).events.length;
const nMenu = composeBars('menu', 7, 4).events.length;
ok(nCombat > nMenu, `combat (${nCombat} events) denser than menu (${nMenu})`);

// 4. State layers match config ('drums' meta-layer emits kick/snare/hat).
for (const st of Object.keys(STATES)) {
  const layers = new Set(composeBars(st, 7, 4).events.map((e) => e.layer));
  const expected = STATES[st].layers.flatMap((l) => (l === 'drums' ? ['kick', 'snare', 'hat'] : [l]));
  ok(expected.every((l) => layers.has(l)), `${st}: expected layers present`);
}

// 5. layerGains crossfade endpoints.
const g0 = layerGains('menu', 'combat', 0);
const g1 = layerGains('menu', 'combat', 1);
ok(g0.drums === 0 && g1.drums === 1, 'crossfade 0->1 endpoints');
const gm = layerGains('menu', 'combat', 0.5);
ok(Math.abs(gm.drums - 0.5) < 1e-9, 'crossfade midpoint');

// 6. Markov melody stays in scale degrees, respects density.
const rand = mulberry32(5);
const mel = markovMelody(rand, [0, 2, 4, 5, 7], 2, 1.0);
ok(mel.length === 16, 'full-density melody fills 16 slots/2bars');
ok(mel.every((n) => n.degree >= 0 && n.degree < 5), 'degrees in scale');

// 7. Unknown state throws.
let threw = false;
try { composeBars('boss', 1, 1); } catch { threw = true; }
ok(threw, 'unknown state throws');

console.log(failures === 0 ? '\nALL GREEN' : `\n${failures} FAILURES`);
process.exit(failures === 0 ? 0 : 1);
