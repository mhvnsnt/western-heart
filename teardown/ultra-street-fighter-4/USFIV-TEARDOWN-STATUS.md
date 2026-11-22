# USFIV teardown status

Checked live 2026-11-20. Owner order (Nov 20 ~19:27 EST): pull the
already-torn-down/decomped fan/mod work instead of buying the games.

## USFIV — Ultra Street Fighter IV

| Item | Status |
|---|---|
| Complete extracted moveset/animation/model pack | NONE FOUND anywhere searched |
| Extraction toolchain | SHARED with SFIV — `../street-fighter-4/tools/sf4tools/` (bac/bcm parser, MIT) |
| Decomp / static-recomp port | NONE — no USFIV equivalent of `sf4-nx` found |
| archive.org teardown/decomp | NONE — game dumps only |
| Models Resource | 2 assets total (Adon model + 1 stage element), no animations — not pulled |
| WH bank converter for bac/bcm | NOT BUILT — next step |

## Still missing (exact gap)

Same as SFIV: no extracted moveset data and no WH bank converter.
Run `../street-fighter-4/tools/sf4tools/` against real USFIV game
files and dump bac/bcm → JSON. USFIV is the best single target for
that run — the complete 44-fighter SFIV roster in one install.
