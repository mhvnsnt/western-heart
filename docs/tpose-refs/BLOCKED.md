# T-pose lane — BLOCKED fighters (2026-10-15 lane)

Per MUSE_TPOSE_SPEC: skip a broken rig and write down why. Don't hand-fix the mesh.

## diablo (heihachi-mishima source) — BLOCKED-no-usable-model
- Source dir `game-reverse-engineering/tekken7/models/heihachi-mishima/` contains only
  `browser-download-..._heihachi_mishima.rar` (10.2MB).
- The rar holds exactly 2 files: `bmost.dff` (3.5MB) + `bmost.txd` (17MB) — GTA: San Andreas
  mod formats, not FBX/GLB/blend. 7z reports "Unsupported Method" on both; extracted 0-byte.
- The dir README promises `heihachi-young-t7.blend` (Open3DLab, 8.6MB) but the file was never
  downloaded into the dir. Needs a fresh pull from Open3DLab before diablo can render.
