# Workflow log

## 2026-10-14: Western Heart inventory (Grok Bot executor)
- `gh repo list mhvnsnt --limit 300`, filtered for related repos. Cloned 6 repos at `--depth 50` with `GIT_LFS_SKIP_SMUDGE=1` into /workspace/western-heart-inventory.
- Python walker (`inv.py`): file category counts and sizes, LFS pointer and empty-file scan, and GLB JSON-chunk parse for meshes, skins, joints and animations.
- Read `game/js/*` (grep for loaders and fetch), the READMEs, CHIMERA-BUILD.md, and MoneyManBusch's audit (via `gh api`).
- `gh release list` to see what's stored in Releases.
- Served `game/` with `python3 -m http.server` and took a headless screenshot with Chrome (`--headless=new --use-gl=swiftshader`).
- Wrote INVENTORY.md and inventory.json. Ran gitleaks on the changed files. Docs-only PR: merged origin/main, no rebase or force-push, no deletions.

## 2026-10-14: Lab M1, skeleton + T3 importer + rig check (Grok Bot executor)
- The repo was confirmed PRIVATE (`gh repo view`). The owner approved the Lab track using his own source games.
- Godot 4.3-stable was installed headless at /workspace/tools/godot. Web export templates were streamed out of the .tpz with python `stream-unzip`, because the disk had only about 2 GB free.
- Read the `kmd_parse.py` hierarchy and the `pose_assemble.py` stance OBJ, then fit a rigid Kabsch transform per part (numpy). The stance → world-aligned canonical bind and the `.glb` writer are hand-rolled (numpy).
- Clips use 2-bone analytic IK in `tools/clips.py`.
- Rig check: a numpy glTF evaluator with CPU skinning, checking edge stretch, bone drift and feet-to-floor. It runs as a unittest.
- Previews were rendered with matplotlib and viewed before committing.
- M2: wrote MoveTable (GDScript) and a headless SceneTree test; ran `godot --headless --import` then the test (PASS 7×4).
- M3 (playable slice):
  - Godot GDScript (fighter/ai/hud/main/attire).
  - Owner GLBs pulled with the Google Drive connector. Decoded and LOD'd with `@gltf-transform/cli` (dequantize, weld, simplify, resize).
  - Auto-rig: landmark joints, inverse-distance weights with lateral gating, Laplacian smoothing (scipy) and continuous sparsification to 4 influences. Rig check iterated from FAIL (×77 stretch) to PASS.
  - Bannon mask: per-rig presets fitted in the head-bone rest frame, plus a follow/clip/pop check over 337 frames.
  - Capture: Godot Movie Maker under xvfb with Mesa llvmpipe → ffmpeg H.264, ffprobe and a contact sheet (viewed). HTML5 export uses the `web_nothreads` template; a puppeteer-core real-time screenshot is the web proof.

## 2026-10-14: Shared Creation Suite v0 (Grok Bot executor)
- Survey: `gh search code --owner mhvnsnt` for creation suite / moveset editor / customizer / morphTargetInfluences; read Bannon DNA_SCHEMA, CREATION_SUITE, moveset_schema.json, customizer manifests via `gh api`. Chose Bannon DNA + moveset schema as base.
- Read western-heart PRs (#110–#116) first; Lab #116 owns `lab/` and `attire.gd`, so this PR only adds `packages/creation-suite/` and `docs/creation-suite/`.
- Sparse shallow clone (`--depth 1 --filter=blob:limit=2m`, sparse-checkout) because disk was ~4.5 GB free.
- Wrote the package (ES modules, three r186). `node --test` 4/4 pass.
- Proof: pulled `pantera_leoman.glb` + `bannon_mask.glb` from branch `grok/lab-playable-slice` via `gh api` (not committed), served with python http.server, rendered with playwright-core + headless Chrome (swiftshader). Fixed three bugs found by the render (morph dictionary names, region size units, front/back regions missing the surface). Labels added with PIL → `docs/creation-suite/creation_suite_proof.jpg`.
- gitleaks on the diff; merged origin/main; no deletions.

## 2026-10-22 ~20:30 CDT — worker 46: Ashlane/Brutalfist model render batch (28 renders)

**Rendered all 28 Ashlane-universe characters** (one best variant each, facing camera, neutral
studio background, natural A-pose/bind pose — no forced T-pose) for the user's WH-fighter review.
Catalog: `docs/research/ashlane-render-catalog-2026-10-22.md`. No roster/canon writes — review only.

- Variant choice = canonical defaults from the source repo's own roster
  (`brutalfistgrokversiontenpointfive/src/data/bannonGlbRoster.ts`, first-listed/"Default" attire).
  PABLO got a **second** render (PABLO_blackreign.glb — canon-relevant dark variant per user).
  SOMBRA_NEGRA_rigged.glb is the only cast model in `AshLane-prototype`.
- VF5 mappings flagged in catalog (user-locked 2026-10-22, no changes without user's word):
  LOCKED = BANNON→Jeffry McWild, EL_TORO_DE_ORO→Wolf Hawkfield, PABLO→El Blaze, NPC_FINXSSE→Lei-Fei.
  Candidates = MASTER_SENSEI→Lau, SOMBRA_NEGRA→Kage, CIPHER→Goh (music-themed "emo type" note),
  AARON_RUBEN→Akira, CODY→Jacky, JAGER→Vanessa.
  Unmapped: TRIPLE_XXX, ECHO, HOLLOW, STATIC, STICKUP, ONYX, TYNESHIA, MAIME, EDWIN_KENNEDY,
  HALL_NIGHTER, STAN_COMBS, KOBRA, VIPER. VF5 women (Sarah/Pai/Aoi/Eileen) have no counterparts
  identified — female-presenting models in this batch: Echo, Maime, Onyx, Tyneshia (flagged).
- Pipeline: three.js r160 GLTFLoader + Playwright headless Chromium/SwiftShader, studio 3-point
  lighting, 720x960 PNG. Viewer + batch scripts at `~/workspace/ashlane-renders/` (site/viewer.html,
  render.mjs, batch.json) — reusable for re-renders. Large GLBs stayed in the source repos.
- Render-time findings: (1) BANNON_rigged.glb needed bone-aware camera framing (skinned geometry
  bounds were bind-pose, camera ended up inside the torso). (2) **SOMBRA_NEGRA_rigged.glb is
  damaged**: JOINTS_0 indices reach 65535 against 58 skeleton joints (~92k vertices affected) and
  the mesh branch carries a bogus 0.035 node scale — rendered as bind-pose T-pose at natural
  scale for review. Needs a full re-rig before any WH intake; skin data unrecoverable as-is.
- Remote-storage links expire 2026-10-24 ~20:30 UTC. 11/28 uploaded at PR time; remaining 17
  pending the user's upload-approval taps (per-file confirmation cards).
