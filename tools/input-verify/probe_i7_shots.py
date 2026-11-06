#!/usr/bin/env python3
"""Item 7 diagnostic 3: screenshot each suspect fighter IN A FIGHT at idle —
the fight plays the bank stance with NO clavicle gate, so a genuinely broken
stance clip shows here exactly as it would for the player."""
import asyncio, sys, glob
from playwright.async_api import async_playwright

BASE = 'http://127.0.0.1:8841'
IDS = sys.argv[1].split(',') if len(sys.argv) > 1 else ['megami', 'menajerii', 'chatur', 'pantera']

async def main():
    exe = glob.glob('/home/hatch/.cache/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell')[0]
    async with async_playwright() as pw:
        b = await pw.chromium.launch(executable_path=exe, args=[
            '--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader',
            '--disable-dev-shm-usage', '--no-sandbox', '--mute-audio'])
        for fid in IDS:
            p = await b.new_page(viewport={'width': 1000, 'height': 760})
            try:
                await p.goto(f'{BASE}/game/index.html?quick={fid},pantera,shrine')
                await p.wait_for_function(
                    "window.__game && __game.roundState === 'fight' && __game.p1 && __game.p1.char.id === '" + fid + "'",
                    timeout=600000)
                await p.wait_for_timeout(2600)  # let the idle stance loop run
                await p.screenshot(path=f"shot-i7-{fid}.png", timeout=180000)
                print(fid, 'shot saved', flush=True)
            except Exception as e:
                print(fid, 'ERROR', str(e)[:150], flush=True)
            await p.close()
        await b.close()

asyncio.run(main())
