/* ============================================================
   WESTERN HEART — Yuka Combat Brain
   Hierarchical combat state machine for the CPU fighter, built on
   the REAL Yuka.js library (game/vendor/yuka/yuka.module.js — MIT,
   (c) 2023 Yuka authors). No hand-tooled FSM: Yuka's State and
   StateMachine classes drive every transition below.

   Hierarchy:
     CombatBrain (root)
       ├─ region "ground" — Yuka StateMachine
       │    ├─ neutral · attack · block · hit
       └─ region "air" — Yuka StateMachine
            ├─ launch (juggled) · down (knocked down)

   The brain DECIDES (emits a directive { state, move }); the
   AIController in game/js/ai.js EXECUTES (it keeps owning every
   tryAttack/tryBlock/tryMove call). The brain never touches the
   fighter directly — decoupled from the render loop and physics,
   per the combat-sim architecture.

   Snapshot contract (built by AIController._snapshot):
     { dist, dir, myState, foeState, foeAttacking, foeAttackPhase,
       onGround, canAct, stun, meter, launched, downed,
       rageOn, urgeOn, urgePips, urgeReady, inBlockstun,
       aggression, reaction, grabBias, roundOver }
   ============================================================ */
import { State, StateMachine } from '../../vendor/yuka/yuka.module.js';

export const COMBAT_STATES = {
  NEUTRAL: 'neutral',
  ATTACK: 'attack',
  BLOCK: 'block',
  HIT: 'hit',
  LAUNCH: 'launch', // juggled / knocked-down region (air machine)
};

export const COMBAT_REGIONS = { GROUND: 'ground', AIR: 'air' };

/* Range bands in world units (matches AIController's spacing). */
const RANGE = {
  GRAB: 1.9,   // chest-to-chest: throws live here
  POKE: 2.6,   // limb threat range
  FAR: 4.2,    // whiff / approach territory
};

/* ---------------- grounded states ---------------- */

class NeutralState extends State {
  enter() {}
  execute(brain) {
    const s = brain.snap;
    // Outgoing transitions (classic Yuka pattern: checked in execute).
    if (s.myState === 'hit' || s.stun > 0.12) { brain.ground.changeTo('hit'); return; }
    if (s.foeAttacking && s.dist < RANGE.POKE && brain.roll(0.30 + s.reaction * 0.45)) {
      brain.ground.changeTo('block'); return; // predictive guard, not a reaction
    }
    if (s.dist <= RANGE.POKE && brain.roll(0.30 + s.aggression * 0.45)) {
      brain.ground.changeTo('attack'); return;
    }
    // Spacing directive for the controller to walk out.
    brain.directive = {
      state: COMBAT_STATES.NEUTRAL,
      move: s.dist > RANGE.FAR ? 'approach' : (s.dist < 1.1 ? 'create-space' : 'space'),
    };
  }
  exit() {}
}

class AttackState extends State {
  enter() {}
  execute(brain) {
    const s = brain.snap;
    if (s.myState === 'hit' || s.stun > 0.12) { brain.ground.changeTo('hit'); return; }
    if (s.foeAttacking && s.dist < 2.2 && brain.roll(0.20 + s.reaction * 0.40)) {
      brain.ground.changeTo('block'); return; // respect the counter-hit
    }
    if (!s.canAct) {
      // Mid-swing: hold the attack state until the move resolves.
      brain.directive = { state: COMBAT_STATES.ATTACK, move: 'continue' };
      return;
    }
    // Move resolved — back to neutral; the controller's lanes pick the
    // actual technique (surge/rage/urge/grab/limbs stay in ai.js).
    brain.ground.changeTo('neutral');
  }
  exit() {}
}

class BlockState extends State {
  enter(brain) { brain._blockEntered = 0; }
  execute(brain) {
    const s = brain.snap;
    if (s.myState === 'hit' || s.stun > 0.12) { brain.ground.changeTo('hit'); return; }
    brain._blockEntered += 1;
    // Hold guard while the threat is live; release after it passes.
    const threatGone = !s.foeAttacking && brain._blockEntered > 4;
    if (threatGone || s.dist > RANGE.POKE + 0.6) { brain.ground.changeTo('neutral'); return; }
    brain.directive = { state: COMBAT_STATES.BLOCK, move: 'hold' };
  }
  exit() {}
}

class HitState extends State {
  enter() {}
  execute(brain) {
    const s = brain.snap;
    // Launched out of the combo -> the air machine takes over.
    if (s.launched || (!s.onGround && !s.downed)) { brain._toAir(s.downed ? 'down' : 'launch'); return; }
    if (s.canAct && s.stun <= 0.05) { brain.ground.changeTo('neutral'); return; }
    brain.directive = { state: COMBAT_STATES.HIT, move: 'recover' };
  }
  exit() {}
}

/* ---------------- air-region states ---------------- */

class LaunchState extends State {
  enter() {}
  execute(brain) {
    const s = brain.snap;
    if (s.onGround && s.canAct) { brain._toGround(); return; }
    if (s.onGround && s.downed) { brain.air.changeTo('down'); return; }
    // Juggled: attempt the tech on the way down (controller checks tryTech).
    brain.directive = { state: COMBAT_STATES.LAUNCH, move: 'tech' };
  }
  exit() {}
}

class DownState extends State {
  enter() {}
  execute(brain) {
    const s = brain.snap;
    if (s.onGround && s.canAct && !s.downed) { brain._toGround(); return; }
    // Knocked down: wakeup timing — the controller waits for canAct.
    brain.directive = { state: COMBAT_STATES.LAUNCH, move: 'wakeup' };
  }
  exit() {}
}

/* Global state: runs every tick regardless of region/state. */
class CombatGlobalState extends State {
  enter() {}
  execute(brain) {
    const s = brain.snap;
    if (!s) return;
    if (s.roundOver) {
      brain.directive = { state: COMBAT_STATES.NEUTRAL, move: 'idle' };
      brain._frozen = true;
    } else {
      brain._frozen = false;
    }
  }
  exit() {}
}

/* ---------------- the brain ---------------- */

export class CombatBrain {
  /**
   * @param {object|null} ai - the AIController (may be null in tests).
   * @param {object} personality - { aggression, reaction, grabBias }.
   */
  constructor(ai = null, personality = {}) {
    this.ai = ai;
    this.aggression = ai?.aggression ?? personality.aggression ?? 0.6;
    this.reaction = ai?.reaction ?? personality.reaction ?? 0.6;
    this.grabBias = ai?.grabBias ?? personality.grabBias ?? 0.1;

    this.snap = null;
    this.directive = { state: COMBAT_STATES.NEUTRAL, move: 'space' };
    this.region = COMBAT_REGIONS.GROUND;
    this._frozen = false;
    this._blockEntered = 0;
    this._rand = Math.random;

    this.ground = new StateMachine(this);
    this.ground.add('neutral', new NeutralState());
    this.ground.add('attack', new AttackState());
    this.ground.add('block', new BlockState());
    this.ground.add('hit', new HitState());
    this.ground.globalState = new CombatGlobalState();
    this.ground.changeTo('neutral');

    this.air = new StateMachine(this);
    this.air.add('launch', new LaunchState());
    this.air.add('down', new DownState());
    this.air.globalState = new CombatGlobalState();
  }

  /** Probability roll; injectable for deterministic tests. */
  roll(p) { return this._rand() < p; }

  _toAir(stateId) {
    this.region = COMBAT_REGIONS.AIR;
    this.air.changeTo(stateId);
  }
  _toGround() {
    this.region = COMBAT_REGIONS.GROUND;
    this.ground.changeTo('neutral');
  }

  /** Current state id of the active region machine (for tests/debug). */
  currentStateId() {
    const m = this.region === COMBAT_REGIONS.GROUND ? this.ground : this.air;
    return m.currentState ? [...m.states.entries()].find(([, v]) => v === m.currentState)?.[0] ?? null : null;
  }

  /**
   * Run one brain tick. Returns the directive for the controller:
   * { state: 'neutral'|'attack'|'block'|'hit'|'launch',
   *   move: 'approach'|'space'|'create-space'|'hold'|'continue'|
   *         'recover'|'tech'|'wakeup'|'idle' }
   */
  think(snap, rand = Math.random) {
    this._rand = rand;
    this.snap = this._withDefaults(snap);

    // Root-level region transitions (the hierarchy).
    if (this.region === COMBAT_REGIONS.GROUND &&
        (this.snap.launched || (!this.snap.onGround && this.snap.myState !== 'attack' && !this.snap.downed))) {
      this._toAir('launch');
    } else if (this.region === COMBAT_REGIONS.GROUND && this.snap.downed) {
      this._toAir('down');
    } else if (this.region === COMBAT_REGIONS.AIR && this.snap.onGround &&
               this.snap.canAct && !this.snap.downed) {
      this._toGround();
    }

    (this.region === COMBAT_REGIONS.GROUND ? this.ground : this.air).update();
    return this.directive;
  }

  _withDefaults(s) {
    return {
      dist: 3, dir: 1, myState: 'idle', foeState: 'idle',
      foeAttacking: false, foeAttackPhase: null,
      onGround: true, canAct: true, stun: 0, meter: 0,
      launched: false, downed: false,
      rageOn: false, urgeOn: false, urgePips: 0, urgeReady: false,
      inBlockstun: false, roundOver: false,
      aggression: this.aggression, reaction: this.reaction, grabBias: this.grabBias,
      ...s,
    };
  }

  /**
   * Adapter for GhostAI fallback: maps a ghost situation snapshot
   * ({ dist, myStance, foeState, foeAttackStartup, ... }) to a ghost
   * action string. Lets the Yuka brain drive ghost fighters too.
   */
  decideFromGhostSnap(gsnap, rand = Math.random) {
    const snap = {
      dist: gsnap.dist ?? 3,
      myState: 'idle',
      foeState: gsnap.foeState || 'neutral',
      foeAttacking: gsnap.foeAttackStartup === true || gsnap.foeState === 'attack',
      foeAttackPhase: gsnap.foeAttackStartup ? 'startup' : null,
      onGround: true, canAct: true, stun: 0, meter: 50,
      aggression: this.aggression, reaction: this.reaction, grabBias: this.grabBias,
    };
    const d = this.think(snap, rand);
    switch (d.state) {
      case COMBAT_STATES.ATTACK: return gsnap.dist < RANGE.GRAB ? 'grab' : '1';
      case COMBAT_STATES.BLOCK: return 'block';
      case COMBAT_STATES.HIT: return 'block';
      case COMBAT_STATES.LAUNCH: return 'neutral';
      default:
        return d.move === 'approach' ? 'walk_in' : (d.move === 'create-space' ? 'walk_out' : 'neutral');
    }
  }
}
