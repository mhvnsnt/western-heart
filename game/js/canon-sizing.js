// Runtime for game/data/canon-sizing.js. Measures the posed (skinned) stance
// height once per model and returns the root scale that makes it canon height.
import * as THREE from 'three';
import { sizingFor, STANCE_PER_CM, SCALE_CLAMP, GIRTH_CLAMP } from '../data/canon-sizing.js';

const _v = new THREE.Vector3();
export function stanceHeight(model, frame = model) {
  let lo = Infinity, hi = -Infinity;
  frame.updateMatrixWorld(true);
  const inv = new THREE.Matrix4().copy(frame.matrixWorld).invert();
  model.traverse((n) => {
    if (!n.isMesh || !n.geometry || !n.visible) return;
    const P = n.geometry.attributes.position; if (!P) return;
    const step = Math.max(1, Math.floor(P.count / 4000));
    for (let i = 0; i < P.count; i += step) {
      _v.fromBufferAttribute(P, i);
      if (n.isSkinnedMesh) n.applyBoneTransform(i, _v);
      _v.applyMatrix4(n.matrixWorld).applyMatrix4(inv);
      if (_v.y < lo) lo = _v.y; if (_v.y > hi) hi = _v.y;
    }
  });
  return hi > lo ? hi - lo : 0;
}

/** {h, w} root scale for this model key, or null when no applied canon entry. */
export function canonRootScale(modelKey, model, frame = model) {
  const e = sizingFor(modelKey);
  if (!e) return null;
  const measured = stanceHeight(model, frame);
  if (!(measured > 0.2)) return null;
  const clamp = (x, [a, b]) => Math.min(b, Math.max(a, x));
  const h = clamp((e.height_cm * STANCE_PER_CM) / measured, SCALE_CLAMP);
  const g = clamp(e.girth ?? 1, GIRTH_CLAMP);
  return { h, w: h * g, measured, entry: e };
}
