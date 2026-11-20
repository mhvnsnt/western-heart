# Western Heart — Chimera Teardown

This is the reverse-engineering source material for the Western Heart Chimera Build.
Per `CHIMERA-BUILD.md` (repo root): the game is built by tearing down five games
and recombining their systems. Every piece of the game traces back to a
reverse-engineered source file in this directory. Steal like an artist — all of it.

## The five games

| Dir | Game | Chimera role |
|---|---|---|
| `tekken7/` | Tekken 7 | Primary base — King model extraction, roster mapping, modding docs |
| `tekken3/` | Tekken 3 | Legacy/retro mode — BNS motion data, TIM textures, disc layout, decomp project |
| `wwf-no-mercy/` | WWF No Mercy (N64) | Wrestling systems + customization — character data, wrestler ID table, decomp |
| `wwe-wrestlemania-xix/` | WWE WrestleMania XIX (GCN) | Modes + arena traversal — file listing, GCN/Yukes format tools |
| eastern-mind | Eastern Mind (Osamu Sato) | Stages/lore — NOT YET PULLED (download never confirmed; lane pending) |

Plus:
- `PLAYBOOK.md` — reverse-engineering playbook (how teardowns are done here)
- `western-heart-design/` — the teardown lane's design output
  (`stages.md`, `systems.md`, `technical-plan.md`, `asset-manifest.md`,
  King-from-Tekken-3 reference images).
  Note: `WESTERN-HEART-DESIGN.md` and `roster.md` from that lane are byte-identical
  to the repo's `DESIGN.md` / `ROSTER.md`, so they live only at the repo root.

## What's NOT in here (and why)

`TEARDOWN-SOURCES.md` lists every excluded binary with its local path, size, and
SHA-256 so any of it can be re-acquired and verified. Excluded categories:

- **Raw disc/ROM binaries over GitHub's limits** — the WMXIX ISO (1.4 GB), the
  Tekken 3 ROM zip (471 MB), TEKKEN3.XAS stream (488 MB), No Mercy ROM + zip.
  The extracted *knowledge* from them (docs, mappings, JSON inventories) IS here.
- **Third-party tool bulk** — `tekken3recompiled/mods/assets` (144 MB of the
  tool's own asset pack; the decomp source itself IS here under
  `tekken3/tools/tekken3recompiled/`).
- **Superseded build intermediates** — early `pantera*.glb` builds (the final
  `pantera_rigged.glb` is at `roster/pantera/`), old `views/` renders.
- **Pantera arena build sources** (`tekken7/king/arena/`) — build-lane work;
  its outputs are at `roster/pantera/showcase/`.

## Working source

The live working copies stay at `~/workspace/game-reverse-engineering/` (never
deleted). This directory is the curated best-of snapshot pushed to the repo.
