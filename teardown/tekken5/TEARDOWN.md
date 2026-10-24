# TEKKEN 5 (PS2) — Teardown for Western Heart

**Role in Chimera Build:** Devil Within source (owner story-mode blueprint: "Heart and Mind Within") + 32-fighter roster movesets + stages. T5 was the last fully-missing Tekken teardown (coverage matrix: 0% → ~15% after this PR).
**Developer:** Namco (2004 arcade / 2005 PS2, USA SLUS-21059)
**Platform:** PlayStation 2 (this dump: USA, SLUS-21059)
**Last updated:** 2026-10-23 (acquisition + survey v1)

---

## Archive

**ISO:** `SLUS_210.59.Tekken 5.ISO` — **4,039,974,912 bytes** (3.76 GiB)
**Source:** Internet Archive `slus-210.59.-tekken-5`
**URL:** https://archive.org/download/slus-210.59.-tekken-5/SLUS_210.59.Tekken%205.ISO
**Checksums (verified post-download, pre-extraction):**
- md5: `5bce17ccabacea46d621d195c4600ebb`
- sha1: `97ca517151229bc1c6a58396ccf470f91676f047`
**ISO deleted after verified extraction** per owner directive (permanently archived at Internet Archive).

**Full inventory:** [`INVENTORY.md`](INVENTORY.md)
**Survey tool:** [`tools/t5_survey.py`](tools/t5_survey.py) (stdlib-only; disc-layout + format fingerprinting + exe string scan)
**ISO extractor:** [`tools/iso9660_extract.py`](tools/iso9660_extract.py) (stdlib-only ISO9660 reader; pycdlib misdetects PS2 ISOs as UDF)

### Disc structure (10 files)

| File | Size | Contents |
|------|------|----------|
| `SYSTEM.CNF` | 57 B | PS2 boot config |
| `IOPRP300.IMG` | 278 KB | IOP modules |
| `IRXARC.BIN` | 305 KB | IRX module archive |
| `SLUS_210.59` | 689 KB | Bootloader ELF (MIPS). References `cdrom0:\TK5DATA3.BIN;1`. Only 522 printable strings — loads the real game from TK5DATA3. |
| `TK5DATA0.BIN` | 2.07 GB | Main data (character/stage, binary format — no ASCII filenames) |
| `TK5DATA1.BIN` | 1.30 GB | Data (binary format) |
| `TK5DATA2.BIN` | 244 MB | **romD archive** — motion/sound/text with filename manifest (see below) |
| `TK5DATA3.BIN` | 423 MB | Bootloader-loaded archive (binary format). **NOTE:** directory lists both `TK5DATA3.BIN` and `TK5DATA5.BIN` at the SAME extent (1646501) — duplicate entries, identical data. |
| `TK5DATA4.BIN` | 179 KB | MIPS EXEC ELF (no strings — secondary program/overlay, purpose TBD) |
| `TK5DATA5.BIN` | 423 MB | Duplicate of TK5DATA3.BIN (same extent) |

### Where the game data lives

- **Motions/animations:** `TK5DATA2.BIN` (romD) — 498 named `.dat` motion files, 109 character codes. Manifest: [`t5_motion_manifest.txt`](t5_motion_manifest.txt), code map: [`t5_char_codes.txt`](t5_char_codes.txt).
- **Character/stage models:** `TK5DATA0.BIN` (2.07 GB, format TBD — RE bench).
- **Main program overlays:** `TK5DATA3.BIN` (loaded by bootloader).
- **Movies/audio:** TBD (likely TK5DATA1.BIN).

### Container formats (survey v1)

- **romD** (`TK5DATA2.BIN`): magic `romD` at offset 0. Contains CRLF filename lists + `BDPK` section markers (21 found). File table → data mapping NOT yet reversed (RE bench).
- **TK5DATA0/1/3**: proprietary binary, no ASCII filenames, no romD magic. High entropy (compressed or packed). Format RE queued.
- **Filename convention** (TK5DATA2): `gym_<charcode>_<motion>.dat` (motions), `snd_*.dat` (sound), `moj_*.dat` (text/moji), `stgXX.dat` (stages).

### Devil Within data (PRIORITY — owner: Devil Within content FIRST)

Found in `TK5DATA2.BIN` motion manifest:
- `gym_dw_nog00.dat`, `gym_dw_raribxk.dat`, `gym_dw_rarixk.dat` — Devil Within enemy/boss animations
- `gym_djin_newhane00.dat` … `gym_djin_newhane03.dat` — Devil Jin animations (transformation)
- `dwfkao00.dat`, `dwhadoh00.dat`, `dwup00.dat` — DW-specific data
- `stg00.dat`, `stg01.dat`, `stg02.dat`, `stg04.dat` — stage files (DW stages likely among these; stg03 absent)
- `c30dvj.dat` — Devil Jin character sound (`c21jac.dat` = Jack, `c15hei.dat` = Heihachi, `c10jin.dat` = Jin)

**NOT found on disc:** ASCII "DEVIL WITHIN" (0 occurrences in TK5DATA0/1/3), `gym_dw_` in TK5DATA0/1/3. DW stage geometry, boss AI, and mechanics live in the binary TK5DATA0/3 formats — RE bench.

Full DW data map: [`DEVIL-WITHIN-DATA.md`](DEVIL-WITHIN-DATA.md). Design baseline: `~/workspace/devil-within-teardown.md` (2026-10-22 research).

### Roster manifest (32 fighters)

**Full list:** [`ROSTER.md`](ROSTER.md) — documented from public game data, to verify against TK5DATA0 once the format is reversed.

### Stage manifest

**Full list:** [`STAGES.md`](STAGES.md) — versus stages (public data) + 5 DW stages.

---

## What's Blocked and Why

- **romD file extraction:** filename manifest extracted, but the file-table → data-offset mapping isn't reversed. The `BDPK` markers (21) don't align with the 498 files — deeper structure needed. → RE bench (`tools/re/QUEUE.md`).
- **TK5DATA0/1/3 formats:** proprietary, no filenames. Need MIPS RE of the loader (SLUS_210.59 → TK5DATA3 → data). → RE bench.
- **DW stage/boss data:** in TK5DATA0's binary format. Blocked on the above.

## Chimera Build Value

- **Motion manifest (498 files):** the complete T5 animation naming scheme — `gym_<char>_<motion>.dat` with romaji motion names (`kamae`=stance, `idling`, etc.). Direct input to the moveset library once extracted.
- **Devil Within:** DW animation files located; stage/boss data mapped to TK5DATA0 for the RE bench. The "Heart and Mind Within" blueprint now has file-level grounding, not just wiki research.
- **32 fighters:** roster documented; per-fighter motion files identified by char code (mapping codes → fighters is RE bench work).

## Next Steps

1. RE bench: romD file table → extract the 498 motion `.dat` files → moveset library
2. RE bench: TK5DATA0 container → character/stage models + DW stage/boss data
3. Map char codes (`ikt5`, `amt3`, `djin`, `dw`, …) to the 32 fighters
4. Wire extracted motions into `moveset-library/`
