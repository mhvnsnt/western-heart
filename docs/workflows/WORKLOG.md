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

## 2026-10-14: Shared Creation Suite v0 (Grok Bot executor)
- Survey: `gh search code --owner mhvnsnt` for creation suite / moveset editor / customizer / morphTargetInfluences; read Bannon DNA_SCHEMA, CREATION_SUITE, moveset_schema.json, customizer manifests via `gh api`. Chose Bannon DNA + moveset schema as base.
- Read western-heart PRs (#110–#116) first; Lab #116 owns `lab/` and `attire.gd`, so this PR only adds `packages/creation-suite/` and `docs/creation-suite/`.
- Sparse shallow clone (`--depth 1 --filter=blob:limit=2m`, sparse-checkout) because disk was ~4.5 GB free.
- Wrote the package (ES modules, three r186). `node --test` 4/4 pass.
- Proof: pulled `pantera_leoman.glb` + `bannon_mask.glb` from branch `grok/lab-playable-slice` via `gh api` (not committed), served with python http.server, rendered with playwright-core + headless Chrome (swiftshader). Fixed three bugs found by the render (morph dictionary names, region size units, front/back regions missing the surface). Labels added with PIL → `docs/creation-suite/creation_suite_proof.jpg`.
- gitleaks on the diff; merged origin/main; no deletions.
