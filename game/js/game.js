/* ============================================================
   WESTERN HEART — Game (match arbiter & main loop)
   • Owns the two fighters, the Shrine arena, input & AI.
   • Resolves hitbox/hurtbox collisions every fixed step.
   • Manages rounds (best of 3), 60s timer, win conditions, HUD.
   • Fixed-timestep update (120 Hz), decoupled render (60fps).

   Demo mode: open with ?demo=1 and P1 is also CPU-driven —
   good for watching AI-vs-AI or unattended verification.
   ============================================================ */
import * as THREE from 'three';
import { Arena } from './scene.js';
// LOADSPEED (2026-10-22): fighter.js (rigs, T3 wiring, movesets) is fight-only —
// it streams via lazy.js on first startMatch, not at boot. See js/lazy.js.
import { lazy } from './lazy.js';
import { AIController } from './ai.js';
import { audio } from './audio.js';
import { voice } from './voice.js';
import { getStage } from './stages.js';
import { applyFighterProfile } from './customization-consumer.js';
import { HitFX } from './hitfx.js';

const ROUND_TIME = 60;
const ROUNDS_TO_WIN = 2;   // best of 3
const FIXED_DT = 1 / 120;

export class Game {
  constructor(canvas, input, ui) {
    this.arena = new Arena(canvas);
    this.input = input;
    this.ui = ui;
    this.p1 = null;
    this.p2 = null;
    this.ai = null;
    this.ai1 = null; // P1 AI (demo mode only)
    this.demo = new URLSearchParams(location.search).has('demo');
    this.running = false;
    this.paused = true;
    this._acc = 0;
    this._last = 0;
    this.timer = ROUND_TIME;
    this.round = 1;
    this.wins = { p1: 0, p2: 0 };
    this.roundState = 'idle'; // idle | intro | fight | over
    this._roundLockT = 0;
    this._hitStop = 0;
    // Tekken hit-effect stack (hitfx.js): spark + debris + ring + flash,
    // dt-driven so hitstop freezes the whole stack like Tekken.
    this.hitfx = new HitFX(this.arena.scene);

    /* ---- hit-feel tuning (review-stage tuner, training mode) ----
       Multipliers on top of the wired hit-feel values (Tekken teardown
       numbers come from the retargeting lane; the user NEVER builds from
       zero). 1.0 = untouched. The review stage's tuning section writes
       these live and the user feels the delta on the dummy immediately. */
    this.feel = { hitstop: 1, shake: 1, knockback: 1, launch: 1 };

    /* ---- game-modes lane hooks (modes.js) ----
       onMatchEnd(playerWon): fired when a full match (not a round) is
       decided, instead of ui.matchOver. Null = classic behavior.
       training: endless rounds vs a passive dummy; rounds auto-reset.
       matchStats: per-match player action counters, folded into the
       story reincarnation profile. Reset in startMatch. */
    this.onMatchEnd = null;
    this.training = false;
    this.matchStats = null;

    this._loop = this._loop.bind(this);
    requestAnimationFrame(this._loop);
  }

  /* ---------------- Match setup ----------------
     CLEAN-INIT: every match starts from a known-clean state. No leftover
     fighters, no running timers, no half-loaded assets, no leaked state
     from the previous match. This is the "starts clean" standard.
     Modes lane (r2): opts.roundsToWin (per-match round count, e.g.
     survival/time-attack single-round) and opts.hpCarry (survival/team
     HP carry-over) are honored here so modes.js never pokes the
     fighter internals directly. */
  async startMatch(playerChar, enemyChar, stageId, opts = {}) {
    this.resetFightState();
    // VOICE (2026-10-22): unlock the voice pipeline (builds the subtitle
    // layer; the AudioContext unlock inside is idempotent — main.js
    // unlockAudio owns the gesture).
    voice.unlock();
    // LOADSPEED: warmed during menu idle; usually cached by fight time.
    const { Fighter, setArenaLimit } = await lazy.fighter();
    // Modes lane: per-match round target (default = classic best-of-3).
    this.roundsToWin = opts.roundsToWin || ROUNDS_TO_WIN;

    // Lane 4: stage selection drives arena, collision bounds, spawns.
    const stage = getStage(stageId || 'shrine');
    setArenaLimit(stage.dims.wallDistance);
    this._stageId = stage.id;
    this._stageName = stage.name;

    this.p1 = new Fighter(playerChar, stage.spawns.p1, 1, true);
    this.p2 = new Fighter(enemyChar, stage.spawns.p2, -1, false);
    // Hit-feel tuning: fighters read live multipliers off game.feel
    // (review-stage tuner). Null-safe when no game is attached.
    this.p1.game = this;
    this.p2.game = this;
    // Transformation cinematics need the arena for camera shake.
    this.p1._sceneRef = this.arena;
    this.p2._sceneRef = this.arena;
    this.arena.scene.add(this.p1.root, this.p2.root);
    // Creation Suite consumer (fighter-completeness lane, 2026-10-21):
    // apply each fighter's suite profile parts at their bone sockets —
    // additive attach layer on the finished models; a no-op for fighters
    // without a profile and fail-silent per part, so it can never block
    // or break a match. See js/customization-consumer.js.
    applyFighterProfile(this.p1);
    applyFighterProfile(this.p2);
    this.ai = new AIController(this.p2, enemyChar.ai);
    this.ai1 = this.demo ? new AIController(this.p1, playerChar.ai) : null;

    this.wins = { p1: 0, p2: 0 };
    this.round = 1;
    this.ui.setNames(playerChar.name, enemyChar.name);
    if (this.ui.setStageName) this.ui.setStageName(stage.name);
    this.ui.setRounds(this.wins);
    this.matchStats = { attacks: { punch: 0, kick: 0, grab: 0, surge: 0, dodge: 0 }, blockTime: 0, time: 0, dmgDealt: 0, dmgTaken: 0 };
    this.running = true;
    this.paused = false;
    // Stage content streams in (Tekken retro OBJs fetch async); the fight
    // intro runs on the base arena while the shell loads.
    this.arena.setStage(stage.id);
    // INTRO INTERACTION (2026-10-22): Tekken-style pre-fight character
    // exchange, played in-engine (both fighters live in the arena)
    // before round 1. Skippable; modes opt out via
    // opts.skipIntroInteraction. The interaction module loads on demand
    // (dynamic import) so the menu boot path stays lean.
    if (!opts.skipIntroInteraction) {
      try {
        const { playIntroInteraction } = await import('./intro-interactions.js');
        // Idle the fighters behind the dialogue: their update() only runs
        // during rounds, so pump it on a timer for the beat's duration.
        const idlePump = setInterval(() => {
          try {
            if (this.p1 && this.p2 && !this.p1.dead && !this.p2.dead) {
              this.p1.update(1 / 60, this.p2);
              this.p2.update(1 / 60, this.p1);
            }
          } catch (e) { /* never break the intro on animation */ }
        }, 1000 / 60);
        await playIntroInteraction(this, playerChar, enemyChar);
        clearInterval(idlePump);
      } catch (e) { console.warn('[WH] intro interaction failed:', e?.message || e); }
    }
    this._startRound();
    // Modes lane: HP carry-over (survival / team battle / qombat) —
    // applied after _startRound's full-heal so the carry is exact.
    if (opts.hpCarry != null && this.p1) {
      this.p1.hp = Math.max(1, Math.min(this.p1.maxHp, opts.hpCarry));
      this.ui.updateHP(this.p1, this.p2);
    }
  }

  /* Fully reset all fight state. Called at the start of every match AND
     when leaving the fight screen, so no state leaks between screens. */
  resetFightState() {
    // Remove old fighters from the scene
    if (this.p1) { this.arena.scene.remove(this.p1.root); this.p1 = null; }
    if (this.p2) { this.arena.scene.remove(this.p2.root); this.p2 = null; }
    this.ai = null;
    this.ai1 = null;
    // Reset all match state
    this.wins = { p1: 0, p2: 0 };
    this.round = 1;
    this.timer = ROUND_TIME;
    this.roundState = 'idle';
    this._roundLockT = 0;
    this._hitStop = 0;
    this._acc = 0;
    this.running = false;
    this.paused = true;
    // Reset input (no stuck keys/buttons from previous match)
    if (this.input) this.input.reset();
    // Reset HUD
    this.ui.setRounds(this.wins);
    this.ui.setTimer(ROUND_TIME);
  }

  /* Called when leaving the fight screen (BACK to menu, etc.) */
  leaveFight() {
    this.resetFightState();
  }

  _startRound() {
    this.timer = ROUND_TIME;
    this.p1.hp = this.p1.maxHp; this.p2.hp = this.p2.maxHp;
    this.p1.meter = this.p2.meter = 0;
    const spawns = getStage(this._stageId || 'shrine').spawns;
    this.p1.root.position.set(spawns.p1, 0, 0); this.p2.root.position.set(spawns.p2, 0, 0);
    // FACING FIX (owner playtest 2026-10-22): the old 0/π values posed the
    // fighters toward/away from the CAMERA, contradicting fighter.js's
    // facing*π/2 convention (face the opponent). Snap both to the convention,
    // visual angle included so no turn tween plays at round start.
    this.p1.facing = 1; this.p1._faceY = Math.PI / 2; this.p1.lean.rotation.y = Math.PI / 2;
    this.p2.facing = -1; this.p2._faceY = -Math.PI / 2; this.p2.lean.rotation.y = -Math.PI / 2;
    this.p1.state = 'idle'; this.p2.state = 'idle';
    // Round reset is also a clean break from any in-progress attack: never let
    // a latched attackName (e.g. 'surge') stick the Soul Surge aura on.
    this.p1.attack = null; this.p1.attackName = null;
    this.p2.attack = null; this.p2.attackName = null;
    this.p1.dead = this.p2.dead = false;
    this.p1.stun = this.p2.stun = 0;
    this.p1.vx = this.p2.vx = 0;
    this.input.enable(false);

    this.roundState = 'intro';
    this._roundLockT = 1.6;
    this.ui.banner(`ROUND ${this.round}`);
    this.ui.updateHP(this.p1, this.p2);
    this.ui.updateMeter(this.p1, this.p2);
    setTimeout(() => {
      if (this.roundState !== 'intro') return;
      this.ui.banner('FIGHT!');
      audio.bell();
      this.roundState = 'fight';
      this.input.enable(true);
    }, 1100);
  }

  pause(on) { this.paused = on; }

  /* ---------------- Main loop (fixed update + render) ---------------- */
  _loop(now) {
    requestAnimationFrame(this._loop);
    if (!this._last) this._last = now;
    let frameDt = Math.min(0.05, (now - this._last) / 1000);
    this._last = now;

    if (this.running && !this.paused) {
      if (this._hitStop > 0) {
        this._hitStop -= frameDt;
      } else {
        this._acc += frameDt;
        while (this._acc >= FIXED_DT) {
          this._update(FIXED_DT);
          this._acc -= FIXED_DT;
        }
      }
    }

    // Tekken hitstop freezes EVERYTHING (hitfx 2026-10-22): the effect stack
    // gets dt=0 while the sim is frozen, so the spark holds then bursts.
    this.hitfx.update(this._hitStop > 0 ? 0 : frameDt);
    this.arena.update(frameDt, this.p1, this.p2);
    this.arena.render();
  }

  _update(dt) {
    if (this.roundState === 'intro') {
      this._roundLockT -= dt;
      this.p1.update(dt, this.p2);
      this.p2.update(dt, this.p1);
      return;
    }

    if (this.roundState === 'fight') {
      this.timer -= dt;
      if (this.timer <= 0) { this.timer = 0; this._timeOut(); }
      this.ui.setTimer(Math.ceil(this.timer));

      // --- Player input -> intents ---
      if (this.ai1) {
        const p1SurgeBefore = this.p1.attackName === 'surge' && this.p1.state === 'attack';
        this.ai1.update(dt, this.p2);
        if (!p1SurgeBefore && this.p1.attackName === 'surge' && this.p1.state === 'attack') {
          this.surgePresentation(this.p1);
        }
      } else {
        const inp = this.input;
        const ms = this.matchStats; // story reincarnation profiling
        const rec = (k) => { if (ms && ms.attacks[k] !== undefined) ms.attacks[k]++; };
        const stick = this._tekkenDir(inp, this.p1.facing);
        this.p1.setStick(stick); // guard + posture (decoded T3 rules, fighter.js _guardBits)
        this.p1.tryMove(inp.axisX);
        if (inp.up) this.p1.tryJump();
        this.p1.tryBlock(inp.held.block);
        this.p1.tryCrouch(inp.down && !inp.up); // hold down = crouch; release = WS. window
        // Feed facing-relative direction into the Tekken input buffer
        // (drives motion specials qcf/f,F and directional attacks f+1)
        this.p1.tekken.noteDirection(stick);
        if (ms && this.p1.isBlocking()) ms.blockTime += dt;
        if (ms) ms.time += dt;
        // Stream 6: while caught in a throw, limb inputs are break attempts.
        if (this.p1.state === 'thrown') {
          for (const act of inp.consume()) {
            if (act === '1' || act === '2' || act === '3' || act === '4' ||
                act === '1+2' || act === '3+4') {
              if (this.p1.tryThrowBreak(act)) {
                this.ui.throwEscape(true);
                audio.block();
              }
            }
          }
        } else for (const act of inp.consume()) {
          if (act === 'punch' || act === 'kick' || act === 'grab' ||
              act === '1' || act === '2' || act === '3' || act === '4' ||
              act === '1+3' || act === '2+4' || act === '1+2' || act === '3+4' ||
              act === '1+4' || act === '2+3') {
            if (this.p1.tryAttack(act)) { audio.whiff(); rec(act); }
          }
          else if (act === 'ss-up') { if (this.p1.trySidestep(-1)) rec('sidestep'); }
          else if (act === 'ss-down') { if (this.p1.trySidestep(1)) rec('sidestep'); }
          else if (act === 'surge') {
            if (this.p1.tryAttack('surge')) {
              rec('surge');
              audio.soulSurge(this.p1.char.id);
              this.ui.surgeFlash(this.p1.char.surge?.color ?? this.p1.char.colors.trim, this.p1.char.surge?.accent ?? 0xffffff);
              this.ui.surgeName(this.p1.char.surge?.name ?? 'SOUL SURGE');
            }
          }
          else if (act === 'dodge') { if (this.p1.tryDodge()) rec('dodge'); }
          else if (act === 'transform') {
            if (this.p1.tryTransform('up')) { audio.soulSurge(this.p1.char.id); rec('transform'); }
          }
          else if (act === 'transform-down') {
            if (this.p1.tryTransform('down')) { audio.soulSurge(this.p1.char.id); rec('transform-down'); }
          }
        }
      }

      // --- AI ---
      const p2SurgeBefore = this.p2.attackName === 'surge' && this.p2.state === 'attack';
      this.ai.update(dt, this.p1);
      if (!p2SurgeBefore && this.p2.attackName === 'surge' && this.p2.state === 'attack') {
        this.surgePresentation(this.p2);
      }

      // --- Advance fighters ---
      this.p1.update(dt, this.p2);
      this.p2.update(dt, this.p1);

      // --- Stream 6: throw-lock resolution (break window expired) ---
      for (const atk of [this.p1, this.p2]) {
        if (atk.state === 'throwing' && atk.lockT <= 0 && atk.lockMove) {
          const def = atk === this.p1 ? this.p2 : this.p1;
          const hpBefore = def.hp;
          const result = atk.completeThrow();
          const dealt = Math.max(0, hpBefore - def.hp);
          if (this.matchStats) {
            if (atk === this.p1) this.matchStats.dmgDealt += dealt;
            else this.matchStats.dmgTaken += dealt;
          }
          this.ui.throwBreakPrompt(false);
          if (result === 'ko') {
            audio.ko(); audio.grunt(def.isPlayer ? 1.1 : 0.85);
            this.arena.shake(0.6 * this.feel.shake, 0.45 * this.feel.shake);
            this._hitStop = 0.18 * this.feel.hitstop;
            this.hitfx.spawn('ko', def.root.position.x, 1.2, def.root.position.z,
              { dirX: Math.sign(def.root.position.x - atk.root.position.x) || 1 });
          } else if (result && result !== 'dodge') {
            audio.grab(); audio.grunt(def.isPlayer ? 1.05 : 0.9);
            this.arena.shake(0.45 * this.feel.shake, 0.28 * this.feel.shake);
            this._hitStop = 0.1 * this.feel.hitstop;
            this.hitfx.spawn('grab', def.root.position.x, 1.2, def.root.position.z,
              { color: atk.char.colors.trim || 0xffffff, scale: 1.2,
                dirX: Math.sign(def.root.position.x - atk.root.position.x) || 1 });
            const combo = atk.registerCombo();
            this.ui.combo(Math.max(1, combo));
          }
        }
      }

      // --- Combat resolution ---
      this._resolveCombat(this.p1, this.p2);
      this._resolveCombat(this.p2, this.p1);

      // --- HUD ---
      this.ui.updateHP(this.p1, this.p2);
      this.ui.updateMeter(this.p1, this.p2);

      // --- Win check ---
      if (this.p1.hp <= 0 || this.p2.hp <= 0) this._endRound();
    } else if (this.roundState === 'over') {
      this._roundLockT -= dt;
      this.p1.update(dt, this.p2);
      this.p2.update(dt, this.p1);
      if (this._roundLockT <= 0) this._afterRound();
    }
  }

  /* Facing-relative Tekken direction from input state: f/b/u/d + diagonals. */
  _tekkenDir(inp, facing) {
    const fwd = (inp.axisX || 0) * facing; // forward-positive
    const f = fwd > 0.25, b = fwd < -0.25;
    const v = inp.vertNow ? inp.vertNow() : (inp.up ? 'up' : inp.down ? 'down' : null);
    const up = v === 'up', down = v === 'down';
    if (up && f) return 'u/f';
    if (up && b) return 'u/b';
    if (up) return 'u';
    if (down && f) return 'd/f';
    if (down && b) return 'd/b';
    if (down) return 'd';
    if (f) return 'f';
    if (b) return 'b';
    return 'n';
  }

  /* Test attacker's active hitbox against defender's hurtboxes */
  _resolveCombat(attacker, defender) {
    const hb = attacker.getHitbox();
    if (!hb) return;
    const hurts = defender.getHurtboxes();
    for (const hu of hurts) {
      const dx = hb.x - hu.x, dy = hb.y - hu.y, dz = hb.z - hu.z;
      const rr = (hb.r + hu.r);
      if (dx * dx + dy * dy + dz * dz <= rr * rr) {
        // Decoded T3 posture rule: highs pass over crouchers, lows under jumpers,
        // standing throws whiff crouching fighters (fighter.js canBeHitBy).
        if (!defender.canBeHitBy(hb.move)) return;
        attacker.registerHit();
        // Stream 6: throws enter the breakable throw-lock instead of
        // landing instantly. Throws whiff against airborne opponents.
        if (hb.move.isGrab && defender.onGround && defender.state !== 'thrown' &&
            defender.state !== 'throwing') {
          defender.startThrowLock(hb.move, attacker);
          attacker.startThrowing(defender);
          this.ui.throwBreakPrompt(defender.isPlayer, hb.move.throw_break || '1');
          audio.grab();
          this.arena.shake(0.3 * this.feel.shake, 0.2 * this.feel.shake);
          this._hitStop = 0.06 * this.feel.hitstop;
          return;
        }
        const hpBefore = defender.hp;
        const result = defender.receiveHit(hb.move, attacker);
        // story reincarnation profiling: who dealt / took what
        const dealt = Math.max(0, hpBefore - defender.hp);
        if (this.matchStats) {
          if (attacker === this.p1) this.matchStats.dmgDealt += dealt;
          else if (defender === this.p1) this.matchStats.dmgTaken += dealt;
        }

        if (result === 'block') {
          audio.block();
          // Tekken block presentation: pale-blue spark, short freeze, small thump.
          this._hitStop = 0.05 * this.feel.hitstop;
          this.arena.shake(0.08 * this.feel.shake, 0.12);
          this.hitfx.spawn('block', hb.x, hb.y, hb.z, { dirX: Math.sign(defender.root.position.x - attacker.root.position.x) || 1 });
          attacker.combo = 0;
        } else if (result === 'dodge') {
          // whiffed into i-frames, nothing
        } else if (result === 'ko') {
          audio.ko(); audio.grunt(defender.isPlayer ? 1.1 : 0.85);
          this.arena.shake(0.6 * this.feel.shake, 0.45 * this.feel.shake);
          this._hitStop = 0.18 * this.feel.hitstop;
          this.hitfx.spawn('ko', hb.x, hb.y, hb.z, { dirX: Math.sign(defender.root.position.x - attacker.root.position.x) || 1 });
        } else {
          const isGrab = !!hb.move.isGrab;
          const isHeavy = hb.move.knock >= 4;
          const isCounter = result === 'counter';
          const isSurge = attacker.attackName === 'surge';
          if (attacker.attackName === 'kick') audio.kick();
          else if (attacker.attackName === 'grab') audio.grab();
          else if (isSurge) { /* surge sound played on startup */ }
          else audio.punch();
          audio.grunt(defender.isPlayer ? 1.05 : 0.9);
          // Tekken-tiered hitstop + shake: light < heavy < counter.
          this.arena.shake(
            (isCounter ? 0.5 : isGrab ? 0.45 : isHeavy ? 0.4 : 0.22) * this.feel.shake,
            (isCounter ? 0.3 : isGrab ? 0.28 : 0.2) * this.feel.shake);
          this._hitStop = (isCounter ? 0.14 : isGrab ? 0.1 : isHeavy ? 0.11 : 0.08) * this.feel.hitstop;
          // Tekken hit-condition presentation (hitfx.js): gold spark on hit,
          // red-orange on counter, ring on heavies, character surge color kept.
          const fxType = isSurge ? 'surge' : isCounter ? 'counter' : isGrab ? 'grab' : isHeavy ? 'heavy' : 'hit';
          const fxColor = isSurge
            ? (attacker.char.surge?.color ?? attacker.char.colors.trim ?? 0xffffff)
            : undefined;
          this.hitfx.spawn(fxType, hb.x, hb.y, hb.z, {
            color: fxColor,
            scale: isGrab ? 1.2 : isHeavy ? 1.1 : 0.9,
            dirX: Math.sign(defender.root.position.x - attacker.root.position.x) || 1,
          });

          const combo = attacker.registerCombo();
          // HITS counter: show on EVERY landed hit, not just 2+ combos.
          // Single hits show "1 HITS" briefly; combos accumulate.
          this.ui.combo(Math.max(1, combo));
        }
        return; // one hit per swing
      }
    }
  }

  /* Legacy shim (hitfx 2026-10-22): the prototype sphere-burst is gone;
     all impact presentation now goes through the Tekken hit-effect stack
     (js/hitfx.js). Kept so any lane still calling _spawnImpact keeps working. */
  _spawnImpact(x, y, z, color, scale) {
    this.hitfx.spawn('hit', x, y, z, { color, scale: scale || 1 });
  }

  /* AI-driven Soul Surge presentation (same as the player's) */
  surgePresentation(fighter) {
    audio.soulSurge(fighter.char.id);
    this.ui.surgeFlash(fighter.char.surge?.color ?? fighter.char.colors.trim, fighter.char.surge?.accent ?? 0xffffff);
    this.ui.surgeName(fighter.char.surge?.name ?? 'SOUL SURGE');
  }

  /* ---------------- Round flow ---------------- */
  _timeOut() {
    if (this.p1.hp > this.p2.hp) this.p2.hp = 0;
    else if (this.p2.hp > this.p1.hp) this.p1.hp = 0;
    else { this.p1.hp = this.p2.hp = 0; }
    this._endRound();
  }

  _endRound() {
    if (this.roundState !== 'fight') return;
    this.roundState = 'over';
    this._roundLockT = 3.0;
    this.input.enable(false);

    // VOICE (2026-10-22): the winner's win-pose voice line. Fire-and-forget —
    // never blocks the 3 s win beat; subtitle-only until recordings land.
    const p1Down = this.p1.hp <= 0, p2Down = this.p2.hp <= 0;
    if (p1Down && !p2Down) { this.wins.p2++; this.p1._knockout(-1); this.p2.victory(); this.ui.banner('K.O.'); voice.play(this.p2.char.id, 'win'); }
    else if (p2Down && !p1Down) { this.wins.p1++; this.p2._knockout(1); this.p1.victory(); this.ui.banner('K.O.'); voice.play(this.p1.char.id, 'win'); }
    else { this.wins.p1++; this.wins.p2++; this.ui.banner('DOUBLE K.O.'); }

    this.ui.setRounds(this.wins);
    this.ui.updateHP(this.p1, this.p2);
  }

  _afterRound() {
    if (this.training) {
      // TRAINING (modes lane): endless round vs the passive dummy.
      // The round resets instead of the match ending; the dummy is restored.
      this.wins = { p1: 0, p2: 0 };
      this.ui.setRounds(this.wins);
      this.round = 1;
      this.ui.banner('RESET — DUMMY RESTORED');
      this._startRound();
      return;
    }
    if (this.wins.p1 >= (this.roundsToWin || ROUNDS_TO_WIN) ||
        this.wins.p2 >= (this.roundsToWin || ROUNDS_TO_WIN)) {
      this.running = false;
      const playerWon = this.wins.p1 > this.wins.p2;
      // modes lane: a mode controller consumes the match result
      // (arcade ladder, story reincarnation, ...). Null = classic.
      if (this.onMatchEnd) this.onMatchEnd(playerWon);
      else this.ui.matchOver(playerWon);
    } else {
      this.round++;
      this._startRound();
    }
  }
}
