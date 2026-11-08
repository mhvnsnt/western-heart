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
| Meter/gem/Force/rank/symbol numbers | NOT in TK5DATA2 or the Code blob as readable data; NOT in TK5DATA1 as readable strings (stream-scan, 232 false-positive "gem" hits only). They are binary values in TK5DATA0/1 or MIPS immediates. TK5DATA0 (2.07 GB) never fetched; TK5DATA1 (1.30 GB) never held whole (quota). |
| NUDP/MIF stage geometry | Container counts + tiling validated; vertex/bone contents NOT parsed (ImHex patterns owed). Symbol locations NOT found. |
| P3Dp audio payload | Container header measured; VAG/ADPCM payload NOT decoded. |
| HM_TEARDOWN enemyAi / waveTables / doorSystems | Null (see §11). enemyAi + doorSystems need TK5DATA0/1; waveTables needs the load-list-to-stage assignment resolved. |
| 6 DW files | No data in TK5DATA2 (list references only). May be in TK5DATA0/1 or absent from this disc image. |
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
  readable strings there. Do NOT present any number for them
  until TK5DATA0/1 bytes or MIPS disassembly yields them.
