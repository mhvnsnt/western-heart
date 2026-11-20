# WH procedural generation + asset pipelines (`tools/procgen/`)

Owner standing order: research everything, pull open source, wire up, push green.
Research docs: `docs/research/procgen-asset-pipelines/` (7 topic docs + PULL-LOG).

## Sub-tools
| Dir | What | Pull basis | Test |
|---|---|---|---|
| `gltf-delivery/` | Web GLB pipeline: `KHR_materials_variants` attire builder, meshopt optimizer | gltfpack (MIT), glTF-Transform (MIT) | ✅ green 2026-10-16 |
| `game-score/` | Adaptive procedural score (Tone.js adapter + pure core) | Tone.js (MIT) | ✅ 21/21 node tests |
| `arena-gen/` | Seeded fighting-arena generator → `.tscn` + three.js JSON | GDQuest PCG concepts (MIT) | ✅ green |
| `textures/` | Prompt→PBR, seamless tiling, Material Maker export, CC0 fetch | Material Maker (MIT), TEXTtoPBR algos (MIT) | ✅ green |
| `usd/` | Headless Blender → USD export, WH conventions | Blender built-in (no pull) | ✅ green |

## Pipeline (teardown → playable)
```
teardown assets → USD archival (usd/) → Blender authoring
  → .glb → attire variants (gltf-delivery) → meshopt+KTX2 optimize → *.web.glb
stages: arena-gen → Material Maker / prompt-PBR textures → glTF delivery
playable build: three.js + WH adaptive score (game-score/)
```

## License honesty
Every pull's license verified via GitHub API 2026-10-16 and logged in
`docs/research/procgen-asset-pipelines/PULL-LOG.md`. Excluded-with-reason items
(MIDI-GPT non-commercial models, Melodrive cracks, HumGen3D paid assets,
GodotShaderCollection unlicensed) are documented there — not pulled.
