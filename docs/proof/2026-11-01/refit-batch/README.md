# Universal rig refit batch, first wave: the fighters that did NOT ship (2026-11-01)

`tools/auto_rig/batch_refit.py` refits a model and ships it only when three gates pass:
- `rig_report` says PASS;
- the re-audit is clean;
- the result fits the 19.5 MB size budget.

These are the reports of the models that failed a gate, so they kept their current rig. Nothing from this folder is in
the game.

`batch.json` is the batch summary. Each fighter folder holds:
- its gate reports (`*.json`);
- the refit log;
- weight-paint renders (`weights.png`).

The main failure was the stretch gate on long hair and secondary geometry (Phantom's waist-length hair was weighted to
his thighs). `tools/auto_rig/secondary_chains.py`, which turns long hair into simulated strands, was built for this.
Next: re-run these fighters with the secondary chains in the refit (`docs/handoff/HANDOFF-CLAUDE-2026-10-31.md`
section 6).
