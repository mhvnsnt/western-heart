# COMPREHENSIVE GAP ANALYSIS + EXPERIMENTAL PROJECTS RESEARCH
## Western Heart vs Tekken Games + What to Pull In and Wire Up
### Date: 2026-10-24 | Research grounded in actual WH repo files (via GitHub API) + Tekken community docs + open source project sources
### User directive: "what other gaps do we need filled and what other things can we pull in and wire up? What experimental projects align with our game and our canon and our style? What do T7 and all Tekken games have that we're missing 100% from their files that we can pull in and wire up completely so our game feels like a mix of all of them and so we can improve our UI, menus, loading times, everything?"

---

# PART 1 — WHAT WH ALREADY HAS (verified, so gaps below are honest, not guesses)

All verified via GitHub API (`custom.github_pat`) against `mhvnsnt/western-heart` main branch, 2026-10-24.

| System | WH file + size | Tekken source | Status |
|---|---|---|---|
| Rage (≤25% HP, once/round) | `game/js/rage.js` (8,220 bytes) | T7 Rage, T6 Rage | EXISTS |
| Rage Art (LP1+RP2 while raging, armored, cinematic) | `game/js/rage.js` | T7 Rage Art | EXISTS |
| Rage Drive (powered-up strike) | `game/js/rage.js` | T7 Fated Retribution | EXISTS |
| Stage breaks (floor/wall/balcony) | `game/js/stagebreaks.js` (20,203 bytes) | T7 Forgotten Realm, Brimstone & Fire, Devil's Pit; TTT2/T7 wall breaks | EXISTS |
| Music engine (file-based BGM, crossfade, intensity scaling) | `game/js/music.js` (10,675 bytes) | Tekken convention (one BGM per stage, title/select/VS/results themes) | EXISTS |
| Online (lobbies, tournaments, netplay, daily challenges) | `game/js/online.js` (43,141 bytes) + `game/netplay/` (bridge, lobby, mirror.mjs, signaling, sim, vendor) | TTT2 Player Matches, SFV Battle Lounge | EXISTS |
| Tag system (Raw Tag, Tag Assault, Tag Crash) | `game/js/tag-relay.js` (5,517 bytes) | TTT2 | EXISTS |
| V-System (V-Skill/V-Trigger/V-Reversal/V-Shift, Tekken-ified) | `game/js/v-system.js` (7,301 bytes) | SFV V-System, owner-approved 2026-10-22 | EXISTS |
| Finisher (KESSHOU, two gates: meter full + victim <25% HP) | `game/js/finisher.js` (10,189 bytes) | Def Jam: Fight for NY BLAZIN.VIV lineage | EXISTS |
| Soul Urge (T8 Heat renamed) | `game/js/soulurge.js` (8,463 bytes) | T8 Heat (Heat Smash, Heat Engager, Heat Dash conditions) | EXISTS |
| Loading progress (real, via THREE.DefaultLoadingManager + creep cap) | `game/js/load-progress.js` (3,547 bytes) | Owner fix 2026-10-23 ("loading bar doesn't visibly move") | EXISTS |
| Training (combo trials, punishment training, fight lab) | `game/js/combo-trials.js`, `punishment-training.js`, `fightlab-gungaku.js` | T7 Practice mode patterns | EXISTS |
| Hit detection (14 swept capsules) | `game/js/hitbox.js`, `hitdetect.js` (PR #1005) | Derived from live data (not T7 per-move hitboxes — see Gap 3) | EXISTS (generic, not per-move) |
| Movesets | `game/assets/movesets/` — 157 files | T3 + T7 (8-9 files with T7 blocks) | PARTIAL (see Gap 5) |
| Animation banks | `game/assets/anim/t3/` — 22 banks (anna, armorking, bosconovitch, bryan, eddy, forestlaw_on_law, gon, gunjack, heihachi, heihachi_on_jin, hwoarang, jin, julia, king_on_pantera_leoman, kuma, law, lei, nina, ogre, paul, xiaoyu, yoshimitsu + reactions.json) | T3 teardown | EXISTS (T3 only, no T7 banks — see Gap 4) |
| Fighter core | `game/js/fighter.js` (122,855 bytes) | T3 frame data + T7 MOD damage | EXISTS |
| Combat core | `game/js/combat-core.js` (5,769 bytes) | WH-original | EXISTS (small — see Gaps 1, 2, 9) |
| Frame tables | `game/js/frame-tables.js`, `game/data/t8_frame_tables.json` | T7/T8 frame data | EXISTS |
| Select screen | `game/js/select-screen.js`, `select-t7-layout.js`, `select-t7.css`, `select-t8.css` | T7 layout, T8 visual reference | EXISTS |
| Menus | `game/js/mainmenu.js`, `menus.js`, `menu-t7-layout.js`, `menu-t7.css` | T7 teardown | EXISTS |
| Ranks | `game/js/ranks.js`, `game/data/ranks.json` | WH 53-tier ladder (user-locked) | EXISTS |
| Replay | `game/js/replay-analysis.js` | T7 replay theater pattern | PARTIAL (analysis, not full theater — see Gap 20) |
| Voice/audio | `game/js/voice.js`, `audio.js`, `game/data/sound-bank.json`, `game/data/voices/` | T7 voice banks (partial) | PARTIAL |

Pantera moveset evidence (verified):
- 874 moves (dict keyed by input notation: '1', '2', '2,1', '3', '4', ...)
- Each move: name, input, t3_source, t3_row, t3_command, startup, active, recovery, damage, t3_damage, limb, heavy, knock, soulGain, anim_ref, input_slots, move_class, t7 block (damage, startup_frames, on_block, on_hit, on_ch, hit_level, notation, id, wired, mod_source)
- Counts in file: t7 = 260 refs, hit_level = 850, on_block = 834, on_hit = 851, startup = 1605, active = 874, recovery = 1344
- hitbox = 0 occurrences in moveset file (see Gap 3)

---

# PART 2 — DELIVERABLE 1: GAP ANALYSIS (WH vs Tekken, grounded in files)

## COMBAT SYSTEM GAPS

### Gap 1 — Power Crush: NOT in core combat (CRITICAL, T7 signature system)
- **What T7 has:** Power Crush moves absorb damage from mid/high attacks and continue anyway, but leave user vulnerable to lows and throws. Every character has at least one Power Crush. Source: Tekkenpedia / Tekken Wiki T7 gameplay pages; community glossary ("Power Crush – an armoured move available for all chars").
- **What WH has:** ZERO mentions of `powercrush` or `power_crush` in `game/js/fighter.js` (122,855 bytes, grepped) AND ZERO in `game/js/combat-core.js` (5,769 bytes, grepped). The core combat file does not implement armor-vs-mid/high at all.
- **File evidence:** `game/js/fighter.js` grep: powercrush=0, power_crush=0. `game/js/combat-core.js` grep: powercrush=0, power_crush=0.
- **What to pull/wire:** T7 Power Crush move list per character (which moves are Power Crush, from T7 frame data — wavu.wiki / TheBigTuna + community docs). Add `power_crush: true` flag to moveset move records. Implement in combat-core: when a Power Crush move is active, mid/high hits deal damage (chip or reduced) but do NOT interrupt the move; low hits and throws DO interrupt. Wire into `game/js/combat-core.js` + `game/js/hitdetect.js` + moveset files. Priority: HIGH (T7 feel depends on it — without it, pressure game is wrong).

### Gap 2 — Screw / Tailspin (S!): NOT in core combat (CRITICAL, T7 combo system)
- **What T7 has:** Screw (aka Tailspin, Kirimomi, S!) replaced Bound as the once-per-combo extender. A Screw move in juggle spins the opponent and drops them in a slump state where extra combos/damage are guaranteed. Can only be done once per combo. Low parry still causes Bound. Source: Tekken Wiki T7 ("Screw moves are the new staple for many juggle-based combos"; "can only be done once during a combo").
- **What WH has:** ZERO mentions of `screw`, `tailspin`, or `kirimomi` in `game/js/fighter.js` AND ZERO in `game/js/combat-core.js`. WH uses Bound instead (bound=12 mentions in fighter.js) — that's the T6/TTT2 system, not T7. T7 combos in WH will feel wrong (Bound where Screw should be, wrong juggle routes, wrong damage scaling).
- **File evidence:** fighter.js grep: screw=0, tailspin=0, kirimomi=0, bound=12. combat-core.js grep: screw=0, tailspin=0, kirimomi=0.
- **What to pull/wire:** T7 Screw move list per character (which moves are Screw, from T7 frame data). Add `screw: true` flag to moveset records. Implement Screw state in combat-core: juggle + Screw move → opponent spins, lands in slump, Screw flag consumed for that combo (no second Screw), follow-up window opens. Keep Bound for low parry only (T7-accurate). Wire into `game/js/combat-core.js` + moveset files. Priority: HIGH (defines T7 combo feel).

### Gap 3 — Per-move hitbox / hurtbox data: MISSING (WH uses generic capsules)
- **What T7 has:** Every move has specific hitbox dimensions, positions, and active frames from the game files. Different moves have different reaches, heights, and hitbox shapes. A jab's hitbox is NOT a generic capsule — it's the exact box T7 attaches to that move.
- **What WH has:** ZERO occurrences of "hitbox" in `game/assets/movesets/pantera.json` (874 moves). WH uses PR #1005's 14 swept capsules — a generic body-part system, not per-move data. This means a jab and a hook have the same hitbox shape (wrong reach, wrong height, wrong whiff behavior).
- **File evidence:** pantera.json grep: hitbox=0. PR #1005 documented: "14 swept capsules replace 2 spheres; capsule radii approximate; 165 uncovered Pantera moves default to mid."
- **What to pull/wire:** T7 per-move hitbox data from T7 files (via live extraction or community hitbox viewers — TekkenMods, Kiloutre structs). Add `hitbox: {shape, dimensions, position, active_frames}` + `hurtbox` per move to moveset files. Wire into `game/js/hitbox.js` + `hitdetect.js` to use per-move boxes when present, fall back to capsules when absent. Priority: HIGH (hit/miss correctness depends on it — user law: "fighters MUST make contact when they hit, 100% wired from Tekken").

### Gap 4 — T7 animation banks: ZERO (WH has T3 only)
- **What T7 has:** Full T7 animation banks per character (motion + MOTA data, thousands of clips per character).
- **What WH has:** `game/assets/anim/` has only `t3/` (22 banks), `oss/`, `made/`. ZERO T7 banks. T7-only moves (e.g., Pantera 1,2,1 Palm Strike Uppercut) play fallback animations, not their real T7 clips.
- **File evidence:** `game/assets/anim/` listing: made, oss, t3 only. No t7 dir.
- **What to pull/wire:** T7 animation extraction (live game memory via TKMovesets, or mot.bin RE for remaining characters). Convert to WH anim format, wire into `game/assets/anim/t7/{character}/` + moveset `anim_ref` fields. Priority: HIGH (already in progress via batch extraction lane — this gap analysis confirms it's the top animation gap).

### Gap 5 — T7 moveset coverage: only 8-9 of 157 files have T7 blocks
- **What T7 has:** Full T7 movelists for 36+ characters (TheBigTuna) + DLC characters.
- **What WH has:** 157 moveset files, but only burger, demonio, diablo, kinpo, pantera, phantom, scimitar, skull, torch have T7 blocks (PR #1000/#1002 MOD damage wiring). 148 files are T3-only. DLC characters (Fahkumram, Ganryu, Geese, Kunimitsu, Leroy, Lidia, Negan, Noctis, Zafina) have no T7 frame data in WH.
- **File evidence:** PR #1000/#1002 counts; TheBigTuna character list (36 chars, missing 13 DLC).
- **What to pull/wire:** T7 frame data for all remaining characters + DLC from wavu.wiki, geppopotamus.info, Tekken Wiki, community docs. Convert via moveset-parser (PR #999) to LP1/RP2/LK3/RK4 + MOD damage. Wire into all 157 moveset files. Priority: HIGH (batch lane in progress).

### Gap 6 — Tornado (T8 combo extender): NOT present
- **What T8 has:** Tornado replaced Screw in T8. Tornado places opponent in ground-bound state when they fall quickly. Different properties from Screw (ground-bound vs slump).
- **What WH has:** Neither Screw nor Tornado in core combat (see Gap 2). WH's Soul Urge (T8 Heat) exists but Tornado as a combo state does not.
- **File evidence:** combat-core.js grep: screw=0, tornado not checked but Screw absence implies Tornado absence (Tornado is T8-only, WH core is T3/T7-based).
- **What to pull/wire:** T8 Tornado move list + state rules from T8 files/community docs. Implement as alternative combo extender (or as WH-original variant tied to Soul Urge). Wire into combat-core. Priority: MEDIUM (T8 system, WH is T7-based — implement after Screw is done, or as WH-original twist).

### Gap 7 — Recoverable health (T8 white gauge): NEEDS VERIFICATION
- **What T8 has:** Recoverable health (white gauge). Chip damage from blocking / Heat attacks creates recoverable health. Recover ONLY by attacking opponent (landing hits or forcing blocks). Does NOT recover over time. Source: Tekken 8 Wikipedia + PC Gamer Heat breakdown.
- **What WH has:** Chip damage exists (chip=15 mentions in fighter.js, 12% chip + blockstun per header comment). Soul Urge (T8 Heat) exists in soulurge.js. But whether chip damage creates a RECOVERABLE gauge (vs permanent chip loss) and whether attacking recovers it is NOT verified from files read.
- **File evidence:** fighter.js header: "blocking w/ 12% chip + blockstun". soulurge.js header mentions Heat conditions. Recoverable gauge implementation not confirmed in files sampled.
- **What to pull/wire:** Verify soulurge.js + fighter.js for recoverable gauge. If absent: implement white-gauge system (chip → recoverable pool, attack → recover pool, low attacks reduce pool). Wire into HUD (white bar under health, like T8). Priority: MEDIUM (T8 system, improves aggression reward).

### Gap 8 — Heat Engager / Heat Dash / Heat Smash specifics: PARTIAL
- **What T8 has:** Heat Engagers (∼5 per character, specific moves that trigger Heat + auto-run + heal recoverable health). Heat Dash (cancel + dash, costs 1 Heat energy, extends combos). Heat Smash (super move, costs Heat, high damage). Heat Burst (manual activation, Power Crush property, Bound-like spike, recoverable damage only).
- **What WH has:** soulurge.js (8,463 bytes) pulls T8 Heat Smash as move category + Heat Engager hit conditions + Heat Dash conditions from T8 files. But per-character Engager lists, Dash cancel implementation in fighter.js, and Smash as distinct move category need verification.
- **File evidence:** soulurge.js header cites T8 files (Move category, Hit_Conditions). fighter.js grep: heat=1 (only 1 mention — Heat/Soul Urge may not be integrated into core fighter loop).
- **What to pull/wire:** Verify soulurge.js integration into fighter.js combat loop. Pull per-character Heat Engager lists from T8 files. Wire Heat Dash (cancel window) + Heat Smash (move category + input) + Heat Burst (input + Power Crush property) into fighter.js + movesets. Priority: MEDIUM-HIGH (Soul Urge is user-locked name, system must be complete).

### Gap 9 — Wall splat as distinct juggle state: NOT in core combat
- **What T7 has:** Wall splat (W!) is a distinct state: opponent hits wall, splats, vulnerable to follow-up. Different from wall BREAK (WB! — wall shatters, bounds extend). Wall splat → wall combo → wall ender is core T7 flow.
- **What WH has:** stagebreaks.js covers wall BREAKS (20,203 bytes). But combat-core.js has ZERO mentions of wall_splat/wallsplat. The core combat may not distinguish wall splat state from generic knockback.
- **File evidence:** combat-core.js grep: wall_splat=0, wallsplat=0. stagebreaks.js exists but is stage geometry, not combat state.
- **What to pull/wire:** Implement wall splat state in combat-core: when knockback trajectory hits wall bounds (arena clamp ≤8.4 per PR #1008), opponent enters splat state (stuck to wall, vulnerable frames, specific follow-up window). Distinguish from wall break (breakable wall → shatter → bounds extend). Wire into fighter.js + stagebreaks.js + arena collision. Priority: MEDIUM-HIGH (wall game is core Tekken).

### Gap 10 — Item moves: NOT present
- **What T7 has:** Item moves (character-specific attacks using customization items — e.g., weapon attacks, funny item attacks). Toned down from TTT2 but most characters still have them.
- **What WH has:** Customization exists (attires.js, customization-consumer.js, creation-parts-private.js, game/data/moveset-library/). But item MOVES (attacks that require equipped items) have no evidence in files sampled.
- **File evidence:** No item-move system found in js file list (no item-moves.js, no item_attacks in moveset sample).
- **What to pull/wire:** T7 item move list per character from community docs. Add item-move slots to moveset files (gated by equipped item). Wire into customization system (equip item → unlock item move). Priority: LOW-MEDIUM (fun, not core combat, but T7-complete).

## UI / MENU / MODE GAPS

### Gap 11 — Jukebox: NOT present
- **What T7 has:** Jukebox — replace T7 soundtrack with any prior Tekken soundtrack (T1-T6, TTT2) in Arcade and Treasure Battle modes. Full series music library, selectable per mode.
- **What WH has:** music.js has one-BGM-per-stage + title/select/VS/results themes + crossfade + intensity scaling. NO jukebox (no soundtrack selection, no prior-game music library in rotation).
- **File evidence:** music.js header: "Tekken convention — one BGM per stage, separate themes for title / character-select / versus / results". No jukebox mention. game/data/music-library.json exists but structure not verified for jukebox.
- **What to pull/wire:** Pull prior Tekken soundtracks (T3, T5, T6, TTT2 BGM) + Nosferatu synth score tracks (already in progress) into music-library.json. Add Jukebox UI (select soundtrack per mode, or per stage). Wire into music.js (soundtrack pool selection). Priority: MEDIUM (user already wants rotating music + Nosferatu tracks — jukebox is the T7-native version of that).

### Gap 12 — Gallery (prior game FMVs/endings): NOT present as T7-equivalent
- **What T7 has:** Gallery — watch every FMV / ending cinematic from every prior Tekken game. Nostalgia content, unlockable.
- **What WH has:** episodes.js, story-endings.js (WH story content). No gallery of prior Tekken FMVs (which would be T7 content, not WH canon — WH canon forbids Tekken names in-universe, so a direct Gallery port conflicts with canon law).
- **File evidence:** js file list has episodes.js, story-endings.js, no gallery.js.
- **What to pull/wire:** WH-canon equivalent: Gallery of WH story cinematics, character endings, show episodes (Cape Jones show content), concept art. Wire into menus (Collection/Gallery screen). Do NOT pull Tekken FMVs as-is (canon law) — pull the GALLERY SYSTEM structure from T7, fill with WH content. Priority: LOW-MEDIUM (collection/completion feature, not core fight).

### Gap 13 — Treasure Battle loop: PARTIAL
- **What T7 has:** Treasure Battle — endless enemies, win → treasure chests → customization items + currency. Addictive loop, hours of play. Unlimited opponents, escalating difficulty, special matches.
- **What WH has:** challenges.js, unlockables.js, modes.js, arcade mode (per mainmenu). But endless + loot-chest + customization-unlock loop as a distinct mode is not verified.
- **File evidence:** js file list has challenges.js, unlockables.js, modes.js. No treasure-battle.js.
- **What to pull/wire:** Implement Treasure Battle mode: endless ladder, win → chest (random customization item + currency), special matches (e.g., vs ghost data, vs powered-up opponents). Wire into modes.js + unlockables.js + customization system. Priority: MEDIUM (retention loop, T7's most-played single-player mode per reviews).

### Gap 14 — Character select T7 5.10 features: NEEDS VERIFICATION
- **What T7 has (v5.10):** Favorite character+costume one-button select. Last costume memory within session. Tournament settings lock (disables favorites/costume/last-costume in Versus). Streaming mode (opponent ID → character name on VS/battle screens).
- **What WH has:** select-screen.js, select-t7-layout.js, select-t7.css, select-t8.css, roster-full.js. T7 layout adopted. But favorite one-button, last-costume memory, tournament lock, streaming mode not verified in files sampled.
- **File evidence:** select files exist. 5.10 features not confirmed in sampled headers.
- **What to pull/wire:** Verify select-screen.js for these features. If absent: implement favorite slots (save fighter+attire, one-button recall), last-attire memory (per session, like T7), tournament mode toggle (locks favorites/attire), streaming mode toggle (hide opponent ID). Wire into select-screen.js + versus-setup.js. Priority: MEDIUM (quality-of-life, T7-complete).

### Gap 15 — VS screen / result screen depth: PARTIAL
- **What T7 has:** VS screen shows rank, win/loss record, connection bars, character + costume, stage. Result screen offers rematch, character change, stage change, back to menu, with stats.
- **What WH has:** versus-setup.js, versus-banter.js, tournament-ui.js. VS flow exists. But rank display on VS screen, connection quality bars, full result-screen options not verified.
- **File evidence:** versus files exist. Depth not confirmed.
- **What to pull/wire:** Verify versus-setup.js + result flow. If absent: add rank/W-L display (from ranks.js), connection bars (from netplay sim), result options (rematch / change fighter / change stage / menu). Wire into versus-setup.js + online.js. Priority: MEDIUM (online + VS polish).

### Gap 16 — Announcer coverage: PARTIAL
- **What T7 has:** Announcer voice for round calls ("Round 1, Fight!"), "K.O.", "Perfect!", "Double K.O.", "Time Up", character names on select, win quotes.
- **What WH has:** voice.js, audio.js, game/data/voices/, game/data/sound-bank.json. Character voices partial (Pantera/King pulled, see king-mods/). Announcer as a distinct voice bank (not character voice) not verified.
- **File evidence:** voice.js exists. Announcer bank not confirmed.
- **What to pull/wire:** Pull/assign announcer voice (from T7 announcer clips via community, or record WH-original announcer). Wire into audio.js (round start/end, KO, perfect, select announcements). Priority: LOW-MEDIUM (polish, fight feel).

### Gap 17 — Stage transitions (multi-level fights): PARTIAL
- **What T7 has:** Multi-level stages: fight starts on upper level, floor break drops both fighters to lower level, fight continues with new geometry (e.g., Forgotten Realm 3 levels, Brimstone & Fire, Devil's Pit). Balcony break flings opponent to lower area (Tag Assault-style launch).
- **What WH has:** stagebreaks.js (20,203 bytes) covers floor breaks (drop + bonus damage + continue below), wall breaks, balcony breaks. But full multi-level stage geometry (distinct levels with distinct layouts, not just drop) needs verification.
- **File evidence:** stagebreaks.js header describes floor breaks (drop to lower level, continue below) + wall breaks + balcony breaks. Stage files: stages.js, stage-variants.js, stage-intros.js.
- **What to pull/wire:** Verify stagebreaks.js + stages.js for multi-level geometry. If absent: implement multi-level stages (level definitions, geometry swap on break, camera transition, continue fight on new level). Pull T7 multi-level stage layouts from teardown/community docs. Priority: MEDIUM (stage variety, T7 spectacle).

## DATA / LOADING / PERFORMANCE GAPS

### Gap 18 — Asset streaming / background loading: PARTIAL
- **What T7 has:** Background asset streaming — loads next fight's assets during current fight's outro / VS screen, so fight-to-fight transition is fast. Does NOT load everything upfront.
- **What WH has:** load-progress.js shows REAL progress (via LoadingManager) + creep cap, but fight load still fetches all models upfront at FIGHT press (user hit 6% stall → bounce bug, fixed by roster proxy PR #1023, but load is still synchronous upfront). lazy.js exists (name suggests lazy loading) but background preloading of NEXT fight not verified.
- **File evidence:** load-progress.js header (real progress, creep cap). lazy.js exists. Netlify publish dir = game/, roster proxied via _redirects.
- **What to pull/wire:** Implement background preloading: while in VS screen / fight outro, preload next likely assets (rematch fighters, stage variants). Implement asset streaming: load low-LOD first, high-LOD in background (see Experimental: gltf-progressive). Wire into lazy.js + load-progress.js + assets.js. Priority: HIGH (user complaint: loading times, fight load stalls — "improve loading times and all of that").

### Gap 19 — Model/texture optimization pipeline: MISSING (no automated pipeline)
- **What T7 has:** Production asset pipeline — models optimized for GPU (mesh optimization, texture compression, LODs, draw call batching) before shipping. T7 models are NOT raw 1.6M-vert meshes.
- **What WH has:** Cape body mesh is 1,638,010 verts, 1,045,182 non-manifold edges (33%) — documented in topology audit 2026-10-24. NO automated optimization pipeline found (no meshoptimizer, no gltfpack, no LOD generation in js file list or pipeline docs sampled).
- **File evidence:** Topology audit (MEMORY.md 2026-10-24): Cape body 1.6M verts, 33% non-manifold. No optimization tool in js list.
- **What to pull/wire:** meshoptimizer/gltfpack (MIT, measured 59% size reduction on test asset, identical vertex attributes). KTX2/Basis texture compression. Automatic LOD generation (high/mid/low). Wire into asset pipeline (build script that optimizes every GLB before deploy). Use Kaggle GPU for batch optimization. Priority: HIGH (load times + FPS + phone performance all depend on this — 1.6M-vert models on phone = slow).

### Gap 20 — Replay theater (save/share/analyze): PARTIAL
- **What T7 has:** Replay theater — save replays, watch, share, analyze (frame-by-frame, input display). Full replay system.
- **What WH has:** replay-analysis.js (analysis, not theater). sim-match.js (simulation). No replay save/share/theater UI verified.
- **File evidence:** replay-analysis.js exists. No replay-theater.js, no replay save in js list.
- **What to pull/wire:** Implement replay save (record inputs + RNG seed, deterministic replay via sim-match.js), replay theater UI (list, play, frame step, input display), share (export file / link). Wire into replay-analysis.js + sim-match.js + menus. Priority: LOW-MEDIUM (competitive + content creation, not core fight).

### Gap 21 — Frame data display IN FIGHT (practice overlay): PARTIAL
- **What T7 has:** Practice mode shows live frame data overlay (startup/active/recovery, advantage on block/hit, input display, hitbox display).
- **What WH has:** frame-tables.js (tables), punishment-training.js, fightlab-gungaku.js (GUNGAKU = fight lab). But in-fight live overlay (during actual fight, not just lab) not verified.
- **File evidence:** frame-tables.js, punishment-training.js, fightlab-gungaku.js exist. Live overlay during VS fight not confirmed.
- **What to pull/wire:** Implement optional in-fight overlay (toggle in options): current move frame data, advantage, input history, hitbox visualization (debug). Wire into fighter.js + hitbox.js + UI. Priority: MEDIUM (training + user playtest loop — user can SEE why a move is wrong, not just feel it).

### Gap 22 — T6 / T5 / TTT2-only systems not yet ported
- **What earlier Tekken has:**
  - T6 Bound (WH HAS this — bound=12 in fighter.js, but T7 replaced Bound with Screw — see Gap 2 for T7 accuracy)
  - TTT2 Tag Assault / Tag Crash / Raw Tag (WH HAS via tag-relay.js)
  - TTT2 Fight Lab (WH HAS via fightlab-gungaku.js, GUNGAKU name)
  - T5/T6 Customization depth (WH HAS customization system, depth TBD)
  - T6 Scenario Campaign (beat-em-up adventure mode) — WH has Heart and Mind Within (story/adventure mode) in planning, but Scenario Campaign-style beat-em-up with Tekken combat not verified as implemented
  - T5 Devil Within (mini-game) — WH has side-games.html, but Devil Within equivalent not verified
- **What to pull/wire:** Scenario Campaign structure (beat-em-up levels + Tekken combat + story) for Heart and Mind Within mode. Side-games depth (Go Qombat exists per canon, other side games TBD). Priority: MEDIUM (modes after combat foundation — user sequencing: models → animations → menus FIRST, arenas after, modes after foundation).

---

# PART 3 — DELIVERABLE 2: EXPERIMENTAL PROJECTS (aligned with WH canon/style)

Canon alignment key (from CANON.md + MEMORY.md):
- Eastern Mind / Western Heart universe: Tong-Nou, Nine Souls, Five Lands, Trial, Trader
- Multiverse: nested realities, realms within realms within beings within thoughts, layered perceptions as navigable realms, "colour is law", roads not portals
- New-age MUGEN: anyone can make/bring any fighter, full 3D, real creation tools, Tekken-level combat, creation suite = HEART
- KESSHOU finisher, Nine-Soul Climax/Release, Reihou, Trial's Seal, Soul Surge, Soul Urge
- Go Qombat (Go-based Chess Kombat), Heart and Mind Within (story/adventure)
- All characters adults, canon-grounded only, Tekken names in technical files only

## COMBAT

### E1. GGPO — Rollback Netcode (MIT License)
- **What:** Rollback netcode library by Tony Cannon (EVO co-founder). Predicts inputs, simulates without delay, rolls back + replays when predictions wrong. Gold standard for fighting games. Open source since 2019-10-09 under MIT.
- **Why aligns:** WH has online.js + netplay/ (lobby, signaling, sim) but rollback implementation depth unknown. GGPO makes online feel like offline — critical for Tekken-level competitive play. WH's sim-match.js (deterministic simulation) is exactly what GGPO needs (deterministic game logic + state snapshots).
- **Source:** https://github.com/pond3r/ggpo (MIT) | Docs: https://words.infil.net/w02-netcode-p5.html | Games using it: Skullgirls, Street Fighter III: 3rd Strike Online, Killer Instinct, Fantasy Strike
- **Pull:** Clone GGPO repo, port JS/WASM binding (GGPO is C — compile to WASM via Emscripten, or use existing JS port). Wire into `game/netplay/` (replace/augment sim + mirror.mjs with GGPO rollback: input prediction, state snapshot, rollback + resim).
- **Wire in:** `game/netplay/sim/` (deterministic sim) + `game/netplay/mirror.mjs` (rollback) + `game/js/online.js` (lobby → GGPO session). Best place: netplay sim layer, NOT fighter.js (keep combat logic deterministic, netcode separate).
- **Improves:** Online play feel (low perceived lag even at 100-150ms ping), cross-regional play, competitive viability. Priority: HIGH for online.

### E2. Castagne Fighting Game Engine (Godot, open source)
- **What:** Fighting game engine built on Godot. Modular, good editing tools, rollback netcode working out of the box. "If you create a character, he will work locally and online the same exact way." Supports 1v1 competitive + beat-em-ups + character action.
- **Why aligns:** WH is Three.js/web, not Godot — but Castagne's ARCHITECTURE is the reference: modular character definitions, editor-driven movesets, rollback-by-default. WH's Move List Creator + creation suite can borrow Castagne's character/module structure. Also a fallback if WH ever ports to Godot.
- **Source:** https://castagneengine.com/docs/ | Discord: https://discord.gg/CWjWfC9K9T | Game made with it: Kronian Titans (2D airdasher)
- **Pull:** Study Castagne docs + source (GitHub). Borrow: character module structure, moveset editor patterns, rollback integration pattern. Do NOT port WH to Godot (WH is web/Three.js) — borrow patterns only.
- **Wire in:** `packages/creation-suite/src/movelist-editor.js` (character module pattern) + `game/netplay/` (rollback-by-default pattern) + docs (architecture reference).
- **Improves:** Creation suite design, moveset editor structure, online architecture. Priority: MEDIUM (reference, not direct port).

### E3. Frame Data Tools (Dustloop / SuperCombo Wiki patterns)
- **What:** Community frame data wikis with structured move data (startup/active/recovery/advantage, hit level, notes, combo routes). Dustloop (Guilty Gear, etc.), SuperCombo Wiki (Street Fighter, etc.).
- **Why aligns:** WH already has frame-tables.js + TheBigTuna data, but in-game frame data DISPLAY (see Gap 21) + community-editable frame data would help user playtest loop (user sees why a move is wrong).
- **Source:** https://www.dustloop.com/w/Using_Frame_Data | https://wiki.supercombo.gg/w/Frame_Data | https://glossary.infil.net/?t=Frame%20Data
- **Pull:** Borrow display patterns (move table layout, advantage coloring, filter/search). Wire into WH movelist-ui.js + fightlab-gungaku.js (in-lab frame data display).
- **Wire in:** `game/js/movelist-ui.js` (move table) + `game/js/fightlab-gungaku.js` (lab display) + `game/js/frame-tables.js` (data).
- **Improves:** Training, playtest feedback, user understanding. Priority: MEDIUM.

## LEVEL DESIGN (Realms / Multiverse — STRONG canon alignment)

### E4. Node-Based Open World ProcGen (Nathan Savant)
- **What:** Node-based open world where each node borrows from Roguelike encounter design, each color = potential biome. Radiating from center, nodes = significant events, pacing like Slay the Spire. Procgen quests at nodes (go to location, find/save NPC, bring item, altar/seal mechanics).
- **Why aligns:** DIRECT canon hit — WH multiverse is "realms within realms within beings within thoughts, nested realities, layered perceptions as navigable realms, roads not portals." Node-based realm generation = Five Lands + nested realms + Trial paths. Quest nodes = Trial challenges. Biome colors = "colour is law."
- **Source:** https://www.nathansavant.com/open-world-procgen
- **Pull:** Borrow node-graph realm generation algorithm (node = realm, edge = road, biome = realm type, quest = Trial). Implement in WH as realm generator for Heart and Mind Within mode + stage variants.
- **Wire in:** `game/js/stages.js` (realm/stage generation) + `game/js/stage-variants.js` (realm variants) + Heart and Mind Within mode (story/adventure).
- **Improves:** Story mode world generation, stage variety, replayability (no two realm runs same). Priority: HIGH for story mode.

### E5. Seedwake — Seed-Based Async Multiplayer (Godot, open source pattern)
- **What:** Same seed = same world, different choices. 30-bit seed determines entire environment (7 floors, 7×7 grid, walls, stairs, enemies, collectibles, shrines). NO random numbers during gameplay — fully deterministic after generation. Imported run becomes a ghost showing where another player went + divergence point.
- **Why aligns:** DIRECT canon hit — multiverse = same world, different choices = parallel realities. Seed = realm seed, ghost = parallel-self / spirit echo. "Realms within beings within thoughts" = seed determines realm, player determines path. Ghost system = Nine Souls concept (multiple souls, same vessel, different paths).
- **Source:** https://blog.darkwood.com/article/darkwaar33-seedwake-asynchronous-multiplayer-without-a-server-1 (Godot 4.6, turn-based tactical roguelike)
- **Pull:** Borrow seed-deterministic generation + ghost replay pattern. Implement: realm seed → deterministic realm layout, ghost data (record inputs + seed, replay as ghost opponent / spirit echo).
- **Wire in:** `game/js/stages.js` (seeded realm gen) + `game/js/ghost-ai.js` (ghost replay — file already exists!) + `game/netplay/` (async multiplayer via seed + ghost, no server needed).
- **Improves:** Story replayability, async multiplayer (no server cost), ghost opponents (canon: spirit echoes). Priority: HIGH (unique + canon-aligned + cheap multiplayer).

### E6. Worldtable — AI RPG Builder (Realms from Questions)
- **What:** Design dungeons under landmarks, draft whole REALMS from three questions. Town editor, rule system editor (line by line), world open to everyone with one switch. Free tools: world generator (one sentence → world + map), town generator (town + battle maps, .dd2vtt export), name generator.
- **Why aligns:** "Draft whole realms from three questions" = WH realm creation (Five Lands, Trial realms). Town/battle map generation = stage generation for story mode. Rule system = realm laws ("colour is law" per realm).
- **Source:** https://maroon280.itch.io/worldtable/devlog/1719169/introducing-worldtable | https://worldtable.gg
- **Pull:** Borrow realm-drafting UX (3 questions → realm) + town/battle map generation patterns. Implement as WH realm creator tool (in creation suite or story mode editor).
- **Wire in:** `packages/creation-suite/` (realm creator) + `game/js/stages.js` (realm maps).
- **Improves:** Story mode worldbuilding, creator tools, realm variety. Priority: MEDIUM.

### E7. Nerulith — Endless Procedural World with Biomes (Unreal, Level Streaming)
- **What:** Endless procedurally generated worlds with level streaming (levels load/unload by distance, like Minecraft chunks). Unlimited biomes, noise-based or grid-based generation, multi-axis control (2.5D/3D), predefined levels at coordinates, world borders, level cleanup (remove unused after timeout), multiplayer replication (listen/dedicated/standalone).
- **Why aligns:** Endless realms + level streaming = WH multiverse (infinite realms, stream in/out as player travels roads). Biome = realm type. Multiplayer replication = online realms.
- **Source:** https://forums.unrealengine.com/t/nerulith-multiplayer-endless-procedural-world-with-biomes-using-level-streaming/2484277
- **Pull:** Borrow level streaming pattern (load/unload by distance, cleanup timeout) + biome system. Implement in WH as realm streaming (not all realms loaded at once — stream as player travels).
- **Wire in:** `game/js/lazy.js` (lazy loading) + `game/js/assets.js` (asset streaming) + `game/js/stages.js` (realm streaming).
- **Improves:** Performance (don't load all realms), scale (infinite realms), loading times (stream, don't block). Priority: MEDIUM-HIGH (performance + scale).

### E8. Dungeonizer — Procedural Dungeon Generator (Unity, simple + hackable)
- **What:** Lightweight procedural dungeon generator. Editor generation + runtime generation. 2D/3D tile-based, custom wall/floor prefabs, custom rooms, adjustable tile size. Focus: simple, customizable, understandable, modifiable.
- **Why aligns:** Simple dungeon/realm generation for story mode interiors (temples, shrines, Trial chambers). Hackable base = WH can adapt quickly (not a huge framework).
- **Source:** https://assetstore.unity.com/packages/tools/level-design/dungeonizer-procedural-dungeon-generator-22162
- **Pull:** Borrow room-and-corridor algorithm (simple, proven). Port to JS/Three.js for WH story interiors.
- **Wire in:** `game/js/stages.js` (dungeon/temple generation for story mode).
- **Improves:** Story mode level variety, fast prototyping. Priority: LOW-MEDIUM (simple, quick win).

## CHARACTER DESIGN / CREATION SUITE (HEART of WH)

### E9. MB-Lab — Blender Character Creator (Open source, GPL)
- **What:** Blender add-on for humanoid character creation. Morphing system (vertex-level deformations in categories: Body, Head, Face, Torso, Arms, Legs, Expressions). Preset library (common phenotypes). Auto-fitting skeleton/clothing/hair, parametric body measure, facial expressions, anime-style option with cell shader. Rigging types: base, IK, muscle, muscle_ik.
- **Why aligns:** DIRECT — WH todo list already has "MB-Lab: pull in and wire 100% end-to-end into pipeline + creation suite." Creation suite = HEART of WH (New-age MUGEN: anyone can make/bring any fighter). MB-Lab morphing = creation suite body customization.
- **Source:** https://deepwiki.com/animate1978/MB-Lab/3-character-creation-guide | GitHub: animate1978/MB-Lab (GPL)
- **Pull:** MB-Lab Blender add-on (already in WH todo — execute it). Wire morphing parameters into WH creation suite (body sliders → MB-Lab morphs → export GLB → WH rig).
- **Wire in:** `packages/creation-suite/` (body customization) + `game/js/custom-fighter.js` (custom fighter pipeline) + `game/js/attires.js` (attire system). Use Kaggle GPU for batch morph + export.
- **Improves:** Creation suite depth (real body customization, not just attire swap), user-generated fighters. Priority: HIGH (already in todo, creation suite = heart).

### E10. MakeHuman / MPFB — Parametric Human Generator (CC0 / Open source)
- **What:** MakeHuman: parametric human generation (age, gender, ethnicity, body proportions) via linear interpolation, high-quality mesh optimized for subdivision/sculpting, CC0 license (no rights reserved — full freedom). MPFB (MakeHuman for Blender): one-click humanoid mesh, parametric body, automatic rigging (Rigify, IK/FK), procedural skin/eyes materials, asset library (clothes, body parts, materials).
- **Why aligns:** Same as MB-Lab — creation suite base mesh generation. CC0 = no license friction. MPFB auto-rigging + Rigify = faster rig pipeline (complements UniRig).
- **Source:** http://www.makehuman.org/ | https://static.makehumancommunity.org/mpfb/about.html | MakeHuman 1.0 (CGW: https://www.cgw.com/Press-Center/News/2014/MakeHuman-Open-Source-Software-Released-in-Versi.aspx)
- **Pull:** MakeHuman (standalone) + MPFB (Blender plugin). Wire parametric generation into creation suite (sliders → base mesh → rig → WH).
- **Wire in:** `packages/creation-suite/` (base mesh generation) + UniRig pipeline (rig the generated mesh).
- **Improves:** Creation suite (fast base mesh, no manual modeling), rig pipeline (auto-rig option). Priority: HIGH (complements MB-Lab, CC0 = clean).

### E11. Tripo AI Open Source (30+ projects, 2024+)
- **What:** Tripo AI released 30+ open source projects covering full 3D stack: single-image 3D generation, automatic rigging, adaptive resolution control, unified animatable asset generation, physically assemblable model synthesis. Outputs work directly in game engines without manual cleanup. Partners: ByteDance, Bambu Lab, Sony, HTC, Unity, Replit.
- **Why aligns:** WH already uses Tripo (Tripo3D intake, tripo-intake.html, tripo-fighters.json). Tripo open source = deeper integration (not just API — run models locally on Kaggle GPU, customize pipeline). Automatic rigging = complements UniRig. Animatable asset generation = characters that move, not just static models.
- **Source:** https://blog.siggraph.org/2026/08/the-teapot-test-reimagined-from-showing-to-making-with-tripo-ai.html/ | Tripo: https://www.tripo3d.ai/ | Tripo open source: GitHub (TripoSG, TripoSG-3D, etc.)
- **Pull:** Tripo open source repos (esp. auto-rigging, animatable generation). Run on Kaggle GPU (2x T4). Wire into WH pipeline (Tripo gen → auto-rig → WH anim bank).
- **Wire in:** `game/tripo-intake.html` (intake) + UniRig pipeline (rigging) + `game/assets/` (output).
- **Improves:** Model generation speed/quality, auto-rigging, animatable characters. Priority: HIGH (already using Tripo, deepen it).

### E12. Scenario Blender Plugin (GPL-3.0, open source)
- **What:** Blender plugin bringing image, video, 3D, material, audio, panorama generation into viewport. 9 lanes: Image, Video (Seedance, Kling, Veo, Wan, LTX), 3D (Meshy, Rodin, Tripo, Hunyuan), Gaussian splat worlds (Marble, TripoSplat). Features: remeshing, retexturing, UV unwrapping, rigging, animation, part separation. Local MCP server (AI clients inspect/modify scene). Blender 5.0+, GPL-3.0, 560 GitHub stars.
- **Why aligns:** All-in-one Blender generation + editing (3D + rigging + animation + retexturing in one place). WH pipeline is Blender-heavy (rigging, retargeting, mesh fixes). Scenario plugin = faster asset iteration inside Blender, no browser round-trips.
- **Source:** https://alphasignal.ai/news/scenario-opens-its-ai-blender-plugin-to-generate-3d-assets-inside-viewport | GitHub: Scenario (GPL-3.0)
- **Pull:** Scenario Blender plugin. Install in WH Blender pipeline. Use for: model generation, retexturing, remeshing, rigging, part separation.
- **Wire in:** Blender pipeline (WH asset workflow) + `game/assets/` (output). Use Kaggle GPU for generation calls.
- **Improves:** Asset iteration speed (no browser round-trip), retexturing/remeshing in one tool. Priority: MEDIUM (Blender pipeline boost).

## 3D GENERATION / ENVIRONMENTS / ITEMS

### E13. Muapi Unified 3D API (Tripo + Meshy, $0.20/gen)
- **What:** Single REST endpoint for 8 models across Tripo3D + Meshy: text-to-3D, image-to-3D, multi-view reconstruction. Configurable topology, polycount, PBR materials. Output: game-ready .glb (+ FBX/OBJ/USDZ on Meshy). From $0.20 per generation.
- **Why aligns:** WH already uses Tripo + Meshy separately. Unified API = one integration for both, cheaper/faster batch generation (models, environments, items/props). Multi-view reconstruction = better accuracy for asymmetric objects (weapons, items).
- **Source:** https://muapi.ai/ai-3d-model-api
- **Pull:** Muapi API key (via browser, user approval for paid API if needed — $0.20/gen is cheap, but confirm budget). Wire batch generation script (prompt list → Muapi → GLB → WH pipeline).
- **Wire in:** `game/tripo-intake.html` (extend to Muapi) + asset pipeline (batch gen).
- **Improves:** Model/item/environment generation speed + cost (one API, two providers). Priority: MEDIUM (if Tripo direct already works, Muapi is convenience + Meshy access).

### E14. Gaussian Splat Worlds (TripoSplat, Marble)
- **What:** Represent scenes as collections of rendered 3D points (Gaussian splats) instead of meshes. Fast rendering, photorealistic environments from photos/video, small file sizes for complex scenes.
- **Why aligns:** WH stages/arenas could use splats for background environments (distant mountains, skies, complex scenery) while fighters remain meshes. Faster load + better visuals for environments. "Colour is law" — splats preserve color/lighting beautifully.
- **Source:** Via Scenario plugin (see E12) + TripoSplat (Tripo open source) + Marble (Gaussian splat world gen)
- **Pull:** TripoSplat / Marble tools. Generate splat environments for WH stages (from photos or Tripo gen).
- **Wire in:** `game/js/stages.js` (splat background layer) + `game/js/scene.js` (render splats + meshes together).
- **Improves:** Stage visuals (photoreal backgrounds, fast load), arena quality (user law: upgrade graphics quality, preserve colors). Priority: MEDIUM (visual upgrade, after combat foundation).

## MENU UI SYSTEMS

### E15. Fighter Creator / MUGEN Menu Editor (MUGEN Guild)
- **What:** MUGEN fighting game engine with menu editor: create title screens, character/stage selects, option menus, link GameModes to menus (VS button → character select → linked game mode). Stage editor (load level, setup shaders/particles/objects/lights/events in real time). Character editor (link objects to characters: weapons, lights, particles). Cinematic editor (intros, stage views, story scenes). SFX editor (explosions, hitsparks, reusable effects).
- **Why aligns:** WH is "New-age MUGEN" — MUGEN's menu/mode linking is the ORIGINAL pattern WH is modernizing. Menu editor → WH menu system (but WH menus must be from teardowns, per user law — borrow STRUCTURE, not visuals). Mode linking → WH modes.js.
- **Source:** https://mugenguild.com/forum/topics/fighter-creator-131679.80.html | MUGEN engine (Elecbyte)
- **Pull:** Study MUGEN menu/mode structure (docs, community guides). Borrow: menu → mode linking pattern, stage editor event pattern, SFX reuse pattern.
- **Wire in:** `game/js/menus.js` (menu structure) + `game/js/modes.js` (mode linking) + `game/js/hitfx.js` (SFX reuse).
- **Improves:** Menu/mode architecture (proven MUGEN pattern), SFX system (reusable effects). Priority: MEDIUM (architecture reference, WH menus stay teardown-based per law).

### E16. Code-Drawn HUD (MEATKLAW pattern)
- **What:** MEATKLAW prototype 0.7.2 rebuilt HUD: health as gems in gold frame (not bars), button prompts (keyboard/mouse/controller icons, bigger/sharper, follow input device), consistent look (counters, name tags, dialogue boxes share finish), readable at any size (drawn in code, not sprite sheets), scalable via HUD Scale option, contextual culling (elements hidden unless in context).
- **Why aligns:** WH HUD needs: phone-first (portrait + landscape), readable at small size, scalable, contextual (don't clutter fight). Code-drawn (not sprites) = crisp at any resolution, easy to theme per character/realm ("colour is law" — HUD color per realm/soul).
- **Source:** https://astt0r.itch.io/meatklaw/devlog/1719520/prototype-072-new-hud
- **Pull:** Borrow HUD patterns: code-drawn frames (Canvas/SVG, not sprites), scalable HUD (user setting), contextual culling (hide meters unless relevant), input-device-aware prompts (touch vs controller vs keyboard).
- **Wire in:** `game/js/ui-screen.js` (HUD) + `game/css/` (HUD styles) + fight HUD (health, meter, timer).
- **Improves:** HUD readability on phone, HUD scalability, fight immersion (no clutter). Priority: MEDIUM (HUD polish, after core fight works).

## LOADING / PERFORMANCE

### E17. meshoptimizer / gltfpack (MIT, measured 59% reduction)
- **What:** Mesh optimization library. gltfpack: optimizes meshes for vertex fetch + transform cache, quantizes geometry, merges meshes (fewer draw calls), quantizes/resamples animations, prunes node tree, simplifies meshes on request. Output: regular .glb/.gltf (KHR_mesh_quantization, three.js r111+) or compressed (EXT_meshopt_compression, three.js r122+). Texture compression: Basis Universal in KTX2 (-tc) or WebP (-tw). Measured: test plant 319,648 → 130,296 bytes (59.2% reduction), decoded vertex attributes IDENTICAL, first-frame median 35.7ms → 17.6ms.
- **Why aligns:** WH load times + phone performance (see Gap 19). Cape 1.6M verts → optimized. All WH GLBs should go through gltfpack before deploy. Three.js native support (no custom loader needed, just setMeshoptDecoder).
- **Source:** https://meshoptimizer.org/gltf/ | GitHub: zeux/meshoptimizer (MIT) | Measurement: https://medium.com/@1228566953qq/three-js-glb-loading-cache-decode-and-the-first-gpu-frame-bead0f5691ab
- **Pull:** gltfpack binary (native, faster for large files). Wire into build pipeline: every GLB → gltfpack -cc -tc → optimized GLB → deploy. Use Kaggle GPU? No — gltfpack is CPU, but fast (native binary). Run in CI on every PR that touches models.
- **Wire in:** Build pipeline (new script: tools/optimize-models.sh) + `game/js/assets.js` (setMeshoptDecoder for EXT_meshopt_compression) + CI (optimize check).
- **Improves:** Load times (59% smaller files), FPS (fewer draw calls, better cache), phone performance. Priority: HIGH (see Gap 19).

### E18. gltf-progressive + Needle Cloud Optimization (LOD streaming)
- **What:** gltf-progressive: small npm package for vanilla three.js + <model-viewer>, progressive LOD streaming (load low-res first, high-res in background). Needle Cloud: upload 3D file → optimized glTF with Draco/Meshopt compression, KTX2 textures, automatic LODs, CDN URL. Works with plain three.js, no lock-in. Free tier: 30 optimizations.
- **Why aligns:** WH fight load: show low-res fighter immediately, stream high-res in background (no 6% stall → bounce). Stage streaming: low-LOD stage first, high-LOD background. Complements Gap 18 (background preloading).
- **Source:** https://cloud.needle.tools/articles/needle-cloud-optimization | gltf-progressive (npm) | Three.js tips: https://www.utsubo.com/blog/threejs-best-practices-100-tips (progressive loading, Web Workers, OffscreenCanvas, chunk streaming)
- **Pull:** gltf-progressive npm package. Wire into assets.js loader (low → high swap). Use Needle Cloud for automatic LOD generation (or generate LODs via gltfpack simplification).
- **Wire in:** `game/js/assets.js` (progressive loader) + `game/js/lazy.js` (LOD streaming) + `game/js/load-progress.js` (progress shows LOD stage).
- **Improves:** Perceived load time (fighter visible fast), actual load time (stream, don't block), phone UX (no frozen bar). Priority: HIGH (user loading complaints).

### E19. Three.js Performance Patterns (code-splitting, Web Workers, OffscreenCanvas)
- **What:** Proven Three.js optimizations: code-split modules (don't bundle everything upfront, dynamic import), preload critical assets (<link rel=preload>), progressive loading (low → high), offload physics/procgen/asset processing to Web Workers, OffscreenCanvas (render in worker, main thread never blocks on frames), chunk streaming (load visible chunks by camera position), instancing (90% draw call reduction for crowds/particles), LOD (1.5-3x FPS), Draco (50% load time), draw call budget (<100/frame for 60fps), stats-gl profiling.
- **Why aligns:** WH is Three.js/web, phone-first. Every pattern applies directly. WH already has lazy.js + loadperf.js (performance measurement) — these patterns are the fixes loadperf would recommend.
- **Source:** https://www.utsubo.com/blog/threejs-best-practices-100-tips | https://r3f.docs.pmnd.rs/advanced/scaling-performance | https://copyprogramming.com/howto/javascript-threejs-render-how-work-code-example | https://moldstud.com/articles/p-optimizing-threejs-for-low-bandwidth-environments
- **Pull:** No single repo — patterns to implement in WH code. Audit WH against checklist, implement missing patterns one by one.
- **Wire in:** `game/js/lazy.js` (code-splitting + lazy load) + `game/js/loadperf.js` (profiling) + `game/js/assets.js` (preload + streaming) + fight loop (Web Worker for physics? OffscreenCanvas for render? — evaluate).
- **Improves:** FPS, load times, phone smoothness, input responsiveness (main thread not blocked). Priority: HIGH (phone-first performance).

## STORY / CANON (Heart and Mind Within, Nine Souls, Multiverse)

### E20. Ink — Branching Narrative Language (MIT, Inkle)
- **What:** Scripting language optimized for choice-driven prose, branching narrative, procedural narrative, state tracking. Unity plugin (official), used by 80 Days, Sorcery!, A Highland Song. MIT open source. Writers write in Ink (text), engine runs it.
- **Why aligns:** Heart and Mind Within story mode: branching story (player choices → different soul paths, Trial outcomes, realm routes). Nine Souls: choices affect which soul vessel / path. Ink variables = soul state, Trial progress, realm flags. "Variables trump branching" (state-driven scales better than duplicating scenes).
- **Source:** https://game-ace.com/blog/narrative-game-design/ (comparison table: Ink MIT, Unity plugin, small to large) | Inkle: https://www.inklestudios.com/ink/ | GitHub: inkle/ink (MIT)
- **Pull:** Ink runtime (JS port: inkjs — runs Ink in browser/JS). Write Heart and Mind Within story in Ink (chapters, choices, soul variables, Trial gates).
- **Wire in:** `game/js/heartmind.js` (story mode) + `game/js/episodes.js` (episodes) + `game/js/story-endings.js` (endings by soul state). Ink JSON → WH story engine.
- **Improves:** Story mode depth (real branching, not linear), writer workflow (writers write Ink, not code), replayability (different soul paths). Priority: HIGH for story mode (after combat foundation).

### E21. Yarn Spinner — Dialogue System (MIT, Unity/Godot)
- **What:** Dialogue system for games, character dialogue + quest lines, visual branching, Unity + Godot official plugins, MIT open source. Used by Night in the Woods, Unpacking. Writers use visual editor (non-technical friendly), engine runs dialogue trees.
- **Why aligns:** WH character dialogue (versus banter, story dialogue, NPC dialogue in Heart and Mind Within). Versus-banter.js already exists — Yarn Spinner is the WRITER-FRIENDLY way to author banter/dialogue (visual nodes, not code). Quest lines = Trial quests, soul quests.
- **Source:** https://game-ace.com/blog/narrative-game-design/ (Yarn MIT, Unity/Godot) | Yarn Spinner: https://yarnspinner.dev/ | GitHub: YarnSpinnerTool/YarnSpinner (MIT)
- **Pull:** Yarn Spinner JS runtime (or port dialogue format to WH). Author versus banter + story dialogue in Yarn (visual editor).
- **Wire in:** `game/js/versus-banter.js` (banter) + `game/js/heartmind.js` (story dialogue) + `game/js/episodes.js`.
- **Improves:** Dialogue authoring (writers, not coders), banter variety, story dialogue depth. Priority: MEDIUM (story mode tooling).

### E22. Twine — Interactive Fiction Prototyping (Free, open source)
- **What:** Visual branching editor, no coding required, exports to HTML/JS. Entry-level standard for prototyping interactive fiction. 2.3M creators (with ChoiceScript, Ren'Py, Yarn). Best for: prototyping, testing narrative structures before full implementation.
- **Why aligns:** Prototype Heart and Mind Within story branches FAST in Twine (visual flowchart) before committing to Ink/Yarn implementation. Test soul paths, Trial structures, realm routes with user (owner) before building.
- **Source:** https://game-ace.com/blog/narrative-game-design/ | Twine: https://twinery.org/ | GitHub: killerfish/twinejs (open source)
- **Pull:** Twine (browser tool, no install). Prototype story in Twine, export HTML, test with owner, then implement winning branches in Ink.
- **Wire in:** Story prototyping workflow (Twine → owner review → Ink implementation). NOT in game code — in design workflow.
- **Improves:** Story design speed (prototype in hours, not weeks), owner feedback loop (play prototype, approve branches). Priority: MEDIUM (design tool, not game code).

## MULTIPLAYER / ONLINE

### E23. GGPO (see E1) + Fightcade Pattern (Spectating, Lobbies)
- **What:** Fightcade: GGPO-based client with matchmaking, challenges, spectating, chat. Superseded original GGPO client. Pattern: lobby → challenge → match → spectate + chat.
- **Why aligns:** WH online.js already has lobbies + tournaments (TTT2 + SFV lineage). Fightcade pattern adds: spectating (watch matches), challenge system (request fight from lobby), chat. WH tournament mode + spectator mode for show (Cape Jones show = fights as content).
- **Source:** Fightcade: https://www.fightcade.com/ | GGPO: https://github.com/pond3r/ggpo
- **Pull:** Borrow Fightcade UX patterns (lobby list → challenge → spectate). Implement spectating in WH netplay (watch live match, ghost data).
- **Wire in:** `game/js/online.js` (lobby + challenge) + `game/netplay/lobby/` (spectate) + `game/js/ghost-ai.js` (spectator ghost?).
- **Improves:** Online community (spectating = content), tournament viewing, show integration (fights as show). Priority: MEDIUM (online depth).

## AUDIO / MUSIC

### E24. FMOD Studio + Wwise — Adaptive Music Middleware (Free indie tiers)
- **What:** FMOD Studio: visual timeline + parameters for adaptive music, widely used by indies. Wwise: deep interactive music system (Music Switch Containers, Music Playlist Containers, RTPC parameters, beat/bar-boundary transitions, vertical remixing via stems), profiling, large-team workflows. Both free/low-cost for smaller projects.
- **Why aligns:** WH music.js is file-based BGM (one per stage, crossfade, intensity scaling) — good start, but NOT adaptive (no stem layering, no beat-boundary transitions, no parameter-driven intensity). User wants rotating music + Nosferatu tracks + Tekken-style music. FMOD/Wwise patterns = real adaptive music (intensity → add percussion/brass stems, calm → drop to pad, transitions on beat boundaries).
- **Source:** FMOD: https://www.fmod.com/ (free indie tier) | Wwise: https://www.audiokinetic.com/ (free indie tier) | Adaptive music explainer: http://dev.to/aplusgamesstudio/video-game-music-how-it-is-composed-and-implemented-1969 | Stems explainer: https://www.mozratai.com/blog/adaptive-music-fmod-wwise-stems.html | Wwise/FMOD export tool: ScoreCanvas (https://backpocketmusic.com/)
- **Pull:** Study FMOD/Wwise adaptive patterns (Music Switch, Transition Matrix, RTPC, stems). Implement WH-native adaptive music in music.js (NOT full FMOD/Wwise SDK — WH is web/Three.js, middleware SDKs are native; borrow PATTERNS: stem layering, beat-boundary transitions, intensity parameters).
- **Wire in:** `game/js/music.js` (adaptive engine: stems + intensity + transitions) + `game/data/music-library.json` (stem definitions per track) + Nosferatu tracks (cut into stems? Or tracks as stems — see music lane).
- **Improves:** Music feel (adapts to fight intensity, not just loops), rotating music done RIGHT (musical transitions, not hard cuts), Tekken-style music (T7 raises mix as fight heats up — WH already has intensity scaling, make it stem-based). Priority: MEDIUM-HIGH (music is user priority — Nosferatu + rotating + Tekken-style).

### E25. Unreal MetaSounds — Procedural Audio (Node-based)
- **What:** Unreal's built-in procedural, node-based audio. Generate + modify procedural sound at runtime while receiving parameters from gameplay. No middleware needed. Procedural = sound synthesized at runtime (not pre-recorded files).
- **Why aligns:** WH is web, not Unreal — but MetaSounds PATTERN (node-based procedural audio) can be implemented in Web Audio API (WH already uses Web Audio via audio.js). Procedural SFX (hits, whooshes, impacts) with parameters (force, speed, material) = varied SFX without 100s of files. Reduces repetition fatigue (user complaint: repetition makes game feel small).
- **Source:** Unreal MetaSounds docs (Epic) | Procedural audio explainer: https://aicompetence.org/ai-game-sound-design/ (MetaSounds = procedural audio environment, parameter-driven)
- **Pull:** Borrow node-graph procedural audio pattern. Implement in WH audio.js via Web Audio API nodes (oscillator + noise + filter + envelope, parameterized by hit force/speed).
- **Wire in:** `game/js/audio.js` (procedural SFX nodes) + `game/js/hitfx.js` (hit sounds parameterized by move).
- **Improves:** SFX variety (no repetition), file size (procedural = tiny, not MBs of WAVs), hit feel (sound matches impact force). Priority: MEDIUM (audio polish, after music system).

## PHYSICS / VFX

### E26. Rapier3D Ragdoll (Three.js, WASM, open source)
- **What:** Rapier physics engine (Rust → WASM, @dimforge/rapier3d-compat). Ragdoll: each body part = Dynamic Rigid Body, joints = constraints (shoulder, hip, etc.). Sync loop: world.step() → copy rigid body position/rotation → Three.js bone. Works with standard GLTF from Blender (bone naming map).
- **Why aligns:** WH ragdoll vision (user-locked): Euphoria (RDR) + Gang Beasts + Human Fall Flat + Tekken mix, contextual ONLY (launches, KOs, wall splats). WH already has physics.js, softbody.js, jiggle.js, cloth-hair.js, springbones.js — Rapier ragdoll is the RIGID BODY complement (for KO/launch ragdoll, not just jiggle/cloth).
- **Source:** https://dev.to/mattvb91/realistic-ragdoll-physics-in-threejs-1pko | GitHub: mattvb91/rapierjs-ragdoll | Rapier: https://rapier.rs/ (Apache-2.0)
- **Pull:** @dimforge/rapier3d-compat (npm, WASM). Implement ragdoll: on KO/launch/wall splat (contextual only, per user law), switch from animation to ragdoll (rigid bodies + joints), sync to bones, switch back on landing/get-up.
- **Wire in:** `game/js/physics.js` (ragdoll world) + `game/js/fighter.js` (KO/launch → ragdoll trigger, contextual only) + bone map (existing Alisa/Cape bone maps).
- **Improves:** KO/launch feel (Euphoria-like weight, not canned fall), ragdoll vision delivery. Priority: MEDIUM (after combat foundation, user sequencing: ragdoll after combat).

### E27. Position-Based Ragdoll (No Engine, Three.js, Samurai Template)
- **What:** Ragdoll WITHOUT physics engine: skeleton = particle per joint, bones = distance constraints, relaxed few times per substep (position-based, predict → project → read velocity). Mass (pelvis/chest heavy, hands/feet light, inverse mass split), Bracing (extra constraints across pelvis/chest/spine for shape), Limits (knee bends one way only, hip-ankle distance floored/capped). Handover: mixer stopped mid-frame, solver's first pose = clip pose at impact (death looks like same body). Twist rebuilt from frame (pelvis/chest full orientation from two directions).
- **Why aligns:** Lighter than Rapier (no WASM, pure JS, phone-friendly). Position-based = survives hit-stop + paused clock (WH has hitstop). Handover mid-frame = KO looks like same body (not teleport to ragdoll). Euphoria-like weight via mass + bracing (not full Euphoria, but close, cheap).
- **Source:** https://github.com/achrefelouafi/SamuraiThirdPersonTemplateThreeJS (ragdoll section, detailed writeup)
- **Pull:** Borrow position-based ragdoll algorithm (particle + constraints + mass + bracing + limits + mid-frame handover). Implement in WH physics.js as lightweight alternative to Rapier (or primary, if Rapier WASM is heavy on phone).
- **Wire in:** `game/js/physics.js` (position-based solver) + `game/js/fighter.js` (KO/launch trigger, contextual only).
- **Improves:** Same as E26 but lighter/faster on phone, hit-stop compatible. Priority: MEDIUM (evaluate vs Rapier — pick one, or use position-based for phone, Rapier for desktop).

### E28. Cloth + SpringBone Physics (Three.js, open source)
- **What:** Cloth Simulation (Three.js, Verlet integration + distance constraints, wind, pinning modes, obstacle collision). three-mmd physics: Ammo.js (Bullet WASM, rigid body, accurate) + SpringBone (VRM spring joints, lightweight hair/clothing, bone name matching, IK/FK).
- **Why aligns:** WH already has cloth-hair.js, jiggle.js, springbones.js, softbody.js — these projects are the REFERENCE implementations to compare/upgrade against. Cape cloth (Cape Jones cape!) needs cloth sim. Hair needs SpringBone. WH cape is a character feature (Cape Jones) — cloth must work.
- **Source:** Cloth: https://github.com/shInNei/Cloth-Simulation | three-mmd physics: https://deepwiki.com/moeru-ai/three-mmd/3.4-rendering-and-materials
- **Pull:** Compare WH cloth-hair.js / springbones.js against these references. Borrow: Verlet cloth solver, SpringBone joint pattern, collider + joint helpers.
- **Wire in:** `game/js/cloth-hair.js` (cape + hair) + `game/js/springbones.js` (hair/clothing) + `game/js/softbody.js`.
- **Improves:** Cape/hair/cloth realism (Cape Jones cape must flow, not clip/tear), character polish. Priority: MEDIUM (Cape Jones show + game, cape is signature).

### E29. Euphoria-Style Active Ragdoll (Research / Pattern)
- **What:** Euphoria (NaturalMotion): ragdoll + procedural animation + behavioral layer. Characters try to protect head when falling, tumble down steps (not slide), grab objects to avoid falling, clutch wounds, stumble/fall/catch themselves when injured. "Will to live" — weighted logic, not limp ragdoll. Used in GTA IV/V, RDR/RDR2, Max Payne 3, Force Unleashed, Backbreaker.
- **Why aligns:** WH ragdoll vision EXPLICITLY cites Euphoria as template ("Mix: Euphoria (RDR) + Gang Beasts + Human Fall Flat + Tekken"). Active ragdoll = WH's target (not limp, not always-on, contextual: launches, KOs, wall splats).
- **Source:** https://tvtropes.org/pmwiki/pmwiki.php/Main/RagdollPhysics (Euphoria section) | https://ludonodestudios.medium.com/beyond-ragdolls-mastering-weighted-character-logic-and-euphoria-physics-23290536dc4a | http://renewablesadvice.com/physics-suggest-004/euphoria-ragdoll-physics.pdf
- **Pull:** No open source Euphoria (proprietary, NaturalMotion). Borrow PATTERNS: procedural layering over ragdoll (muscle stiffness, balance system, protective reflexes, stumble recovery). Implement as: ragdoll + procedural muscle (joint motors with strength/damping/torque limits + balance: center of mass over feet, nothing pinned).
- **Wire in:** `game/js/physics.js` (active ragdoll: ragdoll + muscle + balance) + `game/js/fighter.js` (contextual triggers only).
- **Improves:** Ragdoll vision delivery (Euphoria-like, not limp). Priority: MEDIUM (research pattern, implement after basic ragdoll works).

## OTHER (VFX, Particles, Shaders, Lighting)

### E30. Particle / VFX Systems (Three.js, GPU)
- **What:** GPU particle systems (instancing, compute shaders for physics/particles, 2-10x speedup via compute). Hit sparks, aura effects (Soul Surge aura, Soul Urge blue fire, Rage red aura), stage effects (dust, debris on breaks).
- **Why aligns:** WH has hitfx.js, hitfx-nebula.js, lighting-rig.js. T7 hit effects (sparks, aura) are part of fight feel. Soul Surge / Soul Urge / Rage auras need VFX (per-character aura per fighter.js header: "per-character aura").
- **Source:** Three.js performance guide (instancing, compute shaders): https://copyprogramming.com/howto/javascript-threejs-render-how-work-code-example | https://r3f.docs.pmnd.rs/advanced/scaling-performance
- **Pull:** GPU particle patterns (instanced particles, compute shader physics). Implement hit sparks (parameterized by move), aura shaders (per-character color, per soul), break debris (wall/floor break particles).
- **Wire in:** `game/js/hitfx.js` + `game/js/hitfx-nebula.js` (particles) + `game/js/lighting-rig.js` (aura lighting).
- **Improves:** Fight feel (hits look powerful), aura systems (Soul Surge/Urge/Rage visible), stage breaks (debris). Priority: MEDIUM (feel/polish, after core fight).

---

# PART 4 — PRIORITIZED PULL LIST (what to pull next, in order)

## TIER 1 — DO FIRST (T7 feel + load times + phone performance)
1. **Power Crush implementation** (Gap 1) — T7 move flags + combat-core armor logic. Source: T7 frame data (wavu.wiki, TheBigTuna). Wire: combat-core.js + hitdetect.js + movesets.
2. **Screw / Tailspin implementation** (Gap 2) — T7 Screw move flags + Screw state + once-per-combo rule. Source: T7 frame data. Wire: combat-core.js + movesets. (Keep Bound for low parry only.)
3. **Per-move hitbox data** (Gap 3) — T7 hitbox extraction + per-move boxes. Source: T7 files / TekkenMods hitbox viewers. Wire: hitbox.js + hitdetect.js + movesets.
4. **T7 animation banks** (Gap 4) — Already in batch extraction lane. Continue + wire into anim/t7/ + moveset anim_ref.
5. **T7 moveset coverage for all 157 files** (Gap 5) — Already in batch lane. Continue + DLC frame data (wavu.wiki).
6. **meshoptimizer / gltfpack pipeline** (Gap 19, E17) — Optimize ALL GLBs before deploy. Source: https://meshoptimizer.org/gltf/ (MIT). Wire: build script + assets.js (MeshoptDecoder) + CI.
7. **Progressive LOD loading** (Gap 18, E18) — Low-res first, high-res background. Source: gltf-progressive (npm) + Needle Cloud. Wire: assets.js + lazy.js + load-progress.js.
8. **Three.js performance patterns** (E19) — Code-splitting, Web Workers, preload, chunk streaming, draw call budget. Audit WH against checklist, implement missing.

## TIER 2 — DO NEXT (Online + Creation + Story)
9. **GGPO rollback netcode** (E1) — Port to WASM, wire into netplay/sim + mirror. Source: https://github.com/pond3r/ggpo (MIT).
10. **MB-Lab + MakeHuman/MPFB full wiring** (E9, E10) — Already in todo, execute 100%. Source: MB-Lab (GPL), MakeHuman (CC0), MPFB (open source). Wire: creation-suite + custom-fighter.js.
11. **Tripo open source deepening** (E11) — Auto-rigging + animatable generation on Kaggle GPU. Source: Tripo GitHub (open source). Wire: tripo-intake + UniRig pipeline.
12. **Ink story engine** (E20) — Heart and Mind Within branching story. Source: https://github.com/inkle/ink (MIT) + inkjs. Wire: heartmind.js + episodes.js + story-endings.js.
13. **Seed-based realm generation + ghosts** (E5) — Deterministic realms + ghost opponents. Source: Seedwake pattern. Wire: stages.js + ghost-ai.js + netplay.
14. **Node-based realm generation** (E4) — Five Lands + nested realms + Trial quests. Source: Nathan Savant procgen. Wire: stages.js + stage-variants.js + story mode.
15. **Adaptive music (stem-based)** (E24) — FMOD/Wwise patterns in WH music.js (stems + intensity + beat transitions). Source: FMOD/Wwise docs (patterns, not SDK). Wire: music.js + music-library.json + Nosferatu stems.

## TIER 3 — DO AFTER (Polish + Modes + Depth)
16. **Soul Urge completeness** (Gap 8) — Per-character Engagers, Heat Dash cancel, Heat Smash category, Heat Burst. Source: T8 files. Wire: soulurge.js + fighter.js + movesets.
17. **Recoverable health** (Gap 7) — White gauge + attack-to-recover. Source: T8 docs. Wire: fighter.js + HUD.
18. **Wall splat state** (Gap 9) — Distinct splat state vs break. Wire: combat-core.js + stagebreaks.js + arena.
19. **Tornado** (Gap 6) — T8 extender (after Screw done). Source: T8 files. Wire: combat-core.js.
20. **Ragdoll (position-based + active)** (E26/E27/E29) — Contextual only (KO/launch/wall splat). Source: Rapier + Samurai template + Euphoria patterns. Wire: physics.js + fighter.js.
21. **Cloth/SpringBone upgrade** (E28) — Cape + hair. Source: Cloth-Simulation + three-mmd. Wire: cloth-hair.js + springbones.js.
22. **Jukebox** (Gap 11) — Prior Tekken soundtracks + Nosferatu in rotation. Wire: music.js + music-library.json + UI.
23. **Treasure Battle** (Gap 13) — Endless + loot chests + customization. Wire: modes.js + unlockables.js + customization.
24. **Character select 5.10 features** (Gap 14) — Favorites, last-costume, tournament lock, streaming mode. Wire: select-screen.js + versus-setup.js.
25. **VS/result screen depth** (Gap 15) — Rank, W-L, connection bars, result options. Wire: versus-setup.js + online.js.
26. **Yarn Spinner dialogue** (E21) — Writer-friendly banter + story dialogue. Source: YarnSpinner (MIT). Wire: versus-banter.js + heartmind.js.
27. **Twine story prototyping** (E22) — Prototype story branches fast, owner review, then Ink. Workflow tool, not game code.
28. **Castagne architecture reference** (E2) — Character module + editor patterns. Reference for creation-suite + netplay, not port.
29. **MUGEN menu/mode patterns** (E15) — Menu → mode linking, SFX reuse. Reference for menus.js + modes.js + hitfx.js (WH menus stay teardown-based per law).
30. **Code-drawn HUD** (E16) — Scalable, contextual, input-aware HUD. Wire: ui-screen.js + HUD CSS.
31. **Gaussian splat stages** (E14) — Photoreal stage backgrounds. Source: TripoSplat/Marble. Wire: stages.js + scene.js.
32. **Procedural SFX (MetaSounds pattern)** (E25) — Web Audio node-based procedural hits. Wire: audio.js + hitfx.js.
33. **GPU particles / aura VFX** (E30) — Hit sparks, Soul auras, break debris. Wire: hitfx.js + hitfx-nebula.js + lighting-rig.js.
34. **Item moves** (Gap 10) — T7 item attacks gated by equipped item. Wire: movesets + customization.
35. **Gallery (WH-canon)** (Gap 12) — WH story cinematics + endings + show content. Wire: menus (Collection/Gallery).
36. **Replay theater** (Gap 20) — Save/share/analyze replays. Wire: replay-analysis.js + sim-match.js + menus.
37. **In-fight frame data overlay** (Gap 21) — Optional live overlay. Wire: fighter.js + hitbox.js + UI.
38. **Announcer bank** (Gap 16) — Round/KO/Perfect calls. Wire: audio.js + voice.js.
39. **Multi-level stage geometry** (Gap 17) — Full multi-level stages (not just drop). Wire: stagebreaks.js + stages.js.
40. **Scenario Campaign structure** (Gap 22) — Beat-em-up + Tekken combat for Heart and Mind Within. Wire: story mode.
41. **Scenario Blender plugin** (E12) — In-Blender generation + editing. Source: Scenario (GPL-3.0). Wire: Blender pipeline.
42. **Muapi unified API** (E13) — Tripo+Meshy in one API, $0.20/gen. Wire: tripo-intake + asset pipeline (if budget approved).
43. **Fightcade spectating pattern** (E23) — Lobby → challenge → spectate + chat. Wire: online.js + netplay/lobby/.
44. **Frame data wiki patterns** (E3) — Display + community editing. Wire: movelist-ui.js + fightlab-gungaku.js.
45. **Dungeonizer rooms** (E8) — Simple dungeon gen for story interiors. Wire: stages.js.
46. **Worldtable realm drafting** (E6) — 3-questions → realm creator tool. Wire: creation-suite + stages.js.
47. **Nerulith streaming** (E7) — Realm streaming by distance + cleanup. Wire: lazy.js + assets.js + stages.js.

---

# PART 5 — HOW WH SHOULD FEEL LIKE A MIX OF ALL TEKKEN GAMES (100% pull target)

To feel like a mix of ALL Tekken games (not just T7), WH needs:
- **T3:** Animation banks (HAVE — 22 banks), frame data foundation (HAVE), soundtrack (PULL — Jukebox, Gap 11), stages (PULL — T3 stages as WH arenas? Check canon)
- **T5:** Customization depth (PARTIAL — expand), Devil Within side-game pattern (PULL — side-games.html depth), soundtrack (PULL — Jukebox)
- **T6:** Bound (HAVE, but T7-correct = Bound only on low parry), Scenario Campaign (PULL — Gap 22), Rage (HAVE — T6 origin, T7 kept 25%), soundtrack (PULL — Jukebox), stages with floor breaks (HAVE via stagebreaks.js)
- **TTT2:** Tag system (HAVE — tag-relay.js), Fight Lab (HAVE — fightlab-gungaku.js), Balcony Break (HAVE — stagebreaks.js), Tag Assault/Crash (HAVE), soundtrack (PULL — Jukebox), customization (PARTIAL)
- **T7:** Rage/Art/Drive (HAVE), Power Crush (MISSING — Gap 1, PULL NOW), Screw (MISSING — Gap 2, PULL NOW), Wall/Floor/Balcony Breaks (HAVE), Jukebox (MISSING — Gap 11), Treasure Battle (PARTIAL — Gap 13), Gallery (MISSING WH-equivalent — Gap 12), Character select 5.10 (VERIFY — Gap 14), VS/result depth (PARTIAL — Gap 15), Item moves (MISSING — Gap 10), Announcer (PARTIAL — Gap 16), Frame data (HAVE — tables, PARTIAL in-fight overlay — Gap 21), Replay theater (PARTIAL — Gap 20), Online (HAVE — lobbies/tournaments, ADD rollback — E1)
- **T8:** Heat → Soul Urge (HAVE — soulurge.js, COMPLETE specifics — Gap 8), Tornado (MISSING — Gap 6), Recoverable health (VERIFY — Gap 7), Heat Dash/Smash (PARTIAL — Gap 8), Stages with multi-break walls/floors + explosive walls (PULL — stage hazards), Special Style (easy combo assist — EVALUATE: WH is phone-first, Special Style could help new players, but user law says Tekken-style inputs, not one-button — DO NOT implement one-button combos, but consider assist OPTION for accessibility? Owner decision needed)
- **WH-ORIGINAL (must NOT be replaced by Tekken pulls):** Nine-Soul Meter, Soul Surge, KESSHOU, Nine-Soul Climax/Release, Reihou, Trial's Seal, Soul Urge (name), Go Qombat, Heart and Mind Within, Five Lands, Tong-Nou, Trader, Trial, multiverse/realm system, creation suite (MUGEN-style but WH), V-System (Tekken-ified SFV, owner-approved). Tekken pulls go UNDERNEATH WH systems (foundation), never replace them (Foundation Law).

---

# SOURCES (all URLs verbatim from research)

## Tekken systems
- Tekken 7 gameplay (Tekkenpedia): https://eng.tekkenpedia.com/wiki/Tekken_7/
- Tekken 7 (Tekken Wiki): https://tekken.fandom.com/wiki/Tekken_7
- Tekken 7 glossary: https://gameplay.tips/guides/632-tekken-7.html
- Tekken 7 guide (NamuWiki): https://en.namu.wiki/w/%EC%B2%A0%EA%B6%8C%207/%EA%B0%80%EC%9D%B4%EB%93%9C
- Tekken 7 modes (Mic): https://www.mic.com/articles/178383/tekken-7-game-modes-all-the-different-ways-to-play-the-new-fighting-game
- Tekken 7 story/customization (Gamereactor): https://www.gamereactor.eu/tekken-7-story-mode-impressions/
- Tekken 7 review (WayTooManyGames): http://waytoomany.games/2017/06/01/new-game-review-tekken-7-ps4/
- Tekken 7 update 5.10 (Steam): https://store.steampowered.com/news/app/389730/view/3625991053636159598
- Tekken 8 (Wikipedia): https://en.wikipedia.org/wiki/Tekken_8
- Tekken 8 Heat (PC Gamer): https://www.pcgamer.com/heres-a-detailed-look-at-tekken-8s-new-battle-system/
- Tekken 8 Heat (Tekken Wiki): https://tekken.fandom.com/wiki/Heat?file=TEKKEN_8_%E2%80%93_New_Gameplay_Mechanics_Introduction
- Tekken 8 review (Polygon): https://www.polygon.com/reviews/24046939/tekken-8-review-heat-story-fighting-games

## Experimental projects
- GGPO (Wikipedia): https://en.m.wikipedia.org/wiki/GGPO#p-lang
- GGPO MIT license (Shacknews): https://www.shacknews.com/article/114405/ggpo-good-game-peace-out-sdk-is-now-free-under-mit-license
- GGPO netcode explainer: https://words.infil.net/w02-netcode-p5.html
- Castagne Engine: http://castagneengine.com/docs/
- MB-Lab guide: https://deepwiki.com/animate1978/MB-Lab/3-character-creation-guide
- MakeHuman 1.0 (CGW): https://www.cgw.com/Press-Center/News/2014/MakeHuman-Open-Source-Software-Released-in-Versi.aspx
- MPFB about: https://static.makehumancommunity.org/mpfb/about.html
- Meshy character creators: https://www.meshy.ai/blog/3d-character-creator
- Tripo open source (SIGGRAPH): https://blog.siggraph.org/2026/08/the-teapot-test-reimagined-from-showing-to-making-with-tripo-ai.html/
- Scenario Blender plugin: https://alphasignal.ai/news/scenario-opens-its-ai-blender-plugin-to-generate-3d-assets-inside-viewport
- Muapi 3D API: https://muapi.ai/ai-3d-model-api
- Node procgen (Savant): https://www.nathansavant.com/open-world-procgen
- Worldtable: https://maroon280.itch.io/worldtable/devlog/1719169/introducing-worldtable
- Seedwake: https://blog.darkwood.com/article/darkwaar33-seedwake-asynchronous-multiplayer-without-a-server-1
- Nerulith: https://forums.unrealengine.com/t/nerulith-multiplayer-endless-procedural-world-with-biomes-using-level-streaming/2484277
- Dungeonizer: https://assetstore.unity.com/packages/tools/level-design/dungeonizer-procedural-dungeon-generator-22162
- Narrative tools comparison: https://game-ace.com/blog/narrative-game-design/
- Ink/Yarn/Twine guide: https://generalistprogrammer.com/tutorials/game-narrative-design-complete-storytelling-guide-2025
- Adaptive music (dev.to): http://dev.to/aplusgamesstudio/video-game-music-how-it-is-composed-and-implemented-1969
- Wwise/FMOD stems: https://www.mozratai.com/blog/adaptive-music-fmod-wwise-stems.html
- FMOD/Wwise SFX: https://krotos.studio/blog/sound-effects-for-games
- AI game sound: https://aicompetence.org/ai-game-sound-design/
- Rapier ragdoll (Three.js): https://dev.to/mattvb91/realistic-ragdoll-physics-in-threejs-1pko
- Samurai ragdoll (GitHub): https://github.com/achrefelouafi/SamuraiThirdPersonTemplateThreeJS
- Cloth simulation (GitHub): https://github.com/shInNei/Cloth-Simulation
- three-mmd physics: https://deepwiki.com/moeru-ai/three-mmd/3.4-rendering-and-materials
- Euphoria (TV Tropes): https://tvtropes.org/pmwiki/pmwiki.php/Main/RagdollPhysics
- Euphoria weighted logic: https://ludonodestudios.medium.com/beyond-ragdolls-mastering-weighted-character-logic-and-euphoria-physics-23290536dc4a
- meshoptimizer/gltfpack: https://meshoptimizer.org/gltf/
- Needle Cloud optimization: https://cloud.needle.tools/articles/needle-cloud-optimization
- Three.js 100 tips: https://www.utsubo.com/blog/threejs-best-practices-100-tips
- Three.js GLB loading measurement: https://medium.com/@1228566953qq/three-js-glb-loading-cache-decode-and-the-first-gpu-frame-bead0f5691ab
- R3F scaling/performance: https://r3f.docs.pmnd.rs/advanced/scaling-performance
- Three.js low bandwidth: https://moldstud.com/articles/p-optimizing-threejs-for-low-bandwidth-environments
- Three.js render guide: https://copyprogramming.com/howto/javascript-threejs-render-how-work-code-example
- MUGEN Fighter Creator: https://mugenguild.com/forum/topics/fighter-creator-131679.80.html
- MEATKLAW HUD: https://astt0r.itch.io/meatklaw/devlog/1719520/prototype-072-new-hud
- Frame data guide: https://www.fightinggameguide.com/framedata.html
- Frame data explained: https://verynicegame.com/fighting/how-frame-data-works-in-fighting-games/
- Dustloop/SuperCombo: https://www.dustloop.com/w/Using_Frame_Data | https://wiki.supercombo.gg/w/Frame_Data

## WH repo evidence (all via GitHub API, main branch, 2026-10-24)
- game/js/fighter.js (122,855 bytes) — grep: rage=24, heat=1, powercrush=0, screw=0, wallbreak=0, floorbreak=0, chip=15, launch=11, juggle=6, bound=12, tag=10, sidestep=30, stance=56
- game/js/combat-core.js (5,769 bytes) — grep: powercrush=0, screw=0, tailspin=0, wall_splat=0, floor_break=0, balcony_break=0, hitbox_data=0
- game/js/rage.js (8,220 bytes), stagebreaks.js (20,203 bytes), music.js (10,675 bytes), online.js (43,141 bytes), tag-relay.js (5,517 bytes), v-system.js (7,301 bytes), finisher.js (10,189 bytes), soulurge.js (8,463 bytes), load-progress.js (3,547 bytes)
- game/assets/movesets/ — 157 files; pantera.json — 874 moves, t7=260, hit_level=850, on_block=834, on_hit=851, hitbox=0
- game/assets/anim/ — made/, oss/, t3/ (22 banks + reactions.json); NO t7/ dir
- game/netplay/ — README, bridge/, demo/, lobby/, mirror.mjs, signaling/, sim/, vendor/
- game/data/ — music-library.json, sound-bank.json, ranks.json, roster_map.json, soul-variants.json, t8_frame_tables.json, moveset-library/, movesets/, stances/, voices/
- game/js/ file list (86 files) — full list in Part 1

---

# ADDENDUM — NEW USER DIRECTIVES 2026-10-24 19:41 CDT (from main chat, recorded in MEMORY.md)

These arrived after the main gap analysis was written. They add gaps + music direction and are recorded here so they are not lost:

### A1. Cape Jones theme song: "Ghost Surf Rock" by Loyalty Freak Music
- Ghost Surf Rock = Cape Jones theme song. If Cape Jones gets an arena, Ghost Surf Rock is the MAIN track there, with interchanging tracks rotating around it.
- VIBE: surf rock + spooky + witchy + batty + Halloween (from collection "WITCHY BATTY SPOOKY HALLOWEEN IN SEPTEMBER !!") — spooky, surf, fun, ghostly, Halloween-ish. This vibe defines Cape Jones and should guide music picks for Cape Jones / Western Heart.
- Gap mapping: extends Gap 11 (Jukebox) + music lane — Cape Jones arena BGM pool = Ghost Surf Rock (main, always in rotation) + interchanging tracks (Nosferatu synth tracks, Tekken BGM, other Loyalty Freak tracks). Wire: music-library.json (Cape arena pool: Ghost Surf Rock flagged main) + music.js (rotation keeps main track weighted, not random-only).
- Source: Loyalty Freak (no-copyright music label, already used for Cape Jones show Ep 1 ghost track "A ghost Waltz", CC0).

### A2. REMOVE tap-for-audio — NEW UI GAP (Gap 23)
- **What Tekken + MDickey Wrestling Empire have:** Audio just works. No "tap to turn audio on" unlock screen. Tekken doesn't have tap-for-audio, Wrestling Empire doesn't have tap-for-audio.
- **What WH has:** A "tap to turn audio on" unlock thing when starting the game. User calls it dumb (2026-10-24 19:41 CDT).
- **Fix:** REMOVE the tap-for-audio unlock entirely. Put audio on/off in SETTINGS instead (toggle). Audio on by default, toggle in settings. Use Wrestling Empire as mobile reference for audio + mobile UX setup.
- **Wire in:** game startup flow (wh-boot.js / main.js audio unlock) + settings screen (audio toggle) + audio.js (default on, respect settings toggle).
- **Priority:** HIGH (user-called friction, phone-first law — "no dumb friction").

### A3. MOBILE + USER FRIENDLY (general directive, reinforces existing laws)
- Pretty much everything needs to be more mobile and user friendly. Phone-first, no dumb friction (like tap-for-audio), intuitive controls, clear settings.
- Gap mapping: reinforces Gap 18/19 (loading + performance), Gap 14/15/16 (select/VS/result polish), E16 (code-drawn HUD), E19 (Three.js performance patterns). No new system — a quality bar applied to ALL gaps above: every fix must be verified phone-first (portrait, touch taps, like the owner plays).

# METHOD NOTE
- Every gap above is grounded in a file read (GitHub API) or a grep count, NOT guessed. Where a system was NOT found in fighter.js/combat-core.js, the report says so explicitly and notes that it may exist in another file (e.g., stagebreaks.js for breaks, soulurge.js for Heat) — verification steps are given for each.
- Every experimental project above has a real source URL from web research (not invented). Licenses stated where found (GGPO MIT, Ink MIT, Yarn MIT, MakeHuman CC0, Scenario GPL-3.0, meshoptimizer MIT, Tripo open source). Where license was not found in research, it is NOT stated (do not assume).
- Canon alignment is based on CANON.md concepts as summarized in MEMORY.md (Tong-Nou, Nine Souls, Five Lands, Trial, Trader, multiverse/nested realities, colour is law, roads not portals, New-age MUGEN, creation suite = heart). Tekken names appear in this TECHNICAL research doc only, never in canon/in-universe writing, per user law.
- This doc is research + pull list, NOT implementation. Implementation follows via separate PRs per item (batch where possible, per user batch directive).
