# Zui — Steve Fox Base + Lei Drunken Fist + Stance Switching
**Date:** 2026-10-21
**Owner orders (verbatim):**
- "Wire zui models to Steve and his moves add in drunken gist moves and stance switch from boxing to drunken fist and Steve's other stances and such"
- "Add drunken fist to him from lei moves and stance switching added on top of Steve fix stance switching and boxing etc."
**Method:** Tekken + teardown code/data only. Zui's data only — no shared-engine edits (per-character isolation law). His model entries (assets.js / attires.js / roster-full.js) are owned by the separate zui-tripo wire lane; his base Steve bank bake is owned by the animation-bank lane.

## What was built
`game/assets/movesets/zui.json`: **156 → 482 moves** (additive union, zero loss).
Built by `tools` (builder + guard in the PR); reproducible — a fresh-input rebuild is byte-identical to the shipped file.

## Sources (all in-repo, all cited per move)
1. **Steve Fox full T7 set** — `docs/t7t8-reference/frame-data-t7/steve.json` (t7chicken / TekkenBot-extracted; SOURCE.json in the same dir). **286 of 287 rows imported.** Skipped: `steve_138` "WALL BOUND" — a mechanic row with no move input, nothing to wire.
2. **Lei Wulong drunken fist** — the 40-entry T7 Lei DRU census imported **verbatim** from `game/assets/movesets/rave.json` (35 DRU-prefixed + Drunken Master Walk f+3+4 + PHX 1+2 + PHX 1,D + 2 Startled Drunk entries), full T7 provenance retained on each row.
3. **Pre-existing Zui rows** — 17 Jin T3 proxy entries rekeyed under the repo convention `<input>_r<t3_row>` with payloads byte-identical; Steve's canonical input wins the canonical key (owner order: Zui's moves ARE Steve's). 12 import-vs-import collisions rekeyed the same way. `strings[]` untouched (29); `specials[]` 4 → 12 (buffer-parseable motions + stance-entry chords f+3+4 / b+3+4 only).

## Stance system (data-level, `zui.json` → `stances`)
The engine has **no stance flag** — that is the exact limit. Stances are expressed with the engine's existing mechanisms: entry moves resolve through the input buffer (`specials[]` / directionals); gated moves carry `stance` + `stance_gate` and resolve by exact-notation lookup (the same `getMove`/`tryAttack` path `fighter.js` uses). The `stances.system` string in the JSON records this honestly. No shared-engine edits were made.

| Key | Stance | Entry (touch-mapped) | Gated moves |
|---|---|---|---|
| BOX | Boxing — Steve Fox base stance (default) | — (all non-gated Steve T7 moves) | — |
| DCK | Ducking | `f+3` | 10 |
| LWV | Left Weave | `3` (from Ducking) | 14 |
| RWV | Right Weave | `4` (from Ducking) | 5 |
| FLK | Flicker Stance | `b+3+4` | 23 |
| PKB | Peekaboo | see note | 42 |
| SWY | Swaying | `b+3` | 3 |
| ALB | Albatross (spin) | `3+4` | 5 |
| DRU | **Drunken Fist — Drunken Master** | `f+3+4` (Drunken Master Walk) | 40 |

**PKB entry note (honest):** `f+3+4` is shared with Drunken Master Walk in the source data; on Zui the chord fires Drunken Master Walk (owner headline + Zui's "Drunken Master" canon title). Peekaboo's own entry row (steve_198) is preserved as `f+3+4_r198`; Peekaboo is entered in play via its `,F` transition strings.

**DRU exits:** `DRU b` (Back Roll), `DRU f` / `DRU f,b` in-stance movement; `DRU 1+2` (Tiger Sip) sustains the stance.

## Gaps — named, not papered over
1. **WALL BOUND (steve_138):** mechanic row, no input — skipped by rule, not by loss.
2. **DRU clip row-mapping:** T3 Lei's decoded motion bank exists (`teardown/tekken3/movesets/moveset_lei.json`, 604 rows) but carries no semantic move labels, so no `t3:lei:row:<n>` refs could be honestly assigned. DRU rows carry `t7:lei:<slug>` refs (same status as Rave's T7 kit). In-game they play bank generic clips by last button until the T7 anim pipeline exists. The DRU move list for the bank lane's bake is at `stance_expansion_20261021` in this JSON.
3. **Engine stance-flag limit:** no fighter-state stance flag exists; gating is data-level (exact-notation resolution). An engine-level stance flag would be a shared-engine change — out of lane scope, flagged here for the engine owners.

## Proof
- Guard: 156 → 482, 17 rekeyed-preserved, 286 Steve + 40 DRU imported, zero loss. Every imported move traces to a real `steve_*` T7 row id or a `rave.json` T7 Lei entry id.
- Node proof (17/17) against the game's real `TekkenBuffer` + registry from main: boxing jab = Steve's real T7 jab (steve_2, dmg 7); `f+3+4` resolves to Drunken Master Walk; `DRU 1` = Drunken Tiger Lash (gated); drunken string, exit (`DRU b`), Tiger Sip sustain; `b+3+4` → Flicker Stance; one gated move each from DCK/PKB/SWY/ALB/LWV/RWV; Peekaboo + legacy Jin payloads preserved.
- Harness fight: frames + console log under `your_files/zui-stances-20261021/` (see lane checkpoint for paths).
