# WMXIX (mat-legends) — WIRING INVENTORY

**Game:** WWE WrestleMania XIX (GameCube) — WH universe name: `mat-legends` (root `RENAME-MAP.md` universe table)
**Lane:** Full Wiring + Canon Conversion, WMXIX sub-lane, 2026-10-20
**Count method:** GitHub git-trees API for `main` (recursive, `truncated: false`), counted 2026-10-20. Every blob under both prefixes is listed below with path, extension type, byte size, description, and wiring status.
**Totals:** `teardown/wmxix/` = **1,560 files / 61,751,278 bytes**; `teardown/wwe-wrestlemania-xix/` = **148 files / 3,168,273 bytes**; **combined 1,708 files**.

## TEARDOWN STATE (audit baseline — not re-solved by this lane)

The teardown is SOLVED and closed (2026-10-17): `assemble_wrestler_v2.py` reproduces the assembly solution exactly (max diff 5e-05); YMG bone coords are Y-Z-X order (perm 1,0,2); DOL ground truth verified. 170/170 ringmotion YANM clips decoded to JSON (169 clean; `c138_0a` is a 72-byte stub — see `teardown/wmxix/TEARDOWN.md` section 5). Arena geometry: 40 non-empty OBJ point clouds, 324,425 vertices; face indices OPEN (`teardown/wmxix/arenas/ARENA-FORMAT.md`).

## RECONCILIATION — the two folders

| | `teardown/wmxix/` (1,560) | `teardown/wwe-wrestlemania-xix/` (148) |
|---|---|---|
| Nature | **Extracted asset store** | **Research / solver store** |
| Holds | 1,169 arena texture PNGs, 170 animation clip JSONs, 127 wrestler OBJs, 44 arena files, CAW catalog, ECD render-test proofs, asset docs (`TEARDOWN.md`, `ARENA-UNIVERSE-MAP.md`) | 68 Python tools (YANM/YOBJ decoders, retarget, DOL probes), 53 docs (format specs, skinning solution, assembly solution), retarget maps (`yanm_to_tekken3_v1/v2.json`, `aki_to_tekken3_v1.json`), skeleton data, proof OBJs/renders |
| Unique to it | ALL bulk assets (animations, textures, wrestler/arena geometry, CAW catalog) | ALL solver tooling + retarget maps + `docs/WMXIX-FILE-LISTING.txt` (237,733 B ISO listing) + `WRESTLER-SKELETON.md`, `WMXIX-ASSEMBLY-SOLUTION.md`, `docs/YOBJ-SKINNING-SOLUTION.md` |
| Canonical for | Asset data: animations, arenas, textures, wrestler geometry, CAW catalog | Format/research truth: YANM/YOBJ formats, skinning/assembly solutions, retarget maps, skeleton |

**Overlap:** 37 files are byte-identical in both folders (same git blob SHA): 5 root YANM cycle docs (ITEM6/7/8/9/10), `atr_all_events.json`, and all 31 `ecd-render-test/` files (at `teardown/wmxix/ecd-render-test/` and at `teardown/wwe-wrestlemania-xix/docs/ecd-render-test/`).
**Divergent same-name files (NOT identical):** `YANM-ITEM5-CYCLE.md` exists in both with different content (`wmxix` 6,984 B vs `wwe-wrestlemania-xix` 8,311 B) — the research folder's copy is the longer one; `YANM-ITEM3-ITEM4-CYCLE.md`, `YANM-UNKNOWN8.md`, `YANM-F32-CORR.md`, `YANM-FIRST8B.md` exist ONLY in the research folder. Research docs are canonical in `teardown/wwe-wrestlemania-xix/`; asset docs are canonical in `teardown/wmxix/`.
**Verdict:** The folders are complementary, not duplicates: assets vs research. Canonical going forward — assets: `teardown/wmxix/`; research/format/solvers: `teardown/wwe-wrestlemania-xix/`. The planned physical renames in `teardown/wmxix/docs/RENAME-ENTRIES-WMXIX.md` (`teardown/mat-legends/`, `teardown/mat-legends-research/`) remain PLANNED and owner/watchdog-gated; this lane did NOT execute them and deleted nothing. Open PR #332 adds a third slice (`docs/skinning-solver-20261016/` + `work/` disassembly) into the research folder — consistent with the research-canonical verdict (WIRED-PENDING-MERGE #332).

## WIRING AUDIT SUMMARY (state BEFORE this PR)

| Asset group | Files | State before | Evidence |
|---|---|---|---|
| Animation clips (`wmxix/animations/`) | 170 | INDEXED-ONLY | `moveset-library/animations/ANIMATION-INDEX.json` has a `wwe_wrestlemania_xix` source entry (path + count 170) but ZERO WMXIX clips in any category; all categories are No Mercy clips |
| Moves (library) | 0 entries | NOT WIRED | `moveset-library/movesets/MOVE-DATABASE.json` cites WMXIX in `_meta.sources` but contains zero `WMXIX-###` entries (only NM/T7/WH samples) |
| Arenas (`wmxix/arenas/` + textures) | 44 + 1,169 | DOC-ONLY | Canon mapping exists in `ARENA-UNIVERSE-MAP.md`; `game/js/stages.js` registers 8 procedural canon lands + T3 retro + `nm-` No Mercy stages — no WMXIX stage entry, no WMXIX geometry loaded |
| Wrestler models (`wmxix/wrestlers/`) | 127 | ACCOUNTED-ELSEWHERE | Federation rule: character models belong to mhvnsnt/wrestling-game + mhvnsnt/wrestlemania-xix-mod; WH keeps mechanics + teardown |
| CAW parts catalog (`wmxix/caw-parts/`) | 2 | NOT WIRED | `customization/PARTS-REGISTRY.json` (1,222,194 B) has no WMXIX part entries; `game/js/custom-fighter.js` reads Creation Suite profiles only |
| Revenge Mode (mode design) | docs | NOT WIRED | `game/js/modes.js` modes: ARCADE/VERSUS/SURVIVAL/TIME ATTACK/TEAM BATTLE/TRAINING/STORY — no Revenge/traversal mode |
| Tools + research docs | 121+ | PIPELINE | Consumed by the RE/retarget pipeline (retarget maps referenced by the anim pipeline), not by the game build |
| ECD render-test proofs | 31 x2 copies | PROOF | Verification artifacts for the ECD/retarget decode; no game consumption expected |
| Root canon docs | — | NOT WIRED | `CANON.md` and `ROSTER.md` contain zero WMXIX/mat-legends entries (grep-verified 2026-10-20) |

## WHAT THIS PR WIRES

| Deliverable | Contents |
|---|---|
| `moveset-library/animations/WMXIX-CLIP-INDEX.json` | All 170 clips with canon IDs (`ML-<CLIP>`), bank (a x35, b x24, c x105, d x6), size, SHA, decode status |
| `moveset-library/movesets/WMXIX-MOVES.json` | 169 move entries (stub `c138_0a` excluded) in MOVE-DATABASE schema + Tekken input map for the grapple slot family (federation rule) |
| `game/assets/stages/mat-legends/stages.json` | 12 stage entries following the `game/assets/stages/sf-ex/stages.json` pattern: 3 main arenas, ring, kaijo, 4 backstage sets, cage, Hell-cell, Revenge packages — each with its WH canon target from `ARENA-UNIVERSE-MAP.md` |
| `customization/mat-legends-caw.json` | CAW catalog index (2,690 parts by category/extension/format) pointing at `teardown/wmxix/caw-parts/files.tsv` |
| `teardown/wmxix/CANON-CONVERSION.md` | Per-game canon conversion record (source of truth for this game) |
| Root `CANON.md` + `RENAME-MAP.md` | Appended delimited mat-legends sections only |

## FULL FILE INVENTORY

### teardown/wmxix/ — 1560 files

| Path | Type | Size (bytes) | What it is | Wiring status |
|---|---|---|---|---|
| `teardown/wmxix/ARENA-UNIVERSE-MAP.md` | .md | 22404 | Teardown/research documentation (Markdown) | CANON (conversion source of truth) |
| `teardown/wmxix/TEARDOWN.md` | .md | 29626 | Teardown/research documentation (Markdown) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wmxix/YANM-ITEM10-CYCLE.md` | .md | 8988 | Teardown/research documentation (Markdown) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wmxix/YANM-ITEM5-CYCLE.md` | .md | 6984 | Teardown/research documentation (Markdown) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wmxix/YANM-ITEM6-CYCLE.md` | .md | 15684 | Teardown/research documentation (Markdown) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wmxix/YANM-ITEM7-CYCLE.md` | .md | 5842 | Teardown/research documentation (Markdown) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wmxix/YANM-ITEM8-CYCLE.md` | .md | 5417 | Teardown/research documentation (Markdown) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wmxix/YANM-ITEM9-CYCLE.md` | .md | 6179 | Teardown/research documentation (Markdown) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wmxix/animations/a.json` | .json | 404805 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/a000_0a.json` | .json | 103132 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/a001_0a.json` | .json | 134854 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/a002_0a.json` | .json | 129832 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/a003_0a.json` | .json | 96119 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/a004_0a.json` | .json | 116856 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/a005_0a.json` | .json | 166727 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/a006_0a.json` | .json | 175638 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/a007_0a.json` | .json | 101965 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/a008_0a.json` | .json | 123464 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/a009_0a.json` | .json | 119232 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/a010_0a.json` | .json | 140872 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/a011_0a.json` | .json | 159841 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/a012_0a.json` | .json | 117977 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/a013_0a.json` | .json | 113063 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/a014_0a.json` | .json | 127981 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/a015_0a.json` | .json | 110120 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/a016_0a.json` | .json | 115789 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/a017_0a.json` | .json | 114923 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/a018_0a.json` | .json | 99650 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/a019_0a.json` | .json | 120209 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/a020_0a.json` | .json | 145131 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/a021_0a.json` | .json | 127569 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/a022_0a.json` | .json | 112815 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/a023_0a.json` | .json | 158814 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/a024_0a.json` | .json | 138878 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/a025_0a.json` | .json | 90732 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/a026_0a.json` | .json | 141175 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/a027_0a.json` | .json | 108812 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/a028_0a.json` | .json | 164273 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/a029_0a.json` | .json | 225924 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/a030_0a.json` | .json | 229032 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/a031_0a.json` | .json | 187883 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/a032_0a.json` | .json | 201393 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/a033_0a.json` | .json | 6551 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/b.json` | .json | 47615 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/b000_0a.json` | .json | 344880 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/b001_0a.json` | .json | 216255 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/b002_0a.json` | .json | 268902 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/b003_0a.json` | .json | 288716 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/b004_0a.json` | .json | 183596 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/b005_0a.json` | .json | 332283 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/b006_0a.json` | .json | 188951 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/b007_0a.json` | .json | 260566 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/b008_0a.json` | .json | 260362 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/b009_0a.json` | .json | 312007 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/b010_0a.json` | .json | 219063 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/b011_0a.json` | .json | 223354 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/b012_0a.json` | .json | 220990 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/b013_0a.json` | .json | 283841 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/b014_0a.json` | .json | 248334 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/b015_0a.json` | .json | 244245 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/b016_0a.json` | .json | 263957 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/b017_0a.json` | .json | 250310 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/b018_0a.json` | .json | 61392 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/b019_0a.json` | .json | 245186 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/b020_0a.json` | .json | 196896 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/b021_0a.json` | .json | 194323 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/b022_0a.json` | .json | 316856 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c.json` | .json | 187990 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c000_0a.json` | .json | 323925 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c001_0a.json` | .json | 519846 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c002_0a.json` | .json | 101788 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c003_0a.json` | .json | 39477 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c004_0a.json` | .json | 128975 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c005_0a.json` | .json | 197605 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c006_0a.json` | .json | 100717 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c007_0a.json` | .json | 187627 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c008_0a.json` | .json | 133502 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c009_0a.json` | .json | 193613 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c010_0a.json` | .json | 189791 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c011_0a.json` | .json | 150899 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c012_0a.json` | .json | 159816 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c013_0a.json` | .json | 272870 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c014_0a.json` | .json | 180904 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c015_0a.json` | .json | 144695 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c016_0a.json` | .json | 127063 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c017_0a.json` | .json | 188733 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c100_0a.json` | .json | 547230 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c101_0a.json` | .json | 944668 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c102_0a.json` | .json | 461726 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c103_0a.json` | .json | 745981 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c104_0a.json` | .json | 175642 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c105_0a.json` | .json | 350794 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c106_0a.json` | .json | 62149 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c107_0a.json` | .json | 332529 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c108_0a.json` | .json | 291757 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c109_0a.json` | .json | 307230 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c110_0a.json` | .json | 509950 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c111_0a.json` | .json | 395757 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c112_0a.json` | .json | 477546 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c113_0a.json` | .json | 207673 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c114_0a.json` | .json | 371459 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c115_0a.json` | .json | 159288 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c116_0a.json` | .json | 357890 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c117_0a.json` | .json | 231029 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c118_0a.json` | .json | 307096 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c119_0a.json` | .json | 174623 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c120_0a.json` | .json | 338042 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c121_0a.json` | .json | 212907 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c122_0a.json` | .json | 196586 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c123_0a.json` | .json | 313574 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c124_0a.json` | .json | 307857 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c125_0a.json` | .json | 236293 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c126_0a.json` | .json | 159586 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c127_0a.json` | .json | 145574 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c128_0a.json` | .json | 205996 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c129_0a.json` | .json | 142476 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c130_0a.json` | .json | 193635 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c131_0a.json` | .json | 189789 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c132_0a.json` | .json | 213378 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c133_0a.json` | .json | 151448 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c134_0a.json` | .json | 89276 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c135_0a.json` | .json | 190680 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c136_0a.json` | .json | 159822 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c137_0a.json` | .json | 272905 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c138_0a.json` | .json | 277 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c138_0b.json` | .json | 283041 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c139_0a.json` | .json | 108387 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c140_0a.json` | .json | 139842 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c141_0a.json` | .json | 162327 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c142_0a.json` | .json | 197067 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c143_0a.json` | .json | 180901 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c144_0a.json` | .json | 145287 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c145_0a.json` | .json | 127552 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c146_0a.json` | .json | 121595 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c147_0a.json` | .json | 188733 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c200_0.json` | .json | 38049 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c200_0a.json` | .json | 38087 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c200_1a.json` | .json | 110908 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c200_2a.json` | .json | 101165 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c201_0a.json` | .json | 291740 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c202_0a.json` | .json | 275934 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c203_0a.json` | .json | 269651 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c204_0a.json` | .json | 206539 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c205_0a.json` | .json | 183138 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c206_0a.json` | .json | 166497 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c207_0a.json` | .json | 176986 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c208_0a.json` | .json | 284539 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c209_0a.json` | .json | 229743 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c210_0a.json` | .json | 268080 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c211_0a.json` | .json | 216317 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c212_0a.json` | .json | 90238 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c213_0a.json` | .json | 177919 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c214_0a.json` | .json | 195194 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c215_0a.json` | .json | 119843 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c216_0a.json` | .json | 114740 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c217_0a.json` | .json | 174699 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c218_0a.json` | .json | 159490 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c219_0a.json` | .json | 145531 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c220_0a.json` | .json | 205995 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c221_0a.json` | .json | 142565 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c222_0a.json` | .json | 213375 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c223_0a.json` | .json | 190730 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c224_0a.json` | .json | 60086 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c224_1a.json` | .json | 240106 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c225_0a.json` | .json | 114014 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c226_0a.json` | .json | 140603 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c227_0a.json` | .json | 197065 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c228_0a.json` | .json | 121726 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c400_0a.json` | .json | 385163 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c401_0a.json` | .json | 133393 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c402_0a.json` | .json | 89226 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/c403_0a.json` | .json | 162327 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/d000_0a.json` | .json | 21233 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/d100_0a.json` | .json | 22486 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/d101_0a.json` | .json | 19831 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/d102_0a.json` | .json | 22825 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/d103_0a.json` | .json | 20903 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/animations/d107_0a.json` | .json | 22219 | YANM animation clip JSON (decoded ringmotion .yag; 29 tracks, 70-bone Yukes skeleton) | WIRED (this PR: WMXIX-CLIP-INDEX.json + WMXIX-MOVES.json) |
| `teardown/wmxix/arenas/00.obj` | .obj | 353279 | Arena geometry OBJ (vertex point cloud, faces open — see ARENA-FORMAT.md) | WIRED-DATA (this PR: game/assets/stages/mat-legends/stages.json; engine loader hook flagged) |
| `teardown/wmxix/arenas/01.obj` | .obj | 306357 | Arena geometry OBJ (vertex point cloud, faces open — see ARENA-FORMAT.md) | WIRED-DATA (this PR: game/assets/stages/mat-legends/stages.json; engine loader hook flagged) |
| `teardown/wmxix/arenas/02.obj` | .obj | 244810 | Arena geometry OBJ (vertex point cloud, faces open — see ARENA-FORMAT.md) | WIRED-DATA (this PR: game/assets/stages/mat-legends/stages.json; engine loader hook flagged) |
| `teardown/wmxix/arenas/0_0.obj` | .obj | 473781 | Arena geometry OBJ (vertex point cloud, faces open — see ARENA-FORMAT.md) | WIRED-DATA (this PR: game/assets/stages/mat-legends/stages.json; engine loader hook flagged) |
| `teardown/wmxix/arenas/0_0_ad2.obj` | .obj | 37864 | Arena geometry OBJ (vertex point cloud, faces open — see ARENA-FORMAT.md) | WIRED-DATA (this PR: game/assets/stages/mat-legends/stages.json; engine loader hook flagged) |
| `teardown/wmxix/arenas/0_1.obj` | .obj | 351758 | Arena geometry OBJ (vertex point cloud, faces open — see ARENA-FORMAT.md) | WIRED-DATA (this PR: game/assets/stages/mat-legends/stages.json; engine loader hook flagged) |
| `teardown/wmxix/arenas/0_1_ad2.obj` | .obj | 6104 | Arena geometry OBJ (vertex point cloud, faces open — see ARENA-FORMAT.md) | WIRED-DATA (this PR: game/assets/stages/mat-legends/stages.json; engine loader hook flagged) |
| `teardown/wmxix/arenas/0_2.obj` | .obj | 551041 | Arena geometry OBJ (vertex point cloud, faces open — see ARENA-FORMAT.md) | WIRED-DATA (this PR: game/assets/stages/mat-legends/stages.json; engine loader hook flagged) |
| `teardown/wmxix/arenas/0_2_ad2.obj` | .obj | 40117 | Arena geometry OBJ (vertex point cloud, faces open — see ARENA-FORMAT.md) | WIRED-DATA (this PR: game/assets/stages/mat-legends/stages.json; engine loader hook flagged) |
| `teardown/wmxix/arenas/0_3.obj` | .obj | 404208 | Arena geometry OBJ (vertex point cloud, faces open — see ARENA-FORMAT.md) | WIRED-DATA (this PR: game/assets/stages/mat-legends/stages.json; engine loader hook flagged) |
| `teardown/wmxix/arenas/0_3_ad2.obj` | .obj | 9637 | Arena geometry OBJ (vertex point cloud, faces open — see ARENA-FORMAT.md) | WIRED-DATA (this PR: game/assets/stages/mat-legends/stages.json; engine loader hook flagged) |
| `teardown/wmxix/arenas/1_0.obj` | .obj | 305031 | Arena geometry OBJ (vertex point cloud, faces open — see ARENA-FORMAT.md) | WIRED-DATA (this PR: game/assets/stages/mat-legends/stages.json; engine loader hook flagged) |
| `teardown/wmxix/arenas/1_0_ad2.obj` | .obj | 27382 | Arena geometry OBJ (vertex point cloud, faces open — see ARENA-FORMAT.md) | WIRED-DATA (this PR: game/assets/stages/mat-legends/stages.json; engine loader hook flagged) |
| `teardown/wmxix/arenas/1_1.obj` | .obj | 379183 | Arena geometry OBJ (vertex point cloud, faces open — see ARENA-FORMAT.md) | WIRED-DATA (this PR: game/assets/stages/mat-legends/stages.json; engine loader hook flagged) |
| `teardown/wmxix/arenas/1_1_ad2.obj` | .obj | 86264 | Arena geometry OBJ (vertex point cloud, faces open — see ARENA-FORMAT.md) | WIRED-DATA (this PR: game/assets/stages/mat-legends/stages.json; engine loader hook flagged) |
| `teardown/wmxix/arenas/1_2.obj` | .obj | 305478 | Arena geometry OBJ (vertex point cloud, faces open — see ARENA-FORMAT.md) | WIRED-DATA (this PR: game/assets/stages/mat-legends/stages.json; engine loader hook flagged) |
| `teardown/wmxix/arenas/1_2_ad2.obj` | .obj | 79984 | Arena geometry OBJ (vertex point cloud, faces open — see ARENA-FORMAT.md) | WIRED-DATA (this PR: game/assets/stages/mat-legends/stages.json; engine loader hook flagged) |
| `teardown/wmxix/arenas/1_3.obj` | .obj | 320742 | Arena geometry OBJ (vertex point cloud, faces open — see ARENA-FORMAT.md) | WIRED-DATA (this PR: game/assets/stages/mat-legends/stages.json; engine loader hook flagged) |
| `teardown/wmxix/arenas/1_3_ad2.obj` | .obj | 79984 | Arena geometry OBJ (vertex point cloud, faces open — see ARENA-FORMAT.md) | WIRED-DATA (this PR: game/assets/stages/mat-legends/stages.json; engine loader hook flagged) |
| `teardown/wmxix/arenas/1_4.obj` | .obj | 334212 | Arena geometry OBJ (vertex point cloud, faces open — see ARENA-FORMAT.md) | WIRED-DATA (this PR: game/assets/stages/mat-legends/stages.json; engine loader hook flagged) |
| `teardown/wmxix/arenas/1_4_ad2.obj` | .obj | 86264 | Arena geometry OBJ (vertex point cloud, faces open — see ARENA-FORMAT.md) | WIRED-DATA (this PR: game/assets/stages/mat-legends/stages.json; engine loader hook flagged) |
| `teardown/wmxix/arenas/2_0.obj` | .obj | 479695 | Arena geometry OBJ (vertex point cloud, faces open — see ARENA-FORMAT.md) | WIRED-DATA (this PR: game/assets/stages/mat-legends/stages.json; engine loader hook flagged) |
| `teardown/wmxix/arenas/2_0_ad.obj` | .obj | 3139 | Arena geometry OBJ (vertex point cloud, faces open — see ARENA-FORMAT.md) | WIRED-DATA (this PR: game/assets/stages/mat-legends/stages.json; engine loader hook flagged) |
| `teardown/wmxix/arenas/2_0_ad2.obj` | .obj | 41725 | Arena geometry OBJ (vertex point cloud, faces open — see ARENA-FORMAT.md) | WIRED-DATA (this PR: game/assets/stages/mat-legends/stages.json; engine loader hook flagged) |
| `teardown/wmxix/arenas/2_1.obj` | .obj | 481921 | Arena geometry OBJ (vertex point cloud, faces open — see ARENA-FORMAT.md) | WIRED-DATA (this PR: game/assets/stages/mat-legends/stages.json; engine loader hook flagged) |
| `teardown/wmxix/arenas/2_1_ad2.obj` | .obj | 62189 | Arena geometry OBJ (vertex point cloud, faces open — see ARENA-FORMAT.md) | WIRED-DATA (this PR: game/assets/stages/mat-legends/stages.json; engine loader hook flagged) |
| `teardown/wmxix/arenas/2_2.obj` | .obj | 353227 | Arena geometry OBJ (vertex point cloud, faces open — see ARENA-FORMAT.md) | WIRED-DATA (this PR: game/assets/stages/mat-legends/stages.json; engine loader hook flagged) |
| `teardown/wmxix/arenas/2_2_ad2.obj` | .obj | 52179 | Arena geometry OBJ (vertex point cloud, faces open — see ARENA-FORMAT.md) | WIRED-DATA (this PR: game/assets/stages/mat-legends/stages.json; engine loader hook flagged) |
| `teardown/wmxix/arenas/5_0.obj` | .obj | 64105 | Arena geometry OBJ (vertex point cloud, faces open — see ARENA-FORMAT.md) | WIRED-DATA (this PR: game/assets/stages/mat-legends/stages.json; engine loader hook flagged) |
| `teardown/wmxix/arenas/5_1.obj` | .obj | 60094 | Arena geometry OBJ (vertex point cloud, faces open — see ARENA-FORMAT.md) | WIRED-DATA (this PR: game/assets/stages/mat-legends/stages.json; engine loader hook flagged) |
| `teardown/wmxix/arenas/ARENA-FORMAT.md` | .md | 4619 | Arena format documentation | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wmxix/arenas/README.md` | .md | 1048 | Arena format documentation | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wmxix/arenas/add_x8.obj` | .obj | 1229 | Arena geometry OBJ (vertex point cloud, faces open — see ARENA-FORMAT.md) | WIRED-DATA (this PR: game/assets/stages/mat-legends/stages.json; engine loader hook flagged) |
| `teardown/wmxix/arenas/eff_x8.obj` | .obj | 30936 | Arena geometry OBJ (vertex point cloud, faces open — see ARENA-FORMAT.md) | WIRED-DATA (this PR: game/assets/stages/mat-legends/stages.json; engine loader hook flagged) |
| `teardown/wmxix/arenas/extract_all_arenas.py` | .py | 3356 | Arena extraction tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wmxix/arenas/f01.obj` | .obj | 39563 | Arena geometry OBJ (vertex point cloud, faces open — see ARENA-FORMAT.md) | WIRED-DATA (this PR: game/assets/stages/mat-legends/stages.json; engine loader hook flagged) |
| `teardown/wmxix/arenas/gt_x8.obj` | .obj | 2472 | Arena geometry OBJ (vertex point cloud, faces open — see ARENA-FORMAT.md) | WIRED-DATA (this PR: game/assets/stages/mat-legends/stages.json; engine loader hook flagged) |
| `teardown/wmxix/arenas/kaijo_x8.obj` | .obj | 312419 | Arena geometry OBJ (vertex point cloud, faces open — see ARENA-FORMAT.md) | WIRED-DATA (this PR: game/assets/stages/mat-legends/stages.json; engine loader hook flagged) |
| `teardown/wmxix/arenas/post.obj` | .obj | 677 | Arena geometry OBJ (vertex point cloud, faces open — see ARENA-FORMAT.md) | WIRED-DATA (this PR: game/assets/stages/mat-legends/stages.json; engine loader hook flagged) |
| `teardown/wmxix/arenas/ring.obj` | .obj | 16439 | Arena geometry OBJ (vertex point cloud, faces open — see ARENA-FORMAT.md) | WIRED-DATA (this PR: game/assets/stages/mat-legends/stages.json; engine loader hook flagged) |
| `teardown/wmxix/arenas/s2_ad2.obj` | .obj | 88146 | Arena geometry OBJ (vertex point cloud, faces open — see ARENA-FORMAT.md) | WIRED-DATA (this PR: game/assets/stages/mat-legends/stages.json; engine loader hook flagged) |
| `teardown/wmxix/arenas/scr_wm.obj` | .obj | 687 | Arena geometry OBJ (vertex point cloud, faces open — see ARENA-FORMAT.md) | WIRED-DATA (this PR: game/assets/stages/mat-legends/stages.json; engine loader hook flagged) |
| `teardown/wmxix/arenas/scr_x8.obj` | .obj | 1625 | Arena geometry OBJ (vertex point cloud, faces open — see ARENA-FORMAT.md) | WIRED-DATA (this PR: game/assets/stages/mat-legends/stages.json; engine loader hook flagged) |
| `teardown/wmxix/arenas/yobj_arena_extract.py` | .py | 4418 | Arena extraction tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wmxix/atr_all_events.json` | .json | 242384 | Research data JSON (decode/retarget/mapping data) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wmxix/catalog_caw.py` | .py | 3652 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wmxix/caw-parts/CATALOG.md` | .md | 2144 | CAW (create-a-wrestler) parts catalog data | WIRED-DATA (this PR: customization/mat-legends-caw.json index) |
| `teardown/wmxix/caw-parts/files.tsv` | .tsv | 158114 | CAW (create-a-wrestler) parts catalog data | WIRED-DATA (this PR: customization/mat-legends-caw.json index) |
| `teardown/wmxix/decode_tpl.py` | .py | 6280 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wmxix/docs/RENAME-ENTRIES-WMXIX.md` | .md | 1499 | Teardown/research documentation (Markdown) | CANON (conversion source of truth) |
| `teardown/wmxix/docs/YANM-LR-COORD-FINDINGS.md` | .md | 3645 | Teardown/research documentation (Markdown) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wmxix/ecd-render-test/8503_0a_highpreset_view.png` | .png | 35156 | ECD/retarget render-test proof artifact | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wmxix/ecd-render-test/FACE_ecd_view.png` | .png | 24516 | ECD/retarget render-test proof artifact | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wmxix/ecd-render-test/FACE_front.png` | .png | 21568 | ECD/retarget render-test proof artifact | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wmxix/ecd-render-test/FACE_standard.png` | .png | 39636 | ECD/retarget render-test proof artifact | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wmxix/ecd-render-test/FACE_top.png` | .png | 62261 | ECD/retarget render-test proof artifact | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wmxix/ecd-render-test/FIGHTING_ecd_view.png` | .png | 23369 | ECD/retarget render-test proof artifact | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wmxix/ecd-render-test/FIGHTING_front.png` | .png | 23075 | ECD/retarget render-test proof artifact | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wmxix/ecd-render-test/FIGHTING_standard.png` | .png | 43255 | ECD/retarget render-test proof artifact | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wmxix/ecd-render-test/FIGHTING_top.png` | .png | 65769 | ECD/retarget render-test proof artifact | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wmxix/ecd-render-test/a004_0a_highpreset_view.png` | .png | 29132 | ECD/retarget render-test proof artifact | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wmxix/ecd-render-test/c139_0a_highpreset_view.png` | .png | 32165 | ECD/retarget render-test proof artifact | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wmxix/ecd-render-test/c139_control_below.png` | .png | 31909 | ECD/retarget render-test proof artifact | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wmxix/ecd-render-test/c200_0a_ecd_view.png` | .png | 56317 | ECD/retarget render-test proof artifact | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wmxix/ecd-render-test/c200_0a_front.png` | .png | 23482 | ECD/retarget render-test proof artifact | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wmxix/ecd-render-test/c200_0a_standard.png` | .png | 42910 | ECD/retarget render-test proof artifact | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wmxix/ecd-render-test/c200_0a_top.png` | .png | 64823 | ECD/retarget render-test proof artifact | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wmxix/ecd-render-test/c200_1a_ecd_view.png` | .png | 21427 | ECD/retarget render-test proof artifact | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wmxix/ecd-render-test/c200_1a_front.png` | .png | 23104 | ECD/retarget render-test proof artifact | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wmxix/ecd-render-test/c200_1a_standard.png` | .png | 42263 | ECD/retarget render-test proof artifact | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wmxix/ecd-render-test/c200_1a_top.png` | .png | 65791 | ECD/retarget render-test proof artifact | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wmxix/ecd-render-test/c200_2a_ecd_view.png` | .png | 20883 | ECD/retarget render-test proof artifact | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wmxix/ecd-render-test/c200_2a_front.png` | .png | 23170 | ECD/retarget render-test proof artifact | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wmxix/ecd-render-test/c200_2a_standard.png` | .png | 42644 | ECD/retarget render-test proof artifact | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wmxix/ecd-render-test/c200_2a_top.png` | .png | 65567 | ECD/retarget render-test proof artifact | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wmxix/ecd-render-test/ecd_all_clips.json` | .json | 18674 | ECD/retarget render-test proof artifact | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wmxix/ecd-render-test/highpreset_metrics.json` | .json | 2634 | ECD/retarget render-test proof artifact | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wmxix/ecd-render-test/metrics.json` | .json | 6630 | ECD/retarget render-test proof artifact | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wmxix/ecd-render-test/showcase8503_ecd_view.png` | .png | 37691 | ECD/retarget render-test proof artifact | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wmxix/ecd-render-test/showcase8503_front.png` | .png | 23728 | ECD/retarget render-test proof artifact | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wmxix/ecd-render-test/showcase8503_standard.png` | .png | 43492 | ECD/retarget render-test proof artifact | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wmxix/ecd-render-test/showcase8503_top.png` | .png | 66651 | ECD/retarget render-test proof artifact | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wmxix/extract_arena_textures.py` | .py | 3268 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wmxix/extract_wrestlers.py` | .py | 10465 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wmxix/extract_yanm.py` | .py | 6520 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wmxix/textures/00/RW01.png` | .png | 20345 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/add.png` | .png | 30089 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/ar_00.png` | .png | 21820 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/ar_04.png` | .png | 11949 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/ar_06.png` | .png | 377 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/ar_07.png` | .png | 7687 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/ar_08.png` | .png | 4687 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/ar_09.png` | .png | 4312 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/ar_a3.png` | .png | 63872 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/kage.png` | .png | 733 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/kan01.png` | .png | 4121 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/kan04.png` | .png | 949 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/kan05.png` | .png | 3420 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/kan06.png` | .png | 155 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/l_phon.png` | .png | 807 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/rope.png` | .png | 1341 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/rr_16.png` | .png | 374 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/rr_23.png` | .png | 230 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/rr_31.png` | .png | 2506 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/rr_32.png` | .png | 458 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/rr_38.png` | .png | 3268 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/rr_54.png` | .png | 2639 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/rr_57.png` | .png | 2138 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/rr_66.png` | .png | 755 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/rr_71.png` | .png | 2229 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/rr_76.png` | .png | 1944 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/rr_78.png` | .png | 4972 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/rw02.png` | .png | 1877 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/rw03.png` | .png | 2482 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/rw05.png` | .png | 14674 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/rw06.png` | .png | 16783 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/rw07.png` | .png | 2148 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/rw08.png` | .png | 2331 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/rw09.png` | .png | 16767 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/rw10.png` | .png | 1421 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/rw11.png` | .png | 10308 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/rw12.png` | .png | 4732 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/rw13.png` | .png | 20129 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/rw14.png` | .png | 13653 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/rw16.png` | .png | 5556 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/rw18.png` | .png | 94562 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/rw19.png` | .png | 1268 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/rw20.png` | .png | 532 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/rw21.png` | .png | 25288 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/rw22.png` | .png | 1222 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/rw23.png` | .png | 230 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/rw24.png` | .png | 1573 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/rw25.png` | .png | 1081 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/rw26.png` | .png | 2440 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/rw27.png` | .png | 27039 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/rw28.png` | .png | 19567 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/rw29.png` | .png | 2009 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/rw30.png` | .png | 41892 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/rw31.png` | .png | 14459 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/rw32.png` | .png | 18420 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/rw33.png` | .png | 5095 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/rw34.png` | .png | 6820 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/rw35.png` | .png | 9404 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/rw36.png` | .png | 4701 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/rw37.png` | .png | 1906 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/rw38.png` | .png | 4432 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/rw39.png` | .png | 4286 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/rw40.png` | .png | 788 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/rw41.png` | .png | 5665 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/rw42.png` | .png | 23435 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/rw43.png` | .png | 8039 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/rw45.png` | .png | 657 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/rw46.png` | .png | 1451 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/rw47.png` | .png | 458 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/st_au_01.png` | .png | 67292 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/st_au_02.png` | .png | 66351 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/st_au_03.png` | .png | 72622 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/st_au_04.png` | .png | 44053 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/st_au_05.png` | .png | 46651 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/00/st_au_06.png` | .png | 49766 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/02/add.png` | .png | 30089 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/02/ar_00.png` | .png | 22520 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/02/ar_04.png` | .png | 7198 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/02/ar_06.png` | .png | 377 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/02/ar_07.png` | .png | 7687 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/02/ar_08.png` | .png | 4687 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/02/ar_09.png` | .png | 14042 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/02/ar_a3.png` | .png | 69189 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/02/kage.png` | .png | 733 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/02/kan01.png` | .png | 4121 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/02/kan04.png` | .png | 949 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/02/kan05.png` | .png | 3229 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/02/l_phon.png` | .png | 807 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/02/rope.png` | .png | 1196 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/02/ss01.png` | .png | 9686 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/02/ss02.png` | .png | 4732 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/02/ss03.png` | .png | 54782 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/02/ss04.png` | .png | 58415 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/02/ss06.png` | .png | 12845 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/02/ss07.png` | .png | 12726 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/02/ss08.png` | .png | 5095 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/02/ss09.png` | .png | 19823 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/02/ss10.png` | .png | 6282 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/02/ss11.png` | .png | 1208 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/02/ss12.png` | .png | 879 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/02/ss13.png` | .png | 3583 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/02/ss14.png` | .png | 2782 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/02/ss15.png` | .png | 4259 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/02/ss17.png` | .png | 4857 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/02/ss18.png` | .png | 954 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/02/ss19.png` | .png | 3174 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/02/ss20.png` | .png | 4958 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/02/ss21.png` | .png | 4219 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/02/ss22.png` | .png | 5598 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/02/ss23.png` | .png | 803 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/02/ss24.png` | .png | 187 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/02/ss25.png` | .png | 1003 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/02/ss26.png` | .png | 28619 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/02/ss27.png` | .png | 1222 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/02/ss28.png` | .png | 483 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/02/ss29.png` | .png | 1573 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/02/ss30.png` | .png | 2401 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/02/ss31.png` | .png | 1451 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/02/ss32.png` | .png | 458 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/02/ss33.png` | .png | 10195 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/02/ss35.png` | .png | 1906 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/02/ss36.png` | .png | 4710 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/02/ss37.png` | .png | 24578 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/02/ss38.png` | .png | 10271 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/02/st_au_01.png` | .png | 67292 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/02/st_au_02.png` | .png | 66351 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/02/st_au_03.png` | .png | 72622 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/02/st_au_04.png` | .png | 44053 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/02/st_au_06.png` | .png | 49766 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_0/ami_01.png` | .png | 569 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_0/ami_03.png` | .png | 525 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_0/ami_05.png` | .png | 762 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_0/bg.png` | .png | 55477 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_0/biru_05.png` | .png | 86 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_0/door_02.png` | .png | 10300 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_0/hasira01.png` | .png | 7446 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_0/hasira02.png` | .png | 3896 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_0/ita_01.png` | .png | 4126 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_0/ita_02.png` | .png | 14970 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_0/ita_03.png` | .png | 4172 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_0/kabe_02.png` | .png | 124102 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_0/kabe_03.png` | .png | 1399 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_0/kabe_04.png` | .png | 2101 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_0/kabe_05.png` | .png | 1929 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_0/kabe_06.png` | .png | 4222 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_0/kabe_07.png` | .png | 933 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_0/kabe_08.png` | .png | 684 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_0/kabe_09.png` | .png | 18257 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_0/kabe_10.png` | .png | 853 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_0/kabe_11.png` | .png | 10647 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_0/kabe_12.png` | .png | 25886 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_0/kabe_13.png` | .png | 28309 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_0/kaidan01.png` | .png | 566 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_0/kaidan02.png` | .png | 793 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_0/kaidan03.png` | .png | 6067 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_0/katen_01.png` | .png | 22772 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_0/katen_02.png` | .png | 5757 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_0/katen_03.png` | .png | 75472 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_0/kodo_01.png` | .png | 948 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_0/kodo_02.png` | .png | 2215 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_0/light_09.png` | .png | 30010 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_0/light_10.png` | .png | 2645 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_0/logo_01.png` | .png | 49566 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_0/nuki_02.png` | .png | 1358 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_0/nuki_03.png` | .png | 1124 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_0/nuki_04.png` | .png | 128 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_0/nuki_05.png` | .png | 826 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_0/saku_01.png` | .png | 1695 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_0/saku_02.png` | .png | 588 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_0/san.png` | .png | 20411 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_0/san_02.png` | .png | 7187 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_0/spot_01.png` | .png | 1243 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_0/tekin_01.png` | .png | 13497 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_0/tekin_02.png` | .png | 3444 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_0/tekin_03.png` | .png | 2784 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_0/tekin_04.png` | .png | 4391 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_0/tekin_05.png` | .png | 1965 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_0/tekin_06.png` | .png | 2208 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_0/tekin_07.png` | .png | 36486 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_0/tekin_08.png` | .png | 4599 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_0/tekin_09.png` | .png | 1631 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_0/tekin_10.png` | .png | 1866 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_0/tekin_11.png` | .png | 13284 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_0/yuka_01.png` | .png | 30519 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_0/yuka_07.png` | .png | 12588 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_0/yuka_08.png` | .png | 106961 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_0/yuka_09.png` | .png | 28816 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_0/yuka_10.png` | .png | 29215 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_0/yuka_11.png` | .png | 111058 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_0/yuka_12.png` | .png | 32703 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_0/yuka_15.png` | .png | 33822 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_0/yuka_17.png` | .png | 35841 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_1/ami_01.png` | .png | 569 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_1/ami_02.png` | .png | 1739 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_1/ami_03.png` | .png | 525 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_1/ami_04.png` | .png | 30744 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_1/bg.png` | .png | 1587 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_1/biru_01.png` | .png | 3263 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_1/biru_02.png` | .png | 1419 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_1/biru_04.png` | .png | 2414 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_1/biru_05.png` | .png | 86 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_1/biru_06.png` | .png | 9247 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_1/biru_07.png` | .png | 8363 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_1/haikei03.png` | .png | 75379 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_1/haikei06.png` | .png | 12456 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_1/hasira01.png` | .png | 7826 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_1/hasira02.png` | .png | 3898 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_1/ita_01.png` | .png | 4126 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_1/ita_02.png` | .png | 15010 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_1/ita_03.png` | .png | 4171 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_1/kabe_02.png` | .png | 30059 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_1/kabe_03.png` | .png | 1387 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_1/kabe_04.png` | .png | 2102 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_1/kabe_05.png` | .png | 1929 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_1/kabe_06.png` | .png | 4502 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_1/kabe_07.png` | .png | 930 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_1/kabe_08.png` | .png | 687 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_1/kabe_09.png` | .png | 18451 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_1/kabe_10.png` | .png | 894 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_1/kabe_11.png` | .png | 10638 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_1/kabe_12.png` | .png | 25855 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_1/kabe_13.png` | .png | 28415 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_1/kaidan01.png` | .png | 566 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_1/kaidan02.png` | .png | 792 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_1/kaidan03.png` | .png | 6085 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_1/katen_01.png` | .png | 23590 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_1/katen_02.png` | .png | 5791 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_1/kodo_01.png` | .png | 948 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_1/kodo_02.png` | .png | 2215 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_1/light_01.png` | .png | 32493 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_1/light_02.png` | .png | 32424 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_1/light_03.png` | .png | 22075 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_1/logo_01.png` | .png | 49783 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_1/nuki_02.png` | .png | 1237 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_1/nuki_03.png` | .png | 1134 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_1/nuki_04.png` | .png | 119 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_1/nuki_05.png` | .png | 907 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_1/saku_01.png` | .png | 862 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_1/saku_02.png` | .png | 586 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_1/spot_01.png` | .png | 1187 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_1/tekin_01.png` | .png | 2810 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_1/tekin_02.png` | .png | 3407 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_1/tekin_03.png` | .png | 2784 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_1/tekin_04.png` | .png | 4414 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_1/tekin_05.png` | .png | 1965 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_1/tekin_06.png` | .png | 2210 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_1/tekin_07.png` | .png | 35780 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_1/tekin_08.png` | .png | 4622 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_1/tekin_09.png` | .png | 1631 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_1/yuka_01.png` | .png | 30479 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_1/yuka_07.png` | .png | 12588 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_1/yuka_08.png` | .png | 107482 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_1/yuka_09.png` | .png | 28817 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_1/yuka_10.png` | .png | 29229 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_1/yuka_11.png` | .png | 111436 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_1/yuka_12.png` | .png | 32752 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_1/yuka_14.png` | .png | 9526 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_1/yuka_15.png` | .png | 33720 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/ami_01.png` | .png | 569 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/ami_03.png` | .png | 525 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/ami_05.png` | .png | 762 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/bg.png` | .png | 55477 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/biru_05.png` | .png | 86 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/dono.png` | .png | 5312 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/door_02.png` | .png | 10300 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/dramu_11.png` | .png | 7440 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/dramu_12.png` | .png | 5743 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/hasira01.png` | .png | 7446 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/hasira02.png` | .png | 3896 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/ita_01.png` | .png | 4126 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/ita_02.png` | .png | 14970 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/ita_03.png` | .png | 4172 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/kabe_02.png` | .png | 124102 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/kabe_03.png` | .png | 1399 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/kabe_04.png` | .png | 2101 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/kabe_05.png` | .png | 1929 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/kabe_06.png` | .png | 4222 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/kabe_07.png` | .png | 933 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/kabe_08.png` | .png | 684 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/kabe_09.png` | .png | 18257 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/kabe_10.png` | .png | 853 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/kabe_11.png` | .png | 10647 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/kabe_12.png` | .png | 25886 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/kabe_13.png` | .png | 28309 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/kabe_14.png` | .png | 308 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/kaidan01.png` | .png | 566 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/kaidan02.png` | .png | 793 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/kaidan03.png` | .png | 6067 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/kaku.png` | .png | 338 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/katen_01.png` | .png | 22772 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/katen_02.png` | .png | 5757 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/katen_03.png` | .png | 75472 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/kodo_01.png` | .png | 948 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/kodo_02.png` | .png | 2215 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/light_09.png` | .png | 30010 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/light_10.png` | .png | 2645 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/logo_01.png` | .png | 49566 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/logo_02.png` | .png | 24076 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/logo_03.png` | .png | 971 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/nuki_02.png` | .png | 1358 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/nuki_03.png` | .png | 1124 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/nuki_04.png` | .png | 128 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/nuki_05.png` | .png | 826 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/saku_01.png` | .png | 1695 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/saku_02.png` | .png | 588 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/san.png` | .png | 20411 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/san_02.png` | .png | 7187 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/spot_01.png` | .png | 1243 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/tekin_01.png` | .png | 13497 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/tekin_02.png` | .png | 3444 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/tekin_03.png` | .png | 2784 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/tekin_04.png` | .png | 4391 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/tekin_05.png` | .png | 1965 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/tekin_06.png` | .png | 2208 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/tekin_07.png` | .png | 36486 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/tekin_08.png` | .png | 4599 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/tekin_09.png` | .png | 1631 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/tekin_10.png` | .png | 1866 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/tekin_11.png` | .png | 13284 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/tekin_12.png` | .png | 7511 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/tekin_14.png` | .png | 8371 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/turu.png` | .png | 18195 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/yuka_01.png` | .png | 30519 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/yuka_07.png` | .png | 12588 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/yuka_08.png` | .png | 117127 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/yuka_09.png` | .png | 28816 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/yuka_10.png` | .png | 29215 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/yuka_11.png` | .png | 111058 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/yuka_12.png` | .png | 32703 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/yuka_15.png` | .png | 33822 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_2/yuka_17.png` | .png | 35841 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/ami_01.png` | .png | 569 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/ami_02.png` | .png | 1745 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/ami_03.png` | .png | 525 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/ami_05.png` | .png | 302 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/biru_01.png` | .png | 3257 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/biru_02.png` | .png | 1422 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/biru_04.png` | .png | 2387 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/biru_05.png` | .png | 86 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/biru_06.png` | .png | 9211 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/biru_07.png` | .png | 8519 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/door_02.png` | .png | 10300 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/haikei03.png` | .png | 72669 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/haikei04.png` | .png | 207745 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/haikei05.png` | .png | 16710 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/haikei06.png` | .png | 12463 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/hasira01.png` | .png | 7824 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/hasira02.png` | .png | 3896 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/ita_01.png` | .png | 4126 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/ita_02.png` | .png | 14970 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/ita_03.png` | .png | 4172 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/kabe_02.png` | .png | 30042 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/kabe_03.png` | .png | 1399 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/kabe_04.png` | .png | 2101 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/kabe_05.png` | .png | 1929 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/kabe_06.png` | .png | 4222 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/kabe_07.png` | .png | 933 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/kabe_08.png` | .png | 684 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/kabe_09.png` | .png | 18257 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/kabe_10.png` | .png | 853 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/kabe_11.png` | .png | 10647 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/kabe_12.png` | .png | 25886 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/kabe_13.png` | .png | 28309 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/kaidan01.png` | .png | 566 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/kaidan02.png` | .png | 793 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/kaidan03.png` | .png | 6067 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/katen_01.png` | .png | 23546 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/katen_02.png` | .png | 5757 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/kodo_01.png` | .png | 948 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/kodo_02.png` | .png | 2215 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/light_01.png` | .png | 27603 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/light_02.png` | .png | 28178 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/light_03.png` | .png | 23389 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/light_07.png` | .png | 2659 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/logo_01.png` | .png | 49566 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/nuki_02.png` | .png | 1358 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/nuki_03.png` | .png | 1124 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/nuki_04.png` | .png | 128 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/nuki_05.png` | .png | 826 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/saku_01.png` | .png | 875 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/saku_02.png` | .png | 588 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/spot_01.png` | .png | 1243 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/tekin_01.png` | .png | 2803 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/tekin_02.png` | .png | 3405 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/tekin_03.png` | .png | 2784 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/tekin_04.png` | .png | 4391 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/tekin_05.png` | .png | 1965 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/tekin_06.png` | .png | 2208 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/tekin_07.png` | .png | 36486 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/tekin_08.png` | .png | 4599 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/tekin_09.png` | .png | 1631 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/tekin_10.png` | .png | 1866 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/yuka_01.png` | .png | 30519 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/yuka_07.png` | .png | 12588 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/yuka_08.png` | .png | 106961 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/yuka_09.png` | .png | 28816 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/yuka_10.png` | .png | 29215 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/yuka_11.png` | .png | 111058 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/yuka_12.png` | .png | 32703 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/0_3/yuka_15.png` | .png | 33822 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_0/dramu_1.png` | .png | 8090 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_0/dramu_3.png` | .png | 7864 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_0/dramu_4.png` | .png | 5910 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_0/dramu_9.png` | .png | 7714 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_0/gesui_01.png` | .png | 35756 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_0/kabe_01.png` | .png | 12239 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_0/kabe_03.png` | .png | 25848 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_0/kabe_04.png` | .png | 102967 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_0/kage_01.png` | .png | 2139 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_0/kage_02.png` | .png | 1494 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_0/kage_03.png` | .png | 1555 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_0/kage_04.png` | .png | 139 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_0/kage_05.png` | .png | 639 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_0/kaidan01.png` | .png | 5790 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_0/kaidan02.png` | .png | 24117 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_0/mizu_01.png` | .png | 26442 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_0/obuje_01.png` | .png | 20173 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_0/obuje_02.png` | .png | 6751 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_0/obuje_03.png` | .png | 5273 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_0/paipu_01.png` | .png | 6365 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_0/paipu_02.png` | .png | 533 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_0/s01.png` | .png | 191868 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_0/s02.png` | .png | 9215 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_0/s03.png` | .png | 188287 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_0/s04.png` | .png | 2862 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_0/s05.png` | .png | 69348 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_0/s06.png` | .png | 669 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_0/s07.png` | .png | 1291 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_0/s08.png` | .png | 7621 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_0/s09.png` | .png | 14749 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_0/s11.png` | .png | 156601 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_0/s12.png` | .png | 2823 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_0/s13.png` | .png | 6295 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_0/s14.png` | .png | 1711 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_0/s15.png` | .png | 74224 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_0/s16.png` | .png | 4710 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_0/s17.png` | .png | 5853 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_0/s18.png` | .png | 4214 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_0/s19.png` | .png | 4324 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_0/s20.png` | .png | 1499 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_0/s21.png` | .png | 5558 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_0/s22.png` | .png | 134 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_0/s23.png` | .png | 2927 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_0/s24.png` | .png | 48300 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_0/s25.png` | .png | 259 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_0/s26.png` | .png | 24069 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_0/s27.png` | .png | 742 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_0/s28.png` | .png | 56767 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_0/s29.png` | .png | 946 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_0/s30.png` | .png | 7412 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_0/s31.png` | .png | 903 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_0/s32.png` | .png | 134 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_0/s34.png` | .png | 2857 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_0/s35.png` | .png | 1342 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_0/s36.png` | .png | 7897 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_0/s37.png` | .png | 35700 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_0/s40.png` | .png | 526 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_0/s41.png` | .png | 5248 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_0/s_00.png` | .png | 275763 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_0/san.png` | .png | 20411 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_0/warp.png` | .png | 61916 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_0/yuka_01.png` | .png | 55465 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_0/yuka_02.png` | .png | 21644 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/OBJ_24.png` | .png | 5380 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/OBJ_25.png` | .png | 2980 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/OBJ_29_1.png` | .png | 7210 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/OBJ_29_2.png` | .png | 5821 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/ami_01.png` | .png | 569 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/ami_03.png` | .png | 525 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/dramu_1.png` | .png | 8090 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/dramu_9.png` | .png | 7714 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/gesui_02.png` | .png | 123177 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/gesui_03.png` | .png | 3807 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/haikei01.png` | .png | 17629 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/kabe_01.png` | .png | 1380 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/kabe_03.png` | .png | 25848 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/kabe_04.png` | .png | 7459 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/kage_01.png` | .png | 2139 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/kage_02.png` | .png | 1494 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/kage_03.png` | .png | 1153 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/kage_04.png` | .png | 139 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/kage_05.png` | .png | 639 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/kaidan01.png` | .png | 7039 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/kaidan02.png` | .png | 24117 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/kami_01.png` | .png | 1089 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/kami_02.png` | .png | 1255 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/kemuri01.png` | .png | 8432 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/light_01.png` | .png | 1703 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/light_02.png` | .png | 2154 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/mizu_01.png` | .png | 17056 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/nuki_01.png` | .png | 1494 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/nuki_02.png` | .png | 79 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/obuje_01.png` | .png | 20173 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/obuje_02.png` | .png | 6751 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/obuje_03.png` | .png | 5273 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/paipu_01.png` | .png | 6365 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/paipu_02.png` | .png | 533 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/s01.png` | .png | 191868 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/s03.png` | .png | 182117 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/s04.png` | .png | 2862 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/s05.png` | .png | 4998 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/s06.png` | .png | 686 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/s07.png` | .png | 1291 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/s08.png` | .png | 7699 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/s09.png` | .png | 14749 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/s11_02.png` | .png | 29386 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/s12.png` | .png | 3320 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/s13.png` | .png | 6295 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/s14.png` | .png | 1711 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/s15.png` | .png | 18173 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/s16.png` | .png | 5160 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/s17.png` | .png | 5853 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/s18.png` | .png | 4214 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/s19.png` | .png | 4324 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/s20.png` | .png | 1499 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/s21.png` | .png | 5558 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/s22.png` | .png | 134 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/s23.png` | .png | 2872 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/s24.png` | .png | 27853 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/s25.png` | .png | 259 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/s26.png` | .png | 16017 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/s27.png` | .png | 753 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/s28.png` | .png | 56767 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/s29.png` | .png | 946 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/s30.png` | .png | 2564 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/s31.png` | .png | 903 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/s32.png` | .png | 134 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/s34.png` | .png | 2857 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/s35.png` | .png | 1342 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/s36.png` | .png | 9550 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/s37.png` | .png | 41222 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/s40.png` | .png | 526 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/s41.png` | .png | 5248 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/s_00.png` | .png | 278640 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/san.png` | .png | 3703 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/trakku.png` | .png | 5060 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/warp.png` | .png | 61916 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/yuka_01.png` | .png | 55465 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_1/yuka_02.png` | .png | 21644 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/OBJ_24.png` | .png | 5380 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/OBJ_25.png` | .png | 2980 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/OBJ_29_1.png` | .png | 7210 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/OBJ_29_2.png` | .png | 5821 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/ami_01.png` | .png | 569 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/ami_03.png` | .png | 525 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/dramu_1.png` | .png | 8090 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/dramu_9.png` | .png | 7714 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/gesui_02.png` | .png | 123177 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/gesui_03.png` | .png | 3807 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/haikei01.png` | .png | 17629 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/kabe_01.png` | .png | 1380 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/kabe_03.png` | .png | 25848 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/kabe_04.png` | .png | 7459 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/kage_01.png` | .png | 2139 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/kage_02.png` | .png | 1494 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/kage_03.png` | .png | 1153 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/kage_04.png` | .png | 139 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/kage_05.png` | .png | 639 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/kaidan01.png` | .png | 7039 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/kaidan02.png` | .png | 24117 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/kami_01.png` | .png | 1089 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/kami_02.png` | .png | 1255 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/kemuri01.png` | .png | 8432 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/light_01.png` | .png | 1703 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/light_02.png` | .png | 2154 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/mizu_01.png` | .png | 17056 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/nuki_01.png` | .png | 1494 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/nuki_02.png` | .png | 79 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/obuje_01.png` | .png | 20173 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/obuje_02.png` | .png | 6751 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/obuje_03.png` | .png | 5273 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/paipu_01.png` | .png | 6365 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/paipu_02.png` | .png | 533 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/s01.png` | .png | 191868 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/s03.png` | .png | 182117 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/s04.png` | .png | 2862 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/s05.png` | .png | 4998 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/s06.png` | .png | 686 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/s07.png` | .png | 1291 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/s08.png` | .png | 7699 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/s09.png` | .png | 14749 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/s11_02.png` | .png | 29386 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/s12.png` | .png | 3320 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/s13.png` | .png | 6295 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/s14.png` | .png | 1711 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/s15.png` | .png | 18173 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/s16.png` | .png | 5160 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/s17.png` | .png | 5853 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/s18.png` | .png | 4214 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/s19.png` | .png | 4324 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/s20.png` | .png | 1499 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/s21.png` | .png | 5558 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/s22.png` | .png | 134 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/s23.png` | .png | 2872 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/s24.png` | .png | 27853 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/s25.png` | .png | 259 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/s26.png` | .png | 16017 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/s27.png` | .png | 753 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/s28.png` | .png | 56767 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/s29.png` | .png | 946 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/s30.png` | .png | 2564 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/s31.png` | .png | 903 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/s32.png` | .png | 134 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/s34.png` | .png | 2857 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/s35.png` | .png | 1342 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/s36.png` | .png | 9550 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/s37.png` | .png | 41222 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/s40.png` | .png | 526 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/s41.png` | .png | 5248 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/s_00.png` | .png | 278640 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/san.png` | .png | 3703 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/trakku.png` | .png | 5060 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/warp.png` | .png | 61916 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/yuka_01.png` | .png | 55465 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_2/yuka_02.png` | .png | 21644 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/OBJ_24.png` | .png | 5380 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/OBJ_25.png` | .png | 2980 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/OBJ_29_1.png` | .png | 7210 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/OBJ_29_2.png` | .png | 5821 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/ami_01.png` | .png | 569 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/ami_03.png` | .png | 525 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/dramu_1.png` | .png | 8090 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/dramu_9.png` | .png | 7714 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/gesui_02.png` | .png | 123177 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/gesui_03.png` | .png | 3807 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/haikei01.png` | .png | 17629 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/kabe_01.png` | .png | 1380 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/kabe_03.png` | .png | 25848 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/kabe_04.png` | .png | 7459 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/kage_01.png` | .png | 2139 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/kage_02.png` | .png | 1494 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/kage_03.png` | .png | 1153 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/kage_04.png` | .png | 139 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/kage_05.png` | .png | 639 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/kaidan01.png` | .png | 7039 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/kaidan02.png` | .png | 24117 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/kami_01.png` | .png | 1089 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/kami_02.png` | .png | 1255 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/kemuri01.png` | .png | 8432 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/light_01.png` | .png | 1703 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/light_02.png` | .png | 2154 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/mizu_01.png` | .png | 17056 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/nuki_01.png` | .png | 1494 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/nuki_02.png` | .png | 79 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/obuje_01.png` | .png | 20173 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/obuje_02.png` | .png | 6751 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/obuje_03.png` | .png | 5273 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/paipu_01.png` | .png | 6365 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/paipu_02.png` | .png | 533 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/s01.png` | .png | 191868 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/s03.png` | .png | 182117 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/s04.png` | .png | 2862 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/s05.png` | .png | 4998 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/s06.png` | .png | 686 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/s07.png` | .png | 1291 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/s08.png` | .png | 7699 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/s09.png` | .png | 14749 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/s11_02.png` | .png | 29386 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/s12.png` | .png | 3320 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/s13.png` | .png | 6295 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/s14.png` | .png | 1711 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/s15.png` | .png | 18173 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/s16.png` | .png | 5160 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/s17.png` | .png | 5853 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/s18.png` | .png | 4214 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/s19.png` | .png | 4324 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/s20.png` | .png | 1499 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/s21.png` | .png | 5558 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/s22.png` | .png | 134 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/s23.png` | .png | 2872 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/s24.png` | .png | 27853 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/s25.png` | .png | 259 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/s26.png` | .png | 16017 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/s27.png` | .png | 753 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/s28.png` | .png | 56767 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/s29.png` | .png | 946 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/s30.png` | .png | 2564 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/s31.png` | .png | 903 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/s32.png` | .png | 134 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/s34.png` | .png | 2857 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/s35.png` | .png | 1342 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/s36.png` | .png | 9550 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/s37.png` | .png | 41222 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/s40.png` | .png | 526 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/s41.png` | .png | 5248 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/s_00.png` | .png | 278640 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/san.png` | .png | 3703 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/trakku.png` | .png | 5060 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/warp.png` | .png | 61916 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/yuka_01.png` | .png | 55465 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_3/yuka_02.png` | .png | 21644 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/OBJ_24.png` | .png | 5380 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/OBJ_25.png` | .png | 2980 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/OBJ_29_1.png` | .png | 7210 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/OBJ_29_2.png` | .png | 5821 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/ami_01.png` | .png | 569 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/ami_03.png` | .png | 525 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/dramu_1.png` | .png | 8090 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/dramu_9.png` | .png | 7714 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/gesui_02.png` | .png | 123177 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/gesui_03.png` | .png | 3807 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/haikei01.png` | .png | 17629 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/kabe_01.png` | .png | 1380 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/kabe_03.png` | .png | 25848 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/kabe_04.png` | .png | 7459 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/kage_01.png` | .png | 2139 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/kage_02.png` | .png | 1494 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/kage_03.png` | .png | 1153 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/kage_04.png` | .png | 139 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/kage_05.png` | .png | 639 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/kaidan01.png` | .png | 7039 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/kaidan02.png` | .png | 24117 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/kami_01.png` | .png | 1089 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/kami_02.png` | .png | 1255 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/kemuri01.png` | .png | 8432 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/light_01.png` | .png | 1703 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/light_02.png` | .png | 2154 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/mizu_01.png` | .png | 17056 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/nuki_01.png` | .png | 1494 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/nuki_02.png` | .png | 79 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/obuje_01.png` | .png | 20173 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/obuje_02.png` | .png | 6751 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/obuje_03.png` | .png | 5273 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/paipu_01.png` | .png | 6365 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/paipu_02.png` | .png | 533 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/s01.png` | .png | 191868 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/s03.png` | .png | 182117 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/s04.png` | .png | 2862 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/s05.png` | .png | 4998 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/s06.png` | .png | 686 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/s07.png` | .png | 1291 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/s08.png` | .png | 7699 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/s09.png` | .png | 14749 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/s11_02.png` | .png | 29386 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/s12.png` | .png | 3320 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/s13.png` | .png | 6295 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/s14.png` | .png | 1711 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/s15.png` | .png | 18173 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/s16.png` | .png | 5160 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/s17.png` | .png | 5853 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/s18.png` | .png | 4214 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/s19.png` | .png | 4324 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/s20.png` | .png | 1499 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/s21.png` | .png | 5558 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/s22.png` | .png | 134 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/s23.png` | .png | 2872 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/s24.png` | .png | 27853 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/s25.png` | .png | 259 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/s26.png` | .png | 16017 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/s27.png` | .png | 753 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/s28.png` | .png | 56767 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/s29.png` | .png | 946 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/s30.png` | .png | 2564 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/s31.png` | .png | 903 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/s32.png` | .png | 134 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/s34.png` | .png | 2857 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/s35.png` | .png | 1342 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/s36.png` | .png | 9550 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/s37.png` | .png | 41222 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/s40.png` | .png | 526 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/s41.png` | .png | 5248 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/s_00.png` | .png | 278640 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/san.png` | .png | 3703 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/trakku.png` | .png | 5060 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/warp.png` | .png | 61916 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/yuka_01.png` | .png | 55465 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/1_4/yuka_02.png` | .png | 21644 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/densyoku.png` | .png | 3050 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/door_01.png` | .png | 4052 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/exit_01.png` | .png | 751 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/fence_03.png` | .png | 1400 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/fuku_01.png` | .png | 2514 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/fuku_02.png` | .png | 1492 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/fuku_03.png` | .png | 2567 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/fuku_04.png` | .png | 2561 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/fuku_05.png` | .png | 1462 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/fuku_06.png` | .png | 1687 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/fuku_07.png` | .png | 1733 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/hasira01.png` | .png | 9902 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/hasira03.png` | .png | 5280 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/hasira04.png` | .png | 6385 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/hasira06.png` | .png | 2467 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/hasira07.png` | .png | 4663 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/kabe_03.png` | .png | 5171 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/kabe_04.png` | .png | 6900 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/kabe_05.png` | .png | 16264 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/kabe_06.png` | .png | 3639 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/kabe_07.png` | .png | 1946 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/kabe_09.png` | .png | 776 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/kabe_10.png` | .png | 3244 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/kabe_14.png` | .png | 5483 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/kabe_16.png` | .png | 2860 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/kabe_17.png` | .png | 716 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/kabe_18.png` | .png | 10471 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/kabe_20.png` | .png | 14916 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/kabe_21.png` | .png | 3992 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/kabe_22.png` | .png | 1684 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/kabe_23.png` | .png | 7373 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/kabe_24.png` | .png | 1140 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/kabe_28.png` | .png | 6290 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/kabe_29.png` | .png | 3884 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/kabe_30.png` | .png | 2114 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/kabe_34.png` | .png | 8309 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/kabe_36.png` | .png | 17761 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/kabe_37.png` | .png | 6483 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/kabe_40.png` | .png | 6561 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/kabe_42.png` | .png | 5247 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/kabe_45.png` | .png | 6913 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/kage_02.png` | .png | 1416 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/kaidan02.png` | .png | 1071 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/kaidan03.png` | .png | 1213 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/katen_01.png` | .png | 7777 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/l_01.png` | .png | 217 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/l_02.png` | .png | 997 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/light01g.png` | .png | 79 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/light_01.png` | .png | 756 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/light_04.png` | .png | 167 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/light_05.png` | .png | 180 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/light_t.png` | .png | 30343 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/light_u.png` | .png | 30852 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/mado_02.png` | .png | 1249 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/mado_03.png` | .png | 19640 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/moji_01.png` | .png | 1326 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/moji_02.png` | .png | 1068 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/moji_03.png` | .png | 1597 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/moji_04.png` | .png | 236 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/moji_05.png` | .png | 546 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/moji_06.png` | .png | 1091 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/nuki_01.png` | .png | 261 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/nuki_02.png` | .png | 78 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/nuki_03.png` | .png | 1061 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/nuki_04.png` | .png | 862 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/nuki_05.png` | .png | 1058 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/nuki_07.png` | .png | 4072 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/nuki_08.png` | .png | 2064 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/nuki_09.png` | .png | 2817 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/nuki_10.png` | .png | 3737 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/nuki_12.png` | .png | 1051 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/nuki_15.png` | .png | 2362 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/nuki_16.png` | .png | 202 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/obuje_04.png` | .png | 10229 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/obuje_05.png` | .png | 838 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/obuje_07.png` | .png | 1113 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/obuje_11.png` | .png | 1717 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/parking1.png` | .png | 1465 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/posta_01.png` | .png | 12506 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/posta_02.png` | .png | 3314 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/posta_03.png` | .png | 9308 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/s09.png` | .png | 14749 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/saku_01.png` | .png | 577 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/shop_01.png` | .png | 23042 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/sky.png` | .png | 20408 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/spot_01.png` | .png | 507 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/tenjo_01.png` | .png | 1133 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/tenjo_02.png` | .png | 1028 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/tenjo_05.png` | .png | 897 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/tenjo_06.png` | .png | 1268 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/test_01.png` | .png | 78 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/tetsu_01.png` | .png | 4697 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/warp.png` | .png | 61916 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/yane_01.png` | .png | 2046 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/yuka_03.png` | .png | 6925 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/yuka_04.png` | .png | 6294 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/yuka_05.png` | .png | 5104 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/yuka_06.png` | .png | 5067 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/yuka_07.png` | .png | 475 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/yuka_08.png` | .png | 14575 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/yuka_09.png` | .png | 5882 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/yuka_10.png` | .png | 8775 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/yuka_11.png` | .png | 8730 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/yuka_12.png` | .png | 7352 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/yuka_13.png` | .png | 6566 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/yuka_16.png` | .png | 8158 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/yuka_18.png` | .png | 30800 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/yuka_19.png` | .png | 21059 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_0/yuka_20.png` | .png | 7003 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/densyoku.png` | .png | 3050 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/door_01.png` | .png | 4052 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/exit_01.png` | .png | 751 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/fence_03.png` | .png | 1400 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/fuku_01.png` | .png | 2514 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/fuku_02.png` | .png | 1492 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/fuku_03.png` | .png | 2567 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/fuku_04.png` | .png | 2561 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/fuku_05.png` | .png | 1462 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/fuku_06.png` | .png | 1687 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/fuku_07.png` | .png | 1733 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/hasira01.png` | .png | 9902 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/hasira03.png` | .png | 5280 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/hasira04.png` | .png | 6385 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/hasira06.png` | .png | 2467 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/hasira07.png` | .png | 4663 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/kabe_03.png` | .png | 5171 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/kabe_04.png` | .png | 6900 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/kabe_05.png` | .png | 16264 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/kabe_06.png` | .png | 3639 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/kabe_07.png` | .png | 1946 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/kabe_09.png` | .png | 776 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/kabe_10.png` | .png | 3244 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/kabe_14.png` | .png | 5483 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/kabe_16.png` | .png | 2860 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/kabe_17.png` | .png | 716 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/kabe_18.png` | .png | 10471 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/kabe_20.png` | .png | 14916 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/kabe_21.png` | .png | 3992 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/kabe_22.png` | .png | 1684 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/kabe_23.png` | .png | 7373 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/kabe_24.png` | .png | 1140 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/kabe_28.png` | .png | 6290 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/kabe_29.png` | .png | 3884 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/kabe_30.png` | .png | 2114 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/kabe_34.png` | .png | 8309 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/kabe_36.png` | .png | 17761 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/kabe_37.png` | .png | 6483 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/kabe_40.png` | .png | 6561 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/kabe_42.png` | .png | 5247 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/kabe_45.png` | .png | 6913 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/kage_02.png` | .png | 1416 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/kaidan02.png` | .png | 1071 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/kaidan03.png` | .png | 1213 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/katen_01.png` | .png | 7777 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/l_01.png` | .png | 217 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/l_02.png` | .png | 997 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/light01g.png` | .png | 79 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/light_01.png` | .png | 756 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/light_04.png` | .png | 167 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/light_05.png` | .png | 180 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/light_t.png` | .png | 30343 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/light_u.png` | .png | 30852 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/mado_02.png` | .png | 1249 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/mado_03.png` | .png | 19640 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/moji_01.png` | .png | 1326 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/moji_02.png` | .png | 1068 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/moji_03.png` | .png | 1597 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/moji_04.png` | .png | 236 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/moji_05.png` | .png | 546 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/moji_06.png` | .png | 1091 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/nuki_01.png` | .png | 261 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/nuki_02.png` | .png | 78 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/nuki_03.png` | .png | 1061 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/nuki_04.png` | .png | 862 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/nuki_05.png` | .png | 1058 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/nuki_07.png` | .png | 4072 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/nuki_08.png` | .png | 2064 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/nuki_09.png` | .png | 2817 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/nuki_10.png` | .png | 3737 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/nuki_12.png` | .png | 1051 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/nuki_15.png` | .png | 2362 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/nuki_16.png` | .png | 202 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/obuje_04.png` | .png | 10229 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/obuje_05.png` | .png | 838 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/obuje_07.png` | .png | 1113 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/obuje_11.png` | .png | 1717 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/parking1.png` | .png | 1465 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/posta_01.png` | .png | 12506 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/posta_02.png` | .png | 3314 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/posta_03.png` | .png | 9308 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/s09.png` | .png | 14749 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/s41.png` | .png | 5248 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/saku_01.png` | .png | 577 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/shop_01.png` | .png | 23042 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/sky.png` | .png | 20408 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/spot_01.png` | .png | 507 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/tenjo_01.png` | .png | 1133 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/tenjo_02.png` | .png | 1028 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/tenjo_05.png` | .png | 897 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/tenjo_06.png` | .png | 1268 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/test_01.png` | .png | 78 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/tetsu_01.png` | .png | 4697 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/warp.png` | .png | 61916 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/yane_01.png` | .png | 2046 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/yuka_03.png` | .png | 6925 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/yuka_04.png` | .png | 6294 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/yuka_05.png` | .png | 5104 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/yuka_06.png` | .png | 5067 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/yuka_07.png` | .png | 475 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/yuka_08.png` | .png | 14575 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/yuka_09.png` | .png | 5882 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/yuka_10.png` | .png | 8775 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/yuka_11.png` | .png | 8730 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/yuka_12.png` | .png | 7352 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/yuka_13.png` | .png | 6566 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/yuka_16.png` | .png | 8158 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/yuka_18.png` | .png | 30800 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/yuka_19.png` | .png | 21059 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_1/yuka_20.png` | .png | 7003 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/car_00.png` | .png | 51047 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/car_000.png` | .png | 54616 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/densyoku.png` | .png | 3050 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/door_01.png` | .png | 4052 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/exit_01.png` | .png | 751 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/fence_03.png` | .png | 1400 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/fuku_01.png` | .png | 2514 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/fuku_02.png` | .png | 1492 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/fuku_03.png` | .png | 2567 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/fuku_04.png` | .png | 2561 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/fuku_05.png` | .png | 1462 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/fuku_06.png` | .png | 1687 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/fuku_07.png` | .png | 1733 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/hasira01.png` | .png | 9902 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/hasira03.png` | .png | 5280 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/hasira04.png` | .png | 6385 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/hasira06.png` | .png | 2467 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/hasira07.png` | .png | 4663 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/kabe_03.png` | .png | 5171 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/kabe_04.png` | .png | 6900 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/kabe_05.png` | .png | 16264 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/kabe_09.png` | .png | 776 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/kabe_10.png` | .png | 3244 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/kabe_14.png` | .png | 5483 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/kabe_16.png` | .png | 2860 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/kabe_17.png` | .png | 716 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/kabe_18.png` | .png | 10471 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/kabe_21.png` | .png | 3992 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/kabe_22.png` | .png | 1684 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/kabe_23.png` | .png | 7373 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/kabe_24.png` | .png | 1140 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/kabe_28.png` | .png | 6290 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/kabe_29.png` | .png | 3884 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/kabe_30.png` | .png | 2114 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/kabe_34.png` | .png | 8309 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/kabe_36.png` | .png | 17761 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/kabe_37.png` | .png | 6483 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/kabe_42.png` | .png | 5247 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/kabe_45.png` | .png | 6913 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/kage_02.png` | .png | 1416 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/l_01.png` | .png | 217 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/l_02.png` | .png | 997 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/light01g.png` | .png | 79 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/light_04.png` | .png | 167 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/light_05.png` | .png | 180 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/light_t.png` | .png | 30343 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/light_u.png` | .png | 30852 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/logo.png` | .png | 51560 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/mado_02.png` | .png | 1249 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/mado_03.png` | .png | 19640 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/moji_01.png` | .png | 1326 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/moji_02.png` | .png | 1068 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/moji_03.png` | .png | 1597 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/moji_04.png` | .png | 236 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/moji_05.png` | .png | 546 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/moji_06.png` | .png | 1091 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/nuki_01.png` | .png | 261 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/nuki_02.png` | .png | 78 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/nuki_03.png` | .png | 1061 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/nuki_04.png` | .png | 862 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/nuki_05.png` | .png | 1058 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/nuki_07.png` | .png | 4072 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/nuki_08.png` | .png | 2064 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/nuki_09.png` | .png | 2817 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/nuki_10.png` | .png | 3737 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/nuki_12.png` | .png | 1051 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/nuki_15.png` | .png | 2362 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/nuki_16.png` | .png | 202 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/obuje_04.png` | .png | 10229 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/obuje_05.png` | .png | 838 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/obuje_07.png` | .png | 1113 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/obuje_11.png` | .png | 1717 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/posta_01.png` | .png | 12506 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/posta_02.png` | .png | 3314 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/posta_03.png` | .png | 9308 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/s09.png` | .png | 14749 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/shop_01.png` | .png | 23042 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/sky.png` | .png | 20408 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/spot_01.png` | .png | 507 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/tenjo_01.png` | .png | 1133 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/tenjo_02.png` | .png | 1028 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/tenjo_05.png` | .png | 897 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/test_01.png` | .png | 78 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/tetsu_01.png` | .png | 4697 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/warp.png` | .png | 61916 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/yane_01.png` | .png | 2046 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/yuka_03.png` | .png | 6925 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/yuka_05.png` | .png | 5104 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/yuka_06.png` | .png | 5067 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/yuka_08.png` | .png | 14575 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/yuka_09.png` | .png | 5882 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/yuka_10.png` | .png | 8775 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/yuka_11.png` | .png | 8730 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/yuka_13.png` | .png | 6566 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/yuka_16.png` | .png | 8158 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/yuka_18.png` | .png | 30800 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/yuka_19.png` | .png | 21059 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/2_2/yuka_20.png` | .png | 7003 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/5_0/setumai.png` | .png | 14379 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/5_0/test_wall.png` | .png | 228 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/5_1/gake.png` | .png | 120556 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/5_1/h_1.png` | .png | 71167 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/5_1/h_2.png` | .png | 35481 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/5_1/t3.png` | .png | 18933 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/5_1/t_1.png` | .png | 76072 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/5_1/t_2.png` | .png | 37724 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/5_1/ten_1.png` | .png | 15772 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/5_1/zigoku.png` | .png | 127848 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/README.md` | .md | 1675 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/TEX-MANIFEST.txt` | .txt | 1699 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/f01/f01.png` | .png | 84260 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/f01/f01s.png` | .png | 22207 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/f01/f02.png` | .png | 1227 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/f01/tei__grow.png` | .png | 247 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/kaijo_x8/RR_53.png` | .png | 8343 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/kaijo_x8/add.png` | .png | 21410 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/kaijo_x8/ar_00.png` | .png | 276495 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/kaijo_x8/ar_02.png` | .png | 54032 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/kaijo_x8/ar_04.png` | .png | 10112 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/kaijo_x8/ar_05.png` | .png | 15918 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/kaijo_x8/ar_06.png` | .png | 215 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/kaijo_x8/ar_07.png` | .png | 8946 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/kaijo_x8/ar_08.png` | .png | 4816 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/kaijo_x8/ar_15_2.png` | .png | 16556 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/kaijo_x8/ar_a3.png` | .png | 68913 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/kaijo_x8/ar_b3.png` | .png | 68913 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/kaijo_x8/ar_c3.png` | .png | 4495 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/kaijo_x8/ar_d3.png` | .png | 4495 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/kaijo_x8/au_all.png` | .png | 21471 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/kaijo_x8/au_all2.png` | .png | 5633 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/kaijo_x8/eixtw.png` | .png | 137 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/kaijo_x8/fen_01.png` | .png | 25087 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/kaijo_x8/fen_02.png` | .png | 564 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/kaijo_x8/fen_03.png` | .png | 1219 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/kaijo_x8/fen_03s.png` | .png | 147 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/kaijo_x8/fen_03s2.png` | .png | 122 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/kaijo_x8/l_lan01.png` | .png | 2667 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/kaijo_x8/l_lan02.png` | .png | 1525 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/kaijo_x8/l_phon.png` | .png | 1941 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/kaijo_x8/li01_01.png` | .png | 2395 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/kaijo_x8/li01_02.png` | .png | 1167 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/kaijo_x8/rope.png` | .png | 1607 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/kaijo_x8/rr_05.png` | .png | 21290 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/kaijo_x8/rr_08.png` | .png | 4250 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/kaijo_x8/rr_43.png` | .png | 5879 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/kaijo_x8/sc_01.png` | .png | 4502 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/kaijo_x8/st_au_01.png` | .png | 35825 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/kaijo_x8/st_au_02.png` | .png | 33272 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/kaijo_x8/st_au_03.png` | .png | 38128 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/kaijo_x8/st_au_04.png` | .png | 29773 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/kaijo_x8/wm_dm_01.png` | .png | 6526 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/kaijo_x8/wm_dm_02.png` | .png | 7070 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/kaijo_x8/wm_gt_04.png` | .png | 8609 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/kaijo_x8/wm_gt_08.png` | .png | 37721 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/kaijo_x8/wm_gt_09.png` | .png | 3001 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/kaijo_x8/wm_gt_10.png` | .png | 22305 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/kaijo_x8/wm_gt_13.png` | .png | 167 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/kaijo_x8/x8_01.png` | .png | 9108 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/kaijo_x8/x8_01_2.png` | .png | 6478 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/kaijo_x8/x8_02.png` | .png | 57405 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/kaijo_x8/x8_03.png` | .png | 2257 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/kaijo_x8/x8_04.png` | .png | 3844 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/kaijo_x8/x8_05.png` | .png | 32579 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/kaijo_x8/x8_06.png` | .png | 3069 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/kaijo_x8/x8_07.png` | .png | 63611 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/kaijo_x8/x8_08.png` | .png | 708 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/kaijo_x8/x8_09.png` | .png | 167 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/kaijo_x8/x8_11.png` | .png | 5424 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/kaijo_x8/x8_12.png` | .png | 23995 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/ring/ar_00.png` | .png | 245767 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/ring/ar_02.png` | .png | 54032 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/ring/ar_05.png` | .png | 15918 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/ring/ar_06.png` | .png | 215 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/ring/ar_07.png` | .png | 7235 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/ring/ar_08.png` | .png | 4552 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/ring/ar_a3.png` | .png | 54093 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/ring/ar_b3.png` | .png | 51236 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/ring/ar_c3.png` | .png | 1672 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/ring/ar_d3.png` | .png | 1569 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/ring/l_lan02.png` | .png | 587 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/ring/l_phon.png` | .png | 685 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/ring/rope.png` | .png | 1260 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/textures/ring/sc_01.png` | .png | 1495 | Arena texture PNG (decoded from GameCube TPL via decode_tpl.py) | WIRED-DATA (this PR: stages.json texture_dir refs; blocked on arena faces) |
| `teardown/wmxix/tools/yobj_arena_faces.py` | .py | 2694 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wmxix/wrestlers/000/000_0.obj` | .obj | 19859 | Wrestler model OBJ (assembled YOBJ geometry, slot 000) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/001/001_0.obj` | .obj | 14195 | Wrestler model OBJ (assembled YOBJ geometry, slot 001) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/001/001_1.obj` | .obj | 13268 | Wrestler model OBJ (assembled YOBJ geometry, slot 001) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/002/002_0.obj` | .obj | 19706 | Wrestler model OBJ (assembled YOBJ geometry, slot 002) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/002/002_1.obj` | .obj | 14445 | Wrestler model OBJ (assembled YOBJ geometry, slot 002) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/003/003_0.obj` | .obj | 6487 | Wrestler model OBJ (assembled YOBJ geometry, slot 003) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/003/003_1.obj` | .obj | 9871 | Wrestler model OBJ (assembled YOBJ geometry, slot 003) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/004/004_0.obj` | .obj | 14261 | Wrestler model OBJ (assembled YOBJ geometry, slot 004) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/004/004_1.obj` | .obj | 14030 | Wrestler model OBJ (assembled YOBJ geometry, slot 004) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/005/005_0.obj` | .obj | 15076 | Wrestler model OBJ (assembled YOBJ geometry, slot 005) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/005/005_1.obj` | .obj | 15076 | Wrestler model OBJ (assembled YOBJ geometry, slot 005) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/006/006_0.obj` | .obj | 12003 | Wrestler model OBJ (assembled YOBJ geometry, slot 006) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/006/006_1.obj` | .obj | 12003 | Wrestler model OBJ (assembled YOBJ geometry, slot 006) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/007/007_0.obj` | .obj | 14524 | Wrestler model OBJ (assembled YOBJ geometry, slot 007) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/007/007_1.obj` | .obj | 14276 | Wrestler model OBJ (assembled YOBJ geometry, slot 007) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/008/008_0.obj` | .obj | 11663 | Wrestler model OBJ (assembled YOBJ geometry, slot 008) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/008/008_1.obj` | .obj | 19587 | Wrestler model OBJ (assembled YOBJ geometry, slot 008) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/009/009_0.obj` | .obj | 14471 | Wrestler model OBJ (assembled YOBJ geometry, slot 009) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/009/009_1.obj` | .obj | 14471 | Wrestler model OBJ (assembled YOBJ geometry, slot 009) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/009/009_2.obj` | .obj | 9391 | Wrestler model OBJ (assembled YOBJ geometry, slot 009) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/009/009_3.obj` | .obj | 9391 | Wrestler model OBJ (assembled YOBJ geometry, slot 009) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/010/010_0.obj` | .obj | 16280 | Wrestler model OBJ (assembled YOBJ geometry, slot 010) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/010/010_1.obj` | .obj | 16719 | Wrestler model OBJ (assembled YOBJ geometry, slot 010) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/011/011_0.obj` | .obj | 12074 | Wrestler model OBJ (assembled YOBJ geometry, slot 011) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/012/012_0.obj` | .obj | 13762 | Wrestler model OBJ (assembled YOBJ geometry, slot 012) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/012/012_1.obj` | .obj | 16604 | Wrestler model OBJ (assembled YOBJ geometry, slot 012) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/013/013_0.obj` | .obj | 13532 | Wrestler model OBJ (assembled YOBJ geometry, slot 013) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/013/013_1.obj` | .obj | 13532 | Wrestler model OBJ (assembled YOBJ geometry, slot 013) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/014/014_0.obj` | .obj | 15967 | Wrestler model OBJ (assembled YOBJ geometry, slot 014) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/014/014_1.obj` | .obj | 10647 | Wrestler model OBJ (assembled YOBJ geometry, slot 014) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/015/015_0.obj` | .obj | 14764 | Wrestler model OBJ (assembled YOBJ geometry, slot 015) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/015/015_1.obj` | .obj | 13926 | Wrestler model OBJ (assembled YOBJ geometry, slot 015) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/016/016_0.obj` | .obj | 13462 | Wrestler model OBJ (assembled YOBJ geometry, slot 016) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/016/016_1.obj` | .obj | 13865 | Wrestler model OBJ (assembled YOBJ geometry, slot 016) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/017/017_0.obj` | .obj | 5226 | Wrestler model OBJ (assembled YOBJ geometry, slot 017) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/017/017_1.obj` | .obj | 13824 | Wrestler model OBJ (assembled YOBJ geometry, slot 017) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/017/017_2.obj` | .obj | 8693 | Wrestler model OBJ (assembled YOBJ geometry, slot 017) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/018/018_0.obj` | .obj | 14693 | Wrestler model OBJ (assembled YOBJ geometry, slot 018) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/018/018_1.obj` | .obj | 14693 | Wrestler model OBJ (assembled YOBJ geometry, slot 018) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/019/019_0.obj` | .obj | 15042 | Wrestler model OBJ (assembled YOBJ geometry, slot 019) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/019/019_1.obj` | .obj | 10628 | Wrestler model OBJ (assembled YOBJ geometry, slot 019) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/020/020_0.obj` | .obj | 14738 | Wrestler model OBJ (assembled YOBJ geometry, slot 020) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/020/020_1.obj` | .obj | 15752 | Wrestler model OBJ (assembled YOBJ geometry, slot 020) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/022/022_0.obj` | .obj | 16058 | Wrestler model OBJ (assembled YOBJ geometry, slot 022) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/022/022_1.obj` | .obj | 17179 | Wrestler model OBJ (assembled YOBJ geometry, slot 022) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/023/023_0.obj` | .obj | 15065 | Wrestler model OBJ (assembled YOBJ geometry, slot 023) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/023/023_1.obj` | .obj | 14847 | Wrestler model OBJ (assembled YOBJ geometry, slot 023) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/024/024_0.obj` | .obj | 20573 | Wrestler model OBJ (assembled YOBJ geometry, slot 024) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/024/024_1.obj` | .obj | 6302 | Wrestler model OBJ (assembled YOBJ geometry, slot 024) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/025/025_0.obj` | .obj | 14422 | Wrestler model OBJ (assembled YOBJ geometry, slot 025) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/025/025_1.obj` | .obj | 15270 | Wrestler model OBJ (assembled YOBJ geometry, slot 025) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/026/026_0.obj` | .obj | 11636 | Wrestler model OBJ (assembled YOBJ geometry, slot 026) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/026/026_1.obj` | .obj | 11636 | Wrestler model OBJ (assembled YOBJ geometry, slot 026) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/027/027_0.obj` | .obj | 17280 | Wrestler model OBJ (assembled YOBJ geometry, slot 027) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/027/027_1.obj` | .obj | 17148 | Wrestler model OBJ (assembled YOBJ geometry, slot 027) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/028/028_0.obj` | .obj | 12934 | Wrestler model OBJ (assembled YOBJ geometry, slot 028) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/028/028_1.obj` | .obj | 12934 | Wrestler model OBJ (assembled YOBJ geometry, slot 028) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/029/029_0.obj` | .obj | 12752 | Wrestler model OBJ (assembled YOBJ geometry, slot 029) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/030/030_0.obj` | .obj | 16849 | Wrestler model OBJ (assembled YOBJ geometry, slot 030) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/030/030_1.obj` | .obj | 17123 | Wrestler model OBJ (assembled YOBJ geometry, slot 030) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/031/031_0.obj` | .obj | 16797 | Wrestler model OBJ (assembled YOBJ geometry, slot 031) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/031/031_1.obj` | .obj | 17776 | Wrestler model OBJ (assembled YOBJ geometry, slot 031) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/032/032_0.obj` | .obj | 11452 | Wrestler model OBJ (assembled YOBJ geometry, slot 032) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/032/032_1.obj` | .obj | 10672 | Wrestler model OBJ (assembled YOBJ geometry, slot 032) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/033/033_0.obj` | .obj | 13710 | Wrestler model OBJ (assembled YOBJ geometry, slot 033) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/033/033_1.obj` | .obj | 13693 | Wrestler model OBJ (assembled YOBJ geometry, slot 033) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/033/033_2.obj` | .obj | 8753 | Wrestler model OBJ (assembled YOBJ geometry, slot 033) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/034/034_0.obj` | .obj | 15944 | Wrestler model OBJ (assembled YOBJ geometry, slot 034) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/034/034_1.obj` | .obj | 11038 | Wrestler model OBJ (assembled YOBJ geometry, slot 034) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/035/035_0.obj` | .obj | 6995 | Wrestler model OBJ (assembled YOBJ geometry, slot 035) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/035/035_1.obj` | .obj | 18718 | Wrestler model OBJ (assembled YOBJ geometry, slot 035) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/036/036_0.obj` | .obj | 11296 | Wrestler model OBJ (assembled YOBJ geometry, slot 036) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/036/036_1.obj` | .obj | 11296 | Wrestler model OBJ (assembled YOBJ geometry, slot 036) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/037/037_0.obj` | .obj | 17389 | Wrestler model OBJ (assembled YOBJ geometry, slot 037) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/037/037_1.obj` | .obj | 15646 | Wrestler model OBJ (assembled YOBJ geometry, slot 037) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/038/038_0.obj` | .obj | 12419 | Wrestler model OBJ (assembled YOBJ geometry, slot 038) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/038/038_1.obj` | .obj | 12419 | Wrestler model OBJ (assembled YOBJ geometry, slot 038) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/039/039_0.obj` | .obj | 15181 | Wrestler model OBJ (assembled YOBJ geometry, slot 039) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/039/039_1.obj` | .obj | 5322 | Wrestler model OBJ (assembled YOBJ geometry, slot 039) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/040/040_0.obj` | .obj | 11002 | Wrestler model OBJ (assembled YOBJ geometry, slot 040) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/040/040_1.obj` | .obj | 6829 | Wrestler model OBJ (assembled YOBJ geometry, slot 040) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/041/041_0.obj` | .obj | 14883 | Wrestler model OBJ (assembled YOBJ geometry, slot 041) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/041/041_1.obj` | .obj | 13759 | Wrestler model OBJ (assembled YOBJ geometry, slot 041) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/042/042_0.obj` | .obj | 15085 | Wrestler model OBJ (assembled YOBJ geometry, slot 042) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/042/042_1.obj` | .obj | 16079 | Wrestler model OBJ (assembled YOBJ geometry, slot 042) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/043/043_0.obj` | .obj | 21327 | Wrestler model OBJ (assembled YOBJ geometry, slot 043) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/043/043_1.obj` | .obj | 21327 | Wrestler model OBJ (assembled YOBJ geometry, slot 043) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/044/044_0.obj` | .obj | 15503 | Wrestler model OBJ (assembled YOBJ geometry, slot 044) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/044/044_1.obj` | .obj | 15711 | Wrestler model OBJ (assembled YOBJ geometry, slot 044) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/045/045_0.obj` | .obj | 15842 | Wrestler model OBJ (assembled YOBJ geometry, slot 045) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/045/045_1.obj` | .obj | 14958 | Wrestler model OBJ (assembled YOBJ geometry, slot 045) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/045/045_2.obj` | .obj | 2076 | Wrestler model OBJ (assembled YOBJ geometry, slot 045) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/046/046_0.obj` | .obj | 15329 | Wrestler model OBJ (assembled YOBJ geometry, slot 046) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/046/046_1.obj` | .obj | 17682 | Wrestler model OBJ (assembled YOBJ geometry, slot 046) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/047/047_0.obj` | .obj | 19859 | Wrestler model OBJ (assembled YOBJ geometry, slot 047) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/048/048_0.obj` | .obj | 19859 | Wrestler model OBJ (assembled YOBJ geometry, slot 048) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/049/049_0.obj` | .obj | 19859 | Wrestler model OBJ (assembled YOBJ geometry, slot 049) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/050/050_0.obj` | .obj | 19859 | Wrestler model OBJ (assembled YOBJ geometry, slot 050) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/051/051_0.obj` | .obj | 19859 | Wrestler model OBJ (assembled YOBJ geometry, slot 051) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/052/052_0.obj` | .obj | 19859 | Wrestler model OBJ (assembled YOBJ geometry, slot 052) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/053/053_0.obj` | .obj | 19859 | Wrestler model OBJ (assembled YOBJ geometry, slot 053) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/054/054_0.obj` | .obj | 19859 | Wrestler model OBJ (assembled YOBJ geometry, slot 054) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/055/055_0.obj` | .obj | 19859 | Wrestler model OBJ (assembled YOBJ geometry, slot 055) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/056/056_0.obj` | .obj | 19859 | Wrestler model OBJ (assembled YOBJ geometry, slot 056) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/057/057_0.obj` | .obj | 19859 | Wrestler model OBJ (assembled YOBJ geometry, slot 057) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/058/058_0.obj` | .obj | 19859 | Wrestler model OBJ (assembled YOBJ geometry, slot 058) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/059/059_0.obj` | .obj | 19859 | Wrestler model OBJ (assembled YOBJ geometry, slot 059) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/081/081_0.obj` | .obj | 7529 | Wrestler model OBJ (assembled YOBJ geometry, slot 081) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/082/082_0.obj` | .obj | 7770 | Wrestler model OBJ (assembled YOBJ geometry, slot 082) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/083/083_0.obj` | .obj | 6976 | Wrestler model OBJ (assembled YOBJ geometry, slot 083) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/084/084_0.obj` | .obj | 7833 | Wrestler model OBJ (assembled YOBJ geometry, slot 084) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/085/085_0.obj` | .obj | 7488 | Wrestler model OBJ (assembled YOBJ geometry, slot 085) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/090/090_0.obj` | .obj | 6099 | Wrestler model OBJ (assembled YOBJ geometry, slot 090) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/091/091_0.obj` | .obj | 7468 | Wrestler model OBJ (assembled YOBJ geometry, slot 091) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/092/092_0.obj` | .obj | 7369 | Wrestler model OBJ (assembled YOBJ geometry, slot 092) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/093/093_0.obj` | .obj | 7790 | Wrestler model OBJ (assembled YOBJ geometry, slot 093) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/094/094_0.obj` | .obj | 5920 | Wrestler model OBJ (assembled YOBJ geometry, slot 094) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/095/095_0.obj` | .obj | 21400 | Wrestler model OBJ (assembled YOBJ geometry, slot 095) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/095/095_1.obj` | .obj | 21735 | Wrestler model OBJ (assembled YOBJ geometry, slot 095) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/096/096_0_pools.obj` | .obj | 104542 | Wrestler model OBJ (assembled YOBJ geometry, slot 096) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/097/097_0_pools.obj` | .obj | 104542 | Wrestler model OBJ (assembled YOBJ geometry, slot 097) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/099/099_0.obj` | .obj | 5390 | Wrestler model OBJ (assembled YOBJ geometry, slot 099) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/100/100_0_pools.obj` | .obj | 17889 | Wrestler model OBJ (assembled YOBJ geometry, slot 100) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/101/101_0_pools.obj` | .obj | 17889 | Wrestler model OBJ (assembled YOBJ geometry, slot 101) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/102/102_0_pools.obj` | .obj | 17889 | Wrestler model OBJ (assembled YOBJ geometry, slot 102) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/110/110_0_pools.obj` | .obj | 162975 | Wrestler model OBJ (assembled YOBJ geometry, slot 110) | ACCOUNTED-ELSEWHERE (wrestling repos per federation rule) |
| `teardown/wmxix/wrestlers/EXTRACTION-MANIFEST.txt` | .txt | 11583 | Wrestler model OBJ (assembled YOBJ geometry, slot EXTRACTION-MANIFEST.txt) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |

### teardown/wwe-wrestlemania-xix/ — 148 files

| Path | Type | Size (bytes) | What it is | Wiring status |
|---|---|---|---|---|
| `teardown/wwe-wrestlemania-xix/AKI-TEKKEN3-RETARGET.md` | .md | 2814 | Teardown/research documentation (Markdown) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/REVENGE-MODE-ARENAS.md` | .md | 2253 | Teardown/research documentation (Markdown) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/WMXIX-ASSEMBLY-SOLUTION.md` | .md | 2831 | Teardown/research documentation (Markdown) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/WMXIX-AXIS-PERMUTATION.md` | .md | 1238 | Teardown/research documentation (Markdown) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/WRESTLER-IDENTITY-MAP.md` | .md | 2537 | Teardown/research documentation (Markdown) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/WRESTLER-SKELETON.md` | .md | 6127 | Teardown/research documentation (Markdown) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/YANM-F32-CORR.md` | .md | 1751 | Teardown/research documentation (Markdown) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/YANM-FIRST8B.md` | .md | 1610 | Teardown/research documentation (Markdown) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/YANM-FORMAT.md` | .md | 4867 | Teardown/research documentation (Markdown) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/YANM-ITEM10-CYCLE.md` | .md | 8988 | Teardown/research documentation (Markdown) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/YANM-ITEM3-ITEM4-CYCLE.md` | .md | 7668 | Teardown/research documentation (Markdown) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/YANM-ITEM5-CYCLE.md` | .md | 8311 | Teardown/research documentation (Markdown) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/YANM-ITEM6-CYCLE.md` | .md | 15684 | Teardown/research documentation (Markdown) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/YANM-ITEM7-CYCLE.md` | .md | 5842 | Teardown/research documentation (Markdown) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/YANM-ITEM8-CYCLE.md` | .md | 5417 | Teardown/research documentation (Markdown) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/YANM-ITEM9-CYCLE.md` | .md | 6179 | Teardown/research documentation (Markdown) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/YANM-UNKNOWN8.md` | .md | 3857 | Teardown/research documentation (Markdown) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/YOBJ-PAYLOAD-ITEM1.md` | .md | 2995 | Teardown/research documentation (Markdown) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/YOBJ-SKINNING-NOTES.md` | .md | 1843 | Teardown/research documentation (Markdown) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/aki_to_tekken3_v1.json` | .json | 19683 | Research data JSON (decode/retarget/mapping data) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/atr_all_events.json` | .json | 242384 | Research data JSON (decode/retarget/mapping data) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/docs/CAW-EDIT-DATA-WMXIX.md` | .md | 2276 | Teardown/research documentation (Markdown) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/docs/WMXIX-FILE-LISTING.txt` | .txt | 237733 | Teardown data/listing (text) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/docs/WMXIX-TEARDOWN.md` | .md | 41747 | Teardown/research documentation (Markdown) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/docs/YANM-TEKKEN3-RETARGET.md` | .md | 6091 | Teardown/research documentation (Markdown) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/docs/YOBJ-BATCH-SEMANTICS.md` | .md | 4315 | Teardown/research documentation (Markdown) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/docs/YOBJ-DOL-DECODER-REPORT.md` | .md | 6535 | Teardown/research documentation (Markdown) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/docs/YOBJ-DOL-EXPERIMENT-A-RECORDWRITER.md` | .md | 8135 | Teardown/research documentation (Markdown) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/docs/YOBJ-SKINNING-DECODER-REPORT.md` | .md | 7286 | Teardown/research documentation (Markdown) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/docs/YOBJ-SKINNING-SOLUTION.md` | .md | 2332 | Teardown/research documentation (Markdown) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/docs/YUKES-VS-AKI-ANIMATION.md` | .md | 4702 | Teardown/research documentation (Markdown) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/docs/ecd-render-test/8503_0a_highpreset_view.png` | .png | 35156 | ECD/retarget render-test proof artifact | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/docs/ecd-render-test/FACE_ecd_view.png` | .png | 24516 | ECD/retarget render-test proof artifact | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/docs/ecd-render-test/FACE_front.png` | .png | 21568 | ECD/retarget render-test proof artifact | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/docs/ecd-render-test/FACE_standard.png` | .png | 39636 | ECD/retarget render-test proof artifact | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/docs/ecd-render-test/FACE_top.png` | .png | 62261 | ECD/retarget render-test proof artifact | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/docs/ecd-render-test/FIGHTING_ecd_view.png` | .png | 23369 | ECD/retarget render-test proof artifact | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/docs/ecd-render-test/FIGHTING_front.png` | .png | 23075 | ECD/retarget render-test proof artifact | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/docs/ecd-render-test/FIGHTING_standard.png` | .png | 43255 | ECD/retarget render-test proof artifact | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/docs/ecd-render-test/FIGHTING_top.png` | .png | 65769 | ECD/retarget render-test proof artifact | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/docs/ecd-render-test/a004_0a_highpreset_view.png` | .png | 29132 | ECD/retarget render-test proof artifact | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/docs/ecd-render-test/c139_0a_highpreset_view.png` | .png | 32165 | ECD/retarget render-test proof artifact | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/docs/ecd-render-test/c139_control_below.png` | .png | 31909 | ECD/retarget render-test proof artifact | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/docs/ecd-render-test/c200_0a_ecd_view.png` | .png | 56317 | ECD/retarget render-test proof artifact | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/docs/ecd-render-test/c200_0a_front.png` | .png | 23482 | ECD/retarget render-test proof artifact | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/docs/ecd-render-test/c200_0a_standard.png` | .png | 42910 | ECD/retarget render-test proof artifact | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/docs/ecd-render-test/c200_0a_top.png` | .png | 64823 | ECD/retarget render-test proof artifact | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/docs/ecd-render-test/c200_1a_ecd_view.png` | .png | 21427 | ECD/retarget render-test proof artifact | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/docs/ecd-render-test/c200_1a_front.png` | .png | 23104 | ECD/retarget render-test proof artifact | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/docs/ecd-render-test/c200_1a_standard.png` | .png | 42263 | ECD/retarget render-test proof artifact | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/docs/ecd-render-test/c200_1a_top.png` | .png | 65791 | ECD/retarget render-test proof artifact | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/docs/ecd-render-test/c200_2a_ecd_view.png` | .png | 20883 | ECD/retarget render-test proof artifact | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/docs/ecd-render-test/c200_2a_front.png` | .png | 23170 | ECD/retarget render-test proof artifact | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/docs/ecd-render-test/c200_2a_standard.png` | .png | 42644 | ECD/retarget render-test proof artifact | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/docs/ecd-render-test/c200_2a_top.png` | .png | 65567 | ECD/retarget render-test proof artifact | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/docs/ecd-render-test/ecd_all_clips.json` | .json | 18674 | ECD/retarget render-test proof artifact | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/docs/ecd-render-test/highpreset_metrics.json` | .json | 2634 | ECD/retarget render-test proof artifact | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/docs/ecd-render-test/metrics.json` | .json | 6630 | ECD/retarget render-test proof artifact | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/docs/ecd-render-test/showcase8503_ecd_view.png` | .png | 37691 | ECD/retarget render-test proof artifact | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/docs/ecd-render-test/showcase8503_front.png` | .png | 23728 | ECD/retarget render-test proof artifact | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/docs/ecd-render-test/showcase8503_standard.png` | .png | 43492 | ECD/retarget render-test proof artifact | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/docs/ecd-render-test/showcase8503_top.png` | .png | 66651 | ECD/retarget render-test proof artifact | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/docs/proof/yobj-000_0_assembled.obj` | .obj | 16588 | Model OBJ (proof/assembly output) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/docs/proof/yobj-000_0_assembled_check.png` | .png | 73722 | Render/proof image | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/docs/retarget_v2_paths.png` | .png | 28622 | Render/proof image | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/docs/retarget_v2_render.png` | .png | 249934 | Render/proof image | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/docs/wrestler-skeleton-000.json` | .json | 19364 | Research data JSON (decode/retarget/mapping data) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/docs/yanm-rec3-rule.json` | .json | 340 | Research data JSON (decode/retarget/mapping data) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/docs/yanm-task2-finish.json` | .json | 53748 | Research data JSON (decode/retarget/mapping data) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/docs/yanm-track-joint-map.json` | .json | 40881 | Research data JSON (decode/retarget/mapping data) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/docs/yanm_to_tekken3_v1.json` | .json | 144099 | Research data JSON (decode/retarget/mapping data) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/docs/yanm_to_tekken3_v1_plot.png` | .png | 79669 | Render/proof image | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/docs/yanm_to_tekken3_v2.json` | .json | 177824 | Research data JSON (decode/retarget/mapping data) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/docs/ycg-group-mapping.json` | .json | 5734 | Research data JSON (decode/retarget/mapping data) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/objs/elbow_me0_000_l0.obj` | .obj | 4811 | Model OBJ (proof/assembly output) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/objs/wrestler_000_0.obj` | .obj | 19791 | Model OBJ (proof/assembly output) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/__pycache__/gcn_fst.cpython-312.pyc` | .pyc | 6855 | Compiled Python cache (tooling artifact) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/aki_to_tekken3.py` | .py | 5035 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/assemble_wrestler.py` | .py | 8930 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/dol/dolmap.py` | .py | 1186 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/dol/effscan.py` | .py | 1239 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/dol/funcmap.py` | .py | 1263 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/dol/recwriter_scan.py` | .py | 4948 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/fk_ycg.py` | .py | 2913 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/gcn_fst.py` | .py | 3735 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/render_retarget_v2.py` | .py | 4247 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/wmxix_extract.py` | .py | 1436 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/wmxix_range_iso.py` | .py | 5760 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/yanm_atr_motion_xcorr.py` | .py | 3824 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/yanm_atr_semantics.py` | .py | 5433 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/yanm_atr_semantics2.py` | .py | 7160 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/yanm_baseid.py` | .py | 2379 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/yanm_baseid_hier.py` | .py | 3271 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/yanm_census.py` | .py | 1921 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/yanm_ecd_highpreset.py` | .py | 5265 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/yanm_ecd_marginals.py` | .py | 3090 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/yanm_ecd_render_test.py` | .py | 11905 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/yanm_f32_corr.py` | .py | 3129 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/yanm_first8b_test.py` | .py | 2604 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/yanm_gait.py` | .py | 1459 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/yanm_hash_battery.py` | .py | 7967 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/yanm_hashscan.py` | .py | 1047 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/yanm_idblock_routing.py` | .py | 4113 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/yanm_item3_byteramp2.py` | .py | 2890 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/yanm_item3_pof0.py` | .py | 1917 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/yanm_item3_probe.py` | .py | 3885 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/yanm_item4_byteramp.py` | .py | 2775 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/yanm_item5_cycle.py` | .py | 8340 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/yanm_item5b_cycle.py` | .py | 7693 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/yanm_item6_baseid.py` | .py | 6835 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/yanm_item6_baseid2.py` | .py | 4394 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/yanm_item6_ecd.py` | .py | 7371 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/yanm_item6_ecd2.py` | .py | 5816 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/yanm_item6_ecd3.py` | .py | 5104 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/yanm_item6_lr.py` | .py | 3333 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/yanm_item6_lr2.py` | .py | 1346 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/yanm_keyseg.py` | .py | 2271 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/yanm_pof0_substructure.py` | .py | 4522 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/yanm_rec3_rule.py` | .py | 3663 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/yanm_semantics.py` | .py | 6263 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/yanm_task2_finish.py` | .py | 9167 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/yanm_task2b.py` | .py | 10472 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/yanm_to_tekken3.py` | .py | 5340 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/yanm_to_tekken3_v2.py` | .py | 7454 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/yanm_track_joint_map.py` | .py | 5210 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/yanm_track_probe.py` | .py | 2907 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/yanm_typeb_decode.py` | .py | 3685 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/yanm_typeb_probe.py` | .py | 3211 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/yanm_typeb_probe2.py` | .py | 3365 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/yanm_typeb_table.py` | .py | 2065 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/yanm_unitfit.py` | .py | 3487 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/yanm_unknown8.py` | .py | 4999 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/ycg_parse.py` | .py | 1003 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/ycg_ymg_map.py` | .py | 1934 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/yobj_batch_semantics.py` | .py | 4765 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/yobj_batches.py` | .py | 2186 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/yobj_decode.py` | .py | 10182 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/yobj_diag.py` | .py | 2647 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/yobj_payload_item1.py` | .py | 3655 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/yobj_runtime.py` | .py | 4169 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/yobj_skin_assemble.py` | .py | 3899 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/yobj_strips.py` | .py | 5728 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/yobj_v3_probe.py` | .py | 1650 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/yobj_validate.py` | .py | 2875 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/tools/yukes_fmt.py` | .py | 2746 | Teardown/research tool (Python) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/wrestler-000-solved-faced.obj` | .obj | 26090 | Model OBJ (proof/assembly output) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/wrestler-000-solved-views.png` | .png | 109659 | Render/proof image | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
| `teardown/wwe-wrestlemania-xix/wrestler-000-solved.obj` | .obj | 18341 | Model OBJ (proof/assembly output) | DOC/TOOLING (teardown record; consumed by RE pipeline, not the game build) |
