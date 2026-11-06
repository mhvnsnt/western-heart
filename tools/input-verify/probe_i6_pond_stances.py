"""Item-6 probe: Pond stance-row clip verification through the REAL player input path.

Harness recipe copied from the Wave 3 lanes' probe_i5.py: Playwright headless
shell, the game's ?quick=<p1>,<p2>,<stage> boot (the game's own fight setup),
a 900 s ready poll for roundState 'fight', then fixed-step driving through the
fighter's public input methods — the same calls game.js makes:
  - button steps: tryAttack(chord)
  - directional steps: tekken.noteDirection(dir) first, then the chord press
  - stance-transition tails (F / U / B): Fighter.tryDirFollow(dir)

For each spec row: settle both fighters, place Pond 1.1 m from the foe, set
Pond's stance directly (the stance state is the unit under test — the entries
are tested separately), feed the row's tail, and while stepping record the
fired move key, the attack plan (name/kind/why), whether a real bank clip ran
(maxWeight / sawRunning), the T-pose bind fraction, and HP delta on the foe.

Entry tests: from a settled neutral state, the entry input through the same
player path (b+3+4 = noteDirection('b') + press '3+4'; 3+4 = press; qcf =
tryAttack('qcf') invocation + the raw stick motion), recording the stance
before/after and whether a follow-up row then fires through the buffer.

Usage: probe_i6.py <base_url_with_trailing_slash> <spec.json> <out.json>
"""
import json, sys, time, glob, os
from playwright.sync_api import sync_playwright

BASE, SPEC_PATH, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
spec = json.load(open(SPEC_PATH))
FID, FOE, STAGE = spec['fighter'], spec['foe'], spec.get('stage', 'shrine')

ROWJS = r"""
async (arg) => {
  const { slot, targetKey, stance, tail } = arg;
  const g = window.__game, f = g.p1, o = g.p2, DT = 1 / 120;
  const out = { slot, targetKey, stance, tail };
  const canAct = (x) => (typeof x.canAct === 'function' ? x.canAct() : x.state === 'idle');
  const step = (n) => { for (let i = 0; i < n; i++) g._update(DT); };
  const settle = () => { for (let i = 0; i < 2400 && !(canAct(f) && canAct(o)); i++) g._update(DT); for (let i = 0; i < 12; i++) g._update(DT); };
  const place = () => { o.hp = o.maxHp; f.hp = f.maxHp; f.root.position.x = o.root.position.x - (f.facing || 1) * 1.1; f.root.position.z = o.root.position.z; };
  try {
    settle();
    for (const x of [f, o]) {
      x.stance = null; x.hitDone = false;
      x._queuedNext = null; x._stepChain = null;
      x.tekken.lastMove = null; x.tekken._cdUntil = 0; x.tekken._ssUntil = 0;
      if (x.clearTransientStance) x.clearTransientStance();
    }
    place(); g.timer = 9999; step(6);
    const hp0 = o.hp;
    let maxW = 0, sawRunning = false, bindFrames = 0, frames = 0, firedKey = null, plan = null;
    const sample = () => {
      frames++;
      const a = f.attackName || (f.attack && f.attack.key);
      if (a) { firedKey = a; if (f._plan) plan = { name: f._plan.name, kind: f._plan.kind, why: f._plan.why }; }
      const lm = f.tekken && f.tekken.lastMove;
      if (lm && lm !== firedKey) out.lastMoveSeen = lm;
      if (f.t3actions) {
        let top = 0, any = false;
        for (const k in f.t3actions) { const ac = f.t3actions[k]; const w = ac.getEffectiveWeight(); if (w > top) top = w; if (ac.isRunning() && w > 0.05) any = true; }
        if (top > maxW) maxW = top;
        if (any) sawRunning = true;
        if (top < 0.2) bindFrames++;
      }
    };
    const DIRS = new Set(['f','b','u','d','u/f','d/f','u/b','d/b','n']);
    const isTransition = /^(F|B|U|D)(\/(F|B))?$/.test(tail);
    const arm = () => { if (stance) { f.stance = stance; f.stanceT = 999; } };
    arm();
    if (isTransition) {
      f.tryDirFollow(tail.toLowerCase());
      for (let i = 0; i < 360; i++) { step(1); sample(); }
    } else {
      const steps = tail.split(',');
      let fed = true;
      for (const st of steps) {
        const m = st.match(/^(?:(u\/f|d\/f|u\/b|d\/b|f|b|u|d)\+)?((?:[1-4]\+?)+)?$/i);
        const holdM = st.match(/^([A-Z])(\/[A-Z])?$/);
        if (holdM && !st.includes('+')) {
          f.tekken.noteDirection(st.toLowerCase(), 1/60); step(6);
        } else if (m && (m[1] || m[2])) {
          if (m[1]) { f.tekken.noteDirection(m[1].toLowerCase(), 1/60); arm(); }
          if (m[2]) {
            const ok = f.tryAttack(m[2]);
            if (!ok && steps.length === 1) fed = false;
            step(24);
          } else step(4);
        } else if (DIRS.has(st.toLowerCase())) {
          f.tekken.noteDirection(st.toLowerCase(), 1/60); step(4);
        } else {
          const ok = f.tryAttack(st);
          if (!ok && steps.length === 1) fed = false;
          step(24);
        }
        sample(); arm();
      }
      for (let i = 0; i < 420; i++) {
        if (stance && !f.attack) arm();
        step(1); sample();
      }
      out.fed = fed;
    }
    out.firedKey = firedKey;
    out.plan = plan;
    out.maxWeight = +maxW.toFixed(3);
    out.sawRunning = sawRunning;
    out.bindFrac = frames ? +(bindFrames / frames).toFixed(2) : 1;
    out.hpDelta = +(hp0 - o.hp).toFixed(1);
    out.stanceEnd = f.stance || null;
    out.fHp = f.hp;
  } catch (e) { out.error = String(e && e.message || e).slice(0, 200); }
  return out;
}
"""

ENTRYJS = r"""
async (arg) => {
  const { input, follow } = arg;
  const g = window.__game, f = g.p1, o = g.p2, DT = 1 / 120;
  const out = { input, follow };
  const canAct = (x) => (typeof x.canAct === 'function' ? x.canAct() : x.state === 'idle');
  const step = (n) => { for (let i = 0; i < n; i++) g._update(DT); };
  const settle = () => { for (let i = 0; i < 2400 && !(canAct(f) && canAct(o)); i++) g._update(DT); for (let i = 0; i < 12; i++) g._update(DT); };
  const place = () => { o.hp = o.maxHp; f.hp = f.maxHp; f.root.position.x = o.root.position.x - (f.facing || 1) * 1.1; f.root.position.z = o.root.position.z; };
  const clean = () => {
    f.stance = null; f.hitDone = false; f._queuedNext = null; f._stepChain = null;
    f.tekken.lastMove = null; f.tekken._cdUntil = 0; f.tekken._ssUntil = 0;
    if (f.clearTransientStance) f.clearTransientStance();
  };
  // Fire once and watch the whole move: returns { fired, stanceSeen } — stanceSeen is any
  // stance observed during/after the move (the stance window is 0.8 s of sim time, so a
  // post-settle read is too late; the stance must be caught while it is live).
  const watch = (fireFn, ticks) => {
    fireFn();
    let fired = null, stanceSeen = null;
    for (let i = 0; i < (ticks || 480); i++) {
      step(1);
      const a = f.attackName || (f.attack && f.attack.key);
      if (a) fired = a;
      if (f.stance) stanceSeen = f.stance;
      if (i > 90 && canAct(f) && !f.attack && stanceSeen) break;
      if (i > 90 && canAct(f) && !f.attack && !stanceSeen && i > 200) break;
    }
    return { fired, stanceSeen };
  };
  try {
    settle(); clean(); place(); g.timer = 9999; step(6);
    out.stanceBefore = f.stance || null;
    if (input === 'b+3+4') {
      const r = watch(() => { f.tekken.noteDirection('b', 1/60); f.tryAttack('3+4'); });
      out.firedKey = r.fired; out.stanceAfter = r.stanceSeen;
    } else if (input === '3+4') {
      const r = watch(() => f.tryAttack('3+4'));
      out.firedKey = r.fired; out.stanceAfter = r.stanceSeen;
    } else if (input === 'qcf') {
      const r1 = watch(() => f.tryAttack('qcf'));
      out.viaInvoke = { fired: r1.fired, stance: r1.stanceSeen };
      settle(); clean(); place(); step(6);
      const r2 = watch(() => { for (const d of ['d', 'd/f', 'f']) { f.tekken.noteDirection(d, 1/60); step(3); } }, 240);
      out.viaStick = { fired: r2.fired, stance: r2.stanceSeen };
      settle(); clean(); place(); step(6);
      const r3 = watch(() => f.tryAttack('qcf'));
      out.firedKey = r3.fired; out.stanceAfter = r3.stanceSeen;
    }
    if (follow) {
      // Re-enter and press the follow-up the moment the stance is live and Pond can act —
      // the way a player does (inside the 0.8 s stance window, not after a full settle).
      settle(); clean(); place(); g.timer = 9999; step(6);
      const hp0 = o.hp;
      if (input === 'b+3+4') { f.tekken.noteDirection('b', 1/60); f.tryAttack('3+4'); }
      else f.tryAttack(input);
      let ff = null, maxW = 0, pressed = false, stanceLive = null;
      for (let i = 0; i < 600; i++) {
        step(1);
        if (f.stance) stanceLive = f.stance;
        if (!pressed && stanceLive && canAct(f) && !f.attack) { f.tryAttack(follow); pressed = true; }
        if (pressed) {
          const a = f.attackName || (f.attack && f.attack.key);
          if (a) ff = a;
          if (f.t3actions) for (const k in f.t3actions) { const w = f.t3actions[k].getEffectiveWeight(); if (w > maxW) maxW = w; }
          if (i > 60 && canAct(f) && !f.attack && ff) break;
        }
        if (i > 300 && !pressed) break;
      }
      out.followResult = { fired: ff, pressed, stanceLive, maxWeight: +maxW.toFixed(3), hpDelta: +(hp0 - o.hp).toFixed(1) };
    }
  } catch (e) { out.error = String(e && e.message || e).slice(0, 200); }
  return out;
}
"""

def outcome(r):
    if r.get('error'): return 'ERROR'
    tgt = r.get('targetKey')
    def on_target(k):
        return bool(k) and (k == tgt or (tgt and k.startswith(tgt + ',')) or (tgt and k == tgt.split('~')[0]))
    fk = r.get('firedKey')
    if on_target(r.get('lastMoveSeen')) and not on_target(fk): fk = r.get('lastMoveSeen')
    if not fk: return 'NOFIRE'
    clip = (r.get('maxWeight', 0) >= 0.2 or r.get('sawRunning')) and r.get('bindFrac', 1) < 0.7
    if on_target(fk) and clip: return 'RESOLVED-CLIP'
    if on_target(fk): return 'RESOLVED-NOPLAN'
    return 'WRONG-MOVE'

def main():
    shells = sorted(glob.glob(os.path.expanduser('~/.cache/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell')))
    shell = shells[-1]
    results = {'entries': [], 'rows': [], 'ready': False}
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=shell, args=[
            '--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader',
            '--ignore-gpu-blocklist', '--no-sandbox', '--hide-scrollbars', '--mute-audio',
            '--disable-background-timer-throttling', '--disable-renderer-backgrounding', '--no-first-run'])
        page = browser.new_page(viewport={'width': 640, 'height': 480})
        logs = []
        page.on('pageerror', lambda e: logs.append(f'[pageerror] {str(e)[:240]}'))
        fb = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'repo', 'game', 'assets', 'models', 'pantera.glb'), 'rb').read()
        def roster_route(route):
            url = route.request.url
            if '/tsuyu-asui/' in url: return route.continue_()
            if url.split('?')[0].endswith('.glb'):
                return route.fulfill(status=200, content_type='model/gltf-binary', body=fb)
            return route.continue_()
        page.route('**/roster/**', roster_route)
        def models_route(route):
            if 'pantera' in route.request.url: return route.continue_()
            return route.fulfill(status=200, content_type='model/gltf-binary', body=fb)
        page.route('**/game/assets/models/*.glb', models_route)
        def boot(pg):
            pg.goto(f'{BASE}?quick={FID},{FOE},{STAGE}', wait_until='load', timeout=600000)
            t0 = time.time()
            ok = False
            while time.time() - t0 < 900:
                try:
                    ok = pg.evaluate("""(fid) => { const g = window.__game; return !!(g && g.p1 && g.p1.char && g.p1.char.id === fid && g.roundState === 'fight'); }""", FID)
                except Exception:
                    ok = False
                if ok: break
                pg.wait_for_timeout(1000)
            return ok
        try:
            results['ready'] = bool(boot(page))
            print('READY', results['ready'], flush=True)
            if not results['ready']:
                results['logs'] = logs[-20:]
                json.dump(results, open(OUT, 'w'), indent=1)
                print('WROTE', OUT, '(not ready)', flush=True)
                return
            for e in spec.get('entries', []):
                r = page.evaluate(ENTRYJS, {'input': e['input'], 'follow': e.get('follow')})
                results['entries'].append(r)
                print(f"ENTRY {e['input']:8} -> fired={r.get('firedKey')} stance={r.get('stanceAfter')} follow={r.get('followResult')}", flush=True)
            page.close()
            page2 = browser.new_page(viewport={'width': 640, 'height': 480})
            page2.on('pageerror', lambda e: logs.append(f'[pageerror rows] {str(e)[:240]}'))
            page2.route('**/roster/**', roster_route)
            page2.route('**/game/assets/models/*.glb', models_route)
            results['rowsReady'] = bool(boot(page2))
            print('ROWS READY', results['rowsReady'], flush=True)
            if results['rowsReady']:
                for row in spec['rows']:
                    r = page2.evaluate(ROWJS, {'slot': row['slot'], 'targetKey': row['targetKey'],
                                              'stance': row.get('stance'), 'tail': row['tail']})
                    r['outcome'] = outcome(r)
                    results['rows'].append(r)
                    print(f"{r['outcome']:15} {row['slot']:28} -> {r.get('firedKey')} | {r.get('plan') and r['plan'].get('name')} hp={r.get('hpDelta')}", flush=True)
            results['logs'] = logs[-10:]
        finally:
            browser.close()
    json.dump(results, open(OUT, 'w'), indent=1)
    print('WROTE', OUT, flush=True)

if __name__ == '__main__':
    main()
