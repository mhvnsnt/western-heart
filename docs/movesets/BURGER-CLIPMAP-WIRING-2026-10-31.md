# Burger Clip-Map Wiring — 2026-10-31

Owner ruling (2026-10-31, tapped + typed in chat): **"Wire the 89 clip-map fills now."**
This wiring overrides burger.json's class 1-S (source-pending) status for the
clip-map specifically, on the owner's word. Executed on `burger.json` only.

## What was wired

Of the 111 `anim_ref: "UNMAPPED:t7-clip-pending"` entries in burger.json, the
clip-map (`game/assets/anim/t7/clip-maps/burger-clip-map.json`) holds 89 mapped:
86 with a resolved clip file and 3 in bank 0x0000 with no clip file. The **86
clip-resolved entries are wired**; the 3 bank-0 entries and the 22 unmapped
entries stay UNMAPPED (25 total, listed by name below).

Per wired entry, line-level edits only:

- `anim_ref` set to the T7 wiring: `t7:bob:<t7_id>` where the clip-map carries
  a frame-data id (49 entries — the same form as burger.json's 281 existing
  T7-wired entries, which also set `t7_move_id`), or `t7:bob:anim:<anim_id>`
  where the clip-map resolved the move by motbin walk and no frame-data id
  exists (37 entries; the anim_id is the clip's real MOTA id — no bob_N id was
  invented for these).
- `t7_move_id` set alongside, for the 49 with a frame-data id.
- `anim_t7` record added to all 86, carrying the clip-map resolution verbatim:
  motbin move id/name, anim name/id, clip bank/section/entry, source arc,
  blob file, clip sha256, format word, confidence, and the match note
  "clip-map resolved (burger-clip-map.json) — wired under owner ruling 2026-10-31".

No other field of any entry was changed (verified by recursive structural
diff: outside the 86 entries the file is identical; inside them only
`anim_ref`, `t7_move_id`, `anim_t7` differ). No t3_row, throw, class, or
frame-data edits. The show-animation lock (2026-10-23) is respected: no show
anims were added. burger.json's UNMAPPED count: **111 → 25**.

## The 86 wired keys

| WH key | anim_ref | T7 anim | anim_id | clip bank / entry (source) | confidence |
|---|---|---|---|---|---|
| `1+2+3+4` | `t7:bob:anim:16995` | ikfa_power_up(DVD) | 16995 | 0x4000 / 611 (bobrotsm.arc) | medium |
| `1+2+3+4*` | `t7:bob:anim:16995` | ikfa_power_up(DVD) | 16995 | 0x4000 / 611 (bobrotsm.arc) | medium |
| `1+2,1+2` | `t7:bob:bob_39` | ikfa_utituke_wp_utiage(DVD) | 16729 | 0x4000 / 345 (bobrotsm.arc) | medium |
| `1+3~t8.bob` | `t7:bob:anim:33477` | naco_tukami2l(DVD) | 33477 | 0x8000 / 709 (common.arc) | high |
| `1,1` | `t7:bob:bob_3` | amfa_lplp(DVD) | 16711 | 0x4000 / 327 (bobrotsm.arc) | medium |
| `1,1,2` | `t7:bob:bob_5` | amfa_lplprp(DVD) | 16712 | 0x4000 / 328 (bobrotsm.arc) | high |
| `1,4` | `t7:bob:bob_18` | amfa_lp_rk(DVD) | 16718 | 0x4000 / 334 (bobrotsm.arc) | high |
| `1~t8.bob` | `t7:bob:bob_2` | ikfa_sylp(DVD) | 16788 | 0x4000 / 404 (bobrotsm.arc) | medium |
| `2+4~t8.bob` | `t7:bob:anim:16902` | ikfa_rtukami(DVD) | 16902 | 0x4000 / 518 (bobrotsm.arc) | high |
| `2,1,4` | `t7:bob:bob_25` | amfa_lprp_asi(DVD) | 16726 | 0x4000 / 342 (bobrotsm.arc) | high |
| `3+4` | `t7:bob:anim:16738` | ikfa_lk_ver2(DVD) | 16738 | 0x4000 / 354 (bobrotsm.arc) | medium |
| `b+1` | `t7:bob:bob_154` | ikfa_hiji(DVD) | 16771 | 0x4000 / 387 (bobrotsm.arc) | medium |
| `b+1+2,1` | `t7:bob:bob_175` | amfa_atama_open(DVD) | 16778 | 0x4000 / 394 (bobrotsm.arc) | medium |
| `b+1+2,1,2` | `t7:bob:bob_177` | amfa_atama_open_p(DVD) | 16779 | 0x4000 / 395 (bobrotsm.arc) | high |
| `b+1+2__main` | `t7:bob:bob_174` | amfa_atama(DVD) | 16777 | 0x4000 / 393 (bobrotsm.arc) | medium |
| `b+1,2` | `t7:bob:bob_155` | ikfa_hiji_st_body_blow(DVD) | 16772 | 0x4000 / 388 (bobrotsm.arc) | high |
| `b+2,2` | `t7:bob:bob_159` | amfa_B_combo2(DVD) | 16774 | 0x4000 / 390 (bobrotsm.arc) | medium |
| `b+2,2,4` | `t7:bob:bob_161` | amfa_B_combo3(DVD) | 16775 | 0x4000 / 391 (bobrotsm.arc) | medium |
| `b+2,2,4,4` | `t7:bob:bob_164` | amfa_B_combo4(DVD) | 16776 | 0x4000 / 392 (bobrotsm.arc) | high |
| `b+2__main` | `t7:bob:bob_158` | amfa_b_combo1_13(DVD) | 16773 | 0x4000 / 389 (bobrotsm.arc) | medium |
| `b+3` | `t7:bob:bob_168` | amfa_keriage(DVD) | 16781 | 0x4000 / 397 (bobrotsm.arc) | high |
| `b+3+4` | `t7:bob:bob_257` | ikfa_terada_rk(DVD) | 16786 | 0x4000 / 402 (bobrotsm.arc) | medium |
| `b+4,4` | `t7:bob:bob_172` | amfa_B_combo4(DVD) | 16776 | 0x4000 / 392 (bobrotsm.arc) | high |
| `b+4__main` | `t7:bob:bob_169` | amfa_hiza(DVD) | 16783 | 0x4000 / 399 (bobrotsm.arc) | medium |
| `BT.d+2` | `t7:bob:anim:16801` | amfa_Body(DVD) | 16801 | 0x4000 / 417 (bobrotsm.arc) | high |
| `d+1+2,2,1` | `t7:bob:bob_128` | ikfa_finisher02(DVD) | 16812 | 0x4000 / 428 (bobrotsm.arc) | medium |
| `d+2` | `t7:bob:bob_100` | amfa_Body(DVD) | 16801 | 0x4000 / 417 (bobrotsm.arc) | high |
| `d+2,1` | `t7:bob:bob_101` | amfa_Body_UP(DVD) | 16802 | 0x4000 / 418 (bobrotsm.arc) | medium |
| `d+2,1,2` | `t7:bob:bob_103` | amfa_body_up_body(DVD) | 16803 | 0x4000 / 419 (bobrotsm.arc) | medium |
| `d+2,1,2,2` | `t7:bob:bob_106` | amfa_body_sunkei(DVD) | 16804 | 0x4000 / 420 (bobrotsm.arc) | high |
| `d+2,3` | `t7:bob:bob_110` | amfa_body_kaitenhiza(DVD) | 16805 | 0x4000 / 421 (bobrotsm.arc) | high |
| `d+2,4` | `t7:bob:bob_112` | amfa_Body_KICK(DVD) | 16806 | 0x4000 / 422 (bobrotsm.arc) | high |
| `d+3` | `t7:bob:bob_114` | ikfa_2lk(DVD) | 16814 | 0x4000 / 430 (bobrotsm.arc) | medium |
| `d+3+4` | `t7:bob:bob_133` | ikfa_utiage_k(DVD) | 16817 | 0x4000 / 433 (bobrotsm.arc) | high |
| `d+3,4` | `t7:bob:bob_115` | ikfa_2lk_rk(DVD) | 16815 | 0x4000 / 431 (bobrotsm.arc) | high |
| `d+4` | `t7:bob:bob_117` | ikfa_l_lowkick(DVD) | 16874 | 0x4000 / 490 (bobrotsm.arc) | medium |
| `d+4,3` | `t7:bob:bob_118` | ikfa_l_low_high_k(DVD) | 16875 | 0x4000 / 491 (bobrotsm.arc) | medium |
| `d+4,3,4` | `t7:bob:bob_120` | ikfa_l_low_high_mid_k(DVD) | 16876 | 0x4000 / 492 (bobrotsm.arc) | high |
| `db+1` | `t7:bob:anim:16835` | kzco_sylp01_10f(DVD) | 16835 | 0x4000 / 451 (bobrotsm.arc) | medium |
| `db+1+2` | `t7:bob:anim:16838` | amfa_syagami_up(DVD) | 16838 | 0x4000 / 454 (bobrotsm.arc) | high |
| `db+2` | `t7:bob:anim:16837` | amfa_st_body_blow(DVD) | 16837 | 0x4000 / 453 (bobrotsm.arc) | high |
| `db+3` | `t7:bob:anim:16839` | kofa_1lk(DVD) | 16839 | 0x4000 / 455 (bobrotsm.arc) | high |
| `db+3+4` | `t7:bob:anim:16846` | ikfa_lowkick(DVD) | 16846 | 0x4000 / 462 (bobrotsm.arc) | medium |
| `db+3+4,4` | `t7:bob:anim:16846` | ikfa_lowkick(DVD) | 16846 | 0x4000 / 462 (bobrotsm.arc) | high |
| `db+4` | `t7:bob:anim:16840` | amfa_suimen2(DVD) | 16840 | 0x4000 / 456 (bobrotsm.arc) | medium |
| `db+4,4` | `t7:bob:anim:16841` | amfa_suimen2_jumpk(DVD) | 16841 | 0x4000 / 457 (bobrotsm.arc) | medium |
| `db+4,4,3` | `t7:bob:anim:16842` | amfa_suimen2_jumpk_lk(DVD) | 16842 | 0x4000 / 458 (bobrotsm.arc) | medium |
| `db+4,4,3,3` | `t7:bob:anim:16843` | amfa_suimen2_jumpk_lk_lk(DVD) | 16843 | 0x4000 / 459 (bobrotsm.arc) | high |
| `df+1,2` | `t7:bob:anim:16820` | amfa_3lp_rp(DVD) | 16820 | 0x4000 / 436 (bobrotsm.arc) | high |
| `df+2` | `t7:bob:anim:16790` | ikfa_syrp(DVD) | 16790 | 0x4000 / 406 (bobrotsm.arc) | medium |
| `f+1+2` | `t7:bob:bob_260` | fayt_hara_attack(DVD) | 16749 | 0x4000 / 365 (bobrotsm.arc) | high |
| `f+2,3` | `t7:bob:bob_60` | amfa_Uraken_keriage(DVD) | 16747 | 0x4000 / 363 (bobrotsm.arc) | high |
| `f+2_t8` | `t7:bob:bob_59` | amfa_gail_uraken10(DVD) | 16746 | 0x4000 / 362 (bobrotsm.arc) | medium |
| `f+3+4` | `t7:bob:bob_246` | ikfa_jump_heel(DVD) | 16890 | 0x4000 / 506 (bobrotsm.arc) | medium |
| `f+3,4` | `t7:bob:bob_63` | ikfa_l_heel_rk(DVD) | 16753 | 0x4000 / 369 (bobrotsm.arc) | medium |
| `f+3_t8` | `t7:bob:bob_62` | ikfa_l_heel(DVD) | 16752 | 0x4000 / 368 (bobrotsm.arc) | medium |
| `f+4` | `t7:bob:bob_65` | ikfa_nage_kick(DVD) | 16754 | 0x4000 / 370 (bobrotsm.arc) | high |
| `f,F+2` | `t7:bob:bob_66` | fayt_rari2(DVD) | 16872 | 0x4000 / 488 (bobrotsm.arc) | medium |
| `f,F+4` | `t7:bob:bob_68` | ikfa_jump_rk_01(DVD) | 16887 | 0x4000 / 503 (bobrotsm.arc) | medium |
| `f,F+4,4` | `t7:bob:bob_69` | ikfa_jump_rk_01(DVD) | 16887 | 0x4000 / 503 (bobrotsm.arc) | medium |
| `f,f,F+3` | `t7:bob:anim:16886` | mbfa_66lk(DVD) | 16886 | 0x4000 / 502 (bobrotsm.arc) | medium |
| `f,f,F+3+4` | `t7:bob:anim:16890` | ikfa_jump_heel(DVD) | 16890 | 0x4000 / 506 (bobrotsm.arc) | medium |
| `f,n,d,df+1` | `t7:bob:anim:16731` | amfa_step_lp(DVD) | 16731 | 0x4000 / 347 (bobrotsm.arc) | medium |
| `f,n,d,df+1+2` | `t7:bob:anim:16751` | amfa_ryoute(DVD) | 16751 | 0x4000 / 367 (bobrotsm.arc) | medium |
| `f,n,d,df+1+2*` | `t7:bob:anim:16751` | amfa_ryoute(DVD) | 16751 | 0x4000 / 367 (bobrotsm.arc) | medium |
| `f,n,d,df+2` | `t7:bob:anim:16732` | amfa_apaka(DVD) | 16732 | 0x4000 / 348 (bobrotsm.arc) | medium |
| `f,n,d,df+3` | `t7:bob:anim:16733` | fass_step_lk(DVD) | 16733 | 0x4000 / 349 (bobrotsm.arc) | medium |
| `f,n,d,df+3,2` | `t7:bob:anim:16734` | ikfa_step_lk_rp(DVD) | 16734 | 0x4000 / 350 (bobrotsm.arc) | medium |
| `FC.db+1+2` | `t7:bob:anim:16838` | amfa_syagami_up(DVD) | 16838 | 0x4000 / 454 (bobrotsm.arc) | medium |
| `FC.df+2` | `t7:bob:anim:16795` | amfa_Uraken_A(DVD) | 16795 | 0x4000 / 411 (bobrotsm.arc) | high |
| `FC.df+2,1` | `t7:bob:anim:16796` | amfa_Uraken_B(DVD) | 16796 | 0x4000 / 412 (bobrotsm.arc) | medium |
| `FC.df+2,1,1+2` | `t7:bob:anim:16797` | amfa_Uraken_C(DVD) | 16797 | 0x4000 / 413 (bobrotsm.arc) | high |
| `SS.1+2` | `t7:bob:anim:16727` | ikfa_utituke_wp(DVD) | 16727 | 0x4000 / 343 (bobrotsm.arc) | medium |
| `u+1+2` | `t7:bob:bob_41` | ikfa_spin(DVD) | 16636 | 0x4000 / 252 (bobrotsm.arc) | medium |
| `u+3` | `t7:bob:anim:16882` | amfa_8lk(DVD) | 16882 | 0x4000 / 498 (bobrotsm.arc) | medium |
| `u+3+4` | `t7:bob:bob_43` | amfa_mox02(DVD) | 16816 | 0x4000 / 432 (bobrotsm.arc) | high |
| `ub+4` | `t7:bob:anim:16690` | sjplki00(DVD) | 16690 | 0x4000 / 306 (bobrotsm.arc) | medium |
| `uf+1+2` | `t7:bob:anim:16667` | ikfa_debu_attack(DVD) | 16667 | 0x4000 / 283 (bobrotsm.arc) | medium |
| `uf+3` | `t7:bob:anim:16884` | amfa_9lk(DVD) | 16884 | 0x4000 / 500 (bobrotsm.arc) | high |
| `uf+3+4` | `t7:bob:anim:16672` | ikfa_taekwondo_01(DVD) | 16672 | 0x4000 / 288 (bobrotsm.arc) | medium |
| `uf+3+4,4` | `t7:bob:anim:16672` | ikfa_taekwondo_01(DVD) | 16672 | 0x4000 / 288 (bobrotsm.arc) | high |
| `ws1` | `t7:bob:bob_207` | ikfa_sylp(DVD) | 16788 | 0x4000 / 404 (bobrotsm.arc) | medium |
| `ws1+2` | `t7:bob:bob_221` | ikfa_utituke_wp(DVD) | 16727 | 0x4000 / 343 (bobrotsm.arc) | medium |
| `ws2` | `t7:bob:bob_212` | ikfa_syrp(DVD) | 16790 | 0x4000 / 406 (bobrotsm.arc) | medium |
| `ws2,2` | `t7:bob:bob_215` | amfa_utiage_b(DVD) | 16858 | 0x4000 / 474 (bobrotsm.arc) | high |
| `ws3,3+4` | `t7:bob:bob_218` | ikfa_stlk_hip(DVD) | 16863 | 0x4000 / 479 (bobrotsm.arc) | high |

## Left UNMAPPED by name (25)

Bank 0x0000 — mapped, but no clip file exists in any pulled source:

- `d+1` — t7_id bob_99, bank 0x0000 entry 109: clip file not located in any pulled source (bank-0x0000 pakchunk, the same missing file as the blocked Steam pull).
- `d+1+2` — t7_id bob_123, bank 0x0000 entry 110: clip file not located in any pulled source (bank-0x0000 pakchunk, the same missing file as the blocked Steam pull).
- `d+1+2,2` — t7_id bob_125, bank 0x0000 entry 112: clip file not located in any pulled source (bank-0x0000 pakchunk, the same missing file as the blocked Steam pull).

Unmapped in the clip-map (no unique T7 counterpart proven; reasons recorded in
`burger-clip-map.json` per key):

- `1+2_t8`
- `1,2`
- `1,d+4`
- `4,3`
- `b,B+2+3`
- `df+1`
- `df+3`
- `df+4`
- `FC.df+4`
- `f,F+3`
- `f,n,d,df`
- `f,n,d,DF+4`
- `f,n,d,DF+4,1+2`
- `ws1,2`
- `ws1,3`
- `ws2,1`
- `ws3`
- `ws4`
- `2~t8.bob`
- `2,1~t8.bob`
- `3~t8.bob`
- `4~t8.bob`

## Variant files — untouched, still pending

`burger-demon.json`, `burger-speed-demon.json`, `burger-the-mouth.json` were
NOT touched by this wiring (out of scope of the ruling execution). They remain
class 1-S with their gaps UNMAPPED; wiring them is a separate step if the owner
orders it.

## Not play-verified

This is a data wiring from the clip-map supply layer (medium/high confidence
per entry, as recorded). No entry here is claimed play-verified; in-game
verification follows the standing play-verify gate.
