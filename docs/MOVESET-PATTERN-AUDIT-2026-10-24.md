# Per-character moveset pattern audit — Western Heart

**Date:** 2026-10-24 (audit of main as of this date; file counts below are from the moveset files on main, not from older coverage snapshots).
**Standing rule (owner directive 2026-10-24, verbatim intent):** "there's certain characters where their moveset is going to need to be built just like how Zen's is but it might be on top of a Tekken character but it's like you know there's variation it depends per character some characters have all a certain character's moveset some have a mix some of them have additives I already told you that you'll have to really research the documentation".

**This audit does NOT assume one pattern for all characters.** Every character below was checked individually against its own moveset file and its own documentation. Where the documentation does not settle the pattern, the row says PATTERN UNCLEAR — no character was defaulted to PURE.

Button names use LP1/RP2/LK3/RK4 everywhere: LP1 = Left Punch = Tekken 1, RP2 = Right Punch = Tekken 2, LK3 = Left Kick = Tekken 3, RK4 = Right Kick = Tekken 4.

## Audit universe (substitution noted honestly)

- The task named a "stance audit" document with 58+ characters as the universe. **No document literally titled "stance audit" was found**: GitHub code search for `"stance audit"` in `mhvnsnt/western-heart` returned 0 hits, and a full repo tree grep found no such file. Per the task's fallback, the universe below is therefore:
  1. The select-screen roster: `game/js/roster-full.js` — **58 fighter ids** (verified by id extraction), and
  2. **2 intake characters with documentation but no roster slot and no moveset file**: Birodo and Jotei.
- Total audit rows: **60**. Variant/attire files (burger-demon, demonio-winged, doc-frank-hood, kronos-attire2, gyou-spirit-body, baek, mariposa, dxmmii, deathfang-werewolf, ryuji-rock, etc.) are NOT separate rows; the roster-slot file is audited and variants are noted where they change the picture. Other-game library files (`t3-*`, `sf-*`, `doa-*`, `vf-*`, `ur-*`) and pure source duplicates (`bob`, `armor-king`, `marduk`, `lili`, `vega`, `zangief`, `hugo`, `iori`, `kutz`, `raiden`, `realizzt`, `blanka`) are NOT roster characters and are excluded.
- `KEVIN` appears in `docs/movesets/COVERAGE-2026-10-23.md` (138 moves) but has no roster slot and no moveset file on current main. It is not counted; see NEEDS-DATA (clarification needed: renamed to baek-master-white, or removed?).

## Counts

| Pattern | Rostered (58) | + No-file intake (2) | Total rows (60) | File moves in pattern | Editor entries in pattern |
|---|---|---|---|---|---|
| PURE | 6 | 0 | 6 | 2,802 | 2,905 |
| MIX | 6 | 0 | 6 | 4,536 | 4,666 |
| ADDITIVE | 41 | 0 | 41 | 23,749 | 24,806 |
| BUILT | 5 | 0 | 5 | 1,175 | 1,221 |
| PATTERN UNCLEAR | 0 | 2 | 2 | 0 (no files) | 0 |
| **Total** | **58** | **2** | **60** | **32,262** | **33,598** |

Headline finding: **the roster is overwhelmingly ADDITIVE, not PURE.** Only 6 of 58 rostered characters ship a single-fighter set with zero extras. The reason is systematic, not per-character: a roster-wide WH-signature expansion put 2 canon signature moves (each with 2 input spellings, so 4 entries) on almost every character. Any audit that calls Pantera or Scimitar "pure" is describing the Tekken base, not the shipped file. The shipped file is base + signatures, which is ADDITIVE by this audit's definitions.

## Classification rules (applied identically to every row)

1. **PURE** = every semantic move traces to ONE fighter, and there are zero WH/canon extras (no `wh_original` moves, no `wh:` animation refs that are canon moves, no `canon:`-tagged originals, no foreign donor moves).
2. **MIX** = moves from TWO OR MORE distinct named fighters/characters, whatever the decode status (decoded T7/T8/T3/TTT2 rows, donor rows, or curated movelist rows all count as sources).
3. **ADDITIVE** = ONE fighter's base (see rule 5) PLUS canon extras on top: WH signature moves, `canon:`-tagged originals (Doc Frank's Gero set), canon-layered moves (Megami's Sealed Door set, Tobi's escape set, Ryusan's corrosion set), or renamed signatures (Charger's Blanka set). Extras never replace base moves.
4. **BUILT** = no decoded base set carries the kit; the kit is authored/curated around a concept, possibly layered on a Tekken character (the Zen pattern). A kit whose only decoded rows are a small minority of an authored file is BUILT, not ADDITIVE.
5. **One fighter across generations = one source.** T8 + T7 + T3 rows for the same fighter (King, Jin, Jack-7/Jack-8/Gun Jack, Eddy, Xiaoyu, etc.) count as ONE source, not a mix. Raven + Master Raven count as one lineage (T8 Raven is the character's return). Law + Forest Law T3 bank rows count as one Law lineage (Forest Law is the T3 Law-line bank).
6. **T3 proxy bank rows do NOT count as a second fighter.** Many files carry T3 bank rows from Jin/Bryan/Xiaoyu/Heihachi/King/Gunjack as animation placeholders (the file's `t3_source` is often a proxy, e.g. Scimitar's T3 rows are Jin-bank rows because Shaheen does not exist in Tekken 3). Pattern is judged on semantic sources (T7/T8/TTT2/DOA/donor/canon rows), with proxy rows noted, never mistaken for a second moveset source.
7. **Devil Jin counts as a second fighter.** It is a distinct Tekken roster entry from Jin Kazama, so Jin + Devil Jin = MIX, not ADDITIVE.
8. **Self-donors do NOT count as a second fighter.** `donor:demonio` inside Demonio files, `donor:docfrank` inside Doc Frank files, and `donor:baek` inside Baek files are the character's own curated sets, not foreign sources.
9. **Coverage counts are NOT file-row counts.** `docs/movesets/COVERAGE-2026-10-23.md` counts a source record as covered if it is present by source id OR by the same canonical notation ("T8 wins over T7 for one input"), so its T8 numbers (e.g. Pantera King 215/215) are much larger than the number of rows carrying a `t8:` merge_source in the file (the merge deduplicates generations onto one key). Both numbers are cited below without conflating them.
10. **File first, docs second, conflicts flagged.** Where a file and a doc disagree (Zen, Gyou, Koreshi, Byou), the pattern follows the shipped file for the roster count, and the conflict is stated in the row — never silently resolved.

## Per-character pattern table

| Character (file) | Pattern | Tekken base (file field) | Moves / editor entries | Sources + evidence |
Row counts are merge_source / t7_move_id rows. The remainder of each file is legacy rows carrying the same fighter's `t3_source`, plus `strings`/`specials` entries, except where the row explicitly names another source (Gyou's Hwoarang legacy, Rave's Byou donors, Kronos's multi-source donors). T3 proxy bank rows (rule 6) are part of that remainder, not extra sources.


|---|---|---|---|---|
| rin (`game/assets/movesets/rin.json`) | **ADDITIVE** | Jin Kazama | 659 / 692 | Jin Kazama (T8 128 + T7 198 + T3 Jin 184) + 2 WH sigs: Cold Dignity, Still Point |
| byou (`game/assets/movesets/byou.json`) | **ADDITIVE** | Lei Wulong | 728 / 728 | Lei Wulong T7 571 + 2 WH sigs: Sickness Pattern, Wrong Foot. CONFLICT: owner order (SOURCE-MERGE 2026-10-21) says Lei = Rave, Byou base unrecorded; file still carries full Lei T7 set. |
| tou (`game/assets/movesets/tou.json`) | **ADDITIVE** | Paul Phoenix | 681 / 715 | Paul Phoenix (T8 159 + T7 210 + T3 Paul 169) + 2 WH sigs: Exists To Fight, No Motive |
| sha (`game/assets/movesets/sha.json`) | **ADDITIVE** | Xiaoyu | 785 / 836 | Xiaoyu (T7 282 + T3 193; T8 175/175 notations covered per COVERAGE-2026-10-23) + 2 WH sigs: Erodes Mountains, Grain Shift |
| kai (`game/assets/movesets/kai.json`) | **ADDITIVE** | Eddy Gordo | 877 / 910 | Eddy Gordo (T8 156 + T7 357 + T3 218) + 2 WH sigs: Doesn't Stop, Lowest Point |
| retsu (`game/assets/movesets/retsu.json`) | **ADDITIVE** | Bryan Fury | 685 / 716 | Bryan Fury (T8 168 + T7 266 + T3 140) + 2 WH sigs: No Mission, Pure Force |
| zen (`game/assets/movesets/zen.json`) | **BUILT** | Heihachi | 639 / 684 | DESIGN (sibling Zen lane): Eleven/Twelve concept (2D) + Dural 3D base + own canon moves + X.COPY as one super. SHIPPED FILE DIFFERS: Heihachi (T8 145 + T7 183 + T3 163) + 2 WH sigs: Does Not Compete, Refused Seat. File pattern alone would be ADDITIVE; design pattern is BUILT. Do not rewire here. |
| gyou (`game/assets/movesets/gyou.json`) | **MIX** | Paul | 1005 / 1023 | DECLARED BASE Paul (T7 86 + T8 47, pull 2026-10-23, PR #823 pattern) + LEGACY Hwoarang majority (T8 209 + T7 326 + T3 188) + 2 WH sigs: Cannot Stop, Everywhere Already. Transitioning file: needs an owner call on the canonical base; Hwoarang rows are history-union residue, not yet re-slotted out. |
| pantera (`game/assets/movesets/pantera.json`) | **ADDITIVE** | King | 874 / 987 | King (T7 297 + T3 199; T8 215/215 notations covered per COVERAGE-2026-10-23) + 3 WH sigs: Honest Hold, Tail-Tip Lunge, Battle Itself. CORRECTS the prior PURE claim: the file is not King-only. |
| demonio (`game/assets/movesets/demonio.json`) | **MIX** | Jin Kazama | 764 / 804 | Jin Kazama (T7 214 + T3 183) + Devil Jin (T7 45 + T8 35) + 3 WH sigs: Apology Burned Away, Rin's Baseline, The Unbowed. Devil Jin counted as a second fighter: it is a distinct Tekken roster entry. |
| phantom (`game/assets/movesets/phantom.json`) | **ADDITIVE** | Yoshimitsu | 1019 / 1087 | Yoshimitsu (T7 386 + T3 193) + 3 WH sigs: Cut Is The Prayer, Mask Slip Spin, Three Seconds Quiet |
| diablo (`game/assets/movesets/diablo.json`) | **ADDITIVE** | Heihachi | 661 / 703 | Heihachi (T7 201 + T3 164) + 3 WH sigs: Declaration Of Conquest, Final Boss Tax, Membrane Tear |
| skull (`game/assets/movesets/skull.json`) | **ADDITIVE** | Bryan Fury | 688 / 721 | Bryan Fury (T7 266 + T3 141) + 3 WH sigs: Paint Ride Flurry, Retribution Keeps Books, Stays Down Stomp |
| samura1 (`game/assets/movesets/samura1.json`) | **ADDITIVE** | Gun Jack | 860 / 907 | Jack line, one fighter across generations (T3 Gunjack 213 + T7 Jack-7 298 + T8 Jack-8 7; T8 199/199 notations covered) + 3 WH sigs: Designation Query, Log Entry 24, Undefined Soul Protocol |
| sakura (`game/assets/movesets/sakura.json`) | **ADDITIVE** | Xiaoyu | 764 / 815 | Xiaoyu (T7 259 + T3 192) + 3 WH sigs: Bloom Opening, Called By Name, You Can't Hit A Song. Saku Ra = Sakura file. |
| zui (`game/assets/movesets/zui.json`) | **MIX** | Steve Fox | 654 / 666 | Steve Fox T7 set (286/287 rows per ZUI-STANCE-SYSTEM-2026-10-21; WALL BOUND skipped as a mechanic row) + T8 Steve 171 + Lei Wulong DRU drunken fist 40 (t7 lei_*) + 2 WH sigs: Beautiful Stumble, Bottle's Honest Truth + legacy Jin T3 proxy rows. Sibling Zui-mix lane owns this character; documented here, not rewired here. |
| kinpo (`game/assets/movesets/kinpo.json`) | **ADDITIVE** | Asuka | 525 / 548 | Asuka (T7 232; T8 146/146 + T7 232/232 covered) + 2 WH sigs: Buttercup Finishes, Plus One Pressure |
| waterfall (`game/assets/movesets/waterfall.json`) | **ADDITIVE** | Josie | 365 / 380 | Josie (T7 219) + 2 WH sigs: I'm Sorry, Nine Souls Grief. T8: Josie not in T8, so no T8 layer. |
| kingtyrant (`game/assets/movesets/kingtyrant.json`) | **ADDITIVE** | Eddy Gordo | 848 / 878 | Eddy Gordo (T7 337 + T3 218) + 2 WH sigs: Coronation Entrance, Dig This. Booker T moves NOT present (SOURCE-MERGE known limit: needs WWE data). |
| burger (`game/assets/movesets/burger.json`) | **ADDITIVE** | Bob | 552 / 583 | Bob (T7 281; T8 161/161 covered) + 2 WH sigs: Appetite's Grip, Side Dish Slam. Base form only; demon/speed-demon/mouth variants are Bob-only variant files. |
| awapop (`game/assets/movesets/awapop.json`) | **ADDITIVE** | Nina | 909 / 962 | Nina (T7 354 + T3 209) + 2 WH sigs: Last Thing You Hear, Pop |
| scimitar (`game/assets/movesets/scimitar.json`) | **ADDITIVE** | Shaheen | 362 / 374 | Shaheen (T7 125; T8 90/90 + T7 125/125 covered) + 2 WH sigs: Closing The Deal, Ledger Entry. CORRECTS the prior PURE claim: the file is not Shaheen-only. |
| purplerain (`game/assets/movesets/purplerain.json`) | **ADDITIVE** | Lee | 569 / 593 | Lee (T7 265) + 2 WH sigs: Encore Bow, Four Four Time. Purple Rain = Lee-based; Hwoarang is Tobi's, not Purple Rain's. |
| nightwolf (`game/assets/movesets/nightwolf.json`) | **ADDITIVE** | Julia | 554 / 570 | Julia (T7 236 + T3 183) + 2 WH sigs: Ancestors Answer, Sage For The New Face |
| dio (`game/assets/movesets/dio.json`) | **ADDITIVE** | Akuma | 275 / 275 | Akuma (T7 136; 131/136 covered, 96%) + 2 WH sigs: Crime Scene, Hunger Wears A Mind |
| cyborgx (`game/assets/movesets/cyborgx.json`) | **ADDITIVE** | Alisa | 624 / 662 | Alisa (T7 284; T8 188/188 + T7 284/284 covered) + 2 WH sigs: Lullaby Hum, Motion Mandatory. Cape Jones = Cyborg X Attire 1 (CANON.md owner-locked); hand-cannon flavour maps to Alisa rocket punches per canon, file extras are the 2 sigs. |
| michiko (`game/assets/movesets/michiko.json`) | **ADDITIVE** | Katarina | 344 / 344 | Katarina (T7 189; 181/189 covered, 95%) + 2 WH sigs: Better Marketing, Edge Of The Coin |
| star (`game/assets/movesets/star.json`) | **ADDITIVE** | Christie | 908 / 949 | Christie capoeira line via Xiaoyu data (T7 Xiaoyu 259 + T3 192; T8 Xiaoyu 175/175 covered as the Christie proxy — Christie is not in T8) + 2 WH sigs: Tide Song, Undertow. Single capoeira lineage, not a two-fighter mix. |
| torch (`game/assets/movesets/torch.json`) | **ADDITIVE** | Anna | 892 / 933 | Anna (T7 354 + T3 224) + 2 WH sigs: Extraction Team Of One, Nail File |
| bruno (`game/assets/movesets/bruno.json`) | **ADDITIVE** | Miguel | 328 / 328 | Miguel (T7 219; 213/219 covered, 97%) + 2 WH sigs: 3AM Despair, Lean In |
| negativo (`game/assets/movesets/negativo.json`) | **ADDITIVE** | Negan | 292 / 296 | Negan (T7 183; 163/173 covered, 94%) + 2 WH sigs: Bounty Or Fun, Running Out Of Room |
| thor (`game/assets/movesets/thor.json`) | **ADDITIVE** | Ganryu | 322 / 322 | Ganryu TTT2 78 + 2 WH sigs: Niflheim's Mouth, Swallowed Thunder. Remainder is Ganryu-named authored rows + Bryan T3 proxy bank rows; no T7/T8 Ganryu exists. |
| yukihyo (`game/assets/movesets/yukihyo.json`) | **ADDITIVE** | Armor King | 560 / 577 | Armor King (T7 225 + T8 176; T7 187/202 covered, 92%) + 2 WH sigs: Storm Shadow's Lesson, Whiteout. Yukihyo = Armor King-based. |
| slice (`game/assets/movesets/slice.json`) | **ADDITIVE** | Dragunov | 486 / 492 | Dragunov (T7 234 + T8 141; T7 217/234 covered, 92%) + 2 WH sigs: Skull Mask Off, Surgical Slice |
| docfrank (`game/assets/movesets/docfrank.json`) | **ADDITIVE** | Bosconovitch | 380 / 401 | Bosconovitch T3 266 + 5 Gero-inspired originals (canon:gero-inspired: Energy Absorption, Eye Laser Beam, Rocket Punch, Afterimage, Ki Blast) + 2 WH sigs: Crayon Notes, Peer Review. Variant files add donor:docfrank curated sets (same character, not a second fighter). |
| baek-master-white (`game/assets/movesets/baek-master-white.json`) | **ADDITIVE** | Baek | 291 / 291 | Baek TTT2 153 + donor:baek 25 + 4 WH sigs (Eleventh Lecture, Homework, Kick Is The Question, Master's White; 24 sig entries across donor variants). Roster slot uses this variant file. 153/291 entries unmapped in editor (TTT2 rows carry no anim_ref). |
| mariposa-monarch (`game/assets/movesets/mariposa-monarch.json`) | **ADDITIVE** | Zafina | 518 / 526 | Zafina (T7 236 + T8 146) + 2 WH sigs: Fifth Thing Is The Floor, Seal Check. Roster slot uses this monarch variant; base mariposa.json is Zafina-only (PURE as a file) — character pattern follows the slot file. Mariposa = Mary Posa (Zafina). |
| dxmmii-patchwork (`game/assets/movesets/dxmmii-patchwork.json`) | **BUILT** | Mokujin | 170 / 170 | Mokujin CONCEPT, authored patchwork kit: 146 curated rows + donor:dxmmii + 4 WH sigs (Crooked Patch, Everybody's Sample, Hidden Toolbox, Tongue In Run). No decoded Mokujin set exists in the file; the four-arm stance system (arms OUT/IN/FLOATING) is a built system per CANON.md, not a pull. |
| charger (`game/assets/movesets/charger.json`) | **ADDITIVE** | Blanka (SF) — fighter replaced by CHARGER (owner 2026-10-20) | 203 / 210 | Blanka (SF) set carried over (SF6 85 + SFV 24 rows + Bryan T3 proxy bank rows) with renamed signatures Electric Thunder + Rolling Attack (wh:blanka:sig:1/2) + ice+electric identity. SF 3D-native CHARGER moves NOT yet invented (SOURCE-MERGE known limit). |
| dorowani (`game/assets/movesets/dorowani.json`) | **PURE** | Gon (Tekken 3) | 175 / 177 | Gon, Tekken 3 only: 150 T3 Gon rows + Gon specials/strings (175 moves, t3_source gon throughout), 0 extras. |
| chatur (`game/assets/movesets/chatur.json`) | **PURE** | True Ogre (Tekken 3) | 152 / 157 | True Ogre, Tekken 3 only: 152 moves, t3_source ogre throughout, 0 extras. Four-arm body translation is noted in canon_note (double palms become fourfold strikes) — an adaptation of the same kit, not added moves. |
| pond (`game/assets/movesets/pond.json`) | **PURE** | Raven (Tekken 7) | 620 / 647 | Raven lineage only: T8 Raven 177 + T7 Master Raven 292, 0 extras. Raven/Master Raven treated as one lineage (T8 Raven is the character's return); T8 177/177 + T7 292/292 covered. |
| ryusan (`game/assets/movesets/ryusan.json`) | **ADDITIVE** | Lucky Chloe (Tekken 7) | 211 / 211 | Lucky Chloe T7 205 + 6 wh: corrosion moves: Vitriol Spit, Corrosion Claw, Don't Tell Me To Calm Down, Acid Rain Dance, Jotei's Receipt, Meltdown. Canon_note confirms: "plus proprietary corrosion moves layered on top". |
| tobi (`game/assets/movesets/tobi.json`) | **ADDITIVE** | Hwoarang (Tekken 3) | 729 / 746 | Hwoarang (T8 209 + T7 326 + T3 188) + 6 tobi-canon escape moves: Longleap, Courier's Dash, Tip-Off, Satchel Swing, Escape Soul Flurry, The Undelivered Letter. Canon_note confirms: "plus proprietary escape-artist moves layered on top". |
| megami (`game/assets/movesets/megami.json`) | **ADDITIVE** | Jun Kazama (Tekken Tag Tournament 2) | 304 / 311 | Jun Kazama T8 149 + canon-layered guardian moves (Sealed Door d/b+1+2, Threshold Keeper b+1+2~b, Kaimon GEN 1+2, etc.). GAP: the authored/canon half (162/311 entries) carries no anim_ref, so the editor shows it unmapped — specified, not yet animated. |
| menajerii (`game/assets/movesets/menajerii.json`) | **BUILT** | Roger Jr. (Tekken Tag Tournament 2) | 193 / 193 | Roger Jr. kit authored FRESH with Tekken inputs (canon_note, owner directive) + canon-layered moves (Heron's Patience, Heron Strike, Boar's Commit, Serpent's Economy). Only 39/193 moves carry TTT2 Roger provenance; 190/193 entries are unmapped in the editor (no anim_ref). Built, not pulled — the alternative ADDITIVE reading is noted but the file's own framing is authored-fresh. |
| kronos (`game/assets/movesets/kronos.json`) | **MIX** | Zangief + Golem (Urban Reign) | 900 / 957 | Zangief (SF6/SFV donor sets) + Golem, Urban Reign (t3_source urban-reign 6) + DOA Bass throws (via vainabel, 8) + Armor King chain throw (1) + WH sig entries (Atomic Buster family, Timberwolf Lunge, etc.). Canon_note confirms the multi-source build. |
| deathfang (`game/assets/movesets/deathfang.json`) | **BUILT** | Iori Yagami (KOF) | 127 / 128 | Curated Iori Yagami kit on a Heihachi T3 proxy bank (proxy=True): 14 numbered wh:deathfang:sig:* rows are Iori moves (Maiden Masher, 108 Shiki Yamibarai, 100 Shiki Oniyaki, 127 Shiki Aoi Hana, Kin 1211 Shiki Ya Otome, Sake Saka Claw Throw, Grief Piledriver, Transform: Chained Prisoner Werewolf, No Future), not WH signatures. No decoded KOF set. |
| ryuji (`game/assets/movesets/ryuji.json`) | **MIX** | Ryuji Yamazaki (KOF XV) / The Rock hybrid | 127 / 129 | KOF Yamazaki curated set + The Rock wrestling (King T7 rows per canon_note: Rock Bottom, People's Elbow, DDT) + 7 WH sig entries (Brahma Bull Lariat, Knife Slash, People's Elbow, Sand Kick, Serpent Slash, Smackdown, Tongue Out). Canon_note lists the full Yamazaki set + Rock set. |
| koreshi (`game/assets/movesets/koreshi.json`) | **ADDITIVE** | Kakashi (Naruto) + Super Saiyan 4/5 + ninja | 1080 / 1153 | Vega, one fighter across SFV (405) + SF4 (50) donor sets + 16 canon:koreshi-flavor rows + 2 wh: entries. DESIGN CONFLICT: index tekken_base claims "Kakashi + Super Saiyan 4/5 + ninja" — no Kakashi/SSJ content is in the file. File pattern is ADDITIVE (Vega + flavour); design claim is unverified. Naming artifact: LP1 slot winner is named "IORI 1" (shared-bank generation prefix) — cosmetic, pattern unaffected. |
| rave (`game/assets/movesets/rave.json`) | **MIX** | Lei Wulong | 1086 / 1087 | Lei Wulong (T7 526 + T3 266) + Byou donor rows (~158, incl. Byou's own sigs Sickness Pattern + Wrong Foot) + 2 Rave WH sigs: Green Mist, Entrance Is The Fight. Owner order verbatim (SOURCE-MERGE 2026-10-21): "U can add leis and byous moves to rave". |
| buffalo-bill (`game/assets/movesets/buffalo-bill.json`) | **PURE** | Law | 795 / 816 | Law lineage only: T8 Law 162 + T7 Law 303 + T3 Forest Law 102 (Law-line T3 bank), 0 extras. T8 162/162 + T7 303/303 covered. |
| vainabel (`game/assets/movesets/vainabel.json`) | **ADDITIVE** | Bass Armstrong | 60 / 67 | Bass Armstrong, DOA real data (EXTRACTION-STATUS: 42 real Bass moves, proxy: false after rebuild) + 2 WH sigs: Elias Brothers Chokeslam, Purple Light Sermon. File now 60 moves (52 at COVERAGE time + sigs). |
| cainelias (`game/assets/movesets/cainelias.json`) | **BUILT** | Undertaker (WWE) | 46 / 46 | Curated Undertaker signature kit on a King T3 proxy bank (proxy=True): 5 WH sigs (Tombstone Piledriver, Last Ride, Chokeslam, Hell's Gate, Old School) + 36 King bank rows + 5 further rows. No decoded WWE/Urban Reign set. Owner words (CANON.md) leave the second source undecided: "Glen Kluger (Urban Reign) or a fitting Tekken character". |
| chordz (`game/assets/movesets/chordz.json`) | **ADDITIVE** | Lars | 469 / 488 | Lars (T8 123 + T7 201; T8 121/121 + T7 186/186 covered) + 2 WH sigs: Encore Breakdown, Power Chord |
| gashadokuro (`game/assets/movesets/gashadokuro.json`) | **PURE** | Kuma | 530 / 554 | Kuma line only: T8 Kuma 142 + T7 Kuma 225 + T3 Kuma 163, 0 extras. Canon law 2026-10-23: proprietary successor to the Kuma slot; Kuma himself is obsolete in-universe (technical scaffolding only). |
| aotsuki (`game/assets/movesets/aotsuki.json`) | **PURE** | Panda | 530 / 554 | Kuma line only (Panda slot): T8 Kuma 142 + T7 Kuma 225 + T3 Kuma 163, 0 extras, proxy=True. Canon law 2026-10-23: proprietary successor to the Panda slot; Panda herself is obsolete in-universe. |
| silvertongue (`game/assets/movesets/silvertongue.json`) | **ADDITIVE** | Lili | 508 / 519 | Lili (T8 148 + T7 223) + 2 WH sigs: Curtsy, Kiss Like A Slap. Canon law 2026-10-23: proprietary re-own of the Lili slot; source name retired in-universe. |
| birodo (no file) | **PATTERN UNCLEAR** | Feng Wei (claimed) | 0 / 0 | Docs checked: `docs/owner-directives.md` ("BIRODO … Moveset: Feng Wei (user pick)"), `CANON.md` intake canon, `game/assets/movesets/index.json` (no birodo entry), repo tree (no birodo.json, no Feng Wei decoded set). A single source is NAMED but the pattern is UNSPECIFIED: nothing says "all Feng Wei" vs "Feng Wei + extras". NOT defaulted to PURE. NEEDS-DATA: decoded Feng Wei set + a birodo.json build. |
| jotei (no file) | **PATTERN UNCLEAR** | Craig Marduk (claimed) | 0 / 0 | Docs checked: `docs/owner-directives.md` ("JOTEI … Moveset: Craig Marduk"), `CANON.md` intake canon, `game/assets/movesets/index.json` (no jotei entry), repo tree (marduk.json EXISTS as a source file, but no jotei.json has been built from it). Pattern UNSPECIFIED in docs. NOT defaulted to PURE. NEEDS-DATA: a jotei.json build from marduk.json + a pattern decision (pure vs additive). |

## Prior claims — verified or corrected (each claim from the task brief, checked, not taken as fact)

| Prior claim | Verdict | Evidence |
|---|---|---|
| Pantera = all King (PURE) | **CORRECTED → ADDITIVE** | `pantera.json`: King T7 297 + T3 199 (T8 215/215 notations covered) + 3 WH sigs (Honest Hold, Tail-Tip Lunge, Battle Itself), canon_note "Pantera WH signature moves preserved verbatim". |
| Scimitar = all Shaheen (PURE) | **CORRECTED → ADDITIVE** | `scimitar.json`: Shaheen T7 125 (T8 90/90 + T7 125/125 covered) + 2 WH sigs (Closing The Deal, Ledger Entry). |
| Burger = Bob | **CONFIRMED as base, pattern ADDITIVE** | `burger.json`: Bob T7 281 (T8 161/161 covered) + 2 WH sigs (Appetite's Grip, Side Dish Slam). |
| Demonio = Jin | **CORRECTED → MIX** | `demonio.json`: Jin + Devil Jin (T7 deviljin 45 + T8 Devil Jin 35) + 3 WH sigs. |
| Diablo = Heihachi | **CONFIRMED as base, pattern ADDITIVE** | `diablo.json`: Heihachi + 3 WH sigs. |
| Kinpo = Asuka | **CONFIRMED as base, pattern ADDITIVE** | `kinpo.json`: Asuka + 2 WH sigs. |
| Phantom = Yoshimitsu | **CONFIRMED as base, pattern ADDITIVE** | `phantom.json`: Yoshimitsu + 3 WH sigs. |
| Skull = Bryan | **CONFIRMED as base, pattern ADDITIVE** | `skull.json`: Bryan + 3 WH sigs. |
| Torch = Anna | **CONFIRMED as base, pattern ADDITIVE** | `torch.json`: Anna + 2 WH sigs. |
| Zui = Steve Fox + Lei drunken | **CONFIRMED → MIX** | `zui.json` + `docs/movesets/ZUI-STANCE-SYSTEM-2026-10-21.md` (owner orders verbatim, Steve T7 set + 40 Lei DRU entries + stances). Sibling Zui-mix lane owns Zui. |
| Zen = Eleven/Twelve + Dural + canon | **CONFIRMED as DESIGN, FILE DIFFERS** | Design: task brief + claimed-map exception "Zen=Twelve/SFIII" (`docs/owner-directives.md` moveset-library section). Shipped `zen.json`: Heihachi + 2 WH sigs. Sibling Zen lane owns resolution; this audit does not rewire Zen. |
| Cape Jones = Alisa slot/tech + own extras | **CONFIRMED → ADDITIVE** | `cyborgx.json` (Cape Jones = Cyborg X Attire 1, CANON.md owner-locked): Alisa T7 284 (T8 188/188 + T7 284/284 covered) + 2 WH sigs (Lullaby Hum, Motion Mandatory). |
| Rave = Lei Wulong | **CORRECTED → MIX** | `rave.json`: Lei + Byou donor rows (~158, incl. Byou's sigs) + 2 Rave sigs. Owner order in SOURCE-MERGE: "U can add leis and byous moves to rave". |
| Buffalo Bill = Law | **CONFIRMED → PURE** | `buffalo-bill.json`: Law only (T8 162 + T7 303 + T3 Forest Law 102), 0 extras. One of only 6 PURE rows. |
| Chordz = Lars | **CONFIRMED as base, pattern ADDITIVE** | `chordz.json`: Lars + 2 WH sigs. |
| Gyou = Paul | **CONFIRMED as declared base, file is MIX** | `gyou.json` tekken_base = Paul + paul_pull_20261023 (+133 Paul rows) on top of a Hwoarang majority (723 rows). Owner decision needed on the canonical base; see NEEDS-DATA. ROSTER.md's soul GYOU = Hwoarang is the OLD framework and is superseded for the WH character by the 2026-10-23 Paul pull. |
| Birodo = Feng Wei | **CONFIRMED as claimed source, pattern UNCLEAR** | No file, no Feng Wei decoded set; pattern unspecified. |
| Jotei = Marduk | **CONFIRMED as claimed source, pattern UNCLEAR** | No jotei.json; marduk.json exists as source only; pattern unspecified. |
| Chatur = True Ogre | **CONFIRMED → PURE** | `chatur.json`: T3 Ogre only, 0 extras. |
| Ryusan = Lucky Chloe | **CONFIRMED as base, pattern ADDITIVE** | `ryusan.json`: Lucky Chloe T7 205 + 6 wh: corrosion moves; canon_note "plus proprietary corrosion moves layered on top". |
| Pond = Raven | **CONFIRMED → PURE** | `pond.json`: Raven lineage only (T8 Raven 177 + T7 Master Raven 292), 0 extras. |
| Megami = Jun | **CONFIRMED as base, pattern ADDITIVE** | `megami.json`: Jun T8 149 + canon-layered guardian moves (Sealed Door, Threshold Keeper, Kaimon). |
| Menajerii = Roger Jr. | **CONFIRMED as concept, pattern BUILT** | `menajerii.json`: Roger kit authored FRESH + canon-layered moves; only 39 TTT2 Roger rows. |
| Tobi = Hwoarang | **CONFIRMED as base, pattern ADDITIVE** | `tobi.json`: Hwoarang + 6 tobi-canon escape moves; canon_note "plus proprietary escape-artist moves layered on top". |
| Intake characters (Birodo/Jotei/Chatur/Ryusan/Pond/Megami/Menajerii/Tobi) | **SOURCES ALL CONFIRMED; patterns vary** | See table. The intake canon names sources; it does not assign one pattern — exactly as the standing rule says. |

## Move List Creator wiring — verified, not invented (editor proof only, no play claims)

The Move List Creator (`packages/creation-suite/src/movelist-editor.js`, landed via PR #998, merged) reads moveset files directly through `fromMovesetFile()` — its own header states: "every entry shown comes from a moveset file, or from a library entry the host passes in" and "Nothing here is guessed". **No new moves were added by this audit, because none were needed: every rostered character's moves are already in its file and therefore already in the editor.** Adding duplicate or guessed rows would violate the repo's no-guessing rule. What this audit did instead is verify that wiring, per character, with the editor's own functions (`fromMovesetFile()`, `computeMappingStatus()`, `validateAssignment()` via `createEditor()`/`listAllMoves()`/`renderEditorHTML()`):

- **All 58 roster files load**: 33,598 editor entries total (32,262 file moves + specials). Status distribution across all entries: correct 27,700 / approximate 2,999 / wrong 852 / unmapped 2,047. "Wrong" and "unmapped" entries are SHOWN in the full list with reasons (the editor's design: it blocks new wrong assignments by default, it never silently marks a wrong mapping correct). "Approximate" means input-consistent but not clip-verified — exactly the editor's own honesty label, and it is never presented here as clip-verified.
- **LP1/RP2/LK3/RK4 slot winners validate `correct` for all 47 fighters that HAVE a slots dict** (188/188 slot checks: LP1, RP2, LK3, RK4 each). Examples: Pantera LP1 Jab / RP2 Right Jab / LK3 Left Kick / RK4 Right Kick; Scimitar LP1 SCIMITAR 1 / RP2 SCIMITAR 2 / LK3 Blinding Sands / RK4 Hallux Kick; Cape Jones (cyborgx) LP1 Jab / RP2 CYBORG X 2 / LK3 CYBORG X 3 / RK4 Accelerator; Tobi LP1 Jab / RP2 Right Jab / LK3 TOBI 3 / RK4 TOBI 4; Dorowani LP1 Snap Bite / RP2 Claw Swipe / LK3 Tail Jab / RK4 Tail Swipe.
- **11 fighters have NO slots dict**, so the editor can list their moves but cannot validate canonical slot winners: byou, thor, charger, chatur, ryusan, megami, menajerii, deathfang, ryuji, vainabel, cainelias.** This is a wiring gap, not a pattern gap — it is listed under NEEDS-DATA so a later lane can add slot maps without touching move content.
- **Signature/canon extras validate in their own slots, with one recurring exception that the editor surfaces honestly**: most WH signature entries validate `correct` on their canonical Tekken spelling (e.g. `1+2`), while the alternate non-Tekken spellings of the same move (e.g. `S`, `P+K`, `D+K` spellings carried alongside the Tekken spelling) validate `wrong` (limb/context mismatch for a non-button input). The editor shows both spellings and their statuses; the Tekken spelling is the assignable one. This affects 2 entries per signature on most ADDITIVE characters and is NOT hidden by this audit.
- **Unmapped hotspots (entries with no anim_ref and no bank/row, so the editor correctly refuses them as assignment targets)**: menajerii 190/193, megami 162/311, baek-master-white 153/291 (TTT2 rows carry no anim_ref), pond 178/647 (curated variants; pond's canonical LP1/RP2/LK3/RK4 slot winners DO validate `correct` via `t8:raven` refs — the unmapped rows are non-winner variants), thor 78/322, koreshi 72/1153, kronos 50/957. Menajerii and Megami are the severe cases: their canon-layered moves are specified in the files but have no animation reference at all.
- **Display smoke test**: Pantera via `createEditor()` → `listAllMoves()` = 987 rows, `renderEditorHTML()` = 204,833 characters of HTML. The editor reads and displays the audited moves; no render failure was observed in this Node-level test. This is simulation/editor-test proof only — it is NOT a play-verified claim, and no in-game fight was run for this audit.
- **Zui stance gating spot-check (sibling lane's system, verified as present, not rebuilt)**: `zui.json` carries a `stances` map (BOX/DCK/LWV/RWV/FLK/PKB/SWY/ALB/DRU) with DRU gated moves resolving through the input buffer per `docs/movesets/ZUI-STANCE-SYSTEM-2026-10-21.md`. Zui's LP1/RP2/LK3/RK4 slot winners validate `correct` (LP1 Jab, RP2 ZUI 2, LK3 Ducking Left, RK4 Ducking Right).

### Editor status per fighter (entries; correct / approximate / wrong / unmapped; slots dict?)

| Fighter | Entries | Correct | Approx. | Wrong | Unmapped | Slots dict |
|---|---|---|---|---|---|---|
| rin | 692 | 601 | 41 | 17 | 33 | yes |
| byou | 728 | 484 | 234 | 10 | 0 | NO |
| tou | 715 | 606 | 47 | 28 | 34 | yes |
| sha | 836 | 669 | 92 | 24 | 51 | yes |
| kai | 910 | 748 | 104 | 25 | 33 | yes |
| retsu | 716 | 636 | 29 | 20 | 31 | yes |
| zen | 684 | 577 | 45 | 17 | 45 | yes |
| gyou | 1023 | 707 | 269 | 29 | 18 | yes |
| pantera | 987 | 767 | 51 | 56 | 113 | yes |
| demonio | 804 | 667 | 72 | 25 | 40 | yes |
| phantom | 1087 | 762 | 235 | 22 | 68 | yes |
| diablo | 703 | 584 | 53 | 24 | 42 | yes |
| skull | 721 | 644 | 25 | 19 | 33 | yes |
| samura1 | 907 | 775 | 62 | 23 | 47 | yes |
| sakura | 815 | 654 | 86 | 24 | 51 | yes |
| zui | 666 | 566 | 86 | 2 | 12 | yes |
| kinpo | 548 | 493 | 18 | 14 | 23 | yes |
| waterfall | 380 | 330 | 22 | 13 | 15 | yes |
| kingtyrant | 878 | 725 | 93 | 30 | 30 | yes |
| burger | 583 | 512 | 18 | 22 | 31 | yes |
| awapop | 962 | 847 | 41 | 21 | 53 | yes |
| scimitar | 374 | 323 | 23 | 16 | 12 | yes |
| purplerain | 593 | 502 | 53 | 14 | 24 | yes |
| nightwolf | 570 | 516 | 12 | 26 | 16 | yes |
| dio | 275 | 268 | 1 | 6 | 0 | yes |
| cyborgx | 662 | 482 | 118 | 24 | 38 | yes |
| michiko | 344 | 338 | 3 | 3 | 0 | yes |
| star | 949 | 759 | 124 | 25 | 41 | yes |
| torch | 933 | 792 | 68 | 32 | 41 | yes |
| bruno | 328 | 323 | 3 | 2 | 0 | yes |
| negativo | 296 | 285 | 0 | 7 | 4 | yes |
| thor | 322 | 242 | 0 | 2 | 78 | NO |
| yukihyo | 577 | 483 | 57 | 20 | 17 | yes |
| slice | 492 | 461 | 17 | 8 | 6 | yes |
| docfrank | 401 | 369 | 0 | 14 | 18 | yes |
| baek-master-white | 291 | 126 | 0 | 12 | 153 | yes |
| mariposa-monarch | 526 | 451 | 62 | 5 | 8 | yes |
| dxmmii-patchwork | 170 | 157 | 0 | 13 | 0 | yes |
| charger | 210 | 201 | 0 | 2 | 7 | NO |
| dorowani | 177 | 164 | 0 | 11 | 2 | yes |
| chatur | 157 | 144 | 0 | 8 | 5 | NO |
| pond | 647 | 363 | 92 | 14 | 178 | yes |
| ryusan | 211 | 210 | 0 | 1 | 0 | NO |
| tobi | 746 | 480 | 232 | 17 | 17 | yes |
| megami | 311 | 121 | 27 | 1 | 162 | NO |
| menajerii | 193 | 3 | 0 | 0 | 190 | NO |
| kronos | 957 | 899 | 0 | 8 | 50 | yes |
| deathfang | 128 | 128 | 0 | 0 | 0 | NO |
| ryuji | 129 | 127 | 0 | 2 | 0 | NO |
| koreshi | 1153 | 960 | 105 | 16 | 72 | yes |
| rave | 1087 | 1076 | 3 | 7 | 1 | yes |
| buffalo-bill | 816 | 745 | 36 | 14 | 21 | yes |
| vainabel | 67 | 56 | 0 | 6 | 5 | NO |
| cainelias | 46 | 41 | 0 | 5 | 0 | NO |
| chordz | 488 | 396 | 59 | 14 | 19 | yes |
| gashadokuro | 554 | 439 | 79 | 12 | 24 | yes |
| aotsuki | 554 | 439 | 79 | 12 | 24 | yes |
| silvertongue | 519 | 477 | 23 | 8 | 11 | yes |

## NEEDS-DATA list (specific missing source per item — nothing filled with guesses)

1. **Birodo — NEEDS-DATA**: no decoded Feng Wei set anywhere in the repo; no birodo.json. Also needs a pattern decision (pure vs additive) from the owner — the audit refuses to assume it.
2. **Jotei — NEEDS-DATA**: marduk.json exists as a source file, but no jotei.json has been built from it; also needs a pattern decision (pure vs additive).
3. **Zen — NEEDS-DATA + SIBLING LANE**: Twelve (SFIII 3rd Strike) + Dural (VF5) decoded sets + an X.COPY super specification. Shipped zen.json (Heihachi) must not be treated as the Zen design. Sibling Zen lane owns this; this audit only records the mismatch.
4. **Zui — SIBLING LANE**: MIX already documented (`docs/movesets/ZUI-STANCE-SYSTEM-2026-10-21.md`); remaining gap from that doc is DRU clip row-mapping (T3 Lei bank rows carry no semantic labels) and the engine stance-flag limit. Not duplicated here.
5. **Gyou — NEEDS-DECISION (owner)**: is Paul the canonical base (2026-10-23 pull) with Hwoarang rows to be re-slotted out, or is the file intentionally Paul + Hwoarang? Until the owner calls it, the file stays MIX and no rows are deleted.
6. **Byou vs Rave, Lei ownership — NEEDS-DECISION (owner)**: SOURCE-MERGE 2026-10-21 says Lei = Rave and Byou's base is unrecorded, yet byou.json still carries the full Lei T7 set (571 rows) while rave.json carries Lei + Byou. Both files cannot be the canonical Lei kit. Owner call needed; no rows deleted by this audit.
7. **Menajerii — NEEDS-DATA (animation)**: 190/193 entries unmapped; decoded TTT2 Roger set beyond the 39 rows in the file; anim refs for the authored + canon-layered moves (Heron/Boar/Serpent sets).
8. **Megami — NEEDS-DATA (animation)**: 162/311 entries unmapped (authored/canon half); TTT2 Jun decode (Jun is a TTT2 character, not a T7 roster character — see owner-directives 2026-10-24 note on the 940 blocked slots, which also covers Pond/Raven and Ryusan/Lucky Chloe animation slots). Frame data exists; animation slots are the blocker — the two must not be conflated.
9. **Pond / Ryusan animation slots — NEEDS-DATA (animation, not frame data)**: frame-data rows exist (Pond Raven 177+292, Ryusan Lucky Chloe 205 + corrosion moves), but owner-directives 2026-10-24 records 940 blocked animation slots across Pond, Ryusan, and Megami, unblockable only via live TKMovesets extraction (Raven, Lucky Chloe) / TTT2 extraction (Jun) / mot.bin RE. Until then, unmapped variants stay unmapped in the editor — an honest UNMAPPED beats a wrong clip.
10. **Baek-master-white — NEEDS-DATA (animation + slots)**: 153/291 entries unmapped (TTT2 Baek rows, no anim_ref) and a slots dict of only 36 entries against 291 moves. The roster slot file needs a full slot map.
11. **No-slots-dict files — NEEDS-DATA (slot maps, no move changes)**: byou, thor, charger, chatur, ryusan, megami, menajerii, deathfang, ryuji, vainabel, cainelias. Slot maps can be added without altering move content.
12. **Cainelias second source — NEEDS-DECISION (owner)**: CANON.md owner words leave "Glen Kluger (Urban Reign) or a fitting Tekken character" undecided; Urban Reign PPK moveset semantics are not yet decoded (EXTRACTION-STATUS: blocked on RE lane).
13. **Koreshi design-vs-file conflict — NEEDS-CLARIFICATION**: index tekken_base claims Kakashi + Super Saiyan 4/5 + ninja; the file is Vega (SFV/SF4 donors) + koreshi-flavor rows. Either the design changed or the file is a placeholder. Also cosmetic: LP1 slot winner is named "IORI 1" (shared-bank prefix artifact).
14. **King Tyrant Booker T moves — NEEDS-DATA**: SOURCE-MERGE known limit — not invented, needs WWE data decoded. Same for Doc Frank's further Gero/Mojo/Weird concepts beyond the 5 shipped Gero moves, and Charger's SF 3D-native moves.
15. **Kevin — NEEDS-CLARIFICATION**: in COVERAGE-2026-10-23 (138 moves) but absent from roster-full.js and from current moveset files. Renamed (baek-master-white?), merged, or removed? Not assumed.
16. **Coverage gaps carried forward (from COVERAGE-2026-10-23; file counts have moved since, so re-verify on the next coverage run rather than treating these as current)**: Dio Akuma 131/136 (96%), Michiko Katarina 181/189 (95%), Bruno Miguel 213/219 (97%), Negativo Negan 163/173 (94%), Yukihyo Armor King T7 187/202 (92%), Slice Dragunov T7 217/234 (92%), Rave Lei T7 496/524, Zui Steve T7 279/287.

## Sibling-lane overlaps (coordination, not duplication)

- **Zui mix lane**: owns Zui's Steve + Lei DRU mix and stance system. This audit records Zui as MIX with evidence and does not touch zui.json.
- **Zen lane**: owns Zen's Eleven/Twelve + Dural + canon + X.COPY build. This audit records Zen as BUILT-by-design with a shipped-file mismatch and does not touch zen.json.
- **General canon-move Move List Creator wiring lane**: owns editor wiring work in general. This audit's editor contribution is verification only (load + validate + display for all 58 files, with the per-fighter status table above); no editor code was changed, so there is no merge conflict surface with that lane from this PR.
- **Animation lanes**: the unmapped/animation-slot gaps above (Menajerii, Megami, Pond, Ryusan, Baek-master-white, TTT2/T6/UR extractions) belong to the extraction/animation lanes, not to this audit. This audit flags them with exact counts instead of filling them.

## Honest gaps and limits of this audit

- **Simulation/editor-test proof only.** No fight was played, in-game or otherwise, for this audit. Editor statuses are input-derived unless clip tags exist (the editor's own `verification` field); nothing here is claimed clip-verified or play-verified.
- **No moveset files and no editor code were modified.** The "wiring" in this audit is verification that the existing files already wire into the editor. If the parent agent expected new moves to be authored (e.g. Birodo/Jotei kits, Zen's Twelve/Dural kit), those are NEEDS-DATA items above, not things this audit could honestly invent.
- **T3 proxy rows are treated as animation placeholders, not semantic sources** (rule 6). If a future lane proves a given file's T3 rows are semantic (not proxy), that row's pattern must be re-judged — the per-row evidence above names the T3 bank so re-judgment is possible.
- **Counts are a snapshot of main on 2026-10-24.** Later pulls (e.g. the 2026-10-23 Gyou Paul pull pattern) change files without changing this document; the next audit run should regenerate the table from the files rather than editing numbers by hand.
- **The "stance audit" document could not be found** (see universe section). If it exists under a different name or in a non-main branch, the universe should be re-based on it and any roster differences reconciled.

## Sources consulted (evidence index)

- `game/assets/movesets/*.json` (157 files on main; 58 roster-slot files audited in full: merge_source / t7_move_id / t3_source / donor / wh_original / canon fields counted per move).
- `game/assets/movesets/index.json` (tekken_base per file; 128 entries incl. library/variant files).
- `game/js/roster-full.js` (58 roster ids — audit universe).
- `docs/movesets/COVERAGE-2026-10-23.md` (per-fighter source coverage incl. T8/T7 covered counts).
- `docs/movesets/SOURCE-MERGE-2026-10-21.md` (merge method, slot priority WH signature > T8 > T7 > T3 > donor > proxy, owner corrections incl. Lei=Rave and Doc Frank=Bosconovitch, known limits).
- `docs/movesets/ZUI-STANCE-SYSTEM-2026-10-21.md` (Zui MIX + stance system + gaps).
- `docs/movesets/EXTRACTION-STATUS.md` (DOA Bass real data, T3 proxy counts, TTT2/T6/UR blockers, schema v2).
- `docs/MOVESET-COVERAGE.md`, `docs/MOVESET-STUB-AUDIT-2026-10-22.md`, `docs/FIGHTER-COMPLETENESS-AUDIT-2026-10-21.md`, `docs/CATCHUP-AUDIT-2026-10-23.md`, `docs/ROSTER-CANON-GAPS-2026-10-23.md` (corroboration; catchup audit is the source for the Gashadokuro/Aotsuki/Silvertongue canon-law successor notes).
- `ROSTER.md` (Nine Souls framework + owner-designed characters; soul framework distinguished from WH character files where they differ, e.g. Gyou).
- `CANON.md` (character canon, Cyborg X = Cape Jones owner-lock, Dxmmii four-arm system, Cain Elias owner words, Koreshi/Ryuji/Kronos canon_notes in files).
- `docs/owner-directives.md` (intake moveset claims incl. Birodo Feng Wei / Jotei Marduk / Tobi Hwoarang / Menajerii Roger Jr. / Ryusan Lucky Chloe / Pond Raven / Megami Jun / Chatur True Ogre; moveset source law + claimed-map incl. Zen=Twelve/SFIII exception; 940 blocked animation slots 2026-10-24).
- `packages/creation-suite/src/movelist-editor.js` (PR #998, merged: fromMovesetFile / validateAssignment / computeMappingStatus / createEditor / listAllMoves / renderEditorHTML — the editor under test).
- `docs/research/FIGHTER-DEPTH-CANON-MAPPING-2026-10-22.md` (canon-depth corroboration).
