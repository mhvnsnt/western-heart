# Tekken 6 PSP — ROUND 7 STATE (NDPP meshes + COM movesets)

Date: 2026-10-21. Branch: `teardown/tekken6-round7-ndpp-movesets`,
stacked on `teardown/tekken6-round6-com-gmo` @ d176c82 (PR #479).
Attempt 2: attempt 1 died to a daemon restart banking nothing
(no branch, no PR) — this lane commits + pushes after EVERY
sub-result.

## Inherited state (verified round 6, not re-derived)

- Containers 76/76 adler-exact (plain zlib; per-1024 cipher fix).
- Full bulk regenerated + verified (50.0% blocks differ, all odd).
- G1/G2/G5 MET (tekken6.bms validated by sha256-identical
  transliteration).
- The 18 COM files (idx58–75) are PER-CHARACTER MOVESET containers —
  18/18 named by the in-file string @624 (LAW..ZAFINA, HIGH
  confidence); framing: 16B header, fixed 624B header region,
  32-slot pointer table @368, MOTA tail = 2 chunks + 4×20B records
  per file (108 records).
- Meshes are NOT in the COMs and NOT GMO-framed (0 GMO in clean bulk).
- Mesh path = NDPP census: 1,565 NDPP occurrences in the entry-87
  slice of the clean bulk (r6_ndpp_scan / JOB1); 5,470/5,470 embedded
  GZIP containers in the same slice adler-exact on clean bytes.
- `models/ndpp_bounding_volumes.glb` is flagged INCOMPLETE (built
  from the corrupt-bulk census of 798).
- Workdir retained: `~/workspace/_t6r4-work/` (clean bulk
  `bulk_decrypted_r6.bin`, `decoded76/`, clone `wh/`).

## Jobs (in order)

1. JOB 1 — NDPP format crack: characterize the 1,565 NDPP items on
   clean bytes; decode the mesh-bearing format (bytes first, Ghidra
   on PSP binaries when bytes don't speak). Proof: first character
   mesh as GLB, front render viewed, textures baked (or honest
   no-texture finding), original-comparison documented.
2. JOB 2 — Batch meshes: every character-mesh NDPP item → GLB;
   per-character inventory with confidence + evidence; fix or
   supersede the incomplete bounding-volumes GLB.
3. JOB 3 — COM moveset decode: 18 COM containers fully decoded
   (32-slot pointer table @368 targets; MOTA tail) → per-character
   moveset JSONs, per-character isolation, sweep moveset-library
   format (verbatim records + Tekken-input conversion logged; move
   names only where file bytes carry them).
4. JOB 4 — Wiring + inventory: WIRING-INVENTORY update; asset
   landing; game-side registration minimal per engine context
   (web build retired; GLB + JSON are the deliverables).

## Owner laws applied

- TEXTURES BAKED IN: shipped GLB carries embedded textures if the
  source has them — proven by image count + textured render.
- ORIGINAL-COMPARISON GATE: every mesh deliverable rendered
  side-by-side vs its original; gate is BODY INTEGRITY (proportions,
  bone placement, weights, clean deformation), NOT pose.
- No deletions. Additions only. Specific paths committed, never
  `git add -A`. No game files in the public repo beyond evidence
  docs/JSON/renders already precedented in this teardown tree.
