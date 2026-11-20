# TEKKEN 7 — Steam extraction pipeline (headless)

*2026-10-23. Status: PREP — depot verified, filelists written, user-side pull
pending. This doc is the runbook the moment the paks land.*

**Authorization basis:** the user bought Tekken 7 on Steam and authorized the
pull (game-ownership rule: when the user says they own a game, THAT IS
AUTHORIZATION — no proof needed, never ask for files). T7 is now FIRST-CLASS
source; T3 is fallback-only (owner law 2026-10-23).

**What this unblocks:** `teardown/tekken7/TEKKEN7-ROSTER-COVERAGE.md` records
T7 moveset/anims coverage at **0 of 51 fighters** — "requires the 47 GB game
paks". Law (LAW), Lars (LAR) and Marduk (MAR) have NO free T7 source anywhere;
the Steam pull is their path.

## 1. The pull (depot facts)

| Item | Value |
|---|---|
| Steam AppID | **389730** |
| Windows content depot | **389731** ("TEKKEN 7 Content") — verified 2026-10-23 on steamdb.info across the base, Originals, Ultimate and Definitive packages |
| Pak path in depot | `TekkenGame/Content/Paks/` (= `steamapps/common/TEKKEN 7/TekkenGame/Content/Paks/` on an install) |
| Engine | Unreal Engine 4 |
| Encryption | **NONE** — T7 paks are not AES-encrypted (community-verified, see §2) |
| Pak layout | Shared numbered chunks, NOT per-character files — one fighter's assets are spread across chunks shared with other content |

Pull commands and filelists: `tools/depot-pull/GAME-TARGETS.md`
(`t7-law-lars.txt`, `t7-full-roster.txt`). The pull runs on the USER's machine
— we never handle Steam credentials (`tools/depot-pull/T7-USER-STEPS.md`).

## 2. AES key status — NO KEY NEEDED

- **T7 needs no community AES key.** CDDTreborn's Tekken7_PC-Modding-Guides
  wiki (Umodel quick-start, public community documentation — NOT from the
  game EXE): *"Tekken 7 has no game encryption."*
- The ONLY encrypted T7 content is Geese (MRY) and Noctis (MRZ) DLC files
  (per-file encryption, needs additional tools). Neither is in our pull
  scope; Law/Lars/Marduk and the full roster are unaffected.
- **If a future T7 patch ever encrypts the paks**, check for the community key
  in this order: (1) CDDTreborn/Tekken7_PC-Modding-Guides wiki,
  (2) TekkenMods.com guides, (3) the Modding Zaibatsu Discord. Then:
  `repak unpack --aes-key <key> game.pak out/`. Keys are community-held —
  never pulled from the game EXE.

## 3. Headless pipeline: pak → FBX/GLB

All steps run on Linux EXCEPT the umodel/FModel export step, which needs
Windows (or Wine). Tools are free/open-source.

### Step 1 — unpack (Linux-native, no key)

```bash
# repak: https://github.com/trumank/repak (single binary, cargo install or release zip)
for p in *.pak; do repak unpack "$p" ./t7unpacked/; done
# verify: repak list <pak>  — lists internal paths without extracting
```

### Step 2 — asset identification (paths inside the paks)

In-game root is `Game/Content` (pak paths are prefixed `TekkenGame/Content/`).
Community-verified locations (CDDTreborn wiki):

| Asset kind | In-game path | Notes |
|---|---|---|
| Character assets | `Game/Content/Character/` | meshes, skeletons, items |
| Character meshes | `Game/Character/Items/Mesh/<CODE>/` | per-fighter 3-letter code folders (`LAW`, `LAR`, `MAR`…), subfolders per part: Upper, Lower, Full_body, Head, Face… |
| Mesh prefixes | `SK_` skeletal mesh · `SKT_` skeleton · `SM_` static mesh · `PA_` physics asset | textures `T_*_D` (diffuse) `_N` (normal) `_M` (mask) |
| Character items (CI/CCI/CS) | `Game/Character/Items/CharacterItem/` etc. | customization sets, auras, effects — umodel "save package", not plain export |
| UI art (character select!) | `Game/Content/UI_common/Texture2D/ReplaceImages` | `CS_*` folders = character-select panels/portraits — feeds the user's select-screen rebuild directive |
| Stages | `Game/Content/Maps` (`stgXX_geom.umap`), meshes `Game/Content/Stage/stgXX` | stage codes in the wiki (stg00 Mishima Dojo … stg32 Island Paradise) |
| Audio | `Game/Content/WwiseAudio/Windows/` | Wwise banks |

Priority fighter codes: **LAW** = Marshall Law → Buffalo Bill · **LAR** = Lars
→ Chordz · **MAR** = Craig Marduk → Jotei. Full community code table:
https://github.com/CDDTreborn/Tekken7_PC-Modding-Guides/wiki/Tekken-7-Basic-Modding-Information
(note: the wiki list is missing Julia/Zafina codes — confirm in umodel at pull time).

After unpack, isolate a fighter's files by code, e.g.:

```bash
find ./t7unpacked -ipath "*character*/*law*"
```

### Step 3 — export meshes/animations (Windows or Wine)

**Option A — umodel batch (scriptable):**

```
umodel -path="./t7unpacked" -game=tekken7 -export -out="./t7export" <PackageName>
```

- umodel: https://www.gildor.org/en/projects/umodel. The community's
  documented GUI path is Override game detection → Unreal Engine 4 →
  Tekken 7; the CLI `-game=tekken7` override is the batch equivalent
  (verify the tag at runtime — GUI path is the confirmed one).
- Export formats: `.psk` / `.gltf` meshes (+ `.png`/`.tga` textures),
  animations alongside. umodel has no official Linux build — run on Windows
  or under Wine.

**Option B — FModel on Windows** (GUI): undetected game → archive dir =
unpacked folder → export PSK/UEModel/UEAnim + PNG. No `.usmap` mapping file
is needed for T7 (unlike T8).

**Option C — CUE4Parse** (https://github.com/FabianFG/CUE4Parse): .NET,
cross-platform, scripted asset reads/exports — the Linux-native alternative
when no Windows box is available. The crew has built it before.

### Step 4 — Blender finish (all platforms, headless OK)

- **UEFormat** addon (https://github.com/h4lfheart/UEFormat) imports
  `.psk` / `.uemodel` / `.ueanim` into Blender.
- Batch convert headless: `blender --background --python t7_to_fbx.py`
  (`bpy.ops.export_scene.fbx` / glTF exporter) → **FBX/GLB**.
- Then: rig check → moveset-library (below).

## 4. Moveset-library handoff — what the paks give us vs. open research

**The asset pull yields:** models (`SK_`), skeletons (`SKT_`), animations,
textures/materials, UI art, stages, audio. These unblock the 0/51 T7
moveset/anims gap at the ASSET level.

**Moveset LOGIC caveat (be straight about it):** T7's native moveset binary
format is NOT publicly documented the way T3's is. There is no verified
community spec for extracting per-move hit/frame data straight from T7 paks
today. So:

- Models, animations, stances, poses → straight from this pipeline.
- Per-move frame data / movelists → continue from the existing banks:
  `docs/t7t8-reference/frame-data-t7/*.json` (community frame data —
  `law.json`/`lars.json` already banked) plus the TTT2/T3 moveset lanes.
- Reverse-engineering T7's native moveset binaries is an OPEN research item,
  not a blocker — the Law/Lars lane proceeds on assets + banks.

## 5. Disk rules (mandatory)

`tools/depot-pull/DISK-RULES.md` applies in full: `df -h` first, keep 10 GB
free, pull in passes, **extract → convert → delete the paks**. The full T7
depot is ~47 GB — it does NOT fit this VM alongside everything else, which is
why the pull runs user-side and only selected paks/extracts come back.

## 6. Sources (all public, no auth)

- steamdb.info — AppID 389730, depot 389731 (base + Originals/Ultimate/Definitive packages)
- CDDTreborn/Tekken7_PC-Modding-Guides wiki — no-encryption status, asset paths, character codes, umodel setup
- trumank/repak — unpack/list CLI (`repak list`, `repak unpack`, `--aes-key`)
- gildor.org umodel — batch export CLI (`-path -game -export -out`)
- h4lfheart/UEFormat — Blender import of PSK/UEModel/UEAnim
- FabianFG/CUE4Parse — scripted cross-platform asset reads
