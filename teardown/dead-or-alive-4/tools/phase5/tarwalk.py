import subprocess, requests, sys
tok = subprocess.check_output(['gh','auth','token']).decode().strip()
PART=524288000
assets={0:651130101,1:651155986,2:651173731,3:651189144,4:651243921,5:651266911}
def fetch(goff, n):
    part=goff//PART; lo=goff%PART
    aid=assets[part]
    url=f"https://api.github.com/repos/mhvnsnt/western-heart/releases/assets/{aid}"
    r=requests.get(url, headers={'Authorization': f'token {tok}', 'Accept': 'application/octet-stream', 'Range': f'bytes={lo}-{lo+n-1}'}, timeout=120)
    assert r.status_code==206, r.status_code
    return r.content
off=0; total=524288000*5+506081280
while off < total-512:
    hdr=fetch(off, 512)
    if hdr[:1]==b'\x00' or len(hdr)<512: break
    name=hdr[:100].split(b'\x00')[0].decode('utf-8','replace')
    try: size=int(hdr[124:136].split(b'\x00')[0].strip() or b'0', 8)
    except Exception: break
    print(f'{off} {size} {name}')
    if 'chr' in name or 'mot' in name: print('  ^^ INTEREST', flush=True)
    off += 512 + ((size+511)//512)*512
