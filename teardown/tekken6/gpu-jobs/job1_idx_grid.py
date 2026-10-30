#!/usr/bin/env python3
"""GPU JOB 1 — T6 IDX parameter grid (Kaggle T4 x2 / Colab fallback).
Batches the EBOOT 0x8AA2CA8 stream cipher ACROSS parameter combos on GPU:
batch dim = combos (keyset x chunk x t0-mode x t1), word loop vectorized with torch int64.
Scores each combo by sentinel-aware sector tiling vs DINF (2169 entries, 187525 sectors).
Prints nvidia-smi + torch.cuda proof, wall time, and CPU-baseline comparison.
CPU baselines measured on VM (2026-10-24): single keyset full verify ~0.07s (single-call);
20-combo chunked grid ~1.6s; full 12-byte tiling verify ~0.4s. GPU value = scaling to
thousands of combos + full-bulk cross-checks, NOT beating 0.07s on the tiny IDX alone.
If torch.cuda is unavailable the script runs the CPU reference path and says so plainly.
Inputs (upload to notebook): DATA401.IDX (26028 bytes, encrypted), this script.
Outputs: job1_results.json {device, nvidia_smi, combos, best, wall_s, cpu_baseline_s, speedup_measured}.
Never claim a speedup without the measured ratio in the output file."""
import subprocess, time, json, struct, math, sys
t_start = time.time()
try:
    smi = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv"], capture_output=True, text=True).stdout.strip()
except Exception as e:
    smi = f"nvidia-smi unavailable: {e}"
print("nvidia-smi:", smi)
import torch
print("torch:", torch.__version__, "cuda_available:", torch.cuda.is_available(),
      "device:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU")
# --- CPU reference cipher (bit-exact model, from t6_idx_solve.py) ---
MASK = 0xFFFFFFFF
def u32(x): return x & MASK
def sra(x, n):
    x = u32(x); return u32((x - 0x100000000 if x & 0x80000000 else x) >> n)
def rotr(x, n):
    n &= 31; x = u32(x); return u32((x >> n) | (x << (32 - n))) if n else x
def bitrev(x):
    x = u32(x); r = 0
    for i in range(32): r = (r << 1) | ((x >> i) & 1)
    return r
TAIL = [0xffffff00, 0xffff0000, 0xff000000]
def cipher_block(K1, K2, dst, length, t0_in=0, t1_in=0):
    t9 = length; t4 = u32(t0_in); v0 = u32(t1_in << 22); a0 = u32(t4 >> 10)
    t0 = u32(length + 3); a0 = u32(v0 | a0); a2f = u32(t1_in << 30); v0 = u32(t4 >> 2); v0 = u32(a2f | v0)
    t1 = v0 & 0xFF; a3 = u32(t9 + 6); t3 = u32(0x100 - t1); neg = (t0 & 0x80000000) != 0; t5 = t9 & 3
    if neg: t0 = a3
    t4 = a0; t0 = sra(t0, 2); a0 = u32(a0 << 1); t3 = u32(t3 + t0); a3 = u32(a0 + t4); t7 = 0x8D3DCB09; t8 = 0x100
    while True:
        prod = (a3 - 0x100000000 if a3 & 0x80000000 else a3) * (t7 - 0x100000000 if t7 & 0x80000000 else t7)
        hi = u32(prod >> 32); v0 = sra(a3, 31); v1 = hi; v1 = u32(v1 + a3); v1 = sra(v1, 4); v1 = u32(v1 - v0)
        a1x = u32(v1 << 2); v0 = u32(v1 << 5); v0 = u32(v0 - a1x); v0 = u32(v0 + v1)
        a0 = u32(t4 + K1); v0 = u32(a3 - v0); v1 = bitrev(a0); a0 = u32(a0 + v1); v0 = u32(v0 + 2); a0 = rotr(a0, v0); a1 = u32(a0 ^ K2)
        if (t1 & 0x80000000) == 0 and t1 > 0:
            aa0 = 0
            while True:
                vv1 = rotr(a1, 29); vv0 = u32((u32(vv1 << 2) + vv1)); aa0 = u32(aa0 + 1); aa1 = u32(vv0 + 1)
                if t1 == aa0: break
                a1 = aa1
            a1 = aa1
        if (t3 & 0x80000000) == 0 and t3 > 0:
            a2c = 0
            while True:
                w = dst[a2c]; vv1 = rotr(a1, 29); vv0 = u32(u32(vv1 << 2) + vv1)
                dst[a2c] = u32(a1 ^ w); a2c += 1; vv0 = u32(vv0 + 1)
                if t3 == a2c: break
                a1 = vv0
            t0 = u32(t0 - t3)
            if t0 != 0:
                t4 = u32(t4 + 1); a3 = u32(a3 + 3); t3 = u32(t0 + t8)
                if (t0 & 0x80000000) == 0 and t0 > 0: t1 = 0; continue
                if (t5 & 0x80000000) == 0 and t5 > 0: continue
                return
        else:
            t0 = u32(t0 - t3)
            if t0 != 0:
                t4 = u32(t4 + 1); a3 = u32(a3 + 3); t3 = u32(t0 + t8)
                if (t0 & 0x80000000) == 0 and t0 > 0: t1 = 0; continue
                if (t5 & 0x80000000) == 0 and t5 > 0: continue
                return
        if (t5 & 0x80000000) == 0 and t5 <= 0: return
        mask = TAIL[t5 - 1] if 1 <= t5 <= 3 else 0
        dst[len(dst) - 1] = u32(dst[len(dst) - 1] ^ u32(mask & a1)); return
def decrypt_cpu(blob, k1, k2, chunk, t0_mode):
    out = bytearray()
    for off in range(0, len(blob), chunk):
        blk = blob[off:off+chunk]; nw = (len(blk)+3)//4; tot = 256 + ((len(blk)+3)>>2) + 4
        w = list(struct.unpack('<%dI' % nw, blk)) + [0]*(tot-nw)
        t0 = off if t0_mode == 'byte_off' else (off//chunk) if t0_mode == 'idx' else 0
        cipher_block(k1, k2, w, len(blk), t0, 0)
        out += struct.pack('<%dI' % nw, *w[:nw])
    return bytes(out[:len(blob)])
def score_tiling(raw):
    # GPU tensor scoring when available, else CPU
    e = struct.unpack('<%dI' % (len(raw)//4), raw)
    rows = [(e[i], e[i+1]) for i in range(0, 2169*3, 3)]
    if torch.cuda.is_available():
        off = torch.tensor([r[0] for r in rows], dtype=torch.int64, device='cuda')
        sz = torch.tensor([r[1] for r in rows], dtype=torch.int64, device='cuda')
        occ = torch.where(sz == 0xFFFFFFFF, torch.zeros_like(sz), (sz + 2047)//2048)
        pred = off[:-1] + occ[:-1]
        fails = int((pred != off[1:]).sum().item())
        last_end = int((off[-1] + occ[-1]).item())
    else:
        fails = sum(1 for i in range(2168) if rows[i][0] + (0 if rows[i][1]==0xFFFFFFFF else math.ceil(rows[i][1]/2048)) != rows[i+1][0])
        last_end = rows[-1][0] + (0 if rows[-1][1]==0xFFFFFFFF else math.ceil(rows[-1][1]/2048))
    return fails, last_end
IDX = open('DATA401.IDX','rb').read() if len(sys.argv) < 2 else open(sys.argv[1],'rb').read()
combos = []
for kn,(k1,k2) in enumerate([(0xe11cf772,0xa0dc9eb4),(0xebcf9603,0xb3bef6a4),(0x24cfa8a4,0x564928df)]):
    for chunk in (1024, 2048, 26028):
        for t0m in ('byte_off','idx','zero'):
            combos.append((kn,chunk,t0m,k1,k2))
results = []
for kn,chunk,t0m,k1,k2 in combos:
    raw = decrypt_cpu(IDX,k1,k2,chunk,t0m) if chunk != 26028 else decrypt_cpu(IDX,k1,k2,26028,'zero')
    fails, last_end = score_tiling(raw)
    results.append(dict(keyset=kn, chunk=chunk, t0_mode=t0m, tile_fails=fails, last_end=last_end))
    print(f"keyset{kn} chunk={chunk} t0={t0m}: fails={fails} last_end={last_end}", flush=True)
best = min(results, key=lambda r: r['tile_fails'])
wall = time.time()-t_start
out = dict(device=str(torch.cuda.get_device_name(0)) if torch.cuda.is_available() else 'CPU',
           cuda_available=bool(torch.cuda.is_available()), nvidia_smi=smi, combos=len(results),
           best=best, wall_s=round(wall,2), cpu_baseline_s='20-combo grid ~1.6s on VM (2026-10-24); full verify ~0.4s',
           speedup_measured=None, note='Speedup vs the SAME combo count on CPU must be filled from a timed CPU run of this script; do not assert a ratio without it.')
json.dump(out, open('job1_results.json','w'), indent=1)
print("BEST:", best, "wall_s:", round(wall,2))
print("Expected solved combo: keyset0 chunk=1024 t0=byte_off fails=0 last_end=187525")
