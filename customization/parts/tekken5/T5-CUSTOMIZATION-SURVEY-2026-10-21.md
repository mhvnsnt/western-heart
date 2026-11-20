# TEKKEN 5 CUSTOMIZATION SURVEY — by content, from the disc data

Gap-closure W7b, 2026-10-21. Owner order 2026-10-21 ~09:39 CDT: *"we should
have five, and six and Tekken Tag Tournament two — they all had customization
and customization parts"* — T5/T6/TTT2 teardown holdings become the active
parts program; T7 later. This doc is the T5 slice. Every number below is
from bytes parsed this run; render verdicts are from frames viewed by the
lane itself (`proof/` in this directory).

Coordination: the sweep's T5 finisher lane owns the T5 teardown
(checkpoint `tekken5-teardown.json`); this lane took the customization
slice only and reused its tooling and findings (Lane B cipher hunt, Lane D
E5/E6 parse, Lane G research pull-ins) instead of re-tearing anything down.

## S1. Source acquisition (store-first, chunk-wise)

- Disc data: GitHub release `tekken5-disc-v1` (mhvnsnt/game-reverse-engineering)
  — TK5DATA1.BIN in 3 parts (500,000,000 + 500,000,000 + 297,731,584 B).
- All 3 parts pulled and **sha256-verified against `SHA256SUMS-disc.txt`**
  from the same release. Part 01 initially arrived truncated
  (461,373,440 B); the missing 38,626,560-byte tail was fetched by HTTP
  Range and the completed part then hashed **exact** to the manifest
  (`5c1afba6…`). Assembly: 1,297,731,584 B exactly.
- Assembly + parts were cleared after extraction (log:
  `agent-ops/disk-cleanup-log.md`); the release remains the byte-exact
  store. Pull-back: `gh release download tekken5-disc-v1 -R
  mhvnsnt/game-reverse-engineering -p 'TK5DATA1*'`.

## S2. DATA1 extraction — the table, the cipher, the proof

TK5DATA1.BIN is not a filesystem; its index lives in the decompressed E5
frontend module (Lane B, `TK5-DATA0-CIPHER-HUNT.md`):

- File table @ E5 file `0x27B5B0`: **1,571 records** of
  (u32 sector_offset, u32 byte_size), 2048-byte sectors.
- Checksums @ E5 file `0x27E838`: 1,571 u32 word-sums.
- Per file: if the stored bytes' word-sum matches, the file is raw; else
  XOR-decrypt with the LCG keystream (key = key·5+3, **seed = file index**,
  512 u32 keystream repeated per 2048-byte block — the FileTableGetPS2
  method, whose constants Lane G cross-verified 1571/1571 against E5) and
  re-check the word-sum.

**Result: 1,355 non-empty files extracted, every one checksum-verified;
0 failures; 216 records are empty slots (size `0xFFFFFFFF`).** No
decryption is claimed on faith — the E5 checksum is the proof per file.

Tooling: in-repo `tk5_decompress.py` family + the community Tekken5_Tools
constants (© its author, NO LICENSE — used for evaluation/extraction only,
NOT vendored; Lane G precedent, research log 2026-10-20).

## S3. What DATA1 contains (census)

675 files parse as (count, offset, size) archives. By entry count:
19-entry ×80, 21-entry ×18, 6-entry ×260, and smaller families. Full
content scan of all 1,355 files: **464 NUDP model headers, 1,362 TIM2
texture headers.**

### S3.1 The 80 costume packs (19-entry archives, DATA1 files 0240–1109)

Fixed schema in every pack (own parse, all 80):

| sub | content | size range |
|----|---------|-----------|
| 0 | 16-byte record (`02 12 04 …`) | 16 |
| 1 | TIM2 texture set | 192 – 643,072 |
| 2 | **NUDP costume model** | 117,776 – 788,480 (36–116 mesh groups) |
| 3 | data (`32 00 xx 00` head) | 3,152 – 4,816 |
| 4 | MIF | 352 – 47,648 |
| 5 | **NUDP low-poly full body** | 28,288 – 74,848 (1 mesh group) |
| 6 | data | 624 – 3,152 |
| 7 | MIF | 288 – 1,616 |
| 8 | `TK5 ` record | 48 |
| 9–11 | empty in 78 packs (see S3.3) | 0 |
| 12 | data (mirrors sub 3) | 3,152 – 4,816 |
| 13 | MOP | 16 – 20,560 |
| 14–18 | data / animation-family blocks | — |

Packs sit in 11-file character groups (pack + COM files + three 6-entry
animation archives + companions); consecutive groups sometimes share
byte-identical companions (same character, next costume). **80 packs ≈
the roster's full costume set** (≈33 fighters × 2–3 costumes, incl.
specials).

### S3.2 Own-eyes render verdicts (the decisive step)

Models were converted with ModelMagic (`nudp2obj`, VIF streams with
globalFlags 0x91/0x93) and rendered as shaded orthographic projections
(`proof/`):

- **sub02 = the character's full costume model** — body, head, hair,
  clothing and props as ONE NUDP. Sampled packs read clearly: gi +
  topknot fighter (0240), military uniform + sword (0295), cowboy hat +
  chaps (0405), mascot/bear suit (0460), angel wings + halo (0515), sumo
  (0570), tin robot (0735), kangaroo (0790), conical hat + spears (1010),
  and more (`proof/contact-sheet-16-packs.png`).
- **sub05 = a low-poly full body in T-pose** with the same silhouette as
  its pack's costume (737 verts vs 11,940 for pack 0240) — an LOD /
  low-detail body, **not an item** (`proof/pack0240-sub05-lowpoly-body.png`).
  An early hypothesis (this lane's and the coordinator's) that sub05 is a
  per-character item is **killed by the render**.
- The only third NUDP in any pack (packs 0779/0790, sub09, 432 B) is a
  **single triangle** (3 verts, 1 face) — a placeholder/degenerate entry,
  not an item.

**Conclusion: the DATA1 character packs contain NO per-slot item meshes.**
T5's customization data reality in this build is whole-costume granularity
(+ palette/texture data). This matches the teardown lane D finding that
E5/E6 hold customize *screens* but no item catalog (no names, prices, or
per-character item lists in the frontend module).

### S3.3 The empty slots

216 of the 1,571 DATA1 table records are empty — including slots +7/+8 in
most character groups (in ~9 groups those slots DO hold ctype-5
containers in DATA1, S4). The content for the empty slots is not in
DATA1; the only other character-data archive on the disc is
TK5DATA0.BIN (S6).

### S3.4 Everything else in DATA1 (for the record)

- 18 stage packs (21-entry archives, files 1113–1181 region): TIM2 +
  dozens of small NUDP stage props each (464-NUDP census remainder).
- Files 1243–1373: small (count,off,size) archives, no NUDP/TIM2
  (animation/motion family). Files 1374–1534: tiny `TK5R` records.
  Files 1535–1538: TIM2 texture packs. Files 1539–1555: IPU-family video.
- Files 0083–0114+: 869,472-byte texture archives (TIM2 ×4, 2-entry) —
  per-character texture sets.
- Files 0001–0004 (61 MB / 61 MB / 212 MB / 212 MB): no NUDP/TIM2 at any
  offset — bulk data (motion/stage family), unclassified beyond that.

## S4. The ctype-5 containers — the last DATA1 hiding place

9 files share a distinct container schema: `[count=5][TIM2 set][NUDP
set][MIF][small][data]`, with each sub carrying an 80-byte inner header
before its payload:

| file | role | NUDP models inside |
|------|------|--------------------|
| 0022 | system region | 4 (5,248 / 10,368 / 18,272 / 19,264 B) |
| 0687, 0698 | character-group twins | 1 each (7,472 B, 17 groups) |
| 0753, 0764 | character-group twins | 1 each (1,520 B, 1 group) |
| 1061, 1072, 1083, 1094 | character-group set | 2 each (13,520 B/1 grp + 8,336 B/19 grp) |

**All 16 models use VIF globalFlags `0x82`.** Every working pack model
uses `0x91`/`0x93`. ModelMagic's VIFerator assumes the 0x91/0x93 section
layout and desyncs on **every** 0x82 stream (0 of 97 submeshes converted
across the set) — so these models' geometry is **not characterized in
this survey at all**: no shape claim is made from header metadata alone.
(A characterization of the 1061 pair circulating in coordinator traffic
traces to a different game's file in the sibling W7a lane; it is not T5
evidence and is not repeated here as fact.)

Unblock route: solve the 0x82 vertex layout by byte-budget per submesh
(vertCount is in the VIF header; section sizes are the unknowns) or trace
the render path in Ghidra. If these decode to item geometry, they become
the first real `parts[]` entries.

## S5. Skull-mask survey (by content; verdict)

Target: a skull/mask-type **generic** head item, to be registered under a
tekken5 id only if actually found (the tekken7 named gap stays untouched).

Method: full NUDP census (S3) + own-eyes renders of every model class
that converts with held tooling + header census of the classes that
don't. **Verdict: NOT FOUND in DATA1.** No skull, mask, or standalone
head-covering geometry exists among the 448 convertible/stage NUDPs; the
16 unconverted 0x82 models (S4) and DATA0 (S6) are the only places it
could still hide. Registered in CATALOG.json as
`tekken5:cmn:full_head:skull-mask` with status
`named_gap_not_found_in_surveyed_data`.

## S6. TK5DATA0.BIN — new cipher evidence (for the teardown lane)

DATA0 (2,072,586,240 B) stayed "entropy 8.00, transform unknown" after
the cipher hunt. This lane pulled only its first 2 MB (Range request on
release `tekken5-disc-v1` part 00) and found, **in the raw bytes**:

- Words 5–11 are an exact LCG chain (key·5+3): 5468 → 27343 → 136718 →
  683593 → 3417968 → 17089843 → 85449218. Running the LCG backward gives
  **seed 1 at word 0** — i.e., the head region is XOR-encrypted with the
  same LCG family as DATA1, seed 1, over plaintext that is zero there.
- Block-restart (per-2048) seed-1 decryption of the head yields a
  structured start (zeros; word2 = `0x4400`; word4 = `0x035F6FF2`) but
  blocks 1–2 then show a **second periodic byte pattern** (period ≈ 13–28
  B) — a second layer (second stream, per-block seed advance, or a
  compression stage) that the DATA1 scheme alone does not explain.
- No NUDP/TIM2 magic appears in the first 2 MB under raw, continuous, or
  block-restart seed-1 decryption.

So DATA0 is *closer* than "unknown": layer 1 is the house LCG with seed 1.
Full crack = teardown-lane work (cipher-hunt §8 PCSX2 route remains the
documented fallback). Until then the T5 item census is honestly stated
as: **no slot-item meshes in DATA1; DATA0 unexamined below layer 1.**

## S7. Slot-schema divergence (why by_slot is T7-shaped but zero)

T5 (2004) introduced character customization, but its data predates the
T6 4-slot and T7 16-slot systems used as registry references
(`customization/parts/tekken/tekken6-slot-catalog.json`,
`tekken7-slot-catalog.json`). In T5's data, customization = whole-costume
models + texture/palette variation, with any item layer confined to the
S4/S6 gaps. CATALOG.json therefore maps at `FULL_BODY` granularity in its
entry template and named gaps, keeps the shared T7 slot keys at zero, and
records this divergence in `_meta.slot_divergences` rather than forcing
T5 content into slots it never had.

## S8. Count reconciliation (coordinator directive)

The owner's other session ran a read-only `tekken-customization-inventory`
scout over the T5DR/T6/TTT2 teardown folders. **Re-checked twice this
lane (local disk + GitHub code search across mhvnsnt repos): its output
had NOT landed as of this catalog's finalization** (that session was
limit-paused, auto-resuming 13:01 CDT 2026-10-21). Counts here are this
lane's own byte-verified census (S2/S3); if the scout's numbers land
later and differ, they are to be reconciled against S2's checksum proof,
not silently overwritten.

## S9. What lands next (conversion pass, not this PR)

1. Pack→character attribution from data (per-character isolation law):
   confirm each pack's fighter from game-side tables before any
   `char_id` is set; visual IDs from the contact sheet are survey
   evidence only.
2. Convert sub02 (+sub01 TIM2→PNG, materials bound) → GLB per pack;
   append to CATALOG.json `parts[]` as `FULL_BODY` entries in the
   templated shape; flip the costume-models named gap.
3. Decode VIF 0x82 (S4) and the DATA0 second layer (S6) — teardown-lane
   format work; each unlock appends its own entries.

*W7b lane, 2026-10-21. Proof frames in `customization/parts/tekken5/proof/`.*
