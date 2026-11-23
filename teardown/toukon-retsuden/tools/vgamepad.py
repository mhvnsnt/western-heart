#!/usr/bin/env python3
"""Virtual gamepad daemon for RetroArch input on the Oracle VM.

Creates a uinput gamepad (evdev), listens on a FIFO for button commands.
Run with sudo (needs /dev/uinput write access).
Commands (one per line, written to the FIFO):
  press <button> [ms]   - press+release a button (default hold 300ms)
  combo <b1> <b2> ... [ms] - press multiple buttons simultaneously
  down <button>        - press and hold a button (until matching up)
  up <button>          - release a held button
  quit                  - exit
Buttons: south(a/cross) east(b/circle) north(x/triangle) west(y/square)
  start select tl l2 tr r2 up down left right
Usage:
  sudo python3 vgamepad.py &          # start daemon (creates /tmp/vpad.fifo)
  echo "press start" > /tmp/vpad.fifo # send Start
"""
import os
import sys
import time
from evdev import UInput, ecodes as e

FIFO = "/tmp/vpad.fifo"

BUTTONS = {
    "south": e.BTN_SOUTH,   # A / Cross
    "east": e.BTN_EAST,     # B / Circle
    "north": e.BTN_NORTH,   # X / Triangle
    "west": e.BTN_WEST,     # Y / Square
    "start": e.BTN_START,
    "select": e.BTN_SELECT,
    "tl": e.BTN_TL, "tr": e.BTN_TR,
    "tl2": e.BTN_TL2, "tr2": e.BTN_TR2,
    "thumbl": e.BTN_THUMBL, "thumbr": e.BTN_THUMBR,
    "up": e.BTN_DPAD_UP, "down": e.BTN_DPAD_DOWN,
    "left": e.BTN_DPAD_LEFT, "right": e.BTN_DPAD_RIGHT,
}

def main():
    caps = {
        e.EV_KEY: sorted(set(BUTTONS.values())),
        e.EV_ABS: [
            (e.ABS_X, (0, -32767, 32767, 0, 0)),
            (e.ABS_Y, (0, -32767, 32767, 0, 0)),
        ],
    }
    ui = UInput(caps, name="Virtual Gamepad", version=0x1)
    print(f"device: {ui.device.path}", flush=True)
    try:
        os.unlink(FIFO)
    except FileNotFoundError:
        pass
    os.mkfifo(FIFO)
    print(f"fifo: {FIFO}", flush=True)
    while True:
        with open(FIFO, "r") as f:
            for line in f:
                parts = line.strip().split()
                if not parts:
                    continue
                if parts[0] == "quit":
                    print("quitting", flush=True)
                    ui.close()
                    return
                if parts[0] == "press" and len(parts) >= 2:
                    btn = BUTTONS.get(parts[1])
                    if btn is None:
                        print(f"unknown button: {parts[1]}", flush=True)
                        continue
                    ms = int(parts[2]) if len(parts) > 2 else 300
                    ui.write(e.EV_KEY, btn, 1)
                    ui.syn()
                    time.sleep(ms / 1000.0)
                    ui.write(e.EV_KEY, btn, 0)
                    ui.syn()
                    print(f"pressed {parts[1]} ({ms}ms)", flush=True)
                if parts[0] == "combo" and len(parts) >= 2:
                    # combo <b1> <b2> ... [ms] - last arg numeric = hold ms
                    args = parts[1:]
                    ms = 300
                    if args and args[-1].isdigit():
                        ms = int(args.pop())
                    btns = []
                    for name in args:
                        b = BUTTONS.get(name)
                        if b is None:
                            print(f"unknown button: {name}", flush=True)
                            continue
                        btns.append(b)
                    for b in btns:
                        ui.write(e.EV_KEY, b, 1)
                    ui.syn()
                    time.sleep(ms / 1000.0)
                    for b in btns:
                        ui.write(e.EV_KEY, b, 0)
                    ui.syn()
                    print(f"combo {args} ({ms}ms)", flush=True)
                if parts[0] == "down" and len(parts) >= 2:
                    btn = BUTTONS.get(parts[1])
                    if btn is None:
                        print(f"unknown button: {parts[1]}", flush=True)
                        continue
                    ui.write(e.EV_KEY, btn, 1)
                    ui.syn()
                    print(f"down {parts[1]}", flush=True)
                if parts[0] == "up" and len(parts) >= 2:
                    btn = BUTTONS.get(parts[1])
                    if btn is None:
                        print(f"unknown button: {parts[1]}", flush=True)
                        continue
                    ui.write(e.EV_KEY, btn, 0)
                    ui.syn()
                    print(f"up {parts[1]}", flush=True)

if __name__ == "__main__":
    main()
