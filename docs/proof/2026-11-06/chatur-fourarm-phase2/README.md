# Chatur four-arm Phase 2 proof — 2026-11-06

Live serve-harness fight, Chatur vs Pantera (frozen AI, grounded
resets), headless Chromium, tools pattern = combat_inputs.

- Ambient life: her stance carries the Kuma t3 stance clip on the
  secondary (waist) chain — logged at bind; the waist hands pose at
  [-3.345, 1.026, -0.091], distinct from bind pose and from the
  Phase-1 self-fill pose.
- Composite two-hit: '2' (Second Mudra + Kuma row 130 layer) drops
  the opponent in TWO steps (100 -> 92.8 -> 79.5); the engine logs
  'second-pair contact — 6 dmg from arm2R'.
- Dedicated second-pair moves fire from their own inputs with the
  donor clip on the waist chain: Low Offering (f+2+3, Kuma 219,
  100 -> 85.5), Gate Piston (b+1+3, Gun Jack 248, 100 -> 75.8),
  Procession Lariat (d+2+4, Armor King 220, 100 -> 83.1).
- First-use rule (engine-honest): the first use of a donor bank in
  a match plays unlayered while the bank loads and the layered
  variant builds; layered from the next use on.
- The still (chatur-layer2-lariat-20261106.png) shows Chatur
  mid-lariat. The harness renders her blown-out white (known
  harness lighting state, same as Cyborg X in #1604); her GLB
  renders with correct dark skin in Blender. Playtest re-check
  owed on the owner's device.

Full numbers: probe-results-phase2.json. Phase 1 proof lives in
../chatur-fourarm/.
