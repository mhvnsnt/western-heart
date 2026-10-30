# T7 clipmap runs for the other five T7 core-8 bases (2026-10-30)

Programme step (c), next step 1 named by
`docs/proof/t7-clipmap-king-common-20261030.md`: the same extended
clipmap (with `common.arc`) that closed King's 0x8000 gap in PR #1260,
run for the other five T7-applicable core-8 fighters. Tool unchanged
(`tools/anim/t7_clipmap.py` as extended in #1260, optional 4th argument
`common.arc`); this chunk is a measurement run + record only.

## Sources (all read from the GRE repo, main state at run time)

Private repo `mhvnsnt/game-reverse-engineering`, tree
`teardown/tekken7-steam/tkdata/mothead/` — every file fetched by its
git blob SHA and verified (blob SHA = SHA-1 of `blob <len>\0` +
content) before use; all 11 SHA checks passed:

- `mask/common.arc` — 5,049,396 bytes, blob
  `80453212f9a2a2d526a36991e40841dd01959c3f` (identical to the #1260
  blob — the same shared bank, not a second copy)
- `json/jinmot.json` 6,468,588 bytes, `mask/jinrotsm.arc` 5,417,296 bytes
- `json/mrxmot.json` 7,137,930 bytes, `mask/mrxrotsm.arc` 8,019,328 bytes
- `json/asamot.json` 7,298,226 bytes, `mask/asarotsm.arc` 6,025,040 bytes
- `json/bobmot.json` 6,595,910 bytes, `mask/bobrotsm.arc` 5,366,256 bytes
- `json/migmot.json` 6,257,871 bytes, `mask/migrotsm.arc` 5,206,720 bytes

Method, same bank rule as King: first `MOTA` block, clip index
`anim_id & 0x3FFF`, type byte at the clip offset (`0x64` = full
`Anim64` decode, `0xC8` = frame count from the header). Every
rotsm/common attack row in every output carries a decoded `fmt` +
frame count (verified: 0 attack rows missing a decoded format), so
these counts are decoded clips, not listed indices. Exit 0 and
`decode_errors` 0 on all five runs.

## Result — coverage in the King format

| WH fighter | T7 base | Rotsm clips | Moves | Attacks | Resolved | Inline gap |
|---|---|---|---|---|---|---|
| Demonio | Jin Kazama | 670 | 2,227 | 360 | 352 / 360 = 97.8% | 8 |
| Dio | Akuma | 647 | 2,094 | 319 | 313 / 319 = 98.1% | 6 |
| Cyborg X | Alisa Bosconovitch | 832 | 2,464 | 510 | 482 / 510 = 94.5% | 28 |
| Burger | Bob Richards | 656 | 2,325 | 403 | 390 / 403 = 96.8% | 13 |
| Bruno | Miguel Caballero Rojo | 577 | 2,241 | 345 | 330 / 345 = 95.7% | 15 |

Bank split (attacks) per fighter:

| Fighter | 0x4000 rotsm | 0x8000 common | 0x0000 inline |
|---|---|---|---|
| Demonio | 273 | 79 | 8 |
| Dio | 253 | 60 | 6 |
| Cyborg X | 412 | 70 | 28 |
| Burger | 315 | 75 | 13 |
| Bruno | 256 | 74 | 15 |

Common bank: 1,711 clips in every run. Combined, the five runs
resolve 1,867 of 1,937 attacks (96.4%); the whole remaining gap
across the five is 70 inline attacks (8 + 6 + 28 + 13 + 15).

## Inline attacks (the whole remaining gap per fighter)

- Demonio: `Co_sjprk01F`, `Co_sjprk02F`, `Co_sjprk03F`,
  `Jz_zan_dslplk`, `Jz_zan_srk00`, `Jz_zan_srk00EX`,
  `Jz_karatekick`, `Jz_karate05`
- Dio: `Mx_66rplp2`, `Mx_3lrp`, `Mx_3lrparm`, `Co_s_tlp00`,
  `Ry_Shadoh`, `Ry_ShadohEX`
- Cyborg X: `Co_jplk00F`, `Aa_jprk00`, `Aa_jprkrk2`, `Aa_lk00`,
  `Aa_6rplp`, `Aa_4rkrk`, `Aa_chainsteLP`, `Aa_chainsteRP`,
  `Aa_chain2RP`, `Aa_chain2RP2`, `Aa_Cha2RPRoop`,
  `Aa_Cha2RPRoop2`, `Aa_Cha2RPRoop3`, `Aa_Cha2RPRoopEND`,
  `Aa_66RPLK_EX`, `Aa_TsStep_EX_Y`, `Aa_TsStep_chain_EX_Y`,
  `Aa_steLK`, `Aa_steLKc`, `Aa_steWP`, `Aa_moveK`,
  `Aa_RageArts00`, `Aa_RageArts02`, `Aa_RageArts02_miss`,
  `Aa_RageArts02_miss2`, `Aa_RageArts02_miss3`,
  `Aa_RageArts02_miss4`, `Aa_RageArts02_miss5`
- Burger: `Co_sjprk01F`, `Co_sjprk02F`, `Co_sjprk03F`,
  `Ft_623lkrk`, `Ft_rk02`, `Ft_t_slp00`, `Ft_renda`, `Ft_renda2`,
  `Ft_renda2R`, `Ft_renda3`, `Ft_3lplp`, `Ft_Froll00_EX`,
  `Ft_jprk00F`
- Bruno: `Mt_P_1rk`, `Co_sjprk01F`, `Co_sjprk02F`, `Co_sjprk03F`,
  `Mt_lk_rk`, `Mt_sennpuu`, `Mt_rk00`, `Mt_rp00F`, `Mt_rp00F_lp`,
  `Mt_rk00Frp`, `Mt_rp00B`, `Mt_rp00Brp`, `Mt_3rprp`, `Mt_43rk`,
  `Mt_jplp`

Note, not a conclusion: `Co_sjprk01F/02F/03F` appear in the inline
gap of Demonio, Burger and Bruno as well as King — the same shared
story-bank clips, not four independent gaps. They are still counted
per fighter above, because per-fighter coverage is what this record
measures.

## What this does NOT claim

- The 0x64 joint-frame fix is still open: these clips decode, but
  0x64 attack clips decode crumpled including frame 1 (BUILD-LOG
  2026-10-29 18:00 finding). Clipmap resolution is clip identity,
  not pose quality — baking still waits on the joint-frame fix. No
  clip is claimed bake-ready by this record.
- No T7 clip is wired into the game by this chunk: no
  `game/assets/anim/t7/` bank, no `anim_t7` refs, no
  `_attackClipPlan` change. Wiring is programme step (f) and still
  needs the bake (step (e)), which still needs the joint-frame fix
  (step (a)).
- Deathfang (KOF) and Chatur (T3-only) are not in this record: the
  T7 programme does not apply to them, per the #1259 inventory.

## Next steps named by this record

1. The 0x64 joint-frame fix (step (a)) — still gated on paired
   0xC8/0x64 GRE data or a named community source; no guessed
   rotation.
2. The inline attacks (70 across these five, 14 for King):
   community-extracted source first, then T3/VF5 fill documented
   per move (programme step (g)).
3. The same extended clipmap for the wider T7 roster (the 33
   overlay characters / owner-named T7 fighters in the #1259
   inventory), in this format, so their 0x8000 splits are measured,
   not assumed.
