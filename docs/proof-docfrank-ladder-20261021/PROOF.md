# Doc Frank ladder reorder — proof (2026-10-21)

Owner correction 2026-10-21 ~19:08 CDT: Doc Frank's forefront attires and
defaults were the Dr. Bosconovitch base model and its machine-shop reskin.
His Tripo GLB attires 1–4 belong at the forefront (like every character);
the Tekken base attires and reskins/retextures ladder back behind them.

## What changed

- `game/js/assets.js`: new key `doc-frank-a1` →
  `roster/doc-frank/attires/attire1/pre-transform/model.glb` (Attire 1's
  own pre-form GLB — it previously had NO MODEL_URLS key at all).
- `game/js/attires.js`: `ATTIRE_VARIANTS['docfrank']` reordered — Attire
  1 pair, Attire 2 pair, Attire 3 pair, Attire 4 pair (all Tripo),
  then `doc-frank` (Bosconovitch base) and `doc-frank-machine-shop`
  (reskin) at the back. Labels now carry provenance. First entry =
  default, so the player default is Attire 1.
- `game/js/roster-full.js`: main `docfrank` entry model
  `doc-frank-machine-shop` → `doc-frank-a1` (enemy/preview path default).
  Transform target unchanged: `doc-frank-big` (Tripo).
- `game/tests/model-key-guard.test.mjs`: `docfrank` ownership +=
  `doc-frank-a1`.
- `roster/doc-frank/ATTIRE-SLOTS.md`: ladder rewritten with provenance
  labeled per slot (Tripo / Tekken base / reskin).
- `roster/doc-frank/attires/attire1/pre-transform/model.glb`: bone-name
  normalization (see below). Nothing deleted anywhere; every previously
  reachable variant is still reachable.

## The render (viewed by the agent before shipping)

`docfrank-a1-bosco-stance-front.png` — FRONT render of the NEW DEFAULT
model (`doc-frank-a1`, Attire 1 pre-form GLB) posed on the bosconovitch
animation bank (stance clip at 40%) through the game's real
`game/js/t3anims.js` (`loadT3Clips` → `retargetT3Clips` →
`createT3Actions`), baked and rendered in Blender (Cycles CPU; EEVEE's
GL context is broken on this box tonight). Upright, facing the camera,
head and body the same direction, arms in the drunken guard — not
folded, not backwards, not a T-pose.

Pose numbers from the same run (`pose-a1-stance.json`): rest angles
0/0/0; posed shoulders +20.8°, head +28.7°, pelvis −2.1°; **0 NaN
bones, 0 dropped tracks**; the bank loaded 669 real T3 clips.

## Bone-name normalization (why the GLB changed)

`attire1/pre-transform/model.glb` carried raw Tripo bone names
(`root hips`, `spine lower`, `arm right shoulder 1`, …). The game's
retarget (`canonBoneName` in `game/js/t3anims.js`) only recognizes
canonical/Mixamo/Biped/LR names, so `analyzeRig` returned null for this
file — it could never have animated as the default. Its skeleton is the
same 178-joint template as the base model: verified index-by-index
(204 nodes, 178 joints, 0 parent/children structural mismatches, same
IBM accessor). `roster/doc-frank/bind-fix/rename_bones.py` renamed the
51 descriptive joint-node names to the canonical names of that verified
twin. The BIN chunk is **byte-identical** (sha256-checked against
origin/main) — geometry, skin weights, textures untouched; only JSON
node-name strings changed. After the rename the full game path above
poses it (669 clips, 0 NaN).

## Probe

`probe-output.txt` — imports the real `attires.js`, reads `assets.js` /
`roster-full.js`: ladder order printed, player default = `doc-frank-a1`,
roster model = `doc-frank-a1`, transform target = `doc-frank-big`, all
10 ladder keys resolve in MODEL_URLS. **ALL PROBE CHECKS PASS.**
All 10 MODEL_URLS target files verified present on origin/main via
`git cat-file -e`.

Tests: `fighter-completeness.test.mjs` 3/4 pass (transformation targets
resolve ✓; attire ladders resolve ✓; burger form keys ✓). The 4th
(moveset-file existence across ~20 fighters) fails only in this sparse
worktree where those files are not checked out — environmental, not
this change; same for the guard test's file-existence assertions.
Key-resolution assertions for docfrank pass (no docfrank entries in the
failure list). CI runs both on a full checkout.

## Forefront slots that are unrigged statics (report, not fixed here)

GLB skin scan (skins/joints): rigged = Attire 1 pre-form (178), Attire 3
base (73), base (178), machine-shop (178). **Statics** (skins=0; wired
and selectable, cannot animate until a rigging lane does them): Attire 1
transformed, Attire 2 base + transformed, Attire 3 transformed,
Attire 4 base + transformed. Per the lane order, these were NOT rigged
here.
