# WESTERN HEART — ROSTER
## The Nine Souls

Nine fighters. Each is a lost soul of Tong-Nou. Each soul's **body** is its own model — a Tripo original or its own Eastern Mind soul body where one has been built (KAI, TOU) — with the Tekken donor model kept only as a legacy/ladder-back attire. Each soul's **skin** is recombined Eastern Mind bitmap extractions. Each soul's **moveset** is a Tekken fighting style, reinterpreted through the soul's nature. **Asset rule:** Tripo models are the MAIN / DEFAULT attires (owner 2026-10-18); teardown / foreign-skeleton / older in-game models become alternate attires behind the Tripo default. See `asset-manifest.md` for source tracing and `roster/TRIPO-REGISTRY.md` for the per-fighter model map.

**Note on soul details:** Full visual/personality reference for each soul comes from the Eastern Mind extraction (in-game sprites, the Illustrated Book). Style assignments below are the design framework; the extraction refines them. (§8 ZEN and §9 GYOU record the owner's corrections of 2026-11-21, which supersede the 2026-10-24 and 2026-11-10 decisions on Zen's body and on Gyou's Paul condition — neither is settled canon.)

---

### 1. RIN — The Protagonist Soul
- **Nature:** 凛 — dignified, cold, self-possessed. The soul the player begins as. Remembers nothing but the trial.
- **Fighting style:** Mishima-style karate (Tekken: Jin Kazama's moveset) — precise, fundamental, the "honest" style. Rin is the baseline every other soul deviates from.
- **Body donor:** Jin Kazama TMD — young fighter's build, unadorned (legacy attire, last; extraction pending teardown).
- **Default body:** Demonio's canonical body (`demonio-a1`, `roster/demonio/attires/attire1/model.glb`) — RIN fights in his vessel Demonio's body. `rin-body.glb` was the Steve Fox stand-in (wrong canon per owner 2026-10-15; the Steve body belongs to Zui) and is retired.
- **Skin:** Eastern Mind protagonist-sprite extractions. Cold blue-white palette (kimono-dye winter tones).
- **Archetype:** The shoto. Balanced. The soul learning itself.

### 2. BYOU — The Sick Soul
- **Nature:** 病 — sickness. A soul that twitches, stutters, moves wrong. Its illness is its weapon — opponents can't read a body that doesn't obey itself.
- **Fighting style:** Wang Jinrei's Xingyiquan kung fu (Tekken 6) — deceptive, stance-shifting, deliberately unreadable. The drunken-sick master.
- **Moveset base correction (2026-11-06):** owner ruling — Lei Wulong is Rave's alone; Byou's moveset base is Wang Jinrei (Tekken 6), wired from the decoded T6 PSP kit in `game/assets/movesets/byou.json` (see its `wang_rebuild` record). This replaces the pre-correction Lei Wulong style mapping.
- **Body donor:** Lei Wulong TMD — loose-limbed, expressive. **REPLACED by Rave** (WH name locked 2026-10-15; Great Muta/Keiji Mutoh skin, bald/gray goatee). T3 Lei moves to legacy.
- **Skin:** Eastern Mind sick/decay sprite extractions. Jaundiced yellows, infected greens.
- **Archetype:** The trickster. Stance-dance, unpredictability.

### 3. TOU — The Fighting Soul
- **Nature:** 闘 — battle itself. The soul that exists only to fight. No philosophy, no fear. The purest expression of the trial.
- **Fighting style:** Paul Phoenix's power karate/judo hybrid (Tekken) — devastating single strikes, the Death Fist. Maximum damage, minimum subtlety.
- **Body:** TOU's own Eastern Mind body (`tou-soul-tex.glb`, 2026-11-10). Paul Phoenix is his fighting base / held kit, not his body. **Legacy:** the assembled Paul body (`tou-body.glb`, docs/TOU-BODY-BUILD-2026-11-09.md).
- **Skin:** Eastern Mind warrior-sprite extractions. Blood reds, scorched oranges (Fire force).
- **Archetype:** The grappler/brawler. High damage, honest.

### 4. SHA — The Sand Soul (a SOUL, not a fighter)
- **Nature:** 沙 — sand, desert. From the Sha-mo Desert of the Land of Life. A soul that flows, erodes, surrounds. Never where you struck.
- **SHA is the soul shared by three sisters — Saku Ra (the bloom), Kinpo (the thorn), Awa Pop (the bubble). One soul, three moods, three sisters. SHA is not a fighter and has no select card of its own: the `sha` roster card was retired 2026-11-20 (owner order: Saku Ra is ONE fighter), and the single fighter is SAKU RA below. (CANON.md §4, "On SHA's three-way split.")**
- **Fighting style (of the soul's vessels):** Ling Xiaoyu's Baguazhang (Tekken) — flowing, circular, evasive. The art of not being hit.
- **Body:** Saku Ra's own Tripo main (`saku-ra`, `roster/sakura/attires/attire1/model-rerig.glb`; `saku-ra-main.glb`). **Legacy:** the T7-style Xiaoyu GLB (`sha-body.glb`) and the Ling Xiaoyu TMD (last attire only).
- **Skin:** Eastern Mind desert-sprite extractions. Sand ochres, bleached bone whites.
- **Archetype:** The evasive. Movement as defense.

### 5. KAI — The Sea Soul
- **Nature:** 海 — the sea. Fluid, rhythmic, unstoppable. Fights like water — finds every opening.
- **Fighting style:** Eddy Gordo's Capoeira (Tekken) — rhythmic, ground-flowing, relentless pressure. The tide that doesn't stop.
- **Body:** KAI's own Eastern Mind body (`kai-soul-tex.glb`, 2026-11-10). His vessel King Tyrant fights in his own Tripo. **Legacy:** the T7-style Eddy shell (`kai-body.glb`) and the Eddy Gordo TMD (last attire only).
- **Skin:** Eastern Mind water-sprite extractions. Deep blues, foam whites, abyssal blacks (Water force).
- **Archetype:** The rushdown. Relentless rhythm offense.

### 6. JIN — The Blade Soul
- **Nature:** 刃 — the blade. A soul that cuts. Precise, ritual, terrifying. (Not to be confused with RIN, the protagonist.) The soul JIN (刃) is NOT Jin Kazama and NOT a soul form of Jin Kazama — the soul JIN, the Blade Soul, whose vessel is Phantom. (CANON.md Law 2, owner 2026-11-08.)
- **Fighting style:** Yoshimitsu's advanced ninjutsu (Tekken) — sword techniques, teleportation stances, self-damaging power moves. The blade that cuts both ways.
- **Body:** Phantom's own Tripo — JIN's vessel body. **Body donor (legacy):** Yoshimitsu TMD — armored, masked, inhuman (last attire only).
- **Skin:** Eastern Mind blade/spirit extractions. Polished steel grays, shrine-vermillion accents.
- **Archetype:** The wildcard. High-risk tools, stance complexity.

### 7. RETSU — The Violent Soul
- **Nature:** 烈 — violence, intensity. A soul of pure destructive force. The Helix Palace's Destruction room made flesh.
- **Fighting style:** Bryan Fury's kickboxing (Tekken) — brutal, bone-breaking, no wasted motion. Every hit is meant to end the fight.
- **Body donor:** Bryan Fury TMD — scarred, heavy, military.
- **Skin:** Eastern Mind destruction-sprite extractions. Charcoal blacks, molten cracks (Metal force).
- **Archetype:** The bruiser. Counter-hit monster.

### 8. ZEN — The Still Soul
- **Nature:** 禅 — meditation, stillness. A soul that barely moves — and doesn't need to. The calm center of the storm.
- **Zen is NEITHER Julia NOR Heihachi.** (Owner decision 2026-10-24, `docs/decisions/2026-10-24-zen-base-decision.md`, resolving PR #1016.) Zen is the Still Soul, unvesseled — the soul that refused the trial: "Stillness does not compete." (CANON.md §4, "On ZEN and GYOU.")
- **Fighting base:** Eleven / Twelve (Street Fighter, 2D concept: shapeshifting mimicry) → Dural (Virtua Fighter 5, 3D implementation: chrome humanoid, the closest 3D thing to Eleven/Twelve — Dural is NOT a separate pick, it is the 3D stand-in for Eleven/Twelve) → Zen's OWN canon moves on top. X.COPY (Twelve's copy super) as ONE super, NOT the identity. Plus Tentacle Mode, Oversoul, transformation, spirit-form stand (canon).
- **Default body:** Zen's own Tripo spirit body — the yellow lemon-octopus spirit demon (Tripo 8c46e379, `roster/zen/attires/attire1/model.glb`, key `zen` / `zen-attire1`), wired as Attire 1 default. He has a spirit form of his own (Tripo 803f4cf1, `roster/zen/spirit/model.glb`, key `zen-spirit`) and two transformation modes inside Attire 1 — Tentacle Mode (Tripo 9460095d) and Oversoul (Tripo 2bbc8e88). The T7 Julia model (`game/assets/models/zen-body.glb`) is NOT his body — it is Attire 2, LEGACY BODY only. (Owner correction 2026-11-21; `roster/zen/CANON.md`, owner canon 2026-10-21.)
- **Skin:** Eastern Mind meditation-sprite extractions. Temple-stone grays, incense-smoke whites (Earth force).
- **Archetype:** The counter-fighter. Punish, don't chase.
- **Open:** Zen is hidden from the select grid (`SELECT_HIDDEN` in `game/js/select-screen.js`) while the comment above that set says Zen stays selectable — contradiction reported, not fixed silently (owner call). Zen is he/him (owner 2026-11-21).

### 9. GYOU — The Moving Soul
- **Nature:** 行 — going, action, motion itself. A soul that cannot stop moving. Speed as identity.
- **Gyou is NOT Hwoarang.** (Owner 2026-11-10; `game/js/fighter.js:211`.) Gyou is the Moving Soul, unvesseled as a whole — a splinter is trapped in CYBORG X ("a machine is a nowhere"). (CANON.md §4, "On the GYOU splinter.") Hwoarang's holder is Tobi.
- **Fighting base:** Paul Phoenix's power karate/judo, mixed with fire attacks — Gyou's spirit-body variant, HELD ONLY IF GYOU NEEDS SOMEBODY. Owner-sanctioned 2026-10-23 ("he can have Paul Phoenix moves mixed with like flame attacks") and 2026-11-10 ("Gyou was probably Paul Phoenix and fire attacks") — re-conditioned by the owner 2026-11-21: Paul goes to Gyou only if Gyou needs somebody; if Gyou has somebody else, he is not Paul. He is definitely NOT Hwoarang — Hwoarang's holder is Tobi (she/her). Whether Gyou needs somebody is an open owner call, not settled in this doc.
- **Body:** Gyou's own spirit body (`gyou-attire1`), rigged and wired 2026-11-09. Legacy: Hwoarang TMD (last attire only; framework-era donor, superseded).
- **Skin:** Eastern Mind wind/motion extractions. Storm grays, lightning whites (Wood force — the growing, reaching element).
- **Archetype:** The speedster. Frame-trap pressure.
- **Open:** the owner said "probably Paul" / "whatever" — the Paul holding is NOT locked as permanent in this doc. Owner call still open: does Gyou need somebody, or does he have somebody else?

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
- **One fighter:** Saku Ra is ONE fighter (owner order 2026-11-20 ~19:30). She is the bloom — one of three sisters sharing the SHA soul (with Kinpo and Awa Pop). The `sha` roster card is retired; SAKU RA is the single fighter and `sakura.json` is her file (it holds the only copy of the xiamot wiring and her three signatures: Bloom Opening, Called By Name, You Can't Hit A Song).
- **In the Western Heart universe**

## ROSTER ADDITIONS — SIX STAGED FIGHTERS (owner addendum 2026-11-20 ~19:34 EST)

This section supersedes the P3 hygiene proposal's net "add NONE of the six" (P3 PR-BODY, workdir only — no repo file carried that listing). Owner addendum 2026-11-20: Kutz + Realizzt COUNT and join the playable roster; DXMMII is already in the game; Lili + Baek fold in as OTHER custom characters, not named fighters.

### KUTZ + REALIZZT - JOINING the playable roster (not yet added)
- Owner addendum 2026-11-20: both join the playable roster. Roster entries are NOT added in this change — blocked, in order:
  1. **Correct moveset (P2 rebuild owed):** `kutz.json` (160 moves) plays King (98%); `realizzt.json` (156 moves) plays Jin. Both need their real Virtua Fighter source (Goh Hinogami / Brad Burns).
  2. **Model:** no `kutz.glb` / `realizzt.glb` on main.
- Index entries already exist for both, so once the kit + model land, only the `roster-full.js` entry (+ tier, + attire ladder) is left to add.

### DXMMII - ALREADY on the menu (do not treat as waiting to join)
- DXMMII the fighter IS already rostered and selectable as `dxmmii-patchwork` (`game/js/roster-full.js:206`, Patchwork DJ, model `dxmmii-tripo`, 3-slot attire ladder, not hidden, file loads).
- The BARE `dxmmii` id is staged and never loads (index + MOVESET_IDS only; `dxmmii.json`, 150 moves, fixed Jin bank). The P3 listing ("STAY STAGED under the bare `dxmmii` id") was correct about the bare id — the confusion was the id split: playable fighter `dxmmii-patchwork` vs staged file `dxmmii`.
- OPEN (needs a live check, not touched here): the `mimic` section in `dxmmii-patchwork.json` (2026-10-23) says "the roster does not play it [this file]" while the loader (`fighter.js:899`, `_movesetId = charData.id`) says it does. The mimicry system itself is owed.

### LILI + BAEK - custom-character material, NOT roster entries
- Neither has a roster entry today, so nothing is removed. Their move lists fold in as OTHER custom characters (their successors Silvertongue and KEVIN are separate rostered fighters and are untouched by this).
- Fold-in requirements (all still owed — no ingestion or assembler work in this change):
  1. Ingest via `tools/moveset-library/ingest.mjs` as library banks / editor templates.
  2. Source-law exception needed for Lili's 133-move T3 Xiaoyu proxy layer ("Ling Xiaoyu" is claimed by Saku-ra in `game/data/moveset-library/claimed-map.json`); Baek/Bryan are unlisted in the claimed map (neither claimed nor free).
  3. No custom-material marker exists in code today — one must be created (precedent: `silvertongue.json` `replaces`/`canon_note` headers).
  4. Assembler gap: custom manifests into fights needs `movesets.js` integration + a live fight proof (`game/js/custom-fighter.js`); until then a custom fighter fights on the `'jin'` fallback.
  5. Baek's kit is wrong first: `baek.json` plays Bryan (107/111) — P2 rebuild owed before the fold-in means anything.

**Why these nine styles:** Tekken 3's roster covers every major fighting-game archetype (shoto, grappler, rushdown, zoner, trickster, bruiser, counter-fighter, wildcard, speedster). Mapping the nine souls to these nine archetypes gives Western Heart a competitively complete roster on day one — because Tekken 3 already solved the balance.

**The donor principle:** The Tekken model is a *body*. The Eastern Mind skin is the *soul*. A player should never think "that's Paul Phoenix." They should think "that's TOU" — a being of battle wearing a powerful body, skinned in blood-reds and scorched oranges, moving with Paul's devastating honesty but *being* something else entirely.

**Unlockable (post-launch design space):**
- **The Trader** (Phantom Marketplace) — Mokujin's mimicry moveset. Copies the opponent's style.
- **The Assembled Soul** (final boss) — True Ogre's boss moveset. All nine styles in one body.

---

*All bodies: Tekken 3 TMD extractions (pending teardown). All skins: Eastern Mind bitmap extractions (pending extraction). All movesets: Tekken 3 animation/frame data (pending teardown).*
