#!/usr/bin/env python3
"""VPW2 sound extraction: 8 N64 PtrTablesV2 banks -> WAVs + music sequences.

Adapted from the No Mercy lane's full_pass.py (which ported SubDrag's
N64SoundLibrary N64AIFCAudio.cpp ReadAudioN64PtrWavetableV2 + decode/decode_8).

VPW2 layout (decomp extract_baserom.sh + VPWStudio soundtool.txt agree):
  sndtblN_ptr.bin = control ("N64 PtrTablesV2", 0x30 header)
  sndtblN_wbk.bin = wave data ("N64 WaveTables" header, waves at wav_base)
  sndtblN_tbl.bin = separate small table (recorded raw; role not decoded)
Table 8 has no .tbl blob. Waves are VADPCM @ 22,050 Hz mono s16.

Music sequences: 19 Binary files 0x034C-0x035E labeled "[Music Data]".
Sng->MIDI conversion needs SubDrag's N64MidiTool (Windows GUI) -- same gap
as the No Mercy lane; sequences are dumped raw as .sng.

Usage: python3 vpw2_sound.py   (run from vpw2/tools/)
Outputs: vpw2/extracted/sound/bankN/*.wav, sequences/*.sng, sound.json
"""
import json
import os
import struct
import wave

HERE = os.path.dirname(os.path.abspath(__file__))
VPW2 = os.path.dirname(HERE)
SND = os.path.join(VPW2, 'extracted', 'sound')
RAW = os.path.join(VPW2, 'extracted', 'raw')

BANKS = [
    # (bank, ptr_off, wbk_off, tbl_off or None) -- ROM offsets from decomp
    (1, 0x133AC80, 0x133CE10, 0x144E0A0),
    (2, 0x144FD30, 0x1454C20, 0x156E7D0),
    (3, 0x156EA30, 0x156F2E0, 0x1C97400),
    (4, 0x1C98A10, 0x1C9C700, 0x1D0AC40),
    (5, 0x1D0C170, 0x1D0FB10, 0x1E47EF0),
    (6, 0x1E487B0, 0x1E49FB0, 0x1E90030),
    (7, 0x1E90700, 0x1E930D0, 0x1EDC410),
    (8, 0x1EDCAE0, 0x1EDF4B0, None),
]

# ---------------- VADPCM (port of N64SoundLibrary decode/decode_8) ----------------
ITABLE = [0, 1, 2, 3, 4, 5, 6, 7, -8, -7, -6, -5, -4, -3, -2, -1]


def sign_extend(b, x):
    x &= (1 << b) - 1
    m = 1 << (b - 1)
    return (x ^ m) - m


def _decode_8(data, pos, out, index, pred1, lastsmp):
    pred2 = pred1[8:16]
    tmp = []
    p = pos
    for i in range(8):
        if i & 1:
            nib = data[p] & 0x0F
            p += 1
        else:
            nib = (data[p] >> 4) & 0x0F
        tmp.append(sign_extend(index + 4, ITABLE[nib] << index))
    for i in range(8):
        total = pred1[i] * lastsmp[6] + pred2[i] * lastsmp[7]
        for x in range(i - 1, -1, -1):
            total += tmp[(i - 1) - x] * pred2[x]
        v = ((tmp[i] << 11) + total) >> 11
        out.append(-32768 if v < -32768 else (32767 if v > 32767 else v))
    lastsmp[:] = out[-8:]
    return p


def vadpcm_decode(data, book_order, book_npred, predictors):
    """data: VADPCM bytes (multiple of 9). Returns list of s16 samples."""
    out = []
    lastsmp = [0] * 8
    n = (len(data) // 9) * 9
    i = 0
    while i < n:
        hdr = data[i]
        index = (hdr >> 4) & 0xF
        pred = (hdr & 0xF) % max(1, book_npred)
        pred1 = predictors[pred * 16:pred * 16 + 16]
        i = _decode_8(data, i + 1, out, index, pred1, lastsmp)
        i = _decode_8(data, i, out, index, pred1, lastsmp)
    return out


def write_wav(path, samples, rate=22050):
    with wave.open(path, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(struct.pack('<%dh' % len(samples), *samples))


# ---------------- bank parsing ----------------
def parse_bank(ctl, wbk, bank_name):
    """ctl: ptr blob, wbk: wave blob. Returns manifest dict."""
    assert ctl[:15] == b'N64 PtrTablesV2', f'bad ptr magic in {bank_name}'
    assert wbk[:14] == b'N64 WaveTables', f'bad wbk magic in {bank_name}'
    name = ctl[0x14:0x20].split(b'\x00')[0].decode('ascii', 'replace')
    count = struct.unpack('>I', ctl[0x20:0x24])[0]
    end_offsets = struct.unpack('>I', ctl[0x24:0x28])[0]
    end_extra = struct.unpack('>I', ctl[0x28:0x2C])[0]
    bank_offset = struct.unpack('>I', ctl[0x2C:0x30])[0]
    entries = []
    for x in range(count):
        ioff = struct.unpack('>I', ctl[bank_offset + x * 4:
                                       bank_offset + x * 4 + 4])[0]
        vol = ctl[end_offsets + x] if end_offsets + x < len(ctl) else None
        pan = ctl[end_extra + x] if end_extra + x < len(ctl) else None
        if ioff == 0:
            entries.append({'index': x, 'empty': True,
                            'volume': vol, 'pan': pan})
            continue
        base, ln = struct.unpack('>II', ctl[ioff:ioff + 8])
        loop_off, pred_off = struct.unpack('>II', ctl[ioff + 0xC:ioff + 0x14])
        loop = None
        if loop_off:
            ls, le, lc = struct.unpack('>III', ctl[loop_off:loop_off + 12])
            loop = {'start': ls, 'end': le, 'count': lc}
        book = None
        if pred_off:
            order, npred = struct.unpack('>II', ctl[pred_off:pred_off + 8])
            ncoef = order * npred * 8
            coefs = list(struct.unpack('>%dh' % ncoef,
                                       ctl[pred_off + 8:
                                           pred_off + 8 + ncoef * 2]))
            book = {'order': order, 'npredictors': npred,
                    'predictors': coefs}
        entries.append({'index': x, 'empty': False, 'volume': vol,
                        'pan': pan, 'wav_base': base, 'wav_len': ln,
                        'loop': loop, 'book': book, 'ctl_offset': ioff})
    return {'bank': bank_name, 'name': name, 'count': count,
            'ctl_size': len(ctl), 'wbk_size': len(wbk), 'entries': entries}


def main():
    manifest = {'banks': [], 'sequences': []}
    total_wavs = 0
    total_seconds = 0.0
    for n, ptr_off, wbk_off, tbl_off in BANKS:
        bname = f'bank{n}'
        ctl = open(os.path.join(SND, f'sndtbl{n}_ptr.bin'), 'rb').read()
        wbk = open(os.path.join(SND, f'sndtbl{n}_wbk.bin'), 'rb').read()
        info = parse_bank(ctl, wbk, bname)
        info['ptr_offset'] = hex(ptr_off)
        info['wbk_offset'] = hex(wbk_off)
        info['tbl_offset'] = hex(tbl_off) if tbl_off else None
        outdir = os.path.join(SND, bname)
        os.makedirs(outdir, exist_ok=True)
        n_wav, n_empty, n_nobook = 0, 0, 0
        bank_seconds = 0.0
        peak = 0
        for e in info['entries']:
            if e['empty']:
                n_empty += 1
                continue
            base, ln = e['wav_base'], e['wav_len']
            blob = wbk[base:base + ln]
            book = e['book']
            if book is None:
                n_nobook += 1
                samples = []
            else:
                samples = vadpcm_decode(blob, book['order'],
                                        book['npredictors'],
                                        book['predictors'])
            fn = f'{bname}_{e["index"]:03d}.wav'
            write_wav(os.path.join(outdir, fn), samples)
            if samples:
                peak = max(peak, max(abs(s) for s in samples))
            e['file'] = fn
            e['samples'] = len(samples)
            e['duration_s'] = round(len(samples) / 22050, 3)
            if book:
                e['adpcm_order'] = book['order']
                e['adpcm_npredictors'] = book['npredictors']
            del e['book']
            bank_seconds += e['duration_s']
            n_wav += 1
        info['wavs'] = n_wav
        info['empty_slots'] = n_empty
        info['no_predictor_book'] = n_nobook
        info['total_seconds'] = round(bank_seconds, 1)
        info['peak_amplitude'] = peak
        manifest['banks'].append(info)
        total_wavs += n_wav
        total_seconds += bank_seconds
        print(f'sound {bname}: {info["count"]} slots, {n_wav} WAVs, '
              f'{n_empty} empty, {n_nobook} no-book, '
              f'{bank_seconds:.1f}s, peak {peak}')

    # ---- music sequences: files 0x034C-0x035E ----
    seqdir = os.path.join(SND, 'sequences')
    os.makedirs(seqdir, exist_ok=True)
    labels = {}
    db = os.path.join(os.path.dirname(VPW2), 'pulls', 'VPWStudio',
                      'VPWStudio', 'VPWStudio', 'FileTableDB', 'VPW2.txt')
    import re
    for line in open(db):
        m = re.match(r'([0-9A-Fa-f]{2,})=([A-Za-z0-9_]+);(.*)$', line.strip())
        if m:
            labels[int(m.group(1), 16)] = m.group(3)
    for fid in range(0x034C, 0x035F):
        blob = open(os.path.join(RAW, f'{fid:04X}.bin'), 'rb').read()
        fn = f'seq_{fid:04X}.sng'
        open(os.path.join(seqdir, fn), 'wb').write(blob)
        manifest['sequences'].append({
            'file_id': f'{fid:04X}', 'file': fn, 'len': len(blob),
            'magic': blob[:4].hex(), 'label': labels.get(fid, '')})
    print(f'sequences: 19 .sng dumped')
    json.dump(manifest, open(os.path.join(SND, 'sound.json'), 'w'), indent=1)
    print(f'TOTAL: {total_wavs} WAVs, {total_seconds:.1f}s')


if __name__ == '__main__':
    main()
