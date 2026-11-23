#!/usr/bin/env python3
"""W7: Dolphin .dtm (TAS movie) generator for WMXIX navigation.

DTM format per Dolphin Source/Core/Core/Movie.h (DTMHeader, 256 bytes,
ControllerState 8 bytes/frame/controller). Byte 0 bits (LSB first):
Start=0x01 A=0x02 B=0x04 X=0x08 Y=0x10 Z=0x20 DPadUp=0x40 DPadDown=0x80.
Byte 1: DPadLeft=0x01 DPadRight=0x02 L=0x04 R=0x08 disc=0x10 reset=0x20
is_connected=0x40 get_origin=0x80. Bytes 2..7: TriggerL, TriggerR,
StickX, StickY, CStickX, CStickY (sticks neutral 0x80).
"""
import hashlib
import struct
import sys
import time

# Button bit masks: (byte_index, mask)
BTN = {
    "START": (0, 0x01), "A": (0, 0x02), "B": (0, 0x04),
    "X": (0, 0x08), "Y": (0, 0x10), "Z": (0, 0x20),
    "UP": (0, 0x40), "DOWN": (0, 0x80),
    "LEFT": (1, 0x01), "RIGHT": (1, 0x02),
    "L": (1, 0x04), "R": (1, 0x08),
}
ISO_MD5 = bytes.fromhex("c13c47a5ed24a675545c99a15e44529d")
GAME_ID = b"GW9E78"


class Movie:
    def __init__(self):
        self.frames = []  # list of 8-byte frames

    def _frame(self, buttons=(), stick=(0x80, 0x80), cstick=(0x80, 0x80),
               trig=(0, 0)):
        b = bytearray(8)
        b[1] = 0x40  # is_connected
        for name in buttons:
            i, m = BTN[name]
            b[i] |= m
        b[2], b[3] = trig
        b[4], b[5] = stick
        b[6], b[7] = cstick
        return bytes(b)

    def idle(self, n):
        f = self._frame()
        self.frames.extend([f] * n)
        return self

    def press(self, buttons, hold=8, after=0):
        """Hold buttons for `hold` frames, then idle `after` frames."""
        if isinstance(buttons, str):
            buttons = (buttons,)
        f = self._frame(buttons)
        self.frames.extend([f] * hold)
        if after:
            self.idle(after)
        return self

    def stick_dir(self, x, y, n):
        """Hold the main stick at (x, y) for n frames (0..255, 128 neutral)."""
        f = self._frame(stick=(x, y))
        self.frames.extend([f] * n)
        return self

    def press_stick(self, buttons, x, y, hold=12, after=0):
        """Hold buttons + stick direction for `hold` frames, then idle `after`."""
        if isinstance(buttons, str):
            buttons = (buttons,)
        f = self._frame(buttons, stick=(x, y))
        self.frames.extend([f] * hold)
        if after:
            self.idle(after)
        return self

    def build(self, path, author="W7"):
        n = len(self.frames)
        hdr = bytearray(256)
        hdr[0:4] = b"DTM\x1a"
        hdr[4:10] = GAME_ID
        hdr[0x0A] = 0            # bWii
        hdr[0x0B] = 0x01         # controllers: GC pad 1
        hdr[0x0C] = 0            # bFromSaveState
        struct.pack_into("<Q", hdr, 0x0D, n)   # frameCount
        struct.pack_into("<Q", hdr, 0x15, n)   # inputCount
        struct.pack_into("<Q", hdr, 0x1D, 0)   # lagCount
        struct.pack_into("<Q", hdr, 0x25, 0)   # uniqueID
        struct.pack_into("<I", hdr, 0x2D, 0)   # numRerecords
        hdr[0x31:0x31 + len(author)] = author.encode()
        hdr[0x71:0x81] = ISO_MD5
        struct.pack_into("<Q", hdr, 0x81, int(time.time()))
        hdr[0x89] = 0            # bSaveConfig (use current Dolphin settings)
        hdr[0x97] = 0x01         # memcards: slot A
        struct.pack_into("<Q", hdr, 0xED, n * 8100000)  # tickCount (60fps NTSC)
        with open(path, "wb") as f:
            f.write(hdr)
            for fr in self.frames:
                f.write(fr)
        print(f"wrote {path}: {n} frames ({n/60:.1f}s @60fps)")
        return path


def nav1(path):
    """Probe 1: boot, skip intro, reach main menu, select first item."""
    m = Movie()
    m.idle(2400)                 # 40s: boot + logos + intro start
    m.press("START", 8, 300)     # skip intro video -> title (or title -> menu)
    m.press("START", 8, 600)     # title -> main menu
    m.press("A", 8, 900)         # select first menu item
    m.idle(600)
    return m.build(path)


def nav2(path):
    """Probe 2: mash START early/often to catch the title screen, then A."""
    m = Movie()
    m.idle(600)                  # 10s: boot to title
    for _ in range(10):          # mash Start for ~21s
        m.press("START", 8, 120)
    for _ in range(5):           # mash A for ~26s
        m.press("A", 8, 300)
    m.idle(1200)
    return m.build(path)


def nav3(path):
    """Probe 3: long run. Idle through boot/logos, then mash START through
    the intro video + title, then mash A through menus."""
    m = Movie()
    m.idle(1800)                 # 30s emulation: boot + logos
    for _ in range(45):          # mash Start, frames 1800-7200 (30-120s emu)
        m.press("START", 8, 112)
    for _ in range(6):           # mash A, frames 7200-9000 (120-150s emu)
        m.press("A", 8, 292)
    m.idle(600)
    return m.build(path)


def nav4(path):
    """Full chain to a match: boot -> title -> Exhibition -> Normal Match
    -> rules -> select The Rock (P1) + default COM pick -> arena -> match.
    Presses spaced 600 frames (10s emu) apart so menu transitions complete."""
    m = Movie()
    m.idle(1800)                 # 30s emu: boot + logos
    for _ in range(15):          # mash Start, frames 1800-3600 (skip video, enter menu)
        m.press("START", 8, 112)
    m.idle(600)                  # menu settle
    m.press("A", 8, 592)         # Exhibition (menu) ~frame 4800
    m.press("A", 8, 592)         # Normal Match (match type) ~5400
    m.press("A", 8, 592)         # confirm rules ~6000
    m.press("A", 8, 592)         # P1 picks The Rock (default) ~6600
    m.press("A", 8, 592)         # COM pick (default cursor) ~7200
    m.press("A", 8, 592)         # arena confirm (default) ~7800
    m.idle(6000)                 # entrances + match start (~100s emu)
    return m.build(path)


def obs1(path):
    """Observation run 1: nav3-proven Start-mash (45x) to the menu, then
    A-mash through Exhibition -> Normal Match -> rules -> P1/COM picks ->
    arena, Start-mash to skip entrances, then in-match mashing.
    (nav4's short 15x Start-mash missed the title window in nav4b; nav3's
    45x mash reached the menu twice.)"""
    m = Movie()
    m.idle(1800)
    for _ in range(45):          # mash Start, frames 1800-7200 (proven: nav3)
        m.press("START", 8, 112)
    for _ in range(10):          # mash A, frames 7200-10200 (menu chain)
        m.press("A", 8, 292)
    for _ in range(10):          # Start-mash through entrances (10200-12600)
        m.press("START", 8, 232)
    # in-match mashing: 40 cycles of (stick dir + A/B), 60 frames each
    dirs = [(0x00, 0x80), (0xFF, 0x80), (0x80, 0x00), (0x80, 0xFF),
            (0x40, 0x40), (0xC0, 0xC0), (0x40, 0xC0), (0xC0, 0x40)]
    for i in range(40):
        sx, sy = dirs[i % len(dirs)]
        btn = "A" if i % 3 else "B"
        m.press_stick(btn, sx, sy, 12, 48)
    m.idle(1200)
    return m.build(path)


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "nav1"
    out = sys.argv[2] if len(sys.argv) > 2 else f"/data/wmxix/w7/{which}.dtm"
    {"nav1": nav1, "nav2": nav2, "nav3": nav3, "nav4": nav4, "obs1": obs1}[which](out)
