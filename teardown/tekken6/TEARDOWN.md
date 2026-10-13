# TEKKEN 6 (PSP) — Full Teardown for Western Heart

**Source:** `tekken6-psp.iso` (816MB, PSP, USA)
**Teardown date:** 2026-10-13
**Status:** Videos + structure extracted. Models/textures encrypted (documented below).

---

## What Was Extracted

### 1. Ending Videos — 46 PMF files (337MB)
Every character's ending cinematic + opening videos. H.264, 480x272, ~30fps.
Playable with ffmpeg. Located at `extracted/movies/`.

| File | Character | Size |
|------|-----------|------|
| ending_ann.pmf | Anna Williams | 5.2MB |
| ending_arm.pmf | Armor King | 1.8MB |
| ending_arm2.pmf | Armor King (alt) | 6.7MB |
| ending_asa.pmf | Alisa Bosconovitch | 12.5MB |
| ending_ask.pmf | Asuka Kazama | 6.6MB |
| ending_bae.pmf | Baek Doo San | 5.8MB |
| ending_bob.pmf | Bob Richards | 7.3MB |
| ending_bru.pmf | Bruce Irvin | 4.8MB |
| ending_bry.pmf | Bryan Fury | 5.8MB |
| ending_dji.pmf | Devil Jin | 6.5MB |
| ending_dra.pmf | Sergei Dragunov | 6.6MB |
| ending_edd.pmf | Eddy Gordo | 6.6MB |
| ending_fen.pmf | Feng Wei | 3.3MB |
| ending_gan.pmf | Ganryu | 5.6MB |
| ending_hei.pmf | Heihachi Mishima | 7.2MB |
| ending_hwa.pmf | Hwoarang | 5.6MB |
| ending_jac.pmf | Jack-6 | 4.8MB |
| ending_jin.pmf | Jin Kazama | 4.3MB |
| ending_jin2.pmf | Jin Kazama (alt) | 4.8MB |
| ending_jul.pmf | Julia Chang | 6.4MB |
| ending_kaz.pmf | Kazuya Mishima | 5.4MB |
| ending_kin.pmf | King II | 3.8MB |
| ending_kum.pmf | Kuma | 9.2MB |
| ending_lar.pmf | Lars Alexandersson | 14.7MB |
| ending_law.pmf | Marshall Law | 6.5MB |
| ending_lee.pmf | Lee Chaolan | 7.5MB |
| ending_lei.pmf | Lei Wulong | 5.1MB |
| ending_leo.pmf | Leo Kliesen | 4.1MB |
| ending_lil.pmf | Lili Rochefort | 7.5MB |
| ending_mig.pmf | Miguel Caballero Rojo | 5.1MB |
| ending_mok.pmf | Mokujin | 6.9MB |
| ending_mur.pmf | Craig Marduk | 3.2MB |
| ending_nin.pmf | Nina Williams | 4.8MB |
| ending_pal.pmf | Paul Phoenix | 8.5MB |
| ending_pan.pmf | Panda | 3.4MB |
| ending_rav.pmf | Raven | 7.2MB |
| ending_roj.pmf | Roger Jr. | 6.0MB |
| ending_stv.pmf | Steve Fox | 7.2MB |
| ending_wan.pmf | Wang Jinrei | 7.8MB |
| ending_xia.pmf | Ling Xiaoyu | 7.4MB |
| ending_yos.pmf | Yoshimitsu | 7.2MB |
| ending_zaf.pmf | Zafina | 7.5MB |
| title.pmf | Title screen | 0.6MB |
| opening.pmf | Opening cinematic | 34.6MB |
| br_opening.pmf | Bloodline Rebellion opening | 21.8MB |
| arcade_opening.pmf | Arcade opening | 15.0MB |

### 2. Reference Frames — 42 JPGs
One frame from each ending video at 5-second mark. Located at `extracted/ref_frames/`.
Use these as visual references for Western Heart character design.

### 3. ISO File Structure Map
```
/
├── UMD_DATA.BIN
└── PSP_GAME/
    ├── PARAM.SFO, ICON0.PNG, ICON1.PMF, PIC1.PNG, SND0.AT3
    ├── SYSDIR/
    │   ├── EBOOT.BIN (4.0MB, encrypted ~PSP format)
    │   ├── BOOT.BIN
    │   ├── OPNSSMP.BIN
    │   └── UPDATE/
    └── USRDIR/
        ├── DINF_400.BIN (120 bytes — encryption key/hash)
        ├── DATA401.IDX (26KB — encrypted index table)
        ├── modules/ (2 PSP kernel modules)
        └── movie/ (46 PMF videos, 337MB)
```

---

## Character Roster — 40 Fighters

Confirmed from ending videos:

| # | Code | Character | Notes |
|---|------|-----------|-------|
| 1 | ann | Anna Williams | |
| 2 | arm | Armor King | |
| 3 | asa | Alisa Bosconovitch | T6 newcomer |
| 4 | ask | Asuka Kazama | |
| 5 | bae | Baek Doo San | |
| 6 | bob | Bob Richards | **T6 newcomer, Western Heart candidate** |
| 7 | bru | Bruce Irvin | |
| 8 | bry | Bryan Fury | |
| 9 | dji | Devil Jin | |
| 10 | dra | Sergei Dragunov | |
| 11 | edd | Eddy Gordo | |
| 12 | fen | Feng Wei | |
| 13 | gan | Ganryu | |
| 14 | hei | Heihachi Mishima | |
| 15 | hwa | Hwoarang | |
| 16 | jac | Jack-6 | |
| 17 | jin | Jin Kazama | |
| 18 | jul | Julia Chang | |
| 19 | kaz | Kazuya Mishima | |
| 20 | kin | King II | |
| 21 | kum | Kuma | |
| 22 | lar | Lars Alexandersson | **T6 newcomer** |
| 23 | law | Marshall Law | |
| 24 | lee | Lee Chaolan | |
| 25 | lei | Lei Wulong | |
| 26 | leo | Leo Kliesen | **T6 newcomer** |
| 27 | lil | Lili Rochefort | |
| 28 | mig | Miguel Caballero Rojo | **T6 newcomer** |
| 29 | mok | Mokujin | |
| 30 | mur | Craig Marduk | |
| 31 | nin | Nina Williams | |
| 32 | pal | Paul Phoenix | |
| 33 | pan | Panda | |
| 34 | rav | Raven | |
| 35 | roj | Roger Jr. | |
| 36 | stv | Steve Fox | |
| 37 | wan | Wang Jinrei | |
| 38 | xia | Ling Xiaoyu | |
| 39 | yos | Yoshimitsu | |
| 40 | zaf | Zafina | **T6 newcomer** |

**T6 newcomers:** Alisa, Bob, Lars, Leo, Miguel, Zafina (6 new fighters)

---

## Customization System — Research Documentation

Tekken 6's customization system (from public documentation, not extracted from encrypted data):

### How It Works
- Each character has **4 customization slots**: Head, Upper Body, Lower Body, Other
- Items are purchased with in-game currency (earned through gameplay)
- Items are 3D models that attach to bone anchor points on the character rig
- The game uses a **layered rendering** system — customization items render on top of base model

### Item Categories
- **Head:** Hats, helmets, masks, glasses, hairstyles
- **Upper:** Jackets, shirts, armor, tattoos
- **Lower:** Pants, skirts, belts, shoes
- **Other:** Auras, effects, weapons, companions

### Technical Structure (for Western Heart implementation)
- Base character model has named **socket/anchor points** (e.g., `head_socket`, `hand_L`, `back`)
- Each customization item is a separate mesh with a defined **attachment point** + **offset transform**
- Items can have their own textures/materials independent of base model
- The game stores customization as a **list of item IDs** per slot per character
- UI presents items in a grid with 3D preview on the character model

### Western Heart Application
This is the template for Western Heart's customization system:
1. Define socket points on each fighter's rig
2. Build customization items as separate meshes
3. Store player loadouts as item ID lists
4. Render items as additional mesh layers on the base character

---

## What Could NOT Be Extracted

### Encrypted/Proprietary Data
The following are locked behind PSP encryption and Namco's proprietary formats:

- **Character models** — GMO format, inside encrypted archives. EBOOT.BIN uses `~PSP` encryption.
- **Textures** — Likely TIM2/GIM format, same encryption barrier.
- **Stages/arenas** — Same.
- **Animation data** — Same.
- **Audio** (beyond videos) — AT3 format, encrypted.
- **Customization item meshes** — Same.

### Why
1. EBOOT.BIN starts with `~PSP` magic = Sony's encrypted executable format
2. DINF_400.BIN (120 bytes) appears to be an encryption key or hash, not a file index
3. DATA401.IDX (26KB) is encrypted — no readable file table
4. Namco's PSP archive format is proprietary and undocumented
5. Decryption would require PSP firmware keys + custom tooling (PPSSPP decryption, psptools)

### Future Path
If model extraction is needed later:
1. Decrypt EBOOT.BIN using PPSSPP's built-in decryption or psptools
2. Reverse-engineer Namco's archive format from decrypted binary
3. Extract GMO models, convert via Noesis with PSP plugins
4. This is a multi-day RE task, not a quick extraction

---

## What's Usable for Western Heart NOW

1. **40 character ending videos** — Study each fighter's personality, story, visual design
2. **42 reference frames** — Visual references for reskinning and character design
3. **Full 40-fighter roster** — 6 newcomers (Bob, Lars, Leo, Miguel, Alisa, Zafina) are fresh bodies for Western Heart
4. **Customization system design doc** (above) — Template for building Western Heart's customization
5. **Bob Richards** — Owner-flagged as Western Heart candidate. Reference video + frame extracted.

---

## File Inventory

```
tekken6/
├── tekken6-psp.iso (816MB) — source, DO NOT DELETE until further extraction
├── TEARDOWN.md (this file)
└── extracted/
    ├── movies/ (46 PMF files, 337MB)
    └── ref_frames/ (42 JPG files)
```

---

## Integration Checklist for Western Heart

- [x] ISO acquired and verified
- [x] File structure mapped
- [x] All 46 videos extracted
- [x] 42 character reference frames extracted
- [x] 40-fighter roster documented
- [x] Customization system researched and documented
- [ ] Character models extracted (blocked: encryption)
- [ ] Textures extracted (blocked: encryption)
- [ ] Stages extracted (blocked: encryption)
- [ ] Customization item meshes extracted (blocked: encryption)
- [ ] EBOOT decryption (future RE task if needed)
