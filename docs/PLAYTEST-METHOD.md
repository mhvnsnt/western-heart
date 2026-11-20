# Western Heart Lab — Playtest Method (repeatable)

Who: anyone (owner, Muse, Grok Bot, Repo Co Dev). Goal: play the Lab 1v1 with **scripted, frame-exact inputs**, measure frame data, capture proof frames + video, and compare to Tekken.

## 0. Setup (low-disk box)
```sh
# sparse/shallow clone; skips blobs > 2 MB (big teardown assets) — enough to run the Lab
git clone --depth 1 --filter=blob:limit=2m https://github.com/mhvnsnt/western-heart.git wh-qa
cd wh-qa
godot --version            # needs 4.3.x (box has /usr/local/bin/godot 4.3.stable)
# first run only: import assets (creates lab/game/.godot, ~1-2 min)
godot --headless --path lab/game --import
```
If Godot isn't installed: download `Godot_v4.3-stable_linux.x86_64.zip` from github.com/godotengine/godot/releases, unzip, put it on PATH as `godot`.

## 1. Numbers only (headless, ~30 s)
```sh
godot --headless --path lab/game -s res://tests/qa_playtest.gd | grep '^QA|'
```
Each `QA|<scenario>|...` line gives:
- `presses` — frames where P1 pressed (scenario-local frame numbers, 60 fps)
- `first_active_frames` — frames P1's move was in its active phase (first value = hit frame; extra values are hitstop re-entries)
- `transitions` — `[frame, "P1state/P2state"]` every time either state changes. **Frame advantage = (frame P2 returns to idle) − (frame P1 returns to idle).**
- `p1_dx` walk distance (m), `p2_hp`, `p2_x` (pushback = change from start x)
Full per-frame log: `build/qa/qa_log.csv` (state, move frame, phase, x, hitstop, stun, hp, camera).

## 2. With rendering: proof frames + video
```sh
xvfb-run -a -s "-screen 0 1280x720x24" godot --path lab/game --rendering-driver opengl3 \
  -s res://tests/qa_playtest.gd -- --capture
# PNG every 6th frame + every active frame -> build/qa/NN_<scenario>_fNNN.png
ffmpeg -y -framerate 12 -pattern_type glob -i 'build/qa/*.png' -vf scale=640:-2 \
  -c:v libx264 -pix_fmt yuv420p build/qa/qa_playtest.mp4
```
Real-time match video (CPU vs CPU) still works too:
`xvfb-run godot --path lab/game --rendering-driver opengl3 --write-movie out.avi --fixed-fps 60 -- --autoplay --quit-after-match --touch`

## 3. Scripting new inputs
Edit `scenarios` in `lab/game/tests/qa_playtest.gd`:
```gdscript
_s("name", start_distance_m, "stand"|"block", length_frames, inputs, p2_hp=170)
# inputs helpers: _tap("p1_light", frame)  _hold("p1_right", from, to)
#                 _mash("p1_light", first, count, every_n)  _merge([a, b])
```
Actions: `p1_left p1_right p1_light p1_medium p1_heavy p1_grab p1_block`. They go through the real InputMap (same path as keyboard/pad/touch), injected before `main._physics_process` each frame. P2 is replaced by a `Dummy` (stands or holds block). Results land the same frame, so input delay is measurable (currently 0 frames).

## 4. Comparing to Tekken
Use public frame data (wavu.wiki for T7/T8, rbnorway/TZ archives for T5/T6). Convert: Tekken "i10" = hit on frame 10 after the press frame. Our harness: press on f1, hit on f`N` → equivalent `i(N-1)`. Record results in `docs/qa/<date>/` and the table in `docs/QA-FINDINGS.md`.

## 5. Proof
Copy the key PNGs as JPG (`ffmpeg -i x.png -q:v 4 x.jpg`), the mp4 and csv into `docs/qa/<date>/`. Never commit `build/`.
