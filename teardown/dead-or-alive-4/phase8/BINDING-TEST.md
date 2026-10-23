# DOA4 Phase 8 — Job 4: binding next test — draw-order / sampler-slot hypothesis

Setup (chrone pkg00, phase-6 data): 68 GeoDecls, 42 TX2D textures. Decl parse order == decl_id order (decls are stored sequentially: parse order `[0..67]`, so draw position of decl k = k). Proven assignments to reproduce (phase 6, evidence-backed): **decl1→tex30, decl12→tex40, decl30→tex40**.
Tool: `phase8/tools/binding_test.py`; full output: `phase8/BINDING-TEST-OUTPUT.txt`.

## Rules tested
Decl key ∈ {draw position, decl_id, per-object slot index} × texture ordering ∈ {TX2D table order, diffuse-only subsequence (fmt 18/20)} × mapping ∈ {direct index, mod-cycle over the ordering} — plus by-file-offset and by-size texture orderings, which degenerate to table order because the phase-6 TX2D parser does not expose offset/size fields (recorded as a test limitation, not silently dropped).

Direct-index results (want {decl1:30, decl12:40, decl30:40}):
- draw-pos × table: {1:1, 12:12, 30:30} ✗
- draw-pos × diffuse-only: {1:4, 12:17, 30:∅ (out of range)} ✗
- decl-id × table / diffuse-only: identical to draw-pos ✗
- obj-slot × table: {1:1, 12:0, 30:0} ✗
- obj-slot × diffuse-only: {1:4, 12:2, 30:2} ✗
- All mod-cycle variants: no combination reproduces all three either (script checks every combination; result line: `RULES REPRODUCING ALL 3: NONE`).

## Verdict
**Hypothesis REJECTED.** No draw-order or sampler-slot positional rule reproduces the three proven assignments. This is structurally expected in hindsight: decl12 and decl30 share tex40 while sitting at different draw positions AND different objects, and decl1 (draw position 1) takes tex30 — no positional function of draw order, decl id, or per-object slot produces that pattern under any tested texture ordering. Per the job's success gate, NO new assignment is claimed and no textured pkg00 render is earned by this test (the phase-6 textured render with the 3 proven assignments stands as-is).

## Where the binding most likely lives (next tests, in order)
1. The shader-class field censused in phase 5/6 (item +0x030 ∈ {2,7,32,52}) cross-tabulated against the UV-evidence assignment scores for ALL decls — if shader class partitions decls into texture families, the mapping may be class→texture-set with a per-class sub-index.
2. XEX-side material setup: the phase-7 binding hunt covered XEX strings only; the sampler/texture index may be set from a per-object data table in the XEX data section (same Ghidra route as the anm reader).
3. Per-decl UV-evidence scoring (phase-6 method) extended from the 3 proven decls to all 68, accepting only assignments whose top score separates decisively (as tex40's 0.95 vs 0.71 did) — statistical, so each accepted row needs its own viewed candidate render before it counts as proven.
