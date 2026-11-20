# Free APIs for Character Creation — 2026 Industry-Standard Research

**Researched:** 2026-10-23 · **Project:** Western Heart character creation suite
**Rule used:** every entry below was checked against 2026 sources (crawled Oct 2026). Dead, paywalled-only, or license-trapped services are marked, not recommended.

---

## 1. HuggingFace — Inference API / Inference Providers / Spaces

### What it is now (2026)
HuggingFace retired the old "serverless Inference API." The current product is **Inference Providers**: one HF token routes to 200+ models hosted by partner platforms (OpenAI-compatible endpoint at `https://router.huggingface.co/v1` for text; image gen uses the model-specific `huggingface_hub.InferenceClient` calls).

- **Free tier:** **$0.10/month in Inference Providers credits** for free accounts (PRO gets $2.00). This is a small credit balance, not a request quota — it buys a handful of frontier-model calls. Terms flagged "subject to change" as of Oct 2026 (wording changed 2026-10-23, under re-verification).
- **Account-level rate limits (Free plan, per 5-min window):** 1,000 API requests, 5,000 resolver requests, 200 Pages requests.
- **Independent report (Oct 2026):** ~300 requests/hour on legacy-style free inference.
- **Limits gotcha:** models >10GB generally unsupported on serverless; availability/rate limits vary per model — good for exploration, not predictable production.
- **Spaces:** thousands of free Gradio Spaces (TRELLIS, Hunyuan3D, FLUX image models, face reconstruction demos). Free CPU/ZG3; GPU queues are the bottleneck. Spaces with Gradio API endpoints are callable over plain HTTP — effectively free micro-APIs.

### How we'd use it in the suite
- Text-to-image for textures/decals/tattoos/face-paint via `InferenceClient` against free FLUX/SDXL models.
- Face reconstruction demos and open 3D models (TRELLIS.2, Hunyuan3D) as reference/prototype generators.
- NOT a dependency for anything the suite can't live without — treat as "bonus generation capacity."

### License/terms gotchas
- Commercial use depends on each **model's** license (FLUX.1 [schnell] = Apache 2.0, commercial OK; FLUX.1 [dev] = non-commercial). The API layer doesn't override the model license.
- Images generated on free Spaces can be public by default in some Space configs.

**Recommendation: ★★★★ — Best free image-generation *programming surface* (one token, many models, HTTP Gradio APIs). Budget is tiny, so it's a prototyping lane, not a production backbone.**

---

## 2. 3D Generation APIs (free tiers)

| Service | Free offering (2026-verified) | Outputs | Commercial use | Gotcha |
|---|---|---|---|---|
| **Meshy** | 100 credits/month free | GLB, FBX, OBJ; Meshy 6 Lite | Gallery pre-mades: **CC0**. Your own Free-plan generations: **CC BY 4.0 (attribution required)** | Only 10 Meshy 6 Lite downloads/month; full-res 6/7 downloads are paid |
| **Tripo** | 200 credits/month free | GLB, FBX, OBJ, STL, PBR, auto-rig | Free tier outputs: **non-commercial license** | Raw meshes are heavy (1M+ tris) — retopology mandatory before use |
| **Tencent Hunyuan 3D** | 20 generations/day | OBJ, GLB, PBR | Check plan terms | Hosted, terms less clear |
| **Rodin (Hyper3D)** | "Free to generate," thin credits | Mesh + PBR, quad option | Paid plans for exports | License/exports push you to subscribe |
| **TRELLIS.2** | **Free, open-source (MIT), self-hosted** | GLB, OBJ, PLY, PBR to 4K | Yes | Needs own GPU (~24GB VRAM per user standing note) |
| **Hunyuan3D 2.1** | **Free, open-source, self-hosted** | Mesh + PBR | Yes (region limits on the license — read before shipping) | Same GPU story |
| **3D AI Studio** | Free tier, multi-engine | Text/Image-to-3D + community library | "Yes (check plan)" | Aggregator — terms vary by engine |

### How we'd use it in the suite
- AI generation is a **parts/accessories lane** (masks, gauntlets, jewelry, masks, armor pieces), not a character-body lane — AI bodies can't be rigged/skinned reliably and violate the skinning-pipeline standard. Generated props get Tripo-style intake: retopo → rig → archive.
- Fully free/open path = **TRELLIS.2** (primary) / **Hunyuan3D 2.1** self-hosted — matches the user's standing TRI/Open-source generator decision.

### License/terms gotchas
- **Tripo free-tier = non-commercial.** Do not ship Tripo free-tier geometry into a commercial game build.
- Meshy free = attribution required on generated models (fine, just credit).
- Self-hosted models (TRELLIS.2, Hunyuan3D) = cleanest licensing; GPU cost is the real price.

**Recommendation: ★★★★★ TRELLIS.2 (self-hosted, MIT, unlimited) — it IS the standing plan. ★★★☆☆ Meshy free tier as a zero-GPU fallback for props (respect CC BY attribution). Skip Tripo free-tier for anything shippable (non-commercial).**

---

## 3. Face APIs — detection, landmarks, scan alignment

### ★ MediaPipe (Face Landmarker) — TOP PICK
- **Price:** completely free. **License:** Apache 2.0. **No API calls, no quotas.**
- **Runs:** on-device — Android, iOS, Web (WASM/WebGL), Python. No image ever leaves the machine.
- **Output:** 478 3D facial landmarks (incl. iris 468–477), 52 blendshape scores (ARKit-compatible names), face transform matrix.
- **2026 status:** active, maintained; fresh Flutter/Android wrappers published Oct 2026.
- **Suite use:** face-scan alignment for the face builder — user snaps a photo, landmarks auto-locate eyes/lids/lips (lip contour 61–291, eyes 33–263) to drive UV placement for makeup/tattoos/face paint and morph targets for the GNM/GNL face system.
- **Gotcha:** raw landmark data, no built-in AR/makeup layers — we build those. No official React Native/Flutter SDK from Google (community wrappers exist).

### InsightFace (SCRFD / FaceAnalysis)
- **2026 status:** active, updated Oct 2026. SCRFD-10GF scores 95.16 (WIDER FACE Easy) at ~5ms on a 2080Ti.
- **License gotcha (critical):** code is MIT, but **official pretrained weights are non-commercial research only.** Commercial use requires a paid InsightFace license. SCRFD is a strong *technical* choice but **not ship-ready for a commercial game** without a license.
- **Suite use:** off-limits for shipping until/unless licensed. Use only for R&D comparisons.

### Free hosted face-detection APIs
- General landscape (Oct 2026): managed face APIs exist but are thin free tiers; and the **EU AI Act** (phased rules since Feb 2025) puts restrictions on biometric/face-recognition use, incl. transparency duties for emotion recognition. On-device (MediaPipe) sidesteps both the quota and the data-residency problem.
- **Suite use:** no hosted face API is recommended; MediaPipe covers detection + landmarks with zero cost and zero privacy surface.

**Recommendation: ★★★★★ MediaPipe Face Landmarker — free forever, private, Apache 2.0, exactly the landmark data the suite needs. Avoid InsightFace weights for commercial builds.**

---

## 4. Texture / Material Generation + PBR Libraries

### Free PBR libraries (all verified Oct 2026, all CC0 = commercial-safe, no attribution)

| Library | API? | Contents (Oct 2026 counts) | Resolutions | Notes |
|---|---|---|---|---|
| **Poly Haven** | ✅ Free, **no key required** — `api.polyhaven.com` | ~863 PBR textures, ~997 HDRIs, ~520 models | Textures to 8K (some 16K), HDRIs to 16K | Highest quality bar; scan-based; funded by Patreon/sponsors. **Anchor the suite's material system on this.** |
| **ambientCG** | ✅ Free v2 API — `ambientcg.com/api/v2` | ~2,013 materials, ~429 HDRIs | 1K–8K, JPG or PNG per download | Largest count; per-resolution/format choice; donation-funded (sustainability caveat) |
| **3DTexel** | Via free plugins (Unreal + Substance Painter) | 1,000+ handmade + stylized materials, ~50 HDRIs, AI skyboxes | 4K (some 8K) | Free account required; focused on game-ready stylized |

### Free AI texture generators (2026)
- **3dvalley.com texture generator** — free, no sign-up: text or photo → seamless tileable PBR set (albedo + normal + height + roughness + metallic) at 2048px. FLUX.2-klein color pass + texture-model map inference. Verified live Oct 2026.
- **UltraTex** — open-source (SIGGRAPH Asia 2026): textures an *untextured mesh* + reference image → albedo + metallic-roughness PBR baked to UVs. Runs in ComfyUI at ~6GB VRAM. Perfect for the suite: texture our own body/attire meshes from reference photos.
- **goenhance.ai / glbgpt.com** — "free to try" AI texture generators with royalty-free commercial output claims; trial-tier, not a free API.
- **Scenario/Substance-style AI texture** — API exists but paid (~$54.99/mo Substance). Not free.

### How we'd use it in the suite
- **Material library panel:** pull directly from Poly Haven + ambientCG APIs (keyless, CC0) — leather, denim, metal, cloth for attire creation. Per-tool wiring law: this becomes the texture/material menu's backend.
- **AI gap-filler:** 3dvalley for bespoke seamless materials (wrestling ring canvas, graffiti walls, face-paint base textures); UltraTex to auto-texture imported/sculpted meshes from reference images.
- **HDRIs:** Poly Haven's ~997 HDRI library for the suite's lighting/environment previews.

### License/terms gotchas
- Poly Haven + ambientCG = CC0: use in a commercial game with zero worry. This is the cleanest license story in the entire report.
- 3DTexel handmade library = CC0; free account required (one-time friction).
- AI-generated textures: output rights depend on the tool; 3dvalley's terms weren't verified for commercial reuse — treat as prototyping until checked.

**Recommendation: ★★★★★ Poly Haven API + ★★★★★ ambientCG API (CC0, keyless, commercial-safe — wire into the suite first). ★★★★ UltraTex (open-source, textures our own meshes). ★★★ 3dvalley (free, no sign-up) for bespoke seamless PBR.**

---

## 5. Free 3D Asset Libraries (parts / clothing / accessories)

### ★ Kenney.nl — TOP PICK for props/UI
- **License:** CC0 (public domain), commercial OK, no attribution.
- **Contents:** 200+ packs, 60,000+ assets — GLB/GLTF, OBJ, FBX for 3D; PNG, WAV; UI packs, crosshairs, HUD elements.
- **Access:** direct ZIP download per pack, no account. Also on itch.io with free samples + Blender source files.
- **Suite use:** arena dressing, UI/HUD parts, placeholder props, menu iconography bases. CC0 means everything can ship in the game.
- **Limitation:** low-poly/stylized aesthetic — great for prototyping and props, not realistic character parts.

### ★ Quaternius — TOP PICK for characters/accessories
- **License:** CC0. **Access:** direct ZIP per pack, no account.
- **Contents:** 80+ themed packs (GLTF/GLB, FBX) incl. **rigged Universal Base Characters + CC0 Modular Character Outfit kit** — outfits that fit the base characters.
- **Suite use:** clothing/accessory *patterns* and base meshes; the Modular Outfit kit is a reference for our own attire-ladder system. Stylized, so it's a pattern source, not a photoreal donor.

### Sketchfab — searchable catalog via Download API
- **API:** `GET https://api.sketchfab.com/v3/models/{UID}/download` (OAuth bearer token; temporary glTF + USDZ URLs, 300s expiry).
- **Scope:** ~1M+ free models; Download API covers CC-licensed ones. Per-model licenses: **CC0 / CC BY / CC BY-SA / CC BY-NC / Standard** — must be filtered and respected per model.
- **Free Basic account:** unlimited public downloadable uploads; 10 view-only uploads/month (100MB each).
- **Suite use:** the "long tail" parts search — hair cards, boots, gloves, accessories — filtered to CC0/CC BY, pulled programmatically. Attribution tracking built into the importer (record creator + license per asset).
- **Gotchas:** license heterogeneity is the whole problem — an automated pull must log license per asset. Viewer API needs Premium for embeds (irrelevant to us; we use the Download API).

### Also in the landscape
- **OpenGameArt** — community assets, mixed licenses (verify per asset).
- **cgbookcase / 3DTextures.me / ShareTextures / FreePBR** — CC0 texture supplements (FreePBR: custom license — commercial use is paid, skip).
- **rigmodels.com** — free 3D downloads (hair cards listed) but licenses unclear — **do not auto-pull; manual review only.**

**Recommendation: ★★★★★ Kenney + Quaternius (CC0, zero friction — wire into the suite's parts browser). ★★★★ Sketchfab Download API as the searchable long-tail parts catalog with per-asset license logging (CC0/CC BY only).**

---

## 6. Fonts / Icons / Logos (decal & logo tools)

### Google Fonts Developer API
- **API:** key required (free key), returns full font family metadata + file URLs (variants, subsets, variable-font axes, color capabilities).
- **License:** fonts themselves are SIL OFL / Apache — free for commercial game use.
- **Suite use:** the logo/decal text tool gets live font browsing (filters: display, blackletter, brush, kanji-capable subsets) with one-click download of TTF/OTF.

### Iconify — unified icon API — TOP PICK for icons
- **API:** `https://api.iconify.design/{prefix}.json?icons=name1,name2` — free, no key, returns clean SVGs.
- **Contents:** 150+ icon sets, **200,000+ icons** — incl. **game-icons** set (~4,000 game-themed glyphs: swords, skulls, tribal marks).
- **Licenses:** per-set (MIT / Apache 2.0 / OFL / CC BY 4.0). **game-icons is CC BY 4.0 — attribution required.**
- **Suite use:** decal/logo *glyph* library — swords, tribal patterns, emblems as SVG, recolorable and scalable, stampable onto body UVs as tattoos/decals. Filter to MIT/Apache/OFL sets for zero-attribution; log attribution for CC BY sets.

### game-icons.net (direct)
- Same ~4,000-icon library, CC BY 4.0, SVG/PNG. The Iconify `game-icons` prefix is the same data via API.
- Attribution requirement is the only friction — manageable with an in-suite credits line.

### Simple Icons / svgl / thesvg.org (brand icons)
- Simple Icons: 3,000+ brand logos, **CC0**, monochrome. svgl: 657 curated brand icons, MIT. thesvg.org: 5,600+ brand icons, free/no attribution.
- **Suite use:** NOT for tattoos — brand logos in a shipped game are trademark exposure. Only relevant for menu/UI mockups, never on fighters.

### SVGRepo
- Large free SVG library, generally commercial-use-allowed per their terms — but license varies per vector. Use as a manual-search supplement, verify per asset.

### Logo generation (AI)
- Free image APIs (Gemini 2.5 Flash Image — 500/day; Pollinations key + Pollen) can generate emblem concepts, which get vectorized/traced in-suite.

**Recommendation: ★★★★★ Iconify API (200k icons, free, keyless, SVG — game-icons set is the decal/tattoo glyph goldmine; honor CC BY attribution). ★★★★★ Google Fonts API for the logo text tool. Skip brand-icon sets for in-game use.**

---

## 7. Everything else — tattoo, makeup/face paint, hair cards, anatomy

### Tattoo generation
- **Finding:** no verified CC0/open tattoo-flash API exists. Clipart-style sites (clipart-library, etc.) are "personal use only" — **not commercial-safe, do not pull for the game.**
- **The actual pipeline:** generate tattoo/face-paint artwork with the free image APIs (see §8), place with MediaPipe landmark UV mapping. Tattoo = AI art + SVG glyphs (Iconify/game-icons tribal marks) composited onto body UVs.
- **Cultural caution (canon-relevant):** tā moko / tribal motifs are identity marks in real cultures — the suite should tag traditional-pattern sources and prefer original/generated designs for fighters.

### Makeup / face paint textures
- Same pipeline as tattoos: free image generation + MediaPipe landmark regions (lips 61–291, eyes 33–263, cheeks anchors) as placement guides. The 52 blendshapes give expression-aware placement for AR-style preview.

### Hair cards
- **Finding:** no free hair-card API. Sources: scattered CC0 hair models on **Sketchfab** (filter via Download API), free CGTrader listings (license varies — manual review), MetaHuman-style groom packs are mostly paid. The **Houdini Hair-Card HDA tutorial** (works with free Houdini Apprentice) is the open *method* for generating cards from grooms.
- **Recommendation:** treat hair as a manual/crew lane; use Sketchfab CC0 pulls as donor geometry. Not API-automatable today.

### Anatomy reference
- **BodyParts3D** (Database Center for Life Science, Japan): whole-body adult-male anatomical 3D data, downloadable in VTK/STL. Long-standing open database; used in 2026 open-source anatomy explorers. License is open-access — verify the exact terms on their info page before redistributing meshes, but reference viewing is safe.
- **LearnAnatomy3D** (Oct 2026, three.js): free interactive atlas, ~2,900 structures, built from open datasets (Z-Anatomy, BodyParts3D, Human Reference Atlas) — good in-browser anatomy reference for the anatomy team.
- **Suite use:** anatomy reference panel for the BODY system — muscle/bone placement guides alongside MB-Lab/Build-A-Bod.

**Recommendation: ★★★★ AI-generate tattoos/paint (image APIs + MediaPipe placement); no CC0 tattoo library is safe to use. ★★★ BodyParts3D/LearnAnatomy3D as anatomy reference. Hair cards: manual lane, Sketchfab CC0 donors.**

---

## 8. Free image-generation APIs (cross-cutting: textures, decals, tattoos, paint, logos)

| API | Free tier (2026) | Notes |
|---|---|---|
| **Google Gemini API** (Gemini 2.5 Flash Image) | **500 images/day at 1024×1024, no card** | Most generous verified free image tier. Review commercial/privacy terms before shipping. |
| **Pollinations** (`gen.pollinations.ai`) | Key now required; new accounts earn "Pollen" (free tier ~1.5 Pollen/week). Legacy keyless endpoint is unreliable (402s). | Free FLUX; prompts can be public. Good for prototyping, not production. |
| **Cloudflare Workers AI** | 10,000 Neurons/day, includes FLUX | Edge-hosted; neurons pricing needs estimation. |
| **HuggingFace Spaces / Inference** | $0.10/mo credits + free Gradio API endpoints | Tiny budget; best as a multi-model fallback. |

**Recommendation: ★★★★★ Gemini 2.5 Flash Image (500/day free) as the suite's AI art backend for tattoos/decals/textures/paint. ★★★★ Pollinations (keyed) as fallback. Route both behind one interface with local caching.**

---

## Ranked recommendations (per category)

| Category | Winner | Runner-up |
|---|---|---|
| HF / multi-model inference | **HuggingFace Inference Providers + Spaces** (prototyping lane) | Cloudflare Workers AI |
| 3D generation | **TRELLIS.2 self-hosted (MIT)** | Meshy free tier (CC BY, attribute) |
| Face detection/landmarks | **MediaPipe Face Landmarker** (Apache 2.0, on-device) | — (InsightFace weights are non-commercial) |
| PBR materials | **Poly Haven API** (CC0, keyless) | **ambientCG API** (CC0, keyless) |
| AI texture generation | **UltraTex** (open-source, textures our meshes) | **3dvalley** (free, no sign-up, 2048px PBR) |
| 3D parts/clothing library | **Kenney** + **Quaternius** (CC0, no account) | **Sketchfab Download API** (license-filtered) |
| Fonts | **Google Fonts Developer API** (OFL/Apache fonts) | — |
| Icons/decals glyphs | **Iconify API** incl. **game-icons** set (honor CC BY) | SVGRepo (verify per asset) |
| AI image backend | **Gemini 2.5 Flash Image** (500/day) | Pollinations (keyed) |
| Tattoo/makeup/paint | **AI-generate + MediaPipe placement** (no safe CC0 library found) | — |
| Hair cards | Manual lane, Sketchfab CC0 donors | — |
| Anatomy reference | **BodyParts3D** + **LearnAnatomy3D** | — |

## Universal gotchas
1. **"Free" ≠ commercial-safe.** Tripo free (non-commercial), InsightFace weights (research-only), clipart tattoo sites (personal-only) will all bite a shipped game. CC0/OFL/Apache/MIT are the safe licenses; CC BY is safe with attribution logging.
2. **Free tiers change constantly** — Meshy/Tripo credit amounts, HF's $0.10, Pollinations' keyless endpoint all shifted in 2026. Pin the check date; re-verify before building hard dependencies.
3. **Build the suite on the keyless CC0 backbone** (Poly Haven, ambientCG, Kenney, Quaternius, Iconify, Google Fonts, MediaPipe) — everything there is free *and* license-clean. Put AI generation (Gemini, HF, UltraTex) behind a swappable interface so a tier change never breaks the suite.
