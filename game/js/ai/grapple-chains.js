/* ============================================================
   WESTERN HEART — Yuka Grapple Chains
   State machine for grappling sequences, built on the REAL Yuka.js
   library (game/vendor/yuka/yuka.module.js — MIT, (c) 2023 Yuka
   authors). No hand-tooled FSM: Yuka's State and StateMachine drive
   every transition below.

   Chain: idle -> clinch -> throw -> ground -> idle
                        \-> reversed -> idle   (escape / break)

     idle     — not grappling; watches for clinch range.
     clinch   — chest-to-chest tie-up; fights for the throw entry.
                Times out back to idle if the foe creates space.
     throw    — the throw is executing (fighter.state === 'throwing').
                Tracks the victim; a break sends us to reversed.
     ground   — victim is down: okizeme window (stomp / pickup /
                back off — the controller's attack lanes choose).
     reversed — the attempt was escaped or broken; brief reset.

   The machine is ADVISORY: think(snap) returns an intent string and
   the AIController in game/js/ai.js owns every tryAttack call.
   Intents: 'tie-up' | 'commit-throw' | 'chain-ground' | 'disengage' | null
   ============================================================ */
import { State, StateMachine } from '../../vendor/yuka/yuka.module.js';
import { phaseAtProgress } from './move-melding.js'; // WH meld layer (pure logic, no deps)

export const GRAPPLE_STATES = {
  IDLE: 'idle',
  CLINCH: 'clinch',
  THROW: 'throw',
  GROUND: 'ground',
  REVERSED: 'reversed',
};

export const GRAPPLE_INTENTS = {
  TIE_UP: 'tie-up',
  COMMIT_THROW: 'commit-throw',
  CHAIN_GROUND: 'chain-ground',
  CHAIN_MELD: 'chain-meld', // meld the active throw into another move (see move-melding.js)
  DISENGAGE: 'disengage',
};

const CLINCH_RANGE = 1.7;   // world units: chest-to-chest
const CLINCH_TICKS = 14;     // ~0.23s at 60fps before committing or resetting
const GROUND_TICKS = 45;     // okizeme window before the machine resets

class GrappleIdle extends State {
  enter() {}
  execute(chain) {
    const s = chain.snap;
    chain.intent = null;
    if (!s.canAct || !s.onGround || s.roundOver) return;
    if (s.myState === 'thrown' || s.myState === 'throwing') return;
    if (s.dist <= CLINCH_RANGE && chain.roll(s.grabBias * 2.2)) {
      chain.fsm.changeTo(GRAPPLE_STATES.CLINCH);
    }
  }
  exit() {}
}

class GrappleClinch extends State {
  enter(chain) { chain._t = 0; chain.intent = GRAPPLE_INTENTS.TIE_UP; }
  execute(chain) {
    const s = chain.snap;
    chain._t += 1;
    if (s.myState === 'throwing') { chain.fsm.changeTo(GRAPPLE_STATES.THROW); return; }
    if (s.myState === 'thrown' || s.myState === 'hit' || s.stun > 0.12) {
      chain.fsm.changeTo(GRAPPLE_STATES.REVERSED); return; // stuffed out of the tie-up
    }
    if (s.dist > CLINCH_RANGE + 0.5 || !s.onGround) {
      chain.fsm.changeTo(GRAPPLE_STATES.IDLE); return; // foe created space
    }
    // Commit the throw once the tie-up settles (fair: not instant).
    chain.intent = chain._t >= CLINCH_TICKS ? GRAPPLE_INTENTS.COMMIT_THROW : GRAPPLE_INTENTS.TIE_UP;
  }
  exit() {}
}

class GrappleThrow extends State {
  enter(chain) { chain.intent = null; chain.meld = null; chain._meldPhase = null; }
  execute(chain) {
    const s = chain.snap;
    if (s.myState !== 'throwing') {
      // Throw finished or was broken: victim down -> ground chain,
      // otherwise the attempt died -> idle.
      chain.fsm.changeTo(s.foeDowned ? GRAPPLE_STATES.GROUND : GRAPPLE_STATES.IDLE);
      return;
    }
    chain.intent = null; // mid-throw: hold, the animation owns this window
    // Move melding (WH extension on the Tekken throw base): at each
    // meld-phase boundary, ask the engine for legal exits from the
    // active throw. No engine attached -> today's behavior, bit for bit.
    const eng = chain.meldEngine;
    if (eng && s.throwMove && s.throwProgress != null) {
      const phase = phaseAtProgress(s.throwProgress);
      if (phase !== chain._meldPhase) {
        chain._meldPhase = phase;
        const cands = eng.findMelds(s.throwMove, phase, { rolesOk: s.meldRolesOk !== false });
        const pick = cands[0]; // ranked by blend cost, cheapest first
        // meldBias: technicians chain more; (1.15 - cost) favors smooth paths
        if (pick && chain.roll(chain.meldBias * (1.15 - pick.cost))) {
          chain.meld = { from: s.throwMove, to: pick.to, hybrid: pick.hybrid, kind: pick.kind };
          chain.intent = GRAPPLE_INTENTS.CHAIN_MELD;
        }
      }
    }
  }
  exit() {}
}

class GrappleGround extends State {
  enter(chain) { chain._t = 0; }
  execute(chain) {
    const s = chain.snap;
    chain._t += 1;
    // Okizeme: keep pressure while the victim is down, then reset.
    if (!s.foeDowned || chain._t > GROUND_TICKS || !s.canAct) {
      chain.fsm.changeTo(GRAPPLE_STATES.IDLE); return;
    }
    chain.intent = GRAPPLE_INTENTS.CHAIN_GROUND;
  }
  exit() {}
}

class GrappleReversed extends State {
  enter(chain) { chain._t = 0; chain.intent = GRAPPLE_INTENTS.DISENGAGE; }
  execute(chain) {
    chain._t += 1;
    if (chain._t > 8) chain.fsm.changeTo(GRAPPLE_STATES.IDLE);
  }
  exit() {}
}

export class GrappleChain {
  constructor(ai = null, personality = {}) {
    this.ai = ai;
    this.grabBias = ai?.grabBias ?? personality.grabBias ?? 0.1;
    this.snap = null;
    this.intent = null;
    this._t = 0;
    this._rand = Math.random;
    // Move-melding extension (optional): a MeldEngine from
    // game/js/ai/move-melding.js. The last chosen meld is exposed on
    // chain.meld when intent === 'chain-meld'.
    this.meldEngine = null;
    this.meld = null;
    this.meldBias = ai?.meldBias ?? personality.meldBias ?? 0.35;
    this._meldPhase = null;

    this.fsm = new StateMachine(this);
    this.fsm.add(GRAPPLE_STATES.IDLE, new GrappleIdle());
    this.fsm.add(GRAPPLE_STATES.CLINCH, new GrappleClinch());
    this.fsm.add(GRAPPLE_STATES.THROW, new GrappleThrow());
    this.fsm.add(GRAPPLE_STATES.GROUND, new GrappleGround());
    this.fsm.add(GRAPPLE_STATES.REVERSED, new GrappleReversed());
    this.fsm.changeTo(GRAPPLE_STATES.IDLE);
  }

  roll(p) { return this._rand() < p; }

  /**
   * Attach the WH move-melding engine (game/js/ai/move-melding.js).
   * Optional — without it the chain behaves exactly as before.
   */
  attachMeldEngine(engine, opts = {}) {
    this.meldEngine = engine;
    if (opts.meldBias !== undefined) this.meldBias = opts.meldBias;
    return this;
  }

  currentStateId() {
    const c = this.fsm.currentState;
    return c ? [...this.fsm.states.entries()].find(([, v]) => v === c)?.[0] ?? null : null;
  }

  /**
   * One tick. Returns an intent for the controller, or null.
   * snap: { dist, onGround, canAct, stun, myState, foeDowned,
   *         grabBias, roundOver,
   *         throwMove, throwProgress, meldRolesOk }  // meld extension:
   *         throwMove = active grapple move id, throwProgress = 0..1
   */
  think(snap, rand = Math.random) {
    this._rand = rand;
    this.snap = {
      dist: 3, onGround: true, canAct: true, stun: 0,
      myState: 'idle', foeDowned: false, roundOver: false,
      grabBias: this.grabBias, ...snap,
    };
    this.intent = null;
    this.fsm.update();
    return this.intent;
  }
}
