# accelerators — the 5-stage batch pipeline

> **ALL AGENTS — READ THIS FIRST.**
> This is an **overnight batch pipeline**, not an interactive toolkit. Each stage
> takes a whole directory and processes every file in it, unattended, in order.
> Binaries are **NEVER vendored** in this repo: every stage fetches its tools on
> demand into its own `bin/` directory (`<stage>.sh install`), exactly like
> `tools/depot-pull/`. Before pulling or extracting anything, read
> `../depot-pull/DISK-RULES.md` — the VM disk has filled up before and blocked
> everyone's work. Extract, convert, **delete the downloads**.

## The five stages

| # | Stage | Script | In → Out |
|---|-------|--------|----------|
| 1 | EXTRACTION | `extract/extract.sh` | UE `.pak` files → meshes/anims/textures (PSK/PSA/FBX/GLB + PNG) |
| 2 | RETARGET | `retarget/retarget-batch.sh` | source anims + WH-rigged target → retargeted animated GLBs |
| 3 | RIGGING | `rig/rig-batch.sh` | unrigged meshes → auto-weighted rigged GLBs (Blender bone heat) |
| 4 | CLEANUP | `cleanup/cleanup-batch.sh` | GLBs → decimated, weld-merged, normal-fixed GLBs |
| 5 | WEB OPTIMIZE | `webopt/webopt.sh` | GLBs → meshopt-compressed web-ready GLBs |

## Run the whole pipeline

```bash
# one-time: fetch every stage's tools (Blender comes from tools/setup/setup_toolchain.sh)
./run-pipeline.sh install

# full run: paks in, web-ready GLBs out
./run-pipeline.sh /path/to/pakdir --out /path/to/work --aes <AES_KEY> --ue 5.3

# run only some stages (e.g. overnight rig+cleanup on already-extracted meshes)
./run-pipeline.sh /path/to/meshdir --out /path/to/work --stages 3,4
```

Each stage also runs standalone — see its own README. Stage outputs land in
`<out>/s1-extracted`, `<out>/s2-retargeted`, … plus a `pipeline.log`.

## Stage contracts

- **Inputs are directories, outputs are directories.** Never single files.
- **Continue on error.** One bad file logs and moves on; the summary at the end
  lists every failure. Nothing silently skipped.
- **No clobbering.** Outputs go to a fresh/empty dir (refuse to write into a
  non-empty output dir without `--force`).
- **Disk rules.** `df` check before any big pull; scratch in the work dir, never
  in the repo; delete paks/archives after conversion (see
  `../depot-pull/DISK-RULES.md`).

## Coordination

- Stage 2 consumes the **Tekken bone-map** owned by the retargeting lane
  (`tools/anim-retarget/bone_maps/`). This pipeline does NOT define bone maps —
  it fails loudly if the map it needs isn't there yet.
- Blender 4.0.2 comes from `tools/setup/setup_toolchain.sh`
  (`$PREFIX/blender/blender-4.0.2-linux-x64/blender`, default
  `$HOME/workspace/tools`). Stages 2–4 refuse to run until it's installed.
- glTF-Transform/meshoptimizer versions match `tools/setup/setup_toolchain.sh`
  where applicable.
