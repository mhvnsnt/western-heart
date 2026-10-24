# T-Pose Render Sweep — "The Rest" (owner order 2026-10-17)

Owner's words: *"not ones that we've done already, not characters that we already
made models for, not characters that we already seen in T pose — the rest of them."*

Source of truth for "already done": the `tpose-all-fighters` branch,
`docs/tpose-refs/<character>/p1_front.png` (16 characters, own-eyes verified).

## EXCLUSION LIST — already T-posed (do NOT re-render)

| # | dir | donor / note |
|---|---|---|
| 1 | awa-pop | Nina donor |
| 2 | doc-frank | Dr. Bosconovitch donor (XPS pipeline) |
| 3 | dxmmii | Mokujin donor |
| 4 | king-tyrant | Eddy Gordo donor (p1 only — p2 was byte-identical dup of eddy-gordo, excluded per BLOCKED.md) |
| 5 | kinpo | Asuka donor (p1 only — p2 asuka-alt byte-identical dup, excluded) |
| 6 | n3g4tiv0 | Negan donor |
| 7 | nightwolf | Julia donor |
| 8 | phantom | Yoshimitsu donor |
| 9 | purple-rain | Lee donor |
| 10 | rave | Lei donor |
| 11 | saku-ra | Xiaoyu pink-dress donor (p1 only — p2 byte-identical dup, p3 baked victory pose un-T-poseable, xiaoyu-t8 0-byte; see BLOCKED.md) |
| 12 | sam-ur-a1 | p1/p2/p3 |
| 13 | skull | Bryan donor |
| 14 | thor | Ganryu donor (p1 + p2) |
| 15 | waterfall | Josie donor |
| 16 | zui | Steve Fox donor (p2 only — p3 byte-identical dup of steve-fox, excluded) |

Also excluded (not working models / no files / other lanes):
- **DOA4** `teardown/dead-or-alive-4/models/vertex-buffers/` (105 GLBs) — POINT CLOUDS,
  index buffers undecoded (MODELS-ANIMATIONS.md: "not triangulated surfaces").
  Per TEARDOWN-COMPLETION LAW these are not working character models. Cannot T-pose.
- **WMXIX** — no full-body wrestler geometry yet; owned by blocked lane
  `wh-wmxix-renders` (checkpoint `~/workspace/agent-ops/checkpoints/wh-wmxix-renders.json`).
  Do NOT duplicate — that lane renders 8–10 wrestlers for naming review once geometry lands.
- **Tekken 3** — 7 fighters exist only as unassembled parts OBJs (INVENTORY.md).
- **Tekken 6 PSP** — 0 Tekken character meshes (locked in undecrypted COMs); 19 Dissidia
  GLBs are pipeline test data, not teardown characters.
- **SF / VF / SC / Urban Reign / Def Jam / Eastern Mind / TTT2 / T8** — zero character
  model files on disk (INVENTORY.md 2026-10-16, re-verified 2026-10-17).
- **Quaternius / DXMMII viz GLBs** — open-source placeholders / tooling viz, not teardown characters.

## RENDER LIST v1 — working teardown models, never T-posed

### A. WWF No Mercy — DROPPED per owner 2026-10-17
Owner update (2026-10-17 ~08:12 CDT): **stop all No Mercy renders immediately —
do not render any of the 10 No Mercy wrestlers, drop them from the render list
entirely.** A separate lane is copying the No Mercy models to the wrestling
repos and out of Western Heart — this lane does not touch any No Mercy files.
(The 10 wrestlers / 13 GLBs were: Kevin Nash, Kurt Angle, Rhino, Rob Van Dam,
Scott Hall, Shawn Michaels x2, Stephanie McMahon, Steve Austin, The Rock x3,
Triple H. One Kevin Nash test render was made and then deleted from this
branch; no batch was ever launched.)

### B. Tekken 7 — King (rigmodels FBX rip) — THE ONLY v1 TARGET
Repo: `mhvnsnt/game-reverse-engineering`, `tekken7/king/5PMH7G85GYN7P71W3BD1V0249.fbx`
(+ textures in same dir). 18 meshes, 11,362 verts, loads (INVENTORY.md).
Asuka / Eddy / Steve / Xiaoyu donors already T-posed (kinpo, king-tyrant, zui, saku-ra)
— excluded. King has armatures → full skeleton T-pose path applies.

## WORKLOG

- **2026-10-17 ~08:05 CDT** — Lane opened on branch `tpose-sweep-rest`.
  Inventory complete: `RENDER-LIST-REST.md` v1 (10 No Mercy wrestlers / 13 GLBs +
  Tekken 7 King). Approved script recovered from `tpose-all-fighters` branch to
  `docs/tpose-refs/_tools/tpose_render_cycles.py` (byte-identical).
- **2026-10-17 ~08:08 CDT** — King FBX not on local disk (offloaded 2026-10-16 in
  game-reverse-engineering commit b54792a "disk-clear"). Restored
  `tekken7/king/` (63 files: FBX + textures) from git history parent commit to
  /tmp/king-src for the render; nothing written back to that repo.
- **2026-10-17 ~08:10 CDT** — Kevin Nash test render: No Mercy GLBs face **-Y**,
  not -X (approved script's front camera showed the wrestler's left side;
  -Y side camera showed him facing the camera). Textures are embedded/packed.
- **2026-10-17 ~08:12 CDT** — **OWNER UPDATE: stop all No Mercy renders.**
  No Mercy dropped from the render list entirely; separate lane handles those
  models. Test render outputs + No Mercy tooling removed from this branch.
  Lane continues with Tekken 7 King only.
- **2026-10-17 ~08:15 CDT** — King rendered with the approved script
  (front camera -X, ortho, 2048x2048, white bg, ortho_scale 1.12x span).
- **2026-10-17 ~08:45 CDT** — **PANTERA-T7KING reskin** (owner): original Pantera
  attire (purple tights, black panther mask) on the T7 King. Reskin textures
  recovered from game-reverse-engineering release
  `game-re-terabox-batches-20261016` batch-013 (`tekken7/king/pantera/`:
  `pantera.glb` + `pantera_light.glb`, 19 meshes / 19 materials / 54 embedded
  images — the 2026-10-12 reskin, textures baked in). New branch
  `pantera-t7king`. Rendered `pantera.glb` with the approved script byte-identical;
  own-eyes verified front T-pose: black panther mask, yellow eyes, purple
  tights with panther decals, black trunks with red PANTERA, tail.
  Everything named `pantera-t7king`; model + renders in
  `docs/tpose-refs/pantera-t7king/`.
  Own-eyes verified: front-facing T-pose, textures on. FBX contains NO
  skeleton (no LimbNode markers) — authored mesh is already in T-pose, so the
  skeleton T-pose step is a no-op; render is a true T-pose front reference.
  Landed in `docs/tpose-refs/king/` (p1_front.png + p1_side.png).

## FOLLOW-UPS (not in v1 — flagged, owner call needed)

- **PULL-REST 5**: cyborg-x (Alisa), diablo (Heihachi), kinpo-t8 (Asuka T8),
  phantom-t8 (Yoshimitsu T8), thor_alt1 (Ganryu variant) — GLBs were deleted from
  western-heart main in cd3bf38; verify renders survive in `docs/pull-rest/`.
  Recoverable from git history. Render after owner confirms re-pull.
- **Armor King + King S2** (T8 rips) — sources were local-only 2026-10-14 downloads,
  no longer on disk or in any repo. Need re-download before they can render.
- **DOA4** — renderable only after index buffers are decoded (separate teardown lane).
- **WMXIX full bodies** — owned by `wh-wmxix-renders` lane; sweep picks them up only
  if that lane stays blocked.

## RENDER CONVENTION (resolved — match the approved tool exactly)

- Tool: `docs/tpose-refs/_tools/tpose_render_cycles.py` (from `tpose-all-fighters` branch).
- Spec: 2048×2048 RGB PNG, pure white bg, ortho camera,
  ortho_scale = 1.12 × max(span), Cycles CPU, emission-override flat look.
- Orientation: front camera sits on **-X** (character faces -X in RigModels T7 FBX rips;
  verified on the Asuka pilot). This is the "faces the camera / negative-90" convention
  the owner means — the script's camera placement implements it. **Do not guess** —
  reuse this script; own-eyes verify every render faces the camera.
- Output pattern: `docs/tpose-refs/<character>/p1_front.png` (+ `_report.json`
  per the script). Side views: owner asked front-facing; side only if he asks.
- Blender: 4.0.2 headless under `xvfb-run -a` with `env -u PYTHONPATH`
  (`~/workspace/tools/blender/blender-4.0.2-linux-x64/blender`, see ~/TOOLS.md).
- Run at LOW CPU priority (`nice`), in background — never slow other lanes.
  Long batches get a WATCH per OVERNIGHT-WATCH LAW.

## CHECK-BEFORE-START (2026-10-17)

- `tpose-all-fighters` checkpoint: `needs_owner` (stalled) — this sweep is the
  owner-authorized continuation, not a duplicate.
- `wh-wmxix-renders` checkpoint: `running` but BLOCKED on geometry; different task
  (8–10 wrestlers for naming review). No overlap with v1 list — stand clear of it.
- No Blender/Cycles processes running on this VM at sweep start. merge-law-ci-watch
  cron untouched.
- **2026-10-17 ~08:55 CDT** — Lane `tpose-sweep-pullrest5` opened (owner order):
  front T-pose renders for the 5 models restored from cd3bf38 via PR #227
  (cyborg-x, diablo, kinpo-t8, phantom-t8, thor_alt1 — all in
  `game/assets/models/` on main). Check-before-start: pull-rest-worker,
  tekken7-pull, wh-t7t8-hunt all `done`; tpose-all-fighters `needs_owner`
  (stalled); wh-wmxix-renders `running` on WMXIX wrestlers only — no overlap.
  No other lane rendering these 5.
- **2026-10-17 ~09:00 CDT** — Batch 1 (base script): all 5 imported and
  rendered, BUT own-eyes check showed cyborg-x, diablo, kinpo-t8, phantom-t8
  facing RIGHT (profile) in p1_front.png — these GLBs face **-Y**, not -X.
  thor_alt1 was correct front-facing. Proof: diablo p1_side.png (camera on -Y)
  showed him front-on in T-pose.
- **2026-10-17 ~09:05 CDT** — Created documented variant
  `docs/tpose-refs/_tools/tpose_render_cycles_faceY.py`: byte-identical copy of
  the approved script plus a 3-line, documented Rz(-90°) post-import rotation
  mapping -Y-facing models to face -X (front camera). Side camera then sees the
  model's left side, matching the base script's spec. Did NOT guess — verified
  empirically.
- **2026-10-17 ~09:10 CDT** — Batch 2 (faceY variant): re-rendered the 4.
  Own-eyes verified ALL 5 now front-facing T-pose. Honest flags: cyborg-x
  textures resolve washed-out/gray (geometry + pose correct); kinpo-t8's arms
  angle slightly downward (authored pose, not a perfect horizontal T).
