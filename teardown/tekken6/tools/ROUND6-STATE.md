# Tekken 6 PSP — Teardown ROUND 6 STATE

Date: 2026-10-21. Lane: round 6 attempt 2 (attempt 1 died to a daemon
restart after completing Step 0 only). Branch:
`teardown/tekken6-round6-com-gmo` stacked on
`teardown/tekken6-round4-ppsspp-trace` (PR #446, round-5 head 8cbb284).

## Owner acceptance target

DONE = content LIVE in the western-heart playable build, verified in
`game/` (owner 2026-10-20 ~20:57 CDT). Coordinator steer 2026-10-21
~19:31 CDT: web/Three.js build is RETIRED as shipping target; game
ships as native mobile executable (engine = deep-research pick, Godot 4
frontrunner, not yet locked). For round 6: Jobs 1-3 unchanged
(engine-agnostic). Job 4: GLB conversions are the deliverable (GLB is
the interchange every candidate engine consumes); game-side
registration minimal, no web-build-specific polish; if registration
conflicts with transition, land GLBs + WIRING-INVENTORY and flag it.

## Inherited state — DO NOT REDO (coordinator-verified)

- Step 0 COMPLETE: PR #446 title/body updated to solved state:
  "Tekken 6 PSP SOLVED: 76/76 adler-exact — root cause was per-2048 vs
  per-1024 sector-cipher call (no custom gzip)".
- Round-5 verdict VERIFIED: no custom gzip exists. Round-3 decryptor
  called sector cipher once per 2048B sector; game calls it once per
  1024B block (t0 = block bulk-relative offset). Bodies are plain zlib
  under 20B header. Corrected tools on branch:
  `tools/bulk_decrypt.py` (per-1024), `tools/decode_all76.py`
  (76/76 adler-exact, inventory
  `tools/round5-evidence/r5_inventory_summary.json`),
  `tools/tekken6.bms` (authored, NOT executed),
  `teardown/tekken6/tools/ROUND5-STATUS.md`. G1/G2 MET.
- Workdir `~/workspace/_t6r4-work/` (2.8GB) RETAINED — RAM dump +
  decoded outputs are evidence; ISO untouched. Attempt-1 leftovers
  present at lane start (attempt 2): `bulk_decrypted_r6.bin` (367M,
  to be verified, not trusted blind) + `decoded76/` (76 files).

## Jobs (in order)

- JOB 1 — Full-bulk regeneration + derivative repair: regenerate
  complete bulk with corrected per-1024 decryptor; audit EVERYTHING
  derived from corrupt round-3 bulk in rounds 2-4, verdict each;
  known case = NDPP embedded scan (94/2,720 — redo on clean bytes,
  publish corrected count); search PRs #388/#413/#446 docs +
  `teardown/tekken6/` for other bulk-derived claims ->
  re-derived-clean / corrected / still-valid (with why). Open round-6
  PR (stacked on round-5 branch) once first results land, gate body
  + Gates G1-G6. Binaries to release in 100MB parts only if
  regenerated bulk must be stored — check size first.
- JOB 2 — .bms validation (closes G5): `tekken6.bms` never executed.
  Pull QuickBMS binary (official source; license noted in PR) and run
  against DATA401.BIN for >=2 containers, byte-compare vs
  `decode_all76.py`. If no binary runs, prove equivalence via
  line-by-line semantics + Python transliteration run, documenting
  which path taken.
- JOB 3 — COM inner framing + per-character inventory (G4): 18 COM
  plaintexts (idx58-75, all byte-exact) each hold ONE COM container
  ("COM\0" + count word 7-16) = 176 inner assets total (literal
  GMO\0 scan = 0; inner framing differs; do NOT round to old "40
  meshes" estimate). Crack inner framing from bytes; classify every
  inner asset (mesh/animation/texture/other) with byte evidence per
  class. Per-character inventory: COM file <-> character via DATA401
  index/order + name strings + roster order; confidence + evidence
  per assignment — never guess names. Per-character isolation.
- JOB 4 — GMO->GLB + wiring (G3 -> G6): meshes -> GLB via proven
  round-2 GMO pipeline (PR #388; cloud.glb viewed) extended to COM
  inner framing; proof = >=1 character mesh GLB rendered FRONT and
  VIEWED in real geometry (textured if textures decodable via NTPP
  path, else say untextured plainly). Wire into western-heart minimal
  per steer above: `teardown/tekken6/` assets + game-side registration
  per PR #187-era T6 pattern and UR PRs #429/#434; WIRING-INVENTORY
  update (decoded / wired / left-before-playable per class).

## Discipline

Additions-only; commit SPECIFIC paths (NEVER `git add -A` — clone has
untracked `__pycache__` under `teardown/tekken6/tools/`; never commit
it); PR body EXACT gate headings; NO-HAND-TOOLING (Ghidra
`~/workspace/tools/ghidra/` for code questions); own-eyes on renders,
unique filenames; NEVER delete game files or workdir contents; push
every turn; report local footprint at end.
