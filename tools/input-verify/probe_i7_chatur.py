#!/usr/bin/env python3
"""Item 7 diagnostic 4: why does the fit gate never run for Chatur?
Replicates the pane's preconditions directly against his model instance."""
import asyncio, glob, json
from playwright.async_api import async_playwright

async def main():
    exe = glob.glob('/home/hatch/.cache/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell')[0]
    async with async_playwright() as pw:
        b = await pw.chromium.launch(executable_path=exe, args=[
            '--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader',
            '--disable-dev-shm-usage', '--no-sandbox', '--mute-audio'])
        p = await b.new_page()
        p.on('console', lambda m: print('CONSOLE', m.type, m.text[:180], flush=True) if m.type in ('warning', 'error') else None)
        await p.goto('http://127.0.0.1:8841/game/portrait-capture.html')
        await p.wait_for_function('window.ready', timeout=90000)
        out = await p.evaluate("""async () => {
          const THREE = await import('three');
          const { assets } = await import("/game/js/assets.js");
          const { loadT3Clips } = await import('/game/js/t3anims.js');
          const { ROSTER } = await import('/game/js/characters.js');
          const { attiresFor } = await import('/game/js/attires.js');
          const c = ROSTER.find(r => r.id === 'chatur');
          const modelId = attiresFor(c)[0].model;
          await assets.loadModels([modelId]);
          const inst = assets.createInstance(modelId, 0xffffff, 0x888888, 0, null);
          const keys = Object.keys(inst.bones || {});
          const clips = await loadT3Clips(THREE, 'ogre');
          return {
            modelId,
            boneKeys: keys.length,
            hasHips: !!inst.bones.Hips, hasRightArm: !!inst.bones.RightArm, hasHead: !!inst.bones.Head,
            hasLeftShoulder: !!inst.bones.LeftShoulder,
            armLikeKeys: keys.filter(k => /arm|shoulder/i.test(k)).slice(0, 14),
            clipsLoaded: clips ? Object.keys(clips).length : null,
            hasStanceClip: !!(clips && clips.stance),
          };
        }""")
        print(json.dumps(out, indent=1))
        await b.close()

asyncio.run(main())
