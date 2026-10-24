# MKX / MK11 X-ray & Finisher Technique (2026-10-23)

**Status:** technique research (public sources only). MK names appear here because this is a technical research file — never in in-universe writing or UI.
**Companion design:** `docs/research/FINISHER-DESIGN-2026-10-23.md` (the WH finisher system built from this technique).
**Prior art in-repo:** `game/js/xray.js` (PR #874 — Tekken-styled X-ray beat), `game/js/finisher.js` (PR #872 — Tekken-styled finisher gates).

The user does not play MK and does not like MK fighting games, but likes the **X-ray attack IDEA**: showing the inside of the body at the moment of impact. This document records exactly how NetherRealm implements X-rays and their successors so Western Heart can borrow the technique — and only the technique — inside Tekken-style constraints (flow never breaks, no lethality, no gore).

---

## 1. MK9 (2011) — the X-ray is born

- **Meter:** a 3-part super meter at the bottom of the screen. Builds as you fight — offense, taking damage, using specials. Full meter = X-ray available.
- **Input:** Block + Front Kick + Back Kick, all at once (BL+FK+BK). Early previews described it as a double-tap of the shoulder buttons.
- **Behavior:** a quick cinematic mini-combo. Each character has a **custom-authored** X-ray attack (Johnny Cage's is a counter; Liu Kang's "Chin Up" can combo into more hits after; some X-rays are used mid-combo).
- **Visual:** as the blows land, the camera zooms in and shows an X-ray view — ribs cracking, jaws fracturing, skull damage — then the fight resumes.
- **Why it mattered:** it was MK's take on the super combo — "Mortal Kombat's take on the super combo" (Badger Herald, 2011). The broken bones have **no gameplay effect** — the victim stands up immediately and keeps fighting.

## 2. MKX (2015) — the X-ray matures

### 2a. Meter and gating

- Requires a **full 3-bar Super Meter**. The meter builds from combos, throws, blocking attacks, and special moves.
- Firing the X-ray **consumes all 3 bars immediately**.
- Sources: SuperCombo Wiki (MKX/Offense), GamePressure ("X-Ray special techniques").

### 2b. Input

- **BL + FK + BK simultaneously** (Block + Front Kick + Back Kick), or described as **Stance Change + Block**.
- One press — no motion input, no sequence. (This is the input model WH deliberately does *not* copy; see §6.)

### 2c. Properties

- Each character has a **unique X-ray animation**; once launched it **cannot be interrupted** — but the *startup* can be **blocked or dodged with a jump**. A whiffed X-ray leaves the attacker exposed with an empty meter.
- X-rays are **often armored** (hyper armor on startup): hitting the attacker during startup deals damage but doesn't stop the X-ray, and the attacker usually wins the trade.
- Recommended use: keep the combo short before firing, so damage scaling doesn't eat the X-ray's damage (~30%+).

### 2d. Camera technique (the part WH borrows)

From the MKX reveal trailer and featurettes:

1. **The fight plays normally** until the X-ray's first heavy hit connects.
2. **Hard cut to close-up:** the camera detaches from the fight plane and pushes tight onto the struck body part (ribs, knee, skull). The body surface goes translucent; **internal organs and skeleton are highlighted** against the dark interior.
3. **Slow-motion beat:** the break plays in slow-mo with **snap/crack sound design** — the audio sells it as much as the visual.
4. **Alternating rhythm:** fight-plane hit → X-ray close-up → fight-plane hit → X-ray close-up (e.g., Scorpion's X-ray: teleport strike shows ribs breaking, then a stomp shows the kneecap breaking). Each close-up targets the body part just hit.
5. **Pull back:** camera returns to the fight plane and the round continues.

Total runtime: **"several seconds"** of close-ups per X-ray — long enough that NetherRealm later decided it was *too* long (see MK11).

### 2e. Why it ends

NetherRealm senior designer **Brian Lebaron** (Twin Galaxies interview): *"One thing that we did not really like was that it took so long, and we want [these attacks] to be really quick and instant."* Length was the stated reason the X-ray system was replaced in MK11.

## 3. MK11 (2019) — the X-ray is dissected into two mechanics

MK11 removed the meter-gated X-ray and split its jobs:

### 3a. Fatal Blow (the comeback weapon)

- **Gate:** available only when the attacker's health is **at or below 30%**. The last third of the health bar is drawn visibly wider as a telegraph.
- **Input:** **R2 + L2 (both triggers)** simultaneously — the same two-button physical gesture as the X-ray, re-gated by health instead of meter.
- **Damage:** ~31% on a clean hit.
- **One-shot rule:** only **one landed Fatal Blow per match**. A blocked or whiffed Fatal Blow goes on a short cooldown and becomes available again — landing it spends it for the match.
- **Punishability:** can be blocked; a Flawless Block makes it even more negative on block with no pushback.
- **Visuals:** a quick cinematic combo — but, unlike MKX, **no full X-ray skeleton sequence** (the "quick and instant" lesson).
- MK11 also split the old unified meter into **offensive and defensive meters**, both starting full and auto-replenishing on cooldown — the resource game moved elsewhere, so the big cinematic no longer needed the meter.

### 3b. Krushing Blow (the X-ray visual, conditional)

- Carries the actual **bone-break X-ray visual** forward.
- Triggered **only under specific conditions** per move (e.g., an uppercut landing as a counter-hit).
- Plays as a **quick slow-mo → X-ray zoom on the impact site** → bonus damage → back to the fight. No long cinematic, no mode switch.
- This is the closest MK11 gets to the MKX X-ray — and it's the pattern `game/js/xray.js` independently follows (conditional hook, ~1.9 s beat, fight resumes).

### 3c. MK1 (2023) — the reconciliation

- Fatal Blows return with the **≤30% health gate and one-shot rule**, but the X-ray visuals are back *inside* the Fatal Blow: hits that used to splatter blood now play X-ray effects on the opponent, "identical to the former X-ray attacks."
- Fixed **35% damage** (adjustable ~30–40% via the Fatal Blow Damage Boost setting).
- A **miniature cinematic intro** plays before the attack — "similar to Super Moves in other fighting games."
- Kameo partners participate in the Fatal Blow with their own segment.

## 4. The visual pipeline: how NRS actually renders an X-ray

Publicly documented pieces (IGN's 2011 "Inside the X-Ray" featurette with lead designer John Edwards, art director Steve Beran, and designer Carlos Pesina; subsequent technical analysis):

1. **Pre-modeled internal anatomy per character.** Every fighter ships with authored skeletal components (dev footage shows skeletal builds for Baraka, Goro, and others) plus organ meshes — built in the normal CG pipeline: concept → model → motion capture → animation. **It is not a shader trick and not real-time simulation** — it's a second, hidden body inside every fighter.
2. **Skin reveal.** At the close-up beat, the skin material fades to translucent (or is cut away in framing) and the internal meshes are **highlighted** — bones and organs rendered bright against darkness.
3. **Authored break animation.** The internal rig plays a short break/deform animation synced to the camera beat. Bones crack along pre-planned fracture points; organs compress.
4. **Cheated fluids.** MK11's own VFX approach (documented in technical analysis): blood and innards are a **"blood library" of 15 pre-made samples** (<155 MB total) covering every splash/spray arrangement — "a flipbook of innards from the area of impact," not fluid simulation. Character bodies are "pure surface" meshes; the gore is pre-baked assets triggered at impact.
5. **Sound design.** Snap/crack SFX are mixed as the primary impact cue — reviewers consistently note the sound sells the break as much as the visual.

**WH pipeline parallel (already in-repo):** `game/js/xray.js` uses the same architecture — skin opacity fades to 0.25, analytic proxy meshes (capsule/ellipsoid/sphere from `anatomy-layers.json`) fade in MUSCLE → BONE → ORGAN, a dent deforms the muscle layer at the impact point using the same math as `SoftBody.hit()`, and the camera pushes to 1.6 m and pulls back. The difference: WH reveals **intact** anatomy (no fracture animation, no fluids, no gore) — the spectacle is illumination, not destruction.

## 5. Input and gating comparison (MK vs WH)

| System | Resource gate | Victim gate | Input | Uses | Length |
|---|---|---|---|---|---|
| MKX X-ray | Full 3-bar meter, spent on fire | none | BL+FK+BK (one press) | unlimited while meter rebuilds | several seconds, multi-beat |
| MK11 Fatal Blow | ≤30% own HP | none | R2+L2 (one press) | 1 landed per match; whiff → cooldown | quick cinematic |
| MK11 Krushing Blow | conditional per move | none | normal move input | unlimited | slow-mo zoom beat only |
| MK1 Fatal Blow | ≤30% own HP | none | R2+L2 | 1 landed per match | mini-cinematic + X-ray hits |
| **WH Soul Climax** | Nine-Soul meter full | victim < 25% HP | **f, F + LP+RP** (motion + 2-button) | once per round (round ends at KO) | ~1.9 s single beat (xray.js) |

## 6. What WH takes and what it leaves

**Takes:**
- The IDEA: anatomy revealed at the impact moment (the user-approved pull).
- The camera grammar: push-in on the struck part, brief slow-mo, pull back — compressed to a single ~1.9 s beat instead of MKX's several-second multi-beat sequence (Lebaron's "quick and instant" lesson).
- The comeback-weapon gating philosophy: a big swing gated by a visible resource state (MK11's 30% rule → WH's meter-full + victim-weak rule).
- The Krushing Blow pattern: conditional X-ray visual on a normal fight blow, no mode switch (matches `xray.js`'s R./US.2+3 hook).
- Pre-modeled anatomy + cheated effects over simulation (matches the analytic-proxy approach in `xray.js`; no per-frame meshing).

**Leaves:**
- Lethality and gore: no broken bones as destruction, no blood/flipbook innards, nobody dies (owner law).
- Mode-switch cinematics: the fight flow never breaks (Tekken law; MK's "FINISH HIM" daze-state model is rejected).
- One-press supers: WH uses a Tekken-style motion + button input, not BL+FK+BK / R2+L2 (owner directive: complex inputs like Tekken super moves).
- The word "fatality": the system needs its own Eastern Mind name (see FINISHER-DESIGN §10).

---

### Sources (public, retrieved 2026-10-23)

- SuperCombo Wiki — "Mortal Kombat X/Offense" (X-ray: 3 bars, BL+FK+BK): https://wiki.supercombo.gg/index.php?title=Mortal_Kombat_X/Offense&diff=next&oldid=99535
- SuperCombo Wiki — "Mortal Kombat 9/Universal Abilities/X-Ray Attacks": https://wiki.supercombo.gg/index.php?title=Mortal_Kombat_9/Universal_Abilities/X-Ray_Attacks&oldid=47799
- GamePressure — "Mortal Kombat X: X-Ray special techniques": https://www.gamepressure.com/mortalkombatx/x-ray-special-techniques/z47742
- IGN via Mortal Kombat Online — "Inside the X-Ray Special Feature!" (NRS featurette, Edwards/Beran/Pesina): https://www.mortalkombatonline.com/t/mk2011/ign-inside-the-x-ray-special-feature/0QpRAhLq4A8e
- Cultured Vultures — "Mortal Kombat 11 Isn't Afraid Of Change" (Fatal Blow details): https://culturedvultures.com/mortal-kombat-11-isnt-afraid-of-change/
- GoSunoob — "Mortal Kombat 11 Fatal Blows - How to Do": https://www.gosunoob.com/guides/mortal-kombat-11-fatal-blows-how-to-do/
- GameSpot — "Mortal Kombat 11 Beginner's Guide" (Fatal Blow ≤30%, 31%, one per match): http://gamespot.com/gallery/mortal-kombat-11-beginners-guide-13-tips-to-get-yo/2900-2725/
- GameRant — "How Mortal Kombat 1's X-Ray Moves Compare to Mortal Kombat 11's" (Krushing Blow / MK1 reconciliation): https://gamerant.com/mortal-kombat-1-mk11-xray-fatal-krushing/
- KeenGamer — "Mortal Kombat 1: An Overview of Recent Reveals and Features" (X-ray return, Fatal Blow + Kameo): https://www.keengamer.com/articles/news/mortal-kombat-1-an-overview-of-recent-reveals-and-features/
- SVG — "Things You Won't Be Able To Do In Mortal Kombat 11" (Lebaron "quick and instant" quote): https://www.svg.com/148893/things-you-wont-be-able-to-do-in-mortal-kombat-11/
- WhatCulture — "Mortal Kombat X Trailer: 6 Things You Need To Know" (camera zooms to body part, organs highlighted): https://whatculture.com/gaming/mortal-kombat-x-trailer-6-things-need-know?page=5
- CharlieIntel — "What are Fatal Blows in Mortal Kombat 1?" (35%, ≤30%, blocked → cooldown): https://www.charlieintel.com/mortal-kombat/mortal-kombat-1-fatal-blows-267642/
