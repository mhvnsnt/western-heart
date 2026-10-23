# Law pull for Buffalo Bill — 2026-10-23

Owner directive (verbatim): "pull their animations and movesets fully and everything...
and their stances and poses" (Law/Lars full pull for Buffalo Bill + Chordz;
this log covers the Law/Buffalo Bill half).

## What was done

**Moveset** (`game/assets/movesets/buffalo-bill.json`): 228 -> 229 moves.
- Full-bank audit of `teardown/tekken3/movesets/moveset_law.json` (459 rows) vs
  the 228 generated moves (216 distinct rows): 43 damaging rows unreached by the
  input-branch BFS.
- Motion-fingerprint comparison (sampled 49-channel poses, first/mid/last frame)
  of every row: row 57 duplicates covered rows 54/55/56 (skip); the other 42 have
  unique motions.
- Of those 42, exactly ONE has a decodable Tekken input: row 441, the mash
  follow-up `[5+LP 5 5+RP 5 5+LP+RP](40f)` to row 439 (`d/f+1+2,1_c2`). The bank
  generator skips neutral-mash commands by design, so it was never emitted.
  Added as `d/f+1+2,1_c2,mash` (damage 21 = 35*100/170, heavy, t3_command verbatim).
- The remaining 41 rows have NO incoming input edge of any kind (no branch, no
  <common>, no conditioned edge targets them) — EXE-driven or unreferenced rows.
  Not added: inventing notation would violate the no-guessing law.
- Forest Law cross-bank motion diff: 27 forest-exclusive motions, all with decoded
  inputs — but they are Forest's ALTERNATE versions of Law's basics (his own 1, 2,
  3, 4, f+4...), a different character's movelist. Not merged into Buffalo Bill
  (would duplicate inputs and break 1:1 input->move fidelity). Forest bin stays
  as animation gap-filler only.
- `game/assets/movesets/index.json`: buffalo-bill 228 -> 229 moves/inputs/bytes.

**Animation bank** (`game/assets/anim/t3/law/`, new): 30 wh-anim/1 clips baked from
the owner's disc via the existing pipeline, zero hand keys:
- `t3_neutral.json` = move-index slot 3 — Law's signature fighting stance (idle)
- `t3_stance.json`/`_b`/`_c` = slots 0/1/2 — round-start intro poses
- `t3_light` = row 161 (jab "1"), `t3_medium` = row 237 (kick "3"),
  `t3_heavy` = row 192 (u/f+4 flip kick), `t3_grab` = row 266 (1+3 throw)
- `t3_block`/`_b`, `t3_hit`, `t3_hit_launch`, `t3_ko` (common-bank slots)
- `t3_dash_fwd`, `t3_backdash`, `t3_walk_fwd`/`_back`, `t3_crouch`/`_hold`
- `t3_jump_up`/`_fwd`/`_back`, `t3_sidestep_a`/`b`/`c`/`d`
- `t3_win_lp`/`_rp`/`_lk`/`_rk` = slots 0xd67-0xd6a (win poses; loader uses win_rp)
- `skeleton.json` (wh-anim-skel/1, 18 joints, from the committed t3real GLB)
- `rows.pack.json` (wh-anim-pack/1): 217 referenced rows, 0 missing — per-move
  clips for every t3_row the moveset references
- `lab/game/assets/t3_law_t3real.glb`: bake target rig + all baked animations
  (source_glb of the bank, sha256-recorded)

**Wiring** (`game/js/t3anims.js`): `T3_BANKS.law = 'assets/anim/t3/law/'`,
`SOURCE_TO_BANK.law = 'law'`. `bankIdFor('buffalo-bill')` now resolves via his
moveset's `t3_source: 'law'` (previously null -> no T3 actions).

**Tool extensions** (additive, committed for re-bakes):
- `lab/tools/t3_motion_bake.py`: `BANKS["law"]`
- `tools/anim/t3_row_bake.py`: SRC2BANK/BANK_DIR/TARGET_GLB `law` entries
- `tools/anim/t3_bank_skeleton.py`: BANKS `law` entry

## Method / provenance (no guessing)

- Law KMD re-extracted from the owner's TEKKEN3.BNS via
  `tools/anim/t3_extract_bodies.py --only law` — sha256 c47b991a... matches the
  recorded BODY-EXTRACTION.json value; stance OBJ rendered by pose_assemble
  (slot 0, frame 75, same convention as the other banks).
- Research decoder deps (n0madic/Tekken3Remake `tools/research/{motion,kmd}.py`)
  are not vendored in this environment; cloned public repo to
  `~/workspace/tools/tekken3remake` (sparse: tools/research + bns index doc).
- Baked with the facing-fix build of `t3_motion_bake.py` (knee-direction facing;
  validated on all KMDs). Verified the legacy head-centroid heuristic AGREES with
  the knee heuristic on Law's KMD (both pick -f0), so the bank is consistent under
  either facing build.
- Clip<->GLB gate: `t3_bank_skeleton.py --check` on law: 540 channels,
  max |1-q.q'| = 7.83e-07 (same tolerance as the shipped banks, ~8e-7).
- Stick-figure renders of neutral/intro/jab/u/f+4/throw/win/KO eyeballed: stance
  is Law's crouch fighting stance, u/f+4 is the somersault flip kick, win pose
  raises the arm. Real decoded motion, not procedural.

## Deliberately not done

- 41 unreachable Law rows: no decoded input -> no notation invented.
- Forest Law moves: different character's alternates -> not merged.
- Buffalo Bill's CANON.md untouched (Law moves are his fighting style; lore unchanged).
- Tekken/Law names appear only in technical files (moveset JSON, bake scripts,
  this log) — never in canon files.

## Verification

- `node --check` on edited JS (t3anims.js).
- Bank loads through the real `t3anims.js` loader path (fetch list == files shipped).
- In-game playtest (animations actually playing on Buffalo Bill): flagged for the
  parent/coordinator — no live browser in this lane.
