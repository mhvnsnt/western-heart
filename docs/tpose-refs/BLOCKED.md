# T-pose lane — BLOCKED fighters (2026-10-15 lane)

Per MUSE_TPOSE_SPEC: skip a broken rig and write down why. Don't hand-fix the mesh.

## Duplicate / non-alt sources (not rendered as separate attires)
- kinpo p2 (asuka-alt): `asuka-alt/1L4OIS1UE1EVR6XXD54H6QH96.fbx` is byte-identical
  (md5 467634849878396c1122d25299274841) to `asuka-kazama`'s FBX; renders are pixel-identical.
  Not a real alt — kinpo ships p1 only until a genuinely different Asuka attire is sourced.
- king-tyrant p2 (eddy-gordo-capoeira): entire dir is a byte-identical duplicate of `eddy-gordo`
  (same FBX md5 5520630a3d66be85053b2506683934ef, `diff -rq` clean). Not a real alt —
  king-tyrant ships p1 only.

## diablo (heihachi-mishima source) — BLOCKED-no-usable-model
- Source dir `game-reverse-engineering/tekken7/models/heihachi-mishima/` contains only
  `browser-download-..._heihachi_mishima.rar` (10.2MB).
- The rar holds exactly 2 files: `bmost.dff` (3.5MB) + `bmost.txd` (17MB) — GTA: San Andreas
  mod formats, not FBX/GLB/blend. 7z reports "Unsupported Method" on both; extracted 0-byte.
- The dir README promises `heihachi-young-t7.blend` (Open3DLab, 8.6MB) but the file was never
  downloaded into the dir. Needs a fresh pull from Open3DLab before diablo can render.
- zui p3 (steve-fox-alt): entire dir is a byte-identical duplicate of `steve-fox`
  (same FBX md5 60c8842952b012385c9c4a2405dbbf47, `diff -rq` clean). Not a real alt —
  zui ships p2 only.
- saku-ra p1-alt (xiaoyu/YKV2HEPB9YHUGOB7GDW054BUL.fbx): baked victory pose (peace signs,
  knee up), zero armatures — cannot T-pose via skeleton; mesh editing forbidden. BLOCKED-baked-pose.
- saku-ra p2 (xiaoyu-pink-dress): FBX byte-identical to xiaoyu's and renders pixel-identical
  (both are the pink "bonbon/china" dress). Not a real alt — saku-ra ships the single T-posed
  attire as p1.
- saku-ra p3 (xiaoyu-t8): rar contains only PhoenixDress.obj which extracted 0-byte
  (extraction errors). BLOCKED-no-usable-model.
