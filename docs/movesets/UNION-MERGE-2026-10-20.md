# Moveset union merge — 2026-10-20

Additive union of **all 548 historical versions** (60 commits, all refs) of
`game/assets/movesets/*.json` over current main, resumed from the merge the
prior agent started (its scratch did not survive; the pull was reproduced
exactly from git history — 548 unique (path, blob) versions, 0 missing).

## Method

- Identity = canonical input: `entry.input` when declared, else the storage
  key, whitespace-normalized (spaces around `,`/`+` provably break the runtime
  parser in `game/js/movesets.js` — the only normalization applied).
- Main preserved verbatim: no existing move, string, or special edited,
  rekeyed, or removed. Main wins contested inputs (PR #357 precedent).
- Historical moves whose canonical input is absent from main are added,
  payload verbatim from history; distinct payloads sharing one input are
  kept under the repo `<input>_r<row>` rekey convention.
- Era standard (owner 2026-10-20): addition payloads selected newest-era
  first — T8/WH, T7, TTT2, T6/other teardowns — richest within era; T3
  payloads only where no newer expression exists. Union-first: preferring
  newer data never deletes an older move/string/special.
- Tools: `tools/moveset-merge/build_merge.py` (merge),
  `tools/moveset-merge/guard.py` (independent no-loss guard).

## Result

**9 files changed: +33 moves, +2 strings, +5 specials.** The other 87 fighters' current files already equal their full historical union (proven by the guard).

| Fighter | Moves before → after | Added moves | Strings + | Specials + | Dominant era of final set |
|---|---|---|---|---|---|
| doa-bass | 20 → 22 | P+K, S | 0 | 0 | T6/other-teardown |
| doa-hayabusa | 16 → 18 | S, u+K | 0 | 0 | T6/other-teardown |
| doa-kasumi | 18 → 20 | D+P, S | 0 | 0 | T6/other-teardown |
| docfrank | 102 → 114 | P+K, S, d,d/f,d,d/f+1+2, d,d/f,d,d/f+1+2_r276, d/b,n,f+2, d/b,n,f+2_r271, d/f+2, d/f+2_r156, f+1, f+1_r110, n,d,d/b+1+3, n,d,d/b+1+3_r269 | 0 | 3 | T3 |
| ryuji-rock | 22 → 24 | d/f+1+2, f,f+1 | 0 | 0 | T3 |
| vainabel | 44 → 52 | 2,1, 2,1,2, P+K, S, d,d/f,d,d/f+1+2, d/f+2, n,d/b,n,f+1+2, u/f+4 | 2 | 2 | T6/other-teardown |
| vf-akira | 19 → 20 | S | 0 | 0 | T6/other-teardown |
| vf-kage | 12 → 14 | D+K, S | 0 | 0 | T6/other-teardown |
| vf-sarah | 12 → 14 | S, b+K | 0 | 0 | T6/other-teardown |

## Guard (the law)

`guard.py` independently verifies, per fighter: base preservation (every main
move/string/special deep-equal), union coverage (every historical canonical
input present), and no fabrication (every added key traces to a historical
version). **Result: 96/96 fighters PASS** — no move, string, special, or
working input lost vs the union of all versions + current main.

## Era notes (owner standard: newest-era target, T3 = fallback only)

Fighters whose final set is **T3-only** — no newer-era data exists in ANY of
their 548-version history; flagged as gaps for the teardown lanes, not
silently substituted:

- demonio-human: {'T3': 102}
- doc-frank-hood: {'T3': 101}
- doc-frank-wowomomo: {'T3': 101}

Small unprovenanced sets (no era fields in any version):

- burger-speed-demon: {'unprovenanced': 12}
- burger-the-mouth: {'unprovenanced': 12}

All other fighters carry T6-or-newer expressions (T7/T8 frame-data folds,
TTT2/DOA/VF/Urban Reign teardown data, WH signature entries) per the census
recorded in each changed file's `union_merge.era_note`.

## Flagged, NOT merged (evidence-based)

- `deathfang-werewolf.json` (1 historical version, 127 moves): exists in
  history but not on main and not in `MOVESET_IDS`. The werewolf moveset is
  owned by the Deathfang lane (122-move set, branch
  `feat/deathfang-real-models-20261020`); the `deathfang-werewolf` transform
  key is reserved in canon. Adding the older 127-move file here would collide
  with that lane — flagged for the parent to route.
- `sam-ur-a1.json` (1 historical version, 8 moves): early stub under an id
  the loader never fetches; the wired canonical file is `samura1.json`
  (in `MOVESET_IDS`, union-complete per the guard). Not added — dead duplicate.

## Owner overrides

Hunted in repo docs, `RENAME-MAP.md`, PRs #348/#349, and checkpoints. The
documented overrides (CHARGER signature renames; PR #348 intake wave-2 base
tables; PR #349 KRONOS set) are already applied in the current data — the
merge preserves them verbatim as part of main. No undocumented override was
invented.
