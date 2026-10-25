# TTT2 surgical extraction toolkit

Stream-extracts members from the `ttt2-7z-v1` release (26 split parts,
13.36GB total) **without downloading the whole archive**. Built 2026-10-23
after the VM's egress proxy throttled sustained downloads to ~0.1 MB/s —
the full 13.36GB pull is a ~12h+ job, so every script here works
surgically: fetch the 7z end-header (~2KB over HTTP Range), then decode
only the stream prefix needed for the wanted members.

## How it works

The release parts concatenate to one 7z file (`Tekken Tag Tournament 2.7z`,
13,363,624,393 bytes — byte-identical to the Archive.org item
`tekken-tag-tournament-2_202609`). The 7z holds **one LZMA folder**
(lc=3, lp=0, pb=2, 8MB dict) with all 72 data files concatenated in header
order:

| header idx | member | size |
|---|---|---|
| 0–6 | `00000002/` STFS blobs, stream order: 155MB / 80MB / 51MB / 358MB / 2.03GB / 79MB / 1.94GB | ~4.7GB |
| 7–18 | `00009000/` title-update files (12×, ~3.1MB) | ~3.1MB |
| 19 | GoD container descriptor `392CFF5C9DB17CCAEBC3` | 45,056 |
| 20–71 | GoD data `Data0000`…`Data0051` (52 × 170,459,136) | ~8.86GB |

Because it is one LZMA stream, member N can only be decoded by streaming
from byte 32 through the end of member N's data. `stream_decode.py` does
exactly that over HTTP Range and writes only the wanted members.

## Scripts

- **`fetch_assets.py`** — downloads release assets via the GitHub data API
  (`Accept: application/octet-stream` + surrogate credential; follows the
  302 to the signed URL *without* auth). Resume-safe via `Range`.
  `python3 fetch_assets.py <destdir> [name,...]`
- **`vfile.py`** — `PartVirtualFile`: seekable read-only virtual file over
  the 26 parts via HTTP Range. Lets `py7zr` parse the 7z end-header with
  ~2KB of transfer, and `member_table()` (in `stream_decode.py`) reads
  header order + uncompressed sizes from it.
- **`stream_decode.py`** — the workhorse. `python3 stream_decode.py
  <outdir> <idx> [<idx>...]` — LZMA-decodes the stream from offset 32,
  splits members by known uncompressed sizes, writes only `member_<idx>.bin`
  + `MANIFEST.txt` (sizes + sha256). Indices are header order (see table).
- **`seg_dl.py`** — parallel segmented download of an absolute byte range
  of the concatenated stream: `python3 seg_dl.py <start> <end> <nworkers>
  <outdir>`. Resume-safe per segment. For pre-staging a stream prefix to
  local disk so `stream_decode.py`-style passes can re-run without network.
- **`extract_member.py`** — `python3 extract_member.py <7z-member-path>
  <out>` — single-member extract via py7zr over `vfile.py`. Fine for
  members near the stream start; deep members re-stream from byte 32
  (slow) — prefer `stream_decode.py`.
- **`fetch_zarmanager.py`** — fetches `core/xbox/god.py` + `core/xbox/stfs.py`
  (GodPackage/STFS readers, stdlib-only) from `dfdx047/ZarManager`.
  Not vendored: upstream license unverified.

## Provenance / verification

- 2026-10-23: `vfile.py` + py7zr parsed the end-header over HTTP Range
  (1,970 bytes fetched): **80 entries, byte-matching `INVENTORY.md`**.
- 2026-10-23: member 19 (GoD header, 45,056 bytes) extracted via the
  stream path and **byte-matched** the known-good copy in
  `extracted-small/`.
- 2026-10-23: member 0 (155MB STFS blob) stream-decoded; STFS geometry
  validated with `StfsPackage.describe()`.

## Requirements

- Python 3.10+, `py7zr`, `requests` (`pip install py7zr requests`)
- The `custom.github_pat` connector (for `fetch_assets.py` /
  `fetch_zarmanager.py` credential surrogate)

## Cost model (at ~0.1 MB/s egress)

| target | stream prefix to decode | ~time |
|---|---|---|
| member 2 (51MB blob) | 287MB | ~50 min |
| member 0 (155MB blob) | 155MB | ~26 min |
| member 19 (GoD header) | 4.7GB | ~13 h |
| member 20 (`Data0000`, XDVDFS vol desc + root table) | 4.9GB | ~14 h |
| full archive | 13.36GB | ~38 h |

`Data0000` is the key to the XDVDFS file listing (volume descriptor at
image sector 32 + root directory table), which maps every inner file to
its `DataXXXX` chunk — after that, character pulls (Law/Lars priority)
need only their own chunks. See `../EXTRACTION-RUNBOOK.md`.
