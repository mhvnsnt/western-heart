# tools/cue4parse — CUE4Parse (Unreal pak extraction for IMPORT)

CUE4Parse (github.com/FabianFG/CUE4Parse, MIT) parses Unreal Engine .pak /
.uasset files — the IMPORT lane's extractor for UE-based games (Tekken 8
assets, UE-model teardowns). UModel (the classic UE viewer) covers what
CUE4Parse can't preview; both sit behind the same IMPORT menu.

## Place in the pipeline

```
IMPORT (unified IMPORT panel)
  Tripo auto-intake | CUE4Parse (.pak/.uasset -> glTF) | UModel (preview/extract)
  -> wrap -> rig -> export
```

## Fetch-on-demand (DISK RULES)

```bash
bash tools/cue4parse/fetch-cue4parse.sh [dest]   # default: tools/cue4parse/vendor
```

Pulls the pinned CUE4Parse release (needs dotnet for the CLI; the script
checks). Never committed.

## Suite wiring

IMPORT panel → "Extract UE pak (CUE4Parse)" submits
`{"tool":"cue4parse","params":{"pak":"<file.pak>","aes":"<key hex>"},"out":"<dir/>"}`
to the job queue. The runner shells to the fetched CLI, converts to glTF
where the game version is supported, and lists extracted assets in the
status log. AES keys are passed per-job, never stored.
