# WESTERN HEART — Asset Catalog
## Free / Open-Source / Leaked Content for the Chimera Build

**Compiled:** 2026-10-12/13 · **Purpose:** Get ahead of the curve before game teardown files arrive.
**Rule:** Every entry is free to use (CC0, CC-BY, MIT, royalty-free, or public research data). No AI-generated filler — real assets only.
**License note:** Always re-verify the license on the source page before shipping. Licenses change.

---

## 1. CHARACTER MODELS

### Quaternius — Universal Base Characters
- **URL:** https://quaternius.itch.io/universal-base-characters
- **License:** CC0 (stated on itch.io page; note: quaternius.com also publishes a QAL license — resolve any conflict before commercial use)
- **Format:** GLB/GLTF + FBX/OBJ in zip · **Size:** ~50-100MB per pack
- **Signup:** None (itch.io free tier downloads anonymously)
- **Use for Western Heart:** Base meshes for background fighters, NPCs, crowd characters. Adult-proportioned, rigged. The "Universal" rig is Mixamo-compatible, so all Mixamo animations work on these with zero retargeting.
- **Also grab:** Modular Character Outfits (Fantasy) — separates for customization system prototyping.

### Quaternius — RPG Character Pack (Warrior, Wizard, Cleric, Monk, Ranger, Rogue)
- **URL:** https://quaternius.com (packs page; download folder linked from site)
- **License:** CC0 1.0 Universal
- **Format:** GLTF + textures, weapons as FBX · **Size:** ~100-200MB
- **Signup:** None
- **Use for Western Heart:** The **Monk** is a perfect Zui (drunken master) placeholder/prototype body. Warrior for generic brawler NPCs. All rigged and animated.

### Mixamo Auto-Rigger + Character Library
- **URL:** https://www.mixamo.com/
- **License:** Free for use in games/commercial projects (Adobe ID terms; raw downloads not for redistribution)
- **Format:** FBX (with/without skin), auto-rig any humanoid mesh in ~2 min
- **Signup:** Yes — free Adobe ID required
- **Use for Western Heart:** Rig ANY extracted Tekken/Urban Reign mesh that arrives without a skeleton. Also provides base characters (Y Bot, X Bot) for animation testing.

---

## 2. FIGHTING ANIMATIONS

### Mixamo Fighting Animation Library (2,500+ clips)
- **URL:** https://www.mixamo.com/
- **License:** Free for commercial use (Adobe ID)
- **Format:** FBX, 30/60fps · **Size:** KBs per clip
- **Signup:** Yes — free Adobe ID
- **Search terms:** `punch`, `jab`, `cross`, `hook`, `uppercut`, `roundhouse`, `side kick`, `front kick`, `block`, `guard`, `hit reaction`, `stagger`, `knockdown`, `get up`, `fighting idle`, `dodge`, `roll`
- **Use for Western Heart:** THE stopgap moveset library. Every Western Heart fighter needs: idle, walk, jab, cross, kicks, block, hit-react, knockdown, get-up, KO. All downloadable today. Retarget onto Tekken skeletons via the existing Mixamo retarget pipeline.
- **Bulk download:** Community console scripts exist for batch download (GitHub gists: "Downloads all the free Mixamo Animations") — useful for grabbing the full fighting set at once.

### Quaternius — Universal Animation Library 2 (130+ clips)
- **URL:** https://quaternius.itch.io/universal-animation-library-2
- **License:** CC0
- **Format:** GLB (also `_RM` root-motion variant) · **Size:** ~25-50MB
- **Signup:** None
- **Use for Western Heart:** Sword/shield/block/hit moves included. Same rig as Universal Base Characters = no retargeting. Good for Phantom (sword) prototyping.

### CMU Graphics Lab Motion Capture Database (2,500+ clips)
- **Mirror (BVH):** https://github.com/konyshevgmbh/cmu-mocap
- **Mirror (FBX):** https://archive.org/details/Huge_FBX_Mocap_Library (2,534 clips, organized by group, with spreadsheet index)
- **Original:** http://mocap.cs.cmu.edu/
- **License:** Free for research AND commercial use worldwide (NSF-funded; BVH converter adds no restrictions). Requested acknowledgement: "The data used in this project was obtained from mocap.cs.cmu.edu. Created with funding from NSF EIA-0196217."
- **Format:** BVH (120fps) / FBX · **Size:** Full set ~5GB BVH, ~380MB cleaned 30fps set
- **Signup:** None
- **Verified fighting clips (BVH paths on the GitHub mirror):**
  - Boxing: `data/013/13_17.bvh`, `data/014/14_01.bvh`, `data/017/17_10.bvh`
  - Punching/kicking: `data/143/143_23.bvh`, `data/143/143_24.bvh`
  - Punch sequences: `data/144/144_20.bvh`, `data/144/144_13.bvh`
  - Front kicks: `data/144/144_05.bvh`, `data/144/144_09.bvh`
  - Blocks: `data/144/144_07.bvh`, `data/144/144_26.bvh`
  - Karate (mae-geri, mawashi-geri, oi-zuki, yoko-geri): `data/135/135_04.bvh`, `135_07`, `135_09`, `135_11`
  - Kicking/punching/knee: `data/086/86_06.bvh`
- **Use for Western Heart:** Real human martial-arts motion for moves Mixamo doesn't cover well (karate kicks, blocks). Retarget BVH→Tekken skeleton in Blender.

### RancidMilk CMU Conversions (itch.io)
- **URL:** Search "RancidMilk" on itch.io
- **License:** CC0 / Free
- **Format:** FBX + GLTF (CMU clips pre-converted)
- **Signup:** None
- **Use for Western Heart:** Same as CMU above but pre-converted — faster to drop into the pipeline.

---

## 3. EASTERN / JAPANESE ENVIRONMENTS

### "Lost Shrine" — Japanese temple (Sketchfab)
- **URL:** https://sketchfab.com/3d-models/lost-shrine-a87f6bdabe8c4cecad69e81136d98c8a
- **License:** CC Attribution (CC-BY) — credit required
- **Format:** Downloadable 3D (GLB/FBX/OBJ) · 38.6k tris, 19.8k verts
- **Signup:** Free Sketchfab account for download
- **Use for Western Heart:** Shrine-stage prototype. Eastern Mind's shrine/temple aesthetic. Perfect for a Phantom or Diablo stage.

### Sketchfab — Kiyomizu Temple models (tag search)
- **URL:** https://sketchfab.com/tags/kiyomizu-temple
- **License:** Varies per model — filter by "Downloadable" + check each license
- **Signup:** Free account for download
- **Use for Western Heart:** Real Kyoto temple architecture for stage backgrounds. Multiple artists, multiple quality levels.

### Free3D — Japanese Temple (free)
- **URL:** https://free3d.com/3d-model/japanese-temple-101392.html
- **License:** Free (check page terms)
- **Format:** .blend / .obj / .fbx
- **Signup:** None stated
- **Use for Western Heart:** Backup temple model if Sketchfab options don't fit.

### Quaternius Environment Packs (nature, village, props)
- **URL:** https://quaternius.com (packs page)
- **License:** CC0
- **Format:** GLB/FBX/Blend · **Size:** varies
- **Signup:** None
- **Use for Western Heart:** Bamboo forest / village outskirts stages. Stylized Nature MegaKit + MedievalVillage packs. Low-poly matches a stylized Eastern Mind look; NOT photorealistic.

### Steam Workshop — Shitennō-ji pagoda (from Sketchfab CC-BY model)
- **URL:** https://steamcommunity.com/workshop/filedetails/?id=3159732905
- **License:** CC Attribution (traces to Sketchfab model by galaxxxy)
- **Use for Western Heart:** Five-storied pagoda — Central Mountain / temple stage landmark.

**Stage mapping suggestion:** Shrine stage (Lost Shrine) → Phantom/Diablo · Bamboo/village (Quaternius) → Saku Ra/Kinpo · Pagoda (Shitennō-ji) → final boss / Assembled Soul stage.

---

## 4. FIGHTING GAME UI

### `tk` — 3D fighting game with FULL UI (GitHub)
- **URL:** https://github.com/kamijan44012-ux/tk
- **License:** Check repo (open-source)
- **What it has:** Main menu, character select, **animated health bars, super meter, round timer, round pips, combo popups, K.O. result screen.** Real Mixamo-skeleton fighters, frame-data-driven moves (startup/active/recovery), hitboxes vs hurtboxes, blocking with chip damage, i-frame dodges, hitstop, camera shake. Procedural Web Audio SFX (zero asset downloads). Mobile-first controls.
- **Use for Western Heart:** THE reference implementation. Study its UI code for: health bar animation, super meter (→ Nine-Soul Meter), round timer, combo counter, KO screen. Its frame-data structure is the template for Western Heart's moveset data format. **This is the single most valuable find in this catalog.**

### Devasura — 2D fighting game (Unity, mythological)
- **URL:** https://github.com/vigneshwar-balakrishnan/devasura
- **License:** Check repo
- **What it has:** Character selection screen, real-time combat with health bars, end-game UI, replay, scene management (MainMenu → CharacterSelect → FightScene), health/damage system.
- **Use for Western Heart:** Character-select flow and scene architecture reference. Mythological theme (Indra vs Ravana) is spiritually adjacent to Eastern Mind.

### Champions Struggle — 2D fighting game
- **URL:** https://github.com/ethanpintoa/itcs-4230-champions-struggle
- **License:** Check repo
- **What it has:** Character select (1P/2P), health (green) + energy (purple) bars, local multiplayer, special moves at 50% energy.
- **Use for Western Heart:** Energy-bar → Soul Surge meter UI reference. Simple, readable implementation.

### Kenney UI Packs (CC0)
- **URL:** https://kenney.nl/assets (search "UI pack", "pixel UI pack")
- **Also:** https://github.com/Calinou/kenney-ui-audio (50 UI sounds, Godot-ready, CC0)
- **License:** CC0 1.0 Universal
- **Signup:** None
- **Use for Western Heart:** Buttons, panels, health-bar frames, menu chrome. Placeholder UI that looks clean from day one.

---

## 5. AUDIO

### Freesound.org — CC0 Fight Sounds (verified)
- **Punches (CC0):** https://freesound.org/people/Velvorn/sounds/96486/ (4.7s, 808KB WAV, 5.6K downloads)
- **Punching (CC0):** https://freesound.org/people/JadeW40/sounds/816107/ (9s MP3)
- **Heavy punch (CC0):** https://freesound.org/people/steveuk87/sounds/490769/ (0.27s OGG, 5.2K downloads)
- **Game punch (CC0):** https://FreeSound.Org/people/qubodup/sounds/773737/ (mouth-made, Shure SM7B)
- **License:** CC0 — commercial OK, no attribution
- **Signup:** Free Freesound account required to download
- **Use for Western Heart:** Core hit-impact library. Layer 2-3 per impact for weight.

### OpenGameArt — "Punches, hits, swords and squishes"
- **URL:** https://opengameart.org/node/39377
- **License:** Mixed CC-BY/CC0 (attributions in zip)
- **Use for Western Heart:** Pre-layered fight SFX bundle (punches, sword slices, whooshes). Sword sounds → Phantom's blade.

### Sonniss GDC Audio Bundles (royalty-free, commercial OK)
- **URL:** https://sonniss.com/gameaudiogdc2020/ (50+ GB, 1,466 sounds; earlier years: search "sonniss gdc 2019", "sonniss gdc 2018" — 10-20GB each)
- **License:** 100% royalty-free, commercial use, no attribution. (Do not resell raw.)
- **Format:** 16/24-bit WAV · **Size:** 10-50GB per bundle
- **Signup:** None (direct/torrent/mirror links)
- **Use for Western Heart:** THE bulk SFX library. Crowd ambience, impacts, whooshes, drones, atmospheres. Download once, search forever. **Note:** huge download — pull selectively or via torrent.

### Kenney Impact Sounds + UI Audio (CC0)
- **URL:** https://kenney.nl/assets/impact-sounds · https://kenney.nl/assets?q=audio
- **License:** CC0
- **Signup:** None
- **Use for Western Heart:** Clean stylized impacts (hit_*, block_*) that match a non-photoreal art direction. UI clicks for menus.

### ⚠️ BBC Sound Effects — NOT for commercial use
- 33,000 sounds, free to browse/download — but under **RemArc license: research/education/personal only.** Commercial use requires purchase via pro-sound-effects. **Do NOT use in Western Heart.** Listed here only to prevent accidental use.

### Still needed (not yet sourced)
- **Taiko drums / gongs:** search Freesound CC0 for "taiko", "gong", "shime-daiko". Japanese percussion for menu stingers, round-start, Soul Surge activation.
- **Crowd ambience:** Sonniss bundles contain crowd beds; Freesound "arena crowd" CC0.

---

## 6. TEXTURES / MATERIALS

### Poly Haven (CC0)
- **URL:** https://polyhaven.com
- **License:** CC0 — no account, no attribution
- **What:** 1,000+ PBR textures (wood, metal, fabric, stone), HDRIs, scanned models. API available.
- **Use for Western Heart:** Stage materials (temple wood, stone floors, bamboo), HDRI lighting for renders. Downscale to 1-2K for game use.

### ambientCG (CC0)
- **URL:** https://ambientcg.com
- **License:** CC0
- **What:** 2,000+ PBR materials up to 8K, direct zip download, JSON API (`https://ambientcg.com/api/v2/full_json?q=<term>`, zips via `https://ambientcg.com/get?file=<Id>_1K-JPG.zip`)
- **Signup:** None
- **Use for Western Heart:** Character-adjacent materials: cloth (gi/uniforms), leather (gloves/boots), metal (Phantom's sword, SAM-UR-A1's plating), skin detail overlays.

**Texture mapping suggestion:** Wood → dojo/temple stages · Stone → shrine stages · Fabric → fighter uniforms (recolor per character) · Brushed metal → SAM-UR-A1 · Paper/rice-paper → UI backgrounds, Phantom Marketplace.

---

## 7. PARTICLE EFFECTS

### Kenney Particle Pack (CC0)
- **URL:** https://kenney.nl/assets/particle-pack
- **License:** CC0 1.0 Universal
- **What:** Sprite-sheet particles including `spark_05.png` (hit sparks), `muzzle_03.png` (impact flash), smoke, trails.
- **Signup:** None
- **Use for Western Heart:** Hit sparks, block sparks, KO explosion, dust on knockdown. Drop-in sprites for any particle system.

### Soul Surge auras (to build)
- No pre-made "energy aura" CC0 pack found that matches the Eastern Mind aesthetic. **Recommendation:** build from Kenney sparks + custom shader (fresnel glow) rather than hunting further. The `tk` repo's "energy-glow impact effects" are a code reference.

---

## 8. LEAKED / PRODUCTION-INTEL CONTENT

### Shoryuken Forums Archive — Frame Data & Moveset Editing Docs
- **Frame data guide:** http://archive.supercombo.gg/t/basic-frame-data-guide-for-newbies/102006 (how to read startup/active/recovery, block stun, hit stun)
- **Moveset editor docs:** http://archive.supercombo.gg/t/changing-frame-data-with-ono-in-ssf4-ae-pc/134587 (Ono! editor: animation↔frame mapping, hitbox assignment, speed curves — directly applicable to how Western Heart movesets become data)
- **Use for Western Heart:** The `tk` repo implements frame data; these docs explain the DESIGN. Together they give both theory and code.

### Smashboards — Melee Moveset Data Spreadsheet
- **URL:** https://smashboards.com/threads/moveset-data-thread-chart-updated-dec-04-12.329221/
- **What:** Per-character .xlsx with subactions, hitbox values (ID, bone, damage, size, X/Y/Z, angle, knockback scaling)
- **Use for Western Heart:** Template for the Western Heart moveset spreadsheet format. Columns map 1:1 to what a fighting game needs per move.

### Smashboards — Frame Data Compilation (concepts)
- **URL:** https://smashboards.com/threads/frame-data-compilation.226026/
- **What:** Frame-timing fundamentals (60fps = 1 frame, invincibility windows, shield timing)
- **Use for Western Heart:** Timing bible for the combat designer.

### Tekken community frame data
- **Status:** Not directly verified in this hunt. Known community resources exist (Tekken frame data wikis/apps). **Next step:** targeted search for "Tekken 7 frame data" + character names when building Demonio/Pantera movesets. TekkenMods docs repo (already cloned at `tekken7/tekkenmods-docs`) may contain data-format documentation.

---

## PRIORITY PULL LIST (do first)

| # | Asset | Why first |
|---|-------|-----------|
| 1 | `tk` repo (GitHub) | Full fighting-game UI + frame-data combat code — the blueprint |
| 2 | Mixamo fighting animations | Every fighter's stopgap moveset, downloadable today |
| 3 | Sonniss GDC bundle (selective) | Bulk SFX library — pull impacts/crowds/whooshes only |
| 4 | Quaternius Universal Base + Animation Library 2 | Rigged bodies + 130 clips, Mixamo-compatible, CC0 |
| 5 | CMU mocap fighting clips (FBX mirror) | Real karate/boxing motion for signature moves |
| 6 | Kenney Particle Pack | Hit sparks day one |
| 7 | Poly Haven / ambientCG | Stage + material basics |
| 8 | Sketchfab Lost Shrine | First Eastern Mind stage prototype |

---

## SIGNUP SUMMARY

| Needs free signup | No signup |
|---|---|
| Mixamo (Adobe ID) | Quaternius (itch.io) |
| Freesound | Kenney.nl |
| Sketchfab (download) | Poly Haven |
| | ambientCG |
| | Sonniss |
| | CMU mirrors (GitHub/Archive.org) |
| | OpenGameArt |

---

*Catalog compiled by asset-hunt subagent, 2026-10-12/13. No files downloaded — catalog only, per task. All URLs verified live at time of search except where noted.*
