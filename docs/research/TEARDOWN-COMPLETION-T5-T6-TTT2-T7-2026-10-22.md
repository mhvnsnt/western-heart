# TEARDOWN COMPLETION REPORT — Tekken 5 / 6 / Tag 2 / 7 → 100%

**Worker 72 · 2026-10-22.** Owner directive (verbatim): *"We need to get Tekken 5
and Tekken 6 and Tekken Tag 2 all complete. You're saying they were incomplete,
they should have been 100% done by now."*

## 0. The brief was stale — corrected baseline (verified this session)

The task brief described T5 as "NEVER ACQUIRED", T6 as "~30% PSP-only", TTT2 as
"~15%, needs 13.3GB download". All three are wrong as of 2026-10-22. Verified
against live GitHub Release/API state and byte-level probes this session:

| Game | Brief said | Verified reality 2026-10-22 |
|------|-----------|------------------------------|
| **T5** | Never acquired | **ACQUIRED.** Full PS2 ISO + all TK5DATA archives on `mhvnsnt/game-reverse-engineering` releases `tekken5-iso-v1` (9 parts) and `tekken5-disc-v1` (DATA0/1/2/3 + SHA256SUMS). DATA1 fully extracted (W7b, 2026-10-21): 1,355 files, 464 NUDP models, 1,362 TIM2 textures, 80 costume packs → 80 GLBs + 8 ctype-5 GLBs on western-heart releases. |
| **T6** | ~30% (PSP only) | **PS3 full archive on release.** `tekken6-ps3-full-v1` (draft): `TEKKEN.psarc` in 10 parts + sha256 manifest. PSP side: ISO + 46 endings on releases, EBOOT decrypted, sector cipher reversed. |
| **TTT2** | ~15%, needs 13.3GB download | **Download DONE.** Release `ttt2-7z-v1`: all 26 parts (13.36 GB) + loose-files tar, present and complete. |
| **T7** | ~40% | **Not acquired.** 51 GB full game never pulled. Correctly last priority. |

"100%" here means: full roster models + movesets + animations + stages + audio,
extracted, documented, and referenced from the repo (large binaries on Releases,
never in git). What follows is the per-game gap list with byte-verified evidence
and the exact next step for each gap.

---

## 1. TEKKEN 5 (PS2) — the priority (Devil Within source)

### 1.1 Acquisition — DONE (verified)

- **ISO:** `[PS2](2004) Tekken 5.iso`, **4,483,547,136 bytes**, Internet Archive
  item `ps-2-2004-tekken-5` (also `slus-210.59.-tekken-5`: `SLUS_210.59.Tekken
  5.ISO`, 4,039,974,912 bytes, USA dump — available, not dark).
- **Repo releases (canonical store):** `mhvnsnt/game-reverse-engineering` →
  `tekken5-iso-v1` (ISO, 9 parts + SHA256SUMS), `tekken5-disc-v1` (TK5DATA0/1/2/3
  + `SHA256SUMS-disc.txt` + `data0-head-1mb.bin`).
- **ISO9660 root (parsed this session from range-fetched PVD, CD001 valid,
  root at LBA 261):**

| File | LBA | Bytes | Byte offset |
|------|-----|-------|-------------|
| SYSTEM.CNF | 276 | 57 | 0x8a000 |
| IOPRP300.IMG | 277 | 278,305 | 0x8a800 |
| SLUS_210.59 | 413 | 689,304 | 0xce800 |
| TK5DATA4.BIN | 750 | 179,368 | 0x177000 |
| TK5DATA5.BIN | 838 | 422,901,760 | 0x1a3000 |
| TK5DATA0.BIN | 207333 | 2,072,586,240 | 0x194f2800 |
| TK5DATA1.BIN | 1219338 | 1,297,731,584 | 0x94d85000 |
| TK5DATA3.BIN | 1852996 | 422,901,760 | 0xe2322000 |
| IRXARC.BIN | 2059491 | 305,024 | 0xfb671800 |
| TK5DATA2.BIN | 2059640 | 244,426,640 | 0xfb6bc000 |

- **Correction:** TK5DATA4.BIN is **not a data archive** — it is a MIPS ELF
  (IOP module, `7f 45 4c 46 … MIPS-III`). Only DATA0/1/2/3/5 are archives.

### 1.2 TK5DATA1.BIN — EXTRACTED (W7b, 2026-10-21; verified via their survey)

- File table in decompressed E5 frontend module @ `0x27B5B0`: **1,571 records**
  of (u32 sector_offset, u32 byte_size); checksums @ `0x27E838`.
- Cipher: **FileTableGetPS2** — per-file LCG keystream (`key = key·5+3`,
  seed = file index, 512 u32 per 2048-byte block); word-sum decides raw vs
  encrypted. **1,355 non-empty files, 0 checksum failures.**
- Contents: 464 NUDP model headers, 1,362 TIM2 texture headers, 80 costume
  packs (19-entry archives, files 0240–1109, whole-costume granularity),
  18 stage packs, animation/motion archives, IPU video.
- **On western-heart releases:** `tekken5-costume-glbs-v1` (80 GLBs),
  `tekken5-ctype5-glbs-v1` (8 GLBs). Catalog: `customization/parts/tekken5/`.
- Full survey: `customization/parts/tekken5/T5-CUSTOMIZATION-SURVEY-2026-10-21.md`
  (in the `fix/western-heart` working copy; not yet merged to main).

### 1.3 TK5DATA0.BIN — cipher layer 1 CRACKED this session (was: "unknown")

2,072,586,240 bytes. Header (16 B, LE, plaintext): `[0x1, 0x8, 0x442b, 0xda]`
= version 1, 17,451 entries. Entry table = 17,451 × 16 B = 279,216 bytes.

**Layer 1 (cracked 2026-10-22):** the entry-table region is XOR-encrypted with
the house LCG — `key = key·5+3`, **output-first, seed = 1**, 512 u32 keystream
restarted per 2048-byte block (same family as DATA1's FileTableGetPS2).
Proof: raw words 4–11 of the file are byte-exact LCG output
(`0x155c, 0x6acf, 0x2160e, 0xa6e49, 0x342770, 0x104c533, 0x517da02` =
5468 → 27343 → … chain); LCG-only decryption yields the structured start the
W7b survey predicted (`word2 = 0x4400`, `word4 = 0x035F6FF2`, zeros after).

**Layer 2 (characterized, not yet cracked):** after LCG removal, blocks 1+
show a **21-byte periodic residual** (autocorrelation: 1793/2048 byte matches
at lag 21, then 42/63/84 — confirmed period 21), key
`8d1861b8d1a346186e3468d1861b` with structured anomalies (counter-like bytes
at ~147-byte intervals). It is NOT a simple repeating XOR key (brute-forced
lengths 1–64: best case still entropy 6.7, no clean decrypt). Per-block seed
sweep (0–63) confirms seed 1 remains optimal — layer 2 is a second transform,
not a seed variant.

**Next step:** PCSX2 live-run fallback (documented in W7b §S6: dump decrypted
DATA0 from emulator RAM), or trace the second transform in Ghidra against
SLUS_210.59. Tooling from this session: `tk5_lcg.py`, `data0_crack.py`,
`data0_layer2.py` (kept in worker scratch; to be filed under
`teardown/tekken5/tools/` when the lane continues).

### 1.4 TK5DATA2.BIN — audio, PLAINTEXT (mapped this session)

244,426,640 bytes. Plaintext index at file start: `.dat` sound banks
(`snd_c02lei.dat`, `moj_stg02.dat`, `snd_bg_blu_se.dat`, `snd_c_monst.dat`, …)
plus label tables (`lab_A`, `lab_B`, `egy_A`, `blu_A`, `blu_B`, `szk`, …) with
per-sample parameter rows, e.g.
`lab_A,    1,  120000, 8000, 16000, -90,  1-1`.
77 label entries in the first 2 MB alone. **Next step:** full 244 MB pull
(range-fectchable from IA), parse all bank/label records, decode the PS2
ADPCM payloads.

### 1.5 TK5DATA3/5.BIN — sector-table format (partially mapped this session)

422,901,760 bytes each; **byte-identical 16-byte headers**
`[0xa, 0x800, 0x765c4, 0x77000]` (DATA5 = DATA3 size; headers match exactly —
likely duplicate/shadow archive). As 8-byte records the table reads as
(size, offset) pairs with increasing offsets
(`0x12e000, 0x7f3800, 0x8de800, …`) and zero-runs (122 empty 16-byte records
at byte 96). **Next step:** pull the full table region and resolve the record
schema; this archive likely holds stage/motion bulk data (and possibly Devil
Within assets).

### 1.6 T5 gaps remaining (honest list)

1. **DATA0 layer-2 cipher** (§1.3) — the single biggest T5 gap; 2 GB of
   character/stage/motion data behind it.
2. **DATA3/5 record schema** (§1.5).
3. **VIF 0x82 models** — 16 NUDP models in 9 ctype-5 containers (W7b §S4);
   ModelMagic desyncs on all 97 submeshes. Needs byte-budget VIF analysis.
4. **Movesets** — no T5 moveset binary format documented yet (expected in
   DATA0/DATA3 once open).
5. **Devil Within assets** — level layouts, enemy placements, boss triggers,
   Jin's DW moveset: unlocated (expected in DATA0/DATA3).
6. **T5 survey merge** — W7b's `customization/parts/tekken5/` (survey, catalog,
   proof renders) exists only in a working copy; needs its PR to main.

---

## 2. TEKKEN 6 — PS3 full archive secured; extraction blocked

### 2.1 PS3 archive — ACQUIRED (verified this session)

- Release `tekken6-ps3-full-v1` (**draft**): `TEKKEN.psarc` split into 10 parts
  (`part_aa`–`part_aj`, 9 × 524.3 MB + 112.9 MB) + `TEKKEN.psarc.manifest.txt`
  with expected reassembly sha256
  `c98fb02602d58564ef4e80d386310cb3c48634566990a5050ef20ef2a4afd340`.
  Reassemble: `cat TEKKEN.psarc.part_* > TEKKEN.psarc`, verify sha256.
- **Finding this session:** the first 8 MB of `part_aa` is uniformly
  high-entropy (7.997) with **no `PSAR` magic** — the stored psarc is
  encrypted/obfuscated as kept, or was repacked non-standard. Plain-psarc
  tooling will NOT open it directly; the decrypt lane must treat it like the
  PSP DATA401 problem (see §2.2). A lone `tekken6-ps3-500m.part_aa` asset
  exists but its download 404s (incomplete upload — disregarded).
- **Next step:** full 5 GB pull on a machine with disk headroom → identify the
  psarc transform (compare against the PSP sector-cipher family; T6 PS3 and
  PSP share the engine) → extract.

### 2.2 PSP — documented, bulk decrypt still blocked (no change)

Per `teardown/tekken6/TEARDOWN.md`: ISO (855,638,016 B) + 46 endings (337 MB)
on releases; EBOOT decrypted; **sector cipher 0x8AA2CA8 fully reversed**
(per-word `dst[i] ^= k; k = 5*rotr(k,29)+1`, unicorn-validated 768/768);
K1/K2 extraction solved. **Blocked:** DATA401 bulk region (sectors 230256+)
is uniformly random under an unknown transform — not the sector cipher, not
ktRead. The PS3 psarc (§2.1) is now the better route to T6 models/stages.

---

## 3. TEKKEN TAG TOURNAMENT 2 — archive secured; STFS extraction blocked on disk

- **Acquisition DONE:** release `ttt2-7z-v1` holds all **26 parts**
  (`ttt2-500m.part_01`–`part_26`, 25 × 0.52 GB + 0.26 GB = 13.36 GB) +
  `ttt2-loose-files.tar` (0.17 GB). Verified present via API 2026-10-22.
- **Inventory DONE** (2026-10-13, in-repo): `teardown/tekken-tag-tournament-2/`
  `TEARDOWN.md`, `INVENTORY.md` (80 entries w/ CRC32), `ROSTER.md` (59 fighters),
  `STAGES.md` (29 stages, 10 multi-tiered).
- **Blocked:** full extraction needs ~27 GB scratch (13.3 GB archive +
  13.45 GB extracted); this VM has <1 GB free. Inner content is Xbox 360 STFS
  (52 Data chunks + 7 title blobs); repo already has `tools/stfs_blobs.py`,
  `tools/xdvdfs_reader.py`, `tools/god_surgical.py`.
- **Exact procedure for a machine with disk** (no guessing):
  1. `gh release download ttt2-7z-v1 -R mhvnsnt/western-heart -p 'ttt2-500m.part_*'`
  2. `cat ttt2-500m.part_* > 'Tekken Tag Tournament 2.7z'`; verify size
     13,363,624,393 bytes.
  3. `7z x` (13.45 GB out) → 80 entries per INVENTORY.md.
  4. STFS: `tools/stfs_blobs.py` on `4E4D0859/00007000/…​.data/Data0000–Data0051`
     + the 7 `00000002/` blobs → inner Namco X360 formats (T6-console model
     family, XMA audio, per-character movelist binaries).
- **Lane coordination:** worker 46 (PR #668) owns the TTT2 team-battle *game*
  systems; this teardown feeds it assets, no overlap.

---

## 4. TEKKEN 7 — still blocked on acquisition (documented, last priority)

- 51 GB full game never acquired. T8 character-select grid decode and the
  King-focused T7 work continue independently.
- **Next step:** per `TEKKEN78-ACQUISITION-PLAN.md` (owner purchase step).
  No VM-disk path exists for 51 GB; acquisition must land directly to
  Release/external storage per the large-file rule.

---

## 5. What "complete" still requires (checklist)

| # | Item | Game | State |
|---|------|------|-------|
| 1 | DATA0 layer-2 cipher crack | T5 | 🟡 layer 1 done (§1.3) |
| 2 | DATA3/5 record schema | T5 | 🟡 partially mapped |
| 3 | Full audio bank decode | T5 | 🟡 index mapped, ADPCM pending |
| 4 | VIF 0x82 model decode (16 models) | T5 | 🔴 |
| 5 | Moveset binary format + extraction | T5 | 🔴 (behind #1/#2) |
| 6 | Devil Within asset extraction | T5 | 🔴 (behind #1/#2) |
| 7 | W7b survey/catalog PR to main | T5 | 🟡 written, unmerged |
| 8 | PS3 psarc transform + extraction | T6 | 🔴 (needs 5 GB disk) |
| 9 | PSP DATA401 bulk transform | T6 | 🔴 (superseded by #8) |
| 10 | 7z reassembly + STFS extraction | TTT2 | 🔴 (needs 27 GB disk) |
| 11 | Inner X360 model/moveset/audio parse | TTT2 | 🔴 (behind #10) |
| 12 | Full game acquisition | T7 | 🔴 (owner purchase step) |

**Bottom line:** nothing the owner was told is lost — T5/T6/TTT2 are all
*acquired* and safe on Releases. "100%" is now a decryption/extraction problem
(D
...[truncated 1066 chars]