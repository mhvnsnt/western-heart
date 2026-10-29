# Community mocap: 55 generic bases wired — decision log (2026-10-24)

## What this PR does

Wires the 55 WIRED GENERIC BASE moves from the community-mocap first check
(`~/workspace/community-mocap/MAPPING.md`, source
`~/workspace/canon-moves-needing-made-animations-2026-10-24.md`, 188 canon /
WH-original moves) into the repo:

- `game/assets/anim/oss/community/` — 9 unique CMU FBX clips + this
  manifest (`wired-clips.json`, 55 entries keyed by move_id).
- `game/assets/movesets/` — 42 files gain additive `community_base` +
  `community_base_status` fields on every entry (moves + canon_moves)
  carrying a wired anim_ref. No anim_ref, damage, startup, limb, or any
  other field is changed. The edit is a text-level insertion after the
  anim_ref line; a parse check proves stripping the two added fields
  reproduces the original file exactly (validated on tobi, awapop, skull,
  ryuji-rock before push; the push driver re-validates all 42 and aborts
  on any mismatch).
- Docs: this log + the 105 no-base follow-up (separate file, same PR).

## Verification performed before push (not play verification)

- All 55 anim_refs found in live main movesets: canon_moves entry present
  for 55/55; moves entry present for 55/55 (54 under the canon input key,
  1 remapped: Ryuji Rock smackdown canon input 1+4, moves key P+K with
  source notation retained).
- Damage and canon startup_frames match the prior lane's mapping for
  55/55. Display inputs match for 55/55.
- 49 of 55 anim_refs appear under two moves keys (source notation +
  Tekken notation, e.g. S + 1+2, P+K + 1+4); both entries receive the
  fields, so the wiring holds whichever entry the loader plays.
- Unique-clip counts: 144_20 x28, 144_05 x8, 144_13 x6, 88_06 x3, 86_01 x3,
  90_05 x2, 144_28 x2, 144_09 x2, 86_06 x1 = 55.

## Flagged for the animation lane (not blockers for wiring a BASE)

- 9 wired bases share their anim_ref with a moves entry flagged
  throw=true: AWAPOP Last Thing You Hear, BAEK-MASTER-WHITE Eleventh
  Lecture, DIABLO Final Boss Tax, DIO Hunger Wears a Mind, LILI Kiss Like
  a Slap, MARIPOSA-MONARCH Fifth Thing Is the Floor, NEGATIVO Bounty or
  Fun, RYUJI-ROCK Layin' the Smackdown, SLICE Skull Mask Off. The base is
  a generic strike base only; throw choreography must be confirmed before
  any retarget use. Anim_refs are NOT replaced by this PR.
- SKULL Retribution Keeps Books: duplicate moves entries share the
  anim_ref with different startup_s (S 0.34s vs 1+2 0.2833s). The sidecar
  startup is the canon startup_frames (20f); the animation lane must
  resolve which entry the loader plays before re-timing.
- Mixed sequences needing GPU trim: 86_01 (kick flurries) and 86_06 (knee).
  Trim/hit frame stay UNMAPPED until the GPU classifier fills them.

## What is explicitly NOT done

- GPU retarget/classify/CA-2 run: PENDING parent browser execution
  (Kaggle T4 x2 notebook, Colab T4 backup). No .npz exists yet; no clip
  is claimed retargeted, trimmed, or jumping-classified.
- Merge: this PR is NOT merged by its author. The deploy queue merges via
  git_merge.py ONLY when green + clean.
- Deploy: sequences AFTER the popup deploy. Numbering note: the lane
  brief named popup PR #1076, but on live main #1076 is a UI follow-up
  rebase and the popup fix is PR #1078; this wiring deploys after the
  popup deploy (#1078), per the owner's locked popup-first order.
- Play verification: NOT done and NOT claimed. Parent browser delegation
  (phone portrait, live build) after merge + deploy.
- The 105 no-base moves, 19 near-miss (reference only), 6 login-gated
  Mixamo moves, and Pantera's 3 existing moves are NOT in this wiring:
  55 + 105 + 19 + 6 + 3 = 188. Nothing is dropped; the 105 go to the
  separate BUILD / T7 / T3 adaptation follow-up in this PR's companion doc.

## Accounting (188 total)

WIRED GENERIC BASE 55 | NO COMMUNITY BASE 105 | NEAR-MISS 19 |
LOGIN-GATED 6 | EXISTING (Pantera) 3.
