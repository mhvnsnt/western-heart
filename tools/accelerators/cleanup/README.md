# Stage 4 — CLEANUP

> **ALL AGENTS — READ THIS FIRST.**
> This stage is **destructive by design** (decimation deletes geometry). It
> always writes to a fresh output dir and never touches the inputs. Check the
> per-file before/after report in `<outdir>/cleanup-batch.log` before anything
> downstream consumes the output. When in doubt, re-run with `--decimate 0`.

## What it does

Per mesh, in order: weld duplicate verts (`--merge-dist`), delete loose
verts/edges, recalculate normals outward, decimate (`--decimate` ratio),
optional triangulate. All native Blender ops, headless, whole directory.

## Quick start

```bash
# needs Blender 4.0.2: bash tools/setup/setup_toolchain.sh  (once)
./cleanup-batch.sh /path/to/work/s3 /path/to/work/s4 --decimate 0.5
```

Options: `--decimate 0.5` (0 disables), `--merge-dist 0.0001`,
`--triangulate`, `--no-normals`, `--force`.

## Notes

- Armatures, vertex groups and animations pass through untouched; decimation
  preserves skinning.
- Decimate ratio is per-mesh, not global — 0.5 halves every mesh. Hero assets
  may want a gentler pass; tune per directory, not per file.
