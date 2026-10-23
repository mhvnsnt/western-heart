# DOA4 Phase 9 — Job 4: binding next tests (follow-up to phase8/BINDING-TEST.md)

Gate (unchanged): any new assignment rule must reproduce ALL 3 proven chrone-pkg00 assignments (obj0_decl1→tex30; obj9_decl12→tex40; obj23_decl30→tex40) before claiming more. Success = full textured pkg00 front render (viewed, textures baked) + the documented rule.

## Test 3 (per-decl UV-evidence scoring, extended) — EXECUTED → GATE FAILED, no claims
Phase 8's test list ordered this third; it was the only one runnable this session (tests 1–2 below). The phase-6 v1 scoring table (`tex_assign.json`, all 68 decls × top candidates) was calibrated against the 3 proven assignments:
- decl12 → tex40: v1 rank 1, score 0.952 vs second 0.714 (ratio 1.33) ✓ consistent.
- decl30 → tex40: v1 rank 1, score 0.947 vs second 0.737 (ratio 1.29) ✓ consistent.
- **decl1 → tex30: v1 rank 3, score 0.146 — the v1 top for decl1 is tex9 (0.452). ✗ INCONSISTENT.** The proven decl1 assignment (from phase 6's viewed candidate renders) is NOT what v1 UV scoring prefers.

Because the scoring fails one of the three proven assignments, it fails the gate: **no new assignment is claimed from it**, and no textured pkg00 render is earned. (For the record, the only decls passing a strict decisiveness cut — top ≥ 0.6 and top/second ≥ 1.35 — are decl13 → tex40 (0.748 vs 0.468) and decl31 → tex40 (0.732 vs 0.467). Both are the s3 partner decls of proven objects obj9/obj23, so tex40 is *consistent* with the proven pattern — recorded as a supporting observation only, NOT an assignment.)
The v2 scoring table (`tex_assign2.json`) saturates at 1.000 for the top-2 candidates on most decls and cannot separate at all — also not claimable.

## Test 1 (shader-class cross-tab) — NOT RUN (data not on disk)
Needs per-decl shader class (item +0x030 ∈ {2,7,32,52}) joined to the UV scores. No parsed item-field table survives on disk (phase-5/6 scratch has segmaps and inventories, not item records); producing it requires re-parsing chrone pkg00's ObjGeo item records from the mirror — a named follow-up, not attempted in this session's remaining timebox.

## Test 2 (XEX material setup) — BLOCKED (same as Job 3)
Needs the Ghidra XEX route; no Java runtime exists on this VM (see `phase9/ANM-READER.md`). Blocked identically.

## Binding state at end of phase 9
Proven assignments remain exactly 3 (all chrone pkg00). Draw-order/sampler-slot: rejected (phase 8). UV scoring v1/v2: gate-failed / non-separating (this phase). Next decisive routes, in order: (1) shader-class cross-tab after an item-record re-parse of pkg00; (2) XEX material-setup trace once a JDK exists.
