#!/usr/bin/env python3
"""Oodle Kraken decompression via the open-source ooz library.

The WWE 2K games compress chunks with RAD Game Tools' Oodle Kraken
algorithm. ooz (github.com/zao/ooz) is a clean-room, open-source
reimplementation of the Kraken decoder. Build it with install.sh
(it produces ooz/build/liblibooz.so and the `ooz` command-line tool).

This module prefers the shared library (ctypes, fast, no process
spawn); if the library is missing it falls back to shelling out to
the `ooz` binary.
"""

import ctypes
import os
import subprocess
import tempfile

_HERE = os.path.dirname(os.path.abspath(__file__))

_LIB_NAMES = [
    os.path.join(_HERE, "ooz", "build", "liblibooz.so"),
    os.path.join(_HERE, "liblibooz.so"),
    "liblibooz.so",
]

_BIN_NAMES = [
    os.path.join(_HERE, "ooz", "build", "ooz"),
    "ooz",
]

_lib = None
for _path in _LIB_NAMES:
    try:
        _lib = ctypes.CDLL(_path)
        break
    except OSError:
        continue

if _lib is not None:
    # int Ooz_Decompress(src, src_len, dst, dst_size, a,b,c,d,e,f,g,h,i,j)
    # (OodleLZ_Decompress-compatible signature; only the first four
    # arguments matter to the clean-room decoder.)
    _lib.Ooz_Decompress.argtypes = [
        ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_size_t,
        ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_char_p,
        ctypes.c_size_t, ctypes.c_void_p, ctypes.c_void_p,
        ctypes.c_void_p, ctypes.c_size_t, ctypes.c_int,
    ]
    _lib.Ooz_Decompress.restype = ctypes.c_int


def _decompress_lib(stream, out_len):
    out = ctypes.create_string_buffer(out_len + 64)  # decoder writes past end
    got = _lib.Ooz_Decompress(stream, len(stream), out, out_len,
                              0, 0, 0, None, 0, None, None, None, 0, 0)
    if got < 0:
        raise ValueError("Ooz_Decompress failed")
    return bytes(out.raw[:got])


def _find_ooz_bin():
    for path in _BIN_NAMES:
        if os.path.isfile(path) and os.access(path, os.X_OK):
            return path
    return None


def _decompress_cli(stream, out_len):
    exe = _find_ooz_bin()
    if exe is None:
        raise RuntimeError(
            "no Oodle decoder available: build libooz (install.sh) or "
            "put the `ooz` binary on PATH")
    with tempfile.TemporaryDirectory() as tmp:
        src = os.path.join(tmp, "in.bin")
        dst = os.path.join(tmp, "out.bin")
        with open(src, "wb") as f:
            f.write(stream)
        # ooz expects the raw Kraken stream; -d decompresses.
        subprocess.run([exe, "-d", "-f", src, dst], check=True,
                       capture_output=True)
        with open(dst, "rb") as f:
            return f.read()


def decompress(stream, out_len):
    """Decompress one raw Kraken stream to out_len bytes."""
    if _lib is not None:
        return _decompress_lib(stream, out_len)
    return _decompress_cli(stream, out_len)


def available():
    return _lib is not None or _find_ooz_bin() is not None
