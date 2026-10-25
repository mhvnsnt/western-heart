# MK X-ray Technique Research — 2026-10-23

**Researcher:** MK X-ray technique subagent (DoggByte crew)
**Purpose:** Understand HOW Mortal Kombat implements X-ray attacks (MK9, MKX, MK11)
so we can adapt the *technique* to Western Heart's Tekken-style gameplay.
**Rule observed:** Technique research only — no MK assets, animations, or
character designs copied. Everything below is written from published
descriptions of the games' observable behavior.

---

## 1. X-ray sequence breakdown (MK9 / MKX)

### 1.1 Timing and trigger

- **Meter requirement (MK9):** 3-segment X-Ray Meter. Fighters start the round
  with 1 bar; meter persists across rounds; the "First Attack" bonus grants
  a full bar. Meter fills from: taking damage (~45% damage taken ≈ 1 bar),
  performing special moves (+6% of a bar each), and opponents blocking your
  attacks (~9% of a bar per block). Blocking damage gives no meter.
- **Input (MK9):** Front Kick + Back Kick + Block pressed together — an input
  that behaves like a special move (cancelable into from the same normals as
  other specials). (MKX: Stance Change + Block.)
- **Startup:** The X-ray begins with a physical starter hit (or in some cases
  a counter / grab condition, e.g. Johnny Cage's X-ray only activates on a
  successful counter). **The cinematic is conditional** — the full sequence
  only plays if the starter connects. If it whiffs, is blocked, or is dodged
  (MKX), the X-ray is spent, meter is gone, and the attacker is vulnerable.
- **Duration:** No official number published; measured from gameplay footage
  an MK9/MKX X-ray cinematic runs roughly **6–9 seconds** from starter to
  return-to-neutral. MK11's Fatal Blow (the X-ray successor) runs
  **~8–12 seconds** including startup. The user's planned WH version is
  **~1.9 s** — significantly shorter, so it must compress beats, not run the
  full MK sequence.

### 1.2 Camera behavior during X-ray

- **Slow motion first:** Combat slows as the sequence triggers (this also masks
  the frame-rate drop from 60 fps gameplay to 30 fps cinematics on PC —
  slow-mo hides the transition).
- **Desaturation:** The scene desaturates at sequence start (Kotaku E3 2010
  hands-on; still true in later games). This acts as a universal visual flag:
  "you are now in the X-ray sequence."
- **Zoom + cut per impact:** The camera zooms in close on each body part being
  hit and cuts between angles for each blow in the sequence (ribs → knee →
  skull, etc.). Each beat of the combo gets its own camera framing.
- **Free camera:** During the sequence the camera is no longer constrained to
  the fight plane — it can orbit, push through geometry, and take viewpoints
  impossible in normal play (e.g. inside the victim's body).

### 1.3 Layer reveal — how the internal damage is shown

- **"X-ray window":** On each impact the victim's body becomes a window into
  itself — the exterior goes translucent and the interior layers are revealed:
  **skin → muscle → bone**, then organ damage.
- **Per-impact anatomical beat:** Each blow in the combo maps to one internal
  damage beat: bone shattering, organs bleeding/rupturing, teeth flying. The
  visual progression per beat is: impact flash → translucent body → bone
  deformation → break → blood/organ consequence.
- **Rendering trick (technical analysis):** The characters are "pure surface"
  meshes — there is no real interior. NetherRealm cheats the interior with
  **pre-modeled anatomical parts (skull, ribcage, organs) that are hidden and
  revealed**, plus particle/animated "flip-book of innards" emitted from the
  impact area to sell the idea of fluid and tissue. Damage is 2-keyframed at
  minimum: frame 1 bone intact, frame 2 bone broken (a PC-version critic
  noted MKX X-rays are effectively 2-frame: intact → broken on impact).
- **Audio sells it:** Snap/crack effects are as important as the visuals.

### 1.4 Damage visualization details

- **Bones:** cracks propagate then the bone visibly snaps — segments separate
  and displace, often with small fragment particles.
- **Organs:** bleeding and rupture shown as internal hemorrhage — dark red
  blooms visible through the translucent body; organs squash/deform under
  the impact point.
- **Soft tissue:** blood splatters are physics-based (splatter direction,
  attachment to character, darkening over time).
- **No mechanical effect:** In MK the broken bones have zero effect on the
  fight afterwards — purely visual feedback for a big-damage moment
  (~35% health in MK9; 310–340 damage in MK11, ~30% of health).

### 1.5 Flow integration — does it pause the fight? Can it be blocked?

- **MK9/MKX:** The X-ray is a real in-flow move. The starter hit can be
  **blocked, dodged, or whiffed** — it is NOT guaranteed. Once the cinematic
  starts, the opponent cannot break out (in MK9, an X-ray combo is
  unbreakable). Control returns to both players after the sequence.
- **MK11 Fatal Blow (successor):** Trigger changes to a comeback gate —
  available only at **≤30% health**, input = both triggers. Two stages:
  (1) initial armored hit (armor activates after 8 frames; first hit = fixed
  20 damage), (2) uninterruptible cinematic cutscene. **Once per match**
  (not per round). Whiff/block/interrupt → ~9-second cooldown before reuse.
  Total damage ~310–340 (~30% health).
- **Interactive cinematic (MK11):** During the Fatal Blow cutscene BOTH players
  press a button in rhythm with the attacks — the attacker gains extra damage
  (skull icons), the defender mitigates (shield icons). The cinematic is
  watchable but participatory.
- **Krushing Blows (MK11):** Short X-ray moments attached to specific moves
  when conditions are met (counter-hit, punish, distance, etc.) — the camera
  zooms and shows internal damage for a single beat WITHOUT a full cinematic
  takeover. This is the "distributed" version of the technique: cheap, fast,
  in-flow.

---

## 2. Fatality staging technique

### 2.1 Trigger and staging

- **Trigger window:** After winning the final round, the announcer plays
  "FINISH HIM/HER" and the game enters a special state — the opponent stands
  helpless, the player has a short input window (roughly 4–5 seconds) to
  enter a specific directional + button sequence at a required distance
  (Close / Mid / Far).
- **What the technique does:**
  - Match logic pauses; the loser is put into a passive "victim" animation
    state (dazed/idle), the winner plays a pre-authored cinematic routine.
  - The camera detaches from the fight plane completely — free cinematic
    framing, cuts, orbits, and slow motion are all fair game since nothing
    is interactive anymore.
  - The victim's body is treated as a prop: it can be dismembered, have
    organs pulled out, etc. via pre-modeled anatomical parts + gore
    particles + ragdoll physics blending into the scripted animation.
- **Key design point:** Fatalities are *match-ending* — they don't have to
  preserve game state afterwards. That freedom (camera, destruction, time)
  is why they look so good. Any in-match technique (X-ray, Rage Art) must
  budget its camera and timing against *returning to a playable state*.

### 2.2 Camera and animation technique in fatalities

- **Camera:** full cinematic grammar — establishing frame, punch-in zooms,
  cuts on each gore beat, occasional free orbit. Same 30 fps cinematic
  treatment as X-rays.
- **Animation blending:** Scripted animation drives the winner and the
  victim's body through each beat; ragdoll/physics particles handle loose
  parts (blood, fragments) for dynamism. The victim's skeletal mesh is the
  same rigged character model used in-fight — no special "fatality model" —
  with hidden interior parts revealed by the choreography.
- **Audio/visual layering:** Desaturation is NOT used in fatalities (it's the
  X-ray marker); fatalities use slow-motion, sound design (squash, crack,
  tear), and per-beat camera cuts instead.

---

## 3. The X-ray technique, distilled (what MK is actually doing)

Five discrete systems work together:

1. **Gate:** resource (meter) or state (low health) + conditional starter hit.
2. **Flag:** desaturation + slow-mo + camera zoom tell the viewer "sequence
   mode is on." Frame-rate drops are hidden inside the slow-mo.
3. **Anatomy reveal:** translucent exterior, pre-modeled interior parts
   (bones, organs) revealed per beat; no real interior simulation —
   it's keyframed states (intact → broken) plus particles.
4. **Per-beat camera:** each impact gets its own framing; camera breaks the
   fight plane.
5. **Return:** clean handoff back to gameplay (or match-end for fatalities).

---

## 4. Recommendations: Tekken-style adaptation for Western Heart

**Constraint:** WH X-ray fires on **Rage Art KO** — the fight is already over.
That gives us the fatality-side freedom (no return-to-neutral budget) but
the user's target is a tight **~1.9 s** sequence, so every beat must earn its
frames. 1.9 s at 60 fps = ~114 frames.

### 4.1 Beat plan (~114 frames)

| Time | Frames | Beat |
|---|---|---|
| 0.0–0.3 s | 0–18 | KO impact lands → slow-mo ramp (drop to ~20% speed), scene desaturates, camera punches in on impact point |
| 0.3–1.1 s | 18–66 | INTERNAL DAMAGE beats: 2–3 anatomical beats max (e.g. ribcage → skull), each ~0.25–0.3 s: translucent body → bone crack → bone break → organ consequence |
| 1.1–1.6 s | 66–96 | Final beat + zoom out to body, blood/gore particle peak |
| 1.6–1.9 s | 96–114 | Re-saturate, slow-mo releases, camera returns to fight position, match-end state |

### 4.2 Tekken-specific differences from MK

- **Camera stays in-world:** Tekken fights play out on a 3D stage with a
  free-moving camera; keep the X-ray camera on the fight plane's side of the
  action (zoom in, don't fully detach) so it still reads as *the fight*,
  not a cutaway. Use MK's per-beat re-framing but keep spatial continuity
  with where the fighters were.
- **No 30 fps drop needed:** We run the sequence at gameplay frame rate in
  slow motion — the slow-mo IS the transition, exactly how MK masks its
  cinematic frame-rate change.
- **Desaturation as the flag:** Steal this directly — it's the cheapest,
  most legible "sequence mode" signal and costs no animation budget.
- **Reuse the anatomy cheat:** No real interior simulation. Ship
  pre-modeled skeleton/organ parts per fighter (or one shared anatomical
  layer weighted to the fighter's rig), hidden until the X-ray beats, with
  2-state bones (intact → cracked → broken) and particle blood. This is how
  MK gets away with it; we can too.
- **Krushing-Blow-style micro-X-rays are the real prize for in-flow:**
  WH could attach a single-beat camera zoom + internal-damage flash to
  specific heavy moves (e.g. counter-hit launchers, Rage Drive hits) WITHOUT
  taking control away. This is the MK11 Krushing Blow pattern — it gives the
  X-ray payoff repeatedly per match instead of once per Rage Art, and it
  doesn't cost the 1.9 s budget.

### 4.3 Gate and interaction notes

- Rage Art already has its own gate (Rage state) — the X-ray is a bonus
  visual layer on the KO, so no extra meter/integration work is needed
  beyond the KO detection.
- Keep the X-ray **non-interactive** (unlike MK11's button-press minigame):
  at 1.9 s there's no room for it, and the match is over anyway.
- Optional later: WH equivalent of Krushing Blows could tie into the Nine-Soul
  Meter (canon system) for conditioned micro-X-rays — design call for the
  user, not this research.

---

## Sources consulted

- SuperCombo Wiki — MK9 X-Ray Meter, X-Ray Attacks; MK11 Offense (Fatal Blow)
  (wiki.supercombo.gg)
- GameSpot — "Mortal Kombat 11: All Fatal Blows" (gamespot.com)
- ScreenRant — "Mortal Kombat 11 Fatal Blows Explained" (screenrant.com)
- GameRAnx — "Mortal Kombat 1: How To Use a Fatal Blow" (gameranx.com)
- Digital Trends — "How to do Fatal Blows in Mortal Kombat 11" (digitaltrends.com)
- Kotaku — "The New Mortal Kombat Cuts Deeper Than Ever Before" (kotaku.com)
- Digital Foundry — "Face-Off: Mortal Kombat X" (digitalfoundry.net)
- GamePressure — "MK X: X-Ray special techniques" (gamepressure.com)
- PlayStationLifeStyle — "Mortal Kombat is One of E3 2010's Best Games"
  (playstationlifestyle.net)
- PSX Extreme — "Mortal Kombat Review" (psxextreme.com)
- WhatCulture — MKX trailer breakdown; MK12 wishlist (whatculture.com)
- ExitLag — "Mortal Kombat 1 Fatalities: Every Finishing Move Explained"
  (exitlag.com)
- ImageQualityMatters — "Tech Analysis: Mortal Kombat Demo (PS3)"
  (imagequalitymatters.blogspot.com)

**Standing rule respected:** technique only; no MK assets, animations,
character designs, or move data reproduced. MK names appear only as
technique references in this research doc.
