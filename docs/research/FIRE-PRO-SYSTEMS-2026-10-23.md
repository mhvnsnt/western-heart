# Fire Pro Wrestling World — Systems Research: CPU Simulation, Creation Depth, AI Logic Programming

**Date:** 2026-10-23
**Status:** Researched from public community sources only. **No Steam file pull was possible from this VM (no Steam credentials), and none was faked.** Every substantive claim below cites a public source. Anything requiring the actual game files is marked **AWAITS FILE PULL** and moved to the extraction plan in Section 5.
**Owner instruction (verbatim):** *"the ultimate fighting game where you can build almost any character from any fighting game and it'll be like our game style inputs"*

---

## 0. What Fire Pro Wrestling World is (context)

Fire Pro Wrestling World (Spike Chunsoft, Steam app 564230, 2017; PS4 2018) is the entry in the long-running Fire Pro series (SNES Fire Pro X, Fire Pro Wrestling G, Fire Pro Wrestling Returns on PS2, Fire Pro D on Dreamcast). It is famous less for playing matches yourself and more for *watching* them: the CPU logic system lets creators program a wrestler's in-ring behavior so precisely that "simming" CPU vs CPU matches is the game's core loop for a large part of the community. Multiple community sources confirm simmers log hundreds of hours watching simulated matches and betting on outcomes (Steam discussion: https://steamcommunity.com/app/564230/discussions/0/133258593397876151/?l=japanese).

The official store description itself sells this loop: *"REALISTIC SIMULATION — Give your creations personalities with a robust CPU logic system that defines their every action"* (https://gamecompanies.com/games/fire-pro-wrestling-world).

---

## 1. CPU vs CPU Simulation — the match engine

### 1.1 The hidden resources: HP and SP (no HUD)

Fire Pro deliberately ships **no health HUD**. Match state lives in two hidden resources per wrestler:

- **HP (stamina/health):** depleted by taking damage; visible only through animation cues — breathing heaviness, movement speed, sluggishness, collapse. The "breathe" button (LB/L1) restores stamina, and pacing breath breaks is a core mechanic (https://thatdemoguy.wixsite.com/thatdemoguy/fireprowrestlingworld; https://www.culturedvultures.com/fire-pro-wrestling-world-ps4-review/).
- **SP (spirit):** the perseverance resource. It is *not* "ability to do your finisher" — it is resistance to being pinned/submitted in the late match. Community documentation: **below ~25% SP a pin has a chance to succeed (depending on ref position and count speed); at 0% SP a submission is near-guaranteed** (Steam discussion: https://steamcommunity.com/app/564230/discussions/0/1694920442943613088/?l=portuguese).
- **Key design insight:** big offense doesn't just damage the opponent — some moves can *give the opponent spirit*, empowering them to land a reversal and make a comeback. Selling (see Ukemi, §3.4) grants hidden attribute bonuses later in the match (Steam AI & Moveset Guide: https://steamcommunity.com/sharedfiles/filedetails/?id=973746385; https://thatdemoguy.wixsite.com/thatdemoguy/fireprowrestlingworld).

### 1.2 Match pacing / psychology (the AJPW engine)

Matches are built around **All Japan Pro Wrestling-style psychology**: small moves build to medium moves, which build to large moves, which lead to a finish sequence. The engine enforces this with a **counter mechanic** — using medium/big moves too early gets them automatically reversed, and big moves drain your own stamina faster (https://steamcommunity.com/sharedfiles/filedetails/?id=973746385; https://steamcommunity.com/sharedfiles/filedetails/?id=1082409325).

- The guide notes the **medium-damage window is much shorter than people think**; pacing is: feel out with smalls (4–8 light moves typically before the opponent is breathing heavy), then mediums, then bigs, then finish.
- Pacing differs by **wrestling style** (§3.6): Power/Wrestling styles are efficient in short matches and wane late; Heel styles don't get comeback boosts; Fighter builds collapse at heavy damage; Giant builds start the match already gassed; Juniors/Panthers/Vicious are comeback masters who find a second wind when near death.
- **Special skills** can override the default pacing (e.g. Start Dash for fast starts, One-Hit Finisher for squash machines, MMA-style shoot skills for quick KO/submission finishes).

### 1.3 Spirit, selling, bleeding — drama systems

- **Ukemi ("selling"):** a three-number logic setting (defaults 20/25/15) controlling how often a wrestler "takes" an opponent's move cleanly instead of resisting. High early-game ukemi (40+/20+/0) creates comeback wrestlers who lose early and rally late; low ukemi (5/5/15) creates Goldberg-style squash monsters (https://steamcommunity.com/sharedfiles/filedetails/?id=973746385). Selling for your opponent grants hidden attribute bonuses later — the engine literally rewards cooperation.
- **Bleeding:** blood loss degrades Recovery and Breathing, but some wrestlers get stronger — the **Blood** special skill gives +10% to all moves while bleeding (https://www.magicgameworld.com/fire-pro-wrestling-world-special-skill-guide/).
- **Comeback mechanics:** Juniors/Panthers/Vicious styles inherently get near-death comeback boosts; the Over Turn (One-Hit Reversal) skill doubles critical rate when HP is under 10% but spirit is above 30%; Quick Return enables no-sell "pop back up" moments at 5–20% HP with spirit above 60% (https://www.magicgameworld.com/fire-pro-wrestling-world-special-skill-guide/; https://steamcommunity.com/sharedfiles/filedetails/?id=973746385).

### 1.4 How finishes are decided

- **Criticals:** every wrestler has a **Critical type** (Finisher / Striking / Suplex / Submission / Power / Technical). A "Critical!" is an instant-KO/broken-bone outcome — the match is over. Only moves in the chosen category (and only specific moves within it) can critically hit (http://firepro.ewzzy.com/faqs/fpa_edit_mode.txt; https://gamefaqs.gamespot.com/boards/206703-fire-pro-wrestling-world/76846367).
- **Pins and submissions** resolve against the defender's SP, referee position/count speed, and targeted body-part damage (submission finishers are built up by logic that targets the same body part all match — e.g. working the leg for a Figure Four — pins at low/medium damage reduce spirit to set up later submissions (Steam discussion: https://steamcommunity.com/app/564230/discussions/0/1470841715947280936/?l=greek)).
- **Match rating:** the game scores audience satisfaction; a long, hard-fought battle rates well, but a quick Critical finish can also rate well in the right promotion context. The rating responds to *what the audience expects* (https://nightburn.neocities.org/hol/fireprowrestlingworld).

### 1.5 Randomness and drama under the hood

- Logic percentages are **probability tables**, not scripts — the CPU rolls on its logic weights every decision, so the same two wrestlers produce different matches each time ("the match can be a complete dud, or it can be an epic" — Steam discussion).
- Match outcome variance comes from: critical rolls, reversal/counter timing windows, SP attrition curves, ref positioning, crowd/match-rating feedback, and bleed/guts skill triggers.
- **AWAITS FILE PULL:** the exact RNG implementation, critical probability formulas, SP damage formulas, counter-window frames, and referee AI all live in the game binaries and have not been verified from public sources.

---

## 2. Creation depth — edit-a-wrestler taxonomy

### 2.1 Moveset (the deep part)

- **Move pool:** official description cites **"over a thousand devastating moves"** (https://gamecompanies.com/games/fire-pro-wrestling-world). (FPR on PS2 had 1,648 moves and the count grew with patches — https://www.mobygames.com/game/22508/fire-pro-wrestling-returns/.)
- **Moveset slots by position/situation:** Standing (SML/MED/BIG/SML+MED), Running, Counter (run-at), Initiate Grapple, Front Grapple (SML/MED/BIG × up/down/left-right × damage bands), Back Grapple, Irish Whip follow-ups, Corner grapples, Post/dive moves, Opponent Down (Face Up / Face Down × Head / Legs), Opponent Dazed (corner/center), Corner-to-Center attacks, MMA positions (Guard / Mount / Back Mount), Double & Triple Team moves, plus **Performance slots** (pre-match / in-match taunt / post-match appeal) (https://steamcommunity.com/sharedfiles/filedetails/?id=973746385; https://gamefaqs.gamespot.com/ps/197349-fire-prowrestling-g/faqs/5055).
- **Move affinity:** every move is graded A–E for the chosen style — how much stamina it costs to use (not damage, not success rate). Too many C/D/E moves and the wrestler gasses out (https://steamcommunity.com/sharedfiles/filedetails/?id=973746385).
- **Specialties and finisher:** each wrestler designates **4 specialty moves (blue S) + 1 finisher (red C)**. Finishers can be renamed by the creator. Each move slot can also have a **voice** assigned (V1/V2) that plays during the move (Supercheats beginner's guide: https://www.supercheats.com/playstation2/walkthroughs/fireprowrestlingreturns-walkthrough08.txt).

### 2.2 Parameters / stats

**Profile:** name/nickname, size (S/M/L/Fat), class (Heavy/Junior), height, weight, gender, birthdate, country, organization/group, rank, charisma, stance, fight style, return (defensive) skill, critical type, special skill.

**Skill ratings:** Recovery (+ when bleeding), Breathing (+ when bleeding), Spirit (+ when bleeding), Neck/Arm/Back/Leg endurance, Movement Speed, Ascent (turnbuckle) Speed & Style (can't climb / can climb / can run up), Outside Return Count (0–20), Touchwork/Teamwork, Favorite Weapon, Theme Music (https://www.supercheats.com/playstation2/walkthroughs/fireprowrestlingreturns-walkthrough20.txt; https://gamefaqs.gamespot.com/gba/471238-fire-pro-wrestling/faqs/19306).

**Offense/defense parameter pairs (1–10 scale, budget-capped, ~380 total points on a 0–380 scale):** Punch, Kick, Throw, Joint, Stretch, Power, Agility, Arm, Technical, Rough, MMA, Entertain — each with a matching defense parameter (https://www.supercheats.com/playstation2/walkthroughs/fireprowrestlingreturns-walkthrough20.txt).

**Edit points economy:** better critical types cost points (Striking/Submission 30, Technical 25, Suplex/Power 20, Finisher 0); every special skill costs 15 points; better recovery/breathing/spirit cost 10–20 points. Creators spend from a fixed budget, which is how the game balances created wrestlers (http://firepro.ewzzy.com/faqs/fpa_edit_mode.txt; https://gamefaqs.gamespot.com/ps/197349-fire-prowrestling-g/faqs/5055).

### 2.3 Skills/abilities (all 15-pt special skills, trigger → effect)

Documented with trigger conditions and exact effects (https://www.magicgameworld.com/fire-pro-wrestling-world-special-skill-guide/; https://steamcommunity.com/app/564230/discussions/0/1694920442943613088/?l=portuguese):

| Skill | Trigger | Effect |
|---|---|---|
| Stardom | Taunt at 0% stamina | Next attack +25% damage |
| Quick Return | 5–20% HP, spirit >60% | Recover from knockdown 8× faster (no-sell) |
| Over Turn (One-Hit Reversal) | HP <10%, spirit >30% | Critical probability doubled |
| Start Dash | HP >70% | +1 to all offensive parameters |
| Guts | HP & SP at 0% | Submission tap-out rate drops to ~1/20 normal |
| Strikeback | HP <5% (both wrestlers) | +2 to all offensive parameters |
| Finish (One-Hit Finisher) | First/second finisher use | Finisher +150% damage |
| Blood | Bleeding | All moves +10% damage |
| Hardcore | Holding weapon | +3 all offensive/defensive parameters |
| Focus (Concentration) | Passive | Strike/submission/technical critical chance −50% |

### 2.4 Appearance

Hundreds of parts per body zone (face base + sub-parts: eyes, pupils, highlights, lips; chest/waist/arms/thigh/knee/ankle gear; hair; masks/gloves), each with multi-layer color pickers (up to 4 color layers per part), skin tone layers, and **face layering** (added in FPR). Also: referees, rings (mat color, logos, apron), championship belts, and stables/promotions are all creatable. **One outfit per edit** (a known limitation, noted in the Supercheats FAQ). (https://www.supercheats.com/playstation2/walkthroughs/fireprowrestlingreturns-walkthrough08.txt; https://www.arcade-history.com/game/228769/fire-pro-wrestling-world)

---

## 3. AI logic programming — the famous part

### 3.1 The logic table structure

CPU logic is a set of **percentage tables keyed by (situation × opponent damage state)**. For every situation, the creator assigns a percentage to each available action; the CPU rolls against these weights whenever that situation arises. The damage-state columns are:

- **Sml Dmg** — opponent fresh to lightly damaged; opener logic
- **Med Dmg** — opponent can take suplexes now; this window is shorter than most creators expect
- **Lrg Dmg** — opponent spent; finishers and signatures belong here
- **Opp. Condition Critical** — rare; opponent survived a critical or has been beaten far past the finishable point

(https://steamcommunity.com/sharedfiles/filedetails/?id=973746385)

### 3.2 The full situation list (each with its own percentage table)

From the community AI & Moveset Guide (https://steamcommunity.com/sharedfiles/filedetails/?id=973746385):

1. **Initiate Grapple (Standing Attack):** Grapple / Stand Back (stall) / Circle Opponent / Strike SML / Strike MED / Strike BIG / Strike SML+MED
2. **Stand Back (Stall) — grappling techniques:** what to do after winning a tie-up: Grapple SML/MED/BIG (× up/down/left-right directions) / SML+MED / Irish Whip / Front facelock drag (3D grapple)
3. **Circle Opponent (Back Grapple):** rear-waistlock techniques — Back Grapple SML/MED/BIG (× directions) / SML+MED
4. **Irish Whip:** follow-up attacks after throwing the opponent to the ropes
5. **Running / Counter:** running attacks (SML/MED/BIG) and counters against runners (SML/MED/BIG, breathing-based)
6. **Opponent Dazed in Corner:** running corner attacks, post grapples, back-grapple bigs
7. **Opponent Down Near Corner:** Do Not Ascend / Post SML/MED/BIG / Run-Up Turnbuckle
8. **Opponent Down Near Center:** Don't Run / Running attack at downed opponent / Corner-to-Center attack
9. **Opponent Down Face Up:** pick up / roll over / Head MED/BIG/PIN / Legs MED/BIG/PIN
10. **Opponent Down Face Down:** same grid as above
11. **Opponent Dazed Near Corner / Near Center:** post work, rope slingshots from apron
12. **Guard / Mount / Back Mount:** the three MMA position systems (each gives the initiator an execution advantage)
13. **Opponent At Back:** responses/counters when the *opponent* takes your back
14. **Opponent Outside Ring:** tendency to leave the ring to brawl; diving attacks in/out using posts and ropes
15. **Performance:** tendency to use taunts and signature actions in different situations
16. **Priority Attack:** scripted **move sequences** — a Priority Attack move (almost any move, any position) chained into a Follow-Up (any downed-opponent attack: pin, pickup, stomp, submission, MMA position). This is how "finisher → always pin" behaviors are programmed.

### 3.3 Wrestler psychology / tendencies

Eight top-level personality sliders (https://steamcommunity.com/sharedfiles/filedetails/?id=973746385; Steam discussions https://steamcommunity.com/app/564230/discussions/0/1479857071254205051/?l=schinese):

- **Showmanship:** how often the wrestler tosses opponents into corners/outside the ring (higher = more show, less efficient winning)
- **Discretion:** how often they stop to catch breath; facelock-drag direction (high = drag to center, low = drag to corner); dragging opponents away from ropes
- **Flexibility:** willingness to deviate from style / use situational moves
- **Cooperation:** how much they "work with" the opponent (the engine's sportsmanship knob)
- **Outside Return Count:** when they return to the ring (0–20)
- **Touchwork:** tag-team coordination speed
- **Weapons:** hardcore tendencies
- **Second Interference:** manager/second involvement

Starter advice from the community: begin by tuning the three main personality traits (Entertainment/Serious-time/Flexibility equivalents) before touching the deep tables (https://www.supercheats.com/playstation2/walkthroughs/fireprowrestlingreturns-walkthrough08.txt).

### 3.4 Ukemi — programmable selling

Three percentages (default **20/25/15**) = how often the wrestler lets the opponent's offense land clean at each match phase. This is *programmable selling*: high early ukemi builds comeback arcs, near-zero ukemi builds squash monsters. Selling grants hidden attribute bonuses later in the match — cooperation with the opponent is mechanically rewarded (https://steamcommunity.com/sharedfiles/filedetails/?id=973746385).

### 3.5 Fight styles (16) — the logic presets

**Orthodox, Technician, Wrestling, Ground, Power, American, Junior, Luchador, Heel, Mysterious, Shooter, Fighter, Grappler, Panther, Giant, Vicious** — each with style-vs-style effectiveness, affinity grades, and pacing characteristics (comeback boosts, stamina curves). Paired with a **Return (defensive) skill** chosen from the same list — certain fight/return style combinations "jive" and others don't (https://steamcommunity.com/sharedfiles/filedetails/?id=973746385; https://gamefaqs.gamespot.com/boards/206703-fire-pro-wrestling-world/76846367).

### 3.6 The creator workflow (how it's actually used)

The documented community workflow is: build the edit → set styles/skills/parameters → program logic tables → **throw the wrestler into a CPU vs CPU match against a default wrestler of similar status → observe what it does → adjust** ("it's not always a matter of winning or losing, but whether your creation is doing what he should be doing at all times within the squared circle") (https://www.supercheats.com/playstation2/walkthroughs/fireprowrestlingreturns-walkthrough08.txt). This sim-observe-tune loop is exactly the user's own habit (133 hours watching/simulating).

---

## 4. Vision mapping — how this maps to Western Heart

The owner's vision: *"the ultimate fighting game where you can build almost any character from any fighting game and it'll be like our game style inputs."*

Three Fire Pro systems map 1:1 onto three WH pillars:

### 4.1 Deep creation → WH's creation suite (already in progress)

| Fire Pro system | WH equivalent (proposed) |
|---|---|
| Moveset slots by position/situation (standing, running, grapple, back, downed, corner, post) | **The existing Tekken movelist-library plan** — WH's central move library organized by type/position/orientation (owner directive 2026-10-22) becomes the "move pool"; per-fighter creation assembles moves into situation slots |
| Move affinity grades A–E (stamina cost) | Map onto WH's move data: recovery frames / whiff cost per move — moves with bad "affinity" drain the WH stamina/heat economy faster |
| 4 specialties + 1 finisher | WH per-fighter signature slots; finishers as WH super/rage-art equivalents with usage-gated power (cf. Fire Pro's Finish skill: first two uses +150%) |
| Parameters (offense/defense pairs, skill ratings, edit-point budget) | WH fighter parameter sheet: attack/defense pairs per move class, recovery, spirit/awareness, endurance per body region — **with the same point-budget economy** so created fighters stay balanced against each other |
| Special skills with HP/SP triggers | WH "traits" with trigger conditions (e.g. Quick Return → WH no-sell wakeup trait; Guts → submission/pressure resistance at low health; Start Dash → round-start damage buff) |
| 16 fight styles + return skill + critical type | WH fighting-style presets that set baseline pacing, counter windows, and comeback curves per created fighter |
| Appearance parts + one-outfit-per-edit | WH already exceeds this (attire ladders); Fire Pro's lesson is the *part taxonomy* and color-layer system, which WH's customization menus can adopt |

### 4.2 Fight simulation → a NEW WH mode: "Watch mode" (build characters, watch them fight)

This is the mode the user is actually asking for with their 133 hours of evidence:

- **WH needs a CPU vs CPU exhibition mode** where both fighters run AI built from the creation data. The Fire Pro formula to port is not the code but the *architecture*:
  1. **Hidden state:** HP (stamina, shown via animation/breathing cues, no HUD needed) + SP (composure/resolve — pin/combo-break resistance late in the round).
  2. **Logic tables:** per situation (neutral, pressure, opponent downed, cornered, wall-splat, low health…) × per damage state (fresh / hurt / critical) → weighted move-selection percentages, **editable per fighter in the creation suite**.
  3. **Pacing engine:** small pokes → medium launchers → big moves → finish, enforced by counter windows (big moves early get launched/crushed) and a stamina economy.
  4. **Drama systems:** programmable "selling" (ukemi) so created fighters cooperate to build comebacks; special-skill-style triggers (no-sell wakeups, comeback damage buffs, bleeding-equivalent "desperation" states); audience/match-rating scoring.
  5. **Finish logic:** critical-type system (which move classes can KO), SP-gated finish windows, ref/position-aware pin or KO resolution.
- **The sim-observe-tune loop becomes a WH feature:** create fighter → watch CPU vs CPU → adjust logic sliders → re-sim. Fire Pro's community proved this loop sustains hundreds of hours; it is the exact loop the user already lives in.
- **Randomness, not scripting:** logic percentages are probability weights, so rematches differ — "the match can be a complete dud, or it can be an epic." WH's simulation must be stochastic, seeded per match.

### 4.3 WH's Tekken-style input system (player takes control)

The bridge between simulation and play:

- **One moveset, two drivers.** The created fighter's movelist (built in the creation suite from the WH move library) is wired to Tekken-style inputs (direction + button, e.g. f+2, d/f+1, WS, CH) for the human player — preserving the owner's **input-to-move fidelity law** (press 1, left punch comes out, every time).
- **The same movelist is what the CPU logic tables reference** in simulation mode. Fire Pro does exactly this: moves are assigned to input slots *and* to logic-percentage slots; the human uses inputs, the CPU uses logic weights, both draw from the same pool. (In Fire Pro, setting a move's logic percentage to 0% hides it from the CPU but a human player can still find and use it — documented in the AI guide.)
- **Mode switch:** in Watch/Sim mode the fighter runs its logic tables; the moment a player picks up the controller, logic tables go dormant and inputs drive. Fire Pro's match setup already has this concept (1P vs CP, CP vs CP per match — https://gamefaqs.gamespot.com/snes/580142-super-fire-pro-wrestling-iii-easy-type/faqs/72548).
- **What NOT to port:** Fire Pro's grapple-timing minigame input system (lock-up → timing-based move selection) is wrestling-specific and conflicts with the Tekken feel mandate. Port the *AI/logic architecture*, not the *input scheme*.

### 4.4 Concrete first build (proposed, needs owner sign-off)

1. Fighter creation record gains: logic tables (situation × damage-state percentages), psychology sliders (showmanship/discretion/flexibility/cooperation equivalents), ukemi triple, fight style + return skill, critical type, special-skill trait, parameter sheet with point budget.
2. Sim engine v1: HP/SP hidden state, counter-window pacing, weighted move selection from logic tables, ukemi selling, one drama trigger (comeback buff), stochastic rematches.
3. Watch mode UI: pick two created fighters → CP vs CP → watch, with post-match rating and a "tune logic" button that jumps back to the creation screen (the Fire Pro loop).

---

## 5. Extraction plan — when Steam access exists

No game files were pulled for this research. When the owner confirms a Steam copy of Fire Pro Wrestling World (or provides access), the pull targets are:

1. **Managed code (Unity game):** extract `Assembly-CSharp.dll` (and siblings) from the Steam install; decompile/inspect with ILSpy or dnSpy. Targets: match-engine classes (HP/SP handling, critical rolls, counter windows), CPU-logic evaluation (how percentages are rolled per situation), skill trigger checks, AI state machine, match-rating calculation. *Expected file paths under the Steam install's `FireProWrestlingWorld_Data/Managed/` — to be confirmed on pull.*
2. **Move database:** the 1,000+ move table — names, categories, damage values, affinity grades, which moves can critical, animation references. Likely in asset bundles or scriptable objects; community save editors already parse parts of this format (see below).
3. **Edit/save format:** FPWW save files (and Steam Workshop edit files) contain the full creation record — appearance parts, moveset assignments, parameters, skills, and the complete CPU logic tables. The community has partially documented this format via save editors (e.g. the well-known community save editor by Carlz — verify on pull). Dumping a few workshop edits and diffing them is the fastest route to the exact logic-table serialization.
4. **Parameter/point-budget tables:** the edit-point costs for critical types, skills, and stat tiers — needed to replicate the balance economy.
5. **Workshop corpus (optional, high value):** the Steam Workshop hosts tens of thousands of community edits (9,400+ within weeks of launch per https://memeburn.com/gearburn/2017/08/fire-pro-wrestling-world-early-access-review-no-botchamania-here/). A bulk sample of highly-subscribed edits would give us *real, tuned* logic tables to study and to seed WH's default logic presets.

**AWAITS FILE PULL — do not treat as established:** exact RNG/critical/SP formulas, counter-window frame data, referee AI, the full move database, the save-format byte layout, and any Unity asset-bundle contents. Everything in §§1–3 above the "AWAITS FILE PULL" notes is community-documented and cited; everything below that line is a plan.

---

## Sources

- Steam Community Guide — "Fire Pro Wrestling World: AI & Moveset Guide" (the primary CPU-logic reference): https://steamcommunity.com/sharedfiles/filedetails/?id=973746385
- Supercheats — Fire Pro Wrestling Returns Beginner's Guide / walkthrough (CPU logic, specialties/finishers, creation FAQ): https://www.supercheats.com/playstation2/walkthroughs/fireprowrestlingreturns-walkthrough08.txt
- Supercheats — FPR skill/parameter stat tables (Sting, Vader FAQs): https://www.supercheats.com/playstation2/walkthroughs/fireprowrestlingreturns-walkthrough16.txt and https://www.supercheats.com/playstation2/walkthroughs/fireprowrestlingreturns-walkthrough20.txt
- Steam discussion — "What does 'Special skill' do?" (HP/SP definitions, full special-skill trigger/effect list): https://steamcommunity.com/app/564230/discussions/0/1694920442943613088/?l=portuguese
- Magic Game World — Fire Pro Wrestling World Special Skill Guide (fact-checked skill list): https://www.magicgameworld.com/fire-pro-wrestling-world-special-skill-guide/
- firepro.ewzzy.com — FPA edit-mode FAQ (styles, critical types, point costs): http://firepro.ewzzy.com/faqs/fpa_edit_mode.txt
- GameFAQs — Fire Pro Wrestling G translation guide (CPU logic categories, skill costs): https://gamefaqs.gamespot.com/ps/197349-fire-prowrestling-g/faqs/5055
- Steam discussion — "Question for those who prefer to sim matches" (simmer community practices): https://steamcommunity.com/app/564230/discussions/0/133258593397876151/?l=japanese
- Steam discussion — discretion/showmanship settings explained: https://steamcommunity.com/app/564230/discussions/0/1479857071254205051/?l=schinese
- Steam discussion — submission vs impact finishers (logic body-part targeting, pins reduce spirit): https://steamcommunity.com/app/564230/discussions/0/1470841715947280936/?l=greek
- GameFAQs boards — creation-tools Q&A (affinity, return skill, critical ability): https://gamefaqs.gamespot.com/boards/206703-fire-pro-wrestling-world/76846367
- Operation Rainfall review (CPU logic as the creation suite's real draw): https://operationrainfall.com/2018/12/10/review-fire-pro-wrestling-world-2/2/
- Memeburn early-access review (Workshop scale: 9,400+ edits within weeks): https://memeburn.com/gearburn/2017/08/fire-pro-wrestling-world-early-access-review-no-botchamania-here/
- thatdemoguy — FPWW systems writeup (spirit, breath, no HUD): https://thatdemoguy.wixsite.com/thatdemoguy/fireprowrestlingworld
- Nightburn — FPWW review (trifecta of breath/spirit/match rating; simming as main use case): https://nightburn.neocities.org/hol/fireprowrestlingworld
- Cultured Vultures PS4 review (pacing, breathing mechanic, appearance variety): https://culturedvultures.com/fire-pro-wrestling-world-ps4-review/
- Steam Community Guide — FPWW Tips (small→medium→big pacing, stamina micro-management): https://steamcommunity.com/sharedfiles/filedetails/?id=1082409325
- Destructoid early-access review (sandbox nature, edit mode): https://www.destructoid.com/early-access-review-fire-pro-wrestling-world/
- GameFAQs — Super Fire Pro Wrestling III guide (1P vs CP / CP vs CP match setup): https://gamefaqs.gamespot.com/snes/580142-super-fire-pro-wrestling-iii-easy-type/faqs/72548
- MobyGames — Fire Pro Wrestling Returns (1,648 moves, roster/mode list): https://www.mobygames.com/game/22508/fire-pro-wrestling-returns/
- gamecompanies.com — FPWW official description (1,000+ moves, realistic simulation): https://gamecompanies.com/games/fire-pro-wrestling-world
- arcade-history.com — FPWW version history (CPU-logic patch notes): https://www.arcade-history.com/game/228769/fire-pro-wrestling-world
