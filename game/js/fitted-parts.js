/* fitted-parts.js — template-FITTED hair / facial hair / eyebrows / eyelashes (creation suite HAIR phase, 2026-11-02).

   The parts are MakeHuman / MPFB2 CC0 system assets (hair, eyebrows, eyelashes) and CC0 beard shells cut from the
   MakeHuman base mesh, fitted offline onto each of the 9 creation-suite template bodies
   (tools/mpfb2/hair/fit_proxies.py + build_glb.mjs). Each fit is one GLB per template:
     customization/parts/hair/mpfb2/<part-id>/<template-id>.glb   (+ a shared texture.png beside it)
   Since the Blender stage (tools/mpfb2/hair/blender_fit.py, 2026-11-02) each GLB is authored in the template's
   MODEL BIND space and carries per-vertex skin weights (JOINTS_0 / WEIGHTS_0, joint indices = the template's glTF
   skin joint order) transferred from the template skin in Blender: brows / lashes 100 % head, beards head + neck,
   hair head / neck / upper spine / clavicles, so long hair follows the neck and shoulders instead of swinging
   rigidly with the skull. attachFittedScene turns each weighted mesh into a SkinnedMesh bound to the BODY's own
   skeleton (same joint order), and still parents the group under the head bone for bookkeeping (attached bind
   mode cancels the parent transform). Morph targets carry the template's own slider names (transferred in Blender
   with Surface Deform), so face sliders move brows / lashes / beards / hairline with the body. Older head-local
   GLBs (no weights) still attach rigidly to the head bone.

   Used by both the suite preview (customization/creation-suite-ui/js/viewer3d.js) and the fight/select model
   (game/js/fighter.js, created fighters on custom-template-<id>). Pure helpers first (node-testable), then the
   three.js attach helpers, which only touch plain Object3D APIs (no WebGL draw). */

export const FITTED_TEMPLATES = ['super-heavyweight', 'powerhouse', 'showman', 'technician', 'highflyer', 'luchador',
  'powerhouse-w', 'athletic-w', 'striker-w'];

/* id -> { slot, name } for every fitted part shipped (mirrors customization/parts/hair/mpfb2/MANIFEST.json;
   test/fitted-parts.test.mjs keeps the two in step). slot = the fitted equip slot. */
export const CLOTHING_DIR = 'customization/parts/clothing/generated';
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
  /* CLOTHING + ACCESSORIES phase (2026-11-03): original CC0 garments generated in Blender on each template body
     (tools/mpfb2/clothing/shell_fit.py), mirrors customization/parts/clothing/generated/MANIFEST.json. slot = the
     attire equip key (Tekken slot spine: 9 upper, 10 full body, 11 lower, H hands, F feet, 12x/13x/4 accessories). */
  'wh-top-compression': { slot: '9', name: 'Compression Shirt', dir: CLOTHING_DIR, kind: 'clothing' },
  'wh-top-tee': { slot: '9', name: 'Fitted Tee', dir: CLOTHING_DIR, kind: 'clothing' },
  'wh-top-tank': { slot: '9', name: 'Tank Top', dir: CLOTHING_DIR, kind: 'clothing' },
  'wh-top-crop': { slot: '9', name: 'Sports Top', dir: CLOTHING_DIR, kind: 'clothing' },
  'wh-singlet': { slot: '10', name: 'Singlet', dir: CLOTHING_DIR, kind: 'clothing' },
  'wh-trunks': { slot: '11', name: 'Wrestling Trunks', dir: CLOTHING_DIR, kind: 'clothing' },
  'wh-tights-long': { slot: '11', name: 'Long Tights', dir: CLOTHING_DIR, kind: 'clothing' },
  'wh-shorts-fight': { slot: '11', name: 'Fight Shorts', dir: CLOTHING_DIR, kind: 'clothing' },
  'wh-gloves-mma': { slot: 'H', name: 'Open-Finger Gloves', dir: CLOTHING_DIR, kind: 'clothing' },
  'wh-gloves-full': { slot: 'H', name: 'Full Gloves', dir: CLOTHING_DIR, kind: 'clothing' },
  'wh-boots-knee': { slot: 'F', name: 'Knee-High Boots', dir: CLOTHING_DIR, kind: 'clothing' },
  'wh-boots-ankle': { slot: 'F', name: 'Ankle Boots', dir: CLOTHING_DIR, kind: 'clothing' },
  'wh-kneepads': { slot: '13K', name: 'Knee Pads', dir: CLOTHING_DIR, kind: 'accessories' },
  'wh-elbowpads': { slot: '12E', name: 'Elbow Pads', dir: CLOTHING_DIR, kind: 'accessories' },
  'wh-wrist-tape': { slot: '12W', name: 'Wrist Tape', dir: CLOTHING_DIR, kind: 'accessories' },
  'wh-armbands': { slot: '12A', name: 'Arm Bands', dir: CLOTHING_DIR, kind: 'accessories' },
  'wh-headband': { slot: '4', name: 'Headband', dir: CLOTHING_DIR, kind: 'accessories' },
  'wh-belt': { slot: '13B', name: 'Waist Belt', dir: CLOTHING_DIR, kind: 'accessories' },
};

/* fitted slot -> attire colour key the suite saves the tint under (attire.colors[key]) */
export const FITTED_COLOR_KEY = { hair: 'hair', facial_hair: 'facial_hair', eyebrows: 'brows', eyelashes: 'lashes' };
/* base-body primitives a fitted slot replaces (the template's own MB-Lab eyelash strip hides under fitted lashes) */
export const FITTED_HIDES = { eyelashes: /eyelash/i };
export const FITTED_DIR = 'customization/parts/hair/mpfb2';

export const isFittedPart = id => Object.prototype.hasOwnProperty.call(FITTED_PARTS, id);
export const isFittedClothing = id => isFittedPart(id) && FITTED_PARTS[id].dir === CLOTHING_DIR;

/** Attire colour key a fitted part's tint is saved under: hair-phase parts share their slot key (hair, brows, ...);
    each clothing / accessory slot has its own ('cloth_9', 'cloth_12E', ...). */
export function fittedColorKey(partId, suiteSlot) {
  if (isFittedClothing(partId)) return 'cloth_' + FITTED_PARTS[partId].slot;
  return FITTED_COLOR_KEY[suiteSlot || (isFittedPart(partId) && FITTED_PARTS[partId].slot)] || null;
}

/** Repo-relative GLB path of a fitted part on a template; null when either is unknown. */
export function fittedPartPath(partId, templateId) {
  if (!isFittedPart(partId) || !FITTED_TEMPLATES.includes(templateId)) return null;
  return `${FITTED_PARTS[partId].dir || FITTED_DIR}/${partId}/${templateId}.glb`;
}

/** From a saved attire ({ equipped:{slotKey:partId}, colors:{} }) pick the fitted parts to show on `templateId`.
    Returns [{ id, slot, path, tint }] — one per fitted slot (last equipped wins), unknown ids skipped. */
export function selectFittedParts(attire, templateId) {
  const out = new Map();
  if (!attire || !attire.equipped || !FITTED_TEMPLATES.includes(templateId)) return [];
  for (const partId of Object.values(attire.equipped)) {
    if (!isFittedPart(partId)) continue;
    const slot = FITTED_PARTS[partId].slot;
    const tint = (attire.colors && attire.colors[fittedColorKey(partId, slot)]) || null;
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

/** The body SkinnedMesh whose skeleton holds `bone` (the template's skin primitive group shares one skeleton). */
export function findBodySkin(bone) {
  let root = bone; while (root && root.parent) root = root.parent;
  let hit = null;
  if (root) root.traverse((o) => { if (!hit && o.isSkinnedMesh && o.skeleton && o.skeleton.bones.includes(bone) && !insideFitted(o)) hit = o; });
  return hit;
}

/** Re-bind every skinned fitted mesh to the BODY's live skeleton. The part GLB carries its own small glTF skin (flat
    joints at the template's bind matrices) plus extras wh_joint_index (each joint's index in the template skin) and
    wh_joint_ibm (the template's original inverse bind matrices). Bone i of the part becomes body bone wh_joint_index[i];
    its inverse is bodyInverse * inverse(templateIBM) * partIBM, so the bind pose matches the body even when the instance
    path re-derived the body's inverses (bone remap / frame conversion), and gltfpack's dequantisation (part IBM or
    node matrix) is kept. Returns how many meshes were re-bound. */
export function skinToBody(partScene, bodySkin) {
  if (!bodySkin || !bodySkin.skeleton) return 0;
  const todo = [];
  partScene.traverse((o) => { if (o.isSkinnedMesh && o.skeleton) todo.push(o); });
  let n = 0;
  for (const sm of todo) {
    let ud = null;
    for (let a = sm; a && !ud; a = a.parent) if (a.userData && Array.isArray(a.userData.wh_joint_index)) ud = a.userData;
    if (!ud) continue;
    const bodyBones = bodySkin.skeleton.bones, bodyInv = bodySkin.skeleton.boneInverses;
    const bones = ud.wh_joint_index.map((i) => bodyBones[i]);
    if (bones.some((b) => !b)) continue;
    const M4 = bodyInv[0].constructor;
    const inv = ud.wh_joint_index.map((i, k) => bodyInv[i].clone()
      .multiply(new M4().fromArray(ud.wh_joint_ibm, k * 16).invert())
      .multiply(sm.skeleton.boneInverses[k]));
    const own = sm.skeleton.bones;
    sm.bind(new bodySkin.skeleton.constructor(bones, inv), sm.bindMatrix);
    for (const b of own) if (b.parent && !b.children.some((c) => c.isMesh)) b.parent.remove(b);  // drop the GLB's joint stubs
    sm.userData.whSkinned = true;
    n++;
  }
  return n;
}

/** Attach a loaded fitted part (gltf.scene) under the head bone; weighted meshes are skinned to the body skeleton,
    unweighted (legacy head-local) meshes ride the head bone rigidly. Tint + flag it. Returns the attached group. */
export function attachFittedScene(headBone, partScene, { partId, slot, tint } = {}) {
  partScene.name = 'fitted:' + partId;
  partScene.position.set(0, 0, 0); partScene.quaternion.set(0, 0, 0, 1); partScene.scale.set(1, 1, 1);
  partScene.userData.whFitted = { partId, slot };
  partScene.userData.whFitted.skinned = skinToBody(partScene, findBodySkin(headBone)) > 0;
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
  if (!root) return 0;
  applyBodyHide(root);  // clothing: drop / restore the body triangles under every attached garment
  const re = FITTED_HIDES[slot];
  if (!re) return 0;
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
  for (const g of found) { if (g.parent) g.parent.remove(g); setBaseHidden(root, g.userData.whFitted.slot, false); }
  applyBodyHide(root);
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

/* ---------------- body-triangle hiding under fitted clothing (CLOTHING phase, 2026-11-03) ----------------
   Each clothing GLB carries mesh extras wh_hide = { skin | generic | nails: run-length [start, count, ...] } — the
   template body vertices the garment covers (>= 4 mm inside its region, measured in Blender), indexed in the template
   GLB's own per-primitive vertex order. The body primitive is recognised by its material name (skin / nails /
   generic, same rule as tools/mpfb2/clothing/dump_prims.mjs). A body triangle is dropped when ALL 3 of its vertices
   are hidden, so the cut stays inside the garment and the body can't poke through at bends. The original index
   buffer is kept on the geometry (userData.whOrigIndex) and restored when nothing covers it. */

/** run-length [start, count, ...] -> Set of vertex indices */
export function expandRuns(runs) {
  const out = new Set();
  if (!Array.isArray(runs)) return out;
  for (let i = 0; i + 1 < runs.length; i += 2) for (let k = 0; k < runs[i + 1]; k++) out.add(runs[i] + k);
  return out;
}

/** body primitive key from its material name, or null */
export function bodyPrimKey(materialName) {
  const m = materialName || '';
  return /skin/i.test(m) ? 'skin' : /nails/i.test(m) ? 'nails' : /generic/i.test(m) ? 'generic' : null;
}

/** Index array with every triangle whose 3 vertices are all in `hidden` removed (pure; node-testable). */
export function filterTriangles(index, hidden) {
  if (!hidden || !hidden.size) return index;
  const out = [];
  for (let f = 0; f + 2 < index.length; f += 3) {
    const a = index[f], b = index[f + 1], c = index[f + 2];
    if (hidden.has(a) && hidden.has(b) && hidden.has(c)) continue;
    out.push(a, b, c);
  }
  return out;
}

/** Union of the wh_hide lists of every fitted group attached under `root`, per body primitive key. */
export function collectBodyHide(root) {
  const out = {};
  if (!root || typeof root.traverse !== 'function') return out;
  root.traverse((o) => {
    if (!o.userData || !o.userData.wh_hide) return;
    let inside = false; for (let a = o; a && !inside; a = a.parent) if (a.userData && a.userData.whFitted) inside = true;
    if (!inside) return;
    for (const [k, runs] of Object.entries(o.userData.wh_hide)) {
      const set = out[k] || (out[k] = new Set());
      for (const v of expandRuns(runs)) set.add(v);
    }
  });
  return out;
}

/** Re-apply body-triangle hiding on a body instance from the garments currently attached. Returns triangles hidden. */
export function applyBodyHide(root) {
  if (!root || typeof root.traverse !== 'function') return 0;
  const hide = collectBodyHide(root);
  let dropped = 0;
  root.traverse((o) => {
    if (!o.isMesh || !o.geometry || insideFitted(o)) return;
    const mat = Array.isArray(o.material) ? o.material[0] : o.material;
    const key = bodyPrimKey(mat && mat.name);
    if (!key) return;
    const set0 = hide[key];
    if (!o.userData.whOwnGeom) {
      // instances (SkeletonUtils.clone) share one geometry: take a private copy before the first cut
      if (!(set0 && set0.size) || !o.geometry.index) return;
      o.geometry = o.geometry.clone(); o.userData.whOwnGeom = true;
    }
    const g = o.geometry, idx = g.index;
    if (!g.userData.whOrigIndex) g.userData.whOrigIndex = idx.array.slice();
    const orig = g.userData.whOrigIndex;
    const set = hide[key];
    const next = set && set.size ? filterTriangles(orig, set) : orig;
    if (next === orig && idx.array.length === orig.length) return;
    const Arr = orig.constructor;
    g.setIndex(new idx.constructor(next instanceof Arr ? next : Arr.from(next), 1));
    dropped += (orig.length - next.length) / 3;
  });
  return dropped;
}
