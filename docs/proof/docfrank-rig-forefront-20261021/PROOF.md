# Doc Frank Tripo forefront — proof (2026-10-22)

Owner orders (2026-10-21 ~22:55–23:01 CDT): Doc Frank's ladder entries
1–5 are his Tripo models, Tekken reskins to the back; every Tripo form
rigged on intake ("not just statues") onto the character rig it
belongs to.

## What shipped

- Ladder (`game/js/attires.js`): entries 1–7 are the Tripo forms —
  1 `doc-frank-big` (Attire 1 Transformed, the player default),
  2 `doc-frank-wowomomo`, 3 `doc-frank-wowomomo-big`, 4 `doc-frank-hood`,
  5 `doc-frank-hood-big`, 6 `doc-frank-frankenstein`,
  7 `doc-frank-frankenstein-big`; the reskin-lineage pre-form
  (`doc-frank-a1`), the Tekken base (`doc-frank`) and the machine-shop
  reskin close the ladder at 8–10. Roster main entry model =
  `doc-frank-big`; the transform mechanic is preserved both ways
  (pre-form ⇄ Transformed) via the entry's `forms` map.
- The four previously unrigged Tripo transformed forms are rigged
  (1 skin, 178 joints, 3 embedded texture images each) onto Doc
  Frank's Bosconovitch skeleton — see "Rig method" for why.
- Lane 4's Wowomomo + Frankenstein base rigs were bind-normalized
  (7 pose-encoded binds each → identity; bind-pose skinning
  invariance 4.5e-08, the PR #465 standard).
- `tools/auto_rig/backends/apply_skin.py` generalized (any donor
  rig, not just the 50-node Pantera layout) + the Tripo intake rule
  documented in `roster/TRIPO-REGISTRY.md`: a Tripo pull is rigged to
  its character's rig on intake, automatically.

## Wiring probe

`probe.mjs` (this directory) run against the branch tree — ladder
order, Tripo-first-five, back-of-ladder, default, transform targets,
MODEL_URLS existence, per-file rig/image scan: **all checks PASS**
(full output: `probe-output.txt`).

## Rig method

Repo dense-static path (PR #264): k-NN weight transfer from a donor
rig + `apply_skin.py` assembly, then the repo codec (meshopt +
quantization) to the shipped `model-rigged.glb` files. Donor for
the three re-rigged transformed forms: the Bosconovitch skeleton
(178 joints) carried by `attire1/pre-transform/model.glb` — the same
skeleton as the shipped pre-form and Tekken base, and the skeleton
the T3 animation bank was authored for. Attire 1 + 2 use the k=4
kernel (`knn_transfer.py`); Attire 3 uses the wide smooth kernel
(`knn_smooth.py`, k=64) — on that one the k=4 field aliased across
donor weight creases and tore at the pants hem in pose, the exact
failure knn_smooth's header describes. Target facings were
verified by textured renders of the original GLBs, never assumed:
Attire 1 −90°, Attire 2 −90°, Attire 3 0° (faces +Z as pulled).

Why not the 49-joint template the bases use: a first build of the
four forms on that template (own-attire donors) passed validate.py
and rendered perfectly at rest, but **folded under the game's bank
retarget** in the game's own render path. Controls, same harness,
fresh page per model: the Lane 4 Wowomomo base (template skeleton,
already on main) folds identically; the 178-joint pre-form renders
the bosconovitch stance clean. The defect is the template skeleton
under retarget, not the transfer — so the forms were re-rigged onto
the character's real rig.

## Game-path stance proof (own eyes)

Method: the game's own loader + retarget (`assets.loadModels` /
`createInstance` + `loadT3Clips` / `retargetT3Clips` +
`AnimationMixer.setTime`), bosconovitch `stance` clip at t=0.5,
front + side cameras — the same calls poselab/the fighter make.

Pose measurements, rigged Transformed vs the shipped pre-form
(the game's reference model, same clip):

| model | bones | headAboveHips | toes | facesNegZ | swapLR |
|---|---|---|---|---|---|
| doc-frank-a1 (pre-form, shipped) | 178 | 0.48 | [0.22, 0, 0.98] | false | false |
| doc-frank-big (Attire 1 XL, this PR) | 178 | 0.48 | [0.22, 0, 0.98] | false | false |
| doc-frank-wowomomo-big (this PR) | 178 | 0.48 | [0.22, 0, 0.98] | false | false |
| doc-frank-hood-big (this PR) | 178 | 0.48 | [0.22, 0, 0.98] | false | false |
| doc-frank-frankenstein-big (this PR) | 49 (template build kept — see Attire 4 note below) | — | — | — | — |

Vertex-displacement audit (rest → stance, world space, Attire 1 XL,
981,052 verts): boots band (rest y<0.35, 150,169 verts) p50 0.234 /
p99 0.319 / max 0.33 m, zero verts beyond 0.6 m; the largest
displacements in the body band are the guard hand's legitimate
1.67 m swing. No torn or flying vertices.

Panels (original Tripo GLB at its authored pose beside the rigged
form in the retargeted stance; gate = body integrity — proportions,
bone placement, clean deformation; textures on; not a T-pose):

- `panel-a1-bosco.png` — Attire 1 Transformed
- `panel-a2-bosco.png` — Attire 2 Wowomomo XL
- `panel-a3-bosco.png` — Attire 3 Hood XL

## Attire 4 transformed — kept on the template build (follow-up)

The Bosconovitch re-rig was attempted for Attire 4 the same way
(k=4 and smooth kernels, rest + stance tested in the game path).
The rest pose and the stance skeleton metrics come out right
(headAboveHips 0.48, toes +Z), but the weight field on the
forearms and the back cables streaks under the pose in both
kernels — the model's arms hang into the donor's hip space and
the cable loops float far off the donor surface, so
nearest-surface weights anchor them to the wrong bones. Rather
than ship a form that breaks in motion, Attire 4 transformed
stays on this PR's 49-joint template build (rigged, textured,
wired — the same state as its base) and joins the follow-up
below. A capsule/bone-proximity weight transfer is the fix to
try next; it needs its own lane.

## Known items

- The baked Idle that the 49-joint donor path used to embed is gone:
  the Bosconovitch donor carries no embedded clip and the game never
  plays embedded clips (it retargets bank clips at runtime), so the
  shipped files have `animations: 0` by design. The old baked Idle
  also failed the repo anim_check on the donor itself
  (edge-stretch p99.9 36.8 vs the 2.5 gate) — inherited from the
  template rig, now moot.
- PR #508 note: #508 rotated foot geometry in five static
  originals. Attire 1's post-transform original was untouched by
  #508 ("doc-big was already correct"), so Attire 1 XL is fully
  post-#508. The Attire 2/3/4 XL rigged files carry the pre-#508
  foot geometry of their source originals in the feet only — the
  same state as the already-merged Lane 4 base rigs; in-game feet
  correctness flows through the bank skeleton #508 fixed. A
  geometry refresh of those three files from the post-#508
  originals is a weights-free follow-up (vertex order preserved).
- Follow-up recommended (separate lane): re-rig the Lane 4
  Wowomomo + Frankenstein BASES onto the Bosconovitch skeleton with
  this same path — they fold under bank retarget like the first
  build of the XL forms did.
- No genuine Tripo old-man pre-form exists (registry audit in
  `roster/doc-frank/ATTIRE-SLOTS.md`); Attire 1's pre-form remains
  the reskin-lineage file, at the back of the ladder per the order.
