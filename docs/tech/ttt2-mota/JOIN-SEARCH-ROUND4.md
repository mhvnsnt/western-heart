# TTT2 per-move → MOTA join — ROUND 4: THE JOIN IS FOUND (2026-11-04)

Rounds 1–3 concluded the join lives in no file container and is assigned
when the game builds the motbin in memory. That conclusion was half right:
the assignment logic is the game's, but **the motbins themselves were on
disk all along, inside `data006`**, and every move record inside them
carries its animation reference as a plain field. The earlier census
missed them because it searched for a `MOTA` magic census pattern — the
motbin container has no magic; it is located by its string cluster.

## 1. Where the motbins are

In the decoded `data006` (sha256
`fa486948e1fced19116a5304a9779f2b04bede2328a68913ebdb2b04bede2328a68913ebdb2`,
77,278,156 B) there are **66 motbin blocks**, one per character, identified
by the cluster:

```
[u32 fields] "[NAME]\0CREATOR\0 2012/06/23_0\0 Tue Jul 24 HH:MM:SS JST 2012\0"
```

Roster order in file: Paul, LAW, Lei_Wulong, RAVEN, FENG, ARMOR_KING,
EMILIE, Dragunov, KING, PANDA, EDDY, BOB_SATSUMA, ZAFINA, Miguel, Eleonor,
Lars, Alisa, Jinpachi, YOSHIMITSU, Ogre, **JUN_KAZAMA, Unknown**,
Kunimitsu, SlimBob, Forest, Miharu, ANGEL, Michelle, NINA, P-JACK, ALEX,
GreenOgre (True Ogre), VIOLET, Bosconovitch, Sebastian, TIGER, Combot,
Zako00–Zako07, HWOARANG, Lin_Xiaoyu, CHRISTIE, JIN, JULIA, Kuma, Bryan,
HEIHACHI, KAZUYA, LEE, Steve_Fox, MARDUK, Jack, **ROGER**, ANNA, Wang,
GANRYU, Asuka, BRUCE, BAEK_DOO_SAN, DEVIL_JIN.

Targets: `[JUN_KAZAMA]` name at file offset 24,097,580 (block base
24,097,056, creator MAX); `[ROGER]` at 69,032,589 (base 69,032,065,
creator YONE); `[Unknown]` at 25,422,284 (base 25,421,760).

## 2. Motbin header

Verified on Paul's block (base 256 in data006):

- String pointers at +0x8/+0xC/+0x10/+0x14 are relative to a string pool
  at base+0x20C ("[Paul]", creator, version, build date).
- 148 u16 "aliases" at +0x18 and 36 u16 at +0xF8 (aliases2 looks like
  hitbox/physics parameters, not animations — dead end, closed).
- A section table of (offset, count) big-endian pairs starts at +0x140,
  offsets relative to block base. Measured sections tile exactly at the
  Kiloutre struct sizes (movelist 0x70/record, voice 4/entry, throws
  8/entry, …). **The movelist is pair index 12, at +0x1A0.** (There are
  two more pairs than the 17-section README order suggests; indexing by
  the README order misparses — that was round 4's first false start.)
- An array of MOTA table pointers sits at header+0x1D8 (12 u32 slots,
  nonzero at even slots). These pointers do **not** land on `MOTA` magic
  in the file — they are load-image offsets: the tables are assembled
  into the image from data004/data005 at load. This is the "built in
  memory" behaviour rounds 1–3 inferred; the tables themselves are the
  on-disk MOTA tables censused in round 3.

## 3. Move records — the join field

Move records are 0x70 bytes. Two disk rotations exist:

| variant | name | anim_name | anim_ref | who |
|---|---|---|---|---|
| rotated | +0x4C | +0x50 | **+0x54** | Paul, Roger, most of the roster |
| unrotated | +0x00 | +0x04 | **+0x08** | Jun, Unknown (== Kiloutre's memory layout) |

Jun's records do not start at her section offset: her pair-12 section
begins with a 12-byte (flag, ref, param) triples stream, and clean Move
records sit on the grid `section_ptr + 0x5C + k·0x70` (motOrigin at grid
record 589). Unknown's records sit on `section_ptr + 0x2C` grid.
Jun and Unknown share a moveset core (Jun is the boss Unknown's base);
their bank-1 indices for the same anim differ slightly, so each
character's records must be taken from its own block.

Records 0–3 of each movelist are special/composites; real moves start at
record 4 = `motOrigin` → anim `Bco_newjump2(DVD)`.

**The join: `anim_ref = (bank << 14) | index`**, a pure bijective
function of anim_name within each character (Paul: 1,290 distinct anims
↔ refs; Roger: 1,262). Proof it is the animation reference and not a
coincidence field: it is the only u32 slot in the record that is a
function of anim_name, and its (bank, index) decomposition resolves —
with fingerprint validation — to real clips (§4, §5).

## 4. Bank semantics

The rule is the one the shipped T7 lane resolver already uses
(`0x4000` → per-character table, `0x8000` → common table, `0x0000` →
the motbin's own first MOTA block), confirmed on TTT2 data:

- **Bank 0 (0x0000)** = the character's own first trailing MOTA table
  inside data006. Paul has exactly 4 bank-0 anims (item anims, idx 0–3)
  and a 4-entry table at data006 file 0xD9C7C (entry 0 = null slot,
  entries 1–3 real clips). Roger's and Jun's bank-0 sets are also
  exactly idx 0–3.
- **Bank 1 (0x4000)** = one big MOTA table per character inside
  data005. Identified per character by **clip-fingerprint matching**:
  for anims two characters share in bank 1, the clip at each one's own
  index must have the same (type, track count, frame count, byte size).
  - Paul: table @ file 0x140, 549 entries (bank-1 max used idx 545).
  - **Roger: table @ file 0x56B6C04, 509 entries — 68/89 shared anims
    fingerprint-identical to Paul's table; next-best candidate 24/89.**
    (Roger's bank-1 max used idx 496.)
  - **Jun: table @ file 0xB81FCA4, 596 entries — 35/41 shared anims
    fingerprint-identical to Paul's table.**
- **Bank 2 (0x8000)** = the big table in data004 @ file 0x100, **1875
  entries**. Cross-character index agreement is exact: all 922 bank-2
  anims shared by Paul and Roger carry identical indices (every one of
  the 87 Paul↔Roger disagreements is bank-1, where each character has
  its own table). Max bank-2 index used by any cleanly parsed character
  is 1868–1873, inside the 1875-entry table.

Frame-count fingerprints used above were computed with the verified
formulae (0x64: frames = BE u16 at +(N·2+4), N = track count at +2;
0xC8: BE u32 at +4) — the same formulae the round-3/0x64 lanes validated
by full decode.

## 5. End-to-end decode proof (move → clip → frames)

Using only the join + the shipped decoders:

- Roger move `Rg_sKAM00_` → anim `kjrg_kamae02(DVD)` → bank 1 idx 48 →
  data005 table @0x56B6C04 entry 48 → `tools/ttt2_mota_decode64.py`
  decoded **270 frames, 23 tracks** (a stance loop).
  Proof file: `docs/proof/2026-11-04/ttt2-join/roger-stance-decoded.json`.
- Roger/Jun move `Fall_sKAM` → anim `naco_700dwn2(DVD)` → bank 2
  idx 343 → data004 table @0x100 entry 343 → decoded.
  Proof file: `docs/proof/2026-11-04/ttt2-join/common-fall-decoded.json`.

## 6. What is delivered with this round

- `docs/tech/ttt2-mota/join/roger-join.json` — Roger's full movelist:
  2,180 records with (move name, anim name, bank, index). Complete and
  clean (17 of 2,197 header records fail the string/ref validity check).
- `docs/tech/ttt2-mota/join/jun-join.json` — Jun's movelist from her own
  block: 749 records (system core + her character records incl. her
  bank-1 throws/getups/runs and ju-specific clips).
- `docs/tech/ttt2-mota/join/unknown-join.json` — the Unknown boss block
  (1,484 records) for reference: it carries the shared Jun/Unknown core
  with Unknown's own bank-1 indices; its bank-2 indices are Jun's.
- `docs/tech/ttt2-mota/join/bank-tables.json` — the bank resolution map
  with the evidence for each bank.

## 7. Remaining work to banks (recipe, no guessing left)

1. Slot mapping: parse each motbin's cancel section (0x20-byte records,
   Kiloutre layout) and input sections exactly as the T7 lane's
   `t7_move_resolve.py` did — stance move's cancel graph yields the
   string starters, frame data comes from the move records — and map
   jun.json (101) / rog.json (84) display moves onto the 20 FIGHT slots
   of the PR #1550 bank shape.
2. Decode each slotted clip from its resolved table (bank 0: data006
   trailing table; bank 1: the data005 offsets above; bank 2: data004
   @0x100) with `tools/ttt2_mota_decode64.py` / the 0xC8 decoder.
   Note the known ~10% 0x64 encoder-variant families: report, never
   mangle; pick the clean sibling clip where a slot's clip is affected,
   and log it.
3. Retarget/bake via the proven Blender + TekkenAnimHelper route into
   `game/assets/anim/t3/roger/` and `game/assets/anim/t3/jun/`
   (wh-anim/1: `t3_<action>.json` + `rows.pack.json` + `skeleton.json`).
4. Wire `fighter.js` FIGHTER_BANK: menajerii `kuma` → `roger`, add
   megami → `jun`. Chatur unchanged (True Ogre has no TTT2 moveset
   file — only Ancient Ogre — documented gap, unchanged).
5. Identity-gated probes (menajerii + megami) and short fight videos to
   `~/workspace/your_files/smutbase-ttt2-proof/`.

## 8. Route 1 (xex) notes

The Ghidra trace was run in support of the data-side result: the
sampler's callers (8228C448, 8228D418, 8238A968, 8238AC48) are runtime
sampling, not builders; Function_82348348 is a by-key move lookup over
0x70-byte records (consistent with the on-disk record size); the
load-time relocator that patches the header's MOTA pointer array
(+0x1D8) was not isolated — it is not needed: the table identities are
proven by measurement on the game's own data (§4), which is stronger
than a decompile reading. RPCS3 live-memory (Route 2) is therefore also
not needed.
