#!/usr/bin/env bash
# tools/accelerators/run-pipeline.sh — run the 5 accelerator stages in order.
#
#   ./run-pipeline.sh install
#   ./run-pipeline.sh <input_dir> --out <workdir> [options]
#
# Default chain (1,2,3,4,5): paks -> extracted -> retargeted -> rigged ->
# cleaned -> web-ready GLBs. Each stage's input defaults to the previous
# executed stage's output; override any with --sN-in.
#
# Stage 2 (retarget) needs --target <rigged.glb> and an anim dir (--s2-in);
# without --target it is skipped with a warning (the mesh pipeline 1,3,4,5
# is the common overnight run). See README.md.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

EXTRACT="$SCRIPT_DIR/extract/extract.sh"
RETARGET="$SCRIPT_DIR/retarget/retarget-batch.sh"
RIG="$SCRIPT_DIR/rig/rig-batch.sh"
CLEANUP="$SCRIPT_DIR/cleanup/cleanup-batch.sh"
WEBOPT="$SCRIPT_DIR/webopt/webopt.sh"

usage() {
  cat <<EOF
usage: $0 install
       $0 <input_dir> --out <workdir> [options]

options:
  --stages 1,2,3,4,5     which stages to run, in order (default: 1,2,3,4,5)
  --skip-install          don't auto-fetch stage tools (fail if missing)
  --aes KEY --ue <ver>    stage 1: pak AES key + UE version tag
  --target <rigged.glb>   stage 2: WH-rigged target model (required for stage 2)
  --bonemap PATH          stage 2: explicit bone map
  --s2-in DIR             stage 2: anim source dir (default: previous stage output)
  --s3-in DIR --s4-in DIR --s5-in DIR
                          override any stage's input dir
  --force                 allow writing into non-empty stage output dirs

examples:
  $0 /paks/tekken8 --out /work/t8 --aes <KEY> --ue 5.3
  $0 /anims/mixamo --out /work/r --stages 2 --target /work/fighter.glb \
      --bonemap tools/anim-retarget/bone_maps/mixamo_to_wh.json
  $0 /work/s1-extracted --out /work/r --stages 3,4,5
EOF
}

if [ "${1:-}" = "install" ]; then
  "$EXTRACT" install --umodel --cue4parse
  "$WEBOPT" install
  echo "NOTE: stages 2-4 need Blender 4.0.2 -> bash $REPO_ROOT/tools/setup/setup_toolchain.sh"
  exit 0
fi

[ $# -ge 1 ] || { usage; exit 1; }
input=$1; shift
out=""; stages="1,2,3,4,5"; skip_install=0
aes=""; ue=""; target=""; bonemap=""; force=""
s2_in=""; s3_in=""; s4_in=""; s5_in=""
while [ $# -gt 0 ]; do case "$1" in
  --out) out=$2; shift 2;;
  --stages) stages=$2; shift 2;;
  --skip-install) skip_install=1; shift;;
  --aes) aes=$2; shift 2;;
  --ue) ue=$2; shift 2;;
  --target) target=$2; shift 2;;
  --bonemap) bonemap=$2; shift 2;;
  --s2-in) s2_in=$2; shift 2;;
  --s3-in) s3_in=$2; shift 2;;
  --s4-in) s4_in=$2; shift 2;;
  --s5-in) s5_in=$2; shift 2;;
  --force) force="--force"; shift;;
  *) echo "unknown: $1"; usage; exit 1;;
esac; done

[ -n "$out" ] || { echo "--out <workdir> required"; exit 1; }
[ -d "$input" ] || { echo "input dir not found: $input"; exit 1; }
mkdir -p "$out"
log="$out/pipeline.log"
exec > >(tee -a "$log") 2>&1

echo "=== accelerator pipeline: stages [$stages] ==="
echo "input: $input"; echo "workdir: $out"; echo "log: $log"
df -h "$out" | tail -1

if [ "$skip_install" != 1 ]; then
  "$EXTRACT" install
  "$WEBOPT" install
fi

prev_out="$input"

# ---- stage 1: extraction (input is a pak dir) ----
case ",$stages," in *",1,"*)
  echo "--- stage 1 (extract): $prev_out -> $out/s1-extracted"
  s1_args=()
  [ -n "$aes" ] && s1_args+=(--aes "$aes")
  "$EXTRACT" unpack-dir "$prev_out" "$out/s1-extracted" "${s1_args[@]}" $force
  # umodel batch export needs --ue; without it, s1 output is the unpacked tree
  if [ -n "$ue" ]; then
    "$EXTRACT" umodel-export "$out/s1-extracted" "$out/s1-export" --ue "$ue"
    prev_out="$out/s1-export"
  else
    echo "(no --ue given: skipping umodel export; stage-1 output is the unpacked tree)"
    prev_out="$out/s1-extracted"
  fi
  ;;
esac

# ---- stage 2: retarget ----
case ",$stages," in *",2,"*)
  if [ -z "$target" ]; then
    echo "--- stage 2 (retarget): SKIPPED (no --target <rigged.glb> given)"
  else
    anim_in="${s2_in:-$prev_out}"
    r2_args=()
    [ -n "$bonemap" ] && r2_args+=(--bonemap "$bonemap")
    "$RETARGET" "$anim_in" "$target" "$out/s2-retargeted" --in-place "${r2_args[@]}" $force
    prev_out="$out/s2-retargeted"
  fi
  ;;
esac

# ---- stage 3: rigging ----
case ",$stages," in *",3,"*)
  echo "--- stage 3 (rig): $prev_out -> $out/s3-rigged"
  rig_in="${s3_in:-$prev_out}"
  "$RIG" "$rig_in" "$out/s3-rigged" $force
  prev_out="$out/s3-rigged"
  ;;
esac

# ---- stage 4: cleanup ----
case ",$stages," in *",4,"*)
  echo "--- stage 4 (cleanup): $prev_out -> $out/s4-cleaned"
  clean_in="${s4_in:-$prev_out}"
  "$CLEANUP" "$clean_in" "$out/s4-cleaned" $force
  prev_out="$out/s4-cleaned"
  ;;
esac

# ---- stage 5: web optimize ----
case ",$stages," in *",5,"*)
  echo "--- stage 5 (webopt): $prev_out -> $out/s5-web"
  opt_in="${s5_in:-$prev_out}"
  "$WEBOPT" optimize "$opt_in" "$out/s5-web" $force
  prev_out="$out/s5-web"
  ;;
esac

echo "=== pipeline complete: final output -> $prev_out ==="
echo "full log: $log"
