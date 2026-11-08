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

## What is still blocked — the exact blocker

**Step 1 of the task (offsets/sizes) is blocked on missing bytes, and
step 2 (contents) with it.** No offsets, sizes, headers, motion data,
stage geometry, boss/enemy tables, meter numbers, or rank thresholds
are resolved, because the archive bytes do not exist anywhere found.

Missing files:

| File | Size | What it holds |
|---|---|---|
| `TK5DATA2.BIN` | 244 MB | The romD archive — the 498 named files themselves |
| `TK5DATA0.BIN` | 2.07 GB | Stage geometry, boss AI, meters, rank thresholds |
| `TK5DATA1.BIN` | 1.30 GB | Data archive (indexed by the 1571-entry PS2 LUT) |
| `TK5DATA3.BIN` | 423 MB | Code archive (PKG; holds the LUT overlay) |
| `SLUS_210.59` | 689 KB | Bootloader ELF |

Recorded source: Internet Archive item `slus-210.59.-tekken-5`
(md5 `5bce17ccabacea46d621d195c4600ebb`, sha1
`97ca517151229bc1c6a58396ccf470f91676f047`), per
`teardown/tekken5/INVENTORY.md`. The ISO was deleted after the
2026-10-23 survey; only the name manifest survives. Re-supply must come
from Jay's own disc or that item — **do NOT download a Tekken 5 ISO
from the internet without Jay supplying it.**

When bytes exist, the next steps are mechanical: run
`tools/romd_extract.py --scan` on `TK5DATA2.BIN`, confirm a candidate
table by extracting a known file, `--extract` by name, then decode the
`.dat` contents (motion format, stage geometry, boss/enemy tables, meter
and rank numbers) against the `NUDP` / `TIM2` / `MIF` headers. Still
owed from the community tools: `package_fmt_pkg.py` (PKG layout),
`decNLZ1.py` (NLZ1 format), `NUDP.hexpat` / `BoneFIle.hexpat` (ImHex
patterns), `FileTableGet2x6.py` / `FileTableGetPS3.py`.

## What this means for HeartMind

- The HeartMind mapping in the teardown spec §5d is updated with what
  the index decode proves: Devil Jin's kit is now inventoried (52
  motions with translated names), both Ogre boss kits are inventoried
  (with the True/Monstrous split as a labelled inference), the monster
  archetypes are inventoried (power/speed/standard/tricky), and the
  stage-text and sound inventories are known. The `HM_TEARDOWN` seam
  in `game/js/heartmind.js` stays empty — it waits on real bytes, and
  no game code was changed in this pass.
- Still UNMEASURED (needs bytes): Devil Jin fill rates, laser damage,
  health-drain rate; gem heal values and drop rates; Force values;
  rank thresholds (time/damage/retries/Force); boss exact moves and AI;
  stage layouts; the 40-symbol locations; the `ikt5` kit's fighter.
- Jay's HeartMind design (2026-11-07 ~19:40): Devil Within mashed
  with Urban Reign, any character playable, characters without
  movesets get Urban Reign/Redux movesets. That design is recorded in
  the spec; this decode does not change it.
