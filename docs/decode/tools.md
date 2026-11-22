# Tools — decoders, bone maps, community tools

Every tool the scramble sweep uses, with source, version, and licence logged
honestly. Licence status never gates use (standing law) — but it is still
recorded here. "Licence: not verified in this lane" means nobody in this lane
checked the source repo's licence file; check it before redistributing.

Ownership: RESEARCH Lane C maintains this list when it lands the pipeline;
until then each fix lane seeds the rows for the tools it used. This file was
seeded by Lane X1 (King T3 re-bake, 2026-11-21) for the Tekken 3 tools.

## Tekken 3

| Tool | What it solves | Source | Version / commit | Licence |
|---|---|---|---|---|
| n0madic / Tekken3Remake — `tools/research/motion.py`, `kmd.py`, `pose.py` | T3 motion-bank parsing, KMD parsing, pose matrices; the spline machinery the local decode ports | https://github.com/n0madic/Tekken3Remake | master @ `14037374030ba95e389f62d0924befe370286f18` (head as checked 2026-11-21; the three research files were taken from master 2026-11-21) | Not verified in this lane — check the repo |
| `teardown/tekken3/tools/local/usa_motion.py` | Bit-exact port of the game's `AnimDecodePose` for the USA release (SLUS_004.02); literal port of n0madic's `motion.py` spline machinery, rebound to the verified USA table addresses | In-repo (owner's disc teardown) | — | Owner's repo |
| `teardown/tekken3/tools/local/usa_tables.py` | USA EXE tables (spline/sin/sqrt/Euler/limb/skeleton tables, channel shifts) | In-repo | — | Owner's repo |
| `teardown/tekken3/tools/local/kmd_parse.py` | KMD model parsing (rows, verts, pivots) | In-repo | — | Owner's repo |
| `teardown/tekken3/tools/local/pose_assemble.py` | Assembles a fighter's KMD parts into a posed model: bank → `sample_pose` → slot rotations → part world matrices → OBJ text | In-repo | — | Owner's repo |
| `lab/tools/t3_motion_bake.py` | `T3Space` (stance→glTF transform) + `sample_clip` + `TargetRig` + `retarget` (T3 motion → rig animation, GLB + `wh-anim/1` JSON) | In-repo | — | Owner's repo |
| `lab/tools/t3_common.py`, `lab/tools/clips.py` | Shared bake helpers (KMD/OBJ loading, kabsch, quat/rotation helpers, canonical clip authoring) | In-repo | — | Owner's repo |
| `lab/skeleton/retarget_maps.json` | Bone maps: `tekken3_rigid27` (T3 part → bone name) and `mixamo49` (Mixamo → canonical) | In-repo | — | Owner's repo |
| `tools/anim/t3_row_bake.py` | Bakes every referenced T3 move row into `rows.pack.json` (`wh-anim-pack/1`) | In-repo | — | Owner's repo |
| `tools/anim/t3_reaction_bake.py` | Bakes reactions / throw-victim / air entries into `reactions.pack.json` | In-repo | — | Owner's repo |
| `tools/anim/t3_reaction_tables.py` | `bank_plan`: which move slots are reactions, throwers, victims, air kinds | In-repo | — | Owner's repo |
| `tools/anim/t3_bank_skeleton.py` | Builds `skeleton.json` (bank rig hierarchy + rest positions) from an identity-rest rig | In-repo | — | Owner's repo |
| `tools/anim/t3_hit_frames.py` | Hit-frame table (`hit_frames.json`) from the moveset | In-repo | — | Owner's repo |
| Tek3Ex | Unpacks/repacks `TEKKEN3.BNS` via the EXE LBA table | VelocityRa game-format-reversing index (see `scramble-overview.md` sources) | — | Not verified in this lane |
| Tekken3Recompiled (FishB0nes98) | Native-port / static-recompilation research for T3 USA PS1 (SLUS-00402); v0.1.4 easy-setup; "an early playable vertical slice, not yet a content-complete recreation" | https://github.com/FishB0nes98/Tekken3Recompiled (per research) | v0.1.4 (per research) | Not verified in this lane |

## Other games

Seeded by their fix lanes when they land. Shared community toolkit (all
games): see the research workdir `lane-b-mechanisms/MECHANISMS.md` §6
(TKMovesets, TekkenMovesetExtractor, TekkenMods resources).

## Decoder pipeline path — undecided

Whether the decode pipeline lives under `tools/decode/` or under
`game/assets/anim/` is still undecided — RESEARCH Lane C decides. These docs
reference the current in-repo paths until then.
