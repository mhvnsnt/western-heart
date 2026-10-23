# DOA4 Phase 17 — STATE — OPEN 2026-10-22 (faithful Ghidra project + data-flow attack on the last two G4 items)

Lane: Jobs 1–4. Gates entering phase 17: G1 CLOSED, G2 CLOSED,
G3 at record layer + 70/148 named, G4 OPEN on exactly two items:
(1) the stateful .mot per-item length rule inside sub-block
payloads; (2) the XEX file-side writer (.bin w21 table -> 0x9C
runtime records). Everything else in DOA4 is closed — heads
FINAL, binding terminal, containment complete.

Branch: `teardown/doa4-phase17-ghidra-dataflow` stacked on
`teardown/doa4-phase15-containment-mot` @ `207408fe` (PR #597
head, which carries phases 15+16 via PR #697's merge).
Clone: `~/workspace/_doa4p17/wh` (sparse, teardown/dead-or-alive-4 only).
Scratch: `~/workspace/_doa4p17-scratch/` (lane-local; cleared at
lane end per one-store rule, logged).
Repo path: `teardown/dead-or-alive-4/phase17/`. Wiring inventory:
`teardown/dead-or-alive-4/phase7/WIRING-INVENTORY.md`. Final
state: `teardown/dead-or-alive-4/phase13/DOA4-FINAL-STATE.md`
(additive addendum only).

## ENVIRONMENT (proven — do not re-derive)
- JAVA_HOME=/home/hatch/workspace/tools/ghidra/jdk-21.0.12.1+1 (NOT on PATH); Ghidra 12.1.4: ~/workspace/tools/ghidra/ghidra_12.1.4_PUBLIC. VM RAM low (~1.6 GB free) — capped heap, targeted analysis only; Capstone cross-checks allowed.
- TRUE XEX VA BASE = 0x82000000 (phase 11). PE section map derived this lane from `default_pe.bin`'s own section table (23,068,672 B, sha256 eaa1885a2322df0cf1e8c236a0405a37eeb31b7fdb12b5392a6acc2cabce99d0, header imagebase field = 0x400000 — the base-0/base-wrong import of phase 16 §3b came from loading without correcting this): .rdata RVA 0x400 RAW 0x400 (VA = file + 0x82000000); .text RVA 0x2E0000 RAW 0x2D1800 (VA = file + 0x8200E800); .data RVA 0xB60000 RAW 0xB42200 (VA = file + 0x8201DE00). A uniform image-base shift 0x400000 -> 0x82000000 therefore places every section at its true VA.
- Inputs: default.xex retail sha256 56b68dec68991f007639d796b04cb88c9aa7b484c1fce54641cdda5de4f2b98f (release `doa4-iso-extracts-20261022`); .bin definitions in release `doa4-anime-definition-20261022`; .mot entries in release `doa4-mot-20261022` (mot_entries.tar sha256 026592a07c0c6c93c292d9d8f8dc0f732f0e690420f9f6c1dbc4fdc8fc04221c). Local byte copies surviving from phases 13/14 scratch (zack.bin / zack triple .mot / default_pe.bin) are hash-verified before use; release downloads re-verify the same digests.
- Proven XEX ground (phase 16, do not re-derive): open helper 0x8238ED10 (27 bl sites); loader cluster 0x823918E8–0x82391B2C (reads the loader struct, not a .bin buffer); initializer 0x82406E48 (strides 0x44/0x9C/0x34; 0x34-record id at +0x30); validator 0x824091F0 (bands [0x15,0x1C]/[0x1D,0x24]/[0x25,0x2C]); token decode ~0x823F6D2C over 0x9C records (token u16s at +0x00/+0x02); translator 0x823F6FA0; classifier 0x82408290 (zero direct callers); .mot registry 196 records x 0x6C @ VA 0x82C69A70 (name char* +0x18).
- Proven .mot ground (phase 16): a record = 44 sub-blocks FOLLOWED BY a 44-entry descriptor of u32 BE absolute sub-block offsets in channel order; tiling exact (530 records / 23,320 sub-blocks across zack/m_zack/c_zack/124 t_*); item cadence evidenced (51.65% exact tile under the best simple tag rule over 41,096 blocks) but tag->length as a PURE function is FALSIFIED (constraint propagation); delta-stream decodings refuted vs shuffled controls. The rule is stateful.

## JOBS
1. FAITHFUL PER-SECTION GHIDRA PROJECT: load default.xex's PE form with explicit section mapping at true base 0x82000000. Acceptance (all evidenced here): registry string block (D:\bin\*.bin / *.mot names) resolves xrefs; .mot registry table @ 0x82C69A70 xref'd by the proven loader code; target functions (0x8238ED10, 0x82406E48, 0x824091F0, 0x823F6D2C, 0x823F6FA0, loader cluster) decompile readably at correct VAs. Bank the setup as a reproducible artifact (build script + settings under `phase17/tools/`; project DB to a GitHub release if practical, else script + DB sha256/size manifest with the DB cleared locally per one-store rule — say which). If the faithful project cannot be built in-VM (RAM), land the exact blocker + the derived per-section map, and Jobs 2–3 fall back to Capstone data-flow — state which route each result came from.
2. THE FILE-SIDE WRITER (item 2): from the 0x9C record array base, trace data-flow BACKWARD: who writes token u16s into 0x9C records at +0x00/+0x02, and whose input pointer traces to a .bin file buffer (loops stepping 1024 u32s, or reads at buffer+w21-relative offsets feeding record writes). Deliverable: writer function VA + expansion mechanism at field level; PROVEN when an offline expander reproduces the runtime records for zack (validator bands + record counts/ids + token-decode read pattern). Ship expander under `phase17/tools/` + zack's expanded output (JSON) if proven; else the exact frontier.
3. THE .mot STATEFUL LENGTH RULE (item 1): (a) CODE route — from the .mot registry loader forward to the record-expansion consumer; its per-item loop IS the length rule. (b) DATA route — constraint analysis over the 23,320 sub-blocks with state, rule classes in order: (i) (tag, previous tag), (ii) (tag, running index mod k), (iii) bit-packed items, (iv) f(tag) + per-sub-block header field. PROVEN only at >=99% tiling in BOTH a plain file (zack) and an m_ file at exact boundaries AND plausible keyframe curves. If proven: expander + zack record 0 + one m_zack record expanded; FIRST CLIP only if the .bin side (Job 2) ties channels to joints — else channel-labeled curve JSON + plot (posed render on unproven joint assignment is FORBIDDEN). If neither route proves: stateful-class test results + exact residual + XENIA TRACE SPEC (Job 4 fallback).
4. CLOSEOUT: WIRING-INVENTORY phase-17 section + DOA4-FINAL-STATE.md additive phase-17 addendum (append/pointer only) + this state file final with per-item verdicts. Local clears per one-store rule, logged to ~/workspace/agent-ops/disk-cleanup-log.md.

## DISCIPLINE
Additions-only in git; NO `git add -A` (pathspec commits); commit+push after EVERY job step; per-character isolation (zack's data touches zack's skeleton only); never delete repo content; PR stays OPEN at lane end (merging is the parent's call).

## LOG
- 2026-10-22 lane start: read phase16/W21-TRACE.md (incl. §3b Ghidra base-0 import blocker), phase16/MOT-GRAMMAR.md, phase16/PHASE16-STATE.md, phase14/ANM-DECODE.md. Branch created off 207408fe (verified: that head is PR #697's merge — phases 15+16 both carried). PE section map derived from default_pe.bin's section table (see ENVIRONMENT). This state file is the first commit.
