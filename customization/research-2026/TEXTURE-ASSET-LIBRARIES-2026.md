# Free Texture & Asset Libraries 2026 — Creation Suite Sources
**Date:** 2026-10-23  
**Purpose:** Free sources for textures, materials, tattoo designs, decals, and 3D assets for the WH creation suite. Part of the 2026 industry-standard sweep.

## PBR Texture Libraries (CC0 — no attribution, commercial OK)

| Library | Size | License | API | Notes |
|---------|------|---------|-----|-------|
| **Poly Haven** | 850+ textures, 990+ HDRIs | CC0 | Free, no key | The champ. 8K scanned, full PBR map sets. Textures + HDRIs + models. |
| **ambientCG** | 2,000+ materials, 420+ HDRIs | CC0 | Free (`ambientcg.com/api/v2`) | Biggest pure material library. Per-download resolution/format choice. |
| **3DTextures.me / ShareTextures / cgbookcase** | Thousands combined | CC0 | Varies | Extra variety. |
| **3DTexel** | 1,000+ handmade + stylized | CC0 (handmade lib) | Free account | Game-ready, Unreal + Substance Painter plugins. |
| **Kenney.nl** | Large | CC0 | Direct download | Prototype/stylized textures. Great for placeholder→final pipeline. |

**Pull plan:** Wire Poly Haven + ambientCG APIs into the creation suite's texture/material browser. CC0 = zero legal friction. Cache locally, don't hotlink.

## Blender-Native Material/Texture Tools

| Tool | What | Cost |
|------|------|------|
| **BlenderKit** | Material/asset library inside Blender | Free tier |
| **PBR Painter 3** | Layered multi-channel PBR painting with masks/filters | Paid (check) — evaluate |
| **Layer Painter** | Photoshop-style layer/mask workflow in Blender | Paid (check) — evaluate |
| Built-in Texture Paint | Blender's native workspace | Free, in our toolchain |

## Tattoo / Decal / Logo Design Sources

| Source | License | Use |
|--------|---------|-----|
| **Pixabay** | Free (Pixabay license) | Vectors, PNGs, line art, emblems → tattoo stencils |
| **Freepik** | Free with attribution | Tattoo-inspired icons, ornaments, typography |
| **The Noun Project** | Varies (some free) | Simple vector marks → minimal tattoos/logos |
| **Our 99 No Mercy tattoos** | Already in repo | `teardown/wwf-no-mercy/textures/rom/tattoo/` — already pulled |
| **AI generation** | Via our pipeline | Generate original tattoo/decal/logo designs on demand |

**Avoid:** clipart-library.com (personal use only), FreePBR (commercial = paid).

**Tattoo workflow (FiveM Tattoo Creator model):** drop design → choose body zone → position/scale/rotate on 3D body → export as overlay. We build the same flow in our suite.

## Free 3D Asset Libraries (parts/clothing/accessories)

| Library | License | Use |
|---------|---------|-----|
| **Poly Haven models** | CC0 | Props, accessories |
| **Quaternius** | CC0 | Stylized assets |
| **Kenney.nl** | CC0 | Prototype parts |
| **Sketchfab** | Varies (filter CC) | Specific parts |

## Game Icons (UI)
- **game-icons.net** — CC BY 3.0, must credit designer + site. Thousands of game UI icons.

## License Rules for the Suite
1. **CC0 only** for anything shipped in-game (Poly Haven, ambientCG, Kenney, Quaternius)
2. **Attribution-required** (CC BY) only for dev tools, never shipped assets — or credit properly
3. **Screenshot + URL + license** saved for every pulled asset (GameDev.net legal advice)
4. **Never** pull from "free for personal use only" sources into the game

## Sources
- Cinevva free PBR textures/HDRIs guide (Sept 2026)
- 3DTexel CC0 library comparison (Oct 2026)
- KorviX3D free textures 2026 edition
- StraySpark best Blender material addons 2026
- GeekChamp free tattoo design sites
- GameDev.net texture licensing thread
