# No Mercy Wrong-Window Audit — 2026-10-21

## Owner instruction
Gap-closure finisher audit (continuation of the checkpointed lane
`gap-closure-audit-nm-window-20261021`): determine the blast radius of the
W3b-proven FileTable wrong-window defect beyond The Rock's clip set, across
`mhvnsnt/western-heart` and `mhvnsnt/wrestling-game`. STRICTLY READ-ONLY on
all game data, banks, converters and extractors — no fixes, no re-extraction,
no edits to any bank/moveset/converter file. Deliverable is this audit doc
via a docs-only, additions-only PR (do not merge) plus the same verdict
table in the lane checkpoint.

## Method the owner specified
(1) Enumerate every No Mercy-derived animation asset per bank/fighter in
western-heart (`game/assets/movesets/*.json` provenance, animation bank
.npy/clip files, `moveset-library/`, `teardown/wwf-no-mercy/`) and in
wrestling-game. (2) For each, determine which extractor/converter produced
it and which FileTable window + ID base it used — converter code (current +
git history: `git log`/`git show`/`git blame` for the window constants) and
conversion manifests/provenance in the banks. (3) Verdict per bank:
WRONG-WINDOW (0x16C3238 / 0x1BD1B0 / 0-based), CORRECT-WINDOW (game-exact or
window-independent, with cited evidence), NOT-NM-DERIVED (name the real
source), or INDETERMINATE (name the missing evidence and where it lives).
Never guess. Frame counts do NOT exculpate — W3b showed counts "worked"
under the wrong window. (4) Flag prominently any WRONG-WINDOW bank wired
into a playable fighter; change nothing.

## Method actually used
Read-only inspection only: `grep`, `git log` / `git show` / `git ls-tree`
against `origin/main` of the existing partial clone at
`~/workspace/_w3b-work/wh`, local JSON header/provenance reads, one `.npy`
header/shape read (`anim_339A.npy`), and the GitHub API tree + file read
for `mhvnsnt/wrestling-game` (no local clone exists). Ground truth is the
W3b finding (checkpoint `gap-closure-w3b-aki-fk-ik.json`): decompiled game
code (Rev-A ROM sha256 fc561fce…, FUN_80003ab0/FUN_80003bd0) proves
game-exact = FileTable 0x16C31D8, FirstFile 0x1BD150, 1-based IDs; the repo
converters used the VPWStudio NTSC_U_10 pairing (0x16C3238 / 0x1BD1B0,
0-based), so a clip named `fid` actually read game file `fid+0x19` spliced
+0x60. W3c (PR #499, OPEN, unmerged) empirically confirmed this on the 11
Rock clips by re-extracting on the true window (e.g. Rock Bottom 70 frames
true vs 49 in the bank; People's Elbow 112 vs 7).

## Deviations
- None in scope or method. No bank, converter, extractor or moveset file
  was modified; no re-extraction was run. The one empirical cross-check
  that could have extended W3c's proof clip-by-clip across the whole bank
  (re-decoding sample clips on the true window) was NOT done, because it
  would itself be a re-extraction and the task forbids it; bank verdicts
  below rest on extractor-code provenance + git history + W3c's proof on
  the Rock subset, and say so.

## Proof

### The shared-extractor fact (root of the blast radius)
On `origin/main`, `teardown/wwf-no-mercy/tools/anim_extract.py` defines
`FT = 0x16C3238` / `FIRST = 0x1BD1B0` (the wrong U_10 window) and its
`FileTable.entry(i)` reads `data[FT + i*4]` with no 1-based adjustment
(0-based IDs). Those constants are unchanged since the file's first commit
(9976bfb8). EVERY other NM extractor on main imports this one class and
none overrides the constants:
`extract_all_anims.py` (`from anim_extract import FileTable, … FIRST_ANIM,
FIRST_MOVE_ANIM`), `extract_all_models.py` and `extract_textures.py`
(both `from anim_extract import FileTable`). So every artifact any of them
produced on the main lineage came through the wrong window — regardless of
what their docstrings claim.

### The false "corrected" extraction (commit 772694040)
Commit 772694040 (2026-10-13, PR #39, MERGED) delivered the current bank —
"Animations: 5,787 AKI clips … CORRECT FileTable offsets 0x16C31D8/0x1BD150
(NTSC_U_11); an earlier pass used NTSC_U_10 offsets" and lists
"anim_extract.py (fixed offsets)" among its tools. But
`git show 772694040:teardown/…/anim_extract.py` still contains
`FT = 0x16C3238` / `FIRST = 0x1BD1B0`. The claimed fix is not in the code
at the commit that shipped the bank, and no later main commit re-exported
the clips (clip-dir history: 9976bfb8 → 772694040 → restore commits only).
Either the bank was produced by the committed (wrong-window) code, or by
an uncommitted local variant that was never pushed — in which case W3c's
true-window re-extraction producing different frame counts for all 11 Rock
clips (70/112/39/13/20/28/102/103/82/17/24 vs the bank's values) settles it:
the shipped bank does not match the game-exact window.

### Verdict table

| # | Bank / asset | Location | Clips / files | Verdict | Evidence (one line) |
|---|---|---|---|---|---|
| 1 | AKI animation bank (.npy) + manifest.json | WH `teardown/wwf-no-mercy/animations/clips/` | 5,787 .npy on main (5,762 in first export 9976bfb8 + extension in 772694040); manifest range 0x2DD9–0x4461+, 1,353 system + 4,409 move | **WRONG-WINDOW** | Produced by extract_all_anims.py → shared FileTable with FT 0x16C3238/FIRST 0x1BD1B0, 0-based, unchanged since first commit; W3c true-window re-extraction disagrees on all 11 sampled clips |
| 2 | Model bank (OBJ + .vc) + manifest.json | WH `teardown/wwf-no-mercy/models/` | 7,141 files on main (~3,570 models per PR #39) | **WRONG-WINDOW** | extract_all_models.py imports the same FileTable with no override; its docstring claims U_11 (0x16C31D8/0x1BD150) but the code it calls contradicts it; shipped in the same false-"corrected" commit 772694040. No per-file empirical re-check exists (read-only scope) |
| 3 | Texture bank (PNG) | WH `teardown/wwf-no-mercy/textures/` | 5,381 files on main (5,029 textures per PR #39) | **WRONG-WINDOW** | extract_textures.py imports the same FileTable with no override; same docstring-vs-code contradiction and same commit 772694040 as #2 |
| 4 | Arena assemblies | WH `teardown/wwf-no-mercy/arenas/` (17 .obj/.vc assemblies) | 17 arenas | **WRONG-WINDOW (inherited)** | assemble_arenas.py assembles the already-extracted AkiModel pieces + textures from #2/#3; it does not read the ROM FileTable itself, so it inherits their window |
| 5 | AKI→Tekken3 retarget v1 output | WH `teardown/wwf-no-mercy/aki_to_tekken3_v1.json` (anim 339A, 58f) | 1 clip pose set | **WRONG-WINDOW** | aki_to_tekken3.py calls `load_anim` from the wrong-window anim_extract.py directly against the ROM; v2's own header deprecates v1 as "built on the misaligned NTSC_U_10 bank" |
| 6 | AKI→Tekken3 retarget v2 output | WH `teardown/wwf-no-mercy/aki_to_tekken3_v2.json` (anim 339A, 58f) | 1 clip pose set | **WRONG-WINDOW (falsely labelled corrected)** | v2 loads `animations/clips/*.npy` — the bank in #1, which was never re-exported after 9976bfb8/772694040; v1 and v2 report identical source_frames (58) for anim 339A; the "CORRECTED bank, NTSC_U_11" label (commit 9c11122f) is not backed by any bank re-export |
| 7 | AKI→Tekken3 retarget v3 + aki-rock-v3 pose JSONs | WH branch `feat/aki-trueclips-w3c-20261021` only (PR #499 OPEN) | 11 clips (mk-1240/1885/2843/3120/3473/3659/4233/4269/4347/4353/4354) | **CORRECT-WINDOW — NOT ON MAIN** | W3c commits 751f04d5/01ff7678: game-exact extractor (FT 0x16C31D8/First 0x1BD150, 1-based) + 12/10/10 record split; true frame counts 70/112/39/13/20/28/102/103/82/17/24. Nothing to fix on main; listed so nobody mistakes the unmerged correction for shipped data |
| 8 | mat-kings move database | WH `moveset-library/movesets/mat-kings-move-database.json` | 4,409 move_clips (per its `_meta.counts`) | **WRONG-WINDOW (linkage)** | Its `_meta` states it is a programmatic join of `animations/manifest.json` (bank #1) + FileTableDB labels + re-docs power tables: the fid→clip/frame linkage inherits the wrong window. The move NAMES and power tables themselves are VPWStudio/re-docs text and are window-independent — only the clip linkage is condemned |
| 9 | Animation index | WH `moveset-library/animations/ANIMATION-INDEX.json` | indexes 5,762 clips (1,353 system + 4,409 move) | **WRONG-WINDOW (inherited)** | Points at `teardown/wwf-no-mercy/animations/clips/` + manifest with rule `anim_id = file_id − 0x3322`; pure index over bank #1 |
| 10 | Move database (mixed-source) | WH `moveset-library/movesets/MOVE-DATABASE.json` | NM-### entries among WMXIX/T7/T3 entries | **WRONG-WINDOW for NM entries only (inherited)** | `_meta.sources` lists the NM move database first; NM entries' `anim_ref`s resolve into bank #1. WMXIX (Yukes .yag/.atr), T7 and T3 (divmot) entries are NOT-NM-DERIVED and unaffected |
| 11 | CAW / name-table parses | WH `teardown/wwf-no-mercy/tools/analyze_nomercy.py`, `caw_parse.py` + outputs | name table @0x168D790, wrestler table @0x168D930 | **CORRECT-WINDOW (window-independent)** | These read fixed absolute ROM tables, not FileTable entries; the FileTable window/ID-base defect cannot affect them |
| 12 | re-docs move database (text) | WH `teardown/wwf-no-mercy/re-docs/docs/moves/move-database.md` | 400+ named moves, Power/KO/Bleed tables | **NOT-WINDOW-DEPENDENT** | Documentation text sourced from VPWStudio data, not from a FileTable decode; only its downstream joins (see #8) inherit the defect |
| 13 | GLB texture sidecars | WH `teardown/wwf-no-mercy/` (3 .glb files on main) + `tools/extract_glb_textures.py` | 3 GLBs | **INDETERMINATE** | extract_glb_textures.py shows no FileTable/anim_extract/window-constant reference in the greps run, and no provenance manifest for the 3 GLBs was found in the searches run. Missing evidence: the GLBs' conversion manifest/provenance — if it exists it lives with the GLB conversion lane's records, not in `teardown/wwf-no-mercy/` |
| 14 | wrestling-game repo (all animation assets) | `mhvnsnt/wrestling-game` | 0 NM assets | **NOT-NM-DERIVED** | Full recursive tree (9,846 paths) contains no `wwf-no-mercy` teardown, no `.npy`, no moveset bank: its animation sources are WMXIX (.yag/.atr), Def Jam FFNY and WWE 2K19 packs. Its `docs/WRESTLING-ANIMATION-PIPELINE.md` *cites* the WH NM bank ("5,787 clips / 3,570 models") and the v2 retarget as planned inputs — a documentation dependency on verdicts #1/#2/#6, but it holds no NM-derived data itself |
| 15 | All other WH `game/assets/movesets/*.json` (96 files) | WH `game/assets/movesets/` | 96 fighter files | **NOT-NM-DERIVED** (except #16 below) | Provenance scan: no NM/AKI source fields; flagged files trace to Tekken 3/7, KOF, SF, VF, DOA sources. The three text hits for "aki" outside #16 are substring/name coincidences (e.g. sf-akuma, vf-akira), not AKI-engine data |

### ⚠ WRONG-WINDOW BANKS WIRED INTO PLAYABLE FIGHTERS — FLAG

| Fighter | File | What is wired | Status |
|---|---|---|---|
| **CORNERSTONE (ryuji-rock)** | WH `game/assets/movesets/ryuji-rock.json` (**on main**) | `cornerstone_build.no_mercy_wired` section + move entries referencing mat-kings IDs MK-1240, MK-1885, MK-2843, MK-3473, MK-4353 … and bank clips anim_37FA, anim_3E3D, anim_40B3, anim_441D, anim_4423 … — i.e. references into WRONG-WINDOW banks #1 and #8 | Playable fighter file on main carrying wrong-window-derived NM move references and frame data. Mitigating fact, stated plainly: the file's own `aki_bake` gate records show the converted pose rows FAILED the W3 gate and no baked pose rows shipped — what is live on main is the reference/frame-data layer, not converted poses. Per this lane's orders NOTHING was changed; the fix is a separate per-character lane (W3c's corrective scope covers The Rock clip set) |
| **PANTERA** | WH `moveset-library/movesets/pantera-moveset.json` (library, not the game file) | References MK-0125 / NM-001 + mat-kings (bank #8) | Library-level only in the searches run: `game/assets/movesets/pantera.json` contains no MK-/NM- references, so Pantera's playable file is NOT flagged; the library assignment is wrong-window-derived and must be re-based before any future consumption |
| **(stages, not a fighter)** | WH `game/js/stages.js` | 17 No Mercy arena assemblies (bank #4) wired as playable stages (`NO_MERCY` table, "WWF NO MERCY ARENAS") | Playable stage content assembled from WRONG-WINDOW banks #2/#3. Flagged for completeness; fix is a separate lane |

### Frame counts do not exculpate
Per the W3b proof and this audit's mandate: the bank's frame counts,
manifest totals (5,787 clips, histogram-plausible shapes — local spot
check: `anim_339A.npy` = (58, 26, 3) int16) and the v2 retarget's
"motion correlation 0.69–1.0" claims were all produced under the wrong
window and are consistent with spliced wrong-file decodes. No verdict
above relies on counts looking plausible; each rests on extractor code,
git history, or W3c's true-window comparison.

### Files searched
- WH (clone `~/workspace/_w3b-work/wh`, `origin/main` unless noted):
  `teardown/wwf-no-mercy/tools/{anim_extract,extract_all_anims,
  extract_all_models,extract_textures,assemble_arenas,extract_glb_textures,
  caw_parse,analyze_nomercy}.py` (current + `git show` at 772694040 and
  9976bfb8), `teardown/wwf-no-mercy/{aki_to_tekken3.py,aki_to_tekken3_v2.py,
  aki_to_tekken3_v1.json,aki_to_tekken3_v2.json,animations/manifest.json,
  animations/FORMAT.md,models/manifest.json}`,
  `git log` for the tools, the clips directory and the manifest;
  `game/assets/movesets/*.json` (96 files, provenance scan + full read of
  ryuji-rock.json/ryuji.json), `game/js/stages.js`,
  `moveset-library/{movesets/mat-kings-move-database.json,
  movesets/MOVE-DATABASE.json,movesets/pantera-moveset.json,
  animations/ANIMATION-INDEX.json}`; PR list for AKI lanes (#447/#458/#499
  OPEN, #25/#39/#379 MERGED).
- wrestling-game: GitHub API recursive tree (9,846 paths) +
  `docs/WRESTLING-ANIMATION-PIPELINE.md` full read.
- Checkpoints: `gap-closure-w3b-aki-fk-ik.json` (ground truth),
  `gap-closure-audit-nm-window-20261021.json` (this lane).

## Self-check ticked - [x]
- [x] Read-only: no bank, converter, extractor, moveset or game-data file modified; only writes are this doc (docs-only PR, not merged) and the lane checkpoint
- [x] Every verdict cites code, git history, a manifest, or the W3b/W3c proof — no verdict rests on frame counts or plausibility
- [x] INDETERMINATE used where evidence is missing (#13), with the missing evidence and its likely home named
- [x] Wrong-window playable content flagged by name: CORNERSTONE / ryuji-rock.json (fighter, on main), Pantera (library-level only — playable file cleared), No Mercy arenas in stages.js
- [x] wrestling-game explicitly cleared of NM-derived assets, with its documentation dependency on the WH bank noted
- [x] The false "corrected bank" claims (commit 772694040, v2 header, models/textures docstrings) documented with the contradicting code, so no future lane trusts the labels over the constants
