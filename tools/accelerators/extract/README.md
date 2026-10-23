# Stage 1 — EXTRACTION

> **ALL AGENTS — READ THIS FIRST.**
> Never download a full game onto this machine. Pull **only the paks you need**
> with `tools/depot-pull/` first, then extract from those. Read
> `../depot-pull/DISK-RULES.md` — every rule there applies here: `df` before
> you pull, extract/convert/delete, scratch outside the repo.

## What it does

Batch-extracts Unreal Engine game assets from `.pak` files into working
formats, a whole directory at a time:

- **repak** — unpack `.pak`/`.utoc`/`.ucas` (with AES key support)
- **umodel** (Gildor's UE Viewer CLI) — batch-export skeletal/static meshes to
  PSK, animations to PSA, textures to TGA/DDS
- **cue4parse-tool** — scripted listing + texture→PNG export via CUE4Parse

All three are **fetched on demand** into `extract/bin/` — nothing is vendored
in the repo.

## Quick start

```bash
./extract.sh install --umodel --cue4parse   # fetch repak + umodel + build the C# tool

# unpack every pak in a directory (AES key from the game's wiki/Discord)
./extract.sh unpack-dir /path/to/paks /path/to/work/s1 --aes <AES_KEY>

# batch-export meshes/anims/textures from the unpacked tree
./extract.sh umodel-export /path/to/work/s1 /path/to/work/s1-export --ue 5.3

# scripted: list what's inside before a big export
./extract.sh cue4parse list /path/to/paks --ue 5.3 --aes <AES_KEY> --filter "*SkeletalMesh*"

# scripted: textures straight to PNG
./extract.sh cue4parse export-tex /path/to/paks --ue 5.3 --aes <AES_KEY> --out /path/to/work/tex
```

## UModel notes (please respect the author)

- The native **Linux build of UModel is CLI-only** (no GUI) — ideal for this
  pipeline. Gildor asks that direct download links not be reposted, so this
  script does NOT hardcode his download URL: fetch the Linux build from
  https://www.gildor.org/projects/umodel yourself and set
  `UMODEL_BIN=/path/to/umodel`.
- Fallback: `install --umodel` fetches the Windows `umodel.exe` from Gildor's
  own GitHub repo (his FAQ points there for executables); it runs under `wine`.
- CLI flags used: `-path=`, `-game=` (see `ue-versions.txt`, or `umodel
  -taglist`), `-export`, `-out=`; `--extra` passes anything else through.
- Encrypted paks: **unpack with repak first** — UModel takes no AES key on the
  command line. Point `-path` at the unpacked tree.

## CUE4Parse tool notes

- Source lives in `cue4parse-tool/` (C# 12, net8.0). The build pins
  `CUE4Parse` to the release tag in `extract.sh` (`CUE4PARSE_VER`).
- v1 does listing + texture export. Mesh/animation *geometry* goes through
  UModel (above) — that's the batch workhorse; FModel on Windows covers the
  rest. This division is deliberate, not a gap.
- `DefaultFileProvider` scans a **directory** — point it at the folder holding
  the paks, not a single file.

## What comes out

`PSK`/`PSA` meshes+anims and textures, ready for Blender import (stage 3 rigs
them; `tools/anim-retarget/` has the UEFormat-path notes). Delete the unpacked
bulk once converted — DISK-RULES rule 3.
