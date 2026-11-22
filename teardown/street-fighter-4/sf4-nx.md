# sf4-nx — Street Fighter IV (Xbox 360) static-recomp port to Switch

Record only — the source is NOT vendored in this repo. Read why below.

## Source

- Repo: `jvankooo/sf4-nx` — "xbox360 port of Street Fighter IV on the
  nintendo switch"
- URL: https://github.com/jvankooo/sf4-nx
- Licence: GPL-3.0
- Created: 2026-10-22. Default branch `main`, tip commit
  `06cd530bca8e5dbbebe609c09f2183070ab05273`, pushed 2026-10-23.
- Commits: 11. Stars: 8. Forks: 0.
- Release: v0.1.0 "SF4 for Switch v0.1.0" — `sf4-nx.nro` (42,723,126 B)
  + `sf4.toml` (7,608 B).

## What it is

Static recompilation: `default.xex` (PowerPC) → ReXGlue → C++ →
devkitA64 → Switch `.nro`; the game's GPU command buffers are drawn
natively with Vulkan (NVK); Xenos shaders are translated ahead of time
with XenosRecomp + DXC. No game files are included — it needs the
owner's own Street Fighter IV Xbox 360 disc (World edition, `.iso` or
extracted disc). A browser installer builds the SD-card folder from the
disc locally (nothing uploaded).

## Evidence it works

- README claims full speed, 30 fps locked (game logic 60 steps/sec),
  menus/HUD at 1280×720, HD Rumble, Bink cutscenes, XMA music/voices.
- Release v0.1.0 shipped with a built `.nro`; README shows Ryu vs Ken
  and Balrog vs Dan screenshots.
- It is a port framework, NOT a moveset/animation extraction: the
  generated C++ and shader library are explicitly NOT committed
  ("Nothing derived from the game … is committed").

## Why it is recorded, not vendored

1. Size/shape: full tree is 29,698,523 B across 1,677 files. The bulk
   is generic shared runtime, not SFIV-specific: `sdk/` alone is
   1,038 files / 24,117,934 B (ReXGlue runtime shared with
   masseffect-nx); `shaders/` is 374 generated header files.
   The SFIV-specific parts are `app/` (167 files, 3,228,206 B),
   `docs/` (27 files, 610,328 B), `installer/` (28 files, 519,161 B),
   `tools/` (36 files, 167,848 B) plus root docs.
2. No game-derived content is in the repo at all — vendoring it would
   add a 30 MB generic SDK without adding a single moveset, animation,
   or model.
3. Transport: `git clone` / codeload zip download are blocked from this
   box (codeload returns HTTP 200 with 0-byte files); the only working
   path is the Git Data API, one blob per call — 1,677 calls is not a
   sane pull for a framework whose value to Western Heart is reference
   only.
4. It still needs the owner's Xbox 360 disc to produce anything; the
   owner owns SFIV on Xbox, so the path stays open: fetch this repo
   from the URL above and run its browser installer against the disc.

## How to fetch it later

- `git clone https://github.com/jvankooo/sf4-nx.git` (from a machine
  where git HTTPS works), or download the v0.1.0 release from
  https://github.com/jvankooo/sf4-nx/releases
- Docs that matter for RE reference: `docs/` (native renderer, shaders,
  performance history, platform notes, porting guide).
