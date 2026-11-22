# STATUS — living status table

One row per fix. Every fix PR adds or updates one row here, plus its own
per-file doc. A file stays flagged here as unsolved until a PR lands its
decode with before/after proof.

| Game | Fighter / file | Mechanism | Solved? | Source | Files fixed / remaining | Fix PR |
|---|---|---|---|---|---|---|
| Tekken 3 | King on Pantera — `game/assets/anim/t3/king_on_pantera_leoman/` | Bake defect (decode clean, bake used the wrong rig: pack hip 0.9805 m vs shipped rig 1.0613 m, 8% pair-geometry error) + old-tool Head-track deviation (50.90°) | **Fixed** (this PR) | Verified T3 divmot decode + shipped `game/assets/models/pantera.glb` + `lab/tools/t3_motion_bake.py` | 32 clips + `rows.pack.json` (256 rows) + `reactions.pack.json` (568 rows) + `skeleton.json` re-baked; `hit_frames.json` unchanged (rig-independent) | #1807 |
| Tekken 7 | King throws (10 clips; common_709, rotsm_534, rotsm_574, rotsm_578, …) | Roles disputed — the throw hunt decides them, not this sweep. Do NOT re-label or re-wire until the hunt decides. The frozen Chest / toe channels are proven source-real (see below), not a bake error. | **Verified 4/10** — see verification row below | Real King `.tkmvst` + `tools/anim/tkmovesets2/tkmvst_to_wh.py` | 4 clips validate PASS; 6 pending; 0 fixed / 10 disputed | #1803 open |
| Virtua Fighter 5 | Motion (all) | Motion not decoded | **Unsolved** | — | 0 fixed | PR #713 open |
| Tekken Tag 2 | motbin motion | MOTA offsets present, motion not decoded | **Unsolved** | — | 0 fixed | — |
| WWF No Mercy | Cain Elias — `game/assets/movesets/cainelias.json` (5 throws only) | Frames were analogy estimates, not measured from the clips | **Fixed** | Measured clip values from `teardown/wwf-no-mercy/animations/` (manifest + moves-enriched DB) | 5 moves corrected (15 numbers, nothing else); rest of file unchanged | #1804 |
| Tekken 7 | King — real `.tkmvst` check (the 10 throw clips) | Clip frame counts checked against the real solved decode | **Verified 4/10** | Real King `.tkmvst` (extraction run 44858568891) + `tkmvst_to_wh.py validate` | 1785/common_709 (40 frames), 1787/rotsm_534 (40), 2125/rotsm_574 (130), 2135/rotsm_588 (226) — all PASS. 6 clips pending (578, 590, 592, 594, 716, 718). Receiver move 554 found for both throws (HitCondition rows 507/509). | #1803 open |
| Tekken 7 | All other T7 files (90 files: moves packs, stances, graph-clips shards, move tables, clip maps) | In-house decode never checked against the solved decode (mechanisms M1–M5) | **Game-gated — not fixed** | One real `.tkmvst` per fighter, still owed (Bryan, Heihachi, Jin, Yoshimitsu first, then the rest) | 0 fixed / 90 | — |
| Tekken 5 Devil Within | DW packs (5) + `banks/dw.json` | Keyframe streams ARE decoded (see correction below) — what is owed is watched-render verification, measured body proportions, and timing/damage fills, not another decode job | **Decode solved; verification owed** | `teardown/tekken5/dw-motion-curves.json` (214 clips, 9,002 keyframes) + `tools/gym_keyframes.py` | 0 fixed / 6 (152 pack moves still `verified: false`) | — |
| WWF / WWE | `game/data/moveset-library/banks/wrestling.json` (4,409 moves) + `banks/wmxix.json` (169 moves) | Animation files DO exist in the repo (see correction below) — what is owed is verifying every ref and replacing estimated numbers with measured ones | **Refs resolve; estimates owed** | `teardown/wwf-no-mercy/animations/` + `teardown/wmxix/animations/` (170 clip files) | 0 fixed / 2 | — |

## Notes

- The T3 King row is the first fix in this directory. The T3 decode itself
  (divmot banks + AnimDecodePose port) was already solved in-repo before
  this PR; this PR fixed the *bake* of that decode onto the wrong rig, plus
  a Head-track deviation carried by the old bake. See
  `tekken3/king-pantera/fixed-vs-scrambled.md` §2 and §4.
- Honest limit (carried from the fix PR): the re-bake narrows the 8%
  pair-geometry error to ~0% by construction but does *not* close the
  1.45 m throw-connect gate on its own; the gate fix already landed
  (PR #1781). Do not claim otherwise.
- The No Mercy row (PR #1804) is the second fix in this directory: 5 throws
  corrected from analogy estimates to measured clip values — 34EB 21→69
  frames, 37A5 43→86, 3A5E 18→15, 43D4 45→121, 4405 44→65 (seconds and
  recovery recomputed by the file's own formulas). See
  `wwf-no-mercy/cainelias/fixed-vs-scrambled.md`.
- Correction to the T7 King throws row: an earlier version of this table
  said the clip roles were "swapped". That is not decided — roles are
  DISPUTED and the throw hunt decides them. Nothing in this sweep re-labels
  or re-wires the 10 clips.

## Pattern verdict (Phase 2 Lane A)

The 102 scrambled files do **not** follow one pattern. They are a stack of
at least seven distinct mechanisms, catalogued M1–M9:

- M1 — in-house motbin table decode, never checked against a live export.
- M2 — motion baked through the game's own sampler onto a generic
  mannequin rig, never compared frame-by-frame to the solved decode.
- M3 — move-to-clip links built by guessing (graph walk / string walk /
  input match), not read from the game file.
- M4 — whole tables dropped, or source files never held (missing data,
  not wrong data).
- M5 — throw-clip roles read from the wrong reference chain (roles
  disputed, hunt decides).
- M6 — Devil Within type-7 rotation scale + delta-frame packing.
- M7 — refs pointing at animation files, with per-clip identity never
  decoded.
- M8 — bake done against the wrong rig (the T3 King pack, fixed in
  PR #1807).
- M9 — refs read from the wrong FileTable window (the cainelias 5,
  fixed in PR #1804).

The one real unification: the 94 T7 files share ONE pipeline and ONE
unblock — live TKMovesets2 extraction of a real `.tkmvst` per fighter.
That is one pipeline, not one scramble mechanism, and it covers none of
the 8 non-T7 files.

## What is still owed (game-gated)

- **90 T7 files.** Each fighter needs its own real `.tkmvst` extraction
  (King's is done — see below). Next: Bryan, Heihachi, Jin, Yoshimitsu,
  then the rest. 16 extractions cover every T7 group except the unified
  index, which needs all 38 fighters. The extraction workflow is
  PR #1803 — OPEN and unmerged; the merge call sits with the coordinator
  / owner.
- **King's `.tkmvst` durable home is undecided.** The file lives in the
  extraction run's artifact and in the lane workdir only. No release was
  minted for it — that decision belongs to the coordinator / owner.
- **6 of 10 King throw-clip checks pending** (578, 590, 592, 594, 716,
  718). Their frame counts already match from the `.tkmvst` side; the
  per-clip validate runs were blocked by degraded GitHub access at the
  time, not by a decode problem.

## What the real King `.tkmvst` proved (Lane C2)

- The file exists: `T7_King.tkmvst`, 15,773,258 bytes, header `TKM21.0`,
  extracted by TKMovesets2 v1.1 headless from the in-repo `tkdata.bin`
  (run 44858568891). 2,787 moves — matching `graph.json` exactly.
- **Receiver found:** both King throws (1+3 and 2+4) resolve to receiver
  move 554 (HitCondition rows 507/509, all reaction slots). This fills
  the UNKNOWN receiver id. Roles of the 10 clips are still DISPUTED —
  finding the receiver id is not deciding the roles.
- **Frozen Chest / toes are source-real, not a bake error.** The T7
  format has 23 channels and there is NO Chest channel and NO toe
  channels — the game never had them, so no re-extraction or re-bake
  can produce them. The only route to a moving Chest is a retargeting
  decision (split the upper body over Spine + Chest, as the T8
  converter does) — an owner / coordinator call, not landed.
- **4 of 10 throw clips validate PASS** against the real decode
  (frame counts match exactly). No clip-content fix was owed from
  validate alone, so none was faked.

## Corrections to the Phase 1 audit

- **Devil Within is NOT an unreversed decode.** `DW-DECODE-LOG.md` §8
  (correction, commit `1beffd1`) says the keyframe streams ARE decoded —
  all 214 clips in `dw-motion-curves.json`. The "not yet reversed" text
  in §16 is an older revision that was never updated. What DW still
  needs: watched-render verification of every mapped move (only beam +
  trigger watched so far), measured Head/Neck/ToeBase proportions
  (currently King-bank assumptions), and timing/damage fills in
  `dw.json`. Do NOT assign another type-7/packing decode job.
  TKMovesets2 T5 is NOT a route for DW — Devil Within was cut entirely
  from Dark Resurrection, the only T5 builds that tool can extract.
- **The WWF/WWE animation directories DO exist.** `teardown/wwf-no-mercy/animations/`
  (FORMAT.md, MOVE-ANIM-MAP.md, clips/, manifest.json) and
  `teardown/wmxix/animations/` (170 clip files) are on main. The Phase 1
  "0 hits in the tree" read was wrong (truncated tree). All 4,409
  wrestling refs and all 169 WMXIX refs resolve. The remaining work is
  verification + replacing estimates with measured values, not sourcing.
  WMXIX per-clip identity mapping (§5 hash-set work) needs a follow-up
  lane with bulk access — 170 clip files at ~1 minute per read is not
  completable one-by-one.

## Open follow-ups

- Cain Elias follow-ups (from PR #1804): reclassify the two taunt clips
  listed as throws (43D4/4405); decide the 3A5E ref (menu window says
  clip 0x3a5c, anim-table window says 0x3a5e); re-derive damage and
  startup/active for the 5 moves.
- Staged tool patches NOT landed (deliberate non-change, decision owed):
  row-bake TARGET_GLB retarget + reaction-bake canonical/yaw0 handling
  (Lane X1).
- Lane-G 1.3798 m figure could NOT be reproduced — its definition was
  not in the brief materials. Do not claim it.
- Chest retargeting decision (split UpperBody over Spine+Chest) is an
  owner / coordinator call, not landed.
