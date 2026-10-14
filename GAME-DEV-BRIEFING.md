# WESTERN HEART — Complete Game-Dev Briefing
*Everything a game developer needs to know. Compiled 2026-10-14.*

---

## 1. THE NAME

**"The Western Heart Game"** — owner-corrected 2026-10-12 from "Western Heart" alone.

In-universe: the fighters don't call the world Tong-Nou. They call it the **Western Heart** — the heart that beats in the western dark of the giant head. It's the world of the trial: the lands where souls fight, the roads between them, the shrine where it ends.

The tagline (locked in MISSION.md): *"Western Heart — a lost multiverse bastard child. Familiar enough to pick up, to love. Strange enough to never put down. And to be a mystery."*

---

## 2. THE CONCEPT (one paragraph)

A 3D fighting game set inside the head of Tong-Nou — a giant green floating head from Osamu Sato's *Eastern Mind: The Lost Souls of Tong-Nou*. Nine lost soul-fragments fight a trial by combat across five elemental lands. Death is not game over — it's **reincarnation**: you die, you come back in a new face, and the new face changes your fighter. The final boss is your own assembled soul. The engine is Tekken's. The world is Sato's. Everything is built by tearing down real games and recombining their actual files — never hand-made, never AI filler.

The one-line pitch: **Tekken 3's fighting engine, running inside Osamu Sato's head.**

---

## 3. THE CHIMERA BUILD METHOD

This is the core production philosophy and it's non-negotiable:

1. **Tear down fully.** Get the complete game — every file, whatever decryption/decompiling/reverse-engineering it takes. No deferral.
2. **Study.** Learn how the real systems work — move tables, animation formats, customization systems, audio engines.
3. **Recombine real extracted files.** Build the game from the teardown's actual files — real models, real movesets, real frame data, real textures. No hand-tooled approximations. No mockups. No placeholder code in the playable build.
4. **Transform.** 100% of every teardown gets incorporated, but transformed — edited, reskinned, renamed — so nothing stays proprietary to the source. The owner's design decisions and the glue code are the only new things.

**The foundation (never changes):**
- **Input language:** Tekken. 1/2/3/4 limb buttons, f/b/u/d notation, strings, stances, while-rising, crouch dash.
- **Play style:** Tekken + Urban Reign. Open-plane 3D, juggles, walls (Tekken). Street brawling, weapons, destructibles, multi-fighter (Urban Reign).
- **Feel:** Capcom. Hit-stop, responsiveness, special-move motion inputs layered where they fit.

**The rule:** *"Tekken's inputs are the language. Every federated mechanic must speak that language."* A DOA counter-hold gets a Tekken notation. A Soulcalibur guard impact gets a Tekken input. Nothing replaces the foundation — everything plugs into it.

**Build order:** Tekken input core → Urban Reign brawl layer → federated mechanics one at a time → moveset library → Create Fighter → stages → roster.

**What it feels like (owner's words):** *"like a Tekken mod at first until we get the rest of the teardown into it"* — a lost multiverse bastard child. The Tekken you know, warped through Tong-Nou's dreaming head.

**This is the template for ALL his games.** Once the chimera method is perfected on Western Heart, it applies to Bannon, AshLane, Concrete Dragon, Brutal Fist — same engine/pipeline, different games.

---

## 4. THE ROSTER — 36 NAMED FIGHTERS

### The Nine Souls (core roster — the trial's vessels)
Each is a lost soul of Tong-Nou. Body = Tekken 3 model extraction. Skin = Eastern Mind bitmap extraction. Moveset = Tekken 3 fighting style reinterpreted through the soul's nature.

| Soul | Nature | Tekken base | Archetype |
|------|--------|-------------|-----------|
| RIN | 凛 dignified, cold | Jin (Mishima karate) | The shoto — balanced baseline |
| BYOU | 病 sickness | Lei (Five Animals kung fu) | The trickster — unreadable |
| TOU | 闘 battle itself | Paul (power karate) | The brawler — max damage |
| SHA | 沙 sand, desert | Xiaoyu (Baguazhang) | The evasive — movement as defense |
| KAI | 海 the sea | Eddy (Capoeira) | The rushdown — relentless rhythm |
| JIN | 刃 the blade | Yoshimitsu (ninjutsu) | The wildcard — high-risk tools |
| RETSU | 烈 violence | Bryan (kickboxing) | The bruiser — counter-hit monster |
| ZEN | 禅 stillness | Julia (Xingyiquan) | The counter-fighter — punish, don't chase |
| GYOU | 行 motion itself | Hwoarang (Taekwondo) | The speedster — frame-trap pressure |

### The Main Seven (owner-designed vessels)
- **PANTERA** ← King. Black panther head, yellow eyes, tail. Pro-wrestling grappler. Vessel of TOU. (Character 1 — furthest along: base model in-game, Attire 2 "Leomon" built.)
- **DEMONIO** ← Jin. The "demon" who fights like a saint — Mishima karate, cold discipline. Vessel of RIN.
- **PHANTOM** ← Yoshimitsu. Ghost-blade. Sword techniques, teleportation, self-damaging moves. Vessel of JIN.
- **DIABLO** ← Heihachi. The intruder — NOT one of the nine. Tore into the trial uninvited. Boss-style Mishima karate.
- **SKULL** ← Bryan. Punisher-style punisher. Brutal kickboxing. (Keep Bryan's pants.)
- **SAM-∪R-Λ1** ← Gun Jack. Mech soul. Name reads "SAMURAI" as a Gundam-style designation. Heavy robot moveset.
- **SAKU RA** ← Xiaoyu. Idol soul — K-pop idol Powerpuff Girl (Blossom). Playful evasive kung fu.

### The Twenty Bonus Fighters (Tekken 7 bases, owner-directed reskins)
ZUI (Steve, drunken master) · KINPO (Asuka, Buttercup) · WATERFALL (Josie, soul-bearer who cries) · KING TYRANT (Eddy, King Booker showman) · BURGER (Bob, hunger-cursed glutton) · AWA POP (Nina, Bubbles) · SCIMITAR (Shaheen, Scar×Jafar schemer) · PURPLE RAIN (Lee, MJ×Prince showman) · NIGHTWOLF (Julia, spirit warrior) · DIO (Akuma, the demon) · CYBORG X (Alisa, the android) · MICHIKO (Katarina, outlaw) · STAR (Christie, dancer) · TORCH (Anna, assassin) · BRUNO (Miguel, heartbreak brawler) · N3GΔTIV0 (Negan, galactic zombie bounty hunter) · THOR (Ganryu — IS the Norse god; sumo slaps are thunder claps) · YUKIHYŌ (Armor King, snow-leopard masked ninja) · SLICE (Dragunov, maniacal agent) · DOC FRANK (Dr. Bosconovitch — the machines' father).

**Boss:** SUN RĀ ← Pac-Man. The soul-eating sun. "Immortal Qombat" (always in Japanese 不死クォンバット except when Sun Rā says it in English).

**Design principle:** The soul determines the style; the Tekken moveset is the vocabulary. A player should never think "that's Paul Phoenix" — they should think "that's TOU."

---

## 5. NARRATIVE & WORLD

**The world:** Tong-Nou — a giant green head floating in darkness. Inside: five lands, a marketplace, a mountain, a shrine. Tong-Nou is called the Purifier. It does not explain itself.

**The five lands** (each a fighting stage, each holding an elemental force):
- **Tree of Life** — Wood. Colossal tree holding souls like fruit. Where souls begin.
- **Plains of Chi-U** — Fire. Scorched plains under a burning sky. Confrontation.
- **Octagonal Shrine Par-fang** (Central Mountain) — Earth. Eight-sided, ancient, still.
- **Helix Palace** — Metal. Spiraling palace, five glowing rooms (Greed, Appetite, Immortality, Sexual Desire, Destruction).
- **Palace of Dreaming** — Water. A palace that won't stay still.

Between them: the **Phantom Marketplace** (liminal bazaar, the Trader buys/sells elemental forces).

**The trial:** *Fight. Die. Return. Claim the forces. Forge the katana. Become whole.*

**Death = reincarnation.** Lose a round, die, come back in a new face (three eyes / three noses / three mouths to choose from, as in Eastern Mind). The new face changes your fighter — sharper eyes, faster hands. Death adapts you.

**The twist:** The final boss is the **Assembled Soul** — a composite of all nine souls, including yours. You fight yourself. Winning absorbs it. Tong-Nou wasn't devouring souls. It was purifying them. The trial was healing all along. The characters don't know Tong-Nou is God.

**Soul-vessel mapping:** Pantera→TOU, Demonio→RIN, Phantom→JIN, Diablo→NOT one of the nine (intruder), Skull→RETSU, SAM-UR-A1→built (no soul), Saku Ra→SHA. Bonus: Zui→BYOU, Kinpo→splinter of SHA, Waterfall→all nine's grief, King Tyrant→KAI.

**Modes (owner-locked):**
- **Versus:** fighter-vs-fighter + Tekken Tag-style tag. Pick a character/team and STAY them until you lose → rematch or main menu. Reincarnation does NOT apply in versus.
- **Story/career/campaign:** death is NOT game over — it's forced reincarnation as another character. Your actions influence who you become next. *"That is the entire game."*

---

## 6. SYSTEMS

- **Nine-Soul Meter + Soul Surge:** second resource beyond health; spend meter for the Surge power-up.
- **Reincarnation Rounds:** the death mechanic above — core to story mode.
- **Force Claiming:** winning in a land claims its elemental force → passive for the rest of the set.
- **Tekken core:** 1/2/3/4 limb inputs, strings, stances, while-rising, crouch dash, juggles, walls, best-of-3 rounds.
- **Federated mechanics** (each mapped to Tekken inputs): VF throw escapes/weight classes/ring-outs, DOA triangle (strike>throw>hold) + counter holds, SC 8-way run + guard impact + soul charge, No Mercy/WMXIX moveset slots + AKI grappling, Urban Reign brawl/weapons/destructibles/multi-fighter.
- **Create Fighter:** Tekken 7's 17-slot customization + WWE 2K CAW suite + Def Jam FFNY customization. Full-screen fighter preview, menus float on top, never cover the fighter. (Menu names: CREATE FIGHTER, MOVESET.)
- **Moveset library:** 176 slots, ~5,932 animation clips indexed. Moveset preview shows YOUR fighter performing the move on a SECOND fighter in a ring.

---

## 7. TEARDOWNS — WHAT'S IN THE GAME AND GOING IN

**The rule:** 100% of every teardown is incorporated into Western Heart, transformed so nothing stays proprietary to the source.

| Game | Status | What it contributes |
|------|--------|---------------------|
| **Tekken 3** | 100% ✅ | Input foundation, 3,247 moves, 7 fighters, 15 stages, 8,556 textures, UI art. Legacy/retro mode. |
| **WWF No Mercy** | 100% ✅ | 5,787 anims, 3,570 models, 5,029 textures, 17 arenas. AKI grappling, CAW parts, moveset slots. |
| **Virtua Fighter 5** | 100% ✅ | 19 fighters, 38 stages. Defensive mechanics, throw escapes, weight classes, ring-outs. |
| **Urban Reign** | ~95% | 509 files, 1,033 audio files, 72 fighters extracted (242K verts). Brawl mode, weapons, destructibles, 60+ archetypes. |
| **WMXIX** | ~80% | 170 anims, 2,690 CAW parts, arenas. Moveset tree, CAW system, arena traversal. Format RE in progress. |
| **Soulcalibur II** | ~60% | 8-way run, guard impact, soul charge, weapon ranges, ring-outs. |
| **Tekken 7** | ~40% | King + variants (Pantera's base model). Full game not acquired. |
| **Tekken 6** | ~30% | EBOOT decrypted. DATA401 cipher RE in progress. |
| **Eastern Mind** | ~20% | The universe bible — world, narrative, visual soul, five lands. Extraction pending. |
| **TTT2** | ~15% | 26/26 chunks safe. Full extraction gated on disk. |
| **DOA4** | ~15% | 30/30 chunks safe. Full extraction gated on disk. |
| **SCVI / DOA6** | ~10% | Mechanics docs done. Binaries not acquired. |
| **Def Jam FFNY** | Teardown complete | AKI-engine lineage confirmed. 7,948 CAW parts, 329 finishers. Customization system goes into WH's Create Fighter. |
| **Street Fighter** | Research | SF chars keep SF moves/animations but PLAY Tekken. Mined for mechanics, never replaces the foundation. |

**Wrestling-game separation (owner-locked):** Wrestler CHARACTER MODELS live in a separate game (`mhvnsnt/wrestling-game` — 2,826 models). Western Heart keeps all wrestling MECHANICS. Only models moved out (art-style mismatch). Exception: the WWE 2K CAW suite goes INTO Western Heart's character creation.

---

## 8. TECH STACK

- **Engine:** Godot 4, web export first (phone browser). DriftEngine (WebGPU) evaluated for 3D viewer.
- **Current playable build:** web (Three.js), live at mhvnsnt.github.io/western-heart — Pantera vs Demonio, 36-fighter select, Tekken-style menus, real T3 movesets wired, real T3 title art. Real models/audio/stages being wired in progressively.
- **Rendering target:** PS1-authentic — vertex snapping, affine texture mapping, Sato's kimono-dye palette.
- **Pipelines:** TMD→glTF, TIM→PNG, model library (60+ models), Blender 4.0.2 headless (Cycles only).
- **Repo:** github.com/mhvnsnt/western-heart (public). All work via branch → PR → merge. Zero open PRs.

---

## 9. PRODUCTION STATUS & PIPELINE

- **Character pipeline:** T-pose base → reskin (owner directs via Gemini on renders, all 4 angles) → rig → in-game. Pantera is Character 1 (Attire 1 complete, Attire 2 "Leomon" built).
- **Production order:** Char 1 → Attire 2 → Char 2 → combat test → signature moves → stage → Char 2 attires → UI shell → best-of-3 → sound → roster expansion.
- **Model standard:** every model cut Tekken-style into pieces, rigged to Tekken topology/skeleton, clean — no glitchy imports.
- **Laws that govern everything:** NO-MOCKUPS (everything real/wired), NO-HAND-TOOLING (use proven tools), NO-DEFERRAL (full teardowns), DISK-STORING-MOVING (upload→verify→delete, never "clearing"), NO-UNASKED-WORK (nothing the owner didn't ask for), transformation law, likeness lock, art style lock.

---

## 10. WHAT "TOTAL CONVERSION / CHIMERA" MEANS HERE

Western Heart is not a mod and not a clone. It's a **chimera**: Tekken's skeleton, Eastern Mind's soul, with organs transplanted from a dozen other games — every transplant mapped to speak Tekken's input language, every donor part transformed until it's unrecognizable as the source. The test: a Tekken player picks it up instantly. A Sato fan recognizes the world. Nobody says "that's literally [source game]." Familiar enough to pick up, to love. Strange enough to never put down. And to be a mystery.

---

*Source docs: CHIMERA-ARCHITECTURE.md, CHIMERA-BUILD.md, DESIGN.md, ROSTER.md, CANON.md, MISSION.md, roster/bonus/BONUS-CHARACTERS.md, teardown/TEARDOWN-STATUS.md — all in mhvnsnt/western-heart.*
