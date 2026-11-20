# Stage 3 — RIGGING

> **ALL AGENTS — READ THIS FIRST.**
> This is the **fast automatic pass**: Blender bone-heat automatic weights over
> a whole directory, overnight, no GUI. It is not a replacement for
> `tools/auto_rig/` (GameRig cage fitting, weight painting, validation) — that
> stays the quality path for hero characters. If a model comes out with bad
> weights here, that's expected signal: send it to `tools/auto_rig/`, don't
> hand-tweak the batch output.

## What it does

For every GLB/FBX in the input dir: import, find armature + meshes, parent
each unparented mesh with `ARMATURE_AUTO` (bone heat), export rigged GLB.
Per-file report lines show vertex-group counts. Files with no armature are
logged and skipped, never fatal.

## Quick start

```bash
# needs Blender 4.0.2: bash tools/setup/setup_toolchain.sh  (once)
./rig-batch.sh /path/to/work/s2 /path/to/work/s3
```

Options: `--reweight` (redo weights on already-parented meshes),
`--suffix .rigged`, `--force` (allow non-empty outdir).

## Notes

- Bone heat needs a sane bind pose and non-degenerate geometry — garbage in,
  garbage out. Run stage 4 (cleanup) first if meshes are raw scans.
- Multi-armature files: first armature wins, warning logged.
- The log at `<outdir>/rig-batch.log` is the proof — attach it to the PR.
