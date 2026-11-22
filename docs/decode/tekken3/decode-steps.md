# Tekken 3 — decode steps

Step-by-step T3 decode, so it is reproducible. All paths are repo-relative
unless marked as the lane workdir. Tools: see `../tools.md`.

## 0. Prerequisites

- Owner's disc teardown in `teardown/tekken3/`:
  `disc/files/TEKKEN3/SLUS_004.02`, `animations/divmot03_king.bin`
  (+ `divmot99_common.bin`), `models/king95/king95.kmd`,
  `renders/pose-check/king_stance75.obj`.
- n0madic research files on `T3REMAKE_RESEARCH`
  (`tools/research/motion.py`, `kmd.py`, `pose.py` from
  n0madic/Tekken3Remake master).
- Bake tools in-repo: `lab/tools/t3_motion_bake.py`,
  `tools/anim/t3_row_bake.py`, `tools/anim/t3_reaction_bake.py`,
  `tools/anim/t3_reaction_tables.py`, `tools/anim/t3_bank_skeleton.py`.

## 1. Verify the sources (SHA-256)

Every pack records its input SHAs in its `sha256` field. The King inputs:

| File | sha256 |
|---|---|
| `teardown/tekken3/models/king95/king95.kmd` | `3b280fa477eff73cf76f1729e6c34366135e5d5e988a1a713abce49f1bde6a4c` |
| `teardown/tekken3/animations/divmot03_king.bin` | `8ae24919a89ac81adc6d34f1ef35cbb3ccafd19c55dafe820c923bbd638da899` |
| `teardown/tekken3/disc/files/TEKKEN3/SLUS_004.02` | `c84a320e323efda740547589608fab6500ed5c367d4486d5c3b89afe2eeb594f` |
| `game/assets/models/pantera.glb` (shipped rig) | `7085ce665a6e1dcebb40af4783a1f6661669fb98379b1310871e74f82d736ab6` |

If any SHA differs, stop — the decode inputs changed and the packs must be
re-derived, not patched.

## 2. Decode one clip (smoke test)

```sh
export T3REMAKE_RESEARCH=<path-to>/tools/research
python3 lab/tools/t3_motion_bake.py game/assets/models/pantera.glb \
  /tmp/pantera_smoke.glb --bank king --clips t3_stance=0 \
  --json-dir /tmp/smoke-json
```

This runs `T3Space` + `sample_clip` (pose_assemble bit-exact decode) +
`retarget` onto the target rig, and writes the `wh-anim/1` JSON next to the
GLB. Check: slot `0x0`, move_row 523, stream_frames 150, 75 frames, fps 30.
The JSON `bones` list is the *target rig's* bone names (49 Mixamo names for
`pantera.glb`) — the runtime needs the canonical-22 re-expression (step 5),
not these raw Mixamo-space tracks.

## 3. Bake the move rows

```sh
python3 tools/anim/t3_row_bake.py --bank king --rows <comma-separated row keys> \
  --out <rows.pack.json>
```

`--rows` overrides the referenced-row set (which needs
`game/assets/movesets/*.json`); the King pack has 256 rows, 0 missing.
`TARGET_GLB["king"]` must point at the rig the pack is baked onto
(`game/assets/models/pantera.glb` for the shipped rig). Each row records
`slot`, `move_row`, `stream_frames`, `n`, `used_by`, `q` (base64 int16
`[n][bones][4]`, `q*32767`, w>=0 canonical sign), `rx`/`ry`/`rz` (root in
mm ×1000).

## 4. Bake the reactions

```sh
python3 tools/anim/t3_reaction_bake.py --bank king_on_pantera_leoman
```

Plan comes from `tools/anim/t3_reaction_tables.py` `bank_plan` (568 rows,
0 missing). Each row records `slot`, `move_row`, `src` (own/common),
`stream_frames`, `n`, `roles`, `yaw0` (frame-0 Hips yaw in the heading
frame, rounded to 5 dp), `q`, `rx`/`ry`/`rz`, and `ax`/`ay`/`az` (decoded
root channels 0–2, mm — rig-independent). Header `anchor_mm_to_rig_m` is
`round(scale / 1000, 9)` where `scale = rig.hipsY / T3-stance-hip`
(0.898321216 for the shipped rig → 0.000898321).

Two known tool limits for a Mixamo target (documented, not silently
worked around):

- `heading_yaw` returns `None` for Mixamo-facing rigs. The correct value
  is the F-aware heading yaw; verified on 28 sampled slots (worst
  |diff| 5e-06 rad) to equal `wrap(yaw0_old + pi)`.
- The CANON22 re-encode looks up tracks by canonical name, so `Chest`
  comes out identity (chest motion lives on the Mixamo `Spine2` joint).
  Map canonical names through `rig.by_canon` (Chest←Spine2) instead.

## 5. Re-express Mixamo-space output as the canonical bank

The runtime (`game/js/t3anims.js` `retargetT3Clips`) consumes canonical-22
identity-rest locals with Y-up `root_t`, composed against `skeleton.json`.
A direct Mixamo-space bake is runtime-broken (bind-relative locals, Z-up
parent-space `root_t`, 49 bones). The re-expression (Lane X1,
`convert_to_canonical.py` in the lane workdir — the method, not a
hand-tooling step):

- Recover `D_old` per bone by FK of the old pack's canonical locals
  (exact: the old rig's `wrest` is identity, verified).
- `D_new = F @ D_old @ S_old.T @ F.T @ S_new` per core bone
  (`F = diag(-1,1,-1)` facing flip; `S` from the tool's own `swing()` on
  the tool's own `sp` dicts), Spine/Spine1/Neck/ToeBase re-derived exactly
  as `retarget()` derives them (slerp/inherit), Root = identity.
- `root_t_new = [0, 1.06130751, 0] + (scale_new/scale_old) * F @ (root_t_old - [0, 0.9805, 0])`.
- Head is **not** carried from the old pack (its track deviates from the
  decode by a constant 50.908° — see `tekken3/scramble.md` and the per-file
  doc §2). Head `D` is re-derived from the T3 source via the slot path:
  `sample_pose` → slot rotations → part world rotation → `G` →
  `D_new[Head] = Y_new @ G_Head @ F.T`. Slot-path `G` matches the tool's
  kabsch `G` to ≤0.008° for Head (measured on the stance clip).
- `skeleton.json` = canonical-bone world rest positions of the shipped
  rig (Root rest = Hips rest). `t3_bank_skeleton.py` cannot build it for a
  Mixamo rig (it exits on non-identity rest rotations).
- `hit_frames.json` is rig-independent (no scale fields) — copied
  byte-identical, never regenerated.

## 6. Verify (same method before and after)

- **Runtime-forward round-trip:** pose the new canonical clips through a
  reimplementation of `retargetT3Clips` (G from canonical locals +
  skeleton → D → W on the shipped rig) and compare against the direct-tool
  Mixamo-space outputs (smoke clip + direct 2-row pack). Target: max quat
  angle < 0.1°, max root error < 1 mm. (Lane X1: root 0.0000 mm; 48/49
  bones < 0.5° before the Head fix — see the per-file doc §6 for the
  post-fix numbers.)
- **Counts:** 32 clips (same slots/move_rows/stream_frames/frame counts),
  256 rows / 0 missing, 568 reactions / 0 missing.
- **Pack invariants:** `ax`/`ay`/`az` byte-identical to the old pack
  (rig-independent decode); `roles` identical; `used_by` identical;
  `yaw0_new = wrap(yaw0_old + pi)` (validated on 28 slots, worst 5e-06 rad);
  reactions Chest track non-identity (chest motion preserved).
- **Numbers:** pack hip 0.9805 m → 1.06130751 m (shipped hip, exact);
  `anchor_mm_to_rig_m` 0.000829923 → 0.000898321 (+8.24%);
  pair-geometry error 8.24% → 0% by construction.
- **Slot-path audit:** every motion unit (856: 32 clips + 256 rows +
  568 reactions) checked bone-by-bone against the decode (`Y @ G @ S_old`,
  slot rotations, no vert assembly). Flag threshold 2° (slot-vs-kabsch
  noise ≤ 0.44°, Head noise ≤ 0.008°).

## 7. Ship

- PR: branch → PR → merge only. Instruction-gate PR body (see the lane
  brief). Post-merge read-back of EVERY payload file from main (sha256
  byte-identical) before the merge is reported done.
- The 1.45 m throw-connect gate is a *game* rule: the re-bake does not
  close it (PR #1781 fixed the gate). Never claim otherwise.
