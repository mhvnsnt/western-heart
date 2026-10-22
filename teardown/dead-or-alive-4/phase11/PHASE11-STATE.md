# DOA4 Phase 11 — STATE — OPEN 2026-10-22

Branch: `teardown/doa4-phase11-anm-ppcscan` (stacked on `teardown/doa4-phase10-anm-clips`, PR #509 head `0cd07c8`).
Clone: ~/workspace/_doa4p8-clone (sparse, teardown/dead-or-alive-4 only; retargeted from phase 10).
Scratch: ~/workspace/_doa4p2-scratch/ (p11/ new; p8/p9/p10 retained — p10 = 89MB with the 20 composites + Ghidra logs).
Repo path note: the task brief says `teardown/doa4/`; the repo's actual path is `teardown/dead-or-alive-4/` (phases 6–10 all live there). Phase 11 follows the repo layout: `teardown/dead-or-alive-4/phase11/`. Wiring inventory lives at `teardown/dead-or-alive-4/phase7/WIRING-INVENTORY.md` (updated in place, Job 5).

## ENVIRONMENT (proven phase 10 — do not re-derive)
- JAVA_HOME=/home/hatch/workspace/tools/ghidra/jdk-21.0.12.1+1 (Temurin 21.0.12.1; NOT on PATH); Ghidra headless needs `-process default_pe.bin` (omitting it = null currentProgram).
- Blender: `xvfb-run -a env -u PYTHONPATH ~/workspace/tools/blender/blender-4.0.2-linux-x64/blender`, Cycles CPU; sanitize raw phase-6 GLBs with phase-9 `glb_sanitize.py` first (weight-0 sentinel crashes Blender's importer).
- Disk VERY tight (~98% used, ~2.5GB avail at lane start): pull ONE package at a time from release `doa4-phase6-models-20261021`, render, clear the pulled local copy once its render is committed (rebuildable intermediates only — log clears here; NEVER delete anything that exists only locally).
- Local asset cache found at lane start (no pull needed for these): ALL chrtwo GLBs 00–67 already extracted in scratch `p9/glb-chrtwo/extracted/`; chrone 00–29 in `p8/glb-chrone/extracted/`; sanitized heads (20) + composites (20) in `p10/`. chrthree GLBs are NOT on disk (spanned zips not pulled).

## INHERITED TRUTH (phases 6–10, verified — do not re-derive)
- Assembly + skinning SOLVED: 148 packages / 8,241 meshes (release doa4-phase6-models-20261021); bind reproduction from GLB = 0.000000 max error. TX2D solved; only 3 evidence-backed texture assignments (chrone pkg00: obj0_decl1→tex30; obj9_decl12 + obj23_decl30→tex40).
- ANM (phase 10, PR #509): anm.afs has NO AFS magic/container; 27,392 16B records; 135 distinct u32 values (hi u16: 22 distinct, lo u16: 21); ch4/ch5 = quantized pair on a (v+1)%32 grid. XEX file table @0x61E940 (d:\anm.afs, d:-only) with 5 data-side descriptor pointers, but ZERO CODE XREFS (PPC computed addressing) — xref hunting EXHAUSTED. Bit-unpack guessing (widths 9–13) ≈ chance. Docs: `phase10/ANM-READER2.md`; hunt scripts FindAnmReader2/3/4.java on the #509 branch.
- HEAD ATTACH (phase 10): attach is BY NODE IDENTITY — head packages store copies of the body head node as root nodes at the exact body world position; per-package head-node index+parent tabled for all 148 packages (scratch p10/attach_map.json). 20 composites built: 11 seated, 7 FLOAT (heads 09, 18, 19, 20, 21, 25, 33 — bind-node-local origin sub-population), 1 marginal (07), 1 rendered-not-viewed (43). 9 heads unpaired (identity-matrix anchor copies / off-family copies).
- ID: chrone COMPLETE (pkg23–26 = cord-loop family, one fighter × 4 costumes); chrtwo bodies viewed 00–03 + 46–49 (pkg46 bearded face); tentatives unchanged (pkg02→Kokoro; group C Hayabusa-vs-Hayate; pkg10 Leifang-vs-Helena); 0 certain names. Remaining: chrtwo 50–67, chrthree pkg50, 10 distinct heads never rendered (05, 06, 10, 22, 23, 26, 27, 28, 31, 32).
- BINDING: decl = one item stream group (68/68); classes decl1=52 / decl12=32 / decl30=32 — consistent with the 3 proven but underdetermined; UV-scoring refuted (phase 9); draw-order refuted (phase 8). XEX material route = the remaining route.

## JOBS
1. PPC CONSTANT SCAN → ANM READER (G4): Ghidra script (or Capstone pass) scanning PPC lis/addi (+lis/ori) PAIRS materializing (a) file-table address 0x61E940 + neighbors, (b) the 5 known anm descriptor pointer targets, (c) anm.afs-related data addresses from phase-10 docs. Every containing function = reader-family candidate → targeted decompile → hunt shift/mask network unpacking the 16B records (field widths + record→stream mapping). THEN byte-exact parser (structural round-trip first), decode first clips onto a phase-6 skinned GLB skeleton, gate: joint-distance invariant + viewed posed render vs bind pose. If scan yields candidates but reader resists: land candidate list + decompiles + exact residual. NO guessed bit layouts.
2. HEAD-ORIGIN RESEAT: per-head skin-weight read for the 7 floaters + marginal (heads 09, 18, 19, 20, 21, 25, 33 + 07): read each head GLB's skin weights + joint palettes → decide origin convention (bind-node-local vs body-world) → apply → rebuild composites → gate EVERY rebuilt composite with a VIEWED front render (seated = head sits on neck, no visible float/gap beyond the known fragmentary-neck-decl band). Then extend: composites for every remaining DISTINCT head with a proven body pairing from the 148-package table that phase 10 didn't build, same gate. The 9 unpaired heads stay unpaired unless the weight read produces a PROVEN pairing (state the proof).
3. ID REMAINDER: pull + render (front, Cycles, sanitized) chrtwo bodies 50–67, chrthree pkg50, and the 10 never-rendered distinct heads; ID-table rows, same discipline (tentatives labeled, NO certain names without name-grade evidence). One-at-a-time pulls; clear each pulled copy after its render commits. (Local-cache note: chrtwo bodies + heads are already extracted in scratch p9 — use them, no release pull needed; chrthree pkg50 still needs a pull.)
4. BINDING (material route): IF Job 1's scan exposes the material-setup code path, read it for the decl→texture rule, test against the 3 proven assignments FIRST (must reproduce all 3 exactly); only then assign further decls, each with evidence. If not exposed: short negative note. Do NOT re-run refuted routes (UV scoring, draw order, cross-tab alone).
5. STATE: this file current per job; update `teardown/dead-or-alive-4/phase7/WIRING-INVENTORY.md` (composites count, clips if any, ID coverage).

## GATES
- G1 = Job 1 scan landed (candidate functions + decompiles in repo, whatever the reader verdict).
- G2 = Job 1 parser verdict: bit-layout proven with byte-exact round-trip + clips gated, OR exact residual stated with no guessed layout.
- G3 = Job 2: every floater/marginal reseated per its weight-read convention + viewed render; extension composites built + viewed.
- G4 = Job 3: all remainder renders committed + viewed + ID rows landed.
- G5 = Job 4: material rule proven against the 3 assignments, OR negative note landed.
- G6 = Jobs 2–3 + owner canon Q1–Q6 pending (Q1–Q6 stay OWNER-pending).

## DISCIPLINE
Additions-only; commit SPECIFIC paths (NEVER git add -A — sparse clone); own-eyes on every render; unique filenames; sanitize before Blender; never delete game files or release assets; clear only own verified rebuildable intermediates, log clears here; push every turn; land after every sub-result. Per-character isolation: composites/clips live with their own package's identity only.

## LOG
- 2026-10-22 lane start: PR #509 verified OPEN (base teardown/doa4-phase9-heads-anm, head teardown/doa4-phase10-anm-clips @0cd07c8); branch created off that head; this state file landed first, before job work.
- Clears: none yet.

## SESSION RESULTS
(to be filled per job as results land)
