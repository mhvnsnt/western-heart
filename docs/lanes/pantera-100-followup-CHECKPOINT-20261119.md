# Pantera follow-up — COORDINATOR CHECKPOINT
Owner order (verbatim, 2026-11-18): "turn around is partial and all the other partial things you need to get them to 100%. filled in from kings T7 actual code."
Owner choice (2026-11-19 10:40 EST): "Run the follow-up lane for the 458 rows."
New owner requirement (2026-11-19): VISUAL PROOF, phone-viewable — every fix gets a short mp4 / contact frames in the repo (docs/proof/) with a stable link. No text-only "done".
Lane workdir: ~/workspace/_pantera-100-followup-20261119/
Started: 2026-11-19 ~10:41 EST
Coordinator: subagent (reports to parent; parent relays to owner).
First lane: ~/workspace/_pantera-100-20261118/CHECKPOINT.md — RESUME from it, never restart.

## LAWS
- Fill ONLY from King's T7 ACTUAL code/files. Never hand-tool a substitute clip, never invent one, never ship a fake. A missing real T7 clip = open gap WITH the extraction path, not a fake.
- Do NOT claim 100% until the r17 list is empty WITH probe proof. Every completion claim needs own-eyes proof: probe results AND video/frames.
- Branches + PR → merge only, never push main directly. PR bodies = instruction-gate format (Owner instruction verbatim, Method specified, Method used, Deviations, Proof with backticked paths in diff, Self-check ticked). After each merge, read back EVERY payload file from main (byte sizes, no sampling).
- Stage straight into the repo; no multi-GB local workdirs. Do NOT touch watchdog ledger, CloudDog (decommissioned), BAD tar.
- A blocked sub-job is recorded exactly and the lane moves on — no stalling, no silent skips.

## FIRST LANE RESULT (2026-11-19 ~00:21 EST)
- 70/643 → 185/643 real T7 clips (28.8%). PRs #1749–#1753 merged, HEAD 8249923. Pack 51→166 moves / 50→96 clips. 117 anim_ref updates to t7:king:*.
- Counting method: probe replicating Fighter._attackClipPlan tier 1 (slot resolution, grab guard, t7MoveClip with real normalizers); reproduced committed TSV exactly on baseline, then measured new state. Follow-up recount MUST use the same probe.

## MAIN STATE RE-VERIFIED (this lane, 2026-11-19 ~10:41 EST)
- Main HEAD at lane start: 01c9536 (PR #1763, WWE 2K19 PAC unpack toolchain — unrelated to Pantera).
- Commits since 8249923: #1754 (canon: Pantera partials to 100%, docs), #1755/#1757 (No Mercy bank), #1758/#1760/#1761 (clobber guard), #1759 (No Mercy full-ROM), #1763 (WWE PAC). NONE touch Pantera files.
- Pantera state on current main = first lane's readback exactly: pantera.json 3,355,474 B sha a5bbc5d776f3; moves.pack.json 4,355,654 B sha 7de6d95e03de; fighter.js 298,854 B sha a10384f1; graph.json 3,140,664 B sha 2e08e00b. Baseline for this lane: 185/643 (28.8%).
- First-lane sources (durable, workspace): ~/workspace/_pantera-100-20261118/lane-a-clips/ — CHECKPOINT.md (260 lines, full walker/fill design), fill-v4.json (361 KB, per-row blockers), walk-v4.mjs, validate-v4.mjs, fill-v4.mjs, clip-provenance.new.tsv. Lane C checkpoint: lane-c-grapples/CHECKPOINT.md (thrower-side T7 throw table + victim-gap extraction path). Lane B spec + dash gap: coordinator checkpoint + lane-b-engine/CHECKPOINT.md. Lane D proof method + harness: lane-d-proof/CHECKPOINT.md.
- KEY CORRECTION for this lane's scope: Lane A found "No 'clip missing from bank' gaps — every reached move's clip existed" (graph-clips bank: 772 clips, 10 shards). The 308 plain rows are walk/verification failures (unparseable 79, not-verifiable 84, walk-failed 22, verification-failed 21, *-variant 29, chain 70, rage 3, WH signature 5) — NOT proven clip absences. Lane F1 must re-classify per-row from fill-v4.json and determine honestly whether the bank is exhausted or more motbin extraction is possible, with evidence. Do not assume a bigger bank exists.
- "4 gated fills" question: Lane A's gate calibration passed common_1251 with a note and the other low-rootY clips as legitimate; v3/v4 promotes include d/f+3+4,1, d+3+4,4,4, d+3+4,4,4,2, f,F+1+2. Lane F1 must verify on current main whether those 4 rows play T7 clips now (probe), and only then record gate exceptions for any that are actually gated out.

## LANES (spawned 2026-11-19 ~10:45 EST, 4 in parallel)
- Lane F1 (clip bank + walker v5): OWNS moves.pack.json + provenance docs + fill scripts. Re-classify the 458 from fill-v4.json; walker/fill v5 fixes; determine bank-exhaustion honestly; build new pack + anim_ref updates. PR pantera-100-followup/clips-20261119. Merges FIRST.
- Lane F2 (data rows + engine follow-ups): OWNS pantera.json NEW ROWS/refs (WR.1/2/3/4/3+4, AB t8:→T7 refs) + T3 context map + gate exceptions + damage 19-vs-21 + dash travel gap (fighter.js movement paths) + uf+1+2 inconsistency + SS duplicates + slot-shadowing dead moves. Updates Lane B's WR.4-null test. PR pantera-100-followup/data-20261119. Merges SECOND (rebase onto main after F1 lands; pantera.json anim_ref lines F1 changes are different rows than WR/AB rows — line-based patch).
- Lane F3 (paired T7 throws + victim clips): OWNS t3-throw.js + throw/chain paths in fighter.js ONLY (no pantera.json/pack edits — data needs in a written spec for F1/F2). Victim-side clip search + kinmot→graph extraction; wire paired T7 throws (thrower table from Lane C checkpoint); victim plays a clip mid-throw; damage/break windows from wavu frame data only. PR pantera-100-followup/throws-20261119. Merges THIRD.
- Lane F4 (proof + visual clips): NO game-code edits except capture-harness hardening (spawn at stage ground level, zero vz, set p2.facing in __reset). BT-hit landing proof + BT.1/BT.4 T7 clips live + re-prove first-lane wins + new fixes; phone-viewable mp4s + contact frames in docs/proof/2026-11-19/pantera-100-followup/ + proof index README. PR pantera-100-followup/proof-20261119. Merges LAST (captures must be post-merge to be valid proof).
- Collision rule: only F1 touches moves.pack.json/provenance; only F2 touches pantera.json new rows/refs (F1 owns anim_ref lines); F2 (dash/run paths) and F3 (throw/chain paths) both edit fighter.js in DIFFERENT regions — coordinator merges in order F1→F2→F3→F4 and verifies no overlap; F4 is proof-only + harness.

## PROGRESS LOG
- 2026-11-19 ~10:41 EST: checkpoint created. Main re-verified (HEAD 01c9536; Pantera files byte-identical to first lane's readback). First-lane sources read (coordinator + Lane A + Lane C checkpoints). Next: spawn lanes F1–F4.

## THE 458 ROWS — GAP LIST
1. BIGGER T7 CLIP BANK (308 plain rows: rage/chain/oki rows, unparseable, no verification data, walk derailed — per-row in fill-v4.json + TSV). More motbin extraction from the actual T7 bank only.
2. STANCE/STATE ENTRY WALKS: Rage, JGS/JGR, CD, oki/ground.
3. T3 CONTEXT MAP: 106 _r/_c rows need a T3 row→context map.
4. GATE EXCEPTIONS: 4 fills gated out (d/f+3+4,1 common_1251; d+3+4,4,4 rotsm_403; d+3+4,4,4,2 rotsm_400 start non-upright; f,F+1+2 rotsm_468 dips 0.086 m below floor at f48 vs −0.08 m tolerance) — record a gate exception with measurements, do not silently relax the gate.
5. WR ROWS: WR.1/2/3/4/3+4 have NO data rows. Lane B spec: WR.3=Kg_666lk, WR.4=Kg_rk00, WR.3+4=Kg_dki11, WR.1=Kg_lp00F, WR.2=Kg_rp00F. Land the rows; update Lane B's test (asserts WR.4 resolves null).
6. PAIRED T7 THROWS: no victim-side paired T7 clips in repo; extraction path kinmot→graph pipeline for victim/common bank + wavu frame data. Throws still play T3; victim plays NO clip mid-throw (frozen pose).
7. BT HIT PROOF: BT.1/BT.4 fired but whiffed (FC.1+2 knockback 4.37 m). Prove a BT attack LANDING on screen + BT.1/BT.4 playing their T7 clips live.
8. DASH TRAVEL GAP: live 0.79 m vs node ~1.41 m — engine follow-up, not a clip problem.
9. MINOR: engine resolves 1+3/2+4 damage as 19, data row says 21 — resolve which row the engine picks. AB rows point at t8: refs (real T7 equivalents Kg_12Thrmv*/Kg_123Thrmv* identified, not yet wired) — wire them. Req 1085 + 2132 stay gated (condition 124 unknown; condition 36 needs metre conversion) — record exact blockers, do not assume.
10. NEUTRAL STOP: no req-0 stop in T7 data; WH clip-end stop stands as honest approximation — leave unless T7 data says otherwise.

## LANES
- (Fill in as spawned: lane ids, ownership, merge order.)

## PROGRESS LOG
- 2026-11-19 ~10:41 EST: checkpoint created. Main re-verified (HEAD 01c9536; Pantera files byte-identical to first lane's readback). First-lane sources read (coordinator + Lane A + Lane C checkpoints). Next: spawn lanes F1–F4.
- 2026-11-19 ~10:47 EST: lanes F1–F4 spawned in parallel (F1 bank/walker, F2 data/engine, F3 throws, F4 proof). Merge order F1 → F2 → F3 → F4. Next: collect lane reports, merge in order, read back payloads from main, recount X/643, synthesize per-gap verdicts + proof-clip list for the parent.
