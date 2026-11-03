# tools/eyes — creation suite EYES phase (2026-11-02)

Fitted LEFT / RIGHT eyeballs for the 9 creation-suite template bodies, with the WWE 2K Create-A-Superstar
Face > Eyes options (eye type, iris colour, sclera tint, pupil size; eye SHAPE / position stays on the `f_eye_*`
face sliders), filed on the Tekken 7 EYES slot.

| File | What |
|---|---|
| `build_eye_sockets.mjs` | Measures each template's own eyeball geometry through the game's instance path (assets.js createInstance, MB-Lab -> T3 bone remap): sclera centre + radius, iris gaze axis, and the centre/radius deltas of every eye slider (`f_eye_size/space/h/tilt/open/almond` +/-), all HEAD-BONE-LOCAL. Writes `customization/parts/eyes/eye-sockets.json`. `--check` diffs against the committed file. |
| `catalog_entries.py` | The 4 fitted eye types -> parts-catalog entries (`--apply`); `customization/build_suite_catalog.py` calls it on a full rebuild. |
| `proof_dump.mjs` + `proof_render.py` | No-WebGL proof: dumps world-space head triangles with fitted eyes for 6 scenes and rasterises them with a numpy z-buffer -> `proof/`. |

Runtime: `game/js/fitted-eyes.js` (shared by the suite viewer and the game). Test: `test/fitted-eyes.test.mjs`.

Measured facts (2026-11-02): the templates have no eye bones (MB-Lab game rig stops at `neck` / `head`), but each
carries MB-Lab's own eyeball primitives (materials `MBlab_human_eyes`, `MBLab_Iris_V4`, `MBlab_pupil`,
`MBlab_cornea`) rigid on the head with the eye-slider morph targets baked in. Sockets sit 32.9 mm (male) / 28.9 mm
(female) either side of the midline, eyeball radius 14.2-14.8 mm (eyeball.glb is 12 mm, so it is scaled per template).
Eye Tilt / Opening / Almond move the lids, not the eyeball centre, so only Size / Spacing / Height have socket deltas.

Rebuild after any template mesh change:

    node tools/eyes/build_eye_sockets.mjs && node --test test/fitted-eyes.test.mjs
    node tools/eyes/proof_dump.mjs /tmp/eyes-proof.json && python3 tools/eyes/proof_render.py /tmp/eyes-proof.json tools/eyes/proof

Blender: not available on the agent box (aarch64; no Blender build or `bpy` wheel for linux-aarch64), so the sockets
are measured from the same MB-Lab-baked mesh data in three.js and the proof is a software render. The templates
themselves are Blender/MB-Lab bakes (`tools/mb-lab/run_mblab_job.py`); a Blender-side cross-check of the sockets is
a natural follow-up on a box that has Blender.
