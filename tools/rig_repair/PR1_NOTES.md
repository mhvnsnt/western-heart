# PR 1: Rig-repair baseline (detect + transfer + gate + clips)

Ports Bannon PR #77's `tools/rig_repair/` into western-heart (Grok's documented
next step) with the Track-1 reproduce findings fixed. This is the foundation
the refit/separate/armpit stages (PRs 2-4) build on.

## Track-1 fixes in this PR

1. **Multi-buffer + meshopt decode** (`ingest.py`, new): `detect` crashed on
   meshopt-compressed / multi-buffer GLBs (`ValueError: buffer is smaller than
   requested size` — it read only the first BIN chunk). `ingest.py` is a shared
   Python GLB reader: honors `bufferView["buffer"]`, decodes
   EXT_meshopt_compression via pip `meshopt` (empirical: for TRIANGLES mode the
   extension count is the *index* count, not count×3), raises `DracoError` for
   draco. Verified: meshopt STICKUP.glb → 12,633 verts / 54,000 indices,
   identical metrics to the plain file. No vendored node_modules (disk).
2. **Multi-mesh/primitive support**: `detect` silently read only
   `meshes[0].primitives[0]` (353/17,438 verts on a 15-mesh model, no warning).
   Now iterates all meshes/primitives, reports aggregate + per-primitive.
3. **rigcheck decode path fixed**: was dead (missing node_modules,
   FileNotFoundError before node ran). Now pure Python via `ingest.py`.
4. **The 6 standard gate clips** (`clips/standard/*.glb`): idle, walk, jab,
   kick, hit_react, knockdown — did not exist in the repo, so the full gate
   could never PASS. Shipped as procedural test fixtures (`make_clips.py`
   generates them); labeled as fixtures, not game content.
5. **transfer de-hardcoded**: was STICK-UP-specific (output mesh name hardcoded
   `"STICKUP_HQ"`, `--limb-separate` hardcrashed on non-Mixamo skeletons,
   single-primitive only with silent data loss, dropped `extensionsUsed`/
   `extensionsRequired`, `--retarget` default `aligned` in code vs `rest` in
   docs). Now: mesh name from target, tolerant joint matching via synonym
   tables, loud skip (not crash) on non-Mixamo, multi-primitive, preserves
   extensions. Doc/code default mismatch corrected (code: `aligned`).

## Validation (this PR's scope)

- `detect` on plain + meshopt GLBs: correct JSON, ~1.5 s.
- `rigcheck` static gate on plain GLBs: fails correctly with real numbers.
- The 6 clips load in the gate; ground/stretch checks run.

Full pipeline validation (refit → gate → proof) lands in PR 4.
