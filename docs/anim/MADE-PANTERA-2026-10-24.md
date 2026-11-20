# MADE animations — Pantera's 3 signatures (2026-10-24)

**MADE label, everywhere.** Every file below is labelled MADE in its filename,
its JSON `provenance`/`source` fields, and this doc. None of them is decoded
from a game. Each one is an ADAPT: a real decoded T3 King clip, transformed
by the documented operation. The source clips stay credited as decoded T3
motion; the MADE clip is the transformed result.

**Buttons use LP1/RP2/LK3/RK4 everywhere.** LP1 = Left Punch = Tekken 1,
RP2 = Right Punch = Tekken 2, LK3 = Left Kick = Tekken 3, RK4 = Right Kick =
Tekken 4.

## Pipeline finding (read before wiring)

The game loader does **not** currently have a MADE-clip path, and the
moveset `anim_ref` field is **not** read by combat animation selection:

- `game/js/t3anims.js` `jsonToClip()` reads only `bones`, `rot_xyzw`,
  `root_t`, `fps` — the three clips below are written in exactly that
  `wh-anim/1` shape, so they *load* through `jsonToClip()` unchanged.
- `game/js/t3anims.js` hardcodes `clip.userData.source =
  'REAL T3 decoded motion'`. Before any MADE clip is wired, that line must
  become data-driven (`data.source`), or a MADE clip would be mislabelled
  as decoded at runtime. **Do not wire until that fix lands.**
- `game/js/fighter.js` `_attackClipPlan()` picks clips from the fighter's
  own T3 bank rows (`t3_row` / notation / donor / match / generic). It
  never reads `anim_ref`. Wiring therefore needs a new `made` tier in
  `_attackClipPlan()` (keyed e.g. by a `made_clip` moveset field), plus a
  `hit_frames`-style entry for each MADE clip's hit window. Until then
  these clips are **shipped, validated, and unwired** — the game will keep
  playing its current fallback for the three signatures, and this doc
  must not be read as claiming otherwise.
- The three `wh:` refs (`wh:pantera:sig:honest-hold`,
  `wh:pantera:sig:tail-tip-lunge`, `wh:pantera:sig:battle-itself`) are
  preserved in each clip's `move` field so the wiring PR can key on them.

## Per-move table

Source bank for all three: `game/assets/anim/t3/king_on_pantera_leoman/`
(decoded T3 King, `divmot03_king.bin`). Warp anchors were *measured*, not
guessed: forward kinematics over the bank's own `skeleton.json` rest pose
(identity rest rotations), extension = hand-to-Chest distance per frame,
peak = argmax. Builder: `tools/anim/made_pantera_build.py`.

| Move | Input (LP1/RP2/LK3/RK4) | Limb / dmg / startup | Method | Source clip (decoded) | What changed, and why it matches the canon description |
|---|---|---|---|---|---|
| Honest Hold [WH SIGNATURE] | LP1+RK4 (`1+4`) | armR / 22 / 19f (0.32s; active 0.05s; recovery 0.90s) | ADAPT | `t3_grab.json`, move_row 230, King's decoded grab attempt (35 frames @30fps) | Piecewise time-warp anchored on the measured RightHand-extension peak (source frame 19, 0.731 m): windup stretched to the 0.32s startup, peak frames held through the 0.05s active (the grip), remainder stretched to the 0.90s recovery. Output 38 frames. Class-correct by construction: the source is a throw row, and the move is a throw (`isGrab`, break LP1+RP2). No opponent motion invented — this bank animates the attacker only; victim motion stays game-side. |
| Tail-Tip Lunge [WH SIGNATURE] | f+LP1 (`f+1`) | armR / 16 / 13f (0.22s; active 0.017s; recovery 0.72s) | ADAPT | `rows.pack.json` row 111, King f+2 (forward RP2 strike, armR) | Piecewise time-warp anchored on the measured RightHand-extension peak (source frame 5 of 20, 0.845 m): windup to 0.22s, peak held 1 frame for the 0.017s active, recovery to 0.72s. Output 29 frames. Source picked for filed limb (armR) + forward motion, matching "lunging claw rake". **INPUT CONFLICT, flagged not hidden:** the input token is f+LP1 (left punch) while the filed limb is armR (right arm). Row 110 (King f+1, armL) matches the input button but contradicts the filed limb. This clip follows the filed limb + the canon file's armR; the input/limb conflict in `pantera.json` still needs an owner/moveset-lane ruling before wiring — if the ruling is armL, re-run the builder with row 110. The tail telegraph is NOT in this clip: the 22-bone bank rig has no tail joint, so the telegraph must be model-side (tail bone) or VFX, listed as a gap below. |
| Battle Itself [WH SIGNATURE] | LP1+RP2 (`1+2`) | armL / 19 / 21f (0.30s; active 0.20s; recovery 1.05s) | ADAPT | `rows.pack.json` row 220, King 1+2 (LP1+RP2, armL) | Same input, same limb, and same 0.30s startup as the signature — the closest possible base. Piecewise warp anchored on the measured LeftHand-extension peak (source frame 31 of 43, 0.677 m); the strike segment (peak..peak+9) is repeated 3× across the active+recovery window for the multi-hit flurry, then the tail of the source clip plays once. Head roar: Head pitched back up to 18° during windup, held through active, easing off in recovery. Output 46 frames. **Deliberately NOT mirrored:** an alternating-arm flurry would need a verified mirror transform; none was verified, so the repeat is same-arm. If the owner wants alternating arms, that is a separate, verified-mirror task — not silently shipped. |

## Verification (simulation only — NOT play-verified)

Builder + validator: `tools/anim/made_pantera_build.py` (re-run it to
reproduce all three clips from the bank on disk). Checks run 2026-10-24:

- Shape: all three are `wh-anim/1`, fps 30, 22 bones, `rot_xyzw` and
  `root_t` lengths equal per clip (38 / 29 / 46 frames), all quaternions
  unit-norm (max deviation 0.00002), all values finite.
- Timing: output durations 1.267s / 0.967s / 1.533s vs move totals
  1.270s / 0.957s / 1.550s (30fps rounding, ≤1 frame).
- Continuity: worst per-frame joint step in the MADE clips (100.4° /
  92.9° / 131.0°) is at or below the worst step already present in the
  source clips (140.2° grab / 111.4° row 111 / 97.1° row 220 — fast
  strikes at 30fps plus elbow flips in the decoded data). The warp
  introduced no step larger than its source's own worst step, except
  Battle Itself's repeat joints (131.0° vs source 97.1°): that step is
  the segment-repeat seam, and it is the one place this build adds
  discontinuity — flagged here, to be eye-checked on the wiring PR.
- **Not verified:** in-game playback, hit-window alignment, or how any
  of the three reads on Pantera's model. No play-verification is claimed.

## Gaps / open questions (Pantera)

1. Wiring precondition (above): `t3anims.js` `userData.source` must
   become data-driven, and `fighter.js` needs a `made` tier. No moveset
   `anim_ref` change was made in this PR, because nothing reads it.
2. Tail-Tip Lunge input-vs-limb conflict (f+LP1 vs armR) — needs a ruling.
3. Tail telegraph: no tail joint in the bank rig — model-side or VFX work.
4. Battle Itself repeat seam (131.0° step) — eye-check on wiring PR.
5. Honest Hold's T7 block in `pantera.json` cites King 1+4 damage 33 /
   startup 52f, contradicting the signature's own 22 dmg / 19f. The clip
   follows the signature's own timing (19f); the T7 block is untouched.

## Files in this PR

- `game/assets/anim/made/pantera/made_pantera_honest-hold.json` (MADE)
- `game/assets/anim/made/pantera/made_pantera_tail-tip-lunge.json` (MADE)
- `game/assets/anim/made/pantera/made_pantera_battle-itself.json` (MADE)
- `game/assets/anim/made/pantera/README-MADE.md` (label + wiring precondition)
- `tools/anim/made_pantera_build.py` (builder + validator)
- `docs/anim/MADE-PANTERA-2026-10-24.md` (this file)
- `docs/anim/MADE-PRIORITY-SPECS-2026-10-24.md` (specs for the other
  priority fighters — specs only, no clips)
