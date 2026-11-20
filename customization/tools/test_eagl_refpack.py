"""Tests for eagl_refpack (run by filename: python3 -m pytest test_eagl_refpack.py)."""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from eagl_refpack import refpack_decompress, find_refpack_offset, RefPackError


def test_literal_only_stream():
    # header: 10 FB + 3-byte BE size (8); two literal ops (0xE0 = 4 bytes each); stop 0xFC
    stream = bytes([0x10, 0xFB, 0, 0, 8, 0xE0]) + b"ABCD" + bytes([0xE0]) + b"EFGH" + bytes([0xFC])
    assert refpack_decompress(stream) == b"ABCDEFGH"


def test_back_reference_stream():
    # literal "ABCD", then 2-byte op b1=0x04,b2=0x03: plain=0, copy=4, offset=4 -> "ABCD" again
    stream = bytes([0x10, 0xFB, 0, 0, 8, 0xE0]) + b"ABCD" + bytes([0x04, 0x03, 0xFC])
    assert refpack_decompress(stream) == b"ABCDABCD"


def test_rejects_non_refpack():
    try:
        refpack_decompress(b"\x00\x01\x02\x03\x04\x05")
    except RefPackError:
        return
    raise AssertionError("expected RefPackError")


def test_find_offset_with_prefix():
    stream = b"\x00" * 8 + bytes([0x10, 0xFB, 0, 0, 4, 0xE0]) + b"WXYZ" + bytes([0xFC])
    assert find_refpack_offset(stream) == 8
    assert refpack_decompress(stream[8:]) == b"WXYZ"
