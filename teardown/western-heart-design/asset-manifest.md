# WESTERN HEART — ASSET MANIFEST
## Every Asset Traced to Its Reverse-Engineered Source

**The law:** Every texture, model, animation, and sound in Western Heart comes from one of two sources: the Tekken 3 teardown or the Eastern Mind extraction. Recombined, rearranged, recontextualized — never hand-created, never AI-generated, never fabricated.

**The only hand-made things:** The engine code (glue), this design doc, the asset pipeline scripts, and any small connective pieces the owner explicitly creates himself.

**Status key:**
- ✅ VERIFIED — file confirmed on disk
- 🔄 PENDING — teardown/extraction in progress, file expected but not yet confirmed
- 📋 SPECIFIED — format and location known, awaiting extraction

---

## SOURCE A: TEKKEN 3 (PS1)

**Location:** `~/workspace/game-reverse-engineering/tekken3/`
**Raw file:** `Tekken and roms for files/Tekken 3 (Everything Unlocked).zipy450_4m1.part` 🔄

### A1. Character Models (TMD format)
| Asset | Source file (expected) | Used for | Status |
|-------|----------------------|----------|--------|
| Jin Kazama body | `TMD/JIN.TMD` (in ISO) | RIN's body | 📋 |
| Lei Wulong body | `TMD/LEI.TMD` | BYOU's body | 📋 |
| Paul Phoenix body | `TMD/PAUL.TMD` | TOU's body | 📋 |
| Ling Xiaoyu body | `TMD/XIAOYU.TMD` | SHA's body | 📋 |
| Eddy Gordo body | `TMD/EDDY.TMD` | KAI's body | 📋 |
| Yoshimitsu body | `TMD/YOSHI.TMD` | JIN's body | 📋 |
| Bryan Fury body | `TMD/BRYAN.TMD` | RETSU's body | 📋 |
| Julia Chang body | `TMD/JULIA.TMD` | ZEN's body | 📋 |
| Hwoarang body | `TMD/HWOA.TMD` | GYOU's body | 📋 |
| Mokujin body | `TMD/MOKU.TMD` | THE TRADER's body | 📋 |
| True Ogre body | `TMD/OGRE2.TMD` | THE ASSEMBLED SOUL's body | 📋 |

*Note: Exact TMD filenames to be confirmed by teardown. PS1 Tekken 3 stores character models in the ISO filesystem; the teardown worker is mapping exact paths.*

### A2. Character Textures (TIM format)
| Asset | Source file (expected) | Used for | Status |
|-------|----------------------|----------|--------|
| All fighter base textures | `TIM/*.TIM` (in ISO) | Base texture maps before Eastern Mind reskin | 📋 |

*Note: Tekken TIMs are used as UV-layout reference and fallback. Primary skins are Eastern Mind bitmaps (see B2).*

### A3. Animations / Movesets
| Asset | Source file (expected) | Used for | Status |
|-------|----------------------|----------|--------|
| Jin's move animations | Animation data in executable + overlay files | RIN's moveset | 📋 |
| Lei's move animations | (as above) | BYOU's moveset | 📋 |
| Paul's move animations | (as above) | TOU's moveset | 📋 |
| Xiaoyu's move animations | (as above) | SHA's moveset | 📋 |
| Eddy's move animations | (as above) | KAI's moveset | 📋 |
| Yoshimitsu's move animations | (as above) | JIN's moveset | 📋 |
| Bryan's move animations | (as above) | RETSU's moveset | 📋 |
| Julia's move animations | (as above) | ZEN's moveset | 📋 |
| Hwoarang's move animations | (as above) | GYOU's moveset | 📋 |
| Frame data tables | Executable disassembly (Ghidra) | All frame data | 📋 |
| Hitbox data | Executable disassembly (Ghidra) | All hitboxes | 📋 |
| Juggle physics constants | Executable disassembly (Ghidra) | Air combo system | 📋 |

### A4. Stage Geometry
| Asset | Source file (expected) | Used for | Status |
|-------|----------------------|----------|--------|
| Stage collision/mesh format | Stage data in ISO | All 7 stage arena layouts | 📋 |
| Wall-splat trigger volumes | Executable disassembly | Helix Palace, Shrine walls | 📋 |

### A5. Audio
| Asset | Source file (expected) | Used for | Status |
|-------|----------------------|----------|--------|
| Hit sound effects | `VAB/VAG` sound banks in ISO | Combat SFX base | 📋 |
| Announcer voice | XA audio streams | Round announcements (recontextualized) | 📋 |
| UI sounds | Sound banks | Menu navigation | 📋 |

### A6. Fighting Logic (reference only — reimplemented, not copied)
| Asset | Source | Used for | Status |
|-------|--------|----------|--------|
| Game loop architecture | Ghidra disassembly | Engine structure reference | 📋 |
| Input buffer system | Ghidra disassembly | Input handling reference | 📋 |
| State machine design | Ghidra disassembly | Fighter state logic reference | 📋 |

*Note: We reimplement the logic in our own code. We do not copy executable code. The disassembly is a reference for understanding, not a source for copy-paste.*

---

## SOURCE B: EASTERN MIND (Mac/Win)

**Location:** `~/workspace/animation-techniques/steal-like-artist/osamu-sato/game/`
**Raw file:** `eastern-mind-tongnou.zip` → `EasternM/cd/eastern mind.img` (697MB CD image) ✅ VERIFIED

### B1. Character Skins (Director-embedded bitmaps)
| Asset | Source file (expected) | Used for | Status |
|-------|----------------------|----------|--------|
| Protagonist sprites | Bitmaps in `eastern mind.img` (Director cast) | RIN's skin | 📋 |
| Soul creature sprites (8) | Bitmaps in Director cast | Other 8 souls' skins | 📋 |
| Illustrated Book scans | In-game book screens | Skin detail reference | 📋 |
| Reincarnation face parts | Reincarnation screen bitmaps (3 eyes, 3 noses, 3 mouths) | Reincarnation Round faces | 📋 |

### B2. Stage Visuals (Director-embedded bitmaps)
| Asset | Source file (expected) | Used for | Status |
|-------|----------------------|----------|--------|
| Land of Time backgrounds | Director cast bitmaps | Plains of Chi-u stage | 📋 |
| Fire Tower sprites | Director cast | Chi-u background element | 📋 |
| Helix Palace room bitmaps | Director cast (5 rooms) | Helix Palace stage | 📋 |
| Palace of Dreaming bitmaps | Director cast | Dreaming stage | 📋 |
| Tree of Life bitmaps | Director cast | Tree of Life stage | 📋 |
| Sha-mo Desert backgrounds | Director cast | Tree of Life horizon | 📋 |
| Phantom Marketplace bitmaps | Director cast | Marketplace stage | 📋 |
| Eyeball mountain sprites | Director cast | Marketplace background | 📋 |
| Shrine Par-fang bitmaps | Director cast | Shrine stage | 📋 |
| Head-interior sky textures | Director cast | Shrine skybox | 📋 |
| Drill-wound event bitmaps | Director cast | Secret stage | 📋 |
| Katana of Five Forces bitmap | Director cast | Force-complete overlay | 📋 |

### B3. Audio
| Asset | Source file (expected) | Used for | Status |
|-------|----------------------|----------|--------|
| Land of Time music | Audio in Director cast / `eastern mind.img` | Stage 1 music | 📋 |
| Land of Desire music | (as above) | Stage 2 music | 📋 |
| Land of Dreaming music | (as above) | Stage 3 music | 📋 |
| Land of Life music | (as above) | Stage 4 music | 📋 |
| Marketplace music | (as above) | Stage 5 music | 📋 |
| Central Mountain music | (as above) | Stage 6 music | 📋 |
| UI/click sounds | Director cast | Menu sounds (layered with Tekken UI) | 📋 |
| Ambient creature sounds | Director cast | Stage ambience | 📋 |

### B4. UI Elements
| Asset | Source file (expected) | Used for | Status |
|-------|----------------------|----------|--------|
| Eastern Mind font/typography | Director cast | Menu headings, story cards | 📋 |
| Button/interface bitmaps | Director cast | Menu buttons (recombined with Tekken UI) | 📋 |
| Map/illustration assets | Director cast | Stage select screen | 📋 |

---

## SOURCE C: HAND-MADE GLUE (allowed)

| Asset | Description | Status |
|-------|-------------|--------|
| Engine code (Godot) | Fighting engine reimplementation, game logic, Reincarnation system, Force Claiming, Soul Meter | To be written |
| Asset pipeline scripts | TMD→glTF, TIM→PNG, BMP→PNG converters | To be written |
| Design documents | This manifest, design docs | ✅ In progress |
| Build scripts | Compilation, packaging | To be written |

**Explicitly NOT allowed:** Hand-drawn textures, hand-modeled characters, AI-generated art, AI-generated music, stock assets, fabricated "placeholder" art. If an asset can't be traced to Source A or B, it doesn't go in the game.

---

## EXTRACTION DEPENDENCIES

This manifest is a **specification**, not a completion report. The following must finish before asset production begins:

1. 🔄 Tekken 3 zip download completion (`tekken3/` worker)
2. 📋 Tekken 3 ISO extraction and TMD/TIM catalog
3. 📋 Ghidra disassembly → frame data / hitbox documentation
4. 📋 Eastern Mind `eastern mind.img` mounting and Director cast extraction
5. 📋 Bitmap/audio catalog from Director cast

**Honest status:** As of 2026-10-12, Source A raw file is partially downloaded. Source B raw file is verified on disk but not yet extracted. No game assets have been extracted yet. This manifest defines *what* to extract and *where* each asset goes — it does not claim extraction is complete.

---

*The USE THE IMAGE LAW applied to games. The source files are the material. We rearrange reality; we don't invent it.*
