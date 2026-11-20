# WESTERN HEART
## A fighting game inside the head of Tong-Nou

**Engine:** Tekken 3 (reverse-engineered) | **Universe:** Eastern Mind: The Lost Souls of Tong-Nou (extracted)
**Rule:** Every asset is a recombined reverse-engineered file. Nothing hand-tooled. Nothing AI-generated.

---

## 1. CORE CONCEPT

Tong-Nou is a giant green head floating in darkness. Inside it: five lands, nine souls, and now — a trial by combat.

**The fiction:** Tong-Nou the purifier is weakening. Its five elemental forces (Fire, Metal, Water, Wood, Earth) are scattering. The nine lost souls — fragments of one being — must fight across the five lands. Each victory claims a land's force. The soul that claims all five forces forges the **Katana of Five Forces** — not by collecting it, as in Eastern Mind, but by *proving* it in combat.

This is played completely straight. No winking. A fighting tournament inside a giant head, where losing means dying and dying means coming back stronger, is treated with total seriousness. That is Sato's sincere absurdism. That is the game.

**The one-line pitch:** Tekken 3's fighting engine, running inside Osamu Sato's head.

---

## 2. WHAT MAKES IT NOT TEKKEN AND NOT EASTERN MIND

- **Not Tekken:** No Mishimas. No King of Iron Fist Tournament. The roster is nine surreal soul-creatures. The stages are Buddhist-cosmology lands. Death is a mechanic, not a fail state.
- **Not Eastern Mind:** No point-and-click. No adventure-game exploration. The head-world is the *arena*, not the maze. Combat is the verb, not clicking.
- **Western Heart:** A 3D fighter where the fighting *is* the spiritual trial. Every punch is philosophy. Every KO is reincarnation.

---

## 3. THE ROSTER — THE NINE SOULS

Nine fighters. Each is one of Tong-Nou's lost souls. Each soul's body is a Tekken 3 fighter model, retextured and recombined with Eastern Mind's visual language. Each soul's moveset is a Tekken 3 fighting style, reinterpreted through the soul's nature.

See `roster.md` for the full nine.

**Design principle:** The soul determines the *style*. The Tekken moveset is the *vocabulary*. A capoeira moveset on a gelatinous dream-creature reads differently than on Eddy Gordo — same frames, alien body.

---

## 4. THE STAGES — THE FIVE LANDS (+2)

Seven fighting arenas, each a land of Tong-Nou rendered as a 3D fighting stage. Stage geometry from Tekken 3's stage format; all visual surfaces from Eastern Mind's extracted bitmaps.

See `stages.md` for all seven.

---

## 5. SYSTEMS FUSION

The heart of the design. Tekken's mechanics + Eastern Mind's philosophy = systems neither game has alone.

See `systems.md` for the full design, including:

- **Reincarnation Rounds:** Losing a round triggers the Reincarnation Screen (three eyes / three noses / three mouths, as in Eastern Mind). Your new face modifies your fighter. Death adapts you.
- **The Nine-Soul Meter:** A second resource beyond health, tied to which soul-fragment is dominant.
- **Force Claiming:** Winning in a land claims its elemental force, granting a passive for the rest of the match set.
- **The Purifier Twist:** The final boss isn't evil. Tong-Nou was healing you. The "final boss" fight is against your own assembled soul.

---

## 6. ART DIRECTION

**Target:** PS1 low-poly (1998) meets Sato surrealism (1994). Tekken 3's ~500–1000 poly character models wearing Eastern Mind's kimono-dye color theory, Constructivist geometry, and bedazzled-Jello translucency.

**Rules:**
- All character geometry: Tekken 3 TMD extractions. No new models.
- All textures: Eastern Mind bitmap extractions and Tekken 3 TIM extractions, recombined. No new textures.
- Rendering: authentic PS1 look — vertex snapping, affine texture mapping, no perspective correction, 320×240 internal resolution upscaled.
- Color: Sato's palette. Kimono-dye considered color, not neon-for-neon.

See `asset-manifest.md` for the full asset tracing.

---

## 7. NARRATIVE

See `systems.md` § Story Mode and below.

**Premise:** The nine souls were scattered when Tong-Nou began to weaken. Each soul remembers only its nature — not its name, not the others. Drawn to the Octagonal Shrine Par-fang at the Central Mountain, they find the trial inscribed: *fight, die, return, claim the forces, forge the katana, become whole.*

**Structure:** Arcade ladder through the five lands (one stage per land, in elemental order: Wood → Fire → Earth → Metal → Water, the generating cycle), then the Phantom Marketplace (mid-boss: the Trader), then the Central Mountain shrine (final: your own soul, assembled).

**The twist (earned, not told):** The final opponent is a composite of all nine souls — including yours. You are fighting yourself. Winning doesn't destroy it. Winning *absorbs* it. Tong-Nou wasn't devouring souls. It was purifying them. The trial was healing all along.

---

## 8. TECHNICAL PLAN

See `technical-plan.md`.

**Engine:** Godot 4 (free, open-source — fits the owner's free-tool directive).
**Fighting core:** Reimplemented from the Tekken 3 Ghidra teardown — frame data, hitboxes, juggle physics, sidestep, 3D movement.
**Asset pipeline:** TMD→glTF, TIM→PNG, Director-BMP→PNG, SEQ→playable audio. All conversions are mechanical, not creative.
**What we write:** Only the glue — the engine code, the asset pipeline scripts, the game logic. Everything the player sees and hears is a recombined extraction.

---

## 9. DOCUMENT INDEX

| Doc | Contents |
|-----|----------|
| `WESTERN-HEART-DESIGN.md` | This file — master vision |
| `roster.md` | The nine souls: fighters, styles, asset sources |
| `stages.md` | The seven lands: arenas, asset sources |
| `systems.md` | Mechanics, Reincarnation Rounds, Force Claiming, story mode |
| `asset-manifest.md` | Every asset traced to its reverse-engineered source file |
| `technical-plan.md` | Engine choice, pipeline, build phases |

---

*Design doc 2026-10-12. The owner's game. Built from understanding, not imitation.*
*Study purpose only for source materials. Western Heart itself is original work assembled from extracted components.*
