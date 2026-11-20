/* ============================================================
   WESTERN HEART — Punishment Training
   Owner-approved 2026-10-22 (learning tools: YES, ALL).
   Teardown source: Tekken's punishment training — the dummy performs a
   move on loop; the UI shows its block frames; the player must punish
   with a launcher/appropriate punisher; the mode grades success and
   cycles the repertoire. Faithful port:
     • drill = { foeMove, minusFrames, punishers:[notations] } — data;
     • the dummy loops foeMove; on block the player has minusFrames to
       land any listed punisher (frame math in 60fps frames);
     • grades: PERFECT (fastest punisher), GOOD (any punisher in window),
       MISS (window expired), WRONG (punished with the wrong move class);
     • drill sets built per fighter from moveset frame data where
       available, curated fallback otherwise.
   WH canon mapping (PROPOSED — needs owner approval):
     "SKULL'S LESSONS" — taught by Skull, the Punisher Soul ("he fights
     because the trial provides targets"). The Trial provides the
     targets; Skull provides the lesson: every unsafe move gets buried.
     Alternative: "Punisher's Rite" — flagged for owner call.
   ============================================================ */

export const PUNISH_GRADES = ['PERFECT', 'GOOD', 'MISS', 'WRONG'];

/* Drill: { id, foe, foeMove, foeMoveName, minusFrames, punishers:[{notation, name, startupF}], hint } */
export const PUNISH_DRILLS = {
  /* ——— vs PANTERA (grappler: punish the whiffed strings) ——— */
  pantera: [
    { id: 'pun-pan-1', foe: 'pantera', foeMove: '2,1', foeMoveName: 'Pantera 2,1 string', minusFrames: 14,
      punishers: [{ notation: '1', name: 'Jab', startupF: 7 }, { notation: '2', name: 'Right punch', startupF: 8 }],
      hint: 'He finished the string. Bury the recovery — jab now.' },
    { id: 'pun-pan-2', foe: 'pantera', foeMove: '1+2', foeMoveName: 'Pantera power strike', minusFrames: 18,
      punishers: [{ notation: '2,1', name: 'String', startupF: 10 }],
      hint: 'Big swing, big debt. Collect with your string.' },
  ],
  /* ——— vs DEMONIO (discipline: punish the second jab) ——— */
  demonio: [
    { id: 'pun-dem-1', foe: 'demonio', foeMove: '1', foeMoveName: 'Demonio jab', minusFrames: 12,
      punishers: [{ notation: '1', name: 'Jab', startupF: 7 }],
      hint: 'Rin is dignified, not safe. Jab his recovery.' },
  ],
  /* ——— vs SKULL (the teacher's own drills — hardest) ——— */
  skull: [
    { id: 'pun-sku-1', foe: 'skull', foeMove: '2,1', foeMoveName: 'Skull 2,1', minusFrames: 13,
      punishers: [{ notation: '1', name: 'Jab', startupF: 7 }, { notation: '2,1', name: 'String', startupF: 10 }],
      hint: 'Skull grades on a curve. Be faster than the target.' },
  ],
  /* ——— vs DOROWANI (goofy drills) ——— */
  dorowani: [
    { id: 'pun-dor-1', foe: 'dorowani', foeMove: '2,1', foeMoveName: 'Dorowani flail', minusFrames: 16,
      punishers: [{ notation: '1', name: 'Jab', startupF: 7 }],
      hint: 'He flailed. (The stone is trying not to laugh.) Punish.' },
  ],
};

export function drillsFor(fighterId) { return PUNISH_DRILLS[fighterId] || []; }

/* The drill runner — pure logic. Feed blocked foe moves + player moves. */
export class PunishRunner {
  constructor(drill) {
    this.drill = drill;
    this.state = 'waiting'; // waiting -> window-open -> graded
    this.windowLeft = 0;    // frames left to punish
    this.attempts = 0;
    this.grades = [];
  }
  /* The foe's drill move was blocked: open the punish window. */
  foeBlocked() {
    this.state = 'window-open';
    this.windowLeft = this.drill.minusFrames;
    this.attempts++;
  }
  tick(frames = 1) {
    if (this.state !== 'window-open') return null;
    this.windowLeft -= frames;
    if (this.windowLeft <= 0) {
      this.state = 'graded';
      this.grades.push('MISS');
      return { grade: 'MISS', reason: 'window-expired' };
    }
    return null;
  }
  /* Player landed a move during the window. startupF = its startup frames. */
  playerPunish(notation, startupF) {
    if (this.state !== 'window-open') return { grade: null, reason: 'no-window' };
    const match = this.drill.punishers.find(p => p.notation === notation);
    if (!match) {
      this.state = 'graded';
      this.grades.push('WRONG');
      return { grade: 'WRONG', reason: 'not-a-punisher', expected: this.drill.punishers.map(p => p.notation) };
    }
    this.state = 'graded';
    const fastest = Math.min(...this.drill.punishers.map(p => p.startupF));
    const grade = startupF <= fastest ? 'PERFECT' : 'GOOD';
    this.grades.push(grade);
    return { grade, reason: 'punished', framesUsed: this.drill.minusFrames - this.windowLeft };
  }
  reset() { this.state = 'waiting'; this.windowLeft = 0; }
  score() {
    const g = this.grades;
    return { attempts: this.attempts, perfect: g.filter(x => x === 'PERFECT').length, good: g.filter(x => x === 'GOOD').length, miss: g.filter(x => x === 'MISS').length, wrong: g.filter(x => x === 'WRONG').length };
  }
}
