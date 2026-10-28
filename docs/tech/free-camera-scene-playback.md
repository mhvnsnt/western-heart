# Free camera during game scene playback — design + audit (2026-10-24)

User directive 2026-10-24 21:35 CDT: during scenes the user can move the
camera himself — orbit, pan, zoom, on phone (touch orbit, pinch zoom,
two-finger pan), plus part-focus and preset views. Free-camera toggle:
take over anytime, return to authored on demand, authored camera NEVER
overwritten. Extends the closet manual-control spec
(`~/workspace/ep1-farm/closet/CLOSET_MANUAL_CONTROL_SPEC.md` §6) to scene
playback. Game-first scope: this document covers GAME scene playback
only. Show-only Ep 1 production is Claude's lane and is not built here.

## 1. Camera paths found on main (2026-10-24, main `32f817f`)

Checked via the GitHub API tree of main (58,250 blobs), not from memory:

| Path on main | What it actually is | Free-camera status |
|---|---|---|
| `packages/creation-suite/ui2/viewer.js` | Closet / creation-suite viewer. Pointer drag = yaw/pitch orbit, wheel = zoom (`_bindPointer`, lines ~110-122). One pointer only; no pinch, no two-finger pan, no part-focus, no presets. | CLOSET LANE — do NOT duplicate or clobber. This PR does not edit it. Overlap: part-focus formula only (bbox centre, distance = size x 2.5), reused, not copied code. |
| `game/js/scene.js` — `Arena.update()` | Authored FIGHT camera, procedural, every frame: tracks both fighters' midpoint/span, portrait-aware FOV fit. Overwrites `camera.position` + `lookAt` unconditionally. | GATED by this PR: `freeCameraActive` guard + `setFreeCamera()`. See §2. |
| `game/js/camdirector.js` — `WHCamDirector` | Cutscene shot-list camera (`playCutscene`, `setLookAt` transitions) + `photoMode()` orbit rig, via vendored `game/vendor/camera-controls/`. `takeOver()` saves a pose snapshot; `release()` restores that SNAPSHOT, not the live authored view. No touch input, no part-focus, no presets, no live-during-playback free mode. Loaded lazily by `game/js/integration.js`, updated every integration frame. | NOT gated in this PR — exact blocker in §3. |
| `game/js/photomode.js` — `PhotoMode` | DOA-style photo mode, installed from `game/js/main.js` (P/F9). PAUSES the game (`game.pause(true)`), mouse drag orbit / wheel zoom / right-drag/WASD pan only — no touch pinch/two-finger, no part-focus, no presets. | NOT the free camera. Deliberately NOT reused: it pauses, which the directive forbids for scene playback. Mutual exclusion only (free camera refuses while photo mode is active). |
| `game/js/stage-intros.js` | Stage-intro sweeps: keyframed pos/look/fov paths per land, ~4.2 s, skippable on any input, then hands over to the fight camera. | NOT gated in this PR — exact blocker in §3. |
| `game/js/transform-cinematic.js` | Transformation cinematic: phase timeline of aura/shake/flash, no camera path of its own (camera stays on the fight camera). | No gate needed: it inherits the fight-camera gate. |
| `game/js/menus.js` — `playStoryBeats()` + `game/js/episodes.js` | Story playback is TEXT beats over a portrait card (`#wh-story`, tap to advance). There is NO 3D scene-playback camera path for story mode on main — this was checked, not assumed. | NO free-camera target exists here. Do not invent one. If a 3D story scene lands later, it must expose a camera for `FreeCamera` to gate, the same way `Arena` does. |

## 2. What this PR adds

- NEW `game/js/free-camera.js` — `FreeCamera` + `installFreeCamera(game)`:
  one-finger orbit, pinch zoom, two-finger pan (Pointer Events, so mouse
  and touch share one path), wheel fallback, presets FRONT / SIDE / BACK /
  TOP / WIDE, part-focus via bounding box (target = centre, distance =
  bbox size x 2.5, the closet-spec formula), FOCUS P1 / FOCUS P2,
  FULL BODY, SAVE TAKE, BACK TO AUTHORED. Every button is >= 44 px.
  Entry is a button only — no keyboard hijack, so it cannot collide
  with Photo Mode (P/F9) or fight inputs.
- EDIT `game/js/scene.js` (surgical, 2 spots): `freeCameraActive`
  flag + `setFreeCamera()` in the constructor area, and an early return
  in `Arena.update()` after `stage.update()` when the flag is set.
  Stage animation keeps running; only the camera write is skipped.
- EDIT `game/js/main.js` (surgical, 1 spot): lazy `import('./free-camera.js')`
  next to the existing lazy Photo Mode import, with a catch that logs
  and never blocks the fight.

Why the authored camera is safe: it is procedural, not a stored pose.
Nothing is saved at takeover and nothing is restored at return — the
next `Arena.update()` recomputes the authored view from the live
fighter positions and its own smoothing eases the camera back. A free
move therefore cannot overwrite authored data, because there is no
authored data object to overwrite. `saveTake()` returns a new named,
versioned object and fires `wh:free-camera-take`; it writes nothing
into `stage-intros.js`, `camdirector.js`, or any authored path.

## 3. What is NOT done in this PR (exact blockers, not silent gaps)

1. **Cutscene shot lists (`camdirector.js`)**: `WHCamDirector.update()`
   drives `camera-controls` transitions and its queue timer. Gating it
   needs a decision the owner has not made: does the shot list keep
   advancing underneath the free view (return to the CURRENT shot) or
   pause its transition (return to the SAME shot)? The closet spec §6
   says "authored keeps playing underneath", which argues for advancing
   underneath, but `camera-controls` applies transitions in
   `controls.update()`, so advancing-underneath needs the queue to
   advance without applying — a change to `camdirector.js` that this
   PR does not make, to avoid silently changing cutscene timing.
2. **Stage intros (`stage-intros.js`)**: a 4.2 s skippable sweep. Free
   camera during it would need the intro player to stop writing the
   camera while free is active and resume or skip on return. Same
   decision as (1), plus the intro is so short that the owner may
   prefer free camera to simply be unavailable until the sweep ends.
   Follow-up, not claimed.
3. **Story beats**: no 3D camera path exists (see §1). Nothing to gate.
4. **Photo Mode interplay**: free camera refuses while Photo Mode is
   active; Photo Mode itself is not patched, so pressing P/F9 while
   free is active will still pause into Photo Mode. The UI copy says
   to exit free camera first. Patching `PhotoMode.enter()` to refuse
   while free is active is a one-line follow-up in `photomode.js`.

## 4. Play-verification steps (parent browser delegation — NOT run here)

Phone portrait, live build, after merge + deploy (deploy queue: after
the popup deploy, PR #1076 vehicle — do not jump it):

1. Open the game on phone portrait, start any fight.
2. Tap FREE CAMERA (top-right, >= 44 px). Fight must keep playing —
   fighters keep moving, health/timer keep running, no pause overlay.
3. One finger drag: view orbits. Pinch: view zooms. Two-finger drag:
   view pans. Each must work without the fight pausing.
4. Tap FOCUS P1, then FOCUS P2: camera frames that fighter alone.
   Tap FULL BODY: whole fight returns to frame.
5. Tap FRONT, SIDE, BACK, TOP, WIDE in turn: each preset must land.
6. Tap SAVE TAKE: status line names the new take; authored camera
   must be unchanged (no jump, no saved-over intro/fight framing).
7. Tap BACK TO AUTHORED: camera eases back to the live fight camera
   (tracking both fighters), NOT to a frozen takeover snapshot.
8. Repeat steps 2-7 in landscape. Report any step that fails exactly;
   do not mark the item verified on a partial pass.
