# WESTERN HEART — CANON-MOVESET CHARACTER INVENTORY

**Lane 2B — Kevin + canon-movesets job. Research + inventory only: no moveset was built in this lane.**
**Repo:** mhvnsnt/western-heart (PUBLIC). **Main tip read:** `9c3461db41ff` (2026-11-21T22:47:15Z, "Merge PR #1819 — NO-TEMP-STORAGE law").
**Date:** 2026-11-21. **Workdir:** `~/workspace/_kevin-canon-moveset-20261121/lane-2b-canon-set/`.

## Owner order (2026-11-21 ~19:59 EST, verbatim substance)

> Kevin gets his full canon moveset wired up from decomps/recomps/already-extracted/decrypted/cracked sources — "and for any other character that has a complex or complicated moveset like he does — that's what I've been calling the canon move sets, which are different than the ones that are fully based off of full Tekken character, they have a few different modifications."

## The answer in one page

**THE CANON-MOVESET SET — 15 fighters** (Tier 1, §4; build order in §8):

| # | Fighter | Base the kit is built on | Why it is a canon moveset, not a straight port |
|---|---------|--------------------------|------------------------------------------------|
| 1 | **KEVIN** | Baek Doo San (taekwondo) | Named base's own bank does not exist; plays Bryan-bank rows today; 2 canon sigs unanimated |
| 2 | **ZEN** | Eleven/Twelve → Dural (VF5) + own canon | Cross-game composite; X.COPY super; Tentacle/Oversoul/stand; UNMAPPED in public builds |
| 3 | **GYOU** | Paul Phoenix + flame | Paul base + 4 flame transformations, 12 flame moves; Paul permanence open |
| 4 | **DEMONIO** | Jin + Devil Jin | 3-form transform system (demon / winged Devil / human); Devil-slot completeness disputed |
| 5 | **SAKU RA** | Ling Xiaoyu + T7 motbin | 3 signatures + T7 xiamot wiring (unjoined); 13 conflicting T3 row mappings |
| 6 | **DXMMII** | Mokujin (mimicry) | No fixed kit by design; mimic mechanic missing; four-arm stance system |
| 7 | **KUTZ** | Goh Hinogami (VF5) | No VF5 Goh source anywhere; plays King (98%); not rostered yet |
| 8 | **REALIZZT** | Brad Burns (VF5) | No VF5 Brad source anywhere; plays Jin; not rostered yet |
| 9 | **BURGER** | Bob + Kusaregedo (SamSho) | 4-form transform system; 5+ further forms have no kits at all |
| 10 | **DEATHFANG** | Iori Yagami (KOF) + werewolf | Cross-game base on Heihachi proxy + werewolf form with 13 beast mix-ins |
| 11 | **BYOU** | Wang Jinrei (T6 PSP) | Owner-ordered base correction; decoded Wang layer over Jin-bank playable rows |
| 12 | **CHATUR** | True Ogre (T3) + four arms | Ogre bank + 7 canon moves + Kuma second-pair stance layer; GYOU-touched |
| 13 | **MEGAMI** | Jun Kazama (TTT2) + sealed door | TTT2 kit (no teardown bank) + 4 MADE canon moves, clips not authored |
| 14 | **MENAJERII** | Roger Jr. (TTT2) + beasts | TTT2 kit (no teardown bank) + 4 canon moves incl. Heron stance system |
| 15 | **PHANTOM** (soul JIN) | Yoshimitsu | Kit content is a straight port; the identity is canon-complex: `jin_soul.json` vs `phantom.json` duplication, neither file clearly canonical |

**BORDERLINE — 10 fighters** (§5, owner/coordinator decides promotion): Pond, Tobi, Ryusan, Doc Frank, Kronos, Koreshi, Ryuji-Rock/Cornerstone, Vain Abel, Kinpo + Awa Pop (SHA sisters), plus two ruled OUT with reasons (Cyborg X, Charger, Silvertongue/Lili).

**STRAIGHT TEKKEN PORTS — everyone else** (§6 bulk table): one Tekken character's kit on that character's own bank (or same-character T7/TTT2 kit), no form switch, no composite, no owner-ordered rebuild.

**NOT FIGHTERS** (§7): Baek and Lili (custom-character material only — Baek folds into Kevin, Lili into Silvertongue); `sha` (retired card, file kept); `jin_soul` (staged kit, no roster entry); bare `dxmmii` (staged, never loads); `sunra` (file only).

## The test — how "canon moveset" was decided (read this before disputing a call)

A fighter counts as **CANON-MOVESET** iff the kit it is built to play differs structurally from a single-character Tekken kit in at least one of these ways:

- **(a) Wrong-bank proxy with an owner-ordered rebuild** — the named base's own bank is missing and the owner ordered the true kit (Kevin, Kutz, Realizzt).
- **(b) Cross-game composite base** — the kit spans games/characters by design (Zen, Gyou, Deathfang, Kronos, Koreshi, Ryuji-Rock).
- **(c) Form/transformation system with a distinct moveset per form** (Demonio, Burger, Deathfang-werewolf, Zen's stages).
- **(d) Mimicry / no fixed kit** (DXMMII).
- **(e) Owner-ordered base correction or canon layer with a real second source** (Byou's decoded T6 Wang layer; Chatur's four-arm layer; Megami/Menajerii's TTT2 + MADE canon systems; Saku Ra's T7 motbin wiring).

**What does NOT count (the repo-wide standard pattern):** the 2026-10-24 canon wiring — 190 canon entries across 66 files (`docs/canon-movelist-wiring-2026-10-24.md`), additive only, `wh:` refs are placeholders for animations not yet authored, game-loader wiring of `canon_moves` is explicitly follow-up work. A fighter with only the standard 2–3 signature moves + a T8 frame-data fold-in is a straight port with signatures, not a canon moveset. Every call below cites the file + field it rests on; where the docs do not settle it, the entry says so instead of guessing.

## How a fighter plays today (loader mechanics — governs every "plays today" line below)

- **A fighter plays its OWN file.** `game/js/fighter.js:899`: `this._movesetId = charData.id` ("may be overridden by transform"). `game/js/main.js:1516`: `ensureMovesets(msIds)` with `msIds = [player.id, enemy.id]` plus form-target movesets. The roster `moveset:` field in `game/js/roster-full.js` is legacy/display metadata for the fight path — it does **not** select the file.
- **If the id has no file, the loader returns null and the fighter falls back.** `game/js/movesets.js` `_fetchOne`: if the index has no entry for the id, it returns null without fetching. Bank ids (`king`, `jin`, `bryan`, `heihachi`, `xiaoyu`, `yoshimitsu`, `gunjack`) have **no** `game/assets/movesets/<id>.json` files.
- **Legacy aggregates still exist.** `game/js/fighter.js:355-379` `loadRealMovesets()` loads the 7 legacy T3 aggregate files (`king_moves.json`, `jin_moves.json` as `demonio`, `bryan`, `heihachi`, `xiaoyu`, `yoshimitsu`, `gunjack`) and maps every id in `MOVESET_MAP` (fighter.js:86-140) to one of them in `window.WH_MOVESETS` — the fallback when no per-fighter file resolves.
- **Animation bank is separate from frame data.** `bankIdFor()` (`fighter.js:160-300`) resolves the motion bank from the per-fighter file's `anim_bank`/`t3_source` first, `MOVESET_MAP` second, with the `FIGHTER_BANK` override table. A null binding means embedded locomotion + procedural combat — never another character's clips.
- **T3 teardown banks on main: 21 files** (`teardown/tekken3/movesets/moveset_*.json`): anna, bosconovitch, bryan, common, eddy, forestlaw, gon, gunjack, heihachi, hwoarang, jin, julia, king, kuma, law, lei, nina, ogre, paul, xiaoyu, yoshimitsu. **No Baek bank. No Mokujin bank** (type 15, BNS record 295 size 0 — `CANON.md` appendix). `CANON.md` appendix: all 20 character motion banks on the owner's disc image (types 0–20) + common bank extracted from TEKKEN3.BNS and SHA-256-verified.
- **Roster size:** 85 `{ id:` entries in `game/js/roster-full.js` (its header says "48 selectable fighters" — stale). `game/assets/movesets/index.json` lists 127 fighters + 26 Brutal Fist entries at top level. **The index is STALE vs the files** (see §10.1) — file headers govern every count below.

## Sources read for this inventory (all via `gh api`, main branch)

`ROSTER.md` (174 lines), `CANON.md` (1,666 lines), `game/js/roster-full.js` (504 lines), `game/js/movesets.js` (1,593 lines), `game/js/fighter.js` (relevant ranges), `game/js/main.js` (fight-load range), `game/assets/movesets/index.json` (127 fighters + 26 BF), `game/data/moveset-library/claimed-map.json`, `game/data/moveset-library/banks/vf5.json`, PR #1806 (MERGED — Zen/Gyou/Saku Ra/Jin_soul canon fix) and PR #1805 (MERGED — Demonio Devil attachment fixes) bodies, `docs/decisions/2026-10-24-zen-base-decision.md`, `docs/canon-movelist-wiring-2026-10-24.md`, `docs/ROSTER-CANON-GAPS-2026-10-23.md`, `docs/research/VF5-TEARDOWN-HUNT-20261120.md`, `docs/ZEN-DURAL-REBASE-2026-10-28.md`, `docs/anim/DXMMII-ANIM-GAP-20261023.md`, `docs/anim/VF5-DURAL-ANIM-GAP-20261023.md`, per-fighter `roster/*/CANON.md` (zen, gyou, demonio, saku-ra, dxmmii, baek, jin, phantom, cyborg-x, burger, deathfang, kinpo, rave), and 60+ moveset file headers read directly from the JSON (`tekken_base`, `t3_source`, `t3_bank`, `proxy_note`, `canon_moves`, `canon_note`, `merge_sources`, `flame_attacks`, `mimic`, `wh_true_moveset`, `wang_kit`/`wang_rebuild`, `rebase`, `dural_rebase`, `t7_motbin`, `t7_source`, `ttt2_source`).

---

# §4 — THE CANON-MOVESET SET (Tier 1, 15 fighters)

Each entry follows the same shape: **identity → what the full canon moveset IS → sources → in-repo vs missing → plays today → build-lane slot**.

---

## 1. KEVIN — The Master Soul (build first — the owner's named job)

- **Identity.** Not one of the nine. The teacher who came on purpose. `CANON.md` §7 "KEVIN — The Master Soul"; `roster/baek/CANON.md` (OBSOLETE notice: "Baek does not exist as a character… The fighter IS Kevin", owner 2026-10-20; "Baek's model is Kevin's A2 attire; the Master's White reskin is PARKED"). Backstory: Baek Doo San, taekwondo master who taught Hwoarang; lost at sea, taken, broken, rebuilt; followed a student into the trial. Philosophy: "The kick is the question. Discipline is the answer." Element Fire.
- **What the full canon moveset IS.** Baek Doo San's complete taekwondo kit — flawless textbook kicks as weapons — **plus Kevin's canon modifications**: the teacher's discipline layer. The only canon moves recorded so far are the two signatures in the file (below); the full modification list is **not yet documented anywhere in the repo** — the build lane's first job is to define it from the owner's direction (the "few different modifications" in the 2026-11-21 order), grounded in Baek's real kit, not invented.
- **Sources to pull from.** (a) A real Baek teardown bank — **none exists on main**: no `teardown/tekken3/movesets/moveset_baek.json`, no `moveset_baek` anywhere in the 60,353-path tree, Baek is not among the appendix's 20 extracted T3 banks. The build lane must source it: re-teardown from a fuller Tekken 3 source, or Baek's Tekken 6 / Tag Tournament 2 kit (same character, later games — source to be verified by the lane, not asserted here). (b) Related in-repo material: T3 Hwoarang bank (`teardown/tekken3/movesets/moveset_hwoarang.json`, T7 `t7-hwoarang-lp-rp-lk-rk.json`) — the student's kit, reference only, never the master's substitute. (c) Community movelists (same federation-conversion method as the existing `vf-*` kits) as fallback.
- **In-repo vs missing.** IN REPO: select entry id `baek-master-white`, name KEVIN (`game/js/roster-full.js`, moveset field `'bryan'`, model `'baek'`); `game/assets/movesets/baek-master-white.json` — 291 moves, `tekken_base: "Baek"`, `t3_source: "bryan"`, `t3_bank: "moveset_bryan.json"` (365 rows, 82 attack rows), variant 8; `merge_sources`: donors `[baek]`, 134 → 138 moves; 2 canon sigs — "Eleventh Lecture" (`1+4`, `wh:baek-master-white:sig:eleventh-lecture`, community base `game/assets/anim/oss/community/144_20.fbx`, status `pending-gpu-retarget`) and "Master's White" (`1+2`, `wh:baek-master-white:sig:masters-white`, base `144_05.fbx`, `pending-gpu-retarget`); `game/assets/movesets/baek.json` — 111 moves, same Bryan bank, 2 different sigs ("Homework" `1+4`, "Kick Is the Question" `1+2`). MISSING: `kevin.json` (no such file); any Baek bank; any Baek animation clip; the canon-modification list itself. NOTE: the name "Master's White" is both the PARKED reskin (owner 2026-10-20) and a canon sig name in the file — the build lane should confirm with the owner whether the sig name stands.
- **Plays today.** `baek-master-white.json` (own file, per `fighter.js:899`). Its playable rows are **Bryan's bank** — Kevin currently fights as a Bryan proxy with a Baek label + 2 unanimated sigs.
- **Build-lane slot: 3A (first).** 1) Source the real Baek kit (decomp/recomp/extracted/cracked, per the owner order). 2) Rebuild `baek-master-white.json` on the true Baek bank (P2 rebuild). 3) Define + wire the canon modifications. 4) Animate the 2 sigs (GPU retarget of the community bases). OWNER CALL: should the file become `kevin.json` (new id + roster/loader change) or stay `baek-master-white.json`? Do not rename unilaterally.

---

## 2. ZEN — The Still Soul (longest lead — start in parallel, do not gate Kevin on it)

- **Identity.** Unvesseled; refused the trial: "Stillness does not compete." `ROSTER.md` §8; `CANON.md` §4 "On ZEN and GYOU"; `roster/zen/CANON.md` (owner canon 2026-10-21: "a fucking yellow lemon octopus Spirit demon"; four owner Tripo models, release `zen-tripo-pulls-20261021`: spirit body 8c46e379, spirit 803f4cf1, Oversoul 2bbc8e88, Tentacle mode 9460095d). Default body is the T7 Julia model (`zen-body.glb`) — a BODY, not a vessel, not the fighter's identity. Pronoun unsettled ("she" owner 2026-11-20 vs "his" 2026-10-24 decision doc) — owner call, PR #1806 open Q1.
- **What the full canon moveset IS.** Base chain (owner decision 2026-10-24, `docs/decisions/2026-10-24-zen-base-decision.md`, verbatim): "Zen's base is neither of those [Heihachi/Julia]. Zen is like 11 and 12 but not just a copycat he has his own moves…" → **Eleven/Twelve (SF, 2D shapeshifting mimicry) → Dural (VF5, 3D chrome humanoid, "the closest thing to 10 or 11 in a 3D game") → Zen's OWN canon moves on top**, plus **X.COPY as ONE super, NOT his identity**, plus **Tentacle Mode, Oversoul, transformation, spirit-form stand**. Dural's stance is Zen's stance (permanent layer, owner 2026-10-22); Twelve's dancing idle stance is added ON TOP once converted 2D→3D. The 25 true moves (`wh_true_moveset` in `zen.json`): Twelve moves 10 (N.D.L., A.X.E., A.X.E. Air, D.R.A., H.U.G., F.L.G., T.R.W., B.M.K., Kokkuu, Kabe Haritsuki); non-copy supers 2 (X.N.D.L., X.F.L.A.T.); X.COPY 1 (input `d,d/f,f,d,d/f,f+1+2`, copies opponent briefly, does NOT grant EX/super moves); canon sigs 2 (Does Not Compete `b+1+2`, Refused Seat `1+2`); Tentacle Mode 3 (pastel ink blast, razor beam, pastel wave — all NEEDS-INPUT); Oversoul 1 (NEEDS-INPUT — no named Oversoul attack exists in docs, none invented); transformations 4 (TENTACLE MANIFESTATION up, OVERSOUL up, WITHDRAW down, OVERSOUL RELEASE down — TRANSFORM touch + full nine-soul meter); spirit-form stand 2 (NEEDS-INPUT). **25/25 UNMAPPED animation** — every entry has `anim_ref: null` on purpose.
- **Sources to pull from.** (a) VF5 Dural motion — **missing**: VF5 motion format RE required; Dural stance/idle/strikes/blocks/hits/KO/locomotion converted to `game/assets/anim/vf5/dural/` (`skeleton.json` + `rows.pack.json`); see `docs/anim/VF5-DURAL-ANIM-GAP-20261023.md` and `docs/research/VF5-TEARDOWN-HUNT-20261120.md` ("NO complete working VF5 teardown exists anywhere found"). The Dural rows file is cited in-repo as private only: `private: assets/private/anim/vf5/dural/rows.pack.json (mhvnsnt/game-reverse-engineering virtua-fighter-5/dural-motion)` — **not on main** (no `game/assets/anim/vf5/` in the tree). (b) SF3:3S Twelve 2D→3D conversion (sprites → 3D; its own RE lane) — SuperCombo wiki Twelve/Archive as the move reference. (c) SFV Eleven — in the SFV pull, still blocked on downloads (`teardown/street-fighter-5/CAST-STATUS.md`); Eleven has NO own moveset (morphs pre-match) — concept/lineage only. (d) MADE animations for all 25 true moves (none exist).
- **In-repo vs missing.** IN REPO: `game/assets/movesets/zen.json` — 644 moves (`dural_rebase` 2026-10-28: strike 285, signature 4, throw 37, special 194, string 124; `replaced_base` Heihachi; the interim `moves` map is Heihachi-derived and **never mixed** with `wh_true_moveset`); `X.COPY` playable entry `d,d/f,f,d,d/f,f+1+2` (`canon_id: xcopy`); forms chain in `roster-full.js` (zen → zen-tentacle → zen-oversoul, powerMult 1.15/1.25, moveset stays `'zen'` in every stage — the tentacle pastel-blast specials are a design requirement, "not a moveset key that exists yet"). MISSING: everything in "Sources" above; 6 NEEDS-INPUT (tentacle 3 + oversoul 1 + spirit-form 2); NEEDS-SPEC bindings (SF P/K/MK → Tekken buttons; super meter mapping).
- **Plays today.** `zen.json` (own file). Animation bank: **UNMAPPED (null)** in public builds (`fighter.js` `FIGHTER_BANK zen: null`, owner decision 2026-10-24) — embedded locomotion + procedural combat, never another character's clips. Private builds bind `'dural'` only when `T3_BANKS.dural` exists. Zen is in `SELECT_HIDDEN` while the comment above that set says Zen stays selectable — contradiction reported in PR #1806 (open Q2), not fixed silently.
- **Build-lane slot: 3B (start in parallel with 3A — longest lead time).** Lanes: (i) VF5 motion RE + Dural motion set; (ii) Twelve 2D→3D conversion; (iii) Eleven from SFV pull; (iv) MADE anims for the 25 true moves; (v) resolve the 6 NEEDS-INPUT + NEEDS-SPEC with the owner/spec. Do NOT claim Zen playable as his true kit until (i)/(ii)/(iv) land — the decision doc says so explicitly.

---

## 3. GYOU — The Moving Soul

- **Identity.** Unvesseled as a whole; a splinter is trapped in CYBORG X ("a machine is a nowhere"). `ROSTER.md` §9; `CANON.md` §4 "On the GYOU splinter"; `roster/gyou/CANON.md` (title: Flame Lord / Flaming Angel; spirit floats behind, stand-style, "moves around more aggressively and sporadically" than Zen's; Gyou becomes the flames engulfing the spirit body — armor, cape, flames — never taking the head like Zen). **Gyou is NOT Hwoarang** (owner 2026-11-10; `fighter.js:211`). Hwoarang's holder is Tobi.
- **What the full canon moveset IS.** **Paul Phoenix's power karate/judo + fire attacks** — the spirit-body variant. Owner-sanctioned 2026-10-23 ("he can have Paul Phoenix moves mixed with like flame attacks") and 2026-11-10 ("Gyou was probably Paul Phoenix and fire attacks"). The flame layer in `gyou.json` (`flame_attacks`, user-requested 2026-10-23): **4 transformations** — Flame Emperor (level 1, entry flame form), God of the Flame (ascended offense), Guardian of the Flame (defensive, tanky, knight-like face shield/helm/face plate, 0.5× bigger than God of the Flame, switchable with it), The Flame Eternal (Susanoo-type GIANT form — Gyou's face becomes visible on the oversoul for the first time, giant 5× hands with 7 fingers each, flaming wings); **12 flame moves** (Flaming Death Fist qcf+2, Burning Fist qcb+1+2, Emperor's Breath qcf+1+2, Godfire Eruption qcf+3+4, Wrath of the God f,f+1+2, Heavenfall Dive u+3+4, Flame Guard b+1+4, Ashen Counter d+1+2, Guardian's Wall b,b+1+2, Susanoo Slam d+1+4, Eternal Inferno b+3+4, World-Ash Step f,f+3+4) + `infused_strikes` (bank-derived Paul moves that gain fire VFX while a flame form is active — hits/inputs/frame data unchanged, visual fire layer only). Plus 2 canon sigs: Cannot Stop (`1+2`), Everywhere Already (`d+1`).
- **Sources to pull from.** (a) T3 Paul bank (`teardown/tekken3/movesets/moveset_paul.json`; `game/assets/movesets/t7/t7-paul-lp-rp-lk-rk.json` for the T7 layer). (b) The flame layer is owner-stated canon, not pulled data — its animation/VFX source is the build lane's work (fire VFX over Paul rows; giant-form models for The Flame Eternal). **NOTE:** the flame transformations' `canon_status` in the file is "user-stated 2026-10-23; NOT yet in CANON.md — parent to file them in docs/owner-directives.md and CANON.md" — still unfixed at inventory time.
- **In-repo vs missing.** IN REPO: `game/assets/movesets/gyou.json` — 617 moves, 334 slots, `tekken_base: "Paul Phoenix"`, `t3_source: "paul"`; `rebase` 2026-11-10 from `gyou-spirit-body.json` (kept 46, dropped 326 t7:hwoarang + 209 t8:hwoarang + 188 t3:hwoarang + 145 jin; old file archived at `docs/archive/movesets/gyou-pre-paul-rebase-2026-11-10.json`); `gyou-spirit-body.json` — 567 moves (pre-rebase base file, kept). MISSING: flame-form animation/VFX + giant-form models; CANON.md filing for the flame forms.
- **Plays today.** `gyou.json` (own file). Bank: `'paul'` (`FIGHTER_BANK gyou: 'paul'`). Roster entry: `gyou` → moveset `'gyou'`, model `gyou-attire1`.
- **Build-lane slot: 3C.** 1) Verify the Paul base plays clean post-rebase. 2) Build the flame layer (4 forms + 12 moves + infused VFX). 3) File the flame forms in CANON.md. OWNER CALL (open, PR #1806 Q3): Gyou's Paul holding is "probably Paul" / "whatever" — lock it as permanent or treat as stepping stone? Tou already holds Paul in canon, so Gyou is a SECOND Paul holder only by the owner's explicit words.

---

## 4. DEMONIO — The Demon Soul (vessel of RIN)

- **Identity.** Vessel of RIN (the protagonist soul). "Named demon, fights like a saint." `CANON.md` §2 "DEMONIO — The Demon Soul"; `roster/demonio/CANON.md` (three forms; "never called Jin in-game"; Steve Fox-bodied Demonio was a wrong-canon stand-in, owner ruling 2026-10-15 — the Steve body belongs to Zui). Element Earth. NOTE: `CANON.md` still carries a §7 "JIN KAZAMA — The Bloodline Soul" section that contradicts Law 2 ("There is NO Jin Kazama in our game at all") — flagged in PR #1806, owner call open (retire the section or amend Law 2).
- **What the full canon moveset IS.** **Three forms, one fighter, transform both directions (Roshi-style, TRANSFORM touch + full nine-soul meter):** (1) **Unwinged demon** — base form (Attire 1, Tripo unwinged demon), normal Demonio moveset: Mishima-style karate, Jin Kazama base, 3 canon sigs (Apology Burned Away `qcf+1`, RIN's Baseline `1+2`, The Unbowed `1+4`); T8 Jin frame data (wavu.wiki, CC0) folded in. (2) **Winged devil** — transformation UP: winged, demon bat hands bursting from palms/wrists, **Devil Jin kit** (T8 Jin kit; Devil-Jin flavored moves — ZEN stance, Hellfire/Black Wing set, Heat Burst — flagged `devil_flavor`; specials include DEVIL FLIGHT takeoff, INFERNO BEAM devil laser, HELLFIRE SWEEP). Transformation sequence (owner canon): purple haze → chest/arm markings → wings BURST → bat hands BURST → muscle expansion → shockwave. (3) **Human** — rare transformation DOWN: a human with a demon face on his chest/torso possessing him (the Tripo human model the owner uploaded — NOT the old Tekken 3 Jin); also selectable as a starting form.
- **Sources to pull from.** (a) T7 Devil Jin: `game/assets/movesets/t7-devil-jin.json` — 140 moves, FILL 2 (2026-11-06); frame table `game/data/t7-frame-data/t7-devil-jin-lp-rp-lk-rk.json`; motbin GRE `teardown/tekken7-steam/tkdata/mothead/bin/dvjmot.bin` + `json/dvjmot.json`; mvl `dvj.mvl`; banks GRE release `t7-fighter-banks-v1` (`dvj_clips.bin`, `dvj_bank0_clips.bin`). (b) T8 Devil Jin / Jin frame data (wavu.wiki, CC0). (c) T3 Jin bank (`teardown/tekken3/movesets/moveset_jin.json`). (d) Owner Tripo models (unwinged demon A1, winged devil, human).
- **In-repo vs missing.** IN REPO: `game/assets/movesets/demonio.json` — 684 moves (file count; the index says 764 — stale); `demonio-winged.json` — 1,063 moves, 414 slots, `merge_sources` T8 devil_jin + T7 deviljin + T3 jin + donor demonio; `demonio-human.json` — 683 moves; `demonio-bloodline-ember.json` — 686 moves, 2 sigs (Cliff's Echo `1+4`, Ember Bloodline `1+2`); forms chain in `roster-full.js` (demonio/demonio-a1 up→winged DEVIL ASCENSION 1.5× power, moveset `demonio-winged`; down→human DEPOWER, moveset `demonio`); PR #1805 MERGED (20 Devil slots 394–414 wired; attires.js BASE Steve-body entry removed; winged moveset name fixed). **DISPUTED — see §10.2:** PR #1805's proof claims "slot winner is a Devil record 80/80"; the current alignment synthesis (2026-11-21 night) states the amended fix "keeps all 80 Devil moves in the Devil form, but only 60 of 80 inputs actually play a Devil move and 20 inputs have no move wired yet, and the 18 displaced-key Tekken 7 Devil records … are still open." My own count from the pulled file (method: string-match 'devil' in the resolved move record — crude, NOT a Devil-record verification): 414 slots, 240 resolve to devil-tagged moves, 174 to non-devil moves, 0 unresolved. **Neither claim is verified by this lane.**
- **Plays today.** `demonio.json` base; `demonio-winged.json` on transform up; `demonio-human.json` on transform down (roster forms; `fighter.js:1233-1235` switches `_movesetId` on transform).
- **Build-lane slot: 3D.** 1) Recount the Devil slots from `demonio-winged.json` + `t7-devil-jin.json` and settle 80/80 vs 60/80 + 20 unwired. 2) Resolve the 18 displaced-key T7 Devil records. 3) Wire the human form's kit. OWNER CALLS: does the human form play its own moves or keep the base kit? Is Bloodline Ember an outfit or a fourth form? (both per the 2026-11-21 synthesis).

---

## 5. SAKU RA — The Idol Soul (the bloom; ONE fighter)

- **Identity.** Vessel of SHA (sand, split three ways: Saku Ra the bloom, Kinpo the thorn, Awa Pop the bubble). `ROSTER.md` §4 + SAKU RA section; `CANON.md` §2 + §4 "On SHA's three-way split"; `roster/saku-ra/CANON.md` (K-pop idol Powerpuff Girl direction, CN gigaleak PPG construction; "You can't hit a song"). Owner order 2026-11-20 ~19:30: **Saku Ra is ONE fighter**; the `sha` roster card retired; `sakura.json` is her file (PR #1806).
- **What the full canon moveset IS.** Ling Xiaoyu's flowing Baguazhang (circular, evasive, playful) **plus** her three signatures — Bloom Opening (`1+2`), Called By Name (`1+4`), You Can't Hit a Song (`d+1`) — **plus the T7 xiamot wiring**: the T7 Xiaoyu motion-bin data attached to her file (see Sources). T8 Xiaoyu frame data folded in.
- **Sources to pull from.** (a) T3 Xiaoyu bank (`teardown/tekken3/movesets/moveset_xiaoyu.json`). (b) T7 Xiaoyu motbin: `teardown/tekken7-steam/tkdata/mothead/bin/xiamot.bin` (blob sha `306a2d9685a38823c177210b84f50a3c1cf583be`) + `json/xiamot.json`, character `[Lin_Xiaoyu]` — wired 2026-10-24 as `t7_motbin` in `sakura.json` (counts: reactions 317, requirements 3019, hit_conditions 7, …). **Additive only: "motbin internal moves are NOT joined to playable input keys by name similarity… A future input-key join must be walk-verified from the cancel tables."** That join is the build lane's core job. (c) T8 Xiaoyu frame data (already folded in per `canon_note`).
- **In-repo vs missing.** IN REPO: `game/assets/movesets/sakura.json` — 764 moves, `tekken_base: "Xiaoyu"`, `t3_source: "xiaoyu"`, 3 canon sigs (above, `wh:` placeholder refs, community bases `88_06.fbx` / `144_13.fbx`, `pending-gpu-retarget`); `sha.json` — 785 moves, KEPT until the single-fighter load is verified. MISSING: the xiamot input-key join (motbin → playable inputs); the 3 sig animations; resolution of the **13 conflicting T3 row mappings for 1/2/3/4/1+3/2+4** (PR #1806 open Q4).
- **Plays today.** `sakura.json` (own file). Roster entry: `sakura` → moveset `'xiaoyu'` (legacy field), model `saku-ra`.
- **Build-lane slot: 3G.** 1) Walk-verify the xiamot join from the cancel tables. 2) Resolve the 13-way mapping conflict (owner/spec decision — do not guess). 3) Animate the 3 sigs.

---

## 6. DXMMII — The Rebuilt Soul (Patchwork DJ)

- **Identity.** Not one of the nine. The remix / the mimic soul. Name locked 2026-10-15; pronoun it/its until the owner decides otherwise (owner 2026-10-18). `CANON.md` §7; `roster/dxmmii/CANON.md` (Mokujin was a wooden dummy that learned by copying; DXMMII kept the copies and started *mixing* them; "Everybody's style is my style"). **The four-arm system** (owner-locked chat-canon): arms retractable — four arms OUT is gyro brawler, arms IN is human Tekken style, arms FLOATING detached is its own thing — same inputs as the Tekken stance-switch fighters. The robot/costume question is NEVER to be answered. Limb-system build on main at `tools/limb-system/dxmmii/` (107 files, PR #221).
- **What the full canon moveset IS.** **Mokujin mimicry, Tekken rule: each round/match, the mimic binds a random roster fighter's full moveset — moves, stances, and that fighter's animation bank. No fixed moveset of his own.** Plus his own 2 canon sigs (Crooked Patch `1+2`, Hidden Toolbox `1+4`) and the four-arm stance system. The `mimic` block in `dxmmii-patchwork.json` (design, current wiring, mechanic status, handoff) and `docs/anim/DXMMII-ANIM-GAP-20261023.md` record the design.
- **Sources to pull from.** (a) The roster's own movesets (the mimic borrows them — no new source game needed for the mechanic). (b) The fallback bank: T3 Jin rows (166 per the gap doc; file now counts 170 moves — drift noted). (c) The four-arm rig/animation (tools/limb-system/dxmmii/; Bannon's Goro four-arm rig files as canon precedent). Mokujin has NO T3 bank (type 15, BNS record 295 size 0).
- **In-repo vs missing.** IN REPO: `game/assets/movesets/dxmmii-patchwork.json` — 170 moves, `tekken_base: "Mokujin"`, `t3_source: "jin"`, 57 inputs; `dxmmii.json` — 150 moves, 2 sigs (Everybody's Sample `1+4`, Tongue In, Run `1+2`) — **staged, never loads** (bare `dxmmii` id: index + MOVESET_IDS only). Roster: `dxmmii-patchwork` IS selectable (model `dxmmii-tripo`, 3-slot attire ladder). MISSING: **the mimic selection mechanic itself** (game code, not moveset data — closest existing mechanism: Trader's Mimic mode, `game/js/modes.js` `traderFoe(playerChar, bout, randomMoveset)`); fallback-bank motion (no DXMMII bank); SHOW clips (win/intro/taunts — none documented).
- **Plays today.** `dxmmii-patchwork.json` (own file, per `fighter.js:899` + `main.js:1516`). CORRECTION TO THE 2026-10-23 DOCS: both the gap doc and the file's `mimic` block say "roster-full.js maps dxmmii-patchwork → moveset 'demonio' (static). DXMMII plays Demonio's moveset every round." That phrasing is stale as mechanism — the current fight path loads by fighter id, so he plays his own Jin-bank fallback file. **The gap itself stands** (static file, not mimicry); only the "plays demonio" wording is outdated. See §10.3.
- **Build-lane slot: 3E (game-code lane + moveset lane).** 1) Implement Tekken-style mimic selection (random roster moveset per round/match) for `dxmmii-patchwork` — the file then serves as the fallback bank. 2) Wire the four-arm stance system to the mimic (arms OUT/IN/FLOATING). 3) SHOW clips. Do NOT delete the static wiring until the mimic lands (gap doc's standing instruction).

---

## 7. KUTZ — joining the roster (Goh Hinogami, Virtua Fighter 5)

- **Identity.** Owner addendum 2026-11-20 ~19:34: **Kutz + Realizzt COUNT and join the playable roster** (`ROSTER.md`, "ROSTER ADDITIONS — SIX STAGED FIGHTERS"; PR #1806). No roster entry yet — blocked, in order: (1) correct moveset (P2 rebuild owed), (2) model (no `kutz.glb` on main). Index entries already exist, so once kit + model land, only the `roster-full.js` entry (+ tier + attire ladder) is left.
- **What the full canon moveset IS.** **Goh Hinogami's full Virtua Fighter 5 kit** — judo-based, the real Goh moveset, not a Tekken proxy. Plus 2 canon sigs already filed (Doesn't-Care Drop `1+4`, Moshpit `1+2`, method BUILD, `wh:` placeholder refs).
- **Sources to pull from.** **NONE in-repo and none found anywhere public.** `docs/research/VF5-TEARDOWN-HUNT-20261120.md` (Lane 1, 2026-11-20): "NO complete working VF5 teardown exists anywhere found. No pre-extracted, complete, working VF5 moveset / animation / motion source for Goh, Brad Burns, Dural, or any other VF5 fighter exists in any public source searched live." "Missing from the repo: `vf-goh.json`, `vf-brad.json`, `vf-dural.json`." What EXISTS: (a) community movelists as text/video (VFDC, GameFAQs, YouTube video movelists incl. Brad + Goh) — the repo's 7 existing `vf-*` kits are built from exactly this class of source (federation conversion, Tekken notation); a `vf-goh.json` could be transcribed the same way. (b) Tools, not teardowns: MikuMikuLibrary/FarcPack (opens/rips VF5 models/textures/motions — needs the game files `mot_db` + `mot_*` farcs from `rom/objset` + `rom/rob`; no pre-extracted motion dump ships with it). (c) `sp00nznet/vf5` PS3 static recomp (BLUS30020) — loading screens only, not a working game/moveset/motion. (d) DeviantArt VF5FS mods (`gohitm.farc` 43,611,682 B, `braitm.farc` 47,006,173 B, …) — model/texture swaps only, no motion. (e) In-repo VF bank: `game/data/moveset-library/banks/vf5.json` — 96 moves, federation conversion from community movelists (El Blaze 28, Jeffry 25, Wolf 21, Lei-Fei 22) — **no Goh rows**; per-character `vf-*.json` files: akira, elblaze, jeffry, kage, leifei, sarah, wolf — **no goh**. NOTE: `claimed-map.json` lists "Cipher→Goh" as a *candidate* (not locked) VF5 mapping for a Brutal Fist fighter — separate from Kutz; do not confuse the two Goh claims.
- **In-repo vs missing.** IN REPO: `game/assets/movesets/kutz.json` — 160 moves, `tekken_base: "Goh Hinogami"`, `t3_source: "king"`, `t3_bank: "moveset_king.json"` — i.e. **King's kit, 98% per ROSTER.md**. MISSING: the Goh kit itself; the model (`kutz.glb`); the roster entry.
- **Plays today.** Not playable (no roster entry). The file exists in MOVESET_IDS and loads only if requested.
- **Build-lane slot: 3F (with Realizzt).** 1) Transcribe `vf-goh.json` from community movelists (VFDC/GameFAQs/video) in the repo's federation-conversion style, OR land a real VF5 motion extraction if game files become available (MikuMikuLibrary/FarcPack route needs the game files first). 2) Rebuild `kutz.json` on the true Goh kit (P2 rebuild). 3) Model + roster entry. Licence: VF5 community movelists (GameFAQs/VFDC) — log honestly; licence never gates.

---

## 8. REALIZZT — joining the roster (Brad Burns, Virtua Fighter 5)

- **Identity.** Same owner addendum as Kutz (2026-11-20 ~19:34): joins the playable roster; same two blockers (correct moveset, model — no `realizzt.glb` on main).
- **What the full canon moveset IS.** **Brad Burns' full Virtua Fighter 5 kit** — muay thai, the real Brad moveset, not a Tekken proxy. Plus 2 canon sigs already filed (Certified Slam `1+4`, Wizard of the Mic `1+2`, `wh:` placeholder refs).
- **Sources to pull from.** Same hunt result as Kutz (§7): no `vf-brad.json` anywhere in the repo, no complete working VF5 teardown found anywhere public; community movelists (VFDC, GameFAQs Brad guide, YouTube video movelists) exist as text/video and are the transcribable route; MikuMikuLibrary/FarcPack needs the game files; `braitm.farc` (47,006,173 B) is a model/texture swap only. In-repo VF bank has no Brad rows (El Blaze / Jeffry / Wolf / Lei-Fei only).
- **In-repo vs missing.** IN REPO: `game/assets/movesets/realizzt.json` — 156 moves, `tekken_base: "Brad Burns"`, `t3_source: "jin"`, `t3_bank: "moveset_jin.json"` — i.e. **Jin's kit** per ROSTER.md. MISSING: the Brad kit itself; the model; the roster entry.
- **Plays today.** Not playable (no roster entry).
- **Build-lane slot: 3F (with Kutz).** Same route as Kutz: transcribe `vf-brad.json` from community movelists (federation conversion) or land real VF5 motion; rebuild `realizzt.json`; model + roster entry.

---

## 9. BURGER — The Hunger Soul

- **Identity.** "The Hunger Soul, claimed by the Appetite Room. Shapeshifter cursed with INFINITE HUNGER and INFINITE STARVATION." `roster/burger/CANON.md`: "The most transformations of any character in the game." Slim Bob (TTT2) is NOT a separate character — Burger's uncursed attire. Attire 1 = Demon mode, possessed by greed (owner Tripo b3eed68b).
- **What the full canon moveset IS.** **Bob's FULL Tekken moveset + all animations attached to Burger (base form), PLUS Kusaregedo's Samurai Shodown V/VI kit per demon form** — a multi-form transform system: chain (possible) lower form → base/chill human → cursed human → Getting Hungry → Feral Demonic Hunger → Speed Demon → The Mouth → Mini Tank → more demon forms → **final form (Attire 1 — mix of ALL smaller forms' abilities + exclusives)**. Each form has its own moveset file and switches on the transform (roster forms chain). Demon forms are *demon-flavored*: the move names are Kusaregedo's (SNK) re-skinned into Burger's hunger theme.
- **Sources to pull from.** (a) T8 Bob frame data (already folded into `burger.json` per `canon_note`). (b) Samurai Shodown V/VI Kusaregedo kit — frame data via DreamCancel/Tekitogate (per the form files' `samsho_source: "kusaregedo"` / `proxy_note`), layered on the Bob base. (c) Slim Bob from Tekken Tag Tournament 2 (uncursed attire).
- **In-repo vs missing.** IN REPO: `game/assets/movesets/burger.json` — 552 moves, `tekken_base: "Bob"`, `t3_source: "bryan"` (Bob has no T3 bank — Bryan is the proxy), 2 sigs (Appetite's Grip `1+4`, Side Dish Slam `1+2`), T8 Bob frame data folded in; `burger-speed-demon.json` — 454 moves, "Weakest demon form, fastest mode" (Kusaregedo kit); `burger-the-mouth.json` — 454 moves, "Second demon form. Head overgrows body: slow, topples over, too heavy, clumsy. Weak normals, devastating head/bite attacks"; `burger-demon.json` — 466 moves, final form (specials: Infinite Feast, Starvation's End, Second Helping, Hungry Hands, Never Enough, Toy Transformation, Grater Langouste). Roster forms chain: burger → speed-demon → the-mouth → demon, with down edges. MISSING: kits for the other canon forms — **Getting Hungry, Feral Demonic Hunger, Mini Tank, cursed human, the possible lower form** — no moveset files exist for any of them. `canon_note` says "Base form only (burger-demon kits were done separately in PR #337, untouched)".
- **Plays today.** `burger.json` base; the 3 demon forms switch moveset on transform (roster forms).
- **Build-lane slot: 3H.** 1) Build the 5 missing form kits (Getting Hungry → Mini Tank) from the Kusaregedo + Bob sources, in the form-chain order. 2) Verify the final-form kit carries the smaller forms' abilities + exclusives. 3) Wire the uncursed (Slim Bob) attire.

---

## 10. DEATHFANG — The Werewolf (Iori Yagami + beast)

- **Identity.** Proprietary character based on Iori Yagami (KOF), "chained/shackled, emo, 'NO FUTURE' face tattoo" (Soul Eater). `roster/deathfang/CANON.md`: human form is an emo loner, misunderstood; the werewolf form is "a monster that terrorizes towns — bloodlust; that's why he was put in prison." Owner Tripo models for BOTH forms supersede the Iori reskin as canon attires (human 6486151e, werewolf b4094ecf).
- **What the full canon moveset IS.** **Iori Yagami's full KOF moveset — stance, animations, normals — as the base for BOTH forms, PLUS the werewolf form's beast mix-in moves.** Owner rule (2026-10-20): stance and normal locomotion stay Iori's in BOTH forms (only a more werewolf-flavored run cycle excepted); beast flavor lives ONLY in the wolf mix-in attacks (claw/bite/lunge). Transform mid-fight human ↔ werewolf at a full nine-soul meter (WEREWOLF UNLEASHED, 1.35× power). The werewolf super is CRIMSON HOWL (1 special in each file).
- **Sources to pull from.** (a) KOF Iori motion (the file's `proxy_note`: "Iori has no T3 bank — Heihachi proxy (power), same bank as `iori.json`" — the in-repo Iori bank is `game/assets/movesets/iori.json`, 196 moves, Heihachi proxy). (b) **Real Iori rows**: KOF XV motion Start for the transformed moves — the file's `canon_note` admits the TRANSFORMED: SHACKLE HOWL (`1+2+3+4`) entry is "ADAPT from KOF XV motion Start (transformed)… clip NOT yet authored". The real KOF XV motion data is the build lane's source, not the placeholder. (c) Beast-movement references in the file's own note: KRONOS's Timberwolf Lunge and Vega's Rolling Claw (teardown-library entries) as patterning.
- **In-repo vs missing.** IN REPO: `game/assets/movesets/deathfang.json` — 98 moves (file count; index says 127 — stale), `tekken_base: "Iori Yagami (KOF)"`, `t3_source: "heihachi"`, `proxy: true`, `base_fighter: "iori"`; `deathfang-werewolf.json` — 98 moves, same proxy base, **13 wolf canon_moves** (CHAINBREAK RUSH `b,b+2`, FERAL MAUL `qcf+3`, GRAVE BITE `d/f+1+2`, MOONFANG LUNGE `f,f+2`, RISING MOONCLAW `ws+1+2`, TRANSFORMED: SHACKLE HOWL `1+2+3+4`, + 7 more listed in the file). Roster forms: deathfang up→werewolf (WEREWOLF UNLEASHED, 1.35×), werewolf down→deathfang (CHAINED AGAIN). MISSING: the real Iori rows for the 13 wolf moves (clips not authored); the eye fix — the human form's open eye shipped untextured/skin-colored and the owner REJECTED the painted-eye fix ("that eye looks so funny and it's not placed right; he also needs eyelashes and eyebrows") — real eye via customization, not a painted one.
- **Plays today.** `deathfang.json` base; `deathfang-werewolf.json` on transform.
- **Build-lane slot: 3I.** 1) Pull the real KOF XV Iori motion for the 13 wolf moves. 2) Author the wolf clips (real motion, never hand-tooled). 3) Eye/eyelashes/eyebrows via the customization system.

---

## 11. BYOU — The Sickness Soul (Wang Jinrei, T6 PSP)

- **Identity.** One of the nine (BYOU → Zui). `ROSTER.md` §4 + §6: owner ruling 2026-11-06, **"He can have wang if no one else does"** — Byou takes Wang Jinrei (T6). `CANON.md` §4: the Lei Wulong soul belongs to BYOU, but the *vessel name* is pending the owner's Lei naming decision (Lei's holder is Rave; see §6). 2 canon sigs: Sickness Pattern (`1+2`), Wrong Foot (`d+4`).
- **What the full canon moveset IS.** **Wang Jinrei's decoded Tekken 6 (PSP) kit, wired as a layer over the playable rows** — an owner-ordered base correction: the file was REBUILT 2026-11-06 (`wang_rebuild`, byou-wang lane) from Lei Wulong → Wang Jinrei. The rebuild removed the T7 Lei playable layer (571 moves) and the Lei stance_after map (Five Animals stances) from this file — both live complete in `rave.json` — and wired Wang's full decoded T6 kit as the `wang_kit` layer (254 records, 70 unique commands). The `t6_wang` ref marks every surviving playable entry whose input matches a Wang command.
- **Sources to pull from.** (a) The decoded T6 PSP Wang kit: `teardown/tekken6/movesets/t6psp-wang-moveset-v3.json` (v3 = most complete of v1/v2/v3, one decode of the same source container `idx68_entry724.bin`, SHA-256 `eb6224a929c39d1844540226282e01f1bb76084a2c3781ee1225c3efcedd3fd2`; 254 records total, 233 with decoded command, 70 unique commands — e.g. "1,1,2" Long Zhu Lian Pao; "1+2" Shoulder Smash / Mountain Splitter / Power Push). (b) T3 Jin bank for the playable rows (`teardown/tekken3/movesets/moveset_jin.json`) — see "Plays today".
- **In-repo vs missing.** IN REPO: `game/assets/movesets/byou.json` — 157 moves, `tekken_base: "Wang Jinrei"`, `t3_source: "jin"`, `t6_base: "wang"`, `t6_source` (above), `wang_kit` (254 records / 70 unique commands), `wang_rebuild` (2026-11-06, method documented). **The critical gap, in the file's own words (truncated in this lane's read — re-read before quoting): "Playable frame/damage/anim rows remain the T3 jin bank this file has always run: the Wang sources in our holdings contain nam…"** — i.e. the Wang layer is names/commands, **not playable frame/animation rows**. MISSING: playable Wang rows (frame data + animation for the 70 unique commands); `FIGHTER_BANK` binding — Byou's Lei override was REMOVED 2026-10-21 (owner: "Lei wulong is not byou… Byou keeps its own moveset's bank until the owner names Byou's base") — Byou currently has no named animation bank.
- **Plays today.** `byou.json` (own file). Its playable rows are **T3 Jin's bank** — Byou fights as a Jin proxy with a Wang name layer. Roster `moveset` field says `'demonio'` (legacy field, not the play path).
- **Build-lane slot: 3J.** 1) Convert the 70 unique Wang commands into playable rows (frame data + animation) — the Wang kit's T6 PSP source is the authority, not the Jin bank. 2) Name Byou's animation bank (owner call — the Lei vessel naming decision is the same conversation). 3) Re-read the full `wang_rebuild` method text before quoting it in any build doc.

---

## 12. CHATUR — The Four-Armed Oversoul (True Ogre, T3)

- **Identity.** "Chatur is True Ogre's Western Heart replacement (name locked 2026-10-22). Four-armed Oversoul spirit, temple dancer who refused to die; anchors the spirit realm; GYOU-touched." `game/assets/movesets/chatur.json` `canon_note`. Roster entry: `chatur` → moveset `'chatur'`, surge FOURFOLD MUDRA SURGE.
- **What the full canon moveset IS.** **True Ogre's Tekken 3 kit translated to her four-armed spirit body** — the double palms become fourfold strikes, the unblockables become refusals — **plus a second-pair-of-arms stance layer** (`layer2_stance`: Kuma's T3 stance, `t3:kuma:stance`, chain `arms2`, mode `override-masked` — the second pair guards/breathes with real motion under her own Ogre stance). Plus 7 canon moves (all method BUILD): BRIDGE OF ARMS (`b+1+4`), FOURFOLD MUDRA (`1+2+3+4` — collision with Deathfang's TRANSFORMED: SHACKLE HOWL on the same input `1+2+3+4`, noted in the 2026-10-24 wiring doc — resolver precedence needs an owner decision), GYOU'S MARK (`f,f+2`), OVERSOUL SURGE (`qcf+2`), REFUSED TO DIE (`d+1+2`), TEMPLE DANCE (stance loop `3+4`), BRIDGE (stance loop). Plus 2 stances (TEMPLE DANCE, BRIDGE).
- **Sources to pull from.** (a) T3 True Ogre bank: `teardown/tekken3/movesets/moveset_ogre.json` (bank `divmot14_ogre.bin`, bank_type 14, 330 rows) — cited in the file's `t3_source`. (b) T3 Kuma stance (`teardown/tekken3/movesets/moveset_kuma.json`) for the second-pair layer.
- **In-repo vs missing.** IN REPO: `game/assets/movesets/chatur.json` — 284 moves (file count; index says 281 — stale), `tekken_base: "True Ogre (Tekken 3)"`, `t3_source` (above), `anim_bank: "ogre"`. MISSING: animation for the 7 canon moves (all BUILD — `wh:` placeholder refs); the four-arm layer's motion (the Kuma stance layer is a *design* in the file — whether the second pair's motion is wired in the rig is the build lane's verification); the `1+2+3+4` input collision resolution.
- **Plays today.** `chatur.json` (own file). Bank: `'ogre'`.
- **Build-lane slot: 3K (with Megami + Menajerii — the canon-move animation trio).** 1) Verify the four-arm stance layer is actually wired in the rig (not just the file). 2) Animate/author the 7 canon moves from real Ogre/Kuma motion. 3) Resolve the `1+2+3+4` collision (owner call).

---

## 13. MEGAMI — The Sealed Door (Jun Kazama, TTT2)

- **Identity.** "Jun Kazama's Kazama Style Classic Martial Arts kit… a guardian's kit — parries, reversals (Attack Reversal), stance transitions (Genjitsu `b+1+2`, Izumo `f+1+2`), frame-perfect punishment." Roster entry: `megami` → moveset `'megami'`, surge SEALED DOOR SURGE.
- **What the full canon moveset IS.** **Jun Kazama's Tekken Tag Tournament 2 kit, rebuilt with Tekken inputs, PLUS a 4-move MADE canon system** — the Sealed Door system: Kaimon (Opening) (`GEN 1+2`), Seal of the Shrine (`RAGE,d/f+1+2`), Sealed Door (`d/b+1+2`), Threshold Keeper (`b+1+2~b`, BUILD, stance). The canon system is the only MADE spec in the repo reused by the 2026-10-24 wiring (PR #1012, `game/assets/anim/made/megami/megami-canon-made.json`).
- **Sources to pull from.** (a) TTT2 Jun movelist — **documented, no teardown bank**: `ttt2_source: "tekken.fandom.com/wiki/Jun_Kazama/Tekken_Tag_Tournament_2_Movelist"`. **Jun is NOT in T7** — "TTT2 is the source, NOT T7" (file's `ttt2_note`). (b) The MADE spec (PR #1012) for the 4 canon moves. (c) TTT2 animation bank: `game/assets/anim/t3/jun/` (`FIGHTER_BANK megami: 'jun'`).
- **In-repo vs missing.** IN REPO: `game/assets/movesets/megami.json` — 304 moves (file count; index says 299 — stale), `tekken_base: "Jun Kazama (Tekken Tag Tournament 2)"`. MISSING: the 4 canon-move **clips are NOT yet authored** (MADE spec exists; no clips); a TTT2 Jun teardown (the source is a wiki movelist, not extracted data).
- **Plays today.** `megami.json` (own file). Bank: `'jun'`.
- **Build-lane slot: 3K (with Chatur + Menajerii).** 1) Author the 4 MADE canon clips from the PR #1012 spec. 2) Verify the TTT2 Jun kit against the wiki movelist (no teardown to check against — flag any move that can't be sourced).

---

## 14. MENAJERII — The Menagerie (Roger Jr., TTT2)

- **Identity.** "Roger Jr.'s boxing-kangaroo kit authored FRESH with TEKKEN inputs (owner directive — no Injustice 2 input system): Rocket Stance (`b+1+2`) and Bobbin Dance (`b+3+4`) stances, the Giant Swing, Animal Uppercut, twin 10-hit tenstrings." Roster entry: `menajerii` → moveset `'menajerii'`, surge MENAGERIE SURGE.
- **What the full canon moveset IS.** **Roger Jr.'s Tekken Tag Tournament 2 kit, authored fresh with Tekken inputs, PLUS a 4-move canon system** — Boar's Commit (`f+2+3`), Heron Strike (`HRN 1`, BUILD), Heron's Patience (`b+1+3`, BUILD, stance), Serpent's Economy (`d/b+2+3`) — the beast-temperament layer (boar / heron / serpent) on a boxing-kangaroo base.
- **Sources to pull from.** (a) TTT2 Roger Jr. movelist — **documented, no teardown bank**: `t3_source: "tekken-wiki TTT2 Roger Jr. movelist (documented, no teardown bank)"`. (b) TTT2 animation bank: `game/assets/anim/t3/roger/` (`FIGHTER_BANK menajerii: 'roger'`).
- **In-repo vs missing.** IN REPO: `game/assets/movesets/menajerii.json` — 193 moves, `tekken_base: "Roger Jr. (Tekken Tag Tournament 2)"`. MISSING: clips for the 4 canon moves (BUILD entries — `wh:` placeholder refs); a TTT2 Roger teardown.
- **Plays today.** `menajerii.json` (own file). Bank: `'roger'`.
- **Build-lane slot: 3K (with Chatur + Megami).** 1) Author the 4 canon-move clips. 2) Verify the TTT2 Roger kit against the wiki movelist.

---

## 15. PHANTOM — The Ghost Blade Soul (vessel of JIN the Blade Soul)

- **Identity.** Vessel of JIN (刃, the Blade Soul). "May already be dead — deliberately ambiguous." `CANON.md` §2 + §4; `roster/phantom/CANON.md` (face ruling owner 2026-10-19: nobody has seen his face; mask is Fiend/oni-yokai style with Japanese curved top-and-bottom canine teeth, always showing; long white hair past the waist like Jiraiya; exactly 3 seconds of silence after a kill). **"There is NO Jin Kazama in our game at all — the ONLY Jin is the soul JIN"** (`CANON.md` Law 2) — and the §7 "JIN KAZAMA" bible section contradicts it (flagged in PR #1806, owner call open: retire the section or amend Law 2).
- **What the full canon moveset IS.** **Yoshimitsu's kit — sword, spinning attacks, teleportation, self-damaging power moves.** The kit content is a straight Tekken port; the canon complexity is **identity/duplication**, not move content: **two near-identical files exist** — `phantom.json` (1,019 moves, 3 sigs: Cut Is the Prayer `1+2`, Mask-Slip Spin `u+1`, Three Seconds Quiet `d+1+2`) and `jin_soul.json` (1,012 moves, 2 sigs: Blood Ends With Me `1+2`, Red-Eye Warning `u+1`) — both `tekken_base: "Yoshimitsu"`, `t3_source: "yoshimitsu"`, both with T8 Yoshimitsu frame data folded in. The soul JIN is "folded into Phantom's attire ladder" (owner directive 2026-10-22: "Yoshimitsu is supposed to ladder into Phantom's attires, not stand alone") and `SOUL_IDS` excludes JIN for that reason.
- **Sources to pull from.** (a) T3 Yoshimitsu bank (`teardown/tekken3/movesets/moveset_yoshimitsu.json`). (b) T8 Yoshimitsu frame data (already folded in, both files).
- **In-repo vs missing.** IN REPO: both files above. MISSING: the **decision** — which file is the fighter's kit (`phantom.json` vs `jin_soul.json`); `jin_soul` is in MOVESET_IDS but has **no roster entry** (never plays); the roster `phantom` entry maps `moveset: 'yoshimitsu'` (legacy field — no `yoshimitsu.json` file exists, so the legacy path is dead). The `wh:` sig refs (community bases `144_28.fbx` / `144_20.fbx`) are `pending-gpu-retarget`.
- **Plays today.** `phantom.json` (own file, per `fighter.js:899`). Bank: `'yoshimitsu'`.
- **Build-lane slot: 3L (last — reconcile, don't build).** 1) Owner/coordinator decision: which file is canonical; merge or retire the other. 2) Wire the chosen file + sig animations. 3) Fix the dead `'yoshimitsu'` roster mapping. This is a reconciliation job, not a kit build.

---

# §5 — BORDERLINE (Tier 2): include with the exact ambiguity — coordinator/owner decides promotion

Each entry states the test it meets/fails and what would settle it. **Do not build these as canon movesets until promoted.**

| Fighter | Kit as filed | Meets test? | Exact ambiguity / what would settle it |
|---|---|---|---|
| **POND** | Raven T7 kit, 620 moves (T8 raven 177 + T7 masterraven 292 merged 2026-10-23); 5 canon specials: TONGUE LASH `f+1+2` (frog tongue, "far more range than her arms"), STILL WATER `d+1+2`, EGG GUARD `b+1+4`, MIST VEIL `qcb+3+4`, BOUNDARY CROSSING `f,f+3+4`. `canon_note`: "Master Raven's Tekken 7 kit translated to her still-water body: the teleports become mist, the cruelty becomes patience." Bank `'raven'` (`game/assets/anim/t3/raven/`). | Fails (e): same-character T7 kit; the 5 specials are a flavor translation, no second source. | **Is "teleports become mist" a moveset modification or a skin?** Settles by: owner says the mist/tongue system is a distinct mechanic (promote) or a reskin of Raven's teleports (straight). |
| **TOBI** | Hwoarang T3 kit, 729 moves (`t3_source: "hwoarang"`); 6 canon moves (Courier's Dash `f,F+4`, Escape Soul Flurry `qcf+3`, Longleap `WR+3`, Satchel Swing `SS+3+4`, The Undelivered Letter `d+1+2`, Tip-Off `b+1+2`). Bank `'hwoarang'`. | Fails (e) narrowly: same-character T3 kit + 6-move courier layer. | **Does the 6-move courier layer make it canon?** Settles by: owner says the courier kit is a distinct system (promote) or the standard sig layer (straight). Note: Tobi IS Hwoarang's holder (PR #1806) — the Hwoarang kit is rightfully his. |
| **RYUSAN** | Lucky Chloe T7 kit, 211 moves; 6 canon moves (Acid Rain Dance `SCT,b+3+4`, Corrosion Claw `d/b+3+4`, Don't Tell Me To Calm Down `b+2+3`, Jotei's Receipt `hcb+1`, Meltdown `d+1+2`, Vitriol Spit `qcf+1`). Bank `'luckychloe'`. | Fails (e) narrowly: same-character T7 kit + acid/corrosion layer. | Same question as Tobi. The acid/corrosion layer is the largest canon layer of any borderline fighter (6 BUILD moves). |
| **DOC FRANK** | **REAL** Dr. Bosconovitch T3 kit, 380 moves (`proxy_note`: "REAL Dr. Bosconovitch moveset — Tekken Wiki Tekken 3 movelist (complete T3 command list), not the old Gun Jack proxy. Old proxy moves preserved under legacy_proxy_moves"); 7 canon moves (Crayon Notes `1+4`, Peer Review `1+2`, Afterimage `b,b+3+4`, Energy Absorption `b,b+1+2`, Eye Laser Beam `d,d/f,f+1+2`, Ki Blast `d/f+1+2`, Rocket Punch `d,d/f+1`). Attire-variant files exist (`doc-frank-frankenstein.json`, `-hood.json`, `-machine-shop.json`, `-wowomomo.json`). Forms are model-only transforms (no moveset switch). | Fails (e) narrowly: same-character T3 kit + inventor-themed layer. | Same question as Tobi/Ryusan. The 7-move layer is the largest of any borderline fighter. |
| **KRONOS** | **Zangief + Golem (Urban Reign)** composite, 900 moves (`t3_source: "king"`); 8 canon moves (ATOMIC BUSTER `f,f+2+4`, CYCLONE CHOP RUSH `qcf+2`, CYCLONE KNEE `f+3`, CYCLONE UPPERCUT `d/f+2`, FINAL ATOMIC BUSTER `b,n,f,b,n,f+1+2`, FLYING BODY PRESS `u/f+3+4`, IRON STANCE `b+3+4`, TIMBERWOLF LUNGE `f,f+3+4`). `kronos-attire2` index: 2,600 moves / Timberwolf set 142 moves per movesets.js comment — **discrepancy, not resolved**. | **Meets (b) on paper** — cross-game composite base. | **Is Kronos a canon-moveset character or a custom fighter with a composite kit?** The test was written for the owner's "canon movesets" (his canon characters); Kronos is a custom fighter, not Tekken-canon. Settles by: owner/coordinator says the composite test applies to custom fighters too (promote) or canon-moveset status is reserved for his canon characters (keep in bulk). |
| **KORESHI** | **Kakashi (Naruto) + Super Saiyan 4/5 + ninja**, 1,080 moves (`t3_source: "heihachi"`); `proxy_note`: "the owner's own creation… Heihachi proxy (power)"; specials 73, first CHIDORI BURST. | **Meets (b) on paper** — cross-game composite. | Same question as Kronos. |
| **RYUJI-ROCK / CORNERSTONE** | **Ryuji Yamazaki (KOF) × The Rock**, 129 moves in file (index says 24 — stale); `proxy_note`: "King proxy (grappler; owner: Rock Bottom frame data from King in Tekken, chain row 281)"; 8 canon moves (BRAHMA BULL LARIAT `f,f+2`, KNIFE SLASH `f+1+2`, LAYIN' THE SMACKDOWN `1+4`, PEOPLE'S ELBOW `u/f+2`, SAND KICK `d/b+2`, SERPENT SLASH `qcf+1`, TONGUE OUT `1+2`, ROCK'S DDT `d/b,d/b+1+2`); specials ROCK BOTTOM, PEOPLE'S ELBOW DROP; 2026-10-21 union with the full Yamazaki set from `ryuji.json`. Name locked CORNERSTONE (owner 2026-10-21). | **Meets (b) on paper** — cross-game composite. | Same question as Kronos/Koreshi. Note: two roster entries exist (`ryuji` model-pending, `ryuji-rock` CORNERSTONE) — the `ryuji` card's status is unresolved. |
| **VAINABEL** | Bass Armstrong (DOA) conversion, 60 moves in file (index says 52 — stale); 2 sigs (Elias Brothers' Chokeslam `1+4`, Purple Light Sermon `3+4`). `doa-bass.json` (22 moves) is the DOA bank. | Fails: thin kit; DOA conversion is the standard federation pattern. | **Promote only if** the Bass kit gets a full rebuild (DOA rows + canon layer). As filed, it is a straight conversion with signatures. |
| **KINPO + AWA POP** (SHA sisters) | Kinpo: Asuka base, Jin-bank proxy, 525 moves, 2 sigs (Buttercup Finishes `1+2`, Plus-One Pressure `f+1`). Awa Pop: Nina base, Jin-bank proxy, 909 moves, 2 sigs (Last Thing You Hear `1+4`, Pop! `1+2`). Both are SHA splinters (Kinpo = thorn, Awa Pop = bubble). | Fail: same-character kits on proxy banks. | **Do the sisters get canon-modified kits (thorn/bubble moves) or stay proxies?** Owner call. If Saku Ra's bloom kit gets the xiamot treatment, the sisters' kits are the natural follow-on. |
| **CYBORG X — RULED OUT** | Alisa via Gunjack proxy, 624 moves; T8 Alisa frame data folded in; 2 sigs (Lullaby Hum `d+1+2`, Motion Mandatory `1+2`); bank `'gunjack'` (legacy path `'gunjack'`); stance = CMU 13_17 boxing guard. The GYOU splinter in his chassis is **story, not moves**. | Fails all tests: straight Alisa port. | Listed only to close the question: the Gyou-splinter story does not make the kit canon. |
| **CHARGER — RULED OUT** | Blanka kit **verbatim**: 199 moves, "inputs/frame data IDENTICAL; only signature names in the Electric Thunder and Rolling families were renamed to CHARGER's ice+electric identity" (`canon_note`). | Fails all tests: straight port with a rename layer. | Listed only to close the question. |
| **SILVERTONGUE / LILI — RULED OUT (and not a fighter)** | Lili kit via Xiaoyu proxy, 508 moves (`lili.json` file: 375 moves — stale index; `silvertongue.json` file: 508). Specials incl. Wall Jump Backflip, Allonger Le Bras, Alstroemeria, Piercing Thorn, Root of Evil. **Lili has no roster entry** — custom-character material only (owner addendum 2026-11-20). | Fails all tests: straight Lili port. | Source-law exception still owed for the Xiaoyu proxy layer: "Ling Xiaoyu" is claimed by Saku-ra in `game/data/moveset-library/claimed-map.json`. Fold-in needs the exception + the assembler gap (`movesets.js` integration + live fight proof; custom fighter fights on the `'jin'` fallback until then). |

---

# §6 — STRAIGHT TEKKEN PORTS (bulk table — not canon movesets)

One Tekken character's kit on that character's own bank (or same-character T7/TTT2 kit), no form switch, no composite, no owner-ordered rebuild. The standard 2–3 signature moves + T8 frame-data fold-in do not change the classification. Counts are **file counts as pulled**; "index" means the file was not header-read in this lane and the count comes from `game/assets/movesets/index.json` (stale — see §10.1).

| Fighter | Base (tekken_base) | Bank (t3_source) | Moves | Sigs | Note |
|---|---|---|---|---|---|
| RIN | Jin Kazama | jin | 710 | 2 | Cold Dignity `b+1`, Still Point `1+2` |
| KAI | Eddy Gordo | eddy | 735 | 2 | File t3_source `eddy` (index stale: `jin`) |
| TOU | Paul Phoenix | paul | 542 | 2 | File t3_source `paul` (index stale: `heihachi`); the OTHER Paul holder (Gyou is second) |
| RETSU | Bryan Fury | bryan | 739 | 2 | No Mission `1+4`, Pure Force `1+2` |
| PANTERA | King | king | 874 | 3 | 116 specials |
| DIABLO | Heihachi Mishima | heihachi | 661 | 3 | Membrane Tear `qcf+1` BUILD; his Heihachi KMD has empty vertex rows (parts 2/9/13) blocking the shared bake pipeline — motion gap, not moveset gap |
| SKULL | Bryan Fury | bryan | 688 | 3 | |
| SAM-UR-A1 | Gun Jack | gunjack | 860 | 3 | |
| RAVE | Lei Wulong | lei | 796 | 2 | File t3_source `lei` (index stale: `xiaoyu`); T7 Lei layer from t7chicken; the old Byou/Lei history lives in this file (3 "byou" mentions) |
| DIO | Akuma | akuma | 140 | — | File count 140 (index stale: 275) |
| ZUI | Steve Fox | jin (proxy) | 462 | 2 | The Steve body Demonio wrongly wore; Zui's own kit |
| YUKIHYO | Armor King | king (proxy) | 560 | 2 | |
| NIGHTWOLF | Julia Chang | xiaoyu (proxy) | 567 | 2 | Ancestor's Answer `b+1+2` BUILD; she/her always (canon) |
| STAR | Christie Monteiro | xiaoyu (proxy) | 908 | 2 | |
| TORCH | Anna Williams | jin (proxy) | 892 | 2 | |
| SCIMITAR | Shaheen | jin (proxy) | 362 | 2 | |
| MICHIKO | Katarina | jin (proxy) | 344 | 2 | |
| WATERFALL | Josie Rizal | jin (proxy) | 365 | 2 | |
| PURPLE RAIN | Lee Chaolan | jin (proxy) | 569 | 2 | |
| BRUNO | Miguel Caballero Rojo | bryan (proxy) | 328 (index) | — | File not header-read |
| NEGATIVO | Negan | bryan (proxy) | 292 | 2 | |
| THOR | Ganryu | bryan (proxy) | 330 | 2 | |
| SLICE | Dragunov | bryan (proxy) | 486 | 2 | |
| KING TYRANT | Eddy Gordo | xiaoyu (proxy) | 848 (index) | — | File not header-read beyond index |
| BUFFALO BILL | Law | law | 796 | 0 | **No `canon_moves` key at all** — the truest straight port in the repo |
| DOROWANI | Gon | gon | 175 | — | Direct T3 gon bank (bank type 19, 369 rows, 157 attacks); specials MEGA DINO BREATH, DINO BREATH |
| GASHADOKURO | Kuma | kuma | 530 | — | |
| AOTSUKI | Panda | kuma (proxy) | 530 | — | `proxy_note`: T3 Panda shares Kuma's bank; T7/T8 Panda's diverged kit is a later gapfill |
| MARIPOSA | Zafina | (none) | 372 | 8 specials | Gilgamesh Blast, Sagaris, Tiamat; no `t3_source` |
| CHORDZ | Lars Alexandersson | jin (proxy) | 328 | 2 | |
| CAIN ELIAS | Undertaker (WWE archetype) | king (proxy) | 46 | 5 | Chokeslam, Hell's Gate, Last Ride, Old School, Tombstone Piledriver; `proxy_note`: no Undertaker teardown exists; signature throws are WH-original |
| **Brutal Fist (26 fighters)** | T3 bank per role | per role | 11 each (index) | — | `bf-*` files are 11-move stubs (~7.8 KB each); full kits live in `ur-char*.json` (Urban Reign donor clips, e.g. bf-aaron-ruben: T3 bank king, UR donor ur-char002). **Not built yet** — follow-up lane. |

**Library banks (not fighters — do not build as characters):** `t3-*.json` per-bank files (paul 497, lei 790, hwoarang 723, eddy 707, julia 419, nina 754, anna 743, law 693, kuma 530, ogre 161, gon 151, bosconovitch 266, forestlaw 102); `vf-*.json` (akira 20, elblaze 28, jeffry 25, kage 14, leifei 812, sarah 14, wolf 21 — index counts); `doa-*.json` (ayane 23, bass 22, hayabusa 18, jannlee 21, kasumi 20, tina 26); `sf-*.json` (akuma 168, blanka 37, cammy 10, chunli 10, dhalsim 10, guile 11, ken 32, mbison 12, ryu 34, sagat 10, vega 36, zangief 36); `sunra.json` (Pac-Man base, 139 moves — file only, no roster entry).

---

# §7 — NOT FIGHTERS (do not build as characters)

| Id | What it is | Why it is not a fighter |
|---|---|---|
| `baek` | The custom-character material file (111 moves, Bryan bank) + the name Kevin replaced | `roster/baek/CANON.md`: "Baek does not exist as a character… The fighter IS Kevin." Baek folds into Kevin. |
| `lili` | Custom-character material (375 moves, Lili via Xiaoyu proxy) | Owner addendum 2026-11-20: Lili = custom-character material, NOT a roster entry. Folds into Silvertongue. |
| `sha` | Retired roster card (785 moves, Xiaoyu bank) | Owner order 2026-11-20: Saku Ra is ONE fighter; `sha` card retired; `sha.json` KEPT until the single-fighter load is verified (PR #1806). |
| `jin_soul` | Staged kit (1,012 moves, Yoshimitsu bank) | In MOVESET_IDS, no roster entry; soul JIN is folded into Phantom's attire ladder (owner 2026-10-22). See §4.15. |
| `dxmmii` (bare id) | Staged id (150 moves) | Index + MOVESET_IDS only; never loads. The selectable id is `dxmmii-patchwork`. |
| `sunra` | File only (139 moves, Pac-Man base) | No roster entry in `game/js/roster-full.js`. |

---

# §8 — WIRING PLAN (follow-up lanes, in build order)

**Principle:** Kevin first (the owner's named job). Zen starts in parallel because it has the longest lead time — do not gate Kevin on Zen. Kutz/Realizzt are the VF5 source problem, not a code problem. Every lane is research → source → rebuild → animate → wire → live-fight proof; **no lane claims "done" without the fighter playing the kit in a real fight** (the repo's own proof bar).

| Lane | Fighter(s) | First job (the hard part) | Then | Depends on / owner call |
|---|---|---|---|---|
| **3A** | **KEVIN** | Source the real Baek kit (re-teardown / T6 / TTT2 / community movelist) | P2 rebuild of `baek-master-white.json` on the true Baek bank; define + wire the canon modifications; animate 2 sigs (GPU retarget of `144_20.fbx` / `144_05.fbx`) | Owner call: `kevin.json` or keep `baek-master-white.json`? |
| **3B** | **ZEN** | VF5 motion RE + Dural motion set; Twelve 2D→3D conversion; Eleven from the SFV pull | MADE anims for all 25 true moves; resolve 6 NEEDS-INPUT + NEEDS-SPEC | Owner call: Zen's pronoun; SELECT_HIDDEN vs selectable comment |
| **3C** | **GYOU** | Verify the Paul base plays clean post-rebase | Build the flame layer (4 forms + 12 moves + infused VFX); file the flame forms in CANON.md | Owner call: is Paul permanent? |
| **3D** | **DEMONIO** | Recount the Devil slots; resolve the 18 displaced-key T7 Devil records | Wire the human form's kit; settle Bloodline Ember | Owner calls: human-form kit; Bloodline Ember outfit vs 4th form; CANON.md Law 2 vs JIN KAZAMA section |
| **3E** | **DXMMII** | Implement Tekken-style mimic selection (game code; Trader's Mimic mode is the pattern) | Wire the four-arm stance system to the mimic; SHOW clips | None — design is settled; mechanic is the gap |
| **3F** | **KUTZ + REALIZZT** | Transcribe `vf-goh.json` + `vf-brad.json` from community movelists (federation conversion), or land a real VF5 motion extraction | P2 rebuilds; models; roster entries | None — the source hunt is done (none found); transcription is the route |
| **3G** | **SAKU RA** | Walk-verify the xiamot input-key join from the cancel tables | Resolve the 13 conflicting T3 mappings; animate 3 sigs | Owner/spec: which mapping is correct (do not guess) |
| **3H** | **BURGER** | Build the 5 missing form kits (Getting Hungry → Mini Tank) | Verify the final form carries the smaller forms' abilities + exclusives | None — form chain is settled in canon |
| **3I** | **DEATHFANG** | Pull the real KOF XV Iori motion for the 13 wolf moves | Author the wolf clips; eye/eyelashes/eyebrows via customization | None — the painted-eye fix is already rejected; do not retry it |
| **3J** | **BYOU** | Convert the 70 unique Wang commands into playable rows (T6 PSP source) | Name Byou's animation bank | Owner call: the Lei vessel naming decision (same conversation as the bank) |
| **3K** | **CHATUR + MEGAMI + MENAJERII** | Animate/author the canon-move sets (Chatur 7, Megami 4 MADE, Menajerii 4) from real Ogre/Kuma/TT2 motion | Verify the four-arm stance layer is actually wired in Chatur's rig | Owner call: the `1+2+3+4` input collision (Chatur FOURFOLD MUDRA vs Deathfang SHACKLE HOWL) |
| **3L** | **PHANTOM / JIN_SOUL** | Decide which file is canonical | Merge or retire the other; wire sig animations; fix the dead `'yoshimitsu'` roster mapping | Owner/coordinator decision on the file |
| **Tier 2** | Pond / Tobi / Ryusan / Doc Frank / Kronos / Koreshi / Ryuji-Rock / Vainabel / Kinpo + Awa Pop | **Only on owner/coordinator promotion** — see §5 for each fighter's exact settling question | — | Owner calls listed in §5 |

**Owner calls that gate build lanes (plain list — put to the owner once, plainly, do not decide in a lane):** (1) `kevin.json` vs `baek-master-white.json`; (2) Gyou's Paul permanence; (3) Zen's pronoun ("she" vs "his"); (4) Demonio human-form kit (own moves vs base kit); (5) Bloodline Ember (outfit vs fourth form); (6) CANON.md Law 2 vs the JIN KAZAMA section (retire the section or amend Law 2); (7) Saku Ra's 13 conflicting T3 row mappings; (8) the `1+2+3+4` collision (Chatur vs Deathfang); (9) Tier 2 promotions (Pond, Tobi, Ryusan, Doc Frank, Kronos, Koreshi, Ryuji-Rock, Vainabel, Kinpo + Awa Pop); (10) Byou's animation bank / the Lei vessel naming decision; (11) the Lili Xiaoyu-proxy source-law exception (fold-in).

---

# §9 — LICENCE / SOURCE LOG (LICENCE-NOT-A-GATE: logged honestly; never blocks, never leaves a gap)

| Source | What it feeds | Licence / provenance as recorded |
|---|---|---|
| Tekken 3 teardown banks (`teardown/tekken3/movesets/moveset_*.json`, 21 files) | All T3-banked kits (Kevin's proxy, Gyou, Demonio, Saku Ra, Byou's playable rows, Chatur, DXMMII fallback, all straight ports) | Extracted from TEKKEN3.BNS on the owner's disc image, SHA-256-verified (`CANON.md` appendix). Bandai Namco commercial game; extracted by the owner/his lanes. |
| Tekken 7 motbin / frame data (`teardown/tekken7-steam/…`, `t7-devil-jin.json`, `t7-*.json` banks) | Demonio Devil kit, Saku Ra xiamot, T7 layers | Extracted from the owner's Tekken 7 Steam install (motbin GRE); frame tables from t7chicken (TekkenBot-extracted T7 frame data, dayhaysoos/t7chickenplus-graphql). |
| Tekken 8 frame data (wavu.wiki) | T8 fold-ins (Demonio, Saku Ra, Phantom, Burger, Megami note) | wavu.wiki, **CC0** (per `demonio.json` `canon_note`). |
| Tekken 6 PSP Wang decode (`teardown/tekken6/movesets/t6psp-wang-moveset-v3.json`) | Byou's Wang layer | Decoded from the owner's T6 PSP source container `idx68_entry724.bin` (SHA-256 recorded in the file). Bandai Namco commercial game. |
| TTT2 movelists (Tekken Wiki / tekken.fandom.com) | Megami (Jun), Menajerii (Roger Jr.), Doc Frank (Bosconovitch T3) | Community wiki documentation — **not a teardown**; moves are documented, not extracted. |
| Virtua Fighter 5 (community movelists: GameFAQs, GameRevolution, VFDC, YouTube) | `banks/vf5.json` (El Blaze/Jeffry/Wolf/Lei-Fei), `vf-*.json`; the Kutz/Realizzt transcription route | Community movelists; federation conversion (Tekken notation). No VF5 teardown exists anywhere found (Lane 1, 2026-11-20). SEGA commercial game. |
| Street Fighter (SuperCombo wiki; SFV pull) | Zen's Twelve/Eleven lineage; Charger's Blanka kit (`sf-blanka.json`) | Community wiki / the SFV pull (`teardown/street-fighter-5/`). Capcom commercial game. |
| KOF (KOF XV motion Start) | Deathfang's Iori rows / wolf moves | SNK commercial game; motion Start references in the file's `canon_note`. |
| Samurai Shodown V/VI (DreamCancel / Tekitogate frame data) | Burger's Kusaregedo form kits | SNK commercial game; frame data via community databases. |
| Dead or Alive (community) | `doa-*.json` banks; Vainabel's Bass kit | Community movelists. Koei Tecmo commercial game. |
| WWE (Undertaker archetype) | Cain Elias's 5 sig throws | **No teardown exists** (file's `proxy_note`); signature throws are WH-original. |
| Owner Tripo models (release `zen-tripo-pulls-20261021`, demonio/burger/deathfang Tripo ids) | Zen forms, Demonio forms, Burger A1, Deathfang forms | Owner-uploaded Tripo generations (model ids in `roster/*/CANON.md`). |
| Community animation bases (`game/assets/anim/oss/community/*.fbx`) | Canon sig animations (Kevin `144_05`/`144_20`, Saku Ra `88_06`/`144_13`, Phantom `144_28`/`144_20`, Jin_soul `144_20`) | OSS/community FBX; status `pending-gpu-retarget` in the files. |
| CMU motion capture (13_17 boxing guard) | Cyborg X's stance | CMU license — commercial-safe (per `roster-full.js` comment). |

---

# §10 — OPEN VERIFICATIONS / DISCREPANCIES (do not resolve silently — the build lanes must re-check)

1. **`game/assets/movesets/index.json` is STALE vs the files.** Verified drifts (file count governs): demonio 764 (index) vs 684 (file); rave `t3_source: xiaoyu` (index) vs `lei` (file), 1,086 vs 796 moves; kai `t3_source: jin` vs `eddy`, 877 vs 735; tou `t3_source: heihachi` vs `paul`, 681 vs 542; lili 508 vs 375; deathfang 127 vs 98; ryuji-rock 24 vs 129; megami 299 vs 304; chatur 281 vs 284; vainabel 52 vs 60; dio 275 vs 140; dxmmii-patchwork 166 (index) vs 170 (file); `sha` NOT in the index (retired); `t7-devil-jin` NOT in the index (bank file, not a fighter file); baek-master-white 132,635 B (index) vs 138,709 B (file). **The index must be regenerated from the files before any lane trusts a count.**
2. **Demonio Devil-slot completeness is disputed.** PR #1805's proof claims "slot winner is a Devil record 80/80" after wiring 20 slots (394–414). The 2026-11-21 alignment synthesis states the amended fix "keeps all 80 Devil moves in the Devil form, but only 60 of 80 inputs actually play a Devil move and 20 inputs have no move wired yet, and the 18 displaced-key Tekken 7 Devil records … are still open." This lane's own crude string-match count on the pulled `demonio-winged.json` (414 slots; 240 resolve to devil-tagged moves, 174 non-devil, 0 unresolved) **verifies neither number**. Lane 3D must recount from `demonio-winged.json` + `t7-devil-jin.json` before claiming completeness.
3. **DXMMII "plays demonio" is stale as a mechanism claim.** The 2026-10-23 gap doc and the `mimic` block both say the roster maps `dxmmii-patchwork` → `moveset: 'demonio'` and "DXMMII plays Demonio's moveset every round". Under the current fight path (`fighter.js:899`, `main.js:1516`) he plays his own `dxmmii-patchwork.json` fallback file. The gap (no mimic mechanic) stands; only the wording is outdated.
4. **Saku Ra: 13 conflicting T3 row mappings** for 1/2/3/4/1+3/2+4 (PR #1806 open Q4). The `t7_motbin` wiring is additive metadata, NOT joined to playable inputs.
5. **CANON.md appendix identity map is stale** vs the 2026-10-23 landing waves: Law, Ogre, Gon, Panda, Mokujin are listed as having NO WH mapping, but Chatur←True Ogre, Dorowani←Gon, Gashadokuro←Kuma are now rostered.
6. **Roster header stale:** `game/js/roster-full.js` says "48 selectable fighters"; 85 `{ id:` entries were counted.
7. **Zen interim drift:** the 2026-10-24 decision doc records 639 Heihachi rows; the file now holds 644 moves after the 2026-10-28 dural_rebase.
8. **Kevin file duplication:** `baek.json` (111 moves) vs `baek-master-white.json` (291 moves) — same Baek label / Bryan bank, different canon signatures; `merge_sources` says baek-master-white is an "attire variant of baek" (donors `[baek]`, 134→138). Lane 3A must separate Kevin's kit file from Baek's custom-material file.
9. **Phantom file duplication:** `jin_soul.json` (1,012) vs `phantom.json` (1,019) — near-identical Yoshimitsu kits, different sigs. Lane 3L decides.
10. **Gyou's flame forms are NOT in CANON.md** (file note: parent to file them in `docs/owner-directives.md` and `CANON.md`). Lane 3C files them.
11. **Zen SELECT_HIDDEN contradiction:** the set hides Zen while the comment above it says Zen stays selectable (PR #1806 open Q2).
12. **Zen pronoun open:** "she" (owner 2026-11-20) vs "his" (2026-10-24 decision doc, `zen.json`, `attires.js`) — PR #1806 open Q1.
13. **Rave carries the old Byou/Lei history** (3 "byou" mentions in `rave.json`) — the T7 Lei layer moved here in the 2026-10-21 correction; verify no Byou/Lei rows still leak into Byou's file.
14. **Byou's `wang_rebuild` method text was truncated in this lane's read** ("Playable frame/damage/anim rows remain the T3 jin bank this file has always run: the Wang sources in our holdings contain nam…") — re-read the full field before quoting it.
15. **Kronos attire-2 discrepancy:** index says 2,600 moves; `movesets.js` comment says his Timberwolf set is 142 moves. Unresolved.
16. **Canon-doc fix in flight:** the CANON.md fix has three of four files in; the last file timed out on upload and went through the browser instead (2026-11-21 synthesis) — verify the fourth file landed before citing CANON.md as current on the affected sections.

---

# Sources consulted (inventory of the evidence)

- `ROSTER.md` (main) — §4 Nine Souls, §6 owner-designed fighters, §8 ZEN, §9 GYOU, roster-additions addendum 2026-11-20 ~19:34 EST.
- `CANON.md` (main, 1,666 lines) — Law 2, §2 Demonio, §4 soul table + soul bodies + SHA three-way split + "On ZEN and GYOU", §7 Kevin + DXMMII, appendix T3 banks + identity map + JIN KAZAMA section (flagged).
- `game/js/roster-full.js` (main) — 85 select entries; per-fighter base/moveset/model/forms.
- `game/js/movesets.js` (main) — `_fetchOne`, `MOVESET_IDS`, loadouts (localStorage only), `playedMoveset`, Trader's Mimic reference.
- `game/js/fighter.js` (main) — `MOVESET_MAP` (86–140), `loadRealMovesets` (355–379), `bankIdFor` / `FIGHTER_BANK`, `_movesetId` (899), transform switch (1233–1235).
- `game/js/main.js` (main) — `loadRealMovesets` + `loadFighterMovesets` + `ensureMovesets` (1477–1516).
- `game/assets/movesets/index.json` (main) — 127 fighters + 26 BF (stale — §10.1).
- `game/data/moveset-library/claimed-map.json` — MOVESET SOURCE LAW (owner-locked 2026-10-22).
- `game/data/moveset-library/banks/vf5.json` — 96 moves, VF5 federation conversion.
- PR #1806 (MERGED) — "Fix Zen / Gyou / Saku Ra / Jin_soul canon confusion (documents + data)".
- PR #1805 (MERGED) — "Demonio attachment fixes: wire 20 Devil slots, remove Steve-body BASE attire, fix winged moveset name".
- `docs/decisions/2026-10-24-zen-base-decision.md` — Zen = Eleven/Twelve/Dural + own canon.
- `docs/canon-movelist-wiring-2026-10-24.md` — 190 canon entries across 66 files (additive only).
- `docs/ROSTER-CANON-GAPS-2026-10-23.md` — 69 roster dirs audited (stale as a census).
- `docs/research/VF5-TEARDOWN-HUNT-20261120.md` — Lane 1: no complete working VF5 teardown found anywhere.
- `docs/ZEN-DURAL-REBASE-2026-10-28.md` — Zen dural_rebase (644 moves by class).
- `docs/anim/DXMMII-ANIM-GAP-20261023.md` — DXMMII mimic gap.
- `docs/anim/VF5-DURAL-ANIM-GAP-20261023.md` — Dural motion gap (the single biggest blocker on Zen's permanent base).
- Per-fighter `roster/*/CANON.md` (main): zen, gyou, demonio, saku-ra, dxmmii, baek, jin, phantom, cyborg-x, burger, deathfang, kinpo, rave (pointer to kiko-tanaka).
- Moveset files read directly from main (headers + relevant sections): kevin set (baek-master-white, baek), zen, gyou (+ gyou-spirit-body), demonio set (demonio, demonio-winged, demonio-human, demonio-bloodline-ember, t7-devil-jin), sakura + sha, dxmmii set, kutz, realizzt, burger set (4 files), deathfang set, byou, chatur, megami, menajerii, phantom + jin_soul, pond, tobi, ryusan, docfrank, kronos, koreshi, ryuji-rock, vainabel, kinpo, awapop, cyborgx, charger, silvertongue + lili, and the straight-port spot checks (rin, kai, tobi, retsu, pantera, diablo, skull, samura1, dio, zui, yukihyo, nightwolf, star, torch, scimitar, michiko, waterfall, purplerain, cainelias, buffalo-bill, dorowani, gashadokuro, aotsuki, mariposa, chordz).

*Lane 2B — 2026-11-21. No moveset was built in this lane. No file was merged. The canon-moveset set above is the inventory the follow-up build lanes (3A–3L) work from.*
