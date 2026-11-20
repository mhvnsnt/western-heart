# TEKKEN 5 (PS2) — File Inventory

**Source ISO:** `SLUS_210.59.Tekken 5.ISO` (4,039,974,912 bytes, md5 `5bce17ccabacea46d621d195c4600ebb`)
**Surveyed:** 2026-10-23 via [`tools/iso9660_extract.py`](tools/iso9660_extract.py) + [`tools/t5_survey.py`](tools/t5_survey.py)
**ISO deleted after verified extraction** (archived at Internet Archive).

## Disc files (10)

| Size | File | Format / Notes |
|------|------|----------------|
| 57 B | `SYSTEM.CNF` | PS2 boot config |
| 278 KB | `IOPRP300.IMG` | IOP modules |
| 305 KB | `IRXARC.BIN` | IRX module archive |
| 689 KB | `SLUS_210.59` | MIPS ELF bootloader. Loads `cdrom0:\TK5DATA3.BIN;1`. 522 strings. |
| 2.07 GB | `TK5DATA0.BIN` | Main data. Proprietary binary, no ASCII filenames. Entropy high. |
| 1.30 GB | `TK5DATA1.BIN` | Data. Proprietary binary. |
| 244 MB | `TK5DATA2.BIN` | **romD archive.** Magic `romD` @0. CRLF filename manifest (498 `.dat` motions, 109 char codes) + 21× `BDPK` section markers. |
| 423 MB | `TK5DATA3.BIN` | Bootloader-loaded. Proprietary binary. Extent 1646501. |
| 179 KB | `TK5DATA4.BIN` | MIPS EXEC ELF, no strings (secondary program/overlay). |
| 423 MB | `TK5DATA5.BIN` | **Duplicate of TK5DATA3.BIN** (same extent 1646501, same size). |

## TK5DATA2.BIN contents (romD)

**Motion manifest:** [`t5_motion_manifest.txt`](t5_motion_manifest.txt) — 498 unique `.dat` filenames.
**Char codes:** [`t5_char_codes.txt`](t5_char_codes.txt) — 109 codes with file counts.

Filename conventions:
- `gym_<code>_<motion>.dat` — character motion (e.g. `gym_amt3_kamae.dat` = stance, `gym_amt3_idling.dat` = idle)
- `snd_*.dat` — sound (`snd_c02lei.dat`, `snd_bg_blu_se.dat`, `snd_c_monst.dat`)
- `moj_*.dat` — text (`moj_stg02.dat`)
- `stgXX.dat` — stages (`stg00.dat`, `stg01.dat`, `stg02.dat`, `stg04.dat`)
- `cXXyyy.dat` — character sound (`c10jin.dat` = Jin, `c15hei.dat` = Heihachi, `c21jac.dat` = Jack, `c30dvj.dat` = Devil Jin)

Devil Within files: `gym_dw_nog00.dat`, `gym_dw_raribxk.dat`, `gym_dw_rarixk.dat`, `gym_djin_newhane00-03.dat`, `dwfkao00.dat`, `dwhadoh00.dat`, `dwup00.dat`.

## Extraction log

| Date | Action | Result |
|------|--------|--------|
| 2026-10-23 | Downloaded ISO (16-way parallel curl, md5-verified) | 4,039,974,912 bytes, md5 OK |
| 2026-10-23 | Extracted ISO (stdlib ISO9660 reader) | 10 files |
| 2026-10-23 | Surveyed containers + exe strings | romD identified, motion manifest extracted |
| 2026-10-23 | ISO deleted | Freed 3.76 GB |
