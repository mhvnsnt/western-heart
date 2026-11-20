# HeartMind rename + mix map — Devil Within × Urban Reign × Redux → Western Heart canon

**Date:** 2026-11-08
**Repo:** `mhvnsnt/western-heart`, HEAD `3334ebf`
**Ordered by Jay:** 2026-11-07 ~20:16 — look at ALL the Devil Within files, ALL the Urban Reign files, ALL the Redux files, and ALL our canon, and map how everything gets renamed to fit Western Heart's proprietary canon and universe, and how the three sources mix together.
**This is a MAP, not a code change.** Nothing in the game code gets renamed by this pass. The program coordinator applies it.
**Names:** Pantera is male (he/him). Every other fighter is named only, no guessed pronouns.

**CORRECTION 2026-11-08 ~00:04 (Jay — supersedes the "Jin ×5" framing in §5): there is NO Jin Kazama in our game at all — no Jin Kazama character, no bloodline Jin. The ONLY Jin is the soul JIN (刃, the Blade Soul), pickable as Phantom. The Devil Jin kit is moveset donor data only, never a character; the Redux Jin guest is a template donor only, never a character. Rows below that treat Jin Kazama / the bloodline Jin as characters are superseded — the map's Jin proposals collapse to the soul only. Devil criterion (Jay ~22:43): SOURCE, not spelling — DIABLO / "The Devil Soul" is Jay's own way, lawful. Law 2 in CANON.md states this directly (PR #1648, commit f537e170).**

## Status words (used on every row)

- **CONFIRMED** — the canon / Western Heart name already exists in code or in a canon doc. The mapping is a fact.
- **PROVISIONAL** — derived from the DW index gloss (romaji translation of a file name). The name is a working label until the archive-pull decode lands the file contents, then it is confirmed or corrected.
- **PROPOSED** — a new name suggested here. It is NOT canon. Jay calls it.
- **UNMEASURED** — no target known. No name is assigned; the row says what would unblock it.

## Counts

| Source | Mapped | CONFIRMED | PROVISIONAL | UNMEASURED |
|---|---|---|---|---|
| Devil Within files (dw-motion-index.json, 242) | 242 | 14 | 180 | 48 |
| Urban Reign groups (teardown/urban-reign, ~95%) | 22 groups (~4,400 files/items — see §2) | 6 | 12 | 4 |
| Redux groups (Mod Manager + Editor, on disk) | 20 groups (1,152 files) | 5 | 14 | 1 |

## §0 — Canon name authority (where a HeartMind name is allowed to come from)

In priority order. A name may only come from a higher source; a lower source never overrides a higher one.

1. **Existing HeartMind code** (`game/js/heartmind.js`, `brawler.js`, `heartmind-campaign.js`): THE THRESHOLD, THE GALLERY OF MASKS, THE DROWNING ROOM, THE FURNACE, THE STILL POINT; WARDEN OF THE THRESHOLD, THE MASKS, THE DROWNED OGRE, THE SOUL SPHERE, SHADOW SELF → THE UNMASKED; Nine-Soul Meter, Soul Surge Form, soul embers, ranks S/A/B/C; Shrine体系 terminal; echoes; the roads between stages.
2. **Canon docs** (`CANON.md`, `ROSTER.md`, `DESIGN.md`, `docs/souls/`): the nine souls + kanji + natures + vessels + stands; the five lands (Tree of Life / Ming-ken — Wood; Plains of Chi-U — Fire; Octagonal Shrine Par-fang — Earth; Helix Palace — Metal; Palace of Dreaming — Water); the Phantom Marketplace; the Trader; the Central Mountain; the Eyeball Mountains; Tong-Nou the Purifier; the Katana of Five Forces; Reincarnation; Force Claiming.
3. **Measured source behaviour** (Part B §2 for Devil Within, Part C §2 for Urban Reign): structure and mechanics, renamed by rule 1–2, never by keeping the source's proper nouns.
4. **PROPOSED names (this map)** — flagged PROPOSED, for Jay's call only.

**The rename rules that follow from the above:**
- Devil Within's *places* are dropped (G Corp lab, medical wing, ruins, spaceship) — HeartMind's stages are canon lands. Only the *structure* (5 stages, waves → boss, 1-then-3 trick, orb boss, two-form final) carries over.
- Devil Within's *people* are dropped (Jin Kazama, Heihachi clones, Gun Jack, Ogre) — the bosses are canon analogs already in code (WARDEN, MASKS, DROWNED OGRE, SOUL SPHERE, UNMASKED). Jin Kazama has NO HeartMind target at all: in WH canon, Jin Kazama's data is Demonio, RIN's vessel.
- Urban Reign's *story and people* are dropped (Brad Hawk, Green Harbor, the gangs) — only the *systems* carry over (3-press string, dodge-timing, SPA shape, partners, region damage, Free Mode, missions-as-structure).
- Redux's *guest characters* keep their own names as **template names** (the template-library lane decision: templates are named after the character they came from) — they do NOT become WH canon fighters. In canon terms they are Strays (PROPOSED category, §5.8).
- The word "Devil" never appears in a HeartMind name. Devil Gene → Nine-Soul Meter. Devil Jin → Soul Surge Form. Devil Symbols → Soul Seals (PROPOSED).

---

## §1 — Devil Within files → canon name → HeartMind role

Source: `dw-motion-index.json` (242 files, index level only — names + romaji glosses, no contents yet; the archive-pull decode is running under another agent). Group→boss/kit mappings are CONFIRMED by the existing code (`brawler.js` header, Part B §4 mapping table). Per-file glosses are PROVISIONAL until contents land.

| DW file | Gloss (index) | Canon name in HeartMind | Role | Status |
|---|---|---|---|---|
| **GROUP ikdv** (52 files — Devil Jin's Devil Within moveset) | | | | |
| `gym_ikdv_36_nage_f.dat` | throw, variant 36, _f variant | Surge Kit — throw, variant 36, _f variant | Soul Surge Form move donor (Devil Jin DW kit, any fighter) | PROVISIONAL |
| `gym_ikdv_36_nage_y.dat` | throw, variant 36, _y variant | Surge Kit — throw, variant 36, _y variant | Soul Surge Form move donor (Devil Jin DW kit, any fighter) | PROVISIONAL |
| `gym_ikdv_all_beam.dat` | beam hitting all targets | Surge Kit — beam hitting all targets | Soul Surge Form move donor (Devil Jin DW kit, any fighter) | PROVISIONAL |
| `gym_ikdv_b_nage_f.dat` | throw, variant b, _f variant | Surge Kit — throw, variant b, _f variant | Soul Surge Form move donor (Devil Jin DW kit, any fighter) | PROVISIONAL |
| `gym_ikdv_b_nage_y.dat` | throw, variant b, _y variant | Surge Kit — throw, variant b, _y variant | Soul Surge Form move donor (Devil Jin DW kit, any fighter) | PROVISIONAL |
| `gym_ikdv_beam.dat` | beam / laser | Surge Kit — beam / laser | Soul Surge Form move donor (Devil Jin DW kit, any fighter) | PROVISIONAL |
| `gym_ikdv_chaku.dat` | landing | Surge Kit — landing | Soul Surge Form move donor (Devil Jin DW kit, any fighter) | PROVISIONAL |
| `gym_ikdv_d_beam.dat` | devil beam | Surge Kit — devil beam | Soul Surge Form move donor (Devil Jin DW kit, any fighter) | PROVISIONAL |
| `gym_ikdv_d_jump_k.dat` | devil jump kick | Surge Kit — devil jump kick | Soul Surge Form move donor (Devil Jin DW kit, any fighter) | PROVISIONAL |
| `gym_ikdv_d_jump_p.dat` | devil jump punch | Surge Kit — devil jump punch | Soul Surge Form move donor (Devil Jin DW kit, any fighter) | PROVISIONAL |
| `gym_ikdv_d_nagi_beam.dat` | devil sweeping beam | Surge Kit — devil sweeping beam | Soul Surge Form move donor (Devil Jin DW kit, any fighter) | PROVISIONAL |
| `gym_ikdv_dsrp.dat` | opaque token | Surge Kit — opaque token, no gloss | Soul Surge Form move donor (Devil Jin DW kit, any fighter) | UNMEASURED |
| `gym_ikdv_dsrp_k.dat` | opaque token, kick variant | Surge Kit — opaque token, no gloss | Soul Surge Form move donor (Devil Jin DW kit, any fighter) | UNMEASURED |
| `gym_ikdv_dv2kam2.dat` | opaque token | Surge Kit — opaque token, no gloss | Soul Surge Form move donor (Devil Jin DW kit, any fighter) | UNMEASURED |
| `gym_ikdv_dv_jz.dat` | opaque token | Surge Kit — opaque token, no gloss | Soul Surge Form move donor (Devil Jin DW kit, any fighter) | UNMEASURED |
| `gym_ikdv_fstep.dat` | forward step | Surge Kit — forward step | Soul Surge Form move donor (Devil Jin DW kit, any fighter) | PROVISIONAL |
| `gym_ikdv_jump_beam.dat` | jumping beam | Surge Kit — jumping beam | Soul Surge Form move donor (Devil Jin DW kit, any fighter) | PROVISIONAL |
| `gym_ikdv_jump_k.dat` | jumping kick | Surge Kit — jumping kick | Soul Surge Form move donor (Devil Jin DW kit, any fighter) | PROVISIONAL |
| `gym_ikdv_jump_p.dat` | jumping punch | Surge Kit — jumping punch | Soul Surge Form move donor (Devil Jin DW kit, any fighter) | PROVISIONAL |
| `gym_ikdv_jz_dv.dat` | opaque token | Surge Kit — opaque token, no gloss | Soul Surge Form move donor (Devil Jin DW kit, any fighter) | UNMEASURED |
| `gym_ikdv_k_1.dat` | kick variant 1 | Surge Kit — kick variant 1 | Soul Surge Form move donor (Devil Jin DW kit, any fighter) | PROVISIONAL |
| `gym_ikdv_k_2.dat` | kick variant 2 | Surge Kit — kick variant 2 | Soul Surge Form move donor (Devil Jin DW kit, any fighter) | PROVISIONAL |
| `gym_ikdv_k_3.dat` | kick variant 3 | Surge Kit — kick variant 3 | Soul Surge Form move donor (Devil Jin DW kit, any fighter) | PROVISIONAL |
| `gym_ikdv_k_4.dat` | kick variant 4 | Surge Kit — kick variant 4 | Soul Surge Form move donor (Devil Jin DW kit, any fighter) | PROVISIONAL |
| `gym_ikdv_l2idou.dat` | left movement | Surge Kit — left movement | Soul Surge Form move donor (Devil Jin DW kit, any fighter) | PROVISIONAL |
| `gym_ikdv_lturn.dat` | left turn | Surge Kit — left turn | Soul Surge Form move donor (Devil Jin DW kit, any fighter) | PROVISIONAL |
| `gym_ikdv_lturn90.dat` | left turn 90 degrees | Surge Kit — left turn 90 degrees | Soul Surge Form move donor (Devil Jin DW kit, any fighter) | PROVISIONAL |
| `gym_ikdv_lukemi.dat` | left breakfall | Surge Kit — left breakfall | Soul Surge Form move donor (Devil Jin DW kit, any fighter) | PROVISIONAL |
| `gym_ikdv_nara.dat` | opaque token | Surge Kit — opaque token, no gloss | Soul Surge Form move donor (Devil Jin DW kit, any fighter) | UNMEASURED |
| `gym_ikdv_nige00.dat` | escape / flee | Surge Kit — escape / flee | Soul Surge Form move donor (Devil Jin DW kit, any fighter) | PROVISIONAL |
| `gym_ikdv_p_1.dat` | punch variant 1 | Surge Kit — punch variant 1 | Soul Surge Form move donor (Devil Jin DW kit, any fighter) | PROVISIONAL |
| `gym_ikdv_p_2.dat` | punch variant 2 | Surge Kit — punch variant 2 | Soul Surge Form move donor (Devil Jin DW kit, any fighter) | PROVISIONAL |
| `gym_ikdv_p_3.dat` | punch variant 3 | Surge Kit — punch variant 3 | Soul Surge Form move donor (Devil Jin DW kit, any fighter) | PROVISIONAL |
| `gym_ikdv_p_4.dat` | punch variant 4 | Surge Kit — punch variant 4 | Soul Surge Form move donor (Devil Jin DW kit, any fighter) | PROVISIONAL |
| `gym_ikdv_p_5.dat` | punch variant 5 | Surge Kit — punch variant 5 | Soul Surge Form move donor (Devil Jin DW kit, any fighter) | PROVISIONAL |
| `gym_ikdv_p_kaitenk.dat` | punch into spinning kick | Surge Kit — punch into spinning kick | Soul Surge Form move donor (Devil Jin DW kit, any fighter) | PROVISIONAL |
| `gym_ikdv_pk.dat` | punch-kick combo | Surge Kit — punch-kick combo | Soul Surge Form move donor (Devil Jin DW kit, any fighter) | PROVISIONAL |
| `gym_ikdv_ppk.dat` | punch-punch-kick combo | Surge Kit — punch-punch-kick combo | Soul Surge Form move donor (Devil Jin DW kit, any fighter) | PROVISIONAL |
| `gym_ikdv_ppp_nage_f.dat` | 3-punch combo into throw, _f variant | Surge Kit — 3-punch combo into throw, _f variant | Soul Surge Form move donor (Devil Jin DW kit, any fighter) | PROVISIONAL |
| `gym_ikdv_ppp_nage_y.dat` | 3-punch combo into throw, _y variant | Surge Kit — 3-punch combo into throw, _y variant | Soul Surge Form move donor (Devil Jin DW kit, any fighter) | PROVISIONAL |
| `gym_ikdv_r2idou.dat` | right movement | Surge Kit — right movement | Soul Surge Form move donor (Devil Jin DW kit, any fighter) | PROVISIONAL |
| `gym_ikdv_rturn.dat` | right turn | Surge Kit — right turn | Soul Surge Form move donor (Devil Jin DW kit, any fighter) | PROVISIONAL |
| `gym_ikdv_rturn90.dat` | right turn 90 degrees | Surge Kit — right turn 90 degrees | Soul Surge Form move donor (Devil Jin DW kit, any fighter) | PROVISIONAL |
| `gym_ikdv_rukemi.dat` | right breakfall | Surge Kit — right breakfall | Soul Surge Form move donor (Devil Jin DW kit, any fighter) | PROVISIONAL |
| `gym_ikdv_run_p.dat` | running punch | Surge Kit — running punch | Soul Surge Form move donor (Devil Jin DW kit, any fighter) | PROVISIONAL |
| `gym_ikdv_shoryu.dat` | rising dragon uppercut | Surge Kit — rising dragon uppercut | Soul Surge Form move donor (Devil Jin DW kit, any fighter) | PROVISIONAL |
| `gym_ikdv_sjk.dat` | opaque token | Surge Kit — opaque token, no gloss | Soul Surge Form move donor (Devil Jin DW kit, any fighter) | UNMEASURED |
| `gym_ikdv_sjk00.dat` | opaque token, variant 00 | Surge Kit — opaque token, no gloss | Soul Surge Form move donor (Devil Jin DW kit, any fighter) | UNMEASURED |
| `gym_ikdv_sjk01.dat` | opaque token, variant 01 | Surge Kit — opaque token, no gloss | Soul Surge Form move donor (Devil Jin DW kit, any fighter) | UNMEASURED |
| `gym_ikdv_sjk02.dat` | opaque token, variant 02 | Surge Kit — opaque token, no gloss | Soul Surge Form move donor (Devil Jin DW kit, any fighter) | UNMEASURED |
| `gym_ikdv_sjk03.dat` | opaque token, variant 03 | Surge Kit — opaque token, no gloss | Soul Surge Form move donor (Devil Jin DW kit, any fighter) | UNMEASURED |
| `gym_ikdv_sway.dat` | sway | Surge Kit — sway | Soul Surge Form move donor (Devil Jin DW kit, any fighter) | PROVISIONAL |
| **GROUP kmb1** (39 files — Modified Gun Jack (Devil Within stage 1 boss)) | | | | |
| `gym_kmb1_bakutyu.dat` | explosion-type attack | Warden Kit — explosion-type attack | WARDEN OF THE THRESHOLD move donor | PROVISIONAL |
| `gym_kmb1_bakutyushot.dat` | explosion shot | Warden Kit — explosion shot | WARDEN OF THE THRESHOLD move donor | PROVISIONAL |
| `gym_kmb1_charge_shot_02.dat` | charged shot, variant 2 | Warden Kit — charged shot, variant 2 | WARDEN OF THE THRESHOLD move donor | PROVISIONAL |
| `gym_kmb1_guard_mm.dat` | guard | Warden Kit — guard | WARDEN OF THE THRESHOLD move donor | PROVISIONAL |
| `gym_kmb1_hijump_shot.dat` | high-jump shot | Warden Kit — high-jump shot | WARDEN OF THE THRESHOLD move donor | PROVISIONAL |
| `gym_kmb1_histep_l.dat` | high step, left | Warden Kit — high step, left | WARDEN OF THE THRESHOLD move donor | PROVISIONAL |
| `gym_kmb1_histep_r.dat` | high step, right | Warden Kit — high step, right | WARDEN OF THE THRESHOLD move donor | PROVISIONAL |
| `gym_kmb1_jumpmachinegun.dat` | jumping machine gun | Warden Kit — jumping machine gun | WARDEN OF THE THRESHOLD move donor | PROVISIONAL |
| `gym_kmb1_kamae.dat` | stance | Warden Kit — stance | WARDEN OF THE THRESHOLD move donor | PROVISIONAL |
| `gym_kmb1_lk.dat` | left kick | Warden Kit — left kick | WARDEN OF THE THRESHOLD move donor | PROVISIONAL |
| `gym_kmb1_lk_histep_r.dat` | left kick into right high step | Warden Kit — left kick into right high step | WARDEN OF THE THRESHOLD move donor | PROVISIONAL |
| `gym_kmb1_lturn180.dat` | left turn 180 degrees | Warden Kit — left turn 180 degrees | WARDEN OF THE THRESHOLD move donor | PROVISIONAL |
| `gym_kmb1_lturn90.dat` | left turn 90 degrees | Warden Kit — left turn 90 degrees | WARDEN OF THE THRESHOLD move donor | PROVISIONAL |
| `gym_kmb1_machinegun.dat` | machine gun | Warden Kit — machine gun | WARDEN OF THE THRESHOLD move donor | PROVISIONAL |
| `gym_kmb1_machinegun_f.dat` | machine gun, _f variant | Warden Kit — machine gun, _f variant | WARDEN OF THE THRESHOLD move donor | PROVISIONAL |
| `gym_kmb1_rk.dat` | right kick | Warden Kit — right kick | WARDEN OF THE THRESHOLD move donor | PROVISIONAL |
| `gym_kmb1_rk_histep_l.dat` | right kick into left high step | Warden Kit — right kick into left high step | WARDEN OF THE THRESHOLD move donor | PROVISIONAL |
| `gym_kmb1_rturn180.dat` | right turn 180 degrees | Warden Kit — right turn 180 degrees | WARDEN OF THE THRESHOLD move donor | PROVISIONAL |
| `gym_kmb1_rturn90.dat` | right turn 90 degrees | Warden Kit — right turn 90 degrees | WARDEN OF THE THRESHOLD move donor | PROVISIONAL |
| `gym_kmb1_run01_start.dat` | run cycle, start | Warden Kit — run cycle, start | WARDEN OF THE THRESHOLD move donor | PROVISIONAL |
| `gym_kmb1_run02_loop.dat` | run cycle, loop | Warden Kit — run cycle, loop | WARDEN OF THE THRESHOLD move donor | PROVISIONAL |
| `gym_kmb1_run03_walk.dat` | run cycle, walk | Warden Kit — run cycle, walk | WARDEN OF THE THRESHOLD move donor | PROVISIONAL |
| `gym_kmb1_shortshot_shot.dat` | short shot, shot | Warden Kit — short shot, shot | WARDEN OF THE THRESHOLD move donor | PROVISIONAL |
| `gym_kmb1_shortshot_soten.dat` | short shot, soten variant | Warden Kit — short shot, soten variant | WARDEN OF THE THRESHOLD move donor | PROVISIONAL |
| `gym_kmb1_shotgun_cyop.dat` | shotgun, cyop variant | Warden Kit — shotgun, cyop variant | WARDEN OF THE THRESHOLD move donor | PROVISIONAL |
| `gym_kmb1_shotgun_shot.dat` | shotgun shot | Warden Kit — shotgun shot | WARDEN OF THE THRESHOLD move donor | PROVISIONAL |
| `gym_kmb1_shotgun_soten.dat` | shotgun, soten variant | Warden Kit — shotgun, soten variant | WARDEN OF THE THRESHOLD move donor | PROVISIONAL |
| `gym_kmb1_step_in.dat` | step in | Warden Kit — step in | WARDEN OF THE THRESHOLD move donor | PROVISIONAL |
| `gym_kmb1_step_l.dat` | step left | Warden Kit — step left | WARDEN OF THE THRESHOLD move donor | PROVISIONAL |
| `gym_kmb1_step_r.dat` | step right | Warden Kit — step right | WARDEN OF THE THRESHOLD move donor | PROVISIONAL |
| `gym_kmb1_tojo.dat` | entrance / appearance | Warden Kit — entrance / appearance | WARDEN OF THE THRESHOLD move donor | PROVISIONAL |
| `gym_kmb1_walk_f01_start.dat` | walk forward, start | Warden Kit — walk forward, start | WARDEN OF THE THRESHOLD move donor | PROVISIONAL |
| `gym_kmb1_walk_f02_loop.dat` | walk forward, loop | Warden Kit — walk forward, loop | WARDEN OF THE THRESHOLD move donor | PROVISIONAL |
| `gym_kmb1_walk_l.dat` | walk left | Warden Kit — walk left | WARDEN OF THE THRESHOLD move donor | PROVISIONAL |
| `gym_kmb1_walk_r.dat` | walk right | Warden Kit — walk right | WARDEN OF THE THRESHOLD move donor | PROVISIONAL |
| `gym_kmb1_wdown.dat` | knocked down | Warden Kit — knocked down | WARDEN OF THE THRESHOLD move donor | PROVISIONAL |
| `gym_kmb1_wshot.dat` | weapon shot | Warden Kit — weapon shot | WARDEN OF THE THRESHOLD move donor | PROVISIONAL |
| `gym_kmb1_yoko_l.dat` | side step left | Warden Kit — side step left | WARDEN OF THE THRESHOLD move donor | PROVISIONAL |
| `gym_kmb1_yoko_r.dat` | side step right | Warden Kit — side step right | WARDEN OF THE THRESHOLD move donor | PROVISIONAL |
| **GROUP kob2** (29 files — True Ogre (Devil Within stage 3 boss)) | | | | |
| `gym_kob2_36_nage_f.dat` | throw, variant 36, _f variant | Drowned Ogre Kit — throw, variant 36, _f variant | THE DROWNED OGRE move donor | PROVISIONAL |
| `gym_kob2_36_nage_y.dat` | throw, variant 36, _y variant | Drowned Ogre Kit — throw, variant 36, _y variant | THE DROWNED OGRE move donor | PROVISIONAL |
| `gym_kob2_b_35_nage_f.dat` | throw, variant b-35, _f variant | Drowned Ogre Kit — throw, variant b-35, _f variant | THE DROWNED OGRE move donor | PROVISIONAL |
| `gym_kob2_b_35_nage_y.dat` | throw, variant b-35, _y variant | Drowned Ogre Kit — throw, variant b-35, _y variant | THE DROWNED OGRE move donor | PROVISIONAL |
| `gym_kob2_charge.dat` | charging attack | Drowned Ogre Kit — charging attack | THE DROWNED OGRE move donor | PROVISIONAL |
| `gym_kob2_dash.dat` | dash | Drowned Ogre Kit — dash | THE DROWNED OGRE move donor | PROVISIONAL |
| `gym_kob2_fire.dat` | fire breath / fire attack | Drowned Ogre Kit — fire breath / fire attack | THE DROWNED OGRE move donor | PROVISIONAL |
| `gym_kob2_fire_kyou.dat` | fire attack, variant | Drowned Ogre Kit — fire attack, variant | THE DROWNED OGRE move donor | PROVISIONAL |
| `gym_kob2_jump.dat` | jump | Drowned Ogre Kit — jump | THE DROWNED OGRE move donor | PROVISIONAL |
| `gym_kob2_k_1.dat` | kick variant 1 | Drowned Ogre Kit — kick variant 1 | THE DROWNED OGRE move donor | PROVISIONAL |
| `gym_kob2_k_2.dat` | kick variant 2 | Drowned Ogre Kit — kick variant 2 | THE DROWNED OGRE move donor | PROVISIONAL |
| `gym_kob2_k_3.dat` | kick variant 3 | Drowned Ogre Kit — kick variant 3 | THE DROWNED OGRE move donor | PROVISIONAL |
| `gym_kob2_k_4.dat` | kick variant 4 | Drowned Ogre Kit — kick variant 4 | THE DROWNED OGRE move donor | PROVISIONAL |
| `gym_kob2_landing.dat` | landing | Drowned Ogre Kit — landing | THE DROWNED OGRE move donor | PROVISIONAL |
| `gym_kob2_left_hand.dat` | left hand attack | Drowned Ogre Kit — left hand attack | THE DROWNED OGRE move donor | PROVISIONAL |
| `gym_kob2_p_1.dat` | punch variant 1 | Drowned Ogre Kit — punch variant 1 | THE DROWNED OGRE move donor | PROVISIONAL |
| `gym_kob2_p_2.dat` | punch variant 2 | Drowned Ogre Kit — punch variant 2 | THE DROWNED OGRE move donor | PROVISIONAL |
| `gym_kob2_p_3.dat` | punch variant 3 | Drowned Ogre Kit — punch variant 3 | THE DROWNED OGRE move donor | PROVISIONAL |
| `gym_kob2_p_4.dat` | punch variant 4 | Drowned Ogre Kit — punch variant 4 | THE DROWNED OGRE move donor | PROVISIONAL |
| `gym_kob2_p_5.dat` | punch variant 5 | Drowned Ogre Kit — punch variant 5 | THE DROWNED OGRE move donor | PROVISIONAL |
| `gym_kob2_ppp_nage_f.dat` | 3-punch combo into throw, _f variant | Drowned Ogre Kit — 3-punch combo into throw, _f variant | THE DROWNED OGRE move donor | PROVISIONAL |
| `gym_kob2_ppp_nage_y.dat` | 3-punch combo into throw, _y variant | Drowned Ogre Kit — 3-punch combo into throw, _y variant | THE DROWNED OGRE move donor | PROVISIONAL |
| `gym_kob2_psk.dat` | opaque token | Drowned Ogre Kit — opaque token, no gloss | THE DROWNED OGRE move donor | UNMEASURED |
| `gym_kob2_psk2.dat` | opaque token, variant 2 | Drowned Ogre Kit — opaque token, no gloss | THE DROWNED OGRE move donor | UNMEASURED |
| `gym_kob2_rgt_hand.dat` | right hand attack | Drowned Ogre Kit — right hand attack | THE DROWNED OGRE move donor | PROVISIONAL |
| `gym_kob2_shoryu.dat` | rising dragon uppercut | Drowned Ogre Kit — rising dragon uppercut | THE DROWNED OGRE move donor | PROVISIONAL |
| `gym_kob2_wdown.dat` | knocked down | Drowned Ogre Kit — knocked down | THE DROWNED OGRE move donor | PROVISIONAL |
| `gym_kob2_wdown_shot.dat` | knocked down shot | Drowned Ogre Kit — knocked down shot | THE DROWNED OGRE move donor | PROVISIONAL |
| `gym_kob2_zantetsu.dat` | cutting attack | Drowned Ogre Kit — cutting attack | THE DROWNED OGRE move donor | PROVISIONAL |
| **GROUP ozb3** (36 files — Monstrous Ogre (Devil Within stage 4 boss)) | | | | |
| `gym_ozb3_33_nage_f.dat` | throw, variant 33, _f variant | Unmasked Kit — throw, variant 33, _f variant | THE UNMASKED move donor | PROVISIONAL |
| `gym_ozb3_33_nage_y.dat` | throw, variant 33, _y variant | Unmasked Kit — throw, variant 33, _y variant | THE UNMASKED move donor | PROVISIONAL |
| `gym_ozb3_b_31_nage_f.dat` | throw, variant b-31, _f variant | Unmasked Kit — throw, variant b-31, _f variant | THE UNMASKED move donor | PROVISIONAL |
| `gym_ozb3_b_31_nage_y.dat` | throw, variant b-31, _y variant | Unmasked Kit — throw, variant b-31, _y variant | THE UNMASKED move donor | PROVISIONAL |
| `gym_ozb3_charge.dat` | charging attack | Unmasked Kit — charging attack | THE UNMASKED move donor | PROVISIONAL |
| `gym_ozb3_dash.dat` | dash | Unmasked Kit — dash | THE UNMASKED move donor | PROVISIONAL |
| `gym_ozb3_fire.dat` | fire breath / fire attack | Unmasked Kit — fire breath / fire attack | THE UNMASKED move donor | PROVISIONAL |
| `gym_ozb3_fire_kyou.dat` | fire attack, variant | Unmasked Kit — fire attack, variant | THE UNMASKED move donor | PROVISIONAL |
| `gym_ozb3_god_chrg.dat` | opaque token | Unmasked Kit — opaque token, no gloss | THE UNMASKED move donor | UNMEASURED |
| `gym_ozb3_god_dash.dat` | opaque token | Unmasked Kit — opaque token, no gloss | THE UNMASKED move donor | UNMEASURED |
| `gym_ozb3_god_fire.dat` | opaque token | Unmasked Kit — opaque token, no gloss | THE UNMASKED move donor | UNMEASURED |
| `gym_ozb3_god_kick.dat` | opaque token | Unmasked Kit — opaque token, no gloss | THE UNMASKED move donor | UNMEASURED |
| `gym_ozb3_god_punch.dat` | opaque token | Unmasked Kit — opaque token, no gloss | THE UNMASKED move donor | UNMEASURED |
| `gym_ozb3_jump.dat` | jump | Unmasked Kit — jump | THE UNMASKED move donor | PROVISIONAL |
| `gym_ozb3_k_1.dat` | kick variant 1 | Unmasked Kit — kick variant 1 | THE UNMASKED move donor | PROVISIONAL |
| `gym_ozb3_k_2.dat` | kick variant 2 | Unmasked Kit — kick variant 2 | THE UNMASKED move donor | PROVISIONAL |
| `gym_ozb3_k_3.dat` | kick variant 3 | Unmasked Kit — kick variant 3 | THE UNMASKED move donor | PROVISIONAL |
| `gym_ozb3_k_4.dat` | kick variant 4 | Unmasked Kit — kick variant 4 | THE UNMASKED move donor | PROVISIONAL |
| `gym_ozb3_landing.dat` | landing | Unmasked Kit — landing | THE UNMASKED move donor | PROVISIONAL |
| `gym_ozb3_left_hand.dat` | left hand attack | Unmasked Kit — left hand attack | THE UNMASKED move donor | PROVISIONAL |
| `gym_ozb3_p_1.dat` | punch variant 1 | Unmasked Kit — punch variant 1 | THE UNMASKED move donor | PROVISIONAL |
| `gym_ozb3_p_2.dat` | punch variant 2 | Unmasked Kit — punch variant 2 | THE UNMASKED move donor | PROVISIONAL |
| `gym_ozb3_p_3.dat` | punch variant 3 | Unmasked Kit — punch variant 3 | THE UNMASKED move donor | PROVISIONAL |
| `gym_ozb3_p_4.dat` | punch variant 4 | Unmasked Kit — punch variant 4 | THE UNMASKED move donor | PROVISIONAL |
| `gym_ozb3_p_5.dat` | punch variant 5 | Unmasked Kit — punch variant 5 | THE UNMASKED move donor | PROVISIONAL |
| `gym_ozb3_ppp_nage_f.dat` | 3-punch combo into throw, _f variant | Unmasked Kit — 3-punch combo into throw, _f variant | THE UNMASKED move donor | PROVISIONAL |
| `gym_ozb3_ppp_nage_y.dat` | 3-punch combo into throw, _y variant | Unmasked Kit — 3-punch combo into throw, _y variant | THE UNMASKED move donor | PROVISIONAL |
| `gym_ozb3_psk.dat` | opaque token | Unmasked Kit — opaque token, no gloss | THE UNMASKED move donor | UNMEASURED |
| `gym_ozb3_psk2.dat` | opaque token, variant 2 | Unmasked Kit — opaque token, no gloss | THE UNMASKED move donor | UNMEASURED |
| `gym_ozb3_rgt_hand.dat` | right hand attack | Unmasked Kit — right hand attack | THE UNMASKED move donor | PROVISIONAL |
| `gym_ozb3_shoryu.dat` | rising dragon uppercut | Unmasked Kit — rising dragon uppercut | THE UNMASKED move donor | PROVISIONAL |
| `gym_ozb3_wdown.dat` | knocked down | Unmasked Kit — knocked down | THE UNMASKED move donor | PROVISIONAL |
| `gym_ozb3_wdown_shot.dat` | knocked down shot | Unmasked Kit — knocked down shot | THE UNMASKED move donor | PROVISIONAL |
| `gym_ozb3_zantetsu.dat` | cutting attack | Unmasked Kit — cutting attack | THE UNMASKED move donor | PROVISIONAL |
| `gym_ozb3_fire_fly.dat` | flying fire attack | Unmasked Kit — flying fire attack | THE UNMASKED move donor | PROVISIONAL |
| `gym_ozb3_fly.dat` | flying | Unmasked Kit — flying | THE UNMASKED move donor | PROVISIONAL |
| **GROUP oz_extra** (6 files — Monstrous Ogre extras (same rig, source file names only)) | | | | |
| `gym_ozb3_dsrp.dat` | opaque token | Unmasked Kit — opaque token, no gloss | THE UNMASKED move donor (extra slot) | UNMEASURED |
| `gym_ozb3_dsrp_k.dat` | opaque token, kick variant | Unmasked Kit — opaque token, no gloss | THE UNMASKED move donor (extra slot) | UNMEASURED |
| `gym_ozb3_sjk.dat` | opaque token | Unmasked Kit — opaque token, no gloss | THE UNMASKED move donor (extra slot) | UNMEASURED |
| `gym_ozb3_sjk00.dat` | opaque token, variant 00 | Unmasked Kit — opaque token, no gloss | THE UNMASKED move donor (extra slot) | UNMEASURED |
| `gym_ozb3_sjk01.dat` | opaque token, variant 01 | Unmasked Kit — opaque token, no gloss | THE UNMASKED move donor (extra slot) | UNMEASURED |
| `gym_ozb3_sjk02.dat` | opaque token, variant 02 | Unmasked Kit — opaque token, no gloss | THE UNMASKED move donor (extra slot) | UNMEASURED |
| **GROUP ikt5** (26 files — Unresolved ikt5 kit (T5 source files; Devil Within character not assigned)) | | | | |
| `gym_ikt5_36_nage_f.dat` | throw, variant 36, _f variant | unassigned kit — throw, variant 36, _f variant | UNMEASURED — kit owner unknown; do not wire until contents decode | UNMEASURED |
| `gym_ikt5_36_nage_y.dat` | throw, variant 36, _y variant | unassigned kit — throw, variant 36, _y variant | UNMEASURED — kit owner unknown; do not wire until contents decode | UNMEASURED |
| `gym_ikt5_b_nage_f.dat` | throw, variant b, _f variant | unassigned kit — throw, variant b, _f variant | UNMEASURED — kit owner unknown; do not wire until contents decode | UNMEASURED |
| `gym_ikt5_b_nage_y.dat` | throw, variant b, _y variant | unassigned kit — throw, variant b, _y variant | UNMEASURED — kit owner unknown; do not wire until contents decode | UNMEASURED |
| `gym_ikt5_chaku.dat` | landing | unassigned kit — landing | UNMEASURED — kit owner unknown; do not wire until contents decode | UNMEASURED |
| `gym_ikt5_dsrp.dat` | opaque token | unassigned kit — opaque token, no gloss | UNMEASURED — kit owner unknown; do not wire until contents decode | UNMEASURED |
| `gym_ikt5_dsrp_k.dat` | opaque token, kick variant | unassigned kit — opaque token, no gloss | UNMEASURED — kit owner unknown; do not wire until contents decode | UNMEASURED |
| `gym_ikt5_fstep.dat` | forward step | unassigned kit — forward step | UNMEASURED — kit owner unknown; do not wire until contents decode | UNMEASURED |
| `gym_ikt5_jz_dv.dat` | opaque token | unassigned kit — opaque token, no gloss | UNMEASURED — kit owner unknown; do not wire until contents decode | UNMEASURED |
| `gym_ikt5_k_1.dat` | kick variant 1 | unassigned kit — kick variant 1 | UNMEASURED — kit owner unknown; do not wire until contents decode | UNMEASURED |
| `gym_ikt5_k_2.dat` | kick variant 2 | unassigned kit — kick variant 2 | UNMEASURED — kit owner unknown; do not wire until contents decode | UNMEASURED |
| `gym_ikt5_k_3.dat` | kick variant 3 | unassigned kit — kick variant 3 | UNMEASURED — kit owner unknown; do not wire until contents decode | UNMEASURED |
| `gym_ikt5_k_4.dat` | kick variant 4 | unassigned kit — kick variant 4 | UNMEASURED — kit owner unknown; do not wire until contents decode | UNMEASURED |
| `gym_ikt5_l2idou.dat` | left movement | unassigned kit — left movement | UNMEASURED — kit owner unknown; do not wire until contents decode | UNMEASURED |
| `gym_ikt5_lturn.dat` | left turn | unassigned kit — left turn | UNMEASURED — kit owner unknown; do not wire until contents decode | UNMEASURED |
| `gym_ikt5_lturn90.dat` | left turn 90 degrees | unassigned kit — left turn 90 degrees | UNMEASURED — kit owner unknown; do not wire until contents decode | UNMEASURED |
| `gym_ikt5_lukemi.dat` | left breakfall | unassigned kit — left breakfall | UNMEASURED — kit owner unknown; do not wire until contents decode | UNMEASURED |
| `gym_ikt5_nara.dat` | opaque token | unassigned kit — opaque token, no gloss | UNMEASURED — kit owner unknown; do not wire until contents decode | UNMEASURED |
| `gym_ikt5_p_1.dat` | punch variant 1 | unassigned kit — punch variant 1 | UNMEASURED — kit owner unknown; do not wire until contents decode | UNMEASURED |
| `gym_ikt5_p_2.dat` | punch variant 2 | unassigned kit — punch variant 2 | UNMEASURED — kit owner unknown; do not wire until contents decode | UNMEASURED |
| `gym_ikt5_p_3.dat` | punch variant 3 | unassigned kit — punch variant 3 | UNMEASURED — kit owner unknown; do not wire until contents decode | UNMEASURED |
| `gym_ikt5_p_4.dat` | punch variant 4 | unassigned kit — punch variant 4 | UNMEASURED — kit owner unknown; do not wire until contents decode | UNMEASURED |
| `gym_ikt5_p_5.dat` | punch variant 5 | unassigned kit — punch variant 5 | UNMEASURED — kit owner unknown; do not wire until contents decode | UNMEASURED |
| `gym_ikt5_ppp_nage_f.dat` | 3-punch combo into throw, _f variant | unassigned kit — 3-punch combo into throw, _f variant | UNMEASURED — kit owner unknown; do not wire until contents decode | UNMEASURED |
| `gym_ikt5_ppp_nage_y.dat` | 3-punch combo into throw, _y variant | unassigned kit — 3-punch combo into throw, _y variant | UNMEASURED — kit owner unknown; do not wire until contents decode | UNMEASURED |
| `gym_ikt5_sway.dat` | sway | unassigned kit — sway | UNMEASURED — kit owner unknown; do not wire until contents decode | UNMEASURED |
| **GROUP init_obj** (21 files — stage/boss init objects (Devil Within)) | | | | |
| `gym_init_obj_boss1.dat` | stage 1 boss init object | WARDEN OF THE THRESHOLD — body/init | THE THRESHOLD boss body | CONFIRMED |
| `gym_init_obj_boss2.dat` | stage 2 boss init object | THE MASKS — body/init | THE GALLERY OF MASKS boss body | CONFIRMED |
| `gym_init_obj_boss3.dat` | stage 3 boss init object | THE DROWNED OGRE — body/init | THE DROWNING ROOM boss body | CONFIRMED |
| `gym_init_obj_boss5.dat` | stage 5 boss init object | THE UNMASKED — body/init | THE STILL POINT boss body | CONFIRMED |
| `gym_init_obj_mon01.dat` | enemy init object 01 | Wave echo — archetype 01 | Wave enemy donor (any stage) | CONFIRMED |
| `gym_init_obj_mon02.dat` | enemy init object 02 | Wave echo — archetype 02 | Wave enemy donor (any stage) | CONFIRMED |
| `gym_init_obj_mon03.dat` | enemy init object 03 | Wave echo — archetype 03 | Wave enemy donor (any stage) | CONFIRMED |
| `gym_init_obj_mon04.dat` | enemy init object 04 | Wave echo — archetype 04 | Wave enemy donor (any stage) | CONFIRMED |
| `gym_init_obj_mon05.dat` | enemy init object 05 | Wave echo — archetype 05 | Wave enemy donor (any stage) | CONFIRMED |
| `gym_init_obj_mon06.dat` | enemy init object 06 | Wave echo — archetype 06 | Wave enemy donor (any stage) | CONFIRMED |
| `gym_init_obj_tk05.dat` | unknown kit 05 init object | TK-05 kit — unassigned | UNMEASURED — target unknown; do not wire until decode | UNMEASURED |
| `gym_init_obj_tk09.dat` | unknown kit 09 init object | TK-09 kit — unassigned | UNMEASURED — target unknown; do not wire until decode | UNMEASURED |
| `gym_init_obj_tk10.dat` | unknown kit 10 init object | TK-10 kit — unassigned | UNMEASURED — target unknown; do not wire until decode | UNMEASURED |
| `gym_init_obj_tk11.dat` | unknown kit 11 init object | TK-11 kit — unassigned | UNMEASURED — target unknown; do not wire until decode | UNMEASURED |
| `gym_init_obj_tk12.dat` | unknown kit 12 init object | TK-12 kit — unassigned | UNMEASURED — target unknown; do not wire until decode | UNMEASURED |
| `gym_init_obj_tk14.dat` | unknown kit 14 init object | TK-14 kit — unassigned | UNMEASURED — target unknown; do not wire until decode | UNMEASURED |
| `gym_init_obj_tk15.dat` | unknown kit 15 init object | TK-15 kit — unassigned | UNMEASURED — target unknown; do not wire until decode | UNMEASURED |
| `gym_init_obj_tk16.dat` | unknown kit 16 init object | TK-16 kit — unassigned | UNMEASURED — target unknown; do not wire until decode | UNMEASURED |
| `gym_init_obj_tk17.dat` | unknown kit 17 init object | TK-17 kit — unassigned | UNMEASURED — target unknown; do not wire until decode | UNMEASURED |
| `gym_init_obj_tk19.dat` | unknown kit 19 init object | TK-19 kit — unassigned | UNMEASURED — target unknown; do not wire until decode | UNMEASURED |
| `gym_init_obj_tk21.dat` | unknown kit 21 init object | TK-21 kit — unassigned | UNMEASURED — target unknown; do not wire until decode | UNMEASURED |
| **GROUP djin** (4 files — Devil Jin transform / awakening) | | | | |
| `gym_djin_newhane00.dat` | transform, variant 00 | Soul Surge Bloom — variant 00 | Soul Surge Form transformation/awakening data | PROVISIONAL |
| `gym_djin_newhane01.dat` | transform, variant 01 | Soul Surge Bloom — variant 01 | Soul Surge Form transformation/awakening data | PROVISIONAL |
| `gym_djin_newhane02.dat` | transform, variant 02 | Soul Surge Bloom — variant 02 | Soul Surge Form transformation/awakening data | PROVISIONAL |
| `gym_djin_newhane03.dat` | transform, variant 03 | Soul Surge Bloom — variant 03 | Soul Surge Form transformation/awakening data | PROVISIONAL |
| **GROUP dw_singles** (7 files — Devil Within singles) | | | | |
| `gym_dw_init.dat` | Devil Within init | HeartMind init | HeartMind mode init | PROVISIONAL |
| `gym_dw_mon.dat` | Devil Within enemy init | Wave echo — enemy init | Wave enemy donor | PROVISIONAL |
| `gym_dw_mo_shot.dat` | Devil Within enemy shot | Wave echo — ranged attack | Wave enemy ranged attack donor | PROVISIONAL |
| `gym_dw_mon_sj.dat` | Devil Within enemy sj variant | Wave echo — variant | Wave enemy variant donor | PROVISIONAL |
| `gym_dwfkao00.dat` | Devil Within face — placeholder / stub | Face — STUB (no face data in DW index) | Face system STUB; do not wire as a face | PROVISIONAL |
| `gym_dwhadoh00.dat` | Devil Within hadou / wave | Soul Surge Form — PROPOSED "Soul Beam" | Soul Surge Form beam attack (PROPOSED name) | PROVISIONAL |
| `gym_dwup00.dat` | Devil Within up / trigger | Soul Surge Form — trigger | Soul Surge Form activation trigger | PROVISIONAL |
| **GROUP moj_stg** (4 files — stage text (Devil Within)) | | | | |
| `moj_stg00.dat` | stage text 00 | THE THRESHOLD — stage text | Stage intro/lore text, stage 1 | CONFIRMED |
| `moj_stg01.dat` | stage text 01 | THE GALLERY OF MASKS — stage text | Stage intro/lore text, stage 2 | CONFIRMED |
| `moj_stg02.dat` | stage text 02 | THE DROWNING ROOM — stage text | Stage intro/lore text, stage 3 | CONFIRMED |
| `moj_stg04.dat` | stage text 04 | THE STILL POINT — stage text | Stage intro/lore text, stage 5 | CONFIRMED |
| **GROUP snd** (18 files — sound (Devil Within)) | | | | |
| `snd_bg_blu.dat` | background music, blu | THE STILL POINT — stage theme | Stage 5 music donor | PROVISIONAL |
| `snd_bg_egy.dat` | background music, egy | THE DROWNING ROOM — stage theme | Stage 3 music donor | PROVISIONAL |
| `snd_bg_lab.dat` | background music, lab | THE THRESHOLD — stage theme | Stage 1 music donor | PROVISIONAL |
| `snd_boss_all.dat` | boss battle music | Boss theme | Boss battle music donor (any boss) | PROVISIONAL |
| `snd_boss_last.dat` | final boss music | THE UNMASKED — final theme | Final boss music donor | PROVISIONAL |
| `snd_chara_se.dat` | character sound effects | Character SFX pool | Character sound effects donor | PROVISIONAL |
| `snd_c02lei.dat` | Lei Wulong voice | Rave — voice donor | Voice donor for Rave (Lei's WH fighter) | PROVISIONAL |
| `snd_c10jin.dat` | Jin Kazama voice | voice donor only (no WH fighter target) | Voice donor only — Jin Kazama has no WH fighter; do not attach to a fighter | PROVISIONAL |
| `snd_c15hei.dat` | Heihachi voice | THE MASKS — voice donor | Voice donor for THE MASKS (multi-face boss) | PROVISIONAL |
| `snd_c21jac.dat` | JACK voice | WARDEN OF THE THRESHOLD — voice donor | Voice donor for WARDEN (machine boss) | PROVISIONAL |
| `snd_c30dvj.dat` | Devil Jin voice | Soul Surge Form — voice donor | Voice donor for Soul Surge Form | PROVISIONAL |
| `snd_dmg_se.dat` | damage sound effects | Damage SFX pool | Damage sound effects donor | PROVISIONAL |
| `snd_etc_se.dat` | miscellaneous sound effects | Misc SFX pool | Miscellaneous sound effects donor | PROVISIONAL |
| `snd_gym_se.dat` | Devil Within stage SFX | HeartMind stage SFX pool | Stage sound effects donor | PROVISIONAL |
| `snd_last.dat` | final stage sounds | THE STILL POINT — stage sounds | Final stage sounds donor | PROVISIONAL |
| `snd_sys.dat` | system sounds | System SFX pool | System sound effects donor | PROVISIONAL |
| `snd_system_se.dat` | system sound effects | System SFX pool | System sound effects donor | PROVISIONAL |
| `snd_title.dat` | title sounds | Title sounds | Title screen sounds donor | PROVISIONAL |

**DW notes:**
- `moj_stg03` does NOT exist in the index — THE FURNACE (stage 4) has no DW stage-text donor. Furnace text comes from canon, not DW.
- `gym_init_obj_boss4` does NOT exist — the SOUL SPHERE (stage 4 boss) is an orb that spawns monsters; the missing body is itself the design (the sphere needs no body). CONFIRMED as an absence, not a gap to fill.
- `snd_c10jin` (Jin Kazama voice) has no WH fighter target. It is a voice donor only — do NOT attach it to a fighter, and do NOT use it to give Jin Kazama a HeartMind role.
- Only 3 stage background themes exist in the index (`bg_lab`, `bg_egy`, `bg_blu`) for 5 stages. Gallery of Masks (stage 2) and Furnace (stage 4) music comes from UR/Redux donors (§2/§3) or new composition — UNMEASURED until the decode.
- The DW `ikdv` kit (52 files) is the Soul Surge Form's move kit for ANY fighter — it is not a Devil Jin fighter in WH. "Surge Kit" is the working name for the kit, not a character.

---
## §2 — Urban Reign files/groups → canon name → HeartMind role

Source: `teardown/urban-reign/` inventory + `TEARDOWN-PART-C-URBAN-REIGN.md`. **The UR teardown itself is NOT on disk in this workspace — Part C is the source of record.** Figures below are Part C's, not re-measured here. UR contributes SYSTEMS, not story or people: Brad Hawk, Green Harbor, and the gangs do not enter Western Heart.

| UR group | Size (Part C) | Canon name in HeartMind | Role | Status |
|---|---|---|---|---|
| 72 skinned GLBs (char001–072) | 72 files | Wave echo + boss + stand body donors | Body donors for wave enemies, boss bodies, and celestial stands; retargeted onto the WH-Canonical-22 skeleton | PROVISIONAL |
| 72 textured GLBs (char001–072) | 72 files | Same as above — textured pass | Textured versions of the same donors; the textured swap is the named follow-up not yet done (untextured 72 already in `game/`) | PROVISIONAL |
| 285 animation banks / 3,357 motions | 285 banks | Descent move library | Move donors for wave enemies, bosses, and the moveset template library; retargeted per bone map | PROVISIONAL |
| 484 named moves (moveset library) | 484 moves | Descent move library (named) | Named move donors by input + position + situation, feeding the moveset template library | PROVISIONAL |
| 31 movesets already wired into `game/` | 31 files | Wired Descent donors | Already wired; HeartMind uses them as-is through the moveset system | CONFIRMED |
| 7 stage PPKs (geometry NOT decoded) | 7 files | 7 arenas — PROPOSED | Stage-geometry donors for HeartMind's 7 spaces: 5 lands + Phantom Marketplace + Central Mountain. **Place names UNMEASURED** until geometry decodes; the 5 canon lands are the stages, the arenas are their floors | PROVISIONAL |
| 100 mission PPKs (NOT decoded) | 100 files | Trials — PROPOSED | Mission-structure donors for HeartMind trials (wave + objective + boss per trial). Contents UNMEASURED until decode | PROVISIONAL |
| 3-press string (third hit juggles) | mechanic | Descent String — PROPOSED | HeartMind's core string: 3 presses, third hit juggles. Name PROPOSED for Jay's call | PROVISIONAL |
| Direction = body region | mechanic | Region Strike — PROPOSED | Direction input picks the body region struck (head/body/legs). Name PROPOSED | PROVISIONAL |
| Dodge-timing instead of block | mechanic | Dodge Window — PROPOSED | HeartMind defense is timed dodge, not a block button. Name PROPOSED | PROVISIONAL |
| SPA meter (shape + fill) | mechanic | Nine-Soul Meter (shape donor) | UR's SPA meter shape is the model for the Nine-Soul Meter's fill curve. The meter name is canon CONFIRMED; the shape borrowing is PROVISIONAL until measured against the meter in code | PROVISIONAL |
| Partner double-team commands | mechanic | Twin Strike — PROPOSED | Partner / stand double-team command: your celestial stand strikes with you. Name PROPOSED | PROVISIONAL |
| Body-region damage | mechanic | Region damage | Damage varies by body region hit; feeds the region-strike system | CONFIRMED |
| 60 fps bar (measured) | mechanic | Descent tempo | HeartMind runs on the same 60 fps bar timing as UR | CONFIRMED |
| Free Mode (any fighter, any stage) | mode | Any-fighter Descent | HeartMind lets any fighter run the descent — the mode's any-character rule comes from UR Free Mode | CONFIRMED |
| Audio (counts UNMEASURED) | — | HeartMind SFX pool | UR audio is a donor pool for stage/enemy SFX; exact counts NOT measured in Part C — UNMEASURED | UNMEASURED |
| UI / menus (measured layout) | — | Descent UI pattern | Menu layout patterns (stage select, mission list, results) are donors for HeartMind's stage-select and results screens | PROVISIONAL |
| Glen Kluger (char identity CONFIRMED) | 1 fighter | Cain Elias — moveset source | Glen Kluger's UR moveset is Cain Elias's moveset source in WH. The only UR fighter identity CONFIRMED | CONFIRMED |
| Other 71 UR fighters (char001–072 identities) | 71 fighters | OWNER-pending / UNMEASURED | Per-fighter identities NOT measured in Part C. They are body/move donors only until the owner names them | UNMEASURED |
| Brad Hawk (UR lead) | 1 fighter | NO WH EQUIVALENT | Brad Hawk has no Western Heart counterpart. No name, no fighter, no stand | UNMEASURED |
| UR stage names | 7 stages | UNMEASURED | UR stage names are NOT carried over — HeartMind stages are canon lands. UR stage names stay in the teardown only | UNMEASURED |
| UR gang / story names | — | DROPPED | Green Harbor, gangs, and UR story do not enter Western Heart | CONFIRMED |

**UR notes:**
- UR's biggest contribution is the *feel*: the 3-press string, region strikes, dodge timing, and the 60 fps bar are HeartMind's combat feel. All four are mechanics, not names — the names are PROPOSED, the mechanics are measured (Part C §6b).
- The 72 textured GLBs are the named follow-up not yet done: the untextured 72 are wired, the textured 72 are not yet swapped in. Until the swap, HeartMind donors render untextured.
- UR missions (100 PPKs, NOT decoded) are the structure donor for HeartMind's trials. Until they decode, "Trials" is a PROPOSED name and the trial contents are UNMEASURED.

---
## §3 — Urban Reign Redux files/groups → canon name → HeartMind role

Source: `~/workspace/urban-reign-redux/INVENTORY.md` + `STATUS.md` (both verified by parent read-back, 2026-11-08 ~01:56). **The Redux all-in-one package is NOT on disk** — Google Drive quota-blocked; the one-time retry cron runs Sun Nov 8 ~7:18 PM CST. What IS on disk: Mod Manager 0.5 V97 (1,176,180,939 B, SHA `ad222bad…` matches author) + Editor 0.5 (54,476,021 B, SHA `883387a9…` matches author). Redux guests are TEMPLATE donors, not canon fighters. No LICENSE file exists; the README grants "no blanket license" over game/character assets.

| Redux group | Size (on disk) | Canon name in HeartMind | Role | Status |
|---|---|---|---|---|
| Mod Manager 0.5 V97 zip | 71 files, 1,176,180,939 B | Redux build source | The verified source of the 25 guest fighters + HD packs; builds the byte-identical 0.5 disc from Jay's own USA ISO (Windows step, Jay's PCSX2 machine) | CONFIRMED |
| `.urmod` core payload | ~370 MB | Guest core data | Core guest-fighter data donor | PROVISIONAL |
| `.urmod` HD pack 1 | ~138 MB | HD texture donor | HD texture donor for HeartMind donors | PROVISIONAL |
| `.urmod` HD pack 2 | ~596 MB | HD texture donor | HD texture donor for HeartMind donors | PROVISIONAL |
| 34 fighter portraits | 34 files | Portrait donors | Portrait art donors for the moveset template library (templates named after their source character) | PROVISIONAL |
| 16 Tekken guests (Asuka, Bryan, Jin, Kazuya, King, Nina, Paul, Yoshimitsu, Hwoarang, Heihachi, Devil Jin, Reina, Kunimitsu, Bob, Christie, Armor Queen) | 16 fighters | Strays of the Trial — PROPOSED | Moveset template donors in the template library, named after the character they came from. They are NOT WH canon fighters | PROVISIONAL |
| 9 crossover guests (Cammy, Leon, Carl Johnson, Kiryu, Jeff Hardy, Snake, Renamon, Vergence, Ricardo) | 9 fighters | Strays of the Trial — PROPOSED | Same as above — template donors, not canon fighters | PROVISIONAL |
| Devil Jin guest (Redux) | 1 fighter | Surge Kit donor (guest) | Its moveset is a second donor into the Soul Surge Form kit — NOT a WH fighter, NOT soul JIN, NOT the Surge form itself | PROVISIONAL |
| Jin guest (Redux) | 1 fighter | Template donor only | Template donor only. "Jin" here is Jin Kazama — see collision §5.1. No WH fighter target | PROVISIONAL |
| Grounded idles (Redux method) | method | Foot-ground system | Redux's grounded-idle method is the model for HeartMind's foot-ground system (feet planted, stance reads natural) | PROVISIONAL |
| Skeleton repairs (Redux method) | method | Rig-guard method | Redux's skeleton-repair method is the model for the rig-guard checks on HeartMind donors | PROVISIONAL |
| T8 stances / idles (Redux method) | method | Stance donors | Redux's T8 stance/idle set is a stance donor for HeartMind fighters | PROVISIONAL |
| String-connection fixes (Redux method) | method | Descent String fixes | Redux's string-connection fixes apply to the Descent String (PROPOSED, §2) | PROVISIONAL |
| HD texture packs (Redux method) | method | HD texture pipeline | Redux's HD packs are the texture pipeline model for the UR textured swap (§2) | PROVISIONAL |
| Mouth-animation pilot (Leon, Cammy, Violet) | method | Face — STUB | The only mouth-animation method in the sources. It feeds the face STUB — there is still no face system in HeartMind; this is a method donor, not a working face | PROVISIONAL |
| Editor 0.5 (Editor.exe + Python 3.10) | 1,081 files, 54,476,021 B | Redux build tools | Mod-making tooling; the source of the methods above | CONFIRMED |
| `roster-lib` (gyu_decode, vmd_mesh, ppk_index, texture tools) | 87 files | Decode tools | The decode tooling for UR/Redux files — the same tools that decode the 7 stage PPKs and 100 mission PPKs (§2) | CONFIRMED |
| `Source/editor/` | 36 files | Editor source | Redux editor source; build-tool reference | CONFIRMED |
| `Source/web/` | 15 files | Web reference | Redux web tooling reference | CONFIRMED |
| All-in-one package | NOT on disk | — | Quota-blocked on Google Drive; retry Sun Nov 8 ~7:18 PM CST. Until it lands, Redux content is limited to the Mod Manager + Editor on disk | UNMEASURED |

**Redux notes:**
- "Strays of the Trial" is a PROPOSED category name for the 25 guests as template donors. Jay calls it. The guests keep their own names as template names (template-library lane decision) — "Asuka" the template is not a WH fighter called Asuka.
- The Mod Manager's disc-build step is a Windows step (Launcher.exe) on Jay's PCSX2 machine, not this Linux VM. Nothing about Redux can be built from the disc on this VM.
- The mouth-animation pilot is the ONLY face/mouth method in any of the three sources. It does not make HeartMind have faces — the face system is still a STUB. Do not present the pilot as a working face.

---
## §4 — The mix plan: how DW + UR + Redux combine into HeartMind

**The mix rule:** Devil Within gives the *shape* (5 stages, waves → boss, the boss tricks). Urban Reign gives the *feel* (strings, dodge, region damage, 60 fps bar, any-fighter, missions). Redux gives the *craft* (grounded idles, skeleton repairs, HD textures, template donors). Western Heart canon gives every *name* and every *place*. Nothing keeps a source's proper nouns.

### Stage by stage

**Stage 1 — THE THRESHOLD (Tong-Nou's gate; land: the road in)**
- DW shape: G Corp lab — waves of soldiers + JACKs, then Gun Jack boss. Kept: waves → boss; the boss's gun kit.
- Boss: WARDEN OF THE THRESHOLD (380 HP, scale 1.35). Body: `gym_init_obj_boss1`. Moves: Warden Kit (`kmb1`, 39 files — machine gun, shotgun, explosion shot, charged shot). Voice: `snd_c21jac` (JACK voice). Music: `snd_bg_lab`.
- UR feel: Descent String, region strikes, dodge window; wave enemies are UR body donors (72 GLBs) + DW wave echoes (`mon01–06`).
- Redux craft: grounded idles (foot-ground), skeleton repairs (rig-guard), T8 stances.
- Canon: the Threshold is the gate into Tong-Nou. Soul embers drop here (35%, heal 22 HP).

**Stage 2 — THE GALLERY OF MASKS (Phantom Marketplace; land: under the Eyeball Mountains)**
- DW shape: the medical wing — the 1-then-3 trick (one boss, then three at once). Kept: the trick.
- Boss: THE MASKS — 1 at 135 HP, then 3 at once. Body: `gym_init_obj_boss2`. Voice: `snd_c15hei` (Heihachi voice — the multi-face boss speaks with many voices). Music: UNMEASURED — no DW stage theme for stage 2 (only 3 themes exist); UR/Redux donor or new composition.
- UR feel: the Marketplace is the Trader's floor — the Trader buys/sells elemental forces (Force Claiming lives here). Region damage and dodge timing carry the 3-at-once fight.
- Redux craft: HD texture packs for the masks; mouth pilot feeds the face STUB (the Masks are the one boss where a face matters — still a STUB).
- Canon: the Gallery is the Phantom Marketplace. The Trader's style is mimicry — the Masks borrow the player's moves.

**Stage 3 — THE DROWNING ROOM (Palace of Dreaming; land: Water)**
- DW shape: the ruins — True Ogre boss. Kept: the big-body boss with fire and charge attacks.
- Boss: THE DROWNED OGRE (520 HP, scale 1.42). Body: `gym_init_obj_boss3`. Moves: Drowned Ogre Kit (`kob2`, 29 files — fire breath, charge, dash, cutting attack). Music: `snd_bg_egy`.
- UR feel: Descent String + region strikes; the room's water is the floor — foot-ground matters most here (feet planted on a wet floor).
- Redux craft: grounded idles; HD textures for the ogre's wet skin.
- Canon: the Palace of Dreaming is the Water land. The Drowned Ogre is the water's guardian.

**Stage 4 — THE FURNACE (Plains of Chi-U; land: Fire)**
- DW shape: the spaceship — the orb boss that spawns monsters. Kept: the orb + spawn loop.
- Boss: THE SOUL SPHERE (420 HP, spawns monsters ~every 6 s). Body: NONE — `gym_init_obj_boss4` does not exist, and that absence IS the design: the sphere needs no body. Text: NONE — `moj_stg03` does not exist; Furnace text comes from canon. Music: UNMEASURED — no DW stage theme for stage 4.
- UR feel: the Furnace is the Fire land — region damage runs hottest here; the spawn loop is the wave system at its fastest (max 5 enemies alive).
- Redux craft: HD textures for the sphere's fire; string-connection fixes for the spawn pressure.
- Canon: the Plains of Chi-U are the Fire land. The Soul Sphere is the fire's heart.

**Stage 5 — THE STILL POINT (Octagonal Shrine Par-fang; land: Central Mountain, Earth)**
- DW shape: the final stage — Monstrous Ogre, two forms. Kept: the two-form final.
- Boss: SHADOW SELF (460 HP, power ×1.28) → THE UNMASKED (320 HP, second form, same descent). Body: `gym_init_obj_boss5`. Moves: Unmasked Kit (`ozb3`, 36 files + 6 extras — fire, fly, god-variant attacks). Music: `snd_bg_blu` + `snd_boss_last` (final boss music). Text: `moj_stg04`.
- UR feel: the final fight uses everything — Descent String, region strikes, dodge window, Twin Strike (stand double-team).
- Redux craft: grounded idles, T8 stances, HD textures.
- Canon: the Octagonal Shrine is the Central Mountain, Earth. Winning here ends the descent at the Shrine体系 terminal. The Unmasked is the player's own assembled soul — the final boss is you.

### Meters, ranks, systems — where each comes from

| HeartMind system (canon name) | DW source | UR source | Redux source | Status |
|---|---|---|---|---|
| Nine-Soul Meter (Devil Gauge analog) | Devil Gauge — fill by fighting, spend on Surge | SPA meter shape (fill curve donor) | — | CONFIRMED (meter name + role); shape borrowing PROVISIONAL |
| Soul Surge Form (25 s, power ×1.45, speed ×1.15, defense ×1.20, no health drain, no laser) | Devil Jin form — transformation + beam kit (`ikdv` 52 files, `djin` 4 files, `dwhadoh00` PROPOSED "Soul Beam", `dwup00` trigger, `snd_c30dvj` voice) | — | Devil Jin guest kit (second donor) | CONFIRMED (form); per-file kit PROVISIONAL |
| Soul embers (heal 22 HP, 35% drop) | Devil Within enemy drops | UR mission pickups (structure donor) | — | CONFIRMED |
| Ranks S/A/B/C (S <150 s & <50 dmg, A <240 s & <120 dmg, B <360 s, else C) | Devil Within rank thresholds — UNMEASURED (real thresholds not decoded) | UR mission ranks (structure donor) | — | CONFIRMED (rank letters + current thresholds are the built values); real DW thresholds UNMEASURED |
| Soul Seals — PROPOSED (40-symbol hunt) | Devil Symbols (40 red symbols) — the hunt structure | UR mission collectibles (structure donor) | — | PROPOSED name; hunt thresholds + symbol placement UNMEASURED |
| Force (DW currency → WH Force Claiming) | Devil Within Force economy — values UNMEASURED | — | — | CONFIRMED (system name in DESIGN.md); values UNMEASURED |
| Trials — PROPOSED (mission structure) | — | 100 mission PPKs (NOT decoded) | — | PROPOSED name; contents UNMEASURED until decode |
| Twin Strike — PROPOSED (stand double-team) | — | Partner double-team commands | — | PROPOSED name |
| Any-fighter Descent | — | Free Mode (any fighter, any stage) | 25 Strays as template donors | CONFIRMED |
| Descent String — PROPOSED | — | 3-press string, third hit juggles | String-connection fixes | PROPOSED name; mechanic CONFIRMED (Part C §6b) |
| Dodge Window — PROPOSED | — | Dodge-timing instead of block | — | PROPOSED name; mechanic CONFIRMED (Part C §6b) |
| Region Strike / region damage | — | Direction = body region + body-region damage | — | CONFIRMED |
| Foot-ground system | — | — | Grounded idles | PROVISIONAL (method donor) |
| Rig-guard | — | — | Skeleton repairs | PROVISIONAL (method donor) |
| Face system | `dwfkao00` — STUB (no face data) | — | Mouth-animation pilot (Leon, Cammy, Violet) — method only | STUB — no working face in any source |
| Doors / platforming | DW door systems — NOT in the index, contents UNMEASURED | — | — | UNMEASURED — 0% in the current build |
| Stage select | DW stage select — NOT in the index | UR stage select (layout donor) | — | UNMEASURED — 0% in the current build |
| Finish unlocks | DW "Cathedral" unlock — no WH equivalent (§5.9) | UR unlocks (structure donor) | — | UNMEASURED |

### Build order for applying this map (program coordinator)

1. **Decode lands first** — the archive-pull decode (agent `77efc077`) turns the 180 PROVISIONAL DW rows into CONFIRMED or corrected. Nothing DW is wired as final until its contents decode.
2. **UR geometry + missions** — decode the 7 stage PPKs (arenas) and 100 mission PPKs (Trials) with `roster-lib` (`ppk_index`, `gyu_decode`). Until then, §2's arena/trial rows stay PROVISIONAL.
3. **Redux all-in-one** — the Sun Nov 8 ~7:18 PM CST retry. Until it lands, Redux is limited to the Mod Manager + Editor on disk.
4. **Fill the `HM_TEARDOWN` seam** — `heartmind.js` (`ready: false`, `enemyAi: null`, `waveTables: null`, `doorSystems: null`) gets the decoded DW data, in this map's canon names.
5. **Texture swap** — the 72 textured UR GLBs replace the untextured 72 in `game/`.
6. **Watch a full descent** — a live playthrough of all 5 stages, with video proof, before any of this is called done.

---

## §5 — Conflicts + unresolved names

Every item here is UNMEASURED until Jay calls it, or until the decode lands the data. PROPOSED names are suggestions only.

### 5.1 "Jin" — three different Jins, plus two more
- **JIN (刃, the Blade Soul)** — one of the nine souls; vessel is Phantom. Canon, CONFIRMED (`NINE-SOULS-CANON.md`).
- **Jin Kazama** — Tekken character; in WH canon, Jin Kazama's data is Demonio, RIN's vessel. Has NO HeartMind role. `snd_c10jin` is a voice donor only.
- **The third bloodline Jin** — wears a devil curse, shares the name with Phantom (CANON.md). No fighter, no role yet — UNMEASURED.
- **Redux "Jin" guest** — Jin Kazama as a template donor (Strays). Template name only.
- **Devil Jin** — the DW kit owner (`ikdv`) and a Redux guest. In WH it is the Soul Surge Form's kit, not a person.
- **Collision rule:** in HeartMind text, "Jin" alone always means the soul JIN (刃). Every other Jin is written out in full ("Jin Kazama", "Devil Jin kit", "bloodline Jin"). **Jay's call owed:** confirm the rule, and whether the bloodline Jin gets a name at all.

### 5.2 "Ogre" — four ogres
- **True Ogre** (DW stage 3 boss, `kob2`) → THE DROWNED OGRE. CONFIRMED analog.
- **Monstrous Ogre** (DW stage 4 boss, `ozb3`) → THE UNMASKED. CONFIRMED analog.
- **Ogre** (Tekken 3 arcade final, True Ogre mid-match) — the arcade boss, not a HeartMind boss.
- **The Drowned Ogre** (WH boss) — the canon name; "Ogre" alone in HeartMind text means this one.
- **Collision rule:** "Ogre" never appears alone in HeartMind UI — always "Drowned Ogre" or "Unmasked". The DW source names (True / Monstrous) stay in the teardown only.

### 5.3 "Devil" — four devils
- **Devil Jin** (Tekken) → Soul Surge Form kit. Not a person in WH.
- **Devil Gene** (Tekken) → Nine-Soul Meter. Not a gene in WH.
- **Diablo** — the Devil Soul, one of the nine souls (CANON.md). A soul, not the Tekken devil.
- **Demonio** — the Demon Soul's vessel (RIN's vessel, Jin Kazama's data). A fighter, not a devil.
- **Collision rule:** the word "Devil" never appears in a HeartMind name (§0). Diablo is written "Diablo, the Devil Soul" only in canon docs, never in game UI.

### 5.4 "Force" — three forces
- **DW Force** — Devil Within's currency/economy. Values UNMEASURED.
- **WH Force Claiming** — the DESIGN.md system (claim a foe's force after beating them). Values UNMEASURED.
- **The five elemental forces** — Wood, Fire, Earth, Metal, Water (the Katana of Five Forces). Canon, CONFIRMED.
- **Collision rule:** in HeartMind, "Force" alone means an elemental force. The currency is "Force Claiming" (full phrase) and the DW economy maps onto it — PROPOSED, Jay's call. **Jay's call owed:** does DW Force = Force Claiming, or are they separate?

### 5.5 "Jack" — three Jacks
- **Gun Jack** (DW stage 1 boss, `kmb1`) → WARDEN OF THE THRESHOLD. The boss is a machine; the name "Gun Jack" stays in the teardown.
- **JACK robots** (DW stage 1 enemies) → brute wave enemies. `snd_c21jac` is the Warden's voice donor.
- **SAM-UR-A1's Gun Jack frame** (Urban Reign) — a UR fighter frame; donor only.
- **Collision rule:** no "Jack" in HeartMind UI. Wave brutes are called "brutes" (code term, CONFIRMED in `brawler.js`).

### 5.6 "Surge" — three surges
- **Soul Surge Form** (HeartMind, 25 s transform) — CONFIRMED.
- **Soul Surge** (L key in versus, an 18-damage strike costing the full meter) — the versus move, NOT the HeartMind form. The real versus super is Nine-Soul Release (1+2+3+4 chord).
- **Surge Kit** (this map's working name for the `ikdv` kit) — PROPOSED working name, not a UI name.
- **Collision rule:** in HeartMind, "Surge" alone means the Form. The versus L-key move needs its own name if it keeps existing — UNMEASURED, Jay's call.

### 5.7 BYOU has no body — and no soul-body name
- BYOU (sickness, jaundiced yellows, infected greens) is a soul with NO body of its own; it fights through its vessel **Zui** (pickable, Steve Fox base) and shows as a celestial stand. Canon, CONFIRMED.
- "Give BYOU a model" contradicts canon — what's owed is vessel/stand wiring, not a BYOU body.
- **Gap:** canon names no soul-body for BYOU's stand. **PROPOSED:** "the Jaundiced Stand" — Jay's call. Do not wire a BYOU body.

### 5.8 "Strays of the Trial" — PROPOSED category, Jay's call
- The 25 Redux guests as template donors need a category name in the template library. PROPOSED: "Strays of the Trial" — fighters who wandered into the descent from other worlds.
- Alternative if Jay dislikes it: "Guest Templates" (plain, no canon claim). Either way, the guests are NOT canon fighters.

### 5.9 DW things with no WH equivalent
- **"Cathedral" unlock** (DW finish unlock) — no WH equivalent. HeartMind's finish unlocks are UNMEASURED; the Cathedral name is dropped.
- **"G Corp"** (DW corporation) — no WH equivalent. Its soldiers → gunner wave donors; its JACKs → brute donors; its mutants (Adam, Eve, Duke, Regal, Jill) → echo donors. **PROPOSED group name for the mutants:** "the Hollow" — Jay's call. The mutants keep no individual WH names.
- **Brad Hawk** (UR lead) — no WH equivalent (§2). No name, no fighter, no stand.

### 5.10 Gaps the decode must close (UNMEASURED until contents land)
- `ikt5` kit (26 files) — owner unknown. Do not wire until the decode names it.
- `tk_*` init kits (11 files: tk05, tk09–12, tk14–17, tk19, tk21) — targets unknown.
- Opaque tokens: `dsrp`, `sjk` (+ variants), `nara`, `dv2kam2`, `dv_jz`, `jz_dv`, `psk`/`psk2`, `god_*` (5 files) — 22 files with no gloss. Contents decide them.
- Stage 2 + stage 4 music — only 3 DW stage themes exist for 5 stages.
- Real DW rank thresholds, Force values, symbol-hunt placement, door/platforming systems, stage-select data — none in the index.
- UR: 71 fighter identities OWNER-pending; audio counts; stage names; mission contents.
- ZEN's 12 model files vs the "spirit body" the owner meant — UNMEASURED (canon question, not a decode question).
- The `god_*` files (`god_chrg`, `god_dash`, `god_fire`, `god_kick`, `god_punch`) may be a powered-up Ogre variant — contents decide whether THE UNMASKED gets a third form. Do NOT build a third form on the name alone.

---

## Sources

- `~/workspace/devil-within-decode/repo/teardown/tekken5/dw-motion-index.json` — 242 DW files, index level
- `~/workspace/devil-within-decode/repo/teardown/tekken5/DW-DECODE-LOG.md`, `ROMD-FORMAT.md`, `DEVIL-WITHIN-DATA.md`
- `~/workspace/western-heart-audit/TEARDOWN-PART-B-DEVIL-WITHIN.md`, `TEARDOWN-PART-C-URBAN-REIGN.md`, `TEKKEN-TEARDOWN-SPEC.md` §5
- `~/workspace/western-heart-audit/NINE-SOULS-CANON.md`, `HIDDEN-9-MODELS.md`, `HEARTMIND-COMPLETION.md`
- `~/workspace/urban-reign-redux/INVENTORY.md`, `STATUS.md`
- Canon: `CANON.md`, `ROSTER.md`, `DESIGN.md` (repo `mhvnsnt/western-heart`, HEAD `3334ebf`)
- Code: `game/js/heartmind.js`, `game/js/brawler.js`, `game/js/heartmind-campaign.js`

## What unblocks the rest

1. **The archive-pull decode** (agent `77efc077`, running) — turns 180 PROVISIONAL DW rows into CONFIRMED or corrected, and closes §5.10.
2. **UR PPK decode** (`roster-lib`: `ppk_index`, `gyu_decode`) — 7 stage PPKs + 100 mission PPKs.
3. **Redux all-in-one retry** — Sun Nov 8 ~7:18 PM CST cron.
4. **Jay's calls:** §5.1 (the "Jin" rule + bloodline Jin), §5.4 (DW Force = Force Claiming?), §5.6 (versus L-key move name), §5.7 ("the Jaundiced Stand"), §5.8 ("Strays of the Trial"), §5.9 ("the Hollow"), §4 "Trials" / "Descent String" / "Dodge Window" / "Twin Strike" / "Soul Beam" / "Soul Seals" names.
