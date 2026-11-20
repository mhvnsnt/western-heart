#!/usr/bin/env python3
"""Item 7 diagnostic 1: run the REAL PreviewPane fit gate (via the game's own
portrait-capture page) over the bank-stance fit class + controls, capturing the
gate's own console.warn rejection reasons and stanceSource per fighter."""
import asyncio, json, sys, glob
from playwright.async_api import async_playwright

BASE = 'http://127.0.0.1:8841'
IDS = sys.argv[1].split(',') if len(sys.argv) > 1 else [
    'pantera', 'demonio', 'pond', 'ryusan', 'tobi', 'chatur', 'megami', 'menajerii',
    'star', 'rin', 'gyou', 'negativo', 'purplerain', 'awapop', 'sha', 'kai']

async def main():
    exe = glob.glob('/home/hatch/.cache/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell')[0]
    results = {}
    async with async_playwright() as pw:
        b = await pw.chromium.launch(executable_path=exe, args=[
            '--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader',
            '--disable-dev-shm-usage', '--no-sandbox', '--mute-audio'])
        for fid in IDS:
            warns = []
            p = await b.new_page(viewport={'width': 320, 'height': 320})
            p.on('console', lambda m, w=warns: w.append(m.text) if m.type in ('warning', 'error') else None)
            p.on('pageerror', lambda e, w=warns: w.append('PAGEERROR ' + str(e)[:150]))
            try:
                await p.goto(BASE + '/game/portrait-capture.html')
                await p.wait_for_function('window.ready', timeout=90000)
                r = await p.evaluate('async (id) => await window.capture(id)', fid)
                r.pop('png', None)
                r['gateWarns'] = [w for w in warns if 'does not fit' in w or 'unavailable' in w or 'failed' in w]
                results[fid] = r
                print(fid, json.dumps(r), flush=True)
            except Exception as e:
                results[fid] = {'error': str(e)[:200], 'gateWarns': warns[-3:]}
                print(fid, 'ERROR', str(e)[:150], flush=True)
            await p.close()
        await b.close()
    json.dump(results, open('gate-results.json', 'w'), indent=1)
    print('saved gate-results.json')

asyncio.run(main())
