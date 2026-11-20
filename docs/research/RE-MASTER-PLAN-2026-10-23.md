# Reverse Engineering Battle Plan — Owned Games (2026-10-23)

**Owner directive (verbatim):** *"Find her way around that whole license code issue like bro it's a game that I own and we can reverse engineer the code and everything"*

**Status:** The user owns these games on Steam and explicitly authorizes full reverse engineering. This plan covers WHAT to reverse, HOW, WHERE the results go, and the legal firewall.

---

## 0. The firewall (non-negotiable)

| PRIVATE repo (`mhvnsnt/game-reverse-engineering`) | PUBLIC repo (`mhvnsnt/western-heart`) |
|---|---|
| Raw game files (models, textures, audio) | Original implementations of learned techniques |
| Binary dumps, decompiled code | Technique descriptions in research docs |
| Extracted proprietary formats | Our own file formats inspired by them |
| Anything directly copied from game data | Data we authored (movesets in our notation, etc.) |

**Rule:** We learn TECHNIQUES and pull DATA STRUCTURES. Our code is original. Never commit a game asset, decompiled function, or byte-identical copy to the public repo.

---

## 1. Priority RE targets (by value to WH)

### Tier 1 — Creation suite backbone
1. **WWE 2K22 `.pac` / Oodle** — unlocks ~10,000 creation parts. Blocker: Oodle decompression. Approach: extract `oo2core` DLL from game files via FFI, or use public Oodle research. Then map `.pac` header/chunk/table, then `.ch.pac` character format.

### Tier 2 — High-value single extractions
2. **Nioh 2 character codes** — serialization format via differential RE (two characters, one slider diff, map code positions). Highest-value single file target. Shortcut: codes are shared publicly by the community — may not need game files.
3. **Geo-Mod 2.0 schemas** (RFG Re-Mars-tered, app 667720) — shard/layer/material structures via RSL/FactionFiles + hex analysis.

### Tier 3 — Formula extraction
4. **Fire Pro match formulas** — HP/SP thresholds, critical probability, counter windows. 2D engine: strings analysis + empirical differential testing.
5. **Destiny 2** — Phase 1: public Bungie API (no RE needed). Phase 2: Tiger packages for the rest.

### Tier 4 — Already open
- **Overgrowth** — Apache 2.0 source on GitHub. No RE needed; vendor directly.
- **Euphoria** — proprietary middleware; RE the *behavior* (observable), not the middleware.

---

## 2. Toolchain (this VM)

Available: `strings`, `objdump`, `readelf`, `7z`, `unzip`, Python `capstone`, `pefile`, `struct`/`zlib`/`lzma`.
Missing: Ghidra (no Java), radare2, Oodle libs.

---

## 3. File flow

1. **Credentialed machine** (Grok's side, Steam-logged): pulls game files via DepotDownloader → pushes to PRIVATE `mhvnsnt/game-reverse-engineering` repo (git-lfs for large binaries).
2. **This VM**: clones private repo → runs RE toolchain → writes technique docs → implements original code → pushes technique docs + code to PUBLIC `western-heart`.
3. **Never**: game files on public repo. Never: decompiled code committed anywhere (analyze in working dir, document techniques, delete or keep private).

---

## 4. Per-target technique docs (to be written post-RE)

Each RE target gets a technique doc in `docs/research/` on the public repo describing WHAT was learned and HOW WH implements it originally — no proprietary bytes, no copied code.

---

## 5. What needs the game files (blocked until pull)

- Oodle DLL extraction (needs WWE 2K22 depot)
- `.pac` header mapping (needs .pac files)
- Geo-Mod schemas (needs RFG data files)
- Fire Pro binary (needs the game executable)
- Nioh 2 codes: may be obtainable from public community shares without game files
