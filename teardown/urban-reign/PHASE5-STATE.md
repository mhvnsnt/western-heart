# Urban Reign — Phase 5 State

Branch: `ur-phase5-names-polish` — base: PR #506 branch `ur-phase4-assignment` @ 4c5f40fa (stacked PR).
Lane: TEARDOWN COMPLETION SWEEP, Phase 5: name-bridge generalization + Job-3 executions.

## Inherited state (verified in Phase 4 — do not re-derive)

- 72 chars skinned+textured (`textured-models/` = THE canonical set, PR #464); 31/72 fighters natively animated (pmot banks: 001–005, 016, 020–022, 030–032, 041–046, 054–063, 070–072); 41 proxy fighters have NO per-character table in any shipped file (CLOSED SEARCH, Phase 4) — PCSX2-capture-gated; not re-opened here.
- NAME BRIDGE CRACKED (Phase 4 Job 2): `.bin` record format fully cracked; payload root stream = bank motion's decoded root track ×1000. P1/char001: 27/35 pairs PROVEN (max dev ≤0.06 mm), assigned in `game/assets/movesets/ur-char001.json` + `motion-names/name-bridge-p1-proven.json` + `motion-names/JOB2-NAME-BRIDGE-PHASE4.md`. 8 unproven for P1: 7 blocked by type-14 root-decode gap + record 14 (88 frames, no pmot candidate).
- Job 3 state: `PHASE4-JOB3-POLISH.md` (char064 one missing s16 group 1197/1260 verts; 11 chars with ≥1 unproven accessory piece; node-graph hunt closed for shipped files — H-index proven for bodies at 1.8e-07, suspect only for accessories; PPK 0xae00 decode test named as discriminating step).
- Motion cracking: `tools/ur_gyu.py` (56,844 tracks, 0 failures) — on the Phase-2 branch tree. ISO release `urban-reign-iso-v1`; SLUS_212.09 MD5 `0fa29bd55638f9ebe49feb494d4decd5`.

## Jobs

- JOB 1 — NAME-BRIDGE GENERALIZATION: apply proven P1 method to the other 30 pmot fighters. Per fighter with a held `.info`/`.bin` pair, run record↔motion root-stream match against that fighter's own pmot bank; assign ONLY pairs meeting the proven gate. Land per fighter: `motion-names/name-bridge-<char>-proven.json` + `motdatName` annotations in `game/assets/movesets/ur-charNNN.json`. Per-fighter summary table (held / proven / unproven-with-reason). NEVER force a match.
- JOB 2 — TYPE-14 ROOT-DECODE GAP: crack the type-14 variant from `.gyu` track-family code + Phase-2 sampler evidence, OR prove with data why those records' roots cannot be matched, naming the exact missing decode step. If cracked, complete P1 toward 35/35 and note cross-fighter impact.
- JOB 3 — EXECUTIONS: (a) char064 decoder reject-log step — recover missing s16 group or exact reject reason; if recovered, rebuild textured GLB with Phase-3 pipeline + assert counts. (b) 11 accessory pieces: PPK 0xae00 decode test — per piece PROVE placement/bone or record exact residual; NO guessed placements. (c) state explicitly whether 0xae00 test closes the accessory node-graph suspicion.
- JOB 4 — STATE + INVENTORY: this file kept current; update `WIRING-INVENTORY.md` motion/name sections to new proven counts.

## Progress log

- Phase 5 start: branch `ur-phase5-names-polish` created from `ur-phase4-assignment` @ 4c5f40fa + this state file + PR to be opened BEFORE analysis (stacked on #506).
- Analysis pending.

## Results

- (to be filled per job as work lands)
