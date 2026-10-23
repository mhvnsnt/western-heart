# DOA4 Phase 12 — STATE — OPEN 2026-10-22

Branch: `teardown/doa4-phase12-anm-handlers` (stacked on `teardown/doa4-phase11-anm-ppcscan`, PR #525 head `ef53ffc`).
Clone: ~/workspace/_doa4p8-clone (sparse, teardown/dead-or-alive-4 only; retargeted from phase 11).
Scratch: ~/workspace/_doa4p2-scratch/ (p12/ new; p10/p11 retained).
Repo path note: the task brief says `teardown/doa4/`; the repo's actual path is `teardown/dead-or-alive-4/` (phases 6–11 all live there). Phase 12 follows the repo layout: `teardown/dead-or-alive-4/phase12/`. Wiring inventory lives at `teardown/dead-or-alive-4/phase7/WIRING-INVENTORY.md` (updated in place, Job 4).

## ENVIRONMENT (proven — do not re-derive)
- JAVA_HOME=/home/hatch/workspace/tools/ghidra/jdk-21.0.12.1+1 (NOT on PATH); Ghidra headless needs `-process default_pe.bin`.
- TRUE XEX VA BASE = 0x82000000. For ANM code, RAW CAPSTONE is the primary disassembler (Ghidra function boundaries fail on this code — phase 11).
- Blender: `xvfb-run -a env -u PYTHONPATH ~/workspace/tools/blender/blender-4.0.2-linux-x64/blender`, Cycles CPU; `glb_sanitize.py` on raw phase-6 GLBs.
- Disk: ~87% / ~13G free at lane start. One-package-at-a-time pulls from release `doa4-phase6-models-20261021`, clear each pulled copy after its render commits, log clears here. NEVER delete anything that exists only locally.

## INHERITED TRUTH (phases 6–11, verified — do not re-derive)
- Assembly+skinning solved (148 packages / 8,241 meshes, release doa4-phase6-models-20261021; bind reproduction 0.000000). TX2D solved; only 3 proven texture assignments (chrone pkg00: obj0_decl1→tex30; obj9_decl12 + obj23_decl30→tex40).
- HEAD ATTACH SOLVED + COMPOSITES 23/31 distinct; still unpaired with NO proof: heads 05, 06, 23, 24, 26, 27, 28, 32.
- ID: chrone COMPLETE; chrtwo COMPLETE; chrthree = 1/50 (pkg49 rendered phase 11; pkg50 PROVEN NONEXISTENT — release lists exactly pkg00–49). 0 certain names; tentatives stand.
- ANM (ANM-READER4 authoritative): global stream object = 0x833FA3D0. Ring: 32 slots × 24B @+0xBE8/+0xBF0/+0xBF8 {u32 tag, u64, u64}, cursors +0xBE0/+0xBE4, writers store tags 7/8, 358 materializer sites. Records do NOT flow through the ring. Consumer 0x8243DD08 = 16-case TAG TRANSLATOR (jump table @0x8242F5F8; cases 7–10 SHARED; output arrays obj+0x818…+0x858). Stream-build 0x8295F7D0 = SDK handle-opener (0x3E5 sentinel). anm.afs: 27,392 16B records, no AFS magic/container; ch4/ch5 quantized pair.
- BINDING: decl = one item stream group (68/68); classes 52/32/32 underdetermined; UV-scoring + draw-order + cross-tab-alone REFUTED/exhausted; material path NOT in the anm reader family. Remaining named route: XEX DRAW-path material setup.

## JOBS
0. RECONCILIATION: note that ANM-READER4 supersedes READER3 addendum on (a) stream-object address, (b) DD08 characterization; annotate PHASE11-STATE.md's 0x82C3A3D0 mention as corrected. ANNOTATE ONLY.
1. ANM HANDLERS → BIT-LAYOUT → CLIPS (G4): raw-Capstone read of the 12 jump-table handlers at 0x8242F638+; trace payload writers + readers of output arrays +0x818…+0x858. Goal: 16B-record field layout + record→stream mapping → byte-exact parser → first clips. Pull anime_cm.bin from doa4-iso-v1 if absence blocks a step (single file, size+sha256 here, scratch only). If layout resists: handlers + exact residual, no guessed layouts.
2. CHRTHREE ID COMPLETION: pull + front-render (Cycles, sanitized) chrthree pkg00–48 one at a time with logged clears; ID-TABLE rows (tentative-grade discipline). Test the 8 unpaired heads against each body with the PROVEN pairing method (dominant-joint skin-bind Δ); proven → composite GLB + VIEWED seated render; unproven stays unproven.
3. BINDING — DRAW-PATH MATERIAL SETUP: find XEX draw-call setup binding a decl to a sampler/texture; test any candidate rule against the 3 proven assignments FIRST. If empty: negative + DYNAMIC-ONLY terminal verdict. Do not re-run refuted routes.
4. STATE: this file current per job; WIRING-INVENTORY.md updated.

## GATES
- G1 = Job 0 reconciliation landed.
- G2 = Job 1 handlers read landed (handler dumps + verdict in repo).
- G3 = Job 1 parser verdict: bit-layout proven with byte-exact round-trip + clips gated, OR exact residual with no guessed layout.
- G4 = Job 2: chrthree renders committed + viewed + ID rows; head-pairing tests run per body with proof discipline.
- G5 = Job 3: material rule proven against the 3 assignments, OR negative + DYNAMIC-ONLY verdict landed.
- G6 = Jobs 0–3 + owner canon Q1–Q6 pending (Q1–Q6 stay OWNER-pending).

## DISCIPLINE
Additions-only; commit SPECIFIC paths (NEVER git add -A — sparse clone); own-eyes on every render; unique filenames; sanitize before Blender; never delete game files or release assets; clear only own verified rebuildable intermediates, log clears here; push every turn; land after every sub-result. Per-character isolation throughout.

## LOG
- 2026-10-22 lane start: PR #525 verified OPEN (base teardown/doa4-phase10-anm-clips, head teardown/doa4-phase11-anm-ppcscan @ef53ffc); branch `teardown/doa4-phase12-anm-handlers` created off ef53ffc; collision check — `git log` on the new branch shows only the inherited #525 history, no foreign commits; this state file landed first, before job work.
- Clears (this lane, own rebuildable intermediates only, logged per discipline):
  - p12/sanitized/ chrthree pkg00–48 sanitized GLB copies — cleared per batch after each batch's renders were committed + viewed (sources: extracted GLBs + release `doa4-phase6-models-20261021`).
  - p12/chrthree/extracted/ (50 GLBs, 162MB), p12/chrthree/chrthree_full.zip (concatenation), and the two pulled release parts (z01 + zip, 169MB) — cleared after all 49 renders were committed; everything re-pullable from release `doa4-phase6-models-20261021` (asset names + sizes in Job 2 result above).
  - p12/renders12/ scratch render copies — cleared after the final batch committed (all 49 renders are in `phase12/renders/` on this branch).
  - NOT cleared: p12 scripts/logs/JSONs/contact sheets (~11MB provenance), and NOTHING belonging to earlier phases.

## SESSION RESULTS
- JOB 0 (reconciliation) — DONE: `phase12/RECONCILIATION.md` (ANM-READER4 supersedes the READER3 addendum on (a) stream object 0x833FA3D0 with the byte proof quoted, (b) DD08 = 16-case tag translator, raw-byte read); PHASE11-STATE.md annotated in place (annotation appended, original text kept). Additions only.
- JOB 1 (ANM handlers) — DONE as a landed residual (no parser, no clips): FRAME CORRECTION proven (phase-11 .text VAs are +0xE800 PE-frame labels; true VA = 0x82000000 + fileoff; translator true VA 0x8242F508, table inline at +0xF0, case bodies are the translator's own inline blocks). All 13 case bodies read raw: NO shift/mask extraction on payload data anywhere (~1,900 insns); payloads compared (payload0 = key) and copied whole (payload1 = value); emitter 0x8242EFB8 appends fixed-shape output records, parses nothing. Ring-writer census COMPLETE: 4 writers (tags 5, 6, 7, 8), all posting engine-internal scalars; tags 0–4/9–15 have no writer. Verdict: the ring/translator family is a (tag, key, value) command layer — the anm 16B-record consumer is NOT in it; READER4 next-step 1 EXHAUSTED negative. anime_cm.bin NOT pulled (handler verdict reached without it — the job's pull condition not triggered; ISO pull recorded as the standing next step). Doc: `phase12/ANM-READER5.md`; tools: `phase12/tools/dump_handlers_p12.py`, `phase12/tools/scan_ring_writers.py`.
- JOB 3 (binding draw-path) — DONE, verdict DYNAMIC-ONLY (terminal): TX2D type constant 0x30001 materialized NOWHERE in .text (VBUF 4 hits / IBUF 3 hits, all leaf helpers); XPR2 registry family takes no per-decl/per-item index; translator family touches no texture/shader state. No candidate rule found → the reproduce-all-3 test is vacuous. Proven assignments stay exactly 3. Doc: `phase12/BINDING-DRAWPATH.md`.
- JOB 2 (chrthree ID + head pairing) — DONE: release parts pulled ONCE (z01 99,614,720 B + zip 69,543,514 B, byte-exact vs release doa4-phase6-models-20261021; spanned archive extracted via a central-directory parser after stock unzip/python-zipfile both failed on the span offsets — all 50 GLBs size-verified against the directory). Renders: pkg00–48 (49) front Cycles renders, sanitized (all clamp sums 0.000000), ALL VIEWED via labelled contact sheets, committed in 5 batches to `phase12/renders/`; with phase-11 pkg49, chrthree coverage = **50/50 — chrthree ID pass COMPLETE** (all 148 packages now viewed across phases 8–12). Rows: `phase12/ID-TABLE-CHRTHREE.md` (0 certain names; new tentative groups: 22–28 armored family ×7, 39/41/42/43 cat-ear family). HEAD PAIRING: the 8 unpaired heads tested against all 50 chrthree bodies with the PROVEN method (`phase12/tools/pairing_test_p12.py`): pkg26 min Δ = 0.0646, pkg28 min Δ = 0.0962 (proof bar Δ = 0.000) — NO new pairings; origin-bound heads (05, 06, 23, 24, 27, 32) untestable by this method by phase-11 discipline. **Composites stay 23/31.** No composite GLBs built (none proven).
- JOB 4 (state/inventory) — DONE: this file; `phase7/WIRING-INVENTORY.md` phase-12 section (composites 23/31 unchanged, clips still NONE with the READER5 residual, chrthree 50/50, binding DYNAMIC-ONLY).
