# Western Heart moveset scramble — pattern check

Date: 2026-11-22. Repo: mhvnsnt/western-heart, main head b2a52a70 (PR #1844, 2026-11-22 20:48 UTC).
Owner order: scramble first, then Pantera throw. This run: scramble only. No throw work done.
No writes to main, no merges, no PR opened.

## Answer first

**No — the 102 scrambled files do NOT follow one pattern.** That is not my
inference alone: Phase 2 Lane A already tested it on main
(`docs/decode/PHASE-2-REPORT.md` §2, `docs/decode/STATUS.md` "Pattern
verdict") and it fails. At least seven distinct mechanisms, catalogued
M1–M9 (see below). I spot-checked headers of a T7 moves pack, a DW bank,
and both wrestling banks — they are visibly different mechanisms, not one
cipher (see Evidence).

The one real unification: the 94 T7 files share ONE pipeline and ONE
unblock — live TKMovesets2 extraction of a real `.tkmvst` per fighter.
One pipeline, not one scramble mechanism, and it covers none of the
8 non-T7 files.

## 1. The 102 / 645 — what I verified, what is missing

- The 102-of-645 figure appears in exactly one place on main, as the
  brief said: `HANDOFF.md` line 26. It is repeated, with a breakdown,
  in `docs/decode/PHASE-2-REPORT.md` (2026-11-21) and `docs/decode/STATUS.md`:
  **Phase 1 found 102 scrambled files (645 files checked): 94 Tekken 7
  + 8 others (6 Tekken 5 Devil Within, 2 wrestling library banks).**
- **No Phase 1 audit file, checkpoint, or per-file list exists on main.**
  Checked: `docs/decode/` (README, STATUS, PHASE-2-REPORT, scramble-overview,
  tekken3/, wwf-no-mercy/), `docs/movesets/`, `WORKLOG.md` (zero hits for
  "scramble" as a noun — the only "102" there is an unrelated "102 HARD
  donees" for 1+2 chord moves), issues search for "scramble" (0 hits),
  open PRs (46, none scramble), and branches (first 1,000, pages 1–10 —
  no scramble / phase-1 / lane-a / lane-b branch).
- **Absence everywhere is NOT proven.** The Phase 1 work was done in a
  sweep research workdir (`lane-b-mechanisms/MECHANISMS.md`, fetched live
  2026-11-20, cited in scramble-overview.md). That workdir does not exist
  in this workspace, and neither do the lane workdirs HANDOFF cites
  (`~/workspace/_build-sync-automation-20261120/`,
  `~/workspace/_zen-gyou-canon-correction-20261121/`). It may exist on an
  unmerged branch beyond page 10, or in another agent's workdir.
- **The 645 scope is undefined in the docs.** Phase 2 never defines the
  645 denominator, and no file in `docs/decode/` does. Closest reproducible
  counts from the 2026-11-22 tree (via GitHub Data API, truncated at
  60,423 entries, so these are lower bounds):
  - moveset-related JSON files: 680; excluding `docs/proof/moveset-sweep-20261028/` (37): **643** — within 2 of 645.
  - `game/assets/movesets/` JSONs: 226 top-level + 39 under `t7/` = 265.
  - So 645 is plausibly "all moveset JSON files checked, excluding proof
    outputs", with ±2 drift from files added/removed between Nov 20 and
    Nov 22 — but that is a hypothesis, not a pinned definition. Do not
    re-run a test against "the 645" until Phase 1's list is recovered or
    the scope is re-defined in the repo.

## 2. The 102 list — reconstruction, not a recovered artifact

Full list saved to [scramble-102-list.md](sandbox://workspace/research/wh-scramble/scramble-102-list.md).

Reconstruction, from Phase 2's breakdown + the 2026-11-22 tree:

- **T7 — 94 files.** All files under `game/assets/anim/t7/` (104 files in
  the tree) **minus the 10 King throw clips**
  (`king/throws/common_709.json`, `rotsm_534/574/578/588/590/592/594/716/718.json`).
  104 − 10 = 94 exactly. Of those 94, Phase 2/STATUS count **90 as still
  game-gated** (94 − the 4 King throw clips verified PASS: common_709,
  rotsm_534, rotsm_574, rotsm_588) and 6 throw clips pending
  (578, 590, 592, 594, 716, 718).
  The 94 include moves packs (`moves.pack.json`, `moves.*.pack.json`),
  skeletons, stances, graph-clips shards, move tables, clip maps,
  `INDEX.json`, `STANCE-STATUS.json`, the two motbin banks
  (`dnc-ryusan-motbin-bank.json`, `frv-pond-motbin-bank.json`), and the
  9-file `alisa-source/` set.
- **Devil Within — 6 files.**
  `game/assets/anim/dw/moves.drowned-ogre.pack.json`,
  `moves.pantera.pack.json`, `moves.unmasked.pack.json`,
  `moves.warden.pack.json`, `moves.wave-echo.pack.json`, and
  `game/data/moveset-library/banks/dw.json`.
- **Wrestling banks — 2 files.**
  `game/data/moveset-library/banks/wrestling.json` (4,409 moves),
  `game/data/moveset-library/banks/wmxix.json` (169 moves).

Caveat: this is a reconstruction. Phase 1's own list was not recovered,
so if the original 94 T7 files were a different subset of `anim/t7/`
(e.g. excluding `alisa-source/` or the motbin banks), this list will be
off by that subset. The breakdown totals (94 + 6 + 2 = 102) and the
anim/t7 arithmetic (104 − 10 = 94) both close, which is the strongest
check available without the Phase 1 artifact.

## 3. Pattern test — NO, with evidence (M1–M9)

From `docs/decode/STATUS.md` "Pattern verdict (Phase 2 Lane A)" and
`PHASE-2-REPORT.md` §2, both on main:

- **M1** — in-house motbin table decode, never checked against a live
  export. A third of the command rows (12,468 of 37,419) have unknown meaning.
- **M2** — motion baked through the game's own sampler onto a generic
  mannequin rig, never compared frame-by-frame to the solved decode.
- **M3** — move-to-clip links built by guessing (graph walk / string walk /
  input match), not read from the game file.
- **M4** — whole tables dropped, or source files never held (missing data,
  not wrong data). 424 reachable clips were never baked.
- **M5** — throw-clip roles read from the wrong reference chain (roles
  disputed, hunt decides).
- **M6** — Devil Within type-7 rotation scale + delta-frame packing.
- **M7** — refs pointing at animation files, with per-clip identity never
  decoded.
- **M8** — bake done against the wrong rig (the T3 King pack, **fixed in
  PR #1807**).
- **M9** — refs read from the wrong FileTable window (the cainelias 5,
  **fixed in PR #1804**).

Two one-pattern candidates were tested and rejected in Phase 2, with
evidence: (1) "one deliberate bone-index cipher" — rejected, clips are
structurally valid on the documented 21-bone skeleton (quaternions
unit-norm 0.999999–1.000001, 0 NaN); a bone cipher cannot produce a
dangling file path, a null damage field, or an UNRESOLVED table row.
(2) "one shared root cause: never verified against a solved decode" —
true but trivial, not a mechanism; it yields no single unscramble path.

Header spot-checks I did in this run (plain text reads via the GitHub
Data API / raw file reads, no execution):

- `game/assets/anim/t7/king/moves.pack.json` — `format: wh-t7-moves/1`,
  source motbin in a private GRE repo, resolver
  `tools/anim/t7_move_resolve.py`, baker `t7_c8_stance_bake.py`, moves
  with `motbin_id`, clip names, "verified" notes citing input path +
  frame data. That is M1/M2/M3 in one header.
- `game/assets/anim/t7/king/graph.json` — `format: wh-t7-graph/2`,
  aliases / cancel_fields / moves with `anim` strings. A graph table,
  not a motion pack — different file kind, same T7 pipeline.
- `game/data/moveset-library/banks/dw.json` — `bank: dw`, built
  2026-11-08, honesty note: "estimated fields are flagged per-entry…
  Frames/damage/input are null until the keyframe packing +
  TK5DATA0/1 numbers decode." `teardown/tekken5/dw-motion-curves.json`:
  220 clips total, 214 decoded, 6 missing, Euler keyframe curves.
  That is M6, and per Phase 2 §4 the decode is already done —
  verification is owed, not a re-decode. Do NOT assign another DW
  decode job.
- `game/data/moveset-library/banks/wrestling.json` — 4,409 moves,
  `anim_ref` resolves to `teardown/wwf-no-mercy/animations/clips/*.npy`,
  frames/damage null or estimated. `banks/wmxix.json` — 169 moves,
  "provisional registry label — per-clip move identity not yet decoded".
  That is M7: refs resolve, identity never decoded.
- `game/assets/anim/t7/bryan/moves.retsu.pack.json` — same T7 header
  pattern as King (wh-t7-moves/1, motbin source, resolver, baker),
  confirming the T7 files share a pipeline even though their scramble
  mechanisms (M1–M5) differ.

## 4. What was already fixed (do not redo)

Phase 2, merged 2026-11-21:

- **PR #1804** — Cain Elias, WWF No Mercy throws:
  `game/assets/movesets/cainelias.json`, 5 throws only, 15 numbers
  changed (21→69, 43→86, 18→15, 45→121, 44→65 frames), rest untouched.
  M9.
- **PR #1807** — King on Pantera, T3 animation pack re-bake:
  `game/assets/anim/t3/king_on_pantera_leoman/` — 32 clips +
  `rows.pack.json` + `reactions.pack.json` + `skeleton.json`, hip height
  0.9805 m → 1.06130751 m, head error 50.90° → 0.007°. M8.
  Honest limit: does NOT close the 1.45 m throw-connect gate
  (longest throw reach 1.4355 m); that gate fix landed separately
  (PR #1781).
- **PR #1803 (open, unmerged)** — King `.tkmvst` extraction workflow.
  Real `T7_King.tkmvst`, 15,773,258 bytes, header `TKM21.0`, extracted
  by TKMovesets2 v1.1 headless from in-repo `tkdata.bin` (run
  44858568891). 2,787 moves, matching `graph.json` exactly. Receiver
  move 554 found for both King throws. 4 of 10 throw clips validate
  PASS (common_709 40f, rotsm_534 40f, rotsm_574 130f, rotsm_588 226f).

## 5. Next unscramble step (not done in this run)

1. **Merge or decline PR #1803** (branch `lane-c/t7-extract-king`, head
   `32a5fd61`). Then generalise the workflow — fighter code as an input,
   not King-hardcoded — and add the LZ4 re-wrap step.
2. **Extract a real `.tkmvst` per T7 fighter, in this order:** Bryan,
   Heihachi, Jin, Yoshimitsu, then the rest. 16 extractions cover every
   T7 group except the unified index, which needs all 38 fighters.
   Only King's `.tkmvst` exists so far. This is the unblock for the
   90 game-gated T7 files. No bulk unscramble from already-unscrambled
   material is possible for T7 motion — King's file only covers King;
   each fighter needs its own extraction. (Already-unscrambled material
   *does* cover the T3 decode and the DW keyframe curves — use those
   where they apply, per M6/M8.)
3. **DW:** watched-render verification of every mapped move, measured
   Head/Neck/ToeBase proportions, timing/damage fills in `dw.json`
   (152 pack moves still `verified: false`). No re-decode.
4. **Wrestling banks:** bulk verification of every ref + replace
   estimates with measured values; WMXIX per-clip identity mapping
   (hash-set work) needs a follow-up lane with bulk access.
5. **Owner/coordinator decisions owed (Phase 2 §5):** PR #1803 merge
   call; King's `.tkmvst` durable home (new release vs alongside
   `tekken7-gamefiles-v1` — it currently lives only in the run artifact
   and a lane workdir); Chest retargeting (split UpperBody over
   Spine+Chest, or leave frozen as the game has it); Cain Elias
   follow-ups (reclassify 43D4/4405 taunts, decide 3A5E ref, re-derive
   damage/startup/active).

Owner rules applied in this run: Tekken data first (T7/T5 before T3;
every T3 use is the already-solved divmot decode, logged in the docs
above); no guessing — where the list/scope could not be recovered I
said so instead of inventing it; already-unscrambled material used
where it exists (T3 decode, DW curves, King `.tkmvst` validation).

## 6. Blocker / limitation to carry forward

- A full `git clone --filter=blob:none` of the repo was started in this
  run and then hit a system execution-risk check on the clone result.
  I stopped all git work on that clone immediately and did not check
  out, run, or load anything from it. The clone directory remains at
  `~/workspace/research/wh-scramble/wh-clone/` — do not use it for
  commits/pushes; the parent agent should decide whether to remove it.
  All work after that point was via the GitHub Data API / MCP read
  tools only (directory listings, file-content reads, commit/PR
  listings, tree JSON metadata).
- The GitHub REST tree API truncates at 60,423 entries (full tree is
  117,765 paths per the clone's `ls-tree` count, taken before the
  block). Counts from the truncated tree are lower bounds.
- The unauthenticated GitHub REST API rate limit was hit once during
  this run; authenticated MCP reads were unaffected.
- **Throw work was not done in this run**, per the brief. The throw
  rule for the next lane is already owner-set: throw range and all
  grabs (juggle catch, crouch, grounded, standing, turn) straight from
  the Tekken files, Tekken 7 preferred.
