/* ============================================================
   WESTERN HEART — Versus Setup (Tekken 7 GAME OPTION <VS GAME>)
   T7's versus rules live in GAME OPTION and govern every 2-player
   bout: FIGHT COUNT (rounds to take), ROUND TIME, GUARD DAMAGE.
   This screen puts them where the fight starts — every option is
   REAL: modes.js reads them in _beginVersus and they ride the
   fight opts into game.js (roundsToWin / roundTime / guardDamage).

   Flow: VERSUS card → VERSUS SETUP → CHOOSE FIGHTERS →
   character select (P1, P2) → stage select or random stage → fight.
   ============================================================ */
import { getRules, setRules, ROUND_COUNTS, ROUND_TIMES, fmtRoundTime } from './rules.js';
import { audio } from './audio.js';

const $ = (id) => document.getElementById(id);
const click = () => { try { audio.uiClick && audio.uiClick(); } catch { /* no audio yet */ } };

/* ---- row builders (T7 option-list grammar) ---- */
function segRow(label, sub, options, current, onPick) {
  // options: [[value, text], ...]
  const row = document.createElement('div');
  row.className = 'tk-row';
  const lab = document.createElement('div');
  lab.className = 'tk-row-label';
  lab.innerHTML = `<b>${label}</b>${sub ? `<small>${sub}</small>` : ''}`;
  const seg = document.createElement('div');
  seg.className = 'tk-seg';
  options.forEach(([val, text]) => {
    const b = document.createElement('button');
    b.type = 'button';
    b.textContent = text;
    if (val === current) b.classList.add('sel');
    b.addEventListener('click', () => {
      click();
      seg.querySelectorAll('button').forEach((x) => x.classList.remove('sel'));
      b.classList.add('sel');
      onPick(val);
    });
    seg.appendChild(b);
  });
  row.appendChild(lab);
  row.appendChild(seg);
  return row;
}

function buildRows() {
  const wrap = $('vs-rules');
  if (!wrap) return;
  wrap.innerHTML = '';
  const r = getRules();
  wrap.appendChild(segRow(
    'FIGHT COUNT', 'Rounds to take the bout · T7 FIGHT COUNT <VS GAME>',
    ROUND_COUNTS.map((n) => [n, `${n}`]),
    r.roundsVs, (v) => setRules({ roundsVs: v }),
  ));
  wrap.appendChild(segRow(
    'ROUND TIME', 'Seconds per round · 0 = INFINITY',
    ROUND_TIMES.map((t) => [t, fmtRoundTime(t)]),
    r.roundTime, (v) => setRules({ roundTime: v }),
  ));
  wrap.appendChild(segRow(
    'GUARD DAMAGE', 'Chip damage through block',
    [[true, 'ON'], [false, 'OFF']],
    r.guardDamage, (v) => setRules({ guardDamage: v }),
  ));
  wrap.appendChild(segRow(
    'STAGE', 'Arena for the bout',
    [['select', 'SELECT'], ['random', 'RANDOM']],
    r.stageMode, (v) => setRules({ stageMode: v }),
  ));
}

export function openVersusSetup() {
  click();
  buildRows();
  document.querySelectorAll('.screen').forEach((s) => s.classList.remove('active'));
  const sc = $('screen-vssetup');
  if (sc) sc.classList.add('active');
}

let booted = false;
export function initVersusSetup() {
  if (booted) return;
  booted = true;
  const back = $('vssetup-back');
  if (back) back.addEventListener('click', () => {
    click();
    // Back lands on the main menu with the VERSUS submenu still open.
    document.querySelectorAll('.screen').forEach((s) => s.classList.remove('active'));
    const m = $('screen-menu');
    if (m) m.classList.add('active');
  });
}
