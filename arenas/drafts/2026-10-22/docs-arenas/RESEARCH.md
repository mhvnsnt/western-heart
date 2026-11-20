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

## Urban Reign (PS2) — stage PPKs secured, geometry format in RE
- 7 stage PPKs (stage003, 004, 020, 028, 029, 030, 031; 34MB total)
  surgically extracted 2026-10-18 via HTTP Range requests against release
  `urban-reign-iso-v1` (parsed ISO9660 → DVD000.AFS @ ISO 3063840768 →
  AFS file table → 7 contiguous PPKs @ AFS 998561792–1032468352 → single
  34MB Range fetch from `urban-reign-500m.part_ah`). No 4.1GB ISO download.
  PPKs stored at `~/workspace/_arenas-scratch/ur/ppks/` (scratch, not in repo).
- PPK container: magic `ppk\0`, data offset @ byte 8 (512 for stage PPKs).
  Sub-chunk offset table at data+48: 146 entries (stage028), 4-aligned,
  strictly increasing — header/metadata chunks only (2KB range).
- Geometry: 243 float32-dense 512B windows from data+0x1a000 (stage028).
  Values use 128.0 as separator/sentinel (not clean xyz triplets) —
  likely a Namco strip/packet format, NOT the char-PPK vertex layout.
  Full vertex/index decode is open RE work.
- Status: geometry EXISTS and is located; decode blocked on format RE.
  No real geometry wired yet. Next: identify packet headers around the
  float regions, find index buffers, reconstruct meshes.

## Tekken 7 — arenas/ exists in release, not yet pulled
- Release `tekken7-full-v1` (3.1GB, 7×500MB tar parts) contains
  `tekken7/arenas/` per its description (verified: parts aa–ac hold
  tekkenmods-docs/, tools/umodel_linux, king/, models/king-variants/;
  arenas/ is in later parts ad–ag).
- Disk at 84–85% blocked pulling the full 3.1GB this round. The arenas/
  directory is confirmed present; selective extraction is the next step
  (tar headers are scannable per-part; umodel_linux is bundled for UE4
  .uasset export).
- Status: not pulled, not wired. Next: pull parts ad–ag (or Range-scan
  for arenas/ headers), extract, convert via umodel to GLB.

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
