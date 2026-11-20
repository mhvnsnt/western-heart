# Urban Reign Phase 4 — Job 2: name bridge (CRACKED for P1, 27/35 proven)

Phase 3's named next step: match P1 `.bin` record shapes against
pmot001's 56-motion bank. Result: the shape match **locked**, and a
stronger data-level proof fell out of it.

## The .bin record format — fully cracked (extends phase 3)

Record k of a motdat `.bin` (offsets from the record start):

| Offset | Field |
|---|---|
| +0 | u32 **global motion ID** (monotonic across the list; P1: 45, 92–95, 154, 187, 290, 383, 384, 484–486, … 819–821) |
| +4 | 32 B name — **byte-identical to `.info` name k on all 35 P1 records** |
| +36 | 20 B date (same layout as `.info`) |
| +56 | u32 **frame count** of the motion |
| +64 | u32 payload-related size field (not a bank size; see below) |
| +68 | u32 = frames × 132 (= frames × 33 f32, the sampled-data size) |
| +72 | u32 M = segment count |
| +76 | u32 0 |
| +80 | (M−1) × u32 segment offsets |
| +80+4(M−1) | **payload: per-frame sampled motion data**, starting with frames × 3 f32 = the motion's **root track sampled per frame, ×1000** |

## The proof

For each P1 record, the payload root stream was compared against the
decoded root track (phase-2 `ur_gyu.py` decoder; per-frame sampling,
linear between keys) of every motion in pmot001 (56) and the three
general banks (342 + 373 + 114):

- **27 of 35 records match exactly one pmot001 motion** over all
  frames, max deviation ≤ 0.06 mm on values of order 1000 mm — i.e.
  float-rounding identity, not similarity. Full pairs with per-pair
  max-deviation: `name-bridge-p1-proven.json` (same folder). These
  27 name↔motion pairs are **assigned** (char001's moveset record —
  see the phase-4 state file for where they landed).
- Frame counts alone already aligned 34/35, with the proven pairs in
  increasing pmot slot order (0, 4, 5, 6, 7, 10, 22, 23, 28, 30–43,
  47, 48, 49) — the P1 list is a subset of pmot001 plus outliers below.
- 3 proven pairs (records 1–3) also exist as root-identical copies in
  the general_normal bank (slots 62, 64, 58) — the general pool
  literally duplicates some pmot motions. Their `globalId` values
  (92, 93, 94) are **not** the `general_index` values of those slots
  (131, 133, 123): the `.bin` ID is a third, master enumeration (the
  `gyu_test.lst` space), not the bank index space.

## The 8 unproven records (no pair assigned)

Listed with candidates and deviations in `name-bridge-p1-proven.json`.
Two distinct causes, both named:

1. **Type-14 root decode gap (records 6, 10, 11, 12, and likely 7,
   13, 29):** their frame-unique pmot candidates carry type-14 root
   tracks, and the current `ur_gyu.py` type-14 decode in the pmot
   context yields off-scale root values (e.g. candidate m025 decoded
   root y ≈ 1590 mm with multi-metre deviation vs payload y ≈
   1110 mm standing). The payloads are sane (standing/airborne root
   heights); the decoder's type-14 pmot path is the suspect. Next
   discriminating test: re-derive the type-14 float-pair combine
   from the sampler (`FUN_00292670`) for the pmot flag combination
   (pmot bone-20 flag = 0) and re-run these 7 records.
2. **Record 14** (`moco_doubleairk_f`, 88 frames, globalId 502):
   no 88-frame motion exists in pmot001 at all — its source is
   another bank. Next test: run the same root-stream match for this
   record against the test30/wptest P1 variants' banks once the
   type-14 path is fixed (its `_f` siblings pattern-match the
   doubleairk set: records 15/16 proven to pmot001 m028/m029).

## Generalisation

The record format + root-stream test generalise mechanically to
every held motdat pair (P42 `.info` is held; its `.bin` is in the
AFS — one range-fetch) and to the other pmot fighters' lists
(P2–P63 `.bin` files are all in the AFS). Each fighter's proven
subset can be assigned the same way, per-fighter, with the same
≤0.06 mm identity gate. The Gnrl lists (294/257/44 records) can
likewise be matched against the general banks to name general-pool
motions — that is the naming half of the Job-1 runtime question,
and it needs no new format work, only the type-14 fix for full
coverage.
