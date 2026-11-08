# Western Heart — The Nine Souls: canon record

**Date:** 2026-11-08
**Repo:** `mhvnsnt/western-heart`, HEAD `3334ebf`
**Why this file exists:** Jay corrected us 2026-11-07 ~19:54 ("research the canon bro") — the hidden-9 work had counted RYUJI as a ninth soul and treated BYOU as a soul needing a body. Both were wrong. This file is the nine souls as the repo's own canon states them, with a source per claim. Nothing here comes from Tekken/WWE lore or from guessing.
**Names:** Pantera is male (he/him). Every other fighter is named by name only, no guessed pronouns.

## The nine souls — the canon list

The nine souls are the same nine in every canon source checked:

| Soul | Kanji | Nature | Vessel(s) | Soul body on disk? |
|------|-------|--------|-----------|-------------------|
| RIN | 凛 | Dignified, cold, self-possessed. The baseline. | Demonio | Yes — `rin-body.glb` (T7 Jin), rigged, PASS |
| BYOU | 病 | Sickness. Moves wrong. Unreadable. | Zui | **No — by canon design, not by omission (see below)** |
| TOU | 闘 | Battle itself. Exists only to fight. | Pantera | No own file; Paul models unwired in the Godot lab; soul body awaits T6/TTT2 extraction |
| SHA | 沙 | Sand. Flows, erodes, surrounds. | Saku Ra + Kinpo + Awa Pop (split three ways) | Yes — `sha-body.glb` (T7 Xiaoyu), rigged, PASS |
| KAI | 海 | The sea. Rhythmic, unstoppable. | King Tyrant + Star (the sea's two moods) | Yes — `kai-body.glb` (T7 Eddy), rigged, PASS |
| JIN | 刃 | The blade. Precise, ritual, terrifying. | Phantom | Yes — `jin-body.glb` (T7 Yoshimitsu), rigged, PASS |
| RETSU | 烈 | Violence. Pure destructive force. | Skull | Yes — `retsu-body.glb` (T7 Bryan), rigged, PASS |
| ZEN | 禅 | Stillness. Barely moves. Doesn't need to. | **Unvesseled** | Yes — `zen-body.glb` (T7 Julia) + 11 more ZEN files, rigged 2026-10-22 |
| GYOU | 行 | Motion itself. Cannot stop moving. | **Unvesseled** (a splinter trapped in CYBORG X) | No rigged file; 7 unrigged Tripo statics, archive-only; soul body awaits T6/TTT2 extraction |

**Canon sources for the list:** CANON.md §4 table ("Rin, Byou, Tou, Sha, Kai, Jin, Retsu, Zen, Gyou"); ROSTER.md §1–9 (one section per soul, same nine, same kanji, same natures); `game/js/heartmind.js:143-151` (`NINE` table — rin, byou, tou, sha, kai, jin_soul, retsu, zen, gyou); `game/js/movesets.js:32` (MOVESET_IDS soul list — same nine); DESIGN.md §3 ("Nine fighters. Each is one of Tong-Nou's lost souls"). JIN is the 9th soul — JIN the Blade Soul, **not** Jin Kazama (AGENTS.md owner law 2026-11-01: "there is a j i n character, Jin, he's one of the nine Soul Spirit characters, he's just not Jin Kazama"; Demonio is the fighter built on Jin Kazama's data).

**The seven vesseled + two unvesseled:** the seven vesseled souls are RIN, BYOU, TOU, SHA, KAI, JIN, RETSU (`game/js/select-screen.js` 2026-10-22 directive comment; `docs/souls/VESSELS-AND-STANDS-OWNER-2026-10-21.md` vessel table). ZEN and GYOU are unvesseled (CANON.md §4: "Two souls have not taken vessels. ZEN — the still soul — is said to have refused the trial... GYOU — motion itself — is said to be everywhere already, and therefore nowhere in particular").

## RYUJI is not a soul — the correction

**What RYUJI is:** Ryuji Yamazaki is an **inspiration** for CORNERSTONE, along with The Rock. Canon, CANON.md ~1299–1311 (owner 2026-10-19/21):

- Foundation: "Ryuji Yamazaki version… black shirt, blonde top hair. Version based on The Rock (Dwayne Johnson) mixed with Ryuji Yamazaki — obnoxious like Ryuji, sticks his tongue out, personality mixed with The Rock."
- "CORNERSTONE is the name the owner locked on 2026-10-21 for the Ryuji Yamazaki × The Rock hybrid who first entered the roster as RYUJI ROCK. **He is not one of the nine souls and carries no vessel** — he is a bonus fighter, a collision of two personas: Yamazaki's menace underneath, The Rock's early-Attitude-Era showmanship on top."
- "The pure-Yamazaki roster entry (`ryuji`, carrying the full KOF set) is untouched and stays in the repo." (CANON.md:1311; also `game/js/roster-full.js:317` — id `ryuji`, base 'Ryuji Yamazaki', moveset `ryuji-rock`, `model: null`; and :320 — id `ryuji-rock`, name CORNERSTONE, `model: 'ryuji-rock'`.)
- Also `RENAME-MAP.md:371`: "Ryuji Yamazaki (KOF / Fatal Fury) x The Rock (WWE, early Attitude Era) | `ryuji-rock` | CORNERSTONE | NAME LOCKED".

**Why RYUJI is hidden then:** the owner no-duplicate law (`game/js/select-screen.js` 2026-10-22 comment): entries that share another fighter's model are hidden until they get their own models. RYUJI shares CORNERSTONE's `ryuji-rock` moveset lineage. It is hidden as a duplicate, **not** under the soul rule. Canon asks for no model build and no unhide for it.

**What was wrong:** the spec (§7), Part D, and the first version of `HIDDEN-9-MODELS.md` all counted the 9 hidden roster entries as 9 souls and treated RYUJI as the ninth. The 9 hidden roster entries are 8 souls + RYUJI. JIN, the 9th soul, is pickable as Phantom and is not hidden at all.

## BYOU — not the red/fire guy, and not supposed to have a body

**Identity:** BYOU 病 — sickness. "A soul that twitches, stutters, moves wrong. Its illness is its weapon — opponents can't read a body that doesn't obey itself." (ROSTER.md §2.) Vessel: **Zui**, the drunken-master ex-monk (CANON.md §3 + §4 table; VESSELS doc: "BYOU | Zui (and Steve Fox, same vessel before the monastery)"). Zui is pickable with a body: `model: 'zui-attire1'`, Steve Fox base (`game/js/roster-full.js:104`).

**Not the red/fire guy:** BYOU's canon skin is "jaundiced yellows, infected greens" (ROSTER.md §2); the roster entry colors are olive green (suit `0x4a5a1a`). Sickness, yellow/green — not red, not fire.

**Not supposed to have a body of its own:** the soul-body rule (`docs/souls/VESSELS-AND-STANDS-OWNER-2026-10-21.md`, owner 2026-10-21): "A soul of the nine has no body of its own. In a fight it exists through its **vessel** (the host fighter's body fights) and shows itself as a **celestial stand** with the host." The soul-body map (`docs/souls/SOUL-BODY-REPLACEMENT.md`, owner order 2026-10-15) lists BYOU as the one soul **BLOCKED**, and its Resolution (2026-11-06) records the block resolved: the owner named Lei Wulong's WH fighter **Rave** (Kiko Tanaka / Ghost, locked 2026-10-19/21 — `game/js/roster-full.js:330`: "Lei wulong is not byou, he is Rave/Kiko tanaka ... rave already takes over leis character and slot and moves and personality"), and "Byou's moveset base is **Wang Jinrei** (Tekken 6) per the owner's 2026-11-06 ruling ('He can have wang if no one else does'); the Lei layer was removed from `game/assets/movesets/byou.json` and Wang's decoded T6 PSP kit wired in its place. Byou's vessel remains **Zui** (Steve body), unchanged." (Same ruling in ROSTER.md §2: "Lei Wulong is Rave's alone; Byou's moveset base is Wang Jinrei (Tekken 6)... This replaces the pre-correction Lei Wulong style mapping.")

**What BYOU is owed:** no model build. BYOU fights through vessel Zui + the soul-spirit stand (`game/js/soul-spirit.js`) per the 2026-10-21 owner rule. The work is the stand/vessel wiring, not a BYOU body. **Do NOT "give BYOU a model" — that contradicts canon.**

## GYOU — the fire guy, needs the rig job (confirmed)

**Identity:** GYOU 行 — motion itself. Canon title **Flame Lord (Flaming Angel)** (`roster/gyou/CANON.md`, owner directives verbatim): "Gyou is the spirit floating behind him stand style, but the spirit body is the fighter, the flame emperor mode is the transformation that begins oversoul, except gyou face does not take over his spirit bodies head like zen, he become the flames engulfing him, the armor, the cape, the flames, etc." And: "He is the flame Lord (Flaming Angel) and will have various transformation ls and a giant susanoo form with different levels and transformations too."

**Fire throughout:** transformations Flame Emperor, God of the Flame, Guardian of the Flame, The Flame Eternal (giant flaming Susanoo beast — flaming wings, Gyou's face visible, giant 5× hands, 7 fingers each). Tripo source project: `fiery_humanoid_3d_model` (`roster/gyou/spirit-body/MANIFEST.md`, SHA `a1bd1432…`, 26,875,868 B). Transformation files: level1 "fire elemental", flame-eternal "lava golem", godflame "lava demon", guardian "fire elemental".

**Honest note on "red":** the word "red" does not appear in GYOU's canon text as read. What canon states is fire/flame throughout — Flame Lord, becomes the flames, fiery humanoid, lava/fire transformations. That is the flame identity Jay named. (For contrast, TOU is the soul whose canon skin is "blood reds, scorched oranges" as the Fire-force soul — ROSTER.md §3 — and Pantera, TOU's vessel, wears red PANTERA lettering. Jay's "red guy" = GYOU the Flame Lord stands on GYOU's flame identity.)

**Status:** unvesseled soul; a splinter is trapped in CYBORG X (CANON.md §4: "GYOU cannot take a vessel — a vessel is a *somewhere*, and GYOU is everywhere. But a machine is a nowhere... In CYBORG X's chassis, the ubiquitous got caught. The soul as a whole remains unvesseled."). Soul body awaits T6/TTT2 extraction (no T7-style Hwoarang exists — SOUL-BODY-REPLACEMENT.md). The 7 Tripo GLBs on disk are unrigged archive-only sources; the rig job is the owed work (Blender + GameRig per `roster/gyou/spirit-body/SPEC.md`). Spirit-float behavior: floats behind the spirit body like Zen's, but "more aggressively and sporadically."

## The other souls — body status (from the soul-body map + file checks)

- **RIN** — soul body `rin-body.glb` (T7 Jin), rigged, PASS. Vessel Demonio. Hidden only by `model: null` + `SELECT_HIDDEN` — one-line config fix.
- **TOU** — soul body awaits T6/TTT2 extraction (no T7-style Paul — SOUL-BODY-REPLACEMENT.md; ROSTER.md §3: "PENDING better model"). Vessel Pantera HAS a model. Base Paul models exist unwired in the Godot lab (`lab/game/assets/t3_paul.glb`).
- **SHA** — soul body `sha-body.glb` (T7 Xiaoyu), rigged, PASS. Split three ways: Saku Ra (bloom), Kinpo (thorn), Awa Pop (bubble). One-line config fix.
- **KAI** — soul body `kai-body.glb` (T7 Eddy), rigged, PASS. Two moods: King Tyrant (tide) + Star (current). One-line config fix.
- **JIN** — soul body `jin-body.glb` (T7 Yoshimitsu), rigged, PASS. Vessel Phantom, pickable. Not hidden.
- **RETSU** — soul body `retsu-body.glb` (T7 Bryan), rigged, PASS. Vessel Skull. One-line config fix.
- **ZEN** — soul body `zen-body.glb` (T7 Julia) + 11 more ZEN files, rigged 2026-10-22. Unvesseled; fights in a spirit body with a stand behind it (owner 2026-10-21: unvesseled souls need "his own spirit body tripo model plus a stand version of himself behind it"). Only Jay's bank call is owed (Dural bank is private-build only). **Tension noted, not resolved:** VESSELS-AND-STANDS (2026-10-21) says "ZEN has no spirit-body model yet" — but that predates the 2026-10-22 ZEN rig; the 12 files now on disk include ZEN's spirit/tentacle/oversoul forms. Whether those satisfy the "spirit body" the owner meant is UNMEASURED here — Jay's call, not a guess.
- **ZEN base conflict (carried, unresolved):** CANON.md:1555 flags "Julia→NIGHTWOLF / soul ZEN (a three-way doc conflict... unresolved)"; `fighter.js:197-211` says ZEN is NEITHER Heihachi NOR Julia — base chain Eleven/Twelve → Dural. The roster's `base: 'Heihachi'` is stale against that decision.

## How the nine souls fight (canon rule)

From `docs/souls/VESSELS-AND-STANDS-OWNER-2026-10-21.md` (owner 2026-10-21): "the people like Byou and Zen and stuff like that they have a vessel ... when they have the vessel and they're attached, we need to select them and they're attached to the vessel, then it's going to be like a modified, like celestial version, like JoJo's Bizarre Adventure with a stand ... he doesn't have a body so he needs like a host person to exist and be like a stand too." Unvesseled souls (ZEN, GYOU) fight in their own spirit body (a Tripo model) with a large spectral avatar behind it — Susanoo-scale, stand behaviour, Shaman King Over Soul flavour.

The 2026-10-22 directive (`game/js/select-screen.js` comment): the seven vesseled souls come off the grid as standalone cards and "return LATER as unlockable boss-type characters with vessels/bodies once story modes progress — the unlock path is future design, not this change. Their presence on a fighter is the soul-spirit toggle (`js/soul-spirit.js`), not a select card."

## What is UNMEASURED (canon does not say)

- Whether ZEN's 12 on-disk files satisfy the "spirit body" the owner meant in the 2026-10-21 vessels/stands decision (see ZEN tension above).
- What, if anything, a BYOU soul-body would be after the Lei route closed — canon names no replacement body; BYOU fights through Zui. Any body assignment would need Jay's call.
- The exact unlock path for the seven vesseled souls' return as boss-type characters — "future design, not this change" (select-screen.js comment).
- The Julia/Nightwolf/ZEN three-way doc conflict (CANON.md:1555) — flagged unresolved in canon itself.

## Sources read (repo HEAD `3334ebf`)

CANON.md (§2 The Seven, §3 The Four, §4 The Nine Souls incl. soul table + soul-bodies + ZEN/GYOU + GYOU splinter + the twelve, §6 Cyborg X, ~1299–1311 Cornerstone, :1555–1556 T3 conversion record); DESIGN.md §3; ROSTER.md §1–9 + design notes; `docs/souls/SOUL-BODY-REPLACEMENT.md` (per-soul map + 2026-11-06 Resolution, via `git show HEAD:` — sparse clone); `docs/souls/VESSELS-AND-STANDS-OWNER-2026-10-21.md` (vessel table + stand rule, via `git show HEAD:`); `roster/gyou/CANON.md` + `roster/gyou/spirit-body/SPEC.md` + `roster/gyou/spirit-body/MANIFEST.md` (via `git show HEAD:`); `game/js/roster-full.js` (:13–25 soul entries, :104 Zui, :317 ryuji, :320 ryuji-rock, :330–337 RAVE comment); `game/js/select-screen.js` 2026-10-22 directive comment + SELECT_HIDDEN (:460–480); `game/js/heartmind.js:143–151` (NINE table); `game/js/movesets.js:32` (soul id list); `RENAME-MAP.md:371–374` (Cornerstone name lock); `HIDDEN-9-MODELS.md` (file checks this correction builds on).
