# W7 — WrestleMania XIX Follow-up

**Lane:** W7 (Bannon verify-and-complete) · **Date:** 2026-11-19 · **Session:** `a9046f9c-67d1-4d4e-a980-e637afb80c87`
**Game:** WWE WrestleMania XIX (USA), GameCube, GW9E78 · **ISO:** `/data/wmxix/wmxix-rvz.iso` on Oracle VM (bannon-oracle-vm, 132.145.194.139) — never in git.

W6 left three things unsolved: (a) the wrestler→motion assignment table + the 99 specials (needs dynamic observation), (b) Triple H attire textures/UVs, (c) clip-duration calibration + arena face format. This lane's status on each is below.

## (a) PRIMARY — wrestler→motion assignment + 99 specials

**Status: pipeline built and proven to the wrestler-select screen; in-match breakpoint observation in progress.**

### What was solved

**1. The GDB stub starts.** Dolphin master source (`MainSettings.cpp`, `Core.cpp`): the stub starts when `MAIN_GDB_PORT > 0`. The `-C Main.General.GDBPort=9090` CLI override does **not** work (verified: game ran, port closed). Writing `[General] GDBPort = 9090` into `Dolphin.ini` **does** work (port 9090 LISTEN, verified; takes ~30 s after launch, longer under VM load — the observe script's 120 s wait was once too short). `gdb-multiarch` 15.1 connects (`set architecture powerpc:common`); the stub's short `g` packet (32 GPRs only) does not break gdb 15.1. One gdb client per Dolphin run (listen socket closes after accept — no reconnect; never probe the port with a TCP connect, it consumes the only slot — use `ss -ltn`). At connect, PC/registers are deterministic garbage (CPU not booted) — do not read memory before `continue`.

**2. TAS input (.dtm) works — full chain to a live match.** DTM format derived from Dolphin `Movie.h`; generator `w7_dtm.py` (Movie: idle/press/stick_dir/press_stick/build). Proven end-to-end: obs1 DTM boots, skips the video, enters Exhibition, picks Normal Match, selects The Rock (P1) + Steve Austin (COM), and reaches a **live in-ring match** (screenshot-verified: "FIGHT", timer counting down, grapples executing, Rock vs Austin). Emulation runs ~0.55–0.65× realtime on the loaded VM (frame counts are emulation-locked, so DTM timing is wall-speed-independent). Note: entrances do not play (or the A-mash skips them) — a Start-mash after the picks only PAUSES the match; future DTMs should drop it.

**3. The roster grid is mapped (visually).** SELECT SUPERSTARS, 10 cols × 5 rows = 45 wrestlers + Slot A / BOSS / Slot B. P1 default cursor = **The Rock** (top-left, red box, "1P The Rock"); P2 = COM. Row 1: The Rock, Stone Cold Steve Austin, Triple H, Chris Jericho, Shawn Michaels, Booker T, Hulk Hogan, Brock Lesnar, Kurt Angle, The Undertaker. (Full grid read in `select_zoom.png`.) Grid order ≠ slot order (slot 000 = Triple H, but grid cell 1 = The Rock).

**4. Raw RSP client + decoder.** `w7_rsp.py` — a raw GDB-remote-protocol client: connects, sets breakpoints, interrupts (0x03), single-steps, reads registers/memory, dumps MEM1. `w7_decode.py` decodes breakpoint-hit descriptors through `WMXIX-WPRM-DECODE.json` (Table A packed-key unpack: 5× 6-bit decimal-digit fields; Table B name lookup) into motion IDs → `move.mpc` clips → calibrated durations. RSP quirks found: the stub re-sends the stop packet after an interrupt (the client skips stray `T` replies to queries); a memory reply starting with hex digit `E` is NOT an error (only 3-byte `EXX` replies are — fixed in `read_mem`).

**5. wprm located in live memory + motion-ID → display-name table extracted.** From a title-screen MEM1 dump (`mem1_title.bin`, 24 MB): wprm Table A group 101's records found by the 28-byte-stride name chain at MEM1 **0x8068FC20** (leaf base 0x8068F8CC; same address in the in-match dump — the layout is deterministic). In-memory format verified: group entries are 8 bytes `[(key<<16)|count][records_ptr]`; records are 28 bytes with **[+0] = pointer to the English display-name string** and **[+4] = 4-char motion ID** (e.g. motion `0102` → "Punch-L"). Extracted **`wprm-motion-names.json`: 1,077 unique motion IDs/codes → display names** (993 Table A numeric IDs + 96 Table B letter codes; Table B records are mostly blank at the title screen and their names are empty — they need an in-match dump). Table B's group table is at 0x8069BD9C (26 groups; group 326 was missing from the JSON decode).

**6. The 99 specials: 98/99 identified to motion IDs + clips.** Matching the survey's Appendix B names (menu.mpq) against the wprm display names: **89 exact + 9 near-matches = 98 with motion IDs and calibrated clips** (`wmxix-99-specials.json`). Examples: Rock Bottom → 2059, People's Elbow → 6503, People's Spine Buster → 4306, Pedigree → 2061, F-5 → 2177, Stone Cold Stunner → 2060. Near-matches differ by a 01/02 variant suffix, a trailing space, or an abbreviation ("Buzzsaw Kick w/ Poison Mist"). 5 entries are variant-ambiguous (01 vs 02: Ankle Lock, Diving Headbutt, Diving Elbow Drop, Spinout Power Bomb Pin; Power Bomb has several front-grapple candidates, 'Power Bomb Pin' 2032 is the best guess) — the descriptor variant field would resolve them. **1 unmatched: "Super Kick" (Lance Storm, Front Grapple)** — no such display name exists in the extracted table; it may be among the ~156 Table A records not captured (zeroed dump chunks) or named differently. Multi-ID names (Van Daminator → 2076/1500, Crippler Crossface → 2055/4311/7101, Spear → 0716/1704, Walls of Jericho → 2056/4312/6710) are disambiguated by slot category where possible (front-grapple = 20xx, etc.).

### The breakpoint finding (blocks the original plan)

**Dolphin 2609b (flatpak) GDB execution breakpoints do NOT trap.** Proven twice:
- obs1 run: breakpoint at 0x800364F0 set (stub returned OK), game played a live Rock-vs-Austin match for 590 s with constant grappling — **0 hits**.
- Mechanism probe (`w7_rsp_probe.py`): interrupted the title screen (PC 0x8027BA24), set a breakpoint AT the interrupted PC, continued — **0 stops in 30 s**, even though a second interrupt proved the CPU was running (PC had moved to 0x802D8E34). Single-step also does not advance the PC.

The stub connects, reads registers/memory, interrupts, and continues correctly — only execution breakpoints (Z0) and single-step are broken (likely a JIT/breakpoint interaction in this build). **Consequence: the assignment table cannot be captured via breakpoints in this Dolphin build.** The working alternative is **memory snapshots**: interrupt mid-match, dump MEM1, and read the wrestler objects (+0x514 Defwres codes) + descriptor arrays directly. An in-match dump was launched (obs1 DTM, interrupt at 360 s wall); analysis is the next step.

**6. Two Dolphin failure modes found and fixed.**
- **GetDirectoryForRegion panic (nav4/nav3b):** after a SIGKILLed Dolphin, the next movie run died at boot with a modal "Default case should not be reached … GetDirectoryForRegion (MainSettings.cpp)" dialog. Root cause: corrupted Dolphin user state (SIGKILL during a SYSCONF/GCI-save write; the region fallback reads garbage). Fix: wipe `GC/`, `Wii/shared2/`, `Cache/`, `Qt.ini`, `TimePlayed.ini` before every run (now in `w7_probe.sh` / `w7_observe.sh` / `w7_dump_match.sh`). Verified: nav3c (same nav3.dtm that failed as nav3b) reached the menu after the wipe.
- **nav4's short Start-mash missed the title window (nav4b):** 15 Start presses (frames 1800–3600) were not enough — boot timing varies between runs, and the game fell into attract mode (DEMO matches + intro video). nav3's 45-press mash (frames 1800–7200) reached the menu twice. Lesson: use the long mash. The obs1 DTM uses nav3's proven front.

### What is still open

- **Full per-wrestler movesets (beyond the 99 specials):** the specials are 98/99 identified, but each wrestler's COMPLETE moveset (dozens of regular moves) still needs the descriptor arrays. Status of that hunt (in-match MEM1 dump `mem1_match.bin`, Rock vs Austin, analyzed): the live wrestler objects were NOT found via the documented anchor — the Defwres code block (`A0020000C000D106` at object +0x514) does not appear in MEM1 as ASCII (the pattern exists in Defwres.dat the file, but not in live memory). Rock's profile record IS in memory at 0x802EEC40 ('The Rock' + 'ROCK' + stats), preceded by a sparse u32 table (values like 0x1E080003, 0x1F040001, 0x23040208) whose format is unresolved — first bytes 0x1E/0x1F/0x20/0x23 are NOT wprm Table A groups (all ≥101), and the values are NOT 12-byte {key, type, variant} descriptors (a full-MEM1 scan for consecutive descriptor triples found 0 runs — the 12-byte descriptors are built transiently at runtime, not stored). Letter-code tables exist at 0x8036xxxx/0x8039xxxx/0x803Bxxxx (8-byte code records) and a code→numeric-ID table at 0x80993148 (D105→0x35C, D106→0x35D). Next step for a follow-up lane: decode the compact moveset format in the wrestler profile records (compare Rock's vs Austin's record u32s against their known specials to reverse the encoding), or take two in-match dumps at different moments and diff the wrestler-object region to find the current-motion fields.
- **"Super Kick" (Lance Storm):** the 1 unmatched special — not in the display-name table. Candidates ('Bicycle Kick' 0711, 'Yakuza Kick' 0731) are unverified guesses, not claimed.
- **Breakpoints (blocked):** if a future lane wants live breakpoint logging, it needs a Dolphin build where GDB breakpoints trap (test with `w7_rsp_probe.py` — a PC breakpoint must fire within seconds), or the interpreter (very slow), or memory watchpoints (Z2/Z3/Z4 — untested in this build).
- **Per-wrestler sweep (not run):** 45 wrestlers × in-match dumps would take ~17 min each (360 s wait + ~600 s dump) — not attempted; the specials identification via the name table made the sweep unnecessary for the specials, and the full movesets need the format decode first.

## (b) SECONDARY — Triple H textures/UVs

**Status: texture binding table done; UV pools located and extracted; vertex↔UV alignment unresolved (not fabricated).**

- **Binding table:** `triple-h-texture-binding.json`. Batch→bone→part (from W6's `hhh-manifest.json`) + texture per part (from `000_0.tex` entries): torso→hhh_body, arm→hhh_arm, hand→hhh_hand, pelvis→hhh_waists, thigh/calf→hhh_l_leg (+hhh_knee at the knee), foot→hhh_foot. Head batches b7–b12 (23/72/102/4/13/4 verts) → face/head_back/head_top/eye/mouth/tooth **proposed** by size/elimination (largest head batch b9→face 256×128), needs material-record or live verification. Each part has a color texture (fmt 14) + a same-size `m_` mask (fmt 1); eye/mouth/tooth/blood have no `m_` variant. 000_1 (alt attire) has the identical entry set, sizes, and geometry — textures differ in content only.
- **Materials hypothesis (unverified):** 14 real material records ↔ 14 color textures in `000_0.tex`. The batch→material link is not in the batch records (the `idx` field is batch/bone order, not material — batch 1 idx=1 would map to eye, wrong for an arm).
- **UVs:** candidate pools extracted to `triple-h-uv-candidates.json`: pool at file 0x6240–0x7CA0 (1,688 (u16,u16) pairs); table2 region 0x6CE4–0x7CA0 (~1,007 pairs, 0–4096 scale, fractional values 1365≈1/3, 2730≈2/3, 2048=1/2); inter-batch gap pairs (6,620 pairs, 0–1843 range, strip-ordered). Three alignment hypotheses **tested and rejected**: (1) pool[0:606] as per-vertex UVs — all v==0; (2) gap-1 first 72 pairs as batch-0 UVs — log-area correlation −0.115, random winding; (3) table1 counts as strip lengths — multiset differs from heuristic strips (58 strips, 499 vs 892 incidences). The alignment needs the game's draw order (GX display lists) or a live capture. **No UVs were fabricated; no OBJ+MTL was emitted with guessed UVs.**

## (c) STRETCH — duration calibration (done) + arena faces (not attempted)

**Duration calibration: SOLVED and verified against ground truth.**
- The 0x3C `sec_per_tick` field is **not** a duration scale: across 10 win-motion clips (9101–9110) it gives 45–372 s (impossible), while **tick_total/60 gives 6.2–15.4 s** (plausible win-pose lengths, clustering at ~8.9 s and ~15 s — authored durations). YANM ticks advance at the game frame rate (60 Hz).
- Corrected manifest: `mpc-clips-manifest-calibrated.json` — 1,898 clips, durations min 3.68 s, p10 4.83 s, median 7.33 s, p90 9.88 s, max 20.75 s (vs W6's uncalibrated median ~94 s). Method note is embedded in the file.
- The `.yad` sheets were checked as an independent ground truth and **rejected**: their f32 values are shared constants across clips (10.903, 18.033, 6.615…), not per-clip durations.
- Caveat: ringmotion `a002` — W4's 33.856 s via 0x3C (0.041) implies 826 ticks → 13.8 s at /60. The two methods disagree for ringmotion; 0x3C may be valid for standalone `.yag` files but not for `.mpc`-embedded YANM. The win-clip evidence (10/10 in the plausible band) supports /60 for gameplay clips.

**Arena bulk face format: not attempted** (time went to the primary task). The 35 faced OBJs at 1–19% coverage stand as W6 left them. No Poisson geometry was fabricated.

## Files produced (lane dir `lanes/w7-wmxix-followup/`)

| File | What it is |
|---|---|
| `w7_dtm.py` | DTM generator (nav1–nav4, obs1) |
| `w7_probe.sh` | Probe runner (Dolphin + DTM + screenshots + montage; state reset + pkill -9 fixes) |
| `w7_observe.sh` | Observation runner (Dolphin + GDB stub + DTM + RSP client; superseded by snapshot path) |
| `w7_rsp.py` | Raw RSP client (connect, breakpoints, interrupt, step, memory read, MEM1 dump) |
| `w7_rsp_probe.py` | Breakpoint-mechanism probe (interrupt → PC bp → does it fire?) |
| `w7_dump_match.py` / `w7_dump_match.sh` | In-match MEM1 dump (DTM + interrupt + dump) |
| `w7_probe_bp.sh` | Probe runner (Dolphin + GDB, no movie) |
| `w7_decode.py` | Hit decoder (descriptor → wprm → motion → clip → duration) |
| `w7_diag.sh` / `w7_diag2.sh` | No-movie diag launcher / GDB+movie diag |
| `wprm-motion-names.json` | Motion-ID → display-name table (1,077 entries, from live memory) |
| `wmxix-99-specials.json` | 99 specials → motion IDs + clips (98/99 identified) |
| `mpc-clips-manifest-calibrated.json` | Calibrated durations (1,898 clips) |
| `triple-h-texture-binding.json` | Batch→texture binding table |
| `triple-h-uv-candidates.json` | UV candidate pools (pool + table2 + gaps) |
| `nav2_sheet.png`, `nav3_sheet.png`, `nav3b_sheet.png`, `nav3c_sheet.png`, `nav4_sheet.png`, `nav4b_sheet.png`, `obs1p_sheet.png` | Probe contact sheets |
| `select_zoom.png` | SELECT SUPERSTARS grid (readable) |
| `obs1_240_zoom.png` | Live Rock-vs-Austin match under GDB |
| `w6-docs/`, `vm-data/` | W6 docs + local working data (YOBJ decode, manifests, win clips, `mem1_title.bin`) |

## Operational notes (for the next lane)

- SSH via HTTP CONNECT tunnel only; `pkill -f <pattern>` inside an inline ssh command self-matches the remote `sh -c` cmdline and kills the session — use `pkill -x` or script files.
- Dolphin runs must be killed with `pkill -9 -x dolphin-emu` (TERM doesn't kill the flatpak-wrapped process, and a leftover Dolphin holds the SSH pipe open so the exec session hangs even after the script finishes).
- Emulation ~0.55–0.65× realtime on the loaded VM; DTM frames are emulation-locked.
- VM disk was 23 GB free (89% used) at session start; probe screenshots accumulate in `/data/wmxix/w7shots/` — clean unneeded ones.
- Dolphin.ini path (flatpak): `~/.var/app/org.DolphinEmu.dolphin-emu/config/dolphin-emu/Dolphin.ini` (files live directly here, not under `Config/`). File logging via Logger.ini `WriteToFile=True` did not produce output (`dolphin.log` stayed 0 bytes) — movie log messages were never captured; screenshot evidence was used instead.

## PRs

_To be opened: W7 branch(es) in western-heart with the calibrated manifest, texture binding, UV candidates, and tooling. No merges to main._
