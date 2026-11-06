# Cyborg X and Dio on refit rigs (2026-11-06)

Owner 2026-11-06: "fix them all per character you need to fix all the character models" / "Use ur eyes man ... stop
guessing off the data and numbers".

`tools/auto_rig/batch_refit.py` refit nine broken-card models (charger, cyborgx, deathfang, diablo, dio, koreshi, slice,
waterfall, rave). Every one missed the automatic strict-stretch gate, so each refit was judged BY EYE on the game's
own card render from four angles (`refit-candidates-four-angles.png`):

- **Cyborg X (cape-jones-attire1): adopted.** Clean, front-facing: hood, face, white suit, cape hanging behind. The
  old card had the camera inside a torn, stretched white cape. 86.2 MB -> 14.1 MB (`tools/deploy/fit_cdn_budget.py`).
- **Dio (dio-attire1): adopted.** Front-facing face and chest, no crumple (old rig: cone face + crushed arms).
  28.6 MB -> 19.0 MB (JPEG q85, normal error 0.74 deg mean). Remaining for Dio: his long robe is weighted to his legs
  and stretches into a sheet on high kicks, identically on the old rig and the refit
  (`dio-heavy-kick-old-vs-refit.png`); it needs cloth / secondary chains.
- Not adopted (no clear improvement on the card): charger, deathfang, diablo, koreshi, slice, waterfall; rave's refit
  failed to build. Their refit files were not committed.

`cyborgx-dio-cards-and-fight.png`: old / new cards and a real local fight, Cyborg X vs Dio, both standing and fighting.
Gate reports: `cyborgx-rig_report.json`, `dio-rig_report.json` (strict stretch is the documented deviation, judged by
eye per the owner's rule, same evidence class as the Wave 3 item 2 cainelias deviation).
