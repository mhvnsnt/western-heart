#!/usr/bin/env python3
"""Resilient surgical fetch of Def Jam ISO ranges. Retries tails until byte-exact."""
import os, sys, time, subprocess, threading

HOST = "https://dn721808.ca.archive.org/0/items/slus-210.04.-def-jam-fight-for-ny/SLUS_210.04.Def%20Jam%20-%20Fight%20for%20NY.iso"
D = os.path.expanduser("~/workspace/defjam-work/surgical")

JOBS = [
    ("caw/V2CP_0.VIV", 1716969, 9282398),
    ("caw/V2CP_1.VIV", 1721502, 101383672),
    ("caw/V2CP_2.VIV", 1771006, 81486122),
    ("caw/V2CP_3.VIV", 1810795, 26554644),
    ("motion/WRES_ALL.VIV", 1968777, 64166308),
    ("venues/V2BG.VIV", 1943736, 50614733),
]

def fetch_one(name, lba, size):
    path = os.path.join(D, name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    base = lba * 2048
    for attempt in range(200):
        cur = os.path.getsize(path) if os.path.exists(path) else 0
        if cur >= size:
            if cur > size:
                with open(path, 'r+b') as f:
                    f.truncate(size)
            print(f"{name}: COMPLETE {size}", flush=True)
            return True
        lo, hi = base + cur, base + size - 1
        # stream curl stdout straight into the file in append mode: any
        # partial chunk survives failures and the next retry continues it
        with open(path, 'ab') as out:
            r = subprocess.run(
                ["curl", "-s", "--retry", "2", "--max-time", "900",
                 "-r", f"{lo}-{hi}", "-o", "-", HOST],
                stdout=out, stderr=subprocess.DEVNULL)
        now = os.path.getsize(path)
        if now > cur:
            print(f"{name}: +{(now-cur)//1024}KB -> {now}/{size} ({100*now//size}%)", flush=True)
        else:
            print(f"{name}: attempt {attempt} stalled rc={r.returncode}", flush=True)
            time.sleep(5)
    print(f"{name}: FAILED after 60 attempts", flush=True)
    return False

threads = [threading.Thread(target=fetch_one, args=j) for j in JOBS]
[t.start() for t in threads]
[t.join() for t in threads]
print("RESILIENT_FETCH_DONE", flush=True)
