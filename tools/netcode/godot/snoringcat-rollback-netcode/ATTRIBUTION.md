# Attribution — godot-rollback-netcode (Snoring Cat)

- **What:** Game-agnostic rollback netcode framework for Godot 4. Pure GDScript, no GDExtension: `NetworkOrchestrator` singleton, frame-synchronous 60 FPS simulation loop, `ReconcilableState` base for networked entities, rollback buffer, NTP-style frame sync, pluggable transport (ENet, WebSocket, **WebRTC**), GUT tests, working `simple_game` example.
- **Source:** https://github.com/snoringcatgames/godot-rollback-netcode
- **Author:** Snoring Cat LLC
- **Version vendored:** main @ 2026-10-16
- **License:** MIT (LICENSE vendored alongside)
- **Why:** the closest thing to "GGPO for Godot 4" in pure GDScript — and the **only** Godot rollback option with a WebRTC transport, which matters because the web export can't load GDExtensions. Consumed upstream via git submodule; vendored here as a reference copy.
- **Install:** copy this directory's contents to `res://addons/rollback_netcode/` in a Godot 4.7+ project, enable the plugin.
