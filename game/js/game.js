/* ============================================================
   WESTERN HEART — Game (match arbiter & main loop)
   • Owns the two fighters, the Shrine arena, input & AI.
   • Resolves hitbox/hurtbox collisions every fixed step.
   • Manages rounds (best of 3), 60s timer, win conditions, HUD.
   • Fixed-timestep update (120 Hz), decoupled render (60fps).

   Demo mode: open with ?demo=1 and P1 is also CPU-driven —
   good for watching AI-vs-AI or unattended verification.
   ============================================================ */
import { inReach, moveReach } from './combat-core.js';
import { testSweptHit } from './hitbox.js';
import * as THREE from 'three';
import { Arena } from './scene.js';
// LOADSPEED (2026-10-22): fighter.js (rigs, T3 wiring, movesets) is fight-only —
// it streams via lazy.js on first startMatch, not at boot. See js/lazy.js.
import { lazy } from './lazy.js';
import { AIController } from './ai.js';
import { personalityForChar } from './ai/cpu-personality.js'; // WIRING-MAP: CPU personality layer
import { trySpirit } from './spirit-actions.js'; // WIRING-MAP: 魂 ACTION
import { SoulSystems, loadVariants } from './soul-systems.js'; // SOUL-SYSTEMS.md
// FIGHT LAB · GUNGAKU (軍楽): loaded on demand so the boot path stays lean.
let _GungakuAI = null;
async function gungakuAI() {
  if (!_GungakuAI) ({ GungakuAI: _GungakuAI } = await import('./fightlab-gungaku.js'));
  return _GungakuAI;
}
import { audio } from './audio.js';
import { music } from './music.js';
import { getStage } from './stages.js';
import { applyFighterProfile } from './customization-consumer.js';
/* Stage mechanics + rage/comeback lane (Tekken/DOA teardowns).
   LAZY-SAFE: none of these modules statically import fighter.js or
   movesets.js (those stream via lazy.js) — the directors receive them
   by injection in startMatch. */
import { StageBreaks } from './stagebreaks.js';
import { RageSystem, ensureRageMoves, RAGE_SLOWMO_SCALE } from './rage.js';
/* Soul Urge lane (Tekken 8 Heat, proprietary rename — user-locked 2026-10-22). */
import { SoulUrge, ensureUrgeMoves, URGE_BURST_TIME, URGE_ENGAGER_TIME } from './soulurge.js';
/* X-ray lane (Purdue anatomy × cinematic KO blows, 2026-10-23):
   rendering-only overlay (no anim clips), hooked into rage-art /
   urge-smash KOs. */
import { XraySystem } from './xray.js';
import { V, vskillDispatch, vshiftTap } from './v-system.js';
// HITFX (2026-10-22, #616): Tekken hit-effect stack — spark + debris +
// ring + screen flash, dt-driven so hitstop freezes it like Tekken.
// Restored 2026-10-22 (worker 54): the file + wiring were lost to a
// stale-base clobber; this is the #616 wiring, re-applied surgically.
import { HitFX } from './hitfx.js';
// LIGHTING RIG (worker 27): per-fighter character light rig — SFV/T7-style
// character-vs-stage lighting separation + bible soul glow. Fail-silent.
import { attachCharacterRig } from './lighting-rig.js';
import { getRules } from './rules.js';

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
    this._slowMo = 0; // V-System: V-Shift slow-mo timer (real seconds)
    // Tekken hit-effect stack (hitfx.js): spark + debris + ring + flash,
    // dt-driven so hitstop freezes the whole stack like Tekken.
    this.hitfx = new HitFX(this.arena.scene);
    this._p1BlockWas = false; // V-System: block double-tap (V-Shift) edge tracking
    this._p1BlockUpT = null;

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

    /* Stage-break + rage directors (created once, rebound per match). */
    this.stageBreaks = null;
    this.rage = null;
    /* Soul Urge director (T8 Heat). */
    this.soulurge = null;
    /* Injected module APIs (from lazy.js, set in startMatch). */
    this._stageFx = null;
    this._msApi = null;

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
    // LOADSPEED: warmed during menu idle; usually cached by fight time.
    const { Fighter, setArenaLimit, setGroundY } = await lazy.fighter();
    // Modes lane: per-match round target (default = classic best-of-3).
    this.roundsToWin = opts.roundsToWin || ROUNDS_TO_WIN;
    // Versus SETUP / GAME OPTION: per-match round time (0 = INFINITY)
    // and guard damage. Defaults come from the rules store when the
    // mode doesn't dictate them.
    const _rules = getRules();
    this.roundTime = opts.roundTime != null ? opts.roundTime : _rules.roundTime;
    this.guardDamage = opts.guardDamage != null ? opts.guardDamage : _rules.guardDamage;

    // Lane 4: stage selection drives arena, collision bounds, spawns.
    const stage = getStage(stageId || 'shrine');
    setArenaLimit(stage.dims.wallDistance); this._arenaLimit = stage.dims.wallDistance;
    this._stageId = stage.id;
    this._stageName = stage.name;

    // Stage-break + rage/soul-urge lanes: bind breakables to this stage,
    // synthesize each fighter's rage art/drive + urge burst/smash from
    // their real data. Modules come via lazy.js (loadspeed-safe).
    const msApi = await lazy.movesets();
    this._msApi = { playedMoveset: msApi.playedMoveset, getFighterMoveset: msApi.getFighterMoveset };
    this._stageFx = { setArenaLimit, setGroundY };
    if (!this.stageBreaks) this.stageBreaks = new StageBreaks(this);
    if (!this.rage) this.rage = new RageSystem(this);
    if (!this.soulurge) this.soulurge = new SoulUrge(this);
    if (!this.xray) this.xray = new XraySystem(this, THREE);
    this.stageBreaks.bindStage(stage, this._stageFx);
    ensureRageMoves(playerChar.id, this._msApi);
    ensureRageMoves(enemyChar.id, this._msApi);
    ensureUrgeMoves(playerChar.id, this._msApi);
    ensureUrgeMoves(enemyChar.id, this._msApi);

    this.p1 = new Fighter(playerChar, stage.spawns.p1, 1, true);
    this.p2 = new Fighter(enemyChar, stage.spawns.p2, -1, false);
    // Hit-feel tuning: fighters read live multipliers off game.feel
    // (review-stage tuner). Null-safe when no game is attached.
    this.p1.game = this;
    this.p2.game = this;
    // X-ray lane: prefetch both fighters' anatomy layers in the
    // background so a cinematic KO can reveal them with no mid-sequence fetch.
    if (this.xray) { this.xray.prefetch(playerChar.id); this.xray.prefetch(enemyChar.id); }
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
    // LIGHTING RIG (worker 27): attach each fighter's character light rig —
    // their own key light (follows them) + soul-glow baseline on the
    // existing auraLight + soul-tinted emissive (bible: fighters are
    // luminous sources). No-op-safe; never blocks a match.
    attachCharacterRig(this.p1, stage);
    attachCharacterRig(this.p2, stage);
    // FIGHT LAB · GUNGAKU (軍楽): the programmable dummy replaces the
    // passive AI when the mode requests it (enemyChar.ai.gungaku).
    if (enemyChar.ai && enemyChar.ai.gungaku) {
      const GAI = await gungakuAI();
      this.ai = new GAI(this.p2, enemyChar.ai);
    } else {
      this.ai = new AIController(this.p2, personalityForChar(enemyChar));
    }
    this.soul = new SoulSystems(this); loadVariants(); // SOUL-SYSTEMS.md
    this.ai1 = this.demo ? new AIController(this.p1, personalityForChar(playerChar)) : null;

    this.wins = { p1: 0, p2: 0 };
    this.round = 1;
    this.ui.setNames(playerChar.name, enemyChar.name);
    if (this.ui.setStageName) this.ui.setStageName(stage.name);
    this.ui.setRounds(this.wins, this.roundsToWin);
    this.matchStats = { attacks: { punch: 0, kick: 0, grab: 0, surge: 0, dodge: 0 }, blockTime: 0, time: 0, dmgDealt: 0, dmgTaken: 0 };
    this.running = true;
    this.paused = false;
    // Stage content streams in (Tekken retro OBJs fetch async); the fight
    // intro runs on the base arena while the shell loads.
    this.arena.setStage(stage.id);
    // FIGHTER DEPTH (2026-10-22, worker 34): ki charge, tag relay, cloth/hair,
    // combo trials, ghost AI, replay analysis, stage intros/variants, versus
    // banter, movelist UI, special style, punishment training. Dynamic import
    // so the menu boot path stays lean; every system feature-flagged in
    // WH_DEPTH_FLAGS and fail-silent here.
    try {
      const { FighterDepth } = await import('./fighter-depth.js');
      this._whDepth = FighterDepth;
      FighterDepth.onMatchStart(this, { stageDef: stage, variantId: opts.variantId, skipIntro: opts.skipIntro });
    } catch (e) { console.warn('[WH] fighter-depth wire failed:', e?.message || e); }
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
    this.timer = this.roundTime === 0 ? Infinity : (this.roundTime || ROUND_TIME);
    this.roundState = 'idle';
    this._roundLockT = 0;
    this._hitStop = 0;
    this._slowMo = 0; // V-System reset
    this._p1BlockWas = false; this._p1BlockUpT = null;
    this._acc = 0;
    this.running = false;
    this.paused = true;
    // Reset input (no stuck keys/buttons from previous match)
    if (this.input) this.input.reset();
    // Reset HUD
    this.ui.setRounds(this.wins, this.roundsToWin);
    this.ui.setTimer(this.roundTime === 0 ? '∞' : (this.roundTime || ROUND_TIME));
    // Stage-break lane: restore bounds/ground when leaving or restarting.
    if (this.stageBreaks) this.stageBreaks.reset();
    if (this.rage) this.rage.resetRound();
    if (this.soulurge) this.soulurge.resetRound();
    if (this.xray) this.xray.cancel();
  }

  /* Called when leaving the fight screen (BACK to menu, etc.) */
  leaveFight() {
    this.resetFightState();
  }

  _startRound() {
    this.timer = this.roundTime === 0 ? Infinity : (this.roundTime || ROUND_TIME);
    this.p1.hp = this.p1.maxHp; this.p2.hp = this.p2.maxHp;
    // COMBAT-SYSTEMS 2026-10-24: fresh round = empty recoverable pool,
    // free spin slot, no lingering wall splat.
    this.p1._recoverable = this.p2._recoverable = 0;
    this.p1._spinUsed = this.p2._spinUsed = false;
    this.p1._wallSplat = this.p2._wallSplat = false;
    this.p1.meter = this.p2.meter = 0;
    if (this.rage) this.rage.resetRound();
    if (this.soulurge) this.soulurge.resetRound();
    if (this.xray) this.xray.cancel();
    if (this.stageBreaks) this.stageBreaks.syncRound();
    const spawns = getStage(this._stageId || 'shrine').spawns;
    const gy = this.stageBreaks ? this.stageBreaks.groundY : 0;
    this.p1.root.position.set(spawns.p1, gy, 0); this.p2.root.position.set(spawns.p2, gy, 0);
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
    // MUSIC (2026-10-24): round-start intensity reset (Tekken rule) +
    // T7 match-point variant: when either fighter is one round from
    // winning, the deciding round opens on the Final Round variant track.
    // (Best-of-3, so round 1 can never be match-point except a 1-round match.)
    const _rtw = this.roundsToWin || ROUNDS_TO_WIN;
    this._musicFinal = this.wins.p1 >= _rtw - 1 || this.wins.p2 >= _rtw - 1;
    this._musicLowHp = false;
    music.setIntensity(0.55);
    if (this._musicFinal) music.playFinalRound();
    this._roundLockT = 1.6;
    this.ui.banner(`ROUND ${this.round}`);
    this.ui.updateHP(this.p1, this.p2);
    this.ui.updateMeter(this.p1, this.p2);
    setTimeout(() => {
      if (this.roundState !== 'intro') return;
      this.ui.banner('FIGHT!');
      music.setIntensity(this._musicFinal ? 0.85 : 0.7);
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
    const realDt = frameDt; // X-ray beat runs on real seconds, not slow-mo scale
    this._last = now;
    if (this.rage) frameDt = this.rage.slowMoScale(frameDt);

    if (this.running && !this.paused) {
      if (this._hitStop > 0) {
        this._hitStop -= frameDt;
      } else {
        // V-System: V-Shift slow-mo dilates the sim (arena/camera stay live).
        if (this._slowMo > 0) this._slowMo -= frameDt;
        this._acc += frameDt * (this._slowMo > 0 ? V.SLOWMO_SCALE : 1);
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
    // X-ray: camera + anatomy-layer overlay, AFTER the fight camera so the
    // zoom wins for this frame. Rendering only — no animation clips.
    if (this.xray) this.xray.update(realDt);
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
        // V-System: V-Shift on block double-tap (neutral only — the tap
        // edge while already blocking just keeps blocking).
        const blockNow = !!inp.held.block;
        if (blockNow && !this._p1BlockWas &&
            vshiftTap(this._p1BlockUpT, performance.now()) && this.p1.tryVShift()) {
          this.ui.vShift(); audio.whiff(); rec('vshift');
        }
        if (!blockNow && this._p1BlockWas) this._p1BlockUpT = performance.now();
        this._p1BlockWas = blockNow;
        this.p1.tryCrouch(inp.down && !inp.up); // hold down = crouch; release = WS. window
        // Feed facing-relative direction into the Tekken input buffer
        // (drives motion specials qcf/f,F and directional attacks f+1).
        // Pass the tick length: the buffer's windows are T3 frames of 1/60 s and it
        // weighs each entry by dt, so they stay real-time at FIXED_DT = 1/120 (or any rate).
        this.p1.tekken.noteDirection(stick, dt);
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
        } else {
          const whQueue = inp.consume();
          // FIGHTER DEPTH (worker 34): soul kindle (ki charge) watches the
          // raw queue for the 1+2+3+4 press.
          // SOUL-SYSTEMS: 九魂解放 at a full meter claims the 1+2+3+4 press before soul kindle.
          if (this.soul && this.soul.claimRelease(this.p1, this.p2, whQueue)) { rec('nine-soul-release'); }
          else if (this._whDepth) this._whDepth.onPlayerQueue(this.p1, whQueue, dt);
          for (const act of whQueue) {
          if (act === 'punch' || act === 'kick' || act === 'grab' ||
              act === '1' || act === '2' || act === '3' || act === '4' ||
              act === '1+3' || act === '2+4' || act === '1+2' || act === '3+4' ||
              act === '1+4' || act === '2+3') {
            // 魂 ACTION: 2+3 while the URGE/HEAT gauge is on + a context trigger.
            if (act === '2+3' && this.p1._urgeOn && this._spiritCheck(this.p1, this.p2)) { rec('spirit'); continue; }
            // SOUL-SYSTEMS: 霊放 Reihou on 1+4 only while the foe is raging.
            if (act === '1+4' && this.soul && this.soul.tryReihou(this.p1, this.p2)) { rec('reihou'); continue; }
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
          else if (act === 'vskill') { this._vskillAction(this.p1, rec); }
          else if (act === 'transform') {
            if (this.p1.tryTransform('up')) { audio.soulSurge(this.p1.char.id); rec('transform'); }
          }
          else if (act === 'transform-down') {
            if (this.p1.tryTransform('down')) { audio.soulSurge(this.p1.char.id); rec('transform-down'); }
          }
          } // end for (const act of whQueue) — fighter-depth wire
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
            // main: rage KO hook (kept; _spawnImpact dropped — it is now a shim
            // over hitfx.spawn and would double-spawn the KO burst above).
            if (this.rage) this.rage.onHitKO(atk, def);
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
      if (this.rage) { this.rage.update(this.p1); this.rage.update(this.p2); }
      // MUSIC (2026-10-24): low-HP intensity lift, edge-triggered so the
      // ramp is not re-scheduled every frame (Tekken final-stretch lift).
      const _lowHp = (this.p1.hp < this.p1.maxHp * 0.25) || (this.p2.hp < this.p2.maxHp * 0.25);
      if (_lowHp && !this._musicLowHp) { this._musicLowHp = true; music.setIntensity(1.0); }
      else if (!_lowHp && this._musicLowHp) { this._musicLowHp = false; music.setIntensity(this._musicFinal ? 0.85 : 0.7); }
      // COMBAT-SYSTEMS 2026-10-24: one Soul Urge tick per frame (the old
      // double call passed a fighter as dt and NaN'd the timer).
      if (this.soulurge) this.soulurge.update(dt);

      // FIGHTER DEPTH (worker 34): per-frame systems — kindle timers,
      // tag relay, stage intro camera.
      if (this._whDepth) this._whDepth.onUpdateFrame(this, dt);

      // --- HUD ---
      this.ui.updateHP(this.p1, this.p2);
      this.ui.updateMeter(this.p1, this.p2);

      // --- Win check ---
      if (this.soul) this.soul.update();
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

  /* V-System: one 'vskill' input, three context moves (Tekken-ified SFV).
     Blockstun + 50 souls -> V-Reversal | full meter -> V-Trigger | else V-Skill. */

  /* WIRING-MAP 魂 ACTION: build context, fire, apply damage. Never alters bodies. */
  _spiritCheck(a, d) {
    if (!a || !d || !a.root || !d.root) return false;
    const dx = d.root.position.x - a.root.position.x, lim = this._arenaLimit || 6;
    const r = trySpirit(a, { urgeOn: !!a._urgeOn, spiritUsed: !!a._spiritUsed, dist: Math.abs(dx),
      foeWall: lim - Math.abs(d.root.position.x), foeDowned: d.state === 'down', foeStun: d.stun || 0 }, this.ui);
    if (!r) return false;
    if (typeof d.receiveHit === 'function') { try { d.receiveHit({ damage: r.damage, level: 'mid', spirit: r.id, name: r.label }, a); } catch (e) {} }
    return true;
  }

  _vskillAction(f, rec) {
    const d = vskillDispatch({ state: f.state, stun: f.stun, meter: f.meter });
    if (d === 'vreversal') {
      if (f.tryVReversal()) { this.ui.vReversal(); audio.block(); rec('vreversal'); }
    } else if (d === 'vtrigger') {
      if (f.tryVTrigger()) {
        this.ui.vTrigger(); audio.soulSurge(f.char.id);
        this.arena.shake(0.35 * this.feel.shake, 0.3 * this.feel.shake);
        this._hitStop = 0.08 * this.feel.hitstop; rec('vtrigger');
      }
    } else if (f.tryVSkill()) { audio.whiff(); rec('vskill'); }
  }

  /* Test attacker's active hitbox against defender's hurtboxes */
  _resolveCombat(attacker, defender) {
    const hb = attacker.getHitbox();
    if (!hb) return;
    // V-System: V-Shift evade — the shifter's i-frames beat an incoming
    // attack inside range -> slow-mo + V-Shift Break window. (Hurtboxes are
    // empty during i-frames, so this check lives outside the loop.)
    if (defender.state === 'vshift' && !defender._vshiftProc &&
        attacker.state === 'attack' &&
        (attacker._attackPhase === 'startup' || attacker._attackPhase === 'active')) {
      const dx = Math.abs(attacker.root.position.x - defender.root.position.x);
      if (dx < V.SHIFT_EVADE_RANGE) {
        defender._vshiftProc = true;
        defender._vbreakT = V.BREAK_WINDOW;
        this._slowMo = V.SLOWMO_DURATION;
        this.ui.vShiftBreak(); audio.whiff();
        this._spawnImpact(defender.root.position.x, 1.4, defender.root.position.z, 0x7df9ff, 1.0);
        return;
      }
    }
    // V-System: V-Skill parry — catches a strike during its window.
    // The attack is cancelled into hitstun; the parrier drinks souls.
    if (defender.state === 'vskill' && defender.attack && defender.attack.kind === 'parry' &&
        defender._vparryT > 0 && !hb.move.isGrab && !hb.move.unblockable) {
      const ddx = hb.x - defender.root.position.x, ddz = hb.z - defender.root.position.z;
      if (ddx * ddx + ddz * ddz < 1.6 * 1.6) {
        attacker._enter('hitstun'); attacker.stun = Math.max(attacker.stun, V.PARRY_STAGGER);
        attacker.vx = 0; attacker.vz = 0;
        defender.addMeter(V.PARRY_SOUL_GAIN);
        defender._vparryT = 0;
        this.ui.vParry(); audio.block();
        this._hitStop = 0.08 * this.feel.hitstop;
        this._spawnImpact(hb.x, hb.y, hb.z, 0x9fd8ff, 0.8);
        return;
      }
    }
    const hurts = defender.getHurtboxes();
    // Contact (HITBOX LANE 2026-10-24): TWO paths, either connects —
    // (1) GEOMETRY: the swept weapon segment (limb segment + travel,
    // hitbox.js) against all 14 hurt capsules. This is the path the
    // old code lacked: it tested one sphere against hurts[0] only.
    // (2) RANGE fallback (tekken-command-interpreter lane): root
    // spacing vs the move's range class, same line. Kept for
    // fighters whose animation does not extend the limb (the
    // documented T-pose case) and for mids against a croucher,
    // whose lowered torso the geometry may only graze. Geometry
    // can only ADD hits the fallback missed, never remove one.
    // The hb.reach / moveReach ratio preserves the advancing-input
    // bonus that getHitbox already folded into hb.reach (moveReach
    // with name '' would otherwise drop it). Posture / hit-level
    // gating still happens in canBeHitBy below, for both paths.
    const geo = testSweptHit(hb, hurts);
    const ap = attacker.root.position, dp = defender.root.position;
    const reachHit = hurts.length > 0 && hb.reach > 0 && (dp.y - ap.y) < 1.6 &&
      inReach(ap.x, ap.z, attacker.facing, dp.x, dp.z, hb.move, '', hb.reach / Math.max(0.01, moveReach(hb.move, '')));
    if (geo.hit || reachHit) {
      const hu = geo.segment || hurts[0];
      attacker._lastHitSegment = hu ? hu.id : null;
      defender._lastHitSegment = hu ? hu.id : null;
      {
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
          if (this.soulurge) this.soulurge.onBlockedHit(attacker, hb.move);
        } else if (result === 'dodge') {
          // whiffed into i-frames, nothing
        } else if (result === 'powercrush') {
          // COMBAT-SYSTEMS 2026-10-24: Power Crush absorbed the hit —
          // damage landed (recoverable, see fighter.js) but the
          // defender's swing continues: no combo increment, no
          // hitstun presentation beyond a block-style spark.
          audio.block();
          this._hitStop = 0.05 * this.feel.hitstop;
          this.hitfx.spawn('block', hb.x, hb.y, hb.z, { dirX: Math.sign(defender.root.position.x - attacker.root.position.x) || 1 });
        } else if (result === 'armor') {
          // V-System: armored V-Skill absorbed it — spark, no damage, no combo.
          audio.block();
          this._hitStop = 0.05 * this.feel.hitstop;
          this._spawnImpact(hb.x, hb.y, hb.z, 0xbfd4ff, 0.7);
        } else if (result === 'ko') {
          audio.ko(); audio.grunt(defender.isPlayer ? 1.1 : 0.85);
          this.arena.shake(0.6 * this.feel.shake, 0.45 * this.feel.shake);
          this._hitStop = 0.18 * this.feel.hitstop;
          this.hitfx.spawn('ko', hb.x, hb.y, hb.z, { dirX: Math.sign(defender.root.position.x - attacker.root.position.x) || 1 });
          // main: rage / xray / stage-break KO hooks (kept; _spawnImpact dropped —
          // it is now a shim over hitfx.spawn and would double-spawn the KO burst).
          if (this.rage) this.rage.onHitKO(attacker, defender);
          // X-ray lane: rage-art / urge-smash KO blows trigger the X-ray beat.
          if (this.xray) this.xray.onHitKO(attacker, defender, hb);
          if (this.stageBreaks) this.stageBreaks.checkHit(attacker, defender, hb.move, result);
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
          if (this.stageBreaks) this.stageBreaks.checkHit(attacker, defender, hb.move, result);
          if (this.soulurge) this.soulurge.onHit(attacker, hb.move);
          if (this.rage && attacker.attackName && attacker.attackName.indexOf('R.') === 0) {
            this.rage.rageArtHit(attacker, hb);
          }
          if (this.soulurge && attacker.attackName === 'US.2+3') {
            this.soulurge.urgeSmashHit(attacker, hb);
          }
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
    music.setIntensity(0.3); // MUSIC: KO / time-up intensity drop (Tekken rule)
    this._roundLockT = 3.0;
    this.input.enable(false);

    const p1Down = this.p1.hp <= 0, p2Down = this.p2.hp <= 0;
    if (p1Down && !p2Down) { this.wins.p2++; this.p1._knockout(-1); this.p2.victory(); this.ui.banner('K.O.'); }
    else if (p2Down && !p1Down) { this.wins.p1++; this.p2._knockout(1); this.p1.victory(); this.ui.banner('K.O.'); }
    else { this.wins.p1++; this.wins.p2++; this.ui.banner('DOUBLE K.O.'); }

    this.ui.setRounds(this.wins, this.roundsToWin);
    this.ui.updateHP(this.p1, this.p2);
    if (this.soul) this.soul.onRoundEnd(p1Down, p2Down); // 試練の封 Trial's Seal
  }

  _afterRound() {
    if (this.training) {
      // TRAINING (modes lane): endless round vs the passive dummy.
      // The round resets instead of the match ending; the dummy is restored.
      this.wins = { p1: 0, p2: 0 };
      this.ui.setRounds(this.wins, this.roundsToWin);
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
