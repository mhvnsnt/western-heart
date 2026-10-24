# Game Reverse-Engineering Playbook

**The repeatable process for tearing down any game to learn from it.**

Developed from the Tekken 3 teardown (2026-10-12). Use this for every game we study.

---

## Phase 1: Acquire

1. Get the game files (disc image, ROM, etc.)
2. Note the source — keep it in your records
3. Create workspace: `~/workspace/game-reverse-engineering/<game>/`

## Phase 2: Extract

### Disc-based games (PS1, PS2, etc.)
1. If BIN/CUE with raw sectors (2352 bytes): convert to ISO (2048 bytes) by stripping 24-byte header per sector
   ```python
   # MODE2/2352 → ISO/2048
   with open(src,'rb') as f, open(dst,'wb') as o:
       for i in range(sectors):
           f.seek(i*2352 + 24)
           o.write(f.read(2048))
   ```
2. Extract ISO 9660 filesystem with `pycdlib`
3. Identify: executable, asset archives (largest files), audio/video streams

### Cartridge games (N64, GBA, etc.)
1. ROM is a flat binary — no filesystem
2. Look for magic signatures to find embedded files

## Phase 3: Inventory

1. **Find the executable** — usually obvious (SLUS_xxx.xx, etc.)
2. **Find the asset archive** — usually the largest data file
3. **Look for the index table** — games need to find assets fast
   - Search executable for arrays of `{offset, size}` or `{sector, size}` pairs
   - Validate by checking that entries point to sensible locations
4. **Scan for magic signatures:**
   - PS1 TIM textures: `\x10\x00\x00\x00`
   - PS1 TMD models: `A\x00\x00\x00` (0x41)
   - General: `strings` + hex search for ASCII magic

## Phase 4: Extract Assets

1. **Pull open-source tools first** — someone has probably done this
   - Search GitHub for `<game> recompile`, `<game> decomp`, `<game> extractor`
   - Check their tools/ directory for format parsers
2. **If tools have hash checks** for retail versions and yours is modified:
   - Find the table offset manually (it's usually at a fixed location)
   - Parse it directly with Python `struct`
   - Monkey-patch the tool's expected hash if needed
3. **Extract in order:** textures (easiest) → models → audio → misc data

## Phase 5: Analyze the Executable

### Without Ghidra (lightweight):
1. `strings` — find character names, system labels, debug text
2. `capstone` (MIPS/ARM/x86) — disassemble entry point and key functions
3. Look for: game loop, asset loading, state machines

### With Ghidra (deep dive):
1. Requires Java 17+ and ~1GB disk
2. Use `analyzeHeadless` for automated analysis
3. Look for: render pipeline, physics, AI, fighting systems

## Phase 6: Document

Write these four documents for every game:

1. **`<GAME>-ARCHITECTURE.md`** — file structure, formats, tools used
2. **`<GAME>-RIG-LESSONS.md`** (or equivalent) — what this teaches about our craft
3. **`<GAME>-MAPPING.md`** — how findings apply to our specific games
4. **`REVERSE-ENGINEERING-PLAYBOOK.md`** — update this playbook with new techniques

## Phase 7: Apply

For each finding, ask:
- "How does this apply to Bannon?"
- "How does this apply to AshLane?"
- "How does this apply to Concrete Dragon?"
- "How does this apply to Brutal Fist?"

Write concrete action items, not vague observations.

---

## Tools Reference

| Tool | Purpose | Install |
|---|---|---|
| pycdlib | ISO 9660 extraction | `pip install pycdlib` |
| capstone | Multi-arch disassembly | `pip install capstone` |
| gdown | Google Drive downloads | `pip install gdown` |
| Ghidra | Full RE (needs Java+disk) | github.com/NationalSecurityAgency/ghidra |

## Rules

1. **Study, don't steal.** We learn techniques. We build original work.
2. **Document everything.** If it's not written down, it didn't happen.
3. **Script every step.** The next game should be faster.
4. **Pull open-source first.** Don't hand-roll what exists.
5. **Map to our games.** Every finding needs a "so what for us?"
