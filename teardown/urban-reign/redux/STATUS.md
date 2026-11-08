# Urban Reign Redux — fetch status: GOT IT (Mod Manager + Editor, author's GitHub release)

**Date:** 2026-11-08 ~01:55 CST
**Task:** get Urban Reign Redux v0.5 NOW — Jay ordered an alternate link after the author's Drive link hit quota.
**Result: GOT IT — via the author's own GitHub release, not a mirror.** Full inventory: [INVENTORY.md](sandbox://workspace/urban-reign-redux/INVENTORY.md)

## What is on disk (hash-verified)

- `Urban.Reign.Redux.Mod.Manager.0.5.V97.zip` — 1,176,180,939 bytes, SHA-256 `ad222bad1d0cd1a03672bc88e0132e63ceb15ce0129a406b69b925ceb2f0f6d6` ✓ (matches author's published hash). Builds the byte-identical 0.5 disc from Jay's own Urban Reign (USA) ISO. 71 files: Launcher.exe, 3 `.urmod` payloads (core 0.5 mod + 2 HD texture packs), 34 fighter portraits, fight-scene art, guide, README, SHA256SUMS.json.
- `Urban.Reign.Redux.Editor.0.5.zip` — 54,476,021 bytes, SHA-256 `883387a9d3b78e7c38270697dfe46ddc72dc4958b062bbdb7e1c86f32cc3f7ef` ✓ (matches GitHub asset digest). 1,081 files: Editor.exe, Python 3.10 runtime, full editor + web source, and the `roster-lib` tooling (gyu_decode, vmd_mesh, ppk_index, texture tools, etc.).
- **Source (author's own):** https://github.com/Jasonafex/urban-reign-redux/releases (v0.5.0, Oct 28 2026).

## What is NOT on disk

- **The all-in-one ZIP (2.67 GB, SHA-256 `9b0c94b6…`) — no alternate link exists.** Searched 5 ways (ModDB, GameBanana, Mega, MediaFire, Reddit, Discord mentions, the package hash itself): nothing. The only source is the author's Drive link, re-checked 2026-11-08 ~01:52 — still "Google Drive - Quota exceeded". The 0.4 package (1.75 GB) is a different, older version — not a substitute, not downloaded.
- **Retry stays scheduled:** one-time job `urban-reign-redux-retry`, Sun Nov 8 ~7:18 PM CST, for the all-in-one Drive link.

## Caveats

- The Mod Manager Launcher is a Windows .exe — the disc build runs on Windows (Jay's PCSX2 machine), not this Linux VM. The files are here now; the build step is a Windows step.
- No piracy/ROM/leak sites used. No commercial ISO downloaded — Jay's own USA ISO is already in the repo (release `urban-reign-iso-v1`). No login/paywall bypass.
