# VIRTUA FIGHTER 5 — 100% Verification (wh-sf-dj-vf-100 lane, 2026-10-14)

**WH universe name:** `virtual-soul` (see `RENAME-MAP.md`).

## Release `vf5-ps3-v1` — verified complete

**URL:** https://github.com/mhvnsnt/western-heart/releases/tag/vf5-ps3-v1
**Asset count:** 89 (verified via `gh release view` 2026-10-14).

| Category | Count | Assets |
|---|---|---|
| Fighter archives | 18 | `aki aoi bra dur goh jak jef kag lau lei lio mon msk pai sar shu van wol` (`.farc`) |
| Fighter item archives | 18 | `akiitm` … `wolitm` (`.farc`) |
| Stage archives | 38 | `stgare stgaur stgban stgbar stgcas stgcid stgdjo stgdu1 stgdu2 stgdu3 stgdu4 stgdur stghai stgjin stgnyc stgriv stgsin stgslk stgtak stgtan stgter stgtr2 stgtr3 stgtr4 stgtr5 stgtr6 stgtr7 stgtr8 stgtr9 stgtrm stgtrn stgtrs stgts2 stgts3 stgtst stgumi stgwht stgyuk` (`.farc`) |
| Common | 7 | `akixx.farc dbg.farc effcmn.farc itmcmn.farc test.farc tex_db.bin obj_db.bin` |
| Source RAR chunks | 8 | `vf5-500m.part_00`–`part_07` (7×524,288,000 + 16,440,692 = 3,686,456,692 bytes = verified download) |

**Roster note:** "19 fighters" in earlier status docs counts `akira-yuki-alt` (alt costume,
`akixx.farc`). VF5 base PS3 (BLES00029) has **18 playable fighters** — Jean Kujo and
Taka-Arashi are Final Showdown-only and not in the base game. Code mapping verified:
`mon`=Eileen, `msk`=El Blaze (per-fighter READMEs in the model library).

## Repo state

- `teardown/virtua-fighter-5/`: scaffold + `VF5-MECHANICS.md` + `tools/farc_extract.py` on main.
- Model library (1.3GB, 19 fighter dirs + stages + docs + tools) at
  `~/workspace/western-heart-vf5/teardown/virtua-fighter-5/` — push to GitHub in progress
  by the VF5 recovery worker (smaller chunks). DO NOT DELETE (SHARED-DISK-INVENTORY.md).

## TeraBox

Queued in `~/workspace/terabox-staging/BROWSER-TASKS.md` Task 2C: all 89 release assets
(~4.95GB) → `/western-heart/games/vf5/`. **Browser lane pending.**

## WH rename

18 fighter names → WH proprietary names NEEDED (owner creates). Tracked in `RENAME-MAP.md`.

## Verdict: VF5 = 100% ✅

All fighters, all stages, source RAR, extractor, mechanics doc. Remaining: TeraBox upload
(browser lane) + WH renames (owner names pending).
