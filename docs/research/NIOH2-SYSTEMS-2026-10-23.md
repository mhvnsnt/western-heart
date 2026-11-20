# Nioh 2: The Complete Edition — Systems Research for Western Heart

**Date:** 2026-10-23
**Status:** PUBLIC-SOURCE RESEARCH ONLY. No Steam file pull was attempted or possible on this machine — no Steam credentials exist here, no game files were accessed, and no claims in this document are faked or inferred from file data. Every substantive claim is cited to a public URL in Sources. This document builds on PR #882 (`docs/research/NIOH-SYSTEMS-2026-10-23.md`, Nioh 1 systems); it documents only what is NEW or DEEPER in Nioh 2 and does not duplicate the Nioh 1 findings (stances, Ki Pulse, skill trees, Living Weapon, loot/gear systems, Abyss, Kodama blessings, NG+ cycles).

**Steam app ID:** 1325200 (Nioh 2: The Complete Edition)

---

## Owner instruction (verbatim)

> *"Nioh 2 and nioh: world and Eastern mind and mythology depth and character creation and parts"*

---

## 0. What Nioh 2 adds over Nioh 1 (context)

Nioh 2 is a **prequel** (Sengoku period, 1555–1616) that keeps Nioh 1's stance/Ki Pulse/skill-tree/loot core and adds four headline systems that did not exist in Nioh 1:

1. **Yokai Shift** — replaces Nioh 1's Living Weapon. The protagonist is a half-yokai "Shiftling" who transforms into a full yokai form.
2. **Soul Cores** — drops from defeated yokai; equip 2–6 enemy abilities on your Guardian Spirits.
3. **Burst Counters** — a universal riposte against red-glow "Burst" attacks, with three different behaviors tied to Guardian Spirit type.
4. **Dark Realm** — zone-level debuff fields where player Ki recovery is crippled and yokai are empowered; bosses can convert their arena into it.

Plus: **full character creation** (Nioh 1 had a fixed protagonist), a new **Anima** resource (purple gauge under health/Ki), new weapons (Switchglaive, DLC Splitstaff and Fists), 3 DLC expansions that time-travel to the Heian period, and **The Underworld + Depths** as the endgame successor to Nioh 1's Abyss.

Team Ninja's stated design philosophy for the sequel, from director Fumihiko Yasuda: the goal was "an evolution of the first title in every way," improving from fan feedback — Yokai abilities exist because "when you're a human character fighting against Yokai and these more powerful enemies, the battle can start getting drawn out a bit," so the team wanted the player to "go toe to toe with some of these really fearsome Yokai enemies" — and the character creator exists because it was "one of the biggest requests" from fans, giving players "the freedom to tell their own story" with their own character instead of William.
(Sources: https://filmstories.co.uk/features/masocore-the-making-of-the-nioh-series/, https://www.pcgamesn.com/nioh-2/nioh-2-character-customisation?tw=PCGN, https://gamefaqs.gamespot.com/boards/241160-nioh-2/79248324)

---

## 1. The Yokai systems: Yokai Shift, Soul Cores, Burst Counters, Dark Realm, Anima

### 1.1 Yokai Shift [RESEARCHED]

Yokai Shift is the transformation super that replaces Nioh 1's Living Weapon. Mechanics:

- **Activation:** press Triangle + Circle when the **Amrita Gauge** is full (the circular Guardian-Spirit icon left of the health bar starts glowing). Amrita (the game's XP/currency resource) fills the gauge as you kill enemies or consume Spirit Stones.
- **Form determined by Guardian Spirit type.** There are three shift forms, each with a distinct moveset and playstyle:
  - **Brute** — heavy melee oni wielding a club; overwhelming demon strength; cannot be staggered; special move **Fang Break**, a counter that staggers enemies and opens damage windows.
  - **Feral** — fast kitsune-like form with dual knives; built around tight combos and quick dodges between attacks (dash-cancel routing); can still be staggered, mitigated by dodge-flow.
  - **Phantom** — ghost-like ranged form; pins enemies down at range with projectiles; special **Blood Moon Yin / Blood Moon Yang** lets it teleport in close for the kill and warp back to safety.
- **Shift gauge replaces HP/Ki/Anima.** In Shift, health and Ki become a single Yokai Shift gauge that drains over time; attacking, dodging, blocking, and taking hits all drain it faster. Effectively "infinite HP/Ki/Anima" while active, but time-boxed.
- **Guardian Spirit summon:** pressing Triangle + Circle again in Shift unleashes a per-spirit super attack, but consumes the remainder of the gauge. You can also end Shift early by "sheathing" (R1 + Circle).
- **Yokai Realm interaction:** walking into a Yokai Realm pool in Shift form purifies it and grants Amrita (fuel for the next shift); attacking the pool instead boosts attack damage.
- You can swap Primary/Secondary Guardian Spirits mid-combat (R1 + L2) for different abilities and bonuses.

(Sources: https://www.cbr.com/nioh-2-guardian-spirits-explained/, https://www.thegamer.com/nioh-2-how-do-yokai-forms-work/, https://attackofthefanboy.com/guides/nioh-2-how-to-transform-how-to-yokai-shift/, https://fextralife.com/nioh-2-guide-to-guardian-spirits-soul-cores/?query-0-page=3&cst, https://steamcommunity.com/sharedfiles/filedetails/?l=swedish&id=2432415046)

**[AWAITS FILE PULL]:** Shift-gauge drain rates per action, per-form damage/defense multipliers, Fang Break / Blood Moon frame data and hitbox geometry, Guardian Spirit summon-attack parameters, the per-spirit "different effect" table, Amrita-to-gauge conversion formula.

### 1.2 Soul Cores [RESEARCHED]

Soul Cores are the "steal your enemy's move" system — the beating heart of a yokai's essence dropped on defeat.

- **Acquisition:** any yokai (non-human) enemy can drop one; bosses are guaranteed. Human enemies never drop them.
- **Purification gate:** a dropped core is "impure" and unusable until you Pray at a Shrine, which auto-purifies everything you're carrying. Die and fail to recover your grave, and the cores go with your Amrita.
- **Attunement:** at a Shrine → Manage Soul Cores → Attune Soul Cores. Each core has an **Attunement cost**; each Guardian Spirit has an **Attunement Limit** capping which combinations you can equip. Start: 3 cores per spirit, 2 usable abilities mapped to R2 + Square / R2 + Triangle; progress unlocks a second spirit (4 abilities), and later a third slot per spirit (up to 6 total).
- **Anima cost:** every Yokai Ability consumes **Anima** (the purple gauge under health/Ki). Anima recharges by landing melee hits and defeating enemies; picking up a Soul Core instantly refills the gauge to max (advanced play: leave a core on the ground mid-fight as a refill pickup). Costs range roughly 2–10+ Anima across ~50 abilities — e.g. Enenra's **Fire Twister** (6 Anima), Enki's **Monkey Dance** spear-toss (5), Kasha's **Hellfire Wheel** (8), Scampuss's **Scampush** (4), Ryomen Sukuna's **Fire and Ice** (8).
- **Cores are passive carriers too:** each has Attack/Defense stats and rolled Special Effects (e.g. Yatsu-no-Kami core: increased damage vs. poisoned enemies).
- **Three management verbs at the Shrine:** Attune Soul Cores (equip), **Soul Fusion** (feed a same-yokai core into a base to raise its Soul Core Rank up to 9 — improves Special Effects, not Level/Attack/Defense), and **Resting Rites** (destroy unwanted cores for Shiftling skill points + crafting materials).
- **Mortal Soul Cores:** part-human/part-supernatural bosses drop Mortal variants, used at the Shrine to raise yokai cores to higher levels.
- **Soul Match with Yokai weapons:** infusing a Soul Core into a Corruption-damage weapon upgrades the weapon cheaply (blacksmith economy).

(Sources: https://nioh2.wiki.fextralife.com/Yokai+Skills, https://www.polygon.com/nioh-2-guide/2020/3/13/21175247/soul-cores-yokai-fusion-fragments-shiftling-skill-points/, https://www.gameskinny.com/tips/nioh-2-soul-core-guide-everything-you-need-to-know/, https://fextralife.com/nioh-2-guide-to-guardian-spirits-soul-cores/?query-0-page=3&cst, https://www.psu.com/news/nioh-2-walkthrough-combat-explained/, https://cosmeticszik.weebly.com/blog/nioh-2-difficulty)

**[AWAITS FILE PULL]:** the full Soul Core definition table (all ~50+ cores: Anima cost, Attunement cost, damage formulas, special-effect roll tables, rank scaling), Attunement Limits per Guardian Spirit, Shiftling skill-tree data (unlock costs/gates), Resting Rites conversion rates, Mortal Soul Core level-up curve.

### 1.3 Burst Counters [RESEARCHED]

The single most important combat addition. When a yokai begins an unblockable "Burst" attack, it flashes **red** (with an ominous audio cue). Pressing **R2 + Circle** (1 Anima) performs a Burst Counter whose behavior depends on your Guardian Spirit type — three completely different timings:

- **Brute (offensive / interrupt):** a horizontal swipe with a generous hitbox. Fire it *as the red glow appears* — it interrupts the enemy *before* the attack animation starts ("who acts first"). Most beginner-friendly; taking a little chip damage on mistiming is normal; the Brute skill tree has a perk restoring 40% HP on a counter landed at critical health.
- **Feral (dodge / afterimage):** a directional dash that leaves a ghostly afterimage. The counter triggers if the enemy's attack **hits the afterimage** — dodge *into* the attack at the last moment. Hardest to master, but uniquely can counter **projectiles and grabs** as well.
- **Phantom (defensive / block-parry):** briefly becomes a yokai and auto-guards. If your guard connects with the incoming attack at the last moment, the counter fires. Easiest timing to learn; a mistimed attempt still blocks like a normal block (drains Ki).

A landed Burst Counter deals heavy **Ki damage** plus health damage and opens the enemy to follow-up combos — Ki-breaking is the game's core damage loop. If a Burst attack is NOT countered, it spawns a **Yokai Realm puddle** that lets the demon recover Ki. Grab-type Burst attacks show **black** smoke instead of red and cannot be burst-countered — only dodged.

Design note: this is a single input that the game *deliberately tri-splits by archetype* — offense / evasion / defense — so the counter you learn is a loadout choice, not just a reflex test. It's also the mechanic Team Ninja deepened between the Nioh 2 beta and launch after players said combat hadn't changed enough from Nioh 1.
(Sources: https://www.gamerevolution.com/?p=638165, https://twinfinite.net/guides/nioh-2-parry-counter-guide/, https://www.gamepur.com/guides/everything-you-need-to-know-about-burst-counter-in-nioh-2, https://ethugamer.com/nioh-2/nioh-2-burst-counter-guide/, https://gamefaqs.gamespot.com/boards/241160-nioh-2/78521106?page=2, https://steamcommunity.com/app/1325200/discussions/0/4265444591469826954/?l=czech, https://filmstories.co.uk/features/masocore-the-making-of-the-nioh-series/)

**[AWAITS FILE PULL]:** counter window frame data per type, Ki-damage values, the per-enemy Burst-attack table (which attacks are Burst-flagged, red vs. black smoke flags), Anima cost tuning, any per-form counter modifiers.

### 1.4 Dark Realm [RESEARCHED]

- Sections of a mission map can be **submerged in the Dark Realm**: while inside, the player's Ki recovery is severely hampered and yokai are empowered. It functions like Nioh 1's Yokai Realm pools scaled up to zone level.
- You clear a Dark Realm zone by killing its **main yokai** (typically a buffed-up version of a larger yokai you've already fought).
- **Bosses can convert their entire arena into the Dark Realm**, adding a phase-level obstacle to boss fights.
- Counterplay is yokai-side: Yokai Shift and Soul Core abilities are explicitly most valuable inside the Dark Realm — the game teaches you to answer demonic terrain with demonic tools. (Also ties to 1.1: Shift purifies Yokai Realm pools.)
- Level-design function: Dark Realm sections gate pacing — they're "kill the mini-boss to restore normal rules" checkpoints inside larger stages.

(Sources: https://waytoomany.games/2020/04/01/review-nioh-2/, https://shapes.inc/fandom/nioh/yokai-bestiary, https://www.gadgetpilipinas.net/2019/09/5-new-things-we-learned-from-our-tgs-2019-nioh-2-hands-on-session/3/)

**[AWAITS FILE PULL]:** Dark Realm debuff coefficients (Ki recovery multiplier, yokai buff multipliers), zone trigger/boundary definitions, boss arena-conversion triggers, per-mission Dark Realm zone layouts.

### 1.5 New weapons and skill depth (context) [RESEARCHED]

- **Switchglaive** (base game): transforming spear/scythe hybrid; stance-switching mid-attack is part of its kit. Director Yasuda's personal recommended weapon.
- **Splitstaff** (Tengu's Disciple DLC), **Fists** (Darkness in the Capital DLC) — each DLC added a full weapon class with its own skill tree. Fists are Yasuda's other recommendation.
- Shiftling skill tree (yokai-side skills) sits alongside the Samurai/Ninja/Onmyo trees from Nioh 1.

(Sources: https://www.playstation.com/en-fi/editorial/8-new-things-you-will-be-doing-in-nioh-2/, https://nioh2.wiki.fextralife.com/DLC, https://gamefaqs.gamespot.com/boards/241160-nioh-2/79248324)

**Transferable technique for WH (structure only):** the pattern worth stealing is the *transformation super as a resource-state machine* (meter fills from combat → transform swaps your entire health/stamina resource model → actions drain it → optional super-consumes-remainder finisher → sheathe to bank it), and the *enemy-move theft* pattern (defeat → drop → purify-gate → attunement-budget → 2 active + passives). A fighting-game analogue: a meter that converts your character to an alternate moveset state with its own drain rules, and a "learn the opponent's special" loadout system gated by a budget. WH fills both with its own canon (Nine Souls, Oversoul) — never Nioh's yokai.

---

## 2. Character creation (Nioh 2 added this — Nioh 1 did not have it)

### 2.1 Creator depth [RESEARCHED]

Nioh 1's protagonist was fixed (William, with cosmetic skins only). Nioh 2 replaced him with **Hide (秀)**, a half-yokai "Shiftling" whose appearance and gender the player defines. The creator's documented categories:

- **Base:** Gender (Male/Female), 4 presets, Posture, Skin (color + luster), Aging (Overall Aging, Forehead Wrinkles, Eye Wrinkles, Laugh Lines).
- **Face:** Face Shape, Eyes, Pupils, Eyebrows, Nose, Mouth, Ears — each with fine sliders.
- **Hair:** Style, Length, Curliness, Club Length, Color, Shine, plus Hair Tips 1/2/3 (multi-zone coloring).
- **Facial Hair:** Type, Shine, Tip Color, Tip Area, Tip Shine, Beard (Jaw), Mustache.
- **Makeup/Scars:** Eyeliner (type/color), Eye Shadow (type/color/shine), Eyelash (type/color/length), Lipstick (type/color), plus scars/face paint.
- **Yokai form appearance:** the creator also defines the look of your demonic Yokai form — the transformation is customized, not just the human.

Community reception: press and players describe it as a "pretty detailed character creation section" with "a wide array of sliders," down to "how curly your fringe is." It produced a strong share-culture of recreations of other game icons.

### 2.2 Creator UX patterns [RESEARCHED]

- **Re-editable forever:** Starting Point (world map) → **Hut** → Change Appearance re-opens the full creator at any time — **no cost, unlimited uses**, including gender change. No restart needed.
- **Save/Load + share codes:** save multiple creations, reload old ones, and export/import via **character codes** other players can enter — a copy-paste string that reproduces a full build.
- **Transform option:** in addition to your own creation, you can take on the appearance of story NPCs ("transform into other skins").
- **Builds save slots:** separate from appearance — named full loadouts (equipment + stats + skills) switchable between missions.
- Dev rationale (Yasuda): "One of the biggest requests that we had was character creation"; the story was deliberately written to revolve around the player's protagonist "so that they would feel like they themselves were moving the story forward," while keeping the same shared story beats for all players.

(Sources: https://nioh2.wiki.fextralife.com/Character+Creation, https://www.playstation.com/en-fi/editorial/8-new-things-you-will-be-doing-in-nioh-2/, https://twinfinite.net/guides/nioh-2-how-to-change-character-appearance/, https://attackofthefanboy.com/guides/nioh-2-change-appearance/186, https://Www.thegamer.com/nioh-2-how-change-appearance/, https://www.shacknews.com/article/122257/nioh-2-the-complete-edition-interview-with-producer-fumihiko-yasuda?amphtml=1, https://www.pcgamesn.com/nioh-2/nioh-2-character-customisation?tw=PCGN, https://www.thegamer.com/team-ninja-interview-fumihiko-yasuda-nioh/; Builds: GameFAQs Hut guide cited in PR #882)

**[AWAITS FILE PULL]:** the creator's actual parameter schema (slider ranges, bone/morph target list, texture-layer stack for makeup/scars, the character-code serialization format, yokai-form customization parameters, preset definitions). The share-code format is the single most valuable pull — it's a proven serialization of a full parametric character.

**Transferable technique for WH's creation suite (structure only):** creator-at-start + free unlimited re-edit + save slots + shareable codes + NPC-appearance transform + named build loadouts (appearance separated from gear/stats/skills) + *the transformation form is itself customizable*. WH already has its own suite in progress — Nioh 2 validates these exact patterns and adds one WH should consider: **customizing the powered-up/transformation form as part of the same creator session**.

---

## 3. Mythology depth — STRUCTURE AND TECHNIQUE ONLY (no content transfer)

### 3.1 History × folklore fusion method [RESEARCHED]

- **Setting:** Sengoku-period Japan, 1555–1616 (per the Complete Edition encyclopedia entry). Nioh 2 is a prequel to Nioh 1.
- **Technique: real warlords as cast, yokai as the supernatural layer.** Historical figures appear as characters and bosses: Oda Nobunaga, Toyotomi Hideyoshi (as the merchant Tokichiro), Tokugawa Ieyasu, Akechi Mitsuhide (Honnō-ji betrayal reframed with yokai influence), Hattori Hanzo, Honda Tadakatsu, Maeda Toshiie, Maeda Keiji, Saika Magoichi, Saitō Dōsan, Saitō Yoshitatsu, Shibata Katsuie, Imagawa Yoshimoto, Azai Nagamasa, Tsukahara Bokuden, Minamoto no Yoshitsune, Benkei, Kukai, Taira no Kagekiyo, Ashiya Doman, Matsunaga Hisahide. The history is treated as *accurate scaffolding* — the game "leans into" documented traits (Ieyasu's patience, Hideyoshi's peasant-to-ruler rise and later paranoia, Saika Ikki's gun discipline) and layers the supernatural on as explanation/amp, not replacement.
- **Yokai roster is deep and sourced:** Otakemaru, Shuten Doji, Enenra, Nue, Kamaitachi, Tsuchigumo, Kasha (from the *Konjaku Monogatarishū*), Mezuki & Gozuki, Onryoki, Gyuki, Yatsu-no-Kami, Ryomen Sukuna, Uminyudo, White Tiger (one of the four cardinal-direction beast-gods), Daidara Bocchi, Ippon-Datara (one-legged smiths of the Kumano Mountains), Tesso, Kappa, Gaki, Karasu Tengu, Rokurokubi, Nure-Onna, Yamanba, Namahage, Oboroguruma, Nurikabe, Mujina, Konaki-Jiji, plus benevolent ones below.
- **Yasuda's selection rule (design-relevant):** "We built upon the concepts and way that yokai appeared in the first Nioh, and **chose new yokai to include based on how well their signature movements and unique traits would result in fun new gameplay elements** for the player to enjoy." Folklore is mined for *kinematics* — the creature's legendary behavior becomes its moveset (Ippon-Datara's hammer slam creates a Yokai Realm pool; Kasha's flaming wheel becomes the tracking Scorching Wheel; Tesso flings filth for the Stench status).
- **DLC as time-travel:** the three expansions go back to the Heian period — Tengu's Disciple (coastal Yashima, late Heian), Darkness in the Capital (Heian Kyoto, "Japan's foremost demon slayer and history's most powerful Onmyo mage"), The First Samurai (origins of Otakemaru, the protagonist's lineage) — and the through-line is one figure whose "presence ties the entire Nioh timeline together, linking the ancient Heian period to the Sengoku era." Technique: a single mythic anchor lets you expand the timeline in both directions without breaking continuity.

(Sources: https://sevenswords.uk/nioh-2-real-history/, https://sevenswords.uk/nioh-2-story-explained-timeline-lore-key-events/, https://nioh2.wiki.fextralife.com/Bosses, https://nioh2.wiki.fextralife.com/Enemies, https://shapes.inc/fandom/nioh/yokai-bestiary, https://shapes.inc/fandom/nioh-2-the-complete-edition, https://nioh2.wiki.fextralife.com/DLC, https://www.shacknews.com/article/122257/nioh-2-the-complete-edition-interview-with-producer-fumihiko-yasuda?amphtml=1, http://tvtropes.org/pmwiki/pmwiki.php/Characters/NiohEnemiesAndBosses)

### 3.2 Benevolent-yokai interaction pattern [RESEARCHED]

Not all yokai are combat: **Scampuss** (round cat-yokai; pet it and up to 3 follow you, regenerating Anima), **Sudama** (corrupted Kodama that request item *trades*), **Nurikabe** (wall-mimic blocking paths; pacified with specific gestures or fought), **Mujina** (shapeshifting badger hiding in chests; challenges you to mimic its gestures), **Kodama** (returned to shrines for blessings). Technique: folklore becomes *interaction verbs* (pet, trade, gesture-pacify, gesture-mimic) — the mythology system has a non-combat channel, which makes the world feel inhabited rather than just hunted.

(Sources: https://shapes.inc/fandom/nioh/yokai-bestiary, https://www.gadgetpilipinas.net/2019/09/5-new-things-we-learned-from-our-tgs-2019-nioh-2-hands-on-session/3/, https://steamcommunity.com/sharedfiles/filedetails/?l=swedish&id=2432415046)

### 3.3 Compendium pattern (extends PR #882 §3.1) [RESEARCHED]

Nioh 2 keeps the "View Illustrations" encyclopedia at the Hut (yokai, characters, Guardian Spirits, plus rewatchable cutscenes), unlocked by progression — and adds a wrinkle relevant to boss-reuse: bosses recur later as regular enemies, with entries framing them as **a species, not individuals** — lore justifying mechanical reuse. Each entry follows the fixed architecture documented in PR #882 (name + classification, folklore-natural-history description, behavioral notes tied to gameplay).

**[AWAITS FILE PULL]:** the compendium entry text-format/schema (field structure per entry, unlock-condition mapping) — same target as PR #882 §5, now including Nioh 2's yokai/character/Guardian Spirit entries.

**LORE FIREWALL — READ FIRST:** No Nioh creature, person, place, plot beat, term (Amrita, Ki, Yokai, Shiftling, Dark Realm, Soul Core, etc.), or text enters Western Heart or its canon. What transfers is STRUCTURE AND TECHNIQUE ONLY: (1) mine folklore for signature *movements/behaviors* and convert them to moveset mechanics; (2) keep real-world scaffolding accurate and layer the supernatural as explanation, never replacement; (3) use one mythic anchor figure to extend the timeline in both directions; (4) give mythic entities non-combat interaction verbs (trade, pacify, mimic, follow); (5) compendium entries with fixed fields, unlocked by progression, with "species not individual" framing for reuse. WH fills every slot with its own canon (Nine Souls, Tong-Nou, the Trial, Eastern Mind entities).

---

## 4. World building: mission map, regions, reuse

### 4.1 Region map, not open world [RESEARCHED]

- Between missions you return to a **large map screen** (the "country map") and select missions per **region**. Base-game regions unlock sequentially as you clear main missions: Awakening → Soaring → Shadow → Dawn → Twilight → Dream, plus 3 DLC regions (Yashima, The Capital, Suzuka) appended as new map rows. Complete Edition = 7 main regions + 3 DLC regions.
- **Each region's "starting point"** hosts the hub facilities: the Hut (creator/builds/illustrations), Shrine, Blacksmith (unlocks after the 2nd main mission), Dojo, Hidden Teahouse (unlocks in the 2nd region), Torii Gate (online).
- **Mission types:** Main (story, mandatory, unique bosses) / Sub (optional side stories, sometimes harder than mains; located on previously visited maps) / Twilight (rotating harder remixes of mains/sides — 2 per day, changing daily; the only source of quality umbracite outside first-time rewards) / Dojo (training missions that gate skill tiers — including dedicated Yokai Shift tutorial missions per form).
- **Completing any mission first time** yields unique first-time rewards; repeats give less. Twilight first-time rewards refresh daily.
- **Map reuse as a feature:** sub missions reuse main-mission maps with different layouts/enemy placement; and the game shows **time-passage on revisits** — returning to a town that was intact can find it burning — "so returning to the same general area" still feels like a new mission. Individual stages follow a formula players describe as ~2-path branches that loop to a common shrine, then repeat (horseshoe/loop level design), with unlockable shortcuts back to shrines.
- Player debate notes Nioh 2's maps are larger and less corridor-like than Nioh 1's, with castle levels praised for feeling like functional fortifications and good game levels simultaneously.

(Sources: https://www.ludo.guide/guide/nioh-2/hub-and-overworld-2, https://noisypixel.net/nioh-2-review-ps4/, https://thedrastikmeasure.com/2021/03/14/nioh-2-the-complete-edition-pc-review/, https://steamcommunity.com/app/1325200/discussions/0/5760637065633341605/?l=latam, https://gamefaqs.gamespot.com/boards/241160-nioh-2/80785439)

### 4.2 NG+ cycles and the endgame tail [RESEARCHED]

- NG+ difficulties: **Dream of the Samurai → Strong → Demon → Wise → Nioh** (NG+0–4).
- **The Underworld** (added with The First Samurai DLC; unlocks at Dream of the Nioh): **108 static floors**, each floor a mini-level with yokai, bosses, and cursed loot — the successor to Nioh 1's 999-floor Abyss.
- **The Depths** (the Underworld's second section): **30 randomly generated floors**. Floors 1–5 change daily; 6+ regenerate every entry; progress saves every 5 floors. Floors 11–20 have **two consecutive bosses** per floor; 21–30 have **three** — dying means refighting all of them. Rewards: Scrolls of the Damned (with "Path of the ___" gameplay-altering rules), Jizo blessings from a merchant, +level cap increases, exclusive Ethereal Graces.
- DLC cadence: Tengu's Disciple (Jul 30, 2020), Darkness in the Capital (Oct 15, 2020), The First Samurai (Dec 17, 2020) — each ~10 missions across 3 new locations + a new weapon class + new spirits/skills. DLC philosophy per Yasuda: built from base-game feedback and "what the game still needed" (example: the Amabie Guardian Spirit was added during DLC development because of the societal response to that yokai during COVID-19).

(Sources: https://nioh2.wiki.fextralife.com/The+Underworld, https://sevenswords.uk/nioh-2-how-to-prepare-for-the-underworld/, https://gamefaqs.gamespot.com/boards/305939-nioh-2-the-complete-edition/80496657, https://www.gamerevolution.com/guides/647553-nioh-2-dlc-release-date-tengus-disciple-ps4, https://nioh2.wiki.fextralife.com/DLC, https://www.shacknews.com/article/122257/nioh-2-the-complete-edition-interview-with-producer-fumihiko-yasuda?amphtml=1)

**[AWAITS FILE PULL]:** mission/region/unlock tables, reward tables, Depths floor-generation parameters and boss-selection logic, Scroll of the Damned rule definitions, Twilight mission rotation schedule format.

**Transferable technique for WH/HMW (structure only):** region-mapped chapter select with per-region hub facilities (WH already has this pattern from PR #882 §6 — Nioh 2 adds: facilities unlock *across* regions on a schedule, sub-missions explicitly reuse main maps with remixed layouts, revisits show time-passage state changes, daily-rotating challenge missions with exclusive crafting materials, dedicated tutorial missions per new mechanic, and an endgame gauntlet split into a fixed 108-floor climb plus a 30-floor randomized depths with boss-count escalation). All WH-canon filled.

---

## 5. Extraction plan for the credentialed machine

Context: the user owns games per the standing ownership rule; Nioh 2: The Complete Edition is Steam app **1325200**. This VM has no Steam credentials — no pull was attempted or faked.

1. **Acquire:** on the credentialed machine, SteamCMD `app_update 1325200` (verify the app ID against the Steam store page / SteamDB at pull time; do not hardcode blindly). Footprint is large (tens of GB); record actual size.
2. **Inventory first:** list the install tree (exe, data dirs, archive extensions). Koei Tecmo PC titles ship packed archives — enumerate before touching anything. Write `docs/research/NIOH2-FILE-INVENTORY-<date>.md`. Note: public sources confirm no official modding SDK or documented formats; expect binary reconnaissance.
3. **Priority extraction targets** (structure/technique only — no lore content leaves the lab):
   - **Character creator schema:** slider/morph-target list, parameter ranges, texture-layer stack (makeup/scars), the **character-code serialization format** (highest value — a proven parametric-character codec), yokai-form customization parameters, preset definitions.
   - **Soul Core definition table:** all cores — Anima cost, Attunement cost, damage formulas, special-effect roll tables, rank scaling to 9, Mortal Core level-up curve.
   - **Guardian Spirit definitions:** Attunement Limits, per-spirit passives, the three Shift-form parameter sets, Burst Counter per-type frame data and Ki-damage values, per-spirit Shift summon attacks.
   - **Burst-attack enemy table:** which enemy attacks are Burst-flagged (red vs. black-smoke grab flags).
   - **Dark Realm parameters:** debuff coefficients, zone triggers, boss arena-conversion triggers.
   - **Mission/region/unlock/reward tables;** Twilight rotation format; Depths generation parameters; Scroll of the Damned rule definitions.
   - **Compendium entry schema** (field structure + unlock mapping) for yokai/character/Guardian Spirit entries.
   - **Shiftling skill-tree data** (costs, gates) and Resting Rites conversion rates.
   - **UI layout reference:** creator UI, Manage Soul Cores UI, skill-tree UI — layout technique for WH's own menus (WH's menus-from-teardowns law applies; Nioh 2's dense RPG menus are a second reference pole next to Tekken's).
4. **Tooling:** no official tools exist. Binary recon (headers, `strings`), then format notes; check Nexus/Steam community for any unpacker appearing after this doc's date. If archives resist, fall back to **black-box documentation** (observable behavior + UI text via screenshots) — still valuable for systems design.
5. **Saves (PC):** per the Nioh 1 doc, Koei Tecmo titles store saves under `Documents\KoeiTecmo\NIOH2\Savedata\<SteamID>\` (Nioh 2 path pattern observed on Nexus save mods — https://www.nexusmods.com/nioh2/mods/95; verify at pull time). Useful for studying share-code payloads.
6. **Where assets land:** research derivatives → `docs/research/` (siblings of this file and PR #882's doc); rebuilt WH-canon-filled schemas → the appropriate system design docs. **Never commit Nioh's copyrighted assets, text, or lore to the repo.** Do not redistribute extracted assets. Extraction is for interoperability/systems research under the standing game-ownership rule.
7. **Mapping to HMW:** fold Nioh 2's additions into PR #882 §6's table as new rows — Yokai Shift → per-fighter transformation super (WH-canon soul form); Soul Cores → "learn the opponent's special" loadout system with attunement budget; Burst Counters → archetype-split (offense/evasion/defense) universal counter mechanic; Dark Realm → WH-canon terrain-debuff zones cleared by killing the zone's anchor; Depths → HMW endgame gauntlet v2 (fixed climb + randomized depths with boss escalation).

---

## Sources

Public sources only; no game files were accessed.

- Yokai Shift / Guardian Spirits: https://www.cbr.com/nioh-2-guardian-spirits-explained/, https://www.thegamer.com/nioh-2-how-do-yokai-forms-work/, https://attackofthefanboy.com/guides/nioh-2-how-to-transform-how-to-yokai-shift/, https://fextralife.com/nioh-2-guide-to-guardian-spirits-soul-cores/?query-0-page=3&cst, https://www.playstation.com/en-fi/editorial/8-new-things-you-will-be-doing-in-nioh-2/, https://www.gadgetpilipinas.net/2019/09/5-new-things-we-learned-from-our-tgs-2019-nioh-2-hands-on-session/3/
- Burst Counters: https://www.gamerevolution.com/?p=638165, https://twinfinite.net/guides/nioh-2-parry-counter-guide/, https://www.gamepur.com/guides/everything-you-need-to-know-about-burst-counter-in-nioh-2, https://ethugamer.com/nioh-2/nioh-2-burst-counter-guide/, https://gamefaqs.gamespot.com/boards/241160-nioh-2/78521106?page=2, https://steamcommunity.com/app/1325200/discussions/0/4265444591469826954/?l=czech
- Soul Cores: https://nioh2.wiki.fextralife.com/Yokai+Skills, https://www.polygon.com/nioh-2-guide/2020/3/13/21175247/soul-cores-yokai-fusion-fragments-shiftling-skill-points/, https://www.gameskinny.com/tips/nioh-2-soul-core-guide-everything-you-need-to-know/, https://www.psu.com/news/nioh-2-walkthrough-combat-explained/, https://cosmeticszik.weebly.com/blog/nioh-2-difficulty
- Beginner guide (Anima, Scampuss, stealth, guardian/shift): https://steamcommunity.com/sharedfiles/filedetails/?l=swedish&id=2432415046
- Dark Realm: https://waytoomany.games/2020/04/01/review-nioh-2/
- Character creation: https://nioh2.wiki.fextralife.com/Character+Creation, https://twinfinite.net/guides/nioh-2-how-to-change-character-appearance/, https://attackofthefanboy.com/guides/nioh-2-change-appearance/186, https://Www.thegamer.com/nioh-2-how-change-appearance/
- Mythology/history: https://sevenswords.uk/nioh-2-real-history/, https://sevenswords.uk/nioh-2-story-explained-timeline-lore-key-events/, https://nioh2.wiki.fextralife.com/Bosses, https://nioh2.wiki.fextralife.com/Enemies, https://shapes.inc/fandom/nioh/yokai-bestiary, https://shapes.inc/fandom/nioh-2-the-complete-edition, http://tvtropes.org/pmwiki/pmwiki.php/Characters/NiohEnemiesAndBosses
- Regions/missions/world: https://www.ludo.guide/guide/nioh-2/hub-and-overworld-2, https://noisypixel.net/nioh-2-review-ps4/, https://thedrastikmeasure.com/2021/03/14/nioh-2-the-complete-edition-pc-review/, https://steamcommunity.com/app/1325200/discussions/0/5760637065633341605/?l=latam, https://gamefaqs.gamespot.com/boards/241160-nioh-2/80785439
- Underworld/Depths: https://nioh2.wiki.fextralife.com/The+Underworld, https://sevenswords.uk/nioh-2-how-to-prepare-for-the-underworld/, https://gamefaqs.gamespot.com/boards/305939-nioh-2-the-complete-edition/80496657
- DLC: https://nioh2.wiki.fextralife.com/DLC, https://www.gamerevolution.com/guides/647553-nioh-2-dlc-release-date-tengus-disciple-ps4, https://www.gamerevolution.com/guides/654432-how-to-access-nioh-2-dlc-where-is-tengus-disciple
- Dev interviews / design philosophy: https://filmstories.co.uk/features/masocore-the-making-of-the-nioh-series/, https://www.pcgamesn.com/nioh-2/nioh-2-character-customisation?tw=PCGN, https://www.shacknews.com/article/122257/nioh-2-the-complete-edition-interview-with-producer-fumihiko-yasuda?amphtml=1, https://www.thegamer.com/team-ninja-interview-fumihiko-yasuda-nioh/, https://www.vg247.com/2018/06/13/nioh-2-will-character-creator-wont-set-protagonist/, https://gamefaqs.gamespot.com/boards/241160-nioh-2/79248324, https://www.gamespot.com/articles/nioh-2-embraces-its-dark-side-while-enhancing-the-/1100-6473500/
- Prior work this builds on: PR #882, `docs/research/NIOH-SYSTEMS-2026-10-23.md` (Nioh 1 systems)
