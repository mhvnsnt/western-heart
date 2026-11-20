# Urban Reign Phase 6 — Name-Bridge Addendum (bank-completion re-run)

Method: the Phase-5 bridge (`tools/ur_name_bridge.py` gate logic, Phase-5
scratch runner semantics), gate UNCHANGED: **maxDev ≤ 0.10 mm over all
frames/components AND unique under the gate in the bank where the hit
lands**. Every Phase-5 unproven record (402) was re-run against the 241
banks newly decoded in Phase 6 (1,004 motions — see
`BANK-INVENTORY-PHASE6.json`). Full per-record results:
`PHASE6-RERUN-RESULTS.json` in this folder.

## Own-bank result: ZERO new own-bank proofs — by construction, stated plainly

No Phase-6 bank is any fighter's own pmot bank. The pmot set is closed:
the DVD000 AFS holds exactly 31 pmot PPKs and `tec/motion/gyuindex.bin`'s
populated slots are exactly those 31 (Phase 4, item 1) — all were decoded
and own-bank-searched in Phases 2/5. The newly decoded banks are shared /
demo / facial / debug banks. Therefore every Phase-6 hit is **cross-bank
evidence only** (per-character isolation), nothing was annotated, and the
own-bank totals are unchanged:

| | Phase 5 | Phase 6 |
|---|---|---|
| records held (27 fighters) | 886 | 886 |
| proven own-bank (= `motdatName` annotations) | 484 | **484 (unchanged)** |
| unproven own-bank | 402 | 402 |
| of unproven: identity proven in another bank | 306 | **307** |
| of unproven: no identity in any searched bank | 96 | **95** |

Cross-check (Phase 6, this branch): `motdatName` annotations counted in
`game/assets/movesets/ur-char*.json` = **484** == own-bank proven total 484.

## New cross-bank proofs in the Phase-6 banks (18 records)

All 18 land in the two banks embedded in `afs/safe/ppk/main.ppk`
(`main_bank1` @209024, 331 motions; `main_bank2` @1647872, 326 motions) —
banks Phase 5's Job 2 searched ONLY for the 5 P1 records; Phase 6 is the
first search of them for the other 397 unproven records. All hits are
unique under the gate in their bank; maxDev 0.0027–0.0398 mm.

| fighter | record | name | bank | motion | maxDev (mm) | rootType | already cross-proven in Phase 5? |
|---|---|---|---|---|---|---|---|
| char004 | 22 | `moco_lreversk` | main_bank1 | m270 | 0.0133 | 8 | yes |
| char021 | 11 | `cbmt_kamae` | main_bank1 | m199 | 0.0027 | 14 | yes |
| char022 | 5 | `cbco_lprp12` | main_bank1 | m077 | 0.0043 | 8 | yes |
| char030 | 10 | `cbco_tnuralp` | main_bank1 | m123 | 0.0118 | 8 | yes |
| char030 | 11 | `cbco_tnurarp` | main_bank1 | m125 | 0.0097 | 8 | yes |
| char031 | 10 | `cbco_tnuralp` | main_bank1 | m123 | 0.0118 | 8 | yes |
| char031 | 11 | `cbco_tnurarp` | main_bank1 | m125 | 0.0097 | 8 | yes |
| char032 | 1 | `cbca_kamae` | main_bank1 | m000 | 0.0075 | 14 | yes |
| char032 | 6 | `cbco_chuka_keriage2` | main_bank1 | m038 | 0.0157 | 8 | yes |
| char032 | 15 | `cbco_senpukyaku` | main_bank1 | m108 | 0.0398 | 8 | yes |
| char032 | 16 | `cbco_sensi01` | main_bank1 | m109 | 0.0356 | 8 | yes |
| char032 | 17 | `cbco_sensi02` | main_bank1 | m110 | 0.0304 | 8 | yes |
| char032 | 18 | `cbco_spd_chuka` | main_bank1 | m115 | 0.0343 | 8 | **NO — identity first proven in Phase 6** |
| char055 | 2 | `cbcb_nc01_lp` | main_bank1 | m003 | 0.0098 | 8 | yes |
| char057 | 4 | `cbco_chuka_keriage2` | main_bank1 | m038 | 0.0157 | 8 | yes |
| char057 | 12 | `cbco_senpukyaku` | main_bank1 | m108 | 0.0398 | 8 | yes |
| char059 | 25 | `moco_rreversk` | main_bank1 | m287 | 0.0126 | 8 | yes |
| char060 | 7 | `haam_kamae` | main_bank2 | m188 | 0.0032 | 14 | yes |

Net effect on the cross-bank total: 306 → **307** (only char032 rec18 is
newly identified; the other 17 records gain an additional bank of
evidence for an identity already proven elsewhere).

No hits at all in: `main_bank2` (except char060 rec7 above), `gyu_debug`,
the 35 `demo_motion` banks, or any of the 203 tec/demo facial / anim_obj /
effect banks — those banks' motions are cutscene-length (50–3,991 frames;
facial 101–1,117) and share a frame count with a re-run record in only a
handful of cases, none under the gate (per-record best deviations in
`PHASE6-RERUN-RESULTS.json`).

## The 5 unsourced P1 records — DO NOT CLOSE; the negative is now definitive

Re-run against all 241 new banks (plus the 44 Phase 2–5 banks from
Phase 5): **no hit for any of the five.** Best candidate in the new banks:

| record | name | frames | best new-bank candidate | maxDev (mm) |
|---|---|---|---|---|
| 6 | `cbco_screw_r` | 55 | main_bank1 m155 | 205.0333 |
| 10 | `moco_d_jumpk_f` | 90 | main_bank2 m190 | 1370.8431 |
| 11 | `moco_d_jumpk_y1` | 122 | main_bank2 m267 | 4342.6617 |
| 12 | `moco_d_jumpk_y2` | 122 | main_bank2 m267 | 1795.0018 |
| 14 | `moco_doubleairk_f` | 88 | main_bank2 m069 | 1079.4223 |

Their P2/P3 clone-list counterparts (char002/char003 records 6/10/11/12/14,
same names) likewise get no hit. With the searched set now covering every
motion bank in the shipped AFS set (see `../BANK-COMPLETION.md`), the
Phase-5 verdict stands and is definitive for shipped data: these records'
source bank is **not in the shipped AFS set** (the motdat test tool's
working banks / a variant bank never shipped); only a runtime capture
(PCSX2) could source them. NOT a decode gap — the type-14 decode is
proven and was applied to every bank here.

## Borderline pairs — unchanged

char042 rec50 (`moco_sp_paknage_y`), char055 rec34
(`moco_sp_lucacombo_y`), char057 rec32 (`moco_tp_scopionk_f2`): **no
motion in any Phase-6 bank even shares their frame count**, so no new
evidence touches them. They stay UNPROVEN under the gate (own-bank best
0.1361 / 0.1253 / 0.1020 mm from Phase 5; gate does not move).

## Per-fighter Phase-6 totals

| fighter | held | proven own-bank | unproven | of unproven: proven in another bank (Phase 6 total) |
|---|---|---|---|---|
| char001 | 35 | 27 | 8 | 3 |
| char002 | 35 | 27 | 8 | 3 |
| char003 | 35 | 27 | 8 | 3 |
| char004 | 24 | 9 | 15 | 14 |
| char016 | 44 | 33 | 11 | 8 |
| char020 | 34 | 21 | 13 | 8 |
| char021 | 40 | 31 | 9 | 7 |
| char022 | 32 | 21 | 11 | 6 |
| char030 | 37 | 25 | 12 | 12 |
| char031 | 37 | 25 | 12 | 12 |
| char032 | 39 | 27 | 12 | **7** (was 6 — rec18 `cbco_spd_chuka` identified in main_bank1) |
| char041 | 45 | 38 | 7 | 4 |
| char042 | 55 | 41 | 14 | 6 |
| char043 | 32 | 11 | 21 | 19 |
| char044 | 26 | 5 | 21 | 21 |
| char045 | 23 | 7 | 16 | 12 |
| char046 | 17 | 8 | 9 | 9 |
| char054 | 33 | 8 | 25 | 23 |
| char055 | 35 | 15 | 20 | 11 |
| char056 | 17 | 11 | 6 | 6 |
| char057 | 37 | 20 | 17 | 10 |
| char058 | 34 | 25 | 9 | 9 |
| char059 | 33 | 5 | 28 | 23 |
| char060 | 22 | 4 | 18 | 12 |
| char061 | 18 | 4 | 14 | 10 |
| char062 | 33 | 5 | 28 | 24 |
| char063 | 34 | 4 | 30 | 25 |
| **total** | **886** | **484** | **402** | **307** |
