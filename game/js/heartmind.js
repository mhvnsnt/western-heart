/* ============================================================
   WESTERN HEART — "The Heart and Mind Inside"
   (owner-locked name 2026-10-19 — NOT "Western Heart Eastern Mind mode")

   Devil Within-style action mode, proprietized: the skeleton is
   Tekken 5's Devil Within (5 stages → enemy waves → stage boss,
   transform meter), the flesh is Western Heart — our arenas, our
   enemies, our universe. Pick ANY fighter; each gets their OWN
   storyline: a personal journey down into their own heart and mind.
   The trial turned inward — inner darkness and purification, per
   CANON.md ("Being purified of" per fighter).

   TEARDOWN-INTEGRATION SEAM (T5 teardown in progress, NO-DEFERRAL):
   when the teardown stream delivers Devil Within's exact mechanics
   (enemy AI patterns, wave composition tables, platforming/door
   systems), they land in HM_TEARDOWN and the wave/boss builders
   below consume them 1:1. The story system and proprietary layer
   do not change.

   Combat model (phase 1): sequential inner battles — each wave is a
   single-round fight vs an "echo" with HP carry-over + soul-ember
   restores between waves. Soul Surge is the transform-meter analog
   (channel the nine against the dark inside). Phase 2 (post-teardown):
   simultaneous multi-enemy density via the seam below.
   ============================================================ */
import { scaledAi, whGetRecords, whSetRecord } from './modes.js';
import { playStoryBeats, setModeTag, showLoading, hideLoading } from './menus.js';
import { roadInto, createPartyState, switchPartyFighter, recordPartyStageClear, HM_RAGDOLL_CONTEXTS } from './heartmind-campaign.js';

/* Filled by the teardown lane. Consumed 1:1 when present. */
export const HM_TEARDOWN = {
  ready: false,
  enemyAi: null,    // per-enemy-type AI patterns from T5
  waveTables: null, // stage -> wave composition from T5
  doorSystems: null,// platforming/door progression from T5
  note: 'T5 teardown in progress (NO-DEFERRAL). Phase-1 proprietary tables below.',
};

/* ---------------- The five inner stages ----------------
   Proprietary Eastern Mind mapping: each inner room is a canon land
   that mirrors it. getStage() falls back safely if an id is missing. */
export const HEARTMIND_STAGES = [
  { n: 1, key: 'threshold', name: 'THE THRESHOLD', stage: 'tong-nou',
    sub: 'The door you never opened.',
    waves: 3, diff: 0.45, restore: 0.30 },
  { n: 2, key: 'masks', name: 'THE GALLERY OF MASKS', stage: 'phantom-marketplace',
    sub: 'Every face you have ever worn.',
    waves: 3, diff: 0.55, restore: 0.30 },
  { n: 3, key: 'drowning', name: 'THE DROWNING ROOM', stage: 'palace-of-dreaming',
    sub: 'What you buried.',
    waves: 3, diff: 0.65, restore: 0.32 },
  { n: 4, key: 'furnace', name: 'THE FURNACE', stage: 'plains-of-chi-u',
    sub: 'What burns you.',
    waves: 3, diff: 0.75, restore: 0.32 },
  { n: 5, key: 'stillpoint', name: 'THE STILL POINT', stage: 'octagonal-shrine',
    sub: 'Yourself, unmasked.',
    waves: 0, diff: 0.90, restore: 0.35 }, // boss only: the shadow self
];

/* Phase-1 proprietary wave table: echoes per stage. When HM_TEARDOWN
   lands, waveTables replaces this 1:1. */
const ECHO_POOL = ['skull', 'tou', 'retsu', 'negativo', 'dio', 'slice', 'burger', 'scimitar'];

/* An "echo": a roster fighter as an inner demon. Dark tint, hollow
   name. Real fighter, real moveset — the dark inside wears your world. */
export function makeEcho(char, diff) {
  return {
    ...char,
    id: char.id + '-echo',
    name: 'ECHO OF ' + char.name,
    title: 'An inner demon',
    portrait: char.id,
    tintStrength: 0.9,
    colors: { suit: 0x0a0a12, trim: 0x6a1fb0 },
    ai: scaledAi(char, diff),
  };
}

/* The shadow self: your model, your moveset, darkened, buffed,
   merciless. "It is you, unmasked." */
export function buildShadowSelf(playerChar) {
  const stats = { ...(playerChar.stats || {}) };
  stats.power = (stats.power || 1.1) * 1.28;
  stats.defense = (stats.defense || 1.05) * 1.15;
  stats.speed = Math.min(3.5, (stats.speed || 2.8) * 1.10);
  return {
    ...playerChar,
    id: playerChar.id + '-shadow',
    name: 'SHADOW OF ' + playerChar.name,
    title: 'Yourself, Unmasked',
    portrait: playerChar.id,
    tintStrength: 0.9,
    colors: { suit: 0x05050c, trim: 0xb28dff },
    stats,
    ai: { aggression: 0.95, grabBias: 0.30, reaction: 0.90 },
  };
}

/* ============================================================
   Per-character story system.
   Every fighter: entry cutscene, mid-descent beats tied to their
   CANON.md "Being purified of", a personal shadow confrontation,
   and a resolution. Deep canon first (demonio, docfrank, mariposa,
   thor, the nine souls); the generic frame below lets the rest plug in.
   ============================================================ */
const NINE = {
  rin:   { kanji: '凛', nature: 'dignified, cold, self-possessed', pure: 'the stillness you perform' },
  byou:  { kanji: '病', nature: 'sickness that moves wrong', pure: 'the wrongness you hide' },
  tou:   { kanji: '闘', nature: 'battle itself', pure: 'the fight you cannot stop picking' },
  sha:   { kanji: '沙', nature: 'sand that erodes mountains', pure: 'the slow wearing-down you deny' },
  kai:   { kanji: '海', nature: 'the sea that does not stop', pure: 'the undertow beneath your calm' },
  jin_soul: { kanji: '刃', nature: 'the blade — precise, ritual, terrifying', pure: 'the cut you enjoy making' },
  retsu: { kanji: '烈', nature: 'pure violence', pure: 'the violence you call honesty' },
  zen:   { kanji: '禅', nature: 'stillness', pure: 'the stillness you use as armor' },
  gyou:  { kanji: '行', nature: 'motion itself', pure: 'the running you call journey' },
};

function nineStory(id) {
  const s = NINE[id];
  const up = id === 'jin_soul' ? 'JIN' : id.toUpperCase();
  return {
    title: `${up} ${s.kanji} — DESCENT OF THE ${up} SOUL`,
    entry: [
      { name: 'THE HEART AND MIND INSIDE', charId: id, text:
        `The trial turned inward. Not across the five lands — down. Into the place where ${s.nature} was born.` },
      { name: up, charId: id, text:
        `Every soul carries a dark it will not name. Yours is ${s.pure}. Walk down and meet it.` },
    ],
    beats: {
      masks: [{ name: up, charId: id, text:
        `The masks come off one by one. Under the last one: ${s.nature}. It was never a mask. It was a mirror.` }],
      drowning: [{ name: up, charId: id, text:
        `Here is where you buried it — ${s.pure}. It has been breathing down here the whole time.` }],
      furnace: [{ name: up, charId: id, text:
        `The furnace does not ask what you are. It asks what you will burn to stay yourself.` }],
    },
    bossName: `SHADOW OF ${up} ${s.kanji}`,
    bossLines: [
      { name: `SHADOW OF ${up}`, charId: id, text:
        `I am ${s.nature}. You polished me and called it discipline. Now fight the thing you made.` },
    ],
    resolution: [
      { name: up, charId: id, text:
        `It is quiet at the still point. ${s.pure} — named, faced, and put down like a blade back in its sheath.` },
      { name: 'THE HEART AND MIND INSIDE', charId: id, text:
        `Purification is not becoming someone else. It is meeting yourself and staying.` },
    ],
  };
}

export const HEARTMIND_STORIES = {
  demonio: {
    title: 'DEMONIO — DESCENT OF THE APOLOGY',
    entry: [
      { name: 'THE HEART AND MIND INSIDE', charId: 'demonio', text:
        'Demonio believed the trial was a grading exam — some master, some dojo, some final test. There is no master. There never was. Only a dying head, and a bow that never stops.' },
      { name: 'DEMONIO', charId: 'demonio', text:
        'Then I will descend as I fight: precisely. If there is a sin I am atoning for, I will find it, name it, and put it down.' },
      { name: 'THE HEART AND MIND INSIDE', charId: 'demonio', text:
        'Down. Not across the lands — down. Into the place the bows come from.' },
    ],
    beats: {
      masks: [{ name: 'DEMONIO', charId: 'demonio', text:
        'Every mask bows. Every single one. A thousand apologies with my face on them — and I cannot remember what any of them are for.' }],
      drowning: [{ name: 'DEMONIO', charId: 'demonio', text:
        'Here it is. The guilt. It has no name and no crime. It only has my spine, bent.' }],
      furnace: [{ name: 'DEMONIO', charId: 'demonio', text:
        'RIN is self-possessed. RIN does not apologize to the floor. Burn the bow. Keep the discipline.' }],
    },
    bossName: 'SHADOW OF DEMONIO',
    bossLines: [
      { name: 'SHADOW OF DEMONIO', charId: 'demonio', text:
        'It bows. That is the worst part — it bows exactly the way you do. Like an apology with a spine. It has never once bowed to Diablo either.' },
      { name: 'DEMONIO', charId: 'demonio', text:
        'Then we agree on one thing. FIGHT ME STANDING UP.' },
    ],
    resolution: [
      { name: 'DEMONIO', charId: 'demonio', text:
        'The guilt is not mine. It never was. I put it down at the still point and kept walking.' },
      { name: 'THE HEART AND MIND INSIDE', charId: 'demonio', text:
        'What remains is RIN: cold, dignified, complete. He still bows before every fight — but now it is courtesy. Only courtesy.' },
    ],
  },
  docfrank: {
    title: 'DOC FRANK — DESCENT OF THE BLUEPRINT',
    entry: [
      { name: 'THE HEART AND MIND INSIDE', charId: 'docfrank', text:
        'Doc Frank believed the trial was peer review — that Tong-Nou called him to evaluate the soul as an engineering problem. The trial has other plans. It is taking him apart like one of his own prototypes.' },
      { name: 'DOC FRANK', charId: 'docfrank', text:
        'Fine! Peer review goes both ways. I built Cyborg X. I built SAM-UR-A1. Let us see what the dark built. Taking notes. In crayon.' },
    ],
    beats: {
      masks: [{ name: 'DOC FRANK', charId: 'docfrank', text:
        'Masks? I have reskins for every occasion. But under all of them — notes say — there is a man who was not sure he had a soul, so he built two to check.' }],
      drowning: [{ name: 'DOC FRANK', charId: 'docfrank', text:
        'Here are the souls I cannot build: Mariposa\'s. Waterfall\'s. The nine themselves. The clipboard is filling up. The crayon is shaking.' }],
      furnace: [{ name: 'DOC FRANK', charId: 'docfrank', text:
        'The god complex burns nicely. It turns out "data" was always a word for "I am afraid." Noting that. Underlining it twice.' }],
    },
    bossName: 'SHADOW OF DOC FRANK',
    bossLines: [
      { name: 'SHADOW OF DOC FRANK', charId: 'docfrank', text:
        'It takes notes on you. Mid-fight. In crayon. The notes are detailed, accurate, and deeply insulting.' },
      { name: 'DOC FRANK', charId: 'docfrank', text:
        'I have never been so proud and so offended at once. EXCELLENT craft. Now hold still.' },
    ],
    resolution: [
      { name: 'DOC FRANK', charId: 'docfrank', text:
        'The difference between making a thing and being the thing. I am the thing. The clipboard can rest.' },
      { name: 'THE HEART AND MIND INSIDE', charId: 'docfrank', text:
        'He descended to evaluate the soul and was evaluated instead. Peer review: PASS. Barely. The crayon says so.' },
    ],
  },
  'mariposa-monarch': {
    title: 'MARIPOSA — DESCENT OF THE SEAL',
    entry: [
      { name: 'THE HEART AND MIND INSIDE', charId: 'mariposa-monarch', text:
        'Mariposa hatched in the branches of the Tree of Life — the trial\'s only native. She came down here following a leak: something sealed slipped into the Western Heart. But the oldest truth is this: you do not guard a door that long without the door becoming part of you.' },
      { name: 'MARIPOSA', charId: 'mariposa-monarch', text:
        'The trial keeps offering me purification. I keep declining — I have a post to hold. ...But the wings itch. Fine. I will check the locks on the way down.' },
    ],
    beats: {
      masks: [{ name: 'MARIPOSA', charId: 'mariposa-monarch', text:
        'Masks, masks. Keepers wear so many. Under the last one there is just... a person? The joints crack when I think about it. Backward, like a door unlatching.' }],
      drowning: [{ name: 'MARIPOSA', charId: 'mariposa-monarch', text:
        'What I buried: the question the trial keeps asking. Who am I when I am not guarding anything? I do not know yet. The water is patient. So am I.' }],
      furnace: [{ name: 'MARIPOSA', charId: 'mariposa-monarch', text:
        'The seal holds as long as I do. But cocoons are for changing — and something in me is starting to feel the itch in her wings.' }],
    },
    bossName: 'SHADOW OF MARIPOSA',
    bossLines: [
      { name: 'SHADOW OF MARIPOSA', charId: 'mariposa-monarch', text:
        'It does not guard anything. No post, no seal, no door. It just... is. That is what scares you. Not the dark. The freedom.' },
      { name: 'MARIPOSA', charId: 'mariposa-monarch', text:
        'Everything soft lands last. Even me. Especially me.' },
    ],
    resolution: [
      { name: 'MARIPOSA', charId: 'mariposa-monarch', text:
        'I am still the keeper. But now I know the keeper is a person first and a lock second. The seal holds. So do I.' },
      { name: 'THE HEART AND MIND INSIDE', charId: 'mariposa-monarch', text:
        'Her joints crack backward one last time — and then, for the first time, they bend the right way. The eye-spots blink, left to right. All four. The floor can wait.' },
    ],
  },
  thor: {
    title: 'THOR — DESCENT OF THE THUNDER',
    entry: [
      { name: 'THE HEART AND MIND INSIDE', charId: 'thor', text:
        'Thor does not know he is being purified. That is the point. The thunder god walks down into his own heart the way he walks into weather — like it belongs to him.' },
      { name: 'THOR', charId: 'thor', text:
        'A descent? Into MYSELF? Hah! I have been struck by lightning more times than you have had doubts. Lead on.' },
    ],
    beats: {
      masks: [{ name: 'THOR', charId: 'thor', text:
        'Masks? These are not masks — these are FACES. Every storm I ever was. I remember all of them. I regret none of them. ...Most of them.' }],
      drowning: [{ name: 'THOR', charId: 'thor', text:
        'What I buried: the quiet after the thunder. The part of the god that is afraid of silence. It is LOUD down here, and I do not like it.' }],
      furnace: [{ name: 'THOR', charId: 'thor', text:
        'The furnace asks what I will burn to stay myself. EASY. Everything that is not thunder. ...Why is my hand shaking?' }],
    },
    bossName: 'SHADOW OF THOR',
    bossLines: [
      { name: 'SHADOW OF THOR', charId: 'thor', text:
        'It does not boast. It does not laugh. It just stands there — all the thunder with none of the joy. This is what a god looks like without anyone to protect.' },
      { name: 'THOR', charId: 'thor', text:
        '...Oh. OH. That is what this was about. COME HERE, YOU MISERABLE CLOUD.' },
    ],
    resolution: [
      { name: 'THOR', charId: 'thor', text:
        'I am still thunder. But now I know the silence between the strikes is mine too. A god who only knows noise is just weather.' },
      { name: 'THE HEART AND MIND INSIDE', charId: 'thor', text:
        'He still does not know he was purified. That is still the point. Some doors only open for those who are not looking for them.' },
    ],
  },
  rin: nineStory('rin'), byou: nineStory('byou'), tou: nineStory('tou'),
  sha: nineStory('sha'), kai: nineStory('kai'), jin_soul: nineStory('jin_soul'),
  retsu: nineStory('retsu'), zen: nineStory('zen'), gyou: nineStory('gyou'),
};

/* Generic frame: every other fighter plugs in here. Built from their
   roster identity — a real personal arc, not placeholder text. */
export function genericStory(char) {
  const name = char.name || 'THE SOUL';
  const title = (char.title || 'A wandering soul').toUpperCase();
  const style = char.style || 'their own way';
  return {
    title: `${name} — DESCENT OF THE ${title}`,
    entry: [
      { name: 'THE HEART AND MIND INSIDE', charId: char.id, text:
        `The trial turned inward for ${name}, ${title}. Not across the five lands — down. Every soul carries a dark it will not name.` },
      { name, charId: char.id, text:
        `I fight ${style}. But down here there is no style. Only the truth, waiting with my face on.` },
    ],
    beats: {
      masks: [{ name, charId: char.id, text:
        'Every face I have worn, lined up like opponents. I bow to none of them. I know all their tells.' }],
      drowning: [{ name, charId: char.id, text:
        'What I buried. It has been breathing down here the whole time, waiting for me to get tired of holding my breath.' }],
      furnace: [{ name, charId: char.id, text:
        'The furnace asks what I will burn to stay myself. Everything that is not me. Starting now.' }],
    },
    bossName: 'SHADOW OF ' + name,
    bossLines: [
      { name: 'SHADOW OF ' + name, charId: char.id, text:
        'It moves like you. It wants like you. The only difference is that it stopped pretending.' },
    ],
    resolution: [
      { name, charId: char.id, text:
        'Named. Faced. Put down. The dark is still mine — but now it walks behind me, not inside me.' },
      { name: 'THE HEART AND MIND INSIDE', charId: char.id, text:
        'Purification is not becoming someone else. It is meeting yourself and staying.' },
    ],
  };
}

export function getHeartmindStory(char) {
  return HEARTMIND_STORIES[char.id] || genericStory(char);
}

/* ============================================================
   Controller — wires the descent into Game + ModeController patterns.
   ============================================================ */
export class HeartmindController {
  constructor(deps) {
    this.game = deps.game;
    this.ui = deps.ui;
    this.show = deps.show;
    this.startFight = deps.startFight;
    this.roster = deps.roster;
    this.getChar = deps.getChar;
    this.audio = deps.audio;
    this.run = null;      // { fighterId, stage, hp, wave }
    this._lastCard = null;
    this._shadow = null;
    this.party = null;      // campaign layer (Lane 6): party state, or null
    this._inFight = false;  // campaign layer: true between _fightWave and _waveEnd
  }
  clear() { this.run = null; this._lastCard = null; this._shadow = null; this.party = null; this._inFight = false; setModeTag(''); }

  /* ---- select flow (mirrors ModeController, standalone) ---- */
  beginSelect() {
    this.clear();
    const m = window.__modes;
    if (m) { m.clearState(); m.mode = 'heartmind'; }
    this.show('select');
    const hint = document.getElementById('select-hint');
    if (hint) hint.textContent =
      'THE HEART AND MIND INSIDE — choose your soul.';
    const btn = document.getElementById('confirm-fighter');
    if (btn) btn.disabled = true;
  }
  trackCard(id) { this._lastCard = id; }
  onConfirm() {
    const m = window.__modes;
    if (!m || m.mode !== 'heartmind' || !this._lastCard) return false;
    const id = this._lastCard;
    this._lastCard = null;
    this.start(id);
    return true;
  }

  /* ---- the descent ---- */
  async start(fighterId) {
    const char = this.getChar(fighterId);
    if (!char) return;
    this.run = { fighterId, stage: 0, hp: null, wave: 0, road: null };
    this.party = createPartyState([fighterId]);
    this._shadow = buildShadowSelf(char);
    const story = getHeartmindStory(char);
    this._story = story;
    setModeTag('THE HEART AND MIND INSIDE');
    showLoading('DESCENDING…');
    // Entry cutscene over the select screen, then stage 1.
    playStoryBeats(story.entry, () => this._runStage(), story.title);
  }

  _runStage() {
    const st = HEARTMIND_STAGES[this.run.stage];
    if (!st) { this._complete(); return; }
    this.run.wave = 0;
    this.run.road = roadInto(st.key);
    const story = this._story;
    const beat = story.beats[st.key];
    const open = [
      { name: st.name, charId: this.run.fighterId,
        text: `${st.sub} Stage ${st.n} of 5.` },
      ...(beat || []),
    ];
    playStoryBeats(open, () => this._fightWave(), st.name);
  }

  _pickEcho(diff, excludeId) {
    const pool = this.roster.filter((c) => c.id !== excludeId && ECHO_POOL.includes(c.id));
    const list = pool.length ? pool : this.roster.filter((c) => c.id !== excludeId);
    const c = list[Math.floor(Math.random() * list.length)];
    return makeEcho(this.getChar(c.id) || c, diff);
  }

  _fightWave() {
    const st = HEARTMIND_STAGES[this.run.stage];
    const char = this.getChar(this.run.fighterId);
    this._inFight = true;
    let foe;
    let label;
    if (this.run.wave < st.waves) {
      foe = this._pickEcho(Math.min(0.95, st.diff + this.run.wave * 0.04), this.run.fighterId);
      label = `${st.name} · ECHO ${this.run.wave + 1}/${st.waves}`;
    } else {
      // Stage boss: the shadow self (stage 5) or a named inner demon.
      if (st.key === 'stillpoint') {
        foe = this._shadow;
        label = `${st.name} · ${this._story.bossName}`;
      } else {
        const bossPool = ['diablo', 'phantom', 'dio'];
        const b = this.getChar(bossPool[this.run.stage % bossPool.length]) || this.getChar('diablo');
        foe = makeEcho(b, Math.min(0.95, st.diff + 0.12));
        foe.name = 'WARDEN OF ' + st.name;
        label = `${st.name} · WARDEN`;
      }
    }
    this.ui.banner && this.ui.banner(label);
    setModeTag('HEART ♥ MIND · ' + st.name);
    this.game.onMatchEnd = (won) => this._waveEnd(won);
    const opts = {
      mode: 'heartmind', roundsToWin: 1, stage: st.stage, enemyChar: foe,
    };
    if (this.run.hp != null) opts.hpCarry = this.run.hp;
    showLoading('THE DARK STIRS…');
    this.startFight(this.run.fighterId, null, opts);
  }

  _waveEnd(won) {
    const st = HEARTMIND_STAGES[this.run.stage];
    this._inFight = false;
    const g = this.game;
    if (!won) {
      // Death inside is still death: the descent ends.
      const rec = whGetRecords();
      const key = 'heartmind_' + this.run.fighterId;
      playStoryBeats([
        { name: 'THE HEART AND MIND INSIDE', charId: this.run.fighterId,
          text: `The dark keeps what it catches. ${st.name} holds you at ${this.run.wave < st.waves ? 'echo ' + (this.run.wave + 1) : 'the warden'}. Descend again — it will be waiting.` },
      ], () => {
        this.show('menu');
        if (window.__modes) window.__modes.clearState();
        this.clear();
      }, 'THE DARK KEEPS WHAT IT CATCHES');
      return;
    }
    // Soul ember: the eater grows — HP restore between waves.
    const restored = Math.min(g.p1.maxHp, g.p1.hp + g.p1.maxHp * st.restore);
    this.run.hp = restored;
    this.run.wave++;
    const isBossWave = this.run.wave > st.waves;
    if (!isBossWave) {
      this.ui.banner && this.ui.banner(`ECHO DOWN — SOUL EMBER +${Math.round(st.restore * 100)}%`);
      setTimeout(() => this._fightWave(), 1200);
    } else {
      // Stage clear → record + next stage.
      const key = 'heartmind_' + this.run.fighterId;
      const rec = whGetRecords();
      if (st.n > (rec[key] || 0)) whSetRecord(key, st.n);
      if (this.party) recordPartyStageClear(this.party, this.run.fighterId, st.key);
      if (st.key === 'stillpoint') { this._shadowDown(); return; }
      this.ui.banner && this.ui.banner(`${st.name} CLEARED`);
      setTimeout(() => {
        // Pre-boss confrontation lines on the final stage.
        if (HEARTMIND_STAGES[this.run.stage + 1] &&
            HEARTMIND_STAGES[this.run.stage + 1].key === 'stillpoint') {
          playStoryBeats(this._story.bossLines, () => {
            this.run.stage++;
            this._runStage();
          }, this._story.bossName);
        } else {
          this.run.stage++;
          this._runStage();
        }
      }, 1400);
    }
  }

  _shadowDown() {
    const char = this.getChar(this.run.fighterId);
    const key = 'heartmind_' + this.run.fighterId + '_clear';
    whSetRecord(key, (whGetRecords()[key] || 0) + 1);
    playStoryBeats(this._story.resolution, () => {
      this.game.onMatchEnd = null;
      if (window.__modes) window.__modes.clearState();
      // Reuse the classic result screen for the triumph.
      const ui2 = window.__ui;
      if (ui2 && ui2.matchOver) ui2.matchOver(true);
      const t = document.getElementById('result-title');
      if (t) t.textContent = 'PURIFIED';
      const s = document.getElementById('result-sub');
      if (s) s.textContent = `${char.name} met themselves at the still point — and stayed. The Heart and Mind Inside: complete.`;
      this.clear();
    }, 'PURIFICATION');
  }

  _complete() { this.clear(); }

  rematch() {
    // Retry the current wave from the result screen.
    if (this.run) this._fightWave();
  }

  /* ---- campaign layer (Lane 6: roads, party, journal) ----
     Party switching is allowed BETWEEN fights only, never
     mid-fight (Scenario Campaign model: choose your fighter for
     the next stage, don't swap mid-combo). The shadow self
     follows the active fighter: it is "yourself, unmasked", so
     switching fighters rebuilds it. setParty() preserves the
     current fighter's live run progress. */
  setParty(fighterIds) {
    const current = this.run
      ? { stage: this.run.stage, wave: this.run.wave, hp: this.run.hp }
      : null;
    // Keep journal clears the current fighter already earned.
    const oldCleared = (this.party && this.run && this.party.progress[this.run.fighterId])
      ? this.party.progress[this.run.fighterId].cleared || []
      : [];
    this.party = createPartyState(fighterIds);
    if (current && this.run && this.party.progress[this.run.fighterId]) {
      this.party.progress[this.run.fighterId] = { ...current, cleared: oldCleared };
    }
    return this.party;
  }

  switchFighter(fighterId) {
    if (!this.run) return { ok: false, reason: 'no-run' };
    if (this._inFight) return { ok: false, reason: 'in-fight' };
    if (this.party) {
      this.party.progress[this.run.fighterId] = {
        stage: this.run.stage, wave: this.run.wave, hp: this.run.hp,
        cleared: (this.party.progress[this.run.fighterId] || {}).cleared || [],
      };
    } else {
      this.party = createPartyState([this.run.fighterId, fighterId]);
      this.party.progress[this.run.fighterId] = {
        stage: this.run.stage, wave: this.run.wave, hp: this.run.hp, cleared: [],
      };
    }
    const res = switchPartyFighter(this.party, fighterId);
    if (!res.ok) return res;
    this.run.fighterId = fighterId;
    this.run.stage = res.progress.stage;
    this.run.wave = res.progress.wave;
    this.run.hp = res.progress.hp;
    const char = this.getChar(fighterId);
    if (char) {
      this._story = getHeartmindStory(char);
      this._shadow = buildShadowSelf(char);
    }
    this.run.road = roadInto(HEARTMIND_STAGES[this.run.stage].key);
    return { ok: true, fighterId, stage: HEARTMIND_STAGES[this.run.stage].key, road: this.run.road };
  }

  /* The road the current stage was reached by (null at the
     Threshold, where the descent begins). The UI lane may show
     its `walk` line on the stage card. */
  currentRoad() {
    return (this.run && this.run.road) || null;
  }

  /* Ragdoll contexts this mode allows (physics lane consumes). */
  ragdollContexts() { return HM_RAGDOLL_CONTEXTS; }
}
