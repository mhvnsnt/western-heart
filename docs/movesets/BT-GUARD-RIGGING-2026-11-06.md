# BT-guard rigging — DXMMII extra arms + Zen tentacle chains (2026-11-06)

Owner order: **"We have to rig DXMMII arms extras and zens tentacles in his tentacle forms"**

Follow-up to BT-SYSTEM-FIX-2026-11-06.md: the BT-guard exception is
data-driven (a fighter qualifies only when its in-game model carries
more than one arm pair — `tools/anatomy/bt_guard_arm_scan.py`,
`game/js/bt-guard.js`, re-derived by `test/back-turned.test.mjs`).
Chatur qualified from her rig; DXMMII and Zen did not, because their
extra limbs were not arm chains in the shipped models. This change
rigs them in — no `charData.btGuard` overrides, no fabricated flags.

## DXMMII — attire1 (`roster/dxmmii/attires/attire1/model-rigged.glb`)

**The geometry was already there.** The fused source mesh (1,317,703
verts) carries the extra arm pair as two detached vertex islands
floating above/behind the head (150,200 + 140,471 verts — the same two
assemblies the limb-system extracted as `tools/limb-system/dxmmii/
viz/extra_arm_L.glb` / `extra_arm_R.glb`). In the shipped rig those
verts were smeared across breast / arm-segment bones, so the pair
could not articulate and started no chain. Canon: DXMMII's arms are
retractable/detachable and the floating pair is its gyro-stance
system — detached in bind pose is the correct rest state.

Method (automatic, no manual weight painting — pipeline rules):

1. Islands isolated by voxel connectivity in skeleton space (exactly
   3 clusters: body + one arm per side).
2. A 4-joint chain per arm (Shoulder2 → Arm2 → ForeArm2 → Hand2)
   placed on the arm's own geometry: slice centroids along the arm's
   principal axis at arc fractions 0.02 / 0.34 / 0.66 / 0.97. Roots
   parented to **Spine2** (torso, not an arm bone); identity local
   rotations.
3. Skinning generated algorithmically: each island vert's weights are
   a linear gradient over the chain by its arc-length projection onto
   the chain polyline (top-4, normalized) — the same class of
   automatic transfer as `tools/rig_repair/transfer_weights.py`
   (data-derived, no hand edits).
4. File surgery is append-only: existing 73 joints keep their slots,
   streams and bind matrices byte-exact; the 8 new joints, their
   inverse bind matrices (built in the file's own bind convention,
   `W · IBM = S` for every joint), and the replacement JOINTS_0 /
   WEIGHTS_0 streams are appended uncompressed. All other chunks —
   geometry, textures, the embedded CMU clip — are untouched.

Verification on the written file:

- Arm scan: **4 chains** (`LeftShoulder`, `RightShoulder`,
  `LeftShoulder2`, `RightShoulder2`) → multi-arm.
- Skin-matrix constancy: max |SM_j − S| = 2.5e-6 across all 81
  joints; bind-pose reproduction over all 1,317,703 verts: **max
  error 1.1e-6** (the model renders identically at rest).
- Articulation: rotating `RightForeArm2` +40° moves only the right
  extra arm (mean 0.036 / max 0.169 skeleton units); body and left
  arm displacement exactly 0.

### DXMMII models where the geometry genuinely does not exist

- **Patchwork-DJ** (`roster/dxmmii/attires/patchwork-dj/`) and its
  twin `game/assets/models/dxmmii.glb`: Mokujin-family multipart
  bodies (21 material-panel meshes, 4,443 verts). Per-mesh bounds and
  cluster analysis show a standard two-arm humanoid only — **no
  extra-arm geometry exists in these models or their source**, so
  there is nothing to rig without fabricating geometry. They stay
  documented negatives, and the `dxmmii-patchwork` transform stage
  stays BT-guard-null.
- **Attire2** (`roster/dxmmii/attires/attire2/model.glb`, blockhead
  crash-dummy Tripo): a clean two-arm T-pose, **no extra-arm
  geometry**, and unrigged (no skeleton). Out of scope for this order.

## Zen — tentacle form (`roster/zen/tentacle/model-rigged.glb`)

The tentacle form carries 12 five-joint tentacle chains (T0–T11).
Five are rooted outside the arms — T1/T11 at `LeftUpLeg`, T2/T3 at
`LeftLeg`, T10 at `Head`. Those five were renamed into arm-chain form
(**T#_UpperArm** roots, **T#_Hand** tip effectors; mid-chain names
unchanged), which is exactly the structure the detector reads. The
edit touches node names only: **the BIN chunk is byte-identical**
(sha256-verified), all 109 joints, skinning, and both embedded clips
(ZEN_BUST_OUT, ZEN_IDLE — channels address nodes by index) are
untouched, so his clips sample exactly as before.

The seven arm-rooted chains (T0/T4/T9 off the left thumb chain, T8 off
`LeftArm`, T6 off `LeftShoulder`, T5/T7 off `RightShoulder`) were
**not** re-parented: moving their roots to the torso would re-pose
every frame of the bound clips. They stay spring tentacles.

Result: **7 chain roots** (humanoid pair + 5 tentacle arm chains) →
Zen qualifies in his tentacle form, which is the form this fighter
entry fights in (`zen` → TENTACLE MANIFESTATION transform chain in
`game/js/roster-full.js`).

**Oversoul was deliberately not converted**: by canon its body
tentacles are clothing imagery (only the combined form manifests real
ones), and its single torso-rooted chain (O6) belongs to the spirit
head entity, not to Zen. Attire1 and spirit are unchanged negatives.

## Scan results (tools/anatomy/bt_guard_arm_scan.py)

| model | before | after |
|---|---|---|
| chatur attire1 (control) | 4 — qualifies | 4 — qualifies (untouched) |
| dxmmii attire1 | 2 | **4 — qualifies** |
| dxmmii patchwork / game-assets | 2 | 2 (no extra-arm geometry exists) |
| zen tentacle | 2 | **7 — qualifies** |
| zen attire1 / oversoul / spirit | 2 / 2 / 0 | unchanged |

## Proof stills

`docs/proof/2026-11-06/bt-guard-rigging/` — textured renders (three.js
in headless Chromium, same camera per pair):

- `dxmmii-attire1-before.png` / `dxmmii-attire1-after.png` — bind
  pose, identical framing: no visual change at rest (the extra pair
  floats above the head in both, as canon has it).
- `dxmmii-attire1-after-elbow-bend.png` — the new chains articulated
  (ForeArm2/Arm2 bent): the extra arms bend at their own elbows while
  the body holds its pose — impossible before this rigging.
- `zen-tentacle-before.png` / `zen-tentacle-after.png` — same
  ZEN_IDLE frame: the rename changes structure, not a single vertex.
