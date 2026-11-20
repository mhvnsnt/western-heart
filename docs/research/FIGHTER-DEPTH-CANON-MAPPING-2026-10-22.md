# FIGHTER DEPTH + LEARNING + STAGE LIFE — Canon Mapping
**Worker 34 · 2026-10-22 · for owner approval**

Every system below was pulled from the teardowns first, then mapped into the
Western Heart universe. **Mechanical pulls are done; the NAMES and identity
framings marked [NEEDS APPROVAL] are creative calls for the owner.** Nothing
marked [NEEDS APPROVAL] is presented in-game as canon until approved.

Canon sources: `CANON.md` (Tong-Nou, Nine Souls, Five Lands, the Trial, the
Trader, Reincarnation), owner directives in `docs/owner-directives.md`,
intake canon (MEMORY.md 2026-10-22), `game/js/intro-interactions.js`
(worker 13), `game/js/modes.js` (Soul Surge blessings).

---

## 1. Ki charge → "SOUL KINDLE" [NEEDS APPROVAL]

**Teardown pull:** Tekken 7 Ki Charge — press 1+2+3+4; the fighter glows;
the next landed hit is a guaranteed counter-hit; the kindled fighter takes
+10% damage and cannot block during the charge flash. (`game/js/soul-kindle.js`)

**WH identity (proposed):** the vessel focuses its OWN soul fragment's nature
before striking — TOU burns brighter, RIN grows colder, BYOU moves wronger.
The glow is the soul fragment showing through the vessel.

**Canon collision to resolve [NEEDS APPROVAL]:** three soul-power systems now exist —
- **Soul Kindle** (this work — T7 ki charge: brief, next-hit-CH, self-focused);
- **Soul Surge** (CANON.md Nine-Soul Meter: channel one of the OTHER eight souls, 10s);
- **Soul Urge** (owner-locked 2026-10-22: Tekken 8 Heat renamed).

Proposed reading: Kindle = your own soul focused (seconds, one hit); Surge =
another soul channeled (10s, canon); Urge = the T8 Heat-state renamed.
**Owner call:** keep all three distinct, or merge Surge/Urge?

## 2. Tag throws / crash / assault → "SOUL RELAY" [NEEDS APPROVAL]

**Teardown pull:** Tekken Tag Tournament 2 — raw tag (5, punishable), Tag
Assault (partner continues your combo), Tag Crash (partner takes your juggle
as red health), Tag Throw (tandem throws), red-health regen on the tagged-out
partner. (`game/js/tag-relay.js`)

**Coordination:** worker 24's TTT2 team-battle lane owns the 2v2 match
structure (not on main yet). This module is the MECHANICS layer — worker 24
should call `TagRelay`/`TagTeam`, not reimplement tag state.

**WH identity (proposed):** partners are soul-fragments of one being relaying
vessels mid-trial. Canon precedent: SHA's three-way split (Saku Ra / Kinpo /
Awa Pop — *"when one is hurt, the other two feel the grain shift"*) and KAI's
two moods (King Tyrant / Star). Proposed names: **Relay Assault / Relay
Crash / Relay Throw** under the **Soul Relay** banner. [NEEDS APPROVAL]

## 3. Hair + cloth physics → (tech, no canon name)

**Teardown pull:** DOA/SF cloth-sim approaches. The teardowns document the
design (soft-body secondary motion) but no implementation-level cloth code
survived extraction — so this implements the industry-standard approach
those games use, browser-adapted: verlet particles + distance constraints
(DOA-soft-engine family), bone-chain verlet for hair (DynamicBone-style),
analytic sphere colliders, LOD sleep, particle budgets. (`game/js/cloth-hair.js`)

**Pipeline wiring:** tag meshes in Blender with custom property `wh_cloth` →
glTF extras → `THREE.userData.whCloth` → `autoAttachCloth(scene)`.
Documented in the module header; no canon identity needed (it's craft, not lore).

## 4. Combo trials → "TRIAL INSCRIPTIONS" [NEEDS APPROVAL]

**Teardown pull:** Tekken combo/punishment trials — per-character scripted
notation sequences, step validation, PERFECT/GOOD/LATE timing grades,
progressive difficulty, persisted completion. (`game/js/combo-trials.js`)

**WH identity (proposed):** the TRIAL itself teaches. The trial is inscribed
in stone (*"Fight. Die. Return. Claim the forces. Forge the katana. Become
whole."*) — the shrine stones show each vessel its own techniques, then test
them. Narrator: stone-text in Sato's deadpan register (canon's last card:
*"You are whole. Rest now."*). **Alternative:** Megami (trained Chatur) as the
in-universe master. [NEEDS APPROVAL on teacher: the Trial vs Megami]

## 5. Ghost AI → "SOUL ECHOES" [NEEDS APPROVAL]

**Teardown pull:** Tekken 6 / TTT2 / VF ghost AI — record (situation,
action) pairs, per-situation histograms with smoothing, temperature sampling
blended with a base policy, named persistent ghosts. (`game/js/ghost-ai.js`)

**WH identity (proposed):** echoes of past vessels. Reincarnation (CANON.md):
*"the soul that loses and returns is not the soul that fell"* — the fallen
version's echo remains, still fighting in the head-world. The Assembled Soul
(*"moves like Pantera, strikes like Demonio..."*) is the ultimate echo.
Ghost battle = sparring your own echo. [NEEDS APPROVAL]

## 6. Replay analysis → "TRIAL REVIEW" [NEEDS APPROVAL, minor]

**Teardown pull:** replay theaters + community frame-data analysis —
accuracy, punish rate, whiff rate, throw breaks, combo damage, missed-punish
detection, findings ranked by severity. (`game/js/replay-analysis.js`)

**Coordination:** worker 29's replay capture/playback has NOT merged to main.
This module defines the **REPLAY EVENT CONTRACT v1** it analyzes; worker 29's
recorder should emit these events (or a superset) — the analyzer plugs in.

**WH identity (proposed):** the Trial shows you where you fell — *"It is not
an invitation. It is a diagnosis."* (CANON.md). [NEEDS APPROVAL — minor naming]

## 7. Stage intro camera sweeps → "LAND REVEAL" [NEEDS APPROVAL, minor]

**Teardown pull:** Tekken 7 / TTT2 stage intros — keyframed cinematic sweep
(pos + lookAt + fov, eased, ~4s, skippable) before control hands over.
Per-land authored paths: Chi-U sweeps low past the flames, Dreaming drifts,
Helix spirals down, Tree of Life rises through branches, Shrine pushes in
reverent and still. (`game/js/stage-intros.js`)

**WH identity (proposed):** the land introduces itself before the Trial
begins — each of the Five Lands shows its nature. [NEEDS APPROVAL — minor]

## 8. Weather / time-of-day variants → per-land elemental variants [NEEDS APPROVAL]

**Teardown pull:** T7/TTT2/SC6 stage variants — same arena re-lit and
re-dressed as separate select entries; variants are data layered over the
base stage def (lighting overrides in the stages.js schema + weather
particles). (`game/js/stage-variants.js`)

**WH identity (proposed):** variants tied to each land's ELEMENTAL identity
(the five lands each hold one of the five elemental forces):
- TREE OF LIFE (Wood) — Dawn Mist / Golden Hour / Night Bloom
- PLAINS OF CHI-U (Fire) — Burning Noon / Ash Dusk / Ember Night
- OCTAGONAL SHRINE (Earth) — Stone Dawn / Starfall Night
- HELIX PALACE (Metal) — Mirror Noon / Neon Night / Chrome Dawn
- PALACE OF DREAMING (Water) — Rain / Storm / Moonlit Tide
- PHANTOM MARKETPLACE — Lamplight / Eyeball Eclipse
- SHRINE OF THE BLADE — Lantern Night

Weather: rain/storm (dreaming), embers/ash (chi-u), petals/mist/fireflies
(tree), motes (shrine/marketplace), sparks (helix), starfall (shrine night).
[NEEDS APPROVAL on the variant list]

## 9. Versus banter → extends worker 13's intro system [NEEDS APPROVAL: pairs]

**Teardown pull:** Tekken pre-fight character interactions — extended with
short, punchy 1–2 beat VERSUS-screen dialogue using worker 13's beat
contract and no-repeat selection. Falls back to `pickIntroInteraction` for
unscripted pairs. (`game/js/versus-banter.js`)

**WH identity:** banter along the owner-approved canon web
(Jotei → Ryusan → Tobi → Pond → Dorowani → Chatur → Megami → Menajerii → Zen).
Only `dorowani` and `zen` are rostered today — their pair is PLAYABLE now;
the rest are staged as data marked `[AWAITING-FIGHTER]` and go live when the
fighters land. Writing rules honored: Dorowani speaks ONLY Japanese word
bursts (owner voice canon); Ryusan (15, owner-authorized minor) written
strictly to the crimes/truth, nothing else; Zen's stillness as a beat.

**[NEEDS APPROVAL]:** the pair list and the lines themselves — creative call.

## 10. Movelist UI → "INSCRIPTIONS" [NEEDS APPROVAL]

**Owner-approved 2026-10-22** (learning tools: YES, ALL). Tekken-style
pause-menu movelist: live from the loaded moveset (never a stale copy),
filter by class, search, sort by damage/startup. (`game/js/movelist-ui.js`)

**WH identity (proposed):** the Trial's stone tablets — the stones SHOW
(movelist) and then TEST (trials). One system, two faces, shared with
Combo Trials §4. Alternative: "Soul Manual". [NEEDS APPROVAL]

## 11. Special Style → "GUIDED HANDS" [NEEDS APPROVAL]

**Owner-approved 2026-10-22.** Teardown pull: Tekken 8 Special Style —
one-button curated strings, simplified inputs for new players; throws stay
manual. (`game/js/special-style.js`)

**WH identity (proposed):** the Trial guides a lost soul's hands — the call
draws every lost soul; the Trial steadies the newest ones until their own
hands remember. Alternative: "Soul Guidance". [NEEDS APPROVAL]

## 12. Punishment training → "SKULL'S LESSONS" [NEEDS APPROVAL]

**Owner-approved 2026-10-22.** Teardown pull: Tekken punishment training —
dummy loops a move, UI shows minus frames, player punishes in-window;
PERFECT/GOOD/MISS/WRONG grades; drill sets per foe. (`game/js/punishment-training.js`)

**WH identity (proposed):** taught by Skull, the Punisher Soul — *"he fights
because the trial provides targets."* The Trial provides the targets; Skull
provides the lesson: every unsafe move gets buried. Alternative:
"Punisher's Rite". [NEEDS APPROVAL]

---

## Approval checklist for the owner

- [ ] 1. Soul Kindle — name + the Kindle/Surge/Urge three-way resolution
- [ ] 2. Soul Relay — name (Relay Assault/Crash/Throw)
- [ ] 4. Trial Inscriptions — teacher: the Trial itself vs Megami
- [ ] 5. Soul Echoes — ghost AI identity
- [ ] 6. Trial Review — name (minor)
- [ ] 7. Land Reveal — name (minor)
- [ ] 8. Stage variant list per land
- [ ] 9. Versus banter pairs + lines
- [ ] 10. Inscriptions — movelist name (vs "Soul Manual")
- [ ] 11. Guided Hands — special style name (vs "Soul Guidance")
- [ ] 12. Skull's Lessons — punishment training name (vs "Punisher's Rite")

## Files

`game/js/soul-kindle.js`, `game/js/tag-relay.js`, `game/js/cloth-hair.js`,
`game/js/combo-trials.js`, `game/js/ghost-ai.js`, `game/js/replay-analysis.js`,
`game/js/stage-intros.js`, `game/js/stage-variants.js`,
`game/js/versus-banter.js`, `game/js/movelist-ui.js`, `game/js/special-style.js`,
`game/js/punishment-training.js`, `game/js/fighter-depth.js` (integration),
`game/tests/fighter-depth.test.mjs` (43 tests, all passing),
this doc: `docs/research/FIGHTER-DEPTH-CANON-MAPPING-2026-10-22.md`.

## Integration notes (for the game wiring lane)

`game/js/fighter-depth.js` exports `FighterDepth` with `onMatchStart(game,
opts)` / `onUpdate(game, dt, pressed)` / combat hooks (`onHitLanded`,
`damageTakenMult`, `canBlock`) / `mapInput` — plus feature flags
`WH_DEPTH_FLAGS` so every system ships and rolls back independently. The
three-line `main.js`/`game.js` hookup is documented in the module header;
left unapplied here to avoid clobbering the fast-moving game files — the
wiring lane (or a follow-up) applies it to fresh main.
