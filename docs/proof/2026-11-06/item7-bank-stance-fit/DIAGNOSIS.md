# Bank-stance fit class — diagnosis (Roster-100 Wave 3 item 7, 2026-11-06)

## The gate

`game/js/select-screen.js`, `PreviewPane.show()`: after retargeting the fighter's bank
stance clip it samples one pose (`mixer.update(0.05)`) and applies three checks —
(a) head-hips gap > 0.25, (b) each hand within arm reach, (c) clavicle check: each
shoulder's **world** quaternion angle vs the model's bind pose > **0.6 rad** → reject,
fall back to the CMU 14_01 guard stance. Fighters named in the item brief: the SmutBase
six + Pantera + Demonio.

## Measurement 1 — the gate's own verdicts (real PreviewPane, portrait-capture page)

`gate-before.json` (this folder): 11 of 11 fighters rejected, every one on check (c):

| fighter | bank (effective stance) | world reading | verdict before |
|---|---|---|---|
| Pantera | king (T7 stance) | L 0.69 | rejected |
| Demonio | jin (T3 neutral) | L 0.71 | rejected |
| Pond | raven (T7 stance) | L 1.61 | rejected |
| Ryusan | luckychloe (T7 stance) | L 1.23 | rejected |
| Tobi | hwoarang (T7 stance) | L 1.02 | rejected |
| Megami | jun (T3 neutral) | L 2.50 | rejected |
| Menajerii | roger (T3 neutral) | L 0.80 | rejected |
| Star | xiaoyu (T3 neutral) | L 0.89 | rejected |
| Negativo | bryan (T7 stance) | L 0.77 | rejected |
| Purple Rain | jin bank (T7 stance) | L 1.38 | rejected |
| Awapop | nina (T3 neutral) | L 1.11 | rejected |

A second batch (diablo 0.81, skull 1.38, docfrank 1.32, burger 1.08, sakura 1.37,
phantom 1.59, nightwolf 1.20) was also rejected 7 of 7. **In 18 measured fighters the
gate passed nobody** — the shipped select screen shows the CMU fallback for every
banked fighter, which is why the M3 portrait cards all read cmu-14_01.

## Measurement 2 — intrinsic FK on each clip's own skeleton

`intrinsic.json` (tool: `tools/input-verify/intrinsic_i7.py`): the effective stance
clip composed down its own source skeleton (identity rest rotations — the game's own
FK convention from `bankFacing`), per frame. At the gate's sample time:

| fighter | world L (intrinsic) | chest world | clavicle chest-relative L / R |
|---|---|---|---|
| Pantera | 0.69 | 0.73 | 0.24 / 0.14 |
| Demonio | 0.56 | 0.33 | 0.27 / 0.38 |
| Pond | 1.57 | 1.77 | 0.44 / 0.39 |
| Ryusan | 1.01 | 1.28 | 0.28 / 0.18 |
| Tobi | 1.11 | 1.09 | 0.36 / 0.31 |
| Negativo | 0.57 | 0.58 | 0.17 / 0.27 |
| Purple Rain | 0.97 | 0.98 | 0.11 / 0.41 |
| Star | 0.84 | 0.47 | 0.38 / 0.38 |
| Awapop | 0.72 | 0.24 | **0.85** / 0.40 |
| Megami | 2.40 | 1.67 | **2.38 / 3.09** |
| Menajerii | 0.85 | 1.46 | **2.23 / 0.98** |
| Chatur | 0.45 | 0.70 | 0.69 / 0.55 |

The intrinsic world readings reproduce the pane's numbers (Pantera exact at 0.69;
Pond 1.57 vs 1.61; Tobi 1.11 vs 1.02) — **the retarget is faithful; nothing is
misapplied for the main class.** The mechanism is plain: a real kamae turns the whole
torso side-on, the shoulder's *world* orientation inherits the chest's full turn, and
check (c) was measuring the torso, not the clavicle. The clavicle's own chest-relative
swing in every healthy stance is 0.11–0.44 rad — comfortably under the gate's 0.6.

The world reading also fails in the other direction: Menajerii reads only 0.80 in
world space while her clavicle is intrinsically swung 2.23 rad (her chest
counter-rotates) — the old check understates the one genuinely broken case in the set.

## The genuinely broken data (stays rejected, own defect class)

- **Megami (jun bank)** and **Menajerii (roger bank)**: the bank neutrals themselves
  rotate the clavicles 2.2–3.1 rad relative to the chest, constantly through the clip
  (means 2.24 / 2.23). In a fight (no gate) Menajerii's idle shows it directly:
  head thrown back, left arm flung up behind her — `fight-menajerii-stance.png`.
  Pantera in the same capture stands a correct guard — `fight-pantera-stance.png`.
  The jun/roger shoulder tracks need their own bank-data investigation; not this item.
- **Awapop (nina bank)**: left clavicle intrinsically 0.85 rad — over the cap in her
  own data; stays on the fallback until that data is judged.
- **Chatur (ogre bank)** never reaches the gate at all: `retargetT3Clips` returns
  null for his model (the rig analysis bails on his four-armed 264-joint source rig;
  bank clips load fine — 211 clips, stance present — and his canonical Hips /
  RightArm / Head bones all exist). This matches his pose-only state since the ogre
  bank was attached. Separate defect, separate lane: rig analysis for multi-arm rigs.

## The fix (this PR)

Two parts, no threshold moved on the check's own quantity:

1. `game/js/t3anims.js` — `retargetT3Clips` stamps each retargeted **stance** clip
   with `userData.intrinsicRel` {L, R}: the source clip's chest-relative clavicle
   swing at the gate's 0.05 s sample, composed on the bank's own skeleton (covers
   both the T3 path and the T7-stance swap, which retargets through the same call).
2. `game/js/select-screen.js` — check (c) becomes a paired reading:
   the retargeted pose is read **chest-relative on the rig** (a rig's bind clavicle
   direction legitimately differs from the bank's; measured slack across seven
   shipped rigs 0.32–0.68 rad), and the stance is rejected when
   (c1) the source clip's own intrinsic swing exceeds the gate's original **0.6 rad**
   — the same threshold, applied to the quantity the check always described; or
   (c2) the retargeted chest-relative swing exceeds the intrinsic swing by more
   than **0.75 rad** (the measured rig-divergence slack, with headroom) — the
   gyro/misapplication catcher. When no intrinsic stamp exists, the chest-relative
   reading is still capped at 0.6.

## After (`gate-after.json`, same 11 fighters, same harness)

Accepted (tekken-bank): **Pantera, Demonio, Pond, Ryusan, Tobi, Star, Negativo,
Purple Rain** — select portraits for Pantera / Pond / Demonio in this folder show
their real stances (`select-pantera.png`, `select-pond.png`, `select-demonio.png`).
Still rejected, with the source-clip reason: **Megami (2.38), Menajerii (2.23),
Awapop (0.85)**. Chatur unchanged (his blocker is upstream of the gate).

Negative control: Pantera's source stance with its LeftShoulder track premultiplied
by a +1.3 rad rotation was rejected by the patched pane ("1.31 rad in the source clip
itself", CMU fallback) — the guard still guards. The fidelity half fired in
development too: Star's retargeted swing (1.06) exceeded her intrinsic (0.38) by
0.68 and was rejected while the slack stood at 0.65, accepted at the measured 0.75.

Local suites on the patched tree: stance/input/t3 test files 80/80 pass. CI runs the
full gate set on the PR.
