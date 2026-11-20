# Skeleton GLB supersede notice (round 12, 2026-10-22)

**The r11 skeleton GLBs supersede the r9/r10 skeleton GLBs.**

- Use: `idx{nn}_skeleton_r11.glb` and `idx{nn}_bone_slot12_r11.glb`
  (built by `tools/r11_skeleton_fix.py`).
- Superseded (kept on disk, labeled — do NOT build on them):
  all `*_r9.glb` and `*_r10.glb` skeleton files in this directory.
- Reason: r9/r10 compose bind joints with full TRS — per-bone
  scales propagate into descendant translations. The BONE bytes
  prove the correct composition is T·R only (scales do NOT
  propagate); the TRS walks err by up to 597.3 units (idx00
  ASHI_R lands at y=−9.7 vs the mesh floor −0.7; fingers extend
  30% past the mesh span). The r11 files reproduce the proven
  bind pose to ≤0.02 units on all 24 skeleton GLBs (round 11,
  JOB2-IDX00-SKELETON-VERDICT).
- All future skeleton work — skinning, animation, overlays —
  uses r11 as its only skeleton source.
