# Cutting-Edge Research Scout — 2026-10-23

**Scout directive (user verbatim 2026-10-23):** "this is almost like M Dickey meets Tekken meets all those other games that we're pulling in plus any other open source we can pull in. Any other stuff that's similar to that Purdue University project like any type of cool stuff you can find that's like actually do research on that you can pull in and any of those directions."

**Context:** The Purdue Dissectible Anatomy pull (SIGGRAPH 2026, DestructibleVoxelSystem, MIT) was the template win. This doc scouts for more finds in the same spirit: cutting-edge research + open-source code that levels up the game.

**Vision frame:** New-age MUGEN meets MDickey meets Tekken. MDickey is the template for all the user's games in one multiverse; Western Heart becomes the engine.

---

## TIER 1 — Pull immediately

### 1. UniRig — AI auto-rigging (SIGGRAPH 2025)
- **What:** One model to rig them all. Autoregressive skeleton generation + bone-point cross-attention for skinning weights. Trained on Rig-XL (14,000+ rigged models). 215% rigging accuracy improvement, 194% motion accuracy over prior methods. Handles humans, creatures, mechanical objects.
- **Why it's cool:** Drop in any Tripo/SmutBase/creation-suite model → get a production-quality rig + skin weights in 2-5 minutes vs 8-16 hours manual. ComfyUI-UniRig wrapper exists for one-click use.
- **License:** MIT (code). ✅
- **Source:** https://github.com/VAST-AI-Research/UniRig
- **How we'd use it:** Tripo intake pipeline + creation suite auto-rig. Every user-created fighter gets auto-rigged on import.
- **Pull difficulty:** Medium — needs CUDA GPU 8GB+ for inference. VM has no GPU; run on Grok's machine or cloud.

### 2. FightingICE / DareFightingICE — fighting game AI research platform
- **What:** Open-source fighting game AI competition platform from Ritsumeikan University (Japan). Running since 2015. Java + Python APIs, OpenAI Gym wrapper, gRPC interface. 16.67ms decision budget, 15-frame human-reaction delay built in. Sound-design track for blind AI.
- **Why it's cool:** A decade of fighting-game AI research (MCTS, PPO, self-play, diversity-based RL) built on this platform. Directly applicable to WH's CPU opponent AI.
- **License:** Open source (academic). ✅
- **Source:** https://www.ice.ci.ritsumei.ac.jp/~ftgaic/index-2.html | GitHub: TeamFightingICE
- **How we'd use it:** CPU AI training methodology. Study winning agents' approaches (MCTS + rolling horizon evolution won 2020). Adapt frame-data-driven decision making.
- **Pull difficulty:** Low — it's a research platform, pull techniques not code.

### 3. Semantic-Aware Motion Encoding — topology-agnostic retargeting (arXiv May 2026)
- **What:** Decouples motion from exact bone hierarchy via semantic joint alignment. Zero-shot cross-species retargeting without paired data. High-fidelity on human + animal datasets.
- **Why it's cool:** Retarget Tekken animations to ANY WH character — different proportions, extra limbs, creatures — without manual rig mapping. Directly solves our retargeting bottleneck.
- **License:** Research (check repo). Likely permissive.
- **How we'd use it:** Animation retargeting pipeline. Tekken → WH character motion transfer.
- **Pull difficulty:** Medium — research code, needs integration work.

### 4. jspdown/cloth — WebGPU XPBD cloth
- **What:** Real-time cloth simulation entirely on GPU via WebGPU compute shaders. XPBD with graph-coloring parallel constraint solving, sub-stepping.
- **Why it's cool:** Web-native (matches our Three.js stack). No CUDA needed. Cloth for costumes, hair, capes.
- **License:** Check repo (likely MIT).
- **Source:** https://deepwiki.com/jspdown/cloth
- **How we'd use it:** Costume cloth, hair dynamics, cape physics in-game.
- **Pull difficulty:** Low-Medium — WebGPU, integrates with Three.js.

### 5. SurRoL — MPM soft-body surgical sim
- **What:** Open-source surgical robot simulator. MPM (Material Point Method) + Neo-Hookean soft tissue in Taichi (GPU parallel). Physically interpretable, plausible visuals.
- **Why it's cool:** MPM handles large deformations better than FEM for soft tissue. Direct upgrade path for our Jolt soft-body work.
- **License:** Open source (check).
- **Source:** https://arxiv.org/abs/2402.01181v1
- **How we'd use it:** Next-gen tissue deformation beyond Jolt. Muscle/fat jiggle v2.
- **Pull difficulty:** Medium — Taichi dependency, research-grade code.

---

## TIER 2 — Strong candidates

### 6. NVIDIA Isaac for Healthcare — surgical physics framework
- **What:** Open-source medical physics simulation. Classical layer (Warp + Newton engines: contact, friction, rigid/flexible dynamics) + Cosmos-H Dreams (generative AI predicting soft-tissue deformation in real time).
- **Why it's cool:** Production-grade soft-tissue sim from NVIDIA, open-sourced. Newton physics engine went GA April 2026.
- **License:** Open source (NVIDIA).
- **Source:** https://isaac-for-healthcare.github.io
- **How we'd use it:** Tissue deformation reference. Newton engine for rigid/flexible coupling.
- **Pull difficulty:** Medium — NVIDIA stack, GPU needed.

### 7. XRTailor — dual-mode cloth (XPBD + FEM)
- **What:** Cloth sim with Swift Mode (XPBD, 4-10 iterations, real-time) and Quality Mode (FEM, 200 iterations, offline). SMPL/GLTF input pipelines.
- **License:** Open source (openxrlab).
- **Source:** https://deepwiki.com/openxrlab/xrtailor
- **How we'd use it:** Costume pipeline — swift mode in-game, quality mode for creation-suite previews.
- **Pull difficulty:** Low-Medium.

### 8. Velvet — CUDA XPBD cloth (Flex alternative)
- **What:** CUDA-accelerated XPBD cloth engine. Open-source alternative to NVIDIA Flex.
- **License:** Open source.
- **Source:** https://deepwiki.com/vitalight/Velvet
- **How we'd use it:** High-performance cloth if we go native; reference for WebGPU port.
- **Pull difficulty:** Medium — CUDA only.

### 9. SCRIPT — diffusion policy for physics-based humanoid control
- **What:** Language-driven physics-based humanoid control via Joint Action-State-Text Diffusion Transformer. "Punch like a boxer" → physically believable motion.
- **Why it's cool:** Natural-language → character animation. Future creation-suite feature: describe a move, get animation.
- **License:** Code planned for release.
- **How we'd use it:** Long-term — AI move generation in creation suite.
- **Pull difficulty:** High — research stage, no code yet.

### 10. AdaHuman / GAIA — 3D Gaussian avatars (NVIDIA)
- **What:** Animatable 3D humans from single image (AdaHuman) / expression-conditioned Gaussian avatars (GAIA, SIGGRAPH 2025).
- **Why it's cool:** Photo-to-fighter pipeline. GAIA disentangles identity/expression.
- **License:** Research (NVIDIA, may not be open).
- **Source:** https://nvlabs.github.io/AdaHuman/ | https://research.nvidia.com/labs/amri/projects/gaia/
- **How we'd use it:** Face-scan / photo-to-3D character creation.
- **Pull difficulty:** High — research code, GPU heavy.

---

## TIER 3 — Technique reference

### 11. Tencent "Hidden Ones" AI fighting tech (GDC)
- **What:** AI generates in-between frames in real time for fighting game animation. Self-play trains per-character AI agents ("millions of rounds"). 400 characters trained in a week vs a year manually.
- **Why it's cool:** Proves AI in-betweening works for fighting games at scale. Their roadmap: physics-integrated motion generation.
- **License:** Proprietary — technique only.
- **How we'd use it:** Validation for our AI animation direction. Self-play methodology for CPU AI.
- **Pull difficulty:** N/A (not open).

### 12. MDickey "move melding" — procedural move combination
- **What:** Wrestling Empire's system: combine moves in real time (hurricanrana-to-piledriver). Physics-based animation where "anything can happen at any moment." Every new move adds a new counter + hybrid.
- **Why it's cool:** This IS the MDickey magic — procedural, combinatorial, physics-driven. Not keyframed.
- **License:** Proprietary — concept only.
- **How we'd use it:** Design inspiration for WH grappling: procedural throw combinations, physics-based counters.
- **Pull difficulty:** N/A — design study.

### 13. voro++ — Voronoi diagram library
- **What:** Fast Voronoi computation library. Used in openFrameworks destruction demos.
- **License:** BSD.
- **How we'd use it:** Arena destruction (Red Faction-style Geo-Mod). Procedural fracture.
- **Pull difficulty:** Low.

### 14. Skeletal-Driven Animation via Neural Deformation Gradients (2026)
- **What:** Anatomically consistent animation of bones/muscles/skin at interactive frame rates. Open access (CC BY-NC).
- **License:** CC BY-NC (non-commercial — research only).
- **Source:** https://cg.cs.tu-dortmund.de/publications/2026-ndg.pdf
- **How we'd use it:** Technique reference for anatomy-driven animation.
- **Pull difficulty:** Medium.

---

## MDickey multiverse notes

Per user 2026-10-23: MDickey is the template for ALL the user's games in one connected multiverse. Western Heart becomes the engine/template.

Key MDickey systems to study (from Wrestling Empire):
- **Booking mode:** territory control, ratings, contracts, promotion management
- **Roaming mode:** open-world backstage sandbox
- **Career mode:** 350 opponents, 10 rosters, shared universe
- **Move melding:** real-time procedural move combination
- **No loading times:** retro-style performance priority

These map to WH's Heart and Mind Within (story/career) + booking/management layer.

---

## Pull priority

1. **UniRig** — biggest immediate win for creation suite + Tripo intake
2. **FightingICE** — CPU AI methodology (free, just study)
3. **jspdown/cloth** — web-native cloth for costumes
4. **Semantic retargeting** — solve animation retargeting bottleneck
5. **SurRoL/MPM** — next-gen soft tissue

---

## Sources

- SIGGRAPH 2025/2026 papers and recaps
- arXiv (cs.GR, cs.CV, cs.RO)
- Ritsumeikan ICE Lab (FightingICE)
- NVIDIA Research (Isaac Healthcare, AdaHuman, GAIA)
- MDickey Wiki / TV Tropes / Wrestling Estate interview
- GameDev.net, 80.lv
