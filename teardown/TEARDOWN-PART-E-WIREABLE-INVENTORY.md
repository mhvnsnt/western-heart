# Teardown Research, Part E — Full Wireable Inventory: teardown/ + game/data

**Repo:** `mhvnsnt/western-heart` (GitHub API name `Western-Heart`)
**Date:** 2026-11-07
**HEAD seen in API URLs:** `3334ebff92be68322e8e320b750252291c77d9d5`
**Method:** listed every folder in `teardown/` and `game/data/` through the GitHub connector (directory listings + file sizes), and read the key docs and the heads of the big JSONs. No game code was edited, nothing was pushed, no commercial game file, ISO, ROM, or code file was downloaded. File contents were read through the API only.
**Re-run note (2026-11-07, second pass):** the first attempt's directory listings hit GitHub's 1,000-entry cap on the two biggest folders, so its totals were floors. This pass re-counted with the recursive git-tree at HEAD `3334ebf` (paths + blob sizes, no file bytes) and spot-checked the gaps with direct directory listings. The recursive tree itself came back `truncated: true` at 60,859 entries and is MISSING whole subtrees that direct listings prove exist (`teardown/wwf-no-mercy/arenas/` 36 files, `models/` subdirs, `textures/` subdirs, `teardown/yakuza-kiwami/README.md`). So every total below is a floor, not a census: **≥38,811 files in `teardown/`** per the tree, plus the verified-missing subtrees. Where the tree and a direct listing disagree, the direct listing wins and the row says so.
**How to read this file:** one table per top folder. "Wire into" means the web build under `game/` — the only playable build. Origin flags: **JAY'S OWN** (Jay's own docs, code, JSONs, retarget maps), **COMMERCIAL-DERIVED** (material pulled out of a commercial game — needs a licence decision before use; inventory is NOT approval), **COMMUNITY-FREE** (CC0 / free-for-any-use community data), **UNKNOWN** (origin not stated in the file). Sizes are bytes from the repo listing. **UNMEASURED** means the folder was listed but its deeper contents were not opened, or the file was too big for the read tool to return.
**Gender rule used here:** Pantera is male (he/him). Every other fighter is named by name only, no guessed pronouns.

## Headline counts

- **Files listed:** **≥38,946 across `teardown/` + `game/data/`** — ≥38,811 in `teardown/` (4.05 GB, recursive git-tree floor — the tree was truncated and misses whole subtrees, see Method) + 135 in `game/data/` (15.4 MB). The first attempt's 3,756 was the 1,000-entry listing cap talking, not the repo.
- **Wireable into `game/`:** ~38,500 files (everything except the ~600 research/design `.md` docs, which are reference only, and ~40 unopened archives). "Wireable" means the file can be loaded or converted into the web build — it does NOT mean cleared to use.
- **Origin split (files, estimated from folder + source, not by opening all ~39,000):** JAY'S OWN ≈ 1,250 (teardown tools + docs ~1,164; `game/data/` own JSONs/JS ~85) · COMMERCIAL-DERIVED ≈ 37,500+ · COMMUNITY-FREE (CC0/CMU) 2 files + free sources catalogued in docs · UNKNOWN ≈ 120 files (mostly unopened `.rar` / `.7z` / `.zip` archives) plus the subtrees the truncated tree missed.
- **Biggest single groups:** Tekken 3 TIM textures (8,556 TIM + 8,559 PNG, 17,116 files) · Urban Reign audio (1,034 files) + ADX music (1,133 files) · Tekken 3 movesets (3,247 moves, ~28 MB JSON) · Tekken 6 NDPP model parts (3,444 GLBs in `models/parts/`) · WWF No Mercy arenas (17 arenas, OBJ+VC) + animation bank (436 decoded `.npy` clips) · Soulcalibur II models + stages (66 GLBs + 41 stage GLBs, ~150 MB + 165 MB).
- **Devil Within: found, but only located, not decoded.** See the Devil Within box below. No Devil Within animation file exists as a separate file in the repo — the files are named inside a Tekken 5 disc archive manifest only.

## Licence warning — read this first

This repo is public and it holds extracted commercial-game material, against its own `AGENTS.md` rule (no copyrighted/leaked game files in public repos). Every row flagged COMMERCIAL-DERIVED below is inventoried only. Nothing flagged that way is cleared for copying into any build, public or private, until Jay makes the licence call. Jay's own position (use the actual files, chimera build of mods) is recorded as his, not adopted here. The Tekken 7 frame data also carries its own warning in its README: TheBigTuna's repo has no licence file and TekkenDocs data has no redistribution licence stated — author check needed before verbatim redistribution.

## Devil Within — decoded data hunt (Tekken 5)

| Exact repo path | What it is | Size | Game | What it could wire into | Origin |
|---|---|---|---|---|---|
| `teardown/tekken5/DEVIL-WITHIN-DATA.md` | Own doc: file-level grounding for Devil Within — which disc files hold DW anims, stages, bosses, meter | 3,571 | Tekken 5 (PS2) | HeartMind story mode design + RE bench work list | JAY'S OWN |
| `teardown/tekken5/INVENTORY.md` | Own doc: full T5 ISO survey (10 disc files, sizes, md5) | 2,468 | Tekken 5 (PS2) | Same as above | JAY'S OWN |
| `teardown/tekken5/t5_motion_manifest.txt` | Manifest: 498 `.dat` motion filenames from `TK5DATA2.BIN` (romD archive) | 10,239 | Tekken 5 (PS2) | Move/animation index for the RE bench; names only, no motion bytes in the repo | COMMERCIAL-DERIVED |
| `teardown/tekken5/t5_char_codes.txt` | 109 character codes with file counts | 841 | Tekken 5 (PS2) | Character-code lookup for the manifest | COMMERCIAL-DERIVED |

**Devil Within files located (named in the manifest, NOT decoded, NOT separate files in the repo):** `gym_dw_nog00.dat`, `gym_dw_raribxk.dat`, `gym_dw_rarixk.dat` (enemy/boss anims), `gym_djin_newhane00.dat` … `newhane03.dat` (Devil Jin transformation, wings/feathers), `dwfkao00.dat`, `dwhadoh00.dat`, `dwup00.dat` (+ `dwup_hei.dat`), stage files `stg00.dat`, `stg01.dat`, `stg02.dat`, `stg04.dat`, `moj_stg02.dat` (stage text), character sound `c30dvj.dat` (Devil Jin), `c10jin.dat`, `c15hei.dat`, `c21jac.dat`. All of these live inside `TK5DATA2.BIN` (244 MB romD archive on the T5 disc). **Status per DEVIL-WITHIN-DATA.md (2026-10-23):** animation files LOCATED. DW stage geometry, boss AI/data (Modified Gun Jack, Heihachi clones, True Ogre, Soul Sphere, Monstrous Ogre), enemy data, Devil Gene meter mechanics, and DW UI/menus are in the binary `TK5DATA0.BIN` (2.07 GB) / `TK5DATA3.BIN` (423 MB) formats — mapped for the RE bench, not yet extracted. The design research doc lives outside the repo (`~/workspace/devil-within-teardown.md`, 2026-10-22) and was not part of this inventory. **Wire into:** HeartMind mode (Jin's DW brawler moveset, Devil Gene meter + Devil Jin transformation, 5 stage layouts, boss patterns, ranking thresholds) — only after the romD format is decoded; today it wires in as a spec, not as data.

---

## 1. teardown/ — root docs

| Exact repo path | What it is | Size | Game | What it could wire into | Origin |
|---|---|---|---|---|---|
| `teardown/README.md` | Own readme: the 5-game chimera table + what is excluded and why | 2,492 | — | Orientation | JAY'S OWN |
| `teardown/PLAYBOOK.md` | Own reverse-engineering playbook (how teardowns are done here) | 4,662 | — | RE bench method | JAY'S OWN |
| `teardown/RE-TOOLCHAIN.md` | Own RE toolchain doc | 3,701 | — | RE bench method | JAY'S OWN |
| `teardown/TEARDOWN.md` | Own best-of summary: No Mercy + WMXIX measured findings (wrestler ID table, move tables, AKI anim format, YOBJ/YANM skeleton) | 12,113 | WWF No Mercy / WMXIX | Wrestling systems, CAW, retarget maps | JAY'S OWN |
| `teardown/TEARDOWN-STATUS.md` | Own scoreboard, 14 games, % complete + blockers (updated 2026-10-23) | 6,565 | All | Planning | JAY'S OWN |
| `teardown/TEARDOWN-COVERAGE-MATRIX.md` | Own coverage matrix per game × models/anims/movesets/stages/audio/UI (2026-10-22) | 5,672 | All | Planning | JAY'S OWN |
| `teardown/TEARDOWN-SOURCES.md` | Excluded-binaries list with sizes + SHA-256 (raw discs stay local) | 3,546 | All | Re-acquisition | JAY'S OWN |
| `teardown/western-heart-asset-catalog.md` | Own catalog of free/open assets: Quaternius CC0, Mixamo, CMU mocap, Sketchfab CC-BY stages | 16,336 | — | Free models/anims/stages (licence per entry, re-verify before shipping) | JAY'S OWN |
| `teardown/ARCHIVE-ORG-CATALOG-2026-11-06.md` | Own archive.org catalog | 24,182 | — | Sourcing | JAY'S OWN |
| `teardown/ARENA-INVENTORY.md` | Own arena inventory | 2,512 | — | Stage wiring | JAY'S OWN |
| `teardown/ARENA-PULL-REPORT.md` | Own arena pull report | 4,087 | — | Stage wiring | JAY'S OWN |
| `teardown/TEKKEN-ARENA-STATUS.md` | Own Tekken arena status | 871 | Tekken | Stage wiring | JAY'S OWN |
| `teardown/TEKKEN-CUSTOMIZATION-EXTRACTION-REPORT.md` | Own Tekken customization extraction report | 15,732 | Tekken 6 / TTT2 | Create Fighter / customization | JAY'S OWN |
| `teardown/tekken6-customization-research.md` | Own Tekken 6 customization research | 5,087 | Tekken 6 | Create Fighter | JAY'S OWN |
| `teardown/ttt2-customization-research.md` | Own TTT2 customization research | 5,088 | Tekken Tag 2 | Create Fighter | JAY'S OWN |
| `teardown/TEKKEN78-ACQUISITION-PLAN.md` | Own Tekken 7/8 acquisition plan | 1,436 | Tekken 7/8 | Sourcing | JAY'S OWN |
| `teardown/scvi-doa6-acquisition-2026-10-14.md` | Own SCVI/DOA6 acquisition note | 16,336 | Soulcalibur VI / DOA 6 | Sourcing | JAY'S OWN |
| `teardown/BASS-ARMSTRONG.md` | Own DOA4 Bass Armstrong notes | 1,349 | Dead or Alive 4 | DOA4 model work | JAY'S OWN |
| `teardown/FIGHT_CLUB_TEARDOWN.md` | Research doc from web sources (what Fight Club 2004 did wrong) — for AshLane/brawler design | 20,793 | Fight Club (2004) | Brawler design lessons (reference only) | JAY'S OWN |
| `teardown/WARRIORS_TEARDOWN.md` | Research doc from walkthroughs/reviews (gang combat at scale, 9v9 War Party) | 32,861 | The Warriors (2005) | Gang/team combat design (reference only) | JAY'S OWN |
| `teardown/YAKUZA_TEARDOWN.md` | Research doc (heat-action finishers, style switching) | 38,411 | Yakuza series | Brawler finishers / style switching (reference only) | JAY'S OWN |
| `teardown/SLEEPING_DOGS_TEARDOWN.md` | Research doc (environmental combat, intimidation) | 21,994 | Sleeping Dogs (2012) | Brawler design (reference only) | JAY'S OWN |
| `teardown/SA_TURF_WAR_TEARDOWN.md` | Research doc (GTA San Andreas turf-war system) | 13,777 | GTA San Andreas | Territory layer design (reference only) | JAY'S OWN |

## 2. teardown/tekken3/ — Tekken 3 (PS1), teardown claimed 100%

| Exact repo path | What it is | Size | Game | What it could wire into | Origin |
|---|---|---|---|---|---|
| `teardown/tekken3/animations/divmot00_paul.bin` … `divmot20_forestlaw.bin` (21 files) | Motion bank per fighter (Paul, Law, Lei, King, Yoshimitsu, Nina, Hwoarang, Xiaoyu, Eddy, Jin, Julia, Kuma, Bryan, Heihachi, Ogre, Gun Jack, Anna, Bosconovitch, Gon, Forest Law) + `divmot99_common.bin` | ~107–404 KB each, ~6.6 MB total | Tekken 3 | `game/js/t3anims.js` retarget (already the pattern); idle/walk/attack banks per fighter | COMMERCIAL-DERIVED |
| `teardown/tekken3/movesets/moveset_<fighter>.json` (21 files) | Move table per fighter, 3,247 moves claimed in total | 391 KB–3.41 MB each, ~28 MB total; biggest: `moveset_king.json` 3,409,137 | Tekken 3 | `game/assets/movesets/` + lab move table; frame/damage/anim rows per move | COMMERCIAL-DERIVED |
| `teardown/tekken3/movesets/moveset_<fighter>.csv` (21 files) | Same move tables as CSV | 30–102 KB each | Tekken 3 | Same as above, spreadsheet-readable | COMMERCIAL-DERIVED |
| `teardown/tekken3/movesets/MOVESET-SUMMARY.md` | Own moveset summary | 1,971 | Tekken 3 | Reference | JAY'S OWN |
| `teardown/tekken3/models/<fighter>/` (15 dirs: anna, bosconovitch, bryan183, eddy, gunjack215, heihachi191, hwoarang, jin151, julia, king95, lei, nina, paul, xiaoyu127, yoshimitsu103) | Rigid-part character models: `.kmd` + `_parts.obj` + montage PNG + `renderdata.pkl` per fighter (pattern verified on king95 + jin151; other 13 dirs UNMEASURED deep) | Per-fighter set, sizes not all listed | Tekken 3 | Retro alt-costume models (T3 = alt attire per TEARDOWN.md); rigid parts, NO skinning — needs the rigid-part rig method | COMMERCIAL-DERIVED |
| `teardown/tekken3/models/king95/king95_stance0_pose.json`, `king95_stance2_pose.json` | Sampled King stance poses | (in king95 dir) | Tekken 3 | Pose reference / stance wiring | COMMERCIAL-DERIVED |
| `teardown/tekken3/stages/<letter>/` (15 dirs a–u) | Stage panorama OBJ + `stage.json` per stage (pattern verified on `stages/a`: `stage.json` + `stg_a_panorama.obj`; other 14 UNMEASURED deep) | Per-stage set | Tekken 3 | `game/assets/stages/t3/` — 15 stage panoramas (geometry done; textured atlases still need the full pipeline per TEARDOWN.md) | COMMERCIAL-DERIVED |
| `teardown/tekken3/tim-output/` (17,116 files: 8,559 PNG + 8,556 TIM + `inventory.json` 10,027,227 B) | Decoded TIM textures — exact count from the recursive tree, not the old 1,000-entry listing cap | 27.9 MB total | Tekken 3 | UI art, character textures, stage textures (`game/assets/ui/tim_*.png` already uses this pattern) | COMMERCIAL-DERIVED |
| `teardown/tekken3/tim-inventory.json` | Full TIM texture inventory | 10,022,608 | Tekken 3 | Texture lookup/index | COMMERCIAL-DERIVED |
| `teardown/tekken3/model-inventory.json` / `model-inventory.csv` | Full BNS model inventory | 8,346,757 / 41,530 | Tekken 3 | Model lookup/index | COMMERCIAL-DERIVED |
| `teardown/tekken3/BODY-EXTRACTION.json` | Body extraction record | 15,679 | Tekken 3 | Model wiring | COMMERCIAL-DERIVED |
| `teardown/tekken3/bns-table.pkl` | BNS record index (303 records) | 3,381 | Tekken 3 | Disc-layout lookup | COMMERCIAL-DERIVED |
| `teardown/tekken3/WIRING-INVENTORY.md` | Wiring inventory doc | 3,426,201 | Tekken 3 | Wiring reference — **UNMEASURED deep** (too big for the read tool to return; size only) | JAY'S OWN |
| `teardown/tekken3/TEARDOWN.md` | Own teardown doc (disc layout, BNS IDs, stage table, blockers) | 8,534 | Tekken 3 | Reference | JAY'S OWN |
| `teardown/tekken3/CANON-CONVERSION.md` | Own canon-conversion doc | 23,638 | Tekken 3 | Roster mapping | JAY'S OWN |
| `teardown/tekken3/docs/` (6 .md) | Own docs: 3DMK mapping, BNS pattern, pose solving, RE playbook, architecture, rig lessons | 3,752–6,653 each | Tekken 3 | Reference / rig method | JAY'S OWN |
| `teardown/tekken3/tools/` (1,974 files) | Own parsers (`kmd_parse.py`, `pose_sample_analytic.py`, `extract_stages.py`, `tim_extract.py`, `moveset_extract.py`, `usa_tables.py`, `usa_motion.py`, `extract_fighter.py`, `pose_assemble.py`, `validate_usa_spline.py`, `moveset_common_extract.py`) + pulled-in open-source Tekken 3 PC recompile project `psxrecomp/` (1,566 files: C/H/CPP) + `recomp-ui/` (151), `tools/` (135), `src/` (37), `mods/` (19), `native/` (13), `launcher/` (7) | 49.4 MB total | Tekken 3 | Extraction pipeline (own code; recompile project is open-source — licence not checked here, see UNMEASURED) | JAY'S OWN (own tools); UNKNOWN (psxrecomp licence) |
| `teardown/tekken3/ui/` (README.md + character-art, fonts-text, menus, title-screens) | T3 UI art source (11 TIM+PNG pairs per `game/data/t3-ui-art.json`) | UNMEASURED deep | Tekken 3 | Menu/UI templates — menus must cite a teardown source per repo rules | COMMERCIAL-DERIVED |
| `teardown/tekken3/renders/king/` + `renders/pose-check/` | King texture renders + pose-check renders | UNMEASURED deep | Tekken 3 | Visual reference | COMMERCIAL-DERIVED |
| `teardown/tekken3/rigging-reference/tekken3-hand-arm.md` | Own hand/arm rigging note | 1,934 | Tekken 3 | Rig reference | JAY'S OWN |
| `teardown/tekken3/disc/files/` + `disc/readme.txt` | Disc file listing | 25 (readme) | Tekken 3 | Disc-layout reference | JAY'S OWN |

## 3. teardown/tekken5/ — Tekken 5 (PS2), Devil Within lives here

See the Devil Within box above for the DW files. Rest of the folder:

| Exact repo path | What it is | Size | Game | What it could wire into | Origin |
|---|---|---|---|---|---|
| `teardown/tekken5/ROSTER.md` | Own roster doc | 1,381 | Tekken 5 | Roster mapping | JAY'S OWN |
| `teardown/tekken5/STAGES.md` | Own stage doc (16 versus + 5 DW stages documented) | 887 | Tekken 5 | Stage list | JAY'S OWN |
| `teardown/tekken5/TEARDOWN.md` | Own teardown doc | 5,789 | Tekken 5 | Reference | JAY'S OWN |
| `teardown/tekken5/tools/iso9660_extract.py`, `t5_survey.py` | Own ISO extraction/survey scripts | (2 .py) | Tekken 5 | Extraction pipeline | JAY'S OWN |
| `teardown/tekken5/rigging-reference/` (1 .md) | Own rigging note | UNMEASURED deep | Tekken 5 | Rig reference | JAY'S OWN |
| `teardown/tekken5/ui/` (1 .md) | Own UI note | UNMEASURED deep | Tekken 5 | Menu reference | JAY'S OWN |

## 4. teardown/tekken6/ — Tekken 6 (PSP), ~30% (DATA401 models still encrypted)

| Exact repo path | What it is | Size | Game | What it could wire into | Origin |
|---|---|---|---|---|---|
| `teardown/tekken6/models/` (3,526 files, 84.1 MB) | NDPP model parts: 76 root GLBs (`idx<NN>_skeleton_r<9/10/11>.glb`, `idx<NN>_bone_slot12_r<10/11>.glb`, `idx<NN>_slot<0/10>_r9.glb`, ~3–106 KB each) + `parts/` subdirs seg00–seg25 holding **3,444 more GLBs** + `previews/` (2 PNG) + `tools/` (2 files) + `NDPP-FORMAT.md` + `SKELETON-SUPERSEDE.md` — skeleton/bounding-volume segments, NOT full textured fighters | 84.1 MB total | Tekken 6 (PSP) | Skeleton/bounding reference only; full models blocked on DATA401 decrypt | COMMERCIAL-DERIVED |
| `teardown/tekken6/movesets/t6psp-<fighter>-moveset[-v2/-v3].json` (54 files, 18 fighters × 3 versions) | Per-fighter movesets: Armor King, Asuka, Baek Doo San, Dragunov, Eddy, Heihachi, Jin, King, Kuma, Law, Lee, Lin Xiaoyu, Marduk, Nina, Raven, Roger, Wang, Zafina | 160,418–597,243 each; biggest King v2 597,152 | Tekken 6 (PSP) | `game/assets/movesets/` — T6-era moves per fighter (v3 = latest) | COMMERCIAL-DERIVED |
| `teardown/tekken6/movesets/INDEX.json` | Own moveset index | 2,774 | Tekken 6 (PSP) | Moveset lookup | JAY'S OWN |
| `teardown/tekken6/decrypted/EBOOT.DECRYPTED.ELF` | Decrypted EBOOT (4.1 MB ELF) + note .md | ~4.1 MB | Tekken 6 (PSP) | RE bench (decrypt lane); not game content | COMMERCIAL-DERIVED |
| `teardown/tekken6/T6-VOICE-BANK-INVENTORY-2026-10-24.json` | Voice-bank inventory | 53,123 | Tekken 6 (PSP) | Voice wiring index | COMMERCIAL-DERIVED |
| `teardown/tekken6/WIRING-INVENTORY.md` | Own wiring inventory | 35,931 | Tekken 6 (PSP) | Wiring reference | JAY'S OWN |
| `teardown/tekken6/TEARDOWN.md` + 11 more .md (DATA401-RE-NOTES, DINF-400-DECRYPTED, MOTION-UNBLOCK, KEYHUNT-REPORT, ROUND13/14/15-STATE, T6-IDX-SOLVED, TEKKEN6-FINAL-STATE, PPSSPP-LIVE-RUN-GUIDE) | Own decrypt/teardown docs | 2,352–15,547 each | Tekken 6 (PSP) | RE bench reference | JAY'S OWN |
| `teardown/tekken6/tools/` (34 files, 15 subdirs; 20 .py) | Own decrypt/extraction tools (sector cipher etc.) | UNMEASURED deep | Tekken 6 (PSP) | Extraction pipeline | JAY'S OWN |
| `teardown/tekken6/docs/` (4 .md) | Own docs | UNMEASURED deep | Tekken 6 (PSP) | Reference | JAY'S OWN |
| `teardown/tekken6/gpu-jobs/` (3 .py + 1 .md) | Own GPU job scripts | UNMEASURED deep | Tekken 6 (PSP) | Pipeline | JAY'S OWN |
| `teardown/tekken6/ref_frames/` (42 .jpg) | Ending-video reference frames | ~22–24 KB each | Tekken 6 (PSP) | Visual reference | COMMERCIAL-DERIVED |
| `teardown/tekken6/stages/slice/` | Stage slice data | UNMEASURED deep | Tekken 6 (PSP) | Stage work | COMMERCIAL-DERIVED |
| `teardown/tekken6/ui/` (2 .md + 2 .png) | Own UI notes + 2 images | UNMEASURED deep | Tekken 6 (PSP) | Menu reference | JAY'S OWN |
| `teardown/tekken6/videos/` (1 .md) | Own video note (46 ending videos live on release, not in repo) | UNMEASURED deep | Tekken 6 (PSP) | Reference | JAY'S OWN |
| `teardown/tekken6/rigging-reference/` (1 .json + 1 .md) | Rigging reference | UNMEASURED deep | Tekken 6 (PSP) | Rig reference | JAY'S OWN |

## 5. teardown/tekken7/ — Tekken 7 (PC/Steam), ~40% (King-focused)

| Exact repo path | What it is | Size | Game | What it could wire into | Origin |
|---|---|---|---|---|---|
| `teardown/tekken7/king/` (94 files, 30.1 MB) | King T7 pull: 1 FBX (`5PMH7G85GYN7P71W3BD1V0249.fbx` 963,760 B) + 2 GLB + ~90 PNG textures (Diffuse/Normal/Specular: ArmBelt, ArmProtectors, Arms, BootProtector, DefaultHead 1,338,039 B, Torso, Hands, Pants, MaskFur, Eye, Teeth, Neck, Buckles…) + `License.txt` + `export_tail_glb.py` + `export_tail_light.py` + JPGs; subdirs `pantera/` + `views/` | Per-file sizes not all listed | Tekken 7 | Pantera body (King-based) textures + model reference; Pantera is the King-based fighter | COMMERCIAL-DERIVED (textures/FBX); JAY'S OWN (export scripts) |
| `teardown/tekken7/facepaint-reference.json` | Face-paint reference data | 16,028 | Tekken 7 | Customization / face paint | COMMERCIAL-DERIVED |
| `teardown/tekken7/arenas/` (1 .rar) | Arena archive | UNMEASURED (contents unknown) | Tekken 7 | Stage work — contents UNMEASURED | UNKNOWN |
| `teardown/tekken7/models/king-variants/` | King variant models | UNMEASURED deep | Tekken 7/8 | King variant reference | COMMERCIAL-DERIVED |
| `teardown/tekken7/T7-STEAM-EXTRACTION.md` | Own Steam extraction doc | 7,662 | Tekken 7 | Extraction method | JAY'S OWN |
| `teardown/tekken7/TEKKEN7-ROSTER-COVERAGE.md` | Own roster coverage doc | 13,103 | Tekken 7 | Roster mapping | JAY'S OWN |
| `teardown/tekken7/TEKKEN7-ROSTER-MAPPING.md` | Own roster mapping doc | 7,388 | Tekken 7 | Roster mapping | JAY'S OWN |
| `teardown/tekken7/tekken-model-catalog.md` / `tekken-model-pull-all.md` / `tekken-missing4-catalog.md` | Own model catalog/pull docs | 5,078 / 7,957 / 2,680 | Tekken 7 | Model sourcing | JAY'S OWN |
| `teardown/tekken7/tekkenmods-docs/` (1 .md + 1 subdir) | TekkenMods docs | UNMEASURED deep | Tekken 7 | Modding reference | UNKNOWN |
| `teardown/tekken7/tools/` (1 file) | Own tool | UNMEASURED | Tekken 7 | Pipeline | JAY'S OWN |
| `teardown/tekken7/ui/` (2 .md) | Own UI notes | UNMEASURED deep | Tekken 7 | Menu reference | JAY'S OWN |
| `teardown/tekken7/rigging-reference/` (1 .md) | Own rigging note | UNMEASURED deep | Tekken 7 | Rig reference | JAY'S OWN |

## 6. teardown/tekken8/ — Tekken 8 (PC), ~10%

| Exact repo path | What it is | Size | Game | What it could wire into | Origin |
|---|---|---|---|---|---|
| `teardown/tekken8/models/` (3 files, 113.2 MB) | `PHANTOM-t8-yoshimitsu-s1.7z` (83,173,144 B) + `asuka-kazama-t8_SFM.rar` (30,027,257 B) + `gdrive-dl.sh` (904 B) — fan model archives staged for GPU conversion + owner eye-check, NOT loaded by any game JS | 113.2 MB total | Tekken 8 | Nothing until converted + texture-gated + eye-checked | COMMERCIAL-DERIVED (archives); JAY'S OWN (`gdrive-dl.sh`) |
| `teardown/tekken8/ui/CHARACTER-SELECT.md` + `ui/refs/` | Own character-select doc + refs | UNMEASURED deep | Tekken 8 | Select-screen reference (Tekken 8 select is a cited source) | JAY'S OWN |

## 7. teardown/tekken-tag-tournament-2/ — Tekken Tag Tournament 2 (X360), ~15%

| Exact repo path | What it is | Size | Game | What it could wire into | Origin |
|---|---|---|---|---|---|
| `teardown/tekken-tag-tournament-2/data001-section-table.json` / `data028-section-table.json` / `ttt2-inner-listing.json` | Container section tables + inner listing | 30,448 / 8,793 / 6,216 | TTT2 | Container lookup for extraction | COMMERCIAL-DERIVED |
| `teardown/tekken-tag-tournament-2/INVENTORY.md` / `ROSTER.md` (59 fighters) / `STAGES.md` (29 stages) | Own inventory/roster/stage docs | 13,867 / 3,661 / 2,973 | TTT2 | Roster + stage planning | JAY'S OWN |
| `teardown/tekken-tag-tournament-2/TEARDOWN.md` / `TEARDOWN-STATUS-20261025.md` / `CONTAINER-ANALYSIS-20261025.md` / `DATA000-XML-JOIN-20261025.md` / `DATA001-DATA028-DECODE-20261030.md` / `DATANNN-MAP-20261025.md` / `MVLT-GLYPH-MAP-20261030.md` / `EXTRACTION-RUNBOOK.md` / `HEADER-LISTING.txt` / `INNER-LISTING.md` / `XDVDFS-LISTING.md` / `TTT2-PC-PORT-ASSESSMENT.md` | Own teardown/container docs + listings | 2,671–18,940 each | TTT2 | RE bench reference | JAY'S OWN |
| `teardown/tekken-tag-tournament-2/extracted-small/` (13 files, no extension) | Small extracted files | UNMEASURED (contents unknown) | TTT2 | Extraction output — contents UNMEASURED | UNKNOWN |
| `teardown/tekken-tag-tournament-2/pulls/` (1 .json) | Pull record | UNMEASURED deep | TTT2 | Sourcing | JAY'S OWN |
| `teardown/tekken-tag-tournament-2/tools/` (6 .py + 2 subdirs) | Own extraction tools | UNMEASURED deep | TTT2 | Extraction pipeline | JAY'S OWN |
| `teardown/tekken-tag-tournament-2/ui/` (1 .md) + `rigging-reference/` (1 .md) | Own notes | UNMEASURED deep | TTT2 | Reference | JAY'S OWN |

## 8. teardown/eastern-mind/ — Eastern Mind: The Lost Souls of Tong-Nou (1994), extraction done 2026-10-15

| Exact repo path | What it is | Size | Game | What it could wire into | Origin |
|---|---|---|---|---|---|
| `teardown/eastern-mind/stage-1-plains-of-chi-u/` … `stage-6-octagonal-shrine-par-fang/` (6 dirs) | Per-land extracted art: `bitmaps/` + `sounds/` (+ `text/` / `video/` on some). Exact tree counts: stage-2 Helix Palace 1,282 files (26.7 MB) · stage-3 Palace of Dreaming 676 (30.1 MB) · stage-1 Plains of Chi-U 518 (11.6 MB) · stage-4 Tree of Life 505 (13.0 MB) · stage-6 Octagonal Shrine 223 (13.7 MB) · stage-5 Phantom Marketplace 100 (1.7 MB). Whole-game doc counts: 5,321 bitmaps (PNG, 8-bit, game palette), 229 sounds (WAV), 22 videos (MP4), 31 text files | 5,709 files total, 422.8 MB (tree count; the folder's own WIRING-INVENTORY says 5,707 — 2-file drift = newer HEAD) | Eastern Mind | The 6 WH lands: stage backdrops, stage-intro art, palette + sound per land | COMMERCIAL-DERIVED |
| `teardown/eastern-mind/incarnation-system/` (512 files, 11.5 MB) | Nine-incarnation art + sound (R_BYOU, R_JIN, R_SHA, etc.) | 11.5 MB | Eastern Mind | Reincarnation system art/sound | COMMERCIAL-DERIVED |
| `teardown/eastern-mind/prologue-ending/` (661 files, 16.3 MB) | Prologue/ending art, sound, text, video | 16.3 MB | Eastern Mind | Story prologue/ending screens | COMMERCIAL-DERIVED |
| `teardown/eastern-mind/transcript-promo/` (1,128 files, 100.9 MB) | Transcript/promo art, sound, video (incl. `PROMO.mp4` 60,353,715 B, `PROM000.mp4` 18,380,451 B) | 100.9 MB | Eastern Mind | Promo/transcript screens | COMMERCIAL-DERIVED |
| `teardown/eastern-mind/palettes/` (97 files: 49 `.pal` + 48 `.bin`) | 48 unique 256-colour palettes | 0.1 MB | Eastern Mind | Palette-accurate rendering of EM bitmaps | COMMERCIAL-DERIVED |
| `teardown/eastern-mind/soundtrack/` (4 WAVs, 194.7 MB) | CD audio tracks (Tong-Nou Theme 4:29, 47,519,852 B; Transmigration Ending 5:16, 55,725,980 B; Esoteric Mix 8:01, 84,770,828 B; + 1 more) | 194.7 MB | Eastern Mind | Menu/stage music (already mapped in `game/data/music-library.json` + `sound-bank.json`) — WAVs are full CD quality, need compressing for the web | COMMERCIAL-DERIVED |
| `teardown/eastern-mind/WIRING-INVENTORY.md` | Wiring inventory doc | 2,338,665 | Eastern Mind | Wiring reference — **UNMEASURED deep** (too big for the read tool) | JAY'S OWN |
| `teardown/eastern-mind/CANON-CONVERSION.md` | Own canon-conversion doc | 24,570 | Eastern Mind | Land/stage mapping | JAY'S OWN |
| `teardown/eastern-mind/TEARDOWN.md` | Own teardown doc (counts, formats, WH stage mapping) | 2,965 | Eastern Mind | Reference | JAY'S OWN |

Note: `game/data/sound-bank.json` calls Eastern Mind "owner's own game" with licence "owner-original". That claim is recorded as the repo's own words. Eastern Mind is a 1994 commercial game (Osamu Sato / OutSide Directors Company), so this inventory still flags the extracted bitmaps/sounds as COMMERCIAL-DERIVED until Jay's licence call says otherwise.

## 9. teardown/soulcalibur-2/ — Soulcalibur II (Xbox/PS2), ~60%

| Exact repo path | What it is | Size | Game | What it could wire into | Origin |
|---|---|---|---|---|---|
| `teardown/soulcalibur-2/models/` (22 GLB, idx47–idx827) | Extracted fighter models (untextured pass) | Per-file sizes not listed | Soulcalibur II | Fighter models (weapon fighters) | COMMERCIAL-DERIVED |
| `teardown/soulcalibur-2/models-skinned/` (22 GLB) | Skinned fighter models | Per-file sizes not listed | Soulcalibur II | Same, skinned | COMMERCIAL-DERIVED |
| `teardown/soulcalibur-2/models-textured/` (105 files, 115.9 MB) | Textured fighter GLBs (~0.9–1.4 MB each) + variants named: Mitsurugi, Taki, Maxi, Voldo, Sophitia, Ivy, Kilik, Xianghua, Yoshimitsu, Nightmare, Astaroth, Cervantes, Raphael, Talim, Cassandra, Necrid, Yun-seong, Seong Mi-na (+ rigid-only-b, unidentified-1e) | 115.9 MB | Soulcalibur II | Textured weapon fighters | COMMERCIAL-DERIVED |
| `teardown/soulcalibur-2/stages/stage_m<000–120>.glb` (41 GLB) | Stage models, m000–m120 step 3 | 29,580–27,752,736 each; biggest `stage_m000.glb` 27,752,736 | Soulcalibur II | Arena stages (8-Way Run, Ring Out) | COMMERCIAL-DERIVED |
| `teardown/soulcalibur-2/tools/` (9 .py) | Own tools (`apply_textures.py`, `build_rigid.py`, …) | 6,971–7,496 each (first two) | Soulcalibur II | Model pipeline | JAY'S OWN |
| `teardown/soulcalibur-2/phase13-proof/` (10 .png) / `phase14-proof/` (6 .png) / `phase15-proof/` (3 .png) | Proof renders | UNMEASURED deep | Soulcalibur II | Visual proof | JAY'S OWN |
| `teardown/soulcalibur-2/PHASE14-AV-MANIFEST.json` | AV manifest | 26,922 | Soulcalibur II | AV inventory | COMMERCIAL-DERIVED |
| `teardown/soulcalibur-2/WIRING-INVENTORY.md` | Own wiring inventory | 19,671 | Soulcalibur II | Wiring reference | JAY'S OWN |
| `teardown/soulcalibur-2/*.md` (13 docs: CANON-CONVERSION, CENSUS-PHASE13, CHARACTER-MAP, PHASE13/14/15-STATE, PHASE14-AV-INVENTORY, PHASE14-PROBES, PHASE14-STAGE-LAYOUTS, PHASE15-PROBES, STAGES, TEARDOWN, TEXTURED-MODELS, VXT-FORMAT, XBOX-EXTRACTION-REPORT, XISO-FINDINGS) | Own teardown docs | 2,020–7,629 each | Soulcalibur II | Reference | JAY'S OWN |
| `teardown/soulcalibur-2/rigging-reference/` (1 .md) | Own rigging note | UNMEASURED deep | Soulcalibur II | Rig reference | JAY'S OWN |

## 10. teardown/soulcalibur-6/ + dead-or-alive-6/ — mechanics docs only

| Exact repo path | What it is | Size | Game | What it could wire into | Origin |
|---|---|---|---|---|---|
| `teardown/soulcalibur-6/HOLDINGS-INDEX-2026-11-06.md` | Own holdings index (SCVI acquired 2026-11-06 from archive.org, item dixen-18-soulcalibur-vi, 7 parts on release; extraction pending) | 8,509 | Soulcalibur VI | Sourcing — no extracted data in repo yet | JAY'S OWN |
| `teardown/soulcalibur-6/TEARDOWN.md` | Own mechanics teardown doc | 5,625 | Soulcalibur VI | Mechanics reference | JAY'S OWN |
| `teardown/soulcalibur-6/docs/` (1 .md) | Own doc | UNMEASURED deep | Soulcalibur VI | Reference | JAY'S OWN |
| `teardown/dead-or-alive-6/DOA6-MECHANICS.md` | Own mechanics doc | 9,256 | Dead or Alive 6 | Mechanics reference (50 GB+ binary not acquired) | JAY'S OWN |
| `teardown/dead-or-alive-6/TEARDOWN.md` | Own teardown doc | 2,157 | Dead or Alive 6 | Reference | JAY'S OWN |

## 11. teardown/dead-or-alive-4/ — Dead or Alive 4 (X360), ~15% (chunks on release, not reassembled)

| Exact repo path | What it is | Size | Game | What it could wire into | Origin |
|---|---|---|---|---|---|
| `teardown/dead-or-alive-4/models/` (279 files, 74.2 MB) | Bass Armstrong GLBs (`bass_cos01_plain.glb` 3,334,144 B, `bass_cos01_bandana_glasses.glb` 3,314,984 B, source zip `DOA5_Bass_Armstrong_Costume_1.zip` 20,268,372 B) + triangulated Chrone GLBs (`chrone_00–04`, ~300–343 KB each) + `chrone-pkg00-assembled-v1.glb` (1,794,028 B) | 74.2 MB | DOA 4 | Fighter models (GLBs drop into the web build) | COMMERCIAL-DERIVED |
| `teardown/dead-or-alive-4/workdir/` (221 files, 39.2 MB, incl. `default_pe.bin` 23,068,672 B) | Workdir / raw PE + intermediates | 39.2 MB | DOA 4 | Work files, not game content | COMMERCIAL-DERIVED |
| `teardown/dead-or-alive-4/tools/` (26 files: 20 `.py`, 12 `.cpp`, 10 `.java` across the folder) | Own extraction tools | 0.1 MB | DOA 4 | Extraction pipeline | JAY'S OWN |

## 12. teardown/def-jam-fight-for-ny/ — Def Jam: Fight for NY (PS2, EA Chicago / AKI lineage)

| Exact repo path | What it is | Size | Game | What it could wire into | Origin |
|---|---|---|---|---|---|
| `teardown/def-jam-fight-for-ny/EAGL-FORMAT-SPEC.md` | Own EAGL format spec (41 KB — the deepest format doc in this folder) | 41,542 | Def Jam FFNY | Grappling-system format reference | JAY'S OWN |
| `teardown/def-jam-fight-for-ny/ANIMATION-FINDINGS.md` | Own animation + grappling findings (AKI wrestling core in a Tekken-style 3D fighter) | 8,415 | Def Jam FFNY | Grappling design | JAY'S OWN |
| `teardown/def-jam-fight-for-ny/EAGL-FORMAT-ANALYSIS.md` / `TEARDOWN.md` / `ISO-MANIFEST.md` | Own format analysis / teardown / ISO manifest | 2,905 / 8,853 / 2,088 | Def Jam FFNY | Reference | JAY'S OWN |
| `teardown/def-jam-fight-for-ny/surgical/` (248 files, 29.3 MB: 156 `.o` + 78 `.ssh` character extracts `V2IP_*.o`/`*.ssh` ~140–199 KB each + `audio/ANIMTAGS.DAT` 474,898 B + `TV.TXT`) | Extracted character objects + SSH files + animation-tag data | 29.3 MB | Def Jam FFNY | Raw extracts — not decoded to models/anims yet | COMMERCIAL-DERIVED |
| `teardown/def-jam-fight-for-ny/tools/` (8 files: 7 `.py` + 1) | Own tools | small | Def Jam FFNY | Extraction pipeline | JAY'S OWN |
| `teardown/def-jam-fight-for-ny/lane-logs/` (6 files, incl. `curl-defjam-resume3.log` 490,617 B) | Lane logs | 1.4 MB | Def Jam FFNY | Work logs | JAY'S OWN |
| `teardown/def-jam-fight-for-ny/sample-renders/` (3 PNGs, incl. `V2CP_110_0001_A_STRIP_FAILED.png` 423,670 B) | Sample renders (one labelled FAILED) | 0.9 MB | Def Jam FFNY | Proof (incl. a failed strip) | JAY'S OWN |
| `teardown/def-jam-fight-for-ny/rigging-reference/` (1 file) | Own rigging note | small | Def Jam FFNY | Rig reference | JAY'S OWN |

## 13. teardown/urban-reign/ — Urban Reign (PS2, Namco), ~95%

| Exact repo path | What it is | Size | Game | What it could wire into | Origin |
|---|---|---|---|---|---|
| `teardown/urban-reign/models/char<001–072>/` + `ROSTER.json` | 72 character PPK slots (60+ roster + alternates) | UNMEASURED deep | Urban Reign | Brawl-mode fighters (Paul/Law Tekken guests among them) — inner PPK geometry still open per TEARDOWN.md | COMMERCIAL-DERIVED |
| `teardown/urban-reign/textured-models/` (72 GLB + 1 .json) | Textured character models, char001–char072 | Per-file sizes not listed | Urban Reign | Brawl-mode fighters, textured | COMMERCIAL-DERIVED |
| `teardown/urban-reign/textures/char<001–072>/` + census files | Per-character textures + census | UNMEASURED deep | Urban Reign | Fighter textures | COMMERCIAL-DERIVED |
| `teardown/urban-reign/ppks/chars/` + `ppks/stages/` | 72 fighter PPKs + 7 stage PPKs (stage003/004/020/028/029/030/031, 34 MB) | UNMEASURED deep | Urban Reign | Stage + fighter source packs | COMMERCIAL-DERIVED |
| `teardown/urban-reign/motion/` (6 files: `general_normal.gyu`, `general_30frame.gyu`, `general_weapon.gyu`, `gyuindex.bin`, `gyuindex_ppk.bin`, `gyu_debug.gyu`) | Shared animation pools + per-character move index | Sizes UNMEASURED | Urban Reign | Brawl animation banks (46 motion packs claimed) | COMMERCIAL-DERIVED |
| `teardown/urban-reign/motion-names/` (32 .json + 4 .md) | Motion-name maps | UNMEASURED deep | Urban Reign | Animation lookup | COMMERCIAL-DERIVED |
| `teardown/urban-reign/audio/` (1,034 files: 516 `.p3d` + 516 `.pbd` sound-bank pairs + README) | Extracted audio — exact count from the tree (old listing capped at 1,000; the 1,033 claim was 1 short) | 13.0 MB | Urban Reign | Brawl SFX/BGM (VGS decode cracked) | COMMERCIAL-DERIVED |
| `teardown/urban-reign/sound/ok_adx/adx/` (1,133 files: 998 `.adx` + `ADX-INVENTORY.csv` 41,045 B) | Background-music ADX files (e.g. `bg01_01.adx` 4,231,168 B) | 495.1 MB | Urban Reign | Brawl music — extracted, not wired into the game | COMMERCIAL-DERIVED |
| `teardown/urban-reign/cutscenes/` (35 .ppk) | Cutscene packs | UNMEASURED deep | Urban Reign | Story cutscenes | COMMERCIAL-DERIVED |
| `teardown/urban-reign/afs-map/dvd000_afs_map.json` (+ 1 more .json) | AFS map, all 2,431 DVD000 entries with offsets + sizes | UNMEASURED deep | Urban Reign | Surgical re-extraction without the ISO | COMMERCIAL-DERIVED |
| `teardown/urban-reign/vgs/` (VGS-BATCH-20261013.md + VGS-INVENTORY.csv + `decoded/` + `raw/`) | VGS audio inventory + decoded/raw sets | UNMEASURED deep | Urban Reign | Audio pipeline | COMMERCIAL-DERIVED |
| `teardown/urban-reign/missions/definitions/` + `missions/ppks/` | 100-mission story definitions + mission packs | UNMEASURED deep | Urban Reign | Story/mission mode (100 missions claimed) | COMMERCIAL-DERIVED |
| `teardown/urban-reign/animations/motion-packs/` | Motion packs | UNMEASURED deep | Urban Reign | Animation banks | COMMERCIAL-DERIVED |
| `teardown/urban-reign/sound/ok_adx/` | OK ADX sounds | UNMEASURED deep | Urban Reign | Sound | COMMERCIAL-DERIVED |
| `teardown/urban-reign/ui/` (README.md + character-select, menus, screens, title-screens) | UI screens (72 claimed) | UNMEASURED deep | Urban Reign | Menu/UI reference | COMMERCIAL-DERIVED |
| `teardown/urban-reign/*.md` (15 docs: BANK-COMPLETION, CANON-CONVERSION, PHASE3–6 states, PPK-FORMAT, PPK-GEOMETRY, TEARDOWN-ISO, TEARDOWN, UI-SYSTEM, VGS-FORMAT, WIRING-INVENTORY 6,782) | Own teardown/format docs | 2,565–10,954 each | Urban Reign | Reference / format specs | JAY'S OWN |
| `teardown/urban-reign/dvd000-contents.txt` / `dvd001-contents.txt` / `iso-file-listing.txt` | Disc content listings | 102,639 / 52,824 / 628 | Urban Reign | Disc lookup | COMMERCIAL-DERIVED |
| `teardown/urban-reign/tools/` (26 .py) | Own tools (PPK probe etc.) | UNMEASURED deep | Urban Reign | Extraction pipeline | JAY'S OWN |
| `teardown/urban-reign/rigging-reference/` (1 .md) + `docs/` (1 .md + 1 .txt) | Own notes | UNMEASURED deep | Urban Reign | Reference | JAY'S OWN |

## 14. teardown/wmxix/ — WWE WrestleMania XIX (GameCube, Yukes), ~80%

| Exact repo path | What it is | Size | Game | What it could wire into | Origin |
|---|---|---|---|---|---|
| `teardown/wmxix/animations/a.json` + `a<000–169>_0a.json` (170 JSON) | Decoded YANM animation clips | ~90–405 KB each | WMXIX | Grapple/entrance/taunt animation banks (retarget via YANM→Tekken3 pattern) | COMMERCIAL-DERIVED |
| `teardown/wmxix/arenas/` (40 .obj + ARENA-FORMAT.md + README.md + 2 .py) | Arena geometry OBJs | 3,139–551,041 each | WMXIX | Arena traversal / ring + backstage stages | COMMERCIAL-DERIVED |
| `teardown/wmxix/wrestlers/<000–110>/` (127 files) | 111 wrestler slots, base + alt attires as OBJs | 2.1 MB total | WMXIX | Wrestler models (126 OBJs claimed) | COMMERCIAL-DERIVED |
| `teardown/wmxix/textures/` (1,169 PNGs + 176 JSONs) | Wrestler/arena textures + metadata | 17.6 MB total | WMXIX | Wrestler + arena textures | COMMERCIAL-DERIVED |
| `teardown/wmxix/caw-parts/CATALOG.md` + `files.tsv` | CAW parts catalog (2,690 parts claimed) | 2,144 / 158,114 | WMXIX | Create-a-Wrestler parts | COMMERCIAL-DERIVED |
| `teardown/wmxix/WMXIX-WPRM-DECODE.json` | WPRM decode | 430,220 | WMXIX | Wrestler parameter data | COMMERCIAL-DERIVED |
| `teardown/wmxix/WMXIX-MPC-INDEX.json` | MPC index | 254,274 | WMXIX | Move/parameter index | COMMERCIAL-DERIVED |
| `teardown/wmxix/atr_all_events.json` | Animation metadata records (per-anim 16-byte records) | 242,384 | WMXIX | Animation metadata | COMMERCIAL-DERIVED |
| `teardown/wmxix/WMXIX-MOVE-NAME-SURVEY-2026-10-21.md` / `WMXIX-MPC-ASSIGNMENT-DECODE-2026-10-21.md` / `WMXIX-GHIDRA-MOVESET-XREF-2026-10-21.md` / `YANM-ITEM5/6/7/8/9/10-CYCLE.md` | Own move-name survey + MPC decode + Ghidra xref + YANM cycle docs | 5,417–25,591 each | WMXIX | Moveset decoding reference | JAY'S OWN |
| `teardown/wmxix/ARENA-UNIVERSE-MAP.md` / `TEARDOWN.md` / `CANON-CONVERSION.md` / `WIRING-INVENTORY.md` | Own arena map + teardown + canon conversion + wiring inventory | 22,404 / 29,626 / 7,353 / 348,943 | WMXIX | Reference / wiring | JAY'S OWN |
| `teardown/wmxix/tools/` (decode_tpl.py, extract_arena_textures.py, extract_wrestlers.py, extract_yanm.py, catalog_caw.py) | Own extraction tools | 3,268–10,465 each | WMXIX | Extraction pipeline | JAY'S OWN |
| `teardown/wmxix/docs/` (2 .md) + `ecd-render-test/` (28 .png + 3 .json) + `rigging-reference/` (1 .md) | Own docs + render tests + rigging note | UNMEASURED deep | WMXIX | Reference / proof | JAY'S OWN |

## 15. teardown/wwe-wrestlemania-xix/ — WWE WrestleMania XIX, second folder (retarget lane)

| Exact repo path | What it is | Size | Game | What it could wire into | Origin |
|---|---|---|---|---|---|
| `teardown/wwe-wrestlemania-xix/aki_to_tekken3_v1.json` | Own AKI→Tekken3 retarget map | 19,683 | WMXIX + Tekken 3 | Retargeting WMXIX anims onto Tekken skeletons | JAY'S OWN |
| `teardown/wwe-wrestlemania-xix/aki_to_tekken3.py` (v1/v2/v3: 5,035 / 4,394 / 7,266) | Own retarget scripts | 4,394–7,266 each | WMXIX + Tekken 3 | Retarget pipeline | JAY'S OWN |
| `teardown/wwe-wrestlemania-xix/atr_all_events.json` | Animation metadata records | 242,384 | WMXIX | Animation metadata (same size as the wmxix copy — likely duplicate) | COMMERCIAL-DERIVED |
| `teardown/wwe-wrestlemania-xix/wrestler-000-solved.obj` / `wrestler-000-solved-faced.obj` / `wrestler-000-solved-views.png` | Solved wrestler-000 mesh + views render | 18,341 / 26,090 / 109,659 | WMXIX | Wrestler-000 model proof | COMMERCIAL-DERIVED |
| `teardown/wwe-wrestlemania-xix/*.md` (17 YANM docs + AKI-TEKKEN3-RETARGET, REVENGE-MODE-ARENAS, WMXIX-ASSEMBLY-SOLUTION, WMXIX-AXIS-PERMUTATION, WRESTLER-IDENTITY-MAP, WRESTLER-SKELETON, YANM-F32-CORR, YANM-FIRST8B, YANM-FORMAT, YANM-UNKNOWN8, YOBJ-PAYLOAD-ITEM1, YOBJ-SKINNING-NOTES) | Own format/skeleton docs (70-bone YOBJ rig, 21-joint YCG anim rig, fully decoded per TEARDOWN.md) | 1,238–6,127 each | WMXIX | Retarget + skeleton reference | JAY'S OWN |
| `teardown/wwe-wrestlemania-xix/docs/` (21 files + 3 subdirs) | Own docs + data | UNMEASURED deep | WMXIX | Reference | JAY'S OWN |
| `teardown/wwe-wrestlemania-xix/objs/` (2 .obj) | Wrestler OBJs | UNMEASURED deep | WMXIX | Wrestler models | COMMERCIAL-DERIVED |
| `teardown/wwe-wrestlemania-xix/tools/` (65 .py + 2 subdirs) | Own extraction tools | UNMEASURED deep | WMXIX | Extraction pipeline | JAY'S OWN |
| `teardown/wwe-wrestlemania-xix/work/` (8 .txt) | Work notes | UNMEASURED deep | WMXIX | Work notes | JAY'S OWN |

## 16. teardown/wwf-no-mercy/ — WWF No Mercy (N64, AKI), teardown claimed 100%

| Exact repo path | What it is | Size | Game | What it could wire into | Origin |
|---|---|---|---|---|---|
| `teardown/wwf-no-mercy/arenas/` (36 files, verified by direct listing — the truncated tree missed this whole subtree) | Arena geometry + vertex-colour files, 17 arenas × (OBJ + VC) + `ARENAS.md` (3,049 B) + `assembly_manifest.json` (27,836 B). Named: armageddon, backlash, cage, king_of_the_ring, no_mercy, raw, royal_rumble, smackdown, summerslam, survivor_series, wrestlemania + backstage bar_lounge, boiler_room, hallway, locker_room, parking_lot + lobby | OBJ 43,233–215,588 B each (raw 215,588 B biggest); VC 8,251–38,190 B | WWF No Mercy | Ring + backstage stages (17 arenas claimed complete) | COMMERCIAL-DERIVED |
| `teardown/wwf-no-mercy/animations/clips/anim_*.npy` (436 files) + `FORMAT.md` (3,417 B) | Decoded AKI animation clips (Toki2, 98-byte frames, 19-joint; docs claim ~1,360 clips / 5,787 anims in the ROM — 436 decoded clips are the files in the repo) | ~1–2 KB each; 1.2 MB total | WWF No Mercy | AKI 19-joint animation bank — retarget onto Tekken skeletons | COMMERCIAL-DERIVED |
| `teardown/wwf-no-mercy/models/` (10 top entries, verified by direct listing — the truncated tree missed this subtree: `manifest.json` 769,672 B + 9 subdirs: arena, attire_parts, backstage, body_parts, face, lobby, stage, unlabeled, weapon) | Wrestler models (3,570 claimed in docs) | manifest 769,672 B; subdir contents not opened | WWF No Mercy | Wrestler models | COMMERCIAL-DERIVED |
| `teardown/wwf-no-mercy/textures/` (4 top entries, verified by direct listing: `inventory.json` 10,156 B + subdirs characters, environments, rom) | Textures (5,029 claimed in docs) | inventory 10,156 B; subdir contents not opened | WWF No Mercy | Wrestler/arena textures | COMMERCIAL-DERIVED |
| `teardown/wwf-no-mercy/aki-rock-v3/` (11 .json) | AKI retarget data v3 | UNMEASURED deep | WWF No Mercy | Retarget data | JAY'S OWN |
| `teardown/wwf-no-mercy/aki_to_tekken3_v1.json` / `v2.json` + `aki_to_tekken3.py` (v1/v2/v3) | Own AKI→Tekken3 retarget maps + scripts | 19,683 / 18,779; scripts 4,394–7,266 | WWF No Mercy + Tekken 3 | Retarget pipeline (already the sanctioned pattern) | JAY'S OWN |
| `teardown/wwf-no-mercy/WIRING-INVENTORY.md` | Wiring inventory doc | 2,610,726 | WWF No Mercy | Wiring reference — **UNMEASURED deep** (too big for the read tool) | JAY'S OWN |
| `teardown/wwf-no-mercy/docs/` (4 .md + 3 .json: wrestler-id-table etc.) | Own docs + ID tables (42 wrestlers, IDs 0–43) | 5,342–7,417 (mds) | WWF No Mercy | Wrestler IDs, CAW tables, move tables | JAY'S OWN |
| `teardown/wwf-no-mercy/CANON-CONVERSION.md` / `TEARDOWN.md` / `CAW-SAVE-RECORD-STATUS.md` / `TEXT-CODE-DICTIONARY.md` / `TOKI2-SEMANTICS.md` | Own canon/teardown/CAW/text-code docs | 1,257–10,275 each | WWF No Mercy | CAW system, entrance-music table (50 entries), part-string tables (15 categories) | JAY'S OWN |
| `teardown/wwf-no-mercy/tools/` (9 .py + 1 .txt) | Own tools (`anim_extract.py`, `caw_parse.py`, …) | UNMEASURED deep | WWF No Mercy | Extraction pipeline | JAY'S OWN |
| `teardown/wwf-no-mercy/recomp/` (9 files + 11 subdirs) | Decomp project (WWFNoMercyRecomp) | UNMEASURED deep | WWF No Mercy | Decomp reference (community project) | COMMUNITY-FREE |
| `teardown/wwf-no-mercy/re-docs/` (2 files + 2 subdirs) + `rigging-reference/` (1 .md) | Own RE docs + rigging note | UNMEASURED deep | WWF No Mercy | Reference | JAY'S OWN |

## 17. teardown/virtua-fighter-5/ + vf5/ — Virtua Fighter 5 (PS3), teardown claimed 100%

| Exact repo path | What it is | Size | Game | What it could wire into | Origin |
|---|---|---|---|---|---|
| `teardown/virtua-fighter-5/TEARDOWN.md` / `VF5-STATUS.md` / `VF5-MODELS-MANIFEST.md` / `VF5-VERIFICATION.md` | Own teardown/status/manifest docs (19 fighters + 38 stages claimed) | 4,274 / 23,124 / 1,135 / 2,225 | Virtua Fighter 5 | Roster + stage planning | JAY'S OWN |
| `teardown/virtua-fighter-5/models/aki/` + `akixx/` + `dur/` + README.md | VF5 model work (Akira etc.) | UNMEASURED deep | Virtua Fighter 5 | Fighter models | COMMERCIAL-DERIVED |
| `teardown/virtua-fighter-5/docs/` (2 .7z + 1 .md) | Docs + archives | UNMEASURED (archive contents unknown) | Virtua Fighter 5 | Reference | UNKNOWN |
| `teardown/virtua-fighter-5/stages/` (1 .md) | Own stage note | UNMEASURED deep | Virtua Fighter 5 | Stage list | JAY'S OWN |
| `teardown/virtua-fighter-5/rigging-reference/` (1 .json) | Rigging reference | UNMEASURED deep | Virtua Fighter 5 | Rig reference | JAY'S OWN |
| `teardown/virtua-fighter-5/tools/` (1 .py) | Own tool | UNMEASURED deep | Virtua Fighter 5 | Pipeline | JAY'S OWN |
| `teardown/vf5/ACQUISITION-PLAN.md` | Own acquisition plan | 4,932 | Virtua Fighter 5 | Sourcing | JAY'S OWN |

## 18. teardown/street-fighter-*/ — Street Fighter 3D games + SFV

| Exact repo path | What it is | Size | Game | What it could wire into | Origin |
|---|---|---|---|---|---|
| `teardown/street-fighter-3d-games/CATALOG.md` / `SF-TEARDOWN-STATUS.md` | Own archive.org catalog + status (EX series priority) | 4,399 / 8,754 | Street Fighter EX series | Sourcing | JAY'S OWN |
| `teardown/street-fighter-3d-games/eastern-mind/` (9 .md) | Own Eastern Mind notes (second copy lane) | UNMEASURED deep | Eastern Mind | Reference | JAY'S OWN |
| `teardown/street-fighter-3d-games/tools/` (3 .py) + `work/` (4 .txt + 2 .py) + `extracted/` (1 subdir) | Own tools + work files | UNMEASURED deep | Street Fighter 3D | Pipeline | JAY'S OWN |
| `teardown/street-fighter-5/CAST-STATUS.md` / `SFV-PULL-PLAN.md` | Own cast status + pull plan | 8,276 / 2,697 | Street Fighter V | Sourcing (SFV pull was blocked on the piracy route per CATALOG.md) | JAY'S OWN |
| `teardown/street-fighter-5/models/rashid/` | Rashid model work | UNMEASURED deep | Street Fighter V | Fighter model | COMMERCIAL-DERIVED |
| `teardown/street-fighter-ex-plus-alpha/push.py` + nested `street-fighter-ex-plus-alpha/street-fighter-ex-plus-alpha/` (4 files; deepest dir empty) | Own push script + EX Plus Alpha lane files | 2,221 (push.py) | Street Fighter EX Plus Alpha | Pipeline | JAY'S OWN |
| `teardown/street-fighter-ex2-plus/TEARDOWN.md` / `iso-file-listing.txt` | Own teardown + ISO listing | 4,798 / 11,140 | Street Fighter EX2 Plus | Reference | JAY'S OWN |
| `teardown/street-fighter-ex3/TEARDOWN.md` | Own teardown doc | 2,555 | Street Fighter EX3 | Reference | JAY'S OWN |

## 19. teardown/ — small folders + models/ + community/ + western-heart-design/

| Exact repo path | What it is | Size | Game | What it could wire into | Origin |
|---|---|---|---|---|---|
| `teardown/firepro/README.md` | Own readme only (1 file) | 1,922 | Fire Pro Wrestling | Nothing yet — no data in repo | JAY'S OWN |
| `teardown/gang-beasts/README.md` | Own readme only (1 file) | 1,328 | Gang Beasts | Nothing yet — no data in repo | JAY'S OWN |
| `teardown/nioh/README.md` | Own readme only (1 file) | 1,601 | Nioh | Nothing yet — no data in repo | JAY'S OWN |
| `teardown/wrestling-empire/README.md` | Own readme only (1 file) | 998 | Wrestling Empire | Nothing yet — no data in repo | JAY'S OWN |
| `teardown/yakuza-kiwami/README.md` | Own readme only (1 file) | 1,039 | Yakuza Kiwami | Nothing yet — no data in repo (full Yakuza research is the root doc §1) | JAY'S OWN |
| `teardown/wwe-2k/CATALOG.md` / `WWE2K-PULL-STATUS.md` / `WWE2K-SELECTIVE-EXTRACTION.md` / `WWE2K-TERABOX-SPEC.md` / `WWE2K14-DLC-CATALOG.md` / `WWE2K15-23-ACQUISITION.md` | Own WWE 2K docs (acquisition 0% per matrix) | 1,838–4,628 each | WWE 2K14–23 | Sourcing only | JAY'S OWN |
| `teardown/wwe2k19/FILES-SHA256.txt` / `SOURCE-SHA256.txt` / `PULL.md` / `README.md` / `batch1.txt` | Own pull + hash records | 1,004–193,352 (FILES-SHA256 193,352) | WWE 2K19 | Sourcing/verification | JAY'S OWN |
| `teardown/wwe2k19/extracted/` (1,673 files, 753.7 MB: `ingame/` 1,000 files, `edit/` 641 files, `ch/` 607 files incl. `ch10002/` + `ch10102/` `.yobj`/`.bin`/`.dds`, `fullbody_type/` 28) | Extracted 2K19 files — raw `.bin` (1,059) + `.dds` (597) + `.yobj` (6) + `.cnpc`/`.cnct` (5 each); biggest: `extracted/edit/body/body_10000/8E7394799DE536F6/0000.bin` (23,391,456 B), `body_00000/.../0000.bin` (22,751,200 B), `ch10102/.../0000.yobj` (19,339,488 B) | 753.7 MB | WWE 2K19 | Wrestler/edit/ingame data — raw, needs the WMXIX-style decode path | COMMERCIAL-DERIVED |
| `teardown/wwe2k20/README.md` | Own readme only | 1,022 | WWE 2K20 | Nothing yet | JAY'S OWN |
| `teardown/wwe2k22/README.md` | Own readme only | 1,824 | WWE 2K22 | Nothing yet | JAY'S OWN |
| `teardown/models/king-variants/` (1 .md + 1 .txt) | Own King-variant hunt list | UNMEASURED deep | Tekken | Model sourcing | JAY'S OWN |
| `teardown/models/pharaohillusion/` (1 .md + 1 .txt) | Own hunt list | UNMEASURED deep | — | Model sourcing | JAY'S OWN |
| `teardown/models/soulcalibur-hunt/` (1 .md) | Own SC hunt list | UNMEASURED deep | Soulcalibur | Model sourcing | JAY'S OWN |
| `teardown/models/tekken7/` (4 `.zip` + `MODELS-INDEX.md` 5,727 B) | Model archives: `eddy-t7-fbx.zip` (34,495,007 B), `asuka-t7-fbx.zip` (30,308,209 B), `steve-fox-t7-fbx.zip` (26,922,332 B — Demonio's body source), `xiaoyu-t7-fbx.zip` (17,368,214 B) | 109.1 MB total | Tekken 7 | FBX usable in the Blender pipeline after unpack — zips themselves are not web-loadable | COMMERCIAL-DERIVED (zips); JAY'S OWN (index) |
| `teardown/community/HANDOFF.md` | Own handoff note | 754 | — | Handoff | JAY'S OWN |
| `teardown/community/tekken7/rbnorway/` (143 files: 142 CSVs + 1 TXT) | Community Tekken 7 frame-data CSVs (rbnorway) | 0.6 MB total | Tekken 7 | Frame-data reference, same family as `game/data/t7-frame-data/` | COMMERCIAL-DERIVED (community transcription of Tekken 7 data) |
| `teardown/community/tekken8/movesets/kaiutzi21/` (19 files: `t8_KING_v2/t8_KING.json.gz` 1,109,808 B, `t8_LEE_v2/t8_LEE.json.gz`, `t8_ARMOR_KING/t8_ARMOR_KING.json.gz` 473,794 B + `.summary.json` files + `Tekken 8 Moveset Editing Data.xlsx` 77,310 B + `LICENSE.txt` + `README.md` + `summarize.py` + `SOURCE_COMMIT.txt`) | Community Tekken 8 movesets with summaries + spreadsheet | 6.4 MB total | Tekken 8 | Moveset reference — the most complete T8 moveset data in the repo (T8 coverage is otherwise ~10%) | COMMERCIAL-DERIVED (T8 data, community-packaged; `LICENSE.txt` terms not read — UNMEASURED) |
| `teardown/western-heart-design/asset-manifest.md` / `stages.md` / `systems.md` / `technical-plan.md` | Own design docs (the four docs DESIGN.md cites) | 8,939 / 6,857 / 7,987 / 8,713 | — | Design reference for stages/systems/tech plan | JAY'S OWN |
| `teardown/western-heart-design/king-tekken3-P1-front.png` / `king-tekken3-default.jpg` / `king-tekken3-ingame.jpg` | King-from-Tekken-3 reference images | 870,558 / 143,319 / 182,136 | Tekken 3 | Visual reference for the King body | COMMERCIAL-DERIVED |

---

## 20. game/data/ — root files (the web build's own data layer)

| Exact repo path | What it is | Size | Game | What it could wire into | Origin |
|---|---|---|---|---|---|
| `game/data/t8_frame_tables.json` | Tekken 8 frame tables, 41 chars / 6,284 moves (startup, block, hit, counter, target, KO, throw-break) | 326,507 | Tekken 8 | `game/js/` frame-data lookups, arcade ladder tuning — frame data only, NO animation IDs | COMMUNITY-FREE (CC0-1.0, wavu.wiki) |
| `game/data/soul-variants.json` | Generated soul-variant data (KESSHOU / NINE-SOUL RELEASE / REIHOU / TRIAL'S SEAL per fighter, power multipliers) | 257,102 | — (own system) | `game/js/soul-systems.js` — Nine-Soul Meter variants | JAY'S OWN |
| `game/data/sound-bank.json` | 229-sound bank (Eastern Mind sounds mapped to `game/assets/sounds/*.ogg`, `mappedTo` voice-manifest links) | 82,432 | Eastern Mind | `game/js/voice.js` `voice.playSound(bankId)` — prologues, cutscenes, UI | COMMERCIAL-DERIVED |
| `game/data/music-library.json` | Music library (Kevin MacLeod CC-BY-4.0 tracks + owner's Tong-Nou originals; swap-by-filename rule) | 53,603 | — | `game/js/music.js` MusicEngine, jukebox | JAY'S OWN (CC-BY tracks credited per track) |
| `game/data/cape-alisa-binding.json` | Cape Jones replaces Alisa: moveset + 188 T8 frame-data moves; notes T8/T7 motion files are ABSENT | 44,845 | Tekken 8 | Cape Jones fighter wiring (frame data in, anims owed) | JAY'S OWN |
| `game/data/roster_map.json` | Generated roster map (fighters, Tekken slot, moveset sources t3/t6/t7/t8, attires, ladder_ok) | 41,243 | Tekken (slots) | Select screen + ladder (generated by `tools/roster-map/build.mjs`) | JAY'S OWN |
| `game/data/eastern-mind-sfx.json` | Eastern Mind 229-sound catalog with slot mapping (ui.click, reincarn.death/rebirth, stage intros…) | 34,700 | Eastern Mind | SFX slots → `teardown/eastern-mind/` WAVs | COMMERCIAL-DERIVED |
| `game/data/audio-events.json` | Audio event banks (hits, Pantera voice, stage BGM stems, stingers, UI) | 22,334 | — | `game/js/` audio events | JAY'S OWN |
| `game/data/audio-download-manifest.json` | Music download manifest (Nosferatu 25 cuts etc.) | 10,563 | — | `game/assets/music/` pipeline | JAY'S OWN |
| `game/data/challenges.js` | Daily challenges + rotating events data (deterministic by date) | 10,068 | — (own system) | `game/js/challenges.js` + `unlockables.js` | JAY'S OWN |
| `game/data/ranks.json` | Rank ladder (Wood → Fire → Earth → Metal → Water + S-tier; points/promotion rules) | 8,785 | — (own system, Tekken structure) | `game/js/ranks.js` arcade ladder | JAY'S OWN |
| `game/data/t8-sfm-staging.json` | INERT staging only — stages the 2 Tekken 8 SFM model archives for GPU conversion + eye-check; NOT loaded by any game JS | 8,667 | Tekken 8 | Staging only; select slot stays placeholder until texture gate + eye-check pass | JAY'S OWN |
| `game/data/tripo-fighters.json` | Tripo-model fighters listed first on select (31 ids) | 6,874 | — | Select-screen ordering | JAY'S OWN |
| `game/data/announcer-events.json` | Announcer event → clip table (11 clips, all placeholder, subtitle-only; no announcer audio bytes exist; no call site found in the audited JS) | 6,233 | Tekken (announcer style) | `game/js/voice.js` announce() — call-site edits still owed | JAY'S OWN |
| `game/data/t3-ui-art.json` | Tekken 3 UI art registry (11 TIM+PNG pairs from `teardown/tekken3/ui/`, templates for WH UI) | 6,223 | Tekken 3 | UI art pipeline | JAY'S OWN |
| `game/data/canon-sizing.js` | Canon height + girth per fighter/version (scales fighter root so stance height matches canon) | 5,938 | — (own system) | `game/js/canon-sizing.js` | JAY'S OWN |
| `game/data/clothing-layers.json` | Clothing/hair/facewear layer maps per model (e.g. Parvati/Megami meshes) | 5,831 | — (own intake models) | Attire/customization layer toggles | JAY'S OWN |
| `game/data/jukebox-eras.json` | Jukebox eras (WH originals, Nosferatu, Cape Jones; Tekken data-only era listed, never playable) | 3,420 | — | `game/js/jukebox-eras.js` | JAY'S OWN |
| `game/data/jukebox-pools.json` | Jukebox pools (settings pick wins over stage rotation) | 3,392 | — | `game/js/jukebox.js` | JAY'S OWN |
| `game/data/owner-models.json` | Owner-provided (Tripo/user) model keys per fighter | 2,876 | — | Model-first rule tests | JAY'S OWN |
| `game/data/wrestling-sim-example.json` | WH-authored example wrestler record (no source-game wrestler/move copied) | 2,081 | — | `game/js/ai/cpu-logic-tables.js` exercise record | JAY'S OWN |
| `game/data/frame-data-schema-examples.json` | Frame-data schema examples | 1,096 | — | `game/js/frame-data-schema.js` | JAY'S OWN |
| `game/data/crossover.json` | Anim crossover rules (fight clips ↔ show/cutscene/intro contexts; show must never bleed into fight) | 1,026 | — | Anim context gating | JAY'S OWN |
| `game/data/credits.json` | Credits/dedications (Serena, Rosetta, Emory, Mars, Ken, Marquisha, Bink) | 537 | — | Story-ending + settings credits | JAY'S OWN |

## 21. game/data/t7-frame-data/ — Tekken 7 frame data (44 files, 5,648 base moves + DLC 9)

All 44 files share one LP1/RP2/LK3/RK4 JSON schema (`source`, `metadata_original`, `move_count`, `dups_removed`, `moves`). Loader: `game/js/t7-frame-data-loader.js` (consumer import held per README). Hard limit from the README: frame data is NOT a playable moveset — no animation IDs exist; rows carry `anim_ref: null` / `anim_status: 'UNMAPPED'` by design. Kuma is deliberately absent (upstream file was an empty placeholder).

| Exact repo path | What it is | Size | Game | What it could wire into | Origin |
|---|---|---|---|---|---|
| `game/data/t7-frame-data/README.md` | Own README: two source families, hard limits, licence flags, coverage gaps | 3,254 | Tekken 7 | Reference | JAY'S OWN |
| `game/data/t7-frame-data/t7-akuma-lp-rp-lk-rk.json` | Frame data, Akuma | 36,435 | Tekken 7 | Frame lookups | COMMERCIAL-DERIVED |
| `game/data/t7-frame-data/t7-alisa-lp-rp-lk-rk.json` | Frame data, Alisa | 58,399 | Tekken 7 | Frame lookups | COMMERCIAL-DERIVED |
| `game/data/t7-frame-data/t7-asuka-lp-rp-lk-rk.json` | Frame data, Asuka | 41,302 | Tekken 7 | Frame lookups | COMMERCIAL-DERIVED |
| `game/data/t7-frame-data/t7-bob-lp-rp-lk-rk.json` | Frame data, Bob | 51,831 | Tekken 7 | Frame lookups | COMMERCIAL-DERIVED |
| `game/data/t7-frame-data/t7-bryan-lp-rp-lk-rk.json` | Frame data, Bryan | 52,272 | Tekken 7 | Frame lookups | COMMERCIAL-DERIVED |
| `game/data/t7-frame-data/t7-claudio-lp-rp-lk-rk.json` | Frame data, Claudio | 28,660 | Tekken 7 | Frame lookups | COMMERCIAL-DERIVED |
| `game/data/t7-frame-data/t7-devil-jin-lp-rp-lk-rk.json` | Frame data, Devil Jin | 42,739 | Tekken 7 | Frame lookups | COMMERCIAL-DERIVED |
| `game/data/t7-frame-data/t7-dragunov-lp-rp-lk-rk.json` | Frame data, Dragunov | 42,036 | Tekken 7 | Frame lookups | COMMERCIAL-DERIVED |
| `game/data/t7-frame-data/t7-eddy-lp-rp-lk-rk.json` | Frame data, Eddy | 68,649 | Tekken 7 | Frame lookups | COMMERCIAL-DERIVED |
| `game/data/t7-frame-data/t7-eliza-lp-rp-lk-rk.json` | Frame data, Eliza | 25,841 | Tekken 7 | Frame lookups | COMMERCIAL-DERIVED |
| `game/data/t7-frame-data/t7-fahkumram-lp-rp-lk-rk.json` | Frame data, Fahkumram (DLC 9, TekkenDocs) | 41,060 | Tekken 7 | Frame lookups | COMMERCIAL-DERIVED |
| `game/data/t7-frame-data/t7-feng-lp-rp-lk-rk.json` | Frame data, Feng | 48,628 | Tekken 7 | Frame lookups | COMMERCIAL-DERIVED |
| `game/data/t7-frame-data/t7-ganryu-lp-rp-lk-rk.json` | Frame data, Ganryu (DLC 9, TekkenDocs) | 43,466 | Tekken 7 | Frame lookups | COMMERCIAL-DERIVED |
| `game/data/t7-frame-data/t7-geese-lp-rp-lk-rk.json` | Frame data, Geese (DLC 9, TekkenDocs) | 33,982 | Tekken 7 | Frame lookups | COMMERCIAL-DERIVED |
| `game/data/t7-frame-data/t7-gigas-lp-rp-lk-rk.json` | Frame data, Gigas | 30,094 | Tekken 7 | Frame lookups | COMMERCIAL-DERIVED |
| `game/data/t7-frame-data/t7-heihachi-lp-rp-lk-rk.json` | Frame data, Heihachi | 36,941 | Tekken 7 | Frame lookups | COMMERCIAL-DERIVED |
| `game/data/t7-frame-data/t7-hwoarang-lp-rp-lk-rk.json` | Frame data, Hwoarang | 65,540 | Tekken 7 | Frame lookups | COMMERCIAL-DERIVED |
| `game/data/t7-frame-data/t7-jack-7-lp-rp-lk-rk.json` | Frame data, Jack-7 | 55,729 | Tekken 7 | Frame lookups | COMMERCIAL-DERIVED |
| `game/data/t7-frame-data/t7-jin-lp-rp-lk-rk.json` | Frame data, Jin | 43,756 | Tekken 7 | Frame lookups | COMMERCIAL-DERIVED |
| `game/data/t7-frame-data/t7-josie-lp-rp-lk-rk.json` | Frame data, Josie | 39,689 | Tekken 7 | Frame lookups | COMMERCIAL-DERIVED |
| `game/data/t7-frame-data/t7-katarina-lp-rp-lk-rk.json` | Frame data, Katarina | 31,934 | Tekken 7 | Frame lookups | COMMERCIAL-DERIVED |
| `game/data/t7-frame-data/t7-kazumi-lp-rp-lk-rk.json` | Frame data, Kazumi | 29,710 | Tekken 7 | Frame lookups | COMMERCIAL-DERIVED |
| `game/data/t7-frame-data/t7-kazuya-lp-rp-lk-rk.json` | Frame data, Kazuya | 37,726 | Tekken 7 | Frame lookups | COMMERCIAL-DERIVED |
| `game/data/t7-frame-data/t7-king-lp-rp-lk-rk.json` | Frame data, King (34 dups removed; one jab row kept) | 47,572 | Tekken 7 | Frame lookups — Pantera's King base | COMMERCIAL-DERIVED |
| `game/data/t7-frame-data/t7-kunimitsu-lp-rp-lk-rk.json` | Frame data, Kunimitsu (DLC 9, TekkenDocs) | 54,394 | Tekken 7 | Frame lookups | COMMERCIAL-DERIVED |
| `game/data/t7-frame-data/t7-lars-lp-rp-lk-rk.json` | Frame data, Lars | 37,145 | Tekken 7 | Frame lookups | COMMERCIAL-DERIVED |
| `game/data/t7-frame-data/t7-law-lp-rp-lk-rk.json` | Frame data, Law | 67,355 | Tekken 7 | Frame lookups | COMMERCIAL-DERIVED |
| `game/data/t7-frame-data/t7-lee-lp-rp-lk-rk.json` | Frame data, Lee | 60,910 | Tekken 7 | Frame lookups | COMMERCIAL-DERIVED |
| `game/data/t7-frame-data/t7-leo-lp-rp-lk-rk.json` | Frame data, Leo | 48,820 | Tekken 7 | Frame lookups | COMMERCIAL-DERIVED |
| `game/data/t7-frame-data/t7-leroy-lp-rp-lk-rk.json` | Frame data, Leroy (DLC 9, TekkenDocs) | 36,681 | Tekken 7 | Frame lookups | COMMERCIAL-DERIVED |
| `game/data/t7-frame-data/t7-lidia-lp-rp-lk-rk.json` | Frame data, Lidia (DLC 9, TekkenDocs) | 46,517 | Tekken 7 | Frame lookups | COMMERCIAL-DERIVED |
| `game/data/t7-frame-data/t7-lili-lp-rp-lk-rk.json` | Frame data, Lili | 42,828 | Tekken 7 | Frame lookups | COMMERCIAL-DERIVED |
| `game/data/t7-frame-data/t7-ling-lp-rp-lk-rk.json` | Frame data, Ling Xiaoyu | 66,739 | Tekken 7 | Frame lookups | COMMERCIAL-DERIVED |
| `game/data/t7-frame-data/t7-lucky-chloe-lp-rp-lk-rk.json` | Frame data, Lucky Chloe | 41,326 | Tekken 7 | Frame lookups | COMMERCIAL-DERIVED |
| `game/data/t7-frame-data/t7-master-raven-lp-rp-lk-rk.json` | Frame data, Master Raven | 57,910 | Tekken 7 | Frame lookups | COMMERCIAL-DERIVED |
| `game/data/t7-frame-data/t7-miguel-lp-rp-lk-rk.json` | Frame data, Miguel | 45,920 | Tekken 7 | Frame lookups | COMMERCIAL-DERIVED |
| `game/data/t7-frame-data/t7-negan-lp-rp-lk-rk.json` | Frame data, Negan (DLC 9, TekkenDocs) | 35,426 | Tekken 7 | Frame lookups | COMMERCIAL-DERIVED |
| `game/data/t7-frame-data/t7-nina-lp-rp-lk-rk.json` | Frame data, Nina | 57,452 | Tekken 7 | Frame lookups | COMMERCIAL-DERIVED |
| `game/data/t7-frame-data/t7-noctis-lp-rp-lk-rk.json` | Frame data, Noctis (DLC 9, TekkenDocs) | 31,584 | Tekken 7 | Frame lookups | COMMERCIAL-DERIVED |
| `game/data/t7-frame-data/t7-paul-lp-rp-lk-rk.json` | Frame data, Paul | 36,906 | Tekken 7 | Frame lookups | COMMERCIAL-DERIVED |
| `game/data/t7-frame-data/t7-shaheen-lp-rp-lk-rk.json` | Frame data, Shaheen | 27,246 | Tekken 7 | Frame lookups | COMMERCIAL-DERIVED |
| `game/data/t7-frame-data/t7-steve-lp-rp-lk-rk.json` | Frame data, Steve Fox | 74,002 | Tekken 7 | Frame lookups — Demonio's body is a Steve Fox model | COMMERCIAL-DERIVED |
| `game/data/t7-frame-data/t7-yoshimitsu-lp-rp-lk-rk.json` | Frame data, Yoshimitsu | 114,602 | Tekken 7 | Frame lookups | COMMERCIAL-DERIVED |
| `game/data/t7-frame-data/t7-zafina-lp-rp-lk-rk.json` | Frame data, Zafina (DLC 9, TekkenDocs) | 55,056 | Tekken 7 | Frame lookups | COMMERCIAL-DERIVED |

Sources per README: base 35 from TheBigTuna/Tekken-7-Frame-Data (no licence file — treat as unlicensed community data, author check before verbatim commercial redistribution); DLC 9 from TekkenDocs API / rbnorway Google Sheet (no redistribution licence stated). Missing from the set: Anna, Armor King, Julia, Marduk and other season 2–4 fighters.

## 22. game/data/moveset-library/ + movesets/ + stances/ + moveset-templates/ + voices/

| Exact repo path | What it is | Size | Game | What it could wire into | Origin |
|---|---|---|---|---|---|
| `game/data/moveset-library/banks/t3.json` | Assembled move bank, Tekken 3: 4,648 moves from 20 source banks | 5,673,360 | Tekken 3 | Moveset assembler (`tools/moveset-library/ingest.mjs`) → per-fighter movesets | COMMERCIAL-DERIVED |
| `game/data/moveset-library/banks/wrestling.json` | Assembled move bank, WWF No Mercy: 4,409 moves (4,153 LP rows mapped, 256 unmapped) | 5,698,275 | WWF No Mercy | Same assembler → wrestling movesets | COMMERCIAL-DERIVED |
| `game/data/moveset-library/banks/wmxix.json` | Assembled move bank, WMXIX | 399,542 | WMXIX | Same assembler → WMXIX movesets (see verification overlay below) | COMMERCIAL-DERIVED |
| `game/data/moveset-library/banks/doa.json` | Assembled move bank, DOA | 153,678 | Dead or Alive | Same assembler | COMMERCIAL-DERIVED |
| `game/data/moveset-library/banks/vf5.json` | Assembled move bank, VF5 | 115,728 | Virtua Fighter 5 | Same assembler | COMMERCIAL-DERIVED |
| `game/data/moveset-library/banks/vf.json` | Assembled move bank, VF | 47,423 | Virtua Fighter | Same assembler | COMMERCIAL-DERIVED |
| `game/data/moveset-library/index.json` | Library index (schema v1, built 2026-10-22; banks + move counts) | 2,084 | — | Moveset assembler | JAY'S OWN |
| `game/data/moveset-library/schema.json` | Library entry JSON schema (v1, additive over the v2 moveset-editor contract) | 3,348 | — | Moveset assembler / editor | JAY'S OWN |
| `game/data/moveset-library/claimed-map.json` | MOVESET SOURCE LAW — claimed map (owner-locked 2026-10-22; movesets may only be pulled from unclaimed fighters) | 1,947 | — | Moveset assembler enforcement | JAY'S OWN |
| `game/data/moveset-library/axes.json` | Library axes data | 2,809 | — | Moveset assembler | JAY'S OWN |
| `game/data/moveset-library/wmxix-verified.json` | Verification overlay (NOT a bank edit): 169 rows, 115 wired to SHOW, 54 provisional hidden, 0 wired to combat (no bank row is a sourced gameplay grapple) | 119,607 | WMXIX | Show-only wiring; combat graduation blocked until a row is a sourced grapple with a combat input | JAY'S OWN |
| `game/data/movesets/bannon.json` | Assembled fighter moveset: Bannon → Jeffry McWild (VF5) + heavy T3/wrestling strikes | 1,462 | VF5 / T3 / wrestling | Fighter moveset | JAY'S OWN |
| `game/data/movesets/el-toro.json` | Assembled fighter moveset: El Toro | 1,303 | — | Fighter moveset | JAY'S OWN |
| `game/data/movesets/npc-finxsse.json` | Assembled fighter moveset: NPC Finxsse | 1,044 | — | Fighter moveset | JAY'S OWN |
| `game/data/movesets/pablo.json` | Assembled fighter moveset: Pablo | 3,772 | — | Fighter moveset | JAY'S OWN |
| `game/data/stances/cmu-guard.json` | Guard stance from CMU mocap subject 14 trial 01 boxing (frames 1080–1320 @120fps → 30fps) | 24,821 | — (CMU mocap) | Backup stance for rigs the Tekken bank cannot retarget onto | COMMUNITY-FREE (CMU, free for any use) |
| `game/data/moveset-templates/index.json` | Moveset template index | 4,226 | — | Moveset templates | JAY'S OWN |

### Voices — `game/data/voices/` (49 files)

Every file is an own-written voice manifest (fighter, direction, language, source game/character, clips with triggers). The manifests themselves are JAY'S OWN. The audio they point at is a mix: TekkenMods King grunts (Pantera), Eastern Mind sounds (most fighters), or placeholder subtitle-only (announcer). No announcer audio bytes exist in the repo. One file is big because it carries the full Pantera bank mapping.

| Exact repo path | What it is | Size | Game | What it could wire into | Origin |
|---|---|---|---|---|---|
| `game/data/voices/pantera.json` | Pantera voice manifest — King bank (TekkenMods mod 1242 T2 grunts preferred, mod 681 classic alternate), loudness-normalized decodes | 34,746 | Tekken (King) | `game/js/voice.js` — Pantera grunts/roars | JAY'S OWN manifest; audio source COMMERCIAL-DERIVED |
| `game/data/voices/announcer.json` | Announcer manifest — 11 clips, all placeholder, subtitle-only, audio none | 3,992 | Tekken (announcer) | `game/js/voice.js` announce() | JAY'S OWN |
| `game/data/voices/rin.json` | Rin voice manifest | 2,884 | Eastern Mind | Voice wiring | JAY'S OWN |
| `game/data/voices/retsu.json` | Retsu voice manifest | 2,544 | Eastern Mind | Voice wiring | JAY'S OWN |
| `game/data/voices/demonio.json` | Demonio voice manifest | 2,397 | Eastern Mind | Voice wiring | JAY'S OWN |
| `game/data/voices/armor-king.json` | Armor King voice manifest | 2,346 | Tekken | Voice wiring | JAY'S OWN |
| `game/data/voices/byou.json` | Byou voice manifest | 2,334 | Eastern Mind | Voice wiring | JAY'S OWN |
| `game/data/voices/gyou.json` | Gyou voice manifest | 2,295 | Eastern Mind | Voice wiring | JAY'S OWN |
| `game/data/voices/kai.json` | Kai voice manifest | 2,247 | Eastern Mind | Voice wiring | JAY'S OWN |
| `game/data/voices/sha.json` | Sha voice manifest | 2,248 | Eastern Mind | Voice wiring | JAY'S OWN |
| `game/data/voices/tou.json` | Tou voice manifest | 2,246 | Eastern Mind | Voice wiring | JAY'S OWN |
| `game/data/voices/ryuji.json` | Ryuji voice manifest | 2,212 | Eastern Mind | Voice wiring | JAY'S OWN |
| `game/data/voices/diablo.json` | Diablo voice manifest | 2,155 | Eastern Mind | Voice wiring | JAY'S OWN |
| `game/data/voices/phantom.json` | Phantom voice manifest | 2,153 | Eastern Mind | Voice wiring | JAY'S OWN |
| `game/data/voices/zen.json` | Zen voice manifest | 2,262 | Eastern Mind | Voice wiring | JAY'S OWN |
| `game/data/voices/zangief.json` | Zangief voice manifest | 2,126 | Eastern Mind | Voice wiring | JAY'S OWN |
| `game/data/voices/waterfall.json` | Waterfall voice manifest | 2,132 | Eastern Mind | Voice wiring | JAY'S OWN |
| `game/data/voices/kronos.json` | Kronos voice manifest | 2,127 | Eastern Mind | Voice wiring | JAY'S OWN |
| `game/data/voices/kinpo.json` | Kinpo voice manifest | 2,127 | Eastern Mind | Voice wiring | JAY'S OWN |
| `game/data/voices/michiko.json` | Michiko voice manifest | 2,126 | Eastern Mind | Voice wiring | JAY'S OWN |
| `game/data/voices/star.json` | Star voice manifest | 2,129 | Eastern Mind | Voice wiring | JAY'S OWN |
| `game/data/voices/deathfang.json` | Deathfang voice manifest | 2,209 | Eastern Mind | Voice wiring | JAY'S OWN |
| `game/data/voices/dio.json` | Dio voice manifest | 2,110 | Eastern Mind | Voice wiring | JAY'S OWN |
| `game/data/voices/docfrank.json` | Doc Frank voice manifest | 2,189 | Eastern Mind | Voice wiring | JAY'S OWN |
| `game/data/voices/rave.json` | Rave voice manifest | 2,197 | Eastern Mind | Voice wiring | JAY'S OWN |
| `game/data/voices/bruno.json` | Bruno voice manifest | 2,164 | Eastern Mind | Voice wiring | JAY'S OWN |
| `game/data/voices/burger.json` | Burger voice manifest | 2,134 | Eastern Mind | Voice wiring | JAY'S OWN |
| `game/data/voices/charger.json` | Charger voice manifest | 2,085 | Eastern Mind | Voice wiring | JAY'S OWN |
| `game/data/voices/cyborgx.json` | Cyborg X voice manifest | 2,178 | Eastern Mind | Voice wiring | JAY'S OWN |
| `game/data/voices/dxmmii-patchwork.json` | DXMMII Patchwork voice manifest | 2,087 | Eastern Mind | Voice wiring | JAY'S OWN |
| `game/data/voices/iori.json` | Iori voice manifest | 2,149 | Eastern Mind | Voice wiring | JAY'S OWN |
| `game/data/voices/kingtyrant.json` | King Tyrant voice manifest | 2,106 | Eastern Mind | Voice wiring | JAY'S OWN |
| `game/data/voices/koreshi.json` | Koreshi voice manifest | 2,067 | Eastern Mind | Voice wiring | JAY'S OWN |
| `game/data/voices/mariposa-monarch.json` | Mariposa Monarch voice manifest | 2,067 | Eastern Mind | Voice wiring | JAY'S OWN |
| `game/data/voices/negativo.json` | Negativo voice manifest | 2,068 | Eastern Mind | Voice wiring | JAY'S OWN |
| `game/data/voices/nightwolf.json` | Nightwolf voice manifest | 2,117 | Eastern Mind | Voice wiring | JAY'S OWN |
| `game/data/voices/purplerain.json` | Purple Rain voice manifest | 2,113 | Eastern Mind | Voice wiring | JAY'S OWN |
| `game/data/voices/sakura.json` | Sakura voice manifest | 2,096 | Eastern Mind | Voice wiring | JAY'S OWN |
| `game/data/voices/samura1.json` | Sam Ur A1 voice manifest | 2,096 | Eastern Mind | Voice wiring | JAY'S OWN |
| `game/data/voices/scimitar.json` | Scimitar voice manifest | 2,076 | Eastern Mind | Voice wiring | JAY'S OWN |
| `game/data/voices/skull.json` | Skull voice manifest | 2,118 | Eastern Mind | Voice wiring | JAY'S OWN |
| `game/data/voices/slice.json` | Slice voice manifest | 2,119 | Eastern Mind | Voice wiring | JAY'S OWN |
| `game/data/voices/thor.json` | Thor voice manifest | 2,055 | Eastern Mind | Voice wiring | JAY'S OWN |
| `game/data/voices/torch.json` | Torch voice manifest | 2,098 | Eastern Mind | Voice wiring | JAY'S OWN |
| `game/data/voices/vega.json` | Vega voice manifest | 2,075 | Eastern Mind | Voice wiring | JAY'S OWN |
| `game/data/voices/awapop.json` | Awa Pop voice manifest | 2,101 | Eastern Mind | Voice wiring | JAY'S OWN |
| `game/data/voices/baek-master-white.json` | Baek Master White voice manifest | 2,108 | Eastern Mind | Voice wiring | JAY'S OWN |
| `game/data/voices/yukihyo.json` | Yukihyo voice manifest | 2,037 | Eastern Mind | Voice wiring | JAY'S OWN |
| `game/data/voices/zui.json` | Zui voice manifest | 2,097 | Eastern Mind | Voice wiring | JAY'S OWN |

---

## Still UNMEASURED (could not be inspected in this pass)

- **The recursive git-tree was truncated** (`truncated: true` at 60,859 entries). It is missing whole subtrees that direct directory listings prove exist (`teardown/wwf-no-mercy/arenas/`, `models/`, `textures/` contents, `teardown/yakuza-kiwami/README.md`). Totals in this file are floors. Any folder whose count comes only from the tree could be undercounted; rows verified by direct listing say so.
- `teardown/tekken3/WIRING-INVENTORY.md` (3,426,201 B), `teardown/eastern-mind/WIRING-INVENTORY.md` (2,338,665 B), `teardown/wwf-no-mercy/WIRING-INVENTORY.md` (2,610,726 B) — read tool cannot return files this big in full; sizes counted, contents not read (eastern-mind's head was read in the re-run).
- Deep contents (listed as folders, files inside not opened): `teardown/tekken3/models/` (13 of 15 fighter dirs), `teardown/tekken3/stages/` (14 of 15), `teardown/tekken3/ui/`, `teardown/tekken3/renders/`, `teardown/tekken7/king/pantera/`, `teardown/tekken7/king/views/`, `teardown/tekken7/models/king-variants/`, `teardown/tekken7/tekkenmods-docs/`, `teardown/tekken8/ui/refs/`, `teardown/urban-reign/` models/textures/ppks/missions/animations/sound/ui/vgs subdirs, `teardown/wmxix/wrestlers/` (127 files) + `textures/` (1,169 PNGs + 176 JSONs) contents, `teardown/wwf-no-mercy/models/` + `textures/` subdir contents, `teardown/dead-or-alive-4/models/` subdirs + `movesets/`, `teardown/virtua-fighter-5/models/` + `docs/` archives, `teardown/models/tekken7/` (4 zips — names + sizes known, contents not unpacked), `teardown/def-jam-fight-for-ny/` subdirs, `teardown/tekken6/stages/slice/` + `models/parts/` segment contents, `teardown/soulcalibur-2/models-textured/` variant subdirs, `teardown/tekken-tag-tournament-2/extracted-small/` (13 files, contents unknown), `teardown/tekken7/arenas/` (.rar contents unknown).
- `game/data/moveset-templates/index.json` — listing confirmed it exists (4,226 B); head content was not returned by the read tool in the first attempt (contents since confirmed by the re-run head read: schema `wh.moveset-template.v1`, WH character ids only).
- Devil Within: the `.dat` files themselves (motion bytes, stage geometry, boss data) are not in the repo at all — only their names in the T5 manifest. Decoding them is RE-bench work, not inventory work.
- Licences not checked: `teardown/tekken3/tools/psxrecomp/` (1,566 files, described as open-source, licence file not read); `teardown/tekken7/tekkenmods-docs/` tools (QuickBMS/UnrealPak licences); `teardown/community/tekken8/movesets/kaiutzi21/LICENSE.txt` (present, terms not read); `teardown/virtua-fighter-5/docs/MikuMikuModel.7z` (third-party tool archive).
- No live-load check: nothing in this inventory was loaded in the game or a browser — "wireable" means the format and the existing wiring path allow it, not that it was seen running.

## The 5 biggest / most useful items

1. **`teardown/tekken3/movesets/moveset_king.json` (3,409,137 B) + the whole `teardown/tekken3/movesets/` set (~28 MB, 21 fighters, 3,247 moves)** — the most complete move tables in the repo; already in the shape the web build consumes. COMMERCIAL-DERIVED (Tekken 3).
2. **`game/data/moveset-library/banks/t3.json` (5,673,360 B, 4,648 moves) + `banks/wrestling.json` (5,698,275 B, 4,409 moves)** — the assembled banks the moveset assembler reads; the fastest route to wiring new fighters. COMMERCIAL-DERIVED (assembled from Tekken 3 / No Mercy teardown data).
3. **`teardown/soulcalibur-2/stages/` (41 GLBs, biggest `stage_m000.glb` 27,752,736 B) + `models-textured/` (105 GLBs, 115.9 MB) + `models/`/`models-skinned/` (22 GLBs each)** — the biggest ready-made stage + textured-fighter set in the repo; GLBs drop straight into a Three.js build. COMMERCIAL-DERIVED (Soulcalibur II).
4. **`game/data/t7-frame-data/` (44 files, 5,648 base moves + DLC 9) + `game/data/t8_frame_tables.json` (326,507 B, 41 chars / 6,284 moves, CC0)** — the frame-data layer the fight loop already runs on; T8 tables are the only CC0-cleared frame data in the set. COMMERCIAL-DERIVED (T7, licence flags unresolved) / COMMUNITY-FREE (T8, CC0).
5. **`teardown/wwf-no-mercy/arenas/` (17 named arenas, OBJ + VC pairs) + the AKI animation bank (docs claim ~1,360 clips) + `aki_to_tekken3_v1/v2.json` retarget maps** — the only complete arena set plus a proven retarget path onto Tekken skeletons; the CAW tables (50 entrance-music entries, 15 part-string categories) are the Create Fighter source. COMMERCIAL-DERIVED (No Mercy) + JAY'S OWN retarget maps.

## Method note

Counts come from GitHub directory listings plus, in the re-run, the recursive git-tree at HEAD `3334ebf` (≥38,811 teardown blobs, 4.05 GB; the tree was truncated so totals are floors) and direct-listing spot checks that proved whole subtrees missing from the tree. Per-file origin was assigned from the folder + the file's own stated source, not by opening every file. Where a folder's own docs give a bigger claimed count than the listing showed (No Mercy anims), the doc's number is quoted as claimed, not verified. Nothing in this file is a licence clearance.
