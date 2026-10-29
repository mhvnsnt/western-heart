// t7material.js — Tekken 7 customize materials on three.js (creation suite).
//
// T7 T_CH_*_D albedos are near-greyscale; the _M mask carries the colour layers
// (R = base, G = sub, B = trim; black = keep albedo). The game tints each layer
// with a swatch from the 144-colour customize palette (palette.json from tkdata).
// A part's `materials` list (private catalog, built from the MI_CH_* material
// instances) gives per-section textures + default layer colours:
//   { slot, mi, D, N, M, colors: { base:[r,g,b], sub:[..], trim:[..] } }
// Generic code only — textures load from the private asset path.
import * as THREE from 'three';
import { T7_COLOR_LAYERS } from './t7layout.js';

export const LAYER_CHANNEL = { base: 'r', sub: 'g', trim: 'b' };

export function hexToRgb(hex) {
  const n = parseInt(String(hex).replace('#', ''), 16);
  return [((n >> 16) & 255) / 255, ((n >> 8) & 255) / 255, (n & 255) / 255];
}

/** Nearest palette index for an RGB colour (0..1). */
export function nearestSwatch(palette, rgb) {
  let best = 0, bd = Infinity;
  palette.forEach((h, i) => {
    const c = hexToRgb(h);
    const d = (c[0] - rgb[0]) ** 2 + (c[1] - rgb[1]) ** 2 + (c[2] - rgb[2]) ** 2;
    if (d < bd) { bd = d; best = i; }
  });
  return best;
}

const texCache = new Map();
function loadTex(url, srgb) {
  if (!url) return null;
  const key = url + (srgb ? '|s' : '');
  if (!texCache.has(key)) {
    const t = new THREE.TextureLoader().load(url);
    t.flipY = false;
    t.colorSpace = srgb ? THREE.SRGBColorSpace : THREE.NoColorSpace;
    t.wrapS = t.wrapT = THREE.RepeatWrapping;
    texCache.set(key, t);
  }
  return texCache.get(key);
}

/** Layered T7 material; exposes setLayerColor(layer, rgb). */
export function makeT7Material(def, base = '') {
  const mat = new THREE.MeshStandardMaterial({ roughness: 0.7, metalness: 0, side: THREE.DoubleSide });
  mat.name = def.mi || 'T7';
  const D = loadTex(def.D && base + def.D, true);
  const N = loadTex(def.N && base + def.N, false);
  const M = loadTex(def.M && base + def.M, false);
  if (D) mat.map = D;
  if (N) mat.normalMap = N;
  const c = (k) => new THREE.Color(...((def.colors && def.colors[k]) || [1, 1, 1]));
  const u = {
    t7Mask: { value: M }, t7Base: { value: c('base') }, t7Sub: { value: c('sub') },
    t7Trim: { value: c('trim') }, t7HasMask: { value: M ? 1 : 0 },
  };
  mat.userData.t7 = u;
  mat.onBeforeCompile = (sh) => {
    Object.assign(sh.uniforms, u);
    sh.fragmentShader = sh.fragmentShader
      .replace('#include <common>', `#include <common>
uniform sampler2D t7Mask; uniform vec3 t7Base, t7Sub, t7Trim; uniform float t7HasMask;`)
      .replace('#include <map_fragment>', `#include <map_fragment>
#ifdef USE_MAP
{
  vec3 m = t7HasMask > 0.5 ? texture2D(t7Mask, vMapUv).rgb : vec3(0.0);
  float rest = clamp(1.0 - m.r - m.g - m.b, 0.0, 1.0);
  diffuseColor.rgb *= t7Base * m.r + t7Sub * m.g + t7Trim * m.b + vec3(rest);
}
#endif`);
  };
  mat.customProgramCacheKey = () => 't7layer' + (M ? 'M' : '') + (N ? 'N' : '');
  mat.setLayerColor = (layer, rgb) => {
    const k = { base: 't7Base', sub: 't7Sub', trim: 't7Trim' }[layer];
    if (k) u[k].value.setRGB(...rgb);
  };
  return mat;
}

/** Apply catalog `materials` to a loaded part: glTF material i = UE material slot i. */
export function applyT7Materials(root, materials, base = '') {
  if (!materials || !materials.length) return [];
  const made = materials.map((d) => makeT7Material(d, base));
  root.traverse((o) => {
    if (!o.isMesh) return;
    const pick = (m) => {
      const i = Number(String((m && m.name) || '').match(/(\d+)(\.\d+)?$/)?.[1]);
      return Number.isFinite(i) && made[i] ? made[i] : m;
    };
    o.material = Array.isArray(o.material) ? o.material.map(pick) : pick(o.material);
  });
  return made;
}

/** Recolour one T7 layer on every T7 material under root. */
export function setT7LayerColor(root, layer, rgb) {
  if (!T7_COLOR_LAYERS.includes(layer)) throw new Error(`unknown T7 layer ${layer}`);
  root.traverse((o) => {
    if (!o.isMesh) return;
    for (const m of [].concat(o.material)) if (m && m.setLayerColor) m.setLayerColor(layer, rgb);
  });
}
