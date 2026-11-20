# TTT2 SELECTIVE-EXTRACTION FEASIBILITY — assessment only

Gap-closure W7b, 2026-10-21. Question (owner legacy-parts order 2026-10-21
~09:39 CDT): can Tekken Tag Tournament 2 customization item data be
selectively extracted from release `ttt2-7z-v1` **without** full 13.36 GB
reassembly — and if so, by what exact method and at what disk cost?

## Verdict: NOT FEASIBLE (within the disk gate, and not item-shaped even past it)

Three independent walls, each sufficient on its own:

1. **The 7z is ONE solid LZMA block.** There are no per-file packed
   offsets to compute — the archive's single folder must be decompressed
   sequentially from byte 0 to reach any file (evidence in §1).
2. **The disk gate.** Reassembly/stream-through is gated at disk <70%
   used; the disk measured **89–96% used all day** (7.0 GB → 2.8 GB free
   across this lane's run). Even the cheapest stream-through variant
   (§3) needs ~5.2 GB of staged chunks for the FIRST game-data file —
   it does not fit today's disk, and the gate rule is not this lane's
   to breach.
3. **Even extracted, the content is not items yet.** The files are Xbox
   360 STFS containers (Data0000–Data0051 + 7 title blobs); all game
   content sits behind STFS container handling that the TTT2 teardown
   (2026-10-13) already found unwired on Linux, and behind it Namco's
   console model format. Selective 7z extraction was never the last
   step — it is the first of three.

Coordinator note (2026-10-21, after this assessment's evidence was in):
*"TTT2 [is] a fully written-off strand (7z → STFS → console model
format, three walls) — no catalog is expected, the slot catalog is
design reference only."* This doc is the evidence base for that
write-off. `customization/parts/tekken/ttt2-slot-catalog.json` remains
exactly that: a design reference (from public documentation), with its
own source line already stating item meshes were not extracted.

## §1. Header evidence (quoted, parsed this run)

Method: pulled ONLY chunk 1 (`ttt2-500m.part_01`, 524,288,000 B) and
chunk 26 (`ttt2-500m.part_26`, 256,424,393 B) from release `ttt2-7z-v1`,
sizes exact; assembled a **sparse** virtual archive (13,363,624,393 B
logical, ~780 MB physical) with chunk 1 at offset 0 and chunk 26 at
offset 13,107,200,000, and parsed it with py7zr 1.1.4. Both chunks were
cleared after evidence capture (store: the release itself; log:
`agent-ops/disk-cleanup-log.md`).

Signature header (bytes 0–31 of chunk 1):

```
signature  7z BC AF 27 1C, version 0.3
StartHeaderCRC  0xca1b9f71 — validates against the header bytes read
NextHeaderOffset  13,363,624,323   NextHeaderSize  38   NextHeaderCRC  0x2e0054aa
```

The 38-byte NextHeader at file offset 13,363,624,355 (i.e., **inside
chunk 26, the tail chunk** — chunk 1 alone cannot locate it) is an
*encoded* header:

```
17 06 f3 17 b2 88 1c 01 09 87 6c 00 07 0b 01 00 01 23 03 01 01
05 5d 00 00 80 00 0c bf 4e 0a 01 1c ae b1 a0 00 00
```

(`17` = kEncodedHeader, `06` = kPackInfo …) pointing at the real header
stream, which py7zr resolved from the tail chunk. **Which chunk is
needed: the LAST one (part_26) for the header; chunk 1 only for the
signature/start-header.** A header-only assessment needs both ends —
exactly the two chunks pulled.

Parsed header (py7zr `archiveinfo()` + StreamsInfo, verbatim):

```
solid=True, blocks=1, method_names=['LZMA'], header_size=1970,
uncompressed=13,452,865,536
PackInfo: packpos=0, packsizes=[13,363,622,423], numstreams=1
Folder: coders=[{method: 03 01 01 (LZMA), properties: 5d 00 00 80 00
        (dict size 0x00800000)}], unpacksizes=[13,452,865,536], bindpairs=[]
SubStreams: 72 unpack streams (the 72 files) inside the ONE folder
```

So: **one folder, one packed stream of 13,363,622,423 bytes, one
unpacked stream of 13,452,865,536 bytes, 72 files as substreams.**
Solid = every file's packed bytes are interleaved in the single LZMA
stream; the format stores NO per-file packed offset, by design.

## §2. What IS computable: uncompressed stream offsets per file

Substream order + sizes give each file's exact offset in the *unpacked*
stream (full table computed this run; key rows):

| unpacked offset | size | file |
|---:|---:|---|
| 0 | 155,930,624 | `00000002/3FADC8AF…` (title blob) |
| 645,443,584 | 2,034,626,560 | `00000002/98D464B9…` (title blob) |
| 2,759,323,648 | 1,942,929,408 | `00000002/FC2BA3B3…` (title blob) |
| 4,702,253,056 | ~3,100,000 total | 12 × `00009000/…` avatar-item packages (98–340 KB) |
| 4,705,210,368 | 45,056 | `392CFF5C9DB17CCAEBC3` (STFS descriptor) |
| 4,705,255,424 | 170,459,136 | `…data/Data0000` (first STFS data block) |
| … | 170,459,136 each | Data0001–Data0050 |
| 13,398,626,304 | 54,239,232 | `…data/Data0051` (last file) |

Customization items, if ever reachable, live inside the STFS Data
blocks (the teardown found no plaintext manifests at package level;
character/stage/item data is all inside the containers).

## §3. The exact selective method + cost, IF the gate ever clears

Because the block is solid, "selective" can only mean **stream-through
decompression**: concatenate the release chunks in order into a sparse
virtual file (as this lane did for the header), open with py7zr, request
one target file, and let the decoder decompress-and-discard everything
before it. Disk cost is then NOT the 13.45 GB output — it is:

- **Staged chunks:** every chunk containing packed bytes up to the
  target's packed end. Packed≈unpacked ratio is 0.99336 overall, but a
  target's exact packed end is knowable only by decoding to it; the
  safe upper bound is the chunk containing its unpacked end.
  - STFS descriptor + Data0000 (unpacked end 4,875,714,560): chunks
    1–10 ≈ **5,242,880,000 B ≈ 5.24 GB staged** (sparse; pulled
    chunk-wise, cleared per file after extraction).
  - Data0051 (the last Data block): chunks 1–26 = **the whole
    13,363,624,393 B** — no savings at all for late files.
- **Output:** 45,056 B (descriptor) or 170,459,136 B per Data block.
- **Scratch:** ~0 beyond the decoder's window (LZMA dict 8 MB) if the
  extractor streams; a naive `7z x` that writes all preceding files
  instead costs the full 13.45 GB and is NOT the method.
- **Time:** one full LZMA decode pass up to the target (≈35% of the
  archive for Data0000; ≈100% for Data0051) — CPU-bound, hours-scale on
  this shared box at observed contention.

And after paying that: the extracted Data blocks are STFS containers.
Per the TTT2 teardown (2026-10-13, `wh-ttt2` lane): STFS handling/
decryption tooling is not wired, and the inner content is Namco's
console model family — two more format projects before a single
customization item mesh exists. **Per-block reassembly ceiling: there
is exactly one block; the ceiling is the archive.**

## §4. Gate status

- Rule: TTT2 reassembly work starts only at disk **<70% used**
  (teardown-sweep-ttt2 checkpoint, owner program 2026-10-20).
- Measured this run: **89% (12 G free) at start → 93–96% (2.8–6.4 G
  free) during the run** — other lanes' uploads/downloads, not this
  lane's ~780 MB, which was cleared.
- **The gate was NOT breached.** No reassembly was attempted; the two
  pulled chunks served header evidence only and are cleared.

## §5. Bottom line for the parts program

TTT2 contributes **zero** parts and zero near-term parts: solid-archive
stream-through is possible in principle (§3) but is disk-gated, and
STFS + console-format work sits behind it. The slot-catalog JSON stays
a design reference. Revisit only when (a) disk <70% sustained, AND
(b) an STFS lane exists. Until then the honest TTT2 line in any census
is: **80 entries / 72 files held byte-exact on release `ttt2-7z-v1`;
items not extractable; strand written off by the coordinator
2026-10-21.**

*W7b lane, 2026-10-21. Header evidence captured from chunks 1 + 26 only;
both cleared after capture (disk-cleanup log).*
