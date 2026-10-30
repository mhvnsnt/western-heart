# Top-10 industry standards plan (2026-10-28)

Owner order (t288): reverse engineer the top industry standards and fully wire them, starting with combat and hurt reactions, until 100% of Tekken 7 is covered.

Sources: public docs, open-source code, and data the owner owns (T7 movesets/frame data in private GRE, loaded via `__WH_PRIVATE_ASSETS`). No decrypting closed hosted software. No raw T7 assets on public Pages. Arena sky/colors/lighting untouched; no model cuts.

Order = playability first. One PR per item, merged when clean + green + no deletions.

| # | Standard | What we adopt | WH today | Wire target / done-when |
|---|---|---|---|---|
| 1 | **Tekken 7 move properties + hit/hurt reaction tables** (owner-owned motbin data, tkdata public frame data) | Per-move hit level (h/m/l/SM), on-hit/on-block/on-CH frames, reaction id (stagger, crumple, launch, tailspin/screw, wall splat, knockdown face-up/down, spin) driving the victim's state + reaction clip | Partial: `game/js/t7-frame-data-loader.js`, `frame-tables.js`, `t3-reaction-select.js`, `combat-systems.js` | Every hit resolves a T7 reaction id -> victim state machine -> reaction clip; e2e proves each reaction class fires |
| 2 | **Capcom/Namco hitstop + pushback + block/hit stun standard** | Fixed hitstop per strength, pushback distance on hit/block, stun frames from table, wall-aware pushback | Partial: hitstop in `combat-systems.js`/`fighter.js`; pushback only in `game/netplay/sim/fighter-sim.js` | Live fighter uses the same pushback as netplay sim; frame-advantage test matches table +-1f |
| 3 | **Deterministic fixed-step sim (60 Hz) + GGPO-style rollback** | Accumulator loop, integer-frame state, save/load state, input delay + rollback | Partial: `game/netplay/rollback.js`, `game/netplay/vendor/lite-rollback`, `replay.js` | Combat runs at fixed 60 Hz in offline + online; replay determinism test (same inputs -> same hash) |
| 4 | **Fighting-game input buffer / command interpreter standard** | 8-frame buffer, motion leniency, just-frame windows (EWGF), chord windows, negative edge, crouch-dash/wavedash, sidestep/backdash | Partial: `game/js/input.js`, `test/input-timing.test.mjs`, `tools/input-verify/buffer-test.mjs` | Every T7 notation token parses and executes (moveset sweep owns per-move proof) |
| 5 | **three-mesh-bvh swept hit detection (hitbox/hurtbox)** | Per-limb capsules swept between frames so fast moves never tunnel; hurtbox shrink for crouch/airborne/power-crush | Present: `game/js/hitdetect.js`, `hitbox.js`, `game/lib/hitbox.js` | Sweep test: 0 tunnelling at 60 Hz; high attacks whiff crouchers |
| 6 | **Physics-blended hit reactions (Euphoria/PuppetMaster-style, Rapier)** | Animated pose + Rapier active ragdoll blend on impact, KO ragdoll, wall/floor contact | Partial: `game/js/ragdoll.js`, `game/lib/ragdoll.js` (Rapier), `grab-hold.js` | Impulse-scaled partial ragdoll on heavy hits, full on KO, recover to anim; never through floor |
| 7 | **Retargeting pipeline (Mixamo/Rokoko/Cascadeur-style)** | One canonical skeleton; T7/VF5/OSS clips retargeted with IK foot/hand fix | Partial: `tools/retarget/`, `tools/moveset-merge/` | Every moveset clip plays on every roster rig without foot slide |
| 8 | **Motion matching / animation blending (UE5-style)** | Pose-search for locomotion + reaction transitions, inertial blending | Missing (only a mention in `movesets.js`) | Locomotion + reaction exits chosen by pose match; no pops >1 frame |
| 9 | **Behavior tree / utility AI (Yuka)** | Frame-data-aware CPU: punish, whiff-punish, sidestep, throw-break, tech | Present: `game/js/ai.js`, `game/js/ai/*` (mcts, reversal, frame-data), Yuka tests | CPU punishes unsafe moves from table; difficulty curve |
| 10 | **Playwright e2e + automated combo solver** | e2e for every system; solver that searches the move graph for legal juggles and verifies them in-engine | Present e2e: `test/e2e/combat-inputs.e2e.mjs`; solver missing | Solver emits top combos per fighter; e2e replays them |

## Coordination
- Full per-move sweep: `grok/moveset-sweep-20261028` (do not touch).
- Zen/Dural gap fill: `grok/zen-dural-throws-20261028` (do not touch).
- This plan wires systems; the sweep proves moves.

## Blocker at time of writing
Box disk had 2.3 GB free (rule: keep >= 8 GB). A full game worktree is ~13 GB, so Step 2 (in-engine wiring with e2e proof) waits for the owner's yes to free space (e.g. remove merged `wt-combat`, extract + delete `t7p1P`).
