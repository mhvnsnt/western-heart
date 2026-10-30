# Decision Log — 2026-10-22 — T5/T6/TTT2/T7 teardown completion (Worker 72)

## D1. Brief figures corrected, not acted on
The task brief's status figures (T5 "never acquired", T6 "~30%", TTT2 "~15% +
needs 13.3GB download") were verified stale against live Release/API state
before any work began. Decision: re-baseline from evidence
(`docs/research/TEARDOWN-COMPLETION-T5-T6-TTT2-T7-2026-10-22.md` §0) instead of
re-acquiring assets that already exist on Releases. No duplicate downloads were
performed.

## D2. T5 DATA0: surgical cryptanalysis over full pull
Full TK5DATA0.BIN is 2,072,586,240 bytes; the VM cannot hold it. Decision:
HTTP Range surgery on the Internet Archive source (ISO9660 extents parsed from
the PVD — full root table in the research report) plus the `tekken5-disc-v1`
release. Result: layer-1 cipher cracked (house LCG, seed 1, per-block restart);
layer-2 characterized (21-byte periodic residual, not a simple repeating key).
The 2 GB payload stays remote until layer 2 falls (PCSX2 RAM-dump fallback
documented).

## D3. T6 PS3 psarc: documented as encrypted-at-rest, not forced open
The first 8 MB of `TEKKEN.psarc.part_aa` (release `tekken6-ps3-full-v1`) is
uniformly high-entropy with no `PSAR` magic — plain-psarc tooling does not
apply. Decision: record the sha256 reassembly manifest and the exact
decrypt-then-extract path (compare against the PSP sector-cipher family)
rather than burn VM disk on a 5 GB pull that cannot be opened yet.

## D4. TTT2: procedure documented, extraction deferred to a big-disk machine
All 26 parts verified present on release `ttt2-7z-v1`. The ~27 GB scratch
requirement exceeds this VM's free space by ~26 GB. Decision: write the exact
reassembly + 7z + STFS procedure (reusing in-repo `tools/stfs_blobs.py`,
`xdvdfs_reader.py`) so any machine with disk can run it unattended — no
partial/corrupt local state left behind.

## D5. No game binaries committed to the repo
Per the repo AGENTS.md law ("No copyrighted/leaked game files … in public
repos"), this PR contains documentation and analysis scripts only. All large
binaries remain on GitHub Releases / Internet Archive with hashes and pull
commands recorded.

## D6. MERGE FREEZE honored over merge-it-yourself
Task instruction for this round: push to the PR branch and report merge-ready;
do NOT merge. The repo's standing merge-it-yourself law is superseded by the
explicit round instruction for this PR.

## D7. T7 stays last
51 GB acquisition has no VM-disk path and depends on the owner's purchase step
(`TEKKEN78-ACQUISITION-PLAN.md`). Documented as blocked; no work attempted.
