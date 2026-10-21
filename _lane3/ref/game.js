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
import { Fighter } from './fighter.js';
import { AIController } from './ai.js';
import { audio } from './audio.js';

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

    this._loop = this._loop.bind(this);
    requestAnimationFrame(this._loop);
  }

  /* ---------------- Match setup ----------------
     CLEAN-INIT: every match starts from a known-clean state. No leftover
     fighters, no running timers, no half-loaded assets, no leaked state
     from the previous match. This is the "starts clean" standard. */
  startMatch(playerChar, enemyChar) {
    this.resetFightState();

    this.p1 = new Fighter(playerChar, -3.5, 1, true);
    this.p2 = new Fighter(enemyChar, 3.5, -1, false);
    this.arena.scene.add(this.p1.root, this.p2.root);
    this.ai = new AIController(this.p2, enemyChar.ai);
    this.ai1 = this.demo ? new AIController(this.p1, playerChar.ai) : null;

    this.wins = { p1: 0, p2: 0 };
    this.round = 1;
    this.ui.setNames(playerChar.name, enemyChar.name);
    this.ui.setRounds(this.wins);
    this.running = true;
    this.paused = false;
    this._startRound();
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
    this.p1.root.position.set(-3.5, 0, 0); this.p2.root.position.set(3.5, 0, 0);
    this.p1.facing = 1; this.p1.lean.rotation.y = 0;
    this.p2.facing = -1; this.p2.lean.rotation.y = Math.PI;
    this.p1.state = 'idle'; this.p2.state = 'idle';
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
        this.p1.tryMove(inp.axisX);
        if (inp.up) this.p1.tryJump();
        this.p1.tryBlock(inp.held.block);
        // Feed facing-relative direction into the Tekken input buffer
        // (drives motion specials qcf/f,F and directional attacks f+1)
        this.p1.tekken.noteDirection(this._tekkenDir(inp, this.p1.facing));
        for (const act of inp.consume()) {
          if (act === 'punch' || act === 'kick' || act === 'grab' ||
              act === '1' || act === '2' || act === '3' || act === '4' ||
              act === '1+3' || act === '2+4' || act === '1+2' || act === '3+4') {
            if (this.p1.tryAttack(act)) audio.whiff();
          }
          else if (act === 'surge') {
            if (this.p1.tryAttack('surge')) {
              audio.soulSurge(this.p1.char.id);
              this.ui.surgeFlash(this.p1.char.surge.color, this.p1.char.surge.accent);
              this.ui.surgeName(this.p1.char.surge.name);
            }
          }
          else if (act === 'dodge') this.p1.tryDodge();
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
    if (inp.up && f) return 'u/f';
    if (inp.up && b) return 'u/b';
    if (inp.up) return 'u';
    if (inp.down && f) return 'd/f';
    if (inp.down && b) return 'd/b';
    if (inp.down) return 'd';
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
        attacker.registerHit();
        const result = defender.receiveHit(hb.move, attacker);

        if (result === 'block') {
          audio.block();
          this._hitStop = 0.04;
          attacker.combo = 0;
        } else if (result === 'dodge') {
          // whiffed into i-frames, nothing
        } else if (result === 'ko') {
          audio.ko(); audio.grunt(defender.isPlayer ? 1.1 : 0.85);
          this.arena.shake(0.5, 0.4);
          this._hitStop = 0.12;
          this._spawnImpact(hb.x, hb.y, hb.z, 0xffcf4d, 1.4);
        } else {
          const isGrab = !!hb.move.isGrab;
          const isHeavy = hb.move.knock >= 4;
          if (attacker.attackName === 'kick') audio.kick();
          else if (attacker.attackName === 'grab') audio.grab();
          else if (attacker.attackName === 'surge') { /* surge sound played on startup */ }
          else audio.punch();
          audio.grunt(defender.isPlayer ? 1.05 : 0.9);
          this.arena.shake(isGrab ? 0.45 : isHeavy ? 0.35 : 0.18, isGrab ? 0.28 : 0.18);
          this._hitStop = isGrab ? 0.1 : isHeavy ? 0.08 : 0.05;
          const col = attacker.attackName === 'surge'
            ? attacker.char.surge.color
            : (attacker.char.colors.trim || 0xffffff);
          this._spawnImpact(hb.x, hb.y, hb.z, col, isGrab ? 1.3 : isHeavy ? 1 : 0.6);

          const combo = attacker.registerCombo();
          // HITS counter: show on EVERY landed hit, not just 2+ combos.
          // Single hits show "1 HITS" briefly; combos accumulate.
          this.ui.combo(Math.max(1, combo));
        }
        return; // one hit per swing
      }
    }
  }

  /* Cheap particle burst at impact point */
  _spawnImpact(x, y, z, color, scale) {
    const geo = new THREE.SphereGeometry(0.18, 8, 8);
    const mat = new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 1 });
    const group = new THREE.Group();
    const parts = [];
    for (let i = 0; i < 8; i++) {
      const m = new THREE.Mesh(geo, mat.clone());
      const a = (i / 8) * Math.PI * 2;
      m.userData.v = new THREE.Vector3(Math.cos(a) * 4, Math.sin(a) * 4 + 1, (Math.random() - 0.5) * 2);
      group.add(m); parts.push(m);
    }
    const flash = new THREE.Mesh(new THREE.SphereGeometry(0.5 * scale, 12, 12),
      new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.9 }));
    group.add(flash);
    group.position.set(x, y, z);
    group.scale.setScalar(scale);
    this.arena.scene.add(group);

    let life = 0.35;
    const tick = () => {
      life -= 0.016;
      const f = Math.max(0, life / 0.35);
      flash.scale.setScalar(1 + (1 - f) * 2);
      flash.material.opacity = f * 0.9;
      for (const p of parts) {
        p.position.addScaledVector(p.userData.v, 0.016);
        p.material.opacity = f;
        p.scale.setScalar(f);
      }
      if (life > 0) requestAnimationFrame(tick);
      else this.arena.scene.remove(group);
    };
    requestAnimationFrame(tick);
  }

  /* AI-driven Soul Surge presentation (same as the player's) */
  surgePresentation(fighter) {
    audio.soulSurge(fighter.char.id);
    this.ui.surgeFlash(fighter.char.surge.color, fighter.char.surge.accent);
    this.ui.surgeName(fighter.char.surge.name);
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

    const p1Down = this.p1.hp <= 0, p2Down = this.p2.hp <= 0;
    if (p1Down && !p2Down) { this.wins.p2++; this.p1._knockout(-1); this.p2.victory(); this.ui.banner('K.O.'); }
    else if (p2Down && !p1Down) { this.wins.p1++; this.p2._knockout(1); this.p1.victory(); this.ui.banner('K.O.'); }
    else { this.wins.p1++; this.wins.p2++; this.ui.banner('DOUBLE K.O.'); }

    this.ui.setRounds(this.wins);
    this.ui.updateHP(this.p1, this.p2);
  }

  _afterRound() {
    if (this.wins.p1 >= ROUNDS_TO_WIN || this.wins.p2 >= ROUNDS_TO_WIN) {
      this.running = false;
      const playerWon = this.wins.p1 > this.wins.p2;
      this.ui.matchOver(playerWon);
    } else {
      this.round++;
      this._startRound();
    }
  }
}
