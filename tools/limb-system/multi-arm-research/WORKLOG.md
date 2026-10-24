# WORKLOG — Multi-Arm / Retracting-Limb Research + Pull-in (2026-10-19)

**Owner order (verbatim):** "Study things and characters like DXMMII and multi armed fighters or characters or retracting limb characters to help u wire up and pull in stuff to help into the repo."

## What was done

1. **Researched** multi-arm fighters across games: MK Shokan (Goro/Sheeva/Kintaro — extra bone chains, arm-pair readability), Asura's Wrath (six arms as a power-up STATE — maps to DXMMII's 5-state machine), Doctor Octopus (independent per-tentacle IK targets — maps to DXMMII's floating arms), General Grievous (scripted 2→4 split beat — maps to the grow transition), Tekken Jack robots (modular rigid parts — validates DXMMII's KatsBits method).
2. **Found the keyframing fix** for DXMMII's open detach/reattach issue: Child Of constraints with keyframed Influence (two constraints per arm — one to the socket bone, one to a free control — cross-faded on adjacent frames). This is the Blender-manual-documented standard technique; the current structural-reparenting approach cannot be keyframed. Full migration spec written in `tools/limb-system/dxmmii/RESEARCH-MULTIARM-2026-10-19.md` §2.
3. **Pulled in** Wiggle 2 "Ultimate" (N30Z3N/Blender-Wiggle-Bones-V3), GPL-3.0, Blender 4.0/5.x — spring physics for bones, intended for DXMMII's floating-arm free controls. LICENSE shipped verbatim.
4. **Honest license calls:** 6 items studied but NOT pulled (no license: tentacle_rigs, animaide, springbones, rigid-body-bones, wiggle_bones fork; commercial: Auto-Rig Pro; Maya-only: tentacletk). Full log in `LICENSE-LOG.md`.
5. **Documented** Rigify's `tentacle` rig-type (GPL, ships with Blender) as the future path for true doc-ock arms.

## What was NOT done (follow-ups)

- The Child Of migration in `04_states_demo.py` needs a Blender session to implement + re-run QC — the research doc is the complete spec, not the implementation.
- The 2 missing leg segment parts need a Blender build run.
- Wiggle 2 not yet tried on a floating arm — needs eyes-checked testing.

## Files in this PR (all additions, zero deletions)

- `tools/limb-system/multi-arm-research/README.md`
- `tools/limb-system/multi-arm-research/LICENSE-LOG.md`
- `tools/limb-system/multi-arm-research/WORKLOG.md`
- `tools/limb-system/multi-arm-research/wiggle-bones-v3/{LICENSE,README.md,wiggle_2_ultimate.py}`
- `tools/limb-system/dxmmii/RESEARCH-MULTIARM-2026-10-19.md`
