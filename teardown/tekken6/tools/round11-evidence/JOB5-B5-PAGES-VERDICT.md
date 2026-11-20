# Tekken 6 PSP — ROUND 11 JOB 5 (B5 PAGE RECORDS): geometry hypotheses REJECTED; pages = sparse 16/32B byte-record arrays

Date: 2026-10-22, round 11. Scripts: `round11-evidence/j5_pages.py`,
`round11-evidence/j5_scan.py`, `round11-evidence/j5_images.py`;
page images VIEWED: `round11-evidence/r11_b5_page_images.png`.
Data: idx24 slot 9 (88,768 B) from the retained decoded76 set.

## Correction to the inherited premise

The rounds 8–10 statement "payload 95% BE-float-sane" does NOT
survive a stricter test: it counted tiny denormal-magnitude
values as sane. Measured this round over the 40 pages:
**80.5% of all page bytes are 0x00**; per page only 9–26% of
bytes are nonzero. Page 0's BE f32 stream is 84% exact zeros
with the remainder dominated by small byte patterns
(0x00000800, 0x22020209, 0x4a010110 …). This is byte-structured
record data, not a float stream.

## Stride hypothesis verdicts (one line each, as briefed)

| Hypothesis (2,208 B page) | Verdict |
|---|---|
| BE f3 position stream, 184 verts (start 0 / 60 / 64) | REJECTED — stream fails the \|v\|<1e5 sanity bound (values to 1e37); 84% zeros; no coherent surface exists to render |
| BE f6 pos+normal, 92 verts | REJECTED — same byte statistics; "normals" are zero/denormal |
| BE f8 pos+normal+uv, 69 verts | REJECTED — same |
| BE f4, 138 verts | REJECTED — same |
| LE float stream (any stride) | REJECTED — LE sane-fraction is a denormal artifact; byte histogram is endian-structured (small bytes everywhere), not float-shaped |
| Byte image 48×46 / 69×32 / 92×24 / 184×12 (VIEWED) | REJECTED as image/texture — no picture; instead clear record periodicity (vertical stripes at 184-wide, repeating motifs at 48-wide) |
| GE display-list stream (LE u32, opcode = top byte) | REJECTED — opcode histogram has no PRIM(0x04)/END(0x0B) structure (4 and 3 occurrences in 22k words); top bytes are dominated by 0x00/0x11/0x01/0x10 = data bytes |

No point-cloud / triangle-soup render was produced: the leading
hypothesis (BE f3) fails its own sanity bound, so there is no
geometry to render — stated plainly instead of rendering noise.
No stage GLB is shipped from slot 9.

## What the pages ARE (measured)

- All 40 pages unique; each opens with a sparse field region
  (first nonzero byte at 0–54, varying), and nearly every page
  carries the constant word 0x00000800 at byte offset 52,
  followed by words of four small bytes (e.g. page 0:
  0x22020209, 0x4a010110, 0x59414016).
- Byte-value histogram (all pages): 0x00 80.5%, then 0x11
  (1,542), 0x01 (1,224), 0x10 (1,081), 0x22 (693), 0x12 (670),
  0x21 (659) — small enum/count-like bytes; only 9% of bytes
  exceed 0x40.
- **Record period measured**: nonzero-pattern autocorrelation
  of page 5 peaks at lag 16 (r=0.763) and lag 32 (r=0.593) —
  the page is an array of 16 B records (138/page) or 32 B
  records (69/page); on a 16 B grid, 71/138 records are
  populated in page 5; on a 32 B grid, 41/69.

## Exact residual / next discriminator

The per-record FIELDS are not yet decoded: a 16 B record whose
bytes cluster in {0x00, 0x01, 0x10, 0x11, 0x12, 0x21, 0x22}
reads as packed nibble/enum fields (possibly per-cell stage
collision/grid data or per-object parameter records — the stage
package context argues grid/collision over rendering data).
Next step (not run): align all 40 pages on the 16 B grid,
take the per-column byte alphabets across 5,520 records, and
identify constant vs counter vs enum columns; cross-check the
record count against the stage's slot-7 0x950-stride table
(round 10) which belongs to the same BE directory family.
Stage geometry, if any, is NOT in these pages in float form.
