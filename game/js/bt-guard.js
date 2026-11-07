/* ============================================================
   BACK-TURNED GUARD — Tekken-strict + the owner's hybrid design
   (owner rulings 2026-11-06; engine wiring in fighter.js receiveHit;
    history in docs/movesets/BT-SYSTEM-FIX-2026-11-06.md)

   RULE 1 — TEKKEN-STRICT (owner 2026-11-06 ~15:21 CST: "Yes I want it
   Tekken strict"). While Fighter._bt holds, guard is DISABLED: an
   incoming hit resolves through the engine's existing UNGUARDED path
   (full hit, normal reactions, the #1611 back-hit knockdown flags),
   regardless of guard input. The moment _bt clears, guard works
   exactly as before. No damage change, no counter-hit addition, no
   BT entry/exit change.

   RULE 2 — THE MULTI-ARM EXCEPTION (owner 2026-11-06 ~15:23 CST):
   fighters with MORE THAN ONE ARM PAIR keep guard while back-turned.
   The qualifier is DATA-DRIVEN, never a name list: it is derived from
   the fighter's actual in-game model (extra arm chain present in the
   rig) by tools/anatomy/bt_guard_arm_scan.py, and
   test/back-turned.test.mjs re-derives it from the GLB bytes on every
   run. BT_GUARD_MULTI_ARM below is the checked-in result of that
   derivation, with the evidence per fighter.

   RULE 3 — THE HANDICAP (owner 2026-11-06 ~15:36 CST: "Bleed design
   go with that but we build the guard break design as a layer into
   it from soul calibers files, so we just invented something new
   awesome."): the bleed base plus a SoulCalibur guard-break layer.
   While back-turned and guarding, a qualifying fighter blocks highs
   and mids only; every blocked hit (1) bleeds chip at chipPct of move
   damage through the existing chip formula / recoverable pool (front
   guard chips 0.12), (2) earns meterOnBlock meter (front guard: +4),
   (3) pushes the defender back at pushbackMult of the standard block
   pushback, (4) never clears _bt, and (5) adds STRAIN to the back
   pair. Lows and throws land clean (the engine's guard words already
   guarantee both). At strainMax the back pair is SPENT: BT guard
   turns off for the rest of that back-turned stint (Tekken-strict
   until a real BT exit clears _bt); strain resets when _bt ends.
   Readability tell, SoulCalibur-style: the defender's own health-bar
   fill glows warning yellow at strainWarn1 (60) and warning red at
   strainWarn2 (80) — the minimal equivalent this HUD supports
   (UI._hp in main.js toggles .bt-strain-1 / .bt-strain-2).

   STRAIN PROVENANCE (fabrication banned; judgment calls labeled):
   - Holdings check first: NO extracted SoulCalibur system data is
     held. The SCVI game binaries were never acquired
     (teardown/scvi-doa6-acquisition-2026-10-14.md: "Game binaries
     NOT acquired"); teardown/soulcalibur-6/docs/SCVI-MECHANICS.md is
     our own research write-up ("inferred from player-facing
     behavior") — qualitative only. SC2 teardowns exist but SC2 has
     no guard-stamina gauge.
   - Documented system data (SuperCombo Wiki, SoulCalibur VI /
     System, extracted game data; read 2026-11-06): guard stamina
     accumulates 0 -> 100%; the health bar glows YELLOW at 60% and
     RED at 80%; Guard Crush at 100%; Guard Impact costs 10% and
     recovers 12% on a successful parry; all characters have 240 HP;
     move levels by damage: lights 0-21, mediums 22-34, heavies 35+.
     Per-move Guard Burst values are published per move in frame
     data (Frame Calibur): 16 dmg -> 5%, 18-20 dmg -> 9-14%, 30 dmg
     -> 9%, 32 dmg -> 18%, 36 dmg -> 15%, 40 dmg -> 25%, 52 dmg ->
     41.67%; break/special moves reach 20.67-50%.
   - WH damage scale (measured from game/assets/movesets/
     chatur.json, 281 damaging non-grab moves): min 0, median 13,
     p75 16, max 60; basics '1' = 7, '2' = 11.
   - THE FIT (JUDGMENT CALL, labeled): strainPerDamage = 0.75 strain
     per point of the blocked move's listed damage — the same input
     the existing chip formula starts from, NOT stat-scaled, matching
     SC where Guard Burst is a property of the attacking move.
     Anchors: WH jab 7 dmg -> 5.25 strain (SC light ~5%); WH medium
     ~16 -> 12 (SC medium 9-15%); WH heavy 30 -> 22.5 (SC heavy
     non-break 18-25%); WH max 60 -> 45 (SC break-attack ceiling
     42-50%). Break profile: ~19 jabs, ~8 medium hits (roughly 2-3
     medium strings), ~4-5 heavies — SC's sustained-pressure crush
     profile. The 100/60/80 gauge structure is documented SC data
     plus the owner's spec; the 0.75 slope and the WH<->SC scale
     conversion are fitted judgment calls, NOT SC data.
   - Documented SC nuance NOT implemented (observation only): in SC,
     small quick attacks cannot crush even at 100% stamina — only
     certain/heavier moves break. The owner's design breaks at max
     regardless of the breaking move; the owner's design governs.
   ============================================================ */

// The owner's design block (his spec, camelCase per codebase style;
// his snake_case keys map 1:1: chip_pct->chipPct, meter_on_block->
// meterOnBlock, pushback_mult->pushbackMult, clears_bt->clearsBt,
// strain_max->strainMax, strain_per_block->strainPerDamage (see the
// derivation above: ours is a per-damage function, not a flat value),
// strain_warn_1->strainWarn1, strain_warn_2->strainWarn2,
// on_break->onBreak).
export const BT_GUARD_DESIGN = Object.freeze({
  enabled: true,
  covers: ['high', 'mid'],       // standing-guard-blockable levels only
  chipPct: 0.30,                  // bleed: 30% chip (front guard: 0.12)
  meterOnBlock: 0,                // no meter for a back-pair block (front guard: +4)
  pushbackMult: 0.5,              // half the standard block pushback
  clearsBt: false,                // blocking never turns the fighter around
  strainMax: 100,                 // SC guard-stamina capacity (documented)
  strainPerDamage: 0.75,          // JUDGMENT CALL fitted to documented SC anchors (see header)
  strainWarn1: 60,                // SC: bar glows yellow at 60% (documented)
  strainWarn2: 80,                // SC: bar glows red at 80% (documented)
  onBreak: 'bt_guard_off_until_bt_ends',
});

// Per-fighter multi-arm derivation, checked in from
// tools/anatomy/bt_guard_arm_scan.py over the fighters' in-game GLBs.
// An entry exists ONLY where the model data verifies >1 arm pair;
// test/back-turned.test.mjs re-derives every entry (and the two
// documented negatives) from the GLB bytes, so this table cannot drift
// from the models.
//
// Owner order 2026-11-06 ("We have to rig DXMMII arms extras and zens
// tentacles in his tentacle forms"): DXMMII's extra pair and Zen's
// tentacle chains were rigged into the shipped models as real arm
// chains (method + per-model verification:
// docs/movesets/BT-GUARD-RIGGING-2026-11-06.md), so both qualify from
// rig data below. What still does NOT carry extra chains, verified the
// same day with the same detector (reported plainly, flag NOT faked):
//   dxmmii patchwork-dj rig + game/assets/models/dxmmii.glb (twins) —
//     Mokujin-family bodies with NO extra-arm geometry anywhere in
//     their source (21 material-panel meshes, standard two-arm
//     humanoid, ~4.4k verts); nothing exists there to rig. The
//     'dxmmii-patchwork' transform stage stays a documented negative.
//   dxmmii attire2/model.glb — no extra-arm geometry either (clean
//     two-arm T-pose) and unrigged (no skeleton at all).
//   zen attire1 / spirit / oversoul — rigging was ordered for the
//     tentacle form only; oversoul's body tentacles are clothing
//     imagery by canon and its one torso-rooted chain belongs to the
//     spirit head; spirit carries NO arm chains (spring chains only).
// Roster-wide sweep (game/assets/models/, 64 GLBs, same detector):
// every other model carries exactly one pair. (zafina.glb's apparent
// third root is the standard clavicle->arm chain: RightArm's parent
// IS RightShoulder, an arm bone, so it is not an independent chain.)
export const BT_GUARD_MULTI_ARM = Object.freeze({
  chatur: Object.freeze({
    armPairs: 2,
    model: 'roster/rahkasa/attires/attire1/model-rigged-textured.glb',
    chains: ['LeftArm', 'RightArm', 'DEF-upper_arm.L.002', 'DEF-upper_arm.R.002'],
    evidence: '264-joint rig: the primary Mixamo pair (LeftArm/RightArm) plus a second, ' +
      'independently rooted Rigify DEF pair (DEF-upper_arm.L.002 / DEF-upper_arm.R.002, ' +
      'the waist pair) — 4 arm chain roots, each with a hand descendant.',
  }),
  dxmmii: Object.freeze({
    armPairs: 2,
    model: 'roster/dxmmii/attires/attire1/model-rigged.glb',
    chains: ['LeftShoulder', 'LeftShoulder2', 'RightShoulder', 'RightShoulder2'],
    evidence: '81-joint rig: the standard pair plus a second pair rigged 2026-11-06 ' +
      '(LeftShoulder2/RightShoulder2 roots parented to Spine2, with Arm2/ForeArm2/Hand2 ' +
      'descendants) onto the extra-arm geometry the source mesh always carried detached ' +
      'above the head — DXMMII\'s arms are retractable/detachable by canon, and the ' +
      'floating pair is its gyro-stance system. Bind pose verified unchanged (max skin ' +
      'error 1.1e-6); the new chains articulate independently of the body.',
  }),
  zen: Object.freeze({
    armPairs: 3,
    model: 'roster/zen/tentacle/model-rigged.glb',
    chains: ['LeftShoulder', 'RightShoulder', 'T10_UpperArm', 'T11_UpperArm', 'T1_UpperArm', 'T2_UpperArm', 'T3_UpperArm'],
    evidence: '109-joint tentacle-form rig: the standard pair plus the five tentacle ' +
      'chains rooted outside the arms (T1/T11 at the left hip, T2/T3 at the left leg, ' +
      'T10 at the head), restructured 2026-11-06 into arm-chain form (T#_UpperArm roots ' +
      'with T#_Hand tip effectors) — 7 arm chain roots. The seven arm-rooted tentacle ' +
      'chains (T0/T4/T5/T6/T7/T8/T9) cannot root at the torso without re-posing his ' +
      'bound clips, so they stay spring chains; the rename touches names only (BIN ' +
      'chunk byte-identical), so ZEN_BUST_OUT / ZEN_IDLE sample exactly as before.',
  }),
});

/* Resolve the effective bt_guard config for a fighter id.
   A fighter's own data may carry a btGuard block (the per-fighter
   data hook): it overrides the shared design field-by-field and may
   set multiArm explicitly. Otherwise the design applies when the
   model-derived table qualifies the fighter. Returns null when the
   fighter has no BT guard (the Tekken-strict default). */
export function btGuardFor(fighterId, charData) {
  const own = (charData && charData.btGuard) || null;
  const derived = BT_GUARD_MULTI_ARM[fighterId] || null;
  if (!own && !derived) return null;
  const cfg = { ...BT_GUARD_DESIGN, ...(own || {}) };
  cfg.multiArm = own && own.multiArm != null ? !!own.multiArm : !!derived;
  if (derived) { cfg.armPairs = derived.armPairs; cfg.modelEvidence = derived.evidence; }
  return cfg.enabled && cfg.multiArm ? cfg : null;
}
