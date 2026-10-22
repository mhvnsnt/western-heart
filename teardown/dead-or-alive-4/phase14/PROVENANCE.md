# DOA4 Phase 14 — Job 3: mirror-vs-ISO provenance pass

Question: do the mirror tar's AFS files (release
`doa4-mirror-20261017`, extracted tar; phase-6 member map) match
the same-named files in the owner's retail ISO (release
`doa4-iso-v1`, XDVDFS tree `phase13/xdvdfs_tree_full.json`)?

Method: ISO-side bytes read from the phase-14 assembled ISO
(every landed part sha256-verified against `doa4-iso-v1` digests
before writing). Mirror-side bytes range-fetched with the
phase-6 fetch tool (`tools/phase6/fetch.py`) for anm.afs; for
the chr* files the mirror tar parts were downloaded whole
(sha256-verified against the release asset digests) and the
members hashed locally — the range fetch ran at ~45 KB/s
(~20 h ETA for 1.68 GB) and was replaced by the part path
(~10× faster); the completed anm row is from the range path.
Per file: tar-header name+size (ustar header 512 B before the
member data), sizes, sha256 both sides, first differing byte,
byte-identical fraction over the common length.
Tool: `phase14/tools/provenance_p14.py`.

## Results

| file | mirror size | ISO size | mirror sha256 | ISO sha256 | verdict |
|---|---|---|---|---|---|
| anm.afs | 2,949,120 | 2,949,120 | b0b09edd79e056a5580c644509c47084b3da7dc170de6dd0e03f0d0c8bc54893 | 18eed8a09bb37ea6bc83e5572dd648fd55def823ebdcb6994adf8bb3a918b85a | **DIFFERENT** |
| chrone.afs | 366,094,336 | 366,094,336 | (pending) | 256886a06b1a0cd4405194c2bde10cc3675a721c47ff1aa64bb5f72082e919ff | (pending) |
| chrtwo.afs | 548,042,752 | 548,042,752 | (pending) | a9169c2ad6ede8e2ad768d62cf5bf2eb55a25bedbf0781de04e98f70c4a34553 | (pending) |
| chrthree.afs | 762,955,776 | 762,955,776 | (pending) | da9386eabf253d77f60fe60179844c44ad0d38c9f72b134ab33447448a35ab80 | (pending) |

### anm.afs (complete)

- Same size (2,949,120 B both), **first difference at byte 0**,
  only **9.8271% of bytes identical** (289,814 / 2,949,120).
- Entry count: the ISO file is a standard AFS container with
  **26 named entries** (phase 13). The mirror file is NOT an
  AFS container at all (head `c1ff2852…`; 27,392 × 16 B records
  per the phases 7–12 censuses) — entry count 0 as a container.
- Quantified confirmation of the phase-13 pressing correction:
  the mirror's "anm.afs" is a wholly different file that merely
  shares the retail file's exact size.

### chrone / chrtwo / chrthree (pending — fills in at completion)

Mirror member sizes from the tar headers equal the ISO sizes
exactly (366,094,336 / 548,042,752 / 762,955,776 — the phase-6
map's sizes, re-read from the ustar headers by the tool).
Hash verdicts land here when the part downloads + local
comparison finish; see PHASE14-STATE.md log for status.

## Verdict (to be completed with the chr* rows)

- If all three chr* files are IDENTICAL: phases 6–12 model work
  stands on retail bytes; only the anm file was swapped.
- If any chr* file DIFFERS: per-file first-diff offset + %
  identical are reported in the table's completion note as a
  MAJOR provenance flag (no model rework in this lane).
