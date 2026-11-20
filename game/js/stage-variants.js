/* ============================================================
   WESTERN HEART — Stage Variants (weather / time-of-day)
   Teardown source: Tekken 7 / TTT2 / SC6 stage variants — the same arena
   re-lit and re-dressed (rain, dusk, night) as a separate select entry.
   Faithful port of the structure:
     • variants are DATA layered over a base stage: lighting overrides
       (sky/fog/hemi/sun/rim/fill, same schema as stages.js), optional
       weather particles, optional floor tint shift;
     • applyVariant(stageDef, variantId) returns a NEW def (base untouched);
     • variant select entries appear as "STAGE — VARIANT" in the select.
   WH canon mapping (PROPOSED — needs owner approval): variants are tied
   to each land's ELEMENTAL identity (canon: the five lands each hold one
   of the five elemental forces). Variant list per land:
     • TREE OF LIFE (Wood)   — Dawn Mist / Golden Hour / Night Bloom
     • PLAINS OF CHI-U (Fire)— Burning Noon / Ash Dusk / Ember Night
     • OCTAGONAL SHRINE (Earth) — Stone Dawn / Starfall Night (default dusk)
     • HELIX PALACE (Metal)  — Mirror Noon / Neon Night / Chrome Dawn
     • PALACE OF DREAMING (Water) — Rain / Storm / Moonlit Tide
     • PHANTOM MARKETPLACE   — Lamplight / Eyeball Eclipse
     • SHRINE OF THE BLADE   — Dusk (default) / Lantern Night
   Weather particles: rain (dreaming), embers (chi-u), petals (tree),
   snow/ash (shrine), motes (marketplace) — one THREE.Points system.
   ============================================================ */

/* Lighting override schema matches stages.js stage.lighting. */
export const STAGE_VARIANTS = {
  'tree-of-life': [
    { id: 'dawn-mist', name: 'DAWN MIST', weather: 'mist',
      lighting: { sky: [[0,'#0e2233'],[0.5,'#3a5a6a'],[0.8,'#e8b070'],[1,'#6a4a30']], fog: ['#4a4038', 14, 55], sun: ['#ffca7a', 1.8, [-10, 5, 6]] } },
    { id: 'golden-hour', name: 'GOLDEN HOUR', weather: 'petals',
      lighting: { sky: [[0,'#1a1430'],[0.5,'#7a3a40'],[0.8,'#ff9a4c'],[1,'#3a2030']], fog: ['#3a2430', 20, 65], sun: ['#ff9a4c', 2.8, [-12, 4, 5]] } },
    { id: 'night-bloom', name: 'NIGHT BLOOM', weather: 'fireflies',
      lighting: { sky: [[0,'#020610'],[0.6,'#0a1a30'],[0.85,'#1a3a5a'],[1,'#050a18']], fog: ['#0a1420', 18, 60], hemi: ['#3a5a8a', '#0a1018', 1.2], sun: ['#7ab0e0', 0.7, [-6, 8, 4]] } },
  ],
  'plains-of-chi-u': [
    { id: 'burning-noon', name: 'BURNING NOON', weather: 'embers',
      lighting: { sky: [[0,'#2a0a08'],[0.5,'#8a2410'],[0.8,'#ff6a28'],[1,'#3a0f08']], fog: ['#3a1208', 16, 55], sun: ['#ff7a30', 3.2, [0, 12, 2]] } },
    { id: 'ash-dusk', name: 'ASH DUSK', weather: 'ash',
      lighting: { sky: [[0,'#140a10'],[0.5,'#4a2030'],[0.8,'#a04a3c'],[1,'#1a0f14']], fog: ['#2a1a1e', 14, 50], sun: ['#c06a4c', 1.6, [-11, 4, 5]] } },
    { id: 'ember-night', name: 'EMBER NIGHT', weather: 'embers',
      lighting: { sky: [[0,'#0a0408'],[0.6,'#2a0f18'],[0.85,'#6a2030'],[1,'#0f060c']], fog: ['#1a0d12', 16, 55], hemi: ['#8a4a5a', '#140a10', 1.1], sun: ['#ff5a3c', 1.1, [-6, 6, 4]] } },
  ],
  'octagonal-shrine': [
    { id: 'stone-dawn', name: 'STONE DAWN', weather: 'motes',
      lighting: { sky: [[0,'#101a2e'],[0.5,'#3a5a7a'],[0.8,'#d8a060'],[1,'#4a3a2e']], fog: ['#2e2a26', 22, 70], sun: ['#ffca7a', 2.2, [-10, 7, 6]] } },
    { id: 'starfall-night', name: 'STARFALL NIGHT', weather: 'starfall',
      lighting: { sky: [[0,'#01020a'],[0.6,'#0a1030'],[0.85,'#1e2a5e'],[1,'#04060f']], fog: ['#080a18', 20, 65], hemi: ['#4a5aaa', '#0a0c1a', 1.3], sun: ['#8aa0e0', 0.6, [-6, 8, 4]] } },
  ],
  'helix-palace': [
    { id: 'mirror-noon', name: 'MIRROR NOON', weather: 'motes',
      lighting: { sky: [[0,'#1a2030'],[0.5,'#4a6a8a'],[0.8,'#c0d8e8'],[1,'#3a4a5a']], fog: ['#3a4450', 22, 70], sun: ['#e8f0ff', 2.6, [0, 12, 2]] } },
    { id: 'neon-night', name: 'NEON NIGHT', weather: 'sparks',
      lighting: { sky: [[0,'#0a0518'],[0.5,'#2a1050'],[0.8,'#7a2a9a'],[1,'#120a24']], fog: ['#180f2a', 18, 60], hemi: ['#7a4ac0', '#0e0818', 1.4], sun: ['#c07aff', 1.4, [-6, 8, 4]] } },
    { id: 'chrome-dawn', name: 'CHROME DAWN', weather: 'motes',
      lighting: { sky: [[0,'#141a26'],[0.5,'#4a5a70'],[0.8,'#e89a6a'],[1,'#3a2e28']], fog: ['#38302c', 20, 65], sun: ['#ffb070', 2.2, [-10, 6, 6]] } },
  ],
  'palace-of-dreaming': [
    { id: 'rain', name: 'RAIN', weather: 'rain',
      lighting: { sky: [[0,'#0a1420'],[0.5,'#24384e'],[0.8,'#5a7a94'],[1,'#1a2634']], fog: ['#232f3d', 16, 55], sun: ['#9ab8cc', 1.2, [-8, 8, 6]] } },
    { id: 'storm', name: 'STORM', weather: 'storm',
      lighting: { sky: [[0,'#060a12'],[0.5,'#16202f'],[0.8,'#3a4e63'],[1,'#0d141d']], fog: ['#141c26', 12, 48], hemi: ['#4a5f7a', '#0a0e14', 1.0], sun: ['#7a90ac', 0.8, [-8, 8, 6]] } },
    { id: 'moonlit-tide', name: 'MOONLIT TIDE', weather: 'rain',
      lighting: { sky: [[0,'#040818'],[0.6,'#0e1c3a'],[0.85,'#2a4a7e'],[1,'#080f22']], fog: ['#0e1626', 18, 60], hemi: ['#4a6aaa', '#080c18', 1.2], sun: ['#a0c0e8', 0.9, [-6, 9, 4]] } },
  ],
  'phantom-marketplace': [
    { id: 'lamplight', name: 'LAMPLIGHT', weather: 'motes',
      lighting: { sky: [[0,'#120a20'],[0.5,'#3a2048'],[0.8,'#8a4a5a'],[1,'#1e1226']], fog: ['#241a2e', 18, 60], sun: ['#ff9a5c', 1.8, [-8, 6, 6]] } },
    { id: 'eyeball-eclipse', name: 'EYEBALL ECLIPSE', weather: 'motes',
      lighting: { sky: [[0,'#05030c'],[0.6,'#160a28'],[0.85,'#3a1650'],[1,'#0a0614']], fog: ['#100a1c', 16, 55], hemi: ['#5a2a8a', '#0a0612', 1.1], sun: ['#a05ae0', 0.9, [0, 10, 0]] } },
  ],
  'shrine': [
    { id: 'lantern-night', name: 'LANTERN NIGHT', weather: 'motes',
      lighting: { sky: [[0,'#080614'],[0.5,'#1e1438'],[0.8,'#4a2a5a'],[1,'#100a1c']], fog: ['#141020', 20, 65], hemi: ['#5a4a9a', '#100c1e', 1.5], sun: ['#ff9a5c', 1.6, [-11, 6.5, 5]] } },
  ],
};

export function variantsFor(stageId) { return STAGE_VARIANTS[stageId] || []; }
export function getVariant(stageId, variantId) {
  return variantsFor(stageId).find(v => v.id === variantId) || null;
}

/* Deep-merge a variant's lighting over the base def. Returns a NEW def. */
export function applyVariant(stageDef, variantId) {
  const v = getVariant(stageDef.id, variantId);
  if (!v) return stageDef;
  const def = JSON.parse(JSON.stringify(stageDef));
  def.variantId = v.id;
  def.name = `${stageDef.name} — ${v.name}`;
  def.weather = v.weather;
  if (v.lighting && def.lighting) {
    for (const k of Object.keys(v.lighting)) def.lighting[k] = v.lighting[k];
  }
  return def;
}

/* Select entries: base stage + each variant as its own pick. */
export function stageSelectEntries(stageDef) {
  const entries = [{ stageId: stageDef.id, variantId: null, label: stageDef.name }];
  for (const v of variantsFor(stageDef.id))
    entries.push({ stageId: stageDef.id, variantId: v.id, label: `${stageDef.name} — ${v.name}` });
  return entries;
}

/* ---------- weather particles (one THREE.Points, configured per weather) ---------- */
export const WEATHER_CFG = {
  rain:      { count: 900, color: 0x9ab8cc, size: 0.06, speed: 14, area: 18, streak: true },
  storm:     { count: 1400, color: 0x7a90ac, size: 0.07, speed: 20, area: 18, streak: true },
  embers:    { count: 350, color: 0xff7a30, size: 0.09, speed: 1.6, area: 16, rise: true },
  ash:       { count: 500, color: 0x8a8078, size: 0.07, speed: 1.1, area: 16, drift: true },
  petals:    { count: 300, color: 0xffb0c8, size: 0.08, speed: 0.9, area: 16, drift: true },
  mist:      { count: 120, color: 0xb8c8d0, size: 0.5, speed: 0.25, area: 20, drift: true },
  motes:     { count: 200, color: 0xffe0a0, size: 0.05, speed: 0.4, area: 16, drift: true },
  fireflies: { count: 160, color: 0xa0ff80, size: 0.06, speed: 0.7, area: 14, drift: true },
  sparks:    { count: 260, color: 0xc07aff, size: 0.06, speed: 2.2, area: 16, rise: true },
  starfall:  { count: 400, color: 0xcfe0ff, size: 0.05, speed: 6, area: 22, streak: true },
};
/* makeWeatherPoints(THREE, kind) builds the Points; updateWeatherPoints(points, kind, dt, t)
   advances it. Kept DOM/THREE-agnostic: caller passes THREE. */
export function makeWeatherPoints(THREE, kind) {
  const cfg = WEATHER_CFG[kind] || WEATHER_CFG.motes;
  const geo = new THREE.BufferGeometry();
  const p = new Float32Array(cfg.count * 3);
  for (let i = 0; i < cfg.count; i++) {
    p[i*3] = (Math.random() - 0.5) * cfg.area;
    p[i*3+1] = Math.random() * 10;
    p[i*3+2] = (Math.random() - 0.5) * cfg.area;
  }
  geo.setAttribute('position', new THREE.BufferAttribute(p, 3));
  const mat = new THREE.PointsMaterial({ color: cfg.color, size: cfg.size, transparent: true, opacity: 0.75, depthWrite: false });
  const pts = new THREE.Points(geo, mat);
  pts.userData.whWeather = kind;
  return pts;
}
export function updateWeatherPoints(points, dt, t) {
  const kind = points.userData.whWeather;
  const cfg = WEATHER_CFG[kind] || WEATHER_CFG.motes;
  const attr = points.geometry.getAttribute('position');
  const n = attr.count;
  for (let i = 0; i < n; i++) {
    let y = attr.getY(i) - cfg.speed * dt * (cfg.rise ? -0.6 : 1);
    let x = attr.getX(i) + (cfg.drift ? Math.sin(t * 0.7 + i) * dt * 0.8 : 0);
    if (y < 0) y = 10; if (y > 10) y = 0;
    if (Math.abs(x) > cfg.area / 2) x = -Math.sign(x) * cfg.area / 2;
    attr.setY(i, y); attr.setX(i, x);
  }
  attr.needsUpdate = true;
}
