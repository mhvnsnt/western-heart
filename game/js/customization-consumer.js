/* ============================================================
   WESTERN HEART — Creation Suite in-fight consumer
   (fighter-completeness lane, 2026-10-21)

   THE GAP THIS CLOSES: the Creation Suite could build a profile for a
   fighter, but nothing in the fight scene ever applied it — profiles
   were read for CAW fighters by custom-fighter.js (appearance only,
   and even there `F.profile.parts` was never consumed). This module is
   the missing consumer: after a fighter's model is built for a match,
   the fighter's suite profile is resolved against the merged part
   catalogs and every part is attached at its bone socket ON the
   fighting model, live in the fight.

   CONTRACT (shared, never forked):
   - Profile shape = customization.json v1, exactly what the suite UI
     writes (docs/CREATION-SUITE-UI-SCHEMA-2026-10-21.md): a record with
     `parts: { <slot>: { part_id, glb?, placement? } }`, `textures[]`,
     `item_colors`, plus the UI's additive keys. The same record shape
     custom-fighter.js reads from localStorage 'wh_creation_suite_v1'.
   - Resolution + application are the suite's OWN functions:
     packages/creation-suite/src/catalogs.js (loadCatalog /
     mergeCatalogs / resolveProfileParts) and src/parts.js (applyPart —
     texture swap or bone-socket mesh attach via src/attire.js).
     This module only adapts: profile lookup, placement-dialect
     translation, per-source unit scale, and tint selection.
   - Catalogs merge exactly like the suite: PARTS-REGISTRY wins dedupe,
     per-game catalogs fill in (No Mercy now; Tekken 7's catalog is an
     honest empty parts[] until real meshes land; Tekken 5/6 catalogs
     are picked up automatically when the gap-closure lane lands them).

   PROFILE SOURCES (first hit wins):
   1. localStorage 'wh_creation_suite_v1' — the record the suite UI
      saves. It belongs to this fighter when its `fighter` field is
      this fighter's roster id, or (CAW-style records, fighter
      'custom') when `profile.name` matches the fighter's roster name.
   2. customization/profiles/<fighter-id>.json in the repo — a
      versioned profile committed for the fighter.

   PLACEMENT DIALECTS: profiles carry the Tekken template dialect
   { px, py, pz, rx, ry, rz, s, socket? } (degrees); catalog entries
   carry the parts.js dialect { offset, rotation, scale, socket,
   bone_aliases }. Both are normalized here into the parts.js shape.
   Part scenes are wrapped in a group centred on their bounding box
   before attach, so
   offsets mean "from the bone" in metres.

   UNIT SCALE: No Mercy (AKI) part GLBs are authored in centimetre
   units (a 0.8 m bat is 80 units long in the file) — ×0.01. Registry /
   game-authored parts are already in metres — ×1. The profile's own
   `s` multiplies on top (the UI's s: 1 = as authored).

   SCOPE BOUNDARY (v1): parts + part tints + texture layers apply live.
   Body morphs / body type / skin tone stay with the CAW loader and the
   bake engine (customization/tools/apply_customization.py) — a roster
   fighter's own textured model is never re-tinted here. Parts do NOT
   follow a mid-match transformation in v1: they stay on the model they
   were attached to (re-applying on transform needs a hook inside
   fighter.js's transform path — flagged by this lane, not hacked in).

   SAFETY: fully additive and fail-silent per part. No profile, no
   catalog, an unresolvable part id, or a missing socket bone logs a
   [WH-CS] line and the fight proceeds untouched. This module never
   throws into the match loop.
   ============================================================ */
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.js';
import { loadCatalog, mergeCatalogs, resolveProfileParts } from '../../packages/creation-suite/src/catalogs.js';
import { applyPart } from '../../packages/creation-suite/src/parts.js';

const ROOT = new URL('../../', import.meta.url);
const LS_KEY_SUITE = 'wh_creation_suite_v1';

const CATALOG_PATHS = [
  'customization/parts/no-mercy/CATALOG.json',
  'customization/parts/tekken7/CATALOG.json',
  'customization/parts/tekken6/CATALOG.json',   // lands with gap-closure W7
  'customization/parts/tekken5/CATALOG.json',    // lands with gap-closure W7
  'customization/parts/defjam/CATALOG.json',
  'customization/parts/wmxix/CATALOG.json',
];

/* Authoring-unit scale per part source (see header).
   EXPORTED for the Creation Suite UI v2 lane (2026-10-21): its live
   character viewport is the editor-side twin of this consumer and must
   attach parts identically — import these helpers, never fork them. */
export const UNIT_SCALE = { 'no-mercy': 0.01 };

/* Profile/catalogue slot -> attire.js attach slot (bone-socket family). */
export const SOCKET_BY_SLOT = {
  upper_body: 'torso', upper: 'torso', full_body: 'torso', attire: 'torso', torso: 'torso', jacket: 'torso',
  face: 'face', eyes: 'face', eye: 'face', gla: 'face', glasses: 'face', mask: 'face', eye_lenses: 'face',
  full_head: 'head', cowl: 'head', head: 'head', hair: 'hair',
  lower_body: 'legs', lower: 'legs', tights: 'legs', pants: 'legs', legs: 'legs',
  hands: 'hands', gloves: 'hands', gauntlets: 'hands',
  feet: 'feet', shoes: 'feet',
  waist: 'waist', lower_acc: 'waist',
  accessory: 'accessory', upper_acc: 'accessory', extra: 'accessory', arms: 'arms',
};

let _entriesPromise = null;
let _registryObj = null;
function loadMergedEntries() {
  if (_entriesPromise) return _entriesPromise;
  _entriesPromise = (async () => {
    const fetcher = (u) => fetch(new URL(u, ROOT));
    try { _registryObj = await loadCatalog('customization/PARTS-REGISTRY.json', fetcher); }
    catch (e) { console.warn('[WH-CS] parts registry unavailable:', e.message || e); _registryObj = { parts: [] }; }
    const cats = [];
    for (const p of CATALOG_PATHS) {
      try { cats.push(await loadCatalog(p, fetcher)); }
      catch (e) { /* catalog not landed yet — the merge simply skips it */ }
    }
    const entries = mergeCatalogs(_registryObj, ...cats);
    console.log(`[WH-CS] catalogs merged: ${entries.length} part entries`);
    return entries;
  })();
  return _entriesPromise;
}

let _loader = null;
const _sceneCache = new Map();
function gltfLoader() {
  if (_loader) return _loader;
  _loader = new GLTFLoader();
  try { _loader.setMeshoptDecoder(MeshoptDecoder); } catch (e) { /* non-meshopt parts still load */ }
  return _loader;
}
async function loadPartScene(glbPath) {
  if (_sceneCache.has(glbPath)) return _sceneCache.get(glbPath);
  const url = new URL(glbPath, ROOT).href;
  const gltf = await gltfLoader().loadAsync(url);
  _sceneCache.set(glbPath, gltf.scene);
  return gltf.scene;
}

/* Wrap a part scene in a group whose origin is the part's bounding-box
   centre (raw part units), so profile offsets read as metres-from-the-
   bone after scaling, and placement rotations turn the part around its
   own centre. Per-geometry translation is NOT used: converted parts can
   carry baked node rotations, which swing re-centred geometry off-axis;
   the wrapper centres the whole scene regardless of its internals, and
   leaves the (shared) geometries untouched. */
function centerWrap(scene) {
  scene.updateMatrixWorld(true);
  const box = new THREE.Box3().setFromObject(scene);
  if (box.isEmpty()) return scene;
  const c = box.getCenter(new THREE.Vector3());
  scene.position.sub(c);
  const wrap = new THREE.Group();
  wrap.name = 'cs_part_wrap';
  wrap.add(scene);
  return wrap;
}

/* Normalize a profile/entry placement (either dialect) into the
   parts.js shape, with the socket + unit scale resolved.
   EXPORTED for the UI v2 lane's live viewport (same normalization). */
export function effectivePlacement(raw, entry, slotKey) {
  const p = raw || {};
  const out = {};
  if (Array.isArray(p.offset)) out.offset = p.offset;
  else if (p.px != null || p.py != null || p.pz != null) out.offset = [p.px || 0, p.py || 0, p.pz || 0];
  if (Array.isArray(p.rotation)) out.rotation = p.rotation;
  else if (p.rx != null || p.ry != null || p.rz != null) out.rotation = [p.rx || 0, p.ry || 0, p.rz || 0];
  const unit = UNIT_SCALE[entry?.source_game || entry?.library] ?? 1;
  const s = (p.scale != null ? p.scale : (p.s != null ? p.s : 1)) * unit;
  out.scale = s;
  out.socket = p.socket || SOCKET_BY_SLOT[slotKey] || SOCKET_BY_SLOT[entry?.suite_slot] || 'accessory';
  if (p.bone_aliases) out.bone_aliases = p.bone_aliases;
  if (p.modeled_in_place_for) out.modeled_in_place_for = p.modeled_in_place_for;
  return out;
}

function profileBelongsTo(record, fighter) {
  if (!record || typeof record !== 'object') return false;
  if (record.fighter && record.fighter !== 'custom') return record.fighter === fighter.char.id;
  const nm = (record.profile?.name || '').toUpperCase();
  return !!nm && nm === (fighter.char.name || '').toUpperCase();
}

async function findProfile(fighter) {
  try {
    const raw = localStorage.getItem(LS_KEY_SUITE);
    if (raw) {
      const rec = JSON.parse(raw);
      if (profileBelongsTo(rec, fighter)) return rec;
    }
  } catch (e) { /* storage unavailable — fall through to the repo profile */ }
  try {
    const res = await fetch(new URL(`customization/profiles/${fighter.char.id}.json`, ROOT));
    if (res.ok) {
      const rec = await res.json();
      if (rec && (rec.parts || rec.textures)) return rec;
    }
  } catch (e) { /* no repo profile — the common case */ }
  return null;
}

/**
 * Apply a fighter's Creation Suite profile to their in-fight model.
 * `fighter` is the game's Fighter instance ({ char, model }). Fire and
 * forget: resolves to a small status object, never rejects.
 */
export async function applyFighterProfile(fighter) {
  const status = { char: fighter?.char?.id || '?', applied: [], skipped: [] };
  try {
    const model = fighter?.model;
    const charId = fighter?.char?.id;
    if (!model || !charId) return status;
    if (model.userData.csProfileApplied) return status;
    model.userData.csProfileApplied = true; // set early: attach is one-shot per model instance

    const profile = await findProfile(fighter);
    if (!profile) return status;
    const entries = await loadMergedEntries();

    // --- mesh + registry parts (profile.parts, customization.json v1) ---
    const resolved = resolveProfileParts(entries, profile);
    for (const r of resolved) {
      const label = `${r.slot}:${r.part_id || '?'}`;
      if (r.status !== 'resolved' || !r.entry) {
        console.warn(`[WH-CS] ${charId} part UNRESOLVED ${label} — reported, not dropped silently`);
        status.skipped.push(label);
        continue;
      }
      const entry = r.entry;
      try {
        if (entry.part_class === 'mesh_part' || r.glb) {
          if (!r.glb) throw new Error('entry has no GLB yet (conversion pending)');
          const base = await loadPartScene(r.glb);
          const piece = centerWrap(base.clone(true));
          const placement = effectivePlacement(r.placement, entry, r.slot);
          const effEntry = { ...entry, placement };
          const colors = profile.item_colors?.[r.slot] || [];
          const tint = colors.find((c) => c && c.toLowerCase() !== '#ffffff') || null;
          applyPart(model, effEntry, piece, { registry: _registryObj, charId, edit: tint ? { tint } : {} });
          // Converted catalog parts are thin shells whose winding is not
          // consistent (several No Mercy pieces face inward): rendered
          // single-sided they vanish from most angles. Attached gear is
          // therefore forced double-sided here, in the consumer's layer.
          piece.traverse((o) => {
            if (!o.isMesh) return;
            const ms = Array.isArray(o.material) ? o.material : [o.material];
            ms.forEach((m) => { if (m && 'side' in m) m.side = THREE.DoubleSide; });
          });
          console.log(`[WH-CS] ${charId} part attached: ${entry.id} at socket '${placement.socket}' (scale ${placement.scale})${tint ? ` tint ${tint}` : ''}`);
          status.applied.push(label);
        } else if (entry.part_class === 'texture_part') {
          status.skipped.push(label + ' (texture part without an image layer — see profile.textures)');
        } else {
          status.skipped.push(label + ` (part_class ${entry.part_class || 'none'} not applicable live)`);
        }
      } catch (e) {
        console.warn(`[WH-CS] ${charId} part FAILED ${label}:`, e.message || e);
        status.skipped.push(label);
      }
    }

    // --- texture layers (profile.textures: image + kind, registry-mapped) ---
    for (const layer of profile.textures || []) {
      const entry = entries.find((p) => p.id === layer.part_id);
      if (!entry || !layer.image) { if (layer.part_id) status.skipped.push(`texture:${layer.part_id}`); continue; }
      try {
        const tex = await new THREE.TextureLoader().loadAsync(new URL(layer.image, ROOT).href);
        tex.colorSpace = THREE.SRGBColorSpace;
        applyPart(model, entry, tex, { registry: _registryObj, charId });
        console.log(`[WH-CS] ${charId} texture applied: ${layer.part_id} (${layer.kind || 'layer'})`);
        status.applied.push(`texture:${layer.part_id}`);
      } catch (e) {
        console.warn(`[WH-CS] ${charId} texture FAILED ${layer.part_id}:`, e.message || e);
        status.skipped.push(`texture:${layer.part_id}`);
      }
    }

    console.log(`[WH-CS] STATE char=${charId} profile_applied=[${status.applied.join(', ')}] skipped=[${status.skipped.join(', ')}]`);
  } catch (e) {
    console.warn('[WH-CS] consumer error (fight unaffected):', e.message || e);
  }
  return status;
}
