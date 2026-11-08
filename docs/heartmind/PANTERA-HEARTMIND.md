# PANTERA'S HEARTMIND — DESCENT OF THE HOLD

Pantera's own HeartMind story and flow — the first per-character HeartMind, the template every other character follows. Built 2026-11-08, branch `pantera-heartmind`, commit `ba56303c61712e8c88aa859b7fd78e8470863103`, **PR #1649** (https://github.com/mhvnsnt/western-heart/pull/1649 — OPEN, MERGEABLE, +543/−8, 5 files), from main `a89b10b`. Not merged — parent lands.

> **Standing law, revised (Jay, 2026-11-07 ~22:32; criterion confirmed ~22:43 — SOURCE, not spelling):** "Devil" MAY appear, but ONLY in OUR own way and language (Jay's own characters and words — DIABLO and his title "The Devil Soul", "The Devil That Stays...", Diablo described as a devil, generic "the devil" in Jay's own prose). NEVER the Tekken way (Devil Gene, Devil Jin, "Jin's devil", "Devil Within"). "Jin" ONLY ever means the soul JIN (刃, the Blade Soul). Pantera's story uses neither word at all. The chapter title **"The Devil That Stays..."** is Jay's, allowed under the revised law, and **still unassigned to any character — it is NOT in Pantera's story** (test asserts its absence).

## What Pantera's descent is (plain words)

Pantera is the vessel of TOU (闘 — battle itself). He has nothing to resolve — the trial doesn't purify him, it *uses* him: he is the standard the others are measured against. He doesn't think about why he's here. The mat is here. He is here. He thinks the trial is a tournament that found the right fighter.

Five rooms, five main events — one tournament night:

1. **THE THRESHOLD** — "The mat is here. I am here." The Warden bars the door: big, loud, announces himself with every step. Size is not a hold.
2. **THE GALLERY OF MASKS** — "Every face that would not stay down." Masks, one after another, and every one of them gets up again. Under the last mask there is only the hold — it was never a mask, it was a mirror. **After this room, Demonio joins Pantera's corner** — the one who would not stay down walks with him. No warmth, just the work.
3. **THE DROWNING ROOM** — "Nothing buried. Only water, and a mat under it." They said something is buried down here. There is nothing buried. The trial looked for his dark and found a clinch.
4. **THE FURNACE** — "He hunts where the sky burns." The furnace asks what he will burn to stay himself. Nothing. The fire is his element, not his enemy. The heart with no body throws bodies at him — the trial is running out of fighters.
5. **THE STILL POINT** — "Yourself, unmasked. The watcher, wearing your shape." The shadow is the thing that has been watching — the long wait, the leverage, the patience, wearing his shape. Pantera's answer: then I can finally wrestle it. Come here.

He walks out unchanged. The trial used him as its standard — and he set it.

## The flow, and why it fits Pantera

**Urban Reign story flow, picked for him:** the MISSION structure (a stage = a mission with waves → boss; retry on fail) + the PARTNER-earned-by-beating rule + partner commands. Why it fits HIM, specifically:

- He's a pro wrestler. A mission is a **CARD** (a night's card of opponents), the partner is his **CORNER**, the double-team is a **TAG**. Wrestling is built on cards, corners, and tags — UR's mission+partner structure translates 1:1 into wrestling language without inventing canon.
- His canon respect rule — "respects only those who refuse to stay down" — **IS** the UR partner rule (you earn a partner by beating them; the one who wouldn't stay down walks with you). Sources: UR manual p.34 / HG101 — "to gain an AI companion, you must first defeat them" (TEARDOWN-PART-C-URBAN-REIGN.md §2.5).
- He's the standard the others are measured against — UR's mission structure measures you mission by mission with ranks (S/A/B/C). That is "the standard" made playable.
- His element is Fire / Plains of Chi-U and his style is grappling. UR's feel (3-press string with third hit juggling, dodge-timing instead of block, direction = body region, SPA meter) is a brawler's feel — and Pantera is a brawler-grappler, not a zoner.
- Redux craft: grounded idles (foot-ground — planted feet for holds), HD textures, expanded stage selection, Challenge mode (wave survival) as the shape of his Furnace (spawn loop at max pressure).

What was **NOT** transferred: the 100-mission Green Harbor story, Brad Hawk, Shun Ying Lee, the gang plot. That is Namco's story, not a system — only the structure came over.

**Devil Within mix:** the descent's skeleton (5 stages, waves → boss, Nine-Soul Meter as the gauge, soul embers, ranks) is the shared HeartMind frame; Pantera's own DW donors are recorded in the flow data (see below). The Warden kit, the brute archetype, the boss bodies, and the Surge Form donors are all decoded-file records, not invented numbers.

## What was built (code)

| File | Change |
|---|---|
| `game/js/heartmind-flows.js` **(new)** | Dependency-free per-character flow module (same pattern as `heartmind-campaign.js`): `PANTERA_FLOW` (stages, wave tables, echo pool, partner rule, DW donors) + `HEARTMIND_CHARACTER_FLOWS` + `FIGHTER_SOUL` (vessel → soul map) + `getHeartmindFlow(fighterId)`. |
| `game/js/heartmind.js` | Import flows; Pantera's full story in `HEARTMIND_STORIES` (`PANTERA 闘 — DESCENT OF THE HOLD`); `getHeartmindStory` now falls back fighter → soul's `nineStory` → generic (the nine-soul stories were unreachable by fighter id before — `tou`'s story existed but no fighter could reach it); controller uses the flow's stages/echoIds/waveTables when present; `onBossIntro` plays `story.bossIntros[stageKey]`; `onStageClear` joins the corner partner when `flow.partnerAfter === st.key`. |
| `game/js/brawler.js` | Two minimal backwards-compatible seams: `_layoutZones` prefers `content.waveTables[st.key]`; `_buildCast` draws ONLY from `content.echoIds` when present (no fallback to the full roster). |
| `game/tests/pantera-heartmind.test.mjs` **(new)** | 12 tests: flow shape, stage keys/order, wave-table validity, gunner-only-at-Furnace, echo pool = real roster ids, partner rule, DW donor filenames/frames, canon-law word checks (no Devil / Jin / source names / bare Ogre in Pantera's text; the unassigned chapter title absent), seam presence in both files. **12/12 green.** |

**The template for the next character:** same shape — their own stages (same five keys), their own echo pool from their canon relationships, their own wave tables, their own partner rule, their own DW donors, their own story entry + boss intros + partner beat. Add one entry to `HEARTMIND_CHARACTER_FLOWS`, one to `FIGHTER_SOUL`, one story in `HEARTMIND_STORIES`. Nothing else changes.

## Pantera's flow data (measured, not guessed)

- **Stages:** same five keys/names/arenas as the shared flow (those names are CONFIRMED canon — not changed). His own subs + tuning: diff 0.50 / 0.58 / 0.68 / 0.78 / 0.90 (a step above the shared flow at every stage — the trial tests the standard harder), restore 0.30 / 0.30 / 0.32 / 0.32 / 0.35.
- **Echo pool:** `demonio`, `diablo`, `samura1` — his canon relationships (CANON.md PANTERA): Demonio is the only soul who meets him head-on every time (mutual respect, no warmth); Diablo he dismisses as a pretender; SAM-UR-A1 he is curious about. All three verified as real roster ids.
- **Wave tables:** brute-heavy — his descent is holds, not gunfire. Gunners appear only at the Furnace, where the trial escalates. Bosses are the shared kinds (warden / masks / ogre / sphere / shadow) — their names are CONFIRMED and do not change.
- **Corner partner:** Demonio joins after the Masks (stage 2). Added to the party in place; the player may switch to him between fights, never mid-fight (campaign rule, unchanged).
- **DW donors (all measured — `dw-motion-index.json` + `dw_measurements.json`):**
  - Surge Form throws — `gym_ikdv_36_nage_f.dat` 120f, `gym_ikdv_36_nage_y.dat` 126f, `gym_ikdv_b_nage_f.dat` 170f SPARSE, `gym_ikdv_b_nage_y.dat` 170f SPARSE, `gym_ikdv_ppp_nage_f.dat` 92f, `gym_ikdv_ppp_nage_y.dat` 92f (all 35 bones). Canon name "Surge Kit — throw, …" is PROVISIONAL (rename map §1). **Pilot status (PR #1652):** the 36 pair is wired as Surge Form front throws (1+3 / 2+4), retarget function verified by direct test — pair-binding live re-check owed. The b / ppp pairs are baked as data, mapping owed, not guessed.
  - Surge Form transform — `gym_djin_newhane00.dat` 1f, `01` 13f, `02` 13f, `03` 25f (12 bones each). Canon name "Soul Surge Bloom" is PROVISIONAL.
  - Surge trigger — `gym_dwup00.dat` 60f, 27 bones. Surge beam — `gym_dwhadoh00.dat` 45f, 27 bones; its name is PROPOSED "Soul Beam" (Jay call #6) and is NOT used in code. **Pilot status (PR #1652):** both are wired and watched playing in-game (beam: coherent crouch-gather-rise; trigger: the source clip is a big leap — hips to 2.375 m — so it reads as a launch, not a grounded power-up; the clip choice for the trigger role is the open item, not the retarget).
  - Warden kit — `kmb1`, 39 clips, 3,186 frames, 53.1 s at 60 fps.
  - Brute archetype — `gym_init_obj_mon_power1.dat`, `mon_power2.dat` (1-frame, 78-bone spawn poses — archetype donor only, not motion).
  - Boss bodies (bone counts measured) — Warden `gym_init_obj_boss1.dat` 78, Masks `boss2` 78, Drowned Ogre `boss3` 111, Shadow/Unmasked `boss5` 111. **boss4 does not exist — the sphere needs no body, and that absence IS the design.**
  - Stage map objects — `moj_stg00` 29 NUDP models, `moj_stg01` 18, `moj_stg02` 20, `moj_stg04` 3. These are geometry, NOT text. Which one feeds which inner room is **UNMEASURED** (NUDP/MIF parse pending).
  - Music — `snd_bg_lab` (Threshold), `snd_bg_egy` (Drowning), `snd_bg_blu` + `snd_boss_last` (Still Point). Stages 2 and 4 have no DW theme — UNMEASURED.

## Canon sources per choice

| Choice | Source |
|---|---|
| Pantera = vessel of TOU, Fire, Plains of Chi-U | CANON.md "PANTERA — The Panther Soul"; NINE-SOULS-CANON.md TOU row (blood reds, scorched oranges) |
| "The hold is honest"; respects only those who refuse to stay down; ring introductions are silence; "The mat is here. I am here." | CANON.md PANTERA |
| Being purified of: Nothing; the trial uses him as the standard | CANON.md PANTERA |
| If he knew something was watching, he'd want to wrestle it | CANON.md PANTERA ("Why Pantera thinks he's here") |
| Demonio meets him head-on (mutual respect, no warmth); Diablo a pretender; curious about SAM-UR-A1 | CANON.md PANTERA Relationships |
| Five inner rooms, boss kinds, Nine-Soul Meter, embers, ranks | Shared HeartMind (`heartmind.js` / `brawler.js`); rename map §4 CONFIRMED |
| Mission + partner structure, partner earned by beating | UR Story Mode (TEARDOWN-PART-C §2.1/§2.5; manual p.34 / HG101) |
| Grounded idles, Challenge mode shape | Redux craft (Part C §3) |
| DW donor files + frame/bone counts | `dw-motion-index.json`, `dw_measurements.json`, DW-DECODE-LOG.md |
| Canon names for donors (PROVISIONAL) | HEARTMIND-RENAME-MAP.md §1/§4 |
| No "Devil" in Pantera's text; "Jin" only the soul | Revised Law 1 (Jay 2026-11-07 ~22:32, criterion ~22:43); "The Devil That Stays..." unassigned |

## What waits on decoded contents

- **Gym keyframe-stream decode — DONE, and the pilot IS wired.** The keyframe stream is decoded (`dw-motion-curves.json`, 9,002 keyframes, commit `1beffd18`); the rotation convention is cracked (R = Rz·Ry·Rx, LOCAL) and the FK model is exact (RMS 0.108 mm). **Retarget pilot DONE 2026-11-08 (PR #1652, branch `retarget-dw-curves`, OPEN + MERGEABLE, all 6 checks green):** Pantera's Surge Form beam (`dwhadoh00`) + trigger (`dwup00`) watched playing in-game; the two front throws (`ikdv_36_nage_f` / `ikdv_36_nage_y`, moves 1+3 / 2+4) verified by direct test — the throw pair-binding live re-check is owed. The other 4 nage clips are baked as data, mapping owed, not guessed. The `HM_TEARDOWN` seam still waits on the remaining 178 clips + the Warden kit.
- **TK5DATA0/1 numbers** — meter fill rates, gem heal/drop values, Force values, rank thresholds, symbol locations. The flow uses the built values (restore 0.30–0.35, embers 22 HP / 35%) until the real numbers land.
- **NUDP/MIF stage-geometry parse** — which `moj_stg` feeds which inner room; the stage-map donors are listed as UNMEASURED.
- **P3Dp audio decode** — the music/voice file refs (`snd_bg_lab`, `snd_c21jac`, …) are donor records; no audio is wired.
- **Region damage** — rename map marks it CONFIRMED, but the code has flat damage (`brawler.js:950`) — unresolved, not claimed as done.

## What waits on Jay

- **The 15 rename Jay-calls** (HEARTMIND-JAY-CALLS.md) — nearest to this build: **#5 Twin Strike** (the double-team command name — the partner join uses the existing party system only; no Twin Strike is wired), **#6 "Soul Beam"** (name for `dwhadoh00`), **#13 whether DW Force = Force Claiming**.
- **"The Devil That Stays..."** — allowed under the revised law, **character still unassigned**. It is NOT in Pantera's story. If Jay says it is Pantera's, it becomes his chapter title in a follow-up.
- **True Tekken throw range** (Break 5d — the +0.2 m judgment call) and the other standing calls (ZEN bank, TOU fallback, BF fighter colors) — unchanged, owed elsewhere.
- **Live playthrough proof** — no browser run by this lane (parent re-tests): Pantera's full descent, phone-size, video.

## Tests

- New suite `game/tests/pantera-heartmind.test.mjs`: **12/12 pass** (node --test, in the fix clone).
- Full `game/tests/` suite, same clone: **clean tree 288 tests / 237 pass / 51 fail; with this lane 300 tests / 249 pass / 51 fail — the failing file list is IDENTICAL. +12 tests, +12 pass, zero new failures, zero regressions.** (The 51 pre-existing failures include `heartmind-campaign.test.mjs` and `brawler-sim.test.mjs`; the Lane 3 "242/48" baseline was a different checkout scope.)
