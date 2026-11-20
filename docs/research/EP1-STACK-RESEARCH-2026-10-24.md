# EP1 Open-Source Stacking Research — Game-Facing — 2026-10-24

**Scope note.** This is the game-facing half of Track F (open-source stacking
research + wiring) for Episode 1 "Immortal Qombat". The show-facing half
(SKEL rig-quality checklist for show rigs, Flamenco job setup) lives in
cape-jones `docs/research/EP1-STACK-SHOW-2026-10-24.md`. A similarly named
cape-jones file, `TRACK-F-PULL.md`, is an older merch/community track — it is
a different track and is not this work.

**Shared-pipeline rule (owner scope clarification, 2026-10-24).** This stack
serves BOTH the game and the show as one shared pipeline, not a show-only
fork: anatomy layers feed the game's X-ray/creation suite AND the show's
presentation from the same layer data, and rig checks apply to both rig
sets. Show is the current focus; game wiring is in scope and is reported
separately. In-show naming: inside Episode 1 the game is IMMORTAL QOMBAT,
never "Western Heart" — that rule governs show-facing docs and assets; this
game-facing technical doc uses the repository name only where it identifies
the game repo.

**What this document does and does not do.** It evaluates six stack pieces,
states each one's license from a source actually read, and says what is
pullable vs. methods-only vs. study-only. It builds on — and does not redo —
two 2026-10-23 findings: (a) Purdue Dissectible Anatomy (methods only, no
public code for the splat/SDF layer) and (b) the Human Atlas three-dataset
stack (license verdicts already settled in
`docs/research/ANATOMY-DATASETS-2026-10-23.md`). Where this document repeats
a settled verdict it says so and cites the prior doc, not a fresh re-verdict.

**Honesty rule for this document.** Nothing below is described as "wired"
unless it is a file in this PR that was actually written and, where it is
code or data, actually run. The wiring in this PR is: the layer-stack map
(`tools/anatomy/stack_layers.json`) plus its validator
(`tools/anatomy/validate_stack_layers.py`), and the wiring spec in
`docs/research/ANATOMY-STACK-WIRING-2026-10-24.md`. No game runtime code was
changed, no third-party mesh was bundled, and no farm was stood up.

## Verdict table

| Piece | License (source read) | Status for the game |
|---|---|---|
| Purdue Dissectible Anatomy / Gram-Schmidt voxel method | MIT code for the voxel-fracture core (`DestructibleVoxelSystem`); NO public code for the splat/SDF anatomy layer | **Methods-only for the anatomy layer; MIT code pullable for the fracture core.** See §1. |
| Human Atlas three-dataset stack | BodyParts3D 4.0: CC BY 4.0 (GO, with attribution). Z-Anatomy: CC BY-SA 4.0 (NO-GO for shipped assets). HuBMAP HRA 3D organs: CC BY 4.0 (GO, with attribution). | **Pullable where CC BY 4.0; study-only where CC BY-SA.** Already partially wired (X-ray/organ layer/skeleton variants); §2 gives the next layer. |
| Somakine | Framework code: MIT. BodyParts3D data pack: CC BY 4.0 (NOT relicensed as MIT). | **Pullable.** MIT code may enter `game/` with its notice; the data pack keeps its own CC BY 4.0 attribution. See §3. |
| LearnAnatomy3D | No public source repo found; site is free to use, not open-source code. Its datasets include CC BY-SA 4.0 material. | **Methods-only.** Copy the rendering techniques, never lift its merged geometry. See §4. |
| SKEL (MPG) | Project site: "available for research". MPG sibling model licenses (SMPL/SMPL-X, read) allow non-commercial research/education/art only, prohibit commercial incorporation and distribution. SKEL's own gated download license was NOT directly read. | **Study-only / NO-GO for shipped assets.** Use its joint-placement findings as a rig-quality checklist only. See §5. |
| Blender Flamenco | GPLv3+ (GPL 3.0 on the project site). | **Tool-only, never embedded.** Run it as a separate render-farm process; do not copy its code into `game/` runtime. See §6. |

## 1. Purdue Dissectible Anatomy — methods-only (anatomy layer), MIT code (fracture core)

**What it is.** Tim McGraw (Purdue IGT Lab) + Jack Myers, presented live at
SIGGRAPH 2026 Real-Time Live! (Audience Choice). It converts color
cryosection imagery (e.g. Visible Human Project data) into deformable models
that can be cut, torn, retracted, and separated in real time. The mechanism,
from the prior 2026-10-23 research (workspace reports
`dissectible-anatomy/research-report-mcgraw.md` and
`research-report-pbd-impls.md`, not re-researched here): position-based
dynamics (PBD) particles with **no fixed mesh connectivity**, volumetric
splats at 4× the particle-grid resolution carrying color/texture, a per-splat
signed distance field (SDF) updated at runtime, and fracture via SDF boolean
operations (cut = move splats between regions; only the outer shell of splats
is drawn). Technical foundation: McGraw's MIG 2024 paper "Gram-Schmidt Voxel
Constraints for Real-Time Destructible Soft Bodies" (DOI
10.1145/3677388.3696322) and the Computers & Graphics 2025 extension.

**What is actually public.** One repo, and it is NOT the anatomy layer:
`github.com/brohaooo/DestructibleVoxelSystem` — the voxel-fracture core
(C++/OpenGL 4.6 compute shaders), MIT-licensed (copyright 2025 Lin Xinhao,
per its LICENSE file, verified 2026-10-23). There is **no public code, no
downloadable mod, and no stated release plan for the Dissectible Anatomy
splat/SDF layer itself** — McGraw's own words in the 80.lv interview were
"all we have right now is a demo of a technique."

**What it plugs into.** Two separate plugs, do not conflate them:
- (a) **Fracture core (pullable, MIT):** the VGS voxel constraint and
  breakable face-constraint shaders are the starting point for destructible
  props / creature dismemberment in the game, and for over-the-top finisher
  VFX. MIT code may enter the game with its copyright notice kept.
- (b) **Anatomy splat/SDF layer (methods-only):** implement FROM the
  published methods if an X-ray/dissection interior ever needs true
  cuttable volume instead of the current analytic-SDF-proxy layers. The
  game's existing layer system (`wh.anatomy-layers/2`, analytic SDF
  primitives, ~50 KB JSON per character) is already the shippable,
  procedural version of this idea — it deliberately uses no cryosection
  data. The splat/SDF layer is a future rendering upgrade for that system,
  not a replacement for its data model. See the wiring spec §2.

**Do NOT claim:** that Purdue's anatomy code can be pulled in. It cannot —
it is not public.

## 2. Human Atlas three-dataset stack — settled verdicts, next layer

**What it is.** The stack behind a DeepMind anatomy post the owner shared:
BodyParts3D 4.0 + Z-Anatomy + HuBMAP HRA 3D organs, unified by the Open 3D
Man Project / Human Atlas (`github.com/ashemag/human-atlas`, 2,234 selectable
meshes, 15 systems, 3,432 named concepts). Verified this round from the
repo itself (README + `public/ATTRIBUTION.md`, read via API 2026-10-24):
the viewer is React + Three.js, geometry is merged into batches with
per-structure GPU textures controlling translation/visibility/selection
without a draw call per structure, and the packaged model is 2,288,268
triangles in ~33 MB compressed geometry. The repo's own code license is MIT
(verified from its LICENSE file via API).

**License verdicts (settled 2026-10-23, corroborated this round, not
re-opened).** Full analysis in `ANATOMY-DATASETS-2026-10-23.md`:
- **BodyParts3D 4.0 — CC BY 4.0, GO with attribution.** The current LSDB
  Archive license page (updated 2025-02-27) states CC BY 4.0 with the
  attribution line "BodyParts3D, © The Database Center for Life Science
  licensed under CC BY 4.0 International". The Human Atlas ATTRIBUTION.md
  (read this round) states the same and explicitly addresses the old
  header text: "Source OBJ comments mention an older CC BY-SA 2.1 Japan
  license. The official current database license linked above supersedes
  that legacy text." **Crew rule that follows:** use only current-archive
  4.0 downloads, and keep the per-file check in the validator — any mesh
  whose own header still says BY-SA 2.1 JP is flagged, not silently shipped.
- **Z-Anatomy — CC BY-SA 4.0, study-only, NO-GO for shipped game assets.**
  Corroborated this round (SPI project page: "It is CC-BY-SA 4.0
  licensed"). Share-alike would contaminate game assets. Study its
  labeling/hierarchy ideas; never bundle its geometry.
- **HuBMAP HRA 3D organs — CC BY 4.0, GO with attribution.** Corroborated
  this round (HuBMAP data portal terms: published data under CC BY 4.0;
  HRA reference-organ sets, e.g. female v1.5, CC BY 4.0). This is the
  candidate for first mesh integration where BodyParts3D coverage is thin
  (notably female anatomy — BodyParts3D is male-only).

**Already wired (do not redo).** Per the task brief and the prior docs: the
X-ray system fires on Rage Art / Urge Smash KO blows, there is an organ
layer (`wh.anatomy-layers/2`), and skeleton variants exist for non-human
fighters (extra arms, shell/tail, etc.). The wiring spec §3 gives the NEXT
layer: schema v3 mesh references (already specified in
`ANATOMY-DATASETS-2026-10-23.md` §4) gated by the new
`tools/anatomy/stack_layers.json` allow/block list, so a mesh can only be
referenced if its dataset is on the allow-list with license + attribution
filled in.

## 3. Somakine — pullable (MIT code + CC BY 4.0 data pack, kept separate)

**What it is.** Somakine (`github.com/ivershuo/somakine`, "The open body
framework") is an open-source TypeScript/Three.js anatomy framework. From
its README and repo tree (read via API 2026-10-24): a framework-neutral
core (`packages/core`: canonical anatomy IDs, many-to-many regions, data-pack
validation, deterministic catalog queries, coverage contracts) plus a
Three.js viewer (`packages/viewer`: demand-driven loading, bounded
concurrency, styling, occlusion-aware picking, exploded layouts, structure
dragging, focus/reset), React and Vue integrations, a CLI, and data packs
(`data-packs/bodyparts3d-musculoskeletal` using real BodyParts3D 4.0
musculoskeletal geometry, and a synthetic `musculoskeletal-basic` starter
pack of generated primitives). The Playground toggles layers for bones,
muscles, joints, ligaments, and tendons, filters by region, and does
side-aware semantic selection.

**License (verified from the repo itself).** LICENSE file via API: MIT,
copyright 2026 Somakine contributors. The NOTICE file (read via API) is
explicit and is the whole license story: framework code is MIT; the
`@somakine/bodyparts3d-musculoskeletal` data pack "includes modified
geometry originating from BodyParts3D, © The Database Center for Life
Science, licensed under Creative Commons Attribution 4.0 International",
its public directory carries exact attribution, license URL,
transformation record, upstream/derived manifests, byte counts, and SHA-256
digests, and "that data pack is CC-BY-4.0 and is not relicensed under the
framework's MIT license." The synthetic starter pack is MIT but "must not be
presented as medical anatomy."

**What it plugs into (game).**
- **Creation-suite layer system (direct fit):** Somakine's layer taxonomy
  (bone / muscle / joint / ligament / tendon) maps onto WH layers in the
  wiring spec §4: bone→bone, muscle→muscle, joint→bone-joint metadata,
  ligament/tendon→muscle-group attachments. Its canonical-ID + region model
  is the pattern for naming WH layer groups so the creation suite, X-ray,
  and future dissection views share one vocabulary instead of three.
- **X-ray / dissection viewer techniques:** demand-driven loading with
  bounded concurrency (mobile-safe), occlusion-aware picking (tap the
  visible structure, not the one behind it), exploded layouts (the Human
  Atlas trick, also in Somakine's viewer), and data-pack provenance
  contracts (source + license + attribution + digest per pack). The
  wiring spec turns each into a concrete X-ray enhancement with the
  fallback rule: proxies render when a mesh is absent.
- **License firewall respected:** MIT viewer/core code may be adapted into
  the game with its notice; the BodyParts3D data pack enters only via the
  schema-v3 mesh-reference path with its CC BY 4.0 attribution intact —
  never as unmarked geometry.

**What is NOT claimed:** that Somakine was run or its viewer embedded in
this PR. It was read (README, NOTICE, LICENSE, package/tree layout), not
installed or integrated into runtime code. The wiring spec is the
integration plan; the validator is the gate that makes the data-pack path
enforceable.

## 4. LearnAnatomy3D — methods-only (no public repo found)

**What it is.** LearnAnatomy3D (learnanatomy3d.com) is a free 3D human
anatomy atlas in three.js + react-three-fiber: male and female bodies,
~2,900 clickable structures across 11 systems, layer-by-layer dissection,
cross-section cutting, guided tours/quizzes, 14 languages, phone-friendly.
From the author's own three.js-forum post (2026-10-17) and dev article
(2026-10-16), both read this round: anatomy from open datasets (Z-Anatomy,
BodyParts3D, Human Reference Atlas), packed into gzip'd binary chunks and
streamed in two passes (body surface first, full anatomy after).

**License / pullability — the important distinction.** No public source
repository for LearnAnatomy3D was found in targeted searches this round;
"free to use" on the web is not an open-source license, and its merged
geometry blends datasets including CC BY-SA 4.0 Z-Anatomy material. So:
**nothing is liftable from LearnAnatomy3D — neither code nor geometry.**
What IS usable is its published rendering technique, described by the
author in enough detail to reimplement cleanly:
- One merged mesh per system and material; per-structure visibility and
  highlight via a small data texture indexed by a part-index vertex
  attribute, so selection never re-merges geometry.
- Cross-section via a single persistent clipping plane per material,
  parked far away when off, so cutting never recompiles shaders; a stencil
  "body-volume" mask keeps inner anatomy from showing outside the skin.
- `compileAsync()` before models join the scene and `checkShaderErrors`
  off in production, so loading does not block the main thread
  (author-reported: main-thread blocking ~13.6 s → ~4 s; longest freeze
  ~7.3 s → ~1.5 s; body switch ~0.1 s — author's numbers, not ours).
- Realistic character bodies fitted onto the anatomy with custom
  Node/Blender tooling (TPS warps, cloth simulation for clothes) — the
  pattern for fitting atlas anatomy onto WH fighter bodies, not a tool to
  pull.

**What it plugs into (game).** The wiring spec §5 maps each technique onto
the X-ray system: part-index data texture for KO-blow highlighting,
persistent clipping plane for the cross-section/cut view, stencil mask for
the skin shell, two-pass streaming for creation-suite load. All four are
technique reimplementations in our own code — no LearnAnatomy3D asset, and
no Z-Anatomy-derived geometry, enters the repo through this path.

## 5. SKEL — study-only (research license; checklist, not assets)

**What it is.** SKEL (Keller, Werling, Shin, Delp, Pujades, Liu, Black,
ACM Transactions on Graphics 42(6), Article 253, Dec 2023, DOI
10.1145/3618381) re-rigs the SMPL body model with a biomechanics skeleton.
From the project site (skel.is.tue.mpg.de, read this round): SKEL is built
by fitting a full-body biomechanical skeleton model (BSM, OpenSim format)
to SMPL mesh sequences from AMASS, learning a regressor from SMPL mesh
vertices to optimized joint locations and bone rotations, then
re-parametrizing the SMPL mesh with the new kinematic parameters. Result:
animatable like SMPL but with fewer, biomechanically-realistic degrees of
freedom — knee flexion, arm supination, scapula sliding, forearm twisting
are called out on the site — with joint locations more accurate than SMPL
and bones fitting inside the body surface better than previous methods.
Code offered: a SKEL loader, SMPL2AddBiomechanics fitting support code, and
an ait-viewer-based SKEL viewer; data offered: SKEL and BSM models plus the
BioAmass dataset, via the site's Download tab.

**License — why this is NO-GO for shipped assets.** The SKEL site says the
model, code, and data are "available for research". SKEL's own download
license sits behind the site's gated Download tab and was NOT directly
read this round — so this document does not quote it. What WAS read: the
MPG standard model licenses for sibling models SMPL and SMPL-X, which grant
a single-user, non-exclusive, non-transferable right for non-commercial
scientific research, non-commercial education, or non-commercial artistic
projects only, and prohibit commercial incorporation, commercial services,
production of commercial artifacts, and any distribution to third parties
without Max Planck's prior written permission. SKEL is distributed through
the same MPG system (registration-gated download, same model family). The
conservative, correct verdict is therefore: **treat SKEL exactly like
SMPL — research-only, do not download-and-ship, do not bundle SKEL/BSM
meshes or parameters into the game or the show's shipped assets, and do
not feed SKEL .osim data into `tools/anatomy/osim_to_anatomy.py`** (that
converter exists for other OpenSim sources; SKEL's license bars this use).
If the owner ever wants SKEL assets themselves, that needs Max Planck's
prior written permission — an OWNER-NEEDED item, not something this track
can grant itself.

**What it plugs into (game + show) — the checklist, not the model.**
SKEL's findings are still valuable as a rig-quality audit standard, and
that use (reading the paper's conclusions, applying them as checks to our
own rigs) does not ship SKEL assets. The checklist, with its show-facing
twin in the cape-jones doc:
1. Joint locations: are knees/elbows/shoulders at true anatomical centers,
   not at the simplified SMPL-style joint guesses?
2. Scapula: does the shoulder blade slide on the ribcage with arm raise,
   or is it rigidly parented?
3. Forearm: does the forearm twist (pronation/supination) along its axis
   instead of rotating as a rigid stick?
4. Knee: is flexion a clean hinge axis, without the mesh collapsing or
   the bone poking through the surface at full bend?
5. Bones-inside-surface: at extreme poses, does every bone stay inside
   the skin mesh?
6. Degrees of freedom: are joints limited to anatomically realistic
   ranges, so mocap retargets do not produce impossible poses?
Each check is applied to WH's own rigs and to show rigs; a failed check is
fixed in our own rigging, never by importing SKEL parameters.

## 6. Blender Flamenco — tool-only (GPLv3+), render-farm pointer

**What it is.** Flamenco is Blender's own open-source render-farm manager
(Blender Studio, in production use there). From the project site and docs
(read this round): two single Go binaries — Flamenco Manager (the brain:
job queue, web dashboard, splits jobs into tasks) and Flamenco Worker (the
muscle: polls the manager, launches Blender in the background, reports
progress). Core built on Go + SQLite, cross-platform, self-hosted, no
database server or Kubernetes required. Jobs are frame ranges cut into
chunks; idle workers grab the next chunk (fast machines naturally do more);
failed tasks retry on a different worker, and a worker is blocklisted for a
job after three failures on it. Job types are specified in JavaScript so
TDs can fit it into a pipeline. It supports any Blender render engine and
progressive Cycles renders (frames split across workers by sample count,
then merged). Downloads + Blender add-on at flamenco.blender.org; source
at `https://projects.blender.org/studio/flamenco.git` (public read-only
clone per the getting-started docs).

**License (verified).** GPL 3.0 on the project site ("Released under GPL
3.0, every component"); the source README (via pkg.go.dev) states
"Flamenco is licensed under the GPLv3+ license", and source files carry
SPDX `GPL-3.0-or-later`.

**License firewall — how Flamenco may and may not be used.** Flamenco is a
standalone tool, not a library: running it as separate Manager/Worker
processes to render `.blend` files does not make the game, the show, or
the rendered frames GPL — the GPL covers the Flamenco program itself, and
its output (frames) is not its code. What the firewall forbids is copying
Flamenco code into `game/` runtime (or into shipped show code). Custom
Flamenco job-type scripts, if the crew writes any, live in `tools/`, never
in `game/`. No Flamenco code is included in this PR — only a job-template
pointer (cape-jones doc + example JSON), because farm setup and
measurement belong to the separate render-pipeline track. This track does
not duplicate that track's measurement work and makes no throughput claim:
no farm was run here.

**What it plugs into.** Show production only (Blender rendering for Ep 1
shots), via the render track. It does not plug into the game runtime at
all. The cape-jones doc gives the concrete job shape: one job per shot,
frame-range chunks, shared file storage all workers can reach, simulations
baked centrally before submission (otherwise workers diverge), identical
Blender/add-on versions on every node.

## Sources actually read (2026-10-24 unless noted)

- Somakine repo via GitHub API: README, LICENSE (MIT), NOTICE, package
  tree (`packages/core`, `packages/viewer`, `data-packs`), three.js-forum
  announcement post. `github.com/ivershuo/somakine`.
- Human Atlas repo via GitHub API: README, LICENSE (MIT),
  `public/ATTRIBUTION.md`, `scripts/` tree. `github.com/ashemag/human-atlas`.
- LearnAnatomy3D: author three.js-forum post 2026-10-17; author dev
  article 2026-10-16 ("Rendering a 2.9-million-triangle human body…").
  No public source repo found after targeted search.
- SKEL: project site skel.is.tue.mpg.de (abstract, code/dataset
  description, citation); MPG SMPL + SMPL-X model-license pages (standard
  non-commercial terms quoted in §5). SKEL's gated download license NOT
  read — flagged, not quoted.
- Flamenco: flamenco.blender.org (features/GPL 3.0, about, download,
  getting-started incl. clone URL), pkg.go.dev mirror of the source README
  (GPLv3+), Blender Studio Flamenco 3 announcement.
- Z-Anatomy license: SPI project page ("CC-BY-SA 4.0 licensed").
- BodyParts3D current license: LSDB Archive license page (updated
  2025-02-27, CC BY 4.0) via Human Atlas ATTRIBUTION.md corroboration;
  prior WH doc `ANATOMY-DATASETS-2026-10-23.md` §2 (settled verdict).
- HuBMAP HRA: HuBMAP Data Portal data-use terms (published data CC BY
  4.0); HRA reference-organ sets (female v1.5, CC BY 4.0) per Human Atlas
  ATTRIBUTION.md historical-assets section.
- Purdue: prior workspace reports `dissectible-anatomy/research-report-mcgraw.md`
  and `research-report-pbd-impls.md` (2026-10-23) — relied on, not redone.
- Prior WH docs read: `ANATOMY-LAYERS-SPEC-2026-10-23.md`
  (`wh.anatomy-layers/2`, Pantera proof fighter),
  `ANATOMY-DATASETS-2026-10-23.md` (§3 skeleton variants, §4 schema v3).

## What was NOT verified (open items, not hidden)

- SKEL's own download-license text (gated) — verdict is conservative by
  design; see §5 and OWNER-NEEDED in the coordinator report.
- LearnAnatomy3D's code license — there is no public repo to license;
  treated as methods-only.
- No Somakine/Flamenco software was installed or run in this PR; no
  render throughput, phone performance, or X-ray frame cost is claimed.
- No third-party mesh was downloaded, converted, or bundled in this PR.
