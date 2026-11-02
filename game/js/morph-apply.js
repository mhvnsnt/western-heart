/* morph-apply.js — apply Creation Suite morph slider values to a built
   in-game model (Phase 3 completion, 2026-11-02).

   The suite's template bodies (customization/templates/meshes/*.glb) carry
   glTF morph targets baked from MB-Lab: every slider in
   customization/templates/morph-sliders.json has a '<id>+' target (slider
   at +1) and a '<id>-' target (slider at -1). The suite preview applies
   saved values with customization/creation-suite-ui/js/morph-targets.js;
   this module is the game-side twin (the game module graph does not import
   the suite UI folder) with the identical convention, so a value saved as
   body.morph_targets means the same thing on both sides of the game.

   Pure helpers (no three.js import) so node tests can drive them with
   plain objects shaped like three.js meshes ({ morphTargetDictionary,
   morphTargetInfluences }). */

export const MORPH_MIN = -1;
export const MORPH_MAX = 1;

export const clampMorph = v => Math.max(MORPH_MIN, Math.min(MORPH_MAX, Number(v) || 0));

/** Every mesh in `root` (three.js Object3D or a plain array) that has morph targets. */
export function morphMeshes(root) {
  const list = [];
  const visit = (o) => { if (o && o.morphTargetDictionary && o.morphTargetInfluences) list.push(o); };
  if (Array.isArray(root)) root.forEach(visit);
  else if (root && typeof root.traverse === 'function') root.traverse(visit);
  return list;
}

/** Write influences for `values` ({ sliderId: -1..1 }) onto every morph mesh
    in `root`. Targets of sliders not in `values` return to 0 (template
    shape). Models without morph targets are a no-op.
    Returns the number of influences set non-zero. */
export function applyMorphTargets(root, values) {
  const meshes = morphMeshes(root);
  let live = 0;
  for (const m of meshes) {
    const inf = m.morphTargetInfluences;
    // only the baked slider targets ('<id>+' / '<id>-'); any other targets are left alone
    for (const [name, i] of Object.entries(m.morphTargetDictionary)) if (/[+-]$/.test(name)) inf[i] = 0;
    for (const [id, raw] of Object.entries(values || {})) {
      const v = clampMorph(raw);
      if (!v) continue;
      const idx = m.morphTargetDictionary[id + (v > 0 ? '+' : '-')];
      if (idx === undefined) continue;
      inf[idx] = Math.abs(v);
      live++;
    }
  }
  return live;
}
