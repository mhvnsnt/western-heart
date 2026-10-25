// WH contextual ragdoll — cannon-es edition.
// Wiring target in repo: game/lib/ragdoll.js (drop-in; game passes its CANNON).
// Vision (user): Euphoria + Gang Beasts + Human Fall Flat + Tekken, but
// ragdoll ONLY in the moments Tekken would do it: launches, KOs, wall
// splats. Every other frame the animation drives the body.
// This is the cannon-es counterpart to the Rapier ragdoll in
// game/js/ragdoll.js (PR #1066 lane). The game picks ONE engine at
// integration time; this file does not replace or edit that file.
// Usage:
//   const rag = createRagdoll(CANNON, world, { position: [x, y, z] });
//   rag.setAnimated();            // animation drives (default)
//   rag.launch([vx, vy, vz]);     // KO / launcher: physics takes over
//   rag.sync();                   // each frame while ragdolled: returns
//                                 // { pelvis, chest, head } positions for
//                                 // the game to pose the visible skeleton
//   rag.setAnimated();            // getup: animation takes over again
export function createRagdoll(CANNON, world, opts = {}) {
  const [px, py, pz] = opts.position || [0, 1.5, 0];
  function part(y, r, mass = 5) {
    const b = new CANNON.Body({ mass, shape: new CANNON.Sphere(r) });
    b.position.set(px, y, pz); b.sleepSpeedLimit = -1; // never auto-sleep mid-KO
    world.addBody(b); return b;
  }
  const pelvis = part(py, 0.30), chest = part(py + 0.70, 0.30), head = part(py + 1.30, 0.20);
  const c1 = new CANNON.PointToPointConstraint(pelvis, new CANNON.Vec3(0, 0.30, 0), chest, new CANNON.Vec3(0, -0.30, 0));
  const c2 = new CANNON.PointToPointConstraint(chest, new CANNON.Vec3(0, 0.30, 0), head, new CANNON.Vec3(0, -0.20, 0));
  world.addConstraint(c1); world.addConstraint(c2);
  const bodies = [pelvis, chest, head];
  let ragdolled = false;
  function freeze() { for (const b of bodies) { b.velocity.setZero(); b.angularVelocity.setZero(); b.type = CANNON.Body.KINEMATIC; } }
  function unfreeze() { for (const b of bodies) { b.type = CANNON.Body.DYNAMIC; b.wakeUp(); } }
  freeze(); // start animated
  return {
    get ragdolled() { return ragdolled; },
    // Physics takes over with an impulse (launcher / KO / wall splat).
    launch(impulse) {
      unfreeze(); ragdolled = true;
      pelvis.velocity.set(impulse[0], impulse[1], impulse[2]);
      chest.velocity.set(impulse[0] * 0.9, impulse[1] * 0.9, impulse[2] * 0.9);
      head.velocity.set(impulse[0] * 0.8, impulse[1] * 0.8, impulse[2] * 0.8);
    },
    setAnimated() { freeze(); ragdolled = false; },
    step(dt) { if (ragdolled) world.step(dt); },
    sync() {
      const p = (b) => [b.position.x, b.position.y, b.position.z];
      return { pelvis: p(pelvis), chest: p(chest), head: p(head) };
    },
  };
}
