# TTT2 — Inner File Listing (GoD game partition)

**Method:** streaming virtual-7z extraction (no 13.36GB reassembly).
**Source:** release `ttt2-7z-v1` (mhvnsnt/western-heart), GoD Title ID `4E4D0859` (Namco EU).
**Tool:** `teardown/tekken-tag-tournament-2/tools/ttt2_virtual_god.py`
**Date:** 2026-10-22

## Summary

- **Files: 78**
- **Directories: 2** (root + `$SystemUpdate`)
- **Total bytes: 8,402,073,168** (~8.40 GB)
- XDVDFS volume descriptor: **image sector 32** (byte `0x10000`); root table at sector 3231.

### Key format finding (2026-10-22, verified)

The GoD data stream is a **bare game partition** — `MICROSOFT*XBOX*MEDIA` sits at
image offset `0x10000`, i.e. sector 32 is the *game* partition's descriptor, not
the video partition's. Cross-confirmed by the xverter format notes (PyPI
`xverter` 1.4.0: "The embedded GoD stream is a bare game partition
(`MICROSOFT*XBOX*MEDIA` at `0x10000`) — XGD2 and XGD3 games both reduce to it")
and empirically on this image: sector 32 descriptor valid (magic at `[0:20]`
and `[0x7EC:0x800]`), root table walks clean.

The earlier XGD2-disc assumption (descriptor at sector 129856 =
`(0xFD90000+0x10000)//0x800`) is **wrong for GoD** — sector 129856 holds random
data, no magic; XGD3 disc offset `0x2080000` likewise does not apply (GoD
strips the disc layout). `ttt2_virtual_god.py` / `xdvdfs_reader.py` corrected
accordingly.

### Verification

Two independent methods agree exactly:
1. XDVDFS binary-tree walk (`xdvdfs_reader.py`, layout per xdvdfs-core) → 78 files.
2. Linear raw scan of the root directory table (sector 3231) and the
   `$SystemUpdate` table (sector 3232) for filename patterns → same 78 names.

## Top-level layout

| Location | Files | Notes |
|---|---|---|
| `/` (root) | 46 | `Default.xex`, `nrfo.bin`, `nxeart`, `AvatarAssetPack`, 42× `dataNNN.bin` |
| `/$SystemUpdate` | 32 | Dashboard update payload (not game content) |

### Game data containers (`dataNNN.bin`)

42 Namco data archives, ~6.8 GB combined. Numbering is **not contiguous** —
`data020`–`data024`, `data029`–`data033`, `data048`–`data049` are genuinely
absent from the disc (confirmed by raw table scan, not a walk artifact).
Largest: `data027.bin` (613 MB), `data017.bin` (356 MB), `data001.bin` (386 MB).

Per-fighter/per-stage content lives *inside* these Namco containers (magic
bytes TBD in Phase 2 — no format names claimed without them).

## Full listing

See `ttt2-inner-listing.json` — one row per file: `path`, XDVDFS data `sector`,
`size` in bytes. Sectors are image sectors of the bare game partition
(readable via `GodPackage.read_sector` with the probed layout
`base=0x2000`, `lead=0`).
