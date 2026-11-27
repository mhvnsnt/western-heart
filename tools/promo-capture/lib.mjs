// Western Heart promo/proof capture: HUD-off, scripted camera, deterministic frames.
import { chromium } from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
const here = path.dirname(new URL(import.meta.url).pathname);
export const HIDE_CSS = `
#hud, .hud, .hud-top, #touch-controls, .touch-controls, #touch-ui, .touch-btn, #joystick, .joystick, #vjoy,
[id^="btn-"], .fight-buttons, #pause-btn, .pause-btn, #round-banner, .wh-freecam-bar, .free-cam-bar, #toast, .toast
{ display: none !important; visibility: hidden !important; }`;
export async function launch({ width = 1280, height = 720, base = process.env.WH_URL || 'https://western-heart.pages.dev' } = {}) {
  const browser = await chromium.launch({ executablePath: process.env.CHROME || '/usr/bin/google-chrome',
    args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const page = await browser.newPage({ viewport: { width, height } });
  await page.addInitScript({ path: path.join(here, 'vclock.js') });
  // Local override (proof of an unmerged branch on the live build): WH_OVERRIDE_ROOT=<repo checkout>,
  // WH_OVERRIDE_FILES=game/js/fighter.js,... are served from the checkout; everything else from the live site.
  if (process.env.WH_OVERRIDE_ROOT && process.env.WH_OVERRIDE_FILES) {
    for (const rel of process.env.WH_OVERRIDE_FILES.split(',')) {
      const file = path.join(process.env.WH_OVERRIDE_ROOT, rel);
      await page.route('**/' + rel + '*', (route) => route.fulfill({ path: file, headers: { 'cache-control': 'no-store',
        'content-type': rel.endsWith('.js') ? 'application/javascript' : 'application/json' } }));
    }
  }
  const errors = []; page.on('pageerror', e => errors.push(String(e).slice(0, 200)));
  await page.goto(base + '/game/index.html', { timeout: 180000 });
  await page.waitForFunction(() => typeof window.__startFight === 'function', null, { timeout: 120000 });
  await page.waitForTimeout(6000);
  return { browser, page, errors };
}
export async function startFight(page, p1, p2, { aiPassive = true } = {}) {
  await page.evaluate(([a, b]) => window.__startFight(a, b), [p1, p2]);
  await page.waitForFunction(() => { const h = document.getElementById('hud'); return h && getComputedStyle(h).display !== 'none' && window.__game && window.__game.p1 && window.__game.p1.root; }, null, { timeout: 240000 });
  await page.waitForTimeout(4000); // let assets settle in real time
  await page.addStyleTag({ content: HIDE_CSS });
  await page.evaluate((passive) => {
    const g = window.__game;
    if (passive) for (const ai of [g.ai, g.ai1]) if (ai) { ai.passive = true; ai.aggression = 0; }
    // Gate the authored camera; the capture script drives it every frame.
    if (typeof g.arena.setFreeCamera === 'function') g.arena.setFreeCamera(true); else g.arena.freeCameraActive = true;
    window.__vclock.begin();
  }, aiPassive);
}
// Camera shots: computed from the live fighter positions each frame.
export async function frame(page, shot = {}, dt = 1000 / 30) {
  return page.evaluate(([shot, dt]) => {
    const g = window.__game, cam = g.arena.camera;
    const a = g.p1.root.position, b = g.p2.root.position;
    const focus = shot.focus === 'p1' ? a : shot.focus === 'p2' ? b : null;
    const mx = focus ? focus.x : (a.x + b.x) / 2, mz = focus ? focus.z : (a.z + b.z) / 2;
    const span = Math.hypot(a.x - b.x, a.z - b.z);
    const dist = shot.dist != null ? shot.dist : Math.max(2.6, span * 0.85 + 1.6);
    const yaw = shot.yaw || 0, h = shot.height != null ? shot.height : 1.25, ty = shot.lookY != null ? shot.lookY : 1.05;
    cam.position.set(mx + Math.sin(yaw) * dist, h, mz + Math.cos(yaw) * dist);
    if (shot.fov) { cam.fov = shot.fov; cam.updateProjectionMatrix(); }
    cam.lookAt(mx, ty, mz);
    window.__vclock.step(dt);
    const st = f => ({ hp: f.hp, state: f.state, atk: f.attackName && (f.attackName.name || f.attackName) || null,
      t7: f._t7gActionName ? (typeof f._t7gActionName === 'function' ? null : f._t7gActionName) : null, x: +f.root.position.x.toFixed(2) });
    return { t: window.__vclock.now(), p1: st(g.p1), p2: st(g.p2) };
  }, [shot, dt]);
}
export async function key(page, code, down) { if (down) await page.keyboard.down(code); else await page.keyboard.up(code); }
export function ensureDir(d) { fs.mkdirSync(d, { recursive: true }); return d; }
