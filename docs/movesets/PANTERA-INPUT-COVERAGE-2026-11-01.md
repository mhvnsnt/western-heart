# Pantera — 238-input coverage (stepped probe), 2026-11-01

Measured with `tools/input-verify/input_coverage_probe.mjs`: a real quick
fight is booted, the game loop is paused, game time is stepped directly at
FIXED_DT 1/120 (no wall-clock waits), the input window is reset before
every input, and each of Pantera's 238 neutral-list inputs is fed through
`fighter.tryAttack` while the probe records the plan that fired and
whether an animation actually played (mixer weight + bind-pose fraction,
the same measurement as `tools/anim/move_coverage_probe.mjs`).

## Headline

- **Before the data fix: 201 OK, 37 TPOSE, 0 NOFIRE, 0 ERROR.**
  Every one of the 37 was a string continuation slot (step-plan kind).
- **Root cause:** those slots' `string_step_plans` steps were recorded
  `unmapped` (row: null). The engine's playability gate
  (`game/js/step-plan-bank.js`, Path A) plays a step only when its status
  is `verified` with a finite row — so the attack fired and no clip
  played; the body stayed in bind pose for the whole move.
- **The fix (this PR):** `tools/input-verify/promote_step_plans.py`
  promoted 72 steps across 31 plans in `game/assets/movesets/pantera.json`.
  A step was promoted only when two places in the same moveset agree on
  the row: the plan's `candidate_row` AND the prefix move's own record
  (its name cites the row, or a t3_row field) — and the row exists in the
  bound bank's `rows.pack.json`. Nothing was promoted on one source alone.
- **After the fix (re-measured with the same probe): 229 OK, 9 TPOSE,
  0 NOFIRE, 0 ERROR** — the per-input table below is the after-fix run.
  The repo's strike/throw unit test (`test/attack-anim.test.mjs`) passes
  against the fixed data.

## Still dead (9) — no honest promotion available

- `1+3,1` and `2+4,1`: their records cite rows 415 / 417, and the plans
  agree — but the bank's hit data (`hit_frames.json`) classifies both
  rows as throws while the slots are strikes. The repo's strike/throw
  test rejects the pairing and the engine's runtime gate would too, so
  the promotions are vetoed in the tool and the steps stay unmapped
  until the conflict is adjudicated.
- `1,2,1,1,2,4,4,4,1,3` and `1,2,1,1,3,3,4,3,2,1+2` (the 10-hit combos):
  plans exist, but every step after the first has no candidate row
  anywhere in the moveset data.
- `b+1+2,1+2`: the final step has no candidate row; the move record
  ("Back Swing") names no row.
- `d+1,2`: neither plan step has a candidate row.
- `d/b+1+2,3+4`, `3+4,3,2+3`, `WS+2,2`: no step plan exists for these
  slots at all.

## One more data conflict found, NOT resolved by guessing

The prefix `f+2` is cited as row 230 by its move record, while an
already-verified plan step for the same prefix plays row 111. Both
readings sit in the shipped data; this PR leaves them exactly as found
and flags the conflict here for a dedicated adjudication.

## Run environment

Run from a sparse checkout of main (d2cd6e20) served locally. Pantera's
model, animation banks, moveset and the game code are the repo's real
files. Other fighters' models are absent from a sparse checkout and the
loader's remote retries stall the fight-load queue, so the probe's
`--model-fallback` option served Pantera's own GLB for other fighters'
preload requests only; the measurement is untouched. Full checkouts do
not need the option.

---

# Input coverage (stepped probe): pantera — 238 neutral inputs

Tool: `tools/input-verify/input_coverage_probe.mjs` (game time stepped directly, FIXED_DT 1/120; no wall-clock waits).

**Tally: OK 229, TPOSE 9**; plan kinds: t7 65, anim 42, notation 12, step-plan 58, match 7, own 34, donor 20

Outcomes: OK = fired and an animation played from neutral. TPOSE = fired but the body stayed in bind pose (no animation). CHAIN-OK = a string continuation that stays in bind pose when fed cold from neutral but animates when the string is chained the way a player inputs it (chain pass: prefixes fed in turn, game time stepped between them). NOFIRE = the input layer rejected it. ERROR = probe-side failure.

## Non-OK inputs

| input | fired | animation / clip | kind | outcome | notes |
|---|---|---|---|---|---|
| `1+3,1` | yes |  | step-plan | TPOSE | KING 1+3,1_c36 (T3 king r415) — chained replay: NOFIRE |
| `1,2,1,1,2,4,4,4,1,3` | yes |  | step-plan | TPOSE | 10 Hit Combo 1 — chained replay: TPOSE |
| `1,2,1,1,3,3,4,3,2,1+2` | yes |  | step-plan | TPOSE | 10 Hit Combo 2 — chained replay: TPOSE |
| `2+4,1` | yes |  | step-plan | TPOSE | KING 2+4,1_c36 (T3 king r417) — chained replay: NOFIRE |
| `b+1+2,1+2` | yes |  | step-plan | TPOSE | Back Swing — chained replay: NOFIRE |
| `d+1,2` | yes |  | step-plan | TPOSE | Move d+1 (d+1) — chained replay: NOFIRE |
| `d/b+1+2,3+4` | yes |  | step-plan | TPOSE | Jaguar Sprint — chained replay: NOFIRE |
| `3+4,3,2+3` | yes |  | step-plan | TPOSE | Sobat — chained replay: NOFIRE |
| `WS+2,2` | yes |  | step-plan | TPOSE | Move ws2 (ws2) — chained replay: TPOSE |

## All inputs

| input | fired | animation / clip | kind | outcome | notes |
|---|---|---|---|---|---|
| `1` | yes | t7:1~t7.king | t7 | OK | real T7 Kg_lp00F (kgkb_s3_lp00) |
| `2` | yes | t7:2~t7.king | t7 | OK | real T7 Kg_rp00 (ygkg_rp00_DVD) |
| `3` | yes | t7:3~t7.king | t7 | OK | real T7 Kg_lk00 (ygvt_lk00_DVD) |
| `4` | yes | t7:4~t7.king | t7 | OK | real T7 Kg_rk00 (mokg_hrk_DVD) |
| `1+2` | yes | t7:1+2~t7.king | t7 | OK | real T7 Kg_hiziru (Mkg_hijiupA_DVD) |
| `1+2+3+4` | yes | row:195 | anim | OK | Ki Charge |
| `1+2,1` | yes | t7:1+2~t7.king | t7 | OK | real T7 Kg_hiziru (Mkg_hijiupA_DVD) |
| `1+2,3` | yes | t7:1+2~t7.king | t7 | OK | real T7 Kg_hiziru (Mkg_hijiupA_DVD) |
| `1+3` | yes | row:127 | notation | OK | same input '1+3' |
| `1+3,1` | yes |  | step-plan | TPOSE | KING 1+3,1_c36 (T3 king r415) — chained replay: NOFIRE |
| `1+4` | yes | row:153 | anim | OK | Honest Hold [WH SIGNATURE] |
| `1+4,1` | yes | row:233 | step-plan | OK | step-plan last step (1+4,1) |
| `1+4,1,1` | yes | row:234 | step-plan | OK | step-plan last step (1+4,1,1) |
| `1,1` | yes | row:584 | step-plan | OK | step-plan last step (1,1) |
| `1,2` | yes | t7:1~t7.king | t7 | OK | real T7 Kg_lp00F (kgkb_s3_lp00) |
| `1,2,1` | yes | t7:1~t7.king | t7 | OK | real T7 Kg_lp00F (kgkb_s3_lp00) |
| `1,2,1,1,2,4,4,4,1,3` | yes |  | step-plan | TPOSE | 10 Hit Combo 1 — chained replay: TPOSE |
| `1,2,1,1,3,3,4,3,2,1+2` | yes |  | step-plan | TPOSE | 10 Hit Combo 2 — chained replay: TPOSE |
| `1,2,1,2+4` | yes | row:127 | anim | OK | Suplex |
| `1,2,1,d+2+4` | yes | row:127 | anim | OK | V Driver |
| `1,2,2+4` | yes | row:127 | anim | OK | Head Jammer |
| `1,2,d+2+4` | yes | row:127 | anim | OK | V Driver |
| `2+3` | yes | row:237 | match | OK | btn 6 null m hit@25f |
| `2+3,1` | yes | row:632 | step-plan | OK | step-plan last step (2+3,1) |
| `2+4` | yes | row:128 | notation | OK | same input '2+4' |
| `2+4,1` | yes |  | step-plan | TPOSE | KING 2+4,1_c36 (T3 king r417) — chained replay: NOFIRE |
| `2,1` | yes | t7:2~t7.king | t7 | OK | real T7 Kg_rp00 (ygkg_rp00_DVD) |
| `3+4` | yes | row:66 | anim | OK | Jaguar Step |
| `3+4,1+4` | yes | row:289 | match | OK | throw btn 9 null t hit@12f |
| `3,2` | yes | t7:3~t7.king | t7 | OK | real T7 Kg_lk00 (ygvt_lk00_DVD) |
| `3,2,2` | yes | t7:3~t7.king | t7 | OK | real T7 Kg_lk00 (ygvt_lk00_DVD) |
| `3,2,2*` | yes | t7:3~t7.king | t7 | OK | real T7 Kg_lk00 (ygvt_lk00_DVD) |
| `b` | yes | row:37 | own | OK | PANTERA b (T3 king r37) |
| `b+1` | yes | t7:b+1~t7.king | t7 | OK | real T7 Kg_lp00B (skkg_flp_DVD) |
| `b+1+2` | yes | row:279 | notation | OK | same input 'b+1+2' |
| `b+1+2,1+2` | yes |  | step-plan | TPOSE | Back Swing — chained replay: NOFIRE |
| `b+1+2,1+3` | yes | row:127 | donor | OK | donor row 127 |
| `b+1+2,1,1+3` | yes | row:463 | step-plan | OK | step-plan last step (b+1+2,1,1+3) |
| `b+1+2,1,2+4` | yes | row:467 | step-plan | OK | step-plan last step (b+1+2,1,2+4) |
| `b+1+2,1,3+4` | yes | row:471 | step-plan | OK | step-plan last step (b+1+2,1,3+4) |
| `b+1+2,2` | yes | row:98 | step-plan | OK | step-plan last step (b+1+2,2) |
| `b+1+2,2+4` | yes | row:128 | donor | OK | donor row 128 |
| `b+1+2,3+4` | yes | row:435 | donor | OK | donor row 435 |
| `b+1+3` | yes | row:35 | anim | OK | Arm Whip |
| `b+1,2` | yes | t7:b+1~t7.king | t7 | OK | real T7 Kg_lp00B (skkg_flp_DVD) |
| `b+1,4` | yes | t7:b+1~t7.king | t7 | OK | real T7 Kg_lp00B (skkg_flp_DVD) |
| `b+2` | yes | t7:b+2~t7.king | t7 | OK | real T7 Kg_rp00B (kgkb_s3_rap) |
| `b+2+3` | yes | row:283 | own | OK | PANTERA b+2+3 throw (T3 king r283) |
| `b+2+4` | yes | row:35 | anim | OK | Spinning Heel Hold |
| `b+2+4:3+4` | yes | row:195 | anim | OK | Figure Four Leg Lock |
| `b+2,1` | yes | t7:b+2~t7.king | t7 | OK | real T7 Kg_rp00B (kgkb_s3_rap) |
| `b+2,1+2` | yes | t7:b+2~t7.king | t7 | OK | real T7 Kg_rp00B (kgkb_s3_rap) |
| `b+2,4` | yes | t7:b+2~t7.king | t7 | OK | real T7 Kg_rp00B (kgkb_s3_rap) |
| `b+3` | yes | t7:b+3~t7.king | t7 | OK | real T7 Kg_turas (Bak_turasK_DVD) |
| `b+3+4` | yes | row:103 | notation | OK | same input 'b+3+4' |
| `b+4` | yes | row:115 | own | OK | Disgraceful Kick |
| `b,n,f+1+2` | yes | row:281 | own | OK | PANTERA b,n,f+1+2 throw (T3 king r281) |
| `b,n,f+1+2,1` | yes | row:110 | donor | OK | donor row 110 |
| `d+1` | yes | row:136 | own | OK | Move d+1 (d+1) |
| `d+1+2` | yes | t7:d+1+2~t7.king | t7 | OK | real T7 Kg_WHummer (kgyt_mox01_iwaki_s_DVD) |
| `d+1+2,2` | yes | t7:d+1+2~t7.king | t7 | OK | real T7 Kg_WHummer (kgyt_mox01_iwaki_s_DVD) |
| `d+1+2,2,1` | yes | t7:d+1+2~t7.king | t7 | OK | real T7 Kg_WHummer (kgyt_mox01_iwaki_s_DVD) |
| `d+1+2,2,1,1` | yes | t7:d+1+2~t7.king | t7 | OK | real T7 Kg_WHummer (kgyt_mox01_iwaki_s_DVD) |
| `d+1+2,2,1,1,2` | yes | t7:d+1+2~t7.king | t7 | OK | real T7 Kg_WHummer (kgyt_mox01_iwaki_s_DVD) |
| `d+1+2,2,1,1,2,4` | yes | t7:d+1+2~t7.king | t7 | OK | real T7 Kg_WHummer (kgyt_mox01_iwaki_s_DVD) |
| `d+1+2,2,1,1,3` | yes | t7:d+1+2~t7.king | t7 | OK | real T7 Kg_WHummer (kgyt_mox01_iwaki_s_DVD) |
| `d+1+2,2,1,1,3,3` | yes | t7:d+1+2~t7.king | t7 | OK | real T7 Kg_WHummer (kgyt_mox01_iwaki_s_DVD) |
| `d+1+3` | yes | row:275 | donor | OK | donor row 275 |
| `d+1+3,1` | yes | row:478 | step-plan | OK | step-plan last step (d+1+3,1) |
| `d+1+4` | yes | row:289 | match | OK | throw btn 9 null t hit@12f |
| `d+1,2` | yes |  | step-plan | TPOSE | Move d+1 (d+1) — chained replay: NOFIRE |
| `d+2` | yes | row:142 | anim | OK | Move d+2 (d+2) |
| `d+2+3` | yes | t7:d+2+3~t7.king | t7 | OK | real T7 Kg_Akelbow (Gkg_elbowR_DVD) |
| `d+2+4` | yes | row:128 | donor | OK | donor row 128 |
| `d+3` | yes | t7:d+3~t7.king | t7 | OK | real T7 Kg_t_slk (naak_sune_DVD) |
| `d+3+4` | yes | t7:d+3+4~t7.king | t7 | OK | real T7 Kg_Ari_kick (sukg_ari1_DVD) |
| `d+3+4,2` | yes | row:196 | step-plan | OK | step-plan last step (d+3+4,2) |
| `d+3+4,2,1` | yes | row:201 | step-plan | OK | step-plan last step (d+3+4,2,1) |
| `d+3+4,4` | yes | t7:d+3+4~t7.king | t7 | OK | real T7 Kg_Ari_kick (sukg_ari1_DVD) |
| `d+3+4,4,1` | yes | row:210 | step-plan | OK | step-plan last step (d+3+4,4,1) |
| `d+3+4,4,1,4` | yes | row:212 | step-plan | OK | step-plan last step (d+3+4,4,1,4) |
| `d+3+4,4,1,4,4` | yes | row:214 | step-plan | OK | step-plan last step (d+3+4,4,1,4,4) |
| `d+3+4,4,1,4,4,1` | yes | row:215 | step-plan | OK | step-plan last step (d+3+4,4,1,4,4,1) |
| `d+3+4,4,4` | yes | t7:d+3+4~t7.king | t7 | OK | real T7 Kg_Ari_kick (sukg_ari1_DVD) |
| `d+3+4,4,4,2` | yes | t7:d+3+4~t7.king | t7 | OK | real T7 Kg_Ari_kick (sukg_ari1_DVD) |
| `d+3+4,4,4,4` | yes | t7:d+3+4~t7.king | t7 | OK | real T7 Kg_Ari_kick (sukg_ari1_DVD) |
| `d+4` | yes | row:69 | anim | OK | Move d+4 (d+4) |
| `d,d/b,d,d/b+1+2` | yes | row:287 | own | OK | PANTERA d,d/b,d,d/b+1+2 throw (T3 king r287) |
| `d,d/b,d,d/b+1+2,1` | yes | row:445 | own | OK | KING d,d/b,d,d/b+1+2,1_c2 (T3 king r445) |
| `d,d/f,d,d/f+1+2` | yes | row:284 | own | OK | PANTERA d,d/f,d,d/f+1+2 throw (T3 king r284) |
| `d,d/f,d,d/f+1+2,1` | yes | row:439 | own | OK | KING d,d/f,d,d/f+1+2,1_c2 (T3 king r439) |
| `d/b` | yes | row:119 | own | OK | KING d/b_c37 (T3 king r119) |
| `d/b+1` | yes | row:488 | own | OK | PANTERA d/b+1_c10 (T3 king r488) |
| `d/b+1+2` | yes | row:131 | notation | OK | same input 'd/b+1+2' |
| `d/b+1+2,2` | yes | row:281 | anim | OK | Emerald Elbow |
| `d/b+1+2,3+4` | yes |  | step-plan | TPOSE | Jaguar Sprint — chained replay: NOFIRE |
| `d/b+1+3` | yes | row:277 | own | OK | PANTERA d/b+1+3 throw (T3 king r277) |
| `d/b+1+3,1` | yes | row:482 | step-plan | OK | step-plan last step (d/b+1+3,1) |
| `d/b+2` | yes | t7:d/b+2 | t7 | OK | real T7 Kg_t_srp00B (kokg_thop_DVD) |
| `d/b+2+3` | yes | row:195 | anim | OK | Figure Four Leg Lock |
| `d/b+2+4` | yes | row:278 | own | OK | PANTERA d/b+2+4 throw (T3 king r278) |
| `d/b+2+4,1` | yes | row:486 | step-plan | OK | step-plan last step (d/b+2+4,1) |
| `d/b+2+4,d/b+1` | yes | row:488 | step-plan | OK | step-plan last step (d/b+2+4,d/b+1) |
| `d/b+3` | yes | t7:d/b+3 | t7 | OK | real T7 Kg_gyakuAri (sukg_sitllw_DVD) |
| `d/b+3+4` | yes | row:133 | own | OK | KING d/b+3+4 (T3 king r133) |
| `d/b+4` | yes | t7:d/b+4 | t7 | OK | real T7 Kg_loDropN (kgss_lowdpmiss_DVD) |
| `d/b,f+2+4` | yes | row:128 | donor | OK | donor row 128 |
| `d/b,n,f+2` | yes | row:283 | own | OK | KING d/b,n,f+2_r4 (T3 king r283) |
| `d/b,n,f+2+4` | yes | row:127 | anim | OK | Tombstone Pile Driver |
| `d/b,n,f+2,1` | yes | row:443 | own | OK | KING d/b,n,f+2,1_c2 (T3 king r443) |
| `d/f+1` | yes | t7:d/f+1~t7.king | t7 | OK | real T7 Kg_t_slpF (kgkb_s3_3lp) |
| `d/f+1+2` | yes | row:116 | own | OK | KING d/f+1+2 (T3 king r116) |
| `d/f+1+3` | yes | row:127 | anim | OK | Reverse Arm Slam (RAS1) |
| `d/f+1+4` | yes | row:242 | own | OK | PANTERA d/f+1+4 (T3 king r242) |
| `d/f+1,2` | yes | t7:d/f+1~t7.king | t7 | OK | real T7 Kg_t_slpF (kgkb_s3_3lp) |
| `d/f+2` | yes | t7:d/f+2~t7.king | t7 | OK | real T7 Kg_t_srpF (sukg_dhook_DVD) |
| `d/f+2+3` | yes | row:285 | notation | OK | same input 'd/f+2+3' |
| `d/f+2+3,1` | yes | row:457 | step-plan | OK | step-plan last step (d/f+2+3,1) |
| `d/f+2+4` | yes | row:127 | anim | OK | Reverse Special Stretch Bomb (RSSB1) |
| `d/f+2,1` | yes | t7:d/f+2~t7.king | t7 | OK | real T7 Kg_t_srpF (sukg_dhook_DVD) |
| `d/f+3` | yes | t7:d/f+3 | t7 | OK | real T7 Kg_t_slkF (Bco_fslk00_DVD) |
| `d/f+3+4` | yes | row:127 | anim | OK | Frankensteiner |
| `d/f+3+4,1` | yes | row:247 | step-plan | OK | step-plan last step (d/f+3+4,1) |
| `d/f+3,4` | yes | t7:d/f+3 | t7 | OK | real T7 Kg_t_slkF (Bco_fslk00_DVD) |
| `d/f+4` | yes | t7:d/f+4~t7.king | t7 | OK | real T7 Kg_t_srkF (mokg_flwrk_DVD) |
| `d/f+4,2` | yes | t7:d/f+4~t7.king | t7 | OK | real T7 Kg_t_srkF (mokg_flwrk_DVD) |
| `d/f+4,3` | yes | t7:d/f+4~t7.king | t7 | OK | real T7 Kg_t_srkF (mokg_flwrk_DVD) |
| `d/f+4,3,4` | yes | t7:d/f+4~t7.king | t7 | OK | real T7 Kg_t_srkF (mokg_flwrk_DVD) |
| `d/f+4,3,d+4` | yes | t7:d/f+4~t7.king | t7 | OK | real T7 Kg_t_srkF (mokg_flwrk_DVD) |
| `d/f+4,4` | yes | t7:d/f+4~t7.king | t7 | OK | real T7 Kg_t_srkF (mokg_flwrk_DVD) |
| `f` | yes | row:36 | own | OK | PANTERA f (T3 king r36) |
| `f+1` | yes | row:110 | notation | OK | same input 'f+1' |
| `f+1+2` | yes | row:112 | notation | OK | same input 'f+1+2' |
| `f+1+2*` | yes | row:0 | anim | OK | Jaguar Lariat |
| `f+1+3` | yes | row:127 | donor | OK | donor row 127 |
| `f+1+4` | yes | t7:f+1+4~t7.king | t7 | OK | real T7 Kg_near_kata00 (sukg_neartc_DVD) |
| `f+2` | yes | t7:f+2~t7.king | t7 | OK | real T7 Kg_rp00F (kgke_ren1_ak6rp_DVD) |
| `f+2+3` | yes | t7:f+2+3~t7.king | t7 | OK | real T7 Kg_Mpl_kata (kgyt_katacl_DVD) |
| `f+2+4` | yes | row:128 | donor | OK | donor row 128 |
| `f+2,1` | yes | t7:f+2~t7.king | t7 | OK | real T7 Kg_rp00F (kgke_ren1_ak6rp_DVD) |
| `f+2,1,1` | yes | row:257 | step-plan | OK | step-plan last step (f+2,1,1) |
| `f+2,1,1,2` | yes | row:258 | step-plan | OK | step-plan last step (f+2,1,1,2) |
| `f+2,1,1,2,4` | yes | row:259 | step-plan | OK | step-plan last step (f+2,1,1,2,4) |
| `f+2,1,1,2,4,4` | yes | row:260 | step-plan | OK | step-plan last step (f+2,1,1,2,4,4) |
| `f+2,1,1,2,4,4,4` | yes | row:261 | step-plan | OK | step-plan last step (f+2,1,1,2,4,4,4) |
| `f+2,1,1,2,4,4,4,1` | yes | row:262 | step-plan | OK | step-plan last step (f+2,1,1,2,4,4,4,1) |
| `f+2,1,1,2,4,4,4,1,1` | yes | row:272 | step-plan | OK | step-plan last step (f+2,1,1,2,4,4,4,1,1) |
| `f+2,1,1,2,4,4,4,1,3` | yes | row:263 | step-plan | OK | step-plan last step (f+2,1,1,2,4,4,4,1,3) |
| `f+2,1,1,3` | yes | row:264 | step-plan | OK | step-plan last step (f+2,1,1,3) |
| `f+2,1,1,3,3` | yes | row:265 | step-plan | OK | step-plan last step (f+2,1,1,3,3) |
| `f+2,1,1,3,3,4` | yes | row:266 | step-plan | OK | step-plan last step (f+2,1,1,3,3,4) |
| `f+2,1,1,3,3,4,3` | yes | row:267 | step-plan | OK | step-plan last step (f+2,1,1,3,3,4,3) |
| `f+2,1,1,3,3,4,3,2` | yes | row:268 | step-plan | OK | step-plan last step (f+2,1,1,3,3,4,3,2) |
| `f+2,1,1,3,3,4,3,2,1+2` | yes | row:269 | step-plan | OK | step-plan last step (f+2,1,1,3,3,4,3,2,1+2) |
| `f+2,1,1,3,3,4,3,2,1+2,1` | yes | row:271 | step-plan | OK | step-plan last step (f+2,1,1,3,3,4,3,2,1+2,1) |
| `f+2,d+1` | yes | t7:f+2~t7.king | t7 | OK | real T7 Kg_rp00F (kgke_ren1_ak6rp_DVD) |
| `f+2,d+1,2` | yes | t7:f+2~t7.king | t7 | OK | real T7 Kg_rp00F (kgke_ren1_ak6rp_DVD) |
| `f+3` | yes | t7:f+3~t7.king | t7 | OK | real T7 Kg_lk00F (nokg_ptk_DVD) |
| `f+3+4` | yes | row:109 | anim | OK | Jaguar Sprint |
| `f+3,1+2` | yes | row:127 | anim | OK | DDT |
| `f+4` | yes | t7:f+4~t7.king | t7 | OK | real T7 Kg_rsbt (kokg_sobatter_DVD) |
| `f,F+1` | yes | row:35 | anim | OK | Jaguar Hook |
| `f,F+1+2` | yes | row:220 | match | OK | btn 3 null h hit@20f |
| `f,F+2` | yes | row:203 | anim | OK | Beast Elbow |
| `f,F+2+3` | yes | row:237 | match | OK | btn 6 null m hit@25f |
| `f,F+2,1` | yes | row:110 | donor | OK | donor row 110 |
| `f,F+3+4` | yes | row:35 | anim | OK | Exploder |
| `f,F+4` | yes | row:216 | anim | OK | Konvict Kick |
| `f,f,F` | yes | row:99 | donor | OK | donor row 99 |
| `f,f,F+2+4` | yes | row:128 | donor | OK | donor row 128 |
| `f,f,F+3` | yes | row:54 | anim | OK | Strong Knee |
| `f,f,F+3+4` | yes | row:35 | anim | OK | Running Exploder |
| `f,f,f+2+4` | yes | row:128 | donor | OK | donor row 128 |
| `f,f,f+3` | yes | row:113 | donor | OK | donor row 113 |
| `f,f,f+3+4` | yes | row:109 | donor | OK | donor row 109 |
| `f,f,n,1+2` | yes | row:195 | anim | OK | Lay Off |
| `f,f,n,2` | yes | row:50 | anim | OK | Stomach Smash / Jaguar Hammer |
| `f,hcf+1` | yes | row:280 | anim | OK | Giant Swing |
| `f,hcf+2` | yes | row:586 | anim | OK | Tijuana Twister |
| `f,n,b,d/b,d,f+1` | yes | row:280 | own | OK | PANTERA f,n,b,d/b,d,f+1 throw (T3 king r280) |
| `f,n,b,d/b,d,f+1,1` | yes | row:421 | own | OK | KING f,n,b,d/b,d,f+1,1_c5 (T3 king r421) |
| `f,n,d,D/F` | yes | row:99 | donor | OK | donor row 99 |
| `f,n,d,D/F+1` | yes | row:117 | donor | OK | donor row 117 |
| `f,n,d,D/F+1+2` | yes | row:227 | match | OK | btn 3 null m hit@15f |
| `f,n,d,D/F+1+4` | yes | row:289 | match | OK | throw btn 9 null t hit@12f |
| `f,n,d,D/F+2+3` | yes | row:285 | donor | OK | donor row 285 |
| `f,n,d,D/F+4` | yes | row:135 | donor | OK | donor row 135 |
| `f,n,d,d/f` | yes | row:195 | anim | OK | Beast Step |
| `n,d,d/b+1+3` | yes | row:282 | own | OK | PANTERA n,d,d/b+1+3 throw (T3 king r282) |
| `n,d,d/f,f+1` | yes | row:282 | own | OK | KING n,d,d/f,f+1_r4 (T3 king r282) |
| `n,d,d/f,f+1,1` | yes | row:431 | own | OK | KING n,d,d/f,f+1,1_c2 (T3 king r431) |
| `n,d,d/f,f+1,1,1+2` | yes | row:433 | own | OK | KING n,d,d/f,f+1,1,1+2_c2 (T3 king r433) |
| `n,d/f,n,d/f+2+4` | yes | row:276 | own | OK | PANTERA n,d/f,n,d/f+2+4 throw (T3 king r276) |
| `n,d/f,n,d/f+2+4,1` | yes | row:586 | own | OK | KING n,d/f,n,d/f+2+4,1_c6 (T3 king r586) |
| `qcb+1+2` | yes | row:127 | anim | OK | Muscle Buster |
| `qcb+1+3` | yes | row:127 | anim | OK | Elevating Spine Cracker |
| `qcf+1` | yes | row:280 | anim | OK | Pile Driver (PD) |
| `u+1+2` | yes | row:35 | notation | OK | same input 'u+1+2' |
| `u+1+2*` | yes | row:35 | anim | OK | Burning Knuckle |
| `u+1,1` | yes | row:38 | step-plan | OK | step-plan last step (u+1,1) |
| `u+1,2` | yes | row:50 | step-plan | OK | step-plan last step (u+1,2) |
| `u+1,2+4` | yes | row:243 | step-plan | OK | step-plan last step (u+1,2+4) |
| `u+1,3` | yes | row:54 | step-plan | OK | step-plan last step (u+1,3) |
| `u+1,4` | yes | row:72 | step-plan | OK | step-plan last step (u+1,4) |
| `u+3+4` | yes | row:66 | own | OK | KING u+3+4_r107 (T3 king r66) |
| `u+4` | yes | row:69 | own | OK | KING u+4 (T3 king r69) |
| `u/b+1` | yes | t7:u/b+1~t7.king | t7 | OK | real T7 Kg_Aklp01m (sukg_chop_DVD) |
| `u/b+1+2` | yes | row:37 | own | OK | KING u/b+1+2 (T3 king r37) |
| `u/b+1,1` | yes | row:40 | step-plan | OK | step-plan last step (u/b+1,1) |
| `u/b+1,2` | yes | row:52 | step-plan | OK | step-plan last step (u/b+1,2) |
| `u/b+1,2+4` | yes | row:246 | step-plan | OK | step-plan last step (u/b+1,2+4) |
| `u/b+1,3` | yes | row:56 | step-plan | OK | step-plan last step (u/b+1,3) |
| `u/b+1,4` | yes | row:74 | step-plan | OK | step-plan last step (u/b+1,4) |
| `u/b+2+4` | yes | row:246 | own | OK | PANTERA u/b+2+4 (T3 king r246) |
| `u/b+3` | yes | row:56 | own | OK | PANTERA u/b+3 (T3 king r56) |
| `u/b+3+4` | yes | row:68 | own | OK | PANTERA u/b+3+4 (T3 king r68) |
| `u/b+4` | yes | row:83 | notation | OK | same input 'u/b+4' |
| `u/f+1` | yes | row:36 | notation | OK | same input 'u/f+1' |
| `u/f+1+2` | yes | row:127 | anim | OK | Executioner Drop |
| `u/f+1+2*` | yes | row:222 | own | OK | Burning Knuckle |
| `u/f+1,1` | yes | row:39 | step-plan | OK | step-plan last step (u/f+1,1) |
| `u/f+1,2` | yes | row:51 | step-plan | OK | step-plan last step (u/f+1,2) |
| `u/f+1,3` | yes | row:55 | step-plan | OK | step-plan last step (u/f+1,3) |
| `u/f+1,4` | yes | row:73 | step-plan | OK | step-plan last step (u/f+1,4) |
| `u/f+2` | yes | t7:u/f+2~t7.king | t7 | OK | real T7 Kg_jprp00F (Bkg_jpre00_DVD) |
| `u/f+3` | yes | t7:u/f+3~t7.king | t7 | OK | real T7 Kg_jplk00F (mokg_fnkick_DVD) |
| `u/f+3+4` | yes | row:67 | notation | OK | same input 'u/f+3+4' |
| `u/f+4` | yes | t7:u/f+4~t7.king | t7 | OK | real T7 Kg_jprk00F (mokg_jmprhiza01_DVD) |
| `u/f,n,4` | yes | row:69 | anim | OK | Delayed Rising Toe Kick |
| `3+4,1` | yes | row:195 | anim | OK | Hook |
| `3+4,2` | yes | row:99 | donor | OK | donor row 99 |
| `3+4,3` | yes | row:195 | anim | OK | Sobat |
| `3+4,4` | yes | row:195 | anim | OK | High Kick |
| `3+4,d/f+4` | yes | row:195 | anim | OK | Mid Kick |
| `3+4,3,2+3` | yes |  | step-plan | TPOSE | Sobat — chained replay: NOFIRE |
| `df+4,3,d/b+4` | yes | t7:d/f+4~t7.king | t7 | OK | real T7 Kg_t_srkF (mokg_flwrk_DVD) |
| `d/f+4,3,d/b+4` | yes | t7:d/f+4~t7.king | t7 | OK | real T7 Kg_t_srkF (mokg_flwrk_DVD) |
| `WS+2,2` | yes |  | step-plan | TPOSE | Move ws2 (ws2) — chained replay: TPOSE |

