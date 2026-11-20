# render-prep — RUN THIS BEFORE ANY BLENDER RENDER OF A GLB. NO EXCEPTIONS.

**NEVER feed a raw Tripo GLB straight into Blender on this VM.** Blender 4.0.2
here has ~8 GB RAM and OOM-kills on 20 MB+ / ~1M-vert GLBs with 4096px
textures (Cain 58 MB decoded, Doc Frank 1.38M verts, Star 1M verts — all died
2026-10-19). **NEVER trust a GLB's textures without decoding them first** — a
shipped Mariposa GLB carried a color JPEG truncated by 133 bytes; it rendered
white and nobody knew until a human looked at the render. **NEVER trust
vertex data without scanning it** — PR #317 shipped Star A5 / Silvertongue A2
GLBs carrying 687 / 594 NaN vertex coordinates.

`render-prep` is the gate that catches all three, *before* the render:

```bash
# 1. validate (fail loudly, name the bad texture / verts)
python3 tools/render-prep/render-prep.py validate model.glb

# 2. build a render-safe COPY (the original is never touched)
python3 tools/render-prep/render-prep.py prep model.glb -o model.render.glb \
    --max-verts 250000 --max-texture 2048

# 3. render the copy
blender ... model.render.glb
```

## What `validate` checks

| Check | How | Catches |
|---|---|---|
| Container + structure | Pure-Python GLB parse: header/chunk integrity, buffer/bufferView/accessor bounds, index-reference integrity (glTF-Validator-equivalent structural rules) | truncated files, corrupt writers, out-of-range data |
| **Every embedded texture fully decodes** | Magic bytes vs declared type, JPEG EOI / PNG IEND tail tripwires, then a **full Pillow decode** of every scanline | the Mariposa truncated-JPEG class — reported **by texture name** |
| Vertex sanity | Declared POSITION min/max: finite, no float-max garbage (≥3e38, the PR #317 signature), within `--max-coord`; **plus a byte-level scan of the actual vertex data** (NaN/Inf counts, real bounds vs declared) whenever the data isn't codec-compressed | garbage-bounds GLBs, NaN-poisoned "improved" models |
| Blender blockers | Flags `EXT_meshopt_compression` / `KHR_draco_mesh_compression` (Blender can't import either raw) and KTX2 textures (unreliable in Blender) | silent import failures / OOM thrash |

Exit codes: `0` OK, `2` validation failed (do not render), `3` prep/tooling failed.

Meshopt note: bufferViews under `EXT_meshopt_compression` declare the
*decompressed* layout, so bounds checks skip them at validate time; `prep`
decodes first, then deep-scans the real bytes — nothing reaches Blender
unscanned.

## What `prep` does (in order)

1. Validates the input. Any failure = hard stop, no output.
2. Decodes meshopt/draco via `@gltf-transform/cli copy` (if present).
3. Deep-validates the decoded geometry bytes (NaN scan on real data).
4. Decimates to the vertex budget with **gltfpack** (meshoptimizer, `-si`
   ratio; quality-first refine pass re-runs on the *original* geometry, never
   on an already-decimated mesh). Fallback: `gltf-transform simplify`.
5. Downscales textures over `--max-texture` in pure Python (Pillow, LANCZOS,
   same format re-encode), rebuilding the GLB binary chunk.
6. Deep-validates the **final output** and refuses to write a bad copy.

Originals are never modified — `prep` errors if output path == input path.

## Tooling basis (researched 2026-10)

- **gltfpack 1.3** (meshoptimizer, Arseny Kapoulkine) — the decimation +
  optimization workhorse; native-speed, tiny memory footprint vs Blender.
  `npm i -g gltfpack` (or `npm i -g --prefix ~/.npm-global gltfpack`).
- **@gltf-transform/cli 4.x** (Don McCurdy) — meshopt/draco decode via
  `copy`, plus `inspect`/`validate`/`simplify` fallbacks. Already the house
  tool for meshopt decode. `npm i -g @gltf-transform/cli`.
- **Khronos glTF-Validator** — the spec-conformance reference; render-prep
  reimplements its structural ruleset in dependency-free Python so the gate
  runs anywhere without a Dart/Node validator binary, and adds the two
  checks the Validator does *not* do: full texture pixel decode and
  byte-level vertex NaN scans.
- **Draco / KTX2-Basis** — supported as *inputs to detect*, deliberately not
  produced: Blender 4.0 imports neither reliably enough for this pipeline.
  Output stays plain float geometry + JPEG/PNG — boring on purpose.
- **Blender headless memory practice** (pairs with this tool): run under
  `xvfb-run -a` (this VM's Blender segfaults bare `-b`), `--factory-startup`,
  render the *prepped* copy, keep Cycles tiles modest (256) and prefer
  `--max-verts 250000 --max-texture 2048` defaults on ≤8 GB RAM.

`render-prep.py check-env` reports which optional tools it can see.

## Tests

```bash
python3 tools/render-prep/test_render_prep.py
```

Synthetic GLBs (good / truncated JPEG / bad magic / ±3.4e38 garbage bounds /
NaN vertex bytes): the good one passes, every bad one fails. Real-file
evidence from the 2026-10-19/20 verification run is in the PR that landed
this tool.

## Render pipeline wiring

`~/workspace/render-work/RENDER-PREP.md` + `render_with_prep.sh` make this
the mandatory first step of the render lane: prep → validate-the-copy →
Blender. If render-prep fails, the render does not run.
