#!/usr/bin/env python3
"""Build the hybrid KC2FIRE.000 for the JP/EN toggle (M3).

The hybrid pack keeps the Japanese originals at their own indices and appends
English variants of every group that contains a translated entry, after the
last group. The toggle hook (tools/toggle_patch.py) redirects loads of
affected entries to their mirrors when the flag is EN.

Layout rules (docs/TECHNICAL.md, enforced by pak.layout_errors):
every group starts on a sector and spans whole sectors; entries are
0x80-aligned and contiguous within their group. Mirror groups are laid out
in original group order, entries in original order, so mirror index =
MIRROR_BASE + position in the affected list.

Usage:
  hybrid_pack.py <original.000> <english.000> <hybrid.000> [affected.json]
Writes the hybrid pack and (unless given) the affected-entry list as JSON.
"""
import json
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'sources' / 'kactusken' / 'repo' / 'tools'))
import pak  # noqa: E402

SECTOR = 0x800
ENTRY_ALIGN = 0x80


def build_hybrid(orig_bytes, en_bytes):
    """(hybrid bytes, affected list, mirror_base, changed list)."""
    orig = pak.Pak(orig_bytes)
    en = pak.Pak(en_bytes)
    if len(orig.entries) != len(en.entries):
        raise SystemExit(f'packs differ in entry count: {len(orig.entries)} vs {len(en.entries)}')
    changed = [k for k in range(len(orig.entries)) if orig.raw(k) != en.raw(k)]
    changed_set = set(changed)
    groups = pak.groups(orig.entries)
    affected_groups = [(f, l) for f, l in groups if any(f <= c <= l for c in changed)]
    affected = sorted(k for f, l in affected_groups for k in range(f, l + 1))
    mirror_base = len(orig.entries)
    n_new = mirror_base + len(affected)

    new_base = pak.align(8 + 16 * n_new, SECTOR)
    old_base, old_end = orig.base, orig.end()

    # mirror records + data, group by group, in original order
    mirror_records = {}  # affected entry -> (offset, stored, size, flags)
    mirror_data = bytearray()
    # the original data end is sector-aligned (last group spans whole sectors);
    # mirror offsets count from the new base, so the first mirror entry starts
    # at (old_end - old_base) + (new_base - old_base)... no: offsets are
    # base-relative, and the original data keeps its offsets, so the mirror
    # area starts right after the original data end, base-relative:
    cursor = old_end - old_base
    assert cursor % SECTOR == 0, f'original data end not sector-aligned: {cursor:#x}'
    for f, l in affected_groups:
        group_start = cursor
        blocks = []
        for k in range(f, l + 1):
            if k in changed_set:
                blocks.append((k, en.raw(k), en.entries[k]))
            else:
                blocks.append((k, orig.raw(k), orig.entries[k]))
        span = sum(len(b) for _, b, _ in blocks)
        pad = pak.align(span, SECTOR) - span
        pos = group_start
        for i, (k, block, rec) in enumerate(blocks):
            stored = len(block) + (pad if i == len(blocks) - 1 else 0)
            mirror_records[k] = (pos, stored, rec[2], rec[3])
            pos += stored
        body = b''.join(b for _, b, _ in blocks) + bytes(pad)
        assert len(body) == pos - group_start
        mirror_data += body
        cursor = pos

    # assemble: header + table (zero-padded to new_base) + original data + mirror data
    out = bytearray()
    out += struct.pack('<II', 0x800, n_new)
    records = list(orig.entries)
    for k in affected:
        records.append(mirror_records[k])
    assert len(records) == n_new
    out += b''.join(struct.pack('<4I', *r) for r in records)
    out += bytes(new_base - len(out))
    assert len(out) == new_base
    out += orig_bytes[old_base:old_end]
    out += mirror_data
    return bytes(out), affected, mirror_base, changed


def verify(hybrid_bytes, orig_bytes, en_bytes, affected, mirror_base, changed):
    """Structural checks: layout rules, originals intact, mirrors match EN."""
    errors = pak.layout_errors(hybrid_bytes)
    if errors:
        return [f'layout: {e}' for e in errors[:10]]
    hyb, orig, en = pak.Pak(hybrid_bytes), pak.Pak(orig_bytes), pak.Pak(en_bytes)
    problems = []
    if len(hyb.entries) != len(orig.entries) + len(affected):
        problems.append(f'entry count {len(hyb.entries)} != {len(orig.entries)} + {len(affected)}')
    for k in range(len(orig.entries)):
        if hyb.raw(k) != orig.raw(k):
            problems.append(f'original entry {k} changed')
            if len(problems) > 5:
                return problems
    pos = {k: i for i, k in enumerate(affected)}
    for k in changed:
        if hyb.get(mirror_base + pos[k]) != en.get(k):
            problems.append(f'mirror of changed entry {k} does not match EN')
            if len(problems) > 5:
                return problems
    for k in affected:
        if k not in changed and hyb.raw(mirror_base + pos[k]) != orig.raw(k):
            problems.append(f'mirror of unchanged entry {k} does not match original')
            if len(problems) > 5:
                return problems
    return problems


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if len(argv) < 3:
        print(__doc__)
        return 1
    orig_b = Path(argv[0]).read_bytes()
    en_b = Path(argv[1]).read_bytes()
    hybrid, affected, mirror_base, changed = build_hybrid(orig_b, en_b)
    problems = verify(hybrid, orig_b, en_b, affected, mirror_base, changed)
    if problems:
        print('VERIFY FAILED:')
        for p in problems:
            print('  ' + p)
        return 1
    Path(argv[2]).write_bytes(hybrid)
    info = {'changed': changed, 'affected': affected, 'mirror_base': mirror_base,
            'hybrid_size': len(hybrid), 'original_size': len(orig_b)}
    Path(argv[3] if len(argv) > 3 else 'hybrid-info.json').write_text(json.dumps(info))
    print(f'hybrid pack: {len(hybrid)} bytes ({len(hybrid) - len(orig_b):+,} vs original), '
          f'{len(affected)} mirror entries, {len(changed)} changed entries; '
          f'layout + mirrors verified')
    return 0


if __name__ == '__main__':
    sys.exit(main())
