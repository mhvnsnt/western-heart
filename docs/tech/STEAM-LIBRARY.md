# Steam library: account vil3m (owner's own purchases)

Checked 2026-10-23 with DepotDownloader v3.4.0 (`-manifest-only`, remembered login). No credentials or tokens are stored in this repo.

**Update 2026-10-23 ~17:30 CDT:** Owner pasted their full Steam library (85 games).
Ownership CONFIRMED for all titles below marked YES (confirmed).

| App ID | Title | Owned? | Evidence |
|---|---|---|---|
| 389730 | TEKKEN 7 | **YES** | depot 389731 key OK; extraction in progress (PR #863) |
| 228980 | Steamworks Common Redistributables | yes | depot keys 228986/228990 OK |
| 1255630 | WWE 2K22 | **YES (confirmed)** | Owner's library: 49.2h played. Delisted — DepotDownloader needs Steam auth to pull. |
| 1015500 | WWE 2K20 | **YES (confirmed)** | Owner's library: 57.3h played. Delisted — DepotDownloader needs Steam auth to pull. |
| 846350 | WWE 2K19 | **YES (confirmed)** | Owner's library: 113 min played. |
| 564230 | Fire Pro Wrestling World | **YES (confirmed)** | Owner's library: 133.5h played (mostly sim/spectate). |
| 1620340 | Wrestling Empire | **YES (confirmed)** | Owner's library: 71.4h played. |
| 834530 | Yakuza Kiwami | **YES (confirmed)** | Owner's library: 26.7h played (Legacy). |
| 285900 | Gang Beasts | **YES (confirmed)** | Owner's library: 11.2h played. |
| 485510 | Nioh: Complete Edition | **YES (confirmed)** | Owner's library: 3.1h played. |
| 2878960 | WWE 2K25 | no | "not available from this account" |
| 2315690 | WWE 2K24 | no | not available |
| 1942660 | WWE 2K23 | no | not available |
| 664430 | WWE 2K18 | no | not available |
| 1778820 | TEKKEN 8 | no | not available |
| 544750 | SOULCALIBUR VI | no | not available |
| 976310 / 1971870 | Mortal Kombat 11 / 1 | no | not available |
| 1364780 | Street Fighter 6 | no | not available |
| 678950 | DRAGON BALL FighterZ | no | not available |

The ID guessed for WWE 2K Battlegrounds (1196590) was wrong; resolved to another game. Still needs correct ID if wanted.

## Pull priority (user's top 5, 2026-10-23)

1. Wrestling Empire — diverse wrestling/world → Heart and Mind Within
2. WWE 2K22 — animations, rigs, customization, creation suite, community creations
3. Yakuza Kiwami (Legacy) — Heart and Mind Within
4. Gang Beasts — physics → Tekken-style game + Heart and Mind Within
5. Nioh: Complete Edition — character depth, customization, mythology structure → Eastern Mind canon

Plus: Fire Pro Wrestling World (133h) — CPU sim, creation depth, AI logic.
Plus: WWE 2K19, WWE 2K20 — additional creation/animation libraries.

See `docs/tech/PULL-STRUCTURE-2026-10-23.md` for the full pull/wiring plan.

## For pull lanes

Delisted titles (2K22, 2K20) WILL work with DepotDownloader — they are owned,
just delisted from the store. Use Steam auth (username vil3m) and the app ID
directly. Do NOT let "delisted" stop the pull.
