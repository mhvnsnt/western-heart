# WWE 2K19 Moveset Library — Extracted 2026-10-19

**Source:** `pac/root/createmode.pac` (+ `createmode_p10/p20/p30.pac` patches) from the WWE 2K19 PC files,
via wrestling-game GitHub releases `wwe2k19-moves-pack` / `wwe2k19-animation-packs-v1`.
**Method:** string-table extraction from the Create-A-Moveset editor data (validated: move names in plaintext,
move IDs in `NNNNNNNNNN_def` format).
**Status:** COMPLETE for the moveset string library. Animation blobs (`.YANM`/`.Anim`) inside the motion pacs
are documented at `docs/` level; full binary decode is queued behind the 51GB game pull.

## Totals

| Source | Unique moves |
|--------|-------------|
| createmode.pac (base) | 5,428 |
| + createmode_p10.pac | +33 |
| + createmode_p20.pac | +54 |
| + createmode_p30.pac | +66 |
| **TOTAL** | **5,581** |

Full list: `moveset-library-2k19.txt` (this directory).

## Categories (keyword-classified)

| Category | Count | Notes |
|----------|-------|-------|
| Strikes (punches, kicks, chops, elbows, knees, stomps) | 1,171 | Largest single category |
| Grapples — suplex/slam/driver/bomb family | 795 | Front, back, side variants |
| Submissions (locks, stretches, chokes) | 230 | |
| Diving / aerial (splash, senton, moonsault, 450, 630) | 203 | Top-rope + springboard |
| Running attacks (spear, shoulder block, cross body) | 77 | |
| Corner / turnbuckle | 62 | Avalanche variants |
| Apron / ringside / barricade | 28 | |
| Victory / taunt | 6 | (taunts mostly live in entrance pacs) |
| Uncategorized (throws, slams, specialty, signatures) | 2,856 | Needs positional tagging pass |

## Per-wrestler motion pacs (animation blobs)

`pac/ingame/motion/body/NN_mpc.pac` — one per wrestler ID. Move entries use the
`WWWWWWMMMM_def` ID format (WWWWWW = 6-digit wrestler prefix, MMMM = move index).

| Wrestler ID | Moves | Pac size | ID range |
|-------------|-------|----------|----------|
| 16 | 999 | 1.2 MB | 1600016000 – 1699916999 |
| 33 | 148 | 9.9 MB | 3300033000 – 3394633946 |
| 34 | 252 | 12.5 MB | 3400034000 – 3462134621 |
| 37 | 434 | 2.4 MB | 3700037000 – 3780137801 |
| 40 | 999 | 3.5 MB | 4000040000 – 4099940999 |
| 42 | 991 | 8.9 MB | 4200042000 – 4299942999 |
| 45 | 707 | 14.2 MB | 4500045000 – 4595045950 |
| 50 | 867 | 24.8 MB | 5000050000 – 5099950999 |
| 51 | 320 | 8.3 MB | 5100051000 – 5153451534 |
| 52 | 82 | 1.4 MB | 5200152001 – 5275452754 |
| 54 | 185 | 5.4 MB | 5400054000 – 5471954719 |
| 55 | 267 | 6.3 MB | 5500055000 – 5599955999 |
| 56 | 270 | 10.1 MB | 5600056000 – 5696956969 |
| 57 | 25 | 0.8 MB | 5700057000 – 5702657026 |
| 58 | 225 | 17.6 MB | 5800058000 – 5855658556 |
| 59 | 449 | 7.2 MB | 5910059100 – 5999959999 |
| 60 | 229 | 6.8 MB | 6000060000 – 6090060900 |
| **TOTAL** | **7,449** | | |

Also present: `pac/ingame/motion_param_pcdb.pac` (motion parameter database),
`pac/ingame/peoples_script.pac` (wrestler scripts), `pac/ingame/diving_param.pac`.

## Entrance pacs (186 files)

`pac/evt/NNNNN_Name.pac` — per-wrestler entrance choreography. Naming: `00109_JeffHardy2k20.pac`,
`00128_AJ Styles 2k18 ENT.pac`, etc. These feed the Custom Entrance / Custom Victory editors.

## Yuke's animation format (inside the pacs)

Per LastGenModz community research (2023): Yuke's animation bytecode (`.YANM`/`.Anim`/`.ACTS`),
in use since WWF SmackDown 1 (2000), built on BioVision Hierarchy (BVH) concepts.
- Animation chunk starts at offset `0x14`; first byte minus `0x60` = animation data base.
- `0x0c`-byte delay/settings chunk (mini-games, submissions, pins).
- Joint-count signature `7D 00` → 109 joints (`0x7D - 0x10`).
- Key contributors: ERM391 (format), Hanleys + PWM community (2K23 animation porting).

## .pac container (HSPC)

Yuke's PAC archive, magic `HSPC`, used across WWE 2K14–2K23. All examined pacs are
low-entropy structured binary (tables, not compressed blobs). Full container decode is
queued — the Ghidra+MCP RE bench (`tools/re/`, PR #315) is the designated tool for it
once the full game lands. **No hand-rolled format guessing per the NO-HAND-TOOLING law.**

## What's still in the 51GB (not yet pulled)

`pac/edit/` — the full CAW part library (`bbtemplate.pac`, `default.pac`, `edit.pac`,
`sample.pac`, `ch/`, `body/`), `pac/profile/profile_dat.pac` (CAW metadata).
See `TRANSFER-PLAN-2026-10-19.md` for the pull plan.
