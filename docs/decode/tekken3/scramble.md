# Tekken 3 — scramble mechanism + how it was solved

## The scramble

Tekken 3 does not encrypt its animation data and does not permute its bone
indices. What it does, per the scramble research
(`lane-b-mechanisms/MECHANISMS.md` §1, NamuWiki T3 article):

- **Lossy animation compression, built for the PS1 port.** The arcade
  animation data was so large two fighters' data could not load at once
  (King alone would not fit). Namco built an animation loss-compression tool
  letting animators control the compression rate per animation, depending on
  the animation's importance. T3 animations on disc are **compressed with
  per-animation quality chosen by the animator** — data is thrown away by
  design, not encrypted. Any decode is an approximation of the arcade
  original by construction; the PS1 disc cannot give back the arcade data.
- **Container: `TEKKEN3.BNS` (BinStream).** The file table is not in the
  container — it is read from the **LBA table in the game executable**
  (SLUS_004.02 for the USA release).
- **Motion banks (`divmotNN.bin`).** Each fighter's motion lives in a
  `divmot` bank (King: `divmot03_king.bin`); moves shared across fighters
  live in the common bank (`divmot99_common.bin`, addressed by move-index /
  anim-word values at or above `COMMON_FLAG` = `0x40000000`).
- **Models (`*.kmd`).** Each fighter's body is a KMD model of rigid parts
  (King: `king95.kmd`, 27 parts; 18 body parts + costume attachments). Part
  → KMD row and part → matrix slot come from documented EXE tables
  (JP `0x8001A05C` / `0x8001A074` — semantic values, version-independent).
- **No encryption, no bone permutation found.** The barrier is the
  compression + the container + the EXE tables, not a cipher.

## How it was solved (in-repo)

The decode is solved in the repo's own teardown + bake pipeline — not by a
published T3 moveset doc (none exists). The chain, verified end to end by
the King re-bake lane (2026-11-21):

1. **Container:** `TEKKEN3.BNS` unpacked via the EXE LBA table (Tek3Ex
   route); the banks, KMDs, and SLUS_004.02 live in
   `teardown/tekken3/` with SHA-256 recorded in the pack files.
2. **Motion decode:** `teardown/tekken3/tools/local/usa_motion.py` — a
   bit-exact port of the game's `AnimDecodePose` for the USA release,
   a literal port of n0madic's `motion.py` spline machinery rebound to the
   verified USA table addresses (`usa_tables.py`). n0madic verified the
   algorithm against the game's `AnimDecodePose` in a CPU harness with zero
   mismatches (Japan Rev.1); the USA tables were verified by content
   (weight curves match the analytic B-spline basis).
3. **Part assembly:** `teardown/tekken3/tools/local/pose_assemble.py` —
   bank → `sample_pose` → slot rotations → part world matrices → posed
   model. Part → row / part → slot are the documented EXE tables.
4. **Stance → glTF space:** `lab/tools/t3_motion_bake.py` `T3Space` —
   reproduces the stance-to-glTF transform (KMD + stance OBJ, kabsch
   pivots, facing from the shoulder line + knee-bend direction).
5. **Retarget + bake:** `lab/tools/t3_motion_bake.py` `retarget()` (swing
   corrections per bone, yaw normalisation, hip scaling) + `TargetRig`
   (any glTF skin: WH-Canonical-22 identity-rest rigs or Mixamo-49
   T-pose rigs); `tools/anim/t3_row_bake.py` (move rows) and
   `tools/anim/t3_reaction_bake.py` (reactions / throw pairs) write the
   `wh-anim-pack/1` packs the game loads.
6. **Bone maps:** `lab/skeleton/retarget_maps.json` — `tekken3_rigid27`
   (T3 part → bone name) and `mixamo49` (Mixamo → canonical).

## What "scrambled" meant for the King pack (this lane)

The King T3 decode was **clean** — this was a **bake defect**, not a decode
scramble. The pack in `game/assets/anim/t3/king_on_pantera_leoman/` had
been baked onto the old lab rig (`lab/game/assets/pantera_leoman.glb`,
hip 0.9805 m) while the game ships a different rig
(`game/assets/models/pantera.glb`, hip 1.0613 m). The 8.24% hip mismatch
made every throw-pair anchor wrong by 8.24% (pair-geometry error), because
the reactions pack's `anchor_mm_to_rig_m` (0.000829923) belonged to the old
rig. The re-bake (Lane X1) re-expressed the same verified decoded motion
onto the shipped rig (anchor 0.000898321). See
`tekken3/king-pantera/fixed-vs-scrambled.md`.

A second, subtler finding from the same lane: the old bake's **Head track
does not match the decode** — the old Head motion deviates from the
tool's retarget of the decoded head-part globals by a constant 50.908°
angle on every frame (verified against a direct-tool smoke bake and a
per-frame slot-path audit of all 856 motion units). The old Head track
came from an older bake-tool behaviour, not from the current decode. The
re-bake re-derives Head from the T3 source (slot rotations) instead of
carrying the old Head forward. See the per-file doc §2 and §5.

## What is still open for T3

- The arcade original is not recoverable from the PS1 disc (lossy by
  design). The PS1 decode is the ceiling.
- The moveset-level record (move rows, reaction lists) is the repo's own
  teardown work (`teardown/tekken3/movesets/`), not a published doc — keep
  it that way, and keep its SHAs recorded in the packs.
- The 1.45 m throw-connect gate is a *game* rule, not a decode property:
  the re-bake narrows the pair-geometry error but does not close the gate
  (gate fix: PR #1781).
