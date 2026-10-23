import subprocess, requests, sys
PART = 524288000
ASSETS = {0: 651130101, 1: 651155986, 2: 651173731, 3: 651189144, 4: 651243921, 5: 651266911}
_tok = None
def tok():
    global _tok
    if _tok is None:
        _tok = subprocess.check_output(['gh', 'auth', 'token']).decode().strip()
    return _tok
def fetch(goff, n):
    """Fetch n bytes at global tar offset goff, spanning parts if needed."""
    import time
    out = bytearray()
    while n > 0:
        part = goff // PART; lo = goff % PART
        take = min(n, PART - lo)
        url = f"https://api.github.com/repos/mhvnsnt/western-heart/releases/assets/{ASSETS[part]}"
        last = None
        for attempt in range(6):
            try:
                r = requests.get(url, headers={'Authorization': f'token {tok()}', 'Accept': 'application/octet-stream', 'Range': f'bytes={lo}-{lo+take-1}'}, timeout=300)
                assert r.status_code == 206, (r.status_code, goff)
                assert len(r.content) == take, (len(r.content), take)
                break
            except Exception as e:
                last = e; time.sleep(2 * (attempt + 1))
        else:
            raise last
        out += r.content; goff += take; n -= take
    return bytes(out)
def fetch_to_file(goff, n, path, chunk=1 << 22):
    with open(path, 'wb') as f:
        done = 0
        while done < n:
            take = min(chunk, n - done)
            f.write(fetch(goff + done, take)); done += take
    return path
if __name__ == '__main__':
    goff, n, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    fetch_to_file(goff, n, out); print('wrote', out, n)
