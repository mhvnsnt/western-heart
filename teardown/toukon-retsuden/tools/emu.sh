#!/bin/bash
# Reliable mednafen input helper. Usage:
#   emu.sh press <key> [key...]   # 250ms hold per key
#   emu.sh shot <name>            # F9 screenshot -> work/<name>.png
#   emu.sh wait <seconds>
export DISPLAY=:99
W=$(xdotool search --name "Toukon Retsuden" | head -1)
if [ -z "$W" ]; then echo "no mednafen window"; exit 1; fi
SNAP=~/.mednafen/snaps
case "$1" in
  press)
    shift
    for k in "$@"; do
      xdotool windowfocus "$W" keydown "$k"; sleep 0.25
      xdotool keyup "$k"; sleep 0.4
    done
    ;;
  shot)
    n=$(ls $SNAP/*.png 2>/dev/null | wc -l)
    xdotool windowfocus "$W" key F9; sleep 1
    newest=$(ls -t $SNAP/*.png | head -1)
    cp "$newest" ~/workspace/toukon-english/work/"$2".png
    echo "shot -> work/$2.png"
    ;;
  wait) sleep "$2" ;;
esac
