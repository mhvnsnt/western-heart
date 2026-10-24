# WWE 2K — TeraBox Browser-Lane Spec (STAGE 1)

Lane `wh-wwe2k-100`, 2026-10-14. For parent delegation — subagents cannot run browser tasks.

## Destination
TeraBox folder: `/WesternHeart/teardowns/wwe2k/` (create if missing).

## Batch A — already on GitHub, pull straight to TeraBox (no VM disk used)

| File | Size (bytes) | Source URL |
|------|-------------|------------|
| `wwe2k19-entrance-pack.tar.gz` | 175,112,192 | https://github.com/mhvnsnt/wrestling-game/releases/download/wwe2k19-animation-packs-v1/wwe2k19-entrance-pack.tar.gz |
| `wwe2k19-moves-pack.tar.gz` | 123,317,410 | https://github.com/mhvnsnt/wrestling-game/releases/download/wwe2k19-animation-packs-v1/wwe2k19-moves-pack.tar.gz |
| `WWE.2K14.DLCS.zip` | 44,660,178 | https://github.com/mhvnsnt/wrestling-game/releases/download/wwe2k14-dlcs-v1/WWE.2K14.DLCS.zip |

Verify byte size matches after upload. Contents: 445 entrance motion PACs + 54 gimmicks +
props (entrance pack); 34 motion PACs + patches (moves pack); 12 PS3 DLC unlock PKGs + RAPs.

## Batch B — full games 2K15–2K23 (Archive.org → TeraBox, priority order)

Do NOT route through the VM (85% disk). Download in browser → upload to
`/WesternHeart/teardowns/wwe2k/full-games/`. Full URLs + sizes in
`game-reverse-engineering/wrestling-games/WWE2K15-23-ACQUISITION.md`.

1. WWE 2K19 CSF (50.96GB) — highest priority (best CAW/moveset data, best mod support)
2. WWE 2K15 CSF (33.13GB) — smallest full PC game
3. WWE 2K23 (84.48GB) — newest roster/models
4. 2K18 (45.11GB) → 5. 2K17 (50.28GB) → 6. 2K16 (44.20GB) → 7. 2K20 CSF (53.62GB, last)

## Do NOT pull
- `wwe-2-k-14` / `wwe-2-k-14_202111` — mislabeled (actually SvR2011 PSP, ULUS-10543)
- `wwe-2-k-14_202407` — PSP mod, not the real 2K14
- True WWE 2K14 PS3/360 full game: not found on Archive.org — still hunting.
