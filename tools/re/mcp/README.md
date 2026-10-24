# GhidraMCP — the AI wire into Ghidra

GhidraMCP (LaurieWired, Apache 2.0, v2.0.0) exposes Ghidra to MCP clients:
decompile functions, list methods/imports/exports, rename symbols — all through MCP tools.

## How it's wired here

1. **Extension**: the GhidraMCP plugin zip ships next to this README
   (`ghidra-mcp-plugin.zip`). `../fetch-ghidra.sh` installs it into
   `Ghidra/Extensions/` automatically. Manual: Ghidra → File → Install Extensions → +.
2. **HTTP bridge**: when the plugin is active, Ghidra serves MCP on
   `http://localhost:8080` (configurable in Edit → Tool Options → GhidraMCP HTTP Server).
3. **Client config**: `mcp-config.json` — drop into your MCP client.

```json
{
  "mcpServers": {
    "ghidra": {
      "command": "<venv-python>",
      "args": ["<path-to>/bridge_mcp_ghidra.py"],
      "env": { "GHIDRA_MCP_HOST": "localhost", "GHIDRA_MCP_PORT": "8080" }
    }
  }
}
```

## Headless note

The HTTP server needs the plugin loaded. For batch work, prefer `analyzeHeadless`
with `-postScript` (see `../scripts/`) — no MCP round-trip needed. Use MCP for
interactive, agent-driven RE sessions against a running Ghidra.

## VM status (2026-10-19)

- Extension installed into `~/workspace/tools/ghidra/ghidra_12.1.4_PUBLIC/Ghidra/Extensions/GhidraMCP`
- Bridge: `~/workspace/tools/ghidra-mcp/bridge_mcp_ghidra.py` (venv at `~/workspace/tools/ghidra-mcp/venv`)
- Headless HTTP smoke test: PENDING (plugin load in headless mode unverified)
