# Dead or Alive 6 — Teardown

Owner order (2026-11-20 ~19:27 EST, verbatim substance): "Instead of buying
those games, just go get like the Teardown moves. I have I own those games on
Xbox. Just go get like the already tore down and decomped and already like
don't start it from scratch. Go get like the mod and fan tear down and
decomped and extracted stuff stuff that already has the code and stuff
cracked."

This directory is the DOA6 teardown home. It holds the already-cracked fan/mod
extraction toolchain, pulled in whole, and the wiring that turns DOA6 game
files into Western Heart moveset/animation data.

## What is cracked (and what is not)

CRACKED — the full extraction chain, public and working:

1. The PC game ships as `root.rdb` (+ `root.rdx` index). `RDBExplorer`
   (MrIkso, MIT) opens it, lists every file by hash/name, and extracts or
   injects any entry. See `../tools/anim/doa6-rdbexplorer/README.md`.
2. Inside are Katana-engine files: `.g1m` (models), `.g1t` (textures),
   `.g1a` / `.g2a` (skeletal animations). `Project-G1M` (Joschuka, GPL-2.0)
   is a native Noesis plugin that views and exports all four, including
   most G1A/G2A skeletal animations. See
   `../tools/anim/doa6-project-g1m/README.md`.
3. The chain is proven on DOA6 by the community: Joschuka's 2020 thread
   lists Dead or Alive 6 among the supported games, DOA6 models were tested
   extensively after the last updates, and SegadorMods' 2026 DOA6 / DOA6 Last
   Round tutorial runs RDBExplorer on the real `root.rdb`.

NOT YET HERE — extracted DOA6 moveset/animation DATA. No complete public
DOA6 moveset or animation dump exists in a WH-usable form (see SOURCES.md
for everything searched). What exists publicly is either per-character
GTA: San Andreas conversions (wrong format, partial — see SOURCES.md) or
community movelist/frame-data text (already the basis of the existing
`game/assets/movesets/doa-*.json` kits, which ship NO animation clips).
Running the vendored toolchain against PC game files is the remaining step.

## Pipeline (run on Windows, needs the PC game files)

```
Dead or Alive 6 (PC) install
  └─ root.rdb + root.rdx
       └─ RDBExplorer → extract .g1m / .g1t / .g1a / .g2a  (names DB: DoA6LR_names.csv, see SOURCES.md)
            └─ Noesis + ProjectG1M.dll → open .g1m (model) / .g1a/.g2a (animation) → export FBX
                 └─ WH animation bank / moveset kit (same shape as the T7/T8 flow in tools/anim/tkmovesets2/)
```

Game-file source: the owner owns DOA6 on Xbox. The PC game is on
archive.org (raw full game + updates, see SOURCES.md) but was NOT pulled
here — 62 GB of raw game is not a teardown, and this lane pulls torn-down
work, not raw games. A future lane runs the toolchain against PC files
when they are staged.

## Layout

- `README.md` — this file (pipeline + status).
- `SOURCES.md` — every source searched, with licence, hashes, and what was
  / was not pulled and why.
- `../tools/anim/doa6-project-g1m/` — Project-G1M source, vendored whole.
- `../tools/anim/doa6-rdbexplorer/` — RDBExplorer source, vendored whole.

## Relation to the existing DOA kits

`game/assets/movesets/doa-kasumi.json`, `doa-bass.json`, `doa-hayabusa.json`
(16/18/14 moves) are converted community movelist/frame-data text
(SuperCombo Wiki, GameFAQs, fandom — see
`docs/movesets/DOA-VF-CONVERSION-2026-10-19.md`). They carry `anim_ref`
values (`doa:bass/palm-jab`, …) but ship no animation clips. The toolchain
in this PR is what finally lets those refs resolve to real G1A clips: extract
the character's `.g1a` set, export via Noesis, and map clip → `anim_ref`.
DOA4 (`anm.afs` format unknown) is a separate, still-open gap and is NOT
covered by this toolchain.

## Licence note

Licence never gates pulling (owner law). Project-G1M is GPL-2.0,
RDBExplorer is MIT — both logged in SOURCES.md next to their sources.
