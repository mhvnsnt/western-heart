# DATA401 Compression-vs-Cipher Spot Test (T6 Lane A, 2026-10-21)

Motivation (T5 precedent): on Tekken 5, a region that looked like a keystream
turned out to be LZSS compression. Standing rule: test compression-vs-cipher
FIRST before any cipher hypothesis on a new region.

Reproducer: `teardown/tekken6/tools/bulk_spottest.py`. Source: sweep lane's
ISO, read-only (`/home/hatch/workspace/_t6r4-work/iso/tekken6-psp.iso`).

## Sample
9 sectors across the manifest-declared bulk region (LBA 230253–417777):
230253, 230256, 250000, 280000, 310000, 340000, 370000, 400000, 417777.
(Chose LBA sampling because entry-indexed sampling is impossible: the IDX
entry map is encrypted — see DINF-MANIFEST-NOTES.md.)

## Per-sector tests
- Shannon entropy of the 2048-byte sector
- raw-DEFLATE (`wbits=-15`) and zlib-wrapped (`wbits=15`) decompress of the
  full sector AND of 512-byte windows (catches embedded streams)
- zlib header scan (`0x78 01/9C/DA`)

## Results
| LBA | entropy | deflate full | deflate 512B win | zlib hdr |
|-----|---------|--------------|------------------|----------|
| 230253 | -0.000 (all zeros) | no | no | 0 |
| 230256 | 7.919 | no | no | 0 |
| 250000 | 7.914 | no | no | 0 |
| 280000 | 7.913 | no | no | 0 |
| 310000 | 7.908 | no | no | 0 |
| 340000 | 7.916 | no | no | 0 |
| 370000 | 7.903 | no | no | 0 |
| 400000 | 7.905 | no | no | 0 |
| 417777 | 7.913 | no | no | 0 |

## Verdict
The bulk region is **NOT plaintext-compressed**: entropy ~7.91 uniformly, zero
DEFLATE/zlib decompressibility at sector and sub-sector granularity, zero zlib
headers. The T5 LZSS surprise does **not** repeat here. The bulk is cipher (or
compressed-then-encrypted — indistinguishable statically; stated as the honest
limit, not a claim).

Sector 230253 (first bulk sector) is all zeros — consistent with the 2026-10-14
"first sector all zeros" observation; re-confirmed here.

## Boundary note
This test is disjoint from the sweep lane's 76 DEFLATE containers: theirs are
live-PPSSPP-dumped *decrypted* containers (encode-context crack in
`_t6r4-work`); these are raw *encrypted* bulk sectors from the ISO. No
duplication, no contact with the sweep lane's work.
