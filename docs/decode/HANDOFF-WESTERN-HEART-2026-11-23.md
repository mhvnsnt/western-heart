# HANDOFF — Western Heart push-everything, 2026-11-23

Branch: `muse/push-wh-scramble-lane3-20261123`. PR: #1853.
Base: main `64b0246f7c214647cb0990181f1f328c3cdf9d00`
(Merge PR #1838, 2026-11-23T17:13:54Z). Merge commit: (filled in on merge).

## What landed in this PR

### Batch 1 — scramble docs + listings (14 files, docs/decode/)

- `scramble-pattern-check-report.md` — the 102 do NOT follow one
  pattern; at least seven mechanisms M1–M9.
- `scramble-102-list.md` — reconstructed 102: 94 Tekken 7 + 6 Tekken 5
  Devil Within + 2 wrestling banks. 645 scope undefined (closest
  reproducible count: 680 moveset JSONs, 643 excluding docs/proof).
- `lane3-tekken-report.md` — Lane 3 Tekken full paired moves, 2026-11-22/23.
- `T7-EXTRACTION-NONE.md` — LZ4 → `none` codec record.
- `bannon-paired-throws-king-t7.json` — King paired-throw table from the
  real `.tkmvst`.
- `phase2.json`, `status.json` — Phase 2 sweep data.
- `listings/` (6 JSONs) — anim_t7, banks, docs_movesets,
  game_assets_movesets, game_data_moveset-library, teardown.

### Batch 2 — Tekken + KoC2 lane record (14 files, docs/lane-records/tekken-koc2-2026-11-22/)

Pairing audit (383 clips), seam-gate check (0/383 pass), refusal wiring
brick (14/14 headless tests pass), KoC2 Route A disassembly. Honest
headline: 0 Tekken/KoC2 moves play in a real match; 0 stills, 0 MP4s.
Evidence, not proof. The record is Bannon-facing (counts reference
Bannon's `assets/moves/ik/tekken/manifest.json`); landed here because
this lane owns it — the Bannon lane may want a copy.

### Already on main, not re-pushed (verified byte-identical)

- `docs/decode/PHASE-2-REPORT.md`, `docs/decode/STATUS.md`.
- NOTE: `STATUS.md` rows still say "#1803 open" in two places even
  though PR #1803 is merged. Correction owed as its own row update, not
  a silent rewrite.
- `.github/workflows/lane-c-t7-extract-king.yml` exists on main as the
  OLD LZ4 version (2,885 B, PR #1803 merged 2026-11-22 11:58am ET).

## What did NOT land, and the exact blocker

1. **King workflow update + Bryan/Heihachi/Jin/Yoshimitsu workflow**
   (`.github/workflows/lane-c-t7-extract-king.yml` → `none` codec;
   `.github/workflows/lane-c-t7-extract-bry-hei-jin-yos.yml` new).
   Blocker: the GitHub connector's GitHub App lacks the `workflows`
   permission — `403 refusing to allow a GitHub App to create or update
   workflow ... without workflows permission`. The connector cannot push
   any file under `.github/workflows/`, and a snapshot containing one
   403s the whole snapshot. Route: `git push` from a git-authenticated
   machine (the game-server VM). Files staged in
   `~/workspace/push-everything-2026-11-23/western-heart/staging/.github/workflows/`.
   Opening that follow-up PR triggers BOTH extraction runs (PR event is
   the working trigger; `workflow_dispatch` returns 403). Bryan code
   `bry` is an unverified candidate — the run itself is the verification.
2. **`T7_King.tkmvst`** (15,773,258 B, 2,787 moves, header `TKM21.0`,
   CRC32 ok, 4/10 throw clips PASS). Blocker: connector carries UTF-8
   text only, no binaries. Lives ONLY as Actions artifact run
   44858568891 (`king-tkmvst`, 13.7 MB, sha256 `613826d7…`), NOT in the
   repo, NOT in a release, expires ~2027-02-19, durable home undecided.
   Route: `gh run download 44858568891` with GitHub auth on the VM,
   verify size/header/CRC32, push by git. Full manifest:
   `~/workspace/push-everything-2026-11-23/western-heart/TKMVST-MANIFEST.md`.
3. **`docs/decode/tree-main.json`** — dropped on purpose: the workspace
   copy is a cached GitHub API rate-limit error payload, not a tree
   snapshot.
4. **`research/wh-scramble/tree-b2a52a.json`** (19.9 MB) — exceeds the
   16 MiB per-snapshot cap. Workspace only.

## Exact next step

From the VM (git-authenticated, self-hosted runner `oracle-bannon` is
online): push the two workflow files from the staging dir to a new
branch, open the PR, let the two extraction runs fire on the PR event,
then download the King artifact per TKMVST-MANIFEST.md and land the
`.tkmvst` at its decided durable home. After that, correct the stale
"#1803 open" rows in `docs/decode/STATUS.md`.

## Key facts (do not lose)

- Scramble 102 = 94 T7 + 6 T5DW + 2 wrestling banks; mechanisms M1–M9.
- King `.tkmvst` is the ONLY real fighter extraction; Bryan next.
- Codec is the 4th positional argument, `none` — NOT a `--compression`
  flag. The project's own reader refuses LZ4 type 1 payloads.
- PR #1803 is MERGED, not open. Open PRs #1817/#1818/#1820/#1814/#1770
  and the other 25 open PRs were untouched by this lane.
