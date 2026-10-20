# ArmorPaint 1.0 — open-source Substance Painter alternative

GPU-accelerated 3D texture painting: paint directly on the model with
layers, masks, procedural nodes, and path-traced viewport. ArmorPaint 1.0
(Sept 2026) added mesh modifiers (Decimate/Smooth/Bevel/Subdivide), a UV
editor, timeline + skinning animation playback, and **Neural Nodes** —
including a local **Image-to-PBR** node (base color, AO, roughness, normal,
height from a photo) that runs on-device.

**License: source is free** (open source — verify the LICENSE file in the
repo at build time). Prebuilt binaries are $19; **building from source is
free** — that's the path below.

- Source: https://github.com/armory3d/armorpaint
- Site/manual: https://armorpaint.org

## Free source build (Linux)

```bash
git clone https://github.com/armory3d/armorpaint && cd armorpaint/paint
../base/make          # generates the build files (needs: git, clang, standard C toolchain)
# then build with the generated project files (see armorpaint.org/manual)
```

Needs a GPU for the path-traced viewport (Vulkan/Direct3D12/Metal/WebGPU).
On a headless VM: build on any GPU box, paint there, export PNGs.

## WH workflow

1. Import the fighter GLB into ArmorPaint.
2. Paint layers (base color, roughness variation, edge wear via nodes),
   or run the **Neural → Image to PBR** node on a reference photo for
   instant maps.
3. Export maps (PNG/JPEG/EXR, up to 32-bit).
4. Wire into the GLB with `tools/texture-pipe/apply_pbr_set.py`
   (manifest.json points at the exported PNGs).

## Limits (honest)

- No painting across UDIMs (deal-breaker for film pipelines; fine for our
  single-UV game fighters).
- 1.0 is fresh (Sept 2026) — validate on one fighter before committing the
  whole roster to it.
- Neural nodes need model downloads (FLUX 2 klein 4GB / DA3MONO 6GB /
  Real-ESRGAN 1GB VRAM) — Kaggle/Colab GPU lanes can host them.

## Why not just Substance?

Adobe Substance 3D Painter is the industry standard and it's **paid**.
ArmorPaint is the open equivalent. Per the NO-HAND-TOOLING law we wire the
real system — this is it, built free from source.
