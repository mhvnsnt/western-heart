# Western Heart — Lab track (private, owner's own source games)

The Lab track turns the owner's own Tekken 3 teardown into playable Godot 4 content. Plan: money-machine-hq `docs/western-heart-audit.md`; inventory: `docs/western-heart/INVENTORY.md`.

## Milestone 1: canonical skeleton + Tekken 3 → glTF importer + rig check
- `skeleton/canonical_skeleton.json`: **WH-Canonical-22**. Mixamo-compatible names, Y-up meters, faces +Z. The bind pose is the T3 stance with world-aligned joints.
- `skeleton/retarget_maps.json`: maps three source rigs (Tekken 3 rigid 27-row/18-part, Mixamo 49, and the 13-bone rigify-style pantera rig) to canonical.
- `tools/t3_to_gltf.py`: reads the KMD (hierarchy, joint offsets, faces) and the stance OBJ from `teardown/tekken3/tools/local/pose_assemble.py`. It recovers each part's real stance transform by rigid Kabsch fit (max RMS 0.94 T3 units, about 1 mm). It writes a rigid-skinned GLB (each vertex weighted 100% to its part) with 11 combat clips (`tools/clips.py`, 2-bone IK, planted feet). It also imports a T3 stage panorama.
  ```
  python3 lab/tools/t3_to_gltf.py fighter teardown/tekken3/models/king95/king95.kmd teardown/tekken3/renders/pose-check/king_stance75.obj lab/game/assets/t3_king.glb
  python3 lab/tools/t3_to_gltf.py stage teardown/tekken3/stages/l/stg_l_panorama.obj lab/game/assets/t3_stage_l.glb
  ```
- `tools/rig_check.py` + `tests/test_rig_check.py`: an automated check that bones, weights, mesh and animation agree, with no exploded vertices and feet on the floor. Run `python3 lab/tests/test_rig_check.py`. It also catches the cm-scale Mixamo Idle in `game/assets/models/pantera.glb` (stretch ×21, sinks 8 m).
- `tools/preview.py`: CPU-skinned matplotlib renders (`docs/m1_preview.png`).

### Honest gaps (M1)
- Only King has a decoded stance pose. The others need `pose_assemble.py`, whose `kmd`/`motion` modules lived at `/home/hatch/...` and are not in the repo.
- About 43% of KMD faces reference "imported" seam vertices (two import lists per row) that `kmd_parse.py` doesn't decode yet, so parts render with joint gaps and holes.
- The clips are authored on the canonical rig, not decoded T3 motion banks (same missing decoder). Textures (TIM atlas) aren't applied; the meshes use vertex colours.

## Milestone 2: data-driven move-table interpreter
- `tools/export_moves.py` copies the 7 existing T3 move files (`game/assets/<name>_moves.json`) into `game/data/moves/`. It attaches the full extracted T3 rows they reference and every attack row (195–298 per fighter).
- `game/scripts/move_table.gd` (`MoveTable`) computes the frame data at 60 fps:
  - startup = `active_first`, active = `active_last − active_first + 1`, recovery = `stream_frames − active_last`;
  - damage is T3 damage on the T3 170 life bar;
  - hit freeze comes from the row, falling back to the Urban Reign 6/9/12;
  - hit and block stun follow the Lab advantage rule (light +8 on hit / +1 on block, heavy −8 on block).
  - It also provides the phase and normalized animation seek used by the fighters.
- Test: `godot --headless --path lab/game -s res://tests/test_move_table.gd` passes for all 7 fighters × 4 slots.
- Gap: input → T3 command-branch mapping (the `branches` field) isn't interpreted yet. Slots are light/medium/heavy/grab per the existing move files.

## Milestone 3: playable 1v1 slice (Godot 4.3, GL Compatibility, HTML5)
- **P1 PANTERA, attire Leo-Man.** He is the owner's first original fighter (CANON.md: "King's wrestler frame"), so he uses the King T3 move table. The owner's Tripo GLB is auto-rigged with `tools/autorig.py` (original kept in `source_assets/original/`).
  - `--p1-attire=t3` swaps to the T3 body.
- **P2 KING** is the CPU: the Tekken 3 KMD import, wearing the **Bannon mask** (see `docs/attire/BANNON_MASK.md`).
- **Stage:** King's own T3 stage `l` panorama plus a floor.
- **Rules:** best of 3, 60 s rounds, T3 170 life bar. Frame data comes from `MoveTable`, with hit freeze, blocking (hold back or block), an unblockable grab, knockback and K.O.
- **Controls:**
  - Keyboard: A/D move, J/K/L/U light/medium/kick/grab, Space block, M mask.
  - Gamepad: D-pad or left stick, X/Y/B/A, RB block, Back mask.
  - Touch: on-screen buttons, shown automatically on touch devices or with `--touch`.
- **Run:** `godot --path lab/game`. Web: `godot --headless --path lab/game --export-release Web build/web/index.html`.
- **Tests:**
  - `python3 lab/tests/test_rig_check.py`
  - `godot --headless --path lab/game -s res://tests/test_move_table.gd`
  - `lab/game/tests/run_match_headless.sh` (a full CPU-vs-CPU match through the real input path)
- **Capture:** `xvfb-run godot --path lab/game --rendering-driver opengl3 --write-movie out.avi --fixed-fps 60 -- --autoplay --quit-after-match --touch`
