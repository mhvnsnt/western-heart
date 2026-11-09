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
function segRow(label, sub, options, current, onPick, subFor) {
  // options: [[value, text], ...]
  // subFor (optional): value => sub text — when the picked value changes
  // what the row means, the sub-label follows the pick (Bug 6: the STAGE
  // row's sub used to say only "Arena for the bout", so tapping SELECT —
  // already the default — visibly did nothing and never said the arena
  // list comes on the next screen).
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
      if (subFor) {
        const small = lab.querySelector('small');
        if (small) small.textContent = subFor(val);
      }
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
  // Piece 1 re-test Bug 6 (Stage SELECT does nothing visible): SELECT is
  // the default stageMode, so tapping it re-applied the same value and the
  // only feedback was the already-lit highlight — and nothing said the
  // arena list comes later, on CHOOSE YOUR ARENA after picking fighters
  // (modes.js: the arena screen shows unless stageMode is 'random', when
  // a random arena is picked and the screen is skipped). The sub-label
  // now says what each choice does, so the tap visibly answers.
  const stageSub = (v) => v === 'random'
    ? 'A random arena is picked for you'
    : 'Pick your arena on the next screen, after choosing fighters';
  wrap.appendChild(segRow(
    'STAGE', stageSub(r.stageMode),
    [['select', 'SELECT'], ['random', 'RANDOM']],
    r.stageMode, (v) => setRules({ stageMode: v }), stageSub,
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
