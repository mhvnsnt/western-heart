/* ============================================================
   WESTERN HEART — Fighter Depth integration layer (worker 34)
   One import wires all twelve systems into the Game. Every system is
   feature-flagged (WH_DEPTH_FLAGS) so each can ship, test, and roll
   back independently. Integration points in game.js:
     • startMatch(): FighterDepth.onMatchStart(game)
     • _update(dt):  FighterDepth.onUpdate(game, dt)
     • _resolveCombat: kindle consumption + replay events (see INTEGRATION)
   Flags default ON for versus; training-only systems (trials, punish,
   ghost sparring) activate in their modes via modes.js.
   ============================================================ */

import { SoulKindle, updateKindle } from './soul-kindle.js';
import { TagRelay, TagTeam } from './tag-relay.js';
import { autoAttachCloth } from './cloth-hair.js';
import { TrialRunner, trialsFor, markTrialComplete } from './combo-trials.js';
import { GhostModel, GhostRecorder, GhostAI, loadGhost } from './ghost-ai.js';
import { analyzeReplay, showTrialReview, evHit } from './replay-analysis.js';
import { StageIntro } from './stage-intros.js';
import { applyVariant, makeWeatherPoints, updateWeatherPoints } from './stage-variants.js';
import { pickVersusBanter, playVersusBanter } from './versus-banter.js';
import { renderMovelist } from './movelist-ui.js';
import { mapSpecialInput, isSpecialStyleOn } from './special-style.js';
import { PunishRunner, drillsFor } from './punishment-training.js';

export const WH_DEPTH_FLAGS = {
  soulKindle: true,      // ki charge
  tagRelay: true,        // tag throws/crash/assault (2v2 modes)
  clothHair: true,       // hair + cloth physics
  comboTrials: true,     // combo trials
  ghostAi: true,         // ghost AI (soul echoes)
  replayAnalysis: true,  // trial review overlay
  stageIntros: true,     // stage intro camera sweeps
  stageVariants: true,    // weather/time-of-day variants
  versusBanter: true,     // versus banter
  movelistUi: true,      // in-game movelist
  specialStyle: true,    // guided hands (easy inputs)
  punishTraining: true,  // skull's lessons
};
export function setDepthFlag(k, v) { if (k in WH_DEPTH_FLAGS) WH_DEPTH_FLAGS[k] = !!v; }

const F = WH_DEPTH_FLAGS;

export const FighterDepth = {
  /* Called from Game.startMatch after fighters spawn. */
  onMatchStart(game, opts = {}) {
    const { p1, p2 } = game;
    if (F.soulKindle) { if (!p1.kindle) p1.kindle = new SoulKindle(); if (!p2.kindle) p2.kindle = new SoulKindle(); }
    if (F.clothHair && game.arena) {
      try {
        game._whCloth = [autoAttachCloth(p1.group || p1.model), autoAttachCloth(p2.group || p2.model)];
      } catch { game._whCloth = []; }
    }
    if (F.stageIntros && !opts.skipIntro && game.camera) {
      const stage = opts.stageDef || (game.stageDef);
      if (stage) game._whIntro = new StageIntro(stage, game.camera);
    }
    if (F.stageVariants && opts.variantId && opts.stageDef) {
      game.stageDef = applyVariant(opts.stageDef, opts.variantId);
    }
    // replay event log for this match (worker 29's recorder can adopt it)
    if (F.replayAnalysis) game._whReplayLog = [];
    // tag teams (2v2): opts.tagTeams = { p1: [a, b], p2: [a, b] }
    if (F.tagRelay && opts.tagTeams) {
      game._whTagP1 = new TagRelay(new TagTeam(opts.tagTeams.p1[0], opts.tagTeams.p1[1]), null);
      game._whTagP2 = new TagRelay(new TagTeam(opts.tagTeams.p2[0], opts.tagTeams.p2[1]), null);
      game._whTagP1.foe = game._whTagP2; game._whTagP2.foe = game._whTagP1;
    }
    // versus banter pick (presentation by the versus screen; async, non-blocking)
    if (F.versusBanter && p1.charData && p2.charData) {
      pickVersusBanter(p1.charData.id, p2.charData.id, opts).then(b => { game._whBanter = b; }).catch(() => {});
    }
    return null;
  },

  /* Called from Game._update(dt). Handles per-frame systems. */
  onUpdate(game, dt, pressed = {}) {
    if (F.soulKindle) {
      if (pressed.p1) updateKindle(game.p1, pressed.p1, dt);
      if (pressed.p2) updateKindle(game.p2, pressed.p2, dt);
    }
    if (F.tagRelay) {
      if (game._whTagP1) game._whTagP1.update(dt);
      if (game._whTagP2) game._whTagP2.update(dt);
    }
    if (F.stageIntros && game._whIntro && !game._whIntro.done) {
      game._whIntro.update(dt);
    }
    if (F.stageVariants && game._whWeather) {
      updateWeatherPoints(game._whWeather, dt, (game._whT = (game._whT || 0) + dt));
    }
    // cloth sims advance here (colliders from fighter bodies in the full wire)
    if (F.clothHair && game._whCloth) {
      for (const set of game._whCloth) for (const a of set) {
        if (a.sim && !a.sim.sleeping) { /* stepped by the renderer with camera dist */ }
      }
    }
  },

  /* Combat hooks — call from Game._resolveCombat. */
  onHitLanded(attacker, defender, move, dmg, opts = {}) {
    let counter = !!opts.counter;
    if (F.soulKindle && attacker.kindle && attacker.kindle.consumeOnHitLanded()) counter = true;
    if (F.replayAnalysis && attacker.game && attacker.game._whReplayLog)
      attacker.game._whReplayLog.push(evHit(attacker.isPlayer ? 'p1' : 'p2', move, dmg, { counter }));
    return { counter };
  },
  damageTakenMult(defender) {
    if (F.soulKindle && defender.kindle) return defender.kindle.damageTakenMult();
    return 1;
  },
  canBlock(defender) {
    if (F.soulKindle && defender.kindle && !defender.kindle.canBlock()) return false;
    return true;
  },

  /* Input mapping hook — call before the fighter consumes a button. */
  mapInput(player, fighterId, button) {
    if (F.specialStyle && isSpecialStyleOn(player)) return mapSpecialInput(fighterId, button, true);
    return button;
  },

  /* Per-frame raw input queue from Game._update (p1 only; AI has no queue).
     Watches for the 1+2+3+4 soul-kindle press. */
  onPlayerQueue(fighter, queue, dt) {
    if (!F.soulKindle || !fighter) return;
    if (!fighter.kindle) fighter.kindle = new SoulKindle();
    updateKindle(fighter, queue, 0); // detection only; timers tick in onUpdateFrame
  },

  /* Per-frame housekeeping — call from Game._update's fight branch. */
  onUpdateFrame(game, dt) {
    if (F.soulKindle) {
      if (game.p1 && game.p1.kindle) game.p1.kindle.update(dt);
      if (game.p2 && game.p2.kindle) game.p2.kindle.update(dt);
    }
    this.onUpdate(game, dt);
  },

  /* Training-mode factories (modes.js calls these). */
  newTrialRunner(fighterId, trialIdx = 0) {
    const t = trialsFor(fighterId)[trialIdx];
    return t ? new TrialRunner(t) : null;
  },
  completeTrial(fighterId, trialId) { return markTrialComplete(fighterId, trialId); },
  newPunishRunner(foeId, drillIdx = 0) {
    const d = drillsFor(foeId)[drillIdx];
    return d ? new PunishRunner(d) : null;
  },
  ghostFor(name, fallback) {
    const m = loadGhost(name);
    return new GhostAI(m || new GhostModel(name), fallback);
  },
  newGhostRecorder(name) { return new GhostRecorder(new GhostModel(name)); },

  /* Post-match: trial review overlay. */
  showReview(game) {
    if (!F.replayAnalysis || !game._whReplayLog) return null;
    return showTrialReview(analyzeReplay(game._whReplayLog));
  },
  openMovelist(fighterId, fighterName) {
    if (!F.movelistUi) return 0;
    return renderMovelist(fighterId, fighterName);
  },
  playBanter(p1char, p2char, opts) {
    if (!F.versusBanter) return Promise.resolve({ played: false });
    return playVersusBanter(p1char, p2char, opts);
  },
};

/* Browser global for debugging / the creation suite. */
try {
  const _g = (typeof window !== 'undefined') ? window : globalThis;
  _g.WH_FighterDepth = _g.WH_FighterDepth || { FighterDepth, WH_DEPTH_FLAGS, setDepthFlag };
} catch {}
