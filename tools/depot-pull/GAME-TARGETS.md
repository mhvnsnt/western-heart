# Game targets — app/depot IDs and pull commands

Pull ONLY the paks (or the file types you need). Never the full depot.
Owning the game on the Steam account you pass is required for paid games.

## Tekken 7 (UE4) — FIRST-CLASS source (T3 is fallback-only)

- Steam AppID **389730**, Windows content depot **389731** ("TEKKEN 7
  Content"). Verified 2026-10-23 on steamdb.info: depot 389731 ships in the
  base-game package (Sub 74007) AND the Originals, Ultimate and Definitive
  Edition packages — it is the single Windows content depot for all of T7.
- Paks live under `TekkenGame/Content/Paks/` in the depot (matches an
  installed copy at `steamapps/common/TEKKEN 7/TekkenGame/Content/Paks/`).
- **No AES key needed.** T7's paks are NOT encrypted — verified in the public
  community docs (CDDTreborn/Tekken7_PC-Modding-Guides wiki: "Tekken 7 has no
  game encryption"). The only encrypted T7 content is Geese (MRY) and Noctis
  (MRZ) DLC files (per-file encryption, needs extra tools) — neither is in
  our pull scope. `repak unpack` opens the paks with no `--aes-key`.
- Character assets inside the paks live under in-game paths
  `Game/Content/Character/...`, filed per fighter by the community 3-letter
  code (`LAW` = Marshall Law, `LAR` = Lars, `MAR` = Marduk …).
- T7's depot paks are SHARED numbered chunks, **not** per-character files —
  depot-level filtering cannot isolate one fighter. Pull the paks, then select
  fighters after unpack (see `teardown/tekken7/T7-STEAM-EXTRACTION.md`).

```bash
./depot-pull.sh list 389730 389731
./depot-pull.sh get 389730 389731 t7-full-roster.txt ./t7paks <steam_user>
```

Then: `repak unpack` (no key) → asset identification → umodel batch export
(`-game=tekken7`) or FModel on Windows → Blender (UEFormat addon) → FBX/GLB →
moveset-library. Full pipeline: `teardown/tekken7/T7-STEAM-EXTRACTION.md`.
User-side steps — the pull runs on the USER's machine, we never touch Steam
credentials: `tools/depot-pull/T7-USER-STEPS.md`.

### T7 filelists

- `t7-law-lars.txt` — Law (LAW) + Lars (LAR) pull. Highest priority: the
  active pull lane is waiting on these two (no free T7 source exists —
  `teardown/tekken7/TEKKEN7-ROSTER-COVERAGE.md`). Same `*.pak` pull as below;
  Law/Lars isolation happens post-unpack, or user-side via
  `t7-find-character-paks.bat` (identifies which paks to upload).
- `t7-full-roster.txt` — all fighter paks. Roster data is spread across every
  chunk, so this is the full `*.pak` pull.
- `paks-only.txt` — the generic pattern both T7 filelists are based on
  (`regex:.*\.pak$`).

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
