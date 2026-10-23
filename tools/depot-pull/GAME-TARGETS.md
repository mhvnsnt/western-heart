# Game targets — app/depot IDs and pull commands

Pull ONLY the paks (or the file types you need). Never the full depot.
Owning the game on the Steam account you pass is required for paid games.

## Tekken 8 (UE5) — top teardown priority

- Steam AppID **1778820**, main depot **1778821** (~112 GB full — DO NOT pull all)
- Paks live under `Polaris/Content/Paks/`, AES-encrypted (community key + mappings)

```bash
./depot-pull.sh list 1778820 1778821
./depot-pull.sh get 1778820 1778821 paks-only.txt ./t8paks <steam_user>
```

Then: open `./t8paks` in FModel (undetected game) with the community mappings
file `T8_mapping_01_28_2026.usmap` (github.com/CDDTreborn/Tekken-8-Resources),
export `SK_CH_*` meshes / `AS_*` animations → Blender (T8 Tools addon) → FBX.

## Soulcalibur VI (UE4)

- Steam AppID **544750** (English Windows depot)
- Same pipeline: pull paks only → FModel + community AES key → Blender → FBX/GLB.

## Mortal Kombat 1 (UE4 custom)

- Pull paks only → FModel + AES key (+ mk1hook knowledge) → Blender → FBX/GLB.

## WWE 2K26

- Weakest extraction target: no verified public model exporter for 2K-era `.pac`
  files; tooling (CakeTools/CakeView) is Patreon-gated. Pull for moveset/grapple
  REFERENCE and Community Creations content, not for fast model extraction.
- Depot/filelist filtering still works in principle (it's a Steam game), but
  without an extraction tool the files aren't useful yet.

## Adding a new target

1. Find the AppID + depot on steamdb.info.
2. `./depot-pull.sh list <app> <depot>` and confirm the file layout.
3. Write a filelist (start from `paks-only.txt`) and pull.
4. Document the game's entry in this file for the next agent.
