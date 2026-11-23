# USFIV teardown status

Checked live 2026-11-20. Owner order (Nov 20 ~19:27 EST): pull the
already-torn-down/decomped fan/mod work instead of buying the games.

## USFIV — Ultra Street Fighter IV

| Item | Status |
|---|---|
| Complete extracted moveset/animation/model pack | EXTRACTED 2026-11-22 (v6) — 44 fighters, 3,853 moves, `moveset-library/movesets-v2/usfiv-*.json` |
| Extraction toolchain | SHARED with SFIV — `../street-fighter-4/tools/sf4tools/` (bac/bcm parser, MIT) |
| Decomp / static-recomp port | NONE — no USFIV equivalent of `sf4-nx` found |
| archive.org teardown/decomp | NONE — game dumps only |
| Models Resource | 2 assets total (Adon model + 1 stage element), no animations — not pulled |
| WH bank converter for bac/bcm | BUILT + RUN (`../street-fighter-4/tools/bac_bcm_to_wh.py`, AE path) — 3,853/3,853 converted, 3,847 linked |

## Still missing (exact gap)

SUPERSEDED by v6 below — extracted moveset data now exists (44 fighters) and the WH bank converter has run on it.

## Update 2026-11-22 — Lane 1B (v3 kernel: 0 parsed; character data is in .eaf)

- **USFIV v3 kernel COMPLETE** (`marsfmmg/usfiv-bac-bcm-extract-v3-emz-carve`, ~1h 43m) but **parsed_ok = 0, parsed_failed = 3.** The 3 "characters" are magic-scan false positives (absurd sizes): FLN_RV1_PLY_J_scan_0, JRI_scan_0, CNL_scan_0 — all FAILED. NO `usfiv/*.json` in the kernel output (15 files total).
- **Why 0:** the Xbox USFIV ISO holds NO loose .bac/.bcm and NO .cmn.emz (unlike vanilla SFIV PC). All 501 .emz containers unpacked to #EMB blobs with NO #BAC/#BCM magic ("no-magic" x 501). The .cpk files (313) are ALL sound/narration, not movesets.
- **Where the character data is:** the extracted tree (1,122 files) shows it in **.eaf archives** — `dl1/character_00.eaf` (269,769,056 B) + `dl1/character_01.eaf` (144,697,526 B) + `archive/battle/battle.eaf` (2,804,132,681 B). V3 never opened .eaf (only .emz unpack + magic scan of files <=200 MB).
- **Next step:** a v4 kernel that opens .eaf. Until then, no USFIV movesets exist and the AE converter path (`../street-fighter-4/tools/bac_bcm_to_wh.py` AE mode) is UNTESTED on real data; the vanilla 5LP header field order (9,12,26,32) stays UNVERIFIED.
- **WH bank converter for bac/bcm: BUILT** (`../street-fighter-4/tools/bac_bcm_to_wh.py`, AE path) — but with no USFIV data to run it on.

## Update 2026-11-22 — Lane 1B v6 (AE parse: 244/244, 44 fighters wired)

- **USFIV v6 kernel output pulled + re-parsed locally with the AE parser** (dantarion `bac.py`/`bcm.py`/`util.py`, py3-shimmed — see `ae_bac.py`, `ae_bcm.py`, `ae_util.py` in this directory). The vanilla parser fails on all 244 pairs because USFIV `.bac` is **big-endian SSFIV:AE** (ADN.bac head `#BAC ff fe 00 28`; AE header scriptCount=682, hitboxCount=186, tables at 712/3440/6168 — contiguity exact).
- **Parse: 244/244 OK, 0 failed.** Per-pair script/hitbox/move counts in `USFIV-V6-PARSE-SUMMARY.json`.
- **Convert: 44/44 fighters, 3,853/3,853 moves converted, 3,847 linked to scripts.** The 6 unlinked moves all carry Script = 0xFFFFFFFF (no script by design — system/cancel entries): DAN 6MP (f+2), DAN 6HP (f+1+2), ELN UC01_CANCEL (3+4), HUG SUC1 (1+2), IBK R6LK (f+3), PSN UC01_CANCEL (1+2).
- **5LP cross-check — field order CONFIRMED on the full set.** RYU canonical 5LP = [9, 12, 26, 32], identical to vanilla SFIV 5LP; RYX matches too. The other 42 fighters differ per character (real per-fighter frame data, e.g. VEG [19, 23, 38, 50], CNL [3, 5, 20, 29]) — every fighter satisfies first <= last <= total and iasa <= total. The AE parser reads first/last/iasa/total in the same order as vanilla; the values are the fighters' real jabs, not a field-order error.
- **Canonical variant rule** (first match wins): `patch_battle/regulation/latest_ae` first (39 chars), then `character_00_battle/regulation/latest`, `ae2_battle/regulation/ae2` (5 DLC-only chars: DCP, ELN, HUG, PSN, RLN), `ae2_battle/regulation/concept`, `battle_chara`, `ae2_battle/regulation/sf4`, `patch_battle/regulation/v104`, `patch_battle/regulation/v101`. Full table: `USFIV-V6-VARIANT-TABLE.md`.
- **Where the files are:** WH movesets `moveset-library/movesets-v2/usfiv-*.json` (44); AE parsers in this directory; parse summary `USFIV-V6-PARSE-SUMMARY.json`; variant table `USFIV-V6-VARIANT-TABLE.md`. The 244 decoded raw pairs + combined `usfiv/<CHAR>.json` intermediates live in the v5 kernel output (`marsfmmg/usfiv-bac-bcm-extract-v5-eaf-dir`) and re-parse deterministically with the parsers in this PR — they are NOT duplicated into the repo (same pattern as PR #1832, which shipped WH movesets only).
- **Still owed:** `.anm` animation extraction (movesets carry real frame data + damage now; no animation clips yet); game wiring (index + fighter loading) is a follow-up lane, not this PR.
