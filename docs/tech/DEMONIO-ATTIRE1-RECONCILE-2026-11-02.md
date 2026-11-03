# Demonio attire1 — repo vs bucket reconcile (2026-11-02)

**Verdict: the bucket is STALE / WRONG. The repo file on main is correct.**
The file the assets bucket serves at `roster/demonio/attires/attire1/model.glb`
is byte-for-byte the **pre-rig-fix** version of the file — the version that
commit `e4a832942b1e611bb1bbca23edee880f8590b3e4` (2026-10-31, "Demonio
Attire 1 rig fix (weights) + T7 Jin stance finding") replaced. It is not an
orphan: it matches a known commit's blob exactly. The bucket was uploaded
about 2 h 45 min **before** the rig fix landed and was never re-uploaded.

This reconcile was flagged by the load-times lane in
`docs/tech/LOAD-TIMES-2026-11-01.md` (finding B7): the repo lists the file
at 28,793,068 B while the bucket serves 28,872,600 B at the same key —
a difference of 79,532 B.

## Fingerprints (all measured 2026-11-02, full-byte hashes)

### Bucket file — what the game actually downloads today

Served by the Worker `https://western-heart-assets.mhvnsnt.workers.dev`
at key `roster/demonio/attires/attire1/model.glb`
(`Content-Length: 28872600`, `Last-Modified: Sat, 31 Oct 2026 13:00:51 GMT`,
`x-amz-meta-src_last_modified_millis` = 2026-10-31 12:36:06.881 UTC):

- Size: **28,872,600 B**
- SHA-256: `e5b7b54cb5ab69941c98f99c3d4c2b2fefa37e678df6e7f212bd1f8428fda8a3`
- MD5: `e0cbcdf21df61d53f18d6e75a4cd1477` (identical to the served `ETag` — the hash chain closes)
- Git blob SHA-1 (computed over the served bytes): `5b531cfae95d18fb9cba1ceaf8649dd959bdce39`
- GLB header: `glTF` v2, declared total length 0x01b88f98 = 28,872,600 B (self-consistent)

### Repo file — current main (the correct file)

`roster/demonio/attires/attire1/model.glb` on main (verified unchanged at
dispatch HEAD `5d44753202fb121f3efe691daa1ef102d2e4161b` and at
`1a6c77a7e79b90775b025ba8d38eb79f6f93f21c`; the blob itself was re-fetched
from the GitHub Git API and hashed in full):

- Size: **28,793,068 B**
- SHA-256: `b95e71252ba11b4308b9c96f575217e3e292707579de65b2867558dce307804d`
- Git blob SHA-1: `3bd1e9c98fbcb1bc581ed95ebeb7945a56d56eb6`
- GLB header: `glTF` v2, declared total length 0x01b758ec = 28,793,068 B (self-consistent)

### Repo file — historical version the bucket matches

The same path at commit `9f79689035b35cdae1878ef1f3b88ebd872c0cfc`
(2026-10-21, "Rig Tripo statics: GameRig proxy bone-heat + exact facing +
A-pose fit…"), re-fetched from the GitHub Git API and hashed in full:

- Size: **28,872,600 B**
- SHA-256: `e5b7b54cb5ab69941c98f99c3d4c2b2fefa37e678df6e7f212bd1f8428fda8a3`
- Git blob SHA-1: `5b531cfae95d18fb9cba1ceaf8649dd959bdce39`

## Match result

**The bucket file matches commit `9f79689035b3`'s version of the path
exactly** — same size, same SHA-256, same git blob SHA-1. It is the exact
"before" file documented in
`docs/handoffs/RIGFIX-DEMONIO-ATTIRE1-2026-10-31.md`, which records the
rig fix as: 28,872,600 B → 28,793,068 B, git blob `5b531cfa…` →
`3bd1e9c98fbcb1bc581ed95ebeb7945a56d56eb6`, sha256 `e5b7b54c…` →
`b95e71252ba11b4308b9c96f575217e3e292707579de65b2867558dce307804d`.
Every one of those four numbers was independently re-measured in this
reconcile and matches. The bucket file is **not** an orphan variant and
**not** a pre-pack variant: both files are EXT_meshopt_compression
encoded; the difference is the rig fix (below), whose re-encode accounts
for the 79,532 B size delta.

### Full history of the path (only 3 commits ever touched it)

| Commit | Date (UTC) | Size | Git blob SHA-1 |
|---|---|---|---|
| `d5aac4e0ab8a0da9760e4ee134ef212aae4024d4` | 2026-10-19 | 57,601,828 B | `ed238fe099653e89fde0632ade13a531954d0c38` |
| `9f79689035b35cdae1878ef1f3b88ebd872c0cfc` | 2026-10-21 | 28,872,600 B | `5b531cfae95d18fb9cba1ceaf8649dd959bdce39` |
| `e4a832942b1e611bb1bbca23edee880f8590b3e4` | 2026-10-31 15:46 | 28,793,068 B | `3bd1e9c98fbcb1bc581ed95ebeb7945a56d56eb6` |

### Other Demonio GLBs checked at main (none matches the bucket size)

| Path | Size |
|---|---|
| `roster/demonio/attires/bloodline-ember/demonio-bloodline-ember.glb` | 25,698,348 B |
| `roster/demonio/attires/human/model.glb` | 56,667,288 B |
| `roster/demonio/attires/human/model-rerig.glb` | 28,737,644 B |
| `roster/demonio/attires/human/model-rigged.glb` | 19,377,980 B |
| `roster/demonio/attires/winged-devil/model.glb` | 55,823,720 B |
| `roster/demonio/attires/winged-devil/model-rigged.glb` | 19,010,652 B |
| `game/assets/models/demonio.glb` | 8,808,768 B |

No `source/` or separately packed/meshopt variant of attire1 exists in
the repo; attire1's packed form is the file itself (meshopt, per the
rig-fix handoff).

## Which file is correct, and the evidence

**The current main file (28,793,068 B, sha256 `b95e7125…`) is correct.**

1. **It is newer and it is a deliberate fix.** The bucket bytes are the
   input to the 2026-10-31 rig fix; the repo bytes are its output. The
   fix (per the rig-fix handoff, numbers re-audited there on the shipped
   file) removed all contaminated skin weights (mass 0.00113, 10,301
   verts → 0.0, 0 verts) and revived the dead `RightFoot` joint — in the
   bucket's file, the right foot does not follow foot-animation channels
   at all. Serving the bucket file ships that known rig defect.
2. **Chronology.** Bucket object: source-file mtime 2026-10-31
   12:36:06 UTC, uploaded (`Last-Modified`) 2026-10-31 13:00:51 UTC.
   Rig-fix commit `e4a8329`: 2026-10-31 15:46:20 UTC. The upload predates
   the fix by ~2 h 45 min; nothing at this key was uploaded after it.
3. **The game expects this path as Demonio's base/default form.**
   `roster/demonio/ATTIRE-SLOTS.md`: Attire 1 (unwinged demon,
   base/default, access "Start") = `attires/attire1/model.glb`, loaded
   from the remote asset base like the rest of the roster's large
   models — i.e. players currently get the stale bucket bytes at the
   exact key the fixed file belongs to.
4. **No config expects the bucket size.** The 28,872,600 B figure
   appears in the repo only as the rig fix's "before" number and in the
   load-times flag; 28,793,068 B is the size on main and in the
   load-times measurements (28.7 MB parse bench, finding B7).

## What the bucket SHOULD serve (for the B2 lane — this lane uploads nothing)

- Key: `roster/demonio/attires/attire1/model.glb`
- Currently served (wrong): 28,872,600 B, sha256 `e5b7b54cb5ab69941c98f99c3d4c2b2fefa37e678df6e7f212bd1f8428fda8a3`, MD5/ETag `e0cbcdf21df61d53f18d6e75a4cd1477`
- Should serve (the current main file): **28,793,068 B, sha256 `b95e71252ba11b4308b9c96f575217e3e292707579de65b2867558dce307804d`, git blob `3bd1e9c98fbcb1bc581ed95ebeb7945a56d56eb6`**
- Source of the correct bytes: repo path `roster/demonio/attires/attire1/model.glb` at main (blob above, introduced by commit `e4a832942b1e611bb1bbca23edee880f8590b3e4`).
- After re-upload, the served `Content-Length` must read 28793068 and a
  full download must hash to the sha256 above before the flag on
  issue #866 is closed.

## Method note (measurement conditions)

Fingerprints were computed over the complete byte streams: the Worker's
full 28,872,600 B response (its `Content-Length`, the re-fetched
historical blob's size, and the GLB header's declared length all agree),
and both repo blobs re-fetched in full from the GitHub Git API. During
this lane the VM was under a write storm (shell/exec file writes landed
as 0 bytes or returned EPERM), so hashing was done in memory over the
streams rather than from an on-disk download copy; three independent
measurements agree (Worker stream hash, Git API blob hash, and the
rig-fix handoff's recorded hashes), and the bucket MD5 additionally
equals the Worker-served ETag, which is set by the storage layer, not
by this VM.

## Owner instruction (verbatim quote)
> ALSO FLAGGED: the repo lists `roster/demonio/attires/attire1/model.glb` at 28,793,068 B while the bucket serves 28,872,600 B for the same key — reconcile which file is canonical before any Demonio asset work.

(Verbatim from finding B7 of `docs/tech/LOAD-TIMES-2026-11-01.md`, the
load-times lane's flag this reconcile answers.)

## Method the owner specified
Fingerprint the file the assets bucket serves at the key `roster/demonio/attires/attire1/model.glb` (full-byte download, size and SHA-256), fingerprint every Demonio attire1 candidate in the repo (the current main file, every prior version in the path's git history, and every other Demonio GLB that could match the served size), compare sizes and hashes to determine whether the bucket file matches a known commit's file or nothing in repo history, decide from the evidence which file is correct for the game, land one reconcile doc stating both fingerprints, the match result, which file is correct and what the bucket should serve, and flag the bucket lane on issue #866 if the bucket file is wrong — uploading nothing to the bucket.

## Method actually used
Fingerprint the file the assets bucket serves at the key `roster/demonio/attires/attire1/model.glb` (full-byte download, size and SHA-256), fingerprint every Demonio attire1 candidate in the repo (the current main file, every prior version in the path's git history, and every other Demonio GLB that could match the served size), compare sizes and hashes to determine whether the bucket file matches a known commit's file or nothing in repo history, decide from the evidence which file is correct for the game, land one reconcile doc stating both fingerprints, the match result, which file is correct and what the bucket should serve, and flag the bucket lane on issue #866 if the bucket file is wrong — uploading nothing to the bucket.

## Deviations (none / list, each with owner approval link)
None

## Proof (paths to files, frames, test output)
`docs/tech/DEMONIO-ATTIRE1-RECONCILE-2026-11-02.md`
`docs/handoffs/RIGFIX-DEMONIO-ATTIRE1-2026-10-31.md`
`docs/tech/LOAD-TIMES-2026-11-01.md`
`roster/demonio/ATTIRE-SLOTS.md`
`roster/demonio/attires/attire1/model.glb`

## Self-check: I verified the result against the literal instruction
- [x] I re-read the verbatim instruction above and the result does exactly what it says, using the method it names.
