# FACE-SCAN / PHOTO-TO-3D-FACE — 2026 SOTA Research for the WH Creation Suite

**Date:** 2026-10-23
**Lane:** Research only — no game code. Build phase is a separate lane.
**Owner directive:** "let's continue to research and pull stuff in related to all those areas"
**Project law this serves:** TOOL-TO-MENU WIRING LAW (every tool wired into the suite's actual menus, never standalone scripts), DISPLAY ORDER LAW (Tripo models first; face-scan is a *template/authoring* input, not a display override), and the standing creation-suite base (WWE-style template flow, nothing hand-tooled).

---

## 0. TL;DR — the five things worth wiring in

| # | Tool | What it gives us | License | CPU / API viability |
|---|------|------------------|---------|---------------------|
| 1 | **GNM Head** (google/GNM) | Apache-2.0 parametric head+face: identity/expression/pose, eyeballs, teeth, tongue; 17,821 verts; NumPy/JAX/PyTorch/TF backends; region masks for per-part control | **Apache 2.0** ✅ | **CPU-viable** (NumPy backend; photo→param fitting is DIY optimization) |
| 2 | **MediaPipe Face Landmarker** (+ canonical face mesh) | 468/478 3D landmarks + blendshapes from 1 photo, TFLite, Apache 2.0; drives landmark-fit onto GNM/FLAME and WWE-style photo→texture projection | **Apache 2.0** ✅ | **CPU-viable** ✅ (this is the landmark engine for the whole pipeline) |
| 3 | **MPFB 2** (MakeHuman Plugin for Blender 2) | Deepest per-part morph sliders (nose/eyes/mouth/ears/jaw…) with **CC0 assets** — MakeHuman team's explicit stance: generated models are yours, no copyleft on output | Code GPLv3 / **assets CC0** ✅ | **CPU-viable**, Blender-headless friendly |
| 4 | **FLAME 2023 Open** (+ Blender add-on, fitting frameworks) | Industry-standard face model, now open-licensed; MICA/EMOCA/RingNet fitting code exists | **CC-BY-4.0** ✅ (attribution only) | CPU-viable (slow); GPU helps |
| 5 | **KeenFace API** (KeenTools, launched Oct 2026) | Photos → production-ready heads in MetaHuman topology, 4K PBR maps, browser + REST API, pay-as-you-go w/ free starter credits | Commercial (paid credits) | **API lane** — zero local GPU needed |

**Flagged / deprioritized:** MB-Lab and CharMorph (AGPL data → generated models inherit AGPL copyleft — incompatible with a commercial game); DECA (PS License 1.0, research-only flavor — usable as reference, not as a shipped dependency); 2026 diffusion head generators (FaceLift, SplatShot, Any3DAvatar — SOTA quality but output Gaussian splats, not rigged game meshes; research lane, not wiring lane).

---

## 1. What WWE 2K's "face scan" actually is (and why this matters)

The user asked for "photo-to-3D-face like WWE 2K face photos/scans." Researching how WWE 2K's Face Photo Capture actually works reveals an important design split:

**WWE 2K does NOT do photo→3D-geometry.** Its pipeline is **photo→TEXTURE on a template head**:

1. Player uploads a square selfie (512×512 recommended) via the 2K website / linked mobile device → Community Creations → Image Manager.
2. In Create-A-Superstar: pick a **face template** closest to the head shape → **Face Photo Capture** → the photo is projected as the face **texture**.
3. Player then **manually aligns eyes, nose, mouth** to the photo and edits face sliders to match proportions.

**Implication for our suite:** "WWE-style face import" = two separable features we can build with open tools:
- **(a) Texture lane (WWE-equivalent, cheap):** landmark-detect the photo (MediaPipe), warp/project it onto the head template's face UV region, ship as the face texture. This is exactly what WWE does and is 100% CPU-viable.
- **(b) Geometry lane (better than WWE):** fit the photo to a parametric head (GNM/FLAME) to actually move the *geometry* toward the person's face, then optionally drape the photo texture on top. WWE never did (b) — we can.

Recommendation: build (a) first (WWE parity, days not months), then (b) as the differentiator.

Prior art for (b)-style semi-manual fitting: KeenTools **FaceBuilder for Blender** (2020) — pin-based photo fitting of a head mesh. Its automated successor **KeenFace** (keenface.ai, launched Oct 2026, per AWN) now does it via browser/API in MetaHuman topology.

---

## 2. 2026 SOTA: photo → 3D face, open-source landscape

### 2.1 GNM Head — the preferred Apache-2.0 parametric head (NEW, 2026)

- **Repo:** https://github.com/google/GNM (created 2026-03-23; ~1,600 stars; technical report 2026-07-28, arXiv 2607.23687)
- **License: Apache 2.0** — commercial-safe, no attribution games beyond the license text.
- **What it is:** Google's successor-generation 3DMM. GNM Head = statistical head/face geometry with disentangled identity / expression / pose, **17,821-vertex topology**, and — unlike FLAME — built-in **internal anatomy: eyeballs, teeth, tongue**, plus a 4-joint head/neck skeleton with skinning weights.
- **Backends: NumPy, JAX, PyTorch, TensorFlow.** The NumPy backend is the key fact for us: the parametric model evaluates on **CPU with zero GPU dependency**.
- **Per-part control:** semantic parameter sampling + normalized **region masks** (a community browser demo at huikku.github.io/gnm-head-studio exposes the region randomizer and semantic expression presets from the real model).
- **Photo-fit status (honest):** the repo ships the *model* + CI; the "perception stack" (photo→parameters) is on Google's stated roadmap, not yet released. Fitting a photo to GNM today = our own optimization loop: detect MediaPipe landmarks → optimize GNM identity/expression params to match (differentiable with JAX/PyTorch, or plain SciPy on the NumPy backend). Feasible, but it is **our build work**, not a turnkey script.
- **Why it's #1:** only 2026-SOTA head model that is simultaneously Apache-2.0, CPU-evaluable, and anatomically complete (eyes/teeth/tongue matter for a fighting game's close-up intros and win poses).

### 2.2 FLAME 2023 Open — the industry standard, now actually open

- **Site:** http://flame.is.tue.mpg.de — **November 2025 update: FLAME 2023 Open Model released under CC-BY-4.0.** Previous FLAME versions were research-noncommercial only; the Open release removes that blocker.
- **Ecosystem (all photo→FLAME-params):**
  - **MICA** (2022) — metrical (real-world-scale) 3D face shape from images.
  - **EMOCA** (2022) — expressive FLAME meshes from images.
  - **RingNet** (2019) — FLAME params from images (MIT-licensed code).
  - **DECA** (SIGGRAPH 2021, https://github.com/YadiraF/DECA) — single-image FLAME + *animatable wrinkle detail* + albedo/lighting. **LICENSE FLAG: PS License 1.0** (MPI's research-flavored license — treat as reference only, not a shippable dependency).
  - **RealDenseFace** (https://github.com/LinzhouLi/RealDenseFace, recent) — real-time monocular FLAME fitting from dense UV priors; ships `fit_single_image.py` (ViT-B/ViT-S checkpoints). Check its license file before wiring; newest and fastest of the FLAME fitters.
  - **FLAME Blender Add-on** (official) — shape/expression sliders directly in Blender.
- **CPU note:** FLAME evaluation itself is cheap; the *fitting networks* (MICA/EMOCA/DECA encoders) are PyTorch and want a GPU for speed but **run on CPU** (minutes, not seconds, per photo — acceptable for an offline "import your face" step).

### 2.3 MediaPipe Face Mesh / Face Landmarker — the landmark engine

- **License: Apache 2.0.** TFLite models; **runs on CPU** in real time — this is the one piece of the face-scan stack with zero GPU anxiety.
- **Output:** 468 3D face landmarks (478 with iris contours), plus 52 ARKit-compatible facial blendshapes. Google ships `canonical_face_model.obj` with the landmark index space shared between the canonical mesh and runtime detections — the documented bridge for deforming a mesh to match a detected face.
- **Blender-ready tooling exists:** `jv12347/mediapipe-facemesh-to-obj-blender` (CLI + web + Blender-targeted builds) converts a photo's landmarks into an OBJ in Blender's coordinate space — a starting template for the "landmark-fit" half of our pipeline.
- **Role in our suite:** (1) landmark source for fitting GNM/FLAME params; (2) landmark source for WWE-style photo→texture warping (align eyes/nose/mouth automatically — the step WWE 2K makes the player do by hand); (3) blendshape source for expression sanity checks.

### 2.4 2026 diffusion / feed-forward head generators — research lane, not wiring lane

Genuinely SOTA, but output the wrong representation for a Tekken-style game *today*:

- **FaceLift** (Adobe Research, arXiv 2412.17812) — single image → multi-view diffusion → GS-LRM → **360° head as Gaussian splats**. Best identity preservation in its class. Splat ≠ mesh ≠ rigged fighter.
- **SplatShot** (May 2026) — *training-free* single-photo 3DGS face avatar; couples 3DGS + 2D diffusion in the denoising loop.
- **Any3DAvatar** (arXiv 2604.13856) — single portrait → full-head in **0.65 s** infer+render; beats TRELLIS on head reconstruction metrics. Still Gaussian-splat output.
- **SketchFaceGS** (open-source Jittor, https://github.com/gogoneural/SketchFaceGS_jittor) — sketch-driven 3D face generation/editing with disentangled geometry/appearance (recolor regions, add tattoos that follow facial curvature — directly relevant to our *texture/customization* lane later).

**Verdict:** track for the future (splat→mesh baking is an active research area); do not wire into the suite until the output is a rigged mesh. The one exception is using them as *reference/ideation* tools, which needs no wiring.

### 2.5 API lane — zero local GPU, pay per scan

For the "no GPU guaranteed on the VM" constraint, the API lane is the honest answer for heavyweight reconstruction:

- **AvatarSDK** (avatarsdk.com) — REST: `POST /avatars/` with a selfie → rigged, game-ready avatar (realistic or cartoon), **GLB/glTF or FBX**, Mixamo-compatible skeleton + facial blendshapes. Cloud or on-premise. Commercial pricing (Pro tier covers companies under $2M revenue). *This is the closest thing to "WWE face scan as a service."*
- **KeenFace** (keenface.ai, KeenTools, launched ~Oct 2026) — photos → heads in **native MetaHuman topology** with 4K PBR maps (base color, normal, roughness, specular), automated de-hairing, browser + API, pay-as-you-go with free starter credits. MetaHuman topology is a retarget-friendly, production-proven base.
- **Hyper3D Rodin + ChatAvatar** (hyper3d.ai) — image-to-3D API with a dedicated photo→avatar pipeline; free preview, credits on confirm.

**Wiring implication:** the suite's face-scan menu should be *backend-agnostic* — "Local (CPU)" vs "Cloud (API key)" as a submenu toggle, per the TOOL UNIFICATION LAW (one combined front-end, multiple engines behind it).

---

## 3. Face morphing depth — per-part sliders

The suite needs WWE/2K-depth face editing: nose, mouth, eyes, eyebrows, ears, jaw, chin, cheeks, forehead — individually, not just "age/mass/tone."

### 3.1 MPFB 2 — deepest open per-part morphs with a clean license (RECOMMENDED morph base)

- **What:** MakeHuman Plugin for Blender 2 (actively maintained; v2.08 is an officially vetted Blender extension, Blender 4.2+). One-click humanoid → deep parametric editing → export glTF/FBX/OBJ/USD.
- **Morph depth:** the MakeHuman **target/modifier system** — hundreds of per-part targets (nose bridge/width/tip, eye slant/spacing/size, mouth width/lip fullness, jaw width/chin projection, ear size/placement, cheek fullness, brow ridge, forehead slope…), with left/right symmetry toggle and per-side control. This is the deepest *named, per-part* slider set in any open tool — exactly the "face lab" granularity the suite needs.
- **License (verified from makehumancommunity.org + repo LICENSE.md):** source code **GPLv3**, but **all core assets — base mesh, targets/modifiers, textures, clothes, rigs — are CC0 1.0 Universal.** The MakeHuman team's explicit legal stance: *"no output from MPFB contains any trace of program logic… what you get is a combination of assets and your own creative input. As the assets have been released under CC0, there is no limitation on what you can do with this combined output"* — exports, renders, saved models are **yours, no copyleft**. This is the only parametric human system where the license story is this clean.
- **Headless:** MPFB is a Blender addon — drivable via `blender --background --python` for a headless backend lane.
- **Caveat:** GPLv3 *code* means we don't copy MPFB's Python into our repo — we *drive* it as a tool (the TOOL-TO-MENU WIRING LAW wants menu wiring, not code vendoring anyway), and we build our own slider→target mapping on top of the CC0 target database.

### 3.2 GNM — region masks + semantic parameters (RECOMMENDED head-model base)

- GNM's own region masks give per-region control; identity is PCA (components move correlated features — the community demo is honest that numbered PCA sliders aren't semantic "jaw width" knobs). **Practical approach:** use GNM as the *base head mesh + fit target*, and MPFB-style named targets as the *user-facing slider layer*, with a baked mapping between them. This mirrors how WWE structures it (template + sliders + photo).

### 3.3 MB-Lab — deep, but LICENSE-FLAGGED (do not wire)

- **Morph depth:** hundreds of parameters; docs list low-level nose/eyes/mouth/cheeks/chin controls, meta-parameters (age/mass/tone), expression engine. Genuinely deep.
- **License (verified from the MB-Lab wiki Asset Licensing page):** Python code **GPLv3**; **all data files (meshes, morph JSONs, images) AGPLv3**; and critically — *"The default license for models generated by the software is AGPL 3… as derived product of the AGPL'd database, the models must be distributed under AGPL 3."* The original ManuelBastioniLAB offered a CC-BY-4.0 dual-license for *official* releases only; the MB-Lab fork cannot grant that. **Characters generated through MB-Lab's database would carry AGPL copyleft into our game assets — a hard no for a commercial title.** Flagged, not wired.

### 3.4 CharMorph — MB-Lab's successor, same flag

- "Spiritual successor" to MB-Lab (MB-Lab discontinued after 1.8.1); v0.4 with Blender 4.4 support; reimplements features on the same base meshes/morphs with clean-room code, full Rigify face rig, realtime clothing morphing.
- **Same problem:** base models (`mb_male`/`mb_female`) are **AGPL3**. Clean code doesn't clean the data license. Flagged, not wired.

### 3.5 Bottom line on morphing

| Tool | Per-part depth | Output license | Verdict |
|------|---------------|----------------|---------|
| MPFB 2 | Deepest named per-part targets | **CC0 — yours** | ✅ Wire as morph database |
| GNM Head | Region masks + semantic params | **Apache 2.0** | ✅ Wire as head model |
| MB-Lab | Deep | AGPL (infects output) | 🚫 Flagged |
| CharMorph | Deep | AGPL (infects output) | 🚫 Flagged |

---

## 4. Pipeline fit — where face-scan slots into the suite

Per the standing CREATE-NEW-FIGHTER FLOW (template select → body → head/face → skin → hair → …) and the TOOL-TO-MENU WIRING LAW, face-scan is **one submenu inside the Head/Face step**, not a standalone script:

```
Create New Fighter
 └─ Template select (WWE-style base bodies — never Mixamo)
     └─ Body (unified BODY system: MPFB/Build-A-Bod/…)
         └─ Head / Face
             ├─ Face template select (GNM Head presets / phenotypes)
             ├─ ★ Face Scan Import  ← NEW
             │   ├─ Source: [ Upload 1–3 photos ]  (front + ¾ + profile best; 1 works)
             │   ├─ Engine: [ Local CPU ▾ | Cloud API ▾ ]
             │   │   ├─ Local CPU: MediaPipe landmarks → fit GNM params (NumPy backend)
             │   │   │            → drive face sliders → project photo as face texture
             │   │   └─ Cloud API: AvatarSDK / KeenFace (key in settings) → import GLB/FBX head
             │   ├─ Texture mode: [ WWE-style photo projection | AI-cleaned texture ]
             │   ├─ Alignment preview: auto eye/nose/mouth match (MediaPipe) + manual nudge
             │   └─ Bake: commit to fighter's head mesh + morph deltas + texture
             ├─ Face sliders (per-part: nose/eyes/mouth/brows/ears/jaw/chin/cheeks…)
             │   └─ driven by MPFB CC0 targets mapped onto the GNM base
             └─ … → Skin → Hair → Facial hair → Attire → …
```

**CPU vs API split (per project constraints — headless Blender backend, no GPU guaranteed):**

- **CPU-viable today:** MediaPipe landmarking (TFLite/CPU, realtime); GNM NumPy-backend evaluation + SciPy/JAX-CPU fitting (minutes per face — fine for an offline import step); MPFB target application (Blender headless); photo→texture projection (OpenCV warp — trivially CPU); `mediapipe-facemesh-to-obj-blender` OBJ pipeline.
- **Needs GPU or API:** DECA/EMOCA/MICA/RealDenseFace encoders (PyTorch — *run* on CPU, slowly; practical on GPU); all 2026 diffusion head generators (FaceLift/SplatShot/Any3DAvatar — GPU-only, and splat output anyway). **API lane covers this:** AvatarSDK or KeenFace returns a finished head over REST — the VM never touches a GPU.
- **Recommended default:** Local-CPU path as the built-in default (zero cost, zero keys, works on the VM); Cloud-API as an opt-in submenu for higher fidelity.

**WWE-parity note:** the texture-projection half (2.3 + OpenCV warp) reproduces WWE 2K's Face Photo Capture *exactly* — photo as face texture on a template — and can ship before the geometry-fitting half. The geometry fit (GNM/FLAME) is what makes ours *better than* WWE.

---

## 5. License register (Apache/MIT preferred; GPL flagged)

| Component | License | Shippable in a commercial game? |
|-----------|---------|-------------------------------|
| GNM (google/GNM) | Apache 2.0 | ✅ Yes |
| MediaPipe (Face Landmarker / Face Mesh) | Apache 2.0 | ✅ Yes |
| FLAME 2023 Open model | CC-BY-4.0 | ✅ Yes (attribute MPI) |
| MPFB 2 assets (targets, base mesh) | CC0 | ✅ Yes, no restrictions |
| MPFB 2 source code | GPLv3 | ⚠️ Drive as a tool, don't vendor code |
| mediapipe-facemesh-to-obj-blender | (check repo — community tool) | ⚠️ Verify before wiring |
| RealDenseFace | (check repo license file) | ⚠️ Verify before wiring |
| DECA | PS License 1.0 (research-flavored) | 🚫 Reference only |
| MB-Lab code / data | GPLv3 / AGPLv3 (output inherits AGPL) | 🚫 Do not wire |
| CharMorph code / base meshes | (code open) / AGPL3 | 🚫 Do not wire (data flag) |
| AvatarSDK / KeenFace / Hyper3D | Commercial, per-use/API | ✅ Yes (paid lane, no license contagion) |

---

## 6. Open questions for the owner / build lane

1. **Cloud-API budget:** is a pay-per-scan API (AvatarSDK / KeenFace) acceptable as an opt-in, or local-only for now? (Recommendation: local default, API opt-in — no decision needed to start.)
2. **FLAME attribution:** CC-BY-4.0 requires crediting MPI — fine for us? (Presumed yes; confirm once.)
3. **GNM photo-fitting:** no official photo→GNM fitter exists yet — build-lane work (landmark optimization). Alternatively start from FLAME fitting (MICA/EMOCA exist today) and retarget to GNM. Owner call on which base to fit first.
4. **Likeness/consent:** face-scan of real people (WWE's use case) raises likeness rights — suite should include a consent/ownership checkbox at import. (Policy note, not a blocker.)
5. **Non-human fighters:** many WH fighters are creatures/demons (Dorowani, Chatur/Rahkasa…). Face-scan applies to the human/humanoid roster; creature heads stay in the Tripo/sculpt lane. No conflict — the menu node is per-fighter.

---

## Sources

- GNM repo + README (Apache 2.0, GNM Head, backends, roadmap): https://github.com/google/GNM
- GNM Head technical report (arXiv 2607.23687): https://arxiv.org/pdf/2607.23687v2
- GNM browser demo (community, real GNM geometry): https://huikku.github.io/gnm-head-studio/
- FLAME 2023 Open (CC-BY-4.0), MICA/EMOCA/DECA/Blender add-on: http://flame.is.tue.mpg.de
- DECA repo + license (PS License 1.0): https://github.com/YadiraF/DECA
- RealDenseFace (FLAME fitting, single-image CLI): https://github.com/LinzhouLi/RealDenseFace
- MediaPipe canonical face model + Face Landmarker (Apache 2.0): https://tympanus.net/codrops/2026/09/06/building-a-real-time-3d-face-mask-with-mediapipe-threlte-and-three-js/
- mediapipe-facemesh-to-obj-blender (photo→OBJ for Blender): https://deepwiki.com/jv12347/mediapipe-facemesh-to-obj-blender/1-project-overview
- MB-Lab asset licensing (GPLv3 code / AGPLv3 data / AGPL output): https://github-wiki-see.page/m/animate1978/MB-Lab/wiki/Asset-Licensing
- CharMorph (MB-Lab successor, AGPL3 base meshes): https://www.cgchannel.com/2025/03/check-out-new-open-source-3d-character-generator-charmorph/
- MPFB 2 license (GPLv3 code / CC0 assets / output-is-yours): https://static.makehumancommunity.org/about/license.html and https://raw.githubusercontent.com/makehumancommunity/mpfb2/master/LICENSE.md
- WWE 2K23 face import flow: https://www.spieltimes.io/news/wwe-2k23-how-to-import-or-upload-your-face-and-create-a-wrestler/ and https://gamerjournalist.com/how-to-face-scan-in-wwe-2k23-character-creation-guide/
- AvatarSDK API (photo→rigged GLB/FBX REST): https://avatarsdk.com/avatar-api/
- KeenFace launch (photos→MetaHuman-topology heads, API): https://www.awn.com/news/keentools-keenface-turns-photos-metahuman-ready-3d-heads
- FaceLift (Adobe, single-image 3D head): https://arxiv.org/html/2412.17812v1
- SplatShot (May 2026, training-free 3DGS avatar): https://www.catalyzex.com/s/3d%20Face%20Reconstruction
- Any3DAvatar (single portrait → full head, 0.65 s): https://arxiv.org/pdf/2604.13856
