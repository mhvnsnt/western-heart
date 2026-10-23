# DOA4 Phase 12 — Job 3: BINDING, draw-path material setup — hunt closed empty; verdict DYNAMIC-ONLY (terminal)

The one remaining named route after phases 7–11: the XEX draw-path
material setup — code that binds a GeoDecl/item stream to a
sampler/texture at draw time. This phase ran that one targeted hunt.
**It closes empty. No candidate rule was found, so the
test-against-the-3-proven gate is vacuous (there is nothing to
test), and per the job's terms the binding question lands as
DYNAMIC-ONLY, below.** Refuted routes were NOT re-run (UV scoring
phase 9, draw order phase 8, cross-tab alone phase 10).

## The hunt (all raw-byte / Capstone, true frame — see ANM-READER5 §0)

1. **Descriptor-type dispatch scan.** TX2D descriptors carry type
   0x30001 in their 20B descriptor (phase 4). A static decl→texture
   rule needs code that dispatches on that type. Scan of all of
   .text for lis/ori materializations of the descriptor type
   constants: **0x30001 (TX2D) — ZERO hits**; 0x10001 (VBUF) — 4
   hits; 0x20001 (IBUF) — 3 hits (all small leaf helpers, e.g. the
   3-instruction bit-extract at true VA 0x82742400 — none is a
   descriptor walk and none references a decl, an item, or a
   sampler). Tool: `phase12/tools/scan_ring_writers.py` (scan B).
   No native code path switches on the TX2D descriptor type as an
   immediate — TX2D descriptors are consumed wholesale by the
   XPR2/GPU-image registration layer, not dispatched per-mesh.
2. **XPR2 registry family (phase-4 anchor).** The bundle validator +
   handle builder over the package-registry table (30 slots × 8B;
   `XPR2` magic built at fileoff 0x3A793C, true VA 0x823A793C) and
   its neighbouring range-table walk (stride-0xC entries, bounds
   checks only) register whole packages. No per-decl or per-item
   index participates anywhere in the family — there is no slot in
   which a decl→texture rule could be expressed.
3. **The anm/loader command family (phases 11–12).** The translator,
   emitter, ring writers and finalize handoff (ANM-READER5 §§1–3)
   touch no shader, sampler, or texture state — the last unexamined
   code family from the phase-11 scan is now read and negative.

## Verdict — BINDING IS DYNAMIC-ONLY (terminal, documented)

Across phases 7, 11 and 12, every code family that could carry a
static decl→texture rule has been read or scanned and is negative:
XEX strings/samplers (phase 7), package/sub-package records
(phase 7), the file-table/reader family (phase 11), the command
translator family (phase 12), and the descriptor-type dispatch +
XPR2 registration layer (this hunt). Combined with the data-side
exhaustion (decl = one item stream group, 68/68, classes 52/32/32
underdetermined; ObjGeo item fields carry no validated texture
index — phases 4/6/7), the remaining explanation is the one the
evidence has pointed at since phase 7: **textures are bound at
runtime by the render loop — sampler state set per draw from the
package's descriptor stream and the item's shader class (+0x030) —
a dynamic, data-driven-at-draw-time binding with no static
decl→texture table in the XEX or the package records.**

Consequences, stated plainly:
- The 3 proven assignments stand as the only static facts
  (chrone pkg00: obj0_decl1→tex30; obj9_decl12 + obj23_decl30→tex40)
  and were proven by render/alpha evidence, not by a rule — no rule
  exists to reproduce them with, which is itself consistent with
  the dynamic verdict.
- Further static-binding hunts are CLOSED. Any future texturing
  work must go through the phase-6 pkg00 method (render candidate
  assignments per shader class and judge coherence, package by
  package) or through dynamic capture — not through another table
  hunt.
- Wiring blocker #2 in `phase7/WIRING-INVENTORY.md` is updated to
  carry this verdict.
