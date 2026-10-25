# Soulcalibur II (Xbox) — Phase 14 Probes (evidence-only)

Two small probes from the phase-14 dispatch. Neither probe's result
changes any shipped artifact; both are recorded with their evidence
and a verdict or a named next step.

## Probe A — rec80 secondary texture layer (rec80 +0x0c)

Question: is the second VXT pointer in each 80 B material record
(+0x0c, beside the primary at +0x08) a real runtime texture
reference, and what is its role?

Method (bytes only, all 22 P1 fighter bundles): walk every rec80
record (635 materials), read +0x0c, and test whether a non-zero
value lands exactly on a VXT texture record of the same VMX
((ptr − VXT base − 0x14) divisible by 36 with quotient in range).

Result:

- 159 of 635 materials carry a non-zero +0x0c pointer.
- **159/159 land exactly on a VXT texture record.** A coincidental
  or garbage field does not divide exactly 159 times in a row; the
  field is a genuine second texture-record reference, laid out
  identically to the primary.
- Presence does NOT correlate with the material's w0 low byte
  (carriers: w0 low byte 2 ×95, 1 ×63, 0 ×1; non-carriers have the
  same spread) — the phase-13 note in `VXT-FORMAT.md` tying the
  secondary to a w0 flag class is not supported by this census;
  pointer presence is the only reliable signal.

Verdict: **the secondary pointer is a real second texture layer
reference** (same record type, same relocation class as the
primary). Its runtime role (detail map / environment map / alpha
layer) is NOT established by this probe: that needs the XBE
material-setup consumer read (the function that uploads rec80
records and binds texture stages — the relocator `FUN_00025300`
neighbourhood in the GRE decompile corpus). Named next step: trace
which texture stage the +0x0c record is bound to in that consumer;
until then, phase-13's shipping rule stands (primary →
`baseColorTexture` only; secondary recorded, unassigned). No GLB
changes from this probe.

## Probe B — in-bundle type-0xc sound payload

Question: what format is the character sound resource (type 0xc in
the `FUN_00033fb0` resource table) inside the v982 model bundles?

Evidence gathered:

1. **Bundle section directory located.** Every P1 bundle carries
   the same directory at bundle+0x3800: u32 count = 14, u32 = 128,
   then 14 ascending section offsets (sections are 128-aligned;
   bundle bytes before 0x3800 are zero — a zeroed header page the
   loader fills). Size census (all 22 bundles, bytes):

   | Section | Size pattern across the 22 bundles |
   |---|---|
   | 0 | 640 in every bundle |
   | 1 | 15,232–29,184 |
   | 2 | 7,040 (0 in idx398) |
   | 3 | 0–57,216 |
   | 4 | 3,584–13,952 |
   | 5 | 0–3,456 |
   | 6–10 | 0 in every bundle |
   | 11 | 406,656–581,120 (the large dense section; idx827 is the outlier at 71,040) |
   | 12 | 125,312–502,528 (contains the bundle's VMX#2 in the sampled idx47 layout) |
   | 13 | 0 (last offset sits at the bundle tail) |

2. **No standard audio container magic anywhere.** Full scans of
   the idx47 / idx125 / idx944 bundles find zero occurrences of
   `(c)CRI`, zero ADX file headers (0x8000 + coding-type pattern),
   zero `RIFF`, zero embedded `AFS\0`. The bgm.afs music is plain
   ADX (JOB 3), but the in-bundle payload is not stored as plain
   ADX files.
3. **vgmstream rejects the candidates.** Slices of idx47 sections
   1, 3, 11, 12 all fail vgmstream-cli open ("failed opening") —
   no standard stream format at those offsets.

Verdict: **format unproven.** The phase-13 expectation ("CRI
ADX-family, unproven") survives only as a family guess: CRI's
runtime sound banks on Xbox commonly store headerless ADX/AHX
frames or a CRI ACB/AWB-style bank, none of which carries a magic
a scanner can find, and the section↔type mapping (which of the 14
sections is type 0xc) is itself not yet proven — section 12
containing VMX#2 warns against assuming the directory is purely
the `FUN_00033fb0` table in type order. Named next step (one
targeted read, not a sweep): decompile `FUN_00033fb0` in the XBE
(`~/workspace/scii-work/p2/default.xbe`, Ghidra project
`~/workspace/ghidra-projects/soulcalibur2/`) to pin (a) the true
resource directory location/format, (b) the type-0xc section's
offset/size fields, (c) the codec call it feeds; then extract one
payload and re-test with vgmstream/txth. No audio was extracted
from bundles in this phase, and none is claimed.
