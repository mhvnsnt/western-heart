# Entrance creation tools — repurposed, NOT replaced

## Owner decisions (2026-10-22)

- **Do NOT build full WWE-style entrances.** The existing Tekken-style
  intros and win taunts are OFF LIMITS — they stay exactly as they are.
- The entrance **creation tools** (timeline editor, camera tools, pyro,
  music sync) are repurposed for two jobs:
  1. **cutscene creation tools**
  2. **taunt creation tools**
- The tools get reused. The format stays ours.

## Naming — USER APPROVAL REQUIRED

> **The repurposed toolset needs a proprietary WH name. It is NOT
> "entrance" anything.** Until the user approves a name, every code
> and doc reference uses the working title below — nothing
> entrance-related is locked in.

**Working title: `WH_CINEMATIC_TOOLS_WORKING_TITLE`**
Status: PROPOSED — awaiting user-approved proprietary name.

## Tool inventory (what gets repurposed)

| Entrance-creation tool | Source in repo/teardown | Repurposed as |
|---|---|---|
| Timeline editor (phase timelines) | `game/js/transform-cinematic.js` (TransformCinematic phase API) | Cutscene shot timeline: shots with `t/dur/onStart/onUpdate/onEnd` |
| Camera tools | `game/js/photomode.js` (orbit/dolly/pan) + `game/js/scene.js` fight camera | Cutscene camera framing per shot; taunt close-up framing |
| Pyro / arena fx | arena fx + aura/shockwave systems (`hitfx.js`, fighter aura) | Cutscene beats (climax flashes, shockwaves) — NOT in-fight balance |
| Music sync | `tools/procgen/game-score/` (adaptive music) + promo-cinematic-kit ("music written to the cut times") | Cutscene scoring: beats timed to the shot timeline |

## Wiring map (creation suite menus)

Per the TOOL-TO-MENU WIRING LAW, each tool lands in the suite menu
where it belongs:

- **Cutscene tools** → suite "CINEMATICS" section:
  shot timeline editor (phases), camera framing per shot,
  fx beats, music-to-cut sync. Output: a `StoryEndingPlayer`-style
  shot list (see `docs/modes/STORY-ENDINGS-PIPELINE.md`) — the same
  player plays suite-authored cutscenes and per-character endings.
- **Taunt creation tools** → suite "TAUNTS" section:
  pose timeline + camera close-up framing + optional fx beat.
  Output: authored taunt data on the fighter profile. Win taunts
  that already exist are never overwritten — created taunts are
  *additional* selectable taunts.

## What this is NOT

- Not full WWE-style entrances (explicitly declined by the user).
- Not a replacement for intros or win taunts (owner-protected).
- Not a new format: cutscenes reuse the ending shot-list format;
  taunts reuse the pose/beat format the game already plays.

## Next step

User approves the proprietary name → rename `WH_CINEMATIC_TOOLS_WORKING_TITLE`
everywhere (code, docs, suite menus) in one pass.
