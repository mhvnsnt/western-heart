# depot-pull — pull game files WITHOUT downloading the whole game

> **ALL AGENTS — READ THIS FIRST.**
> Never download a full game onto this machine. The VM disk has filled up before
> and blocked everyone's work. **Always pull only the files you need** using
> DepotDownloader's manifest/filelist filtering below. This applies to every
> agent on Western Heart and every chimera build pipeline. If your task needs
> game files, this directory is the way in — not `steamcmd`, not a full install.

## What lives here

- `depot-pull.sh` — wrapper: installs DepotDownloader, lists depot files, pulls
  only what matches your filelist.
- `paks-only.txt` — example filelist: pulls `*.pak` files only (the standard
  move for Unreal Engine games — models/animations live in the paks).
- `GAME-TARGETS.md` — app/depot IDs and exact pull commands per game.
- `DISK-RULES.md` — disk-budget rules. Read them. Follow them.
- `FMODEL.md` — FModel notes (Windows) + Linux-native alternatives
  (`repak`, CUE4Parse) for headless extraction.

## Quick start

```bash
# one-time: fetch DepotDownloader (standalone, no dotnet needed)
./depot-pull.sh install

# see what a depot contains (no download)
./depot-pull.sh list 1778820 1778821          # Tekken 8 main depot

# pull ONLY the pak files into ./t8paks  (requires owning the game on Steam)
./depot-pull.sh get 1778820 1778821 paks-only.txt ./t8paks <your_steam_username>
```

Then extract the paks (see `FMODEL.md`), convert to FBX/GLB, and **delete the
paks** when you're done with them.

## Why this exists

Full game downloads are 30–120 GB. The `.pak` files you actually need are a
fraction of that. Pulling per-file keeps the disk free for everyone and keeps
teardowns to hours, not days.
