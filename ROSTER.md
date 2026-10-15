# WESTERN HEART — ROSTER
## The Nine Souls

**Body replacement (owner order 2026-10-15):** T3 default bodies are being replaced with T6, TTT2, or better (preference T6 > TTT2 > T7-style). 6 of 9 souls now default to T7-style bodies (RigModels fan rips via PR #170) — see `docs/souls/SOUL-BODY-REPLACEMENT.md` for the per-soul map. T3 TMD extractions move to legacy (last attire; extraction still pending teardown). BYOU is blocked pending the owner's Lei naming decision; TOU and GYOU are pending T6/TTT2 extraction (no T7-style Paul or Hwoarang models exist yet).

Nine fighters. Each is a lost soul of Tong-Nou. Each soul's **body** is a Tekken 3 TMD model extraction (geometry only — the donor, not the character). Each soul's **skin** is recombined Eastern Mind bitmap extractions. Each soul's **moveset** is a Tekken 3 fighting style, reinterpreted through the soul's nature.

**Asset rule:** No new models. No new textures. Body + skin + moveset are all recombined extractions. See `asset-manifest.md` for source tracing.

**Note on soul details:** Full visual/personality reference for each soul comes from the Eastern Mind extraction (in-game sprites, the Illustrated Book). Style assignments below are the design framework; the extraction refines them.

---

### 1. RIN — The Protagonist Soul
- **Nature:** 凛 — dignified, cold, self-possessed. The soul the player begins as. Remembers nothing but the trial.
- **Fighting style:** Mishima-style karate (Tekken: Jin Kazama's moveset) — precise, fundamental, the "honest" style. Rin is the baseline every other soul deviates from.
- **Body donor:** Jin Kazama TMD — young fighter's build, unadorned (legacy attire, last; extraction pending teardown).
- **Default body:** `game/assets/models/rin-body.glb` — T7-style Jin (RigModels fan rip, via Demonio's T7 model).
- **Skin:** Eastern Mind protagonist-sprite extractions. Cold blue-white palette (kimono-dye winter tones).
- **Archetype:** The shoto. Balanced. The soul learning itself.

### 2. BYOU — The Sick Soul
- **Nature:** 病 — sickness. A soul that twitches, stutters, moves wrong. Its illness is its weapon — opponents can't read a body that doesn't obey itself.
- **Fighting style:** Lei Wulong's Five Animals kung fu (Tekken) — deceptive, stance-shifting, deliberately unreadable. The drunken-sick master.
- **Body donor:** Lei Wulong TMD — loose-limbed, expressive.
- **Default body:** PENDING — owner decision needed (Lei's WH fighter name unmapped as of 2026-10-15; `rave.glb` T7-style Lei exists on PR #170). T3 TMD remains the documented body until the owner unblocks.
- **Skin:** Eastern Mind sick/decay sprite extractions. Jaundiced yellows, infected greens.
- **Archetype:** The trickster. Stance-dance, unpredictability.

### 3. TOU — The Fighting Soul
- **Nature:** 闘 — battle itself. The soul that exists only to fight. No philosophy, no fear. The purest expression of the trial.
- **Fighting style:** Paul Phoenix's power karate/judo hybrid (Tekken) — devastating single strikes, the Death Fist. Maximum damage, minimum subtlety.
- **Body donor:** Paul Phoenix TMD — heavy, powerful build.
- **Default body:** PENDING — no T7-style Paul model exists yet (not in PR #170). Needs T6/TTT2 extraction. T3 TMD remains the documented body until then.
- **Skin:** Eastern Mind warrior-sprite extractions. Blood reds, scorched oranges (Fire force).
- **Archetype:** The grappler/brawler. High damage, honest.

### 4. SHA — The Sand Soul
- **Nature:** 沙 — sand, desert. From the Sha-mo Desert of the Land of Life. A soul that flows, erodes, surrounds. Never where you struck.
- **Fighting style:** Ling Xiaoyu's Baguazhang (Tekken) — flowing, circular, evasive. The art of not being hit.
- **Body donor:** Ling Xiaoyu TMD — small, agile frame (legacy attire, last; extraction pending teardown).
- **Default body:** `game/assets/models/sha-body.glb` — T7-style Xiaoyu (RigModels fan rip, via Saku Ra's T7 model).
- **Skin:** Eastern Mind desert-sprite extractions. Sand ochres, bleached bone whites.
- **Archetype:** The evasive. Movement as defense.

### 5. KAI — The Sea Soul
- **Nature:** 海 — the sea. Fluid, rhythmic, unstoppable. Fights like water — finds every opening.
- **Fighting style:** Eddy Gordo's Capoeira (Tekken) — rhythmic, ground-flowing, relentless pressure. The tide that doesn't stop.
- **Body donor:** Eddy Gordo TMD — long-limbed, acrobatic (legacy attire, last; extraction pending teardown).
- **Default body:** `game/assets/models/kai-body.glb` — T7-style Eddy (RigModels fan rip, via King Tyrant's T7 model).
- **Skin:** Eastern Mind water-sprite extractions. Deep blues, foam whites, abyssal blacks (Water force).
- **Archetype:** The rushdown. Relentless rhythm offense.

### 6. JIN — The Blade Soul
- **Nature:** 刃 — the blade. A soul that cuts. Precise, ritual, terrifying. (Not to be confused with RIN, the protagonist.)
- **Fighting style:** Yoshimitsu's advanced ninjutsu (Tekken) — sword techniques, teleportation stances, self-damaging power moves. The blade that cuts both ways.
- **Body donor:** Yoshimitsu TMD — armored, masked, inhuman (legacy attire, last; extraction pending teardown).
- **Default body:** `game/assets/models/jin-body.glb` — T7-style Yoshimitsu (RigModels fan rip, via Phantom's T7 model). (This is JIN 刃, the Blade Soul — not to be confused with RIN 凛.)
- **Skin:** Eastern Mind blade/spirit extractions. Polished steel grays, shrine-vermillion accents.
- **Archetype:** The wildcard. High-risk tools, stance complexity.

### 7. RETSU — The Violent Soul
- **Nature:** 烈 — violence, intensity. A soul of pure destructive force. The Helix Palace's Destruction room made flesh.
- **Fighting style:** Bryan Fury's kickboxing (Tekken) — brutal, bone-breaking, no wasted motion. Every hit is meant to end the fight.
- **Body donor:** Bryan Fury TMD — scarred, heavy, military (legacy attire, last; extraction pending teardown).
- **Default body:** `game/assets/models/retsu-body.glb` — T7-style Bryan (RigModels fan rip, via Skull's T7 model).
- **Skin:** Eastern Mind destruction-sprite extractions. Charcoal blacks, molten cracks (Metal force).
- **Archetype:** The bruiser. Counter-hit monster.

### 8. ZEN — The Still Soul
- **Nature:** 禅 — meditation, stillness. A soul that barely moves — and doesn't need to. The calm center of the storm.
- **Fighting style:** Julia Chang's Xingyiquan (Tekken) — internal martial art, minimal movement, explosive short power. Stillness that kills.
- **Body donor:** Julia Chang TMD — compact, grounded (legacy attire, last; extraction pending teardown).
- **Default body:** `game/assets/models/zen-body.glb` — T7-style Julia (RigModels fan rip, via Nightwolf's T7 model).
- **Skin:** Eastern Mind meditation-sprite extractions. Temple-stone grays, incense-smoke whites (Earth force).
- **Archetype:** The counter-fighter. Punish, don't chase.

### 9. GYOU — The Moving Soul
- **Nature:** 行 — going, action, motion itself. A soul that cannot stop moving. Speed as identity.
- **Fighting style:** Hwoarang's Taekwondo (Tekken) — kick-dominant, constantly advancing, stance-switching pressure.
- **Body donor:** Hwoarang TMD — lean, fast, aggressive posture.
- **Default body:** PENDING — no T7-style Hwoarang model exists yet (not in PR #170). Needs T6/TTT2 extraction. T3 TMD remains the documented body until then.
- **Skin:** Eastern Mind wind/motion extractions. Storm grays, lightning whites (Wood force — the growing, reaching element).
- **Archetype:** The speedster. Frame-trap pressure.

---

## ROSTER DESIGN NOTES

**Owner-designed characters (2026-10-12):**

### PANTERA — The Panther Soul
- **Tekken 3 counterpart:** King
- **Name origin:** Pantera, like the band
- **Look:** Black panther head (not leopard), yellow eyes, black panther tail. Pro wrestling gear.
- **Fighting style:** King's pro wrestling grappling — chain throws, multi-part holds, Jaguar Step mixups
- **Body donor:** King TMD
- **In the Western Heart universe** (not Tong-Nou, not Tekken — this is Western Heart's world)

### DEMONIO — The Demon Soul
- **Tekken 3 counterpart:** Jin Kazama
- **Fighting style:** Mishima-style karate — precise, fundamental, the "honest" style
- **Body donor:** Jin Kazama TMD
- **In the Western Heart universe**

### PHANTOM — The Ghost Blade Soul
- **Tekken 3 counterpart:** Yoshimitsu (yes, he's in Tekken 3)
- **Fighting style:** Yoshimitsu's sword techniques — spinning attacks, teleportation, self-harm moves
- **Body donor:** Yoshimitsu TMD
- **In the Western Heart universe**

### DIABLO — The Devil Soul
- **Tekken 3 counterpart:** Heihachi Mishima
- **Fighting style:** Mishima karate — powerful, aggressive, the boss style
- **Body donor:** Heihachi Mishima TMD
- **In the Western Heart universe**

### SKULL — The Punisher Soul
- **Tekken 3 counterpart:** Bryan Fury
- **Look direction:** Punisher-style / Finn Balor demon paint version. Keep Bryan's pants.
- **Note:** Need to see all alternate attires from Tekken 3 before finalizing textures.
- **Fighting style:** Bryan's brutal kickboxing — bone-breaking, no wasted motion
- **Body donor:** Bryan Fury TMD
- **In the Western Heart universe**

### SAM-∪R-Λ1 — The Mech Soul
- **Tekken 3 counterpart:** Gun Jack
- **Name styling:** Gundam-style designation. SAM dash, U replaced with ∪ symbol, R, dash, Λ (symbol that looks like A), 1. Reads as "SAMURAI" but looks like a mech model number.
- **Look direction:** Gundam / Transformer / Power Ranger mech mashup. Mix pieces from different mech designs into one robot. Stylized spelling like a Gundam name.
- **Inspiration:** Biomechanica game designs, mixed mech aesthetics
- **Fighting style:** Gun Jack's power robot moveset — heavy, mechanical, devastating
- **Body donor:** Gun Jack TMD
- **In the Western Heart universe**

### SAKU RA — The Idol Soul
- **Tekken 3 counterpart:** Ling Xiaoyu
- **Name:** Saku Ra (Saku = bloom 咲, Ra = last name)
- **Look direction:** Chinese/Japanese K-pop idol Powerpuff Girl. Use CN gigaleak Powerpuff Girls study materials for the PPG construction.
- **Fighting style:** Xiaoyu's playful kung fu — evasive, acrobatic, tricky stances
- **Body donor:** Ling Xiaoyu TMD
- **In the Western Heart universe**

**Why these nine styles:** Tekken 3's roster covers every major fighting-game archetype (shoto, grappler, rushdown, zoner, trickster, bruiser, counter-fighter, wildcard, speedster). Mapping the nine souls to these nine archetypes gives Western Heart a competitively complete roster on day one — because Tekken 3 already solved the balance.

**The donor principle:** The Tekken model is a *body*. The Eastern Mind skin is the *soul*. A player should never think "that's Paul Phoenix." They should think "that's TOU" — a being of battle wearing a powerful body, skinned in blood-reds and scorched oranges, moving with Paul's devastating honesty but *being* something else entirely.

**Unlockable (post-launch design space):**
- **The Trader** (Phantom Marketplace) — Mokujin's mimicry moveset. Copies the opponent's style.
- **The Assembled Soul** (final boss) — True Ogre's boss moveset. All nine styles in one body.

---

*All bodies: Tekken 3 TMD extractions (pending teardown). All skins: Eastern Mind bitmap extractions (pending extraction). All movesets: Tekken 3 animation/frame data (pending teardown).*
