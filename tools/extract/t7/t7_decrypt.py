#!/usr/bin/env python3
"""Decrypt Tekken 7 per-asset encryption in place (public community key, credit Gneiss).
T7's tool applies AES-256-ECB *encrypt* to turn the stored asset back into plaintext
(the stored file is the AES "decryption" of the original). Only full 16-byte blocks."""
import sys, os
from Crypto.Cipher import AES
KEY = b'=d6nw6YY6E#tI=6li6pI5CVaBC@fy%vR'
MAGIC = bytes.fromhex('c1832a9e')
def fix(p):
    d = open(p, 'rb').read()
    if d[:4] == MAGIC: return 'plain'
    n = len(d) // 16 * 16
    out = AES.new(KEY, AES.MODE_ECB).encrypt(d[:n]) + d[n:]
    if out[:4] != MAGIC: return 'skip'
    open(p, 'wb').write(out); return 'dec'
if __name__ == '__main__':
    from collections import Counter; c = Counter()
    for root in sys.argv[1:]:
        for dp, _, fs in os.walk(root):
            for f in fs:
                if f.endswith(('.uasset', '.umap')): c[fix(os.path.join(dp, f))] += 1
    print(dict(c))
