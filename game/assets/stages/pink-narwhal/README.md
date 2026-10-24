# Pink Narwhal — stage source (intake 2026-10-22)

**ARENA ASSET — not a character. CONFIRMED: this IS the club/DJ arena base
(SmutBase b8ada591), a strip-club map.**

- Source: SmutBase download `ThePinkNarwhal_zVamCQj.blend` (51.6 MB, sha256 `419a2b6f…ee1a09`)
- **Staged (not committed):** `~/workspace/fix2/smutbase-source/pink-narwhal/ThePinkNarwhal.blend`

**Why staged, not committed:** the file exceeds what the Git Database blobs API
will accept in one request (HTTP 422 on a 51.6MB blob; gzip gives no relief —
the .blend is already internally compressed). Registered here with its hash;
the repo stays the system of record.

**For the arena lane:** build the club / DJ-booth / concert variants on this
base per `~/workspace/intake-stage/stages/CLUB-ARENA-PLAN.md`
(`club-neon`, `club-djbooth`, `club-concert`).
