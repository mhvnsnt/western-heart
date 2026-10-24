/* SIMULATE / WATCH (clean-room, 2026-10-23). Watch = existing ?demo=1 AI-vs-AI
   fight (game.js). Simulate = instant abstract result from two CPU personalities,
   for tournaments/booking without rendering. Deterministic with a seed. */
import { resolvePersonality, pickOption } from './ai/cpu-personality.js';
const DMG = { poke: 4, heavy: 9, launcher: 14, grab: 11, taunt: 0, block: 0, sidestep: 0, backdash: 0 };
const HIT = { poke: .7, heavy: .5, launcher: .4, grab: .55 };
export function seeded(seed = 1) { let s = seed >>> 0 || 1; return () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296); }
export function simulateMatch(idA, idB, { seed = 1, rounds = 3, base = {} } = {}) {
  const rng = seeded(seed); const P = [resolvePersonality(idA, base[idA]), resolvePersonality(idB, base[idB])];
  const wins = [0, 0]; const log = [];
  for (let r = 0; r < rounds && Math.max(...wins) < Math.ceil(rounds / 2); r++) {
    const hp = [100, 100]; let t = 0;
    while (hp[0] > 0 && hp[1] > 0 && t < 600) {
      const a = t % 2, d = 1 - a; t++;
      if (rng() > P[a].aggression + .2) continue;
      const { option } = pickOption(P[a], { dist: 1 + rng() * 3, foeDamage: 1 - hp[d] / 100, foeDowned: rng() < .08 }, rng);
      const defend = rng() < P[d].reaction * .35;
      if (HIT[option] && !defend && rng() < HIT[option]) hp[d] -= DMG[option];
    }
    const w = hp[0] === hp[1] ? (rng() < .5 ? 0 : 1) : hp[0] > hp[1] ? 0 : 1;
    wins[w]++; log.push({ round: r + 1, winner: w ? idB : idA, hp: hp.map(h => Math.max(0, h)) });
  }
  return { winner: wins[0] > wins[1] ? idA : idB, wins, log };
}
export function watchUrl(idA, idB) { return `?demo=1&p1=${encodeURIComponent(idA)}&p2=${encodeURIComponent(idB)}`; }
