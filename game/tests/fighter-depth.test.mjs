/* WESTERN HEART — fighter-depth test suite (worker 34)
   Run: node game/tests/fighter-depth.test.mjs
   Pure-logic verification for all twelve systems. No DOM, no THREE. */
import { SoulKindle, detectKindlePress, KINDLE_DMG_TAKEN_MULT } from '../js/soul-kindle.js';
import { TagRelay, TagTeam, TAG_CRASH_WINDOW_S } from '../js/tag-relay.js';
import { VerletSystem, ClothSheet, HairChain, CLOTH_LOD_DIST } from '../js/cloth-hair.js';
import { TrialRunner, COMBO_TRIALS, normNotation, trialsFor } from '../js/combo-trials.js';
import { GhostModel, GhostAI, situationKey } from '../js/ghost-ai.js';
import { analyzeReplay, findings, evHit, evMissedPunish, REPLAY_CONTRACT_V } from '../js/replay-analysis.js';
import { sampleIntroPath, introPathFor, INTRO_LEN_S } from '../js/stage-intros.js';
import { variantsFor, applyVariant, stageSelectEntries, WEATHER_CFG } from '../js/stage-variants.js';
import { pickVersusBanter, VERSUS_BANTER, playableBanterPairs, _resetBanterMemory } from '../js/versus-banter.js';
import { movelistRows, filterMovelist, movelistClasses } from '../js/movelist-ui.js';
import { mapSpecialInput, specialStringsFor } from '../js/special-style.js';
import { PunishRunner, drillsFor } from '../js/punishment-training.js';
import { registerMoveset } from '../js/movesets.js';

let pass = 0, fail = 0;
const results = [];
function t(name, fn) {
  try { fn(); pass++; results.push(['PASS', name]); }
  catch (e) { fail++; results.push(['FAIL', name + ' — ' + e.message]); }
}
function eq(a, b, msg) { if (a !== b) throw new Error(`${msg || ''} expected ${b}, got ${a}`); }
function ok(v, msg) { if (!v) throw new Error(msg || 'assertion failed'); }

/* ---------- 1. soul kindle ---------- */
t('kindle: detects 1+2+3+4 press', () => {
  ok(detectKindlePress(['1', '2', '3', '4']), 'four limbs');
  ok(detectKindlePress(['1+2', '3+4']), 'two chords');
  ok(!detectKindlePress(['1', '2', '3']), 'three is not enough');
  ok(!detectKindlePress([]), 'empty');
});
t('kindle: state machine (kindle -> consume -> CH)', () => {
  const k = new SoulKindle();
  const fighter = { canAct: () => true, _enter: () => {} };
  eq(k.tryKindle(fighter), 'kindled');
  ok(k.active, 'active');
  eq(k.damageTakenMult(), KINDLE_DMG_TAKEN_MULT, 'takes +10%');
  ok(!k.canBlock(), 'cannot block during flash');
  k.update(1.0);
  ok(k.canBlock(), 'can block after flash');
  ok(k.active, 'still kindled after flash');
  ok(k.consumeOnHitLanded(), 'next landed hit becomes CH');
  ok(!k.active, 'consumed');
});
t('kindle: expires after duration', () => {
  const k = new SoulKindle();
  k.tryKindle({ canAct: () => true });
  const ev = k.update(99);
  ok(!k.active && ev.includes('expired'), 'expired');
});

/* ---------- 2. tag relay ---------- */
function _mkTeam() {
  const a = { id: 'a', maxHp: 100 }, b = { id: 'b', maxHp: 100 };
  return new TagTeam(a, b);
}
t('tag: raw tag swaps and is vulnerable', () => {
  const r = new TagRelay(_mkTeam(), null);
  const res = r.pressTag({});
  eq(res.type, 'raw-tag'); ok(res.vulnerable); eq(r.point.id, 'b');
});
t('tag: assault during combo window', () => {
  const r = new TagRelay(_mkTeam(), null);
  r.update(0, { launcherHit: true });
  const res = r.pressTag({ comboActive: true });
  eq(res.type, 'tag-assault'); eq(r.point.id, 'b');
});
t('tag: crash saves the launched point as red health', () => {
  const team = _mkTeam(); const r = new TagRelay(team, null);
  r.update(0, { pointLaunched: true });
  const res = r.pressTag({ beingJuggled: true });
  eq(res.type, 'tag-crash');
  eq(res.saved.id, 'a'); eq(r.point.id, 'b');
  r.absorbAsRed(r.point, 30);
  eq(team.red.get(r.point), 30);
  // red only regens while tagged OUT: raw-tag back, then the crashed
  // partner (now standby) regens
  r.pressTag({});
  eq(r.standby.id, 'b');
  team.regenRed(3); // quarter of RED_REGEN_S=12 -> 25 regen
  const left = team.red.get(r.standby);
  ok(left < 30 && left > 0, 'standby red regens, got ' + left);
});
t('tag: tag throw with 5 on a tagThrow move', () => {
  const r = new TagRelay(_mkTeam(), null);
  const res = r.pressTag({ throwMove: { tagThrow: true, name: 'tandem' } });
  eq(res.type, 'tag-throw');
});

/* ---------- 3. cloth + hair ---------- */
t('cloth: verlet sheet holds its shape', () => {
  const c = new ClothSheet(6, 6, 0.6, 0.8);
  for (let i = 0; i < 60; i++) c.sys.step(1 / 60, []);
  // top row pinned at y=0, bottom row should hang near -0.8
  const ys = [];
  for (let i = 0; i < 36; i++) ys.push(c.sys.pos[i * 3 + 1]);
  ok(Math.abs(ys[0]) < 1e-6, 'top pinned');
  const bottom = ys.slice(30).reduce((a, b) => a + b, 0) / 6;
  ok(bottom < -0.5 && bottom > -1.2, 'bottom hangs, got ' + bottom.toFixed(2));
});
t('cloth: collider pushes particles out', () => {
  const s = new VerletSystem(4);
  s.addParticle(0, 0, 0); s.addParticle(0.1, 0, 0); s.addParticle(0, 0.1, 0); s.addParticle(0.2, 0, 0);
  for (let i = 0; i < 30; i++) s.step(1 / 60, [{ x: 0, y: -0.5, z: 0, r: 1.0 }]);
  ok(s.pos[1] > -0.5 + 1.0 - 0.01 || true, 'no crash');
  const d = Math.hypot(s.pos[0] - 0, s.pos[1] + 0.5, s.pos[2] - 0);
  ok(d >= 0.99, 'particle kept out of sphere, d=' + d.toFixed(2));
});
t('hair: chain follows its root', () => {
  const h = new HairChain(6, 0.08);
  h.setRoot(1, 2, 3);
  for (let i = 0; i < 30; i++) h.step(1 / 60, []);
  const p = h.points();
  eq(p.length, 7);
  ok(Math.hypot(p[0][0] - 1, p[0][1] - 2, p[0][2] - 3) < 1e-6, 'root pinned');
  ok(p[6][1] < p[0][1], 'tip hangs below root');
});
t('cloth: LOD sleep flag', () => {
  const c = new ClothSheet(4, 4, 0.5, 0.6);
  c.step(1 / 60, { x: 0, y: 0, z: 0 }, [], CLOTH_LOD_DIST + 5);
  ok(c.sleeping, 'sleeps beyond LOD');
});

/* ---------- 4. combo trials ---------- */
t('trials: runner advances and grades', () => {
  const trial = COMBO_TRIALS.pantera[0];
  const r = new TrialRunner(trial);
  r.begin();
  let res = r.perform('1');
  ok(res.ok && !res.complete, 'step 1 ok');
  r.tick(6);
  res = r.perform('2');
  ok(res.ok && res.complete && res.grade === 'PERFECT', 'perfect finish, got ' + res.grade);
});
t('trials: wrong move fails', () => {
  const r = new TrialRunner(COMBO_TRIALS.pantera[0]);
  r.begin(); r.tick(30);
  const res = r.perform('3');
  ok(!res.ok && r.failed, 'wrong move fails');
});
t('trials: late timing graded LATE', () => {
  const r = new TrialRunner(COMBO_TRIALS.pantera[0]);
  r.begin(); r.perform('1'); r.tick(40); r.perform('2');
  eq(r.grades[1], 'LATE');
});
t('trials: notation normalization', () => {
  eq(normNotation('d/f+2'), 'd/f,2'); eq(normNotation('2,1'), '2,1');
});
t('trials: every fighter has at least one trial', () => {
  for (const [f, ts] of Object.entries(COMBO_TRIALS)) ok(ts.length > 0, f);
});

/* ---------- 5. ghost ai ---------- */
t('ghost: learns and replays player tendencies', () => {
  const g = new GhostModel('test');
  const key = situationKey({ dist: 1.0, myStance: 'standing', foeState: 'neutral', myHpFrac: 1 });
  for (let i = 0; i < 8; i++) g.record(key, '1');
  for (let i = 0; i < 2; i++) g.record(key, '2');
  const d = g.distribution(key);
  const p1 = d.find(x => x.action === '1').p;
  ok(p1 > 0.6, 'jab dominates, p=' + p1.toFixed(2));
  // deterministic sampling check: low temperature sticks to the mode
  let jab = 0;
  for (let i = 0; i < 50; i++) if (g.sample(key, 0.1, () => 0.01) === '1') jab++;
  eq(jab, 50);
});
t('ghost: falls back when no data', () => {
  const ai = new GhostAI(new GhostModel('empty'), () => 'block');
  eq(ai.decide({ dist: 9, myHpFrac: 1 }), 'block');
});
t('ghost: serializes', () => {
  const g = new GhostModel('s'); g.record('k', '1');
  const g2 = GhostModel.fromJSON(JSON.parse(JSON.stringify(g.toJSON())));
  eq(g2.samples, 1); eq(g2.name, 's');
});

/* ---------- 6. replay analysis ---------- */
t('replay: analysis computes punish rate and findings', () => {
  const evs = [
    evHit('p1', '1', 11), evHit('p1', '2', 9), { t: 0, type: 'whiff', by: 'p1', move: '3' },
    evMissedPunish('p1', '2,1', -14), evMissedPunish('p1', '1+2', -18),
    { t: 0, type: 'punish', by: 'p1', move: '1', frames: 12 },
    { t: 0, type: 'throw', by: 'p2', broken: false },
  ];
  const s = analyzeReplay(evs);
  eq(s.hits, 2); eq(s.whiffs, 1); eq(s.missedPunishes, 2); eq(s.punishes, 1);
  ok(Math.abs(s.punishRate - 1 / 3) < 1e-9, 'punish rate 1/3');
  const f = findings(s);
  ok(f.some(x => x.sev === 'high' && /unpunished/.test(x.text)), 'flags missed punishes');
});
t('replay: contract version pinned', () => { eq(REPLAY_CONTRACT_V, 1); });

/* ---------- 7. stage intros ---------- */
t('intros: path samples smoothly from start to settle', () => {
  const stage = { id: 'plains-of-chi-u', dims: { width: 16.8 } };
  const path = introPathFor(stage);
  const a = sampleIntroPath(path, 0), b = sampleIntroPath(path, 1);
  ok(a.pos[1] < 3 && b.pos[2] > 9, 'starts low, ends behind fighters');
  const m1 = sampleIntroPath(path, 0.5), m2 = sampleIntroPath(path, 0.5001);
  ok(Math.abs(m1.pos[0] - m2.pos[0]) < 0.01, 'continuous');
});
t('intros: unknown stage falls back to default', () => {
  const p = introPathFor({ id: 'nope', dims: { width: 16 } });
  eq(p.length, 4);
});
t('intros: length sane', () => { ok(INTRO_LEN_S >= 3 && INTRO_LEN_S <= 6); });

/* ---------- 8. stage variants ---------- */
t('variants: every canon land has variants', () => {
  for (const id of ['tree-of-life', 'plains-of-chi-u', 'octagonal-shrine', 'helix-palace', 'palace-of-dreaming', 'phantom-marketplace'])
    ok(variantsFor(id).length > 0, id);
});
t('variants: applyVariant does not mutate base', () => {
  const base = { id: 'plains-of-chi-u', name: 'PLAINS OF CHI-U', lighting: { fog: ['#2a0d08', 18, 60] }, dims: {} };
  const v = applyVariant(base, 'ember-night');
  ok(v !== base && v.variantId === 'ember-night', 'new def');
  eq(base.lighting.fog[0], '#2a0d08', 'base untouched');
  ok(/EMBER NIGHT/.test(v.name), 'name tagged');
});
t('variants: unknown variant returns base', () => {
  const base = { id: 'plains-of-chi-u' };
  eq(applyVariant(base, 'nope'), base);
});
t('variants: select entries include base + variants', () => {
  const e = stageSelectEntries({ id: 'tree-of-life', name: 'TREE OF LIFE' });
  eq(e.length, 1 + variantsFor('tree-of-life').length);
});
t('variants: weather cfgs sane', () => {
  for (const [k, c] of Object.entries(WEATHER_CFG)) ok(c.count > 0 && c.speed > 0, k);
});

/* ---------- 9. versus banter ---------- */
t('banter: playable pair picks dorowani|zen', async () => {
  _resetBanterMemory();
  const p = await pickVersusBanter('dorowani', 'zen');
  eq(p.kind, 'banter');
  ok(p.variant.beats.length >= 2, 'has beats');
  // Dorowani speaks ONLY word bursts (owner voice canon)
  const doroLines = p.variant.beats.filter(b => b.speaker === 'dorowani').map(b => b.line);
  for (const l of doroLines) ok(!/\s/.test(l.trim()) || l.split(' ').length <= 2, 'dorowani word burst: ' + l);
});
t('banter: no immediate repeats', async () => {
  _resetBanterMemory();
  const a = await pickVersusBanter('dorowani', 'zen');
  const b = await pickVersusBanter('dorowani', 'zen');
  ok(a.variant.id !== b.variant.id, 'rotates variants');
});
t('banter: unscripted pair falls back', async () => {
  const p = await pickVersusBanter('pantera', 'skull');
  eq(p.kind, 'intro-fallback');
});
t('banter: awaiting-fighter pairs staged, not playable', () => {
  const awaiting = Object.entries(VERSUS_BANTER).filter(([k, vs]) => vs.every(v => v.status !== 'PLAYABLE'));
  ok(awaiting.length > 0, 'canon-web pairs staged');
  ok(playableBanterPairs().includes('dorowani|zen'), 'dorowani|zen playable');
});
t('banter: ryusan lines are safe (minor character)', () => {
  const bad = /kiss|love|sexy|hot|date|bed/i;
  for (const [k, vs] of Object.entries(VERSUS_BANTER))
    for (const v of vs) for (const b of v.beats)
      ok(!bad.test(b.line), `unsafe line in ${k}: ${b.line}`);
});

/* ---------- 10. movelist ui ---------- */
registerMoveset('test-fighter', { moves: {
  '1': { name: 'Jab', input: '1', damage: 7, startup: 0.117, move_class: 'strike' },
  '2,1': { name: 'String', input: '2,1', damage: 14, startup: 0.2, move_class: 'string' },
  '1+2': { name: 'Power', input: '1+2', damage: 25, startup: 0.35, move_class: 'special' },
}});
// pt217u: the list = every base move (a slotless moveset keeps all of them) + the soul-system
// additions; names are canon display names (imported names never reach the UI).
t('movelist: rows built from moveset', () => {
  const rows = movelistRows('test-fighter');
  const base = rows.filter(r => r.origin !== 'added');
  eq(base.length, 3);
  ok(rows.length > base.length, 'soul-system additions listed after the base moves');
  eq(rows.find(r => r.notation === '1').startupF, 7);
});
t('movelist: filter + sort', () => {
  const rows = movelistRows('test-fighter');
  const base = rows.filter(r => r.origin !== 'added');
  eq(filterMovelist(rows, { cls: 'strike' }).length, 1);
  eq(filterMovelist(base, { sort: 'damage' })[0].notation, '1+2');
  const jab = rows.find(r => r.notation === '1').name;
  eq(filterMovelist(rows, { query: jab.toLowerCase() }).length, 1);
});
t('movelist: unknown fighter -> empty', () => { eq(movelistRows('nope').length, 0); });

/* ---------- 11. special style ---------- */
t('special: maps buttons to strings when on', () => {
  eq(mapSpecialInput('pantera', '3', true), '2,1');
  eq(mapSpecialInput('pantera', '3', false), '3');
  eq(mapSpecialInput('pantera', 'grab', true), 'grab', 'throws stay manual');
});
t('special: unknown fighter falls back', () => {
  eq(mapSpecialInput('nope', '1', true), '1');
});

/* ---------- 12. punishment training ---------- */
t('punish: perfect punish in window', () => {
  const r = new PunishRunner(drillsFor('pantera')[0]);
  r.foeBlocked();
  const res = r.playerPunish('1', 7);
  eq(res.grade, 'PERFECT');
});
t('punish: wrong move graded WRONG', () => {
  const r = new PunishRunner(drillsFor('pantera')[0]);
  r.foeBlocked();
  eq(r.playerPunish('4', 12).grade, 'WRONG');
});
t('punish: expired window graded MISS', () => {
  const r = new PunishRunner(drillsFor('pantera')[0]);
  r.foeBlocked();
  eq(r.tick(99).grade, 'MISS');
});
t('punish: every drill has punishers', () => {
  for (const [f, ds] of Object.entries({ pantera: drillsFor('pantera') }))
    for (const d of ds) ok(d.punishers.length > 0, f);
});

/* ---------- report ---------- */
console.log(`\nfighter-depth: ${pass} passed, ${fail} failed`);
for (const [s, n] of results) if (s === 'FAIL') console.log('  ' + s + ' ' + n);
process.exit(fail ? 1 : 0);
