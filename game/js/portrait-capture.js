/* Portrait capture (owner t133u: no wrong-model / T-posed select portraits).
   Renders each fighter's ATTIRE-1 model (attires.js ladder: owner's own
   models first) through the SAME PreviewPane the select screen uses, so
   the portrait shows the fighter in its own moveset-bank stance clip
   (t3anims retarget + fit gates). Driven by tools/portraits/capture.mjs,
   which writes game/assets/portraits/<id>.png + portraits-manifest.json. */
import * as THREE from 'three';
import { PreviewPane } from './select-screen.js';
import { ROSTER } from './characters.js';
import { attiresFor } from './attires.js';
import { bankIdFor } from './fighter.js';
import { getMovesetInfo } from './movesets.js';

const pane = new PreviewPane(document.getElementById('c'), 'p1');
pane.baseRotY = 0.25;

function armDropDeg(inst, side) {
  const b = inst.bones || {};
  const a = b[side + 'Arm'], f = b[side + 'ForeArm'];
  if (!a || !f) return null;
  const pa = a.getWorldPosition(new THREE.Vector3()), pf = f.getWorldPosition(new THREE.Vector3());
  const d = pf.sub(pa).normalize();
  return Math.round(THREE.MathUtils.radToDeg(Math.acos(Math.max(-1, Math.min(1, -d.y)))));
}

window.capture = async (id) => {
  const c = ROSTER.find(r => r.id === id);
  if (!c) return { id, error: 'not in roster' };
  const model = attiresFor(c)[0].model;
  const ok = await pane.show(c, model);
  if (!ok) return { id, model, error: 'model failed to load' };
  if (pane.mixer) for (let i = 0; i < 12; i++) pane.mixer.update(1 / 30);
  pane.model.updateWorldMatrix(true, true);
  let bones = 0; pane.model.traverse(o => { if (o.isBone) bones++; });
  const inst = { bones: {} };
  pane.model.traverse(o => { if (o.isBone) inst.bones[o.name.replace(/^mixamorig:?/, '')] = o; });
  pane._resize();
  // T8 grid cards are face art (T8-GRID-DECODE §3): frame head+shoulders.
  const B = inst.bones, head = B.Head, hips = B.Hips;
  let framed = false;
  if (head && hips) {
    const hp = head.getWorldPosition(new THREE.Vector3()), wp = hips.getWorldPosition(new THREE.Vector3());
    const torso = Math.max(0.2, hp.distanceTo(wp)) * 0.62;
    const cy = hp.y + torso * 0.05;
    const dist = (torso * 1.15) / Math.tan(THREE.MathUtils.degToRad(pane.camera.fov / 2));
    pane.camera.aspect = 1; pane.camera.updateProjectionMatrix();
    pane.camera.position.set(hp.x + dist * 0.18, cy + torso * 0.08, hp.z + dist);
    pane.camera.lookAt(hp.x, cy - torso * 0.12, hp.z);
    framed = true;
  }
  if (!framed) { // unrigged GLB: frame the top quarter of its bounds
    const bb = new THREE.Box3().setFromObject(pane.model), sz = bb.getSize(new THREE.Vector3());
    const cy = bb.max.y - sz.y * 0.13, hgt = sz.y * 0.16;
    const dist = hgt / Math.tan(THREE.MathUtils.degToRad(pane.camera.fov / 2));
    const cx = (bb.min.x + bb.max.x) / 2, cz = (bb.min.z + bb.max.z) / 2;
    pane.camera.aspect = 1; pane.camera.updateProjectionMatrix();
    pane.camera.position.set(cx, cy, cz + sz.z / 2 + dist); pane.camera.lookAt(cx, cy, cz);
  }
  pane.renderer.render(pane.scene, pane.camera);
  const png = pane.canvas.toDataURL('image/png');
  return {
    id, model, bones, stance: pane.hasStance, framed,
    bank: bankIdFor(c.id, getMovesetInfo(c.id) ? c.id : (c.moveset || c.id)) || null,
    armDeg: { L: armDropDeg(inst, 'Left'), R: armDropDeg(inst, 'Right') }, png,
  };
};
window.rosterIds = () => ROSTER.map(r => r.id);
window.ready = true;
