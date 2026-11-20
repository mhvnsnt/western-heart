# WMXIX .MPC MOVE-ASSIGNMENT DECODE — 2026-10-21 (gap-closure W4b)

Follow-up to `WMXIX-MOVE-NAME-SURVEY-2026-10-21.md` (W4, PR #439).
Question: how does WMXIX map a wrestler's named special (the `//menu/menu.mpq`
profile slot, e.g. The Rock's **Rock Bottom** [Front Grapple]) to a gameplay
animation clip inside `//motion/*.mpc`, and which clips are Rock Bottom,
People's Elbow and People's Spine Buster?

## VERDICT — container decoded; wrestler assignment NOT located; no clips claimed

- **The .mpc container is FULLY decoded** (format spec below, proven
  self-consistent): every gameplay motion in `move.mpc` is now addressable —
  **870 motion IDs → 1,905 YANM clips**, each with exact file offset and size.
  Machine-readable index: `teardown/wmxix/WMXIX-MPC-INDEX.json` (this PR).
  Given a motion ID, its clip(s) can be extracted today with the existing
  range reader + YANM decoder.
- **The wrestler → motion-ID assignment table was NOT found** in any data
  surface searched (list below). It is not in the .mpc trees, not in
  `com_dt.mpc`, not in `static.mpc`'s leaves, not in the menu.mpq profile
  blocks, and not an obvious table in the DOL. **Rock Bottom / People's
  Elbow / People's Spine Buster clips are therefore NOT identified, and no
  clip is claimed for them.** `moveset-library/movesets/rock-moves-wmxix.json`
  is unchanged by this lane, per instructions.
- The survey's candidate assignment files are resolved: `motion/sheet/91xx.yad`
  and `motion/win/91xx_00A.tmp` belong to the **win-motion system only**
  (details below) — they do not assign gameplay specials.

## The .mpc (POF tree) container format — decoded and proven

All `*.mpc` packages share one container (the "POF" family the DOL loader
relocates, cf. `YOBJ-DOL-DECODER-REPORT.md`). Layout, big-endian:

- **Header (0x20 B):** `[0x00] u32 index_end` · `[0x04] u32 data_size` ·
  `[0x08] u32 0x20 (header size)` · `[0x0C] u32 data_start`.
  For `move.mpc`: index_end `0x8220`, data_size `0x7C5BC0`,
  data_start `0x8240`, file size 8,183,296 B (ISO offset `0x105925CC`).
- **Index:** a flat array of **12-byte records** starting at `0x20`:
  - record 0 = root directory (`child_count` = number of motion nodes,
    name `root`/`froot`).
  - **Directory / motion node:** `[u32 child_count][char[4] name]
    [u32 first_leaf_record_index]`. `first_leaf_record_index` chains
    perfectly: each node's value = previous node's value + previous node's
    child_count (**zero breaks across all 870 nodes**).
  - **Leaf (one YANM clip):** `[u16 marker][u16 size_units]
    [char[4] sub_name][u32 data_offset]`. `marker` is `0xFF00` normally,
    `0x0100` for 2 leaves in move.mpc (large clips; semantics of the
    distinction not yet known). `size_bytes = size_units × 32`.
    `data_offset` is relative to `data_start`. Sub-names: `00A`, `00B`,
    `01A`, `01B`, `02A`, `02B`, `00C`, `03A`, `03B` — the A/B pairs read as
    the two synchronized sides of a move (attacker/victim), numbered
    groups as phases/variants. Most motions have kids `00A` (309) or
    `00A,00B` (345); turnbuckle/whip-class IDs (41xx/43xx) have 6.
- **Proof of exactness:** parsing `move.mpc`'s index yields 1 root + 870
  nodes + **1,905 leaves**, and the clip references sum to exactly 1,905;
  the last leaf ends at `data_offset + size = 0x7C5BC0` = the header's
  data_size field, to the byte. The survey's raw "1,905 YANM markers"
  count is therefore 1,905 real clips, not marker noise.
- **Extraction proof:** leaf `0101 / 00A` (data_offset 0, 2,560 B) was cut
  from the range-read head of move.mpc: magic `YANM`, payload `0x928`,
  29-track directory parses with the repo's YANM layout
  (`teardown/wmxix/extract_yanm.py`). The same quick parse of
  `ringmotion/a002_0a.yag` reproduces W4's 33.856 s exactly, validating
  the method; `.mpc` clips' `sec_per_tick` field (0.159 for 0101) differs
  from the ringmotion set's (0.041), so per-clip durations for .mpc clips
  are **not yet calibrated** and none are claimed here.

## Package census (same container, all trees parsed)

| Package | ISO offset | Size | Node namespace | Nodes | Leaves |
|---|---|---|---|---|---|
| `//motion/move.mpc` | 0x105925CC | 8,183,296 | numeric IDs `0101`–`9008` | 870 | 1,905 |
| `//motion/common.mpc` | 0x0FB6CF8C | 4,396,640 | letter codes `A000`, `A100`… | 818 | 1,584 |
| `//motion/common_1.mpc` | 0x0FF9E5EC | 1,913,088 | letter codes `A…` | 381 | 784 |
| `//motion/common_2.mpc` | 0x101716EC | 1,246,208 | letter codes `F…` | 180 | 372 |
| `//motion/common_3.mpc` | 0x102A1AEC | 1,259,680 | letter codes `J…` | 265 | 430 |
| `//motion/MENU.mpc` | 0x103D538C | 1,818,208 | letter codes `A…` | 330 | 751 |
| `//motion/nyujo_ch.mpc` | 0x10D603CC | 2,128,224 | `A000`–`A0xx` entrances (A002 = ROCK ✓) | 178 | 327 |
| `//motion/mini.mpc` | 0x105911EC | 5,088 | not a POF package (raw data) | — | — |
| `//com_dt.mpc` | 0x05A7D670 | 754,176 | data tree (below) | — | 117 |
| `//static.mpc` | 0x1212DF80 | 1,018,496 | data tree (below) | — | ~70 |

The letter-coded packages use the `EMotName`/`cmot` code namespace;
`move.mpc`'s numeric IDs are the gameplay-move namespace. The two
namespaces coexist; no cross-map between them was found in data.

## Candidate assignment files — resolved

- **`motion/win/91xx_00A.tmp` (64 files):** each is a standalone YANM clip
  byte-identical in format to a `ringmotion/*.yag` (same header, same
  first track hash `CD89A39E`, own `POF0`/`DATA` tail). These are the
  **win (victory) motions**, numbered 8109, 9100–9159, 9200, 9201.
- **`motion/sheet/91xx.yad` (41 files, 9101–9141):** header
  `[u32 1][u32 1][name-len]["9101_0A.tmp"]` followed by 28-byte keyframe
  records (id + f32 time pairs + flag words) — a **camera/effect sheet
  for the matching win motion**, referenced by filename. No move
  assignment data.
- **`//Entrance/Defwres*.dat`** remains entrance-only (W4).

## `com_dt.mpc` and `static.mpc` inventories (searched for the table)

- `com_dt.mpc` tree: `root/com/{cmn, tbl, bg}`. `cmn` leaves: `cmn0`,
  `cmn1` (common params; embed the path string `.\com\bg\`), `comb`,
  `cnt0`–`cnt3` (counters), `rule` (match rules), `char` (64 character
  attribute records, sequential IDs, `0xFF`-padded fields), **`cmot`**
  (5,312 B: 24-byte records `[u32][u32][letter-code][u32][u32][u32]`
  listing codes `A100…U112` — a **motion-category catalog** for the
  letter-coded packages, not a per-wrestler assignment). `tbl` = 61
  parameter tables (`pl0/pl1`, `sl0`–`sl29`, `al0`–`al21`, `mb0`–`mb6`);
  `bg` = 41 stage tables (`r00…`, `cs`, `fa`, `ha`, `pa`, `sm`).
  `pl0` is percentage-style player parameters (values of 100/200/300…).
  None contains motion-ID runs in any encoding tried.
- `static.mpc` leaves include the boot tables named in the DOL string
  table (`sys/anim`, `sys/wprm`, `sys/sprm`, `sys/mstb`, `sys/mcmsg` are
  paths inside this package): **`wprm`** (94,496 B, wrestler parameters),
  **`mstb`** (25,472 B; content is Revenge-mode stage data — it contains
  the strings `HARBOR 1`, `HARBOR 2`), **`anim`** (59,040 B; CAW face/part
  name lists), **`edit`** (112,448 B; CAW edit data — contains the motion
  catalog described next), **`wset`** (56,416 B; 3ds-Max-style `Bip …`
  bone-name tables), `sprm`, `bs_win_tbl` (boss roster name records:
  Default / The Rock / Triple H / Hulk Hogan / Undertaker / Kurt Angle…,
  ~128 B per record with binary fields), `mst2`, `wanm`, `vwps`, `boss`,
  `mdl`, plus UI/texture leaves.
- **Embedded motion catalog (in the `edit` leaf's region of static.mpc,**
  data-relative ≈ `0x8A280`): records of 28 B × k per motion ID covering
  **816 of move.mpc's 870 IDs in ID order** (`0101`…`9008`): each record =
  `[u32 cumulative_offset][char[4] motion_ID][u32 0][16 B parameter
  tail]` with 1–6 records per ID. This is a **per-motion parameter
  catalog** (the moveset-editor's move list), still keyed by motion
  alone — it does not say which wrestler owns which move.

## Searches that came up empty (assignment table)

- FST listing (4,222 files): no moveset/wrestler-parameter file outside
  the surfaces above; `//model/wrestler/` is models/textures only.
- `menu.mpq` profile blocks (Rock at `0x5B52B`–`0x5B773`): a string pool
  with u32 offset tables — presentation text only (name, height, weight,
  titles, the three special names). No binary moveset fields.
- DOL (`main.dol`, 3,422,208 B, pulled whole): u16 and u32 sliding-window
  scans for density in the valid 870-ID set found only a trig table and a
  sequential index; ASCII scans found no 4-char-ID tables (516 isolated
  valid-ID quads = binary noise, e.g. `2222` runs). The DOL boot string
  table confirms `motion/move.mpc`, `static.mpc`, `com_dt.mpc` are loaded
  at boot. A moveset table could still exist in the DOL in an interleaved
  record format the density scans cannot see — that is a code-analysis
  question, not a data scan.
- `menu.mpq` / `//menupause` MPQ internals: both are real `MPQ\0`
  archives (145 / 98 block-table entries respectively). Only menu.mpq's
  profile string file was read (by W4); their remaining internal files
  were **not** decoded in this lane.

## Where it stalls, and what would crack it

The decoded path is: *named special (menu.mpq slot)* → **[missing:
wrestler moveset table]** → *motion ID* → *(this doc's index)* → *YANM
clip(s) in move.mpc*. The missing link is a single table. Ranked routes:

1. **Ghidra trace of the consumer (most direct):** the DOL code that
   plays a grapple must convert (wrestler, slot) → motion ID and call
   the POF node lookup on the already-decoded tree. XREF the
   `motion/move.mpc` string (DOL file offset `0x2D92A0`, in the boot
   file list beside `static.mpc`/`com_dt.mpc`) and the POF lookup
   function; the moveset table will appear as a data reference beside
   the slot-indexed load. Ghidra 12.1.4 is installed
   (`~/workspace/tools/ghidra/`); the prior DOL RE
   (`YOBJ-DOL-DECODER-REPORT.md`) already mapped the POF loader at
   `0x8007A71C`/`0x8007AACC`.
2. **MPQ internals:** decode the block tables of `menu.mpq` and
   `//menupause` and inventory their internal files; a wrestler-data
   file, if present, resolves the table without code analysis.
3. **Runtime observation:** Dolphin + the in-game moveset viewer
   (the `//viewer/motion/` 85xx set proves a viewer exists) while
   watching which move.mpc node loads for Rock's Front Grapple.

## Secondary deliverable (this PR)

`moveset-library/movesets/WMXIX-MOVES.json` annotated (additions only,
no entries deleted or renamed): `_meta.provenance_correction_2026_10_21`
plus a per-move `provenance_correction` note and `emotname_label` on the
111 entries the W4 survey name-mapped — the file's 169 "Mat Legends
Grapple" entries are the ringmotion **entrance/taunt/win** set, not
gameplay grapples.

## Method / provenance

Range reads only, via the repo's existing reader pattern
(`teardown/wwe-wrestlemania-xix/tools/wmxix_range_iso.py`; W4's
`fetch.py`/`iso.py` working copies) against release `wmxix-iso-v1`
(current `part_00`+`part_aa`+`part_ab` layout). Files pulled: move.mpc
head (128 KB) + full index region, heads of common/common_1/2/3, MENU,
nyujo_ch (100 KB each), full `com_dt.mpc` (754,176 B), full `static.mpc`
(1,018,496 B), `main.dol` (3,422,208 B), menu.mpq profile region (64 KB),
the contiguous sheet+win region (582,800 B), `a002_0a.yag`. Scratch
stayed under ~8 MB on a ~93%-full disk and is cleared by this lane.
Decoders used/extended: the repo YANM layout
(`teardown/wmxix/extract_yanm.py`) and the POF tree walk proven across
all ten packages above. No guessed clip assignments were made.
