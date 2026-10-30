# T7 clipmap runs for the first five T7 overlay characters (2026-10-30)

Programme step (c), next step 3 named by
`docs/proof/t7-clipmap-owner-named-20261030.md`: the same extended
clipmap (with `common.arc`) that closed King's 0x8000 gap in PR #1260
and measured the core-8 and owner-named fighters in PRs #1261/#1263,
run for the first five not-yet-clipmapped T7 overlay characters from
the #1259 inventory (`docs/anim/T7-SOURCE-INVENTORY-20261030.md`),
in inventory order. Tool unchanged (`tools/anim/t7_clipmap.py` as
extended in #1260, optional 4th argument `common.arc`); this chunk
is a measurement run + record only. These five are T7 overlay
characters held in western-heart as
`game/assets/movesets/t7/t7-<name>-lp-rp-lk-rk.json`, not
WH-named fighters — so the table below names the T7 character
itself, with its GRE code.

## Sources (all read from the GRE repo, main state at run time)

Private repo `mhvnsnt/game-reverse-engineering`, tree
`teardown/tekken7-steam/tkdata/mothead/` — every file listed by the
API with size + blob SHA and fetched by that blob SHA; fetched sizes
match the listing exactly for all 11 files, and every fetched
blob SHA re-verifies (SHA-1 of `blob <len>\0` + content):

- `mask/common.arc` — 5,049,396 bytes, blob
  `80453212f9a2a2d526a36991e40841dd01959c3f` (identical to the #1260
  blob — the same shared bank, not a second copy)
- `json/itamot.json` 5,942,812 bytes, blob
  `81d4c12479f24c7d442b2a16ce635c9e983a98c1`; `mask/itarotsm.arc`
  5,249,472 bytes, blob `f5003b9fb72f7d40b13d53e183daaf7d0aa7f10d`
- `json/dramot.json` 6,473,196 bytes, blob
  `07cbd75cc7a45235ac4ccd313e0cee781130f7a9`; `mask/drarotsm.arc`
  5,465,888 bytes, blob `04bb25742ef976277a781886d1c5d656c19d2fc2`
- `json/eddmot.json` 6,876,802 bytes, blob
  `974d399b53d8e3df0eb406bed21e7cc825467a3c`; `mask/eddrotsm.arc`
  5,594,928 bytes, blob `7a0ad6473e5cdcbd9fce31030b07304fd06c9820`
- `json/elzmot.json` 6,353,238 bytes, blob
  `a612306f688c60c98d2a00f95271f7b277d70a68`; `mask/elzrotsm.arc`
  5,583,152 bytes, blob `31c503d53c2c629edd6512df889ace915d43beb7`
- `json/nscmot.json` 5,968,000 bytes, blob
  `9a1e089514498fc0d1b242cdf7395b8cfb001e1d`; `mask/nscrotsm.arc`
  3,891,648 bytes, blob `534b1327490cb38a1bdfec21e95f2e387138b0b1`

Method, same bank rule as King: first `MOTA` block, clip index
`anim_id & 0x3FFF`, type byte at the clip offset (`0x64` = full
`Anim64` decode, `0xC8` = frame count from the header). Every
rotsm/common attack row in every output carries a decoded `fmt` +
frame count (verified: 0 attack rows missing a decoded format, all
`0x64`), so these counts are decoded clips, not listed indices.
Exit 0 and `decode_errors` 0 on all five runs. Common-bank attacks
were additionally full-frame decoded (`Anim64.frames()`) per
fighter, 0 errors throughout (see detail below).

## The NSC shared-bank finding (the #1259 flag, resolved, not assumed)

The inventory flagged `nsa`/`nsb`/`nsc`/`nsd` rotsm.arc as all
exactly 3,891,648 bytes and told the next run to verify distinct
content before use. Verified: they are not merely the same size —
all four carry the SAME blob SHA
`534b1327490cb38a1bdfec21e95f2e387138b0b1`, i.e. byte-identical
content in the GRE tree. Fahkumram's run below therefore joins
against that one shared bank (396 clips), not a Fahkumram-only
bank — and its low resolution (60.0%, see below) is the measured
consequence, not a tool failure: most of its attacks fall through
to the inline gap because the shared bank holds only 246 of its
moves. The same shared bank will govern Negan (NSA), Leroy (NSB)
and Lidia (NSD) when their runs land; their coverage should be
read against this finding, not against a per-character bank.

## Result — coverage in the King format

| T7 character | GRE code | Rotsm clips | Moves | Attacks | Resolved | Inline gap |
|---|---|---|---|---|---|---|
| Claudio Serafino | ITA | 540 | 2,109 | 341 | 320 / 341 = 93.8% | 21 |
| Sergei Dragunov | DRA | 669 | 2,254 | 390 | 380 / 390 = 97.4% | 10 |
| Eddy Gordo | EDD | 716 | 2,316 | 447 | 435 / 447 = 97.3% | 12 |
| Eliza | ELZ | 546 | 2,076 | 278 | 265 / 278 = 95.3% | 13 |
| Fahkumram | NSC | 396 | 2,089 | 345 | 207 / 345 = 60.0% | 138 |

Bank split (attacks) per fighter:

| Fighter | 0x4000 rotsm | 0x8000 common | 0x0000 inline |
|---|---|---|---|
| Claudio Serafino | 246 | 74 | 21 |
| Sergei Dragunov | 303 | 77 | 10 |
| Eddy Gordo | 362 | 73 | 12 |
| Eliza | 204 | 61 | 13 |
| Fahkumram | 132 | 75 | 138 |

Common bank: 1,711 clips in every run. Combined, the five runs
resolve 1,607 of 1,801 attacks (89.2%); the whole remaining gap
across the five is 194 inline attacks (21 + 10 + 12 + 13 + 138),
of which Fahkumram alone is 138.

Common-bank attack detail (same shared bank in every run, so the
range repeats): clip indices 2–1647 in all five runs, all type
`0x64`, per-attack frames 3–232. Distinct common clips and
full-frame decode totals per fighter: Claudio 68 distinct clips,
5,532 frames; Dragunov 67, 5,391 frames; Eddy 67, 5,437 frames;
Eliza 55, 4,808 frames; Fahkumram 69, 5,529 frames — 0 errors.

## Inline attacks (the whole remaining gap per fighter)

- Claudio Serafino: `Co_sjprk01F`, `Co_sjprk02F`, `Co_sjprk03F`,
  `It_lprpF`, `It_lplkF`, `It_4lp`, `It_quetzalnn`, `It_quetzal2n`,
  `It_quetzal`, `It_quetzal2`, `It_4rklkrp`, `It_4rklkrpn`,
  `It_4rklp`, `It_2lprp_n`, `It_2lprp2`, `It_4rp`, `It_4lklk`,
  `It_s_tlprpn`, `It_s_tlprp`, `It_66lrp`, `It_chest`
- Sergei Dragunov: `Cn_blind`, `Co_sjprk01F`, `Co_sjprk02F`,
  `Co_sjprk03F`, `Cn_lklprk`, `Cn_urakenNSP`, `Cn_lplkrpuraNSP`,
  `Cn_3lrk`, `Cn_RageArts_n2`, `Cn_RageArts_n2_km`
- Eddy Gordo: `Cp_jprk00`, `Co_sjprk01F`, `Co_sjprk02F`,
  `Co_sjprk03F`, `Cp_6rplk`, `Cp_45lk00`, `Cp_06lk00`, `Cp_4rplk`,
  `Cp_4rplklk`, `Cp_66lrk_EX`, `Cp_66lrk_EX2`, `Cp_66lrk_EX3`
- Eliza: `Vp_6lk`, `Vp_syalk00`, `Jn_syark00`, `Co_R_clk00L`,
  `Co_R_crk00R`, `Vp_t_slk00`, `Co_t_srk00`, `Vp_4lprprk`,
  `Vp_9lrp2`, `Vp_shoryulp`, `Vp_shoryulprk`, `Vp_66lklk`,
  `Vp_shoryuAB_n`
- Fahkumram: `Co_wDASH_lk00`, `Nc_jplp00F`, `Nc_jplp00`,
  `Nc_jplp00B`, `Nc_jprp00F`, `Nc_jprp00Farm`, `Co_jplk00`,
  `Co_jplk00F`, `Co_jplk00B`, `Nc_RageD3`, `Nc_RageD_n`,
  `Nc_RageD_nl`, `Nc_RageD_nr`, `Co_jprk00`, `Co_jprk00F`,
  `Co_jprk00B`, `Co_sjprk01F`, `Co_sjprk02F`, `Co_sjprk03F`,
  `Nc_lp00F`, `Nc_lphizi`, `Nc_lprp00`, `Nc_rplp00`,
  `Nc_lprplprk`, `Nc_lprk00`, `Nc_rp00`, `Nc_rprk`, `Nc_lk00`,
  `Nc_lkrk`, `Nc_lkrklk`, `Nc_lkrklkN`, `Nc_lkrkrk`, `Nc_lklp`,
  `Nc_lklprp`, `Nc_lklp2rk`, `Nc_lklprk`, `Nc_lklprkrk`,
  `Nc_rk00`, `Nc_rkrk`, `Nc_rkrk_n`, `Nc_rklk`, `Nc_RageD`,
  `Nc_RageD2h`, `Nc_RageD2`, `Nc_RageD4`, `Nc_RageD5h`,
  `Nc_RageD5`, `Nc_rklklp`, `Nc_rklkrk`, `Nc_rklkrkN`,
  `Nc_yokork`, `Nc_WK00`, `Nc_rp00F`, `Nc_6rplp`, `Nc_66RP`,
  `Nc_66rplp`, `Nc_6lrp`, `Nc_66WP`, `Nc_6lk`, `Nc_6lkrp`,
  `Nc_6lkrprk`, `Nc_6lkrplp`, `Nc_66LK`, `Nc_66RK`, `Nc_66rklp`,
  `Nc_66RKlk`, `Nc_66RKlkrpy`, `Nc_66rklkrp`, `Nc_WK00F`,
  `Nc_WK00Farm`, `Nc_lp00B`, `Nc_rp00B`, `Nc_4rpclp`,
  `Nc_4rplp`, `Nc_4rplk`, `Nc_lk00B`, `Nc_NLauncher`,
  `Nc_GuardH`, `Nc_rk00B`, `Nc_rk00B2`, `Nc_4rklkrp`,
  `Nc_4lrklk1`, `Nc_4lrklk2`, `Nc_4lrklk3`, `Nc_syarp00`,
  `Co_syalk00`, `Nc_23lk`, `Nc_23lkrpy`, `Nc_2lp`,
  `Nc_t_srp00`, `Nc_1rprp`, `Nc_2rp`, `Co_t_slk00`,
  `Nc_t_slk00`, `Nc_2lkrk`, `Co_t_srk00`, `Nc_t_srk00`,
  `Nc_t_sWK00`, `Nc_2lrk`, `Nc_2lrk2`, `Co_t_slpF`,
  `Nc_3lprp`, `Nc_3lprplp`, `Nc_3lprk`, `Co_t_srpF`,
  `Nc_3rplp`, `Nc_3rplk`, `Nc_t_slkF`, `Co_t_srkF`,
  `Nc_3rklk`, `Nc_3rklklk`, `Co_s_tlp00`, `Co_s_tlprp`,
  `Co_s_trp00`, `Nc_s_trprk`, `Co_s_tlk00`, `Co_s_trk00`,
  `Co_runlk00`, `Nc_10com3`, `Nc_10com4`, `Nc_10com5`,
  `Nc_10com6`, `Nc_10com7`, `Nc_10com8`, `Nc_10com9`,
  `Nc_10com10`, `Thrmv_B2_01`, `Nc_FLnage_n`, `Nc_FRnage_n`,
  `Nc_FRnage_nb`, `Nc_LSide_n`, `Nc_RSide_n`, `Nc_RSide_nb`,
  `Nc_Bnage_n`, `Nc_Bnage_nb`, `Nc_com_n`, `Nc_RageArts02`,
  `Nc_RageArts_n`

Note, not a conclusion: `Co_sjprk01F/02F/03F` appear in the inline
gap of Claudio, Dragunov and Eddy as they do in King, Demonio,
Burger, Bruno and the owner-named runs — the same shared
story-bank clips, not independent gaps. They are still counted
per fighter above, because per-fighter coverage is what this
record measures.

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
- Fahkumram's 60.0% is a source-bank limit, not a measurement
  failure: its GRE rotsm bank is the shared nsa/nsb/nsc/nsd file
  (see above). A Fahkumram-only bank, if one exists in another
  extraction, is a separate source hunt — not assumed here, and
  no closest-match clip is substituted.
- The remaining 26 T7 overlay files are not in this record: their
  clipmap runs are the remaining step-3 item, in directory order
  (Feng Wei next, then Ganryu, Geese Howard, Gigas, Hwoarang, and
  on through the list; the already-clipmapped overlays Akuma,
  Alisa, Jack-7, Ling Xiaoyu and Miguel are skipped as measured,
  not re-run). Count note: `game/assets/movesets/t7/` on main at
  run time holds 36 `t7-*.json` overlay files, not the 33 the
  #1259 inventory text states — 10 are now measured (the five
  above plus the five already-clipmapped overlays), leaving 26.

## Next steps named by this record

1. The 0x64 joint-frame fix (step (a)) — still gated on paired
   0xC8/0x64 GRE data or a named community source; no guessed
   rotation.
2. The inline attacks (194 across these five, 138 of them
   Fahkumram's): community-extracted source first, then T3/VF5
   fill documented per move (programme step (g)). For Fahkumram
   the fill question comes first: whether a character-specific
   bank exists anywhere, since the GRE bank is shared.
3. The same extended clipmap for the remaining 26 T7 overlay
   files, in this format, so their 0x8000 splits are measured,
   not assumed.
