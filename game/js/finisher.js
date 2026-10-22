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
   ============================================================ */

/* A finisher definition (authored in the creation suite):
   { name, beats: [ { btn: '1'|'2'|'3'|'4'|null, dur, pose } ... ],
     meterCost: 1.0, victimHpGate: 0.25 } */
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
   as attacks/poses, spends the meter. Returns true if it fired. */
export function tryFinisher(game, def) {
  if (!def || !Array.isArray(def.beats) || !def.beats.length) return false;
  if (!gatesOpen(game, def)) return false;
  const p1 = game.p1, p2 = game.p2;
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
          if (beat.btn) p1.tryAttack(beat.btn);
          else if (beat.pose && p1.playPose) p1.playPose(beat.pose);
        } catch (e) { /* a dropped beat never breaks the fight */ }
      }, at * 1000);
      t += Math.max(0.3, beat.dur || 0.8);
    }
    setTimeout(() => { p2._finisherLock = false; }, t * 1000);
    if (game.ui && game.ui.banner) game.ui.banner(`FINISHER — ${def.name}`);
    return true;
  } catch (e) {
    p2._finisherLock = false;
    return false;
  }
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
