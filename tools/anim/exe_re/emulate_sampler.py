#!/usr/bin/env python3
"""tools/anim/exe_re/emulate_sampler.py — run Tekken 7's OWN animation sampler on chosen clip bytes, in an emulator.

Static reading of compiler-generated SSE is error-prone; this maps TekkenGame-Win64-Shipping.exe's sections into
Unicorn (CPU emulation only: no OS, no files, nothing of the game "runs" as a program), stubs the C-runtime imports the
code calls (sinf, cosf, modff, ...) in Python, and calls the sampler (RVA 0x73ea30, found with
magic_compare_funcs.py) with a clip buffer we control. It returns what the game computes: one 16-byte record per
bone, a quaternion (x, y, z, w) for rotation bones (descriptor 4..7) or (x, y, z, 1) for position bones.

    python3 -I tools/anim/exe_re/emulate_sampler.py EXE selftest      # 0xC8 probes + 0x64 formula check
library use:  S = Sampler(exe); S.sample(clip_bytes, t) -> (n, 4) array

Requires: pip install --user unicorn pefile capstone   (run with python3 -I from outside the exe's folder)
"""
import math
import site
import struct
import sys

sys.path.append(site.getusersitepackages())
import numpy as np  # noqa: E402
import pefile  # noqa: E402
from unicorn import Uc, UC_ARCH_X86, UC_MODE_64, UC_HOOK_CODE, UC_PROT_ALL  # noqa: E402
from unicorn.x86_const import (UC_X86_REG_RSP, UC_X86_REG_RIP, UC_X86_REG_RCX, UC_X86_REG_RDX,  # noqa: E402
                               UC_X86_REG_R8, UC_X86_REG_R9, UC_X86_REG_XMM0, UC_X86_REG_XMM1,
                               UC_X86_REG_XMM2, UC_X86_REG_RAX)

SAMPLER_RVA = 0x73ea30
STUB_BASE = 0x7FFF00000000
STACK_TOP = 0x7FFE00000000
STACK_SIZE = 0x400000
DATA_BASE = 0x7FFD00000000
DATA_SIZE = 0x400000


def _f(x):
    return struct.unpack('<f', struct.pack('<f', x))[0]


class Sampler:
    def __init__(self, exe):
        pe = pefile.PE(exe, fast_load=True)
        pe.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_IMPORT']])
        self.base = base = pe.OPTIONAL_HEADER.ImageBase
        data = open(exe, 'rb').read()
        mu = Uc(UC_ARCH_X86, UC_MODE_64)
        img = (pe.OPTIONAL_HEADER.SizeOfImage + 0xFFF) & ~0xFFF
        mu.mem_map(base, img, UC_PROT_ALL)
        mu.mem_write(base, data[:pe.OPTIONAL_HEADER.SizeOfHeaders])
        for s in pe.sections:
            raw = data[s.PointerToRawData: s.PointerToRawData + s.SizeOfRawData]
            mu.mem_write(base + s.VirtualAddress, raw)
        mu.mem_map(STACK_TOP - STACK_SIZE, STACK_SIZE, UC_PROT_ALL)
        mu.mem_map(DATA_BASE, DATA_SIZE, UC_PROT_ALL)
        mu.mem_map(STUB_BASE, 0x10000, UC_PROT_ALL)
        # fake TEB for gs: __chkstk reads gs:[0x10] (StackLimit); gs:[0x08] = StackBase
        teb = STUB_BASE - 0x10000
        mu.mem_map(teb, 0x10000, UC_PROT_ALL)
        mu.mem_write(teb + 0x08, struct.pack('<QQ', STACK_TOP, STACK_TOP - STACK_SIZE))
        mu.msr_write(0xC0000101, teb)  # IA32_GS_BASE
        mu.mem_write(STUB_BASE, b'\xc3' * 0x10000)  # every stub is a 'ret' (the hook does the work first)
        # every import -> its own stub address; the hook implements the few math/CRT ones the sampler uses
        self.stubs = {}
        i = 0
        for d in pe.DIRECTORY_ENTRY_IMPORT:
            for imp in d.imports:
                name = imp.name.decode() if imp.name else 'ord%d' % imp.ordinal
                addr = STUB_BASE + 16 * i
                mu.mem_write(imp.address, struct.pack('<Q', addr))
                self.stubs[addr] = name
                i += 1
        self.done_addr = STUB_BASE + 0xFFF0
        self._last_clip = None
        self.mu = mu
        self.unknown = []
        mu.hook_add(UC_HOOK_CODE, self._hook, begin=STUB_BASE, end=STUB_BASE + 0xFFFF)

    # --- import stubs -------------------------------------------------------------------------------------------
    def _xf(self, reg):
        v = self.mu.reg_read(reg)
        return struct.unpack('<f', struct.pack('<I', v & 0xFFFFFFFF))[0]

    def _setxf(self, reg, x):
        self.mu.reg_write(reg, struct.unpack('<I', struct.pack('<f', x))[0])

    def _hook(self, mu, addr, size, user):
        if addr == self.done_addr:
            mu.emu_stop()
            return
        name = self.stubs.get(addr)
        if name is None:
            return
        x = self._xf(UC_X86_REG_XMM0)
        if name == 'sinf':
            self._setxf(UC_X86_REG_XMM0, _f(math.sin(x)))
        elif name == 'cosf':
            self._setxf(UC_X86_REG_XMM0, _f(math.cos(x)))
        elif name == 'sqrtf':
            self._setxf(UC_X86_REG_XMM0, _f(math.sqrt(max(x, 0.0))))
        elif name == 'acosf':
            self._setxf(UC_X86_REG_XMM0, _f(math.acos(max(-1.0, min(1.0, x)))))
        elif name == 'atan2f':
            self._setxf(UC_X86_REG_XMM0, _f(math.atan2(x, self._xf(UC_X86_REG_XMM1))))
        elif name in ('memcpy', 'memmove'):
            dst, src, n = mu.reg_read(UC_X86_REG_RCX), mu.reg_read(UC_X86_REG_RDX), mu.reg_read(UC_X86_REG_R8)
            mu.mem_write(dst, bytes(mu.mem_read(src, n)))
            mu.reg_write(UC_X86_REG_RAX, dst)
        elif name == 'memset':
            dst, val, n = mu.reg_read(UC_X86_REG_RCX), mu.reg_read(UC_X86_REG_RDX) & 0xFF, mu.reg_read(UC_X86_REG_R8)
            mu.mem_write(dst, bytes([val]) * n)
            mu.reg_write(UC_X86_REG_RAX, dst)
        elif name == 'modff':
            ip = math.floor(x) if x >= 0 else math.ceil(x)
            mu.mem_write(mu.reg_read(UC_X86_REG_RDX), struct.pack('<f', ip))
            self._setxf(UC_X86_REG_XMM0, _f(x - ip))
        else:
            self.unknown.append(name)
            mu.emu_stop()
        # the stub byte is 'ret': execution continues there and returns to the caller

    # --- run --------------------------------------------------------------------------------------------------
    def sample(self, clip, t, flag=0, n_out=None):
        mu = self.mu
        clip = clip if isinstance(clip, bytes) else bytes(clip)
        if clip is not self._last_clip:          # same clip object: bytes already in place
            mu.mem_write(DATA_BASE, clip)
            self._last_clip = clip
        out = DATA_BASE + ((len(clip) + 0xFFF) & ~0xFFF)
        n0 = n_out or struct.unpack_from('<H', clip, 2)[0]
        mu.mem_write(out, b'\0' * (16 * n0))
        rsp = STACK_TOP - 0x10000
        rsp &= ~0xF
        rsp -= 8
        mu.mem_write(rsp, struct.pack('<Q', self.done_addr))
        mu.reg_write(UC_X86_REG_RSP, rsp)
        mu.reg_write(UC_X86_REG_RCX, DATA_BASE)
        mu.reg_write(UC_X86_REG_RDX, out)
        mu.reg_write(UC_X86_REG_R8, 0)
        mu.reg_write(UC_X86_REG_R9, flag)
        mu.reg_write(UC_X86_REG_XMM2, struct.unpack('<I', struct.pack('<f', t))[0])
        self.unknown = []
        mu.emu_start(self.base + SAMPLER_RVA, 0, count=20_000_000)
        if self.unknown:
            raise RuntimeError('sampler called unstubbed imports: %s' % self.unknown)
        n = n_out or struct.unpack_from('<H', clip, 2)[0]
        return np.frombuffer(bytes(mu.mem_read(out, 16 * n)), dtype='<f4').reshape(n, 4).astype(np.float64), \
            mu.reg_read(UC_X86_REG_RAX)


def c8_clip(frames, desc=None):
    """Minimal 0xC8 clip: header 0xC8, u16 bone count, u32 frame count, u32 descriptors, frames x bones x 3 f32."""
    frames = np.asarray(frames, dtype='<f4')
    nf, n, _ = frames.shape
    desc = desc or [4] * n
    b = bytearray(struct.pack('<BBHI', 0xC8, 0, n, nf))
    b += struct.pack('<%dI' % n, *desc)
    b += frames.tobytes()
    return b


def anim64_to_le(data, off):
    """A 0x64 clip as the PC game holds it in memory (little-endian header; the bitstream is byte-oriented and is
    copied as-is). Field layout = tools/anim/t7_anim64.py (TKMovesets2 ParseAnimation0x64)."""
    e = '<' if data[off] != 0 else '>'
    out = bytearray()
    p = off
    def take(fmt, n=1):
        nonlocal p
        v = struct.unpack_from(e + fmt * n, data, p)
        out.extend(struct.pack('<' + fmt * n, *v))
        p += struct.calcsize('<' + fmt * n)
        return v
    typ, nb = take('H', 2)
    desc = take('H', nb)
    length, = take('H')
    out.extend(data[p:p + 2]); p += 2                        # shift, fshift bytes
    nf, = take('H')
    take('f', nf)
    for d in desc:
        take('h', 3) if 4 <= d <= 7 else take('f', 3)
    nk = (length + 14) >> 4
    kofs = take('I', nk)
    end = p + (max(kofs) if kofs else 0) + 4096                # keyframe blocks follow; copy generously
    out.extend(data[p:min(end, len(data))])
    return bytes(out)


def q_axis_angle(X, Y, Z):
    """The 0x64 rotation (read from the exe, docs/anim/T7-0x64-FRAME-RESEARCH-2026-10-30.md)."""
    ax = np.array([math.cos(X) * math.sin(Y), -math.sin(X), math.cos(X) * math.cos(Y)])
    return np.r_[ax * math.sin(Z / 2), math.cos(Z / 2)]


def selftest(exe):
    S = Sampler(exe)
    rng = np.random.default_rng(1)
    print('0xC8 single-axis probes (game output quaternion x,y,z,w):')
    for name, v in (('X', (0.6, 0, 0)), ('Y', (0, 0.6, 0)), ('Z', (0, 0, 0.6))):
        q, _ = S.sample(c8_clip([[v], [v]]), 0.0)
        print('  %s=0.6 -> %s' % (name, np.round(q[0], 5)))
    return S


if __name__ == '__main__':
    if len(sys.argv) >= 3 and sys.argv[2] == 'selftest':
        selftest(sys.argv[1])
    else:
        print(__doc__)
