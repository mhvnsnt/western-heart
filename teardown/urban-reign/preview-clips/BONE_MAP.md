# Urban Reign — Bone Map & FK Convention

Converter: `ur_to_bannon.py` in this directory. Proven 2026-11-21.
Clip format: VPW2 v1.3 / KoC2 v1.2 converter clips
`{dur, keys: [{t, root: [x, z], pose: {joint: [x, y, z]}}]}`,
clip frame x=forward, y=up, z=left, meters, 60 fps.

## 1. The UR skeleton (21 joints)

Source: western-heart `teardown/urban-reign/tools/ur_skin_bake.py`
(`MB2NODE`, `PARENT_GAME`) + `rigging-reference/urban-reign-hand-arm.md`
(49 decoded Japanese bone names). Motion bone 0 is the root position
track (KOSHI). Rows in `rows.pack.json` are per GLB node 0..20, in
`MB2NODE` order (motion bone b -> GLB node MB2NODE[b]).

Game hierarchy (`PARENT_GAME`):

```
12 KOSHI (pelvis, root)
├─ 0 MUNE1 (chest low)
│  └─ 1 MUNE2 (chest high)
│     ├─ 2 KUBI (neck) ── 3 ATAMA (head)
│     ├─ 4 SAKOTSU_L (collarbone) ── 5 KATA_L (shoulder)
│     │  └─ 6 UDE_L (elbow) ── 7 TE_L (hand, terminal)
│     └─ 8 SAKOTSU_R ── 9 KATA_R ── 10 UDE_R ── 11 TE_R
├─ 13 MOMO_L (thigh) ── 14 HIZA_L (knee) ── 15 ASHI_L (ankle) ── 16 TSUMASAKI_L (toe)
└─ 17 MOMO_R ── 18 HIZA_R ── 19 ASHI_R ── 20 TSUMASAKI_R
```

Notes:
- Chain A (nodes 4–7, 13–16) is anatomical LEFT — verified: in the
  FK'd stance its shoulder lands at +z (clip z = left), and the guard
  reads as a textbook stance (lead left hand forward).
- There are NO finger bones: UR hands are mitten-style; TE is terminal.
  There is no separate forearm joint: UDE→TE spans elbow→wrist, so the
  elbow bend and wrist rotation are combined in TE's rotation.
- The GLB node hierarchy is NOT anatomical (e.g. nodes 14–20 are all
  children of node 3 in the GLB). Always use PARENT_GAME, never the
  GLB parents, for FK. (The GLB parents matter only for qbind recovery,
  §3.)

## 2. Bone map (UR node -> clip joint)

| UR node | Japanese | Clip joint | Notes |
|---|---|---|---|
| 12 | KOSHI | pelvis | root; translation from root_t, rotation bind-only (§3) |
| 0 | MUNE1 | spineLow | |
| 1 | MUNE2 | spineMid + chest | chest is a virtual child of spineMid (REST offset), same rotation — UR has 2 spine joints, the clip needs 3 (same as VPW2's spineMid+chest sharing UpperBody) |
| 2 | KUBI | neck | |
| 3 | ATAMA | head | |
| 4 / 8 | SAKOTSU | clavL / clavR | |
| 5 / 9 | KATA | shL / shR | |
| 6 / 10 | UDE | elL / elR | elbow = UDE joint position |
| 7 / 11 | TE | wrL / wrR + haL/R + fiL/R | ha/fi are rigid extensions of the wrist (REST offsets in the wrist frame); finger curl ~0, honest — UR has no finger articulation |
| 13 / 17 | MOMO | hipL / hipR | |
| 14 / 18 | HIZA | knL / knR | |
| 15 / 19 | ASHI | ankL / ankR + ftL/R | ftL/R (sole) is a virtual child of the ankle (REST offset) |
| 16 / 20 | TSUMASAKI | toL / toR | toe joint position (driver uses it for foot direction only) |

NO BONE LIMITING: every joint the UR motion drives moves in the output —
both spine joints, both clavicles, wrists, ankles, toes. Nothing the
source has is dropped; nothing the source lacks is invented (no finger
curl, no third spine joint).

## 3. FK convention (proven)

- **Euler recovery.** Packed quats are `q_bindlocal × q_euler`, where
  `q_bindlocal` is the bind-local rotation under the GLB hierarchy
  (from `W = inv(IBM)` of char001.glb). The delta is recovered as
  `qe = qbind_glb^-1 × q_packed`. **Validated to 0.002° RMS**: the
  recovered root qe matches `eul2mat(root position)` exactly across all
  frames of 3 clips — because the packer fed the root POSITION track
  through the Euler path. Consequence: the packed root quat is garbage
  (50–68° of spurious rotation) and is DISCARDED; the root keeps its
  bind rotation (as in `ur_skin_bake.bake`). Whether the true motion
  rotates the pelvis (flips/throws) is therefore NOT captured — the
  pelvis orientation comes from the FK chain, not from a root rotation.
  (Open item: if a flip/throw proof shows the pelvis failing to rotate,
  the root rotation must be sourced from the .gyu directly.)
- **FK chain.** `R_world(n) = R_world(parent) @ Lbind_game(n) @ R(qe)`,
  over PARENT_GAME, with `Lbind_game` rotations from W. Positions use
  Bannon REST offsets (see §4), converted into each parent's bind frame.
- **Axis map (GLB → clip):** `clip = (glb_x, -glb_z, -glb_y)`.
  Proven by the stance test (§5) against 4 other candidate maps.
- **Root motion.** `root_t` (GLB) → clip root `[x, z]` + pelvis height
  (`REST pelvis + root_clip_y`). The pose is root-relative (pelvis
  x/z = 0; all joints minus root x/z). Per-frame pair lift (VPW2-style):
  `lift = max(0, -min_y)` over non-tip joints, so feet never sink below
  a flat floor. For a two-person pair, `--pair` re-lifts with a SHARED
  lift and stages the receiver 0.65 m in front (the driver's fallback;
  the starting grapple distance is not in the data — staging
  assumption, flagged in the clip `_ur` block).

## 4. Proportions (REST)

The FK uses the target rig's proportions — `rest_mixamo.json`
(build_rest.py measurement of BANNON_repaired.glb, pelvis 1.085 m),
copied into this directory. The VPW2 converter file's hardcoded REST
(pelvis 0.90) gave clip/rig ratios 1.57–2.35 against the Bannon GLB
(the squash defect class Mars flagged 2026-11-21); the measured Mixamo
REST gives ratios IDENTICAL to the proven VPW2 v1.3 mixamo clips
(Foot 2.07/2.01, Head/Neck 1.89, Shoulder 1.41 — the remaining ratios
are direction-only swing segments, inherent to the Mixamo REST).

Why not the UR skeleton's own bone lengths: the UR bind skeleton is NOT
recoverable from the staged GLB — W-derived bind translations are
incoherent (zero-length bones, asymmetric limbs, nodes clustered in a
4 cm ball; FK from them gives no standing human in any hypothesis), and
the raw mesh is in per-part local frames, not a posed body. The preview
plays on the Bannon rig, and the driver requires clip/rig ratios ~1.00,
so the converter uses the target rig's proportions — the same approach
as the VPW2/KoC2 converters. The UR ROTATIONS are preserved exactly;
only the bone lengths are the target rig's.

## 5. Validation

- **Root recovery:** 0.002° RMS (see §3).
- **Stance test (H1 FK):** 791/829 general-bank motions FK into a sane
  stance at frame 0 (pelvis 1.085, head ~1.68, ankles ~0.12 with the
  Mixamo REST). ur_m001 reads as a textbook fighting guard (lead left
  hand forward at (0.39, 1.22, 0.15), rear right back, knees bent).
  The 38 f0-unsane motions start mid-action (jumps/throws/ground).
- **H2 (qbind_game) and H0 (packed direct) both fail** the same test
  (head ~1.0, ankles 0.35–1.28) — H1 is the unique correct convention.
- **Exporter CALIB:** R_bt exact, R_cm max deviation 0.000001,
  q_clip vs apply() max diff 0.0000°. Ratios identical to proven VPW2.
- **IK clamps:** 0/516 chain-frames on the golemnage pair render.
- **Renders:** golemnage pair at f1/f49/f97/f129 in `shots/` — two
  coherent figures in fighting stances, correct proportions, feet on
  the floor, grapple distance reads.

## 6. Known limits / honest gaps

- **136/829 clips have a corrupt root decode in the staging**
  (frame-to-frame root jumps of 0.5–11.6 m — physically impossible;
  the type-14 range decode fails for those tracks). Their rotations
  are fine; the root is zeroed (motion plays in place) and the clip
  is flagged `root_corrupt: true` in `_ur` (with `root_max_jump_m`).
  Breakdown: normal 41, 30frame 49, weapon 46.
- **Root rotation is bind-only** (see §3) — pelvis orientation in
  flips/throws comes from the chain, not from a root rotation track.
- **_f/_y semantics unconfirmed** in teardown docs: _f is treated as
  P1 (attacker) and _y as P2 (receiver) by fighting-game convention.
  Only one _f/_y pair exists in the general banks (golemnage1).
- **Chest shares MUNE2's rotation; ha/fi are rigid wrist extensions**
  (see §2) — honest consequences of UR having 2 spine joints and no
  finger bones, not invented motion.
- **pmot banks (1,151 moves) are NOT decoded locally.** Only 5 pmot
  clips are proven identical to general-bank motions (see
  `ur_move_map.json`). Decoding the 31 pmot .ppk banks needs the ELF
  range-decoder tables (SLUS_212.09, not in the repo) or the
  street-reign GLBs with embedded clips (location unknown — index
  lists bare filenames; the western-heart char GLBs are 269 KB
  without animations). The 5 no-bank records (cbco_screw_r,
  moco_d_jumpk_f/_y1/_y2, moco_doubleairk_f) have no source bank in
  the shipped disc at all — emulator capture only.
- **41 proxy-only fighters** (no native animation) can only use
  general-pool motions.
