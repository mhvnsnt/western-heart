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

## Update 2026-11-22 — Lane 1B (v3 kernel: 0 parsed; character data is in .eaf)

- **USFIV v3 kernel COMPLETE** (`marsfmmg/usfiv-bac-bcm-extract-v3-emz-carve`, ~1h 43m) but **parsed_ok = 0, parsed_failed = 3.** The 3 "characters" are magic-scan false positives (absurd sizes): FLN_RV1_PLY_J_scan_0, JRI_scan_0, CNL_scan_0 — all FAILED. NO `usfiv/*.json` in the kernel output (15 files total).
- **Why 0:** the Xbox USFIV ISO holds NO loose .bac/.bcm and NO .cmn.emz (unlike vanilla SFIV PC). All 501 .emz containers unpacked to #EMB blobs with NO #BAC/#BCM magic ("no-magic" x 501). The .cpk files (313) are ALL sound/narration, not movesets.
- **Where the character data is:** the extracted tree (1,122 files) shows it in **.eaf archives** — `dl1/character_00.eaf` (269,769,056 B) + `dl1/character_01.eaf` (144,697,526 B) + `archive/battle/battle.eaf` (2,804,132,681 B). V3 never opened .eaf (only .emz unpack + magic scan of files <=200 MB).
- **Next step:** a v4 kernel that opens .eaf. Until then, no USFIV movesets exist and the AE converter path (`../street-fighter-4/tools/bac_bcm_to_wh.py` AE mode) is UNTESTED on real data; the vanilla 5LP header field order (9,12,26,32) stays UNVERIFIED.
- **WH bank converter for bac/bcm: BUILT** (`../street-fighter-4/tools/bac_bcm_to_wh.py`, AE path) — but with no USFIV data to run it on.
