# Round-2 evidence bundle (2026-10-20, sweep lane 2)

Raw evidence behind `../ROUND2-DECRYPT-GMO-STATUS.md` and PR #388.
Kept in-repo per the store-and-work-off-disk law: the lane's local
scratch copies were cleared after this bundle was pushed and verified.

- `ghidra/decompI.txt` — Ghidra 12.1.4 decompilation of the EBOOT
  inflate region: wrapper 0x8b559c8, header validator 0x8b55ab0,
  inflate 0x8b55bf0 (region import of 0x8b54000–0x8b57000 at base 0;
  vaddr = file offset + 0x8b54000).
- `ghidra/decompM.txt` — decompilation of the CL reader / table
  builder 0x8b55fa4→0x8b560b4 plus Ghidra's listing of the main loop.
- `ghidra/listM.txt` — Ghidra listing of vaddr 0x8b55c00–0x8b55f50
  (function entry, block dispatch, transforms, builder calls).
- `ghidra/diag3.txt` — proof the MIPS disassembler works on region
  imports (the full-size import path fails on this VM; see the
  ROUND2 doc §3 environment note).
- `ghidra/scripts/` — the headless scripts that produced the above
  (DecompRegion, DecompMore, ListMatch, T6Opts, plus diagnostics).
- `experiments/` — the decoder probes: `exp_cl.py` (the CL
  repeat-semantics solve), `exp_batch2.py` (post-fix batch),
  `exp_blocks.py` / `exp_b1end.py` (block-boundary traces),
  `exp_len.py` (the four rejected length-composition readings),
  `exp_shift.py` (block-boundary shift sweep), `exp_emu.py`
  (Unicorn harness for the wrapper — stalled under VM contention).
- `scoreboard/final_scoreboard.txt` — the shipped tool
  (`../tekken6_gzip.py`) run over all 76 containers:
  20 BYTE-EXACT=True, 56 FAIL at a too-far distance.
- `scoreboard/iso_sha256.txt` — sha256sum output verifying the
  re-downloaded PSP ISO byte-exact against release `tekken6-psp-v1`.

Regeneration: all inputs live on GitHub — the EBOOT on main
(`teardown/tekken6/decrypted/`), the bulk + manifest in release
`tekken6-recon-20261016` (`work/decrypt3/` inside the tar).
