# DOA4 GLB REPAIR — 2026-10-20 (sweep phase 2)

Repairs all 165 shipped triangulated GLBs under `models/triangulated/` so they
import in Blender. This is an **importability/header repair**, not assembly:
the pools remain per-part local space (assembly needs the MdlGeo ObjGeo work,
still open — see SWEEP-AUDIT-2026-10-20.md).

## Defect 1 — TEXCOORD_0 byteOffset (all 165 GLBs)

The original `doa4_decode.write_glb` wrote TEXCOORD_0 `byteOffset = n*12`
(vertex index × 12) into interleaved vertex data. The correct offset is 12
(POSITION is 12 bytes; UVs follow immediately). Every shipped GLB therefore
failed Blender's glTF import in `decode_accessor`, while lenient readers
parsed positions/indices fine — which is how the broken files shipped.

Fix: re-wrap with the corrected writer (fixed writer lives in
`tools/doa4_decode3.py`, landed with the audit PR #381).

## Defect 2 — NaN in accessor min/max (chrtwo_25 only)

`chrtwo/chrtwo_25_1531v_1881t.glb` failed with "Bad glTF: json contained
NaN". Root cause: the writer initialized bounds from vertex 0, whose POSITION
Z component is NaN in the source pool; NaN comparisons never fire, so Z
min/max stayed NaN (X/Y, finite at vertex 0, escaped).

Fix: recomputed per-component min/max over the finite values in the actual
BIN buffer (stride 20, count 1531). Patched Z min = -2.681690505891295e+38,
Z max = 3.3860991998984055e+38, computed over 1527 finite Z values (payload
also contains 4 Z-NaNs, 70 X-NaNs, 5 Y-NaNs — source pool defects, not
writer defects). Proof of method: recomputed finite X/Y min/max equal the
shipped header X/Y values EXACTLY. The BIN chunk is byte-identical
before/after (sha256
0784f6d3cf955bea680e2fe453727d92fcf2d9cfefa6bbecbc0fc93842deb2f5) — only
the JSON header changed.

## Verification

Full-set Blender headless import check (verify_import.py): **165/165 OK**
(164 after defect-1 repair + chrtwo_25 after defect-2 repair), each with
meshes ≥ 1 and uv=True. Sample renders of repaired GLBs viewed by the repair
lane: coherent per-part pools, matching the documented unassembled state.

## Honest caveats

- Several pools (chrtwo_25, chrtwo_24/26, mot_00, …) contain finite ±3e38
  extremes and NaN payload vertices — decode-quality issues in the source
  tables, documented in the audit. A re-decode of those tables from the AFS
  sources via `tools/doa4_decode3.py` is the quality follow-up; this repair
  makes the files importable and their headers truthful, nothing more.
- No skeletons, weights, or animations exist in these GLBs. Assembly
  (MdlGeo ObjGeo parsing) remains the biggest open DOA4 item.
- Per-character isolation: files remain per-character-table self-contained;
  the repair touched each file independently.

## Process note

Three worker lanes were killed by daemon restarts during this repair; the
verified work was preserved in scratch (`RECOVERY-STATE.md` trail) and the
final landing was executed by the sweep coordinator under the owner's
standing auto-recovery approval.
