# Auto-Rig Deep Research — 2026 State of the Art

Owner order 2026-10-18: the PR #264 auto-rig wave worked, but it smelled like
hand-tooling. This doc is the real research pass: what exists in 2026, what's
open-source, what we pulled into `tools/auto_rig/`, and the honest gaps.

## 1. The field, 2007 → 2026

| Method | Year | Type | Skeleton | Skinning | License | Verdict |
|---|---|---|---|---|---|---|
| Pinocchio (Baran & Popović) | 2007 | template fit + heat diffusion | template embed | heat diffusion | research code, no clean license | document only — Blender's bone heat IS this method |
| Blender bone heat | — | heat diffusion on mesh | n/a (needs skeleton) | ✅ | GPL (part of Blender) | **CPU baseline, proven on #264** |
| Voxel heat diffuse skinning | — | heat diffusion on voxel grid | n/a | ✅ | GPL (Blender addon) | **pulled as reference impl** |
| RigNet (Xu et al.) | 2020 | GNN: joints + MST + skin | predicted | predicted | **GPLv3** | document only — copyleft, can't vendor |
| TARig (Ma & Zhang) | 2023 | template-aware GNN | humanoid template | predicted | unknown | document only — humanoid-only |
| MagicArticulate (Seed3D) | 2025 | autoregressive transformer | predicted, 1–2s | — | **Apache-2.0** | **PULLED** — best skeleton predictor |
| UniRig (VAST/Tsinghua) | 2025 | autoregressive transformer | predicted | predicted | **MIT** | **PULLED** — skeleton + skinning |
| Puppeteer (Seed3D) | 2025 | transformer + video anim | predicted | predicted | **Apache-2.0** | **PULLED** — rig + video-guided animation |
| RigAnything | 2025 | autoregressive diffusion | predicted, ~2s | pairwise | unknown | watch — no code found yet |
| SMPL/SMPL-X fitting | — | parametric body fit | SMPL joints | SMPL weights | model weights need account | document — heavyweight, human-only |
| Auto-Rig Pro | — | Blender addon | marker-based | heat + corrective | **commercial** | document only — do NOT touch leaked copies |
| Rokoko | — | mocap + retarget | — | — | **commercial** | document only |
| Mixamo | — | auto-rigger service | humanoid | ✅ | Adobe ToS | service only, dying slowly |

Sources: papers + repo pages verified 2026-10-18. Benchmark table (Puppeteer
paper, Articulation-XL2.0): Puppeteer > MagicArticulate ≈ UniRig > RigNet >
Pinocchio on joint/bone metrics; Puppeteer is 2.6× faster than Pinocchio,
3.0× faster than RigNet.

## 2. What we pulled and why

All three permissive-license AI riggers, vendored slim (code + configs +
launch scripts + READMEs + LICENSEs; demo meshes/doc videos excluded — see
each `VENDOR.md`):

- `tools/auto_rig/vendor/magicarticulate/` — Apache-2.0, Seed3D/MagicArticulate.
  Fastest skeleton predictor (4.6 GB VRAM, 1–2 s/mesh). Use for: skeleton
  prediction on unrigged statics, then skin with Blender heat.
- `tools/auto_rig/vendor/unirig/` — MIT, VAST-AI-Research/UniRig. Skeleton +
  skinning prediction, FBX in/out. Use for: full rigs when no good skeleton
  template fits (needs 8 GB+ VRAM).
- `tools/auto_rig/vendor/puppeteer/` — Apache-2.0, Seed3D/Puppeteer. Rig +
  **video-guided animation** — the animation folder is the differentiator:
  animate a rigged model from a video. Use for: motion prototyping.
- `tools/auto_rig/vendor/voxel_heat/` — reference: voxel heat-diffuse
  skinning concept (Blender's method lineage). CPU, robust on dense meshes.

NOT pulled: RigNet (GPLv3 — copyleft would taint the repo), Auto-Rig Pro
(commercial — leaked copies exist, we don't touch them), Pinocchio original
(superseded: Blender bone heat is the same heat-diffusion math, maintained).

Checkpoints are NEVER vendored (GBs). `tools/auto_rig/checkpoints/README.md`
has the exact download commands; they land on Kaggle/Colab, not in git.

## 3. Why rig_repair's pipeline failed its own pilot (failure-mode analysis)

From PR #264's pilot on awa-pop, plus the `tools/rig_repair` README:

1. **`refit.py` (volume-mode skeleton refit) moves joints to wrong places.**
   It casts rays through the mesh on 3 axes and moves each joint to the
   volume center. On arms-up poses the rays exit through the armpit gap and
   the "volume center" lands in empty space — the left arm detached. Ray-cast
   refits assume a closed, convex-ish volume per limb segment; T-pose arms,
   skirts, and capes violate that.
2. **`separate.py` (topology limb/body separation) tears the torso.**
   It flood-fills across the mesh to assign limb regions; thin bridges
   (armpit webbing, tight clothing) let the fill leak — 753 verts wrongly
   reassigned on the pilot. Topology separation needs a watertight,
   single-component mesh; game rips are rarely that clean.
3. **The pipeline is staged Python + one Blender process per stage.**
   Correct for crash isolation, but each stage re-exports the GLB, so errors
   compound and no stage sees the final posed result.

What replaced it in #264 (and is now the CPU baseline in `tools/auto_rig/`):
Blender bone-heat auto-rig (heat diffusion — the Pinocchio skinning method,
battle-tested inside Blender for 15 years) + k-NN weight transfer from a
donor rig for dense Tripo statics. Verified numerically: stretch p99.9
1.06–2.14, under the 2.5 gate, on every clip.

## 4. The wired system (`tools/auto_rig/`)

```
auto_rig.py --in MODEL.glb --out RIGGED.glb --backend {blender-heat|knn|unirig|magicarticulate|puppeteer}
```

- **blender-heat**: normalize (face −Z, feet y=0, scale to height) → build WH
  Mixamo-style skeleton → Blender automatic weights (heat diffusion) →
  export. CPU. This is the #264-proven path, cleaned into one module.
- **knn**: k-NN weight transfer from a donor rigged mesh (pantera.glb).
  For dense statics where Blender's exporter chokes (~1M verts).
- **unirig / magicarticulate / puppeteer**: GPU backends. Run on Kaggle
  (30 h/wk) or Colab via `tools/auto_rig/kaggle/auto_rig_gpu.py`. Predict
  skeleton (+ skinning), map joint names to WH canonical set, merge into GLB.
- **retarget.py**: bone-name canonicalization tables (Mixamo ↔ WH ↔
  Tekken-style names) + optional geometric retarget. The #264 deviation
  (canonicalization instead of geometric retarget) is kept as the default —
  it preserves native skeleton structure; geometric retarget is the fallback.
- **validate.py**: the playable gate — valid glTF, ≥1 skinned mesh,
  Mixamo-style bones present, height 1.5–2.2 m, p99.9 stretch < 2.5 on
  standard clips. Nothing ships without passing.

## 5. Honest gaps — what still needs a human or a GPU

1. **GPU backends are wired, not yet run.** The adapters are written against
   the vendored code, but no Kaggle run has happened in this wave. First GPU
   run is the next step (owner has 30 h/wk Kaggle).
2. **Dense Tripo statics (~1M verts)** still need decimation before Blender
   touches them; the k-NN path handles weights but the exporter chokes.
3. **Fingers.** AI predictors are weakest on hands (UniRig paper notes
   missing/misaligned hand bones). Hand bones still need human review.
4. **Facial rigs** are out of scope — PANTERA RIG RULE (no facial/mouth rig on
   King-based models) stands; face work belongs to the GNM face-rig lane.
5. **Motion retargeting** (wrestling clips → WH skeletons) is the next wave —
   Puppeteer's video-guided animation is the seed, Rokoko-style bone mapping
   tables are in `retarget.py`.
