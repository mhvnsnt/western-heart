#!/usr/bin/env python3
"""Round 3 evidence: EBOOT length table (0x8bd637c) packing, cracked.
LT values are the 32 signed halfwords quoted in round-2 evidence
(round2-evidence/experiments/exp_len.py, read from the decrypted EBOOT).
Claim: LT is indexed by (symbol - 256), NOT (symbol - 257) as rounds
4-11 and round 2's exp_len.py assumed. With that indexing:
  base(sym)  = -(LT[sym-256] >> 4)        (arithmetic shift, floor)
             = standard RFC1951 LBASE for all 29 length symbols
  extra bits = standard RFC1951 LEXT, encoded in the packed entry as
             -LT = (base<<4)                      if LEXT == 0
             -LT = ((base-1)<<4) + 1 + bitrev4(LEXT-1)  otherwise
Run: python3 lt_table_verify.py  -> prints ALL MATCH: True
"""
LT = [-25, -48, -64, -80, -96, -112, -128, -144, -160, -161, -193, -225,
      -257, -297, -361, -425, -489, -549, -677, -805, -933, -1069, -1325,
      -1581, -1837, -2083, -2595, -3107, -3619, -4128, -1, -1]
LBASE = [3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 15, 17, 19, 23, 27, 31, 35, 43,
         51, 59, 67, 83, 99, 115, 131, 163, 195, 227, 258]
LEXT = [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4,
        4, 4, 5, 5, 5, 5, 0]

def bitrev4(x):
    return int(f"{x:04b}"[::-1], 2)

ok = True
for i, (b, e) in enumerate(zip(LBASE, LEXT)):
    sym = 257 + i
    lt = LT[sym - 256]
    base_rec = -(lt >> 4)
    neg_expected = (b << 4) if e == 0 else ((b - 1) << 4) + 1 + bitrev4(e - 1)
    good = base_rec == b and -lt == neg_expected
    ok &= good
    print(f"sym{sym}: LT={lt} base_rec={base_rec} base={b} e={e} "
          f"-LT={-lt} formula={neg_expected} {'OK' if good else 'MISMATCH'}")
print("LT[0] (sym256, unused):", LT[0], " LT[30..31] (sym286/287):", LT[30:])
print("ALL MATCH:", ok)
