# WMXIX Moveset Table via Ghidra XREF — W4c Evidence Report (2026-10-21)

**Verdict up front:** Route 1 (Ghidra) traced the complete runtime chain from a
menu.mpq special slot to a YANM clip — CMPack loader, motion manager, the
`wprm` move-definition database (fully decoded in this lane), the two lookup
functions, and the move-execution function — **except the last link: the
per-wrestler default-moveset data** (which move descriptor each wrestler
carries into each slot). That data was not found in any file, package leaf, or
static DOL table searched by W4b or by this lane, and the code path that fills
a wrestler object's moveset at match load was not isolated. **No clip
assignments are made. `moveset-library/movesets/rock-moves-wmxix.json` is
unchanged.** A wrong "Rock Bottom" is worse than an honest unknown. Route 3
(Dolphin runtime observation) is specified at the end — it will crack this,
because the descriptor the game builds for each special can be read directly
off the two lookup functions whose addresses and semantics are now proven.

## Established before this lane (W4 / W4b, not redone)

- `.mpc` POF container fully decoded (`WMXIX-MPC-INDEX.json`): `move.mpc` =
  870 motion IDs → 1,905 YANM clips; any ID extractable, proven.
- The Rock's three specials are named with slots in `//menu/menu.mpq`:
  **Rock Bottom [Front Grapple]**, **People's Elbow [Upper Down Grapple
  Facing Up]**, **People's Spine Buster [Irish Whip Grapple]**.
- The wrestler→motion-ID table is not in any data file W4b searched (all 10
  `.mpc` trees, `com_dt`, `static.mpc` incl. the CAW per-motion catalog,
  `menu.mpq` strings, full DOL density scans).
- Rock's `menu.mpq` profile index (W4): Defwres record @ 0xB0, codes
  A002/C000/D106.

## Route 2 — menu.mpq / menupause MPQ internals (closed, no table)

Both archives are a **big-endian MPQ-variant** (Yuke's), not Blizzard MPQ:
header = magic `MPQ\0`, u32 header size 0x800, u32 entry size 0x10, u32 file
count (**145** `menu.mpq` / **98** `menupause`), then count × u32 offsets from
0x10, data from 0x800. Offsets strictly increasing; implied sizes sum
**exactly** to archive size − 0x800 in both.

- `menu.mpq` (ISO 0x093E8460, 29,953,536 B): file 0 (463,328 B) = profile/text
  (Rock profile at archive +0x5B52B — re-verified this lane: pure string pool,
  English move lists + Shift-JIS text + a small u32 offset table; **no binary
  move IDs in the block tail**); file 1 (5,051,936 B) = menu scene resources
  (named nodes `2D_Blink`, `char_sel_*`, `cam_*`); file 3 (704,416 B) = menu
  scene resource (`A102_27a`, `abiility_mt`); dominant classes 262,784 B ×47
  and 66,176 B ×51 = **TPL textures** (magic `00 20 AF 30`).
- `menupause` (ISO 0x0B079260, 22,145,664 B): same TPL classes ×47/×46;
  file 1 (5,263,552 B) = pause-menu scene resources.
- Every rare-size file in both archives was full-scanned with ASCII +
  u16-BE + variety-filtered motion-ID detectors: **zero hits**. (An apparent
  1,142-long u16 "run" in menu file 3 was the constant graphics value 0x2222
  repeated — verified false alarm, excluded by the variety filter.)

## Route 1 — Ghidra setup (full system, no hand-tooling)

- `main.dol` pulled whole via the W4 range reader (ISO offset 0x1F700,
  3,422,208 B exact). Sections tile vaddr 0x80003100–0x8039D6E0, entry
  0x80003154.
- Ghidra 12.1.4 headless, `PowerPC:BE:32:default`. Full auto-analysis was
  OOM/SIGKILLed repeatedly in this VM; the working recipe: flat memory image
  (sections placed at load addresses, **zero overlap byte conflicts**),
  BinaryLoader base 0x80003100, memory split into the 11 DOL sections, heavy
  analyzers disabled, heap capped (`GHIDRA_HEADLESS_MAXMEM=1100m`), Ghidra
  tmpdir redirected off the small `/tmp` tmpfs, then scripted disassembly in
  0x60000-byte slices with per-slice saves.
- **Result: 714,266 instructions** (slice counts sum exactly to the earlier
  full-run count — cross-validated) and **3,902 functions**.

## The loader layer (proven from code)

- `FUN_8007A71C` / `FUN_8007AACC` = the CMPack chunk resolver/iterator pair:
  they walk chunk headers comparing 4-char tags (memcmp-like `FUN_802A6098`)
  against a path-component stack; the error path references the
  "not find 'POF0' chunk" string (0x802E12E4). Source strings in rodata:
  `cmpack.cpp`, `CMPackDir`. `FUN_8007A5F8` = load-file-by-name + relocate.
- `FUN_8008E9A8(pkg, path, out)` = CMPack find-by-path: splits the path at the
  last `/`, resolves the directory via `FUN_8008ED50`, scans children
  comparing names (`FUN_802A60D8`). It operates on exactly W4b's record
  formats — 12-byte records (`[u32 count][char[4] name][u32 first]`) in raw
  packages and 0x28-byte records after relocation — **W4b's container decode
  is confirmed by the game's own code**.
- `FUN_8008E59C` = instantiate a chunk cursor into a loaded-chunk object;
  `FUN_8008E37C` = return its data pointer; `FUN_8008F200(pkgObj, filename)`
  = the two-segment package file loader used for every `.mpc`.

## Boot wiring (FUN_8001FB84, game init)

- `motion/move.mpc` (string vaddr 0x802DC2A0) is loaded via `FUN_8008F200`
  into a package object stored at SDA slot **r13−0x6F20**, then enabled with
  `FUN_8008F0A8(obj, 1)`. (The bare string is never materialized as a
  lis/addi address anywhere in the DOL and has no u32 pointer — it only
  appears as a decompiler-resolved immediate here, which is why W4b's
  density/pointer scans could not see the reference.)
- `static.mpc` package object at r13−0x6F4C. Its leaves are fetched by name:
  `sys/sprm` → r13−0x6F1C (raw), **`sys/wprm` → r13−0x6F18 (relocated via
  `FUN_8007A71C`)**, `sys/mstb` → r13−0x6F14 (relocated), plus `sys/anim`,
  `2d/eff/*`, `sys/mcmsg`. (W4b identified the `mstb` leaf's content as
  Revenge-mode stage data — HARBOR strings — consistent with it being
  boot-loaded alongside the parameter tables but unrelated to movesets.)

## The motion manager (where move.mpc actually goes)

`FUN_80072610` (system init) creates a manager object (ctor `FUN_8008AB18`,
capacity 16 packages) at game-context +0x5C and registers packages with
**`FUN_8008A73C(manager, package)`**:

1. `move.mpc`'s package object (r13−0x6F20) is registered first (call site
   0x80073A8C).
2. Four further packages are attached in a loop (sites 0x80073AE8–0x80073B18)
   from YOBJ headers obtained via `FUN_800764F0` (a loaded-file table lookup
   that can also format package filenames from templates) and attached with
   `FUN_8008F624`, then registered the same way. Their individual filenames
   were not resolved in this lane; by namespace they are the letter-code
   motion packages (the `common*` family of the W4b census).

**`FUN_8008A73C` builds the unified motion index**: for every top-level node
name in every registered package it computes bucket = decode(name[0])×10 +
decode(name[1]) over a 360-entry table (decode: digit → −0x30, letter →
−0x37, so `00`–`99` and `A0`–`Z9` all fit), and in each bucket a 100-cell u16
array indexed by decode(name[2])×10 + decode(name[3]). Cell value =
**packageIndex<<12 | nodeIndex** (cells initialise to 0xFFFF; packageIndex
0xF marks empty). Every motion in every registered package — numeric
`move.mpc` IDs and letter codes alike — is addressable by its 4-char name
through this one index.

## The load API (what gameplay calls)

- **`FUN_8008A548(manager, name4, variant, suffixChar)`** = load a motion:
  resolves name4 through the index to (package, node record), builds the leaf
  name as two decimal digits of `variant` plus the letter `'A'+suffixChar`,
  finds that leaf among the node's children (`FUN_8008EB6C`), instantiates
  the YANM chunk (`FUN_8008E79C` + `FUN_8008E59C`), and caches it in the
  manager's 16-slot loaded-motion array. Returns the slot or −1.
- **`FUN_8008A3AC(manager, &name4, variant)`** = variant-availability query:
  enumerates a node's leaves, maps leaf suffix letters to a bitmask, returns
  the highest available variant class (0–4). This is how the game asks "how
  many variants does this motion have".
- Sole direct caller of `FUN_8008A548`: `FUN_80226404`, a wrapper on the
  per-wrestler motion object (fields +0x98 = manager pointer, +0xC8 = entry
  count, +0xCC = array of {u32 name, ptr def} with the def's variant count at
  +0xC).

## `wprm` decoded — the move-definition database (this lane's main artifact)

`static.mpc` uses 0x28-stride records on disk (directory: count u16 @+2,
name @+4, first-child u32 @+0x24; leaf: marker 0xFF00, size = u16 @+2 × 32,
data offset u32 @+0x24, data at data_start 0xE60 + offset). The `sys/wprm`
leaf (94,496 B) is a YOBJ chunk; the relocator's return value — the pointer
the game stores at r13−0x6F18 — is **leaf + 8** (YOBJ header: count 69 @+0x08,
table offset 0x110 @+0x0C). It holds **two group tables of 28-byte records**:

- **Table A** (69 group entries @ leaf+0x110; reached by the packed-key
  lookup `FUN_8007609C`): group entry = `[u16 key][u16 count][u32
  recordsOffset]`; group records chain contiguously (1,708 record slots in
  the 68 category groups; the alias entry's fields point at Table B).
  Entry key 0 is a header alias (its count/offset fields are Table B's
  header); the 68 real groups (keys 101–354) are **move categories** — e.g.
  group 101 holds only 01xx motions (24), group 111 only 03xx (59), group
  121 mixes 11xx/03xx/07xx by index range, group 172 holds 20xx–22xx (91),
  group 351 is the 85xx/86xx viewer set (128). **1,149 records carry a
  4-char motion name** (plus category metadata: flag s16 @ record+0xC,
  variant byte @ record+0x1A, in the code's framing where the name sits at
  record+4). Machine-readable decode: `WMXIX-WPRM-DECODE.json`.
- **Table B** (26 group entries @ leaf+0xC4B4; reached by the name lookup
  `FUN_80075FB8`, whose header fields sit at base+0x108/base+0x10C): the
  letter-code namespace (A709, B210, C101, K202, L205, M104, P306, Q303,
  R204, S203, V102, W204…), 94 named records. The code's group-key formula —
  decode(name[0])×10 + (name[1]−'0'), index = decode2(name[2..3]) — was
  **verified against the data** (e.g. `A709` → group 107, index 9 ✓;
  `B210` → group 112, index 10 ✓).
- Cross-validation: W4b's "per-motion parameter catalog in the `edit` leaf's
  region at data-relative ≈0x8A280" is this same Table A record array
  (static data-relative 0x8A280 = wprm leaf + 0x360, inside group 101/102's
  records) — the two lanes' decodes agree byte-for-byte on the record shape
  `[u32][char[4] motion ID][u32][16 B tail]`.

**What wprm is:** a *move-definition* database — it maps a move **command**
(packed key or name) to a motion name + variant + flags. It is keyed by move,
not by wrestler. It does not say which wrestler owns which move.

## Move execution (FUN_800364F0)

Gameplay executes a move from a 12-byte **descriptor** `{key, type,
variant}`:

- type 1 → `FUN_80075FB8(wprm, &key)` (Table B, by name);
- type 2 → `FUN_8007609C(wprm, &key)` (Table A, by packed key — the key
  packs decimal digits in 6-bit fields: group = top two digits, index = low
  three digits);
- the returned record's **+4 field is the motion name** and
  **byte +0x1A bits 1–5 are the variant**; the name is then checked/loaded
  through the motion manager (`FUN_8008A3AC`, and the `FUN_80226404` →
  `FUN_8008A548` path). If no record matches, a default name constant from
  `.sdata` is used instead.

## The wrestler layer — traced, and where it ends

- The three names at offset +0x30 of a wrestler record **are** read as
  motion names by the game: `FUN_801CCE94` (sole caller: the editor/match
  setup state machine `FUN_801D2CCC`, 3 call sites) variant-checks exactly
  three consecutive names at record +0x30/+0x34/+0x38, and `FUN_801CD9B8`
  copies all four codes at record +0x30..+0x3F into the live wrestler object
  at +0x514..+0x520. For The Rock those fields are the Defwres codes
  **A002 / 0000 / C000 / D106** — letter-code (entrance-class) motions, with
  A002 already identified in the fragment as his entrance. They are **not**
  the grapple specials, which are numeric `move.mpc` IDs reached through
  descriptors.
- The editor's record accessor `FUN_801D7CA0(db, i, j)` =
  `*(int *)(*(int *)(db + 0x244) + i*0x20 + 0x1C) + j*0x80` — a database of
  0x20-byte entries pointing at blocks of 0x80-byte records. Its backing
  file was not identified in this lane (Defwres.dat's 72×0x80 records fit
  the stride but are appearance/stats/codes, per W4).
- The in-match state machine (`FUN_8012BAF8` and callers in
  0x8012B000–0x8014F000) builds descriptors from wrestler-object fields that
  are filled during play; the **initial fill** — where a wrestler's default
  per-slot descriptors come from at match load — was not isolated. No
  function was found that loops over wprm groups per wrestler, and no
  wrestler→group table exists in the DOL data sections (scanned for u16 runs
  of Table A group keys: none with ≥16 varied values).
- Additional empty searches this lane: `static.mpc` `edit` leaf (112,448 B —
  zero motion-name windows), `boss` leaf (45,376 B — only the 0x2222 graphics
  pattern), `anim` leaf (zero), `com_dt` `char` leaf (1,536 B = 64 attribute
  records of 24 B — too small to hold move assignments), `EMotName.dat`
  (entrance/taunt names only; confirms A002 = ROCK).

**Where the trail ends:** between "wrestler object exists" and "descriptor
{key, type, variant} is executed". The wrestler's default moveset is either
constructed at runtime from data not yet identified (candidates: the
`FUN_801D7CA0` database's backing file; a per-wrestler block inside a
package leaf not yet structurally decoded; derivation from Defwres binary
fields + wprm categories), or filled by a constructor this lane did not
isolate among the 3,902 functions.

## Route 3 — Dolphin runtime observation plan (what would crack it)

The static trail is exhausted; the dynamic one is short because the
chokepoints are known:

1. Boot WMXIX in Dolphin with the Ghidra-derived addresses. Set a breakpoint
   on **`FUN_800364F0` (0x800364F0)** filtered to the player wrestler = The
   Rock, or on **`FUN_8007609C` (0x8007609C)** / **`FUN_80075FB8`
   (0x80075FB8)**.
2. In a match, perform each special: Rock Bottom (Front Grapple), People's
   Elbow (Upper Down Grapple Facing Up), People's Spine Buster (Irish Whip
   Grapple). At the breakpoint, read the descriptor `{key, type, variant}`
   and the returned record: **record+4 = the motion ID**. That is the
   assignment, observed — not guessed.
3. Map each motion ID to its clips via `WMXIX-MPC-INDEX.json`, extract and
   decode via the proven YANM path, and extend the fragment
   (mk:MK-1240 / mk:MK-2843 / mk:MK-1885).
4. Oracle for sanity: the in-game motion viewer (`//viewer/motion/` 85xx set;
   wprm Table A group 351 lists the same viewer namespace) can play a motion
   by ID, so each observed ID can be eyeballed against the named move before
   it is written into the fragment.
5. Alternative static continuation: identify the backing file of the
   `FUN_801D7CA0` database (trace `*(db + 0x244)`'s initialization at boot),
   or find the wrestler-object constructor that writes the descriptor array
   later read by the 0x8012B000–0x8014F000 state machine, and follow its data
   source.

## Honesty notes

- No clip is assigned to any of the three specials by this lane. Per-clip
  durations are not calibrated for `.mpc` and none are claimed.
- Claims above are limited to what the decompiled code and the decoded bytes
  show; inferences are labeled as such (e.g. the identity of the four
  loop-registered packages, the purpose of `mstb`).
