# Auto-Rig + Auto-Skinning-Weights Survey — Industry-Standard Solutions

**Date:** 2026-11-09 (research performed live, 2026-11-09 ~09:20–09:35 CST)
**Use case driving every verdict:** rig static character *statues* — fused single meshes,
~1M verts, humanoid fighters — with **ZERO hand edits**. Output must be shippable in a
commercial game. A candidate is "pull-and-wire" only if (a) code **and** weights are
actually released, (b) the licence permits commercial use, and (c) it can run in an
unattended pipeline (local GPU / scriptable API — no manual marker placement, no GUI-only step).

**Method / honesty note:** Licence names below were read from the repo header / LICENSE
file as rendered on GitHub, the vendor's own FAQ/terms/pricing/docs pages, or the
Hugging Face model card, on the date above. Where a licence could not be read from a
primary source, the entry is flagged **UNVERIFIED** rather than guessed. Where primary
and secondary sources conflict, both are stated and the conservative verdict wins.

---

## 0. Executive summary — the short answer

1. **The learned field moved in 2026.** UniRig (SIGGRAPH 2025) is no longer the newest
   VAST model. Its own README now banners its successor:
   **SkinTokens / TokenRig (VAST-AI-Research, TOG 2026, arXiv:2602.04805, repo created
   2026-02-08)** — MIT code, weights on Hugging Face, single-pass skeleton + skinning,
   claiming **+98–133% skinning accuracy and +17–22% bone prediction over prior SOTA**
   (vendor/paper claim, not independently benchmarked here). For a fresh wire-up in
   Nov 2026, TokenRig is the primary candidate and UniRig is the proven fallback.
2. **Only three learned backends are cleanly commercial + released + local:**
   SkinTokens/TokenRig (MIT), UniRig (MIT), Make-It-Animatable (MIT code — see its
   caveats), plus the ByteDance Seed3D pair MagicArticulate / Puppeteer (Apache-2.0 code)
   with release-completeness caveats detailed below.
3. **Everything with an NC / research-only / GPL-commercial licence is reference-only**
   for a sellable game: RigNet (GPLv3 or paid UMass commercial licence), RigAnything
   (Adobe Research License, noncommercial), TailorRig (Tencent, academic-only, Nov 2026),
   HumanRig (MIT licence file but *no code or weights in the repo* — dataset only).
4. **No learned model consumes 1M verts directly.** All of them sample a point cloud /
   simplified proxy, predict skeleton + weights on the proxy, then transfer weights back
   to the full-resolution mesh (SkinTokens exposes this explicitly as `--use_transfer`;
   UniRig has a separate merge step). The transfer-back step, not the model, is what
   preserves the statue's full detail. Budget pipeline work for it.
5. **Weight-solving fallback stack (given a skeleton from anywhere):** learned skinning
   head first; then a **geodesic-voxel** solver (Maya's production bind method — no clean
   permissive OSS drop-in exists, see §4.1); then **libigl Bounded Biharmonic Weights**
   (core MPL-2.0, but its tetrahedralisation path drags in copyleft — see §4.2).
   Blender's built-in bone-heat is **disqualified** for fused statues (§4.2).
   Delta Mush is a *deformation corrector*, not a weight solver, and its open form is
   Blender's Corrective Smooth (§4.3).

---

## 1. Learned backends (skeleton + skinning from geometry alone)

### 1.1 SkinTokens / TokenRig — VAST-AI-Research (Tsinghua / Tripo) — **2026, NEWEST**

- **What it does:** BOTH, unified. An FSQ-CVAE compresses skinning weights into discrete
  "SkinTokens"; a Qwen3-0.6B-based autoregressive transformer ("TokenRig") then emits
  the *entire* rig — skeleton hierarchy followed by skin tokens — as one token sequence
  from a single input mesh. GRPO (RL) refinement targets out-of-distribution assets.
  Flags include `--use_skeleton` (skin-only, given an existing skeleton) and
  `--use_postprocess` (voxel-based skin post-processing).
- **Quality standing:** Successor to UniRig per the UniRig README itself. Paper/repo
  claim +98–133% skinning accuracy, +17–22% bone prediction vs SOTA baselines
  (RigNet, MagicArticulate, UniRig, Puppeteer compared in the paper). Qualitative repo
  figure claims baselines "bleed" across disconnected parts where TokenRig stays
  locally coherent — exactly the fused-statue failure mode that matters here.
  Independent third-party benchmarks: **UNVERIFIED** (too new).
- **Licence — VERIFIED (code):** GitHub repo header and README §License:
  **"This project is licensed under the MIT License."** Repo: `VAST-AI-Research/SkinTokens`.
  **Weights:** hosted at `VAST-AI/SkinTokens` on Hugging Face (~1.6 GB total:
  `grpo_1400.ckpt` TokenRig model + `last.ckpt` FSQ-CVAE, both required). The HF model
  page text fetched 2026-11-09 did not render a licence tag in its card body; a
  third-party licence audit (QtMeshEditor `THIRD_PARTY_AI_MODELS.md`, verified 2026-07)
  records **weights MIT, ungated**, and the Qwen3-0.6B backbone is Apache-2.0.
  Treat weights as MIT per that audit, but re-confirm the HF card's licence tag in the
  browser before shipping — flagged as a one-click residual check, not a blocker.
- **Where it runs:** Local GPU only (plus a hosted HF Space demo, §5). **NVIDIA GPU ≥14 GB
  VRAM required for inference** (repo README, verbatim). Python ≥3.11, CUDA ≥12.1,
  PyTorch 2.7.0, flash-attn. CLI: `python demo.py --input <mesh> --output <rigged.glb>
  --use_transfer`. Input examples are `.glb`; output `.glb`.
- **1M-vert reality:** Predicts from sampled geometry; `--use_transfer` ("Rig with
  original texture and scale preserved") is the path that maps the rig back onto the
  original high-res mesh. Validate weight transfer quality on one statue before batch use.
- **Verdict: ✅ PULL-AND-WIRE — Rank #1.** Newest, MIT, both stages unified, local,
  scriptable, no per-asset fee, no vendor lock-in.

### 1.2 UniRig — VAST-AI-Research (Tsinghua / Tripo), SIGGRAPH 2025 (TOG)

- **What it does:** BOTH, in two stages. (1) Skeleton prediction: GPT-like autoregressive
  transformer with "Skeleton Tree Tokenization". (2) Skinning: Bone-Point Cross Attention
  predicts per-vertex skinning weights (+ bone attributes) from the predicted skeleton.
  Inputs `.obj/.fbx/.glb/.vrm`; pipeline = `generate_skeleton.sh` → `generate_skin.sh` →
  `merge.sh` → rigged `.fbx/.glb`.
- **Quality standing:** SIGGRAPH 2025 SOTA on release; paper reports large margins over
  RigNet-era methods on Rig-XL (14k+ rigged models). Handles humans, animals, fictional
  and inorganic categories with one model. Widely integrated downstream (ComfyUI nodes,
  ONNX ports) — the most battle-tested learned rigger in this survey. Its own README
  warns skinning "may degrade significantly if the skeleton is inaccurate — e.g. tail or
  wing bones missing" and recommends skeleton refinement first; under a zero-hand-edit
  rule that means *seed/parameter retries*, not manual fixes.
- **Licence — VERIFIED:** GitHub repo header: **MIT License (MIT)** for code
  (`VAST-AI-Research/UniRig`, LICENSE file present). **Weights MIT** — HF repo
  `VAST-AI/UniRig`; corroborated by the QtMeshEditor licence audit ("MIT code + MIT
  weights, trained on Articulation-XL2.0, CC-BY-4.0 — a fully clean chain").
- **⚠️ Release-completeness caveat — VERIFIED from the HF model card (fetched 2026-11-09):**
  The HF card still states this release "contains **only the Skeleton & Skinning
  Prediction component** … trained specifically on the Articulation-XL2.0 dataset" and
  that checkpoints "trained on Rig-XL/VRoid datasets (representing the full results
  reported in the paper)" are *coming soon / planned*. The GitHub README says the same:
  the Articulation-XL2.0 checkpoint is available now; the full Rig-XL/VRoid checkpoint
  replicating headline paper numbers is **⏳ planned, not released**. What you can pull
  today is real and usable, but it is **not** the paper's headline model.
- **Where it runs:** Local GPU, **>8 GB VRAM** (HF card requirements). Python 3.11,
  PyTorch ≥2.3.1, plus a fragile dependency stack (spconv, torch_scatter/torch_cluster,
  flash-attn) — budget setup time. Headless/CLI-native. Hosted options: community
  HF Space (§5) and a third-party Replicate port (`aaronjmars/unirig-ai`, per Replicate
  guide coverage — third-party, not VAST-official; **UNVERIFIED** as an official channel).
- **Verdict: ✅ PULL-AND-WIRE — Rank #2.** The proven fallback / cross-check for
  TokenRig: run both, keep the better rig per statue. MIT end-to-end.

### 1.3 Make-It-Animatable (MIA) — jasongzy et al., CVPR 2025 Highlight

- **What it does:** BOTH, humanoid-specialised. Particle-based shape autoencoder predicts
  joints, skinning weights and pose; outputs a Mixamo-compatible skeleton — which is a
  practical advantage: the rig drops straight into Mixamo-bone animation libraries.
  Claimed <1 s per character. **MIA v2** (current repo news) upgrades to a Hunyuan3D 2.1
  ShapeVAE backbone, mesh inputs only, with improved skinning post-processing and
  Blender integration (`app_v2.py`, v2 branch).
- **Quality standing:** CVPR 2025 Highlight; for *humanoids specifically* it is a
  first-tier candidate and historically the fastest of the learned riggers. Humanoid-only
  is not a limitation for this use case (humanoid fighters).
- **Licence — code VERIFIED, weights BACKBONE-RISK:** GitHub repo header:
  **MIT License (MIT)** (`jasongzy/Make-It-Animatable`, LICENSE file present).
  Two residual risks, both flagged honestly:
  1. An older secondary survey reported conflicting tags (Apache-2.0 on GitHub vs
     CC-BY-NC-4.0 on an HF Space). The repo as fetched 2026-11-09 says **MIT**; the HF
     model-discussion history shows the HF licence tag being set *from* the GitHub
     licence. Treat the NC tag report as **stale/UNVERIFIED**, but screenshot the HF
     card tag before commercial reliance.
  2. **v2's backbone is Tencent Hunyuan3D 2.1 ShapeVAE.** Hunyuan3D models ship under
     Tencent's Hunyuan Community Licence (territory/MAU conditions in the 2.x line),
     *not* MIT. Whether MIA v2's released weights inherit that licence is
     **UNVERIFIED** from primary sources. **MIA v1 is the licence-clean version;
     do not wire v2 until its weight licence is read directly.**
  Also note its training data is Mixamo-derived (hosted as `jasongzy/Mixamo` dataset) —
  Mixamo's own terms (§2.2) govern the *source* assets; MIA's MIT code licence does not
  by itself launder training-data terms. Standard research-model caveat, noted not resolved.
- **Where it runs:** Local GPU; also an official HF Space demo by the author
  (`jasongzy/Make-It-Animatable` / "Make It Animatable", and a separate MIA v2 Space —
  see §5). Blender is used in its demo/export path.
- **Verdict: ✅ PULL-AND-WIRE (v1) — Rank #3, humanoid second opinion.**
  Especially valuable because its skeleton is Mixamo-native. v2 = reference-only until
  the Hunyuan-backbone weight licence is verified.

### 1.4 Puppeteer — ByteDance Seed3D / NTU / A*STAR, NeurIPS 2025 Spotlight

- **What it does:** BOTH, plus animation. Autoregressive skeleton generation, an
  attention/PartField-feature skinning stage, then video-guided animation via a
  differentiable optimisation pipeline. Successor/companion to MagicArticulate from the
  same team. Trained on Articulation-XL2.0 (59.4K rigged samples, diverse-pose subset
  included).
- **Quality standing:** NeurIPS 2025 Spotlight; in the SkinTokens paper's comparison it
  is a top baseline (TokenRig beats it, per that paper). Category-agnostic, not
  humanoid-only.
- **Licence — VERIFIED (code):** GitHub repo header: **Apache License 2.0 (Apache-2.0)**
  (`Seed3D/Puppeteer`, LICENSE file present). **Weights:** README news 2025-09-04:
  "We also release the inference codes and model checkpoints" (HF-linked, per-component
  downloads inside `skeleton/`, `skinning/`, `animation/` folders). A separate HF *dataset*
  licence for Articulation-XL2.0 was reported as CC BY-NC 4.0 in one secondary sweep —
  that concerns the **dataset**, and whether the *checkpoints* carry any NC term is
  **UNVERIFIED** from the checkpoint cards themselves. Read the three checkpoint cards
  before shipping weights-derived output commercially.
  (Noise warning: low-quality blog coverage claims Puppeteer is "MIT / free for
  commercial use" — that contradicts the repo's own Apache-2.0 header. Trust the repo.)
- **Where it runs:** Local GPU. Python 3.10, PyTorch 2.1.1, CUDA 11.8 (older stack —
  expect environment friction on a modern driver), flash-attn, PyTorch3D.
  `bash demo_rigging.sh` → `results/final_rigging`; FBX export via `export.py`
  (needs `bpy==4.2.0`). Also an author-run HF Space (§5).
- **Verdict: ⚠️ PULL AS SECOND ENGINE / CROSS-CHECK** (Apache-2.0 code; checkpoint-card
  licence check is the one gate). Its skinning is a genuinely different architecture
  from VAST's, making it the best diversity vote when TokenRig/UniRig disagree on a statue.

### 1.5 MagicArticulate — ByteDance Seed3D / NTU / A*STAR, CVPR 2025

- **What it does:** Paper = BOTH: autoregressive transformer skeleton generation +
  functional-diffusion skinning conditioned on volumetric geodesic distance priors
  (Articulation-XL / Articulation-XL2.0, 48K+ models).
  **Release = skeleton only, as far as the public repo shows.** The repo root fetched
  2026-11-09 contains `skeleton_models/` and no skinning module; README news records
  releases for preprocessed data (2025-03-20), skeleton *inference code* (2025-03-28),
  skeleton *weights* (2025-04-16, updated 2025-08-07 for a normalisation bug), and a
  Blender GLB-reading script — **no skinning-weight checkpoint or `predict_weights`
  release is recorded in the repo**. (A third-party summary site describes a
  `predict_weights.py` workflow; that file is not in the official repo root listing —
  **UNVERIFIED / not in the official release**.) So the brief's question is answered:
  **effectively code-and-weights for the skeleton stage; the skinning stage is
  paper-only in the official release.** Its skinning idea lives on, released, in Puppeteer.
- **Licence — VERIFIED (code):** GitHub repo header: **Apache License 2.0 (Apache-2.0)**
  (`Seed3D/MagicArticulate`, LICENSE file present). **No NC clause was found in the
  code licence.** Skeleton weights are HF-hosted (linked from README via `download.py`);
  their card licence is **UNVERIFIED** here.
- **Quality standing:** CVPR 2025; strong published skeleton metrics (CD-J2J/J2B/B2B on
  Articulation-XL2.0-test and ModelsResource-test reproduced in README). Superseded
  within its own lab by Puppeteer (2025-09) and, on skinning, by TokenRig (2026).
- **Where it runs:** Local GPU; skeleton inference needs ~4.6 GB VRAM, 1–2 s/model
  (README). Python 3.10 / PyTorch 2.1.1 / CUDA 11.8.
- **Verdict: ⚠️ REFERENCE + SKELETON-ONLY SECOND OPINION.** Pull it if a statue's
  skeleton defeats VAST + Puppeteer; pair its skeleton with a §4 weight solver.
  Do not plan on its skinning stage existing.

### 1.6 RigNet — Xu et al., UMass Amherst, SIGGRAPH 2020

- **What it does:** BOTH (historical baseline): JointNet/BoneNet graph networks predict
  joints + connectivity; SkinNet refines geodesic-initialised skinning weights.
  Trained on ModelsResource (~2.7K characters). Requires heavy decimation
  (works at ~1–5K verts) — a poor native fit for 1M-vert statues except via proxy+transfer.
- **Licence — VERIFIED:** Project page and repo, verbatim in substance: *"Our code is
  licensed under the General Public License Version 3 (GPLv3), or under a Commercial
  License. To inquire into a Commercial License, please contact the University of
  Massachusetts Amherst Technology Transfer Office at tto@umass.edu…"*
  Weights are distributed with the code under that dual scheme; the underlying
  ModelsResource dataset is not public-licensed for redistribution (per third-party
  licence audits). **GPLv3 code in a shipped game pipeline tool is a copyleft problem;
  the commercial path is a negotiated university licence.**
- **Quality standing:** The 2020 baseline every 2025–26 paper beats. Unmaintained,
  legacy CUDA/PyTorch-Geo
...[truncated 20887 chars]metric stack.
- **Where it runs:** Local GPU (old PyTorch Geometric environment).
- **Verdict: ❌ REFERENCE-ONLY.** Cite it, benchmark against it, do not ship it
  without a UMass commercial licence.

### 1.7 RigAnything — Liu et al. (Adobe Research internship work), SIGGRAPH 2025 (TOG)

- **What it does:** BOTH, template-free. Autoregressive transformer with BFS joint
  ordering + diffusion for continuous joint positions; predicts skeleton + skinning
  for arbitrary categories. Repo (`Isabella98Liu/RigAnything`, created 2025-10-18)
  provides inference only: `.glb/.obj` in, rigged `.glb` out, checkpoint via
  `hf download Isabellaliu/RigAnything`. Its own quick-start *simplifies the mesh
  first* (example target 8,192 faces) — proxy-then-rig, like all the others.
- **Licence — CONFLICTED, treat as noncommercial:** GitHub classifies its `LICENSE.md`
  as **"Other (NOASSERTION)"**. Multiple independent licence audits record it as
  **Adobe Research License — noncommercial research purposes only** (that licence's
  text, read from Adobe Research's own hosting, grants use "for noncommercial research
  purposes only" and expressly excludes "development of commercial products").
  Counter-signal: an HF discussion proposed tagging the model card `apache-2.0`.
  The `LICENSE.md` file itself was not rendered in this pass — **the exact file text
  is UNVERIFIED here** — but with an Adobe Research License attribution on record,
  the only safe commercial posture is noncommercial until the file is read directly.
- **Quality standing:** SIGGRAPH 2025 TOG; SOTA-class template-free results on
  RigNet + Objaverse data on publication. No production adoption signal comparable
  to UniRig's.
- **Where it runs:** Local GPU (`cuda:0`), Python 3.11, needs `bpy` for export.
- **Verdict: ❌ REFERENCE-ONLY** for a commercial game (licence). Scientifically
  worth studying for its BFS-ordering/diffusion design.

### 1.8 HumanRig — Chu et al., Alibaba AMAP, CVPR 2025 Highlight (arXiv:2412.02317)

- **What it does (paper):** BOTH, humanoid-only, uniform skeleton topology.
  Prior-Guided Skeleton Estimator (2D prior → 3D skeleton) + Mesh-Skeleton Mutual
  Attention Network for skinning. Dataset of 11,434 T-posed humanoid meshes, built
  specifically to survive messy AI-generated meshes with complex clothes/accessories.
  **Requires T-pose input** (per its dataset design).
- **⚠️ Release reality — VERIFIED from the repo (fetched 2026-11-09):** The GitHub
  repo (`c8241998/HumanRig`) contains only `assets/`, `LICENSE` and `README.md` —
  7 commits, README is project description + a TODO ("Release dataset on Hugging
  Face") + citation. **No inference code, no training code, no weights in the repo.**
  What is actually public is the *dataset* (HF `jellyczd/HumanRig`, also on
  ModelScope). A separate 2026 paper describes the HumanRig *dataset* as released
  under CC BY-NC 4.0 — dataset licence **UNVERIFIED** from its own card here.
- **Licence (repo):** GitHub header: **MIT License (MIT)** — but it licences an
  essentially empty repo; it does not give you a runnable rigger.
- **Verdict: ❌ REFERENCE / DATASET-ONLY.** Valuable as training/eval data and as a
  design reference (uniform topology is exactly what a game wants); it is not a
  pullable backend. Anyone claiming to "run HumanRig" is running a reimplementation.

### 1.9 TailorRig — Tencent LIGHTSPEED, arXiv:2611.02902 (submitted 2026-11-02) — NEWEST PAPER

- **What it does:** BOTH, humanoid + garments: keeps an artist-specified body-skeleton
  template, autoregressively generates auxiliary bone chains for clothing/accessories
  from semantic labels, and assigns weights with a hierarchical chain-to-bone
  formulation designed to stop weight bleeding between adjacent-but-unrelated parts.
  Ships with the Human-Mix dataset (~38–39K humanoid models; HF `tencent/TailorRig`,
  39,073 `.npz` samples).
- **Licence — VERIFIED (dataset card, fetched 2026-11-09):** **"TailorRig License"
  (Copyright © 2026 Tencent)** — key constraint quoted from the card: *"Academic
  research use only; it must not be used for any commercial or production purposes."*
  The arXiv HTML carries a CC BY-NC-ND licence marker. Code licence at
  `github.com/Tencent/TailorRig` was not separately read — **UNVERIFIED** — but the
  dataset's academic-only term already closes the commercial door for the package.
- **Quality standing:** Days old at survey time; no independent evaluation exists.
  The garment/auxiliary-bone problem it targets is real for clothed fighters, which
  makes it the most *relevant* reference paper of 2026 — and unusable commercially.
- **Verdict: ❌ REFERENCE-ONLY** (academic-only). Read the chain-to-bone skinning
  formulation; do not pull code/data into a production pipeline.

### 1.10 Names checked and ruled out of the rigger category

- **UniAnimate / UniMate:** "UniAnimate" could not be verified as a rigging system
  from primary sources in this pass — **UNVERIFIED as a rigger**. The verifiable
  near-name is **UniMate (SIGGRAPH Asia 2026)**: text-to-*motion* for already-rigged
  assets. It consumes rigs; it does not create them. Not a candidate.
- **Auto-Connect / RigFormer, DRiVE, TARig, "How to Train Your Dragon":** surfaced in
  2025–26 literature sweeps as rigging research; no verified released code + weights
  + commercial licence was established for any of them in this pass — **UNVERIFIED /
  paper-only** for pipeline purposes. Do not plan around them.

---

## 2. Production auto-riggers (commercial products)

### 2.1 AccuRIG / AccuRIG 2 — Reallusion

- **What it does:** BOTH (skeleton + skinning) for humanoids (v2 also markets broader
  character support), Windows desktop app. Workflow is *guided*: automatic detection
  with user-adjustable joint markers — i.e. **not zero-touch by design**, though
  defaults often need no adjustment. Exports FBX/USD with presets for Blender,
  Unreal, Unity, Maya, etc. Tied to the ActorCore motion library (free + paid packs,
  licensed separately from the tool).
- **Price:** The rigging software itself is **free** (Reallusion magazine, 2025-07-30:
  "completely free… you only pay for premium ActorCore animation packs if needed").
- **Licence / terms — MIXED, partly UNVERIFIED:** (a) A Reallusion forum answer from
  staff (2025-08-27) states that with **100% your own content and no Reallusion
  content**, "you can certainly use AccuRig to rig your character for use in your
  game, including a character generator" — the character-generation restriction
  applies only when Reallusion content is used. (b) Separately, a **Reallusion AI
  Service EULA dated 2026-10-29** (for its AI *cloud* service tiers) says Free-plan
  output is "for testing and evaluation purposes only", with commercial use granted
  from Starter tier up. Whether that AI-service EULA governs desktop AccuRIG 2
  exports is **UNVERIFIED** — they read as different products, but the Oct 2026 EULA
  is a warning against assuming "free tool = free commercial output" without a
  written confirmation from Reallusion for the specific version in use.
- **Where it runs:** Local Windows desktop, GUI. No documented headless/API mode —
  that alone disqualifies it from an unattended statue pipeline.
- **Quality standing:** Actively developed, widely regarded as the best free
  *interactive* humanoid rigger and the practical Mixamo successor.
- **Verdict: ⚠️ REFERENCE / MANUAL FALLBACK ONLY** for this pipeline (GUI + marker
  workflow breaks zero-hand-edit automation; terms need written clarification).
  Fine for a one-off hero asset a human shepherds; not a wire-up.

### 2.2 Mixamo — Adobe

- **What it does:** BOTH (auto-rigger + skinning) for **bipedal humanoids only**,
  web service, plus a large animation library retargeted onto its standard skeleton.
  Requires a clean, neutral/T-pose, origin-centred, error-free mesh; explicitly does
  not work on disjoined parts (e.g. a floating head). **No API** — browser upload only.
- **Licence — VERIFIED (Adobe Mixamo FAQ):** Free with an Adobe ID, no Creative Cloud
  subscription required (not available for Enterprise/Federated IDs). *"You can use
  both characters and animations royalty free for personal, commercial, and
  non-profit projects including… create video games."* No attribution required.
  Limit (Adobe General Terms / FAQ ecosystem): assets must be embedded in a finished
  project — no standalone redistribution/resale of the raw character/animation files.
- **Quality standing:** The decade-old industry baseline for humanoid quick-rigging;
  effectively unmaintained feature-wise since Adobe's 2015 acquisition, but stable
  and predictable. Its skeleton is the de-facto interchange standard (MIA §1.3 and
  Tripo §2.3 both offer Mixamo bone naming).
- **Verdict: ⚠️ REFERENCE / BENCHMARK + ANIMATION-LIBRARY SOURCE.** Commercially
  clean for game use, but no API and a manual web workflow = cannot be wired into
  an automated pipeline. Use it as the quality floor every automated candidate must
  beat, and as a motion source for Mixamo-topology rigs.

### 2.3 Auto-Rig Pro (ARP) — Artell / Lucky3D, Blender add-on

- **What it does:** Template-based rig *building* (not learned): a reference rig is
  fitted to the character. The **Smart tool** (Full version) auto-detects a biped
  body and places the skeleton on a T-pose mesh; otherwise placement is
  marker/manual. Skinning uses Blender's automatic weights, with "Voxelize" and
  "Split Parts" options for multi-piece meshes, and documented compatibility with
  Voxel Heat Diffuse Skinning (§4.2). Includes Remap (mocap/animation retargeting)
  and Unity/Unreal/Godot FBX+glTF exporters.
- **Licence — VERIFIED (Superhive listing + vendor licence page, as reported
  Sep 2026):** Listing licence field: **GPL**. Vendor nuance, quoted in secondary
  verification: *"Auto-Rig Pro cannot be freely distributed as is. Some components
  are GPL, some are not"* — the Blender-Python parts are GPL, while the Smart tool's
  AI binaries are under a restrictive copyrighted licence forbidding redistribution.
  **Output rigs are the user's** (GPL covers the add-on code, not assets you make
  with it — the standard Blender add-on position).
- **Price — VERIFIED (Superhive):** **Lite $25 / Full $50** one-time (Smart + Remap +
  exporters only in Full); 10 seats $162, 20 seats $227; Blender 2.93–5.2;
  65,000+ sales — the category leader among Blender rigging add-ons.
- **Quality standing:** Production-proven for bipeds and (with manual limb work)
  creatures. But its automation is *template fitting inside an interactive Blender
  session* — Smart still expects a human to check/correct placement.
- **Verdict: ⚠️ PAID REFERENCE / INTERACTIVE TOOL.** Buy it as a TD's instrument
  and retargeting utility if wanted; it is not a zero-hand-edit backend and its
  mixed GPL + proprietary-binary licence makes redistribution of the tool itself
  impermissible. Its *output* is commercially clean.

### 2.4 Tripo (hosted product + API) — VAST / Tripo3D

- **What it does:** BOTH via cloud API. Task chain on `api.tripo3d.ai`:
  `animate_prerigcheck` (**free** — returns riggable + recommended rig type) →
  `animate_rig` (**25 credits**) → `animate_retarget` (10 credits/animation).
  Since Feb 2026 the rigger covers **7 skeleton types**: biped, quadruped, hexapod,
  octopod, avian, serpentine, aquatic. Bone-naming specs include **Tripo, Mixamo,
  ActorCore, Unity Humanoid, Unreal (UE5 Mannequin), VRM**. Outputs GLB/FBX.
  Biped rig model is the older `v1.0-20240301` (90+ preset animations); other types
  use `v2.5-20260210`. Note the same company (VAST) publishes UniRig/SkinTokens —
  the hosted rigger is a *product*, its exact relationship to the open models is
  not documented; do not assume API output = UniRig output.
- **Licence / terms — VERIFIED in substance (Tripo pricing + terms, as quoted in
  Nov 2026 licence audits):** Free tier = **public models, non-commercial use**,
  and Tripo's terms retain broad rights over free users' inputs/outputs. Paid
  tiers: "Private & Commercially Licensed — all generated assets are private to
  your account and fully owned by you; use them commercially in games, products,
  or client work." Credits are $0.01 each ($1 = 100), so **a rig ≈ $0.25**,
  rig-check free. Pro subscription ~$20/mo / 3,000 credits.
- **Where it runs:** Cloud API only (async task API, API key). No local option.
- **Quality standing:** Broadest commercial skeleton taxonomy; fast; but
  auto-rigging is nondeterministic — practitioner pipelines built on the API
  include automatic skeleton validation + rig retries (at 25 credits per retry).
  Uploading proprietary statues to a third-party cloud is itself a pipeline decision.
- **Verdict: ⚠️ COMMERCIAL API FALLBACK (paid tier only).** The best *scriptable*
  hosted option and a legitimate overflow valve when local learned rigs fail —
  priced per rig, commercially clean on paid plans. Not Rank-1 because it is a
  metered black-box cloud service, while an MIT local equivalent exists.

### 2.5 Meshy — Meshy AI (rigging exists — confirmed)

- **What it does:** BOTH, hosted. Web app rigs **humanoids and quadrupeds** (plus a
  "Smart Rig" beta for creatures/robots/props, GLB-only, no animation library);
  the **API rigging endpoint is documented for humanoid bipeds only**:
  `POST /openapi/v1/rigging`, 5 credits per rig (+3 per animation from a 600+-clip
  library). API constraints (**VERIFIED from Meshy API docs**): input must be a
  textured GLB, **≤380,000 triangles** (over → HTTP 400; remesh to ≤300K first),
  character must face **+Z**. Web-app rigging is free; API rigging is credit-metered.
- **Licence — VERIFIED (Meshy Terms of Use, as quoted Oct–Nov 2026):** **Free plan:
  Meshy owns the Customer Output and licenses it back under CC BY 4.0** — commercial
  use allowed *with attribution to Meshy*. **Paid plans (Pro $20/mo / 1,000 credits,
  and up): customers own their output.** Also note: API-generated assets are deleted
  after 3 days on individual plans (download promptly).
- **1M-vert reality:** The 380K-triangle API cap forces a remesh/decimation step
  before rigging a ~1M-vert statue, then a weight transfer back — same proxy pattern
  as the local models, but with the proxy cap imposed by the vendor.
- **Verdict: ⚠️ COMMERCIAL API FALLBACK (paid plan).** Scriptable and cheap, but
  capped, cloud-only, and free-plan output carries CC-BY attribution + Meshy
  ownership language. Below Tripo for this use case on skeleton-spec flexibility.

### 2.6 Anything World ("Animate Anything", now Everything Universe Ltd.)

- **What it does:** BOTH + animation, hosted: upload a mesh, it auto-rigs and
  animates it (humanoids, quadrupeds, insects, fish, birds), with a 2,000+-clip
  library, a REST API / Python package, and plugins for Unity, Unreal, Blender,
  Maya, 3ds Max, Roblox.
- **⚠️ Fatal constraint for this use case — VERIFIED from vendor-documented limits
  as reported Oct 2026:** **meshes over 20,000 vertices are decimated**, uploads are
  capped at 30 MB, and processing takes minutes to ~30 minutes per model. A
  1M-vert fused statue would be destroyed as a source asset by that decimation
  unless a separate high-res weight-transfer step is built around it.
- **Licence / pricing — VERIFIED in substance (vendor terms eff. 2024-10-10, as
  quoted Nov 2026):** Revenue-tiered subscriptions: Individual **free** (<$100K
  revenue/funding, 1 seat), Micro $50/mo (<$200K), Pro $250/mo (<$4M), Enterprise
  custom. Terms: you own what you create and may use it for any purpose, **but must
  credit Anything World** (e.g. "Animated by Anything World"); library static
  models keep their own creators' licences.
- **Verdict: ❌ NOT FOR THIS PIPELINE** (20K-vert decimation vs 1M-vert statues),
  despite a real API and game-usable terms. Reference-only here.

---

## 3. (Reserved — see §4 for weight-solving; §3 merged into §4 during writing.)

## 4. Weight-solving standards (given a skeleton, compute the weights)

### 4.1 Geodesic Voxel Binding (GVB)

- **What it is:** Dionne & de Lasa (SCA 2013). Voxelise the character's *volume*,
  compute geodesic distances *through the interior voxels* from each bone, convert
  to weights. Distances cannot shortcut across air gaps, so **cross-limb bleed is
  impossible by construction** — the property fused/overlapping statues need most.
- **Who implements it:** **Autodesk Maya** — it is Maya's default production bind:
  `skinCluster` bindMethod **3 = Geodesic Voxel**, computed by `geomBind`
  (GPU-accelerated; Autodesk docs note it is **not supported in headless/batch
  Maya** — a real automation caveat). Resolution parameter is a power of two
  (default 256 in `geomBind`).
- **Open implementations:** **No clean, permissive, drop-in OSS GVB library was
  verified.** What exists: (a) from-scratch reimplementations described in detail
  inside open-source projects (e.g. QtMeshEditor's issue #819 specifies a native,
  dependency-free GVB — voxelise → rasterise bones → multi-source Dijkstra over
  interior voxels keeping top-K bone distances — explicitly to avoid libigl/TetGen
  licensing; treat that project as an implementation *reference*, its shipped
  status for GVB specifically is per its repo, **not independently verified here**);
  (b) the geodesic *half* of the idea inside learned models (MagicArticulate's and
  UniRig's skinning both condition on geodesic distances). Honest summary:
  **GVB is an algorithm you implement (~a few hundred lines from the paper), not a
  package you install.**
- **Licence:** The paper/algorithm — implement freely. Maya — proprietary
  Autodesk subscription, and its implementation won't run headless.
- **Verdict: ✅ IMPLEMENT-AS-FALLBACK (algorithm), ❌ Maya itself is not a pipeline
  answer** (licence cost + no headless geomBind). GVB is the recommended
  deterministic weight solver underneath/behind the learned heads: skeleton from
  TokenRig/UniRig → GVB weights as the guaranteed-sane baseline → learned weights
  where they beat it.

### 4.2 Heat-diffusion family: Blender bone-heat, BBW, Voxel Heat Diffuse

**(a) Blender "Automatic Weights" (bone heat) — DISQUALIFIED for fused statues.**
Surface heat diffusion (mesh-Laplacian solve, `meshlaplacian.cc`). Known failure
modes, all documented and all triggered by exactly this use case:
- Hard failure: **"Bone Heat Weighting: failed to find solution for one or more
  bones"** — the linear solve degenerates on non-manifold geometry, doubled verts,
  zero-area faces, interior faces. In one 2026 test, 8 of 46 clean Mixamo characters
  threw it outright.
- **Disconnected shells get nothing:** heat travels only along the surface, so a
  component a bone doesn't touch receives zero weight everywhere — fatal for fused
  statues with clothing/armour/eyes as separate islands, and a sleeve 2 mm from an
  arm is a whole seam-path away in surface distance.
- Bones fully enclosed by geometry (spine inside a thick torso) or outside the mesh
  fail the ray-visibility step; extreme scale/unapplied transforms produce garbage
  that *looks* like success.
This is the "house bone-heat chain" failure pattern, confirmed as an industry-known
limitation, not a local bug. **Do not use as the production solver.**

**(b) Bounded Biharmonic Weights (BBW) — libigl — the academic gold standard.**
Jacobson et al.: solve a bounded biharmonic problem over a *tetrahedralised volume*
with bone handles → smooth, bounded [0,1], partition-of-unity weights; historically
the quality reference every learned method compares against.
- **Licence — VERIFIED (libigl official licence page):** *"Libigl is primarily
  licensed under MPL2"* — all files directly in `include/igl` are **Mozilla Public
  License 2.0 only**. MPL-2.0 is file-level weak copyleft: **commercial use is
  fine**, modified libigl files stay MPL, your surrounding code need not open.
  **The trap is below the core:** subdirectory/copyleft modules inherit their
  external libraries' licences, and BBW needs a tetrahedraliser — **TetGen is
  GPL/commercial-licensed**, and libigl's copyleft TetGen wrapper would drag a
  shipped binary into GPL territory (the stated reason QtMeshEditor refused BBW).
  Practical clean path: core BBW (MPL-2.0) + a permissively-licensed tet mesher
  (e.g. a BSD/MIT tet library such as fTetWild/TetWild-class — **per-library licence
  UNVERIFIED in this pass; check before wiring**) or a commercial TetGen licence.
- **Scale reality:** BBW on a true 1M-vert surface requires tet-meshing a decimated
  proxy and transferring weights back — same proxy pattern as everything else;
  the sparse solve is the slow step. CPU (Eigen) — no GPU path in libigl.
- **Verdict: ✅ PULL (core, MPL-2.0) as the quality-baseline solver, with the
  TetGen trap explicitly engineered around.** Reference implementation for
  "heat-diffusion done right": volumetric, bounded, smooth — everything Blender's
  surface version is not.

**(c) Voxel Heat Diffuse Skinning — Mesh Online (Blender add-on) — the pragmatic fix.**
Voxelises the character into a solid and diffuses heat *through the volume*, so
multi-shell/fused characters bind where Blender's solver refuses; pitch is literally
the bone-heat error message. Includes Surface Heat mode, an "Iterative Bone Heat"
module that "always generates a result, never fails", Adaptive Voxel mode, and an
Auto Fusion Skinning module (v5.x) targeting fingers/toes/face. **Price: $30 Indie**
(Superhive; 12,500+ sales; Blender 3.6–5.1). **Licence: GPL Python + a separate
compiled solver binary** (per Superhive-derived listings) — fine to *use* on your
own assets; do not redistribute the add-on.
- **Verdict: ⚠️ PAID UTILITY — best cheap insurance inside a Blender-based stage.**
  It is a weight solver only (bring your own skeleton), GUI/Blender-bound, so it
  supports — but does not replace — the headless learned stack.

### 4.3 Delta Mush class — a deformer, not a weight solver

- **What it is:** Mancewicz et al. (Weta, 2014): smooth the *deformed* mesh and add
  back per-vertex detail deltas → volume-preserving, wrinkle-retaining deformation
  that hides mediocre weights at pose time. It **corrects deformation; it does not
  compute skinning weights** and cannot rescue an unbound mesh.
- **Proprietary forms:** Maya ships Delta Mush as a deformer (Autodesk, proprietary).
  Cinema 4D got a €25–30 third-party implementation (Valkaari, 2015).
- **Open equivalent — VERIFIED:** **Blender's Corrective Smooth modifier is
  Blender's Delta Mush** (Blender commit history, 2015-05-12: "Corrective Smooth
  Modifier (aka delta-mush)"), GPL as part of Blender, built-in and free. It runs
  only inside Blender — on export to an engine its effect disappears unless baked:
  **Corrective Smooth Baker** (Mesh Online, **$15**, GPL Python) bakes the
  modifier's effect back into vertex weights; newer tools (e.g. JointForge, $12.99,
  GPL, Superhive) bake Delta-Mush joint corrections into bone-driven shape keys for
  Unity. EA's **Direct Delta Mush** (SIGGRAPH 2019, SEED) is the modern variant —
  research/code-availability for a clean pull: **UNVERIFIED** in this pass.
- **Verdict: ✅ USE AS POLISH, NOT AS THE SOLVER.** Corrective Smooth (free, in
  Blender) + a baker is the open Delta-Mush-class path if a post-pass is wanted
  for shipped weight sets. Budget it as deformation QA, never as a substitute for
  §4.1/§4.2 weights.

### 4.4 Also in the weight toolbox (brief)

- **Pinocchio** (Baran & Popović, 2007): the classic template-embedding auto-rigger
  (sphere-packing + heat weights) inside many tools (incl. QtMeshEditor's native
  fallback). Humanoid-template only, ageing quality — reference/fallback only;
  original code licence varies by mirror — **UNVERIFIED**, check the specific mirror.
- **Dual-quaternion skinning (DQS):** a *runtime deformation* choice, not a weight
  solver; several pipelines above expose it as an export/runtime option. Decide at
  engine level; it does not change which weights you compute.

---

## 5. Hosted UniRig demo on Hugging Face Spaces — VERIFIED

**Question asked:** does an official/hosted UniRig demo exist on HF Spaces (or another
hosted endpoint) whose API could be called programmatically? Exact Space id/URL?

**Answer — two different things exist; do not conflate them:**

1. **A UniRig Space exists and is running, but it is NOT VAST-official.**
   - **Space id: `jasongzy/UniRig`**
   - **URL: https://huggingface.co/spaces/jasongzy/UniRig**
   - Verified 2026-11-09 from the HF profile page of `jasongzy` (Zhiyang Guo, the
     Make-It-Animatable author), which lists among his 5 Spaces: *"UniRig 😻 — One
     Model to Rig Them All — Running"*. The Space page itself was fetched
     (title confirmed: "UniRig - a Hugging Face Space by jasongzy").
   - It is a **community/author-hosted demo** (Guo is a rigging researcher, not the
     UniRig author — UniRig's authors are Zhang et al. / VAST-AI-Research). The
     **VAST-AI organisation itself hosts models (`VAST-AI/UniRig`,
     `VAST-AI/SkinTokens`), not a UniRig Space**, in anything verified here.
     A second community copy also exists upstream of duplicates:
     `MohamedRashad/UniRig` (named as the duplication source of another Space) —
     **existence noted from HF metadata; its current status UNVERIFIED**.
   - **Programmatic access:** as a Gradio Space it is in principle callable via the
     standard Gradio client / Space API (`gradio_client` against `jasongzy/UniRig`,
     or the Space's `/gradio_api` endpoints) *if* it is public and awake — but
     **the endpoint signature (function names, input/output schema) was NOT verified
     in this pass** (the Space page text fetch returned only its shell), and a
     free/community Space has no SLA, queue guarantees, or commercial-use grant
     from VAST. **Treat it as a try-before-you-install demo, never as production
     infrastructure.** The production route is the MIT code + weights run locally.
2. **The official successor's demo IS organisation-hosted:**
   - SkinTokens README §"Hugging Face Space Demo" links a hosted Space from the
     repo's own badges; the corresponding Space under the MIA author's account is
     **Space id: `jasongzy/SkinTokens`** —
     **URL: https://huggingface.co/spaces/jasongzy/SkinTokens** (verified from the
     same HF profile listing: *"SkinTokens 🐨 — Generate rigged 3D models from
     OBJ/FBX/GLB files — Running"*; README describes it as "upload a mesh and get a
     rigged result in the browser"). Whether the canonical VAST-hosted Space URL
     differs from this account's copy is **UNVERIFIED** — the profile-verified id
     above is the one to cite.
   - Same account also hosts **`jasongzy/Puppeteer`** ("Rig and Animate Your 3D
     Models", Running) and the MIA Spaces (`jasongzy/Make-It-Animatable` family,
     incl. an MIA v2 Space) — useful for zero-install quality comparisons of all
     three Rank-1..3 candidates on one statue before wiring anything.
3. **Other hosted UniRig endpoints:** a third-party **Replicate** model
   (`aaronjmars/unirig-ai`) is documented in Replicate guide coverage — it wraps
   the same SIGGRAPH '25 model behind Replicate's paid API. **Third-party, not
   VAST-official; pricing/terms are Replicate's + the porter's — UNVERIFIED here.**
   If a hosted API is genuinely required, Tripo's first-party API (§2.4) is the
   cleaner commercial contract.

---

## 6. Ranked verdicts

### Top-3 pull-and-wire (commercial-clean, released, automatable)

| Rank | Candidate | Licence (code / weights) | Runs | Why |
|---|---|---|---|---|
| **1** | **SkinTokens / TokenRig** (VAST, 2026) | **MIT / MIT** (weights per 2026-07 audit; re-check HF tag) | Local GPU ≥14 GB VRAM | Newest SOTA per its paper (+98–133% skinning vs baselines), single-pass skeleton+skin, `--use_skeleton` + `--use_transfer` fit both full-rig and skin-only/full-res-transfer needs |
| **2** | **UniRig** (VAST, SIGGRAPH 2025) | **MIT / MIT** | Local GPU >8 GB VRAM | Most battle-tested learned rigger; two-stage design lets you keep its skeleton and re-skin (or vice versa). Caveat: shipped checkpoint is the Articulation-XL2.0 one, not the paper's Rig-XL/VRoid headline model |
| **3** | **Make-It-Animatable v1** (CVPR 2025) | **MIT / MIT (v1)** — v2 weights UNVERIFIED (Hunyuan backbone) | Local GPU + HF Space | Humanoid specialist, sub-second, **Mixamo-native skeleton** = instant access to the Mixamo motion library. v1 only until v2's weight licence is read |

**Wire-up pattern that follows from the whole survey:** TokenRig primary → UniRig
cross-check (keep the better rig per statue, by automated deformation QA) → MIA v1
when a Mixamo-topology rig is wanted → Puppeteer (Apache-2.0, §1.4) as the diversity
vote → GVB/BBW (§4) as the deterministic weight floor under any skeleton →
Corrective Smooth (§4.3) as optional deformation polish. Tripo API (§2.4) as the
paid overflow valve. Everything runs local except the optional valve — no per-rig
fees, no uploads of proprietary statues, no GUI steps, no hand edits.

### Reference-only list (do not pull into a commercial production pipeline)

- **RigNet** — GPLv3 or negotiated UMass commercial licence; superseded baseline.
- **RigAnything** — Adobe Research License (noncommercial) per audits; LICENSE.md
  classified "Other"; HF apache-2.0 tag proposal conflicts — unresolved, so NC posture.
- **TailorRig** (Tencent, Nov 2026) — TailorRig License: academic research only.
  (Read it: its chain-to-bone anti-bleed skinning is the most relevant 2026 idea
  for clothed fighters.)
- **HumanRig** — MIT licence on an empty repo; only the dataset is public
  (dataset licence reported CC BY-NC 4.0, UNVERIFIED). Dataset/design reference.
- **MagicArticulate** — Apache-2.0 but *skeleton-stage release only*; its skinning
  stage is paper-only in the official repo. (Borderline: usable as a skeleton
  second opinion — see §1.5.)
- **AccuRIG 2** — free + commercially usable per Reallusion staff for own-content,
  but GUI/marker workflow (not zero-touch) and an Oct-2026 AI-service EULA that
  muddies free-tier output rights (UNVERIFIED scope). Manual fallback only.
- **Mixamo** — commercially clean (royalty-free for games, Adobe FAQ) but web-GUI
  only, no API, humanoid-only. Benchmark + motion library, not a backend.
- **Auto-Rig Pro** — $50, output clean, but interactive template fitting; mixed
  GPL + proprietary-binary licence bars redistributing the tool.
- **Meshy API** — paid-plan fallback only; free plan = CC BY 4.0 + Meshy ownership
  language; 380K-tri cap forces vendor-imposed decimation.
- **Anything World** — disqualified on facts: decimates anything over 20K verts.
- **Blender bone-heat** — disqualified as a solver (surface diffusion; fails /
  starves fused multi-shell statues). **Maya GVB / Delta Mush** — proprietary
  implementations (and geomBind won't run headless); implement/bake the *algorithms*
  via §4.1/§4.3 instead.
- **UniMate / "UniAnimate"** — motion generation / unverified-as-rigger; consumes
  rigs, doesn't create them.

### Residual verification checklist (one sitting, before first ship)

1. Screenshot the licence tag on HF `VAST-AI/SkinTokens` (weights) and on
   `jasongzy/Make-It-Animatable` (resolve the stale NC-tag report).
2. Read `LICENSE.md` in `Isabella98Liu/RigAnything` verbatim (only item that could
   move RigAnything off the reference-only list — expect it to stay there).
3. Read the three Puppeteer checkpoint cards on HF (any NC term on weights?).
4. Read MIA v2's weight licence / Hunyuan3D 2.1 ShapeVAE terms before touching v2.
5. Pick a permissive tet mesher for the BBW path and verify its licence
   (TetGen itself is GPL/commercial — do not link it blindly).
6. If AccuRIG is ever used for a shipped asset, get Reallusion's commercial-use
   confirmation for that exact version in writing (Oct-2026 AI EULA muddies this).
7. Probe `jasongzy/UniRig`'s Gradio API schema only if a hosted trial is wanted —
   production stays on the local MIT stack regardless.

*End of survey — 2026-11-09. All licence statements above are tied to the primary
sources named in each entry as fetched on that date; items marked UNVERIFIED were
deliberately left unasserted rather than guessed.*
