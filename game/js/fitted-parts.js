/* fitted-parts.js — template-FITTED hair / facial hair / eyebrows / eyelashes (creation suite HAIR phase, 2026-11-02).

   The parts are MakeHuman / MPFB2 CC0 system assets (hair, eyebrows, eyelashes) and CC0 beard shells cut from the
   MakeHuman base mesh, fitted offline onto each of the 9 creation-suite template bodies
   (tools/mpfb2/hair/fit_proxies.py + build_glb.mjs). Each fit is one GLB per template:
     customization/parts/hair/mpfb2/<part-id>/<template-id>.glb   (+ a shared texture.png beside it)
   Geometry is authored in HEAD-BONE-LOCAL space (inverse head-joint bind matrix), so the part is parented to the
   head bone with an identity transform: it follows every head animation exactly (rigid head weight), and its morph
   targets carry the template's own face/head slider names, so face morphs move brows / lashes / beards / hairline
   when the same slider values are applied to the model.

   Used by both the suite preview (customization/creation-suite-ui/js/viewer3d.js) and the fight/select model
   (game/js/fighter.js, created fighters on custom-template-<id>). Pure helpers first (node-testable), then the
   three.js attach helpers, which only touch plain Object3D APIs (no WebGL draw). */

export const FITTED_TEMPLATES = ['super-heavyweight', 'powerhouse', 'showman', 'technician', 'highflyer', 'luchador',
  'powerhouse-w', 'athletic-w', 'striker-w'];

/* id -> { slot, name } for every fitted part shipped (mirrors customization/parts/hair/mpfb2/MANIFEST.json;
   test/fitted-parts.test.mjs keeps the two in step). slot = the fitted equip slot. */
export const FITTED_PARTS = {
  'mh-hair-short01': { slot: 'hair', name: 'Short Crop' },
  'mh-hair-short02': { slot: 'hair', name: 'Textured Short' },
  'mh-hair-short03': { slot: 'hair', name: 'Side Part' },
  'mh-hair-short04': { slot: 'hair', name: 'Slick Back' },
  'mh-hair-bob01': { slot: 'hair', name: 'Bob' },
  'mh-hair-bob02': { slot: 'hair', name: 'Layered Bob' },
  'mh-hair-long01': { slot: 'hair', name: 'Long Straight' },
  'mh-hair-ponytail01': { slot: 'hair', name: 'High Ponytail' },
  'mh-hair-braid01': { slot: 'hair', name: 'Single Braid' },
  'mh-hair-afro01': { slot: 'hair', name: 'Rounded Afro' },
  'mh-brows-001': { slot: 'eyebrows', name: 'Natural Brows' },
  'mh-brows-003': { slot: 'eyebrows', name: 'Thick Brows' },
  'mh-brows-006': { slot: 'eyebrows', name: 'Arched Brows' },
  'mh-brows-010': { slot: 'eyebrows', name: 'Thin Brows' },
  'mh-lashes-01': { slot: 'eyelashes', name: 'Natural Lashes' },
  'mh-lashes-02': { slot: 'eyelashes', name: 'Long Lashes' },
  'wh-beard-full': { slot: 'facial_hair', name: 'Full Beard' },
  'wh-beard-goatee': { slot: 'facial_hair', name: 'Goatee' },
  'wh-beard-moustache': { slot: 'facial_hair', name: 'Moustache' },
  'wh-beard-chinstrap': { slot: 'facial_hair', name: 'Chin Strap' },
  'wh-beard-stubble': { slot: 'facial_hair', name: 'Stubble' },
};

/* fitted slot -> attire colour key the suite saves the tint under (attire.colors[key]) */
export const FITTED_COLOR_KEY = { hair: 'hair', facial_hair: 'facial_hair', eyebrows: 'brows', eyelashes: 'lashes' };
/* base-body primitives a fitted slot replaces (the template's own MB-Lab eyelash strip hides under fitted lashes) */
export const FITTED_HIDES = { eyelashes: /eyelash/i };
export const FITTED_DIR = 'customization/parts/hair/mpfb2';

export const isFittedPart = id => Object.prototype.hasOwnProperty.call(FITTED_PARTS, id);

/** Repo-relative GLB path of a fitted part on a template; null when either is unknown. */
export function fittedPartPath(partId, templateId) {
  if (!isFittedPart(partId) || !FITTED_TEMPLATES.includes(templateId)) return null;
  return `${FITTED_DIR}/${partId}/${templateId}.glb`;
}

/** From a saved attire ({ equipped:{slotKey:partId}, colors:{} }) pick the fitted parts to show on `templateId`.
    Returns [{ id, slot, path, tint }] — one per fitted slot (last equipped wins), unknown ids skipped. */
export function selectFittedParts(attire, templateId) {
  const out = new Map();
  if (!attire || !attire.equipped || !FITTED_TEMPLATES.includes(templateId)) return [];
  for (const partId of Object.values(attire.equipped)) {
    if (!isFittedPart(partId)) continue;
    const slot = FITTED_PARTS[partId].slot;
    const tint = (attire.colors && attire.colors[FITTED_COLOR_KEY[slot]]) || null;
    out.set(slot, { id: partId, slot, path: fittedPartPath(partId, templateId), tint });
  }
  return [...out.values()];
}

/** The head bone of a template body under any of its names (MB-Lab 'head', Mixamo/T3 'Head' after remap). */
export function findHeadBone(root) {
  let hit = null;
  const names = ['Head', 'head', 'mixamorig:Head', 'mixamorigHead'];
  if (root && typeof root.traverse === 'function') {
    root.traverse((o) => { if (!hit && o.isBone && names.includes(o.name)) hit = o; });
  }
  return hit;
}

/** Parent a loaded fitted part (gltf.scene) to the head bone with an identity transform; tint + flag it.
    Returns the attached group. */
export function attachFittedScene(headBone, partScene, { partId, slot, tint } = {}) {
  partScene.name = 'fitted:' + partId;
  partScene.position.set(0, 0, 0); partScene.quaternion.set(0, 0, 0, 1); partScene.scale.set(1, 1, 1);
  partScene.userData.whFitted = { partId, slot };
  partScene.traverse((o) => {
    if (!o.isMesh) return;
    o.frustumCulled = false; // follows a skinned head; its own bbox lags the animated bone
    o.castShadow = true;
    if (o.material) {
      o.material = o.material.clone();
      if (tint && o.material.color) o.material.color.set(tint);
    }
  });
  headBone.add(partScene);
  return partScene;
}

export function setFittedTint(partScene, tint) {
  if (!partScene || !tint) return;
  partScene.traverse((o) => { if (o.isMesh && o.material && o.material.color) o.material.color.set(tint); });
}

function insideFitted(o) {
  for (let a = o; a; a = a.parent) if (a.userData && a.userData.whFitted) return true;
  return false;
}

/** Hide (or restore) base-body primitives a fitted slot replaces. Returns how many meshes changed. */
export function setBaseHidden(root, slot, hidden) {
  const re = FITTED_HIDES[slot];
  if (!re || !root) return 0;
  let n = 0;
  root.traverse((o) => {
    if (!o.isMesh || insideFitted(o)) return;
    const mats = Array.isArray(o.material) ? o.material : [o.material];
    if (mats.some(m => m && re.test(m.name || ''))) { o.visible = !hidden; n++; }
  });
  return n;
}

/** Remove every fitted part from a model; restores hidden base primitives. */
export function clearFittedParts(root) {
  if (!root) return 0;
  const found = [];
  root.traverse((o) => { if (o.userData && o.userData.whFitted) found.push(o); });
  for (const g of found) { setBaseHidden(root, g.userData.whFitted.slot, false); if (g.parent) g.parent.remove(g); }
  return found.length;
}

/** Load + attach the selected fitted parts onto `root` (a template body instance).
    loadScene(url) -> Promise<Object3D> (the gltf.scene). urlPrefix maps repo paths to the page ('../' in game/).
    afterAttach(root) re-applies morph values so new parts take the body's face sliders. Resolves to the groups. */
export async function loadFittedParts(root, list, { loadScene, urlPrefix = '', afterAttach } = {}) {
  const head = findHeadBone(root);
  if (!head || !list || !list.length) return [];
  const groups = [];
  for (const p of list) {
    try {
      const scene = await loadScene(urlPrefix + p.path);
      const g = attachFittedScene(head, scene, { partId: p.id, slot: p.slot, tint: p.tint });
      setBaseHidden(root, p.slot, true);
      groups.push(g);
    } catch (e) {
      console.warn('[WH] fitted part failed to load', p.id, e && (e.message || e));
    }
  }
  if (groups.length && afterAttach) { try { afterAttach(root); } catch (e) { /* morph re-apply is best effort */ } }
  return groups;
}
