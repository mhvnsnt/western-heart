# Roly-Polys World Hub — Western Heart integration

Owner orders: "pull them in and wire into Western Heart with WH canon + WH
characters (never clones)" (2026-11-20 ~07:57 EST); "make the game PLAY
better" (same morning). Roly-Polys also feeds the world, environment, stages,
and the "god within" layer + canon — not just minigames.

## What shipped (branch `p2/rolypolys-world-hub`, NOT merged)

- `game/data/rolypolys-world.js` — the World Tour disc catalog, verbatim:
  7 areas, 40 regions, 288 scenes, per-continent endings, 6 embedded
  `*GAME.DXR` minigames + 2 mazes, 12 god-within anchors, 26 lore vignettes,
  3 Nanakorobi games. Source: `sato/rolypolys/WORLD-TOUR.md`
  (mhvnsnt/game-reverse-engineering, release `sato-rolypolys-20261120`).
- `game/js/rolypolys-hub.js` — hub state machine (sail → visit → collect →
  ending) + 4 playable minigames + DOM shell `mountRolyPolysHub(host)`.
- `game/side-games.html` — new "Banabana MK.1 — Roly-Polys World Hub" section
  in the Side Games hub (the page the main menu's SIDE GAMES opens), mounted
  with the same `<script type="module">` pattern as Shrine OS.
- `test/rolypolys-hub.test.mjs` — node test (CI pattern `node test/*.test.mjs`).

## How to play

Side Games → Banabana MK.1. Sail the ship area → region → scene; each scene
visit collects its item; finishing every scene in an area unlocks that area's
ending cinematic (AFEND / USAEND / ASIAEND / SAEND on disc; Europa, Japan,
Oceania close on the finale END.DXR). Minigames, all paying Soul Shards:
TOU's Shooting Gallery (8 targets, 30 s, 10 shards a hit), KAI's Cooking
School — Miso (stop the marker in the gold, 3 rounds), the Trader's Slot
(3 of a kind 10×, pair 2×), Bull Run — TOU's Ox Dodge (OXGAME.DXR shell,
5 shards a dodge). A–Z lore vignettes, hosted by RIN. Progress persists in
localStorage (`wh-rolypolys-hub-v1`).

## WH mapping (characters, never clones)

RIN leads (disc's Pon) · TOU hosts shooting (disc's Cho) · KAI hosts cooking
(disc's Mr. Okhotsk) · the Trader hosts the slot (disc's Las Vegas Akiko).
God-within anchors are the disc's own mythic sites (SHRINE, PRAYER, GODDESS,
TENG region / TENGIN3, PYRAMID, NASKA, BIGHEAD, DEVIL, STPAUL, TAJI) with
proposed WH stage names — proposals, not shipped stages.

## PULL-WORKING-COMPLETE record (owner law 2026-11-20 ~15:05 EST)

Pulled whole: the disc catalog data; the Side Games hub shell, Soul Shards
currency and canvas-game patterns (existing WH prototypes). Checked, NOT
pulled: ScummVM Director engine — it detects both games (`rolypolys`,
`rolypolys2`, v501) but neither appears on ScummVM's 2026.4.0 compatibility
chart (no support level at all) and it is a desktop runtime, not a phone web
build component. DirPlayer (Rust/WASM Shockwave) — boots some Shockwave
games, but the Roly-Polys slot .dcr is unverified in it and it is v0.2–0.4.
No fan remake / reimplementation / decomp of Roly-Polys exists anywhere
found (GitHub + web search 2026-11-20). No complete working source exists
for the shooting game, cooking game, slot, the six `*GAME.DXR` shells, or
the travel hub — those are WH-native builds from the verified disc
structures, recorded here, not rebuilt silently. Only OXGAME ships playable
among the six embedded games; the other five are data entries with rules
living inside their .DXR files. The 9,664 extracted PNGs + OST were NOT
pulled into the WH build (commercial assets, 500 MB+ disc) — catalog names
only. Follow-ups: desktop ScummVM boot test of ROLY_2; browser test of
slot.dcr in the DirPlayer polyfill.

## Verification

`node test/rolypolys-hub.test.mjs` passes (7 areas, 40 regions, 288 scenes,
26 vignettes, hub + all four games). Browser-capture proof (video /
screenshots) is BLOCKED: Chromium is SIGTRAP-broken box-wide, so no
playthrough could be captured on this box. The slice is verified by the
node test + static checks only; the coordinator own-eyes gate needs a
working browser (or the CI Playwright menu-touch job) before the owner
sees it. No proof was faked.
