/* Combat-systems tests (2026-10-24, revised onto main's GAP-FILL LANE 1).
   Run from repo root: node --test game/tests/combat-systems.test.mjs
   Pure rules come from game/js/combat-core.js; Soul Urge list support
   from game/js/soulurge.js (its audio.js import is headless-safe: no
   imports, no top-level window use). fighter.js needs THREE so it is
   verified by source anchors, not import — same convention as the
   original file. Buttons: LP1/RP2/LK3/RK4. */
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import {
  isPowerCrushMove, isLowHit, powerCrushAbsorbs, POWER_CRUSH_ARMOR_DELAY,
  isScrewMove, isTornadoMove, extenderKind, SCREW_SLUMP_STUN, TORNADO_BOUND_STUN,
  WALL_SPLAT_MAX_HITS, WALL_SPLAT_STUN, nextWallSplatState,
  requiresItemOf, itemGate,
} from '../js/combat-core.js';
import { ensureUrgeMoves, listUrgeEngagers, SoulUrge, URGE_ENGAGER_TIME } from '../js/soulurge.js';

const here = path.dirname(fileURLToPath(import.meta.url));
const read = (rel) => readFileSync(path.join(here, rel), 'utf-8');

test('Power Crush absorbs mid/high, loses to low/throw/unblockable/Rage Art, honors armor delay', () => {
  const pc = { powerCrush: true };
  const mid = { hit_level: 'mid' }, high = { hit_level: 'high' };
  const low = { hit_level: 'low' }, grab = { isGrab: true };
  const ub = { unblockable: true }, ra = { hit_level: 'mid', rageArt: true };
  assert.equal(isPowerCrushMove(pc), true);
  assert.equal(isPowerCrushMove({}), false);
  assert.equal(isPowerCrushMove({ power_crush: true }), true);
  assert.equal(isLowHit(low), true);
  assert.equal(isLowHit(mid), false);
  assert.equal(powerCrushAbsorbs(pc, 'active', 0.2, mid), true);
  assert.equal(powerCrushAbsorbs(pc, 'active', 0.2, high), true);
  assert.equal(powerCrushAbsorbs(pc, 'active', 0.2, low), false);
  assert.equal(powerCrushAbsorbs(pc, 'active', 0.2, grab), false);
  assert.equal(powerCrushAbsorbs(pc, 'active', 0.2, ub), false);
  assert.equal(powerCrushAbsorbs(pc, 'active', 0.2, ra), false);
  assert.equal(powerCrushAbsorbs({}, 'active', 0.2, mid), false);
  // Armor delay: startup absorbs only after ~8 frames (wavu).
  assert.equal(powerCrushAbsorbs(pc, 'startup', 0, mid), false);
  assert.equal(powerCrushAbsorbs(pc, 'startup', POWER_CRUSH_ARMOR_DELAY, mid), true);
  assert.equal(powerCrushAbsorbs(pc, 'recovery', 0.5, mid), false);
});

test('Screw/Tornado share one extender slot; wall splat drops after max hits', () => {
  assert.equal(isScrewMove({ screw: true }), true);
  assert.equal(isScrewMove({ tailspin: true }), true);
  assert.equal(isTornadoMove({ tornado: true }), true);
  assert.equal(isScrewMove({}), false);
  assert.equal(extenderKind({ screw: true, tornado: true }), 'screw');
  assert.equal(extenderKind({ tornado: true }), 'tornado');
  assert.equal(extenderKind({}), null);
  assert.equal(SCREW_SLUMP_STUN, 0.9);
  assert.equal(TORNADO_BOUND_STUN, 0.8);
  assert.equal(WALL_SPLAT_MAX_HITS, 3);
  assert.equal(WALL_SPLAT_STUN, 0.55);
  assert.equal(nextWallSplatState(2), 'wallsplat');
  assert.equal(nextWallSplatState(3), 'knockdown');
});

test('Item-move gate: unflagged always available, flagged needs the item', () => {
  assert.equal(requiresItemOf({}), null);
  assert.equal(requiresItemOf({ requiresItem: 'belt' }), 'belt');
  assert.equal(itemGate({}, []).blocked, false);
  assert.equal(itemGate({ requiresItem: 'belt' }, []).blocked, true);
  assert.equal(itemGate({ requiresItem: 'belt' }, ['belt']).blocked, false);
  assert.equal(itemGate({ requiresItem: 'belt' }, [{ id: 'belt' }]).blocked, false);
  assert.equal(itemGate({ requiresItem: 'belt' }, ['cape']).blocked, true);
});

test('Soul Urge: per-character engager lists beat the single-key fallback', () => {
  const mk = (moves, extra = {}) => ({ moves, ...extra });
  const api = (ms) => ({ playedMoveset: () => ms, getFighterMoveset: () => ms });
  const listed = mk({
    'f+2': { damage: 20, knock: 4, move_class: 'strike' },
    'df+1': { damage: 15, knock: 3, move_class: 'strike' },
    'grab': { damage: 25, knock: 9, isGrab: true },
    '1': { damage: 10, knock: 2, move_class: 'strike' },
  }, { urgeEngagers: ['f+2', 'df+1', 'grab', 'missing-key'] });
  assert.equal(ensureUrgeMoves('x', api(listed)), true);
  assert.equal(listed.moves['f+2'].urgeEngager, true);
  assert.equal(listed.moves['df+1'].urgeEngager, true);
  assert.equal(listed.moves.grab.urgeEngager, undefined); // grabs can never engager
  assert.deepEqual(listUrgeEngagers(listed), ['f+2', 'df+1']);
  // Fallback: no list -> single highest-knock non-grab strike.
  const fb = mk({
    '1': { damage: 10, knock: 2, move_class: 'strike' },
    'f+2': { damage: 20, knock: 5, move_class: 'strike' },
    'grab': { damage: 25, knock: 9, isGrab: true },
  });
  ensureUrgeMoves('x', api(fb));
  assert.deepEqual(listUrgeEngagers(fb), ['f+2']);
  // A listed engager actually activates Soul Urge on hit (T8: 2 pips, 15 s).
  const p1 = { hp: 50, maxHp: 100, facing: 1, _urgeUsed: false, _urgeOn: false };
  const p2 = { state: 'idle', onGround: true };
  const dir = new SoulUrge({ p1, p2 });
  dir.onHit(p1, listed.moves['f+2']);
  assert.equal(p1._urgeOn, true);
  assert.equal(p1._urgePips, 2);
  assert.equal(p1._urgeT, URGE_ENGAGER_TIME);
  // Timer ticks by dt and expires (never NaN).
  dir.update(1);
  assert.equal(p1._urgeT, URGE_ENGAGER_TIME - 1);
  assert.ok(Number.isFinite(p1._urgeT));
});

test('Wiring anchors: fighter crush-pool delta, HUD white bar, bridge forward', () => {
  const fighter = read('../js/fighter.js');
  assert.match(fighter, /damage absorbed by a Power Crush becomes/);
  assert.match(fighter, /_addRecoverable\(Math\.max\(0, Math\.min\(dmg, this\.maxHp - this\.hp/);
  assert.match(fighter, /_extenderUsed/);
  assert.match(fighter, /wallsplat/);
  const main = read('../js/main.js');
  assert.match(main, /f\._recoverable/);
  const bridge = read('../js/ui-wh-bridge.js');
  assert.match(bridge, /recoverable: x\._recoverable/);
  const ui = read('../ui-wh/ui.js');
  assert.match(ui, /bar\.querySelector\("b"\)/);
  const idx = read('../ui-wh/index.html');
  assert.equal((idx.match(/<b style="width:0%"><\/b>/g) || []).length, 2);
  const css = read('../ui-wh/ui.css');
  assert.match(css, /\.bar b \{[^}]*rgba\(255,255,255,0\.55\)/);
  const manifest = JSON.parse(read('../ui_sources.json'));
  const hudFight = manifest.screens['hud-fight'] || manifest['hud-fight'];
  const files = hudFight.files || [];
  assert.ok(files.includes('game/ui-wh/ui.css'), 'ui.css must be listed under hud-fight');
});

test('Pantera flags: exactly the proven moves, zero Tornado flags', () => {
  const pantera = JSON.parse(read('../assets/movesets/pantera.json'));
  const moves = pantera.moves || {};
  const pc = Object.keys(moves).filter((k) => moves[k] && moves[k].powerCrush);
  const sc = Object.keys(moves).filter((k) => moves[k] && moves[k].screw);
  const to = Object.keys(moves).filter((k) => moves[k] && moves[k].tornado);
  assert.deepEqual(pc.sort(), ['db+1+2', 'db+1+2,3+4', 'uf+3+4'].sort());
  assert.deepEqual(sc, ['SS.2']);
  assert.deepEqual(to, []);
});
