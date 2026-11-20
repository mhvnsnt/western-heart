# Doc Frank bind fix — proof (2026-10-21)

Owner's complaint: Doc Frank's head faced his opponent but his body was
backwards, and the game kept showing the Dr. Bosconovitch model instead of
his own Tripo GLBs in the Bosconovitch stance. The fix normalizes the bind
locals inside Doc Frank's own GLBs only (all identity — see
`roster/doc-frank/bind-fix/README.md` for the root cause and method).
His attires were already wired on main (fighter-completeness lane):
`attires.js` lists 9 Doc Frank models under the `docfrank` entry and the
roster enemy path resolves to `doc-frank-machine-shop`, the player default
to `doc-frank` — verified through the game's own modules.

## The renders (viewed by the agent before shipping)

Both are FRONT renders of Doc Frank's OWN Tripo GLBs posed on the
bosconovitch animation bank (stance clip at 40%), posed by running the
game's real `game/js/t3anims.js` (`loadT3Clips` -> `retargetT3Clips` ->
`createT3Actions`, i.e. the full stage-1 + stage-2 path the game plays),
baking the posed skeleton into the mesh, and rendering in Blender. They
are NOT the Bosconovitch model.

- `docfrank-machineshop-bosco-stance-front.png` — the machine-shop GLB
  (the model the game loads for Doc Frank as opponent): upright in
  Bosconovitch's hunched drunken stance, face/tie/coat forward, hands in
  guard, body and head facing the same direction.
- `docfrank-base-bosco-stance-front.png` — the base GLB (player default,
  white lab coat): same stance, same verdict.

Before the fix, the same full-path evaluation folded him at the waist
(shoulders -164.9 deg). After: shoulders +1.7 deg, head +10.8 deg, pelvis
+5.9 deg, 0 NaN bones, rest frame all-zero — stage 2 is now a no-op and
the played pose is exactly the stage-1 solve.

## Cross-checks

- Facing-lane sim (the instrument that matched the live game to <1 deg on
  the original file): original GLB stage 2 = 108.6 / 98.1 deg off-source;
  fixed GLB stage 1 == stage 2 == 0.8 / 6.9 deg (bosconovitch bank).
- Hood attire GLB (attire3/base, the meshopt one) through the same
  game-code path: shoulders +1.5 deg, head +10.8 deg, pelvis +5.9 deg,
  0 NaN. Its Blender render was OOM-killed twice on this saturated box
  (rc=137); the numeric pose proof stands, the render is owed when the
  box quiets.
- Bind-pose skinning invariance for every fixed GLB: max vertex deviation
  1.21e-07 (attire3 bone-matrix invariance 2.98e-08); joint world
  positions unchanged.

## Honest limits

- 6 of his attire GLBs are unrigged Tripo statics (no skin/binds):
  attire1/post-transform, attire2 base + transformed, attire3/transformed,
  attire4 base + transformed. They are wired and selectable, but they
  cannot animate until they are rigged (separate lane's work, not this fix).
- The main `docfrank` entry's transform target is always `doc-frank-big`
  regardless of the selected attire; per-attire transforms live on the
  separate single-attire roster entries. Pre-existing wiring, not changed
  here.
- Full-game browser playtest frames were environment-blocked all day
  (Chromium renderers die under multi-lane load on this box); the pose
  proof runs the game's own retarget modules directly, the same approach
  the personality-pass lane used for its playtest proof.
