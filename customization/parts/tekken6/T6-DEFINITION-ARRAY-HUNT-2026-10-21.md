# Tekken 6 PSP — `sbcustomize_item_t` Definition-Array Hunt (W7c, 2026-10-21)

Gap `T6-ITEM-DEFINITIONS` (named in `customization/parts/tekken/TEKKEN6-ITEM-TABLE-SEARCH-2026-10-20.md`
§4): the definition array that would join the 9,440 held item-name records
(`customization/parts/tekken/tekken6-item-names.json`) to slot/category, price,
character eligibility, and model-pack/container per item.

## Verdict

**The definition array is NOT located in any plaintext data held — and the
EBOOT proves why: there is no static definition array in the EBOOT to find.**
`sbcustomize_item_t` records are loaded at runtime from DATA401 container
files into a heap vector. The containers that carry them sit in the same
DEFLATE-blocked population as the item meshes, so the name→definition join
stays gated on the teardown sweep's encode-context crack (owned by the sweep;
not duplicated here). Everything this hunt *could* prove is proven and shipped
in `item-definitions.json` beside this doc; every record's slot / character
scope / container stays **`unproven`** — no field in any located data assigns
them, and none is guessed.

## What is proven

1. **Name records, re-validated first-hand, 9,440 / 9,440 exact.** Against
   `bulk_decrypted.bin` (384,073,728 B, SHA-256 computed this lane
   `802417902fad787fdbafc5aa19d227d958a8435b0623e340bb9b7ab0bbc408f2`;
   extracted from release `tekken6-recon-20261016`'s `t6-recon-backup.tar`,
   member `tekken6/work/decrypt3/bulk_decrypted.bin`): every record in
   `tekken6-item-names.json` matches byte-for-byte — `u32 rec_size` at
   `bulk_offset`, `u8 item_idx` at +4, ASCII name at +5, null-only padding.
   0 mismatches.
2. **Arbiters verified.** "Skull Mask" at bulk offset 124705559 parses as
   rec_size 32, item_idx 36; at 129124535 as rec_size 32, item_idx 99.
3. **Table (run) membership is a proven join.** Chaining records by
   `next_offset = offset + rec_size` groups all 9,440 records into **768
   contiguous runs** (per-language / per-category tables). The idx-36 Skull
   Mask sits in run 583 (16 records, bulk start 124705271); the idx-99 Skull
   Mask in run 613 (30 records, bulk start 129124375). Run membership +
   position is shipped per record in `item-definitions.json`. (W7a's survey,
   PR #453, reads run 583's neighborhood as a head-category cluster and run
   613's as one character's full item table — that reading is W7a's
   interpretation of neighboring names; this lane ships the membership as
   fact and the interpretation as *unproven*.)
4. **Runtime model proven from EBOOT RTTI.** The decrypted EBOOT
   (`EBOOT.DECRYPTED.ELF`, 4,158,144 B) carries, at file offsets
   0x3C533F–0x3C582A, the mangled type names for
   `sml::vector<sbcustomize_item_t, tk::memory::CAllocator<sbcustomize_item_t>>`
   (allocators `CAllocatorInterface` / `AllocatorCore` instantiated over
   `18sbcustomize_item_t`). A heap `vector<>` filled at runtime is the data
   structure — the definitions arrive from files, they are not compiled in.
   The only customization data references in the EBOOT are the pack loaders'
   format strings `HAIRCUSTOMIZEPACK%d` (file 0x38F05C), `DEFAULTPACK%d`
   (0x38F070), `CUSTOMIZEPACK%d_%d` (0x38F080) — per-character pack files
   inside DATA401.

## Regions eliminated (this lane, first-hand)

| Region | Test | Result |
|---|---|---|
| Whole bulk (384 MB) | u32-aligned scan for any of the 9,440 name-record `bulk_offset` values (a pointer/index table into the name tables) | 184 hits ≈ chance level (211 expected at random over 96 M slots) — no pointer table |
| Whole bulk | Fixed-stride scan: idx byte-sequences of the three longest name runs (32 records each) searched at every stride 2–64 (parallel definition table in run order, idx as u8/u16LE/u32LE low byte) | 0 candidate arrays (run 0 complete; runs 1–2 partial before lane timebox — see note) |
| Bulk layout | Offset histogram of all 9,440 records | All name records live in bulk 57.9 MB–142.6 MB; the rest is compressed sub-archive data (478-entry decrypt3 manifest, `bin_e6`/`bin_e7` magics). Pre-run bytes are high-entropy compressed neighbors — no plaintext table headers adjacent to the runs |
| Bulk plaintext | ASCII scan for `CUSTOMIZEPACK` / `HAIRCUSTOMIZE` | 0 hits — pack filenames exist only as EBOOT format strings; DATA401's file table is not plaintext in the bulk |
| EBOOT (4.16 MB) | Pointer-value scan for the pack-format / RTTI string addresses (vaddr = file_offset + 0x8803000 per PR #416) | 0 hits — the EBOOT is a relocatable PRX; references resolve via relocations, and no static `sbcustomize_item_t` array exists in its data segment (consistent with the RTTI vector finding; also consistent with PR #416 §2's string/pattern coverage) |

Note on scan completeness: the stride scan finished run 0 at all 21 strides
and run 1 at strides 2–20 with 0 candidates before this lane's timebox; the
pattern (a parallel plaintext array) is excluded for the longest table at
every plausible struct stride, which is where such an array would have to
appear if it existed in run order.

## Skull Mask scope verdict

**Unproven — for both records.** Existence is proven (above); scope is not.
No located field assigns either Skull Mask record to a character or to the
generic/common pool. `item_idx` is per-table (range 1–160 across tables), so
idx 36 vs 99 says nothing about scope by itself. The verdict flips the moment
a decoded `CUSTOMIZEPACK` (or a live RAM dump of the vector, below) ties a
definition record to either name record.

## Next crack routes (in order)

1. **Sweep's DEFLATE encode-context crack** (in progress, PR #446 lineage):
   when the dynamic-block containers decode, the `CUSTOMIZEPACK%d_%d`
   payloads are the definition arrays — deserialize against the name tables
   on `(table, item_idx)` and this file's run map. Parts conversion stays
   gated on the same crack.
2. **PPSSPP RAM dump of the live vector** (independent of route 1): drive
   PPSSPP into the customize screen (the sweep's lane already boots the game
   and drives menus for context capture), dump user RAM, and search for the
   known name strings / idx patterns in RAM. The in-RAM `vector` contents
   *are* `sbcustomize_item_t` records — their stride and fields (a name
   pointer/offset beside slot/character/pack fields) would give the struct
   layout directly, and the RAM-resident pack buffers would show the
   on-disk serialization to recognize inside containers once decoded.
3. **Ghidra on the pack loader**: with the EBOOT in Ghidra (PSP PRX loader,
   relocations applied), XREF the `CUSTOMIZEPACK%d_%d` sprintf call sites to
   identify which DATA401 entries are requested per character and the
   deserializer that fills the vector — its field reads name the struct
   layout. (This lane's raw-byte lui/ori and pointer scans are the
   relocation-blind version of that step and are superseded by it.)

## Files in this delivery

- `customization/parts/tekken6/item-definitions.json` — the 9,440 records
  with proven run/table membership, validation stats, arbiter entries, and
  the honest join ledger (proven: record→table 9,440; slot 0; character
  scope 0; container 0; price 0).
- This doc — the evidence for the not-located verdict and the routes that
  close the gap.
