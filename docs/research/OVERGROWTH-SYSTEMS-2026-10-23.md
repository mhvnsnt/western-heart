# Overgrowth — Systems Research for Heart and Mind Within

**Date:** 2026-10-23
**Status:** PUBLIC-SOURCE RESEARCH ONLY. No Steam file pull was performed or was possible from this machine. Every substantive claim below is cited to a public URL. Nothing was faked, extrapolated beyond what sources state, or presented as verified from game files. Steam app ID: **25000**.
**Purpose:** Owner pull list — feed traversal, parkour, acrobatics, combat feel, and world-building techniques into Western Heart's "Heart and Mind Within" (WH's Devil Within-style 3D beat-em-up story mode).

> **Owner instruction (verbatim):** *"Overgrowth: heart and mind inside world building, traversal, combat, and free flow, parkour, acrobatics, etc"*

---

## Section 0: What Overgrowth is

Overgrowth is a 3D third-person martial-arts action game by Wolfire Games, starring anthropomorphic animals (rabbits, wolves, cats, dogs, rats), and is the sequel to Lugaru (2005). It was announced September 17, 2008, developed for 9 years, and released October 16, 2017 on Steam (app 25000) [https://dev.library.kiwix.org/content/allthetropes_en_all_maxi_2025-06/Overgrowth](https://dev.library.kiwix.org/content/allthetropes_en_all_maxi_2025-06/Overgrowth), [https://pvs-studio.com/en/blog/posts/cpp/0957/](https://pvs-studio.com/en/blog/posts/cpp/0957/). It runs on Wolfire's in-house **Phoenix Engine**, which couples physics, procedural animation, and combat into one system rather than separate modes [https://www.christcenteredgamer.com/reviews/pc-mac/overgrowth-pc](https://www.christcenteredgamer.com/reviews/pc-mac/overgrowth-pc). On April 22, 2022, Wolfire open-sourced the game's **code** (engine, project files, scripts, shaders) under the **Apache 2.0** license on GitHub — assets (models, textures, audio, levels) remain proprietary and require owning the game [https://www.gamingonlinux.com/2022/04/overgrowth-from-wolfire-games-goes-open-source/comment_id=224878/](https://www.gamingonlinux.com/2022/04/overgrowth-from-wolfire-games-goes-open-source/comment_id=224878/), [https://github.com/WolfireGames/overgrowth](https://github.com/WolfireGames/overgrowth). Apache 2.0 permits commercial reuse of the code with attribution, which is directly relevant to WH.

---

## 1. Movement / Traversal

### [RESEARCHED]

**Control scheme (default, rebindable):** WASD run, Spacebar jump (hold to jump farther; hold against a wall to wall-run), Shift to roll/crouch/sneak [https://www.magicgameworld.com/?p=11736](https://www.magicgameworld.com/?p=11736). Characters can run up and sideways on walls, jump from wall to wall, grab ledges, roll, and flip [https://plannedallalong.blogspot.com/2021/03/quick-review-overgrowth.html](https://plannedallalong.blogspot.com/2021/03/quick-review-overgrowth.html).

**No mode split.** Wolfire's David: *"There's no shift between movement and combat modes. You can smoothly jump out of a fight to wall-run up a wall at any time, without having to 'tear' yourself away from the combat system."* The combat system is deliberately simple (attack + block buttons) so complexity lives in movement and positioning [https://www.pcgamer.com/overgrowth-preview/](https://www.pcgamer.com/overgrowth-preview/).

**Wall-running is velocity-gated, not sticky.** Per the community (Steam thread): each wall-run has a fixed duration (~3 seconds); entry requires horizontal speed above a threshold and vertical speed below a threshold; easiest entry is at the peak of a jump after a full-speed run (max ground speed reached ~1 second); you steer the run by rotating the camera / pressing the direction you want to go [https://steamcommunity.com/app/25000/discussions/0/1488861734115900357/?l=italian](https://steamcommunity.com/app/25000/discussions/0/1488861734115900357/?l=italian).

**Three-layer controller architecture (documented on the Wolfire wiki):**
- Intent layer: `Data/Scripts/playercontrol.as` (player) or `enemycontrol.as` (AI) — decides what to do.
- Capability layer: `Data/Scripts/aschar.as` (shared by player and NPCs) — dictates what the character is physically allowed to do, triggers events/consequences via the Controller Script Interface.
- Engine layer: `MovementObject` (C++) — physics body.
The interface exposes intent queries like `WantsToJump()`, `WantsToFlip()`, `WantsToFlipOffWall()`, `WantsToJumpOffWall()`, `WantsToGrabLedge()`, `WantsToRoll()`, `WantsToRollFromRagdoll()`, `GetTargetVelocity()`, `GetTargetJumpVelocity()` [http://wiki.wolfire.com/index.php/Character_Control_Script](http://wiki.wolfire.com/index.php/Character_Control_Script). This "intent → capability arbitration → physics" layering is a clean, portable pattern.

**Procedural animation, not clip libraries.** The Phoenix Engine's stated design principle is *"procedural generation of animation via keyframes and interpolation"* for fluidity [https://wiki.wolfire.com/index.php/Phoenix_Engine](https://wiki.wolfire.com/index.php/Phoenix_Engine). David Rosen's talk on the dynamic procedural animation system (summarized by developers): bone transforms are interpolated between a small set of keyframes, and parameters (speed, slope, etc.) drive the interpolation mathematically — *"instead of having an artist tweak the animation, we can automate it with math"* [https://hub.jmonkeyengine.org/t/dynamic-procedural-character-animation-system/29460](https://hub.jmonkeyengine.org/t/dynamic-procedural-character-animation-system/29460). Wolfire told IndieDB the same: important animations like running, climbing, fighting are *"determined on the fly… depending on a bunch of variables"* rather than hard-coded [https://www.indiedb.com/features/interview-with-wolfires-jeffrey-rosen](https://www.indiedb.com/features/interview-with-wolfires-jeffrey-rosen). Shipped features include: leg IK for movement, procedural animation for edge movement, soft IK bones (ears), acceleration tilt while running, and **cancellable animations** [https://www.wolfire.com/blog/2010/06/Overgrowth-Alpha-84/](https://www.wolfire.com/blog/2010/06/Overgrowth-Alpha-84/), [https://www.wolfire.com/blog/2010/11/Overgrowth-Weekly-Alpha-Video/](https://www.wolfire.com/blog/2010/11/Overgrowth-Weekly-Alpha-Video/). Custom animations are keyframed in Blender and exported to Wolfire's binary PHXANM (`.anm`) format with their Blender addon; scripts can call them [https://wiki.wolfire.com/index.php/Custom_Animations](https://wiki.wolfire.com/index.php/Custom_Animations), [https://www.wolfire.com/blog/2010/02/Scripting-and-Custom-Animations/](https://www.wolfire.com/blog/2010/02/Scripting-and-Custom-Animations/).

**Momentum is committed.** Characters speed up/slow down with terrain trajectory, and *"jumping cannot be altered once the motion is carried"* — air control is limited, which makes movement feel weighty and skill-based [https://www.christcenteredgamer.com/reviews/pc-mac/overgrowth-pc](https://www.christcenteredgamer.com/reviews/pc-mac/overgrowth-pc).

### [AWAITS FILE PULL]
- Exact numeric constants: wall-run entry thresholds, run acceleration/top speed, jump velocities, flip trigger conditions/timings — all live in `aschar.as` / `playercontrol.as` (open-source scripts; extractable without owning assets).
- The camera-side of wall-run steering (how camera rotation maps to run direction) — in the C++ camera code.
- Which flips exist as distinct moves vs. emergent from jump+direction (the script interface lists `WantsToFlip()` but the exact bindings need the scripts).

---

## 2. Combat System

### [RESEARCHED]

**One-button contextual combat (design doc, Wolfire 2009):** An attack is *"an animation paired with an intended damage value"*, initiated by the **release** of left click. Attack = **F(distance, preparation time, position)**:
- **Distance** (close/ranged to auto-targeted enemy — targeting picks "the most dangerous enemy," i.e. whoever will strike first, like Clint Eastwood clearing a room).
- **Preparation time** (how long left click was held = wind-up): controls animation playback speed toward a "preparation frame," then snaps to the "attack frame" on release. It does NOT select which attack plays.
- **Position** (standing / crouching / moving left / moving right across the target): selects the animation — e.g. `[close][standing] → knee to the gut`, `[ranged][moving left] → roundhouse kick` [https://www.wolfire.com/blog/2009/02/overgrowth-fighting-system-design-doc-1st-draft/](https://www.wolfire.com/blog/2009/02/overgrowth-fighting-system-design-doc-1st-draft/). This maps to the owner's "fight feel" interest: input-to-move fidelity is replaced by *context*-to-move fidelity — the system picks the tactically right move so the player thinks about positioning, not buttons [https://www.pcgamer.com/overgrowth-preview/](https://www.pcgamer.com/overgrowth-preview/).

**Damage model:** each move has a max damage scaled by a preparation-time curve with a quick zone, an **optimal zone**, and a late zone (holding a strike too long forfeits damage — arms get tired). Two damage types carried over from Lugaru: **permanent damage** (stays forever) and **temporary damage** (decays over time — 5 punches in 5 seconds knock you out; spread over 5 hours they don't). Death/unconsciousness when permanent + temporary exceeds health [https://www.wolfire.com/blog/2009/02/overgrowth-fighting-system-design-doc-1st-draft/](https://www.wolfire.com/blog/2009/02/overgrowth-fighting-system-design-doc-1st-draft/).

**One-hit-kill philosophy:** *"Fights end fast: one or two good blows can kill you"* — and the same applies to enemies, so the instant of engagement is critical [https://www.pcgamer.com/overgrowth-preview/](https://www.pcgamer.com/overgrowth-preview/). There are no health bars or HUD; kills register from sheer physical damage — a forceful kick, a fall, a weapon strike [https://www.digitallydownloaded.net/2017/10/review-overgrowth-pc.html](https://www.digitallydownloaded.net/2017/10/review-overgrowth-pc.html).

**Blocks are parries.** Combat is described as blow-for-blow rather than combo-for-combo: *"every block is a parry"* — timed right-mouse blocks trigger counters; holding block after a successful block lets you **throw** the opponent (they can break it by pulling away or rolling); duck-attacks sweep legs; dodging is a directional tap just before impact [http://nightmaremode.thegamerstrust.com/2011/10/10/overgrowth-alpha-impressions/](http://nightmaremode.thegamerstrust.com/2011/10/10/overgrowth-alpha-impressions/), [https://www.pcgamer.com/overgrowth-preview/](https://www.pcgamer.com/overgrowth-preview/).

**Weapons:** swords, knives, spears, rapiers scattered through levels; often one-hit kills (dog broadswords, thrown knives at close range, spears); grab/disarm moves steal them; enemies can catch thrown weapons out of the air; spear-specific systems include spear throw, sweep attacks, and active-block poses [https://tvtropes.org/pmwiki/pmwiki.php/YMMV/Overgrowth](https://tvtropes.org/pmwiki/pmwiki.php/YMMV/Overgrowth), [https://www.cubed3.com/games/reviews/pc/overgrowth](https://www.cubed3.com/games/reviews/pc/overgrowth), [https://www.wolfire.com/blog/2013/09/Overgrowth-a201-video-changelog/](https://www.wolfire.com/blog/2013/09/Overgrowth-a201-video-changelog/). A "reaction override system" lets weapons define specific hit animations on victims [https://www.wolfire.com/blog/2013/09/Overgrowth-a201-video-changelog/](https://www.wolfire.com/blog/2013/09/Overgrowth-a201-video-changelog/).

**Combat AI:** goal-based (Patrol, Attack, Investigate, Get Weapon, Flee, Escort, Navigate, Struggle, Hold Still) driven by simulated senses — vision cones with "seen" counters, hearing radii (rabbits hear 2x as far), suspicion accumulation from sounds and collisions [http://wiki.wolfire.com/index.php/Character_Control_Script](http://wiki.wolfire.com/index.php/Character_Control_Script).

### [AWAITS FILE PULL]
- Exact preparation-time damage curve parameters and per-move damage values (`aschar.as` + attack data files).
- Counter/throw timing windows and the active-block rules (shipped values may differ from the 2009 draft).
- Weapon stat tables (damage, throw behavior) — data files, proprietary.

---

## 3. World Building (the in-game editor)

### [RESEARCHED]

**The editor ships inside the game** and is the same tool Wolfire used to build the Overgrowth and Lugaru story campaigns — press **F1** to toggle it on any level, `Esc` reopens the editor window mid-play [https://wiki.wolfire.com/index.php/Basic_Controls](https://wiki.wolfire.com/index.php/Basic_Controls) (page titled "Editor Interface").

**Object-based construction:** levels are assemblies of objects loaded from XML definition files via the Load menu (click in the world to spawn; thumbnails on hover). Selection supports single, toggle, box-select, and select-similar; transforms are direct-manipulation (translate/scale/rotate via bounding-box faces/edges/corners) with ctrl = snap to half-meter, alt = clone-on-transform [https://wiki.wolfire.com/index.php/Basic_Controls](https://wiki.wolfire.com/index.php/Basic_Controls).

**Prefab vs. template distinction:** *Prefabs* auto-update in every level they're placed in when resaved; *templates* are one-shot copies. Groups transform around a shared center. Edit-mode filters (cmd+1 static meshes, cmd+2 decals, cmd+3 gameplay objects) keep layers manageable [https://wiki.wolfire.com/index.php/Basic_Controls](https://wiki.wolfire.com/index.php/Basic_Controls).

**Gameplay wiring in-editor:** characters are placed as spawn-point boxes (`Load → Character`, click to place); cmd-shift-P toggles a spawn between player-controlled (green) and AI (white); up to four player spawns = local multiplayer. Script params on any object tune AI behavior, speed, scale, etc. Dialogue is triggered by placing "Start Dialogue" hotspots and resizing trigger volumes. A checkpoint system (`Data/Objects/Hotspots/overgrowth_level.xml`) handles progress, respawn, enemy persistence, and level transitions [https://wiki.wolfire.com/index.php?title=Characters_](https://wiki.wolfire.com/index.php?title=Characters_), [https://wiki.wolfire.com/index.php/Dialogue](https://wiki.wolfire.com/index.php/Dialogue), [https://wiki.wolfire.com/index.php/Checkpoints](https://wiki.wolfire.com/index.php/Checkpoints).

**AI navigation tooling built in:** nav mesh create/save/load/view, collision preview, navmesh_hint objects (collision only the generator sees), navmesh_region volumes, and **jump nodes** (navmesh_connection) so AI can traverse parkour geometry [https://wiki.wolfire.com/index.php/Basic_Controls](https://wiki.wolfire.com/index.php/Basic_Controls).

**Fastest iteration loop in the business:** press **8** to instantly playtest the level from the editor camera (auto-spawns a player character if none exists); **L** reloads the level; **X** restores all characters to full health and clears blood — effectively a one-key reset for encounter testing. Slow-motion (Tab) and freeze-frame (backtick) debug keys exist for tuning [https://wiki.wolfire.com/index.php/Basic_Controls](https://wiki.wolfire.com/index.php/Basic_Controls). Levels are plain files under `Data/Levels`, shared via Steam Workshop [https://wiki.wolfire.com/index.php/Overgrowth_Bug_FAQ](http://wiki.wolfire.com/index.php/Overgrowth_Bug_FAQ).

### [AWAITS FILE PULL]
- The actual shipped campaign `.xml` level files (proprietary) to study encounter layout, hotspot density, and checkpoint pacing.
- Editor source (open-source C++) for the transform-gizmo math and nav-mesh pipeline, if WH wants to build a similar in-game editor.
- Terrain system specifics (heightfield vs. mesh, material painting) — needs code + data.

---

## 4. "Free Flow" — what makes it feel free

### [RESEARCHED]

**No seams.** The single biggest factor: movement and combat are one continuous system (PC Gamer quote, §1). You never "enter combat mode" — you can wall-run out of a fight mid-swing [https://www.pcgamer.com/overgrowth-preview/](https://www.pcgamer.com/overgrowth-preview/).

**Cancellable everything.** Animations are cancellable by design (shipped in the 2010 alpha) [https://www.wolfire.com/blog/2010/11/Overgrowth-Weekly-Alpha-Video/](https://www.wolfire.com/blog/2010/11/Overgrowth-Weekly-Alpha-Video/); the three-layer controller means a new intent (roll, jump, block) can preempt the current animation at any frame through `WantsToCancelAnimation()`-style arbitration [http://wiki.wolfire.com/index.php/Character_Control_Script](http://wiki.wolfire.com/index.php/Character_Control_Script).

**Ragdoll ↔ animation is a continuum, not a switch.** Active ragdoll (hold Z — character protects itself while falling), pain ragdoll (N), floppy ragdoll (M) are all player-triggerable; you can **roll out of ragdoll** back into control; "flip ragdoll wipeouts" turn hard landings into flips; alpha 78 added "better integration of ragdolls and animation" so recovery is fluid [https://www.wolfire.com/blog/2010/11/Overgrowth-Weekly-Alpha-Video/](https://www.wolfire.com/blog/2010/11/Overgrowth-Weekly-Alpha-Video/), [https://wiki.wolfire.com/index.php/Alpha_78](https://wiki.wolfire.com/index.php/Alpha_78), [https://wiki.wolfire.com/index.php/Basic_Controls](https://wiki.wolfire.com/index.php/Basic_Controls).

**Momentum sells the freedom.** Reviews consistently describe movement as "fun and free," with weight and trajectory-commitment making speed feel earned; dust clouds at the feet on run/jump landings and particle streams reinforce impact [https://www.christcenteredgamer.com/reviews/pc-mac/overgrowth-pc](https://www.christcenteredgamer.com/reviews/pc-mac/overgrowth-pc), [https://wiki.wolfire.com/index.php/Phoenix_Engine](https://wiki.wolfire.com/index.php/Phoenix_Engine).

**Camera is the weak link (honest note).** The camera is a simple follow cam with **no enemy lock-on**, and multiple reviewers flag it as the game's main feel problem in multi-enemy fights [https://www.gamegrin.com/reviews/overgrowth-review/&q](https://www.gamegrin.com/reviews/overgrowth-review/&q). For HMW this is a known pitfall to design around (soft-lock or intelligent framing), not a technique to copy.

### [AWAITS FILE PULL]
- Camera spring/damping parameters and wall-run camera tilt behavior — in the open-source C++ camera code.
- Input buffering details (whether attack inputs queue during animations) — needs the scripts.

---

## 5. What WH can pull (transferable techniques)

### [RESEARCHED — all grounded above]
1. **Three-layer controller (intent → capability → physics).** `playercontrol.as` / `aschar.as` / `MovementObject` is a proven, scriptable architecture WH can mirror for HMW's 3D mode: input intents from the player, a shared arbitration layer that also serves AI, and one physics body underneath.
2. **Parametric procedural animation blending.** Interpolate between a small keyframe set driven by speed/slope/airtime, plus leg IK and acceleration tilt — far cheaper than authoring full parkour clip libraries, and it matches WH's open-source-stack approach.
3. **Contextual combat function.** Attack = F(distance, charge, position) with an optimal-zone charge curve and permanent-vs-temporary damage — a strong model for HMW's beat-em-up combat, where Tekken's 1:1 input fidelity matters less than readable, brutal encounters.
4. **In-game editor with instant playtest.** F1 editor + "press 8 to play" + one-key encounter reset (X) is the iteration loop HMW's world-building tool should copy: build story stages inside the running game, not in an external DCC.
5. **Ragdoll-as-gameplay.** Roll-out-of-ragdoll, active/pain/floppy ragdoll states, and weapon reaction overrides — directly applicable to WH's "partial ragdoll" goal (Gang Beasts/Human Fall Flat-inspired, not full ragdoll).
6. **Nav mesh with jump nodes.** AI that can traverse parkour geometry is a prerequisite for HMW's 3D stages; Overgrowth's in-editor nav tools (hints, regions, jump connections) are the reference design.
7. **License advantage.** All of the *code* — movement controller, camera, animation blending, editor — is Apache 2.0 and legally reusable in WH commercially with attribution. Only art assets/levels/audio are off-limits.

### [AWAITS FILE PULL]
- Numeric tuning constants for every system above (wall-run thresholds, damage curves, camera params) — extract from the open-source repo on a credentialed machine and bank them in `docs/research/`.

---

## Extraction plan for the credentialed machine

1. **Clone the public repo** (no purchase needed): `https://github.com/WolfireGames/overgrowth` — Apache 2.0. Priority files: `Data/Scripts/aschar.as`, `playercontrol.as`, `enemycontrol.as` (movement/combat/camera intents); `Source/` camera + character + animation-blending code; `Data/Scripts/` attack/damage definitions.
2. **Confirm Steam ownership of app 25000** and install — needed only for proprietary assets/levels (study reference, never redistribute). The scripts and code above do NOT require the purchase.
3. **Extract and bank constants**: wall-run entry speeds/duration, jump velocities, flip conditions, camera spring/damping/tilt, preparation-time damage curve, counter/throw windows → write to `docs/research/overgrowth-constants.md` in mhvnsnt/western-heart (standing rule: everything goes in the repo).
4. **Study shipped level XMLs** (`Data/Levels/`) for encounter layout, checkpoint pacing, hotspot/trigger usage → `docs/research/overgrowth-level-design.md`.
5. **Evaluate code reuse**: identify the exact functions/files for the movement controller and camera that can be vendored under Apache 2.0 with attribution notices; prototype the three-layer controller against WH's 3D story-mode sandbox.
6. **Animation pipeline**: pull Wolfire's Blender `.anm` export scripts (in-repo) to understand the PHXANM format in case WH wants keyframe-interpolated traversal anims.

---

## Vision mapping: Overgrowth systems → Heart and Mind Within

| Overgrowth system | HMW application |
|---|---|
| Velocity-gated parkour controller (wall-run, wall-jump, ledge grab, roll, flip) | HMW's 3D stage traversal layer — the "free flow" movement between fights in each character's campaign |
| Intent → capability → physics controller architecture | HMW player + enemy AI share one arbitration layer; scriptable intents keep AI and player mechanics identical (same rule the WH team uses for Tekken-side parity) |
| Procedural keyframe-interpolation animation + leg IK + accel tilt | Traversal animation for HMW without authoring hundreds of clips; complements WH's Tekken-sourced fight anims |
| Contextual one-button combat, optimal-zone charge, permanent/temporary damage | HMW beat-em-up encounters: readable, brutal, no HUD clutter; Tekken 1:1 inputs stay in the 1v1 arenas, contextual combat rules the story stages |
| In-game editor (F1), instant playtest (8), one-key reset (X), prefabs, nav mesh + jump nodes | HMW world-building tool: build story stages inside the running game; AI that can chase the player across parkour geometry |
| Ragdoll ↔ animation continuum (roll recovery, active ragdoll, reaction overrides) | WH's partial-ragdoll goal — physicality without losing control |
| Goal-based sensory AI (patrol/investigate/attack/get weapon) | HMW encounter design: enemies that investigate noise, seek weapons, flee — stages feel alive, not arena-spawned |
| No-lock-on follow camera (known weakness) | Anti-pattern: HMW gets soft-lock/intelligent framing from day one |

**Bottom line:** Overgrowth is the single best public reference for what the owner asked for — its code is open, its architecture is documented on Wolfire's own wiki, and its techniques (layered controller, parametric animation, in-game editor, ragdoll integration) transfer to Heart and Mind Within without needing a single proprietary asset. The file pull that matters is the *already-public source repo*, not Steam.
