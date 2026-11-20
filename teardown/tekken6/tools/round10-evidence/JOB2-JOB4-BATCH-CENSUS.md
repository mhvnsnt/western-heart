# Tekken 6 PSP — ROUND 10 JOB 2 (full-section batch) + JOB 4 (B3 census)

Date: 2026-10-22, round 10. Tool: `tools/r10_batch.py`.
Data: `tools/round10-evidence/r10_inventory.json` (top-76,
full slot maps) + `tools/round10-evidence/r10_b3_census.json`
(entry-87 slice, from round-7 census slot maps).

## JOB 2 — the full-section batch is COMPLETE (and smaller than feared)

Full slot enumeration of all 12 character packages proves
each holds exactly TWO nonzero NDPP sections — slot 0 (head)
and slot 10 (body) — plus BONE slot 1 (body skeleton), BONE
slot 12 (head skeleton, 1,664 B / 22 bones in 12/12), the
48 B slot-6 table, and a slot-11 name chunk (`kao_…` /
`MODEL_…`). Slots 2–5 and 7–9 are zero-size in 12/12 (idx04
additionally carries a 1,904 B float chunk in slot 2). There
are no further costume/item NDPP sections inside the
character packages — costume parts live in the slice's
separate A-packages (Job 4), per-character isolation kept.

All 24 sections were re-decoded this round with the round-9
decoder (counts in the inventory JSON; e.g. idx00 slot0 =
3,217 verts / 1,897 tris / 176 units, slot10 = 821 / 489 /
46). Their GLBs are the round-9 files already in `models/`
(`idx{nn}_slot{0,10}_r9.glb`) — not duplicated under r10
names; the inventory records the mapping per package.

NEW this round: skeleton GLBs for ALL 12 packages (round 9
shipped only idx00/idx04): `models/idx{nn}_skeleton_r10.glb`
(body, slot 1: 110 bones; idx04 = 146) +
`models/idx{nn}_bone_slot12_r10.glb` (head, 22 bones), built
by `tools/r10_batch.py` from the proven BONE layout
(parents / translations / Eulers Rz·Ry·Rx / scales / names).

Bind sanity (world joints from the batch, per package in
the inventory): every body skeleton composes to a T-pose —
ATAMA above HARA, TE_R/TE_L out on ±x, ASHI near the floor —
with per-character proportions (idx20 is the largest:
ATAMA y = 1,886.8, hand span ±1,309.4; idx04: 146 bones).
Overlay renders VIEWED: `r10_idx05_skeleton_overlay.png`
(clean: skeleton inside the slot-10 mesh volume, arms/legs/
spine aligned) and `r10_idx00_skeleton_overlay.png` (in-mesh
T-pose; NOTE: finger-chain joints extend past the slot-10
mesh's arm span and idx00's composed ATAMA/TE positions
differ from round 9's published spot values — 1,708.9 /
−969.6 here vs 1,653.8 / −800.8 in JOB2-BONE-ROLES — while
idx01/05/08 land on round numbers, ASHI y = 130.0 exactly.
Flagged, not hidden: the composition convention is the
documented T·Rz·Ry·Rx·S chain; which convention round 9's
spot-check used for idx00 is unresolved.)

Stage/object packages (16: idx24…54 even): slot 0 = 624 B
NDPP transform node in 16/16 (quaternion floats, NOT
geometry — the character unit parser does not apply; see
JOB3-JOB5-STATUS), so no stage mesh GLBs are produced from
slot 0; their geometry lives in slot 9 (Job 5).

## JOB 4 — B3 census: slice A-packages classified by slot pattern

From the round-7 census slot maps (5,470 containers), A-model
packages beyond the top-76 anchors classify structurally:

| Class (slot pattern) | Count |
|---|---|
| Full-character pattern (BONE body + NDPP slot0/10 + BONE head 1,664 B) | 28 |
| Boned part (BONE present, not the full pattern) — costume/part packages with their own skeleton subset | 3,002 |
| Rigid NDPP part/item (NDPP, no BONE) | 436 |
| Stage/object pattern (624 B node + large slot 9) | 236 |
| (B-texture 1,432 + dir-other 336 = the known remainder) | 1,768 |

Top-76 accounting is now closed: 12 character + 16
stage/object + 28 NTPP-identified (27 slot-0 NTPP + idx03,
whose NTPP sits in the payload slots of a type-B directory)
+ 2 stubs (idx56/57) + 18 COM moveset files (idx58–75) = 76.
The brief's "29 NTPP" count: the 29th is not distinguishable
in the top-76 slot maps (idx03 was the last unclassified
type-B file) — stated as found, not rounded up.

NOT proven (stays open): per-character ASSIGNMENT of the
3,002 boned-part / 436 rigid slice packages. A-packages carry
no name strings beyond head/name chunks; assignment needs
the DATA401 index-order analysis against the top-76 anchors
(the same interleave that pairs A and B packages by entry).
Unknowns remain unknown with the pattern evidence above.
