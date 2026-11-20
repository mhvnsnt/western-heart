# T7 clipmap runs for the five owner-named T7 fighters (2026-10-30)

Programme step (c), next step 3 named by
`docs/proof/t7-clipmap-core8-20261030.md`: the same extended
clipmap (with `common.arc`) that closed King's 0x8000 gap in PR #1260
and measured the other five T7 core-8 bases in PR #1261, run for
the five owner-named WH fighters with a T7 base from the #1259
inventory. Tool unchanged (`tools/anim/t7_clipmap.py` as extended
in #1260, optional 4th argument `common.arc`); this chunk is a
measurement run + record only.

## Sources (all read from the GRE repo, main state at run time)

Private repo `mhvnsnt/game-reverse-engineering`, tree
`teardown/tekken7-steam/tkdata/mothead/` — every file listed by the
API with size + blob SHA and fetched by that blob SHA; fetched sizes
match the listing exactly for all 11 files:

- `mask/common.arc` — 5,049,396 bytes, blob
  `80453212f9a2a2d526a36991e40841dd01959c3f` (identical to the #1260
  blob — the same shared bank, not a second copy)
- `json/yosmot.json` 7,304,792 bytes, blob
  `6eb96bfe5a0674b58368f9b8ce368f06f4873ef0`; `mask/yosrotsm.arc`
  5,190,512 bytes, blob `393977131b1af307fab2f0579b6652dbe98c616a`
- `json/heimot.json` 7,502,768 bytes, blob
  `c87b48f3536f6330d409ea6b0d5f20dfe89778c3`; `mask/heirotsm.arc`
  14,927,664 bytes, blob `00ba5f921a2689a50566673367ea30757a0b1522`
- `json/brymot.json` 6,596,873 bytes, blob
  `70b720ebb86d35ffe2caf2f3c8961adc238d28e0`; `mask/bryrotsm.arc`
  5,010,368 bytes, blob `7f4f13a327e99245f44b61251d4cc6b9d833aea0`
- `json/jacmot.json` 6,631,866 bytes, blob
  `ce00959db14cb72d8cf860e7a8e88a2c92021ef8`; `mask/jacrotsm.arc`
  5,193,184 bytes, blob `351c215a8f79f847082ebfe5e87b0a64476eed22`
- `json/xiamot.json` 6,888,701 bytes, blob
  `3fb07f7e54f8dce49061e7ffaa22225bcd0a7566`; `mask/xiarotsm.arc`
  5,536,528 bytes, blob `eb83e2aacd4849162e4fe189fb9eb61dbee2791e`

Method, same bank rule as King: first `MOTA` block, clip index
`anim_id & 0x3FFF`, type byte at the clip offset (`0x64` = full
`Anim64` decode, `0xC8` = frame count from the header). Every
rotsm/common attack row in every output carries a decoded `fmt` +
frame count (verified: 0 attack rows missing a decoded format, all
`0x64`), so these counts are decoded clips, not listed indices.
Exit 0 and `decode_errors` 0 on all five runs. Common-bank attacks
were additionally full-frame decoded (`Anim64.frames()`) per
fighter, 0 errors throughout (see detail below).

## Result — coverage in the King format

| WH fighter | T7 base | Rotsm clips | Moves | Attacks | Resolved | Inline gap |
|---|---|---|---|---|---|---|
| Phantom | Yoshimitsu | 813 | 2,520 | 520 | 503 / 520 = 96.7% | 17 |
| Diablo | Heihachi Mishima | 846 | 2,480 | 427 | 411 / 427 = 96.3% | 16 |
| Skull | Bryan Fury | 663 | 2,319 | 416 | 403 / 416 = 96.9% | 13 |
| Sam-∪R-Λ1 | Jack-7 | 761 | 2,345 | 494 | 480 / 494 = 97.2% | 14 |
| Saku Ra | Ling Xiaoyu | 831 | 2,437 | 443 | 437 / 443 = 98.6% | 6 |

Bank split (attacks) per fighter:

| Fighter | 0x4000 rotsm | 0x8000 common | 0x0000 inline |
|---|---|---|---|
| Phantom | 406 | 97 | 17 |
| Diablo | 330 | 81 | 16 |
| Skull | 323 | 80 | 13 |
| Sam-∪R-Λ1 | 411 | 69 | 14 |
| Saku Ra | 366 | 71 | 6 |

Common bank: 1,711 clips in every run. Combined, the five runs
resolve 2,234 of 2,300 attacks (97.1%); the whole remaining gap
across the five is 66 inline attacks (17 + 16 + 13 + 14 + 6).

Common-bank attack detail (same shared bank in every run, so the
range repeats): clip indices 2–1647 in all five runs, all type
`0x64`, per-attack frames 3–232. Distinct common clips and
full-frame decode totals per fighter: Phantom 86 distinct clips,
6,576 frames; Diablo 75, 5,892 frames; Skull 74, 5,793 frames;
Sam-∪R-Λ1 62, 5,118 frames; Saku Ra 67, 5,445 frames — 0 errors.

## Inline attacks (the whole remaining gap per fighter)

- Phantom: `Ym_rplp00`, `Ym_Xrplp00`, `Ym_Xrplp01`,
  `Ym_zan2`, `Ym_zan2_R_A`, `Ym_zan2_R_2A`, `Ym_zan2Noutouy`,
  `Ym_KinBlade`, `Ym_XKinBlade`, `Ym_kin_6LP`, `Ym_kin_X6LP`,
  `Ym_kin4rp`, `Ym_kin4rplp`, `Ym_Xkin4rplp`, `Ym_getuki00`,
  `Ym_Xgetuki00`, `Ym_Heli04`
- Diablo: `He_lp00F`, `He_WK00F_LP`, `He_yamazuki`, `He_44LRP`,
  `He_lk01B`, `He_4lkrp`, `He_lk02B`, `He_s_tlp00`, `He_s_tlk00`,
  `He_s_tlkwp`, `He_m_p01`, `He_3lplpRev`, `He_kawara`,
  `He_dslpZ`, `He_dslp30`, `He_RageArts_n2`
- Skull: `Co_sjprk01F`, `Co_sjprk02F`, `Co_sjprk03F`,
  `Bx_lrplp`, `Bx_rk00`, `Bx_hiRK_LKrv`, `Bx_23rp`, `Bx_23rplp`,
  `Bx_2RLpunch`, `Bx_sphiji_EX`, `Bx_Sway_RK`, `Bx_Relbow`,
  `Bx_RageArts_nB`
- Sam-∪R-Λ1: `Jc_lrp00`, `Jc_lrp02`, `Jc_6LPLP`, `Jc_6LPRPLP`,
  `Jc_lk00F`, `Jc_6lkwpRv`, `Jc_6lkwpRv2`, `Jc_6lkrp`,
  `Jc_lp00B`, `Jc_4lprp`, `Jc_lrp_sp2`, `Km_halp00`,
  `Km_halp00E`, `Pj_genkrp00`
- Saku Ra: `Fu_seiou00`, `Fu_t_srp00B`, `Co_s_tlp00`,
  `Co_s_tlprk`, `Fu_R_lowrk`, `Fu_lrpF00`

Note, not a conclusion: `Co_sjprk01F/02F/03F` appear in Skull's
inline gap as they do in King, Demonio, Burger and Bruno — the same
shared story-bank clips, not independent gaps. They are still
counted per fighter above, because per-fighter coverage is what
this record measures.

## What this does NOT claim

- The 0x64 joint-frame fix is still open: these clips decode, but
  0x64 attack clips decode crumpled including frame 1 (BUILD-LOG
  2026-10-29 18:00 finding). Clipmap resolution is clip identity,
  not pose quality — baking still waits on the joint-frame fix. No
  clip is claimed bake-ready by this record.
- No T7 clip is wired into the game by this chunk: no
  `game/assets/anim/t7/` bank, no `anim_t7` refs, no `_attackClipPlan`
  change. Wiring is programme step (f) and still needs the bake
  (step (e)), which still needs the joint-frame fix (step (a)).
- The 33 T7 overlay characters in the #1259 inventory are not in
  this record: their clipmap runs are the remaining step-3 item.

## Next steps named by this record

1. The 0x64 joint-frame fix (step (a)) — still gated on paired
   0xC8/0x64 GRE data or a named community source; no guessed
   rotation.
2. The inline attacks (66 across these five, 70 across the core-8
   five, 14 for King): community-extracted source first, then
   T3/VF5 fill documented per move (programme step (g)).
3. The same extended clipmap for the 33 T7 overlay characters in
   the #1259 inventory, in this format, so their 0x8000 splits are
   measured, not assumed.
