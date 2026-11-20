# Rated-M Skin Workflows — Research 2026-10-19

How professional adult 3D models are skinned/textured, and the 2026 high-level tech.
Researched from real sources (not training data). All URLs verified live 2026-10-19.

## 1. Professional skin texturing pipeline (film/VFX standard)

Source: 80.lv "Guts: Sculpting & Texturing Realistic Skin Detail"
(https://80.lv/articles/guts-sculpting-texturing-realistic-skin-detail?amp=1)

- **Sculpt first**: pores/wrinkles sculpted in high-poly (ZBrush/Mudbox), then baked to
  normal/displacement maps for the low-poly. Never model pores — bake them.
- **TexturingXYZ displacement workflow**: multi-channel displacement maps (separate
  channels for large/medium/micro detail), intensity kept subtle (values ≤ 0.1).
- **Subsurface scattering**: the "flesh-like quality". Arnold `randomwalk_v2`,
  subsurface color painted in Mari from the color map, "Skin 2" preset radius.
- **Specular layering**: specular + coat driven by the red channel of the displacement
  map through remap nodes; coat intensity from a dedicated spec map.
- **Eyes as separate parts**: sclera, iris, lacrimal, plus a "liquid" geo layer with
  noise bump for irregular reflection.

Source: Adobe Substance 3D Painter docs — Subsurface material type
(https://experienceleague.adobe.com/en/docs/substance-3d-painter/using/features/subsurface-scattering/subsurface-material-type)
- Skin needs: good base texture (lots of color variation), STRONG height/normal
  texture ("the subsurface effect will soften surface details — strong details
  compensate"), scale 0.05–0.2, per-region scatter tint.

Source: iRendering "5 Tips for Skin Texturing Real-time Characters"
(https://irendering.net/5-tips-for-skin-texturing-real-time-characters-with-daz3d/)
- Projection-paint skin details from photo reference directly onto the mesh
  (Substance Painter projection tool), then bake to low-poly.
- Always include a pore **bump map** — real skin is never smooth; micro-bumps sell it.
- Keep topology clean around eyes/lips or texture/topology misalignment causes
  "strange colorization".

## 2. Real-time / game skin (PBR)

Standard map stack for game skin in 2026:
- **Base color**: layered — base tone → mottling (red/yellow blotches) → blemishes,
  freckles, veins → makeup/tattoos as separate decal layers.
- **Normal**: baked pore/micro-wrinkle detail (OpenGL format for glTF).
- **Roughness**: skin ~0.55–0.7; oilier zones (forehead, nose) lower; dry zones higher.
- **Subsurface/thickness**: red-dominant scatter color; thin areas (ears, nostrils)
  scatter more.
- **AO/cavity**: baked from high-poly for creases.

## 3. "Clothes as skin texture" (second-skin / body-paint technique)

Common in stylized adult game mods: garments are painted directly into the skin's
base-color texture (trompe-l'œil) instead of modeled as geometry.
- DAZ Studio technique (daz3d.com forums): select skin surfaces, remove diffuse maps,
  drive metallic/painted looks via shader params while KEEPING bump/normal maps so
  skin detail shows through the "paint" — the Goldfinger gold-body method.
- LIE (Layered Image Editor) overlays in DAZ: paint layers composited over skin
  without destroying the base.
- For our pipeline: paint garment designs (lace, straps, latex seams) as texture
  layers over the nude skin base, keeping the pore normal map underneath untouched.

## 4. 2026 high-level tech

- **AI-assisted texture generation**: Tripo 3D documents AI skin-texture generation
  from text/reference images with cross-map consistency, then manual refinement
  (https://www.tripo3d.ai/blog/explore/3d-skin-texture-creation-techniques-tools-best-practices).
  Bake3D (Oct 2026) unifies image→textured-model→rig→motion with MCP connectivity.
- **Procedural skin materials**: MakeHuman's MPFB2 `EnhancedSkinMaterial` adds
  PROCEDURAL pore detail + SSS config in-shader — no texture dependency.
  (https://static.makehumancommunity.org/mpfb/docs/materials.html)
- **Neural materials / real-time SSS**: 2026 SSS shader guides emphasize per-region
  scatter-distance maps painted in Substance/Mari + real-time iteration.
  (https://www.all-you-search.com/subsurface-scattering-skin-shader-guide-2026)
- **Photogrammetry-derived detail**: scan-based pore alphas (TexturingXYZ-style)
  remain the film gold standard; tiled and blended at low intensity for games.

## 5. What we pulled in (license-documented)

| Asset | Source | License | Use |
|---|---|---|---|
| skin_0001 4K PBR set (color, normal-OpenGL, roughness, subsurface, AO, height) | texturecan.com/details/574/ | Site brands "Free PBR Textures and CC0 3D Models"; third-party roundups list TextureCan as free-for-commercial. No per-file license text found — attribution to texturecan.com kept in README. | Pore/micro-wrinkle normal detail blended over body normals; roughness variation reference |
| MakeHuman skin system docs | makehumancommunity.org / CGW / CGChannel | MakeHuman 1.1+ content (incl. skin texture library) is CC0 "No Rights Reserved" per CGW/CGChannel reporting | Workflow reference: skin = PNG + MHMAT descriptor; procedural pore approach |
| BodyParts3D / Z-Anatomy | dbcls.jp / z-anatomy.com | CC BY-SA (attribution + share-alike) | DOCUMENTED ONLY — not pulled (share-alike incompatible with repo use without relicensing) |

NOT pulled (honest exclusions):
- TexturingXYZ multi-channel skin alphas — commercial, paid. Documented as the film-standard upgrade path.
- DAZ 3D base figures — proprietary license, cannot redistribute.
- Quixel Megascans skin — free only inside Unreal Engine.

## 6. Our pipeline (what was built)

`tools/customization/skin-library/` in western-heart:
1. **Patch repair**: pale unpainted fills detected (HSV: high-V/low-S + flat-fill +
   connected-component size gate) → OpenCV Telea inpainting from surrounding skin.
2. **Tone-safe detail**: multi-octave mottling (±3.5% luminance, warm shift) + fine
   grain (±1.5%) — applied globally, tattoos/clothing masked by darkness/saturation.
3. **Pore normals**: TextureCan OpenGL pore normal map blended at 35% over the
   model's normal map (tangent space, tileable).
4. **GLB rebuild**: fixes the broken image bufferView offsets in the shipped A5/A2
   GLBs (textures were pointing at wrong BIN offsets) — new files, originals untouched.
