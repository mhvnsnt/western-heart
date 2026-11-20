# JOB 2 — COM SLOTS 25/26/30 STRUCTURE: **tail-zone layout PROVEN in part; payload schemas EXHAUSTIVE NEGATIVE**

Method: the 18 COM files as a panel (sha256 re-verified 18/18
against the round-7 JSONs this round), census slot boundaries
from round 13, correlates from the moveset JSONs (7,341 name
records). Data: `r15_slot_structure.json` (this directory).

## Proven: the tail zone and its MOTA placement (parser shipped)

Slots 25/26/30 are pointer-table slices of **one tail zone**.
The 6 MOTA chunks per file sit at **fixed offsets relative to
the slot starts** — slot25+604, slot26+624, slot30+564/+584/
+604/+624 — in all 18 files. `tools/r15_tailzone_parse.py`
reads every placement and cross-validates against known data:
predicted offsets == the round-7 JSONs' `mota.offsets` for
18/18 files, and all 108 chunks carry a valid MOTA header
(magic, ver 1, size 20); the four slot-30 chunks are the
byte-identical empty stubs of rounds 13/14, and slot 30's last
80 bytes are exactly those 4×20B stubs (slot 30 ends at EOF in
every file). The slot-26 stub's word_3 is 32 or 33 (per file);
the slot-25 stub is the empty form. **108/108 validated.**
Slots 27/28/29 (between 26 and 30) are 20B each of packed
payload — the pointer table simply cuts the zone finely there.

## Per-slot findings

**Slot 25** (len 1,812–2,652). Two parts. Head [0:604]: a
**fixed-size, low-entropy table** (H ≈ 2.0–2.4 in every file)
with a strong 12-byte periodicity (pooled byte-match
autocorrelation at lag 12 = 0.239, lags 24/36/48 ≈ 0.23/0.24/
0.22 vs ~0.004 random) built from records containing
(0x0016, X, X) u16 triples with X in the 0x800–0x9FF band,
per-character values; 14–30 triples per file, phase varies,
134/604 head bytes universal (mostly structural zeros).
Tail [624:]: packed payload, H ≈ 6.5–6.9.
Correlations of slot length: moves r=0.18, name bytes r=0.30,
file size r=0.35, strings r=0.23, count-word r=0.27 — **no
correlate explains the size**, and the triple count matches
nothing known (not move count, not count-word). The 12B-record
schema does NOT cross-validate against any known census →
**schema UNPROVEN** (the table's existence, size, period and
value band are proven facts; its field semantics are not).

**Slot 26** (len 4,168–4,708). Packed payload throughout
(head [0:624] H ≈ 6.5, tail H ≈ 7.2), **no size correlate**
(all |r| ≤ 0.14). It embeds a **shared u16 sub-table** at tail
offset ≈ +132 (absolute ≈ 776, Asuka 772): values from a small
set ({0x07, 0x13, 0x26, 0x164, 0x4fc, …}), present in all 18
files; long runs are shared between files (AK vs LAW: 469/756
bytes equal over [644:1400]; AK vs JIN 370/756; AK vs Asuka
186/756) and a high-entropy 16B-block cluster is shared by
{Armor King, Heihachi, Wang, Xiaoyu}. A common data block
exists inside the per-character payload; its fields do not
cross-validate against known data → **schema UNPROVEN**.

**Slot 30** (len **644 in all 18 files**). Layout proven:
[0:564] packed payload (H ≈ 7.2) + [564:644] the 4 MOTA stubs.
The payload is **byte-identical between ARMOR_KING and KING**
(644/644 bytes; the only identical pair in the panel) and
unique to every other file — a per-character payload that the
two King-family files share exactly. No periodicity
(autocorrelation on [0:564] ≤ 0.032 at lags 4–48), IC flat
≈ 0.0156 at periods 1–16 (no repeating XOR key), not
compression (round 14, 0/54). **Schema UNPROVEN.**

## Verdict and the exact next hop

No parser reads the payloads of slots 25/26/30 into records
that cross-validate against known data, and every static
angle in the brief was run: size correlations (above),
sliding-window entropy profiles (slot 25 bimodal 2.3/6.8;
slot 26 6.5/7.2; slot 30 uniform 7.2 + stub zone),
autocorrelation (12B period in slot 25's head only),
first-bytes classification (slot 25: structured u16 heads,
11 classes; slot 26: 9 classes incl. the shared
`1e0010003001…` family in 8 files; slot 30: per-file random
+ the AK≡King pair). The payloads are packed binary with no
static schema recoverable from the panel alone.

**Next hop (named exactly):** the EBOOT-side consumer — a
Capstone caller-chain hop from the COM pointer-table parser
to the code that reads slots 25–30 after load (the same
class of hop as rounds 12–14's descriptor hunt, pointed at
the tail zone), OR one PPSSPP session dumping the parsed
tail structures from RAM (the capture session already
specified for textures/palette in rounds 12/13 can take this
in the same sitting). No third static hop is claimed.
