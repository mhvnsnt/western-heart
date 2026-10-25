# NDPP — Tekken 6 PSP Model Container (Reverse-Engineered)

**Status:** Partial. Header, descriptors, bounding volumes, and normal arrays are
decoded and validated. Full render-mesh position arrays and index buffers were
**not found** in the examined sources. See "What NDPP does NOT contain" below.

**Sources examined:**
- `bulk_decrypted.bin` offset `38592*2048` (81,591,641-byte plaintext archive,
  manifest idx 325 / entry 87 / `bin_e6.2`): 357 chained NDPP sections
  (rel 66,636,400–72,140,288) + 441 scattered NDPPs (rel 73,556,304–81,508,608).
- `work/decrypt8/file0_decoded.bin` (GZIP entry 454, custom inflate, 98.7% —
  1,418-byte gap): one 78,560-byte NDPP section at file offset 112.

GMO magic (`OMG.00.1PSP`) has **zero** hits in the bulk. The GMO→GLB pipeline
does not apply. NDPP is the container.

## Section header (20 bytes, little-endian)

| Offset | Type | Example | Meaning |
|---|---|---|---|
| +0 | u32 | `0x5050444E` | Magic `"NDPP"` |
| +4 | u32 | 1840 / 3216 / 78560 | Section size in bytes **including** this header; next section (when chained) starts at `off + size` |
| +8 | u32 | `0x00010001` (351/357), `0x00020001`, `0x00030001`, `0x00050001`, `0x00190001` | Flags / section type |
| +12 | u32 | 0 | Reserved |
| +16 | f32 | 237.4784, -75.80, 0.004 | Unknown float; echoed inside descriptor records (see below) |

Chain-walking by `size` recovers 357 contiguous sections. 225 inter-section gaps
(896–8,704 bytes) contain compressed/random data, not vertex buffers.

## Descriptor record (64 bytes, follows header)

Observed in every section, 1–64 records per section:

| Words | Content |
|---|---|
| w0–w2 | f32 ×3 — meaning unconfirmed (see bbox note) |
| w3–w8 | f32 ×6 — axis-aligned bbox as `(minx, maxx, miny, maxy, minz, maxz)` — **validated**: min<max on all axes in every record checked |
| w9 | f32 — unconfirmed |
| w10–w13 | u32 ×4 — small ints, e.g. `(0, 16, 4, 2)`, `(0, 48, 1, 0xFFFFFFFF)` |
| w14 | f32 — `-15000.0`, `-18000.0`, or NaN/0 |
| w15 | f32 — **echo of header +16 float** (exact match in all sections checked) |

The 0x190001 section holds 64 sub-mesh descriptors; each has per-submesh varying
u16/u32 fields consistent with `(count, flags=0x1002, offB, offC, flags, count2)`
but offB/offC/offD do **not** resolve to vertex data as byte offsets into the
section (checked 10448 / 10592 / 11456 — random data).

## Bounding volumes (8-vertex boxes)

After the descriptors, sections contain 8-vertex hexahedra stored as 24
little-endian f32 (xyz × 8), axis-aligned cuboids in a **normalized local space**.
Validated: box corners × ~50,000 ≈ the descriptor bbox
(e.g. box xmax 0.2483 × 50000 = 12415 ≈ bbox maxx 12371).

- 1,103 boxes extracted from 357 sections (96 sections: none detected).
- Typical section: 2 boxes; observed range 0–64.
- Vertex order in clean boxes: `(-,-,-), (+,-,-), (-,+,-), (+,+,-), (-,-,+),
  (+,-,+), (-,+,+), (+,+,+)`.

## Normal arrays

Contiguous runs of f32 triplets with magnitude 0.90–1.10 (typically 0.93–0.95),
dominant axis varies per block. In `file0_decoded.bin` (offsets 500/1000 of the
file) 187 such triplets were verified. In the 81 MB archive they appear as
24–61-word blocks, one per sub-mesh in multi-part sections.

## What NDPP does NOT contain (verified by exhaustive scan)

- **No contiguous vertex-position arrays.** Longest position-like float3 run in
  the 64,560-byte 0x190001 section: 3 triplets (the descriptor itself). Same for
  the 19,344-byte 0x50001 section. Scattered "position-like" triplets elsewhere
  are misalignment false positives.
- **No index buffers.** u16/u32 scans show no runs of small sequential integers.
- The 0–66 MB region before the NDPP data is high-entropy (compressed/encrypted),
  not float arrays. Inter-section gaps are likewise not vertex data.

## Interpretation

NDPP sections as found are **metadata + bounding volumes + normals**, not render
meshes. The 8-vertex boxes are per-part/per-bone bounding volumes (hitboxes or
culling volumes). Full skinned-mesh positions + indices were not located in the
81 MB archive. The GZIP dynamic files (e.g. entry 454 → `file0_decoded.bin`)
contain NDPP sections with clean normals but their position data is destroyed by
the 1,418-byte custom-inflate length gap (separate decrypt-lane problem); the
larger GZIP files fail to decode at all with the current inflater.

## Extraction deliverables

- `ndpp_bounding_volumes.glb` — all 1,103 boxes, one object per section
  (`section_NNN`), grid-arranged for preview. **These are bounding volumes, not
  character meshes.**
- `boxes.json` (build intermediate, not shipped) — per-section box vertices.
- `preview_grid.png`, `preview_closeup.png` — Blender Cycles renders.
- `extract_boxes.py`, `build_glb.py` — reproducible extraction scripts.
