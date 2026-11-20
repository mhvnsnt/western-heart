#!/usr/bin/env python3
"""Decode Tekken 5 Devil Within P3Dp audio payloads (snd_*.dat).

Measured P3Dp layout (validated on all 17 P3Dp files):
  file: 'P3Dp' magic + 16-byte header of u16s:
    [0]=0x0A01, [1]=id (1..20), [2]=clip count, [3]=clips*104+16,
    [4]=unresolved, [5]=1..6, [6]=0, [7]=mostly 4.
  clip table at +20: clip_count records of 80 bytes (20 u32s):
    [0]=0x0100647F/0x0101647F, [1]=0xFFFF mostly, [3]=0xD mostly,
    [5]=unresolved, [6]=unresolved, [7]=pan/volume pair,
    [10]=[15]=[16]=1.0f, [11]=0x5FCC00FF/0x5FCD00FF,
    [13]=clip byte size, [14]=clip start offset (payload-relative),
    [19]=0x40000+clip index. Clips SHARE payload regions: several
    records point at the same (start, size) — same sample, different
    playback parameters. [14] is NOT a cumulative chain.
  then 24-byte records of 6 floats (180, 1, 30, 5, 30, 180) repeated
  clip_count times (constant parameter block, unresolved), then the
  payload: raw PS2 VAG ADPCM, 16-byte frames, starting 13 bytes after
  the table end (alignment verified per file by frame-header scoring).
  Frame: [0]=(filter<<4)|shift, [1]=flags (0 normal, 1 end),
  [2..15]=28 4-bit samples. Decoded with ffmpeg's standard adpcm_psx
  decoder via a synthetic VAGp header (48 bytes).
  Sample rate is NOT in the bytes: decoded at 22050 Hz, the standard
  PS2 sound-effect rate — ASSUMED, to be confirmed against the game
  code (Job 3). Durations/RMS below are at that rate.

Usage: python3 snd_decode.py <romd_out_dir> <out.json> [proof_wav_dir]
Decodes every unique payload region via ffmpeg (in-memory; only a few
small proof WAVs are written to disk).
"""
import json, math, struct, subprocess, sys
from collections import Counter
from pathlib import Path

RATE = 22050  # ASSUMED standard PS2 SE rate; not in the bytes (see above)

def vagp(raw, rate=RATE, name=b'clip'):
    h = bytearray(48)
    h[0:4] = b'VAGp'
    struct.pack_into('>I', h, 4, 0x20)
    struct.pack_into('>I', h, 12, len(raw))
    struct.pack_into('>I', h, 16, rate)
    h[32:32 + len(name)] = name
    return bytes(h) + raw

def frame_ok(b0):
    # (filter<<4)|shift: filter 0..4, shift 0..12
    return (b0 >> 4) <= 4 and (b0 & 0xF) <= 12

def find_payload_base(d, table_end):
    best = None
    for delta in range(32):
        base = table_end + delta
        ok = 0
        n = 0
        for i in range(1000):
            if base + i * 16 >= len(d):
                break
            n += 1
            if frame_ok(d[base + i * 16]):
                ok += 1
        if best is None or ok > best[1]:
            best = (delta, ok, n)
    return table_end + best[0], best

def decode_vag(raw):
    """Decode raw VAG frames with ffmpeg; return list of s16 samples."""
    p = subprocess.run(
        ['ffmpeg', '-v', 'error', '-i', 'pipe:0',
         '-f', 's16le', '-ac', '1', '-ar', str(RATE), 'pipe:1'],
        input=vagp(raw), capture_output=True)
    if p.returncode != 0:
        raise RuntimeError(f'ffmpeg failed: {p.stderr.decode()[:300]}')
    n = len(p.stdout) // 2
    return struct.unpack(f'<{n}h', p.stdout)

def main():
    romd_dir, out_path = Path(sys.argv[1]), Path(sys.argv[2])
    proof_dir = Path(sys.argv[3]) if len(sys.argv) > 3 else None
    files = []
    tot_clips = tot_unique = tot_samples = 0
    problems = []
    for name in sorted(p.name for p in romd_dir.glob('snd_*.dat')):
        d = (romd_dir / name).read_bytes()
        if d[:4] != b'P3Dp':
            files.append({'source_file': name, 'container': 'NOT P3Dp',
                          'note': 'plain text (sound positions + event '
                                  'script), no audio payload',
                          'clips': []})
            continue
        hdr = struct.unpack_from('<8H', d, 4)
        clips = hdr[2]
        table_end = 20 + (hdr[3] - 16)
        base, (delta, ok, n) = find_payload_base(d, table_end)
        if ok < n:
            problems.append(f'{name}: payload alignment {delta} scores '
                            f'{ok}/{n} valid frames (expected all)')
        recs = []
        for k in range(clips):
            r = struct.unpack_from('<20I', d, 20 + 80 * k)
            recs.append({'index': k, 'clip_id': r[19],
                         'size_bytes': r[13], 'start': r[14],
                         'field5': r[5], 'field6': r[6], 'field7': r[7]})
        # unique payload regions (shared samples decoded once)
        uniq = {}
        for r in recs:
            uniq.setdefault((r['start'], r['size_bytes']), []).append(r['index'])
        decoded = {}
        for (start, size), idxs in sorted(uniq.items()):
            raw = d[base + start:base + start + size]
            truncated = 0
            partial_frame = 0
            if len(raw) != size:
                # Measured 2026-11-08: 13 of 16 short regions are short by
                # exactly one 16-byte VAG frame (the clip table's size field
                # overstates the stored bytes by one frame); one (snd_c_tks)
                # is 4 bytes short past EOF with a 12-byte partial frame;
                # one (snd_title.dat clip 5) is 37,376 bytes short — the
                # file holds only the first 60% of that clip. Decode the
                # available whole frames instead of dropping the clip;
                # record both shortfalls exactly. Regions with zero bytes
                # available stay undecodable.
                truncated = size - len(raw)
                partial_frame = len(raw) % 16
                avail = len(raw) - partial_frame
                if avail < 16:
                    problems.append(f'{name}: clip region {start}+{size} '
                                    f'runs past EOF ({len(raw)} bytes read, '
                                    f'0 whole frames available)')
                    continue
                raw = raw[:avail]
                problems.append(f'{name}: clip region {start}+{size} '
                                f'truncated: {truncated} bytes past EOF'
                                f'{f" + {partial_frame}-byte partial frame" if partial_frame else ""}, '
                                f'decoded {avail} bytes ({avail // 16} frames)')
            frames = len(raw) // 16
            try:
                pcm = decode_vag(raw)
            except RuntimeError as e:
                problems.append(f'{name}: region {start}+{size}: {e}')
                continue
            if len(pcm) != frames * 28:
                problems.append(f'{name}: region {start}+{size}: decoded '
                                f'{len(pcm)} samples, expected {frames * 28}')
            nz = sum(1 for x in pcm if x != 0)
            rms = round(math.sqrt(sum(x * x for x in pcm) / len(pcm)), 1) \
                if pcm else 0.0
            decoded[(start, size)] = {
                'frames': frames, 'samples': len(pcm),
                'truncated_bytes_past_eof': truncated,
                'dropped_partial_frame_bytes': partial_frame,
                'duration_s_at_22050': round(len(pcm) / RATE, 3),
                'peak': max((abs(x) for x in pcm), default=0),
                'rms': rms, 'nonzero_fraction': round(nz / len(pcm), 3)
                if pcm else 0.0, 'silent': nz == 0,
                'clip_indexes': idxs,
            }
            tot_samples += len(pcm)
        tot_clips += clips
        tot_unique += len(uniq)
        files.append({'source_file': name, 'container': 'P3Dp',
                      'size_bytes': len(d), 'clip_count': clips,
                      'payload_base': base, 'payload_alignment_delta': delta,
                      'payload_frames_valid': f'{ok}/{n}',
                      'unique_regions': len(uniq),
                      'clips': [{**r,
                                 'decoded': decoded.get((r['start'],
                                                         r['size_bytes']))}
                                for r in recs]})
    out = {
        'format': 'western-heart dw-audio-decoded v1',
        'source': 'Tekken 5 disc, TK5DATA2.BIN (romD), Internet Archive item slus-210.59.-tekken-5',
        'decoder': 'ffmpeg adpcm_psx via synthetic VAGp header (standard tool)',
        'sample_rate_hz': RATE,
        'sample_rate_note': 'ASSUMED standard PS2 sound-effect rate; the rate is NOT stored in the P3Dp bytes. Confirm against the game code (Job 3).',
        'totals': {'files': len(files), 'clips': tot_clips,
                   'unique_regions': tot_unique, 'samples': tot_samples,
                   'duration_s_at_22050': round(tot_samples / RATE, 1)},
        'problems': problems,
        'files': files,
    }
    out_path.write_text(json.dumps(out, indent=1))
    print(f"files={len(files)} clips={tot_clips} unique={tot_unique} "
          f"samples={tot_samples} ({tot_samples / RATE:.1f}s at {RATE} Hz)")
    print(f"problems: {len(problems)}")
    for pr in problems[:10]:
        print('  PROBLEM:', pr)
    if proof_dir is not None:
        proof_dir.mkdir(parents=True, exist_ok=True)
        # three small proof WAVs: first clip of the stage-theme file, the
        # largest unique region overall, first clip of a character file.
        picks = []
        by_name = {f['source_file']: f for f in files if f.get('clips')}
        blu = by_name.get('snd_bg_blu_se.dat')
        if blu and blu['clips']:
            picks.append(('blu-clip0', blu, blu['clips'][0]))
        biggest = None
        for f in files:
            for c in f.get('clips', []):
                dec = c.get('decoded')
                if dec and (biggest is None or dec['samples'] > biggest[1]['decoded']['samples']):
                    biggest = (f, c)
        if biggest:
            picks.append(('largest', biggest[0], biggest[1]))
        c10 = by_name.get('snd_c10jin.dat')
        if c10 and c10['clips']:
            picks.append(('c10-clip0', c10, c10['clips'][0]))
        for tag, f, c in picks:
            d = (romd_dir / f['source_file']).read_bytes()
            raw = d[f['payload_base'] + c['start']:
                    f['payload_base'] + c['start'] + c['size_bytes']]
            wav = proof_dir / f'{tag}.wav'
            p = subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', 'pipe:0',
                                str(wav)], input=vagp(raw),
                               capture_output=True)
            print(f'proof {tag}: {f["source_file"]} clip{c["index"]} '
                  f'{c["decoded"]["samples"]} samples -> {wav} '
                  f'({"OK" if p.returncode == 0 else "FAIL " + p.stderr.decode()[:200]})')

if __name__ == '__main__':
    main()
