# Moveset Provenance Classification — 2026-10-30

## Owner instruction (verbatim quote)

> "What donors moves were okd by me tho vs what are placeholders that need to be replace needs to be considered. First work on whatever characters have movesets that come straight from another game and need no kid or extras mixed in but only have 1 moveset straight from 1 character base and then once those are all done do the rest"

Owner addendum (2026-10-30, after the lane was briefed): (1) Steam-library real code is a named gap-filling source — a separate lane is pulling Tekken 7 first, then Tekken 8; within a fighter, gaps still fill ONLY from that fighter's own base source. When the Steam extraction lands, it is preferred over branch-graph inference for fighters whose base is T7/T8, and is cited as the source. (2) Video-evidence standard: a move or string is only "works" with fight video behind it (separate play-verify lane). This lane's fixes are labeled **data-corrected**; nothing in this lane is **video-verified**, and the two labels are never blurred.

## Method the owner specified

Classify first: which donor moves the owner approved vs which are placeholders that need replacing. Then work in order: (Phase 1) every character whose moveset comes straight from one character in one game — one moveset, one character base, no kit or extras mixed in — and only once those are all done, (Phase 2) the rest.

## Method actually used

1. **Canon evidence first.** Every fighter's canon base and every claimed mix approval was taken from CANON.md, ROSTER.md, per-fighter `roster/<fighter>/CANON.md` files, and recorded owner decisions under `docs/decisions/` — quoted with file + line in the working papers and in Appendix A below. Approval was NEVER inferred from the moveset data itself.
2. **Data recomputed on current main.** All 163 files in `game/assets/movesets/` were re-parsed at the main tip current at lane start (56,527 moves in 129 moves-bearing files; totals agree with `docs/movesets/REAL-MOVES-AUDIT-2026-10-29.md`). Per file: declared `tekken_base` / `t3_source` / `anim_bank`, `donor_fighter` distribution, guess-grade `anim_t3` count (`nearest (approximate)` + `same-notation` labels), `UNMAPPED:*` count, no-anim count, cross-bank `anim_t3` detail.
3. **Classes.** (1) **Single-source straight port** — canon base is ONE character and the data is drawn from that character only (any game in their own lineage; self-donor inheritance from the fighter's own base file is not a mix; WH signature moves added under the global additive directive, `docs/canon-movelist-wiring-2026-10-24.md` L3/L8, are not a base change). Sub-states: **1-C** complete, **1-W** workable now (guess-grade `anim_t3` provable from the fighter's own T3 bank branch graph), **1-S** source-pending (gaps whose only real source is the base character's own T7/T8/TTT2/DOA/VF extraction). (2) **Owner-approved mix** — only with a canon/decision citation. (3) **Placeholder** — foreign-character data with NO canon basis. **D** — owner decision list: ambiguous or undocumented borrowings and canon conflicts, left untouched.
4. **A recurring wiring artifact is named, not hidden:** many files carry exactly 4 `anim_t3` entries on a foreign bank (system/shared rows from the 2026-10-23 merge tooling). These are counted in the table notes as "the standard 4-row residue" and are not treated as donor mixes. Larger foreign layers are class-3 items and are named individually.
5. **Phase 1 corrections** use the branch-walk proof method (proofs A/B/C/S in the lane spec, same family as PR #1232's Pantera fills): a guess-grade mapping is corrected only when the fighter's OWN bank branch graph (`teardown/tekken3/movesets/moveset_<bank>.json`: `branches[]` + `move_index`, gated by `game/assets/anim/t3/<bank>/hit_frames.json` where present) proves the real row. Unproven mappings stay exactly as they are and are counted per fighter. Every correction is recorded in the moveset file itself (`provenance_fix` per move + a file-level `provenance_fixes` entry) and labeled **data-corrected, not video-verified**.

## Deviations

- None against the owner's order. Two scoping facts are recorded, not hidden: (a) the brief for this lane named an "Echo copy-opponents" approval — NO Western Heart canon doc supports an Echo copy-moveset (copy traits in canon belong to The Trader, DXMMII/Mokujin, and Zen's single X.COPY super), and no echo moveset file exists; it is carried on the Decision List instead of being treated as approved. (b) The signature-add directive was located as the 2026-10-24 canon-movelist-wiring directive (quoted in the working papers), not a 2026-10-19 verbatim order; it is cited as found.

## Summary counts (163 files)

| Class | Files | Meaning |
|---|---:|---|
| 1-W (Phase 1 workable now) | 34 | Single-source; guess-grade anim_t3 correctable from own T3 bank graph |
| 1-W + class-3 residue | 2 | demonio (devil_jin×34), gyou (paul×47) — own-bank corrections in Phase 1, residue replaced in Phase 2 |
| 1-C (complete) | 28 | Single-source; no guess-grade, no UNMAPPED |
| 1-S (source-pending) | 49 | Single-source; gaps await the base character's own T7/T8/TTT2/DOA/VF extraction (Steam lane for T7/T8) |
| 1-core + class-3 layer | 1 | koreshi — Vega core is canon; a 312-move Yoshimitsu layer sits on top, explicitly rejected in its canon doc |
| 2 (owner-approved mix) | 6 | kronos, kronos-attire2, rave, ryuji-rock (CornerStone), zen, zui — NOT reworked |
| 2-spec (approved spec, base unresolved) | 1 | cainelias |
| 3 (placeholder) | 1 whole file | street-reign stub (5 moves, no base anywhere) — plus the class-3 layers/residues named above |
| D (owner decision list) | 7 | byou, charger, charger-attire2, demonio-winged, gyou-spirit-body, jin_soul, star — untouched |
| DATA (non-fighter files) | 34 | 31 ur-char* Urban Reign motion banks + index.json + t3_input_tables.json + ur-native-index.json |

## Per-fighter classification

| File | Fighter | Canon base (game + character) | Class | Moves | Guess-grade anim_t3 | UNMAPPED | Donor flags (data) | Evidence / notes |
|---|---|---|---|---:|---:|---:|---|---|
| aotsuki.json | AOTSUKI | Tekken — Panda (bear bank, technical only) | 1-W | 530 | 251 | 0 | — | Bear-bank scaffolding per roster/panda/CANON.md; corrections use the Kuma graph (same bear bank). |
| armor-king.json | Armor King (original file) | Tekken — Armor King | 1-C | 500 | 0 | 0 | — | Own-character data file; WH version is Yukihyō. |
| awapop.json | AWA POP | Tekken — Nina Williams | 1-W | 909 | 286 | 0 | — | CANON.md L597 'Nina Williams base.' File t3_source field says jin — field mismatch, data anim bank is nina; corrections use the Nina graph. |
| baek-master-white.json | KEVIN (file: Baek Master's White) | Tekken — Baek Doo San | 1-S | 291 | 0 | 0 | baek×25 | CANON.md L961: the fighter IS Kevin; Baek's model is his A2 attire, reskin PARKED. donor baek×25 = inheritance from baek.json. Anim bank is a Bryan proxy (Baek has no T3 bank); 153 no-anim moves await a Baek source (T5/T6/T7). |
| baek.json | Baek Doo San (original file) | Tekken — Baek Doo San | 1-S | 111 | 0 | 0 | — | Source file for Kevin's base. Bryan bank is a declared proxy (no T3 Baek bank exists). |
| blanka.json | Blanka (original file) | Street Fighter — Blanka | 1-S | 199 | 0 | 0 | — | Data file; Bryan bank is a stand-in anim layer. WH fighter using this data is Charger (see Decision List). |
| bob.json | Bob Richards (original file) | Tekken — Bob Richards | 1-C | 557 | 0 | 0 | — | Own-character file; WH version is Burger. |
| bruno.json | BRUNO | Tekken — Miguel Caballero Rojo | 1-C | 328 | 0 | 0 | — | CANON.md L880 'Miguel base'; spec: 'Bruno takes ALL of Miguel's moves' (owner directive 2026-10-22). T7-import file, no guess-grade anim_t3; Bryan entries are the standard 4-row residue. |
| buffalo-bill.json | BUFFALO BILL / ASHES | Tekken 3 — Marshall Law / Forest Law | 1-W | 796 | 390 | 0 | — | roster/buffalo-bill/CANON.md: Law base (T3 teardown), T3 is the PROVISIONAL fallback, TTT2 primary pending extraction (2026-10-23 decision). Corrections use Law + Forest Law graphs. |
| burger-demon.json | BURGER (variant file) | Tekken — Bob Richards (wiring-doc base only) | 1-S | 466 | 0 | 0 | — | Variant identity has NO canon statement; built on Bob per SOURCE-MERGE like burger.json. |
| burger-speed-demon.json | BURGER (variant file) | Tekken — Bob Richards (wiring-doc base only) | 1-S | 454 | 0 | 0 | — | As burger-demon. |
| burger-the-mouth.json | BURGER (variant file) | Tekken — Bob Richards (wiring-doc base only) | 1-S | 454 | 0 | 0 | — | As burger-demon. |
| burger.json | BURGER | Tekken — Bob Richards | 1-S | 552 | 0 | 111 | — | CANON.md L567 'Bob Richards base.' 111 UNMAPPED await the Bob T7 source. |
| byou.json | BYOU (soul) | NONE — base explicitly unrecorded | D | 728 | 0 | 0 | — | Owner correction 2026-10-21 (SOURCE-MERGE): 'Byou keeps exactly its origin/main file; its base is not recorded anywhere.' File data rides Lei/T7-Jin wiring. DECISION LIST — untouched. |
| cainelias.json | CAIN ELIAS | Urban Reign — Glen Kluger OR a fitting Tekken character (owner spec, alternatives open) | 2-spec | 46 | 0 | 0 | — | CANON.md L1273 owner spec approves the mix elements (Last Ride, Tombstone); the base choice was never settled ('Moveset pick owned by the moveset lane', L1279). 5 No Mercy anim_refs are SUSPECT (wrong FileTable window) — flagged, not fixed. |
| charger-attire2.json | CHARGER (Attire 2) | NONE FOUND for Charger (file data: Street Fighter — Blanka) | D | 199 | 0 | 0 | — | Blanka data is a stand-in file, not a canon base (SOURCE-MERGE: Charger's SF 3D moves 'need WWE/SF data decoded first'). DECISION LIST — untouched. |
| charger.json | CHARGER | NONE FOUND for Charger (file data: Street Fighter — Blanka) | D | 203 | 0 | 0 | — | As charger-attire2. |
| chatur.json | CHATUR | Tekken 3 — True Ogre (wiring-doc base only) | 1-C | 281 | 0 | 0 | — | No CANON.md entry (ROSTER-CANON-GAPS lists chatur as missing canon); data is a straight T3 Ogre-bank port, all 281 moves on t3:ogre refs. |
| chordz.json | CHORDZ | Tekken — Lars Alexandersson (wiring-doc base only) | 1-S | 469 | 0 | 0 | — | No CANON.md entry found; built on t8:lars/t7:lars per SOURCE-MERGE. |
| cyborgx.json | CYBORG X (= Cape Jones) | Tekken — Alisa Bosconovitch | 1-S | 624 | 0 | 0 | — | CANON.md L847 'Alisa Bosconovitch base.' File t3_source says gunjack — field mismatch; anim data is alisa-bank. No guess-grade; T7/T8 Alisa source pending. |
| deathfang-werewolf.json | DEATHFANG (werewolf form) | KOF — Iori Yagami | 1-S | 127 | 0 | 0 | — | CANON.md L1285: Iori's moves/stance/animations in BOTH forms. Heihachi anim_t3 is the file's declared proxy layer (proxy: true); anim_refs are KOF XV (Iori's own game). |
| deathfang.json | DEATHFANG (human form) | KOF — Iori Yagami | 1-S | 127 | 0 | 0 | — | As deathfang-werewolf (CANON.md L1285). |
| demonio-bloodline-ember.json | DEMONIO (Bloodline Ember file) | Tekken — Jin Kazama | 1-W | 686 | 267 | 0 | demonio×30 | Jin base via Demonio self-inheritance (donor demonio×30). No canon statement names this form; data is single-source Jin. Corrections use the Jin graph. |
| demonio-human.json | DEMONIO (human attire file) | Tekken — Jin Kazama (via Demonio self-inheritance) | 1-W | 683 | 153 | 0 | demonio×581 | donor demonio×581 = inheritance from demonio.json ONLY (SOURCE-MERGE), not a foreign donor. Corrections use the Jin graph. |
| demonio-winged.json | DEMONIO (winged/Devil form file) | Tekken — Jin Kazama + Devil Jin layer (wiring build; NO canon approval found) | D | 1063 | 433 | 0 | demonio×125 | CANON.md gives Demonio a Jin base and a Devil-Gene theme but NO line approves a Devil Jin moveset layer for this file. DECISION LIST — untouched. |
| demonio.json | DEMONIO | Tekken — Jin Kazama | 1-W + 3-residue | 764 | 153 | 80 | — | CANON.md L95/L110; ROSTER.md L91-92. Corrections use the Jin graph. Residue: 34 devil_jin-bank anim_t3 with no canon basis — Phase 2 item. 80 UNMAPPED await the Jin T7 source. |
| diablo.json | DIABLO | Tekken — Heihachi Mishima | 1-W | 661 | 138 | 80 | — | CANON.md L152. Corrections use the Heihachi graph. 80 UNMAPPED await the Heihachi T7 source. |
| dio.json | DIO | Street Fighter — Akuma, as he appears in Tekken 7 | 1-C | 275 | 0 | 0 | — | CANON.md L817 'Akuma base.' Wiring t7:akuma. Distinct from the sf-akuma data file. |
| doa-ayane.json | Ayane (data file) | DOA — Ayane (DOA4 / DOA Ultimate) | 1-S | 23 | 0 | 0 | — | Data file, not a WH roster fighter (DOA-VF-CONVERSION-2026-10-19). Anim extraction belongs to the DOA lane. |
| doa-bass.json | Bass Armstrong (data file) | DOA — Bass Armstrong (DOA5LR / DOA Ultimate) | 1-S | 22 | 0 | 0 | — | Data file; also Vain Abel's base source. |
| doa-hayabusa.json | Ryu Hayabusa (data file) | DOA — Ryu Hayabusa (DOA5LR) | 1-S | 18 | 0 | 0 | — | Data file. |
| doa-jannlee.json | Jann Lee (data file) | DOA — Jann Lee (DOA4 / DOA Ultimate) | 1-S | 21 | 0 | 0 | — | Data file. |
| doa-kasumi.json | Kasumi (data file) | DOA — Kasumi (DOA5LR) | 1-S | 20 | 0 | 0 | — | Data file. |
| doa-tina.json | Tina Armstrong (data file) | DOA — Tina Armstrong (DOA4 / DOA Ultimate) | 1-S | 26 | 0 | 0 | — | Data file. |
| doc-frank-frankenstein.json | DOC FRANK (Frankenstein attire) | Tekken 3 — Dr. Bosconovitch | 1-W | 788 | 266 | 0 | docfrank×421 | CANON.md L1150. donor docfrank×421 = self-inheritance. Gun Jack is proxy-only per SOURCE-MERGE and never a default input. Corrections use the Bosconovitch graph (anim bank), NOT gunjack. |
| doc-frank-hood.json | DOC FRANK (hood attire) | Tekken 3 — Dr. Bosconovitch | 1-W | 892 | 332 | 0 | docfrank×525 | As doc-frank-frankenstein (donor docfrank×525). Owner-directed exclusions of Gun-Jack-only inputs are recorded for this file in SOURCE-MERGE. |
| doc-frank-machine-shop.json | DOC FRANK (machine-shop attire) | Tekken 3 — Dr. Bosconovitch | 1-W | 933 | 332 | 0 | docfrank×520 | As doc-frank-frankenstein (donor docfrank×520). |
| doc-frank-wowomomo.json | DOC FRANK (wowomomo attire) | Tekken 3 — Dr. Bosconovitch | 1-W | 892 | 332 | 0 | docfrank×525 | As doc-frank-frankenstein (donor docfrank×525). |
| docfrank.json | DOC FRANK | Tekken 3 — Dr. Bosconovitch | 1-C | 380 | 0 | 0 | — | CANON.md L1150 'Dr. Bosconovitch base.' 5 no-anim moves noted. |
| dorowani.json | DOROWANI | Tekken 3 — Gon | 1-C | 175 | 0 | 0 | — | roster/dorowani/README.md: 'Base: Gon (Tekken 3)' — name locked 2026-10-22, superseding CANON.md L1558 (2026-10-20, no mapping at that time). All 175 moves on t3:gon refs. |
| dxmmii-patchwork.json | DXMMII (patchwork file) | Tekken — Mokujin (via DXMMII self-inheritance) | 1-C | 170 | 0 | 0 | dxmmii×20 | donor dxmmii×20 = self-inheritance only. Mimicry is the base itself (CANON.md L1049/L1074). |
| dxmmii.json | DXMMII | Tekken — Mokujin | 1-C | 150 | 0 | 0 | — | CANON.md L1074 'Mokujin base.' |
| gashadokuro.json | GASHADOKURO | Tekken 3 — Kuma (bear bank, technical only) | 1-W | 530 | 251 | 0 | — | CANON.md L1559 name lock 2026-10-22; roster/kuma/CANON.md: moveset scaffolding is the bear bank (technical only). Corrections use the Kuma graph. |
| gyou-spirit-body.json | GYOU (spirit-body form file) | NONE FOUND in canon for this form (file data: Tekken — Paul Phoenix) | D | 567 | 278 | 0 | — | roster/gyou/CANON.md defines the spirit body and its forms but states NO moveset base; the Paul wiring conflicts with Gyou's canon Hwoarang base and has no canon citation. DECISION LIST — untouched. |
| gyou.json | GYOU (soul) | Tekken — Hwoarang | 1-W + 3-residue | 1005 | 496 | 0 | — | ROSTER.md L71; CANON.md L1555 'Hwoarang→GYOU'. The file's own tekken_base field says 'Paul' — field error vs canon; anim bank is hwoarang. Corrections use the Hwoarang graph. Residue: 47 paul-bank anim_t3, no canon basis — Phase 2 item. |
| hugo.json | Hugo Andore (data file) | Final Fight / Street Fighter — Hugo Andore | 1-C | 130 | 0 | 0 | — | Data file (SOURCE-MERGE not-merged list). No CANON.md entry. |
| index.json | — | — | DATA | — | — | — | — | Non-fighter data file (no moves dict). |
| iori.json | Iori Yagami (data file) | KOF — Iori Yagami | 1-C | 196 | 0 | 0 | — | Data file; Deathfang's base source. Heihachi anim_t3 is the declared proxy layer. |
| jin_soul.json | JIN — identity ambiguous (soul JIN vs Jin Kazama) | Tekken — Yoshimitsu (per file/wiring) — CONFLICTS with Jin Kazama canon | D | 1012 | 509 | 0 | — | Two different 'Jins': ROSTER.md L50 soul JIN = Yoshimitsu style; CANON.md L988-1006 Jin Kazama = Mishima-ryu. Which canon identity this file serves is stated nowhere. DECISION LIST — untouched. |
| kai.json | KAI (soul) | Tekken — Eddy Gordo | 1-W | 877 | 364 | 0 | — | ROSTER.md L43. King Tyrant's soul file; same base as kingtyrant. Corrections use the Eddy graph. |
| kingtyrant.json | KING TYRANT | Tekken — Eddy Gordo | 1-W | 848 | 250 | 0 | — | CANON.md L403 'Eddy Gordo base. Straightforward reskin.' Corrections use the Eddy graph. Booker T moves were NOT invented (SOURCE-MERGE known limits) — no wrestling donor is approved. |
| kinpo.json | KINPO | Tekken — Asuka Kazama | 1-S | 525 | 0 | 103 | — | CANON.md L338 'Asuka base.' File t3_source says jin — field mismatch; anim data is asuka-bank. 103 UNMAPPED await the Asuka T7 source (Steam lane preferred when it lands). |
| koreshi.json | KORESHI | Street Fighter — Vega | 1-core + 3-layer | 1080 | 0 | 0 | vega×571, sf-vega×180 | roster/koreshi/CANON.md: 'Base/animation bank: Vega (owner mapping, 2026-10-20).' Donors vega×571 + sf-vega×180 are the SAME character from two source sets — canon core. LAYER: 312 yoshimitsu-bank anim_t3 — a production lane once set Koreshi's base to Yoshimitsu; the same canon doc records that as NOT owner-specified and rejected. Phase 2 replaces the Yoshimitsu layer from the Vega source; what Vega lacks stays UNMAPPED by name. |
| kronos-attire2.json | KRONOS (Attire 2 — TimberWolf) | Street Fighter — Zangief | 2 | 2600 | 0 | 0 | kronos×1815, zangief×463, sf-zangief×180 | Approved mix — see Class 2 citations. donor kronos×1815 = self-inheritance; zangief×463 + sf-zangief×180 are the canon base. NOT reworked. |
| kronos.json | KRONOS | Street Fighter — Zangief | 2 | 900 | 0 | 0 | zangief×463, sf-zangief×180 | Approved mix — roster/kronos/CANON.md: 'Zangief moves plus other fighters mixed in (Golem from Urban Reign, etc.)'. NOT reworked. |
| kutz.json | KUTZ | Virtua Fighter — Goh Hinogami (wiring-doc base only) | 1-C | 160 | 0 | 0 | — | No CANON.md entry found (SOURCE-MERGE not-merged list). |
| lili.json | Lili (retired-name original file) | Tekken — Lili De Rochefort | 1-S | 508 | 0 | 0 | — | Own-character file; in WH canon this fighter is Silvertongue (owner canon law 2026-10-23). Duplicate identity with silvertongue.json — same base, two files. |
| marduk.json | Craig Marduk (original/guest file) | Tekken — Craig Marduk | 1-C | 340 | 0 | 0 | — | Built on t7:marduk (SOURCE-MERGE). No WH canon name found. |
| mariposa-monarch.json | MARIPOSA (Monarch attire file) | Tekken — Zafina | 1-S | 518 | 0 | 0 | — | CANON.md L1117 'Monarch → Slot 3'; self-inheritance from mariposa.json. Zafina T7/T8 source pending. |
| mariposa.json | MARIPOSA | Tekken — Zafina | 1-S | 372 | 0 | 0 | — | CANON.md L1111: Zafina's Tekken frame is the moveset base (the Tripo butterfly is the Attire-1 MODEL default, not the moveset). No T3 row refs exist for Zafina; T7/T8 source pending. |
| megami.json | MEGAMI | Tekken Tag Tournament 2 — Jun Kazama (document-sourced) | 1-S | 304 | 0 | 0 | — | No CANON.md entry. Movelist was document-sourced; the decoded TTT2 data now in this repo (PR #1235 layer + teardown) is its future real source. 20 no-anim moves. |
| menajerii.json | MENAJERII | Tekken Tag Tournament 2 — Roger Jr. (document-sourced) | 1-S | 193 | 0 | 0 | — | No CANON.md entry. As megami: TTT2 data is the future source. 51 no-anim moves. |
| michiko.json | MICHIKO | Tekken — Katarina Alves | 1-C | 344 | 0 | 0 | — | CANON.md L720 'Katarina Alves base.' T7-import file, no guess-grade. |
| negativo.json | N3GΔTIV0 / NEGATIVO | Tekken 7 — Negan | 1-C | 292 | 0 | 0 | — | CANON.md L913 'Negan base.' Its 'No Mercy' move NAME is not No Mercy-sourced (anim_ref is t7:negan:) — listed in the 2026-10-29 audit §f to prevent a false flag. |
| nightwolf.json | NIGHTWOLF | Tekken — Julia Chang | 1-W | 567 | 179 | 0 | — | CANON.md L688 'Julia Chang base.' Corrections use the Julia graph. |
| pantera.json | PANTERA | Tekken — King | 1-W | 874 | 198 | 109 | — | CANON.md L69; ROSTER.md L83-86. Step plans landed in PR #1232 (Batch 1: 57 REVIEW candidates, 41 occurrences UNMAPPED by name — none promoted to verified; FK gate + play-verify still owed). This lane corrects the remaining guess-grade anim_t3 via the King graph. 109 UNMAPPED await the King T7 clip source. The No Mercy grappling library is a shared library (CANON.md L1591-93), not a second base. |
| phantom.json | PHANTOM | Tekken — Yoshimitsu | 1-W | 1019 | 295 | 127 | — | CANON.md L123; ROSTER.md L97-98. Corrections use the Yoshimitsu graph. 127 UNMAPPED await the Yoshimitsu T7 source. |
| pond.json | POND | Tekken 7 — Raven (wiring-doc base only) | 1-S | 620 | 0 | 0 | — | No CANON.md entry (gaps doc: Pond missing canon). 151 no-anim moves; Raven T7 source pending (Steam lane preferred when it lands). |
| purplerain.json | PURPLE RAIN | Tekken — Lee Chaolan | 1-C | 569 | 0 | 0 | — | CANON.md L658 'Lee Chaolan base.' No guess-grade. |
| raiden.json | RAIDEN | Fatal Fury / KOF — Big Bear / Raiden (wiring-doc base only) | 1-C | 114 | 0 | 0 | — | No CANON.md entry found. Data rides the gunjack bank as a stand-in layer over its own move list. |
| rave.json | RAVE (= Kiko Tanaka) | Tekken — Lei Wulong | 2 | 1086 | 20 | 0 | byou×158 | Approved mix — SOURCE-MERGE owner corrections: 'U can add leis and byous moves to rave' (donor byou×158 is the approved Byou addition). Zui decision (2026-10-24) confirms 'Rave KEEPS his full Lei moveset.' NOT reworked. |
| realizzt.json | REALIZZT (Brad Burns) | Virtua Fighter — Brad Burns (wiring-doc base only) | 1-C | 156 | 0 | 0 | — | No CANON.md entry found. (The Enzo Amore tie is a likeness/voice reference, not a moveset base.) |
| retsu.json | RETSU (soul) | Tekken — Bryan Fury | 1-W | 739 | 388 | 0 | — | ROSTER.md L57. Skull's soul file; same base as skull. Corrections use the Bryan graph. |
| rin.json | RIN (soul) | Tekken — Jin Kazama | 1-W | 710 | 246 | 0 | — | ROSTER.md L14. Demonio shares the Jin slot (replacement-map flags the slot claim). Corrections use the Jin graph. |
| ryuji-rock.json | CORNERSTONE (internal id ryuji-rock) | KOF — Ryuji Yamazaki | 2 | 129 | 0 | 0 | — | Approved mix — CANON.md L1297-1309 (owner words): Yamazaki stance/moveset + The Rock's uranage/Rock Bottom (from King AND WWE sources) + King diving elbow + Toguro fingernail blast as approved INTENT (source not yet in hand, never invented). Its 7 No Mercy-sourced Rock specials are SUSPECT (wrong FileTable window) — flagged, not fixed. NOT reworked. |
| ryuji.json | RYUJI (pure Yamazaki entry) | KOF — Ryuji Yamazaki | 1-C | 127 | 0 | 0 | — | CANON.md L1311: 'The pure-Yamazaki roster entry (ryuji, carrying the full KOF set) is untouched and stays in the repo.' SOURCE-MERGE's 'hybrid' label for this file is a doc error — the hybrid is ryuji-rock; CANON.md wins. |
| ryusan.json | RYUSAN | Tekken 7 — Lucky Chloe (wiring-doc base only) | 1-S | 211 | 0 | 0 | — | No CANON.md entry (gaps doc: Ryusan missing canon). T7 source pending. |
| sakura.json | SAKU RA | Tekken — Ling Xiaoyu | 1-W | 764 | 185 | 0 | — | CANON.md L244/L270 'Xiaoyu base.' Corrections use the Xiaoyu graph. |
| samura1.json | SAM-UR-A1 | Tekken 3 — Gun Jack | 1-W | 860 | 218 | 0 | — | CANON.md L237 'Gun Jack base.' Wiring also uses Jack-7/Jack-8 era data — the same robot lineage; canon names Gun Jack. Graph corrections apply to the gunjack-bank mappings; jack-8-bank mappings await a Jack source. |
| scimitar.json | SCIMITAR | Tekken — Shaheen | 1-S | 362 | 0 | 57 | — | CANON.md L628 'Shaheen base.' 57 UNMAPPED await the Shaheen T7 source. |
| sf-akuma.json | Akuma (SF data file) | Street Fighter — Akuma (as in Tekken 7) | 1-S | 168 | 0 | 0 | — | Data file; the WH fighter using Akuma is Dio. Heihachi/T7 anim layers are stand-ins pending SF/T7-Akuma extraction. |
| sf-blanka.json | Blanka (SF data file) | Street Fighter — Blanka | 1-S | 37 | 0 | 0 | — | Data file. Bryan bank is a stand-in anim layer (declared pattern for the thin SF files). |
| sf-cammy.json | Cammy (SF data file) | Street Fighter — Cammy | 1-S | 10 | 0 | 0 | — | Thin data file (10 moves, no anim mapping). 'Akuma-pattern translation' in SOURCE-MERGE is a data-translation pattern, NOT an approved Akuma mix. |
| sf-chunli.json | Chun-Li (SF data file) | Street Fighter — Chun-Li | 1-S | 10 | 0 | 0 | — | As sf-cammy. |
| sf-dhalsim.json | Dhalsim (SF data file) | Street Fighter — Dhalsim | 1-S | 10 | 0 | 0 | — | As sf-cammy. |
| sf-guile.json | Guile (SF data file) | Street Fighter — Guile | 1-S | 11 | 0 | 0 | — | As sf-cammy. |
| sf-ken.json | Ken (SF data file) | Street Fighter — Ken Masters | 1-S | 32 | 0 | 0 | — | Data file. Jin bank is a stand-in anim layer. |
| sf-mbison.json | M. Bison (SF data file) | Street Fighter — M. Bison | 1-S | 12 | 0 | 0 | — | As sf-cammy. |
| sf-ryu.json | Ryu (SF data file) | Street Fighter — Ryu | 1-S | 34 | 0 | 0 | — | Data file. Jin bank is a stand-in anim layer. |
| sf-sagat.json | Sagat (SF data file) | Street Fighter — Sagat | 1-S | 10 | 0 | 0 | — | As sf-cammy. |
| sf-vega.json | Vega (SF data file) | Street Fighter — Vega | 1-S | 36 | 0 | 0 | — | Data file; one of Koreshi's two Vega source sets. Xiaoyu bank is a stand-in anim layer. |
| sf-zangief.json | Zangief (SF data file) | Street Fighter — Zangief | 1-S | 36 | 0 | 0 | — | Data file; one of Kronos's Zangief source sets. King bank is a stand-in anim layer. |
| sha.json | SHA (soul) | Tekken — Ling Xiaoyu | 1-W | 785 | 185 | 0 | — | ROSTER.md L36. Saku Ra is its vessel. The soul does not impose one base on its vessels (CANON.md L420: SHA's vessels hold Xiaoyu/Asuka/Nina bases respectively). Corrections use the Xiaoyu graph. |
| silvertongue.json | SILVERTONGUE | Tekken 7 — Lili De Rochefort | 1-S | 508 | 0 | 0 | — | CANON.md L954: 'Lili's Tekken 7 frame.' Duplicate identity with lili.json (retired-name file). No guess-grade; T7 Lili source pending. |
| skull.json | SKULL | Tekken — Bryan Fury | 1-W | 688 | 244 | 114 | — | CANON.md L180; ROSTER.md L109-112. Corrections use the Bryan graph. 114 UNMAPPED await the Bryan T7 source. |
| slice.json | SLICE | Tekken — Sergei Dragunov | 1-C | 486 | 0 | 0 | — | CANON.md L1253 (owner words). Wiring t8:dragunov/t7:dragunov. No guess-grade. |
| star.json | STAR | Tekken — Christie Monteiro | D | 908 | 290 | 0 | — | CANON.md L752 'Christie Monteiro base' — but the file's moves come from the xiaoyu (+eddy) banks, and ROSTER-REPLACEMENT-MAP itself flags: 'star: slot Christie but moves come from {xiaoyu}; owner must confirm which Tekken slot.' DECISION LIST — untouched. |
| street-reign.json | STREET REIGN (stub) | NONE FOUND | 3 | 5 | 0 | 0 | — | No canon, roster, decision, or wiring-doc base found anywhere. 5 moves, 0 with any anim mapping — a placeholder stub. Named on the Decision List for a base assignment; nothing to replace from until then. |
| sunra.json | SUN RĀ (boss/realm, not a tournament fighter) | Pac-Man — Pac-Man | 1-C | 139 | 0 | 0 | — | CANON.md L1190: 'Sun Rā (Pac-Man base)... Not a fighter. A realm.' Heihachi bank entries are the standard residue. |
| t3-anna.json | Anna Williams (T3 original bank file) | Tekken 3 — Anna Williams | 1-W | 743 | 400 | 0 | — | Self-base bank file. CANON.md appendix: 'Anna→TORCH'. Corrections use the Anna graph. |
| t3-bosconovitch.json | Dr. Bosconovitch (T3 original bank file) | Tekken 3 — Dr. Bosconovitch | 1-C | 266 | 0 | 0 | — | Self-base bank file. CANON.md appendix: 'Dr. Bosconovitch→DOC FRANK'. No guess-grade (no anim_t3 layer). |
| t3-eddy.json | Eddy Gordo (T3 original bank file) | Tekken 3 — Eddy Gordo | 1-W | 707 | 364 | 0 | — | Self-base bank file. CANON.md L1554: 'Eddy→KING TYRANT (soul KAI)'. Corrections use the Eddy graph. |
| t3-forestlaw.json | Forest Law (T3 original bank file) | Tekken 3 — Forest Law | 1-C | 102 | 0 | 0 | — | Self-base bank file; one of Buffalo Bill's two Law sources. No guess-grade. |
| t3-gon.json | Gon (T3 original bank file) | Tekken 3 — Gon | 1-C | 151 | 0 | 0 | — | Self-base bank file; Dorowani's source. No guess-grade. |
| t3-hwoarang.json | Hwoarang (T3 original bank file) | Tekken 3 — Hwoarang | 1-W | 723 | 496 | 0 | — | Self-base bank file. CANON.md L1555: 'Hwoarang→GYOU'. Corrections use the Hwoarang graph. |
| t3-julia.json | Julia Chang (T3 original bank file) | Tekken 3 — Julia Chang | 1-W | 419 | 179 | 0 | — | Self-base bank file. CANON.md L1555: 'Julia→NIGHTWOLF / soul ZEN' (the flagged conflict concerns Zen, resolved 2026-10-24 — see zen.json). Corrections use the Julia graph. |
| t3-kuma.json | Kuma (T3 original bank file) | Tekken 3 — Kuma | 1-W | 530 | 251 | 0 | — | Self-base bank file; Gashadokuro's scaffolding bank. Corrections use the Kuma graph. |
| t3-law.json | Marshall Law (T3 original bank file) | Tekken 3 — Marshall Law | 1-W | 693 | 390 | 0 | — | Self-base bank file; Buffalo Bill's source (mapping landed 2026-10-23). Corrections use the Law graph. |
| t3-lei.json | Lei Wulong (T3 original bank file) | Tekken 3 — Lei Wulong | 1-W | 790 | 464 | 0 | — | Self-base bank file; Rave's source. Corrections use the Lei graph. |
| t3-nina.json | Nina Williams (T3 original bank file) | Tekken 3 — Nina Williams | 1-W | 754 | 425 | 0 | — | Self-base bank file. CANON.md appendix: 'Nina→AWA POP'. Corrections use the Nina graph. |
| t3-ogre.json | Ogre (T3 original bank file) | Tekken 3 — Ogre | 1-C | 161 | 0 | 0 | — | Self-base bank file; Chatur's wiring source. No guess-grade. |
| t3-paul.json | Paul Phoenix (T3 original bank file) | Tekken 3 — Paul Phoenix | 1-W | 497 | 278 | 0 | — | Self-base bank file. CANON.md L1554: 'Paul→TOU'. Corrections use the Paul graph. |
| t3_input_tables.json | — | — | DATA | — | — | — | — | Non-fighter data file (no moves dict). |
| thor.json | THOR | Tekken — Ganryu | 1-S | 322 | 0 | 0 | — | CANON.md L1225 (owner words): 'Ganryu is Thor.' 78 no-anim moves await a Ganryu source; Bryan entries are the standard 4-row residue. |
| tobi.json | TOBI | Tekken 3 — Hwoarang (wiring-doc base only) | 1-W | 729 | 496 | 0 | — | No CANON.md entry (gaps doc: Tobi missing canon). Data is a straight T3 Hwoarang port (FULL-REAL on the hwoarang bank per Coverage). Slot also claimed by Gyou — noted, data work is unaffected. Corrections use the Hwoarang graph. |
| torch.json | TORCH | Tekken — Anna Williams | 1-W | 892 | 270 | 0 | — | CANON.md L782 'Anna Williams base.' Corrections use the Anna graph (anim bank anna; jin entries are the standard residue). |
| tou.json | TOU (soul) | Tekken — Paul Phoenix | 1-W | 681 | 278 | 0 | — | ROSTER.md L29; CANON.md L1554 'Paul→TOU'. Coverage bank heihachi ≠ base — the anim data is paul-bank; corrections use the Paul graph. |
| ur-char001.json | — | — | DATA | — | — | — | — | Non-fighter data file (no moves dict). |
| ur-char002.json | — | — | DATA | — | — | — | — | Non-fighter data file (no moves dict). |
| ur-char003.json | — | — | DATA | — | — | — | — | Non-fighter data file (no moves dict). |
| ur-char004.json | — | — | DATA | — | — | — | — | Non-fighter data file (no moves dict). |
| ur-char005.json | — | — | DATA | — | — | — | — | Non-fighter data file (no moves dict). |
| ur-char016.json | — | — | DATA | — | — | — | — | Non-fighter data file (no moves dict). |
| ur-char020.json | — | — | DATA | — | — | — | — | Non-fighter data file (no moves dict). |
| ur-char021.json | — | — | DATA | — | — | — | — | Non-fighter data file (no moves dict). |
| ur-char022.json | — | — | DATA | — | — | — | — | Non-fighter data file (no moves dict). |
| ur-char030.json | — | — | DATA | — | — | — | — | Non-fighter data file (no moves dict). |
| ur-char031.json | — | — | DATA | — | — | — | — | Non-fighter data file (no moves dict). |
| ur-char032.json | — | — | DATA | — | — | — | — | Non-fighter data file (no moves dict). |
| ur-char041.json | — | — | DATA | — | — | — | — | Non-fighter data file (no moves dict). |
| ur-char042.json | — | — | DATA | — | — | — | — | Non-fighter data file (no moves dict). |
| ur-char043.json | — | — | DATA | — | — | — | — | Non-fighter data file (no moves dict). |
| ur-char044.json | — | — | DATA | — | — | — | — | Non-fighter data file (no moves dict). |
| ur-char045.json | — | — | DATA | — | — | — | — | Non-fighter data file (no moves dict). |
| ur-char046.json | — | — | DATA | — | — | — | — | Non-fighter data file (no moves dict). |
| ur-char054.json | — | — | DATA | — | — | — | — | Non-fighter data file (no moves dict). |
| ur-char055.json | — | — | DATA | — | — | — | — | Non-fighter data file (no moves dict). |
| ur-char056.json | — | — | DATA | — | — | — | — | Non-fighter data file (no moves dict). |
| ur-char057.json | — | — | DATA | — | — | — | — | Non-fighter data file (no moves dict). |
| ur-char058.json | — | — | DATA | — | — | — | — | Non-fighter data file (no moves dict). |
| ur-char059.json | — | — | DATA | — | — | — | — | Non-fighter data file (no moves dict). |
| ur-char060.json | — | — | DATA | — | — | — | — | Non-fighter data file (no moves dict). |
| ur-char061.json | — | — | DATA | — | — | — | — | Non-fighter data file (no moves dict). |
| ur-char062.json | — | — | DATA | — | — | — | — | Non-fighter data file (no moves dict). |
| ur-char063.json | — | — | DATA | — | — | — | — | Non-fighter data file (no moves dict). |
| ur-char070.json | — | — | DATA | — | — | — | — | Non-fighter data file (no moves dict). |
| ur-char071.json | — | — | DATA | — | — | — | — | Non-fighter data file (no moves dict). |
| ur-char072.json | — | — | DATA | — | — | — | — | Non-fighter data file (no moves dict). |
| ur-native-index.json | — | — | DATA | — | — | — | — | Non-fighter data file (no moves dict). |
| vainabel.json | VAIN ABEL ELIAS | DOA — Bass Armstrong | 1-S | 60 | 0 | 0 | — | roster/vainabel/CANON.md: 'Bass Armstrong (DOA) is his base in Western Heart: he needs ALL of Bass Armstrong's moves, motions, animations (owner 2026-10-16).' Kane is his likeness/story basis, NOT a moveset base. DOA anim extraction pending. |
| vega.json | Vega (WH-side source file) | Street Fighter — Vega | 1-S | 207 | 0 | 0 | — | Koreshi's primary Vega source file (sf-vega.json is the second source set — one character, two sets). Its own anim layer rides xiaoyu-bank stand-ins. |
| vf-akira.json | Akira Yuki (data file) | Virtua Fighter 5 FS — Akira Yuki | 1-S | 20 | 0 | 0 | — | Data file, not a WH roster fighter (DOA-VF-CONVERSION table). |
| vf-elblaze.json | El Blaze (data file) | Virtua Fighter 5 — El Blaze | 1-S | 28 | 0 | 0 | — | Data file; Pablo's Ashlane base source (CANON.md L1500, 'technical only — never in canon'). |
| vf-jeffry.json | Jeffry McWild (data file) | Virtua Fighter 5 — Jeffry McWild | 1-S | 25 | 0 | 0 | — | Data file; Bannon's Ashlane base source (CANON.md L1436, technical only). |
| vf-kage.json | Kage-Maru (data file) | Virtua Fighter 5 FS — Kage-Maru | 1-S | 14 | 0 | 0 | — | Data file (DOA-VF-CONVERSION table). |
| vf-leifei.json | Lei-Fei (data file) | Virtua Fighter 5 — Lei-Fei | 1-S | 812 | 464 | 0 | — | Data file; NPC Finxsse's Ashlane base source (CANON.md L1534, technical only). DATA WARNING: this file's content is overwhelmingly the Lei Wulong set (524 t7:lei refs, 266 t3:lei refs, only 22 vf: refs) under a Lei-Fei label — it is EXCLUDED from Phase 1 graph corrections (Lei-Fei ≠ Lei Wulong; correcting it as Lei would entrench the mislabel). The VF conversion program owns its rebuild. |
| vf-sarah.json | Sarah Bryant (data file) | Virtua Fighter 5 FS — Sarah Bryant | 1-S | 14 | 0 | 0 | — | Data file (DOA-VF-CONVERSION table). |
| vf-wolf.json | Wolf Hawkfield (data file) | Virtua Fighter 5 — Wolf Hawkfield | 1-S | 21 | 0 | 0 | — | Data file; El Toro de Oro's Ashlane base source (CANON.md L1468, technical only). |
| waterfall.json | WATERFALL | Tekken — Josie Rizal | 1-C | 365 | 0 | 0 | — | CANON.md L371 'Josie Rizal base.' No guess-grade. |
| yukihyo.json | YUKIHYŌ | Tekken — Armor King | 1-C | 560 | 0 | 0 | — | CANON.md L1265: 'YUKIHYŌ is the Western Heart version of Armor King.' No guess-grade. |
| zangief.json | Zangief (bank file) | Street Fighter — Zangief | 1-C | 217 | 0 | 0 | — | Kronos's base bank data (roster/kronos/CANON.md: 'no separate Zangief fighter exists or is needed'). King-bank anim_t3 is the stand-in layer for the SF move list. |
| zen.json | ZEN (soul/fighter) | Street Fighter — Eleven/Twelve (concept) via Virtua Fighter 5 — Dural (3D base) + Zen's own canon moves | 2 | 644 | 0 | 0 | — | Approved mix — docs/decisions/2026-10-24-zen-base-decision.md + roster/zen/CANON.md. Supersedes ROSTER.md L64 (Julia) and the interim Heihachi rows. FIGHTER_BANK zen is null/UNMAPPED by owner decision — no Dural bank exists yet. NOT reworked. |
| zui.json | ZUI | Tekken — Steve Fox | 2 | 654 | 0 | 0 | — | Approved mix — docs/decisions/2026-10-24-zui-mix-per-canon.md: Steve Fox base + Lei Wulong drunken fist + WH originals. Legacy T3 Jin proxy layers in the file are explicitly NOT part of the canon mix (decision doc) — noted, not reworked (class 2 files are out of this lane's edit scope). |

## Appendix A — Class 2 approvals (verbatim citations)

1. **zui.json — Steve Fox base + Lei Wulong drunken fist + WH originals.** `docs/decisions/2026-10-24-zui-mix-per-canon.md` L1 (title): "ZUI MIX PER CANON — Steve Fox base + Lei Wulong drunken fist + WH originals (2026-10-24)"; L5-8: "Zui's moveset is a MIX per canon — Steve Fox base PLUS Lei Wulong drunken fist moves PLUS other moves mixed in per canon. Zui KEEPS his hands-up drunken stagger stance (do NOT change it). Sharing, not transfer: Lei's drunken fist moves go to Zui TOO; Rave KEEPS his full Lei moveset. Nothing is removed from Rave." Mix counts L32-34: Steve Fox T7 base 345 keys / Lei drunken 40 keys / WH original canon 4 keys.
2. **zen.json — Eleven/Twelve concept + Dural (VF5) 3D base + own canon + one X.COPY super.** `docs/decisions/2026-10-24-zen-base-decision.md` L1: "Zen = Eleven/Twelve/Dural + own canon, NOT Heihachi, NOT Julia"; L9-12 (owner decision): "Zen's base is neither of those. Zen is like 11 and 12 but not just a copycat he has his own moves he has all these different things that go with him and to his character and his canon so his thing is completely built off of that and like a little bit of copy X but like not really copy X". `roster/zen/CANON.md`: "Base mix: Dural (Virtua Fighter 5) + Twelve/Eleven on top, owner 2026-10-22".
3. **ryuji-rock.json — CORNERSTONE: Yamazaki base + The Rock + King pieces + Toguro (intent).** CANON.md L1297 (owner words): "I told u how ryuji character will be mixed with the rock from WWE and do the uranage/rock bottom, he will also get the rock bottom from king and from WWE all stars, and some animations of the rock from the WWE teardown games, and kings jumping diving elbow attack, mixed with ryuji yamazakis stance and taunts and moveset and antics mixed with the rock persona from early attitude era WWE. And his name will be CornerStone"; L1299: "His moveset was set the same night: Ryuji base + The Rock's moves (Rock Bottom — King has it in Tekken, pull from there) + wrestling moves from Urban Reign, Tekken, and the other teardown games."; L1307-1309: Toguro fingernail blast approved "when a Yu Yu Hakusho teardown source is in hand... never invented" (approved intent; source not yet in hand).
4. **kronos.json + kronos-attire2.json — Zangief base + other fighters mixed in.** `roster/kronos/CANON.md`: "KRONOS — a custom Zangief-based fighter (owner, 2026-10-19)"; Moves/base: "Base/animation bank: Zangief. Moveset: Zangief moves plus other fighters mixed in (Golem from Urban Reign, etc.), with Tekken-style inputs."
5. **rave.json — Lei Wulong base + Byou's moves added.** `docs/movesets/SOURCE-MERGE-2026-10-21.md`, owner corrections: "Lei Wulong = RAVE / Kiko Tanaka, not Byou" + Rave gets "Lei T7 + Lei T3 + Byou's moves ('U can add leis and byous moves to rave')".
6. **cainelias.json — approved spec, base unresolved (2-spec).** CANON.md L1273: "Moveset: Glen Kluger (Urban Reign biker gang leader) or a fitting Tekken character — NOT one already remade. Signature moves include the Last Ride powerbomb and the Tombstone"; L1279: "Moveset pick owned by the moveset lane" — the elements are owner-directed; which base was never settled in canon.
7. **GLOBAL (not a base mix) — WH canon signature moves added additively to 66 files.** `docs/canon-movelist-wiring-2026-10-24.md` L3 (owner directive, 2026-10-24): "make sure all extra canon animations that are pulled from non Tekken games or made get added to the move list creator and to appropriate additive Tekken style input to each character they go to individually"; L8: "Additive only. No Tekken moves entry was replaced, overwritten, or deleted."

## Owner Decision List (verbatim — these fighters are NOT touched by this lane)

1. **star.json (STAR)** — Canon base is Christie Monteiro (CANON.md L752), but the file's moves come from the xiaoyu bank (+145 eddy-bank anim_t3). ROSTER-REPLACEMENT-MAP flags it in the repo's own words: "star: slot 'Christie' but moves come from {xiaoyu}; owner must confirm which Tekken slot." Question for the owner: is Star's base Christie (replace the Xiaoyu/Eddy data from a Christie source when one is extracted) or is the Xiaoyu slot intended?
2. **byou.json (BYOU, soul)** — The owner correction of 2026-10-21 records that Byou's base "is not recorded anywhere" and the file must keep "exactly its origin/main file"; CANON.md L1556 leaves the Lei vessel naming decision pending. The file's data currently rides Lei/T7-Jin wiring (571 cross-bank anim_t3). Question: what is Byou's moveset base?
3. **jin_soul.json (JIN)** — Identity conflict: ROSTER.md L50's soul JIN is Yoshimitsu-style; CANON.md L988-1006's Jin Kazama is Mishima-ryu. The file is built on Yoshimitsu. Question: which canon identity does this file serve?
4. **demonio-winged.json (DEMONIO, winged/Devil form)** — Built on Jin + Devil Jin (wiring). Canon gives Demonio a Jin base and a Devil-Gene bloodline theme but no line approves a Devil Jin moveset layer. Question: is the Devil Jin layer approved for Demonio's winged form?
5. **gyou-spirit-body.json (GYOU, spirit-body form)** — The form is the playable fighter per roster/gyou/CANON.md, but no moveset base is stated for it; the file's data is Paul Phoenix, which conflicts with Gyou's canon Hwoarang base. Question: what is the spirit-body form's base — Hwoarang like Gyou, or Paul?
6. **charger.json + charger-attire2.json (CHARGER)** — No canon base exists for Charger himself; the files carry Blanka (SF) data as a stand-in (SOURCE-MERGE: his SF 3D moves "need WWE/SF data decoded first"). Question: what is Charger's moveset base?
7. **street-reign.json (STREET REIGN stub)** — 5 moves, no anim mapping, no base stated in any canon, roster, decision, or wiring doc. Question: does this fighter exist, and what is its base?
8. **cainelias.json (CAIN ELIAS)** — The mix spec is approved (Appendix A.6) but the base was left open: Glen Kluger (Urban Reign) OR a fitting Tekken character not already remade. Question: which base? (Separately: its 5 No Mercy anim_refs are SUSPECT — see the No Mercy note.)
9. **Echo (no moveset file exists)** — The lane brief named an owner-approved "copy-opponents" trait for Echo; no Western Heart canon doc supports it. In canon, copy/mimicry traits belong to The Trader (CANON.md L481; ROSTER.md: "Mokujin's mimicry moveset"), DXMMII/Mokujin, and Zen's single X.COPY super. Echo appears in roster/buffalo-bill/CANON.md only as a Wizard Gang wizard. Question: does Echo have a copy-moveset in Western Heart, or was that another show's trait?
10. **koreshi.json Yoshimitsu layer (Phase 2 confirmation)** — roster/koreshi/CANON.md already records the Yoshimitsu base attempt as "not owner-specified. It is not canon; Vega stands." This lane reads that as settled — Phase 2 will replace the 312-move Yoshimitsu anim layer from Koreshi's Vega source and leave what Vega lacks UNMAPPED by name. It is listed here so the owner can stop it if that reading is wrong.

## Phase 1 program (class 1 first — in progress under this doc's PR series)

Branch-walk corrections run per bank group, one PR per fighter file (attire variants of one fighter may share a PR), tests green (batch1 / attack-anim / combat-systems / root-motion), per-character isolation. Groups: King (pantera); Lei (t3-lei); Hwoarang (t3-hwoarang, gyou, tobi); Nina (t3-nina, awapop); Anna (t3-anna, torch); Law (t3-law, buffalo-bill); Eddy (t3-eddy, kai, kingtyrant); Paul (t3-paul, tou); Julia (t3-julia, nightwolf); Kuma (t3-kuma, aotsuki, gashadokuro); Bryan (skull, retsu); Jin (demonio, demonio-human, demonio-bloodline-ember, rin); Heihachi (diablo); Yoshimitsu (phantom); Xiaoyu (sakura, sha); Gun Jack (samura1 — gunjack-bank mappings only); Bosconovitch (doc-frank-frankenstein, doc-frank-hood, doc-frank-machine-shop, doc-frank-wowomomo).

Known limit, stated plainly: the branch-walk proofs fire where an anchor (a direct native twin, a validated strings path, or a unique branch chain) exists. Stance-state and directional-first-step moves (WS/FC/BT/stance prefixes, slide inputs) mostly do NOT prove with current tooling — their T3 identity runs through branch **condition codes** that have not been decoded yet. Those mappings stay guess-grade, are counted per fighter in each Phase 1 PR, and the condition-code decode is the named research that unblocks them. Nothing is promoted without a proof, and no corrected row is video-verified — in-fight video proof belongs to the play-verify lane (the Pantera session video is being produced separately; PR #1232's step-plan REVIEW candidates still owe their FK gate + play-verify and are NOT promoted by this lane).

1-S gaps (UNMAPPED / no-anim) stay UNMAPPED by name until the fighter's own source lands: T7/T8 via the Steam-library extraction lane (preferred over inference when it lands, per the owner addendum), TTT2 via the decoded TTT2 data now in this repo (megami, menajerii), DOA/VF via their own conversion programs.

## Phase 2 scope (starts only after Phase 1 is fully landed)

- **koreshi.json** — replace the 312-move Yoshimitsu anim layer from the Vega source files (vega.json / sf-vega.json notations); what Vega lacks stays UNMAPPED by name.
- **demonio.json** — the 34 devil_jin-bank anim_t3: replace from the Jin source where Jin proves an equivalent; otherwise UNMAPPED by name. (demonio-winged as a whole is Decision List item 4, untouched either way.)
- **gyou.json** — the 47 paul-bank anim_t3: replace from the Hwoarang source; otherwise UNMAPPED by name.
- **street-reign.json** — no base exists to replace from; stays a named placeholder until Decision List item 7 is answered.

## No Mercy note (flagged, NOT fixed by this lane)

13 No Mercy-sourced rows remain SUSPECT (wrong FileTable window extraction), per `docs/movesets/REAL-MOVES-AUDIT-2026-10-29.md` §f: cainelias ×5 (`2+4`, `f+2+4`, `1+3`, `1+2+3+4_u1`, `1+2+3+4_u2`, pointing at wrong-window bank clips) and ryuji-rock ×7 (the Route-3-gated Rock specials). Negativo's `u/f+1+2` is a move NAME only (ref is t7:negan:) and is NOT No Mercy-sourced. The true-window re-extraction is a separate owed program; this lane flags and does not silently fix.

## Proof

- Classification inputs: `docs/movesets/REAL-MOVES-AUDIT-2026-10-29.md` (audit at main 1fa7d25f) + a full re-parse of `game/assets/movesets/` at the current main tip by this lane (56,527 moves / 129 moves-bearing files, totals agreeing with the audit), and the canon working papers (CANON.md, ROSTER.md, `docs/decisions/2026-10-24-zui-mix-per-canon.md`, `docs/decisions/2026-10-24-zen-base-decision.md`, `docs/movesets/SOURCE-MERGE-2026-10-21.md`, `roster/kronos/CANON.md`, `roster/koreshi/CANON.md`, `roster/gyou/CANON.md`, `roster/vainabel/CANON.md`, `roster/kuma/CANON.md`, `roster/panda/CANON.md`, `roster/zen/CANON.md`, `roster/buffalo-bill/CANON.md`, `roster/dorowani/README.md`).
- Phase 1 correction method: `teardown/tekken3/movesets/moveset_king.json` precedent from PR #1232 (`docs/movesets/REAL-MOVES-AUDIT-2026-10-29.md`, Corrections section), generalized to all 20 T3 bank graphs in `teardown/tekken3/movesets/` with `game/assets/anim/t3/lei/hit_frames.json`-format gates.

## Self-check: I verified the result against the literal instruction

Every fighter file in `game/assets/movesets/` appears exactly once in the table with a class decided from canon evidence (approval) + current-main data (provenance), in the owner's order: class 1 worked first (Phase 1), class 3 after (Phase 2), class 2 untouched, ambiguous cases on the Decision List untouched. No approval was inferred from data alone; no row in this lane is described as video-verified.
