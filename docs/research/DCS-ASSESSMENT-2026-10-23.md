# DCS World — Assessment for Western Heart (character customization / animations / "powers")

- **Date:** 2026-10-23
- **Status:** Research complete from public sources ONLY. **NO Steam file pull was possible in this pass** — no game files were accessed, no assets extracted, no claims below are based on proprietary file contents. All findings are from wikis, Eagle Dynamics docs, and the DCS modding community. Nothing is faked.
- **Steam App ID:** 223750

> **Owner instruction (verbatim):** *"DCS World Steam Edition: powers and caharcter customization and animations"*

---

## Section 0: What the game is

Digital Combat Simulator (DCS) World is a free-to-play combat flight simulator developed by Eagle Dynamics, running as a unified modular platform: the base client is free and paid "modules" (aircraft, maps, campaigns) plug into it, produced by Eagle Dynamics and third-party developers. It is a "study sim" — aircraft are modeled from real-world data with authentic flight models, subsystems, and detailed cockpits with clickable buttons and switches — and includes a Lua-scriptable mission editor and multiplayer. [RESEARCHED — https://en.wikipedia.org/wiki/DCS_World]

---

## 1. What DCS World IS (context)

Covered above. The relevant framing for WH: DCS is not a character game. The "characters" are jet cockpits; the human pilot is almost entirely invisible (first-person view, no player avatar). Everything DCS does best — clickable cockpit systems simulation, internal-component damage modeling, flight dynamics — lives at the *machine* layer, not the *humanoid character* layer. That single fact caps the ceiling of this pull.

---

## 2. Pilot / character models and animation

### [RESEARCHED]

- **Pilots are seat-shaped set dressing, not characters.** DCS's pilot models (e.g. `pilot.edm`, `pilot+f14-seat.edm`, `aces.edm`) are seated humanoids bolted to an ejection seat, placed by Lua coordinates in the aircraft's `crew_members` data block. The modding manual instructs placement of "ejection seat and pilot" as a single unit with the origin at mid-torso. [RESEARCHED — https://manuals.plus/m/af6aef5989130787b7606cb923cff3d5c7e4e1377625fc0dac113a041507cfef.pdf]
- **No standing/walking humanoid pipeline.** A community modder's well-known pilot-mod project confirmed the base models are bones-rigged but "all are sitting, not standing" — heads can turn, arms/legs can be posed, hands-on-controls animation exists via "args," and they "could be placed in any cockpit with lua," but there is no walkable humanoid rig, no standing idle, no locomotion. [RESEARCHED — https://forum.dcs.world/topic/313974-female-pilot-faces-for-aircraft-helos-infantry/]
- **Pilot body is often absent by design.** A long-running ED forum wishlist thread is literally a plea for a toggle-able pilot body in cockpits — in most modules you see no pilot at all in first person, and when one exists (Ka-50, P-51) it's "all kinds of animations... the pilot even makes some gestures after landing," which was considered a novelty feature, not a baseline. The P-51 pilot moves legs/arms from external view and has a first-person bail-out sequence. [RESEARCHED — https://forum.dcs.world/topic/87545-pilot-body-for-all-dcs-modules-plea-toggle-able-as-is-for-ka50-and-p51/]
- **The animation system is "animation arguments," not a character anim system.** DCS animates model parts through indexed arguments ("args") driven by Lua logic: gear levers, canards, flaperons, canopy, wingflex, control sticks, throttles, even pilot hands are each an "argument" on the model driven by the systems-logic layer. Modders animate cockpit gauges in Lua and link "everything... including throttle and control yokes/pedals." [RESEARCHED — https://manuals.plus/m/af6aef5989130787b7606cb923cff3d5c7e4e1377625fc0dac113a041507cfef.pdf and https://forum.dcs.world/topic/170346-mods-by-cubanace-simulations/]
- **Infantry/ground units exist but are primitive.** DCS's Combined Arms module includes infantry soldier models — they are static/low-fidelity AI ground units, not character assets with customization or meaningful animation. [RESEARCHED — https://www.3rd-wing.net/index.php?s=ab67727dc6fd341f2ad1454f949ec899&act=Print&client=printer&f=10&t=14616]
- **Character customization: effectively zero.** There is no character creator, no body slider, no face system — the "customization" in DCS is aircraft *liveries* (paint schemes). The closest community character work is a fan mod adding female pilot faces/models, done out-of-engine (3ds Max bones + args + connectors) and injected via Lua. [RESEARCHED — https://forum.dcs.world/topic/313974-female-pilot-faces-for-aircraft-helos-infantry/]

### [AWAITS FILE PULL]

- Inspecting `pilot.edm` / `Bazar/World/Shapes` models directly would let us see exact bone counts, bind poses, and how "animation arguments" map to bones — and whether any standing humanoid skeleton exists at all (unlikely per community evidence).
- Exact arg indices for pilot hand/head control (for porting the *concept* of per-part arg-driven animation, not the models themselves).
- Infantry unit meshes/animations (Combined Arms) to confirm their fidelity floor.

---

## 3. "Powers": aircraft systems, weapons, damage models

### [RESEARCHED]

- **"Powers" in DCS = systems simulation + weapons, not special moves.** High-fidelity modules model complete electrical systems with every relay/switch/breaker and bus-switching logic, hydraulic systems where flight controls depend on hydraulic pressure, pressurization, oxygen, fuel, and air-data computers that simulate "organic" downstream failure behavior (e.g., a blocked pitot tube produces correct altimeter/VSI behavior without special-case code). [RESEARCHED — https://forum.dcs.world/topic/104660-aviodev-c-101-systems-simulation-overview/]
- **The WWII damage model is the genuinely interesting piece.** Eagle Dynamics built a damage model that calculates hits to *internal aircraft systems* based on their actual location inside the airframe — oil, air, hydraulic and cooling systems, engine/prop installation, throttle controls, flight controls including trim connectors, and structural longerons/spars/stringers. The system "precisely calculates hits to these internal aircraft systems as the projectile passes through the aircraft," so damage to the wing skin decreases lift, damage to a spar reduces strength (wing can snap at specific loads). Damage states have distinct visual tells: white-reddish vapor = hydraulic leak (trail size = leak size), brownish haze = oil system damage (engine will overheat and fail), bright white steam = radiator/cooling damage, fine white vapor = fuel leak. [RESEARCHED — https://forum.dcs.world/topic/252280-new-wwii-damage-model-test-servers-are-active/]
- **Weapon visual effects.** Modders commonly implement "wing vapors," explosion effects, and missile/tracer visuals. The Skyward FM review of the SK-60 mod notes custom visual-effect work (e.g., pilot wave animation) as a modding-level capability. [RESEARCHED — https://www.skywardfm.com/post/preview-sk60-mod-for-dcs-world-by-baas-dynamics]
- **What does NOT transfer:** specific aircraft systems (hydraulics, circuit breakers) have no fighting-game analogue; the Lua "device/element/indicator" MVC architecture for cockpits (Model = logic, View = animated 3D, Controller = clickable interaction code) is for cockpits, not combat. [RESEARCHED — https://forum.dcs.world/topic/97337-beginners-guide-to-dcs-world-aircraft-mods/page/4/]

### [AWAITS FILE PULL]

- The actual damage-system data structures (hit-box definitions, per-component damage values, damage→flight-model coupling code) to port the *design pattern* of location-based internal damage.
- Weapon-effect particle/effect definitions (vapor trails, explosions, smoke) as reference for WH hit-effect upgrades — though WH already pulls hit effects from Tekken teardown files per standing directive, so this is a backup source at best.

---

## 4. Honest assessment: is there anything worth pulling?

**Yes — but very little, and it's design patterns, not assets.**

DCS World has essentially nothing for WH's two stated asks:

1. **Character customization — ZERO pull.** DCS has no character creator, no parametric bodies, no face system, no rigged standing humanoids. The "characters" are planes. The pilot models are seated, low-detail, and considered optional garnish by the community. There is no WWE-CAW-style system to learn from here; that whole lane belongs to the WWE 2K teardowns already on the pull list.
2. **Character animations — ~ZERO pull.** The animation pipeline is arg-driven mechanical part animation (levers, canopies, flaperons) plus minimal seated-pilot posing. No locomotion, no combat animation, no pose library, no idle/movement data. Nothing transfers to a Tekken-style fighter rig.

The **1–2 genuinely transferable things**, both as design philosophy rather than files:

- **(a) Location-based internal damage modeling → WH body-damage system.** DCS's WWII damage model (projectile passes through airframe → damages specific internal systems at their real locations → systems degrade with correct downstream behavior → distinct visual tells per system) maps directly onto a WH feature Tekken does *not* have: per-body-zone damage with functional consequences. Example design: repeated hits to a fighter's left arm could degrade that arm's moves (weaker/fewer punch options, visual tell like a limp or damage decal) — an "internal systems" model for humanoid fighters. This would be a WH differentiator, and DCS is one of the few games to implement this pattern rigorously. (Note: would need user sign-off — it changes fight feel, and the user is protective of Tekken feel.)
- **(b) Arg-driven secondary animation → WH costume/gear animation system.** DCS animates sub-parts of a model through indexed arguments driven by game logic rather than full animation clips (canopy opens, wing flexes, pilot hand follows stick). The *concept* ports to WH as: fighter attachments (belts, coats, weapon props, tentacles for Zen/Chatur-adjacent designs) animated parametrically from fight state (heat, movement speed, hit reactions) instead of hand-authored clips. Cheap, systemic, and reusable across the roster. The concept can be implemented from scratch; the DCS files are not required to copy it.

**Bottom line:** DCS World is a weak pull for WH. It should stay at the very bottom of the pull list. If anything, only (a) and (b) above are worth a coordinator ticket — and both are design documents, not file extractions. A Steam file pull of app 223750 is NOT recommended as a priority; the value was establishable from public sources. The user said "powers and character customization and animations" — DCS offers none of those three for a fighting game. Say so plainly.
