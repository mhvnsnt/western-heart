#!/usr/bin/env python3
"""GPU JOB 2 — T6 bulk census (Kaggle T4 x2 / Colab fallback).
Splits bulk_decrypted.bin by the solved IDX table and computes per-file
magic + entropy. Entropy histograms use torch bincount (GPU when available).
CPU baseline measured on VM (2026-10-24): full 2093-file census 98.5s.
Prints nvidia-smi + torch.cuda proof and wall time; speedup_measured is
computed against the 98.5s baseline ONLY for the same work (same file set).
Inputs: bulk_decrypted.bin (384073728 bytes, private upload — never a public repo),
idx_decrypted_keysetA_chunk1024.bin (26028 bytes, solved IDX plaintext table).
Outputs: census_gpu.json + job2_results.json."""
import subprocess, time, json, struct, math, sys
from collections import Counter
t0 = time.time()
try: smi = subprocess.run(["nvidia-smi","--query-gpu=name,memory.total","--format=csv"],capture_output=True,text=True).stdout.strip()
except Exception as e: smi = f"nvidia-smi unavailable: {e}"
print("nvidia-smi:", smi)
import torch
dev = 'cuda' if torch.cuda.is_available() else 'cpu'
print("torch:", torch.__version__, "cuda:", torch.cuda.is_available(), "device:", dev)
raw = open('idx_decrypted_keysetA_chunk1024.bin','rb').read()
e = struct.unpack('<%dI'%(len(raw)//4), raw)
rows = [(e[i],e[i+1],e[i+2]) for i in range(0,2169*3,3)]
def ent_gpu(data):
    if not data: return 0.0
    t = torch.frombuffer(bytearray(data), dtype=torch.uint8).to(dev)
    bc = torch.bincount(t, minlength=256).double()
    p = bc / bc.sum()
    p = p[p > 0]
    return float(-(p * torch.log2(p)).sum().item())
out=[]
with open('bulk_decrypted.bin','rb') as f:
    for idx,(off,sz,tag) in enumerate(rows):
        if sz == 0xFFFFFFFF: out.append(dict(entry=idx,off=off,size=-1,tag=tag,kind='sentinel')); continue
        if sz == 0: out.append(dict(entry=idx,off=off,size=0,tag=tag,kind='empty')); continue
        f.seek(off*2048); data = f.read(sz); head = data[:20]; kind='other'
        for m in (b'MOTA',b'NTPP',b'NTXL',b'GZIP',b'NDPP',b'TIM2',b'RIFF',b'GMO\x00'):
            if head.startswith(m): kind=m.decode(errors='replace').strip('\x00'); break
        if kind=='other' and data[16:20]==b'GZIP': kind='GZIP+prefix16'
        out.append(dict(entry=idx,off=off,size=sz,tag=tag,kind=kind,head=head.hex(),entropy=round(ent_gpu(data),3)))
        if idx % 500 == 0: print(f"  ...entry {idx} elapsed {time.time()-t0:.1f}s", flush=True)
json.dump(dict(files=out), open('census_gpu.json','w'), indent=1)
wall = time.time()-t0
res = dict(device=str(torch.cuda.get_device_name(0)) if torch.cuda.is_available() else 'CPU',
           cuda_available=bool(torch.cuda.is_available()), nvidia_smi=smi, wall_s=round(wall,2),
           cpu_baseline_s=98.5, speedup_measured=(round(98.5/wall,2) if wall>0 else None),
           entries=len(out), kinds=dict(Counter(o['kind'] for o in out)))
json.dump(res, open('job2_results.json','w'), indent=1)
print("DONE wall_s:", round(wall,2), "speedup_vs_98.5s_CPU:", res['speedup_measured'], "kinds:", res['kinds'])
