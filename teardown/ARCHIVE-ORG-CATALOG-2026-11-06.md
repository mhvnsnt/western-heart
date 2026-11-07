# Archive.org Catalog — 2026-11-06

**Sweep date:** 2026-11-06 (America/Chicago). **Method:** live archive.org
advancedsearch + metadata APIs; every candidate's REAL file list (names, sizes,
formats) inspected — never judged by title. Misses got a second pass with
full-text, product-code (BLUS/BLES), and identifier-wildcard queries. Two items
were inspected down to their internal file lists (a 360 GB No-Intro set and the
Tekken 6 regional set). Held status cross-checked the same day against all
GitHub releases on `mhvnsnt/game-reverse-engineering` (GRE) and
`mhvnsnt/western-heart` (WH) plus WH
`docs/handoffs/TEKKEN-HOLDINGS-GAP-AUDIT-2026-11-06.md`. This file is mirrored
identically in both repos (GRE root + WH `teardown/`).

> ## ARCHIVE-ORG-FIRST LAW (owner 2026-11-06)
> For ANY game acquisition or teardown pull, **archive.org is checked FIRST** —
> before Steam, before stores, before torrents, before anywhere else. Only when
> archive.org verifiably does NOT have the game — checked LIVE via its
> search/metadata API with the item's actual files inspected (names, sizes,
> formats), never a title guess — do we move to another source. A stale
> "not on archive.org" note is NOT a check: catalogs change. Proof case: SCVI
> was recorded absent in Oct 2026 and was sitting on archive.org in Nov 2026
> while lanes burned hours on the Steam route and a purchase decision got put
> in front of the owner. Every acquisition brief names the archive.org check
> and its date. Every lane, every game, every time.

**Verdict key:** FOUND-COMPLETE = the item's files are a complete game copy
(disc image / full install archive at the title's real size class).
FOUND-UNVERIFIED = a copy exists but completeness cannot be proven from its
file list — internal contents must be read at pull time. NOT FOUND = searched
with the method above, verifiably absent as of the sweep date (absence
expires; re-check before concluding anything). PARTIAL = only a subset exists
(DLC / demo / free-to-play subset / update files).

## A. Known gaps (checked first)

| Game | Platform | IA identifier | Size | Format (from file list) | Verdict | Gap it fills | Held status |
|---|---|---|---|---|---|---|---|
| Tekken 8 | PC | `tekken-8-ultimate-edition-2024-all-dlc` | 11,708,243,811 B item | Single RAR (`040470r.ER-GameDrive.Org.rar`) | **FOUND-UNVERIFIED** — uploader claims Ultimate Ed. v3.00.02 + all DLC, but 11.7 GB is far below T8's real install class; the RAR's internal file list MUST be read before treating this as the game | Fill 4; the 81 WH moves that are strong T8-only candidates | NOT-HELD (community TKData pieces for 6 fighters + 1 frame file + Law anim slice only) |
| Tekken 6 | PS3 | `tekken-6-europe-en-ja-fr-de-es-it-ko-ru-v-02.00` | 3 regional disc zips, 12,267,59x,xxx B each (USA zip 12,267,591,621 B, md5 `629ca9122a10876e7e85f1994806cb65`) | Redump-style regional disc zips: Europe (v02.00), Japan (v01.00), USA | **FOUND-COMPLETE** — pull needs ONE region zip only (USA) | Scenario Campaign + PS3 stage geometry (PSP packages provably carry no stage geometry) | HELD-UNVERIFIED (WH release `tekken6-ps3-full-v1` is a Draft, never verified) |
| Tekken 6 | PS3 (alt) | `tekken-6.-play-station-3` | 11,474,930,053 B | Single zip, folder rip | FOUND-COMPLETE (alt copy) | Same as above | NOT-HELD |
| Tekken 6 | Arcade (System 357) | `Tekken6BRVer4-Namco357` | 13,628,818,952 B item | Raw HDD image rar 8,325 MB + HDD contents zip 5,292 MB + dongle zip | FOUND-COMPLETE (arcade BR Ver.4) — no Scenario Campaign (console-only mode) | Arcade-original BR data | NOT-HELD |
| Tekken Tag Tournament 2 | PS3 | `tekken-tag-tournament-2-unlimited-r-2-prpcs-3.-7z` | `Tekken Tag Tournament 2 Unlimited (R2PRPCS3).7z` 6,272,135,887 B, md5 `4e86d833b1ba5fd5dbdd47a7149c99ec` | 7z, RPCS3-ready PS3 build | **FOUND-COMPLETE** — PS3 route avoids the held 360 STFS container entirely | ~57 unbuilt character banks + stages (extraction never ran on held data) | HELD (360 full archive: WH release `ttt2-7z-v1`, 13,363,624,393 B in 26 chunks) |
| Tekken Tag Tournament 2 | Xbox 360 | `tekken-tag-tournament-2_202609` | 13,363,711,580 B item | Single 7z 13,364 MB | FOUND-COMPLETE (same size class as the held 7z; likely the same STFS archive) | Same as above | HELD (same as above) |
| Tekken Tag Tournament 2 | Xbox 360 | `tekken-tag-tournament-2-tu-3-final.-7z` | 8,590,418,857 B item | 7z, game + TU3 | FOUND-COMPLETE (alt) | Same as above | HELD (base archive) |
| SoulCalibur IV (base game) | PS3 / 360 | — | — | — | **NOT FOUND** (2026-11-06, see §D) | SC creation-system + roster data | NOT-HELD |
| SoulCalibur IV (DLC/updates only) | PS3 | `soul-calibur-iv-RPCS3` (4,916,231,864 B zip titled "DLC + ONLINE"), `soul-calibur-iv-usa-all-dlc-pack-fix-blus-30160` (99,452,669 B), `soul-calibur-iv-all-dlc-complete` (360 DLC set), update pkgs | ~5.1 GB total | Zips + PKGs of DLC/update content only; item `soul-calibur-iv` exists but holds ZERO game files | PARTIAL — DLC and updates with no base game to attach to | — | NOT-HELD |
| SoulCalibur V | PS3 (JP) | `soulcalibur-v-bljs-10115` | File `SOULCALIBUR Ⅴ [BLJS10115].rar` 7,557,277,117 B, md5 `de2cb4d409e13d0712866e0b8498b9e8`, sha1 `8e68ce4876a4c3dd04891d0e21c07cb26d78a913` (re-verified 2026-11-06) | Single RAR, full BLJS10115 disc archive | **FOUND-COMPLETE** | SCV roster/creation data; SC lane's standing gap | NOT-HELD |
| SoulCalibur V | Xbox 360 (alt) | `soulcalibur-v-nude-version-xbox-360-dlc-4-e-4-d-083-d` | RAR 6,723 MB | Modded 360 build + DLC | FOUND-COMPLETE but MODIFIED build — prefer the PS3 retail copy | Same as above | NOT-HELD |
| Dead or Alive 6 | PC | `dead.or.-alive.-6.v-1.22.-incl.-all.-dlcs` | Zip 62,512,519,293 B | Single zip, v1.22 + all DLCs | **FOUND-COMPLETE** | DOA6 binary (GRE status row: "mechanics doc only, game binary not acquired") | NOT-HELD |
| Dead or Alive 6 | PC (alt) | `dead-or-alive-6-repack` | Zip 62,377,908,124 B | Single zip | FOUND-COMPLETE (second independent copy) | Same as above | NOT-HELD |
| Dead or Alive 5 Last Round | PC | `DeadOrAlive5LastRound_378` | 13,341,858,999 B item | Split-zip set (z01… + zip, 23 files) | **FOUND-COMPLETE** | DOA5LR full roster/movesets | NOT-HELD (DOA4 is held extensively; DOA5/6 are not) |
| Dead or Alive 5 (vanilla) | PC | `dead-or-alive-5` | 8,611,893,333 B item | DOA5DVD1.iso 4,295 MB + DOA5DVD2.iso 4,316 MB | FOUND-COMPLETE | Vanilla DOA5 | NOT-HELD |
| Dead or Alive 5 Last Round | PS3 (JP) | `redump_disc_96268` | ISO 9,092,006,838 B | Redump disc ISO | FOUND-COMPLETE (console alt) | Same as LR row | NOT-HELD |
| Dead or Alive 5 Last Round: Core Fighters | PC | `dead-or-alive-5-last-round-core-fighters-pc` | 10,738,960,774 B item | Installer bins (xatab) | PARTIAL by design — the free-to-play subset, not the full roster | — | NOT-HELD |
| Tekken 5: Dark Resurrection | PSP | `tekken-dark-resurrection-usa-psp_202603_ver2` (+ 4 more PSP copies) | ISO 1,750 MB (ULUS-10139) | PSP ISO | **FOUND-COMPLETE** | DR roster deltas over held T5 PS2 | NOT-HELD (T5 PS2 held; DR is not) |
| Tekken 5: Dark Resurrection | Arcade (System 246) | `tekken-5-dark-resurrection-ted-1-ver.-a-2005-namco-system-246-tp` | Zip 2,671,685,702 B | [TP] arcade dump zip | FOUND-COMPLETE (arcade) | Arcade-original DR | NOT-HELD |
| Tekken 5: Dark Resurrection | PS3 | inside junk bundles `tekken-dark-resurrection_202508` / `tekken-dark-resurrection_202603` | `Tekken Dark Resurrection.iso` 1,888 MB inside items padded with an unrelated TEKKEN 7 Season Pass 4 zip (54,509 MB) + a VPN iso | ISO inside a contaminated bundle | FOUND-UNVERIFIED — do NOT pull the bundle items; the bare ISO's provenance is unproven | PS3 DR Online build | NOT-HELD |
| Tekken 4 | PS2 | `tekken-4-us-ps-2-archive-1` (ISO 2,698 MB), `tekken-4_202602` (same ISO), `tekken-4-ps-2-classics-slps-25100` (PKG 2,750 MB) | ~2.7 GB each | PS2 ISO / PS2-Classics PKG | **FOUND-COMPLETE** | T4 roster/banks (fills the T3→T5 motion gap) | NOT-HELD as a binary (WH `teardown/tekken4/` holds teardown files; no ISO on any release) |

## B. The teardown universe

| Game | Platform | IA identifier | Size | Format (from file list) | Verdict | Need it serves | Held status |
|---|---|---|---|---|---|---|---|
| Virtua Fighter 5 | PS3 | — (see held) | — | — | Held already: WH release `vf5-ps3-v1` (BLES00029), teardown scored 100% | Zen's VF5/Dural layer, VF systems | HELD |
| Virtua Fighter 5 Final Showdown | PS3 / 360 (download title) | — | — | — | **NOT FOUND** (2026-11-06, see §D; every game-sized candidate inspected was a video of the game, incl. the Giant Bomb Quick Look) | FS balance/anim deltas over held VF5 | NOT-HELD |
| Def Jam: Fight for NY | PS2 | `slus-210.04.-def-jam-fight-for-ny` | ISO 4,695 MB | PS2 ISO (+ 2 prototypes and the PSP "Takeover" on IA) | FOUND-COMPLETE (also already held) | Creation-suite templates (CAW) | HELD (release `defjam-ps2-iso-v1` on `mhvnsnt/def-jam-fight-for-ny`; WH teardown files) |
| Def Jam Vendetta | PS2 | `slus-206.39.-def-jam-vendetta` | ISO 2,216 MB | PS2 ISO | **FOUND-COMPLETE** | Creation-suite lineage, roster/moves | NOT-HELD |
| Def Jam Icon | PS3 (JP) | `def-jam-icon-bljm-60029` | 7z 7,837 MB (item 7,935,943,455 B) | PS3 disc 7z + scans | **FOUND-COMPLETE** | Icon's fighter-creator templates | NOT-HELD |
| Urban Reign | PS2 | `urban-reign-usa_202608` | ISO 4,141 MB | PS2 ISO (+ Jul 2005 prototype on IA) | FOUND-COMPLETE (also already held) | AshLane's base game systems | HELD (WH release `urban-reign-iso-v1`) |
| WWE 2K19 | PC | `WWE_2K19_CSF` | 7z 50,956 MB ("Clean Steam Files", Build 3467910) | 7z full install | **FOUND-COMPLETE** (second copy: `wwe-2k19`, 7z 49,507 MB) | Full 2K19: CAW system + complete anim set (held teardown has models only) | NOT-HELD as a binary (WH `teardown/wwe2k19/` = 1,677 extracted model files) |
| WWE 2K15 | PC | `WWE_2K15_CSF` | 7z 33,131 MB | 7z full install | FOUND-COMPLETE | WWE creation/moves lineage | NOT-HELD |
| WWE 2K16 | PC | `WWE_2K16_CSF` | 7z 45,267 MB | 7z full install | FOUND-COMPLETE | Same | NOT-HELD |
| WWE 2K15–2K20 (collection) | PC | `wwe-2-k-15` ("[PC] WWE 2K Collection (2K15-2K20)") | Item 277,376,999,987 B; per-game RARs: 2K17 51,747 MB, 2K20 51,312 MB, 2K19 50,827 MB, 2K18 46,196 MB + 2K15/2K16 | Per-game RARs inside one item — each file downloadable individually | FOUND-COMPLETE (all six titles, one item) | Whole 2K arc for the creation suite | NOT-HELD |
| WWE SmackDown vs Raw (2004) | PS2 | `wwe-smack-down-vs-raw` | RAR 2,331 MB | PS2 game rar | FOUND-COMPLETE | SvR creation lineage | NOT-HELD |
| WWE SmackDown vs Raw 2011 | PC | `wwe-smackdown-vs.-raw-2011-in-all-qualities-unlock-all-version-full-original-lit` | RAR 3,252 MB | Uploader-modified "unlock all" PC build | FOUND-COMPLETE but MODIFIED — flag before use | Same | NOT-HELD |
| WWE SmackDown vs Raw 2006–2010 (retail) | PS2/PS3/360 | — | — | — | NOT FOUND as retail copies (2026-11-06); SvR 2009 exists on IA only as two PROTOTYPE builds (`WWESmackDownvsRaw2009Aug282008prototype` 4,611 MB, `WWESmackDownvsRaw2009Prototype` 4,448 MB) — prototypes catalogued, they are not retail | Same | NOT-HELD |
| The King of Fighters XIII | PC | `King_of_Fighters_XIII_CSF` | 7z 2,047 MB (Steam Edition, Build 222940) | 7z full install | **FOUND-COMPLETE** (console alts: Redump ISOs `redump_disc_36445` USA / `redump_disc_57145` EU, 2,611 MB each; Galaxy Edition rar 2,086 MB) | KOF systems/movesets | NOT-HELD |
| The King of Fighters XIV | PS4 / PC | — | — | — | **NOT FOUND** (2026-11-06, see §D) | KOF XIV roster | NOT-HELD |
| The King of Fighters XV | PS4/PS5 / PC | — | — | — | **NOT FOUND** (2026-11-06, see §D) | KOF XV roster | NOT-HELD |
| Street Fighter V | PC | `street.-fighter.-v.-championship.-edition.v-7.010.-incl.-all.-dlc` | Zip 55,356 MB (item 55,356,596,917 B) | Single zip, Champion Edition v7.010 + all DLC | **FOUND-COMPLETE** | SFV roster/systems (GRE status row: "SFV acquisition needs call" — this is the call) | NOT-HELD |
| Street Fighter 6 | PC / PS | `street-fightertm-6-multi-13.rar` | RAR 2,125 MB | Single small rar | **NOT FOUND complete** — SF6 is a ~50 GB-class game; the only candidate is a 2.1 GB rar (partial/unproven contents) plus MUGEN fan builds (fan junk) | SF6 roster | NOT-HELD |
| Ultra Street Fighter IV | PS3 | `ultra-street-fighter-iv-blus-31218` | ISO 17,839 MB | PS3 disc ISO (360 alt: `ultra-street-fighter-iv.-xbox-360`, zip 8,254 MB) | **FOUND-COMPLETE** | SFIV systems (GRE row 15 had SFIV/USFIV "blocked on disk + owner go-ahead" — now sourced) | NOT-HELD |
| Street Fighter X Tekken | PS3 | `street-fighter-x-tekken-blus-30722` | ISO 13,949 MB | PS3 disc ISO (alt: `street-fighter-x-tekken-rpcs3` zip 14,156 MB) | **FOUND-COMPLETE** | The Tekken-side crossover cast (incl. the T7-join guest data) | NOT-HELD |
| Street Fighter X Tekken | PC | `street-fighter-x-tekken-pc-fix-v-1.1` | Zip 6,346 MB | Modded PC build ("Complete PC Fix") | FOUND-COMPLETE but MODIFIED — prefer the PS3 retail ISO | Same | NOT-HELD |
| Mortal Kombat X / XL | PC / PS4 / XB1 | — | — | — | **NOT FOUND** (2026-11-06, see §D; IA holds only the iOS app IPAs and one EMPTY item `mortal.kombat.x` with zero game files) | MK systems/roster | NOT-HELD |
| Mortal Kombat 11 | ? | `mortal-kombat-11_202508` | Single ISO 116,736 MB (item 116,758,809,320 B) | One opaque .iso | **FOUND-UNVERIFIED** — size is in MK11 Ultimate's class but MK11 was never distributed as a PC ISO; internal verification required before any pull is trusted | MK11 roster/systems | NOT-HELD |
| Mortal Kombat 9: Komplete Edition | PC | `flt-mkka_202601` | DVD1 ISO 8,542 MB + DVD2 ISO 1,504 MB | FLT scene release, 2 ISOs (alts: GOG-style setup-bin set 17,677 MB in `mortal-kombat-komplete-edition-hoanglong`; no-install rar 9,076 MB) | **FOUND-COMPLETE** | MK9 roster/systems | NOT-HELD |
| Guilty Gear Xrd REV 2 (+ SIGN) | PC | `guilty-gear-xrd-rev-2_202404` | Steam-Rip 7z 12,899 MB + `-REVELATOR-` ISO 9,231 MB in one item (22,130,601,904 B) | 7z + ISO, REV 2 v2.10b + 12 DLC | **FOUND-COMPLETE** (more copies: `CA-WINDOWS-Guilty-Gear-Xrd-Rev-2` 12,536 MB, `guilty-gear-xrd-rev-2_202610` 12,319 MB; SIGN: `guilty-gear-xrd-sign_202403` ISO 7,760 MB) | ArcSys anim/system reference | NOT-HELD |
| Guilty Gear Strive | PC | `guilty-gear-strive-deluxe-edition` | RAR 19,568 MB (item 19,568,740,152 B) | Single rar, Deluxe Edition | **FOUND-COMPLETE** | Strive roster/systems | NOT-HELD |
| Guilty Gear Strive (dev builds) | PC | `ggst-arcrevo2019-build` (7,831 MB), `ggst-reveal2019-build` (3,694 MB) | Debug product zips (`GGXrd3_Win64_Product_Debug…`) | Leaked 2019 dev builds | FOUND (dev builds — bonus RE material, not retail) | Pre-release system data | NOT-HELD |
| Samurai Shodown (2019) | PS4 / PC / XB1 | — | — | — | **NOT FOUND** (2026-11-06, see §D; IA's Samurai Shodown holdings are the NeoGeo titles, iOS ports, and the PS1 RPG) | 2019 SamSho roster | NOT-HELD |
| Bloody Roar 3 | PS4 (PS2 Classics) | `bloodyroar3-ps4` | PKG 703 MB (UP9000-SLUS20212) | PS4 PKG wrapping the PS2 SLUS-20212 build | **FOUND-COMPLETE** (the other BR3 item, `bloody-roar-3-japan-v-1.02-new-opening`, is an xdelta PATCH only — not a game) | BR beast-form systems | NOT-HELD |
| Bloody Roar 4 | PS2 | `bloody-roar-4-ps2` (ISO 1,294 MB), `slus-207.95.-bloody-roar-4` (same ISO), `bloody-roar-4-ps-2-para-ps-3-sles-51877_202405` (RAR 1,317 MB) | ~1.3 GB | PS2 ISOs | **FOUND-COMPLETE** | Same | NOT-HELD |
| Power Stone 1 + 2 | PSP | `power-stone-collection-usa` | Zip 319,686,493 B | PSP Collection (both games) | **FOUND-COMPLETE** (PSP route) | Power Stone arena-brawler systems | NOT-HELD |
| Power Stone 2 | Dreamcast | `power-stone-2_202508` (RAR 293 MB), `cdi-power-stone-2-pal-rdc.-7z` (281 MB) | ~0.3 GB | CDI selfboot rips (downsampled video) + two Apr-2000 prototypes | PARTIAL quality — CDI rips are content-complete but video-compressed; a full GDI was NOT FOUND | Same | NOT-HELD |
| Project Justice (Rival Schools 2) | Dreamcast | `project-justice-rival-schools-2-v-1.001-2000-virgin-pal` | CHD 868 MB (v1.001 PAL) | CHD disc image (alt: PAL rar 665 MB; US Dec-2000 prototype 766 MB) | **FOUND-COMPLETE** | Rival Schools team systems | NOT-HELD |
| Ehrgeiz | PS1 | `SLES-02111` (item 700,754,619 B), `psx_ehrgeiz` (item 946,371,205 B incl. derived) | ~0.6–0.7 GB game data | PS1 disc sets | **FOUND-COMPLETE** | Ehrgeiz roster (incl. the FF7 guest cast data) | NOT-HELD |
| Tobal No. 1 | PS1 | `psx_tobal1` | Item 646,145,858 B | PS1 disc set | **FOUND-COMPLETE** | Tobal quest/fighter systems | NOT-HELD |
| Tobal 2 | PS1 | `tobal-2-20261011` | Item 2,189,284,403 B | PS1 set (multi-file) | **FOUND-COMPLETE** | Same | NOT-HELD |
| Bushido Blade | PS1 | `psx_bblade` | Item 563,313,957 B | PS1 disc set | **FOUND-COMPLETE** | Weapon-fighter systems | NOT-HELD |
| Bushido Blade 2 | PS1 | `psx_bblade2` | Item 697,832,775 B | PS1 disc set | **FOUND-COMPLETE** | Same | NOT-HELD |
| SoulCalibur III: Definitive Edition | PS2 (fan definitive build) | `soulcalibur-iii-definitive-edition-v-1.20` | RAR 1,788 MB (item 1,788,016,478 B) | RAR, v1.20 | **FOUND-COMPLETE** (located by the SC lane; file list re-verified this sweep) | SCIII roster/systems | NOT-HELD |
| SoulCalibur II HD Online | Xbox 360 | `soulcalibur-ii-hd-online` | GOD 7z 484 MB + ISO 7z 481 MB + game-folder 7z 481 MB + package 7z 500 MB (item 1,950,047,148 B) | XBLA package in 4 encodings (second copy: USA zip 719,040,406 B inside `PS3_NOINTRO_USA_9`) | **FOUND-COMPLETE** | HD-remaster data over the held SD SCII | NOT-HELD (SCII PS2 ISO + Xbox extraction ARE held) |
| SoulCalibur: Broken Destiny | PSP | `soulcalibur-broken-destiny-usa-psp` | ISO 901 MB (item 1,397,335,695 B incl. extras) | PSP ISO | **FOUND-COMPLETE** | SCIV-era portable roster/creation data | NOT-HELD |
| Battle Arena Toshinden 1 + 2 | PS1 | `battle-arena-toshinden-u` (item 283,198,945 B), `TOSHINDEN2-BRDISC` (item 315,772,341 B) | ~0.3 GB each | PS1 disc sets | **FOUND-COMPLETE** | Early 3D weapon-fighter reference | NOT-HELD |
| Fighting Vipers | Saturn | `fightingvipers_saturn` | Item 1,758,775,021 B | Saturn disc set | **FOUND-COMPLETE** (FV2 exists only as a Dec-2000 prototype, `FightingVipers2Dec122000prototype`) | VF-adjacent armor-break systems | NOT-HELD |
| Fighters Megamix | Saturn | `fighters-megamix-usa.-7z` (USA 7z 506 MB), `fightersmegamix_saturn` (JP sets) | ~0.5 GB | Saturn disc images | **FOUND-COMPLETE** | VF/ FV crossover roster | NOT-HELD |
| SoulCalibur VI (control) | PC | `dixen-18-soulcalibur-vi` | Zip 11,441,266,068 B | Zip (FreeArc .dxn payloads inside) | FOUND-COMPLETE — **store in progress** (release `soulcalibur6-archiveorg-20261106`, both repos) | SCVI guard/stamina system data | STORING NOW |

## C. Also surfaced (maps to a real project need)

| Item | What it is | Need |
|---|---|---|
| `PS3_NOINTRO_USA_9` → `Soulcalibur - Lost Swords (USA).zip` (3,615,480,838 B) | The F2P PS3 SoulCalibur (2014), downloadable as a single file out of the 360 GB set | SC creation-system cousin; completes the SC console arc |
| `PS3_NOINTRO_USA_9` → SoulCalibur V DLC zips (~50 files: Cepheus Compatibility Packs 1–8, costume/music packs) | The full SCV PS3 DLC set as individual zips | Pairs with the SCV base pull (§E #1) |
| `tekkentagtournament_playstation2` | Tekken Tag Tournament 1 (PS2), multi-region zips ~457 MB each | Background for the TTT2 banks lane |
| `Tekken_CollectionArchive-LivBs` | Multi-game Tekken collection incl. PSP Dark Resurrection in 5 regions | Regional DR variants |
| Prototypes on IA (all catalogued in the sweep data) | Def Jam FFNY (Aug 2004 ×2), Urban Reign (Jul 2005), SvR 2009 ×2, Power Stone 2 ×2, Project Justice US, Bloody Roar 4 ×2, Fighting Vipers 2, MK (Mar 2011) | Pre-release builds are primary RE material for system history |

## D. NOT FOUND — verified absent as of 2026-11-06 (absence expires; re-check per the law)

| Game | What was checked |
|---|---|
| SoulCalibur IV base game | Title/identifier/product-code (BLUS30160, BLES00296) searches across two passes; every SCIV item's file list read (DLC, updates, one empty item); the 360 GB `PS3_NOINTRO_USA_9` set's full 859-file list read — SCIV appears there ONLY as a 16,372,528 B disc-update zip + DLC zips. No base disc anywhere. |
| Virtua Fighter 5 Final Showdown | 103 hits across two passes (title, full-text, identifier wildcard); every game-sized candidate's files read — all were videos (Giant Bomb Quick Look, G4 trailers) or print (Arcadia command book). Download-title PKGs are simply not on IA today. |
| The King of Fighters XIV | 143 hits across two passes; files inspected — longplays, guidebooks, a frame-data spreadsheet, character mods. No game copy. |
| The King of Fighters XV | 74 hits across two passes; files inspected — trailers, 3D-print models, ads, three hash-named items (~110–160 MB, not identifiable as the game and far below its size). No game copy. |
| Street Fighter 6 (complete) | 90 hits across two passes; the only game-claiming item is a 2,125 MB rar against a ~50 GB-class game; the rest is MUGEN fan builds and combo-trial videos. No complete copy. |
| Mortal Kombat X / XL | 151 hits across two passes; files inspected — iOS IPAs (six versions), combo videos, one empty item. No console/PC copy. |
| Samurai Shodown (2019) | 155 hits across two passes; IA's SamSho holdings are the NeoGeo entries, iOS ports, and the PS1 RPG (fan translation). No 2019 copy. |

## E. Pull queue (in owner-set priority order; SCVI stream-store pattern)

Pattern (proven 2026-11-06 on SCVI): stream the file in 1.9 GB range parts →
sha256 each part → upload to releases on BOTH repos → GitHub API digest must
match → local part deleted → finish with a manifest asset + a full pull-back
verification (stream all parts back, compare whole-file md5/sha1 to the
archive.org metadata values) on both releases. One pull at a time; the disk
guard pauses any pull above 124 GB used on the home volume.

1. **SoulCalibur V** — release tag `soulcalibur5-archiveorg-20261106` (both
   repos). Source file: `SOULCALIBUR Ⅴ [BLJS10115].rar` in item
   `soulcalibur-v-bljs-10115`, 7,557,277,117 B, md5
   `de2cb4d409e13d0712866e0b8498b9e8`, sha1
   `8e68ce4876a4c3dd04891d0e21c07cb26d78a913`. 4 parts. **Status: QUEUED**
   behind the SCVI store (one-at-a-time rule) — the store script is written
   and gated on SCVI's completion marker; see the sweep PROGRESS.md in
   `~/workspace/_archiveorg-sweep-20261106/` for the resume command.
2. **Tekken 6 PS3** — pull ONLY the USA zip `Tekken 6 (USA)
   (En,Ja,Fr,De,Es,It,Ko,Ru).zip` (12,267,591,621 B, md5
   `629ca9122a10876e7e85f1994806cb65`) out of item
   `tekken-6-europe-en-ja-fr-de-es-it-ko-ru-v-02.00` — 7 parts, tag
   `tekken6-ps3-archiveorg-20261106`. Queued behind #1.
3. **TTT2 (PS3)** — `Tekken Tag Tournament 2 Unlimited (R2PRPCS3).7z`
   (6,272,135,887 B, md5 `4e86d833b1ba5fd5dbdd47a7149c99ec`), item
   `tekken-tag-tournament-2-unlimited-r-2-prpcs-3.-7z` — 4 parts, tag
   `ttt2-ps3-archiveorg-20261106`. Queued behind #2. (The 360 game is already
   held; this is the STFS-free platform copy.)
4. **SoulCalibur IV base** — NOT FOUND, nothing to pull. Stays a logged gap.

**Catalogued, not queued** (found complete; pull when the owner sets them in
the order / disk is staged): DOA6 (62.5 GB — needs a staged-space plan),
DOA5LR + vanilla DOA5, Street Fighter V CE (55.4 GB), WWE 2K19 + the 2K
collection (33–277 GB class), MK9 Komplete, GG Xrd REV 2 / Strive, USFIV,
SFxT, KOF XIII, Def Jam Vendetta + Icon, Tekken 4, T5DR (PSP), and the
PS1/Saturn/DC set (Bloody Roar 3/4, Power Stone Collection, Project Justice,
Ehrgeiz, Tobal 1/2, Bushido Blade 1/2, Toshinden 1/2, Fighting Vipers,
Fighters Megamix, SCIII Definitive, SCII HD Online, Broken Destiny).
Tekken 8 and MK11 stay FOUND-UNVERIFIED until a pull reads their internals.

*Sweep data (raw search + metadata JSON, both passes): retained in the sweep
lane's workspace and summarized in this catalog; every verdict above traces
to a file list read on 2026-11-06.*
