# Attribution — netfox

- **What:** Godot 4 multiplayer framework: fixed-tick timing, `RollbackSynchronizer` (client prediction + server reconciliation), `StateSynchronizer`, `TickInterpolator`, network-condition simulator, noray NAT-punchthrough integration. Vendored: `netfox` (core), `netfox.extras`, `netfox.internals`, `netfox.noray`.
- **Source:** https://github.com/foxssake/netfox
- **Author:** Tamás Gálffy / Fox's Sake Studio
- **Version vendored:** main @ 2026-10-16 (v1.35.x line; releases carry AssetLib zips)
- **License:** MIT (LICENSE vendored alongside)
- **Why:** the most mature Godot 4 netcode framework (AssetLib-listed, Forest Brawl demo, active 2026). RollbackSynchronizer is the server-authoritative-with-rollback lane for the Godot 4 target; noray gives free NAT punchthrough for P2P without running relay infra.
- **Install into a Godot 4 project:** copy these four addon dirs to `res://addons/`, enable in Project Settings → Plugins.
