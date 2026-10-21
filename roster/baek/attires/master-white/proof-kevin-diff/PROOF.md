# PROOF — Master White differentiated toward KEVIN (Creation Suite Pass, Worker D)

**Attire:** `roster/baek/attires/master-white/` — "Master White, differentiated
toward Kevin." This is NOT a Kevin replacement: Kevin IS the fighter, his face
is his Tripo model (`roster/baek/attires/attire1/model.glb`, unrigged static,
reference only). Master White stays a parked-weak attire on Baek's Tekken
model; this pass measures how far the landed Creation Suite machinery can push
it toward Kevin.

**Verdict (own eyes, three-way: BEFORE / AFTER / Kevin reference):**
He DOES read as a different person than Baek after the bake — slimmer build,
narrower shoulders and jaw, thinner neck, softer and younger face. He does NOT
yet read as Kevin. The morph layer differentiates for real; the hair/beard
layer only partially lands (white-gray parts, partial cap coverage, low-sitting
beard), and Kevin's skin tone could not be applied at all. What is missing for
full Kevin is named, item by item, under "What's missing" below. No closeness
percentages are claimed — the renders are the evidence.

---

## The three-way comparison (all viewed by the authoring agent)

| | BEFORE (`before_front.png`, `before_head.png`) | AFTER (`after_front.png`, `after_head.png`) | KEVIN (`kevin-ref_front.png`, `kevin-ref_head.png`) |
|---|---|---|---|
| Build | Broad, muscular master; thick neck, wide shoulders | Slimmer torso/arms, narrower shoulders, thinner neck, slight belly kept | Average, soft build, slight belly |
| Face | Wide strong jaw, stern, heavy PAINTED slanted brows, narrow eyes | Narrower oval face, slimmer jaw, softer expression; painted brows remain | Rectangular-oval face, tall forehead, widow's-peak hairline, straight medium brows, deep-set eyes |
| Hair | Slicked-back BLACK hair + ponytail (base texture/mesh) | Base hair still visible (cannot be hidden); gray CC0 buzzed cap sits over the crown, coverage partial | Short dark-brown buzz crop, ears fully visible |
| Beard | Clean-shaven | Gray CC0 beard present at chin/jaw, sits ~2 cm low, reads as a chin beard | Full short DARK beard + mustache, some gray at chin |
| Skin | Tan | UNCHANGED tan (bake could not apply the tone — see gaps) | Light |

## Values used (`roster/baek/attires/master-white/customization.json`)

Body type "Medium 1". Skin tone (suite swatch) `#dba06e`. Hair color intent
`#2a1c10` (Kevin's dark brown).

MPFB morphs (suite BODY sliders; the iteration softened forehead/oval/eye
after the first bake tore a spike into the forehead — see "Iterations"):

| morph | value | morph | value |
|---|---|---|---|
| face_oval | +0.35 | bulk | −0.50 |
| jaw_width | −0.50 | muscle | −0.45 |
| cheekbones | +0.25 | shoulders | −0.35 |
| nose_width | −0.25 | chest | −0.25 |
| nose_length | −0.15 | neck | −0.25 |
| mouth_width | −0.20 | fat | +0.10 |
| forehead_height | +0.20 | belly | +0.15 |
| eye_size | +0.25 | | |

Parts (CC0 / Quaternius, `customization/parts/hair/cc0/`), placements measured
from evaluated bounding boxes and a Kabsch fit against the source files (see
"Machinery findings" — placements are NOT the suite's zero defaults):

| slot key | part | placement |
|---|---|---|
| hair | `cc0-hair-quaternius-buzzed` (Hair_Buzzed.gltf) | px 0, py 0.03, pz 2.12, ry 180, s 1.25 |
| face | `cc0-hair-quaternius-beard` (Hair_Beard.gltf) | px 0, py 0.01, pz 1.91, ry 180, s 1.10 |
| eye | `brow-cc0-regular` (Eyebrows_Regular.gltf) | px 0, py 0.04, pz 1.59, ry 180, s 1.00 |

Eyes: base eyes kept — no eyeball mesh part exists in-repo (documented gap);
no texture eye was painted (owner rejected exactly that). No eyelash mesh
exists either.

## How the record was authored (suite-first, hand-completions disclosed)

Authored by driving the real suite UI (Playwright harness,
`suite_harness.py`): Baek → Master White loaded (real rigged GLB), the morph
sliders set through DOM input events, the `#dba06e` skin swatch clicked, the
brow equipped through the PARTS tab. Hand-authored in the suite's exact v1
format, and why:

1. `base_glb` — the suite emits a repo-relative path; the schema wants the
   in-folder file name (`baek-master-white-rigged.glb`), else the bake joins
   the path twice and aborts.
2. `out_glb` — the suite emits `null`; set to `model-kevin-diff.glb` (the
   name this proof ships).
3. `parts.hair` / `parts.face` — the catalog classifies the CC0 hair/beard as
   `texture_part`, so the suite record cannot emit them as mesh parts (it
   emits the beard under `textures[]` with a .gltf as the "image", and the
   buzzed hair is overwritten by the beard because both share T7 slot 2).
   They were equipped in the UI and are carried here as the mesh parts they
   physically are. The bogus beard-as-texture entry was removed from
   `textures[]`.
4. Brow slot key `eyebrows` → `eye` — the bake's socket table has no
   `eyebrows` key; `eye` is the schema's eye socket on the Head bone.
5. `colors.hair` — the suite has no hair-color control (emits `null`); set to
   Kevin's `#2a1c10` as standing intent (the bake fails it loudly today — see
   gaps).
6. All part placements — computed/measured by this worker (see findings);
   the suite's placement dock exists but the values that land parts on a
   Tekken head are not defaults anyone ships.

Round-trip proof: with the record committed and `customization_json` wired in
`customization/creation-suite-ui/data/roster-attires.json` (it was `null` —
the suite only restores attires whose roster entry declares the file), the
suite restores the record live: all 15 morphs, all 3 equipped parts, skin
`#dba06e` (`suite-report.json`: ok true; screenshots `suite-full.png`,
`suite-controls.png`, `suite-brow.png`). The suite's re-emitted record
(`suite-record.json`) keeps the 15 morphs but re-emits hair/beard under
`textures[]` — the same classification divergence as item 3.

## Bake + game hook

- Bake: `customization/tools/apply_customization.py` on the attire folder.
  All 15 morphs transferred and baked into Basis on all 36 meshes; the 3
  parts bone-parented to the Head bone. Exit code 2 = ONLY the two color
  items failing loudly (below); `model-kevin-diff.glb` written (1,313,048 B)
  and the registry emitted.
- Registry: `game/js/attire-customizations.js` maps
  `'baek-master-white' → '../roster/baek/attires/master-white/model-kevin-diff.glb'`.
- Smoke: `node customization/tools/test_game_hook.mjs` → **SMOKE PASS**
  (103 MODEL_URLS keys; the override resolves to a real file and is applied;
  synthetic-override and empty-registry no-op phases pass). One latent bug in
  the test itself was fixed in this PR: phase 4b captured its baseline from
  the load WITH the real registry applied, so it failed by construction as
  soon as any real override existed; the baseline now comes from a pristine
  empty-registry load.

## Machinery findings (the proof's real payload)

1. **Bake placement rotations were silently ignored (FIXED in this PR).**
   glTF-imported part roots are in QUATERNION rotation mode; the bake set
   `o.rotation_euler = ...`, which does nothing in that mode. Measured
   consequence: every bone-parented part baked with a Kabsch rotation of
   exactly 180° about Y vs its source file (front/back and left/right
   flipped) from the bone-parent conjugation, with no way to cancel it.
   Fix: `o.rotation_mode = 'XYZ'` before assigning, in
   `customization/tools/apply_customization.py`. After the fix the shipped
   cap's Kabsch rotation vs source is identity (probe scripts:
   `kabsch.py`, `kabsch2.py`, `probe_ry180.py`, `render_rotprobe.py`).
   With rotation honored, placement `ry: 180` cancels the conjugation flip;
   the `pz` values above include the rotation-about-origin compensation
   (2·s·(part center height)) because the part pivot sits at its own
   skeleton origin, not at the head.
2. **Colors can't reach this model.** PARTS-REGISTRY has no `baek` character
   mapping and none of Baek's 35 materials is named for hair or skin, so
   `colors.hair` and `colors.skin` fail loudly by design (`CSBAKE ERROR
   [colors.hair]: no material resolved...`). Skin tone is therefore UNCHANGED
   in the bake, and even a mapping could not fix hair color: multiply-tinting
   cannot lighten tan skin or recolor black hair to brown, and the bake's
   color step only iterates base-model materials captured before parts are
   added — **part materials can never be tinted by the bake**, which is why
   the CC0 hair/beard (near-white `T_Hair_1_BaseColor.png`, designed to be
   tinted) bake in light gray. On a young man that reads gray-haired — the
   single biggest likeness blocker after skin.
3. **Catalog misclassification.** The CC0 hair/beard GLBs are real meshes but
   are cataloged `part_class: texture_part` (their PARTS-REGISTRY entries
   carry no part_class; the catalog builder defaulted). Consequences: the
   suite emits them as textures, one T7 slot (2) is shared by hair and beard
   so equipping one evicts the other, and `brow-cc0-regular` — a proper
   `mesh_part` in the catalog — is absent from PARTS-REGISTRY.json entirely
   (catalog-scan only) with no `eyebrows` key in the bake's socket table.
4. **Multi-bone-skinned parts are unstable through the bone-parent path.**
   The buzzed cap (weighted ~entirely to Head) bakes stably and
   deterministically (the pipeline reproduced byte-size-identical output
   across runs: 1,313,048 B). The beard, weighted across the UE skeleton's
   neck/clavicle/spine bones, evaluated into a broken ring at cap s=1.32 /
   beard s=1.18 (`after_head_bake6-ring.png`, `after_front_bake6.png` —
   kept as evidence) and sits ~2 cm low in the shipped configuration.
   Root-cause class: the part keeps its own full skeleton under the base
   Head bone; nothing in the bake re-binds part vertex groups to the base
   rig.
5. **Base hair cannot be hidden.** No schema mechanism suppresses the base
   model's hair meshes/textures, so Baek's black slicked hair and ponytail
   remain under/around any hair part. The heavy brows are PAINTED into
   Baek's face texture (pek1u_12), so mesh brows layer over painted ones
   instead of replacing them.
6. **Suite restore was unwired for this attire** (`customization_json: null`
   in roster data) — fixed in this PR for master-white only.

## Iterations (honest log)

- Bake 1 (suite attempt-1 values, zero placements): morphs differentiated
  body/face immediately; parts landed at his feet (bone-parent origin) and a
  morph spike tore the forehead (forehead_height 0.4 / face_oval 0.45 /
  eye_size 0.3 on a 4,032-vert head). Softened to 0.2 / 0.35 / 0.25 — spike
  gone in all later renders.
- Bakes 2–4: placement tuning from measured evaluated bounding boxes
  (translation mapping Δworld = (−px, +py, −pz)); rendered parts still
  flipped — root-caused to finding 1 via Kabsch.
- Bake 5 (rotation fix + ry 180 + compensated pz): cap orientation exact
  (Kabsch identity); beard coherent but low. **This configuration ships**
  (re-baked as bake 7, byte-size identical).
- Bake 6 (micro-tune: larger scales): beard ring breakage (finding 4) —
  reverted; evidence kept.
- The original pre-compaction worktree for this pass was deleted by an
  external disk process mid-task (the branch was rebuilt in a fresh clone;
  every value above was re-derived or reproduced deterministically — the
  rebake matched the lost bake's byte size exactly).

## Render method notes

- Locked pipeline: `docs/tpose-refs/_tools/tpose_render_cycles.py` (Cycles,
  emission override, white background). The rigged Baek faces −Y, so the
  script's `_side` output is the true front (locked doc's facing-variant
  detection) — `before_front.png`/`after_front.png` are that output;
  `_front` outputs are kept as `*_side.png`. Head close-ups:
  `render_head.py` (same method, head framing, `frontY` camera).
- Kevin's GLB is `EXT_meshopt_compression`, which this Blender cannot
  import; it was decoded with gltf-transform (`copy`) and simplified
  (ratio 0.15, error 0.02) for the reference renders ONLY — the repo file is
  untouched. Kevin faces +X, so his renders use the root-only Rz(180°)
  variant (`render_full_rot180.py`, `render_head.py` rot180 mode); the
  stock faceY variant mangles rigged models and was not used on Baek.
- Suite screenshots come from `suite_harness.py` (Playwright driving the
  real suite UI; SwiftShader viewer).

## What's missing for full Kevin (named gaps, nothing invented)

1. Skin-tone application: a `baek` entry in PARTS-REGISTRY character_mappings
   naming the face/skin materials — and a bake color path that can lighten,
   not only multiply.
2. Part-material tinting in the bake (hair `#2a1c10`), or CC0 hair/beard
   variants with dark textures.
3. A base-hair suppression mechanism in the schema/bake (hide base hair
   meshes when a hair part is equipped).
4. Catalog fixes: CC0 hair/beard as `mesh_part`, a distinct beard slot,
   `brow-cc0-regular` into PARTS-REGISTRY, an `eyebrows` socket in the bake.
5. Multi-bone part re-binding (part vertex groups → base rig) so beards and
   similar parts evaluate stably at any scale.
6. Kevin-specific likeness details with NO in-repo parts: his left-arm
   tattoo sleeve, his wristwatch, widow's-peak hairline geometry (MPFB
   morphs transfer surface deltas onto the Tekken head; they cannot carve a
   hairline), eyelash meshes, eyeball mesh parts (documented suite gap).
7. MPFB morph strength on a 4k-vert Tekken head is a blunt instrument —
   the face reads younger/narrower, not Kevin-shaped; a Kevin likeness pass
   ultimately needs the Tripo head's proportions transferred, which no
   landed tool does.

## Files in this proof pack

`PROOF.md` (this file) · `before_front.png` `before_side.png`
`before_head.png` `before_report.json` · `after_front.png` `after_side.png`
`after_head.png` · `after_head_min.png` (Principled-material close-up of the
same shipped bake, `render_min.py` — no emission override) ·
`after_front_bake6.png` `after_head_bake6-ring.png`
(bake-6 evidence) · `kevin-ref_front.png` `kevin-ref_head.png` ·
`suite-full.png` `suite-controls.png` `suite-brow.png` `suite-report.json`
`suite-record.json` · render/bake logs (`before_render.log`,
`after_render.log`, `kevin_render.log`) · helper scripts (`render_head.py`,
`render_min.py`, `render_full_rot180.py`, `render_rotprobe.py`, `kabsch.py`,
`kabsch2.py`, `probe_ry180.py`, `suite_harness.py`).
