# T7 extraction, uncompressed — the LZ4 → `none` record

**Date:** 2026-11-22. **Lane:** Lane 3 (Tekken, full paired moves).
**Status:** workflows prepared, not yet run. The PR that carries them is the
test: opening it triggers both extraction runs (PR event is the working
trigger — `workflow_dispatch` returns 403 for this lane's token).

## What was wrong

The only real Tekken 7 fighter extraction, King (run 44858568891, PR #1803
merged), produced an LZ4-compressed `.tkmvst` (compression type 1).
Western Heart's own reader, `tools/anim/tkmovesets2/tkmvst_to_wh.py`,
refuses it outright:

> `payload uses LZ4 compression (type 1); install python-lzma or re-export
> the moveset uncompressed (TKMovesets2 headless: --compression none). No LZ4
> decode is attempted here.`

So the King file that exists cannot be read by the project's own tool — not
by any decode bug, but by a codec choice at extraction time. The 4/10 throw
validations that passed were done against the payload by other means; the
6 pending validations (578, 590, 592, 594, 716, 718) and every receiver
rebuild need a readable file.

## Correction: `--compression none` is not a flag

The brief's phrasing ("re-extract with --compression none") is wrong as a
command line. There is no `--compression` flag. Verified against upstream,
Kiloutre/TKMovesets `docs/headless.md` **at v1.1** (the pinned exe version):

- `build-disk-movesets-t7 | TKDATA_BIN DIRECTORY [CODE,...|all] [CODEC]` —
  "Builds T7 movesets from the game's files. Codec default `lz4`."
- "Codecs: `none`, `lz4`, `lzma`, `compact-zstd`. File commands default to
  `none` unless stated."

The correct invocation is a 4th **positional** argument:

```
TKMovesets2.exe --headless build-disk-movesets-t7 gamefiles\tkdata.bin out kin none
```

(`--compression none` would fail with exit 2, usage error.) Both workflows
in this PR use the positional `none` and verify the result in-run: header
magic `TKM2` plus compression byte `0x60 == 0`, with sha256 + size logged.

Side note: the `tkmvst_to_wh.py` error text is itself misleading — it says
"install python-lzma" for an LZ4 payload, which would not help (LZMA ≠ LZ4).
The actionable part is the re-export. An alternative fix — teaching the tool
LZ4 via `python-lz4` — was not taken: the tool deliberately refuses LZ4, and
re-exporting uncompressed keeps one canonical readable form.

## What the two workflows do

1. `lane-c-t7-extract-king.yml` (modified) — re-extracts King with `none`.
   Artifact `king-tkmvst-none`, superseding `king-tkmvst` (13.7 MB, LZ4).
   Expected: `T7_King.tkmvst`, ~15.7 MB uncompressed, 2,787 moves.
2. `lane-c-t7-extract-bry-hei-jin-yos.yml` (new) — extracts Bryan, Heihachi,
   Jin, Yoshimitsu with `none` in one run. Artifact
   `t7-tkmvst-bry-hei-jin-yos-none`.

## Fighter codes: how they are (not) verified

TKMovesets2 keeps **no hardcoded fighter-code table**. The codes are read
from `tkdata.bin` itself — files `mothead\bin\<code>mot.bin`
(`T7DiskMoveset.cpp`, `Characters()`). `kin` for King is proven by run
44858568891. `bry` for Bryan is expected but unverified; `hei`, `jin`,
`yos` are candidates in the same form. The fighter run IS the verification:
its headless JSON prints one entry per code (`{code, ok, name, character,
moves, animations}` or `{code, ok:false, error}`), a wrong code fails only
its own entry, and the upload step runs anyway (`if: always()`), so the
correct fighters still land. Do not "fix" a failed code by guessing another
one — read the run log first.

## What is still owed after these runs

- **Durable home (undecided, owner/coordinator call).** The LZ4 King file
  lives ONLY as a run artifact (expires ~2027-02-19, 90-day default, no
  retention-days set) — not in the repo, not in a release. The `none`
  re-extracts will have the same problem at 5× the size unless a home is
  chosen first (new release vs alongside `tekken7-gamefiles-v1`). Do not
  treat the new artifacts as landed.
- **6 pending King throw validations** (578, 590, 592, 594, 716, 718) — run
  `tkmvst_to_wh.py validate` against the `none` file once it exists. Frame
  counts already match from the `.tkmvst` side.
- **Receiver rebuild** (22 P1/P2 receivers + bank thrower 588) with the joint
  sandwich in `docs/decode/T7-RECEIVER-FIX.md` §3c. Needs the readable
  `.tkmvst` (animation blobs) + the game-sampler decode chain
  (`TekkenGame-Win64-Shipping.exe`, sha256 `7f2b6872…`) — the receivers
  `rotsm_575` / `rotsm_579` are NOT on main; they were built in lane
  workdirs only.
- **Remaining fighters.** 16 extractions cover every T7 group except the
  unified index, which needs all 38 fighters. Same workflow pattern, one
  fighter (or small batch) per file, codes verified by their own runs.
