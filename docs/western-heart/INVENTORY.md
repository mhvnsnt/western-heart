# Western Heart — Asset & Teardown Inventory (Oct 14, 2026)

Inventory only: no engine changes. Machine-readable data: `inventory.json`. Read alongside
`mhvnsnt/money-machine-hq` `docs/western-heart-audit.md` (MoneyManBusch). This inventory confirms that audit's findings.

Note: Western Heart is a **chimera fighting game** (Tekken 7 base + Tekken 3 legacy + Eastern Mind world + Urban Reign/No Mercy/WMXIX systems), per CHIMERA-BUILD.md. It is not a western/RDR game.

## Repos inventoried (cloned to /workspace/western-heart-inventory, depth 50, LFS smudge off)
| Repo | Size on disk | Role |
|---|---|---|
| western-heart | 2.5 GB (≈1.46 GB teardown/) | Game + teardowns + narrative |
| game-reverse-engineering | 458 MB | Earlier/duplicate T3, T7, No Mercy teardowns + tools |
| wrestling-game | 662 MB | Def Jam: Fight for NY teardown (371 MB, 9.8k files). Wrestlers split here on Oct 13 |
| wwe-wrestler-models | 28 MB | No Mercy (5,401 files) + WMXIX (127) wrestler OBJ dumps + converters |
| BrutalfistbaseofTekken3Recompiled | 361 MB | Tekken 3 PSX recompiler (psxrecomp), launcher, mod system, 169 MB mod assets |
| steal-like-artist-archive | README only | Empty study archive |
Not cloned (ROM storage, noted only): chimera-roms (2.4 GB), chimera-rom-nomercy, drive-storage, google-drive-repo.

## western-heart contents
| Group | Files | Size | Notes |
|---|---|---|---|
| teardown/urban-reign | 2,032 | 970 MB | PS2 .ppk/.p3d/.pbd/.bin; bone translation WIP |
| teardown/tekken3 | 19,426 | 205 MB | 8,567 .tim + 8,835 png, models (27-part rigid, unskinned), movesets, recomp tools |
| teardown/wwf-no-mercy | 18,557 | 105 MB | 3,587 OBJ+.vc, 5,787 .npy, 13 unskinned GLB wrestlers + 2 menu scenes, recomp |
| teardown/models | 9 | 105 MB | 4 zips (incl. T7 steve-fox-t7-fbx.zip) |
| teardown/wmxix | 1,551 | 63 MB | 166 OBJ, 1,191 png, arenas, CAW parts, animations |
| teardown/tekken7 | 164 | 44 MB | Docs, tekkenmods-docs, UModel; game files NOT pulled (47 GB blocked) |
| teardown/tekken6, ttt2, vf5 | 76 | 15 MB | Videos/frames, small extracts, 7z |
| teardown/doa6, sc2, sc6, sf5, sfex2+, def-jam, sf3d | docs only | <1 MB | Plans/notes only |
| customization/ | 3,740 | 75 MB | WMXIX/No Mercy CAW .tex/.ymg/.vc parts, create-fighter page (Soldier.glb, Mixamo, 49 joints) |
| roster/ | 97 | 37 MB | Pantera rig work (pantera_body.glb 18 meshes unskinned; pantera_rigged.glb 13 joints) |
| assets/free-pull-1 | 90 | 101 MB | 16 CMU BVH, tk-fighting-game template, 6 .usdc |
| game/ | ~60 | 35 MB | Playable build (below) |
| Narrative/design docs | 458 .md | 4.8 MB | MISSION, CANON, ROSTER, CHIMERA-ARCHITECTURE, DESIGN, GAME-DEV-BRIEFING, teardown/western-heart-design, docs/production-study |
| moveset-library | 8 | 0.7 MB | Move JSON + docs |

GLB census: 24 total; only 5 skinned (pantera/demonio/Soldier: 49 Mixamo joints with 4 clips Idle/Run/TPose/Walk; two pantera_rigged at 13 joints), 0 with fighting animations. No LFS pointers. Empty files: TEKKEN3.DA, TEKKEN3.DMY (disc dummies), No Mercy recomp `skip_functions.txt` and `reloc_addrs.txt` (may break the recomp build), 2 .gitkeep.

GitHub Releases (17): full ISOs/archives (Tekken 3, Tekken 6 PSP, TTT2, Urban Reign, WMXIX, No Mercy, VF5, SC2, DOA4, SF EX2+, Eastern Mind) plus model batches.

## How the current build loads assets
- Entry: `game/index.html` (importmap → `vendor/three.module.js`, vendored addons) → `js/main.js`. Static, no build step, GitHub Pages serves `game/`.
- `js/assets.js`: `GLTFLoader` loads only `assets/models/pantera.glb` (7 MB) and `demonio.glb` (23 MB, Tekken 7 Steve Fox body). Prefetch happens on character select.
- `js/fighter.js`: `fetch('assets/{king,jin,bryan,heihachi,xiaoyu,yoshimitsu,gunjack}_moves.json')`, the Tekken 3 move data. All 7 are present.
- `js/roster-full.js`: 36 fighters, each mapped to one of the 2 models plus a tint.
- Portraits: `<img>` 36 png. Audio: fully procedural Web Audio, so no audio files ship.
- Animation: Mixamo Idle/Walk/Run plus a CCD IK strike layer. No extracted game animations play.
- **Unused at runtime:** everything outside `game/`, which is ≈99% of the repo (the teardowns, CAW parts, roster rigs, BVH, Urban Reign/No Mercy/WMXIX data). There is no stage loader, so the stage is procedural.
- Headless run (Chrome + SwiftShader, `python3 -m http.server`): the title screen renders (ARCADE/VERSUS/STORY/CREATE FIGHTER/HOW TO PLAY). See `headless-boot.png`. A match was not driven headlessly.
- CI: none (`.github/workflows` absent).

## License / provenance classes
| Group | Class | Risk |
|---|---|---|
| Release ISOs/archives | third-party commercial, full game images | **CRITICAL: public redistribution** |
| teardown/*, customization parts, wwe-wrestler-models, wrestling-game, game-reverse-engineering extracts | third-party ripped (Namco, THQ/Yuke's, EA, Sega, Koei, Capcom, Osamu Sato) | **Commercial-release blocker** |
| game/assets/models/*.glb | ripped mesh (T7) + Mixamo rig/anims | **Blocker**: replace before sale |
| game/assets/*_moves.json | derived from T3 data | Risky: re-author as original frame data |
| game/js, docs, narrative, owner names | original | OK |
| vendor three.js | MIT | OK |
| CMU BVH | free-use mocap | OK (credit) |
| portraits, usdc, misc jpg, BrutalFist mods/assets | unknown | Verify |

## Biggest gaps
1. There's no bridge from the teardown to the runtime: no TMD/TIM, PPK, or No Mercy → glTF importer that outputs a common skeleton.
2. There's no canonical rig or retarget tables. Tekken 3 is rigid with 27 parts, No Mercy/WMXIX are OBJ dumps, and Urban Reign bones are still WIP.
3. There are no stages or extracted animations in the game. The move JSONs exist but there is no move-table interpreter.
4. Duplicate teardowns across western-heart, game-reverse-engineering and wwe-wrestler-models. Wrestlers are still in western-heart despite the Oct 13 split directive.
5. Legal: the public repo and its Releases host commercial ISOs. Recommend making them private or BYO-files (see the audit). Nothing should be deleted.

## Update (Oct 14): Lab assets
- `lab/source_assets/original/pantera_leoman_original.glb` and `bannon_mask_original.glb`: **ORIGINAL (owner-made)**, from Drive and untouched.
  - Rig state on arrival: both were unrigged Tripo exports (meshopt + quantized, ~1M verts, 3 textures).
- `lab/game/assets/t3_king.glb` and `t3_stage_l.glb`: third-party (Namco), from the owner's own disc. **Private Lab only.**
- Rig-check findings in other assets:
  - `game/assets/models/pantera.glb`: FAIL. The Idle clip is cm-scale on a meter rig (×21 stretch, 8 m sink).
  - brutalfist `BANNON_rigged.glb`: FAIL. Its bind matrices don't match its skeleton.
