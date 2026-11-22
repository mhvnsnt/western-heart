# MikuMikuLibrary — VF5 motion toolchain (vendored)

**Upstream:** https://github.com/blueskythlikesclouds/MikuMikuLibrary
**Pinned commit:** `82380f1e40bbcf07d19c4ac8d0bdb95845be3628` (master, 2026-04-22,
"Replace Position in IK bones with Rotation (#72)")
**Tarball sha256:** `c43022504a54f7096d7aa8c0ef0d6d5f800eaf5f912fd014efd342a12a305352`
(codeload `tar.gz/refs/heads/master`, 236,154 B, fetched 2026-11-21)
**Licence:** MIT, Copyright (c) 2023 Skyth — see `LICENSE.md`. SEGA owns VF5;
licence status never gated this pull (LICENCE-NOT-A-GATE), logged honestly here.
**Vendored:** 2026-11-21 by Lane 1A (VF5 complete teardown).

## What this is

Format library + file editor for Hatsune Miku: Project DIVA games. VF5 runs on
the same engine family, so the library also opens VF5 models, textures and
**motions** — it is the only public tool found (live search 2026-11-20 and
2026-11-21) that reads VF5 motion files. No pre-extracted VF5 motion dump
exists anywhere searched; this toolchain is the closest thing to a complete
VF5 motion teardown, and the route by which real Goh / Brad / Dural motion
can be produced from game files the owner already holds.

## What is vendored here (206 files, ~1.2 MB)

- `MikuMikuLibrary/` — the core format library (models, motions, databases,
  archives, textures). Motion parsing: `Motions/Motion.cs`,
  `Motions/MotionSet.cs`, `Motions/KeySet.cs`, `Databases/MotionDatabase.cs`.
- `CliTools/FarcPack/` — CLI: extract/create `.farc` (and CPK) archives.
- `CliTools/DatabaseConverter/` — CLI: convert `obj_db.bin`, `tex_db.bin`,
  `mot_db.bin`, `aet_db.bin`, `bone_data.bin` between binary and XML.
- `MikuMikuLibrary.Shared/` — shared project items.
- `LICENSE.md`, `README.md` (upstream).

Both CLI tools target **net8.0** and reference only
`MikuMikuLibrary.csproj` — no other project reference is needed to build them:

```
dotnet build CliTools/FarcPack/FarcPack.csproj
dotnet build CliTools/DatabaseConverter/DatabaseConverter.csproj
```

## What is NOT vendored (and why)

- `MikuMikuModel/` (254 files) — the Windows GUI. Not needed for extraction;
  the CLI tools are the extraction path.
- `MikuMikuLibrary.Native/` (C++ native lib + submodules DirectXTex,
  meshoptimizer, MikkTSpace) — needed only for FBX export / texture paths
  (native DLLs). FarcPack and DatabaseConverter do not need it. Prebuilt
  binaries are NOT vendored: build from upstream or take them from an
  upstream release (see README.md).
- No game files ship here. You must supply your own VF5 game files
  (owner owns VF5 on Xbox; PS3 dump in repo release `vf5-ps3-v1`).

## How VF5 motion extraction works with this

Per the upstream wiki ("Motions" section), a VF5 configuration needs 4 files:

| File | Location in a full game dump |
|---|---|
| `obj_db.bin` | `rom\objset` (already in release `vf5-ps3-v1`) |
| `tex_db.bin` | `rom\objset` (already in release `vf5-ps3-v1`) |
| `bone_data.bin` / `.bon` | `rom` |
| `mot_db.bin` / `.farc` | `rom\rob` |

Motion files themselves live in `rom\rob`, inside `.farc` files with the
`mot_` prefix. Steps once the full dump is available:

1. `FarcPack` — extract the `mot_*.farc` archives from `rom\rob`.
2. `DatabaseConverter` — convert `mot_db.bin` to XML: the motion inventory
   (every motion in the game, with IDs/names) for Goh (`goh`), Brad (`bra`)
   and Dural (`dur`).
3. Open a motion file in Miku Miku Model (or via the library) with the
   4-file configuration set, and export / port the motions.
4. Convert the exported motion to `wh-anim/1` via `tools/anim/` and land at
   `game/assets/anim/vf5/<fighter>/` with `skeleton.json` + `rows.pack.json`
   (per `docs/anim/VF5-DURAL-ANIM-GAP-20261023.md`).

## Status on this box

No .NET runtime is installed on the lane VM, so the CLI tools were **not**
run here. Vendoring is the toolchain pull (same pattern as the DOA6
Project-G1M + RDBExplorer pull, PR #1808): the tools are in the repo,
pinned and hash-verified, ready to run where .NET 8 is available.
The remaining work is the extraction run itself — see
`docs/research/VF5-COMPLETE-TEARDOWN-20261121.md` for the live-search
verdict and the exact open fork (whether motion files exist in the full
PS3 dump).

## Verification (own-eyes, this lane)

- Upstream repo: MIT, master `82380f1e…`, pushed 2026-04-22 (GitHub API).
- Tarball sha256 matches the file fetched (see above).
- Vendored file count 206; `Motions/` (8 files) and `Databases/`
  (`MotionDatabase.cs` present) confirmed by listing after extraction.
- No binary files in the vendored subset (all text source).
