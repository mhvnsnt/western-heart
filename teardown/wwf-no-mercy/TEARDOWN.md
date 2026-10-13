# WWF NO MERCY — Teardown for Western Heart

**Role in Chimera Build:** Wrestling systems + character customization + grappling animations.
**Engine:** AKI Corporation (same family: WCW/nWo Revenge, WrestleMania 2000, Virtual Pro Wrestling 2)
**Platform:** Nintendo 64
**Last updated:** 2026-10-13 (teardown sweep)

---

## What's Extracted and Documented

### ROM — Verified
- `WWF No Mercy (USA) (Rev-A).z64` — 32,554,432 bytes, CRC32 `BACEEA13` (byte-verified)
- Source: Internet Archive `n64patchedwrestlingroms` (`WWF No Mercy (Unlocked).zip`, also in TeraBox `/western-heart/teardown-source-binaries/`)

### Wrestler Data Tables (ROM-verified, static RE)
- **Wrestler display-name / internal-ID table @ `0x168D930`:** 2 pad bytes, count `0x2A` = **42 entries**, per entry `u8 wrestler_id` + null-terminated ASCII name. Alphabetical; ID gaps at 5 and 37 (hidden/unused slots). Full mapping in `docs/wrestler-id-table.json`
- **Move tables match community docs** — structural analysis confirms AKI table layout is as documented
- Tool: `tools/analyze_nomercy.py` (re-runnable; regenerates the ID table)
- Documented: `docs/CHARACTER-DATA.md`, `docs/NOMERCY-TEARDOWN.md`

### Animation Isolation (Chunk 2 — DONE 2026-10-13)
- `0x13E4A0` = 10-pointer move-data index (targets → ovl_c ROM `0xF4930`; no ROM xrefs; table sits in a section gap) — committed `docs/ANIMATION-ISOLATION.md`
- Float table `@0x13E2BC` resolved = 7 position records `[0,x,y,z]` (camera/spawn); u16 run = 7,565 entries; 2nd pointer block `@0x13E530`
- `recomp/syms` has NO animation labels (dead end, documented so nobody repeats it)

### Community RE Resources (cloned locally)
- `re-docs/` — chaotix610/wwfnomercy-docs: game systems, move database, creation suite docs
- `recomp/` — Gadge64/WWFNoMercyRecomp: N64Recomp static recompilation project (CMake build, disasm, syms)

### Creation Suite Architecture
- Each character slot: 4 attire slots. Attires share moves/style/parameters/ally-enemy; differ in profile/music/appearance
- Appearance system: 14 male + 9 female body types × 8 skin tones; 7M/3F head shapes; 98M/20F face textures; 22 hair styles (+63 front-hair options); 31 facial hair options

---

## What's Blocked and Why

- **Animation keyframe bank NOT yet isolated** — the core open problem. Next leads: DMA/loader path for `0x8014CD00`, animation indices in `0xF4730` move records, or emulator RAM diffing. `recomp/syms` labels are a dead end.
- **Per-code text-engine semantics** — open (does not block motion work).
- **Best-of push pending** — wrestling-lane chunks 1–2 (CAW + animation isolation) have commits in the lane tree; the western-heart TEARDOWN.md best-of push still needs to land.

---

## Chimera Build Value

- **AKI engine wrestling systems** are the template for Western Heart's Wrestling Mode grappling: move tables, move-data index, and per-character fighting styles are real, ROM-verified data — not approximations
- **Customization architecture** (4 attires per slot, shared-vs-per-attire data split) is the reference model for the chimera character customization system
- **42-wrestler ID table** gives the canonical No Mercy roster as data, ready for import as chimera archetypes
- Combined with WMXIX's arenas (geometry) and Revenge Mode (structure), No Mercy supplies the wrestling *soul*: moves, customization, roster

---

## Next Steps

1. Isolate the animation keyframe bank (DMA path → `0x8014CD00`, `0xF4730` indices, or emulator RAM diff)
2. Land the wrestling-lane best-of into western-heart main (chunks 1–2)
3. Port move-table/move-index findings into the chimera move database schema
4. Feed decoded grapple/throw animation indices into the retarget pipeline (YANM→Tekken3 v2 pattern)
