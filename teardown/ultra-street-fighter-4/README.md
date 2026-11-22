# Ultra Street Fighter IV — teardown

USFIV is the final update of the SFIV series (44 fighters: SFIV + Super
+ AE + AE v2012 + Poison, Hugo, Elena, Rolento, Decapre). Same engine,
same formats (`.bac` / `.bcm` / `.emo` / `.emz`) as SFIV — so the SFIV
toolchain in `../street-fighter-4/tools/sf4tools/` reads USFIV files
too. This directory holds records, not a separate toolchain pull.

## What exists

- Models Resource, USFIV (PC): 2 assets TOTAL — Adon fighter
  (DAE + PNGs, 14.21 MB, submitted Dec 10, 2017 by Ozci) and 1 stage
  element. A single fighter model, no animations, no moveset. NOT
  pulled (one model is not a teardown).
- Sounds Resource, USFIV (PC): 138 assets — voices (EN + JP, 46
  fighters each) and character sounds. Audio only.
- archive.org: `ultra-street-fighter-iv.-xbox-360` (8.25 GB Xbox 360
  image), `ultra-street-fighter-iv-blus-31218` (PS3 image),
  `link_20251007_20251007_1905` (USFIV) — all raw game dumps, none a
  teardown. The first archive.org search (15 rows) showed no USFIV
  game item at all; the software-filtered search (40 rows) found only
  the dumps above.
- PC modding scene: same SF4 tools (Asset Explorer v0.38, Ono!, EMG
  tools) work on USFIV files; character mods exist (e.g. Oni Sakura).
  Mods, not a teardown.

## What does NOT exist

- No complete extracted USFIV moveset/animation/model pack.
- No USFIV decomp/recomp project (no USFIV equivalent of `sf4-nx`
  was found).
- No full-roster USFIV model pack anywhere.

## Still missing (exact gap)

Same as SFIV: run `../street-fighter-4/tools/sf4tools/` against real
USFIV game files and dump bac/bcm → JSON, then build the WH bank
converter. USFIV is the best single target for that run — it is the
complete SFIV roster (44 fighters) in one install.
