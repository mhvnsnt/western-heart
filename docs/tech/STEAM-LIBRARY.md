# Steam library: account vil3m (owner's own purchases)

Checked 2026-10-23 with DepotDownloader v3.4.0 (`-manifest-only`, remembered login). No credentials or tokens are stored in this repo.

The account holds **85 licenses** (packages). DepotDownloader reports the license count but not the app names, and the Steam profile's game list is private, so I couldn't pull the full app list automatically. Each app ID below was probed one by one.

| App ID | Title | Owned? | Evidence |
|---|---|---|---|
| 389730 | TEKKEN 7 | **YES** | depot 389731 key OK; extraction in progress (PR #863) |
| 228980 | Steamworks Common Redistributables | yes | depot keys 228986/228990 OK |
| 1255630 | WWE 2K22 | **UNCLEAR** | app is delisted; not refused, but "Couldn't find any depots" |
| 1015500 | WWE 2K20 | **UNCLEAR** | same as 2K22 (delisted) |
| 2878960 | WWE 2K25 | no | "not available from this account" |
| 2315690 | WWE 2K24 | no | not available |
| 1942660 | WWE 2K23 | no | not available |
| 664430 | WWE 2K18 | no | not available |
| 1778820 | TEKKEN 8 | no | not available |
| 544750 | SOULCALIBUR VI | no | not available |
| 976310 / 1971870 | Mortal Kombat 11 / 1 | no | not available |
| 1364780 | Street Fighter 6 | no | not available |
| 678950 | DRAGON BALL FighterZ | no | not available |

The IDs I guessed for WWE 2K Battlegrounds (1196590) and WWE 2K19 (816020) are wrong; they resolved to other games. Those two still need a re-probe with the correct IDs.

## To get the full 85-title list
Pick one:
1. The owner sets Steam → Profile → Privacy → **Game details: Public**. After that, `https://steamcommunity.com/id/vil3m/games?tab=all&xml=1` lists every owned app with no login.
2. The owner pastes the list from store.steampowered.com/account/licenses.

## For Muse (WWE 2K → teardown/wwe2k/)
Not one WWE 2K title is confirmed owned on vil3m yet. 2K22 and 2K20 might be, since both are delisted and DepotDownloader can't resolve their depots. A machine logged into Steam (the Steam client Library view) can confirm.
