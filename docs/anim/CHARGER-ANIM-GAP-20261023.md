# Charger motion bank — precise gap (2026-10-23)

**Source priority: documented SF Blanka sources FIRST
(`game/assets/movesets/sf-blanka.json` — SFEX+alpha / EX2 Plus,
SuperCombo Wiki verbatim for EX2+ supers; `game/assets/movesets/blanka.json`
`sf_motion` translations), T3 bryan rows LAST (fallback only).**
Charger is the owner's proprietary Blanka replacement (owner 2026-10-20).

## Moveset status (done this pass — batch10-special-pull)

Verified complete, then +4:
- All 109 `blanka.json` `sf_motion` moves already present in
  `game/assets/movesets/charger.json` (id-diffed, 0 missing) — the full
  199-move set carried over per the file's canon_note (post-#363 union:
  SF6 set + SFV extras + T3 bryan bank rows).
- +4 documented EX2+ supers pulled from `sf-blanka.json` (199 → 203):
  `b,f,b,f+1+2` Ground Shave Rolling (super),
  `b,f,b,f+3+4` Jungle Beat (super, EX2+),
  `u,qcf,qcf+1+2` Beast Hurricane (air super, EX2+),
  `qcf,qcf+3+4` Super Electric Thunder (meteor Lv3, EX2+).
  Kept `sf_move`/`sf_input`/`sf_category`/`sf_game`/`sf_source`
  provenance; names follow the file's plain-SF convention.

**SHOW-ANIMATION LOCK (owner 2026-10-23):** `anim_set_lock` added;
200/203 moves stamped `"set": "FIGHT"`. 3 taunt entries
(`1+2+3+4`, `f+1+2+3+4`, `b+1+2+3+4` — Taunt Neutral/Forward/Back)
stamped `"set": "SHOW"` — taunts wire to intro/win slots and cutscenes
ONLY, never the moveset, without the user's explicit approval.

## The missing bank — FIGHT vs SHOW
- **FIGHT** — moveset moves, combat stances → the moveset
  (`game/assets/movesets/charger.json`) and the combat animation bank.
  SF motion: real frame data pending OVL decode (TEARDOWN.md 2c) —
  frame data on the SF translations is archetype-estimated, stated
  in-file.
- **SHOW** — 3 taunts tagged SHOW in-file (wire to taunt slots only);
  win pose / intro pose: no documented clips on disk — gap.
