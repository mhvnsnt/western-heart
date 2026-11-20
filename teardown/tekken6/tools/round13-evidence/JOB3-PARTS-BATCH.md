# Tekken 6 PSP — ROUND 13 JOB 3: slice-parts batch decode

Date: 2026-10-22, round 13. Tool: `tools/r13_batches.py parts`.
Manifest (per segment, per GLB, with sha256):
`tools/round13-evidence/r13_parts_manifest.json`.
GLBs: `teardown/tekken6/models/parts/seg{NN}/bulk{NNNN}_slot{K}_r13.glb`.

## Totals

| measure | value |
|---|---|
| slice containers scanned | 5,470 |
| part packages (round-11 classes boned-part 3,002 + rigid-part 436) | **3,438** |
| NDPP sections decoded → GLBs | **3,039** |
| NDPP sections failed (reported, never skipped) | 405 |
| vertices total | 2,005,929 |
| triangles total | 1,211,043 |
| GLB bytes total | 65,388,452 (62.4 MiB) |
| placement | **IN-TREE** under `models/parts/seg{NN}/` (below the ~150 MB volume-rule threshold — no release needed) |

Determinism: the batch ran twice (first run's output directory was
lost with a volatile /tmp mount); all **3,039 GLBs are
sha256-identical across both runs** — the decode is byte-stable.

## Per-character isolation / labeling

Parts are organized strictly per round-11 B3 segment
(`seg00`–`seg27`). Segment assignment for slice parts is
**contiguity-INFERRED** (round 11: 28 anchor-proven / 5,206
contiguity-inferred) and stays labeled as such in the manifest's
`confidence_note`; no fighter names are claimed for segments, and
**nothing was merged into the 12 proven character packages**.

## Failures by reason (405)

| reason | count |
|---|---|
| `IndexError: list index out of range` — VTYPE color-format 7 (the `0x*33d` family: 0x33d, 0x433d, 0x833d, 0xc33d, 0x1033d, 0x1433d; also the 0x11d stage tail class is absent here) — r9 `vtype_layout` raises because its `COL_SZ` table has no entry for color field 7 | 400 |
| `KeyError: 'pos'` — VTYPE with no position field | 4 |
| `struct.error` — truncated vertex buffer vs declared unit pairs | 1 |

Per-package failure records (bulk index, slot, decoder reason,
offending VTYPE) are in the manifest's per-segment `failures`.

**The col=7 residual, measured but NOT guessed:** for the `0x*33d`
family, pair-offset deltas prove the vertex stride exactly —
20 B for VTYPE 0x33d/0x433d, 24 B for 0x833d/0xc33d — and every
vertex carries the constant bytes `80 80 80 ff` at offset
stride−16 (an RGBA8888-looking color) followed by two s16×3
position-like triples (the second with a constant-zero third
component in sampled units — a morph-target shape). A candidate
layout was tested against the section descriptor bbox and did NOT
validate cleanly (a −32768 sentinel value appears in the decoded
range), so no layout was shipped: presenting it would be a guess,
and 400 sections wait on proving it. Named residual for a future
round: prove the col=7 vertex layout (weights/uv split of the
leading stride−16 bytes; role of the second s16 triple), extend the
decoder as a new tool, re-run only the 400 failed sections.

## Gate render — VIEWED

`tools/round13-evidence/r13_gate_part_bulk0086_front.png`
(Blender Cycles CPU, clay): `models/parts/seg00/bulk0086_slot0_r13.glb`
(4,061 verts / 2,179 tris) renders as a coherent female torso
costume part in T-pose — corset/bustier top with front lacing,
both arms with hands, wrist bands. A customization part, exactly
the class the census promised; geometry is coherent, not a
wall-pile. (Two earlier renders were black/empty due to render-side
camera/lighting setup; the mesh data was never the problem — the
final framing is a fixed front camera.)
