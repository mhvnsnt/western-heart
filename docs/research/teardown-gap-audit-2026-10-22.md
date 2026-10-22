# Teardown Gap Audit — Second Pass (2026-10-22)

**Worker 25 · audit-only · DO NOT BUILD until the user approves.**

Owner directive (verbatim): *"After the jiggle/face/hands wiring is done, do a second teardown audit pass: go back through ALL the teardown files (Tekken 3/6/7/8, TTT2, DOA4/6, SF, SC2/6, Urban Reign, VF5, WWE, Def Jam, No Mercy) and list what else we haven't wired up yet. Report it back for the user's approval before building — same 'here's what we can wire up' format as the mode-mapped audit."*

## How this audit was done

- Read every teardown source dir's summary docs (`TEARDOWN.md`, `WIRING-INVENTORY.md`, mechanics docs, catalogs) at `teardown/` on main @ `822bdcc9` (2026-10-22 18:14 UTC). Teardown reference files were verified unchanged in the audit window via the GitHub compare API.
- Cross-referenced against what's already wired: `game/js/*`, `game/assets/`, `customization/`, `moveset-library/`, `docs/`, plus the merges that landed during the audit window (hit detection + hit FX #616, camera bounds #612, voice pipeline + intro interactions #614, menu load-speed lane, WMXIX/TTT2 lanes, worker 15/16/17/19 work).
- **Excluded (already wired):** Tekken hit detection + hit effects (PR #616), Tekken camera bounds port (#612), voice pipeline + intro interaction system (#614), menu load-speed fixes (lazy.js / loadperf / VGS atlas), TTT2-style team battle mode, T3 motion banks 1–7 + movesets, No Mercy arenas, WMXIX clip/move indexes + mat-legends stages + CAW catalog, SF moveset JSONs (sf-*.json), DOA moveset JSONs (doa-*.json).
- **Excluded (in flight, will be wired):** worker 21 jiggle/face/hands wiring; worker 24 TTT2 work; T8 character-select grid transplant (`docs/select-redesign/T8-GRID-DECODE.md`).
- Items marked **verify** = the auditor couldn't confirm wired/not-wired from the evidence at hand; needs a check, not a guess.

**How to use this doc:** each item has what it adds, why it matters, and a checkbox. Tick OK or leave unticked (= skip). Nothing below is built — approval first.

---

## TEKKEN 3 (`teardown/tekken3/`)

### T3-1. Round-2 movesets: 13 banks, 5,663 move rows
- **What it adds:** Real Tekken 3 movesets for 13 more fighters (banks extracted + SHA-256-verified 2026-10-20; movesets extracted with the teardown's own `moveset_extract.py`). Needs schema-v2 conversion (the PR #243 generator is not in the repo as a runnable script).
- **Why it matters:** Only 7 fighters have real T3 movesets today; everyone else rides proxies. This is the single biggest moveset-fidelity unlock left from T3.
- [ ] OK to wire / [ ] Skip

### T3-2. T3 UI art templates (23 files: title screens, menus, character art, fonts-text)
- **What it adds:** The actual Tekken 3 menu/title/character-art textures as templates for WH UI generation (`teardown/tekken3/ui/`).
- **Why it matters:** The select-screen overhaul lane is rebuilding menus now; these are the authentic layout/art references instead of designing blind.
- [ ] OK to wire / [ ] Skip

### T3-3. Stage metadata JSONs (15 stages: extents, home_stage_of, texture keys)
- **What it adds:** Per-stage metadata the game doesn't read today — arena extents (camera/fight bounds), canonical home fighter, texture keys.
- **Why it matters:** Camera-bounds work (#612) and stage select could consume real per-stage bounds instead of constants.
- [ ] OK to wire / [ ] Skip

### T3-4. Heihachi animation decode (blocked — flagged, not actionable yet)
- **What it adds:** Nothing yet — his KMD part rows 2/9/13 are empty, GLB/bake blocked.
- **Why it matters:** Listed so it isn't mistaken for a wire-up item. Needs a decode fix first.
- [ ] OK to wire / [ ] Skip

---

## TEKKEN 6 (`teardown/tekken6/`)

### T6-1. Customization item tables (decoded from EBOOT: item names + slot categories)
- **What it adds:** Real Tekken 6 customization items — `sbcustomize_item_t` records, item name tables, slot/price/model-ref categories — into the creation suite's parts library.
- **Why it matters:** The suite's customization is being unified right now; authentic T6 item data (not invented items) is exactly what the tool-unification law wants.
- [ ] OK to wire / [ ] Skip

### T6-2. 46 ending videos (on release `tekken6-endings-v1`, 337MB)
- **What it adds:** Every T6 character ending as reference (or direct inspiration) for WH character-episode endings and cutscenes.
- **Why it matters:** Story mode (`episodes.js`) exists but endings are unwritten; these are the real Tekken ending structures to study/convert.
- [ ] OK to wire / [ ] Skip

### T6-3. DATA401 bulk decrypt (blocked — flagged, not actionable yet)
- **What it adds:** T6 models, stages, animations, audio — still locked behind the unknown bulk transform (sector cipher solved; bulk region still random).
- **Why it matters:** Listed so the gap is visible. Needs the decrypt lane to crack it first.
- [ ] OK to wire / [ ] Skip

---

## TEKKEN 7 (`teardown/tekken7/`)

### T7-1. 34-stage ID table → stage expansion
- **What it adds:** The mapped T7 stage roster (IDs, asset prefixes SK/SKT/SM/BP/PA/CS/CCI/CI/T) as the stage expansion list.
- **Why it matters:** Biggest modern stage pool; currently only the ID table exists (geometry needs the full 47GB game).
- [ ] OK to wire / [ ] Skip — **blocked on acquisition** (owner purchase step per `TEKKEN78-ACQUISITION-PLAN.md`)

### T7-2. T7 customization system data
- **What it adds:** T7's customization items/outfits into the suite.
- **Why it matters:** Same as T6-1, modern-era items.
- [ ] OK to wire / [ ] Skip — **blocked on acquisition**

### T7-3. Full per-character T7 movesets (tekkenmods docs exist as reference)
- **What it adds:** Complete modern movesets beyond the 7 T3 banks (the tekkenmods T8 moveset docs were already used for hit detection).
- **Why it matters:** Moveset philosophy = Tekken movelist layouts first, 100% complete. T7 docs are the modern reference.
- [ ] OK to wire / [ ] Skip — **blocked on acquisition** (docs partial only)

---

## TEKKEN 8 (`teardown/tekken8/`)

### T8-1. Heat system (research gap — not documented in teardown)
- **What it adds:** T8's signature Heat mechanic (offense timer, Heat Smash, chip damage) — currently the teardown has only models (King variants, Asuka), no mechanics doc.
- **Why it matters:** If WH wants a modern Tekken layer, Heat is the defining T8 system; right now nobody has documented it for federation.
- [ ] OK to research + wire / [ ] Skip

---

## TEKKEN TAG TOURNAMENT 2 (`teardown/tekken-tag-tournament-2/`)

### TTT2-1. Tag-team combat systems (tag-in/out, tag assaults, tag throws, tag crash)
- **What it adds:** Real 2v2 simultaneous tag fighting. Current `team` mode is Tekken 2-style elimination (3v3, winner stays on) — TTT2's tag mechanics (partner on sideline, tag assaults, tag throws) are a different, deeper system.
- **Why it matters:** TTT2 is the deepest tag fighter ever shipped; its tag grammar is the template if WH ever does real tag.
- [ ] OK to wire / [ ] Skip — **verify:** worker 24's TTT2 work may already cover part of this (no WORKLOG entry found at audit time)

### TTT2-2. 59-fighter roster manifest → reskin/attire pool
- **What it adds:** The biggest Tekken roster ever (documented in `ROSTER.md`) as the reskin-base and alt-costume donor list.
- **Why it matters:** Body-type coverage from Kuma/Panda to Slim Bob to Alisa for future roster expansion.
- [ ] OK to wire / [ ] Skip

### TTT2-3. 29 stages incl. 10 multi-tiered (documented in `STAGES.md`)
- **What it adds:** Stage list with multi-tiered/breakable-floor arenas as the template for WH's federated arena mechanics.
- **Why it matters:** Breakable-floor / multi-tier fights are a marquee arena feature none of our stages have.
- [ ] OK to wire / [ ] Skip

### TTT2-4. Fight Lab / Combot (customizable robot fighter)
- **What it adds:** TTT2's build-your-own fighter (Combot) as a design reference for the creation suite's custom fighter.
- **Why it matters:** The suite already has a WWE-style template flow; Combot is the fighting-game-native version of the same idea.
- [ ] OK to wire / [ ] Skip — **verify** overlap with current create-a-fighter flow

### TTT2-5. Customization data (blocked — 7z reassembly stalled)
- **What it adds:** TTT2's deep customization items — needs the full 13.3GB archive reassembled first (11/26 parts only).
- **Why it matters:** Listed as blocked, not actionable.
- [ ] OK to wire / [ ] Skip

---

## DEAD OR ALIVE 4 (`teardown/dead-or-alive-4/`)

### DOA4-1. 105 carved models (vertex buffers decoded, index buffers NOT decoded)
- **What it adds:** 85 character models + 18 stage models + motion models as GLB point clouds today; needs the index-buffer format cracked to become triangulated surfaces.
- **Why it matters:** Real DOA4 geometry (with 219 carved XPR2 textures) one decode step away from usable.
- [ ] OK to finish decode + wire / [ ] Skip

### DOA4-2. DOA4 fighter movesets beyond Bass
- **What it adds:** Bass's moveset is wired (`doa-bass.json`); the other fighters' move data from the carved animation/motion archives.
- **Why it matters:** DOA4's holds/stuns need the DOA6 systems below, but the raw movesets are the prerequisite.
- [ ] OK to wire / [ ] Skip

---

## DEAD OR ALIVE 6 (`teardown/dead-or-alive-6/` — mechanics documented, no binaries)

### DOA6-1. Triangle system (strikes > throws > holds > strikes)
- **What it adds:** DOA's rock-paper-scissors counter layer ON TOP of Tekken inputs: a new reaction table where hold inputs matched against incoming strikes cancel the strike into a counter.
- **Why it matters:** This is THE DOA federation contribution per the mechanics doc — a whole new decision engine for every exchange, without touching Tekken's input feel.
- [ ] OK to wire / [ ] Skip

### DOA6-2. 4-way hold system (high / mid-punch / mid-kick / low)
- **What it adds:** Direction+hold-button counters matched to strike levels; wrong level = whiffed hold = punished. New "counter" category in the moveset slots.
- **Why it matters:** The deepest defensive mechanic in the genre; maps cleanly onto Tekken's existing high/mid/low tags.
- [ ] OK to wire / [ ] Skip

### DOA6-3. Stun system (critical stun / critical burst / fatal stun + slow escape)
- **What it adds:** Stun as a real state machine: stun depth, slow-escape counterplay (stick spin to recover), stun→launch→juggle as an explicit combo grammar.
- **Why it matters:** Gives WH a DOA-style combo engine layered on Tekken moves — new reaction types, not new moves.
- [ ] OK to wire / [ ] Skip

### DOA6-4. Break gauge (Break Blow + Break Hold)
- **What it adds:** A per-round meter: full-gauge cinematic armored strike (beats highs/mids, breaks throws, loses to lows) or a universal defensive escape from any stun.
- **Why it matters:** A resource layer independent of the triangle — clean gauge + two special move entries. (Check overlap with Soul Surge before building.)
- [ ] OK to wire / [ ] Skip

### DOA6-5. Fatal Rush (universal beginner auto-combo)
- **What it adds:** A canned 4-hit string any character can do (first hit = unholdable fatal stun) — an onboarding tool, deliberately unsafe on block.
- **Why it matters:** Lowest-cost accessibility win in the whole audit; teaches new players the stun game.
- [ ] OK to wire / [ ] Skip

---

## STREET FIGHTER (`teardown/street-fighter-*/`)

### SF-1. SFEX Plus Alpha move data (165 move names + per-character overlays, 100% pulled)
- **What it adds:** Documented Arika move tables (commands, move names, per-character data) to complete SF-based fighters' movesets. `sf-*.json` movesets exist — this fills/verifies them from real data.
- **Why it matters:** Owner law: SF characters keep SF movesets but play like Tekken. Real data > invented data.
- [ ] OK to wire / [ ] Skip

### SF-2. SFEX3 tag-battle system (research reference)
- **What it adds:** Arika's tag mechanics as a second tag reference alongside TTT2 (research-only per the SF federation law — nothing here replaces Tekken systems).
- **Why it matters:** Cheap design input if TTT2-1 is approved.
- [ ] OK to wire / [ ] Skip

### SF-3. SFEX stage packs (8 + 8 stages)
- **What it adds:** 16 Arika stage packs as stage-art reference/expansion.
- **Why it matters:** Stage variety; PS1-era geometry is light enough to convert cheaply.
- [ ] OK to wire / [ ] Skip

### SF-4. Street Fighter V: 34 stages + roster (not pulled — pipeline documented)
- **What it adds:** Modern SF stage pool; pull plan exists (`SFV-PULL-PLAN.md`, FitGirl 26.7GB → TeraBox).
- **Why it matters:** Only if the user wants SFV-era content; blocked on the pull.
- [ ] OK to pull + wire / [ ] Skip

---

## SOULCALIBUR 2 (`teardown/soulcalibur-2/`)

### SC2-1. 8-way run movement
- **What it adds:** Hold-any-direction running as the movement foundation (vs Tekken's step/dash).
- **Why it matters:** SC movement feel is the genre's gold standard for 3D spacing; federates as a movement layer.
- [ ] OK to wire / [ ] Skip

### SC2-2. Guard Impact (parry)
- **What it adds:** Forward+Guard parry that repels attacks and creates advantage.
- **Why it matters:** A Tekken-true game has no parry; GI is the weapon-fighter answer and pairs with DOA6-2's holds as the defensive suite.
- [ ] OK to wire / [ ] Skip

### SC2-3. Ring Out (instant win by knocking opponent out of the arena)
- **What it adds:** Arena-edge instant-win condition + the stage flag (walled vs ring-out-legal).
- **Why it matters:** Changes stage strategy completely; needs the stage metadata (T3-3) to know which arenas allow it.
- [ ] OK to wire / [ ] Skip

### SC2-4. Weapon clash (simultaneous attacks negate)
- **What it adds:** Clash resolution when two attacks land on the same frame.
- **Why it matters:** WH is unarmed-focused, so this is a design question — clash as a universal mechanic or skip.
- [ ] OK to wire / [ ] Skip

### SC2-5. Soul Charge (power-up state)
- **What it adds:** Temporary powered state with new properties.
- **Why it matters:** **Verify overlap** with Soul Surge / Break gauge (DOA6-4) before building — three meter/power systems may be one.
- [ ] OK to wire / [ ] Skip

---

## SOULCALIBUR 6 (`teardown/soulcalibur-6/` — full mechanics federation doc; binary not acquired)

### SC6-1. Guard stamina & guard crush
- **What it adds:** Blocking drains a separate guard-stamina meter; at zero the guard breaks (guard crush = counter-hit punish). Heavy attacks drain more; turtling gets punished, pressure gets rewarded.
- **Why it matters:** A whole defensive-resource layer Tekken lacks — portable as-is (`guard_stamina` 0–100, drain per blocked hit by move level).
- [ ] OK to wire / [ ] Skip

### SC6-2. Guard Impact (modern: +28/+16/+8 reward rule)
- **What it adds:** Timed parry that cancels the opponent's action outright; reward scales by parried move level (light +28 knockdown / medium +16 / heavy +8). Costs guard stamina instead of meter.
- **Why it matters:** The skill-based defensive answer; the level-scaled reward is an elegant portable rule. Supersedes the SC2-era GI (SC2-2) — pick one.
- [ ] OK to wire / [ ] Skip

### SC6-3. Reversal Edge (comeback/clash moment)
- **What it adds:** SCVI's signature slow-mo clash sequence — a comeback mechanic and hype moment generator.
- **Why it matters:** Maps to the Trial narrative (soul-clash moments); the "never been done before" spectacle layer.
- [ ] OK to wire / [ ] Skip

### SC6-4. Soul gauge: Critical Edge (metered super) + Soul Charge (install state)
- **What it adds:** Two-bar meter: 1-bar cinematic super (Critical Edge), and Soul Charge — invincible burst into an enhanced state with exclusive moves, damage boost, chip damage on all attacks, timer stops.
- **Why it matters:** Soul Charge maps directly onto WH's soul-vessel theme (a vessel "charging" their soul). **Verify overlap** with Soul Surge / Break gauge / Special arts — fold into X-2.
- [ ] OK to wire / [ ] Skip

### SC6-5. Lethal Hit (conditional combo starters)
- **What it adds:** Character-specific moves gain enhanced properties + slowdown + combo opportunity when landed under specific conditions (e.g., whiff-punish a GI attempt).
- **Why it matters:** Rewards matchup knowledge and conditioning; portable as conditional move predicates.
- [ ] OK to wire / [ ] Skip

### SC6-6. Move-level taxonomy (light/medium/heavy) + clash rules
- **What it adds:** Damage/frame taxonomy driving GI scaling, guard crush, meter gain, and simultaneous-hit clash resolution (integer comparison, not a coin flip).
- **Why it matters:** The ruleset that makes SC2-4/SC6-2/SC6-1 hang together — adopt the taxonomy and the systems follow.
- [ ] OK to wire / [ ] Skip

### SC6-7. Create-a-Soul ("any style on any body")
- **What it adds:** Design reference: SCVI's CaS proves full moveset assignment from any character's style onto any body works at retail quality.
- **Why it matters:** Direct input to the creation suite's unification work (any-style-on-any-template).
- [ ] OK to wire / [ ] Skip

### SC6-8. Full game acquisition (not acquired — 50GB+, UE4 .pak plan documented)
- **What it adds:** Modern models, stages, internal data structures (FModel supports SCVI).
- **Why it matters:** Can't wire what we don't have; free Steam Workshop model collections are the no-purchase path.
- [ ] OK to acquire / [ ] Skip

---

## URBAN REIGN (`teardown/urban-reign/`)

### UR-1. Brawl mode (4-player free-for-all street brawling)
- **What it adds:** A new mode: multi-fighter arena brawls (the owner's "hybrid of wrestling, WMXIX/No Mercy, and Tekken modes").
- **Why it matters:** Every other mode is 1v1; this is the only multi-combatant mode in any teardown. **Owner design question is open:** standalone BRAWL MODE vs merged into wrestling mode.
- [ ] OK to wire / [ ] Skip

### UR-2. 100-mission structure (256 mission definitions extracted)
- **What it adds:** Mission-based content (objectives, win conditions, per-mission data) for a challenge/mission mode.
- **Why it matters:** Story mode has episodes; missions are the bite-sized replayable complement. Data is already extracted.
- [ ] OK to wire / [ ] Skip

### UR-3. AI partner double-team system
- **What it adds:** Partner AI that catches launched enemies and slams them — double-team combos.
- **Why it matters:** Only partner mechanic in any teardown; feeds story mode (partner fights) and brawl mode.
- [ ] OK to wire / [ ] Skip

### UR-4. Weapons (30+: bats, pipes, bottles, shovels, 2x4s)
- **What it adds:** Pickup/useable weapons with their own motion pool (`general_weapon.gyu` extracted).
- **Why it matters:** No weapons exist in WH today; brawl mode without weapons is half the fantasy.
- [ ] OK to wire / [ ] Skip

### UR-5. Destructible environments
- **What it adds:** Breakable furniture, shattering cars/pinball machines, shelves shedding boxes.
- **Why it matters:** Arena interactivity — the arenas directive wants real arenas, not static dioramas.
- [ ] OK to wire / [ ] Skip

### UR-6. Special arts meter (uncounterable super moves)
- **What it adds:** Meter that builds on damage/dodges/hits, spent on uncounterable supers.
- **Why it matters:** **Verify overlap** with Soul Surge / Break gauge / Soul Charge — may be the same system with a different name.
- [ ] OK to wire / [ ] Skip

### UR-7. 60+ fighter styles (boxing, wrestling, karate, brawling, capoeira, kung fu)
- **What it adds:** Style reference data for moveset building (~30 special moves + ~50 double-team attacks per character documented).
- **Why it matters:** Style diversity input for the intake roster's movesets.
- [ ] OK to wire / [ ] Skip

### UR-8. Stage PPK geometry (7 stages extracted, inner decode open)
- **What it adds:** Back alleys, bars, rooftops, Chinatown, junkyards as real stage geometry — needs the Namco inner-chunk decode finished.
- **Why it matters:** The most WH-flavored stage art in any teardown (street-level, not tournament).
- [ ] OK to finish decode + wire / [ ] Skip

### UR-9. Cutscene data (35 demo_data PPKs)
- **What it adds:** Real cutscene staging data for the real-time-rendered cutscene directive.
- **Why it matters:** Owner wants in-engine cutscenes; these show how Namco staged theirs.
- [ ] OK to wire / [ ] Skip

---

## DEF JAM: FIGHT FOR NY (`teardown/def-jam-fight-for-ny/`)

### DJ-1. One shared grappling state machine (grab → struggle → throw/hold), 5 style skins
- **What it adds:** EA Chicago's proven architecture: ONE grappling core (streetfighting/kickboxing/martial-arts/wrestling/submission only change which `wresNNN` anim set and WAZA moves fire). Current WH throws are Tekken-style only (throw lock + breaks).
- **Why it matters:** This is the owner's thesis item — "wrestling/grappling animations work inside a Tekken-style 3D fighter engine" — and the AKI lineage (`AKI_CFG.XML` ships on-disc) matches our No Mercy systems.
- [ ] OK to wire / [ ] Skip

### DJ-2. 48 venues (`VENUE.XML`: name → model, crowd/ambient/speech config)
- **What it adds:** 48 venue definitions with crowd and ambient audio config.
- **Why it matters:** Stage expansion + the crowd/ambience config format the arena audio layer doesn't have.
- [ ] OK to wire / [ ] Skip

### DJ-3. `COMBS.XML` (combo/skill chains) + `TAUNT.XML`
- **What it adds:** Real combo-chain data and taunt definitions.
- **Why it matters:** Combo strings are a known user complaint (randomly mapped); real chain data is the fix material. Taunts feed the win-pose/taunt system.
- [ ] OK to wire / [ ] Skip

### DJ-4. WAZA move database (676 named moves, `MOTION/MAIN_ALL.DAT`)
- **What it adds:** 676 named grappling/strike techniques in plaintext to name and structure the grappling move tables.
- **Why it matters:** No-AI-slop move naming for the wrestling layer.
- [ ] OK to wire / [ ] Skip

### DJ-5. `FIGHTER.XML` (142 fighters: style, bodysize, speechID)
- **What it adds:** Style/body/speech metadata per fighter — a template for WH's own fighter metadata records.
- **Why it matters:** Data-model reference; cheap to adopt.
- [ ] OK to wire / [ ] Skip

---

### DJ-6. BLAZIN' momentum system (momentum meter → BLAZIN' mode → dedicated finisher bank)
- **What it adds:** Landing strikes/grapples/taunts fills a momentum meter; full meter = BLAZIN' mode (glow, crowd roar), where grapple + direction fires a style-specific finisher from a DEDICATED bank (`MOTION/BLAZIN.VIV`, 2.9MB — finishers are authored, not scaled-up normals). KO rule is two-gated: finishers only work when the victim is in the red "danger" zone AND you have the resource.
- **Why it matters:** The fight-economy design that makes grappling pay — and the two-gate KO rule is why FFNY fights have drama instead of one-touch kills. **Fold into X-2** (meter unification) rather than building separately.
- [ ] OK to wire / [ ] Skip

## VIRTUA FIGHTER 5 (`teardown/virtua-fighter-5/`)

### VF5-1. 38 stage archives (extracted, on release `vf5-ps3-v1`)
- **What it adds:** 18 arenas' geometry + textures, already extracted — the most complete ready-to-convert stage pool in the audit.
- **Why it matters:** Stage expansion with zero additional RE work; VF5's clean arena design fits WH's aesthetic.
- [ ] OK to wire / [ ] Skip

### VF5-2. 19-fighter roster + farc model formats
- **What it adds:** Per-character model packs (documented formats: `.farc`, `.bin` via chrrox script, `.txp` textures).
- **Why it matters:** Model pool, especially grapplers (Wolf, Jeffry, Goh, El Blaze, Vanessa, Aoi — all flagged HIGH priority in the teardown).
- [ ] OK to wire / [ ] Skip

### VF5-3. Weight classes (juggle physics)
- **What it adds:** Feather/light/middle/heavy/super-heavy classes scaling launch height, juggle length, and throw damage — a pure data addition (`weight_class` per fighter), no input changes.
- **Why it matters:** Gives Tekken's juggle system real physicality; featherweights fly, heavies barely leave the ground.
- [ ] OK to wire / [ ] Skip

### VF5-4. Sabaki + inashi + reversals (defensive move properties)
- **What it adds:** Attacks that auto-deflect incoming strikes of specific levels mid-attack (sabaki), catch-and-redirect throws (inashi), and a new `reversal` move category that plays a canned counter on a successful catch.
- **Why it matters:** New move properties/slots, zero input changes — deepens defense without touching Tekken feel.
- [ ] OK to wire / [ ] Skip

### VF5-5. Evade advantage + Offensive Move (OM) attacks
- **What it adds:** Sidestepping clean through an attack's active frames grants +frames; plus OM-flagged moves usable only from sidestep.
- **Why it matters:** Makes sidestep a real defensive answer with reward, not just repositioning.
- [ ] OK to wire / [ ] Skip

### VF5-6. Multi throw escapes (buffer 2 break inputs)
- **What it adds:** Allow buffering two throw-break directions during throw startup (VF's ETEG option-select), deepening the throw mindgame.
- **Why it matters:** Tekken's throw-break system exists; this extends it without changing inputs.
- [ ] OK to wire / [ ] Skip

### VF5-7. Two-tier counter hits (minor +25% / major +50% + crumple)
- **What it adds:** Replace Tekken's single counter-hit flag with VF's minor/major tiers (interrupt startup = major).
- **Why it matters:** More granular reward for reads; feeds the stun/juggle grammar.
- [ ] OK to wire / [ ] Skip

### VF5-8. Tech roll + rising attacks + ground throws (oki game)
- **What it adds:** Roll on landing (left/right/neutral), rising mid/low attacks, downed-attack and ground-throw slots.
- **Why it matters:** VF has the deepest wakeup game in 3D fighters; Tekken's oki is comparatively thin.
- [ ] OK to wire / [ ] Skip

### VF5-9. Wall stagger + pushback limiter
- **What it adds:** Hitting a walled opponent causes stagger (combo extender); wall pushback caps combo length so infinites can't happen.
- **Why it matters:** Wall game exists in Tekken; VF's version is more principled.
- [ ] OK to wire / [ ] Skip

### VF5-10. Open/closed stance (Phase 2)
- **What it adds:** Relative foot-forward stance state affecting throw-break directions, tracking, and combo routing.
- **Why it matters:** High-level depth; the doc itself flags it as Phase 2 after core defense lands.
- [ ] OK to wire / [ ] Skip

### VF5-11. Ring-out rules (both feet out + hitstun; half-fenced stages)
- **What it adds:** Precise ring-out condition and the half-fenced stage type (walls on some sides, ring-out on others).
- **Why it matters:** Pairs with SC2-3/SC6 ring-out — VF's rule formulation is the most implementable.
- [ ] OK to wire / [ ] Skip

---

## WWE / WRESTLING SOURCES

### WWE-1. WMXIX: 170 YANM clips indexed but NOT engine-playable
- **What it adds:** An engine loader for the indexed WMXIX clips (`WMXIX-CLIP-INDEX.json` exists; retarget is proven on ONE clip only — `yanm_to_tekken3_v2.py` on King's entrance). Same for No Mercy's 5,787 indexed `.npy` clips (no engine loader plays them).
- **Why it matters:** Thousands of real wrestling animations sit indexed but unplayable; the retarget pipeline needs to go library-scale.
- [ ] OK to wire / [ ] Skip

### WWE-2. WMXIX Revenge Mode (mode design doc)
- **What it adds:** A traversal/backstage brawl mode design (out-of-ring areas documented in the teardown).
- **Why it matters:** Distinct from arcade/story — the "wrestling mode" the brawl-mode question (UR-1) keeps circling.
- [ ] OK to wire / [ ] Skip

### WWE-3. WWE 2K ported moves/animations packs (0.69GB — highest value per MB)
- **What it adds:** Real 2K15–2K20 animation data (ported moves pack + entrance/victory motions pack) without downloading 300+ GB of games. Cataloged, never pulled.
- **Why it matters:** The owner wants WWE 2K26 animations/code/physics, not models — these packs are the cheapest way to get real 2K animation data.
- [ ] OK to pull + wire / [ ] Skip

### NM-1. No Mercy entrance-music table (50 entries, ROM-verified)
- **What it adds:** The real entrance-theme table (`0x168D790`, incl. 7 CAW original-theme slots) → entrance music system. `game/js/audio.js` has no music table today.
- **Why it matters:** Entrances are half the wrestling fantasy; the data is decoded and waiting.
- [ ] OK to wire / [ ] Skip

### NM-2. No Mercy CAW save-record layout (blocked — needs emulator save dump)
- **What it adds:** Nothing yet — the byte layout can't be decoded from ROM alone.
- **Why it matters:** Listed as blocked, not actionable.
- [ ] OK to wire / [ ] Skip

### NM-3. No Mercy menu/UI texture categories (titantron, portraits, icons — 500+ files)
- **What it adds:** Menu/titantron/portrait textures for the creation suite and menu art (faces + skins already wired; these categories were skipped).
- **Why it matters:** Menu art the select-screen overhaul can use instead of generating from scratch.
- [ ] OK to wire / [ ] Skip

---

## CROSS-CUTTING (new directives + follow-ups)

### X-1. Rank ladder (user-built 2026-10-22: 53 tiers, data-driven, NOT wired)
- **What it adds:** Lost Soul → 9th Kyu → 1st Dan → Brawler → … → Nine Souls → Tong-Nou → Master God of the Universe (#51), with tiers 52–53 RESERVED UNNAMED (invented when a player holds #51 long enough, Tekken God→True→Prime→Omega style) — all as DATA (not hardcoded), plus offline rank battles, online ladders/leaderboards, promotion/demotion.
- **Why it matters:** The user's own rank system, specified the same day as this audit. Tekken's dan/kyu data in the teardowns can source the real-terms tiers.
- [ ] OK to wire / [ ] Skip

### X-2. Meter/power unification (Soul Surge vs Break gauge vs Soul Charge vs Special arts vs BLAZIN')
- **What it adds:** One unified meter/power system instead of five overlapping ones (DOA6-4, SC2-5, SC6-4, UR-6, DJ-6, existing Soul Surge).
- **Why it matters:** Building all of them separately would be incoherent; the user should pick the federation shape first. Note the two-gate KO rule (resource + victim danger zone) from DJ-6 as a candidate universal finisher rule.
- [ ] OK to unify / [ ] Skip

### X-3. Persistent asset cache (IndexedDB GLB cache — flagged follow-up from load-speed lane)
- **What it adds:** Offline-first / repeat-visit speed: Tekken's "install" equivalent for the browser build.
- **Why it matters:** HTTP caching covers repeat visits, but the 40–90MB GLBs still re-download; flagged by the load-speed lane, not built.
- [ ] OK to wire / [ ] Skip

---

## Counts

| Source | Gap items |
|---|---|
| Tekken 3 | 3 actionable (+1 blocked) |
| Tekken 6 | 2 actionable (+1 blocked) |
| Tekken 7 | 3 (all blocked on acquisition) |
| Tekken 8 | 1 (research) |
| TTT2 | 4 (+1 blocked) |
| DOA4 | 2 |
| DOA6 | 5 |
| Street Fighter | 4 |
| Soulcalibur 2 | 5 |
| Soulcalibur 6 | 8 (7 mechanics + 1 acquisition) |
| Urban Reign | 9 |
| Def Jam FFNY | 6 |
| Virtua Fighter 5 | 12 (2 assets + 10 mechanics) |
| WWE / No Mercy | 6 (+1 blocked) |
| Cross-cutting | 3 |
| **Total** | **~73 actionable** (+4 blocked, +3 verify) |

**Verify items:** TTT2-1 (worker 24 overlap), TTT2-4 (Combot vs create-a-fighter overlap), SC2-5/DOA6-4/UR-6 (folded into X-2).
