/* ============================================================
   WESTERN HEART — Create-a-Finisher runtime
   From the Def Jam: Fight for NY teardown (ANIMATION-FINDINGS.md):
   finishers are their OWN authored bank (BLAZIN.VIV), not scaled-up
   normals, and they fire behind TWO gates:
     1. resource gate — the fighter's meter is full
     2. victim gate — the opponent is in the "danger" (red) zone
   Western Heart mapping: Nine-Soul Meter full + opponent HP < 25%.

   Suite side (customization/finisher-creator.js) authors a finisher
   as a sequence of authored beats; this module checks the gates
   and plays the sequence in the live fight. Finishers never replace
   win taunts — the taunt still plays after the finisher resolves.

   TEKKEN-STYLED FINISHERS (2026-10-23, docs/research/FINISHER-DESIGN-2026-10-23.md):
   no separate input mode — the finisher IS the killing blow, an extension
   of the win-pose/victory flow. When no suite-authored finisher exists,
   ensureFinisherMoves() synthesizes one per fighter from their own real
   moveset data (strongest strike = the finisher blow, same pattern as
   rage.js _strongestStrike) — never hand-authored. The beats play in
   INTRO_OUTRO anim context (after the KO is decided, before the win pose)
   so they respect the anim gate; the context is save/restored so a dropped
   finisher can never strand the game in the wrong context. On the killing
   blow the X-ray hook fires (game/js/xray.js, built in parallel — the
   import is fire-and-forget with a fallback, so the finisher plays on
   whether or not that module has landed). Impact visualization is the
   X-ray layer reveal + soft-body deformation ONLY — no gore, no
   cutting/tearing (softbody.js header), per the owner.
   ============================================================ */
import { setAnimContext, getAnimContext, CTX } from './anim-gate.js';

/* A finisher definition (authored in the creation suite):
   { name, beats: [ { btn: '1'|'2'|'3'|'4'|null, dur, pose,
                     xray?: { limb, power, fluid?: { preset, intensity } } } ... ],
     meterCost: 1.0, victimHpGate: 0.25 }
   The optional per-beat `xray` field marks the killing blow: when that
   beat plays, the X-ray hook fires (see _xrayFlash below) and the fluid
   hook fires a viscous splash (see _fluidBurst below). */
export function gatesOpen(game, def) {
  const p1 = game.p1, p2 = game.p2;
  if (!p1 || !p2 || p1.dead || p2.dead) return false;
  const meter = p1.soulMeter ?? p1.meter ?? 0;
  const meterMax = p1.soulMeterMax ?? p1.meterMax ?? 1;
  const resourceGate = (meter / Math.max(1e-6, meterMax)) >= (def.meterCost ?? 1.0);
  const victimGate = (p2.hp / Math.max(1e-6, p2.maxHp)) <= (def.victimHpGate ?? 0.25);
  return resourceGate && victimGate;
}

/* Fire the finisher: roots both fighters, plays the authored beats
   as attacks/poses, spends the meter. Returns true if it fired.
   The beats run in INTRO_OUTRO anim context (the round's outro — after
   the KO is decided, before the win pose), save/restored around the
   sequence so the anim gate is respected without stranding FIGHT. */
export function tryFinisher(game, def) {
  if (!def || !Array.isArray(def.beats) || !def.beats.length) return false;
  if (!gatesOpen(game, def)) return false;
  const p1 = game.p1, p2 = game.p2;
  // Tekken-styled: the finisher is the victory outro, not a fight mode.
  const prevCtx = getAnimContext();
  try { setAnimContext(CTX.INTRO_OUTRO); } catch (e) { /* stay put */ }
  const restoreCtx = () => { try { setAnimContext(prevCtx); } catch (e) {} };
  try {
    // Spend the meter (Nine-Soul meter is the WH resource gate).
    if (p1.soulMeter != null) p1.soulMeter = 0;
    else if (p1.meter != null) p1.meter = 0;
    // Root the victim for the cinematic beats (both stay hittable=false
    // only for the finisher's duration — same contract as throws).
    p2._finisherLock = true;
    let t = 0;
    for (const beat of def.beats) {
      const at = t;
      setTimeout(() => {
        try {
          if (beat.xray) { _xrayFlash(game, p1, p2, beat.xray); _fluidBurst(game, p1, p2, beat.xray); }
          if (beat.btn) p1.tryAttack(beat.btn);
          else if (beat.pose && p1.playPose) p1.playPose(beat.pose);
        } catch (e) { /* a dropped beat never breaks the fight */ }
      }, at * 1000);
      t += Math.max(0.3, beat.dur || 0.8);
    }
    setTimeout(() => { p2._finisherLock = false; restoreCtx(); }, t * 1000);
    if (game.ui && game.ui.banner) game.ui.banner(`FINISHER — ${def.name}`);
    return true;
  } catch (e) {
    p2._finisherLock = false;
    restoreCtx();
    return false;
  }
}

/* X-ray hook: flash the victim's anatomy layers on the killing blow.
   game/js/xray.js is built in parallel — the dynamic import is
   fire-and-forget with a try/catch fallback, so the finisher plays
   identically whether or not that module has landed. A missed flash
   never breaks the fight. Interface contract is documented in
   docs/research/FINISHER-DESIGN-2026-10-23.md §5. */
function _xrayFlash(game, attacker, victim, xray) {
  try {
    const spec = Object.assign({ attacker, victim, game }, xray || {});
    import('./xray.js').then((mod) => {
      try {
        if (mod && typeof mod.xrayFlash === 'function') mod.xrayFlash(spec);
      } catch (e) { /* a bad flash never breaks the fight */ }
    }).catch(() => { /* xray.js not landed yet — finisher continues */ });
  } catch (e) { /* sync import failure — never break the finisher */ }
}

/* Fluid hook: viscous splash (blood/mud/ink) at the killing blow.
   game/js/fx/fluid.js is built on the fluids track — the dynamic import is
   fire-and-forget with a try/catch fallback, so the finisher plays
   identically whether or not that module has landed. A missed splash
   never breaks the fight. The beat's xray field may carry an optional
   `fluid: { preset: 'blood'|'mud'|'ink', intensity }` to tune the burst;
   without it the hook defaults to a blood splash scaled by xray.power.
   Stylized impact splash only — no dismemberment, no gore systems, per
   the PR #872 constraint (impact viz = X-ray reveal + deformation). */
function _fluidBurst(game, attacker, victim, xray) {
  try {
    const spec = Object.assign({ attacker, victim, game }, xray || {});
    import('./fx/fluid.js').then((mod) => {
      try {
        if (mod && typeof mod.fluidBurst === 'function') mod.fluidBurst(spec);
      } catch (e) { /* a bad splash never breaks the fight */ }
    }).catch(() => { /* fx/fluid.js not landed yet — finisher continues */ });
  } catch (e) { /* sync import failure — never break the finisher */ }
}

/* Strongest real strike in the moveset (no grabs): returns [key, move].
   Same pattern as rage.js _strongestStrike — the finisher blow is derived
   from the fighter's own real strike data, never hand-authored. */
function _strongestStrike(ms, excludeKey = null) {
  let best = null, bestKey = null, bestDmg = -1;
  for (const [key, m] of Object.entries(ms.moves)) {
    if (!m || key === excludeKey) continue;
    if (m.isGrab || m.move_class === 'throw') continue;
    const d = m.damage || 0;
    if (d > bestDmg && (m.move_class === 'strike' || !m.move_class)) { best = m; bestKey = key; bestDmg = d; }
  }
  return [bestKey, best];
}

/* Generic fallback when a fighter has no loaded moveset at all. */
function _fallbackBase() {
  return {
    name: 'HEAVY STRIKE', t3_source: 't7', limb: 'armR',
    startup: 0.3, active: 0.05, recovery: 0.6, damage: 18, knock: 4,
    anim_ref: null, input_slots: [],
  };
}

/* Best-effort mapping of the blow's moveset input onto a finisher beat
   button ('1'..'4'). The finisher blow is always the heavy strike. */
function _finisherBtn(blow) {
  const slots = blow.input_slots || (blow.input ? [blow.input] : []);
  for (const s of slots) if (/^[1-4]$/.test(String(s))) return String(s);
  return '4';
}

export const FINISHER_NOTATION = 'F.FIN';

/**
 * Synthesize a finisher def for a fighter from their own real moveset
 * data: the strongest strike becomes the finisher blow (killing-blow
 * beat, carrying the X-ray flash). Mirrors ensureRageMoves in rage.js:
 * idempotent (cached on the moveset), safe to call every match, returns
 * the def (not a boolean) so the game lane can pass it to tryFinisher:
 *   tryFinisher(game, getCustomFinisher() || ensureFinisherMoves(id, msApi))
 * A suite-authored finisher always wins over the synthesized one.
 * Returns null when no moveset is available.
 */
export function ensureFinisherMoves(fighterId, msApi) {
  if (!msApi) return null;
  const ms = (msApi.playedMoveset && msApi.playedMoveset(fighterId)) ||
             (msApi.getFighterMoveset && msApi.getFighterMoveset(fighterId));
  if (!ms || !ms.moves) return null;
  if (ms._finisherDef) return ms._finisherDef;

  const [blowKey, blow0] = _strongestStrike(ms);
  const blow = blow0 || _fallbackBase();
  const dmg = blow.damage || 18;
  const def = {
    name: `${(blow.name || 'STRIKE').toUpperCase()} — FINISHER`,
    meterCost: 1.0,
    victimHpGate: 0.25,
    notation: FINISHER_NOTATION,
    source: { move: blowKey || 'fallback', limb: blow.limb || 'armR' },
    beats: [
      {
        btn: _finisherBtn(blow),
        dur: 1.1,
        xray: {
          limb: blow.limb || 'armR',
          power: Math.min(1, Math.max(0.3, dmg / 40)),
        },
      },
    ],
  };
  ms._finisherDef = def;
  return def;
}

/* Read the custom fighter's authored finisher (suite localStorage). */
export function getCustomFinisher() {
  for (const key of ['wh_creation_suite_v1', 'wh_create_fighter_v1']) {
    try {
      const raw = localStorage.getItem(key);
      if (!raw) continue;
      const F = JSON.parse(raw);
      if (F && F.finisher && Array.isArray(F.finisher.beats) && F.finisher.beats.length) {
        return F.finisher;
      }
    } catch (e) { /* try next key */ }
  }
  return null;
}
