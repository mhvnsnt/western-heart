# MEGAMI JUN-BANK SCALE FIX — 2026-11-04

Owner flag (2026-11-04 18:06 CST): in both Jun-bank proof videos (PR #1558,
PR #1561) Megami renders tiny (~half height), dark and crumpled while her Jun
bank clips play. Pantera's frozen pose in those videos is a capture-harness
artifact (bank lanes drove P1 only) — not a regression. Megami's crumple is
real and Jun-bank-specific: the roster-pass video (same model, unbanked,
generic fallback) shows her at ~85% of Pantera's height with normal
proportions, and Menajerii + Roger bank renders at normal size.

## Root cause (measured, leads eliminated in order)

Measurement unit throughout: skeleton height = Head world Y − lowest bone
world Y, taken (1) by FK of the baked bank JSONs on the bank skeleton,
(2) through the game's own `retargetT3Clips` run offline in node on the real
GLBs, and (3) in-game under the roster harness (identity-gated, deterministic
stepping). Pantera control in-game: span 1.60 m, hips 0.981.

1. **Bank skeleton scale — eliminated.** `jun/skeleton.json` and
   `roger/skeleton.json` are byte-identical in joints and `root_rest_y`
   (1.15). Nothing to differ.
2. **Megami's model/rig — eliminated.** Her no-outfit GLB and Menajerii's
   GLB carry the same 52 joints at the same rest positions (Hips y 0.95,
   Head y 1.48). Jun clips retargeted onto Menajerii's rig produce
   sample-for-sample identical spans as on Megami's. In-browser swap
   (Megami served Roger bank data under the jun bank name): idle span
   1.38 m — she stands tall on Roger data. The defect is in the Jun bank
   clip data itself.
3. **The clips as baked fold mid-play.** Shipped-bank in-game measurement
   reproduces the owner's flag exactly: idle span med 0.91 m, min 0.57 m
   (a floating folded ball), strikes 0.90–0.94 m. Mannequin FK of the
   shipped JSONs shows where: the stance's tail collapses (in-game
   0.55 m), the grab rides folded (FK med 0.85 m), the medium sags for its
   whole back half (FK med 1.07 m), walk_back collapses (FK med 1.00 m).
4. **Why the bake produced folds.** `tools/anim/ttt2_bank_bake.py` poses
   decoded 0x64 frames through `pose_synth`, whose '64' convention is a
   half-angle euler map (game local = ZXY euler of the stored triple / 2).
   In that convention the euler *branch* is physical: adding ±2π to a
   stored component rotates the joint by π. The bake's
   `unwrap_rotations` re-branches the decoded series against a seed, and
   the plausibility gate that arbitrates forward- vs backward-anchored
   chains checks only upright start, floor contact and relative joint
   jumps — it never looks at whether the pose stays anatomically coherent
   mid-clip. The Jun-family clips sit where the shipped chains flip
   branches and fold; the Roger-bank clips sit in a branch-stable region
   of the same pipeline, which is why Menajerii was unaffected.

## The fix (this PR)

Four clips re-baked from the **same source entries** — no frames added,
removed or altered, FK self-check 0.000000 m each — with the representative
chain that measures coherent for that clip, selected by whole-clip FK span
profile plus an anatomical-coherence sweep (feet-inversion / head-fold /
span-outside-range counts) and stick-figure inspection. Each replaced file
carries a `bake_note` recording its chain.

| slot | source (unchanged) | shipped chain | shipped FK med/min | fixed chain | fixed FK med/min |
|---|---|---|---|---|---|
| t3_neutral | amju_kamae_test, Jun bank-1 idx 139 | forward | 1.32 / 0.82 (in-game min 0.55) | backward | 1.32 / 0.96 |
| t3_grab | Tco_ntukami, Jun bank-1 idx 126 | backward (gate fallback) | 0.78 / 0.42 | forward | 1.44 / 0.27 |
| t3_medium | amju_lk, Unknown bank-1 idx 234 | forward | 1.07 / 0.98 | raw decoded frames | 1.46 / 1.35 |
| t3_walk_back | ygco_bwalk00, shared bank-2 idx 40 | shipped bake | 1.00 / 0.24 | raw decoded frames | 1.34 / 0.35 |

**t3_light audited and kept as shipped.** Its low segment (frames ~34–54)
is a genuine deep-leaning palm thrust — stick figures show a coherent
bowing strike with feet planted. The raw-chain alternative inverts the
legs for 6 frames (feet above hips +1.0 m), which is worse; the shipped
forward chain is the correct reading of this clip.

Unchanged: t3_heavy, t3_backdash, t3_crouch_hold, t3_sidestep_a, the three
jump clips, skeleton.json, all wiring, and every other bank. The Roger
bank (control) is byte-untouched — including its own copy of the shared
walk_back clip.

## Verification

- Retarget bench (game code, Megami's rig): stance samples
  1.04 0.84 0.86 0.98 1.02 1.06 1.14 1.23 1.01 0.80 1.04 (shipped:
  …0.57 0.55…); grab 0.86–1.21 throughout (shipped: 0.60–0.92, folded).
- In-game (roster harness standard, shrine, vs Pantera): idle span med
  0.95 m / min 0.86 m (shipped bank: med 0.91 / min 0.57); strike '3' med
  1.18 m; grapple med 1.00 m. Jun's kamae is a genuinely deep stance
  (mannequin head tops at 1.51 vs Roger's 1.66) — she now reads as a low
  fighting stance at full skeleton integrity instead of a folded ball.
- Proof video (roster harness, animated Pantera, standard camera):
  `docs/proof/2026-11-04/megami-bank-scale/megami-jun-bank-fixedscale-20261104.mp4`
  — idle + 1/2/3/4 + d/f+2 + grapples 1+3 and 2+4; frames unique; a
  mid-strike frame shows her upright at full height.
- Full measurements: `docs/proof/2026-11-04/megami-bank-scale/fix-measurements.json`.

## Remaining gaps (documented, not forced)

1. **Stance tail.** Frames ~60–96 of amju_kamae_test (its traveling
   segment; root XZ travel 1.39 m, stripped in-game) stay low under every
   unwrap branch — best tail min 0.96 m FK. This is the same
   non-upright-start family already awaiting the owner's normalization
   ruling (TTT2-BANKS handoff follow-up); this PR does not trim or alter
   the clip's frames.
2. **walk_back tail.** The clip's final frames fold under every branch
   (shared bank-2 clip ygco_bwalk00). The Roger bank's shipped copy of
   the same clip has the same property and is untouched here.
3. **Asuka's najn_jn2kam** — the Jun-family production kamae named by
   Asuka's own sKAM record (Jn_sKAM00_, her bank-1 idx 62) — could not be
   substituted for the test-named stance: her bank-1 table is not yet
   pinpointed (two candidate tables tie on shared-clip fingerprints,
   22/59 each, and neither is confirmable as hers; the idx-62 entry of
   one is provably Roger Jr.'s kjrg_kamae02). A future option if the
   table is pinpointed; nothing Asuka-sourced is shipped in this PR.
4. **Bake-gate follow-up (recommended, not in this PR):** the shipped
   bake's plausibility gate should gain a whole-clip anatomical-coherence
   check (feet-inversion / span profile) so future banks catch this fold
   class at bake time instead of at the owner's eyes.

## Method note

Diagnosis and verification ran on trees assembled from current main
(bank files verified byte-identical to main before and after the fix);
the proof video was shot in the same tree with this PR's four bank files
in place, under the roster-pass harness standard (opponent live and
animated). Zen and Chatur untouched.
