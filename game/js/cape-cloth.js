/* ============================================================
   WESTERN HEART — Cape cloth upgrade layer (E28)
   Existing solvers stay untouched: game/js/cloth-hair.js (XPBD
   sheet/hair), game/js/springbones.js (VRM-style spring chains),
   game/js/softbody.js. This module is the CAPE-JONES-CAPE
   configuration + a dependency-free chain solver the caller can
   use for the cape, so the cape gets its own tuning instead of
   sharing breast/hair defaults:
     • anchor at the neck/shoulders (cape top), free hem;
     • stiffness FALLS toward the hem (top holds shape, hem flows);
     • gravity + wind response; hem never penetrates the torso
       sphere (analytic collider, same approach as cloth-hair.js).
   The springbones.js call site (documented in the lane doc) is:
   build a SpringChain over the cape bones with capeChainParams()
   per-joint values. This file does not import THREE, so its math
   is Node-testable; the THREE binding lives in springbones.js.
   ============================================================ */

// Per-joint spring params for a cape chain of `joints` joints,
// root (neck) -> tip (hem). Stiffness falls root->tip, drag rises
// slightly (hem settles instead of whipping).
export function capeChainParams(joints) {
  const out = [];
  for (let i = 0; i < joints; i++) {
    const t = joints <= 1 ? 0 : i / (joints - 1);
    out.push({
      joint: i,
      stiffness: 0.95 - t * 0.45, // 0.95 at neck -> 0.50 at hem
      dragForce: 0.25 + t * 0.25, // 0.25 -> 0.50
      gravityPower: 0.6,
      hitRadius: 0.06,
    });
  }
  return out;
}

// Pure verlet chain step (dependency-free): points = [[x,y,z]...],
// prev = previous positions, restLengths per segment, anchorIndex
// stays fixed (neck attachment). Returns new positions.
export function stepCapeChain(points, prev, restLengths, { gravity = -9.81, dt = 1 / 60, damping = 0.98, wind = [0, 0, 0], torsoSphere = null } = {}) {
  const next = points.map((p, i) => (i === 0 ? [...p] : [
    p[0] + (p[0] - prev[i][0]) * damping + wind[0] * dt * dt,
    p[1] + (p[1] - prev[i][1]) * damping + gravity * dt * dt + wind[1] * dt * dt,
    p[2] + (p[2] - prev[i][2]) * damping + wind[2] * dt * dt,
  ]));
  // Constraint passes: hold segment lengths, keep anchor fixed.
  for (let pass = 0; pass < 3; pass++) {
    for (let i = 1; i < next.length; i++) {
      const a = next[i - 1], b = next[i];
      const d = [b[0] - a[0], b[1] - a[1], b[2] - a[2]];
      const len = Math.hypot(...d) || 1;
      const diff = (len - restLengths[i - 1]) / len;
      if (i - 1 === 0) { // anchor fixed: move only the free end
        b[0] -= d[0] * diff; b[1] -= d[1] * diff; b[2] -= d[2] * diff;
      } else {
        for (let c = 0; c < 3; c++) { a[c] += d[c] * diff * 0.5; b[c] -= d[c] * diff * 0.5; }
      }
    }
  }
  // Torso collision: push points out of the torso sphere.
  if (torsoSphere) {
    const [cx, cy, cz, r] = torsoSphere;
    for (let i = 1; i < next.length; i++) {
      const p = next[i];
      const d = [p[0] - cx, p[1] - cy, p[2] - cz];
      const len = Math.hypot(...d);
      if (len < r && len > 0) {
        for (let c = 0; c < 3; c++) p[c] = [cx, cy, cz][c] + (d[c] / len) * r;
      }
    }
  }
  return next;
}
