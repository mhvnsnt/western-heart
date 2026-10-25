# Yakuza Kiwami 2 / Kiwami 2 (Legacy) / Yakuza 0 — Expanded Research
**Date:** 2026-10-23
**Status:** PUBLIC-SOURCE RESEARCH ONLY. No Steam file pull was possible from this machine (no access to the owner's Steam library or game files here). No claims in this doc are faked or inferred from file data; everything substantive is cited. This doc BUILDS ON PR #883 (`docs/research/YAKUZA-KIWAMI-2026-10-23.md`, Kiwami 1) and does not repeat it — see Section 0 for the explicit diff.
**Games:** Yakuza Kiwami 2 (Steam app 927380), Yakuza Kiwami 2 (Legacy) (same app, storefront label — see Section 0), Yakuza 0 (Steam app 638970)

## Owner instruction (verbatim)
- *"Yakuza Kiwami 2 (Legacy): story and heart and mind inside and Japanese story building and culture"*
- *"Yakuza 0: same as other Yakuza games"*
- *"Yakuza Kiwami 2: same reason"*

"Heart and Mind Within" = WH's Devil Within-style 3D beat-em-up story mode (see MEMORY.md).

---

## Section 0: What these three add over Kiwami 1 (context)

A note on naming: "Yakuza Kiwami 2 (Legacy)" is how the Steam storefront labels the original 2019 Kiwami 2 release (app 927380) — it is not a separate game from Yakuza Kiwami 2. The Gamivo/instant-gaming listings for "Yakuza Kiwami 2 Legacy 2019 (PC)" all resolve to Steam app 927380, released May 8–9, 2019 by Ryu Ga Gotoku Studio / SEGA (https://steamscore.io/game/yakuza-kiwami-2-927380).

What is genuinely NEW here vs. PR #883's Kiwami 1 research:

1. **Dragon Engine.** Kiwami 1 was a PS3/PS4 cross-release built on the old engine; Kiwami 2 (2017 JP / 2018 WW, the second Dragon Engine game after Yakuza 6) is the engine transition — seamless exploration↔combat, real simulated physics, ragdoll enemies, enterable interiors. This is the single biggest technical delta. (https://www.vintageisthenewold.com/faq/why-is-yakuza-kiwami-2-so-different)
2. **Majima Saga:** Kiwami 2's all-new 3-chapter playable-Majima side campaign — the direct counterpart to Kiwami 1's "Majima Everywhere" addition, but structurally different (a gated side-campaign on the title menu, not an in-world stalker system). (https://yakuza.fandom.com/wiki/Yakuza_Kiwami_2)
3. **Yakuza 0's dual-protagonist + style-switching combat:** two playable leads (Kiryu/Majima) with 3 mid-combat-switchable fighting styles each, plus a hidden 4th Legend style. None of this existed in Kiwami 1's research scope.
4. **Business-management minigames** (Real Estate Royale, Cabaret Club Czar) — full management sims with rival-boss structure, tied directly into character power progression. A first for the research docs.
5. **Money-as-XP economy:** yen literally buys your stats; 1980s bubble-economy theming as a game mechanic, not just set dressing.
6. **Substory/chapter craft at scale:** 100 substories in 0, ~70 in Kiwami 2, chapter-gated; plus documented RGG writing philosophy (Yokoyama on main/side-story pacing balance; novelist Hase Seishu's realism editing pass).
7. **Two-city structure** (Kamurocho + Sotenbori) mirroring two protagonists — a reusable story-architecture pattern.

---

## 1. Dragon Engine (Kiwami 2)

### [RESEARCHED]

- **What it is:** Kiwami 2 is a ground-up remake of Yakuza 2 in the Dragon Engine, the same engine as Yakuza 6: The Song of Life — "seamless transitions (no loading screens!) between battles or when entering or leaving buildings," plus re-recorded voice acting and cutscenes. (SEGA official marketing via https://www.gamestop.com/video-games/playstation-4/products/yakuza-kiwami-2---playstation-4/174062.html?sku=10160714.html)
- **Why RGG built it (dev quote):** Battle director Nakamura (AUTOMATON interview with Like a Dragon programmers): pre-Dragon Engine games used a cheat — "the thug who attacks you in the street and the thug who actually fights you in the battle were different people... we sneakily swapped them to make it appear seamless." Kiwami and earlier used this method. The Dragon Engine was built so the team "could use the same characters for both battles and adventure sections." (https://automaton-media.com/en/interviews/like-a-dragons-programmers-talk-about-the-struggles-involved-in-making-game-breaking-mechanics-like-kiryus-dragon-resurgence/)
- **Graphics goal:** The studio's main goal was visual — Oda: "When we switched to the Dragon Engine for Yakuza 6, we pushed the memory to the limit to make Kamurocho look as beautiful as possible"; later titles cut memory (Infinite Wealth's Kamurocho runs on half of Yakuza 6's memory). (Same AUTOMATON interview.)
- **Why they keep it instead of UE5:** Technical manager Yutaka Ito — the Dragon Engine concentrates resources on RGG-specific functions, so "new features can be added quickly. If you are using a general-purpose engine, you can send an email to support and get a response in about 3 days, but if you ask the programmer next to you, it will only take 5 seconds." (https://www.gamereactor.eu/partnerstuff/newsfeed.php?partner=graingergames&id=1373963)
- **Physics change:** Pre-DE physics were "canned"; the Dragon Engine moved to simulated physics with organic knockdowns — enemies ragdoll in combat, loose props (bikes, traffic cones) react to collision instead of being glued to the floor, and real-time destructive environments (break windows, knock shelves over). The canonical example: start a fight on the street, run into an M Store, continue fighting indoors, wreck the store. (https://www.resetera.com/threads/yakuza-lad-interview-roundup-from-tgs-2022-kenzan-never-getting-remade-overseas-talk-unreal-en-ishin-changes-8-story-hints-je-crossover.641223/page-3 ; https://www.resetera.com/threads/yakuza-kiwami-2-demo-out-on-jp-psn.7489/page-3)
- **No invisible walls:** Fights can be fled — "you can just run away" and the crowd gives way; fights can carry into convenience stores and eateries. Kicked/knocked items can damage enemies. (https://backloggd.com/u/Lexa_/review/415225/ ; https://www.resetera.com/threads/yakuza-kiwami-2-demo-out-on-jp-psn.7489/page-3)
- **Combat trade-offs observed by players:** Kiryu went from multiple switchable styles (0/Kiwami, including Legend) down to one refined style in the DE games; Yakuza 6 shipped without weapon storage, which Kiwami 2 addressed ("storing weapons mid-fight" returned, plus environment-specific heat actions and ally-assist heat actions). Combat feels weightier than the "arcadey" old titles. (https://backloggd.com/u/SerialK86/review/3596036 ; https://rageworks.net/slicks-nit-picks-yakuza-kiwami-2/)
- **Heat Actions:** Kiwami 2 carries over Yakuza 6's heat system with new environment-specific and ally heat actions, and re-recorded cutscenes. PC version adds 4K, unlocked framerates, customizable controls. (https://www.gamivo.com/product/yakuza-kiwami-2?glv=dy8lq0ou)
- **Minigames ported forward:** the Cabaret Club sim from 0 returns (with fan-favorite hostess Yuki), the Clan Creator from 6 (with NJPW stars Keiji Mutoh, Masahiro Chono, Riki Choshu, Genichiro Tenryu, Tatsumi Fujinami), plus new additions: Golf Bingo, arcade Virtual-On, SEGA's Toylets. (https://en.wikipedia.org/wiki/Yakuza_Kiwami_2)

**Transfers to WH:** the seamless battle/adventure character model (same actor object across explore and combat — no swap cheat) is the cleanest possible beat-em-up architecture; simulated-physics knockdowns + ragdoll + breakable interiors are exactly WH's "extra physics, partial ragdoll" direction; fleeable fights = no hard arena locks, useful for Devil Within-style open stages.

### [AWAITS FILE PULL]
- Actual Dragon Engine data formats (archive/container structure), physics/ragdoll parameter tables, heat-action script format and trigger conditions, cutscene choreography files, interior-destruction object data — all require app 927380's files on the credentialed machine.

---

## 2. Yakuza 0's systems

### [RESEARCHED]

- **Dual protagonists, two cities:** Kiryu in Kamurocho (Tokyo) and Majima in Sotenbori (Osaka), chapters alternating between them across 17 chapters (16 + Finale "Black and White"). Full chapter list documented at (https://gamefaqs.gamespot.com/ps4/816306-yakuza-0/faqs/74451/glossary-of-terms).
- **Style-switching combat:** Each has 3 base styles, switchable mid-combat. Kiryu: **Brawler** (balanced light/heavy mix), **Rush** (rapid-fire flurries, fast enemies), **Beast** (raw strength; auto-picks up environmental weapons like bikes and signs). Majima: **Thug** (takedowns, throws, counters), **Slugger** (baseball bat — near-invincible vs. knife users, blocks everything), **Breaker** (breakdancing-inspired; the triple-spin spam clears rooms). (https://www.segalization.com/2016/12/15/kiryu-majima-fight-style-new-yakuza-0-trailer/ ; https://gaming-age.com/2016/12/new-yakuza-0-ps4-battle-trailer-pulls-no-punches/amp/ ; https://manualdobruxo.com.br/yakuza-0-game-guide-how-to-actually-rule-1980s-kamurocho-without-losing-your-mind-1gz1)
- **Hidden 4th style — Legend:** Completing the two business storylines unlocks locked portions of the standard skill trees AND a hidden fourth "Legend" style, where money is pumped directly into health/defense/attack to reach "completely broken levels of power." (https://www.noobfeed.com/articles/yakuza-0-directors-cut-beginners-guide)
- **Money is XP:** There is no XP — yen buys HP, strength, and new attacks/moves. Skills climb into the billions of yen; the 1980s bubble economy is a mechanic. You can throw ¥100k into the air to scatter civilians and enemies and walk past fights. (https://buymeacoffee.com/carldexter/yakuza-0-enjoy-glitz-glamour-1980s-japan-yakuza-style?l=en)
- **Real Estate Royale (Kiryu, from ch. 5):** Buy and manage properties across Kamurocho to overthrow the **Five Billionaires**; area-by-area territory takeover, staff management, and rival-boss challenges resolved through minigame duels. "Can make billions" — the economy runs on yen, so it's worth playing. (https://thegamer.com/yakuza-0-zero-beginner-tips/)
- **Cabaret Club Czar (Majima, from ch. 7, Club Sunshine):** Pre-night prep — dress/customize hostesses, partner with businesses — then run the club live: match the right hostess to each customer's type to maximize spend, keep customers happy; special training sessions level up S-Rank hostesses via dialogue-choice quizzes; rival-club battles vs. the **Five Stars of Sotenbori** are one-on-one profit duels where the highest-earning club wins the area, awarding the rival's platinum hostess + a lump sum. (https://www.trueachievements.com/game/Yakuza-0/walkthrough/15 ; https://thegamer.com/yakuza-0-zero-beginner-tips/)
- **Substories as business fuel:** Regional substories recruit security staff (real estate) and top-tier hostesses (cabaret). 0 has **100 substories** (60 Kiryu / 40 Majima), chapter-gated, all clearable in post-game Premium Adventure; rewards include gear (Encounter Finder, Trouble Finder map icons, French Wallet money boost), weapons, and 200k+ EXP-equivalents each early on. They make up ~40% of the completion list. (https://md-eksperiment.org/en/post/20260107-yakuza-0-all-100-substories-chapter-by-chapter-checklist-locations-rewards-and-platinum-path)
- **Completion Points (CP):** Earned by eating at restaurants, finishing substories, even walking certain distances; spent with the clown NPC at the shrine/temple (Bob Utsunomiya) on perks like Bottomless Stomach and Dash upgrades — a meta-layer that rewards engagement with the world itself. (https://manualdobruxo.com.br/yakuza-0-game-guide-how-to-actually-rule-1980s-kamurocho-without-losing-your-mind-1gz1)
- **Mr. Shakedown:** A recurring super-enemy who drains your money when he beats you — the money-economy made into a combat mechanic. (https://gamefaqs.gamespot.com/ps4/816306-yakuza-0/faqs/74451/glossary-of-terms)

**Transfers to WH:** mid-combat style switching is directly applicable to WH's style/moveset system (e.g., stance-switching per fighter or "Mad Dog" equivalents); money/upgrade economy maps to any progression currency; the business-sim + rival-boss structure is a template for non-combat progression modes in Heart and Mind Within; CP is a good model for rewarding world interaction outside fights; substory-gated staff/hostess recruitment = side-content feeding core power.

### [AWAITS FILE PULL]
- Style-switch input mapping and per-style movelists/frame data, money-cost balance tables, Real Estate/Cabaret sim logic and rival-AI tables, CP reward tables, substory trigger data — all require app 638970's files.

---

## 3. Japanese story building (structure + technique only — WH canon is its own)

### [RESEARCHED]

- **Chapter format:** Kiwami 2 runs 16 titled chapters (e.g., "Letter of Blood," "The Dragon of Kansai," "Osaka Castle," "Decision"); Yakuza 0 runs 17 (16 + Finale). Chapters are hard narrative gates — substories, businesses, and areas unlock per chapter. (https://yakuza.fandom.com/wiki/Yakuza_Kiwami_2 ; https://gamefaqs.gamespot.com/ps4/816306-yakuza-0/faqs/74451/glossary-of-terms)
- **The Majima Saga (Kiwami 2's new-story technique):** 3 chapters starring Majima as a second playable lead, unlocked after main-story chapters 5/8/11 and launched from the title menu (separate from the main save); bridges the gap between Kiwami and Kiwami 2 (leaving the Tojo, founding Majima Construction) and gives closure to a Yakuza 0 thread (what happened to Makoto). No EXP/skill upgrades in this mode; money earned can transfer to Kiryu; no substories. (https://gamefaqs.gamespot.com/ps4/218734-yakuza-kiwami-2/faqs/76366/the-majima-saga-walkthrough ; https://trophieshunter.com/games/yakuza-kiwami-2-xbox/achievements/the-majima-factor ; https://axmn.co.uk/narrative-analysis-yakuza-kiwami-2/)
- **Main/side-story pacing as a design discipline (Yokoyama, RGG Studio head):** "When it comes to the side stories and the main stories, there is a lot of calculation that goes into it to make the story flow very well. If the main story is in a serious mood with very much high tension, we don't want to have a silly side story that would remove that mood overall." Side stories exist to add character depth when the main story gets serious; minigames are likewise chosen to fit the setting, not randomly. (https://www.ungeek.ph/2023/07/rgg-studio-had-no-idea-like-a-dragon-side-stories-were-seen-as-silly-outside-japan/)
- **Theme echo:** Each game's substories reflect its core theme — 0's substories drip with bubble-era excess; Yakuza 5's with its "dreams" theme. The side content is a mirror of the main theme, not filler. (Same source.)
- **Realism editing:** Scenarios are written in-house (lead writer Masayoshi Yokoyama), then edited by novelist Hase Seishu (underground crime novels) for realism and emotional truth — producer Kikuchi: "he edited it and pointed out instances where things weren't realistic or when a character's emotions didn't fit in." Substories are written alongside the main plot to keep tone consistent. (https://tigogardenofmadness.substack.com/p/yakuza-and-no-longer-running-away)
- **The formula skeleton:** introduce the big players → reveal the central crime → a long middle of building power and unraveling the conspiracy → a final showdown that "rocks every time, just from an emotional standpoint." Protagonist-splitting (0's two leads, 5's five) with per-character chapter blocks that converge. (https://noescapevg.com/year-of-games-7-yakuza-5-remastered/)
- **Real-life-based cities:** Kamurocho is modeled on Tokyo's Kabukichō; Sotenbori on Osaka's Dotonbori — dense, walkable, real-world districts rebuilt as game levels. (https://www.slashskill.com/yakuza-series-review/)
- **Long-arc character writing:** Kiwami 2's main story is read as Kiryu's slow-burn character development — the payoff of the Majima Saga and 0's Majima arc only lands because the franchise developed the character over multiple entries. (https://axmn.co.uk/narrative-analysis-yakuza-kiwami-2/)

**Transfers to WH:** chapter-gated substory pacing matched to main-story tension; "theme echo" side content; a second-protagonist side campaign (Majima Saga pattern) as the template for multi-fighter story branches in Heart and Mind Within; real-district-modeled arenas for Japanese flavor; the alternate-chapters dual-lead structure as the skeleton for per-character beat-em-up campaigns.

### [AWAITS FILE PULL]
- Chapter event scripts, substory data tables and dialogue files, cutscene direction/camera data, localization diffs (JP vs EN) — require both games' files.

---

## 4. What differs from Kiwami 1's research (explicit diff vs PR #883)

1. Kiwami 2 = **Dragon Engine**; Kiwami 1 = old PS3-era engine. Every seamlessness/physics/ragdoll/enterable-interior finding in Section 1 is new.
2. Kiwami 2's new content = **Majima Saga** (gated 3-chapter side campaign); Kiwami 1's = Majima Everywhere (in-world stalker). Different systems, different lessons.
3. Yakuza 0's **dual protagonists + 6+1 styles with mid-combat switching** — entirely outside Kiwami 1's scope.
4. **Business sims** (Real Estate Royale / Cabaret Club Czar) and the **money-as-XP economy** — new research area.
5. **Completion Points** meta-layer and **Mr. Shakedown** money-combat mechanic — new.
6. **Substory craft at documented scale** (100 in 0, ~70 in K2) with Yokoyama's pacing philosophy and Hase Seishu's editing pass — PR #883 covered Kiwami 1's substories; this is the writing-process layer behind them.
7. **Two-city / two-protagonist mirroring** (Kamurocho/Sotenbori) as story architecture.

---

## CULTURE NOTE — craft to learn, not content to copy

Everything in Section 3 is **storytelling technique**: chapter gating, tension-matched side content, theme-echo substories, realism-editing passes, real-district level building, long-arc character payoffs. WH's canon — Tong-Nou, the Nine Souls, the Five Lands, the Trial — remains the only content source. Do not lift yakuza-clan plots, Japanese organized-crime tropes, or specific substory scenarios into WH; what transfers is the *machinery* (how stories are paced, gated, and mirrored), never the *material*.

---

## Extraction plan for the credentialed machine

When the owner authorizes the pull (they own these on Steam per the standing game-ownership rule — confirm with owner before downloading):

1. **Targets:** Steam apps **927380** (Yakuza Kiwami 2) and **638970** (Yakuza 0) via the credentialed machine's Steam install.
2. **Dragon Engine priorities (927380):** archive/container format + extractor (check the RGG modding community's open-source tools, e.g. Parless-class `.par` extractors on GitHub — verify on the machine, do not assume names); physics/ragdoll parameters; heat-action scripts and trigger tables; cutscene choreography data; interior-destruction object lists; voice-line re-record metadata.
3. **Yakuza 0 priorities (638970):** per-style movelist and frame-data tables; style-switch input mapping; money-balance/XP-cost tables; Real Estate Royale and Cabaret Club Czar sim logic + rival AI; Completion Point reward tables; substory trigger/dialogue data; chapter-gate tables; Mr. Shakedown spawn/loss logic.
4. **Story pipeline (both):** chapter event scripts, substory data tables, JP/EN localization diffs for the writing-process study.
5. **Storage:** large files go to Releases/external per the game-ownership rule — not local disk.
6. **Output:** extraction reports to `docs/research/` in mhvnsnt/western-heart; findings feed the moveset library system and the Heart and Mind Within story-mode design docs.
