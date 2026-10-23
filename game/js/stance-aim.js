/* Bind-pose-independent stance retarget ("aim" retarget).
   Fallback for rigs whose Tekken bank stance fails the select fit
   gates (tools/portraits/POSE-BLOCKERS.json). Source: CMU mocap
   subject 14 trial 01 (boxing guard), exported by
   tools/anim-retarget/cmu_stance_export.py to
   data/stances/cmu-guard.json as per-bone aim directions in the
   body frame (+X left, +Y up, +Z forward). Each frame every mapped
   bone is rotated so its bone->child segment points along the mocap
   direction, so the result never depends on the target's bind pose
   (T-pose, A-pose, foreign roll axes). Works on any rig that exposes
   the canonical bone names on inst.bones (assets.js). */
let _data = null;
export async function loadGuardStance() {
  if (_data) return _data;
  const r = await fetch('data/stances/cmu-guard.json');
  _data = r.ok ? await r.json() : null;
  return _data;
}
const CHILD = {
  Neck: 'Head', LeftShoulder: 'LeftArm', LeftArm: 'LeftForeArm', LeftForeArm: 'LeftHand',
  RightShoulder: 'RightArm', RightArm: 'RightForeArm', RightForeArm: 'RightHand',
  LeftUpLeg: 'LeftLeg', LeftLeg: 'LeftFoot', LeftFoot: 'LeftToeBase',
  RightUpLeg: 'RightLeg', RightLeg: 'RightFoot', RightFoot: 'RightToeBase',
};
const ORDER = ['Neck', 'LeftShoulder', 'LeftArm', 'LeftForeArm', 'RightShoulder', 'RightArm', 'RightForeArm',
  'LeftUpLeg', 'LeftLeg', 'LeftFoot', 'RightUpLeg', 'RightLeg', 'RightFoot'];

// Rig aliases: Tekken-native rigs (Hip, L_Arm, L_Toe ... e.g. dio) and the
// descriptive rig on mariposa-monarch ("arm left shoulder 2", "leg left knee").
const DESC = { Hips: 'root hips', Neck: 'head neck lower', Head: 'head neck upper' };
for (const [S, s] of [['Left', 'left'], ['Right', 'right']]) Object.assign(DESC, {
  [S + 'Shoulder']: `arm ${s} shoulder 1`, [S + 'Arm']: `arm ${s} shoulder 2`, [S + 'ForeArm']: `arm ${s} elbow`,
  [S + 'Hand']: `arm ${s} wrist`, [S + 'UpLeg']: `leg ${s} thigh`, [S + 'Leg']: `leg ${s} knee`,
  [S + 'Foot']: `leg ${s} ankle`, [S + 'ToeBase']: `leg ${s} toes`,
});
function withAliases(bones) {
  if (bones.Hips && bones.LeftArm) return bones;
  const out = { ...bones };
  for (const [k, b] of Object.entries(bones)) {
    const m = /^([LR])_(.+)$/.exec(k);
    if (m) { const n = (m[1] === 'L' ? 'Left' : 'Right') + (m[2] === 'Toe' ? 'ToeBase' : m[2]); out[n] = out[n] || b; }
  }
  if (bones.Hip && !out.Hips) out.Hips = bones.Hip;
  for (const [n, d] of Object.entries(DESC)) { const b = bones[d] || bones[d.replace(/ /g, '_')]; if (!out[n] && b) out[n] = b; }
  return out;
}

export function createAimStance(THREE, model, bones, data) {
  bones = bones && withAliases(bones);
  if (!data || !bones || !bones.Hips || !bones.LeftUpLeg || !bones.RightUpLeg || !bones.LeftArm || !bones.RightArm) return null;
  const used = ['Hips', ...ORDER].filter(n => bones[n] && (n === 'Hips' || bones[CHILD[n]]));
  const bind = new Map(used.map(n => [n, bones[n].quaternion.clone()]));
  const v = (x, y, z) => new THREE.Vector3(x, y, z);
  const wp = (b) => b.getWorldPosition(new THREE.Vector3());
  // body frame of the model at bind: left = LeftUpLeg - RightUpLeg (horizontal), up = +Y
  model.updateWorldMatrix(true, true);
  const L0 = wp(bones.LeftUpLeg).sub(wp(bones.RightUpLeg)); L0.y = 0; L0.normalize();
  const Y = v(0, 1, 0), Z0 = new THREE.Vector3().crossVectors(L0, Y).normalize();
  const modelQ0 = model.quaternion.clone();
  const toWorld = (d) => {
    // body-frame dir -> world, following the model's current yaw relative to bind
    const w = v(0, 0, 0).addScaledVector(L0, d[0]).addScaledVector(Y, d[1]).addScaledVector(Z0, d[2]);
    const dq = model.quaternion.clone().multiply(modelQ0.clone().invert());
    return w.applyQuaternion(dq).normalize();
  };
  const tmpQ = new THREE.Quaternion(), pq = new THREE.Quaternion();
  function rotWorld(bone, q) {
    // bone.world' = q * bone.world  ->  local' = parentWorld^-1 * q * parentWorld * local
    bone.parent.getWorldQuaternion(pq);
    tmpQ.copy(pq).invert().multiply(q).multiply(pq);
    bone.quaternion.premultiply(tmpQ);
    bone.updateWorldMatrix(false, true);
  }
  const F = data.dirs.Hips.length;
  return {
    apply(t) {
      // ping-pong so the 2 s clip loops without a pop
      let f = (t * data.fps) % (2 * F - 2); if (f >= F) f = 2 * F - 2 - f;
      const i = Math.floor(f), k = f - i, j = Math.min(F - 1, i + 1);
      const at = (n) => { const a = data.dirs[n][i], b = data.dirs[n][j]; return a.map((x, c) => x + (b[c] - x) * k); };
      for (const n of used) bones[n].quaternion.copy(bind.get(n));
      model.updateWorldMatrix(true, true);
      // hips: align (left, up) frame
      const h = at('Hips');
      const dl = toWorld(h.slice(0, 3)), du = toWorld(h.slice(3, 6));
      const cl = wp(bones.LeftUpLeg).sub(wp(bones.RightUpLeg)).normalize();
      const head = bones.Head || bones.Neck;
      const cu = head ? wp(head).sub(wp(bones.Hips)).normalize() : v(0, 1, 0).applyQuaternion(model.quaternion);
      const mk = (l, u) => { const z = new THREE.Vector3().crossVectors(l, u).normalize(); const uu = new THREE.Vector3().crossVectors(z, l).normalize(); return new THREE.Quaternion().setFromRotationMatrix(new THREE.Matrix4().makeBasis(l, uu, z)); };
      const sp = data.dirs.Spine ? toWorld(at('Spine')) : du;
      const qh = mk(dl, sp).multiply(mk(cl, cu).invert());
      rotWorld(bones.Hips, qh);
      for (const n of ORDER) {
        const b = bones[n], c = b && bones[CHILD[n]];
        if (!b || !c || !data.dirs[n]) continue;
        const cur = wp(c).sub(wp(b));
        if (cur.lengthSq() < 1e-10) continue;
        rotWorld(b, new THREE.Quaternion().setFromUnitVectors(cur.normalize(), toWorld(at(n))));
      }
    },
  };
}
