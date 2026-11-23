# SFxT teardown status

Checked live 2026-11-20. Owner order (Nov 20 ~19:27 EST): pull the
already-torn-down/decomped fan/mod work instead of buying the games.

## SFxT — Street Fighter X Tekken

| Item | Status |
|---|---|
| Complete extracted moveset/animation/model pack | NONE FOUND — the only known complete extraction (ShiroiKaze, 2012, Xbox 360 disc) has no surviving downloadable pack |
| Extraction toolchain | SHARED with SFIV — `../street-fighter-4/tools/sf4tools/` (bac/bcm parser, MIT) |
| Decomp / static-recomp port | NONE — "SFxT RECOMP" is a Facebook logo image only, no repo/code |
| archive.org teardown/decomp | NONE — game dumps only |
| Models Resource | No SFxT page |
| WH bank converter for bac/bcm | NOT BUILT — next step |

## Still missing (exact gap)

Same as SFIV: no extracted moveset data and no WH bank converter.
Run `../street-fighter-4/tools/sf4tools/` against real SFxT game files
(PC install or the owner's Xbox 360 disc) and dump bac/bcm → JSON.
If the 2012 ShiroiKaze rips resurface as a downloadable pack, pull
that whole.
