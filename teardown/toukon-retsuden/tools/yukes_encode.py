#!/usr/bin/env python3
"""Re-encode a TIM using Yuke's ORIGINAL BPE dictionaries (byte-identical).

BREAKTHROUGH (test BE, 2026-11-20): the game's BPE decoder mishandles
dictionaries produced by our emit_dict for CHANGED pixel data (though it
handles them for original data). The fix: reuse the original section's
dictionaries byte-for-byte, and re-encode ONLY the block data via DP
(shortest-path) using the original pairs. The section's dictionaries,
block count, and block output lengths are preserved exactly.

Usage:
  python3 yukes_encode.py <orig_section.bin> <new_tim.bin> <out_section.bin>
  (orig section and new TIM must have the same decompressed size)
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from bpe import decompress_section
from bpe_compress import dummy_block, split_padding


def parse_blocks(sec):
    """Parse a BPE section into (dict_bytes, dict1, dict2, bdata, out_len) per block."""
    payload = sec[16:]
    pos = 0
    blocks = []
    while pos < len(payload):
        dstart = pos
        dict1 = list(range(256))
        dict2 = list(range(256))
        i = 0
        while i < 0x100:
            num = payload[pos]
            pos += 1
            if num > 0x7F:
                i += num - 0x7F
                num = 0
                if i == 0x100:
                    break
            for _ in range(num + 1):
                a = payload[pos]
                pos += 1
                if a != i:
                    b = payload[pos]
                    pos += 1
                    dict1[i] = a
                    dict2[i] = b
                i += 1
                if i >= 0x100:
                    break
        dend = pos
        blen = payload[pos] | (payload[pos + 1] << 8)
        pos += 2
        bdata = payload[pos:pos + blen]
        pos += blen
        # Compute this block's output length by simulating the decoder
        heap = []
        src = 0
        out_len = 0
        while src < len(bdata) or heap:
            if heap:
                x = heap.pop()
            else:
                x = bdata[src]
                src += 1
            a = dict1[x]
            if a == x:
                out_len += 1
            else:
                heap.append(dict2[x])
                heap.append(a)
        blocks.append((payload[dstart:dend], dict1, dict2, bdata, out_len))
    return blocks


def build_reverse_map(dict1, dict2):
    """Build byte-sequence -> code map from a dictionary."""
    pairs = {c: (dict1[c], dict2[c]) for c in range(256) if dict1[c] != c}
    memo = {}

    def expand(c):
        if c not in pairs:
            return bytes([c])
        if c in memo:
            return memo[c]
        a, b = pairs[c]
        memo[c] = expand(a) + expand(b)
        return memo[c]

    rev = {}
    for c in range(256):
        rev.setdefault(expand(c), c)
    return rev


def dp_encode(chunk, rev):
    """Encode chunk with the reverse map via DP (shortest path). Returns bytes or None."""
    maxlen = max(len(k) for k in rev)
    n = len(chunk)
    INF = 10 ** 9
    dp = [INF] * (n + 1)
    dp[n] = 0
    choice = [None] * n
    for i in range(n - 1, -1, -1):
        for ln in range(1, min(maxlen, n - i) + 1):
            seq = chunk[i:i + ln]
            if seq in rev and dp[i + ln] + 1 < dp[i]:
                dp[i] = dp[i + ln] + 1
                choice[i] = (ln, rev[seq])
    if dp[0] >= INF:
        return None
    out = bytearray()
    i = 0
    while i < n:
        ln, code = choice[i]
        out.append(code)
        i += ln
    return bytes(out)


def reencode(orig_section, new_tim, target_len):
    """Re-encode new_tim with orig_section's dictionaries. Returns section bytes or raises."""
    blocks = parse_blocks(orig_section)
    total_out = sum(b[4] for b in blocks)
    assert total_out == len(new_tim), f"output {total_out} != TIM {len(new_tim)}"
    payload = bytearray()
    pos = 0
    for bi, (dbytes, d1, d2, orig_bdata, out_len) in enumerate(blocks):
        chunk = new_tim[pos:pos + out_len]
        pos += out_len
        if chunk == decompress_section(orig_section)[pos - out_len:pos]:
            # Unchanged chunk: reuse original block data verbatim
            payload += dbytes
            payload += struct.pack("<H", len(orig_bdata))
            payload += orig_bdata
        else:
            rev = build_reverse_map(d1, d2)
            enc = dp_encode(chunk, rev)
            if enc is None:
                raise ValueError(f"block {bi}: chunk not encodable with original dict")
            payload += dbytes
            payload += struct.pack("<H", len(enc))
            payload += enc
    need = (target_len - 16) - len(payload)
    if need < 0:
        raise ValueError(f"encoded payload {len(payload)}B exceeds target {target_len - 16}B by {-need}B")
    if need > 0:
        for s in split_padding(need):
            payload += dummy_block(s)
    sec = b"BPE " + struct.pack("<III", 0x100, len(payload), len(new_tim)) + bytes(payload)
    assert len(sec) == target_len, f"section {len(sec)}B != target {target_len}B"
    assert decompress_section(sec) == new_tim, "roundtrip FAILED"
    return sec


if __name__ == "__main__":
    orig = Path(sys.argv[1]).read_bytes()
    tim = Path(sys.argv[2]).read_bytes()
    target = int(sys.argv[3]) if len(sys.argv) > 3 else len(orig)
    out = reencode(orig, tim, target)
    Path(sys.argv[4] if len(sys.argv) > 4 else "/tmp/out.sec").write_bytes(out)
    print(f"OK: {len(out)}B (target {target}B)")
