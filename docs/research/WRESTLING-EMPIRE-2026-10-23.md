# Wrestling Empire — Systems Research for Heart and Mind Within

**Date:** 2026-10-23 · **Game:** Wrestling Empire (MDickie, solo developer) · **Platform target:** Steam (AppID 1620340; owner owns it, account vil3m, 71.4 hours)
**Owner instruction:** "Diverse wrestling and world, perfect for the heart and mind within"
**Status marker:** Every section below is labeled **RESEARCHED** (public sources, cited) or **AWAITS FILE PULL** (needs the Steam build from this VM or any machine with Steam access). Nothing was faked — no game files were available to this VM (no Steam credentials), so no extraction was performed.

---

## 1. What the game is (RESEARCHED)

Wrestling Empire is the 2021 flagship of Mat "MDickie" Dickie, a one-person development operation in Lincoln, UK — he has been the most prolific solo wrestling-game developer for over two decades (Hardy Boyz Stunt Challenge, Wrestling Revolution 3D, Weekend Warriors MMA, Hard Time, School Days). The official store copy describes it as "the lightweight champion of mobile wrestling… the fun first with no loading times" and the standard install is a mere ~286 MB, built for speed over visual fidelity (sources: official App Store listing; dailyddt.com review, 2022-06-22; estate.w1wrestling.com interview, 2021).

The manual itself confirms the build target: **v1.7.8 "Rebuilt in the latest version of Unity for enhanced compatibility with the latest hardware"** — the game is a Unity title, which governs the whole extraction plan in §7 (source: official manual v1.8.0, http://mdickie.com/guides/wempire.pdf).

---

## 2. Why the wrestling is "diverse" (RESEARCHED)

### 2.1 Match-type and rules variety

Exhibition mode ships a large catalog of match types and rule sets (sources: official manual v1.8.0; community guide page.genspark.site; Steam news for app 1620340). Documented items:

- **Standard formats:** singles, tag team (2+ per side), triple threat / fatal 4-way, battle royal, handicap, "Most Falls Wins", "War" matches (multi-team elimination), Royal Rumble-style "Intervals" entries, "Clockwork Carnage" (Most-Falls + Intervals hybrid, added v1.8.0).
- **Gimmick stipulations:** Hardcore / No-DQ (career Hardcore matches scatter extra weapons around the ring, v1.7.9), steel cage (4-sided and 6-sided), First Blood (ground attacks aim for the head in this rule set, v1.7.8), Ironman (timed most-falls), Last Man Standing (10-count), Furniture Smash / Buried Alive (win by putting opponent through specific furniture), MMA cage with "Ropeless Ring" Bloodsport-style matches appearing often in the MMA promotion, "Christmas Chaos" (gift-opening variant), Bull Rope and Dog Collar gimmicks (v1.6.2).
- **Combat style modifiers:** v1.6.2 added "Combat Style" options that can **forbid strikes or grapples entirely** — the same combat engine with toggled subsystems, a cheap way to make two matches feel different.
- **Set dressing:** water levels can be applied to ANY venue in exhibitions; weapons/props lists per venue are reset on venue change; larger "Epic Arena" for PPVs with interactive ramp/stage/video screens (v1.6.2).

Note: **Hell in a Cell is NOT vanilla** — it exists as a Steam Workshop mod (steamcommunity.com, mod listing). Keep it out of any vanilla-only claim.

### 2.2 Roster and promotion diversity

350 wrestlers spread over **11 rosters** (manual v1.8.0; App Store). Each promotion has a distinct stylistic identity (estate.w1wrestling.com interview):

| Promotion | Flavor |
|---|---|
| All American Wrestling | 1980s WWF |
| Federation Online | Modern WWE |
| Weekend Warriors | UFC/MMA |
| Rising Sun Puroresu | Japanese wrestling |
| Maple Leaf Grappling | Jim Crockett / technical |
| Super Lucha Libre | Mexican lucha |
| Strong Style Wrestling | ECW |
| Wrestling Revolution | MDickie's own originals |
| Wrestling School | Developmental / indie training school |
| Hollywood | Movie-crossover wrestlers |
| Legends | Retired greats / Hall-of-Fame destination |

Character names are pun-based parodies (Oliver Gold = Kurt Angle, Hank Slogan = Hulk Hogan, Mat Showman = Macho Man, Brad Goodman = Bret Hart) — relevant because WH also needs parody-safe naming conventions (sources: dailyddt.com; estate.w1wrestling.com).

The 11th roster, Legends, is where characters land after retiring with a successful career — roster placement itself is a progression mechanic, not just a filter (manual v1.8.0, "Retirement" section).

### 2.3 Move variety and grapple system

Wrestling Empire's combat is explicitly modeled on the AKI/THQ N64 lineage (No Mercy, WrestleMania 2000): freestyle grappling where **Grapple + direction + Attack/Run/Pick-Up selects a move from the wrestler's own moveset**, with corner overrides (hold toward = lift to top turnbuckle, away = drag out), Focus to turn front/back, transitions into holds/pins via "Final Destinations", and reversals computed from Skill levels, size difference, and struggle direction. Ground grapples, lying holds, and pick-up moves exist as separate positions (sources: official manual v1.8.0; magicgameworld.com grappling guide; thefamicast.com Switch review).

Key systems-level points:

- **No canned combos.** Matches run on what the store copy calls **"freestyle animation"** — bodies collide, tumble, and react procedurally rather than through canned sequences (isthereanydeal.com store summary; oyunclubnet review). MDickie's own update notes reference procedural detail like tethers (upper-body tethers can tug a distant opponent closer, v1.7.x notes), limb-loss affecting climbing/grappling, severed limbs, holds falling apart if the required limbs are missing. The animation core is **procedural + code-driven**, not a library of motion-captured clips — this is the single most important extraction caveat (see §7).
- **Taunt to attempt finisher early** (with high failure chance) — a risk/reward call the player makes mid-match (manual v1.8.0).
- **Adrenaline/momentum:** the thin yellow meter under health tracks positive momentum; when filled, an **"adrenaline rush"** makes the wrestler temporarily ~10% stronger in every respect, and any move triggered becomes a special finisher (if available) or a stronger version (manual v1.8.0).
- **Six attributes:** Popularity, Strength, Skill, Agility, Stamina, Attitude. Skill drives counters; Strength drives damage and power moves; Agility gates springboards/jumps; Stamina drives health recovery rate and injury/tap-out resistance; Popularity gates adrenaline rushes and comebacks; Attitude (a morality balance) drives betrayal/trouble events (manual v1.8.0).
- **Reversals:** holding GRAPPLE during an incoming attack raises parry/counter odds; pressing GRAPPLE on the ground raises odds of popping up directly into a move (manual v1.8.0).

### 2.4 AI behavior (RESEARCHED)

- Difficulty tiers exist; **"Extremely Hard" is gated behind Pro purchase** and the game periodically challenges the player to raise difficulty (manual v1.8.0).
- Changelogs show AI tuning history: "Improved AI attacks at the correct range" (v1.7.8), "The AI no longer stops fighting against unconscious wrestlers and still tries to end the match" (v1.7.7), "Improved AI climbs the turnbuckles more successfully" (v1.7.7), "AI is half as likely to leave the ring for no reason" (v1.8.0), near-falls scale with difficulty and match type (v1.7.9), hardcore referees track active competitors (v1.7.2).
- Opponents also have per-character behavior from stats (Skill → counter odds) and from the booking layer (see §3.3).
- **AWAITS FILE PULL:** exact AI decision-tree/utility weights live in the Unity C# assemblies (Assembly-CSharp.dll) — not recoverable from public sources.

---

## 3. How it builds its world (RESEARCHED)

### 3.1 Career mode: weekly calendar skeleton

Each week the player is **assigned one match** they must win to raise profile and attract contract offers from major promotions. They start as a trainee in Wrestling School (pays no money; fame capped at 70%) and work up. Past/future dates are browsable on a calendar; the control method used to "Proceed" becomes the controlled character. After working at each promotion, the player unlocks the privilege of **inheriting the status of anyone, anywhere** — a prestige mechanic that lets a completed career become a new start (source: manual v1.8.0, "Careers" section).

### 3.2 Contracts, money, and self-improvement

- Contract negotiations are a **"battle of wills"** over pay-per-appearance, weeks, and clauses — some clauses are favorable (creative control: change attire/moveset, hire partners) and some are unfavorable (the "Enhancement Talent" clause: only paid if you lose). Counter-offers are interactive (manual v1.8.0; magicgameworld.com).
- Money is **a high score, not a resource**: weekly expenses scale with bank balance, so even wealthy stars feel pressure to keep working (manual v1.8.0, "Finances"). (The oyunclubnet guide corroborates: trading salary for Creative Control is the optimal early move.)
- Training is interactive and **trade-off based**: gym weights train Strength, bag trains Skill, wall trains Agility, track trains Stamina — but each activity drains health into that stat and can weaken others; gains get harder at high stats and with age; no training = stat deterioration over time (manual v1.8.0, "Self Improvement" + "Health Conscious").

### 3.3 Roaming Empire: the explorable backstage world

Roaming mode is the game's "world": instead of skipping to the match, the player **physically roams a real-time 3D backstage/outside world** and must get through the curtain on time (amber clock = a show is in progress but not your match — you may interfere and face consequences; green clock = your segment, missing it damages reputation). Documented world elements (manual v1.8.0 + Steam update notes):

- **Needs simulation:** sleep anywhere (bed vs. rough affects restoration; stamina gates max restoration), eat/drink (junk food backfires), toilets (needing to go distracts from attacking/grappling; weather-cold damages health, offset by fire), mental health / **Spirit meter** (high spirit enables adrenaline rushes; low spirit risks a **nervous breakdown** where the player literally loses control and becomes violent).
- **Spaces:** backstage area, press conference room (v1.5), podcast studio, TV studio, barber shop, gym, street, studio, suburbs, trailer park (rentable housing cheaper than hotels), airport, subway, houses. v1.8.0 added a 4-way junction, houses, trailer park, cars/vans/bicycles, fires can be deliberately set on flammable objects.
- **NPC social systems:** other wrestlers have dialogue when you linger; you can initiate conversations to propose working with/against them, recruit managers/partners; attitude drops each time you pester someone; friends wave at each other; managers/partners follow you scene to scene; talking to the booker in their office = retire; you can pay for objects you take; strangers cost or offer money; cash spawns on the floor.
- **Danger is real:** wrestlers can be severely injured, disabled, or **die** (accidents, natural causes, drug addiction, suicide, murder — all attested on the game's TV Tropes page; losers of "Loser Leaves" school matches are counted as dead). Injuries also flow from overworking: wrestling a match too long can sideline a character for weeks or end a career (dailyddt.com).

### 3.4 Booking mode: the universe simulation

Booking mode lets the player run an entire promotion. Its systems (manual v1.8.0):

- **Roster management:** edit any gimmick (unless Creative Control blocks), train attributes, rearrange or release talent (releases require a compensation package), ~35 talent is the advised roster size.
- **Hiring:** sign talent from other rosters, buy out contracts, negotiate against their reservations; existing talent renegotiate renewals; rival promoters try to poach your stars.
- **Match quality model:** every action scores toward a **5-star rating** based on combined Popularity, with modifiers — **Skull** (hardcore violence desensitization: diminishing returns on weapon spots), **Clock** (audience boredom over time; no boredom in the final minute of a time limit), **Chemistry** (face/heel conflict engages the audience; rivalries and title stakes "enflame" it), **Balance** (crowd wants a close contest; squashes bore them unless a comeback "shines up" the loser and both hit finishers). This is a readable, implemented version of wrestling psychology — directly reusable.
- **Cards:** 6 segments for TV tapings, 10 for PPVs; order runs under-card → main event, each spot more significant to the final rating; unfilled segments count as if filled; anyone can play/sum/skip.
- **TV ratings and money:** ratings move one notch per week toward the show's score (1-star = 60%, 2 = 70%, 3 = 80%, 4 = 90%, 5 = 100%); PPVs count double. Ticket price = $4 + $1/segment (TV $10, PPV $14), multiplied by attendance; only half the fans show up from company/champion reputation — the rest must be **earned during the show**, with attendance building segment by segment. Talent are paid per appearance (full fee per match, half for manager/referee spots); expenses can't exceed 50% of show revenue (v1.7.x patch note).
- **Territories:** the signature "territorial twist" — a world map of territories to claim by setting attendance records, each with local likes/dislikes (adapt your style) and perks (higher revenues in Arabia); invading a rival territory triggers **inter-promotional war** (6-match series, champions auto-entered, winner seizes the territory); spreading too thin weakens all fronts; a brand's following decays if not revisited. Unlocking "golden pen" status (top ratings) grants promotion editing privileges.

### 3.5 Narrative devices

- **Promos/Scripts:** before a match you can script a promo — choose a topic, who speaks, and who receives it. The aggressor **turns heel** and the victim **turns face** if they weren't already opposed — story is produced by the system, not written lines. A "Broadcasting" promo category enables press conferences; WECCL modding supports fully custom `.promo` files with taunts, demeanor, audio, and dialogue templating (`$name1`, pronouns), assigned to vanilla or custom categories, playable in career mode (manual v1.8.0; WECCL v1.3.10 docs, thunderstore.io).
- **Missions, interviews, court cases:** career mode issues missions, shoot interviews (a Joe Rogan Show parody is referenced on the MDickie wiki), and court cases; news is read after each match.
- **Universe persistence:** "Universe" options to restore/backup the entire world state (rosters, title histories, era, aging on/off); save data in `Save.bytes` — PC: `%UserProfile%\AppData\LocalLow\MDickie\Wrestling Empire\Save.bytes`; Android: `InternalStorage/Android/data/com.MDickie.WrestlingEmpire/files/Save.bytes` (manual v1.8.0).
- **Hall of Fame:** retirement is player-chosen (hold exit at calendar); careers are judged on longevity, wealth, win rates, physical prowess.

---

## 4. Mapping to Heart and Mind Within (HMW)

HMW = WH's per-character 3D beat-em-up story campaigns modeled on Tekken 5's Devil Within. Each finding below is a concrete, borrowable technique. Labels: **TECHNIQUE** = what to steal; **HMW FIT** = how it maps.

1. **Weekly calendar skeleton.** Wrestling Empire structures its entire career as a browsable weekly calendar of assigned matches; roaming fills the space between.
   *TECHNIQUE:* chapter calendar. *HMW FIT:* each fighter's HMW campaign is a calendar of weeks; "story weeks" are beat-em-up stages, "show weeks" are arena brawls. Gives a campaign spine without writing a linear script.

2. **Eleven promotion flavors.** Each roster has a genre identity (lucha = aerial, strong style = hardcore, puroresu = technical, MMA = ropeless Bloodsport, school = tutorial).
   *TECHNIQUE:* genre-tagged level packs. *HMW FIT:* HMW stages are tagged by "promotion genre" per Tong-Nou land — a lucha district plays aerial, a strong-style district is weapon-dense. One beat-em-up engine, many flavors, via tags — this is exactly how MDickie gets diversity from one combat system.

3. **Gimmick-match rule sets as stage modifiers.** First Blood, Last Man Standing, Ironman, Furniture Smash/Buried Alive, Bull Rope/Dog Collar tether, Combat Style (no strikes / no grapples).
   *TECHNIQUE:* stage rule sets. *HMW FIT:* HMW boss stages use rule variants — First-Blood boss (make the spirit bleed), Last-Man-Standing gauntlet, Buried-Alive finale (seal the demon), tethered-weapon escort. Rules are cheaper than new mechanics.

4. **The 5-star match-quality model** (hardcore desensitization, boredom clock, face/heel chemistry, balance, rivalry/title stakes).
   *TECHNIQUE:* crowd-psychology scoring. *HMW FIT:* HMW stages are scored by an adapted version: weapon-spam desensitizes the "crowd" (skull), dragging stages bore it (clock), fighting a rival or for a title inflames it, one-sided fights score low unless the underdog shines. This is a ready-made, proven formula for grading beat-em-up performance beyond "time + hits".

5. **Adrenaline/momentum meter** (yellow meter → rush = +10% all stats + finisher unlock).
   *TECHNIQUE:* momentum-as-resource. *HMW FIT:* HMW's momentum meter fills from stylish play; at full, the fighter's super/stand attacks unlock — same shape as the Heat/Oversoul systems, and it directly answers the "attacks feel disconnected" complaint: full meter = your finisher is guaranteed available.

6. **Roaming Empire as a hub world.** Real-time explorable backstage/outside world with needs (sleep, food, health, spirit), NPC conversations, shops, consequences for being late.
   *TECHNIQUE:* explorable hub between stages. *HMW FIT:* between beat-em-up stages, the fighter roams a Tong-Nou district hub: talk to NPCs for side fights, eat for stat boosts, sleep to restore health, find cash/props. This is the single biggest world-building lift and it is *the* thing the owner asked about ("world" for HMW).

7. **Spirit meter and nervous breakdowns.** Mental health is a second resource: high spirit = adrenaline advantage; low spirit = you lose control and attack friends.
   *TECHNIQUE:* morale resource. *HMW FIT:* each HMW chapter has a Spirit meter shaped by dialogue choices and stage results; bottoming out triggers a "breakdown" stage variant (harder, chaotic). Ties HMW to WH's Nine-Souls theming.

8. **Promo system with systemic heel/face turns.** Choosing who talks to whom changes alignment; alignment changes match chemistry and booking outcomes.
   *TECHNIQUE:* systemic alignment from dialogue. *HMW FIT:* HMW intro interactions (already a user directive — multiple per matchup) can write to an alignment flag the same way; the flag then modifies stage chemistry/scoring and unlocks alternate story branches.

9. **Injuries, death, and retirement as stakes.** Overwork injures; losers of loser-leaves matches are counted dead; aging deteriorates stats; the Hall of Fame judges a whole career.
   *TECHNIQUE:* persistent consequence layer. *HMW FIT:* optional HMW "hard road" mode — injuries carry between stages, aging across chapters, retirement into the Hall of Fame (which doubles as a character-select legacy screen). Even without permadeath, stage injuries that persist one chapter add the stakes the owner's vision asks for.

10. **Territory invasions as map conquest.** Claiming territories, adapting style to regional tastes, 6-match inter-promotional wars.
    *TECHNIQUE:* territory map between chapters. *HMW FIT:* HMW chapter select is a territory map of the Five Lands; invading a rival's territory triggers a multi-stage "war" series — the Devil Within-style campaign gets a strategy layer for free.

11. **Exhibition cast setup.** Drag-and-drop casting with role assignment (wrestler / announcer / manager / referee) and team separation by position.
    *TECHNIQUE:* stage director UI. *HMW FIT:* HMW's stage-setup tooling (for the user-as-booker) should copy this UX: drop characters into a scene, position = role, no dialog boxes.

12. **Freestyle procedural animation.** Bodies collide and tumble rather than playing canned clips; limb-loss, tethers, and furniture physics are all code-driven.
    *TECHNIQUE:* partial-procedural combat. *HMW FIT:* the owner's standing goal is "Tekken feel + partial ragdoll (Gang Beasts/Human Fall Flat), NOT full ragdoll." Wrestling Empire is the reference implementation of exactly that middle ground — study its collision/tumble/transition layer before building WH's own.

---

## 5. What is genuinely NOT worth borrowing

- The visual bar (Dreamcast-era faces; the dailyddt review notes female and male bodies share geometry) — WH's visual direction is the opposite.
- Controller/UX patterns are touch-first and idiosyncratic; WH's mobile-input law needs its own teardown.
- The pun-name generator approach needs care for WH's canon-grounded naming law — borrow the *mechanism* (name tables), not the jokes.

---

## 6. Extraction plan (AWAITS FILE PULL)

No Steam credentials exist on this VM, so nothing below was executed. This is the concrete plan for any machine where the user is signed into Steam (account vil3m owns the game).

### 6.1 Install layout (to verify on the Steam machine)

- Game path: `<SteamLibrary>\steamapps\common\Wrestling Empire\` (Steam AppID **1620340**, confirmed from steamcommunity.com/app/1620340 URLs).
- Unity player data: `<game>\Wrestling Empire_Data\` — contains `sharedassets*.assets`, `resources.assets`, `level*` files, `Managed\Assembly-CSharp.dll` (game code), `Managed\UnityEngine*.dll`.
- Save data: `%UserProfile%\AppData\LocalLow\MDickie\Wrestling Empire\Save.bytes`.

### 6.2 Tools (all free/open-source)

1. **AssetRipper** (https://github.com/AssetRipper/AssetRipper) — export the Unity build to an editable project: meshes, textures, audio, prefabs, animation clips, scenes (arenas, backstage, roaming world).
2. **AssetStudio / AssetStudio.NET** — fast browser for textures/audio/text assets; dump crowd textures, ring canvases, themes.
3. **dnSpy or ILSpy** — decompile `Assembly-CSharp.dll`: the freestyle animation engine, AI decision logic, match-rating formula, roaming systems, and promo engine all live in code, not in clips. This is the highest-value target.
4. **Unity's own WebExtract / binary2text** (ships with every Unity Editor install) — inspect `data.unity3d`/SerializedFiles if AssetRipper chokes (Unity docs: docs.unity.cn "Analyze built assets").
5. **BepInEx 5.4.21 + WECCL** (thunderstore.io/c/wrestling-empire) — the established mod stack: install, then use WECCL's **character import/export** to dump wrestler definitions (stats, movesets, costumes, relationships) in editable form; WECCL's save-file repairer source shows the `Save.bytes` layout.

### 6.3 Priority asset targets

| Priority | Target | Where | Why |
|---|---|---|---|
| P0 | `Assembly-CSharp.dll` decompile | `Wrestling Empire_Data\Managed\` | Animation/tumble engine, AI, rating formula — the crown jewels; all procedural |
| P0 | Wrestler definitions via WECCL export | In-game export | All 350 wrestlers: stats, movesets, move-category lists (e.g. 'Rear moves'), relationships |
| P1 | Arena + roaming-world scenes | AssetRipper scene export | Backstage layout, 11 promotion arenas, Epic Arena, outside world (street/suburbs/trailer park/airport/subway) |
| P1 | Prop/furniture/weapon list | AssetRipper + WECCL docs | Object behaviors for HMW weapon-dense stages |
| P2 | Costume textures + naming table | `BepInEx\plugins\Assets` conventions (`body_material`, `face_male`, `legs_pattern`…; WECCL docs list ~22 texture names) | Body-reference donors for WH customization suite |
| P2 | Themes/audio | AssetStudio audio dump | Entrance themes, crowd loops |
| P3 | Promo/dialogue tables | DLL strings + `.promo` format docs | Dialogue templating format for HMW intro interactions |

### 6.4 Where it lands in the WH repo

Follow the standing rule (AGENTS.md): everything goes in the repo. Per the disk note (2026-10-23, VM at 86% — do not touch the big workspaces), large dumps do **not** live on disk:

- Extracted text/JSON (wrestler defs, move lists, promo tables): `docs/research/wrestling-empire/` (small, committed).
- Binary assets (meshes, textures, audio, Unity projects): uploaded to a **GitHub Release** on mhvnsnt/western-heart tagged `research-wrestling-empire` — never committed to git, never left on the VM.
- Extraction log + inventory: `docs/decisions/2026-10-23-wrestling-empire-extraction.md`.

### 6.5 What public sources cannot answer (needs the pull)

Exact move counts per wrestler; frame/transition data for the grapple system; the AI's decision weights; the precise 5-star rating formula constants; arena geometry; `Save.bytes` serialization format; whether any animation data exists as clips vs. pure code.

---

## 7. Sources

- Official manual v1.8.0 (primary): http://mdickie.com/guides/wempire.pdf
- Official App Store listing (store copy: 350 wrestlers, 10/11 rosters, roaming, booking): https://backiee.wasmer.app/https_apps_apple_com/me/app/wrestling-empire/id1543750891
- MDickie Builds Wrestling Video Game Empire (interview, promotion list + design philosophy): https://estate.w1wrestling.com/mdickie-builds-wrestling-video-game-empire/
- "Wrestling Empire is a dumpster fire of sheer genius" (career/mode detail, dailyddt, 2022-06-22): https://dailyddt.com/2022/06/22/video-games-wrestling-empire-is-a-dumpster-fire-of-sheer-genius/
- Collecting Asylum review (8/10; promotions, booking): https://www.collectingasylum.com/game-reviews/wrestling-empire
- Grappling systems guide (magicgameworld): https://www.magicgameworld.com/wrestling-empire-combinations-grappling-final-destinations/
- Career/contracts guide (magicgameworld): https://www.magicgameworld.com/wrestling-empire-careers-self-improvement-contracts/
- Switch review (AKI-style controls): https://www.thefamicast.com/2021/01/wrestling-empire-review-switch.html
- Store summary (freestyle animation): https://isthereanydeal.com/game/wrestling-empire/stats/
- WECCL v1.0.6/v1.2.5/v1.3.10 docs (modding: BepInEx 5.4.21, Assets/Overrides folders, costume texture names, custom moves/promos/arenas, character import-export): https://thunderstore.io/c/wrestling-empire/p/IngoH/WECCL/
- WECCL changelog (v1.7.x: custom strikes/grapples, promo categories, career promos): https://thunderstore.io/c/wrestling-empire/p/IngoH/WECCL/changelog/
- Steam Workshop mods (Essential mods; Hell-in-a-Cell is a mod, not vanilla): https://steamcommunity.com/sharedfiles/filedetails/?id=3522863308 · https://steamcommunity.com/sharedfiles/filedetails/?id=3465676914
- Steam announcements for app 1620340 (patch notes: hardcore refs, cold damage, tethers, promos): https://steamcommunity.com/app/1620340/announcements/?l=indonesian · https://steamcommunity.com/app/1620340/allnews/?l=greek
- MDickie Wiki (Wrestling Empire; Wrestling School; career details): https://mdickie.fandom.com/wiki/Wrestling_Empire · https://mdickie.fandom.com/wiki/Wrestling_School
- TV Tropes: Wrestling MPire (injuries/death, shoot interviews, murders): https://tvtropes.org/pmwiki/pmwiki.php/VideoGame/WrestlingMpire
- Unity "Analyze built assets" (WebExtract/binary2text): https://docs.unity.cn/6000.6/Documentation/Manual/assets-analyze-built-assets.html
- Google Play listing (update notes): https://play.google.com/store/apps/details?id=com.MDickie.WrestlingEmpire&hl=en_GB
- The Grappling Gamer review (career/unlock structure): https://www.merchandiseandmemories.com/the-grappling-gamer-wrestling-emp
