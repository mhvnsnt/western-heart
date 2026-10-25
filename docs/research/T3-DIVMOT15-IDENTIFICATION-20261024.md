# T3 divmot15 — IDENTIFIED as Mokujin, with its wiring blocker (2026-10-24, Lane E)

## Identity: divmot15 = Mokujin — file evidence (not a guess)

1. Bank-field sequence gap. Every live T3 bank's `rows.pack.json`
   `bank` field names its divmot source. Present numbers are
   00, 01, 02, 03, 04, 05, 06, 07, 08, 09, 10, 11, 12, 13, 14, 16, 17,
   18, 19, 20 — i.e. 00 Paul, 01 Law, 02 Lei, 03 King, 04 Yoshimitsu,
   05 Nina, 06 Hwoarang, 07 Xiaoyu, 08 Eddy, 09 Jin, 10 Julia, 11 Kuma,
   12 Bryan, 13 Heihachi, 14 Ogre, 16 Gunjack, 17 Anna, 18 Bosconovitch,
   19 Gon, 20 Forest Law, plus 99 common in the 21-bin source listing.
   The sole missing number in 00–20 is 15.
2. Prior teardown docs name slot 15 directly: RENAME-MAP ("divmot15
   (Mokujin)"), docs/anim/BANK-TABLE-2026-10-20.md (dxmmii row:
   "divmot15 is ABSENT from the disc (BNS 295, size 0, proven)"),
   docs/anim/T3-REMAINDER-BANKS-20261020.md §4.
3. Mokujin's model exists but his motion does not, on the owner's disc:
   Mokujin KMD model is BNS record 207 (parses, 24,728 bytes); only the
   motion bank is absent. No fighter references mokujin as a t3_source,
   so nothing in-game changes today.

## Two discs, two states — do not merge them

- Owner's T3 disc image (teardown/tekken3/bns-table.pkl): BNS record 295
  = sector 17534, size 0. A raw read at sector 17534 of the size the
  original-disc index lists for divmot15 (127,368 bytes) yields header
  `00108701` — the start of Gun Jack's data (record 296, same sector,
  316,944 bytes), NOT a divmot stream. Conclusion: divmot15 cannot be
  baked from the owner's disc, and Gun Jack data at that sector must
  NEVER be baked as Mokujin (provenance break).
- Original Japan SLPS-01300 disc (BNS original index,
  tools/t3r/docs/research/bns-original-index.md): divmot15.bin IS present
  — records 194 and 198, LBA 10862 / 11000, 127,368 bytes, SHA-256
  `5cead15fe33b1e88cf54cf25b2c773763a71f89cdd369b85b584110ec6acc57c`.
  Its smaller size (127,368 vs ~260,000–400,000 for other divmots) is
  consistent with Mokujin's mimic role, but size alone is NOT the
  identification evidence — items 1–3 above are.

## Wiring status: NOT baked (honest gap, active path)

- DXMMII (Mokujin) keeps its FLAGGED jin substitution (BANK-TABLE G-T5
  note). A per-match mimic binding is a game-design option for the
  owner, not a silent default — no bank was fabricated from another
  character's motion.
- Active step to close it: re-rip the 127,368-byte divmot15 record from
  a complete disc image (Japan SLPS-01300 BNS, LBA 10862/11000),
  SHA-verify against `5cead15f…`, then run the identical divmot bake
  pipeline that produced the other 21 banks. Until that SHA matches,
  divmot15 stays open. Delegated to the coordinator's browser/GPU lane
  with these exact parameters (see GPU job E3 delegation note).
- Fallback if a future teardown holds it: TTT1/T5 Mokujin data (per
  PROCEDURAL_AUDIT G-T5 note). T3 is fallback-only per the instruction
  gate; this note logs the T3 use and the reason (no T5/6/7/8/TTT2
  Mokujin bank is available).

## Separate gap — do NOT conflate with divmot15

- `heihachi/` has NO `rows.pack.json` (33 files: clips + skeleton +
  reactions, but no rows pack). `heihachi_on_jin/` HAS `rows.pack.json`
  sourced from divmot13_heihachi (its bank field says so).
- Rule: bake heihachi's rows pack ONLY from a divmot13 source. Never
  copy heihachi_on_jin rows into heihachi (different target rig and
  used-by lists). This is a bake-completeness gap, not a missing-source
  gap like divmot15, and fixing one does not fix the other.

## Bank verification (GPU job E3, same batch)

22 bank dirs verified, 4,685 clips total across the 21 banks that have
a rows pack (per-bank counts in the E3 output JSON), heihachi the sole
bank missing a rows pack, divmot numbers present exactly 00–14, 16–20.
CPU baseline for the full verification pass: 0.879 s on this lane's VM.
GPU wall time and speedup are recorded by job E3 on its Kaggle/Colab run.
