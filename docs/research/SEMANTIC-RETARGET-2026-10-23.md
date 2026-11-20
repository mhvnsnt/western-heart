# Semantic-Aware Motion Encoding — integration report (2026-10-23)

**User directive (verbatim 2026-10-23):** "Pulling everything from the list
and wire it all up and where it'll work and where it's appropriate"

**Item:** Semantic-Aware Motion Encoding (arXiv May 2026) — topology-agnostic
motion retargeting via semantic joint alignment.

## 1. The paper

- **Title:** "Semantic-Aware Motion Encoding for Topology-Agnostic Character
  Animation" (SATA)
- **Authors:** Zongye Zhang, Yuzhuo Cui, Qingjie Liu, Yunhong Wang
  (Beihang University)
- **Venue:** arXiv:2605.27055 (26 May 2026), accepted ICML 2026
- **Code:** https://github.com/zzysteve/SATA — **license Apache-2.0**
  (verified via GitHub API `license.spdx_id`; permissive, attribution only)
- **Demo:** https://huggingface.co/spaces/SteveZh/SATA

**Core claim:** motion can be decoupled from exact bone hierarchy. A
semantic-aware topology-agnostic autoencoder learns a unified latent motion
manifold across species, enabling **zero-shot cross-species retargeting
without paired data** — no canonical joint set, no source-target motion
pairs, no hand-crafted joint correspondences (Sec. 3).

## 2. Methodology (studied from the paper, Sec. 3 + appendices)

**Sec. 3.1 — Topology-agnostic graph representation.** A motion frame is an
undirected graph `G=(V,E,E_f,F_s,F_m)`. Static node features
`F_s=(X_g, X_l, X_t)`: global offset w.r.t. root, rest-pose coordinate
relative to parent, and **encoded joint semantic features**. Edge features
`E_f`: topological depth and reverse depth. Dynamic features
`F_m=(q, x, v_q, v_x, r, c)`: 6D rotations (Zhou et al. 2019), relative
positions, rotational/linear velocities, root motion, foot contacts.

**Sec. 3.2 — Semantic-Aware Feature Modulation.** MLLM (Gemini 2.5 Pro)
generates taxonomic-neutral functional descriptions per joint
(e.g. "the pelvis and hip root anchor" — Table 11); a frozen T5 encoder
embeds them into `X_t`. FiLM-style modulation
`x̂ = LN(z_m)⊙(1+γ)+β` with `[γ,β]=Ψ(Φ([z_s;z_t]))` plus a gated residual
(eq. 1–3) aligns functional correspondences across species.

**Sec. 3.3 — Spatio-temporal interleaved graph VAE.** GINEConv + spatial
Transformer for bio-constraints, temporal Transformer for dynamics;
spatial max-pool → topology-independent latent; decoder conditioned on
target `{X'_t, X'_g, X'_l}` predicts `(q, r, c)` → recovered via FK.

**App. D.2 — Retarget metric:** character-normalized MSE
`E=1000·Σ|p−p̂|²/(T·J·H²)` (SAN, Aberman et al. 2020).

**Results:** beats SAME/MoMask/AniMo on AT-HumanML3D (80.5k seq) and
AT-AniMo4D (30k seq, 115 species); zero-shot biped→quadruped preserves
motion intentionality. Description variants (Table 12) and MLLM variants
(Table 13) show robustness to paraphrase.

## 3. Where it wires in (WH animation pipeline)

**The bottleneck it solves:** `game/js/t3anims.js` `retargetT3Clips()`
maps Tekken clip bones to fighter rigs **by bone name** against a
hardcoded canonical list (`['Hips','Chest','Head','LeftShoulder',...]`).
Any WH character whose rig doesn't use those exact names/topology —
creatures (Gon), extra limbs (Chatur's four arms), non-humanoid builds —
needs manual rig mapping today. SATA's semantic alignment removes that:
joints match by *functional meaning*, never names.

**What was built:** `tools/anim-retarget/` — a WH-native, dependency-free
(numpy-only) implementation of the paper's **semantic joint alignment**
core:

| file | paper section |
|---|---|
| `semantic_tags.py` — functional description protocol + TF-IDF embedding (offline stand-in for MLLM+T5) | Sec. 3.2, Table 11 |
| `graph_rep.py` — topology-agnostic graphs, direction-free structural descriptor, semantic-spatial correspondence | Sec. 3.1, 3.2 |
| `semantic_retarget.py` — CLI: correspondence → rotation transfer → root scaling → wh-anim/1 export + FK validation | Sec. 3.3, App. D.2 |
| `quat.py` — quaternion/FK utilities | — |
| `tests/test_semantic_retarget.py` — 5 real-data tests | — |

**Documented deviation:** the paper trains the full VAE on 110k sequences;
this tool implements the alignment core in training-free analysis mode
(no torch/checkpoints). The mechanism — functional correspondence from
semantic tags + spatial structure, no names, no manual maps — is fully
preserved. See Sec. 5 for the checkpoint-backend upgrade path.

**Wiring status:** offline intake path (complements `retargetT3Clips`,
doesn't replace it yet). Run per bank/slot to bake `wh-anim/1` clips for
non-standard rigs → register in `T3_BANKS`/`SOURCE_TO_BANK` as usual.
No runtime code paths changed.

## 4. Test results (real retargeting test, 2026-10-23)

Source: `game/assets/anim/t3/paul/t3_light.json` (Tekken punch, 22 frames,
22 bones). All tests use real repo data, no fixtures.

| test | result |
|---|---|
| Paul → Paul (identity) | 22/22 identity map, bit-exact rotation transfer (max 1e-6 rad), E=0.0 |
| **Paul punch → Gon creature rig** | **18/18 functional maps** (Root→Root 0.96, Chest→Chest 0.97, …), exact rotation transfer, root motion scaled by leg ratio 0.205, bone lengths preserved to 1e-16 m |
| Synonym rename (RightUpLeg→RightThigh, …) | 18/18 map identically — **proof alignment is semantic, not name-based** |
| 4-arm + tail rig (Chatur-style topology) | 18 core mapped; 16 extra arm joints inherit counterpart motion; tail (no counterpart) holds rest — zero-shot novel topology |
| Reduced rig (Head removed) | 17/17 clean |

Full output: `python3 tools/anim-retarget/tests/test_semantic_retarget.py`
→ `ALL SEMANTIC-RETARGET TESTS PASSED`.

**Key design findings (logged for the crew):**
- Rest-pose bone *directions* are not a valid cross-species cue (Gon's
  "shoulder" points down, Paul's up) — the structural descriptor is
  direction-free (proportions, depth, branching, subtree size).
- Soft-blending rotations across source joints corrupts transfer
  (~0.3–0.6 rad); hard top-1 semantic mapping transfers exactly.
- Hold-threshold 0.40 keeps margin above the ~0.35 noise floor of
  terminal-chain coincidences; true matches score ≥0.56.
- Mirror-side joint is the expected runner-up (differs by one semantic
  token: left vs right) — argmax is correct 18/18 regardless.

## 5. Upgrade path (not done — flagged, not faked)

1. **SATA checkpoint backend:** the official repo ships VAE/RVQ-VAE
   checkpoints (`huggingface.co/SteveZh/sata_models`) + `retarget()` in
   `src/sata/test.py`. A `--backend sata` mode could call it for the full
   learned decoder (better handling of extreme rest-pose differences).
   Blocked on: torch + torch_geometric install, checkpoint download,
   BVH↔wh-anim/1 converters. The WH-native tool stands alone until then.
2. **HF embedding backend:** `SEMRET_EMBED=hf` hook is in place for
   sentence-transformer embeddings (closer to the paper's T5 `X_t`).
3. **Roster rollout (integration standard):** run the tool across every
   non-standard rig in `game/assets/anim/` (kuma, ogre, gon, …) and
   bake banks where the name-based path can't reach. Creature/extra-limb
   WH-original characters (Chatur, Menagerie) are the priority targets.

## 6. License & provenance

- Paper/code Apache-2.0 (verified). No SATA source files vendored; this
  is an original WH-native implementation of the published methodology.
- Test data: existing repo teardown banks (`game/assets/anim/t3/paul`,
  `game/assets/anim/t3/gon`); no new game files copied.
- Owner instruction (verbatim): "Pulling everything from the list and wire
  it all up and where it'll work and where it's appropriate"
