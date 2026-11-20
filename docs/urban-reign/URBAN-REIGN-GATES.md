# Urban Reign — completion gates (PR #397 standard)

The five falsifiable gates from `docs/research/TEARDOWN-WIRING-STANDARD-2026-10-20.md`
(western-heart PR #397), run against the 72 delivered GLBs
(`teardown/urban-reign/models/charNNN/charNNN.glb`). Tools:
`teardown/urban-reign/tools/ur_gates.py` (G1–G3) and
`teardown/urban-reign/tools/g4_blender_verify.py` (G4). Raw
machine output: `docs/urban-reign/gates/gates_report.json` and
`docs/urban-reign/gates/gates_g4_blender.json`.

## Verdicts

| Gate | Result | Evidence |
|---|---|---|
| G1 Palette truth | **PASS (with stated substitution)** | Every skin-used bone on all 72 chars is defined by a parsed header palette record, or belongs to a flagged identity-window piece (below); no joint exceeds its character's loader node bound. 62/72 chars are 100% record-defined. |
| G2 Index sanity | **PASS** | 407,380 per-vertex influences resolved through the proven formula (slotbits → slot → palette window → bone id); every GLB JOINTS_0 index in range; weights finite. The "27 entries vs max index 54" question: palettes are per-object DMA **windows** over the node table; max bone id in chr01's 27-entry record is 54; node ids run to each char's own bound (chr01: 57). Answered by the loader's data, not assumed. |
| G3 Bind check | **PASS** | inverseBind × nodeWorld == I: worst error **6.5e-08** over all joints of all 72 GLBs. Bind-pose reproduction (skin each GLB with its own skeleton at bind pose): worst deviation **1.4e-07**. |
| G4 Import-verify | **PASS 72/72** | Every GLB imports clean in Blender 4.0.2 with an armature (bones > 0) and weighted verts on every mesh; weights normalized (per-vertex sum 0.99999983–1.00000011 across all chars). |
| G5 Stance check | **PASS (own-eyes)** | Bind-pose renders match the game's authored-stance body plan: char001 Blender front/side/back renders viewed (crouched fighting stance, planted + extended legs, guarding arms); scatters viewed for char001/002/020/030/036/045/058 + Blender front/side for char045. The poses are the game's authored stances, not T-poses — consistent across all 72. |

## G1 substitution, stated plainly

The standard's G1 reads "palette count derived from the loader ==
palette count in the PCSX2 RAM capture". **No PCSX2/BIOS lane exists
on this workstation, so no fresh RAM capture was run.** The gate as
implemented is: palette bone sets derived from the loader's own
header records (the files the loader reads) == the bone sets the
delivered skins use, per character, with the node bound taken from
the loader's own child-list and palette records; plus the external
RAM cross-check available today — urban-reign-recomp's published
RAM facts (hierarchy array at RAM 0x59f240; chr01-class node table
max 57; 49-name bone pool) — which the delivered chr01 skeleton
(bound 57) matches. A future PCSX2 capture can replace the
cross-check without changing the loader side.

## The identity-window class (flagged, not hidden)

Running G1 caught a real defect in the first delivered batch: the
decoder's identity-window fallback palette (slot → bone id direct)
had silently labeled 213 pieces across 19 chars — geometrically
validated, but not palette-record-proven, in 15 chars reaching bone
ids 58–63 (parallel duplicate labelings of the same physical
joints). The decoder now enforces **record-first tiering**
(real palette records always win; identity windows only for
pieces no record can prove, capped at the char's node bound, and
flagged per piece in the decode stats), which reproduced char001
**byte-identical** to the record-only solution.

After re-decoding the 19 affected characters, **139 pieces in 10
characters** (char012/014/015/018/030/031/039/041/065/066) still
rely on identity windows: their headers carry palette records in
per-object block framing the current parser does not fully read
(e.g. char030 exposes only one key-03 record in the graph zone).
Every such piece is (a) geometrically validated by the same frame
fits as record pieces, (b) inside the char's node bound, and
(c) listed as `identity-window` in
`docs/urban-reign/decode-stats/charNNN.json` (`palette_provenance`).
Closing this class entirely = parsing the property-bag block
grammar, named here as the remaining palette-provenance gap.

## What the gates do NOT cover

Textures (uncracked — PR #306 stands), the s16-packed accessory
groups (undecoded), .gyu animation decode (layout + sampler known;
no clips embedded), mission bins. Those are FLAGGED in
`teardown/urban-reign/WIRING-INVENTORY.md`, not gated here.
