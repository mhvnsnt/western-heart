# Euphoria Physics Research — Red Dead Online / RDR2 (Rockstar)
**Date:** 2026-10-23
**Status:** RESEARCH ONLY — public sources only. NO Steam file pull was performed (no credentialed machine available to this researcher), and no claims below are faked or inferred from game binaries. Anything that requires the actual game files is marked [AWAITS FILE PULL].

> **Owner instruction (verbatim):** *"Red Dead Online: the euphoria physics and gta red dead physics and ragdolling"*
> Steam app IDs: 1174180 (Red Dead Redemption 2), 1404210 (Red Dead Online standalone).

---

## Section 0 — What Euphoria is

Euphoria is NaturalMotion's (Oxford, UK) real-time procedural character-animation middleware, built on their proprietary **Dynamic Motion Synthesis (DMS)** technology. It is not a physics engine itself — it is a *motion engine* that sits on top of a commercial physics engine (PhysX in shipped integrations) and synthesizes character animation on the fly from a full simulation of the character's body, simulated muscles, and motor nervous system, driven by AI "Adaptive Behaviors." Instead of playing canned animations, characters' actions and reactions are computed in real time, so no two falls, stumbles, or tackles ever replay identically. It debuted in Grand Theft Auto IV (2008), appeared in Red Dead Redemption, Max Payne 3, GTA V, Star Wars: The Force Unleashed, and Red Dead Redemption 2 (with a "radically overhauled" version). NaturalMotion ended third-party licensing in 2017 and was acquired by Zynga in 2014 — so WH cannot license it; it can only learn from its *observable technique*.

---

## 1. Euphoria (NaturalMotion): how it actually works

### [RESEARCHED]

**Core concept: active ragdoll / behavioral simulation.** Wikipedia's Euphoria entry describes it as animating 3D characters "on the fly based on a full simulation of the 3D character, including body, muscles and motor nervous system." Where typical games swap to a *limp* ragdoll (passive, zero muscle torque) on events like death or impact, Euphoria keeps a layer of *simulated muscular control* running at all times — the character is always a physics object whose joints are driven by virtual muscles with tunable stiffness, and the muscles *react* to forces. ([source](https://en.wikipedia.org/wiki/Euphoria_(software)))

**The muscle/motor model.** Euphoria treats the character as a rigid-body skeleton where every joint is driven by a virtual muscle. Those muscles can tense and relax "just like our muscles do" — i.e., each joint has a controllable stiffness/damping/force ceiling, and the engine varies these per behavior. This is what lets an NPC *balance* rather than collapse: a balance controller applies corrective torques against the support polygon (the feet) while disturbances (shoves, bullet hits) push the body out of balance, and the muscle layer fights back until it can't. ([source](https://entropicdomain.net/formats/misc/pig-euphoria-engine/))

**The behavioral layer.** Per reporting on NaturalMotion, Euphoria ships with tens of prebuilt "Adaptive Behaviors" (balance, stumble, fall, brace, grab, shot-reaction, etc.), and the design power comes from *combining* them like LEGO bricks — a relatively small set of behaviors composed in state machines yields near-infinite variation. An MCV interview with NaturalMotion execs (Topping/Cavanagh) confirms: "they number in the tens, but the point about them is that their strength is in their combination. You could compare it with LEGO bricks, were a relatively low number of brick shapes let you create near infinite different models." It also shipped bundled with Morpheme, and needs a physics engine underneath — "it does need PhysX as a physics engine, because the characters are using physics for these movements." ([source](https://mcvuk.com/development-news/ecstatic-movement-naturalmotion-on-euphoria/))

**Self-preservation and shot reactions.** The observable signature behaviors in GTA/RDR titles: NPCs and the player character have "an inherent sense of self preservation. When shot, bludgeoned, pushed or violently tackled, a character will naturally try to balance itself out. NPCs will even protect their head and vital organs by assuming the fetal position." When Michael stumbles in GTA V, "he doesn't just drop; he reaches out. He tries to brace himself against a nearby wall" — this is the procedural layering of mocap *underneath* the physics reaction: "It layers procedural physics over motion capture data. Instead of just playing a clip, the engine calculates the force of the impact and determines how the character's muscles would realistically react." ([sources](https://entropicdomain.net/formats/misc/pig-euphoria-engine/), [Ludono Studios breakdown](https://ludonodestudios.medium.com/beyond-ragdolls-mastering-weighted-character-logic-and-euphoria-physics-23290536dc4a))

**Origin: nervous-system simulation + genetic algorithms.** Founder Torsten Reil (Oxford zoology, neural researcher) built DMS from real-time simulations of organisms' bodies, muscles, and motor nerves, using simulated genetic evolution to teach virtual characters to walk and react to being tripped or shoved. The same tech powered virtual stuntmen in *Lord of the Rings: Return of the King* battle sequences (notably equine combat) before being commercialized for games. A TED talk by Reil documents the approach; a ProVideo Coalition write-up notes they "used a form of simulated genetic evolution and mutation to teach it how to at first walk, and then react to external forces (such as being tripped or shoved)." ([sources](https://www.provideocoalition.com/ted_talk_reil/amp/), [English-video.net TED summary](https://www.english-video.net/v/en/300))

**Games using Euphoria:** GTA IV (first Rockstar use, confirmed via press release), Red Dead Redemption, Max Payne 3, GTA V, The Force Unleashed I & II, RDR2, NaturalMotion's Backbreaker (football — tackles synthesized in real time, no canned tackle animations) and Clumsy Ninja (first mobile use). Euphoria is integrated into the RAGE engine source. ([source](https://en.wikipedia.org/wiki/Euphoria_(software)))

### [AWAITS FILE PULL]
- The actual behavior graphs (which behaviors ship in RDR2 vs GTA V, their blend weights, muscle-stiffness tables per character/horse) live in RAGE resource files on the credentialed machine — observable only via in-game testing + file extraction.
- Exact joint-muscle parameterization (stiffness/damping/force limits, balance-controller gains) — proprietary, never published.
- The RAGE↔Euphoria integration glue (how animation states hand control to the physics character and back) is source-level; observable behavior is what we can study.

---

## 2. Euphoria vs Morpheme vs Endorphin

### [RESEARCHED]

NaturalMotion sold three complementary products, all registered trademarks, all built in Oxford:

| Product | What it is | Technology | Phase |
|---|---|---|---|
| **Endorphin** | Offline DMS authoring tool — "a tool for creating virtual stuntmen"; synthesizes animation at edit time, bakes results to clips | Dynamic Motion Synthesis (AI + dynamics) | Film/game pre-production; used on *Troy*, *Lord of the Rings*, *Poseidon*; customers Sony, Capcom, Namco, Konami ([gamedeveloper.com](https://www.gamedeveloper.com/press-release/naturalmotion-launches-endorphin-20-at-gdc-2005)) |
| **Morpheme** | Runtime animation engine + graphical authoring tool — "the industry's first graphically authorable animation engine"; blends/trees/transition graphs, IK, authored in `morpheme:connect` | **NOT DMS** — classic blend-tree animation + IK + rigid-body hooks ([animationmagazine.net](https://www.animationmagazine.net/2007/03/naturalmotion-ships-morpheme/)) | Runtime locomotion/animation; users BioShock Infinite, Enslaved, Tony Hawk: RIDE ([dcemu.co.uk](https://www.dcemu.co.uk/vbulletin/threads/226387-Activision-and-Robomodo-Choose-NaturalMotion-s-morpheme-for-Tony-Hawk-Ride)) |
| **Euphoria** | Real-time *behavioral physics* layer — synthesizes reactions on the fly from muscle/nervous-system simulation | Dynamic Motion Synthesis, real time | Runtime reactions: stumbles, shot reactions, falls, tackles |

**How they relate:** Morpheme handles the *authored* side — locomotion, blends, the character's normal animation state machine, built by animators in a visual graph editor. Euphoria handles the *reactive* side — the moments where canned animation would fail (being shoved, shot, tackled, falling). In Rockstar's shipped games Euphoria is sold/shipped *bundled with* Morpheme: "It does basically come with Morpheme, and it does need PhysX as a physics engine" (MCV interview). A gamesindustry.biz Morpheme announcement spells out the division of labor: Morpheme "doesn't use DMS and is designed, the firm claims, to complement the euphoria technology." Endorphin is the offline sibling — it uses the same DMS brain to generate *bakeable* stunt animation for film/game cinematics, i.e., you can synthesize a reaction once in Endorphin and store it, or compute it live in Euphoria. ([sources](https://www.gamesindustry.biz/gdc-naturalmotion-unveils-morpheme-technology), [animationmagazine.net](https://www.animationmagazine.net/2007/03/naturalmotion-ships-morpheme/), [mcvuk.com](https://mcvuk.com/development-news/ecstatic-movement-naturalmotion-on-euphoria/))

**WH analog:** this maps directly onto WH's architecture — WH's authored fight animations/moveset library ≈ Morpheme's job; WH's partial-ragdoll layer (Rapier + Jolt + PhysicsServo) ≈ Euphoria's job; WH's pre-rendered/FMV cutscenes ≈ Endorphin's job (bake once). The design lesson: *keep the authored and reactive layers cleanly separated, with a defined handoff between them*.

### [AWAITS FILE PULL]
- Whether RDR2's horse locomotion runs through Morpheme-style blend trees or fully procedural DMS gait — needs file/animation inspection.

---

## 3. RDR-specific applications

### [RESEARCHED]

**"Radically overhauled" for RDR2.** Rockstar North's director of technology Phil Hooker told VG247 that RDR2's animation system was "radically overhauled" to be more lifelike, and "We use Euphoria specifically to enhance the physics-based reactions of both humans and animals." His headline example: "if a rider's horse is shot then there are a range of realistic outcomes like **rolling off the horse, being dragged in the stirrups, or even being trapped under a dead horse and fighting to get free**" — all synthesized per-incident, never the same twice. ([source](https://gamingbolt.com/red-dead-redemption-2s-euphoria-engine-is-radically-overhauled-says-rockstar))

**Death animations.** Euphoria-driven deaths are per-force-vector: a body shot at 25 mph reacts differently than a standing pistol shot — Reil's interview notes the engine "can accurately determine the cowboy fall when the arm stretching movement and posture" for a rider knocked off a 25-mph horse. Bodies crumple according to momentum, impact surface, and which behaviors (brace/fetal-protect/flail) are active — the classic RDR sight of a shot rider tumbling over the horse's neck is Euphoria, not a clip. ([source](https://topic.alibabacloud.com/article/how-a-neurologist-created-a-gaming-company-and-was-bought-by-zynga_2_8_258844.html))

**Horse physics.** Horses are full Euphoria/DMS characters, not animated props: muscle-tension in legs/neck, weight transfer during gallop turns, stumble-and-recover on terrain, rearing when lassoed, and the infamous individually-physics'd anatomy (confirmed real by Jason Schreier's 2026 Rockstar reporting — the detail was added by a developer independently, outside the production schedule). Reil's TED work explicitly included "modeling the mayhem of equine combat in Lord of the Rings: Return of the King" — horses were one of the earliest DMS successes. ([sources](https://geniusgeeks.com/rockstar-confirms-rdr2s-horse-anatomy-detail-hinting-at-gta-6s-depth/), [english-video.net](https://www.english-video.net/v/en/300))

**Lasso / rope physics.** The lasso is a rope constraint between two physics characters (player/horse ↔ victim). Observable behaviors from gameplay documentation: the rope is a held tension link (must keep holding the trigger or the captive is released), the player can *reel* the victim in (winch the constraint length down), drag victims behind a galloping horse (victim goes full-physics, dragged by the rope attach point, taking damage from terrain collisions), or hogtie (transition to a constrained "bound" state that can be slung over the horse). Notable: in RDR1, lassoing large animals made them act as an *anchor* — the rope constraint could drag the *player* around the animal, proving the link is a symmetric force constraint, not a scripted drag. ([sources](https://twinfinite.net/guides/red-dead-redemption-2-how-to-hog-tie-lasso-and-tie-npcs-to-horses/?amp=1), [alteredgamer.com](https://www.alteredgamer.com/red-dead-redemption/79541-lots-of-nifty-tricks-with-lassos/))

**Character-vs-character grappling.** Backbreaker (NaturalMotion's own football game) is the purest public demo: "employs Euphoria to generate tackles in real-time, as opposed to playback animation" — every tackle is two active-physics bodies colliding, grabbing, and falling per the forces involved. ([source](https://en.wikipedia.org/wiki/Euphoria_(software)))

**Known cost of the approach.** The entropicdomain analysis notes Euphoria's weight comes with sluggishness: "The Euphoria generated animations have a lot of weight behind them but it also takes more time for the player to turn around for instance, since the player character has to literally turn around." This is the core tradeoff WH must manage: physical believability vs. input responsiveness. ([source](https://entropicdomain.net/formats/misc/pig-euphoria-engine/))

### [AWAITS FILE PULL]
- Lasso rope solver parameters (constraint stiffness, segment count, breaking thresholds — reinforced lasso vs knife).
- Horse-vs-rider joint topology (stirrup attach, drag-behind-horse constraint graph).
- Grapple/tackle behavior composition in RDR2's brawling (fistfights use heavily scripted sequences blended with physics — the exact blend is in the files).
- Death-behavior tables per weapon/force in RDR2.

---

## 4. What WH can pull — transferable technique

### [RESEARCHED]

**The core transferable idea: the "puppet on muscles" architecture.** The open, re-implementable version of Euphoria's technique is the *active ragdoll*:

1. **Every fighter is always a rigid-body skeleton** (Rapier handles this in WH) — no separate "animated mesh" vs "ragdoll" modes that cause popping handoffs.
2. **Joints are driven by virtual muscles** — PD/PID servo controllers (this is exactly what WH's existing **PhysicsServo spec** from the Gang Beasts research already describes) that track a target pose. Muscle *stiffness is a runtime variable*, not a constant.
3. **A behavior layer modulates stiffness per event** — getting punched *reduces* stiffness on the hit limb (so it yields to the blow, then the servo pulls it back = flinch/reaction), a knockdown *drops* global stiffness (fall), a wall nearby *raises* arm stiffness toward a brace target (self-preservation). This is the whole secret: Euphoria ≈ active ragdoll + a small library of stiffness-modulating behaviors + authored target poses to servo toward.
4. **Authored animation feeds the servos, not the mesh.** The moveset library (WH's Tekken-sourced clips) plays on an invisible "ghost rig"; the physics body servos toward it. When undisturbed, the fighter looks 100% authored (tight Tekken feel preserved). When hit, the servos yield proportionally to force — this is how WH gets *partial* ragdoll without losing input-to-move fidelity (the owner's feel law).

This architecture is publicly documented in open implementations: Rawad Akar's self-balancing active-ragdoll breakdown describes exactly the dual-rig setup — an invisible **Ghost Rig** (procedural logic, IK, animation states = "where the character should be") and a visible **Physical Rig** (ragdoll on configurable joints acting as muscles, PID-driven toward the ghost pose), with *dynamic muscle tension*: "When the character is hit by a light object, the system reduces joint strength on specific limbs. This allows those parts of the body to yield to the force, creating localized reactions like flinching, before the joints pull the limb back toward the target pose." ([sources](https://jettelly.com/blog/self-balancing-active-ragdoll-in-unity-breakdown-of-an-upcoming-tool/), [desirefx.me](https://desirefx.me/gamedev/self-balancing-active-ragdoll-unity/))

**Specific techniques WH should adopt (all public-domain technique, no middleware):**

- **Per-limb stiffness modulation on hit** (the flinch system above) — the single highest-value Euphoria behavior for a fighting game. Punch lands → reduce stiffness in struck limb + head by force-scaled amount → servo recovers over ~200–400 ms → looks like a real reaction, never the same twice.
- **Balance controller with support polygon** — track the fighter's center of mass over their feet; when a hit pushes the projected CoM outside the base, trigger stumble/knockdown instead of playing a canned "hit stun" clip. This generalizes Tekken's hit-stun into physics.
- **Brace-on-wall / ground-protect behaviors** — raycast around a falling fighter; if a wall is near, servo arms toward it; on hard knockdown, raise arm/neck stiffness into a fetal-guard pose. Direct Euphoria self-preservation analog.
- **Two-body constraint grappling** — throws/tackles as temporary physics constraints between the two fighters' rigid bodies (like RDR's lasso link), released per the throw's authored trajectory. Backbreaker proved full-physics tackles work; WH needs them constrained enough to stay readable for fighting-game timing.
- **Death/KO as stiffness collapse** — KO = global stiffness → 0 over a few frames with the last momentum preserved. Every KO unique, zero extra animation memory.

**What Euphoria deliberately does NOT do (boundaries for WH):** it does not replace authored locomotion or core gameplay animation (Morpheme's job); it does not guarantee responsiveness (the GTA IV "sluggish turn" problem — WH must clamp servo lag on player-controlled limbs to protect the input-to-move feel law); and hard-coded logic still decides *when* behaviors fire (an old but honest avforums engineer's note: "Euphoria provides the animation whilst a character is in air, but the logic that dictates that a character can hold on to the beams is hard-coded and is not on-the-fly"). WH should likewise keep *game logic* (hit detection, state machine, move data) authoritative and let physics handle only the *reaction layer*. ([sources](https://entropicdomain.net/formats/misc/pig-euphoria-engine/), [avforums.com](https://www.avforums.com/threads/euphoria-and-naturalmotion.744246/))

### [AWAITS FILE PULL]
- RDR2's actual hit-reaction behavior compositions (to copy blend structure, not code).
- Muscle/stiffness response curves per body region (observable via frame-by-frame gameplay analysis as a proxy).

---

## Extraction plan (credentialed machine)

Euphoria is proprietary middleware integrated into RAGE source — **there is no middleware to extract** (licenses ended 2017; Zynga owns it). The plan targets *observable behavior and file formats*:

1. **Behavioral capture:** scripted in-game scenarios on the Steam build (1174180 / 1404210) — shoot NPCs from measured angles/distances, lasso-drag across terrain types, shoot horses from under riders, fistfight brawls; record at high frame rate for frame-by-frame reaction analysis (which limbs yield, brace timing, fetal-protect onset).
2. **File-format survey:** RAGE resource containers (`.ydr/.ydd` models, animation clip banks, behavior graphs if exposed in text/rel formats) — catalog which reaction data is data-driven (curves, blend weights) vs hard-coded.
3. **Parameter harvesting:** any data-driven stiffness/response tables found become reference curves for WH's servo tuning.
4. **Horse/rider joint topology:** document the constraint graph (saddle, stirrup, drag links) as the reference design for any WH mounted/vehicle content later.
5. Store large captures on external/Releases, not local disk (per owner's game-pull rules; user owns the game = authorization, no proof needed — but RDR2 pull itself awaits the user's say-so per standing rules; T8 is the only currently-gated title).

---

## Vision mapping — Euphoria vs WH's Rapier / Jolt / PhysicsServo stack

| Concern | Euphoria (RDR2) | WH current stack | Gap Euphoria fills |
|---|---|---|---|
| Rigid bodies | PhysX underneath | **Rapier.js** ✅ equivalent | None — Rapier covers it |
| Soft tissue / jiggle | DMS muscle layer (stiffness-simulated, not true soft-body) | **Jolt soft-body** ✅ arguably *more* physical than Euphoria's muscles for flesh | WH is ahead here; use Jolt for jiggle, Euphoria-style servos for skeleton |
| Muscle servos | Virtual muscles w/ variable stiffness (proprietary) | **PhysicsServo spec** ✅ exists from Gang Beasts research | **Needs implementation**: servo-per-joint with *runtime-variable stiffness* — the spec likely has fixed gains; Euphoria's lesson is stiffness as the primary animation control signal |
| Behavior layer | Tens of Adaptive Behaviors (balance, stumble, brace, fetal-protect, shot-react) composed LEGO-style | ❌ Missing | **The main gap**: build WH's behavior library (flinch, stumble, brace-on-wall, KO-collapse, throw-constraint) as stiffness modulators over the servo layer |
| Authored animation | Morpheme blend trees feeding target poses | Moveset library (Tekken-sourced) | Needs the **ghost-rig pattern**: clips drive an invisible target skeleton; physics body servos to it — never blend mesh directly to physics |
| Game logic vs physics | Hard-coded logic decides *when*; Euphoria decides *how it looks* | Hit detection / state machine (in progress) | Architectural rule to adopt: logic authoritative, physics cosmetic-reactive; clamp servo lag on player limbs to protect input-to-move fidelity |

**Bottom line:** WH doesn't need Euphoria — it needs Euphoria's *two architectural decisions*: (1) **one always-physical body driven by variable-stiffness muscle servos tracking an authored ghost rig** (partial ragdoll with zero mode-switch popping), and (2) **a small LEGO library of stiffness-modulating behaviors** (flinch/stumble/brace/KO) instead of canned reaction clips. Rapier + the PhysicsServo spec + a ghost-rig + a behavior library = an open-source Euphoria-equivalent purpose-built for fighting games, with tighter responsiveness than Rockstar's (no GTA-style sluggish turns — clamp it, per the owner's feel law).

---

*Citations are inline per claim. No Steam files were pulled; no game binaries were inspected. All technical claims derive from the public sources linked above.*
