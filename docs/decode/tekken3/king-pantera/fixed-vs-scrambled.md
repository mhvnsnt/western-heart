# King (Tekken 3) on Pantera — fixed vs scrambled

Re-bake of `game/assets/anim/t3/king_on_pantera_leoman/` onto the shipped
`game/assets/models/pantera.glb`. Lane X1, 2026-11-21.

## 1. What was fixed

The King Tekken 3 animation pack was baked onto the wrong rig. The pack
carried the old lab rig's hip height (0.9805 m) while the game ships a
different rig (`game/assets/models/pantera.glb`, hip 1.06130751 m). Every
throw-pair anchor in the reactions pack was therefore wrong by 8.24%
(pair-geometry error), because `anchor_mm_to_rig_m` belonged to the old rig.

This PR re-bakes the same verified decoded T3 motion onto the shipped rig:

- 32 clips (`t3_*.json`) — same slots, move rows, stream frames, frame
  counts; new root heights and rotations for the shipped rig.
- `rows.pack.json` — 256 rows, 0 missing; same keys, same `used_by`.
- `reactions.pack.json` — 568 rows, 0 missing; same roles, same decoded
  anchor channels; `anchor_mm_to_rig_m` 0.000829923 → 0.000898321.
- `skeleton.json` — canonical-bone rest positions of the shipped rig.
- `hit_frames.json` — **unchanged** (rig-independent moveset data; no
  scale fields). Not in this PR.

A second defect found while verifying: the old clips/rows **Head track
does not match the decode** — it deviates from the tool's retarget of the
decoded head-part globals by a constant 50.91° on every frame (all 32 clips
+ 255 of 256 rows). The re-bake re-derives Head from the T3 source instead
of carrying the old Head forward (§2, §5).

## 2. How scrambled

This was a **bake defect, not a decode scramble**. The T3 decode is clean
and solved in-repo (divmot banks + bit-exact `AnimDecodePose` port +
`pose_assemble.py`); see `../scramble.md` and `../decode-steps.md`.

Two distinct layers:

1. **Wrong-rig bake.** The pack's `skeleton.json` records
   `source_glb: lab/game/assets/pantera_leoman_t3real.glb` and
   `root_rest_y: 0.9805`; `rows.pack.json` records
   `target_rig: lab/game/assets/pantera_leoman.glb` (sha256
   `b9f4b0c2…`). The game ships `game/assets/models/pantera.glb`
   (sha256 `7085ce66…`, 68 nodes / 49 joints, Mixamo T-pose rig).
   The old rigs are 22-joint identity-rest rigs; the shipped rig is a
   49-joint Mixamo rig with non-identity bind rotations. The bake tool
   (`lab/tools/t3_motion_bake.py`) retargets onto either, but the pack
   was baked onto the old one.
2. **Old-tool Head deviation.** The old clips/rows Head track is offset
   from the current decode by a constant 50.91° (verified against a
   direct-tool smoke bake: pre-fix V1 max 50.908° on Head, 48/49 other
   bones < 0.5°; and against a per-frame slot-path audit of all 856
   motion units). The reactions pack does NOT have this deviation (its
   Head matches the decode to ≤ 0.05°) — it was baked with the current
   tool; the clips/rows carry an older tool's Head behaviour. The old
   Head is inconsistent with the current decode+tool for Head only.

What it is NOT: no encryption, no bone-index permutation, no swapped clip
roles (that is the T7 King-throw problem, a different lane, still under
hunt — the 10 King throw clips are untouched here).

## 3. Decoding steps

See `../decode-steps.md` for the full reproducible steps. Summary:

1. Verify input SHAs (KMD `3b280fa4…`, divmot03_king `8ae24919…`,
   SLUS_004.02 `c84a320e…`, shipped rig `7085ce66…`).
2. `T3Space` + `sample_clip` decode the divmot bank slot (bit-exact
   `AnimDecodePose` port) into per-frame part globals (kabsch).
3. `retarget()` maps part globals onto the target rig (swing corrections
   per bone, yaw normalisation, hip scaling
   `scale = rig.hipsY / 1.18143431` — T3 stance hip height).
4. `t3_row_bake.py` / `t3_reaction_bake.py` write the `wh-anim-pack/1`
   packs; `t3_bank_skeleton.py` builds `skeleton.json` (identity-rest
   rigs only).

## 4. Cracking steps

No cipher was cracked — T3 has none. The "cracking" work was:

- **Proving the decode was clean and the bake was the defect:** SHA
  verification of all inputs against the pack's recorded hashes; direct
  tool smoke bake onto the shipped rig; runtime-contract read of
  `game/js/t3anims.js` (which proves a naive Mixamo-space re-bake is
  runtime-broken — see §5).
- **Proving the Head deviation was real and Head-only:** (a) V1
  round-trip vs the direct-tool smoke bake (Head 50.908°, everything
  else < 0.5°); (b) a slot-path audit of all 856 motion units
  (`sample_pose` → slot rotations → part world rotation, no vert
  assembly, ~ms/frame): Head 50.91° in 287 units (all clips + 255
  rows), 0.01–0.05° everywhere else; (c) ruling out constant-swing /
  constant-rotation / Chest-swing / facing-flip explanations by direct
  measurement; (d) confirming the current tool's Head is exactly the
  documented retarget of the decoded head-part globals
  (`D_tool[Head] == Y_new @ G_Head @ F.T` to 1.8e-15).
- **Correcting the audit's own bug:** the first audit used a trace
  angle formula on slot-path matrices that carry ~1% stretch from the
  4.12 fixed-point slot rotations (det up to 1.01 on distal bones),
  producing phantom 2–7° deviations. Recomputed with quaternion
  angles (SVD orthogonalisation): Hips ≤ 0.043°, Chest ≤ 0.046°,
  shoulders ≤ 0.056°, legs ≤ 0.37°, feet ≤ 0.74°. The arm/hand
  slot-vs-kabsch differences (up to 27° in one reaction) are
  kabsch-vs-slot twist noise on near-cylindrical parts, not pack
  defects — the old pack matches the tool's kabsch output there
  (stance arms < 0.5°, win_lp arms 0.0000° vs direct-tool references).

## 5. Decomp / recomp steps

The bake tool was run **unmodified** for the bake itself; the conversion
below is a format step the runtime contract requires (Option 2, see the
PR body Deviations). The staged tool patches (row-bake `TARGET_GLB`
retarget, reaction-bake canonical/yaw0 handling) are documented here and
NOT landed in this PR — the conversion achieves the same result without
changing the tools; whether they land is a follow-up decision.

1. **Direct-tool references** (proof anchors, not shipped):
   `t3_motion_bake.py` onto shipped `pantera.glb` — smoke clip
   `t3_stance` (75 frames) and `t3_win_lp` (128 frames); patched staged
   `t3_row_bake.py` (`TARGET_GLB` king → shipped rig) for rows 0 and 35.
2. **Conversion** (`convert_to_canonical.py` in the lane workdir —
   the method, not hand-tooling): recover `D_old` per bone by FK of the
   old pack's canonical locals (exact: old rig `wrest` is identity);
   `D_new = F @ D_old @ S_old.T @ F.T @ S_new` per core bone
   (`F = diag(-1,1,-1)`; `S` from the tool's own `swing()` on its own
   `sp` dicts); Spine/Spine1/Neck/ToeBase re-derived exactly as
   `retarget()` derives them; Root = identity;
   `root_t_new = [0, 1.06130751, 0] + (scale_new/scale_old) * F @ (root_t_old - [0, 0.9805, 0])`.
   Bones: CANON22. `skeleton.json`: canonical-bone world rest positions
   of the shipped rig (Root rest = Hips rest). `used_by` restored from
   the old pack (same rows, same movesets — metadata preservation).
   Reactions `ax`/`ay`/`az` copied verbatim (rig-independent decode);
   `yaw0 = wrap(yaw0_old + pi)` (validated on 28 sampled slots, worst
   5e-06 rad).
3. **Head re-derivation** (287 units: 32 clips + 255 rows; reactions +
   row 183 already match and are untouched): `D_new[Head] = Y_new @
   orth(G_Head) @ F.T` where `G_Head` is the slot-path head-part global
   (SVD-orthonormalised; slot-vs-kabsch Head noise ≤ 0.008°), and
   `local[Head] = quat(D_new[Neck].T @ D_new[Head])`, Neck = Chest.
   No other bone is re-derived from the slot path — the old pack already
   matches the tool there.
4. **Why not a full per-frame re-decode:** measured ~1.3 s/frame (OBJ
   text round-trip) → ~23k frames ≈ 8+ hours. The fast path is the
   tool's own retarget equations applied to the verified decoded motion
   (`D_old`), with direct-tool references as proof. No hand-keyed
   motion anywhere.

## 6. Before / after proof

| Measure | Before (old pack) | After (this PR) |
|---|---|---|
| Pack hip height | 0.9805 m | 1.06130751 m (shipped rig, exact) |
| `anchor_mm_to_rig_m` | 0.000829923 | 0.000898321 (+8.24%) |
| Pair-geometry error | 8.24% | 0% by construction |
| Scale (T3 stance hip 1.18143431 m) | 0.829923415 | 0.898321216 |
| Root travel ratio (every clip) | — | exactly 1.082414594 |
| `t3_grab` root travel | 2.9512 m | 3.1944 m |
| `t3_win_lp` root travel | 1.3262 m | 1.4355 m (still < 1.45 m gate) |
| Stance `root_t[0]` height | 0.47924 m | 0.51874 m |
| Head track deviation vs decode | 50.91° (32 clips + 255 rows) | ≤ 0.0082° (slot noise) |

Verification (all measured 2026-11-21, lane workdir):

- **V1** — converted `t3_stance` forwarded to Mixamo space vs the
  direct-tool smoke bake: max quat angle **0.006944°** (mean 0.000070°),
  max root error **0.0000 mm** (pre-Head-fix: Head 50.908°).
- **V1b** — converted `t3_win_lp` (arm-heavy) vs direct-tool reference:
  overall max **0.0082°** (Head, slot noise), arms **0.0000°**, root
  **0.0000 mm** (128 frames, 49 bones).
- **V2** — converted rows 0 and 35 vs a direct 2-row pack bake:
  max |q int16 diff| **3 LSB** (row 0) / **2 LSB** (row 35), max |root
  mm diff| **1 mm** — within source-pack quantization noise.
- **V3** — 568 reactions: `ax`/`ay`/`az` identical, roles identical,
  anchor 0.000898321, Chest non-identity (max |q−identity| 0.6540 —
  chest motion preserved). 256 rows: keys + `used_by` identical.
- Counts: 32 clips (same slots/move_rows/stream_frames/frame counts),
  256 rows / 0 missing, 568 reactions / 0 missing.

Honest limit: the re-bake narrows the 8.24% error but does **not** close
the 1.45 m throw-connect gate on its own (the gate fix already landed,
PR #1781). The lane-G 1.3798 m figure could not be reproduced — its
definition was not in the brief materials; the numbers above are the
lane's own measurements with stated definitions. Do not claim 1.3798 m
or gate closure from this PR.

## 7. Sources

- Repo: `mhvnsnt/western-heart`, main `727afe13` (base of this PR).
  Pack: `game/assets/anim/t3/king_on_pantera_leoman/`. Shipped rig:
  `game/assets/models/pantera.glb` (sha256 `7085ce66…`).
  Runtime contract: `game/js/t3anims.js` (`retargetT3Clips`,
  `retargetClipToRig`, `decodePackRow`).
  Bake tools: `lab/tools/t3_motion_bake.py` (blob
  `9004a070…`), `tools/anim/t3_row_bake.py`,
  `tools/anim/t3_reaction_bake.py`, `tools/anim/t3_reaction_tables.py`,
  `tools/anim/t3_bank_skeleton.py`, `lab/skeleton/retarget_maps.json`.
  Decode: `teardown/tekken3/tools/local/{pose_assemble,usa_motion,
  usa_tables,kmd_parse}.py`; banks
  `teardown/tekken3/animations/divmot03_king.bin` (`8ae24919…`) and
  `divmot99_common.bin`; KMD `teardown/tekken3/models/king95/king95.kmd`
  (`3b280fa4…`); SLUS_004.02 (`c84a320e…`).
- External: n0madic/Tekken3Remake master
  `14037374030ba95e389f62d0924befe370286f18` (head as checked
  2026-11-21) — `tools/research/{motion,kmd,pose}.py`.
- Research: sweep `lane-b-mechanisms/MECHANISMS.md` §1 (T3 lossy
  compression, BNS/LBA container); `lane-c-coordination/DOCS-SKELETON.md`
  (docs layout); mapping `phase2-lane-b-mapping/MAPPING.md` App. X1;
  audit `AUDIT-INVENTORY.md` (King pack row, lane-G 8% measurement).
- Archive.org check: not applicable to this fix — no game was acquired;
  all inputs are the repo's own teardown. (Standing law: archive.org is
  checked first for any game acquisition.)

## 8. Gaps / open items

- The 1.45 m throw-connect gate is a *game* rule, not a decode property
  — the re-bake does not close it (PR #1781 fixed the gate). The
  lane-G 1.3798 m figure's definition is still unknown; if a lane finds
  its definition, record it here.
- Staged tool patches not landed in this PR (follow-up decision):
  row-bake `TARGET_GLB` retarget for the shipped rig; reaction-bake
  canonical mapping through `rig.by_canon` (Chest←Spine2) and F-aware
  `yaw0` (currently returns `None` for Mixamo-facing rigs). The
  conversion in this PR achieves the same result without changing the
  tools.
- Direct-tool references cover 2 clips (stance, win_lp) + 2 rows (0,
  35) — the full-pack proof is the V1/V2/V3 round-trip above, which
  replays the runtime's own math. A full 32-clip direct-tool reference
  set was not produced (time; each clip bake is ~1–3 min).
- The T7 King-throw role hunt (10 clips) is a separate, still-open
  problem — untouched here; its doc lands with the T7 fix.
