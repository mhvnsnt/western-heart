// ANIMATION GATE test (owner t117u). Run: node test/anim-gate.test.mjs
// Simulates a fight for EVERY roster fighter through the real createT3Actions() path with show
// clips injected, and asserts 0 show clips ever become/play as fight actions; then checks
// that crossover happens only through game/data/crossover.json.
import { readFileSync, readdirSync, statSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, '..');
const G = await import(join(root, 'game', 'js', 'anim-gate.js'));
const T3 = await import(join(root, 'game', 'js', 't3anims.js'));
const xo = JSON.parse(readFileSync(join(root, 'game', 'data', 'crossover.json'), 'utf8'));
G.setCrossover(xo);
const console_warn = console.warn; console.warn = () => {};

let pass = 0, fail = 0;
const ok = (c, n) => { if (c) pass++; else { fail++; console.log('FAIL -', n); } };

const roster = [...readFileSync(join(root, 'game', 'js', 'roster-full.js'), 'utf8').matchAll(/\bid:\s*'([^']+)'/g)].map(m => m[1]);
ok(roster.length >= 20, `roster parsed (${roster.length} fighters)`);

const FIGHT_CLIPS = ['stance','intro','light','medium','heavy','grab','block','hit','launch','ko','win','walkFwd','walkBack','dash','crouch','crouchHold','backdash','jumpUp','jumpFwd','jumpBack','sidestepA','sidestepB','row:12','row:40'];
const SHOW_SLOTS = xo.show_to_fight.clips;
const THREE = { LoopPingPong: 2, LoopRepeat: 1, LoopOnce: 0 };
function fakeMixer(played) {
  return { clipAction(clip) { const a = { clip, setLoop() {}, setEffectiveWeight() {}, play() { played.push(clip); return a; } }; return a; } };
}
let rng = 12345; const rand = (n) => { rng = (rng * 1103515245 + 12345) & 0x7fffffff; return rng % n; };

let showPlayed = 0, totalPlays = 0;
for (const id of roster) {
  const clips = {};
  for (const n of FIGHT_CLIPS) clips[n] = { name: n, userData: { loop: n === 'stance' } };
  // inject show clips under every naming style a loader might use
  for (const s of SHOW_SLOTS) {
    clips['show:' + s] = G.markShowClip({ name: s, userData: {} }, s);
    clips[s] = G.markShowClip({ name: s, userData: {} }, s);           // same bare name as a show clip
    clips[`anims/show/${id}/${s}`] = { name: s, userData: {} };          // path-style, untagged
  }
  G.setAnimContext(G.CTX.FIGHT);
  const played = [];
  const actions = T3.createT3Actions(fakeMixer(played), clips, THREE);
  // simulate 600 frames of random inputs: request any clip name (fight or show)
  const names = Object.keys(clips);
  for (let f = 0; f < 600; f++) {
    const want = names[rand(names.length)];
    const a = actions[want];
    if (a) { a.play(); totalPlays++; }
  }
  const bad = played.filter(c => G.isShowClip(c) || SHOW_SLOTS.includes(c.name) && !FIGHT_CLIPS.includes(c.name));
  showPlayed += bad.length;
  ok(bad.length === 0, `${id}: 0 show clips played in FIGHT (got ${bad.length})`);
  ok(FIGHT_CLIPS.every(n => actions[n]), `${id}: every moveset clip still available in FIGHT`);
  ok(Object.keys(actions).every(n => FIGHT_CLIPS.includes(n)), `${id}: actions contain only moveset clips`);
}
ok(G.gateLog.some(e => e.ctx === 'FIGHT' && e.set === 'show' && e.verdict === 'rejected'), 'rejections are logged');

// crossover only via allowlist
for (const ctx of ['INTRO_OUTRO', 'CUTSCENE', 'SHOW']) {
  for (const s of SHOW_SLOTS) ok(G.checkClip('show:' + s, G.markShowClip({ name: s }, s), ctx).ok, `show ${s} allowed in ${ctx}`);
  ok(!G.checkClip('show:secret_dance', G.markShowClip({ name: 'secret_dance' }, 'secret_dance'), ctx).ok, `unlisted show clip blocked in ${ctx}`);
  for (const n of FIGHT_CLIPS) ok(G.checkClip(n, { name: n }, ctx).ok === xo.fight_to_show.clips.includes(n), `fight ${n} in ${ctx} follows allowlist`);
}
let threw = false; try { G.setCrossover({ ...xo, show_to_fight: { ...xo.show_to_fight, allowed_contexts: ['FIGHT'] } }); } catch { threw = true; }
ok(threw, 'crossover.json can never allow show clips into FIGHT');

// static: nothing in game/js loads anims/show except the gate
for (const f of readdirSync(join(root, 'game', 'js'))) {
  if (!f.endsWith('.js') || f === 'anim-gate.js') continue;
  const src = readFileSync(join(root, 'game', 'js', f), 'utf8');
  ok(!src.includes('anims/show'), `${f} does not reference anims/show directly`);
}
ok(readFileSync(join(root, 'game', 'js', 't3anims.js'), 'utf8').includes('checkClip(name, clip, CTX.FIGHT)'), 'createT3Actions is gated');
ok(readFileSync(join(root, 'game', 'js', 'assets.js'), 'utf8').includes('checkClip(name, clip, CTX.FIGHT)'), 'assets.js embedded clips are gated');

console.warn = console_warn;
console.log(`anim-gate: ${pass} pass, ${fail} fail; fighters=${roster.length}, fight plays=${totalPlays}, show clips played in FIGHT=${showPlayed}`);
if (fail) process.exit(1);
