/* morph-targets.js — REAL body + face morphing for the Creation Suite.

   The template bodies (customization/templates/meshes/*.glb) carry glTF morph
   targets baked from MB-Lab's morph database by
   tools/mb-lab/bake_morph_templates.py: every slider in
   customization/templates/morph-sliders.json has a '<id>+' target (slider at +1)
   and a '<id>-' target (slider at -1), as deltas from the template's own shape.
   This module turns slider values (-1..1, 0 = template) into
   mesh.morphTargetInfluences on every mesh of the loaded model that carries
   those targets, so the GPU reshapes the actual skinned mesh live.

   Pure helpers (no three.js import) so node tests can drive them with plain
   objects shaped like three.js meshes ({ morphTargetDictionary,
   morphTargetInfluences }).

   Window / group structure: WWE 2K22 Create-A-Superstar APPEARANCE ->
   Body (Body Morphing per region) and Face (Face Deformation per facial part),
   regions from the WrestleMania XIX CAW FIGURE editor; sources are listed in
   morph-sliders.json "sources". */

export const SLIDER_MIN = -1;
export const SLIDER_MAX = 1;

/** Flatten the catalog into [{ id, label, label_female, window, group, groupLabel, windowLabel }] */
export function flattenCatalog(cat) {
  const out = [];
  for (const w of (cat && cat.windows) || []) {
    for (const g of w.groups || []) {
      for (const s of g.sliders || []) {
        out.push({ ...s, window: w.key, windowLabel: w.label, group: g.key, groupLabel: g.label });
      }
    }
  }
  return out;
}

/** Every mesh in `root` (three.js Object3D or a plain array of mesh-likes) that has morph targets. */
export function morphMeshes(root) {
  const list = [];
  const visit = (o) => { if (o && o.morphTargetDictionary && o.morphTargetInfluences) list.push(o); };
  if (Array.isArray(root)) root.forEach(visit);
  else if (root && typeof root.traverse === 'function') root.traverse(visit);
  return list;
}

/** Slider ids that are fully wired on this model: both '+' and '-' targets exist on at least one mesh. */
export function wiredSliderIds(root, sliders) {
  const meshes = morphMeshes(root);
  const ok = new Set();
  for (const s of sliders) {
    if (meshes.some(m => (s.id + '+') in m.morphTargetDictionary && (s.id + '-') in m.morphTargetDictionary)) ok.add(s.id);
  }
  return ok;
}

export const clampSlider = v => Math.max(SLIDER_MIN, Math.min(SLIDER_MAX, Number(v) || 0));

/** Write influences for `values` ({ sliderId: -1..1 }) onto every morph mesh in `root`.
    Targets of sliders not in `values` go back to 0 (the template shape).
    Returns the number of influences set non-zero (for probes / tests). */
export function applyMorphTargets(root, values) {
  const meshes = morphMeshes(root);
  let live = 0;
  for (const m of meshes) {
    const inf = m.morphTargetInfluences;
    // only the baked slider targets ('<id>+' / '<id>-'); body.js 'cs_*' proxies and any other targets are left alone
    for (const [name, i] of Object.entries(m.morphTargetDictionary)) if (/[+-]$/.test(name)) inf[i] = 0;
    for (const [id, raw] of Object.entries(values || {})) {
      const v = clampSlider(raw);
      if (!v) continue;
      const idx = m.morphTargetDictionary[id + (v > 0 ? '+' : '-')];
      if (idx === undefined) continue;
      inf[idx] = Math.abs(v);
      live++;
    }
  }
  return live;
}

/** Drop zero / unknown entries so saved records stay small and only carry real sliders. */
export function cleanValues(values, sliders) {
  const known = new Set((sliders || []).map(s => s.id));
  const out = {};
  for (const [id, raw] of Object.entries(values || {})) {
    if (sliders && !known.has(id)) continue;
    const v = Math.round(clampSlider(raw) * 100) / 100;
    if (v) out[id] = v;
  }
  return out;
}

/** WWE-style display value: -100..+100 */
export const displayValue = v => Math.round(clampSlider(v) * 100);

let _catalog = null;
/** Load customization/templates/morph-sliders.json relative to the suite page. */
export async function loadMorphCatalog(url = '../templates/morph-sliders.json') {
  if (_catalog) return _catalog;
  const r = await fetch(url);
  if (!r.ok) throw new Error('morph-sliders.json ' + r.status);
  _catalog = await r.json();
  return _catalog;
}
