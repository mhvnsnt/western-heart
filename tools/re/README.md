# THE RE BENCH — tools/re/

**This is the reverse-engineering bench. Point it at a game, get answers.**

Owner law: NO-HAND-TOOLING. No one-off Python scripts guessing at formats. Use the full
systems: Ghidra for disassembly/decompilation, MCP to wire it to the agents, the real
decoder stack for archives. Stop fiddling with a screwdriver for a jackhammer job.

## What's on the bench

| Tool | What it does | Where |
|------|--------------|-------|
| **Ghidra 12.1.4** | NSA RE platform: disassembler, decompiler, headless batch analysis | `fetch-ghidra.sh` pulls it (1.3GB, not in git); VM has it at `~/workspace/tools/ghidra/` |
| **GhidraMCP** | MCP server exposing Ghidra to AI agents (decompile, list, rename via MCP) | `mcp/` — bridge + client config |
| **PyGhidra scripts** | Headless analysis scripts (matrix hunter, string dumper, etc.) | `scripts/` |
| **CLI decoders** | binwalk, QuickBMS, 7z, vgmstream, xdelta, PS2/PSP tools | `cli/README.md` — inventory + install |
| **Game queue** | Every teardown game, its RE status, what's next | `QUEUE.md` |

The narrative doc lives at `teardown/RE-TOOLCHAIN.md`. This directory is the runnable bench.

## 60-second start

```bash
cd tools/re
source env.sh            # sets JAVA_HOME, GHIDRA_HOME, PATH
./fetch-ghidra.sh        # first time only: downloads Ghidra 12.1.4 + Temurin JDK 21, verifies SHA-256
./analyze.sh /path/to/game.elf myproject
# project lands in ./projects/, analysis log in ./logs/
```

Then point the MCP client at it (see `mcp/README.md`) and ask the agent to reverse-engineer.

## Provenance

- Ghidra 12.1.4 PUBLIC (2026-09-21) — Apache 2.0, NationalSecurityAgency/ghidra
- Temurin JDK 21 — required by Ghidra 12
- GhidraMCP 2.0.0 — Apache 2.0, LaurieWired/GhidraMCP
- First blood: Urban Reign SLUS_212.09 bind-matrix hunt (see `scripts/find_matrices.py`)
