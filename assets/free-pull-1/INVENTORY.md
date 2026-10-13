# Western Heart — Free Asset Pull #1
**Date:** 2026-10-13
**Total size:** 126MB
**All licenses:** Free for commercial use (see per-item)

---

## 1. tk-fighting-game (5.4MB)
**Source:** https://github.com/kamijan44012-ux/tk
**License:** Check repo (open source)
**What:** "SHADOW STRIKERS" — complete browser-based 3D fighting game (Three.js/WebGL, 60fps mobile).
**Key files:** `js/fighter.js`, `js/game.js`, `js/characters.js`, `js/ai.js`, `js/audio.js`, `js/input.js`
**Western Heart use:** Combat system blueprint — frame data, hitboxes, health bars, super meter, combo popups, KO screen, AI. Reference implementation for Godot port.

## 2. Quaternius Animation Libraries (39MB)
**Source:** GitHub mirrors of https://quaternius.com (CC0, no signup)
- `quaternius/animations/` (29MB) — Universal Animation Library 1 Standard (UAL1_Standard.fbx) via IAFahim/quaternius.universalAnimationLibrary.standard
- `quaternius/gltf-animations/` (9.7MB) — glTF version via J-Ponzo/gltf-universal-animation-library
**License:** CC0 (public domain)
**Western Heart use:** Base animation clips for all fighters. Mixamo-compatible rig. Stopgap movesets until Tekken animations are extracted.
**Note:** Base character models need browser download from itch.io (not yet pulled).

## 3. Kenney Assets (13MB)
**Source:** https://kenney.nl (CC0) via GitHub mirrors
- `kenney/particles/` (11MB) — Particle Pack via Calinou/kenney-particle-pack. Hit sparks, impact flashes, dust.
- `kenney/audio/` (2MB) — Impact Sounds via Boyquotes/kenney-impact-sounds-for-godot. OGG format: footsteps, impacts.
**License:** CC0 (public domain)
**Western Heart use:** Soul Surge particle effects, hit impact visuals, fight SFX.

## 4. CMU Mocap Fighting Clips (36MB)
**Source:** https://github.com/konyshevgmbh/cmu-mocap (free for research/commercial per CMU terms)
**Location:** `cmu-mocap/fighting/` — 16 BVH files:
- Boxing: 13_17, 14_01, 17_10
- Punching/kicking: 143_23, 143_24
- Punch sequences: 144_20, 144_13
- Front kicks: 144_05, 144_09
- Blocks: 144_07, 144_26
- Karate: 135_04, 135_07, 135_09, 135_11
- Kicking/punching/knee: 86_06
**Western Heart use:** Real human fighting motion for retargeting onto Tekken models. Verified clip IDs from CMU database.

## 5. ambientCG PBR Textures (35MB)
**Source:** https://ambientcg.com (CC0, API download, 1K-JPG)
**Location:** `ambientcg/textures/`
- Wood096, Wood095 — wood grain (stages, weapons)
- Fabric085, Fabric084 — fabric/cloth (costumes, customization)
- Metal063, Metal049A — brushed metal (armor, accessories)
**License:** CC0 (public domain)
**Western Heart use:** PBR materials for stages, costumes, customization parts.

---

## Skipped (per task)
- **Sonniss GDC bundles** (10-50GB) — too big for current disk
- **Mixamo** (2,500+ clips) — needs Adobe ID signup
- **Sketchfab Lost Shrine** — needs account
- **Freesound** — needs account
- **Poly Haven** — deferred (ambientCG covers texture needs)
- **Quaternius base characters** — needs browser download from itch.io

## Next pulls (when disk/signup allows)
1. Quaternius Universal Base Characters (itch.io, ~50-100MB)
2. Mixamo fighting animations (Adobe ID needed)
3. Sonniss GDC SFX (needs 10GB+ free space)
4. Poly Haven HDRI + textures
