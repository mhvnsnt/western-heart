# Rig fix — Demonio Attire 1 (Demonio T7-treatment lane, 2026-10-31)

Lane: Demonio T7 treatment (owner ruling 2026-10-31: Demonio is a
SHORT-class job — straightforward Jin moveset, visual-only
transformations — and is startable now; his skin weights, rig, motions
and stance are completed before he is shown again). Tool: the pipeline
already on main — `tools/auto_rig/backends/skin_audit.py` →
`tools/auto_rig/backends/weight_cleanup.py` → re-audit →
`tools/auto_rig/validate.py` gate, with `tools/anim/gltf_codec.mjs`
for the meshopt decode/encode around it. No new tooling was written
for this fix. Per-character isolation: this change touches Demonio's
Attire 1 file only.

File: `roster/demonio/attires/attire1/model.glb`
(28,872,600 B before → 28,793,068 B after; the size delta is the
codec's re-encode, see below — the weight repair itself patches skin
accessors in place at identical byte length).

Git blob SHA: `5b531cfa…` → `3bd1e9c98fbcb1bc581ed95ebeb7945a56d56eb6`
(sha256 after: `b95e71252ba11b4308b9c96f575217e3e292707579de65b2867558dce307804d`;
sha256 before: `e5b7b54cb5ab69941c98f99c3d4c2b2fefa37e678df6e7f212bd1f8428fda8a3`).

## Diagnosis (all numbers measured by this lane on main's file)

The 2026-10-30 rig sweep (docs/RIG-AUDIT-SWEEP-2026-10-30.md) listed
this file as **AUDIT-ERROR** — it is EXT_meshopt_compression and the
sweep-era audit could not read it. This is the first real audit
verdict on the file. Audit before (skin_audit.py on the
`gltfpack -noq` decode the tool itself specifies; the tool's own
meshopt detour produces the same decode), 1,286,272 verts, 73 joints,
height 2.0 m: FAIL on three checks.

1. **Dead major joints** — `RightFoot` carries zero weight (the right
   foot's verts are painted to Leg/ToeBase neighbours, so foot
   animation channels move nothing), plus `LeftForeArm.001` /
   `RightForeArm.001` (see blocker 1) and 29 minor finger/palm joints.
2. **Contamination** — mass **0.00113** (gate: < 0.001), 10,301 verts.
   Worst verts split ~0.4 of their weight between `RightUpLeg` and
   its leaf twin `RightUpLeg.001`, whose audit segment sits far from
   those verts — the twin-split class.
3. **Arm joints outside the mesh** — `LeftForeArm` / `RightForeArm`
   0.185 m and `LeftHand` / `RightHand` 0.257 m from the mesh surface
   (mesh not watertight, so the audit's distance fallback applies).
   Skeleton-domain — see blocker 2.

Passing before: weight sums (0 bad), unweighted (0), no JOINTS_1,
proportions (warnings only), no folded chains, feet planted (0.0).

## Fix applied (weights domain only)

Standard cleanup (`weight_cleanup.py`) on the decoded file:
**10,842 contaminated slots pruned**, **34,081 verts revived** onto
dead joints by proximity reassignment (this is what brings RightFoot
back — its territory was sitting on its chain neighbours),
0 unweighted verts to fill, edge smoothing, prune + renormalize.
The repaired plain file was then re-encoded to the shipped meshopt
form with the repo's own codec (`tools/anim/gltf_codec.mjs encode`:
gltf-transform prune with keepSolidTextures + meshopt medium) — the
same encode the Tripo rig pipeline ships with; the shipped file
carries the same extensions as the original
(EXT_meshopt_compression + KHR_mesh_quantization), 73 joints, 1 mesh.

**Weights-only proof (on the plain repaired file, pre-encode):** the
JSON chunk is byte-identical to the decoded original; of 10
bufferViews exactly 2 differ — `JOINTS_0` and `WEIGHTS_0`. Every
POSITION/NORMAL/TEXCOORD/index/inverse-bind/image accessor is
bit-identical. The shipped (encoded) file was then audited itself:
its verdict and every headline number are identical to the plain
repaired file's (table below).

## Result (re-audited on the shipped file)

| Check | Before | After |
|---|---|---|
| contaminated weight mass | 0.00113 (10,301 verts) | **0.0 (0 verts)** |
| dead major joints | RightFoot, LeftForeArm.001, RightForeArm.001 | LeftForeArm.001, RightForeArm.001 (blocker 1) |
| weight_sum_bad / unweighted | 0 / 0 | 0 / 0 |
| joints inside mesh | FAIL (forearms 0.185 m, hands 0.257 m) | FAIL — unchanged (blocker 2) |
| proportions / folded chains / feet planted | pass | pass |
| validate.py hard checks | — | **all pass** on the plain repaired file (valid_gltf, skinned_mesh, bones_present, height_ok, fingers_symmetric) |

8 of 10 audit checks pass; both weight-domain gates that failed
(contamination, and the RightFoot half of the dead-joint gate) are
fully clear. Note on validate.py: run against the shipped meshopt
file it reports height_ok=false — it does so identically on the
ORIGINAL shipped file (its reader does not dequantize meshopt
buffers); a pre-existing tool limit on this file class, not a
regression. The audit, which decodes meshopt properly, verifies the
shipped file directly.

**Proof renders** (proof_pose.py, same pose on both files:
RightUpLeg:X:-25, RightLeg:X:35, RightFoot:X:-20, LeftArm:X:-40;
viewed by this lane): before, the posed RightFoot channel moves
nothing (the foot stays behind while the leg lifts); after, the foot
follows the leg as one piece. Files: `proof-demonio-a1-before-front.png`,
`proof-demonio-a1-after-front.png`, `proof-demonio-a1-before-side.png`,
`proof-demonio-a1-after-side.png` beside this doc (the tool's "front"
camera shows this model's back; the side pair shows the leg/foot).

## Not fixed — named blockers (skeleton-domain)

1. **Dead leaf bones `LeftForeArm.001` / `RightForeArm.001`.** This
   rig carries `.001` leaf helpers (Arm.001, UpLeg.001, Leg.001 all
   hold real weight — UpLeg.001 more than its parent). The forearm
   pair was simply never painted: zero weight, no children. Cleanup's
   revival cannot revive them — their segment spans ForeArm→Hand and
   its verts are dominated by ForeArm and Hand, while revival only
   reassigns verts dominated by the dead joint's parent or children
   (Hand is a sibling, not a child). Zero-weight leaves deform
   nothing at runtime. Clearing the gate needs a skeleton-domain
   decision: paint them by splitting ForeArm territory, or drop the
   two bones. Recorded, not forced.
2. **Arm-chain bind positions outside the mesh** (ForeArm 0.185 m,
   Hand 0.257 m, both sides; the offset grows along the chain —
   shoulder inside, wrist far out — a bind-pose divergence between
   the skeleton's arm chain and the mesh's arm volume). Weights
   cannot move joints. Clearing it needs a bind-pose refit decision
   (the `tools/auto_rig/refit_skeleton.py` class). Recorded, not
   forced — the same treatment as bloodline-ember's proportions
   blocker (RIGFIX-DEMONIO-BLOODLINE-EMBER-2026-10-31.md).

## Environment note

The stock audit OOM-killed three times on this VM under multi-lane
load (7 GB; exit 137) before completing — the verdict above was
produced by the unmodified tool, launched through a RAM gate
(≥ 2.3 GB MemAvailable) against a pre-decoded `-noq` copy (the same
gltfpack -noq decode the tool performs internally; the shipped
meshopt file was ALSO audited directly through the tool's internal
decode, with identical results). Blender proof renders used the
staged EGL stack (see the bloodline-ember handoff for the recipe).
Input file was fetched from main and verified by git blob SHA
before use.
