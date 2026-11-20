# Attribution — nakama-godot (client)

- **What:** Official Godot 4 client SDK for the Nakama game server: accounts, matchmaker, realtime multiplayer socket, leaderboards, chat, storage. GDScript, Godot 4.0+.
- **Source:** https://github.com/heroiclabs/nakama-godot
- **Author:** Heroic Labs
- **Version vendored:** main @ 2026-10-16
- **License:** Apache-2.0 (LICENSE vendored alongside)
- **Why:** pairs with our self-hosted Nakama server (`tools/netcode/matchmaking/docker-compose.yml`) for accounts + 1v1 matchmaking + leaderboards. The server itself runs from the official Docker image — not vendored here.
- **Install:** copy `addons/com.heroiclabs.nakama/` to `res://addons/`, add `Nakama.gd` as an autoload, `Nakama.create_client("defaultkey", host, 7350, "http")`.
