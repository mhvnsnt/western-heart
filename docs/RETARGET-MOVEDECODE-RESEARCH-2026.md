# RETARGET + MOVE-DECODE RESEARCH — 2026-10-19

Why this doc exists: two recurring problems converged on 2026-10-19.
(A) Mocap retargets ship with triangular tearing/stretching (root causes
found so far: Z-up verts vs Y-up skeleton, animation channels on wrong
nodes, scene placements baked into clips, hard L/R skin weights tearing at
seams). (B) Movesets were thin and proxy-heavy; the FULL MOVESET LAW
(owner 2026-10-19) requires every Tripo-model fighter to carry the FULL
moveset of their base character, 100+ moves, from real teardown data.

Method: current (Oct 2026) web research + inventory of what this repo and
workspace already had. Nothing here distributes game assets: extraction
tooling is documented for study/RE of games in the owner's collection
(STEAL-LIKE-AN-ARTIST law: learn how the pros built it; the data formats
and our own conversions are ours).

---

## A. Mocap retargeting — 2026 state of the art

### What we already had (do not duplicate)

- `tools/auto_rig/` — unified auto-rig system (PR #264 lineage): bone-name
  canonicalization to the WH Mixamo-style set (`backends/retarget.py`),
  Blender heat-weight backend, k-NN weight transfer, AI skeleton backends
  (MagicArticulate Apache-2.0, UniRig MIT — vendored), and `validate.py`,
  the playable gate. Its check #5 (p99.9 triangle-edge stretch < 2.5 on the
  standard clips) was documented but NEVER IMPLEMENTED — `--clips` was in
  the usage string but not in argparse. **This PR implements it** (see
  "What this PR adds").
- `lab/skeleton/retarget_maps.json` — canonical bone maps for the three rig
  families in use (tekken3_rigid27, mixamo49, rigify13), incl. the Mixamo
  world-space-delta rest-pose note.
- `docs/ANIMATION-PIPELINE.md` — CMU BVH fighting clips (16 files in
  `assets/free-pull-1/cmu-mocap/fighting/`) + Quaternius UAL1 retarget plan.
- Workspace side tools (not in repo): `universal-retarget/`, `wt-mocapsit/
  mocap_retarget.py`, `anim-harvest/` (CMU bank builder).

### External tooling found (Oct 2026)

| Tool | License / cost | What it is | URL |
|---|---|---|---|
| Rokoko Studio + free Blender retargeting plugin | Free (account required) | Industry-standard retarget path for our Blender pipeline; Build Bone List -> Retarget Animation, auto-scale for height mismatch | https://www.3dblendered.com/blender-add-ons/how-to-do-motion-capture-in-blender-with-rokoko-tools/ |
| Blender built-ins (NLA, Pose Library, slotted Actions, Animation Layers) | GPL (Blender) | Native layering/cleanup; dedicated addon still recommended for bone mapping | https://www.strayspark.studio/blog/best-blender-animation-addons-2026 |
| MotionBridge | MIT (open source, Oct 2026) | Browser mocap -> rigged GLB/FBX with automatic/manual bone mapping; animated GLB + BVH export; MediaPipe-based | http://dev.to/adonisglobal/motionbridge-open-source-motion-capture-for-blender-and-2d-animation-gm6 |
| BlendMoCap | Open source (GitHub) | BVH -> character transfer addon; requires same core structure; explicit "will not correct differences between armatures" caveat | https://github-wiki-see.page/m/AO-StreetArt/BlendMoCap/wiki/Initial-Design |
| CEB SAM 3D Body Loader | Free (Patreon) | AI mocap inside Blender 4.0-5.2; bi-directional Auto-Rig Pro + MHR/SOMA cross-rig retargeting, foot-slide killer | https://www.patreon.com/cebstudios/posts/ceb-sam-3d-body-172610949 |
| BlenRig 6 | Open source | Production deformation rig; pairs with native Blender retarget flows | https://www.strayspark.studio/blog/best-blender-animation-addons-2026 |
| FreeMoCap | Open source | Markerless mocap, fully free pipeline | https://aimocapfree.com/ |
| Cascadeur (free tier) | Proprietary, free tier | Physics-based mocap cleanup, FBX/USD export | https://aimocapfree.com/ |
| Auto-Rig Pro | Commercial (~$40) — DOCUMENT ONLY, not pulled | The reference Blender retarget addon; our `blender-heat` + canonicalization covers the same job in-repo | https://mocaponline.com/blogs/mocap-news/3d-animation-software-comparison |
| Mimem "Mocap Blender" addon (MB) | Commercial — DOCUMENT ONLY | mimem FBX retarget into Blender rigs; requires applied transforms + matched facing (same failure class as our incidents) | https://www.mimem.ai/docs/retarget-to-blender |

**Retargeting verdict for WH:** keep the in-repo pipeline (canonicalize ->
Blender bake) as the spine; Rokoko's free plugin is the best external
cross-check for Mixamo-family rigs; MotionBridge (MIT) is the most
promising pull-in for browser-side quick retargets. Every external tool
above shares the same precondition set that caused our incidents: matched
facing, applied transforms, similar rest poses. The missing piece was never
another retargeter — it was a VALIDATOR that refuses bad output. That is
what this PR builds.

### Stretch/tearing detection (the gap this PR fills)

No surveyed tool ships an automated bone-length/tearing gate. The standard
checks, implemented in `tools/auto_rig/anim_check.py` (headless, pure
python + numpy, no Blender):

1. **Bone-length variance** — per bone, (max-min)/rest across frames;
   rigid bones must not stretch (default fail > 2%).
2. **Rest deviation** — a bone whose MEAN animated length sits > 2% off
   rest is permanently deformed by baked scale (constant scale keys are
   invisible to check 1).
3. **Vertex tearing** — per-vertex displacement spikes between consecutive
   frames (> 0.35 m absolute, or > 8x frame median and > 0.10 m).
4. **Edge stretch p99.9** — triangle-edge ratio vs rest, edges < ~1 cm
   excluded as ratio noise; fail > 2.5 (the validate.py gate value).
5. **Root offset** — root joint wandering > 1.0 m from bind = scene
   placement baked into the clip.
6. **Wrong-node channels** — channels animating nodes that are neither
   joints nor joint ancestors do nothing at runtime.

Verified against Blender 4.0.2 headless on `game/assets/models/pantera.glb`
(the main shipped model): the validator's numbers match Blender's own
evaluation exactly (Hips world pos [0.496, -0.150, -7.128] at Idle frame 0;
pants-seam vertex pair 0.0103 m at bind -> 0.1458 m evaluated).

### Findings on the shipped pantera.glb (proof the gate was needed)

- **Idle**: root joint `Hips` wanders **8.21 m** from bind (Run/Walk/TPose
  stay at bind) — a scene placement was baked into this one clip.
- **Idle**: p99.9 edge stretch **11.27** (gate 2.5). Worst offenders are
  hard-weight seam edges: pants mesh verts bound 100% to LeftUpLeg vs
  RightUpLeg sit 1.0 cm apart at bind and 14.6 cm apart mid-Idle.
- Bones themselves are rigid (0 variance flags) — the GLB's skeleton data
  is sound; the defects are clip placement + skin weights, which matches
  the owner's playtest read (detached/spinning limbs are a runtime/weight
  problem, not corrupt bone data).
- Run/Walk are only **2-keyframe STEP stubs** — flagged here as a data
  note for the gameplay lanes, not a validator failure.

---

## B. Fighting-game move-data extraction — 2026 state of the art

### What we already had

- **T3 banks decoded in-repo**: `tools/gen-movesets-t3.py` merged full
  Tekken 3 bank depth into every fighter file (bank sizes 365-652 rows;
  e.g. King bank 652 rows / 218 attacks). Per-file provenance lives in each
  moveset JSON (`t3_bank`, `t3_bank_rows`, `generated_full_moveset`).
- `moveset-library/movesets/MOVE-DATABASE.json` — WWF No Mercy (400+ named
  moves) + WMXIX YANM clip index + T7 data-format study.
- Doc Frank precedent: complete T3 command list for Dr. Bosconovitch from
  the Tekken Wiki movelist (102 base moves) + 5 owner-canon originals.
- DOA/VF conversions: `docs/movesets/DOA-VF-CONVERSION-2026-10-19.md`
  (DOA5LR / VF5FS community movelists + frame data, HP-scaled).
- T8/T7/SF/KOF cluster lanes merged this week (see MOVESET-COVERAGE.md).

### External tooling found

| Tool | License / cost | What it does | URL |
|---|---|---|---|
| Kiloutre/TekkenMovesetExtractor | Open source (GitHub; verify LICENSE before vendoring) | Extracts FULL movesets from a running Tekken 7 (memory read; T5/T6/Tag2 export exists but T6 exports are known-glitchy, Tag2 best-supported after T7); exports/imports `.bin` moveset files via GUI or scripts; Python 3.6.5 + pywin32 | https://github.com/Kiloutre/TekkenMovesetExtractor/releases |
| tekkendocs (pbruvoll) + Wavu | Open source | T8 frame data as per-character CSVs (`data/wavuConvertedCsv/{char}/{char}-special.csv`, 15-column semicolon format) + JSON movelists; the canonical T8 data source | https://deepwiki.com/pbruvoll/tekkendocs/4.1-csv-data-format-and-fields |
| MMDK (alphazolam) | Open source (GitHub) | Street Fighter 6 modding dev kit on REFramework: per-character `moves_dict.json` (movesets, hit data, animations, commands) under `reframework/data/MMDK/PlayerData/{char}/` | https://deepwiki.com/alphazolam/MMDK/3-character-data-system |
| xmduke/hitbox | Open source (GitHub) | KOF XV hitbox visualization + in-game data extraction (memory); VS2019/CMake, DX11 overlay | https://deepwiki.com/xmduke/hitbox/6-development-guide |
| UModel / UE Viewer | Freeware | Tekken 7 asset extraction (meshes/textures) — pairs with the moveset extractor for full T7 character pulls | https://github-wiki-see.page/m/CDDTreborn/Tekken7_PC-Modding-Guides/wiki/Umodel-UE-Viewer-Quick-Start-Guide-or-Reference---Tekken-7 |

**Extraction verdict for WH:** the T3-bank path is already at full depth
in-repo. The next real-data frontiers, in order: (1) T7 full movesets via
TekkenMovesetExtractor against owned T7 (our T7-era bases — Katarina,
Miguel, Bob, Lars — currently ride ASSIGNED T3 style banks, the
FULL-BANKED class in the coverage report); (2) T8 frame data via
tekkendocs/Wavu CSVs for the T8 cluster; (3) SF6 via MMDK `moves_dict.json`
for the SF-based fighters; (4) KOF XV via hitbox-style extraction for
Iori-class fighters. DOA/VF already converted from community movelists.

---

## What this PR adds

- `tools/auto_rig/anim_check.py` — headless retarget validator (above).
- `tools/auto_rig/validate.py` — `--clips` finally wired: check #5 runs
  anim_check over the supplied clip GLB(s) instead of reporting "unknown".
  Additive only; behavior without `--clips` is unchanged.
- `tools/auto_rig/tests/test_anim_check.py` — 7 tests with synthetic GLB
  fixtures, one per failure mode (clean / variance / rest-deviation /
  tearing / wrong-node / root-offset / CLI exit codes).
- `tools/moveset-coverage/moveset_coverage.py` + `docs/MOVESET-COVERAGE.md`
  — the FULL MOVESET LAW made measurable (see below).
- This doc.

## Test evidence (2026-10-19 run)

- `anim_check tests: 7/7 pass`; existing `test_retarget.py` 3/3 and
  `test_normalize.py` pass (no regressions).
- `anim_check.py --in game/assets/models/pantera.glb`: Idle FAILS (root
  8.21 m drift; edge p99.9 11.27); Run/TPose/Walk PASS. Blender 4.0.2
  cross-check reproduces both numbers exactly (quoted above).
- `validate.py --in pantera.glb --clips <dir>`: check #5 now returns real
  per-clip stretch verdicts instead of "unknown".

## Coverage snapshot (from docs/MOVESET-COVERAGE.md, this run)

85 fighter files · 7,294 base moves (7,612 with strings/specials) ·
15 FULL-REAL (own bank, >= 100) · 37 FULL-BANKED (full real bank assigned
as style) · 30 REAL-THIN · 3 PROXY. The stale 2026-10-19 evening snapshot
(62 files / ~822-999 moves / 45 proxy) is superseded: the T3-bank
generator and the T8/T7/SF/KOF cluster lanes landed on main after it.
