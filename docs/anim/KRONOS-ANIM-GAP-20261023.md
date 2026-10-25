# Kronos motion bank — precise gap (2026-10-23)

**Source priority: documented SF Zangief sources FIRST
(`game/assets/movesets/sf-zangief.json` — SFEX+alpha, SLUS_005.48 binary
verbatim list + Kao_Megura EX+alpha guide; `game/assets/movesets/zangief.json`
sf_motion translations), T3 king proxy LAST (fallback only).**

## Moveset status (done this pass — batch10-special-pull)

Kronos's SF/Zangief side is COMPLETE — verified by id diff, nothing to
pull: all 34 `sf-zangief.json` documented moves and all 92
`zangief.json` `sf_motion` moves are present in
`game/assets/movesets/kronos.json` (772 moves total; 628 T3 king rows
remain as the logged fallback).

**SHOW-ANIMATION LOCK (owner 2026-10-23):** `anim_set_lock` added;
752/772 moves stamped `"set": "FIGHT"`. 20 taunt entries
(`Taunt (Neutral/Forward/Back/Down)` + `~donor.zangief` variants) are
stamped `"set": "SHOW"` — taunts wire to intro/win slots and cutscenes
ONLY, never the moveset, without the user's explicit approval.

## The missing bank — FIGHT vs SHOW

- **FIGHT** — moveset moves, combat stances → the moveset
  (`game/assets/movesets/kronos.json`) and the combat animation bank.
- **SHOW** — win poses, intro poses, taunts, cutscene animations →
  intro/win slots and cutscenes ONLY.

### FIGHT clips → combat bank + moveset
SF motion for Zangief is not decoded (TEARDOWN.md 2c: real frame data
pending OVL decode) — `anim_ref`s on the SF translations are
archetype-level until the SF teardown lane lands.

### GOLEM (Urban Reign) side — NO DOCUMENTED SOURCE (explicit gap)
Kronos's tekken_base is "Zangief + Golem (Urban Reign)". There is NO
documented Golem/Urban Reign movelist anywhere in the repo: no bank in
`game/data/moveset-library/banks/`, no moveset file, no teardown
movelist doc (the only Urban Reign mention is a menu-layout reference in
`docs/CREATE_A_FIGHTER_SPEC.md`). Nothing was invented to fill it —
per the no-guessing law this side stays empty until a documented source
exists. Handoff: extraction/teardown lane.

### SHOW clips → intro/win slots + cutscenes ONLY (never the moveset)
- 20 taunt entries — tagged SHOW in-file; wire to taunt slots only.
- Win pose / intro pose: no documented clips on disk — gap.
