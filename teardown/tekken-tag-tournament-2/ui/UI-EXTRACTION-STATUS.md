# Tekken Tag Tournament 2 (Xbox 360) — UI Asset Extraction Status

**Updated:** 2026-10-23 (UI sweep)
**Status:** 🟡 ARCHIVE MAPPED — surgical extraction infeasible; full-download path documented

## Archive layout (proven 2026-10-23 via 7z end-header parse over HTTP ranges)

**Archive:** `Tekken Tag Tournament 2.7z` — 13,363,624,393 bytes
(byte-exact vs Internet Archive `tekken-tag-tournament-2_202609`),
on release `ttt2-7z-v1` (26 × 500MB parts).

**Critical format fact:** the 7z is a **single 13.36GB solid LZMA2 block**
(1 folder, 72 files). Members in archive order:

| # | Member (suffix) | Unpacked | Solid offset |
|---|---|---|---|
| 0 | `00000002/3FADC8AF...` (title-data STFS) | 155,930,624 | 0 |
| 1 | `00000002/81048E1C...` | 80,576,512 | 155,930,624 |
| 2 | `00000002/869D8990...` | 51,015,680 | 236,507,136 |
| 3 | `00000002/86EC81D4...` | 357,920,768 | 287,522,816 |
| 4 | `00000002/98D464B9...` | 2,034,626,560 | 645,443,584 |
| 5 | `00000002/CA05E232...` | 79,253,504 | 2,680,070,144 |
| 6 | `00000002/FC2BA3B3...` | 1,942,929,408 | 2,759,323,648 |
| 7–18 | `00009000/00000544...` (12 DLC STFS) | 98KB–340KB | ~4,702,253,056 |
| 19 | `392CFF5C9DB17CCAEBC3` (GoD STFS header) | 45,056 | 4,705,165,312 |
| 20–71 | `392CFF5C9DB17CCAEBC3.data/Data0000–Data0051` | 52 × 170,459,136 | ~4,705,210,368+ |

**Consequence:** extracting ANY member past #0 requires streaming gigabytes
through the solid block. HTTP-range "surgical" extraction is **not viable**
for the GoD content (header at 4.7GB in). Verified: `py7zr` member extract of
the GoD header timed out after 300s; only ~2KB of header metadata is
range-readable.

## GoD STFS header parsed (from `extracted-small/`, in-repo)

`teardown/tekken-tag-tournament-2/extracted-small/392CFF5C9DB17CCAEBC3`
(45,056 bytes): magic `LIVE`, display name "TEKKEN TAG 2", description
"This is installed game. To play, insert the original game disc.", embedded
PNG thumbnail. **No inner file table** — GoD file metadata lives in the Data
chunks, so the XDVDFS file listing (and UI file locations) requires the Data
files, not just this header.

## 00009000/ DLC files — identified

12 STFS packages (98–340KB) = **Xbox Live avatar-item DLC bundles**
(each embeds PNG thumbnails). Already extracted to `extracted-small/`.
Not game UI.

## Title-data blobs (00000002/) — probing

7 STFS blobs (51MB–2.03GB, 2012 build mtimes). Blob #0 (`3FADC8AF...`,
156MB, solid offset 0) is the only cheaply streamable member; its STFS
listing was pulled 2026-10-23 — see below. Tools for the rest:
`teardown/tekken-tag-tournament-2/tools/stfs_blobs.py` (needs full 7z),
`xdvdfs_reader.py`, `god_surgical.py`.

### Blob #0 inner listing (STFS file table, parsed 2026-10-23)

### Blob #0 inner listing (STFS file table, parsed 2026-10-23)

Streamed 155,930,624 bytes via HTTP ranges (solid offset 0 — the only
cheaply-streamable member). STFS content type `0x2` (Marketplace Content).

| Inner file | Size | Format |
|---|---|---|
| `data011.dat` | 154,948,232 | `sarc` archive: 79 entries, 2× `NUS3` audio banks + opaque game data |
| `index.dat` | 49 | binary index |

**Verdict: no menu UI in blob #0** — it is DLC data (audio banks + game
blobs), not menu textures. The 6 other `00000002/` blobs sit at solid offsets
156MB–2.7GB (multi-GB streaming each — not viable this lane); the actual menu
UI lives in the GoD Data chunks (solid offset ~4.7GB in).

Parser: `~/workspace/ttt2-extract` tooling + Free60 STFS spec
(file table at `((HeaderSize+0xFFF)&0xF000)+0x1000` for block 0;
0x40-byte entries: name[0x28], flaglen, nblocks LE24, startblk LE24,
size BE32). Verified against the 12 avatar-item DLC packages
(`asset_v2.bin` + `icon.png` per package).


## Where the game UI lives

Character data, stage data, movesets, audio, and textures are all inside the
52 Data chunks + the 7 `00000002/` blobs — Xbox 360 STFS containers holding
Namco's in-house-engine formats (NOT UE4). **No plaintext manifest exists at
package level.** Per `TEARDOWN.md`: textures = Namco X360 texture containers,
audio = XMA banks, movesets = per-character binaries.

## Full extraction path (when scheduled)

1. Download 13.36GB via release `ttt2-7z-v1` (26 parts, `~/workspace/ttt2-extract/dl.py`)
   or IA `tekken-tag-tournament-2_202609` — ~27GB peak disk (archive + extract)
2. `7z x` the archive; walk GoD with `tools/xdvdfs_reader.py` /
   `tools/god_surgical.py --list`
3. Pull UI texture containers → convert X360 textures → land in
   `teardown/tekken-tag-tournament-2/ui/` via branch + PR (large files to Releases)

## Already landed

- `extracted-small/` — 13 sub-10MB files (GoD header + 12 avatar DLC), 2.9MB
- `HEADER-LISTING.txt`, `INVENTORY.md`, `ROSTER.md`, `STAGES.md`, `TEARDOWN.md`
