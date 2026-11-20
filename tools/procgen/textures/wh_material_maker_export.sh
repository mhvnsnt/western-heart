#!/usr/bin/env bash
# wh_material_maker_export.sh — batch-export Material Maker (.ptex) graphs to PBR sets.
# Material Maker (RodZill4/material-maker, MIT) CLI (documented at
# rodzill4.github.io/material-maker/doc/command_line.html):
#   material_maker --export-material --target <engine> -o <output_path> <input_files>
# Engines: Blender, Godot, Unity, Unreal. Install: Linux build from
# https://github.com/RodZill4/material-maker/releases (or Steam build to fund dev).
# Usage: wh_material_maker_export.sh graphs/ exported/ [Godot]
set -euo pipefail
MM="${MATERIAL_MAKER_BIN:-material_maker}"
GRAPHDIR="${1:?usage: wh_material_maker_export.sh graphs/ exported/ [target]}"
OUTDIR="$2"
TARGET="${3:-Godot}"
command -v "$MM" >/dev/null || { echo "Material Maker not found. Set MATERIAL_MAKER_BIN or install from https://github.com/RodZill4/material-maker/releases"; exit 1; }
mkdir -p "$OUTDIR"
"$MM" --export-material --target "$TARGET" -o "$OUTDIR" "$GRAPHDIR"/*.ptex 2>&1 | tail -3
echo "exported -> $OUTDIR/ (target: $TARGET)"
