#!/usr/bin/env python3
"""S7 throw-execution probe: for one (thrower, victim) pair, load a real fight
on a served tree of main, then run a controlled SEQUENCE of inputs in one
match session (state carries between trials, like a real match). Per trial:
resolved move snapshot, plan attribution, pair-vs-legacy path evidence
(_throwPair sampling + [WH-THROW] console lines), victim state transitions,
first-damage time, and victim HP delta. HP is refilled between trials so a
KO never ends the sequence; no engine flag is touched.

Usage: probe_s7.py <thrower> <victim> <base_url> <out.json> <input1,input2,...>
Adapted from the S5 lane's probe_s5.py (identity gate + fixed-step driver).
"""
import glob, json, sys, time
from playwright.sync_api import sync_playwright

FID, OPP, BASE, OUT = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
INPUTS = sys.argv[5].split(',')

SETUP_JS = r"""
() => {
  const g = window.__game;
  g.ai = { update() {}, reset() {} };
  g.p1.hp = g.p1.maxHp = 1e6; g.p2.hp = g.p2.maxHp = 1e6;
  g.roundTime = 0; g.timer = Infinity;
  g.paused = true;
  if (!window.__whlogs) {
    window.__whlogs = [];
    const orig = console.log.bind(console);
    console.log = (...a) => { try { window.__whlogs.push(a.map(x => String(x)).join(' ')); } catch (e) {} orig(...a); };
  }
  const info = (f) => ({ id: f.char ? f.char.id : null,
    t3dir: f._t3 ? (f._t3.dir || null) : null, t3bank: f._t3 ? (f._t3.bank || null) : null,
    t3actions: f.t3actions ? Object.keys(f.t3actions).length : null });
  return { roundState: g.roundState, p1: info(g.p1), p2: info(g.p2) };
}
"""

TRIAL_JS = r"""
async (n) => {
  const g = window.__game, f = g.p1, v = g.p2;
  const DT = 1 / 120;
  const canAct = (x) => (typeof x.canAct === 'function' ? x.canAct() : x.state === 'idle');
  const log0 = window.__whlogs.length;
  for (let i = 0; i < 1200 && !(canAct(f) && canAct(v)); i++) g._update(DT);
  for (let i = 0; i < 1200 && v.state !== 'idle'; i++) g._update(DT);
  for (let i = 0; i < 12; i++) g._update(DT);
  v.hp = v.maxHp;
  f.root.position.x = v.root.position.x - (f.facing || 1) * 1.1;
  f.root.position.z = v.root.position.z;
  const hp0 = v.hp;
  let ok = false, err = null;
  try { ok = f.tryAttack(n); } catch (e) { err = String(e.message || e).slice(0, 160); }
  const atk = f.attack ? { name: f.attackName, damage: f.attack.damage,
      isGrab: !!f.attack.isGrab, move_class: f.attack.move_class || null,
      throw: !!f.attack.throw, anim_ref: f.attack.anim_ref || null,
      t3_row: f.attack.t3_row != null ? f.attack.t3_row : null } : null;
  const plan = f._atkPlan ? { name: f._atkPlan.name || null, kind: f._atkPlan.kind || null,
      why: (f._atkPlan.why || '').slice(0, 120) } : null;
  const trans = []; let last = ''; let firstDmgT = null, pairSeen = false, lockSeen = false;
  let t = 0;
  for (let i = 0; i < 600; i++) {
    g._update(DT); t += DT;
    const pair = !!(f._throwPair || v._throwPair);
    if (pair) pairSeen = true;
    if (v.state === 'thrown' && !pair) lockSeen = true;
    const key = f.state + '|' + v.state + '|' + (pair ? 'P' : '-');
    if (key !== last) { trans.push({ t: +t.toFixed(3), p1: f.state, p2: v.state, pair }); last = key; }
    if (firstDmgT === null && v.hp < hp0) firstDmgT = +t.toFixed(3);
    if (t > 1.0 && canAct(f) && canAct(v)) break;
  }
  return { n, ok, err, atk, plan, pairSeen, lockSeen,
    hpDelta: +(hp0 - v.hp).toFixed(1), firstDmgT,
    vThrowHitDone: v._throwHitDone != null ? v._throwHitDone : null,
    whLogs: window.__whlogs.slice(log0).filter(s => s.includes('WH-THROW') || s.includes('throw')).slice(0, 8),
    trans: trans.slice(0, 48), p1state: f.state, p2state: v.state };
}
"""


def main():
    shell = glob.glob('/home/hatch/.cache/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell')[0]
    result = {'thrower': FID, 'victim': OPP, 'base': BASE, 'ready': False, 'trials': []}
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=shell, args=[
            '--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader',
            '--ignore-gpu-blocklist', '--no-sandbox', '--hide-scrollbars', '--mute-audio',
            '--disable-background-timer-throttling', '--disable-renderer-backgrounding', '--no-first-run'])
        page = browser.new_page(viewport={'width': 640, 'height': 480})
        logs = []
        page.on('pageerror', lambda e: logs.append(f'[pageerror] {str(e)[:240]}'))
        page.on('response', lambda r: logs.append(f'[http {r.status}] {r.url[-90:]}') if r.status >= 400 else None)
        try:
            page.goto(f'{BASE}?quick={FID},{OPP},shrine', wait_until='load', timeout=600000)
            t0 = time.time()
            ready = False
            while time.time() - t0 < 900:
                try:
                    ready = page.evaluate("""(fid) => { const g = window.__game; return !!(g && g.p1 && g.p1.char && g.p1.char.id === fid && g.roundState === 'fight'); }""", FID)
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
                result['logs'] = logs[-40:]
                return
            result['setup'] = page.evaluate(SETUP_JS)
            for n in INPUTS:
                try:
                    r = page.evaluate(TRIAL_JS, n)
                except Exception as e:
                    r = {'n': n, 'ok': False, 'err': str(e)[:200]}
                result['trials'].append(r)
                print(FID, 'vs', OPP, n.ljust(6), 'ok=', r.get('ok'), 'plan=', (r.get('plan') or {}).get('name'),
                      'pair=', r.get('pairSeen'), 'lock=', r.get('lockSeen'), 'dmg=', r.get('hpDelta'),
                      'firstDmgT=', r.get('firstDmgT'), r.get('err') or '', flush=True)
            result['logs'] = logs[-30:]
        finally:
            browser.close()
            with open(OUT, 'w') as fh:
                json.dump(result, fh, indent=1)
            print('SAVED', OUT, 'ready=', result['ready'])


if __name__ == '__main__':
    main()
