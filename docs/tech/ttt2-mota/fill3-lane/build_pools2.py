#!/usr/bin/env python3
"""Rebuild pools with bound = distance to next block's bracket (roster order),
then retry chain assembly for the pool-suspect blocks."""
import struct, json, pickle, os, re
from collections import defaultdict

W = os.path.expanduser('~/workspace/_fill3-ttt2-20261106/work')
d6 = open(os.path.expanduser('~/workspace/_ttt2-motion-20261103/join-cont/data006-decoded.bin'), 'rb').read()
u32 = lambda o: struct.unpack('>I', d6[o:o + 4])[0]

ROSTER = ['Paul', 'LAW', 'Lei_Wulong', 'RAVEN', 'FENG', 'ARMOR_KING', 'EMILIE',
          'Dragunov', 'KING', 'PANDA', 'EDDY', 'BOB_SATSUMA', 'ZAFINA', 'Miguel',
          'Eleonor', 'Lars', 'Alisa', 'Jinpachi', 'YOSHIMITSU', 'Ogre',
          'JUN_KAZAMA', 'Unknown', 'Kunimitsu', 'SlimBob', 'Forest', 'Miharu',
          'ANGEL', 'Michelle', 'NINA', 'P-JACK', 'ALEX', 'GreenOgre', 'VIOLET',
          'Bosconovitch', 'Sebastian', 'TIGER', 'Combot', 'Zako00', 'Zako01',
          'Zako02', 'Zako03', 'Zako04', 'Zako05', 'Zako06', 'Zako07', 'HWOARANG',
          'Lin_Xiaoyu', 'CHRISTIE', 'JIN', 'JULIA', 'Kuma', 'Bryan', 'HEIHACHI',
          'KAZUYA', 'LEE', 'Steve_Fox', 'MARDUK', 'Jack', 'ROGER', 'ANNA',
          'Wang', 'GANRYU', 'Asuka', 'BRUCE', 'BAEK_DOO_SAN', 'DEVIL_JIN']

brackets = {}
for name in ROSTER:
    pat = b'[' + name.encode() + b']\x00'
    i = d6.find(pat)
    assert i >= 0, name
    brackets[name] = i
order = sorted(ROSTER, key=lambda n: brackets[n])
pools2 = {}
for k, name in enumerate(order):
    start = brackets[name]
    end = brackets[order[k + 1]] if k + 1 < len(order) else len(d6)
    pool, rel = {}, 0
    while rel < end - start:
        j = d6.find(b'\x00', start + rel)
        if j < 0: break
        raw = d6[start + rel:j]
        if 2 <= len(raw) <= 80 and all(32 <= c < 127 for c in raw):
            pool[rel] = raw.decode()
        rel = (j - start) + 1
    pools2[name] = pool
    print('%-14s bracket=%9d pool strings=%6d max_rel=%7d span=%7d'
          % (name, start, len(pool), max(pool) if pool else 0, end - start))
pickle.dump({'pools': pools2, 'brackets': brackets},
            open(os.path.join(W, 'pools2.pkl'), 'wb'))
