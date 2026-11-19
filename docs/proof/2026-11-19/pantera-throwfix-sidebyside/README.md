# Pantera 2+4 — old-vs-fixed side-by-side (2026-11-19)

## The video

`pantera-2plus4-old-vs-fixed-20261119.mp4` — 1600x450, 44 frames @ 20 fps,
2.2 s, 644 KB. Left panel OLD, right panel NEW, labels burned in.
`pantera-2plus4-old-vs-fixed-contact-800w.png` — contact sheet, 6 paired
frames (frames 1, 11, 22, 30, 36, 44).

## What the two panels are

- **OLD (left) — the Nov 12 build.** Frames from the original video
  `pantera-2plus4-throw-20261118.mp4`, rendered from commit
  `43d29bf6bcc6919aff35c025f01e0a7e9aea69c5` (2026-11-17, merge PR #863;
  zero Pantera runtime changes Nov 12-17). The original is 960x720 with a
  closer camera; frames were center-cropped to 16:9 (960x540) and scaled to
  800x450 so the panel geometry matches NEW with no distortion.
- **NEW (right) — fixed capture on merged main
  `38a6e4062c4720f590a8c94dca180c15968c14ee`** (merge PR #1768; includes the
  full A+B+D throw fix: #1764 victim clip, #1765 proof, #1766 clinch yaw +
  hips floor, #1767 proof, #1771 knee-pole). Captured by Lane R's clean
  re-proof on the same harness as the prior lanes: opponent Demonio,
  `__reset(1.0)`, free camera, 800x450, hand-stepped 60 Hz sim, 20 fps
  grabs, served from a full tree at 38a6e40 with GitHub-raw fallback.
  Log: `video-pantera-log-vid24-38a6e40.json` in this directory.

## Time alignment

Panels are paired by frame index: same throw (2+4), same start frame
(throw connect), same 20 fps, 44 frames each, no offset. NEW logged 132
sim frames / 44 shots; OLD is the original 44-frame video. Framing is
NOT pixel-matched (OLD camera is closer/tighter than NEW) — time sync is
frame-exact, framing is not. A matched-framing OLD re-capture at 43d29bf
is possible later (OLD serve tree kept in the Lane S workdir); it is not
needed for the time comparison.

## Numbers (NEW panel, from the capture log)

- Throw states: p1 attack, throwing, throwExec, idle; p2 idle, thrown,
  thrownExec, knockdown — all PASS.
- Victim plays a clip: **84/84 thrown frames**, names
  `t3_jin_stance@demonio-a1`, `t3_jin_hit@demonio-a1`,
  `t3_jin_launch@demonio-a1` — PASS, majority coverage PASS.
- Damage: hp 180 -> 155.3 (**24.7**).
- Gap at connect: **1.45 m** on every frame 0-11 (same as Lane A's run).

## Own-eyes verdict (Lane S, viewed the paired frames)

- The panels ARE time-aligned: same throw beats at the same frames
  throughout (clinch ~frame 6, hit burst ~frame 16, mid-throw ~frame 22,
  floor ~frame 30, both standing again ~frame 36+).
- **Pantera does the SAME sacrifice roll in both panels** — horizontal /
  flipped mid-air at frame 22, prone on the floor at frame 30, back on his
  feet by frame 36. That is correct Tekken 3 source motion (Lane M
  verdict: the grab clip's forward roll, pitch 109.8 deg, then prone
  0.149 m — NOT an inverted pair). The AFTER panel does NOT show Pantera
  upright through the throw, and upright would be wrong: the source
  motion takes him down.
- **The visible fix is the victim.** OLD: Demonio stands frozen on his
  feet through the whole throw. NEW: Demonio reacts (leaning back from
  frame 11), is airborne upside down at frame 22, and is down on the
  floor next to Pantera at frame 30. He plays a real clip on 84/84 thrown
  frames instead of standing frozen.

## What this video does NOT prove (read before citing it)

- It does NOT prove the paired throw binds live. The clips the victim
  plays are the GENERIC reactions (`t3_jin_hit` / `t3_jin_launch`), not
  the paired `t3_react_3051`; the thrower plays `t3_king_row128` ->
  `t3_king_grab`, not the paired `t3_react_2797`. The pair never binds
  because the live connect gap (1.45 m) is over the file's max range
  (1.2748 m) — the distance gate (Lane G: needs the owner's call, no PR
  filed). What this video proves is narrower and real: on merged main the
  victim is animated and visibly thrown instead of frozen.
- It does NOT show Pantera staying upright — see the verdict above; the
  roll is the source motion.

## Supersedes

Lane D's side-by-side (`pantera-throwfix-kneepole/
pantera-kneepole-side-by-side-2plus4.mp4`, PR #1771) showed the legacy
path in BOTH panels (victim 0/84 thrown frames with a clip in both
captures) — effectively before-vs-before. Its frame 30 shows Pantera
prone in both panels because both panels ran the same unbound legacy
throw, not because the panels were time-misaligned. This rebuild
replaces it as the old-vs-fixed record.

## Rebuild note

If a distance-gate or mid-throw fix lands on main after 38a6e40, this
side-by-side is on the pre-fix main and needs a rebuild on the newer
commit. Lane M filed no fix (correct source motion); Lane G filed no fix
(owner's call pending).
