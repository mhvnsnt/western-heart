# Anim-motion audit 2026-10-24 — Pantera + 8 MOD-damage fighters

**Scope:** does each move play a clip whose ACTUAL motion matches the move
(limb, hit level, stance, direction, travel)? NOT hit detection (PR #1005),
NOT strings/grace (PR #1007), NOT root motion (PR #1008). Animation-to-move
correctness only.

**Button names:** LP1 = Left Punch = Tekken 1, RP2 = Right Punch = Tekken 2,
LK3 = Left Kick = Tekken 3, RK4 = Right Kick = Tekken 4. Used everywhere below.

**Proof:** simulation/scan only. The audit replicates `game/js/fighter.js`
`_attackClipPlan` (own > notation > anim > donor > match > generic) over the
decoded T3 banks and checks the played clip with forward kinematics — NOT
JSON labels, NOT play-verified. Live-browser phone play verification is still
open (this lane cannot drive the live browser).

**Tool (reproduces every number below):**
`tools/combat-qa/anim_motion_audit.py` — run from the repo root:
`python3 tools/combat-qa/anim_motion_audit.py --out results.json`.
It matches the pre-fix and post-fix runs exactly (verified 2026-10-24).

## Method (what "wrong" means here)

- **What plays:** the runtime does NOT simply play `anim_ref`. Clip selection
  (first match wins, within the fighter's OWN bank): (1) `own` — the move's
  decoded T3 row; (2) `notation` — the T3 row of the move bound to the SAME
  input (this is how a T8 press gets its clip: the T3 basic's row);
  (3) `anim` — `anim_t3 {bank,row}` same-notation; (4) `donor` — the closest
  animated move in the SAME moveset (same command, else direction+button,
  else button/limb), first in JSON order per key; (5) `match` — the bank's
  decoded attack pool by buttons, then limb, then level tiers, nearest
  startup; (6) `generic` — the bank's light/medium/heavy (grab for throws)
  action clips. A type guard (`fits()`) rejects strike-on-throw-row and
  throw-on-strike-row and falls through; those rejections are DATA, not HARD.
- **Stance:** from `root_t` Y trajectory, RELATIVE to each bank's own
  neutral-clip median (never absolute — Yoshimitsu's `root_t` scale does not
  match its skeleton). `starts-airborne` (y0 > neutral + 0.25), `jump` (peak >
  neutral + 0.30 with return), `ground` (falls to floor), `crouch`, `duck-dip`,
  else `standing`. Active-frame body height is checked against the stance the
  move's input implies (standing / d+/FC crouch / WS / u/f jump).
- **Limb:** the decoded branch-command button when that limb participates
  (arm ext >= 0.2); if the button limb barely moves while another limb
  extends >= 0.5, the dominant limb is what the eye sees (jin row 97, btn LP1,
  armR ext 0.83 / armL ext 0.10, is a RIGHT-arm motion, not a left jab).
  **For legs the FOOT decides:** extension is nearly useless for kicks (a
  straight leg rotating up keeps hip distance ~constant). A leg-branch row
  with foot lift >= 0.3 m is that leg's kick even when arm swing dominates
  extension; a leg move whose clip never lifts that foot (< 0.15 m) is
  `no-kick-motion` HARD (king row 108 back-3 family: foot never leaves the
  ground, not a kick). Chord/unknown rows: dominant limb, except a chord row
  with no extension-dominant limb and exactly one leg lifting >= 0.5 m is
  that leg's kick (king row 113 f+3: btn 12 chord branch, but a legL kick by
  foot 1.35 m at active).
- **Level:** decoded attack word vs the move's T7/T8 level. h<->l is HARD,
  m<->l is MED, h<->m is note only (word and foot height can disagree — see
  king row 216 below). `s` matches m/l, `u` matches anything.
- **String-vs-chord:** a string ender on a chord row is HARD only when the
  MOTION is multi-limb or the wrong limb. A chord BRANCH mask alone is INFO
  (king row 113 f+3 again). Throws are exempt — chord branches are legitimate
  for throws (1+3/2+4). The literal branch-mask scan is reported separately
  below (66 string enders on chord-branch rows), because the task's rule is
  stated at branch level; the motion verdict is what decides a rewire.
- **Jab identity:** keys `1`, `2` and `^[12]~t8\.` — duck-dip or travel >
  0.5 m is HARD. A jumping punch is NOT a jab even if both are "strikes".
- **Keys split:** PRESSABLE (clean Tekken notations) vs VARIANT (keys with
  `__` or `_[rc]<digit>`, or bare directions `b/f/u/d` — T3-table dump keys,
  not pressable inputs). Headline counts are pressable only. `parry` moves
  excluded. WH signatures have no T7 truth; limb/level checked against
  declared fields only, flagged INFO.
- **Bank binding:** pantera→`king` (`king_on_pantera_leoman/`), burger→`bryan`,
  demonio→`jin`, diablo→`heihachi` (`heihachi_on_jin/`), kinpo→`jin` (proxy —
  Asuka has no T3 bank), phantom→`yoshimitsu`, scimitar→`jin` (proxy),
  skull→`bryan`. Burger uses the Bryan bank like all its T3 rows (Bob has no
  T3 bank) — disclosed wherever it matters.
- **Caveats carried, not hidden:**
  - Yoshimitsu turn: banks are labeled by the game's knee-forward turn logic
    (yoshimitsu = turned, all others = not). If the Yoshimitsu turn is wrong,
    ALL Yoshimitsu L/R limb labels flip — a bank-level rig-lane question, not
    a per-move fix. Audit labels follow the game's turn logic, so they match
    what the game shows under the current engine.
  - T3 King JSON is NOT T7 truth. T3 tables are used only for what a T3 row
    IS in T3's own tree. T7 truth is wavu.wiki per-character pages + the
    in-repo `docs/t7t8-reference/frame-data-t7/` mirror.
  - Rows 50/51/52 share identical motion in king and bryan banks: T3 shares
    one slot motion across multiple move rows — expected, not a decode error.
  - Slot families (shared T3 move-index table across banks): slots ~295–354
    = directional basics; 3335–3359 = jumping-1 family; 3366–3386 =
    jumping-kick family. Slot 318 motion = a back-step RIGHT-arm punch in
    every bank — NOT a left jab anywhere, despite btn 1.
  - Donor fallback is approximate by design: a donor clip is limb/level/
    stance-correct at best, never the exact move (a hook is not a jab even
    when both are standing armL high). Donor improvements below are reported
    as "standing limb-correct clip", not exact-identity fixes.

## Summary (pressable moves; foot-aware audit code, same code both sides)

| Fighter (Tekken base) | Checked | HARD before | HARD after | Δ | Variant HARD (unchanged) |
|---|---|---|---|---|---|
| pantera (King) | 762 | 308 | 236 | −72 | 98 |
| burger (Bob → Bryan bank) | 471 | 281 | 151 | −130 | 60 |
| demonio (Jin) | 665 | 174 | 174 | 0 | 79 |
| diablo (Heihachi) | 559 | 210 | 156 | −54 | 76 |
| kinpo (Asuka → Jin bank) | 429 | 108 | 108 | 0 | 79 |
| phantom (Yoshimitsu) | 937 | 623 | 553 | −70 | 73 |
| scimitar (Shaheen → Jin bank) | 268 | 54 | 54 | 0 | 78 |
| skull (Bryan) | 605 | 261 | 122 | −139 | 59 |
| **Total** | **4696** | **2019** | **1554** | **−465** | **602** |

Changes in this PR: **11 basic rewires + 22 jumping-move restoration
bindings = 33 moveset changes** (77 insertions / 33 deletions across 5 files:
33 rewire lines + 44 binding lines; nothing else touched — no damage,
startup, t7/t8 fields, slots, or legacy `strings` arrays).
MED counts rose in 5 fighters (e.g. burger 54→94, skull 82→99): moves that
were HARD (airborne) now play standing rows whose level grades MED — a
HARD→MED migration, not a regression. Variant keys were not touched, so
variant HARD is unchanged by construction.

## Basics: what pressing the buttons plays

T8-resolved basics resolve via NOTATION to the T3 basic's row, so fixing the
T3 basic fixes the T8 press (except where slots point elsewhere — see Slots
below). LP1/RP2/LK3/RK4 = Tekken 1/2/3/4.

### Pantera (King) — all four basics fixed, all CLEAN

| Button | Before (row, what it was) | After | Evidence for the new row |
|---|---|---|---|
| LP1 `1` | 44, starts-airborne (feet 0.75/0.78 m off ground at frame 0; jumping-1 family slots 3337–3343; also the old row 38's family) | **110** | T3 `f+1` (pantera `f+1~t3.king`), btn 1, h, standing, armL ext 0.51, active 10 = T7 startup 10 exactly, travel 0.30. Residual: small forward step vs a stationary jab (disclosed directional-variant substitution — every neutral king LP1 row is contaminated: slot-318 back-step right-arm punch, `2,1` ender uppercut travel 0.67, long string enders). |
| RP2 `2` | 203, duck-dip (hips to 0.61 vs neutral 0.89) + 0.95 m travel — a lunging ducking straight, not a jab | **99** | T3 `b+2` (slot 296; row 111 `f+2` slot 303 is the identical motion — 99 picked, shared motion noted), btn 2, h, standing, armR 0.86, active 10 = startup 10, travel 0.32. |
| LK3 `3` | 54, jump clip (arcs +0.41 above neutral, body 1.25 at hit) | **264** | T7 Face Kick is high, heavy. Row 264: btn 4, h, standing, legL foot +0.34 above hips at active, travel 0.45, active 26, 70-frame clip. Provenance disclosed: T3 string-ender kick (used by `d+1+2,2,1,1,3` and `f+2,1,1,3` enders). Row 108 (slot 325 back-3 family) rejected: foot never leaves the ground. Row 122 (T7-wired `3~t3.king`) rejected: crouch stance, word low, leg ext 0.00. |
| RK4 `4` | 216, standing, legR — already correct | **KEPT 216** | T7 King 4 = High Kick / Magic 4, h, 20, i13, CH knockdown (wavu T7 page). Foot +0.31 above hips AT active (chest height) — a real high kick despite the decoded word saying mid (word-vs-shape conflict, see below). |

T7 King basics (wavu T7 page, verified 2026-10-24): 1 Jab h 7 i10; 2 Right
Jab h 10 i10; 3 Face Kick h 25 i17, −14; 4 High Kick h 20 i13. Moveset MOD
damages differ (e.g. pantera `3` damage 33) — damage is the MOD lane, untouched.

### Burger (Bob, Bryan bank) — LP1/RP2/RK4 fixed with stepping residuals; LK3 UNMAPPED

| Button | Before | After | Note |
|---|---|---|---|
| LP1 `1` | 52, starts-airborne | **172** | T3 `f+1` (skull `f+1`, same bryan bank), btn 1, h, standing, armL 0.62, active 10 = T7 startup 10, travel 0.53. Residual: `jab-travels` HARD remains (0.53 > 0.50 threshold) — a stepping jab, not a stationary one. Motion now correct (standing jab, not airborne); travel residual disclosed. |
| RP2 `2` | 152, jab-travels (0.99 m) | **100** | T3 `b+2` (skull `b+2~t3.bryan`, slot 296), btn 2, h, standing, armR 1.15, active 10, travel 0.52. Residual: `jab-travels` HARD remains (0.52) — same stepping-jab caveat. Current 152 travels 0.99 m, active 17, slot 2063. |
| LK3 `3` | 65, jump clip | **UNMAPPED** | No clean row: current 65 is a jump clip; only h candidate bryan row 106 has a foot that never leaves the ground — not a kick. Row unchanged, still plays a jumping clip. |
| RK4 `4` | 78, starts-airborne (slot 3386, jumping-4 family) | **104** | The moveset's own T7-wired Bryan 4 (`skull:4~t3.bryan`, T7 bryan_71, high, 20, startup 12): btn 8, h, standing, foot +0.37 above hips AT active, active 12 = startup 12 exactly, travel 0.67, slot 301. CLEAN. |

### Skull (Bryan) — mirrors burger; LK3 UNMAPPED

| Button | Before | After | Note |
|---|---|---|---|
| LP1 `1` | 50, starts-airborne | **172** | Same bryan-bank reasoning as burger. Residual `jab-travels` (0.53). |
| RP2 `2` | 152, jab-travels (0.99 m) | **100** | Same as burger. Residual `jab-travels` (0.52). |
| LK3 `3` | 63, jump clip | **UNMAPPED** | Current 63 is a jump clip; m candidates are bryan row 135 (back-variant, travels 1.29 m) and row 188 (`f+1,4,3` string ender, high foot +0.12 for a mid kick). Neither verified. Row unchanged. |
| RK4 `4` | 76, starts-airborne (slot 3384) | **104** | Same row as burger's fix (skull's own `4~t3.bryan`). CLEAN. |

### Diablo (Heihachi) — RK4 fixed; LP1 UNMAPPED; RP2/LK3 kept

| Button | Before | After | Note |
|---|---|---|---|
| LP1 `1` | 46, starts-airborne | **UNMAPPED** | No clean heihachi LP1 row exists (see UNMAPPED section). Row unchanged. |
| RP2 `2` | 157, standing h, armR 1.03 | **KEPT 157** | Clean. |
| LK3 `3` | 153, standing, foot +0.89 above hips AT active (baked frame 9) | **KEPT 153** | Genuine head-height kick; decoded word `m` is the outlier (T7 Heihachi 3 is high). Word-vs-shape conflict, see below. Jin 195 / heihachi 153 are the same slot-562 motion. |
| RK4 `4` | 74, starts-airborne (slot 3384) | **104** | T3 `f+4` (diablo `f+4~t3.heihachi`), btn 8, h, standing, foot +0.25 at active, travel 0.68, active 16. T8 Otoko Geri is high + launch, so level h wins over row 136 (word m, foot −0.15 at active despite +0.48 peak just after active; row 136 = back-variant `b_r136`). CLEAN. Also improves the `4~3` Demon Scissors donee chain (donor row 74 → 104), noted as approximate for that move. |

### Phantom (Yoshimitsu) — LK3 fixed; LP1/RP2/RK4 UNMAPPED

| Button | Before | After | Note |
|---|---|---|---|
| LP1 `1` | 62, starts-airborne | **UNMAPPED** | No clean yoshi row (row 224 is a `d/f+1,1` string punch, travel 0.81, active 18; rows 213–217 are `b+1,1` family with arm ext only 0.13; row 131 is a 1.54 m back-lunge). Row unchanged. |
| RP2 `2` | 307, crouch-clip + travels | **UNMAPPED** | No clean yoshi row (row 116 `b+2` is left-arm-dominant 1.03 vs armR 0.00 under turned labels; rows 119/125 are left-dominant; row 302 is a string ender, travel 1.00, active 22–23). Row unchanged. |
| LK3 `3` | 73, jump clip (slot 3366) | **123** | Btn 4, h, standing, travel 0.33, active 10, foot lift +1.09 m (scale-free Yoshimitsu metric — a real high kick). Provenance disclosed: `b~t3.yoshimitsu.3` (back-3 variant). Row 173 rejected (lift +0.10, not a kick). CLEAN. |
| RK4 `4` | 243, chord row btn 9, armL, word u — badly wrong for a legR high kick | **UNMAPPED** | No verified high RK row in the yoshi bank — all btn8 h standing rows lift the foot ≤ 0.14 m (rows 121/130/141/243 are not kicks by lift), while T7 Yoshi 4 (Magic 4) is high, 22, i15, KND. Row unchanged, still plays the chord arm motion. |

### Demonio (Jin), Kinpo (Asuka → Jin bank), Scimitar (Shaheen → Jin bank) — no basic rewires

| Fighter | LP1 | RP2 | LK3 | RK4 |
|---|---|---|---|---|
| demonio | 41, starts-airborne — **UNMAPPED** | 220, standing h armR 1.00 travel 0.45 — **KEPT** | 195, foot head-height at active — **KEPT** (word m vs T7 high, see below) | 199, mid-height roundhouse at active (foot −0.15 below hips, travel 0.68, standing, legR) — **KEPT, soft level mismatch** (T7 high; only high alternative jin row 100 travels 1.28 m — a lunge, a bigger visual error) |
| kinpo | 35, starts-airborne (body 2.00 m vs neutral 1.03 at hit) — **UNMAPPED** | 220 — **KEPT** | 195 — **KEPT, height concern** (T7 Asuka 3 is MID asuka_31, while jin 195's foot reaches head height at active; no mid-height LK row exists in the jin bank — row 102's foot never leaves the ground — so this is a proxy-bank limitation, not a fixable rewire; gameplay-wise the decoded word is mid, so blocking is mid, but the visual is high) | 199 — **KEPT, soft level mismatch** (same as demonio) |
| scimitar | 184, chord btn 9 (LP1+RK4), armR, level s, travel 1.63 m — **UNMAPPED** (single-on-chord-row + limb-mismatch + jab-travels HARD) | 220 — **KEPT** | 195 — **KEPT** (T7 Shaheen 3 = high; shape high ✓, word m ✗) | 199 — **KEPT, soft level mismatch** (T7 Shaheen Hallux Kick = high) |

**UNMAPPED basics (no verified replacement row in-bank; row unchanged, reason
documented — not available from VM+browser sources checked; removing the row would fall to donor/match, possibly worse):**
demonio LP1, kinpo LP1, scimitar LP1, diablo LP1 (no clean jin/heihachi LP1
row: slot-318 back-step right-arm punch (armR 0.83 / armL 0.10 — wrong arm),
`2,1` ender uppercut (row 221/158, travel 0.67, active 14), long string
enders); phantom LP1/RP2/RK4 (above); burger LK3, skull LK3 (above).

## Jumping-move restoration bindings (22 moves)

Fixing the standing basics moved their donor source, which regressed jumping
moves that had (correctly, by luck) borrowed the old jumping rows via donor.
These moves get explicit own rows — restorations of verified-passing clips,
not new guesses. T8/T7 moves keep their names and `anim_ref`; only `t3_source`
+ `t3_row` were added.

- **Burger (bryan):** `ub+4`→87, `uf+4`→183, `uf,n,4`→183, `u+1+2,4`→183,
  `ub+3+4,4`→87, `uf+3+4,4`→183, `u/f+4,4`→183 (+`~t7.bob` variant),
  `u/f+1+2,4`→183 (+`~t7.bob`), `u/f+3+4,4`→183 (+`~t7.bob`, `~t7.bob.2`),
  `u/f+2,3,3+4,4`→183. Rows 183 (`u/f+4`, jump, btn 8, legR lift 2.14, travel
  0.05) and 87 (`u/b+4`, jump, btn 8, legR lift 1.68, travel 0.00) are burger's
  OWN T3 jumping moves — the T8 moves missed them via notation spelling
  (`uf` vs `u/f`). Direction-matched (u/b→87, u/f→183; neutral `u+`→183).
  Strings among these remain sequence-UNMAPPED in principle (no single row
  is a multi-hit sequence); the bound clip preserves their jumping-kick
  character, which is what they played before.
- **Diablo (heihachi):** `uf+3,4`→74, `uf+4`→74 (pre-PR donor row, jumping-4
  family, btn 8, legR lift 1.54, starts-airborne; no T3 jumping counterpart
  exists in the diablo moveset).
- **Phantom (yoshimitsu):** `uf+3`→73, `uf+3+4,3`→73 (pre-PR donor row, jump,
  btn 4, legL lift 0.43).
- **Skull (bryan):** `uf+4`→76, `uf,n,4`→76,
  `ub+1+2,1,2,1,2,1,2,1,2,1,4`→76, `u/b+1+2,1,2,1,2,1,2,1,2,1,4`→76
  (pre-PR donor row, jumping-4 family, btn 8, legR lift 1.70; the two long
  Gatling strings are sequence-UNMAPPED, bound clip preserves the jumping
  opening they played before).

All 22 bound moves verify CLEAN in the post-fix audit (sampled: burger
`uf+4`→183, `ub+4`→87, `u/f+4,4`→183; diablo `uf+4`→74; phantom `uf+3`→73;
skull `uf+4`→76).

## What the fixes improved (donor chains)

Improvements are dominated by donor donees of the fixed basics shedding
airborne/jump flags (same audit code both sides):
pantera −72 (donor jump 41 + donor airborne 33, plus notation/own basics);
burger −130 (donor airborne 125); diablo −54 (donor airborne 52);
phantom −70 (donor jump 67); skull −139 (donor airborne 134). Examples:
pantera `b+1` (Quick Hook), `FC.1`, `WS.1`, `df+1` now play standing row 110
instead of airborne row 44; pantera `b+3`, `BT.3`, `ws3`, `df+3` now play
standing row 264 instead of jump row 54; burger/skull `b+1`, `FC.1`, `WS.1`,
`TACKLE.1…` now play standing row 172 instead of airborne 52/50. These are
limb/stance-correct donor clips, NOT exact-identity fixes (see Method caveat).

## Worst remaining mismatches (post-fix audit)

| Fighter | Top HARD classes (post-fix) | Worst examples |
|---|---|---|
| pantera | limb-mismatch 119, jump-clip 72, no-kick-motion 26, ground-clip 21, level 19 | `2,1` → row 220 (chord jump sequence for a jab-uppercut string); `1+2` signature → notation row 35 (jump chord clip; signatures have no T7 truth — left, noted); `d/f+4` → row 135 (no-kick-motion + limb); `u/b+1` → row 37 (jump) |
| burger | jump-clip 119, level 20, jab-travels 4, ground 3, crouch 3 | `3` (LK3) → row 65 jump (UNMAPPED); `1+2` → notation row 41 jump; `d+4` family → donor row 104 (high) for low/mid kicks (level MED/HARD) |
| demonio | jump-clip 60, limb 55, starts-airborne 52, no-kick 19, level 8 | `1` (LP1) → row 41 airborne (UNMAPPED) + 40+ donees; `4,1` → row 184 chord/wrong-arm; `d/f+1` family → jump rows |
| diablo | jump-clip 58, starts-airborne 45, limb 39, no-kick 13, single-on-chord 10 | `1` (LP1) → row 46 airborne (UNMAPPED) + donees; `f+3` → row 135 (chord row, limb); `b+1+2,1` → row 145 chord |
| kinpo | starts-airborne 47, jump-clip 40, limb 11, level 7, single-on-chord 5 | `1` (LP1) → row 35 airborne (UNMAPPED) + donees; `1+2` → notation row 32 jump; `4,1` → row 184 chord/wrong-arm |
| phantom | crouch-clip 157, limb 150, starts-airborne 134, jump-clip 82, no-kick 72 | `2` (RP2) → row 307 crouch (UNMAPPED); `4` (RK4) → row 243 chord arm motion (UNMAPPED) + 12 stance variants; `1` (LP1) → row 62 airborne (UNMAPPED) + donees |
| scimitar | limb 34, single-on-chord 28, jump-clip 22, string-ender-chord 13, jab-travels 2 | `1` (LP1) → row 184 chord/wrong-arm/1.63 m (UNMAPPED) + ~20 donees (`4,1`, `SNK.1`, `TACKLE.1…` all play 184 via donor); `1+2` → notation row 32 jump |
| skull | jump-clip 68, limb 26, level 13, ground 7, crouch 7 | `3` (LK3) → row 63 jump (UNMAPPED); `1+2` → notation row 41 jump; `WS.2:f+2` → donor row 209 chord |

## String-vs-chord re-verification (task item 4)

- **Motion-verified HARD string-enders on chord rows (post-fix): 35**
  (pantera 4 — all the `2,1` family → row 220; demonio 7; diablo 8; kinpo 3;
  scimitar 13; burger/skull/phantom 0). No string ender was rewired to a
  single-hit row: strings play as single resolved moves, so a string needs a
  verified SEQUENCE clip, and no such row exists for these strings in-bank.
  All 35 are UNMAPPED with that reason (the chord rows they play: king 220,
  jin 184/177/231, heihachi 145/135/190/152).
- **Literal branch-mask scan (post-fix): 66** string enders whose played row
  has a multi-bit branch mask, regardless of motion (pantera 17, demonio 11,
  diablo 11, kinpo 7, phantom 5, scimitar 15, burger 0, skull 0). The gap
  between 66 and 35 is chord-branch rows whose MOTION matches the ender
  (e.g. pantera `f,f,F+3` → row 113, a legL kick by foot) plus throw moves
  (exempt). The literal scan is the task's branch-level rule; the motion
  verdict is what decides a rewire, and no rewire survived verification:
  the chord-fix candidate search returned UNIQUE candidates only for
  motion-special/stance moves (pantera `f,n,b,d/b,d,f+1` → 110 rejected: it
  is a THROW playing its own throw row 280; phantom CD+1 → 237 rejected:
  237's provenance is string enders `u+2+3,1`/`b+1,1`, dominant armR) and
  for pantera `f+3` → 139 rejected (113 IS T3's own f+3 row, legL kick by
  shape — the chord mask is a T3-tree artifact, not the motion).
- **Legacy `strings` arrays (NOT consumed by fighter.js — passed through by
  moveset-library.js only; documented, not edited):** per-hit-mapped entries
  (len(t3_rows) == len(hits)) with a single-button hit on a chord row: 6
  total — pantera `2,1` hit `1` → row 220 (btn 3); demonio `4,1` and `4,1,2`
  hit `1` → row 184 (btn 9); kinpo same 2; scimitar `1,2` hit `1` → row 184.
  If these arrays are ever consumed, they need the same sequence-clip fix.
- **Chord-on-single-row (chord move playing a single-button row):** still
  HARD where it occurs (pantera 6, demonio 3, diablo 1, kinpo 3, phantom 2,
  skull 1 — own/notation/anim only). A chord move playing a single-limb
  motion is visibly wrong (one arm instead of two).

## Slots overrides (reported, NOT changed — moveset-lane/owner decision)

Slots resolve a press to a different move than the T8 basic (measured
post-fix):
demonio `4`→`4~3` (Spinning Flare Kick) — harmless: it plays donor row 199,
the same row as T8 `4~t8.jin`'s notation, CLEAN before and after;
diablo `4`→`4~3` (Demon Scissors) — donor row 74 (airborne HARD) → 104
(CLEAN) via this PR's `4` rewire; a standing high kick for Demon Scissors,
approximate but now stance/limb-clean;
phantom `3`→`3~4` (Tobi Ushiwaka) — donor row 73 (jump HARD) → 123 (CLEAN)
via this PR's `3` rewire;
phantom `4`→`4~3` (Kangaroo Kick) — donor row 309, jump-clip HARD before
and after (a standing string playing a jump clip). Pressing RK4 on phantom
therefore plays a jump clip via the slot override, while the T3 basic `4`
itself plays chord arm row 243 — both wrong, differently. Changing slots is
out of this lane's scope.

## Alternate T7/T3 wirings explicitly REJECTED (shape contradicts the claim)

Do NOT use these rows for these moves — report as miswires, do not rewire to
them: pantera `1~t3.king` row 290 = a THROW row for a jab (the known
fighter.js-comment bug class: Pantera T8 Jab anim_t3 row 290 is King's
decoded throw attempt); pantera `4~t3.king` row 106 = btn 2 punch row for a
RK4 move (foot +0.48 is a leg lift inside a punch motion, not a kick);
pantera `3~t3.king` row 122 = crouching low kick for Face Kick (high);
demonio `4~t3.jin` row 114 = low kick (word l) for High Right Roundhouse
(high); demonio `1~t3.jin` row 165 = lunging mid punch (travel 1.14, word m)
for a jab; diablo `1~t3.heihachi` row 209 = duck-dip lunging right punch
(travel 1.24) for a jab; phantom `2~t3.yoshimitsu` row 126 = retreating motion
(travel 1.83, netZ −1.17, word m) for a jab; phantom `3~t3.yoshimitsu` row 139
= crouching low kick for a high kick; phantom `4~t3.yoshimitsu` row 141 =
low, retreating (netZ −0.55), leg ext ~0.03 for Magic 4 (high); phantom
`1~t3.yoshimitsu.2` row 317 = a THROW row for a jab (same bug class as
pantera 290).

## Word-vs-shape conflicts (decoded word is not the motion)

- king 216 (pantera RK4, KEPT): word m, foot +0.31 above hips at active —
  T7 says high; shape wins, kept.
- jin 195 / heihachi 153 (demonio/kinpo/scimitar LK3, diablo LK3, KEPT): word
  m, foot +0.89 above hips at active — T7 says high for Jin/Heihachi/Shaheen;
  shape wins, kept. For kinpo (Asuka 3 = mid) this is a height concern, not a
  fixable rewire (see kinpo LK3 above).
- jin 199 (demonio/kinpo/scimitar RK4, KEPT): word m, foot −0.15 below hips at
  active — mid-height roundhouse; T7 says high for all three. Only high
  alternative (jin 100, foot +0.37) travels 1.28 m — a lunge, a bigger visual
  error. Soft level mismatch, kept.
- king 113 (pantera f+3, KEPT): branch btn 12 (chord) but legL kick by shape
  (foot 1.35 m at active). Branch mask ≠ motion.

## Regressions from this PR (honest list)

10 moves, all pantera LOW RP2 moves, all MED→HARD level-grade changes (not
new wrong clips — they still play a donor jab row, but the donor changed
from mid row 203 to high row 99, so the level grade vs LOW went MED→HARD):
`f,F+1+2~t7.king`, `CH.f,f,n,2` (Jaguar Hammer), `f,f,F~t7.king`,
`t7.king_140` (Face Up, Feet Towards+3), `t7.king_232` (Head Bomber),
`t7.king_235`, `t7.king_236`, `t7.king_237`, `t7.king_238`, `t7.king_239`.
No verified low RP2 row exists in the king bank (only row 130, travel 0.84,
whose only user is the `d/f+4` kick move — not a verified low punch).
These 10 are UNMAPPED: no low RP2 clip available from VM+browser sources checked (king bank searched; only row 130 exists and the file attaches it to the `d/f+4` kick move, so the file does not specify a low RP2 punch clip). No other regressions: every
other ok→HARD flip from the basics fix was restored via the 22 bindings
above (verified: remaining regression count is exactly these 10).

## What is still wrong (honest statement)

- **9 UNMAPPED basics still play broken clips:** demonio/kinpo/scimitar/diablo
  LP1 (airborne/wrong-arm/chord rows), phantom LP1 (airborne), RP2 (crouch),
  RK4 (chord arm motion), burger/skull LK3 (jump clips). These are the
  highest-visibility remaining failures after this PR.
- **~33% of pressable moves (1554/4696) are still HARD-flagged** — the bulk
  is jump/airborne/ground/crouch/limb mismatches beyond basics and
  chord-enders, documented here but NOT bulk-rewired, because no verified
  replacement row exists per move. Bulk-rewiring them to class-correct rows
  would repeat the exact failure this audit was built to stop (a jumping
  punch is not a jab; a hook is not a jab; a donor clip is not the move).
- **Donor poisoning is structural:** the largest plan kind for most fighters
  is donor fallback (e.g. pantera 411 donor picks pre-fix). Every donor
  donee inherits its source row's wrongness. Fixing donor sources (as done
  here for basics) is the highest-leverage fix, but the engine still has no
  per-hit string clips: a string move plays ONE clip, so no single row can
  ever be a correct multi-hit string. That needs an engine lane, not a
  moveset lane.
- **Slots overrides** (above) mean diablo RK4 and phantom LK3/RK4 presses play
  different moves than the T8 basics, regardless of this PR.
- **Yoshimitsu L/R labels** depend on the turn assumption (see Caveats).
- **Not play-verified.** Everything above is simulation/scan proof from
  decoded frames. The live game must still be played on a phone (portrait,
  human navigation) to confirm the fixes land as expected.

## Files changed in this PR

- `game/assets/movesets/pantera.json` — `1`: 44→110, `2`: 203→99, `3`: 54→264.
- `game/assets/movesets/burger.json` — `1`: 52→172, `2`: 152→100, `4`: 78→104;
  14 jumping bindings (rows 183/87).
- `game/assets/movesets/skull.json` — `1`: 50→172, `2`: 152→100, `4`: 76→104;
  4 jumping bindings (row 76).
- `game/assets/movesets/diablo.json` — `4`: 74→104; 2 jumping bindings (row 74).
- `game/assets/movesets/phantom.json` — `3`: 73→123; 2 jumping bindings (row 73).
- `tools/combat-qa/anim_motion_audit.py` — the audit tool (new).
- `docs/anim/ANIM-MOTION-AUDIT-2026-10-24.md` — this doc (new).
- `WORKLOG.md` — entry (prepended).
- kinpo.json, scimitar.json: audited, NO changes (all their
  basics are KEEP or UNMAPPED; no verified rewire exists).
- demonio.json: 1+2 rewire in the 2026-10-24 follow-up section below
  (this line superseded by that section).

## 2026-10-24 follow-up — LP1+RP2 (1+2) chord decision

Button names: LP1 = Left Punch = Tekken 1, RP2 = Right Punch = Tekken 2,
LK3 = Left Kick = Tekken 3, RK4 = Right Kick = Tekken 4.

After the main audit, a top-donor scan showed the `1+2__main` chord moves
as the largest remaining fixable donor sources: 7 fighters, 102 HARD
donees plus 7 HARD sources, all playing jump clips. The T3 tables attach
the current rows to T3's own 1+2 (king row 35, bryan row 41, heihachi row
37, jin row 32, yoshimitsu row 265) — so the current rows are T3-own
attachments, not misassignments. But they measure as jump clips (except
yoshimitsu 265) for standing strikes, so the file attachment and the
standing-strike motion disagree. Each fighter below was judged on the
same rewire rule as the main audit: same bank, standing stance, level
match (or no single-level truth), filed limb = played limb under the
audit's dominant-limb rule, reasonable travel, named file provenance
(a T3-table move or a moveset move whose input is a LP+RP command).
A candidate failing ANY check was rejected; no closest-match fill.

### Rewired (2 moves)

- demonio `1+2__main`: jin row 32 → row 92. Provenance: demonio moves
  `d+1+2` (input d+1+2) and `1+2~t3.jin` (input 1+2_r107, a 1+2 variant)
  both use row 92. Profile: standing, level h, dominant armL (audit
  extension armL 0.53 / armR 0.38, both arms participate), travel 0.21,
  active 10 vs move startup 12. Filed T7 level is `mmh` (multi-level
  string in the source data; the audit treats it as no single-level
  truth), so no level conflict. Result: source CLEAN (was HARD
  jump-clip + MED posture). Pressable flips: 13 (4 notation donees —
  signature `1+2`, `1+2_t8`, `1+2~t7.jin`, `1+2~t7.jin.2` — plus 9 donor
  donees: ZEN.1+2, TACKLE.1+2, WR.1+2, FUFT.1+2, FLY.1+2, FLY.4,2,1+2,
  f,n,d,d/f+4,1+2, MCR.1+2, MCR.4,2,1+2). Pressing LP1+RP2 now plays a
  standing double-arm strike instead of a jump clip. No bindings
  needed: all 9 donor donees have standing expectations.
- diablo `1+2__main`: heihachi row 37 → row 133. Provenance: T3 table
  key `b_r133`, command 4/6+LP+RP (a directional LP+RP move), and
  diablo move `b_r133`. Profile: standing, level m, dominant armL
  (audit extension armL 0.28 / armR 0.07 — right-arm radial extension
  is low, disclosed; the file provenance is a directional LP+RP
  command, and the audit's chord limb rule passes it via dominant
  armL = filed armL), travel 0.23, active 10 vs move startup 12.
  Result: source CLEAN (was HARD jump-clip + MED posture). Pressable
  flips: 22 (4 notation donees — signature `1+2`, `1+2_t8`,
  `1+2~t7.heihachi`, `1+2~t7.heihachi.2` — plus 18 donor donees,
  including ws3,1+2, WS.3,1+2, FUJ.1+2, WAR.1+2, RAI.1+2, WR.1+2,
  FUFT.1+2). No bindings needed: the only non-standing donees are
  WS (while-standing) strikes, which a standing chord row suits; no
  jumping donee exists for this row.

Verification (audit tool, same code both sides, current main movesets):
demonio pressable HARD 174 → 161, diablo pressable HARD 156 → 134.
Every changed move is listed above; ZERO moves went from CLEAN to
HARD, and no move changed rows except 32 → 92 (demonio) and 37 → 133
(diablo). Only `t3_row`, the `(T3 <bank> rNN)` row reference in `name`,
and `anim_ref` changed; no damage, startup, T7/T8 fields, slots, or
other move fields were touched.

### UNMAPPED, with file-absence evidence (5 fighters)

- pantera `1+2__main` (king row 35): NO verified standing chord row.
  Every standing chord candidate has LP+RP provenance but fails a hard
  criterion: row 143 (standing, m, armL, travel 0.19; pantera move
  b~t3.king.4, command 4/6+LP+RP) fails timing (active 10 vs startup 18,
  1.8x stretch, beyond the 1.53x max accepted in the main audit for row
  264); row 97 (pantera d+1+2 / b+1+2) fails level (h vs m) and timing
  (1.8x); rows 116 (pantera d/f+1+2) and 131 (pantera d/b+1+2) fail
  timing (active 8 vs 18, 2.25x) and level (s vs m); row 227 (T3 1+2
  variant) fails limb (dominant armR vs filed armL) and travel (0.91).
  UNMAPPED: no candidate passes all criteria.
- burger `1+2__main` (bryan row 41): NO verified standing chord row.
  Row 129 (d/f+1+2 provenance, standing, m, travel 0.43) fails the
  audit's limb check (dominant armR 0.46 vs armL 0.33, filed armL) —
  rewiring to it would trade a jump HARD for a limb HARD, not a fix.
  Row 132 is a back move (`b` input), not a LP+RP motion, and its
  right arm barely moves (ext 0.07). Row 108 fails level (h vs m),
  limb (armR), and travel (0.37 is fine but the other two fail).
  Row 116 fails level (l vs m), timing (active 8 vs 19), and
  provenance. UNMAPPED: no verified replacement row in-bank.
- skull `1+2__main` (bryan row 41): same bryan-bank evidence as burger
  (startup 17 vs 19; row 129 still fails limb, row 132 still a back
  move). UNMAPPED: no verified replacement row in-bank.
- kinpo `1+2__main` (jin row 32): NO verified standing chord row.
  Row 134 is a back move (`b` input), dominant armR (limb fail),
  travel 0.58. Rows 92/105 (the demonio rewire) fail timing for kinpo
  (active 10 vs startup 16). UNMAPPED: no verified replacement row
  in-bank.
- scimitar `1+2__main` (jin row 32): same jin-bank evidence as kinpo
  (startup 18; rows 92/105 active 10 vs 18). UNMAPPED: no verified
  replacement row in-bank.

### No change needed (1 fighter)

- phantom `1+2__main` (yoshimitsu row 265): NO ACTION. Row 265 passes
  the audit (standing, m, active 22 = startup 22, zero flags) and all
  33 donor donees are CLEAN. The T3 table attaches row 265 to Yoshi
  1+2. Rewiring would risk 33 clean donees for no flagged fault; the
  1.51 m retreat travel is not flagged by any audit rule.

### Totals after this follow-up

Pressable HARD: demonio 174 → 161, diablo 156 → 134 (combined −35,
0 regressions). All other fighters unchanged by this follow-up.
