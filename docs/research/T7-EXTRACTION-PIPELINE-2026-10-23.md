# T7 Extraction Pipeline — TRACK 1 (2026-10-23)

End-to-end pipeline: Tekken 7 (Steam, AppID 389730, account vil3m — user owns it;
game-ownership rule = authorization) → extracted assets → game-ready files in
`game/assets/`. Companion to `docs/research/T7-STEAM-PREP-2026-10-23.md` (depot
pull, pak layout, AES findings) — this doc starts where that one ends: the
paks are on disk, now extract.

Runner: `tools/t7-extract/run_pipeline.py` (wrapper). Validator:
`tools/t7-extract/validate.py`.

Status legend used throughout:
- **[WIRED]** — done in this PR: tool vendored, script written, validated without game files.
- **[AWAITS FILE PULL]** — needs the real T7 install on the credentialed machine
  (Grok's, Steam-logged-in). Nothing here is faked: no T7 files exist on this VM.

## 0. Tool inventory [WIRED]

All vendored (shallow clones, 2026-10-23) at `~/workspace/tools/t7-pipeline/`.
Large tools stay OUT of the game repo per repo rules.

| Tool | Repo | Vendored SHA (date) | License (transparency; firewall OFF per user override 2026-10-23) |
|---|---|---|---|
| TKMovesets2 (moveset/animation extractor — live tool) | github.com/Kiloutre/TKMovesets | a1b1917a (2023-08-12) | **GPL-3.0** (LICENSE.txt) |
| TekkenMovesetExtractor (legacy, obsolete) | github.com/Kiloutre/TekkenMovesetExtractor | ddd676a5 (2023-06-30) | **GPL-3.0** (LICENSE). README: "THIS PROJECT IS OBSOLETE — use TKMovesets" |
| UEViewer / umodel (uasset viewer+exporter) | github.com/gildor2/UEViewer | a0bfb468 (2024-02-23) | **MIT** (LICENSE.txt) |
| BlenderTekkenAnimationImporter (Blender addon, .bin anims) | github.com/Kiloutre/BlenderTekkenAnimationImporter | a5a2b8e3 (2023-04-15) | No license file (all rights reserved by default) |
| Tekken-7-Extracting-Packing-Tools (QuickBMS scripts) | github.com/a5tronomy/Tekken-7-Extracting-Packing-Tools | 46849c47 (2024-03-09) | No license file; bundles QuickBMS by Luigi Auriemma (freeware, own license) |

Copyleft note: TKMovesets/TekkenMovesetExtractor are GPL-3.0. They are used as
**external pipeline tools** (run on the extraction machine, never linked into
the game); their outputs (extracted animation/moveset data) are game data, not
derived code. Flagged here for transparency per the user's license-firewall
override — it does not block the pipeline.

Prebuilt binaries (fetch at pull time, not vendored): umodel from
gildor.org/en/projects/umodel#files; repak already vendored at
`~/workspace/tools/t8extract/repak`; TKMovesets2.exe from
github.com/Kiloutre/TKMovesets/releases; QuickBMS ships inside the a5tronomy
`Required/` folder.

## 1. Stage 0 — Locate the T7 install [AWAITS FILE PULL]

Input: `--t7-dir` — the Steam install root, e.g.
`C:\Program Files (x86)\Steam\steamapps\common\TEKKEN 7`.
The wrapper verifies these paths exist before doing anything:

- `TekkenGame/Content/Paks/*.pak` — the archives (numbered chunk paks + DLC paks)
- `TekkenGame/Binaries/Win64/TekkenGame-Win64-Shipping.exe` — needed for Stage 2
  (TKMovesets injects into the RUNNING game)

## 2. Stage 1 — Unpack .pak archives (no game running needed)

T7 paks are NOT pak-level encrypted (CDDTreborn wiki: "Tekken 7 has no game
encryption"). Per-file AES only for Geese/Noctis DLC (out of scope). Three
equivalent unpack paths — use repak first, umodel for selective export,
QuickBMS scripts as the Windows-GUI fallback.

### 2a. repak (primary, scriptable) [WIRED — command verified from project README]

```bat
repak.exe unpack --output "<OUT>\paks_unpacked" "C:\...\TEKKEN 7\TekkenGame\Content\Paks\*.pak"
repak.exe list "<pak>" > pak_filelist.txt
```

Output: raw UE4 file tree rooted at `TekkenGame/Content/`. No `--aes-key` for T7.

### 2b. umodel batch export (selective, converts on export) [WIRED]

Community-verified GUI path (CDDTreborn wiki): open umodel in the Paks folder →
tick "Override game detection" → engine "Unreal Engine 4" → game "Tekken 7" →
export. Headless batch form (per UEViewer Docs/FAQ.md):

```bat
umodel.exe -export -path="C:\...\TEKKEN 7\TekkenGame\Content\Paks" -out="<OUT>\umodel_out" -game=ue4 *.uasset
```

Confirm the exact `-game` override tag via `umodel -help` at pull time (GUI
selection is UE4 + "Tekken 7"; CLI tag name is the one unverified detail).
umodel exports: skeletal/static meshes → `.psk/.pskx`, animations → `.psa`,
textures → `.tga`, with materials.

### 2c. a5tronomy QuickBMS scripts (Windows fallback) [WIRED]

Vendored batch files under `Tekken-7-Extracting-Packing-Tools/`:
`Extract/Extract Everything.bat`, `Extract/Extract Character Assets.bat`,
`Extract/Extract Stage Assets.bat`, `Extract/Extract Sound Assets.bat`,
`Extract/Extract UI Assets.bat`, `Extract/Extract 'tkdata.bin'.bat`.
Requires `Generate Config.bat` once (writes `Required/tools.config` with the
T7 paths). The bundled `Required/Decrypt.bms` carries the per-file AES key
`=d6nw6YY6E#tI=6li6pI5CVaBC@fy%vR` used for encrypted entries; `tk7.bms` is
the UE4 pak parser.

## 3. Stage 2 — Moveset + animation-binary extraction (GAME MUST BE RUNNING)

This is the only stage that needs T7 actually launched. **TKMovesets2** is the
live tool (the old TekkenMovesetExtractor is obsolete — kept vendored only for
its `motbinExport.py` reference implementation).

### 3a. TKMovesets2 moveset extraction [AWAITS FILE PULL]

1. Build (once, on the extraction machine): Windows + Visual Studio + vcpkg
   (`vcpkg install`, triplet `x64-windows`) + Steamworks SDK headers in a
   `steamapi sdk` folder at repo root (see vendored README "Developer readme").
   Or take `TKMovesets2.exe` from the releases page.
2. Launch T7, load the character (practice or versus — any mode that loads the
   fighter), then in TKMovesets2: Extractor → select player → Extract.
3. Output per character: compressed `.tkmoveset` file in `extracted_chars/`
   (default folder). One file carries the full moveset: move list, frame data,
   hitboxes, requirements, plus camera / face / hand animations when toggled
   in the extractor options.
4. Supported sources: T7, Tag2, T6, T5, T5DR, T4, Revolution (extraction);
   T7 only for re-import.

### 3b. Raw animation .bin extraction (feeds the Blender addon) [AWAITS FILE PULL]

Two paths to the `.bin` files that `BlenderTekkenAnimationImporter` consumes
(`filename_ext = ".bin"`, little-endian `0xC8`/`0x17` animation blocks):

- Legacy: `motbinExport.py` from the vendored TekkenMovesetExtractor
  (needs Python 3.6.5 + pywin32, game running) — exports `mota_*.bin` per
  character from `extracted_chars/`.
- Modern: TKMovesets2 `Utils/Animations*.cpp` extraction path (same data,
  current addresses).

## 4. Stage 3 — Animations into Blender [WIRED — addon vendored, flow documented]

`BlenderTekkenAnimationImporter` (Blender 2.80+, install the folder as an
addon zip named exactly `BlenderTekkenAnimationImporter.zip`):

1. Load the Koenji T7 mannequin armature (bones the importer keys:
   `Armature` → `BASE`, `BODY_SCALE__group`, `Spine1`, `Hip`, `Neck`, `Head`,
   `R/L_Shoulder`, `R/L_Arm`, `R/L_ForeArm`, `R/L_Hand`, …).
2. File → Import → Tekken7 Animation → pick the `.bin` → keyframes are baked
   per frame (`scene.frame_end = len(frames)`).
3. File → Export → Export Tekken7 Animation (round-trip), or bake/export to
   glTF for the game.

Note: the addon authors state only *some* T7 animations are compatible —
expect per-character triage at pull time. `.psa` files from umodel import via
the existing UEFormat/Blender path (`tools/depot-pull/FMODEL.md`).

## 5. Stage 4 — Convert to game-ready formats [WIRED — mapping; converters run at pull time]

In-game asset roots (verified against main):

| T7 source (post-unpack path) | Converter | Game destination |
|---|---|---|
| `Game/Character/Items/Mesh/<CODE>/` `SK_*` skeletal meshes (+`SKT_` skeleton) | umodel → `.psk` → Blender → glTF/`.glb` | `game/assets/models/` |
| `.tkmoveset` per character (Stage 2) | `tkmoveset→json` converter (struct layout in `TKMovesets2/GameSpecific`; implement at pull time against real files) → game moveset schema | `game/assets/movesets/<fighter>.json` |
| `.bin` anims / `.psa` (Stages 2–3) | Blender bake → game anim format | `game/assets/anim/` |
| `Game/Content/WwiseAudio/Windows/*.wem` | wwiseutil/vgmstream decode → `.ogg/.wav` | `game/assets/sounds/` (sfx), `game/assets/voices/` (VO), `game/assets/music/` (bgm) |
| `Game/Content/UI_common/Texture2D/ReplaceImages`, `CS_*` select art | umodel texture export → `.png` | `game/assets/ui/`, `game/assets/portraits/` |
| `Game/Content/Maps/stgXX_geom.umap`, `Game/Content/Stage/stgXX` meshes | umodel export → Blender cleanup → glTF | `game/assets/stages/` |
| `T_*` textures (`_D/_N/_M/_R/_S/_E`) | umodel → `.tga/.png` | `game/assets/materials/` |

Character codes (from `T7-STEAM-PREP` §4): `Game/Character/Items/Mesh/<3-LETTER-CODE>/`
(e.g. LAW, LAR). Priority lanes: Law → Buffalo Bill, Lars → Chordz (per
`tools/depot-pull/t7-law-lars.txt`). Animation-asset in-pak paths and the
Julia/Zafina code gaps are flagged "confirm in umodel at pull time" in the
prep doc — unchanged.

Target moveset JSON schema (must match existing files, e.g.
`game/assets/movesets/buffalo-bill.json`):

```json
{
  "fighter": "<wh-fighter-id>",
  "display": "<DISPLAY NAME>",
  "tekken_base": "<Tekken fighter name>",
  "moves": {
    "<input>": {
      "name": "...", "input": "<input>", "startup": 0.3, "active": 0.017,
      "recovery": 0.567, "damage": 7, "limb": "armL", "heavy": false,
      "knock": 2.2, "soulGain": 8, "anim_ref": "t7:<code>:<move_id>",
      "input_slots": ["<input>"], "move_class": "strike"
    }
  }
}
```

`.tkmoveset` fields map: move display name → `name`, command list → `input` /
`input_slots`, startup/active/recovery frames → `startup`/`active`/`recovery`
(seconds at 60fps), damage → `damage`, hitbox data → `limb`/`knock`, animation
id → `anim_ref` (`t7:` prefix for new T7 pulls; existing files use `t3:`/`t7chicken:`/`t8:` refs).

## 6. Stage 5 — Validate [WIRED]

`tools/t7-extract/validate.py` runs WITHOUT game files:

- `--check-tools`: verifies each vendored tool dir exists and prints version/SHA.
- `--check-output <OUT>`: verifies the extracted tree
  (`paks_unpacked/`, `movesets/*.tkmoveset`, `anim_bin/*.bin`, `meshes/`,
  `textures/`, `audio/`, `ui/`, `stages/`) and validates every
  `game/assets/movesets/*.json` against the schema above (required keys per
  move; `anim_ref` prefix sanity).
- Exit non-zero with a file-by-file report on failure — CI-runnable.

## 7. What was NOT done here (honest gaps)

1. No T7 files were pulled (no Steam credentials on this VM) — every
   `[AWAITS FILE PULL]` step above is unexecuted by definition.
2. The `.tkmoveset`→`movesets/*.json` converter is specified, not implemented
   (needs real `.tkmoveset` binaries to test against).
3. The exact umodel CLI `-game` override tag for the Tekken 7 profile is
   unconfirmed (GUI path is community-verified).
4. Blender `.bin` compatibility is per-animation — triage at pull time.

## 8. Handoff to the credentialed machine

On Grok's Steam-logged-in machine, in order:

1. `python tools/t7-extract/run_pipeline.py --t7-dir "<T7>" --out "<OUT>" --check-only`
   (verifies tools + paths, no game launch).
2. Stage 1: `--stage unpack` (repak; no game needed).
3. Stage 2: launch T7, load Law/Lars, run TKMovesets2 extraction
   (`--stage movesets` prints the exact click-path; extraction itself is
   interactive by design — memory injection can't be headless).
4. Stage 3–4: Blender addon import/bake, umodel exports, conversions.
5. `python tools/t7-extract/validate.py --check-output "<OUT>"` — green before
   anything lands in `game/assets/`.
