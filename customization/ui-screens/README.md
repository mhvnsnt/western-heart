# UI screens — the workshop's screen definitions

The UI WORKSHOP (`game/ui-workshop.html`) is the visual screen builder: the user
drags elements, styles them, previews live, and exports through the SAME
round-trip patch as everything else (`ui_screen_define` kind in `wh-tweak-patch`
v1 — see `customization/TWEAK-PATCH-SPEC.md`).

## Sourcing order (owner directive)

1. **Tekken 8 FIRST.** `t8-source/` holds extracted T8 UI art when the extraction
   lane delivers it. The workshop prefers t8-source assets whenever present —
   get T8's UI to 100% before anything else.
2. **Other games layered on top** from teardown files (`other-sources/`).
3. **Built-in templates** (this dir, `*.t8-template.json`) are RECREATIONS of T8
   screen layouts — structure only, zero extracted art. They exist so the
   workshop is usable today; they swap to real assets the moment t8-source lands.

## Proprietary remix (the whole point)

T8 is the starting template; the USER's workshop edits make it ours. Every
user-remixed screen is saved as `<screen-id>.json` here (proprietary Western
Heart version). The `source` field on each screen records its lineage
(`t8-template`, `t8-source`, `workshop`, ...).

## Format

`wh-ui-screen` v1 — see `game/js/ui-screen.js` (loader, renderer, validator).
Element types v1: `label`, `button`, `panel`, `image`, `card-grid`
(data-bound: `stages`, `fighters`). `flow` and `wiring` sections are reserved
for the flow-designer and wiring phases.

## Open-source power

Element styling builds on the MIT-licensed game-hud kit
(`tools/creation-suite/ui-kit/game-hud/`, Fantasy dark/gold skin) — pure
HTML/CSS, zero deps, matching our stack.
