# Photo-to-Fighter — AdaHuman + GAIA integration design

**Date:** 2026-10-23
**Lane:** Future Tech prototyping (research-stage)
**Owner directive (verbatim 2026-10-23):** "Pulling everything from the list and wire it all up and where it'll work and where it's appropriate"
**Status:** RESEARCH-DESIGN — **neither AdaHuman nor GAIA has public code as of 2026-10-23** (verified: GitHub API search finds no `adahuman` repo; the AdaHuman project page says "Code and models will be publicly available for research purposes" with no link; the GAIA project page is a research-demonstration page with no code or model links). Nothing is vendored. The prototype in this PR is the **pipeline as code** (`tools/photo-to-fighter/`): stage contracts, consent/adult gates, and the 3DGS→mesh→rig bridge design, all CPU-testable on synthetic data.

**Companion doc:** `docs/research/FACE-SCAN-PHOTO-TO-3D-2026-10-23.md` — the FACE lane (GNM Head / FLAME / MediaPipe: geometry-first, mesh-first, CPU-viable, wired now). **This doc is the BODY lane (AdaHuman: full-body single-photo → animatable avatar) + the generative head-editing lane (GAIA: identity/expression-disentangled heads).** Read the face doc first; this one does not repeat it.

**The shared constraint:** both AdaHuman and GAIA output **3D Gaussian Splats (3DGS), not rigged meshes**. A Tekken-style fighter needs a skeleton, skinning weights, and a GLB the phone can render. The 3DGS→mesh→rig bridge (§3) is the critical path of this entire design — everything else is plumbing.

---

## 0. TL;DR — the whole picture

| # | Fact | Detail |
|---|------|--------|
| 1 | AdaHuman (NVIDIA, ICCV 2025, arXiv:2505.24877) | Single in-the-wild photo → high-fidelity **animatable 3DGS avatar in standardized A-pose**, "enabling rigging and animation with any input motion". Two innovations: (a) pose-conditioned joint 3D diffusion that synthesizes consistent multi-view images in arbitrary poses *alongside* 3DGS reconstruction at each diffusion step; (b) compositional 3DGS refinement that enhances local body parts via image-to-image refinement and fuses them with a crop-aware camera ray map |
| 2 | GAIA (NVIDIA AMRI lab, SIGGRAPH 2025) | **Generative** animatable head avatars with expression-conditioned Gaussians. Two-branch architecture disentangles **identity and expression**, trained on in-the-wild image datasets. Gaussians embedded in an underlying morphable head model via shared UV parameterization; animatable with blendshape + rigging params (eyes, jaw); photorealistic novel-view synthesis at **43 FPS on an RTX A6000**; interactive viewer for realtime animation/editing |
| 3 | WH pipeline | Photo → (AdaHuman, GPU offline) A-pose 3DGS → 3DGS→mesh extraction → **UniRig auto-rig** (MIT, already vendored in `tools/auto_rig/` via PR #273) → texture bake (WWE-style photo projection + PBR) → WH fighter assembly → attire slot → select screen |
| 4 | GAIA's role | Head-editing pass: identity-preserving expression control for the avatar's head; expression library for intros/win poses (SHOW-set; show-animation lock applies) |
| 5 | Code status | NEITHER released (2026-10-23). Pipeline contracts + consent gates prototyped now; real models plug in later |
| 6 | GPU | AdaHuman inference: high-end NVIDIA (24GB+ class), cloud/workstation. GAIA interactive: RTX A6000-class. **Nothing runs on the phone; nothing runs on this VM** — the game only ever receives a baked GLB |
| 7 | License | NVIDIA research code ships under the NVIDIA Source Code License-NC (non-commercial, research/evaluation only; derivatives inherit the limitation). AdaHuman's "for research purposes" promise matches this pattern. **NC-licensed code/weights never enter `game/` or ship** — research lane only until a commercial grant exists |

---

## 1. AdaHuman deep dive — what it gives the creation suite

**Paper:** AdaHuman: Animatable Detailed 3D Human Generation with Compositional Multiview Diffusion — Huang, Yuan, Li, Kautz, Iqbal (NVIDIA). ICCV 2025, pp. 13533–13543. arXiv:2505.24877. Project: https://nvlabs.github.io/AdaHuman/

**Why it's the right body primitive for photo-to-fighter:**
1. **Single in-the-wild photo in.** No multi-camera rig, no scan booth — a selfie works. That's the WWE-2K-face-scan UX bar, extended to the whole body.
2. **A-pose out, by construction.** The model generates the avatar *reposed into a standardized A-pose with minimal self-occlusion* — i.e., it outputs exactly the pose an auto-rigger wants. This is not an accident: the paper frames A-pose generation as the enabler for "rigging and animation with any input motion."
3. **Detail where it counts.** The compositional refinement module enhances local body parts (face, hands — the parts that usually break in single-image reconstruction) and fuses them coherently.

**What it does NOT give us:** a mesh, a skeleton, skinning weights, PBR materials, or a game-ready file. Output is a 3DGS splat cloud. §3 covers the bridge.

---

## 2. GAIA deep dive — what it gives the creation suite

**Paper:** GAIA: Generative Animatable Interactive Avatars with Expression-conditioned Gaussians — Yu, Li, Sun, Shapira, Park, Stengel, Chan, Li, Wang, Nagano, De Mello (NVIDIA). ACM SIGGRAPH 2025. Project: https://research.nvidia.com/labs/amri/projects/gaia/

**Why it matters for WH:**
1. **Identity/expression disentanglement.** The two-branch generator learns identity and expression as separable controls from in-the-wild image datasets. For a fighting game this is gold: one head, many expressions — intros, win poses, damage reactions — without rebuilding geometry.
2. **Morphable-model grounding.** Gaussians are embedded in an underlying 3D morphable head model via shared UV parameterization, and animation follows blendshape + rigging parameters (eyes, jaw). That means GAIA heads speak a control language (blendshapes) the game already understands — the face doc's MediaPipe blendshape work (`FACE-SCAN` §2.3) is the same vocabulary.
3. **Interactive speed.** 43 FPS generation+rendering on an RTX A6000 with an interactive viewer — this is an *authoring workstation* tool, not a batch job.

**Honest limits for our use:**
- GAIA is **generative** (latent-space heads), not photo→head. Getting *your* face into GAIA means latent inversion or fine-tuning — a research task, not a turnkey step. Phase 3 treats it as such.
- GAIA is **heads only**. The body still comes from AdaHuman. The head/body seam (neck topology, skin tone match) is a real integration task — see §4 Stage 5.
- No code released. The design below assumes the paper's described interface (blendshape + rigging params in/out).

**How GAIA complements the face doc:** the face doc's GNM/FLAME/MediaPipe lane is the *wired-now* path (parametric mesh, CPU-viable). GAIA is the *quality-ceiling* path (photorealistic Gaussian heads, GPU, later). They converge at the blendshape control layer — work done on one transfers to the other.

---

## 3. The 3DGS bridge — critical path (the whole list of options)

Splats must become a rigged mesh. Every option, no cherry-picking:

| # | Method | What it does | License (check at pull time) | Verdict |
|---|--------|--------------|------------------------------|---------|
| 1 | **SuGaR** (Surface-Aligned Gaussian Splatting) | Aligns Gaussians to surfaces, extracts a mesh from a trained 3DGS scene | Research-origin; verify LICENSE file before pulling | Primary candidate — purpose-built for splat→mesh |
| 2 | **2DGS** (2D Gaussian Splatting) | Surfel-based splatting with better surface reconstruction; mesh via TSDF fusion | Verify at pull time | Strong alternate — better thin surfaces (fingers, ears) |
| 3 | **Gaussian Opacity Fields / GOF** | Mesh extraction directly from 3D opacity fields | Verify at pull time | Candidate — no separate surfacing step |
| 4 | **Multiview render → photogrammetry** | Render N views of the splats, run classic MVS + marching cubes | Tool-dependent (open MVS pipelines exist) | Fallback — lossy, but zero splat-meshing research risk |
| 5 | **Direct splat rendering in-game** | Render 3DGS natively in the Three.js client (splat viewers exist) | Inria/MPII NC terms on the 3DGS technique itself | ❌ REJECTED for fighters — no skeletal animation, no hitboxes, breaks the Tekken fighter contract; possibly viable later for *arena statics*, not characters |

**License flag on the foundation:** the original 3D Gaussian Splatting technique is © Inria / Max Planck, distributed under its own non-commercial-flavored license (per the CF-3DGS licensing summary). Any splat-meshing method inherits that consideration for the *technique*, separate from each method's code license. Documented here so nobody is surprised later.

**After meshing:** cleanup (watertight, retopo to WH humanoid proportions) → **UniRig** (MIT, already in `tools/auto_rig/`, PR #273) predicts skeleton + skinning → `validate.py` playable gate → WH skeleton. This reuses the exact intake path Tripo models already travel — photo-fighters are not a special case downstream of the rig.

---

## 4. Pipeline architecture — stage contracts

```
① INTAKE (likeness_policy.py — CPU, in repo)
   photo (front-facing, ≥1024px, neutral expression preferred)
   → CONSENT GATE: user's own face OR AI-generated face ONLY
   → ADULT GATE: subject must be an adult (ALL CHARACTERS ARE ADULTS)
   → NO-FAMOUS-FACES: third-party/celebrity faces rejected
      (canon law: game ships no famous names — faces follow the same rule)
   → likeness record logged per avatar (who consented, when)
  │
  ▼ ② ADAHUMAN (GPU service — cloud/workstation, NOT in repo)
  │   photo → A-pose 3DGS avatar (.ply splats) + canonical turntable views
  │   API: POST /v1/avatars {photo, pose:"a-pose", refine:true} → job → splats
  │
  ▼ ③ 3DGS → MESH (§3 method, GPU-assisted)
  │   splats → watertight mesh → scale to WH humanoid proportions
  │   → proportions check vs roster height/scale metadata
  │
  ▼ ④ AUTO-RIG (tools/auto_rig/ — in repo, MIT UniRig)
  │   mesh → skeleton + skinning weights → validate.py playable gate
  │   → WH fighter skeleton (same contract as Tripo intake)
  │
  ▼ ⑤ TEXTURE (tools/texture-pipe/ — in repo)
  │   WWE-style photo→UV projection (MediaPipe landmarks align eyes/nose/mouth
  │   automatically — the step WWE 2K makes the player do by hand) + PBR bake
  │   → albedo/normal/roughness; 4K maps optional (cf. KeenFace API lane)
  │
  ▼ ⑥ GAIA HEAD PASS (GPU workstation — Phase 3, when code drops)
  │   head region → GAIA latent space → identity-locked expression library
  │   (neutral, intro-smirk, win-grin, damage-grimace — SHOW-set only)
  │   → neck-seam blend + skin-tone match to body
  │
  ▼ ⑦ FIGHTER ASSEMBLY (existing: tools/wire-fighter/)
      body + head → attire slot → select-screen entry
      → DISPLAY ORDER LAW: Tripo models first; the photo avatar is a
        USER attire (never overrides), per ATTIRE ORDER 5-7 RULE
      → played verification: T-pose + idle renders viewed,
        proof-harness fight reaches "round":"fight" with no [pageerror]
```

**Menu flow (functional spec for the menus lane — UI itself is rebuilt from teardowns, never hand-tooled):**
Character Customization → New Fighter → Appearance → Photo Import → consent screen (the §4 gates, plain-language) → capture/upload → offline processing job with progress → A-pose preview → parametric fallback sliders (face doc's GNM/MPFB2 lane) for fixes → confirm → attire saved. When the UI lane builds this, every screen cites its teardown source in `game/ui_sources.json` per the ui_sources gate.

---

## 5. GPU requirements — the whole list

| Stage | Hardware | Where it runs | Notes |
|-------|----------|---------------|-------|
| AdaHuman inference | NVIDIA 24GB+ (A6000/A100/H100 class), CUDA | Cloud (vast.ai/runpod-class) or crew workstation | Batch/offline; minutes per avatar expected |
| 3DGS → mesh (SuGaR/2DGS/GOF) | GPU strongly preferred; CPU possible but slow | Same box as AdaHuman | Keep on the GPU box — don't move splats around |
| UniRig auto-rig | 8GB+ CUDA for the GPU backend; CPU backends exist in `tools/auto_rig/` | VM-OK via CPU backends | Already vendored (PR #273) |
| GAIA interactive editing | RTX A6000-class for 43 FPS | Crew workstation | Authoring only; baked expressions ship, not the model |
| Texture bake / projection | CPU-OK | VM-OK | `tools/texture-pipe/` |
| Fighter assembly / verification | CPU-OK | VM-OK | Existing pipeline |
| **Phone (player device)** | — | — | **Renders the final GLB only. Zero AI on device, ever.** |

Cost note (per the standing directive to maximize free resources): AdaHuman/GAIA inference wants a cloud GPU by the hour or a crew workstation with a 24GB+ card — the VM's CPU-only profile cannot do this stage. Budget it as an offline batch cost, not a runtime cost.

---

## 6. Prototype delivered in this PR (`tools/photo-to-fighter/`)

CPU-runnable, std-lib + numpy only, synthetic-data tests — the pipeline as code, with backends injectable (real GPU services swap in without changing the orchestration):

| File | What it is |
|------|-----------|
| `stages.py` | Stage I/O contracts as dataclasses: `IntakeSpec` → `SplatAvatar` → `GameMesh` → `RiggedFighter` → `TexturedFighter` → `PhotoFighter`; per-stage `validate()` methods encoding the real constraints (photo resolution, splat count ranges, watertight flag, skeleton joint list, texture set completeness) |
| `likeness_policy.py` | The §4 gates as code: `check_consent()`, `check_adult()`, `check_no_famous_face()`, `log_likeness_record()` — policy failures raise, they don't warn |
| `pipeline.py` | `PhotoToFighterPipeline` orchestrator: runs stages in order with injected backends (`StubAdaHuman`, `StubMesher`, `StubRigger`, `StubTexturer`, `StubGaiaHead`); each stub documents the real service's exact I/O so swapping is mechanical |
| `README.md` | Stage contracts, the §4.2-style API specs for the future GPU services, "when code drops" runbook |
| `tests/test_pipeline_contract.py` | Happy-path synthetic run end-to-end; gate rejections (minor / celebrity / no-consent); contract validation failures (bad photo spec, non-watertight mesh, incomplete texture set) |

Run: `python3 -m pytest tools/photo-to-fighter/tests/ -q` (or `python3 tools/photo-to-fighter/tests/test_pipeline_contract.py`).

**Honest boundary:** stubs synthesize plausible stage outputs (seeded); they prove the orchestration, gates, and contracts — not the AI. The AI arrives with the model releases.

---

## 7. License transparency — the whole list

| Component | License | Shippable? |
|-----------|---------|-----------|
| AdaHuman code/weights | NOT released; paper promises "publicly available for research purposes" → expect **NVIDIA Source Code License-NC** (non-commercial, research/evaluation only; §3.3 use limitation; derivatives must carry the limitation; NVIDIA + affiliates excepted) | ❌ research lane only |
| GAIA code/weights | NOT released; no promise stated → expect NVIDIA SCL-NC if released | ❌ research lane only |
| 3D Gaussian Splatting technique (Inria/MPII) | Own non-commercial-flavored license | ⚠️ technique-level flag; document, don't assume |
| SuGaR / 2DGS / GOF (mesh extraction) | Verify LICENSE at pull time | TBD |
| UniRig | **MIT** ✅ (already vendored, PR #273) | ✅ |
| GNM Head | **Apache-2.0** ✅ (face doc) | ✅ |
| FLAME 2023 Open | **CC-BY-4.0** ✅ (face doc) | ✅ attribution |
| MediaPipe Face Landmarker | **Apache-2.0** ✅ (face doc) | ✅ |
| KeenFace API | Commercial, pay-as-you-go (face doc) | ✅ paid lane |
| **This PR's code** (`tools/photo-to-fighter/`) | WH-original, repo license — contains no NVIDIA code, weights, or derived artifacts | ✅ |

**Rules that follow from this table:**
1. NC-licensed code/weights never enter `game/`, never ship, never run on player devices. Research lane only.
2. Avatars *generated* with NC-licensed models need a commercial grant from NVIDIA before they ship in any commercial context. (Sale status: the owner has not declared a sale track — but clearance is documented now, not discovered later.)
3. The likeness policy (§4 gates) is independent of copyright: even with clean code licenses, a real person's face needs consent.

---

## 8. Roadmap

- **Phase 0 (this PR):** stage contracts + consent gates + design doc. Done.
- **Phase 1 — AdaHuman code drop:** run on a cloud GPU box against 5 consented-adult crew photos; measure splat quality; evaluate §3 meshing options head-to-head (fidelity on hands/face, watertight rate, time); publish the comparison.
- **Phase 2 — full-pipeline pilot:** one photo → one playable test-slot fighter → T-pose/idle renders viewed → proof-harness fight. Photo-fighter enters as a *user attire*, never a default.
- **Phase 3 — GAIA code drop:** latent-inversion spike for photo→GAIA-head; expression library pilot (SHOW-set); neck-seam solution.
- **Phase 4 — creation-suite wiring:** spec feeds the menus lane (teardown-sourced UI per owner law); parametric fallback sliders from the face doc stay as the no-GPU path.

**Fallback if NVIDIA never releases:** the face doc's wired-now lane (GNM + FLAME + MediaPipe + MPFB2, all permissive licenses, CPU-viable) already delivers photo-to-face; the body stays Tripo/sculpt-based. This design loses nothing — the contracts make the GPU path additive.

---

## 9. Risks and limits

1. **Neither model is released; timelines unknown.** Mitigation: contracts are built from the papers' published interfaces; the permissive-license face lane proceeds independently.
2. **3DGS→mesh fidelity.** Hands, teeth, and thin geometry are the known failure points of splat meshing — the Phase 1 head-to-head exists to measure exactly this.
3. **A-pose assumption.** Loose clothing, occlusion, or non-frontal photos degrade reconstruction — intake validation (§4 gates) rejects bad inputs early with actionable messages.
4. **Likeness/deepfake.** The consent/adult/no-famous-faces gates are code, not documentation. Real-person faces without consent never enter the pipeline.
5. **ALL CHARACTERS ARE ADULTS.** Enforced at intake (§4, `likeness_policy.py`) — a photo failing the adult gate stops the pipeline, no exceptions.
6. **Canon fit.** A photo-fighter is the player's creation in the player's attire slot — it never alters canon roster fighters, bios, or the Nine-Souls setting.
7. **No GPU on this VM.** All heavy stages are cloud/workstation; the contract code and tests are CPU-only by design.

---

## Sources

- AdaHuman project: https://nvlabs.github.io/AdaHuman/
- AdaHuman paper (arXiv): https://arxiv.org/abs/2505.24877
- AdaHuman (ICCV 2025 Open Access): https://openaccess.thecvf.com/content/ICCV2025/html/Huang_AdaHuman_Animatable_Detailed_3D_Human_Generation_with_Compositional_Multiview_Diffusion_ICCV_2025_paper.html
- GAIA project: https://research.nvidia.com/labs/amri/projects/gaia/
- GAIA paper (PDF): https://d1qx31qr3h6wln.cloudfront.net/publications/sig25_gaia_paper.pdf
- NVIDIA Source Code License-NC text: https://nvlabs.github.io/stylegan2/license.html
- Scout entry: `docs/research/CUTTING-EDGE-SCOUT-2026-10-23.md` §10
- Companion (face lane): `docs/research/FACE-SCAN-PHOTO-TO-3D-2026-10-23.md`
- Auto-rig (vendored): `tools/auto_rig/` (PR #273)
- Pipeline code: `tools/photo-to-fighter/`
