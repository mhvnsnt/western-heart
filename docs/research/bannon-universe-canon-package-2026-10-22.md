# Bannon Universe — Canon Package (Raw Material Inventory)

**Worker 49 — 2026-10-22.** The consolidated canon reference for the Bannon/Ashlane/BrutalFist
sub-universe. This is the RAW MATERIAL inventory: every fighter's identity / character / moves /
bones / hitboxes data as the owner authored it. It does NOT contain canon bridges into
Western Heart (worker 48's lane) — it is the source worker 48 and all future canon work draws on.

**Canon sources (precedence order):**
1. `mhvnsnt/Bannon` repo — "Off The Top Rope cast and characters .txt" (Book 3 master roster, 41
   characters, faction matrix). The owner's definitive narrative canon.
2. `mhvnsnt/brutalfistgrokversion` — `native/media/characters/chara_bannon/` TXT package
   (identity / character / moves / bones / hitboxes). The engine-format "off the top rope canon"
   template every fighter's data package follows.
3. `mhvnsnt/brutalfistgrokversiontenpointfive` — `src/data/bannonRoster.ts` (27 playable-fighter
   profiles: bio, personality, style, stats, full defaultMoveSet), `src/data/canonPronouns.ts`
   (canon pronouns — never infer from the mesh), `public/models/` (the 28 model set),
   `public/motion/` (Mixamo JSON motion bank the `bf_*` move aliases resolve into).
4. `mhvnsnt/AshLane-prototype` — `public/models/cast/SOMBRA_NEGRA_rigged.glb` (28th fighter).

**Sub-universe law (owner):** the Bannon universe is a SUB-UNIVERSE of the Western Heart
multiverse. Ashlane characters keep their existing bios/backstories from their repos, then each
gets a "how they arrived" bridge (the call, the trial, Tong-Nou, lost souls). All writing laws
apply: adults only, canon-grounded, no Tekken names in canon.

---

## 1. The template: Bannon's full data package

`native/media/characters/chara_bannon/` in `mhvnsnt/brutalfistgrokversion`. Every fighter's
package follows this exact schema.

### bannon.identity.txt (verbatim)
```
BannonId=bannon
DisplayName=Bannon
Bio=The physical nucleus and absolute force of the Bannon Engine. Driven by raw physics and unmatched grit.
SourceGLB=native/source/BANNON_rigged.glb
Policy=REAL_GLB_ONLY
MeshFormat=DirectX.x
Triangles=17998
Bones=58
```

### character.txt (verbatim)
Engine config: `#NAME Bannon`, `#SHORTNAME Bannon`, `#AI_TYPE aggressor`, `#MOVESFILE moves.txt`,
`#BONESFILE bones.txt`, `#LIFE 250.0`, `#WALKSPEED 60.0`, `#WEIGHT 1.1`, `#HIT_SFX hit.png`.
Animation bindings (all fighters map states onto the locomotion bank): STANCE/WALKING/RUNNING/
SIDESTEP → `idle 0 115` / `walkFast 0 30` / `running 0 20`; STANDGUARD/CROUCHGUARD/CROUCHING/
LOWSTANCE → idle; all 16 HIT*/WAKEUP/GROUNDED*/WINPOSE/INTRO/JUMPING reactions → `idle 0 N`
(placeholders — per-move hit anims are the gap the teardown banks fill).

### moves.txt (verbatim)
Two authored moves; the rest of the kit comes from the engine bank:
- **Jab** — input `A`, range 0.0–90.0, anim `idle`, frames 0–12, stance Ground, 120ms delay.
- **Heavy** — input `B`, range 0.0–110.0, anim `idle`, frames 0–18, stance Ground, 200ms delay.

### bones.txt (verbatim) — the canonical 23-bone map
All 23 canonical bones bind to `mixamorig_*` rigs (every Bannon GLB is Mixamo-rigged; e.g.
TARZANIAN_DEVIL / FINXSSE banked at 58 Mixamo joints):
```
HEAD→mixamorig_Head  NECK→mixamorig_Neck  TORSO→mixamorig_Spine2  SPINE→mixamorig_Spine
HIPS→mixamorig_Hips  SHOULDER_L/R→mixamorig_LeftShoulder/RightShoulder
ELBOW_L/R→mixamorig_LeftArm/RightArm  WRIST_L/R→mixamorig_LeftHand/RightHand
LEG_L/R→mixamorig_LeftUpLeg/RightUpLeg  KNEE_L/R→mixamorig_LeftLeg/RightLeg
ANKLE_L/R→mixamorig_LeftFoot/RightFoot  FOOT_L/R→mixamorig_LeftToeBase/RightToeBase
THUMB_L/R→mixamorig_LeftHandThumb2/RightHandThumb2
FINGERS_L/R→mixamorig_LeftHandIndex2/RightHandIndex2
```

### additionalHitboxes.txt
Empty for Bannon (0 bytes) — hitboxes are procedural (cf. `BannonProceduralStrikeHitbox` in the
Bannon engine repo). Per-fighter hitbox tuning is unwritten; the base hitbox model is the
shared procedural system.

### Mesh + animations
- `Mesh1/BF_bannon.x` (3.4MB DirectX .x), `bannon.png`, `portrait.png`, `fightPreview.png`,
  `selectionPreview0.png`; `config.txt`: outfit `Classic_Black_and_Gold`, `AVAILABLE_FROM_START 1`,
  mesh scale 6.383048.
- `animations/idle.x`, `animations/running.x`, `animations/walkFast.x`.
- `roster.ini`: `chara_bannon  0` (roster slot 0).

---

## 2. The 28 fighters — identity / character / moves / bones / hitboxes

Bones/hitboxes for all 28 follow the §1 template (23-bone Mixamo map; procedural hitboxes).
What differs per fighter is listed below. Move aliases (`bf_*`) resolve into the
`public/motion/` Mixamo JSON bank (CHOKESLAM, DDT, GERMANSUPLEX, BOXING__1–5, GINGA_*, etc.).

### 1. BANNON — he/him — `bannon`
- **Role:** Protagonist / Power Wrestler. **Faction:** AWE (Rebel), alliance.
- **Stats:** poise 95, hp 10000, speed 85, strength 90, scale 1.1. **Payback:** Beast Mode. **Manager:** none.
- **Bio:** The physical nucleus and absolute force of the Bannon Engine. A redeemed anti-hero who
  found true loyalty after shedding control. Fights to prove that authentic expression and loyalty
  are stronger than corporate control.
- **Personality:** Quiet, intensely focused on philosophy and numerology. Seeks authentic emotional
  connection. Hates pretense. Driven artist who views every match as a statement.
- **Style:** Power Wrestling / Technical Hybrid. Explosive grapples, heavy strikes, high-impact
  throws. Payback finisher activates when poise is broken.
- **Moves:** idle bf_idle_wide · walk bf_walk_lumber / bf_walk_back_injured · crouch bf_crouch ·
  guard bf_guard · light bf_jab · heavy bf_cross · lowKick bf_low_kick · highKick bf_high_kick ·
  combo bf_jab_cross_hook · counter bf_reversal · grapple bf_clinch · throw bf_powerbomb ·
  knockdown bf_knockdown · wakeup bf_wakeup · hitReact bf_hit_reaction · ko bf_ko ·
  signature bf_beast_mode · extras bf_uppercut, bf_body_slam.
- **Models:** BANNON.glb, BANNON_muscular.glb (+_rig28, _rigready, _skinned), BANNON_rigged.glb
  (playable). **Book 3 alias:** Marquis Whitacre (The Free Agent).

### 2. MAIME — he/him — `maime`
- **Role:** Technical Striker. **Faction:** AWE, alliance.
- **Stats:** poise 85, hp 10000, speed 90, strength 78, scale 1.0. **Payback:** Precision Protocol.
- **Bio:** A precise, technically gifted fighter whose speed and accuracy make him a constant threat.
  Fights with calculated efficiency, never wasting a movement.
- **Personality:** Methodical and focused. Speaks little but observes everything. Finds beauty in
  perfect technique. **CANON FACT:** Maime is Marquis Whitacre / Bannon's alter — three facets of
  one man (canon/04_book4_core_unlocked.md). Book 5: "Maime drew his machete. He looked at Iida."
- **Style:** Technical Striking / Speed. Fast combos, precise counters, quick throws. Punishes mistakes.
- **Moves:** idle bf_idle_box · walk bf_walk_prowl / bf_walk_back_box · light bf_jab_fast ·
  heavy bf_straight · lowKick bf_leg_kick · highKick bf_roundhouse · combo bf_jab_cross_lead_hook ·
  counter bf_slip_counter · grapple bf_clinch_muay_thai · throw bf_hip_toss · signature bf_precision_rush ·
  extras bf_elbow_slash, bf_knee_strike. (knockdown/wakeup/hitReact/ko: bank defaults)
- **Models:** MAIME.glb, MAIME_skinned.glb, MAIME_tattered.glb (+_skinned). **Book 3 alias:** Atlas Vance (The Anchor).

### 3. ONYX — `onyx`
- **Role:** Dark Powerhouse / God Within conduit. **Faction:** independent (chaos-adjacent).
- **Stats:** poise 90, hp 11000, speed 70, strength 95, scale 1.15. **Payback:** God Within.
- **Bio:** A vessel of the God Within. Onyx teams with Cipher (as her minion) and Echo in God
  Within mode appearances; Hollow, Static, Echo, Cipher all orbit her God Within faction.
- **Personality:** Dominant, ritualistic. Speaks in proclamations.
- **Style:** Power / dark aura grappling. Slow, inexorable, devastating throws.
- **Moves:** idle bf_idle_menace · walk bf_walk_heavy / bf_walk_back_heavy · light bf_claw_swipe ·
  heavy bf_lariat · lowKick bf_stomp · highKick bf_big_boot · combo bf_claw_lariat_slam ·
  counter bf_dark_reversal · grapple bf_choke_lift · throw bf_godwithin_driver ·
  signature bf_godwithin_ascension · extras bf_abyss_slam, bf_soul_crush.
- **Models:** ONYX.glb, ONYX_corset.glb (+_rig28, _rigready, _skinned), ONYX_rig28.glb,
  ONYX_rigready.glb, ONYX_skinned.glb, ONYX_straightjacket.glb, ONYX_street.glb.

### 4. CAIN_ELIAS — he/him — `cain_elias`
- **Role:** Enforcer / Past Trauma. **Faction:** AWE (Corporate Structure).
- **Stats:** poise 92, hp 10500, speed 75, strength 93, scale 1.12. **Payback:** Final Verdict.
- **Bio:** Kennedy's most trusted, cold-hearted weapon. A physical test of Marquis's emotional resolution.
- **Personality:** Cold, professional, vindictive. No wasted words.
- **Style:** Technical Power / Vindictive. Finisher: The Final Verdict (Tombstone Piledriver).
- **Moves:** idle bf_idle_cold · walk bf_walk_stalk / bf_walk_back_stalk · light bf_jab_heavy ·
  heavy bf_overhand · lowKick bf_shin_kick · highKick bf_head_kick · combo bf_jab_overhand_hook ·
  counter bf_catch_counter · grapple bf_front_headlock · throw bf_tombstone · signature bf_final_verdict ·
  extras bf_chokeslam, bf_powerbomb.
- **Models:** CAIN_ELIAS_gear.glb, CAIN_ELIAS_godwithin.glb, CAIN_ELIAS_ring.glb,
  CAIN_ELIAS_snakeskin.glb (ring/entrance/cutscene/street + snakeskin variants).
- **Book 3 alias:** Cain Elias (The Executioner).

### 5. STICKUP — he/him — `stick_up`
- **Role:** The Weapon / Consequence. **Faction:** JPCW conspiracy (Corporate Structure).
- **Stats:** poise 88, hp 10000, speed 80, strength 88, scale 1.05. **Payback:** Optimization Drive.
- **Bio:** The consequence of lost will. A controlled machine used for brutal efficiency.
- **Personality:** Machine-like, obedient, no self.
- **Style:** Technical / Brutal Hybrid. Finisher: The Optimization Drive (Exploder Suplex).
- **Moves:** idle bf_idle_machine · walk bf_walk_march / bf_walk_back_march · light bf_chop ·
  heavy bf_clothesline · lowKick bf_low_kick · highKick bf_high_kick · combo bf_chop_clothesline_slam ·
  counter bf_auto_reversal · grapple bf_german_setup · throw bf_exploder · signature bf_optimization_drive ·
  extras bf_brainbuster, bf_sitout_powerbomb.
- **Models:** STICKUP.glb. **Book 3 alias:** Stick-Up (Cyborg).

### 6. CIPHER — `cipher`
- **Role:** Feral Chaos Striker. **Faction:** God Within (Onyx's minion).
- **Stats:** poise 70, hp 9000, speed 97, strength 75, scale 0.98. **Payback:** Feral Break.
- **Bio:** "Blackheart Lio Rush feral black sludge psycho maniac." Teamed with Onyx as a minion in
  God Within mode. Pure manic energy.
- **Personality:** Manic, feral, laughing mid-fight. Unpredictable.
- **Style:** Feral high-speed striking / sludge brawling.
- **Moves:** idle bf_idle_feral · walk bf_walk_skitter / bf_walk_back_skitter · light bf_feral_jab ·
  heavy bf_feral_cross · lowKick bf_drop_kick · highKick bf_enzuigiri · combo bf_feral_flurry ·
  counter bf_crazy_counter · grapple bf_rabid_clinch · throw bf_tornado_ddt · signature bf_blackheart_break ·
  extras bf_450_splash, bf_poisonrana.
- **Models:** CIPHER.glb, CIPHER_feral.glb, CIPHER_minion.glb, CIPHER_rigged.glb (+_rig28).
- **VF5 mapping (candidate):** Goh Hinogami.

### 7. ECHO — `echo`
- **Role:** God Within Striker. **Faction:** God Within (Onyx/Cipher team).
- **Stats:** poise 75, hp 9500, speed 92, strength 80, scale 1.0. **Payback:** Echo Chamber.
- **Bio:** Teamed with Onyx and Cipher in God Within mode (Shotzi Blackheart vs Lio Rush Blackheart
  inspired appearance).
- **Personality:** Echoing, mirroring, taunting.
- **Style:** High-speed mirroring striker.
- **Moves:** idle bf_idle_echo · walk bf_walk_bounce / bf_walk_back_bounce · light bf_jab ·
  heavy bf_spinning_backfist · lowKick bf_capoeira_kick · highKick bf_spinning_heel ·
  combo bf_echo_flurry · counter bf_mirror_counter · grapple bf_clinch · throw bf_german_snap ·
  signature bf_echo_chamber · extras bf_hurricanrana, bf_springboard_crossbody.
- **Models:** ECHO.glb.

### 8. CODY — he/him — `cody`
- **Role:** Fallen Manager / Toxic Pawn. **Faction:** AWE (Corporate Structure).
- **Stats:** poise 60, hp 8500, speed 78, strength 70, scale 1.0. **Payback:** Corduroy Crash.
- **Bio:** Marquis's former manager, used for distraction and personal attack. Sober/stressed duality
  (two attires: sober vs stressed).
- **Personality:** Sycophantic, bitter, scheming. Managerial interference.
- **Style:** Cowardly opportunist / propaganda. Managerial interference.
- **Moves:** idle bf_idle_smug · walk bf_walk_strut / bf_walk_back_strut · light bf_sl
...[truncated 20634 chars]