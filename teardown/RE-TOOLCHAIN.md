# REVERSE ENGINEERING TOOLCHAIN

This is the production-grade RE stack for Western Heart teardowns. No hand-tooling, no prototypes — these are the full systems wired together.

## The Stack

### 1. Ghidra (NSA) — Disassembly & Decompilation
- **What:** Full-featured reverse engineering platform. Disassembles binaries, decompiles to C-like pseudocode.
- **Install:** Download from https://ghidra-sre.org — requires Java 21+
- **Local:** `~/workspace/tools/ghidra/` (ghidra_12.1.4.zip + jdk21.tar.gz)
- **Use for:** Finding PAC loaders, vertex decode functions, file format parsers in game executables. This is the PRIMARY tool — always check the actual game code before guessing at formats.

### 2. GhidraMCP — AI-Accessible Ghidra
- **What:** Model Context Protocol server that exposes Ghidra functionality to AI agents. Lets LLMs autonomously reverse engineer.
- **Repo:** https://github.com/LaurieWired/GhidraMCP
- **Local:** `~/workspace/tools/ghidra-mcp/`
- **Setup:**
  1. Install Ghidra 12.1.4
  2. Install the GhidraMCP extension: Ghidra → File → Install Extensions → select the ghidraMCP zip
  3. Restart Ghidra, enable plugin in File → Configure → Developer
  4. Configure MCP client with the server (see ghidra-mcp README for JSON config)
- **Use for:** AI agents can decompile functions, list methods/imports/exports, rename functions — all through MCP.

### 3. Codex CLI + Kilo Code Free Gateway — Free AI Coding Agent
- **What:** OpenAI's Codex CLI running through Kilo Code's free API gateway. No sign-in, no API key, no credit card.
- **Status:** WORKING NOW
- **Config:** `~/.codex/kilo-code.config.toml`
- **Usage:** `codex -p kilo-code exec --skip-git-repo-check "<prompt>"`
- **Limits:** 200 requests/hour per IP. Free tier prompts may be used for training (Kilo Code terms).
- **Use for:** Code generation, repo analysis, automated RE assistance.

### 4. GitHub Copilot CLI — GitHub-Native AI
- **What:** GitHub's CLI coding agent. Free tier: 2,000 completions + 50 chats/month.
- **Setup:** `copilot login --device-code` → visit https://github.com/login/device → sign in as mhvnsnt
- **Use for:** GitHub-integrated coding tasks.

### 5. Codex CLI (ChatGPT) — OpenAI's Agent
- **What:** Codex with ChatGPT Plus/Pro subscription.
- **Setup:** `codex login --device-auth` → visit https://auth.openai.com/codex/device → sign in with Google (fmmg.mars@gmail.com)
- **Use for:** When the free gateway hits limits.

## The Workflow

1. **Get the game files** — ISO, executable, data archives
2. **Load the executable in Ghidra** — let it auto-analyze
3. **Find the file loaders** — search for strings matching file extensions (.PAC, .TMD, etc.)
4. **Decompile the loader functions** — this tells you the EXACT format, no guessing
5. **Use GhidraMCP** — let AI agents explore the decompiled code systematically
6. **Write the extractor** — based on the decompiled code, not byte-guessing
7. **Verify** — extract and render, compare against the real game

## Laws

- **NO-HAND-TOOLING:** Use Ghidra + MCP + the full systems. No one-off Python scripts guessing at formats.
- **NO-DEFERRAL:** Full teardown — extracted, decrypted, decoded, AND assembled.
- **PUSH-AFTER-EVERY-TURN:** Branch → PR → merge, verify green.

## Current Status (2026-10-16)

- Ghidra 12.1.4: Downloaded to `~/workspace/tools/ghidra/` (extraction in progress)
- JDK 21: Downloaded (required for Ghidra)
- GhidraMCP: Present in `~/workspace/tools/ghidra-mcp/`
- Codex + Kilo Code: Working, no auth needed
- Copilot CLI: Awaiting device-code sign-in
- Codex (ChatGPT): Awaiting device-code sign-in
- Antigravity: Web signed in, CLI blocked on interactive TTY
