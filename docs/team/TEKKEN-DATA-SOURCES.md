# Tekken data sources — how any agent pulls it (Claude, Muse, Jules, Grok)

*2026-10-23 (CT). Owner order pt166u: "let all the other agents know where you're getting the Tekken 8 [files] from like a full move sets and everything so they can also go there and use that way to get stuff."*

Facts below were checked against `main` and the open PR branches #849 (T8 tools) and #858 (T7 Steam prep) on 2026-10-23. Anything not verified is marked **UNVERIFIED**. Full source log: `docs/tech/COMMUNITY-SOURCES.md`. Lane notes: `teardown/community/HANDOFF.md`.

## 0. Rules (read first)
1. **T8 first, T7 as backup, T3 only as a last resort.** Every T3 use gets logged (`t3_last_resort_log`, see `docs/tech/T8-EXTRACTION.md` §3 on PR #849).
2. **No hand-made content.** Teardown/source data only. Menus must pass the `ui_sources` gate (#834).
3. **Log every source.** Add a row to `docs/tech/COMMUNITY-SOURCES.md` (URL, author, license, pinned commit) and drop a `SOURCE_COMMIT.txt` next to pulled files.
4. **Private use only.** Kaiutzi21 data is CC BY-NC 4.0 and rbnTekkenFrameData has no license. Keep it in the private repos and never ship it in a commercial build.
5. **No pirated game copies.** Allowed: public community/mod files, plus the owner's own Steam purchases.
6. **Never commit credentials** (Steam login, AES keys, API tokens). Run `gitleaks` before every push.
7. **Disk is tight.** Use sparse checkouts and pull one file at a time. Delete raw files after the converted output is pushed, and only through the safe-delete script.

## 1. Tekken 8 full movesets — Kaiutzi21/Tekken8Movesets
- Repo: https://github.com/Kaiutzi21/Tekken8Movesets (default branch `main`, CC BY-NC 4.0, credit Kaiutzi21).
- Format: TekkenMovesetExtractor export (https://github.com/Kiloutre/TekkenMovesetExtractor). JSON containing moves, cancels, hit conditions, pushbacks, throws, input sequences and voiceclips. It holds move **logic** only, with **no animation curves**.
- Folders upstream (listed via the GitHub API on 2026-10-23): `t8_ARMOR_KING`, `t8_BYRON`, `t8_CLIVE_COOL`, `t8_FAHKURMUM`, `t8_HEIHACHI`, `t8_JINBOSLICE`, `t8_KING_DLC`, `t8_KING_v2`, `t8_LARPS`, `t8_LAW`, `t8_LEE_v2`, `t8_MIARY_ZO`, `t8_PAUL`, `t8_RAVEN_DLC`, `t8_SHAHEENIBRATATINI`, `t8_STEVE`, `t8_STEVE_v2`, `t8_UNKNOWN`, `t8_YOSHIMITSURUGI`. Folder names are the uploader's nicknames (BYRON = Bryan, LARPS = Lars, and so on). `_v2`/`_DLC` folders are edited movesets, so read each folder's `Documentary.md`.
- **Already in our repo** at `teardown/community/tekken8/movesets/kaiutzi21/` (pinned upstream commit `1535cf5121aa462b1c1fd7a016eb49c19d4f3d4d`): `t8_LEE_v2` (Purple Rain), `t8_KING_v2`, `t8_ARMOR_KING`, `t8_LAW` (Buffalo Bill), `t8_PAUL`. Each has `<name>.json.gz` plus `<name>.summary.json`.
- **Not in T8 at all:** Bob (Burger) and Alisa (Cape Jones). Use the T7 frame data in §2 for them.

Fetch more without cloning the whole repo:
```bash
git clone --depth 1 --filter=blob:none --sparse https://github.com/Kaiutzi21/Tekken8Movesets /tmp/k21
cd /tmp/k21 && git sparse-checkout set t8_HEIHACHI t8_STEVE_v2   # folders you need
git rev-parse HEAD                                                # -> SOURCE_COMMIT.txt
```
Land it in our layout (gzip the JSON and build the summary):
```bash
D=teardown/community/tekken8/movesets/kaiutzi21/t8_HEIHACHI; mkdir -p "$D"
cp /tmp/k21/t8_HEIHACHI/*.md "$D"/ 2>/dev/null || true
for j in /tmp/k21/t8_HEIHACHI/*.json; do gzip -c "$j" > "$D/$(basename "$j").gz"; \
  python3 teardown/community/tekken8/movesets/kaiutzi21/summarize.py "$D/$(basename "$j").gz" "$D/$(basename "$j" .json).summary.json"; done
```
`summarize.py <in.json[.gz]> <out.summary.json>` writes a compact per-move table (name, anim_name, hitlevel, active frames, airborne window, transition, cancel_idx, hit_condition_idx, hitbox_location) plus list counts and the throw count. **UNVERIFIED:** the exact JSON file name inside each upstream folder; check with `ls` before running.

Decoding help: Kiloutre/TekkenMovesetExtractor (GPL-3.0, maps `anim_key` to animation data) and AliK3112/tekken-8-movesets-scripts.

## 2. Tekken 7 frame data — pbruvoll/rbnTekkenFrameData
- Repo: https://github.com/pbruvoll/rbnTekkenFrameData (top level `frameData/`, `metaData/`, `README.md`). It has no license, so treat it as all rights reserved and use it as a private reference only.
- **Already in our repo** at `teardown/community/tekken7/framedata/rbnorway/csv/<Character>/` (`-basic`, `-special`, `-gifs` CSVs) for every T7 fighter, including `Bob`, `Alisa`, `Lee`, `Law`, `King`. Pinned commit: `teardown/community/tekken7/framedata/rbnorway/SOURCE_COMMIT.txt` (`c5677a82978868aea0a0ccee1c8993b61e901f28`).
- Refresh:
```bash
git clone --depth 1 --filter=blob:none --sparse https://github.com/pbruvoll/rbnTekkenFrameData /tmp/rbn
cd /tmp/rbn && git sparse-checkout set frameData && git rev-parse HEAD
```
- Also in repo: T8 frame data from wavu.wiki (CC0) at `docs/t7t8-reference/frame-data-t8-full/` (41 files, including `alisa.json`).

## 3. Tekken 7 game files — owner's Steam account
- Owner bought Tekken 7 on Steam (account `vil3m`). App **389730**, Windows content depot **389731** (one depot holds all of T7). The depot manifest lists 577 files and about 87 GB on disk. The paks are `TekkenGame/Content/Paks/pakchunk{0,1}-WindowsNoEditor{,_P}.pak` (4–20 GB each) plus small chunks.
- Tool: DepotDownloader v3.4.0 (https://github.com/SteamRE/DepotDownloader).
- **Grok's box:** installed at `/workspace/tools/depotdl/`, and the Steam login token is already saved there (`-remember-password`), so no password is needed again. Agents on Grok's box run:
```bash
cd /workspace/tools/depotdl
echo 'regex:TekkenGame/Content/Paks/pakchunk1-WindowsNoEditor_P\.pak' > /tmp/one.txt   # ONE file at a time
./DepotDownloader -app 389730 -depot 389731 -username vil3m -remember-password -filelist /tmp/one.txt -dir /workspace/t7raw
```
  List the files without downloading: `./DepotDownloader -app 389730 -depot 389731 -username vil3m -remember-password -manifest-only -dir /tmp/t7man`. A saved copy is at `/workspace/tools/depotdl/manifest/manifest_389731_*.txt`.
- **Other machines (Muse, Claude):** need their own Steam login. The owner signs in there himself (password plus Steam Guard code from his Gmail). Never copy Grok's token, never ask for or store the password, and never commit anything from `~/.local/share/DepotDownloader` or the tool's `.DepotDownloader` folder. Owner-side Windows route: `tools/depot-pull/T7-USER-STEPS.md` (PR #858).
- **Chunked rule:** one pak per run. Unpack only what you need, push the converted output, then delete the pak (Steam can always redownload it).

Unpack and convert (see `teardown/tekken7/T7-STEAM-EXTRACTION.md` on PR #858):
1. `repak list <pak>` and `repak unpack <pak> ./t7unpacked/` (https://github.com/trumank/repak).
2. **Correction to PR #858:** its doc says T7 has no encryption. Grok's real run found **per-asset encryption** on `.uasset`/`.umap` files. Grok's box has a decrypter at `/workspace/tools/extract-t7/t7_decrypt.py` (it uses the public community key credited to Gneiss; `python3 t7_decrypt.py <unpacked_dir>`) and a converter at `/workspace/tools/extract-t7/convert.py`. Neither is in the repo yet, so **UNVERIFIED** for other machines.
3. Paths: meshes `Game/Character/Items/Mesh/<CODE>/`, select art `UI_common/Texture2D/ReplaceImages` (`CS_*`), stages `Maps/stgXX_geom.umap`, audio `WwiseAudio/Windows/`. **UNVERIFIED:** where the animation assets live, and the Julia/Zafina codes.
4. Export: umodel (`-game=tekken7`, Windows/Wine), FModel, or CUE4Parse. Then Blender (UEFormat / `io_scene_psk_psa`) to GLB, then `tools/anim-retarget/retarget_rot.py` onto the 52-bone rig.

**Tekken 8 paks** (not owned on Steam yet): `tools/extract/t8/` on PR #849, with `locate_paks.sh`, `extract.sh` (CUE4Parse, needs `T8_AES_KEY` set in the environment only), `psa_to_glb.py` and `t8_to_wh.json` (an **unverified** bone map). Runbook: `docs/tech/T8-EXTRACTION.md` (PR #849).

## 4. HUD, announcer, artwork — Spriters Resource / Sounds Resource
These sites use Cloudflare, which blocks curl and scripts with a 403. **Use a browser** and download the ZIP by hand.
- T7 HUD (236 PNG): https://www.spriters-resource.com/arcade/tekken7/asset/561802/
- T7 announcer (94 WAV): https://sounds.spriters-resource.com/arcade/tekken7/asset/561714/
- T7 PC sound sets: https://sounds.spriters-resource.com/pc_computer/tekken7/
- T8 artwork, rank icons and select renders: https://www.spriters-resource.com/pc_computer/tekken8/
Land them under `teardown/community/tekken7/` or `teardown/community/tekken8/` and mark the row **Pulled** in `COMMUNITY-SOURCES.md`.

## 5. Checklist before you push
- [ ] Source row and `SOURCE_COMMIT.txt` added
- [ ] `gitleaks detect --no-git --source .` is clean
- [ ] Feature branch and PR with the instruction-gate template; no force-push
- [ ] Raw game files deleted only after the converted output is on GitHub
