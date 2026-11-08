# Devil Within decode log — 2026-11-08

Task: decode Tekken 5's Devil Within mode (Jay's order, 2026-11-07 ~19:33:
"the decoding is supposed to be done for the devil within mode, you have
to do that"). Steps were: (1) advance the romD file-table mapping until
Devil Within files resolve to real offsets/sizes; (2) extract and decode
what is decodable; (3) land decoded data + this log in `teardown/tekken5/`
on a branch; (4) if blocked, state exactly what is missing and where it
should come from — no ISO/ROM download from the internet.

## What got decoded

### 1. Index-level decode of all 242 Devil Within files — DONE

`dw-motion-index.json` — every Devil Within file named in the romD
manifest (`t5_motion_manifest.txt`, 498 names), with a romaji gloss and a
confidence per file. Verified mechanically: all 242 names exist in the
manifest, 0 duplicates, counts per group re-checked by grep.

| Group | Files | Assignment (confidence) |
|---|---|---|
| `gym_ikdv_*` | 52 | Devil Jin's DW brawler kit — beams, punches, kicks, throws, turns, breakfalls (high) |
| `gym_kmb1_*` | 39 | Modified Gun Jack, stage 1 boss — machinegun, shotgun, charge shots (high) |
| `gym_kob2_*` | 29 | True Ogre, stage 3 boss — fly, fire, horn, tail, snake (medium, INFERENCE) |
| `gym_ozb3_*` | 36 | Monstrous Ogre, stage 5 boss — whirlwind `tatumaki`, stomp `fumi`, burn (medium, INFERENCE) |
| `gym_ozt4/ozhe/oznj` | 6 | Ogre-family extras, boss unassigned (low) |
| `gym_ikt5_*` | 26 | UNRESOLVED gun/fly kit, base + `_mon` monster variants (low) |
| `gym_init_obj_*` | 21 | Boss init 1/2/3/5 (boss4 ABSENT), Jin, devil, monster archetypes power/speed/standard/tricky, 3 test characters (high) |
| `gym_djin_newhane00-03` | 4 | Devil Jin transform — wings/feathers (high) |
| `gym_dw_*` singles | 7 | Face (`dwfkao`), wave (`dwhadoh`), power-up (`dwup`, `dwup_hei`), 3 opaque (medium) |
| `moj_stg00/01/02/04` | 4 | Stage text/messages, NOT geometry; `moj_stg03` absent (high) |
| `snd_*` | 18 | Lab / Egyptian / blue themes; Lei/Jin/Heihachi/JACK/Devil Jin voices (high) |

Confidence spread: 155 high, 56 medium, 31 opaque (tokens not translated:
`dsrp`, `sjk`, `PSrlpf00`, `ttlp`, `hkrp`, `nog`, `rari`, `cyop`,
`soten`, `ap`, `jz`, `nara`, `dv2kam2`). Inferences are labelled as
inferences with their evidence in the JSON; nothing guessed is presented
as fact.

Code anchors proved by `snd_cXX` filenames (not guessed): c02 = Lei,
c10 = Jin, c15 = Heihachi, c21 = JACK, c30 = Devil Jin.

### 2. romD format documented — DONE, table layout UNVALIDATED

`ROMD-FORMAT.md` — everything known about the romD archive and the
related LUT tables, with sources:

- Repo survey (2026-10-23): magic `romD` at 0, CRLF manifest (498
  names), 21 `BDPK` markers, file-table mapping never reversed.
- Community tools `smb123w64gb/Tekken5_Tools` (public, commit
  `a1df701812e6b263a773f23e725a2a03d7cc27f5`), read as text:
  - PS2 LUT (indexes TK5DATA1.BIN, table in the NLZ1-decompressed
    `files[5]` overlay from the TK5DATA3.BIN PKG): `TABLESTART
    0x0027B5B0`, `CHECKSTART 0x0027E838`, `TABLECOUNT 1571`; entries
    8 bytes (offset u32 × 0x800, size u32); separate u32 checksum array.
  - Generic LUT: Retail NTSC `0x002F82B4` / 5004 (commented out), Beta
    `0x26F63C` / 3030 (active); entries **40 bytes** (10 x u32:
    offset, size, crc[5], unk0, id, unk1); `size == 0xFFFFFFFF` =
    empty slot; output `%04i_%04x.bin`.
  - Sector cipher `tk5psp_crypt.py` (read in full, 60 lines): LCG
    keystream, `key = key*5+3` mod 2^32, 512 u32 words, XOR in
    2048-byte blocks, seed = entry id.
  - Headers inside extracted data (TekkenMods tutorial): `NUDP`
    model container, `TIM2` texture, `MIF` bone data. Caution: the
    tutorial's "only Devil Within data is extractable" claim is about
    arcade 5.1 BINs, not PS2 retail romD.
- Neither documented LUT is proven to be the romD table (counts 1571 /
  5004 / 3030 vs the manifest's 498). Working hypothesis (UNPROVEN):
  romD follows the same Namco LUT pattern with the manifest order
  matching table order.

### 3. romD reader/extractor built and self-tested — DONE (mechanical)

`tools/romd_extract.py` (stdlib only): manifest parser, both LUT
parsers, the sector-cipher port, a romD scanner (magic / manifest region
/ BDPK markers / candidate-LUT hunt with structural validation), and an
extractor that writes files by manifest name order with per-entry
decryption. `--selftest` builds a synthetic romD in memory and verifies
scan → parse → decrypt → extract round-trips: **PASS** (run 2026-11-08).
The tool is proven mechanically only — it has never run against real
romD bytes, and it refuses to extract on an unconfirmed table.

### 4. Corrections to earlier records — DONE

- **No plain `stg*.dat` stage files exist in the romD manifest.**
  An earlier draft (and `DEVIL-WITHIN-DATA.md` §2) said
  `stg00/01/02/04.dat` exist. They do not — only `moj_stg00/01/02/04`
  (stage text). Fixed in `DEVIL-WITHIN-DATA.md` and in the spec §5b.
  Stage geometry lives in TK5DATA0/1/3, not romD.
- `ikdv` is 52 files including `jump_k` / `jump_p`, which an earlier
  enumeration missed.
- The manifest is 498 single-spaced lines, not 996.
- The generic LUT entry is **40 bytes**, not 36 — caught by the
  extractor's self-test, verified by re-reading `FileTableGet.py`
  `LUT.read` (1+1+5+1+1+1 u32).
- `DEVIL-WITHIN-DATA.md` §1 file names corrected to manifest
  spellings (`gym_dwfkao00.dat`, `gym_dwhadoh00.dat`,
  `gym_dwup00.dat`, `gym_dwup_hei.dat`).

### 5. What was checked and found absent — DONE

- `game/data/moveset-library/banks/`: `doa.json`, `t3.json` (4,648
  moves, keyed by fighter name — no T5 codes), `vf.json`, `vf5.json`,
  `wmxix.json`, `wrestling.json`. **No T5 bank, no T5 motion bytes.**
- Repo clone (`teardown/tekken5`, `game/data/moveset-library/banks`,
  `docs/modes`, `tools/re`): zero `*.dat`, `*.BIN`, `*.bin` files.
- Home top level + `/tmp`: no ISO / BIN / TK5DATA files. (A full
  `~/workspace` + `/tmp` find was started; its result had not been
  delivered when this log was written — targeted checks found nothing.)

## What got decoded with real bytes — 2026-11-08 (archive pull)

Jay authorized the pull 2026-11-07 ~20:15 ("Get it from the archive
item"). Source: Internet Archive item `slus-210.59.-tekken-5` ONLY.

### 1. Disc bytes fetched by range — quota-forced, hash caveat

The full 4.04 GB ISO could NOT be downloaded here: the VM's disk quota
caps new writes well below `df` free space (measured ceilings ~512 MB,
then ~1.5 GB after deleting a partial ISO). So each BIN was fetched by
HTTP Range from the ISO's own byte offsets (ISO directory read from the
real ISO header, bytes [0, 2 MB)). **The full-ISO md5/sha1 could NOT be
verified** — the full ISO was never on disk. Each BIN was verified by
exact ISO-directory size + internal structure (romD magic, PKG parse,
ELF headers). That is a deviation from the task's "verify md5/sha1
BEFORE using them" step, forced by the quota; stated here plainly.

| File | Bytes fetched | Size vs ISO directory | Verified by |
|---|---|---|---|
| `TK5DATA2.BIN` | 244,426,640 | exact | `romD` magic @0 + 99-container structure |
| `TK5DATA3.BIN` | 422,901,760 | exact | PKG parse (10 files) + NLZ1 Code blob |
| `SLUS_210.59` | 689,304 | exact | ELF header, 1,376 strings |
| `SYSTEM.CNF` | 57 | exact | — |
| `IOPRP300.IMG` | 278,305 | exact | — |
| `IRXARC.BIN` | 305,024 | exact | — |
| `TK5DATA4.BIN` | 179,368 | exact | ELF header |
| `TK5DATA0.BIN` | — NOT fetched | 2,072,586,240 | blocked on quota |
| `TK5DATA1.BIN` | — NOT fetched | 1,297,731,584 | blocked on quota |

Raw bytes live ONLY on disk under `~/workspace/devil-within-decode/raw/`
— never in git. `TK5DATA3.BIN` was deleted 2026-11-08 ~04:00 to free
quota headroom for the decode work (SHA-256 recorded in the log below;
its Code blob is saved as `TK5DATA3_code.bin`; PKG `files[7]` mask.bin
+ `files[9]` table were NOT extracted — re-fetchable from the same
archive item, TK5DATA3 extent 1646501). The partial ISO (1.1 GB) was
deleted 2026-11-08 ~02:40 for the same reason; re-fetchable.

### 2. romD archive format CRACKED — BDPK containers + BD directory

The romD file-table mapping is SOLVED (not a LUT — a container
directory). Measured from the real bytes; see `ROMD-FORMAT.md` for the
full layout and `tools/romd_extract_full.py` for the extractor.

- **99 `BDPK` containers** (not 21 as the 2026-10-23 survey said).
  Container = `BDPK` + u32 A (entry count) + u32 B (payload size) +
  payload. Total BDPK payload 167,172,864 bytes.
- Payload = [116-byte prefix: a fixed bone/skeleton block, first 32
  bytes identical across containers] + [A × 128-byte BD directory
  records] + [file data in directory order] + [12-byte trailer].
- **BD record (128 bytes):** `BD` + u16 type + u32 X + u32 Y +
  8 bytes + filename (WITHOUT `.dat`) + NUL + zero pad. **Y = file
  size in bytes.** Validated on every container: entry count == A,
  and the Y values sum to (data region − 12) exactly.
- Type codes measured: 0 = `gym_` motion, 1 = `obj_` object, 2 =
  `nut_`, 3 = (1 file, unassigned), 4 = `snd_` sound, 5 = `cap_`
  font, 8 = `moj_` stage. X is an unassigned per-file value (clusters
  by character group — e.g. amt3 motions X≈12123–12176 — possibly a
  motion/group ID; UNRESOLVED).
- The 116-byte prefix is NOT a file; the 12-byte trailer is NOT a
  file. Some containers have empty directory slots (all zeros, or
  zeros + a stray float −1.857) — those hold no file.
- **No romD table exists in TK5DATA3 / the Code blob / SLUS.**
  Searched and found absent: no `romD`, no `TK5DATA2`, no `.dat`,
  no `gym_` names in the Code blob, SLUS, or TK5DATA4. The romD
  index lives ONLY in the BDPK containers themselves.
- The archive also holds 97 name-list blocks (stage-pack load lists,
  5,780 name lines, 1,143 unique names — NOT an archive manifest),
  a text file at offset 16 (`snd_c02lei.dat`, Lei's sound-position
  file, 6,944 bytes, extracted directly), and a ~74 MB tail of
  motion data (MovO/RotO records) + compressed blobs + textures.

### 3. Extraction — 1,022 files, 236/242 Devil Within files

`tools/romd_extract_full.py` (grid reader: BD records at
payload+116+i×128). **1,022 unique files, 108,866,592 bytes**
extracted to `raw/romd_out/` (disk only). Per-container validation:
entry count == A and Y-sum == data region − 12 on every container
extracted; 3 containers are empty/false hits (no file data) and 2
hold only zero slots — nothing lost there.

**Devil Within: 236/242 files extracted.** The 6 missing have NO
file data in TK5DATA2 — they appear only as names in load lists
(referenced, never stored as BD entries):

| Missing file | Where its name appears |
|---|---|
| `gym_ozhe_1ckj66a.dat` | load list @0x7cfd934 |
| `gym_ikt5_katgym_Bbr_bbblow.dat` | load list @0xa1e2cf4 |
| `gym_ikt5_katgym_Gan_mekin.dat` | load list @0xa1e2844 |
| `gym_init_obj_testchr1.dat` | load list @0xa1e0e0b |
| `gym_init_obj_testchr2.dat` | load list @0xa1e103b |
| `gym_init_obj_testchr3.dat` | load list @0xa1e120b |

They may live in TK5DATA0/1 (not fetched) or be absent from this
disc image. The index listed them from references; the bytes say
they are not in this archive. Two non-DW files (`asb_staffroll.dat`,
`ast_staffroll.dat`) exist in two containers with DIFFERENT bytes —
first copy kept, difference logged in `romd_extract_report.json`.

### 4. Gym motion format — header decoded, frame counts measured

`tools/dw_analyze_dat.py` + per-file measurements in
`dw_measurements.json`. The `gym_*.dat` motion header (32 bytes,
little-endian u16):

| Field | Meaning (measured) |
|---|---|
| [1] | bone count: 35 (fighter motions), 78/111/96 (`init_obj` monsters), 12 (`djin` transform), 4 (7 special kob2/ozb3 files) |
| [2] | frame count |
| [3] | 276 (motions); = bones×10 (`init_obj`); 108 (`djin`) — section offset, use UNRESOLVED |
| [5] | 16528 (0x4090) constant; u32 @8 = 0x40900000 = 4.5f |
| [7] | 8192 (0x2000) constant |
| [10] | = bone count × 128 |
| [12] | = frames × bones × 12 for standard motions (420 values/frame at 35 bones); SPARSE subtype below |
| [14] | 68 (motions) / 180 (`init_obj`) / 15 (`djin`) — UNRESOLVED |
| [64:68] | magic `GYM1` (at offset 0x40 in every gym file) |

So each bone carries **12 values per frame**. The keyframe stream
after the header is a variable-length record encoding (records
separated by `ff ff`, values incrementing like bone/channel indices)
— the bit-exact keyframe decode is NOT finished; it needs the record
packing reversed. What IS measured and usable now: bone counts,
frame counts, and durations for every clip.

Motion totals (at 60 fps):

| Group | Clips | Frames | Seconds |
|---|---|---|---|
| ikdv (Devil Jin) | 52 | 3,488 | 58.1 |
| kmb1 (Gun Jack) | 39 | 3,186 | 53.1 |
| kob2 (True Ogre) | 29 | 3,245 | 54.1 |
| ozb3 (Monstrous Ogre) | 36 | 4,165 | 69.4 |
| oz_extra | 5 | 352 | 5.9 |
| ikt5 | 24 | 1,644 | 27.4 |
| init_obj (1-frame poses) | 18 | 18 | 0.3 |
| djin (transform) | 4 | 52 | 0.9 |
| dw_singles | 7 | 353 | 5.9 |
| **Total motion** | **214** | **17,553** | **~292 s (~4.9 min)** |

**Sparse subtype (14 clips):** field12 ≠ frames×bones×12, with far
fewer values per frame (11–135 vs 420) — these store only changed
channels (sparse keyframes), not per-frame data. They are the long /
special motions: `ozb3_dead` (500 frames, 26 values/frame),
`ozb3_toujyou` (460 frames, entrance), `kob2_escape` (321 frames,
11 values/frame), `kmb1_machinegun` / `jumpmachinegun` /
`bakutyushot` / `hijump_shot` (projectile attacks), `kob2_ap` /
`warp2fire`, `ozb3_burn` / `houmingf`, `kmb1_tojo`,
`ikdv_b_nage_f/y` (throws). A retarget must handle the sparse
subtype separately from the per-frame subtype.

### 5. Stage map objects — CORRECTION: moj_stg is geometry, not text

The earlier log (§1, §4) called `moj_stg*` "stage text/messages".
**Wrong.** `moj_stg00/01/02/04.dat` are stage MAP OBJECT files
(`.moj`): each starts with the dev build path
`C:\temp\mapobj\stgNN.moj`, then effect-archive references
(`stgNN_effnud.arc`, `stgNN_effmif.arc`, `stgNN.efp`,
`stgNN_effnut.arc`), then NUDP model containers + TIM2 textures +
MIF bone data. Measured:

| Stage file | Bytes | NUDP models | TIM2 textures | MIF bones |
|---|---|---|---|---|
| moj_stg00 | 1,916,672 | 29 | 29 | 56 |
| moj_stg01 | 872,320 | 18 | 18 | 18 |
| moj_stg02 | 1,392,384 | 20 | 20 | 22 |
| moj_stg04 | 200,192 | 3 | 3 | 3 |

`moj_stg03` does NOT exist anywhere in the archive (no name, no
entry) — stage 3 has no DW stage file, consistent with the
rename-map note. The NUDP/MIF contents (actual stage geometry,
positions, collision) are NOT yet parsed — that needs the NUDP
model + MIF bone formats reversed (ImHex patterns owed). The 40
symbol locations are NOT in these files as readable text.

### 6. Sounds — P3Dp container

17 of 18 `snd_*` files start with magic `P3Dp` (u32 0x70443350);
`snd_c02lei.dat` is the plain-text sound-position file from §2.
P3Dp header (16 bytes): magic, then u16 fields (0x0A01,
a count 8–20, a second count 8–12, sizes). Entropy ~6.5
(compressed/encoded audio). `snd_c_tks.dat` is near-empty
(entropy 0.41). Audio decode (VAG/ADPCM inside P3Dp) is NOT done.

### 7. TK5DATA3 PKG + Code blob — PS2 LUT VALIDATED

PKG parse of TK5DATA3.BIN: **10 files.** files[0–4] are ELFs,
files[5] is the NLZ1 Code blob (1,279,250 compressed →
2,719,159 bytes decompressed, saved as `TK5DATA3_code.bin`),
files[6] MIPS code-like (2,089,943 B), files[7] starts with
`mask.bin` ASCII (298,375,168 B), files[8] (4,152,832 B) and
files[9] (106,386,560 B) table-like. The PS2 LUT in the Code blob
is REAL and VALID: TABLESTART 0x0027B5B0, CHECKSTART 0x0027E838,
TABLECOUNT 1571; 1,355 plausible entries; total bytes covered
1,296,543,666 of TK5DATA1's 1,297,731,584 (99.9%); entries tile
sequentially. That LUT indexes TK5DATA1 (not fetched), so no
TK5DATA1 files were extracted.

Code-blob string scan for Devil Within numbers: `item_force`
(a menu/config item, `tcb_confitem_force_t`) and
`handycap_gauge_yellow_p1/p2` (handicap gauge UI) exist;
`Devil Jin` / `name_DEVILJIN` / `RankingMode` exist. **Zero hits
for `symbol`, `laser`, `drain`, `heal`.** The `Gem` hit is binary
garbage, not a string. So the Devil Gauge fill rates, laser
damage, health-drain rate, gem heal/drop values, Force values,
rank thresholds, and symbol locations are NOT in the Code blob
as readable data — they live in TK5DATA0/1 tables or as MIPS
immediates (needs disassembly). See "still blocked".

## What is still blocked — the exact blocker (revised 2026-11-08)

**Bytes now exist for TK5DATA2 (romD) and TK5DATA3 (code). The
romD decode above is DONE. What remains blocked:**

| Item | Blocker (exact) |
|---|---|
| `TK5DATA0.BIN` (2.07 GB) + `TK5DATA1.BIN` (1.30 GB) | Disk quota: VM caps new writes (~1.5 GB ceiling measured); cannot download 2.07 GB / 1.30 GB here. Workaround not yet run: stream-scan in discardable chunks, or range-fetch specific PS2-LUT entries (LUT validated, entries are huge unnamed blobs — content ID needs sampling). |
| Devil Gauge fill rates, laser damage, health-drain rate | Not in TK5DATA2 `.dat` files or the Code blob as readable data. Needs TK5DATA0/1 tables or MIPS disassembly of the Code blob (capstone NOT installed). |
| Gem heal/drop values, Force values | Same as above. `item_force` is only a menu/config name. |
| Rank thresholds (time/damage/retries/Force) | Same as above. `RankingMode` strings are arcade ranking UI, not DW rank thresholds. |
| 40 symbol locations | Not in `moj_stg*` as text; needs NUDP/MIF stage-geometry parse (TK5DATA2) or TK5DATA0. |
| Boss/enemy AI tables | `init_obj` files are 1-frame bone poses, not AI tables. AI lives in TK5DATA0/1 or code. |
| Full keyframe stream decode (gym) | Record packing after the `GYM1` header not yet reversed (variable-length records, `ff ff` separators). Header + frame/bone counts are measured; per-joint curves are not. |
| Stage geometry parse (NUDP/MIF) | NUDP model + MIF bone formats not yet reversed (ImHex patterns `NUDP.hexpat` / `BoneFIle.hexpat` owed). Counts measured only. |
| Sound decode (P3Dp) | Container header measured; audio payload (VAG/ADPCM) not decoded. |
| 6 DW files (ozhe_1ckj66a, katgym ×2, testchr ×3) | No data in TK5DATA2 (list references only). May be in TK5DATA0/1 or absent from this disc image. |

## What this means for HeartMind (revised)

- Bucket B moves from "0 bytes, 242 files inventoried" to **236/242
  files extracted + measured** (motion header/frames/bones, stage
  map-object inventories, sound container). The `HM_TEARDOWN` seam
  still waits on the keyframe-stream decode before DW motions can
  be retargeted into playable banks — header/frame data alone does
  not animate a model.
- Devil Jin's kit (52 clips, 58.1 s), Gun Jack (39, 53.1 s), True
  Ogre (29, 54.1 s), Monstrous Ogre (36, 69.4 s), ikt5 (24, 27.4 s)
  are inventoried WITH frame counts and bone counts — the clip
  list a retarget lane can work from. The 14 sparse-subtype clips
  are flagged for separate handling.
- Stage files are map objects (geometry), not text — the stage
  lane needs the NUDP/MIF parse, not a text read.
- Meter/gem/Force/rank/symbol numbers remain UNMEASURED — they are
  in TK5DATA0/1 (quota-blocked) or in MIPS code, not in the romD
  files. Do NOT present any number for them until those bytes are
  read.

## What is still blocked — the exact blocker (superseded)

Superseded by the revised sections above ("What got decoded with
real bytes — 2026-11-08" and "What is still blocked — the exact
blocker (revised 2026-11-08)"). Kept here only as history: before
the archive pull, ALL bytes were missing (TK5DATA2/0/1/3, SLUS) and
the instruction was "do NOT download a Tekken 5 ISO from the
internet without Jay supplying it." Jay authorized the archive pull
2026-11-07 ~20:15, and TK5DATA2 + TK5DATA3 + SLUS + small files
were fetched from the Internet Archive item `slus-210.59.-tekken-5`
by range. Only TK5DATA0 (2.07 GB) and TK5DATA1 (1.30 GB) remain
unfetched, blocked on the VM disk quota. Still owed from the
community tools: `package_fmt_pkg.py` (PKG layout), `decNLZ1.py`
(NLZ1 format), `NUDP.hexpat` / `BoneFIle.hexpat` (ImHex patterns),
`FileTableGet2x6.py` / `FileTableGetPS3.py`.

## What this means for HeartMind (superseded)

Superseded by "What this means for HeartMind (revised)" above.
History: the index decode proved Devil Jin's kit (52 motions),
both Ogre boss kits, monster archetypes, and the stage/sound
inventories; the `HM_TEARDOWN` seam in `game/js/heartmind.js`
stays empty — it waits on the keyframe-stream decode, and no
game code was changed in this pass. Jay's HeartMind design
(2026-11-07 ~19:40): Devil Within mashed with Urban Reign, any
character playable, characters without movesets get Urban Reign /
Redux movesets. That design is recorded in the spec; this decode
does not change it.
