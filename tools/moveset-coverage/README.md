# tools/moveset-coverage — FULL MOVESET LAW coverage report

One script, no dependencies beyond the stdlib:

```bash
python3 tools/moveset-coverage/moveset_coverage.py \
    --dir game/assets/movesets --md docs/MOVESET-COVERAGE.md --json-out /tmp/cov.json
```

Scans every `game/assets/movesets/*.json` and reports per fighter file:
move/string/special counts, the data bank the moves came from
(`t3_bank` / `doa_source` / …), whether that bank is the fighter's named
base character's own bank, the file's own `proxy` flag, animation
coverage (% of moves with an `anim_ref`), and a law status:

| Status | Meaning |
|---|---|
| FULL-REAL | >= 100 moves from the base character's own decoded bank — FULL MOVESET LAW met |
| FULL-BANKED | >= 100 moves from a real teardown bank assigned as the style bank (e.g. a T7-era base with no T3 bank of its own) |
| REAL-THIN | Real teardown data, < 100 moves — partial extraction |
| PROXY | The file itself declares `proxy: true` |

The generated `docs/MOVESET-COVERAGE.md` is the canonical snapshot;
regenerate it whenever a moveset extraction lands so the law's progress
stays measurable.
