#!/usr/bin/env python3
"""Stage A: fetch GLB JSON chunks (range requests) for every default model in assets.js MODEL_URLS.
Saves <key>.json (gltf json) under glbmeta/. No full GLB downloads."""
import re, os, sys, json, struct, subprocess, concurrent.futures

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'glbmeta'); os.makedirs(OUT, exist_ok=True)
assets = open(os.path.join(ROOT, 'wh/game/js/assets.js')).read()
m = re.search(r'const MODEL_URLS = \{(.*?)\n\};', assets, re.S)
urls = {}
for km, um in re.findall(r"'?([\w\-]+)'?\s*:\s*'([^']+)'", m.group(1)):
    urls[km] = um
print(f'{len(urls)} MODEL_URLS entries')

def repo_path(url):
    # urls are relative to game/ page: '../roster/x' -> roster/x ; 'assets/...' -> game/assets/...
    if url.startswith('../'): return url[3:]
    return 'game/' + url

def fetch_json(key):
    url = urls[key]
    if not url.endswith('.glb'): return (key, 'not-glb')
    dest = os.path.join(OUT, key + '.json')
    if os.path.exists(dest): return (key, 'cached')
    rp = repo_path(url)
    raw = f'https://raw.githubusercontent.com/mhvnsnt/western-heart/main/{rp}'
    tmp = dest + '.part'
    # first 20 bytes for header
    r = subprocess.run(['curl', '-sL', '-r', '0-19', '-o', tmp, raw], capture_output=True)
    try:
        d = open(tmp, 'rb').read()
        if d[:4] != b'glTF': return (key, 'bad-magic')
        total, jlen = struct.unpack('<II', d[8:16])
        need = 20 + jlen
        r = subprocess.run(['curl', '-sL', '-r', f'0-{need-1}', '-o', tmp, raw], capture_output=True)
        d = open(tmp, 'rb').read()
        gj = json.loads(d[20:20+jlen])
        gj['_wh_total'] = total; gj['_wh_url'] = url; gj['_wh_repo'] = rp; gj['_wh_jsonlen'] = jlen
        json.dump(gj, open(dest, 'w'))
        os.remove(tmp)
        return (key, f'ok {total}')
    except Exception as e:
        return (key, f'ERR {e}')

keys = list(urls.keys())
with concurrent.futures.ThreadPoolExecutor(6) as ex:
    for k, s in ex.map(fetch_json, keys):
        print(k, s)
