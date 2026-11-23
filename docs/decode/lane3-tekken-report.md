# Lane 3 — TEKKEN, full paired moves — report

Date: 2026-11-22/23. Owner order 2026-11-22: get ALL Tekken moves/animations
decoded, wired, merged clean.

## Answer first

Decoded/wired/landed in this lane: **0 clips decoded, 0 wired to named Bannon
moves, 0 landed.** Nothing was faked. What this lane did land as prepared work:
a corrected re-extraction path (verified against upstream docs), a King
paired-throw table transcribed from the real `.tkmvst` record, and a full
fixability verdict on the 383 partial clips. The two PRs that would carry
that work were prepared but NOT opened: the GitHub write approval for the
first step (create branch `lane-c/t7-extract-none` in western-heart) timed
out unanswered (approval_expired, approval_id
connector-attempt-ee66cacd41d47040df85078b03eba75a0b76390d87d1e3b6100e8b249e30045a)
and the instruction is not to retry without the user asking. Prepared file
contents are in `lane3-push-ready/` in this directory, ready to push once a
fresh approval is given.

## 1. King .tkmvst — status

- The file exists and was already verified: `T7_King.tkmvst`, 15,773,258 B,
  header `TKM21.0`, gameId 0, target King, 2,787 moves, CRC32 ok (expected ==
  actual 2114714009), extraction run 44858568891 (PR #1803, MERGED 2026-11-22
  11:58am ET by mhvnsnt — it is NOT open).
- It lives ONLY as a GitHub Actions artifact (`king-tkmvst`, 13.7 MB, sha256
  613826d7…), NOT in the repo on main, NOT in a release. Durable home
  undecided. Artifact expires ~2027-02-19 (90-day default, no retention-days
  set). This lane did NOT verify the artifact is still downloadable: the
  GitHub MCP connector has no artifact-download tool, and the `gh` CLI in
  this VM is not logged in (`gh auth status`: not logged into any GitHub
  hosts). No token is available to this lane. Download needs the main agent
  (browser / git-authed machine) or a workflow run that re-fetches it.
- **Blocker 1 (codec):** the extracted file is LZ4 type 1, and
  `tools/anim/tkmovesets2/tkmvst_to_wh.py` refuses it outright
  (`decompress_payload` raises TkmvstError for comp == 1). The file cannot be
  read by the project's own tool.
- **Correction found this lane:** the brief's "re-extract with --compression
  none" is wrong as a command line — there is no `--compression` flag.
  Verified against Kiloutre/TKMovesets `docs/headless.md` AT v1.1 (the pinned
  exe version): `build-disk-movesets-t7 | TKDATA_BIN DIRECTORY [CODE,...|all]
  [CODEC]`, "Codec default `lz4`", "Codecs: `none`, `lz4`, `lzma`,
  `compact-zstd`". The correct invocation is a 4th POSITIONAL argument:
  `build-disk-movesets-t7 gamefiles\tkdata.bin out kin none`.
  `--compression none` would fail with exit 2 (usage error). The prepared
  workflows use the positional `none` and verify in-run (TKM2 magic +
  compression byte 0x60 == 0 + sha256 + size).
- **Fighter codes:** TKMovesets2 keeps no hardcoded code table — codes come
  from tkdata.bin itself (`mothead\bin\<code>mot.bin`,
  `T7DiskMoveset.cpp` `Characters()`). `kin` (King) is proven. `bry` (Bryan)
  is expected but UNVERIFIED; `hei`, `jin`, `yos` are candidates in the same
  form. The prepared fighter workflow IS the verification: one headless JSON
  entry per code, a wrong code fails only its own entry, upload runs anyway
  (`if: always()`). Do not guess a replacement code from a failed run — read
  the run log / tkdata TOC first.

## 2. Paired-throw verification (King)

Verified from the real `.tkmvst` record (`docs/decode/T7-RECEIVER-FIX.md`,
`docs/decode/STATUS.md`), NOT re-derived in this lane (no readable
`.tkmvst` in hand):

- 4 of 10 throw clips PASS validation: 1785/common_709 (40f), 1787/rotsm_534
  (40f), 2125/rotsm_574 (130f), 2135/rotsm_588 (226f). 6 pending: 578, 590,
  592, 594, 716, 718 (frame counts already match from the `.tkmvst` side;
  per-clip validate runs were blocked by degraded GitHub access, not a decode
  problem).
- Mechanism is TWO-STAGE: grab (1785/1787, connect window [12,14]) → victim
  into HOLD move 554 (30f `nab6_guard`, anim_id 33363, breakable to 1423) →
  thrower's throw motion selects the specific `_y` receiver from its standing
  slot. Move 554 is the hold, NOT the final receiver. No move in the 2,787-move
  graph cancels into any `_y` move.
- Full pair table transcribed to `lane3-push-ready/bannon-paired-throws-king-t7.json`:
  8 standing/air pairs, 4 crouch pairs, 11 ground pairs, 4 thrower-only
  extras, 2 grabs + F-variants, hold 554, break windows (front [1,15], side
  [1,10]; escapes 2127/2133/237/239/235), damage via extra property 33307
  (2135 = 40, 2274 = 30, corrected from move-field 0).
- Receiver rebuild owed: all 22 P1/P2 receivers + bank thrower 588, with the
  joint sandwich (U/V/W verbatim in the JSON + T7-RECEIVER-FIX.md §3c; joint
  fit cost 1.26e-11, hold-out 588 max 0.1278°). Audit: 18/22 need the flip,
  4 unclear (ground face-down 692/696/700/704), 0 OK; 575/579 both need it.
  Receivers `rotsm_575`/`rotsm_579` are NOT on western-heart main (verified
  against the b2a52a tree: `game/assets/anim/t7/king/throws/` holds exactly
  the 10 throw clips + index.json). Rebuild needs: readable (uncompressed)
  King `.tkmvst` + game-sampler chain (`TekkenGame-Win64-Shipping.exe`,
  sha256 `7f2b6872…`) + `decode-sampler.py`/`pull-clips.py` updated to the
  joint sandwich. NOT doable from JSONs alone (they carry final quats, not
  raw c8 triples).
- Unsolved flags carried: Spine approximate (53.5° max / 17.8° mean on 574);
  Chest/toes source-real frozen (T7 format has 23 channels, NO Chest/toe
  channels — moving Chest needs an owner retargeting decision); runtime yaw
  question open; ground face-down 4 unclear.

## 3. The 383 partial clips — fixability verdict

Source: Bannon `assets/moves/ik/tekken/` (README + manifest.json, 2026-11-19,
K3 lane, PR #136 open unmerged). Counts re-confirmed this lane: 383 total =
230 T3 + 96 T7 + 54 DW + 3 MADE. Coverage FULL 0 / PARTIAL 383 / GAP 0 clips;
86 registry moves with no clip at all (82 T8-data-only + 4 WH originals
unauthored: Pantera Claw Driver, Pantera's Hunt, Storm Shadow's Lesson,
Whiteout). Registry moves in scope 1,002; with clip 916; without clip 86.
`bannon_library_mapping.mapped_named_moves`: 0. Per-clip class: strike 136,
throw 27, special 2, signature 4, mixed 63, none 151.

### (a) Receiver halves — NOT fixable from the 383 as they stand

- Bannon has ZERO of the 10 King throw `_n` clips and ZERO `_y` receivers.
  The 96 T7 Bannon clips (from `moves.pack.json`, 166 moves → 96 clips) do
  not include rotsm_534/574/578/588/590/592/594/716/718 or common_709
  (checked against the manifest files list). The throw clips live only in
  western-heart `game/assets/anim/t7/king/throws/`.
- What IS needed, in order: (1) convert the 10 WH throw clips with
  `tools/tekken/whanim_to_bannon.py` (needs a git-authed machine with both
  repos checked out — blocked in this lane: no clone; see §5); (2) rebuild
  the `_y` receivers with the joint sandwich (needs uncompressed King
  `.tkmvst` + sampler — §1/§2); (3) a registry lane linking clips to named
  Bannon library moves (K3 deliberately did NOT do this: Tekken-side move
  names are generated, e.g. "PANTERA 1 (T3 king r110)" — matching a Tekken
  jab to a specific library name would be guessing).
- DW note: filename pairs `T5DW_PANTERA_ikdv_36_nage_f/_y`,
  `b_nage_f/_y`, `ppp_nage_f/_y` exist as converted Bannon clips, but their
  thrower/receiver roles are UNVERIFIED from any source read in this lane.
  Do NOT use them as pairs until the DW bank confirms roles. (K3's "no
  receiver clip exists in the batch" refers to paired/reaction data, not to
  these filenames.)

### (b) Root travel — fixable, but it is a deliberate v1 design decision, not a bug

- The converter (`tools/tekken/whanim_to_bannon.py`) drops root x/z BY DESIGN:
  "Root horizontal travel is DROPPED in v1 — in Bannon the fighter root moves
  by locomotion + physics, not by the clip (same rule as AKI)." Pelvis height
  IS kept (delta from source root rest height + Bannon pelvis rest 0.90 m).
- The source data is NOT missing: western-heart clips carry full `root_t`
  (verified: `game/assets/anim/t7/king/throws/common_709.json` on main has
  full `root_t` + `root_motion_fwd_m`). So root travel is recoverable per clip
  from the WH source pack root track — no new extraction needed for the data.
- What a fix requires: (1) an owner/coordinator decision — clip-driven root
  travel changes how all 383 clips play (locomotion vs clip-driven root) and
  touches the engine clip pipeline (`studioApplyClipPose`); (2) a converter
  v2 (e.g. `--keep-root-travel`, default off to preserve v1 behaviour) +
  re-run over all 383 sources + re-verification (gates T1–T5); (3) a
  git-authed machine to run it. This lane did NOT land a converter change:
  editing `whanim_to_bannon.py` through the MCP would mean resubmitting the
  whole file from a truncated read — too error-prone without a checkout — and
  the behaviour change needs the owner decision first. It matters most for
  paired throws (thrower travels ~1.19 m by f30).

### (c) The 86 clipless registry moves — unfixable from Tekken data

- 82 are T8-data-only (western-heart holds clip-MAPS only, no T8 clip data
  packs) — need T8 extraction, a separate workstream.
- 4 are WH originals with animation not authored (Pantera Claw Driver,
  Pantera's Hunt, Storm Shadow's Lesson, Whiteout) — need authoring, not
  decoding.

## 4. PRs prepared (NOT opened — approval expired)

All contents in `lane3-push-ready/` in this directory, ready to push:

- WESTERN-HEART PR (branch `lane-c/t7-extract-none`, base main @ fd055e8b):
  1. `.github/workflows/lane-c-t7-extract-king.yml` — modified: positional
     `none` codec, artifact renamed `king-tkmvst-none`, in-run verification
     step (TKM2 magic + compression byte 0x60 == 0 + sha256/size), header
     comment corrected. Blob SHA on main at read time: 770684d4…
  2. `.github/workflows/lane-c-t7-extract-bry-hei-jin-yos.yml` — new:
     candidate codes `bry,hei,jin,yos` + `none`, `if: always()` upload,
     artifact `t7-tkmvst-bry-hei-jin-yos-none`.
  3. `docs/decode/T7-EXTRACTION-NONE.md` — new: the LZ4 → `none` record,
     the `--compression` correction, code-verification plan, durable-home
     note. Opening this PR triggers BOTH extraction runs (PR event is the
     working trigger). Merge after both runs report success.
- BANNON PR (branch `lane-3/tekken-king-paired-throws`, base main @ 158a088f):
  1. `assets/moves/ik/tekken/paired-throws-king-t7.json` — new: the full King
     pair table (8 + 4 + 11 pairs, grabs, hold 554, break windows, damage,
     validation 4/10, rebuild spec with joint sandwich, honest
     `mapped_named_bannon_moves: 0`). No existing files touched.

## 5. Exact blockers + exact files needed

1. GitHub write approval expired — `create_branch` for
   `lane-c/t7-extract-none` (western-heart) timed out unanswered
   (approval_id connector-attempt-ee66cacd41d47040df85078b03eba75a0b76390d87d1e3b6100e8b249e30045a).
   No retry without the user asking. Parent: request a fresh approval for
   the two branches + PRs + merges, or push the prepared files from
   `lane3-push-ready/` on a git-authed machine.
2. King `.tkmvst` download — no artifact-download tool in the GitHub MCP
   connector; `gh` CLI not logged in. File needed: artifact `king-tkmvst`
   from run 44858568891 (or the new `king-tkmvst-none` artifact once the
   prepared PR runs). Alternative: a workflow run that downloads it
   (`gh run download 44858568891 -n king-tkmvst`) + `recompress … none`
   (offline headless command, verified in docs).
3. Receiver rebuild + throw-clip conversion — need a git-authed machine with
   checkouts of western-heart (main @ fd055e8b) and Bannon (main @ 158a088f),
   the uncompressed King `.tkmvst`, the game exe
   (`TekkenGame-Win64-Shipping.exe`, sha256 `7f2b6872…`), and the lane
   workdir decode scripts (`decode-sampler.py`, `pull-clips.py` — NOT on
   main; last known in `~/workspace/_t7throw-fix-20261121/` lane workdirs,
   which this lane did not verify still exist). This lane did not clone:
   an earlier exec result in this workspace failed an execution-risk check
   on a clone directory, and cloning was not attempted again.
4. Durable home for `.tkmvst` files — owner/coordinator decision, still
   open: new release vs alongside `tekken7-gamefiles-v1`. Do not treat run
   artifacts as landed.
5. Root-travel v2 + library-move mapping — owner/coordinator decisions (see
   §3b/§3a). Converter edit + 383-clip re-run needs a checked-out machine.

## 6. What was verified in this lane (sources)

- PR #1803 MERGED (not open); King workflow file read from main @ fd055e8b;
  `tkmvst_to_wh.py` LZ4 refusal read in full (comp == 1 raises TkmvstError);
  v1.1 `headless.md` codec + `build-disk-movesets-t7` row (CODEC positional);
  `T7DiskMoveset.cpp` `Characters()` (codes from tkdata TOC, no hardcoded
  table); `T7-RECEIVER-FIX.md` full text; `STATUS.md`; Bannon Tekken README +
  manifest.json (383 counts, 0 mapped, 86 clipless); K3 doc (383/0 table,
  deliberate non-mapping); `whanim_to_bannon.py` root-drop docstring;
  `common_709.json` on main (full `root_t` present); b2a52a tree (10 throw
  clips only, no 575/579); Bannon main head 158a088f (merge PR #413,
  2026-11-23 01:20 UTC); western-heart main head fd055e8b (merge PR #1846,
  2026-11-22 22:43 UTC).
- NOT verified: artifact still downloadable (no tool); fighter codes
  bry/hei/jin/yos (run is the test); DW `_f`/`_y` roles; lane workdir
  scripts still present on disk.
