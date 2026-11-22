# SFIV teardown status

Checked live 2026-11-20. Owner order (Nov 20 ~19:27 EST): pull the
already-torn-down/decomped fan/mod work instead of buying the games.

## SFIV — Street Fighter IV

| Item | Status |
|---|---|
| Complete extracted moveset/animation/model pack | NONE FOUND anywhere searched |
| Extraction toolchain (bac/bcm parser) | PULLED — `tools/sf4tools/` (Dantarion, MIT) |
| Decomp / static-recomp port | RECORDED — `sf4-nx.md` (`jvankooo/sf4-nx`, GPL-3.0, working v0.1.0); framework only, not vendored |
| archive.org teardown/decomp | NONE — 40 software items checked; all raw game images/builds/prototypes/fixes/MUGEN |
| Models Resource | No SFIV vanilla roster pack; USFIV page has 2 assets total (Adon + 1 stage) |
| WH bank converter for bac/bcm | NOT BUILT — next step |

## USFIV — Ultra Street Fighter IV

Same engine, same formats, same toolchain as SFIV — covered by this
directory. No separate USFIV teardown exists; the only USFIV-specific
extraction found is a single Adon fighter model (DAE, 14.21 MB) on the
Models Resource, no animations, not pulled. USFIV status is recorded
separately in `../ultra-street-fighter-4/`.

## SFxT — Street Fighter X Tekken

Same bac/bcm/emo formats as SFIV (ShiroiKaze ripped the Xbox 360 disc
with SF4 tools in 2012, full DLC cast with rigs + animations) — but no
surviving downloadable pack was found; only EventHubs images, single
MMD rips, and sound rips remain. No SFxT recomp project exists (a
"SFxT RECOMP" logo image on Facebook, Oct 11 2026, has no repo/code).
SFxT status is recorded separately in `../street-fighter-x-tekken/`.

## Still missing (exact gap)

1. **Extracted moveset data.** Nobody publishes a complete SFIV/SFxT/USFIV
   moveset dump. To get one, run `tools/sf4tools/` against real game files
   (SF4 PC install or the owner's Xbox 360 disc files) and dump bac/bcm →
   JSON. That run has not happened yet.
2. **WH bank converter.** bac/bcm JSON → WH moveset bank. Not built.

## Update 2026-11-22 — Lane 1B (vanilla SFIV solved, movesets wired)

- **Extracted moveset data: DONE.** Vanilla SFIV (Build 3584) stores char data in `.emz` containers; Kaggle kernel `marsfmmg/sfiv-bac-bcm-extract-v2-emz` unpacked all 25 chars (EMZ `skip=16 wbits=-15`, raw deflate after a 16-byte header; #BAC/#BCM carved magic-to-next-magic) and the vanilla parser (`tools/sfiv_bac_bcm.py`) parsed 50/50 files: 1,922 moves, 5,403 named scripts.
- **Vanilla format solved** (hex-verified on RYU.bac 174,464 B / RYU.bcm 7,948 B): BAC `#BAC`+FE FF, 687-entry script/name tables (196 nonzero, indices align exactly); script header (first,last,iasa,total) + directory in vanilla order (frameOff, type, count, dataOff); BCM counts/offsets solved; input bits use the AE layout exactly.
- **WH bank converter: BUILT.** `tools/bac_bcm_to_wh.py` `--sfiv-dir` mode (tested on all 25 parsed JSONs); SFIV WH movesets wired in `moveset-library/movesets-v2/sf4-*.json` (25 files, 1,922 moves, 1,663 linked to scripts).
- **Frame data/damage: honest placeholders.** BAC script bodies are NOT decoded (open RE task; one focused attempt 2026-11-22 failed — recorded in the lane workdir). Each move note quotes the raw BAC header values. The 5LP header field order (first=9 last=12 iasa=26 total=32) is UNVERIFIED — the USFIV AE cross-check that was supposed to settle it could not run (USFIV parsed 0; see `../ultra-street-fighter-4/USFIV-TEARDOWN-STATUS.md`).
