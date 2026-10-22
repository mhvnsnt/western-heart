# Western Heart — Godot Vertical Slice (2026-10-22)

First Godot build of Western Heart, proving the locked engine pipeline
end-to-end: **Godot 4.7.2 (pinned), Mobile (Vulkan) renderer**, Compatibility
fallback. Engine lock: owner-delegated pick 2026-10-21; sibling session's
decision doc lives at `docs/godot/ENGINE-DECISION.md`. This project sits
alongside `lab/game` (the Godot 4.3 Tekken-3 lab slice) and `godot/prototype/`
— nothing here modifies them.

## What the slice does

- Loads **two real roster GLBs** through Godot's native glTF import:
  - `assets/models/pantera.glb` — Pantera (HOUSE-49 template donor, 49
    joints, textured, carries embedded Idle/Walk/Run clips).
  - `assets/models/star-house49.glb` — Star, re-templated MINI (53 joints:
    HOUSE-49 + her 4 extra jiggle bones; ships textureless — her textures
    live in other attire files, restoring them is another lane's work).
- Plays **real decoded Tekken 3 bank clips** (`assets/anim/`, wh-anim/1 JSON
  from the owner's disc teardown) retargeted at runtime by
  `scripts/bank_clip_loader.gd`:
  - Pantera's attack = King bank clip `t3_light` (move row 35) — a
    crouch-leap strike; his Idle/Walk are the GLB's own embedded clips.
  - Star has no embedded clips, so her Idle and Walk are bank clips too
    (`t3_stance`, `t3_walk_fwd`), retargeted onto her rig by the same solver.
- **Deterministic sim core** (`sim/fight_sim.gd`): a RefCounted fixed-step
  (60 Hz) simulation — input bitmask in, positions/states out. No Node, no
  engine physics, no wall clock, no RNG driving fight state. Presentation
  (`scripts/fighter_view.gd`, `scripts/main.gd`) only mirrors the sim.
- **Touch controls stub**: on-screen ◀ ▶ ATK buttons feed the same input
  bits as the keyboard (A/D/arrows + J). Buttons move P1 and trigger the
  attack clip through the sim, never around it.

## Retargeting — what actually worked (probe-verified)

Sharing Animation resources between rigs verbatim FAILS here: same bone
names, different bone frames — the receiving fighter ended up lying flat.
`BankClipLoader` instead transfers **world-space deltas** (FK over the
canonical wh-anim skeleton vs FK over the target rig's own rest pose):

    posed_local = rest_local * (rest_world^-1 * (D * rest_world))

where `D` is the source bone's world rotation delta for the frame, first
conjugated into the target rig's skeleton space. The space conversion is
**per-rig and auto-detected from the rest pose** (`detect_conv`): Pantera's
skeleton space is Z-up (rotX+90 conjugation); Star's is Y-up but turned
180° about Y (rotY180 conjugation — a proper rotation; the Z-mirror variant
was probe-rejected: it threw her guard overhead). Quaternion sign
continuity is enforced along every built track (a flipped key tumbles the
body mid-clip). Looping stance/walk clips skip hip translation (the web
runtime does the same; the stance slot's root track contains a get-up
crouch that must not dip the fighter); attack clips keep root motion —
Pantera's leap lives in it.

Fighter state names in the HUD (`walk/walk_fwd/attack/idle`) come from the
sim, and the proof run below is driven through the same input bits the
touch buttons set.

## Proof

Headless proof mode (scripted inputs through the sim, frames captured from
the running slice):

    godot --path . --resolution 1280x720 -- --proof --proof-out=<dir>

captures `slice_walk.png` (P1 walking, P2 in bank stance) and
`slice_attack.png` (P1 mid bank-clip leap strike, P2 walking). Both frames
were viewed by the building agent: Pantera textured and upright in profile;
Star upright in a guard stance with hands at waist height, body intact.

Disclosure: this VM has no Vulkan device, so headless captures run on
Godot's automatic OpenGL (Compatibility) fallback. The project default is
Mobile/Vulkan; on-device validation is still owed (gap list in the
checkpoint `agent-ops/checkpoints/godot-slice-20261021.json`).

## Android export

Preset `Android` in `export_presets.cfg` (arm64-v8a, debug signing, no
Gradle build). Headless:

    godot --headless --path . --export-debug "Android" exports/western-heart-slice-debug.apk

Requires Godot 4.7.2 export templates + an Android SDK (platform 35,
build-tools 35.0.0) configured in the editor settings. Export status and
any blocker are recorded in the checkpoint JSON above.
