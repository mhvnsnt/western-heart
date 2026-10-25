# Morphing Freedom Research — Which System to Pull
**Date:** 2026-10-23  
**Owner question (verbatim):** "find out which of the WWE games had the most the most face and body morphing freedom... because they have a lot of good ones now in the 2k26 but it's more like choosing templates than it is with sliders like you can't really change specific areas with sliders like how you used to be able to on some games"

**Owner decision (verbatim):** "we still want all the parts though from 2k26... that we can get from the creation suite or from 2k25 but then like I said whatever else that had like more freedom pull that in too and wire that up"

## TL;DR

**Best morphing freedom in a WWE game: SmackDown vs. Raw 2006–2007 era (peak of the slider system that started in Here Comes the Pain 2003).**

- Per-area face sliders (head, forehead, eyebrows, eyes, nose, cheeks, mouth, jaw, ears, skin aging) — multi-value per region
- Per-part body sliders (neck, chest, bust, shoulder, abdomen, waist, arms, hands, legs, feet, height)
- Community still shares full slider formulas with exact numeric values — the system is completely documented by players

**Combined plan: 2K26/2K25 PARTS LIBRARY + SvR-era MORPHING SYSTEM, wired together.**

- 2K26/2K25 = the parts (thousands of meshes, textures, clothing, accessories)
- SvR 2006–07 = the morphing engine (per-area sliders driving parametric deformation)
- Open source = MB-Lab parametric engine + MakeHuman fuzzy-logic as the implementation backbone

---

## 1. WWE Morphing Freedom Rankings (researched 2026-10-23)

### Tier 1 — Maximum freedom (per-area sliders)
| Game | Year | System | Notes |
|------|------|--------|-------|
| **SmackDown vs. Raw 2007** | 2006 | Face morphing + full body scaling | Most granular documented: head(-48,44,0,12), eyebrows, eyes(7 values), nose(8 values), cheeks, mouth(7), jaw(6), ears, age + body type + advanced per-part (head/neck/chest/bust/shoulder/abdomen/waist/arms/hands/legs/feet/height) |
| **SmackDown vs. Raw 2006** | 2005 | Same slider engine | Full morphing formulas shared by community |
| **SmackDown! Here Comes the Pain** | 2003 | Face morphing + body morphing added | First game with body morphing; reviewers: "morph almost every part of your wrestler's body in 3D" |

### Tier 2 — Good but simplified
| Game | Year | System | Notes |
|------|------|--------|-------|
| WWE 2K15–2K22 | 2014–2022 | Face templates + limited sliders | Template-based faces; height/weight sliders return in 2K23 |
| WWE 2K23+ | 2023+ | Remade face templates, height/weight sliders | "Face templates and skin textures entirely remade for much better looking characters. Height and weight sliders have also made their return." — still template-first |

### Tier 3 — Current (template-heavy)
| Game | Year | System | Notes |
|------|------|--------|-------|
| WWE 2K25 / 2K26 | 2025–2026 | Templates + limited sliders | Per owner: "more like choosing templates than it is with sliders like you can't really change specific areas with sliders" |

**Conclusion:** Pull the morphing system design from **SmackDown vs. Raw 2007** (or 2006). It's the peak of per-area slider freedom, fully documented by the community, and the slider→mesh-deformation mapping is recoverable.

## 2. Best Non-WWE Morphing Systems (survey)

| Game | Morphing approach | Why it matters |
|------|-------------------|----------------|
| **Black Desert Online** | Widely called "best character creation of all time". Sliders for nearly every body part (nose, chin, thighs, calves, waist...). **Direct manipulation**: touch a point on face/body and drag, or use sliders. Eyelash length slider. Hair: cut/extend per section, curl degree, asymmetric lengths, per-section colors. | The gold standard for per-area freedom + direct manipulation. Study its UI. |
| **APB Reloaded** | Deep body sliders + **create-your-own clothing graphics** (gallery + custom uploads) | Clothing customization model to copy |
| **EVE Online** | Hover-and-drag facial sculpting | Direct manipulation precedent |
| **Soulcalibur IV** | Muscle tone slider (still rare) | Muscle tone is a slider our system should have |
| **Dragon's Dogma** | Deep body morphing | Body proportion freedom |

## 3. Open Source Morphing Systems

| System | License | What it gives us |
|--------|---------|------------------|
| **MB-Lab** (Blender addon) | Open source | **Hundreds of morphing parameters**, measures editor (anthropometric: direct/indirect/file), coherent fuzzy-logic interpolation (knows bodybuilder vs overweight patterns), expression units, skin editor auto-generating displacement from muscle/tone/age. **Already in our unification plan.** |
| **MakeHuman** | Open source | Parametric sliders (gender/age/muscle/weight/height/proportion/ethnicity), fuzzy logic amalgamation, up to 163-bone rigs, template+areas-of-influence morphing |

## 4. What Gets Pulled and Wired

### From 2K26 / 2K25 (when available on archives)
- **ALL parts**: meshes, textures, clothing, accessories, hair, face paint, makeup, tattoos
- Selective extraction: creation-suite files only (~2-5GB, not 60GB full game)
- See `teardown/wwe-2k/WWE2K-SELECTIVE-EXTRACTION.md`

### From SmackDown vs. Raw 2006–2007
- **The morphing engine design**: per-area face sliders + per-part body sliders
- Slider→deformation mapping: how each slider value transforms the mesh
- The full slider taxonomy (face regions × values, body parts × values)
- Community formula data (exact numeric slider values = free test data)

### From Black Desert Online (study, don't copy assets)
- Direct-manipulation UI: touch face/body point → drag
- Per-section hair editing (cut/extend/curl/color per section)
- Slider organization and density

### From MB-Lab + MakeHuman (implementation backbone)
- Parametric morphing engine with fuzzy-logic coherence
- Measures editor (anthropometric direct/indirect)
- Expression units

## 5. Combined Architecture

```
┌─────────────────────────────────────────────────┐
│  WH MORPHING SYSTEM (creation suite)            │
│                                                 │
│  UI LAYER (BDO-inspired)                        │
│  - Direct manipulation (touch + drag)           │
│  - SvR-style per-area sliders (fallback)       │
│                                                 │
│  MORPHING ENGINE (MB-Lab + MakeHuman)           │
│  - Hundreds of parametric targets               │
│  - Fuzzy-logic coherence (bodybuilder vs fat)   │
│  - Face regions: head/forehead/brows/eyes/      │
│    nose/cheeks/mouth/jaw/ears/aging             │
│  - Body parts: neck/chest/bust/shoulder/        │
│    abdomen/waist/arms/hands/legs/feet/height    │
│                                                 │
│  PARTS LIBRARY (2K26/2K25 + teardowns)          │
│  - Thousands of meshes/textures/clothing        │
│  - Parts auto-fit to morphed bodies             │
└─────────────────────────────────────────────────┘
```

## 6. Implementation Order

1. **Document the SvR 2007 slider taxonomy** from community formula guides (free, no pull needed)
2. **Wire MB-Lab morphing engine** into creation suite (already planned in unification)
3. **Build SvR-style slider UI** on top of MB-Lab parameters
4. **Add BDO-style direct manipulation** as an alternative input mode
5. **Fit 2K26/2K25 parts** to morphed bodies (auto-fit system)
6. Pull 2K25/2K26 parts when they hit archives

## Sources
- SvR 2007 formula guides (supercheats.com, cheatcodes.com) — full numeric slider values
- HCTP reviews (GameFAQs, WhatCulture, Slam Wrestling) — morphing system documentation
- BDO character creator coverage (WhatCulture, PC Gamer, MMOByte, LineGames)
- MB-Lab docs (mb-lab-docs.readthedocs.io), MB-Lab wiki
- MakeHuman research (ResearchGate, freesoftwaremagazine.com)
