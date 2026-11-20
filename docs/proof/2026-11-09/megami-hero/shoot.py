import sys, os, json
from playwright.sync_api import sync_playwright
# usage: shoot.py <query> <outprefix> <cam1,cam2,...>
query = sys.argv[1]
prefix = sys.argv[2]
cams = sys.argv[3].split(',')
import urllib.parse
q = urllib.parse.parse_qs(query)
vw = int(q.get('w', ['820'])[0]); vh = int(q.get('h', ['1230'])[0])
os.environ['PLAYWRIGHT_BROWSERS_PATH'] = '/home/hatch/workspace/_hair-wire-20261108/pw-browsers'
with sync_playwright() as p:
    b = p.chromium.launch(args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--no-sandbox'])
    pg = b.new_page(viewport={'width': vw, 'height': vh})
    pg.on('pageerror', lambda e: print('PAGEERROR', str(e)[:300]))
    pg.on('console', lambda m: print('CONSOLE', m.type, m.text[:200]) if m.type == 'error' else None)
    pg.goto('http://127.0.0.1:8843/_hero-shot-20261109/stage.html?' + query)
    pg.wait_for_function('window.__ready===true', timeout=300000)
    print('LOG:', pg.evaluate('window.__log'))
    print('FACTS:', json.dumps(pg.evaluate('window.__facts')))
    for v in cams:
        print(pg.evaluate(f"window.__cam('{v}')"))
        out = f'{prefix}-{v}.png'
        for attempt in range(4):
            try:
                pg.screenshot(path=out, timeout=180000)
                break
            except Exception as e:
                print('screenshot retry', attempt, str(e)[:120])
                pg.evaluate(f"window.__cam('{v}')")
        print('shot', out, os.path.getsize(out) if os.path.exists(out) else 'MISSING')
    b.close()
