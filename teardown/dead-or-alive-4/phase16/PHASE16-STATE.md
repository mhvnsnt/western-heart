# DOA4 Phase 16 — STATE — OPEN 2026-10-22 (.mot expansion grammar + w21 expansion trace + containment scatter-pass completion)

Branch: `teardown/doa4-phase16-mot-grammar` (stacked on `teardown/doa4-phase15-containment-mot`, PR #597 head `7001b3b32e82fd80451818d8ecbfc1a5ffb7be14`).
Clone: `~/workspace/_doa4p16-clone` (sparse, teardown/dead-or-alive-4 only).
Scratch: `~/workspace/_doa4p16-scratch/` (lane-local; cleared at lane end per one-store rule, logged). NOTE: /tmp on this VM is a 512 MB tmpfs — the clone was moved off /tmp at lane start for that reason.
Repo path: `teardown/dead-or-alive-4/phase16/`. Wiring inventory: `teardown/dead-or-alive-4/phase7/WIRING-INVENTORY.md`. Final state: `teardown/dead-or-alive-4/phase13/DOA4-FINAL-STATE.md` (additive addendum only).

## ENVIRONMENT (proven — do not re-derive)
- JAVA_HOME=/home/hatch/workspace/tools/ghidra/jdk-21.0.12.1+1 (NOT on PATH); Ghidra: ~/workspace/tools/ghidra/ghidra_12.1.4_PUBLIC. VM RAM low — capped-heap/targeted passes only; Capstone acceptable.
- TRUE XEX VA BASE = 0x82000000. RAW CAPSTONE is the primary XEX disassembler.
- Blender: `xvfb-run -a env -u PYTHONPATH ~/workspace/tools/blender/blender-4.0.2-linux-x64/blender`, Cycles CPU; unique filenames.
- ISO CLOSED: release `doa4-iso-v1`; whole-ISO sha256 `4423cd5ca0979e38b48fce3dbdd78de6416abfd4dd01fc8cc9140e2c92b104aa` is the re-assembly check value. Local ISO cleared in phase 15 — re-assemble with the phase-13/15 assembler under per-part digest discipline when a job needs ISO bytes, verify the whole-ISO hash, clear again at lane end + log it.
- mot.afs 197 entries extracted + released: release `doa4-mot-20261022`, `mot_entries.tar` sha256 `026592a07c0c6c93c292d9d8f8dc0f732f0e690420f9f6c1dbc4fdc8fc04221c` (API-verified at lane start: size 75,325,440 B, digest matches); per-file manifest in `phase15/mot-entries-manifest.json`.
- default.xex in release `doa4-iso-extracts-20261022`; retail sha256 `56b68dec68991f007639d796b04cb88c9aa7b484c1fce54641cdda5de4f2b98f`; PE form at `teardown/dead-or-alive-4/workdir/default_pe.bin` (in-repo path reference; bytes re-fetched from the release for this lane).
- Mirror streams from release `doa4-mirror-20261017` (phase-15 fetch/part tooling).

## INHERITED TRUTH (phases 13–15 — do not re-derive)
- 24 fighter .bin definitions: PROVEN 32-pointer section table; w21 = 1024-entry clip command table of u16 token scripts (opcodes table-driven, not compare-driven — 15 dispatch sites on runtime records; classifier VA 0x82408290, dispatcher VA 0x824F388C).
- .mot grammar at the RECORD layer: table A (1000 plain / 1004 m_ / 400 c_ slots by class), a 44-entry record descriptor before each record, packed non-f32 payloads; t_* files use a simpler (id, offset) format.
- zack.bin w21 (1024 entries / 584 distinct targets) and zack.mot (1000 slots / 376 distinct) are PROVEN different index spaces — no slot mapping may be claimed between them.
- .mot registry in real default.xex data: 196 records x 0x6C @ VA 0x82C69A70, name char* at +0x18; loader resolves .mot by runtime index -> record -> name.
- Phase-6 skeletons/GLBs: bind reproduction 0.000000 (the clip targets). Heads FINAL (23/31 composites), TX2D binding DYNAMIC-ONLY terminal — do NOT reopen.

## JOBS
1. .mot PACKED-ENCODING EXPANSION GRAMMAR (phase-15 blocker #1): (a) expand ONE SMALL t_* file first; (b) correlate sub-block byte length vs key count across plain/m_ pairs (zack vs m_zack vs c_zack; 44-entry descriptor is the map); (c) identify the expansion rule — PROVEN only when it expands >=2 files from different classes to value streams that are (i) internally plausible AND (ii) consistent between a plain file and its m_/c_ counterpart for the same motion; (d) if proven: assemble the FIRST CLIP (zack; track assignment via .bin side, count-correlated maps LABELED as such), clip JSON + VIEWED posed render with honest body-integrity gate. If it resists: full correlation evidence + exact residual, no guessed expansions.
2. w21 TOKEN->RUNTIME-RECORD EXPANSION TRACE (blocker #2): trace FORWARD from the .bin loader cluster at VA 0x823FA430 in default.xex: how .bin sections (esp. w21 + w31 J token stream, 0x22xx namespace) become runtime records and reach classifier 0x82408290 / dispatcher 0x824F388C. Deliverable: expansion mechanism EVIDENCED at function level (which function reads w21 offsets, record layout field offsets/sizes, token runtime-record layout) — enough for an offline expander, or the exact frontier (function VA + missing evidence). Feed proven results into Job 1 if timing allows.
3. CONTAINMENT SCATTER-PASS COMPLETION (phase-15 deviation #dev-1/2): full piecewise reconstruction with phase-15 tools (extend where needed) for chrthree's 66 scattered + 41 unresolved entries and chrtwo's 38 piecewise-unresolved + 2 absent entries: per entry, mirror-stream piece map (ordered piece list: mirror offset+length per piece, coverage %) or proof of absence (whole-stream search incl. piece probes at multiple sizes). jan02.tpr absence re-verified in the same pass. Deliverable: CONTAINMENT-AUDIT-2.md + updated machine-readable map (additive; phase-15 verdicts superseded per-entry ONLY where the scatter pass changes them, each change logged). Needs ISO bytes: re-assemble under the discipline above; mirror streams from release doa4-mirror-20261017 via phase-15 tooling; clear both at lane end, logged.
4. CLOSEOUT: WIRING-INVENTORY phase-16 section + DOA4-FINAL-STATE.md additive phase-16 addendum (append/pointer only) + this state file final.

## DISCIPLINE
Additions-only in git; NO `git add -A` (pathspec commits); commit+push after EVERY job step; own-eyes on every render; unique filenames; per-character isolation (zack's data touches zack's skeleton only); never delete repo content; local clears only per one-store rule + logged to ~/workspace/agent-ops/disk-cleanup-log.md; NO hand-tooling where a system exists (grammar/trace work is format research — bespoke analysis code is the system here, following phase-15 precedent of banked tools).

## LOG
- 2026-10-22 PR #697 opened (base `teardown/doa4-phase15-containment-mot`). Clone moved from /tmp (512 MB tmpfs, 92% full) to ~/workspace/_doa4p16-clone; scratch at ~/workspace/_doa4p16-scratch/.
- 2026-10-22 lane start: read phase15/PHASE15-STATE.md + phase15/CONTAINMENT-AUDIT.md + phase15/MOT-CENSUS.md + phase15/XEX-HUNT.md + phase14/ANM-DECODE.md. PR #597 verified via gh: head `teardown/doa4-phase15-containment-mot` @ 7001b3b32e82fd80451818d8ecbfc1a5ffb7be14, OPEN. Branch `teardown/doa4-phase16-mot-grammar` created off that head (sparse checkout, teardown/dead-or-alive-4 only). Release `doa4-mot-20261022` verified via gh API: mot_entries.tar 75,325,440 B, sha256 026592a07c...21c. This state file is the first commit.
