# WESTERN HEART — TECHNICAL PLAN
## How We Actually Build This

---

## 1. ENGINE: GODOT 4

**Choice:** Godot 4.x (free, open-source, MIT license).

**Why:**
- $0. Fits the owner's free-tool directive. No licensing, no royalties, no seats.
- Real 3D with full shader control — we need custom PS1-style rendering.
- GDScript is fast to write; C# available for performance-critical fighting logic.
- Exports to PC (primary target). Console later if warranted.
- The owner's team already works across Godot-friendly pipelines.

**Why not Unity:** Licensing cost, corporate overhead. Why not Unreal: overkill for PS1 aesthetics, revenue share. Why not custom engine: we'd spend a year on renderer instead of game.

---

## 2. PS1 RENDERING (the look)

Tekken 3 ran at 320×240 on real hardware. Western Heart targets the same aesthetic — not as nostalgia, but because the low-poly + affine-mapping look *is* the art direction.

**Implementation (Godot shaders):**
- **Internal resolution:** Render 3D at 320×240 (or 480×270 for widescreen), upscale with nearest-neighbor. Authentic pixel density.
- **Vertex snapping:** Snap vertices to a coarse grid in the vertex shader — reproduces PS1's characteristic wobble.
- **Affine texture mapping:** Disable perspective-correct interpolation. Textures warp on angled surfaces, exactly like 1998.
- **No texture filtering:** Nearest-neighbor only. Every texel is visible.
- **Gouraud shading:** Per-vertex lighting, no per-pixel. Flat, bold light response.
- **Dithering:** Optional 2×2 ordered dither on gradients (PS1's signature banding solution).

**This is all shader code (glue).** The models and textures are extractions; the *rendering* is our implementation of 1998 hardware behavior.

---

## 3. ASSET PIPELINE

### Phase 1: Extraction (mechanical, not creative)

| Step | Input | Output | Tool |
|------|-------|--------|------|
| 1a | Tekken 3 ISO | File listing | 7zip / ISO parser |
| 1b | TMD files | `.obj` or `.glTF` | TMD parser script (write once) |
| 1c | TIM files | `.png` | TIM parser script (write once) |
| 1d | Animation data | Frame/pose data `.json` | From Ghidra analysis (manual mapping) |
| 1e | VAB/VAG banks | `.wav` | PS1 audio extractor |
| 1f | SEQ music | `.mid` + soundfont → `.ogg` | SEQ parser |
| 2a | `eastern mind.img` | Mounted filesystem | CD image mounter |
| 2b | Director cast members | `.bmp` / `.wav` | Director cast extractor |
| 2c | Embedded bitmaps | `.png` | Batch converter |
| 2d | Embedded audio | `.wav` → `.ogg` | Batch converter |

**All pipeline scripts are glue.** They convert formats. They don't create content.

### Phase 2: Recombination (the creative act)

| Step | Process | Example |
|------|---------|---------|
| Skin mapping | Map Eastern Mind bitmap onto Tekken TMD UV layout | RIN: protagonist sprite colors → Jin's UV map |
| Palette application | Apply kimono-dye palette extracted from Eastern Mind to Tekken base textures | All fighters |
| Face variants | 9 face-part bitmaps (3 eyes × 3 noses × 3 mouths) → 27 texture variants for Reincarnation | Reincarnation Screen |
| Stage assembly | Tekken arena geometry + Eastern Mind background bitmaps as skybox + wall textures | All 7 stages |
| Audio layering | Tekken hit SFX + Eastern Mind ambient beds | Combat audio |
| UI recombination | Tekken menu layout logic + Eastern Mind typography bitmaps | Menus |

**Recombination is rearrangement, not creation.** We are placing extracted pixels onto extracted polygons. The USE THE IMAGE LAW holds: the source files are the material.

### Phase 3: Retargeting (animations)

Tekken 3's animations are bone transforms. Our fighters use Tekken 3's skeletons (same TMD models). Retargeting is 1:1 — no adaptation needed, because the body *is* the Tekken body.

**Soul Surge borrowed moves:** When RIN channels KAI's capoeira kick, we play Eddy's animation data on Jin's skeleton. Skeletons are proportionally similar (all humanoid). Minor foot-sliding is acceptable — it's PS1.

---

## 4. FIGHTING ENGINE ARCHITECTURE

```
western-heart/
├── engine/
│   ├── fighter/          # Fighter state machine, physics
│   │   ├── state.gd      # Idle/walk/attack/hit/launcher/airborne/etc.
│   │   ├── hitbox.gd     # Hitbox/hurtbox system (from teardown spec)
│   │   ├── frame_data.gd # Move database (from teardown spec)
│   │   └── input.gd      # Input buffer, motion detection
│   ├── combat/
│   │   ├── juggle.gd     # Air combo physics (from teardown spec)
│   │   ├── throw.gd      # Throw break system
│   │   ├── wall.gd       # Wall-splat logic
│   │   └── counter.gd    # Counter-hit detection
│   ├── reincarnation/    # OUR system (original game logic)
│   │   ├── face_builder.gd   # Eye/nose/mouth selection
│   │   ├── modifier.gd       # Stat/moveset modifications
│   │   └── soul_meter.gd     # Nine-Soul Meter + Soul Surge
│   ├── forces/           # OUR system (original game logic)
│   │   └── force_claim.gd    # Elemental force tracking + buffs
│   └── render/
│       └── ps1.gdshader  # Vertex snap, affine mapping, dither
├── assets/               # ALL EXTRACTED + RECOMBINED (see asset-manifest.md)
│   ├── models/           # TMD→glTF
│   ├── textures/         # TIM→PNG + EM BMP→PNG, recombined
│   ├── animations/       # Frame data JSON
│   ├── audio/            # WAV→OGG
│   └── stages/           # Arena data + backgrounds
├── ui/                   # Recombined menu assets + layout code
└── story/                # Story mode script, text cards
```

**What's reimplemented (from teardown):** Fighter physics, frame data application, hitbox resolution, juggle gravity, input buffering, throw breaks, wall-splats, counter-hits.

**What's original (our game logic):** Reincarnation Rounds, Nine-Soul Meter, Soul Surge, Force Claiming, story mode structure, Trader interactions.

---

## 5. BUILD PHASES

### Phase 0: Teardown Completion (in progress — other workers)
- Tekken 3 zip → ISO → TMD/TIM/animation catalog
- Ghidra → frame data / hitbox / system documentation
- Eastern Mind `.img` → Director cast → bitmap/audio catalog

### Phase 1: Pipeline (2–4 weeks est.)
- Write TMD→glTF, TIM→PNG, Director extractors
- Verify: one Tekken model renders in Godot with PS1 shader
- Verify: one Eastern Mind bitmap displays correctly

### Phase 2: Fighting Prototype (4–6 weeks est.)
- One fighter (RIN), one stage (Tree of Life), basic combat
- Implement: movement, 4-button attacks, blocking, hitboxes, health
- Target: it *feels* like Tekken 3

### Phase 3: Systems (3–4 weeks est.)
- Reincarnation Rounds (face builder + modifiers)
- Nine-Soul Meter + Soul Surge
- Juggles, throws, walls, counters

### Phase 4: Roster + Stages (4–6 weeks est.)
- All 9 fighters (bodies + skins + movesets)
- All 7 stages
- Force Claiming across arcade ladder

### Phase 5: Story + Polish (3–4 weeks est.)
- Story mode script, text cards, Trader, Assembled Soul boss
- Audio mix, UI completion, balance pass

**Total estimate:** 16–24 weeks for a playable build. Estimates are rough — the teardown unknowns (especially animation data format) are the biggest risk.

---

## 6. RISKS

| Risk | Mitigation |
|------|------------|
| Tekken 3 animation data format is undocumented | Ghidra analysis + PS1 reversing community docs; fallback: hand-derive frame data from gameplay footage (still using extracted models) |
| Director cast extraction tools don't handle 1994 format | The `.img` also contains rendered screens; worst case, capture from emulation (still Eastern Mind pixels, not hand-made) |
| TMD skeletons differ between characters | Normalize to a standard humanoid rig in the pipeline script (mechanical, not creative) |
| Scope creep (9 fighters × full movesets) | Phase 2 proves one fighter; roster expands only after core feels right |

---

## 7. WHAT WE NEVER DO

- Never model a character from scratch.
- Never paint a texture from scratch.
- Never compose a music track from scratch.
- Never generate art or audio with AI.
- Never use stock assets, asset store packs, or "temporary" placeholders that aren't extractions.
- If we can't extract it, we recombine something we *did* extract. If we can't recombine, the feature waits.

**The game is a collage. The collage is the art.**

---

*Technical plan 2026-10-12. Engine: Godot 4. All art/audio: extracted + recombined. All game logic: original code implementing reverse-engineered systems + original Western Heart systems.*
