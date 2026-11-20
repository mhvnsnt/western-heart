# TTT2 Extraction Runbook

**Goal:** 100% extraction of the TTT2 Xbox 360 package (release `ttt2-7z-v1`)
— full 59-fighter roster, stages, audio — with **Law and Lars first**
(their modern movesets/animations unblock the Buffalo Bill / Chordz pull lane).

**Standing laws:** T3 is fallback-only (instruction gate, 2026-10-23) — every
pull here is TTT2-native. No game binaries in the repo tree (owner law) —
large artifacts go to GitHub Releases; the repo carries tools, manifests,
and docs only.

## Where things stand (2026-10-23)

- [x] Archive inventoried (INVENTORY.md, 80 entries, per-file CRC32) — 2026-10-13
- [x] Roster/stage manifests documented from public data (ROSTER.md, STAGES.md)
- [x] Small files extracted (extracted-small/, 2.9MB) — avatar DLC only, no game metadata
- [x] Release `ttt2-7z-v1` holds all 26 parts + loose tar (13.5GB) — safe storage done
- [x] **Surgical extraction pipeline built** (`tools/surgical/`) — 7z end-header
      parsed over HTTP Range (80 entries verified vs INVENTORY.md); GoD header
      stream-extracted and byte-matched to `extracted-small/` copy
- [ ] `00000002/` STFS blobs listed/extracted (member 0 decoding 2026-10-23)
- [ ] `Data0000` → XDVDFS volume → full inner file listing
- [ ] **Law/Lars character data carved** (models, movesets, animations, stances, win poses)
- [ ] Remaining 57 fighters, stages, audio banks

## The pipeline

```
release parts (26×) --HTTP Range--> vfile.py --py7zr--> 7z end-header
       |
       +--stream_decode.py--> LZMA stream --> member_<idx>.bin (only wanted)
       |
       +--fetch_zarmanager.py--> core/xbox/{god,stfs}.py
       |
       +--god.py GodPackage + xdvdfs_reader.py--> inner file listing --> carve
```

Full usage: [`tools/surgical/README.md`](tools/surgical/README.md).

## Step-by-step

### 1. Stage the tooling (one-time per machine)

```bash
pip install py7zr requests
cd teardown/tekken-tag-tournament-2/tools/surgical
python3 fetch_zarmanager.py ~/tools/zarmanager   # GodPackage/StfsPackage
export PYTHONPATH=~/tools/zarmanager:$PYTHONPATH
```

### 2. Verify the archive header (fast, ~2KB transfer)

```bash
python3 - <<'EOF'
import sys; sys.path.insert(0, '.')
import fetch_assets, vfile, py7zr
vf = vfile.PartVirtualFile(fetch_assets.ASSETS[:26])
with py7zr.SevenZipFile(vf, mode='r') as z:
    print(len(z.getnames()), 'entries')   # expect 80
EOF
```

### 3. Extract the STFS blobs (indices 0–6)

```bash
python3 stream_decode.py ./blobs 0 1 2 3 4 5 6
python3 - <<'EOF'
import sys; sys.path.insert(0, '.'); sys.path.insert(0, '/path/to/zarmanager')
from pathlib import Path
from core.xbox.stfs import StfsPackage
for i in range(7):
    with StfsPackage(Path(f'blobs/member_{i:02d}.bin')) as pkg:
        files = pkg.files()
    print(f'blob{i}: {len(files)} entries')
    Path(f'blobs/blob{i}-listing.txt').write_text(
        '\n'.join(f'{e.path}\t{e.size}' for e in files))
EOF
```

### 4. Extract Data0000 → XDVDFS listing (the long pole)

`Data0000` is header index 20; decoding it needs the ~4.9GB stream prefix
(all 7 blobs + small files + GoD header first). At throttled egress this is
an overnight background job — run it with `nohup`:

```bash
nohup python3 stream_decode.py ./god 20 > god-20.log 2>&1 &
```

Then map sectors and walk the filesystem:

```bash
python3 - <<'EOF'
import sys; sys.path.insert(0, '.'); sys.path.insert(0, '/path/to/zarmanager')
sys.path.insert(0, '..')  # for xdvdfs_reader
from pathlib import Path
from core.xbox.god import GodPackage
from xdvdfs_reader import XdvdfsReader
pkg = GodPackage(Path('extracted-small/392CFF5C9DB17CCAEBC3'))
pkg._read_header()
pkg.data_files = [Path('god/member_20.bin')]  # + more as extracted
pkg.layout = pkg.probe()
rdr = XdvdfsReader(pkg.read_sector)
files = rdr.list_files()
Path('xdvdfs-listing.txt').write_text(
    '\n'.join(f'{s}\t{p}' for p, _, s in sorted(files)))
print(len(files), 'inner files')
EOF
```

### 5. Carve Law / Lars (priority)

In the XDVDFS listing, look for the character packages (Tekken 6-family
naming; match case-insensitively):

```bash
grep -i -E 'law|lars' xdvdfs-listing.txt
```

For each hit note its sector range → `DataXXXX` index
(`sector // 0x14388` adjusted by `layout.lead_sectors`). Extract exactly
those Data members with `stream_decode.py` (indices 20+N), re-run the
XDVDFS walk with all extracted Data files present, and pull the character
files with `XdvdfsReader.read_file_to()`.

Expected per-character bundle: model package(s), move-list binary
(moveset), animation set, stance/idle, win poses, voice bank refs.
Document the bundle layout in `roster/<fighter>/MANIFEST.md` and upload
binaries >50MB to a new GitHub Release (never the repo tree).

### 6. Continue the roster

Repeat step 5 per fighter (ROSTER.md order). Stages: `stg00`–`stg48` ids in
STAGES.md. Audio: XMA banks — decode to WAV/OGG for the voice/music lanes.

## Cost model

VM egress is proxy-throttled (~0.1 MB/s sustained, 2026-10-23). Full
13.36GB pull ≈ 38h — hence surgical. Per-member prefix costs are in
`tools/surgical/README.md`. Prefer `nohup` + resume-safe scripts for
anything over ~200MB.

## What NOT to do

- Do not `git add` extracted game binaries — owner law (no copyrighted /
  leaked game files in the public repo). Releases only.
- Do not pull from Tekken 3 for this lane — T3 is fallback-only; log any
  T3 use per the instruction gate.
- Do not commit from a sparse checkout (NO-SPARSE-COMMIT LAW) — push via
  the Git Database API pattern (`tools/surgical` docs reference the
  established `push_branch.py` flow).
