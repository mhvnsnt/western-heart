# Blender pin — Western Heart, 2026-11-02

## Decision: PIN Blender 5.2.3 LTS (unified, no split)

Blender **5.2.3 LTS is the Western Heart Blender standard**, including for
MB-Lab. No 4.0.2 / 5.2.3 split is needed: MB-Lab 1.8.1 was run headless on
Blender 5.2.3 on this VM and produced a finished GLB (proof below).

This closes wiring-plan item 1 of
`docs/handoffs/TOOLS-AUDIT-20261102.md` ("Pin Blender 5.2.3 + verify
MB-Lab on it, or document the 4.0.2/5.2.3 split") on the first branch:
the pin, with verification. The audit's prior statement — that MB-Lab
1.8.1 on Blender 5.x was NOT verified in the repo — is superseded by
this run. The older in-repo standard (Blender 4.0.2 for MB-Lab, per
`tools/mb-lab/README.md`) remains true as history; it is no longer the
only verified MB-Lab Blender.

## What this PR changes (0 deletions)

- `tools/blender/check-blender-pin.sh` (new) — runnable pin check:
  detects a 5.2.3 LTS binary (or uses `$BLENDER`), prints PASS only on
  an exact `Blender 5.2.3` version line, and optionally reports an
  MB-Lab checkout when `$MBLAB_DIR` is set. No network, no secrets.
  Run it with: `bash tools/blender/check-blender-pin.sh`
  (it passes with and without `HOME=/tmp`; see "Environment" below).
- `tools/mb-lab/fetch-mb-lab.sh` (one-line fix) — the pinned tag was
  `v1.8.1`, which does not exist upstream; the real upstream tag is
  `1_8_1` (commit `063bff04e60f3e7c651fda628c30f5d83f3f3078`). The
  script now defaults to `1_8_1`. Proven: `git clone --depth 1 --branch
  1_8_1 https://github.com/animate1978/MB-Lab.git` succeeds, while
  `--branch v1.8.1` fails with "Remote branch v1.8.1 not found".
- `tools/mb-lab/README.md` (table addition only) — records the 5.2.3
  verification alongside the existing 4.0.2 row.
- This doc (new) — the proof note.

No deploy. No API keys or secrets in any file. No raw commercial game
files, models, textures, animations, audio, or ROMs in this PR.
MB-Lab itself is never committed to git (~357 MB checkout); the fetch
script is the install, and this run's checkout lived only in scratch.

## Proof — headless MB-Lab 1.8.1 on Blender 5.2.3 (2026-11-02, this VM)

Environment: 4 CPU, no NVIDIA device, no GPU — CPU-only Blender.
Blender is not in PATH; the binary used was
`~/workspace/tools-industry/blender-5.2.3-linux-x64/blender`, with
`HOME=/tmp` for Blender config writes (home-disk quota blocked some
home writes during this lane; see "What failed" below).

| Item | Verified value |
|---|---|
| Blender | `Blender 5.2.3 LTS`, build 2026-10-22, hash `e13b728c6880`, branch `blender-v5.2-release` |
| MB-Lab | 1.8.1, upstream tag `1_8_1`, commit `063bff04e60f3e7c651fda628c30f5d83f3f3078`, `bl_info` Blender minimum `(4, 0, 0)` |
| Addon enable (probe) | `MBLAB_ENABLE_OK`, version `(1, 8, 1)` on Blender 5.2.3 |
| Character run | `tools/mb-lab/run_mblab_job.py` (repo version, unmodified logic; a scratch copy only added flushed prints), spec character `m_ca01`, `finalize: true`, `decimate_ratio: 0.06` |
| Session | `lab session started`, then `finalized to standard Blender model` |
| Character mesh | `MBlab_bd1793641431.7641513`, 17,074 polys before decimation |
| Decimated mesh | 2,048 polys (x0.06) |
| GLB export | exit 0, `exported -> /tmp/mb523.glb`, glTF export 59.37 s, generator `Khronos glTF Blender I/O v5.2.41`, glTF 2.0 |
| GLB file | 3,589,092 bytes, SHA-256 `cdc5a3dfd1b2dfc494c09a2408de9e3f7356888b6b79ac92178f2c540c010a4e`, magic `glTF`, 1 mesh (`MBLab_human_male`), 73 nodes, 1 skin, 0 animations |
| Total run time | ~13 minutes on this 4-CPU VM (session + finalize + export); the export step alone was 59 s |

Warnings seen (non-fatal, recorded honestly, not hidden):

- `Warning: Cannot move modifier beyond the start of the list` (at finalize)
- `Info: Applied modifier was not first, result may not be as expected` (at decimate)
- `WARNING: There are more than 4 joint vertex influences. The 4 with highest weight will be used (and normalized).` (at GLB export)

None of these stopped the run, and the exported GLB parses as valid
glTF 2.0 (header, length field, and JSON chunk all agree with the file
size above).

## Re-run (for a later run)

```bash
# 1. Pin check
bash tools/blender/check-blender-pin.sh

# 2. Fetch MB-Lab (corrected tag; ~357 MB, scratch only, never committed)
bash tools/mb-lab/fetch-mb-lab.sh /tmp/mblab-test
#    -> /tmp/mblab-test/MB-Lab

# 3. Headless generation on Blender 5.2.3 (allow ~15 min on a 4-CPU VM)
BLENDER=~/workspace/tools-industry/blender-5.2.3-linux-x64/blender
HOME=/tmp "$BLENDER" -b --factory-startup \
  --python tools/mb-lab/run_mblab_job.py -- \
  --spec /tmp/spec523.json --out /tmp/mb523.glb \
  --mblab-dir /tmp/mblab-test/MB-Lab
```

Spec used (`/tmp/spec523.json`, not committed — it is scratch):

```json
{"params": {"character": "m_ca01", "finalize": true, "decimate_ratio": 0.06}, "out": "/tmp/mb523.glb"}
```

Character-ID note: the live MB-Lab 1.8.1 humanoid list on 5.2.3 is
`f_af01, f_as01, f_ca01, f_la01, m_af01, m_as01, m_ca01, m_la01, f_an01,
f_an02, f_an03, m_an01` — not the `male_01` / `female_01` examples in
`tools/mb-lab/README.md`. `run_mblab_job.py` warns and falls back to
the first available ID when given an unknown one, so use an ID from
this list in new specs.

## What failed / was NOT claimed

- First full run (2026-11-02, ~17:2x CST): killed by the agent tool's
  own timeout (~343 s, SIGTERM), NOT by Blender or MB-Lab. Its log
  already showed a character update in progress. It is not counted as
  a failure of MB-Lab on 5.2.3; the later background run completed.
- A workspace scratch checkout vanished between steps and a later
  home clone failed with `Disk quota exceeded` despite filesystem
  free space — the home-disk quota, not a repo problem. All MB-Lab
  scratch therefore stayed in `/tmp` (512 MB tmpfs; the 357 MB
  checkout plus a 3.5 MB GLB fit, with ~73 MB to spare at the end).
- A second background attempt failed only because that missing
  workspace checkout was not there (`MB-Lab not found at ...`);
  again, not a Blender/MB-Lab incompatibility.
- GPU rendering was NOT tested: this VM has no GPU. The pin covers
  CPU headless generation / rig / export. GPU renders still need a
  GPU machine or notebook, per the audit's owner GPU-first rule.
- Windows was NOT tested. Nothing in this PR claims Windows behavior.
- The GLB from this run was NOT committed to the repo (scratch only,
  and it is a generated test character, not a shipped template).
  Re-baking the 9 shipped templates on 5.2.3 is a follow-up bake run,
  not claimed here.

## Still owed (with reasons)

- Re-bake the shipped MB-Lab templates on 5.2.3 and land them only
  through the normal template-bake path — owed: a bake run, not a
  claim in this PR.
- `tools/mb-lab/fetch-mb-lab.sh` still hints at a Blender 4.0.2
  binary path in its warning text; that hint is warning-only (the
  script does not fail without it) and is left for a follow-up
  cleanup so this PR stays to the pin + tag fix.
- `tools/mb-lab/README.md`'s `male_01` / `female_01` spec examples
  predate the live 1.8.1 ID list above; updating those examples is
  owed as a docs follow-up, not faked here.
- GPU-render proof on a GPU machine — owed until such a run exists.
