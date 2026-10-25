# Anatomy Datasets Integration — 2026-10-23

**Owner directive:** Use open-source anatomy datasets (from the DeepMind "Gemini 4 Argon" post) to build inner skeletons and X-ray for our models. Some fighters have non-human skeletons — need variant parts. Get organs from open source + Purdue project. Enhance the X-ray system with real anatomical data. Research MK's X-ray technique.

## 1. Datasets identified

### The three datasets from the DeepMind post

The Google DeepMind post (Oct 21, 2026) describes "Gemini 4 Argon combined three open-source datasets to build an interactive 3D visualization of human anatomy." Based on the ecosystem of open anatomy projects in 2026, the three datasets are:

| # | Dataset | Source | License | Game-use |
|---|---------|--------|---------|----------|
| 1 | **BodyParts3D 4.0** | Database Center for Life Science, Japan | **CONFLICTING** — see §2 | **PENDING** |
| 2 | **Z-Anatomy** | Gauthier Kervyn (derived from BodyParts3D) | **CC BY-SA 4.0** (share-alike) | **NO-GO** — contaminates game assets |
| 3 | **Human Reference Atlas (HRA)** | NIH HuBMAP Consortium | CC BY 4.0 (verify per-release) | Likely OK |

### Why these three

- **BodyParts3D**: The foundational 3D anatomy database (1,000+ structures, OBJ format). Every open anatomy viewer starts here.
- **Z-Anatomy**: Blender-based atlas built on BodyParts3D, adds hierarchical labeling, 8 body systems, cardiovascular detail. The "usable" version of BodyParts3D.
- **HRA**: NIH's Human Reference Atlas — newer, includes female anatomy (BodyParts3D is male-only), cell-type annotations.

All three are used together in projects like LearnAnatomy3D, human-atlas, and Somakine.

## 2. License analysis — CRITICAL

**CORRECTION (2026-10-23, post-merge):** License verifier confirmed from primary sources:
- BodyParts3D **4.0 (current archive)**: CC BY 4.0 — GO. Older releases (≤4.3): CC BY-SA 2.1 JP — NO-GO. Use only current archive downloads.
- **Z-Anatomy: CC BY-SA 4.0 — NO-GO.** Share-alike contaminates game assets. Do not use.
- HRA 3D organs: CC BY 4.0 — GO.

### BodyParts3D: CONFLICTING license claims

**Two different licenses are published for BodyParts3D:**

| Source | License claimed | Date |
|--------|-----------------|------|
| LSDB Archive (dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html) | **CC BY 4.0 International** | Updated 2025/02/27 |
| BodyParts3D README (dbarchive.biosciencedbc.jp/data/bodyparts3d/20110915/README_e.html) | **CC BY-SA 2.1 Japan** | Older |
| lifesciencedb.jp/bp3d | CC BY-SA 2.1 Japan | — |

**Interpretation:** The license appears to have CHANGED from CC BY-SA 2.1 JP to CC BY 4.0 at some point. The newer LSDB Archive page (2025) claims CC BY 4.0.

**Why this matters:**
- **CC BY 4.0** (attribution only): ✅ Safe for game use with credit line
- **CC BY-SA 2.1 JP** (share-alike): ❌ **CONTAMINATES** — any derivative work (including game models using the data) must be released under the same license

### Decision: DO NOT BUNDLE BodyParts3D meshes until license is definitively resolved

**Safe path forward:**
1. The existing SDF primitive system (`tools/anatomy/generate_layers.py`) is **100% our own procedural generation** — no license issues. This remains the default.
2. Schema v3 (see §4) supports optional mesh references with per-mesh license attribution, but **no meshes are bundled** until the license is confirmed.
3. If BodyParts3D is confirmed CC BY 4.0: we can use meshes with attribution "BodyParts3D, © The Database Center for Life Science licensed under CC BY 4.0 International"
4. If BodyParts3D remains CC BY-SA: we use it for **reference only** (looking at anatomy to inform our procedural generation), never bundling the meshes.

### Z-Anatomy

Derived from BodyParts3D — inherits whatever license BodyParts3D has. Same PENDING status.

### HRA (Human Reference Atlas)

NIH HuBMAP data is generally CC BY 4.0, but verify per-release. More permissive than BodyParts3D. **Candidate for first mesh integration** if confirmed.

## 3. Skeleton variant system

### Design: base + modular additions

The human skeleton is the base. Non-human fighters get modular bone additions:

```
base_human_skeleton (53 joints, Tekken standard)
    ├── variant: extra_arms (Chatur/Rahkasa)
    │   ├── shoulder.L2, upperarm.L2, forearm.L2, hand.L2
    │   └── shoulder.R2, upperarm.R2, forearm.R2, hand.R2
    ├── variant: kappa_shell (Dorowani)
    │   ├── shell (carapace — modified ribcage)
    │   ├── tail.1, tail.2, tail.3
    │   └── skull_kappa (modified skull shape)
    └── variant: [others per auditor findings]
```

### Anatomy layer generation for variants

`tools/anatomy/generate_layers.py` already positions primitives from rig joints (no hand-tooled coordinates). For variant skeletons:
- Extra arms → generate arm bone/muscle primitives for the additional joints
- Shell → generate modified ribcage (wider, flatter ellipsoid)
- Tail → generate tail bone capsules
- The organ layer positions from chest/spine/hips — works for any torso shape

### Non-human fighters (preliminary — auditor confirming)

| Fighter | Variant | Notes |
|---------|---------|-------|
| Chatur (Rahkasa) | extra_arms | Four arms — needs 2 additional full arm chains |
| Dorowani | kappa_shell | Kappa/crocodile demon — shell, tail, modified skull |
| Kuma / Panda | ursine | Bear proportions — verify if rig differs |
| Zen | spirit | Spirit/tentacle form — may need custom |
| DXMMII | patchwork | Patchwork body — verify joint structure |
| Cyborg-X | cybernetic | May have mechanical additions |

## 4. Schema v3: mesh reference support

### `wh.anatomy-layers/3` (proposed)

Additive to v2. New optional fields:

```json
{
  "$schema": "wh.anatomy-layers/3",
  "layers": {
    "bone": {
      "primitives": [...],
      "meshes": [
        {
          "id": "skull",
          "url": "roster/pantera/anatomy/meshes/skull.glb",
          "dataset": "bodyparts3d",
          "dataset_version": "4.0",
          "license": "CC-BY-4.0",
          "attribution": "BodyParts3D, © The Database Center for Life Science licensed under CC BY 4.0 International",
          "joint": "head"
        }
      ]
    }
  }
}
```

**Key rules:**
- `meshes` is OPTIONAL — primitives remain the default
- Every mesh MUST have `dataset`, `license`, and `attribution`
- xray.js loads meshes when present, falls back to proxies when absent
- **No meshes are bundled until their license is verified**

### xray.js enhancement

Current: `_proxyMesh()` builds analytic meshes from SDF primitives.
Enhanced: `_anatomyMesh()` checks for mesh data first:

```javascript
// Pseudocode for the enhancement
_anatomyMesh(prim, mat, seg) {
  if (prim.mesh && prim.mesh.url) {
    // Load real mesh from dataset (cached)
    return this._loadDatasetMesh(prim.mesh, mat);
  }
  // Fallback: analytic proxy (existing behavior)
  return this._proxyMesh(prim, mat, seg);
}
```

The enhancement is **additive** — existing proxy behavior is unchanged when no mesh data exists.

## 5. MK X-ray technique → WH adaptation

See `docs/research/MK-XRAY-TECHNIQUE-2026-10-23.md` for full research.

**Key takeaways for our X-ray system:**
1. **MK cheats the interior** — pre-modeled anatomical parts, hidden/revealed. No real simulation. We already do this with proxies; dataset meshes make the cheat better.
2. **Desaturation + slow-mo** as the "sequence mode" flag — cheap, legible, no animation budget.
3. **Krushing Blows** (micro-X-rays on specific moves) are the real prize — single-beat camera zoom + damage flash without full cinematic. Recommend for WH's heavy counter-hits.
4. **2-state bones** (intact → broken) — our bone flash can evolve into crack/break states.
5. **Camera stays on fight plane** for Tekken-style (don't fully detach like MK fatalities).

## 6. Implementation plan

### Phase 1: Schema + docs (this PR)
- [x] Dataset identification
- [x] License analysis (PENDING resolution — safe path documented)
- [x] Skeleton variant system design
- [x] Schema v3 spec
- [x] MK technique research

### Phase 2: xray.js enhancement (next PR)
- Add `_anatomyMesh()` with mesh loading + proxy fallback
- Add dataset attribution to X-ray credits
- No behavior change when no mesh data present

### Phase 3: Mesh integration (after license confirmed)
- Download and convert dataset meshes
- Generate per-fighter mesh references
- Wire into anatomy-layers.json v3

### Phase 4: Skeleton variants (after auditor report)
- Implement variant bone additions in generate_layers.py
- Generate layers for Chatur, Dorowani, other non-humans
- Verify X-ray works with variant skeletons

## 7. Attribution

If/when dataset meshes are used, attribution will appear in:
- `docs/ATTRIBUTION.md` (project-level)
- Per-mesh `attribution` field in anatomy-layers.json
- In-game credits screen

**Current status:** No third-party meshes bundled. All anatomy is procedurally generated from our own code.
