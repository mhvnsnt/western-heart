# Lane 1B — Street Fighter family wiring (SFIV + SFxT; USFIV 0)

Owner order 2026-11-21 ~19:57 EST (Order B Track 1): complete teardowns or the closest thing, finished into complete versions, wired 100% into Western Heart.

## What landed in this PR

- **SFIV:** 25 WH movesets in `moveset-library/movesets-v2/sf4-*.json` — 1,922 moves, 1,663 linked to scripts. Source: vanilla SFIV PC (archive.org `Street_Fighter_IV_CSF`), .emz unpack + vanilla parser. Vanilla BAC/BCM format solved (see `SFIV-TEARDOWN-STATUS.md`).
- **SFxT:** 55 WH movesets in `moveset-library/movesets-v2/sfxt-*.json` — 5,612 moves, 3,352 linked to scripts. Source: SFxT PC (archive.org `street-fighter-x-tekken_202508`), loose .bac/.bcm + SFxT parser. SFxT BAC/BCM format solved (see `SFXT-TEARDOWN-STATUS.md`).
- **Converter + parsers:** `tools/bac_bcm_to_wh.py` (AE + `--sfxt-dir` + `--sfiv-dir` modes), `tools/sfiv_bac_bcm.py`, `tools/sfxt_bcm.py`.
- **Docs:** updated `SFIV-TEARDOWN-STATUS.md`, new `SFXT-TEARDOWN-STATUS.md`, updated `../ultra-street-fighter-4/USFIV-TEARDOWN-STATUS.md`.

## What did NOT land (honest gaps)

- **USFIV: 0 characters parsed.** v3 kernel COMPLETE but parsed_ok = 0 (see USFIV status doc). Character data is in .eaf archives; a v4 kernel that opens .eaf is the next step. NO USFIV movesets in this PR.
- **Frame data/damage: honest placeholders** in every SFIV/SFxT move (BAC script bodies not decoded — open RE task; one focused attempt failed, recorded in the lane workdir). Each move note quotes the raw BAC header values where available.
- **5LP cross-check: NOT POSSIBLE** (no USFIV AE data). Vanilla 5LP header field order (9,12,26,32) stays UNVERIFIED.
- **AE converter path: UNTESTED on real data** (no USFIV combined JSONs exist).
- **Animation clips (.anm/.emm):** not extracted. anim_ref points at `sf4:<char>/<script>` / `sfxt:<char>/<script>` pending .anm extraction.
- **Library index:** `game/data/moveset-library/index.json` is NOT updated in this PR — the index refresh is a separate owed lane (it predates these 80 files). The movesets are the payload; the index is generated from them.

## Sources / licence

- Game files: Capcom's Street Fighter IV / Street Fighter X Tekken / Ultra Street Fighter IV (Xbox 360 / PC). Extraction tool: dantarion/sf4tools (MIT), vendored in PR #1810. Licence never gates use; logged honestly.
