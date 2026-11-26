# Western Heart — God Within mode (branch `godwithin/wiring-20261126`)

Owner order 2026-11-26 (reinforced 09:34 CST): "Get it fully into the repo
and wired up into God within mode how it should be and built with our
characters and environments and Canon." Done-state (owner restatement):
the game loads God Within mode FROM THE REPO with no outside file.

**Status: BUILT on this branch, NOT merged — the owner decides merges.**
Branch: `godwithin/wiring-20261126` in `mhvnsnt/western-heart`, from main
`d65c53a9557942d8aac658e902f4fb9b4d2085d1`. No merges, no PRs from this lane.

## What plays end-to-end

Menu → mode → stage → fight → death → dream/voyage → face-pick → next life:

1. **MENU** — Main menu → story submenu → **GOD WITHIN** card
   (`game/js/mainmenu.js`, action `mode-godwithin`).
2. **SELECT** — Pick any GLB-backed roster fighter (83 of 85).
   `byou` + `ryuji` are never offered — they have no GLB.
3. **RUNG** — Seven rungs (`GODWITHIN_RUNGS` in `game/js/godwithin.js`):
   five Devil Within chapters, the Trader's rung, the final Shrine.
4. **FIGHT** — Trial fight with the DW base kit (punch/kick/block/jump/
   throw, launcher, L1 5-hit combo, rolls), Soul Surge transform, and
   shard pickups. The foe is the rung's next undefeated anchor
   guardian, then the chapter boss (DW boss *behaviour* on a WH body).
5. **DEATH** — Loss increments deaths and runs the between-lives
   sequence (NOT straight to reincarnation):
   - **DREAM** — one LSD dream night (`DreamSys.startDay()` on the
     shipped dream system; day-end minimum 20 shards, the
     `dream.html` rule). Skipped, never blocking, if its data/module
     fails.
   - **VOYAGE** — a SAIL button on the reincarnation screen mounts
     the Banabana hub overlay (`game/js/rolypolys-hub.js`): area →
     region → scene, one item per scene, 288 scenes, winnings pay
     Soul Shards to the shared wallet.
   - **FACE-PICK** — the reincarnation screen's face strip becomes
     the RNF ritual: pick each piece (eyes/nose/mouth); the assembly
     is scored against the chosen vessel's TRUE face. Art 50 = TRUE
     face (briefing + 500-shard bonus); 40 = offered; 30 = wearable
     copy; below 30 = not offered.
   - **REINCARNATE** — vessel cards from the FULL 83-fighter pool
     (`chooseGodwithinVessels` — explicit affinities score; the other
     49 fighters get the documented neutral fallback of all .3, not
     invented per-fighter stats). Diablo gated at 3+ deaths.
6. **NEXT LIFE** — Same rung, new vessel, forces carried over.
   Cleared guardians/bosses persist across deaths.
7. **SHRINE** — Final rung vs the Assembled Soul. Win: 100,000-shard
   completion payout (owner-adjustable), ending, and the Sky note.

The "Heart and Mind Within" brawler (`game/js/brawler.js`) stays the
free-roam companion: God Within fights are Trial fights with the DW
kit/surge/shard rules; the clear screen points at the brawler on the
main menu ("descend again, free-roam, same soul").

## Reskin map as implemented (source → WH)

### 5 Devil Within chapters → WH stages + 12-anchor guardian map

| DW stage (on-disk dir) | WH stage | Anchors → guardians | Boss reskin (DW behaviour, WH body) |
|---|---|---|---|
| lab_A — G Corp Lab | HELIX PALACE | PYRAMSTP→TOU, TAJI→SHA (SAKU RA vessel), STPAUL→SKULL | Modified Gun Jack → SAM-UR-A1 |
| lab_B — Deeper Lab | CENTRAL MOUNTAIN (host: Octagonal Shrine) | PYRAMID→RETSU, SHRINE→ZEN | Clone-Heihachi ×3 → three GYOU |
| egy_A — Ancient Ruins | OCTAGONAL SHRINE | GODDESS→SAKU RA, PRAYER→RAVE (BYOU stand-in) | True Ogre → DIABLO |
| blu_A — Mystical / alien ship | PALACE OF DREAMING | NASKA→PHANTOM, TENG→GYOU | Soul Sphere → PHANTOM |
| blu_B — Final arena | THE TRIAL / FINAL SHRINE (host: Tong-Nou) | DEVIL→DEMONIO, BIGHEAD→DIABLO, PYRAMSUN→PANTERA | True→Monstrous Ogre → DEMONIO (shared-health-bar transform) |

Guardian rooms are data in two places (kept in sync):
`game/js/godwithin.js` (`GODWITHIN_ANCHORS`, `GODWITHIN_CHAPTERS`) and
`game/js/stages.js` (`GODWITHIN_GUARDIAN_ROOMS`).

### Urban Reign / Redux + Def Jam systems (data, WH-native)

- **UR/Redux (10 rows in `GODWITHIN_COMBAT.urbanReign`)**: street brawls
  at Phantom Marketplace / Plains of Chi-U; co-op up to 8 in arena
  brawls; Redux guest slots become WH slots (Yoshimitsu's → JIN +
  PHANTOM, Jin's → RIN — no Tekken character appears); grounded-idle /
  skeleton fixes; Eastern Mind texture pass; Mod Pack + Stage/Fighter
  Editor patterns (WH-original, Redux as reference); the Redux stage-1
  door bug becomes the WH rule — **the door DOES block until the room
  is cleared** — and the regression test.
- **Def Jam (8 rows in `GODWITHIN_COMBAT.defJam`)**: Vendetta grapple
  chains (TOU / PANTERA / RETSU lead); crowd as stage hazard; FFNY
  5-style pick-3 structure as WH style schools (TOU Streetfighting +
  Kickboxing, RETSU Kickboxing + Martial Arts, PHANTOM Martial Arts +
  Submission, GYOU Martial Arts + Streetfighting, RAVE Submission +
  Martial Arts, KAI Wrestling + Streetfighting, ZEN Submission +
  Martial Arts, SAKU RA Martial Arts + Submission, RIN Streetfighting
  + Martial Arts); WH stage weapons; CAW *structure* for WH customs
  (no Def Jam character creatable); 48-venue structure mapped onto WH
  stages. **Def Jam Icon is EXCLUDED** — no decomp/recomp exists
  anywhere; owner call (gap GW-5).
- **DW combat (7 rows)**: base kit, Devil Gauge → Soul Surge,
  blue/red gems → blue/red Soul Shards, points/rank → shards + Rank S
  multiplier, third-person follow camera, blocking door.

### Sato layers → mode entry points

| Sato layer | Entry point in God Within mode |
|---|---|
| The Trial spine | The mode itself — the 7-rung ladder |
| Roly-Polys voyages between deaths | SAIL button → Banabana hub overlay (ported slice) |
| RNF face-pick | Interactive face strip on the reincarnation screen |
| LSD dreams between lives | One dream night on every death |
| Planetokio sky layer | **GATED — data + entry points only** (see gaps) |
| Trader / shards economy | Shared WHIdentity wallet; Trader rung; slot (3-of-a-kind 10×, 2 pays 2×) + Chō-han; forces bought with shards, never won on a machine |

## Playable characters (verified GLBs only)

**Full pool: 83 of 85 roster fighters.** Verified 2026-11-26 by live
HEAD checks against the Worker remote base + the R2 upload manifest
(2,242 models) + the git tree at `d65c53a9`.

Featured cast (16 playable + Trader as NPC host):

| Fighter | Model key | GLB (as authored) | Verified |
|---|---|---|---|
| RIN | demonio-a1 | ../roster/demonio/attires/attire1/model.glb | R2-200 |
| TOU | tou-body | assets/models/tou-soul-tex.glb | in-tree blob + jsDelivr-200 |
| SAKU RA | saku-ra | ../roster/sakura/attires/attire1/model-rerig.glb | R2-200 |
| KAI | kai-body | assets/models/kai-soul-tex.glb | in-tree blob + jsDelivr-200 |
| PHANTOM (JIN's blade) | phantom | ../roster/phantom/attires/attire1/model-rerig.glb | R2-200 |
| RETSU | retsu-body | assets/models/retsu-body.glb | in-tree blob + in-manifest |
| ZEN | zen | ../roster/zen/attires/attire1/model-rigged.glb | R2-200 |
| GYOU | gyou-attire1 | ../roster/gyou/spirit-body/model-gamerig-cdn.glb | via spirit-form alt (R2-200 + in-manifest) |
| PANTERA | pantera-leoman | ../roster/pantera/attires/leomon/model.glb | R2-200 |
| DEMONIO (+winged/human) | demonio-a1 | ../roster/demonio/attires/attire1/model.glb | R2-200 |
| SKULL | skull | ../roster/skull/attires/attire1/model-rerig.glb | R2-200 |
| SAM-UR-A1 | sam-ur-a1 | ../roster/sam-ur-a1/attires/attire1/model-rerig.glb | R2-200 |
| DIABLO | diablo | ../roster/diablo/attires/attire1/model-rigged.glb | R2-200 |
| NIGHTWOLF | nightwolf-attire1 | ../roster/nightwolf/attires/attire1/model-rigged.glb | via base key assets/models/nightwolf.glb (in-tree + in-manifest) |
| DXMMII | dxmmii-tripo | ../roster/dxmmii/attires/attire1/model-rigged-cdn.glb | via base key assets/models/dxmmii.glb (in-tree + in-manifest) |
| MEGAMI | megami | ../roster/parvati/attires/attire1/model-rigged-cdn.glb | via non-cdn R2 filename (R2-200 + in-manifest) |
| TRADER | — | — | NOT rostered — economy host / NPC only |

**Unplayable, exact gap:** `byou` + `ryuji` — `model: null`,
`modelPending: true` in `roster-full.js`, no GLB anywhere. Never
invented. PRAYER's room is guarded by RAVE (Byou's replacement
vessel) until a BYOU GLB lands.

**Hosting truth (corrects the "83 resolve to MODEL_URLS" shorthand):**
no `roster/` GLB directory exists in the WH git tree (0 paths).
Roster GLBs live in the private B2 bucket behind the Cloudflare
Worker remote base (`game/js/asset-config.js`, owner 2026-10-31
no-card route); `assets/models/*.glb` are in-tree blobs. jsDelivr
200/403 responses for `roster/` paths are STALE CACHE (the files are
not in the tree) and were NOT trusted as verification. See gaps
GW-7, GW-7b, GW-8, GW-19, GW-20.

## Files on this branch

| File | What it is |
|---|---|
| `game/js/godwithin.js` | The mode module (pure, node-testable): chapters, anchors, rungs, combat tables, RNF, sky, economy, featured cast, run state machine, flow, gaps GW-1–GW-21 |
| `game/js/modes.js` | Wiring: import, `MODE_LIST` godwithin entry, `startMode` hint, `onConfirm` branch, `_godwithinStageIntro/_godwithinFight/_godwithinEnd/_godwithinBetweenLives/_godwithinComplete`, Trader routing, reincarnate full-pool picks + interactive RNF face strip + SAIL button |
| `game/js/mainmenu.js` | GOD WITHIN card (story submenu) |
| `game/js/main.js` | Delegated data-action router: `mode-godwithin` → `startMode('godwithin')` (without this branch the card would be dead — the same gap the pre-existing `mode-heartmind` card has) |
| `game/js/stages.js` | `GODWITHIN_GUARDIAN_ROOMS` export |
| `game/js/rolypolys-hub.js` + `game/data/rolypolys-world.js` + `test/rolypolys-hub.test.mjs` | Banabana hub, ported byte-identical from the Sato phase-2 slice (`_sato-wh-minigames-20261120/phase2-rolypolys-world-hub`) |
| `test/godwithin.test.mjs` | 17 tests (pure node, CI pattern) |
| `test/e2e/godwithin.e2e.mjs` + `.github/workflows/game-checks.yml` (`godwithin-e2e` job) | God Within tap-path e2e on ubuntu-latest + Playwright: menu → GOD WITHIN card → pantera → rung-1 guardian fight → lose → dream → reincarnate (RNF strip + SAIL) → Banabana sail → reborn same rung, new vessel; shots uploaded as `godwithin-shots` |
| `docs/GOD-WITHIN.md` | This file |
| `docs/DREAM-SYSTEM-LSD-CORE.md` | One-line fix: the LSD slice is merged on main (was "unmerged") |

## Proof

- `test/godwithin.test.mjs`: 17/17 pass locally (`node
  test/godwithin.test.mjs`); `test/rolypolys-hub.test.mjs` passes
  (7 areas, 40 regions, 288 scenes).
- CI: `.github/workflows/game-checks.yml` (`rig-guard` job) runs
  `for t in test/*.test.mjs; do node "$t"; done` on ubuntu-latest
  (GitHub-hosted) — the branch run is the proof gate. The
  self-hosted runner oracle-ppp is OFFLINE since Nov 23 (infra, not
  code) and was NOT relied on.
- Live playtest frames/video: NOT captured in this lane (Chromium
  SIGTRAP-broken box-wide; no live-browser step available to a
  subagent). The God Within tap-path e2e above (`godwithin-e2e` job)
  is the capture route: it runs the full flow on a GitHub-hosted
  runner and uploads `godwithin-shots` (menu card, stage intro,
  fight, reincarnate, Banabana hub, reborn intro) as its artifact.
  Until that job is green and its shots viewed, **no playtest is
  claimed that was not viewed.**

## Exact gaps (full list in `game/js/godwithin.js` GODWITHIN_GAPS)

GW-1 BYOU no GLB · GW-2 RYUJI no GLB · GW-3 EM_FACE art missing from
repo (reincarnation face images 404) · GW-4 RNF manual PDF missing
(true-face triples provisional; faces 10–12 proposals) · **GW-5 Def
Jam Icon — OWNER CALL** · GW-6 Planetokio discs not staged in WH
(sky gated) · GW-7 GYOU roster key 404 on R2 (plays via spirit-form
alt) · GW-7b NIGHTWOLF/DXMMII attire keys 404 on R2 (play via base
keys) · GW-8 roster GLBs live in the B2 bucket, not the git tree ·
**GW-9 Redux 24-part shape — OWNER CALL** · GW-10 FFNY v1.2.0 GA
refresh owed · GW-11 Vendetta 782-vs-783 blob gap · GW-12 DW 2-player
co-op unverified (single-player only) · GW-13 Def Jam parts catalog
not re-verified · GW-14 5 shell minigames + 2 mazes (rules in .DXR)
· GW-15 sparse ISO + disc part_00 files gone from disk · GW-16 Sato
scans RAR tail + manual + art book + OST never landed · GW-17 Trader
not a roster fighter · GW-18 KUTZ/REALIZZT not rostered · GW-19
MEGAMI `-cdn` key suffix looks stale (file on R2 is non-cdn) ·
GW-20 TOU/KAI soul-tex GLBs not in the R2 manifest. ·
**GW-21 STORY stage intro is a dead end on main (found by the
godwithin-e2e, C9 run 45865036342 — OWNER CALL whether to fix)**:
`_storyStageIntro` (modes.js:846) calls `show('stage')`, which shows
CHOOSE YOUR ARENA (`#screen-stage`); its CONFIRM is a no-op without
a versus `pendingFight`, and the intro text + ENTER button live on
the hidden `#screen-stage-intro` panel that nothing ever shows
(`show('stageIntro')` has zero callers on main). The Trial cannot
reach its first fight through the UI. God Within had the identical
line (`_godwithinStageIntro`, modes.js:936, inherited from the story
pattern) — fixed on this branch to `show('stageIntro')` so the rung
intro panel + ENTER button actually display. STORY itself is left
untouched here for the owner's call; the one-word fix is the same
(`_storyStageIntro`: `show('stage')` → `show('stageIntro')`).

## Screen art pass (2026-11-26 — owner direction)

Owner, on the CI shots: the menus and screens were "too much like text
dumps — they need art, UI art, menu art, stuff that makes them feel part
of the game." The reincarnate screen is "one of the most important
screens and mechanics and systems of our game." This pass: art first,
text second, fighting-game layout (Tekken-style), phone-width clean.

### Art map (all art is the game's own, except the sea — noted)

| Screen | Art | Source |
|---|---|---|
| Reincarnate hero banner | Lantern shrine at dusk | `game/assets/stages/thumbs/shrine.png` (repo stage thumb) |
| Stage intro ch. 1 Helix Palace | `helix-palace.png` | repo stage thumb |
| Stage intro ch. 2–3 Mountain/Shrine | `octagonal-shrine.png` | repo stage thumb |
| Stage intro ch. 4 Palace of Dreaming | `palace-of-dreaming.png` | repo stage thumb |
| Stage intro ch. 5 Final Shrine | `shrine.png` | repo stage thumb (`tong-nou.png` is an unusable black void) |
| Stage intro Trader rung | `phantom-marketplace.png` | repo stage thumb |
| Banabana hub header | Banabana crossing the violet sea at dawn | NEW key art, `game/assets/godwithin/banabana-sea.png` (generated 2026-11-26 — no sea art exists in the repo) |
| STORY rail GOD WITHIN card | `shrine.png` thumb strip | repo stage thumb |
| Face strip / vessel portraits | Eastern Mind D_FACE bitmaps / `assets/portraits/*.png` | original game art / repo portraits (unchanged) |

### What changed (files)

- `game/godwithin-art.css` (new): art banners, chips, VS rows, VS
  splash, hub shell, mode-card thumbs. The hub's `.wh-btn` /
  `.wh-row` / `.wh-input` / `.wh-dice` had NO styles anywhere in the
  game CSS — hub buttons rendered as native white buttons; defined
  here, scoped to `.gw-hub`.
- `game/index.html`: art banner slots on stage-intro + reincarnate,
  subline + dream chip on reincarnate, `#stage-foe` is a `<div>` now
  (it holds the VS row), `#gw-vs` VS-splash overlay.
- `game/js/modes.js`: draft copy (below); stage art per chapter;
  reward as two chips; opponent as a VS row (vessel vs guardian);
  SAIL is a primary `.gw-sail` button; VS splash ~1.4s before
  ROUND 1 (defensive — any failure starts the fight at once);
  MODE_LIST desc trimmed to one line. STORY's `_storyStageIntro`
  untouched (GW-21, owner's call) — the stage-art banner stays
  hidden there.
- `game/js/mainmenu.js`: GOD WITHIN card gets its shrine thumb +
  one-line desc.
- `game/js/rolypolys-hub.js`: sea-art header replaces the long Ship
  paragraph; progress line tightened to one line. All hub ids kept.
- `test/e2e/godwithin.e2e.mjs`: asserts the new copy + art anchors
  (CHOOSE A FACE, dream chip, shrine banner, Helix art on reborn,
  solid `#070714` hub overlay, sea-art header).

### Ghost-text fix (hub)

The Banabana hub overlay was `rgba(5,5,12,0.92)` — 8% transparent,
so the reincarnate screen ("DEATH IS NOT THE END", flavor, face
strip) bled through behind the hub. The overlay is solid `#070714`
now (`gw-hub-overlay`), and the hub carries its own `#070714`
background. Proven by the 06 shot in CI.

### Draft copy (owner's rewrite pending — NOT final)

- Reincarnate title: **DEATH IS NOT THE END** (kept). Subline:
  *It's just a new beginning.*
- Body: "You fell. The fight goes on. Dream tonight, wake in a new
  body, and take the rung back."
- Dream chip: "Dreamed — Day 1, Palace of Dreaming · +20 shards from
  the dream" (day/stage/shards are live values).
- Face-pick: "CHOOSE A FACE" / "The soul remembers, the body is
  new." / "PICK EACH PIECE (RNF)".
- Vessel: "YOUR NEXT VESSEL AWAITS — PICK ONE".
- Stage intro: chapter title kept; sub kept (one line); reward as
  chips (CLAIM … + ◆ N SOUL SHARDS); opponent as VS row.
- MODE_LIST / STORY card: "Five chapters. Twelve guardians. Death
  is not the end — it is a new beginning."

## Sources / licences (honest log)

- Devil Within spec: `mhvnsnt/game-reverse-engineering`
  `tekken5/TEARDOWN-DEVIL-WITHIN.md` + GameFAQs CJ800 v2.30a;
  recomp pipeline verified headless (t5-headless sha
  `978c782d…`, 6 playtests, unknown 0); upstream devilwithin-coop
  still WIP.
- Urban Reign recomp v1.4.1: GPL-3.0 (thiagordsfx).
- Def Jam Vendetta recomp v0.7.3: GPL-3.0 (jcsix694).
- Def Jam: Fight for NY recomp v1.2.0-beta: MIT (vyanhursky);
  modding tools MIT. GA v1.2.0 refresh owed.
- Urban Reign Redux v0.5: NO licence declared (Jasonafex);
  release `urban-reign-redux-20261120`, whole sha `ad222bad…`.
- LSD dream core: klnuno/lsd-decomp (MATCHING decomp) as truth;
  TheShovel/lsd-dream-emu-ds JS port (no licence declared;
  upstream Revamped MIT). WH data WH-authored.
- Roly-Polys World Tour disc catalog: Sato slice, WH-native build.
- RNF mechanic: `RHYTHM-N-FACE-MECHANIC.md` spec; manual PDF missing.
- No Sato / Def Jam / Urban Reign character or place is cloned.
  No code was copied from the recomps into WH — WH-native
  implementations of the systems, WH characters only.
