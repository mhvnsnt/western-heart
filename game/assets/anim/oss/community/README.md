# Community mocap bank — game/assets/anim/oss/community/

Retarget-ready GENERIC BASES for canon/WH-original moves, from community
motion-capture libraries. A base is NOT the finished canon animation:
canon flavour (roar, acid, satchel, stance geometry) is added by the
animation lane. No wh: anim ref is replaced by anything in this directory.

## Contents

- 9 CMU FBX clips (see wired-clips.json for the 55-move mapping):
  144_05.fbx, 144_09.fbx, 144_13.fbx, 144_20.fbx, 144_28.fbx, 86_01.fbx,
  86_06.fbx, 88_06.fbx, 90_05.fbx.
- wired-clips.json: the 55 wired generic bases, keyed by move_id, with
  repo clip path, moveset file, anim_ref (unchanged), limb, damage,
  canon startup frames, alternate base, and status. Every entry's
  retarget_status is pending-gpu-retarget; clip_trim, hit_frame, and
  jumping_ca2 are UNMAPPED until the GPU run fills them.
- Moveset wiring: each moveset file gains additive community_base +
  community_base_status fields on every entry (moves + canon_moves)
  carrying a wired anim_ref. No other field is touched.

## What is NOT here (and why)

- No retargeted .npz files: the GPU retarget has not run yet (parent
  browser job — Kaggle T4 x2 first, Colab T4 backup). See the GPU run
  package in the workspace (community-mocap-gpu-package/).
- No Mixamo clips: Mixamo is login-gated and nothing was downloaded; no
  Mixamo soldier goes in the game (creation-suite law).
- No Rokoko clips: form-gated, no clip names verified, nothing downloaded.
- No clips for the 105 no-base moves: no verified community clip fits
  (two-person grapples, projectiles/energy, non-human limbs/props/weapons,
  canon stances, empty source descriptions). Those 105 are tracked
  separately in docs/decisions/2026-10-24-community-mocap-105-no-base-followup.md
  for BUILD / T7 / T3 adaptation — NOT dropped.

## Classification authority (CA-2)

Jumping is hip/pelvis Y rise+fall ONLY, measured by the GPU CA-2 pass —
never from a file name or metadata token. Clips whose descriptions contain
jump tokens (90_05, 88_06, 86_01) stay jumping UNMAPPED until that pass.

## Licences (animation lane: re-confirm at copy time)

- CMU: free for all uses; may be included in commercially-sold products;
  may NOT be resold directly even in converted form; published work should
  cite mocap.cs.cmu.edu / NSF EIA-0196217.
- Bandai Namco alternates (named in wired-clips.json, not stored here):
  CC BY-NC 4.0 — reference/prototyping only for a commercial game unless
  cleared or re-authored. Bandai file names do NOT label left/right.
