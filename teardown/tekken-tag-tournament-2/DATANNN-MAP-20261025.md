# TTT2 dataNNN -> characters/moves map (2026-10-25)

Owner order 2026-10-14: TTT2 100% into western-heart, characters and moveset data FIRST.
Follow-up to PR #1143 (extraction 72/72) and PR #1145 (0ff512ed LZX crack, MERGED 2026-10-25T16:46:31Z).
Source: the 7 decoded inner files in `~/workspace/_ttt2-work/decoded-*.bin` (91.3 MB total),
decoded 100% from release `ttt2-7z-v1` via `tools/lzx-decode/lzx_chunks.c`.
Decoded binaries stay OFF the repo per AGENTS.md rule 8; this doc maps them. Reproducible from the release via the tool.

## 1. Shared NRFI envelope (all 7 files)

Every decoded file is `ftyp(20) + head(28) + idgt(200) + imge(payload)`, all box sizes BE u32.
6 of 7 files: `248 + imge.size == file size` exactly. EXCEPTION: data000 declares
`imge.size = 17,777,576` but the file is 17,755,827 B — declared size overruns the file by 21,997 B.
Decode verified 100% by the LZX commit, so this is flagged as VERIFY-ON-REDECODE, not corruption.

## 2. Per-file roles

| file | size | payload starts | role (verified) |
|---|---|---|---|
| data000.bin | 17,755,827 | `paof` + 3x `<?xml`, 91,120 `<` | Moveset XML container (paof table + XML text) — XML extraction is the next parse step |
| data004.bin | 6,522,032 | `MOTA` (21x) | MOTA motion/animation table |
| data018.bin | 3,027,808 | 59x `MVLT` | Move-list table — one list per character (Section 3) |
| data019.bin | 177,104 | `xtal` (`libtutorial.xtal`) | Tutorial script (Stage1Info, toplevel) |
| data050.bin | 44,928,288 | offset table + 104,085 ASCII strings | Name/sparse tables — structure TBD (no UTF-16 names found; strings are mostly short codes) |
| data052.bin | 15,463,552 | 59x `BXML` | Per-character CUSTOMIZATION tables (Section 4) — 58 characters + 1 shared table |
| data053.bin | 3,461,024 | `BXML` (1x) | Single BXML doc — Fighter/Equipment/Position customization (first item `uju_cmn_aur_type1green`) |

## 3. data018 — MVLT move lists (59 tags)

`#0` (176 B) is a header/offset table, not a move list: `MVLT` + u32s `2, 1, 0, 32, 80, 172, 172, ...`
then a table stepping by 64 (`0x40, 0x80, 0xc0, 0x100, ...`). `#1`-`#57` are per-character move lists
(move names in plain text, EN/FR/IT/DE variants). `#58` (142,672 B) starts with the literal string `title`
and mixes moves from several characters — treated as a master/index list, not a character list.
First-5-moves column is the fingerprint used for character identification below.

| # | offset | len | strings | first 5 moves |
|---|---|---|---|---|
| 0 | 256 | 176 | 1 | (header table) |
| 1 | 432 | 40240 | 340 | Left Right Combo / Reverse PDK Combo / Jab Roundhouse / Jab Sweep / Piston Fire |
| 2 | 40672 | 62208 | 671 | Machine Gun Arrow / Left Right Combo / Left Right Dragon Fist / Left Right Dragon Fist Combo / Left Right Blazing Fist Combo |
| 3 | 102880 | 86240 | 1119 | Serpent Strike / Left Right Punch / Yue Ya Cha Shou / Yue Ya Lian Tui / High and Low Kicks |
| 4 | 189120 | 105936 | 1191 | Palm Attack / Palm Strike to Head Jammer / Palm Strike to Jumping Power Bomb / Palm Attack to Uppercut / Palm Upper to Suplex |
| 5 | 295056 | 73936 | 920 | Naguri Kabuto Wari / Seiken Douharai / Flash Punch / Flash Attack / Flash Punch Low Kick |
| 6 | 368992 | 66784 | 535 | Left Right Combo / Biting Snake / Left Right to Spider Knee / Bermuda Triangle / Double Explosion 1 |
| 7 | 435776 | 81936 | 931 |  Commands during Left Stance  /  Pendant Left Stance  /  Durante Left Stance  /  Befehle w / hrend Left Stance  |
| 8 | 517712 | 67920 | 865 | Bayonet / Bayonet Thruster / Fan Dance to Rain Dance / Bayonet McTwist / Fan Dance to Pushing Hands |
| 9 | 585632 | 76528 | 838 | One Two Elbows / Combo Jilar / Left Jab to Island Mirage / Left Jab Island Mirage to Negativa / Gancho Chibata |
| 10 | 662160 | 35936 | 279 | Left Right Combo / Left Right Axe Kick / Left Right to Spinning Hook Kick / Kazama Style 5 Hit Combo / Ni Rengeki Sen |
| 11 | 698096 | 54032 | 449 | G-Clef Cannon / Divine Impact / Divine Intervention / Left Right Combo / Baiyuan Sanshou |
| 12 | 752128 | 45632 | 495 | Left Right Bear Claw / Jab Elbow Smash / Jab Elbow Stomp / Triple Hammer / Hunting |
| 13 | 797760 | 44816 | 267 | Left Right Combo / One Two Body Blow / One Two Low Kick / One Two High Kick / Lair's Dance |
| 14 | 842576 | 37120 | 289 | Flash Punch Combo / Left Right Combo / Demon Slayer / Demon Executioner / Demon Executioner Feint |
| 15 | 879696 | 41104 | 308 | Flash Punch Combo / Left Right Combo / Demon Slayer / Twin Fang Stature Smash / Twin Fang Double Kick |
| 16 | 920800 | 46880 | 406 | Left Right Combo / Left Right Combo to Revolution Zwei / Left Right Mid Kick / Left Right Max Mid /  Hold |
| 17 | 967680 | 64144 | 662 | Double Jab / Lightning Combo / Double Jab Body Blow / Double Jab Body Blow to Flicker Stance / Left Right |
| 18 | 1031824 | 54288 | 550 | Left Right Combo / Left Right to Gut Check / Left Right to Ready Position / Left Right to Power Elbow Combo / Jab Body Combo |
| 19 | 1086112 | 51744 | 423 | Jab to Jackhammer / Jab to Stunning Hook / Jab Elbow Smash / Cyclone Hammer / Giant Foot Stomp |
| 20 | 1137856 | 36864 | 268 | Left Right Combo / Left Right Body Blow / Left Right Arrow / One Two Kangaroo Combo / Left Right Rocket Stance |
| 21 | 1174720 | 63120 | 494 | Left Right Combo / Left Right to Left Low Kick / Jab Combo Roundhouse / Left Right Left Combo / Left Right Left to Frost Needle |
| 22 | 1237840 | 35168 | 299 | Long Zhu Lian Pao / Jab to Right High Kick / Spin Behind /  (must hit from front) /  (coup doit toucher de face) |
| 23 | 1273008 | 42640 | 384 | Open Palm Combo / Enma Harite / Harite to Kekaeshi / Splits Stomp / Left High Kick to Splits Stomp |
| 24 | 1315648 | 38336 | 336 | Whiplash / Jab Uppercut / Jab Uppercut to Spinning Heel Drop / Jab Uppercut to Front Kick / Jab Low Kick |
| 25 | 1353984 | 47504 | 381 | Left Right Combo / Bruce Rush / Northern Lights Combination / One Two High Kick to Pasart Stance / Pasart Krabong |
| 26 | 1401488 | 46000 | 377 | Double Jab / One Two Combo  / One Two Flamingo Step /  (or  /  (or  |
| 27 | 1447488 | 41008 | 265 | Flash Punch Combo / Left Right Combo / Demon Slayer / Shoot the Works / Shoot the Works Upper |
| 28 | 1488496 | 59328 | 566 | Left Right Combo / Right Straight to Left Low Kick / PK Combo / Valkyrie Lance Combo / Brocken Connect |
| 29 | 1547824 | 39744 | 320 | Jab Spear Fist / Firestorm / Jab Roundhouse Combo / San Lian Heng / Peacock Sweep |
| 30 | 1587568 | 55072 | 507 | One Two Punch / Left Right Uppercut / Jab Uppercut / Dark Cyclone / Dark Buzzsaw |
| 31 | 1642640 | 38544 | 343 | Left Right Back Strike / Left Right Piercing Thorn / Sunrise Sunset / Bed Time / Peacock Waltz |
| 32 | 1681184 | 42992 | 334 | Eye Gouge to Hilt / Jab to Body Blow / Salvo / Hammer and Sickle / One Two Scud Kick |
| 33 | 1724176 | 45632 | 495 | Left Right Bear Claw / Jab Elbow Smash / Jab Elbow Stomp / Triple Hammer / Hunting |
| 34 | 1769808 | 76080 | 833 | One Two Elbows / Combo Jilar / Left Jab to Island Mirage / Left Jab Island Mirage to Negativa / Gancho Chibata |
| 35 | 1845888 | 41888 | 290 | Straight Rondel / One Two Punch / Fast Break / Course Picante / Course Sarat |
| 36 | 1887776 | 44688 | 557 | Left Right Combo / Left Right Scarecrow / Anzu / Ecdysis / Kapara |
| 37 | 1932464 | 52288 | 576 | Resorte / Up-stroke / Up-stroke to Savage Stance / Martillo / Bombo |
| 38 | 1984752 | 37264 | 373 | He Zi Shou / Liang Yi Zhou / Wai Bai Tui / Ye Chui / Lian Tan |
| 39 | 2022016 | 42336 | 411 | Delta Slicer / One-Two Combination / Legionnaire's Spin / Lightning Assault Middle / Lightning Assault High |
| 40 | 2064352 | 56432 | 562 | Stop Bit / Stop Bit to Destructive Form / Coil Punch Combo / Down Time  / Down Link |
| 41 | 2120784 | 34816 | 387 | Flash Punch Combo / Tamonsatsu / Demon Backhand Spin / Roundhouse / Enma's Fury |
| 42 | 2155600 | 33024 | 247 | Left Right Combo / Demon Slayer / Demon Backhand Spin / Piston Fire / Demon Scissors |
| 43 | 2188624 | 41280 | 429 | Whiplash / Jab Uppercut / Jab Uppercut Spin Kick / Jab Low Kick / Jab Leg Cutter |
| 44 | 2229904 | 45984 | 481 | Whiplash / Jab Uppercut / Jab Uppercut Spin Kick / Jab Low Kick / Jab Leg Cutter |
| 45 | 2275888 | 39968 | 421 | Memai Tsuki / Flash Kick Combination / Lotus Blade / Oni Kick Combo / Zig Zag |
| 46 | 2315856 | 41376 | 289 | Straight Rondel / One Two Punch / Fast Break / Course Picante / Course Sarat |
| 47 | 2357232 | 53728 | 509 | Machine Gun Arrow / Left Right Combo / Left Right Dragon Fist / Left Right Dragon Fist Combo / Left Right Blazing Fist Combo |
| 48 | 2410960 | 68560 | 855 | Bayonet / Bayonet Thruster / Fan Dance to Rain Dance / Bayonet McTwist / Fan Dance to Pushing Hands |
| 49 | 2479520 | 31744 | 218 | Flash Punch Combo / Left Right Combo / Demon Slayer / Spin Claw Combo / Wheel of Pain |
| 50 | 2511264 | 47680 | 438 | G-Clef Cannon / Divine Impact / Divine Intervention / Left Right Combo / Baiyuan Sanshou |
| 51 | 2558944 | 52128 | 435 | P.Jack Hammer / Fragmentation Spin Punch / Jab Elbow Smash / Cyclone Hammer / Giant Foot Stomp |
| 52 | 2611072 | 36784 | 261 | Left Right Combo / Left Right Body Blow / Left Right Arrow / One Two Kangaroo Combo / Left Right Rocket Stance |
| 53 | 2647856 | 32784 | 250 | Flash Punch Combo / Left Right Combo / Quick Elbow Combo / Demon Backhand Spin / Catapult Tackle Combo |
| 54 | 2680640 | 47168 | 415 | Left Right Combo / Left Right Combo to Revolution Zwei / Left Right Mid Kick / Left Right Max Mid /  Hold |
| 55 | 2727808 | 41968 | 537 | Left Right Combo / Scared Combination / Scared Combination to Mad Pain /  (must hit) /  (coup doit toucher) |
| 56 | 2769776 | 39136 | 363 | Left Right Back Strike / Left Right Piercing Thorn / Sunrise Sunset / Bed Time / Peacock Waltz |
| 57 | 2808912 | 76224 | 822 | One Two Elbows / Combo Jilar / Left Jab to Island Mirage / Left Jab Island Mirage to Negativa / Gancho Chibata |
| 58 | 2885136 | 142672 | 764 | title / Flash Punch Combo / Coil Punch Combo / Demon Slayer / Fast Break |

### 3a. Duplicate groups (identical first-5 = shared/clone movelists)

- `#12` = `#33` — Bear Claw / Triple Hammer / Hunting (Kuma / Panda)
- `#9` = `#34` = `#57` — Combo Jilar / Gancho Chibata (capoeira: Eddy / Christie / Tiger)
- `#2` = `#47` — Machine Gun Arrow / Dragon Fist (Law / Forest Law)
- `#16` = `#54` — Revolution Zwei (Lee / Violet)
- `#43` = `#44` — Whiplash / Jab Uppercut (identical lists, characters TBD)
- `#8` = `#48` — Bayonet / Fan Dance
- `#20` = `#52` — Kangaroo Combo (Roger / Alex)
- `#35` = `#46` — Straight Rondel / Fast Break
- `#31` = `#56` — Sunrise Sunset / Peacock Waltz
- `#19` vs `#51` share Jab Elbow Smash / Cyclone Hammer / Giant Foot Stomp (Jack family)

### 3b. Anchors verified by distinctive moves (MVLT#n = BXML#(n-1) through #18)

- #1 Paul (Piston Fire, Hammer of the Gods, Shoulder Tackle) | #2 Law (Dragon Fist) | #3 Lei (Yue Ya Cha Shou)
- #4 King (Palm Strike to Jumping Power Bomb, Suplex) | #7 Hwoarang ("Commands during Left Stance")
- #9 Christie (capoeira) | #10 Jin (Kazama Style 5 Hit Combo) | #11 Julia (G-Clef Cannon)
- #12 Kuma (Bear Claw) | #14 Heihachi (Demon Executioner) | #15 Kazuya (Twin Fang)
- #17 Steve (Flicker Stance) | #18 Marduk (Gut Check, Power Elbow)

### 3c. Order ambiguity AFTER #18 — do not treat as settled

From #19 on, the MVLT order and the BXML order diverge by one in places:
- #19 Jab to Jackhammer = Jack (BXML#19 jac), not Mokujin (BXML#18 mok) — Mokujin likely has NO MVLT list (he mimics).
- #20 Kangaroo Combo = Roger (BXML#20 rog). #32 Hammer and Sickle / Scud Kick = Dragunov (BXML#32 dra), not Lili.
- #33 Bear Claw = Panda (BXML#43 pan), sitting at MVLT position 33, not 43.
- #39 Lightning Assault / Legionnaire's Spin = Lars (BXML#38 lar) under the n-1 mapping.
- #40 Stop Bit / Destructive Form / Coil Punch / Down Time = Alisa the android (BXML#39 asa) under the n-1 mapping.
Working hypothesis: MVLT order = BXML order with Mokujin skipped, BUT the #31/#32/#33 positions
contradict it, so the true join must come from data000's XML (character IDs) or data050's name table.
Do NOT assign characters to MVLT #19+ from order alone — use the move fingerprints in the table above.

## 4. data052 — BXML customization tables (59 docs, in file order)

Each doc's first item label carries the character prefix (`xxx_...`); character-specific items repeat the
prefix (`xxx_xxx_...`). 58 docs are per-character; doc #44 (`uju`) has NO character-specific items — it is
the SHARED/common table (all items `uju_cmn_*`). Prefix -> character is by the prefix except where marked.
First-item English name is the doc's first `name/English` value.

| # | prefix | first item label | first item (English) | character |
|---|---|---|---|---|
| 0 | pau | `pau_hcc_fro_ayanami` | Shaggy | Paul |
| 1 | law | `law_cmn_opu_Flag9` | Flag - Break Time | Marshall Law |
| 2 | lei | `lei_hcc_acc_chainlock` | Chain | Lei Wulong |
| 3 | kin | `kin_cmn_opu_BeamShieldForce` | Blue Space Shield | King |
| 4 | yos | `yos_cmn_opl_PaintBladeGreen` | Paint Blade (Green) | Yoshimitsu |
| 5 | nin | `nin_hcf_hed_back_twin_up_tail_middle` | Mid-Length Pigtails (High) | Nina |
| 6 | hwo | `hwo_cmn_aur_type1skyblue` | Prana (Aqua) | Hwoarang |
| 7 | xia | `xia_cmn_aur_type2kuro` | Aura (Black) | Ling Xiaoyu |
| 8 | chr | `chr_hcc_hed_back_pony_mid_tail_middle` | Mid-Length Ponytail (Mid) | Christie |
| 9 | jin | `jin_cmn_opl_SilverKnifeSakate` | Silver Combat Knife (Backward) | Jin |
| 10 | jul | `jul_cmn_opl_AssaltRifle` | Assault Rifle | Julia |
| 11 | kum | `kum_cmn_eff_default_ss` | Effect (Rank S) | Kuma |
| 12 | bry | `bry_bry_hed__Knit` | Knit Cap | Bryan |
| 13 | hei | `hei_cmn_aur_type2white` | Aura (White) | Heihachi |
| 14 | kaz | `kaz_hcc_hed_back_pony_mid_tail_middle` | Mid-Length Ponytail (Mid) | Kazuya |
| 15 | lee | `lee_cmn_opu_Fude` | Brush | Lee |
| 16 | ste | `ste_cmn_opu_Nuncyaku` | Black Nunchuks | Steve |
| 17 | mar | `mar_cmn_opl_katana` | Katana | Craig Marduk |
| 18 | mok | `mok_cmn_opl_AssaltRifle` | Assault Rifle | Mokujin |
| 19 | jac | `jac_cmn_opu_Pizza` | Giant Pizza | Jack-6 |
| 20 | rog | `rog_cmn_opu_Flag1` | Flag - Pirates | Roger Jr. |
| 21 | ann | `ann_wcf_upb_holtercami_wcf_arm_longglove` | Haltertop & Long Gloves | Anna |
| 22 | wan | `wan_cmn_opl_BlackKnifeJunte` | Black Combat Knife (Forward) | Wang |
| 23 | gan | `gan_hcc_fro_tare_staggered` | Asymmetrical | Ganryu |
| 24 | ask | `ask_cmn_rag_red01` | SP Rage (Red) | Asuka |
| 25 | bru | `bru_cmn_opl_ChristmasTree` | Christmas Tree | Bruce |
| 26 | bae | `bae_hcc_hed_back_pony_un_tail_middle` | Mid-Length Ponytail (Low) | Baek |
| 27 | dvj | `dvj_cmn_opu_Nobori_low1` | Banner - Rising Dragon | Devil Jin |
| 28 | rav | `rav_wcm_upb_down_jacket_wcm_slv_no_wcm_arm_no` | Puffy Jacket | Raven |
| 29 | fen | `fen_hcc_acc_bell` | Bell | Feng |
| 30 | aki | `aki_cmn_meg_cellframe_oval` | Oval Glasses | UNRESOLVED |
| 31 | lil | `lil_cmn_opu_BeamShieldEvil` | Red Space Shield | Lili |
| 32 | dra | `dra_cmn_opl_MagicWand` | Magic Wand | Dragunov |
| 33 | edd | `edd_cmn_opl_ChristmasTree` | Christmas Tree | Eddy |
| 34 | bob | `bob_bob_upb_hunter` | Hunter Top | Bob |
| 35 | zaf | `zaf_cmn_opu_StuffedAnimal` | Stuffed Rabbit | Zafina |
| 36 | mig | `mig_mig_fac_1p` | Default Face | Miguel |
| 37 | leo | `leo_cmn_rag_white01` | SP Rage (White) | Leo |
| 38 | lar | `lar_cmn_opu_koduchi` | Golden Mallet | Lars |
| 39 | asa | `asa_hcf_hed_back_twin_up_tail_middle` | Mid-Length Pigtails (High) | UNRESOLVED (probable Alisa, see notes) |
| 40 | ji8 | `ji8_cmn_opl_Bouquet` | Bouquet | UNRESOLVED (probable Jinpachi, see notes) |
| 41 | ogr | `ogr_cmn_opl_MagicWand` | Magic Wand | Ogre |
| 42 | jun | `jun_cmn_opl_SilverSword` | Excalibur | Jun |
| 43 | pan | `pan_pan_fac_punk_make_d` | Punk Face 1 | Panda |
| 44 | uju | `uju_cmn_aur_type1green` | Prana (Green) | SHARED/common table (no char-specific items) |
| 45 | cbt | `cbt_cbt_exp_1p_all` | Default Parts | Combot |
| 46 | mih | `mih_mih_hed_Soft` | Fedora | Miharu |
| 47 | flw | `flw_flw_hed_Kabuto` | Kabuto | UNRESOLVED (probable Forest Law, see notes) |
| 48 | knm | `knm_knm_upb_1p` | Default Top | Kunimitsu |
| 49 | ang | `ang_ang_hed__Tengallonhat` | Cowboy Hat | Angel |
| 50 | sli | `sli_sli_hed__Bret` | Beret | Slim Bob |
| 51 | mic | `mic_mic_hed_Cap` | Baseball Cap | Michelle |
| 52 | tig | `tig_tig_hed_tg2` | Default | Tiger |
| 53 | alx | `alx_alx_hed_1p` | Default Head | Alex |
| 54 | vio | `vio_vio_upd_1p` | Default Top | Violet |
| 55 | pja | `pja_pja_hed_Crown` | Crown | Prototype Jack |
| 56 | gre | `gre_gre_hed_Silkhat` | Top Hat | UNRESOLVED (probable True/Ancient Ogre, see notes) |
| 57 | seb | `seb_seb_hed_1p` | Default Hair | Sebastian |
| 58 | bcv | `bcv_bcv_hed__Bandana` | Bandana | UNRESOLVED (probable Dr. Bosconovitch, see notes) |

### 4a. Unresolved prefixes — evidence, not guesses

- `aki` (#30): Oval Glasses first item; `aki_aki_*` character-specific items exist. MVLT#31 (Sunrise Sunset / Peacock Waltz)
  sits at the matching position under the n-1 mapping — character TBD from data000 XML.
- `asa` (#39): twin-pigtails hair first item; `asa_asa_*` items exist. `asa` = A...S...A fits Alisa; MVLT#40's android
  moves (Stop Bit, Destructive Form, Down Link) align here under the n-1 mapping. Probable Alisa — VERIFY via data000.
- `ji8` (#40): `ji8_ji8_et1_tg2_juzu` (juzu prayer beads) among its items. `ji` + `8` reads as Jinpachi (hachi = 8).
  Probable Jinpachi — VERIFY via data000.
- `flw` (#47): `flw_flw_hed_Kabuto`. `flw` = F-L-W fits Forest Law. Probable Forest Law — VERIFY via data000.
- `gre` (#56): Top Hat first item. `gre` = G-R-E is Ogre-derived (`ogr` #41 = O-G-R, `gre` = G-R-E).
  Probable True Ogre or Ancient Ogre — VERIFY which via data000.
- `bcv` (#58): Bandana first item. `bcv` = B-o-s-C-o-no-V-itch fits Dr. Bosconovitch. Probable Bosconovitch — VERIFY via data000.
- `uju` (#44): NOT Unknown — it is the shared/common customization table (no `uju_uju_*` items, all `uju_cmn_*`).

## 5. What is still missing

- The remaining 33 dataNNN.bin inner files (of 42 total: 9 pulled, 33 to go). DISK-GATED: /home/hatch was 82%
  (19G free) at map time; the <70% gate from the resume brief does not open for bulk pulls. Pull one at a time only.
- data000 XML extraction (character IDs -> definitive MVLT/BXML join) and data050 name-table parse.
- data000 imge declared-size overrun (21,997 B) — re-verify on the next re-decode.
- Character models/textures/stages live in the remaining dataNNN files and the extracted 7z tree — not in these 7 files.

## 6. Method

Parsed with stdlib Python only (`struct` box walk + regex string scan) over the local decoded files;
no downloads, no new tools. Counts re-checked twice (59 MVLT tags, 59 BXML docs, 104,085 data050 strings).
Move-name strings are quoted verbatim from the files, including the source's own `Japanease` spelling.
