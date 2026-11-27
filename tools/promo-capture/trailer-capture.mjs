// PRIVATE trailer capture: Pantera vs Zen, HUD-off, scripted camera, deterministic 30 fps frames.
// node trailer-capture.mjs <outDir> [startShot] — frames: <outDir>/<shot>/f0000.jpg ...
import { launch, startFight, frame, key, ensureDir } from './lib.mjs';
import fs from 'node:fs';
const OUT = ensureDir(process.argv[2] || '/workspace/focus-nov27/trailer-wh/frames');
const W = +(process.env.W || 1280), H = +(process.env.H || 720);
const lerp = (a, b, t) => a + (b - a) * t;
// Input script entries: [frameIndex, 'down'|'up', code]
const tap = (f, codes, len = 2) => [...codes.map(c => [f, 'down', c]), ...codes.map(c => [f + len, 'up', c])];
const SHOTS = [
  // Entrance: Pantera alone in frame, low orbit (Zen kept out of frame by focus + tight distance).
  { id: 'S1_hero_orbit', frames: 120, passive: true, cam: t => ({ focus: 'p1', dist: lerp(2.0, 1.7, t), yaw: lerp(-1.1, -0.35, t), height: lerp(0.7, 1.0, t), lookY: 1.25, fov: 40 }), input: [] },
  { id: 'S2_walk_in', frames: 180, passive: true, cam: t => ({ focus: 'p1', dist: lerp(2.6, 2.2, t), yaw: lerp(0.9, 0.6, t), height: 1.1, lookY: 1.1, fov: 40 }),
    input: [[0, 'down', 'KeyD'], [150, 'up', 'KeyD']] },
  // Exchanges vs Zen (cut every 2 s on the 120 bpm bar line).
  { id: 'S3_one_two', frames: 60, reset: true, passive: true, cam: t => ({ dist: 3.1, yaw: lerp(0.3, 0.45, t), height: 1.2, fov: 42 }), input: [...tap(8, ['Digit1']), ...tap(18, ['Digit2'])] },
  { id: 'S4_fwd2', frames: 60, reset: true, passive: true, cam: t => ({ dist: 3.0, yaw: lerp(-0.55, -0.4, t), height: 1.05, fov: 42 }), input: [[4, 'down', 'KeyD'], ...tap(6, ['Digit2']), [8, 'up', 'KeyD']] },
  { id: 'S5_zen_attacks', frames: 60, reset: true, passive: false, cam: t => ({ dist: 3.3, yaw: lerp(0.15, 0.3, t), height: 1.3, fov: 42 }), input: [] },
  { id: 'S6_fwd3_kick', frames: 60, reset: true, passive: true, cam: t => ({ dist: 2.9, yaw: lerp(-1.0, -0.9, t), height: 0.75, lookY: 0.9, fov: 42 }), input: [[4, 'down', 'KeyD'], ...tap(6, ['Digit3']), [8, 'up', 'KeyD']] },
  { id: 'S7_left_kick', frames: 60, reset: true, passive: true, cam: t => ({ dist: 3.1, yaw: lerp(0.75, 0.65, t), height: 1.1, fov: 42 }), input: [...tap(6, ['Digit3'])] },
  { id: 'S8_exchange_ai', frames: 120, reset: true, passive: false, cam: t => ({ dist: 3.4, yaw: lerp(0.5, -0.2, t), height: 1.25, fov: 42 }), input: [...tap(10, ['Digit1']), ...tap(20, ['Digit2']), ...tap(60, ['Digit4'])] },
  // Big hit, half-speed (slow-mo = 1/60 s of game time per output frame).
  { id: 'S9_big_kick_slowmo', frames: 120, reset: true, passive: true, dt: 1000 / 60, cam: t => ({ dist: lerp(2.8, 2.4, t), yaw: lerp(0.7, 0.4, t), height: 0.9, lookY: 1.1, fov: 38 }), input: [...tap(10, ['Digit4'], 3)] },
  { id: 'S10_hero_hold', frames: 60, passive: true, cam: t => ({ focus: 'p1', dist: lerp(2.0, 1.8, t), yaw: -0.45, height: 1.0, lookY: 1.3, fov: 38 }), input: [] },
];
const startAt = process.argv[3] || null;
const { browser, page, errors } = await launch({ width: W, height: H });
await startFight(page, 'pantera', 'zen');
// Promo look (capture-only, nothing saved): softer bloom so bright/emissive fighters (Zen) don't clip to white.
const BLOOM = process.env.BLOOM ? process.env.BLOOM.split(',').map(Number) : null;
if (BLOOM) await page.evaluate(([s, th]) => { const b = window.__game.arena.bloom; if (b) { b.strength = s; b.threshold = th; } }, BLOOM);
const log = [];
let go = !startAt;
for (const s of SHOTS) {
  if (!go && s.id === startAt) go = true; if (!go) continue;
  const dir = ensureDir(`${OUT}/${s.id}`);
  await page.evaluate(([reset, passive]) => { const g = window.__game;
    if (reset) { g.p1.root.position.x = -0.8; g.p2.root.position.x = 0.8; g.p1.vx = g.p2.vx = 0; }
    g.p1.hp = g.p1.maxHp; g.p2.hp = g.p2.maxHp; g.timer = 99;
    for (const ai of [g.ai]) if (ai) { ai.passive = !!passive; ai.aggression = passive ? 0 : 0.8; } }, [!!s.reset, s.passive]);
  if (s.reset) for (let i = 0; i < 12; i++) await frame(page, s.cam(0));
  const evs = [...s.input].sort((a, b) => a[0] - b[0]);
  const hp0 = await page.evaluate(() => window.__game.p2.hp);
  for (let i = 0; i < s.frames; i++) {
    for (const [f, d, c] of evs) if (f === i) await key(page, c, d === 'down');
    const r = await frame(page, s.cam(i / Math.max(1, s.frames - 1)), s.dt || 1000 / 30);
    await page.screenshot({ path: `${dir}/f${String(i).padStart(4, '0')}.jpg`, type: 'jpeg', quality: 92 });
    if (i % 15 === 0) log.push({ shot: s.id, i, ...r });
  }
  const hp1 = await page.evaluate(() => window.__game.p2.hp);
  console.log(s.id, 'done', 'p2 dmg', +(hp0 - hp1).toFixed(1));
  fs.writeFileSync(`${OUT}/capture-log.json`, JSON.stringify({ shots: SHOTS.map(s => ({ id: s.id, frames: s.frames })), log, errors }, null, 1));
}
await browser.close();
