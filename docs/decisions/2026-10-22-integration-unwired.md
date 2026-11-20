# Decision log — items left unwired by the 2026-10-22 integration pass

Worker 22. For each: what it is, why it stays unwired, and what would
change the decision. "Unwired" here means a deliberate decision, not neglect.

## 1. Tone.js (MIT) — not vendored, adapter stays the upgrade path
**What:** Full Web Audio framework (~1MB ESM). `tools/procgen/game-score/`
already ships `wh_tone_adapter.mjs` + `wh_adaptive_music.mjs` (unwired).
**Why unwired:** `game/js/audio.js` is a complete, zero-dependency procedural
audio engine (impacts, whooshes, KO stinger, taiko/shakuhachi battle loop)
that works today on the owner's phone. Vendoring Tone.js buys an upgrade
path we don't need yet at the cost of 1MB+ and a second audio paradigm.
**Revisit when:** the music lane wants real adaptive stems (layers that
follow fight intensity) — then vendor Tone and wire the existing adapter.

## 2. Chatterbox (voice default) — external service, never vendored
**What:** Owner law: Chatterbox stays the character-voice default.
**Why unwired:** It runs on the GPU server (Kaggle T4), not in the repo or
the game. The game is a thin client by architecture
(`docs/research/AI-INFERENCE-GAMESIDE-2026.md`). Vendoring is impossible
(weights) and wrong (licenses forbid redistribution).
**Wired instead:** `tools/character-voice/` (cleanup chain, changer rig
notes) + new `tools/character-voice/lipsync/` (WAV → mouth cues) +
`game/js/lipsync-player.js` (runtime cue playback).

## 3. Materialize / ArmorPaint — documented, code not vendored
**What:** Materialize (GPL-3.0 app) photo→PBR workflow; ArmorPaint (open
source, verify LICENSE at build) 3D paint + neural Image-to-PBR.
**Why unwired:** Both are desktop apps in the artist's workflow, not
libraries. Their workflows are documented (`tools/texture-pipe/`); their
*outputs* (PBR sets) are what the game consumes via `tools/texture-pipe/`.
Vendoring app source would add MBs nobody imports.
**Revisit when:** we want one-click in-suite texture painting — then wire
ArmorPaint's brush engine as a suite tab (needs a lane + owner call).

## 4. transformers.js (Apache-2.0) — not pulled
**What:** In-browser ML inference.
**Why not pulled:** The established architecture is server-side inference
(llama-server / ComfyUI on Kaggle T4, thin game client). In-browser models
would fight the phone's memory budget for no current use case.
**Revisit when:** a concrete client-side AI feature is specified (e.g.
on-device commentary) with a model that fits.

## 5. Rapier (Apache-2.0) — not pulled, cannon-es chosen
**What:** High-performance Rust/WASM physics.
**Why not pulled:** cannon-es (MIT, pure JS ESM, zero-dep) covers our
visuals-only physics needs (props, debris, KO tumble) with no WASM
payload and no build step. Rapier is faster but heavier to integrate;
combat never touches physics (determinism rule), so the speed is moot.
**Revisit when:** we need hundreds of simultaneous bodies or soft-body.

## 6. MoCapAnything — watched, not depended on
**What:** Video→any-skeleton mocap (arXiv 2512.10881).
**Why not pulled:** Research-grade, no usable release (per 2026-10-19
research). Keemap + Mixamo + Rokoko cover retargeting today.
**Revisit when:** it ships a release.

## 7. BlenRig 6 — not pulled (400MB)
**What:** Best free deformation rigging (GPL-3.0).
**Why not pulled:** 400MB over the disk budget; GameRig + auto_rig
backends cover game-ready rigs. Documented in OPEN-SOURCE-PULL-INS.
**Revisit when:** film-grade deformation is needed and disk frees up.

## 8. WMXIX .ymg meshes — BLOCKED (real, documented)
**What:** 1,200 WrestleMania XIX CAW part meshes.
**Why unwired:** The YOBJ vertex assembly is unsolved with existing
tooling (tangled ribbons; 11 hypotheses rejected; the one claimed
solution's artifacts aren't in the repo). Cataloged `blocked_ymg_decode`.
**Unblock path:** reverse the game's YOBJ vertex loader in main.dol or
take a Dolphin GX vertex dump. Until then: no fake GLBs.

## 9. WWE 2K pac/edit binaries — BLOCKED (~96GB transfer)
**What:** WWE 2K CAW parts (the creation-suite base the owner wants).
**Why unwired:** The binaries aren't on disk; structure-level integration
only. This is the standing blocker for the WWE-template base bodies.
**Unblock path:** the ~96GB transfer the owner scoped.

## 10. Tekken 7 .uasset item meshes — never pulled (open)
**What:** T7 customization item meshes (the slot schema IS wired).
**Why unwired:** Nobody has pulled the `.uasset` binaries yet.
**Next step:** a pull lane for the T7 item meshes, converted to GLB and
cataloged to the 16-slot schema like the No Mercy parts were.

## 11. lip-sync-engine WASM (37MB) — CDN, not vendored
**What:** The acoustic model + WASM for the lip-sync pipeline.
**Why not vendored:** 37MB of model data would bloat the repo and it
never ships to players — the game only consumes KB-sized `*.cues.json`.
The pipeline loads it from the package's own unpkg CDN on the crew
machine. Same pattern as Chatterbox/RVC (server side, thin client).
