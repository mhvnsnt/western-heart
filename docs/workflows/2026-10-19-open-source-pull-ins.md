# Workflow log — open-source pull-ins (2026-10-19)

Task: owner research-first pull-in order (2026-10-19 ~23:01 CDT) — research, pull, WIRE UP.
Branch/worktree: `research/pullins-2026-10-19` in `~/workspace/_wh-work/research-pullin-20261019`.

What was done:
1. Web research (2026 roundups, 80.lv, GitHub API search, Blender Extensions) for the five
   problem areas: move data decode, retargeting, straight-to-store, 3D pipeline, game dev.
2. Pulled straight into the repo worktree (no local warehousing), shallow clones vendored:
   - TKMovesets (Kiloutre, GPL-3.0) — Tekken T5–T8 moveset extraction reference.
   - Wiggle 2 (shteeve3d) — jiggle physics; TESTED: registers in Blender 4.0.2 headless.
   - Wiggle Bones (Hans-xwh, GPL-3.0) — Blender 5.0+ upgrade path.
   - Keemap (nkeeline, GPL-3.0) — retargeting; TESTED: registers in Blender 4.0.2 headless.
     Vendored Source only; 56MB example/ dropped, upstream URL in the pull-in doc.
   - GameRig (Arminando) — game-ready auto-rigging.
3. Documented in `docs/research/OPEN-SOURCE-PULL-INS-2026-10-19.md` + `tools/open-source/README.md`.
4. Not pulled: BlenRig 6 (repo 400MB, disk budget), MoCapAnything (research-grade),
   Auto-Rig Pro (paid), Good Good tool (no public repo). Reasons in the pull-in doc.
5. Straight-to-store/CloudDog mode owned by the separate CloudDog lane — not duplicated.

Test commands:
- Blender: `xvfb-run -a env -u PYTHONPATH blender -b --python-expr "import wiggle_2; wiggle_2.register()"`
  → "WIGGLE2 REGISTERED OK"
- Keemap: register as package → "KEEMAP REGISTERED OK"
