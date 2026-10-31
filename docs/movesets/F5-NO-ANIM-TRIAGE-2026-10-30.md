# F5 No-Anim Remainder Triage — 2026-10-30

WH-100 burn-down continuation, Worker D lane. This document is a triage:
it recounts F5 from current main, records a second-pass re-examination of
the megami/menajerii remainders, records a NOT-APPLIED candidate analysis
for the two class 1-S pools (baek-master-white, pond), names thor's exact
blocker, and gives one line for every other file carrying F5 moves. It
makes NO change to any moveset file: the megami/menajerii second pass
found zero fills that pass the strict B1 method (see §3), and the
baek-master-white/pond files are class 1-S, which this lane does not edit.

Base verified: main HEAD `3f7f1d1430fbd4b59865470857810ed17fc7aca8`
(merge of PR #1314). All counts below were re-parsed from that tree, not
copied from the inventory.

## 1. Recount of F5 from current main

Definition applied, per file, over the `moves` dict of all 163 moveset
files in `game/assets/movesets/`:

- **Strict pool (442):** a move entry with no `anim_ref` AND no `anim_t3`
  AND no `t3_row`.
- **Bare-`t3_row` annex (11):** a move entry with a `t3_row` but no
  `anim_ref` and no `anim_t3` — a row pointer with no anim mapping behind
  it. The WH-100 inventory's headline 453 is exactly 442 + 11 (its own
  arithmetic: 487 at inventory open = 476 with no row at all + 11 bare
  `t3_row`; B1 wired 34, all from the strict pool; 442 + 11 = 453). The
  headline total of **453 is therefore CONFIRMED**, with the definitional
  split made explicit here so nobody has to re-derive it.

### Strict pool — every file (442)

| File | F5 moves | File total | Provenance class |
| --- | ---: | ---: | --- |
| baek-master-white.json | 153 | 291 | 1-S |
| pond.json | 151 | 620 | 1-S |
| thor.json | 78 | 322 | 1-S |
| menajerii.json | 32 | 193 | 1-S (TTT2 named as its fill source) |
| megami.json | 5 | 304 | 1-S (TTT2 named as its fill source) |
| phantom.json | 5 | 1019 | 1-W |
| street-reign.json | 5 | 5 | class 3 stub (owner-gated; no edits) |
| demonio.json | 3 | 764 | 1-W + 3-residue |
| diablo.json | 3 | 661 | 1-W |
| skull.json | 3 | 688 | 1-W |
| burger.json | 2 | 552 | 1-S |
| kinpo.json | 1 | 525 | 1-S |
| scimitar.json | 1 | 362 | 1-S |
| **Total** | **442** | | |

All other 150 moveset files carry zero strict-pool F5 moves. The
concentration in the inventory (baek-master-white 153/291, pond 151/620,
thor 78/322, menajerii 32, megami 5) is confirmed exactly.

### Bare-`t3_row` annex — every file (11)

| File | Bare `t3_row` moves | Entries |
| --- | ---: | --- |
| docfrank.json (1-C) | 5 | `d,d/f,d,d/f+1+2_r276` (r276), `d/b,n,f+2_r271` (r271), `d/f+2_r156` (r156), `f+1_r110` (r110), `n,d,d/b+1+3_r269` (r269) — all T3 gunjack rows named in the entry names |
| vainabel.json (1-S, DOA — Bass Armstrong) | 6 | `2,1` (r153), `2,1,2` (r151), `d,d/f,d,d/f+1+2` (r211), `d/f+2` (r149), `n,d/b,n,f+1+2` (r211), `u/f+4` (r183) — all T3 bryan rows named in the entry names |

442 + 11 = **453**, the inventory headline. These 11 are not part of the
strict pool and no lane should quote either number without saying which
definition it used.

## 2. Provenance basis (read before any fill decision)

From `docs/movesets/MOVESET-PROVENANCE-2026-10-30.md`:

- **baek-master-white** — 1-S. The fighter IS Kevin (CANON.md L961);
  Baek's model is his A2 attire. 153 no-anim moves await a Baek source
  (T5/T6/T7 per the provenance entry).
- **pond** — 1-S. Tekken 7 — Raven (wiring-doc base only), no CANON.md
  entry. 151 no-anim moves; Raven T7 source pending, Steam lane
  preferred when it lands.
- **thor** — 1-S. Tekken — Ganryu (CANON.md L1225, owner words: "Ganryu
  is Thor"). 78 no-anim moves await a Ganryu source. (Thor is NOT a
  DOA/VF file; the DOA/VF family in this tree is the `doa-*.json` data
  files and vainabel — DOA Bass Armstrong — none of which carry
  strict-pool F5 moves.)
- **megami / menajerii** — also classed 1-S in the provenance table, but
  their entries and the provenance summary (L237) name the decoded TTT2
  data now in this repo as their fill source ("TTT2 via the decoded TTT2
  data now in this repo (megami, menajerii)"). Wiring their own
  characters' TTT2 records is therefore the established, sanctioned fill
  for these two files specifically — the precedent is B1, PRs #1306
  (megami) and #1307 (menajerii). This does NOT extend to
  baek-master-white or pond, whose provenance names a different,
  not-yet-landed source generation.
- The 1-S rule (provenance summary): 1-S gaps stay UNMAPPED by name until
  the fighter's own source lands — T7/T8 via the Steam-library extraction
  lane preferred, TTT2 via the decoded layer for megami/menajerii,
  DOA/VF via their own conversion programs.

## 3. Megami (5) + menajerii (32) — second-pass re-examination

Method: the strict B1 method, re-applied from the raw records in
`game/assets/ttt2/movesets/jun.json` (110 records, 101 moves) and
`game/assets/ttt2/movesets/rog.json` (91 records, 84 moves) — notation_std
match (whitespace removed), move name used wherever notation is ambiguous,
condition-prefixed forms checked (IZU/GEN stance prefixes for megami;
RN/ROS/WS/FC/BT prefixes for menajerii), truncated-prefix sequences and
name conflicts are NOT fills. Every one of the 37 remainders was checked
against every move record of its character, including the records B1
already consumed (to catch any condition-prefixed form B1 might have
missed).

**Result: zero fills in both files.** The second pass independently
confirms every B1 disposition; no entry passes the strict method with a
unique record, so no PR was opened for either file and the files are
unchanged. Final F5 remainder is unchanged by this section.

### Megami — 5 remainders, all stay UNMAPPED by name

| Move | Input | Second-pass disposition |
| --- | --- | --- |
| Tsukuyomi | `IZU 1+4` | Name and Izumo condition match TTT2 Jun row 27 exactly, but that record's notation_std is the two-part sequence `1+4, 2+3`; this entry's notation is only the first part (its `input_slots` list `IZU 1+4` / `IZU 2+3` as alternatives, not a sequence). Truncated sequence — NOT a fill. Re-examined specifically for the slot form; the strict method does not join alternatives into a sequence. |
| Rootward Seal | `GEN P (Low)` | Canon-layer name. Genjitsu records in jun.json (rows 51–54) are buttons 1, 2, 3, 4 only; no Genjitsu low-parry (P) record exists. |
| Threshold Grasp | `GEN P (Throw)` | Canon-layer name. No Genjitsu throw-reversal record exists in jun.json. (The T8-layer twin entry `t8.Jun-GEN.P (Throw)` is already wired from the T8 source; that does not create a TTT2 record.) |
| White Door Hold | `IZU 1+3` | Canon-layer name. Izumo records (rows 19–27) are 1, 1,2, 1,4, 2, 3, 4,1, 1+2, 3+4 and the 1+4,2+3 chain; no Izumo 1+3 throw record exists. |
| Threefold Seal | `FC,d/b+1+2` | Canon-layer name. Crouching records in jun.json are rows 71 (3+4,3), 72 (d/f+2) and 101 (d/f, d, d/f+1+2); no crouching d/b+1+2 throw record exists. |

### Menajerii — 32 remainders, all stay UNMAPPED by name

| Move | Input | Second-pass disposition |
| --- | --- | --- |
| Spirit Bear Hug | `hcb,f+1+2` | No half-circle-back throw record in rog.json. The motion-family throw that exists, Giant Swing (row 83), is `f, b, d/b, d, d/f, f+1` — button 1, not 1+2, and a different name. |
| Mauling Grab | `f+1+3` | The only record at f+1+3 is row 74, Head Stomp. Name conflict — NOT a fill. |
| Hunting Grab | `HBS f+1+2` | No HBS (Hunting Bear Stance) exists anywhere in the TTT2 Roger Jr. records. |
| Animal Smash | `FC+1+2` | Name matches row 58, but that record's notation_std is the motion input `f, d, d/f+1+2`, not FC+1+2. Notation mismatch — NOT a fill. |
| Animal Rush | `f+1,2,1` | No f+1 string record exists in rog.json. |
| Animal Hush | `b+1,2,1` | Truncated prefix of the 10 Hit Combo records (rows 71, 72); name matches neither. |
| (BT) | `d+1+2~b` | Transition entry; no standalone d+1+2 record exists in rog.json. |
| Second Storm | `d+1+2,1+2` | Truncated prefix of row 23 (`d+1+2, 1+2, 2`, Animal Roundhouse); notation incomplete and name conflicts. |
| (BT) | `d+1+2,1+2~b` | Transition entry; same row-23 truncation as Second Storm, no matching record. |
| Kangaroo Dasher | `BT d/f+1+2` | Back-turned records are rows 69 (3+4) and 70 (d+3); no BT d/f+1+2 record exists. |
| Elbow Drop | `u/b+2` | Name matches row 47, but that record's notation is `u/f+2` (and it is consumed by the `u/f+2` entry); no u/b+2 record exists. |
| Kick Rushes (Side Roll) | `u/b+3,3>4` | No u/b+3,3 record exists in rog.json (row 46 is u/b+3 alone, Animal Yo-Yo). |
| Rising Foot | `WS+3` | While-rising records are rows 63 (2,2), 64 (3,3), 65 (3,3 hold), 66 (4); a standalone WS 3 would be a truncated prefix of rows 64/65. |
| Power Stomper | `WS+3,3#` | Notation 3,3 while rising is shared by TWO records (row 64 Spring Stomp Kick, row 65 Charge Stomp Kick) and the name matches neither. Ambiguous + name conflict — NOT a fill. |
| Bomb Stomp | `u/b+3+4` | Row 51 is `u/f+3+4` (Kangaroo Stomp, consumed by the u/f+3+4 entry); no u/b+3+4 record exists. |
| Baiame's Spear | `RN 3` | Closest near-miss of the pass. Name matches row 59 exactly, but that record's notation_std is the run input `f, f, f+3`, which this file already carries as its own separate `f,f,f+3` entry; `RN 3` is a different input encoding and the record carries no run condition to map (unlike rows 61/62, whose "Run more than 3 steps" condition B1 mapped to the RN 4,2 / RN 4,4,4 entries). Not filled on name alone. |
| Kick Rushes (Side Roll) | `f+3+4,3>4` | No f+3+4,3 record exists in rog.json (row 13 is f+3+4 alone). |
| Tail Mopping | `FC,d/f+4` | Name matches row 24, but that record's notation is neutral `d+3+4`; the only crouching record is row 67 (d/f+2). Notation/condition mismatch — NOT a fill. |
| Charge-Up | `b+3+4,N` | Stance-hold entry; row 42 is Bobbin Dance (b+3+4 itself, consumed); no b+3+4,N record exists. |
| Twisting Roo, (BT) | `f+4` | No standalone f+4 record exists; f+4 appears only as the head of row 11 (`f+4, 3, 2`). Truncated prefix. |
| Roo Rage | `f+4,3` | Truncated prefix of row 11 (`f+4, 3, 2`, Ayer's Rock); name conflicts. |
| Satellite Dropkick | `RN+3+4` | The running 3+4 record is row 60, notation `f, f, f+3+4`, named Running Exploder (and carried as this file's own `f,f,f+3+4` entry). Notation and name both mismatch the RN encoding. |
| Kick Rushes (Side Roll) | `d/b+4,3>4` | No d/b+4,3,4-form record matches; row 26 is the five-hit Animal Kick Rush (`d/b+4, 3, 4, 3, 4`), a different sequence and name. |
| Ali Kick | `RN 4` | No standalone running-4 record exists; the running records are rows 61 (4,2) and 62 (4,4,4), both consumed by the RN entries B1 wired. |
| Leaping Body Splash | `u~u/b` | No matching record exists in rog.json. |
| Animal Godfist | `ROS D/F,1` | Rocket Stance follow-ups in rog.json (rows 34–41) are f, d/f, 1, 2, 3, 4, 1+2, 3+4 after b+1+2; there is no d/f,1 follow-up record (row 35, Running Start, is the d/f transition itself). |
| Kick Rushes (Side Roll) | `ROS 1+2,3+4,3>4` | No Rocket Stance 1+2,3+4 string record exists in rog.json. |
| Kick Rushes, Roll Back | `u/b+3,1,3>4,3>4,B` | No matching record exists in rog.json. |
| Kick Rushes, Roll Back | `f+3+4,1,3>4,3>4,B` | No matching record exists in rog.json. |
| Kick Rushes, Roll Back | `d/b+4,1,3>4,3>4,B` | No matching record exists in rog.json. |
| Animal Kick, (Side Roll) | `ROS 1+2,3+4,1` | No Rocket Stance 1+2,3+4 string record exists in rog.json. |
| Kick Rushes, Roll Back | `ROS 1+2,3+4,1,3>4,3>4,B` | No matching record exists in rog.json. |

## 4. Baek-master-white (153) + pond (151) — candidate analysis, NOT APPLIED

**These files are class 1-S. Nothing in this section was wired, and
nothing here authorizes wiring.** This is evidence for the owner's source
decision and for a future lane, produced by applying the join method of
`docs/movesets/TTT2-JOIN-BUFFALO-BILL-2026-10-30.md` (notation_std match,
whitespace removed, with each TTT2 record's `condition_text` mapped to
the condition prefixes the WH file itself uses — FLA / F: / L: / R: / B: /
A: for baek-master-white; HAZ / LAB / WS / FC / BT / SS prefix forms for
pond) from the WH side: each no-anim entry is classified by how it would
fare against the TTT2 records of its base character
(`game/assets/ttt2/movesets/bae.json`, Baek Doo San, 95 move records;
`game/assets/ttt2/movesets/rav.json`, Raven, 125 move records).
Classification follows the join doc: **unique** = exactly one record
matches through its condition-appropriate form and no conditioned record
matches only neutrally; **ambiguous** = more than one candidate, or a
record whose condition cannot be proven from the entry's form;
**none** = no candidate record at all. Sample combos and separators are
not joined.

| File | No-anim | Unique | Ambiguous | None |
| --- | ---: | ---: | ---: | ---: |
| baek-master-white (vs bae.json) | 153 | 35 | 1 | 117 |
| pond (vs rav.json) | 151 | 50 | 13 | 88 |

### baek-master-white detail

- Unique (35): `F:1+3`, `F:f+1+3`, `F:2+4`, `F:f+2+4`, `F:d/b+1+3`,
  `F:f+2+3`, `L:1+3`, `L:2+4`, `R:1+3`, `R:2+4`, `B:1+3`, `B:2+4`, `1,1`,
  `3,3,3,4`, `3,3,3,d+4`, `b+1`, `d/f+1,3`, `1+2,4`, `2,2`, `2,3`,
  `b,b+2`, `d+2`, `d/b+2`, `u/f+2`, `WS+2,1`, `f+3,3,2`, `f+3,3,b+2`,
  `f,f+3`, `FLA f+4`, `FLA 3,3,4`, `FLA 3,3,d+4`, `FLA b+3`, `FLA f+3`,
  `FLA u/f+3`, `FLA b+3+4`. (The 13 approach-throw keys resolve because
  bae.json carries the front/left/right/behind throw records as separate
  rows and this file keys them F:/L:/R:/B:.)
- Ambiguous (1): `A:d/f+3+4` — matches BOTH bae row 27 (Heel Hunter,
  neutral `d/f+3+4`) and bae row 93 (Heel Hunter, `d/f+3+4`, "Approach
  mid-air enemy"); the A: key proves the mid-air form exists as an entry
  but the neutral twin entry is the same key family, so the join cannot
  prove which record this entry is without the name/condition evidence a
  future lane must supply.
- None (117): the bulk of the pool — this file's move list is Kevin's
  canon-expanded list (e.g. the Butterfly/Widow string families,
  `3,3,3~f_b` cancels, COBRA BITE) and Baek's TTT2 record set simply has
  no counterpart for most of it. Even if the TTT2 join were authorized,
  it could clear at most 36 of 153 (35 unique + 1 ambiguous); the
  remaining 117 need a Baek source regardless.

### pond detail

- Unique (50): `1,2`, `2,3`, `2,4`, `3,3,4`, `4,1`, `f+3,2`, `f+4`,
  `f,F+2`, `f,F+4`, `d/f+1`, `d/f+2,3`, `d/f+2,4`, `d/f+3`, `d/f+4,4,3`,
  `d+4`, `d/b+2,1`, `d/b+3`, `d/b+4`, `b+1`, `b+2,2,3`, `b+2,2,1+2`,
  `b+3`, `b+4,B+4,3,4,2`, `b+1+2,3`, `b+1+2,2`, `u/f+3`, `u/f+4,4`,
  `u+3,3`, `u+3,4`, `u+3,d+3`, `WS+1`, `WS+2`, `WS+3`, `WS+4`, `1+3`,
  `2+4`, `d/f+1+4`, `d/b+1+2`, `d/b+2`, `u/b+1`, `b+4,B+4,3,3+4`,
  `u/b,b+3+4`, `b+4,B+4,3`, `b+4,4`, `b+4,B+4`, `d/f+4,4`, `u/b+1,2`,
  `b,B+2`, `u+3,d+3,3`, `u/b+1,2,2,2,4,2,3,4,2,1+2`.
- Ambiguous (13): `1` (only conditioned records exist at notation 1 —
  rav rows 11 Haze, 57 BT, 102 WS); `2` (rows 14, 103, conditioned only);
  `3` (rows 15, 104, 109, conditioned only); `4` (rows 16, 105,
  conditioned only); `1+2` (row 9 proven; rows 17 Haze and 63 BT match
  only neutrally); `f+2,3` (row 19 proven; row 66 conditioned);
  `f,F+3` (row 89 proven; row 75 conditioned); `d+3` (row 34 proven;
  row 71 conditioned); `3+4` (row 10 proven; rows 18, 64, 106
  conditioned); `b+3+4` (row 56 proven; row 74 conditioned); `f+3`
  (row 68 conditioned only); `f+1+2` (row 22 proven; row 124
  conditioned); `b+2,4` (row 73 conditioned only).
- None (88): pond's list is a T7/T8-generation Raven/Master Raven list
  (its wired entries carry `t8:raven:` refs and its `t7_source` is the
  Master Raven frame sheet); TTT2's original Raven record set has no
  counterpart for the majority of it. Even if authorized, the TTT2 join
  could clear at most 63 of 151.

### Does the preferred T7 source exist yet? (verification)

The inventory names T7 Steam extraction as the preferred fill source for
both files. Verified state at this HEAD:

- **Baek: no T7 source exists anywhere reachable.** Baek has no file in
  the in-repo T7 frame-data roster (`docs/t7t8-reference/frame-data-t7/`
  — 47 character files, masterraven.json among them, no baek file), no
  T7 moveset file under `game/assets/movesets/t7/`, and no bank in the
  game-reverse-engineering release `t7-rotsm-clips-v1` (2026-10-30;
  banks present: arb, ask, bob, bry, hei, jin, kin, yos + common). The
  provenance entry's own wording ("await a Baek source (T5/T6/T7)") is
  the accurate frame: a Baek anim source has not landed from any
  generation.
- **Raven: partially present, not the finished extraction.** In-repo
  today: T7 frame data (`docs/t7t8-reference/frame-data-t7/masterraven.json`,
  Master Raven, 292 moves — this is pond's declared `t7_source`), T8
  frame data (`docs/t7t8-reference/frame-data-t8-full/raven.json`), a T7
  Master Raven moveset file (`game/assets/movesets/t7/t7-master-raven-lp-rp-lk-rk.json`),
  and pond's own `t7_motbin_clips` provenance pointing at the T7 mot.bin
  decode held in game-reverse-engineering (PR #61, open at pond's wiring
  time). No Raven/Master Raven clip bank (`frv`) is in
  `t7-rotsm-clips-v1`. So frame/move data exists in-repo; the per-move
  anim-clip extraction the inventory calls for has not landed for Raven
  either.
- The T7 Steam extraction lane is real and shipping (the rotsm release
  above is dated today), but neither Baek nor Raven banks are in its
  first clip release. The 1-S hold on both files stands.

## 5. Thor (78) — exact blocker

Thor's source per the provenance doc is **Tekken — Ganryu** (class 1-S;
CANON.md L1225). The 78 no-anim entries are the TTT2-documented Ganryu
moves added to `game/assets/movesets/thor.json` on 2026-10-23 (see
`docs/anim/TTT2-GANRYU-ANIM-GAP-20261023.md`): the move DATA landed; the
MOTION never did. What of the Ganryu source exists in-repo today:

- `game/assets/ttt2/movesets/gan.json` — decoded TTT2 Ganryu MVLT records
  (93 moves): a notation/name layer only, carrying `ttt2:gan:row:{n}`
  refs to records, not playable clips.
- `game/assets/movesets/t7/t7-ganryu-lp-rp-lk-rk.json` — a T7 Ganryu
  frame-data moveset file (data, not anim wiring for thor).
- thor.json's own `t7_motbin` section (wired 2026-10-24) — the T7
  Ganryu mot.bin decode (ganmot.bin; 2,265 internal moves, bank counts
  0x8000: 1575 / 0x4000: 508 / 0x0000: 182) recorded as a section, with
  the explicit note that motbin internal moves are **NOT joined to
  playable input keys** and no display walk was performed; a future
  input-key join must be walk-verified from the cancel tables.
- thor's bound anim bank is still the Bryan T3 proxy (`t3_source:
  bryan`); Ganryu has no T3 divmot stream in the extracted banks, so T3
  can never fill this gap (gap doc, owner source priority 2026-10-23:
  TTT2/T6 FIRST, T3 LAST).

**Blocker, named exactly:** there is no decoded Ganryu FIGHT motion bank
in-repo — the target `game/assets/anim/t6/ganryu/` bank (registered as
`ganryu` in `SOURCE_TO_BANK` / `T3_BANKS`) does not exist. The TTT2
route is blocked upstream on extraction of the TTT2 Xbox 360 STFS
game-data chunks (~8.86GB not extracted; disk, safe storage, STFS
decrypt tooling, console motion-format RE — owned by the extraction
coordinator lane per the gap doc). The T7 route is blocked on the
walk-verified motbin input-key join that thor's own `t7_motbin` section
says has not been performed. Thor is 1-S, so this lane wires nothing
into it from the TTT2 record layer on its own authority.

## 6. All other files with F5 counts — one line each

Strict pool:

- **phantom.json — 5** (1-W, Yoshimitsu): entries `1`, `2`, `4`,
  `1_r62`, `u+1,1~t3.yoshimitsu.2` — their names cite T3 yoshimitsu rows
  (r62/r307/r243) but the entries carry no row field; fill source per
  provenance is the Yoshimitsu T7 source (127 UNMAPPED already await it).
- **street-reign.json — 5** (class 3 stub, OWNER-GATED — no edits):
  all 5 of its moves (`1`, `2`, `3`, `4`, `1+3`) have no mapping; it has
  no canon base anywhere and is named on the Decision List for a base
  assignment; nothing to fill from until then.
- **demonio.json — 3** (1-W + 3-residue, Jin): entries `1`, `1_r41`,
  `u+1,1~t3.jin.2` name T3 jin r41 without a row field; fill source is
  the Jin T7 source (80 UNMAPPED await it). (demonio itself is not on
  the owner-gated list; demonio-winged is, and is untouched.)
- **diablo.json — 3** (1-W, Heihachi): entries `1`, `1_r46`,
  `u+1,1~t3.heihachi.2` name T3 heihachi r46 without a row field; fill
  source is the Heihachi T7 source (80 UNMAPPED await it).
- **skull.json — 3** (1-W, Bryan): entries `3`, `3_c36`, `u+1,3` name
  T3 bryan r63 / c36 without a row field; fill source is the Bryan T7
  source (114 UNMAPPED await it); corrections otherwise use the Bryan
  graph.
- **burger.json — 2** (1-S, Bob): entries `3`, `b_c36_r65` name T3
  bryan r65 without a row field; 1-S — stays UNMAPPED until the Bob T7
  source lands (111 UNMAPPED already await it).
- **kinpo.json — 1** (1-S, Asuka): entry `1` names T3 jin r35 without a
  row field; 1-S — stays UNMAPPED until the Asuka T7 source lands (103
  UNMAPPED already await it; Steam lane preferred).
- **scimitar.json — 1** (1-S, Shaheen): entry `1` names T3 jin r184
  without a row field; 1-S — stays UNMAPPED until the Shaheen T7 source
  lands (57 UNMAPPED already await it).

Bare-`t3_row` annex:

- **docfrank.json — 5** (1-C, Dr. Bosconovitch): the entries carry a
  gunjack `t3_row` pointer only; provenance notes "5 no-anim moves" for
  this file; fill would come from its own T3 Bosconovitch/gunjack bank
  work, not from this lane.
- **vainabel.json — 6** (1-S, DOA — Bass Armstrong): the entries carry
  a bryan `t3_row` pointer only — a stand-in bank, not Bass data; per
  its canon page he needs ALL of Bass Armstrong's moves/motions/
  animations, and DOA anim extraction is pending (the DOA/VF conversion
  program is this file's fill source).

## 7. What unblocks each pool

- **baek-master-white (153):** a Baek anim source landing — per the
  inventory, the T7 Steam extraction lane is the preferred route, but
  no Baek extraction exists yet from any generation (T5/T6/T7 per the
  provenance entry); the TTT2 candidate analysis above (35 unique /
  1 ambiguous / 117 none, NOT applied) is the evidence base if the owner
  ever chooses to settle this file's source generation differently.
  Until then: 1-S hold, no edits.
- **pond (151):** the Raven T7 Steam extraction completing — frame/move
  data is already in-repo (Master Raven T7 sheet, T8 sheet, T7 moveset
  file, mot.bin decode in game-reverse-engineering); the missing piece
  is the per-move anim-clip extraction/join for Raven. TTT2 candidate
  analysis (50 unique / 13 ambiguous / 88 none, NOT applied) is on
  record above. Until then: 1-S hold, no edits.
- **thor (78):** the Ganryu motion program — either the TTT2/T6
  extraction coordinator's lane landing the Ganryu FIGHT bank from the
  STFS game-data chunks, or the walk-verified T7 motbin input-key join
  against the ganmot cancel tables already decoded in thor's
  `t7_motbin` section. No other source can fill it (no T3 Ganryu bank
  exists).
- **megami (5) + menajerii (32):** nothing needed beyond the strict
  method — it has now been applied twice (B1, PRs #1306/#1307, and this
  second pass) with the same result. The 37 remainders are canon-layer
  moves, transitions, truncated sequences, and name/notation conflicts
  that their own TTT2 records do not contain; they stay UNMAPPED by name
  unless a future source (e.g. a T6 layer or the fighters' T8 data,
  which megami's file already draws on for other entries) supplies a
  record that passes the strict method.
- **Scattered remainders (24 strict + 11 annex):** each file's own
  named source above — the T7 sources for the 1-W/1-S Tekken files
  (Yoshimitsu, Jin, Heihachi, Bryan, Bob, Asuka, Shaheen), the DOA
  conversion/extraction program for vainabel, the owner's base
  assignment for street-reign, and docfrank's own T3 bank work.

**Final F5 state after this lane: 453 (442 strict + 11 bare-`t3_row`),
unchanged** — zero fills passed the strict method on the second pass,
and the two big pools are 1-S analysis-only by provenance. No
play-verification is claimed for anything in this document; it is a data
triage only.
