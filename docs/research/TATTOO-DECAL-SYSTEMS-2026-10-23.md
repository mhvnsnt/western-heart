# Tattoo / Decal / Face-Paint Systems — Research for the Western Heart Creation Suite

**Date:** 2026-10-23 · **Status:** Research only — no game code written (build phase is a separate lane)
**Owner instruction:** "let's continue to research and pull stuff in related to all those areas"
**Scope:** tattoo/decal systems, placement systems, custom-design generation, face paint + makeup.
Related work: `docs/research/CREATION-TOOLCHAIN-MBLAB-GNM-MPFB2.md` (body/face systems),
`docs/research/WWE-CAW-EXTRACTION-STATUS.md`, `docs/research/creation-suite-sharing-2026-10-23.md`,
`docs/research/smutbase-batch2-tool-evaluations-2026-10-22.md` (Fluid Painter NSFW — texture painting,
filed for the skin system).

---

## 1. The three ways tattoos get onto a game character

Every system found reduces to one of three architectures. WH's creation suite will need
a mix of (A) and (B); (C) is a scene-level fallback, not a character-creation tool.

| # | Method | How it works | Pros | Cons |
|---|--------|--------------|------|------|
| A | **UV-baked overlay** | Tattoo PNG (with alpha) is composited onto the skin's albedo texture at a UV coordinate; the tattoo becomes part of the texture (or a second stacked layer texture). | Persists through animation perfectly; cheap at runtime (same draw call); scales to dozens of tattoos; mirrors/rotates/slides trivially in UV space; works with skin-tone changes if drawn multiplicatively. | Needs predictable UV layouts; seams can cut tattoos crossing UV islands (fix: dilation/padding around islands when compositing). |
| B | **Projected geometry decal** | A mesh "patch" is carved from the body surface and the tattoo texture is projected onto it (three.js `DecalGeometry`; Godot `Decal` node; Unity decal projectors). | Works on any mesh without UV knowledge; drag/position in 3D; zero texture work. | Must be re-baked when the mesh deforms — **bad for animated fighters**; extra draw calls; polygon-offset/z-fighting tuning needed; each decal is a separate draw call. |
| C | **Engine clustered decals** (Godot 4 `Decal`, URP/HDRP decals) | Runtime projection volumes for transient effects. | Free in engine. | Explicitly not for character customization (Godot decals: projected only, "cannot be baked to UV"; no transparency-blend into materials; 8-per-mesh limit on Mobile). |

**Recommendation for WH:** use **A (UV-baked overlay) as the production pipeline**, with B
(three.js `DecalGeometry`, MIT — already in our stack) as the *interactive preview* while the
user positions the tattoo in the creation suite, then bake the result into the skin texture
on confirm. This is the architecture worth wiring in.

---

## 2. Open-source systems worth wiring in

### 2a. three.js `DecalGeometry` — interactive placement engine (MIT)
- Ships with three.js examples (`examples/jsm/geometries/DecalGeometry.js`); WH already runs three.js.
- Workflow found in the wild: user clicks a point on the body → `DecalGeometry(mesh, position, orientation, size)` carves a surface patch → tattoo PNG applied with polygon-offset to beat z-fighting. Moving the tattoo re-generates the geometry (must `dispose()` the old one to avoid leaks).
- Key gotcha (three.js forums): DecalGeometry takes a **world-space position as the projection point** — rotating the node alone spins the sticker, it doesn't move the placement. The suite's drag-to-place UI must track position + rotation + scale explicitly.
- Limitation for fighters: it must be rebuilt whenever the geometry changes, so use it for **preview/placement only** in the suite, then bake to texture (method A) for the final fighter. Marco Fugaro's `three-projected-material` plugin (alternative "projector" approach) lets the decal origin be moved freely as a child of the geometry.
- Sources: https://discourse.threejs.org/t/how-to-draw-stuff-on-stuff/48934 · https://discourse.threejs.org/t/change-position-decal-geometry-with-dragcontrol/61420 · http://drei.docs.pmnd.rs/abstractions/decal

### 2b. GTA V / FiveM tattoo architecture — the best shipping reference for zone-based tattoos
- The entire GTA V tattoo system is open: tattoos are **decals applied to a ped through a decoration collection**. Each tattoo is a texture + overlay collection + catalogue entries; placement is stored as **uvPos + scale + rotation** per zone.
- Zones: torso, either arm, either leg, head — the tattoo belongs to one zone, and the zone decides which part of the skin the decal lands on. This is exactly the "per-body-region placement" model our suite needs.
- The Orb's "FiveM Tattoo Creator" (web tool, https://theorb.tech/studio/fivem-tattoo-creator): drop any PNG (transparency = what makes it a tattoo, not a rectangle), crop in-page, **choose zone, drag to position, scale, rotate**, then export a resource pack (texture + overlay collection + catalogue JSON the shop UI reads). This is the closest thing to a complete, shipping, open tattoo-shop pipeline — worth studying feature-for-feature for WH's UI.
- Note on license: GTA tooling is built around a proprietary game; pull the *architecture* (zone → uvPos/scale/rotation catalogue) and the *UI flow*, not Rockstar assets.

### 2c. Diffeomorphic / DAZ "Decals" workflow — Blender-side tattoo authoring (open, free)
- Diffeomorphic (the DAZ-to-Blender bridge, open source) documents two workflows (http://diffeomorphic.blogspot.com/2020/12/decals.html):
  1. **Snap-to-face decal empty** parented to the body (vertex parent so it survives posing) — lightweight, single-material only.
  2. **Dedicated tattoo mesh**: duplicate shoulder/body vertices → separate mesh named "Tattoo" → inherits armature modifier + vertex groups (prune empties) → shrinkwrap with small offset so it rides on the skin → clear seams and re-unwrap so the decal area has no UV seam → tattoo material with alpha.
- Why it matters for WH: this is the proven authoring pipeline for the tattoo *content library* — tattoos authored on the Lily donor rig / Scarlett-Madeline anatomy refs can be transferred to any fighter via the same vertex-group inheritance trick. Replaces ad-hoc Photoshop work with a repeatable pipeline step.
- Generic Blender flow also documented: tattoo PNG → Image Texture node → Mix Shader / Mix RGB over Principled BSDF skin → UV placement in the UV Editor (https://umatechnology.org/how-to-add-tattoos-to-avatars-in-blender/). Fine for one-offs; the Diffeomorphic mesh workflow is the one to standardize.

### 2d. ComfyUI Body Decal — pose-aware AI placement/compositing (open source)
- `verias/comfyui-body-decal` (GitHub): pose-aware decal placement, masking, warping, and compositing for ComfyUI. Applies tattoos, scars, body paint, cybernetic markings, glowing circuitry, logos, makeup onto generated or existing images with body-aware placement regions, perspective warping, displacement and depth maps.
- Why it matters: WH's pipeline already uses AI image tooling — this node plugs tattoo/makeup *generation + placement* into the same ComfyUI flow that produces reference art, so tattoo designs can be prototyped on renders before being committed to the character. (Verify license on pull — repo README carries license/credits sections.)

### 2e. Design-source tooling (open)
- **GIMP / Inkscape / Blender**: GIMP (GPL) and Inkscape (GPL) are the free design stack for tattoo art — transparent-background PNG export is the tattoo format (one guide walks the exact fuzzy-select → alpha-channel → PNG pipeline). Inkscape gives infinitely scalable vector tattoo designs (SVG → PNG at any resolution). Tattoo-specific *brushes* are almost all commercial (Procreate bundles), but the *formats* (ABR/PNG/SVG brushes, transparent PNG flash, SVG vectors) are the interchange standard our suite should accept.
- **Tattoo Pack (tattoopack.app)**: free tier converts any uploaded PNG/JPEG/WebP into a tattoo stencil via Google Gemini — relevant as a reference for the "user image → tattoo" conversion step (line-art extraction). **Tattoo stencil generator** reference: https://tattoopack.app/
- **pngmaker.io** hosts free AI-generated tattoo-art transparent PNGs — a free stopgap flash library (verify each asset's license before shipping).

---

## 3. Teardown sources: how the big games do it

### WWE 2K series (CAW) — the layering gold standard
Our lane (teardown extraction is already in-flight: `WWE-CAW-EXTRACTION-STATUS.md`, `~/workspace/w65-wwe-caw`):
- **Image Uploader**: players upload custom logos/images (up to 2,000 image slots in WWE 2K26, doubled from 1,000) and use them as tattoos, designs, even custom face textures. This is the exact "user-uploaded image → tattoo" pipeline WH needs.
- **Layer system (WWE 2K26, Ringside Report)**: 60 layers for attire + **40 layers for head and body** (previously 60 total shared). Layers stack with per-layer position, scale, rotation, opacity, color tinting — the suite's tattoo UI should copy this layer-stack mental model.
- **Paint Tool**: last-gen consoles' paint tool (replaced on PS4/Xbox One by direct logo import) offered transparency and shine controls per design; face/body paint designs live in the same layer system as tattoos. Community wishlist (still relevant): designs should move freely between sections (tattoos ↔ tights designs ↔ mask designs), every design should carry transparency/shine options.
- **40+ body templates** as creation starting points (2K26) — relevant to the template-first flow the user already ordered.
- Sources: https://www.thesmackdownhotel.com/news/wwe2k26/wwe-2k26-ringside-report-universe-creations · https://www.operationsports.com/wwe-2k26-creation-suite-upgrades-add-body-morphing-and-60-layer-attires/ · https://gamedaily.com/games/wwe-2k26-creation-suite-features-double-the-content

### Soulcalibur VI (Creation) — stickers as tattoos
- Built on SCV's foundation: faces, armor, **sticker sets** carry over. Stickers/patterns/tattoos can be placed on the character, including equipment — a Siliconera creation walkthrough notes recreating a dress's bird design with stickers.
- Face side: pick from face presets + add **wrinkles, makeup, scars, stickers**. Character customization also offers tattoos and *Chinese characters* as body decoration (DashFight guide).
- Lesson for WH: stickers = the same texture-overlay system as tattoos, applied to clothing as well as skin. Unify them — one decal layer stack that targets skin *or* attire textures.
- Sources: https://dashfight.com/news/soul-calibur-vi-custom-character-creation-guide-1556 · https://www.siliconera.com/soulcalibur-vi-creation-suite-works-best-when-you-try-to-stick-to-the-spirit-of-a-character/ · https://culturedvultures.com/soulcalibur-vi-modes-might-just-rival-injustice-2/

### Tekken 7 / Tekken 8 — accessories + face paint (thin, but instructive)
- T7/T8 customization is **accessory-slot based**, not free tattoo placement: two accessory slots equippable to face, head, left/right shoulders, arms, legs, back; **size, angle, depth, and position adjustable** per accessory (Tekken Wiki "Customize").
- T7 dropped the decal system TTT2 had; T8 added a **face-paint tab** (players note only ~2 face-paint options at launch — "Having a facepaint tab when there a whopping 2 facepaints options hurts so bad it's funny"). Makeup exists as a separate T7 category ("Make-up").
- Lesson for WH: Tekken's per-accessory transform controls (size/angle/depth/position) are the right UI vocabulary for tattoo placement too, but their *catalogue* approach is thin — WH beats it by combining WWE-style layers + upload with Tekken's transform controls.

### Def Jam: Fight for NY — tattoos as progression
- **Manny's Tats** shop: tattoos bought with fight cash, **more styles/patterns unlock as story progresses**; tattoos raise the Charisma stat (with clothes and jewelry), which fills the Momentum meter faster (GameFAQs FAQ by Rice_Boi_510; Wikipedia).
- Lesson for WH: tattoos as *unlockable content tied to progression* (rank ladder / story) — fits WH's 53-tier rank system and the "Just Fun" festival modes. Tattoo catalogue can double as a reward track.

### WWF No Mercy / WrestleMania XIX (teardown lane)
- No dedicated tattoo system found in public docs — CAW guides document a **layer-based system** (32 layers total incl. compulsory Face Skin, Body Skin, Hair, Eyebrows, Eyes, Lips, Teeth, Underwear layers) with body-part sections. The WMXIX/No Mercy teardown files (already in our pull lane) should be mined for their body-part layer tables and any paint/decal structures — flagged as an open extraction item in §7.

---

## 4. Placement-system spec (distilled from all sources)

The suite's tattoo/decal editor should implement this control set — every item below is
attested in at least one shipping system above:

1. **Body zones** (GTA/FiveM model): torso-front, torso-back, left arm, right arm, left leg,
   right leg, head/face. A tattoo belongs to one zone; the zone selects the target texture
   (skin region or attire piece).
2. **Transform controls** (Tekken accessory vocabulary + FiveM creator): position (drag on
   3D body), rotation (spin), scale (uniform + per-axis), mirror (flip horizontally for
   symmetrical placement — e.g. left arm ↔ right arm), depth/offset (polygon offset to
   beat z-fighting on the baked texture's normal map if used).
3. **Layering order** (WWE 2K model): tattoos stack in an ordered layer list — 40 head/body
   layers is the reference budget; reorder, toggle visibility, duplicate layer.
4. **Opacity** (WWE paint tool / SC stickers): per-layer alpha 0–100%.
5. **Color tinting** (WWE layers): multiply tint over the tattoo art — lets one blackwork
   flash serve as red ink, white ink, etc. without duplicate assets.
6. **Blend/composite behavior**: multiply-over-skin for ink (so skin tone and tan show
   through), normal-alpha for face paint/makeup; optional shine/metallic toggle (WWE
   community request — useful for gold-leaf / cybernetic decals).
7. **Symmetry**: mirror-copy a tattoo to the opposite limb in one action.
8. **Bake step**: interactive `DecalGeometry` preview → on confirm, composite into the
   skin/albedo texture at the zone's UV coordinates with island-padding (dilation) to avoid
   seam artifacts (the three.js-forum "Fill Texture Seams" technique — bleed edge pixels
   ~16 texels past UV boundaries).

---

## 5. Custom design generation

- **User-uploaded image → tattoo** (WWE Image Uploader is the reference): accept PNG (alpha),
  SVG, JPG; pipeline steps — crop to design, optional background removal (GIMP fuzzy-select
  flow or Tattoo Pack's Gemini stencil conversion as reference), optional stencil-ize
  (line-art extraction for blackwork), resize to zone texture budget, register into the
  tattoo catalogue with tags (style, zone, color profile).
- **Procedural generation**: Inkscape SVG parametric designs (mandalas, tribal bands, geometric
  sleeves — sacred-geometry generators fit WH's visual art direction: kaleidoscope/mandala/
  fractal motifs from the art bible); GIMP script-fu batch conversion of flash packs to
  tattoo-ready alpha PNGs.
- **AI-generated tattoo designs (2026)**: the open route is **Stable Diffusion (+ tattoo
  LoRAs)** — local, free, fine style control (wowslider roundup). Dedicated free tools:
  **Tat Ink (tat.ink)** — text-to-tattoo, Tattoo Diffusion V2/V1 models, style presets
  (Japanese, tribal, blackwork, dotwork, watercolor), image-to-tattoo, virtual try-on;
  **AI Tattoo Salon (aitattoosalon.com)** — no-signup diffusion generator; **iapixora.com**
  — free, no-watermark dev-built generator (DEV.to walkthrough). Commercial references:
  BlackInk AI, InkHunter (AR try-on — the AR preview concept maps to our 3D placement
  preview), Midjourney (high-art concepts, needs simplification to linework).
  Recommendation: SD + tattoo LoRAs for the in-pipeline generator (offline, no per-design
  cost, fits the repo's open-source posture); Tat Ink as the manual ideation tool.
  Sources: https://en.ai-pedias.com/blog/ai-tattoo-design-generator-2026 · https://tat.ink/blog/best-tattoo-generator/ · https://www.jotform.com/ai/best-ai-tattoo-generator/ · https://clawdbytes.com/article/2026-09-03-i-built-a-free-ai-tattoo-generator-in-2026-no-signup-no-watermark

---

## 6. Face paint + makeup

- **Face zones** (distilled from T8/SCVI/WWE): forehead, eyes (lids + surrounding),
  cheeks, nose, mouth/lips, chin/jaw, full-face. Per-zone placement with the same
  layer stack as body tattoos (opacity, tint, mirror).
- **Types to catalogue** (attested across games): war paint (stripes/blocks), tribal
  markings, clown (full-face + accents), skull/sugar-skull, kami-shibai/kabuki-inspired
  striping (fits WH's Japanese-mythology lane), scar overlays, "Chinese characters" style
  calligraphy decals (SCVI), team/logo paint.
- **Makeup subsystem** (T7 "Make-up" category; SCVI makeup+wrinkles+scars): lipstick
  (color + finish: matte/gloss), eye makeup (eyeshadow, eyeliner, per-eye control),
  blush, foundation tint — these are small-zone, high-opacity layers on the face texture;
  implement as preset layer stacks in the face-zone editor.
- **WWE paint tool note**: face/body paint shares the layer system with tattoos — one
  implementation, two catalogues (art differs; mechanics identical). SCVI's lesson stands:
  makeup, scars, wrinkles, stickers are all entries in the same overlay stack.
- **T8 caution**: a face-paint tab with only 2 options reads as a joke to players —
  ship the *system* with a real starter catalogue (procedural + AI-generated sets) or
  don't ship the tab.

---

## 7. Open items / extraction queue

1. **WMXIX / WWF No Mercy teardown**: mine the CAW body-part/layer tables for paint/decal
   structures (wwe-2k, wmxix, wrestlemania-xix, wwf-no-mercy pulls already authorized).
2. **Tekken 8 pull** (waiting on user's Steam purchase confirmation): extract the face-paint
   assets and the accessory transform (size/angle/depth/position) implementation.
3. **TTT2 decal system**: T7 dropped decals; TTT2 had them — extract TTT2's decal
   implementation as the closer Tekken-side reference.
4. **WWE 2K Paint Tool**: extract the legacy paint-tool transparency/shine math for the
   per-layer blend controls.
5. **ComfyUI Body Decal**: verify license, evaluate as the AI tattoo/makeup prototyping
   node in the existing ComfyUI flow.
6. **Fluid Painter NSFW** (already filed for the skin system) owns hand-painted tattoo
   touch-up; the tattoo layer stack must round-trip through it (bake → paint → re-bake).
7. **Ink/paint as progression**: design the tattoo-unlock track against the 53-tier rank
   ladder and story/festival modes (Def Jam Manny's Tats model) — design decision for the
   user, not this doc.

---

*Filed per standing directive: every conversation's substance goes in the repo (docs/owner-directives.md, docs/research/, docs/decisions/). Research only — no code. Build phase is a separate lane.*
