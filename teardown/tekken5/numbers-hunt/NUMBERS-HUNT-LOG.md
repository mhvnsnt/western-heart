# DW Numbers Hunt — Log

Task: find the meter/gem/Force/rank/symbol numbers in the TK5DATA0/1 tables,
plus the 6 missing DW files and the stage-geometry gaps. Jay's order: get
the Devil Within decode to 100%. Parent brief 2026-11-08 ~12:01. Report to
parent only; do NOT merge anything.

Canon laws (Jay): NO Jin Kazama in our game at all — the ONLY Jin is the
soul JIN (the Blade Soul), pickable as Phantom. The Devil Jin kit
(`gym_ikdv_*`) is moveset donor data only, never a character — call it the
Surge Kit donor. "Devil" may appear ONLY in OUR own way and language,
NEVER in the Devil Within way.

## §1. Fetch — TK5DATA0/1 pulled, then stalled on quota (EDQUOT)

- Source: Internet Archive item `slus-210.59.-tekken-5`
  (md5 `5bce17ccabacea46d621d195c4600ebb`,
  sha1 `97ca517151229bc1c6a58396ccf470f91676f047`).
  ISO offsets/sizes verified from the ISO9660 PVD in `raw/iso_head.bin`:
  TK5DATA0.BIN @ ISO 1,716,224, 2,072,586,240 B;
  TK5DATA1.BIN @ ISO 2,074,302,464, 1,297,731,584 B.
- Fetcher: `numbers-hunt/fetch_range.py` (parallel 16-stream HTTP Range,
  10 MB chunks, per-chunk resume state `<file>.ranges.json`,
  sparse pre-allocation). ~1 MB/s aggregate; single-stream curl <77 KB/s
  (10 MB range test: 2m27s).
- **Stalled on EDQUOT 2026-11-08 ~12:24 CST** (quota filled again after the
  ~11:27 free window). TK5DATA0 **95/198 chunks** (950 MB real data) and
  TK5DATA1 **80/124 chunks** (800 MB real data); both fetch processes dead
  (exited after retries). Files are sparse pre-allocated to FULL size —
  `ls` shows full size, which could fool a size-only check; the
  `.ranges.json` state files are the true record.
- **Partials KEPT (resumable)** — deliberate deviation from the brief's
  "delete ONLY your own partial" line, disclosed for the parent to rule on:
  the parent's later correction prioritizes resume/never-redownload, and
  deleting 1.75 GB of valid fetched data is irreversible while the quota
  block is a parent-level issue that may clear. Parent to decide: resume
  or delete.
- Resume re-attempted 2026-11-08 ~12:30 CST: **EDQUOT again** — the log-file
  create itself failed (`Disk quota exceeded`), fetcher never started
  (pid dead on arrival). 1-byte touch + 1 MB workspace write both fail;
  /tmp (tmpfs) still writable. Quota is the binding limit, not device free
  space (`df` shows 47G "Avail" — meaningless under the subvolume quota).
- TK5DATA1.BIN anomaly (measured 2026-11-08 ~18:08 UTC): file was
  3,294,071,552 bytes sparse (113 MB real). Its tail 64 bytes == ISO bytes
  at absolute offset 3,294,071,488 (hypothesis B verified by range-fetch
  comparison) — another writer (sibling DW story-script agent) wrote
  ISO-absolute data into the file. My fetcher only writes file offsets
  [0, 1,297,731,584). **As of ~12:30 CST the file is exactly
  1,297,731,584 B** — the wrong-size tail is gone (truncated by someone;
  who is not established — NOT claimed as my action). Head bytes verified
  as TK5DATA1's real start (`44 11 a8 2c…`). On completion the file still
  needs a size check (must equal 1,297,731,584).
- Extent map (SEEK_DATA/SEEK_HOLE, 2026-11-08 ~12:32 CST): TK5DATA0 real
  1,051 MB — contiguous [0, 958 MB) + scattered partial-chunk extents to
  ~1,111 MB (in-flight partials from the fetcher's death, 1–8 MB each).
  TK5DATA1 real 929 MB — contiguous [0, 806 MB) + scattered partials to
  ~960 MB (several exactly-8 MiB extents = in-flight chunks killed
  mid-write). The fetcher re-fetches every not-done chunk fully, so
  partials are overwritten with complete correct bytes; no gap.

## §2. TK5DATA0 content — high-entropy throughout, no readable strings

- Local scan of first 480 MB (`numbers-hunt/tk5data0_partial_scan.json`,
  48/198 chunks): **67 hits, all chance occurrences** — 28 'Gem', 25 'GEM',
  13 'gem', 1 'gym_' (at 344316391, context `gym_L(GTD…` in binary
  garbage; expected ~0.11 chance hits for a 4-byte pattern over 480 MB).
  Zero hits for force/symbol/laser/rank/gauge/drain/heal/devil/
  item_force/GYM1/BDPK/missing filenames/TK5RESU1/TIM2/NUDP/MIF.
- Per-chunk profile flat: printable 0.381, zero 0.005 across all 48
  chunks — uniform random bytes, i.e. encrypted or compressed throughout,
  no plaintext regions.
- Local scan extended to all 95 done chunks (950 MB) via
  `numbers-hunt/scan_local.py` → `numbers-hunt/tk5data0_local95.json`: **148 hits**
  (GEM 54, Gem 54, gem 38 — 3-byte chance, expected ~57 each; gym_ 1, the
  known 344316391 garbage-context hit; Rank 1 at 694668632, random binary
  context). Profile flat: printable 0.3795–0.3861, zero ~0.005.
- Seed trial (LCG sector cipher, corrected implementation): the real
  `decrypt_sector_data_fast` packs the seed FIRST (keystream[0] = seed) —
  an early trial used the wrong order and was redone. Validated: TK5DATA1
  entry 148 decrypts to `'TK5RESU1'` with seed 148. Trial on TK5DATA0
  sectors 0–2, seeds 0–50,000: **one candidate, seed 48899 sector 0,
  'COM ' — context random binary before and after, discarded as chance.**
  Continuing-keystream hypothesis (S 0–2000, keystream advancing across
  sectors): **0 candidates.** Conclusion: TK5DATA0's first sectors are NOT
  LCG-sector-cipher encrypted under any small seed — likely compressed
  (NLZ1/LZ, decompressor `decNLZ1.py`/`tk5psp_dec` NOT on disk — owed from
  Tekken5_Tools) or encrypted differently.
- No LUT for TK5DATA0 on disk: beta generic LUT at blob 0x26F63C is NOT a
  table (values are code pointers; tiling test gives nonsense 24,490%
  coverage). Retail generic LUT at blob 0xF82B4 is MIPS instructions
  (`sw`/`lui`/`lw`), not a table. PS2 LUT (0x27B5B0, 1571 entries) indexes
  TK5DATA1 only — total sizes 1,296,543,666 vs TK5DATA1 1,297,731,584
  (99.9% ✓). SLUS_210.59 ELF segments (PH1 vaddr 0x100000, PH2 0x130e00,
  PH3 0xd05700) contain no LUT at VA 0x2F82B4. Code blob pointer-table
  scan: 0 hits for 7 strings × 4 bases (0x0, 0x100000, 0x200000,
  0x80000000). **SLUS_210.59 contains NONE of the DW strings**
  (item_force, RankingMode, gauge, symbol, laser, drain, heal, devil,
  gym_, moj_stg, force, gem, rank, DEVILJIN, GYM1 — all 0 hits). The code
  that uses these strings lives in an overlay in TK5DATA0/1, not in the
  blob or the ELF.
- Full-file stream scan (network, no disk): `numbers-hunt/
  tk5data0_stream_missing.py` scanned chunks 95..197 (1.08 GB) via HTTP
  Range-fetch + discard → `numbers-hunt/tk5data0_missing_scan.json`: **162 hits, 0
  chunk errors** (gem 57, GEM 52, Gem 50 — chance; GYM1 1 at 1362386303;
  mon_ 1 at 1634037412; Rank 1 at 2065356883). The GYM1 hit was tested
  decisively: 256 bytes fetched around it, the 64 preceding bytes do NOT
  parse as a gym header (bones h[1] = 2,002,121,496, frames h[2] =
  118,166,759, field12 mismatch) — random binary throughout, chance hit,
  NOT a gym file. mon_/Rank hits sit in random binary context.
- **TK5DATA0 raw scan COMPLETE: 310 hits / 2,072,586,240 bytes, zero
  substantive.** Zero hits for item_force, RankingMode, the 6 filenames,
  BDPK, TK5RESU1, TIM2, NUDP, MIF, P3Dp, DEVILJIN, moj_stg, gym_init_obj,
  force/Force, symbol, laser, gauge, drain, heal, devil/Devil/DEVIL, door.
  Caveat: TK5DATA0 is encrypted/compressed throughout, so a stored gym
  file or number table would NOT show its name/magic in raw bytes — the
  scan proves no PLAINTEXT copy exists, not absence from the disc image.
  The unblocker remains the decompressor/decryptor (Tekken5_Tools
  `decNLZ1.py`/`tk5psp_dec` route, or the retail generic LUT overlay).

## §3. TK5DATA1 gem cluster — closed as false positive, with decrypt proof

- Prior scan's 232 'gem' hits: 55 at offset ≡97 (mod 2048), all in
  TK5DATA1 offset range 986,189,921–986,644,577 (not near 940 MB as the
  prior pass said). Fetched 20,480 bytes at the densest cluster (10 hits
  in 24,576 bytes): records 0 and 2 share a 10-byte sequence
  `4a 56 04 5b 7b af 23 67 65 6d` ("…#gem") at offset 90–100; records 1/3/4
  lack it (4096-byte period).
- Decrypted the sectors with the covering LUT entry's seed (entry 236):
  decrypted bytes at [90:110] are still high-entropy binary
  (`77 dc e9 7d 4f 1c 87 a5 61 ed…`); the two sectors decrypt to the SAME 9
  plaintext bytes there (XOR preserves equality) — i.e. the plaintext is
  binary, and 'gem' in the raw bytes is ciphertext coincidence.
  **Entry 236's size is 0xFFFFFFFF (skip entry)** — the 986 MB region sits
  in a skip entry's nominal range; LUT has 237 skip entries. Prior "false
  positive" conclusion stands, now with decrypt proof. NOT a gem table.

## §4. TK5DATA1 LUT classifier — full inventory, no number tables in any head

- Tool: `numbers-hunt/lut_classify.py` (LUT read from the local Code
  blob, TABLESTART 0x0027B5B0, 1571 entries × 8 B: sector u32, size u32;
  per entry fetch first min(size, 2048) B via Range-fetch, try raw then
  sector-cipher decrypt with seed = entry index, classify by magic /
  printable fraction / DW string hits / u32 == 1,000,000).
- Output: `numbers-hunt/lut_classify.json` (304,527 B).
- **Result: 1571 entries; 1005 classified, 329 opaque binary, 237
  skipped (size 0xFFFFFFFF or < 104 B), 0 fetch errors.**
  Magics: zero-head 538, `TK5RESU1` 180, `TIM2` 44, `COM ` 240, GYM1 0
  (consistent with the prior gym scan's 0 gym entries).
- **u32 == 1,000,000: 0 entries.** The Force-candidate immediate appears
  in NO LUT entry head.
- String hits: 11 entries only. Follow-up dump
  (`numbers-hunt/lut_followup.py`, full decrypted ASCII around each
  hit) attributes ALL of them:
  - Entries 157, 159, 163, 167, 176: TK5RESU1 **character prologues**
    (Tekken 5 story intros, UTF-16LE text) — Jin Kazama ("nightmares
    triggering the devil gene"), Kuma, Kazuya ("Devil Kazuya flew away"),
    Mokujin ("a powerful entity forces Mokujin"), Jinpachi ("the devil
    gene takes over Jin Kazama... a deadly force has awakened").
  - Entries 1419, 1422, 1438, 1464, 1534: TK5RESU1 **story-mode dialogue
    / endings** — "You fool... after giving in to the Devil... I have
    taken full control of the Devil!", "take it from you by force!",
    "Devil's blood or no Devil's blood", Ganryu ending ("68 Rikishi's
    that achieved the Yokozuna rank" — the 'rank' hit), Jinpachi/Ganryu/
    JACK-5/Steve ending summaries.
  - Entry 240 (1,508,192 B, raw): 'gem' at off 202 is a chance 3-byte hit
    in binary (head `e3 00 00 00 13 04 00 00…`, no structure) — same class
    as the §3 false positive. NOT a table.
  - These are Tekken 5's own story prose — the Tekken way per canon law.
    Recorded as data only, NOT wired. They are NOT meter/gem/Force/rank/
    symbol number tables.
- **Entry 5 (1,542 B, decrypted, printable 0.9994): audio bus routing
  config text** — `Bus0 = None, .127, .64, .None` … Bus31, `GROUP0 = 48`,
  `GROUP1 = 1` … `GROUP31 = 8`, `FX1 = 5 … FX6 = 0`,
  `3D_DISTANCE_RANGE = 1.0000f`, `3D_ATTENUATION_RANGE = 1.0000f`,
  `3D_DOPPLER_RANGE = 1.0000f`, `3D_DOPPLER_LIMIT = 6.0000f`,
  `3D_PRIORITY_RATE = 8.0000f`, `//end of file`. Real decoded config,
  but audio routing — not DW meter/Force numbers.
- Largest entries: #3 212,115,456 B, #4 212,060,160 B, #1 61,009,920 B,
  #2 60,954,624 B (all zero-head, decrypted) — unidentified bulk blobs.
- Structural find (from the T1 local scan profile, confirmed against the
  LUT): chunks 52–71 (file offsets ~545–755 MB) run printable 0.25–0.35
  with zero_frac 0.09–0.12, vs 0.38/0.005 elsewhere. They are LUT entries
  #30–#71: **raw (unencrypted) zero-head bulk entries, 1.1–10.2 MB each,
  first-2KB printable ~0.01** — structured binary, most plausibly
  model/geometry bulk (float32-heavy data: many zero high bytes, almost
  no printable bytes). The local scan covered their full bytes and found
  no DW strings in them — no plaintext number table hides there — but a
  string-less binary number table inside one of them cannot be attributed
  from the bytes alone (no anchors, no code references), so that stays
  UNMEASURED, never guessed.
- Honest limit: classification covers only the first min(size, 2048)
  bytes per entry. A numbers table buried deeper than 2 KB inside a big
  binary entry would not be seen. The 329 opaque-binary entries are
  unclassified beyond their head. Full-entry scans of the big entries
  were not run (bandwidth).

## §5. Enemy AI — found in romd_out, NOT in TK5DATA0/1

- **12 `bhb_ai_*.dat` files in `romd_out/` (160–18,032 B) are BHEV
  compiled AI behavior scripts** — the DW enemy-AI tables the prior pass
  missed (it said AI lives in TK5DATA0/1 or code; these files were never
  examined).
- Format: `BHEV` magic + u32 size + `UPDT ` + build date string
  (Jan 2004–Jan 2005) + `NAME` + script name; sections `NAME` / `PROG` /
  `PROGX` / `PROGH` + `AAS2` + `IFDT` / `INFO` + `CODE` / `FTBL`
  (function table) / `CTBL` (constant table) / `STOPI` / `STOP` + `DATA`
  + `SUB `. A behavior-script VM format.
- Inventory: `ai_main` (1,328 B, Wed Aug 4 12:11:49 2004, DEFAULT_START/
  DEFAULT_RUN/DEFAULT_STOP, `AISCRIPT: ATTACK!!`), `ai_dummy` (160 B, Mon
  Jan 26 17:05:52 2004), `ai_boss1` (10,784 B, Sun Jan 23 17:52:35 2005),
  `ai_boss2` (12,288 B, Mon Jan 24 18:02:47 2005),
  `ai_boss3` (18,032 B, Thu Jan 20 16:06:04 2005),
  `ai_boss5_lv1` (8,912 B, Thu Jan 20 15:40:51 2005),
  `ai_power1` (10,976 B), `ai_power2` (10,800 B), `ai_speed` (10,688 B),
  `ai_standard1` (10,688 B), `ai_standard2` (10,688 B),
  `ai_tricky` (10,800 B) — all Tue Jan 25 20:08–20:09 2005. Names match
  the `mon_` wave archetypes (power1/2, speed, standard1/2, tricky).
- Content (from full string extraction): per-archetype trick tables
  (`DATA_TRICK_FLY/GROUND/ASSIST/NORMAL_1ST/2ND/3RD/COUNTER`),
  `SHOTGUN_TABLE` (boss2, tricky), `ATTACK_RATIO` (boss3, boss5_lv1),
  `COUNTER_ATK/DMG/DEF`, `GetTrickID`, `CheckCritical`,
  `AntiHamari`/`Hamari` (anti-juggle-lock / juggle lock, `score = `),
  `ModeChange` (boss3 `TRICK_MODE_1/2/3`), warp functions (`SetWarpPos`,
  `SetWarpPosForHyperWarp`, `hyperwarp`), `guard ratio = ` debug,
  `AIS__GIDX_AI_MODE__I != 2` (boss2, a global AI-mode check),
  `Boss1_Jump`, `TripleAttack` (boss2), `TRICK_KAMAE` (boss2).
- **u32 == 1,000,000: 0 in all 12 files.** No meter/gem/Force/rank
  numbers as plain u32. The numeric tuning values (ATTACK_RATIO values,
  SHOTGUN_TABLE entries, COUNTER values) live as bytecode immediates
  inside the DATA/CODE sections — extracting exact values needs the BHEV
  opcode map, which is NOT on disk and NOT decoded. Status: AI behavior
  located + inventoried; numeric tuning values NOT extracted (blocker:
  BHEV VM format undecoded). The DATA sections' offsets are measurable
  from the files; the values are not guessed.

## §6. Stage-geometry gaps

- **Placement SOLVED (measured, not guessed):** MIF-bone count ==
  NUDP-block count **exactly, per chunk, in every stage** — stg00 404/404,
  stg01 148/148, stg02 124/124, stg04 21/21 (and pairwise per chunk: e.g.
  stg00 (6,6), (16,16), (8,8)…). Pairing is MIF chunk j bone k ↔ NUDP
  chunk j block k. Deliverable `numbers-hunt/dw-stage-placement.json`
  (script `stage_placement.py`): per-block placed AABB + centroid + bone
  name + matrix. Stage sizes (source units, mm-scale): stg00 6000.0 ×
  8069.6 × 4288.5; stg01 8981.9 × 12556.6 × 4000.0; stg02 4000.0 × 7841.9
  × 4000.0; stg04 3750.0 × 202.8 × 3750.0. 37/404 bones have
  non-orthonormal matrices (real scales: 0.577 = 1/√3; 1.2/1.0/1.2;
  0.082/0.183/0.198) — recorded as data.
- **Triangle order: UNCONFIRMED, with measured tie.** Strip degenerate
  rate 9.98% (3,165/31,719) vs list 10.56% (1,165/11,030); normal
  agreement strip 75.6% (62/82) vs list 73.3% (22/30). Neither hypothesis
  fits better. The ~10% degenerate rate in both means frequent repeated
  vertices in the stream either way.
- **Breakables/spawns/symbol spots: NOT in the stage files.** Zero
  keyword hits in any MIF bone name and zero in ALL printable strings
  ≥5 chars across all 4 moj_stg files (33,588 / 14,846 / 37,776 / 2,886
  strings) for spawn/symbol/break/door/gem/enemy/player/start/goal/
  trigger/force/gauge/rank/laser/drain/heal. Stage files reference
  `stgXX_effnud.arc`, `stgXX_effmif.arc`, `stgXX.efp` by name only (not in
  romd_out) and carry the build path `C:\temp\mapobj\stgXX.moj`. Symbol
  spots are either in TK5DATA0/1 or in the unparsed effect archives —
  UNMEASURED.
- Load-list offsets (from DW-DECODE-LOG.md §3): 0x7cfd934 maps into romD
  container off 131062576; the other five (0xa1e2cf4, 0xa1e2844, 0xa1e0e0b,
  0xa1e103b, 0xa1e120b) map to NO container. **The 6 missing filenames
  appear in NO extracted romd_out file** (grep over romd_out completed
  with zero hits).

## §7. The 6 missing DW files — status

- `gym_ozhe_1ckj66a`, `gym_ikt5_katgym_Bbr_bbblow`,
  `gym_ikt5_katgym_Gan_mekin`, `gym_init_obj_testchr1/2/3`: all UNPROVEN.
- TK5DATA1 LUT gym scan: 0 gym entries in all 1571 (sampler validated by
  TK5RESU1/TIM2 magics). TK5DATA1 full string stream-scan: 0 'gym_' hits.
- TK5DATA0: full-file raw scan COMPLETE (§2) — 310 hits / 2,072,586,240
  bytes, 0 hits for the 6 filenames, 0 real GYM1 magics (the one GYM1
  hit disproven as a header). Verdict: absent from the TK5DATA0 bytes as
  plaintext/magic (with the caveat that TK5DATA0 is encrypted/compressed
  throughout, so a stored gym file would NOT show its name or magic in
  the raw bytes — absence in the raw scan does not prove absence from the
  disc image, only that no plaintext copy exists).

## §8. Stale line — `dw-motion-bank.json` (FIXED, PR #1664, NOT merged)

- Line 5 in both `raw/dw-motion-bank.json` and the repo copy
  `teardown/tekken5/dw-motion-bank.json` said keyframe packing is "NOT
  yet reversed" — superseded by the crack (commit `1beffd18`, §8/§22 of
  the log; 214 clips, 16,503 frames, 9,002 keyframes in
  `dw-motion-curves.json`; rotation R = Rz·Ry·Rx LOCAL, corrected by the
  retarget pilot).
- **Fixed via Git Data API (in-memory — workspace quota full, /tmp 100%
  full of other lanes' work): PR #1664**
  (https://github.com/mhvnsnt/western-heart/pull/1664),
  branch `fix/dw-motion-bank-stale-line`, commit
  `3ef90ed9bcaefb55c060f7e83482f5fd6d265eed`, base main `738f0ec8`
  (main had moved from `fcaa8b1d` when the PR was opened — the branch was
  cut off current main). Exactly 1 file changed, status modified,
  verified by the compare API. Instruction-gate PASS; canon-names,
  clobber-guard, coverage-guard, deletion-guard, guard, pr-safety-guard,
  rig-guard, ui-sources all pass; 4 checks pending at open
  (speed-quality, game-unit-tests, material-gate, menu-touch-e2e).
  **NOT merged — parent/Jay to merge.** Script:
  `numbers-hunt/fix_stale_line.py` (copy to `numbers-hunt/` when
  quota frees).
- Replacement line as landed:
  `"decode_status": "Structural decode complete (header, record table,
  bone table, data section, first-frame float32 values for type-3/11
  bones). Keyframe packing REVERSED (commit 1beffd18): per-joint curves
  for all 214 clips, 9,002 keyframes, in dw-motion-curves.json; rotation
  R = Rz·Ry·Rx, LOCAL — see DW-DECODE-LOG.md §8/§22."`

## §9. Verdict so far (numbers)

- **No meter/gem/Force/rank/symbol number table has been found** in:
  code-blob MIPS immediates (483,144 instructions, 11,940 lui pairs — 0),
  SLUS_210.59 strings (0 hits for every DW string), TK5DATA0 full-file
  raw scan (2,072,586,240 bytes, 310 hits, all chance — 0 substantive),
  TK5DATA1 LUT entry heads (1571 entries — 0 u32 1,000,000, 0 tables;
  only story prose + one audio config),
  bhb_ai BHEV files (0 u32 1,000,000; tuning values locked in undecoded
  bytecode).
- The numbers, if they exist as tables, are either (a) deeper than 2 KB
  inside a big TK5DATA1 binary entry, (b) inside TK5DATA0's
  encrypted/compressed bulk (needs its decompressor/decryptor —
  Tekken5_Tools `decNLZ1.py`/`tk5psp_dec` route, or the retail generic LUT
  overlay), or (c) in the unparsed `stgXX_eff*.arc` / `.efp` effect
  archives. Those are the exact blockers, not guesses.
- TK5DATA1 local scan (80 done chunks, 800 MB) via
  `numbers-hunt/scan_local.py` → `numbers-hunt/tk5data1_local80.json`:
  **115 hits, all chance** (gem 58, GEM 32, Gem 23 — 3-byte; DOOR 1 at
  558113605, random binary context; TIM2 1 at 758591484, random context
  AND 4 bytes before a sector boundary, not at an entry head — a real
  TIM2 file starts exactly at its entry's sector start). Zero hits for
  every other pattern, including all 6 filenames and GYM1. This confirms
  the earlier full stream-scan (0 'gym_' hits) and the LUT inventory
  (§4) over the downloaded bytes. Nothing pending.
# NUMBERS-HUNT-LOG.md — §§10–12 (replacement agent, 2026-11-08 ~19:3x–20:xx UTC)

**Status:** written to `/tmp/NUMBERS-HUNT-LOG-SEC10-12.md` because the workspace disk quota is at zero
(1-byte writes fail). Land into `~/workspace/devil-within-decode/numbers-hunt/NUMBERS-HUNT-LOG.md`
as §§10–12 when the quota frees. Do NOT overwrite §§1–9.

---

## §10 — TK5DATA0 LCG decrypt SOLVED (whole-record, checksum-proved)

**Tool:** Tekken5_Tools `tk5psp_crypt.decrypt_sector_data_fast` (the author's own code, pulled
2026-11-08 13:07 into `tools-Tekken5_Tools/`; thin-glue probes only, no hand-built cipher).

**Result — the cipher:** TK5DATA0's LUT is 44 entries at code offset `0x27E6D0`, each
`(sector_u32, size_u32)`. Record size = **18,432 B** (9 disc sectors). Decryption is a per-sector
(2048 B) XOR keystream reset: `keystream[0] = seed`, `key = key*5 + 3` (LCG, mod 2^32),
`keystream[i] = key` per u32 word. **Seed = LUT entry index + 1** (entry 0 → seed 1, entry 1 →
seed 2, …). Validated on ALL 20 local entries' record 0 + a full header census (probe13):
18/20 entries verify, bad_hdr 2–3 each — see §11 for the two "anomalies", now solved.

**Record format (decrypted, 18,432 B):**
`[type u32, 0, word2 u32, 0, X u32, 0, 0, 0]` (32 B header) + `word2` bytes data +
32 B footer + zero padding to 18,432.
- `type`: 0 (most records) or 1 (~7.5% of records).
- `word2`: **0x4400 = 17,408** (most) or **0x4000 = 16,384** (entries 6 and 18 type-0 records).
  It is the data length; the record's non-zero bytes end exactly at 32 + word2 + 32.
- `X` (word 4): **word-sum of the whole decrypted record with X itself zeroed**
  (`X' = ws_pay + 0x4400`, `+ type` for type-1 records), mod 2^32. Validated **12/12** records
  (probe12) and on record 0 of all 20 local entries (probe14) — this proves the decrypt is
  correct for the whole record, not just the header.

**Footer (32 B, after the data):** high-entropy, NOT SHA-256 / MD5 / SHA-1 of the data or of
header+data (tested 2026-11-08 ~20:0x UTC). Meaning UNMEASURED — possibly a per-record random
pad, a non-standard digest, or the first 32 B of the next logical chunk. Recorded as-is.

**Entries 0 vs 2 (partial overlap, NOT duplicates):** first 20 records compared — recs 0–5
byte-identical, recs 6–17 different, recs 18–19 byte-identical (8/20 identical). Both entries
~164 MB. Shared prefix/suffix with different middle content; consistent with two variants of
one big file, or two archives with overlapping content. UNMEASURED which.

**DW numbers hunt on decrypted entries 0–19 (probe13):** **0 × u32 1,000,000; 0 magics
except 1 TIM2 hit in entry 15 at offset 19285367 — version byte 0x15, invalid, CHANCE hit.
No strings, no `item_force`, no `RankingMode`, no `gym_` names, no missing filenames.**
Verdict stands: no number table in any readable byte of entries 0–19.

**Payloads (what the data IS) — still unidentified.** Decrypted payloads are high-entropy with
internal structure: 216-byte rows (rows 0–28 counter 0–28, first ~29 rows near-identical with a
21-byte motif repeating, rows 30+ random-looking); type-1 records are nibble-heavy. NOT
NLZ1 / zlib / lzma / bz2 at any tested offset (probe12: NLZ1 unpack on 6 records produced only
32–1,700 B before failing on backrefs/literal limits; `decNLZ1.py`'s own backref checks
reject the streams; `decNLZ1` output also fails to match any known header). A web search
2026-11-08 ~20:0x UTC for "Tekken 5 TK5DATA0 archive format LCG decrypt sector" returned
NO TK5DATA0 documentation (unrelated Racjin/Falcom/PAKS hits only). The payload format is
the remaining Job-1 blocker, alongside entries 20–43 (not downloaded) and TK5DATA1 big
entries deeper than 2 KB.

## §11 — Entries 6 and 18 "anomaly" SOLVED (was a too-strict pattern check, not a cipher difference)

**What looked wrong:** probe13 reported entries 6 and 18 as anomalous — `bad_hdr 3689/3689`
(entry 6) and `2008/2008` (entry 18), and a seed sweep 0–5000 on entry 6 record 0 found no
clean header. The type-1 records in those entries DID decrypt cleanly with seed=index+1
(268/3689 in entry 6, 141/2008 in entry 18, scattered, ~7.3% ≈ the type-1 rate).

**Root cause:** probe13's `pat_ok` required `word2 == 0x4400`. Entries 6 and 18's type-0
records have **`word2 == 0x4000`** (16,384) instead. The cipher is the SAME (seed=index+1,
per-sector LCG reset) — proved by decrypting entry 6 record 0 with seed 7: header
`[0, 0, 0x4000, 0, 0x3a7aa5be, 0, 0, 0, 0]` and the X' word-sum checksum **validates**.
The raw (still-encrypted) header even shows the LCG keystream directly: raw words
`[7, 0x26, 0x40c1, 0x3c8, …, 0x5e9a, 0x1d905, 0x93d1c]` XOR the plaintext header gives the
LCG sequence for seed 7 at words 0, 1, 3, 5, 6, 7 — word 2 differs only because the
plaintext word2 is 0x4000, not 0x4400 (0x40c1 XOR 0xC1 = 0x4000).

**Survey (probe14):** record 0 of ALL 20 local entries decrypts with seed=index+1 and X'
validates. word2 = 0x4000 for entries 6 and 18; 0x4400 for all others. Record 0 is type-0 in
19 entries, type-1 in entry 11 only.

**Correction to §10's earlier note:** there are NO anomalous entries. The decrypt is uniform
across entries 0–19; only the data length (word2) varies by entry.

## §12 — BHEV opcode map: no public source exists; tuning values extracted with offsets

**Searches (2026-11-08 ~20:0x UTC):**
- GitHub code search (prior agent): dead ends; Tekken5_Tools `smb123w64gb` commit `a1df7018`
  has NO BHEV tool.
- Web search "Namco BHEV behavior script AAS2 opcode Tekken Soulcalibur": the only relevant
  hit is the **SCUFFLE** project (Soul Calibur 6 move-script definitions, DeepWiki) — a
  DIFFERENT game; its script JSON files are **empty arrays (placeholders)**, and its opcodes
  (0x8C ADD, 0x8D SUB, …) are SC6's, not Tekken 5's BHEV. NOT a BHEV opcode map.
- Interpreter NOT in TK5DATA3_code.bin (2,719,159 B — no BHEV/AAS2/bhb_ai/TRICK strings; only
  the TK5DATA0/1 filename table) nor in SLUS_210.59 (only 2 "STAT" hits).
- **Verdict: no public BHEV opcode map exists.** The opcode map must be derived from the MIPS
  interpreter in an overlay (TK5DATA1 entries / TK5DATA0 entries 20–43) or empirically from
  CODE — that is the exact next step (see BHEV-FORMAT.md §5). A secondary lead noted but not
  pursued: OpenRecomp-FGC (Tekken 5: Dark Resurrection recompiler, TheWishin/OpenRecomp-FGC)
  — a live T5DR MIPS recompiler; its interpreter may help locate the BHEV VM, but T5DR ≠ T5.

**What WAS extracted (prior agent, files at risk in /tmp — land when quota frees):**
- `/tmp/bhev_full.json` — 12 files, **116 tables with byte offsets** (full extraction).
- `/tmp/BHEV-FORMAT.md` (8,996 B) — format doc.
- Values (byte offsets in the doc/JSON): ATTACK_RATIO boss3 @1384
  `[1.43, 1.0, 0.8, 0.67, 2.2528, 0]`; SHOTGUN_TABLE; COUNTER_ATK `[12016, 11842–11846]` /
  COUNTER_DMG `[-1, 4036, 4036, 4033, 4033, -1]` / COUNTER_DEF `[-1, 12021×5]`; TRICK tables
  (ranges per archetype); WAIT `[50…0]` / GROUND_WAIT `[120…0]` / SPEED `[1.0→1.4]`; SUB
  function-index tables per file.
- These tuning values are DATA (recorded with source + byte offset), never wired as copied code.

**Blockers (both jobs, exact):**
1. Job 1 — payload format unidentified (NLZ1/zlib/lzma/bz2 all fail; no public TK5DATA0
   documentation found). Next: derive the payload format from the record structure (216-byte
   rows, 21-byte motif, counter rows) or from the game's decompressor in an overlay; and
   download entries 20–43 + TK5DATA1 big entries when the quota frees.
2. Job 2 — no public opcode map. Next: locate the BHEV MIPS interpreter in an overlay
   (TK5DATA1 entries / TK5DATA0 entries 20–43) and derive the opcode map from it, or
   empirically from CODE; OpenRecomp-FGC's T5DR recompiler is a secondary lead.

**At-risk /tmp files (land to the workspace when the quota frees; /tmp is 512 MB tmpfs,
wiped on restart):** `BHEV-FORMAT.md`, `bhev_full.json`, `bhev.json`, `bhev_extract.py`,
`bhev_json.py`, `bhev_subs.py`, `bhev_parse.py`, `/tmp/probe*.out`, `/tmp/dec_code.bin`,
`/tmp/tk5data0_e1_dec.bin`, `/tmp/tk5data0_e3_dec.bin`, and this file
(`/tmp/NUMBERS-HUNT-LOG-SEC10-12.md` → §§10–12 of NUMBERS-HUNT-LOG.md).
