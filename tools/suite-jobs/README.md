# tools/suite-jobs — creation suite job queue

The creation suite is a static browser app. Blender-backed tools (MB-Lab,
GNM bake, MPFB2-live, GameRig auto-rig, jiggle bake, texture paint,
export/optimize) cannot run inside the browser — so every such menu option
submits a **job** here instead of being a dead button.

Two ways to run jobs:

## 1. One-shot CLI (no server)

```bash
python3 tools/suite-jobs/run_job.py --spec jobs/mb-lab-heavyweight.json
# writes jobs/mb-lab-heavyweight.status.json: {state: done|error, out, log}
```

## 2. Job server (live status in the suite UI)

```bash
python3 tools/suite-jobs/server.py [--port 8766] [--jobs-dir jobs]
```

Endpoints (all JSON):

| Method | Path | Does |
|---|---|---|
| POST | /jobs | body = job spec → `{id}` (queued) |
| GET | /jobs | list all jobs (id, tool, state) |
| GET | /jobs/<id> | full status: state, params, out, log, timings |
| GET | /tools | tool registry: which tools are installed & runnable here |

The suite's **Jobs panel** POSTs specs, polls `/jobs/<id>`, and offers the
result GLB for import when `state == "done"`. If the server isn't running,
the panel shows the exact command to start it — honest, never a dead end.

## Job spec format

```json
{
  "tool": "mb-lab",
  "params": { "character": "male_01", "params": {"mass": 0.7} },
  "out": "customization/templates/meshes/heavyweight.glb"
}
```

`tool` dispatches to `tools/<tool>/run_<tool>_job.py` (or the registered
entry in TOOLS below). `out` is where the artifact lands. Status JSON is
written next to the spec (`<spec>.status.json`) for the CLI path, and kept
in memory + `<jobs-dir>/status/` for the server path.

## Adding a tool

1. Put `run_<tool>_job.py` in `tools/<tool>/` with a `run_job(spec, log)`
   function returning the artifact path (or a `main()` taking
   `--spec/--out`).
2. Register it in `run_job.py`'s TOOLS table.
3. It shows up in `GET /tools` automatically, and the suite menus can
   submit jobs for it.
