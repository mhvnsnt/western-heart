# DOA4 Phase 9 — STATE — OPEN 2026-10-21

Branch: `teardown/doa4-phase9-heads-anm` (stacked on `teardown/doa4-phase8-id-anm`, PR #470 head fc5d0d7, itself stacked on PR #466).
Clone: ~/workspace/_doa4p8-clone (sparse, teardown/dead-or-alive-4 only). Scratch: ~/workspace/_doa4p2-scratch/ (PHASE8-STATE.md = phase-8 results; p8/ ~210MB retained: chrone release zips + extracted GLBs).

## Inherited verified facts (phase 8, do not re-derive)
- Anm head census done: 27,392 records; +8 global distinct = 135; ch4/ch5 quantized pair on (v+1)%32 grid; records NOT frame-sequential; container round-trips byte-exact; bit-layout + record→stream mapping still missing.
- Draw-order/sampler-slot texture-binding hypothesis REJECTED (phase8/BINDING-TEST.md names next tests: 1 shader-class cross-tab, 2 XEX material setup, 3 per-decl UV scoring).
- Chrone ID pass partial: renders viewed pkg00–08+10; stats for all 30; costume groups A {00,01,05}, B {03,04}, C {06,07,08+09}; pkg29 non-character strong; tentative: pkg02→Kokoro, group C→Ryu Hayabusa vs Hayate, pkg10→Leifang vs Helena.
- Tooling: phase8/tools/render_front_c2.py (Cycles; Workbench CRASHES here — libEGL), phase8/tools/extract_span.py (spanned release zips).
- Chrone GLBs extracted at ~/workspace/_doa4p2-scratch/p8/glb-chrone/extracted/.
- GLB source: release doa4-phase6-models-20261021 (148 packages / 8,241 meshes, bind error 0.000000).
- Ghidra project: ~/workspace/ghidra-projects/doa4/ (DOA4.gpr verified present).
- Tar member map (release doa4-mirror): chrone @1212324864, chrtwo @1578419712, chrthree @2135433728, anm @2898390016.
- Canon Q1–Q6 stay OWNER-pending — never answered by this lane.

## Jobs (in order)
- JOB 1 — HEAD/HAIR GEOMETRY HUNT (gates everything): (a) re-audit phase-6 assembly for dropped geometry classes; (b) census containers for head-sized packages (chr AFS members not in the 148, the 25 chrthree texture-only packages, mot/stg); (c) map head-package ↔ body-package with evidence. PROOF: one package rendered WITH head, front, VIEWED, attached per game's own skeleton (Hie hierarchy, per-character isolation, no hand-placed heads) — or proof heads are in the same pools and the skinned export truncated them, naming the exact fix.
- JOB 2 — ID PASS COMPLETION: renders chrone pkg09, 11–29, then chrtwo 68, then chrthree 50 (phase-8 tooling, VIEW each); ID table in phase9 extending phase8 format; re-grade phase-8 tentative rows against headed renders. NEVER invent a name. Land per AFS batch.
- JOB 3 — XEX ANM READER → CLIPS (Gate G4): Ghidra file-open path (CRI/filename strings; format RE, keystream DISPROVEN phase 7). Extract bit-level field layout + record→stream mapping for 16B head records. PROOF: parser round-trips head byte-exact AND maps records to body streams consistent with region map (float regions 0x06B000–0x16B000, 0x2AF000–EOF; 8-float groups @0x2B0000 lead). If index yields: first clips on owning character's phase-6 skeleton (≥3 frames rendered + viewed), game clip format (WH PR #425 pattern). If not: full evidence + exact missing piece.
- JOB 4 — BINDING NEXT TESTS: run tests named in phase8/BINDING-TEST.md; any new rule must reproduce ALL 3 proven pkg00 assignments (obj0_decl1→tex30; obj9_decl12→tex40; obj23_decl30→tex40); success = full textured pkg00 front render (viewed, textures baked) + documented rule.

## Gates
- G4 = Job 3. G6 = Jobs 1–2 + owner canon Q1–Q6 pending.

## Discipline
Additions-only; commit SPECIFIC paths (never git add -A); own-eyes on every render; never delete game files or release assets; disk ~99% full at lane start — pull GLBs per-AFS, clear only own verified-mirrored intermediates, log clears to ~/workspace/agent-ops/disk-cleanup-log.md; push every turn; land after every sub-result.

## Log
- 2026-10-21 lane start: phase-8 branch/PR #470 verified (head fc5d0d7); branch teardown/doa4-phase9-heads-anm created from it; this state file landed first.
