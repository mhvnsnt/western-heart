# Head-region weight-bleed fix — 2026-11-06

Owner order (2026-11-06): "and so do many others, evaluate and fix them all"
(the Yukihyō face-stretch report: "Yukihyō has some face stretch issues
during match and so do many others").

Follow-up to PR #1620, which fixed the engine-side twisted neck/head
(bank head-frame constants in `game/js/t3anims.js`) and scoped the residual
model-side component: on auto-rigged models, head-area vertices are never
fully weighted to the head chain, so body motion (spine turns, arm swings)
drags the face. This PR fixes that component in the model files themselves.

**Provenance of the defect (owner correction 2026-11-07):** the defect
was introduced by **our own auto-rig pipeline's weight assignment**,
not by the source models. The Tripo 3D sources are static statue
meshes — no weights, no skeleton — and are defect-free; every weight
on the game-loaded GLBs was produced by our rig stage, and the bleed
is our rig stage's nearest-bone weight bleed. Raw statues render
clean (proven 2026-10-22); only the rigged versions carry the defect.
This fix therefore corrects our pipeline's weights in place — it does
not modify any source geometry, for any model.

## Method (pipeline stage, no hand work)

New stage `tools/rig_repair/head_debleed.py`, built on the pipeline's own
precedents (`armpit.py`'s region rule, `separate.py`, and
`transfer_weights.py`'s topology smoothing):

- head chain = the `Head` joint + its node descendants; `Neck` = Head's
  parent joint (the anatomical transition).
- **Region rule:** every vertex with head-chain weight ≥ 0.10 keeps only
  head-chain + Neck influences, renormalized; the allowed-joint weight
  field is then laplacian-smoothed over the mesh topology (4 iterations)
  so the region boundary blends instead of tearing. Smoothing
  redistributes only among allowed joints — drag can never be smoothed
  back in.
- JOINTS/WEIGHTS are rewritten only for region vertices; meshopt files
  get only the WEIGHTS payload stream re-encoded (byte-exact round-trip
  verified against the original stream before use); every other byte is
  preserved.
- **Coincident-vertex weld:** multi-prim / multi-mesh exports duplicate
  seam vertices per primitive. Smoothing per-prim fields independently
  split those duplicates under motion (armor-king's jaw seam measured
  2.7 cm apart under a head turn). The restricted field is therefore
  weld-averaged across coincident positions (1e-4 grid) over **all
  meshes sharing the skin**, before and after smoothing, and the fix
  set extends to coincident partners — the 0.10 line cannot split one
  surface point. After the weld, armor-king's worst seam split is
  0.0000.
- **Meshopt EXPONENTIAL filter:** the 49-joint float-weight family
  stores WEIGHTS with an `EXPONENTIAL` meshopt filter; the stage
  re-applies `encode_filter_exp(bits=12, SharedVector)` — calibrated to
  reproduce the original stream byte-for-byte — and verifies filtered
  streams with a float tolerance (the filter is lossy by design);
  unfiltered streams keep the byte-exact assertion. A file the stage
  cannot round-trip is refused, never written corrupt.
- **Canonical head pick** (`tools/rig_repair/headpick.py`): the `Head`
  joint is identified with the game's own canonicalization
  (`canonBoneName` in `game/js/t3anims.js`): `mixamorig:` prefix and
  Sketchfab `_NNN` suffixes stripped, Biped family prefix handled.
  When several joints canonicalize to Head (Rigify exports carry
  control + deform heads), the one whose subtree carries the skin
  weights wins, scored on the file's own JOINTS/WEIGHTS. No per-model
  constants anywhere in the stage.

Why not `transfer_weights.py`'s kNN copy from correctly-weighted verts:
in this defect family there are no correctly-weighted verts to copy
from — the family's max Head weight is ~0.48 (yukihyo-attire1) — a
nearest-neighbour copy can only average the bleed. The intra-mesh region
de-bleed is the pipeline's own answer for this class.

Why not a "plurality" fix-set (only verts whose chain+Neck weight already
beats every other joint): measured and rejected on yukihyo-attire1. The
verts it leaves behind are the worst bleeders (9,347 verts, mean outside
weight 0.666), sitting at t = −0.4..1.25 on the Neck→Head axis — the
jaw/neck/collar band, i.e. head assembly, not torso. Under the
distortion arbiter below, plurality made jaw distortion *worse* in both
poses (body-sway 0.213 → 0.246; head-turn 0.109 → 0.133) while the
region rule takes body-sway jaw distortion to 0.000.

## Verification method (per model)

- `tools/rig_repair/head_bleed_measure.py`: head-region weight stats —
  mean chain weight, mean Neck weight, **drag** = mean weight on driven
  bones outside chain+Neck over region verts (clean control, Pantera
  Mixamo: 0.025), max Head weight, soft fraction.
- `tools/rig_repair/head_distortion.py`: true linear-blend skinning of
  the model's own verts under two canonical poses — (A) head turn
  (Head +35°, Neck −12° about the Neck→Head axis), (B) body sway
  (chest + shoulders +8°, head unposed, inheriting through the
  hierarchy — face distortion here is pure weight-bleed drag) —
  reporting pairwise-distance distortion in face / jaw / collar bands
  plus a collar↔chest seam metric. Rest state = skin-at-bind, so each
  file's bind-pose scale cancels exactly. Face/jaw bands are intersected
  with the head-assembly region (chain weight ≥ 0.10): on multi-arm
  rigs (dxmmii) the spatial shell above the neck also contains raised
  arm geometry on arm bones, and pairwise distortion across two
  anatomical parts measures their relative motion, not face stretch —
  the purely spatial band falsely read dxmmii's fix as worse before
  this correction (his corrected numbers: body-sway face 0.010 → 0.000,
  jaw 0.013 → 0.000).
- Textured fighting-stance stills (before/after) per model, rendered
  through the game's own retarget engine (the #1620 audit harness):
  `docs/proof/2026-11-06/weight-bleed-fix/stills/`. Banks are each
  fighter's own (moveset index `anim_bank`/`t3_source`, validated
  against the bank directories on main; per-file provenance in
  `fix-table.md`). 10 fighters have no T3 bank in the index and were
  posed with the king reference bank, labelled in the table. One bank
  swap was forced by the data: the `devil_jin` bank nulls the harness's
  stance clip (`Cannot read properties of null (reading 'stance')`),
  so Demonio's winged attire is posed with `jin` — Demonio's own index
  anim_bank.
- **Star attire5 stills note:** the source file
  `roster/star/attires/attire5/model-improved.glb` contains **681
  non-finite (NaN) position vertices** — identical count before and
  after this fix (the stage never touches positions). They poison the
  harness's framing bounds, so her still pair shows the same framing
  failure on both sides; her fix is carried by the stats + distortion
  rows (drag 0.763 → 0.000). The NaN verts are a separate pre-existing
  model defect, flagged here, not repaired by this stage.

## Headline case — Yukihyō attire1 (the owner's report)

File: `roster/yukihyo/attires/attire1/source/yukihyo-a1-rigged.glb`
(the file the audit's 0.48 Head-max measurement was taken on; the default
`game/assets/models/yukihyo.glb` is a different, nearly clean ADR rig —
drag_hard 0.003 — and is deliberately untouched; its 0.082 soft drag is
that rig's own inert aux-joint design).

| metric | before | after |
|---|---|---|
| drag (total) | 0.130 | **0.000** |
| max Head weight | 0.478 | 0.694 |
| mean chain weight | 0.774 | 0.847 |
| distortion B (body sway), face | 0.024 | **0.000** |
| distortion B (body sway), jaw | 0.213 | **0.000** |
| distortion A (head turn), face | 0.066 | 0.053 |
| distortion A (head turn), jaw | 0.109 | 0.106 |
| seam collar↔chest (B) | 0.030 | 0.033 |

Stills: `stills/yukihyo-a1-stance-front-before.png`,
`stills/yukihyo-a1-stance-front-after.png` — identical at stance (no
bind-pose regression); the fix acts under motion, per the table.

## Census

All 182 unique GLBs referenced by MODEL_URLS were measured
(`census-table.md`): 147 measured, 31 are unskinned source files
(nothing skinned to bleed), 4 have no canonical head chain (itemized
under "Not fixed" in the PR). Clean control band: drag ≤ 0.03 (Pantera
0.025). 103 files measured above the band; 102 were fixed with the same
stage and settings — one exclusion is the ADR yukihyo default (below),
one is HELD (Diablo, below) and one was REMOVED (the Julia-based
nightwolf.glb, below), leaving **100 payloads shipped**. Per-model before/after stats + distortion are in `fix-table.md`
and the machine-readable `fix-records.json`. Eight further files the
first-pass measure had errored on (a zero-division bug in the early
measure, since fixed) were re-measured inside the fix run and came out
at drag 0.000 — clean, no payload landed for them.

## Stage notes (defects found in the tooling while running the roster)

- **Merged meshopt index streams:** gltfpack can merge many
  primitives' indices into one meshopt stream whose extension count is
  the whole stream; each accessor slices the decoded stream by its own
  byteOffset. `ingest.accessor` decodes only the accessor count and
  the codec refuses the truncated stream, which crashed the stage on
  `roster/parvati/attires/attire1/model-rigged.glb` (29 prims sharing
  one 443,148-index stream). `head_debleed.py` therefore reads indices
  through its own `read_indices` (full-stream decode, accessor-offset
  slice; every slice validated: max index = vertex count − 1). The
  same latent bug exists in the pipeline's `ingest.py` for any stage
  that reads indices — flagged here rather than silently forked.
  Output on non-merged files is byte-identical before/after this
  addition (verified on the yukihyo headline case).
- **Canonical head pick** (`headpick.py`): see Method. Census pass 3
  re-measured the 8 files the naive name match had failed on: Soldier
  (create-fighter template, drag 0.0317 — fixed), iori attire1 (0.010,
  clean), Ryusan's intake (0.004, clean), vega attire1 (0.000, clean),
  and the 4 no-head-chain files under "Not fixed".

<!-- FIXED-TABLE: fix-table.md -->
<!-- NOT-FIXED: in the PR body -->

## HELD — Diablo attire1 (owner correction 2026-11-07)

`roster/diablo/attires/attire1/model-rigged.glb` measured drag 0.108
and a weights-only de-bleed was produced (→ 0.000), but **no Diablo
payload ships in this PR**. Per the owner's correction: Diablo's
Tripo source is a defect-free static statue; his skeleton, weights,
hair chains (the rig stage's "Tail" chains run through his hair — he
has no tail) and facing all come from our auto-rig pipeline, and his
fix is to be re-scoped as a rig-pipeline fix (weights + skeleton
orientation produced by the rig stage, fixed with the researched
industry-standard method) with honest provenance. The de-bleed record
is retained in the lane scratch, out of this PR's payload set, until
the lead re-scopes it.

## REMOVED — Julia-based nightwolf.glb (owner correction 2026-11-07)

`game/assets/models/nightwolf.glb` measured drag 0.378 and was fixed
(→ 0.000) in the batch — but the file is **Julia's model**, a later
attire that "ladders back" per `roster/nightwolf/attires/ATTIRE-SLOTS.md`;
it is not Nightwolf, and per the owner's order its fix does not ship
in this PR. The real Nightwolf is her Tripo "tribal warrior" default:
the statue `roster/nightwolf/attires/attire1/model.glb` (unskinned,
nothing to fix) and its loadable rigged form
`roster/nightwolf/attires/attire1/model-rigged.glb` (registered as
`nightwolf-attire1`, her DEFAULT attire, in `game/js/assets.js`) —
that file IS fixed here (0.276 → 0.000) and is the Nightwolf headline
proof alongside Yukihyō attire1. The Julia file's de-bleed is retained
in the lane scratch; its remaining weight-stage defects (Phase C
render census: stance shred) stay queued in the Phase C follow-up,
framed as that attire file.

## Visual acceptance review (owner bar 2026-11-07)

All 100 shipped before/after still pairs were re-reviewed side-by-side
against the owner's acceptance bar (posed output must look like the
clean bind — no crushed arms/forearms, no twists, no twisted necks).
Result: **no pair shows a deformation introduced by the de-bleed**;
every AFTER matches its BEFORE's pose and proportions, with visible
head-area improvement on the bleed-heavy cases. Pairs whose harness
framing fails identically on both sides (fix carried by stats +
distortion): kiko-tanaka + alt1 (pre-existing full-body robe shred —
Phase C weight-stage queue), mariposa-monarch (skeleton/retarget
incompatibility — rig lane), silvertongue attire2, zangief attire1,
zen oversoul + tentacle (camera inside oversized / non-humanoid
geometry), star attire5 (681 NaN position verts in the shipped file,
identical before/after — flagged above, not a weights defect). Thor
attire1's pair caught two different frames of the same stance clip
(capture timing); both frames are clean.

## Merge-gate verification (PR #1641, 2026-11-07)

Diff verified independently of the API diff view (which times out on
this payload size): local diff-tree between the branch base and the
final tree = exactly the 309 intended paths, every blob sha matching
the staged change set, 0 deletions, 0 unexpected paths. Check runs on
the head commit: guard, deletion-guard, pr-safety-guard, clobber-guard,
rig-guard, coverage-guard, canon-names, ui-sources, material-gate,
budgets, speed-quality and menu-touch-e2e all SUCCESS. Two runs failed
inside actions/checkout itself ('/usr/bin/git' exit code 128 while
fetching this PR's ~2.6 GB of GLB payloads): game-unit-tests and
instruction-gate — no test or gate logic executed in either (this diff
contains zero .js files); instruction-gate failed 3 of 4 runs on the
already-shipped #1640 the same way. This section was appended to
re-trigger those two runs under lower contention. S6 read-back of
every payload file from main follows the merge.
