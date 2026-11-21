# RDBExplorer — vendored (Dead or Alive 6 toolchain)

Utility for browsing, extracting, and modifying Koei Tecmo archive files
(`.rdb` + `.rdx`, `.fdata` / `archive_xx.bin`, `.lnk`). This is the DOA6
archive extractor: it opens the PC game's `root.rdb` and extracts the
`.g1m` / `.g1t` / `.g1a` / `.g2a` files that Project-G1M then reads.

Upstream: https://github.com/MrIkso/RDBExplorer — by MrIkso.
Licence: MIT License (MIT) — see `LICENSE.txt`.

## Version pinned

- Vendored source: upstream `main` at commit
  `22e72d8768092f8411480aaa7b8218c5003c8348` (246 files, 2,800,992 B).
- Upstream main tarball sha256:
  `842d4d5afc9af1d970dd573a37981e191d24011b48be2c0a97def35124fd6945`
  (fetched 2026-11-20; per-file sizes verified against the tarball listing).
- Upstream releases: 5 tags (latest v1.0.1). Prebuilt binary: fetch the
  release asset from https://github.com/MrIkso/RDBExplorer/releases —
  the exe itself is NOT vendored here (source-only pull; build it or take
  the release asset).

Note: the upstream README is Nioh-3-focused (`.fdata` / `.bin` / `.lnk`),
but the tool opens generic `.rdb` archives — SegadorMods' 2026 DOA6 /
DOA6 Last Round tutorial runs it on the real DOA6 `root.rdb` (extract +
inject, with readable names via `DoA6LR_names.csv`).

## Build

.NET 10.0, Windows 10/11. Solution `RDBExplorer.sln`. Includes the
vendored `Be.Windows.Forms.HexBox` (hex viewer control) and `PictureBox`
(image viewer) subprojects, as upstream ships them.

Two files are stored base64 in this vendored tree (binary originals; no
decoding was done on disk — they are consumed as base64 blobs):
`Be.Windows.Forms.HexBox/HexBox.bmp` and
`Be.Windows.Forms.HexBox/HexBox.snk`. Every other file is plain source.

## Use (DOA6)

1. File → Open → select `root.rdb` (keep its `.rdx` in the same folder).
2. Settings → Preferences → Rdb Names Database Path → select
   `DoA6LR_names.csv` (from SegadorMods' tutorial post — see
   `teardown/doa6/SOURCES.md`; not vendored here) for readable names.
3. Search by name/hash, filter by type. Right-click → Extract Selected
   (or Tools → Extract All). Enable "Export With Name" first so files
   keep their real names.
4. Right-click → Inject New Data replaces a file inside the archive.
   Double-click a file to preview it (texture viewer + model viewer
   included — the model previewer builds on Joschuka's Project-G1M
   research).

## Formats the tool understands

`.rdb` archives, `.bin` archives (manifest-based unpack/pack), locales
(unpack to / pack from `.csv`), and parsers for `g1co`, `g1mx`, `ktid`,
`lsqtree`, `mtl`, `kidsobjdb`, `oboro`, `oid`, `oidsq`, `grp`, `grbf`,
`sid`, `texinfo`, `kts` — plus a simple game-script decompiler and a
`.g1t` texture extractor/editor. See upstream `Formats.md`.
