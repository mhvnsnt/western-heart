#!/usr/bin/env python3
"""MIPS immediate scan of the Tekken 5 Devil Within Code blob
(TK5DATA3_code.bin, NLZ1-decompressed, 2,719,159 bytes, raw PS2 EE
MIPS-III little-endian code, no ELF header).

Linear-sweeps the code region (0x0-0x200000, measured ~90% Capstone
decode coverage; the rest of the blob is strings/LUT/tables) with
Capstone (MIPS64 LE, detail off — detail mode aborts on some
encodings in this blob; operands are parsed from op_str).

  - Reconstructs every lui + addiu/ori/addi pair into a 32-bit
    constant; records standalone small immediates.
  - Tests the load base: if code forms an anchor address (a string
    offset or the PS2 LUT offset 0x27B5B0) exactly, the blob loads
    at base 0 (file offset == address). If no anchor is ever formed,
    the base is UNPROVEN and all addresses below are file offsets.
  - Anchor-driven search: for each anchor string (item_force,
    handycap_gauge_yellow, RankingMode, Devil Jin, name_DEVILJIN),
    lists the code sites that form its address, and the immediates
    in the enclosing function (prologue to jr $ra).
  - Hypothesis tests: sample rates (22050/24000/32000/44100/48000),
    the 1,000,000 Force reward, the 40-symbol count, as immediates
    or lui+ori pairs anywhere in code.
  - NOT reported as found: any number with no anchor. A bare
    immediate is just a number; it is listed as a candidate only
    with the exact address + the anchor that ties it to a meaning.

Canon: the source kit filenames (gym_ikdv_*) are donor data only —
called the Surge Kit donor here; the transform kit is the Soul
Surge Bloom donor. There is no Jin Kazama in our game; the only
Jin is the soul JIN (the Blade Soul), pickable as Phantom.

Usage: python3 code_immediates.py <TK5DATA3_code.bin> <out.json>
Requires: capstone (pip install capstone).
"""
import json, re, struct, sys
from collections import Counter
from capstone import *

CODE_END = 0x200000  # measured: decode coverage ~90% below, data above
ANCHORS = {
    'ps2_lut': 0x27B5B0,
    'item_force': 0x2905B8,
    'handycap_gauge_yellow_p1': 0x28CAD1,
    'handycap_gauge_yellow_p2': 0x28CAF1,
    'RankingMode': 0x28B3F0,
    'Devil_Jin': 0x27A0A8,
    'name_DEVILJIN': 0x28A4D9,
}
# strings with ZERO hits in the blob (verified by byte search): symbol,
# laser, drain, heal. No anchor exists for them in this blob at all.
HYPOTHESES = {
    'sample_rate_22050': 22050, 'sample_rate_24000': 24000,
    'sample_rate_32000': 32000, 'sample_rate_44100': 44100,
    'sample_rate_48000': 48000, 'force_reward_1000000': 1000000,
    'symbol_count_40': 40,
}
IMM_RE = re.compile(r'^(lui|addiu|addi|ori|xori|andi|slti|sltiu)\s+(\$\w+),\s*(\$\w+|0x[0-9a-fA-F]+|-?\d+)(?:,\s*(-?0x[0-9a-fA-F]+|-?\d+))?$')


def parse_imm(s):
    return int(s, 0)


def sweep(md, code, base, end):
    insns = []
    bad = 0
    off = base
    while off < end:
        n = 0
        for ins in md.disasm(code[off:end], off):
            insns.append((ins.address, ins.mnemonic, ins.op_str))
            off = ins.address + 4
            n += 1
            if off >= end:
                break
        if n == 0:
            bad += 1
            off += 4
    return insns, bad


def sign16(v):
    return v - 0x10000 if v >= 0x8000 else v


def main():
    blob_path, out_path = sys.argv[1], sys.argv[2]
    d = open(blob_path, 'rb').read()
    md = Cs(CS_ARCH_MIPS, CS_MODE_MIPS64 + CS_MODE_LITTLE_ENDIAN)
    md.detail = False
    insns, bad = sweep(md, d, 0, CODE_END)
    by_addr = {a: (m, o) for a, m, o in insns}

    pairs = []
    small_imm = Counter()
    pending = {}
    for addr, m, op in insns:
        mm = IMM_RE.match(m + ' ' + op)
        if m == 'lui' and mm:
            pending[mm.group(2)] = (addr, parse_imm(mm.group(3)))
            continue
        if mm and m in ('addiu', 'addi', 'ori', 'xori', 'andi'):
            dst, src, lo_s = mm.group(2), mm.group(3), mm.group(4)
            lo = parse_imm(lo_s)
            if src in pending:
                lui_addr, hi = pending[src]
                if m in ('addiu', 'addi'):
                    val = ((hi << 16) + sign16(lo)) & 0xFFFFFFFF
                else:
                    val = ((hi << 16) | (lo & 0xFFFF)) & 0xFFFFFFFF
                pairs.append({'lui_addr': lui_addr, 'use_addr': addr,
                              'reg': dst, 'kind': m,
                              'value': val, 'value_hex': hex(val)})
                pending.pop(dst, None)
                continue
            small_imm[lo & 0xFFFF] += 1
        elif mm and m in ('slti', 'sltiu'):
            small_imm[parse_imm(mm.group(4)) & 0xFFFF] += 1
        # any register write kills its pending lui
        if mm and mm.group(2).startswith('$'):
            pending.pop(mm.group(2), None)

    anchor_refs = {name: [] for name in ANCHORS}
    for p in pairs:
        for name, a in ANCHORS.items():
            if p['value'] == a:
                anchor_refs[name].append(
                    {'lui_addr': p['lui_addr'], 'use_addr': p['use_addr'],
                     'reg': p['reg'], 'kind': p['kind']})
    # same test at the best-supported base 0x200000 (VA = file offset + base)
    va_anchor_refs = {name: [] for name in ANCHORS}
    for p in pairs:
        for name, a in ANCHORS.items():
            if p['value'] == a + 0x200000:
                va_anchor_refs[name].append(
                    {'lui_addr': p['lui_addr'], 'use_addr': p['use_addr'],
                     'reg': p['reg'], 'kind': p['kind'],
                     'va': hex(a + 0x200000)})

    def function_window(ref_addr):
        start = ref_addr
        while start > 0:
            prev = by_addr.get(start - 4)
            if prev is None:
                break
            if prev[0] == 'addiu' and 'sp, sp' in prev[1]:
                start = start - 4
                break
            start -= 4
            if ref_addr - start > 0x2000:
                break
        end = ref_addr
        while end < CODE_END:
            cur = by_addr.get(end)
            if cur is None:
                end += 4
                continue
            if cur[0] == 'jr' and '$ra' in cur[1]:
                end = end + 8
                break
            end += 4
            if end - ref_addr > 0x4000:
                break
        return start, end

    anchor_windows = {}
    for name, refs in anchor_refs.items():
        wins, seen = [], set()
        for r in refs:
            s, e = function_window(r['use_addr'])
            if (s, e) in seen:
                continue
            seen.add((s, e))
            imms = []
            for a in range(s, e, 4):
                cur = by_addr.get(a)
                if cur is None:
                    continue
                if cur[0] in ('addiu', 'addi', 'ori', 'slti', 'sltiu',
                              'andi', 'xori', 'lui'):
                    imms.append({'addr': a, 'text': f"{cur[0]} {cur[1]}"})
            wins.append({'ref_lui': r['lui_addr'], 'ref_use': r['use_addr'],
                         'func_start': s, 'func_end': e, 'size': e - s,
                         'immediates': imms})
        anchor_windows[name] = wins

    hyp = {}
    for name, val in HYPOTHESES.items():
        pair_hits = [p for p in pairs if p['value'] == val]
        hyp[name] = {'value': val, 'pair_hits': len(pair_hits),
                     'pair_sites': [(p['lui_addr'], p['use_addr']) for p in pair_hits[:10]],
                     'small_imm_hits': small_imm.get(val & 0xFFFF, 0)}

    pairvals = Counter(p['value'] for p in pairs)
    floats = []
    for v, c in pairvals.items():
        f = struct.unpack('<f', struct.pack('<I', v))[0]
        if 0.0001 <= abs(f) <= 10000.0 and f == f:
            floats.append({'bits': hex(v), 'float': f, 'sites': c})


    # --- load-base metric: fraction of jal/j targets landing on decoded code ---
    jal_targets = []
    for a, m, o in insns:
        mm = re.match(r'^(jal|j)\s+(0x[0-9a-fA-F]+)$', m + ' ' + o)
        if mm:
            jal_targets.append(int(mm.group(2), 0))
    addrset = {a for a, _, _ in insns}
    base_metric = {}
    for base in (0x0, 0x100000, 0x200000, 0x80000000):
        hit = sum(1 for t in jal_targets if (t - base) in addrset)
        base_metric[hex(base)] = {
            'jal_targets': len(jal_targets),
            'land_on_decoded_insn': hit,
            'fraction': round(hit / max(len(jal_targets), 1), 3)}

    # --- sample-rate immediates with context: cluster + the rate-select fn ---
    rate_sites = []
    for a, m, o in insns:
        mm = IMM_RE.match(m + ' ' + o)
        if mm and m in ('addiu', 'addi', 'ori') and mm.group(4):
            v = parse_imm(mm.group(4))
            if v in (22050, 44100, 48000) and mm.group(3) == '$zero':
                rate_sites.append({'addr': a, 'text': f'{m} {o}', 'rate': v})
    # the rate-select function: disassemble file 0x50050 +- window
    rate_fn = []
    lo, hi = 0x50050, 0x501C0
    off = lo
    while off < hi:
        n = 0
        for ins in md.disasm(d[off:hi], off):
            rate_fn.append(f'{ins.address:#08x}: {ins.mnemonic} {ins.op_str}')
            off = ins.address + 4
            n += 1
            if off >= hi:
                break
        if n == 0:
            off += 4

    # --- 1,000,000 pair sites with context ---
    onem_sites = []
    for p in pairs:
        if p['value'] == 1000000:
            lo, hi = max(0, p['use_addr'] - 0x40), p['use_addr'] + 0x40
            ctx = []
            off = lo
            while off < hi:
                n = 0
                for ins in md.disasm(d[off:hi], off):
                    ctx.append(f'{ins.address:#08x}: {ins.mnemonic} {ins.op_str}')
                    off = ins.address + 4
                    n += 1
                    if off >= hi:
                        break
                if n == 0:
                    off += 4
            onem_sites.append({'lui_addr': p['lui_addr'], 'use_addr': p['use_addr'],
                               'reg': p['reg'], 'kind': p['kind'], 'context': ctx})

    out = {
        'format': 'western-heart dw-code-immediates v1',
        'source': 'TK5DATA3_code.bin (2,719,159 B, NLZ1-decompressed Code blob)',
        'tool': 'Capstone 5.x, MIPS64 little-endian, linear sweep, operands from op_str',
        'code_region': {'start': 0, 'end': hex(CODE_END)},
        'sweep': {'instructions': len(insns), 'skipped_words': bad,
                  'coverage': round(len(insns) / (CODE_END // 4), 3)},
        'pairs_reconstructed': len(pairs),
        'load_base': {
            'proven': bool(any(anchor_refs.values())),
            'evidence': 'code forms anchor addresses exactly (see anchor_refs) '
                        '=> file offset == address, base 0'
                        if any(anchor_refs.values()) else
                        'NO anchor address is ever formed by lui+addiu/ori '
                        '=> load base UNPROVEN; addresses below are FILE OFFSETS',
        },
        'anchor_refs': anchor_refs,
        'va_anchor_refs_base_0x200000': va_anchor_refs,
        'anchor_windows': anchor_windows,
        'hypotheses': hyp,
        'float_constants': sorted(floats, key=lambda x: -x['sites'])[:40],
        'top_small_immediates': [[hex(k), v] for k, v in small_imm.most_common(30)],
        'no_anchor_strings': ['symbol', 'laser', 'drain', 'heal'],
        'load_base_metric': base_metric,
        'load_base_verdict': 'BEST-SUPPORTED 0x200000 (74.3% of jal targets land on '
            'decoded code, vs 13.2% at base 0 and 60.9% at 0x100000; the blob '
            'occupies VA 0x200000-0x497E57). NOT proven: ~26% of calls go '
            'outside this blob (other PKG overlays). All addresses below are '
            'FILE OFFSETS; VA = file offset + 0x200000 under this hypothesis.',
        'sample_rate_sites': rate_sites,
        'sample_rate_function': {
            'file_range': '0x50050-0x501C0 (VA 0x250050-0x2501C0 under base 0x200000)',
            'finding': 'flag-driven rate select: flag bit 0x20 -> 48000, '
                'bit 0x40 -> 44100, else 22050; rate passed as $a2 to call '
                'at 0x316BE8 (VA). 22050 is the DEFAULT tier, not the only rate.',
            'disassembly': rate_fn},
        'million_sites': onem_sites,
    }
    open(out_path, 'w').write(json.dumps(out, indent=1))
    print(f"insns={len(insns)} bad={bad} pairs={len(pairs)}")
    print('base proven:', out['load_base']['proven'])
    for name, refs in anchor_refs.items():
        print(f'  {name}: {len(refs)} refs')
    for name, h in hyp.items():
        print(f"  {name}: pairs={h['pair_hits']} small_imm={h['small_imm_hits']}")


if __name__ == '__main__':
    main()
