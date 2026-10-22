# In-suite hand-tooling (Blender backend) — research report

Worker 66, 2026-10-22. Owner directives (verbatim):

1. *"Set up all the stuff on your side, then when I go into the character creation suite, make it where I can do the hand-tooling part IN the character creation suite — where I don't have to actually use Blender, but Blender's just hooked up in the character creation suite."*
2. *"I'll call that up so it works for all of the models, all the characters, all the parts. They're all interchangeable, deletable, replaceable, addable, movable, resizable, scalable, reshapeable — full Blender-level capabilities."*

INTEGRATION LAW (user, permanent): everything nests into the Tekken menu/system structure as
submenus/subsystems; the mesh-editing tools live inside the creation suite's menu flow (worker 65's
WWE CAW blueprint) — never a parallel editor.

## 1. What already exists in the repo (do not re-invent)

| Proven thing | Where | Relevance |
|---|---|---|
| Headless Blender driver pattern | `tools/auto_rig/backends/gamerig_backend.py` — `blender -b --factory-startup --python script.py -- --in A --out B` | The exact run shape for every mesh-edit op; GameRig backend already drives Blender 4.0.2 this way |
| Blender 4.0.2 install path | `tools/setup/setup_toolchain.sh` → `$PREFIX/blender/blender-4.0.2-linux-x64/blender` | Backend resolves the binary the same way |
| Tool→menu wiring convention | `customization/create-fighter/js/tools.js` — TOOL REGISTRY, `command:` strings like `blender -b --python tools/mb-lab/run_mblab_job.py` | Mesh-edit registers the same way (layer 1 unified + layer 2 per-op) |
| Suite 3D viewer | `customization/create-fighter/js/preview3d.js` — vendored three.js + GLTFLoader, orbit/drag/pinch already | The viewport the editor mode attaches to |
| Vendored three addons | `customization/create-fighter/vendor/addons/{loaders,utils}/` — GLTFLoader, BufferGeometryUtils, SkeletonUtils | TransformControls slots into the same vendor dir |
| Tripo auto-intake | `tools/tripo-intake/` — claim → sha256 → ledger → rig → validate; source GLBs never modified | Same immutability rule: mesh-edit jobs never overwrite source GLBs; outputs are new files + an edit manifest |
| mcp-for-blender eval | `tools/mcp/README.md` — MCP server verified, but the Blender addon's socket server **refuses `--background`** ("commands would never execute — run Blender with a GUI") and this VM has no EGL/libEGL | MCP is the *agent* lane, not the suite lane. The suite lane is headless `--python` jobs, which work on any server |

## 2. Tool survey (touch-first 3D editing + headless Blender)

### three.js TransformControls — CHOSEN for the in-suite gizmo
- `attach(object)` / `detach()` / `setMode('translate'|'rotate'|'scale')`; gizmos: arrows (translate), circles (rotate), handles (scale). Dispose removes "all mouse and touch event listeners" — pointer-event based, so it works with touch. (Sources: threejs-editor DeepWiki pages; webcodingcenter.com add-ons list.)
- The vendored three.js in `create-fighter/vendor/` predates a vendored TransformControls; we vendor the matching version from the same three release as `vendor/three.module.js` (license MIT, same as three). The suite already pins three locally, so no CDN risk.
- Touch caveat: gizmo handles are small on phones. Prisma3D-style answer: a fat-finger-safe selection + axis-lock UI (big axis buttons under the viewport) rather than relying on hitting 6px handles. Documented as a UI requirement in the decision doc.

### Prisma3D (Android, 10M+ installs, proprietary) — UX REFERENCE ONLY, not embeddable
Feature list confirms the right capability surface for a touch-first modeler:
position/rotation/scale tools, vertex/edge/face modeling "very similar to Blender's workflow",
digital drawing, 3D sculpting, mesh creator, grouping multiple models, rigging/skinning,
keyframe timeline, import/export `.obj .fbx .gltf .stl .ply`. (play.google.com listing,
updated 2026-09-21.)
What we steal: the interaction vocabulary — object list → tap select → big touch-friendly
transform tools → simple numeric nudge for precision. What we don't: the app itself.

### Blockbench (GPL-3.0) — evaluated, REJECTED for embedding
Free/open-source web-capable low-poly editor (blockbench.net, github.com/CoralRP/blockbench).
Wrong target: cuboid/low-poly Minecraft-style modeling, not skinned character GLBs. Its *plugin*
pattern (JS plugins extending a core editor) is the right shape and mirrors our tools.js registry.

### MeshySmith (AGPL-3.0) — evaluated, REJECTED for embedding
Tinkercad-loop web editor with Manifold booleans (meshysmith.com). AGPL-3.0 makes embedding
into our MIT-ish game repo a license hazard. Booleans via Manifold remain a valid *Blender-side*
technique (Blender's own boolean modifier) — no dependency needed.

### blender-remote (PyPI, MIT-ish packaging) — PATTERN reference
Headless automation via `blender --background` + temp script file + subprocess with timeout and
stdout/stderr parsing (same flow documented in threedle/ll3m `blender/headless.py`). Our job
server uses this flow directly with our own op scripts — no new dependency.

### Daz Studio-type viewers — pattern reference
Daz's accessibility win is *named part selection + sliders*, not 3D gizmo skill. Our editor
keeps the same dual path: (a) tap-to-select + gizmo for spatial people, (b) a named part list
(worker 64's mesh taxonomy) + numeric sliders/buttons for everyone else. Both drive the same
job queue.

## 3. Capability → execution layer matrix (drives the decision doc)

| Capability | In-suite (instant, three.js) | Blender job (baked) |
|---|---|---|
| show / hide mesh | ✅ visibility flag in edit manifest | — (manifest is data, no job) |
| delete mesh | ✅ soft-delete flag (reversible) | hard delete → new GLB (`mesh_delete`) |
| move / rotate / scale (uniform + non-uniform) | ✅ gizmo + numeric nudge, live preview | bake → new GLB (`mesh_transform`), skin weights preserved (object-space op) |
| interchange (swap part between characters) | pick source part in catalog | `part_import`: import donor GLB mesh, fit to socket, bake → new GLB |
| add part | — | `part_import` (from suite parts catalog or uploaded GLB) |
| reshape (vertex sculpt) | brush *preview* only | `mesh_sculpt`: Blender sculpt with brush params (grab/smooth/inflate), bake → new GLB + **re-weight pass** |
| reshape (remesh/subdivide/decimate) | — | `mesh_remodel` (modifier stack: remesh, subdivision, decimate) + re-weight pass |
| reshape (vertex-group mask edit) | — | `weights_paint` via GameRig weight-transfer, reuse of `tools/anim/repair_sleeve_weights.py` k-NN approach |

Honest boundary: geometry-changing jobs **invalidate skin weights**; every reshape job ends
with an automatic weight-transfer/validation pass (same gate as tripo-intake). Delete/transform/
visibility never touch weights and are near-instant.

## 4. Teardown-file editing patterns consumed

- **Tekken teardown (T3 motion/anim pipeline):** op scripts are data-driven (`--in/--out` flags,
  JSON sidecars) — mesh ops follow the same contract: `mesh_edit.py --op <op> --job job.json --out result.glb`.
- **WWE/Def Jam CAW teardown (parts catalogs):** parts are addressed by library+id+slot
  (`customization/PARTS-REGISTRY.json`, `parts-catalog.json`). The `part_import` op addresses
  donors the same way, so suite catalog entries drop straight into jobs.
- **Def Jam honest-state pattern** (`DEFJAM-CAW-WIRING.md`): parts with unproven geometry ship
  `geometry_pending: true` and the UI says so. Same rule here: any op whose result hasn't passed
  the validation gate is badged `bake_pending` in the manifest and the suite shows it as pending,
  never as finished.

## 5. Risks / open questions

1. **Blender not installed on this VM** — `tools/setup/setup_toolchain.sh` handles install; the
   backend must degrade cleanly (queue jobs, mark `backend_unavailable`) when the binary is absent.
2. **Phone GPUs + heavy GLBs** — the suite viewer already handles roster GLBs; edit mode adds one
   gizmo, negligible cost. Blender jobs run server-side, never on the phone.
3. **Worker 64 (clothing-layer taxonomy) and worker 65 (WWE CAW menu blueprint) have not landed
   in main yet** — the integration contract is documented in the decision doc (mesh-id naming,
   menu nesting point) so their landings slot in without rework.
4. **Undo** — every edit is a manifest entry (JSON) on top of immutable sources; undo = drop
   entries. Hard-baked GLBs are versioned outputs, never overwrites.
