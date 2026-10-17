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

### A. WWF No Mercy — 10 wrestlers (13 files)
Local: `~/workspace/wmxix-mod-testbed/mods/no-mercy-wrestlers/`
(all verified: 22 meshes each, humanoid proportions, ~2.3–2.5k verts, INVENTORY.md)

| wrestler | file(s) |
|---|---|
| Kevin Nash | kevin_nash/kevin_nash_1.glb |
| Kurt Angle | kurt_angle/kurt_angle_1.glb |
| Rhino | rhino/rhyno_1.glb |
| Rob Van Dam | rob_van_dam/rob_van_dam_1.glb |
| Scott Hall | scot_hall/scott_hall_1.glb |
| Shawn Michaels | shawn_michaels/shawn_michaels_{1,2}.glb |
| Stephanie McMahon | stephanie_mcmahon/stephanie_mcmahon_1.glb |
| Steve Austin | steve_austin/steve_austin_1.glb |
| The Rock | the_rock/the_rock_{1,2}_glb + the_rock_bald.glb |
| Triple H | triple_h/triple_h_1.glb |

Note: GLBs contain **no armatures** (skins=0, verified 2026-10-17) — unrigged N64-era
meshes. The tpose script's skeleton T-pose step will no-op; models render in authored
pose (expected T/A-pose). Facing direction unverified for GLB sources — first render
of each confirms front-facing; adjust per-model if a source faces differently.

### B. Tekken 7 — King (rigmodels FBX rip)
Repo: `mhvnsnt/game-reverse-engineering`, `tekken7/king/5PMH7G85GYN7P71W3BD1V0249.fbx`
(+ textures in same dir). 18 meshes, 11,362 verts, loads (INVENTORY.md).
Asuka / Eddy / Steve / Xiaoyu donors already T-posed (kinpo, king-tyrant, zui, saku-ra)
— excluded. King has armatures → full skeleton T-pose path applies.

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
