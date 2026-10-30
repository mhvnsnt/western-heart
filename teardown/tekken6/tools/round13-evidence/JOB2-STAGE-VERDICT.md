# Tekken 6 PSP — ROUND 13 JOB 2: stage geometry batch

Date: 2026-10-22, round 13. Tool: `tools/r13_batches.py stage`.
Inventory: `tools/round13-evidence/r13_stage_inventory.json`
(all 16 packages, every slot enumerated).
Slice twin census: `tools/round13-evidence/r13_stage_slice_manifest.json`.

## Result: 0 stage GLBs from the 16 stage/object packages — and the reason is structural, not a decoder gap

Every one of the 16 stage/object packages (top-76 idx 24, 26, 28, 30,
32, 34, 36, 38, 40, 42, 44, 46, 48, 50, 52, 54) holds exactly six
non-empty slots: 0, 6, 7, 8, 9, 11. The **only NDPP-magic section in
any of them is slot 0 (624 B)** — the transform node proven in rounds
7/10. Running the round-9 decoder on all 16 slot-0 sections fails
identically, 16/16:

```
IndexError: list index out of range   (bad VTYPE 0x11d, units_found = 1)
```

The single "unit" `parse_units` finds at +528 is spurious: its pairs
point at the section's tail words (GE state words 0x14/0x10/0x12…,
USCALE/VSCALE constants 0x483f0081/0x493f0081, then 0x13/0x0B
terminator words and ±32767 bbox-corner records) — there is no
vertex payload. Slot 0's real contents (idx24 dumped in full):
`NDPP` header (+4 = 0x270 = section size, +8 = 0x00010001), two
64-byte transform records at +16 and +80 (floats incl. the 0.7071
quaternion component), GE-state words at +128, two s16 pattern
blocks (+176, +416), a record/index region (+272), and the tail GE
header words at +528. It is a placement/transform node. No arena
geometry is carried in NDPP form in these packages.

The remaining slots (idx24/34/52 sampled in depth, all 16
inventoried):

| slot | size | content |
|---|---|---|
| 6 | 48 B | small fixed record |
| 7 | 2,384 B | shared block, identical head across stages; contains exactly 1 embedded NTPP + 1 GIDX (a shared texture section) |
| 8 | 896–25,088 B | big-endian u32 directory/table (starts 5, 0x30, then increasing offsets) — not NDPP |
| 9 | variable | NTPP texture bundle (idx24: 40 NTPP/40 GIDX; idx34: 31/31; idx52: 102/104; the `NDPP` strings inside idx52's slot 9 are bytes inside NTPP payloads, not standalone sections) |
| 11 | 32 B | `tfm_` transform name (`tfm_cmnglow000_O_OBJ_O_HIR_` in idx24/34/52) |

## The slice twins agree — stage geometry is not in NDPP stage sections anywhere

The round-11 B3 "stage-pattern" class (236 slice packages, the
unassigned set) was batch-attempted with the same decoder
(`stages/slice/`): **235 of 236 fail identically at slot 0** (bad
VTYPE 0x11d — the same transform-node signature). Sampled packages
(bulk 104/106/107) reproduce the top-76 stage layout slot-for-slot,
including identical slot sizes (slot 7 = 2,384 B, slot 8 = 25,088 B,
slot 9 = 67,312 B — the idx34 twin). Exactly **one** stage-class
NDPP section in the entire sweep decodes: bulk 3640 slot 0 — 4
verts / 2 tris, a single flat 2×2 quad (a ground-plane card).
Shipped: `stages/slice/unassigned/bulk3640_slot0_r13.glb`.

## Gate render — VIEWED

`tools/round13-evidence/r13_gate_stage_bulk3640_quad.png`
(Cycles, tilted front view): one flat quad in empty space. It is
not an arena, not a prop cluster — a lone plane card. That is the
complete NDPP-geometry content of the stage package class.

## Verdict

Stage/object packages are **placement + texture containers**:
transform nodes (slot 0), a shared texture (slot 7), a BE directory
(slot 8), per-stage NTPP texture bundles (slot 9), and a transform
name (slot 11). Arena meshes, if the game builds them from data in
this bulk at all, are not stored as NDPP sections in stage
packages — the NDPP geometry of this game lives in the character
and part packages (Jobs 3 / round 9). The textured idx24 variant is
also not shippable: it depends on Job 1's NTPP pixel decode, which
stopped at the descriptor-factory residual (JOB1 verdict).
Residual named: stage geometry source format (slot 8's BE directory
+ slot 9's NTPP bundles are the only undecoded stage-side
structures; any mesh data would have to be referenced from there).
