/* CPU PERSONALITY LAYER (clean-room, 2026-10-23)
   Design study: a wrestling sim's CPU logic sheets (situation x foe-damage tier
   -> weighted option list). Reimplemented from the design idea only; no source
   code was copied. Feeds AIController's existing personality knobs
   (aggression / grabBias / reaction) and adds per-situation option weights.
   Data: public default archetypes below; a private derived table can override
   via globalThis.__WH_PRIVATE_ASSETS && globalThis.__WH_CPU_LOGIC. */
export const SITUATIONS = ['far', 'mid', 'close', 'foeDown', 'foeStunned', 'cornered', 'foeCornered'];
export const OPTIONS = ['poke', 'heavy', 'launcher', 'grab', 'block', 'sidestep', 'backdash', 'taunt'];
export const TIERS = ['low', 'mid', 'high']; // foe damage taken: <33%, <66%, >=66%

const w = (o) => Object.fromEntries(OPTIONS.map(k => [k, o[k] || 0]));
export const ARCHETYPES = {
  brawler:   { aggression: .8, grabBias: .15, reaction: .5, table: { close: w({ heavy: 4, poke: 3, launcher: 2, grab: 1 }), far: w({ backdash: 0, poke: 1, sidestep: 1 }), foeDown: w({ heavy: 3, taunt: 1 }) } },
  grappler:  { aggression: .6, grabBias: .45, reaction: .55, table: { close: w({ grab: 5, poke: 2, heavy: 1 }), foeStunned: w({ grab: 6, launcher: 1 }), foeCornered: w({ grab: 4, heavy: 2 }) } },
  turtle:    { aggression: .35, grabBias: .1, reaction: .8, table: { close: w({ block: 4, poke: 3, sidestep: 2 }), mid: w({ block: 2, backdash: 2, poke: 1 }), cornered: w({ sidestep: 4, poke: 2 }) } },
  showboat:  { aggression: .55, grabBias: .2, reaction: .5, table: { foeDown: w({ taunt: 4, heavy: 1 }), close: w({ launcher: 3, heavy: 2, poke: 2 }) } },
  technician:{ aggression: .6, grabBias: .2, reaction: .75, table: { close: w({ poke: 4, launcher: 3, sidestep: 2 }), foeStunned: w({ launcher: 5, heavy: 2 }) } },
};
const DEFAULT_ROW = w({ poke: 3, heavy: 2, launcher: 1, grab: 1, block: 2, sidestep: 1, backdash: 1 });

export function situationOf(s) {
  if (s.foeDowned) return 'foeDown';
  if ((s.foeStun || 0) > 0.2) return 'foeStunned';
  if (s.myWall != null && s.myWall < 1.2) return 'cornered';
  if (s.foeWall != null && s.foeWall < 1.2) return 'foeCornered';
  return s.dist > 3 ? 'far' : s.dist > 1.4 ? 'mid' : 'close';
}
export function tierOf(foeDamage01) { return foeDamage01 >= .66 ? 'high' : foeDamage01 >= .33 ? 'mid' : 'low'; }

export function resolvePersonality(fighterId, base = {}) {
  const priv = globalThis.__WH_PRIVATE_ASSETS && globalThis.__WH_CPU_LOGIC;
  const arch = (priv && priv.fighters && priv.fighters[fighterId]) || base.archetype || 'brawler';
  const a = typeof arch === 'string' ? (ARCHETYPES[arch] || ARCHETYPES.brawler) : arch;
  return { ...base, aggression: base.aggression ?? a.aggression, grabBias: base.grabBias ?? a.grabBias,
    reaction: base.reaction ?? a.reaction, table: { ...(a.table || {}) }, archetype: typeof arch === 'string' ? arch : 'custom' };
}

/* Weighted pick; high foe-damage tier pushes toward finishing options. rng injectable for tests. */
export function pickOption(p, snap, rng = Math.random) {
  const sit = situationOf(snap); const tier = tierOf(snap.foeDamage || 0);
  const row = { ...(p.table && p.table[sit] || DEFAULT_ROW) };
  if (tier === 'high') { row.launcher = (row.launcher || 0) + 2; row.heavy = (row.heavy || 0) + 1; }
  if (tier === 'low') row.poke = (row.poke || 0) + 1;
  const tot = OPTIONS.reduce((t, k) => t + (row[k] || 0), 0) || 1;
  let r = rng() * tot;
  for (const k of OPTIONS) { r -= row[k] || 0; if (r < 0) return { option: k, situation: sit, tier }; }
  return { option: 'poke', situation: sit, tier };
}

/* Roster style -> CPU archetype (roster-full.js `archetype`). */
export const STYLE_TO_ARCHETYPE = { Balanced: 'technician', Shoto: 'technician', Counter: 'turtle', Defensive: 'turtle', Evasive: 'turtle', Zoner: 'turtle',
  Power: 'brawler', Rushdown: 'brawler', Pressure: 'brawler', Boss: 'brawler', Intimidation: 'brawler', Grappler: 'grappler', 'Zoner/Grappler': 'grappler',
  Trickster: 'showboat', Tricky: 'showboat', Showman: 'showboat', Stylish: 'showboat', Ninja: 'technician' };
export function personalityForChar(ch) { const ai = (ch && ch.ai) || {}; return resolvePersonality(ch && ch.id, { archetype: STYLE_TO_ARCHETYPE[ch && ch.archetype] || 'brawler', ...ai }); }
