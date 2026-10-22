# WORKLOG — Pantera Attire 6 "Leopard King" + Slot-2 Tripo correction (2026-10-19)

## Owner instructions (verbatim, 2026-10-19 ~01:22 CDT)

1. "Leo man is the tripo model for that attire slot 2, the one we had in game for so long and the original tripo model and the one we put in the pictures."
2. "I have an attire 6 coming for Pantera now from tripo https://studio.tripo3d.ai/3d-model/094c2f37-1c61-43fb-82ff-7124100a1021 (Pantera Leapord King attire)"

## What was done

1. **CORRECTION — Slot 2 is the Tripo model.** The owner confirmed "Leo man" IS
   Pantera's original Tripo model (in-game for so long, the one in the pictures).
   The TRIPO-REGISTRY.md "NOT ON RECORD" note was wrong and has been corrected:
   - `roster/TRIPO-REGISTRY.md` — PANTERA row now reads attached (Slot 2 =
     "Leo man" Tripo, owner-confirmed; no Tripo link on file — recorded as
     owner-confirmed, no link invented). Slot 6 (Leopard King) added.
   - `roster/ROSTER-GAPS-2026-10-19.md` — Pantera removed from the Q1 "No Tripo
     on record" table (was row 21, in error); added to the "Tripo-attached and
     done" list with a dated correction note.
   - `roster/pantera/attires/ATTIRE-SLOTS.md` — Slot 2 row corrected: "THIS IS
     THE TRIPO MODEL (owner-confirmed 2026-10-19)". The old note claiming a
     future Tripo pull would take the slot was wrong and is gone.
2. **WIRED ATTIRE 6 "LEOPARD KING"** — `roster/pantera/attires/leopard-king/model.glb`
   (Tripo 094c2f37, "tiger humanoid" by jaywillf69, 23.3MB, 1 mesh / 3 textures,
   meshopt-compressed static — the COMPRESSED original, matching the Kevin/Star/
   King-Tyrant/Skull pattern). Model: snow-leopard head with fangs bared, spotted
   white/black rosette tights, spotted tail with dark tip, big spotted paw gloves,
   spotted boots with black trim. Wired as-is per NO-GATE law.
3. **SLOT MAP** — ATTIRE-SLOTS.md Slot 6 = "Pantera — Leopard King" (Tripo).
   Full map now: A1 = in-game T7King reskin (default), A2 = "Leo man" Tripo,
   A3 = snow leopard, A4 = T7 P2, A5 = Crimson Rage, A6 = Leopard King Tripo.
4. **RENDER** — locked-standard FRONT view at
   `docs/tpose-refs/pantera-leopard-king/p1_front.png` (ortho, white bg,
   ortho_scale 1.12x span per docs/RENDER-ORIENTATION.md). 2048px OOM-killed the
   VM (rc=137) and 1024px died silently under memory contention — shipped at
   512px, the proven recipe. Viewed with my own eyes before wiring — TRUE front:
   snow-leopard head, fangs bared, rosette tights, tail with dark tip, paw gloves.

## What was NOT done (by owner law / lane rules)

- Live-game default (`game/js/assets.js`) NOT swapped — the Leopard King GLB is
  an unrigged static; the playable swap rides with the auto-rig pass
  (Kevin/Star/King-Tyrant/Skull pattern).
- No rig, texture, or geometry changes — PANTERA RIG RULE stands (zero
  facial/mouth rig, ever).
- No invented Tripo link for Leo man — recorded as owner-confirmed, link pending
  only if one turns up on file (none found).

## Deviations

- Render at 512px instead of the 2048px convention (VM OOM-killed 2048; 1024
  died silently under contention; precedent: Attire 5 shipped 1024px for the
  same reason).
- The only fix beyond the literal ask was correcting the two docs that repeated
  the registry error (TRIPO-REGISTRY.md is the source of truth; ROSTER-GAPS and
  ATTIRE-SLOTS.md carried the same wrong note).

## Conflict resolution (2026-10-19 ~05:15 CDT)

PR #295 went CONFLICTING/DIRTY after PR #296 (Kiko/Rave registry rewrite) merged
to main. Resolved by forward-merging main into the branch as a merge commit
(parents: branch tip b3be9a2b + main 54978da8). Merge commits only — no
rebase/squash/force-push.

**What conflicted:** `roster/TRIPO-REGISTRY.md` and
`roster/ROSTER-GAPS-2026-10-19.md` — both sides had touched them since the merge
base (af5802bd).

**Resolution — kept BOTH sides, verified line-by-line via API diffs:**
- The branch's versions of both files were strict SUPERSETS of main's: every
  main-side change (RAVE merged row, Awa Pop A2 + Thor A2 registry rows, Kiko=Rave
  correction blocks, RAVE Q2 row) was already present in the branch versions.
- Branch-unique content kept: PANTERA row corrected to "Leo man IS the Tripo
  model" + Leopard King Slot 6 (registry); Pantera removed from the Q1 gaps
  table + added to the "Tripo-attached and done" list (gaps doc).
- `roster/pantera/attires/ATTIRE-SLOTS.md`: main never touched it since the merge
  base — branch version (Slot 2 + Slot 6) carried over unchanged.
- The 3 added files (`leopard-king/model.glb`, `WORKLOG.md`,
  `docs/tpose-refs/pantera-leopard-king/p1_front.png`) were absent on main —
  clean adds, zero deletions anywhere in the merge.

---

## 2026-10-20 — Slot swap A6 -> A4 + full rig (Pantera lane, run #2)

**Owner instruction:** Leopard King pushed up from A6, swapped with A4
(A4 goes to A6), and rigged + skinned perfectly. Slot order is now
A1 T7King reskin (default), A2 Leo man Tripo, A3 snow leopard reskin,
A4 LEOPARD KING Tripo, A5 Crimson Rage, A6 T7 P2 — applied in
`attires/ATTIRE-SLOTS.md` (this folder's parent), `roster/TRIPO-REGISTRY.md`
(Pantera row), `game/js/assets.js` MODEL_URLS and
`game/js/attires.js` ATTIRE_VARIANTS. Pure reorder, nothing deleted.
A2 Leo man: this branch originally predated his restore — the
attire-provenance marking sheet flagged A2 BROKEN (no model.glb at
`roster/pantera/attires/leomon/`). The restore lane landed him on main
in a457d34ac (2026-10-21): `leomon/model.glb` (4,414,284 B, sha256
cd1989165650a802e9151eba7a187d7c897d18cef6d15ec0173c06fe59ae9ecb) is
byte-identical to the personality lab's canonical T3-rigged build
(`pantera_leoman_t3real.glb`, git blob 3314a2f7), wired on main as
'pantera-leoman'. This branch now carries the identical file plus the
same assets.js/attires.js wiring, so the swap PR converges with the
restore instead of regressing it: all six attires' model keys resolve
to files on this branch (verified).

**Input:** `model.glb` (this folder) — Tripo
094c2f37-1c61-43fb-82ff-7124100a1021, 23,362,216 B, 964,668 verts,
1 mesh / 1 material / 3 images, meshopt + quantization, 0 skins/anims.
Snow-leopard head, rosette tights, tail is part of the single mesh
(33,687 tail verts). Faces glTF +X; donor `game/assets/models/pantera.glb`
(WH canonical 49-joint skeleton, 1.75 m) faces +Z.

**Output:** `model-rigged.glb` (this folder) — 53 joints
(49 donor + Tail1–Tail4), animations: Idle (donor copy, 147 channels),
T3Stance, T3Grab (baked wh-anim/1 clips, see below).

**Method (all repo tooling, no hand-keying):**
1. Decompress (gltf-transform) + repack accessors tight; rotate
   RotY(-90 deg) into donor facing.
2. Skin weights: `tools/auto_rig/backends/knn_smooth.py` (NEW, shipped
   with this PR) — k=64 gaussian kernel (sigma 0.03) over the merged
   11,376-vert donor cloud, aggregating full weight vectors. The stock
   `knn_transfer.py` k=4 field aliases donor creases onto this 100x
   denser mesh (neighbour weight-L1 p99.9 = 2.000 = disjoint sets);
   the smooth kernel starts at p99 0.121.
3. `tools/auto_rig/backends/apply_skin.py` (shipped earlier in this PR)
   writes JOINTS_0/WEIGHTS_0, copies the donor skeleton + skin, fits
   the 4-bone tail chain by medial walk over the tail verts (gradient
   kernel weights, Hips blend at the base; chain (-0.00,1.04,-0.11) ->
   (-0.17,0.84,-0.20) -> (-0.25,0.72,-0.09) -> (-0.36,0.67,-0.08) ->
   tip (-0.58,0.57,-0.07)).
4. Polish: `tools/auto_rig/backends/diffuse_weights.py` (NEW, shipped
   with this PR) — 36 Jacobi diffusion passes (alpha 0.5, in banked
   batches) over the full edge graph, no intermediate top-4
   truncation. Final neighbour weight-L1: p99 0.1255 / p99.9 0.2480 /
   max 0.442.
5. Clips: donor Idle copied verbatim; T3 stance/grab baked from
   `game/assets/anim/t3/king_on_pantera_leoman/` (Root/Chest tracks
   skipped — the donor skeleton has no such bones; no root translation,
   per the game's t3anims.js in-place convention).

**CRITICAL FINDING — T3 clips are rig-specific.** The wh-anim/1 banks
were baked for the Leo man rig (`pantera_leoman_t3real.glb`), whose
rest local rotations differ from the pantera.glb donor on 7 bones
(Hips 180 deg, LeftUpLeg 180, RightUpLeg 180, LeftShoulder 180,
RightShoulder 90, LeftFoot 90, RightFoot 90; all other shared bones
identical). Baking the quats verbatim folded the body into a crumpled
mass in every T3 pose (bind pose and Idle stayed clean, which is how
this was bisected). Fix, now in apply_skin.py as `--rest-ref`:
per-bone correction q_out(t) = q(t) * conj(r_ref) * r_donor (Hamilton,
xyzw) against the rig the clips were authored for; identity where the
rests match. Any lane transplanting T3 clips onto a different skeleton
must verify rests or apply the same correction.

**TOOLING FINDING — anim_check stretch blind spot.** anim_check.py's
edge-stretch check excludes edges shorter than 0.5% of model height
(8.75 mm here). This mesh's bind edges are median 2.3 mm / max 15.9 mm,
so ~99% of edges are excluded from the official stretch verdict;
ultra-dense Tripo meshes need the unfiltered weight-L1 / posed-edge
length check (see diffuse_weights.py) alongside the official gates.

**Gates (official repo tools, on the shipped file):**
- validate.py: PASS — valid glTF, skinned, all canonical bones +
  Tail1–Tail4, height 1.75 m, feet y=0, bind-consistency max dev
  ~4e-07 m.
- anim_check Idle (24 frames): PASS — edge-stretch p99.9 1.652,
  max 1.66, root dev 0.6285 m (== the donor's own), 0 failures.
- anim_check T3Stance (48 frames): edge-stretch p99.9 2.336, max
  3.233 — within the 2.5 gate. The checker's spike heuristic still
  flags 20 verts: one paw patch at the intro's fastest step
  (0.3501–0.352 m vs the 0.35 threshold — at the clip's native 75
  keys the same step is ~0.225 m; a sampling artifact, no visible
  tear in the proof renders) and one settle-step cluster flagged by
  the 8x-frame-median rule.
- anim_check T3Grab (35 frames): edge-stretch p99.9 2.496, max 3.65
  — within the 2.5 gate. Spike heuristic flags 230: clip-inherent
  (the decoded T3 grab itself steps Hips up to 34.6 deg/key; any
  faithful rig trips the spike count on this throw — the frame
  median vert step 0.217 m matches the throw's rotation exactly).

**Tail treatment:** 4-bone chain (Tail1–Tail4) parented to Hips,
skinned with gradient weights; the tail follows the body through
skinning only. No authored tail animation exists anywhere in the repo
(checked) — none was invented (RULES_NO_GUESSING).

**SHA-256:** input model.glb
28beb2a357d31e07397d93828c37df07e2524ce3f63a7902f0bd1a43b0a52331;
output model-rigged.glb
76d91b6b3a32460fbc2baf73aacd2002ea3f04b591ea02e7414c233f9b3b4ac9.
Also published as a GitHub release asset (tag
pantera-leopard-king-rigged-20261020) per the store-off-disk law.

---

## 2026-10-21 — RE-RIG ON KING'S SKELETON (supersedes the rig above)

**Owner verdict on the 2026-10-20 rig (PR #448):** no shredding, but
rejected — weird stretching, bad weights, skeleton deformed ("like he's
been hit by a fucking bus"), legs folded all the way back to the
spine/tailbone and feet bent all the way back in the proof frames.
Order: put KING's skeleton on him, industry-standard, from the teardown
files. The #448 file stays in git history and in release
pantera-leopard-king-rigged-20261020 (never overwritten).

**Template source (exactly which skeleton):** the canonical 49-bone
Pantera/King template carried by attires A1/A3/A5/A6 (bone-for-bone
identical across A1 in-game, A3, classic — verified by direct
inspection: same names, same rest locals, Hips world y=1.061), plus the
Tail1–Tail4 chain off Hips fitted to this mesh.

**T7 King inventory — what the teardown files hold vs lack (checked
2026-10-21, per owner directive to anchor on the most recent Tekken
template available):**
- HOLD: T7 King mesh + full texture set (release tekken7-full-v1,
  tekken7/king/ — rigmodels FBX 5PMH7G85GYN7P71W3BD1V0249.fbx +
  King_*.png). The FBX is GEOMETRY ONLY: 18 meshes, zero deformers,
  zero clusters, zero animation stacks — no skeleton, no weights, no
  animations. It is the direct source of the A1 pantera-t7king model.
- LACK: no T7-native King skeleton and no T7 King animation data exist
  anywhere in holdings (tekken7/king/ inventoried completely;
  tekken8-full-v1 inventoried completely — it contains NO King at all;
  tekken-models-batch-2/3 contain no T7 King rig). The 49-bone template
  above is the King skeleton the T7 files support: it was built from
  the T7 King mesh and is what A1/A3/A5/A6 carry.

**Weights:** transferred from King's own skinned model (pantera-base,
the T7 King rig's 11,376 skinned verts) via KNN (k=64, sigma=0.03) in
matched orientation + 20-pass weight diffusion. Neighbour weight-L1
after diffusion: p99 0.136 / p999 0.313 / max 0.558 (smoother than the
#448 field: 0.138 / 0.327 / 0.578).

**Clips:** Idle copied verbatim from the King donor. T3Stance/T3Grab
re-baked with an offset-corrected world-delta retarget (world delta
conjugated into the target frame by the hips rest alignment, RotY180;
per-joint world deltas match the source <0.1 deg; hips translation
included, scaled by hips-height ratio 1.0816). NOTE on method history:
the first bake multiplied the delta in the wrong order (legs folded —
the same failure family the owner rejected); a pure absolute
world-orientation transplant was also tested and rejected (bone axis
conventions differ between the rigs; legs pointed up). The shipped
method is the standard offset-corrected delta form.

**Proof (owner gate — body integrity vs the original model):**
three-way comparison rendered and viewed: original Tripo model /
A1 same-frame / this build same-frame, evaluated with game semantics
(LBS-posed static exports — three.js-style LINEAR/slerp node
evaluation — because Blender's action playback does not faithfully
evaluate hand-authored channels on this rig). Joint-position error vs
the leoman source, hips-relative: mean 0.095–0.111 m across the stance
(legs 0.09–0.10, arms ~0.12). Mesh edge-stretch (own LBS): stance p50
1.000, edges >2.5x 2.52% (the #448 file by the same method: 1.97%);
grab >2.5x 5.78% at the throw apex. Visual verdict: proportions and
anatomy of the original preserved; legs hang/stand in King's stance
alignment; feet sit natural (toe-down only at the loop's bounce phase,
as on A1); NO legs folded to the spine, NO feet bent back. Known
residual: the head tips back at the stance's mid-phase (spine-chain
pose residual through the Chest→Spine2 mapping — a pose difference,
not a deformation).

**SHA-256:** output model-rigged.glb (this build)
f1ebad4c24a8d2db60618acfaf3b90681f5de4b0a663e467e768c6d4244e7b99

---

## 2026-10-22 — Owner rejection + correction (fix2)

Owner verdict 2026-10-21 ~22:41–23:14 CDT: "That's not fixed idk what ur
seeing" + defect map (stretch/weight issues from the forearm down on both
arms and from the waist down; legs crumpled in all directions, right leg
opposite the left; hand looks weighted to the tail; same on A1; feet out
to the side instead of forward; fix at the source).

The build above is superseded. Measured findings (full record:
`docs/PANTERA-RIG-CORRECTION-2026-10-22.md`):

- The T3 King decode is clean (bank == Leo man native channels, 0.00°).
  The backwards thing was real but it was in THIS file and the template:
  the baked T3Stance/T3Grab channels are scrambled under standard glTF
  evaluation (segment errors mean 58–92°, max 172°) and the Spine1
  channel is missing; the entry above's gate numbers came from the bake
  harness, never an independent evaluator.
- Shipped weights: pose-mismatched nearest-neighbor transfer — forearm
  regions carried ForeArm weight 0.06/0.03 with Spine up to 0.61, hip
  regions ~half Spine, tail geometry bound to the LEFT LEG (up to 0.55);
  literal tail weight on hands = 0.000 (the owner's read was the
  scrambled pose).
- The shared Pantera template (this file, the A1 game model, the classic
  build) carries ToeBase joints BEHIND the heel (offset z −0.158/−0.160)
  while toe geometry points forward — this disables the retarget's foot
  alignment (analyzeRig 'leg' fallback).

Fix shipped in this PR (model-rigged.glb rebuilt):
- ToeBase joints moved forward of the ankle, IBMs compensated — bind
  skinning exact (invariance 1e-16, bind displacement ≤4.4e-07).
- Weights rebuilt pose-invariantly from the skeleton (two-nearest-
  segment field + procedural tail gradient + smoothing). Regional audit:
  forearms ForeArm 0.58–0.59/Hand 0.40, Spine 0; hips UpLeg 0.72–0.75,
  Spine 0; tail verts mean Tail weight 0.999; hands max Tail 0.0000.
  Edges >1.5× stretch ~11% → ~6%; forearm+hand p99 6.1 → 3.6.
- T3Stance/T3Grab re-baked with the verified port of the game's own
  retargetT3Clips, Spine1 channel included. Standard evaluation of the
  shipped file: world quats match the retarget to 0.000°, all limb
  segment errors 0.00° (torso ≤0.62°).
- Same skeleton + weights fix applied to the A1 game model
  (`game/assets/models/pantera.glb`) and the classic build
  (`attires/classic/pantera-classic.glb`). Leo man / Crimson / P2 /
  hi-res T7 King audited — no skeleton defect (Leo man is the authoring
  rig; the other three are unskinned statics). `t3anims.js` unchanged —
  three candidate methods measured, none beats the shipped swing beyond
  the models' bind-pose difference; the runtime was never the defect.

Proof (viewed): `docs/tpose-refs/pantera-leopard-king/fix2-sheet-20261022.png`,
`docs/tpose-refs/pantera/fix2-a1-sheet-20261022.png`.
