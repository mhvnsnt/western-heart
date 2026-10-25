# WH asset pipeline (`tools/assets/`)

One reusable pipeline for every GLB the game ships (fighters, attires, stages, props).
Goal: fast loads with **nothing cut**.

```bash
cd tools/assets && npm i                      # MIT deps, node_modules not committed
node wh_asset_pipeline.mjs IN.glb OUT.web.glb # one file (default: meshopt + WebP)
node wh_asset_pipeline.mjs --dir ../../game/assets/models --out-dir /tmp/web --report /tmp/web/report.json
```

| option | default | runtime support today |
|---|---|---|
| `--geo meshopt` | yes | `game/js/assets.js`, `customization-consumer.js`, `ui-wh/cards.js` already call `setMeshoptDecoder` |
| `--geo draco` | no | needs `DRACOLoader` + decoder wasm vendored in `game/vendor/addons/libs/` (not there yet) |
| `--tex webp` | yes | native in three.js (`EXT_texture_webp`), no decoder |
| `--tex ktx2` | no | needs `toktx` + `KTX2Loader`/basis transcoder vendored (not there yet) |
| `--max-tex N` | off | only downsizes textures above N px; off = full resolution |

**No-cut gate:** the script counts nodes, primitives, vertices, triangles, morph targets, skins,
joints, animations, channels, materials and node names before and after, and exits 1 if any drop.
Originals are never overwritten (`--dir` requires `--out-dir`). `dedup` may merge byte-identical
textures/meshes, and quantization splits one skin into per-mesh skins (inverse-bind matrices get
the dequantize transform) — both are expected and are not cuts.

## Measured (2026-10-23, main @ c8ff565, scratch copies)
| file | before | after |
|---|---|---|
| game/assets/models/awa-pop.glb | 0.41 MB | 0.25 MB |
| game/assets/models/baek.glb | 0.39 MB | 0.28 MB |
| game/assets/models/bruno.glb | 41.59 MB | 11.26 MB |
| total | 42.4 MB | 11.8 MB (28%) |

All three: no-cut gate OK (same vertex/triangle/joint-bearing/node-name counts).

## Lazy loading
The game already loads fighters on demand through the shared loader in `game/js/assets.js`
(`_sharedGLTFLoader`, timeouts via `_timeoutSignal`), and #852 made the loading bar track real
bytes. Smaller GLBs from this pipeline shrink exactly those on-demand fetches.
Next step (separate PR, needs a visual check per fighter): write `*.web.glb` next to the
originals and point the roster at them, keeping the originals as the source of truth.

## Deploy speed fix (`tools/deploy/build_pages.py`)
In the shared blob:none clone, `git ls-tree -l` lazily downloaded every blob one by one
(>10 min, never finished). Sizes now come from local objects (`GIT_NO_LAZY_FETCH`) plus the
GitHub trees API, and all runtime text blobs are prefetched in one batched fetch.
Dry run: >600 s → 9.8 s. Real deploy (`--onto origin/gh-pages --push`): 28 s.
