# Tekken 7 Steam extraction log

Source: owner's own Steam purchase of TEKKEN 7 (app 389730, main depot 389731, manifest 1653672533371481747 dated 2023-02-14). Downloaded with DepotDownloader v3.4.0 using `-filelist`, one file at a time. Steam credentials and token files are never committed.

## Tools (all public)
- DepotDownloader v3.4.0: github.com/SteamRE/DepotDownloader
- repak: github.com/trumank/repak. T7 paks are UE4 pak V3 with an unencrypted index.
- Pak key, public from the community (TekkenMods docs, credit Gneiss): `0x3d64366e7736595936452374493d366c69367049354356614243406679257652`. Assets are encrypted one by one. To decrypt, run AES-256-ECB **encrypt** with this key over the full 16-byte blocks; the result starts with `C1832A9E`. Script: `tools/extract/t7/t7_decrypt.py`.
- UModel (UEViewer), built from source on Linux, run with `-game=tekken7`. It exports glTF with `-notex`, because MaterialInstance assets crash it. Textures are exported as TGA.
- `tools/extract/t7/convert.py` converts glTF to glb (pygltflib), character TGAs to WebP q90, and UI TGAs to PNG.
- Reference only: a5tronomy/Tekken-7-Extracting-Packing-Tools (QuickBMS scripts; `tkdata.bms` holds the tkdata.bin key).
- To re-run: `tools/extract/t7/extract_pak.sh <pak> <workdir> <dest>`

## Extracted so far
### pakchunk0-WindowsNoEditor.pak (20.1 GB raw, deleted after extraction)
Output: `teardown/tekken7-steam/pakchunk0/`. `manifest.json` lists every file and its joint count.
Output (PRIVATE repo mhvnsnt/game-reverse-engineering, PR #51): `teardown/tekken7-steam/pakchunk0/`. `manifest.json` lists every file and its joint count.
- 200 skeletal meshes as glb: base 1P costume (face, hair, upper, lower) for 38 codes, including **asa (Alisa → Cape/Cyborg-X), lee (Lee → Purple Rain), bob (Bob → Burger)**, plus kin, yos, xia, jin, bry, hei, jac, lar, hwo, nin, edd, ask, mig, mrx, ltn, lil, kaz and others.
- Rig: the T7 skeleton `SKT_CH_base_Skeleton` has about 207–233 joints per mesh. That is far more than 52, so under the "most bones" rule it becomes the preferred rig.
- 622 textures: character textures plus the UI flash textures for CharacterSelect, StageSelect, HUD_Gauge, Makuai, Title, MainMenu and Result.
- 15 meshes failed in UModel (kaz hair/body variants, arb head items, the drop items).

### Content/Binary/tkdata.bin (305 MB raw, deleted after extraction)
- Unpacked with `tools/extract/t7/t7_tkdata.py`, a Python port of the community `tkdata.bms` v0.2.1. It uses the tkdata AES key published in that public script. The archive holds 1087 files.
- Output: `teardown/tekken7-steam/tkdata/`
- Output (PRIVATE repo mhvnsnt/game-reverse-engineering, PR #51): `teardown/tekken7-steam/tkdata/`
  - `mothead/bin/<code>mot.bin`: **full movesets for every T7 character, DLC included** (moves, cancels, hit and frame data, throws). Examples: `asamot.bin` (Alisa → Cape), `leemot.bin` (Lee → Purple Rain), `bobmot.bin` (Bob → Burger).
  - `mothead/movelist`, `mothead/nua`, `mothead/mask`: command lists and related data.
  - `list/`: character list, character_panel_list (select-screen layout), customization tables, stage and area structs.
  - `dictionary/`: text tables.
  - Subtitles were skipped.
- The motbin layout matches what the TKMovesets/T7 moveset tools parse. Converting it to the repo's moveset JSON is the next step.

## Not yet extracted (next PAKs)
- `pakchunk0_P` (4.5 GB), `pakchunk1` (15.9 GB), `pakchunk1_P` (18.2 GB): remaining characters (DLC), stages and patches.
- `Content/Binary/tkdata.bin` (305 MB, loose): motion and moveset data. It needs a Python port of `tkdata.bms`, which uses a separate key.
- Animations, frame data, collision and camera are not UE assets in T7. They live in tkdata.bin and the motbin data, so they're still pending.

## Where the assets live
western-heart is public, so the T7 assets are kept only in the private repo `mhvnsnt/game-reverse-engineering` (PR #51). This repo keeps just the tools and docs. Private builds load the assets through the `__WH_PRIVATE_ASSETS` hook pattern (#855). Draft PR #863 is the abandoned public copy and must not be merged.
