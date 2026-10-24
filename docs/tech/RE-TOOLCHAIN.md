# RE toolchain

The whole reverse-engineering toolkit is now kept in the **private** repo `mhvnsnt/game-reverse-engineering` under `toolkit/`. Some tools and scripts are game-specific, so nothing from it lives in this public repo. Rebuild it on any fresh Linux box with one command:

```bash
toolkit/bootstrap.sh /workspace/tools && toolkit/selftest.sh /workspace/tools && source /workspace/tools/env.sh
```

- Third-party tools are pinned by version, download URL and sha256 (`toolkit/pins.tsv`), or by git commit (`toolkit/git-pins.tsv`). Their binaries are never committed.
- Our own scripts are committed in full, plus the DepotDownloader patch (a diff and its build script).
- No Steam tokens or credentials are stored. Logins happen at run time.
- `toolkit/README.md` lists every tool with its version and purpose.

Main tools: .NET 8 (+ .NET 9 to build), ilspycmd 8.2, Ghidra 12.2 on Temurin JDK 25 (Ghidra 12.2 needs Java 25), DepotDownloader 3.4.0 plus our patched `dd-range`, ParTool 1.3.4, repak 0.2.3, Godot 4.3, Node 22 with gltf-transform, UEViewer, WrestleMINUS, ARC I/O, and the Tekken 7 packing tools.

Still to add: GhidraMCP (agents query a Ghidra project over MCP), UnityPy/AssetRipper, and QuickBMS for Linux.

For an unknown format, try a community spec first, then QuickBMS, then Ghidra on the loader function. Decoders go in `game-reverse-engineering/tooling/<game>/`. This game loads private assets only through `__WH_PRIVATE_ASSETS`.
