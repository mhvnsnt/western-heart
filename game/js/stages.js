/* ============================================================
   WESTERN HEART — Stage system (Lane E: ARENAS)
   • Registry of every playable stage: 8 canon Eastern Mind lands
     (per CANON.md: Tong-Nou, the Five Lands, Phantom Marketplace,
     plus the Shrine of the Blade) + 15 Tekken 3 retro arenas built
     from REAL teardown geometry (teardown/tekken3/stages/<letter>/).
   • Every stage: collision bounds (wallDistance), spawn points,
     lighting rig, floor, backdrop. Builders return an update hook
     for animated elements (flicker, drift, ripple).
   • Tekken 3 panoramas are TEXTURED: per-stage atlases
     (game/assets/stages/t3/stg_<letter>_atlas.png) decoded from the
     real stage texture ARCs (BNS 36-50) by the texture-atlas pipeline
     (docs/arenas/t3-texture-pipeline/). TMD per-packet RGB rides as
     vertex colors. If an atlas fails to load, the builder falls back
     to the palette tint (panoTint) so the stage still renders.
   ============================================================ */
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
// Unified lighting rig (worker 27): stage light rigs, character key/fill/rim
// separation, soul glow, grade hooks. See game/js/lighting-rig.js for the
// T7/SFV/DOA6/T8 teardown audit.
import { buildStageLightRig } from './lighting-rig.js';

/* ---------------- minimal OBJ loader ----------------
   Tekken 3 panoramas use v / vt / f (triangles, 1-indexed, faces as
   v/vt). Textured panoramas additionally carry TMD vertex colors on
   the v lines (v x y z r g b) — parsed when present, ignored by old
   tint-only shells. No materials, no groups — a tiny parser beats
   vendoring all of OBJLoader for this. */
export function parseStageOBJ(text) {
  const pos = [], uv = [], col = [], outP = [], outU = [], outC = [];
  let hasColor = false;
  for (const line of text.split('\n')) {
    const c = line.charAt(0);
    if (c === 'v' && line.charAt(1) === ' ') {
      const p = line.split(/\s+/); pos.push(+p[1], +p[2], +p[3]);
      if (p.length >= 7 && p[4] !== '') { // v x y z r g b (TMD vertex colors)
        col.push(+p[4], +p[5], +p[6]); hasColor = true;
      } else {
        col.push(1, 1, 1);
      }
    } else if (c === 'v' && line.charAt(1) === 't') {
      const p = line.split(/\s+/); uv.push(+p[1], +p[2]);
    } else if (c === 'f') {
      const p = line.trim().split(/\s+/);
      for (let i = 1; i < p.length; i++) {
        const [vi, vti] = p[i].split('/').map(Number);
        outP.push(pos[(vi - 1) * 3], pos[(vi - 1) * 3 + 1], pos[(vi - 1) * 3 + 2]);
        outC.push(col[(vi - 1) * 3], col[(vi - 1) * 3 + 1], col[(vi - 1) * 3 + 2]);
        if (vti && uv.length) outU.push(uv[(vti - 1) * 2], uv[(vti - 1) * 2 + 1]);
      }
    }
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(outP, 3));
  if (outU.length === outP.length / 3 * 2)
    g.setAttribute('uv', new THREE.Float32BufferAttribute(outU, 2));
  if (hasColor && outC.length === outP.length)
    g.setAttribute('color', new THREE.Float32BufferAttribute(outC, 3));
  g.computeVertexNormals();
  return g;
}
const _objCache = {};
export async function fetchStageOBJ(path) {
  if (_objCache[path]) return _objCache[path].clone();
  const res = await fetch(path);
  if (!res.ok) throw new Error(`stage OBJ missing: ${path}`);
  const geo = parseStageOBJ(await res.text());
  _objCache[path] = geo;
  return geo.clone();
}

/* ---------------- shared procedural textures ---------------- */
function _canvas(size, draw) {
  const c = document.createElement('canvas');
  c.width = c.height = size;
  draw(c.getContext('2d'), size);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}
export function makeSkyTexture(stops) {
  const t = _canvas(256, (ctx, s) => {
    const g = ctx.createLinearGradient(0, 0, 0, s);
    for (const [at, col] of stops) g.addColorStop(at, col);
    ctx.fillStyle = g; ctx.fillRect(0, 0, s, s);
  });
  t.wrapS = t.wrapT = THREE.ClampToEdgeWrapping;
  return t;
}
// Generic mottled floor. kind: 'stone' | 'sand' | 'scorched' | 'metal' | 'dream' | 'dark'
export function makeFloorTexture(kind, tint, repeat) {
  const base = {
    stone: '#3a3440', sand: '#8a6f4d', scorched: '#2a1410',
    metal: '#3c4048', dream: '#2c2a55', dark: '#141418',
  }[kind] || '#3a3440';
  const t = _canvas(512, (ctx, s) => {
    ctx.fillStyle = base; ctx.fillRect(0, 0, s, s);
    const n = kind === 'metal' ? 2500 : 9000;
    for (let i = 0; i < n; i++) {
      const v = 20 + Math.random() * 60;
      ctx.fillStyle = `rgba(${v},${v * 0.96},${v * 0.92},${Math.random() * 0.4})`;
      const sz = kind === 'scorched' ? 1 + Math.random() * 5 : 2;
      ctx.fillRect(Math.random() * s, Math.random() * s, sz, sz);
    }
    if (kind === 'stone' || kind === 'metal') { // tile seams
      ctx.strokeStyle = 'rgba(8,6,10,0.9)'; ctx.lineWidth = 4;
      const step = kind === 'metal' ? 128 : 128;
      for (let x = 0; x <= s; x += step) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, s); ctx.stroke(); }
      for (let y = 0; y <= s; y += step) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(s, y); ctx.stroke(); }
    }
    if (kind === 'scorched') { // ember cracks
      ctx.strokeStyle = 'rgba(255,90,30,0.55)'; ctx.lineWidth = 2;
      for (let i = 0; i < 26; i++) {
        ctx.beginPath();
        let x = Math.random() * s, y = Math.random() * s;
        ctx.moveTo(x, y);
        for (let k = 0; k < 6; k++) { x += (Math.random() - 0.5) * 90; y += (Math.random() - 0.5) * 90; ctx.lineTo(x, y); }
        ctx.stroke();
      }
    }
  });
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.repeat.set(repeat, repeat);
  t.anisotropy = 4;
  const mat = new THREE.MeshStandardMaterial({ map: t, roughness: kind === 'metal' ? 0.35 : 0.9, metalness: kind === 'metal' ? 0.75 : 0.05, color: tint });
  return mat;
}
export function makeWoodTexture() {
  return _canvas(256, (ctx, s) => {
    ctx.fillStyle = '#241610'; ctx.fillRect(0, 0, s, s);
    for (let i = 0; i < 46; i++) {
      const x = Math.random() * s;
      ctx.fillStyle = `rgba(${10 + Math.random() * 24},${6 + Math.random() * 12},4,0.55)`;
      ctx.fillRect(x, 0, 2 + Math.random() * 5, s);
    }
    ctx.fillStyle = 'rgba(0,0,0,0.35)';
    for (let x = 0; x < s; x += 64) ctx.fillRect(x, 0, 2, s);
  });
}
// Eyeball texture for the Phantom Marketplace's Eyeball Mountains.
export function makeEyeTexture() {
  return _canvas(256, (ctx, s) => {
    ctx.fillStyle = '#e8e0d0'; ctx.fillRect(0, 0, s, s);
    const g = ctx.createRadialGradient(s / 2, s / 2, 8, s / 2, s / 2, 90);
    g.addColorStop(0, '#101018'); g.addColorStop(0.35, '#3a1a5a');
    g.addColorStop(0.55, '#7a3ac0'); g.addColorStop(0.75, '#c0c0b8'); g.addColorStop(1, 'rgba(232,224,208,0)');
    ctx.fillStyle = g; ctx.beginPath(); ctx.arc(s / 2, s / 2, 90, 0, 7); ctx.fill();
    ctx.strokeStyle = 'rgba(160,30,30,0.5)'; ctx.lineWidth = 3; // veins
    for (let i = 0; i < 14; i++) {
      const a = Math.random() * Math.PI * 2;
      ctx.beginPath(); ctx.moveTo(s / 2 + Math.cos(a) * 60, s / 2 + Math.sin(a) * 60);
      ctx.lineTo(s / 2 + Math.cos(a) * 120, s / 2 + Math.sin(a) * 120); ctx.stroke();
    }
  });
}
// Veined dark sky for the Octagonal Shrine (inside of Tong-Nou's head).
export function makeVeinSkyTexture() {
  return _canvas(256, (ctx, s) => {
    const g = ctx.createLinearGradient(0, 0, 0, s);
    g.addColorStop(0, '#060608'); g.addColorStop(0.7, '#0d0a14'); g.addColorStop(1, '#1a0f18');
    ctx.fillStyle = g; ctx.fillRect(0, 0, s, s);
    ctx.strokeStyle = 'rgba(150,40,50,0.18)'; ctx.lineWidth = 1;
    for (let i = 0; i < 34; i++) {
      ctx.beginPath();
      let x = Math.random() * s, y = 0; ctx.moveTo(x, y);
      for (let k = 0; k < 8; k++) { x += (Math.random() - 0.5) * 60; y += s / 8; ctx.lineTo(x, y); }
      ctx.stroke();
    }
  });
}

/* ---------------- stage registry ----------------
   dims.wallDistance: fighters clamp at ±wallDistance (Tekken standard
   8.4 for a 16.8-wide arena). spawns: P1/P2 round-start X. */
export const STAGES = [
  {
    id: 'shrine', name: 'SHRINE OF THE BLADE', tier: 'CANON LANDS',
    universe: 'Octagonal Shrine (Central Mountain)', element: 'Earth',
    description: 'Stone temple courtyard at dusk. Paper lanterns cast warm light against cold stone. Phantom home stage.',
    dims: { width: 16.8, depth: 6.0, wallDistance: 8.4 },
    spawns: { p1: -3.5, p2: 3.5 },
    lighting: {
      sky: [[0.0, '#120e33'], [0.45, '#3a2358'], [0.72, '#a34a3c'], [0.88, '#ff7a3c'], [1.0, '#2a1626']],
      fog: ['#1a1428', 20, 65],
      hemi: ['#6a6aaa', '#2a2038', 1.9],
      sun: ['#ff9a5c', 2.6, [-11, 6.5, 5]],
      rim: ['#5a6ab0', 0.65, [8, 6, -7]],
      fill: ['#ffe0c0', 1.0, [0, 4, 10]],
      // Lighting rig (worker 27): Earth land — lantern gold motes (bible:
      // "dust motes in lantern beams"), warm character key, lifted grade.
      rig: {
        charKey: ['#ffe9d2', 20, 7], rimBoost: 1.15,
        motes: { color: '#FFC85C', count: 200, size: 0.06, opacity: 0.55 },
      },
      grade: { exposure: 1.5, bloom: 0.7 },
    },
    floor: { kind: 'stone', tint: '#a89a90', repeat: 30, platformTint: '#b5a498', platformRepeat: 7 },
    swatch: ['#120e33', '#ff7a3c'],
    builder: 'shrine',
    associatedFighters: ['phantom', 'diablo'],
    // Stage-break lane (Tekken floor break): cracked crypt seal at center —
    // a heavy slam shatters it and the fight drops to the crypt below.
    breakables: [{ type: 'floor', x: 0, z: 0, r: 2.6, depth: 6 }],
  },
  {
    id: 'tong-nou', name: 'TONG-NOU', tier: 'CANON LANDS',
    universe: 'The Head Itself', element: 'Void',
    description: 'The Purifier. A giant green head floats in the dark, and the trial happens inside its gaze. Its eyes follow the fighters.',
    dims: { width: 16.8, depth: 6.0, wallDistance: 8.4 },
    spawns: { p1: -3.5, p2: 3.5 },
    lighting: {
      sky: [[0.0, '#020402'], [0.6, '#041004'], [0.85, '#0a2a12'], [1.0, '#031008']],
      fog: ['#030a05', 18, 60],
      hemi: ['#2a5a3a', '#050a06', 1.5],
      sun: ['#7ae08a', 1.4, [-6, 8, 4]],
      rim: ['#3ae060', 1.1, [6, 5, -6]],
      fill: ['#b8e8c0', 0.5, [0, 4, 10]],
      // Lighting rig (worker 27): the Void — sparse soul-lights in darkness
      // (bible: "like plankton in a night ocean"), darker grade, high bloom.
      rig: {
        charKey: ['#c8ffd8', 18, 7], rimBoost: 1.2,
        motes: { color: '#9fd8ff', count: 90, size: 0.05, opacity: 0.5 },
      },
      grade: { exposure: 1.35, bloom: 0.85 },
    },
    floor: { kind: 'dark', tint: '#1a2a1e', repeat: 24, platformTint: '#223a28', platformRepeat: 6 },
    swatch: ['#031008', '#3ae060'],
    builder: 'tongnou',
    associatedFighters: ['diablo'],
  },
  {
    id: 'tree-of-life', name: 'TREE OF LIFE', tier: 'CANON LANDS',
    universe: 'Tree of Life (Ming-ken)', element: 'Wood',
    description: 'Land of Life. A colossal tree holds glowing souls like fruit; the Sha-mo Desert stretches to the horizon. Where souls begin.',
    dims: { width: 16.8, depth: 6.0, wallDistance: 8.4 },
    spawns: { p1: -3.5, p2: 3.5 },
    lighting: {
      sky: [[0.0, '#0a1a2a'], [0.5, '#1a3a4a'], [0.8, '#c08040'], [1.0, '#5a3a20']],
      fog: ['#2a2018', 22, 70],
      hemi: ['#7a9aba', '#4a3a22', 1.7],
      sun: ['#ffca7a', 2.4, [-10, 7, 6]],
      rim: ['#4a7a5a', 0.6, [8, 6, -7]],
      fill: ['#ffe8c0', 0.9, [0, 4, 10]],
      // Lighting rig (worker 27): Wood land — pollen-light motes (bible:
      // "humid luminosity, pollen-light motes"), dawn-warm character key.
      rig: {
        charKey: ['#ffe0b0', 20, 7], rimBoost: 1.1,
        motes: { color: '#FFD76A', count: 260, size: 0.05, opacity: 0.5 },
      },
      grade: { exposure: 1.5, bloom: 0.7 },
    },
    floor: { kind: 'sand', tint: '#c09a68', repeat: 26, platformTint: '#d0aa74', platformRepeat: 6 },
    swatch: ['#0a1a2a', '#ffca7a'],
    builder: 'treelife',
    pano: 'assets/stages/eastern-mind/tree-of-life/pano.png', // real Eastern Mind background art
    associatedFighters: ['saku-ra'],
  },
  {
    id: 'plains-of-chi-u', name: 'PLAINS OF CHI-U', tier: 'CANON LANDS',
    universe: 'Plains of Chi-U (Shi-chieng)', element: 'Fire',
    description: 'Land of Time. Scorched plains under a burning sky. The Fire Tower of Time burns and never collapses. Confrontation lives here.',
    dims: { width: 16.8, depth: 6.0, wallDistance: 8.4 },
    spawns: { p1: -3.5, p2: 3.5 },
    lighting: {
      sky: [[0.0, '#1a0608'], [0.45, '#5a1410'], [0.75, '#c03a18'], [1.0, '#2a0a08']],
      fog: ['#2a0d08', 18, 60],
      hemi: ['#b05a3a', '#2a0f08', 1.7],
      sun: ['#ff6a2a', 2.8, [-11, 5, 5]],
      rim: ['#ff3a1a', 0.7, [8, 6, -7]],
      fill: ['#ffc0a0', 0.9, [0, 4, 10]],
      // Lighting rig (worker 27): Fire land — floating cinders (bible:
      // "heat shimmer, floating cinders"), ember character key, hot grade.
      rig: {
        charKey: ['#ffc0a0', 22, 7], rimBoost: 1.1,
        motes: { color: '#E85D1F', count: 240, size: 0.06, opacity: 0.55 },
      },
      grade: { exposure: 1.55, bloom: 0.75 },
    },
    floor: { kind: 'scorched', tint: '#8a5a48', repeat: 24, platformTint: '#9a6a50', platformRepeat: 6 },
    swatch: ['#1a0608', '#ff6a2a'],
    builder: 'chiu',
    pano: 'assets/stages/eastern-mind/plains-of-chi-u/pano.png', // real Eastern Mind background art
    associatedFighters: ['michiko'],
    // Stage-break lane: scorched weak crust off-center — heavy slams break
    // through to the ember hollow below.
    breakables: [{ type: 'floor', x: 2.5, z: 0.5, r: 2.4, depth: 6 }],
  },
  {
    id: 'octagonal-shrine', name: 'OCTAGONAL SHRINE PAR-FANG', tier: 'CANON LANDS',
    universe: 'Central Mountain - The Source', element: 'Earth',
    description: 'Eight-sided, ancient, still. The sky above is the inside of the head - dark, vast, veined. The trial is inscribed in stone here.',
    dims: { width: 16.8, depth: 6.0, wallDistance: 8.4 },
    spawns: { p1: -3.5, p2: 3.5 },
    lighting: {
      sky: 'veins',
      fog: ['#0a0810', 20, 62],
      hemi: ['#4a4a6a', '#141018', 1.4],
      sun: ['#c0a080', 1.6, [-8, 9, 4]],
      rim: ['#6a5a8a', 0.6, [8, 6, -7]],
      fill: ['#d0c0b0', 0.7, [0, 4, 10]],
      // Lighting rig (worker 27): the Source — stillness; Moonface Pale
      // motes (Malakor thread), restrained grade ("absolute quiet").
      rig: {
        charKey: ['#f4e8d8', 18, 7], rimBoost: 1.0,
        motes: { color: '#C9B8E8', count: 120, size: 0.045, opacity: 0.45 },
      },
      grade: { exposure: 1.4, bloom: 0.7 },
    },
    floor: { kind: 'stone', tint: '#8a8492', repeat: 26, platformTint: '#9a94a2', platformRepeat: 6, octagon: true },
    swatch: ['#0a0810', '#c0a080'],
    builder: 'parfang',
    pano: 'assets/stages/eastern-mind/octagonal-shrine/pano.png', // real Eastern Mind background art
    associatedFighters: ['pantera'],
  },
  {
    id: 'helix-palace', name: 'HELIX PALACE', tier: 'CANON LANDS',
    universe: 'Helix Palace (Yui-wang)', element: 'Metal',
    description: 'Land of Desire. A spiraling palace with five glowing rooms - Greed, Appetite, Immortality, Sexual Desire, Destruction. Everything reflects.',
    dims: { width: 16.8, depth: 6.0, wallDistance: 8.4 },
    spawns: { p1: -3.5, p2: 3.5 },
    lighting: {
      sky: [[0.0, '#0a0a18'], [0.5, '#1a1a3a'], [0.8, '#3a2a5a'], [1.0, '#140a20']],
      fog: ['#141020', 18, 58],
      hemi: ['#6a6ab0', '#1a1428', 1.8],
      sun: ['#c0d0ff', 2.0, [-9, 8, 5]],
      rim: ['#ff6ad0', 0.7, [8, 6, -7]],
      fill: ['#e0d0ff', 0.9, [0, 4, 10]],
      // Lighting rig (worker 27): Metal land — refracted light motes
      // (bible: "refracted light beams, floating dust as prisms"), cool key.
      rig: {
        charKey: ['#e8f0ff', 20, 7], rimBoost: 1.25,
        motes: { color: '#EAF6FF', count: 200, size: 0.05, opacity: 0.5 },
      },
      grade: { exposure: 1.45, bloom: 0.85 },
    },
    floor: { kind: 'metal', tint: '#a0a8b8', repeat: 20, platformTint: '#b0b8c8', platformRepeat: 5 },
    swatch: ['#0a0a18', '#ff6ad0'],
    builder: 'helix',
    pano: 'assets/stages/eastern-mind/helix-palace/pano.png', // real Eastern Mind background art
    // Arena upgrade pipeline, Stage 3 (detail pass): the Pink Narwhal club
    // interior (SmutBase Virt-A-Mate scene; see
    // tools/stage-arena-pull/convert_pinknarwhal.py) replaces the procedural
    // spiral blockout. The club carries its own fighting surface.
    glb: 'assets/stages/pink-narwhal/pink-narwhal.glb',
    hidePlatform: true,
    associatedFighters: ['purple-rain'],
    // Stage-break lane (T7 balcony break): the palace balcony edge — a heavy
    // hit there shatters the railing and drops the fight one level.
    breakables: [{ type: 'balcony', x: 5.5, z: 0, r: 2.2, w: 4.5, depth: 6 }],
  },
  {
    id: 'palace-of-dreaming', name: 'PALACE OF DREAMING', tier: 'CANON LANDS',
    universe: 'Palace of Dreaming (Mon-chien)', element: 'Water',
    description: 'Land of Dreaming. A palace that will not stay still - walls ripple, and the floor reflects a sky that is not there. Change is the only law.',
    dims: { width: 16.8, depth: 6.0, wallDistance: 8.4 },
    spawns: { p1: -3.5, p2: 3.5 },
    lighting: {
      sky: [[0.0, '#0a1030'], [0.45, '#1a2a60'], [0.75, '#3a5ac0'], [0.9, '#7ab0e0'], [1.0, '#0a1030']],
      fog: ['#101838', 20, 64],
      hemi: ['#5a7ac0', '#1a2040', 1.8],
      sun: ['#9ac0ff', 2.0, [-9, 7, 6]],
      rim: ['#4ae0ff', 0.8, [8, 6, -7]],
      fill: ['#c0e0ff', 0.9, [0, 4, 10]],
      // Lighting rig (worker 27): Water land — bioluminescent drift
      // (bible: "bioluminescent drift... underwater while breathing air").
      rig: {
        charKey: ['#c8f0ff', 20, 7], rimBoost: 1.2,
        motes: { color: '#4FD8E8', count: 220, size: 0.055, opacity: 0.5 },
      },
      grade: { exposure: 1.45, bloom: 0.85 },
    },
    floor: { kind: 'dream', tint: '#8a90c8', repeat: 18, platformTint: '#9aa0d8', platformRepeat: 5 },
    swatch: ['#0a1030', '#4ae0ff'],
    builder: 'dreaming',
    pano: 'assets/stages/eastern-mind/palace-of-dreaming/pano.png', // real Eastern Mind background art
    associatedFighters: ['waterfall'],
  },
  {
    id: 'phantom-marketplace', name: 'PHANTOM MARKETPLACE', tier: 'CANON LANDS',
    universe: 'The Liminal Bazaar', element: 'Spirit',
    description: 'A liminal bazaar under the Eyeball Mountains, where the Trader buys and sells elemental forces. An audience of eyeball mountains.',
    dims: { width: 16.8, depth: 6.0, wallDistance: 8.4 },
    spawns: { p1: -3.5, p2: 3.5 },
    lighting: {
      sky: [[0.0, '#0c0a20'], [0.5, '#241a4a'], [0.78, '#6a3a7a'], [1.0, '#180f28']],
      fog: ['#160f28', 20, 62],
      hemi: ['#7a6aba', '#241a38', 1.7],
      sun: ['#ffaa6a', 2.0, [-10, 6, 6]],
      rim: ['#b06ae0', 0.7, [8, 6, -7]],
      fill: ['#ffd0a0', 0.8, [0, 4, 10]],
      // Lighting rig (worker 27): liminal bazaar — Malakor-thread primary
      // zone. Nostalgia Haze motes, Trader-gold character key.
      rig: {
        charKey: ['#ffd76a', 20, 7], rimBoost: 1.2,
        motes: { color: '#8A6FB8', count: 200, size: 0.055, opacity: 0.5 },
      },
      grade: { exposure: 1.5, bloom: 0.8 },
    },
    floor: { kind: 'stone', tint: '#7a6a80', repeat: 26, platformTint: '#8a7a90', platformRepeat: 6 },
    swatch: ['#0c0a20', '#b06ae0'],
    builder: 'marketplace',
    pano: 'assets/stages/eastern-mind/phantom-marketplace/pano.png', // real Eastern Mind background art
    associatedFighters: ['skull'],
  },
];

/* ---------------- Tekken 3 retro stages ----------------
   Real teardown geometry + real teardown textures: panorama shells
   from T3 TMD records (teardown/tekken3/stages/{letter}/) with
   texture atlases decoded from the stage texture ARCs (BNS 36-50)
   by docs/arenas/t3-texture-pipeline/. TMD per-packet RGB rides as
   vertex colors; panoTint remains as the no-texture fallback.
   Home-fighter attribution from each stage.json. */
const T3_RETRO = [
  // letter, name, fighters, palette notes, panoTint, floor kind/tint, sky, fog, sun, hemi
  ['a', 'PAUL / BRYAN', 'Paul, Bryan', '#7a5a3a', 'stone', '#a89a90',
   [[0.0,'#1a1430'],[0.5,'#3a2a50'],[0.8,'#c06a3a'],[1.0,'#2a1626']], '#1a1428', '#ff9a5c', '#5a5a8a'],
  ['b', 'LAW / KUMA / PANDA', 'Law, Kuma, Panda', '#5a3a6a', 'stone', '#8a7a9a',
   [[0.0,'#0a0a24'],[0.5,'#1a1a44'],[0.8,'#c03a8a'],[1.0,'#160a20']], '#120a20', '#ff6aca', '#5a5aba'],
  ['c', 'YOSHIMITSU / MOKUJIN', 'Yoshimitsu, Mokujin', '#3a6a4a', 'stone', '#8a9a8a',
   [[0.0,'#0a1a14'],[0.5,'#1a3a2a'],[0.8,'#7aca9a'],[1.0,'#0c1410']], '#0c1410', '#9ae0ba', '#4a6a5a'],
  ['d', 'XIAOYU', 'Xiaoyu', '#c07a9a', 'stone', '#c0a0b0',
   [[0.0,'#1a2a5a'],[0.5,'#3a5aca'],[0.8,'#ff9aca'],[1.0,'#2a1a3a']], '#1a1430', '#ffb0d0', '#6a7aca'],
  ['e', 'HWOARANG', 'Hwoarang', '#6a6a3a', 'scorched', '#9a8a5a',
   [[0.0,'#1a1008'],[0.5,'#4a2a14'],[0.8,'#e08a3a'],[1.0,'#241208']], '#201408', '#ff9a4a', '#8a6a4a'],
  ['f', 'LEI', 'Lei', '#3a6a5a', 'stone', '#7a9a8a',
   [[0.0,'#0a1420'],[0.5,'#14324a'],[0.8,'#3aca8a'],[1.0,'#0c1820']], '#0c1620', '#6ae0aa', '#4a6a7a'],
  ['g', 'OGRE', 'Ogre, True Ogre', '#6a4a3a', 'stone', '#9a8a7a',
   [[0.0,'#140c08'],[0.5,'#3a2014'],[0.8,'#c05a2a'],[1.0,'#1c100a']], '#181008', '#ff7a3a', '#6a5040'],
  ['i', 'JIN', 'Jin', '#9abaca', 'stone', '#bacae0',
   [[0.0,'#1a2a3a'],[0.5,'#3a5a7a'],[0.8,'#badef0'],[1.0,'#203040']], '#182430', '#c0e0ff', '#6a8aaa'],
  ['j', 'NINA / ANNA / GUN JACK', 'Nina, Anna, Gun Jack', '#4a3a6a', 'stone', '#8a7a9a',
   [[0.0,'#0c0a1c'],[0.5,'#241a44'],[0.8,'#7a5aca'],[1.0,'#120c20']], '#100c20', '#a07aea', '#5a4a8a'],
  ['k', 'EDDY / TIGER', 'Eddy, Tiger', '#c0a05a', 'sand', '#d0b070',
   [[0.0,'#1a3a5a'],[0.5,'#2a7a9a'],[0.8,'#7adaca'],[1.0,'#1a3a3a']], '#142a30', '#ffe08a', '#5a9aba'],
  ['l', 'KING', 'King', '#8a2a2a', 'stone', '#b08a7a',
   [[0.0,'#1c0a0a'],[0.5,'#4a1414'],[0.8,'#e04a2a'],[1.0,'#200c0c']], '#180c0c', '#ff8a4a', '#8a4a4a'],
  ['m', 'JULIA / HEIHACHI', 'Julia, Heihachi', '#2a5a3a', 'stone', '#7a9a7a',
   [[0.0,'#0a140c'],[0.5,'#1a3a20'],[0.8,'#5aca6a'],[1.0,'#0c140c']], '#0c140c', '#8ae09a', '#4a6a4a'],
  ['n', 'XIAOYU / JIN', 'Xiaoyu, Jin (alt)', '#6a3a8a', 'stone', '#9a7aba',
   [[0.0,'#120a24'],[0.5,'#2a1a54'],[0.8,'#9a5ae0'],[1.0,'#160f28']], '#120e24', '#b07aea', '#5a4a9a'],
  ['t', 'GON', 'Gon', '#3a7a3a', 'stone', '#8aaa7a',
   [[0.0,'#0a1a0c'],[0.5,'#1a4a20'],[0.8,'#8ae05a'],[1.0,'#0c1c0c']], '#0c180c', '#aae07a', '#4a7a4a'],
  ['u', 'DOCTOR B.', 'Doctor B.', '#7a9aba', 'metal', '#a0b0c0',
   [[0.0,'#0c1420'],[0.5,'#1a2a44'],[0.8,'#5a9ae0'],[1.0,'#0e1626']], '#0e1624', '#9ac0ff', '#5a6a8a'],
];
for (const [letter, label, fighters, panoTint, floorKind, floorTint, sky, fogC, sunC, hemiC] of T3_RETRO) {
  STAGES.push({
    id: `t3-${letter}`,
    name: `T3 RETRO: ${label}`,
    tier: 'TEKKEN RETRO',
    universe: 'Tekken 3 (legacy)',
    element: 'Retro',
    description: `Real Tekken 3 panorama (${fighters}) — real TMD geometry with the decoded texture atlas.`,
    dims: { width: 16.8, depth: 6.0, wallDistance: 8.4 },
    spawns: { p1: -3.5, p2: 3.5 },
    lighting: {
      sky, fog: [fogC, 18, 60],
      hemi: [hemiC, '#1a1420', 1.6],
      sun: [sunC, 2.2, [-10, 7, 5]],
      rim: [sunC, 0.6, [8, 6, -7]],
      fill: ['#ffe0c0', 0.8, [0, 4, 10]],
    },
    floor: { kind: floorKind, tint: floorTint, repeat: 26, platformTint: floorTint, platformRepeat: 6 },
    swatch: [sky[0][1], sunC],
    builder: 't3retro',
    obj: `assets/stages/t3/stg_${letter}_panorama.obj`,
    map: `assets/stages/t3/stg_${letter}_atlas.png`,
    panoTint,
    homeFighters: fighters,
  });
}


/* ---------------- WWF NO MERCY ARENAS (teardown-integration 2026-10-19) ----
   17 real arena assemblies from teardown/wwf-no-mercy/arenas/ (see ARENAS.md
   there): 11 show/PPV arenas + cage + 6 backstage areas. Geometry is the
   actual AkiModel pieces; vertex colors from the teardown .vc sidecars. */
const NO_MERCY = [
  // file, name, description, skyTop, skyMid, sun, floorTint
  ['arena_raw', 'RAW IS WAR', 'The Monday-night war room — ring, ramp, trons and a full crowd bowl.', '#0a0a18', '#2a0a14', '#ff3a3a', '#6a5a52'],
  ['arena_smackdown', 'SMACKDOWN', 'Blue-brand arena bowl with the fist-era staging bones.', '#0a0a20', '#101a3a', '#3a7aff', '#5a6068'],
  ['arena_royal_rumble', 'ROYAL RUMBLE', 'January classic bowl — every fighter for themselves.', '#120a20', '#241040', '#8a4aff', '#605a68'],
  ['arena_wrestlemania', 'WRESTLEMANIA', 'The grandest stage of them all, No Mercy vintage.', '#0c0c1c', '#1c1440', '#ffd76a', '#6a6058'],
  ['arena_king_of_the_ring', 'KING OF THE RING', 'Tournament-night arena. Win three and take the crown.', '#100c08', '#2a1c0c', '#ffb03a', '#6a5c4a'],
  ['arena_summerslam', 'SUMMERSLAM', 'The biggest party of the summer, year-2000 edition.', '#081018', '#0c2a3a', '#3ad0ff', '#5a6660'],
  ['arena_survivor_series', 'SURVIVOR SERIES', 'Thanksgiving-tradition arena — teams of five strive to survive.', '#140c0c', '#301414', '#ff6a3a', '#66584e'],
  ['arena_backlash', 'BACKLASH', 'Post-WrestleMania fallout bowl.', '#0c0814', '#1c1030', '#b03aff', '#5c565e'],
  ['arena_armageddon', 'ARMAGEDDON', 'End-of-the-world PPV arena, six-man cell energy.', '#100808', '#2c0c0c', '#ff2a2a', '#605450'],
  ['arena_no_mercy', 'NO MERCY', 'The namesake show — barricades, bowl and bad intentions.', '#0a0c14', '#14202c', '#7ab0ff', '#5e6058'],
  ['arena_cage', 'STEEL CAGE', 'Cage-match ring — the walls are part of the fight.', '#0a0a0c', '#18181c', '#c0c8d0', '#565a60'],
  ['backstage_bar_lounge', 'BACKSTAGE: BAR LOUNGE', 'Where the brawls spill after last call.', '#120c08', '#241408', '#ff9a4a', '#5c4a3a'],
  ['backstage_boiler_room', 'BACKSTAGE: BOILER ROOM', 'Steam, pipes and Mankind energy.', '#0c0a08', '#1c140c', '#ff7a2a', '#54483e'],
  ['backstage_hallway', 'BACKSTAGE: HALLWAY', 'Gorilla-adjacent corridor — anything can happen here.', '#0c0c10', '#181820', '#aab4c0', '#585c60'],
  ['backstage_locker_room', 'BACKSTAGE: LOCKER ROOM', 'Benches, lockers and grudges.', '#0a0e0c', '#14201a', '#6aff9a', '#4e5c50'],
  ['backstage_parking_lot', 'BACKSTAGE: PARKING LOT', 'Asphalt rules. Cars are furniture.', '#080a10', '#101820', '#8ab4d8', '#4c5054'],
  ['lobby', 'THE LOBBY', 'Gorilla position — one corridor from the curtain.', '#0e0c0a', '#201a12', '#ffd9a0', '#5e584c'],
];
for (const [file, name, desc, skyTop, skyMid, sunC, floorTint] of NO_MERCY) {
  STAGES.push({
    id: `nm-${file.replace(/_/g, '-')}`,
    name: `NO MERCY: ${name}`,
    tier: 'WRESTLING',
    universe: 'WWF No Mercy (AKI)',
    element: 'Ring',
    description: desc,
    dims: { width: 16.8, depth: 6.0, wallDistance: 8.4 },
    spawns: { p1: -3.5, p2: 3.5 },
    lighting: {
      sky: [[0.0, skyTop], [0.55, skyMid], [0.85, sunC], [1.0, skyTop]],
      fog: [skyTop, 22, 80],
      hemi: ['#8a8aa8', '#1a1420', 1.5],
      sun: [sunC, 2.2, [-10, 8, 5]],
      rim: [sunC, 0.6, [8, 6, -7]],
      fill: ['#ffe0c0', 0.8, [0, 4, 10]],
    },
    floor: { kind: 'stone', tint: floorTint, repeat: 26, platformTint: floorTint, platformRepeat: 6 },
    swatch: [skyTop, sunC],
    builder: 'nomercy',
    obj: `assets/stages/no-mercy/${file}.obj`,
    panoTint: '#ffffff',
  });
}

/* ---- SUN RĀ — THE STARING SKY (boss stage; Kevin's home base) ---- */
STAGES.push({
  id: 'sunra',
  name: 'SUN RĀ — THE STARING SKY',
  tier: 'BOSS STAGES',
  universe: "God Molecule fever-dream (Sun Rā's arena)",
  element: 'Curse',
  description: "Mars floats in the sky — cobalt head, bleeding eyes that never blink — with Mercury→Neptune+Pluto on inclined orbits around him. Fever-dream floor zoned by the four lands; Central Mountain is Kevin's home turf. Malakor-occult sigils ring the arena.",
  dims: { width: 16.8, depth: 6.0, wallDistance: 8.4 },
  spawns: { p1: -3.5, p2: 3.5 },
  lighting: {
    sky: [[0.0, '#020208'], [0.5, '#0a0a24'], [0.78, '#1a1040'], [0.9, '#4a1030'], [1.0, '#0a0512']],
    fog: ['#0a0818', 25, 95],
    hemi: ['#3a3a8a', '#0a0512', 1.6],
    sun: ['#ff4a3a', 2.0, [-10, 8, 6]],
    rim: ['#4a6aff', 0.8, [8, 7, -8]],
    fill: ['#8a7aff', 0.7, [0, 5, 12]],
  },
  floor: { kind: 'dark', tint: '#8a8aa8', repeat: 40, platformTint: '#6a6a8a', platformRepeat: 8 },
  swatch: ['#050510', '#ff3a2a'],
  builder: 'sunra',
  homeFighters: 'Sun Rā, Kevin',
  associatedFighters: ['sun-ra', 'baek'],
  // God Molecule canon: per-land musical palettes + continuous music across
  // reality transitions ("the cut carries the story"). Consumed by audio.js
  // when the per-land palette wiring lands (follow-up).
  music: { land: 'dreaming', palette: 'fluid ambient textures', continuous: true },
});

/* ---------------- WWF NO MERCY arenas ----------------
   Real N64 arena geometry: teardown/wwf-no-mercy/arenas/*.obj
   (AkiModel assemblies) converted to GLB by
   tools/stage-arena-pull/convert_nomercy.py — vertex colors from
   the .vc sidecars, fighting surface at y=0, uniform 0.007 scale.
   Template pieces (ring posts, turnbuckles, apron skirts, cage
   walls, announce table) ship in the ROM without placement data
   and are omitted; the builder re-adds procedural posts+ropes. */
const NM_ARENAS = [
  // nm-raw, RAW IS WAR, arena_raw.glb
  ['nm-raw', 'RAW IS WAR', 'arena_raw', true, '',
   14, 14, 5.2, -2.8, 2.8,
   '#ff6a5a', '#0a0508', '#3a0a10', '#140608', '#7a4a4a',
   `The real No Mercy RAW arena: titan tron, ramp, crowd bowl, ring. Template pieces (posts, ropes, aprons) omitted — ropes rebuilt procedurally.`],
  // nm-smackdown, SMACKDOWN, arena_smackdown.glb
  ['nm-smackdown', 'SMACKDOWN', 'arena_smackdown', true, '',
   14, 14, 5.2, -2.8, 2.8,
   '#6a9aff', '#04060e', '#0a1a3a', '#060a14', '#4a5a7a',
   `The real No Mercy SmackDown arena: blue stage set, oval tron, crowd bowl, ring.`],
  // nm-royal-rumble, ROYAL RUMBLE, arena_royal_rumble.glb
  ['nm-royal-rumble', 'ROYAL RUMBLE', 'arena_royal_rumble', true, '',
   14, 14, 5.2, -2.8, 2.8,
   '#b07aea', '#0a0612', '#2a1040', '#0c0816', '#5a4a7a',
   `The real No Mercy Royal Rumble arena.`],
  // nm-wrestlemania, WRESTLEMANIA, arena_wrestlemania.glb
  ['nm-wrestlemania', 'WRESTLEMANIA', 'arena_wrestlemania', true, '',
   14, 14, 5.2, -2.8, 2.8,
   '#ffca5a', '#0c0804', '#3a2408', '#100a06', '#7a6a4a',
   `The real No Mercy WrestleMania arena: grand stage, gold trim.`],
  // nm-king-of-the-ring, KING OF THE RING, arena_king_of_the_ring.glb
  ['nm-king-of-the-ring', 'KING OF THE RING', 'arena_king_of_the_ring', true, '',
   14, 14, 5.2, -2.8, 2.8,
   '#ff8a6a', '#0c0408', '#40101a', '#12060a', '#7a4a5a',
   `The real No Mercy King of the Ring arena.`],
  // nm-summerslam, SUMMERSLAM, arena_summerslam.glb
  ['nm-summerslam', 'SUMMERSLAM', 'arena_summerslam', true, '',
   14, 14, 5.2, -2.8, 2.8,
   '#ff9a3a', '#0c0804', '#402408', '#120c06', '#7a6a4a',
   `The real No Mercy SummerSlam arena.`],
  // nm-survivor-series, SURVIVOR SERIES, arena_survivor_series.glb
  ['nm-survivor-series', 'SURVIVOR SERIES', 'arena_survivor_series', true, '',
   14, 14, 5.2, -2.8, 2.8,
   '#5a7aff', '#04060c', '#0a1430', '#060a12', '#4a5a7a',
   `The real No Mercy Survivor Series arena.`],
  // nm-backlash, BACKLASH, arena_backlash.glb
  ['nm-backlash', 'BACKLASH', 'arena_backlash', true, '',
   14, 14, 5.2, -2.8, 2.8,
   '#ff4a4a', '#0a0404', '#380a0a', '#120606', '#7a4a4a',
   `The real No Mercy Backlash arena.`],
  // nm-armageddon, ARMAGEDDON, arena_armageddon.glb
  ['nm-armageddon', 'ARMAGEDDON', 'arena_armageddon', true, '',
   14, 14, 5.2, -2.8, 2.8,
   '#9aaa8a', '#060806', '#1a2416', '#0a0c08', '#5a6a5a',
   `The real No Mercy Armageddon arena.`],
  // nm-no-mercy, NO MERCY, arena_no_mercy.glb
  ['nm-no-mercy', 'NO MERCY', 'arena_no_mercy', true, '',
   14, 14, 5.2, -2.8, 2.8,
   '#a06aea', '#080410', '#200a3a', '#0c0616', '#5a4a7a',
   `The real No Mercy PPV arena: purple truss, No Mercy tron.`],
  // nm-cage, STEEL CAGE, arena_cage.glb
  ['nm-cage', 'STEEL CAGE', 'arena_cage', true, 'cage',
   12, 12, 4.6, -2.5, 2.5,
   '#aab0c0', '#060608', '#1a1a22', '#0a0a0e', '#5a5a6a',
   `The real No Mercy cage-match arena. Cage wall pieces ship as ROM templates (no placement data) — pending the arena-code RE lane.`],
  // nm-bar, BACKSTAGE: BAR, backstage_bar_lounge.glb
  ['nm-bar', 'BACKSTAGE: BAR', 'backstage_bar_lounge', false, '',
   6, 8, 2.8, -2, 2,
   '#ffca8a', '#0a0604', '#241408', '#0e0a06', '#6a5a4a',
   `Real No Mercy backstage bar/lounge: bottles, counter, chairs. Falls-count-anywhere energy.`],
  // nm-boiler-room, BACKSTAGE: BOILER ROOM, backstage_boiler_room.glb
  ['nm-boiler-room', 'BACKSTAGE: BOILER ROOM', 'backstage_boiler_room', false, '',
   10, 6, 4.5, -2.5, 2.5,
   '#ff9a5a', '#080604', '#201410', '#0c0806', '#6a5a4a',
   `Real No Mercy boiler room: pipes, tanks, industrial gloom.`],
  // nm-hallway, BACKSTAGE: HALLWAY, backstage_hallway.glb
  ['nm-hallway', 'BACKSTAGE: HALLWAY', 'backstage_hallway', false, '',
   5, 15, 2.2, -2, 2,
   '#c0c8d8', '#060608', '#14161c', '#0a0a0c', '#5a5e6a',
   `Real No Mercy backstage hallway: long corridor brawl.`],
  // nm-locker-room, BACKSTAGE: LOCKER ROOM, backstage_locker_room.glb
  ['nm-locker-room', 'BACKSTAGE: LOCKER ROOM', 'backstage_locker_room', false, '',
   10, 7, 4.5, -2.5, 2.5,
   '#ffd8a0', '#080604', '#1c140c', '#0c0806', '#6a5e4a',
   `Real No Mercy locker room: lockers, benches, chairs, whiteboard.`],
  // nm-parking-lot, BACKSTAGE: PARKING LOT, backstage_parking_lot.glb
  ['nm-parking-lot', 'BACKSTAGE: PARKING LOT', 'backstage_parking_lot', false, '',
   15, 14, 6.5, -3, 3,
   '#9ab0d0', '#04060a', '#101820', '#080a0e', '#5a6a7a',
   `Real No Mercy parking lot: cars, open asphalt, room to brawl.`],
  // nm-lobby-glb, LOBBY, lobby.glb
  ['nm-lobby-glb', 'LOBBY', 'lobby', false, '',
   11, 11, 5, -3, 3,
   '#d0b89a', '#080604', '#1a140e', '#0c0806', '#6a5e4a',
   `Real No Mercy lobby/gorilla position: the area just behind the curtain.`],
];
for (const [sid, nmName, glb, ropes, cageFlag, w, d, wall, s1, s2, sunC, sky0, sky1, fogC, hemiC, nmDesc] of NM_ARENAS) {
  STAGES.push({
    id: sid, name: nmName, tier: 'WWF NO MERCY',
    universe: 'WWF No Mercy (N64)', element: 'Wrestling',
    description: nmDesc + ' Extracted from the No Mercy ROM (Rev-A).',
    dims: { width: w, depth: d, wallDistance: wall },
    spawns: { p1: s1, p2: s2 },
    lighting: {
      sky: [[0.0, sky0], [0.6, sky1], [1.0, sky0]],
      fog: [fogC, 20, 70],
      hemi: [hemiC, '#0a0a0c', 1.5],
      sun: [sunC, 2.0, [-10, 7, 5]],
      rim: [sunC, 0.5, [8, 6, -7]],
      fill: ['#ffe0c0', 0.7, [0, 4, 10]],
    },
    floor: { kind: 'dark', tint: '#1c1c22', repeat: 30, platformTint: '#22222a', platformRepeat: 6 },
    swatch: [sky1, sunC],
    builder: 'nomercy',
    glb: `assets/stages/nomercy/${glb}.glb`,
    hidePlatform: true, // the GLB carries its own fighting surface
    ropes,
    cage: cageFlag === 'cage',
    associatedFighters: [],
  });
}
/* Per-stage camera + interior lighting: the cage camera sits INSIDE the
   walls; backstage rooms are small enclosed spaces needing their own
   camera distance and warm interior lights. */
for (const [sid, camDist, interior, camAngle] of [
  ['nm-cage', 4.2, false, 0], ['nm-bar', 3.0, true, 0],
  ['nm-boiler-room', 4.0, true, 0], ['nm-hallway', 5.0, true, 0],
  ['nm-locker-room', 3.5, true, 0], ['nm-parking-lot', 7, false, 32],
  ['nm-lobby-glb', 5.0, true, 28],
]) {
  const s = STAGES.find((x) => x.id === sid);
  if (s) { s.camDist = camDist; if (interior) s.interior = true; if (camAngle) s.camAngle = camAngle; }
}
// Explicit elevated poses for the two dense backstage areas (the default
// fighting camera sits inside pillars/lobby clutter at eye level).
for (const [sid, pos, tgt] of [
  ['nm-parking-lot', [8, 4.2, 10], [0, 0.4, 0]],
  ['nm-lobby-glb', [5.5, 3.6, 6.5], [0, 0.4, 0]],
]) {
  const s = STAGES.find((x) => x.id === sid);
  if (s) { s.camPos = pos; s.camTgt = tgt; }
}

/* Thumbnails: rendered own-eyes shots, one per stage
   (tools/stage-arena-pull/render_gallery.py). The select screen shows the
   thumbnail and falls back to the palette swatch when the file is absent. */
for (const s of STAGES) s.thumb = `assets/stages/thumbs/${s.id}.png`;

export function getStage(id) {
  return STAGES.find((s) => s.id === id) || STAGES[0];
}
export function randomStageId() {
  return STAGES[(Math.random() * STAGES.length) | 0].id;
}

/* ---------------- builders ----------------
   Each builder fills `g` (a THREE.Group) and returns an array of
   per-frame update functions: (dt, t) => void. `api` carries
   { isMobile, hex } helpers. */
function _hex(c) { return new THREE.Color(c); }

function buildBase(g, def, api) {
  const updaters = [];
  const L = def.lighting;
  // sky
  const skyTex = L.sky === 'veins' ? makeVeinSkyTexture() : makeSkyTexture(L.sky);
  // real teardown panorama backdrop (Eastern Mind bitmaps, etc.): a cylinder
  // wearing the original game's background art, behind the procedural sky.
  if (def.pano) {
    try {
      const panoTex = new THREE.TextureLoader().load(def.pano);
      panoTex.colorSpace = THREE.SRGBColorSpace;
      // The teardown panos are 580px-wide 2D backdrops: repeat 3x around so
      // the art reads at a sane scale instead of one stretched wrap.
      panoTex.wrapS = THREE.RepeatWrapping; panoTex.repeat.set(3, 1);
      const pano = new THREE.Mesh(
        new THREE.CylinderGeometry(30, 30, 10, 48, 1, true),
        new THREE.MeshBasicMaterial({ map: panoTex, side: THREE.BackSide, fog: false })
      );
      pano.position.y = 3.5; g.add(pano);
    } catch (e) {
      console.warn(`[WH] stage ${def.id}: pano ${def.pano} failed (${e.message})`);
    }
  }
  // ground far plane
  const ground = new THREE.Mesh(
    new THREE.PlaneGeometry(140, 140),
    makeFloorTexture(def.floor.kind, def.floor.tint, def.floor.repeat)
  );
  ground.rotation.x = -Math.PI / 2; ground.position.y = -0.05;
  ground.receiveShadow = true; g.add(ground);
  // fighting platform (16.8 wide arena, octagonal option for Par-fang).
  // Stages with real geometry floors (No Mercy GLBs) skip it: it would
  // z-fight the model's own fighting surface at y=0.
  if (!def.hidePlatform) {
    const platGeo = def.floor.octagon
      ? new THREE.CylinderGeometry(9.2, 9.6, 0.5, 8)
      : new THREE.CylinderGeometry(9.2, 9.6, 0.5, 8);
    const plat = new THREE.Mesh(platGeo,
      makeFloorTexture(def.floor.kind, def.floor.platformTint, def.floor.platformRepeat));
    plat.position.y = -0.25; plat.rotation.y = Math.PI / 8;
    plat.receiveShadow = true; g.add(plat);
  }
  // lights — unified rig (T7 light/lightstatic split: hemi+sky+fog is the
  // baked-ambient half; key/rim/fill + accent points are the dynamic half).
  // Also adds atmosphere motes (bible: "darkness is a material").
  const { updaters: rigUpdaters } = buildStageLightRig(g, def, api);
  updaters.push(...rigUpdaters);
  return { updaters, skyTex, fog: new THREE.Fog(_hex(L.fog[0]), L.fog[1], L.fog[2]) };
}

/* ---- SHRINE OF THE BLADE (moved from scene.js, unchanged visuals) ---- */
function buildShrine(g, def, api) {
  const { updaters, skyTex, fog } = buildBase(g, def, api);
  const lanterns = [];
  // ember trim ring
  const trim = new THREE.Mesh(new THREE.TorusGeometry(8.9, 0.09, 12, 8),
    new THREE.MeshBasicMaterial({ color: 0xff7a3c }));
  trim.rotation.x = Math.PI / 2; trim.rotation.z = Math.PI / 8; trim.position.y = 0.02; g.add(trim);
  // dark wood temple panels
  const woodTex = makeWoodTexture();
  const woodMat = new THREE.MeshStandardMaterial({ map: woodTex, roughness: 0.9, metalness: 0, color: 0x9a7a62 });
  for (let i = 0; i < 10; i++) {
    const a = (i / 10) * Math.PI * 2 + Math.PI / 10, r = 13.5;
    const panel = new THREE.Mesh(new THREE.BoxGeometry(8.6, 4.6, 0.5), woodMat);
    panel.position.set(Math.cos(a) * r, 2.2, Math.sin(a) * r);
    panel.lookAt(0, 2.2, 0); panel.receiveShadow = true; g.add(panel);
    const beam = new THREE.Mesh(new THREE.BoxGeometry(9.4, 0.5, 1.2),
      new THREE.MeshStandardMaterial({ color: 0x17100a, roughness: 0.9 }));
    beam.position.set(Math.cos(a) * r, 4.7, Math.sin(a) * r);
    beam.lookAt(0, 4.7, 0); g.add(beam);
  }
  // paper lanterns
  const postMat = new THREE.MeshStandardMaterial({ color: 0x1c120a, roughness: 0.8 });
  const paperMat = new THREE.MeshStandardMaterial({ color: 0xffd9a0, emissive: 0xff9a3c, emissiveIntensity: 1.6, roughness: 0.9 });
  for (let i = 0; i < 5; i++) {
    const a = (i / 5) * Math.PI * 2 + Math.PI / 5;
    const px = Math.cos(a) * 11.4, pz = Math.sin(a) * 11.4;
    const post = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.14, 3.0, 8), postMat);
    post.position.set(px, 1.5, pz); post.castShadow = true; g.add(post);
    const lantern = new THREE.Mesh(new THREE.CylinderGeometry(0.34, 0.34, 0.62, 12), paperMat);
    lantern.position.set(px, 3.2, pz); g.add(lantern);
    const capT = new THREE.Mesh(new THREE.CylinderGeometry(0.38, 0.38, 0.08, 12), postMat);
    capT.position.set(px, 3.55, pz); g.add(capT);
    const capB = capT.clone(); capB.position.y = 2.85; g.add(capB);
    const light = new THREE.PointLight(0xff9a4d, 12, 20, 2);
    light.position.set(px, 3.2, pz); g.add(light);
    lanterns.push({ light, base: 12, phase: Math.random() * 10 });
  }
  // toro stone lanterns
  const stoneMat = new THREE.MeshStandardMaterial({ color: 0x6a6a70, roughness: 0.95 });
  const fireMat = new THREE.MeshStandardMaterial({ color: 0xffc27a, emissive: 0xff8a2a, emissiveIntensity: 2.2 });
  const toroAt = (x, z, ry, withLight) => {
    const tg = new THREE.Group();
    const base = new THREE.Mesh(new THREE.BoxGeometry(0.9, 0.25, 0.9), stoneMat); base.position.y = 0.12; tg.add(base);
    const pillar = new THREE.Mesh(new THREE.CylinderGeometry(0.22, 0.26, 1.1, 8), stoneMat); pillar.position.y = 0.8; tg.add(pillar);
    const mid = new THREE.Mesh(new THREE.BoxGeometry(0.8, 0.18, 0.8), stoneMat); mid.position.y = 1.44; tg.add(mid);
    const firebox = new THREE.Mesh(new THREE.BoxGeometry(0.62, 0.5, 0.62), stoneMat); firebox.position.y = 1.78; tg.add(firebox);
    const glow = new THREE.Mesh(new THREE.BoxGeometry(0.66, 0.2, 0.66), fireMat); glow.position.y = 1.78; tg.add(glow);
    const roof = new THREE.Mesh(new THREE.ConeGeometry(0.72, 0.5, 4), stoneMat); roof.position.y = 2.28; roof.rotation.y = Math.PI / 4; tg.add(roof);
    tg.traverse(o => { if (o.isMesh) { o.castShadow = true; o.receiveShadow = true; } });
    if (withLight) {
      const light = new THREE.PointLight(0xff8a3a, 6, 9, 2);
      light.position.y = 1.78; tg.add(light);
      lanterns.push({ light, base: 6, phase: Math.random() * 10 });
    }
    tg.position.set(x, 0, z); tg.rotation.y = ry; g.add(tg);
  };
  toroAt(-9.4, -2.6, 0.4, true); toroAt(9.4, 2.6, -2.7, false);
  toroAt(-9.4, 2.6, -0.4, false); toroAt(9.4, -2.6, 2.7, true);
  // distant mountains
  const mtnMat = new THREE.MeshBasicMaterial({ color: 0x0d0a20 });
  for (let i = 0; i < 7; i++) {
    const w = 14 + Math.random() * 16, h = 8 + Math.random() * 14;
    const m = new THREE.Mesh(new THREE.ConeGeometry(w / 2, h, 5), mtnMat);
    const a = Math.PI + (i / 6 - 0.5) * 1.6;
    m.position.set(Math.sin(a) * 46, h / 2 - 1, -Math.cos(a) * 46);
    g.add(m);
  }
  // falling maple leaves (instanced)
  const N = api.isMobile ? 60 : 90;
  const leaves = new THREE.InstancedMesh(new THREE.PlaneGeometry(0.16, 0.16),
    new THREE.MeshBasicMaterial({ side: THREE.DoubleSide, transparent: true, opacity: 0.95 }), N);
  leaves.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
  leaves.frustumCulled = false;
  const colors = [0xd43a1a, 0xe86a1e, 0xc9202a, 0xf0a030];
  const leafData = [];
  const dummy = new THREE.Object3D(); const col = new THREE.Color();
  for (let i = 0; i < N; i++) {
    leafData.push({ x: (Math.random() - 0.5) * 26, y: Math.random() * 9, z: (Math.random() - 0.5) * 18,
      fall: 0.35 + Math.random() * 0.45, sway: Math.random() * 10, swayAmp: 0.4 + Math.random() * 0.8,
      rot: Math.random() * Math.PI * 2, rotV: (Math.random() - 0.5) * 3 });
    dummy.position.set(0, -99, 0); dummy.updateMatrix();
    leaves.setMatrixAt(i, dummy.matrix);
    col.setHex(colors[(Math.random() * colors.length) | 0]); leaves.setColorAt(i, col);
  }
  g.add(leaves);
  updaters.push((dt, t) => {
    for (const ln of lanterns) {
      const f = 0.8 + Math.sin(t * 9 + ln.phase) * 0.12 + Math.sin(t * 21 + ln.phase) * 0.08;
      ln.light.intensity = ln.base * f;
    }
    for (let i = 0; i < leafData.length; i++) {
      const L = leafData[i];
      L.y -= L.fall * dt; L.sway += dt * 1.6; L.rot += L.rotV * dt;
      if (L.y < 0) { L.y = 8 + Math.random() * 2; L.x = (Math.random() - 0.5) * 26; }
      dummy.position.set(L.x + Math.sin(L.sway) * L.swayAmp, L.y, L.z + Math.cos(L.sway * 0.7) * L.swayAmp * 0.5);
      dummy.rotation.set(L.rot, L.rot * 0.7, L.rot * 0.4);
      dummy.updateMatrix(); leaves.setMatrixAt(i, dummy.matrix);
    }
    leaves.instanceMatrix.needsUpdate = true;
  });
  return { updaters, skyTex, fog };
}

/* ---- TONG-NOU: the giant green head in the dark ---- */
function buildTongNou(g, def, api) {
  const { updaters, skyTex, fog } = buildBase(g, def, api);
  const headTex = _canvas(512, (ctx, s) => {
    ctx.fillStyle = '#1a5a2a'; ctx.fillRect(0, 0, s, s);
    for (let i = 0; i < 4000; i++) {
      const v = 20 + Math.random() * 50;
      ctx.fillStyle = `rgba(${v * 0.4},${v},${v * 0.5},${Math.random() * 0.5})`;
      ctx.fillRect(Math.random() * s, Math.random() * s, 3, 3);
    }
    ctx.strokeStyle = 'rgba(120,220,140,0.4)'; ctx.lineWidth = 3;
    for (let i = 0; i < 30; i++) {
      ctx.beginPath(); let x = Math.random() * s, y = 0; ctx.moveTo(x, y);
      for (let k = 0; k < 8; k++) { x += (Math.random() - 0.5) * 80; y += s / 8; ctx.lineTo(x, y); }
      ctx.stroke();
    }
  });
  const head = new THREE.Mesh(new THREE.SphereGeometry(18, 32, 24),
    new THREE.MeshStandardMaterial({ map: headTex, roughness: 0.7, emissive: 0x0a3a14, emissiveIntensity: 0.7 }));
  head.position.set(0, 17, -58); g.add(head);
  const eyeMat = new THREE.MeshBasicMaterial({ color: 0xaaffaa });
  const eyeL = new THREE.Mesh(new THREE.SphereGeometry(1.3, 16, 12), eyeMat);
  const eyeR = eyeL.clone();
  eyeL.position.set(-6, 19, -39); eyeR.position.set(6, 19, -39);
  g.add(eyeL, eyeR);
  const eyeLight = new THREE.PointLight(0x5aff7a, 30, 60, 2);
  eyeLight.position.set(0, 17, -39); g.add(eyeLight);
  const N = api.isMobile ? 50 : 120;
  const motes = new THREE.InstancedMesh(new THREE.SphereGeometry(0.09, 8, 6),
    new THREE.MeshBasicMaterial({ color: 0x9affaa, transparent: true, opacity: 0.85 }), N);
  motes.frustumCulled = false;
  const moteData = []; const dummy = new THREE.Object3D();
  for (let i = 0; i < N; i++) {
    moteData.push({ x: (Math.random() - 0.5) * 40, y: Math.random() * 12, z: (Math.random() - 0.5) * 30,
      sp: 0.2 + Math.random() * 0.5, ph: Math.random() * 10 });
    dummy.position.set(0, -99, 0); dummy.updateMatrix(); motes.setMatrixAt(i, dummy.matrix);
  }
  g.add(motes);
  updaters.push((dt, t, fA, fB) => {
    if (fA && fB) {
      const mid = (fA.root.position.x + fB.root.position.x) / 2;
      eyeL.position.x = -6 + mid * 0.2; eyeR.position.x = 6 + mid * 0.2;
    }
    const pulse = 0.75 + Math.sin(t * 1.7) * 0.25;
    eyeMat.color.setRGB(0.55 * pulse + 0.2, 1.0 * pulse, 0.55 * pulse + 0.2);
    eyeLight.intensity = 30 * pulse;
    for (let i = 0; i < moteData.length; i++) {
      const m = moteData[i];
      m.y += m.sp * dt; if (m.y > 13) m.y = 0;
      dummy.position.set(m.x + Math.sin(t * 0.6 + m.ph) * 1.2, m.y, m.z);
      dummy.updateMatrix(); motes.setMatrixAt(i, dummy.matrix);
    }
    motes.instanceMatrix.needsUpdate = true;
  });
  return { updaters, skyTex, fog };
}

/* ---- TREE OF LIFE (Ming-ken): colossal tree + soul fruit + Sha-mo Desert ---- */
function buildTreeLife(g, def, api) {
  const { updaters, skyTex, fog } = buildBase(g, def, api);
  const barkMat = new THREE.MeshStandardMaterial({ color: 0x4a3420, roughness: 1 });
  const trunk = new THREE.Mesh(new THREE.CylinderGeometry(2.2, 3.0, 18, 10), barkMat);
  trunk.position.set(-10, 8, -15); trunk.castShadow = true; g.add(trunk);
  const leafMat = new THREE.MeshStandardMaterial({ color: 0x1e4a24, roughness: 0.9 });
  for (const [x, y, z, r] of [[-10, 17, -15, 6], [-14, 15, -13, 4], [-6, 15.5, -16, 4.5], [-10, 20, -15, 5]]) {
    const c = new THREE.Mesh(new THREE.SphereGeometry(r, 14, 10), leafMat);
    c.position.set(x, y, z); g.add(c);
  }
  const N = api.isMobile ? 24 : 48;
  const fruits = new THREE.InstancedMesh(new THREE.SphereGeometry(0.22, 10, 8),
    new THREE.MeshStandardMaterial({ color: 0xffd98a, emissive: 0xffb83a, emissiveIntensity: 2.4 }), N);
  fruits.frustumCulled = false;
  const fruitData = []; const dummy = new THREE.Object3D();
  for (let i = 0; i < N; i++) {
    const a = Math.random() * Math.PI * 2, r = 1.5 + Math.random() * 3;
    fruitData.push({ x: -10 + Math.cos(a) * r, y: 11 + Math.random() * 6, z: -15 + Math.sin(a) * r, ph: Math.random() * 10 });
  }
  g.add(fruits);
  const fruitLight = new THREE.PointLight(0xffc86a, 20, 40, 2);
  fruitLight.position.set(-10, 14, -15); g.add(fruitLight);
  const duneMat = new THREE.MeshStandardMaterial({ color: 0xa8824e, roughness: 1 });
  for (let i = 0; i < 6; i++) {
    const d = new THREE.Mesh(new THREE.SphereGeometry(6 + Math.random() * 6, 12, 8, 0, Math.PI * 2, 0, Math.PI / 2), duneMat);
    const a = Math.PI + (i / 5 - 0.5) * 2.2;
    d.position.set(Math.sin(a) * 42, -0.4, -Math.cos(a) * 42);
    d.scale.y = 0.35; g.add(d);
  }
  updaters.push((dt, t) => {
    for (let i = 0; i < fruitData.length; i++) {
      const f = fruitData[i];
      dummy.position.set(f.x, f.y + Math.sin(t * 1.2 + f.ph) * 0.4, f.z);
      dummy.updateMatrix(); fruits.setMatrixAt(i, dummy.matrix);
    }
    fruits.instanceMatrix.needsUpdate = true;
    fruitLight.intensity = 20 * (0.8 + Math.sin(t * 2.1) * 0.2);
  });
  return { updaters, skyTex, fog };
}

/* ---- PLAINS OF CHI-U: scorched plains + the Fire Tower of Time ---- */
function buildChiU(g, def, api) {
  const { updaters, skyTex, fog } = buildBase(g, def, api);
  const towerMat = new THREE.MeshStandardMaterial({ color: 0x1a0f0c, roughness: 0.95 });
  const tower = new THREE.Mesh(new THREE.BoxGeometry(4, 26, 4), towerMat);
  tower.position.set(9, 12, -20); tower.castShadow = true; g.add(tower);
  const winMat = new THREE.MeshBasicMaterial({ color: 0xff7a2a });
  for (let i = 0; i < 6; i++) {
    const w = new THREE.Mesh(new THREE.PlaneGeometry(2.6, 0.7), winMat);
    w.position.set(9, 4 + i * 3.6, -17.95); g.add(w);
  }
  const fireLight = new THREE.PointLight(0xff5a1a, 60, 55, 2);
  fireLight.position.set(9, 14, -18); g.add(fireLight);
  const N = api.isMobile ? 40 : 80;
  const embers = new THREE.InstancedMesh(new THREE.PlaneGeometry(0.12, 0.12),
    new THREE.MeshBasicMaterial({ color: 0xff8a3a, transparent: true, opacity: 0.9, side: THREE.DoubleSide }), N);
  embers.frustumCulled = false;
  const emberData = []; const dummy = new THREE.Object3D();
  for (let i = 0; i < N; i++) {
    emberData.push({ x: (Math.random() - 0.5) * 30, y: Math.random() * 10, z: (Math.random() - 0.5) * 20,
      sp: 0.8 + Math.random() * 1.6, ph: Math.random() * 10 });
    dummy.position.set(0, -99, 0); dummy.updateMatrix(); embers.setMatrixAt(i, dummy.matrix);
  }
  g.add(embers);
  updaters.push((dt, t) => {
    const fl = 0.75 + Math.sin(t * 11) * 0.15 + Math.sin(t * 23 + 1) * 0.1;
    fireLight.intensity = 60 * fl;
    for (let i = 0; i < emberData.length; i++) {
      const e = emberData[i];
      e.y += e.sp * dt; if (e.y > 12) { e.y = 0; e.x = (Math.random() - 0.5) * 30; }
      dummy.position.set(e.x + Math.sin(t * 2 + e.ph) * 0.8, e.y, e.z);
      dummy.rotation.set(0, t * 2 + e.ph, 0);
      dummy.updateMatrix(); embers.setMatrixAt(i, dummy.matrix);
    }
    embers.instanceMatrix.needsUpdate = true;
  });
  return { updaters, skyTex, fog };
}

/* ---- OCTAGONAL SHRINE PAR-FANG: eight-sided, ancient, still ---- */
function buildParFang(g, def, api) {
  const { updaters, skyTex, fog } = buildBase(g, def, api);
  const pilMat = new THREE.MeshStandardMaterial({ color: 0x5a5462, roughness: 0.9 });
  const capMat = new THREE.MeshStandardMaterial({ color: 0xc0a060, emissive: 0x6a4a1a, emissiveIntensity: 0.8, roughness: 0.6 });
  for (let i = 0; i < 8; i++) {
    const a = (i / 8) * Math.PI * 2 + Math.PI / 8, r = 12.5;
    const p = new THREE.Mesh(new THREE.BoxGeometry(1.2, 7, 1.2), pilMat);
    p.position.set(Math.cos(a) * r, 3.5, Math.sin(a) * r);
    p.castShadow = true; p.receiveShadow = true; g.add(p);
    const cap = new THREE.Mesh(new THREE.BoxGeometry(1.6, 0.5, 1.6), capMat);
    cap.position.set(Math.cos(a) * r, 7.2, Math.sin(a) * r); g.add(cap);
  }
  const ring = new THREE.Mesh(new THREE.TorusGeometry(7.6, 0.07, 8, 64),
    new THREE.MeshBasicMaterial({ color: 0xc0a060 }));
  ring.rotation.x = Math.PI / 2; ring.position.y = 0.03; g.add(ring);
  const N = api.isMobile ? 30 : 60;
  const dust = new THREE.InstancedMesh(new THREE.SphereGeometry(0.05, 6, 4),
    new THREE.MeshBasicMaterial({ color: 0xa09ab0, transparent: true, opacity: 0.5 }), N);
  dust.frustumCulled = false;
  const dustData = []; const dummy = new THREE.Object3D();
  for (let i = 0; i < N; i++) {
    dustData.push({ x: (Math.random() - 0.5) * 24, y: Math.random() * 8, z: (Math.random() - 0.5) * 16, ph: Math.random() * 10 });
    dummy.position.set(0, -99, 0); dummy.updateMatrix(); dust.setMatrixAt(i, dummy.matrix);
  }
  g.add(dust);
  updaters.push((dt, t) => {
    for (let i = 0; i < dustData.length; i++) {
      const d = dustData[i];
      dummy.position.set(d.x + Math.sin(t * 0.3 + d.ph) * 2, d.y + Math.sin(t * 0.2 + d.ph) * 0.5, d.z);
      dummy.updateMatrix(); dust.setMatrixAt(i, dummy.matrix);
    }
    dust.instanceMatrix.needsUpdate = true;
  });
  return { updaters, skyTex, fog };
}

/* ---- HELIX PALACE: spiral palace + five glowing desire rooms ---- */
function buildHelix(g, def, api) {
  const { updaters, skyTex, fog } = buildBase(g, def, api);
  const wallMat = new THREE.MeshStandardMaterial({ color: 0x3a3a4e, roughness: 0.4, metalness: 0.8 });
  for (let i = 0; i < 24; i++) {
    const a = (i / 24) * Math.PI * 2.6, r = 12 + i * 0.25;
    const seg = new THREE.Mesh(new THREE.BoxGeometry(4.2, 5.5, 0.4), wallMat);
    seg.position.set(Math.cos(a) * r, 2.6, Math.sin(a) * r);
    seg.lookAt(0, 2.6, 0); g.add(seg);
  }
  const rooms = [
    [0xffd24a, -9, 2.2, -7], [0xff6a2a, 9, 2.2, -7], [0xf0f0ff, 0, 2.6, -11],
    [0xff4a9a, -6, 2.2, 8], [0x8a2ae0, 6, 2.2, 8],
  ];
  const roomMats = [];
  for (const [color, x, y, z] of rooms) {
    const m = new THREE.MeshStandardMaterial({ color, emissive: color, emissiveIntensity: 1.0, roughness: 0.3 });
    const pod = new THREE.Mesh(new THREE.SphereGeometry(0.9, 18, 14), m);
    pod.position.set(x, y, z); g.add(pod);
    const halo = new THREE.PointLight(color, 8, 14, 2);
    halo.position.set(x, y, z); g.add(halo);
    roomMats.push({ m, halo, base: 1.0, ph: Math.random() * 10 });
  }
  updaters.push((dt, t) => {
    for (const r of roomMats) {
      const p = 0.7 + Math.sin(t * 2.4 + r.ph) * 0.3;
      r.m.emissiveIntensity = r.base * p;
      r.halo.intensity = 8 * p;
    }
  });
  return { updaters, skyTex, fog };
}

/* ---- PALACE OF DREAMING: rippling walls, mirror floor, a sky that isn't there ---- */
function buildDreaming(g, def, api) {
  const { updaters, skyTex, fog } = buildBase(g, def, api);
  const walls = [];
  for (let i = 0; i < 8; i++) {
    const a = (i / 8) * Math.PI * 2, r = 14;
    const w = new THREE.Mesh(new THREE.PlaneGeometry(7, 5.5),
      new THREE.MeshStandardMaterial({ color: 0x3a5ac0, emissive: 0x1a2a80, emissiveIntensity: 0.7,
        transparent: true, opacity: 0.55, roughness: 0.2, metalness: 0.3, side: THREE.DoubleSide }));
    w.position.set(Math.cos(a) * r, 3.2, Math.sin(a) * r);
    w.lookAt(0, 3.2, 0); g.add(w);
    walls.push({ w, ph: (i / 8) * Math.PI * 2 });
  }
  const N = api.isMobile ? 16 : 32;
  const orbs = new THREE.InstancedMesh(new THREE.SphereGeometry(0.3, 12, 10),
    new THREE.MeshBasicMaterial({ color: 0x9ae0ff, transparent: true, opacity: 0.7 }), N);
  orbs.frustumCulled = false;
  const orbData = []; const dummy = new THREE.Object3D();
  for (let i = 0; i < N; i++) {
    orbData.push({ x: (Math.random() - 0.5) * 26, y: 1 + Math.random() * 7, z: (Math.random() - 0.5) * 18, ph: Math.random() * 10 });
    dummy.position.set(0, -99, 0); dummy.updateMatrix(); orbs.setMatrixAt(i, dummy.matrix);
  }
  g.add(orbs);
  updaters.push((dt, t) => {
    for (const { w, ph } of walls) {
      w.material.emissiveIntensity = 0.9 * (0.6 + Math.sin(t * 1.5 + ph) * 0.4);
      w.position.y = 3.2 + Math.sin(t * 0.9 + ph) * 0.5;
    }
    for (let i = 0; i < orbData.length; i++) {
      const o = orbData[i];
      dummy.position.set(o.x + Math.sin(t * 0.7 + o.ph) * 1.5, o.y + Math.sin(t * 1.1 + o.ph) * 0.8, o.z);
      const s = 0.7 + Math.sin(t * 2 + o.ph) * 0.3;
      dummy.scale.set(s, s, s); dummy.updateMatrix(); orbs.setMatrixAt(i, dummy.matrix);
    }
    dummy.scale.set(1, 1, 1);
    orbs.instanceMatrix.needsUpdate = true;
  });
  return { updaters, skyTex, fog };
}

/* ---- PHANTOM MARKETPLACE: bazaar stalls under the Eyeball Mountains ---- */
function buildMarketplace(g, def, api) {
  const { updaters, skyTex, fog } = buildBase(g, def, api);
  const eyeTex = makeEyeTexture();
  const mtnMat = new THREE.MeshStandardMaterial({ color: 0x1a1426, roughness: 1 });
  const eyeAt = (x, z, s) => {
    const cone = new THREE.Mesh(new THREE.ConeGeometry(7 * s, 16 * s, 7), mtnMat);
    cone.position.set(x, 8 * s - 1, z); g.add(cone);
    const eye = new THREE.Mesh(new THREE.SphereGeometry(2.4 * s, 18, 14),
      new THREE.MeshStandardMaterial({ map: eyeTex, roughness: 0.25 }));
    eye.position.set(x, 16.5 * s - 1, z); g.add(eye);
    return eye;
  };
  const eyes = [eyeAt(-24, -32, 0.9), eyeAt(0, -40, 1.1), eyeAt(24, -32, 0.9), eyeAt(-16, -14, 0.7), eyeAt(16, -14, 0.7)];
  const stallWood = new THREE.MeshStandardMaterial({ color: 0x6a4020, roughness: 0.9 });
  const awnTex = _canvas(128, (ctx, s) => {
    for (let i = 0; i < 8; i++) { ctx.fillStyle = i % 2 ? '#8a2a4a' : '#e0c080'; ctx.fillRect(i * s / 8, 0, s / 8, s); }
  });
  const awnMat = new THREE.MeshStandardMaterial({ map: awnTex, roughness: 0.8, side: THREE.DoubleSide });
  const stallAt = (x, z, ry) => {
    const st = new THREE.Group();
    const counter = new THREE.Mesh(new THREE.BoxGeometry(2.4, 1.0, 1.2), stallWood);
    counter.position.y = 0.5; counter.castShadow = true; st.add(counter);
    for (const [px, pz] of [[-1.1, -0.5], [1.1, -0.5], [-1.1, 0.5], [1.1, 0.5]]) {
      const post = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, 2.4, 6), stallWood);
      post.position.set(px, 1.2, pz); st.add(post);
    }
    const awn = new THREE.Mesh(new THREE.PlaneGeometry(3.0, 1.8), awnMat);
    awn.position.y = 2.5; awn.rotation.x = -0.35; st.add(awn);
    for (let i = 0; i < 4; i++) {
      const jar = new THREE.Mesh(new THREE.SphereGeometry(0.14, 8, 6),
        new THREE.MeshStandardMaterial({ color: 0xffc86a, emissive: 0xff9a3a, emissiveIntensity: 1.6 }));
      jar.position.set(-0.8 + i * 0.5, 1.15, (Math.random() - 0.5) * 0.5); st.add(jar);
    }
    st.position.set(x, 0, z); st.rotation.y = ry; g.add(st);
  };
  stallAt(-7.5, -3, 0.5); stallAt(7.5, -3, -0.5); stallAt(-7.5, 4, 2.6); stallAt(7.5, 4, -2.6);
  const bulbMat = new THREE.MeshBasicMaterial({ color: 0xffc86a });
  for (let i = 0; i <= 12; i++) {
    const b = new THREE.Mesh(new THREE.SphereGeometry(0.09, 8, 6), bulbMat);
    const k = i / 12;
    b.position.set(-11 + 22 * k, 4.2 - Math.sin(k * Math.PI) * 1.2, -4);
    g.add(b);
  }
  const bLight = new THREE.PointLight(0xffaa5a, 18, 30, 2);
  bLight.position.set(0, 4, -4); g.add(bLight);
  const stallLight = new THREE.PointLight(0xffc080, 12, 25, 2);
  stallLight.position.set(0, 3, 1); g.add(stallLight);
  updaters.push((dt, t) => {
    for (const e of eyes) e.rotation.y = Math.sin(t * 0.4) * 0.25;
    bLight.intensity = 18 * (0.85 + Math.sin(t * 7) * 0.1 + Math.sin(t * 13) * 0.05);
  });
  return { updaters, skyTex, fog };
}

/* ---- HELIX PALACE: Pink Narwhal club interior (teardown-sourced detail pass) ----
   Arena upgrade pipeline, Stage 3: the procedural spiral blockout below is kept
   as the no-GLB fallback (it is the saved Stage-2 draft in arenas/drafts/); the
   real geometry is the Pink Narwhal club map (SmutBase Virt-A-Mate scene,
   converted by tools/stage-arena-pull/convert_pinknarwhal.py). The five canon
   desire rooms ride as glowing pods marking the club's five zones. */
async function buildHelix(g, def, api) {
  const { updaters, skyTex, fog } = buildBase(g, def, api);
  let detailed = false;
  if (def.glb) {
    try {
      const gltf = await new GLTFLoader().loadAsync(def.glb);
      const club = gltf.scene;
      club.traverse((o) => {
        if (o.isMesh) {
          o.castShadow = true; o.receiveShadow = true;
          if (o.material && o.geometry.getAttribute('color'))
            o.material.vertexColors = true;
        }
      });
      g.add(club);
      detailed = true;
    } catch (e) {
      console.warn(`[WH] stage ${def.id}: GLB ${def.glb} failed (${e.message}), blockout fallback`);
    }
  }
  if (!detailed) {
    // Stage-2 blockout fallback: spiral palace walls (the approved blockout).
    const wallMat = new THREE.MeshStandardMaterial({ color: 0x3a3a4e, roughness: 0.4, metalness: 0.8 });
    for (let i = 0; i < 24; i++) {
      const a = (i / 24) * Math.PI * 2.6, r = 12 + i * 0.25;
      const seg = new THREE.Mesh(new THREE.BoxGeometry(4.2, 5.5, 0.4), wallMat);
      seg.position.set(Math.cos(a) * r, 2.6, Math.sin(a) * r);
      seg.lookAt(0, 2.6, 0); g.add(seg);
    }
  }
  // Five desire rooms (canon): Greed, Appetite, Immortality, Sexual Desire,
  // Destruction. With the club interior they mark the five zones — VIP west,
  // bar east, stage center-back, pole stage, DJ booth.
  const rooms = detailed ? [
    [0xffd24a, -7.5, 3.0, -9], [0xff6a2a, 7.5, 3.0, -9], [0xf0f0ff, 0, 3.6, -12],
    [0xff4a9a, 1.2, 3.0, -9.5], [0x8a2ae0, 5.8, 3.0, -10],
  ] : [
    [0xffd24a, -9, 2.2, -7], [0xff6a2a, 9, 2.2, -7], [0xf0f0ff, 0, 2.6, -11],
    [0xff4a9a, -6, 2.2, 8], [0x8a2ae0, 6, 2.2, 8],
  ];
  const roomMats = [];
  for (const [color, x, y, z] of rooms) {
    const m = new THREE.MeshStandardMaterial({ color, emissive: color, emissiveIntensity: 1.0, roughness: 0.3 });
    const pod = new THREE.Mesh(new THREE.SphereGeometry(0.9, 18, 14), m);
    pod.position.set(x, y, z); g.add(pod);
    const halo = new THREE.PointLight(color, 8, 14, 2);
    halo.position.set(x, y, z); g.add(halo);
    roomMats.push({ m, halo, base: 1.0, ph: Math.random() * 10 });
  }
  updaters.push((dt, t) => {
    for (const r of roomMats) {
      const p = 0.7 + Math.sin(t * 2.4 + r.ph) * 0.3;
      r.m.emissiveIntensity = r.base * p;
      r.halo.intensity = 8 * p;
    }
  });
  return { updaters, skyTex, fog };
}

/* ---- PALACE OF DREAMING: rippling walls, mirror floor, a sky that isn't there ---- */
function buildDreaming(g, def, api) {
  const { updaters, skyTex, fog } = buildBase(g, def, api);
  const walls = [];
  for (let i = 0; i < 8; i++) {
    const a = (i / 8) * Math.PI * 2, r = 14;
    const w = new THREE.Mesh(new THREE.PlaneGeometry(7, 5.5),
      new THREE.MeshStandardMaterial({ color: 0x3a5ac0, emissive: 0x1a2a80, emissiveIntensity: 0.7,
        transparent: true, opacity: 0.55, roughness: 0.2, metalness: 0.3, side: THREE.DoubleSide }));
    w.position.set(Math.cos(a) * r, 3.2, Math.sin(a) * r);
    w.lookAt(0, 3.2, 0); g.add(w);
    walls.push({ w, ph: (i / 8) * Math.PI * 2 });
  }
  const N = api.isMobile ? 16 : 32;
  const orbs = new THREE.InstancedMesh(new THREE.SphereGeometry(0.3, 12, 10),
    new THREE.MeshBasicMaterial({ color: 0x9ae0ff, transparent: true, opacity: 0.7 }), N);
  orbs.frustumCulled = false;
  const orbData = []; const dummy = new THREE.Object3D();
  for (let i = 0; i < N; i++) {
    orbData.push({ x: (Math.random() - 0.5) * 26, y: 1 + Math.random() * 7, z: (Math.random() - 0.5) * 18, ph: Math.random() * 10 });
    dummy.position.set(0, -99, 0); dummy.updateMatrix(); orbs.setMatrixAt(i, dummy.matrix);
  }
  g.add(orbs);
  updaters.push((dt, t) => {
    for (const { w, ph } of walls) {
      w.material.emissiveIntensity = 0.9 * (0.6 + Math.sin(t * 1.5 + ph) * 0.4);
      w.position.y = 3.2 + Math.sin(t * 0.9 + ph) * 0.5;
    }
    for (let i = 0; i < orbData.length; i++) {
      const o = orbData[i];
      dummy.position.set(o.x + Math.sin(t * 0.7 + o.ph) * 1.5, o.y + Math.sin(t * 1.1 + o.ph) * 0.8, o.z);
      const s = 0.7 + Math.sin(t * 2 + o.ph) * 0.3;
      dummy.scale.set(s, s, s); dummy.updateMatrix(); orbs.setMatrixAt(i, dummy.matrix);
    }
    dummy.scale.set(1, 1, 1);
    orbs.instanceMatrix.needsUpdate = true;
  });
  return { updaters, skyTex, fog };
}

/* ---- PHANTOM MARKETPLACE: bazaar stalls under the Eyeball Mountains ---- */
function buildMarketplace(g, def, api) {
  const { updaters, skyTex, fog } = buildBase(g, def, api);
  const eyeTex = makeEyeTexture();
  const mtnMat = new THREE.MeshStandardMaterial({ color: 0x1a1426, roughness: 1 });
  const eyeAt = (x, z, s) => {
    const cone = new THREE.Mesh(new THREE.ConeGeometry(7 * s, 16 * s, 7), mtnMat);
    cone.position.set(x, 8 * s - 1, z); g.add(cone);
    const eye = new THREE.Mesh(new THREE.SphereGeometry(2.4 * s, 18, 14),
      new THREE.MeshStandardMaterial({ map: eyeTex, roughness: 0.25 }));
    eye.position.set(x, 16.5 * s - 1, z); g.add(eye);
    return eye;
  };
  const eyes = [eyeAt(-24, -32, 0.9), eyeAt(0, -40, 1.1), eyeAt(24, -32, 0.9), eyeAt(-16, -14, 0.7), eyeAt(16, -14, 0.7)];
  const stallWood = new THREE.MeshStandardMaterial({ color: 0x6a4020, roughness: 0.9 });
  const awnTex = _canvas(128, (ctx, s) => {
    for (let i = 0; i < 8; i++) { ctx.fillStyle = i % 2 ? '#8a2a4a' : '#e0c080'; ctx.fillRect(i * s / 8, 0, s / 8, s); }
  });
  const awnMat = new THREE.MeshStandardMaterial({ map: awnTex, roughness: 0.8, side: THREE.DoubleSide });
  const stallAt = (x, z, ry) => {
    const st = new THREE.Group();
    const counter = new THREE.Mesh(new THREE.BoxGeometry(2.4, 1.0, 1.2), stallWood);
    counter.position.y = 0.5; counter.castShadow = true; st.add(counter);
    for (const [px, pz] of [[-1.1, -0.5], [1.1, -0.5], [-1.1, 0.5], [1.1, 0.5]]) {
      const post = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, 2.4, 6), stallWood);
      post.position.set(px, 1.2, pz); st.add(post);
    }
    const awn = new THREE.Mesh(new THREE.PlaneGeometry(3.0, 1.8), awnMat);
    awn.position.y = 2.5; awn.rotation.x = -0.35; st.add(awn);
    for (let i = 0; i < 4; i++) {
      const jar = new THREE.Mesh(new THREE.SphereGeometry(0.14, 8, 6),
        new THREE.MeshStandardMaterial({ color: 0xffc86a, emissive: 0xff9a3a, emissiveIntensity: 1.6 }));
      jar.position.set(-0.8 + i * 0.5, 1.15, (Math.random() - 0.5) * 0.5); st.add(jar);
    }
    st.position.set(x, 0, z); st.rotation.y = ry; g.add(st);
  };
  stallAt(-7.5, -3, 0.5); stallAt(7.5, -3, -0.5); stallAt(-7.5, 4, 2.6); stallAt(7.5, 4, -2.6);
  const bulbMat = new THREE.MeshBasicMaterial({ color: 0xffc86a });
  for (let i = 0; i <= 12; i++) {
    const b = new THREE.Mesh(new THREE.SphereGeometry(0.09, 8, 6), bulbMat);
    const k = i / 12;
    b.position.set(-11 + 22 * k, 4.2 - Math.sin(k * Math.PI) * 1.2, -4);
    g.add(b);
  }
  const bLight = new THREE.PointLight(0xffaa5a, 18, 30, 2);
  bLight.position.set(0, 4, -4); g.add(bLight);
  const stallLight = new THREE.PointLight(0xffc080, 12, 25, 2);
  stallLight.position.set(0, 3, 1); g.add(stallLight);
  updaters.push((dt, t) => {
    for (const e of eyes) e.rotation.y = Math.sin(t * 0.4) * 0.25;
    bLight.intensity = 18 * (0.85 + Math.sin(t * 7) * 0.1 + Math.sin(t * 13) * 0.05);
  });
  return { updaters, skyTex, fog };
}

/* ---- TEKKEN RETRO: real T3 panorama shell + decoded texture atlas ---- */
async function buildT3Retro(g, def, api) {
  const { updaters, skyTex, fog } = buildBase(g, def, api);
  try {
    const geo = await fetchStageOBJ(def.obj);
    geo.scale(0.015, 0.015, 0.015); // T3 units (~±1200) -> game units
    let mat = null;
    if (def.map) {
      try {
        const tex = await new THREE.TextureLoader().loadAsync(def.map);
        tex.colorSpace = THREE.SRGBColorSpace;
        tex.anisotropy = 4;
        mat = new THREE.MeshBasicMaterial({
          map: tex, vertexColors: !!geo.getAttribute('color'),
          side: THREE.DoubleSide, fog: true,
        });
      } catch (e) {
        console.warn(`[WH] stage ${def.id}: atlas ${def.map} failed (${e.message}), tint fallback`);
      }
    }
    if (!mat) { // untextured fallback: palette-tinted shell
      mat = new THREE.MeshBasicMaterial({
        color: _hex(def.panoTint), side: THREE.DoubleSide, fog: true,
      });
    }
    const shell = new THREE.Mesh(geo, mat);
    // The TMD panorama shell spans y<=0 (below the floor plane) — lift it
    // so its midsection forms a visible backdrop ridge above the horizon.
    shell.position.y = 6;
    g.add(shell);
  } catch (e) {
    console.warn(`[WH] stage ${def.id}: panorama failed (${e.message}), palette backdrop only`);
  }
  // arena edge markers in the stage palette
  const edge = new THREE.Mesh(new THREE.TorusGeometry(8.9, 0.08, 10, 48),
    new THREE.MeshBasicMaterial({ color: _hex(def.lighting.sun[0]) }));
  edge.rotation.x = Math.PI / 2; edge.position.y = 0.02; g.add(edge);
  return { updaters, skyTex, fog };
}

/* ---- WWF NO MERCY: real N64 arena GLB + procedural ropes ----
   The GLB carries vertex-colored arena geometry with the fighting surface
   at y=0. The ROM never stored ropes (procedural at runtime) and its ring
   posts/turnbuckles/aprons are placement-less templates, so the builder
   re-adds simple posts + 3 ropes per side for ring arenas. Backstage
   arenas (rooms, lot) skip ropes. */
async function buildNoMercy(g, def, api) {
  const { updaters, skyTex, fog } = buildBase(g, def, api);
  if (def.glb) {
    // GLB arena family (arena-pull lane): real N64 arena GLB + ring furniture.
      try {
        const gltf = await new GLTFLoader().loadAsync(def.glb);
        const arena = gltf.scene;
        arena.traverse((o) => {
          if (o.isMesh) {
            o.castShadow = true; o.receiveShadow = true;
            // GLBs ship vertex colors; make sure the material honors them.
            if (o.material && o.geometry.getAttribute('color'))
              o.material.vertexColors = true;
          }
        });
        g.add(arena);
      } catch (e) {
        console.warn(`[WH] stage ${def.id}: GLB ${def.glb} failed (${e.message})`);
      }
      if (def.interior) {
        // enclosed backstage rooms: warm ceiling lights (the sun/rim rig is
        // built for open arenas and doesn't reach indoors)
        for (const [lx, lz] of [[-2.5, -1.5], [2.5, 1.5], [0, 0]]) {
          const pl = new THREE.PointLight(0xffd9a0, 7, 14, 2);
          pl.position.set(lx, 2.0, lz); g.add(pl);
        }
      }
      if (def.id === 'nm-parking-lot') {
        // night lot: cool sodium streetlights so the fighters read
        for (const [lx, lz] of [[-6, -5], [6, 5], [0, 0]]) {
          const pl = new THREE.PointLight(0xbfd4ff, 30, 30, 2);
          pl.position.set(lx, 6.0, lz); g.add(pl);
        }
      }
      if (def.cage) {
        // Procedural steel-cage walls: the ROM's cage pieces are placement-less
        // templates (no arena-code positions yet), so the builder stands in
        // chain-link panels around the ring. Swapped for real geometry when the
        // arena-code RE lane lands.
        const linkTex = (() => {
          const c = document.createElement('canvas'); c.width = c.height = 128;
          const x = c.getContext('2d');
          x.clearRect(0, 0, 128, 128);
          x.strokeStyle = 'rgba(180,190,205,0.95)'; x.lineWidth = 3;
          for (let i = -128; i < 256; i += 16) {
            x.beginPath(); x.moveTo(i, 0); x.lineTo(i + 128, 128); x.stroke();
            x.beginPath(); x.moveTo(i + 128, 0); x.lineTo(i, 128); x.stroke();
          }
          const t = new THREE.CanvasTexture(c);
          t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(6, 6);
          return t;
        })();
        const wallMat = new THREE.MeshStandardMaterial({
          map: linkTex, transparent: true, side: THREE.DoubleSide,
          roughness: 0.4, metalness: 0.8, alphaTest: 0.25,
        });
        const C = 4.7, CH = 4.2; // half-width, height
        for (const [w, h, px, pz, ry] of [
          [C * 2, CH, 0, -C, 0], [C * 2, CH, 0, C, 0],
          [C * 2, CH, -C, 0, Math.PI / 2], [C * 2, CH, C, 0, Math.PI / 2]]) {
          const wall = new THREE.Mesh(new THREE.PlaneGeometry(w, h), wallMat);
          wall.position.set(px, CH / 2, pz); wall.rotation.y = ry;
          wall.castShadow = false; wall.receiveShadow = false; g.add(wall);
        }
        const frameMat = new THREE.MeshStandardMaterial({ color: 0x3a3d45, roughness: 0.5, metalness: 0.7 });
        const top = new THREE.Mesh(new THREE.BoxGeometry(C * 2 + 0.3, 0.18, C * 2 + 0.3), frameMat);
        top.position.y = CH + 0.09; g.add(top);
        // The cage assembly ships no center mat (its "Ring_Mat" label is a tiny
        // mislabeled quad; the true mat geometry isn't in the ROM dump), so the
        // builder lays a procedural mat. The ROM's dark apron ring surrounds it.
        const mat = new THREE.Mesh(
          new THREE.PlaneGeometry(7.3, 7.3),
          new THREE.MeshStandardMaterial({ color: 0x8a94a8, roughness: 0.95 })
        );
        mat.rotation.x = -Math.PI / 2; mat.position.y = 0.012;
        mat.receiveShadow = true; g.add(mat);
      }
      if (def.ropes) {
        // ring mat is ±3.64 m; posts just outside, ropes at 3 heights
        const postMat = new THREE.MeshStandardMaterial({ color: 0x2a2c34, roughness: 0.5, metalness: 0.7 });
        const ropeMat = new THREE.MeshStandardMaterial({ color: 0xd83a3a, roughness: 0.8 });
        const H = 3.95, heights = [0.55, 0.9, 1.25];
        for (const sx of [-1, 1]) for (const sz of [-1, 1]) {
          const post = new THREE.Mesh(new THREE.CylinderGeometry(0.07, 0.07, 1.5, 10), postMat);
          post.position.set(sx * H, 0.75, sz * H); post.castShadow = true; g.add(post);
        }
        for (const y of heights) {
          for (const [x1, z1, x2, z2] of [[-H, -H, H, -H], [H, -H, H, H], [H, H, -H, H], [-H, H, -H, -H]]) {
            const len = Math.hypot(x2 - x1, z2 - z1);
            const rope = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, len, 8), ropeMat);
            rope.position.set((x1 + x2) / 2, y, (z1 + z2) / 2);
            rope.rotation.z = Math.PI / 2; rope.rotation.y = -Math.atan2(z2 - z1, x2 - x1);
            g.add(rope);
          }
        }
      }
      // arena edge marker in the stage palette
      const edge = new THREE.Mesh(new THREE.TorusGeometry(def.dims.wallDistance, 0.07, 10, 48),
        new THREE.MeshBasicMaterial({ color: _hex(def.lighting.sun[0]) }));
      edge.rotation.x = Math.PI / 2; edge.position.y = 0.02; g.add(edge);
  } else if (def.obj) {
    /* WWF No Mercy arenas (teardown-integration 2026-10-19): real assembled
       arena geometry from teardown/wwf-no-mercy/arenas/ (AkiModel pieces grouped
       by assemble_arenas.py), vertex colors merged from the .vc sidecars into
       the OBJ v-lines (game/assets/stages/no-mercy/). AkiModel units: floor
       plane sits at y=0, bowl spans ~+-2700 -> scale 0.012 puts the ring at
       fight scale and the bowl walls ~32 units out. */
      try {
        const geo = await fetchStageOBJ(def.obj);
        geo.scale(0.012, 0.012, 0.012);
        const mat = new THREE.MeshBasicMaterial({
          vertexColors: !!geo.getAttribute('color'),
          color: _hex(def.panoTint),
          side: THREE.DoubleSide, fog: true,
        });
        const shell = new THREE.Mesh(geo, mat);
        g.add(shell);
      } catch (e) {
        console.warn(`[WH] stage ${def.id}: arena shell failed (${e.message}), palette backdrop only`);
      }
  }
  return { updaters, skyTex, fog };
}

const BUILDERS = {
  shrine: buildShrine, tongnou: buildTongNou, treelife: buildTreeLife,
  chiu: buildChiU, parfang: buildParFang, helix: buildHelix,
  dreaming: buildDreaming, marketplace: buildMarketplace, t3retro: buildT3Retro,
  sunra: buildSunRa, nomercy: buildNoMercy,
};

/* Build a stage into a fresh group. Returns { group, update, def, skyTex, fog }.
   update(dt, t, fighterA, fighterB) drives animated elements. */
export async function buildStage(def, api) {
  const g = new THREE.Group();
  g.name = `stage-${def.id}`;
  const builder = BUILDERS[def.builder] || buildShrine;
  const { updaters, skyTex, fog } = await builder(g, def, api);
  return {
    group: g, def, skyTex, fog,
    update(dt, t, fA, fB) { for (const u of updaters) u(dt, t, fA, fB); },
  };
}

/* Deep-dispose a stage group so switching stages doesn't leak GPU memory. */
export function disposeStage(group) {
  group.traverse((o) => {
    if (o.isMesh || o.isInstancedMesh) {
      if (o.geometry) o.geometry.dispose();
      const mats = Array.isArray(o.material) ? o.material : [o.material];
      for (const m of mats) {
        if (!m) continue;
        for (const k of ['map', 'emissiveMap', 'normalMap']) if (m[k]) m[k].dispose();
        m.dispose();
      }
    }
  });
}

/* Tier order for the stage-select screen. */
export const STAGE_TIERS = ['CANON LANDS', 'TEKKEN RETRO', 'WWF NO MERCY', 'WRESTLING', 'BOSS STAGES'];

/* ---------------- SUN RĀ — THE STARING SKY ----------------
   Boss stage. Kevin's home base (he takes Baek's roster slot; can fight
   anywhere, but THIS is home).

   RESEARCH (game/assets/stages/sunra/README.md):
   - GOD MOLECULE bible: four-land taxonomy — Life=Wood/organic-techno/growth,
     Time=Fire/driving-percussion/urgency, Desire=Metal/sharp-synthetic/appetite,
     Dreaming=Water/fluid-ambient/memory; Central Mountain = Kevin's trickster
     hub (barter-only, absurd exchange rates). Mars: cobalt/electric blue,
     glowing white eyes, forehead symbol = living portal/organ. Reality
     transitions = datamosh-style bridges + continuous music ("the cut carries
     the story").
   - TONG-NOU / EASTERN MIND: Osamu Sato surrealist fever-dream; living-island
     heads; reality-shift mechanics; death-as-transition.
   - MALAKOR (@obruxomalakor, TikTok): occult grimoire/mystery aesthetic —
     arcane sigils, ritual rings, infernal iconography ("AVEH Belzebub").
   - Planets: REAL relative diameters (NASA fact sheets, km): Mercury 4879,
     Venus 12104, Earth 12756, Mars 6792, Jupiter 142984, Saturn 120536,
     Uranus 51118, Neptune 49528, Pluto 2376 (owner: the 9th is Pluto).
     Textures: NASA/USGS public-domain cylindrical maps (sources in README).
   - Mars head: decimated Tripo pull (spiky_sun_creature_3d_model, 1M verts
     -> ~50k), full-res stays in tripo-downloads/.
   --------------------------------------------------------------- */

const SUNRA_PLANETS = [
  // name, diameterKm (NASA), texture, orbitRadius, periodSec, inclinationDeg, spinRate
  { name: 'mercury', d: 4879, tex: 'mercury.jpg', orbit: 11, period: 44, incl: 7.0, spin: 0.10 },
  { name: 'venus', d: 12104, tex: 'venus.jpg', orbit: 14, period: 58, incl: -4.0, spin: 0.05 },
  { name: 'earth', d: 12756, tex: 'earth.jpg', orbit: 17, period: 72, incl: 2.5, spin: 0.20 },
  { name: 'mars', d: 6792, tex: 'mars.jpg', orbit: 20, period: 86, incl: -6.5, spin: 0.19 },
  { name: 'jupiter', d: 142984, tex: 'jupiter.jpg', orbit: 25, period: 112, incl: 3.2, spin: 0.45 },
  { name: 'saturn', d: 120536, tex: 'saturn.jpg', orbit: 30, period: 132, incl: -8.0, spin: 0.42, ring: 'saturn_ring.jpg' },
  { name: 'uranus', d: 51118, tex: 'uranus.jpg', orbit: 34, period: 152, incl: 5.5, spin: 0.28 },
  { name: 'neptune', d: 49528, tex: 'neptune.jpg', orbit: 38, period: 172, incl: -3.0, spin: 0.27 },
  { name: 'pluto', d: 2376, tex: 'pluto.jpg', orbit: 42, period: 200, incl: 9.0, spin: 0.12 },
];
const SUNRA_JUPITER_R = 2.2; // game units; every other planet scales from real diameters

function _sunraZoneDisc() {
  // Fever-dream floor: four-land quadrant washes + Central Mountain hub + Malakor sigil rings.
  return _canvas(1024, (ctx, s) => {
    const c = s / 2;
    ctx.fillStyle = '#0a0a16'; ctx.fillRect(0, 0, s, s);
    for (let i = 0; i < 5000; i++) { // void grain
      const v = 8 + Math.random() * 22;
      ctx.fillStyle = `rgba(${v},${v},${v + 8},${Math.random() * 0.5})`;
      ctx.fillRect(Math.random() * s, Math.random() * s, 2, 2);
    }
    const quad = (x0, y0, col) => { // four-land washes: Life/Time/Desire/Dreaming
      const g = ctx.createRadialGradient(x0, y0, 40, x0, y0, 420);
      g.addColorStop(0, col); g.addColorStop(1, 'rgba(0,0,0,0)');
      ctx.fillStyle = g; ctx.fillRect(0, 0, s, s);
    };
    quad(c + 260, c - 260, 'rgba(40,140,70,0.20)');   // Life = Wood (NE)
    quad(c + 260, c + 260, 'rgba(200,60,30,0.20)');    // Time = Fire (SE)
    quad(c - 260, c + 260, 'rgba(130,60,200,0.20)');   // Desire = Metal (SW)
    quad(c - 260, c - 260, 'rgba(50,110,220,0.20)');   // Dreaming = Water (NW)
    // Central Mountain: Kevin's trickster hub — bronze disc, barter glyphs
    const hub = ctx.createRadialGradient(c, c, 20, c, c, 190);
    hub.addColorStop(0, '#3a2a14'); hub.addColorStop(0.8, '#241a0c'); hub.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = hub; ctx.beginPath(); ctx.arc(c, c, 190, 0, 7); ctx.fill();
    ctx.strokeStyle = 'rgba(220,170,90,0.75)'; ctx.lineWidth = 5;
    ctx.beginPath(); ctx.arc(c, c, 178, 0, 7); ctx.stroke();
    ctx.fillStyle = 'rgba(230,190,110,0.85)'; ctx.font = '44px serif'; ctx.textAlign = 'center';
    const glyphs = ['\u2715', '\u20bf', '\u2609', '\u263d', '\u2696', '\u2318', '\u2726', '\u2756'];
    for (let i = 0; i < 8; i++) {
      const a = (i / 8) * Math.PI * 2;
      ctx.fillText(glyphs[i], c + Math.cos(a) * 128, c + Math.sin(a) * 128 + 16);
    }
    // Malakor sigil rings: arcane runes circling the arena
    for (const [rr, alpha] of [[330, 0.55], [392, 0.35]]) {
      ctx.strokeStyle = `rgba(190,40,50,${alpha})`; ctx.lineWidth = 3;
      ctx.beginPath(); ctx.arc(c, c, rr, 0, 7); ctx.stroke();
      ctx.fillStyle = `rgba(220,80,90,${alpha})`; ctx.font = '30px serif';
      const runes = '\u16a0\u16a2\u16a6\u16a8\u16b1\u16b2\u16b7\u16b9\u16ba\u16be\u16c1\u16c3\u16c7\u16c8\u16c9\u16ca\u16cf\u16d2\u16d6\u16d7\u16da\u16dc\u16de\u16df';
      const n = 28;
      for (let i = 0; i < n; i++) {
        const a = (i / n) * Math.PI * 2;
        ctx.save(); ctx.translate(c + Math.cos(a) * rr, c + Math.sin(a) * rr);
        ctx.rotate(a + Math.PI / 2); ctx.fillText(runes[i % runes.length], 0, 10); ctx.restore();
      }
    }
  });
}

async function buildSunRa(g, def, api) {
  const { updaters, skyTex, fog } = buildBase(g, def, api);
  const texLoader = new THREE.TextureLoader();
  const sunraTex = (f) => {
    const t = texLoader.load('assets/stages/sunra/planets/' + f);
    t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 4;
    return t;
  };

  // ---- starfield shell ----
  {
    const N = api.isMobile ? 250 : 700;
    const pos = new Float32Array(N * 3);
    for (let i = 0; i < N; i++) {
      const r = 120 + Math.random() * 60, th = Math.random() * Math.PI * 2, ph = Math.acos(2 * Math.random() - 1);
      pos[i * 3] = r * Math.sin(ph) * Math.cos(th);
      pos[i * 3 + 1] = Math.abs(r * Math.cos(ph)) * 0.7 - 6;
      pos[i * 3 + 2] = r * Math.sin(ph) * Math.sin(th);
    }
    const sg = new THREE.BufferGeometry();
    sg.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    const stars = new THREE.Points(sg, new THREE.PointsMaterial({ color: 0xbfd0ff, size: 0.55, sizeAttenuation: true, fog: false }));
    stars.frustumCulled = false; g.add(stars);
  }

  // ---- Mars: the staring head (decimated Tripo GLB sky prop) ----
  const MARS_POS = new THREE.Vector3(0, 24, -46);
  let marsHead = null;
  const portal = new THREE.Mesh(new THREE.SphereGeometry(0.55, 16, 12),
    new THREE.MeshBasicMaterial({ color: 0xbfe8ff }));
  portal.position.set(0, 26.6, -40.6); g.add(portal);
  const portalLight = new THREE.PointLight(0x4a9aff, 60, 70, 2);
  portalLight.position.copy(portal.position); g.add(portalLight);
  // bleeding-eye glow: twin red points where the eyes stare (Sun Rā never blinks)
  const eyeGlowMat = new THREE.MeshBasicMaterial({ color: 0xff2a1a, transparent: true, opacity: 0.9 });
  const eyeL = new THREE.Mesh(new THREE.SphereGeometry(0.32, 12, 10), eyeGlowMat);
  const eyeR = eyeL.clone();
  eyeL.position.set(-1.7, 32, -40.9); eyeR.position.set(1.7, 32, -40.9); // owner 2026-10-19: raised 25% on Y
  g.add(eyeL, eyeR);
  const eyeLight = new THREE.PointLight(0xff3a22, 25, 40, 2);
  eyeLight.position.set(0, 31.75, -40.4); // owner 2026-10-19: raised 25% on Y with the glow g.add(eyeLight);
  try {
    const gltf = await new GLTFLoader().loadAsync('assets/stages/sunra/mars-sky.glb');
    marsHead = gltf.scene;
    // normalize: fit head height to ~11 units, center it on MARS_POS
    const bbox = new THREE.Box3().setFromObject(marsHead);
    const size = bbox.getSize(new THREE.Vector3());
    const k = 11 / Math.max(size.x, size.y, size.z);
    marsHead.scale.setScalar(k);
    const c = bbox.getCenter(new THREE.Vector3());
    marsHead.position.set(MARS_POS.x - c.x * k, MARS_POS.y - c.y * k, MARS_POS.z - c.z * k);
    marsHead.traverse((o) => { if (o.isMesh) { o.material.side = THREE.DoubleSide; } });
    marsHead.rotation.y = -Math.PI / 2; // face the arena (+z); the slow spin continues from here
    g.add(marsHead);
  } catch (e) {
    console.warn(`[WH] stage sunra: mars-sky.glb failed (${e.message}) — portal + planets carry the sky`);
  }

  // ---- 9 planets: real relative diameters, inclined orbits around Mars ----
  const planets = [];
  const kR = SUNRA_JUPITER_R / (142984 / 2); // game units per km of radius
  for (const p of SUNRA_PLANETS) {
    const r = Math.max((p.d / 2) * kR, 0.03);
    const pivot = new THREE.Group();
    pivot.position.copy(MARS_POS);
    pivot.rotation.x = p.incl * Math.PI / 180;
    const mesh = new THREE.Mesh(
      new THREE.SphereGeometry(r, api.isMobile ? 16 : 28, api.isMobile ? 12 : 20),
      new THREE.MeshStandardMaterial({ map: sunraTex(p.tex), roughness: 0.95, metalness: 0.02 })
    );
    if (p.ring) { // Saturn's ring
      const ringTex = sunraTex(p.ring);
      const ring = new THREE.Mesh(
        new THREE.RingGeometry(r * 1.3, r * 2.3, 48),
        new THREE.MeshBasicMaterial({ map: ringTex, transparent: true, side: THREE.DoubleSide, opacity: 0.9 })
      );
      ring.rotation.x = -Math.PI / 2 + 0.35;
      mesh.add(ring);
    }
    pivot.add(mesh); g.add(pivot);
    planets.push({ p, pivot, mesh, angle: Math.random() * Math.PI * 2 });
  }

  // ---- fever-dream floor disc: four lands + Central Mountain + Malakor rings ----
  // (shared shift-state S is declared with the reality-shift updater below)
  let S = null;
  {
    const discTex = _sunraZoneDisc();
    discTex.colorSpace = THREE.SRGBColorSpace; discTex.anisotropy = 4;
    discTex.wrapS = discTex.wrapT = THREE.RepeatWrapping;
    const disc = new THREE.Mesh(
      new THREE.CircleGeometry(9.18, 48),
      new THREE.MeshStandardMaterial({ map: discTex, roughness: 0.85, metalness: 0.1, transparent: true, opacity: 0.96 })
    );
    disc.rotation.x = -Math.PI / 2; disc.position.y = 0.012;
    g.add(disc);
    updaters.push((dt) => { if (S && S.shiftT >= 0) discTex.offset.x += dt * 2.5; });
  }

  // ---- zone totems: wizards / thugs / goblins / knights ----
  const totemDefs = [
    { name: 'wizards', land: 'Life - Wood', color: 0x3ae06a, pos: [-11.5, 0, -3.5], geo: () => new THREE.OctahedronGeometry(1.5) },
    { name: 'thugs', land: 'Time - Fire', color: 0xff4a22, pos: [11.5, 0, -3.5], geo: () => new THREE.BoxGeometry(1.8, 3.2, 1.8) },
    { name: 'goblins', land: 'Desire - Metal', color: 0xa04aff, pos: [-11.5, 0, 4.5], geo: () => new THREE.ConeGeometry(1.3, 3.4, 7) },
    { name: 'knights', land: 'Dreaming - Water', color: 0x4aa8ff, pos: [11.5, 0, 4.5], geo: () => new THREE.BoxGeometry(0.7, 4.2, 1.4) },
  ];
  const totems = [];
  for (const td of totemDefs) {
    const grp = new THREE.Group(); grp.position.set(td.pos[0], 0, td.pos[2]);
    const base = new THREE.Mesh(new THREE.CylinderGeometry(1.1, 1.4, 0.5, 8),
      new THREE.MeshStandardMaterial({ color: 0x1a1a26, roughness: 0.9 }));
    base.position.y = 0.25; grp.add(base);
    const crystal = new THREE.Mesh(td.geo(),
      new THREE.MeshStandardMaterial({ color: td.color, emissive: td.color, emissiveIntensity: 0.55, roughness: 0.35 }));
    crystal.position.y = 2.4; grp.add(crystal);
    const halo = new THREE.Mesh(new THREE.TorusGeometry(2.2, 0.06, 8, 40),
      new THREE.MeshBasicMaterial({ color: td.color, transparent: true, opacity: 0.6 }));
    halo.position.y = 2.4; halo.rotation.x = Math.PI / 2.4; grp.add(halo);
    g.add(grp);
    totems.push({ grp, crystal, halo, ph: Math.random() * 10, color: td.color });
  }

  // ---- T3 panorama shell: real teardown geometry as the distant fever-dream ridge ----
  try {
    const geo = await fetchStageOBJ('assets/stages/t3/stg_n_panorama.obj');
    geo.scale(0.02, 0.02, 0.02);
    let mat = null;
    try {
      const tex = await new THREE.TextureLoader().loadAsync('assets/stages/t3/stg_n_atlas.png');
      tex.colorSpace = THREE.SRGBColorSpace;
      mat = new THREE.MeshBasicMaterial({ map: tex, vertexColors: !!geo.getAttribute('color'), side: THREE.DoubleSide, fog: true, color: 0x8a7ab8 });
    } catch (e) { mat = new THREE.MeshBasicMaterial({ color: 0x2a1a4a, side: THREE.DoubleSide, fog: true }); }
    const shell = new THREE.Mesh(geo, mat);
    shell.position.y = 7; shell.rotation.y = Math.PI;
    g.add(shell);
  } catch (e) {
    console.warn(`[WH] stage sunra: T3 shell failed (${e.message}) — sky gradient carries the backdrop`);
  }

  // ---- datamosh reality-shift: glitch slices + planet smear + portal shockwave ----
  const slices = [];
  {
    const sliceGeo = new THREE.PlaneGeometry(60, 1);
    for (let i = 0; i < 14; i++) {
      const m = new THREE.Mesh(sliceGeo, new THREE.MeshBasicMaterial({
        color: new THREE.Color().setHSL(Math.random(), 0.9, 0.55),
        transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false, fog: false,
      }));
      m.position.set((Math.random() - 0.5) * 40, 4 + Math.random() * 26, -30 - Math.random() * 25);
      m.scale.y = 0.4 + Math.random() * 2.2;
      g.add(m); slices.push(m);
    }
  }
  const shock = new THREE.Mesh(new THREE.TorusGeometry(1, 0.18, 10, 48),
    new THREE.MeshBasicMaterial({ color: 0x9ad0ff, transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false, fog: false }));
  shock.position.copy(portal.position); g.add(shock);

  S = { shiftT: -1, prePulse: -1, nextShift: 24 };
  // debug hook (used by the stage-test harness to force a shift on demand)
  g.userData.sunraDebug = { forceShift: () => { if (S.shiftT < 0) S.prePulse = 0; } };
  updaters.push((dt, t) => {
    // planets: inclined orbits, real relative sizes, visual-period motion + spin
    for (const pl of planets) {
      pl.angle += dt * (Math.PI * 2 / pl.p.period);
      pl.mesh.position.set(Math.cos(pl.angle) * pl.p.orbit, 0, Math.sin(pl.angle) * pl.p.orbit);
      pl.mesh.rotation.y += dt * pl.p.spin;
      if (S.shiftT >= 0) { // datamosh smear: jitter positions during the shift
        pl.mesh.position.x += (Math.random() - 0.5) * 1.6;
        pl.mesh.position.z += (Math.random() - 0.5) * 1.6;
      }
    }
    if (marsHead) { marsHead.rotation.y += dt * 0.08; marsHead.position.y = MARS_POS.y + Math.sin(t * 0.35) * 0.7; }
    // Mars stares: eye glow breathes, never blinks
    const stare = 0.7 + Math.sin(t * 0.9) * 0.3;
    eyeGlowMat.opacity = 0.55 + stare * 0.4;
    eyeLight.intensity = 18 + stare * 14;
    // totems drift
    for (const tm of totems) {
      tm.crystal.rotation.y += dt * 0.5;
      tm.crystal.position.y = 2.4 + Math.sin(t * 0.8 + tm.ph) * 0.25;
      tm.halo.rotation.z += dt * 0.7;
    }
    portal.rotation.y += dt * 1.2;
    // reality-shift state machine: organ pre-pulse -> datamosh bridge
    if (S.shiftT < 0 && S.prePulse < 0 && t > S.nextShift - 1.2) S.prePulse = 0;
    if (S.prePulse >= 0) { // the forehead organ reacts before transit (Tong-Nou)
      S.prePulse += dt;
      const k = Math.min(S.prePulse / 1.2, 1);
      portal.scale.setScalar(1 + k * 0.8);
      portalLight.intensity = 60 + k * 90;
      if (S.prePulse >= 1.2) { S.prePulse = -1; S.shiftT = 0; S.nextShift = t + 24 + Math.random() * 8; }
    }
    if (S.shiftT >= 0) {
      S.shiftT += dt;
      const k = S.shiftT / 1.4;
      for (const s of slices) {
        s.material.opacity = 0.5 * (1 - k);
        s.position.x += (Math.random() - 0.5) * 6;
      }
      shock.material.opacity = 0.8 * (1 - k);
      shock.scale.setScalar(1 + k * 22);
      if (S.shiftT >= 1.4) {
        S.shiftT = -1;
        for (const s of slices) s.material.opacity = 0;
        shock.material.opacity = 0; shock.scale.setScalar(1);
        portal.scale.setScalar(1); portalLight.intensity = 60;
      }
    }
  });
  return { updaters, skyTex, fog };
}
