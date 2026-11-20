# Pantera Classic — Attire Slot 3

**Model:** `pantera-classic.glb` (7,625,912 bytes, 18 meshes / 18 materials / 54 embedded images, 1 skin)

**What it is:** the older Pantera build — the original purple-tights / black-panther-mask
attire, game-optimized and rigged to the Mixamo skeleton with hand-painted region
weights. Lower visual fidelity than the new full-res Attire 1, same design.

**Source (forensics 2026-10-17):** built from the **Tekken 7 King P1** (rigmodels FBX) —
NOT Tekken 6 PSP (the T6 PSP teardown yielded 0 Tekken meshes; its models were still
encrypted). Material names (`Modelhead_Material005`, `Modelboots1_Material020`, …)
are the rigmodels T7 King naming. Same source model as Attire 1; this is the
optimized in-game build, Attire 1 is the full-res reskin.

**Provenance:** recovered from `game/assets/models/pantera.glb` at commit `cd3bf38^`
(deleted by the DXMMII mass-deletion, restored here as the slot-3 model).
The 54k restore also brings back `game/assets/models/pantera.glb` — same bytes.

**Slot:** 3 — see `../ATTIRE-SLOTS.md`.
