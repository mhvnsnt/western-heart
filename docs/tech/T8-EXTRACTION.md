# Tekken 8 extraction — repeatable method + inventory (2026-10-23 CT)

Owner order (pt128u, 2026-10-23): pull everything possible from Tekken 8 (Alisa moves and stances, menus, select, files), T7 as fallback, and leave a method Muse / Claude / any agent can rerun **without Steam**.

## 0. Plain-language summary
Tekken 8 keeps all its art, animation and menus packed in big locked container files (`.utoc`/`.ucas`/`.pak`) inside the game's `Paks` folder. The method is:
1. Get that `Paks` folder onto the box once (copy from the owner's install). After that, Steam isn't needed.
2. Unlock and unpack it with **CUE4Parse** (the open-source engine behind FModel) using the game's AES key, which lives only in an environment variable and never in git.
3. Convert what comes out: animations to `.psa`, then GLB in Blender, then `tools/anim-retarget/retarget_rot.py` onto our rigs. Menus and textures go to PNG, and data tables go to JSON.
4. Land the results by PR with a source log, the same as every other teardown.

**Current state: step 1 has never happened.** No T8 or T7 game containers exist on the box, in the repos, or in the owner's Drive (Drive search "Tekken" finds only the T3 zip and the T6 teardown parts). So no T8 animation can be extracted yet. Everything below is ready to run the moment the `Paks` folder lands.

## 1. Where the files live
| What | Path | Status |
|---|---|---|
| T8 game containers | `<Steam>/steamapps/common/TEKKEN 8/Polaris/Content/Paks/` (`*.utoc`, `*.ucas`, `*.pak`, `global.utoc`) | **not on box.** Owner copies the folder (~100 GB) to the box or to agent storage (`/cursor/stores/...`) |
| Locator | `tools/extract/t8/locate_paks.sh [extra_roots]` | Done. Prints `T8_PAKS=<dir>` or exits 2 with the owner step. Run on 2026-10-23: exit 2 |
| Disk | Box has about 40–55 GB free. Extract with filters (below), not the whole game. Clear outputs once pushed (owner t126u) | |

## 2. Unpack (UE5 IoStore)
- **Tool: CUE4Parse** (Apache-2.0, github.com/FabianFG/CUE4Parse) through our headless exporter `tools/extract/t8/cue4-export/` (.NET 8). FModel is the same library with a Windows GUI, which suits a person but isn't scriptable here.
- **Alternatives:**
  - `retoc` (github.com/trumank/retoc) converts IoStore to legacy pak/zen for other tools.
  - `repak` handles legacy `.pak`.
  - UE Viewer (umodel) does **not** reliably read UE5 IoStore, so we don't use it for T8.
- **AES key:** T8 containers are encrypted. Put the key in the environment only: `export T8_AES_KEY=0x...`. Get it from the owner, or from the public community key lists that FModel users share for their own copies. **Never commit it, never write it to a repo file.** Gitleaks runs before every push.
- **Run:** `T8_AES_KEY=... tools/extract/t8/extract.sh "$T8_PAKS" /workspace/t8-out [filters...]`
  - With no filters, it pulls everything whose path contains `alisa`, `/UI/`, `Select`, `CharaSelect`, `Customize` or `Menu`.
  - It writes `MANIFEST.tsv` (every package with its type and exported file).
- **Status of `Program.cs`:** it's a scaffold that has never run against real T8 data. Expect small CUE4Parse API drift on the first run. Fix it, pin the package versions in the `.csproj`, and log what changed here.

## 3. Convert anims to our rigs
1. Exporter writes `AnimSequence` as `.psa` and the skeleton/mesh as `.psk` (ActorX).
2. `blender -b --python tools/extract/t8/psa_to_glb.py -- --psk X.psk --psa X.psa --out clips/` gives one GLB per clip. This needs the `io_scene_psk_psa` Blender add-on.
3. `tools/anim-retarget/retarget_rot.py --source clips/<move>.glb --target game/assets/models/cyborg-x.glb --bonemap tools/extract/t8/t8_to_wh.json --in-place --anim-only --out game/assets/anim/t8/alisa/<move>.glb`
   - `retarget_rot.py` is a rotation-only, scale-safe world-delta retarget, proven on CMU onto cyborg-x and pantera (see `anims/show/README.md`).
   - `t8_to_wh.json` is an **unverified template** with UE mannequin names. Check it against the first exported bone list.
4. Bind each move: `game/data/cape-alisa-binding.json` → `moves[].anim_source` (now `PENDING-T8-PAKS`) = the clip path. Then drop the `cyborgx: 'gunjack'` T3 fallback in `game/js/fighter.js` and close the `t3_last_resort_log` entry.

## 4. What T8 data exists today (inventory)
| Item | Where | Integrated? |
|---|---|---|
| Alisa T8 frame data, 188 moves (wavu.wiki, CC0) | `docs/t7t8-reference/frame-data-t8-full/alisa.json` | Yes. `game/data/cape-alisa-binding.json` (#814) |
| T8 frame data, all 41 files | `docs/t7t8-reference/frame-data-t8-full/` | Reference. Moveset lanes use it |
| T8 fan model archives (Asuka SFM, Yoshimitsu "Phantom") | `teardown/tekken8/models/` | Asuka → `kinpo-t8.glb` (pull-rest batch 3); Phantom → `phantom-t8` |
| Tekken 7 Alisa model (SFM port; armature `T7\Alisa_ARM`, 160 joints) | `game/assets/models/cyborg-x.glb` | **Yes, now Cape Jones's first-attire rig** (this PR) |
| T8 menus, select, customization UI | — | **Not on box.** Needs Paks (§2 filter `/UI/`) |
| T8 animations (any character) | — | **Not on box.** Needs Paks |
| T7 containers | — | Not on box (`teardown/TEKKEN78-ACQUISITION-PLAN.md`, never fulfilled) |

## 5. Still left to pull (once Paks exist)
1. Alisa: every move and stance, plus walk/run/sidestep/crouch/jump/backdash, hit reactions and intros/wins.
2. Select-screen layout, fonts and UI textures (→ `ui_sources` gate citations for the menu lane).
3. Customization item tables and the attire system (→ attire ladder).
4. The rest of the cast's movesets, to replace the remaining T3 banks (no-T3 law t121u).
5. Stages and voice/SFX banks (Wwise `.bnk`/`.wem` → vgmstream).
