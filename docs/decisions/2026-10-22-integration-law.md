# Decision log — INTEGRATION LAW (user directive 2026-10-22, permanent)

Worker 63. The user called this one permanent: it governs how everything
pulled into Western Heart gets wired up.

## Owner verbatim (2026-10-22)

"Wire everything up that you pull in in a way that's aligned with the Tekken systems and menus. Don't just throw in a bunch of random menus and extra systems on top of stuff. Make it within submenus and subsystems of us trying to build into the Tekken teardown file direction of the layout of everything and the menus and all that. Everything that you pull in, set it up in a Tekken way."

## The rules (user-set)

1. Every pulled asset/system gets integrated into the Tekken menu/system structure — as submenus and subsystems, never as bolted-on random menus or extra systems piled on top of existing ones.
2. Tekken is the architectural authority for layout, menus, flow, everything. New work follows the direction of the Tekken teardown files.
3. No parallel systems competing with Tekken's structure — everything pulled in nests inside it.

## End goal (user-set)

"Keep setting up and pulling in everything from the Tekken games until my game has 100% of all the Tekken games wired up from the back end to the front end, everything."

100% Tekken coverage — every game, every system, backend to frontend.

## What this means for workers

- A new system (jukebox, replays, Gungaku, Soul Urge, arena drafts, whatever) ships as a Tekken-structured submenu/subsystem, matching how Tekken lays out that screen — not as a new top-level menu inventing its own layout.
- When a Tekken teardown shows the canonical layout for a screen/mode, that layout is the target; proprietary additions (canon mapping, Nine-Soul flavor) layer inside it, never as competing chrome.
- Pairs with the canon-mapping requirement (every system canon-mapped) and the input-to-move fidelity law: Tekken feel, Tekken structure, our canon inside.
- Deliberately unwired items (see `2026-10-22-integration-unwired.md`) stay unwired — this law governs HOW things get wired, not THAT everything must be wired immediately.

## Standing references

- Law: `docs/owner-directives.md` → INTEGRATION LAW (permanent section).
- Repo reference: `AGENTS.md` → INTEGRATION LAW.
- Tekken 3 model carve-out: `docs/decisions/2026-10-22-tekken3-scope.md`.
