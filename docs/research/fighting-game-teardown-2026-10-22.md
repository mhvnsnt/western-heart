# Fighting Game Teardown Research — Asset Extraction for a Tekken-Based 3D Fighter
Date: 2026-10-22. Research window: ~45 min. Sources: web index + direct page fetches (SteamDB depots fetched live).

## Summary
- **Best WWE target: WWE 2K26** (Mar 13, 2026) — biggest Creation Suite/Community Creations (400+ roster, 200 CAW slots, 2,000 image slots) — but its **raw asset-extraction pipeline is weak**: modern 2K .pac tooling is mostly private/Patreon-gated (CakeTools/CakeView), no verified public FBX/PSK exporter for 2K-era models; Denuvo blocks exe-level tampering but file-based `_mods` .pac injection still works.
- **Tekken 8 CAN be pulled without the full 100+ GB install**: AppID **1778820**, main depot **1778821** (112.3 GiB download). Use **DepotDownloader** with `-depot 1778821` + a `-filelist` regex on `.*\.pak$` (requires owning the game on Steam) — downloads just the UE5 pak files, then open them directly in **FModel** with the community mappings file (`T8_mapping_01_28_2026.usmap`); no install, no EXE needed for extraction.
- Tekken 8 is UE5, AES-encrypted paks; the ModdingZaibatsu/CDDTreborn wiki is the live knowledge base (updated July 2026) with Blender addons (T8 Tools), base meshes, character/stage ID tables.
- **Fastest generic pipeline for UE games (SCVI, MK1, KOF XV, GG Strive):** partial depot download → FModel/UModel + AES key → export .psk/.uemodel/.ueanim → Blender (UEFormat plugin) → FBX/GLB. Hours, not days.
- **Top-3 teardown priority:** (1) Tekken 8, (2) Soulcalibur VI, (3) Mortal Kombat 1. Best YYH target: **Dark Tournament (PS2)** via emulator frame-capture — low fidelity, capture-only.

## Findings

### 1. WWE Games
**Most recent worth tearing down: WWE 2K26** (Visual Concepts, launched March 13, 2026; PC via Steam with Denuvo; PS5/Xbox Series X|S/Switch 2). Its Creation Suite/Community Creations is the largest in franchise history: 400+ playable roster, 200 Create-A-Superstar slots, 2,000 image slots, deeper body/face morphing, two-tone hair, create-an-arena — the richest source of in-game custom content ever for WWE (`index`, operationsports.com https://www.operationsports.com/wwe-2k26-devs-reveal-major-universe-mode-and-creation-suite-overhauls/ ; videogameschronicle.com https://www.videogameschronicle.com/news/wwe-2k26-release-date-editions-new-match-types-ringside-pass-system-showcase-mode-and-pre-order-bonus-revealed/).
- **Engine/format:** proprietary Visual Concepts engine. Assets live in `.pac` archives; moveset data format is not publicly documented.
- **Tools:** the active scene uses CakeTools/CakeHook (`.pac` injection via a `_mods` folder) and installers Tribute/CakeView — **both Patreon-gated; no free installer was known** as of the operationsports report (`index`, https://www.operationsports.com/how-to-download-mods-in-wwe-2k26/). Denuvo blocks exe/memory tampering (Cheat Engine, trainers) but **file-based .pac mods still work**. Old-era only: X-Packer for Xbox 360-era PAC files (`index`, http://sf4mods.blogspot.com/2010/07/how-to-work-with-xbox-360-pac-files.html).
- **Extraction reality:** no verified public tool exports 2K24/25/26-era wrestler models to FBX/PSK, and no documented moveset-file spec. Extraction means reverse-engineering the .pac model format yourself.
- **Partial download:** WWE 2K26 is on Steam, so DepotDownloader depot/filelist filtering works in principle (same method as Tekken 8 below) — but without an extraction tool the files aren't useful yet.
- **Verdict:** tear down 2K26 for **moveset/grapple reference and Community Creations content** (download CAWs in-game), but do NOT count on fast model/animation extraction — it's the weakest extraction target on this list.

### 2. Tekken 8 — extraction without the full game
- **Steam AppID 1778820** (`verified live` via SteamDB https://steamdb.info/app/1778820/depots/, read 2026-10-22). Depots: **1778821** main content (129.52 GiB on disk / **112.30 GiB download**), 1778822 (1.59 GiB, binaries), plus small DLC depots.
- **Engine/format:** built from scratch in **Unreal Engine 5** (`index`, multiple: https://www.gamespot.com/articles/tekken-8-is-built-from-the-ground-up-in-ue5-is-a-turning-point-for-the-series/1100-6507585/ ). Assets in AES-encrypted `.pak` files under `Polaris/Content/Paks/`; custom UE5 build requires a **`.usmap` mappings file** in FModel.
- **Exact path (no full install):**
  1. Install DepotDownloader: https://github.com/SteamRE/DepotDownloader (`index`).
  2. Discover pak paths: `DepotDownloader -app 1778820 -depot 1778821 -manifest-only` (dumps the file listing; `-filelist` supports `regex:` lines).
  3. Write `paks.txt` containing one line: `regex:.*\.pak$` then:
     `DepotDownloader -app 1778820 -depot 1778821 -filelist paks.txt -dir C:\T8paks -username <your_steam_user>`
     (owning the game on Steam is required; this skips ~110 GB of everything-but-paks).
  4. Get FModel from https://fmodel.app/ and the mappings file `T8_mapping_01_28_2026.usmap` from https://github.com/CDDTreborn/Tekken-8-Resources (both `verified live` via the wiki https://github.com/CDDTreborn/Tekken-8-Resources/wiki/T8-Resources-%E2%80%90-FModel-Setup-and-Basic-Use.).
  5. In FModel: add undetected game → point archive dir at the paks folder → enable Local Mapping File → Load mode **All** → right-click any `SK_CH_*` skeletal mesh / `AS_*` animation → export (PSK/UEModel/UEAnim, PNG textures).
- **Community:** ModdingZaibatsu Discord; CDDTreborn wiki (updated July 2026) has character abbreviation/ID table (Jin=`ant`, Kazuya=`grl`, Jun=`aml`), stage table, customization asset hierarchy, Blender "T8 Tools" addon (Blender 3.6–4.5 LTS), male/female base mesh .blend files (`verified live`, wiki info-dump https://github.com/CDDTreborn/Tekken-8-Resources/wiki/Tekken-8-Info-Dump-(Diary)).
- **Caveats:** the AES key is community-held (the mappings file + key workflow is documented in the Discord/wiki; you never need the game EXE if you pull paks from CDN). Season patches can shift the mappings file — the repo updates it (latest Jan 2026).

### 3. Yu Yu Hakusho Games
Candidates (`index`, hardcoregaming101 http://www.hardcoregaming101.net/yu-yu-hakusho-conclusion-playstation-2-cont-nintendo-ds-mobile/):
- **Dark Tournament (PS2, 2004, Atari)** — 3D fighter, 25+ characters, full movesets. **Most viable:** 4.7 GB DVD, runs in PCSX2, single-player; no public format docs, so extraction = **Ninja Ripper/RenderDoc frame capture** (static poses, manual cleanup; no clean rigs/animations).
- **The Battle of Yu Yu Hakusho 120% (Arcade 2006 / PS2 JP 2007)** — flashier, Virtua Fighter-like; same capture-only route, Japanese disc.
- **Tournament Tactics (GBA)** — 2D sprites; useless for 3D.
- **Spirit Detective (DS)** — low-poly/2D hybrid; poor value.
- Mobile "100% Maji Battle" was Unity but servers shut down — dead target.
- **Verdict:** Dark Tournament PS2 only if you need YYH-specific reference; expect **capture-only, days of cleanup per character** — lowest automation of all targets here.

### 4. Other Fighting Games — ranked for a Tekken-based 3D fighter
| Game | Engine / Format | Extraction tools | Teardown viability vs effort |
|---|---|---|---|
| **Soulcalibur VI** | UE4, .pak | FModel + community AES key; UModel | **Best effort/value after T8** — same Namco UE pipeline, 3D weapon fighter, small-ish download |
| **Mortal Kombat 1** | Custom UE4, .pak | FModel + AES key; mk1hook mod loader (`index`) | **High** — rich models/animations, mature FModel path |
| **Guilty Gear Strive** | UE4, .pak | UModel custom build + AES key + UE version from community Discord; assets at `RED/Content/Chara/<id>/Costume01/Mesh`; ASW modding book (`index`, https://gamebanana.com/tuts/14999, https://muuyo.github.io/asw-modding-book/ue4/getting-unreal.html) | **High** — very active modding scene, strong animation value |
| **King of Fighters XV** | UE4, .pak | FModel-compatible; mod-friendly per community | **High** — cheap, standard UE4 path |
| **Street Fighter 6** | RE Engine, `re_chunk_000.pak` | REtool (`retool -h <game>.list -x re_chunk_000.pak`, https://www.fluffyquack.com/tools/REtool.rar) + filename lists via ree-path-searcher (https://github.com/eigeen/ree-path-searcher); mesh conversion via RE-Engine-Lib | **Medium** — models extractable, no direct FBX; animation pipeline is work |
| **Dead or Alive 6** | Proprietary (Team Ninja), .tmc | TMC OBJ Tool / TMC Texture Tool (`index`, nexusmods), AutoLink loader | **Low–medium** — models yes, animations poor, scattered GUI tools |
| **EA Sports UFC 5** | Frostbite | Frosty Tool Suite (browse/extract; UFC 5 support partial) | **Low–medium** — powerful tooling exists but per-game support lags |
| **Virtua Fighter 5 Ult. Showdown** | Dragon Engine (RGG) | No mature public extraction pipeline found | **Low** — skip unless format research is the goal |
| **Def Jam FFNY / Fight Night** | Console-only, proprietary | Emulator + Ninja Ripper capture only | **Low** — capture-only, no rigs; reference value only |

### 5. Fast Automated Teardown Methods
- **Steam partial downloads:** SteamCMD can't filter files — use **DepotDownloader** (https://github.com/SteamRE/DepotDownloader). Workflow: `-manifest-only` to list → `-depot <id> -filelist <regex on .pak>` → get only what you need. Requires game ownership on the Steam account for paid games. Community manifests/keys: https://github.com/pjy612/SteamManifestCache.
- **UE .pak (the core pipeline):** **FModel** (https://fmodel.app/, repo https://github.com/4sval/FModel) → browse + bulk-export models/animations/textures as `.psk/.uemodel/.ueanim` → **UEFormat Blender plugin** (https://github.com/h4lfheart/UEFormat) imports to Blender → export **FBX/GLB**. AES keys: community Discords/wikis (never from the EXE unless you must — Steamless + AES-key-finder is the fallback). **UModel** (https://www.gildor.org/en/projects/umodel) for older UE titles; **repak** (https://github.com/trumank/repak) for scripted batch unpacks (`repak unpack -a <key> game.pak out/`).
- **Unity:** **AssetStudio** (https://github.com/Perfare/AssetStudio) — load bundles → export FBX with AnimationClips in one batch.
- **PS2/PS3-era:** ISO dump → QuickBMS (https://aluigi.altervista.org/quickbms.htm) with community scripts if format is known; else emulator + Ninja Ripper/RenderDoc capture (slow, manual).
- **Batch conversion:** script FModel CLI exports or repak unpacks, then a Blender headless Python pass (`bpy.ops.export_scene.fbx`) to convert .psk/.uemodel imports to FBX/GLB unattended — this is the "hours not days" loop for UE titles.

### 6. Legal Reality Check
Extracting assets you own sits in a gray zone: game EULAs (Steam, 2K, Bandai Namco) uniformly prohibit reverse engineering and redistribution; DMCA §1201 makes circumventing access-control tech (e.g., pak AES encryption, Denuvo) independently unlawful, with only narrow exemptions such as §1201(f) reverse engineering for interoperability (law.justia.com/codes/us/2021/title-17/chapter-12/sec-1201/). The models/animations/stages themselves are copyrighted works — private study/extraction is the lowest-risk posture, while **redistributing ripped assets or shipping them inside a released mod/game is copyright infringement and the usual trigger for C&Ds and DMCA takedowns**; in practice modding communities survive by staying non-commercial and not redistributing original assets, and publishers tolerate file-mods while striking redistribution. (Factual summary, not legal advice — consult counsel before shipping anything.)

## Ranked Action Plan
**(a) Tear down FIRST (max moveset/model value, min effort):**
1. **Tekken 8** — UE5, best docs, direct Tekken moveset/animation lineage for your Tekken base; pak-only CDN pull avoids the 112 GB.
2. **Soulcalibur VI** — UE4, same publisher pipeline, 3D weapon-fighter stages/models via standard FModel path; small download.
3. **Mortal Kombat 1** — UE4, FModel + AES key, huge animation/moveset library (fatalities, strings) with clean skeletal data.

**(b) Toolchain per game:**
- T8: DepotDownloader → FModel (+ `T8_mapping_01_28_2026.usmap`) → Blender (T8 Tools addon + psk/psa importer) → FBX.
- SCVI: DepotDownloader (AppID 544750, English Windows depot) → FModel + community AES key → Blender (UEFormat plugin) → FBX/GLB.
- MK1: DepotDownloader → FModel + AES key → same Blender finish. Batch via `repak unpack` + Blender headless script.

**(c) Fastest no-full-download method (copy-paste):**
```
# 1. list the depot's files (Tekken 8 example)
DepotDownloader -app 1778820 -depot 1778821 -manifest-only
# 2. paks.txt contains one line:  regex:.*\.pak$
DepotDownloader -app 1778820 -depot 1778821 -filelist paks.txt -dir C:\T8paks -username <steam_user>
# 3. open C:\T8paks in FModel (undetected game) + mappings file, export; convert in Blender headless to FBX/GLB
```
Requires: Steam account owning the game; .NET 8 for FModel; Blender 3.6–4.5 LTS for the T8 Tools addon.

## Could Not Verify / Open Questions
- WWE 2K26 Steam AppID/depot layout not pulled (not needed given weak extraction tooling); no public FBX/PSK exporter for 2K-era models was found — if WWE models are essential, budget format RE work or use CAW/Community Creations content in-game.
- Exact Tekken 8 pak filenames inside depot 1778821 (get via `-manifest-only`); AES key distribution point (Discord/wiki — rotates per patch; mappings file current as of 2026-01-28).
- VF5US Dragon Engine and UFC 5 Frostbite extraction maturity — no verified turnkey path found; treated as low priority.
- DepotDownloader CLI syntax verified against docs; exact pak-folder layout for T8 (`Polaris/Content/Paks/`) confirmed via community wiki.

## Sources
- Tekken 8 modding wiki (CDDTreborn), FModel setup + info dump — https://github.com/CDDTreborn/Tekken-8-Resources/wiki (read 2026-10-22, `verified live`)
- SteamDB — TEKKEN 8 depots — https://steamdb.info/app/1778820/depots/ (read 2026-10-22, `verified live`): AppID 1778820; depots 1778821 (112.30 GiB DL), 1778822, DLC depots
- FModel — https://fmodel.app/ ; repo https://github.com/4sval/FModel (`index`)
- Tekken 8 UE5-from-scratch — https://www.gamespot.com/articles/tekken-8-is-built-from-the-ground-up-in-ue5-is-a-turning-point-for-the-series/1100-6507585/ (`index`)
- WWE 2K26 Creation Suite overhaul — https://www.operationsports.com/wwe-2k26-devs-reveal-major-universe-mode-and-creation-suite-overhauls/ (`index`)
- WWE 2K26 Denuvo vs mods — https://www.operationsports.com/how-wwe-2k26-denuvo-drm-will-affect-pc-mods/ (`index`)
- WWE 2K26 details/editions — https://www.videogameschronicle.com/news/wwe-2k26-release-date-editions-new-match-types-ringside-pass-system-showcase-mode-and-pre-order-bonus-revealed/ (`index`)
- X-Packer (360-era PAC) — http://sf4mods.blogspot.com/2010/07/how-to-work-with-xbox-360-pac-files.html (`index`)
- DepotDownloader docs (SteamRE) — https://github.com/SteamRE/DepotDownloader + deepwiki CLI reference (`index`)
- UEFormat ecosystem — https://deepwiki.com/h4lfheart/UEFormat/5.1-asset-extraction-tools (`index`); repo https://github.com/h4lfheart/UEFormat
- GG Strive modding workflow — https://gamebanana.com/tuts/14999 (`index`); ASW modding book https://muuyo.github.io/asw-modding-book/ue4/getting-unreal.html (`index`)
- REtool for RE Engine — https://www.fluffyquack.com/tools/REtool.rar via https://gist.github.com/osyu/895c38cf77f08853353988780e52dfc0/revisions (`index`); ree-path-searcher https://github.com/eigeen/ree-path-searcher (`index`)
- TMC tools (DOA) — https://www.nexusmods.com/deadoralive5/mods/139/ (`index`)
- YYH games overview — http://www.hardcoregaming101.net/yu-yu-hakusho-conclusion-playstation-2-cont-nintendo-ds-mobile/ (`index`)
- DMCA §1201 — https://law.justia.com/codes/us/2021/title-17/chapter-12/sec-1201/ (`index`)
- Tools: UModel https://www.gildor.org/en/projects/umodel ; QuickBMS https://aluigi.altervista.org/quickbms.htm ; AssetStudio https://github.com/Perfare/AssetStudio ; repak https://github.com/trumank/repak ; CUE4Parse https://github.com/FabianFG/CUE4Parse ; SteamManifestCache https://github.com/pjy612/SteamManifestCache
