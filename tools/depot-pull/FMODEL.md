# FModel + Linux extraction notes

## FModel (Windows)

FModel (https://fmodel.app) is the interactive UE pak browser/exporter.
It is Windows-only and GUI-driven — it does NOT go in this repo (it updates
often; download it fresh). Use it on a Windows machine:

1. Add undetected game → point the archive directory at your pulled paks.
2. Enable the Local Mapping File (`.usmap`, e.g. Tekken 8's
   `T8_mapping_01_28_2026.usmap`) when the game needs it.
3. Load mode **All** → browse → right-click meshes/animations → export
   (PSK/UEModel/UEAnim + PNG textures).

## Headless / Linux agents

Use scriptable tools instead of FModel:

- **repak** (https://github.com/trumank/repak) — CLI pak unpacker:
  `repak unpack -a <aes_key> game.pak out/`
- **CUE4Parse** (https://github.com/FabianFG/CUE4Parse) — .NET library for
  scripted UE asset reads/exports.
- **UModel** (https://www.gildor.org/en/projects/umodel) — older UE titles.

## Blender finish (all platforms)

- **UEFormat** plugin (https://github.com/h4lfheart/UEFormat) imports
  `.psk/.uemodel/.ueanim` → export **FBX/GLB**.
- Tekken 8: the community **T8 Tools** Blender addon (3.6–4.5 LTS).
- Batch: Blender headless `bpy.ops.export_scene.fbx` over exported assets.

## AES keys

Community-held (game wikis, Discords). Never from the game EXE unless you
must (Steamless + AES-key-finder is the fallback). Keys rotate per patch —
check the game's wiki for the current one.
