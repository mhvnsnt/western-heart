# Wrestler/Grappler + DOA Roster Model Hunt — Results
**Date:** 2026-10-13
**Agent:** Subagent (no live browser access — discovery via web search + page fetch only)

## Summary

Searched Open3DLab, SFMLab, DeviantArt, and rigmodels.com for all target characters.
**Key finding:** SFMLab/Open3DLab downloads require a free account signup (verified — download links redirect to open3dlab.com/accounts/signup/). rigmodels.com requires login (parent has fmmgmars). DeviantArt requires login (parent has fmmgmars via browser).

**Nothing was directly downloadable** without authentication. All models below are confirmed to EXIST with exact URLs for browser-task delegation.

---

## CONFIRMED MODELS (with exact URLs)

### Street Fighter

| Character | Source | URL | Details |
|-----------|--------|-----|---------|
| **Zangief** | SFMLab | http://sfmlab.com/project/aed74fe8-8d9c-404d-b59f-ec63a0a04f19/ | **5 variants:** SFIV version (zangief.rar, 5.41MB) + 4x SFV versions (13-22MB each). XNALara/SFM ports. |
| **R. Mika** | SFMLab | (search "Rainbow Mika - Street Fighter V" on sfmlab.com) | SFV version confirmed on SFMLab Street Fighter listing page |
| **Alex** | Thingiverse | (search "Alex SFV by Irnkman" on thingiverse.com) | STL for 3D printing, free direct download — NOT a game rip |
| Hugo | — | NOT FOUND on SFMLab/rigmodels | Needs DeviantArt search |
| El Fuerte | — | NOT FOUND | Needs DeviantArt search |

### Dead or Alive

| Character | Source | URL | Details |
|-----------|--------|-----|---------|
| **Bass Armstrong** | rigmodels.com | https://rigmodels.com/model.php?view=Bass_Armstrong-3d-model__KU3Y64NFE6YJUZKN5AFGE4WKL&searchkeyword=pain&manualsearch=1 | **4 variants:** 7,800 / 7,553 / 7,794 / 8,150 polygons. DOA: Dimensions rip. T-pose, textured, FBX/OBJ available. |
| **Tina Armstrong** | SFMLab | https://sfmlab.com/project/636f7b5f-b827-40c3-81d3-1a63b058de26/ | **2 attires:** wrestling outfit + bikini. Skingroups for red/golden outfit. DOA5. |
| **Mila** | SFMLab | http://sfmlab.com/project/6c39c91d-c11f-444e-895c-eefdd9805e0b/ | Bikini + fighter suit bodygrouped. DOA5. |
| **Ayane** | rigmodels.com | (related on Bass page — search "DOA Ayane" on rigmodels) | Confirmed exists |
| **Ayane (DOA2U)** | rigmodels.com | (related on Bass page — search "DOA2U Ayane" on rigmodels) | 14,114 polygons. Confirmed exists |
| **Nyotengu** | rigmodels.com | (related on Bass page — search "DOA Nyotengu" on rigmodels) | 47,946 polygons. Confirmed exists |
| **Marie Rose** | rigmodels.com | (related on Bass page — search "DOA Marie" on rigmodels) | 29,354 polygons. Confirmed exists (listed as "DOA Marie") |
| **Naotora Ii** | rigmodels.com | (related on Bass page — search "DOA Naotora" on rigmodels) | 21,665 polygons. Bonus find. |
| Ryu Hayabusa | — | Steam Workshop has DOA:D version | https://steamcommunity.com/sharedfiles/filedetails/?id=3233007898 — needs Steam |
| Kasumi, Hayate, Jann Lee, Zack, Rig, Kokoro, Bayman, Christie, La Mariposa, Raidou, Alpha-152, Phase 4, Honoka | — | NOT directly confirmed | SFMLab likely has most (extensive DOA collection). Needs Open3DLab account + site search. |

### Fatal Fury / King of Fighters

| Character | Source | URL | Details |
|-----------|--------|-----|---------|
| Tizoc / Griffon Mask | — | NOT FOUND | Needs DeviantArt search |
| Raiden / Big Bear | — | NOT FOUND | Needs DeviantArt search |

### Virtua Fighter

| Character | Source | URL | Details |
|-----------|--------|-----|---------|
| Wolf Hawkfield, El Blaze, Shun Di, Kage-Maru, Lion, Aoi, Lei-Fei, Vanessa, Eileen, Goh | — | NOT FOUND on SFMLab/rigmodels | VF models are rare. **BEST PATH:** VF5FS game pull (already running as separate worker) — extract directly from game files. |

### Tekken

| Character | Source | URL | Details |
|-----------|--------|-----|---------|
| Craig Marduk | — | NOT FOUND on SFMLab | Needs rigmodels search (parent) or DeviantArt |

---

## RECOMMENDED ACTION PLAN (for parent)

### Immediate (browser tasks)
1. **rigmodels.com** (logged in as fmmgmars) — Download ALL of these:
   - Bass Armstrong (4 variants) — https://rigmodels.com/model.php?view=Bass_Armstrong-3d-model__KU3Y64NFE6YJUZKN5AFGE4WKL&searchkeyword=pain&manualsearch=1
   - Search "DOA" on rigmodels — grab Ayane, DOA2U Ayane, Nyotengu, Marie Rose, Naotora
   - Search "Marduk" — grab Craig Marduk if available
   - Search "Hugo" "Alex" "El Fuerte" — grab if available

2. **SFMLab** (needs free Open3DLab account — parent must sign up at open3dlab.com/accounts/signup/) — Download:
   - Zangief (all 5 variants) — http://sfmlab.com/project/aed74fe8-8d9c-404d-b59f-ec63a0a04f19/
   - R. Mika (Rainbow Mika SFV)
   - Tina Armstrong (2 attires) — https://sfmlab.com/project/636f7b5f-b827-40c3-81d3-1a63b058de26/
   - Mila — http://sfmlab.com/project/6c39c91d-c11f-444e-895c-eefdd9805e0b/
   - Site-search "Dead or Alive" — SFMLab has extensive DOA collection (Kasumi, Ayane, Hayabusa, Honoka, Marie Rose, etc.)

3. **DeviantArt** (logged in as fmmgmars) — Search and download:
   - "Hugo Street Fighter 3D model download"
   - "El Fuerte 3D model download"
   - "Tizoc Griffon Mask 3D model download"
   - "Raiden Big Bear Fatal Fury 3D model download"
   - "Craig Marduk 3D model download"

### Already in progress
- **VF5FS game pull** (separate worker) — will provide ALL Virtua Fighter characters via direct game extraction. This is the best source for Wolf, El Blaze, Shun Di, Kage-Maru, Lion, Aoi, Lei-Fei, Vanessa, Eileen, Goh.

### Lower priority
- Thingiverse Zangief/Alex STLs — 3D printing models, not game-accurate. Only useful as last resort.

---

## Files created
- This report: `~/workspace/game-reverse-engineering/models/wrestler-hunt/HUNT-RESULTS.md`
- Checkpoint: `~/workspace/agent-ops/checkpoints/wrestler-model-hunt.json` (status: running → set to done after parent review)

## Notes
- No models were directly downloaded (all sources require authentication this agent cannot provide).
- All URLs above are verified from search results and page fetches.
- The Virtua Fighter game extraction is the highest-value path — one game pull yields all 10 VF characters.
- rigmodels.com is the fastest win — parent is already logged in, Bass + 5 DOA characters confirmed there.
