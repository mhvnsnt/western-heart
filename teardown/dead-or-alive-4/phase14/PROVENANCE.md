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
| chrone.afs | 366,094,336 | 366,094,336 | d6b99c60af3712a73a0a3901882c364ed1b613f55458bb400e066aa85e6000bc | 256886a06b1a0cd4405194c2bde10cc3675a721c47ff1aa64bb5f72082e919ff | **DIFFERENT** |
| chrtwo.afs | 548,042,752 | 548,042,752 | a7ca3ec4cc18bbcef99cb46eca78c8e0086930be13df343abd9ee9f801548e75 | a9169c2ad6ede8e2ad768d62cf5bf2eb55a25bedbf0781de04e98f70c4a34553 | **DIFFERENT** |
| chrthree.afs | 762,955,776 | 762,955,776 | 34eca0637d4c076503800aac89833ad0d8f27bc988e0097d8f53890c04482622 | da9386eabf253d77f60fe60179844c44ad0d38c9f72b134ab33447448a35ab80 | **DIFFERENT** |

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

### chrone.afs (complete) — MAJOR PROVENANCE FLAG

- Same size (366,094,336 B both), **first difference at byte
  0**, only **4.2795% of bytes identical** (15,667,147 /
  366,094,336), **0 of 87 4 MiB blocks identical**. No XOR
  relation (XOR stream is aperiodic noise).
- The two files are different KINDS of object: the ISO's
  chrone.afs is a **standard AFS container with 73 named
  entries** (chr_version.bin + .tpr/.cat pairs: zac00.tpr,
  zac00.cat, …). The mirror member (tar header
  `extracted/chrone.afs`, size field matches) is a **raw
  stream opening with f32 data** (`3e84aa31 3f0d2063
  bf482dab…` — the head phase 7 tabulated), not a container.
- Containment (payloads ARE related): the ISO entries'
  payloads occur inside the mirror stream at permuted
  offsets — zac00.tpr's 64 B head at mirror +262,148,096
  (ISO offset 4,096), its mid at +271,436,800 (8,192 B
  earlier than the ISO layout predicts — an internal shift);
  entry 2 (.cat) head AND mid at exactly layout-consistent
  mirror offsets, and the entry2→entry3 gap (1,376 B) is
  identical on both sides. So the mirror volume holds the
  same package payloads in a different physical layout with
  at least one internal size difference.
- **Consequence, stated plainly:** phases 6–12 model work
  was carved from these mirror payloads (by structure), so
  the MODELS stand on the same payload bytes — but the
  mirror chrone.afs is NOT the retail container, and any
  phase 6–12 claim of byte-identity between mirror chr
  volumes and the retail disc is FALSE. Per the task, this
  flag + numbers are the deliverable; no model rework is
  attempted in this lane.

### chrtwo.afs (complete) — MAJOR PROVENANCE FLAG (same class as chrone)

- Same size (548,042,752 B both), **first difference at byte
  0**, only **4.6732% of bytes identical** (25,611,380 /
  548,042,752).
- ISO copy: **standard AFS container, 128 entries** (head
  `41465300 80000000`). Mirror copy: raw f32-stream data
  from byte 0 (`3ebe10dc bf7ff769 bc7411d5…`), not a
  container. Same flag class as chrone; containment spot
  checks were run on chrone only.
- Mirror bytes for this row came from digest-verified tar
  parts 02 + 03 (release sha256 matched) plus the first
  30,462,464 B of the loop part-04 partial (sequential
  prefix written before its proxy kill; the row's verdict
  does not hinge on that span — the files differ from byte
  0 — and the span is re-validated when the verified
  part-04 lands: see PHASE14-STATE.md).

### chrthree.afs (complete) — MAJOR PROVENANCE FLAG (same class)

- Same size (762,955,776 B both), **first difference at byte
  0**, only **4.4639% of bytes identical** (34,057,353 /
  762,955,776).
- ISO copy: **standard AFS container, 188 entries** (head
  `41465300 bc000000`). Mirror copy: raw f32-stream data
  from byte 0 (`bf3f690f 3eed06e3 3eae2660…`, a repeating
  float pattern), not a container.
- Mirror bytes: digest-verified tar parts 02/03/04 plus the
  range-fetched part-05's first 276,950,016 B. Part-05's
  whole-file digest has since verified too (sha256
  cccd3eed… == release digest, `fetch_part_resume_p14.py`
  round 1), so every mirror byte used in this pass comes
  from a digest-verified part.

## Verdict — ALL FOUR FILES DIFFER (the major flag, complete)

**No mirror AFS file is byte-identical to the retail ISO
file.** anm (9.8271% identical), chrone (4.2795%), chrtwo
(4.6732%), chrthree (4.4639%) — all same-size, all differing
from byte 0. On the ISO side all four are standard AFS
containers (26 / 73 / 128 / 188 entries); on the mirror side
all four are raw streams from the earlier source image.

What this does and does not say about phases 6–12:

- The phases 6–12 MODEL work was carved from the mirror
  payloads by structure, and the chrone containment test
  (above) found the retail entries' payloads present inside
  the mirror stream at permuted offsets with matching
  inter-entry gaps — the payloads are the same logical
  content in a different physical layout. The models are
  not invalidated by this pass.
- What IS falsified: any claim that the mirror chr/anm
  files ARE the retail files, or that work verified against
  the mirror was verified against retail bytes. The mirror
  is a different pressing's/raw-layout source throughout —
  not only its anm.afs (the phase-13 correction widened:
  it applies to every AFS the mirror carries).
- Per the task: the flag + numbers are the deliverable.
  No model rework is attempted in this lane; re-deriving
  the 148 packages from the retail AFS containers (which
  are now fully extracted and released) is a named future
  lane, and the retail containers' entry structure
  (.tpr/.cat pairs, named) makes it a mechanical re-run,
  not a research problem.
