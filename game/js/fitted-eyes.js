/* fitted-eyes.js — template-FITTED left / right eyeballs (creation suite EYES phase, 2026-11-02).

   Options follow the WWE 2K Create-A-Superstar Face > Eyes window (customization/wwe2k-caw/CAW-SUITE-BREAKDOWN.md
   "Eyes (color, shape)": eye type, iris colour, sclera tint, pupil size; eye SHAPE / position stays on the face
   sliders, f_eye_*), filed on the Tekken 7 EYES slot (teardown/tekken7-steam-ui/T7-UI-LAYOUT.md).

   Geometry: customization/parts/eyes/eyeball.glb (EyeballSclera / EyeballIris / EyeballPupil, radius 0.012, gaze
   +Z). Placement: customization/parts/eyes/eye-sockets.json, MEASURED per template by tools/eyes/build_eye_sockets.mjs
   from each template body's own eyeball geometry and baked eye-slider morph targets, in HEAD-BONE-LOCAL space.
   One eyeball clone per side is parented to the Head bone at that socket (so it follows every head animation),
   scaled to the socket radius and turned to the socket's gaze axis; the body's own eye primitives (sclera / iris /
   pupil / cornea) are hidden under it. Eye-region sliders (size / spacing / height) move and scale the sockets
   linearly from the measured deltas.

   Shared by the suite preview (customization/creation-suite-ui/js/viewer3d.js) and the game (game/js/fighter.js,
   created fighters on custom-template-<id>). Pure helpers first (node-testable), then plain Object3D helpers
   (no WebGL draw). Player-facing names are generic (names law). */

import { FITTED_TEMPLATES, FITTED_HIDES, findHeadBone } from './fitted-parts.js';

export const EYE_SLOT = 'EYES';                       // attire.equipped key (Tekken 7 EYES slot)
export const EYEBALL_GLB = 'customization/parts/eyes/eyeball.glb';
export const EYE_SOCKETS_JSON = 'customization/parts/eyes/eye-sockets.json';
export const EYEBALL_RADIUS = 0.012;                  // eyeball.glb sclera radius
export const IRIS_RADIUS = 0.0055;                    // eyeball.glb iris disc radius (planar UV for lens textures)
/* eyeball.glb authors the iris disc at z 0.0113 and the pupil at 0.0119, both INSIDE the sclera sphere's front cap
   (radius 0.012): the opaque sclera then shows through the middle of the iris as a white ring + dot (seen in the
   EYES proof render, tools/eyes/proof/). Lift both discs just past the cap (a 0.2-0.4 mm corneal bulge). */
export const IRIS_LIFT = 0.0009, PUPIL_LIFT = 0.0005;

/* Eye types (catalog entries, suite_slot 'eye', fitted_eyes). lens = iris texture from the eye library (repo path). */
export const EYE_TYPES = {
  'wh-eye-natural': { name: 'Natural Eyes', lens: null },
  'wh-eye-lens-gold': { name: 'Gold Iris', lens: 'customization/eye-library/eye-classic-original.png' },
  'wh-eye-lens-ice': { name: 'Ice Blue Iris', lens: 'customization/eye-library/eye-blue-snow-leopard.png' },
  'wh-eye-lens-amber': { name: 'Amber Striated Iris', lens: 'customization/eye-library/eye-yellow-tiger.png' },
};
export const DEFAULT_EYE = 'wh-eye-natural';

/* swatch rows the suite shows (WWE 2K Eyes > Color). hex strings; first = default */
export const IRIS_COLORS = ['#3b2414', '#5a3a22', '#8a5a32', '#b07a2a', '#6b7a3a', '#3f6e4a', '#2f5d8a', '#6f8fb0',
  '#7d8a91', '#3a3a3a', '#8a2a2a', '#c9a227'];
export const SCLERA_TINTS = ['#f5f2ec', '#ffffff', '#efe6d2', '#f0d8d0', '#e8c0b8', '#1a1a1a'];
export const PUPIL_SIZES = [0.6, 0.8, 1.0, 1.2, 1.4];
export const PUPIL_MIN = 0.4, PUPIL_MAX = 1.6;
export const EYE_HIDES = FITTED_HIDES.eyes; // the template body's own eye primitives (MB-Lab materials)

export const isEyeType = id => Object.prototype.hasOwnProperty.call(EYE_TYPES, id);
const HEX = /^#[0-9a-f]{6}$/i;
export const clampPupil = v => { const n = Number(v); return Number.isFinite(n) && n > 0 ? Math.max(PUPIL_MIN, Math.min(PUPIL_MAX, n)) : 1; };

/** From a saved attire pick the fitted-eye setup for `templateId`, or null (off-template / nothing chosen).
    Saved shape (per attire): equipped.EYES = eye type id; colors.iris, colors.sclera = hex; eyes.pupil = scale.
    An attire that only set an eye colour / pupil still gets the default eye type. */
export function selectEyes(attire, templateId) {
  if (!attire || !FITTED_TEMPLATES.includes(templateId)) return null;
  const eq = attire.equipped || {}, col = attire.colors || {}, ex = attire.eyes || {};
  let id = Object.values(eq).find(isEyeType) || null;
  const touched = HEX.test(col.iris || '') || HEX.test(col.sclera || '') || ex.pupil != null;
  if (!id && !touched) return null;
  id = id || DEFAULT_EYE;
  return {
    id, lens: EYE_TYPES[id].lens,
    iris: HEX.test(col.iris || '') ? col.iris : (EYE_TYPES[id].lens ? null : IRIS_COLORS[0]),
    sclera: HEX.test(col.sclera || '') ? col.sclera : null,
    pupil: clampPupil(ex.pupil),
    template: templateId,
  };
}

/** Socket pose for one side under the face-slider values ({ f_eye_size: -1..1, ... }).
    Returns { center:[x,y,z], radius, forward:[x,y,z] } in head-bone-local metres. */
export function eyeSocketPose(templateSockets, side, morphValues = {}) {
  const s = templateSockets && templateSockets[side];
  if (!s) return null;
  const c = s.center.slice(); let r = s.radius;
  for (const [id, raw] of Object.entries(morphValues || {})) {
    const v = Math.max(-1, Math.min(1, Number(raw) || 0));
    if (!v) continue;
    const d = s.sliders[id + (v > 0 ? '+' : '-')];
    if (!d) continue;
    const w = Math.abs(v);
    c[0] += d.dc[0] * w; c[1] += d.dc[1] * w; c[2] += d.dc[2] * w; r += d.dr * w;
  }
  return { center: c, radius: r, forward: s.forward.slice() };
}

/* ---------- three.js helpers (plain Object3D APIs, no draw) ---------- */

function setSidePose(g, pose) {
  g.position.set(pose.center[0], pose.center[1], pose.center[2]);
  g.scale.setScalar(pose.radius / EYEBALL_RADIUS);
  // turn eyeball +Z (its iris axis) onto the socket's measured gaze axis
  const f = pose.forward, len = Math.hypot(f[0], f[1], f[2]) || 1;
  const fx = f[0] / len, fy = f[1] / len, fz = f[2] / len;
  // shortest-arc quaternion from (0,0,1) to f
  const w = 1 + fz;
  if (w < 1e-6) g.quaternion.set(0, 1, 0, 0);
  else { const n = Math.hypot(-fy, fx, 0, w); g.quaternion.set(-fy / n, fx / n, 0, w / n); }
}

function partMeshes(g) {
  const m = {};
  g.traverse((o) => {
    if (!o.isMesh) return;
    const n = (o.name || '') + ' ' + ((o.material && o.material.name) || '');
    if (/pupil/i.test(n)) m.pupil = o; else if (/iris/i.test(n)) m.iris = o; else if (/sclera/i.test(n)) m.sclera = o;
  });
  return m;
}

/** Apply colour / pupil / lens to one attached eyeball. makeTexture(url) -> THREE.Texture (optional; skipped in Node). */
export function styleEye(g, cfg, { makeTexture, urlPrefix = '' } = {}) {
  const m = partMeshes(g);
  if (m.sclera && m.sclera.material && cfg.sclera) m.sclera.material.color.set(cfg.sclera);
  if (m.pupil) m.pupil.scale.set(cfg.pupil, cfg.pupil, 1);
  if (m.iris && m.iris.material) {
    const mat = m.iris.material;
    if (cfg.lens && makeTexture) {
      ensureIrisUV(m.iris.geometry);
      const tex = makeTexture(urlPrefix + cfg.lens);
      if (tex) { mat.map = tex; mat.color.set(cfg.iris || '#ffffff'); mat.needsUpdate = true; }
    } else {
      if (mat.map) { mat.map = null; mat.needsUpdate = true; }
      if (cfg.iris) mat.color.set(cfg.iris);
    }
  }
  g.userData.whFitted.style = { id: cfg.id, iris: cfg.iris, sclera: cfg.sclera, pupil: cfg.pupil, lens: cfg.lens };
}

/* the iris disc ships without UVs: planar-map it so a full-frame eye-library iris texture fills the disc */
export function ensureIrisUV(geom) {
  if (!geom || geom.attributes.uv) return;
  const pos = geom.attributes.position, uv = new Float32Array(pos.count * 2);
  for (let i = 0; i < pos.count; i++) {
    uv[i * 2] = pos.getX(i) / (2 * IRIS_RADIUS) + 0.5;
    uv[i * 2 + 1] = pos.getY(i) / (2 * IRIS_RADIUS) + 0.5;
  }
  if (pos.isInterleavedBufferAttribute) return; // eyeball.glb positions are plain float accessors
  geom.setAttribute('uv', new pos.constructor(uv, 2));
}

function hideBaseEyes(root, hidden) {
  let n = 0;
  root.traverse((o) => {
    if (!o.isMesh) return;
    for (let a = o; a; a = a.parent) if (a.userData && a.userData.whFitted) return;
    const mats = Array.isArray(o.material) ? o.material : [o.material];
    if (mats.some(m => m && EYE_HIDES.test(m.name || ''))) { o.visible = !hidden; n++; }
  });
  return n;
}

/** Remove fitted eyes from a model and show its own eyes again. */
export function clearEyes(root) {
  if (!root) return 0;
  const found = [];
  root.traverse((o) => { if (o.userData && o.userData.whFitted && o.userData.whFitted.slot === 'eyes') found.push(o); });
  for (const g of found) if (g.parent) g.parent.remove(g);
  if (found.length) hideBaseEyes(root, false);
  return found.length;
}

/** Attach both eyes. eyeballScene = loaded eyeball.glb scene (cloned per side, materials cloned).
    sockets = eye-sockets.json; cfg = selectEyes(...). Returns [left, right] groups (or [] when it cannot). */
export function attachEyes(root, eyeballScene, sockets, cfg, { morphValues = {}, makeTexture, urlPrefix = '' } = {}) {
  const head = findHeadBone(root);
  const ts = sockets && sockets.templates && cfg && sockets.templates[cfg.template];
  if (!head || !ts || !eyeballScene) return [];
  clearEyes(root);
  const out = [];
  for (const side of ['left', 'right']) {
    const g = eyeballScene.clone(true);
    g.name = 'fitted-eye:' + side;
    g.traverse((o) => {
      if (!o.isMesh) return;
      o.frustumCulled = false; o.castShadow = false;
      if (o.material) o.material = o.material.clone();
      if (o.geometry) o.geometry = o.geometry.clone();
    });
    const pm = partMeshes(g);
    if (pm.iris) pm.iris.position.z += IRIS_LIFT;
    if (pm.pupil) pm.pupil.position.z += PUPIL_LIFT;
    g.userData.whFitted = { partId: cfg.id, slot: 'eyes', side, template: cfg.template };
    setSidePose(g, eyeSocketPose(ts, side, morphValues));
    styleEye(g, cfg, { makeTexture, urlPrefix });
    head.add(g);
    out.push(g);
  }
  hideBaseEyes(root, true);
  return out;
}

/** Re-place attached eyes after face sliders change (suite live sliders / game load-time morphs). */
export function updateEyeSockets(root, sockets, morphValues = {}) {
  let n = 0;
  if (!root || !sockets) return 0;
  root.traverse((o) => {
    const f = o.userData && o.userData.whFitted;
    if (!f || f.slot !== 'eyes') return;
    const ts = sockets.templates[f.template];
    if (!ts) return;
    setSidePose(o, eyeSocketPose(ts, f.side, morphValues)); n++;
  });
  return n;
}

/** Restyle attached eyes in place (colour / pupil swatch taps) without reloading. */
export function restyleEyes(root, cfg, opts = {}) {
  let n = 0;
  if (!root || !cfg) return 0;
  root.traverse((o) => { const f = o.userData && o.userData.whFitted; if (f && f.slot === 'eyes') { f.partId = cfg.id; styleEye(o, cfg, opts); n++; } });
  return n;
}
