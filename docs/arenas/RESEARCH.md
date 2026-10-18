# Western Heart — Arena Source Research (Lane E / ARENAS, Round 2)

Owner order: "texture the T3 arenas AND add more — DOA arenas, Urban Reign
arenas, TTT2, T6, T7 arenas. Not just T3."

Per-game format findings (all verified against the teardown docs on
origin/main, 2026-10-18). "Real geometry" = decoded from game files by a
teardown lane; only that counts as wired — no hand-tooled stand-ins.

## Tekken 3 (PSX) — DONE: real textured arenas
- Panorama TMD records: BNS 56–70 (geometry + per-corner texture keys
  `<cba>_<tsb>` + per-packet RGB). Floor/texture ARCs: BNS 36–50.
- ARC = chain of standard PSX TIMs, each carrying its own VRAM destination
  (image DX/DY, CLUT x/y). Blitting in order rebuilds the 1024×512
  index-VRAM exactly as the game uploaded it.
- All 15 stages' panoramas use 4-bit textures (TSB mode bits = 0, verified
  on all keys). UVs are texel offsets from the page origin; CLUT from CBA.
- Pipeline: `docs/arenas/t3-texture-pipeline/build_t3_atlas.py` → per-stage
  atlas PNG + regenerated OBJ (atlas-space UVs, TMD vertex colors).
- Wired in `game/js/stages.js` (`buildT3Retro` loads `stg_<l>_atlas.png`;
  tint fallback preserved). Screenshot-verified in-game.

## Dead or Alive 4 (Xbox 360) — BLOCKED: stage exports broken
- DOA4 lane decoded the XPR2 VBUF/IBUF format (`teardown/dead-or-alive-4/
  IBUF-DECODED.md`, 2026-10-18): 20-byte big-endian verts (float3 pos +
  float2 uv), u16 triangle strips with 0xFFFF restarts.
- 18 stage meshes triangulated: `teardown/dead-or-alive-4/models/
  vertex-buffers/stg_model_000..017_*.glb` (+ `stg_manifest.json`).
- Lane E verification 2026-10-18: the stage GLBs are NOT yet usable —
  (1) every model has the identical bbox max (15.894373893737793 on all
  axes), i.e. positions are not in world space (normalized grid or
  missing instance transforms); (2) the GLB binaries are malformed
  (GLTFLoader: "Invalid typed array length" — buffer/byteLength
  mismatch). Character GLBs from the same lane verify clean; stage
  exports need a DOA4-lane fix. No materials/textures yet either
  (TX2D decode is the DOA4 lane's open item).
- Status: blocked on DOA4 lane (world-space stage meshes + valid GLBs +
  TX2D textures). Coordinate, don't duplicate. NOT wired this round.

## Urban Reign (PS2) — stage geometry NOT yet decoded
- 7 stage PPKs extracted (34MB). PPK container format understood
  (`teardown/urban-reign/PPK-FORMAT.md`); character geometry decoded
  (`PPK-GEOMETRY.md`), but the *stage* PPKs' inner Namco geometry is
  explicitly "not yet decoded" (ARENA-INVENTORY.md).
- Status: blocked on stage-PPK geometry RE. No real geometry to wire yet.

## Tekken Tag Tournament 2 — stage data opaque
- 29 battle stages + Fight Lab documented from public data (Tekkenpedia /
  TekkenMods / OST): `teardown/tekken-tag-tournament-2/STAGES.md` with
  internal stage IDs (stg00–stg48).
- Geometry lives in the Data chunks of release `ttt2-7z-v1`; chunks are
  opaque until STFS decryption is wired. No real geometry to wire yet.

## Tekken 6 (PSP) — encrypted
- Sector cipher fully reversed, EBOOT decrypted; bulk DATA401 transform
  still under analysis (`teardown/tekken6/TEARDOWN.md`). Models/textures/
  stages pending the decrypt breakthrough. No real geometry to wire yet.

## Tekken 7 — geometry never acquired
- 34 stages mapped (stage ID table); full game is 47GB, never acquired
  (`teardown/tekken7/`). No real geometry to wire yet.
- Note: T7 stage *textures* live under `TekkenGame/Stages/stgXX/...` per
  the Tekken7 PC modding guides — relevant once geometry exists.

## Collision / gameplay
All arenas keep the standard `dims` contract: `wallDistance: 8.4`
(fighters clamp at ±8.4), spawns p1 −3.5 / p2 +3.5, so any wired arena
is playable with Tekken 1/2/3/4 inputs regardless of source game.
