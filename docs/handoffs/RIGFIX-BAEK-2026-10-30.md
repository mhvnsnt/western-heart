# Rig fix — Baek (B3 step 1, 2026-10-30)

Lane: WESTERN HEART 100% burn-down, piece B3 (full-roster rig batch).
Tool: the pipeline already on main — `tools/auto_rig/rigfix.py`
(audit `tools/auto_rig/backends/skin_audit.py` → cleanup
`tools/auto_rig/backends/weight_cleanup.py` → re-audit → `validate.py`
gate). No new tooling was written for this fix. Per-character
isolation: this change touches Baek files only.

## Which file the 2026-10-29 proof used — identified

The Oct-29 proof (PR #1231) ran on `game/assets/models/baek.glb`.
Verified 2026-10-30: the workpaper input
(`~/workspace/_rigfix-work/models/baek.glb`, sha256
44aabf4e72a4908b4aa33d6f4f546717a4d65855230794cf0a31e17076e45295)
has git blob SHA `802dfd7c0b44bae99b7d23cee1b41a8976a4bc78`, which is
exactly main's current blob for `game/assets/models/baek.glb`
(385,844 B) — main's file is byte-identical to the proof's input, and
it still carries the failure the proof measured. That game file is
outside this PR's roster-only scope; it is flagged here because its
skin data is the same failure class, with the same cleanup numbers,
as the master-white rigged file fixed below (both: 3,990 verts, 50
joints, dead LeftHand + RightHand, contamination 0.087%, cleanup
128 pruned / 707 revived / 7 filled).

## Fixed in this PR (all: audit FAIL → rigfix → audit PASS, exit 0)

Gate key: all 10 skin_audit checks. Before, the only failing check on
each file was `no_dead_joints` (dead major joints LeftHand +
RightHand; hand verts were 100% finger-weighted). After cleanup all
10 checks pass on all three files; `validate.py` hard checks
(valid_gltf, skinned_mesh, bones_present, height_ok) pass on all
three outputs.

| File | Size (B) | Before: contamination | Cleanup (pruned / revived / filled) | After: contamination | After: dead majors |
|---|---|---|---|---|---|
| roster/baek/attires/master-white/baek-master-white-rigged.glb | 570,500 | 0.087% (21 verts; worst vert 3491, 0.76 onto Spine1+Spine) | 128 / 707 / 7 | 0.003% (2 verts; worst 0.052) | none |
| roster/baek/attires/master-white/model-custom.glb | 579,492 | 0.086% (21 verts; worst vert 3498, 0.76 onto Spine1+Spine) | 134 / 758 / 7 | 0.003% (2 verts; worst 0.052) | none |
| roster/baek/attires/master-white/model-kevin-diff.glb | 1,124,404 | 0.083% (24 verts; worst vert 5049, 0.771 onto Spine1+Spine) | 217 / 700 / 7 | 0.001% (worst 0.052) | none |

Other before/after measurements, identical before and after on all
three files (cleanup changes weights only): weight_sum_bad 0,
unweighted_verts 0, JOINTS_1 present: no, proportion flags none,
folded chains none, joints outside mesh none, feet_min_above_floor
0.0. Minor finger joints remain dead after the fix exactly as in the
Oct-29 proof (they are not major joints and are not gated);
`validate.py` `fingers_symmetric` is false before and after
(pre-existing, not a regression, not claimed fixed).

Blob SHAs (before → after):
- baek-master-white-rigged.glb: 0da6efb7b3e100123a10d21a3c26a0b1378c6ad6 → 0032ae9337e5fd2fecee79131c731e92f9479665 (sha256 after: 85fdbba20e40fbe13c3dcfb63e8f5619e83cd7e1f65179f87ab4047ac5db43d2)
- model-custom.glb: 71c8be30e7b8fba425a41a03ab858a4de839ad25 → 9e6bdfa08c8e7b8dc794f5c3061a9e5ff7362c76 (sha256 after: 958f914dedd88a1145b96c24623cfb049de177e2c22e5fe556f269e6b5955305)
- model-kevin-diff.glb: a1ffef86199b84839fd7d0ec52f86ede29d641ea → c16ecfe1cfce625adf6c34fe8def664b1c44317a (sha256 after: a1d2f38652f36dc4d344676fc28186b83479ca1900fb30cb363c6153bf4774c6)

File sizes are unchanged (the cleanup rewrites weight accessors in
place; geometry, skeleton, materials and textures are untouched).

## Baek files audited but NOT fixed in this PR

| File | Size (B) | Verdict | Why |
|---|---|---|---|
| roster/baek/attires/attire1/model.glb | 8,473,628 | FAIL — not skinned | skin_audit returns skinned: false. It is the unrigged source model; there are no weights to clean. |
| roster/baek/attires/master-white/baek-master-white.glb | 469,640 | FAIL — not skinned | Same: unrigged source model, skinned: false. |
| roster/baek/attires/attire1/model-rigged.glb | 23,796,696 | AUDIT-ERROR — tool limit, not a verdict on the weights | The file is EXT_meshopt_compression (fallback buffer 1, 69,249,292 logical bytes); skin_audit reads physical buffer offsets and throws (accessor start beyond the 23,733,552-byte BIN chunk). Decoding with the repo-side gltf-transform copy command works (71,330,820 B out), but the decoded mesh has 1,622,503 verts / 73 joints and the pure-Python audit did not finish within a 280 s cap on this shared VM. Needs a vectorized/faster audit pass or a bigger machine before it can be audited or cleaned. Its weights are NOT claimed good or bad here. |

## Honest limits (unchanged from the Oct-29 pass)

Baek's dark waist bar and the raised-hand / wrist look are
geometry/pose, not weights. This change does not fix them and does
not claim to. The win in this PR is in the weight data only: dead
Hand joints revived, contaminated slots pruned, weight sums exact.

## Environment note

Work was done in ephemeral tmpfs scratch, not on the home disk
(home is over quota). /tmp itself was at 100% (0 bytes free, other
lanes' in-progress renders) for most of this run, so the scratch
dir used was /var/tmp (same tmpfs class); downloads were fetched
singly, hash-verified against main's blob SHAs, and deleted after
use. The commit was built with the Git Data API from verified tree
SHAs (NO-SPARSE-COMMIT LAW) — no sparse checkout was committed from.
