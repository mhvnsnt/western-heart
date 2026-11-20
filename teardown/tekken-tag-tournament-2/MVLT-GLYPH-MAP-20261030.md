# TTT2 MVLT glyph → Tekken-notation map (2026-10-30)

Source: `data018.bin` (pulled 557,332 B, sha256
`7e06ad5336374973bf8f637b898c975585226fc7a260a730ad981365b2056db4`)
decoded to `decoded-data018.bin` (3,027,808 B, sha256
`54db09ebc63ee1a05a7b1c00cc2d7b5528d0d97c6ed1949da805daac7709293e`),
parsed by `parse_mvlt_v4.py` (authoritative; v1/v2/v3 superseded),
converted by `convert_mvlt_notation.py`.

Coverage: MVLT lists 1–57 = 6,559 records = 6,122 moves + 399 sample
combos + 38 stance separators. List 0 is a header/offset table, not a
character list. List 58 is a master/`title` list (433 rows mixing several
characters), not a character list. Mokujin (BXML doc 18) and Combot
(BXML doc 45) have customization docs but no MVLT lists. Unknown
(list 44) has a list but no BXML doc.

## Character join (MVLT list → character → BXML doc)

MVLT order is NOT BXML order after list 18. Identity is by move-name
fingerprint + published-movelist alignment + elimination; the count
argument closes it (58 BXML character docs − Mokujin − Combot + Unknown
= 57 lists). MainID = BXML index is proven by the data000
DirectionOffsets XML (tag pair 9/27 = Jin/Devil Jin; MainID 18 skipped
in KakeaiOffset but present in EnbuOffset = Mokujin).

| MVLT | Prefix | Character | BXML doc |
|---|---|---|---|
| 1 | pau | Paul Phoenix | 0 |
| 2 | law | Marshall Law | 1 |
| 3 | lei | Lei Wulong | 2 |
| 4 | kin | King | 3 |
| 5 | yos | Yoshimitsu | 4 |
| 6 | nin | Nina Williams | 5 |
| 7 | hwo | Hwoarang | 6 |
| 8 | xia | Ling Xiaoyu | 7 |
| 9 | chr | Christie Monteiro | 8 |
| 10 | jin | Jin Kazama | 9 |
| 11 | jul | Julia Chang | 10 |
| 12 | kum | Kuma | 11 |
| 13 | bry | Bryan Fury | 12 |
| 14 | hei | Heihachi Mishima | 13 |
| 15 | kaz | Kazuya Mishima | 14 |
| 16 | lee | Lee Chaolan | 15 |
| 17 | ste | Steve Fox | 16 |
| 18 | mar | Craig Marduk | 17 |
| 19 | jac | Jack-6 | 19 |
| 20 | rog | Roger Jr. | 20 |
| 21 | ann | Anna Williams | 21 |
| 22 | wan | Wang Jinrei | 22 |
| 23 | gan | Ganryu | 23 |
| 24 | ask | Asuka Kazama | 24 |
| 25 | bru | Bruce Irvin | 25 |
| 26 | bae | Baek Doo San | 26 |
| 27 | dvj | Devil Jin | 27 |
| 28 | rav | Raven | 28 |
| 29 | fen | Feng Wei | 29 |
| 30 | aki | Armor King II | 30 |
| 31 | lil | Lili | 31 |
| 32 | dra | Sergei Dragunov | 32 |
| 33 | pan | Panda | 43 |
| 34 | edd | Eddy Gordo | 33 |
| 35 | bob | Bob | 34 |
| 36 | zaf | Zafina | 35 |
| 37 | mig | Miguel | 36 |
| 38 | leo | Leo Kliesen | 37 |
| 39 | lar | Lars Alexandersson | 38 |
| 40 | asa | Alisa Bosconovitch | 39 |
| 41 | ji8 | Jinpachi Mishima | 40 |
| 42 | gre | True Ogre | 56 |
| 43 | jun | Jun Kazama | 42 |
| 44 | unk | Unknown | — (none) |
| 45 | knm | Kunimitsu | 48 |
| 46 | sli | Slim Bob | 50 |
| 47 | flw | Forest Law | 47 |
| 48 | mih | Miharu Hirano | 46 |
| 49 | ang | Angel | 49 |
| 50 | mic | Michelle Chang | 51 |
| 51 | pja | Prototype Jack | 55 |
| 52 | alx | Alex | 53 |
| 53 | ogr | Ancient Ogre | 41 |
| 54 | vio | Violet | 54 |
| 55 | bcv | Dr. Bosconovitch | 58 |
| 56 | seb | Sebastian | 57 |
| 57 | tig | Tiger Jackson | 52 |

## Glyph map

The command font is laid out as 8 tap directions, 8 hold directions,
then button combos in binary order by highest button, then a separator.

### Tap directions

| Glyph | Notation |
|---|---|
| E000 | d/b |
| E001 | d |
| E002 | d/f |
| E003 | b |
| E004 | f |
| E005 | u/b |
| E006 | u |
| E007 | u/f |

### Hold directions (capital = held, Tekkenpedia convention)

| Glyph | Notation |
|---|---|
| E008 | D/B |
| E009 | D |
| E00A | D/F |
| E00B | B |
| E00C | F |
| E00D | U/B (unused in all 57 lists) |
| E00E | U |
| E00F | U/F |

### Buttons (binary enumeration: groups by highest button)

| Glyph | Notation | Glyph | Notation |
|---|---|---|---|
| E015 | 1 | E01C | 4 |
| E016 | 2 | E01D | 1+4 |
| E017 | 1+2 | E01E | 2+4 |
| E018 | 3 | E01F | 1+2+4 |
| E019 | 1+3 | E020 | 3+4 |
| E01A | 2+3 | E021 | 1+3+4 |
| E01B | 1+2+3 | E022 | 2+3+4 (see note) |
| | | E023 | 1+2+3+4 |

### Separator

| Glyph | Meaning |
|---|---|
| E063 | Part separator inside sample combos and multi-part strings; rendered as `, ` |

## How each mapping was pinned (no guesses)

- Buttons/directions, True Ogre list 42 vs its published TTT2 movelist
  (row order matches exactly): 1,2 → 1,2; 3,2 → 3,2; 1+2,1+2,1+2 →
  1+2,1+2,1+2; 3+4 → 3+4; f+2, f+3; d/b+1, d/b+2, d/b+4; b+1, b+2,
  b+3,4, b+1+2; u/b+3; u+4, u+1+2, u+3+4.
- Ancient Ogre list 53 vs its published movelist: 1,1,2; 2,1; 2,d+1+2;
  f+2, f+3,2, f+4, f+1+2, f+3+4; 1+3 (Bear Hug), f+1+3 variant, 2+4
  (Mextli), f+2+4 variant, d/f,d/f+2+4 (Waning Moon).
- Armor King II list 30: Dark Cyclone 1+2,2; Dark Buzzsaw 1+2,4;
  Capital Punishment u/f+1+2 (vs True Ogre's u+1+2 — the u vs u/f
  distinction is real); Burning Knuckle u/f+1+2,D (matches the
  published trailing `D`); Moonsault Drop 1+4 (back-turned variation
  of Moonsault Body Press, 1+4).
- Jin list 10: Thrusting Uppercut f,N,d,d/f+1; Evil Intent b,f+2,1,2;
  Twin Lancer WS+1,2 (WS lives in condition text, not glyphs);
  Shoulder Flip 1+3 (or 2+4); Mental Alertness 1 = 1+3+4; Shun Ren Dan
  d/f+2+3.
- Miharu list 48 + Kunimitsu list 45 vs their published movelists:
  d+1, d+2, d+3, d+1+2, d/f+1, d/f+2, d/f+3,4, d/f+1+2, d/f+3+4,
  d/b+1, d/b+3, d/b+4, d/b+1+2, b+1, b+2,2, b+3, b+4, b+1+2, b+3+4,
  u+1+2, u/b+3+4, f+2,3, f+3, f+4, f+1+2, f+3+4.
- Yoshimitsu list 5: Stone Fists d/b,2×6; Manji Spin Low Kicks
  d/b,3×6 (T8 notation); Indian Stance d+3+4; Backfist to Stone Fist
  f+2,D/B+2,2×5.
- King list 4 chains (TTT multi-throw guides, 10/10 on Screwdriver):
  Rolling Death Cradle 1+3,3+4,2+4,1+2,1+2+3; Screwdriver
  2+4,3+4,1+3,1+2,1+2+3,2+4,3+4,1+3,1+2,1+2+4; Dragon Sleeper Finish
  2,1,3,1+2+4,1+2+4; Chicken Wing Face Lock 2,1,1+2+3; Muscle Buster
  (chain) 3,1,2,3+4,1+2+3+4 (`ALL` in the guides); Muscle Buster
  (standalone) d,d/b,b+1+2.
- Or-pair: adjacent E019,E01E renders as `1+3 or 2+4`. Proven by the
  EN text itself for Xiaoyu/Miharu Reverse Throw:
  `Back towards enemy f,F,1+3 (or 2+4)`, and by Jin Shoulder Flip
  1+3 (or 2+4). When preceded by a direction, that direction combines
  with both: `f, D/F+1+3 or D/F+2+4` (King Reverse Arm Slam),
  `f, F+1+3 or F+2+4` (Reverse Throw). 175 moves carry an or-pair.
- E022 = 2+3+4 by binary enumeration: it is the only unfilled slot in
  the button enumeration (4-group: 4, 1+4, 2+4, 1+2+4, 3+4, 1+3+4,
  2+3+4, 1+2+3+4), and the other 7 slots in that group are each
  confirmed by an independent published alignment. It appears only in
  8 taunt-named moves (Taunt 2 / Greetings / Welcome / Auger / Taunt).
  Flagged here as enumeration-derived, not directly fandom-confirmed.

## Rendering rules (convert_mvlt_notation.py)

1. A direction glyph immediately followed by a button glyph combines
   with `+` (d/f+2, D/B+1, u/f+1+2). A direction followed by another
   direction, a separator, or end-of-command stands alone (`, `).
   Consequence: a hold-direction + first-button pair like `D/B+3, 3,
   3…` and the simplified `d/b, 3, 3…` describe the same physical
   input (hold d/b, press 3 six times); the converter emits the
   combined form.
2. `N` (neutral) is never a glyph: the game omits it (Jin
   f,N,d,d/f+1 is stored as f,d,d/f,1). `WS` / `FC` / `SS` conditions
   live in the EN condition text, not in glyphs (Twin Lancer
   `While rising 1,2`).
3. `notation` preserves the hold/tap distinction (capitals);
   `notation_std` lowercases hold directions for standard-notation
   matching. For standalone moves the distinction is presentational
   (d/b+1 and D/B+1 are the same press); it is meaningful for
   trailing holds (Burning Knuckle `…, D`; Body Blow to Sway `…, B`).
4. `condition_text` is the EN string with PUA glyphs stripped,
   verbatim (e.g. `While rising`, `Approach enemy`, `(Counter)`,
   `during hit`, `Back towards enemy`). For sample combos the text is
   interleaved per part and is kept as one verbatim string.
5. 240 moves carry a `☆` (U+2606) marker inside their condition text.
   It is preserved verbatim and NOT interpreted here.
6. Duplicate EN names with different inputs are kept as separate
   records (e.g. King has two Bear Hugs: 1+3 and f+1+3; two Mextlis:
   2+4 and f+2+4). Row order is Table A order; `anim_ref` is
   `ttt2:{prefix}:row:{row}` per the moveset schema registry.

## Validation

- Spot checks against published movelists: 34/34 pass (Ogre rows,
  King chains, Jin EWGF family, Armor King, Miharu, Kunimitsu,
  Yoshimitsu, Paul).
- Notation grammar check over all 6,521 non-separator records:
  0 violations. Unknown glyphs: 0.
- Loader proof (all 57 JSONs + index): rows contiguous 0..N−1 per
  file, every `anim_ref` resolves to its own row, index counts match
  file counts.
- Clone/duplicate groups (verified, not merged): Kuma=Panda
  (EN-exact); Bob=Slim Bob (EN-exact, sample combos differ); Law≈
  Forest Law; Xiaoyu≈Miharu; Roger≈Alex; Lee=Violet; Jun≈Unknown
  (Unknown adds dark variants); Lili≈Sebastian (shift pattern);
  Christie≈Eddy (first 157 EN equal, throws diverge);
  Christie≈Eddy≈Tiger (first 52 EN equal).

## Boundary

Supply-only source data. These files do NOT modify any fighter
moveset, step plan, or moveset-library file. Fighter integration is
the Real-Moves lane's step; per its audit
(`docs/movesets/REAL-MOVES-AUDIT-2026-10-29.md`) 0 steps currently wait
on TTT2. `anim_ref` values use the schema-registered
`ttt2:{char}:row:{n}` form so the rows are consumable when wanted.

## Still open (not claimed here)

- data051 pull (watchdog worker, in flight); data001 section 1570 and
  data028 chunk 2383 decode blockers; BXML node-tree decode (pool scan
  gives IDs + counts only — per-item EN names/categories/prices need
  the tree); data004 MOTA parse; per-character model/animation
  containers in the remaining dataNNN files.
