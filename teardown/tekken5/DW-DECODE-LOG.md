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
| `gym_ikdv_*` | 52 | Surge Kit donor — source: Devil Jin's DW brawler kit (moveset data only, never a character) — beams, punches, kicks, throws, turns, breakfalls (high) |
| `gym_kmb1_*` | 39 | Modified Gun Jack, stage 1 boss — machinegun, shotgun, charge shots (high) |
| `gym_kob2_*` | 29 | True Ogre, stage 3 boss — fly, fire, horn, tail, snake (medium, INFERENCE) |
| `gym_ozb3_*` | 36 | Monstrous Ogre, stage 5 boss — whirlwind `tatumaki`, stomp `fumi`, burn (medium, INFERENCE) |
| `gym_ozt4/ozhe/oznj` | 6 | Ogre-family extras, boss unassigned (low) |
| `gym_ikt5_*` | 26 | UNRESOLVED gun/fly kit, base + `_mon` monster variants (low) |
| `gym_init_obj_*` | 21 | Boss init 1/2/3/5 (boss4 ABSENT), source init objects `jin` / `devil` (source filenames only — neither is a character in our game), monster archetypes power/speed/standard/tricky, 3 test characters (high) |
| `gym_djin_newhane00-03` | 4 | Soul Surge Bloom donor — source: Devil Jin transform, wings/feathers (moveset data only, never a character) (high) |
| `gym_dw_*` singles | 7 | Face (`dwfkao`), wave (`dwhadoh`), power-up (`dwup`, `dwup_hei`), 3 opaque (medium) |
| `moj_stg00/01/02/04` | 4 | Stage text/messages, NOT geometry; `moj_stg03` absent (high) |
| `snd_*` | 18 | Lab / Egyptian / blue themes; source voice files for Lei / Jin / Heihachi / JACK / Devil Jin (source characters — voice donor data only) (high) |

Confidence spread: 155 high, 56 medium, 31 opaque (tokens not translated:
`dsrp`, `sjk`, `PSrlpf00`, `ttlp`, `hkrp`, `nog`, `rari`, `cyop`,
`soten`, `ap`, `jz`, `nara`, `dv2kam2`). Inferences are labelled as
inferences with their evidence in the JSON; nothing guessed is presented
as fact.

Code anchors proved by `snd_cXX` filenames (not guessed): c02 = Lei,
c10 = Jin, c15 = Heihachi, c21 = JACK, c30 = Devil Jin (source char codes — the source game's characters, not ours).

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
| ikdv (Surge Kit donor — source: Devil Jin kit) | 52 | 3,488 | 58.1 |
| kmb1 (Gun Jack) | 39 | 3,186 | 53.1 |
| kob2 (True Ogre) | 29 | 3,245 | 54.1 |
| ozb3 (Monstrous Ogre) | 36 | 4,165 | 69.4 |
| oz_extra | 5 | 352 | 5.9 |
| ikt5 | 24 | 1,644 | 27.4 |
| init_obj (1-frame poses) | 18 | 18 | 0.3 |
| djin (transform) | 4 | 52 | 0.9 |
| dw_singles | 7 | 353 | 5.9 |
| **Total motion** | **214** | **16,503** | **275.1 s (~4.6 min)** |

**CORRECTION 2026-11-08:** the total above was first written as 17,553
frames / ~292 s — a mis-add. The per-group numbers were right; their
sum is 16,503 frames / 275.1 s. Corrected here and in `ROMD-FORMAT.md`
and `DEVIL-WITHIN-DATA.md`.

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
- Surge donor kit — source: Devil Jin's kit (52 clips, 58.1 s), Gun Jack (39, 53.1 s), True
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
History: the index decode proved the Surge donor kit — source: Devil Jin's kit (52 motions),
both Ogre boss kits, monster archetypes, and the stage/sound
inventories; the `HM_TEARDOWN` seam in `game/js/heartmind.js`
stays empty — it waits on the keyframe-stream decode, and no
game code was changed in this pass. Jay's HeartMind design
(2026-11-07 ~19:40): Devil Within mashed with Urban Reign, any
character playable, characters without movesets get Urban Reign /
Redux movesets. That design is recorded in the spec; this decode
does not change it.

---

## Full contents + wire-up — 2026-11-08 (Jay's order, 2026-11-07 ~22:19)

Jay re-ordered: get ALL the decoding/decrypting/deciphering done
for it all and get it all wired up. This pass continues the same
lane (Tekken 5 Devil Within) to full contents + wire-up.

**Canon laws applied (Jay, 2026-11-07 ~22:19, revised ~22:32,
criterion corrected ~22:43, Law 2 corrected 2026-11-08 ~00:04):**
the word "Devil" MAY appear, but ONLY written in OUR own way
and language, NEVER in the Devil Within way (never Tekken's
Devil Jin / Devil Gene sense, never the source game's usage).
The criterion is SOURCE, not spelling: Tekken way = devil tied
to Jin Kazama / the Mishima bloodline / the Tekken mode; OUR
way = devil tied to Jay's own characters and words (DIABLO and
his title "The Devil Soul", "The Devil That Stays..." chapter).
**Law 2 (corrected 2026-11-08 ~00:04, supersedes the earlier
"three Jin figures" reading): there is NO Jin Kazama in our
game at all — no Jin Kazama character, no bloodline Jin. The
ONLY Jin is the soul JIN (刃, the Blade Soul), pickable as
Phantom. The Devil Jin kit (source group `gym_ikdv_*`) is
moveset donor data only, never a character.** In this log,
"Devil Jin" / "Jin" name the SOURCE game's character and kit
only (Tekken 5's Devil Within) — never anyone in our game.
Canon names come from `HEARTMIND-RENAME-MAP.md`; source
filenames come from `dw-motion-index.json` (the REAL
filenames). Names blocked on one of the 15 Jay-calls
(`HEARTMIND-JAY-CALLS.md`) are flagged PROVISIONAL with a
clearly-marked provisional name — never decided here.

### 8. Gym keyframe structure — record table + channel kinds decoded

`tools/gym_parse.py` — structural parser, validated on all 214
extracted gym files (0 validation problems). The container
layout (see `ROMD-FORMAT.md` for the full spec):

- **Sub-header @32 (4 u32):** record-table offset (= 72, always),
  bone-table offset, data offset, field3 (again). `GYM1` @64.
- **Record table @72, 16 bytes/bone:** per bone — channel pair
  (u16, u16; −1 = none), type u16, index u16 (records pair up:
  0,0,1,1,2,2…), cumulative data offset u32 (×2, identical pair).
  Offsets are monotonic in every file.
- **Bone table @bone_table_off:** bone indices (u16) with 0xFFFF
  markers.
- **Data section @data_off:** per-frame blocks. The record-table
  cumulative offsets describe the layout WITHIN one frame block.
  Frame blocks are variable-length (keyframe/delta encoding: a
  13-frame file is NOT 13× the 1-frame size — `newhane01`
  13 frames = 760 data bytes vs `newhane00` 1 frame = 114).
  The first 108 bytes of `newhane01` are byte-identical to
  `newhane00` (same first frame), proving the block layout.

**Channel kind is carried by the record type LOW byte
(measured, validated across all files):**

| Type low | Bytes/entry | Channel | Values |
|---|---|---|---|
| 3 | 12 | SCALE | 3 float32 (sx,sy,sz), near 1.0 (0.96–1.07) |
| 11 | 12 | POSITION | 3 float32 (x,y,z) in millimetres |
| 7 | 6 | ROTATION (packed) | 3 × i16; angle scale NOT yet confirmed |

Position decode validated: root bone ~origin; height bone
Y ≈ 989–1011 mm; side bone X = −400 mm; upper-body bones
Y ≈ 1280–1365 mm — a coherent skeleton across all kits.
Airborne clips confirm it: `kmb1_tojo` (entrance) Y ≈ 5517 mm,
`kob2_fly2fire` / `fly2landing` / `flykamae` (flying) Y ≈ 7050 mm,
`ozb3_warp2` Y ≈ 4445 mm, `ikdv_d_jump_p` Y ≈ 2566 mm — all
consistent with their clip names (jump / fly / warp / entrance).

First-frame channel counts (214 clips): position 2,431,
rotation-packed 4,908, scale 520. **NOT yet decoded:** the inner
keyframe packing (how delta frames are delimited) and the
type-7 6-byte rotation encoding (3 × i16; the angle scale is
unconfirmed). The per-frame keyframe stream is the remaining
gym blocker — see "still blocked".

> **CORRECTION (2026-11-08, retarget lane — commit `1beffd1` + this lane):**
> the keyframe streams ARE now decoded. The inner packing is full frame
> blocks (step flag: header u16[7] 8192 = every 2nd frame, 0 = every frame);
> rotations are i16 × 180/32768 deg with the LOCAL convention
> **R = Rz(t2)·Ry(t1)·Rx(t0)** (the decode's stated R = Ry(t0)·Rx(t1)·Rz(t2)
> was WRONG — cracked by a direction test, 9.2° mean error vs 35.9° for the
> next-best of 24 conventions). Positions are mm Y-up. Per-joint curves for
> all 214 clips are in `dw-motion-curves.json` (9,002 keyframes; tool
> `tools/gym_keyframes.py`). The FK model, the L/R swap, and the retarget
> bake are recorded in §22.

### 9. Canon-named motion bank — `dw-motion-bank.json`

`tools/gym_parse.py` → `dw-motion-bank.json` (220 clips:
214 extracted + 6 missing). Every clip carries: source file,
group, index gloss + confidence, **canon kit + canon role
(rename map)**, wireable flag, bones, frames, duration,
subtype (standard/sparse), record table, bone table, data
size, and first-frame channel values. **182 clips wireable.**
Canon kits: Surge Kit (52), Warden Kit (39), Drowned Ogre Kit
(29), Unmasked Kit (41: 36 ozb3 + 5 oz_extra), Soul Surge Bloom
(4), Wave echo archetypes (12: mon_ 6 + tk_ 6), boss bodies (4).
Not wireable: unassigned kit (26 ikt5 — owner unknown),
face STUB (1), Surge Beam provisional (1 — Jay-call #6),
transform-init provisional (1), source init no-target (1),
opaque dw_singles (3), Heihachi-variant trigger (1),
6 missing files.

### 10. Moveset-library bank — `game/data/moveset-library/banks/dw.json`

`tools/dw_bank_to_moveset.py` projects the 165 motion clips
(frames > 1, wireable kit) into the moveset-library v1 schema
(`game/data/moveset-library/index.json` gains a `dw` bank
entry; `total_moves` 9516 → 9681). Per move: id
`dw:<canon_kit>:<slug>`, canon name (kit + gloss),
name_status (PROVISIONAL gloss flagged), source
`tekken5_devil_within`, anim_ref, type / subtype / position
(derived from the gloss + measured first-frame max-Y),
frames.total = measured clip frames. **frames.startup /
active / recovery, damage, and input are null** — the keyframe
timing split and the damage numbers are not decoded; all are
listed in `provenance.estimated` per entry. 1-frame bodies /
archetypes are NOT moves — they go in the HM_TEARDOWN data,
not this bank. By kit: Surge 52, Unmasked 41, Warden 39,
Drowned Ogre 29, Soul Surge Bloom 3, Surge trigger 1. By type:
strike 68, transition 43, special 23, stance 11, aerial 8,
throw 6, hold 4, taunt 2. All 165 ids unique; 0 missing
required fields (validated).

### 11. HM_TEARDOWN data — `game/data/heartmind-dw-teardown.json`

`tools/dw_teardown.py` builds the data for the `HM_TEARDOWN`
seam (`game/js/heartmind.js`). `ready` is **false** — the three
core fields are null, NOT guessed: `enemyAi` (AI patterns live
in TK5DATA0/1), `waveTables` (per-stage wave composition needs
the load-list-to-stage assignment resolved; spawn counts/order
are not in the load lists), `doorSystems` (platforming/door
progression, TK5DATA0/1). The measured data IS carried in
`dw_data`: the 12 wave-echo archetypes (mon_ 6 + tk_ 6, all
78 bones, 1 frame), the 5 boss kits (clips/frames/duration),
the 4 boss bodies (boss1/2: 78 bones; boss3/5: 111 bones),
the 4 stage inventories, the load-list evidence (120 blocks
reference mon_ archetypes, 76 reference tk_, 16 reference a
boss), and the 6 missing files. THE FURNACE (stage 4) has no
DW donor: no boss4 init, no moj_stg03. The SOUL SPHERE is an
orb that spawns monsters; the missing body is the design.

### 12. Stage inventory — `moj-stage-inventory.json`

`tools/moj_parse.py` — full per-stage container inventory.
**NUDP chunk length validated:** NUDP u32[1] = chunk byte
length (distance to the next NUDP) — tiling holds on all 4
stages. MIF: u32[3] = 0x05010000, u32[4] = small count
(bone count?), u32[5] = 64, u32[6] = data size (multiple of
64), u32[7] = chunk size − 16. NUDP u32[4..7] are float32
values (position / bounds — unresolved which). The actual
stage geometry / positions / collision inside NUDP/MIF are
NOT yet parsed (needs the NUDP model + MIF bone formats
reversed). Stage totals: THE THRESHOLD 29 NUDP / 29 TIM2 /
56 MIF; THE GALLERY OF MASKS 18/18/18; THE DROWNING ROOM
20/20/22; THE STILL POINT 3/3/3.

### 13. Audio inventory — `dw-audio-inventory.json`

`tools/snd_inventory.py` — all 18 sound files. P3Dp header
measured: u16[0] = 0x0A01 constant; u16[1] = sequential id
(1–20, ids 4/14/19 missing); u16[2] = clip count (8–54);
u16[3] = clip_count × 104 + 16 (table size); u16[5] = 1–6;
u16[6] = 0; u16[7] mostly 4. Entropy ~6.5 (compressed/
encoded audio) except `snd_c_tks.dat` (0.39, near-empty).
**Audio payload (VAG/ADPCM inside P3Dp) is NOT decoded.**
`snd_c02lei.dat` is plain text (sound positions + event
script), not P3Dp.

### 14. TK5DATA1 stream-scan — numbers NOT in TK5DATA1 as text

`tools/tk5data1_scan.py` — TK5DATA1.BIN (1,297,731,584 bytes)
could NOT be downloaded whole (disk quota). Stream-scanned
instead: fetched in 124 × 10 MB parallel Range chunks,
scanned IN MEMORY for DW-relevant strings (force/gem/symbol/
laser/rank/gauge/drain/heal/devil/gym_/mon_/romD/item_force),
discarded each chunk; only the 48 KB hit log was written.
**Result: 232 hits, 0 chunk errors — and ALL 232 are "gem"
(140) / "GEM" (52) / "Gem" (40). Zero hits for force, symbol,
laser, rank, gauge, drain, heal, devil, gym_, mon_, romD,
item_force, DEVILJIN.** The "gem" hits are FALSE POSITIVES:
binary data that happens to contain those bytes, in a
repeating 2048-byte record structure (e.g. +940 MB region,
55 hits at exact 2048-byte intervals with the context
`[{.#gem`). They are NOT a gem table. **Conclusion: TK5DATA1
contains NO readable DW-relevant strings.** The meter/gem/
Force/rank/symbol numbers are NOT in TK5DATA1 as labelled
ASCII data — they are binary values in TK5DATA0/1 (unlabelled,
needs the LUT entry + structure to identify) or MIPS
immediates in the Code blob (needs disassembly). No number
for them is presented here.

### 15. Rename-map corrections found by this pass (for the coordinator)

The rename map (`HEARTMIND-RENAME-MAP.md`) has filename errors
against `dw-motion-index.json` (the index is right; the map's
rows are wrong). The bank uses the index's REAL filenames.
Corrections owed in the map:

- **init_obj mon/tk:** map says mon01–06 and tk05/tk09/tk10/
  tk11/tk12/tk14/tk15/tk16/tk17/tk19/tk21. Real: mon_power1/2,
  mon_speed1, mon_standard1/2, mon_tricky1; tk_power1/2,
  tk_speed1, tk_standard1/2, tk_tricky1. The tk family is the
  SECOND wave-enemy family (parallel to mon_), not unassigned.
- **init_obj devil/jin:** map does not list
  `gym_init_obj_devil.dat` or `gym_init_obj_jin.dat` at all.
  Both extracted. devil = source transform init (INFERENCE:
  Soul Surge Bloom donor — PROVISIONAL, Jay's call). jin =
  source init object; there is NO Jin Kazama in our game at all
  (Law 2, Jay 2026-11-08 ~00:04) — source data only. Do NOT wire
  as a fighter.
- **ikt5:** map lists ikdv-like filenames (36_nage_f, b_nage_f,
  chaku, dsrp, fstep, k_1…). Real ikt5 files are _mon variants
  + cross-references (PSrlpf00, fly3_mon, fumi, gunup01,
  guru2, hkrp, kamae, kata_mon, katgym_Bbr_bbblow,
  katgym_Gan_mekin, rgun_mon, rlp_sp2, strk01, ttlp).
  Group stays unassigned (owner unknown) — the per-file rows
  are wrong.
- **dw_singles:** map lists dw_init, dw_mon, dw_mo_shot,
  dw_mon_sj (do not exist). Real: dw_nog00, dw_raribxk,
  dw_rarixk (opaque tokens, unassigned), dwfkao00 (face STUB),
  dwhadoh00 (Surge Beam provisional — Jay-call #6), dwup00
  (Surge trigger), dwup_hei (source Heihachi-variant, unassigned).
- **oz_extra:** map lists ozb3_dsrp / dsrp_k / sjk / sjk00-02
  (those are ozb3 files). Real oz_extra: ozt4_aidoring,
  ozt4_goron, ozt4_kamae, ozhe_1ckj66a (MISSING), ozhe_power,
  oznj_meteorite. Group stays Unmasked Kit (index grouping).
- **snd:** map lists snd_bg_blu/egy/lab.dat, snd_boss_all,
  snd_boss_last, snd_dmg_se, snd_gym_se, snd_last, snd_sys
  (do not exist). Real: snd_bg_blu_se / bg_egy_se / bg_lab_se,
  snd_c_03_ogre, snd_c_04_iseki, snd_c_05_ogre, snd_c_boss,
  snd_c_monst, snd_c_tks (+ the 9 that match).
- **Non-DW gym files in the archive (out of DW scope):** the
  romD archive also holds **242 extra gym files NOT in the DW
  index** (versus-mode motions: amjz, amt3, naco, kmt2, kot6,
  etc.) — extracted to `romd_out/`, not in the DW bank.
  Available for the versus-moveset lane, not this pass.

### 16. What is still blocked — revised 2026-11-08 (this pass)

| Item | Blocker (exact) |
|---|---|
| Gym per-frame keyframe stream | Record table + channel kinds decoded; the inner delta-frame packing and the type-7 rotation angle scale are NOT yet reversed. Needs the packing reversed (the frame-block delimiter). |
| Meter/gem/Force/rank/symbol numbers | NOT in TK5DATA2 or the Code blob as readable data; NOT in TK5DATA1 as readable strings (stream-scan, 232 false-positive "gem" hits only); NOT in the Code blob as MIPS immediates either (Capstone sweep, 483,144 insns, §20 — no anchored value for any of them; sample rates FOUND: 48000/44100/22050 select, 22050 default). They are binary values in TK5DATA0/1 tables. TK5DATA0 (2.07 GB) never fetched; TK5DATA1 (1.30 GB) never held whole (quota). |
| NUDP/MIF stage geometry | PARSED (§18, commit `f1a2e29`): 70 models, 697 bones, 1,212 sub-meshes, 34,143 vertices byte-verified, 0 problems. Triangle indices NOT found; positions chunk-relative (no stage-absolute placement); symbol locations NOT found. |
| P3Dp audio payload | DECODED (§19): 391 clips, 318 regions, 297.6 s at 22050 Hz (assumed — see §20, 22050 is the default tier of a 3-rate select, per-clip rate NOT confirmed). 2 clips (`snd_title.dat` 6–7) absent from this disc image. |
| HM_TEARDOWN enemyAi / waveTables / doorSystems | Null (see §11). enemyAi + doorSystems need TK5DATA0/1; waveTables needs the load-list-to-stage assignment resolved. |
| 6 DW files | No data in TK5DATA2 (list references only). NOT in TK5DATA1 as gym entries — LUT scan of all 1571 entries found 0 gym files (§21; sampler validated by TK5RESU1/TIM2 magics). TK5DATA0 (2.07 GB) has no LUT and was not scanned — blind 2 GB scan not run. May be in TK5DATA0 or absent from this disc image. Per-file verdicts: all 6 UNPROVEN. |
| Disk quota | Flaky / nearly full. This pass hit EDQUOT twice writing a 10 KB file (Redux ISO download, 3.8 GB in `~/workspace/urban-reign-redux/`, is the current consumer — NOT this lane's to delete). TK5DATA0/1 cannot be held whole here. Stream-scan (fetch + discard) is the viable route for them. |

### 17. What this means for HeartMind (revised, this pass)

- Bucket B moves again (see `HEARTMIND-COMPLETION.md`): the
  motion bank is now **canon-named and wired** — 165 moves in
  the moveset library (v1 schema, honest nulls for the
  undecoded timing/damage/input), 182 clips wireable, 12 wave-
  echo archetypes + 4 boss bodies + 4 stage inventories in the
  HM_TEARDOWN data file. The seam's three core fields
  (enemyAi / waveTables / doorSystems) stay null — they need
  TK5DATA0/1 or the stage assignment, not guesses.
- Per-joint curves are NOT yet playable: the first-frame
  channel values are decoded (position/scale/rotation-packed),
  but the per-frame keyframe stream is not. A retarget lane
  can use the clip list, durations, bone counts, and first-
  frame poses now; full motion needs the packing reversed.
- No meter/gem/Force/rank/symbol number is presented anywhere
  in this pass — the TK5DATA1 stream-scan proved they are not
  readable strings there, and the MIPS immediate scan (§20)
  proved they are not anchored immediates in the Code blob
  either. Do NOT present any number for them until TK5DATA0/1
  table bytes yield them.
- Bucket B moves again (see `HEARTMIND-COMPLETION.md`): B8 stage
  geometry 10% → 35% (vertices+bones parsed and byte-verified;
  indices, placement, spawns, symbol spots still missing); B1
  50% → 60% (geometry parse + audio decode close two of its
  missing items; meter/rank numbers still missing, retarget
  still missing). Bucket B ~12% → ~15%; headline ~45% → ~47%.
- Audio is decoded and measurable — 391 clips, 297.6 s — but the
  per-clip sample rate is NOT confirmed (22050 assumed; the
  code's rate-select proves 22050 is only the default tier).

### 18. Stage geometry — NUDP vertices + MIF bones parsed (commit `f1a2e29`, pushed)

- Parser: `tools/moj_geometry.py`; `moj_parse.py` fix (raw `'MIF'` search overcounted false EMIF bytes; inventory corrected stg00 MIF 56→29, stg02 22→20).
- Totals: **70 NUDP models, 697 bones, 697 blocks, 1,212 sub-meshes, 34,143 vertices, 0 validation problems.**
- Verification: **all 34,143 vertices byte-verified against the raw `.dat` files** (positions are chunk-relative — the first spot-check failed only because file-absolute offsets were used; corrected, 0 mismatches). UVs match. All positions inside chunk bounding spheres. All 1,212 sub-mesh checks pass (sphere, UV finite, aux header/trailer, normal header). Variants 0x82: 1,182 / 0x83: 14 / 0x86: 16.
- Files: `moj-stage-geometry.json` (7,347,961 B), `tools/moj_geometry.py`, updated `moj-stage-inventory.json`.
- Honest limits: **triangle indices NOT found** (vertices in draw order; strip order UNCONFIRMED). Positions are chunk-relative — no stage-absolute placement. No breakables/spawns/symbol spots. Symbol locations NOT found.

### 19. P3Dp audio decoded (this pass)

- `tools/snd_decode.py` fixed: decode available whole frames instead of skipping a region short by a partial frame. Recovered 21 of 23 skipped clips.
- Totals: **18 files, 391 clips, 318 unique regions decoded, 6,562,472 samples, 297.6 s at 22050 Hz.**
- Deliverable: `dw-audio-decoded.json` (187,999 B) — measurements only. 3 proof WAVs in `~/workspace/devil-within-decode/audio-proof/` (**workspace only, NOT in git** — decoded commercial audio stays out of git): `blu-clip0.wav` (8,086 B, 0.18 s), `c10-clip0.wav` (9,374 B, 0.21 s), `largest.wav` (328,014 B, 7.44 s) — all ffprobe-verified PCM s16le mono 22050 Hz.
- Short regions: 13 short by exactly one 16-byte VAG frame (clip table size overstates by one frame); 1 (`snd_c_tks.dat` clips 5–9) 4 bytes past EOF + 12-byte partial frame; 1 (`snd_title.dat` clip 5) 37,376 bytes short — file holds only its first 60%.
- **Only 2 clips remain undecodable: `snd_title.dat` clips 6–7 (0 bytes in file — data absent from this disc image).**
- Sample rate 22050 Hz is ASSUMED (standard PS2 SE rate, not in the bytes) — see §20: 22050 is the DEFAULT tier of a 3-rate select, not the only rate. Per-clip rate NOT confirmed.

### 20. Code blob MIPS immediate scan — meter/gem/Force/rank/symbol numbers (this pass)

- Tool: `tools/code_immediates.py` (Capstone 5.0.7, MIPS64 LE, linear sweep, detail=False + op_str parsing; detail=True aborts on some encodings; MIPS32 mode stops after 1 instruction because `sd` is 64-bit).
- Sweep: **483,144 instructions, 41,144 skipped words, ~90% coverage in file 0x0–0x200000** (real code region; above that strings/LUT/tables). **11,940 lui+addiu/ori pairs reconstructed.**
- Load base: **BEST-SUPPORTED 0x200000, NOT proven** (jal/j landing over 22,414 targets: base 0x0 → 13.2%, 0x100000 → 60.9%, **0x200000 → 74.3%**, 0x80000000 → 0%). Blob occupies VA 0x200000–0x497E57 under this hypothesis. ~26% of calls go outside this blob (other PKG overlays). `$gp` zeroed at file 0x1CAC14 — no gp-relative addressing.
- Anchor refs: essentially NONE. At base 0 AND base 0x200000, zero lui-pair refs for PS2 LUT (0x27B5B0), `item_force` (0x2905B8), `handycap_gauge_yellow_p1/p2` (0x28CAD1/0x28CAF1), `RankingMode` (0x28B3F0), `name_DEVILJIN` (0x28A4D9). Single exception: `'Devil Jin'` (file 0x27A0A8) formed once — lui file 0x9D2A0, use 0x9D2AC, `$a1`, VA 0x47A0A8 — in a name-lookup loop calling `jal 0x296DE0` (VA) with successive fighter-name pointers (Eddy Gordo, Roger Jr., Anna Williams, Bruce Irvin, Devil Jin, Feng Wei; one pointer lands mid-string, `'rei'` tail of Wang Jinrei — recorded, not resolved), clearing flag bit 0x1000 (field +0x80) on each found record.
- **Sample rates FOUND — the one solid hit.** Function at file 0x50050 (VA 0x250050): reads a sound-header word (struct+0x58), tests flag bits, selects a rate passed as `$a2` to a call at VA 0x316BE8 with `$a3=7`: **flag bit 0x20 → 48000; bit 0x40 → 44100; else 22050.** Rates sit within 12 bytes (file 0x50178 `ori $a2=0xbb80`=48000; 0x50180 `ori $v0=0xac44`=44100; 0x50184 `addiu $a2=0x5622`=22050; `movz` picks 44100 if flag 0x40 set). Other rate sites: 22050 also at file 0x594F4; 48000 also at 0x11A2F0, 0x175128, 0x175F58. **22050 is the DEFAULT tier, not the only rate.** No caller (`jal 0x250050`) exists in the scanned code — called from outside this blob.
- 1,000,000 (Force reward hypothesis): 2 pair sites, NEITHER attributable to Force. Site A (file 0x67E5C lui / 0x67E64 ori, `$v1`): stored to stack struct +0xB20 in a float-math function with a 6-entry loop, 0.5/1.0 float constants, 16-byte-entry table at 0x16CD70+16*i — UNCONFIRMED candidate, no Force/gauge/rank anchor nearby. Site B (file 0x148200 lui / 0x148204 ori, `$a1`): inside a 64-bit divide helper (multu by magic 0x8CA, mflo/mfhi, jal 0x120CC8) — most plausibly a time conversion (µs→s divisor), NOT a reward. Candidates only.
- Meter/gem/Force/rank/symbol numbers: **NOT FOUND as anchored values.** No string anchors in the blob for `symbol`, `laser`, `drain`, `heal` (0 byte-search hits). `item_force`, `RankingMode`, `handycap_gauge` strings exist but are never referenced by lui pairs. Float constants from pairs are mostly ~2.0 bit patterns (0x40000400 ×12, 0x3FFFFFFF ×9, 0x40000800 ×4) — likely addresses/fixed-point, not confirmed tuning floats; 1500.0 (0x44BB8000) ×2, unattributed.
- Verdict: the numbers live in TK5DATA0/1 tables (or in data the code reads via tables/pointers this scan cannot resolve without the load map) — NOT recoverable from this blob by immediate scan.
- Deliverables: `tools/code_immediates.py` + `dw-code-immediates.json` (12,913 B — sweep stats, pairs, base metric + verdict, anchor refs, hypotheses, float constants, top small immediates, sample-rate sites + rate-select disassembly, 1M sites with context).

### 21. The 6 missing DW files — LUT gym scan of TK5DATA1 (this pass)

- Tool: `tools/lut_gym_scan.py`. Method: first 2048 bytes of each of the 1571 PS2 LUT entries, HTTP Range-fetch + discard (no whole-file download, no big disk writes); GYM1 magic at offset 64, raw then sector-cipher (seed = entry index).
- Result: **1571 entries; 237 skipped (size 0xFFFFFFFF or < 104 B); 0 fetch errors; 1334 sampled; 0 gym entries** (0 raw, 0 encrypted).
- Sampler validated: 8 random entries' decrypted first bytes show real structure — entry 148 decrypts to `'TK5RESU1'`, entry 192 to `'TIM2'`, entries 758/936 to a `'COM '` container header — proving the LUT offsets and the sector-cipher decrypt (seed = entry index) are right. The 0-gym result is real, not a sampler bug. (A full-entry word-sum checksum check was started and stopped: the largest entry is 212,115,456 B and the single-stream fetch was still running after ~9 minutes; the magic-based validation already proves the offsets and decrypt, and the LUT itself was validated in an earlier pass.)
- Per-file verdicts — all 6 **UNPROVEN** (none found, none excluded):
  - `gym_ozhe_1ckj66a.dat` — UNPROVEN (not in TK5DATA1 as a gym entry; TK5DATA0 not scanned — no LUT for it; may be absent from this disc image).
  - `gym_ikt5_katgym_Bbr_bbblow.dat` — UNPROVEN (same).
  - `gym_ikt5_katgym_Gan_mekin.dat` — UNPROVEN (same).
  - `gym_init_obj_testchr1.dat` — UNPROVEN (same).
  - `gym_init_obj_testchr2.dat` — UNPROVEN (same).
  - `gym_init_obj_testchr3.dat` — UNPROVEN (same).
- Why attribution is impossible even if gym entries existed: the 6 names appear NOWHERE in TK5DATA1 (full string stream-scan: 0 `'gym_'` hits) and the index records no sizes for them, so no LUT entry can be matched to one of them by name or size.
- Deliverables: `tools/lut_gym_scan.py` + `dw-lut-gym-scan.json` (687 B).

### 22. Retarget — DW motion curves onto Western Heart fighters (this lane, branch `retarget-dw-curves`)

Pilot: Pantera's flow donors (Surge Kit throws, Soul Surge Bloom trigger + beam). The curves are retargeted through the game's existing `retargetT3Clips` path — no second animation system. Bake tool `tools/anim/dw_curve_bake.py` (+ shared FK module `teardown/tekken5/tools/dw_fk.py`, verification `teardown/tekken5/tools/dw_rotcheck.py` + `dw_roundtrip.py`); wiring in `game/js/t3anims.js` (`DW_MOVES` / `ensureDwMoves` / `dwMoveClip` / `dwMoveRetarget`, a mirror of the T7 moves) and `game/js/fighter.js` (the `dw:` hooks); pilot bank `game/assets/anim/dw/` (skeleton.json + `moves.pantera.pack.json`, wh-dw-moves/1); tests `game/tests/dw-retarget.test.mjs` (7 tests). Probe `tools/proof-harness/dw_probe.mjs`.

- **Rotation convention (CRACKED, corrects the decode): R = Rz(t2)·Ry(t1)·Rx(t0), LOCAL**, composed down the DW hierarchy. The decode's stated R = Ry(t0)·Rx(t1)·Rz(t2) was WRONG (direction test: 9.2° mean error vs 35.9° for the next-best of 24 conventions; the 9.2° residual is wrist/ankle articulation + position locators' own translations, not a wrong convention).
- **FK model (exact):** bone 0 = root ground travel, stage frame (Y always 0); bone 1 (hips) is root-relative `[0, height, 0]` (X/Z exactly 0 every frame); limb endpoints (25–32) are stage-frame absolute; bone 8 = FIXED marker `[-400, 0, 0]` (not a joint — excluded); bone 2 = lone chain, rotation-only on t1, sweeping −166° to +176° (affects no joint position — unmapped, dropped, nature unidentified, candidate facing/spin/prop); bones 33/34 = CONSTANT `[-180, -180, 89.99]` (frozen toes, offsets unidentifiable); bones 9/10 = 2-bone chain off bone 6 (chest), rotation-only, nature unidentified (candidate tail/wing/hair/cape — unmapped, dropped); bones 4/5/7 carry large frame-0 rotations (rest locals are NOT identity — the bake emits deltas from a rest pose); bones 13/17/20/23 are single-axis hinges (t0=t1=0, only t2 varies). Rest offsets (mm, parent-local; authored bone lengths, identical across the throw clips): arm 140+300+230 = 670 mm, leg 440+420 = 860 mm; bones 3/5/7 co-located ([0,0,0] each — gauge freedom, only the sum matters). FK check: ikdv_36_nage_f RMS 0.108 mm (max 0.380), ozb3_greaction2 0.093 mm, kmb1_kamae 0.118 mm, kmb1_yoko_l 0.287 mm (max 3.125) — one skeleton for all 35-bone clips.
- **L/R swap (measured):** DW bone 11 (and 12/13/14/19/20/21/25/27/29/31/33) is the character's RIGHT side and bone 15 (16/17/18/22/23/24/26/28/30/32/34) is the LEFT side (after rotating the facing to +Z, the bone-11 side sits at −X; in a right-handed Y-up frame facing +Z, left is +X). The first "11=Left" hypothesis was WRONG. Verified on 4 clips (ozb3_greaction2, kmb1_kamae, kmb1_yoko_l, ikdv_36_nage_f).
- **Skeleton variants:** the 27-bone skeleton is the 35-bone minus the 8 locator bones, toes renumbered 33→25, 34→26 (chains match exactly after removal). Bone lengths transfer directly. The 27-bone clips have no limb position data, so transferred offsets are UNVERIFIED until the watched render confirms them. The 12-bone newhane skeleton (two 6-chains, no positions at all) is NOT retargetable the same way — rest offsets unidentifiable from the clip alone; deferred with an honest note.
- **Reference rest pose + facing:** neutrality scan over all 174 decoded 35-bone clips (frame 0) picks `gym_ozb3_greaction2.dat` (score 304; shoulders symmetric, hips 885 mm, feet 143 mm, knee_mag 182, knee_dot 0.91, facing −7.5° by the old knee measure). The DW rest pose is a guard stance (bent knees ~177 mm, feet ~130 mm off the floor), not a flat standing pose — fine for the skeleton rest (the retarget's floor clamp handles the feet). **Facing is the PELVIS forward (W_3 at frame 0), already +Z (0.0°)** — no facing rotation. (The earlier +7.5° rotation from the bankFacing kneeDeg was a misread: kneeDeg is the knee direction RELATIVE TO the pelvis forward, not the facing.) Head-vs-chest constant at frame 0 is 4.5–11.4° (below the retarget's head-correction gate — no bake-time head correction needed). **No stance window exists in the DW clips** (the first 8 keyframes already move 74–126°), so no `stance` clip can be emitted and the load-time head/arm/spine estimators (which need a clip named `stance`) do NOT run for the DW bank — arm transport twist is UNCORRECTED (the render is the arbiter).
- **Emission (conjugated deltas, plus bank-frame conjugation):** `E_c(k) = W_parent(ref) · local_c(k) · local_c(ref)⁻¹ · W_parent(ref)⁻¹`, additionally conjugated by the facing rotation R_y so the whole bank (rest positions, root_t AND rotations) lives in the bank frame. Only the conjugated delta makes the composed G equal the true world delta `W_c(k)·W_c(ref)⁻¹` (verified by induction). Absolute locals (round-trip worst 8.6 m) and plain deltas (1,677 mm) are both WRONG. Canonical mapping: W_Hips = W_3 (pelvis; bone 1 has no rotation); W_Spine = W_3 (Spine local = identity); W_Chest = W_6; W_Neck = W_Chest; W_Head = W_4; UpLeg local = q_7·q_19 (leg-girdle twist folded in exactly); Shoulder local = q_11/q_15. `root_t` = `[pos_0.x, pos_1.y, pos_0.z]` in metres, rotated into the bank frame. fps = 30 for step-2 clips (60 for step-1). `active_frames` is null for every DW move (the decode carries no hit timing — honest nulls; the game times DW moves on the moveset's own S/A/R).
- **Skipped-joint residual (real limit of the 35→21 bone map):** the canonical hierarchy skips DW joints 5 (Chest) and 7 (UpLeg). Their rotations are folded into the child's local, but the child's POSITION cannot be recovered from the parent's rotation alone — the residual is the skipped joint's rotation change × its offset (chest ~44–65 mm, upleg ~95–190 mm, up to 200–400 mm at the foot during a big throw). This does NOT corrupt the retarget's joint rotations (G is correct); it only bounds the torso-match direction error by a few degrees. The render is the arbiter.
- **Assumptions in the skeleton (DW data has no positions for these; the game's own canonical proportions at the same scale — DW leg 0.86 m = king leg 0.86 m):** (1) Head/Neck rest from the king bank (Chest→Head 0.4229 m, Chest→Neck 0.273 m, Hips→Chest 0.1365 m). (2) ToeBase rest = Foot + [0, −0.1, 0.153] m (king bank's foot direction; ratio 0.2125, inside the retarget's 0.3 sanity gate). Without a real Head rest, the torso match would break — a real Head rest is required.
- **Pilot bank (baked, verified):** 8 clips, 4 moves. `surge` → `dwhadoh00` (beam, input `1+2+3+4`); `surge-trigger` → `dwup00` (power-up, plays once when Soul Surge Form starts); `1+3` → `ikdv_36_nage_f` (Surge Form front throw); `2+4` → `ikdv_36_nage_y` (Surge Form front throw). Unmapped (baked as data, mapping owed, not guessed): `ikdv_b_nage_f/y`, `ikdv_ppp_nage_f/y` — the HeartMind doc lists the six nage clips only as "Surge Form throws" and does not say which Pantera throw each one is. Rotation round-trip worst **0.00°** across all 8 clips (rounding from 6-decimal quat storage). Position round-trip worst **129.8–288.8 mm** (the pure skipped-joint residual). Bank-frame pelvis forward 0.00° from +Z; LeftShoulder +0.024 / RightShoulder −0.170, LeftFoot +0.351 / RightFoot −0.472 (left at +X, right at −X).
- **In-game verification (watched, headless Chromium + software WebGL, Pantera vs Demonio, Shrine of the Blade):** the beam (`dw:surge`, kind `dw`) PLAYS — Pantera crouches low, gathers energy (bright glow), and rises; the motion is coherent (no T-pose, no wrong facing, feet on the floor). The trigger (`dw:surge-trigger`) PLAYS — but the source clip is a big leap (hips to 2.375 m, down to 0.136 m; the raw DW data confirms it), so it reads as Pantera launching into the air and landing flat, NOT as a grounded power-up. `dwup00`'s "power-up" gloss is only medium confidence in the index ("could be Devil Gauge UI or a power-up object") — the clip choice for the trigger role is the open item, not the retarget (the retarget is faithful to the source). The throw retarget function (`_dwThrowAction`) is verified by direct test (returns `dw:1+3`, action created, Surge Form on, attackName `1+3`), but the pair-binding (`_bindThrowPair` engaging the DW thrower clip during a real throw) was NOT confirmed in-game — the throw never connected within the observation windows (software rendering runs the game in slow motion; the 25 s Surge Form is game-time), and a VM restart wiped the long-wait test. The throw pair-binding re-check is owed before the throw is called verified. The T3 throw (row 277) plays correctly in the meantime (Pantera throws Demonio over, Demonio lands and recovers) — it is the game's own throw, not the DW clip.
- **Wiring order (landed):** beam first (single-character strike, hooks into `_attackClipPlan`, keyed on `attackName === 'surge'`), then trigger (one-shot on `startSurgeForm`), then throws (pair-path override in `_bindThrowPair`: DW clip replaces the thrower action only, victim still plays the T3 reaction, pair root still follows pack anchors; DW clip durations 2.0/2.1 s vs the T3 pair duration is a known limitation — the pair clock rules).
- **Tests:** full suite 313 tests (306 baseline + 7 new DW), 264 pass, 49 fail — the failing file list is IDENTICAL to the baseline (40 files). Zero new failures.
- **Still owed in this lane:** the throw pair-binding live re-check (above); the remaining 178 wireable clips in the same shape (kmb1 Warden kit next — same 35-bone skeleton, same bake; its fighter binding is a follow-up, the Warden is a brawler kind, not a fighter id); the `dwup00` trigger-role clip choice (a grounded power-up clip vs the leaping source clip); P3Dp audio payload decoded but not wired.

### 23. Retarget rollout — all remaining wireable 35-bone clips (this lane, branch `retarget-dw-rollout`, base PR #1652 head `c2eaed35`)

Same bake, same shape as the pilot (§22). Tool extended, not rewritten:
`tools/anim/dw_curve_bake.py` gains `KIT_SETS` (warden←kmb1, unmasked←ozb3,
drowned-ogre←kob2, wave-echo←oz_extra), `kit_clip_names()` (wireable 35-bone
clips of a group, from the bank), `kit_exclusions()` (measured reason per
non-bakeable clip), `pantera_unmapped()` (the pilot's 4 nage + every remaining
wireable 35-bone ikdv clip — the Surge Kit is Pantera's kit, so its clips
live in his pack as data until a move mapping claims them), `bake_set()`,
`--set` (pantera/warden/unmasked/drowned-ogre/wave-echo/all) + `--bank`.
One bug fixed in `kit_exclusions()`: a MISSING file (`ozhe_1ckj66a`, no data
in TK5DATA2) was reported as "None-bone" — it now reads "missing file — no
data in TK5DATA2 (list reference only, no curves to bake)".

- **CORRECTION to the pilot's count:** the remaining wireable set is **175,
  not 178**. The pilot's "178" = 182 wireable − 4 mapped moves, which
  double-counts the 4 unmapped-but-baked nage clips. Decoded 214; wireable
  182; pilot baked 8 (7 wireable + `dwhadoh00`, non-wireable "wave").
  Remaining wireable by bones: **35-bone 144 (bakeable now)**, 78-bone 14
  (all 1-frame init objects — poses, not motion), 4-bone 11 (appendage
  part-clips: kob2 tail ×4, ozb3 teil1 ×7), 12-bone 4 (djin wings/feathers),
  111-bone 2 (boss init objects, 1-frame). Remaining by group: ikdv 46,
  kmb1 39, ozb3 36, kob2 29, ikt5 24 (ALL non-wireable — opaque tokens /
  monster variants), init_obj 18, oz_extra 5, dw_singles 5, djin 4.
  Remaining 27-bone decoded clips: 5, all non-wireable. The 31 non-35/27
  clips are NOT bakeable with the current FK model — each with a measured
  reason, recorded by `kit_exclusions()` and in the kit bake logs.

- **Bake `--set all` (2026-11-08 ~12:24):** pantera 54 clips / 4 moves
  (3,372,185 B), warden 39 / 0 (3,362,815 B), unmasked 29 / 0
  (2,747,447 B), drowned-ogre 25 / 0 (2,219,485 B), wave-echo 5 / 0
  (299,333 B). **Total 152 clips = 144 remaining 35-bone wireable + 8
  pilot.** Verified: all 8 pilot clips byte-identical to the committed
  pack, moves identical, skeleton identical; pantera pack 54 clips / 50
  skipped; kit packs 0 moves / skipped == all clips. 10 clips are step-1
  (60 fps): 6 ikdv + 4 kmb1; the other 142 are step-2 (30 fps). Root_t Y
  (hips height) across the rollout: min 0.109 m (a throw low point),
  max 8.000 m (the flying boss's fire attack, `kob2_fly2fire`) — the
  test band is 0.05–8.5 m, which catches unit/sign errors, not jumps.

- **Round-trip verification** (`teardown/tekken5/tools/dw_roundtrip.py`,
  extended with `--pack`, default all `moves.*.pack.json`): all 152 clips
  checked, exit 0. Per-pack worst: drowned-ogre 239.9, pantera 371.0,
  unmasked 292.0, warden 376.5, wave-echo 182.8 mm. **Overall worst
  376.5 mm** (`kmb1_yoko_r`, RightLeg); median worst 136.4 mm; 9 clips
  over 300 mm, 43 over 200 mm — inside the documented residual envelope
  (up to 200–400 mm at the foot during a big throw; worst offenders are
  jumps/side-steps, consistent with the skipped-joint residual at the
  legs). Rotation round-trip worst 0.00° (unchanged).

- **Wiring:** `game/js/t3anims.js` `DW_MOVES` gains `warden`, `unmasked`,
  `drowned-ogre`, `wave-echo` — kit data packs, `moves = {}` in every kit
  pack, move mapping owed. Nothing in-game calls `ensureDwMoves()` with
  these ids yet; the binding is the follow-up (the Warden pack's hook is
  the HeartMind Warden boss in `brawler.js`). The entries make the packs
  loadable through the existing path and testable in node. All four names
  are canon terms (Warden / Unmasked / Drowned Ogre bosses, wave-echo
  archetype). The Warden is a brawler kind, not a fighter id — not forced
  onto one.

- **Tests:** new `game/tests/dw-rollout.test.mjs` (5 tests: pack files
  exist; shapes — 21 bones, fps follows the source step, unit quats,
  root_t band; DW_MOVES has one entry per pack; `ensureDwMoves` loads
  every pack with fetch stubbed to disk; totals 152 clips + exclusions
  recorded). The pilot test `dw-retarget.test.mjs` updated to the extended
  pack: 54 clips, 50 skipped, fps follows step, root_t band 0.05–8.5 m.
  **12 DW tests, all green.** Full `game/tests` suite: 358 tests, 315
  pass, 43 fail — all 43 failures are pre-existing sparse-checkout ENOENTs
  (missing moveset/model files, e.g. `game/assets/movesets/burger.json`,
  `game/ui-wh/ui.js`); zero failures mention DW/rollout. (Count shift vs
  the pilot's 313/264/49: the sparse-checkout adds needed for the probe —
  game/vendor, game/css, game/netplay, packages/creation-suite, the two
  roster attire models — unblocked test files that previously failed at
  import, so more tests run and pass.)

- **Probe (Job 1 — reproduce the pilot proof + Job 2 — throw re-check):
  run 4, 2026-11-08 ~13:00, headless Chromium + software WebGL, Pantera
  vs Demonio, Shrine of the Blade, probe `tools/proof-harness/dw_probe.mjs`.**
  Run 1 FAILED (READY false, models 404 — sparse checkout lacked them,
  remote fallback 404 on the Worker). Run 2 FAILED (READY false after
  241 s; only error: `demonio-human` 404 — Demonio's DEPOWER form,
  `roster/demonio/attires/human/model-rerig.glb`, 28,661,076 B; local copy
  missing, the Worker fallback is aborted by the probe, jsDelivr 403s
  files over 20 MiB). Run 3 FAILED (READY false after 241 s; the human
  404 was GONE after the overlay fix — only T7 stance warnings remained).
  A diagnostic probe (`/tmp/probe-env/dw_diag.mjs`, 10 s samples × 18)
  then showed the real cause: the game LOADS (models true, HUD up) and
  `roundState` goes idle → `fight` at ~t+49 s and stays there — but
  `p1.t3actions` / `p2.t3actions` stay **0 at every sample**. The T3
  animation banks (`game/assets/anim/t3/king_on_pantera_leoman/` +
  `jin/`) are NOT in the sparse checkout, and `loadT3Clips`
  (`game/js/t3anims.js:495`) fetches them with **no jsDelivr fallback**
  (unlike `fetchT7Json`), so every bank fetch 404s and the bank cannot
  be retargeted. Fix: both banks downloaded to the /tmp overlay (70
  files, 15 MB — every size verified against the repo listing, hashes
  spot-checked) + the human model (28,661,076 B, hash-verified). The
  overlay server (`/tmp/probe-env/dw_server_overlay.mjs`) serves a file
  from the overlay only when it is missing under the repo root.
  - **Run 4: READY true after 52 s.** Beam TRIGGER ok (`dw:surge`, kind
    `dw`, dwhadoh00), 12 frames — WATCHED: crouches low, gathers energy
    (bright white/gold glow + purple particles), goes low/flat on the
    floor, rises, stands; no T-pose, feet on the floor — **the pilot's
    beam result is REPRODUCED**. Trigger TRIGGER surgeForm true, actions
    [`dw:surge`, `dw:surge-trigger`], 12 frames — WATCHED: Surge Form on
    (purple meter), bright glow, low/grounded in the captured window;
    the leap is in the raw data (hips 2.375 m) even though this window
    did not catch the apex — the `dwup00` defect stands on measurement.
    Throw TRIGGER ok (1+3, Surge Form on) but the PLAN is the T3 throw
    (`row:463`, kind `own`, "KING 1+3 (T3 king r463)") and the actions
    are [`dw:surge`, `dw:surge-trigger`] — **no `dw:1+3`**. 16 frames —
    WATCHED: Pantera glowing in Surge Form next to Demonio, Demonio's
    health dropping, but NO throw arc, Demonio never goes over. **The DW
    throw did NOT connect**: the throw pair never formed within the
    window, so `_bindThrowPair` never ran and the DW override never
    engaged (the 1+3 attack fired, P2 was placed 1.2 m away inside the
    1.9 m reach, but in slow-motion rendering the grab connects after
    the 2.4 s-real capture window). Follow-up owed: a probe variant that
    polls for `f._throwPair` / `pair.throwerAction` with a long window.
    The throw pair-binding live re-check is STILL OWED.
  - Side notes from run 4: `[WH-T7] pantera: real T7 move clips
    unavailable ... HTTP 404 for assets/anim/t7/king/moves.pack.json` —
    the T7 move pack 404s locally AND on jsDelivr; fighters keep their
    T3 clips (pre-existing environment limitation, not this lane). `[WH-DW]
    pantera: 54 DW move clips` — the extended pack loads.
  - **Proof: 40 frames + 3 mp4s + 3 contact sheets in
    `/tmp/dw-proof-pilot/` (15 MB) — watched end to end (beam, trigger,
    throw sheets). They could NOT be copied to
    `~/workspace/devil-within-decode/dw-proof/` (EDQUOT — quota at zero,
    flapping; even a 2 KB copy fails). They MUST be copied ASAP when the
    quota frees; /tmp is tmpfs and is wiped on restart. Run log:
    `/tmp/dw-proof-pilot-run4.log`.

- **Trigger clip choice (Job 3, measured + watched + ADOPTED):**
  `gym_dwup00.dat` (27-bone, "power-up"): hips Y start 1283, min 136,
  max 2375, end 136 mm — leaps and ends prone. `gym_dwup_hei.dat`
  (27-bone, non-wireable): hips max 3015, end 136 — an even bigger leap,
  NOT a replacement. The DW source's power-ups ARE leaps that end on the
  floor; no DW power-up clip is grounded. **Replacement by measurement:
  `gym_ozhe_power.dat`** (unmasked kit, 45f, gloss "power"): hmin 620,
  hmax 1122, rise 200, end+ 59, travel 470 mm — starts ~922, dips to 620
  (crouch), rises to 1122, ends 981; grounded, crouch-then-rise.
  **Watched verification DONE 2026-11-08 ~13:10** (trigger-only probe,
  `/tmp/probe-env/dw_trigger_probe.mjs`, overlay pack with surge-trigger
  → ozhe_power, 55 DW clips — the overlay pack is /tmp-only, the repo
  pack untouched): READY true after 41 s, triggerAction `dw:surge-trigger`,
  12 frames — WATCHED: crouch (dips low), gather (bright glow), rise
  back up, feet on the floor throughout, NO leap, NO prone. **ADOPTED:**
  the bake's `PANTERA_MOVES['surge-trigger']` now points at `ozhe_power`
  (`gym_ozhe_power.dat`); `dwup00` is out of the pantera pack (it stays a
  decoded clip only). Re-baked pantera pack: 54 clips, 4 moves,
  3,359,575 B; round-trip worst 371.0 mm (unchanged), ozhe_power
  157.6 mm; 12 DW tests green against the new pack (run from a /tmp
  mirror — the repo pack cannot be overwritten locally, EDQUOT; the new
  pack lands via this commit's Data API blobs). The overlay pack was
  removed from /tmp/dw-overlay immediately after the run.

- **Audio (Job 5, assessed — wiring only if 1–4 are done):** the game's
  sound path (`game/js/audio.js:227-228`) is `fetch(path)` →
  `arrayBuffer()` → `decodeAudioData(ab)` — it takes WAV, and SFX are
  named events → repo paths (`audio.js:335+`, e.g. teardown WAVs). So the
  P3Dp-decoded WAVs (22050 Hz 16-bit mono) ARE playable by the game's
  sound path — the format is not the blocker. The blockers: (a) the full
  WAV set is not on disk (only 3 proof WAVs, 345 KB; regenerating all 391
  clips ≈ 13 MB via `snd_decode.py`); (b) the task's disk rule forbids
  audio in git, so live wiring needs remote-asset hosting (R2/B2) or a
  build-time generation step — that hosting/generation decision is owed;
  (c) clip→game-event curation is owed (which of the 391 clips is a hit,
  a roar, a sting — the decode gives regions, not roles).

- **Disk quota (2026-11-08 ~12:33):** the btrfs quota is at ZERO — even a
  1-byte `touch` and a `mkdir` fail with EDQUOT, in the repo AND the
  workspace. The 28.7 MB human model could not be checked out (git
  fetch of its blob fails EDQUOT) and could not be written to the repo
  at all. Workaround for the probe ONLY: the real file (size 28,661,076
  B, `git hash-object` 8b8f0b78c21683e933a38aa96df1c94860c510b9 — matches
  the GitHub API blob SHA) was downloaded to /tmp (tmpfs, separate from
  the quota) and served by a /tmp copy of the probe server
  (`/tmp/probe-env/dw_server_overlay.mjs`) with an overlay root
  (`/tmp/dw-overlay/`), consulted only when a file is missing under the
  repo root. The landed `tools/proof-harness/dw_server.mjs` is UNTOUCHED
  (it could not even be edited — EDQUOT); the overlay feature lives only
  in /tmp and is NOT committed. All doc updates for this lane (this §23,
  WORKLOG, HEARTMIND-COMPLETION.md B7) are prepared in /tmp and land via
  the Git Data API (which writes to GitHub, not the local disk) or when
  the quota frees — the workspace copies cannot be edited locally right
  now.

- **Still owed in this lane:** the commit on `retarget-dw-rollout`
  (Data API from verified tree SHAs per NO-SPARSE-COMMIT LAW, deletion
  check, grep secret scan) + PR (do NOT merge); the B7 re-score in
  `HEARTMIND-COMPLETION.md` (draft in /tmp — the workspace file cannot
  be edited locally, EDQUOT); Job 5 audio wiring (blocked as above); the
  throw pair-binding live re-check (probe variant polling for
  `f._throwPair` / `pair.throwerAction`); the 31 non-bakeable clips (new
  FK models or stay as data records); kit-pack move mappings + the
  Warden/brawler binding; copying the /tmp proof (40 frames + 3 mp4s +
  3 sheets) into `~/workspace/devil-within-decode/dw-proof/` when the
  quota frees (EDQUOT now — /tmp is wiped on restart).
