# Teardown Fighter Inventory — Master Per-Game → Per-Fighter Asset List

**Worker 49 — 2026-10-22.** One inventory of EVERY teardown game with usable fighter data:
per fighter — movesets (format + location), animations (format + location), voice files, audio
files, models, textures. "Usable" = extraction has produced real per-fighter assets (or a
documented manifest of them). Games with only plans/catalogs are marked as such.

**Cross-links:** worker 47's moveset library should ingest this inventory (linkage noted;
their lane files untouched). Worker 48's canon bridges draw on
`docs/research/bannon-universe-canon-package-2026-10-22.md`. Coverage scores grounded on
`teardown/TEARDOWN-COVERAGE-MATRIX.md` (regenerated 2026-10-22) and
`teardown/TEARDOWN-STATUS.md` (2026-10-13).

**Location key:** paths are repo-relative to `mhvnsnt/western-heart` unless marked otherwise.
`~/workspace/game-reverse-engineering/` = local RE bench. Releases = github.com/mhvnsnt/western-heart/releases.

---

## 1. Tekken 3 (PS1) — 100% ✅

20 fighter animation banks + full movesets + models + textures + stages + audio.

**Movesets** — per-fighter JSON, `tools/moveset-decode/` lane + `game/assets/movesets/t3-*.json`:
t3-anna, t3-bosconovitch, t3-eddy, t3-forestlaw, t3-gon, t3-hwoarang, t3-julia, t3-kuma,
t3-law, t3-lei, t3-nina, t3-ogre, t3-paul (+ 3,247 decoded T3 moves total; generator
`tools/gen-movesets-t3.py` merged bank depth over 61 per-fighter files).

**Animations** — `teardown/tekken3/animations/divmotNN_<fighter>.bin` (raw motion banks):
divmot00_paul, 01_law, 02_lei, 03_king, 04_yoshimitsu, 05_nina, 06_hwoarang, 07_xiaoyu,
08_eddy, 09_jin, 10_julia, 11_kuma, 12_bryan, 13_heihachi, 14_ogre, 16_gunjack, 17_anna,
18_bosconovitch, 19_gon, 20_forestlaw, 99_common. Decoded via `t3_row_bake.py`/`t3anims.js`;
retarget stage under `tools/`.

**Models** — `teardown/tekken3/BODY-EXTRACTION.json`; 7 fighters geometry-mapped (King fully
extracted); `tools/anim/t3_extract_bodies.py` (KMD bodies). ~1K tris/fighter, 20–27 rigid
parts (no skinning — "clay pieces on a wire skeleton"), 32×32 textures.

**Textures** — 8,556 TIM-decoded textures (100%).

**Stages** — 15. **Audio** — 100%.

**Per-fighter table (20):** Paul Phoenix, Marshall Law (as Forest Law bank), Lei Wulong, King,
Yoshimitsu, Nina Williams, Hwoarang, Ling Xiaoyu, Eddy Gordo, Jin Kazama, Julia Chang, Kuma,
Bryan Fury, Heihachi Mishima, Ogre, Gun Jack, Anna Williams, Dr. Bosconovitch, Gon,
Forest Law — each with: moveset JSON (format: WH moveset schema, decoded from T3 banks),
anim bank (divmot .bin), model (KMD via t3_extract_bodies.py), textures (TIM set), audio.

---

## 2. Tekken 7 (PS4/PC) — ~40%

**Movesets** — frame data: 47 characters × 11,137 rows (`tools/fetch_t7chicken_framedata.py`).
Format: community frame-data tables (not extracted move binaries). TKMovesets decode lane ready
(`tools/moveset-decode/`) — extractor exists, needs data.

**Animations** — via TKMovesets path only where extracted (~30%).

**Models** — King ONLY: 5 variants with exact poly counts — T8 base 50,950p · T8 S2 43,462p ·
T3 legacy 66,052t · T7 1P 54,612t · Armor King 48,870p (`teardown/tekken7/king/`:
`5PMH7G85GYN7P71W3BD1V0249.fbx` + D/N/S texture sets). Other fighters rely on
rigmodels/DeviantArt pulls. Full 51GB game never acquired.

**Textures** — King D/N/S sets (~20%). **Stages** — Mishima Dojo only (~10%).
**Audio** — 0%.

**Roster reference** — `teardown/tekken7/TEKKEN7-ROSTER-MAPPING.md` (51 fighters with T3
overlap + WH names): Paul, Law, King→Pantera, Yoshimitsu→Phantom, Hwoarang, Xiaoyu→Saku-ra,
Jin→Demonio, Bryan→Skull, Heihachi→Diablo, Kazuya, Steve, Jack-7→SAM-UR-A1, Asuka, Devil Jin,
Feng, Lili, Dragunov, Leo, Lars, Alisa, Claudio, Katarina, Lucky Chloe, Shaheen, Josie, Gigas,
Kazumi, Nina, Master Raven, Lee, Bob, Akuma, Kuma, Panda, Eddy, Eliza, Miguel, Geese, Noctis,
Anna, Lei, Marduk, Armor King, Julia, Negan, Zafina, Ganryu, Leroy, Fahkumram, Kunimitsu, Lidia.

**Per-fighter usable now:** frame-data rows for 47 fighters (reference-grade); full asset
sets (model/anim/moveset binary) ONLY for King + Armor King.

---

## 3. Tekken 6 (PSP) — ~30%

**Roster** — 40 fighters mapped (no per-fighter moves). **Models** — NDPP bounding volumes only
(`teardown/tekken6/models/NDPP-FORMAT.md`, `ndpp_bounding_volumes.glb`); DATA401.IDX + 384MB
region encrypted (AES-level, entropy 7.99/8). EBOOT.BIN decrypted via KIRK (valid 4MB ELF;
`packdatas_t`/`ReadInfo`/`ktRead`/`openPac` symbols confirmed). **Animations** — motion data
locked in DATA401. **Videos** — 46 endings extracted. **Audio** — ~30%.

**Per-fighter:** roster list only (40 names mapped); no per-fighter models/anims/movesets until
DATA401 key recovery (MIPS RE or PPSSPP live-dump — see `teardown/tekken6/PPSSPP-LIVE-RUN-GUIDE.md`).

---

## 4. Tekken Tag Tournament 2 (X360) — ~15%

**Roster** — `teardown/tekken-tag-tournament-2/ROSTER.md`: 60 names (59 console + Dr. Bosconovitch):
Alex, Alisa, Ancient Ogre, Angel, Anna, Armor King, Asuka, Baek, Bob, Bruce, Bryan, Christie,
Combot, Marduk, Devil Jin, Dr. Bosconovitch, Dragunov, Eddy, Feng, Forest Law, Ganryu, Heihachi,
Hwoarang, Jack-6, Jaycee, Jin, Jinpachi, Julia, Jun, Kazuya, King, Kuma, Kunimitsu, Lars, Lee,
Lei, Leo, Lili, Marshall Law, Michelle, Miguel, Miharu, Mokujin, Nina, True Ogre, Panda, Paul,
Prototype Jack, Raven, Roger Jr., Sebastian, Slim Bob, Steve, Tiger Jackson, Unknown, Violet,
Wang, Xiaoyu, Yoshimitsu, Zafina. **Documented from public data, NOT extracted** — lives inside
encrypted STFS chunks. **Stages** — 29 documented, none extracted. **Models/Anims/Movesets/Audio** — 0%.

**Per-fighter:** name list only. TKMovesets supports TTT2 gameId 2 — extractor ready when data lands.

---

## 5. Tekken 8 (PC) — ~10%

Binary not acquired. **Movesets (reference)** — wavu frame data: 41 characters / 6,284 moves
(reference tables, not extraction). **Models** — King T8 base/S2 pulled as reference only.
Per-fighter: reference-grade frame data; no extracted assets.

---

## 6. Virtua Fighter 5 (PS3) — 100% ✅

**19 fighters** — Akira Yuki, Pai Chan, Lau Chan, Wolf Hawkfield, Jeffry McWild, Kage-Maru,
Sarah Bryant, Jacky Bryant, Shun Di, Lion Rafale, Aoi Umenokouji, Lei-Fei, Vanessa Lewis,
Brad Burns, Goh Hinogami, Eileen, El Blaze, Dural (boss), + Jean Kujo & Taka-Arashi (FS).

**Models** — on release `vf5-ps3-v1` / `vf5-model-library-v1` (1.3GB, 108 files):
- `vf5-models-a.tar` (394MB): lau, wol, jef, jak, aoi, lio, bra, shu (8 fighters)
- `vf5-models-b.tar` (386MB): lei, msk, kag, goh, van, sar, mon, pai, aki, dur, akixx,
  common (11 + common)
- FARC archives + `teardown/virtua-fighter-5/tools/farc_extract.py`; `VF5-MODELS-MANIFEST.md`.
- Manifest note: `msk`/`mon` = Eileen/El Blaze archives (verify on extract).

**Animations** — 100% decoded banks. **Movesets** — 100% (VF5 movelists; mechanics doc
`teardown/virtua-fighter-5/docs/VF5-MECHANICS.md`). **Stages** — 38 (`vf5-stages.tar`, 462MB).
**Audio** — 100%. **Customization/moveset RE** — queued.

**Per-fighter:** full model + anim + moveset + audio for all 19. VF5 is the richest
non-Tekken fighter source. NOTE (owner, 2026-10-22): VF5 MOTION DATA NEVER CONVERTED —
model only; motion extraction is the crew's lane (blocks the Zen/Twelve-style conversion work).

---

## 7. Dead or Alive 4 (X360) — ~15%

**Models** — 105 vertex buffers carved from chrone.afs (21) / chrtwo.afs (25) / chrthree.afs (39)
character models + mot.afs (2) + stg.afs (18 stage); format decoded (20B/vertex big-endian
float3 pos + float2 UV) but **index buffers undecoded — point clouds, not meshes**; fighter
identities unmapped. **Textures** — 219 XPR2 carved. **Movesets** — `teardown/dead-or-alive-4/movesets/bass-armstrong/BASS-MOVELIST.md`
(Bass Armstrong, full movelist doc — wired in-game as `vainabel`/`doa-bass`).
**Animations/Audio/Stages** — 0% extracted (30/30 ISO chunks on release `doa4-iso-v1`,
reassembly sequenced after TTT2; ~16GB disk needed).

**Per-fighter:** Bass Armstrong = full movelist doc (only DOA4 fighter with usable moveset);
all others = unidentified vertex point clouds.

## 8. Dead or Alive 6 (PC) — ~10%

Mechanics doc only (`teardown/dead-or-alive-6/`, `teardown__dead-or-alive-6__DOA6-MECHANICS.md`).
50GB+ binary not acquired. No per-fighter assets. In-game: `doa-kasumi`, `doa-hayabusa`,
`doa-jannlee`, `doa-tina`, `doa-ayane` moveset files built from community movelists + frame data
(`game/assets/movesets/doa-*.json`; REAL-THIN status).

---

## 9. Soulcalibur II (Xbox) — ~60%

**Movesets** — 24 moveset files from `root.olk` v33 (@0x1000); each = one fighter's full command
list (internal IDs, input notation, English move names). **Identified (18):** Mitsurugi (01),
Seong Mi-na (02), Taki (03), Maxi (04), Voldo (05), Sophitia (06), Ivy (0b), Kilik (0c),
Xianghua (0d), Yoshimitsu (0f), Nightmare (11), Astaroth (12), Cervantes (14), Raphael (15),
Talim (16), Cassandra (17), Necrid (19), Yun-seong (1a), Link (1b, GC guest — data present),
Heihachi (1c, PS2 guest — data present), Spawn (1d, Xbox guest). **Unidentified:** slots
1e/1f/20 (command data only); Siegfried, Rock, Lizardman, Assassin, Berserker, Charade likely
among them. `teardown/soulcalibur-2/CHARACTER-MAP.md`; tools `dl_olk.py`/`Olk_extract.py`.
WH rename: all PENDING owner assignment.

**Models/Anims** — ~70/60% (Xbox extracted); **Audio/Textures/Stages** — ~60%.
**Per-fighter:** 21 named fighters with full command-list movesets — the only SC source with
per-fighter move data.

## 10. Soulcalibur VI (PC) — ~10%

Mechanics doc only (`teardown/soulcalibur-6/`, SCVI-MECHANICS.md). 32GB binary not acquired.
No per-fighter assets.

---

## 11. Street Fighter EX2 Plus (PS1) — cataloged

**Models/moves** — 19 player overlay slots: `data/OVL/PL00_1.OVL`–`PL12_1.OVL` (hex 00–12;
iso-file-listing.txt, 403 entries). **Fighter identities UNMAPPED** (no name table found in
this dump — slot→fighter mapping pending). Known EX2+ roster (public): Ryu, Ken, Chun-Li,
Guile, Zangief, Dhalsim, Blanka, Vega, Sagat, Bison, Sakura, Skullomania, Doctrine Dark,
Cracker Jack, Sharon, Area, Kairi, Hayate, Nanase, Garuda, Shadow Geist, Hokuto/Bloody Hokuto.
Extraction lane: `~/workspace/game-reverse-engineering/street-fighter-3d-games/extracted/ex2-plus/`.

**Per-fighter:** 19 unnamed OVL slots (model+move data per slot, names TBD).

## 12. Street Fighter EX Plus Alpha (PS1) — roster-mapped ✅

**Roster (23, verbatim from `SLUS_005.48` name table @~705572):**
SAKURA, DHALSIM, BETA (Cycloid-β), GAMMA (Cycloid-γ), AKUMA, GOUKI (boss/alt Akuma),
ZANGIEF, CHUN-LI, KEN, RYU, GARUDA, M.BISON, VEGA, GUILE, C.JACK (Cracker Jack),
ALLEN (Snider), SKULLO (Skullomania), BLAIR (Dame), PULLUM (Purna), D.DARK (Doctrine Dark),
DARUN (Mister), HOKUTO, KAIRI.
`teardown/street-fighter-ex-plus-alpha/street-fighter-ex-plus-alpha/character-roster.md`.
WH names: PENDING owner assignment.

**Per-fighter assets:** `data/OVL/PLxx_1.OVL` + `data/OVL2/PLxx_2.OVL` (xx = hex slot 00–19);
`move-names.txt` (165 move names, verbatim from binary). Model+move data present per slot;
NMD model extraction (`/PLNMD/`) still open.

---

## 13. Urban Reign (PS2) — ~95% ✅

**Fighters** — 60+ playable (boxing, wrestling, karate, brawling, capoeira, kung fu styles);
~30 special moves + ~50 double-team attacks each. **Models** — 72 fighter PPKs
`ppks/chars/char001–char072` (44MB); **fighter names ABSENT from data** (float-heavy identity
quats, no ASCII names). **Animations** — 46 motion packs (`animations/motion-packs/*.ppk`).
**Audio** — 1,033 files extracted (`teardown/urban-reign/audio/`). **UI** — 72 screens.
**Tekken guests:** Paul + Law (Tekken 5-era models — alt-model/reference material for WH's
existing Paul/Law bases).

**Per-fighter:** char001–char072 slots with full geometry + motion-pack anims + audio, but
identities unmapped. VGS/PPK/DCM formats documented (`VGS-FORMAT.md`, `PPK-FORMAT.md`,
`PPK-GEOMETRY.md`); AFS offset maps (`afs-map/dvd000_afs_map.json`).

---

## 14. WWF No Mercy (N64) — 100% ✅

**Roster** — 42 wrestler ID entries (`0x168D930`, IDs 0–43, gaps at 5/37; name→ID map in
`wwf-no-mercy/docs/wrestler-id-table.json` @ `~/workspace/game-reverse-engineering/`).

**Movesets** — move data segment @ `0x13E000`: u32 move-attribute records + float table +
N64 RAM pointer table + 15KB u16 index run (7,565 entries, move-index→data-index remap);
move menu entries carry `AnimID` = fileID − `0x3322`.

**Animations** — KEYFRAME BANK: FileTable @ `0x16C3238` (19,462 entries);
**AkiAnimation format** = 4-byte Toki2 + N×98-byte frames (19× PivotRotation: 12-bit pivot X,
s8 rotation, 12-bit pivot Z + OverallMovementXYZ + 6× MovementXYZ; fixed joint order
pelvis→arms); ~1,360 clips, 1–123 frames; `tools/anim_extract.py`. 5,787 anims total.

**Models** — 3,570. **Textures** — 5,029. **Stages** — 17 (wired in-game:
`game/assets/stages/no-mercy/`). **Audio** — 100%.

**CAW system (ROM-verified, directly reusable):** entrance-music table @ `0x168D790`
(50 entries); part-string regions @ `0x168DD89`+ (15 categories: body types, elbow pads,
masks, entrance attire, gloves, feet, wrists, hair, front hair, facial hair, hats, knee
pads, accessories, ring attire) — `caw_parse.py` regenerates the JSON maps.

**Per-fighter:** all 42 with full anim/move/model/audio. The AKI 19-joint clips retarget
onto Tekken skeletons (`AKI-TEKKEN3-RETARGET.md`; `aki_to_tekken3_v2.py`).

---

## 15. WWE WrestleMania XIX (GC) — ~80%

**Model slots** — 108 (numbered 000–110, some unused); 484 files (`_0` = base tex+ymg+ycg;
`_1` alt attire on 67 slots; `_2` on 22; `_3` on 5); alt attires are **texture-only**
(`_0.ymg` == `_1.ymg` byte-identical); universal 70-bone skeleton (`WRESTLER-SKELETON.md`).
**Identity: PENDING owner visual ID** — only slot 000 = **Triple H** confirmed (hhh_ textures);
~45 playable + 20 Revenge bosses + 4 NPCs ≈ 69 named; extras = CAW parts/managers/divas/dupes.

**Animations** — 170 YANM anims (`teardown/wmxix/YANM-*.md` — F32 correction, item cycles);
**motion codes indexed by name table:** `//menu/menu.mpq` = per-wrestler profile blocks with
**99 named specials across 45 wrestlers** (e.g. The Rock: Rock Bottom [Front Grapple],
People's Elbow [Upper Down Grapple Facing Up], People's Spine Buster [Irish Whip Grapple]);
`//Entrance/EMotName.dat` = 177 code→name pairs (A002=ROCK, C000=ROCK, D105=ROCK_01…).
**THE ROCK IDENTIFIED:** `ML-A002-0A` (entrance, `ringmotion/a002_0a.yag`) + `ML-C000-0A`
(trio/stable variant) — decoded and in the library.

**CAW** — 2,690 parts (`edit_data/`). **Arenas** — Revenge Mode arenas doc'd. **Audio/UI** — ~85%.

**Per-fighter:** 45 named wrestlers identifiable via menu.mpq special-move blocks + EMotName
codes once the owner assigns slot→identity (mat-legends worksheet). Until then: code-indexed
clips, not name-indexed.

---

## 16. WWE 2K series — catalog only

`teardown/wwe-2k/CATALOG.md`: 2K14 (1.26GB) → 2K23 (84.48GB) verified on Archive.org;
**nothing downloaded**. Mod packs of interest: "Ported Moves & Animations (2K15–2K20)"
0.12GB; "Ported Entrance & Victory Motions (2K20+)" 0.57GB. Acquisition plan: issue #253.
No per-fighter assets yet.

---

## 17. Def Jam: Fight for NY (PS2) — assessed ✅

**Fighters** — `FIGHTER.XML`: **142 fighter entries** (name → model `V2IP_xxx`, style
STF/MAR/WRE/SUB/KIC, bodysize, speechID) incl. CAW/story variants; `CHARS.XML` select metadata.
**Models** — `V2IP.VIV` (28.3MB, 234 entries): **78 fighter model sets** (`teardown/def-jam-fight-for-ny/models/fighters/`,
78× `.ssh`+`.o`+`_F.o`); each = 3 files; bosses/alts in `V2IP_4xx/5xx/126B`; CAW parts
`V2CP_xxx_xxxx_A01_01.ssh` (from-scratch builder parts federate as a system).
**Animations** — `MOTION/WRES_ALL.VIV` (64MB): `wresNNN` sets; one shared grappling core,
5 style skins (STF dirty brawling / MAR acrobatic / WRE pure AKI slams / KIC knees-elbows /
SUB submissions). `COMBS.XML` combo chains. BLAZIN' momentum system.
**Voice/audio** — speechID per fighter in FIGHTER.XML; `.orl` track decode (triplet structure).

**Per-fighter:** 142 XML entries → 78 base models; style + voice + combo data per entry.
AKI wrestling lineage (Def Jam Vendetta) — grappling-system reference for WH.

---

## 18. Bloody Roar — NOT LANDED

No Bloody Roar teardown exists in the repo or the audit bench as of 2026-10-22. When it
lands, inventory per fighter: beast-form transformation data (the series' signature system),
movesets, models (human + beast), audio. (Owner-listed in the round scope; acquisition open.)

## 19. Eastern Mind (PC-98/Mac/Win) — NOT A FIGHTER SOURCE

Osamu Sato's *Eastern Mind: The Lost Souls of Tong-Nou* is an adventure game — no fighters.
Teardown (100%: 5,321 bitmaps, 229 sounds, 3 CD tracks, 22 videos, 31 text resources,
48 palettes) feeds WH **canon/stages/audio** (the Nine Incarnations, Tong-Nou lands), not the
fighter inventory. Listed here only because the round scope names it.

---

## 20. Wrestling CAW part libraries (creation-suite feed)

- **No Mercy:** 15 part categories (body types, elbow pads, masks, entrance attire, gloves,
  feet, wrists, hair, front hair, facial hair, hats, knee pads, accessories, ring attire),
  ROM-verified id→name maps — `game-reverse-engineering/wwf-no-mercy/docs/`.
- **WMXIX:** 2,690 CAW parts (`edit_data/`) — `teardown/wwe-wrestlemania-xix/CAW-EDIT-DATA-WMXIX.md`.
- Both feed the unified creation suite per the tool-wiring/unification laws (never separate islands).

---

## How the unmapped Ashlane 28 pick from this inventory

Unmapped: Triple XXX, Echo, Hollow, Static, Stickup, Onyx, Tyneshia, Maime, Edwin Kennedy,
Hall Nighter, Stan Combs, Kobra, Viper, Brutus, Wreck Patterson (+ more). Locked: Bannon→Jeffry
(VF5), El Toro de Oro→Wolf (VF5), Pablo→El Blaze (VF5), Finxsse→Lei-Fei (VF5); candidates:
Master Sensei→Lau, Sombra Negra→Kage, Cipher→Goh, Aaron Ruben→Akira, Cody→Jacky, Jager→Vanessa.

**Best per-fighter sources to map from (richest first):**
1. **VF5 §6** — 19 fighters, full model+anim+moveset+audio. Remaining unmapped VF5: Akira,
   Sarah, Shun, Lion, Aoi, Lei-Fei (candidate: Finxsse), Brad, Eileen, Dural, Jean, Taka.
2. **Tekken 3 §1** — 20 fighters, full banks (3,247 moves). Unused T3 banks: Paul, Law,
   Nina, Hwoarang, Xiaoyu, Julia, Kuma, Bryan, Ogre, Anna, Bosconovitch, Gon, Forest Law.
3. **SC2 §9** — 21 named fighters with full command lists (weapons-based; fits Kobra/Viper
   weapon-user concepts).
4. **TTT2 §4 / T7 §2** — 60/51-name reference rosters for frame-data-grade movesets once
   extraction unblocks.
5. **Def Jam §17** — 142 entries/78 models across 5 styles; brawler/street archetypes for
   Hall Nighter, Wreck Patterson, Brutus.
6. **No Mercy §14** — 42 wrestlers, full AKI grapple kits; wrestling archetypes.
7. **WMXIX §15** — 45 named wrestlers pending owner visual ID; 99 named specials mapped.

**For worker 47 (moveset library):** ingest priority = T3 divmot banks (§1) → VF5 FARC anims
(§6) → SC2 command lists (§9) → No Mercy AkiAnimation bank (§14) → Def Jam wresNNN sets
(§17) → WMXIX YANM/code-indexed clips (§15). All formats and repo locations are in the
sections above.
