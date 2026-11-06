#!/usr/bin/env python3
"""Roster-100 item 5 (L5) fight probe: CD context + directional sidestep in
real fights, driven through the fighter's own public input methods
(tryAttack / trySidestep — the same calls game.js makes), fixed-step.

Usage: probe_i5.py <p1> <base_url> <out.json>
Cases are chosen by p1: rin/demonio/gyou -> CD sequence + neutral control;
purplerain/negativo -> SSL/SSR sidestep sequences. Opponent is pantera.

Findings (2026-11-06, docs/proof/2026-11-06/item5-l5-contexts/): demonio and
rin CD.d/f+2 fire from the raw f,n,d,d/f motion and connect; gyou CD.3 fires
from d,d/f on a bare press inside the latch window, connects, and chains
into LFS exactly as his stance_after declares (CD.4 fires the same way; with
d/f held the engine's attached-direction d/f+3 wins, the same candidate
order that fires CD.d/f+2 for rin/demonio); Purplerain SSL.3+4 (25.8) /
SSR.3+4 (26.7) fire directionally and the post-step _foeFlank reads L / R as
the ssSide convention predicts; Negativo SSL.2 (9.9) / SSR.2 fire
directionally after the side-prefix priority fix (previously the generic
SS.2 shadowed them).
"""
import sys, json, time, glob
from playwright.sync_api import sync_playwright

FID = sys.argv[1]
BASE = sys.argv[2]
OUT = sys.argv[3]
OPP = 'pantera'

DRIVER = r"""
async (spec) => {
  const g = window.__game, f = g.p1, v = g.p2, DT = 1 / 120;
  const canAct = (x) => (typeof x.canAct === 'function' ? x.canAct() : x.state === 'idle');
  const settle = () => { for (let i = 0; i < 2400 && !(canAct(f) && canAct(v)); i++) g._update(DT); for (let i = 0; i < 12; i++) g._update(DT); };
  const place = () => { v.hp = v.maxHp; f.root.position.x = v.root.position.x - (f.facing || 1) * 1.1; f.root.position.z = v.root.position.z; };
  settle(); place();
  let hp0 = v.hp;
  const out = { fid: f.char.id, steps: [] };
  const snap = (tag) => ({ tag, state: f.state, atk: f.attackName, stance: f.stance,
    cd: f.tekken && f.tekken.cdActive ? f.tekken.cdActive() : null,
    ssSide: (() => { try { return f._inputCtx().ssSide; } catch (e) { return 'ERR'; } })(),
    flank: (() => { try { return f._foeFlank(); } catch (e) { return 'ERR'; } })(),
    hpDelta: +(hp0 - v.hp).toFixed(1) });
  for (const st of spec) {
    if (st.do === 'attack') { const ok = f.tryAttack(st.name); out.steps.push({ ...snap('attack:' + st.name), ok }); }
    else if (st.do === 'dirs') { for (const d of st.dirs) { f.tekken.noteDirection(d, 1 / 60); g._update(DT); g._update(DT); } out.steps.push(snap('dirs:' + st.dirs.join(','))); }
    else if (st.do === 'hold') { f.tekken.noteDirection(st.dir, 1 / 60); out.steps.push(snap('hold:' + st.dir)); }
    else if (st.do === 'step') { for (let i = 0; i < st.n; i++) g._update(DT); out.steps.push(snap('step' + st.n)); }
    else if (st.do === 'sidestep') { const ok = f.trySidestep(st.dir); out.steps.push({ ...snap('sidestep:' + st.dir), ok }); }
    else if (st.do === 'settle') { settle(); place(); hp0 = v.hp; out.steps.push(snap('settle')); }
  }
  return out;
}
"""

CASES = {
    'rin': [
        {'do': 'dirs', 'dirs': ['f', 'n', 'd', 'd/f']},
        {'do': 'hold', 'dir': 'd/f'},
        {'do': 'attack', 'name': '2'}, {'do': 'step', 'n': 110},
        {'do': 'settle'},
        {'do': 'attack', 'name': 'd/f+2'}, {'do': 'step', 'n': 110},
    ],
    'demonio': [
        {'do': 'dirs', 'dirs': ['f', 'n', 'd', 'd/f']},
        {'do': 'hold', 'dir': 'd/f'},
        {'do': 'attack', 'name': '2'}, {'do': 'step', 'n': 110},
        {'do': 'settle'},
        {'do': 'attack', 'name': 'd/f+2'}, {'do': 'step', 'n': 110},
        {'do': 'settle'},
        {'do': 'attack', 'name': 'f,n,d,df'}, {'do': 'step', 'n': 6},
        {'do': 'attack', 'name': '2'}, {'do': 'step', 'n': 110},
    ],
    'gyou-close34': [
        {'do': 'dirs', 'dirs': ['d', 'd/f']}, {'do': 'hold', 'dir': 'd/f'},
        {'do': 'dirs', 'dirs': ['n']},
        {'do': 'attack', 'name': '3'}, {'do': 'step', 'n': 130},
        {'do': 'settle'},
        {'do': 'dirs', 'dirs': ['d', 'd/f']}, {'do': 'hold', 'dir': 'd/f'},
        {'do': 'dirs', 'dirs': ['n']},
        {'do': 'attack', 'name': '4'}, {'do': 'step', 'n': 130},
    ],
    'gyou-close': [
        {'do': 'dirs', 'dirs': ['d', 'd/f']}, {'do': 'hold', 'dir': 'd/f'},
        {'do': 'attack', 'name': '2'}, {'do': 'step', 'n': 110},
    ],
    'gyou': [
        {'do': 'dirs', 'dirs': ['d', 'd/f']},
        {'do': 'hold', 'dir': 'd/f'},
        {'do': 'attack', 'name': '3'}, {'do': 'step', 'n': 110},
        {'do': 'settle'},
        {'do': 'attack', 'name': '3'}, {'do': 'step', 'n': 110},
    ],
    'purplerain-ssr': [
        {'do': 'sidestep', 'dir': -1}, {'do': 'step', 'n': 20},
        {'do': 'attack', 'name': '3+4'}, {'do': 'step', 'n': 110},
        {'do': 'settle'},
        {'do': 'sidestep', 'dir': -1}, {'do': 'step', 'n': 80},
    ],
    'negativo': [
        {'do': 'sidestep', 'dir': 1}, {'do': 'step', 'n': 20},
        {'do': 'attack', 'name': '2'}, {'do': 'step', 'n': 110},
        {'do': 'settle'},
        {'do': 'sidestep', 'dir': -1}, {'do': 'step', 'n': 20},
        {'do': 'attack', 'name': '2'}, {'do': 'step', 'n': 110},
    ],
    'purplerain': [
        {'do': 'sidestep', 'dir': 1}, {'do': 'step', 'n': 20},
        {'do': 'attack', 'name': '3+4'}, {'do': 'step', 'n': 110},
        {'do': 'settle'},
        {'do': 'sidestep', 'dir': -1}, {'do': 'step', 'n': 20},
        {'do': 'attack', 'name': '3+4'}, {'do': 'step', 'n': 110},
        {'do': 'settle'},
        {'do': 'sidestep', 'dir': 1}, {'do': 'step', 'n': 80},
    ],
    'negativo': [
        {'do': 'sidestep', 'dir': 1}, {'do': 'step', 'n': 20},
        {'do': 'attack', 'name': '2'}, {'do': 'step', 'n': 110},
        {'do': 'settle'},
        {'do': 'sidestep', 'dir': -1}, {'do': 'step', 'n': 20},
        {'do': 'attack', 'name': '2'}, {'do': 'step', 'n': 110},
    ],
}


def main():
    shells = sorted(glob.glob('/home/hatch/.cache/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell'))
    shell = shells[-1]
    # case names may carry a suffix (gyou-close34, purplerain-ssr); the fighter
    # id is the part before the first '-' — the quick URL and the ready check
    # must use the fighter id, the CASES lookup keeps the full case name.
    fighter = FID.split('-')[0]
    result = {'p1': fighter, 'case': FID, 'p2': OPP, 'base': BASE, 'ready': False}
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=shell, args=[
            '--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader',
            '--ignore-gpu-blocklist', '--no-sandbox', '--hide-scrollbars', '--mute-audio',
            '--disable-background-timer-throttling', '--disable-renderer-backgrounding', '--no-first-run'])
        page = browser.new_page(viewport={'width': 640, 'height': 480})
        logs = []
        page.on('pageerror', lambda e: logs.append(f'[pageerror] {str(e)[:240]}'))
        try:
            page.goto(f'{BASE}?quick={fighter},{OPP},shrine', wait_until='load', timeout=600000)
            t0 = time.time()
            ready = False
            while time.time() - t0 < 900:
                try:
                    ready = page.evaluate("""(fid) => { const g = window.__game; return !!(g && g.p1 && g.p1.char && g.p1.char.id === fid && g.roundState === 'fight'); }""", fighter)
                except Exception:
                    ready = False
                if ready:
                    break
                try:
                    page.wait_for_timeout(1000)
                except Exception:
                    pass
            result['ready'] = bool(ready)
            if not ready:
                result['error'] = 'fight never reached roundState=fight'
                result['logs'] = logs[-20:]
                return
            result['run'] = page.evaluate(DRIVER, CASES[FID])
            result['logs'] = logs[-10:]
        finally:
            browser.close()
            with open(OUT, 'w') as fh:
                json.dump(result, fh, indent=1)
            print(json.dumps(result, indent=1)[:3000])


if __name__ == '__main__':
    main()
