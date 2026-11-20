// WH fight VFX wiring — three.quarks (MIT) hit bursts + three-simplecloth
// (MIT) cape/cloth. Wiring target in repo: game/lib/vfx.js.
// RUNTIME NOTE: these libraries render through Three.js in the browser.
// Node import was proven (2026-10-24); visual tuning must be done by
// playing the live build (phone portrait), per project law — this file is
// the wiring, not a claim that the look is final.
// Hit-burst presets, one per button. Call spawnHitBurst(scene, button, pos)
// on a confirmed hit; intensity scales with move damage in game code.
//   LP1 = Left Punch (quick jab spark), RP2 = Right Punch (heavy spark),
//   LK3 = Left Kick (low sweep dust), RK4 = Right Kick (high launch burst).
export const HIT_BURST_PRESETS = {
  LP1: { color: 0xffe08a, count: 40, speed: 3.0, size: 0.12, life: 0.35 },
  RP2: { color: 0xffb347, count: 90, speed: 5.0, size: 0.18, life: 0.5 },
  LK3: { color: 0xcbb89d, count: 60, speed: 2.5, size: 0.15, life: 0.45 },
  RK4: { color: 0xff7a45, count: 120, speed: 6.5, size: 0.22, life: 0.6 },
};
// three.quarks wiring sketch (game fills in its own BatchedRenderer setup):
//   import { BatchedRenderer, ParticleSystem, ... } from 'three.quarks';
//   const renderer = new BatchedRenderer(scene); // one per scene
//   const burst = new ParticleSystem({ ...preset mapped to quarks behaviours });
//   burst.emitter.position.copy(hitPos); burst.play();
// three-simplecloth cape wiring sketch (WebGPU renderer only):
//   import { SimpleCloth } from 'three-simplecloth';
//   // Vertex-paint the cape mesh RED where it should drape (see
//   // three-simplecloth README: red channel = cloth mask, skinned mesh).
//   const cloth = SimpleCloth.onSkinnedMesh(capeMesh, webgpuRenderer);
//   // each frame: cloth.update(delta);
// GPU NOTE: both systems are GPU-rendered (instanced quads / WebGPU
// compute). On the player's phone they run on the phone GPU; on Kaggle
// they are NOT benchmarked — Kaggle T4s are for the offline pipeline
// (see tools/gpu/). Do not claim Kaggle numbers for runtime VFX.
export function presetFor(button) {
  const p = HIT_BURST_PRESETS[button];
  if (!p) throw new Error('unknown button: ' + button + ' (use LP1/RP2/LK3/RK4)');
  return p;
}
