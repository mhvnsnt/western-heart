# Tekken 6 (PSP) Customization Parts — Holdings Survey + Mesh Hunt

**Lane:** gap-closure W7a, 2026-10-21.
**Owner order (2026-10-21 ~09:39 CDT):** customization parts from the Tekken
games already in teardown become the active parts program — T5 + T6 + TTT2 —
with Tekken 7 parked for later. T6 PSP is the LEAD source (item-names DB
held, meshes via the sweep's teardown data — coordinate, never re-tear-down).

**Consumer:** `packages/creation-suite/src/catalogs.js` via
`customization/parts/tekken6/CATALOG.json` (this directory, PR #437
Phase-1 shape).

---

## 1. Verdict

**Zero T6 customization part meshes are extracted today — and the reason is
measured, not assumed:**

- The item MESH STORE is located (§2): 2,546 embedded custom-DEFLATE
  "GZIP" containers inside the 81 MB `bin_e6.2` archive in the decrypted
  DATA401 bulk.
- Those containers share the ONE remaining DATA401 decode defect (§3):
  they were encoded against a decode context the game's own bundled
  inflate does not provide — proven by executing the EBOOT's inflate
  under Unicorn (PR #413). 20/76 top-level containers decode byte-exact;
  the dynamic-block population — the embedded item containers are that
  population — does not yet decode with any decoder we hold.
- NDPP is NOT the item mesh format (§4): its sections are metadata +
  bounding volumes + normals, verified to contain no vertex positions.
- The item NAME side is fully held (§5): 9,440 records (PR #416), but the
  `sbcustomize_item_t` definition array that would join names to
  slot/character/model-pack is NOT located — so even the names cannot be
  authoritatively classified yet. Mesh-side evidence will be the
  authority when the decode lands.
- Skull mask: the NAME is confirmed in T6's own tables (§6) — two real
  records. Its mesh is behind the same decode wall. Registered as a
  named gap under its tekken6 id; the tekken7 named gap is untouched.

No parts are fabricated, force-matched, or silently dropped anywhere in
this survey. Unkeyed/unresolved material is cataloged as named gaps with
evidence.

## 2. The mesh store — located

Per PR #388 (teardown sweep round 2, `teardown/tekken6/tools/
ROUND2-DECRYPT-GMO-STATUS.md` §5), the NDPP archive `bin_e6.2` (DATA401
IDX entry 87, an 81,591,641-byte plaintext archive inside
`bulk_decrypted.bin`) holds:

- **2,546 embedded GZIP containers — the customization parts**, and
- 950 NDPP bounding volumes (1,103 boxes / 357 sections landed on main
  in PR #187 as `teardown/tekken6/models/ndpp_bounding_volumes.glb`).

The pack patterns in the decrypted EBOOT agree: item model packs load as
`CUSTOMIZEPACK%d_%d` and `HAIRCUSTOMIZEPACK%d`
(`teardown/tekken6-customization-research.md` §1), and the customization
type system (`sbcustomize_item_t`, `tcb_CustomizePSP_Manager`, 12
`kkItemMotionTick` handlers) is catalogued in
`customization/parts/tekken/tekken6-item-catalog.json` (PR #416).

Bulk source, byte-verified: release `tekken6-recon-20261016`
(`t6-recon-backup.tar`, SHA-256
`2c738b24f46395960e463fd03c637b038a0942590c0055b9ef3fe1bc9d77afcc`),
path in tar `tekken6/work/decrypt3/bulk_decrypted.bin` (384,073,728 B).

W7a first-hand check on the SHA-verified bulk: this lane scanned the
entry-87 archive (2,760 `GZIP` magic hits — the 2,546 real containers
plus mid-stream false positives) and ran the existing decoder
(`teardown/tekken6/tools/tekken6_gzip.py` from PR #388, unmodified) on
the first 300 plausible embedded containers (20-byte header, sane
uncompressed size, zlib stream start): **6/300 byte-exact — and none of
the six is a mesh.** The six payloads (336–3,200 B) are small u32
offset/index tables (leading count 13 or 6, then offset pairs) —
infrastructure data. 20 more containers decoded without an exception
but failed the size/adler oracle; 255 failed with the signature
`dist > out_len` defect; 23 were invalid-Huffman false positives; 2
blew the output cap (false positives). So the decodable class in this
archive is small structured data; **every mesh-bearing container in the
sample sits in the blocked dynamic-block population.** Full method and
numbers in the appendix.

## 3. The decode wall — one defect, emulator-proven

State of the DATA401 custom-DEFLATE crack (PRs #388 + #413, both OPEN;
checkpoint `teardown-sweep-tekken6-psp.json`):

- 20/76 top-level containers decode byte-exact (size AND adler32 — the
  oracle the EBOOT wrapper at 0x8b559c8 itself returns).
- Round 2 solved the code-length repeat semantics (Ghidra-proven);
  round 3 solved the length-table packing (off-by-one; all 29 symbols
  match RFC 1951 LBASE/LEXT read directly from the EBOOT).
- Round 3's Unicorn ground truth then REFRAMED the defect: the game's
  own inflate, executed on container 0, returns error 0x80000108 after
  producing exactly the same 2,815 bytes as the Python decoder, failing
  at the same match. The loader (sole wrapper caller 0x89d27a0) supplies
  no priming, no dictionary, no preprocessing (FDICT is rejected by the
  wrapper). The containers were encoded against a decode context no
  artifact we hold provides.
- Named next step (owned by teardown sweep round 4, in flight): PPSSPP
  live trace of a real DATA401 load — record whether the runtime calls
  this inflate for these entries at all, and with what (dest, src).

The 18 COM containers (gzip idx 58–75) and the 2,546 embedded item
containers are all behind this same wall. **The GMO→GLB pipeline behind
the wall is already proven** (PR #388 §5: PiosGmoLibrary → gmo2json →
Blender 4.0.2 glTF export; `cloud.glb` from a real PSP GMO sample
re-imported and front-rendered; GIM textures via puyotools). What is
missing is decrypted Tekken 6 GMO payloads, not tooling.

## 4. What NDPP is (and is not)

`teardown/tekken6/models/NDPP-FORMAT.md` (on main, PR #187), from an
exhaustive scan of the 81 MB archive and a decoded NDPP container:

- NDPP sections carry a 20-byte header, 64-byte descriptor records
  (validated bboxes), 8-vertex bounding volumes, and normal arrays.
- **No contiguous vertex-position arrays. No index buffers.** The
  0x190001 section's longest position-like float3 run is 3 triplets.
- Interpretation: NDPP = per-part/per-bone bounding volumes (hitboxes /
  culling) + normals — metadata, not render meshes.

So the earlier shorthand "T6 PSP models are NDPP-format" does not hold
for render geometry: the render meshes are the GMO payloads inside the
§2 containers. (The one NDPP GLB the J1 lane handled is the bounding-
volume GLB above — correctly labeled as bounding volumes in its own
doc, never as character/item meshes.)

## 5. The name side — held, but not joinable yet

`customization/parts/tekken/tekken6-item-names.json` (PR #416, on main):

- 9,440 records in runs of 4+ (11,053 valid record starts), extracted
  from the SHA-verified bulk; record = u32 rec_size + u8 item_idx +
  ASCII name. item_idx range 1–160, **per-table** (the same idx recurs
  across language tables and categories).
- Tables are per-language copies AND per-character/category lists,
  interleaved in unmapped bulk regions; language boundaries are not
  clean and lang_id is not recoverable from the record format alone.
- Census of the held records (this lane, by name content): 41 mask-named
  records, 77 hat/helmet, 72 glasses, 79 weapon-named, 147 effect,
  1,056 aura/ki (the aura/ki count is inflated by per-language copies).

The join key to slot/character/price/model-pack is the
`sbcustomize_item_t` definition array — **NOT located** (PR #416's named
gap; candidates: EBOOT data segment, or a binary table adjacent to the
name tables). Until it is found (or the decoded pack layout supplies the
key), a name record CANNOT be authoritatively assigned a slot, a
character, or a mesh container. This catalog therefore classifies
nothing from names alone.

## 6. Skull-mask survey (by content)

Question: does T6 PSP have a skull/mask-type generic head item?

Method: exact + pattern search over all 9,440 held name records
(`skull|mask|skeleton|bone`, case-insensitive → 43 hits), then context
reads around every exact hit.

**Exact name `Skull Mask` — 2 records:**

| # | bulk_offset | item_idx | Table context (neighboring records in the same table run) |
|---|---|---|---|
| A | 124,705,559 | 36 | Head-category cluster: Default Head, Cyclops, Twisted Clown, Default Head, Sports Cap, Dark Helm, Mechanical Mask, Beginner's Mask, Bandana, **Skull Mask**, Mad Beast, Cowboy Hat, Thick Frame Glasses, Aviator Sunglasses, Sharp Sunglasses — followed in the same region by a rage/aura cluster |
| B | 129,124,535 | 99 | One character's full item table — face cluster first: Modified Gas Mask (98), War Paint Black/White/Camo (96/97/95), Reaper Face Paint (94), **Skull Mask** (99); then upper items idx 1–7 (2P Top, 1P Top, Military Coat, Shirtless, Joker Top, Straitjacket Top, Heavy Combat Armor), lower idx 108–114, weapons (Sledgehammer, Japanese Sword, Broadsword, Death Scythe, …), effects |

Corroboration: the German table paired with B carries `Totenkopfmaske`
(item_idx 99, bulk_offset 129,137,527) and `Modifizierte Gasmaske`
(98) — the same two items at the same idx, so record B is a real item in
a real per-language table set, not a scan artifact.

**Verdict:** a skull mask EXISTS in Tekken 6 PSP's item tables by name —
twice, in two different tables. What held data does NOT establish:
(a) which character(s) the tables belong to, (b) whether either record
is a GENERIC item (T6 tables are per-character lists; record B sits in
one character's full list, record A's cluster reads as a head-category
list whose owner table is unidentified), (c) which embedded container
holds its mesh. Scope is therefore recorded as unproven on the named
gap (`tekken6:cmn:head:skull-mask` — the `cmn` segment is the catalog's
expected-source placeholder, NOT an assertion of generic scope; the gap
entry states this explicitly). The tekken7 named gap stays untouched.

Other mask-family names in the tables (content evidence for the mask
need generally): Wrestling Mask, Rudo Mask (4 colors), Mummy Mask (4),
Ultimate Mask (4), Mechanical Mask, Okina Mask, Phantom Mask, Crow
Mask, Tengu Mask, Dark Fist Mask, Bastet Mask, Assassin Mask, Modified
Gas Mask — masks are a real T6 item family; the skull entry is the
named target.

## 7. Slot mapping — T6 schema → registry shape, and divergences

Held schema: `customization/parts/tekken/tekken6-slot-catalog.json`
(source note in that file: compiled from public documentation in
2026-10 — PSP archives were still encrypted at the time; treat its
titles/anchors as the working schema, to be re-verified against decoded
data when it lands).

| T6 slot | slot_id | anchors | suite_slot (held schema) | T7 fan-out (schema's own t7_slot_map) |
|---|---|---|---|---|
| head | 1 | Head, HairSocket, FaceSocket | hair | T7 1 HEAD |
| upper_body | 2 | Spine1, Chest, ShoulderL, ShoulderR | upper_body | T7 9 UPPER |
| lower_body | 3 | Hips, LegL, LegR, FootL, FootR | lower_body | T7 11 LOWER |
| other | 4 | Back, HandL, HandR, AuraRoot | accessory | T7 12 UPPER_ACC / 13 LOWER_ACC / 14 EXTRA (by item type) |

Divergences from T7's 16 slots (also in CATALOG.json `_meta`):

1. **Four slots, not sixteen.** T6 `head` is one bucket for hats,
   helmets, masks, glasses, hairstyles and facial hair — T7 splits it
   eight ways (HEAD/HAIR/FULL_HEAD/HAIR_ACC/GLA/FACE/FACE_HAIR/MAKE_UP).
2. **The held T6 schema maps head → suite_slot `hair`.** Followed here
   for schema fidelity; head-GEAR entries (masks/helmets/glasses) will
   need per-content suite_slot refinement (head/full_head/glasses/
   face) at import time, recorded per entry — the skull-mask gap
   inherits `hair` from the schema and flags this.
3. **T6 `other` fans out** to three T7 slots by item type; weapons,
   auras, effects and companions share it.
4. **slot_id type:** strings ('1'..'4') in the held schema; integers in
   catalog entries (registry shape).
5. **Conflicts (held schema):** full-body items clear Upper+Lower;
   one head-gear item per Head slot; mask + glasses may coexist
   (different sub-slots) — noted for the suite's equip logic.

## 8. Counts

| Class | Held (names) | Meshes located | Meshes decoded | Converted GLB | Cataloged parts |
|---|---|---|---|---|---|
| head (T6 slot 1) | names exist, unjoinable | in §2 store | 0 | 0 | 0 |
| upper_body (slot 2) | names exist, unjoinable | in §2 store | 0 | 0 | 0 |
| lower_body (slot 3) | names exist, unjoinable | in §2 store | 0 | 0 | 0 |
| other (slot 4) | names exist, unjoinable | in §2 store | 0 | 0 | 0 |
| **Total** | **9,440 name records** | **2,546 containers** | **0** | **0** | **0 parts, 2 named gaps** |

Unkeyed count: all 2,546 containers are currently unkeyed (no container
has been joined to a name) — they are cataloged as the full-set named
gap with this evidence, not dropped and not force-matched.

## 9. Proof render — not applicable, honestly

The brief's proof render requires one representative part placed on a
fighter. No part mesh exists to place: rendering anything would mean
rendering a bounding volume or a stand-in, which this program does not
ship as a part proof. The proof obligation transfers to the first
decoded part: when the decode lands, the skull mask (if its container
is among the first decoded) or the first head/upper part gets the
`apply_customization.py` / PartPoser placement + front render +
own-eyes check, and `catalog.test.mjs` test 3 flips to resolved. The
bounding-volume GLB's own previews already exist on main
(`teardown/tekken6/models/previews/`) and are NOT presented as part
proof.

## 10. Continuation state

1. **Decode crack** — teardown sweep round 4 (PPSSPP live trace) owns
   the encode-context hunt; W7a does not duplicate it (CHECK-BEFORE-
   STARTING). When it lands: decode bin_e6.2's 2,546 containers with
   `tekken6_gzip.py`, inventory payloads (GMO magic), convert via the
   proven pipeline, key against the name tables + definition array,
   append parts to this catalog additively.
2. **Definition array hunt** — `sbcustomize_item_t` array (EBOOT data
   segment / pre-table region adjacent to the name tables); whoever
   finds it unlocks the name→slot/character/pack join for all 9,440
   records.
3. **Count reconciliation** — the owner's parallel read-only
   `tekken-customization-inventory` scout (T5DR/T6/TTT2) had not landed
   when this survey was written; when it does, reconcile its T6 counts
   against §8 and flag discrepancies in the open — never silently
   override either side.
4. W7b/W7c (T5, TTT2) proceed under the same Phase-1 shape; T7 stays
   parked per the owner's order.

## Appendix — W7a embedded-container test (first-hand)

Method (this lane, 2026-10-21, all against artifacts pulled fresh from
the store and verified):

1. Downloaded release `tekken6-recon-20261016` (3 tar parts,
   524,288,000 + 524,288,000 + 82,708,480 B). Concatenated
   SHA-256 = `2c738b24f46395960e463fd03c637b038a0942590c0055b9ef3fe1bc9d77afcc`
   — byte-identical to the value recorded by PR #416 / round 2.
2. Extracted only `tekken6/work/decrypt3/bulk_decrypted.bin`
   (384,073,728 B) + `manifest.json` (478 entries).
3. Entry 87 sub `y` (`bin_e6.2`, start_rel 38,592 sectors, 81,591,641 B)
   read out of the bulk; scanned for `GZIP` magic: **2,760 hits**.
4. For each hit with a plausible 20-byte container header (w[3] =
   uncompressed size in (0, 64 MB]) and a zlib stream start, ran
   `tekken6_gzip.decompress()` (the PR #388 decoder, unmodified) and
   scored byte-exactness by the EBOOT's own oracle (output size +
   adler32 trailer immediately after the stream).
5. Result, first 300 plausible containers: **6 byte-exact, 0 meshes.**
   - 6 byte-exact: archive offsets 3,074,288 (3,200 B), 3,278,880
     (336 B), 4,135,776 (416 B), 5,939,552 (1,088 B), 6,267,584
     (416 B), 6,294,256 (1,088 B). Every payload is a u32 table:
     leading count (13 or 6) followed by offset/size pairs
     (e.g. `0d000000 70000000 70020000 e0020000 …`). No GMO magic
     (`OMG.00.1PSP`), no NDPP, no float geometry — these are
     sub-archive index/infrastructure tables, and the two 416 B and
     two 1,088 B payloads are pairwise identical duplicates.
   - 20 decoded without exception but failed size/adler (the
     round-3 lenient-parse class).
   - 255 failed `dist > out_len` (the signature defect; first failure
     at out_len 128–2,773 across the earlier 40-sample detail run).
   - 23 invalid Huffman code + 2 output-cap — magic false positives.
   Sample usize range (first-40 detail): 11,184–101,952 B.

This confirms first-hand, on this lane, what rounds 2–3 inferred: the
embedded item containers are the blocked dynamic-block population, and
the small fixed-block class that does decode carries tables, not
geometry. No new format code was written for this test; the framing
used is the decoder's own documented container layout.
