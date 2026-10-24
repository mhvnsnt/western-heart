# Combined Creation Suite — Unified Spec (WWE 2K × Tekken) — 2026-10-19

**Owner order:** "their combined creative suite with the Tekken one fully."
**Design basis:** WWE 2K19 CAW depth + Tekken front-end/flow, per `docs/creation-suite/DESIGN.md` (v0)
which already mandates "deeper than the WWE 2K Creation Suite and Tekken Customization."
This doc is the v1 unified spec incorporating today's WWE 2K19 teardown findings.

## 1. Design principle

**WWE 2K depth, Tekken speed.** Every screen keeps Tekken's fast per-character list,
preset slots, category tabs, and always-on live preview. Every screen offers WWE 2K's
part depth, layering, morph sliders, paint/tattoo layers, and the 5,581-move library.

## 2. Suite structure (per game, renamed)

| Game | Suite name |
|------|-----------|
| Western Heart | Create a Fighter |
| Bannon | Create a Wrestler |
| AshLanev2 | Create a Brawler |
| brutalfistgrokversionten | Create a Fighter |

Flow: Main menu → suite → **Character** or **Moveset** → character list → sub-menu.

## 3. Character sub-menu (unified tabs)

1. **Presets** — saved looks (Tekken-style preset slots), community/shared recipes
2. **Body** — WWE 2K morph sliders (height/weight/muscle per region) + Tekken body-type presets
   + procedural morph targets for Tripo models (per DESIGN.md §3: `cs_<region>` targets)
3. **Head & Face** — WWE 2K face sliders (jaw/cheek/brow/nose/eyes/mouth/chin/ears) + hair/facial-hair parts
4. **Attire (layered)** — WWE 2K ordered layers per region (part + color/pattern/material);
   up to 8 attire slots per fighter (in-ring + entrance); Tekken category tabs for browsing
5. **Paint & Tattoos** — decal layers (position/scale/rotation/opacity), face paint, body paint
6. **Alternate Attires** — per-slot management
7. **Moveset** — see §4
8. **Profile & Style** — name/nickname/hometown, Face/Heel/Tweener, weight class, fighting style, AI
9. **Entrance** — choreography picker (from 186 entrance pacs), lighting, Titantron

## 4. Moveset editor (unified)

- **Library:** 5,581 WWE 2K19 moves (`MOVESET-LIBRARY-2026-10-19.md`) + Tekken/DOA/VF federation movesets
  (PR #314: Kasumi, Bass, Hayabusa, Akira, Sarah, Kage) + Bannon's 439-slot schema
- **Categories:** 25 (Bannon schema) extended with WWE positions (apron, diving, corner, submissions)
- **Slot edit:** position slot ← move; per-move AI (priority/repetition/timing)
- **Command list:** Tekken notation with frame data (Tekken-style inputs per owner law)
- **Preview:** live 3D preview of the move on the current character
- **Editor UX (owner law):** tap/scroll the library, tap to assign — NEVER drag-and-drop

## 5. Data model (DNA v2 + extensions)

```
FighterDNA {
  body:   { type, sliders: {height, weight, muscle, belly, chest, ...}, morphTargets },
  head:   { faceSliders: {...}, hair, facialHair, eyes },
  attire: [ { slot, layers: [ { partId, color, pattern, material } ] } ],  // 8 slots
  paint:  [ { layer, decalId, transform, opacity } ],
  moveset:{ slots: { position: moveId }, ai: {...} },
  entrance:{ pacId, lighting, pyro, titantron },
  victory: { face: sceneId, heel: sceneId },
  profile:{ name, nickname, hometown, reaction, weightClass, style },
  physics:{ springs: auto }  // size-adaptive secondary physics (DESIGN.md §4)
}
```

- DNA v2 is a strict superset of Bannon's DNA v1; `migrate()` reads v1 saves.
- Part IDs resolve against `customization/parts/` manifests (KayKit, Quaternius, WMXIX, No Mercy,
  Tekken slots, and — once pulled — `customization/parts/wwe2k/`).
- Move IDs resolve against the 5,581 library + federation movesets.

## 6. Implementation status

| Piece | Status |
|-------|--------|
| `packages/creation-suite` (DNA, body, secondary physics) | ✅ In repo |
| `docs/creation-suite/DESIGN.md` v0 | ✅ In repo |
| Bannon DNA v1 + moveset_schema.json (439 slots) | ✅ In repo (Bannon) |
| WWE 2K19 5,581-move library | ✅ This PR (data + doc) |
| DOA/VF federation movesets | ✅ PR #314 (open) |
| WWE 2K part meshes (`pac/edit/`) | 🔲 Blocked on 51GB pull |
| Entrance pac choreography data | 🔲 186 pacs have filenames; blob decode queued |
| In-game UI wiring | 🔲 Next lane |

## 7. What this PR adds

- `MOVESET-LIBRARY-2026-10-19.md` + `moveset-library-2k19.txt` (5,581 moves)
- `CAW-STRUCTURE-2026-10-19.md` (viewing/editing structure)
- `TRANSFER-PLAN-2026-10-19.md` (51GB+45GB pull plan)
- This spec (`COMBINED-CREATION-SUITE.md`)
