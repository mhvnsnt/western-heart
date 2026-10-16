# 3D Pipeline Research — October 2026

**Researched:** 2026-10-16. All claims checked against GitHub repos, arXiv papers, and
2026 roundups (3daistudio.com state-of-2026, cinevva.com comparison, dev.to roundup) —
never from training-data memory. License terms quoted from the projects' own repos/cards.

**Our use case:** (1) rank Tripo-style image-to-3D models for making character models from
our T-pose renders; (2) Source `.mdl/.vvd/.vtx` → GLB on Linux; (3) XPS `.mesh/.ascii` →
GLB on Blender 4.x headless; (4) Cycles speed levers for T-pose stills.

Note: the owner builds his Tripo 3D models HIMSELF from our renders — our renders exist so
he can do that faithfully. Image-to-3D here is for OUR side of the pipeline (draft
geometry, reference meshes, game-ready low-polys), never a replacement for his renders.

---

## 1. Image-to-3D, ranked for character models from T-pose renders

### Why T-pose white-void renders are the ideal input
- Neutral pose + white void background = maximum conditioning signal, minimum
  background contamination. Several 2026 tools (e.g. arashsajjadi/local3d) explicitly
  route character inputs through a person-detector/crop stage — our renders skip that.
- **The back is always a hallucination.** Single-image models see front only and invent
  the rest. Expect back-side texture/design drift on every model below.
- Front + side pairs can feed multi-view-aware paths (TRELLIS.2 accepts extra views;
  InstantMesh-style multi-view diffusion) — worth testing, unproven at scale here.
- Output meshes are **dense, non-game-ready tri-soups**. Budget a decimate → quad-remesh
  → bake step (see §5: `instant-meshes` by wjakob, MIT) before any engine use. Textures
  are projection-baked — good enough as reference/Tripo input, not production PBR.

### The ranking

| # | Model | Origin | License (verified) | Speed | Quality | Weights size | Verdict |
|---|-------|--------|-------------------|-------|---------|--------------|---------|
| 1 | **TRELLIS.2** (4B) | Microsoft | **MIT — fully commercial** | ~3s @512 / ~17s @1024 / ~60s @1536 (H100); under 20s on 24GB VRAM @1536 | Best open-source quality 2026; full PBR (albedo/metal/rough), handles open surfaces | Multi-GB (4B params) | **Winner on quality+license. QUEUED — needs Kaggle/24GB lane** |
| 2 | **Stable Fast 3D** | Stability AI | **Community License** — free for research/non-commercial + commercial **under $1M/yr revenue**; enterprise license above. Gated weights, must accept license | Sub-second–seconds; ~5–10s on 4090 | Good; **UV-unwrapped, delighting step, consistent normals, low-poly game-friendly**, per-material rough/metal | ~4 GB | **PULL code now; QUEUE weights.** Best speed/quality trade for drafts |
| 3 | **TripoSR** | Tripo + Stability | **MIT** | <0.5s on A100 — fastest of all | Modest; draft quality, known inverted-face issues SF3D fixed | Small (hundreds of MB) | **PULL — tiny, MIT, instant drafts** |
| 4 | **SPAR3D** | Stability AI | **Community License** (same $1M threshold as SF3D) | <1s | Good; UV-unwrapped GLB + **point-level editing** (delete/duplicate/stretch/recolor points), better backs than SF3D via point-cloud conditioning | Multi-GB | **PULL code; QUEUE weights** |
| 5 | **Hi3DGen** | research | **MIT** | Slower, precision-focused | Best-in-class geometric precision per 2026 roundups | TBD (multi-GB likely) | **QUEUED — verify size/license on Kaggle lane** |
| — | Hunyuan3D 2.1 | Tencent | Custom community license: **NOT valid in EU, UK, South Korea; >1M MAU needs separate Tencent license** | Two-stage shape→paint, heavier | Best-in-class textures/PBR in benchmarks (beats TRELLIS on ULIP/Uni3D texture metrics) | ~15 GB total (shape 3.3B + paint 2B) | **DOCUMENTED ONLY — region-excluded, do NOT pull as pipeline default.** Hosted 3.x platform (3d.hunyuanglobal.com, 20 free gens/day, 3.1 since Jan 2026) noted as a manual option |
| — | Unique3D | AiuniAI | MIT | ~minutes (multi-view diffusion + ISOMER) | Strong 2024-era, superseded by TRELLIS.2/Hunyuan3D | Multi-GB | Document only — skip pull |
| — | InstantMesh | Tencent ARC | code MIT-ish, Tencent weights | ~10s | 2024 SOTA, superseded | Multi-GB | Document only — skip pull |
| — | CRM / LGM | various | open | fast | 2024-era, superseded | — | Document only — skip pull |
| — | SAM 3D (Meta) | Meta | SAM License (commercial OK) | fast | Reconstruction, not generation — outputs Gaussian splat .ply, not mesh | — | Noted, not a mesh generator |

### Closed/hosted (documented, not pulled)
- **Tripo 3.0** — closed API, speed champion (<30s), clean topology; free tier
  **non-commercial** (fact-checked 2026). He already uses Tripo himself — no pull.
- **Meshy 5/6**, **Rodin Gen-2**, **Seed3D 2.0** (ByteDance, SOTA 69–89.9% human-preference
  win rate Apr 2026) — closed APIs, documented only.
- **Dead in 2026: Luma Genie, CSM** — do not build on these.

### Recommendation for our pipeline
1. **Drafts/iteration:** TripoSR (instant, MIT) + SF3D (UV-unwrapped, game-friendly).
2. **Quality pass:** TRELLIS.2 (MIT, best open quality) on Kaggle when the lane is up.
3. **Character backs:** our front+side T-pose pair is the natural input for multi-view
   testing; SPAR3D's point editing is the fallback for fixing hallucinated backs.
4. Hunyuan3D 2.1 stays **out** of the automated pipeline (license). The hosted
   3.x free tier is a legitimate manual tool — 20 free/day — but read output-rights
   terms before building on it.

---

## 2. Source (.mdl/.vvd/.vtx) → GLB on Linux

### Winner: SourceIO — direct import, no decompile step
- **Repo:** `REDxEYE/SourceIO`, **v5.5.3 released 2026-04-08**, actively maintained
  (82 commits since the 5.5.x line). Blender addon, imports `.mdl` **directly** —
  mesh + armature + materials, with **VTF→PNG texture conversion on import**.
- Already present in `~/workspace/tools/source-tools/` (do not re-pull).

### Blender Source Tools — second place, keep for modding
- Valve's official addon imports `.smd`/`.dmx` with excellent rigs (Steam SFM community
  reports better flex/rig fidelity than SourceIO in edge cases), BUT it cannot read
  `.mdl` — you must decompile with **Crowbar first, which is Windows-only** (Wine
  workaround). No clean headless-Linux story.
- Keep it for `.qc` compile / DMX export work (modding direction), not for import.

### Recommended Linux headless recipe
```
SourceIO import (bpy.ops.sourceio.import_mdl)  →  clean (apply scale, fix axes)  →
bpy.ops.export_scene.gltf (Blender's built-in glTF 2.0 exporter) → .glb
```
- Materials: SourceIO rebuilds them; for full PBR GLB output, bake to Principled
  BSDF nodes before export (exporter reads Principled directly).
- Source Engine assets are proprietary Valve IP — study/reverse-engineer per the
  steal-like-an-artist law; never redistribute their assets.

---

## 3. XPS (.mesh/.ascii) → GLB on Blender 4.x headless

### Winner: Valerie-Bosco/XNALara-io-Tools (active fork)
- Original `johnzero7/XNALaraMesh` discontinued (~5 years stale, Blender 2.8x-era).
- **Fork:** `Valerie-Bosco/XNALara-io-Tools` — "patched and improved to support
  **3.6 – 5.2**", updated ~40 days ago, active issue tracker + Discord. This is the
  one.
- Also seen: `mayloglog/XNALaraMesh-blender4.4` (4.4/5.0-only, **binary .xps export
  disabled** — import works; we only need import anyway). Bosco's fork is the safer,
  wider pick.

### Headless recipe (Blender 4.x)
1. Download `XNALara-io-Tools.zip` from the fork's releases (`main_branch_latest`).
2. Install to the user scripts dir (4.2+: "Install from Disk" = unzip into
   `~/.config/blender/<ver>/scripts/addons`).
3. `blender -b --python script.py` where the script does:
   `bpy.ops.preferences.addon_enable(module="XPS Tools")` (verify exact module/
   operator id at wiring time — fork may differ) → call the XPS import operator on
   the `.mesh`/`.mesh.ascii` → `bpy.ops.export_scene.gltf` → `.glb`.
4. Must run under `xvfb-run -a` on this VM (see TOOLS.md — Blender 4.0.2 segfaults
   on bare `-b` without libEGL).

---

## 4. Cycles speed levers for T-pose still renders

Extends — does not replace — `~/workspace/tools/RENDER-SPEED.md` and
`~/workspace/tools/RENDER-2026-OPTIMAL.md` (the Pantera measured numbers). T-pose
stills are single frames, so temporal levers (RIFE, OptiX-flicker) do not apply;
what matters is per-frame cost on simple white-void lighting.

| Lever | Setting | Why it wins on T-pose stills |
|-------|---------|------------------------------|
| **Blender 4.5.12 LTS** | upgrade from 4.0.2 | enables GPU OIDN (`denoising_use_gpu`) — the single biggest win |
| **Low samples + GPU OIDN** | 8–16spp, adaptive threshold 0.1, min 4 | White-void studio lighting converges fast; measured identical-at-100%-crop territory per RENDER-SPEED.md (16spp/threshold 0.05) |
| **Persistent data** | `scene.render.use_persistent_data = True` | One still per character → BVH/scene build amortized across the roster batch |
| **Minimal light paths** | diffuse 2, glossy 1, transmission 0, transparent max | Characters are opaque; cuts bounce waste |
| **Resolution discipline** | 1024–1536px square/pose | Tripo and image-to-3D models condition at ≤1024px; don't render 4K to downscale |
| **Skip on stills** | half-fps+RIFE, OptiX-vs-OIDN-flicker debates | No motion → no temporal artifacts; OIDN on GPU is just free |

Keep Cycles for the owner-facing renders (fidelity law — he builds Tripo models from
these). EEVEE is acceptable only for internal drafts.

---

## 5. Phase 2 pull order (small, one at a time, each committed separately)

| Order | Item | License | Size | Action |
|-------|------|---------|------|--------|
| 1 | **TripoSR** (`VAST-AI-Research/TripoSR`) | MIT | Small (code + sub-GB weights) | PULL |
| 2 | **Stable Fast 3D** (`Stability-AI/stable-fast-3d`) | Community License <$1M OK | Code small; weights ~4 GB gated | PULL code; QUEUE weights |
| 3 | **SPAR3D** (`Stability-AI/stable-point-aware-3d`) | Community License <$1M OK | Code small; weights multi-GB | PULL code; QUEUE weights |
| 4 | **XNALara-io-Tools** (`Valerie-Bosco/XNALara-io-Tools`) | check at pull (fork of johnzero7; verify LICENSE) | Small zip | PULL into `tools/xps-io/` |
| 5 | **instant-meshes** (`wjakob/instant-meshes`) | **unverified** — no LICENSE file in repo (2026-10-16); commonly described as MIT but NOT confirmed — verify at pull | Small C++ | PULL only after license confirmation — quad-remesh for game-ready topology |
| — | TRELLIS.2 (`microsoft/TRELLIS.2`) | MIT | Multi-GB | QUEUED — Kaggle/24GB lane |
| — | Hi3DGen | MIT | TBD | QUEUED — verify size |
| — | Hunyuan3D 2.1 | region-excluded | ~15 GB | EXCLUDED from pulls (license); hosted 3.x noted |

**Queued (not pulled):** anything multi-GB — TRELLIS.2, Hi3DGen, SF3D/SPAR3D weights —
pending the Kaggle GPU lane and per-item license re-verification at pull time.

**Already in tree (do not duplicate):** Blender Source Tools + SourceIO
(`~/workspace/tools/source-tools/`), ToonCrafter, AnimeInbet, RealESRGAN-anime, SPAN,
Kandinsky 6.0, ChibiRigKit, RIFE, BasicPBC, guided-tweening, smart2d, tiny-2d-rig.
