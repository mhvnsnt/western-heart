// Attire slots. Every game uses the same slot names so any piece (the Bannon
// mask first) attaches to any character. Pieces are GLBs + a manifest
// (see western-heart lab/game/attire/bannon_mask/bannon_mask.manifest.json).
import * as THREE from 'three';

export const SLOTS = ['face', 'head', 'hair', 'torso', 'jacket', 'arms', 'hands', 'waist', 'legs', 'feet', 'accessory'];
export const SOCKETS = {
  face: ['Head', 'mixamorig:Head', 'head', 'J_Head', 'Bip01 Head'],
  head: ['Head', 'mixamorig:Head', 'head', 'J_Head', 'Bip01 Head'],
  hair: ['Head', 'mixamorig:Head', 'head'],
  torso: ['Chest', 'Spine2', 'mixamorig:Spine2', 'Spine'],
  jacket: ['Chest', 'Spine2', 'mixamorig:Spine2'],
  waist: ['Hips', 'mixamorig:Hips', 'pelvis'],
  hands: ['RightHand', 'mixamorig:RightHand'],
  accessory: ['Chest', 'Neck'],
};

export function findSocket(root, slot, aliases) {
  const names = aliases || SOCKETS[slot] || [];
  let found = null;
  for (const n of names) { root.traverse(o => { if (!found && o.isBone && o.name === n) found = o; }); if (found) break; }
  return found;
}

// edit = { offset:[x,y,z], rotation:[x,y,z] deg, scale:number|[x,y,z], tint:'#rrggbb', roughness, metalness, visible }
export function applyEdit(piece, edit = {}) {
  const base = piece.userData.csBase || (piece.userData.csBase = { p: piece.position.clone(), r: piece.rotation.clone(), s: piece.scale.clone() });
  piece.position.copy(base.p).add(new THREE.Vector3(...(edit.offset || [0, 0, 0])));
  const r = edit.rotation || [0, 0, 0];
  piece.rotation.set(base.r.x + THREE.MathUtils.degToRad(r[0]), base.r.y + THREE.MathUtils.degToRad(r[1]), base.r.z + THREE.MathUtils.degToRad(r[2]));
  const s = edit.scale ?? 1; piece.scale.copy(base.s).multiply(Array.isArray(s) ? new THREE.Vector3(...s) : new THREE.Vector3(s, s, s));
  piece.visible = edit.visible ?? true;
  piece.traverse(o => {
    if (!o.isMesh) return;
    o.material = o.userData.csOwnMat || (o.userData.csOwnMat = o.material.clone());
    if (edit.tint) o.material.color.set(edit.tint);
    if (edit.roughness != null) o.material.roughness = edit.roughness;
    if (edit.metalness != null) o.material.metalness = edit.metalness;
  });
  return piece;
}

// Attach a loaded attire scene to a character. fit: { headHeight } lets the
// piece auto-scale to the target head (so one mask fits every rig size).
export function attach(character, slot, pieceScene, { manifest = null, edit = {}, fit = null } = {}) {
  const socket = findSocket(character, slot, manifest?.socket?.bone_aliases);
  if (!socket) throw new Error(`no socket bone for slot ${slot}`);
  detach(character, slot);
  const holder = new THREE.Group(); holder.name = 'cs_attire_' + slot;
  holder.add(pieceScene);
  // cancel the socket's world scale so piece is in metres
  socket.updateWorldMatrix(true, false);
  const ws = new THREE.Vector3(); socket.getWorldScale(ws);
  holder.scale.set(1 / ws.x, 1 / ws.y, 1 / ws.z);
  const q = new THREE.Quaternion(); socket.getWorldQuaternion(q); holder.quaternion.copy(q.invert());
  if (fit) {
    const box = new THREE.Box3().setFromObject(pieceScene), size = box.getSize(new THREE.Vector3());
    const k = fit.headHeight / size.y; pieceScene.scale.multiplyScalar(k);
    const c = box.getCenter(new THREE.Vector3()).multiplyScalar(k); pieceScene.position.sub(c).add(new THREE.Vector3(...(fit.offset || [0, 0, 0])));
  }
  socket.add(holder);
  applyEdit(pieceScene, edit);
  (character.userData.csAttire ||= {})[slot] = { holder, piece: pieceScene, edit };
  return holder;
}

export function detach(character, slot) {
  const a = character.userData.csAttire?.[slot]; if (!a) return;
  a.holder.parent?.remove(a.holder); delete character.userData.csAttire[slot];
}

export const UNIVERSAL_PIECES = {
  bannon_mask: { slot: 'face', manifest: 'attire/bannon_mask/bannon_mask.manifest.json', editable: ['tint', 'roughness', 'metalness', 'offset', 'rotation', 'scale', 'visible'] },
};
