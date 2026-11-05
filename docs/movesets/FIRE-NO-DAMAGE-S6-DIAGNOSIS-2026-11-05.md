# Roster-100 Wave 1 · S6 — Fire-no-damage diagnosis

Item: S6 of `docs/handoffs/ROSTER-100-FIX-2026-11-04.md` — the 41 roster
inputs the #1559 roster pass scored `fires-no-damage` (the animation
fires, the defender's HP does not move), waterfall's 5 first, then the
`1+2` cluster of 16, then the remainder. Brief rule: fix only on a proven
cause, per fighter, from that fighter's own data; damage figures are
never invented; a fighter whose own data cannot produce a damage path is
documented as a data gap, not filled.

**Verdict: none of the 41 is a hit-data defect. No game data file is
changed by this item.** Every input is accounted for in one of four
classes, each proven in a real fixed-step fight probe against Pantera on
current main (tip `a2aa63e8` at write time; the probed tree was built
from `3996ab07` + the #1580/#1581 payloads and re-audited by blob SHA —
the intervening merges do not touch any probed moveset):

- **Class A — roster-pass harness artifact (30 inputs).** The input
  fires and deals exactly its recorded damage once the defender is
  actually standing at the probed spacing (root cause 1, below).
- **Class B — throw completes with the fight model loaded (5 inputs).**
  All five `1+3` throws bind their file pair (or complete their lock)
  and deal their recorded damage; the roster-pass/model-less readings
  were root cause 2.
- **Class C — honest zero in the fighter's own source data (4 inputs).**
  Stance/parry entries whose source rows carry no damage at all
  (`t8_damage`/`t3_damage` null in the fighter's own file). They are not
  strikes and there is no damage to restore; inventing one is exactly
  what the brief forbids.
- **Class D — in-range only (2 inputs).** The input deals its full
  recorded damage at 1.1 m and whiffs at 1.8 m — the same envelope as
  the fighter's own control inputs at 1.8 m. Not a hit-data defect.

The S1 charger d/f+2 damage rider is closed as the same Class A harness
artifact (section 4). The S5 buttons referral is assessed with a nil
blast radius for this set (section 5). The S3 scale/reach class
(Cainelias) was checked across the whole set on the coordinator's
instruction: zero of the 41 belong to it (section 3).

## Method

- Serve tree = current main, assembled per-file from the GitHub API;
  every `game/` JS/moveset/anim file used was blob-SHA audited against
  main, and every fight model in the tree was size-verified against
  main (25 files; cyborgx's 86 MB attire-1 model — the game's actual
  load path `roster/cyborg-x/attires/attire1/model-rigged.glb` — was
  completed by a resumable range download and verified by git blob
  SHA-1 `6c6ee948…`, matching main).
- Probe: the S5 lane's fixed-step harness pattern (DT = 1/120,
  `g._update` stepped manually, AI stubbed, 1e6 HP, `receiveHit` /
  `startThrowLock` instrumented on the defender). Placement: settle-wait
  until the defender's root is stable (< 0.02 m over 30 steps), then
  place BOTH fighters explicitly (defender at x=0, attacker at
  x=−spacing) and step 6 so facing re-derives before `tryAttack`.
  Spacings 1.1 m and 1.8 m for every input, plus a working control
  input per fighter. Proof files: `docs/proof/2026-11-05/fire-no-damage-s6/`.
- Damage figures below are the probe's measured HP deltas; the recorded
  (data) damage is the moveset row's own `damage` — dealt = recorded ×
  attacker power / defender defense, the engine's own formula.

## Root cause 1 — the defender is still relocating when the ready gate opens

Frame-level trace of waterfall d/f+1 in the ORIGINAL (S5-style)
placement, `probe-waterfall-diag.json`: at sample start the defender
(Pantera) is not yet at her fight anchor. The ready gate opens on
`roundState == 'fight'` + fighter identity while round-start
positioning is still moving her. The old probe placed the attacker
relative to her transient position (she sat at x=−2.2; the attacker was
placed at −1.1 facing −1, correct toward her at that instant); she then
snapped to her anchor (x=0) BEHIND him. At the active window the roots
were 3.81 m apart with the weapon pointing away: the geometry path
misses and the range fallback's facing sign check fails, so neither
contact path can register. The #1559 roster pass used the same
place-relative-to-defender pattern, and its fire-no-damage verdicts
inherit this artifact. With settled placement, the same inputs deal
their recorded damage (Class A table).

## Root cause 2 — paired throws need the fight model in the tree

Waterfall 1+3 in the model-less tree: `startThrowLock` engaged with the
correct row (jin r276, damage 21) and the defender's HP never moved. In
the same harness with waterfall's verified model
(`roster/waterfall/attires/attire1/model-rigged.glb`, blob-audited)
loaded, the throw binds its file pair (jin vs king), `_throwPairDamage`
lands at the pair's damage time, and the defender goes to knockdown:
HP 1,000,000 → 999,980.75 = **19.3 dealt** (`throw-waterfall-1p3b.json`).
All five Class B throws were re-proven the same way, with models.

## 3. The S3 scale/reach check (Cainelias class) — zero of 41

On the coordinator's instruction (S3 / PR #1584: cainelias `3` was
fire-no-damage purely from miniature scale — 0.979 m tall, origin at
figure center, lower half below the floor — whiffing at 0.75 m spacing;
post-fix 1.819 m and grounded, the same untouched move data connects
for 8.2): every fighter in this set was checked for the same signature —
a damaging input that whiffs at close spacing because the model is
undersized or sunk. Findings:

- Every damaging input in the 41 connects at 1.1 m. Cainelias's defect
  whiffed at 0.75 m; no input here whiffs at 1.1 m except the Class C
  non-strikes (no damage exists) — the scale signature is absent.
- The only range-limited cases (Class D) were measured directly:
  mariposa-monarch's idle model height is **1.933 m** with
  **minY −0.006** (grounded) — normal roster scale, not miniature, not
  sunk (`scale-mariposa.json`). Silvertongue's harness bbox measurement
  was degenerate (bind-pose bounds) and is not used; her classification
  rests on the control-parity evidence instead (her control whiffs at
  1.8 m identically).
- Verdict: **zero of the 41 are scale/reach artifacts of the Cainelias
  class.** The class is real (S3 proved it for cainelias, who is not in
  this set) but it does not occur here.
## Class A — harness artifact; input deals its recorded damage (30)

Dealt values at 1.1 m / 1.8 m (— = whiff at 1.8 m, in-range class D or
control-parity reach; every entry deals its damage at 1.1 m).

| Fighter · input | Resolved plan | Data dmg | Dealt 1.1 / 1.8 |
|---|---|---|---|
| waterfall 1+2 | signature "Nine Souls' Grief" (jin row 32) | 19 | 25.2 / 25.2 |
| waterfall d/f+1 | jin row | 8 | 10.8 / 10.8 |
| waterfall d+1 | jin row | 3 | 4.1 / 4.1 |
| waterfall d/f+2 | jin row | 6 | 8.1 / 8.1 |
| phantom 2 | `2~t7.yoshimitsu` | 13 | 11.9 / 11.9 |
| phantom 1+2 | t3 yoshimitsu row 265 | 20 | 18.3 / 18.3 |
| diablo 1+2 | `1+2~t7.heihachi` | 33 | 42.3 / 30.3 |
| skull d/f+1 | `D/F+1` (bryan) | 10 | 9.2 / 9.2 |
| samura1 1+2 | row 49 | 20 | 30.3 / 18.3 |
| sakura 4 | `4~t7.xiaoyu` | 8 | 19.3 / 7.3 |
| sakura 1+2 | `1+2~t7.xiaoyu` | 17 | 15.6 / 15.6 |
| kinpo 1+2 | row 32 | 21 | 19.3 / 19.3 |
| dio 2 | row 222 (akuma) | 9 | 8.3 / 8.3 |
| dio 4 | row 83 | 7 | 6.4 / 6.4 |
| star 1+2 | row 314 | 18 | 16.5 / 16.5 |
| baek-master-white 4 | bryan row 81 | 15 | 13.8 / 13.8 |
| baek-master-white 1+2 | row 41 | 17 | 15.6 / 15.6 |
| dxmmii-patchwork 1+2 | row 32 | 18 | 16.5 / 16.5 |
| pond d/f+1 | `d/f+1~t7.masterraven` | 7 | 5.8 / 5.8 |
| tobi u/f+4 | hwoarang row 95 | 7 | 5.5 / 5.5 |
| rave 2 | row 200 | 6 | 5.5 / 5.5 |
| rave 3 | row 131 | 18 | 16.5 / 16.5 |
| buffalo-bill 1+2 | row 99 (strike, hit word 535) | 11 | 22.1 / 10.1 |
| buffalo-bill u/f+4 | row 86 | 8 | 7.3 / 7.3 |
| chordz 1+2 | row 32 | 18 | 16.5 / 16.5 |
| gashadokuro 4 | `4~t8.kuma` row 118 | 11 | 22.1 / 10.1 |
| cyborgx 1+2 | row 49 | 19 | 17.4 / 17.4 |
| cyborgx d/f+1 | row 239 | 10 | 9.2 / 9.2 |
| cyborgx d+1 | row 169 (gunjack) | 5 | 4.6 / 4.6 |
| koreshi 1+2 | row 105 — spacing-dependent resolution | 0 / 36 | 0 (stance contact) / 33.0 |

Koreshi note: at 1.1 m the slot resolves to the close form — contact
registers (defender hitstun) with the row's recorded 0; at 1.8 m the
same input resolves to the row's damaging form (data 36, dealt 33.0).
Both behaviors are the fighter's own recorded data; neither is a
defect. (His first probe attempt crashed the headless renderer —
`probe-D-koreshi.json`, every sample "Target page … has been closed";
the clean re-probe is `probe-F-koreshi.json`.)

## Class B — throws complete with the fight model loaded (5)

All five `1+3` inputs: defender state sequence `thrown → thrownExec →
knockdown` in the probe (waterfall via the pair path, §2).

| Fighter · input | Data dmg | Dealt 1.1 / 1.8 |
|---|---|---|
| waterfall 1+3 (jin r276) | 21 | 19.3 / (pair proof at 1.1) |
| zui 1+3 (steve row 274) | 19 | 17.4 / 17.4 |
| bruno 1+3 (miguel "Paseo", row 210) | 21 | 19.3 / 19.3 |
| chordz 1+3 (lars row 273) | 19 | 17.4 / 17.4 |
| gashadokuro 1+3 (kuma) | 19 | 17.4 / 17.4 |

Out of scope and untouched, per the brief: Menajerii 2+4 and Vain Abel
1+3 remain the S7 throw-execution class.

## Class C — honest zero in the fighter's own source data (4)

| Fighter · input | What the source row is | Probe behavior |
|---|---|---|
| zui 3 | Steve "Ducking Left" — DCK stance transition, `t8_damage` null, damage 0 | contact + hitstun, 0 damage, both spacings |
| zui 4 | Steve "Ducking Right" — SWY stance transition, `t8_damage` null, damage 0 | contact + hitstun, 0 damage, both spacings |
| docfrank 1+2 | Bosconovitch "Parry" — parry stance entry, `t3_damage` null | contact + hitstun, 0 damage, both spacings |
| tobi 1+2 | Hwoarang "Disrespect" — "Transition to BT", `t8_damage` null | no contact (pure stance turn), both spacings |

These animate and (except the pure turn) connect; their source data
carries no damage because they are not attacks. Documented, not
filled — the #1560/S1 data-gap pattern.

## Class D — in-range only (2)

| Fighter · input | Data dmg | Dealt 1.1 / 1.8 | Evidence |
|---|---|---|---|
| mariposa-monarch 1+2 | 16 (t3 row 314) | 14.7 / whiff | measured height 1.933 m, minY −0.006 (§3); the move's own reach ends before 1.8 m |
| silvertongue 2 | 4 (lili row 124) | 3.7 / whiff | her control `1` whiffs at 1.8 m identically — fighter-wide short-poke envelope, not input-specific |

## 4. S1 rider — charger d/f+2: CLOSED, harness artifact

S1 (#1580) re-keyed charger d/f+2 to Bryan bank row 149 (damage 9, hit
word 535, hit_frames row 149 = active frame 23 only) and recorded 0
damage at every spacing in its harness, while the same bank row dealt
19 through Skull. In this item's deterministic fixed-step harness
(`probe-E-charger.json`):

- charger d/f+2 at 1.1 m: plan `row:149`, move damage 9, hit word 535,
  contact registered, **HP delta 9 — the row deals exactly its recorded
  damage.** (At 1.8 m it whiffs, as do charger's own `1` and `2`
  controls in this harness — his kit's reach envelope, not the row.)
- The S1 number is explained by the harness difference: S1 drove real
  keyboard input through real-time stepping in software GL, where the
  row's single active frame (frame 23 of 60, active window 0.017 s in
  the bank-raw timing his file carries) can fall between rendered
  frames; the fixed-step harness steps the combat clock at 1/120 and
  the combat-core active-window floor (3 frames) applies. Skull's 19
  in the #1559 pass is the same row family resolved through Skull's
  own T7-layer wiring (his d/f+2 plan is `d/f+2~t7.bryan`, data damage
  12, dealt 11 in this harness) — a different record for a different
  fighter, not evidence about charger's row.
- No change to charger.json or charger-attire2.json. The rider is
  closed; S1's fix stands as landed.

## 5. S5 referral — buttons = 0 in produced roger/jun rows: nil blast radius here

S5 deviation 1: in the two S5-produced TTT2 banks (roger, jun),
`hit_frames.json` buttons are 0 (unknown) except four slot identities,
because the motbin cancel/branch graph is not cracked. Assessment for
this set: **no fighter in the 41 resolves through the roger or jun
bank** (Menajerii and Megami are not in the fire-no-damage set), and
the T3 banks the set does use carry decoded buttons (e.g. bryan row
149, buttons 2 — the value charger's hit word path consumed above).
The limitation stays recorded as a bank-production item for the TTT2
line; it causes none of the 41 and fixing it is not an S6 data change.

## 6. What changed

Nothing in `game/`. This item lands the diagnosis (this file), the
proof set (`docs/proof/2026-11-05/fire-no-damage-s6/`), the handoff
execution record, and the checkpoint record. If a future pass wants the
roster harness itself hardened against root cause 1, the fix belongs
to the probe tooling (settle + explicit placement, as in this item's
method), not to any fighter's data.
