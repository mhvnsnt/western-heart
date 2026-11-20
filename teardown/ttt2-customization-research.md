# TTT2 (Xbox 360) — Customization Research

**Lane:** tekken-mining (2026-10-16)
**Source:** `Tekken Tag Tournament 2 (EU)` Xbox 360 Games-on-Demand package, title ID `4E4D0859`
**Local:** `~/workspace/game-reverse-engineering/tekken-tag-tournament-2/`
**Status:** EXTRACTION BLOCKED — 7z reassembly stalled (see §5). Research + tool catalog complete.

---

## 1. What we have

- `chunks/Tekken Tag Tournament 2.7z` (5,767,168,000 bytes = 11 × 500MB parts — **truncated**,
  first 11 of 26 parts only; py7zr rejects it: archive header lives at EOF which is missing)
- `chunks/ttt2-500m.part_12` (156MB of 500MB — partial, download stalled)
- `HEADER-LISTING.txt` — GOD container structure (STFS title-update files + 52 DataXXXX entries)
- `tools/god_surgical.py` + `tools/xdvdfs_reader.py` — prior lane's surgical GOD→XDVDFS reader
  (extracts single files from the 7z without full reassembly; needs the COMPLETE 7z to function)

### GOD layout (from HEADER-LISTING.txt)
```
Tekken Tag Tournament 2 (EU)/
  4E4D0859/00007000/392CFF5C9DB17CCAEBC3.data/Data0000..Data0051  (52 × 170,459,136 bytes)
  0000000000000000/4E4D0859/00000002/<hash>...                    (GOD game partition)
  0000000000000000/4E4D0859/00009000/<hash>...                    (STFS title updates)
```
Data file geometry (per zarmanager's GOD reader): 0xA290000-byte files =
1 L1 hash block + 203 × (1 L0 hash block + 204 data blocks); 0x14388 sectors/file.

## 2. Known TTT2 asset formats (from tekkenmods-docs, local mirror)

`game-reverse-engineering/tekken7/tekkenmods-docs/files/en/Tekken_Tag_Tournament_2/`

| Ext | Description | Xbox 360 header |
|-----|-------------|-----------------|
| .nud | Namco Geometry (character/item models) | `NDXR` |
| .nut | Namco Texture | `NTXR` |
| .mvl | Movelist | ? |
| .alo | Effect file | ? |
| .pack | Unknown (likely archive container) | ? |
| .pam | Unknown | ? |
| .sqebin | Stage binary / `BONE` skeleton | `BONE` |
| (shader) | Shader file | `NSXR` |

Customization item models will be `.nud` (NDXR) + `.nut` (NTXR) files, plausibly
inside `.pack` archives or per-character directories once the XDVDFS tree is readable.

## 3. Open-source extraction tool catalog (researched 2026-10-16)

| Tool | Repo | License | What it does | Verdict |
|------|------|---------|--------------|---------|
| zarmanager | https://github.com/dfdevx2/zarmanager | **unknown — no LICENSE in checkout; verify before redistributing** | Pure-Python GOD/STFS/XISO/ZAR reader (GoD block geometry, hash tables) | **Already in use** — `god_surgical.py` builds on its `GodPackage`; covers our need |
| 360tools | https://github.com/sp00nznet/360tools | check repo (not pulled) | `extract_iso.py` (XDVDFS XGD1/XGD2), `extract_stfs.py`, `xex_info.py` | Evaluated, not pulled — overlaps zarmanager+xdvdfs_reader |
| XGDTool | https://github.com/wiredopposite/XGDTool | check repo (not pulled) | Convert Xbox discs to/from formats: `--extract`, `--god`, `--xiso`, `--list` | Evaluated, not pulled — CLI alternative if Python path fails |
| GODSend-360 | https://github.com/ghostyshell/GODSend-360 | check repo (not pulled) | Pure-Go ISO→GOD conversion, game manager | Evaluated, not pulled — ISO→GOD direction, we need GOD→files |
| ulbox360 | https://github.com/vladkioladki/ulbox360 (fork of alchichosz/ulbox360) | check repo (not pulled) | Rust: ISO→GOD, XISO unpack/pack, FATX FUSE | Evaluated, not pulled |
| SimpleXisoDrive | https://github.com/purelogiccode/SimpleXisoDrive | GPL-3.0 | FUSE/Dokan mount of XISO (XDVDFS-only) | Evaluated, not pulled — mount path not needed |
| pycdlib | pip `pycdlib` | **LGPL-2.1-or-later** | Pure-Python ISO9660 reader | **Pulled this lane** — used for Tekken 6 PSP ISO listing |

No DRM circumvention involved: GOD/XDVDFS are container formats, not encryption;
all tools above parse our own disc image's filesystem structures.

## 4. What to do once the 7z completes

1. `python3 tools/god_surgical.py --sevenz <full 7z> --work /tmp/ttt2god --list` → full XDVDFS tree
2. Hunt order: `*.pack` files → `.nud` (NDXR) character/item geometry → `.nut` (NTXR) textures
3. Document item record layout; **do NOT push extracted Namco models to this repo**
   (document format + offsets only, per lane rule)

## 5. Blocker — 7z reassembly stalled (NO-DROPPED-WORK surfaced)

- `chunks/reassemble.state` = `11` (11/26 parts appended); `part_12` partial at 156MB/500MB
- Last log activity 2026-10-15 20:58Z; **no reassemble process currently running**
- Resume path: `chunks/one_chunk_12.sh` (loops `gh release download ttt2-7z-v1
  --repo mhvnsnt/western-heart --pattern ttt2-500m.part_N`), owned by the reassemble lane
- This lane did NOT resume it (another lane's in-flight work; ~7GB remaining download = their disk budget call)
- `Tekken Tag Tournament 2.7z` (5.7GB) retained per NEVER-DELETE-GAME-FILES LAW

## 6. Still locked

- Inner XDVDFS file listing (needs complete 7z)
- Item definition records (names/slots/prices) and item `.nud` models
- Whether TTT2 item data lives in `.pack` archives or loose files
