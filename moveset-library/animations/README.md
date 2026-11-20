# Animation Index

`ANIMATION-INDEX.json` indexes **5,932 animation clips** across all chimera source games, organized into 13 categories.

## Categories

| Category | Clips | Description |
|---|---|---|
| stances | 193 | Idle stances, ready positions |
| walks | 193 | Walking, running locomotion |
| entrances | 222 | Entrance walks, ring entries |
| taunts | 222 | Taunts, celebrations |
| getups | 193 | Knockdown recoveries, getups |
| grapple_positions | 193 | Grapple hold positions, lockups |
| misc_system | 194 | Referee, corner, other system motion |
| strikes | 762 | Punches, kicks, chops, elbows, knees |
| grapples | 763 | Suplexes, slams, throws, powerbombs, DDTs |
| submissions | 764 | Submission holds, rest holds, stretches |
| high_flying | 763 | Diving attacks, top-rope moves, springboards |
| weapons | 735 | Weapon swings, chair shots, table spots |
| misc_moves | 735 | Counters, reversals, special moves |

## Sources

- **WWF No Mercy** (5,787 clips): `../../teardown/wwf-no-mercy/animations/clips/anim_XXXX.npy` — NPY int16, shape (nframes, 26, 3). Move clips join via `anim_id = file_id - 0x3322`. Format: `../../teardown/wwf-no-mercy/animations/FORMAT.md`.
- **WWE WrestleMania XIX** (170 clips): `../../teardown/wmxix/animations/*.json` — per-clip JSON with `[dt, ch1, ch2, asin_deg]` keys. Yukes 70-bone skeleton.
- **Tekken 3** (7 banks): `../../teardown/tekken3/animations/` — divmot banks per character (King, Yoshimitsu, Xiaoyu, Jin, Bryan, Heihachi, Gun Jack).
- **Tekken 6**: animation data encrypted; 46 ending cinematics in `../../teardown/tekken6/`.
- **Urban Reign**: PPK motion pools in `../../teardown/urban-reign/ppks/`.
- **Owner motion bank** (72 clips): `owner-motion-bank/*.json` — the owner's own Mixamo-convention (52-bone) FBX→JSON conversions, mined from `brutalfistgrokversiontenpointfive/public/motion/` (2026-10-22, worker 61). Index: `OWNER-MOTION-BANK.json`; ships the combat move→clip map (140 moves scored by limb/trajectory). Covers wrestling grapples (suplex family, chokeslam, DDT), capoeira ginga/esquiva, drunken style — gaps in the teardown sets. License: owner-granted.
- **Quaternius Universal Animation Library (CC0)** (86 clips): `UAL-CC0.json` — UAL1 (43: locomotion, barehand combat, reactions) + UAL2 (43: melee/weapon combat), mined from the owner's AshLane-prototype (`public/motion/ual/`). GLBs are fetched at build time from that repo (not copied); 65-joint Quaternius rig — no retargeting on Quaternius bodies.

## Usage

Each index entry: `{file, file_id, anim_id, nframes}` (No Mercy) or `{file, source}` (WMXIX).

To use a clip in a moveset: copy the `file`/`anim_ref` path into the move entry's `anim_ref` field in `../movesets/MOVE-DATABASE.json`, then assign the move to a slot in the fighter's moveset JSON.

**Retargeting:** No Mercy AKI clips retarget to Tekken skeletons via `../../teardown/wwf-no-mercy/aki_to_tekken3.py` (v1 proven on King).
