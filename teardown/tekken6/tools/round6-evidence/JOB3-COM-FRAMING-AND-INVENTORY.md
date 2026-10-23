# Tekken 6 PSP — ROUND 6 JOB 3: COM inner framing + per-character inventory (G4)

Date: 2026-10-21, round 6 attempt 4. Inputs: the 18 adler-exact COM
plaintexts (gzip idx58–75, entries 709–735) in the retained workdir
`_t6r4-work/decoded76/`. Machine-readable evidence:
`round6-evidence/r6_com_inventory.json` (per-file offsets, hashes,
magics, sample strings).

## HEADLINE: the COM files are MOVESET / command data — not models

Every COM plaintext carries, in plain bytes, its character's name,
an author name, build dates (`2009/08/26`, `Sun Nov 01 21:5x JST
2009`), and hundreds of move names (`Machine Gun Arrow`, `Palm
Strike to Head Jammer`, `Left Right Combo`, `Sample Combo 4/5`, …).
There is **no mesh and no texture data in any COM file** (magic scan
below). Rounds 2–4's "COM = character model container, ~40 meshes"
framing is retired: COM holds per-character movesets with MOTA
animation references at the tail.

## Framing (byte-proven, uniform across all 18 files)

| Element | Evidence |
|---|---|
| COM header, 16 bytes | `00 00 00 01` (BE u32 version 1) + `"COM\0"` + u32 0 + **LE u32 count word at +12** (values 7–16, sum = 176) — 18/18 files |
| Fixed 624-byte header region | The character name string (`[NAME]1`) sits at **offset 624 in 18/18 files**; everything before it is header/tables |
| Pointer table at offset 368 | 32 slots × 8 bytes `(u32, u32 offset)`, offsets monotonic non-decreasing into the file body, terminated by `(0,0)` in slot 32 — 18/18 files (31 live slots each) |
| String / move-name region | Starts at 624: `[NAME]1`, author, dates, then move-name records (254–1,028 strings ≥5 chars per file) |
| MOTA tail | **6 `MOTA` magics per file (108 total)**, uniform layout 18/18: two substantive chunks (~2.4 KB apart; first chunk header `MOTA`, v1, `0x14` …) near the end of the body, then **four 20-byte MOTA records spaced exactly 20 bytes, the last ending exactly at EOF** |

### The count word (176) — honest status

The +12 word sums to 176, but no table of that length exists in the
header: the only monotonic offset table is the fixed 32-slot table
at 368 (searched offsets 0–624, entry strides 8, all 18 files), and
6 MOTA magics / 31 live pointer slots are likewise fixed counts.
So the word is a real per-file count (7–16) of something inside the
body (it correlates with nothing fixed in the header), but **its
exact referent is NOT proven** — this doc does not repeat round 5's
"176 inner assets" as a measured asset census. What IS measured:
18 moveset bodies + 36 substantive MOTA chunks + 72 twenty-byte
MOTA tail records. Pinning the count word's referent is a named
remaining blocker (needs EBOOT-side COM-loader RE or a body-record
census that reproduces 7–16 per file).

## Classification of COM contents (byte evidence per class)

| Class | Count | Evidence |
|---|---|---|
| Mesh | **0** | `GMO\0` = 0, `NDPP` = 0 in all 18 files |
| Texture | **0** | `TIM2` = 0, `GIM\0` = 0 in all 18 files |
| Animation (MOTA) | **108 magics: 36 substantive chunks + 72 tail records** | Offsets in `r6_com_inventory.json`; uniform 2 + 4×20B pattern, last record ends at EOF in 18/18 |
| Other — moveset/command data | **18 files (whole bodies)** | Move-name strings, author/date strings, pointer table, u16 command streams in the header region (repeating ~140-byte u16 blocks) and body records |

## Per-character inventory — HIGH confidence, direct byte evidence

Assignment evidence per file is the character's OWN name string at
offset 624 of its own plaintext — no roster-order guessing.
Corroboration: distinct author strings + distinct Nov 1 2009 build
timestamps (minutes apart, sequential) + character-specific move
names in each body.

| idx | entry | Character (in-file string) | Count word | Size | Sample move names |
|---|---|---|---|---|---|
| 58 | 709 | LAW | 7 | 538,604 | Machine Gun Arrow, Left Right Combo |
| 59 | 711 | KING | 8 | 703,400 | Palm Attack, Palm Strike to Head Jammer |
| 60 | 712 | NINA | 8 | 552,136 | Biting Snake, Left Right to Spider Knee |
| 61 | 714 | Lin_Xiaoyu | 14 | 549,944 | Bayonet, Bayonet Thruster |
| 62 | 715 | JIN | 7 | 499,500 | Left Right Axe Kick |
| 63 | 717 | Kuma | 8 | 473,680 | Left Right Bear Claw, Jab Elbow Smash |
| 64 | 718 | HEIHACHI | 12 | 475,520 | Flash Punch Combo |
| 65 | 720 | LEE | 7 | 502,800 | Left Right Combo to Revolution Zwei |
| 66 | 721 | MARDUK | 10 | 536,212 | Left Right to Gut Check |
| 67 | 723 | ROGER | 9 | 450,636 | Left Right Body Blow |
| 68 | 724 | Wang | 8 | 462,668 | Long Zhu Lian Pao |
| 69 | 726 | Asuka | 9 | 458,848 | Whiplash, Jab Uppercut |
| 70 | 727 | BAEK_DOO_SAN | 16 | 484,604 | Double Jab, One Two Combo |
| 71 | 729 | RAVEN | 9 | 529,268 | Right Straight to Left Low Kick |
| 72 | 730 | ARMOR_KING | 14 | 542,280 | One Two Punch, Jab Uppercut |
| 73 | 732 | Dragunov | 12 | 494,876 | Eye Gouge to Hilt, Hammer and Sickle |
| 74 | 733 | EDDY | 8 | 607,144 | One Two Elbows, Combo Jilar |
| 75 | 735 | ZAFINA | 10 | 477,708 | Left Right Scarecrow, Ecdysis |

Confidence: **HIGH for all 18** (name + author + timestamp + move
vocabulary all inside the file itself). Note these are 18 of the
roster — the remaining characters' movesets are not in the DATA401
top-76 set; they presumably live in the embedded-container space
(JOB 1 found 5,470 adler-exact embedded containers in the entry-87
slice alone, whose decoded heads match the small-record classes).
Per-character isolation is preserved: each COM file is one
character's moveset only; no cross-file mixing was done or needed.
