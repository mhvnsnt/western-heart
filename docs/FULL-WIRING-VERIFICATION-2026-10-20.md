# FULL WIRING + CANON CONVERSION — INDEPENDENT VERIFICATION (2026-10-20)

**Verifier:** verification sub-lane (recovery attempt 2; attempt 1 was killed by a daemon
restart mid-work — its one surviving piece of work, the PR #375 forward-merge, is audited
in §5 below). **Scope:** the four game lanes of the FULL WIRING + CANON CONVERSION order
(owner, 2026-10-20 ~08:06 CDT) for mhvnsnt/western-heart: WMXIX / mat-legends (PR #374),
Eastern Mind (PR #375), WWF No Mercy / mat-kings (PR #379), Tekken 3 / iron-legacy
(PR #382). **Method:** API-first (GitHub git-trees / contents / pulls APIs; no full clone).
Every inventory file below was re-counted from the lane's own `WIRING-INVENTORY.md` rows
and cross-checked against the live git tree. Spot-checks were run against the actual data
files (JSON row counts, SHA-256, header bytes), not against lane prose.

**State change during verification:** PR #375 was OPEN when this lane was briefed and was
MERGED to main at 2026-10-20T16:56:52Z while verification ran. Final PR states:
#374 MERGED, #375 MERGED, #379 OPEN + MERGEABLE + all checks pass (after §5
reconciliation), #382 OPEN + MERGEABLE + all checks pass (after §5 reconciliation).

## 0. Terminal accounting — definitions

Every inventoried file is counted in exactly one terminal state:

- **WIRED+CONVERTED** — a wiring consumer is cited AND a canon-conversion record applies.
- **WIRED** — a wiring consumer is cited (game data, library, registry, canon, pipeline).
- **FLAGGED** — not (fully) wired, with a named reason (includes the lanes' PARTIAL,
  NOT-WIRED, SOURCE-ONLY, DOC/TOOLING and ACCOUNTED-ELSEWHERE statuses; the sub-reason is
  always given, and the lane-native status table is reproduced so no lane number is lost).

## 1. WMXIX / mat-legends — PR #374 (MERGED)

Inventory rows re-counted: **1,709** = 1,708 baseline files (wmxix 1,560 +
wwe-wrestlemania-xix 148, both tree-verified) + `CANON-CONVERSION.md`, which the inventory
lists as a row; `WIRING-INVENTORY.md` itself is the 1,710th file (main now holds
1,562 + 148 = 1,710 in the two folders).

Lane-native statuses (row-level recount, exact): WIRED 170 · WIRED-DATA 1,211
(1,169 arena textures + 40 arena files + 2 CAW catalog files) · CANON 2 · conversion
record 1 · DOC/TOOLING 199 · ACCOUNTED-ELSEWHERE 126. Sum = 1,709.

| Terminal state | Files | Composition |
|---|---:|---|
| WIRED+CONVERTED | 212 | 170 animation clips (ML- canon IDs + move entries) + 40 arena files (canon stage entries in `game/assets/stages/mat-legends/stages.json`) + 2 CAW catalog files (Creation Suite index) |
| WIRED | 1,172 | 1,169 arena textures (stages.json `texture_dir` refs) + 2 canon source docs + 1 conversion record |
| FLAGGED | 325 | 199 DOC/TOOLING (teardown record; consumed by the RE pipeline, not the game build) + 126 ACCOUNTED-ELSEWHERE (wrestler models — wrestling repos, federation rule) |
| **Total** | **1,709** | |

Spot-checks (all against files on main): `WMXIX-CLIP-INDEX.json` = 170 clips, bank split
a×35 / b×24 / c×105 / d×6 exactly as claimed; `WMXIX-MOVES.json` = 169 move entries;
`stages.json` = 12 stage entries; every move `anim_ref` resolves to a file in the tree.
Sample of 25 inventory paths: all exist.

**Lane claims that did NOT verify as stated:**
- **"1,385 newly wired"** — not reproducible from the inventory. Row-level newly wired =
  1,381 (170 WIRED + 1,211 WIRED-DATA). 1,385 is reached only by also counting the 4 new
  deliverable files themselves (clip index, moves, stages, CAW index), which are outputs,
  not inventoried teardown files.
- **CAW "2,690 parts by category"** — the total 2,690 verifies by extension
  (`.tex` 1,470 + `.ymg` 1,200 + 20 others), but `customization/mat-legends-caw.json`'s
  `by_category` table sums to **2,682**, not 2,690: 8 parts carry no category (the count
  matches the 8 `.ycg` files; stated as the probable cause, not proven per-file).
- Audit summary says "127 wrestler OBJs ACCOUNTED-ELSEWHERE"; row-level truth is 127
  files under `wrestlers/`, of which 126 are ACCOUNTED-ELSEWHERE and 1 is DOC/TOOLING.
  (Folder count conflated with status count; no file is missing.)

## 2. Eastern Mind — PR #375 (MERGED 2026-10-20T16:56:52Z)

Inventory rows re-counted: **5,707** (the inventory's own category-summary table adds 12
non-file rows; excluded, the file rows reconcile exactly). Main now holds 5,709 blobs
under `teardown/eastern-mind/` (5,707 + the lane's inventory + conversion docs).

| Terminal state | Files | Composition |
|---|---:|---|
| WIRED+CONVERTED | 762 | prologue-ending 661 + palettes 97 + soundtrack 4 — converted to authored canon in `CANON.md` §8 + registry in `game/assets/stages/eastern-mind/stages.json` by this PR |
| WIRED | 3,817 | stage groups 3,304 (helix-palace 1,282, tree-of-life 505, plains-of-chi-u 518, palace-of-dreaming 676, octagonal-shrine 223, phantom-marketplace 100) + incarnation-system 512 + TEARDOWN.md 1 — canon (§1/§5/§6) + `game/js/stages.js` / `game/js/modes.js` consumers cited per file |
| FLAGGED | 1,128 | transcript-promo — archival promo/transcript material, accounted-elsewhere as source archive (registry `archive` entry), no canon/game consumer by design |
| **Total** | **5,707** | 3,817 + 762 + 1,128 — the lane's claimed split verifies **exactly** |

Spot-checks: `stages.json` on main = 6 stages, 2 systems, 4 audio tracks (soundtrack = 4
files ✓), 1 archive entry. Sample of 25 inventory paths: all exist.

**Honesty note (the lane's own Flag 2, verified):** "WIRED" for Eastern Mind is at
canon/registry/system level. No game code loads any individual file from
`teardown/eastern-mind/` — the extracted bitmaps are not yet stage textures, the face
bitmaps do not yet feed the reincarnation screen, and the soundtrack does not yet play.
The lane disclosed this plainly; it is carried into the engine follow-up roll-up (§8),
not treated as a failed claim.

## 3. WWF No Mercy / mat-kings — PR #379 (OPEN, reconciled §5)

Inventory rows re-counted: **18,544**, and the per-status recount matches the lane's
stated verdict totals to the file: WIRED-DATA 5,787 · PARTIAL 5,030 · NOT WIRED 5,384 ·
WIRED 2,318 · WIRED-DOC 19 · WIRED-TOOL 6. Sum = 18,544.

| Terminal state | Files | Composition |
|---|---:|---|
| WIRED+CONVERTED | 5,787 | all animation clips wired as library data by this PR in `moveset-library/movesets/mat-kings-move-database.json`: 4,409 moves converted NM-### → MK-#### + 1,353 system clips + 25 previously unmanifested tail clips |
| WIRED | 2,343 | 2,318 WIRED + 19 WIRED-DOC + 6 WIRED-TOOL (pre-existing consumers: stages, customization parts, move-slot templates, FileTableDB pipeline) |
| FLAGGED | 10,414 | 5,384 NOT WIRED (incl. `models/unlabeled/` 4,862 — wrestler attire meshes, not wired by federated design; `recomp/` 164; character/environment textures 350) + 5,030 PARTIAL (`textures/rom/`: only 379 copied into the Creation Suite — 146 faces + 233 skins; the rest feeds the stage-reskin pipeline in open PR #345) |
| **Total** | **18,544** | |

**Baseline drift (not a lane error):** the inventory is exact at its stated baseline
commit `fa4f375`. Current main holds **18,549** files in the folder — 5 files landed
after the baseline from another lane and are in no inventory: `docs/ANIMATION-ISOLATION.md`,
`docs/CAW-EDIT-DATA.md`, `docs/caw-categories.json`, `docs/caw-name-table.json`,
`tools/caw_parse.py` (CAW documentation/tooling). Terminal state for those 5: FLAGGED —
uninventoried. Current-tree accounting: 5,787 + 2,343 wired (8,130) + 10,419 flagged
= 18,549.

Spot-checks against the branch's move database (all exact): moves 4,409 (IDs MK-0000 …
MK-4408), system_anims 1,353, unmanifested_clips 25 (first `0x445b`, last `0x4c04`);
entries with power data 507; with Tekken-style inputs 4,153; with slot eligibility 1,966;
all 5,787 `anim_ref`s resolve to files in the tree. `animations/manifest.json` itself
re-verified: 5,762 clips (move 4,409 / system 1,353), range `0x2dd9`–`0x445a`, **no
`label` field on any entry**.

**Lane claim that did NOT verify as stated:** "−9 lines = exactly the 3 anim_ref
corrections." The PR's −9 deletions are: 7 anim_ref line replacements (the 3 unique
moves NM-001/002/003, appearing in 3 files) + 2 `_note` line replacements (one in each
copy of MOVE-DATABASE.json). There are **no other deletions** — the substance (nothing
hidden was deleted) verifies; the shorthand does not.

## 4. Tekken 3 / iron-legacy — PR #382 (OPEN, reconciled §5)

Inventory rows re-counted: **19,477** = 19,435 on main (tree-verified, exact) + 42
lane-added files (enumerated and matched one-for-one against the PR diff: 13 divmot
banks + 26 moveset files + 1 pose OBJ + inventory + conversion record). The per-status
recount matches the lane's stated status table to the file: SOURCE-ONLY 19,301 ·
WIRED 75 · WIRED (tooling) 9 · WIRED (extraction source) 4 · WIRED (record) 2 ·
PARTIAL 20 · NOT-WIRED 66. Sum = 19,477.

| Terminal state | Files | Composition |
|---|---:|---|
| WIRED | 90 | 75 WIRED (original 7 fighters' banks/movesets/models/stages — converted at the game-data layer per CANON-CONVERSION §§2–3) + 9 tooling + 4 extraction sources + 2 lane records. No file was newly converted *in* this PR; its 42 additions are verified extractions awaiting conversion (lane's own status) |
| FLAGGED | 19,387 | 19,301 SOURCE-ONLY (teardown reference/provenance: `tim-output/` 17,116 + vendored `tools/tekken3recompiled/` 1,957 + renders/docs) + 66 NOT-WIRED (26 round-2 moveset-layer + 13 bank-layer + 23 UI templates + 4 disc metadata/empty) + 20 PARTIAL (15 stage metadata JSONs, 4 Heihachi model files, 1 Heihachi bank — decode blocked, below) |
| **Total** | **19,477** | |

Triple verification, re-run by this verifier on 3 of the 13 new banks (size + header
byte at offset 1 == divmot type + SHA-256 prefix vs `docs/BNS-ORGANIZATION-PATTERN.md`):
**Paul** divmot00 — 313,472 B ✓, byte 0 ✓, `06f6447a` ✓ · **Dr. Bosconovitch** divmot18 —
332,372 B ✓, byte 18 ✓, `130ee660` ✓ · **Julia** divmot10 — 267,924 B ✓, byte 10 ✓,
`d4c8ce91` ✓. Moveset rows re-summed from the 13 CSVs: **5,663 exactly** (per-file
counts match the PR's own additions: paul 372, law 459, lei 604, nina 529, hwoarang 496,
eddy 436, julia 360, kuma 303, ogre 330, anna 560, bosconovitch 647, gon 369,
forestlaw 198). No lane claim for Tekken 3 failed verification.

## 5. PR diff discipline (Job B) + reconciliation (Job C)

Diff discipline — all four PRs, from the pulls API file lists and deletion patches:

| PR | Files | Additions / deletions | Verdict |
|---|---|---:|---|
| #374 WMXIX | 8 | +8,838 / **−0** | Additions-only claim TRUE. No `game/js/` files. No rig/animation-data edits (new data files only). |
| #375 Eastern Mind | 4 | +6,757 / **−0** | Additions-only claim TRUE. CANON.md append-only (+86/−0). No `game/js/` files. |
| #379 No Mercy | 9 | +100,014 / **−9** | Deletions audited line-by-line (§3): 7 anim_ref replacements + 2 `_note` replacements, nothing else. No `game/js/` files. No file deletions. |
| #382 Tekken 3 | 47 | +1,116,707 / **−3** | "3 replaced lines" claim TRUE: MOVES-LIBRARY.md bank-count line (1), ANIMATION-INDEX.json stale pose-solving note (1) + Gun Jack entry comma line (1). No `game/js/` files; no `lab/tools/` or shared bake/retarget code touched. No file deletions. |

No mass-staging event in any PR (largest file count is #382's 47, all enumerated
per-character/per-bank artifacts). No shared rig, shared animation data, or retarget
code was edited by any lane.

**C0 — audit of attempt 1's PR #375 forward-merge: SOUND.** The branch history is two
commits: `efbde06d` (lane commit) and `1cfaa6a3` "Merge remote-tracking branch
'origin/main' into wiring/eastern-mind-canon-20261020" (attempt 1's work). At the branch
head, CANON.md contains BOTH #374's complete mat-legends section (BEGIN/END markers
intact) AND #375's complete §8 (all eight subsections), with zero conflict markers; the
merged main file was re-verified directly with the same result. Final checks on #375:
instruction-gate SUCCESS, deletion-guard SUCCESS, no-deletion guard SUCCESS. Nothing was
lost in that merge; no fix was needed.

**C1 — PR #379 forward-merge: DONE.** Merged current `origin/main` into
`wiring/mat-kings-no-mercy-20261020` (merge commit `73b2bd4`, pushed). Conflicts were
exactly the append-adjacency conflicts in CANON.md and RENAME-MAP.md (MOVES-LIBRARY.md
auto-merged); resolved keeping ALL appended sections from both sides (settled main
content first, mat-kings append after it), no content lost, no markers, MARIPOSA header
untouched. The PR's instruction-gate had been FAILURE on paraphrased body headings; the
body was reformatted to the gate's exact heading strings with content unchanged (every
deviation line now carries its approval link/#ref). Result: **MERGEABLE, all checks
pass** (instruction-gate pass, deletion-guard pass, no-deletion guard pass).

**C2 — PR #382 forward-merge: DONE (scope note).** The brief asked to re-confirm #382
"still MERGEABLE + green"; it was no longer either — #375's merge had made it
CONFLICTING on CANON.md. The same forward-merge was therefore applied (merge commit
`960d131`, pushed): one CANON.md adjacency conflict, resolved keeping both sides (main's
§8 + mat-legends first, the Tekken 3 appendix after), no markers, all other files
auto-merged; the PR diff vs main remains 47 files (insertions 1,116,706 — one context
line deduped by the merge). Result: **MERGEABLE, all checks pass.**

**Content contradictions — NOT resolved, both texts kept (per brief):**
- Tekken 3 Julia: ROSTER.md (ZEN's body donor = Julia) vs CANON.md §6 (NIGHTWOLF's base
  = Julia) vs `game/js/roster-full.js` (zen base = 'Heihachi'). Flagged §8.
- Eastern Mind ZEN/GYOU: CANON.md §4 leaves both unvesseled while `game/js/modes.js`
  already carries zen/gyou vessel-affinity entries. Flagged §8.

## 6. MARIPOSA — the "Butterfly Soul" header (Job D1)

**Answer: the text "Butterfly Soul" exists nowhere reachable.** CANON.md was fetched and
grepped at five refs — current main, and the head of every wiring branch (#374, #375,
#379, #382). Every ref carries exactly ONE Mariposa header: `### MARIPOSA — The Sealed
Soul` (§7). No "Butterfly Soul" header, and the string "Butterfly Soul" does not occur
anywhere in CANON.md at any of those refs. (A repo code search was also attempted but
its index returned 0 even for MARIPOSA, which is demonstrably indexed in CANON.md, so
the conclusion rests on the direct file fetches.) The standing note's second header is
either already resolved on main or lives somewhere outside the repo's reachable refs —
it is **not** an open duplication in the canon file. ("Butterfly" does exist in CANON.md
§7 as Mariposa's *attire* decision — Butterfly Default, Slot 1 — a different thing from
a second character header; owner law there already states Mariposa is ONE character.)

## 7. ANIMATION-INDEX.json + stale docs (Jobs D2, D3)

**ANIMATION-INDEX — both lane claims verified in substance; recommendation:
ANNOTATE AS SUPERSEDED PER GAME; do not rewrite the chunks in place, and correct the
summary counts in a follow-up.**
Verified structure on main: the No Mercy categories are equal range-chunks of the
manifest — system bank `0x2DD9`–`0x3321` (1,353 clips) chopped into 7 near-equal chunks
(193/193/222/222/193/193/194) labelled stances/walks/entrances/taunts/getups/grapple
positions/misc, and move bank `0x3322`–`0x445A` (4,409) into 6 chunks (762–764, 735,
735) labelled strikes/grapples/submissions/high_flying/weapons/misc_moves. The labels
are **not** the clips' true FileTableDB categories (true labels vary inside every
chunk). 170 WMXIX entries (different schema, no `file_id`) are mixed into 5 of the
categories. Category lists total 5,932 entries = 5,762 manifested NM clips + 170 WMXIX;
the summary's `no_mercy_clips: 5,762` is the **manifest** count — the real NM bank is
5,787, and the 25 tail clips (`0x445B`–`0x4472`, `0x4C04`) are absent from the index
entirely. The No Mercy lane's framing ("lists sum 5,932 vs 5,787 real") mixes the two
sources in its arithmetic, but its substance — range-chunk labels are inaccurate for No
Mercy and the label-true mat-kings database supersedes the index for that game — is
**correct**. The Tekken 3 lane's claim also verifies: the index's T3 section on main
still lists only the original 7 banks with the stale "pose solving blocked on USA EXE
tables" note; PR #382 updates it to all 20 banks with the verified current note.
Reasoning for annotate-not-rewrite: other lanes consume the index's range layout; the
label-true replacements already exist per game (mat-kings DB, WMXIX-CLIP-INDEX, the
#382 T3 section). A follow-up should (a) add a per-source "superseded by" annotation,
(b) correct the summary to state manifested-vs-real NM counts. This verification PR
does not rewrite the index (per brief).

**Stale doc (a) — `teardown/wwf-no-mercy/TEARDOWN.md`: STALE, FIXED in this PR.**
Verified against the tree: `re-docs/assets/` contains exactly **2 GLBs**, both
environment menu scenes (`main-menu-scene.glb`, `menu_scene.glb`, 201,180 bytes each).
The doc's "13 character GLBs + 2 environment GLBs in re-docs/assets/3d Assets/ (9
wrestlers: Rock ×3, Austin, HHH, Nash, Hall, HBK ×2, Angle, RVD, Rhino, Stephanie)" is
false for the current tree — the wrestler GLBs are not in Western Heart at all (they are
accounted-elsewhere in the wrestling repos). Also stale in the same doc: the manifest
description claims a per-clip `label` (no entry carries one) and `move` kind count
4,434 (actual 4,409), and the "15 community GLBs" line for `re-docs/` (15 is the folder's
total file count, of which 2 are GLBs). Corrections applied line-by-line in this PR and
named in its body.

**Stale doc (b) — `teardown/tekken3/TEARDOWN.md`: STALE, FIXED in this PR.**
Its "Correction 2026-10-13" BNS table (Jin 143, Bryan 167, Heihachi 175, Gun Jack 199)
contradicts `docs/BNS-ORGANIZATION-PATTERN.md` (Jin 151, Bryan 183, Heihachi 191, Gun
Jack 215) — and the pattern doc is the one the tree proves: the model folders on main
are `models/jin151`, `models/bryan183`, `models/heihachi191`, `models/gunjack215`
(King 95, Yoshimitsu 103, Xiaoyu 127 agree in both docs and in the folders). The root
cause is visible in the doc itself: its name-index list omits TIGER (9) and PANDA (13),
shifting every index from JIN onward, and 71 + index×8 then yields the wrong IDs. The
four wrong P1/P2 pairs are corrected in this PR in both places they appear (the table
and the "remaining character extractions" list), with a dated correction note flagging
the index-list inconsistency and the superseded pose-sampling / motion-bank sections
(banks are now all extracted; pose solving uses the verified USA EXE tables — see
teardown/tekken3/CANON-CONVERSION.md §5, PR #382). The index list itself was not
rewritten wholesale: which roster the full 22-name list should carry is a coordinator
call; the note names the pattern doc as governing.

## 8. Flagged-items roll-up (all four games)

**Owner canon decisions**
- No Mercy: 17 stage display names (conversion table staged, CANON-CONVERSION §4);
  42 wrestler identities (zero mapped, none invented); persona-named move labels
  (e.g. Reverse Tazzplex) awaiting a naming pass.
- WMXIX: wrestler slot → WH character assignment (127 model files accounted-elsewhere
  pending it); Revenge Mode canon name; per-clip move names (semantics decode open,
  provisional labels explicitly non-canon); `bs/5_*` and `kaijo_x8` stage assignments.
- Tekken 3: mappings for Law/Forest Law, Ogre, Gon, Panda (none exist); Lei/BYOU vessel
  name (CANON.md itself marks it blocked on the owner); the Julia/ZEN/Nightwolf donor
  conflict (§5); WH names for the 15 T3 stages; the `iron-legacy` directory rename
  (PENDING in RENAME-MAP.md, coordinator-sequenced).
- Eastern Mind: ZEN/GYOU canon-vs-code vessel availability (§5); per-file WH asset
  names (RENAME-MAP.md: NEEDED); any further mining of transcript-promo (1,128 files).

**Format / pipeline blockers**
- Tekken 3: Mokujin divmot15 has no data on this disc image (BNS record 295, size 0) —
  unblocking needs a different disc image; Heihachi wh-anim decode/GLB blocked on his
  KMD's empty part rows 2/9/13 (both costumes) — the shared bake tool was deliberately
  NOT patched (per-character isolation); the PR #243 schema-v2 moveset generator is not
  in the repo, blocking round-2 game-layer movesets.
- No Mercy: CAW save-record layout needs a real emulator save dump; library-scale
  AKI→Tekken retarget is proven on exactly 1 clip (owned by PR #364).
- WMXIX: arena geometry is decoded point clouds — face reconstruction open, so no
  WMXIX geometry is playable yet; clip `c138_0a` is a 72-byte stub with wrong magic.
- Eastern Mind (source teardown gaps): ~7% of BITD chunks unmatched to dimension info;
  Lingo scripts not decompiled; THUM thumbnails not extracted (redundant).

**Engine follow-ups (game/js/ and build consumption)**
- Eastern Mind: sample the extracted bitmaps as stage textures; face bitmaps into the
  reincarnation screen; soundtrack into `game/js/audio.js`; palette consumption in the
  texture pipeline. The registry (`game/assets/stages/eastern-mind/stages.json`) is the
  map for all of it.
- No Mercy: engine consumption of the grappling data (fighter.js implements Tekken
  throws only); stage display-name renames in stages.js once the owner names them;
  ANIMATION-INDEX annotation follow-up (§7).
- WMXIX: engine loader hook for `game/assets/stages/mat-legends/stages.json`;
  Creation Suite consumption of the CAW catalog (`custom-fighter.js` does not read it
  yet); a Revenge/traversal mode in modes.js if the owner canonizes one.
- Tekken 3: schema-v2 game movesets for the 13 round-2 banks; `t3anims.js` heihachi
  registration after his decode lands; T3 stage label renames in stages.js;
  retro-attire wiring in attires.js (T3 GLBs currently live only in `lab/game/assets/`).

**Accounted-elsewhere**
- Eastern Mind transcript-promo: 1,128 files, retained in place as source archive.
- WMXIX wrestler models: 126 files → mhvnsnt/wrestling-game +
  mhvnsnt/wrestlemania-xix-mod; CAW part files (2,690) live on the ISO/release side,
  catalogued in-repo, not duplicated.
- No Mercy: the 10 wrestler models (13 GLBs) → wrestling repos (NOT in this tree; only
  the 2 environment GLBs are); `models/unlabeled/` 4,862 files and the 350
  character/environment textures stay in the teardown per owner law, unwired by
  federated design.

## 9. Feel-gap roll-up

- **Eastern Mind:** reincarnation has no face (the face bitmaps exist; the screen offers
  vessels, not faces); the lands do not look like themselves (procedural stages, bitmaps
  unsampled); the head-world is silent (4 soundtrack files, none plays); soul
  progression is invisible between fights (no diegetic surface implements §8's Colour
  Is Law settling).
- **No Mercy:** no No Mercy clip plays in-engine yet — the grappling *feel* cannot be
  verified in a build until the retarget/loader step (PR #364) lands; the data layer is
  complete and Tekken-input-mapped.
- **WMXIX:** clips are library data on a research skeleton — nothing is attached to any
  WH fighter; arena geometry is point clouds, so mat-legends stages have canon identity
  and registry entries but no playable geometry.
- **Tekken 3:** TOU (Paul), KAI (Eddy) and GYOU (Hwoarang) still play on proxy
  movesets at the game layer (their real banks + 5,663 moves now exist in the
  teardown); Diablo has no decoded animation bank (blocker above) while the other six
  T3-sourced fighters do; only 7 of 20 character banks have any game-layer presence.

## 10. Per-character isolation verdict

**PASS for all four lanes.** No lane edited a shared rig, shared animation data, or
shared retarget/bake code. WMXIX and Eastern Mind touched no character files at all.
The Tekken 3 lane's artifacts are per-character by construction (each bank sliced and
SHA-verified independently; the only shared input is the read-only divmot99 common
bank, Tekken 3's own design, exactly as the original 7 were parsed; Eddy/Tiger and
Kuma/Panda bank sharing is the source game's own). The No Mercy lane touched shared
library data plus exactly one character file — `pantera-moveset.json` — correcting
Pantera's *own* Scoop Slam anim_ref to the clip the FileTableDB proves is the Scoop
Slam (MK-0125). The Heihachi blocker was reported rather than fixed via the shared
bake tool, which is the isolation law working as intended.

## 11. Recommended merge order

1. **PR #379** (No Mercy) — MERGEABLE, all checks pass. Smallest remaining diff
   (9 files); its gate body is now in the exact format.
2. **Forward-merge main into PR #382, then merge #382** — after #379 lands, #382 will
   conflict once more on the CANON.md append adjacency (both appendices sit at the end
   of the file). The resolution is mechanical and already proven twice in §5: keep both
   sections, settled content first, the new append after. Then #382 is MERGEABLE with
   checks already passing on identical content.
3. **This verification PR last** — it touches only `docs/` + the two TEARDOWN.md files,
   which no other wiring PR touches, so it cannot conflict with either merge above;
   its counts describe the branches as verified.

## 12. What this verification did NOT do

It did not re-run any lane's extraction, decode, or conversion; failed or imprecise
claims are documented above, not silently fixed (the only content changes are the
Job D stale-doc corrections in `teardown/wwf-no-mercy/TEARDOWN.md` and
`teardown/tekken3/TEARDOWN.md`, named line-by-line in this PR's body). It did not merge
any PR. Visual/playtest verification was out of scope — no lane altered anything
renderable in this program except data files.
