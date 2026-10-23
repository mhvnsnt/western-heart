# RE toolchain (shared box, /workspace/tools)

Check what is already here before installing anything. The existing tools are `tools/depotdl` (DepotDownloader 3.4.0, saved login), `tools/umodel`, `tools/repak`, `tools/cue4parse` (FModel notes in `tools/depot-pull/FMODEL.md`), `tools/t7tools`, `tools/godot`, plus `game-reverse-engineering/tooling`.

| Tool | Path | State | Use |
|---|---|---|---|
| Ghidra 12.2 + Temurin JDK 21.0.13 | `/workspace/tools/ghidra/` | installed | `JAVA_HOME=/workspace/tools/ghidra/jdk-21.0.13+9 ghidra_12.2_PUBLIC/support/analyzeHeadless /tmp/proj P -import game.exe -postScript <script>` for native sim/AI logic and custom containers |
| GhidraMCP (LaurieWired/GhidraMCP) | `/workspace/tools/ghidra/mcp` | todo | agents query a Ghidra project over MCP |
| ilspycmd | `~/.dotnet/tools` | todo | Unity Mono games (Fire Pro, Wrestling Empire, Gang Beasts): `Managed/Assembly-CSharp.dll` |
| UnityPy / AssetRipper | pip | todo | Unity meshes, anims, ScriptableObject data |
| QuickBMS | `/workspace/tools/quickbms` | todo | Koei and PAR archives via community .bms scripts |

For an unknown format, try a community spec first, then QuickBMS, then Ghidra on the loader function. Decoders go in `game-reverse-engineering/tooling/<game>/`.
