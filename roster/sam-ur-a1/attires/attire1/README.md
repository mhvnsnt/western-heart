# SAM-UR-A1 Attire 1 — Tripo Default + ROCKET FIST mechanic

## Model

- **Source:** https://studio.tripo3d.ai/3d-model/7c94ba99-d5ed-4391-bb79-d6cd6eeb51ac ("sci-fi mecha 3d model" by dg88will)
- **Pulled:** 2026-10-19 via `tools/tripo-pull/tripo-pull.py` (public API, no sign-in)
- **File:** `model.glb` (22,786,736 bytes, meshopt-compressed, 1 mesh, 3 textures)
- **Character:** Dark sci-fi mecha, bronze/gold armor accents, tentacle-cable shoulder rigs, armored greaves.
- **Canon base:** Gun Jack (per `roster/sam-ur-a1/kitbash_v1.json`).

## The floating forearms — ROCKET FIST (owner 2026-10-19, verbatim)

> "Has extra floating arms like DXMMII tripo model had, but this one's is just the forearms down, can be used to blast his fist off like a rocket like how gun Jack does in his movesets In Tekken games."

The Tripo mesh includes **detached forearm/fist units** floating at the shoulders —
the same class of hardware as DXMMII's gyro arms. This is a FEATURE, not a
modeling error. In-game it becomes the **ROCKET FIST** special:

- **Input:** `qcf+1+2` (Tekken notation) — wired in `game/assets/movesets/sam-ur-a1.json`.
- **Effect:** heavy projectile-style fist blast, Gun Jack style. Damage 26, long
  startup (0.45s), big knockback.
- **Current status:** moveset data ships with a placeholder `anim_ref`
  (`"tbd:sam-ur-a1:rocket-fist"`). The real animation needs the detached-fist
  rig: see below.

## Rigging the rocket fist (for the rig lane)

The multi-arm research applies directly (`tools/limb-system/dxmmii/`,
PR #302 — the Child Of keyframing fix spec):

1. **Separate the fist units** into their own objects (they're already
   disconnected geometry in the Tripo mesh — no cutting needed, just split
   by loose parts).
2. **Child Of constraints** with keyframed Influence on empty "socket" targets
   at the forearm stump (PR #302's fix: keyframe the Influence, not just the
   constraint).
3. **States:** DOCKED (fist at wrist) → LAUNCH (fist flies, influence 0, driven
   by a projectile path) → RETURN (influence back to 1 at the socket).
4. The DXMMII 5-state machine (`ATTACHED → DETACHED → GYRO → REATTACHED`)
   in `tools/limb-system/dxmmii/BUILD.md` is the reference implementation.

## Name status

⚠️ **Owner calls this fighter "SAM-UR-A1"** — wired under that id. If the
canon name differs, rename the folder/id (do not invent canon).
