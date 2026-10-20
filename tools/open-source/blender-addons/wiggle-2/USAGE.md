# Wiggle 2 — usage notes (from the vendored source, verified on Blender 4.0.2)

Wiggle 2 (shteeve3d, v2.2.4) simulates spring physics on pose-bone
transforms. This file documents the REAL API as read from
`wiggle_2.py` in this directory and exercised by
`tools/jiggle/wiggle2_jiggle.py` on the Scarlett/Star rig. It is a
single-file addon: load the `.py` as a module and call `register()`
(or install it as a normal addon). No `__init__.py`, no package.

## Enable chain (all three levels required)

1. Scene: `scene.wiggle_enable = True`
   (3D Viewport > Animation panel > "Enable Scene" in the UI).
2. Armature: `object.wiggle_enable` — read-only in practice; it is set
   automatically by `build_list()` once any pose bone has wiggle on.
   `object.wiggle_mute` mutes the armature, `object.wiggle_freeze`
   freezes it (the bake operator sets freeze when it finishes).
3. Bone: `pose_bone.wiggle_tail = True` and/or
   `pose_bone.wiggle_head = True`. Head is unavailable on bones with
   `use_connect` (the parent's tail covers that point).

## Per-bone physics properties (tail; `_head` twins exist for head)

| Property | Default | Meaning |
|---|---|---|
| `wiggle_stiff` | 400 | Spring stiffness pulling the point back to its animated target. Large numbers allowed. Per solver iteration the step is `stiff * dt^2 / iterations`, capped at the full distance — very high values snap, they do not explode. |
| `wiggle_damp` | 1.0 | Velocity damping: velocity is multiplied by `clamp(1 - damp*dt, 0, 1)` each frame. Can exceed 1. |
| `wiggle_stretch` | 0.0 | 0..1, how much the bone may change length (0 = rigid length projection). |
| `wiggle_gravity` | 1.0 | Multiplier on `scene.gravity`. |
| `wiggle_mass` | 1.0 | Used for chain force splitting between parent/child. |
| `wiggle_chain` | True | The bone pushes back on its wiggle parent (chain reaction). |
| `wiggle_wind_ob` / `wiggle_wind` | None / 1 | Wind force-field object + multiplier. |
| `wiggle_collider_type` + `wiggle_collider` / `wiggle_collider_collection`, `wiggle_radius`, `wiggle_friction`, `wiggle_bounce`, `wiggle_sticky` | — | Mesh/collection collision for the point. |

Internal state lives in `pose_bone.wiggle` (position, velocity, matrices)
— never write it by hand.

Scene-level (`scene.wiggle`): `iterations` ("Quality", solver passes,
default 2), `loop` (physics continues across timeline loops instead of
resetting at frame start), `preroll` (frames of settle run before a
bake), `bake_overwrite`, `bake_nla`.

## Operators

- `bpy.ops.wiggle.reset()` — reset physics state to rest.
- `bpy.ops.wiggle.select()` — select all wiggle bones (POSE mode).
- `bpy.ops.wiggle.copy()` — copy active bone's settings to selected.
- `bpy.ops.wiggle.bake()` — the bake. Runs reset + preroll, then calls
  `bpy.ops.nla.bake(only_selected=True, visual_keying=True,
  use_current_action=scene.wiggle.bake_overwrite, bake_types={'POSE'})`.
  With overwrite on, baked keys merge into the current action (other
  bones' curves untouched). With overwrite off, a new action is created
  (and the old one can be pushed to an NLA track with `bake_nla`).
  Sets `object.wiggle_freeze = True` afterwards. Requires the armature
  active in POSE mode (its internal `wiggle.select` poll demands it).

## How the sim runs

`frame_change_pre` clears every wiggle bone's basis transform
(location 0, rotation identity, scale 1) — **any keyframes on a wiggle
bone are ignored while wiggle is live**; the bone's animated target is
derived from its parent chain only. `frame_change_post` then integrates:
`move()` (velocity + gravity + wind, collision) and `iterations` passes
of `constrain()` (spring toward target + stretch projection), and writes
the result back into `bone.matrix`. Handlers early-out while rendering
(`scene.wiggle.is_rendering`), so **a live wiggle scene renders WITHOUT
jiggle — always bake before rendering**.

## Gotchas (all hit for real on the Scarlett rig, 2026-10-20)

1. **Multi-select property stamping.** Every property's update callback
   (`update_prop`) copies the new value to ALL selected pose bones. In
   the UI that is a feature (multi-edit); in a script it silently stamps
   `wiggle_head` + `wiggle_tail` + the last-set params onto every
   selected bone. Configure bones with exactly ONE bone selected.
2. **Tiny bones + tail wiggle = singular matrix crash.** The solver is
   world-space: its per-frame step at 24 fps / gravity 1.0 is ~0.017
   units. Scarlett's `Butt_*` bones are 0.0026 units long while their
   parent moves ~0.005/frame — the tail point crosses the head,
   `update_matrix()` computes a zero Y scale, and the next
   `relative_matrix()` raises
   `ValueError: Matrix.invert(ed): matrix does not have an inverse`
   (wiggle_2.py lines 201/283/448), poisoning the bone's stored matrix
   with NaN for the rest of the session. Reproduced with gravity 0 and
   stiffness 400–8000: it is a bone-length vs step-size degeneracy, not
   tuning. **Use HEAD wiggle for such bones** — it simulates the head
   point (translation of the whole bone), the Y-scale is then 1 by
   construction, and children still inherit the motion.
3. **Head stiffness ceiling.** With head wiggle, an over-stiff spring
   can jump the head past the tail target, collapsing the same Y-scale.
   Keep `stiff * dt^2 / iterations` below ~0.5 (at 24 fps, iterations
   4: stiffness ≲ 1150). Tail springs are step-capped and far more
   forgiving.
4. **Handler exceptions abort the whole frame.** One crashing bone
   kills `wiggle_post` mid-loop, so unrelated bones lose that frame of
   physics. A single bad bone corrupts the whole bake — check the
   console for tracebacks and NaN-check the baked curves.
5. **Bake freezes the armature.** After `wiggle.bake`, either keep
   `wiggle_freeze=True` / disable `scene.wiggle_enable` before rendering,
   or the pre-handler will fight the baked keys.

## Production parameters (Scarlett/Star, CMU lambada, 24 fps)

- `DEF-breast.*` chains: TAIL, stiff 1400·0.88^level, damp 1.1,
  stretch 0.02, gravity 0.6, chain on.
- `Butt_*` chains: HEAD, stiff 1100·0.85^level, damp 1.3,
  stretch 0.02, gravity 0.6, chain on.
- Scene: iterations 4, loop on, preroll 24.
Measured results and the verlet-baseline comparison:
`tools/jiggle/proof/scarlett-wiggle2-metrics.json`.
Driver: `tools/jiggle/wiggle2_jiggle.py`.
