# 3D Generation Pipeline Research — SOTA Open Models (Late 2026)

**Date:** 2026-10-22
**Worker:** 44 (3D generation pipeline research round)
**User directive (verbatim):** *"Research the current state-of-the-art open-source image-to-3D and text-to-3D models (as of late 2026). Candidates from earlier research: TRELLIS.2 (MIT), TripoSR, Hunyuan3D 2.1 — but check what's newest and best NOW. Goal: our in-house generation pipeline should be the most stacked, most current, best possible — BETTER than Tripo3D's output quality."*
**Scope:** RESEARCH ONLY. No model weights downloaded, nothing on disk. Report, don't build.

**Feeds:** Jin (Eastern Mind) from user's reference photos, creature characters (puma, bear, Godzilla-type, gorilla), any future character from user-provided images.

---

## 1. Executive Summary

As of late October 2026, the open-source image-to-3D frontier is led by **TRELLIS.2** (Microsoft, MIT) as the best all-round open model, with **Hi3DGen** (Stable-X, MIT) holding the raw-geometry-detail crown and **Hunyuan3D 2.1** (Tencent) holding the texture/PBR crown but carrying a license geography caveat. The newest commercial engines (**Hunyuan3D 3.0/3.1**, **Hi3D 3.0/Twinkle3D**) are **hosted-only — their weights were never open-sourced**, so they are API options, not pipeline components. For text-to-3D, no frontier open model is natively text-conditioned; the working pattern is text→image chaining in front of image-to-3D.

**Recommended stack (the "stacked" answer):** **Hi3DGen (geometry) → TRELLIS.2 shape-conditioned PBR texturing → UniRig (auto-rig, humanoids + quadrupeds/creatures) → decimation/retopo → existing Tripo-intake ingest.** All stages MIT-licensed, all runnable weightlessly via hosted APIs (fal.ai / Replicate), no local weights on disk.

---

## 2. Model Comparison Table

| Model | Org / Release | License | Image→3D | Text→3D | Geometry quality | Texture / PBR | Output formats | Topology notes | VRAM (self-host) | Remote inference (no local weights) |
|---|---|---|---|---|---|---|---|---|---|---|
| **TRELLIS.2** (4B) | Microsoft, Nov 2025 | **MIT** | ✅ (primary) | ❌ (no text checkpoint; use TRELLIS v1 or chain) | Excellent — O-Voxel handles open surfaces, non-manifold, internal structures | ✅ Full PBR: base color, roughness, metallic, opacity; 4K textures | GLB | Triangles; built-in decimation/remesh | ≥24 GB official (A100/H100, CUDA 12.4, Linux); 16 GB+ community-usable | **fal.ai `fal-ai/trellis-2`** (REST, queue+webhooks, res 512/1024/1536, texture ≤4096); **Replicate** (fishwowater); HF Spaces demo |
| **Hunyuan3D 2.1** (shape 3.3B + paint 2B) | Tencent, Jan 2025 | Tencent Community License — ⚠️ **commercial-use geography caveat: does not cover EU/UK/South Korea**; attribution required | ✅ (+ multi-view 2mv variant) | ⚠️ chains HunyuanDiT text→image in front of image stage (no native text 3D weights) | Very good (10× over 2.0) | ✅ **Best open textures** — PBR + texture-only repaint mode for existing meshes | GLB, OBJ | Triangle mesh; smart topology on hosted Studio only | 10 GB shape-only / 21 GB texture-only / **29 GB full** (~15 GB with `--low_vram_mode`) | Tencent Cloud API (credits); **WaveSpeedAI** hosts the commercial **v3** engine ($0.30/run); Tencent platform 20 free/day (hosted 3.x, not open) |
| **Hi3DGen** | Stable-X, paper Mar 2025, code Apr 2025 | MIT (per community tracking) | ✅ | ❌ | **Best raw geometric detail** — normal-bridging (NiRNE+NoRLD), beats CraftsMan-1.5, Hunyuan 2.0, TRELLIS v1, Tripo-2.5 in user/artist evals | ❌ **Geometry only — no textures** | Mesh (export) | Triangle mesh | 16 GB+ | HF Spaces demo (free, non-production) |
| **TripoSR** | Stability AI + Tripo, 2024 | MIT | ✅ | ❌ | Lowest of the group (blurry on detail) | Baked UV texture (basic) | OBJ, GLB | Triangle mesh | **~6 GB** | Replicate / various hosts |
| **Stable Fast 3D** | Stability AI, 2024 | Stability Community License (free < $1M revenue) | ✅ | ❌ | Mid | Baked | GLB | **UV-unwrapped** (saves post-processing) | ~8 GB | Replicate |
| **InstantMesh** | 2024 | (check per release) | ✅ multi-view | ❌ | Mid-good | Baked | OBJ/GLB | — | ~12 GB | Replicate |
| Hunyuan3D 3.0 / 3.1 | Tencent, Sep 2025–Jan 2026 | **NOT open** — hosted only | ✅ (hosted) | ✅ (hosted) | Frontier (1536³, 3.6B voxels, 3× over 2.1, character-optimized) | 8K PBR | OBJ/FBX/GLB | Tri/quad smart topology, **rigging built in** | n/a | HY 3D Engine / Tencent Cloud API / 3d.hunyuanglobal.com |
| Hi3D 3.0 (Twinkle3D) | Hi3D (commercial), Oct 2026 | **NOT open** — commercial platform | ✅ (hosted) | via image | 2048³ watertight meshes, 8K PBR, beats 4 commercial systems on object fidelity | 8K PBR | — | Watertight triangles | n/a | hi3d.ai platform + APIs |

**Dead / do-not-build-on (2026):** Luma Genie (Luma pivoted to video), CSM Cube (shut down Jan 2026, acquired by Google).

### Quality ranking for our use case (character + creature generation from images)

1. **Geometry:** Hi3DGen > TRELLIS.2 ≈ Hunyuan3D 2.1 > InstantMesh > Stable Fast 3D > TripoSR
2. **Texture/materials:** Hunyuan3D 2.1 ≥ TRELLIS.2 (full PBR both) > Stable Fast 3D > TripoSR; Hi3DGen = n/a (geometry only)
3. **Fidelity to reference (faces/details):** TRELLIS.2 (O-Voxel sharp features) and Hi3DGen lead; Hunyuan 3.0 (hosted) is the overall frontier but not open
4. **Riggability:** all output static triangle meshes — rigging is a downstream stage, not a model feature. See §4. None output quad topology natively (Tripo's "native quad" is a commercial advantage); plan a retopo step.
5. **License cleanliness:** TRELLIS.2 (MIT), Hi3DGen (MIT), TripoSR (MIT) are clean worldwide. Hunyuan3D 2.1's Tencent license has EU/UK/SK commercial exclusions — route around it if selling there.

**vs Tripo3D (commercial):** Tripo's edges are native quad topology, built-in rigging/animation, and one-click polish. Our stacked open pipeline beats it on: zero per-asset cost at scale, full PBR material control, geometry-detail leadership (Hi3DGen), arbitrary topology (clothing/open surfaces via O-Voxel), fine-tunability (TRELLIS.2 ships training code), and MIT license with no vendor lock-in.

---

## 3. VRAM / GPU Trade-off (user's question, answered directly)

| Model | Min VRAM | Comfortable | Notes |
|---|---|---|---|
| TripoSR | **~6 GB** | 8 GB | The only real option for a small consumer GPU; quality is draft-tier |
| Stable Fast 3D | ~8 GB | 12 GB | Best UV output at low VRAM |
| Hunyuan3D 2.1 | 10 GB (shape) / 21 GB (texture) | **29 GB full** (15 GB low-vram mode, 15–30% slower) | Texture stage is the hog; a 24 GB RTX 4090 can run shape comfortably, full pipeline needs offload |
| Hi3DGen | 16 GB+ | 24 GB | Geometry only — no texture cost |
| **TRELLIS.2** | 16 GB+ (community) | **≥24 GB** (official; A100/H100, Linux, CUDA 12.4) | 4B params. Resolution ladder: 512³ ≈3 s, 1024³ ≈17 s, 1536³ ≈60 s on H100 |

**Bottom line for the user:** nothing at Tripo-beating quality runs on a 6–8 GB card. The quality tier needs 16–24 GB+ VRAM. That is exactly why the pipeline is designed **remote-first** (§5): rent the VRAM per generation via fal.ai/Replicate instead of buying it.

---

## 4. The Missing Half: Rigging (required for fighters AND creatures)

Generation gives a **static mesh**. For WH, every model must be rigged (fighters) — including non-humanoids (puma, bear, Godzilla-type, gorilla, Dorowani). Findings:

- **UniRig** (Tsinghua + Tripo/VAST-AI, SIGGRAPH 2025) — **MIT licensed**, open code + checkpoints. One autoregressive model predicts skeleton hierarchy **and** per-vertex skinning weights for humans, quadrupeds, birds, insects, water creatures, objects (Mixamo/Biped/Quadruped/Bird&Flyer/Insect&Arachnid/Water/Static/Other categories). Inputs: obj/fbx/glb/vrm → outputs rigged FBX/GLB. 1,868 GitHub stars. Successor **SkinTokens** announced (98–133% skinning accuracy gain) — watch, don't adopt yet. **Hosted on Replicate (aaronjmars)** → no local weights needed.
- **RigAnything** (2025 paper, template-free autoregressive rigging, seconds per shape, humanoids→insects) — strong but code availability unconfirmed; backup option.
- Mixamo: free, royalty-free, but **bipeds only** — insufficient for the creature roster.
- Tripo/Meshy/Nira hosted rigging: commercial, per-use.

**Recommendation:** **UniRig as the pipeline's rigging stage** — it's the only open, MIT, creature-capable auto-rigger, and it's literally built by the Tripo team, so it slots into the same intake philosophy.

---

## 5. Remote Inference Options (no weights on local disk — standing constraint)

| Route | What it hosts | Cost model | Fit |
|---|---|---|---|
| **fal.ai** | `fal-ai/trellis-2` (REST API, queue + webhooks, no coldstarts; resolution/texture-size/decimation params) | Pay per compute-second | **Primary gen endpoint** — production-ready, scriptable |
| **Replicate** | TRELLIS.2 (fishwowater), UniRig (aaronjmars), TripoSR, Hunyuan3D 2.1 variants | Pay per second | Gen + rigging without any infra |
| **WaveSpeedAI** | Hunyuan3D **v3** text-to-3D / image-to-3D (commercial 3.0 engine, PBR, face-count + polygon-type control) | **$0.30/run** | Cheapest way to touch the frontier 3.x engine; NOT open, but fine as a per-asset service |
| **Tencent Cloud** | Hunyuan3D 3.x API, 20 free/day on public platform | Credits/free tier | Enterprise path; license geography caveat applies |
| RunPod / Vast.ai / Modal | Any of the above via rented A100/H100 containers | Per-hour GPU rental | Fallback if we ever want private self-hosting without buying GPUs |
| HF Spaces | TRELLIS.2, Hi3DGen demos | Free | Evaluation only, not production |

---

## 6. Recommended Stack ("most stacked, most current, better than Tripo3D")

### Stage 0 — Reference prep (unchanged human step)
User provides reference photo(s) (e.g., Jin's photos) or a text brief. For text-only briefs: generate reference images with any strong image model first (text→image chaining is how Hunyuan3D itself does text-to-3D — this is the industry-standard pattern, not a hack).

### Stage 1 — Generation (primary): **TRELLIS.2 via fal.ai**
- Why: MIT, best all-round open quality, full PBR materials in one pass, O-Voxel handles hard cases (open clothing surfaces, complex creature topology), GLB output drops straight into the engine/Blender.
- Params: 1024³ for production (17 s on H100-class), 1536³ for hero assets; `texture_size` 2048–4096; `decimation_target` tuned to fighter budget.

### Stage 1b — Geometry-max path (hero assets): **Hi3DGen → TRELLIS.2 texture pass**
- Why: Hi3DGen is the measured geometry-detail leader; TRELLIS.2 ships a shape-conditioned PBR texture generator (`app_texturing.py` / `example_texturing.py`) that can texture any mesh. Combines the two crowns. Cost: two stages, more VRAM/time.

### Stage 1c — Fast iteration: **TripoSR (~6 GB, <0.5 s)**
- Draft silhouettes and proportions before spending H100-seconds. MIT, trivially hostable.

### Stage 2 — Rigging: **UniRig (Replicate or self-hosted container)**
- Skeleton + skinning weights for fighters AND creatures (quadruped/bird/water categories cover the whole creature list). Human review of skeleton before skinning (UniRig's own README recommends this for exotic topologies).

### Stage 3 — Retopo / decimation
- fal.ai trellis-2 `decimation_target` param, or Blender (Quadriflow/remesh) in the existing pipeline. Note: open models output triangles; quad topology (Tripo's commercial edge) comes from this retopo step.

### Stage 4 — Ingest into existing Tripo-intake pipeline
- Conform output to the established convention: `roster/<character>/attires/attire<N>/source/` (immutable original) + rigged/processed alongside, same as the Torch A3 and Dorowani A1 intakes. GLB in, GLB out — the intake pipeline doesn't care which generator produced it.

### Text-to-3D
No native open frontier model; use the chained pattern (text→image→TRELLIS.2). Keep watching **Hunyuan 3D Omni** (Tencent-announced open multi-condition model, "on the horizon") and TRELLIS roadmap for a text checkpoint.

---

## 7. Wiring Plan (how it connects to the existing Tripo-intake pipeline)

```
pipeline/gen3d/                      ← NEW, repo-held, no weights
  clients/
    fal_trellis2.py                  ← image → GLB (fal-ai/trellis-2), params: resolution, texture_size, decimation_target
    replicate_unirig.py              ← GLB → rigged GLB/FBX (skeleton + skinning)
    wavespeed_hunyuan_v3.py          ← optional frontier path ($0.30/run, commercial engine)
    triposr_local.py                 ← draft path (~6 GB local, optional)
  stages/
    10_reference_prep.md             ← input spec (photos / text brief → reference images)
    20_generate.md                   ← Stage 1/1b/1c selection logic + QC gates
    30_rig.md                        ← UniRig call + skeleton human-review gate
    40_retopo.md                     ← decimation/retopo to fighter poly budget
    50_ingest.md                     ← conform to roster/<char>/attires/attire<N>/source/ convention
  workflows/
    comfyui_trellis2.json            ← local alternative (ComfyUI native trellis.2 template, MIT)
    comfyui_hunyuan21.json           ← local alternative (ComfyUI-Hunyuan3D-2.1 nodes)
```

- **Secrets:** API keys (fal.ai, Replicate, WaveSpeedAI) go through the Secure Vault / approved connection flow — never in repo files.
- **No weights on disk:** all production paths are remote APIs; the repo holds only client code, stage docs, and ComfyUI workflow JSONs. Local paths (TripoSR draft, ComfyUI) are opt-in and documented as such.
- **Compatibility with standing orders:** output GLB + PBR matches what the Tripo-intake pipeline already consumes; rigging stage replaces the manual/auto-rig bottleneck for both humanoids and the creature roster (puma, bear, Godzilla-type, gorilla, Dorowani).
- **Proof standard:** every intake gets the same proof bar as current intakes (renders + motion capture for jiggle/physics-relevant assets per the Torch A3 spec).

---

## 8. Risks / Open Questions

1. **Hunyuan3D 2.1 license geography** — verify with counsel before any commercial distribution in EU/UK/SK; TRELLIS.2 (MIT) has no such issue and is the safer default.
2. **Hi3DGen texture gap** — its MIT status and geometry crown are per community tracking; verify license file in the Stable-X repo before wiring Stage 1b.
3. **TRELLIS.2 Linux/CUDA-only** — fine for remote (fal.ai/Replicate) and container self-hosting; don't plan a Windows-local path.
4. **Rig quality on exotic creatures** — UniRig recommends human skeleton review for non-standard topologies (four-armed Chatur/Rahkasa, Dorowani). Budget the user's surgical review time there, per the division of labor.
5. **Watch list:** Hunyuan 3D Omni (open), SkinTokens (UniRig successor), TRELLIS text-to-3D checkpoint, Hi3D 3.0 open-sourcing (unlikely — commercial).

---

## 9. Sources

- TRELLIS.2 repo (Microsoft, MIT, 12.4k stars): https://github.com/microsoft/TRELLIS.2
- TRELLIS.2 vs Hunyuan3D 2.1 vs TripoSR comparison (2026): https://triposr.org/blog/hunyuan3d-vs-trellis
- Open-source 3D API roundup: https://www.pixazo.ai/blog/best-open-source-3d-model-generation-apis
- 7-model comparison table (licenses/VRAM): https://www.cmarix.com/blog/top-open-source-ai-models-for-3d-image-generation/
- 2026 generator roundup (commercial + open): https://app.cinevva.com/guides/ai-3d-model-generators
- Hunyuan 3D 3.0 launch (hosted-only, 3.6B voxels): https://www.notebookcheck.net/Tencent-s-new-Hunyuan-3D-3-0-brings-realistic-AI-model-generation-to-developers-and-creators.1116964.0.html
- Tencent Hunyuan 3D global engine/API: https://www.tencent.net.cn/tencent-announces-global-launch-of-hunyuan-3d-engine-to-empower-creators-with-advanced-creation-tools/
- WaveSpeedAI Hunyuan3D v3 API ($0.30/run): https://wavespeed.ai/models/wavespeed-ai/hunyuan3d-v3/text-to-3d
- fal.ai trellis-2 API: https://fal.ai/docs/model-api-reference/3d-api/trellis-2
- Hi3DGen paper (normal bridging): https://arxiv.org/html/2503.22236v1
- Hi3D 3.0 / Twinkle3D paper (commercial, 2048³): https://arxiv.org/abs/2610.11685v1
- UniRig repo (Tsinghua + Tripo, MIT): https://github.com/VAST-AI-Research/UniRig
- RigAnything paper (backup rigger): https://arxiv.org/pdf/2502.09615
- Hunyuan3D-2.1 requirements (10/21/29 GB VRAM): https://deepwiki.com/Tencent-Hunyuan/Hunyuan3D-2.1/2-getting-started
- Hunyuan3D 2.0 guide (pipelines, ComfyUI): https://biff.ai/hunyuan3d-2-a-game-changing-sota-open-source-3d-foundation-model/
