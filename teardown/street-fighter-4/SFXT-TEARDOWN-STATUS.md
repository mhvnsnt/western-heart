# SFxT teardown status

Checked live 2026-11-21/22. Owner order (Nov 21 ~19:57 EST): complete teardowns or the closest thing, finished into complete versions, wired 100% into Western Heart.

## SFxT — Street Fighter X Tekken

| Item | Status |
|---|---|
| Complete extracted moveset/animation/model pack | NONE FOUND anywhere searched (ShiroiKaze 2012 Xbox 360 disc rips are LOST — EventHubs images only) |
| Extraction toolchain | SHARED with SFIV — `../street-fighter-4/tools/sf4tools/` (bac/bcm parser, MIT) |
| Extracted moveset data | DONE — Kaggle kernel `marsfmmg/sfxt-bac-bcm-extract` (SFxT PC, archive.org `street-fighter-x-tekken_202508`, loose .bac/.bcm): 327 .bac files found |
| SFxT format | SOLVED (hex-verified on RYU.bac 247,216 B / RYU.bcm 22,996 B): BAC header (version u16 @12, ScriptCount, VFXCount, 5 offsets); BCM header (counts, 8 offsets; AE's 4-byte zero int32 at 12-15 is GONE). Parser `../street-fighter-4/tools/sfxt_bcm.py` parses 362/362 files: 12,797 moves, 8,570 named scripts |
| WH bank converter | BUILT — `../street-fighter-4/tools/bac_bcm_to_wh.py` `--sfxt-dir` mode (tested on all SFxT parsed JSON); SFxT WH movesets wired in `moveset-library/movesets-v2/sfxt-*.json` (55 files, 5,612 moves, 3,352 linked to scripts) |
| Frame data/damage | Honest placeholders — BAC script bodies NOT decoded (open RE task) |

## Still missing (exact gap)

1. **BAC script-body decode** (frame data/damage) — open RE task; BCM moves + script names/directories are complete.
2. **Animation clips (.anm/.emm)** — bac/bcm is moveset logic + frame data + hitboxes, NOT skeletal animation clips. anim_ref points at `sfxt:<char>/<script>` pending .anm extraction.
