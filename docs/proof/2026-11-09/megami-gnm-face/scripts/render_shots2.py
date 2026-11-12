"""Render shots from gnmproof2.html (clean stage: fitted hair part + exposure).
Same driver pattern as render_shots.py but the page URL carries ?glb=&hair=&exp=.
Config: {"glb": ..., "hair": ..., "exp": ..., "shots": [{name, size?, cam?,
angel?, body?, eye?, vis?, glb?, hair?, exp?}]}
"""
import base64, json, os, sys, time
from playwright.sync_api import sync_playwright

BASE = '/home/hatch/workspace/_gnmface-20261109'
CHROME = '/home/hatch/workspace/_playverify-20261030/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell'
os.makedirs(f'{BASE}/proof', exist_ok=True)

cfg = json.load(open(sys.argv[1]))
shots = cfg['shots']

def page_url(s):
    glb = s.get('glb', cfg.get('glb'))
    hair = s.get('hair', cfg.get('hair'))
    exp = s.get('exp', cfg.get('exp'))
    u = f'http://127.0.0.1:8843/_gnmface-20261109/gnmproof2.html?glb={glb}'
    if hair:
        u += f'&hair={hair}'
    if exp:
        u += f'&exp={exp}'
    return u

def run_once(p, shots):
    browser = p.chromium.launch(executable_path=CHROME, args=['--use-angle=swiftshader', '--no-sandbox'])
    page = browser.new_page(viewport={'width': 760, 'height': 1320})
    cur_url = None
    for s in shots:
        u = page_url(s)
        if u != cur_url:
            page.goto(u)
            page.wait_for_function('window.__ready === true', timeout=120000)
            cur_url = u
            print('loaded', u)
            print(' log:', page.evaluate('window.__log'))
        if 'size' in s:
            page.evaluate(f"window.setSize({s['size'][0]}, {s['size'][1]})")
        if 'eye' in s:
            page.evaluate(f"window.setEye({json.dumps(s['eye'])})")
        if 'vis' in s:
            page.evaluate(f"window.setVis({json.dumps(s['vis'])})")
        if 'angel' in s:
            print(' ', page.evaluate(f"window.setAngel({s['angel']})"))
        if 'body' in s:
            print(' ', page.evaluate(f"window.setBody({s['body']})"))
        if 'cam' in s:
            c = s['cam']
            page.evaluate(f"window.setCam({json.dumps(c['pos'])}, {json.dumps(c['tgt'])}, {c.get('fov', 55)})")
        page.wait_for_timeout(250)
        b64 = page.evaluate('window.shot()')
        out = f"{BASE}/proof/{s['name']}.png"
        open(out, 'wb').write(base64.b64decode(b64))
        print('shot', out, os.path.getsize(out))
    browser.close()

with sync_playwright() as p:
    for attempt in range(4):
        try:
            run_once(p, shots)
            break
        except Exception as e:
            print(f'attempt {attempt} failed: {e}')
            if attempt == 3:
                raise
            time.sleep(3)
print('RENDER DONE')
