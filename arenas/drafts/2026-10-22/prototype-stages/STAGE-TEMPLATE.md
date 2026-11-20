# Stage Template

Each stage is defined in a JSON file: `prototype/stages/{id}.json`.

## Required Fields

```json
{
  "id": "stage-id",
  "name": "DISPLAY NAME",
  "universe": "Which Eastern Mind land (Tree of Life / Plains of Chi-U / Shrine / Helix Palace / Palace of Dreaming / Phantom Marketplace / Central Mountain)",
  "description": "Visual and thematic description",
  "dimensions": {
    "width": 16.8,
    "depth": 4.0,
    "wallDistance": 8.4
  },
  "floor": {
    "material": "path/to/floor/texture/",
    "roughness": 0.8,
    "metallic": 0.0
  },
  "walls": {
    "material": "path/to/wall/texture/",
    "visible": false
  },
  "background": {
    "type": "skybox | 3d-model | image",
    "source": "path/to/background/"
  },
  "lighting": {
    "ambient": "#hex",
    "directional": "#hex",
    "intensity": 1.0
  },
  "music": "path/to/stage/theme.ogg",
  "ambientSfx": "path/to/crowd_or_nature.ogg"
}
```

## Dimensions

Standard fighting arena: 16.8 units wide (matches tk's ARENA_LIMIT of 8.4 each side).
Depth is visual only — combat happens on the X axis.

## Texture Sources

- ambientCG (CC0): `assets/free-pull-1/ambientcg/textures/`
  - Wood096, Wood095 → dojo/temple floors
  - Fabric085, Fabric084 → banners, curtains
  - Metal063, Metal049A → Helix Palace, industrial stages
- Poly Haven (CC0): additional PBR textures as needed.
