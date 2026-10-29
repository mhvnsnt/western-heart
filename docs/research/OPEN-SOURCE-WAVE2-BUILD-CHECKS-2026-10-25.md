# Open-source wave-2 — build checks — 2026-10-25 (Phase 3 execution)

Companion to `docs/research/OPEN-SOURCE-WAVE2-2026-10-24.md` (which
already records the per-item licences). This note records ONLY what
the Phase 3 execution lane actually built or attempted on 2026-10-25.
It does not re-record licences, and it does not change any
disposition in the wave-2 doc.

## Licence re-verification (this lane, against the pulled files)

Re-read from `~/workspace/opensource/` clones on 2026-10-25; all seven
match the wave-2 doc exactly — no correction needed:

- assimp: BSD-3-Clause (assimp team, 2006–2026).
- fbx2gltf: BSD-3-Clause (Facebook, Inc.) — the earlier
  "Apache-2.0" label stays corrected.
- webgpu-cloth-jspdown: MIT (Harold Ozouf, 2023).
- webgpu-cloth-nakjun: NO LICENSE STATED — no LICENSE file, no
  license field in package.json (`private: true`), no license
  statement in the README. Reference-only; NOT labeled MIT, Apache,
  or anything else. Gap carried, never papered over.
- filediver: BSD-3-Clause (Copyright 2026 Filediver contributors).
- godot-shinobi-arena: NO LICENSE STATED — no LICENSE file, no
  license statement in the README. Reference-only. Gap carried.
- godot-topdown-template: MIT (Stefano Mercadante 2025; bundled
  Dialogue Manager / TileBitTools parts carry their own MIT notices).

## Build check 1: filediver — BUILD PASS, binary runs

- Toolchain: Go 1.25.1 (official tarball, unpacked to scratch;
  the box had no Go installed).
- Command: `go build -o filediver-cli ./cmd/filediver-cli` in the
  filediver clone (go.mod: `go 1.25.0`).
- First attempt failed ONLY on disk space: Go's default temp dir
  is the 512 MB tmpfs `/tmp`, which filled. Re-run with
  `GOTMPDIR`/`GOCACHE` pointed at workspace scratch: BUILD PASS.
- Binary: 33,227,209 bytes; `--help` runs and prints the
  filediver CLI help (Helldivers 2 game asset extractor,
  `https://github.com/xypwn/filediver`).
- Pipeline meaning: the `.bnk`-container gap step (extract embedded
  `.wem` with a filediver build, then decode with
  `tools/audio/wem-decode.sh` via vgmstream-cli) is now proven
  buildable from the pulled source. The binary itself is NOT
  committed — the repo keeps the pipeline note, not a 33 MB blob.

## Build check 2: fbx2gltf — configure reaches the Conan wall (BLOCKED, exact reason)

Steps actually run, in order:

1. CMake configure on the bare clone: FAILS — `Can't find FBX SDK`
   (no `sdk/` dir in the clone). This is the documented state.
2. FBX SDK 2019.2 fetched from the README's own URL
   (`zellski/FBXSDK-Linux` 2019.2 tarball, 42 MB) and extracted
   into a scratch copy of the clone (workspace clone untouched).
   SDK libs ship zstd-compressed; `zstd` was installed via apt
   (1.5.5) and 399 files decompressed (263 MB).
3. CMake configure re-run: FBX SDK 2019.2 FOUND
   (`include/`, `lib/gcc/x64/release/libfbxsdk.a`), then stops at
   `CMakeLists.txt:37` — "The Conan package manager must run
   ('install') first."
4. Conan 1.66.0 installed via pip (the project's conanfile era).
   First conan install failed on TLS (egress proxy cert chain);
   fixed by pointing Conan's `cacert.pem` at the system bundle
   plus the egress CA. Then the REAL blocker surfaced:
   `ERROR: Unable to find 'boost_filesystem/1.69.0@bincrafters/stable'
   in remotes` — the 2019-era Bintray/bincrafters recipe reference
   is dead on conancenter.

- Result: fbx2gltf does NOT build on this box today, for a named
  dependency reason, not a skipped step.
- Unblock path: port `conanfile.py` to current Conan Center
  references (boost, fmt, nlohmann_json, cli11, stb) or vendor the
  deps; do not fake a binary. Until then the documented fallback
  stands: Blender FBX→GLB, with every GLB through
  `tools/glb-tools/validate.mjs` first.
- No prebuilt binary was relied on (GitHub releases API returned
  no latest tag at scout time, and none was fetched here).

## Build check 3: assimp binary — VERIFIED PRESENT AND WORKING

- Before this lane: no `assimp` binary on the box (the wave-2
  doc's "unverified" state was correct).
- Installed via apt: `assimp-utils 5.3.1+ds-2build1`.
- Proof: `assimp info` on the wave-1 smoke GLB imports cleanly
  (1 node, 1 mesh, 1 material, 0 animations, import OK).
- Pipeline meaning: "verify a working assimp binary before
  pipeline use" is now satisfied for this box. The 383 MB assimp
  source clone stays out of git, as the wave-2 doc directs.

## What is still owed (not hidden)

- fbx2gltf full build (Conan port above) — pipeline owner step.
- Kaggle T4 runs for `tools/gpu/` (see `tools/gpu/KAGGLE_RUNBOOK.md`).
- Blender addon headless-enable tests (see
  `customization/OPEN-SOURCE-CREATION-RUNBOOK.md`).
- Live-build play verification for VFX/cloth (parent browser
  delegation, after merge + deploy).
- nakjun + godot-shinobi-arena licences: still unstated —
  reference-only until their authors state one. No derived code
  from either is shipped by this lane.
