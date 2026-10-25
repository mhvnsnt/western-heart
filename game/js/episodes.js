/* ============================================================
   WESTERN HEART — Character Episodes (full story mode)
   Every fighter gets their own storyline, drawn from CANON.md:
   what they want, who they love/hate, what they're being purified
   of. Each episode: chapters of story beats + fights, climbing
   their own ladder to the shrine — where they all face themselves.

   Deep canon first (demonio, docfrank, mariposa, thor, nine souls);
   the generic frame builds a real arc for everyone else from their
   roster identity — no placeholders, every button works.
   ============================================================ */
import { scaledAi, whGetRecords, whSetRecord } from './modes.js';
import { playStoryBeats, setModeTag, showLoading } from './menus.js';
import { buildShadowSelf } from './heartmind.js';

/* Chapter fight spec: { foe } may be a roster id (scaled by diff) or a
   full char entry (echo/shadow). */
function foeEntry(getChar, foe, diff) {
  if (typeof foe === 'string') {
    const c = getChar(foe) || getChar('skull');
    return { ...c, ai: scaledAi(c, diff) };
  }
  return foe;
}

export const EPISODES = {
  demonio: {
    title: 'DEMONIO — THE CODE HE CANNOT REMEMBER',
    chapters: [
      { name: 'CHAPTER 1 — THE GRADING EXAM', stage: 'shrine',
        beats: [
          { name: 'DEMONIO', charId: 'demonio', text:
            'He fights for the code he cannot remember. Wholeness might mean remembering. The trial is a grading exam — some master set it, some dojo recognizes his discipline. He has never considered that there is no master. Only a dying head.' },
          { name: 'DEMONIO', charId: 'demonio', text:
            'First lesson: the only soul he respects without reservation. PANTERA. If the trial is an exam, let the first question be the hardest one he admires.' },
        ],
        fights: [{ foe: 'pantera', diff: 0.55, label: 'PANTERA — the respected' }] },
      { name: 'CHAPTER 2 — THE PUNISHER', stage: 'tong-nou',
        beats: [
          { name: 'DEMONIO', charId: 'demonio', text:
            'SKULL fights because the trial provides targets. Demonio fights because the code demands it. Targets versus discipline — the trial loves this kind of math.' },
        ],
        fights: [{ foe: 'skull', diff: 0.65, label: 'SKULL — targets' }] },
      { name: 'CHAPTER 3 — MIRROR AND ENEMY', stage: 'plains-of-chi-u',
        beats: [
          { name: 'DEMONIO', charId: 'demonio', text:
            'DIABLO. His mirror and his enemy — the true demon versus the pretender. This is the rivalry the trial was built for. He bows to every opponent. He has never once bowed to Diablo. Everyone has noticed.' },
          { name: 'DIABLO', charId: 'diablo', text:
            'The little saint comes to lecture me about demons? I AM what you pretend not to be, boy.' },
        ],
        fights: [{ foe: 'diablo', diff: 0.8, label: 'DIABLO — the mirror' }] },
      { name: 'FINAL — THE SHRINE', stage: 'octagonal-shrine', boss: true,
        beats: [
          { name: 'DEMONIO', charId: 'demonio', text:
            'They all reach the same shrine. They all face themselves. At the top of his ladder waits everything he apologizes for — wearing his face, refusing to bow.' },
        ],
        fights: [] },
    ],
    ending: [
      { name: 'DEMONIO', charId: 'demonio', text:
        'The code was never written down. It was never taught. It is simply what remains when the apology burns away: cold courtesy, precision, no cruelty. RIN — the baseline. The still point.' },
      { name: 'CHARACTER EPISODES', charId: 'demonio', text:
        'Demonio remembers now. There was no master. There was only the work. That was always enough.' },
    ],
  },
  docfrank: {
    title: 'DOC FRANK — THE PUBLISHED SOUL',
    chapters: [
      { name: 'CHAPTER 1 — PEER REVIEW', stage: 'helix-palace',
        beats: [
          { name: 'DOC FRANK', charId: 'docfrank', text:
            'Born Franklin Bauzzkoh. Shortened it to Frank Bozko — nobody funds a Bauzzkoh. He believes the trial is peer review: Tong-Nou called him to evaluate the soul as an engineering problem, and he will publish. The idea that he is here to be purified offends him professionally.' },
          { name: 'DOC FRANK', charId: 'docfrank', text:
            'First test subject: my own build. SAM-UR-A1 keeps asking what it fights for. Let us see if it has an answer that is not "data."' },
        ],
        fights: [{ foe: 'samura1', diff: 0.55, label: 'SAM-UR-A1 — the question' }] },
      { name: 'CHAPTER 2 — THE DAUGHTER', stage: 'helix-palace',
        beats: [
          { name: 'DOC FRANK', charId: 'docfrank', text:
            'CYBORG X: his daughter, his masterpiece, his proof. She has detachable parts and his stubbornness. He pretends the pride is scientific. It is not. Fathers should not have to fight their daughters. Scientists, however, take notes.' },
        ],
        fights: [{ foe: 'cyborgx', diff: 0.65, label: 'CYBORG X — the masterpiece' }] },
      { name: 'CHAPTER 3 — THE UNFIXABLE', stage: 'phantom-marketplace',
        beats: [
          { name: 'DOC FRANK', charId: 'docfrank', text:
            'DXMMII: the patchwork wants no fixing. Doc Frank wants to fix it anyway. It is the great unresolved tension of the Western Heart\'s machine shop. Today the tension resolves the old way.' },
        ],
        fights: [{ foe: 'dxmmii-patchwork', diff: 0.75, label: 'DXMMII — the unresolved' }] },
      { name: 'FINAL — THE SHRINE', stage: 'octagonal-shrine', boss: true,
        beats: [
          { name: 'DOC FRANK', charId: 'docfrank', text:
            'Three built souls climbed. Two machines who wonder if they have souls, and the man who built them because he was not sure he did. At the shrine: the one soul he never built. His own.' },
        ],
        fights: [] },
    ],
    ending: [
      { name: 'DOC FRANK', charId: 'docfrank', text:
        'The difference between making a thing and being the thing. I am the thing. Paper accepted. The clipboard is full — and for the first time, it can stay closed.' },
      { name: 'CHARACTER EPISODES', charId: 'docfrank', text:
        'Android 9. Or just 9. The soul that chose its own vessel, bolt by bolt — and finally stopped trying to improve it.' },
    ],
  },
  'mariposa-monarch': {
    title: 'MARIPOSA — THE KEEPER\'S LEAK',
    chapters: [
      { name: 'CHAPTER 1 — CHECKING THE LOCKS', stage: 'tree-of-life',
        beats: [
          { name: 'MARIPOSA', charId: 'mariposa-monarch', text:
            'Every other fighter arrived in the Western Heart. Mariposa hatched here — in the branches of the Tree of Life, while the trial was not looking. She did not hear a summons. She heard a leak. Something sealed followed her in — or was already here, wearing a new shape.' },
          { name: 'MARIPOSA', charId: 'mariposa-monarch', text:
            'The intruder tore his way in. I watch him the way a locksmith watches a crowbar. He knows. He performs for me. Let him perform.' },
        ],
        fights: [{ foe: 'diablo', diff: 0.6, label: 'DIABLO — the crowbar' }] },
      { name: 'CHAPTER 2 — THE GHOST BLADE', stage: 'palace-of-dreaming',
        beats: [
          { name: 'MARIPOSA', charId: 'mariposa-monarch', text:
            'PHANTOM fights because he was already fighting when the trial started. He may not stop when it ends. A keeper recognizes another kind of seal — his is just worn on the outside.' },
        ],
        fights: [{ foe: 'phantom', diff: 0.7, label: 'PHANTOM — the sealed blade' }] },
      { name: 'CHAPTER 3 — WHAT SLIPPED THROUGH', stage: 'phantom-marketplace',
        beats: [
          { name: 'MARIPOSA', charId: 'mariposa-monarch', text:
            'The seal was always going to follow me. You do not guard a door that long without the door becoming part of you. So: what slipped through — was it ever out there at all?' },
        ],
        fights: [{ foe: 'dio', diff: 0.78, label: 'DIO — the venue' }] },
      { name: 'FINAL — THE SHRINE', stage: 'octagonal-shrine', boss: true,
        beats: [
          { name: 'MARIPOSA', charId: 'mariposa-monarch', text:
            'The trial keeps offering me purification. I keep declining — I have a post to hold. But at the shrine there is one last lock to check. It has my face. It has my wings. It is not guarding anything.' },
        ],
        fights: [] },
    ],
    ending: [
      { name: 'MARIPOSA', charId: 'mariposa-monarch', text:
        'The seal holds as long as I do. But now I know: I am a person first and a lock second. The joints crack backward one last time — and then bend the right way.' },
      { name: 'CHARACTER EPISODES', charId: 'mariposa-monarch', text:
        'The keeper checked every lock, including the one inside. The leak was never out there. It was the part of her that wanted to be more than a door. She let it out. On purpose. It pollinates now.' },
    ],
  },
  thor: {
    title: 'THOR — THE WEATHER INSIDE',
    chapters: [
      { name: 'CHAPTER 1 — LIKE IT BELONGS TO HIM', stage: 'plains-of-chi-u',
        beats: [
          { name: 'THOR', charId: 'thor', text:
            'He does not know he is being purified. That is the point. The thunder god walks into his own story the way he walks into weather — like it belongs to him. Today the weather is TOU: battle itself. Good. Thunder likes a straight fight.' },
        ],
        fights: [{ foe: 'tou', diff: 0.6, label: 'TOU — battle itself' }] },
      { name: 'CHAPTER 2 — THE QUIET AFTER', stage: 'palace-of-dreaming',
        beats: [
          { name: 'THOR', charId: 'thor', text:
            'ZEN barely moves. Does not need to. Stillness — the one thing thunder has never understood. The god of noise versus the soul of quiet. This will be LOUD. Or... very, very quiet.' },
        ],
        fights: [{ foe: 'zen', diff: 0.7, label: 'ZEN — stillness' }] },
      { name: 'FINAL — THE SHRINE', stage: 'octagonal-shrine', boss: true,
        beats: [
          { name: 'THOR', charId: 'thor', text:
            'At the shrine waits the storm with no joy in it. All the thunder. None of the laughter. This is what a god looks like with no one left to protect.' },
        ],
        fights: [] },
    ],
    ending: [
      { name: 'THOR', charId: 'thor', text:
        'I am still thunder! But now I know the silence between the strikes is mine too. A god who only knows noise is just weather — and I am MUCH more than weather.' },
      { name: 'CHARACTER EPISODES', charId: 'thor', text:
        'He still does not know he was purified. That is still the point. Some doors only open for those who are not looking for them.' },
    ],
  },
};

const NINE_EP = {
  rin:   ['The baseline. Every other soul deviates from RIN — this episode is the measure of all the others.', 0.55],
  byou:  ['Sickness moves wrong. This is the story of the soul that learned to fight crooked.', 0.55],
  tou:   ['Battle itself. No philosophy, no apology — the purest episode: a soul that only wants the next fight.', 0.55],
  sha:   ['Sand erodes mountains. The slowest episode, and the most certain.', 0.55],
  kai:   ['The sea does not stop. Neither does KAI. An episode about outlasting.', 0.55],
  jin_soul: ['The blade — precise, ritual, terrifying. An episode about the cut.', 0.55],
  retsu: ['Pure violence. The episode does not apologize, and neither does RETSU.', 0.55],
  zen:   ['Stillness. Barely move. Do not need to. The quietest episode.', 0.55],
  gyou:  ['Motion itself. Cannot stop moving. The episode never sits still.', 0.55],
};
for (const [id, [line, diff]] of Object.entries(NINE_EP)) {
  const up = id === 'jin_soul' ? 'JIN' : id.toUpperCase();
  EPISODES[id] = {
    title: `${up} — SOUL EPISODE`,
    chapters: [
      { name: 'CHAPTER 1 — THE NATURE', stage: 'shrine',
        beats: [{ name: up, charId: id, text: line + ' Every soul climbs its own ladder to the same shrine.' }],
        fights: [{ foe: 'skull', diff, label: 'SKULL — the first rung' }] },
      { name: 'CHAPTER 2 — THE TEST', stage: 'tong-nou',
        beats: [{ name: up, charId: id, text: 'The trial provides targets. The soul provides the reason. Only one of those matters.' }],
        fights: [{ foe: 'tou', diff: diff + 0.1, label: 'TOU — the test' }] },
      { name: 'FINAL — THE SHRINE', stage: 'octagonal-shrine', boss: true,
        beats: [{ name: up, charId: id, text: 'They all reach the same shrine. They all face themselves.' }],
        fights: [] },
    ],
    ending: [
      { name: up, charId: id, text: 'The ladder is climbed. The soul is what it is — named, faced, and kept.' },
      { name: 'CHARACTER EPISODES', charId: id, text: `${up}'s episode is complete. The nine are remembered, not borrowed.` },
    ],
  };
}

/* Generic frame: real arc from roster identity. No placeholders. */
export function genericEpisode(char) {
  const name = char.name || 'THE SOUL';
  const want = char.title || 'a wandering soul';
  const style = char.style || 'their own way';
  const beatsFor = (n) => [
    { name, charId: char.id, text:
      n === 1 ? `${name} — ${want}. Every soul climbs its own ladder to the same shrine, fighting ${style}. This is that climb.` :
      n === 2 ? 'The middle of the ladder is where the trial gets honest. No crowd. No excuses. Just the next fight.' :
      'One rung left. The shrine is close enough to hear. And at the top — everyone says it — you face yourself.' },
  ];
  return {
    title: `${name} — ${want.toUpperCase()}`,
    chapters: [
      { name: 'CHAPTER 1 — THE CLIMB', stage: 'shrine', beats: beatsFor(1),
        fights: [{ foe: 'skull', diff: 0.55, label: 'SKULL — the first rung' }] },
      { name: 'CHAPTER 2 — THE HONEST MIDDLE', stage: 'tong-nou', beats: beatsFor(2),
        fights: [{ foe: 'tou', diff: 0.65, label: 'TOU — the honest fight' }] },
      { name: 'CHAPTER 3 — THE LAST RUNG', stage: 'plains-of-chi-u', beats: beatsFor(2),
        fights: [{ foe: 'diablo', diff: 0.75, label: 'DIABLO — the last rung' }] },
      { name: 'FINAL — THE SHRINE', stage: 'octagonal-shrine', boss: true, beats: beatsFor(3), fights: [] },
    ],
    ending: [
      { name, charId: char.id, text:
        'The ladder is climbed. Whatever I was fighting for — I am still fighting for it. That is the whole story, and it is enough.' },
      { name: 'CHARACTER EPISODES', charId: char.id, text:
        `${name}'s episode is complete. Every soul, their story.` },
    ],
  };
}

export function getEpisode(char) {
  return EPISODES[char.id] || genericEpisode(char);
}

/* ============================================================
   Controller
   ============================================================ */
export class EpisodesController {
  constructor(deps) {
    this.game = deps.game;
    this.ui = deps.ui;
    this.show = deps.show;
    this.startFight = deps.startFight;
    this.roster = deps.roster;
    this.getChar = deps.getChar;
    this.audio = deps.audio;
    this.run = null; // { fighterId, chapter, fight }
    this._lastCard = null;
  }
  clear() { this.run = null; this._lastCard = null; setModeTag(''); }

  beginSelect() {
    this.clear();
    const m = window.__modes;
    if (m) { m.clearState(); m.mode = 'episodes'; }
    this.show('select');
    const hint = document.getElementById('select-hint');
    if (hint) hint.textContent =
      'CHARACTER EPISODES — choose your soul.';
    const btn = document.getElementById('confirm-fighter');
    if (btn) btn.disabled = true;
  }
  trackCard(id) { this._lastCard = id; }
  onConfirm() {
    const m = window.__modes;
    if (!m || m.mode !== 'episodes' || !this._lastCard) return false;
    const id = this._lastCard;
    this._lastCard = null;
    this.start(id);
    return true;
  }

  start(fighterId) {
    const char = this.getChar(fighterId);
    if (!char) return;
    this._ep = getEpisode(char);
    this.run = { fighterId, chapter: 0, fight: 0 };
    setModeTag('CHARACTER EPISODES');
    showLoading('OPENING THE EPISODE…');
    playStoryBeats(
      [{ name: this._ep.title, charId: fighterId,
         text: 'Every fighter gets their own storyline. This one belongs to ' + char.name + '.' }],
      () => this._runChapter(), this._ep.title);
  }

  _runChapter() {
    const ch = this._ep.chapters[this.run.chapter];
    if (!ch) { this._finish(); return; }
    this.run.fight = 0;
    playStoryBeats(ch.beats, () => this._runFight(), ch.name);
  }

  _runFight() {
    const ch = this._ep.chapters[this.run.chapter];
    const spec = ch.fights[this.run.fight];
    const char = this.getChar(this.run.fighterId);
    let foe;
    if (spec) {
      foe = foeEntry(this.getChar, spec.foe, spec.diff);
    } else if (ch.boss) {
      foe = buildShadowSelf(char); // they all face themselves
    } else { this._nextChapter(); return; }
    const label = spec ? `${ch.name} · ${spec.label}` : `${ch.name} · YOURSELF`;
    this.ui.hudNote && this.ui.hudNote(label);
    setModeTag('EPISODES · ' + ch.name);
    this.game.onMatchEnd = (won) => this._fightEnd(won);
    showLoading('THE STORY CONTINUES…');
    this.startFight(this.run.fighterId, null, {
      mode: 'episodes', roundsToWin: ch.boss ? 2 : 1,
      stage: ch.stage, enemyChar: foe,
    });
  }

  _fightEnd(won) {
    if (!won) {
      const ch = this._ep.chapters[this.run.chapter];
      playStoryBeats([
        { name: ch.name, charId: this.run.fighterId,
          text: 'The episode pauses here — but stories are patient. Run it back.' },
      ], () => {
        this.show('menu');
        if (window.__modes) window.__modes.clearState();
        this.clear();
      }, 'TO BE CONTINUED…');
      return;
    }
    const ch = this._ep.chapters[this.run.chapter];
    this.run.fight++;
    if (this.run.fight < ch.fights.length) {
      setTimeout(() => this._runFight(), 1100);
    } else {
      this._nextChapter();
    }
  }

  _nextChapter() {
    this.run.chapter++;
    this.run.fight = 0;
    setTimeout(() => this._runChapter(), 900);
  }

  _finish() {
    const char = this.getChar(this.run.fighterId);
    const key = 'episode_' + this.run.fighterId;
    whSetRecord(key, (whGetRecords()[key] || 0) + 1);
    // Extra: feed the episodes record panel.
    const extra = document.getElementById('wh-rec-extra');
    if (extra) {
      extra.innerHTML = `<div class="wh-rec-row"><span>EPISODES COMPLETED</span><span class="rv">${Object.keys(whGetRecords()).filter((k) => k.startsWith('episode_')).length}</span></div>`;
    }
    playStoryBeats(this._ep.ending, () => {
      this.game.onMatchEnd = null;
      if (window.__modes) window.__modes.clearState();
      const ui2 = window.__ui;
      if (ui2 && ui2.matchOver) ui2.matchOver(true);
      const t = document.getElementById('result-title');
      if (t) t.textContent = 'EPISODE COMPLETE';
      const s = document.getElementById('result-sub');
      if (s) s.textContent = `${char.name}'s story is told. Every soul, their story.`;
      this.clear();
    }, 'EPISODE COMPLETE');
  }

  rematch() { if (this.run) this._runFight(); }
}
