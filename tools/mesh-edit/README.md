# tools/mesh-edit/ — in-suite hand-tooling backend (headless Blender)

Owner directive: *"make it where I can do the hand-tooling part IN the character creation suite —
where I don't have to actually use Blender, but Blender's just hooked up in the character
creation suite."* Full capability set: models/parts are interchangeable, deletable, replaceable,
addable, movable, resizable, scalable, reshapeable.

Architecture: `docs/decisions/2026-10-22-W66-mesh-edit-architecture.md`.
Research: `docs/research/2026-10-22-W66-in-suite-mesh-edit-research.md`.

## Pieces

| File | What |
|---|---|
| `mesh_edit.py` | Blender-side op driver. Run: `blender -b --factory-startup --python mesh_edit.py -- --job JOB.json`. Reads job JSON, imports `source_glb`, applies ops in order, exports `out_glb` + `out_report` (+ preview PNG). `validate_job()` / `resolve_blender()` / `run_command()` importable from plain python3. |
| `run_mesh-edit_job.py` | suite-jobs runner (`tool: "mesh-edit"`). `run_job(spec, log)` builds the job file, spawns headless Blender, parses the report, returns the artifact path. Registered in `tools/suite-jobs/server.py`'s tool registry. |
| `tests/test_runner.py` | Unit tests: job validation, report-line parsing with a fake Blender. No Blender needed. |

Mesh-edit is a **tool in the existing suite job queue** (`tools/suite-jobs/`), not a parallel
server (TOOL UNIFICATION LAW). The suite's JOBS tab already lists/polls these jobs and offers
LOAD GLB IN PREVIEW on completion.

## Op catalog (v1)

`mesh_list` (read-only) · `mesh_hide` / `mesh_show` (manifest hints, suite-side) ·
`mesh_delete` · `mesh_transform` (bake TRS into verts) · `mesh_duplicate` (+`mirror_x`) ·
`part_import` (donor GLB or `library:id` from the suite parts catalog) ·
`mesh_sculpt` (smooth/grab/inflate/pinch strokes — flags `reweight_needed`) ·
`mesh_remodel` (remesh/subdivide/decimate — flags `reweight_needed`).

Any op that changes vertex count sets `report.reweight_needed = true`; the caller then runs
the weight-transfer pass (k-NN approach from `tools/anim/repair_sleeve_weights.py`) and the
tripo-intake validation gate. Failed-gate results are badged `bake_pending`, never finished.

## Running

```bash
# 1. install Blender (once, on the job-server machine)
bash tools/setup/setup_toolchain.sh        # Blender 4.0.2 -> ~/workspace/tools/blender/

# 2. start the suite job server (serves ALL tools incl. mesh-edit)
python3 tools/suite-jobs/server.py         # :8766

# 3. in the suite: TOOLS tab → MODEL EDIT (unified) → ENTER MODEL EDIT,
#    or JOBS tab → submit {"tool":"mesh-edit", "params":{...}, "out":"..."} directly.

# crew-mode (no server): run a spec directly
python3 tools/suite-jobs/run_job.py --spec jobs/my-meshedit.json
```

## Safety

- Source GLBs are **immutable** — `out_glb` must differ from `source_glb` (enforced).
- Suite-side undo = drop edit-manifest entries; "Reset to source" = empty manifest.
- Geometry-changing ops flag `reweight_needed`; bake is gated on weight validation.
