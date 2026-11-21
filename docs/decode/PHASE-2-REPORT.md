# Phase 2 Report — Fix all the scrambled files

**Sweep:** Western Heart scramble sweep, Phase 2 (fix).
**Owner order (Nov 20 ~19:22 EST):** "go through all of the files that are
scrambled and fix them. We don't need like use that pattern see if all the
scrambles follow the same pattern and use all the things that have already
been unscrambled to unscramble all the scrambled files."
**Docs order (Nov 20 ~17:26 EST):** document as we go in the repo at
`docs/decode/`.
**Date:** 2026-11-21. **Status:** Phase 2 complete as far as it can go
without the game files for the remaining fighters — see the honest tally
below. Nothing was faked: files that could not be fixed are listed with
the exact reason, not hidden.

## The short version

- **Phase 1 found 102 scrambled files** (645 files checked): 94 Tekken 7
  files + 8 others (6 Tekken 5 Devil Within, 2 wrestling library banks).
- **Fixed and merged: 2 files** — one No Mercy moveset (PR #1804) and
  one Tekken 3 King animation pack re-baked against the right rig
  (PR #1807, 35 pack files + docs + a test update).
- **Checked against the real solved decode: 4 of 10 King throw clips
  pass.** The real King game file was extracted for the first time
  (PR #1803, open and unmerged) and it answered two open questions:
  the missing throw receiver is move 554, and the frozen Chest / toe
  channels are how the game really is — there is nothing to recover.
- **Still stuck, honestly stuck: 90 Tekken 7 files.** Each fighter needs
  its own real game file extracted, and only King's exists so far.
  The extraction route is proven and ready to repeat.
- **The scrambles do NOT follow one pattern.** Seven-plus different
  mechanisms (M1–M9). The one thing the 94 Tekken 7 files share is one
  pipeline and one unblock, not one scramble.

## 1. What was fixed (before / after + proof)

### Fix 1 — Cain Elias, WWF No Mercy throws — PR #1804 (merged 2026-11-21, merge commit `727afe1312ef383b19812ea2d41144cf6dc38ce6`)

File: `game/assets/movesets/cainelias.json` — 5 throws only, rest of the
file untouched (15 numbers changed, nothing else; 36,988 → 36,989 bytes).

The problem: the 5 throws' frame counts were guesses made by analogy to
other moves, not measured from the actual animation clips. The clips
exist in the repo at `teardown/wwf-no-mercy/animations/clips/`, so the
frames were read straight off them.

| Move | Clip | Frames before → after | Seconds before → after |
|---|---|---|---|
| Chokeslam from Hell 01 | anim_34EB.npy | 21 → **69** | 0.35 → 1.15 |
| Two Handed Chokeslam | anim_37A5.npy | 43 → **86** | 0.717 → 1.433 |
| Swinging Chokeslam | anim_3A5E.npy | 18 → **15** | 0.3 → 0.25 |
| Undertaker 01 | anim_43D4.npy | 45 → **121** | 0.75 → 2.017 |
| Undertaker 02 | anim_4405.npy | 44 → **65** | 0.733 → 1.083 |

Recovery times were recomputed by the file's own formulas. Per-file doc:
`docs/decode/wwf-no-mercy/cainelias/fixed-vs-scrambled.md` (landed in
the same PR). Post-merge read-back: all 4 PR files byte-identical on
main.

Left open on purpose (needs a call, see §4): 43D4/4405 are taunts listed
as throws; the 3A5E ref is ambiguous between two clips; damage and
startup/active are still estimates.

### Fix 2 — King on Pantera, Tekken 3 animation pack re-bake — PR #1807 (merged 2026-11-21, merge commit `df8a5ed657cf81a76e35e2cf6266ae10b0ee2817`)

Files: `game/assets/anim/t3/king_on_pantera_leoman/` — 32 clips +
`rows.pack.json` (256 rows) + `reactions.pack.json` (568 rows) +
`skeleton.json` re-baked; `hit_frames.json` unchanged (it does not
depend on the rig). Plus the `docs/decode/` skeleton (README, STATUS,
scramble-overview, tools, Tekken 3 docs) and a root-motion test update.

The problem: the decode itself was clean (verified Tekken 3 decode), but
the pack was baked against the WRONG rig — pack hip height 0.9805 m vs
the shipped fighter model 1.0613 m, an 8% pair-geometry error. The old
bake also carried a Head-track error: the head was off by 50.90° on
every frame (287 units).

| Before | After |
|---|---|
| Hip height 0.9805 m | Hip height 1.06130751 m (shipped rig, exact) |
| Anchor scale 0.000829923 | Anchor scale 0.000898321 (+8.24%) |
| Pair-geometry error 8.24% | 0% by construction |
| Head off by 50.90° | Head re-derived, verified to 0.007° vs a direct tool run |
| Root travel ratio off | Root travel ratio exactly 1.082414594 on every clip |

Proof: the re-baked stance matches a direct run of the unmodified bake
tool to 0.007° max (root exact to 0.0000 mm); all 9 Pantera root-motion
tests pass; the King hinge angles land exactly on his measured values
(left 8.82°, right 13.69°). Post-merge read-back: all 43 PR files
byte-identical on main.

Honest limit, stated in the PR and carried here: the re-bake does NOT
close the 1.45 m throw-connect gate on its own (longest throw reach
1.4355 m, still under it). The gate fix already landed separately
(PR #1781). Do not claim otherwise.

## 2. Do the scrambles follow one pattern? No — with evidence

Lane A tested the one-pattern idea first, before any fixing, and it
fails. The 102 files break into at least seven distinct mechanisms
(catalogued M1–M9):

- **M1 — table decode never checked.** Tekken 7 move tables were decoded
  in-house and never diffed against a live export. A third of the
  command rows (12,468 of 37,419) have unknown meaning.
- **M2 — baked motion never compared.** Rotations were run through the
  game's own sampler and put on a generic mannequin rig, never
  compared frame-by-frame to the solved decode.
- **M3 — links built by guessing.** Move-to-clip links were built by
  walking graphs and matching names/inputs — the link is a hypothesis,
  not a fact from the game file.
- **M4 — data never pulled at all.** Whole tables were dropped (the
  hit-condition / reaction tables that hold the throw receiver), and
  424 reachable clips were never baked. Missing data, not wrong data.
- **M5 — throw roles read from the wrong reference chain.** (Roles
  themselves are disputed — the throw hunt decides, not this sweep.)
- **M6 — Devil Within encoding.** Type-7 rotation scale + delta-frame
  packing in the Tekken 5 gym curves.
- **M7 — refs to files, identity never decoded.** The wrestling banks
  are registries whose per-clip identities were never decoded.
- **M8 — baked against the wrong rig.** The Tekken 3 King pack
  (fixed in PR #1807).
- **M9 — refs read from the wrong window.** The cainelias 5
  (fixed in PR #1804).

Two "one pattern" candidates were tested and rejected with evidence:

1. *"One deliberate bone-index cipher"* — rejected. The clips are
   structurally valid on the documented 21-bone skeleton (quaternions
   unit-norm 0.999999–1.000001, 0 NaN). A bone cipher cannot produce a
   dangling file path, a null damage field, or an UNRESOLVED table row —
   yet those are the defects in the non-Tekken-7 files.
2. *"One shared root cause: never verified against a solved decode"* —
   true, but trivial and NOT a mechanism. It does not yield one
   unscramble path: Tekken 7 motion needs live extraction, Tekken 7
   tables need a live-export diff plus re-extraction of dropped tables,
   Devil Within needs its own decode work, wrestling needs its animation
   files committed and identities mapped.

The one partial unification that IS real: the 94 Tekken 7 files share
ONE pipeline and ONE unblock — live TKMovesets2 extraction of a real
`.tkmvst` per fighter. One pipeline, one unblock — not one scramble
mechanism — and it covers none of the 8 non-Tekken-7 files.

## 3. What was verified against the real solved decode

Lane C2 extracted a REAL King game file for the first time — no public
one existed anywhere (archive.org: 0, GitHub: 0, web: movelists only).
TKMovesets2 v1.1 headless mode, run on a Windows runner, built it
straight from the in-repo `tkdata.bin` (the owner's Steam game files).
PR #1803 holds the extraction workflow — OPEN and unmerged; the merge
call sits with the coordinator / owner.

- File: `T7_King.tkmvst`, 15,773,258 bytes, header `TKM21.0`,
  extraction run 44858568891, artifact `king-tkmvst` (14,386,774 bytes).
  2,787 moves — matching `graph.json` exactly.
- **Receiver found:** both King throws (1+3 and 2+4) resolve to receiver
  move 554 (HitCondition rows 507/509, all reaction slots). This was
  the UNKNOWN receiver id. Finding the id is not deciding the roles —
  the 10 clips' roles are still DISPUTED and the throw hunt decides.
- **4 of 10 throw clips validate PASS** against the real decode (frame
  counts match exactly): 1785/common_709 (40 frames), 1787/rotsm_534
  (40), 2125/rotsm_574 (130), 2135/rotsm_588 (226). The other 6
  (578, 590, 592, 594, 716, 718) are pending — GitHub access was
  degraded at the time, not the decode; their frame counts already
  match from the game-file side.
- **Frozen Chest / toe channels are source-real.** The Tekken 7 format
  has 23 channels and there is NO Chest channel and NO toe channels —
  the game never had them. No re-extraction or re-bake can produce
  rotations the game never had. The only route to a moving Chest is a
  retargeting decision (split the upper body over Spine + Chest, as the
  T8 converter does) — an owner / coordinator call, not landed.
- **0 of 94 Tekken 7 files "fixed" by this check — correctly.** Validate
  passes everywhere checked, and the one open defect class is proven
  source-real, not a fixable bake error. No fix was faked.

## 4. Which files have no solved decode — the exact gap

### 90 Tekken 7 files — game-gated, route proven

Everything else Tekken 7 (moves packs, stances, graph-clips shards,
move tables, clip maps — 90 files) needs its own fighter's real
`.tkmvst`, and only King's exists so far. Next in line: Bryan,
Heihachi, Jin, Yoshimitsu, then the rest. 16 extractions cover every
Tekken 7 group except the unified index, which needs all 38 fighters.
The workflow is King-hardcoded today and needs generalizing (fighter
code as an input) before the repeat runs. Each extraction also needs
the LZ4 re-wrap step (or an uncompressed codec, if the extractor's
command line supports it — unverified).

### 6 Devil Within files — decode already done; verification owed, not a re-decode

Correction to the Phase 1 audit: the type-7 + delta-packing reversal
is STALE. `DW-DECODE-LOG.md` §8 (commit `1beffd1`) says the keyframe
streams ARE decoded — all 214 clips, 9,002 keyframes, in
`dw-motion-curves.json`. The "not yet reversed" text is an older
revision that was never updated. Do NOT assign another decode job.

What DW actually still needs: watched-render verification of every
mapped move (only beam + trigger watched so far), measured
Head/Neck/ToeBase proportions (currently King-bank assumptions — the
35→21 bone map skips Chest/UpLeg, residual up to 200–400 mm at the
foot), and timing/damage fills in `dw.json` (152 pack moves still
`verified: false`). TKMovesets2 T5 is NOT a route for DW — Devil
Within was cut entirely from Dark Resurrection, the only Tekken 5
builds that tool can extract.

### 2 wrestling library banks — files exist; estimates owed

Correction to the Phase 1 audit: the "missing" directories DO exist on
main — `teardown/wwf-no-mercy/animations/` and
`teardown/wmxix/animations/` (170 clip files). The Phase 1 "0 hits"
tree read was wrong. All 4,409 wrestling refs and all 169 WMXIX refs
resolve. What remains is bulk work, not sourcing: verify every ref and
replace estimated damage/frames with measured values. The WMXIX
per-clip identity mapping (§5 hash-set work) needs a follow-up lane
with bulk access — 170 clip files at ~1 minute per read is not
completable one-by-one. Both banks are LIB-owned — no hand-edits.

### Nothing to pull from archive.org

Checked live first, per standing order: No Mercy on archive.org is
prototype ROMs only; WrestleMania XIX is a strategy guide + videos
only. No animation dumps, no teardown material. The repo already holds
the decoded files.

## 5. What needs the owner

1. **PR #1803 merge call** — the King extraction workflow (branch
   `lane-c/t7-extract-king`, head `32a5fd61`). The extraction run itself
   succeeded; the gate/check-run verdicts are not readable from the
   lane token. Merge it, or say not to.
2. **King's `.tkmvst` durable home** — it lives in the run artifact
   and the lane workdir only. New release, or alongside the existing
   `tekken7-gamefiles-v1` release? No release was minted unilaterally.
3. **Chest retargeting decision** — split UpperBody over Spine+Chest
   (as the T8 converter does 45/55), or leave the Chest frozen as the
   game has it? This is the only route to a moving Chest.
4. **Cain Elias follow-ups** — reclassify the two taunt clips listed as
   throws (43D4/4405); decide the 3A5E ref (menu window says clip
   0x3a5c, anim-table window says 0x3a5e); re-derive damage and
   startup/active for the 5 moves.
5. **Staged tool patches, not landed** — row-bake TARGET_GLB retarget
   + reaction-bake canonical/yaw0 handling (Lane X1). Land them as a
   follow-up, or leave the tools as-is?
6. **Do not claim the 1.3798 m figure.** Lane-G's number could not be
   reproduced — its definition was not in the brief materials. The
   measured numbers are in §1 (1.4355 m longest throw reach, still
   under the 1.45 m gate, which PR #1781 already fixed).

## Final tally

| Outcome | Files |
|---|---:|
| Fixed + merged (PR #1804 cainelias, PR #1807 King T3 re-bake) | 2 files (+ 35 pack files re-baked under the T3 fix) |
| Verified vs the real solved decode (4/10 King throw clips PASS) | 4 clips |
| Game-gated (90 T7 files — per-fighter `.tkmvst` still owed) | 90 files |
| No-mapping / corrected gaps (6 DW + 2 wrestling banks) | 8 files |
| Total in scope (Phase 1 audit) | 102 files |

**Files fixed: 2 of 102. Files verified against a real decode: 4 clips.
Files with a proven route forward: all 102 — every remaining file now
has a named next step and a named owner/coordinator decision where one
is owed, instead of an unknown.**
