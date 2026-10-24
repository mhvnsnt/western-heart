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
  `repak unpack -a <aes_key> game.pak out/` (the `-a` key is only needed for
  encrypted games — Tekken 7's paks need NO key, see below).
- **CUE4Parse** (https://github.com/FabianFG/CUE4Parse) — .NET library for
  scripted UE asset reads/exports.
- **UModel** (https://www.gildor.org/en/projects/umodel) — older UE titles.

## Blender finish (all platforms)

- **UEFormat** plugin (https://github.com/h4lfheart/UEFormat) imports
  `.psk/.uemodel/.ueanim` → export **FBX/GLB**.
- Tekken 8: the community **T8 Tools** Blender addon (3.6–4.5 LTS).
- Batch: Blender headless `bpy.ops.export_scene.fbx` over exported assets.

## AES keys

### Tekken 7 — NO KEY NEEDED (verified 2026-10-23, public community docs)

T7's pak files are NOT AES-encrypted. Source: CDDTreborn's
Tekken7_PC-Modding-Guides wiki (Umodel quick-start page): "Tekken 7 has no
game encryption". `repak unpack` opens them with no `--aes-key`.
The ONLY encrypted T7 content is Geese (MRY) and Noctis (MRZ) DLC files
(per-file encryption, needs additional tools) — neither is in our pull scope
(Law/Lars/Marduk/full roster are unaffected).

If a future T7 patch ever encrypts the paks, check for the community key in
this order: (1) CDDTreborn/Tekken7_PC-Modding-Guides wiki, (2) TekkenMods.com
guides, (3) the Modding Zaibatsu Discord. Then pass it to
`repak unpack --aes-key <key>`.

### General rule

Community-held (game wikis, Discords). Never from the game EXE unless you
must (Steamless + AES-key-finder is the fallback). Keys rotate per patch —
check the game's wiki for the current one.
