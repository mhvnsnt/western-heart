/* ============================================================
   WESTERN HEART — Story Endings
   Per-character story endings / cinematics.

   Builds on worker 13's cutscene systems (intro-interactions.js,
   transform-cinematic.js phase timelines, episodes.js story beats).
   LAYERS BESIDE the existing Tekken-style intros and win taunts —
   those are owner-protected and are never touched or replaced here.
   Endings play AFTER a story/arcade run completes, from a
   "WATCH ENDING" button on the clear screen.

   Canon law: ending text uses only CANON.md vocabulary (the Trial,
   the Nine Souls, purification, Tong-Nou). No invented backstory.
   ============================================================ */

/* Shot: { dur, cam, text, fx }
   cam: 'wide' | 'close' | 'orbit' | 'low'
   fx: 'aura' | 'flash' | 'shockwave' | 'none' */
function S(dur, cam, text, fx = 'none') { return { dur, cam, text, fx }; }

const FALLBACK_ENDING = (name) => ({
  title: `${name} — WHOLE`,
  shots: [
    S(3.0, 'wide', 'The Trial is over. The shrine is quiet.', 'aura'),
    S(3.0, 'close', `${name} stands in the stillness after the last bell.`, 'none'),
    S(3.5, 'orbit', 'One soul, weighed and found whole. Purification holds — for now.', 'flash'),
  ],
});

/* Canon-grounded endings for the flagship cast. The Nine Souls'
   endings follow the rank-ladder order (Rin → Gyou). */
export const STORY_ENDINGS = {
  pantera: {
    title: 'PANTERA — THE KING EATS LAST',
    shots: [
      S(3.0, 'wide', 'The last challenger falls. The arena empties.', 'aura'),
      S(3.2, 'close', 'Pantera does not roar. Kings do not need to announce themselves.', 'none'),
      S(3.8, 'orbit', 'The Nine Souls turn their eyes to Tong-Nou. The king walks toward them — hungry, patient, whole.', 'shockwave'),
    ],
  },
  demonio: {
    title: 'DEMONIO — THE CODE REMEMBERED',
    shots: [
      S(3.0, 'close', 'He fought for the code he could not remember.', 'aura'),
      S(3.2, 'wide', 'No master set this exam. There is no dojo. There never was.', 'none'),
      S(3.8, 'orbit', 'Demonio bows — to no one, and to everyone. The code was his own all along.', 'flash'),
    ],
  },
  docfrank: {
    title: 'DOC FRANK — THE MACHINE KEEPS ITS PROMISE',
    shots: [
      S(3.0, 'wide', 'The workshop falls silent. The tools hang still.', 'none'),
      S(3.2, 'close', 'Bosco built a body that could survive the Trial. He never asked what would survive in it.', 'aura'),
      S(3.8, 'orbit', 'The machine keeps its promise: it endures. What endures in it is finally, entirely Frank.', 'shockwave'),
    ],
  },
  phantom: {
    title: 'PHANTOM — THE MASK COMES OFF',
    shots: [
      S(3.0, 'close', 'A mask is a promise you make to everyone watching.', 'none'),
      S(3.2, 'wide', 'The Trial weighed the phantom and found the person underneath.', 'aura'),
      S(3.8, 'orbit', 'The mask comes off. The face beneath is not hiding anymore.', 'flash'),
    ],
  },
  diablo: {
    title: 'DIABLO — WHAT THE MIRROR SHOWED',
    shots: [
      S(3.0, 'wide', 'The true demon surveys the wreckage of pretenders.', 'aura'),
      S(3.2, 'close', 'Demonio would not bow to him. That refusal was the only honest thing in the arena.', 'none'),
      S(3.8, 'orbit', 'Diablo laughs — and for once it is not cruel. The Trial purifies even mirrors.', 'shockwave'),
    ],
  },
  skull: {
    title: 'SKULL — TARGETS, NO MORE',
    shots: [
      S(3.0, 'close', 'Skull fought because the Trial provided targets.', 'none'),
      S(3.2, 'wide', 'With no targets left, something unfamiliar surfaces: a reason.', 'aura'),
      S(3.8, 'orbit', 'The skull grins at nothing. For the first time, the grin is his own.', 'flash'),
    ],
  },
  rin: {
    title: 'RIN 凛 — DIGNITY, PURIFIED',
    shots: [
      S(3.0, 'wide', 'The first soul of the nine stands alone at the shrine gate.', 'aura'),
      S(3.4, 'orbit', 'Rin — dignity. The Trial asked what dignity costs. The answer: everything, gladly paid.', 'flash'),
    ],
  },
  byou: {
    title: 'BYOU 病 — THE SICKNESS LIFTS',
    shots: [
      S(3.0, 'close', 'Byou carried the sickness so others would not have to.', 'none'),
      S(3.4, 'orbit', 'Purified, the sickness lifts like morning fog. What remains is compassion with teeth.', 'aura'),
    ],
  },
  tou: {
    title: 'TOU 闘 — THE FIGHT, FINISHED',
    shots: [
      S(3.0, 'wide', 'Tou lived for the struggle. The struggle is over.', 'aura'),
      S(3.4, 'orbit', 'A fighter without a fight discovers the hardest opponent: peace. Tou bows to it.', 'flash'),
    ],
  },
  sha: {
    title: 'SHA 沙 — SETTLED',
    shots: [
      S(3.0, 'close', 'Sha — sand. Countless grains, one desert.', 'none'),
      S(3.4, 'orbit', 'The grains settle. What the wind scattered, the Trial gathered.', 'aura'),
    ],
  },
  kai: {
    title: 'KAI 海 — STILL WATER',
    shots: [
      S(3.0, 'wide', 'Kai — the sea. It drowned every version of itself that was not true.', 'aura'),
      S(3.4, 'orbit', 'Still water reflects clearly. Kai finally sees who survived.', 'flash'),
    ],
  },
  retsu: {
    title: 'RETSU 烈 — THE FIRE, BANKED',
    shots: [
      S(3.0, 'close', 'Retsu burned. Everything it touched learned the shape of fire.', 'aura'),
      S(3.4, 'orbit', 'The fire is banked, not out. Warmth, aimed. That is the whole of the lesson.', 'shockwave'),
    ],
  },
  zen: {
    title: 'ZEN 禅 — THE ANSWER',
    shots: [
      S(3.0, 'wide', 'Zen asked the Trial one question and fought every answer.', 'none'),
      S(3.4, 'orbit', 'The answer was the asking. Zen smiles — the first honest koan.', 'flash'),
    ],
  },
  gyou: {
    title: 'GYOU 行 — THE LAST SOUL WALKS ON',
    shots: [
      S(3.0, 'wide', 'Gyou — the ninth soul. The last to be weighed.', 'aura'),
      S(3.4, 'orbit', 'Nine souls, one road. Gyou walks it last, and the road holds.', 'shockwave'),
    ],
  },
};

export function getEnding(charId, charName) {
  return STORY_ENDINGS[charId] || FALLBACK_ENDING((charName || charId || 'THE SOUL').toUpperCase());
}

/* ---------- Player: plays an ending in the live arena ----------
   Hooks: { game, ui, onDone }. Reuses the arena camera; each shot
   sets a camera framing, shows the text card, fires the fx beat. */
export class StoryEndingPlayer {
  constructor(hooks) {
    this.game = hooks.game;
    this.ui = hooks.ui;
    this.onDone = hooks.onDone || (() => {});
    this._timers = [];
    this._el = null;
  }

  play(charId, charName) {
    const ending = getEnding(charId, charName);
    const game = this.game;
    try { game.pause(true); } catch (e) { /* fail-safe */ }
    // Letterbox + title card.
    const el = document.createElement('div');
    el.id = 'story-ending';
    el.style.cssText = 'position:fixed;inset:0;z-index:80;display:flex;flex-direction:column;' +
      'justify-content:flex-end;align-items:center;pointer-events:none;color:#f2ecff;';
    el.innerHTML =
      `<div style="position:absolute;top:0;left:0;right:0;height:12vh;background:#000"></div>` +
      `<div style="position:absolute;bottom:0;left:0;right:0;height:12vh;background:#000"></div>` +
      `<div id="se-title" style="position:absolute;top:14vh;font:700 22px/1.3 system-ui;letter-spacing:.12em;text-shadow:0 2px 12px #000">${ending.title}</div>` +
      `<div id="se-text" style="margin-bottom:16vh;max-width:640px;text-align:center;font:16px/1.6 system-ui;text-shadow:0 2px 8px #000;padding:0 24px"></div>` +
      `<button id="se-skip" style="pointer-events:auto;position:absolute;bottom:13vh;right:24px;background:rgba(10,10,16,.8);color:#cfc6ff;border:1px solid #7a5cff;border-radius:8px;padding:8px 14px;font:12px system-ui">SKIP ▸</button>`;
    document.body.appendChild(el);
    this._el = el;
    el.querySelector('#se-skip').onclick = () => this.finish();
    const textEl = el.querySelector('#se-text');
    let t = 1200; // beat after the title lands
    for (const shot of ending.shots) {
      const at = t;
      this._timers.push(setTimeout(() => this._shot(shot, textEl), at));
      t += shot.dur * 1000;
    }
    this._timers.push(setTimeout(() => this.finish(), t + 800));
  }

  _shot(shot, textEl) {
    textEl.textContent = shot.text;
    textEl.style.opacity = 0;
    textEl.style.transition = 'opacity .6s';
    requestAnimationFrame(() => { textEl.style.opacity = 1; });
    // Camera framing per shot (fail-safe: the fight camera just stays).
    try {
      const cam = this.game.arena && this.game.arena.camera;
      const p1 = this.game.p1;
      if (cam && p1) {
        const base = p1.root.position;
        if (shot.cam === 'close') {
          cam.position.set(base.x + 1.6, 1.7, base.z + 2.2);
          cam.lookAt(base.x, 1.3, base.z);
        } else if (shot.cam === 'low') {
          cam.position.set(base.x - 2.4, 0.5, base.z + 3.2);
          cam.lookAt(base.x, 1.4, base.z);
        } else if (shot.cam === 'orbit') {
          const a = performance.now() / 1400;
          cam.position.set(base.x + Math.sin(a) * 4.2, 2.0, base.z + Math.cos(a) * 4.2);
          cam.lookAt(base.x, 1.2, base.z);
        } else { // wide
          cam.position.set(base.x * 0.4, 2.6, 8.5);
          cam.lookAt(0, 1.1, 0);
        }
      }
    } catch (e) { /* camera is decorative — never break the ending */ }
    // Fx beat on the winning fighter (best-effort; the aura system is optional).
    try {
      const f = this.game.p1;
      if (f && shot.fx === 'aura' && f.auraSurge) f.auraSurge(0xaa44ff, 0.8);
      if (f && shot.fx === 'flash' && f.flash) f.flash(0.8);
      if (f && shot.fx === 'shockwave' && f.shockwave) f.shockwave(0xaa44ff);
    } catch (e) { /* fx is decorative */ }
  }

  finish() {
    this._timers.forEach(clearTimeout);
    this._timers = [];
    if (this._el) { this._el.remove(); this._el = null; }
    try { this.game.pause(false); } catch (e) { /* fail-safe */ }
    this.onDone();
  }
}
