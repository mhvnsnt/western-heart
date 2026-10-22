# DOA4 Phase 10 — STATE — OPEN 2026-10-22

Branch: `teardown/doa4-phase10-anm-clips` (stacked on `teardown/doa4-phase9-heads-anm`, PR #487).
Clone: ~/workspace/_doa4p8-clone (sparse, teardown/dead-or-alive-4 only). Scratch: ~/workspace/_doa4p2-scratch/ (p10/ new; p8/p9 retained).

## ENVIRONMENT FIX — VERIFIED (phase 9's "no JDK" blocker was false)
- JDK: `/home/hatch/workspace/tools/ghidra/jdk-21.0.12.1+1` — `java -version` = `openjdk version "21.0.12.1" 2026-08-18 LTS` (Temurin-21.0.12.1+1).
- Ghidra: `~/workspace/tools/ghidra/ghidra_12.1.4_PUBLIC/support/analyzeHeadless`, project `~/workspace/ghidra-projects/doa4/` (DOA4.gpr).
- Smoke test 2026-10-22: `JAVA_HOME=/home/hatch/workspace/tools/ghidra/jdk-21.0.12.1+1 analyzeHeadless ~/workspace/ghidra-projects/doa4 DOA4 -noanalysis -scriptPath phase9/tools -postScript FindAnmReader.java` → **exit 0, script executed** (string enumeration output produced). Phase 9's blocker is DEAD. Run ALL Ghidra with JAVA_HOME exported above.

## Inherited verified facts (phase 9, do not re-derive)
- Heads = separate head+hair packages in chrtwo.afs pkg04–45 (42 packages, 31 distinct GLBs); anchor-bone matching maps heads→body families (Δ≤0.006); composite proof viewed (chrone00 + head29); residual 0.080 head-joint float + dark neck band (fragmentary neck decls); raw-Hie attach-parent index unknown.
- ID: chrone viewed 00–20; tentatives stand (pkg02→Kokoro strengthened); 7 anchorless heads (pkg05,06,23,24,27,28,32).
- Anm: census complete (27,392 records; container round-trips byte-exact; bit-layout + record→stream mapping missing); `phase9/tools/FindAnmReader.java` ready-to-run; `phase9/ANM-READER.md` documents route + secondary bit-unpack route.
- Binding: proven set exactly 3 (pkg00 decl1→tex30, decl12→tex40, decl30→tex40); draw-order REJECTED (phase 8), UV-scoring gate-failed (phase 9); next = shader-class cross-tab (needs pkg00 item-record re-parse) + XEX material setup.
- Canon Q1–Q6 stay OWNER-pending.

## Jobs (in order)
- JOB 1 — ANM READER → PARSER → FIRST CLIPS (G4): run FindAnmReader.java; trace anm.afs reader via CRI file-open path; extract 16B head records' bit-level layout + record→stream mapping. PROOF: parser round-trips head byte-exact AND maps records to body streams consistently (float regions 0x06B000–0x16B000, 0x2AF000–EOF; 8-float groups @0x2B0000 lead). Then first clips on owning character's phase-6 skeleton (≥3 frames rendered + viewed), game clip format (WH PR #425 pattern), batch identically-parsing streams. Fallbacks: ANM-READER.md secondary bit-unpack; else full evidence + exact unknown.
- JOB 2 — ID COMPLETION: chrone 21–28; chrtwo remaining body packages; chrthree 50 (per-AFS GLBs from release doa4-phase6-models-20261021 via phase8/tools/extract_span.py; small batches); VIEW each; extend ID table (phase9 format). Solo-render unviewed head families; attack 7 anchorless heads (TX2D color schemes, costume-slot adjacency, Hie node counts). Re-grade tentatives ONLY on new evidence.
- JOB 3 — HEAD ATTACHMENT DONE PROPERLY: find raw-Hie attach-parent node index (head packages' own Hie / phase-3 assembly graph); kill or explain 0.080 float + neck band. Deliverable: headed composite GLBs for every anchor-proven body↔head pair (per-character isolation), each with viewed front render. Unproven pairs stay separate + listed.
- JOB 4 — BINDING NEXT TESTS: (a) shader-class cross-tab (re-parse chrone pkg00 item records; rule must reproduce all 3 proven before claiming more); (b) XEX material-setup via Ghidra. Success = documented rule + full textured pkg00 front render VIEWED (textures baked).

## Gates
- G4 = Job 1. G6 = Jobs 2–3 + owner canon Q1–Q6 pending.

## Discipline
Additions-only; commit SPECIFIC paths (NEVER git add -A); own-eyes on every render; unique filenames; sanitize GLBs with phase9 glb_sanitize.py before Blender import; Blender Cycles via phase8/tools/render_front_c2.py pattern under `xvfb-run -a env -u PYTHONPATH` (Workbench crashes); never delete game files or release assets; clear only own verified intermediates, log clears; push every turn; land after every sub-result.

## Log
- 2026-10-22 lane start: phase-9 PR #487 verified OPEN (base teardown/doa4-phase8-id-anm); JDK verified + Ghidra smoke exit 0 (above); branch created; this state file landed first.
