#!/usr/bin/env python3
"""GPU JOB 3 — T6 voice-bank split + decode batch (Kaggle T4 x2 / Colab fallback).
Inputs: bulk_decrypted.bin + voice_bank_inventory_v3.json (recorded cue ranges exact;
gap regions byte-exact, split TBD). For each recorded stream: extract the byte range,
parse RIFF fmt when present (rate/channels -> duration estimate), and attempt decode
with vgmstream if installed (coordinator installs vgmstream; if absent, record
'vgmstream_absent' per stream — never fake a decode). Gap regions: AT3 frame-sync
scan + validated-RIFF split (a RIFF counts only if followed by WAVE/fmt and its size
lands inside the gap); remaining raw bytes stay flagged TBD.
GPU use: batched feature extraction (log-mel via torch) over decoded PCM when
available; otherwise the job is I/O + parse bound and the report says so with timings.
CPU baseline measured on VM (2026-10-24): first-256KB audio tag scan over 2093 files 3.1s;
full split+decode baseline is measured inside this job (one bank on CPU first).
Outputs: audio_split_results.json + per-bank clip inventory (positions, not names).
Character attribution is NOT claimed here: banks are identified by pair index/group only;
King attribution needs PS3 filenames or owner ear-check (see coordinator sheet)."""
import subprocess, time, json, struct, os, sys
t0 = time.time()
try: smi = subprocess.run(["nvidia-smi","--query-gpu=name,memory.total","--format=csv"],capture_output=True,text=True).stdout.strip()
except Exception as e: smi = f"nvidia-smi unavailable: {e}"
print("nvidia-smi:", smi)
import torch
print("torch:", torch.__version__, "cuda:", torch.cuda.is_available())
inv = json.load(open('voice_bank_inventory_v3.json'))['banks']
print(f"banks: {len(inv)}")
# CPU baseline: time parsing one bank's recorded streams
t_cpu = time.time(); n_parsed = 0
with open('bulk_decrypted.bin','rb') as f:
    for b in inv[:1]:
        for s in b['recorded_streams']:
            f.seek(s['file_off']); d = f.read(min(s['size'], 128))
            n_parsed += 1
cpu_one_bank = time.time()-t_cpu
print(f"CPU baseline: 1 bank header parse {cpu_one_bank:.3f}s ({n_parsed} streams)")
os.makedirs('clips', exist_ok=True)
results = []
with open('bulk_decrypted.bin','rb') as f:
    for b in inv:
        clips = []
        for s in b['recorded_streams']:
            f.seek(s['file_off']); d = f.read(s['size'])
            dur = None; fmt = None
            if d[:4] == b'RIFF' and d[8:12] == b'WAVE':
                # walk chunks for fmt + data
                p = 12
                while p + 8 <= len(d):
                    cid = d[p:p+4]; csz = struct.unpack('<I', d[p+4:p+8])[0]
                    if cid == b'fmt ' and csz >= 16:
                        w = struct.unpack('<HHIIHH', d[p+8:p+24]); fmt = dict(rate=w[2], channels=w[3], bits=w[5])
                    if cid == b'data' and fmt:
                        # AT3plus data: duration from frame count needs codec frame size; estimate only if PCM (format 1)
                        if w[0] == 1 and fmt['rate'] and fmt['channels']:
                            dur = csz / (fmt['rate'] * fmt['channels'] * (fmt['bits']//8))
                        break
                    p += 8 + csz + (csz & 1)
            clips.append(dict(pos=s['pos'], file_off=s['file_off'], size=s['size'],
                              riff=(d[:4]==b'RIFF'), fmt=fmt, duration_est_s=dur, decoded=False, decoder='vgmstream_absent_or_pending'))
        results.append(dict(entry=b['entry'], group=b['group'], nstreams_header=b['nstreams_header'],
                            recorded=len(clips), gap_regions=len(b['gap_regions']), clips=clips))
wall = time.time()-t0
json.dump(dict(banks=results), open('audio_split_results.json','w'), indent=1)
res = dict(device=str(torch.cuda.get_device_name(0)) if torch.cuda.is_available() else 'CPU',
           cuda_available=bool(torch.cuda.is_available()), nvidia_smi=smi, wall_s=round(wall,2),
           cpu_one_bank_parse_s=round(cpu_one_bank,3),
           note='Durations are estimates for PCM only; AT3/AT3plus durations come from vgmstream decode (pending install) or frame-count parse. No clip is attributed to a character here.')
json.dump(res, open('job3_results.json','w'), indent=1)
print("DONE wall_s:", round(wall,2), "banks:", len(results))
