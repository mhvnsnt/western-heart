# Stage 5 — WEB OPTIMIZE

> **ALL AGENTS — READ THIS FIRST.**
> This stage rewrites geometry aggressively (quantization, meshopt codecs).
> Keep the stage-4 output — the web GLBs are a **delivery format**, not an
> archive. If the game build ever needs to re-optimize with different settings,
> re-run from stage 4, don't stack optimizations on already-optimized files.

## What it does

For every GLB in the input dir:

1. **gltfpack `-cc`** — meshopt compression (vertex/index buffer codecs,
   quantization, cache optimization). Typically 3–8× smaller.
2. **optional `--ktx2`** — gltf-transform `etc1s`: textures to KTX2/Basis.

Per-file before/after byte counts print to stdout — that's the proof.

## Quick start

```bash
./webopt.sh install
./webopt.sh optimize /path/to/work/s4 /path/to/work/s5 --ktx2
```

Options: `--ktx2`, `--no-meshopt` (copy + report only), `--force`.

## Loader requirements

`-cc` output needs `EXT_meshopt_compression`: three.js r122+ (call
`GLTFLoader.setMeshoptDecoder`) or Babylon.js 5.0+. The game's
`AssetManager`/viewer already handles this — if it doesn't, that's a game
bug, not a pipeline bug.

## Tool versions

- gltfpack from meshoptimizer `v1.3` release (`gltfpack-ubuntu.zip`)
- `@gltf-transform/cli@4.1.1` (matches the 4.1.x line pinned in
  `tools/setup/setup_toolchain.sh`)
