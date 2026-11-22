# Source motion inventory — what move/motion data we actually hold (2026-11-05)

Owner instruction (2026-11-05): stop saying characters have no move set / data list when they exist in
the previous games (Tekken 3, Tekken 5, Tag 2, Tekken 7, ...). This file records **what is held**, per
game, and maps every Western Heart fighter that is on a stand-in bank (or has no bank) to the exact held
file(s) of their real character.

Checked against `main` @ `839565071` (merge #1595), the releases of `mhvnsnt/western-heart` and
`mhvnsnt/game-reverse-engineering` (GRE, private), and the local `/workspace/work` checkouts. **Inventory only: no banks were built in this run.**

Words used below:
- **bank** = the wh-anim/1 clip folder a fighter animates from (`game/assets/anim/t3/<bank>/`, bound by
  `game/js/fighter.js` `bankIdFor` → `game/js/t3anims.js` `T3_BANKS`). The folder is named `t3/` for all
  of them, but the motion inside can come from T3, T7 or TTT2.
- **own** = the bank is the fighter's canon base character. **stand-in** = the bank is someone else's.
- **FULL (GRE)** = all four T7 files are held in GRE `teardown/tekken7-steam/tkdata/mothead/`:
  `bin/<code>mot.bin`, `json/<code>mot.json`, `mask/<code>rotsm.arc`, `movelist/<code>.mvl`.

---

## 1. Holdings by game

| Game | What we hold (motion/move data) | Format | Characters | Working converter to a WH bank? |
|---|---|---|---|---|
| **Tekken 3** (PS1) | 22 T3-decoded bank folders in `game/assets/anim/t3/` (anna, armorking, bosconovitch, bryan, eddy, forestlaw_on_law, gon, gunjack, heihachi, heihachi_on_jin, hwoarang, jin, julia, king_on_pantera_leoman, kuma, law, lei, nina, ogre, paul, xiaoyu, yoshimitsu). The same folder also holds 4 later-game banks: raven and luckychloe (T7), roger and jun (TTT2); move tables in `teardown/tekken3/movesets/` (43 files); raw disc + 19.5k work files in releases `tekken3-ps1-v1`, `tekken3-work-v1` | divmot banks from TEKKEN3.BNS → wh-anim/1 | The T3 cast, **except Mokujin** (divmot15 has size 0 on the owner's disc, per `game/js/t3anims.js`) | **Yes**: `tools/anim/t3_bake_bank.py`, `t3_row_bake.py`, `t3_bake_packs.py`, `t3_hit_frames.py` (all used) |
| **Tekken 5** (PS2) | Full disc in GRE releases `tekken5-iso-v1`, `tekken5-disc-v1` (TK5DATA0–3), `tekken5-tk5data5-v1`, `tekken5-e7-extract-v1`; the romD motion filename list `teardown/tekken5/t5_motion_manifest.txt` (498 `.dat` names); costume GLBs in WH release `tekken5-costume-glbs-v1` | romD / BDPK containers | Whole T5 cast (raw) | **No.** Only survey tools (`teardown/tekken5/tools/t5_survey.py`, `iso9660_extract.py`). No motion or moveset decode exists. |
| **Tekken 6** (PSP; plus PS3 BR archive) | 18 decoded move lists `teardown/tekken6/movesets/t6psp-<char>-moveset-v3.json` (armor-king, asuka, baek-doo-san, dragunov, eddy, heihachi, jin, king, kuma, law, lee, lin-xiaoyu, marduk, nina, raven, roger, wang, zafina); PSP ISO (`tekken6-psp-v1`); PS3 `TEKKEN.psarc` (`tekken6-ps3-full-v1`) | COM move tables (names + notation, 6,814/6,814 decoded) | 18 characters (moves only) | **Moves only.** Clip data: the COM tail-zone MOTA records are empty stubs (`teardown/tekken6/TEKKEN6-FINAL-STATE.md`); no T6 clip decoder. (`tools/open-source/tkmovesets/TKMovesets2/GameSpecific/AnimExtractors/AnimExtractor_t6.cpp` is vendored reference code, not wired.) |
| **Tekken Tag Tournament 2** (X360) | Full 13.3 GB disc `ttt2-7z-v1`; LZX-decoded containers in `ttt2-work-archive-2026-10-30` (`top__decoded-data004.bin.gz` = common MOTA table, `top__decoded-data005.bin.gz` = per-character MOTA tables, `top__decoded-data006.bin.gz` = **66 motbins, one per character**); 57 decoded move lists `game/assets/ttt2/movesets/<prefix>.json` (index `game/assets/ttt2/index.json`) | motbin (0x70-byte move records, `anim_ref = (bank<<14)|index`) + MOTA 0x64/0xC8 clips | Motbins: Paul, Law, Lei, Raven, Feng, Armor King, Lili, Dragunov, King, Panda, Eddy, Bob, Zafina, Miguel, Leo, Lars, Alisa, Jinpachi, Yoshimitsu, Ogre, Jun, Unknown, Kunimitsu, Slim Bob, Forest Law, Miharu, Angel, Michelle, Nina, P-Jack, Alex, True Ogre, Violet, Bosconovitch, Sebastian, Tiger, Combot, Zako 0–7, Hwoarang, Xiaoyu, Christie, Jin, Julia, Kuma, Bryan, Heihachi, Kazuya, Lee, Steve, Marduk, Jack-6, **Roger**, Anna, Wang, Ganryu, Asuka, Bruce, Baek, Devil Jin (`docs/tech/ttt2-mota/JOIN-SEARCH-ROUND4.md` §1) | **Yes, proven for Roger Jr. and Jun:** `tools/ttt2_mota_decode64.py` (0x64), `tools/ttt2_mota_decode.py` (0xC8), `tools/anim/ttt2_bank_bake.py` (slot bank), `tools/anim/ttt2_bank_rows.py` (rows.pack + hit_frames). **Limit:** both bank tools take `--bank roger|jun` only. Join tables exist only for roger, jun and unknown (`docs/tech/ttt2-mota/join/`), and only Paul/Roger/Jun/Unknown have located bank-1 tables in data005 (`BANK1_TABLE` in `tools/anim/ttt2_bank_rows.py`). Any other character needs a join extract and a bank-1 fingerprint first. The recipe is in ROUND4 §3–§4 and §7. |
| **Tekken 7** (Steam) | GRE `teardown/tekken7-steam/tkdata/mothead/`: 57 `bin/*mot.bin`, 56 `json/*mot.json`, 58 `mask/*rotsm.arc` (incl. `common.arc`), 53 `movelist/*.mvl`; the shipping exe (GRE release `t7-shipping-exe-20261031`, needed for 0x64 conversion); clip cache (`t7-rotsm-clips-v1`: yos/ask/bry/bob/kin/jin/hei/arb + common); in WH: 33 move overlays `game/assets/movesets/t7/`, stance/move packs in `game/assets/anim/t7/<char>/`, `game/assets/anim/t7/alisa-source/` (asamot.bin/json, asarotsm.arc, asa.mvl) | motbin + rotsm MOTA (0x64/0xC8) | Effectively the whole T7 roster (codes below) | **Yes, generic per code:** `tools/anim/t7_generic_bank_bake.py` (whole bank from the character's own motbin state moves; used for Pond/raven and Ryusan/luckychloe), `t7_c8_stance_bake.py`, `t7_move_resolve.py` + `t7_move_bake.py` (per-move packs), `t7_anim64_to_c8.py` (0x64 via the exe's sampler). Needs Blender + TekkenMannequin + TekkenAnimHelper (documented in the tool headers). |
| **Tekken Tag 1** (arcade System 12) | Decoder only: `teardown/tekken3/tools/tekken3recompiled/tools/ttt1_motion.py` (+ `capture_ttt1_motion.lua`) | System 12 ROM joint motion | — | Decoder exists, but it needs a "verified local ROM bank". **No TTT1 ROM was found** in any WH/GRE release or tree searched. |
| **Tekken 8** | GRE `t8-community-pieces-v1`: `t8_{KING_v2,KING_DLC,BRYAN,HEIHACHI,JIN,SHAHEEN,YOSHIMITSU}.json` + `king/yoshimitsu/bryan/asuka/jin/heihachi/shaheen/bob.json`; `game/assets/anim/t8/clip-maps/` (8 fighters); `tools/tekken8-community/t8_join.py` | TKMovesetExtractor JSON (several are edited community builds, see PROVENANCE.md in the release) | 8 characters | Moveset/clip-map level only; no T8 clip-to-bank converter. |
| Other games (non-Tekken bases) | VF5 Dural bank (private, `game/assets/private/anim/vf5/dural/`, Zen); DOA4 `mot.afs` entries (`doa4-mot-20261022`) and anim definitions; SF EX2 (30 chars) and EX3 (41 PLPACs) clip JSONs (GRE `sfex-phase4-anim-*`); Urban Reign general clips `game/assets/anim/ur-general-*` | various | — | Dural: yes (private build only). DOA4 / SF EX: no converter to a WH bank found in `tools/anim/`. SF EX manifests carry only `P00X`-style IDs. Index → character names are not established there. |

### T7 codes held FULL in GRE (verified 2026-11-05 against the GRE tree)
ste, ask, mut, bob, arb, lee, mrx, asa, ltn, mig, nsa, gan, aki, dra, zaf, lar, lil, jac, kin, jin, hwo, hei,
bry, yos, xia, kum, pan, jul, nin, edd, ann, lei, law, pau, dnc, frv (and the rest of the 57/56/58/53 listing).
Flag carried from `docs/anim/T7-SOURCE-INVENTORY-20261030.md`: `nsa/nsb/nsc/nsdrotsm.arc` are all the same
size (3,800 KB). Check that the content is distinct before baking Negan (nsa).

---

## 2. Roger Jr. (Menajerii): verdict

**Real TTT2 Roger Jr. motion is held, decoded, and already on main as Menajerii's bank.**

| Item | Where |
|---|---|
| Source motbin | `[ROGER]` block in TTT2 `data006` (decoded, sha256 `fa486948…3ebdb2`). Archived as `top__decoded-data006.bin.gz` in WH release `ttt2-work-archive-2026-10-30`. The block base is at data006 file offset 69,032,065. |
| Source clips | bank 1 = `data005` table @ file 0x56B6C04 (90,926,084), 509 entries; bank 2 = `data004` @ 0x100, 1,875 entries (`docs/tech/ttt2-mota/join/bank-tables.json`) |
| Move → clip join | `docs/tech/ttt2-mota/join/roger-join.json` (2,180 records) |
| Move list (notation) | `game/assets/ttt2/movesets/rog.json` (84 moves, MVLT data018) |
| Decoders | `tools/ttt2_mota_decode64.py` (0x64), `tools/ttt2_mota_decode.py` (0xC8) |
| Converter (to WH bank) | `tools/anim/ttt2_bank_bake.py` (slots) → `tools/anim/ttt2_bank_rows.py --bank roger` (rows) |
| Built bank (on main) | `game/assets/anim/t3/roger/`: 15 slot clips (neutral, walk f/b, dash f/b, crouch, crouch_hold, jump up/f/b, sidestep_a, medium, heavy, grab, hit), `rows.pack.json` (323 move rows), `hit_frames.json` (336 rows), `skeleton.json` |
| Wiring | `game/js/fighter.js` `FIGHTER_BANK.menajerii = 'roger'`; `game/js/t3anims.js` `T3_BANKS.roger` (PRs #1557, #1558, #1581) |
| Proof | `docs/proof/2026-11-04/ttt2-banks/menajerii-roger-bank-proof-20261104.mp4`, `docs/proof/2026-11-05/roster-100-s5/bake-report-roger.json` |

What is still open on Roger Jr. is **wiring, not source**:
- No slot clip for t3_light, t3_block, t3_hit_launch, t3_ko or t3_sidestep_b in `game/assets/anim/t3/roger/`.
- `game/assets/movesets/menajerii.json` (193 moves): only 3 moves carry a `t3_row`. 139 still point their
  `anim_t3` at the placeholder bank `tekken-wiki`, and 39 carry `ttt2_source: roger`. The 323 real Roger rows in
  `rows.pack.json` are not yet mapped to her move inputs. Next step: map moves → `roger-join.json` records → `t3_row`.
- Draft PR #1547 (source frame table) and its two open owner calls (damage source; 12 Kuma-sourced moves on
  Roger inputs) are unchanged.

Megami / Jun is in the same state: `game/assets/anim/t3/jun/` is real TTT2 Jun. In `game/assets/movesets/megami.json`,
270 of 304 moves still carry the class-stamp `anim_t3` row 48 (135 `jun`, 135 `tekken-wiki`).

---

## 3. Every Western Heart fighter: base, current bank, held real source

Roster = the 59 entries (29 own + 19 stand-in-with-source + 1 owner call + 10 no Tekken source = 59) of `game/js/roster-full.js`. "Bank" was computed from main's `bankIdFor` rules
(FIGHTER_BANK, then `game/assets/movesets/index.json` anim_bank/t3_source, then MOVESET_MAP).
"T7 overlay" = a real T7 stance (S) and/or per-move pack (M) from `T7_STANCES` / `T7_MOVES` in `game/js/t3anims.js`.
An overlay sits on top of the bank. Every action without an overlay clip still plays from the bank.

### 3a. Already on their own base's bank (29)

| Fighter | Base | Bank | T7 overlay | Optional later upgrade held |
|---|---|---|---|---|
| rin | Jin | jin (T3) | – | T7 JIN FULL; TTT2 [JIN] |
| tou | Paul | paul (T3) | – | T7 PAU FULL; TTT2 [Paul] |
| sha | Xiaoyu | xiaoyu (T3) | S M | T7 XIA FULL |
| kai | Eddy | eddy (T3) | – | T7 EDD FULL; TTT2 [EDDY] |
| retsu | Bryan | bryan (T3) | S M | T7 BRY FULL |
| gyou | Hwoarang | hwoarang (T3) | S M | T7 HWO FULL |
| pantera | King | king (T3 on Leo-man rig) | S M | T7 KIN FULL |
| demonio | Jin | jin (T3) | – | T7 JIN FULL |
| phantom | Yoshimitsu | yoshimitsu (T3) | S M | T7 YOS FULL |
| diablo | Heihachi | heihachi (T3 on Jin skeleton) | S M | T7 HEI FULL |
| skull | Bryan | bryan (T3) | S M | T7 BRY FULL |
| samura1 | Jack-7 | gunjack (T3 Gun Jack, predecessor) | – | **T7 JAC FULL**. This is the only way to get Jack-7 himself. |
| sakura | Xiaoyu | xiaoyu (T3) | S M | T7 XIA FULL |
| kingtyrant | Eddy | eddy (T3) | – | T7 EDD FULL |
| awapop | Nina | nina (T3) | – | T7 NIN FULL |
| nightwolf | Julia | julia (T3) | S M | T7 JUL FULL |
| torch | Anna | anna (T3) | – | T7 ANN FULL |
| docfrank | Bosconovitch | bosconovitch (T3) | – | TTT2 [Bosconovitch] + `bcv.json` |
| dorowani | Gon | gon (T3) | – | – |
| chatur | True Ogre | ogre (T3 divmot14) | – | **TTT2 [GreenOgre] motbin + `game/assets/ttt2/movesets/gre.json` (True Ogre, 75 moves)**. ROUND4 §7 said no True Ogre TTT2 file exists. The index shows one. |
| pond | Raven | raven (= T7 **Master** Raven, frv) | S M | Classic Raven: TTT2 [RAVEN] + `rav.json`; T6 `t6psp-raven-moveset-v3.json` |
| ryusan | Lucky Chloe | luckychloe (T7 dnc) | S M | – |
| tobi | Hwoarang | hwoarang (T3) | S M | T7 HWO FULL |
| megami | Jun | jun (TTT2) | – | moves→rows wiring (§2) |
| menajerii | Roger Jr. | roger (TTT2) | – | moves→rows wiring (§2) |
| rave | Lei | lei (T3) | – | T7 LEI FULL; TTT2 [Lei_Wulong] |
| buffalo-bill | Law | law (T3) | – | T7 LAW FULL |
| gashadokuro | Kuma | kuma (T3) | S M | T7 KUM FULL |
| aotsuki | Panda | kuma (T3, Panda shares Kuma in T3) | S M (panda) | **T7 PAN FULL; TTT2 [PANDA]** (own bank possible) |

### 3b. On a stand-in bank, real character held (19 can move off stand-ins)

| Fighter | Base | Current bank (stand-in) | Held real source (exact) | Converter |
|---|---|---|---|---|
| zui | Steve Fox | jin | GRE `…/mothead/{bin/stemot.bin, json/stemot.json, mask/sterotsm.arc, movelist/ste.mvl}`; TTT2 [Steve_Fox] + `game/assets/ttt2/movesets/ste.json`; `game/assets/movesets/t7/t7-steve-lp-rp-lk-rk.json` | `tools/anim/t7_generic_bank_bake.py --code ste` |
| kinpo | Asuka | jin | GRE `askmot.bin/askmot.json/askrotsm.arc/ask.mvl`; GRE `t7-rotsm-clips-v1/ask_clips.bin`; TTT2 [Asuka] + `ask.json`; `teardown/tekken6/movesets/t6psp-asuka-moveset-v3.json`; T8 `asuka.json` | t7_generic_bank_bake `--code ask` |
| waterfall | Josie | jin | GRE `mutmot.bin/mutmot.json/mutrotsm.arc/mut.mvl`; `t7-josie-lp-rp-lk-rk.json` | `--code mut` |
| burger | Bob | bryan (+ T7 Bob stance) | GRE `bobmot.*/bobrotsm.arc/bob.mvl`; `bob_clips.bin`; TTT2 [BOB_SATSUMA] + `bob.json`; `game/assets/anim/t7/bob/` | `--code bob` |
| scimitar | Shaheen | jin | GRE `arbmot.*/arbrotsm.arc/arb.mvl`; `arb_clips.bin`; T8 `t8_SHAHEEN.json` (hash-clean) | `--code arb` |
| purplerain | Lee | jin (+ T7 Lee S M) | GRE `leemot.*/leerotsm.arc/lee.mvl`; TTT2 [LEE] + `lee.json`; `t6psp-lee-moveset-v3.json`; `game/assets/anim/t7/lee/` | `--code lee` (bank for the generic actions) |
| dio | Akuma | heihachi | GRE `mrxmot.*/mrxrotsm.arc/mrx.mvl`; `t7-akuma-lp-rp-lk-rk.json` | `--code mrx` |
| cyborgx | Alisa | gunjack | GRE `asamot.*/asarotsm.arc/asa.mvl` (copy also in WH `game/assets/anim/t7/alisa-source/`); TTT2 [Alisa] + `asa.json` | `--code asa` |
| michiko | Katarina | jin | GRE `ltnmot.*/ltnrotsm.arc/ltn.mvl`; `t7-katarina-lp-rp-lk-rk.json` | `--code ltn` |
| bruno | Miguel | bryan | GRE `migmot.*/migrotsm.arc/mig.mvl`; TTT2 [Miguel] + `mig.json` | `--code mig` |
| negativo | Negan | bryan (+ T7 Negan S M) | GRE `nsamot.*/nsarotsm.arc/nsa.mvl` (size flag above); `game/assets/anim/t7/negan/` | `--code nsa` |
| thor | Ganryu | bryan | GRE `ganmot.*/ganrotsm.arc` (gan.mvl); TTT2 [GANRYU] + `gan.json` | `--code gan` |
| yukihyo | Armor King | armorking (King's motion) | GRE `akimot.*/akirotsm.arc/aki.mvl` (AKI = Armor King, `teardown/tekken7/TEKKEN7-ROSTER-MAPPING.md`); TTT2 [ARMOR_KING] + `aki.json`; `t6psp-armor-king-moveset-v3.json` | `--code aki` |
| slice | Dragunov | bryan | GRE `dramot.*/drarotsm.arc/dra.mvl`; TTT2 [Dragunov] + `dra.json`; `t6psp-dragunov-moveset-v3.json` | `--code dra` |
| mariposa-monarch | Zafina | xiaoyu | GRE `zafmot.*/zafrotsm.arc/zaf.mvl`; TTT2 [ZAFINA] + `zaf.json`; `t6psp-zafina-moveset-v3.json` | `--code zaf` |
| chordz | Lars | jin (+ T7 Lars S M) | GRE `larmot.*/larrotsm.arc/lar.mvl`; TTT2 [Lars] + `lar.json`; `game/assets/anim/t7/lars/` | `--code lar` |
| silvertongue | Lili | xiaoyu | GRE `lilmot.*/lilrotsm.arc/lil.mvl`; TTT2 [EMILIE] + `lil.json` | `--code lil` |
| star | Christie | xiaoyu | Not in T7. TTT2 [CHRISTIE] motbin in data006 + `game/assets/ttt2/movesets/chr.json` (164 moves) | TTT2 tools, after extending `ttt2_bank_rows.py`/`ttt2_bank_bake.py` beyond roger/jun (join extract + data005 bank-1 fingerprint, ROUND4 §3–§4) |
| baek-master-white | Kevin / Baek (roster says "Kevin"; index `tekken_base` says "Baek") | bryan | Not in T7. TTT2 [BAEK_DOO_SAN] + `bae.json`; `t6psp-baek-doo-san-moveset-v3.json` (moves only) | same TTT2 extension. **Owner to confirm the base is Baek.** |

Count: **17** stand-ins can move with the existing generic T7 converter (zui, kinpo, waterfall, burger, scimitar,
purplerain, dio, cyborgx, michiko, bruno, negativo, thor, yukihyo, slice, mariposa-monarch, chordz, silvertongue).
**2** more can move once the existing TTT2 converter is extended past roger/jun (star, baek-master-white).
**19 total.**

### 3c. Owner call needed before any bank change (1)

| Fighter | Roster base | Bank | Note |
|---|---|---|---|
| byou | Lei Wulong (roster-full.js) | jin (via moveset `demonio`) | Owner ruling quoted in `game/js/fighter.js`: "Lei wulong is not byou, he is Rave". The roster `base` string still says Lei. If the owner names Byou's base, the held source follows from §1. |

### 3d. No held Tekken source for the real character (10; Zen has a private non-Tekken bank)

| Fighter | Base | Current bank | What is held / not held |
|---|---|---|---|
| dxmmii-patchwork | Mokujin | jin | T3 divmot15 is empty on the owner's disc. Mokujin has no motbin of his own in TTT2 data006 (not in the 66-block list). Not in T7. **Nothing held.** |
| zen | Dural (owner decision 2026-10-24; roster `base` still says Heihachi) | null in public builds | VF5 Dural bank exists **privately** (`game/assets/private/anim/vf5/dural/`, private build only) |
| charger | Blanka (SF) | bryan | Not a Tekken character. SF EX clip JSONs are held in GRE, but no Blanka mapping or converter. |
| kronos | Zangief + Golem (Urban Reign) | king | Urban Reign general clips in `game/assets/anim/ur-general-*` and `game/assets/movesets/ur-char*.json`; no own bank built |
| deathfang | Iori (KOF) | heihachi | No KOF motion held (`docs/anim/DEATHFANG-ANIM-GAP-20261023.md`) |
| ryuji, ryuji-rock | Ryuji Yamazaki (+ The Rock) | king | No KOF motion held |
| koreshi | Kakashi + Super Saiyan | heihachi | None |
| vainabel | Bass Armstrong (DOA) | none | DOA4 `mot.afs` entries held (WH release `doa4-mot-20261022`). No DOA4 → WH bank converter in `tools/anim/`. |
| cainelias | Undertaker (WWE) | king | WWE 2K19 teardown (moves); no motion converter |

---

## 4. What this means

- The owner is right. Every Tekken-based fighter now on a stand-in has their real character in our holdings:
  17 in the Tekken 7 GRE mothead tree and 2 more in the TTT2 data006 motbins. Most of the 17 are also in TTT2.
- Tekken 7 has a generic, already-used converter (`tools/anim/t7_generic_bank_bake.py`) and is the fastest
  route. TTT2 has a proven converter that is hard-coded to roger/jun. Generalising it is the next tool job.
- Tekken 5 and Tekken 6 hold move lists (T6: 18 decoded) and raw discs. **Neither has a clip decoder**, so
  neither can supply motion today. TTT1 has a decoder but no ROM held.
- Roger Jr. needs no new source. The remaining job is wiring Menajerii's moves to the 323 real rows already shipped.
