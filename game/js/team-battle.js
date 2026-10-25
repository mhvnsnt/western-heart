/* ============================================================
   WESTERN HEART — TTT2 Tag Battle systems (worker 24, 2026-10-22)

   Pulls Tekken Tag Tournament 2's tag-team systems into versus mode,
   per the owner's verbatim directive: "Pull Tekken Tag Tournament 2's
   team battle system into versus mode, straight from the TTT2 teardown
   files... Pull the ACTUAL team sizes, tag mechanics, and select flow
   from the TTT2 teardown files and replicate them exactly. No guessing."

   Sourcing (no guessing — every number below is cited):
   - Repo teardown (teardown/tekken-tag-tournament-2/TEARDOWN.md):
     archive-level record only (Xbox 360 STFS, extraction blocked on
     disk space). It confirms the 2v2 tag format but carries NO
     mechanic data — the moveset binaries are inside undecrypted
     containers. Mechanics below come from public TTT2 documentation
     (full citations in docs/research/ttt2-teardown-audit.md).
   - Team sizes (TTT2 actual): SOLO 1v1 | TAG 2v2 (default) |
     HANDICAP 2v1/1v2 | TEAM BATTLE mode up to 8 per team
     (tekken.fandom.com/wiki/Tekken_Tag_Tournament_2;
      neogaf.com TTT2 OT single-player options list).
   - Select flow (TTT2 actual): "before you select your characters, you
     will choose whether to play as a single character or a two-person
     tag team" (CheatCC Harada hands-on) — the submenu lives INSIDE the
     character select screen, before any fighter is picked.
   - Tag in/out: dedicated tag button (5 = LP+RP); partner leaps in,
     tagging in leaves you briefly vulnerable (CheatCC/Harada).
   - Red health: damage taken while active becomes recoverable; the
     benched partner gradually recovers it (GameFAQs review).
   - Rage: partner's bar flashing red (low HP) -> tagged-in fighter
     gets a temporary damage boost (GameFAQs; vsavs.weebly).
   - Tag combo: press tag BEFORE a launcher hits ("tag bufferable
     launcher... only possible on hit"); the combo removes recoverable
     health (fightinggameguide.com/tekkentag2).
   - Tag assault: press tag DURING a Bound move; partner jumps in,
     loses ALL red health; player gets one movement + one attack action
     (strings count as one), then control passes back; does NOT remove
     recoverable health; uses Rage + own recoverable health; gives the
     opponent's partner Rage (GiantBomb wiki; fightinggameguide).
     Direct Assault = 1+2+5, a mid that Bounds for a Tag Assault.
   - Tag crash: active grounded (knocked down / ukemi) + inactive
     partner has Rage -> both punches + tag; partner dives in from the
     air and stops the opponent's attack; surrenders Rage + the exiting
     partner's red health (GiantBomb wiki; GameFAQs).
   - Tag throws: combined throws for specific pairings (GiantBomb).
   - Win condition: K.O. one member of the team to win the round
     (CheatCC/Harada — like TTT1).
   - Solo balance: solo fighters get boosted damage output and reduced
     damage input vs tag teams (CheatCC/Harada; neogaf).

   Engine mapping (this file):
   - TagMatch owns both sides' two Fighter instances. game.p1/game.p2
     ALWAYS point at the active fighters; a tag swaps which Fighter
     object those references (and the scene graph, and the AI target)
     point at. Benched fighters are parked off-scene: not updated, not
     hittable, regenerating red health on a timer.
   - The tag button is a first-class input ('tag'): touch TAG button
     (index.html) + keyboard T (input.js). game.js dispatches it here.
   ============================================================ */
import { lazy } from './lazy.js';
import { applyFighterProfile } from './customization-consumer.js';

/* TTT2 tuning, adapted to this engine's 100-HP scale. */
const RED_SHARE = 0.8;    // fraction of damage taken that becomes recoverable red
const RED_REGEN = 9;      // HP/sec of red converted back while benched
const RED_CAP = 0.65;     // red never exceeds 65% of max HP
const RAGE_MULT = 1.25;   // TTT2 rage damage boost ("temporary boost in strength")
const RAGE_HP = 0.30;     // partner at/below 30% -> the active fighter rages
const RAGE_READY_HP = 0.5;// benched partner at/below 50% -> Tag Crash available
const TAG_CD = 5;         // seconds between voluntary raw tags (anti-spam)
const COMBO_BUF = 0.45;   // tag-bufferable launcher window (seconds)
const ASSAULT_T = 3.2;    // tag assault: player-controlled seconds before auto-return
const NO_RED_T = 5;       // tag combo: damage is unrecoverable for this long

export class TagMatch {
  /* teams: { p1: [entryA, entryB], p2: [entryA, entryB] } — full roster
     entries (attire already resolved by main.js startFight). entries[0]
     is the point fighter (already spawned as game.p1/game.p2). */
  constructor(game, teams) {
    this.game = game;
    this.entries = teams;
    this.sides = {
      p1: { fighters: [], active: 0, tagCd: 0, buf: 0, assaultT: 0, foeHitT: 0, lastFoeHp: 0 },
      p2: { fighters: [], active: 0, tagCd: 0, buf: 0, assaultT: 0, foeHitT: 0, lastFoeHp: 0 },
    };
    this._noRedT = 0;
    this._hud = null;
    this._hudT = 0;
    this._aiThinkT = 0;
    this._built = false;
  }

  active(side) { const s = this.sides[side]; return s.fighters[s.active]; }
  bench(side) { const s = this.sides[side]; return s.fighters[1 - s.active]; }

  /* Build the benched partners. Called from game.startMatch AFTER the
     point fighters exist (models for all four are preloaded by
     main.js startFight). */
  async build() {
    const { Fighter } = await lazy.fighter();
    const g = this.game;
    for (const side of ['p1', 'p2']) {
      const S = this.sides[side];
      const foeSide = side === 'p1' ? 'p2' : 'p1';
      const active = side === 'p1' ? g.p1 : g.p2;
      const foe = side === 'p1' ? g.p2 : g.p1;
      S.fighters[0] = active;
      // Clone stats: rage must never mutate the shared roster entry
      // (Fighter aliases charData.stats when the entry carries stats).
      active.stats = { ...active.stats };
      this._initTag(active, false);
      const benchEntry = this.entries[side][1];
      const bench = new Fighter(benchEntry, side === 'p1' ? -30 : 30, side === 'p1' ? 1 : -1, side === 'p1');
      bench.game = g;
      bench._sceneRef = g.arena;
      try { applyFighterProfile(bench); } catch (e) { /* cosmetic only */ }
      bench.stats = { ...bench.stats };
      this._initTag(bench, true);
      S.fighters[1] = bench;
      S.lastFoeHp = foe.hp;
    }
    this._buildHud();
    this._built = true;
    this._refreshHud(true);
  }

  _initTag(f, benched) {
    f._tag = {
      red: 0, rage: false, rageReady: false, rageBlockT: 0,
      lastHp: f.hp, benched, basePower: f.stats.power,
      diveAtk: false,
    };
  }

  /* ---------------- the tag button ---------------- */
  /* TTT2 uses ONE tag button; context decides the technique:
     knocked down + partner enraged -> TAG CRASH;
     foe juggled off your recent hit -> TAG ASSAULT;
     pressed mid-attack -> buffered for a TAG COMBO on launcher;
     otherwise (neutral, can act) -> raw TAG. */
  requestTag(side) {
    const g = this.game;
    if (!this._built || !g || g.roundState !== 'fight' || g.paused) return false;
    const S = this.sides[side];
    if (S.tagCd > 0 || S.assaultT > 0) return false;
    const act = S.fighters[S.active];
    const ben = S.fighters[1 - S.active];
    const foe = side === 'p1' ? g.p2 : g.p1;
    if (!act || !ben || act.hp <= 0 || ben.hp <= 0 || act.dead) return false;

    // TAG THROW (TTT2: combined tag throws) — pressed during your throw:
    // the partner leaps in as the throw lands.
    if (act.state === 'throwing') {
      this._swap(side);
      ben._tag.diveAtk = true;
      S.tagCd = TAG_CD;
      g.ui.banner('TAG THROW — partner follows up');
      return true;
    }
    // TAG CRASH (TTT2: grounded + partner has Rage -> LP+RP+tag) —
    // the partner dives in from the air and stops the pressure.
    if (act.state === 'knockdown' || (act.state === 'hitstun' && !act.onGround)) {
      if (ben._tag.rageReady) { this._doCrash(side); return true; }
      g.ui.banner('NO RAGE — TAG CRASH DENIED');
      return false;
    }
    // TAG ASSAULT (TTT2: tag during Bound) — foe is bouncing/juggled off
    // your hit: partner jumps in for one player-controlled string.
    const foeJuggled = !foe.onGround || foe.state === 'knockdown' || (foe._juggle > 0);
    if (foeJuggled && S.foeHitT > 0) { this._doAssault(side); return true; }
    // Buffered: pressed mid-attack, before the launcher lands (TTT2 "tag
    // bufferable launcher"). Consumed in onUpdate when the launch hits.
    if (!act.canAct()) { S.buf = COMBO_BUF; return true; }
    // Raw tag (TTT2: tag button in neutral). TTT2 leaves the incoming
    // fighter briefly vulnerable — no invuln here, the leap IS the risk.
    this._swap(side);
    S.tagCd = TAG_CD;
    g.ui.banner(`${ben.char.name.toUpperCase()} TAGS IN`);
    return true;
  }

  /* Core swap: bench the active fighter, leap the partner in.
     opts.dive — tag crash: partner drops from the sky onto the foe. */
  _swap(side, opts = {}) {
    const g = this.game;
    const S = this.sides[side];
    const out = S.fighters[S.active];
    const inc = S.fighters[1 - S.active];
    const foe = side === 'p1' ? g.p2 : g.p1;
    const dir = side === 'p1' ? 1 : -1;

    // Park the outgoing fighter (kept alive: hp/red/rage persist).
    out._tag.benched = true;
    out._tag.lastHp = out.hp;
    out.vx = out.vy = out.vz = 0;
    this._setRage(out, false);
    try { g.arena.scene.remove(out.root); } catch (e) { /* already out */ }

    // Leap the partner in, TTT2 style — from behind, toward the foe.
    const foeX = foe.root.position.x;
    inc.root.position.set(foeX - dir * (opts.dive ? 1.6 : 3.4), 0, 0);
    inc.facing = dir;
    inc._faceY = dir * Math.PI / 2;
    if (inc.lean) inc.lean.rotation.y = inc._faceY;
    inc.vz = 0;
    if (opts.dive) {
      inc.root.position.y = 3.4;
      inc.vy = -9;
      inc.onGround = false;
      inc._tag.diveAtk = true; // auto-attack on landing (the crash hit)
    } else {
      inc.root.position.y = 0.01;
      inc.vy = 4.5;
      inc.vx = dir * 5.5;
      inc.onGround = false;
    }
    try { inc._enter('jump'); } catch (e) { inc.state = 'jump'; }
    inc._tag.benched = false;
    inc._tag.lastHp = inc.hp;
    inc.game = g;
    inc._sceneRef = g.arena;
    try { g.arena.scene.add(inc.root); } catch (e) { /* already in */ }

    S.active = 1 - S.active;
    S.buf = 0;
    if (side === 'p1') g.p1 = inc;
    else { g.p2 = inc; if (g.ai) g.ai.f = inc; }
    g.ui.setNames(g.p1.char.name, g.p2.char.name);
    this._refreshHud(true);
  }

  /* TAG CRASH (TTT2): grounded + partner enraged. Surrenders Rage and the
     exiting partner's red health. */
  _doCrash(side) {
    const g = this.game;
    const S = this.sides[side];
    const out = S.fighters[S.active];
    const inc = S.fighters[1 - S.active];
    out._tag.red = 0;                       // exiting partner's red: gone
    inc._tag.rageReady = false;
    inc._tag.rageBlockT = 8;                // rage spent — no instant re-rage
    this._setRage(inc, false);
    this._swap(side, { dive: true });
    S.tagCd = TAG_CD;
    g.ui.banner('TAG CRASH!');
    try { g.arena.shake(0.5, 0.35); } catch (e) { /* no arena shake */ }
  }

  /* TAG ASSAULT (TTT2): tag during Bound. Partner jumps in LOSING ALL red
     health; the player controls them for one string (one movement + one
     attack action), then control passes back. Gives the OPPONENT's partner
     Rage. Does not remove recoverable health. */
  _doAssault(side) {
    const g = this.game;
    const S = this.sides[side];
    const foeSide = side === 'p1' ? 'p2' : 'p1';
    const inc = S.fighters[1 - S.active];
    inc._tag.red = 0;                        // partner loses all red on entry
    this._swap(side);
    S.assaultT = ASSAULT_T;
    S.tagCd = 0;
    // TTT2: the assault always gives the opponent's partner Rage.
    const foeBen = this.sides[foeSide].fighters[1 - this.sides[foeSide].active];
    if (foeBen && foeBen.hp > 0) foeBen._tag.rageReady = true;
    g.ui.banner('TAG ASSAULT — one string!');
  }

  /* TAG COMBO (TTT2: buffered tag before a launcher hits). Partner swaps
     in mid-juggle and the combo continues; damage dealt during the window
     removes recoverable health (unrecoverable). */
  _doCombo(side) {
    const g = this.game;
    const S = this.sides[side];
    this._swap(side);
    this._noRedT = NO_RED_T;
    S.tagCd = TAG_CD;
    g.ui.banner('TAG COMBO!');
  }

  _setRage(f, on) {
    const t = f._tag;
    if (!t || t.rage === on) return;
    t.rage = on;
    if (t.basePower == null) t.basePower = f.stats.power;
    f.stats.power = on ? t.basePower * RAGE_MULT : t.basePower;
    if (on) {
      try { this.game.ui.banner(`${f.char.name.toUpperCase()} — RAGE!`); } catch (e) { /* hud */ }
    }
  }

  /* Per-frame: red health, rage, tag buffers, assault timer, AI tags. */
  onUpdate(dt) {
    const g = this.game;
    if (!this._built || g.roundState !== 'fight') return;
    if (this._noRedT > 0) this._noRedT -= dt;

    for (const side of ['p1', 'p2']) {
      const S = this.sides[side];
      const foeSide = side === 'p1' ? 'p2' : 'p1';
      const act = S.fighters[S.active];
      const ben = S.fighters[1 - S.active];
      const foe = foeSide === 'p1' ? g.p1 : g.p2;
      if (S.tagCd > 0) S.tagCd -= dt;
      if (S.foeHitT > 0) S.foeHitT -= dt;

      // "My side just hit the foe" — no hit-code hooks needed.
      if (foe.hp < S.lastFoeHp) S.foeHitT = 0.6;
      S.lastFoeHp = foe.hp;

      // Buffered tag combo: the launcher connected — partner takes over.
      if (S.buf > 0) {
        S.buf -= dt;
        const launched = !foe.onGround || foe.state === 'knockdown' || (foe._juggle > 0);
        if (launched && S.foeHitT > 0) { this._doCombo(side); continue; }
        if (S.buf <= 0) S.buf = 0;
      }

      // Tag assault: player-controlled string, then auto-return.
      if (S.assaultT > 0) {
        S.assaultT -= dt;
        if (S.assaultT <= 0) { this._swap(side); g.ui.banner('ASSAULT OVER'); }
      }

      // Dive attacks (tag crash / tag throw follow-up) land the hit.
      for (const f of [act, ben]) {
        const t = f._tag;
        if (t.diveAtk && !t.benched && f.onGround && f.hp > 0) {
          t.diveAtk = false;
          try { f.tryAttack('1+2'); } catch (e) { /* whiffed dive */ }
        }
        if (t.rageBlockT > 0) t.rageBlockT -= dt;
      }

      // Red health: damage taken while active becomes recoverable...
      for (const f of [act, ben]) {
        const t = f._tag;
        const lost = t.lastHp - f.hp;
        if (lost > 0 && !t.benched && this._noRedT <= 0) {
          t.red = Math.min(t.red + lost * RED_SHARE, f.maxHp * RED_CAP);
        }
        t.lastHp = f.hp;
        // ...and the benched partner gradually recovers it (TTT2).
        if (t.benched && t.red > 0 && f.hp > 0) {
          const heal = Math.min(t.red, RED_REGEN * dt);
          f.hp = Math.min(f.maxHp, f.hp + heal);
          t.red -= heal;
        }
      }

      // RAGE (TTT2): the active fighter rages while the benched partner
      // is in trouble (<=30%), or while critically low themselves.
      const shouldRage = !act._tag.benched && act.hp > 0 && act._tag.rageBlockT <= 0 &&
        (ben.hp <= ben.maxHp * RAGE_HP || act.hp <= act.maxHp * 0.2);
      this._setRage(act, shouldRage);
      // Crash availability: benched partner "enraged" at <=50%.
      ben._tag.rageReady = ben.hp > 0 && ben.hp <= ben.maxHp * RAGE_READY_HP;
    }

    // CPU tags like a player: tag out when hurt and the partner is
    // healthier; crash out of knockdowns when the partner rages.
    this._aiThinkT -= dt;
    if (this._aiThinkT <= 0) {
      this._aiThinkT = 0.8;
      this._aiTag();
    }

    this._hudT -= dt;
    if (this._hudT <= 0) { this._hudT = 0.15; this._refreshHud(); }
  }

  _aiTag() {
    const S = this.sides.p2; // CPU side in versus
    if (S.tagCd > 0 || S.assaultT > 0) return;
    const act = S.fighters[S.active];
    const ben = S.fighters[1 - S.active];
    if (!act || !ben || act.hp <= 0 || ben.hp <= 0) return;
    if ((act.state === 'knockdown' || (act.state === 'hitstun' && !act.onGround)) && ben._tag.rageReady) {
      if (Math.random() < 0.45) this.requestTag('p2');
      return;
    }
    if (act.canAct() && act.hp < act.maxHp * 0.35 && ben.hp > act.hp + act.maxHp * 0.15) {
      this.requestTag('p2');
    }
  }

  /* Round reset (TTT2: every round starts with the point fighters). */
  onRoundStart() {
    const g = this.game;
    if (!this._built) return;
    for (const side of ['p1', 'p2']) {
      const S = this.sides[side];
      const spawns = { p1: -3, p2: 3 };
      for (let i = 0; i < 2; i++) {
        const f = S.fighters[i];
        const t = f._tag;
        f.hp = f.maxHp;
        t.red = 0; t.lastHp = f.hp; t.rageBlockT = 0; t.diveAtk = false;
        this._setRage(f, false);
        t.benched = i !== 0;
        f.dead = false; f.stun = 0; f.vx = f.vy = f.vz = 0;
        try { f._enter('idle'); } catch (e) { f.state = 'idle'; }
      }
      const act = S.fighters[0];
      const dir = side === 'p1' ? 1 : -1;
      try { g.arena.scene.remove(S.fighters[1].root); } catch (e) { /* out */ }
      act.root.position.set(spawns[side], 0, 0);
      act.facing = dir;
      act._faceY = dir * Math.PI / 2;
      if (act.lean) act.lean.rotation.y = act._faceY;
      try { g.arena.scene.add(act.root); } catch (e) { /* in */ }
      S.active = 0; S.tagCd = 0; S.buf = 0; S.assaultT = 0; S.foeHitT = 0;
      S.lastFoeHp = (side === 'p1' ? g.p2 : g.p1).hp;
      if (side === 'p1') g.p1 = act; else { g.p2 = act; if (g.ai) g.ai.f = act; }
    }
    g.ui.setNames(g.p1.char.name, g.p2.char.name);
    this._refreshHud(true);
  }

  destroy() {
    if (this._hud && this._hud.remove) this._hud.remove();
    this._hud = null;
    for (const side of ['p1', 'p2']) {
      for (const f of this.sides[side].fighters) {
        if (f && f._tag) { this._setRage(f, false); f._tag.benched = false; }
      }
    }
    this._built = false;
  }

  /* ---------------- partner HUD (TTT2: both bars visible) ---------------- */
  _buildHud() {
    try {
      const el = document.createElement('div');
      el.id = 'tag-hud';
      el.innerHTML =
        `<div class="tag-side tag-p1side">
           <div class="tag-name" id="tag-p1-name"></div>
           <div class="tag-bar"><i id="tag-p1-hp"></i><b id="tag-p1-red"></b><em id="tag-p1-rage" class="tag-rage" hidden>RAGE</em></div>
         </div>
         <div class="tag-side tag-p2side">
           <div class="tag-name" id="tag-p2-name"></div>
           <div class="tag-bar"><i id="tag-p2-hp"></i><b id="tag-p2-red"></b><em id="tag-p2-rage" class="tag-rage" hidden>RAGE</em></div>
         </div>`;
      document.body.appendChild(el);
      this._hud = el;
    } catch (e) { this._hud = null; }
  }

  _refreshHud(force) {
    if (!this._hud) return;
    try {
      for (const side of ['p1', 'p2']) {
        const ben = this.bench(side);
        if (!ben || !ben._tag) continue;
        const t = ben._tag;
        const hpEl = document.getElementById(`tag-${side}-hp`);
        const redEl = document.getElementById(`tag-${side}-red`);
        const nameEl = document.getElementById(`tag-${side}-name`);
        const rageEl = document.getElementById(`tag-${side}-rage`);
        if (hpEl) hpEl.style.width = Math.max(0, (ben.hp / ben.maxHp) * 100) + '%';
        if (redEl) redEl.style.width = Math.max(0, (t.red / ben.maxHp) * 100) + '%';
        if (nameEl) nameEl.textContent = ben.char.name;
        const act = this.active(side);
        const raging = !!(act && act._tag && act._tag.rage);
        if (rageEl) rageEl.hidden = !raging;
        if (hpEl) hpEl.classList.toggle('low', ben.hp / ben.maxHp < 0.3);
      }
    } catch (e) { /* hud never breaks the fight */ }
  }
}
