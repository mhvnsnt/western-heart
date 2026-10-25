// rigswap.js — Tekken-style part swapping on a shared rig.
//
// Tekken 7 builds every fighter from separate skinned parts (face, hair,
// upper body, lower body, ...) that are all bound to the same skeleton
// (MODEL_00 / BASE / Spine1 ... ~210 joints). Swapping an item is not a
// socket attach: the new part's SkinnedMesh is re-bound to the live
// character's bones by NAME, and the old part in that slot is removed.
// This module does that for any rig whose part and body share bone names
// (T7 parts on a T7 body; WH parts made on the WH rig). Parts that do not
// match enough bones are refused (caller falls back to the socket attach in
// parts.js), never half-bound.
import * as THREE from 'three';

export function boneMap(root) {
  const m = new Map();
  root.traverse((o) => { if (o.isBone && !m.has(o.name)) m.set(o.name, o); });
  return m;
}

/** Fraction of a part's joints the target rig has (0..1). */
export function rigCoverage(partRoot, targetRoot) {
  const bones = boneMap(targetRoot);
  let need = 0, have = 0;
  partRoot.traverse((o) => {
    if (!o.isSkinnedMesh) return;
    for (const b of o.skeleton.bones) { need++; if (bones.has(b.name)) have++; }
  });
  return need ? have / need : 0;
}

export function removeSwapped(targetRoot, slot) {
  const reg = targetRoot.userData.csSwapped || {};
  const prev = reg[slot];
  if (!prev) return false;
  for (const m of prev) { m.parent?.remove(m); m.geometry?.dispose?.(); }
  delete reg[slot];
  return true;
}

/**
 * Bind every SkinnedMesh of `partRoot` to `targetRoot`'s skeleton and add it
 * under the target. Returns { ok, coverage, meshes }.
 * Opts: minCoverage (default 0.9), hide: array of mesh names on the target to
 * hide while this slot is filled (e.g. the base upper body).
 */
export function swapSkinnedPart(targetRoot, partRoot, slot, { minCoverage = 0.9 } = {}) {
  const cov = rigCoverage(partRoot, targetRoot);
  if (cov < minCoverage) return { ok: false, coverage: cov, meshes: [] };
  removeSwapped(targetRoot, slot);
  const bones = boneMap(targetRoot);
  const meshes = [];
  const src = [];
  partRoot.traverse((o) => { if (o.isSkinnedMesh) src.push(o); });
  for (const o of src) {
    // Joints the target lacks (part-only cloth/physics bones) follow their
    // nearest ancestor the target has, so no weight is ever left unbound.
    const fallback = [...bones.values()][0];
    const mapped = o.skeleton.bones.map((b) => {
      for (let n = b; n; n = n.parent) { const t = n.isBone !== false && bones.get(n.name); if (t) return t; }
      return fallback;
    });
    const inv = o.skeleton.boneInverses.map((m) => m.clone());
    const mesh = new THREE.SkinnedMesh(o.geometry, o.material);
    mesh.name = o.name; mesh.frustumCulled = false;
    mesh.userData.csSlot = slot;
    targetRoot.add(mesh);
    mesh.bind(new THREE.Skeleton(mapped, inv), new THREE.Matrix4());
    meshes.push(mesh);
  }
  (targetRoot.userData.csSwapped ||= {})[slot] = meshes;
  return { ok: true, coverage: cov, meshes };
}
