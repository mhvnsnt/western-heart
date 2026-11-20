# TTT2 join — end-to-end decode proof (2026-11-04)

Produced by the JOIN CONTINUATION lane (round 4). Each file is the output
of the shipped decoder `tools/ttt2_mota_decode64.py` run on the exact
MOTA entry the join resolves to — no hand assembly.

- `roger-stance-decoded.json` — Roger move `Rg_sKAM00_` → anim
  `kjrg_kamae02(DVD)` → anim_ref bank 1, index 48 → data005-decoded.bin
  MOTA table at file offset 0x56B6C04, entry 48. Decoded: 270 frames,
  23 tracks.
- `common-fall-decoded.json` — Roger/Jun move `Fall_sKAM` → anim
  `naco_700dwn2(DVD)` → anim_ref bank 2, index 343 →
  data004-decoded.bin MOTA table at file offset 0x100, entry 343.
  Decoded by the same tool.

Full join writeup: `docs/tech/ttt2-mota/JOIN-SEARCH-ROUND4.md`.
Join data: `docs/tech/ttt2-mota/join/` (roger-join.json, jun-join.json,
unknown-join.json, bank-tables.json).
