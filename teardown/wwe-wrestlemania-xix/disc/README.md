# WWE WrestleMania XIX (GameCube) - VM sweep Lane B (2026-11-21)

Moved off the Oracle VM disk into western-heart.

- `disc/WWE WrestleMania XIX (USA).rvz` - the game disc image (RVZ).
  SHA-256 `0fd3540dbf053dfee0fc76ef51ec5ee617cf9ce667e2675ff43e9ce5f1e16f82`.
  Split into <=100 MB pieces; reassemble with `cat *.part* > file` and verify
  against MANIFEST.tsv. The plain `.iso` (1,459,978,240 B) was deleted from the
  VM after dolphin-tool proved the RVZ decompresses to a byte-identical ISO
  (SHA-256 `b84472a45f66c2ea968f18a4fec7b9abf44b0f1c6fd834e8727332f054e8fcb0`).
- `extracted/` - ISO extraction remainder: every file here was verified NOT
  already in western-heart by blob hash. (Files whose blobs were already in
  the repo were deleted from the VM instead of re-pushed.)
- `w7/` - W7 follow-up work: RAM dumps + Dolphin DTM inputs + probe logs.
- `tools/wit/` - Wiimms ISO Tools v3.05a (wit/wwt/wdf) used for ISO work.
- `work/` - Dolphin boot screenshots + download/extract logs.
- `teardown/wmxix/tools/w6_*.py|sh` - W6 probe/push/runfind scripts (remainder;
  the rest of tools-src was already in the repo).
