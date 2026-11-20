#!/usr/bin/env python3
"""smoke_mcp_server.py — CI smoke test for the mcp-for-blender MCP server.

Spawns `python -m blender_mcp.server` over stdio (JSON-RPC) and checks:
  1. initialize handshake -> server name/version
  2. tools/list -> expected core tools present
  3. tools/call get_scene_info with no Blender attached -> graceful
     "Could not connect to Blender" error (proves error path, not a crash)

Stdlib only. Requires the mcp-for-blender package importable
(tools/setup/setup_toolchain.sh installs it into a venv).
Blender itself is NOT required.

Usage: python3 tools/mcp/smoke_mcp_server.py [--python /path/to/python]
Exit 0 = all checks pass.
"""
import json
import os
import subprocess
import sys

REQUIRED_TOOLS = {"get_scene_info", "execute_blender_code", "look",
                  "get_addon_status", "search_assets"}


def main(argv):
    py = sys.executable
    if "--python" in argv:
        py = argv[argv.index("--python") + 1]
    env = dict(os.environ, DISABLE_TELEMETRY="true")
    try:
        p = subprocess.Popen(
            [py, "-m", "blender_mcp.server"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, env=env)
    except FileNotFoundError as e:
        print("FAIL: cannot start blender_mcp.server: %s" % e)
        return 1

    def rpc(method, params=None, mid=1):
        msg = {"jsonrpc": "2.0", "id": mid, "method": method}
        if params is not None:
            msg["params"] = params
        try:
            p.stdin.write((json.dumps(msg) + "\n").encode())
            p.stdin.flush()
        except BrokenPipeError:
            return {"error": "server died writing %s" % method}
        line = p.stdout.readline()
        if not line:
            return {"error": "server died reading %s" % method}
        return json.loads(line.decode())

    failures = []

    init = rpc("initialize", {"protocolVersion": "2024-11-05",
                              "capabilities": {},
                              "clientInfo": {"name": "smoke", "version": "1"}},
               mid=1)
    info = (init.get("result") or {}).get("serverInfo", {})
    print("server: %s %s" % (info.get("name"), info.get("version")))
    if "blender" not in info.get("name", "").lower():
        failures.append("unexpected server name: %r" % info.get("name"))

    tools = rpc("tools/list", {}, mid=2)
    names = {t["name"] for t in (tools.get("result") or {}).get("tools", [])}
    print("tools (%d): %s" % (len(names), sorted(names)))
    missing = REQUIRED_TOOLS - names
    if missing:
        failures.append("missing tools: %s" % sorted(missing))

    call = rpc("tools/call",
               {"name": "get_scene_info", "arguments": {}}, mid=3)
    res = call.get("result", {}) or {}
    text = ""
    for c in res.get("content", []) or []:
        text += c.get("text", "")
    graceful = ("Could not connect to Blender" in text) or res.get("isError")
    print("no-Blender call graceful: %s" % graceful)
    if not graceful:
        failures.append("get_scene_info without Blender did not fail gracefully: %r"
                        % text[:200])

    try:
        p.kill()
    except Exception:
        pass

    if failures:
        print("FAIL:")
        for f in failures:
            print("  -", f)
        return 1
    print("PASS: mcp-for-blender stdio MCP OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
