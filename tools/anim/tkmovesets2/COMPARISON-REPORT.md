# Re-decode comparison report — our 4 T7 King throw clips vs the solved decode

Date: 2026-11-20. Lane C (scramble-research).
Solved source: TKMovesets2, pinned commit `8e6bfc1` (pushed 2026-11-18, v1.1,
GPL-3.0). See `README.md` + `VENDORED.md` for the pin and the format specs.

## Headline (read this first)

**A full re-decode was NOT done and is NOT claimed.** TKMovesets2 extraction
needs Tekken 7 itself (Steam), which we do not have, and no public King
`.tkmvst` exists anywhere we could find (see §5). What this report does is
the format-level verification that IS possible without the game — our four
clips parsed against the documented `.tkmvst` / MOTA / skeleton structure —
plus the role verification from the resolved mechanism (see
`CONFLICT-RESOLUTION.md`), plus the exact numbers for the bone mapping.

**Role verdict (structural, from repo data): `rotsm_574` and `rotsm_578`
are the THROWER's throw motions, not the victim's receiver.** The repo's
`throws/index.json` and `game/js/t7-throw-clips.js` label them "victim" —
that label is inverted. The real victim receiver move id is still UNKNOWN
(§4). Until it is resolved, the throw pair in the repo is
grab + throw-motion with no receiver — the owner's verification criterion
(throw motion AND receiver, correct roles) is NOT yet satisfied.

## §1 — The four clips (as they stand in the repo)

| Clip | Graph move | Graph name | Label in repo | Resolved role | Anim (MOTA) | Bank | Frames |
|---|---|---|---|---|---|---|---|
| `common_709` | 1785 | `ThrmvLB2_00` | thrower (grab) | thrower's grab (1+3) | `naco_tukami2l(DVD)` | `common.arc` | 40 |
| `rotsm_534` | 1787 | `ThrmvRB2_00` | thrower (grab) | thrower's grab (2+4) | `msco_rtukami(DVD)` | `kinrotsm.arc` | 40 |
| `rotsm_574` | 2125 | `Kg_FLnage00_n` | **victim** | **thrower's throw motion** (1+3, forward) | `nakg_nagexx0a_f(DVD)` | `kinrotsm.arc` | 130 |
| `rotsm_578` | 2129 | `Kg_FRnage00_n` | **victim** | **thrower's throw motion** (2+4, forward) | `kjkg_brain_f(DVD)` | `kinrotsm.arc` | 138 |

Role evidence: move 1785's cancel rows on throw-hit requirements (3/4/5/6/27)
point at 2125/2135/2137/2139/2276; move 1787's point at
2129/2135/2137/2141/2274 — all rows inside King's own moveset, evaluated
throw-side (see CONFLICT-RESOLUTION.md Evidence 5, verified live against
`graph.json`, 2787 moves: all 43 throw-class moves' throw-hit targets sit
inside the graph, 11 with all five branches). A clip that is the target of
the thrower's own throw-hit cancel is the thrower's follow-through.

## §2 — Format-level verification (own run, `verify/clip-format-check.txt`)

Source: repo-scratch shards `clips.01.json` + `clips.03.json`
(`game/assets/anim/t7/king/graph-clips/`), cross-checked against
`throws/index.json`. All four clips:

- Format `wh-anim/1`, 60 fps, **21 bones exactly matching `skeleton.json`
  order** (Hips, Spine, Chest, Neck, Head, LeftShoulder, LeftArm,
  LeftForeArm, LeftHand, LeftUpLeg, LeftLeg, LeftFoot, LeftToeBase,
  RightShoulder, RightArm, RightForeArm, RightHand, RightUpLeg, RightLeg,
  RightFoot, RightToeBase). Missing: none. Extra: none.
- **All quaternions unit-norm** (normMin 0.999999 – normMax 1.000001 in
  every channel of every clip). No NaN.
- Frame counts 40 / 40 / 130 / 138 match the index.
- Banks match the documented MOTA split (`docs/t7-structures.md`: even
  slots = `motbin`, odd slots = `rotsm.arc`): `common_709` from
  `common.arc`, the other three from `kinrotsm.arc`.
- Graph moves carry `fmt: 0x64`, matching the documented T7 animation type
  byte (`0x64` or `0xC8`).
- Provenance (clip `t7_source` fields): format `0x64`, `mota_block` 0,
  conversion tool `tools/anim/t7_anim64_to_c8.py`, method = "the game's
  own sampler (`TekkenGame-Win64-Shipping.exe` RVA 0x73ea30, CPU-emulated)
  sampled at frames 0..n-1, each rotation re-expressed as the 0xC8 Euler
  triple (round trip through the game 0xC8 path exact to 3.6e-7)".
  Applier: Kiloutre BlenderTekkenDirect `TekkenAnimHelper.py`
  `applyRotationFromAnimdata`, commit
  `bebb3d8bc5c4c2c58778ac6af4f87f3dc80062b1`. So the clips did NOT come
  from raw scrambled files — they came through the game's own 0xC8
  sampler path. **The remaining question is the BONE MAPPING** (which
  channel → which named joint), done by that applier onto the mannequin.

### Joint-by-joint channel table (distinct quaternions per clip)

"distinct" = number of different quaternions in the channel (a channel
with 1 distinct quat is frozen at identity for the whole clip).

| Bone | common_709 (40f) | rotsm_534 (40f) | rotsm_574 (130f) | rotsm_578 (138f) |
|---|---|---|---|---|
| Hips | 40 | 39 | 130 | 137 |
| Spine | 40 | 40 | 130 | 138 |
| **Chest** | **1 (identity)** | **1 (identity)** | **1 (identity)** | **1 (identity)** |
| Neck | 40 | 40 | 18 | 134 |
| Head | 40 | 40 | 130 | 138 |
| LeftShoulder | 36 | 35 | 130 | 138 |
| LeftArm | 40 | 40 | 130 | 138 |
| LeftForeArm | 38 | 38 | 124 | 120 |
| LeftHand | 40 | 40 | 69 | 136 |
| LeftUpLeg | 40 | 40 | 130 | 138 |
| LeftLeg | 37 | 35 | 126 | 129 |
| LeftFoot | 40 | 40 | 130 | 138 |
| **LeftToeBase** | **1 (identity)** | **1 (identity)** | **1 (identity)** | **1 (identity)** |
| RightShoulder | 38 | 39 | 129 | 138 |
| RightArm | 40 | 40 | 130 | 138 |
| RightForeArm | 38 | 39 | 121 | 126 |
| RightHand | 40 | 38 | 93 | 136 |
| RightUpLeg | 40 | 40 | 130 | 138 |
| RightLeg | 36 | 38 | 125 | 132 |
| RightFoot | 40 | 40 | 130 | 138 |
| **RightToeBase** | **1 (identity)** | **1 (identity)** | **1 (identity)** | **1 (identity)** |

### The frozen-channel finding (OPEN, needs a `.tkmvst`)

**Chest is frozen at identity `[0,0,0,1]` in all four clips. So are
LeftToeBase and RightToeBase.** Hunt Lane C's independent audit
(`audit-decode.json`) agrees: Chest maxDev 0° / path 0 in all four T7
clips, vs 36.9–40.0° maxDev in all four T3 reference clips (2795/2797
thrower, 3018/3051 victim). Spine DOES move in the T7 clips (34–70.8°
maxDev), so the torso is not entirely frozen — the freeze is specific to
Chest and the toe bases.

Two explanations remain open and cannot be distinguished without the
source blob + skeleton bone map:

1. The T7 `0x64` blob genuinely does not drive Chest / toe bases (the
   game's own skeleton has no live channel there for these anims), or
2. The bake padded those channels with identity.

`rotsm_574` also shows Neck with only 18 distinct quats over 130 frames
(heavily stepped) and hands partially frozen early — consistent with a
bake that quantises or drops sparse channels, but again not provable
without the source. `tkmvst_to_wh.py validate` flags frozen-identity
channels as warnings (not errors) for exactly this reason.

### Skeleton caveat

`skeleton.json` is the Koenji TekkenMannequin
(`TekkenMannequin_no_ik.blend`, sha256 `ce8171083d0c6da5…`), 21 joints,
all rest rotations identity — a generic mannequin, NOT King's
per-character `SKT_CH` skeleton. WH's T7 bone map is mannequin-based;
whether King's own skeleton differs in a way that matters is unverified
and needs the `.tkmvst` (which carries the per-character skeleton).

### Root motion (own run)

- `common_709`: root_t f0 y=1.052 → fLast y=1.070, forward 0.194 m.
- `rotsm_534`: forward 0.190 m.
- `rotsm_574`: root x −1.169 → +1.208, forward 2.377 m.
- `rotsm_578`: forward −0.162 m.

### Motion totals (hunt Lane C audit, for reference)

| Clip | armL | armR | legL | legR | spineHead |
|---|---|---|---|---|---|
| common_709 | 693 | 552 | 368 | 296 | 341 |
| rotsm_534 | 594 | 747 | 263 | 249 | 287 |
| rotsm_574 | 1704 | 1578 | 2073 | 1989 | 1761 |
| rotsm_578 | 1676 | 2170 | 1393 | 1596 | 1182 |

All quat norms 1.0, 0 NaN. Hunt Lane B twist numbers: `common_709`
33.6° @f14, `rotsm_534` 58.4° @f11 (both 40f upright grab holds);
`rotsm_574` twist 280.8° @f111, pitch 116.3°, root XZ 2.715 m;
`rotsm_578` twist 193.3° @f136 (late ground roll only); `rotsm_718`
348.8° is the biggest spin in the set. Hunt Lane B caveat stands: motion
alone cannot prove roles — the role verdict above comes from the
cancel-row structure, not from the motion.

## §3 — What the solved pipeline changes vs our graph-bank clips

Honest answer: **at the format level, nothing contradicts the clips** —
bones, frames, quats, banks and the 0x64 type byte all match the documented
structure, and the clips already came through the game's own 0xC8 sampler.
The solved pipeline does not overturn the clips' geometry; it changes the
**provenance and the roles**:

1. **Roles**: 574/578 flip from "victim" to "thrower throw motion"
   (structural proof, §1). The pair clock in `t7-throw-clips.js` (thrower
   40f finishes before victim 130f/138f) is built on the mislabeled roles
   and needs re-derivation once the real receiver is known.
2. **Receiver**: the solved pipeline says the receiver is a Reaction List
   move in King's moveset — a clip this repo does not have at all. Our
   graph extraction dropped the hit-condition/reaction tables, so no
   receiver clip exists in WH data today.
3. **Bone mapping**: unproven either way. The mannequin-based mapping
   stands unchallenged but unverified; a real King `.tkmvst` + its
   `SKT_CH` skeleton is the only way to confirm or correct it (notably
   the frozen Chest / toe bases).
4. **Tooling**: `tkmvst_to_wh.py` now exists in the repo to resolve the
   triple and validate clips against any future `.tkmvst` — proven
   against a spec-conformant synthetic King `.tkmvst` (29 assertions,
   `test_tkmvst_to_wh.py`, all passing).

## §4 — What is still UNKNOWN

- The receiver move id for King's 1+3 and 2+4 throws (HitCondition →
  ReactionList). Field path documented in `tkmvst_to_wh.py` and
  `king-throw-triple.json`; value: unknown.
- The throw-camera animation (throwCameras table / Extra Move Property
  rows on the throw moves). Same status: field path known, value unknown.
- Whether Chest / toe-base identity is real (game data) or a bake
  artefact.
- Whether King's per-character skeleton differs from the mannequin in a
  way that changes the bone map.

## §5 — Public King `.tkmvst` search (negative, 2026-11-20)

- archive.org, live search (`site:archive.org tekken moveset`): only
  manuals (Tekken 3 manual, Tekken 5 USA djvu, Tekken 2 demo) — no
  `.tkmvst` / moveset item.
- Web: "King Tekken 7.tkmvst moveset download", "TKMovesets2 tkmvst
  download King TekkenMods", `"tkmvst" filetype OR github OR tekkenmods
  moveset download`: no public King `.tkmvst`, no decoded T7 animation
  pack, no `.tkmvst` file host. TekkenMods moveset mods exist (e.g.
  Project Angel, old `.bin` format) but none is a King `.tkmvst`.
- The T7 throw hunt's Lane C was still searching when this report was
  written; this lane did not duplicate its in-flight search beyond the
  checks above.

## §6 — What unblocks the full re-decode (in order)

1. **Tekken 7 (Steam, latest build) + TKMovesets2** — extract King
   (and, if EMP 0x83C3 work is ever needed, the victim) and run
   `tkmvst_to_wh.py triple` + `validate`. This is the real unblock.
2. **A public King `.tkmvst`** — same commands, no game needed.
3. **The `kinmot.json` source with hit-condition/reaction tables** —
   would resolve the receiver id even without a `.tkmvst`, though it
   would not give the raw animation blob for a byte-level re-decode.

## §7 — Fix proposal (NOT made — per brief, propose, don't touch)

`game/assets/anim/t7/king/throws/index.json` and
`game/js/t7-throw-clips.js` label 574/578 (and 588/590/592/594/716/718)
as the victim's reaction. Per §1 they are the thrower's throw motions.
Proposed: re-label them `thrower` in both files, remove the "victim
reaction" claim from the `t7-throw-clips.js` header, and leave the
`victim` slot empty until the Reaction List receiver is resolved from a
real King `.tkmvst`. The pair clock (40f thrower vs 130f/138f victim)
must be re-derived at that point — do not keep the old timing on the new
roles. No throw wire-up file was touched in this lane.
