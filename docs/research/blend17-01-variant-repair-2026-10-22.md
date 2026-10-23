# BLENDER17-01 Variant Repair — Research Report (2026-10-22)

Worker 75, SMUTBASE INTAKE REPAIR round. Owner directive: "get the files to open."

## The problem

Four SmutBase intake models arrived as files that no stock Blender would open:

| Character (WH name) | Intake model | Symptom |
|---|---|---|
| Tobi | Mirko (`mirkoIK.blend`, in-repo `roster/miruko/intake/miruko IK/`) | zstd stream mislabeled `.blend` |
| Chatur | Rahkasa (four-armed Oversoul model) | `BLENDER17-01` header after decompress |
| Ryusan | Mina Ashido | `BLENDER17-01` header after decompress |
| Birodo | Lily (donor body) | `BLENDER17-01` header after decompress |

Two more intake models (Cydney/Jotei, Vixen/Menajerii) carry **standard** Blender
4.02 headers and open natively — they are not affected by this issue.

## What the files actually are (reverse-engineered 2026-10-22)

Three layers, outside → in:

1. **zstd stream** (magic `28 B5 2F FD`), mislabeled with a `.blend` extension.
   Decompresses with stock zstandard (single-frame streams seen so far; the
   repair tool uses a streaming reader so multi-frame also works).
2. **"BLENDER17-01" variant container:**
   - 12-byte file header: `BLENDER17-01` (bytes 7–11 are mangled — NOT valid
     Blender pointer-size/endianness/version fields).
   - 5-byte marker: `v0500` / `v0501` (variant revision tag).
   - 32-byte block headers: `code(4), sdna_index(4), ptr(8), size(4), unk(4),
     count(4), pad(4)` — vs the standard 24-byte
     `code(4), size(4), ptr(8), sdna_index(4), count(4)`.
   - Verified by walking the blocks (`REND → TEST → GLOB → WM → DATA … ENDB`);
     `sdna_index` matches vanilla Blender (`REND=0`, `TEST=0`, `GLOB=171`), so
     the embedded **SDNA/DNA block is intact and standard** — no DNA
     reconstruction is needed.
3. **A Blender 4.5.x scene.** `FileGlobal.minversion=405, minsubversion=85`.

## Approaches tried

| # | Approach | Result |
|---|---|---|
| 1 | Patch 12-byte header to `BLENDER-v404`, keep rest | ❌ "Missing DNA block" in 4.0.2 — block headers are 32-byte, parser desyncs immediately |
| 2 | `blend17_to_standard.py`: rewrite header to `BLENDER-v402` + convert every 32-byte block header to standard 24-byte layout + patch `GLOB` minversion 405/85 → 402/0 | ✅ produces a structurally valid `.blend` |
| 3 | Open repaired file in **Blender 4.0.2** | ❌ "The file was saved by a newer version, open it with Blender 4.2 (sub 0) or later" — the DNA contains 4.2+-era structs; **no header patch can fix this**, it is expected version gating, not corruption |
| 4 | Open repaired file in **Blender 4.5.3** | ✅ all four files open; object/mesh/armature counts verified (see table) |
| 5 | Blender 2.x/3.x | ❌ not attempted beyond reasoning — strictly older than 4.0.2, guaranteed to fail harder on 4.5-era DNA |
| 6 | Manual DNA block reconstruction | ❌ unnecessary — the SDNA block survives the variant container intact (sdna_index values match vanilla) |
| 7 | Check for stripped zstd frames/headers | ✅ streaming decompress handles it; single-frame streams confirmed, no missing data (decompressed sizes match the known-good local copies) |
| 8 | Fluid Painter / NaughTyRig Blender setups | ❌ not applicable — they are addons, not file-format repair tools |

**Conclusion / the "way" the owner asked for:** the 17-01 variant is a
*container* problem, not a *data* problem. Convert the container
(`tools/blend17-repair/blend17_to_standard.py`, which also auto-decompresses
the zstd layer), then **open the result with Blender ≥ 4.2** (4.5.3 on the VM
at `~/workspace/tools/blender/blender-4.5.3-linux-x64/blender`). Blender 4.0.2
can never open these files — they were authored in 4.5.

## Open-test results (Blender 4.5.3, headless)

| File | Objects | Meshes | Armatures | Verts | Status |
|---|---|---|---|---|---|
| `mirkoIK_std_fromrepo.blend` (Tobi, via git blob API `16032bad…`) | — | — | — | — | ✅ opened, T-pose rendered |
| `rahkasa_std.blend` (**Chatur**) | 216 | 211 | 2 | 47,612 | ✅ |
| `Mina Ashido rigify_std.blend` (Ryusan) | 149 | 144 | 2 | 43,073 | ✅ |
| `lily_std.blend` (Birodo) | 169 | 159 | 2 | 665,960 | ✅ |
| `Cydney Sweeny.blend` (Jotei) | standard header | — | — | — | ✅ native open, GLB exported |
| `Vixen (Commission).blend` (Menajerii) | standard header | — | — | — | ✅ native open, GLB exported |

## GLB export findings (Cydney/Jotei, Vixen/Menajerii)

`tools` used: `worker75/export_glb.py` (headless Blender 4.5.3, glTF exporter).

1. **Bump maps mislabeled as normal maps → black skin.** Daz-sourced materials
   plug grayscale *bump/height* maps (e.g. `TorsoB_1002`, `Cindy_Torso` "B"
   suffix = bump) into `Bump → Normal` node chains. The glTF exporter writes
   these as tangent-space `normalTexture`s; mid-gray (0.5,0.5,0.5) decodes to a
   near-zero normal → lighting collapses → skin renders near-black. Verified by
   A/B render: with normal links present the body is black; with them removed
   the skin is correct. **Fix:** strip `BUMP → Normal` and `NORMAL_MAP →
   Normal` links on the Principled BSDF before export (27 links stripped for
   Cydney, 55 for Vixen). Base-color/roughness/metallic maps are unaffected.
2. **Alternate-outfit collections OOM the 7.7 GB VM.** Enabling *every*
   collection (or linking the disabled "Pretty Refined Lingerie II"
   Pantie/Stocking set) kills the exporter with OOM (exit 137) during
   primitive extraction. Export the primary body + main outfit only; the
   lingerie set stays in the source `.blend` for the customization suite.
3. **The 247 KB Cydney GLB was an empty/broken export** (no meshes). A real
   export is tens of MB: Cydney 85 MB (40 meshes, 404,964 verts, 3 armatures,
   67 images), Vixen 76 MB (56 meshes, 510,180 verts, 1 armature, 125 images).
   Both verified by re-import + T-pose render from the GLB.

## Repair tool

`tools/blend17-repair/blend17_to_standard.py` — single-command pipeline:

```
python3 blend17_to_standard.py <in.blend> <out.blend>
```

Accepts either the raw 17-01 variant or the zstd-compressed mislabeled file
(auto-detected by magic). Tested: byte-identical output to the previously
proven manual conversion (sha256 `8cfdd829…` on the Mirko file).

## Files delivered (this PR)

- `tools/blend17-repair/blend17_to_standard.py` — repair tool
- `docs/research/blend17-01-variant-repair-2026-10-22.md` — this report
- `docs/proof/smutbase-intake-repair-2026-10-22/mirko-tpose.png` — Tobi
- `docs/proof/smutbase-intake-repair-2026-10-22/cydney-tpose.png` — Jotei
- `docs/proof/smutbase-intake-repair-2026-10-22/vixen-tpose.png` — Menajerii

GLB exports (kept in workspace, ~85 MB / ~76 MB — over the in-repo large-file
convention, see `~/workspace/worker75/cydney.glb` and `vixen.glb`).
