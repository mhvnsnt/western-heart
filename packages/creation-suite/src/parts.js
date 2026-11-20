// parts.js — Creation Suite consumer for customization/PARTS-REGISTRY.json.
// Wires the universal libraries (eye-library, decal-library/pantera,
// parts/pantera-eyes, parts/superhero) so every part drops onto any
// character, Tekken/WWE-style: texture parts swap live and restore
// (nothing overwritten), mesh parts attach at bone sockets via attach().
// Data-only registry: the suite fetches the JSON and never edits it.
import * as THREE from 'three';
import { attach, detach } from './attire.js';

// part_class values carried by the registry
export const PART_CLASSES = ['texture_part', 'mesh_part'];

// --- loading --------------------------------------------------------------
// `fetcher` defaults to global fetch; pass a stub in tests/tools.
export async function loadRegistry(url, fetcher = (typeof fetch !== 'undefined' ? fetch : null)) {
  if (!fetcher) throw new Error('loadRegistry needs a fetch implementation');
  const res = await fetcher(url);
  if (!res.ok) throw new Error(`parts registry fetch failed: ${res.status} ${url}`);
  const reg = await res.json();
  if (!Array.isArray(reg.parts)) throw new Error('parts registry missing parts[]');
  return reg;
}

// --- queries ---------------------------------------------------------------
export function entriesForSlot(registry, suiteSlot) {
  return (registry.parts || []).filter(p => p.suite_slot === suiteSlot);
}
export function entriesForClass(registry, partClass) {
  return (registry.parts || []).filter(p => p.part_class === partClass);
}
export function entriesForLibrary(registry, library) {
  return (registry.parts || []).filter(p => p.library === library);
}
export function getEntry(registry, id) {
  return (registry.parts || []).find(p => p.id === id) || null;
}

// A part is usable on a character when the registry has a mapping for that
// character, or (mesh parts) when the character has the socket bone —
// attach() does the bone lookup per rig, so mapping is optional there.
export function usableOn(registry, entry, charId) {
  if (entry.part_class === 'mesh_part') return true;              // socket-fit on any rig
  return !!(registry.character_mappings?.[charId]);               // texture needs a mapping
}
export function entriesForCharacter(registry, charId) {
  return (registry.parts || []).filter(p => usableOn(registry, p, charId));
}

// Merge a character's mapping into a texture part's placement. Result is a
// concrete placement: { texture, material, mode, pixel_rect?, texture_size }.
export function resolveEntry(registry, entry, charId) {
  const pl = { ...(entry.placement || {}) };
  if (entry.part_class !== 'texture_part') return pl;
  const map = registry.character_mappings?.[charId];
  const kindMap = map?.[entry.kind] || map?.[entry.kind?.replace('_logo', '')];
  if (kindMap) {
    if (kindMap.texture) pl.texture = kindMap.texture;
    if (kindMap.material) pl.material = kindMap.material;
    if (kindMap.texture_size) pl.texture_size = kindMap.texture_size;
  }
  return pl;
}

// --- texture parts: live swap on a three.js scene --------------------------
// Find materials whose map (or material name) matches the placement, swap in
// the new texture, keep the originals for one-call restore. Returns a handle:
//   { restore(), targets: [{material, original}] }.
export function swapTexture(character, placement, texture) {
  const targets = [];
  const wantTex = (placement.texture || '').toLowerCase();
  const wantMat = (placement.material || '').toLowerCase();
  character.traverse(o => {
    if (!o.isMesh) return;
    const mats = Array.isArray(o.material) ? o.material : [o.material];
    for (const m of mats) {
      if (!m) continue;
      const texName = (m.map?.name || m.map?.image?.src || '').toLowerCase();
      const hit = (wantTex && texName.includes(wantTex)) ||
                  (wantMat && (m.name || '').toLowerCase().includes(wantMat));
      if (hit) targets.push({ material: m, original: m.map });
    }
  });
  if (!targets.length) throw new Error(`no material matched texture "${placement.texture}" / material "${placement.material}"`);
  for (const t of targets) { t.material.map = texture; t.material.needsUpdate = true; }
  return {
    targets,
    restore() { for (const t of targets) { t.material.map = t.original; t.material.needsUpdate = true; } },
  };
}

// Track live swaps per character so the suite can list/restore them.
export function applyTexturePart(character, entry, texture, { registry = null, charId = null } = {}) {
  const placement = registry && charId ? resolveEntry(registry, entry, charId) : (entry.placement || {});
  const handle = swapTexture(character, placement, texture);
  (character.userData.csParts ||= {})[entry.id] = { kind: 'texture', handle, placement };
  return handle;
}
export function removePart(character, entryId) {
  const slot = character.userData.csParts?.[entryId];
  if (!slot) return false;
  if (slot.kind === 'texture') slot.handle.restore();
  else detach(character, slot.socket);
  delete character.userData.csParts[entryId];
  return true;
}

// --- mesh parts: socket attach via attire.js --------------------------------
export function applyMeshPart(character, entry, pieceScene, { registry = null, charId = null, edit = {}, fit = null } = {}) {
  const placement = entry.placement || {};
  const manifest = { socket: { bone_aliases: placement.bone_aliases } };
  const merged = {
    offset: placement.offset || [0, 0, 0],
    rotation: placement.rotation || [0, 0, 0],
    scale: placement.scale ?? 1.0,
    ...edit,
  };
  // auto-scale for characters the piece wasn't modeled in place for
  const autoFit = fit || (placement.modeled_in_place_for && charId && placement.modeled_in_place_for !== charId
    ? { headHeight: 0.24 } : null);
  const holder = attach(character, placement.socket, pieceScene, { manifest, edit: merged, fit: autoFit });
  (character.userData.csParts ||= {})[entry.id] = { kind: 'mesh', socket: placement.socket, holder };
  return holder;
}

// One call the UI/tests use: routes texture_part vs mesh_part.
export function applyPart(character, entry, asset, { registry = null, charId = null, edit = {}, fit = null } = {}) {
  if (entry.part_class === 'texture_part') return applyTexturePart(character, entry, asset, { registry, charId });
  if (entry.part_class === 'mesh_part') return applyMeshPart(character, entry, asset, { registry, charId, edit, fit });
  throw new Error(`unknown part_class "${entry.part_class}"`);
}
