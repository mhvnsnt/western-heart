// godwithin: God Within mode tap-path e2e (branch godwithin/wiring-20261126).
// iPhone-13 profile (hasTouch, 390x844). Serve the repo root on $WH_URL
// (default http://127.0.0.1:8811). Run: node test/e2e/godwithin.e2e.mjs [shotsDir]
// 1) the GOD WITHIN menu card is topmost at its centre (nothing eats the tap)
// 2) menu -> STORY rail -> GOD WITHIN card -> select pantera -> confirm
//    -> rung-1 stage intro (guardian foe named, shards shown)
// 3) tap FIGHT -> HUD up, fight live (pantera vs the rung-1 guardian)
// 4) lose the match (p1 hp zeroed via the __game hook, mirror of the
//    menu-touch REMATCH KO loop — best of 3, so up to 3 rounds) ->
//    one LSD dream night -> reincarnate screen with the RNF face strip
//    title, the SAIL button and vessel cards
// 5) SAIL -> Banabana hub overlay mounts -> sail once (status "Sailed to")
//    -> close -> back on the reincarnate screen
// 6) pick a vessel card -> same rung, new vessel (stage kicker: DEATH 1)
// Notes: the two cutscenes on this path (story.intro LOGO.mp4,
// reincarn.flash ANIM01.mp4) live under ../teardown/, outside CI's sparse
// checkout, so the video errors and playCutscene() resolves at once in CI.
// The RNF face-piece imgs 404 for the same reason and hide themselves
// (img.onerror) — the test asserts the strip TITLE text, not the imgs.
// The foe is NOT asserted by id: if the guardian GLB ever fails to load,
// the mode falls back to a pool draw (modes.js _godwithinFight) — the
// test proves the fight starts and the death flow runs, whatever the foe.
import { chromium, devices } from 'playwright';
import fs from 'node:fs';
const BASE = process.env.WH_URL || 'http://127.0.0.1:8811';
const SHOTS = process.argv[2] || 'godwithin-shots';
fs.mkdirSync(SHOTS, { recursive: true });
const fails = [];
const b = await chromium.launch();
const ctx = await b.newContext({ ...devices['iPhone 13'], viewport: { width: 390, height: 844 }, hasTouch: true, isMobile: true });
const p = await ctx.newPage();
p.on('pageerror', (e) => console.log('PAGEERROR:', String(e).slice(0, 300)));
const visible = (id) => p.evaluate((i) => { const e = document.getElementById(i); return e && getComputedStyle(e).display !== 'none' && !e.classList.contains('hidden'); }, id);
const scr = () => p.evaluate(() => ['screen-menu', 'screen-select', 'screen-stage', 'screen-stage-intro', 'screen-reincarnate', 'hud'].filter((id) => { const e = document.getElementById(id); return e && getComputedStyle(e).display !== 'none' && !e.classList.contains('hidden'); }));

await p.goto(BASE + '/game/index.html?roster=all');
await p.waitForSelector('#screen-menu [data-mm]', { state: 'visible', timeout: 30000 });
await p.waitForTimeout(5000); // past the tap-hint and failsafe timers
await p.waitForFunction(() => !!window.__modes, null, { timeout: 120000 });
await p.evaluate(() => {
  window.__clicks = [];
  document.addEventListener('click', (e) => {
    const el = e.target.closest && e.target.closest('[data-action]');
    if (el) window.__clicks.push(el.dataset.action + (e.isTrusted ? ':trusted' : ':synth'));
  }, true);
});

// 1) GOD WITHIN card: open the STORY submenu first (the card lives
//    inside it, mainmenu.js SUBMENUS.story — not on the bare menu),
//    then check the card is topmost at its centre, >= 44px.
try {
  await p.tap('[data-mm="story"]', { timeout: 90000 });
  await p.waitForFunction(() => { const s = document.getElementById('mm-submenu'); const c = document.querySelector('[data-action="mode-godwithin"]'); return s && !s.hidden && c && getComputedStyle(c).display !== 'none'; }, null, { timeout: 60000 });
  // The submenu slides in — measure only once the card's rect has
  // settled (C9 measured mid-transition: elementFromPoint returned
  // null for a centre still outside the viewport).
  await p.waitForFunction(() => {
    const el = document.querySelector('[data-action="mode-godwithin"]');
    if (!el) return false;
    const r1 = el.getBoundingClientRect();
    return new Promise((res) => setTimeout(() => {
      const r2 = el.getBoundingClientRect();
      res(r1.x === r2.x && r1.y === r2.y && r1.width === r2.width && r1.height === r2.height);
    }, 300));
  }, null, { timeout: 30000 });
  const card = await p.evaluate(() => {
    const el = document.querySelector('[data-action="mode-godwithin"]');
    if (!el) return null;
    el.scrollIntoView({ block: 'center' });
    const r = el.getBoundingClientRect();
    const t = document.elementFromPoint(r.x + r.width / 2, r.y + r.height / 2);
    return { h: Math.round(r.height), hit: !!t && (t === el || el.contains(t)), top: t ? (t.id || t.className || t.tagName) : null, text: el.textContent.slice(0, 40) };
  });
  if (!card) fails.push('menu: no [data-action="mode-godwithin"] card');
  else {
    console.log('menu: GOD WITHIN card', JSON.stringify(card));
    if (!card.hit) fails.push(`menu: GOD WITHIN card covered by ${card.top}`);
    if (card.h < 44) fails.push(`menu: GOD WITHIN card hit area ${card.h}px < 44px`);
  }
  await p.screenshot({ path: `${SHOTS}/01-menu-godwithin.png` });
} catch (e) { fails.push('menu card check: ' + e.message.split('\n')[0]); }

// 2) menu -> GOD WITHIN -> select pantera -> rung-1 stage intro
//    (guardian foe named, shards shown). GOD WITHIN is a card inside
//    the STORY submenu (mainmenu.js SUBMENUS.story) — the submenu is
//    closed on load, so the card is not in the DOM until the STORY
//    rail item is tapped (C8 tapped the card on the bare menu and
//    failed here; the fix is the rail tap first).
try {
  await p.tap('[data-action="mode-godwithin"]', { timeout: 90000 });
  await p.waitForFunction(() => { const e = document.getElementById('screen-select'); return e && getComputedStyle(e).display !== 'none' && !e.classList.contains('hidden'); }, null, { timeout: 120000 });
  await p.screenshot({ path: `${SHOTS}/02-select.png` });
  await p.tap('.char-card[data-id="pantera"]', { timeout: 90000 });
  await p.tap('#confirm-fighter', { timeout: 90000 });
  // The rung intro is #screen-stage-intro (ENTER button #stage-fight),
  // NOT #screen-stage — that id is the CHOOSE YOUR ARENA picker, whose
  // CONFIRM is a no-op without a versus pendingFight (C9 waited on the
  // picker while the intro text sat on the hidden panel).
  await p.waitForFunction(() => { const e = document.getElementById('screen-stage-intro'); return e && getComputedStyle(e).display !== 'none' && !e.classList.contains('hidden'); }, null, { timeout: 300000 });
  const intro = await p.evaluate(() => ({
    title: document.getElementById('stage-title')?.textContent || '',
    foe: document.getElementById('stage-foe')?.textContent || '',
    reward: document.getElementById('stage-reward')?.textContent || '',
  }));
  console.log('stage intro:', JSON.stringify(intro));
  if (!intro.title) fails.push('stage intro: empty stage title');
  if (!intro.foe.includes('GUARDIAN')) fails.push('stage intro: rung-1 foe is not a guardian: ' + intro.foe);
  await p.screenshot({ path: `${SHOTS}/03-stage-intro.png` });
} catch (e) { fails.push('mode entry: ' + e.message.split('\n')[0] + ' on ' + JSON.stringify(await scr())); }

// 3) FIGHT -> HUD up, round live. Log the pairing; do not assert the foe id.
try {
  await p.tap('#stage-fight', { timeout: 90000 });
  await p.waitForFunction(() => { const g = window.__game; const h = document.getElementById('hud'); return g && g.roundState === 'fight' && h && getComputedStyle(h).display !== 'none' && !h.classList.contains('hidden'); }, null, { timeout: 300000, polling: 500 });
  const pair = await p.evaluate(() => ({ p1: window.__game.p1.char.id, p2: window.__game.p2.char.id }));
  console.log('fight: live pairing', JSON.stringify(pair));
  if (pair.p1 !== 'pantera') fails.push(`fight: p1 resolved to ${pair.p1}, not pantera`);
  await p.waitForTimeout(2000);
  await p.screenshot({ path: `${SHOTS}/04-fight.png` });
} catch (e) { fails.push('fight start: ' + e.message.split('\n')[0] + ' on ' + JSON.stringify(await scr())); }

// 4) Lose the match, then wait for the reincarnate screen.
const reincVisible = () => p.evaluate(() => { const e = document.getElementById('screen-reincarnate'); return e && getComputedStyle(e).display !== 'none' && !e.classList.contains('hidden'); });
try {
  for (let round = 0; round < 3; round++) {
    if (await reincVisible()) break;
    await p.waitForFunction(() => window.__game && window.__game.roundState === 'fight', null, { timeout: 300000, polling: 500 });
    await p.evaluate(() => { window.__game.p1.hp = 0; });
    try {
      await p.waitForFunction(() => { const g = window.__game; const e = document.getElementById('screen-reincarnate'); return g.roundState === 'over' || (e && getComputedStyle(e).display !== 'none' && !e.classList.contains('hidden')); }, null, { timeout: 300000, polling: 500 });
    } catch { fails.push(`death: round ${round + 1} did not settle after p1 KO`); break; }
    if (await reincVisible()) break;
    await p.waitForFunction(() => { const g = window.__game; const e = document.getElementById('screen-reincarnate'); return g.roundState === 'fight' || (e && getComputedStyle(e).display !== 'none' && !e.classList.contains('hidden')); }, null, { timeout: 300000, polling: 500 });
  }
  await p.waitForFunction(() => { const e = document.getElementById('screen-reincarnate'); return e && getComputedStyle(e).display !== 'none' && !e.classList.contains('hidden'); }, null, { timeout: 300000, polling: 500 });
  console.log('death: reincarnate screen up');
} catch (e) { fails.push('death -> reincarnate: ' + e.message.split('\n')[0] + ' on ' + JSON.stringify(await scr())); }

// 5) Reincarnate screen: RNF strip title, SAIL button, vessel cards.
try {
  const reinc = await p.evaluate(() => {
    const face = document.getElementById('reinc-face')?.textContent || '';
    const cards = [...document.querySelectorAll('#reinc-cards .reinc-card')];
    return {
      faceTitle: face.includes('PICK EACH PIECE (RNF)'),
      sail: cards.some((c) => c.textContent.includes('SAIL BETWEEN LIVES')),
      vessels: cards.filter((c) => !c.textContent.includes('SAIL BETWEEN LIVES')).length,
      deaths: document.getElementById('reinc-deaths')?.textContent || '',
      flavor: document.getElementById('reinc-flavor')?.textContent || '',
    };
  });
  console.log('reincarnate:', JSON.stringify(reinc));
  if (!reinc.faceTitle) fails.push('reincarnate: RNF face-strip title missing (expected PICK EACH PIECE (RNF))');
  if (!reinc.sail) fails.push('reincarnate: SAIL button missing');
  if (reinc.vessels < 1) fails.push('reincarnate: no vessel cards');
  if (!reinc.deaths.includes('DEATH 1')) fails.push('reincarnate: deaths line is not DEATH 1: ' + reinc.deaths);
  if (!reinc.flavor.includes('dreamed')) fails.push('reincarnate: dream line missing from flavor (no dream night recorded?)');
  await p.screenshot({ path: `${SHOTS}/05-reincarnate.png` });
} catch (e) { fails.push('reincarnate checks: ' + e.message.split('\n')[0]); }

// 6) SAIL -> Banabana hub overlay -> sail once -> close.
try {
  await p.evaluate(() => { [...document.querySelectorAll('#reinc-cards .reinc-card')].find((c) => c.textContent.includes('SAIL BETWEEN LIVES'))?.click(); });
  await p.waitForFunction(() => { const o = document.querySelector('div[style*="z-index:9999"]'); return o && o.querySelector('#rp-sail'); }, null, { timeout: 60000 });
  await p.tap('#rp-sail', { timeout: 90000 });
  await p.waitForFunction(() => { const o = document.querySelector('div[style*="z-index:9999"]'); return o && o.textContent.includes('Sailed to'); }, null, { timeout: 60000 });
  console.log('voyage: sailed, hub status confirms');
  await p.screenshot({ path: `${SHOTS}/06-banabana-hub.png` });
  await p.evaluate(() => { [...document.querySelectorAll('button')].find((x) => x.textContent.includes('RETURN TO THE REINCARNATION SCREEN'))?.click(); });
  await p.waitForFunction(() => !document.querySelector('div[style*="z-index:9999"]'), null, { timeout: 60000 });
  if (!(await reincVisible())) fails.push('voyage: reincarnate screen not showing after hub close');
} catch (e) { fails.push('voyage (SAIL -> hub -> close): ' + e.message.split('\n')[0]); }

// 7) Pick a vessel -> same rung, new vessel (stage kicker: DEATH 1).
try {
  await p.evaluate(() => { [...document.querySelectorAll('#reinc-cards .reinc-card')].find((c) => !c.textContent.includes('SAIL BETWEEN LIVES'))?.click(); });
  await p.waitForFunction(() => { const e = document.getElementById('screen-stage-intro'); return e && getComputedStyle(e).display !== 'none' && !e.classList.contains('hidden'); }, null, { timeout: 120000 });
  const kicker = await p.evaluate(() => document.getElementById('stage-kicker')?.textContent || '');
  console.log('reborn: stage kicker:', JSON.stringify(kicker));
  if (!kicker.includes('DEATH 1')) fails.push('reborn: stage kicker is not DEATH 1: ' + kicker);
  else console.log('reborn: same rung, new vessel OK');
  await p.screenshot({ path: `${SHOTS}/07-reborn-stage-intro.png` });
} catch (e) { fails.push('reborn vessel pick: ' + e.message.split('\n')[0] + ' on ' + JSON.stringify(await scr())); }

try { console.log('CLICKS:', await p.evaluate(() => JSON.stringify(window.__clicks))); } catch {}
await p.close();
await b.close();
if (fails.length) { console.error('FAIL\n' + fails.join('\n')); process.exit(1); }
console.log('PASS');
