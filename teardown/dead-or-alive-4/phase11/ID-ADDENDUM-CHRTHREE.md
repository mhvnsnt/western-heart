# DOA4 Phase 11 — ID addendum: chrthree (continuation lane)

Companion to `phase11/ID-TABLE.md` (primary lane). The brief's
"chrthree pkg50" item is resolved as follows:

- **chrthree pkg50 does not exist as a model package** — proven two
  independent ways: (1) the phase-6 inventory/manifest ends at
  pkg49 (50 full packages, pkg00–49; indices ≥50 are TX2D-only
  sub-packages, `phase7/WIRING-INVENTORY.md`); (2) this lane pulled
  release `doa4-phase6-models-20261021` assets
  `doa4-phase6-chrthree.z01` (99,614,720 B) + `doa4-phase6-chrthree.zip`
  (69,543,514 B — sizes match the release exactly) and listed the
  concatenated archive: exactly 50 files, `chrthree-pkg00-skinned.glb`
  … `chrthree-pkg49-skinned.glb`. No pkg50 entry exists to render.
- As the family's first viewed representative, the archive's last
  package was extracted and rendered instead:

| package | identification | evidence (viewed render) | confidence | competing candidates |
|---|---|---|---|---|
| chrthree-pkg49 | unidentified | VIEWED `renders/p11-chrthree-pkg49.png`: heavily shattered torso mass above a smooth wide apron/skirt panel with a rounded front pouch/ornament; wide shattered sleeve masses both sides (raw-geometry front render, `phase11/tools/render_front_p11.py`, of the phase-6 skinned GLB extracted from the release above) | — | — |

chrthree coverage after this addendum: **1/50 viewed (pkg49)**;
pkg00–48 remain unviewed — still the largest ID gap, named not
hidden. No name claimed; no re-grades.

Clears (this lane, own rebuildable intermediates only): the
concatenated `chrthree_full.zip` (169 MB) and the extracted
`chrthree-pkg49-skinned.glb` were cleared after this render
committed; the two pulled release parts were cleared with them.
Everything is re-pullable from release
`doa4-phase6-models-20261021` (asset names + sizes above).
