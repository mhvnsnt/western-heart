# DOA4 Phase 10 — Job 3: head attachment via the raw Hie (phase-3 assembly graphs)

## The attach-parent answer (from raw Hie data, not GLB guesswork)
Every package's Hie node record (0x50B: 4×4 local matrix + u16 links @+0x40, parent at links[1]) is preserved in the phase-3 assembly graphs (`assembly-graphs/*_graph.json`, `hie_node.parent` + `world_matrix`). Reading them for heads and bodies:

- **Body side:** each body package has exactly one central head node. Examples (node index, parent, world position): chrone00 = **node 17, parent 2**, world (0, 0.486, −0.021); chrone01 = 19/4; chrone02 = 23/9; chrone06–09 (group C) = 18/4 @ Y 0.525; chrone10 = 25/11 @ 0.478; chrone17 = 19/5 @ 0.468; chrone14–16 = 3/10 @ 0.581. Full per-package table: `phase10/tools/shader_crosstab.py`-style dump in scratch `p10/attach_map.json` (all 148 packages).
- **Head side:** each head package stores **copies of its body family's head node as ROOT nodes (parent = 0xFFFF)** at the EXACT body world position — e.g. chrtwo-pkg29 nodes 1 and 2 both sit at (0, 0.486, −0.021), identical to chrone00's node 17. The head package's own local hierarchy hangs off its node 0 at the origin.
- **So there is no stored cross-package parent integer to find — the game's attach is by node identity:** the head package carries duplicate bind nodes whose world transform equals the body head node's; at load, the two packages' Hie fragments merge on those shared nodes, and the head's local root (node 0) binds at the neck-base row of the merged skeleton. This explains phase 9's positional rule and its 0.080 residual exactly: the head-joint world Y (0.486) is the shared bind node, while the head's local geometry origin sits one neck segment lower — the clavicle row (Y 0.406 in the chrone00 family = head-joint Y − 0.080, the head-node→parent-row distance in the body Hie). The "float" was the distance between the bind node and the geometry origin, not a placement error. The dark neck band remains a source-content gap (fragmentary neck decls in both packages, phase 9) — no placement change removes it.

## Families proven by exact anchor-copy positions (Δ = 0.000 on world position)
- Y 0.486 (z −0.021): heads pkg29, 30, 34, 35–40 → bodies chrone00–05 family (head node world 0.486).
- Y 0.483 (z −0.022) + a second copy pair at 0.478: heads pkg17, 18, 19, 20 → same chrone00-family cluster (Δ0.003 from 0.486, within phase-9 tolerance; the dual copies are the neck + head bind nodes).
- Y 0.478 (z −0.020/−0.024): heads pkg08, 09, 33 → chrone10/13, chrtwo46/49, chrthree01 family.
- Y 0.468 (z −0.025): heads pkg04, 07, 21 → chrone17/18/20/21/22, chrthree18/19 family.
- Y 0.477 (z −0.041): heads pkg25, 41, 42, 43, 44/45 → chrtwo50–55, chrthree02–07 family.
- Y 0.581 (z 0.005): heads pkg10–16 (node 1) → chrone14/15/16 family (their graph head node is at 0.581 — this CORRECTS phase 9's GLB-mean guess that pkg11–16 belonged to the 0.519–0.525 group-C family; the graph root copies also carry 0.478 copies, so this family assignment rests on the unique 0.581 copy).

## Anchorless heads — root cause found for most, pairing still unproven
- pkg05, 06, 22, 31, 32: their anchor-copy roots carry **identity matrices (world = origin)** — position matching is impossible by construction. pkg23: no positioned copies (only hair nodes at (±0.029, 0.132, 0.075)). pkg24, 27: 15-node rigs whose roots are all identity. pkg26: one copy at (0, 0.277, −0.030) — no body family exists at 0.277. pkg28: copies at (0, 0.310, −0.041) — no body family at 0.310. These 9 packages (phase 9's 7 + pkg22 + pkg26 counted here by graph evidence) stay UNPAIRED and are listed, not forced.

## Deliverable: headed composites
20 composite GLBs built with `phase10/tools/batch_composite.py` (body GLB + sanitized head GLB, head roots translated to the family's neck-base anchor (headY − 0.080, headZ), per-character isolation — each composite is one body + one head from its proven family), exported to scratch `p10/composites/` (mirrored by the phase-6 release sources; GLBs are re-buildable from the committed tool + lists), each with a front Cycles render in `phase10/renders/p10-composite-*.png`, viewed by this agent (see PHASE10-STATE session results for the viewed list). Representative body per family: chrone00 (0.486/0.483), chrone10 (0.478), chrone17 (0.468), chrtwo50 (0.477), chrone14 (0.581, head pkg11).
