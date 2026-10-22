# DOA4 Phase 10 — Job 4: binding next tests

Gate (unchanged): any new rule must reproduce ALL 3 proven chrone-pkg00 assignments (decl1→tex30, decl12→tex40, decl30→tex40) before claiming more.

## Test (a) shader-class cross-tab — EXECUTED (`phase10/tools/shader_crosstab.py` + corrected join)
Re-parsed chrone pkg00's 150 ObjGeo item records and 68 GeoDecls from the raw package bytes (phase-4 bins + phase-3 graph). Join discovery: a decl's index count (rec +0xC) equals the SUM of its object's item index counts grouped by item stream field (+0x18) — each decl is exactly one stream group of its object (68/68 decls matched, 0 unmatched). Item shader class (+0x030) is uniform within each group:
- decl1 → class 52 (stream group 3); decl12 → class 32 (group 2); decl30 → class 32 (group 2).
- Class census over decls: class 32 = 29 decls, class 52 = 22, class 7 + class 2 = the rest (item census: 32×82, 52×52, 7×14, 2×2 of 150 items).
Cross-tab vs proven: class 32 → tex40 (both proven class-32 decls), class 52 → tex30 (the one proven class-52 decl). **The partition is CONSISTENT with all 3 proven assignments — but it is not a binding rule:** 4 classes cannot select among 42 textures, and within class 32 the phase-6 UV top-1 is tex9 for 22 decls (tex40 for only 5) while both proven class-32 decls take tex40 — class + UV-top1 would misassign the proven decls themselves. Verdict: shader class is a stream/format partition, recorded as a constraint (any future rule must respect it), **no new assignments claimed, no textured render earned**.

## Test (b) XEX material setup — route opened, not completed
The Ghidra route is unblocked (see ANM-READER2.md): the XEX file table and its data-side descriptor pointers are located, but code xrefs are absent from the reference manager (PPC computed addressing), so the material-setup function was not isolated this phase. Same next step as Job 1: PPC lis/addi constant scan.

## Binding state at end of phase 10
Proven assignments remain exactly 3 (all chrone pkg00). Rejected/failed so far: draw-order (p8), UV scoring v1/v2 (p9), shader-class as a selector (p10, consistent-but-underdetermined). Next decisive route: XEX material-setup trace via PPC constant scan, or per-decl viewed candidate renders for the statistically decisive UV rows (phase-8 test 3) with the class constraint applied.
