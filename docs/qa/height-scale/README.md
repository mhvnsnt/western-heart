# Per-character height/scale (owner rule c)

- Data: `lab/game/data/characters/heights.json`. There's one entry per CANON fighter: its Tekken body (from CANON.md "Body / Mind / Soul") and that body's official profile height (T7 list, or T8 where T7 has none). `null` means owner or teardown to confirm, and the model keeps its native size.
- Runtime: `scripts/height_scale.gd` measures the rest-pose mesh height and scales the model to `height_cm`. `Fighter.apply_height(id)` is the hook. `main.gd` applies it to both fighters and adds "NNN cm" to the HUD names. Test-only overrides: `--p1-char=<id>` and `--p2-char=<id>`.
- Replace the profile numbers with skeleton-measured T6/TTT2 teardown heights once the importer (Repo Co Dev) lands.

## Proof (2026-10-14)
- `godot --headless --path lab/game -s res://tests/test_height_scale.gd` → `HEIGHT SCALE TESTS (46 cases): PASS` (both Lab GLBs × 23 ids, within 0.5 cm)
- `tests/run_match_headless.sh` → `MATCH RESULT wins=[2, 1] ... MATCH TEST: PASS`; `test_move_table.gd` → PASS
- Render (xvfb + opengl3, `--write-movie`, frame 150), with log `HEIGHT ... measured_m=2.000 / 1.570 / 1.960`:
  - `pantera200_vs_sakura157.png`: `--p2-char=saku_ra`
  - `pantera200_vs_burger196.png`: `--p2-char=burger`
- Known, pre-existing: the Bannon mask floats above the head on the T3 King rig (it also does at native scale).
