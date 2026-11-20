# Skin Library — production nude-reskin resources

Pulled 2026-10-19 for the Star Attire 5 / Silvertongue Attire 2 improved reskins
(owner order: "do better nude reskins than that").

## Pulled assets (license-documented)

### texturecan_skin0001/ — Human Face Skin 4K PBR set
- Source: https://www.texturecan.com/details/574/
- Files: color, normal (OpenGL), roughness, subsurface, AO, height — 4K
- License: TextureCan brands itself "Free PBR Textures and CC0 3D Models";
  third-party roundups (egneva.com, technofizi.net) list TextureCan as
  free-for-commercial-use. No per-file license text ships in the archive.
  Treated as free-for-commercial with attribution; NOT claimed as CC0.
- Used for: pore/micro-wrinkle normal detail (blended 35% over body normals),
  roughness variation reference.

### makehuman_notes.md — MakeHuman skin system (reference only, not pulled)
- MakeHuman 1.1+ content incl. its skin texture library is CC0 "No Rights Reserved"
  per CGW/CGChannel reporting; skins are PNG + MHMAT descriptors.
- MPFB2's EnhancedSkinMaterial does procedural pores + SSS in-shader — the
  approach our pipeline follows for generated detail.

## Honest exclusions (documented, NOT pulled)
- TexturingXYZ multi-channel skin alphas — commercial/paid (film gold standard).
- DAZ 3D base figures — proprietary, cannot redistribute.
- BodyParts3D/Z-Anatomy — CC BY-SA (share-alike incompatible here).
- Quixel Megascans skin — free only inside Unreal Engine.

## Pipeline (scripts/)
1. `build_skin.py` — patch detection (HSV high-V/low-S + flat-fill +
   connected-component gate) → OpenCV Telea inpaint.
2. `build_skin_v2.py` — regional skin-tone fill for large patches (median of
   surrounding good skin + matched grain, feathered edges) + mottling pass.
3. `build_maps.py` — pore normal blend (TextureCan OpenGL @ 35%) + roughness map.
4. `rebuild_compact.py` — GLB rebuild: new textures, FIXED image bufferView
   offsets (the shipped A5/A2 GLBs pointed textures at wrong BIN offsets),
   compacted (drops orphaned data), mesh/skin/weights byte-identical.

## Research
See `docs/customization/ADULT-SKIN-WORKFLOWS-2026-10-19.md` for the full
research: film skin pipelines (80.lv, Adobe), real-time PBR skin, second-skin /
body-paint technique, 2026 AI/procedural tech.
