# Decision: in-suite hand-tooling with headless Blender backend

Worker 66, 2026-10-22. Implements owner directives (verbatim):
*"Set up all the stuff on your side, then when I go into the character creation suite, make it where
I can do the hand-tooling part IN the character creation suite — where I don't have to actually use
Blender, but Blender's just hooked up in the character creation suite."*
*"I'll call that up so it works for all of the models, all the characters, all the parts. They're all
interchangeable, deletable, replaceable, addable, movable, resizable, scalable, reshapeable — full
Blender-level capabilities."*

Research: `docs/research/2026-10-22-W66-in-suite-mesh-edit-research.md`.

## Decision

Ship a **three-layer system**, all inside the creation suite's existing structure:

1. **Edit-manifest layer (in-browser, instant).** Every hand-tooling action is first a JSON entry
   in a per-fighter manifest (visibility, soft-delete, staged transforms). Reversible,
   undoable, phone-instant. Never touches a GLB.
2. **Job-queue layer — the EXISTING suite queue, no parallel server.** Mesh-edit is a new tool
   in `tools/suite-jobs/` (`tool: "mesh-edit"` → `tools/mesh-edit/run_mesh-edit_job.py`), running
   on the same server (`tools/suite-jobs/server.py :8766`) the JOBS tab already polls. Suite UI
   POSTs `{tool:"mesh-edit", params:{...}, out}` → runner spawns headless Blender
   (`blender -b --factory-startup --python tools/mesh-edit/mesh_edit.py -- --job job.json`)
   → job writes `out_glb` + `out_report` (+ preview render). Crew-runnable without the server
   via `python3 tools/suite-jobs/run_job.py --spec <spec>.json` (same as every other tool).
3. **Suite UI layer (`customization/create-fighter/js/meshedit.js`).** A "MODEL EDIT" mode inside
   the existing suite viewport (`preview3d.js`): tap-to-select meshes, touch gizmo (vendored
   TransformControls), part list, hide/show/delete buttons, job submit. Progress + results live
   in the existing JOBS tab (it already polls `/jobs/<id>` and offers LOAD GLB IN PREVIEW).
   Registered in `js/tools.js` like every other tool. Nests under the Appearance step of the
   WWE flow — never a parallel editor (INTEGRATION LAW).

Rejected: (a) a second Node job server for mesh-edit — would duplicate `tools/suite-jobs`
(PER-TOOL UNIFICATION LAW: one queue, tools register into it); (b) mcp-for-blender as the suite
backend (its addon socket refuses `--background`; needs a display machine — see
`tools/mcp/README.md`). MCP stays the *agent* lane; the suite lane is plain headless jobs.

## Job schema (v1)

```json
{
  "job_id": "me-20261022-0001",
  "fighter": "pantera",
  "attire": "attire1",
  "source_glb": "roster/pantera/attires/attire1/model.glb",
  "ops": [
    { "op": "mesh_hide",   "mesh": "Jacket_Mesh" },
    { "op": "mesh_delete", "mesh": "BeltBuckle_Mesh" },
    { "op": "mesh_transform", "mesh": "Pauldron_L",
      "translate": [0, 0.02, 0], "rotate_euler": [0, 0, 0.1], "scale": [1.1, 1.1, 1.1] },
    { "op": "part_import", "donor": "defjam:vest_0142", "socket": "Spine1",
      "fit": { "scale_to_bone": true } },
    { "op": "mesh_sculpt", "mesh": "Head_Mesh",
      "strokes": [{ "brush": "smooth", "strength": 0.4, "radius": 0.05,
                    "center": [0.0, 1.62, 0.12] }] }
  ],
  "out_glb": "roster/pantera/attires/attire1/model-edit-me-20261022-0001.glb",
  "out_report": "roster/pantera/attires/attire1/model-edit-me-20261022-0001.report.json",
  "reweight": "auto"
}
```

### Op catalog (v1)

| op | Effect | Weight-safe | Notes |
|---|---|---|---|
| `mesh_list` | inventory: names, verts, skinned? | n/a | read-only; feeds the part list |
| `mesh_hide` / `mesh_show` | visibility flag in manifest | ✅ | no job needed; suite applies instantly |
| `mesh_delete` | remove mesh datablock, export | ✅ | soft-delete first (manifest), hard delete on bake |
| `mesh_transform` | bake translate/rotate/scale (object-space) | ✅ | non-uniform scale allowed; baked into verts |
| `mesh_duplicate` | copy mesh (mirror option) | ✅ | weights duplicated with it |
| `part_import` | import donor GLB/part-catalog mesh, align to socket | ✅ | interchange + add; donor addressed as `library:id` (Def Jam/WWE/No Mercy conventions) |
| `mesh_sculpt` | sculpt strokes (grab/smooth/inflate/pinch) | ⚠️ re-weight pass | geometry changes → auto weight-transfer + validate gate |
| `mesh_remodel` | remesh / subdivide / decimate | ⚠️ re-weight pass | same gate |

`"reweight": "auto"` — any op marked ⚠️ triggers a GameRig-style weight-transfer
(`tools/anim/repair_sleeve_weights.py` k-NN approach) and the tripo-intake validation gate.
Results that fail the gate are badged `bake_pending` (Def Jam honest-state pattern), never
presented as finished.

## API (existing suite-jobs server — mesh-edit registers as a tool)

```
POST /jobs        {tool:"mesh-edit", params:{<mesh-job v1>}, out:"<out_glb>"} -> {id} (202)
GET  /jobs        -> [{id, tool, state}]
GET  /jobs/<id>   -> {id, tool, state, out, log[], error?}
GET  /tools       -> [{tool:"mesh-edit", runnable, detail}]   (add to registry list)
```

The mesh-job v1 params are the schema in this doc (fighter/attire/source_glb/ops/out_glb/
out_report/reweight). The runner (`run_mesh-edit_job.py`) maps them 1:1 to the `mesh_edit.py`
job file. The JOBS tab (creation-flow module) already polls `GET /jobs/<id>` and offers
LOAD GLB IN PREVIEW on `state == "done"` — mesh-edit jobs appear there with zero new UI.

- When the `blender` binary is missing, the runner raises a clear error ("run
  tools/setup/setup_toolchain.sh") instead of a dead button. The manifest layer
  (hide/show/staged transforms) keeps working regardless — it never needs Blender.
- Static hosting note: GitHub Pages can't run the server. When unreachable, the suite
  downloads the job spec (`downloadJobSpec`) for crew-mode execution via
  `python3 tools/suite-jobs/run_job.py --spec <spec>.json` — same pattern as every
  other tool in the TOOLS tab.

## Suite UI wiring (no parallel editor)

- `customization/create-fighter/js/meshedit.js` (new): `MeshEditMode` class. Attaches to the
  existing `Preview3D` instance: raycast tap-to-select → `TransformControls` gizmo
  (translate/rotate/scale mode buttons, big touch targets, axis-lock buttons) → action bar
  (Hide / Show / Delete / Duplicate / Bake transform / Import part / Sculpt) → job submit →
  progress toast → apply result.
- Registered in `js/tools.js` TOOL REGISTRY as a layer-1 unified system ("Model Edit —
  Blender backend") with per-op layer-2 menus. `command:` strings point at the real scripts
  (same convention as the MB-Lab / GameRig entries).
- Menu nesting: under the WWE flow's **Appearance → Attire Parts → MODEL EDIT (hand-tooling)**
  submenu, per worker 65's blueprint. Documented as the nesting point; worker 65's landing
  adds the actual menu node.
- `customization/CHARACTER-CREATION.md` §2 gets a "Model Edit (hand-tooling)" subsection
  describing the mode and its menu home.

## Integration contracts (workers 64 / 65 — not yet landed)

- **w64 (clothing-layer taxonomy):** mesh ids in jobs are raw GLB node names; w64's taxonomy
  provides the *label* layer (`mesh_taxonomy.json`: mesh → slot/category/label). `meshedit.js`
  resolves labels through it when present, falls back to node names. No duplication: we do not
  invent a second taxonomy.
- **w65 (WWE CAW menu blueprint):** we own the *engine* (ops, queue, UI mode); w65 owns the
  *menu tree*. Our nesting point is fixed above; w65 places the node.

## Undo / safety

- Source GLBs are immutable (tripo-intake rule). Jobs write new files; the manifest references
  them. Undo = drop manifest entries; "Reset to source" = empty manifest.
- `>20-line deletions` rule and the no-clobber policy apply to every suite-file edit in this lane.

## Proof plan (this round)

1. `node --check` on suite `meshedit.js`.
2. AST-parse `mesh_edit.py` + `run_mesh-edit_job.py` (no Blender on this VM; run-shape mirrors
   proven `gamerig_backend.py`).
3. Runner unit test: `build_mesh_job` validation (bad op rejected, out==source refused),
   `validate_job` pure-function checks, fake-Blender `run_blender_job` parse of the
   `WH_MESH_EDIT_REPORT` line.
4. `tools/suite-jobs` server still imports (registry list edit is one word).
5. Suite loads with zero page errors (headless Chromium harness already used by worker 38).

Follow-ups (not this round): real Blender run of `mesh_edit.py` ops on a roster GLB (needs
setup_toolchain.sh), vendored TransformControls file, worker 64/65 contract handshake,
one-line JOBS-tab tool-dropdown addition (`mesh-edit` option in creation-flow.js — worker 37's
file, left for their lane with the contract documented here).
