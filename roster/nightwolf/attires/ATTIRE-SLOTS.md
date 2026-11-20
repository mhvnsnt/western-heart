# NIGHTWOLF — ATTIRE SLOTS

Owner 2026-10-18: Nightwolf's Tripo model ("tribal warrior 3d model" by marz6kdabest,
https://studio.tripo3d.ai/3d-model/5b0835eb-6c87-4257-899e-0771698d02c6)
is his DEFAULT attire (TRIPO=MAIN ATTIRES law). Tribute to Serena Misae Brown. Pulled via
tools/tripo-pull/ (public API, no sign-in); front render own-eyes verified 2026-10-18.

- **Attire 1 (DEFAULT)** — Tripo "tribal warrior" as pulled: tribal warrior build, face paint,
  tribal gear (21.87MB meshopt, 1 mesh, 1,015,766 verts). `attires/attire1/model.glb`
- **Attire 2+** — reserved. The existing base build (`game/assets/models/nightwolf.glb`) ladders back
  per the Tripo-main/base-back rule.

NOTE: All Tripo GLBs are unrigged statics — the live game default (`game/js/assets.js`) does NOT swap yet.
The playable swap rides with the auto-rig pass (Kevin/Star/King Tyrant pattern). Until then A1 is the
canonical default per the TRIPO=MAIN ATTIRES law.

## Attire 1 rigged model — re-rig landed 2026-11-09

`attires/attire1/model-rigged.glb` (the file `game/js/assets.js` key `nightwolf-attire1`
loads) was REPLACED with the 2026-11-07 pipeline refit of that same file
(`tools/auto_rig/refit_rig.py`, Pantera template fit → bone-heat rebind → head
territory → secondary chains): 27,414,444 B (blob 1cfe2f3d) → 28,428,932 B,
sha256 8cb4adeb80bea3c864526ce24c3916537e1e5a47abbf636fb25fb3570093180a,
58 joints, 1 mesh, 0 animations. The embedded CMU test clip and the material-less
Icosphere node from the old file do not carry over. Acceptance (lane probe on the
final encoded file): anatomical face slab 100.0% Head (was 53% head chain),
LeftArm dominant verts 0 → 30,447, forearm height offsets 21.5/21.6 cm → 0.6/0.4 cm;
validate + seam gates PASS. Known gap: the seam_safe_smooth pass never completed
(SIGKILL on the build box) — the landed rig is the post-territory/chains stage.
Full report: `docs/handoffs/NIGHTWOLF-RERIG-REPORT-2026-11-07.md`; proof frames:
`docs/proof/2026-11-09/nightwolf-rerig/`. Original deliverable preserved byte-identical
in release `nightwolf-rerig-20261107-20261108` (mhvnsnt/clouddog-storage).
