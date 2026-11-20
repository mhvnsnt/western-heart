# Research: Kenney.nl accessory packs (CC0)

## What it is
Kenney (kenney.nl) publishes hundreds of game asset packs under **CC0 1.0 Universal**.
Several 3D packs contain equippable-style props directly usable in the Western Heart
Creation Suite's 16 equipment slots (extra/weapons, head, etc.).

## Where from
- Pack index: https://kenney.nl/assets
- Direct downloads are content-hashed zips, e.g.
  `https://kenney.nl/media/pages/assets/<slug>/<hash>/kenney_<slug>.zip`
- Canonical URL+SHA256 manifest used for verification: `MIRROR.toml` in
  zhanghandong/makepad (`apps/arcade/resources/MIRROR.toml` at commit
  5f83480ae3fc8b76d4017ec50befe040c1d222ab) — 50 packs with upstream
  kenney.nl URLs and sha256. Only used to *locate* canonical URLs; bytes were
  fetched from kenney.nl and hash-verified.

## License
CC0 1.0 Universal (public domain). `License.txt` ships in every pack zip.
No attribution required. Owner pre-approved 2026-10-16.

## Why pulled
Highest-value accessory gap: handheld weapons for the Creation Suite `extra` slot.
Kenney ships single-file GLB (`Models/GLB format/`) — our pipeline consumes GLB
directly, no conversion needed.

## What was pulled (2026-10-16)
| Pack | Kept | Skipped (why) |
|---|---|---|
| Blaster Kit | 18 blasters + 2 grenades (20 GLB) | targets/crates/clips/scopes/silencers/smoke (not equippable) |
| Survival Kit | 10 hand tools: axe/hammer/hoe/pickaxe/shovel +upgraded (10 GLB) | camp/architecture/nature (not equippable) |
| Mini Arena | weapon-sword, weapon-spear, trophy, banner (4 GLB) | arena architecture |
| Pirate Kit | 0 — **no hats/accessories**, ships+cannons only | n/a |
| Castle Kit | 0 — architecture only | n/a |
| Retro Fantasy Kit | 0 — architecture only | n/a |

## Where landed
- `game/assets/accessories/kenney-blaster-kit/` (20 GLB + LICENSE-CC0.txt + README.md)
- `game/assets/accessories/kenney-survival-kit/` (10 GLB + LICENSE-CC0.txt + README.md)
- `game/assets/accessories/kenney-mini-arena/` (4 GLB + LICENSE-CC0.txt + README.md)

## Notes / follow-ups
- HATS still open: Kenney has no dedicated hat pack; Pirate Kit has no hats.
  Next: KayKit Adventurers (CC0, helmets/hoods on characters — characters are a
  separate tier), Quaternius hair via itch.io, Poly Pizza CC0-only models
  (note: many Poly Pizza models are CC-BY, not CC0 — filter per model page).
- All 34 GLBs validated: `glTF` magic + JSON chunk parses.
