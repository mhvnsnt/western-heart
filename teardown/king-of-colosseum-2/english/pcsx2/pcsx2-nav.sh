#!/bin/bash
# PCSX2 navigation helpers for the KoC2 M3 boot tests (Xvfb :99, no WM).
#   press <key> [count] [hold_secs]  - focus game window, send held key(s)
#   shot <name>                      - screenshot to pcsx2/shots/ (retry for
#                                      quota), falling back to /tmp
# Keys: l = Circle (confirm), k = Cross (back), Return = Start,
#       Up/Down/Left/Right = D-pad. Japanese buttons: Circle confirms.
SHOTS=~/workspace/koc2-english/pcsx2/shots
export DISPLAY=:99

gamewin() { xdotool search --name 'コロシアム' | head -1; }

press() {
  local key="$1" count="${2:-1}" hold="${3:-3}"
  local W; W=$(gamewin)
  [ -n "$W" ] || { echo "no game window"; return 1; }
  xdotool windowfocus --sync "$W"
  for _ in $(seq 1 "$count"); do
    xdotool keydown "$key"; sleep "$hold"; xdotool keyup "$key"; sleep 3
  done
}

shot() {
  local name="$1" ok=0
  for _ in 1 2 3; do
    import -window root "$SHOTS/$name.png" 2>/dev/null && { ok=1; break; }
    sleep 5
  done
  if [ "$ok" = 1 ]; then echo "shot: $SHOTS/$name.png";
  else import -window root "/tmp/$name.png" && echo "shot: /tmp/$name.png (quota fallback)"; fi
}

# allow direct use: ./pcsx2-nav.sh press l 3 / ./pcsx2-nav.sh shot foo
if [ "${BASH_SOURCE[0]}" = "$0" ]; then "$@"; fi
