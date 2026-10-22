# DOA4 Phase 13 — Job 2: the ANM definition layer — complete census, and the STATICALLY EXHAUSTED verdict

This phase executed ANM-READER5 §4's only remaining named route:
pull `D:\bin\anime_cm.bin` + the per-fighter `.bin` definition files
from the ISO and derive the anm record→stream mapping from them.
**The route was executed to its end. The files do not exist in the
shipped ISO — proven by a complete storage census, not by a failed
search — and with every other route already exhausted (phases
8–12), ANM is declared STATICALLY EXHAUSTED below, with the full
evidence chain.** No parser is claimed, no layout is guessed, no
clips are shipped (gate discipline, unchanged since phase 8).

Tools: `phase13/tools/xdvdfs_tree_p13.py`,
`phase13/tools/iso_assemble_p13.py`,
`phase13/tools/scan_bintable_p13.py`,
`phase13/tools/dump_binloader_p13.py`. Evidence:
`phase13/xdvdfs_tree_full.json` (62 entries), scratch
`p13/scan_bintable.txt`, `p13/data_bintable.txt`,
`p13/anm_regions.txt`, `p13/iso_assembly_log.json`.

## §1 What the definition layer was supposed to be

From the XEX's own string tables (local `workdir/default_pe.bin`,
censused this phase): a contiguous path table at file 0x278480
(true VA 0x82278480) names, in order, `:\anm.afs`,
`D:\bin\anime_cm.bin`, and 24 per-fighter files `D:\bin\<name>.bin`
(sambo, rtm, koryu, gokei, suiken, spartan, tengu, alpha, lisa, boy,
ayane, leifang, ninja, hakyo, bass, bayman, hika, genfu, kasumi, ryu,
karate, janlee, tina, zack), then `D:\dat\version\anm_version.bin`
at 0x278670. Nearby tables name ~206 `D:\bin\*.mot` files and the
`D:\dat\...` set (stage `sXXX_dat.bin` ×30, version bins, camera /
light / watch bins). A `.data` pointer registry (file 0xC4D588,
VA 0x82C6B388) holds one stored pointer per bin path, in reverse
order — the game's logical-file registry. Phases 11–12 established
that the loader pairs these definitions with the anm data at
runtime; the files were the last unexamined storage in the game.

## §2 The ISO pull (Job 1) — verification facts

Release `doa4-iso-v1` re-verified from the GitHub API before any
download: 30 assets, sizes summing to **exactly 7,834,892,288 B**,
per-asset sha256 digests recorded. Parts are stream-assembled by
`iso_assemble_p13.py` (download → sha256 vs the release digest →
sparse write at the part's ISO offset → part deleted):

| part | sha256 (== release digest) | status |
|---|---|---|
| 01 | d51386e4b1e3482c5355ca249033d3445f03ad5c491146dcff4534b5b78c4114 | landed, ISO [0, 262144000) |
| 02 | def4930de07de3242d2112d6906f2a0421bd2eb860bb27d2da0aa7ae5d63b212 | landed |
| 03 | 1e22b3b5ecfba1cf0e36a03cb5c05f70258740bb954997748a73c1228624f122 | landed |

(Assembly continues part-by-part in scratch `p13/`; the log
`iso_assembly_log.json` is the resumable state. The whole-ISO
sha256 is computable only at 30/30; every landed part is
individually byte-verified against the store, which is the
verification the one-store rule requires.)

**Early-doc correction (proven from verified bytes):** the
phase-1 EXTRACTION-REPORT's "XDVDFS partition at 0x390000, magic at
0x3A0000" is WRONG for this ISO — [0, 262 MB) contains no XDVDFS
magic at all (0x390000 carries DVD-video MPEG data). The partition
is the standard XGD2 layout: **base 0x0FD90000, magic
`MICROSOFT*XBOX*MEDIA` at 0x0FDA0000, root sector 152365, size
2048**. (The phase-1 extraction's file results stand — they are
hash-verified in the mirrors; its tool's brute-force scan is what
actually found the partition, and the offset note misrecorded it.)

## §3 The complete storage census — the files are not there

Every byte-addressable storage in the ISO was censused:

1. **XDVDFS (whole disc)** — `xdvdfs_tree_full.json`: 62 entries.
   Root: default.xex + 10 AFS files (chrone/chrtwo/chrthree/anm/
   mot/stg/avt/snd/spr/cmn) + 3 directories: `dic/` (3 Japanese IME
   dictionaries), `SOUND/` (26 entries: bgm_stream.xwb, 24 voice
   streams, doa4_sound.xgs), `movie/` (19 .sfd FMVs). **There is
   no `bin/` or `dat/` directory and no `.bin` file anywhere in
   the tree.**
2. **Standard-AFS filename blocks** (the game's D:\ paths resolve
   by NAME into AFS volumes — proven by cmn.afs, whose 7 entries
   are exactly the files the XEX calls `D:\dat\version\
   cmn_version.bin`, `D:\dat\camera\cam_raw.bin`, `D:\dat\light\
   rtmlight.bin`, `D:\dat\watch\rtmwatch.bin`, plus `comon.mot`
   and `efc0.tpr`): **cmn** 7 entries (above — no anime/fighter
   bins); **snd** 201 entries (snd_version.bin + .xwb/.xsb sound
   banks only); **avt** 700 entries (avt_version.bin,
   goodsdata*.bin/.bi, dmy.bin fillers, .tpr/.c/.tdp avatar data
   only); **spr** 53 entries (all sprite-scale sizes, 100 KB–10 MB;
   its attr block does not parse as name records). **No
   anime_cm.bin, no fighter .bin, no .mot names in any block.**
3. **Custom volumes** (chrone/chrtwo/chrthree/stg/anm/mot): no AFS
   header, no filename block; entries are index-addressed packages
   (phases 3–7). anm.afs and mot.afs are pure data to EOF (head
   and tail censused this phase) — no embedded name table, and
   (§5) no embedded offset table either.
4. **The XEX itself**: one `AFS\0` constant (a string, not an
   archive), no embedded sub-archive, no static (offset, size)
   allocation for any bin file (§4).

**Conclusion of fact: `anime_cm.bin` and the per-fighter `.bin`
files do not exist as stored files in the shipped ISO.** The
`D:\bin\` paths are logical registry entries (development-volume
paths); whatever backs them at runtime is resolved by the game's
file layer from the index-addressed volumes — i.e. dynamically,
exactly the class of the phase-12 texture-binding verdict.

## §4 XEX-side corroboration (this phase, new scans)

- Stored-pointer census: the bin path table is referenced ONLY by
  the `.data` pointer registry at 0x82C6B388 (26 pointers, reverse
  order) — a name registry, carrying no volume/offset/size fields.
- Lis/const-prop scan (phase-11 engine): NO code materializes the
  table base 0x82278480, the anime_cm string 0x8227849C, or the
  registry 0x82C6B388. The two apparent hits near the table
  (0x823FABA0, 0x823FB3A0) resolve to the adjacent AVATAR/HOUSE
  strings at 0x8227848C/94 — false adjacencies, named so nobody
  re-chases them. The one genuine neighbour hit (0x823FA430) uses
  `:\anm.afs` (0x82278480) in an AFS-volume lookup over the
  0x1C-stride descriptor table — the anm VOLUME, not the bin files.
- The 0x1C-stride table at 0x82C6CD7C holds runtime-initialized
  index data in the file image (0x07000040+i / 0x03000000+i runs),
  not static file allocations.
- The registry's surrounding `.data` (0x82C6B638+) is game data
  (u16 index-pair tables), not file descriptors.

## §5 anm.afs itself — the last un-censused regions, censused

If the definition data lived anywhere, anm.afs's unexamined spans
were the place. This phase censused them (local copy, 2,949,120 B,
sha256 b0b09edd79e056a5580c644509c47084b3da7dc170de6dd0e03f0d0c8bc54893,
from the doa4-mirror — byte-identical source to the ISO's anm.afs,
same size as the XDVDFS entry):

- **Offset-table signature scan, whole file, all 4 alignments:**
  NO run of ≥12 monotonically increasing BE u32s bounded by the
  file size exists anywhere in anm.afs. There is no (offset,…)
  table in the file.
- **Sparse-mid region [0x16B000, 0x29D000)** (1,253,376 B): 54.3%
  nonzero; 62,321 distinct u32s; s16 (v+1)%32 grid fraction 0.140
  (not the head encoding); f32 plausibility 0.426 — packed
  animation payload in a second form, NOT a definition table
  (a counts/offsets table is small-integer data; this is not).
- **Chunk [0x2A1000, 0x2B000)** (61,440 B): 42.3% nonzero, 4,217
  distinct u32s — same payload class (phase 8's "sparse table"
  reading is superseded by this census: its +8-field zeros were
  a 16B-grid artifact of the payload, not a TOC).
- Head [0, 0x6B000) and float regions: phases 7–8 censuses stand
  (27,392 × 16B records; ch4/ch5 quantized pair; 135 distinct +8
  u32s; byte-exact round-trip of the structural parse).

So anm.afs contains NO definition layer either — only the records
and their payloads, with no stored mapping between them.

## §6 Verdict — ANM STATICALLY EXHAUSTED (terminal)

The complete evidence chain, every route executed to a proven end:

| route | phase | result |
|---|---|---|
| Ghidra xref hunt on the anm strings | 10 | zero xrefs — later proven a wrong-image-base artifact (11) |
| Uniform bit-unpack of the head (9–13 bit, both orders) | 10 | grid fraction ≈ chance at every width — refuted |
| PPC lis/addi constant scan (true base) | 11 | loader family FOUND (anm%d.afs @0x8243D650, stream object, 0x20 stride) — record consumer NOT in it |
| Stream-build / completion functions | 11–12 | SDK handle-opener + tail thunk — no record read |
| Ring + 16-case tag translator, all 13 case bodies raw | 12 | (tag, key, value) command layer; NO shift/mask extraction on payload data in ~1,900 insns; records do not flow through the ring |
| Ring-writer census | 12 | 4 writers (tags 5/6/7/8), engine-internal scalars only |
| **Definition files from the ISO** | **13** | **DO NOT EXIST in the shipped ISO (complete storage census, §3)** |
| anm.afs internal definition data | 13 | no offset table (any alignment), no name table; remaining regions are payload (§5) |

The record→stream mapping and the 16B-record field layout are
therefore **not statically recoverable from the shipped game**:
the only information that ever connected records to streams was
the runtime file layer's dynamic resolution — the same terminal
class as texture binding (phase 12, DYNAMIC-ONLY). Any further
route is dynamic analysis (running the game under an emulator and
observing the loader), which is outside static teardown scope.

**Gate outcomes:** G2 (census) — landed (this doc + tree JSON).
G3 — lands as this declaration, per the job's terms ("that
declaration, if earned, is this lane's terminal ANM deliverable").
No parser, no clips: shipping either would require guessing a
layout, which eight phases of gate discipline exist to prevent.
The structural facts that ARE proven (record grid, ch4/ch5 pair,
region map, loader family, stream stride 0x20) remain the standing
corpus for any future dynamic lane.
