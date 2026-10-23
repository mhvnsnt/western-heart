# tools/gltfpack — meshoptimizer's gltfpack (export/optimize)

gltfpack (github.com/zeux/meshoptimizer, MIT) is the mesh/GLB optimizer in
the suite's EXPORT chain: quantize, compress (meshopt), and slim exported
fighters for the game.

## Place in the pipeline

```
EXPORT (unified EXPORT panel)
  Blender batch cleanup -> glTF-Transform -> gltfpack -> game-ready GLB
```

## Fetch-on-demand (DISK RULES)

```bash
bash tools/gltfpack/fetch-gltfpack.sh [dest]   # default: tools/gltfpack/vendor
```

Builds gltfpack from the pinned meshoptimizer commit (or downloads the
pinned release binary). Re-running is a no-op when present. Never committed.

## Suite wiring

EXPORT panel → "Optimize with gltfpack" submits
`{"tool":"gltfpack","params":{"in":"...glb"},"out":"...-opt.glb"}` to the
job queue; the runner shells to the fetched binary with sane game defaults
(`-cc -tc`), reports input/output sizes in the status log.
