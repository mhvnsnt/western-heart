# Tekken 6 PSP — ROUND 6 JOB 4: GMO→GLB + wiring (G3 → G6)

Date: 2026-10-21, round 6 attempt 4.

## Result: ZERO new GLBs — honestly, because there are no proven meshes to convert

JOB 3 (this round, byte-proven) established that the 18 COM
plaintexts contain **no meshes at all**: they are per-character
moveset/command files with MOTA animation references. The whole
clean bulk contains **zero literal `GMO\0` magics** (JOB 1,
re-counted on the regenerated bulk). Converting anything to GLB
from this data would require inventing geometry — speculative
meshes are explicitly out of scope, so none were made.

What remains proven and on file from earlier rounds:

- The round-2 GMO→GLB pipeline itself (PR #388) is still-valid and
  proven on real PSP GMO samples (`tools/proof/cloud_front.png`,
  viewed front render of `cloud.glb`) — it was never fed by T6 bulk
  data, so the corrupt-bulk audit does not touch it.
- `models/ndpp_bounding_volumes.glb` (1,103 boxes) exists on main —
  JOB 1 flags it **incomplete**: it was extracted from a census of
  798 NDPP sections on corrupt bytes; the clean bulk shows 1,565
  NDPP occurrences in the same slice. Re-extraction from the clean
  bulk is owed before that GLB is treated as complete. (These are
  bounding volumes, not character meshes, in any case.)

## Where the meshes actually are — the open problem, stated plainly

Character geometry was not found in (a) the top-76 containers,
(b) the COM set, or (c) as literal GMO anywhere in the bulk. The
remaining candidate space is the **5,470 adler-exact embedded
containers** in the entry-87 slice (JOB 1 corrected count) plus the
NDPP section space at its corrected census (1,565) — the NDPP
"does not contain vertex arrays" verdict was withdrawn in JOB 1
because it was an exhaustive scan over corrupt bytes. A clean-bulk
NDPP re-scan + embedded-container census is the next lane's first
job; until it lands, T6 PSP has **0 proven character meshes** and
therefore 0 new GLBs and 0 new game-side registrations this round.

## Wiring

No game-side registration was added: per the engine steer
(2026-10-21) registration is minimal and GLBs are the deliverable,
and there are no new GLBs to register. `WIRING-INVENTORY.md` was
updated this round with the corrected decoded/wired/left state.
